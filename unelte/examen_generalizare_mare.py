"""Examenul mare de generalizare (S15, 22 octombrie 2026, aprobat de supraveghetor): e 2/15 la S4 (b) chiar zero? Și
s-au învățat măcar tipurile antrenate în S11?

- Textele: DOAR din cele 280 de articole puse deoparte de unelte/conversatie_text.py (sămânța 1019; din ele vin și cele 70
  de texte ale examenului nopții 10 și ale lui S4). Unealta le reface exact (cam 30 de secunde, pe procesor).
- **(b2) 50 de întrebări de tipuri care nu există în nicio antrenare** (text, text_v2, text_v3), scrise de mână de Claude
  Code mai jos (B2): 13 tipuri, cel mult 6 pe tip, răspunsul luat din text.
- **(e) 30 de întrebări din tipurile adăugate în S11** (TIPURI_NOI), făcute de intrebari_noi() pe textele puse deoparte,
  cu formulările de la antrenare (alese cu random.Random(2022)).
- Fără „Nu scrie în text.” și fără da/nu (sunt în S4).
Verificările (toate trebuie 0): texte de examen în vreo antrenare, întrebări (b2) al căror început de 4 cuvinte apare la
începutul unei întrebări de antrenare, întrebări copiate din S4, răspunsuri care nu se găsesc în text.

    python unelte/examen_generalizare_mare.py
Iese: docs/conversatie/examen_generalizare_mare.json (+ verificările, pe ecran).
"""

from __future__ import annotations

import json
import random
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

IESIRE = "docs/conversatie/examen_generalizare_mare.json"
ANTRENARI = ("date/conversatie/text/antrenare.jsonl", "date/conversatie/text_v2/antrenare.jsonl",
             "date/conversatie/text_v3/antrenare.jsonl")
NOTA = ("S15 (cascada, aprobat de supraveghetor pe 21 octombrie 2026): 80 de întrebări pe textele celor 280 de articole "
        "puse deoparte (sămânța 1019; niciunul în antrenare). b2 = 50 de întrebări de tipuri care nu există în nicio "
        "antrenare (scrise de mână de Claude Code, 13 tipuri, cel mult 6 pe tip); e = 30 de întrebări din tipurile "
        "adăugate în S11, cu formulările de la antrenare. Fără „Nu scrie” și fără da/nu.")

