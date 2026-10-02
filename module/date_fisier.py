"""Date dintr-un fișier text (de ex. Shakespeare).

Ultimele `procent_validare` din fișier sunt păstrate pentru examen și
nu sunt folosite niciodată la antrenare.
"""

from __future__ import annotations

from pathlib import Path


class DateFisier:
    MANIFEST = {
        "nume": "date_fisier",
        "port": "date",
        "versiune": "0.1.0",
        "versiune_contract": 1,
        "resurse": {},
        "permisiuni": ["citire_fisier"],
    }

    def __init__(self, cale: str, procent_validare: float = 0.1) -> None:
        fisier = Path(cale)
        if not fisier.exists():
            raise ValueError(
                f"Nu găsesc „{cale}”. Pentru Shakespeare rulează întâi: python unelte/descarca_date.py"
            )
        if not 0 < procent_validare < 0.5:
            raise ValueError("procent_validare trebuie să fie între 0 și 0.5")
        text = fisier.read_text(encoding="utf-8")
        if len(text) < 1000:
            raise ValueError(f"„{cale}” e prea scurt ({len(text)} caractere)")
        taietura = int(len(text) * (1 - procent_validare))
        self._antrenare = text[:taietura]
        self._validare = text[taietura:]

    def text_antrenare(self) -> str:
        return self._antrenare

    def text_validare(self) -> str:
        return self._validare
