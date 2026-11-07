"""S77b (C-64 R2 pasul 2, 5 nov 2026): antrenarea lungă cu recalculul activărilor, fără nicio schimbare în module/.

În procesul acesta (și doar în el), după ce `ModelGPTConversatieMuon._pregateste_reteaua()` a construit rețeaua, fiecare
strat e împachetat în `torch.utils.checkpoint` (`use_reentrant=False`), exact ca `masoara_unul` din creste_model.py: la
întoarcere, stratul își recalculează activările în loc să le țină minte (mai puțină memorie pe placă, ~30 % mai încet).
Apoi rulează `antrenare_lunga.main(...)` cu aceleași argumente; Kronos (RulareLocala) antrenează în același proces, într-un
fir, deci vede clasa împachetată.

Împachetarea e o metodă legată de strat (types.MethodType), nu o închidere: o copie a rețelei (copy.deepcopy) rămâne
împachetată pe straturile ei, iar state_dict-ul nu se schimbă (nicio cheie nouă). La examen (fără gradiente sau în
modul eval) stratul rulează direct, fără checkpoint.

`--memorie-max-mb` (implicit 5.800): plafonul PyTorch pe placă (set_per_process_memory_fraction), ca nvidia-smi să nu
urce peste ~6.700 MB (lecția S77a: cu 6,6 GB, nvidia-smi a urcat scurt la 7,2–7,4 GB). 0 = fără plafon.

    python unelte/antrenare_recalcul.py --config config/conv_w2_mare_24.toml --ore 5
"""

from __future__ import annotations

import argparse
import sys
import types
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

MEMORIE_MAX_MB = 5800


def _inainte_cu_recalcul(self: Any, x: Any) -> Any:
    """forward-ul stratului, cu recalcul la antrenare (gradiente + train); altfel exact forward-ul clasei."""
    import torch
    from torch.utils.checkpoint import checkpoint

    if torch.is_grad_enabled() and self.training:
        return checkpoint(type(self).forward, self, x, use_reentrant=False)
    return type(self).forward(self, x)


def e_impachetat(strat: Any) -> bool:
    return getattr(strat.__dict__.get("forward"), "__func__", None) is _inainte_cu_recalcul


def impacheteaza(retea: Any) -> int:
    """Pune recalculul pe fiecare strat din retea.straturi; întoarce câte straturi sunt împachetate."""
    for strat in retea.straturi:
        if not e_impachetat(strat):
            strat.forward = types.MethodType(_inainte_cu_recalcul, strat)
    return sum(e_impachetat(s) for s in retea.straturi)


def instaleaza(clasa: Any = None) -> Any:
    """_pregateste_reteaua al clasei (implicit ModelGPTConversatieMuon) împachetează straturile după ce a construit
    rețeaua. Doar în procesul acesta; fișierul module/ nu se schimbă. A doua chemare nu mai face nimic."""
    if clasa is None:
        from module.model_muon import ModelGPTConversatieMuon as clasa
    original = clasa._pregateste_reteaua
    if getattr(original, "_cu_recalcul", False):
        return clasa
    era_in_clasa = "_pregateste_reteaua" in clasa.__dict__

    def _pregateste_reteaua(self: Any) -> None:
        original(self)
        n = impacheteaza(self.retea)
        if not getattr(self, "_recalcul_anuntat", False):
            print(f"   Recalculul activărilor: {n} straturi împachetate (torch.utils.checkpoint, use_reentrant=False).",
                  flush=True)
            self._recalcul_anuntat = True

    _pregateste_reteaua._cu_recalcul = True  # type: ignore[attr-defined]
    _pregateste_reteaua._original = original  # type: ignore[attr-defined]
    _pregateste_reteaua._era_in_clasa = era_in_clasa  # type: ignore[attr-defined]
    clasa._pregateste_reteaua = _pregateste_reteaua
    return clasa


def dezinstaleaza(clasa: Any = None) -> None:
    if clasa is None:
        from module.model_muon import ModelGPTConversatieMuon as clasa
    actual = clasa.__dict__.get("_pregateste_reteaua")
    if getattr(actual, "_cu_recalcul", False):
        if actual._era_in_clasa:
            clasa._pregateste_reteaua = actual._original
        else:  # originalul era moștenit: ștergem doar ce am pus noi
            delattr(clasa, "_pregateste_reteaua")


