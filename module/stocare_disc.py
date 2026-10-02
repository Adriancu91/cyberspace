"""Stocare pe discul local, într-un folder al proiectului."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class StocareDisc:
    MANIFEST = {
        "nume": "stocare_disc",
        "port": "stocare",
        "versiune": "0.1.0",
        "versiune_contract": 1,
        "resurse": {},
        "permisiuni": ["scriere_fisier"],
    }

    def __init__(self, director: str = "lucru/stocare") -> None:
        self.director = Path(director).resolve()
        self.director.mkdir(parents=True, exist_ok=True)

    def cale_pentru(self, nume: str) -> str:
        cale = (self.director / nume).resolve()
        if self.director not in cale.parents and cale != self.director:
            raise ValueError(f"„{nume}” ar ieși din folderul de stocare")
        cale.parent.mkdir(parents=True, exist_ok=True)
        return str(cale)

    def salveaza_json(self, nume: str, obiect: Any) -> str:
        cale = Path(self.cale_pentru(nume)).with_suffix(".json")
        cale.write_text(json.dumps(obiect, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        return str(cale)

    def incarca_json(self, nume: str) -> Any | None:
        cale = Path(self.cale_pentru(nume)).with_suffix(".json")
        if not cale.exists():
            return None
        return json.loads(cale.read_text(encoding="utf-8"))
