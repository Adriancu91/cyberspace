"""Ajutorul executantului din cascadă (19 octombrie 2026, cerut de Adrian; regulile: plan/REGULI_CASCADA.md).

Executantul (Claude Code pornit la 30 de minute de sarcina Windows „Kronos executant coada”) nu stă lângă o
antrenare de 3 ore: o pornește desprinsă de el, iese, iar rulările următoare se uită dacă s-a terminat.

    python unelte/cascada.py stare                       # placa, procesele grele, fereastra, sarcinile pornite
    python unelte/cascada.py porneste S4 -- python -X utf8 unelte/antrenare_lunga.py --config ... --ore 3
    python unelte/cascada.py sarcina S4                  # merge? s-a terminat? cu ce cod? ultimele rânduri
    python unelte/cascada.py porneste S4 --din-nou -- ...  # S4 terminată: mută S4.json/.log în S4_<HHMM>.*, pornește

Fiecare sarcină pornită are lucru/cascada/S<n>.json (comanda, procesul, pornirea, iar la final codul) și
lucru/cascada/S<n>.log (tot ce a scris). Unealta doar pornește și citește; nu oprește și nu șterge nimic.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, time, timedelta
from pathlib import Path

RADACINA = Path(__file__).resolve().parent.parent
DOSAR = RADACINA / "lucru" / "cascada"
# Ferestrele plăcii (Adrian, 19 octombrie): ziua 08:00–18:30, noaptea 19:00–07:00.
FERESTRE = {"zi": (time(8, 0), time(18, 30)), "noapte": (time(19, 0), time(7, 0))}
# Peste atât, placa e folosită de altcineva (Windows și ecranul țin ~600 MB).
MEMORIE_OCUPATA_MB = 2000
INCARCARE_OCUPATA = 30
# Programe care rulează mereu și nu folosesc placa (CONTINUUM doar observă, interfața merge pe procesor).
USOARE = ("module.continuum.bucla", "module.interfata", "unelte/cascada.py", "unelte\\cascada.py",
          "urmareste_placa.py")


def fereastra(acum: datetime) -> tuple[str | None, int]:
    """Fereastra în care e `acum` și câte minute mai are; (None, minute până la următoarea) în afara lor."""
    for nume, (inceput, sfarsit) in FERESTRE.items():
        start = datetime.combine(acum.date(), inceput)
        stop = datetime.combine(acum.date(), sfarsit)
        if sfarsit < inceput:  # noaptea trece de miezul nopții
            if acum.time() < sfarsit:
                start -= timedelta(days=1)
            else:
                stop += timedelta(days=1)
        if start <= acum < stop:
            return nume, int((stop - acum).total_seconds() // 60)
    urmatoarele = []
    for inceput, _ in FERESTRE.values():
        start = datetime.combine(acum.date(), inceput)
        if start <= acum:
            start += timedelta(days=1)
        urmatoarele.append(start)
    return None, int((min(urmatoarele) - acum).total_seconds() // 60)


def placa() -> dict | None:
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=temperature.gpu,memory.used,memory.total,utilization.gpu",
                            "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=30)
        t, m, total, u = (int(x) for x in r.stdout.strip().split(","))
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None
    return {"temperatura": t, "memorie_mb": m, "memorie_totala_mb": total, "incarcare": u,
            "ocupata": m > MEMORIE_OCUPATA_MB or u > INCARCARE_OCUPATA}


def procese_python() -> list[dict]:
    if os.name != "nt":
        return []
    comanda = ("Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
               "ForEach-Object { \"$($_.ProcessId)`t$($_.CommandLine)\" }")
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command", comanda], capture_output=True, text=True,
                           timeout=60, encoding="utf-8", errors="replace")
    except (OSError, subprocess.TimeoutExpired):
        return []
    procese = []
    for rand in r.stdout.splitlines():
        pid, _, linie = rand.partition("\t")
        if pid.strip().isdigit():
            procese.append({"pid": int(pid), "comanda": linie.strip()})
    return procese


def grele(procese: list[dict]) -> list[dict]:
    """Procesele care pot ține placa: tot ce nu e în USOARE. Pe Windows, venv-ul pornește câte două python.exe
    pentru aceeași comandă; le numărăm o dată."""
    vazute, rezultat = set(), []
    for p in procese:
        if not p["comanda"] or any(u in p["comanda"] for u in USOARE):
            continue
        cheie = p["comanda"].split("python.exe", 1)[-1]
        if cheie not in vazute:
            vazute.add(cheie)
            rezultat.append(p)
    return rezultat


def traieste(pid: int) -> bool:
    if os.name == "nt":
        r = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"], capture_output=True, text=True)
        return str(pid) in r.stdout
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def sarcina(nume: str, dosar: Path = DOSAR) -> dict | None:
    cale = dosar / f"{nume}.json"
    if not cale.exists():
        return None
    s = json.loads(cale.read_text(encoding="utf-8"))
    if "cod" in s:
        s["merge"] = False
    else:
        s["merge"] = traieste(s["pid"])
        if not s["merge"]:
            s["cod"] = None  # s-a oprit fără să-și scrie codul (calculatorul repornit, proces omorât)
    jurnal = dosar / f"{nume}.log"
    s["ultimele_randuri"] = (jurnal.read_text(encoding="utf-8", errors="replace").splitlines()[-15:]
                             if jurnal.exists() else [])
    return s


def pornite(dosar: Path = DOSAR) -> list[dict]:
    return [s for s in (sarcina(c.stem, dosar) for c in sorted(dosar.glob("*.json"))) if s] if dosar.exists() else []


def muta_vechea(nume: str, dosar: Path = DOSAR) -> bool:
    """Mută <nume>.json și <nume>.log ale unei sarcini terminate în <nume>_<HHMM>.* (ora pornirii), ca să poată
    porni din nou (S9, 21 octombrie). Nu șterge nimic; dacă sarcina încă merge, nu mută și întoarce False."""
    s = sarcina(nume, dosar)
    if s is None:
        return True
    if s["merge"]:
        print(f"{nume} încă merge (procesul {s['pid']}); nu o pornesc din nou.")
        return False
    try:
        ora = datetime.fromisoformat(s["pornita"]).strftime("%H%M")
    except (KeyError, TypeError, ValueError):
        ora = "vechi"
    baza, n = f"{nume}_{ora}", 1
    while any((dosar / f"{baza if n == 1 else f'{baza}_{n}'}{ext}").exists() for ext in (".json", ".log")):
        n += 1
    nou = baza if n == 1 else f"{baza}_{n}"
    for ext in (".json", ".log"):
        vechi = dosar / f"{nume}{ext}"
        if vechi.exists():
            vechi.rename(dosar / f"{nou}{ext}")
            print(f"Am mutat {vechi.name} → {nou}{ext}")
    return True


def porneste(nume: str, comanda: list[str], dosar: Path = DOSAR, din_nou: bool = False) -> int:
    """Pornește `comanda` desprinsă de executant (supraviețuiește după ce Claude Code iese). Cu `din_nou`, o
    pornire veche terminată e mutată deoparte întâi (`muta_vechea`)."""
    dosar.mkdir(parents=True, exist_ok=True)
    stare = dosar / f"{nume}.json"
    if stare.exists() and din_nou and not muta_vechea(nume, dosar):
        return 1
    if stare.exists():
        print(f"{nume} a mai fost pornită ({stare}); nu o pornesc a doua oară.")
        return 1
    stare.write_text(json.dumps({"sarcina": nume, "comanda": comanda, "pornita": datetime.now().isoformat(timespec="seconds"),
                                 "pid": 0}, ensure_ascii=False, indent=1), encoding="utf-8")
    fanioane = 0
    if os.name == "nt":
        fanioane = (subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW
                    | subprocess.CREATE_BREAKAWAY_FROM_JOB)
    argumente = [sys.executable, "-X", "utf8", str(Path(__file__).resolve()), "ruleaza", nume, "--dosar", str(dosar),
                 "--", *comanda]
    try:
        p = subprocess.Popen(argumente, cwd=RADACINA, creationflags=fanioane, stdin=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)
    except OSError:  # sarcina Windows nu lasă procesul să iasă din grupul ei: pornesc fără asta
        p = subprocess.Popen(argumente, cwd=RADACINA, creationflags=fanioane & ~getattr(subprocess, "CREATE_BREAKAWAY_FROM_JOB", 0),
                             stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)
    s = json.loads(stare.read_text(encoding="utf-8"))
    s["pid"] = p.pid
    stare.write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Am pornit {nume} (procesul {p.pid}): {' '.join(comanda)}")
    print(f"Jurnalul: {dosar / f'{nume}.log'}")
    return 0


def programul(comanda: list[str]) -> list[str]:
    """Pe Windows, „.venv/Scripts/python” (cale relativă, cu /) nu se găsește singur: îl caut în proiect;
    „python” e Python-ul proiectului."""
    primul = comanda[0]
    if primul in ("python", "python.exe"):
        return [sys.executable, *comanda[1:]]
    for cale in (RADACINA / primul, RADACINA / f"{primul}.exe"):
        if not Path(primul).is_absolute() and cale.is_file():
            return [str(cale), *comanda[1:]]
    return comanda


def ruleaza(nume: str, comanda: list[str], dosar: Path = DOSAR) -> int:
    """Rulează comanda până la capăt (în procesul desprins) și scrie codul cu care s-a încheiat."""
    jurnal = dosar / f"{nume}.log"
    with jurnal.open("a", encoding="utf-8") as f:
        f.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Pornesc: {' '.join(comanda)}\n")
        f.flush()
        try:
            cod = subprocess.call(programul(comanda), cwd=RADACINA, stdout=f, stderr=subprocess.STDOUT,
                                  stdin=subprocess.DEVNULL)
        except OSError as e:  # programul nu există: se vede în jurnal, nu moare în tăcere
            f.write(f"Nu pot porni comanda: {e}\n")
            cod = 127
        f.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] S-a încheiat (cod {cod}).\n")
    stare = dosar / f"{nume}.json"
    s = json.loads(stare.read_text(encoding="utf-8"))
    s.update(cod=cod, terminata=datetime.now().isoformat(timespec="seconds"))
    stare.write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding="utf-8")
    return cod


def stare(acum: datetime | None = None, dosar: Path = DOSAR) -> dict:
    acum = acum or datetime.now()
    nume, minute = fereastra(acum)
    p = placa()
    greu = grele(procese_python())
    ale_mele = pornite(dosar)
    return {"acum": acum.isoformat(timespec="minutes"), "fereastra": nume,
            "minute_ramase" if nume else "minute_pana_la_fereastra": minute, "placa": p, "procese_grele": greu,
            "sarcini_pornite": [{k: s[k] for k in ("sarcina", "pid", "pornita", "merge") if k in s} | {"cod": s.get("cod")}
                                for s in ale_mele],
            "liber": not (p and p["ocupata"]) and not greu and not any(s["merge"] for s in ale_mele)}


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    argv = sys.argv[1:] if argv is None else argv
    comanda: list[str] = []
    if "--" in argv:
        i = argv.index("--")
        argv, comanda = argv[:i], argv[i + 1:]
    parser = argparse.ArgumentParser(description="Ajutorul executantului din cascadă.")
    sub = parser.add_subparsers(dest="ce", required=True)
    sub.add_parser("stare").add_argument("--dosar", type=Path, default=DOSAR)
    for ce in ("porneste", "ruleaza", "sarcina"):
        p = sub.add_parser(ce)
        p.add_argument("nume")
        p.add_argument("--dosar", type=Path, default=DOSAR)
        if ce == "porneste":
            p.add_argument("--din-nou", action="store_true",
                           help="dacă a mai fost pornită și s-a terminat, mută fișierele vechi deoparte și pornește")
    args = parser.parse_args(argv)
    if args.ce == "stare":
        print(json.dumps(stare(dosar=args.dosar), ensure_ascii=False, indent=1))
        return 0
    if args.ce == "sarcina":
        s = sarcina(args.nume, args.dosar)
        print(json.dumps(s, ensure_ascii=False, indent=1) if s else f"{args.nume} n-a fost pornită de cascadă.")
        return 0
    if not comanda:
        parser.error("după „--” vine comanda de pornit")
    if args.ce == "porneste":
        return porneste(args.nume, comanda, args.dosar, din_nou=args.din_nou)
    return ruleaza(args.nume, comanda, args.dosar)


if __name__ == "__main__":
    sys.exit(main())
