"""Module „de jucărie” pentru porturile pe care le folosim mai târziu.

Respectă contractul, deci platforma merge cap-coadă de acum,
dar nu fac încă nimic util. Le înlocuim pe rând:
- ProfesorGol  -> profesor Qwen prin Ollama (Faza 5)
- TraducereIdentitate -> opus-mt-en-ro (Etapa N6)

MemorieGoala rămâne: e memoria configurațiilor care nu folosesc biblioteca de sensuri.
"""

from __future__ import annotations

from typing import Any


class ProfesorGol:
    MANIFEST = {
        "nume": "profesor_gol",
        "port": "profesor",
        "versiune": "0.1.0",
        "versiune_contract": 1,
        "resurse": {},
        "permisiuni": [],
    }

    def genereaza_exercitii(self, tema: str, numar: int) -> list[dict[str, str]]:
        return []


class TraducereIdentitate:
    MANIFEST = {
        "nume": "traducere_identitate",
        "port": "traducere",
        "versiune": "0.1.0",
        "versiune_contract": 1,
        "resurse": {},
        "permisiuni": [],
    }

    def traduce(self, text: str, din_limba: str, in_limba: str) -> str:
        return text


class MemorieGoala:
    """Memorie care nu știe niciun cuvânt: fiecare literă primește codul gol."""

    MANIFEST = {
        "nume": "memorie_goala",
        "port": "memorie",
        "versiune": "0.1.0",
        "versiune_contract": 1,
        "resurse": {},
        "permisiuni": [],
    }

    nivele = 1

    def cod(self, cuvant: str) -> tuple[int, ...]:
        return (0,)

    def caracteristici(self, text: str) -> list[tuple[int, ...]]:
        return [(0,)] * len(text)

    def cauta(self, cuvant: str) -> list[dict[str, Any]]:
        return []

    def statistici(self) -> dict[str, Any]:
        return {"cautari": 0, "acoperire": 0.0}
