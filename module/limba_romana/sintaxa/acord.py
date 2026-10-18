"""Grupurile nominale și verificarea acordului (regulile din reguli.py, secțiunea „acord”).

Verificările produc `Problema` cu mesaj în română, regula invocată, poziții și, când se poate, forma sugerată
(căutată în bază pentru lexemul respectiv, cu trăsăturile corecte).
"""

from __future__ import annotations

import re

from ..baza import Baza, canonic_trasaturi
from ..morfologie.analizator import Analiza
from ..morfologie.trasaturi import canonic_pentru_pos
from ..text import normalizeaza
from .structuri import Cuvant, Grup, Problema, Propozitie

RE_CIFRE = re.compile(r"^\d+$")
NUMERALE_CUVANT = {"zero": 0, "unu": 1, "una": 1, "un": 1, "o": 1, "doi": 2, "două": 2, "trei": 3, "patru": 4, "cinci": 5, "șase": 6, "șapte": 7, "opt": 8, "nouă": 9,
                   "zece": 10, "unsprezece": 11, "doisprezece": 12, "douăsprezece": 12, "treisprezece": 13, "paisprezece": 14, "cincisprezece": 15, "șaisprezece": 16,
                   "șaptesprezece": 17, "optsprezece": 18, "nouăsprezece": 19, "douăzeci": 20, "treizeci": 30, "patruzeci": 40, "cincizeci": 50, "șaizeci": 60,
                   "șaptezeci": 70, "optzeci": 80, "nouăzeci": 90, "sută": 100, "sute": 100, "mie": 1000, "mii": 1000, "milion": 1000000, "milioane": 1000000,
                   "miliard": 10 ** 9, "miliarde": 10 ** 9}
VERBE_FARA_OBIECT = {"fi", "veni", "pleca", "sosi", "apărea", "exista", "muri", "părea", "lipsi", "intra", "ieși", "cădea", "dispărea", "zbura", "dormi",
                     "râde", "plânge", "trăi"}
# unități de măsură, monede și luni: „200 lei”, „30 aprilie” sunt uzuale/corecte; nu aplicăm regula „de”
FARA_DE = {"lei", "leu", "euro", "dolari", "bani", "km", "kg", "g", "m", "cm", "mm", "l", "ml", "ha", "mp", "kw", "mw", "gb", "mb", "ianuarie", "februarie",
           "martie", "aprilie", "mai", "iunie", "iulie", "august", "septembrie", "octombrie", "noiembrie", "decembrie", "grade", "volți", "amperi", "la", "sută", "sute", "mii", "mie"}
PREPOZITII_CU_GENITIV = {"asupra", "contra", "deasupra", "dedesubtul", "dinaintea", "împotriva", "înaintea", "înapoia", "îndărătul", "împrejurul"}


def _gn(c: Cuvant) -> tuple[str | None, str | None, str | None]:
    return c.tr("Gender"), c.tr("Number"), c.tr("Case")


def _acord_simplu(tr: dict[str, str], gen: str | None, nr: str | None) -> bool:
    return (gen is None or tr.get("Gender") in (gen, None)) and (nr is None or tr.get("Number") in (nr, None))


def valoare_numeral(prop: Propozitie, i: int) -> tuple[int | None, int]:
    """Valoarea numeralului care începe la poziția i (0-based) și poziția ultimului cuvânt al lui."""
    cuv = prop.cuvinte[i]
    if RE_CIFRE.match(cuv.text.replace(".", "")):
        return int(cuv.text.replace(".", "")), i
    total, curent, j, gasit = 0, 0, i, False
    while j < len(prop.cuvinte):
        t = normalizeaza(prop.cuvinte[j].text)
        if t in NUMERALE_CUVANT and prop.cuvinte[j].pos in ("NUM", "DET"):
            v = NUMERALE_CUVANT[t]
            if v >= 100:
                curent = (curent or 1) * v
                total += curent
                curent = 0
            else:
                curent += v
            gasit = True
            j += 1
        elif t == "și" and gasit and j + 1 < len(prop.cuvinte) and normalizeaza(prop.cuvinte[j + 1].text) in NUMERALE_CUVANT:
            j += 1
        else:
            break
    if not gasit:
        return None, i
    return total + curent, j - 1


