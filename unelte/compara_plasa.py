"""Testul plasei în două runde (Etapa M2, pasul 2).

Poveștile de validare se împart în două jumătăți: runda 1 și runda 2. Pentru fiecare sămânță rulează,
prin Kronos (același examen, același buget, paznicul veghează, totul în jurnal):
    fără plasă runda 1, fără plasă runda 2, cu plasă runda 1, cu plasă runda 2
Cu plasă, legăturile învățate în runda 1 se păstrează pentru runda 2 (câte un fișier de plasă pentru
fiecare sămânță, gol la început). Fiecare rundă are linia ei în jurnal, iar varianta fără plasă rulează
prima: „câștigul la examen” primit de plasă = cât a bătut-o varianta cu plasă pe cea fără, pe aceeași
jumătate de validare și cu aceeași sămânță. Plasa primește doar acest număr, nu textul.

Tabelul arată, pentru fiecare variantă, runda 2 − runda 1. Fără plasă, diferența vine doar din
jumătățile diferite de validare; cu plasă, se adaugă ce a păstrat plasa din runda 1.

    python unelte/compara_plasa.py                             # 2 semințe, 8 experimente, ~45-50 de minute
    python unelte/compara_plasa.py --seminte 1337 --buget 20   # probă rapidă

Rezultatul apare pe ecran și în lucru/comparatie_plasa_<data>.json.
"""

from __future__ import annotations

import argparse
import copy
import json
import statistics
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from kronos.config import citeste_config  # noqa: E402
from kronos.contracte import Propunere  # noqa: E402
from kronos.orchestrator import Orchestrator  # noqa: E402

SEMINTE = [1337, 2024]


def verdict(diferenta: float, prag: float, perechi: int) -> str:
    """diferenta = media(runda 2 − runda 1 cu plasă) − media(runda 2 − runda 1 fără plasă); negativ = plasa ajută."""
    if diferenta < -prag:
        concluzie = f"Plasa a AJUTAT runda 2 (cu {-diferenta:.4f} mai mult decât fără plasă)."
    elif diferenta > prag:
        concluzie = f"Plasa a ÎNCURCAT runda 2 (cu {diferenta:.4f} mai rău decât fără plasă)."
    else:
        concluzie = f"NEHOTĂRÂT: diferența ({diferenta:+.4f}) e sub pragul de zgomot ({prag})."
    if perechi < 3:
        concluzie += f" Cu doar {perechi} semințe, rezultatul e orientativ."
    return concluzie


