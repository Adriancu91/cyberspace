"""Variantele CCM: nume → fabrică (cale KGR1 → motor cu `logits`, `completeaza_simboluri`, `tok`, `context`).

Câte un fișier pe operație; deocamdată doar înmulțirea (S47). Firele (OpenBLAS) nu sunt variante de cod: bancul le
schimbă din mediu, într-un proces separat.
"""

from __future__ import annotations

from typing import Any, Callable

from module.calcul.variante import inmultire

VARIANTE: dict[str, Callable[[Any], Any]] = dict(inmultire.VARIANTE)
REFERINTA = "referinta"
