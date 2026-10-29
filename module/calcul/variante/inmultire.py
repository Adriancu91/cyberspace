"""Variantele pentru înmulțirea cu greutățile (S47). Restul calculului e cel din `MotorBrut` (referința).

- referinta:  `MotorBrut`, Q8_0 desfăcut o dată, la încărcare (matricile în ordinea din fișier, folosite transpuse).
- la_pas:     `MotorBrut` cu desfacerea Q8_0 la fiecare înmulțire (memorie ~4× mai puțină).
- transpus:   ca referința, dar matricile ținute în ordinea coloanelor (Fortran), ca `h @ W.T` să citească o matrice
              așezată la rând în memorie; se plătește o dată, la încărcare.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from unelte.inferenta_bruta import MotorBrut


class MotorTranspus(MotorBrut):
    def __init__(self, cale: str | Path) -> None:
        super().__init__(cale, "la_incarcare")
        self.t = {k: (np.asfortranarray(v) if isinstance(v, np.ndarray) and v.ndim == 2 else v)
                  for k, v in self.t.items()}


VARIANTE = {
    "referinta": lambda cale: MotorBrut(cale, "la_incarcare"),
    "la_pas": lambda cale: MotorBrut(cale, "la_pas"),
    "transpus": MotorTranspus,
}
