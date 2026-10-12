"""Date din două fișiere text gata făcute: unul de antrenare și unul de validare (pentru amestecul workstation-ului).

Antrenarea e un amestec din mai multe surse (engleză simplă, română, cod, numere), construit o singură dată de
unelte/pregateste_amestec_ws.py. Validarea e un fișier separat, de obicei validarea TinyStories R2: examenul oficial
(val_bpb, în biți pe octet) rămâne pe același text ca până acum, deci linia nouă se compară direct cu cele vechi.
"""

from __future__ import annotations

from pathlib import Path


class DateAmestec:
    MANIFEST = {
        "nume": "date_amestec",
        "port": "date",
        "versiune": "0.1.0",
        "versiune_contract": 1,
        "resurse": {},
        "permisiuni": ["citire_fisier"],
    }

    def __init__(self, cale_antrenare: str, cale_validare: str) -> None:
        for cale in (cale_antrenare, cale_validare):
            if not Path(cale).exists():
                raise ValueError(f"Nu găsesc „{cale}”. Pentru amestecul workstation-ului rulează întâi: "
                                 f"python unelte/pregateste_amestec_ws.py")
        self._antrenare = Path(cale_antrenare).read_text(encoding="utf-8")
        self._validare = Path(cale_validare).read_text(encoding="utf-8")
        if len(self._antrenare) < 1000 or len(self._validare) < 100:
            raise ValueError("textul de antrenare sau cel de validare e prea scurt")

    def text_antrenare(self) -> str:
        return self._antrenare

    def text_validare(self) -> str:
        return self._validare
