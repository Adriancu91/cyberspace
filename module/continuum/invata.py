"""ÎNVAȚĂ (etapa 7): ce reține CONTINUUM din verdict (secțiunea 4.7 din plan).

Fiecare strategie (de ex. „continua:povesti:antrenare”, „dezvolta:fapte:hrana”) are:
- o încredere: pornește de la „incredere_initiala”; SUCCES o crește cu „pas_incredere”, EȘEC o scade;
- numărătorile: succese, succese scumpe, eșecuri (și câte la rând), rezultate neconcludente, succese în așteptare;
- câștigurile pe oră de placă ale succeselor ei (pentru „SUCCES SCUMP”, masoara.py).

În v1:
- **SUCCES** mută încrederea doar după confirmare. Scorul nou e un candidat (stabilitate.py); până la a doua
  măsurătoare, succesul stă „în așteptare”.
- **SUCCES SCUMP** nu urcă încrederea.
- **Limita de reîncercări:** după [anti_bucla] max_esecuri eșecuri la rând, strategia e „blocată” (ALEGE nu o mai
  alege), iar omul primește un raport.

Experimentul cerut intră în lista „experimente”, cu fișele Kronos, costul și verdictul. Ciclurile simulate nu schimbă
nimic.
"""

from __future__ import annotations

from typing import Any, Callable

from module.continuum import ESEC, NECONCLUDENT, SUCCES, SUCCES_SCUMP
from module.continuum.alege import Alegere

BLOCATA = "blocată"


def strategie_noua(reguli: dict[str, Any]) -> dict[str, Any]:
    return {"incredere": reguli["incredere_initiala"], "succese": 0, "esecuri": 0, "neconcludente": 0, "stare": "activa",
            "succese_scumpe": 0, "in_asteptare": 0, "esecuri_la_rand": 0, "castiguri_pe_ora": []}


def strategia(memorie: dict[str, Any], nume: str, reguli: dict[str, Any]) -> dict[str, Any]:
    strategie = memorie["strategii"].setdefault(nume, strategie_noua(reguli))
    for cheie, implicit in strategie_noua(reguli).items():  # o memorie din v0 n-are câmpurile noi
        strategie.setdefault(cheie, implicit)
    return strategie


def aplica_succes(strategie: dict[str, Any], reguli: dict[str, Any], castig_pe_ora: float | None) -> None:
    strategie["succese"] += 1
    strategie["esecuri_la_rand"] = 0
    strategie["incredere"] = round(min(1.0, strategie["incredere"] + reguli["pas_incredere"]), 4)
    if castig_pe_ora is not None:
        strategie["castiguri_pe_ora"].append(castig_pe_ora)


def dupa_confirmare(memorie: dict[str, Any], config: dict[str, Any]) -> Callable[[dict[str, Any]], None]:
    """Pentru stabilitate.actualizeaza: când un candidat cu o strategie în așteptare e confirmat, succesul ei se aplică;
    când e infirmat, devine neconcludent."""
    def aplica(candidat: dict[str, Any]) -> None:
        strategie = strategia(memorie, candidat["strategie"], config["invatare"])
        strategie["in_asteptare"] = max(0, strategie["in_asteptare"] - 1)
        if candidat["stare"] == "confirmat":
            aplica_succes(strategie, config["invatare"], candidat.get("castig_pe_ora"))
        else:
            strategie["neconcludente"] += 1
    return aplica


def invata(memorie: dict[str, Any], alegere: Alegere, masurare: dict[str, Any], config: dict[str, Any],
           ciclu: int, timp: str) -> dict[str, Any]:
    verdict = masurare.get("verdict")
    if alegere.plan is None or verdict is None:
        return memorie
    reguli = config["invatare"]
    strategie = strategia(memorie, alegere.plan.strategie, reguli)
    confirmare = None
    if verdict == SUCCES:
        if masurare.get("confirmat", True):
            aplica_succes(strategie, reguli, masurare.get("castig_pe_ora"))
        else:
            strategie["in_asteptare"] += 1
            confirmare = "în așteptarea unei a doua măsurători"
    elif verdict == SUCCES_SCUMP:
        strategie["succese_scumpe"] += 1
        strategie["esecuri_la_rand"] = 0
        if masurare.get("castig_pe_ora") is not None:
            strategie["castiguri_pe_ora"].append(masurare["castig_pe_ora"])
    elif verdict == ESEC:
        strategie["esecuri"] += 1
        strategie["esecuri_la_rand"] += 1
        strategie["incredere"] = round(max(0.0, strategie["incredere"] - reguli["pas_incredere"]), 4)
        if strategie["esecuri_la_rand"] >= config["anti_bucla"]["max_esecuri"] and strategie["stare"] != BLOCATA:
            strategie.update(stare=BLOCATA, blocata_la=timp)
            memorie["de_raportat"].append({
                "tip": "strategie_blocata", "strategie": alegere.plan.strategie, "ciclu": ciclu, "timp": timp,
                "esecuri_la_rand": strategie["esecuri_la_rand"], "ultimul_motiv": masurare.get("motiv")})
    elif verdict == NECONCLUDENT:
        strategie["neconcludente"] += 1
    memorie["experimente"].append({
        "ciclu": ciclu, "timp": timp, "nevoie": alegere.plan.nevoie, "strategie": alegere.plan.strategie,
        "actiune": alegere.plan.descriere, "fise": masurare.get("fise", []), "verdict": verdict,
        "motiv": masurare.get("motiv"), "model_inainte": masurare.get("model_inainte"),
        "cel_mai_bun_inainte": masurare.get("cel_mai_bun_inainte"),  # de unde se poate reveni
        "cost": masurare.get("cost"), "castig_pe_ora": masurare.get("castig_pe_ora"), "confirmare": confirmare,
    })
    return memorie
