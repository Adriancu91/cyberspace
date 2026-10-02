"""Module „de jucărie” pentru porturile pe care le folosim mai târziu.

Respectă contractul, deci platforma merge cap-coadă de acum,
dar nu fac încă nimic util. Le înlocuim pe rând:
- ProfesorGol  -> profesor Qwen prin Ollama (Faza 5)
- TraducereIdentitate -> opus-mt-en-ro (Etapa N6)
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
