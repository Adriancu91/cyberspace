"""Rata care scade singură, față de rata fixă: aceeași rețetă, de la zero, la timp egal (pasul 1 după prima buclă).

Rețeta e cea din config/laptop_bucla.toml (10 straturi × 512, context 256, lot 30; testul din 4 octombrie a folosit rata
primei bucle, 0,00035, care atunci era în configurare: azi se dă cu --rata 0.00035), de la zero, câte 5 minute de
antrenare, fără nicio stare salvată.
- „Fără”: rata fixă, ca până acum.
- „Cu”: încălzire în primii 100 de pași, apoi scădere cosinus până la 10% din rata de pornire, la finalul celor 5 minute.
Pentru fiecare sămânță, întâi „fără”, apoi „cu”, pe aceeași linie de jurnal; aceeași sămânță = aceleași greutăți de
pornire și aceleași bucăți de text. Înainte de fiecare rulare, pauză și răcire. Verdictul compară scorurile sămânță cu
sămânță, cu pragul de zgomot din configurare.

    python unelte/compara_scaderea_ratei.py                            # semințele 0 și 1, câte 5 minute; ~25 de minute
    python unelte/compara_scaderea_ratei.py --seminte 0 --minute 0.5   # probă rapidă

Cu --rata, rețeta (amândouă variantele) are altă rată. Cu --rata-cu, doar varianta cu scădere pornește de la altă rată (ex.
dublă: cosinusul până la 10% are în medie ~55% din rata de pornire, deci o rată dublă dă cam aceeași rată medie ca rata
fixă). Cu --fara-din / --cu-din, rulările unei variante se iau dintr-un rezultat de dinainte (aceleași semințe, aceleași
minute, aceeași rețetă și rată), fără să se repete.

Rezultatul apare pe ecran și în lucru/scaderea_ratei_<data>.json.
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
from unelte.compara_plasa_adaptiva import ruleaza  # noqa: E402

VARIANTE = ("fara", "cu")
NUME = {"fara": "rata fixă", "cu": "rata care scade"}


def verdict(randuri: list[dict[str, Any]], prag: float) -> str:
    """Cinstit: aceeași rețetă și același timp; contează doar scorul, sămânță cu sămânță, cu pragul de zgomot."""
    diferente = [r["cu"]["scor"] - r["fara"]["scor"] for r in randuri]  # negativ = scăderea ajută
    medie = statistics.mean(diferente)
    text = f"diferență medie {medie:+.4f}, pe semințe: {', '.join(f'{d:+.4f}' for d in diferente)}"
    if all(d < -prag for d in diferente):
        return f"AJUTĂ: cu rata care scade, scorul e mai bun la fiecare sămânță, peste pragul {prag} ({text})."
    if all(d > prag for d in diferente):
        return f"STRICĂ: cu rata care scade, scorul e mai slab la fiecare sămânță, peste pragul {prag} ({text})."
    if abs(medie) <= prag:
        return f"NU CONTEAZĂ: diferența e sub pragul de zgomot {prag} ({text})."
    return f"NECONCLUDENT: diferența nu are același semn la toate semințele ({text})."


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Rata care scade singură, față de rata fixă: aceeași rețetă, de la zero.")
    parser.add_argument("--config", default="config/laptop_bucla.toml", help="configurarea cu rețeta")
    parser.add_argument("--seminte", type=int, nargs="+", default=[0, 1], help="câte o rulare din fiecare variantă")
    parser.add_argument("--minute", type=float, default=5, help="timpul de antrenare al fiecărei rulări, în minute")
    parser.add_argument("--pauza", type=float, default=30, help="pauza dintre rulări, în secunde")
    parser.add_argument("--racire", type=float, default=70, help="înainte de fiecare rulare, aștept placa până la atâtea grade")
    parser.add_argument("--rata", type=float, default=None, help="rata rețetei, pentru amândouă variantele (implicit: din configurare)")
    parser.add_argument("--rata-cu", type=float, default=None, help="rata de pornire a variantei cu scădere (implicit: a rețetei)")
    parser.add_argument("--fara-din", default="", help="rulările cu rata fixă, dintr-un rezultat de dinainte (fișierul .json)")
    parser.add_argument("--cu-din", default="", help="rulările cu rata care scade, dintr-un rezultat de dinainte (fișierul .json)")
    args = parser.parse_args(argv)
    if args.minute <= 0:
        parser.error("--minute trebuie să fie pozitiv")

    config = citeste_config(args.config)
    rata = {"fara": args.rata if args.rata is not None else config.setari_port("model")["rata_invatare"]}
    rata["cu"] = args.rata_cu if args.rata_cu is not None else rata["fara"]
    vechi: dict[str, dict[int, dict[str, Any]]] = {"fara": {}, "cu": {}}
    for varianta, fisier in (("fara", args.fara_din), ("cu", args.cu_din)):
        if not fisier:
            continue
        rezultat = json.loads(Path(fisier).read_text(encoding="utf-8"))
        rata_veche = rezultat.get(f"rata_{varianta}", rezultat["reteta"]["rata_invatare"])
        if rezultat["minute"] != args.minute or rezultat["reteta"] != config.setari_port("model") or rata_veche != rata[varianta]:
            print(f"Rezultatul din --{varianta}-din are alt timp, altă rețetă sau altă rată: comparația n-ar fi cinstită. "
                  "Nu pornesc.", flush=True)
            return 1
        vechi[varianta] = {r["samanta"]: r[varianta] for r in rezultat["randuri"]}
    config.buget_antrenare_secunde = args.minute * 60  # același timp pentru amândouă; limita paznicului rămâne deasupra
    if config.buget_antrenare_secunde >= float(config.paznic.get("timp_max_secunde", 600)):
        print("Timpul cerut trece de limita paznicului (timp_max_secunde). Nu pornesc.", flush=True)
        return 1
    reteta = config.setari_port("model")
    prag = config.prag_zgomot
    eticheta = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"Rata care scade, față de rata fixă: semințele {args.seminte}, câte {args.minute:g} minute de la zero; rețeta "
          f"{reteta['n_straturi']}×{reteta['n_emb']}, context {reteta['context']}, lot {reteta['lot']}; "
          f"rata fixă {rata['fara']:g}, rata care scade pornește de la {rata['cu']:g}.", flush=True)

    randuri: list[dict[str, Any]] = []
    prima = True
    for samanta in args.seminte:
        rand: dict[str, Any] = {"samanta": samanta}
        for varianta in VARIANTE:
            if samanta in vechi[varianta]:
                rand[varianta] = vechi[varianta][samanta]
                sursa = args.fara_din if varianta == "fara" else args.cu_din
                print(f"   sămânța {samanta}, {NUME[varianta]}: val_bpb {rand[varianta]['scor']:.4f} (din {sursa})", flush=True)
                continue
            # De la zero și fără stări salvate: nu atinge stările buclei.
            modificari = {"samanta": samanta, "rata_care_scade": varianta == "cu", "rata_invatare": rata[varianta],
                          "de_la_zero": True, "director_stari": "", "cale_stare": "", "pasi_max": 0}
            rulare = ruleaza(
                config, f"scaderea_ratei_{eticheta}_s{samanta}", f"{NUME[varianta]}, {args.minute:g} minute, sămânța {samanta}",
                modificari, pauza=0 if prima else args.pauza, racire=args.racire, cu_fisa=True,
            )
            prima = False
            if rulare is None:
                return 1
            statistici = rulare.pop("fisa").get("statistici_antrenare") or {}
            rulare["rata_la_final"] = statistici.get("rata_la_final")
            rulare["memorie_rezervata_mb"] = statistici.get("memorie_rezervata_mb")
            rand[varianta] = rulare
            temperatura = rulare["temperatura_la_start"]
            print(f"   sămânța {samanta}, {NUME[varianta]}: val_bpb {rulare['scor']:.4f}, {rulare['pasi']:,} de pași "
                  f"({rulare['pasi_pe_secunda']} pași/s; placa la start: {temperatura if temperatura is not None else '?'}°C)",
                  flush=True)
        randuri.append(rand)

    print(f"\n=== Rata care scade, față de rata fixă (val_bpb, mai mic = mai bine; {args.minute:g} minute de la zero) ===")
    print(f"{'sămânța':>7}  {'pași fixă':>9}  {'scor fixă':>9}  {'pași scade':>10}  {'scor scade':>10}  {'scade − fixă':>12}")
    for r in randuri:
        print(f"{r['samanta']:>7}  {r['fara']['pasi']:>9,}  {r['fara']['scor']:>9.4f}  {r['cu']['pasi']:>10,}  "
              f"{r['cu']['scor']:>10.4f}  {r['cu']['scor'] - r['fara']['scor']:>+12.4f}")
    concluzie = verdict(randuri, prag)
    print(f"\nVerdict: {concluzie}")

    iesire = config.director_lucru / f"scaderea_ratei_{eticheta}.json"
    iesire.parent.mkdir(parents=True, exist_ok=True)
    iesire.write_text(
        json.dumps(
            {"data": datetime.now().isoformat(timespec="seconds"), "minute": args.minute, "prag_zgomot": prag,
             "configurare": str(args.config), "reteta": reteta, "rata_fara": rata["fara"], "rata_cu": rata["cu"],
             "fara_din": args.fara_din or None, "cu_din": args.cu_din or None, "randuri": randuri, "verdict": concluzie},
            ensure_ascii=False, indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Salvat în {iesire}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
