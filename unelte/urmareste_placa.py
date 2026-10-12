"""Notează temperatura, memoria și încărcarea plăcii video la câteva secunde, apoi spune maximele.

Doar citește (nvidia-smi); nu pornește și nu oprește nimic. Memoria e cea a întregii plăci, cu Windows cu tot;
paznicul Kronos măsoară altfel (doar ce a cerut antrenarea de la PyTorch) și e în jurnalul Kronos.

    python unelte/urmareste_placa.py --minute 15 --iesire lucru/placa_noapte.csv
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


def citeste() -> tuple[int, int, int] | None:
    r = subprocess.run(["nvidia-smi", "--query-gpu=temperature.gpu,memory.used,utilization.gpu",
                        "--format=csv,noheader,nounits"], capture_output=True, text=True)
    try:
        t, m, u = (int(x) for x in r.stdout.strip().split(","))
    except ValueError:
        return None
    return t, m, u


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Notează temperatura și memoria plăcii video.")
    parser.add_argument("--minute", type=float, default=15)
    parser.add_argument("--la-secunde", type=float, default=5)
    parser.add_argument("--iesire", default="lucru/placa.csv")
    args = parser.parse_args(argv)
    iesire = Path(args.iesire)
    iesire.parent.mkdir(parents=True, exist_ok=True)
    masuratori: list[tuple[int, int, int]] = []
    capat = time.monotonic() + args.minute * 60
    with iesire.open("a", encoding="utf-8") as f:
        if iesire.stat().st_size == 0:
            f.write("ora,temperatura,memorie_mb,incarcare_procent\n")
        while time.monotonic() < capat:
            m = citeste()
            if m:
                masuratori.append(m)
                f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S},{m[0]},{m[1]},{m[2]}\n")
                f.flush()
            time.sleep(args.la_secunde)
    if not masuratori:
        print("Nu am putut citi placa (nvidia-smi).")
        return 1
    lucru = [m for m in masuratori if m[2] >= 50] or masuratori
    print(json.dumps({
        "masuratori": len(masuratori), "minute": args.minute,
        "temperatura_max": max(m[0] for m in masuratori), "temperatura_la_final": masuratori[-1][0],
        "memorie_max_mb_toata_placa": max(m[1] for m in masuratori),
        "incarcare_medie_cat_lucreaza": round(sum(m[2] for m in lucru) / len(lucru)),
        "masuratori_cu_placa_la_lucru": len(lucru), "fisier": iesire.as_posix(),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
