"""Jurnalul: fișa completă a fiecărui experiment, într-un fișier care doar crește.

Fiecare linie din experimente.jsonl e un experiment. Nimic nu se șterge,
inclusiv eșecurile, ca orice rezultat să poată fi verificat și reprodus.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


class Jurnal:
    def __init__(self, director_lucru: Path) -> None:
        self.director = Path(director_lucru) / "jurnal"
        self.director.mkdir(parents=True, exist_ok=True)
        self.fisier = self.director / "experimente.jsonl"

    def adauga(self, fisa: dict[str, Any]) -> None:
        with self.fisier.open("a", encoding="utf-8") as f:
            f.write(json.dumps(fisa, ensure_ascii=False, default=str) + "\n")

    def istoric(self, linie: str | None = None) -> list[dict[str, Any]]:
        """Toate experimentele, opțional doar cele dintr-o anumită configurare."""
        if not self.fisier.exists():
            return []
        fise = []
        with self.fisier.open(encoding="utf-8") as f:
            for rand in f:
                rand = rand.strip()
                if not rand:
                    continue
                try:
                    fisa = json.loads(rand)
                except json.JSONDecodeError:
                    continue  # un rând stricat (ex. oprire bruscă) nu blochează restul
                if linie is None or fisa.get("linie") == linie:
                    fise.append(fisa)
        return fise

    def cel_mai_bun(self, linie: str, scor: str, mai_mic_e_mai_bun: bool) -> dict[str, Any] | None:
        """Cel mai bun experiment PĂSTRAT dintr-o configurare."""
        pastrate = [
            f
            for f in self.istoric(linie)
            if f.get("decizie") == "pastrat"
            and isinstance(f.get("scoruri", {}).get(scor), (int, float))
            and math.isfinite(f["scoruri"][scor])
        ]
        if not pastrate:
            return None
        cheie = lambda f: f["scoruri"][scor]  # noqa: E731
        return min(pastrate, key=cheie) if mai_mic_e_mai_bun else max(pastrate, key=cheie)

    def urmatorul_id(self) -> int:
        return len(self.istoric()) + 1