# (b2): (numărul articolului din cele 280, tipul, întrebarea, răspunsul)
B2: list[tuple[int, str, str, str]] = [
    (4, "tara", "În ce țară se află Peștera Mondmilchloch?", "În Elveția."),
    (63, "tara", "În ce țară se află Podul Pupin?", "În Serbia."),
    (41, "tara", "În ce țară se găsește parcul Efteling?", "În Olanda."),
    (26, "tara", "În ce țară este așezarea Nahalal?", "În Israel."),
    (98, "tara", "În ce țară e orașul Sacavém?", "În Portugalia."),
    (2, "oras", "În ce oraș își are sediul San Antonio Spurs?", "În San Antonio, Texas."),
    (153, "oras", "În ce oraș își are sediul Interpol?", "În Lyon, Franța."),
    (250, "oras", "În ce oraș își are sediul Industria Vehiculelor Elene?", "În Salonic."),
    (269, "oras", "În ce oraș se află Liceul de Artă „Ioan Sima”?", "În Zalău."),
    (279, "oras", "În ce oraș este Loftus Versfeld Stadium?", "În Pretoria, Africa de Sud."),
    (3, "premiu", "Ce premiu a câștigat romanul Week-end la Zuydcoote?", "Prix Goncourt."),
    (113, "premiu", "Ce premiu a câștigat filmul Torment la Cannes?", "Grand Prix du Festival International du Film."),
    (211, "premiu", "Ce medalie a câștigat Patrick Jørgensen la Campionatul Mondial de Scrimă din 2015?",
     "Bronz individual."),
    (12, "actori", "Ce actori joacă rolurile principale în Înapoi în cartier?", "Mody Levente, Florin Matingo, Horia Radu."),
    (17, "actori", "Cine joacă rolurile principale în Planeta Petrila?", "Ion Barbu, Cătălin Cenușă."),
    (82, "actori", "Ce actori joacă în Arsenalul morții?",
     "Christopher Lambert, Ice-T, Michael Halsey, Deborah Van Valkenburgh, Kimberly Warren și Hunter Doughty."),
    (183, "actori", "Ce actori apar în rolurile principale din Amurgul fântânilor?",
     "Mircea Diaconu, Costel Constantin, Mircea Albulescu."),
    (272, "actori", "Cine sunt actorii principali din Doar cu buletinul la Paris?", "Mircea Diaconu și Dorel Vișan."),
    (5, "profesie", "Ce profesie a avut Giulio Magni?", "Arhitect și critic de artă."),
    (22, "profesie", "Ce profesie a avut Julius Lothar Meyer?", "Chimist."),
    (62, "profesie", "Cu ce se ocupa Paul Menu?", "Fotograf și operator de film documentar."),
    (123, "profesie", "Ce meserie a avut Alexandru Fodor?", "Medic."),
    (215, "profesie", "Ce era de profesie Pedro Leandro Ipuche?", "Poet."),
    (241, "profesie", "Cu ce se ocupa Eddie Hazel?", "Chitarist de muzică funk."),
    (37, "post", "Pe ce post joacă Nicolae Milinceanu?", "Atacant."),
    (130, "post", "Pe ce post evoluează Nicolae Daniel Balauru?", "Mijlocaș dreapta."),
    (235, "post", "Pe ce post joacă Mirza Hasanović?", "Mijlocaș defensiv."),
    (76, "post", "Pe ce post a jucat Elena Jianu?", "Intermediar drepta."),
    (229, "post", "Ce post are Nuri Șahin în echipă?", "Mijlocaș."),
    (18, "pictor", "Cine a pictat Persistența memoriei?", "Salvador Dalí."),
    (145, "pictor", "Cine a pictat Mont Sainte-Victoire văzut din Bellevue?", "Paul Cézanne."),
    (190, "pictor", "Al cui tablou este Barca de pescuit?", "Gustave Courbet."),
    (40, "producator", "Cine a produs Pași pe Lună?", "Barry Coe."),
    (72, "producator", "Ce companie a produs Elevi Interdimensionali Zero?", "Bogan Entertainment."),
    (152, "producator", "Ce companie a produs A Million Bid?", "Vitagraph Company of America."),
    (24, "functie", "Ce funcție a avut Jean-Luc Dehaene între 1992 și 1999?", "Prim-ministru al Belgiei."),
    (105, "functie", "Ce funcție a îndeplinit Jan Garrigue Masaryk?", "Ministru de externe al Cehoslovaciei."),
    (73, "functie", "Ce funcție îndeplinește Vladimir Valerievici Iastrebciak?",
     "Ministru al afacerilor externe al auto-proclamatei Republici Moldovenești Nistrene."),
    (146, "functie", "Ce funcție a avut Igor Colenov între 2001 și 2009?",
     "Director general al Serviciului de Grăniceri al Republicii Moldova."),
    (126, "functie", "Ce funcție a avut Pierre Mauroy între 1981 și 1984?", "Prim-ministrul Franței."),
    (51, "functie", "Ce funcție a avut Ștefan-Constantin Ciurel în 1990?", "Primarul municipiului București."),
    (72, "canal", "Pe ce canal a avut premiera Elevi Interdimensionali Zero?", "Pe Cartoon Network."),
    (233, "canal", "Pe ce canal au fost difuzate episoadele din Super motanul?", "Pe ABC."),
    (253, "canal", "Pe ce canal este difuzat serialul Flash?", "Pe The CW."),
    (240, "canal", "Pe ce post de televiziune a avut premiera Ice Road Truckers?", "Pe History Channel."),
    (48, "personaj", "Ce rol a interpretat Mary Frances Crosby în Dallas?", "Kristin Shepard."),
    (154, "personaj", "Prin ce rol a devenit cunoscut Joshua Jackson?", "Peter Bishop."),
    (174, "castigator", "Cine a câștigat Paris-Roubaix 1975?", "Roger De Vlaeminck."),
    (214, "castigator", "Cine a câștigat Turul Italiei 2016?", "Vincenzo Nibali."),
    (127, "sot", "Cu cine s-a căsătorit Beatrice de Sicilia?", "Cu Filip I de Courtenay."),
]
# (e): câte întrebări din fiecare tip S11 (35 posibile pe textele puse deoparte; 30 alese, ca niciun tip să nu le acopere)
E_PE_TIP = {"nou_raion": 5, "nou_familie": 5, "nou_partid": 3}
# scoase de mână: la 252 (Wiener Athletiksport Club) anul 1900 e al echipei de hochei, nu al clubului
E_SCOASE = {252}
_PREFIXE = ("În ", "Pe ", "Din ", "Cu ", "Al ")


