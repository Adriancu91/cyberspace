"""Un fișier citit ca și cum anumite porțiuni (de octeți) n-ar fi în el — fără să scrie o copie pe disc (S119, 17 nov
2026: cele 162 de texte cu scurgeri din `date/ws/s119/antrenare.txt` se sar la a doua verificare și la tokenizare,
din aceeași listă). Pozițiile (`seek`, `tell`, `marime`) sunt ale fișierului „fără porțiuni”.
"""

from __future__ import annotations

import bisect
from typing import BinaryIO


class FaraPortiuni:
    def __init__(self, f: BinaryIO, portiuni: list[tuple[int, int]], marime_reala: int) -> None:
        portiuni = sorted((int(a), int(b)) for a, b in portiuni)
        capat = 0
        for a, b in portiuni:
            if not capat <= a < b <= marime_reala:
                raise ValueError(f"porțiune greșită sau suprapusă: {(a, b)}")
            capat = b
        self._f = f
        self._a = [a for a, _ in portiuni]
        self._b = [b for _, b in portiuni]
        # Începutul fiecărei porțiuni în pozițiile „fără porțiuni” și cât s-a sărit înaintea ei.
        self._inainte: list[int] = []
        self._v: list[int] = []
        sarit = 0
        for a, b in portiuni:
            self._inainte.append(sarit)
            self._v.append(a - sarit)
            sarit += b - a
        self.sarit = sarit
        self.marime_reala = marime_reala
        self.marime = marime_reala - sarit
        self._poz = 0

    def seek(self, poz: int, de_unde: int = 0) -> int:
        if de_unde != 0:
            raise ValueError("doar seek de la început")
        self._poz = max(0, min(int(poz), self.marime))
        return self._poz

    def tell(self) -> int:
        return self._poz

    def read(self, n: int = -1) -> bytes:
        if n is None or n < 0:
            n = self.marime - self._poz
        parti: list[bytes] = []
        while n > 0 and self._poz < self.marime:
            k = bisect.bisect_right(self._v, self._poz)  # porțiunile care încep la sau înainte de poziție: sărite
            real = self._poz + (self._inainte[k - 1] + self._b[k - 1] - self._a[k - 1] if k else 0)
            pana = self._a[k] if k < len(self._a) else self.marime_reala
            cat = min(n, pana - real)
            self._f.seek(real)
            bucata = self._f.read(cat)
            if not bucata:
                break
            parti.append(bucata)
            self._poz += len(bucata)
            n -= len(bucata)
        return b"".join(parti)
