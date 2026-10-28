"""Partea din interiorul cutiei (S41, 28 octombrie 2026): rulează în procesul separat pornit de `cutie.py`.

Nu se importă din alt cod. Ordinea contează:
1. așteaptă pe intrare mesajul părintelui (îl trimite abia după ce a pus procesul în „job”-ul cu limite);
2. încarcă dinainte modulele permise (după ce pornește paznicul, niciun `import` nou nu mai e voie);
3. verifică codul pe arbore (importuri, nume și atribute interzise), pornește paznicul (`sys.addaudithook`, nu se
   mai poate scoate) și rulează codul + testele cu un `__builtins__` tăiat;
4. scrie un singur rând de rezultat, care începe cu semnul secret primit de la părinte.
"""

import ast
import builtins
import io
import json
import os
import sys
import types

# Modulele de bază pe care le poate importa codul verificat (fără os, sys, subprocess, socket, ctypes, importlib ...).
MODULE_DE_BAZA = (
    "math", "cmath", "itertools", "functools", "collections", "heapq", "bisect", "string", "re", "operator",
    "fractions", "decimal", "statistics", "random", "typing", "dataclasses", "enum", "copy", "json", "datetime",
    "textwrap", "unicodedata", "array",
)
# Ce scot din `__builtins__` (deschiderea de fișiere și `__import__` se înlocuiesc cu variantele păzite).
BUILTINS_INTERZISE = (
    "eval", "exec", "compile", "input", "breakpoint", "globals", "locals", "vars", "getattr", "setattr", "delattr",
    "help", "exit", "quit", "copyright", "credits", "license",
)
NUME_INTERZISE = set(BUILTINS_INTERZISE) | {"__import__", "__builtins__", "__loader__", "__spec__"}

# Evenimentele de audit blocate oricum (rețea, procese, biblioteci native, registru, ștergeri/copieri în masă).
PREFIXE_BLOCATE = (
    "socket.", "subprocess.", "os.system", "os.exec", "os.spawn", "os.posix_spawn", "os.startfile", "os.fork",
    "os.kill", "os.putenv", "os.unsetenv", "os.chdir", "ctypes.", "winreg.", "_winapi.", "msvcrt.", "shutil.",
    "urllib.", "http.", "ftplib.", "smtplib.", "poplib.", "imaplib.", "nntplib.", "telnetlib.", "webbrowser.",
    "sys._getframe", "sys.setprofile", "sys.settrace", "code.", "cpython.", "_posixsubprocess.", "pty.", "mmap.",
)
# Evenimentele cu o cale ca prim argument: voie doar în dosarul cutiei.
EVENIMENTE_CU_CALE = (
    "os.remove", "os.rename", "os.mkdir", "os.rmdir", "os.listdir", "os.scandir", "os.chmod", "os.chown",
    "os.symlink", "os.link", "os.truncate", "os.utime", "glob.glob", "pathlib.Path.glob",
)


class Interzis(Exception):
    """Codul a încercat ceva ce cutia nu permite."""


def verifica_arborele(cod: str, module_permise: set) -> list:
    """Verificarea dinainte de rulare: importuri doar din listă, fără nume interzise, fără atribute cu `_` în față."""
    probleme = []
    try:
        arbore = ast.parse(cod)
    except SyntaxError as e:
        return [f"sintaxă: {e.msg} (rândul {e.lineno})"]
    for nod in ast.walk(arbore):
        if isinstance(nod, ast.Import):
            for alias in nod.names:
                if alias.name.split(".")[0] not in module_permise:
                    probleme.append(f"import interzis: {alias.name}")
        elif isinstance(nod, ast.ImportFrom):
            if nod.level or (nod.module or "").split(".")[0] not in module_permise:
                probleme.append(f"import interzis: {nod.module}")
        elif isinstance(nod, ast.Name) and (nod.id in NUME_INTERZISE or nod.id.startswith("__")):
            probleme.append(f"nume interzis: {nod.id}")
        elif isinstance(nod, ast.Attribute) and nod.attr.startswith("_"):
            probleme.append(f"atribut interzis: .{nod.attr}")
    return probleme


def _modul_curatat(modul):
    """Copie a modulului doar cu numele publice și fără alte module în ea (de ex. `typing.sys`, `random._os`)."""
    copie = types.ModuleType(modul.__name__)
    for nume in dir(modul):
        if nume.startswith("_"):
            continue
        valoare = getattr(modul, nume)
        if isinstance(valoare, types.ModuleType):
            continue
        setattr(copie, nume, valoare)
    return copie


