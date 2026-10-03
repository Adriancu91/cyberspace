"""Memoria ierarhică: biblioteca de sensuri, cu coduri pe niveluri și relații.

Cele trei straturi din desen:
1. Biblioteca — fiecare SENS are un loc fix: parte de vorbire → raft (ex.
   „noun.animal”) → lanțul de categorii (organism → animal → mamifer → cal).
   Locul se scrie ca un cod pe niveluri, ex. 1.7.1.2.3.38.5.4...
2. Relațiile — legături între sensuri din rafturi diferite (parte-din,
   membru-din, opus, domeniu...).
3. Plasa — ține minte drumurile deja găsite și de câte ori a fost folosit
   fiecare, ca o căutare repetată să meargă direct la țintă.

Ce primește modelul: pentru fiecare literă din text, codul ULTIMULUI CUVÂNT
TERMINAT înaintea ei. Niciodată cuvântul în curs de scriere: asta i-ar
dezvălui modelului literele care urmează (ar fi trișat la examen).

Biblioteca se construiește o singură dată: python unelte/construieste_biblioteca.py
"""

from __future__ import annotations

import gzip
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

FARA_CUVANT = 0  # încă niciun cuvânt terminat
NECUNOSCUT = 1  # cuvânt care nu e în bibliotecă
PRIMUL_COD = 2  # de aici încep codurile reale (cod real = valoare + PRIMUL_COD)

LITERA = re.compile(r"[A-Za-z]")

# Reguli simple pentru a găsi forma de bază (ca „morphy” din WordNet),
# plus câteva terminații vechi din Shakespeare („loveth”, „know'st”).
TERMINATII = [
    ("'s", ""), ("s'", "s"), ("ies", "y"), ("es", ""), ("s", ""), ("ied", "y"), ("ed", "e"), ("ed", ""),
    ("ing", "e"), ("ing", ""), ("est", ""), ("est", "e"), ("er", ""), ("er", "e"),
    ("eth", ""), ("eth", "e"), ("'st", ""), ("st", ""), ("'d", ""), ("'d", "e"),
]


class MemorieIerarhica:
    MANIFEST = {
        "nume": "memorie_ierarhica",
        "port": "memorie",
        "versiune": "0.1.0",
        "versiune_contract": 1,
        "resurse": {"ram_mb": 600},
        "permisiuni": ["citire_fisier"],
    }

    def __init__(self, cale: str = "date/biblioteca.json.gz", nivele: int = 12) -> None:
        fisier = Path(cale)
        if not fisier.exists():
            raise ValueError(
                f"Nu găsesc biblioteca „{cale}”. Construiește-o întâi: python unelte/construieste_biblioteca.py"
            )
        if not 1 <= nivele <= 30:
            raise ValueError("nivele trebuie să fie între 1 și 30")
        with gzip.open(fisier, "rt", encoding="utf-8") as f:
            biblioteca = json.load(f)
        self.nivele = nivele
        self._noduri: list[dict[str, Any]] = biblioteca["noduri"]
        self._forme: dict[str, list[int]] = biblioteca["forme"]
        self._relatii: dict[str, list[list[Any]]] = biblioteca["relatii"]
        self._rafturi: list[str] = biblioteca["rafturi"]
        self.sursa: str = biblioteca["sursa"]
        # Plasa (stratul 3): drumuri deja găsite + de câte ori a fost folosit fiecare.
        self._plasa: dict[str, tuple[int, ...]] = {}
        self._folosiri: Counter = Counter()
        self._cautari = 0
        self._gasite = 0

    # --- căutarea unui cuvânt ----------------------------------------------

    def _sensuri(self, cuvant: str) -> list[int]:
        cuv = cuvant.lower().strip("'")
        if cuv in self._forme:
            return self._forme[cuv]
        for terminatie, inlocuire in TERMINATII:
            if cuv.endswith(terminatie) and len(cuv) > len(terminatie) + 1:
                baza = cuv[: len(cuv) - len(terminatie)] + inlocuire
                if baza in self._forme:
                    return self._forme[baza]
                # consoană dublată: „running” → „runn” → „run”
                if not inlocuire and len(baza) > 2 and baza[-1] == baza[-2] and baza[-1] not in "aeiouls":
                    if baza[:-1] in self._forme:
                        return self._forme[baza[:-1]]
        return []

    def _cod_nod(self, nod: int) -> tuple[int, ...]:
        return tuple(self._noduri[nod]["cod"])

    def cod(self, cuvant: str) -> tuple[int, ...]:
        """Codul sensului principal (primul sens), cu `nivele` niveluri, completat cu zero."""
        cheie = cuvant.lower()
        self._cautari += 1
        self._folosiri[cheie] += 1
        if cheie in self._plasa:  # scurtătură: drumul e deja știut
            drum = self._plasa[cheie]
        else:
            sensuri = self._sensuri(cheie)
            if sensuri:
                cod = self._cod_nod(sensuri[0])
                drum = tuple(PRIMUL_COD + x for x in cod[: self.nivele])
            else:
                drum = (NECUNOSCUT,)
            self._plasa[cheie] = drum
        if drum[0] != NECUNOSCUT:
            self._gasite += 1
        return drum + (FARA_CUVANT,) * (self.nivele - len(drum))

    # --- contractul -------------------------------------------------------------

    def caracteristici(self, text: str) -> list[tuple[int, ...]]:
        """Pentru fiecare literă: codul ultimului cuvânt TERMINAT până la ea, inclusiv."""
        gol = (FARA_CUVANT,) * self.nivele
        rezultat: list[tuple[int, ...]] = []
        curent = gol
        inceput_cuvant = -1
        for i, c in enumerate(text):
            if LITERA.match(c) or (c == "'" and inceput_cuvant >= 0 and i + 1 < len(text) and LITERA.match(text[i + 1])):
                if inceput_cuvant < 0:
                    inceput_cuvant = i
            elif inceput_cuvant >= 0:
                # Litera `c` nu e literă: cuvântul tocmai s-a terminat, deci acum îl putem folosi.
                curent = self.cod(text[inceput_cuvant:i])
                inceput_cuvant = -1
            rezultat.append(curent)
        return rezultat

    def cauta(self, cuvant: str) -> list[dict[str, Any]]:
        """Toate sensurile unui cuvânt, cu codul, raftul, drumul și relațiile (pentru oameni)."""
        rezultat = []
        for nod in self._sensuri(cuvant):
            drum, j = [], nod
            while j != -1:
                drum.append(self._noduri[j]["n"])
                j = self._noduri[j]["p"]
            relatii = [
                {"tip": tip, "catre": self._noduri[tinta]["n"]}
                for tip, tinta in self._relatii.get(str(nod), [])
            ]
            info = self._noduri[nod]
            rezultat.append({
                "cod": ".".join(map(str, info["cod"])),
                "raft": self._rafturi[info["raft"] - 1],
                "drum": list(reversed(drum)),
                "relatii": relatii,
            })
        return rezultat

    def statistici(self) -> dict[str, Any]:
        frecvente = self._folosiri.most_common(5)
        return {
            "cautari": self._cautari,
            "acoperire": round(self._gasite / self._cautari, 4) if self._cautari else 0.0,
            "drumuri_in_plasa": len(self._plasa),
            "cele_mai_folosite": [c for c, _ in frecvente],
        }
