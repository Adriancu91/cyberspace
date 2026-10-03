"""Comparația cinstită: aceeași rețetă GPT, cu și fără memoria ierarhică (Etapa M1).

Pentru fiecare sămânță (alt „noroc” la pornire) rulează prin Kronos două experimente,
unul fără memorie și unul cu memorie: același examen, același buget de timp, paznicul
veghează (pauze de răcire, butonul de oprire), iar fiecare experiment intră în jurnal,
pe linia „<nume>_comparatie”. Ordinea alternează de la o sămânță la alta, ca o placă
video mai caldă să nu dezavantajeze mereu aceeași variantă.

    python unelte/compara_memorie.py                     # 3 semințe, ~35-45 de minute
    python unelte/compara_memorie.py --seminte 1337      # o singură pereche, ~12 minute
    python unelte/compara_memorie.py --buget 20          # probă rapidă: 20 s de antrenare

Rezultatul (tabel + verdict) apare pe ecran și în lucru/comparatie_memorie.json.
"""

from __future__ import annotations

import argparse
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

SEMINTE = [1337, 2024, 7]


def verdict(diferente: list[float], prag: float) -> str:
    """diferente = scor fără memorie − scor cu memorie: pozitiv înseamnă că memoria ajută."""
    if len(diferente) < 2:
        return "O singură pereche nu ajunge pentru o concluzie; rulează cu cel puțin 2 semințe."
    if all(d > prag for d in diferente):
        return f"Memoria AJUTĂ: a fost mai bună la fiecare sămânță, peste pragul de zgomot ({prag})."
    if all(d < -prag for d in diferente):
        return f"Memoria STRICĂ: a fost mai slabă la fiecare sămânță, peste pragul de zgomot ({prag})."
    return (
        f"NEHOTĂRÂT: diferențele sunt sub pragul de zgomot ({prag}) "
        "sau nu merg în aceeași direcție la toate semințele."
    )


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Compară aceeași rețetă GPT cu și fără memoria ierarhică.")
    parser.add_argument("--config", default="config/laptop_gpt_memorie.toml", help="fișierul de configurare")
    parser.add_argument("--seminte", type=int, nargs="+", default=SEMINTE, help="câte o pereche pentru fiecare sămânță")
    parser.add_argument("--buget", type=float, default=None, help="secunde de antrenare (implicit: din configurare)")
    args = parser.parse_args(argv)

    config = citeste_config(args.config)
    config.nume += "_comparatie"  # linie separată în jurnal: nu se amestecă cu bucla obișnuită
    if args.buget is not None:
        config.buget_antrenare_secunde = args.buget
    reteta = config.setari_port("model")  # aceeași rețetă pentru ambele variante, luată din configurare
    o = Orchestrator(config)
    scor = o.examen.scor_principal
    print(
        f"Comparație „{config.nume}”: {len(args.seminte)} semințe × 2 variante, "
        f"câte {config.buget_antrenare_secunde:.0f} s de antrenare.\nRețeta: {reteta}",
        flush=True,
    )

    perechi: list[dict[str, Any]] = []
    for nr, samanta in enumerate(args.seminte):
        pereche: dict[str, Any] = {"samanta": samanta}
        for cu_memorie in ([False, True] if nr % 2 == 0 else [True, False]):
            if o._opreste():  # butonul de oprire și pauzele de răcire, exact ca în bucla obișnuită
                print("Comparația s-a oprit înainte de final (motivul e scris mai sus).", flush=True)
                return 1
            o.setari_curente = {"model": dict(reteta)}  # mereu rețeta din configurare, nu „cel mai bun” din jurnal
            fisa = o.experiment(
                Propunere(
                    f"comparație: {'cu' if cu_memorie else 'fără'} memorie, sămânța {samanta}",
                    {"model": {"memorie": cu_memorie, "samanta": samanta}},
                )
            )
            if fisa["decizie"] == "anulat":
                print(f"Experimentul #{fisa['id']} a fost anulat: {fisa.get('motiv')}", flush=True)
                return 1
            statistici = fisa.get("statistici_antrenare") or {}
            pereche["cu" if cu_memorie else "fara"] = {
                "experiment": fisa["id"],
                "scor": fisa["scoruri"][scor],
                "pasi": statistici.get("pasi"),
                "parametri": statistici.get("parametri"),
                "parametri_memorie": statistici.get("parametri_memorie", 0),
                "acoperire_memorie": statistici.get("acoperire_memorie"),
                "memorie_gpu_mb": (fisa.get("consum") or {}).get("memorie_gpu_max_mb"),
            }
        pereche["castig"] = pereche["fara"]["scor"] - pereche["cu"]["scor"]
        perechi.append(pereche)

    diferente = [p["castig"] for p in perechi]
    medie_fara = statistics.mean(p["fara"]["scor"] for p in perechi)
    medie_cu = statistics.mean(p["cu"]["scor"] for p in perechi)
    abatere = statistics.stdev(diferente) if len(diferente) >= 2 else None
    concluzie = verdict(diferente, config.prag_zgomot)

    print(f"\n=== Rezultatul comparației ({scor}, mai mic = mai bine) ===")
    print(f"{'sămânța':>8}  {'fără memorie':>12}  {'cu memorie':>10}  {'câștig':>8}  {'pași fără / cu':>17}")
    for p in perechi:
        pasi = f"{p['fara']['pasi'] or 0:,} / {p['cu']['pasi'] or 0:,}"
        print(f"{p['samanta']:>8}  {p['fara']['scor']:>12.4f}  {p['cu']['scor']:>10.4f}  {p['castig']:>+8.4f}  {pasi:>17}")
    print(f"{'media':>8}  {medie_fara:>12.4f}  {medie_cu:>10.4f}  {medie_fara - medie_cu:>+8.4f}")
    if abatere is not None:
        print(f"Abaterea câștigului de la o sămânță la alta: {abatere:.4f}")
    ultima = perechi[-1]
    print(
        f"Parametri: fără memorie {ultima['fara']['parametri'] or 0:,}; cu memorie {ultima['cu']['parametri'] or 0:,} "
        f"(din care memoria: {ultima['cu']['parametri_memorie'] or 0:,})"
    )
    if ultima["cu"]["acoperire_memorie"] is not None:
        print(f"Cuvinte găsite în bibliotecă: {ultima['cu']['acoperire_memorie']:.0%}")
    print(f"\nVerdict: {concluzie}")

    iesire = config.director_lucru / "comparatie_memorie.json"
    iesire.write_text(
        json.dumps(
            {
                "data": datetime.now().isoformat(timespec="seconds"),
                "configurare": str(args.config),
                "linie_jurnal": config.nume,
                "buget_secunde": config.buget_antrenare_secunde,
                "reteta": reteta,
                "perechi": perechi,
                "medie_fara": medie_fara,
                "medie_cu": medie_cu,
                "abatere_castig": abatere,
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