def grupuri_nominale(prop: Propozitie) -> list[Grup]:
    """Grupul nominal: [DET/NUM/ADJ antepus]* SUBST [ADJ/DET postpus]*; adjectivele intră doar dacă nu contrazic clar acordul."""
    grupuri: list[Grup] = []
    n = len(prop.cuvinte)
    i = 0
    while i < n:
        c = prop.cuvinte[i]
        if c.pos in ("NOUN", "PROPN") or (c.pos == "PRON" and c.tr("PronType") not in ("Prs",) and not c.tr("Strength")):
            # înapoi: determinanți, numerale, adjective antepuse (fără prepoziție între ele)
            inceput = i
            j = i - 1
            while j >= 0 and prop.cuvinte[j].pos in ("DET", "NUM", "ADJ") and prop.cuvinte[j].grup is None:
                if prop.cuvinte[j].pos == "DET" and prop.cuvinte[j].a.lema == "al":
                    break  # „turul doi al alegerilor”: al/a/ai/ale începe dependentul genitival, nu grupul următor
                if prop.cuvinte[j].pos == "ADJ" and prop.cuvinte[j].text[:1].isupper() and j > 0:
                    break  # adjectiv cu majusculă în interiorul propoziției: parte a unui nume (Comisia Europeană pentru … Alimentar)
                if prop.cuvinte[j].pos == "ADJ" and prop.cuvinte[j].tr("Definite") == "Def" and c.tr("Definite") == "Def":
                    break  # „albeața paginii”: un „adjectiv” articulat înaintea unui substantiv articulat e de fapt substantiv (cap propriu)
                if prop.cuvinte[j].pos == "DET" and prop.cuvinte[j].tr("PronType") == "Art" and normalizeaza(prop.cuvinte[j].text) == "lui":
                    pass  # „lui Ion”: articolul proclitic intră în grup
                inceput = j
                j -= 1
            sfarsit = i
            j = i + 1
            gen_c, nr_c, _ = _gn(c)
            while j < n and prop.cuvinte[j].pos in ("ADJ", "DET", "NUM", "PROPN") and prop.cuvinte[j].grup is None:
                cj = prop.cuvinte[j]
                if cj.pos == "DET" and not (cj.tr("Position") == "Postnom" or normalizeaza(cj.text) in ("tot", "toți", "toate", "toată")):
                    break  # „un”, „o”, „al/a”, „acestor” (genitiv), „celorlalți” încep alt grup / sunt dependenți genitivali
                if cj.pos == "NUM" and cj.tr("NumType") != "Ord":
                    break
                if cj.pos == "PROPN" and c.pos != "NOUN":
                    break
                if cj.pos == "ADJ" and cj.tr("Case") == "Dat,Gen" and cj.tr("Definite") == "Def" and c.tr("Case") != "Dat,Gen":
                    break  # „sensul romanticului”: adjectiv substantivizat la genitiv, dependent, nu modificator
                if cj.pos == "ADJ" and any(prop.cuvinte[k].pos == "PROPN" for k in range(i + 1, j)):
                    break  # „romanul Piatra neagră”: adjectivul de după numele propriu ține de nume (titlu)
                if cj.pos == "ADJ" and gen_c and nr_c:
                    # adjectivul postpus care nu se acordă cu capul, dar se acordă cu substantivul următor, e al grupului următor
                    acord_cap = any(_acord_simplu(x.analiza.trasaturi, gen_c, nr_c) for x in cj.candidati if x.analiza.pos == "ADJ")
                    urm = next((prop.cuvinte[k] for k in range(j + 1, min(n, j + 3)) if prop.cuvinte[k].pos in ("NOUN", "PROPN")), None)
                    if not acord_cap and urm is not None:
                        g_u, n_u, _ = _gn(urm)
                        if any(_acord_simplu(x.analiza.trasaturi, g_u, n_u) for x in cj.candidati if x.analiza.pos == "ADJ"):
                            break
                sfarsit = j
                j += 1
            # apoziție nemarcată: „practicile TAIJIQUAN”, „orașul București”, „domnul profesor Ionescu” → în același grup, nu cap nou
            while sfarsit + 1 < n and prop.cuvinte[sfarsit + 1].pos in ("NOUN", "PROPN") and prop.cuvinte[sfarsit + 1].grup is None \
                    and (prop.cuvinte[sfarsit + 1].text[:1].isupper() or prop.cuvinte[sfarsit + 1].pos == "PROPN") and c.pos == "NOUN":
                sfarsit += 1
                j = sfarsit + 1
            g = Grup(inceput + 1, sfarsit + 1, i + 1, membri=list(range(inceput + 1, sfarsit + 2)))
            for k in range(inceput, sfarsit + 1):
                prop.cuvinte[k].grup = len(grupuri)
            grupuri.append(g)
            i = sfarsit + 1
        else:
            i += 1
    return grupuri


