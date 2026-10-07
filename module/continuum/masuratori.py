"""Măsurătorile din jurnalul Kronos, pentru EVALUEAZĂ și pentru zgomotul învățat.

O valoare a unei capacități pe modelul unei fișe vine, în ordine:
1. din scorurile fișei (examenul oficial);
2. din fișa unei unelte de examen care pomenește experimentul (ex. unelte/examen_profesor.py). E mai nouă decât ora
   lui și poate fi mai precisă (ex. nota pe 40 de povești, nu pe 20);
3. din criteriile fișei (examene_suplimentare, date la sfârșitul orei).
"""

from __future__ import annotations

import math
from typing import Any

REUSITE = ("pastrat", "respins")  # ca la unelte/antrenare_lunga.py: o oră făcută = un experiment reușit


def numar(valoare: Any) -> bool:
    return isinstance(valoare, (int, float)) and not isinstance(valoare, bool) and math.isfinite(valoare)


def criterii_din(fisa: dict[str, Any]) -> dict[str, Any]:
    """Criteriile unei ore (examene_suplimentare): cu [criterii] în fișă; fără, în răspunsul dupa_examen."""
    return fisa.get("criterii") or (fisa.get("dupa_examen") or {}).get("criterii") or {}


def masuratori_unelte(fise: list[dict[str, Any]], config: dict[str, Any]) -> dict[tuple[str, int], dict[str, Any]]:
    """(linia uneltei, experimentul) → scorurile fișelor ei pentru acel experiment (o fișă mai nouă le înlocuiește pe
    cele pe care le are și le păstrează pe rest)."""
    linii = {cap["unealta"]["linie"] for cap in config["capacitati"].values() if cap["unealta"]}
    rezultat: dict[tuple[str, int], dict[str, Any]] = {}
    for fisa in sorted((f for f in fise if f.get("linie") in linii), key=lambda f: f.get("id", 0)):
        experiment = ((fisa.get("module") or {}).get("elev") or {}).get("experiment")
        if isinstance(experiment, int):
            rezultat.setdefault((fisa["linie"], experiment), {}).update(fisa.get("scoruri") or {})
    return rezultat


def valoare(fisa: dict[str, Any], cap: dict[str, Any], unelte: dict[tuple[str, int], dict[str, Any]]) -> float | None:
    """Valoarea capacității pe modelul unei fișe, sau None dacă n-a fost măsurată."""
    oficial = (fisa.get("scoruri") or {}).get(cap["metrica"])
    if numar(oficial):
        return float(oficial)
    if cap["unealta"]:  # măsurarea cu unealta vine după oră: cea mai nouă
        scor = unelte.get((cap["unealta"]["linie"], fisa.get("id")), {}).get(cap["unealta"]["scor"])
        if numar(scor):
            return float(scor)
    criteriu = criterii_din(fisa).get(cap["metrica"])
    return float(criteriu) if numar(criteriu) else None
