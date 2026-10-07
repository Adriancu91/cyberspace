"""Lanțul de antrenare (7 octombrie 2026): antrenarea pe fapte, apoi a cincea antrenare lungă, din cel mai bun model
după fapte, fără ca cineva să aștepte între ele. Nu schimbă kronos/ și nici uneltele: le pornește pe rând.

1. Antrenarea pe fapte: unelte/antrenare_lunga.py cu config/laptop_fapte.toml (4 × 30 de minute, din #239).
2. Cel mai bun model după fapte: experimentul păstrat al liniei fapte_1 cu cele mai multe fapte_noi (criteriul
   principal; Kronos îl alege la fel). Dacă niciunul n-are fapte_noi, ultimul păstrat.
3. A cincea antrenare: unelte/antrenare_lunga.py cu config/laptop_antrenare_lunga_5.toml (5 ore), din modelul de la 2.

Înainte de fiecare etapă:
- butonul STOP (lucru/STOP) oprește lanțul;
- o etapă care iese cu eroare îl oprește și ea;
- se așteaptă (cel mult --asteptare-minute) ca placa să fie liberă: niciun alt program Python pe ea (o singură sarcină
  grea), destulă memorie liberă (limita de 5,5 GB) și temperatura sub limita paznicului.

    python unelte/lant_antrenare.py          # lanțul întreg, cu setările de azi
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parent.parent
INCEPUT_POVESTE = "Once upon a time, there was a fearful little dog named Coco"


def spune(text: str) -> None:
    print(f"[{datetime.now():%H:%M:%S}] {text}", flush=True)


def fise_din_jurnal(director_lucru: Path) -> list[dict[str, Any]]:
    fisier = director_lucru / "jurnal" / "experimente.jsonl"
    fise = []
    for rand in fisier.read_text(encoding="utf-8").splitlines() if fisier.exists() else []:
        try:
            fise.append(json.loads(rand))
        except json.JSONDecodeError:
            continue
    return fise


def cel_mai_bun_dupa_fapte(fise: list[dict[str, Any]], linie: str, criteriu: str) -> tuple[int | None, str]:
    """(experimentul, de ce): cel păstrat cu cel mai mare criteriu (ca referința lui Kronos pentru criteriul principal);
    fără criteriu în fișe, ultimul păstrat cu model salvat."""
    pastrate = [f for f in fise if f.get("linie") == linie and f.get("decizie") == "pastrat" and f.get("model_salvat")]
    cu_criteriu = [f for f in pastrate if isinstance((f.get("criterii") or {}).get(criteriu), (int, float))]
    if cu_criteriu:
        fisa = max(cu_criteriu, key=lambda f: f["criterii"][criteriu])
        return fisa["id"], f"#{fisa['id']}: {criteriu} {fisa['criterii'][criteriu]:g}, cel mai mare dintre cele păstrate"
    if pastrate:
        return pastrate[-1]["id"], f"#{pastrate[-1]['id']}: ultimul păstrat (niciunul n-are {criteriu})"
    return None, f"linia {linie} n-are niciun experiment păstrat"


def placa_libera(memorie_max_mb: float, temperatura_max: float) -> str | None:
    """None dacă placa e liberă; altfel, de ce nu."""
    if shutil.which("nvidia-smi") is None:
        return "nu găsesc nvidia-smi"
    try:
        temp, folosita, totala = (float(x) for x in subprocess.run(
            ["nvidia-smi", "--query-gpu=temperature.gpu,memory.used,memory.total", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=10, check=True).stdout.strip().splitlines()[0].split(","))
        procese = subprocess.run(["nvidia-smi", "--query-compute-apps=pid,process_name", "--format=csv,noheader"],
                                 capture_output=True, text=True, timeout=10, check=True).stdout
    except (subprocess.SubprocessError, OSError, ValueError, IndexError) as e:
        return f"nu pot citi placa ({e})"
    grele = [r.strip() for r in procese.splitlines() if "python" in r.lower()]
    if grele:
        return f"altă sarcină grea e pe placă: {'; '.join(grele)}"
    if totala - folosita < memorie_max_mb:  # antrenarea (cu profesorul, la examene) are voie până la limită
        return f"placa are deja {folosita:.0f} MB ocupați"
    if temp > temperatura_max:
        return f"placa are {temp:.0f} °C, peste {temperatura_max:.0f} °C"
    return None


def asteapta_placa(args: argparse.Namespace) -> bool:
    sfarsit = time.monotonic() + args.asteptare_minute * 60
    while True:
        if (Path(args.director_lucru) / "STOP").exists():
            spune("Butonul STOP e apăsat: lanțul se oprește.")
            return False
        motiv = placa_libera(args.memorie_max_mb, args.temperatura_max)
        if motiv is None:
            return True
        if time.monotonic() > sfarsit:
            spune(f"Placa nu s-a eliberat în {args.asteptare_minute:g} minute ({motiv}): lanțul se oprește.")
            return False
        spune(f"Aștept placa: {motiv}.")
        time.sleep(60)


def etapa(nume: str, comanda: list[str]) -> bool:
    spune(f"=== {nume} ===\n   {subprocess.list2cmdline(comanda)}")
    cod = subprocess.run(comanda, cwd=RADACINA).returncode
    spune(f"=== {nume}: gata (cod {cod}) ===")
    return cod == 0


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Fapte, apoi a cincea antrenare, din cel mai bun model după fapte.")
    parser.add_argument("--config-fapte", default="config/laptop_fapte.toml")
    parser.add_argument("--ore-fapte", type=int, default=4)
    parser.add_argument("--porneste-din", type=int, default=239)
    parser.add_argument("--linie-fapte", default="fapte_1")
    parser.add_argument("--criteriu", default="fapte_noi")
    parser.add_argument("--config-dupa", default="config/laptop_antrenare_lunga_5.toml")
    parser.add_argument("--ore-dupa", type=int, default=5)
    parser.add_argument("--director-lucru", default="lucru")
    parser.add_argument("--memorie-max-mb", type=float, default=5500)
    parser.add_argument("--temperatura-max", type=float, default=85)
    parser.add_argument("--asteptare-minute", type=float, default=30)
    args = parser.parse_args(argv)
    unealta = [sys.executable, "-u", "unelte/antrenare_lunga.py"]

    if not asteapta_placa(args):
        return 1
    if not etapa("Antrenarea pe fapte", unealta + [
            "--config", args.config_fapte, "--ore", str(args.ore_fapte), "--porneste-din", str(args.porneste_din),
            "--compara-cu", str(args.porneste_din), "--inceput", INCEPUT_POVESTE]):
        spune("Antrenarea pe fapte s-a terminat cu eroare: lanțul se oprește aici.")
        return 1
    model, de_ce = cel_mai_bun_dupa_fapte(fise_din_jurnal(Path(args.director_lucru)), args.linie_fapte, args.criteriu)
    if model is None:
        spune(f"Nu am din ce porni a cincea antrenare: {de_ce}.")
        return 1
    spune(f"Cel mai bun model după fapte: {de_ce}.")
    if not asteapta_placa(args):
        return 1
    if not etapa("A cincea antrenare lungă", unealta + [
            "--config", args.config_dupa, "--ore", str(args.ore_dupa), "--porneste-din", str(model),
            "--compara-cu", str(model), "--inceput", INCEPUT_POVESTE]):
        spune("A cincea antrenare s-a terminat cu eroare.")
        return 1
    spune("Lanțul s-a încheiat.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