def _forma_sugerata(baza: Baza, a: Analiza, trasaturi: dict[str, str]) -> str | None:
    """Caută în bază forma lexemului cu trăsăturile cerute (întâi validată/atestată, apoi generată)."""
    if not a.lexem_id:
        return None
    tr = canonic_trasaturi(canonic_pentru_pos(a.pos, trasaturi, a.gen_lexem))
    r = baza.con.execute("SELECT forma FROM forme WHERE lexem_id = ? AND trasaturi = ? ORDER BY CASE statut WHEN 'validat' THEN 0 WHEN 'atestat' THEN 1 ELSE 2 END, forma LIMIT 1",
                         (a.lexem_id, tr)).fetchone()
    return r[0] if r else None


def verifica_acord_grup(baza: Baza, prop: Propozitie, g: Grup) -> list[Problema]:
    probleme: list[Problema] = []
    cap = prop.cuvant(g.cap)
    if cap.pos not in ("NOUN", "PROPN"):
        return probleme
    gen_c, nr_c, caz_c = _gn(cap)
    if not nr_c:
        return probleme
    def_c = cap.tr("Definite")
    # analizele plauzibile ale capului (sincretisme: „politici” = plural sau genitiv singular)
    analize_cap = [x.analiza for x in cap.candidati if x.analiza.pos in ("NOUN", "PROPN") and x.scor >= cap.candidati[0].scor - 1.5]
    for idx in g.membri:
        if idx == g.cap:
            continue
        cuv = prop.cuvant(idx)
        a = cuv.a
        if a.pos not in ("ADJ", "DET", "NUM"):
            continue
        if a.pos == "ADJ" and cuv.text[:1].isupper() and idx > 1:
            continue  # parte a unui nume propriu
        if a.pos == "NUM" and idx > g.cap:
            continue  # numeral postpus cu valoare ordinală (turul doi, anexa II)
        ambiguu_categorie = cuv.ambiguu and any(x.analiza.pos != a.pos for x in cuv.candidati[1:3])
        if a.pos == "DET" and a.tr("PronType") == "Art":
            continue  # „lui” proclitic
        if a.pos == "DET" and a.lema == "al":
            continue  # se verifică separat
        if a.pos == "DET" and a.tr("PronType") == "Int,Rel" and idx > 1 and prop.cuvant(idx - 1).pos == "DET" and prop.cuvant(idx - 1).a.lema == "al":
            continue  # „a cărui ascendență”: cărui se acordă cu posesorul, nu cu substantivul
        if a.pos == "NUM" and a.tr("NumType") != "Ord" and a.lema not in ("doi", "unu"):
            continue
        if a.pos == "DET" and any(prop.cuvant(k).pos == "NUM" and prop.cuvant(k).tr("NumType") != "Ord" for k in g.membri if idx < k < g.cap):
            continue  # „vreo 200 lei”, „câțiva 3 oameni”: determinantul aproximativ nu se acordă cu substantivul
        gen_a, nr_a, caz_a = _gn(cuv)
        # există o altă analiză a aceluiași cuvânt care se acordă? (sincretism) → nu e greșeală
        potrivit = None
        for cand in cuv.candidati:
            t = cand.analiza.trasaturi
            if cand.analiza.pos not in ("ADJ", "DET", "NUM") or not t:
                continue
            for ac in analize_cap:
                g_c, n_c, c_c = ac.trasaturi.get("Gender"), ac.trasaturi.get("Number"), ac.trasaturi.get("Case")
                if (t.get("Gender") in (g_c, None) or g_c is None) and (t.get("Number") in (n_c, None) or n_c is None):
                    if c_c and t.get("Case") and t.get("Case") != c_c and c_c != "Voc":
                        continue
                    potrivit = cand
                    break
            if potrivit is not None:
                break
        if potrivit is not None:
            if potrivit is not cuv.candidati[cuv.ales or 0]:
                cuv.ales = cuv.candidati.index(potrivit)
                potrivit.motive.append("acord: aleasă analiza care se acordă cu substantivul din grup")
            # articolul hotărât o singură dată în grup (adjectiv antepus articulat + substantiv articulat)
            if a.pos == "ADJ" and idx < g.cap and potrivit.analiza.tr("Definite") == "Def" and def_c == "Def":
                probleme.append(Problema("acord_subst_adj", [idx, g.cap], f"Și adjectivul „{cuv.text}”, și substantivul „{cap.text}” sunt articulate; articolul hotărât se pune o singură dată.",
                                         "articol_hotarat_unic", f"{cuv.text} {_forma_sugerata(baza, cap.a, {**cap.a.trasaturi, 'Definite': 'Ind'}) or cap.text}", "probabila"))
            continue
        # nu se acordă: formulăm problema cu forma sugerată
        tinta = dict(a.trasaturi)
        if gen_c:
            tinta["Gender"] = gen_c
        tinta["Number"] = nr_c
        if caz_c and "Case" in a.trasaturi:
            tinta["Case"] = caz_c
        if a.pos == "ADJ" and idx > g.cap:
            tinta["Definite"] = "Ind"
            if gen_c == "Masc" or nr_c == "Plur":
                tinta.pop("Case", None)
        sugestie = _forma_sugerata(baza, a, tinta)
        ce = {"ADJ": "Adjectivul", "DET": "Determinantul", "NUM": "Numeralul"}[a.pos]
        desc_c = " ".join(x for x in ({"Masc": "masculin", "Fem": "feminin"}.get(gen_c or "", ""), {"Sing": "singular", "Plur": "plural"}.get(nr_c, "")) if x)
        desc_a = " ".join(x for x in ({"Masc": "masculin", "Fem": "feminin"}.get(gen_a or "", ""), {"Sing": "singular", "Plur": "plural"}.get(nr_a or "", "")) if x)
        regula = "subst_adj" if a.pos == "ADJ" else ("doi_doua" if a.pos == "NUM" else "subst_det")
        probleme.append(Problema("acord_subst_adj" if a.pos == "ADJ" else "acord_subst_det", [idx, g.cap],
                                 f"{ce} „{cuv.text}” ({desc_a or 'fără gen/număr'}) nu se acordă cu substantivul „{cap.text}” ({desc_c}).",
                                 regula, sugestie, "sigura" if cap.a.incredere == "baza" and a.incredere == "baza" and not ambiguu_categorie else "probabila"))
    return probleme


