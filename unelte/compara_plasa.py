"""Testul plasei în două runde, la același număr de pași (Etapa M2, pasul 2).

Poveștile de validare se împart în două jumătăți: runda 1 și runda 2. Pentru fiecare sămânță rulează,
prin Kronos (același examen, paznicul veghează, totul în jurnal):
    fără plasă runda 1, fără plasă runda 2, cu plasă runda 1, cu plasă runda 2
Fiecare rulare se oprește la EXACT același număr de pași (--pasi), nu la timp: așa antrenarea se repetă
identic, iar scorurile se pot compara. Cu plasă, legăturile din runda 1 se păstrează pentru runda 2 (câte
un fișier de plasă pentru fiecare sămânță, gol la început). Fiecare rundă are linia ei în jurnal, iar
varianta fără plasă rulează prima: „câștigul la examen” primit de plasă = cât a bătut-o varianta cu plasă
pe cea fără, pe aceeași jumătate și cu aceeași sămânță. Plasa primește doar acest număr, nu textul.

Efectul plasei, pentru o sămânță = (cu plasă R2 − R1) − (fără plasă R2 − R1): fără plasă, diferența dintre
runde vine doar din jumătățile diferite de validare; cu plasă, se adaugă ce a păstrat plasa din runda 1.
Verdictul e NECONCLUDENT dacă rulările au pași diferiți sau dacă plasa e goală la începutul rundei 2.

    python unelte/compara_plasa.py                          # semințele 0, 1, 2; 25.000 de pași; ~70 de minute
    python unelte/compara_plasa.py --seminte 0 --pasi 2000  # probă rapidă

Între rulări, placa se răcește (--racire, implicit până la 70°C). Rezultatul apare pe ecran și în
lucru/comparatie_plasa_<data>.json.
"""

from __future__ import annotations

import argparse
import copy
import json
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from kronos.config import citeste_config  # noqa: E402
from kronos.contracte import Propunere  # noqa: E402
from kronos.orchestrator import Orchestrator  # noqa: E402

SEMINTE = [0, 1, 2]
PASI = 25_000


def verdict(serii: list[dict[str, Any]], pasi_ceruti: int | None, prag: float) -> str:
    """Cinstit: întâi verifică dacă testul e valid, abia apoi spune dacă efectul e mare, mic sau neclar.

    serii: pentru fiecare sămânță, {"samanta", "fara": {1: rulare, 2: rulare}, "cu": {1: rulare, 2: rulare}}.
    """
    pasi = sorted({r["pasi"] for s in serii for v in ("fara", "cu") for r in s[v].values()})
    if len(pasi) > 1 or (pasi_ceruti is not None and pasi != [pasi_ceruti]):
        return f"NECONCLUDENT: pași diferiți ({', '.join(f'{p:,}' for p in pasi)}); scorurile nu se pot compara."
    goale = [s["samanta"] for s in serii if not s["cu"][2].get("legaturi_la_start")]
    if goale:
        return (
            f"NECONCLUDENT: plasa goală la runda 2 (semințele {', '.join(map(str, goale))}): "
            "runda 2 n-avea nicio legătură de folosit, deci nu se pot trage concluzii."
        )
    efecte = [
        (s["cu"][2]["scor"] - s["cu"][1]["scor"]) - (s["fara"][2]["scor"] - s["fara"][1]["scor"]) for s in serii
    ]
    medie = statistics.mean(efecte)
    text = f"efect mediu {medie:+.4f}, pe semințe: {', '.join(f'{e:+.4f}' for e in efecte)}"
    if all(e < -prag for e in efecte):
        return f"MARE (merge): plasa păstrată a ajutat runda 2 la fiecare sămânță, peste pragul de zgomot {prag} ({text})."
    if all(e > prag for e in efecte):
        return f"MARE, dar în rău: plasa păstrată a încurcat runda 2 la fiecare sămânță ({text})."
    if abs(medie) <= prag:
        return f"MICĂ (noroc): efectul e sub pragul de zgomot {prag} ({text})."
    return f"NECONCLUDENT: efectul nu are același semn la toate semințele ({text})."


