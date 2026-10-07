"""MĂSOARĂ (etapa 6): ce a ieșit, din fișele din jurnalul Kronos (secțiunea 4.6 din plan).

Activitate ≠ progres: verdictul vine doar din măsurători, comparate cu pragul folosit al fiecărei capacități
(max(podea, zgomot învățat)).
- **examene**: SUCCES dacă ultimul model are acum valori pentru toate capacitățile cerute, altfel EȘEC.
- **antrenare**: modelul nou păstrat față de cel dinainte, pe capacitatea vizată și pe celelalte (regula 4):
  - SUCCES: capacitatea vizată e mai bună cu mai mult decât pragul ei, iar nicio altă capacitate nu a scăzut mai
    mult decât pragul ei;
  - EȘEC: capacitatea vizată a scăzut peste prag, sau a pierdut alta;
  - NECONCLUDENT: schimbarea e sub prag, nu e nicio oră păstrată nouă, sau lipsesc măsurătorile.
- **hrana**: SUCCES dacă sunt mai multe povești decât înainte.
- **raport** (repara): scris; nu e un verdict de măsurat.

v1, punctul 4, eficiența:
- MĂSOARĂ ia și costul acțiunii: orele pe placă (cât au durat comenzile), pașii pe secundă și memoria video (din
  fișele noi).
- Un SUCCES la antrenare al cărui câștig pe oră e sub [eficienta] fractie_scump din media strategiei (din succesele
  ei de dinainte) devine **SUCCES SCUMP**: nu urcă încrederea.
- Un SUCCES la antrenare face din scorul nou un **candidat** (stabilitate.py): încrederea urcă abia după confirmare.

O unealtă care cade sau depășește timpul înseamnă EȘEC. Decizia păstrat / respins rămâne a lui Kronos; aici se
judecă doar dacă acțiunea lui CONTINUUM a ajutat.
"""

from __future__ import annotations

from typing import Any

from module.continuum import ESEC, NECONCLUDENT, SUCCES, SUCCES_SCUMP, peste, ro, ro_scurt
from module.continuum.alege import Alegere
from module.continuum.evalueaza import StareaOrganismului
from module.continuum.masuratori import REUSITE, numar


def valori(stare: StareaOrganismului | None) -> dict[str, float | None]:
    return {n: c.curent for n, c in stare.capacitati.items()} if stare else {}


def cost(rezultat: dict[str, Any] | None, fise: list[dict[str, Any]] | None, ultimul_id: int) -> dict[str, Any]:
    """Orele pe placă (cât au durat comenzile), pașii pe secundă și memoria video (din fișele reușite noi)."""
    secunde = sum(c.get("secunde") or 0 for c in (rezultat or {}).get("comenzi", []) if isinstance(c, dict))
    viteze, memorie = [], []
    for fisa in fise or []:
        s = fisa.get("statistici_antrenare") or {}
        if fisa.get("id", 0) <= ultimul_id or fisa.get("decizie") not in REUSITE:
            continue
        if numar(s.get("pasi")) and numar(s.get("secunde_bucla")) and s["secunde_bucla"] > 0:
            viteze.append(s["pasi"] / s["secunde_bucla"])
        if numar(s.get("memorie_rezervata_mb")):
            memorie.append(s["memorie_rezervata_mb"])
    return {"secunde_placa": round(secunde, 1), "ore_placa": round(secunde / 3600, 3),
            "pasi_pe_secunda": round(sum(viteze) / len(viteze), 2) if viteze else None,
            "memorie_video_mb": max(memorie) if memorie else None}


def masoara(alegere: Alegere, inainte: StareaOrganismului, dupa: StareaOrganismului | None,
            rezultat: dict[str, Any] | None, fise_dupa: list[dict[str, Any]] | None = None,
            memorie: dict[str, Any] | None = None, config: dict[str, Any] | None = None) -> dict[str, Any]:
    if alegere.plan is None:
        return {"verdict": None, "motiv": "n-am pornit nimic"}
    if rezultat is None or rezultat.get("simulat"):
        return {"verdict": None, "motiv": "simulat: n-am pornit nimic, deci n-am ce măsura"}
    if alegere.plan.fel == "raport":
        return {"verdict": None, "motiv": f"raport scris: {rezultat.get('raport')}"}
    # Totul reversibil: ce model era ultimul și care erau cele mai bune experimente păstrate, înainte de acțiune.
    masurare: dict[str, Any] = {"inainte": valori(inainte), "dupa": valori(dupa),
                                "model_inainte": (inainte.ultimul_model or {}).get("experiment"),
                                "cel_mai_bun_inainte": {n: c.experiment_baza for n, c in inainte.capacitati.items()},
                                "cost": cost(rezultat, fise_dupa, inainte.ultimul_id)}
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
    pierdute = [n for n, d in schimbari.items() if n != tinta and d is not None and peste(-d, dupa.capacitati[n].prag_zgomot)]
    d, prag = schimbari.get(tinta), dupa.capacitati[tinta].prag_zgomot if tinta in dupa.capacitati else None
    if d is None:
        return {**masurare, "verdict": NECONCLUDENT, "motiv": f"{tinta} nu e măsurat și înainte, și după"}
    text = f"{tinta}: {ro_scurt(inainte.capacitati[tinta].curent)} → {ro_scurt(dupa.capacitati[tinta].curent)}"
    if pierdute:
        return {**masurare, "verdict": ESEC, "motiv": f"{text}, dar a pierdut " + ", ".join(
            f"{n} ({ro_scurt(inainte.capacitati[n].curent)} → {ro_scurt(dupa.capacitati[n].curent)}, pragul e "
            f"{ro_scurt(dupa.capacitati[n].prag_zgomot)})" for n in pierdute)}
    if peste(-d, prag):
        return {**masurare, "verdict": ESEC, "motiv": f"{text}, mai rău cu mai mult decât pragul de {ro_scurt(prag)}"}
    if not peste(d, prag):
        return {**masurare, "verdict": NECONCLUDENT, "motiv": f"{text}, schimbare sub pragul de zgomot ({ro_scurt(prag)})"}

    verdict, motiv = SUCCES, f"{text}, mai bine cu mai mult decât pragul de {ro_scurt(prag)}"
    masurare["candidat"] = {"capacitate": tinta, "experiment": model["experiment"], "valoare": dupa.capacitati[tinta].curent}
    ore = masurare["cost"]["secunde_placa"] / 3600
    if ore > 0:
        masurare["castig_pe_ora"] = round(d / ore, 6)
        istoric = (((memorie or {}).get("strategii") or {}).get(plan.strategie) or {}).get("castiguri_pe_ora") or []
        if istoric and config is not None:
            media, fractie = sum(istoric) / len(istoric), config["eficienta"]["fractie_scump"]
            if masurare["castig_pe_ora"] < fractie * media:
                verdict = SUCCES_SCUMP
                motiv += (f"; dar câștigul pe oră de placă ({ro_scurt(masurare['castig_pe_ora'])}) e sub {ro(100 * fractie)}% "
                          f"din media strategiei ({ro_scurt(media)}): SUCCES SCUMP, încrederea nu urcă")
    return {**masurare, "verdict": verdict, "motiv": motiv}
