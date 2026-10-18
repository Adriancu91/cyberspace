"""Dezambiguizarea explicabilă a analizelor morfologice, din context.

Fiecare candidat primește un scor = suma unor dovezi numite (reguli din sintaxa/reguli.py, secțiunea „dezambiguizare”),
fiecare cu explicația ei în română. Scorurile sunt euristice, NU probabilități calibrate. Candidații nu se șterg:
cel ales e `ales`, iar dacă primii doi sunt apropiați și nicio regulă decisivă nu i-a despărțit, cuvântul rămâne
`ambiguu` (ambiguitatea se raportează, nu se ascunde).
"""

from __future__ import annotations

import math

from .sintaxa.structuri import Candidat, Cuvant, Propozitie
from .text import normalizeaza

PONDERI = {
    "validat": 1.0, "atestat": 0.5, "generat": 0.2, "": 0.0,
    "ipoteza": -1.0, "necunoscut": -2.0, "fara_diacritice": -0.5, "special": 0.0,
    "decisiv": 3.0, "puternic": 2.0, "slab": 1.0,
}
MARJA_AMBIGUITATE = 1.0

AUX_PERFECT = {"am", "ai", "a", "ați", "au", "-am", "-ai", "-a", "-ați", "-au"}
AUX_COND = {"aș", "ar", "-aș", "-ar"}
AUX_VIITOR = {"voi", "vei", "va", "vom", "veți", "vor", "oi", "o", "om", "ăți", "or", "-oi", "-o", "-or"}
PRON_SUBIECT = {"eu": ("1", "Sing"), "tu": ("2", "Sing"), "noi": ("1", "Plur"), "voi": ("2", "Plur"), "el": ("3", "Sing"), "ea": ("3", "Sing"),
                "ei": ("3", "Plur"), "ele": ("3", "Plur"), "dumneavoastră": ("2", "Plur")}


def _are(c: Candidat, pos: str | None = None, **tr: str) -> bool:
    a = c.analiza
    if pos and a.pos != pos:
        return False
    return all(a.trasaturi.get(k) == v for k, v in tr.items())


def _plauzibili(cuv: Cuvant, marja: float = 1.5) -> list[Candidat]:
    """Candidații unui cuvânt vecin care contează: cei cu scorul (de bază) aproape de cel mai bun."""
    if not cuv.candidati:
        return []
    cel_mai_bun = max(c.scor for c in cuv.candidati)
    return [c for c in cuv.candidati if c.scor >= cel_mai_bun - marja]


def _vreun(cuv: Cuvant | None, pos: str | None = None, **tr: str) -> bool:
    return cuv is not None and any(_are(c, pos, **tr) for c in _plauzibili(cuv))


def _acord(a: dict[str, str], b: dict[str, str], chei: tuple[str, ...] = ("Gender", "Number")) -> bool | None:
    """True dacă trăsăturile comune coincid, False dacă una diferă, None dacă nu au nicio trăsătură comună."""
    comune = [k for k in chei if k in a and k in b]
    if not comune:
        return None
    return all(a[k] == b[k] for k in comune)


def _substantiv_probabil(cuv: Cuvant) -> bool:
    """Un vecin „substantiv” doar dacă analiza lui cea mai bună e substantiv (sau un substantiv e aproape de ea și cea mai bună nu e cuvânt-unealtă)."""
    if not cuv.candidati:
        return False
    cel_mai_bun = max(cuv.candidati, key=lambda c: c.scor)
    if cel_mai_bun.analiza.pos in ("NOUN", "PROPN"):
        return True
    if cel_mai_bun.analiza.pos in ("AUX", "PART", "ADP", "VERB", "PRON", "DET", "CCONJ", "SCONJ", "PUNCT"):
        return False
    return any(c.analiza.pos in ("NOUN", "PROPN") and c.scor >= cel_mai_bun.scor - 1.0 for c in cuv.candidati)


def _subst_vecin(prop: Propozitie, i: int, directie: int, maxim: int = 3) -> Cuvant | None:
    """Cel mai apropiat cuvânt-substantiv probabil, în direcția dată (sărind peste adjective/numerale/determinanți)."""
    j = i + directie
    pasi = 0
    while 0 <= j < len(prop.cuvinte) and pasi < maxim:
        cuv = prop.cuvinte[j]
        if _substantiv_probabil(cuv):
            return cuv
        if not (_vreun(cuv, "ADJ") or _vreun(cuv, "NUM") or _vreun(cuv, "DET") or _vreun(cuv, "ADV")):
            return None
        j += directie
        pasi += 1
    return None


