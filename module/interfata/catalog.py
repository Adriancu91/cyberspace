"""Catalogul: istoricul conversațiilor din interfață, într-o bază SQLite (un singur fișier .db).

Nu e jurnalul Kronos (acela rămâne JSONL, în lucru/jurnal/, și interfața nu-l atinge). Aici stau doar conversațiile:
fiecare conversație are mesaje, iar fiecare mesaj spune cine l-a scris (omul sau un creier, cu eticheta lui).
"""

from __future__ import annotations

import sqlite3
import threading
from contextlib import closing
from datetime import datetime
from pathlib import Path
from typing import Any

ROL_OM = "om"
ROL_CREIER = "creier"
LUNGIME_TITLU = 60

SCHEMA = """
CREATE TABLE IF NOT EXISTS conversatii (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    titlu   TEXT NOT NULL,
    creata  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS mesaje (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    conversatie INTEGER NOT NULL REFERENCES conversatii(id),
    rol         TEXT NOT NULL,
    autor       TEXT NOT NULL,
    text        TEXT NOT NULL,
    creat       TEXT NOT NULL,
    secunde     REAL
);
CREATE INDEX IF NOT EXISTS mesaje_pe_conversatie ON mesaje(conversatie, id);
"""


def _acum() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


class Catalog:
    """Conversațiile și mesajele lor. Fiecare operație își deschide legătura ei la bază, iar scrierile trec pe rând
    printr-un zăvor, ca serverul să poată răspunde la mai multe cereri deodată."""

    def __init__(self, cale: str | Path) -> None:
        self.cale = Path(cale)
        self.cale.parent.mkdir(parents=True, exist_ok=True)
        self._zavor = threading.Lock()
        with self._zavor, closing(self._legatura()) as baza, baza:
            baza.executescript(SCHEMA)

    def _legatura(self) -> sqlite3.Connection:
        baza = sqlite3.connect(self.cale, timeout=10)
        baza.row_factory = sqlite3.Row
        baza.execute("PRAGMA foreign_keys = ON")
        return baza

    def conversatie_noua(self, titlu: str = "") -> int:
        """Deschide o conversație și întoarce numărul ei."""
        titlu = " ".join(titlu.split())[:LUNGIME_TITLU] or "Conversație nouă"
        with self._zavor, closing(self._legatura()) as baza, baza:
            return int(baza.execute("INSERT INTO conversatii (titlu, creata) VALUES (?, ?)", (titlu, _acum())).lastrowid)

    def exista(self, conversatie: int) -> bool:
        with closing(self._legatura()) as baza:
            return baza.execute("SELECT 1 FROM conversatii WHERE id = ?", (conversatie,)).fetchone() is not None

    def adauga_mesaj(self, conversatie: int, rol: str, autor: str, text: str,
                     secunde: float | None = None) -> dict[str, Any]:
        """Scrie un mesaj în conversație și îl întoarce așa cum a ajuns în bază."""
        if rol not in (ROL_OM, ROL_CREIER):
            raise ValueError(f"rol necunoscut: „{rol}”")
        with self._zavor, closing(self._legatura()) as baza, baza:
            if baza.execute("SELECT 1 FROM conversatii WHERE id = ?", (conversatie,)).fetchone() is None:
                raise KeyError(f"Conversația #{conversatie} nu există.")
            numar = baza.execute(
                "INSERT INTO mesaje (conversatie, rol, autor, text, creat, secunde) VALUES (?, ?, ?, ?, ?, ?)",
                (conversatie, rol, autor, text, _acum(), secunde),
            ).lastrowid
            return dict(baza.execute("SELECT * FROM mesaje WHERE id = ?", (numar,)).fetchone())

    def conversatii(self) -> list[dict[str, Any]]:
        """Toate conversațiile, cea mai nouă prima, cu numărul de mesaje."""
        with closing(self._legatura()) as baza:
            randuri = baza.execute(
                "SELECT c.id, c.titlu, c.creata, COUNT(m.id) AS mesaje FROM conversatii c "
                "LEFT JOIN mesaje m ON m.conversatie = c.id GROUP BY c.id ORDER BY c.id DESC"
            ).fetchall()
        return [dict(r) for r in randuri]

    def mesaje(self, conversatie: int) -> list[dict[str, Any]]:
        """Mesajele unei conversații, în ordinea în care au fost scrise."""
        with closing(self._legatura()) as baza:
            randuri = baza.execute("SELECT * FROM mesaje WHERE conversatie = ? ORDER BY id", (conversatie,)).fetchall()
        return [dict(r) for r in randuri]