def verifica_al(baza: Baza, prop: Propozitie) -> list[Problema]:
    """al/a/ai/ale se acordă cu obiectul posedat (substantivul dinaintea lor, capul grupului), nu cu posesorul."""
    probleme: list[Problema] = []
    for i, cuv in enumerate(prop.cuvinte):
        if not (cuv.pos == "DET" and cuv.a.lema == "al"):
            continue
        # obiectul posedat: capul grupului nominal precedent (sau substantivul precedent)
        posedat = None
        for j in range(i - 1, max(-1, i - 5), -1):
            cj = prop.cuvinte[j]
            if cj.pos == "NOUN" and cj.grup is not None:
                posedat = prop.cuvant(prop.grupuri[cj.grup].cap)
                break
            if cj.pos in ("NOUN", "PROPN", "PRON"):
                posedat = cj
                break
            if cj.pos not in ("ADJ", "NUM", "ADV"):
                break  # între obiectul posedat și „al” pot sta doar adjective/numerale; altfel nu verificăm
        if posedat is not None and posedat.tr("Case") == "Dat,Gen":
            continue  # „în vederea consumului uman a …”: posedatul e el însuși genitiv; posesorul se leagă mai sus
        if posedat is None or posedat.pos == "PROPN":
            continue
        inceput_grup = prop.grupuri[posedat.grup].inceput - 1 if posedat.grup is not None else posedat.idx - 1
        if inceput_grup > 0 and prop.cuvinte[inceput_grup - 1].pos == "ADP":
            continue  # „producția de caviar a țării”: posesorul se poate lega de capul de dinaintea prepoziției; nu verificăm
        gen_p, nr_p, _ = _gn(posedat)
        if not gen_p or not nr_p:
            continue
        # vreo analiză a lui al/a/ai/ale care se acordă?
        ok = any(x.analiza.lema == "al" and x.analiza.tr("Gender") == gen_p and x.analiza.tr("Number") == nr_p for x in cuv.candidati)
        if ok:
            for k, x in enumerate(cuv.candidati):
                if x.analiza.lema == "al" and x.analiza.tr("Gender") == gen_p and x.analiza.tr("Number") == nr_p:
                    cuv.ales = k
                    break
            continue
        forma = {("Masc", "Sing"): "al", ("Fem", "Sing"): "a", ("Masc", "Plur"): "ai", ("Fem", "Plur"): "ale"}[(gen_p, nr_p)]
        probleme.append(Problema("acord_al", [i + 1, posedat.idx],
                                 f"„{cuv.text}” nu se acordă cu „{posedat.text}” ({'masculin' if gen_p == 'Masc' else 'feminin'} {'singular' if nr_p == 'Sing' else 'plural'}); al/a/ai/ale se acordă cu obiectul posedat.",
                                 "al_a_ai_ale", forma, "sigura" if posedat.a.incredere == "baza" else "probabila"))
    return probleme


