"""Lanțul de antrenare: mai multe rulări ale uneltei unelte/antrenare_lunga.py, una după alta, fără ca cineva să
aștepte între ele. Nu schimbă kronos/ și nici uneltele: le pornește pe rând.

Fără --plan, lanțul din 7 octombrie 2026:
1. Antrenarea pe fapte: unelte/antrenare_lunga.py cu config/laptop_fapte.toml (4 × 30 de minute, din #239).
2. Cel mai bun model după fapte: experimentul păstrat al liniei fapte_1 cu cele mai multe fapte_noi (criteriul
   principal; Kronos îl alege la fel). Dacă niciunul n-are fapte_noi, ultimul păstrat.
3. A cincea antrenare: unelte/antrenare_lunga.py cu config/laptop_antrenare_lunga_5.toml (5 ore), din modelul de la 2.

Cu --plan (ex. config/lant_6.toml), etapele vin dintr-un fișier TOML: câte un [[etapa]] cu nume, config, ore,
porneste_din, compara_cu (implicit: porneste_din) și, opțional, nota (se scrie în jurnalul lanțului la pornirea etapei).
[lant] la_eroare spune ce se face când o etapă iese cu eroare: „opreste” (implicit) sau „continua” (când etapele nu
depind una de alta). Planul se verifică întreg înainte de prima etapă: configurările există, iar fiecare model de pornire
are un model salvat de Kronos.

Înainte de fiecare etapă:
- butonul STOP (lucru/STOP) oprește lanțul;
- o etapă care iese cu eroare îl oprește și ea;
- se așteaptă (cel mult --asteptare-minute) ca placa să fie liberă: niciun alt program Python pe ea (o singură sarcină
  grea), destulă memorie liberă (limita de 5,5 GB) și temperatura sub limita paznicului.

    python unelte/lant_antrenare.py                              # lanțul din 7 octombrie
    python unelte/lant_antrenare.py --plan config/lant_6.toml    # etapele din plan
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
import tomllib
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


def citeste_plan(cale: Path, fise: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Planul unui lanț, verificat întreg (vezi sus). Cu `fise` (jurnalul Kronos), și modelele de pornire. ValueError cu
    motivul, în română, dacă ceva nu e în regulă."""
    try:
        date = tomllib.loads(cale.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as e:
        raise ValueError(f"nu pot citi planul {cale}: {e}") from None
    la_eroare = (date.get("lant") or {}).get("la_eroare", "opreste")
    if la_eroare not in ("opreste", "continua"):
        raise ValueError("în [lant], „la_eroare” e „opreste” sau „continua”")
    etape = date.get("etapa") or []
    if not etape:
        raise ValueError("planul n-are nicio [[etapa]]")
    salvate = {f.get("id") for f in fise or [] if f.get("model_salvat")}
    rezultat = []
    for nr, e in enumerate(etape, start=1):
        lipsa = [k for k in ("nume", "config", "ore", "porneste_din") if k not in e]
        if lipsa:
            raise ValueError(f"etapa {nr}: lipsește {', '.join(lipsa)}")
        if not (RADACINA / e["config"]).exists():
            raise ValueError(f"etapa {nr}: nu există {e['config']}")
        numere = [e["ore"], e["porneste_din"], e.get("compara_cu", e["porneste_din"])]
        if any(not isinstance(x, int) or isinstance(x, bool) for x in numere) or e["ore"] < 1:
            raise ValueError(f"etapa {nr}: „ore”, „porneste_din” și „compara_cu” sunt numere întregi (ore ≥ 1)")
        for cheie in ("porneste_din", "compara_cu"):
            if fise is not None and e.get(cheie, e["porneste_din"]) not in salvate:
                raise ValueError(f"etapa {nr}: #{e.get(cheie, e['porneste_din'])} n-are un model salvat de Kronos")
        rezultat.append({"nume": str(e["nume"]), "config": str(e["config"]), "ore": e["ore"],
                         "porneste_din": e["porneste_din"], "compara_cu": e.get("compara_cu", e["porneste_din"]),
                         "nota": e.get("nota")})
    return {"la_eroare": la_eroare, "etape": rezultat}


def ruleaza_plan(plan: dict[str, Any], args: argparse.Namespace, unealta: list[str]) -> int:
    """Etapele planului, pe rând: STOP și placa liberă înainte de fiecare; o etapă căzută oprește lanțul doar cu
    la_eroare = „opreste”."""
    reusite: list[bool] = []
    total = len(plan["etape"])
    for nr, e in enumerate(plan["etape"], start=1):
        if not asteapta_placa(args):
            return 1
        if e["nota"]:
            spune(f"Etapa {nr} din {total}: {e['nota']}.")
        ok = etapa(f"Etapa {nr} din {total}: {e['nume']}", unealta + [
            "--config", e["config"], "--ore", str(e["ore"]), "--porneste-din", str(e["porneste_din"]),
            "--compara-cu", str(e["compara_cu"]), "--inceput", INCEPUT_POVESTE])
        reusite.append(ok)
        if not ok and plan["la_eroare"] == "opreste":
            spune(f"Etapa {nr} s-a terminat cu eroare: lanțul se oprește aici.")
            return 1
        if not ok:
            spune(f"Etapa {nr} s-a terminat cu eroare; etapele nu depind una de alta, deci merg mai departe.")
    spune(f"Lanțul s-a încheiat: {sum(reusite)} din {total} etape reușite.")
    return 0 if all(reusite) else 1


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
    parser = argparse.ArgumentParser(description="Antrenări lungi una după alta: un plan, sau fapte și apoi a cincea.")
    parser.add_argument("--plan", default=None, help="un plan TOML cu etapele (ex. config/lant_6.toml)")
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

    if args.plan:
        try:
            plan = citeste_plan(RADACINA / args.plan, fise_din_jurnal(Path(args.director_lucru)))
        except ValueError as e:
            spune(f"Planul nu e în regulă: {e}. Nu pornesc nimic.")
            return 1
        spune(f"Planul {args.plan}: {len(plan['etape'])} etape; la o eroare: {plan['la_eroare']}.")
        return ruleaza_plan(plan, args, unealta)

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
