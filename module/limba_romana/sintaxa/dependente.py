"""Analiza sintactică de bază: arbore de dependențe (etichete UD) construit cu reguli explicite.

Nivel de bază, asumat: regulile acoperă propozițiile simple și pe cele cu o subordonată (că/să/dacă/care…);
atașarea grupurilor prepoziționale e ambiguă (la verb sau la substantivul dinainte) și se raportează ca
analiză alternativă când există un substantiv candidat. Rezultatul se evaluează pe UD RRT test (UAS/LAS),
cu cifrele reale în raportul de acoperire.
"""

from __future__ import annotations

from ..text import normalizeaza
from .acord import gaseste_subiect
from .structuri import Cuvant, Propozitie

PREP_NMOD = {"de", "a", "al", "din", "cu", "pentru", "fără", "despre", "la", "în", "pe", "sub", "printre", "între", "dintre", "spre"}
VERBE_XCOMP = {"vrea", "putea", "trebui", "începe", "continua", "termina", "încerca", "dori", "reuși", "ști", "învăța", "prefera", "părea", "trebuie"}


def _este_verb_finit(c: Cuvant) -> bool:
    """Verb la formă personală sau auxiliar al unui timp compus (am/ai/a…, voi/vei…, aș/ar… poartă persoana, fără VerbForm în UD)."""
    return c.pos in ("VERB", "AUX") and (c.tr("VerbForm") == "Fin" or (c.pos == "AUX" and c.tr("Person") is not None and c.tr("VerbForm") is None))


def _predicat(prop: Propozitie, i: int) -> int:
    """Poziția (0-based) a verbului principal al grupului verbal care începe/conține poziția i."""
    c = prop.cuvinte[i]
    n = len(prop.cuvinte)
    if c.pos == "AUX" and i + 1 < n:
        j = i + 1
        while j < n and (prop.cuvinte[j].pos in ("PRON", "ADV", "PART") and prop.cuvinte[j].tr("Strength") == "Weak" or normalizeaza(prop.cuvinte[j].text) in ("fi", "mai", "tot", "cam", "prea")):
            j += 1
        # „a fost citită”, „va fi plecat”, „ar fi putut”: peste auxiliarul „fi/fost” spre participiul principal
        if j < n and prop.cuvinte[j].pos == "AUX" and prop.cuvinte[j].a.lema == "fi" and j + 1 < n and prop.cuvinte[j + 1].pos in ("VERB", "AUX") and prop.cuvinte[j + 1].tr("VerbForm") == "Part":
            return j + 1
        if j < n and prop.cuvinte[j].pos == "AUX" and prop.cuvinte[j].a.lema == "fi" and j + 1 < n and prop.cuvinte[j + 1].pos in ("ADJ", "NOUN", "ADV", "PRON", "NUM", "PROPN"):
            return j + 1
        if j < n and prop.cuvinte[j].pos in ("VERB", "AUX") and prop.cuvinte[j].tr("VerbForm") in ("Part", "Inf"):
            return j
        if j < n and prop.cuvinte[j].pos in ("ADJ", "NOUN", "PRON", "ADV", "NUM", "PROPN") and c.a.lema == "fi":
            return j  # copula: capul e numele predicativ
    if c.pos == "VERB" and c.a.lema == "fi" and i + 1 < n and prop.cuvinte[i + 1].pos in ("ADJ", "NOUN", "ADV", "PRON", "NUM", "PROPN") and prop.cuvinte[i + 1].tr("VerbForm") != "Part":
        return i + 1
    return i


