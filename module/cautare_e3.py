"""Portul „cautare”: căutarea E3 aleasă la S29/S33, ca modul înlocuibil (S40).

Refolosește codul din unelte/ (import, nu copie): căutarea S25 (`unelte/e3_memorie.py`, varianta din
`validare_s25.json`, implicit „nume_obligatorii_liste”) pe indexul obișnuit și pe cel cu rădăcini românești,
listele unite cu RRF și paginile-listă coborâte la urmă (`unelte/e3_reordonare.py:cauta_rrf`).
Fără judecătorul-model (reordonarea „rrf_reord” cere placa): varianta asta merge doar pe procesor.

Bazele SQLite se deschid doar pentru citire.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from unelte import e3_memorie as e3
from unelte import e3_reordonare as r
from unelte.verificator_text import cuvinte

VARIANTA_IMPLICITA = "nume_obligatorii_liste"


def _doar_citire(cale: Path) -> sqlite3.Connection:
    if not cale.is_file():
        raise ValueError(f"nu există baza „{cale}”")
    return sqlite3.connect(f"file:{cale.as_posix()}?mode=ro", uri=True, check_same_thread=False)


class CautareE3:
    MANIFEST = {
        "nume": "cautare_e3",
        "port": "cautare",
        "versiune": "0.1.0",
        "versiune_contract": 1,
        "resurse": {"gpu": False},
        "permisiuni": [],
    }

    def __init__(
        self,
        cale_index: str = "lucru/e3/index.sqlite",
        cale_index_radacini: str = "lucru/e3/index_radacini.sqlite",
        cale_liste: str = "lucru/e3/liste_s25.json",
        varianta: str = VARIANTA_IMPLICITA,
    ) -> None:
        e3.interogare("proba", varianta)  # ValueError la o variantă necunoscută
        self.varianta = varianta
        self.cale_index = Path(cale_index)
        self.cale_index_radacini = Path(cale_index_radacini)
        self.con = _doar_citire(self.cale_index)
        self.con_r = _doar_citire(self.cale_index_radacini)
        if cale_liste:
            info = json.loads(Path(cale_liste).read_text(encoding="utf-8"))
            self.liste = {"fraze_lista": set(info["fraze_lista"]), "randuri_scurte": set(info["randuri_scurte"])}
        else:
            self.liste = {"fraze_lista": set(), "randuri_scurte": set()}

    def cauta(self, intrebare: str, k: int) -> list[dict[str, Any]]:
        """Scorul e cel al locului din lista unită, 1 / (K_RRF + loc): mai mare = mai sus."""
        if k <= 0 or not any(any(x.isalnum() for x in c) for c in cuvinte(e3.curata(intrebare))):
            return []
        _, unite = r.cauta_rrf(self.con, self.con_r, intrebare, self.varianta, self.liste,
                               cate=max(k, e3.CATE_PENTRU_LISTE))
        return [{**g, "scor": 1.0 / (r.K_RRF + loc)} for loc, g in enumerate(unite[:k], 1)]

    def statistici(self) -> dict[str, Any]:
        return {
            "bucati": self.con.execute("SELECT count(*) FROM bucati").fetchone()[0],
            "varianta": self.varianta,
            "rrf_k": r.K_RRF,
            "pagini_lista": len(self.liste["fraze_lista"]),
            "index": str(self.cale_index),
            "index_radacini": str(self.cale_index_radacini),
        }
