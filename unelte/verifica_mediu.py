"""Verifică mediul de lucru (Faza 0): Python, Git, placa video, PyTorch, spațiu pe disc.

Rulează din folderul proiectului:
    python unelte/verifica_mediu.py
"""

from __future__ import annotations

import platform
import shutil
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

probleme: list[str] = []


def ok(text: str) -> None:
    print(f"  ✓ {text}")


def rau(text: str, cum_repari: str) -> None:
    print(f"  ✗ {text}\n      → {cum_repari}")
    probleme.append(text)


def info(text: str) -> None:
    print(f"  · {text}")


print("Verific mediul de lucru...\n")

# Python
v = sys.version_info
if v >= (3, 11):
    ok(f"Python {v.major}.{v.minor}.{v.micro}")
else:
    rau(f"Python {v.major}.{v.minor} e prea vechi", "Instalează Python 3.12 de pe python.org")

info(f"Sistem: {platform.system()} {platform.release()} ({platform.machine()})")

# Git
if shutil.which("git"):
    versiune = subprocess.run(["git", "--version"], capture_output=True, text=True).stdout.strip()
    ok(versiune)
else:
    rau("Git nu e instalat", "Instalează Git de pe git-scm.com")

# Placa video
if shutil.which("nvidia-smi"):
    r = subprocess.run(
        ["nvidia-smi", "--query-gpu=name,memory.total,driver_version,temperature.gpu", "--format=csv,noheader"],
        capture_output=True,
        text=True,
    )
    if r.returncode == 0 and r.stdout.strip():
        for linie in r.stdout.strip().splitlines():
            ok(f"Placă video: {linie}")
    else:
        rau("nvidia-smi nu răspunde", "Actualizează driverul NVIDIA")
else:
    rau("Nu găsesc nvidia-smi (driverul NVIDIA)", "Instalează driverul de pe nvidia.com sau din GeForce Experience")

# pytest
try:
    import pytest  # noqa: F401

    ok(f"pytest {pytest.__version__}")
except ImportError:
    rau("pytest nu e instalat", "pip install pytest")

# PyTorch
try:
    import torch

    ok(f"PyTorch {torch.__version__}")
    if torch.cuda.is_available():
        nume = torch.cuda.get_device_name(0)
        memorie = torch.cuda.get_device_properties(0).total_memory / 2**30
        ok(f"PyTorch vede placa: {nume} ({memorie:.1f} GB)")
        ok(f"bfloat16 suportat: {'da' if torch.cuda.is_bf16_supported() else 'nu'}")
        x = torch.randn(1024, 1024, device="cuda")
        (x @ x).sum().item()
        ok("Un calcul de probă pe GPU a mers")
    else:
        rau(
            "PyTorch e instalat, dar NU vede placa video (e varianta doar pentru procesor)",
            "Reinstalează PyTorch cu CUDA: comanda de pe pytorch.org/get-started/locally",
        )
except ImportError:
    info("PyTorch nu e instalat încă (necesar doar pentru modelul GPT)")

# Disc
liber = shutil.disk_usage(Path.cwd()).free / 2**30
(ok if liber > 20 else rau)(
    f"Spațiu liber pe disc: {liber:.0f} GB", *(() if liber > 20 else ("Eliberează spațiu (minim 20 GB)",))
)

print()
if probleme:
    print(f"Sunt {len(probleme)} probleme de rezolvat (vezi ✗ mai sus).")
    sys.exit(1)
print("Totul e în regulă.")
