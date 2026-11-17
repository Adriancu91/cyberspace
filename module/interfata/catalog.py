"""Catalogul: istoricul conversațiilor din interfață, într-o bază SQLite (un singur fișier .db).

Nu e jurnalul Kronos (acela rămâne JSONL, în lucru/jurnal/, și interfața nu-l atinge). Aici stau doar conversațiile:
fiecare conversație are mesaje, iar fiecare mesaj spune cine l-a scris (omul sau un creier, cu eticheta lui).

S118 (C-126 B, 17 noiembrie 2026): la fiecare răspuns al unui creier, omul poate pune 👍 (nota 1) sau 👎 (nota -1) și poate
scrie „răspunsul corect ar fi…” (tabelul `aprecieri`). Întrebările din fila „Întreabă din text” se păstrează și ele
(`intrebari_text`, cu paragraful și răspunsul), cu aprecierile lor (`aprecieri_text`). Totul rămâne local, în lucru/
(în afara Git); din ele, unelte/lectii_din_conversatii.py strânge lecțiile.
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
CREATE TABLE IF NOT EXISTS aprecieri (
    mesaj      INTEGER PRIMARY KEY REFERENCES mesaje(id),
    nota       INTEGER,
    corectura  TEXT,
    creata     TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS intrebari_text (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    paragraf   TEXT NOT NULL,
    intrebare  TEXT NOT NULL,
    raspuns    TEXT NOT NULL,
    autor      TEXT NOT NULL,
    creat      TEXT NOT NULL,
    secunde    REAL
);
CREATE TABLE IF NOT EXISTS aprecieri_text (
    intrebare  INTEGER PRIMARY KEY REFERENCES intrebari_text(id),
    nota       INTEGER,
    corectura  TEXT,
    creata     TEXT NOT NULL
);
"""
NOTE = (1, -1, None)        # 👍, 👎, fără notă
LUNGIME_MAXIMA_CORECTURA = 2000
SELECT_MESAJ = ("SELECT m.*, a.nota AS nota, a.corectura AS corectura FROM mesaje m "
                "LEFT JOIN aprecieri a ON a.mesaj = m.id")
