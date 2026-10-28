"""Portul „inferenta”: un model din fișierul KGR1, citit fără PyTorch (S40).

Învelește `MotorBrut` din `unelte/inferenta_bruta.py` (import, nu copie). Doar citire: nu antrenează nimic.
"""

from __future__ import annotations

from typing import Any

from unelte.inferenta_bruta import MotorBrut


class InferentaKGR1:
    MANIFEST = {
        "nume": "inferenta_kgr1",
        "port": "inferenta",
        "versiune": "0.1.0",
        "versiune_contract": 1,
        "resurse": {"gpu": False},
        "permisiuni": [],
    }

    def __init__(self, cale: str = "lucru/export/kronos_459_q8_0.kgr", desfacere: str = "la_incarcare") -> None:
        self.cale = cale
        self.motor = MotorBrut(cale, desfacere)

    def logits(self, simboluri: list[int]) -> list[float]:
        """Peste context, contează doar ultimele `context` simboluri (ca la completare)."""
        if not simboluri:
            raise ValueError("trebuie cel puțin un simbol")
        return self.motor.logits(list(simboluri)[-self.motor.context:])[-1].tolist()

    def genereaza(self, simboluri: list[int], cate: int) -> list[int]:
        if cate <= 0:
            return []
        if not simboluri:
            raise ValueError("trebuie cel puțin un simbol")
        noi, _ = self.motor.completeaza_simboluri(list(simboluri), cate)
        return noi

    def statistici(self) -> dict[str, Any]:
        m = self.motor
        return {
            "vocabular": m.vocabular,
            "context": m.context,
            "format": str(m.chei.get("fel", "")).upper(),
            "n_straturi": m.n_straturi,
            "n_capete": m.n_capete,
            "n_emb": m.n_emb,
            "octeti_greutati": m.octeti_greutati(),
            "desfacere": m.desfacere,
            "sursa": m.chei.get("sursa", ""),
        }
