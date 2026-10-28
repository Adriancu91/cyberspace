"""Cutia izolată pentru codul de verificat (S41, C-28 „Kronos-Cod”, 28 octombrie 2026).

Codul (de exemplu un răspuns al modelului de cod) rulează într-un PROCES SEPARAT, cu dosarul de lucru un dosar
temporar nou, și trece prin patru straturi:

1. **verificarea dinainte** (pe arborele codului): importuri doar din lista permisă (fără `os`, `sys`, `subprocess`,
   `socket`, `ctypes`, `importlib` ...), fără `eval`/`exec`/`getattr`/`__import__`, fără atribute cu `_` în față;
2. **`__builtins__` tăiat**: `open` deschide doar în dosarul cutiei, `__import__` dă doar copii curățate ale
   modulelor permise;
3. **paznicul de audit** (`sys.addaudithook`, nu se poate scoate odată pornit): blochează orice fișier în afara
   dosarului, rețeaua, pornirea de procese, `ctypes`, registrul și orice import nou;
4. **limitele procesului**: timpul (procesul e oprit după `limita_secunde`) și, pe Windows, un „job object”
   (din `kernel32`, fără nimic instalat) cu limită de memorie, limită de timp de procesor și cel mult UN proces
   (deci nici un proces copil). Pe Linux/macOS, `resource.setrlimit`.

Ce NU face (scris și în raportul S41): nu e o mașină virtuală; rețeaua e oprită doar din interiorul lui Python
(paznicul), nu printr-o regulă de firewall (aceea ar cere o schimbare de setări Windows).
"""

from __future__ import annotations

import json
import os
import secrets
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

INTERIOR = Path(__file__).resolve().parent / "_cutie_interior.py"
# Pe Windows, python.exe din .venv e doar un lansator care pornește alt proces: folosim interpretorul de bază.
PYTHON = getattr(sys, "_base_executable", None) or sys.executable


@dataclass
class Rezultat:
    stare: str  # ok | picat | eroare | interzis | blocat | timp | memorie | cazut
    teste_trecute: int = 0
    teste_total: int = 0
    mesaj: str = ""
    blocate: list = field(default_factory=list)
    iesire_cod: str = ""
    secunde: float = 0.0

    @property
    def trecut(self) -> bool:
        return self.stare == "ok" and self.teste_trecute == self.teste_total


