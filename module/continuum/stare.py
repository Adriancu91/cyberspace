"""STARE (etapa 8): ce ține minte CONTINUUM, în lucru/continuum/ (secțiunile 4.8, 10 și 11 din plan).

**stare.json** e memoria mică, rescrisă la fiecare ciclu. Ține:
- **ciclu**: numărul ultimului ciclu.
- **capacitati**, pentru fiecare:
  - metrica și direcția;
  - linia de bază, plus experimentul care a dat-o;
  - ultimul scor, pe ce model și când s-a schimbat ultima oară.
  Liniile de bază vin doar din experimente păstrate de Kronos.
- **strategii** și **experimente**: din ÎNVAȚĂ.
- **probleme**, deschise sau rezolvate. Se deschid singure când apar și se închid când dispar: un modul care nu se
  încarcă, o etapă care a căzut, configurarea stricată.
- **de_reluat**: gol în v0.
- v1: **vector_capacitati** (toate capacitățile, cu scor, linie de bază, zonă, prag folosit, procent), **candidati**
  (coada de confirmare, stabilitate.py), **racire** (nevoie → ciclul până la care nu se reia), **rapoarte** (ce a primit
  omul) și **de_raportat** (strategiile blocate, până se scrie raportul).

**cicluri.jsonl** are un rând pe ciclu și doar crește. Peste „jurnal_max_mb” se mută deoparte (cicluri_<data>.jsonl)
și se începe altul. Nu se editează de mână, ca jurnalul Kronos.

Fără SQLite: doar JSON, ca restul proiectului.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from module.continuum import ROSIE
from module.continuum.evalueaza import StareaOrganismului


def memorie_goala() -> dict[str, Any]:
    return {"versiune": 1, "ciclu": 0, "actualizat": None, "capacitati": {}, "strategii": {}, "experimente": [],
            "probleme": [], "de_reluat": [],
            # v1: vectorul capacităților, coada de confirmare, răcirea nevoilor, rapoartele către om
            "vector_capacitati": {}, "candidati": [], "racire": {}, "rapoarte": [], "de_raportat": []}


def incarca(director: Path) -> dict[str, Any]:
    """Memoria de data trecută. Dacă fișierul e stricat, îl mută deoparte (nu-l șterge) și pornește cu una goală."""
    fisier = director / "stare.json"
    if not fisier.exists():
        return memorie_goala()
    try:
        memorie = json.loads(fisier.read_text(encoding="utf-8"))
        if not isinstance(memorie, dict):
            raise ValueError("nu e un obiect JSON")
    except (OSError, ValueError) as e:
        deoparte = fisier.with_name(f"stare_stricata_{datetime.now():%Y%m%d_%H%M%S}.json")
        fisier.replace(deoparte)
        memorie = memorie_goala()
        memorie["probleme"].append({"cheie": "stare.json", "ce": f"stare.json era stricat ({e}); mutat în {deoparte.name}",
                                    "deschisa": False, "de_la": None, "rezolvata": None})
        return memorie
    return {**memorie_goala(), **memorie}


def salveaza(director: Path, memorie: dict[str, Any]) -> None:
    """Scrie întâi alături, apoi înlocuiește: o oprire bruscă nu lasă un fișier pe jumătate."""
    director.mkdir(parents=True, exist_ok=True)
    temporar = director / "stare.json.tmp"
    temporar.write_text(json.dumps(memorie, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    os.replace(temporar, director / "stare.json")


def actualizeaza_capacitati(memorie: dict[str, Any], stare: StareaOrganismului, timp: str) -> None:
    model = (stare.ultimul_model or {}).get("experiment")
    for nume, c in stare.capacitati.items():
        m = memorie["capacitati"].setdefault(nume, {})
        if c.curent is not None and (m.get("ultimul_scor"), m.get("pe_modelul")) != (c.curent, model):
            m["ultima_schimbare"] = timp
        if not m.get("baza_confirmata"):  # o linie de bază confirmată se mută doar prin stabilitate.py
            m.update(linie_de_baza=c.linie_de_baza, experiment_baza=c.experiment_baza)
        m.update({"metrica": c.metrica, "mai_mare_e_mai_bine": c.mai_mare_e_mai_bine, "ultimul_scor": c.curent,
                  "pe_modelul": model, "procent": c.procent, "disponibila": c.disponibila, "zona": c.zona,
                  "prag_folosit": c.prag_zgomot, "retentie": c.retentie, "retentie_fata_de": c.retentie_fata_de})
    memorie["vector_capacitati"] = stare.vector()
    for raport in memorie["rapoarte"]:  # zona roșie s-a dus: raportul se închide, iar o recădere aduce unul nou
        c = stare.capacitati.get(raport.get("capacitate"))
        if raport.get("tip") == "repara" and raport.get("deschis") and (c is None or c.zona != ROSIE):
            raport.update(deschis=False, inchis=timp, zona_la_inchidere=c.zona if c else None)


def actualizeaza_probleme(memorie: dict[str, Any], curente: dict[str, str], timp: str) -> None:
    """Problemele de acum (cheie → ce): cele noi se deschid, cele care au dispărut se închid."""
    deschise = {p["cheie"]: p for p in memorie["probleme"] if p.get("deschisa")}
    for cheie, ce in curente.items():
        if cheie not in deschise:
            memorie["probleme"].append({"cheie": cheie, "ce": ce, "deschisa": True, "de_la": timp, "rezolvata": None})
    for cheie, problema in deschise.items():
        if cheie not in curente:
            problema["deschisa"], problema["rezolvata"] = False, timp


def scrie_ciclu(director: Path, rand: dict[str, Any], max_mb: float) -> None:
    director.mkdir(parents=True, exist_ok=True)
    fisier = director / "cicluri.jsonl"
    if fisier.exists() and fisier.stat().st_size > max_mb * 1024 * 1024:
        fisier.replace(director / f"cicluri_{datetime.now():%Y%m%d_%H%M%S}.jsonl")
    with fisier.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rand, ensure_ascii=False, default=str) + "\n")


def citeste_cicluri(director: Path, ultimele: int) -> list[dict[str, Any]]:
    fisier = director / "cicluri.jsonl"
    if not fisier.exists():
        return []
    randuri = []
    for rand in fisier.read_text(encoding="utf-8").splitlines()[-ultimele:]:
        try:
            randuri.append(json.loads(rand))
        except json.JSONDecodeError:
            continue
    return randuri
