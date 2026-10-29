"""Variantele CCM: nume → fabrică (cale KGR1 → motor cu `logits`, `completeaza_simboluri`, `tok`, `context`).

Câte un fișier pe operație; deocamdată doar înmulțirea (S47). Firele (OpenBLAS) nu sunt variante de cod: bancul le
schimbă din mediu, într-un proces separat. S49: variantele pe placa video (`placa.py`) stau separat, în `VARIANTE_PLACA`
(cer CUDA); `TOATE` = procesor + placă.
"""

from __future__ import annotations

from typing import Any, Callable

from module.calcul.variante import inmultire, placa

VARIANTE: dict[str, Callable[[Any], Any]] = dict(inmultire.VARIANTE)
VARIANTE_PLACA: dict[str, Callable[[Any], Any]] = dict(placa.VARIANTE)
TOATE: dict[str, Callable[[Any], Any]] = {**VARIANTE, **VARIANTE_PLACA}
REFERINTA = "referinta"