def construieste(prop: Propozitie) -> None:
    n = len(prop.cuvinte)
    if n == 0:
        return
    for c in prop.cuvinte:
        c.cap, c.rel = None, ""
    # 1. predicatele (capetele grupurilor verbale) și rădăcina
    predicate: list[int] = []
    i = 0
    while i < n:
        c = prop.cuvinte[i]
        if _este_verb_finit(c) or (c.pos in ("VERB",) and c.tr("VerbForm") in ("Ger", "Inf") and (i == 0 or prop.cuvinte[i - 1].pos != "AUX")):
            p = _predicat(prop, i)
            if p not in predicate:
                predicate.append(p)
            i = max(p, i) + 1
            continue
        i += 1
    if not predicate:
        # elipsă: propoziție fără verb → capul e primul substantiv/adjectiv/adverb
        for j, c in enumerate(prop.cuvinte):
            if c.pos in ("NOUN", "PROPN", "ADJ", "ADV", "PRON", "NUM", "INTJ"):
                predicate = [j]
                prop.note.append("fără predicat (elipsă sau propoziție nominală)")
                break
        if not predicate:
            predicate = [0]
    # rădăcina: primul predicat care nu e introdus de o conjuncție subordonatoare / pronume relativ
    radacina = predicate[0]
    for p in predicate:
        introdus = False
        for j in range(p - 1, max(-1, p - 6), -1):
            cj = prop.cuvinte[j]
            if cj.pos == "SCONJ" or (cj.pos == "PRON" and cj.tr("PronType") == "Int,Rel") or normalizeaza(cj.text) in ("să", "s-", "că", "dacă", "care", "ce", "cine"):
                introdus = True
                break
            if cj.tip == "punct" or _este_verb_finit(cj) or cj.pos in ("NOUN", "VERB"):
                break
        if not introdus:
            radacina = p
            break
    prop.cuvinte[radacina].cap, prop.cuvinte[radacina].rel = 0, "root"
    # 2. celelalte predicate: conj (coordonate) / ccomp / advcl / acl (relative) / xcomp
    for p in predicate:
        if p == radacina:
            continue
        cap, rel = radacina, "parataxis"
        marca = None
        for j in range(p - 1, max(-1, p - 6), -1):
            cj = prop.cuvinte[j]
            t = normalizeaza(cj.text)
            if cj.pos == "SCONJ" or t in ("că", "dacă", "să", "s-", "deși", "fiindcă", "deoarece", "când", "unde", "cum"):
                marca = cj
                break
            if cj.pos == "CCONJ":
                marca = cj
                break
            if cj.pos == "PRON" and cj.tr("PronType") == "Int,Rel":
                marca = cj
                break
            if cj.tip == "punct" and cj.text != ",":
                break
        # verbul principal din stânga (cel mai apropiat predicat anterior)
        anterioare = [q for q in predicate if q < p]
        stanga = anterioare[-1] if anterioare else radacina
        if marca is None:
            rel = "parataxis"
            cap = stanga
        elif marca.pos == "CCONJ":
            rel, cap = "conj", stanga
        elif marca.pos == "PRON" and marca.tr("PronType") == "Int,Rel":
            # relativă: se atașează la substantivul dinaintea pronumelui
            rel, cap = "acl", stanga
            for j in range(marca.idx - 2, max(-1, marca.idx - 5), -1):
                if prop.cuvinte[j].pos in ("NOUN", "PROPN", "PRON"):
                    cap = j
                    break
        else:
            t = normalizeaza(marca.text)
            if t in ("să", "s-") and prop.cuvinte[stanga].a.lema in VERBE_XCOMP:
                rel = "xcomp"
            elif t in ("că", "să", "s-", "dacă") and prop.cuvinte[stanga].pos == "VERB":
                rel = "ccomp"
            else:
                rel = "advcl"
            cap = stanga
        if cap == p:
            cap = radacina
        prop.cuvinte[p].cap, prop.cuvinte[p].rel = cap + 1, rel
    # 3. grupul verbal: auxiliare, clitice, negație, mărci
    for p in predicate:
        for j in range(p - 1, max(-1, p - 7), -1):
            cj = prop.cuvinte[j]
            if cj.cap is not None:
                break
            t = normalizeaza(cj.text)
            if cj.pos == "AUX":
                # „a fi” + participiu: pasiv când „fi” e la formă personală sau participiu (este citit, a fost citit);
                # „fi” la infinitiv după ar/va/să e auxiliarul timpurilor compuse (ar fi venit, va fi plecat)
                pasiv = cj.a.lema == "fi" and prop.cuvinte[p].tr("VerbForm") == "Part" and cj.tr("VerbForm") in ("Fin", "Part")
                cj.cap, cj.rel = p + 1, "aux:pass" if pasiv else ("cop" if prop.cuvinte[p].pos not in ("VERB", "AUX") else "aux")
            elif cj.pos == "PRON" and cj.tr("Strength") == "Weak":
                if cj.tr("Reflex") == "Yes":
                    cj.cap, cj.rel = p + 1, "expl:pv"
                elif cj.tr("Case") == "Dat":
                    cj.cap, cj.rel = p + 1, "iobj"
                else:
                    cj.cap, cj.rel = p + 1, "obj"
            elif t in ("nu", "n-"):
                cj.cap, cj.rel = p + 1, "advmod"
            elif t in ("să", "s-") or (cj.pos == "PART" and cj.tr("PartType") == "Inf"):
                cj.cap, cj.rel = p + 1, "mark"
            elif cj.pos == "SCONJ":
                cj.cap, cj.rel = p + 1, "mark"
            elif cj.pos == "ADV" and t in ("mai", "tot", "cam", "prea", "și", "chiar", "doar", "numai", "abia"):
                cj.cap, cj.rel = p + 1, "advmod"
            elif cj.pos == "VERB" and cj.a.lema == "fi" and cj.tr("VerbForm") == "Inf":
                cj.cap, cj.rel = p + 1, "aux"
            else:
                break
        # clitice după verb (imperativ, gerunziu): spune-mi, văzându-l
        for j in range(p + 1, min(n, p + 4)):
            cj = prop.cuvinte[j]
            if cj.tip == "clitic" and cj.pos == "PRON" and cj.cap is None:
                cj.cap, cj.rel = p + 1, "expl:pv" if cj.tr("Reflex") == "Yes" else ("iobj" if cj.tr("Case") == "Dat" else "obj")
            elif cj.pos == "AUX" and cj.tip == "clitic" and cj.cap is None:
                cj.cap, cj.rel = p + 1, "aux"
            else:
                break
    # 4. grupurile nominale: interior (det, amod, nummod, flat, case) și atașarea capului
    subiecte: dict[int, int] = {}
    for p in predicate:
        s, _, membri = gaseste_subiect(prop, p)
        if s is not None and prop.cuvinte[p].rel != "acl":
            subiecte[s.idx] = p
            for m in membri[1:]:
                pass
    for g in prop.grupuri:
        cap = prop.cuvant(g.cap)
        for m in g.membri:
            if m == g.cap:
                continue
            cm = prop.cuvant(m)
            if cm.cap is not None:
                continue
            if cm.pos == "DET":
                cm.cap, cm.rel = g.cap, "det"
            elif cm.pos == "ADJ":
                cm.cap, cm.rel = g.cap, "amod"
            elif cm.pos == "NUM":
                cm.cap, cm.rel = g.cap, "nummod"
            elif cm.pos == "PROPN":
                cm.cap, cm.rel = g.cap, "flat"
    # 5. atașarea capetelor nominale și a restului
    ultimul_nominal: int | None = None
    for i, c in enumerate(prop.cuvinte):
        if c.cap is not None:
            if c.pos in ("NOUN", "PROPN", "PRON") and c.rel in ("root",):
                ultimul_nominal = i
            continue
        t = normalizeaza(c.text)
        if c.tip == "punct":
            c.cap, c.rel = radacina + 1, "punct"
            continue
        if c.pos == "ADP":
            # prepoziția se atașează la capul grupului care urmează
            j = i + 1
            while j < n and (prop.cuvinte[j].pos in ("DET", "ADJ", "NUM", "ADV") or prop.cuvinte[j].tip == "clitic"):
                j += 1
            if j < n and prop.cuvinte[j].pos in ("NOUN", "PROPN", "PRON", "ADJ", "NUM", "VERB", "ADV"):
                cap_g = prop.grupuri[prop.cuvinte[j].grup].cap if prop.cuvinte[j].grup is not None else j + 1
                c.cap, c.rel = cap_g, "case"
            else:
                c.cap, c.rel = radacina + 1, "case"
            continue
        if c.pos in ("NOUN", "PROPN", "PRON", "NUM") or (c.pos == "ADJ" and c.grup is None) or (c.pos == "DET" and c.grup is None):
            if c.grup is not None and prop.grupuri[c.grup].cap != c.idx:
                c.cap, c.rel = prop.grupuri[c.grup].cap, "nmod"
                continue
            inc = prop.grupuri[c.grup].inceput - 1 if c.grup is not None else i
            ant = prop.cuvinte[inc - 1] if inc > 0 else None
            verb_stanga = max([p for p in predicate if p < i], default=None)
            verb_dreapta = min([p for p in predicate if p > i], default=None)
            verb = verb_stanga if verb_stanga is not None else (verb_dreapta if verb_dreapta is not None else radacina)
            if c.idx in subiecte:
                p = subiecte[c.idx]
                pasiv = any(prop.cuvinte[k].rel == "aux:pass" for k in range(max(0, p - 4), p))
                c.cap, c.rel = p + 1, "nsubj:pass" if pasiv else "nsubj"
            elif ant is not None and ant.pos == "ADP":
                # grup prepozițional: la verb (obl) sau la substantivul dinainte (nmod) — ambiguitate raportată
                subst_inainte = None
                for k in range(inc - 2, max(-1, inc - 4), -1):
                    if prop.cuvinte[k].pos in ("NOUN", "PROPN"):
                        subst_inainte = k
                        break
                    if prop.cuvinte[k].pos in ("VERB", "AUX") or prop.cuvinte[k].tip == "punct":
                        break
                if subst_inainte is not None and normalizeaza(ant.text) in PREP_NMOD:
                    c.cap, c.rel = subst_inainte + 1, "nmod"
                    if verb_stanga is not None:
                        prop.analize_alternative.append({"cuvant": c.idx, "cap": verb_stanga + 1, "rel": "obl", "motiv": f"grupul „{ant.text} {c.text}” s-ar putea lega și de verbul „{prop.cuvinte[verb_stanga].text}” (obl), nu doar de „{prop.cuvinte[subst_inainte].text}” (nmod)"})
                else:
                    c.cap, c.rel = verb + 1, "obl"
                    if subst_inainte is not None:
                        prop.analize_alternative.append({"cuvant": c.idx, "cap": subst_inainte + 1, "rel": "nmod", "motiv": f"grupul „{ant.text} {c.text}” s-ar putea lega și de substantivul „{prop.cuvinte[subst_inainte].text}” (nmod)"})
            elif ant is not None and ant.pos == "DET" and ant.a.lema == "al":
                for k in range(ant.idx - 2, max(-1, ant.idx - 6), -1):
                    if prop.cuvinte[k].pos in ("NOUN", "PROPN", "PRON"):
                        c.cap, c.rel = k + 1, "nmod"
                        break
                if c.cap is None:
                    c.cap, c.rel = verb + 1, "nmod"
            elif c.tr("Case") == "Dat,Gen" and ant is not None and ant.pos in ("NOUN", "PROPN") and ant.grup is not None:
                c.cap, c.rel = prop.grupuri[ant.grup].cap, "nmod"
            elif ant is not None and ant.pos in ("NOUN", "PROPN") and c.pos in ("NOUN", "PROPN") and c.tr("Case") == "Dat,Gen":
                c.cap, c.rel = ant.idx, "nmod"
            elif verb_stanga is not None and c.tr("Case") in (None, "Acc,Nom", "Acc"):
                c.cap, c.rel = verb_stanga + 1, "obj" if not any(x.rel == "obj" and x.cap == verb_stanga + 1 for x in prop.cuvinte) else "obl"
            elif c.tr("Case") == "Dat,Gen":
                c.cap, c.rel = verb + 1, "iobj"
            else:
                c.cap, c.rel = verb + 1, "obl"
            if c.rel in ("obl", "obj", "nmod", "iobj") and c.pos == "PROPN":
                pass
            continue
        if c.pos == "ADV":
            verb_stanga = max([p for p in predicate if p < i], default=None)
            verb_dreapta = min([p for p in predicate if p > i], default=None)
            # adverb înaintea unui adjectiv: îl modifică pe el
            if i + 1 < n and prop.cuvinte[i + 1].pos == "ADJ" and t in ("foarte", "mai", "prea", "cel", "destul", "tot", "atât", "așa", "extrem", "mult", "puțin"):
                c.cap, c.rel = i + 2, "advmod"
            else:
                verb = verb_dreapta if (verb_stanga is None or (verb_dreapta is not None and verb_dreapta - i <= 2 and i - verb_stanga > 2)) else verb_stanga
                c.cap, c.rel = (verb if verb is not None else radacina) + 1, "advmod"
            continue
        if c.pos == "CCONJ":
            # conjuncția se leagă de elementul coordonat care urmează
            j = i + 1
            while j < n and prop.cuvinte[j].pos in ("DET", "ADV", "NUM"):
                j += 1
            c.cap, c.rel = (j + 1 if j < n else radacina + 1), "cc"
            continue
        if c.pos == "SCONJ":
            verb_dreapta = min([p for p in predicate if p > i], default=radacina)
            c.cap, c.rel = verb_dreapta + 1, "mark"
            continue
        if c.pos == "INTJ":
            c.cap, c.rel = radacina + 1, "discourse"
            continue
        if c.pos in ("ADJ",):
            # adjectiv fără substantiv în grup: nume predicativ sau modificator al substantivului dinainte
            if i > 0 and prop.cuvinte[i - 1].pos in ("NOUN", "PROPN"):
                c.cap, c.rel = i, "amod"
            else:
                verb = max([p for p in predicate if p < i], default=radacina)
                c.cap, c.rel = verb + 1, "xcomp"
            continue
        if c.pos in ("VERB", "AUX"):
            verb = max([p for p in predicate if p < i], default=radacina)
            c.cap, c.rel = verb + 1, "acl" if c.tr("VerbForm") == "Part" else ("advcl" if c.tr("VerbForm") == "Ger" else "xcomp")
            continue
        c.cap, c.rel = radacina + 1, "dep"
    # 6. coordonarea nominală: „Ion și Maria” → Maria conj Ion
    for i, c in enumerate(prop.cuvinte):
        if c.pos == "CCONJ" and c.cap and c.cap - 1 < n:
            dreapta = prop.cuvinte[c.cap - 1]
            if dreapta.pos in ("NOUN", "PROPN", "PRON", "ADJ", "NUM") and dreapta.rel not in ("root", "nsubj", "nsubj:pass"):
                for k in range(i - 1, max(-1, i - 6), -1):
                    ck = prop.cuvinte[k]
                    if ck.pos == dreapta.pos or (ck.pos in ("NOUN", "PROPN") and dreapta.pos in ("NOUN", "PROPN")):
                        if ck.grup is not None and prop.grupuri[ck.grup].cap != ck.idx:
                            continue
                        dreapta.cap, dreapta.rel = ck.idx, "conj"
                        break
    # 6b. conjuncția dinaintea unui subiect leagă propoziții: se atașează la predicatul subiectului (dar mama a rămas → cc la „rămas”)
    for c in prop.cuvinte:
        if c.pos == "CCONJ" and c.cap and c.cap - 1 < n:
            dreapta = prop.cuvinte[c.cap - 1]
            if dreapta.rel in ("nsubj", "nsubj:pass") and dreapta.cap:
                c.cap = dreapta.cap
    # 7. fără cicluri: un cuvânt nu poate fi propriul cap; capetele lipsă merg la rădăcină
    for c in prop.cuvinte:
        if c.cap is None or c.cap == c.idx:
            c.cap, c.rel = (radacina + 1, c.rel or "dep") if c.idx != radacina + 1 else (0, "root")
