"""Date de probă, generate pe loc (nu cer internet).

Propoziții simple în engleză, făcute după câteva tipare. Au destulă
structură ca un model să învețe ceva și sunt mereu aceleași (sămânță fixă),
deci rezultatele se pot compara între rulări.
"""

from __future__ import annotations

import random

SUBIECTE = ["the cat", "the dog", "a small bird", "the old man", "a happy child", "the red fox", "my friend"]
VERBE = ["sat on", "looked at", "ran to", "jumped over", "walked past", "slept near", "played with"]
OBIECTE = ["the mat", "the tree", "a big box", "the river", "the green hill", "a warm house", "the garden"]
FINALURI = [".", ".", ".", " today.", " again.", " in the morning.", " at night."]


class DateMostra:
    MANIFEST = {
        "nume": "date_mostra",
        "port": "date",
        "versiune": "0.1.0",
        "versiune_contract": 1,
        "resurse": {},
        "permisiuni": [],
    }

    def __init__(self, propozitii: int = 4000, procent_validare: float = 0.1, samanta: int = 7) -> None:
        if propozitii < 20:
            raise ValueError("propozitii trebuie să fie cel puțin 20")
        if not 0 < procent_validare < 0.5:
            raise ValueError("procent_validare trebuie să fie între 0 și 0.5")
        rng = random.Random(samanta)
        randuri = [
            f"{rng.choice(SUBIECTE)} {rng.choice(VERBE)} {rng.choice(OBIECTE)}{rng.choice(FINALURI)}"
            for _ in range(propozitii)
        ]
        taietura = int(len(randuri) * (1 - procent_validare))
        self._antrenare = "\n".join(randuri[:taietura]) + "\n"
        self._validare = "\n".join(randuri[taietura:]) + "\n"

    def text_antrenare(self) -> str:
        return self._antrenare

    def text_validare(self) -> str:
        return self._validare