def articole_deoparte() -> list[dict[str, Any]]:
    """Cele 280 de articole puse deoparte, refăcute exact ca în unelte/conversatie_text.py (16.000 + 280, sămânța 1019)."""
    from unelte.conversatie_text import articole_bune
    from unelte.conversatie_wikipedia import SURSA
    from unelte.genereaza_conversatie import bucati_interzise
    from unelte.ortografie_ro import citeste_exceptii, citeste_lista

    rng = random.Random(1019)
    bune = articole_bune(RADACINA / SURSA, bucati_interzise(), citeste_lista(), citeste_exceptii(), 150, 700,
                         16000 + 280, Counter(), rng)
    rng.shuffle(bune)
    return bune[:280]


def intrebari_e(articole_: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """(e): intrebari_noi() pe textele puse deoparte, cu o formulare de la antrenare; din tipurile din E_PE_TIP, primele."""
    from unelte.conversatie_text import _intrebare_noua, intrebari_noi

    rng = random.Random(2022)
    luate: Counter[str] = Counter()
    perechi: list[dict[str, Any]] = []
    for i, a in enumerate(articole_):
        for q in intrebari_noi(a["text"], a["x"], a["tip"]):
            if i in E_SCOASE or luate[q["tip"]] >= E_PE_TIP.get(q["tip"], 99):
                continue
            luate[q["tip"]] += 1
            perechi.append({"fel": "text", "limba": "ro", "categorie": "e", "tip": q["tip"], "text": a["text"],
                            "intrebare": _intrebare_noua({**q, "x": a["x"]}, rng), "raspuns": q["raspuns"],
                            "articol": i})
    return perechi


def _miez(raspuns: str) -> str:
    r = raspuns.rstrip(".")
    for p in _PREFIXE:
        r = r.removeprefix(p)
    return r.lower()


def verificari(examen: list[dict[str, Any]], antrenari: list[list[dict[str, Any]]], s4: list[dict[str, Any]]
               ) -> dict[str, Any]:
    """Ce cere S15 la pasul 1 (toate trebuie 0) și cum arată examenul."""
    from unelte.conversatie_text import _inceput

    toate = [p for a in antrenari for p in a]
    texte_antrenare = {p.get("text") for p in toate}
    inceputuri = {_inceput(p["intrebare"]) for p in toate}
    b2 = [p for p in examen if p["categorie"] == "b2"]
    s4_intrebari = {p["intrebare"].strip().lower() for p in s4}
    pe_tip = Counter(p["tip"] for p in b2)
    return {
        "texte_in_antrenare": sum(p["text"] in texte_antrenare for p in examen),
        "b2_inceput_din_antrenare": [p["intrebare"] for p in b2 if _inceput(p["intrebare"]) in inceputuri],
        "intrebari_copiate_din_S4": [p["intrebare"] for p in examen if p["intrebare"].strip().lower() in s4_intrebari],
        "raspunsuri_care_nu_sunt_in_text": [p["intrebare"] for p in examen if _miez(p["raspuns"]) not in p["text"].lower()],
        "b2_tipuri": len(pe_tip), "b2_cel_mult_pe_tip": max(pe_tip.values()), "b2_pe_tip": dict(pe_tip),
        "e_pe_tip": dict(Counter(p["tip"] for p in examen if p["categorie"] == "e")),
        "pe_categorie": dict(Counter(p["categorie"] for p in examen)),
        "articole_folosite": len({p["articol"] for p in examen}),
    }


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    articole_ = articole_deoparte()
    examen = [{"fel": "text", "limba": "ro", "categorie": "b2", "tip": tip, "text": articole_[i]["text"],
               "intrebare": intrebare, "raspuns": raspuns, "articol": i} for i, tip, intrebare, raspuns in B2]
    examen += intrebari_e(articole_)
    for k, p in enumerate(examen):
        p["grup"] = f"mare_{k}"
    antrenari = [[json.loads(r) for r in (RADACINA / c).read_text(encoding="utf-8").splitlines() if r.strip()]
                 for c in ANTRENARI]
    s4 = json.loads((RADACINA / "docs/conversatie/examen_generalizare_401.json").read_text(encoding="utf-8"))["perechi"]
    v = verificari(examen, antrenari, s4)
    (RADACINA / IESIRE).write_text(json.dumps({"nota": NOTA, "verificari": v, "perechi": examen}, ensure_ascii=False,
                                              indent=1), encoding="utf-8")
    print(json.dumps(v, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