def asteapta_racirea(
    temperatura: Callable[[], float | None],
    tinta: float,
    maxim: float = 300,
    pas: float = 10,
    asteapta: Callable[[float], None] = time.sleep,
) -> None:
    """Pauză de răcire între rulări: până placa coboară la `tinta` grade (cel mult `maxim` secunde)."""
    if tinta <= 0:
        return
    temp = temperatura()
    if temp is None or temp <= tinta:
        return
    print(f"      răcire: placa are {temp:.0f}°C, aștept să coboare la {tinta:.0f}°C...", flush=True)
    asteptat = 0.0
    while temp is not None and temp > tinta and asteptat < maxim:
        asteapta(pas)
        asteptat += pas
        temp = temperatura()


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Testul plasei în două runde, la același număr de pași.")
    parser.add_argument("--config", default="config/laptop_plasa.toml", help="fișierul de configurare")
    parser.add_argument("--seminte", type=int, nargs="+", default=SEMINTE, help="câte o serie pentru fiecare sămânță")
    parser.add_argument("--pasi", type=int, default=PASI, help="câți pași de antrenare face fiecare rulare")
    parser.add_argument("--buget", type=float, default=None, help="limita de siguranță în secunde (implicit: din configurare)")
    parser.add_argument("--racire", type=float, default=70, help="între rulări, aștept placa până la atâtea grade (0 = fără)")
    args = parser.parse_args(argv)
    if args.pasi < 1:
        parser.error("--pasi trebuie să fie cel puțin 1")

    baza = citeste_config(args.config)
    if args.buget is not None:
        baza.buget_antrenare_secunde = args.buget
    else:  # timpul e doar o limită de siguranță: dublul bugetului obișnuit, sub limita paznicului
        timp_max = float(baza.paznic.get("timp_max_secunde", 600))
        baza.buget_antrenare_secunde = min(2 * baza.buget_antrenare_secunde, 0.9 * timp_max)
    reteta = baza.setari_port("model")
    eticheta = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(
        f"Testul plasei în două runde: semințele {args.seminte}, câte {args.pasi:,} de pași pe rulare "
        f"(limită de siguranță {baza.buget_antrenare_secunde:.0f} s).\nRețeta: {reteta}",
        flush=True,
    )

    serii: list[dict[str, Any]] = []
    prima = True
    for samanta in args.seminte:
        cale_plasa = baza.director_lucru / "plase" / f"comparatie_{eticheta}_s{samanta}.json"  # goală la început
        serie: dict[str, Any] = {"samanta": samanta, "fara": {}, "cu": {}}
        for cu_plasa in (False, True):
            for runda in (1, 2):
                config = copy.deepcopy(baza)
                config.nume = f"{baza.nume}_comparatie_{eticheta}_s{samanta}_r{runda}"  # o linie pe rundă
                config.porturi["date"].setdefault("setari", {})["runda"] = runda
                o = Orchestrator(config)
                if not prima:
                    asteapta_racirea(o.paznic.temperatura_gpu, args.racire)
                prima = False
                if o._opreste():  # butonul de oprire și pauzele obișnuite ale paznicului
                    print("Testul s-a oprit înainte de final (motivul e scris mai sus).", flush=True)
                    return 1
                o.setari_curente = {"model": dict(reteta)}
                fisa = o.experiment(
                    Propunere(
                        f"{'cu' if cu_plasa else 'fără'} plasă, runda {runda}, sămânța {samanta}",
                        {"model": {"plasa": cu_plasa, "samanta": samanta, "cale_plasa": str(cale_plasa), "pasi_max": args.pasi}},
                    )
                )
                if fisa["decizie"] == "anulat":
                    print(f"Experimentul #{fisa['id']} a fost anulat: {fisa.get('motiv')}", flush=True)
                    return 1
                statistici = fisa.get("statistici_antrenare") or {}
                durata = (fisa.get("consum") or {}).get("durata_antrenare_secunde") or 0
                dupa = (fisa.get("dupa_examen") or {}).get("plasa") or {}
                rulare = {
                    "experiment": fisa["id"],
                    "scor": fisa["scoruri"][o.examen.scor_principal],
                    "pasi": statistici.get("pasi"),
                    "secunde": durata,
                    "pasi_pe_secunda": round(statistici.get("pasi", 0) / durata, 1) if durata else None,
                    "legaturi_la_start": (statistici.get("plasa") or {}).get("legaturi_la_start"),
                    "legaturi_final": dupa.get("legaturi"),
                    "nascute": dupa.get("nascute"),
                    "castig_primit": dupa.get("castig_primit"),
                    "plasa": dupa or None,
                }
                serie["cu" if cu_plasa else "fara"][runda] = rulare
                if cu_plasa:
                    print(
                        f"      plasa: {rulare['legaturi_la_start']} legături la start → {rulare['legaturi_final']} la final "
                        f"(născute {dupa.get('nascute')}, întărite {dupa.get('intarite')}, slăbite {dupa.get('slabite')}, "
                        f"tăiate {dupa.get('taiate')}, definitive {dupa.get('definitive')})",
                        flush=True,
                    )
        serii.append(serie)

    print(f"\n=== Rezultatul (val_bpb, mai mic = mai bine; {args.pasi:,} de pași fiecare) ===")
    print(
        f"{'sămânța':>7}  {'fără R1':>7}  {'fără R2':>7}  {'cu R1':>7}  {'cu R2':>7}  {'Δ fără':>7}  {'Δ cu':>7}"
        f"  {'legături R1→R2':>14}  {'pași/s fără/cu':>14}"
    )
    for s in serii:
        f1, f2, c1, c2 = s["fara"][1], s["fara"][2], s["cu"][1], s["cu"][2]
        viteza_fara = statistics.mean(r["pasi_pe_secunda"] or 0 for r in (f1, f2))
        viteza_cu = statistics.mean(r["pasi_pe_secunda"] or 0 for r in (c1, c2))
        legaturi = f"{c1['legaturi_final']} → {c2['legaturi_final']}"
        viteza = f"{viteza_fara:.0f} / {viteza_cu:.0f}"
        print(
            f"{s['samanta']:>7}  {f1['scor']:>7.4f}  {f2['scor']:>7.4f}  {c1['scor']:>7.4f}  {c2['scor']:>7.4f}"
            f"  {f2['scor'] - f1['scor']:>+7.4f}  {c2['scor'] - c1['scor']:>+7.4f}  {legaturi:>14}  {viteza:>14}"
        )
    nascute = sum((s["cu"][r]["nascute"] or 0) for s in serii for r in (1, 2))
    print(f"Legături născute în total (toate semințele, ambele runde): {nascute}")
    concluzie = verdict(serii, args.pasi, baza.prag_zgomot)
    print(f"\nVerdict: {concluzie}")

    iesire = baza.director_lucru / f"comparatie_plasa_{eticheta}.json"
    iesire.write_text(
        json.dumps(
            {
                "data": datetime.now().isoformat(timespec="seconds"),
                "configurare": str(args.config),
                "pasi": args.pasi,
                "reteta": reteta,
                "serii": serii,
                "legaturi_nascute": nascute,
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
