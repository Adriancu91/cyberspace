"""Lanțul de analiză a unei propoziții: tokenizare → analize morfologice → dezambiguizare → grupuri nominale →
acord → dependențe (de bază) → a doua dezambiguizare (cu subiectele găsite)."""

from __future__ import annotations

from ..baza import Baza
from ..dezambiguizare import scoreaza
from ..morfologie.analizator import Analizator
from ..text import Token, normalizeaza, tokenizeaza
from . import acord, dependente
from .structuri import Candidat, Cuvant, Problema, Propozitie


def _potriveste_expresii(baza: Baza, tokeni: list[Token], maxim: int = 4) -> dict[int, tuple[int, list[dict]]]:
    """Expresiile multicuvânt din bază (locuțiuni): poziția de început → (număr de tokeni, analizele). Doar potrivire exactă."""
    rez: dict[int, tuple[int, list[dict]]] = {}
    i = 0
    while i < len(tokeni):
        gasit = None
        for lung in range(min(maxim, len(tokeni) - i), 1, -1):
            text = " ".join(t.text for t in tokeni[i:i + lung])
            if any(t.tip == "punct" for t in tokeni[i:i + lung]):
                continue
            randuri = [r for r in baza.cauta_forma(text, si_fara_diacritice=False) if r["multicuvant"] and r["pos"] in ("ADP", "SCONJ", "CCONJ", "ADV", "INTJ")]
            if randuri:
                gasit = (lung, randuri)
                break
        if gasit:
            rez[i] = gasit
            i += gasit[0]
        else:
            i += 1
    return rez


def analizeaza_propozitie(baza: Baza, analizator: Analizator, text: str, cu_dependente: bool = True) -> Propozitie:
    tokeni = tokenizeaza(text)
    expresii = _potriveste_expresii(baza, tokeni)
    cuvinte: list[Cuvant] = []
    from ..baza import desparte_trasaturi
    from ..morfologie.analizator import Analiza
    for i, t in enumerate(tokeni):
        candidati = [Candidat(a) for a in analizator.analizeaza(t.text, t.tip)]
        if i in expresii:
            # expresia fixă rămâne o înșiruire de tokeni (ca în UD RRT); primul token primește și analiza expresiei,
            # următorii se vor lega de el prin relația „fixed”
            lung, randuri = expresii[i]
            for r in randuri:
                a = Analiza(r["forma"], r["lema"], r["lexem_id"], r["pos"], desparte_trasaturi(r["trasaturi"]), "baza", r["statut"], r["gen"], True,
                            sum(p["frecventa"] for p in r["provenienta"] if p["sursa_id"] == "ud_rrt"),
                            ["expresie fixă din bază: " + ", ".join(sorted({p['sursa_id'] for p in r['provenienta']}))], r["atribute"])
                candidati.insert(0, Candidat(a, 0.0, []))
        cuv = Cuvant(len(cuvinte) + 1, t.text, t.tip, candidati, spatiu_dupa=t.spatiu_dupa)
        if i in expresii:
            cuv.atribute_expresie = (expresii[i][0], " ".join(x.text for x in tokeni[i:i + expresii[i][0]]))
        cuvinte.append(cuv)
    prop = Propozitie(text, cuvinte)
    scoreaza(prop)
    prop.grupuri = acord.grupuri_nominale(prop)
    probleme: list[Problema] = []
    for g in prop.grupuri:
        probleme.extend(acord.verifica_acord_grup(baza, prop, g))
    probleme.extend(acord.verifica_al(baza, prop))
    probleme.extend(acord.verifica_numerale(baza, prop))
    probleme.extend(acord.verifica_prepozitii(baza, prop))
    pr_sp, subiecte = acord.verifica_subiect_predicat(baza, prop)
    probleme.extend(pr_sp)
    if subiecte:
        scoreaza(prop, subiect_persoana=subiecte)
        prop.grupuri = acord.grupuri_nominale(prop) if not prop.grupuri else prop.grupuri
    # necunoscutele
    for c in prop.cuvinte:
        if c.necunoscut:
            probleme.append(Problema("necunoscut", [c.idx], f"Cuvântul „{c.text}” nu e cunoscut (nu e în nicio sursă și nu se potrivește cu nicio regulă).", "necunoscute", None, "sigura"))
        elif all(x.analiza.incredere in ("ipoteza", "necunoscut") for x in c.candidati) and c.tip == "cuvant":
            probleme.append(Problema("ipoteza", [c.idx], f"Cuvântul „{c.text}” nu e în bază ca formă; analiza e o ipoteză: {c.a.dovezi[0] if c.a.dovezi else ''}", "necunoscute", None, "posibila"))
        elif c.a.incredere == "fara_diacritice" and any(ch in "aist" for ch in normalizeaza(c.text)):
            forma_corecta = c.a.forma
            if normalizeaza(forma_corecta) != normalizeaza(c.text):
                probleme.append(Problema("ortografie", [c.idx], f"„{c.text}” pare scris fără diacritice: „{forma_corecta}”.", "diacritice", forma_corecta, "probabila"))
    prop.probleme = probleme
    if cu_dependente:
        dependente.construieste(prop)
        for i, c in enumerate(prop.cuvinte):
            exp = getattr(c, "atribute_expresie", None)
            if exp and c.ales is not None and c.candidati[c.ales].analiza.multicuvant:
                for k in range(i + 1, min(len(prop.cuvinte), i + exp[0])):
                    prop.cuvinte[k].cap, prop.cuvinte[k].rel = c.idx, "fixed"
    return prop
