"""Orice model salvat de Kronos, după numărul experimentului sau ultimul de pe o linie de jurnal (pentru examenele din
unelte/: examenul de fapte și examenul profesorului)."""

from __future__ import annotations

from typing import Any

from kronos.cai import gaseste_model
from kronos.registru import Registru


def fisa_modelului(jurnal: Any, experiment: int | None = None, linie: str | None = None) -> dict[str, Any]:
    """Fișa experimentului dat sau, cu linia, a ultimului experiment de pe ea care are un model salvat de Kronos."""
    if experiment is not None:
        fise = [f for f in jurnal.istoric() if f["id"] == experiment and f.get("model_salvat")]
        if not fise:
            raise ValueError(f"Experimentul #{experiment} nu există în jurnal sau n-are un model salvat de Kronos.")
        return fise[0]
    fise = [f for f in jurnal.istoric(linie) if f.get("model_salvat")]
    if not fise:
        raise ValueError(f"Linia „{linie}” n-are niciun model salvat de Kronos.")
    return fise[-1]


def incarca_modelul(fisa: dict[str, Any], dispozitiv: str = "") -> Any:
    """Modelul din fișă: clasa din fișă (module.model.cale), setările lui și greutățile salvate. Cu dispozitiv (ex.
    „cpu”), pe acela: un model mic se poate examina pe procesor cât placa video lucrează la altceva."""
    setari = {**fisa["setari"]["model"], **({"dispozitiv": dispozitiv} if dispozitiv else {})}
    model = Registru().creeaza("model", fisa["module"]["model"]["cale"], setari).instanta
    model.incarca(gaseste_model(fisa["model_salvat"]))
    return model
