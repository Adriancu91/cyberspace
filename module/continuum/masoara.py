"""MĂSOARĂ (etapa 6): ce a ieșit, din fișele din jurnalul Kronos (secțiunea 4.6 din plan).

Activitate ≠ progres: verdictul vine doar din măsurători, comparate cu pragul de zgomot al fiecărei capacități.
- **examene**: SUCCES dacă ultimul model are acum valori pentru toate capacitățile cerute, altfel EȘEC.
- **antrenare**: modelul nou păstrat față de cel dinainte, pe capacitatea vizată și pe celelalte (regula 4):
  - SUCCES: capacitatea vizată e mai bună cu mai mult decât pragul ei, iar nicio altă capacitate nu a scăzut mai
    mult decât pragul ei;
  - EȘEC: capacitatea vizată a scăzut peste prag, sau a pierdut alta;
  - NECONCLUDENT: schimbarea e sub prag, nu e nicio oră păstrată nouă, sau lipsesc măsurătorile.
- **hrana**: SUCCES dacă sunt mai multe povești decât înainte.
O unealtă care cade sau depășește timpul înseamnă EȘEC. Decizia păstrat / respins rămâne a lui Kronos; aici se
judecă doar dacă acțiunea lui CONTINUUM a ajutat.
"""

from __future__ import annotations

from typing import Any

from module.continuum import ESEC, NECONCLUDENT, SUCCES, ro_scurt
from module.continuum.alege import Alegere
from module.continuum.evalueaza import StareaOrganismului


def valori(stare: StareaOrganismului | None) -> dict[str, float | None]:
    return {n: c.curent for n, c in stare.capacitati.items()} if stare else {}


def masoara(alegere: Alegere, inainte: StareaOrganismului, dupa: StareaOrganismului | None,
            rezultat: dict[str, Any] | None) -> dict[str, Any]:
    if alegere.plan is None:
        return {"verdict": None, "motiv": "n-am pornit nimic"}
    if rezultat is None or rezultat.get("simulat"):
        return {"verdict": None, "motiv": "simulat: n-am pornit nimic, deci n-am ce măsura"}
    # Totul reversibil: ce model era ultimul și care erau cele mai bune experimente păstrate, înainte de acțiune.
    masurare: dict[str, Any] = {"inainte": valori(inainte), "dupa": valori(dupa),
                                "model_inainte": (inainte.ultimul_model or {}).get("experiment"),
                                "cel_mai_bun_inainte": {n: c.experiment_baza for n, c in inainte.capacitati.items()}}
    if dupa is not None and dupa.ultimul_id > inainte.ultimul_id:
        masurare["fise"] = list(range(inainte.ultimul_id + 1, dupa.ultimul_id + 1))
    if not rezultat["reusit"]:
        return {**masurare, "verdict": ESEC, "motiv": rezultat["motiv"]}
    if dupa is None:
        return {**masurare, "verdict": NECONCLUDENT, "motiv": "nu pot citi starea de după"}
    plan = alegere.plan

    if plan.fel == "examene":
        lipsa = [n for n in plan.detalii["capacitati"] if dupa.capacitati.get(n) is None or dupa.capacitati[n].curent is None]
        if lipsa:
            return {**masurare, "verdict": ESEC, "motiv": f"examenele au rulat, dar lipsesc încă: {', '.join(lipsa)}"}
        return {**masurare, "verdict": SUCCES, "motiv": "modelul #{} are acum: {}".format(
            plan.detalii["experiment"], ", ".join(f"{n} {ro_scurt(dupa.capacitati[n].curent)}" for n in plan.detalii["capacitati"]))}

    if plan.fel == "hrana":
        h = dupa.hrana.get(alegere.nevoie.capacitate, {})
        vechi, nou = plan.detalii.get("povesti_inainte") or 0, h.get("povesti") if h.get("stare") == "ok" else None
        if nou is not None and nou > vechi:
            return {**masurare, "verdict": SUCCES, "motiv": f"hrana a crescut de la {ro_scurt(vechi)} la {ro_scurt(nou)} povești"}
        return {**masurare, "verdict": ESEC, "motiv": "hrana nu a crescut"}

    model = dupa.ultimul_model
    masurare["model_dupa"] = model["experiment"] if model else None
    if model is None or model["experiment"] <= inainte.ultimul_id:
        return {**masurare, "verdict": NECONCLUDENT, "motiv": f"nicio oră păstrată nouă pe linia {plan.linie}"}
    tinta = alegere.nevoie.capacitate
    schimbari = {}
    for nume, c in dupa.capacitati.items():
        vechi = inainte.capacitati[nume].curent if nume in inainte.capacitati else None
        schimbari[nume] = c.castig(c.curent, vechi) if c.curent is not None and vechi is not None else None
    masurare["schimbari"] = schimbari
    pierdute = [n for n, d in schimbari.items() if n != tinta and d is not None and d < -dupa.capacitati[n].prag_zgomot]
    d, prag = schimbari.get(tinta), dupa.capacitati[tinta].prag_zgomot if tinta in dupa.capacitati else None
    if d is None:
        return {**masurare, "verdict": NECONCLUDENT, "motiv": f"{tinta} nu e măsurat și înainte, și după"}
    text = f"{tinta}: {ro_scurt(inainte.capacitati[tinta].curent)} → {ro_scurt(dupa.capacitati[tinta].curent)}"
    if pierdute:
        return {**masurare, "verdict": ESEC, "motiv": f"{text}, dar a pierdut " + ", ".join(
            f"{n} ({ro_scurt(inainte.capacitati[n].curent)} → {ro_scurt(dupa.capacitati[n].curent)}, pragul e "
            f"{ro_scurt(dupa.capacitati[n].prag_zgomot)})" for n in pierdute)}
    if d > prag:
        return {**masurare, "verdict": SUCCES, "motiv": f"{text}, mai bine cu mai mult decât pragul de {ro_scurt(prag)}"}
    if d < -prag:
        return {**masurare, "verdict": ESEC, "motiv": f"{text}, mai rău cu mai mult decât pragul de {ro_scurt(prag)}"}
    return {**masurare, "verdict": NECONCLUDENT, "motiv": f"{text}, schimbare sub pragul de zgomot ({ro_scurt(prag)})"}