def verifica_numerale(baza: Baza, prop: Propozitie) -> list[Problema]:
    """De la 20 în sus: numeral + „de” + substantiv; sub 20 fără „de”; 101–119 fără „de”. Plus acordul doi/două."""
    probleme: list[Problema] = []
    n = len(prop.cuvinte)
    i = 0
    while i < n:
        cuv = prop.cuvinte[i]
        if cuv.pos not in ("NUM", "DET") or cuv.tr("NumType") == "Ord":
            i += 1
            continue
        valoare, ultim = valoare_numeral(prop, i)
        if valoare is None:
            i += 1
            continue
        urm = prop.cuvinte[ultim + 1] if ultim + 1 < n else None
        urm2 = prop.cuvinte[ultim + 2] if ultim + 2 < n else None
        are_de = urm is not None and normalizeaza(urm.text) == "de"
        subst = urm2 if are_de else urm
        if subst is not None and subst.pos in ("NOUN", "ADJ") and not (subst.pos == "ADJ" and not are_de and urm2 is not None and urm2.pos == "NOUN"):
            if subst.pos == "ADJ" and urm2 is not None and urm2.pos == "NOUN":
                subst = urm2
        if subst is None or subst.pos not in ("NOUN",) or subst.text in ("%",) or len(subst.text) <= 2 or subst.tr("Abbr") == "Yes" or subst.a.incredere != "baza" \
                or normalizeaza(subst.text) in FARA_DE or any(x.analiza.pos in ("ADJ", "VERB") and x.scor >= subst.candidati[0].scor - 1.0 for x in subst.candidati):
            i = ultim + 1
            continue
        ultimele_doua = valoare % 100
        cere_de = valoare >= 20 and not (1 <= ultimele_doua <= 19)
        if cere_de and not are_de and normalizeaza(subst.text) not in ("la", "sută", "sute", "mii", "mie", "milioane", "miliarde", "milion", "miliard"):
            probleme.append(Problema("numeral_de", [i + 1, subst.idx], f"De la 20 în sus numeralul se leagă de substantiv prin „de”: „{' '.join(c.text for c in prop.cuvinte[i:ultim + 1])} de {subst.text}”.",
                                     "numeral_de", f"{' '.join(c.text for c in prop.cuvinte[i:ultim + 1])} de {subst.text}", "sigura"))
        elif not cere_de and are_de and valoare >= 2 and subst.pos == "NOUN" and any(x.analiza.tr("Number") == "Plur" for x in subst.candidati):
            probleme.append(Problema("numeral_de", [i + 1, subst.idx], f"Sub 20 (sau 101–119) numeralul nu se leagă prin „de”: „{' '.join(c.text for c in prop.cuvinte[i:ultim + 1])} {subst.text}”.",
                                     "numeral_de", f"{' '.join(c.text for c in prop.cuvinte[i:ultim + 1])} {subst.text}", "probabila"))
        # acordul doi/două (și la 12, 22…)
        ultim_cuv = normalizeaza(prop.cuvinte[ultim].text)
        gen_s = subst.tr("Gender")
        if ultim_cuv in ("doi", "două", "doisprezece", "douăsprezece") and gen_s:
            asteptat = {"Masc": {"doi": "doi", "două": "doi", "doisprezece": "doisprezece", "douăsprezece": "doisprezece"},
                        "Fem": {"doi": "două", "două": "două", "doisprezece": "douăsprezece", "douăsprezece": "douăsprezece"}}[gen_s][ultim_cuv]
            if asteptat != ultim_cuv and subst.a.incredere == "baza":
                probleme.append(Problema("acord_numeral", [ultim + 1, subst.idx], f"„{prop.cuvinte[ultim].text}” nu se acordă în gen cu „{subst.text}” ({'masculin' if gen_s == 'Masc' else 'feminin'}).",
                                         "doi_doua", asteptat, "sigura"))
        i = ultim + 1
    return probleme