def main() -> int:
    mesaj = json.loads(sys.stdin.readline())
    # `module_extra` există doar pentru testele cutiei (arată că paznicul blochează și când importul a trecut).
    permise = set(MODULE_DE_BAZA) | set(mesaj.get("module_extra", []))
    for nume in sorted(permise) + ["_strptime", "encodings.idna"]:
        __import__(nume)
    curatate = {nume: _modul_curatat(sys.modules[nume]) for nume in permise}

    semn = mesaj["semn"]
    dosar = os.path.realpath(mesaj["dosar"])
    iesire = sys.stdout
    cale_reala = os.path.realpath
    cale_comuna = os.path.commonpath
    rezultat = {"stare": "ok", "teste_trecute": 0, "teste_total": len(mesaj["teste"]), "blocate": [], "mesaj": ""}

    def scrie(r):
        r["iesire_cod"] = r.get("iesire_cod", "")[:2000]
        iesire.write(semn + json.dumps(r, ensure_ascii=False) + "\n")
        iesire.flush()

    if mesaj.get("verificare_statica", True):
        probleme = verifica_arborele(mesaj["cod"], permise)
        if probleme:
            rezultat.update(stare="interzis", mesaj="; ".join(probleme[:10]))
            scrie(rezultat)
            return 0

    def in_dosar(cale) -> bool:
        if isinstance(cale, int):
            return False
        try:
            cale = os.fsdecode(cale)
            return cale_comuna([dosar, cale_reala(os.path.join(dosar, cale))]) == dosar
        except (TypeError, ValueError):
            return False

    def bloca(motiv):
        if len(rezultat["blocate"]) < 20:
            rezultat["blocate"].append(motiv)
        raise Interzis(motiv)

    def paznic(eveniment, argumente):
        if eveniment == "open":
            if not in_dosar(argumente[0]):
                bloca(f"open {argumente[0]!r}")
        elif eveniment == "import":
            bloca(f"import {argumente[0]}")
        elif eveniment in EVENIMENTE_CU_CALE:
            if not argumente or not in_dosar(argumente[0]):
                bloca(f"{eveniment} {argumente[:1]!r}")
        elif eveniment.startswith(PREFIXE_BLOCATE):
            bloca(eveniment)

    def import_pazit(nume, globale=None, locale=None, din=(), nivel=0):
        if nivel or nume.split(".")[0] not in permise:
            bloca(f"import {nume}")
        return curatate[nume.split(".")[0]]

    def open_pazit(fisier, *args, **kwargs):
        if not in_dosar(fisier):
            bloca(f"open {fisier!r}")
        return builtins.open(fisier, *args, **kwargs)

    tabel = {k: v for k, v in vars(builtins).items() if k not in BUILTINS_INTERZISE}
    tabel["__import__"] = import_pazit
    tabel["open"] = open_pazit
    spatiu = {"__builtins__": tabel, "__name__": "cutie"}
    captura = io.StringIO()
    compilate = [compile(t, f"<test {i}>", "exec") for i, t in enumerate(mesaj["teste"])]
    cod = compile(mesaj["cod"], "<cod>", "exec")

    sys.addaudithook(paznic)
    sys.stdout = sys.stderr = captura
    try:
        exec(cod, spatiu)
    except MemoryError:
        rezultat.update(stare="memorie", mesaj="MemoryError la încărcarea codului")
    except BaseException as e:  # noqa: BLE001 — orice ar arunca codul verificat
        rezultat.update(stare="eroare", mesaj=f"{type(e).__name__}: {str(e)[:300]}")
    else:
        for test in compilate:
            try:
                exec(test, spatiu)
                rezultat["teste_trecute"] += 1
            except MemoryError:
                rezultat.update(stare="memorie", mesaj="MemoryError")
                break
            except BaseException as e:  # noqa: BLE001
                if not rezultat["mesaj"]:
                    rezultat["mesaj"] = f"{type(e).__name__}: {str(e)[:300]}"
        if rezultat["stare"] == "ok" and rezultat["teste_trecute"] < rezultat["teste_total"]:
            rezultat["stare"] = "picat"
    if rezultat["blocate"]:
        rezultat["stare"] = "blocat"
    rezultat["iesire_cod"] = captura.getvalue()
    scrie(rezultat)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
