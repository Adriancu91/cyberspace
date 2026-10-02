"""Paznicul: limitele și siguranța. Nu depinde de niciun modul înlocuibil.

Verifică:
- că o propunere atinge doar porturile permise (nu examenul, nu nucleul);
- că examenul n-a fost modificat (amprentă/hash a fișierului);
- timpul, memoria video și temperatura plăcii;
- butonul de oprire (fișierul STOP din folderul de lucru).
"""

from __future__ import annotations

import hashlib
import inspect
import json
import math
import shutil
import subprocess
from pathlib import Path
from typing import Any

from .contracte import Propunere, RezultatRulare

PORTURI_MODIFICABILE_IMPLICIT = ("model", "date")
TIPURI_PERMISE = (int, float, str, bool)


class Paznic:
    def __init__(self, setari: dict[str, Any], director_lucru: Path) -> None:
        self.timp_max_secunde = float(setari.get("timp_max_secunde", 600))
        self.timp_test_secunde = float(setari.get("timp_test_secunde", 60))
        self.memorie_gpu_max_mb = setari.get("memorie_gpu_max_mb")
        self.temperatura_gpu_max = setari.get("temperatura_gpu_max")
        self.pauza_racire_secunde = float(setari.get("pauza_racire_secunde", 60))
        self.incercari_racire = int(setari.get("incercari_racire", 5))
        self.porturi_modificabile = tuple(
            setari.get("porturi_modificabile", PORTURI_MODIFICABILE_IMPLICIT)
        )
        self.director = Path(director_lucru)
        self.director.mkdir(parents=True, exist_ok=True)
        self.fisier_stop = self.director / "STOP"
        self.fisier_amprente = self.director / "amprente.json"

    # --- butonul de oprire -------------------------------------------------

    def oprire_ceruta(self) -> bool:
        return self.fisier_stop.exists()

    def cere_oprire(self) -> None:
        self.fisier_stop.write_text("Șterge acest fișier ca platforma să poată porni din nou.\n")

    def anuleaza_oprire(self) -> None:
        self.fisier_stop.unlink(missing_ok=True)

    # --- propuneri -----------------------------------------------------------

    def verifica_propunere(self, propunere: Propunere) -> str | None:
        for port, setari in propunere.modificari.items():
            if port not in self.porturi_modificabile:
                return (
                    f"Propunerea vrea să schimbe portul „{port}”, dar agentul are voie doar la: "
                    f"{', '.join(self.porturi_modificabile)}"
                )
            if not isinstance(setari, dict):
                return f"Modificările pentru „{port}” trebuie să fie de forma {{setare: valoare}}"
            for cheie, valoare in setari.items():
                if not isinstance(valoare, TIPURI_PERMISE):
                    return f"Valoarea pentru „{port}.{cheie}” are un tip nepermis: {type(valoare).__name__}"
                if isinstance(valoare, float) and not math.isfinite(valoare):
                    return f"Valoarea pentru „{port}.{cheie}” nu e un număr finit"
        return None

    # --- examenul nu are voie să se schimbe ----------------------------------

    @staticmethod
    def amprenta_examen(examen: Any) -> str:
        sursa = inspect.getsourcefile(type(examen))
        if sursa is None:
            raise RuntimeError("Nu găsesc fișierul sursă al examenului")
        return hashlib.sha256(Path(sursa).read_bytes()).hexdigest()

    def _citeste_amprente(self) -> dict[str, str]:
        if not self.fisier_amprente.exists():
            return {}
        return json.loads(self.fisier_amprente.read_text(encoding="utf-8"))

    def verifica_examen(self, examen: Any) -> str | None:
        """La prima rulare memorează amprenta; apoi refuză orice schimbare."""
        nume = type(examen).__module__ + "." + type(examen).__qualname__
        actuala = self.amprenta_examen(examen)
        amprente = self._citeste_amprente()
        if nume not in amprente:
            amprente[nume] = actuala
            self.fisier_amprente.write_text(json.dumps(amprente, indent=2), encoding="utf-8")
            return None
        if amprente[nume] != actuala:
            return (
                f"Examenul „{nume}” s-a schimbat de la ultima aprobare. "
                "Dacă schimbarea e făcută de tine, rulează: python -m nucleu aproba-examen --config ..."
            )
        return None

    def aproba_examen(self, examen: Any) -> str:
        nume = type(examen).__module__ + "." + type(examen).__qualname__
        amprente = self._citeste_amprente()
        amprente[nume] = self.amprenta_examen(examen)
        self.fisier_amprente.write_text(json.dumps(amprente, indent=2), encoding="utf-8")
        return nume

    # --- consum ----------------------------------------------------------------

    def verifica_consum(self, rezultat: RezultatRulare) -> str | None:
        if rezultat.durata_secunde > self.timp_max_secunde:
            return f"A durat {rezultat.durata_secunde:.0f} s, limita e {self.timp_max_secunde:.0f} s"
        if (
            self.memorie_gpu_max_mb is not None
            and rezultat.memorie_gpu_max_mb is not None
            and rezultat.memorie_gpu_max_mb > float(self.memorie_gpu_max_mb)
        ):
            return (
                f"A folosit {rezultat.memorie_gpu_max_mb:.0f} MB memorie video, "
                f"limita e {float(self.memorie_gpu_max_mb):.0f} MB"
            )
        return None

    # --- temperatura -----------------------------------------------------------

    @staticmethod
    def temperatura_gpu() -> float | None:
        """Temperatura plăcii NVIDIA, sau None dacă nu se poate citi."""
        if shutil.which("nvidia-smi") is None:
            return None
        try:
            iesire = subprocess.run(
                ["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=10,
                check=True,
            ).stdout
            return float(iesire.strip().splitlines()[0])
        except (subprocess.SubprocessError, ValueError, IndexError, OSError):
            return None

    def prea_cald(self) -> str | None:
        if self.temperatura_gpu_max is None:
            return None
        temp = self.temperatura_gpu()
        if temp is not None and temp > float(self.temperatura_gpu_max):
            return f"Placa video are {temp:.0f}°C, limita e {float(self.temperatura_gpu_max):.0f}°C"
        return None
