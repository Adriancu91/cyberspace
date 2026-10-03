"""Module „de jucărie” pentru porturile pe care le folosim mai târziu.

Respectă contractul, deci platforma merge cap-coadă de acum,
dar nu fac încă nimic util. Le înlocuim pe rând:
- ProfesorGol  -> profesor Qwen prin Ollama (Faza 5)
- TraducereIdentitate -> opus-mt-en-ro (Etapa N6)
- MemorieGoala -> pentru configurațiile fără memorie ierarhică
"""

from __future__ import annotations


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
    """Memorie care nu știe nimic: pentru configurațiile care nu folosesc memoria."""

    MANIFEST = {
        "nume": "memorie_goala",
        "port": "memorie",
        "versiune": "0.1.0",
        "versiune_contract": 1,
        "resurse": {},
        "permisiuni": [],
    }

    nivele = 1

    def caracteristici(self, text: str) -> list[tuple[int, ...]]:
        return [(0,)] * len(text)

    def cauta(self, cuvant: str) -> list[dict]:
        return []

    def statistici(self) -> dict:
        return {"cautari": 0, "acoperire": 0.0}