def gaseste_subiect(prop: Propozitie, iv: int) -> tuple[Cuvant | None, str, list[int]]:
    """Subiectul verbului de la poziția iv (0-based): (cuvântul-cap, persoana, pozițiile membrilor). Întoarce None când e subînțeles.
    Regula: grup nominal / pronume în nominativ, fără prepoziție înainte, cel mai apropiat (întâi la stânga, apoi la dreapta)."""
    n = len(prop.cuvinte)

    def candidat(j: int) -> bool:
        c = prop.cuvinte[j]
        if c.tip == "punct":
            return False
        if c.pos in ("NOUN", "PROPN"):
            # vreo analiză plauzibilă în nominativ-acuzativ (nume proprii: forma de bază nu are caz)
            nominativ = [k for k, x in enumerate(c.candidati) if x.analiza.pos in ("NOUN", "PROPN") and x.analiza.tr("Case") in (None, "Acc,Nom", "Nom")
                         and x.scor >= c.candidati[0].scor - 1.5]
            if not nominativ:
                return False
            if c.tr("Case") not in (None, "Acc,Nom", "Nom"):
                c.ales = nominativ[0]
                c.candidati[nominativ[0]].motive.append("subiect: aleasă analiza în nominativ (subiect)")
            # în interiorul grupului, mergem la cap
            if c.grup is not None and prop.grupuri[c.grup].cap != c.idx:
                return False
            inc = prop.grupuri[c.grup].inceput - 1 if c.grup is not None else j
            ant = prop.cuvinte[inc - 1] if inc > 0 else None
            if ant is not None and (ant.pos == "ADP" or (ant.pos == "DET" and ant.a.lema == "al")):
                return False
            return True
        if c.pos == "PRON" and c.tr("Strength") == "Strong" and c.tr("Case") in ("Nom", "Acc,Nom") and c.tr("PronType") in ("Prs", "Dem", "Ind", "Int,Rel", "Neg", "Tot"):
            ant = prop.cuvinte[j - 1] if j > 0 else None
            return not (ant is not None and ant.pos == "ADP")
        if c.pos == "PRON" and c.tr("PronType") in ("Dem", "Ind", "Neg") and c.tr("Case") == "Acc,Nom":
            ant = prop.cuvinte[j - 1] if j > 0 else None
            return not (ant is not None and ant.pos == "ADP")
        return False

    # la stânga, în aceeași propoziție: ne oprim la orice alt verb, conjuncție, pronume relativ sau virgulă (granițe de propoziție)
    for j in range(iv - 1, -1, -1):
        c = prop.cuvinte[j]
        if j == iv - 1 and c.pos == "AUX":
            continue
        if c.pos in ("VERB", "AUX", "SCONJ", "CCONJ") or (c.pos == "PRON" and c.tr("PronType") == "Int,Rel") or c.tip == "punct" or c.pos == "PART" and normalizeaza(c.text) in ("să", "s-"):
            break
        if any(getattr(prop.cuvinte[k], "atribute_expresie", None) and k <= j < k + prop.cuvinte[k].atribute_expresie[0] and prop.cuvinte[k].a.multicuvant for k in range(max(0, j - 3), j + 1)):
            continue  # cuvânt dintr-o locuțiune recunoscută (pe urmă, în loc de): nu e subiect
        if candidat(j):
            # „Maria și Ion merge”: dacă e al doilea termen al unei coordonări cu „și”, pornim de la primul
            k = j
            while True:
                inc = prop.grupuri[prop.cuvinte[k].grup].inceput - 1 if prop.cuvinte[k].grup is not None else k
                if inc - 2 < 0 or normalizeaza(prop.cuvinte[inc - 1].text) != "și":
                    break
                st = prop.cuvinte[inc - 2]
                cap_st = prop.grupuri[st.grup].cap - 1 if st.grup is not None else inc - 2
                if candidat(cap_st):
                    k = cap_st
                else:
                    break
            return _cap_cu_coordonare(prop, k)
    # la dreapta (subiect postpus) doar când verbul nu poate avea complement direct: verbe intranzitive/copulative uzuale sau pasiv
    verb = prop.cuvinte[iv]
    lema_v = normalizeaza(verb.a.lema)
    pasiv = iv + 1 < n and prop.cuvinte[iv + 1].pos in ("VERB", "AUX") and prop.cuvinte[iv + 1].tr("VerbForm") == "Part" and lema_v == "fi"
    if (lema_v in VERBE_FARA_OBIECT or pasiv or (verb.pos == "AUX" and lema_v == "fi")) and verb.tr("Person") in (None, "3"):
        for j in range(iv + 1, min(n, iv + 6)):
            c = prop.cuvinte[j]
            if (c.pos in ("VERB", "AUX") and not (j == iv + 1 and c.tr("VerbForm") in ("Part", "Inf"))) or c.pos in ("SCONJ", "ADP") or c.tip == "punct":
                break
            if candidat(j) and not any(x.analiza.pos == "ADJ" for x in c.candidati[:3]) and not (c.pos == "PRON" and c.tr("PronType") != "Prs"):
                return _cap_cu_coordonare(prop, j)
    return None, "", []