class _Job:
    """Job object pe Windows: memorie, timp de procesor, un singur proces; închis = procesul e oprit."""

    def __init__(self, limita_mb: int, limita_secunde_procesor: float):
        import ctypes
        from ctypes import wintypes

        class IO_COUNTERS(ctypes.Structure):
            _fields_ = [(n, ctypes.c_ulonglong) for n in (
                "ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
                "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]

        class BASIC(ctypes.Structure):
            _fields_ = [("PerProcessUserTimeLimit", ctypes.c_longlong), ("PerJobUserTimeLimit", ctypes.c_longlong),
                        ("LimitFlags", wintypes.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
                        ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", wintypes.DWORD),
                        ("Affinity", ctypes.c_size_t), ("PriorityClass", wintypes.DWORD),
                        ("SchedulingClass", wintypes.DWORD)]

        class EXTINS(ctypes.Structure):
            _fields_ = [("BasicLimitInformation", BASIC), ("IoInfo", IO_COUNTERS),
                        ("ProcessMemoryLimit", ctypes.c_size_t), ("JobMemoryLimit", ctypes.c_size_t),
                        ("PeakProcessMemoryUsed", ctypes.c_size_t), ("PeakJobMemoryUsed", ctypes.c_size_t)]

        self._ctypes = ctypes
        self._EXTINS = EXTINS
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.CreateJobObjectW.restype = wintypes.HANDLE
        k32.CreateJobObjectW.argtypes = (ctypes.c_void_p, wintypes.LPCWSTR)
        k32.SetInformationJobObject.argtypes = (wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD)
        k32.QueryInformationJobObject.argtypes = (wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD,
                                                  ctypes.c_void_p)
        k32.AssignProcessToJobObject.argtypes = (wintypes.HANDLE, wintypes.HANDLE)
        k32.CloseHandle.argtypes = (wintypes.HANDLE,)
        self._k32 = k32
        self.handle = k32.CreateJobObjectW(None, None)
        if not self.handle:
            raise OSError(ctypes.get_last_error(), "CreateJobObjectW")
        info = EXTINS()
        info.BasicLimitInformation.LimitFlags = 0x100 | 0x2000 | 0x8 | 0x2  # memorie, ucide la închidere, procese, timp
        info.BasicLimitInformation.ActiveProcessLimit = 1
        info.BasicLimitInformation.PerProcessUserTimeLimit = int(limita_secunde_procesor * 10_000_000)
        info.ProcessMemoryLimit = limita_mb * 1024 * 1024
        if not k32.SetInformationJobObject(self.handle, 9, ctypes.byref(info), ctypes.sizeof(info)):
            raise OSError(ctypes.get_last_error(), "SetInformationJobObject")

    def adauga(self, proces: subprocess.Popen) -> None:
        if not self._k32.AssignProcessToJobObject(self.handle, int(proces._handle)):
            raise OSError(self._ctypes.get_last_error(), "AssignProcessToJobObject")

    def varf_memorie_mb(self) -> float:
        info = self._EXTINS()
        self._k32.QueryInformationJobObject(self.handle, 9, self._ctypes.byref(info), self._ctypes.sizeof(info), None)
        return info.PeakProcessMemoryUsed / 1024 / 1024

    def inchide(self) -> None:
        if self.handle:
            self._k32.CloseHandle(self.handle)
            self.handle = None


def _limite_posix(limita_mb: int, limita_secunde: float):
    def aplica():
        import resource
        octeti = limita_mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (octeti, octeti))
        resource.setrlimit(resource.RLIMIT_CPU, (int(limita_secunde) + 1, int(limita_secunde) + 1))
        resource.setrlimit(resource.RLIMIT_NPROC, (0, 0))
    return aplica


def ruleaza(cod: str, teste: list[str] | None = None, *, limita_secunde: float = 5.0, limita_mb: int = 256,
            verificare_statica: bool = True, module_extra: tuple[str, ...] = (),
            fisiere: dict[str, str] | None = None) -> Rezultat:
    """Rulează `cod`, apoi fiecare test (câte un șir de cod, de obicei un `assert`), în cutie.

    `fisiere` = fișiere puse în dosarul temporar înainte de rulare (singurele pe care codul le poate citi).
    `verificare_statica=False` și `module_extra` sunt pentru testele cutiei (arată că straturile 2–4 blochează singure).
    """
    import time

    teste = list(teste or [])
    semn = "@@CUTIE-" + secrets.token_hex(16) + "@@"
    inceput = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="cutie_") as dosar:
        for nume, continut in (fisiere or {}).items():
            (Path(dosar) / nume).write_text(continut, encoding="utf-8")
        mesaj = json.dumps({"semn": semn, "dosar": dosar, "cod": cod, "teste": teste,
                            "verificare_statica": verificare_statica, "module_extra": list(module_extra)})
        mediu = {k: os.environ[k] for k in ("SYSTEMROOT", "WINDIR", "TEMP", "TMP") if k in os.environ}
        argumente = [PYTHON, "-I", "-X", "utf8", "-B", str(INTERIOR)]
        job = None
        if os.name == "nt":
            proces = subprocess.Popen(argumente, cwd=dosar, env=mediu, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
            try:
                job = _Job(limita_mb, limita_secunde)
                job.adauga(proces)
            except OSError:
                proces.kill()
                proces.communicate()
                if job:
                    job.inchide()
                raise
        else:
            proces = subprocess.Popen(argumente, cwd=dosar, env=mediu, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE, preexec_fn=_limite_posix(limita_mb, limita_secunde))
        try:
            iesire, eroare = proces.communicate(mesaj.encode("utf-8") + b"\n", timeout=limita_secunde)
        except subprocess.TimeoutExpired:
            proces.kill()
            proces.communicate()
            if job:
                job.inchide()
            return Rezultat("timp", 0, len(teste), f"depășit {limita_secunde} s",
                            secunde=time.perf_counter() - inceput)
        varf = job.varf_memorie_mb() if job else 0.0
        if job:
            job.inchide()
    secunde = time.perf_counter() - inceput
    for rand in iesire.decode("utf-8", "replace").splitlines():
        if rand.startswith(semn):
            d = json.loads(rand[len(semn):])
            return Rezultat(d["stare"], d["teste_trecute"], d["teste_total"], d["mesaj"], d["blocate"],
                            d.get("iesire_cod", ""), secunde)
    # Fără rândul de rezultat: procesul a murit (de obicei la limita de memorie sau de timp de procesor).
    text = eroare.decode("utf-8", "replace")[-500:]
    stare = "memorie" if ("MemoryError" in text or varf >= limita_mb * 0.9) else "cazut"
    return Rezultat(stare, 0, len(teste), f"cod de ieșire {proces.returncode}; {text}".strip(), secunde=secunde)


if __name__ == "__main__":
    r = ruleaza("x = sum(range(10))", ["assert x == 45"])
    print(r)