SELECT_TEXT = ("SELECT t.*, a.nota AS nota, a.corectura AS corectura FROM intrebari_text t "
               "LEFT JOIN aprecieri_text a ON a.intrebare = t.id")


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
            return dict(baza.execute(SELECT_MESAJ + " WHERE m.id = ?", (numar,)).fetchone())

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
            randuri = baza.execute(SELECT_MESAJ + " WHERE m.conversatie = ? ORDER BY m.id", (conversatie,)).fetchall()
        return [dict(r) for r in randuri]

    # --- S118: aprecierile omului și întrebările „din text” -----------------------------------------------------

    @staticmethod
    def _verifica_aprecierea(nota: Any, corectura: Any) -> tuple[int | None, str | None]:
        if isinstance(nota, bool) or nota not in NOTE:
            raise ValueError("nota e 1 (👍), -1 (👎) sau nimic")
        if corectura is not None and not isinstance(corectura, str):
            raise ValueError("corectura e un text")
        corectura = (corectura or "").strip() or None
        if corectura is not None and len(corectura) > LUNGIME_MAXIMA_CORECTURA:
            raise ValueError(f"corectura are cel mult {LUNGIME_MAXIMA_CORECTURA} caractere")
        return nota, corectura

    def apreciaza(self, mesaj: int, nota: int | None, corectura: str | None = None) -> dict[str, Any]:
        """Pune (sau schimbă) nota și corectura la un răspuns al creierului; întoarce mesajul cu ele."""
        nota, corectura = self._verifica_aprecierea(nota, corectura)
        with self._zavor, closing(self._legatura()) as baza, baza:
            rand = baza.execute("SELECT rol FROM mesaje WHERE id = ?", (mesaj,)).fetchone()
            if rand is None:
                raise KeyError(f"Mesajul #{mesaj} nu există.")
            if rand["rol"] != ROL_CREIER:
                raise ValueError("doar răspunsurile lui Kronos se notează")
            baza.execute("INSERT INTO aprecieri (mesaj, nota, corectura, creata) VALUES (?, ?, ?, ?) "
                         "ON CONFLICT(mesaj) DO UPDATE SET nota = excluded.nota, corectura = excluded.corectura, "
                         "creata = excluded.creata", (mesaj, nota, corectura, _acum()))
            return dict(baza.execute(SELECT_MESAJ + " WHERE m.id = ?", (mesaj,)).fetchone())

    def adauga_intrebare_text(self, paragraf: str, intrebare: str, raspuns: str, autor: str,
                              secunde: float | None = None) -> dict[str, Any]:
        """Păstrează o întrebare din fila „Întreabă din text”, cu paragraful și răspunsul."""
        with self._zavor, closing(self._legatura()) as baza, baza:
            numar = baza.execute(
                "INSERT INTO intrebari_text (paragraf, intrebare, raspuns, autor, creat, secunde) VALUES (?, ?, ?, ?, ?, ?)",
                (paragraf, intrebare, raspuns, autor, _acum(), secunde)).lastrowid
            return dict(baza.execute(SELECT_TEXT + " WHERE t.id = ?", (numar,)).fetchone())

    def apreciaza_text(self, intrebare: int, nota: int | None, corectura: str | None = None) -> dict[str, Any]:
        """Ca `apreciaza`, pentru un răspuns din fila „Întreabă din text”."""
        nota, corectura = self._verifica_aprecierea(nota, corectura)
        with self._zavor, closing(self._legatura()) as baza, baza:
            if baza.execute("SELECT 1 FROM intrebari_text WHERE id = ?", (intrebare,)).fetchone() is None:
                raise KeyError(f"Întrebarea #{intrebare} nu există.")
            baza.execute("INSERT INTO aprecieri_text (intrebare, nota, corectura, creata) VALUES (?, ?, ?, ?) "
                         "ON CONFLICT(intrebare) DO UPDATE SET nota = excluded.nota, corectura = excluded.corectura, "
                         "creata = excluded.creata", (intrebare, nota, corectura, _acum()))
            return dict(baza.execute(SELECT_TEXT + " WHERE t.id = ?", (intrebare,)).fetchone())

    def apreciate(self) -> list[dict[str, Any]]:
        """Toate răspunsurile notate sau corectate, pentru lecții: fila („chat” / „text”), întrebarea omului (la chat,
        mesajul omului de dinaintea răspunsului), paragraful (doar la „text”), răspunsul modelului, cine l-a dat, nota
        și corectura."""
        with closing(self._legatura()) as baza:
            chat = baza.execute(
                "SELECT 'chat' AS fila, r.id AS id, "
                "(SELECT o.text FROM mesaje o WHERE o.conversatie = r.conversatie AND o.id < r.id AND o.rol = ? "
                " ORDER BY o.id DESC LIMIT 1) AS intrebare, '' AS paragraf, r.text AS raspuns, r.autor AS autor, "
                "a.nota AS nota, a.corectura AS corectura, a.creata AS creata "
                "FROM aprecieri a JOIN mesaje r ON r.id = a.mesaj ORDER BY r.id", (ROL_OM,)).fetchall()
            text = baza.execute(
                "SELECT 'text' AS fila, t.id AS id, t.intrebare AS intrebare, t.paragraf AS paragraf, "
                "t.raspuns AS raspuns, t.autor AS autor, a.nota AS nota, a.corectura AS corectura, a.creata AS creata "
                "FROM aprecieri_text a JOIN intrebari_text t ON t.id = a.intrebare ORDER BY t.id").fetchall()
        return [dict(r) for r in chat if r["intrebare"] is not None] + [dict(r) for r in text]