def _obiect_probabil(prop: Propozitie, j: int) -> bool:
    """Un substantiv articulat imediat după un verb tranzitiv e mai probabil complement direct decât subiect; nu putem ști fără
    informații de valență, deci întoarcem False (îl acceptăm ca subiect) și lăsăm regula „ambiguitate_pastrata” să noteze."""
    return False


def _cap_cu_coordonare(prop: Propozitie, j: int) -> tuple[Cuvant, str, list[int]]:
    c = prop.cuvinte[j]
    membri = [c.idx]
    persoana = c.tr("Person", "3") or "3"
    numar = c.tr("Number")
    # coordonare: „Ion și Maria”, „eu și tu”, „toată mintea și tot trupul”
    k = (prop.grupuri[c.grup].sfarsit if c.grup is not None else c.idx)   # 0-based al următorului = sfârșitul grupului (1-based)
    plural = False
    while k + 1 < len(prop.cuvinte) and normalizeaza(prop.cuvinte[k].text) == "și":
        urm = prop.cuvinte[k + 1]
        cap_urm = prop.grupuri[urm.grup].cap - 1 if urm.grup is not None else k + 1
        if prop.cuvinte[cap_urm].pos not in ("NOUN", "PROPN", "PRON"):
            break
        membri.append(prop.cuvinte[cap_urm].idx)
        plural = True
        p2 = prop.cuvinte[cap_urm].tr("Person", "3") or "3"
        persoana = min(persoana, p2)
        k = prop.grupuri[prop.cuvinte[cap_urm].grup].sfarsit if prop.cuvinte[cap_urm].grup is not None else cap_urm + 1
    if plural:
        numar = "Plur"
    return c, f"{persoana}|{numar or ''}", membri


