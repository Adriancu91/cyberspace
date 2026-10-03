"""Comparația cinstită: aceeași rețetă GPT, cu și fără memoria ierarhică (Etapa M1).

Pentru fiecare sămânță (alt „noroc” la pornire) rulează prin Kronos două experimente,
unul fără memorie și unul cu memorie: același examen, aceleași date, paznicul veghează
(pauze de răcire, butonul de oprire), iar fiecare experiment intră în jurnal, pe o linie
separată. Ordinea alternează de la o sămânță la alta, ca o placă video mai caldă să nu
dezavantajeze mereu aceeași variantă.

Două feluri de comparație:
- la același TIMP (implicit): fiecare variantă are aceleași secunde de antrenare;
  varianta mai lentă apucă mai puțini pași.
- la același număr de PAȘI (--pasi N): ambele variante fac exact N pași de antrenare;
  timpul devine doar o limită de siguranță. Așa se vede dacă memoria ajută „pe pas”.

    python unelte/compara_memorie.py                     # 3 semințe, la același timp, ~35-45 min
    python unelte/compara_memorie.py --pasi 35000        # 3 semințe, la același număr de pași
    python unelte/compara_memorie.py --pasi 35000 --adancime 2   # memoria folosește doar 2 niveluri
    python unelte/compara_memorie.py --seminte 1337      # o singură pereche
    python unelte/compara_memorie.py --buget 20          # probă rapidă: 20 s de antrenare

Rezultatul (tabel + verdict) apare pe ecran și în lucru/comparatie_memorie[_pasi][_adancimeN].json;
fiecare fel de comparație are fișierul și linia lui din jurnal, ca să nu se suprascrie între ele.
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
    parser.add_argument(
        "--pasi", type=int, default=None,
        help="compară la același număr de pași de antrenare; timpul devine doar o limită de siguranță",
    )
    parser.add_argument(
        "--adancime", type=int, default=None,
        help="câte niveluri din codul cuvântului folosește memoria (implicit: din configurare)",
    )
    args = parser.parse_args(argv)
    la_pasi = args.pasi is not None
    if la_pasi and args.pasi < 1:
        parser.error("--pasi trebuie să fie cel puțin 1")
    if args.adancime is not None and args.adancime < 1:
        parser.error("--adancime trebuie să fie cel puțin 1")

    config = citeste_config(args.config)
    # Linii separate în jurnal și fișiere separate, pentru fiecare fel de comparație.
    sufix = ("_pasi" if la_pasi else "") + (f"_adancime{args.adancime}" if args.adancime is not None else "")
    config.nume += "_comparatie" + sufix
    if args.adancime is not None:
        config.porturi["model"].setdefault("setari", {})["adancime_memorie"] = args.adancime
    if args.buget is not None:
        config.buget_antrenare_secunde = args.buget
    elif la_pasi:
        # Limita de siguranță: dublul bugetului obișnuit, dar sub limita paznicului (altfel experimentul ar fi anulat).
        timp_max = float(config.paznic.get("timp_max_secunde", 600))
        config.buget_antrenare_secunde = min(2 * config.buget_antrenare_secunde, 0.9 * timp_max)
    reteta = config.setari_port("model")  # aceeași rețetă pentru ambele variante, luată din configurare
    o = Orchestrator(config)
    scor = o.examen.scor_principal
    mod = (
        f"la același număr de pași: {args.pasi:,} (limită de siguranță {config.buget_antrenare_secunde:.0f} s)"
        if la_pasi
        else f"la același timp: {config.buget_antrenare_secunde:.0f} s de antrenare"
    )
    print(f"Comparație „{config.nume}”: {len(args.seminte)} semințe × 2 variante, {mod}.\nRețeta: {reteta}", flush=True)

    perechi: list[dict[str, Any]] = []
    for nr, samanta in enumerate(args.seminte):
        pereche: dict[str, Any] = {"samanta": samanta}
        for cu_memorie in ([False, True] if nr % 2 == 0 else [True, False]):
            if o._opreste():  # butonul de oprire și pauzele de răcire, exact ca în bucla obișnuită
                print("Comparația s-a oprit înainte de final (motivul e scris mai sus).", flush=True)
                return 1
            o.setari_curente = {"model": dict(reteta)}  # mereu rețeta din configurare, nu „cel mai bun” din jurnal
            modificari: dict[str, Any] = {"memorie": cu_memorie, "samanta": samanta}
            if la_pasi:
                modificari["pasi_max"] = args.pasi
            fisa = o.experiment(
                Propunere(f"comparație: {'cu' if cu_memorie else 'fără'} memorie, sămânța {samanta}", {"model": modificari})
            )
            if fisa["decizie"] == "anulat":
                print(f"Experimentul #{fisa['id']} a fost anulat: {fisa.get('motiv')}", flush=True)
                return 1
            statistici = fisa.get("statistici_antrenare") or {}
            consum = fisa.get("consum") or {}
            pereche["cu" if cu_memorie else "fara"] = {
                "experiment": fisa["id"],
                "scor": fisa["scoruri"][scor],
                "pasi": statistici.get("pasi"),
                "secunde": consum.get("durata_antrenare_secunde"),
                "parametri": statistici.get("parametri"),
                "parametri_memorie": statistici.get("parametri_memorie", 0),
                "acoperire_memorie": statistici.get("acoperire_memorie"),
                "memorie_gpu_mb": consum.get("memorie_gpu_max_mb"),
            }
        pereche["castig"] = pereche["fara"]["scor"] - pereche["cu"]["scor"]
        perechi.append(pereche)

    diferente = [p["castig"] for p in perechi]
    medie_fara = statistics.mean(p["fara"]["scor"] for p in perechi)
    medie_cu = statistics.mean(p["cu"]["scor"] for p in perechi)
    abatere = statistics.stdev(diferente) if len(diferente) >= 2 else None
    concluzie = verdict(diferente, config.prag_zgomot)
    pasi_inegali = [
        f"sămânța {p['samanta']} {'cu' if v == 'cu' else 'fără'} memorie: {p[v]['pasi'] or 0:,} pași"
        for p in perechi for v in ("fara", "cu") if la_pasi and p[v]["pasi"] != args.pasi
    ]
    if pasi_inegali:
        concluzie = (
            f"ATENȚIE: nu toate antrenările au ajuns la {args.pasi:,} pași înainte de limita de timp "
            f"({'; '.join(pasi_inegali)}), deci comparația NU e la număr egal de pași. " + concluzie
        )

    print(f"\n=== Rezultatul comparației ({scor}, mai mic = mai bine; {mod}) ===")
    print(f"{'sămânța':>8}  {'fără memorie':>12}  {'cu memorie':>10}  {'câștig':>8}  {'pași fără / cu':>17}  {'secunde fără / cu':>17}")
    for p in perechi:
        pasi = f"{p['fara']['pasi'] or 0:,} / {p['cu']['pasi'] or 0:,}"
        secunde = f"{p['fara']['secunde'] or 0:.0f} / {p['cu']['secunde'] or 0:.0f}"
        print(
            f"{p['samanta']:>8}  {p['fara']['scor']:>12.4f}  {p['cu']['scor']:>10.4f}  {p['castig']:>+8.4f}  "
            f"{pasi:>17}  {secunde:>17}"
        )
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

    iesire = config.director_lucru / f"comparatie_memorie{sufix}.json"
    iesire.write_text(
        json.dumps(
            {
                "data": datetime.now().isoformat(timespec="seconds"),
                "configurare": str(args.config),
                "linie_jurnal": config.nume,
                "mod": "pasi" if la_pasi else "timp",
                "pasi": args.pasi,
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