def plafon_placa(memorie_max_mb: int) -> float | None:
    """set_per_process_memory_fraction pentru memorie_max_mb; None dacă nu e placă sau plafonul e 0."""
    if memorie_max_mb <= 0:
        return None
    import torch

    if not torch.cuda.is_available():
        return None
    total_mb = torch.cuda.get_device_properties(0).total_memory / 2**20
    fractie = min(1.0, memorie_max_mb / total_mb)
    torch.cuda.set_per_process_memory_fraction(fractie)
    return fractie


PRAG_PAZA_MB = 6700  # S86: peste atât nvidia-smi înainte de testul rapid al unei ore → oprire curată


class PazaMemorie(RuntimeError):
    """Memoria plăcii e prea sus înainte de testul rapid al unei ore."""


def nvidia_smi_mb() -> int | None:
    """Memoria folosită pe placă după nvidia-smi (MB); None dacă nu se poate citi."""
    import subprocess

    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=30)
        return int(r.stdout.strip().splitlines()[0])
    except (OSError, ValueError, IndexError, subprocess.TimeoutExpired):
        return None


def verifica_memoria(ora: int, prag_mb: int = PRAG_PAZA_MB, citeste: Any = None) -> int | None:
    """Înainte de testul rapid al orei: golește memoria rezervată fără folos (empty_cache), citește nvidia-smi; peste
    prag ridică PazaMemorie cu ora și MB (ora se anulează → antrenare_lunga iese cu cod 1 și motivul în log)."""
    import torch

    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    mb = (citeste or nvidia_smi_mb)()
    if mb is not None and mb > prag_mb:
        mesaj = (f"paza de memorie: ora {ora} din procesul acesta, nvidia-smi {mb:,} MB > {prag_mb:,} MB înainte de "
                 f"testul rapid — oprire curată")
        print(f"   {mesaj}", flush=True)
        raise PazaMemorie(mesaj)
    return mb


def instaleaza_paza(clasa: Any = None, prag_mb: int = PRAG_PAZA_MB, citeste: Any = None) -> Any:
    """antreneaza al clasei verifică memoria înainte de fiecare test rapid (buget ≤ 2 s, ca în orchestrator) și
    numără orele. Doar în procesul acesta; a doua chemare nu mai face nimic."""
    if clasa is None:
        from module.model_muon import ModelGPTConversatieMuon as clasa
    original = clasa.antreneaza
    if getattr(original, "_cu_paza", False):
        return clasa
    stare = {"ora": 0}

    def antreneaza(self: Any, date: Any, buget_secunde: float) -> Any:
        if buget_secunde <= 2.0:
            stare["ora"] += 1
            verifica_memoria(stare["ora"], prag_mb, citeste)
        return original(self, date, buget_secunde)

    antreneaza._cu_paza = True  # type: ignore[attr-defined]
    antreneaza._original = original  # type: ignore[attr-defined]
    antreneaza._era_in_clasa = "antreneaza" in clasa.__dict__  # type: ignore[attr-defined]
    antreneaza._stare = stare  # type: ignore[attr-defined]
    clasa.antreneaza = antreneaza
    return clasa


def dezinstaleaza_paza(clasa: Any = None) -> None:
    if clasa is None:
        from module.model_muon import ModelGPTConversatieMuon as clasa
    actual = clasa.__dict__.get("antreneaza")
    if getattr(actual, "_cu_paza", False):
        if actual._era_in_clasa:
            clasa.antreneaza = actual._original
        else:
            delattr(clasa, "antreneaza")


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0], add_help=False)
    p.add_argument("--memorie-max-mb", type=int, default=MEMORIE_MAX_MB)
    p.add_argument("--paza-mb", type=int, default=PRAG_PAZA_MB)
    a, rest = p.parse_known_args(argv)
    fractie = plafon_placa(a.memorie_max_mb)
    if fractie is not None:
        print(f"   Plafonul PyTorch pe placă: {a.memorie_max_mb:,} MB (fracția {fractie:.3f}).", flush=True)
    instaleaza()
    if a.paza_mb > 0:
        instaleaza_paza(prag_mb=a.paza_mb)
        print(f"   Paza de memorie: înainte de fiecare test rapid, peste {a.paza_mb:,} MB nvidia-smi → oprire.",
              flush=True)
    from unelte import antrenare_lunga

    return antrenare_lunga.main(rest)


if __name__ == "__main__":
    raise SystemExit(main())