def _rezumat_plasa(plasa: dict[str, Any] | None) -> str:
    if not plasa:
        return "-"
    return (
        f"{plasa['legaturi']} legături (născute {plasa['nascute']}, întărite {plasa['intarite']}, "
        f"slăbite {plasa['slabite']}, tăiate {plasa['taiate']}, definitive {plasa['definitive']})"
    )


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Testul plasei în două runde: fără / cu plasă.")
    parser.add_argument("--config", default="config/laptop_plasa.toml", help="fișierul de configurare")
    parser.add_argument("--seminte", type=int, nargs="+", default=SEMINTE, help="câte o serie pentru fiecare sămânță")
    parser.add_argument("--buget", type=float, default=None, help="secunde de antrenare (implicit: din configurare)")
    args = parser.parse_args(argv)

    baza = citeste_config(args.config)
    if args.buget is not None:
        baza.buget_antrenare_secunde = args.buget
    reteta = baza.setari_port("model")
    eticheta = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(
        f"Testul plasei în două runde: {len(args.seminte)} semințe × 4 experimente, "
        f"câte {baza.buget_antrenare_secunde:.0f} s de antrenare.\nRețeta: {reteta}",
        flush=True,
    )

    rezultate: list[dict[str, Any]] = []
    for samanta in args.seminte:
        cale_plasa = baza.director_lucru / "plase" / f"comparatie_{eticheta}_s{samanta}.json"  # goală la început
        for cu_plasa in (False, True):
            for runda in (1, 2):
                config = copy.deepcopy(baza)
                config.nume = f"{baza.nume}_comparatie_{eticheta}_s{samanta}_r{runda}"  # o linie pe rundă
                config.porturi["date"].setdefault("setari", {})["runda"] = runda
                o = Orchestrator(config)
                if o._opreste():  # butonul de oprire și pauzele de răcire, ca în bucla obișnuită
                    print("Testul s-a oprit înainte de final (motivul e scris mai sus).", flush=True)
                    return 1
                o.setari_curente = {"model": dict(reteta)}
                varianta = "cu plasă" if cu_plasa else "fără plasă"
                fisa = o.experiment(
                    Propunere(
                        f"{varianta}, runda {runda}, sămânța {samanta}",
                        {"model": {"plasa": cu_plasa, "samanta": samanta, "cale_plasa": str(cale_plasa)}},
                    )
                )
                if fisa["decizie"] == "anulat":
                    print(f"Experimentul #{fisa['id']} a fost anulat: {fisa.get('motiv')}", flush=True)
                    return 1
                plasa = (fisa.get("dupa_examen") or {}).get("plasa")
                rezultate.append({
                    "samanta": samanta, "plasa_pornita": cu_plasa, "runda": runda, "experiment": fisa["id"],
                    "scor": fisa["scoruri"][o.examen.scor_principal],
                    "pasi": (fisa.get("statistici_antrenare") or {}).get("pasi"),
                    "castig_primit": None if plasa is None else plasa.get("castig_primit"),
                    "plasa": plasa,
                })
                if cu_plasa:
                    print(f"      plasa după runda {runda}: {_rezumat_plasa(plasa)}", flush=True)

    def scor(samanta: int, cu_plasa: bool, runda: int) -> float:
        return next(r["scor"] for r in rezultate if (r["samanta"], r["plasa_pornita"], r["runda"]) == (samanta, cu_plasa, runda))

    print("\n=== Rezultatul (val_bpb, mai mic = mai bine) ===")
    print(f"{'varianta':<11} {'sămânța':>8}  {'runda 1':>8}  {'runda 2':>8}  {'runda 2 − runda 1':>17}")
    diferente: dict[bool, list[float]] = {False: [], True: []}
    for cu_plasa in (False, True):
        for samanta in args.seminte:
            r1, r2 = scor(samanta, cu_plasa, 1), scor(samanta, cu_plasa, 2)
            diferente[cu_plasa].append(r2 - r1)
            nume = "cu plasă" if cu_plasa else "fără plasă"
            print(f"{nume:<11} {samanta:>8}  {r1:>8.4f}  {r2:>8.4f}  {r2 - r1:>+17.4f}")
    medie_fara, medie_cu = statistics.mean(diferente[False]), statistics.mean(diferente[True])
    print(f"Media runda 2 − runda 1: fără plasă {medie_fara:+.4f}, cu plasă {medie_cu:+.4f}")
    print(f"Diferența (cu − fără): {medie_cu - medie_fara:+.4f}  (negativ = plasa a ajutat runda 2)")
    for runda in (1, 2):
        castiguri = [scor(s, False, runda) - scor(s, True, runda) for s in args.seminte]
        print(f"Runda {runda}: cu plasă față de fără plasă, câștig mediu {statistics.mean(castiguri):+.4f}")
    print("\nPlasa, după fiecare rundă cu plasă:")
    for r in rezultate:
        if r["plasa_pornita"]:
            print(f"   sămânța {r['samanta']}, runda {r['runda']}: {_rezumat_plasa(r['plasa'])}")
    concluzie = verdict(medie_cu - medie_fara, baza.prag_zgomot, len(args.seminte))
    print(f"\nVerdict: {concluzie}")

    iesire = baza.director_lucru / f"comparatie_plasa_{eticheta}.json"
    iesire.write_text(
        json.dumps(
            {
                "data": datetime.now().isoformat(timespec="seconds"),
                "configurare": str(args.config),
                "buget_secunde": baza.buget_antrenare_secunde,
                "reteta": reteta,
                "seminte": args.seminte,
                "rezultate": rezultate,
                "media_diferentei_fara_plasa": medie_fara,
                "media_diferentei_cu_plasa": medie_cu,
                "verdict": concluzie,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Salvat în {iesire}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
