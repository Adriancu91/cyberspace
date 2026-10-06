"""ÎNVAȚĂ (etapa 7): ce reține CONTINUUM din verdict (secțiunea 4.7 din plan).

Fiecare strategie (de ex. „continua:povesti:antrenare”, „dezvolta:fapte:hrana”) are:
- o încredere: pornește de la „incredere_initiala”; SUCCES o crește cu „pas_incredere”, EȘEC o scade;
- numărătorile de succese, eșecuri și rezultate neconcludente.
Experimentul cerut intră în lista „experimente”, cu fișele Kronos și verdictul. În v0 încrederea doar se ține minte;
deciziile după ea (reîncercări, „blocată” după prea multe eșecuri) sunt pentru v1. Ciclurile simulate nu schimbă nimic.
"""

from __future__ import annotations

from typing import Any

from module.continuum import ESEC, NECONCLUDENT, SUCCES
from module.continuum.alege import Alegere


def invata(memorie: dict[str, Any], alegere: Alegere, masurare: dict[str, Any], config: dict[str, Any],
           ciclu: int, timp: str) -> dict[str, Any]:
    verdict = masurare.get("verdict")
    if alegere.plan is None or verdict is None:
        return memorie
    reguli = config["invatare"]
    strategie = memorie["strategii"].setdefault(alegere.plan.strategie, {
        "incredere": reguli["incredere_initiala"], "succese": 0, "esecuri": 0, "neconcludente": 0, "stare": "activa"})
    if verdict == SUCCES:
        strategie["succese"] += 1
        strategie["incredere"] = round(min(1.0, strategie["incredere"] + reguli["pas_incredere"]), 4)
    elif verdict == ESEC:
        strategie["esecuri"] += 1
        strategie["incredere"] = round(max(0.0, strategie["incredere"] - reguli["pas_incredere"]), 4)
    elif verdict == NECONCLUDENT:
        strategie["neconcludente"] += 1
    memorie["experimente"].append({
        "ciclu": ciclu, "timp": timp, "nevoie": alegere.plan.nevoie, "strategie": alegere.plan.strategie,
        "actiune": alegere.plan.descriere, "fise": masurare.get("fise", []), "verdict": verdict,
        "motiv": masurare.get("motiv"), "model_inainte": masurare.get("model_inainte"),
        "cel_mai_bun_inainte": masurare.get("cel_mai_bun_inainte"),  # de unde se poate reveni
    })
    return memorie
