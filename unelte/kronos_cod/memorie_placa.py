"""Memoria plăcii pentru uneltele de examen de cod (S62): citire + oprire singură peste o limită.

La S58, `examen_cod.py model` a ținut placa la 7.188–7.971 MB ~17 minute și nimic n-a putut-o opri. De aceea uneltele
de examen citesc memoria după fiecare lot și se opresc singure (cod de ieșire ≠ 0) peste `--memorie-max`.

Cifra e cât ar arăta `nvidia-smi` la vârf: memoria folosită acum pe toată placa (`torch.cuda.mem_get_info`, include
contextul CUDA și alte procese), din care scădem ce ține acum PyTorch rezervat și adunăm vârful rezervat de la pornire
(`torch.cuda.max_memory_reserved`). Pe procesor nu e nimic de citit (None).
"""

from __future__ import annotations

MEMORIE_MAX_MB = 6500.0


class MemoriePeste(RuntimeError):
    """Memoria plăcii a trecut de limită: unealta se oprește și scrie ce a apucat."""

    def __init__(self, mb: float, limita: float):
        super().__init__(f"memoria plăcii {mb:.0f} MB > limita {limita:.0f} MB: mă opresc")
        self.mb, self.limita = mb, limita


def memorie_folosita_mb(dispozitiv) -> float | None:
    """Vârful estimat al memoriei plăcii (MB, ca nvidia-smi); None pe procesor."""
    import torch

    if str(dispozitiv).split(":")[0] != "cuda" or not torch.cuda.is_available():
        return None
    torch.cuda.synchronize()
    torch.cuda.empty_cache()
    liber, total = torch.cuda.mem_get_info()
    acum = (total - liber) / 2**20
    rezervat = torch.cuda.memory_reserved() / 2**20
    varf = torch.cuda.max_memory_reserved() / 2**20
    return max(acum, acum - rezervat + varf)


class Paza:
    """Ține vârful văzut și oprește (MemoriePeste) peste limită. `citeste` se poate înlocui în teste."""

    def __init__(self, dispozitiv, limita: float = MEMORIE_MAX_MB, citeste=None):
        self.dispozitiv, self.limita = dispozitiv, float(limita)
        self.citeste = citeste or memorie_folosita_mb
        self.varf: float | None = None

    def verifica(self) -> float | None:
        mb = self.citeste(self.dispozitiv)
        if mb is None:
            return None
        self.varf = mb if self.varf is None else max(self.varf, mb)
        if mb > self.limita:
            raise MemoriePeste(mb, self.limita)
        return mb
