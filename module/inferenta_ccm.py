"""Portul „inferenta” prin CCM (S48): aceeași inferență ca `inferenta_kgr1`, dar cu varianta și firele alese de bancul
CCM pe calculatorul acesta (`lucru/ccm/reglaj-<calculator>.json`, scris de `module.calcul.reglaj`).

Rezerva: fără reglaj sau la orice nepotrivire (alt calculator, alt model, variantă necunoscută sau neacceptată, eroare la
încărcarea variantei) → exact calea `inferenta_kgr1` (MotorBrut, desfacere la încărcare, firele cum sunt).
Ce s-a ales și de ce se vede în `statistici()["ccm"]`. Firele se pun doar pe durata fiecărui calcul, apoi înapoi.

S49: cu `placa=True`, dacă reglajul are o variantă pe placa video acceptată și mai rapidă după măsurători, se folosește
aceea (PyTorch, CUDA); altfel varianta de procesor, cu motivele la `motive_placa`. Implicit placa NU se folosește:
o antrenare pe placă n-ar mai fi singura (o singură sarcină grea pe placă o dată).
"""

from __future__ import annotations

from typing import Any

from module.calcul import fire, reglaj
from module.calcul.variante import TOATE
from module.inferenta_kgr1 import InferentaKGR1
from unelte.inferenta_bruta import MotorBrut


class InferentaCCM(InferentaKGR1):
    MANIFEST = {
        "nume": "inferenta_ccm",
        "port": "inferenta",
        "versiune": "0.2.0",
        "versiune_contract": 1,
        "resurse": {"gpu": False},  # placa doar cu placa=True (S49)
        "permisiuni": [],
    }

    def __init__(self, cale: str = "lucru/export/kronos_459_q8_0.kgr", cale_reglaj: str = "",
                 placa: bool = False) -> None:
        self.cale = cale
        self.ccm = reglaj.alege(cale_reglaj or reglaj.cale_implicita(), cale, placa)
        self._fire: int | None = None
        if self.ccm["folosit"]:
            try:
                self.motor = TOATE[self.ccm["varianta"]](cale)
                self._fire = fire.din_text(self.ccm["fire"])
                return
            except Exception as e:  # orice problemă a variantei → rezerva, cu motivul
                self.ccm.update(folosit=False, dispozitiv="procesor", motive=[f"varianta nu s-a încărcat: {e!r}"])
        self.motor = MotorBrut(cale, "la_incarcare")

    def logits(self, simboluri: list[int]) -> list[float]:
        with fire.cu_fire(self._fire):
            return super().logits(simboluri)

    def genereaza(self, simboluri: list[int], cate: int) -> list[int]:
        with fire.cu_fire(self._fire):
            return super().genereaza(simboluri, cate)

    def statistici(self) -> dict[str, Any]:
        return {**super().statistici(), "ccm": dict(self.ccm)}