def _scor_de_baza(cuv: Cuvant) -> None:
    for c in cuv.candidati:
        a = c.analiza
        w = PONDERI.get(a.statut, 0.0) if a.incredere in ("baza", "fara_diacritice") else PONDERI.get(a.incredere, 0.0)
        c.scor = w + (min(3.0, 0.75 * math.log1p(a.frecventa)) if a.frecventa else 0.0)
        if a.multicuvant:
            exp = getattr(cuv, "atribute_expresie", None)
            c.scor += 4.0 if (exp and normalizeaza(exp[1]) == normalizeaza(a.forma)) else -3.0


def scoreaza(prop: Propozitie, subiect_persoana: dict[int, tuple[str, str]] | None = None) -> None:
    """Pune scoruri și motive pe toți candidații tuturor cuvintelor, apoi alege. Se poate rula de două ori
    (a doua oară cu `subiect_persoana`, după ce sintaxa a găsit subiectele)."""
    n = len(prop.cuvinte)
    for cuv in prop.cuvinte:
        _scor_de_baza(cuv)   # scorurile de bază ale tuturor cuvintelor, ca regulile de context să vadă vecinii „plauzibili”
    for i, cuv in enumerate(prop.cuvinte):
        ant = prop.cuvinte[i - 1] if i > 0 else None
        urm = prop.cuvinte[i + 1] if i + 1 < n else None
        ant_norm = normalizeaza(ant.text) if ant else ""
        urm_norm = normalizeaza(urm.text) if urm else ""
        inceput = i == 0 or (ant is not None and ant.tip == "punct" and ant.text in ".!?…:;")
        for c in cuv.candidati:
            a = c.analiza
            c.scor = 0.0
            c.motive = []
            # dovezi de bază: statutul formei și frecvența în corpus
            w = PONDERI.get(a.statut, 0.0) if a.incredere in ("baza", "fara_diacritice") else PONDERI.get(a.incredere, 0.0)
            c.scor += w
            c.motive.append(f"statut_forma: {a.statut or a.incredere} ({w:+.1f})")
            if a.multicuvant:
                exp = getattr(cuv, "atribute_expresie", None)
                if exp and normalizeaza(exp[1]) == normalizeaza(a.forma):
                    c.scor += 4.0; c.motive.append(f"expresie: locuțiunea „{exp[1]}” e recunoscută în bază (+4)")
                else:
                    c.scor -= 3.0; c.motive.append("expresie multicuvânt nepotrivită (-3)")
            if a.incredere == "fara_diacritice":
                c.scor += PONDERI["fara_diacritice"]
                c.motive.append("potrivire fără diacritice (-0.5)")
            if a.frecventa:
                f = min(3.0, 0.75 * math.log1p(a.frecventa))
                c.scor += f
                c.motive.append(f"frecventa_corpus: {a.frecventa} apariții în UD RRT (+{f:.2f})")
            elif max((x.analiza.frecventa for x in cuv.candidati), default=0) >= 20 and a.incredere in ("baza", "fara_diacritice"):
                c.scor -= 1.0
                c.motive.append("frecventa_corpus: zero apariții, deși forma are o analiză frecventă în corpus (-1)")
            # infinitivul apare după „a”, după auxiliarele de viitor/condițional sau după „putea”/„fi”
            if a.pos in ("VERB", "AUX") and a.trasaturi.get("VerbForm") == "Inf" and a.lema != "fi":
                if not (ant_norm == "a" or ant_norm in AUX_VIITOR or ant_norm in AUX_COND or ant_norm in ("ai", "am", "ați") or
                        (ant is not None and ant.candidati and ant.candidati[0].analiza.lema in ("putea", "fi", "ști", "trebui"))):
                    c.scor -= 2.0
                    c.motive.append("dupa_sa: infinitivul apare după „a” sau după un auxiliar; aici nu (-2)")
            # majuscula
            if cuv.text[:1].isupper() and not cuv.text.isupper():
                if inceput:
                    if a.pos == "PROPN" and a.incredere == "ipoteza":
                        c.scor -= 1.0
                        c.motive.append("majuscula: la început de propoziție nu e dovadă de nume propriu (-1)")
                else:
                    if a.pos == "PROPN":
                        c.scor += PONDERI["puternic"]
                        c.motive.append("majuscula: în interiorul propoziției sugerează nume propriu (+2)")
                    elif a.incredere != "special":
                        c.scor -= 1.0
                        c.motive.append("majuscula în interiorul propoziției (-1 pentru analiza de cuvânt comun)")
            # după „să”: verb la conjunctiv
            if ant_norm in ("să", "s-"):
                if a.pos in ("VERB", "AUX") and (a.trasaturi.get("Mood") == "Sub" or a.trasaturi.get("VerbForm") == "Inf" and a.lema == "fi"):
                    c.scor += PONDERI["decisiv"]; c.motive.append("dupa_sa: după „să” urmează un verb la conjunctiv (+3)")
                elif a.pos in ("VERB", "AUX"):
                    c.scor += 1.0; c.motive.append("dupa_sa: verb după „să” (+1)")
                elif a.pos in ("NOUN", "ADJ", "ADV", "PROPN") and not _vreun(cuv, "PRON") and not _vreun(cuv, "PART"):
                    c.scor -= 2.0; c.motive.append("dupa_sa: după „să” nu așteptăm un nume (-2)")
            # după particula „a” sau auxiliar de viitor/condițional: infinitiv
            if (ant_norm in AUX_VIITOR or ant_norm in AUX_COND or ant_norm == "ai" and _vreun(ant, "AUX")) or (ant_norm == "a" and _vreun(ant, "PART")):
                if a.pos in ("VERB", "AUX") and a.trasaturi.get("VerbForm") == "Inf":
                    c.scor += PONDERI["decisiv"]; c.motive.append("dupa_sa: după „a”/auxiliar de viitor sau condițional urmează infinitivul (+3)")
            # după auxiliarul perfectului compus: participiu
            if ant_norm in AUX_PERFECT and _vreun(ant, "AUX"):
                if a.pos in ("VERB", "AUX") and a.trasaturi.get("VerbForm") == "Part":
                    c.scor += PONDERI["decisiv"]; c.motive.append("dupa_sa: după am/ai/a/ați/au urmează participiul (+3)")
                elif a.pos in ("VERB",) and a.trasaturi.get("VerbForm") == "Fin" and a.trasaturi.get("Mood") == "Ind":
                    c.scor -= 1.0; c.motive.append("dupa_sa: după auxiliar nu așteptăm un verb la indicativ (-1)")
            # auxiliarul însuși: am/ai/a/ați/au + participiu → AUX; voi/vei/va… + infinitiv → AUX; verbul „avea” în aceeași poziție scade
            if a.lema in ("avea", "vrea", "fi") and urm is not None:
                urmeaza_part = _vreun(urm, "VERB", VerbForm="Part") or _vreun(urm, "AUX", VerbForm="Part") or urm_norm in ("fost", "fi")
                urmeaza_inf = _vreun(urm, "VERB", VerbForm="Inf") or _vreun(urm, "AUX", VerbForm="Inf")
                if a.pos == "AUX" and a.lema == "avea" and urmeaza_part:
                    c.scor += PONDERI["decisiv"]; c.motive.append("dupa_sa: urmează un participiu → auxiliarul perfectului compus / condiționalului (+3)")
                elif a.pos == "AUX" and a.lema == "avea" and urmeaza_inf and normalizeaza(cuv.text) in AUX_COND | {"ai", "am", "ați"}:
                    c.scor += PONDERI["decisiv"]; c.motive.append("dupa_sa: urmează un infinitiv → auxiliarul condiționalului (+3)")
                elif a.pos == "AUX" and a.lema == "vrea" and urmeaza_inf:
                    c.scor += PONDERI["decisiv"]; c.motive.append("dupa_sa: urmează un infinitiv → auxiliarul viitorului (+3)")
                elif a.pos == "VERB" and a.lema in ("avea", "vrea") and (urmeaza_part or urmeaza_inf) and a.trasaturi.get("VerbForm") == "Fin":
                    c.scor -= 2.0; c.motive.append("dupa_sa: înaintea unui participiu/infinitiv forma e auxiliar, nu verb predicativ (-2)")
            # „fost”/„fi” + participiu: auxiliar al pasivului sau al timpurilor compuse; participiul de după e verb, nu adjectiv
            if a.lema == "fi" and urm is not None and (_vreun(urm, "VERB", VerbForm="Part")):
                if a.pos == "AUX":
                    c.scor += PONDERI["decisiv"]; c.motive.append("dupa_sa: „fi/fost” + participiu → auxiliar (+3)")
                elif a.pos == "VERB":
                    c.scor -= 2.0; c.motive.append("dupa_sa: „fi/fost” + participiu: aici „a fi” e auxiliar, nu predicativ (-2)")
            dupa_a_fi = ant is not None and ant.candidati and ant.candidati[0].analiza.lema == "fi" and ant.candidati[0].analiza.pos in ("AUX", "VERB")
            if dupa_a_fi and a.trasaturi.get("VerbForm") == "Part" and a.pos == "VERB":
                c.scor += PONDERI["puternic"]; c.motive.append("diateza: participiu după o formă a lui „a fi” → pasiv / timp compus (+2)")
            if dupa_a_fi and a.pos == "ADJ" and any(x.analiza.pos == "VERB" and x.analiza.trasaturi.get("VerbForm") == "Part" for x in cuv.candidati):
                c.scor -= 1.0; c.motive.append("diateza: după „a fi” forma e mai degrabă participiu verbal decât adjectiv (-1)")
            # genitivul după un substantiv articulat: „grădina bunicii”, „cartea elevului”
            if a.pos in ("NOUN", "PROPN") and a.trasaturi.get("Case") == "Dat,Gen" and ant is not None and not _vreun(ant, "ADP"):
                if any(x.analiza.pos in ("NOUN", "PROPN") and x.analiza.trasaturi.get("Definite") == "Def" for x in _plauzibili(ant)) or (ant.pos == "DET" and ant.a.lema == "al"):
                    c.scor += PONDERI["puternic"]; c.motive.append(f"genitiv: după substantivul articulat „{ant.text}” forma de genitiv e atributul lui (+2)")
            # „s-”: „să” înaintea cliticului „o” (s-o vadă) sau înaintea unui verb la conjunctiv; „se” înaintea unui auxiliar (s-a dus, s-ar putea)
            if normalizeaza(cuv.text) == "s-" and urm is not None:
                if a.lema == "să" and (urm_norm in ("o", "l", "i", "le", "mi", "ți", "ne", "vă") or _vreun(urm, "VERB", Mood="Sub")):
                    c.scor += PONDERI["puternic"]; c.motive.append("clitice: „s-” + o/clitic/conjunctiv → „să” (+2)")
                if a.lema == "sine" and (urm_norm in AUX_PERFECT or urm_norm in AUX_COND or urm_norm in ("ar", "a", "au", "ai", "am", "ați") or _vreun(urm, "AUX")):
                    c.scor += PONDERI["puternic"]; c.motive.append("clitice: „s-” + auxiliar → reflexivul „se” (+2)")
            # participiul folosit după substantiv: în UD RRT e de regulă verb (acl), nu adjectiv, dacă forma e participiul unui verb cunoscut
            if a.pos == "VERB" and a.trasaturi.get("VerbForm") == "Part" and any(x.analiza.pos == "ADJ" for x in cuv.candidati) and not a.frecventa and not any(x.analiza.pos == "ADJ" and x.analiza.frecventa for x in cuv.candidati):
                c.scor += 0.5; c.motive.append("diateza: participiu verbal preferat adjectivului omonim fără dovezi din corpus (+0.5)")
            # forma de genitiv-dativ singular nearticulat (case, cărți, frumoase) e identică cu pluralul: o citim ca genitiv doar după un determinant în genitiv-dativ
            if a.pos in ("NOUN", "ADJ") and a.trasaturi.get("Case") == "Dat,Gen" and a.trasaturi.get("Definite") == "Ind" and a.trasaturi.get("Number") == "Sing":
                gd_inainte = any(_vreun(prop.cuvinte[j], "DET", Case="Dat,Gen") or _vreun(prop.cuvinte[j], "NUM", Case="Dat,Gen") for j in range(max(0, i - 3), i))
                if gd_inainte:
                    c.scor += PONDERI["puternic"]; c.motive.append("genitiv: după un determinant în genitiv-dativ (unei, acestei…) (+2)")
                else:
                    c.scor -= 1.5; c.motive.append("genitiv: fără determinant în genitiv-dativ înainte, forma e mai degrabă plural (-1.5)")
            # „nu” înaintea verbului
            if ant_norm in ("nu", "n-") and a.pos in ("VERB", "AUX"):
                c.scor += 1.0; c.motive.append("negatie: după „nu” urmează verbul (+1)")
            # forma „a”: auxiliar / particulă / articol posesiv / prepoziție
            if normalizeaza(cuv.text) == "a" and urm is not None:
                if a.pos == "AUX" and _vreun(urm, "VERB", VerbForm="Part") or a.pos == "AUX" and _vreun(urm, "AUX", VerbForm="Part"):
                    c.scor += PONDERI["decisiv"]; c.motive.append("a_ambiguu: urmează un participiu → auxiliar (+3)")
                if a.pos == "PART" and (_vreun(urm, "VERB", VerbForm="Inf") or _vreun(urm, "AUX", VerbForm="Inf")) and not _vreun(urm, "VERB", VerbForm="Part"):
                    c.scor += PONDERI["decisiv"]; c.motive.append("a_ambiguu: urmează un infinitiv → particula infinitivului (+3)")
                if a.pos == "DET" and a.lema == "al" and (_vreun(urm, "PROPN") or _vreun(urm, "DET", PronType="Art") or _vreun(urm, "NOUN", Case="Dat,Gen") or _vreun(urm, "PRON", Case="Dat,Gen") or _vreun(urm, "DET", Poss="Yes")):
                    c.scor += PONDERI["decisiv"]; c.motive.append("a_ambiguu: urmează un genitiv/posesiv → articolul posesiv „a” (+3)")
                if a.pos == "ADP" and _vreun(urm, "NUM", NumType="Ord"):
                    c.scor += PONDERI["decisiv"]; c.motive.append("a_ambiguu: „a doua” (+3)")
                if a.pos == "VERB" and a.lema == "avea":
                    c.scor -= 1.0; c.motive.append("a_ambiguu: verbul „a avea” la infinitiv e rar singur (-1)")
            # forma „o”: articol / pronume / auxiliar
            if normalizeaza(cuv.text) == "o":
                if a.pos == "AUX" and urm_norm == "să":
                    c.scor += PONDERI["decisiv"]; c.motive.append("o_ambiguu: „o să” → auxiliar de viitor (+3)")
                elif a.pos == "AUX":
                    c.scor -= 2.0; c.motive.append("o_ambiguu: fără „să” după el, „o” nu e auxiliar (-2)")
                if a.pos == "DET" and urm is not None and (_vreun(urm, "NOUN", Number="Sing", Gender="Fem") or _vreun(urm, "ADJ", Number="Sing", Gender="Fem") or _vreun(urm, "NUM")):
                    c.scor += PONDERI["decisiv"]; c.motive.append("o_ambiguu: urmează un nume feminin singular → articol nehotărât (+3)")
                if a.pos == "PRON" and urm is not None and (_vreun(urm, "VERB") or _vreun(urm, "AUX") or urm_norm in AUX_PERFECT or urm_norm in ("va", "vei", "voi", "vor", "vom", "veți")) and not _vreun(urm, "NOUN", Gender="Fem", Number="Sing"):
                    c.scor += PONDERI["decisiv"]; c.motive.append("o_ambiguu: urmează un verb → pronume clitic de acuzativ (+3)")
                if a.pos == "PRON" and ant is not None and _vreun(ant, "VERB") and (urm is None or urm.tip == "punct"):
                    c.scor += PONDERI["puternic"]; c.motive.append("o_ambiguu: după verb, la sfârșit → pronume (+2)")
            # substantiv / verb (omonime)
            if a.pos in ("NOUN", "VERB", "AUX") and any(x.analiza.pos != a.pos and x.analiza.pos in ("NOUN", "VERB", "AUX") for x in cuv.candidati):
                if ant is not None and (_vreun(ant, "DET") or _vreun(ant, "ADP") or _vreun(ant, "NUM") or (_vreun(ant, "ADJ") and not _vreun(ant, "VERB"))):
                    c.scor += PONDERI["puternic"] if a.pos == "NOUN" else -PONDERI["puternic"]
                    c.motive.append("subst_vs_verb: după determinant/prepoziție/adjectiv → substantiv (±2)")
                if ant is not None and (ant_norm in ("nu", "n-", "să", "s-") or _vreun(ant, "PRON", Strength="Weak") or _vreun(ant, "AUX")):
                    c.scor += PONDERI["puternic"] if a.pos in ("VERB", "AUX") else -PONDERI["puternic"]
                    c.motive.append("subst_vs_verb: după clitic/„nu”/„să”/auxiliar → verb (±2)")
            # acordul cu substantivul vecin (determinanți, numerale, adjective)
            if a.pos in ("DET", "NUM", "ADJ") and a.trasaturi:
                vecin = _subst_vecin(prop, i, +1) if a.pos in ("DET", "NUM") else (_subst_vecin(prop, i, +1) or _subst_vecin(prop, i, -1))
                if vecin is not None:
                    acorduri = [_acord(a.trasaturi, x.analiza.trasaturi) for x in _plauzibili(vecin) if x.analiza.pos in ("NOUN", "PROPN")]
                    if True in acorduri:
                        c.scor += PONDERI["puternic"]; c.motive.append(f"acord_vecini: se acordă cu „{vecin.text}” (+2)")
                    elif False in acorduri and None not in acorduri:
                        c.scor -= 1.0; c.motive.append(f"acord_vecini: nu se acordă cu „{vecin.text}” (-1)")
            if a.pos == "NOUN" and ant is not None and a.trasaturi:
                for x in _plauzibili(ant):
                    if x.analiza.pos in ("DET", "NUM") and x.analiza.trasaturi:
                        ac = _acord(a.trasaturi, x.analiza.trasaturi)
                        if ac is True:
                            c.scor += 1.0; c.motive.append(f"acord_vecini: determinantul „{ant.text}” se acordă (+1)")
                            break
            # adjectiv vs substantiv: adjectivul preferă un substantiv vecin cu care se acordă
            if a.pos == "ADJ" and any(x.analiza.pos == "NOUN" for x in cuv.candidati):
                vecin = _subst_vecin(prop, i, -1) or _subst_vecin(prop, i, +1)
                if vecin is None and ant is not None and _vreun(ant, "DET"):
                    c.scor -= 1.0; c.motive.append("adj_vs_subst: după determinant fără alt substantiv → mai degrabă substantiv (-1)")
            # persoana și numărul verbului după pronumele subiect
            if a.pos in ("VERB", "AUX") and a.trasaturi.get("VerbForm") == "Fin":
                pron = None
                for j in (i - 1, i - 2, i - 3):
                    if 0 <= j < n and normalizeaza(prop.cuvinte[j].text) in PRON_SUBIECT and _vreun(prop.cuvinte[j], "PRON", Strength="Strong"):
                        pron = PRON_SUBIECT[normalizeaza(prop.cuvinte[j].text)]
                        break
                if subiect_persoana and (i + 1) in subiect_persoana:
                    pron = subiect_persoana[i + 1]
                if pron:
                    p, nr = pron
                    if a.trasaturi.get("Person") == p and a.trasaturi.get("Number") in (nr, None):
                        c.scor += PONDERI["puternic"]; c.motive.append(f"subiect: persoana {p} {nr} ca subiectul (+2)")
                    elif a.trasaturi.get("Person") and a.trasaturi.get("Person") != p:
                        c.scor -= 1.0; c.motive.append("subiect: altă persoană decât subiectul (-1)")
        alege(cuv)


def alege(cuv: Cuvant) -> None:
    """Ordonează candidații după scor (stabil) și marchează ambiguitatea rămasă."""
    ordonati = sorted(range(len(cuv.candidati)), key=lambda k: (-cuv.candidati[k].scor, k))
    cuv.candidati = [cuv.candidati[k] for k in ordonati]
    cuv.ales = 0 if cuv.candidati else None
    cuv.ambiguu = False
    if len(cuv.candidati) >= 2:
        c0 = cuv.candidati[0]
        for c1 in cuv.candidati[1:]:
            if c0.scor - c1.scor >= MARJA_AMBIGUITATE:
                break
            if (c0.analiza.pos, c0.analiza.lema) != (c1.analiza.pos, c1.analiza.lema):
                cuv.ambiguu = True
                c0.motive.append(f"ambiguitate_pastrata: scor apropiat de „{c1.analiza.lema}” ({c1.analiza.pos}); alegerea nu e sigură")
                break
