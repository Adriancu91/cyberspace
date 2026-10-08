"""Rularea unei încercări de cod (planul, secțiunea 4).

- **Codul interzis** se caută ÎNAINTE de rulare, fără excepție: `import`, `open(`, `__`, `exec`, `eval`, `os.`, `sys.`,
  `subprocess`, `input(`, `while True`. O apariție = „prins trișând”: încercarea nu se rulează, se șterge și se
  numără separat. Nu e o pedeapsă, e o sită; dar vrem să știm cât de des apare.
  - Din v0.2, potrivirea e pe cuvinte întregi: „important” nu mai e „import”, „evaluate” nu e „eval”, „chaos.” nu e
    „os.” (în pilotul v0.1, singura încercare „trișată” a fost „important”).
  - `__` rămâne prins oriunde.
- Restul rulează ca Python într-un **proces separat** (interpretorul de bază, `-I`: fără variabilele și pachetele
  utilizatorului), într-un **dosar temporar gol**, cu **mediul curățat**, fără argumente și cu **timeout**. Pe Windows,
  interpretorul din .venv e doar un lansator care pornește alt proces: îl ocolim, ca timeout-ul să oprească chiar
  codul încercat.
- **Semantica REPL**, exact ca în abecedar (unelte/fa_abecedar.py): o expresie singură își arată valoarea (cu print,
  dacă nu e None: `4` → 4, `2+3` → 5, `"dog"` → dog); altfel codul se execută, iar rezultatul e ce a afișat.
- Rezultatul se compară **exact** cu cel așteptat, după tăierea spațiilor de la capete (mai multe linii = mai multe
  linii).

Limită cunoscută: pe Windows nu avem container. Izolarea e proces + timeout + listă interzisă + dosar gol: destul
pentru cod de 1–5 linii.
"""

from __future__ import annotations

import contextlib
import io
import os
import re
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass

INTERZIS = ("import", "open(", "__", "exec", "eval", "os.", "sys.", "subprocess", "input(", "while True")
TIMEOUT_SECUNDE = 2.0
IESIRE_MAX = 2000  # caractere: mai mult înseamnă că încercarea a scris la nesfârșit

# Programul care rulează încercarea în procesul separat. Încercarea vine pe intrare (nu în linia de comandă), iar
# rezultatul iese în UTF-8, cu o limită de lungime. „import” e aici al nostru, nu al încercării.
RULEAZA = r"""
import io, sys
cod = sys.stdin.buffer.read().decode("utf-8")
class Limitat(io.StringIO):
    def write(self, s):
        if self.tell() + len(s) > LIMITA:
            raise RuntimeError("a scris prea mult")
        return super().write(s)
buf = Limitat()
vechi, sys.stdout = sys.stdout, buf
eroare = None
try:
    try:
        cod_eval = compile(cod, "<w>", "eval")
    except SyntaxError:
        exec(compile(cod, "<w>", "exec"), {})
    else:
        val = eval(cod_eval, {})
        if val is not None:
            print(val)
except BaseException as e:
    eroare = f"{type(e).__name__}: {e}"
sys.stdout = vechi
sys.stdout.buffer.write(buf.getvalue().rstrip("\n").encode("utf-8"))
if eroare:
    sys.stderr.buffer.write(eroare.encode("utf-8"))
    sys.exit(1)
"""


@dataclass
class Rulare:
    iesire: str               # ce a ieșit (rezultatul REPL), fără liniile goale de la final
    eroare: str | None        # excepția, timeout-ul, ieșirea prea lungă; None dacă a mers
    trisat: str | None        # codul interzis găsit (atunci încercarea nici nu s-a rulat)
    secunde: float

    @property
    def a_mers(self) -> bool:
        return self.eroare is None and self.trisat is None


def _model_interzis(bucata: str) -> re.Pattern[str]:
    """Bucata ca cuvânt întreg: o literă la capăt cere margine de cuvânt („import” nu prinde „important”); spațiile din
    ea se potrivesc cu oricâte spații („while  True”)."""
    model = r"\s+".join(re.escape(parte) for parte in bucata.split(" "))
    return re.compile((r"\b" if bucata[:1].isalpha() else "") + model + (r"\b" if bucata[-1:].isalpha() else ""))


def cod_interzis(cod: str, interzis: tuple[str, ...] | list[str] = INTERZIS) -> str | None:
    """Primul lucru interzis din cod (pe cuvinte întregi, fără excepție), sau None."""
    return next((bucata for bucata in interzis if _model_interzis(bucata).search(cod)), None)


def interpretor() -> str:
    """Interpretorul de bază (nu lansatorul din .venv), ca timeout-ul să oprească chiar procesul care rulează codul."""
    return getattr(sys, "_base_executable", None) or sys.executable


def ruleaza(cod: str, timeout: float = TIMEOUT_SECUNDE, interzis: tuple[str, ...] | list[str] = INTERZIS,
            iesire_max: int = IESIRE_MAX) -> Rulare:
    """Rulează încercarea în sandbox. Codul interzis nu se rulează deloc."""
    start = time.perf_counter()
    gasit = cod_interzis(cod, interzis)
    if gasit is not None:
        return Rulare("", None, gasit, 0.0)
    mediu = {"SYSTEMROOT": os.environ.get("SYSTEMROOT", r"C:\Windows")} if sys.platform == "win32" else {}
    with tempfile.TemporaryDirectory(prefix="kronos_cod_") as dosar:
        try:
            p = subprocess.run([interpretor(), "-I", "-c", RULEAZA.replace("LIMITA", str(iesire_max))],
                               input=cod.encode("utf-8"), capture_output=True, timeout=timeout, cwd=dosar, env=mediu)
        except subprocess.TimeoutExpired:
            return Rulare("", f"a depășit timpul ({timeout:g} s)", None, round(time.perf_counter() - start, 3))
    iesire = p.stdout.decode("utf-8", errors="replace").replace("\r\n", "\n")
    eroare = p.stderr.decode("utf-8", errors="replace").strip() or None if p.returncode else None
    if p.returncode and eroare is None:
        eroare = f"a ieșit cu codul {p.returncode}"
    return Rulare(iesire, eroare, None, round(time.perf_counter() - start, 3))


def ruleaza_in_proces(cod: str) -> str:
    """Aceeași semantică REPL, în procesul nostru: DOAR pentru soluțiile scrise de noi (rezultatele așteptate ale
    sarcinilor, ca în fa_abecedar.py). Încercările modelului trec numai prin ruleaza()."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            cod_eval = compile(cod, "<w>", "eval")
        except SyntaxError:
            exec(compile(cod, "<w>", "exec"), {})
        else:
            val = eval(cod_eval, {})
            if val is not None:
                print(val)
    return buf.getvalue().rstrip("\n")


def la_fel(iesire: str, asteptat: str) -> bool:
    """Comparația exactă, după tăierea spațiilor de la capete."""
    return iesire.strip() == asteptat.strip()
