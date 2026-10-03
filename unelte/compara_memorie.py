"""Comparația cinstită: același GPT, cu și fără memoria ierarhică.

Rulează aceeași rețetă de mai multe ori (cu „semințe” diferite, adică alt
noroc la pornire), o dată fără memorie și o dată cu memorie. Totul trece
prin Kronos: același examen, aceleași 5 minute, paznicul veghează, iar
fiecare experiment intră în jurnal.

    python unelte/compara_memorie.py                    # 3 perechi, ~35 de minute
    python unelte/compara_memorie.py --perechi 1        # test rapid, ~12 minute
    python unelte/compara_memorie.py --buget 20         # probă de câteva secunde

Rezultatul se salvează și în lucru/comparatie_memorie.json.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

RADACINA = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RADACINA))

from kronos.config import citeste_config  # noqa: E402
from kronos.contracte import Propunere  # noqa: E402
from kronos.orchestrator import Orchestrator  # noqa: E402

SEMINTE = [1337, 2024, 7]


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="config/laptop_gpt_memorie.toml")
    parser.add_argument("--perechi", type=int, default=3, help="câte perechi (fără / cu memorie)")
    parser.add_argument("--buget", type=float, default=None, help="secunde de antrenare (implicit: din configurare)")
    args = parser.parse_args(argv)

    config = citeste_config(args.config)
    config.nume = config.nume + "_comparatie"
    if args.buget is not None:
        config.buget_antrenare_secunde = args.buget
    orchestrator = Orchestrator(config)
    scor = orchestrator.examen.scor_principal

    rezultate: dict[str, list[float]] = {"fara": [], "cu": []}
    detalii = []
    for samanta in SEMINTE[: args.perechi]:
        for varianta, memorie in (("fara", False), ("cu", True)):
            if orchestrator._opreste():  # butonul de oprire și pauzele de răcire
                print("Comparația a fost oprită înainte de final.")
                return 1
            fisa = orchestrator.experiment(
                Propunere(f"comparație: {varianta} memorie, sămânța {samanta}",
                          {"model": {"memorie": memorie, "samanta": samanta}})
            )
            if fisa["decizie"] == "anulat":
                print(f"Experimentul a fost anulat: {fisa.get('motiv')}")
                return 1
            rezultate[varianta].append(fisa["scoruri"][scor])
            stat = fisa.get("statistici_antrenare", {})
            detalii.append({
                "varianta": varianta, "samanta": samanta, "scor": fisa["scoruri"][scor],
                "pasi": stat.get("pasi"), "parametri": stat.get("parametri"),
                "parametri_memorie": stat.get("parametri_memorie"), "experiment": fisa["id"],
            })

    medie_fara, medie_cu = statistics.mean(rezultate["fara"]), statistics.mean(rezultate["cu"])
    diferente = [f - c for f, c in zip(rezultate["fara"], rezultate["cu"])]
    castig = statistics.mean(diferente)
    print("\n=== Rezultatul comparației (val_bpb, mai mic = mai bine) ===")
    print(f"{'sămânța':>8}  {'fără memorie':>12}  {'cu memorie':>10}  {'câștig':>8}")
    for s, f, c in zip(SEMINTE, rezultate["fara"], rezultate["cu"]):
        print(f"{s:>8}  {f:>12.4f}  {c:>10.4f}  {f - c:>+8.4f}")
    print(f"{'media':>8}  {medie_fara:>12.4f}  {medie_cu:>10.4f}  {castig:>+8.4f}")

    if len(diferente) >= 2:
        abatere = statistics.stdev(diferente)
        if all(d > 0 for d in diferente) and castig > config.prag_zgomot:
            verdict = "Memoria AJUTĂ: a fost mai bună de fiecare dată, peste pragul de zgomot."
        elif all(d < 0 for d in diferente):
            verdict = "Memoria a fost mai SLABĂ de fiecare dată."
        else:
            verdict = f"NEHOTĂRÂT: diferențele schimbă semnul sau sunt mici (abatere {abatere:.4f})."
    else:
        verdict = "O singură pereche nu ajunge pentru o concluzie; rulează cu --perechi 3."
    print(f"\n{verdict}")
    print(f"Acoperirea memoriei (cuvinte găsite în bibliotecă): {orchestrator.memorie.statistici().get('acoperire', 0):.0%}")

    iesire = config.director_lucru / "comparatie_memorie.json"
    iesire.write_text(json.dumps({
        "configurare": str(args.config), "buget_secunde": config.buget_antrenare_secunde,
        "medie_fara": medie_fara, "medie_cu": medie_cu, "castig_mediu": castig,
        "verdict": verdict, "detalii": detalii,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Salvat în {iesire}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
