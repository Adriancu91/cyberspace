"""Paznicul școlii de cod (planul, secțiunea 9), în afara buclei:

- **amprente** (sha256) pe generatorul de teste, setul sacru, abecedar și codul sandbox-ului, aprobate o dată în
  lucru/cod/amprente.json. O schimbare neaprobată oprește școala. După o schimbare aprobată de om:
  `python unelte/scoala_cod.py --aproba-amprente`;
- **placa:**
  - temperatura sub `temperatura_max` (altfel se așteaptă răcirea până la `racire_la`);
  - memoria video sub limită;
  - un singur lucru pe placă: niciun alt proces pe ea;
- **alimentarea:** pe baterie, placa încetinește (noaptea 6) și bugetul de timp n-ar mai fi cinstit. Se așteaptă
  încărcătorul, apoi oprire;
- **STOP:** fișierul lucru/STOP din worktree (același buton ca la Kronos, dar al acestui folder);
- bugetele (timp și runde pe nivel) și numărarea încercărilor „trișat” sunt în buclă (unelte/scoala_cod.py).

Senzorii (temperatura, procesele de pe placă, alimentarea) se citesc prin `Senzori`, ca testele să-i poată înlocui.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

from kronos.paznic import Paznic  # doar citire: temperatura plăcii, ca la Kronos

AMPRENTATE = {"generatorul de teste": "module/cod/examen_cod.py", "setul sacru": "date/cod/sacru.json",
              "abecedarul": "date/cod/abecedar.txt", "sandbox-ul": "module/cod/sandbox.py"}


def amprenta(cale: Path) -> str:
    """sha256 pe conținut, cu sfârșitul de rând unificat: Git pe Windows rescrie LF ↔ CRLF fără să schimbe nimic din
    fișier, iar asta nu trebuie să oprească școala."""
    return hashlib.sha256(cale.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def amprente(radacina: Path) -> dict[str, str]:
    return {nume: amprenta(radacina / cale) if (radacina / cale).exists() else "lipsește"
            for nume, cale in AMPRENTATE.items()}


def aproba(radacina: Path, lucru: Path) -> dict[str, str]:
    """Amprentele de acum devin cele aprobate."""
    acum = amprente(radacina)
    fisier = lucru / "cod" / "amprente.json"
    fisier.parent.mkdir(parents=True, exist_ok=True)
    fisier.write_text(json.dumps({"aprobat": datetime.now().isoformat(timespec="seconds"), "amprente": acum,
                                  "fisiere": AMPRENTATE}, ensure_ascii=False, indent=1), encoding="utf-8")
    return acum


def verifica(radacina: Path, lucru: Path) -> str | None:
    """De ce trebuie oprită școala (amprente neaprobate sau schimbate), sau None."""
    fisier = lucru / "cod" / "amprente.json"
    if not fisier.exists():
        return "amprentele n-au fost aprobate încă: python unelte/scoala_cod.py --aproba-amprente"
    aprobate = json.loads(fisier.read_text(encoding="utf-8"))["amprente"]
    schimbate = [nume for nume, valoare in amprente(radacina).items() if aprobate.get(nume) != valoare]
    if schimbate:
        return (f"s-a schimbat fără aprobare: {', '.join(schimbate)}. Dacă schimbarea e aprobată de om: "
                f"python unelte/scoala_cod.py --aproba-amprente")
    return None


def oprire_ceruta(lucru: Path) -> bool:
    return (lucru / "STOP").exists()


# --- senzorii ---------------------------------------------------------------------------------------------------------

def _nvidia_smi(*argumente: str) -> list[str] | None:
    if shutil.which("nvidia-smi") is None:
        return None
    try:
        rezultat = subprocess.run(["nvidia-smi", *argumente], capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.SubprocessError):
        return None
    return [r.strip() for r in rezultat.stdout.splitlines() if r.strip()] if rezultat.returncode == 0 else None


def alte_procese_pe_placa() -> list[str] | None:
    """Procesele care calculează pe placa video, în afară de acesta (sau None, dacă nu se poate afla)."""
    randuri = _nvidia_smi("--query-compute-apps=pid,process_name,used_memory", "--format=csv,noheader")
    if randuri is None:
        return None
    alte = []
    for rand in randuri:
        parti = [p.strip() for p in rand.split(",")]
        if parti[0].isdigit() and int(parti[0]) != os.getpid():
            alte.append(" ".join(parti))
    return alte


def memorie_ocupata_mb() -> int | None:
    randuri = _nvidia_smi("--query-gpu=memory.used", "--format=csv,noheader,nounits")
    try:
        return int(randuri[0]) if randuri else None
    except ValueError:
        return None


def pe_baterie() -> bool | None:
    """True dacă laptopul merge pe baterie (fără încărcător), False pe încărcător, None dacă nu se poate afla."""
    if sys.platform != "win32":
        return None
    import ctypes

    class _Alimentare(ctypes.Structure):
        _fields_ = [("ACLineStatus", ctypes.c_ubyte), ("BatteryFlag", ctypes.c_ubyte),
                    ("BatteryLifePercent", ctypes.c_ubyte), ("SystemStatusFlag", ctypes.c_ubyte),
                    ("BatteryLifeTime", ctypes.c_ulong), ("BatteryFullLifeTime", ctypes.c_ulong)]

    stare = _Alimentare()
    if not ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(stare)):
        return None
    return {0: True, 1: False}.get(stare.ACLineStatus)


@dataclass
class Senzori:
    """Ce citește paznicul de pe laptop. În teste, se înlocuiesc cu funcții care întorc ce vrea testul."""
    temperatura: Callable[[], float | None] = Paznic.temperatura_gpu
    alte_procese: Callable[[], list[str] | None] = alte_procese_pe_placa
    memorie_ocupata_mb: Callable[[], int | None] = memorie_ocupata_mb
    pe_baterie: Callable[[], bool | None] = pe_baterie
    asteapta: Callable[[float], None] = time.sleep


def de_ce_nu_e_libera(senzori: Senzori, memorie_max_mb: int = 1000) -> str | None:
    """La pornire: alt proces pe placă sau memorie video ocupată de altcineva („un singur lucru pe placă”)."""
    alte = senzori.alte_procese()
    if alte:
        return "placa nu e liberă: " + "; ".join(alte)
    ocupat = senzori.memorie_ocupata_mb()
    if ocupat is not None and ocupat > memorie_max_mb:
        return f"placa nu e liberă: {ocupat} MB de memorie video ocupați de alt program"
    return None


def asteapta_racirea(temperatura_max: float, racire_la: float, senzori: Senzori, pauza: float = 30.0,
                     maxim_secunde: float = 1800.0) -> str | None:
    """Peste temperatura_max: așteaptă până la racire_la (cel mult maxim_secunde). Întoarce ce s-a întâmplat, pentru
    jurnal, sau None dacă placa era rece."""
    temp = senzori.temperatura()
    if temp is None or temp <= temperatura_max:
        return None
    asteptat = 0.0
    while temp is not None and temp > racire_la and asteptat < maxim_secunde:
        senzori.asteapta(pauza)
        asteptat += pauza
        temp = senzori.temperatura()
    return f"placa avea peste {temperatura_max:g} °C: am așteptat {asteptat:.0f} s, până la {temp} °C"


def asteapta_incarcatorul(senzori: Senzori, pauza: float = 30.0, maxim_secunde: float = 600.0) -> tuple[bool, str | None]:
    """(se poate continua, ce s-a întâmplat). Pe baterie: se așteaptă încărcătorul cel mult maxim_secunde."""
    if not senzori.pe_baterie():
        return True, None
    asteptat = 0.0
    while senzori.pe_baterie() and asteptat < maxim_secunde:
        senzori.asteapta(pauza)
        asteptat += pauza
    if senzori.pe_baterie():
        return False, (f"laptopul merge pe baterie de cel puțin {asteptat:.0f} s: placa încetinește și bugetul de timp "
                       f"n-ar mai fi cinstit")
    return True, f"laptopul a mers pe baterie: am așteptat încărcătorul {asteptat:.0f} s"