def verifica_subiect_predicat(baza: Baza, prop: Propozitie) -> tuple[list[Problema], dict[int, tuple[str, str]]]:
    probleme: list[Problema] = []
    subiecte: dict[int, tuple[str, str]] = {}
    for i, cuv in enumerate(prop.cuvinte):
        finit = cuv.pos in ("VERB", "AUX") and (cuv.tr("VerbForm") == "Fin" or (cuv.pos == "AUX" and cuv.tr("Person") and not cuv.tr("VerbForm")))
        if not finit:
            continue
        # la timpurile compuse auxiliarul poartă persoana/numărul; participiul/infinitivul de după el nu se verifică
        if cuv.pos == "VERB" and i > 0 and prop.cuvinte[i - 1].pos == "AUX" and cuv.tr("VerbForm") in ("Part", "Inf"):
            continue
        subiect, pn, membri = gaseste_subiect(prop, i)
        if subiect is None:
            continue
        pers_s, nr_s = pn.split("|")
        if cuv.tr("Person") in ("1", "2") and subiect.pos != "PRON":
            continue  # la persoanele I și II subiectul exprimat e pronume; un substantiv găsit e altceva (vocativ, complement)
        if subiect.pos == "PRON" and subiect.tr("PronType") != "Prs":
            pers_s = "3"
        subiecte[i + 1] = (pers_s, nr_s)
        pers_v, nr_v = cuv.tr("Person"), cuv.tr("Number")
        if not pers_v:
            continue
        # vreo analiză a verbului care se potrivește? (cântă = 3 sg / 3 pl)
        potriviri = [k for k, x in enumerate(cuv.candidati) if x.analiza.pos == cuv.pos and x.analiza.lema == cuv.a.lema
                     and (x.analiza.tr("VerbForm") == "Fin" or (x.analiza.pos == "AUX" and not x.analiza.tr("VerbForm")))
                     and x.analiza.tr("Person") == pers_s and (not nr_s or x.analiza.tr("Number") in (nr_s, None))]
        if potriviri:
            if potriviri[0] != cuv.ales:
                cuv.ales = potriviri[0]
                cuv.candidati[potriviri[0]].motive.append("acord: aleasă analiza care se acordă cu subiectul")
            continue
        if subiect.a.incredere != "baza" or cuv.ambiguu:
            continue
        tinta = {**cuv.a.trasaturi, "Person": pers_s}
        if nr_s:
            tinta["Number"] = nr_s
        sugestie = _forma_sugerata(baza, cuv.a, tinta)
        desc_s = f"persoana {pers_s}" + (f", {'singular' if nr_s == 'Sing' else 'plural'}" if nr_s else "")
        desc_v = f"persoana {pers_v}" + (f", {'singular' if nr_v == 'Sing' else 'plural'}" if nr_v else "")
        probleme.append(Problema("acord_subiect_predicat", [cuv.idx] + membri,
                                 f"Predicatul „{cuv.text}” ({desc_v}) nu se acordă cu subiectul „{' '.join(prop.cuvant(m).text for m in membri)}” ({desc_s}).",
                                 "subiect_predicat", sugestie, "probabila" if len(membri) == 1 else "posibila"))
    return probleme, subiecte


def verifica_prepozitii(baza: Baza, prop: Propozitie) -> list[Problema]:
    """Prepozițiile cu genitivul cer forma de genitiv (asupra copiilor, împotriva lor); cu dativul (datorită lui)."""
    probleme: list[Problema] = []
    for i, cuv in enumerate(prop.cuvinte):
        if cuv.pos != "ADP" or cuv.tr("Case") not in ("Gen", "Dat"):
            continue
        urm = prop.cuvinte[i + 1] if i + 1 < len(prop.cuvinte) else None
        if urm is None or urm.pos not in ("NOUN", "PRON", "DET") or urm.tr("Abbr") == "Yes" or urm.tip == "abrev" or len(urm.text) <= 3:
            continue
        if any(x.analiza.pos == "ADP" for x in urm.candidati[:2]) or normalizeaza(cuv.text) in ("conform cu", "potrivit cu"):
            continue
        if urm.pos == "DET" and urm.tr("PronType") == "Art":
            continue
        if urm.pos == "DET" and urm.tr("Poss") == "Yes":
            continue  # asupra sa / împotriva mea
        if urm.pos == "PRON" and urm.tr("Case") in ("Dat,Gen", "Dat", "Gen"):
            continue
        if any(x.analiza.tr("Case") in ("Dat,Gen", "Dat", "Gen") for x in urm.candidati):
            for k, x in enumerate(urm.candidati):
                if x.analiza.tr("Case") in ("Dat,Gen", "Dat", "Gen"):
                    urm.ales = k
                    x.motive.append(f"acord: prepoziția „{cuv.text}” cere {cuv.tr('Case')}")
                    break
            continue
        if urm.a.incredere != "baza":
            continue
        tinta = {**urm.a.trasaturi, "Case": "Dat,Gen", "Definite": "Def"}
        sugestie = _forma_sugerata(baza, urm.a, tinta)
        probleme.append(Problema("regim_prepozitie", [cuv.idx, urm.idx], f"Prepoziția „{cuv.text}” cere {'genitivul' if cuv.tr('Case') == 'Gen' else 'dativul'}: „{cuv.text} {sugestie or '…'}”.",
                                 "complement_prepozitional", sugestie, "probabila"))
    return probleme
