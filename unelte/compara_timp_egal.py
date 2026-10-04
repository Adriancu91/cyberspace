"""Comparația la timp egal (Etapa M3): GPT simplu / plasa adaptivă, câte 5 minute de antrenare fiecare.

La pași fixați, plasa adaptivă a ieșit în medie puțin mai bună, dar face ~100 de pași pe secundă, iar GPT-ul simplu
~145. Aici fiecare primește același timp (--minute, implicit 5), fără limită de pași: GPT-ul apucă mai mulți pași, plasa
mai puțini, dar mai „bogați”. Pregătirea plasei (memoria pe tot textul de antrenare) intră în timpul ei.

Pentru fiecare sămânță, câte un experiment prin Kronos din fiecare variantă, pe toată validarea; plasa adaptivă pornește
goală, ca în runda 1. Câți pași apucă fiecare depinde și de cât de caldă e placa: înainte de fiecare rulare, pauză și
răcire, iar temperatura de la start intră în rezultat. Verdictul compară scorurile (plasa adaptivă − GPT simplu), sămânță
cu sămânță, cu pragul de zgomot din configurare.

    python unelte/compara_timp_egal.py                              # semințele 0, 1, 2; 5 minute fiecare; ~40 de minute
    python unelte/compara_timp_egal.py --seminte 0 --minute 0.5     # probă rapidă

Rezultatul apare pe ecran și în lucru/timp_egal_m3_<data>.json.
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

from unelte.compara_plasa_adaptiva import CONFIGURARI, NUME, SEMINTE, citeste_configurari, ruleaza  # noqa: E402

VARIANTE = ("simplu", "adaptiva")


def verdict(randuri: list[dict[str, Any]], prag: float) -> str:
    """Cinstit: la timp egal, pașii diferă prin construcție; contează doar scorul, cu pragul de zgomot."""
    diferente = [r["adaptiva"]["scor"] - r["simplu"]["scor"] for r in randuri]  # negativ = plasa adaptivă e mai bună
    medie = statistics.mean(diferente)
    text = f"diferență medie {medie:+.4f}, pe semințe: {', '.join(f'{d:+.4f}' for d in diferente)}"
    if all(d < -prag for d in diferente):
        return f"MARE (merge): la același timp, plasa adaptivă e mai bună la fiecare sămânță, peste pragul {prag} ({text})."
    if all(d > prag for d in diferente):
        return f"MARE, dar în rău: la același timp, GPT-ul simplu e mai bun la fiecare sămânță, peste pragul {prag} ({text})."
    if abs(medie) <= prag:
        return f"MICĂ (noroc): diferența e sub pragul de zgomot {prag} ({text})."
    return f"NECONCLUDENT: diferența nu are același semn la toate semințele ({text})."


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="GPT simplu / plasa adaptivă, la același timp de antrenare.")
    for varianta in VARIANTE:
        parser.add_argument(f"--config-{varianta}", default=CONFIGURARI[varianta], help=f"configurarea: {NUME[varianta]}")
    parser.add_argument("--seminte", type=int, nargs="+", default=SEMINTE, help="câte o rulare din fiecare variantă")
    parser.add_argument("--minute", type=float, default=5, help="timpul de antrenare al fiecărei rulări, în minute")
    parser.add_argument("--pauza", type=float, default=30, help="pauza dintre rulări, în secunde")
    parser.add_argument("--racire", type=float, default=70, help="înainte de fiecare rulare, aștept placa până la atâtea grade")
    args = parser.parse_args(argv)
    if args.minute <= 0:
        parser.error("--minute trebuie să fie pozitiv")

    configurari, _, diferite = citeste_configurari({v: getattr(args, f"config_{v}") for v in VARIANTE})
    if diferite:
        print(f"Rețetele nu sunt la fel ({', '.join(diferite)}): comparația n-ar fi cinstită. Nu pornesc.", flush=True)
        return 1
    for config in configurari.values():
        config.buget_antrenare_secunde = args.minute * 60  # același timp pentru toți; limita paznicului rămâne deasupra
        if config.buget_antrenare_secunde >= float(config.paznic.get("timp_max_secunde", 600)):
            print("Timpul cerut trece de limita paznicului (timp_max_secunde). Nu pornesc.", flush=True)
            return 1
    prag = configurari["adaptiva"].prag_zgomot
    eticheta = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"Timp egal: semințele {args.seminte}, câte {args.minute:g} minute de antrenare; variante: "
          f"{', '.join(NUME[v] for v in VARIANTE)}.", flush=True)

    randuri: list[dict[str, Any]] = []
    prima = True
    for samanta in args.seminte:
        rand: dict[str, Any] = {"samanta": samanta}
        for varianta in VARIANTE:
            config = configurari[varianta]
            modificari: dict[str, Any] = {"samanta": samanta, "pasi_max": 0}  # fără limită de pași: doar timpul
            if varianta == "adaptiva":  # plasa pornește goală, în fișierul ei
                modificari["cale_plasa"] = str(config.director_lucru / "plase" / f"m3_timp_{eticheta}_s{samanta}.json")
            rulare = ruleaza(
                config, f"{config.nume}_timp_{eticheta}_s{samanta}",
                f"{NUME[varianta]}, {args.minute:g} minute, sămânța {samanta}", modificari,
                pauza=0 if prima else args.pauza, racire=args.racire,
            )
            prima = False
            if rulare is None:
                return 1
            rand[varianta] = rulare
            temperatura = rulare["temperatura_la_start"]
            print(f"   sămânța {samanta}, {NUME[varianta]}: val_bpb {rulare['scor']:.4f}, {rulare['pasi']:,} de pași "
                  f"({rulare['pasi_pe_secunda']} pași/s; placa la start: {temperatura if temperatura is not None else '?'}°C)",
                  flush=True)
        randuri.append(rand)

    print(f"\n=== Timp egal (val_bpb, mai mic = mai bine; {args.minute:g} minute de antrenare fiecare) ===")
    print(f"{'sămânța':>7}  {'pași simplu':>11}  {'scor simplu':>11}  {'pași adaptivă':>13}  {'scor adaptivă':>13}  {'adaptivă − simplu':>17}")
    for r in randuri:
        print(f"{r['samanta']:>7}  {r['simplu']['pasi']:>11,}  {r['simplu']['scor']:>11.4f}  {r['adaptiva']['pasi']:>13,}  "
              f"{r['adaptiva']['scor']:>13.4f}  {r['adaptiva']['scor'] - r['simplu']['scor']:>+17.4f}")
    concluzie = verdict(randuri, prag)
    print(f"\nVerdict: {concluzie}")

    iesire = configurari["adaptiva"].director_lucru / f"timp_egal_m3_{eticheta}.json"
    iesire.parent.mkdir(parents=True, exist_ok=True)
    iesire.write_text(
        json.dumps(
            {"data": datetime.now().isoformat(timespec="seconds"), "minute": args.minute, "prag_zgomot": prag,
             "configurari": {v: str(getattr(args, f"config_{v}")) for v in VARIANTE}, "randuri": randuri,
             "verdict": concluzie},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Salvat în {iesire}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
