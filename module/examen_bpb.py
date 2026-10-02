"""Examenul de bază: val_bpb (biți pe octet pe textul de validare).

val_bpb = câți biți îi trebuie modelului, în medie, pentru fiecare octet
de text pe care NU l-a văzut la antrenare. Mai mic = mai bine.
Nu depinde de felul în care modelul împarte textul, deci e corect
să comparăm modele foarte diferite între ele.

ATENȚIE: Paznicul memorează amprenta acestui fișier. Orice schimbare
oprește experimentele până când omul o aprobă (python -m kronos aproba-examen).
"""

from __future__ import annotations

import math
from typing import Any


class ExamenBpb:
    MANIFEST = {
        "nume": "examen_bpb",
        "port": "examen",
        "versiune": "0.1.0",
        "versiune_contract": 1,
        "resurse": {},
        "permisiuni": [],
    }

    scor_principal = "val_bpb"
    mai_mic_e_mai_bun = True

    def __init__(self, max_caractere: int = 100_000) -> None:
        if max_caractere < 100:
            raise ValueError("max_caractere trebuie să fie cel puțin 100")
        self.max_caractere = max_caractere

    def examineaza(self, model: Any, date: Any) -> dict[str, float]:
        text = date.text_validare()[: self.max_caractere]
        biti = float(model.biti_pentru(text))
        octeti = len(text.encode("utf-8"))
        val_bpb = biti / octeti if octeti and math.isfinite(biti) else float("inf")

        continuare = model.genereaza(text[:20], 50)
        generare_ok = 1.0 if isinstance(continuare, str) and len(continuare) == 50 else 0.0
        return {"val_bpb": val_bpb, "generare_ok": generare_ok, "caractere_examinate": float(len(text))}
