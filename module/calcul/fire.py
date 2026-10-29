"""S48: numărul de fire al înmulțirilor (OpenBLAS din numpy), schimbat în procesul de acum.

Bancul S47 alege firele din mediu, într-un proces nou; modulul `inferenta_ccm` nu poate porni alt proces, așa că le
schimbă direct în biblioteca OpenBLAS adusă de numpy (`numpy.libs/*openblas*.dll`), prin ctypes, fără nimic instalat.
Schimbarea e pe tot procesul: `cu_fire` le pune doar pe durata unui calcul și apoi le pune înapoi.
Dacă biblioteca nu se găsește (alt numpy, alt sistem), `disponibil()` e fals și nimic nu se schimbă.
"""

from __future__ import annotations

import ctypes
import glob
import os
from contextlib import contextmanager
from typing import Iterator

import numpy as np

_PERECHI = (("scipy_openblas_get_num_threads64_", "scipy_openblas_set_num_threads64_"),
            ("openblas_get_num_threads64_", "openblas_set_num_threads64_"),
            ("openblas_get_num_threads", "openblas_set_num_threads"))
_functii: tuple | None = None
_cautat = False


def _incarca() -> tuple | None:
    global _functii, _cautat
    if _cautat:
        return _functii
    _cautat = True
    baza = os.path.dirname(np.__file__)
    for dll in sorted(glob.glob(os.path.join(baza + ".libs", "*openblas*")) + glob.glob(os.path.join(baza, ".libs", "*openblas*"))):
        try:
            lib = ctypes.CDLL(dll)
        except OSError:
            continue
        for citeste, pune in _PERECHI:
            if hasattr(lib, citeste) and hasattr(lib, pune):
                _functii = (getattr(lib, citeste), getattr(lib, pune))
                return _functii
    return None


def disponibil() -> bool:
    return _incarca() is not None


def citeste() -> int | None:
    f = _incarca()
    return None if f is None else int(f[0]())


def din_text(fire: str) -> int | None:
    """„toate” → None (nu se schimbă nimic); „1”, „4” … → numărul. Altceva → ValueError."""
    if fire == "toate":
        return None
    if not fire.isdigit() or int(fire) < 1:
        raise ValueError(f"fire necunoscute: {fire!r}")
    return int(fire)


@contextmanager
def cu_fire(n: int | None) -> Iterator[None]:
    """Pe durata blocului, `n` fire (None = cum sunt). La ieșire, înapoi cum erau."""
    f = _incarca() if n is not None else None
    if f is None:
        if n is not None:
            raise RuntimeError("firele OpenBLAS nu se pot schimba în procesul acesta")
        yield
        return
    vechi = int(f[0]())
    f[1](int(n))
    try:
        yield
    finally:
        f[1](vechi)
