"""Runda 2 pentru plasa adaptivă (Etapa M3), ca testul în două runde din M2.

Pornește de la comparația din runda 1 (lucru/comparatie_m3_<data>.json, făcută cu unelte/compara_plasa_adaptiva.py):
aceleași semințe și același număr de pași, dar examenul se dă pe a doua jumătate a poveștilor de validare (runda 2).
Fiecare plasă (veche și adaptivă) pornește cu ce a hotărât în runda 1, la aceeași sămânță: legăturile născute și
nodurile libere alocate. Lucrează pe o copie a fișierului ei, ca runda 1 să rămână neatinsă. GPT-ul simplu rulează și el,
ca martor.

Pentru fiecare sămânță, cele trei rulări stau pe aceeași linie din jurnal, în ordinea: GPT simplu, plasa adaptivă, plasa
veche. Așa, câștigul primit de plasa adaptivă după examen (singurul lucru pe care îl află despre examen: un număr) e cât
a bătut-o pe GPT-ul simplu, pe aceeași jumătate și cu aceeași sămânță; legăturile folosite se întăresc sau slăbesc după
el. Plasa veche primește câștigul față de cea mai bună variantă de dinainte de pe linie (de obicei GPT-ul simplu).

Efectul adaptării, pentru o sămânță = (R2 − R1 plasa adaptivă) − (R2 − R1 GPT simplu). La GPT-ul simplu (antrenat la fel
în ambele runde), diferența dintre runde vine doar din textul de examen diferit (R1 = toată validarea, R2 = a doua
jumătate); la plasa adaptivă se adaugă ce a adus ce a hotărât în runda 1. Verdictul e NECONCLUDENT dacă rulările au pași
diferiți sau dacă plasa adaptivă a pornit goală (fără legături și fără noduri libere alocate).

    python unelte/runda2_plasa_adaptiva.py                   # ultima comparație din lucru/; ~45 de minute
    python unelte/runda2_plasa_adaptiva.py --runda1 lucru/comparatie_m3_20261004_001816.json

Rezultatul apare pe ecran și în lucru/runda2_m3_<data>.json.
"""

from __future__ import annotations

import argparse
import json
import shutil
import statistics
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from unelte.compara_plasa_adaptiva import NUME, citeste_configurari, limita_de_timp, ruleaza  # noqa: E402

ORDINE = ("simplu", "adaptiva", "plasa5")  # GPT-ul simplu primul: câștigul plasei adaptive e față de el
CU_PLASA = ("adaptiva", "plasa5")


def _efect(rand: dict[str, Any], varianta: str) -> float:
    """(R2 − R1 varianta) − (R2 − R1 GPT simplu): negativ = ce a hotărât plasa în runda 1 a ajutat în runda 2."""
    return (rand[varianta]["r2"]["scor"] - rand[varianta]["r1"]["scor"]) - (rand["simplu"]["r2"]["scor"] - rand["simplu"]["r1"]["scor"])


def verdict(randuri: list[dict[str, Any]], pasi_ceruti: int | None, prag: float, varianta: str = "adaptiva") -> str:
    """Cinstit: întâi verifică dacă testul e valid (pași, plasa pornită goală), abia apoi spune cât de mare e efectul."""
    pasi = sorted({r[v][runda]["pasi"] for r in randuri for v in ("simplu", varianta) for runda in ("r1", "r2")})
    if len(pasi) > 1 or (pasi_ceruti is not None and pasi != [pasi_ceruti]):
        return f"NECONCLUDENT: pași diferiți ({', '.join(f'{p:,}' for p in pasi)}); scorurile nu se pot compara."
    goale = [
        r["samanta"] for r in randuri
        if not r[varianta]["r2"].get("legaturi_la_start") and not r[varianta]["r2"].get("ajutoare_la_start")
    ]
    if goale:
        return (
            f"NECONCLUDENT: plasa a pornit goală în runda 2 (semințele {', '.join(map(str, goale))}): n-avea nici "
            "legături, nici noduri libere alocate de folosit, deci nu se pot trage concluzii."
        )
    efecte = [_efect(r, varianta) for r in randuri]
    medie = statistics.mean(efecte)
    text = f"efect mediu {medie:+.4f}, pe semințe: {', '.join(f'{e:+.4f}' for e in efecte)}"
    if all(e < -prag for e in efecte):
        return f"MARE (merge): ce a hotărât plasa în runda 1 a ajutat runda 2 la fiecare sămânță, peste pragul {prag} ({text})."
    if all(e > prag for e in efecte):
        return f"MARE, dar în rău: ce a hotărât plasa în runda 1 a încurcat runda 2 la fiecare sămânță ({text})."
    if abs(medie) <= prag:
        return f"MICĂ (noroc): efectul e sub pragul de zgomot {prag} ({text})."
    return f"NECONCLUDENT: efectul nu are același semn la toate semințele ({text})."


def ultima_comparatie(director: Path) -> Path | None:
    comparatii = sorted(director.glob("comparatie_m3_*.json"))
    return comparatii[-1] if comparatii else None


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Runda 2 pentru plasa adaptivă, pornind de la comparația din runda 1.")
    parser.add_argument("--runda1", default=None, help="rezultatul rundei 1 (implicit: ultimul lucru/comparatie_m3_*.json)")
    parser.add_argument("--buget", type=float, default=None, help="limita de siguranță în secunde (implicit: din configurare)")
    parser.add_argument("--pauza", type=float, default=30, help="pauza dintre rulări, în secunde")
    parser.add_argument("--racire", type=float, default=70, help="înainte de fiecare rulare, aștept placa până la atâtea grade")
    args = parser.parse_args(argv)

    cale_r1 = Path(args.runda1) if args.runda1 else ultima_comparatie(Path("lucru"))
    if cale_r1 is None or not cale_r1.exists():
        print("Nu găsesc rezultatul rundei 1 (lucru/comparatie_m3_*.json). Rulează întâi unelte/compara_plasa_adaptiva.py.")
        return 1
    runda1 = json.loads(cale_r1.read_text(encoding="utf-8"))
    eticheta_r1 = cale_r1.stem.removeprefix("comparatie_m3_")
    configurari, retete, diferite = citeste_configurari({v: runda1["configurari"][v] for v in ORDINE})
    if diferite:
        print(f"Rețetele nu mai sunt la fel ({', '.join(diferite)}): comparația n-ar fi cinstită. Nu pornesc.", flush=True)
        return 1
    for config in configurari.values():
        limita_de_timp(config, args.buget)
    pasi = runda1["pasi"]
    prag = configurari["adaptiva"].prag_zgomot
    eticheta = datetime.now().strftime("%Y%m%d_%H%M%S")
    plase = configurari["adaptiva"].director_lucru / "plase"
    copii = {}
    for rand in runda1["randuri"]:  # fiecare plasă pornește din starea ei de la sfârșitul rundei 1, într-o copie
        for varianta in CU_PLASA:
            sursa = plase / f"m3_{eticheta_r1}_{varianta}_s{rand['samanta']}.json"
            if not sursa.exists():
                print(f"Lipsește plasa din runda 1: {sursa}. Nu pornesc.", flush=True)
                return 1
            copii[(varianta, rand["samanta"])] = copie = plase / f"m3_runda2_{eticheta}_{varianta}_s{rand['samanta']}.json"
            shutil.copyfile(sursa, copie)
    print(
        f"Runda 2 (a doua jumătate a validării), pornind de la {cale_r1}: semințele "
        f"{[r['samanta'] for r in runda1['randuri']]}, câte {pasi:,} de pași. Fiecare plasă pornește cu ce a hotărât în runda 1.",
        flush=True,
    )

    randuri: list[dict[str, Any]] = []
    prima = True
    for rand_r1 in runda1["randuri"]:
        samanta = rand_r1["samanta"]
        rand: dict[str, Any] = {"samanta": samanta}
        for varianta in ORDINE:
            modificari: dict[str, Any] = {"samanta": samanta, "pasi_max": pasi}
            if varianta in CU_PLASA:
                modificari["cale_plasa"] = str(copii[(varianta, samanta)])
            r2 = ruleaza(
                configurari[varianta], f"m3_runda2_{eticheta}_s{samanta}",  # o linie pe sămânță: câștigul e față de GPT
                f"{NUME[varianta]}, runda 2, sămânța {samanta}, {pasi:,} de pași", modificari, runda=2,
                pauza=0 if prima else args.pauza, racire=args.racire,
            )
            prima = False
            if r2 is None:
                return 1
            rand[varianta] = {"r1": rand_r1[varianta], "r2": r2}
            print(
                f"   sămânța {samanta}, {NUME[varianta]}: R1 {rand_r1[varianta]['scor']:.4f} → R2 {r2['scor']:.4f}, "
                f"{r2['pasi']:,} de pași" + (f"; a pornit cu {r2['legaturi_la_start']} legături" if varianta in CU_PLASA else "")
                + (f" și {len(r2['ajutoare_la_start'] or [])} noduri libere" if varianta == "adaptiva" else "")
                + (f"; câștig primit {r2['castig_primit']:+.4f}" if r2.get("castig_primit") is not None else ""),
                flush=True,
            )
        randuri.append(rand)

    print(f"\n=== Runda 2 (val_bpb, mai mic = mai bine; R1 = toată validarea, R2 = a doua jumătate; {pasi:,} de pași) ===")
    print(f"{'sămânța':>7}  {'simplu R1':>9}  {'simplu R2':>9}  {'adaptivă R1':>11}  {'adaptivă R2':>11}  "
          f"{'Δ simplu':>8}  {'Δ adaptivă':>10}  {'efect':>7}  {'veche R1→R2':>15}  {'efect veche':>11}")
    for r in randuri:
        print(
            f"{r['samanta']:>7}  {r['simplu']['r1']['scor']:>9.4f}  {r['simplu']['r2']['scor']:>9.4f}  "
            f"{r['adaptiva']['r1']['scor']:>11.4f}  {r['adaptiva']['r2']['scor']:>11.4f}  "
            f"{r['simplu']['r2']['scor'] - r['simplu']['r1']['scor']:>+8.4f}  "
            f"{r['adaptiva']['r2']['scor'] - r['adaptiva']['r1']['scor']:>+10.4f}  {_efect(r, 'adaptiva'):>+7.4f}  "
            f"{r['plasa5']['r1']['scor']:.4f}→{r['plasa5']['r2']['scor']:.4f}  {_efect(r, 'plasa5'):>+11.4f}"
        )
    for r in randuri:
        r2 = r["adaptiva"]["r2"]
        dupa = r2["legaturi_dupa"] or {}  # tăria după examenul rundei 2
        castig = f"{r2['castig_primit']:+.4f}" if r2["castig_primit"] is not None else "niciunul"
        print(f"Sămânța {r['samanta']} (câștig primit de plasa adaptivă: {castig}):")
        print(f"   noduri libere folosite: {'; '.join(r2['ajutoare_la_start'] or []) or '-'}")
        print(f"   legături folosite (tăria la start → după examen):")
        for leg in r2.get("legaturi_folosite") or []:
            nume = f"{leg['de_la']} → {leg['la']}"
            print(f"      {nume:<45} {leg['tarie']:.3f} → {dupa.get(nume, 0.0):.3f}  (folosire {leg['folosire']:.3f})")
        print(f"   legături născute acum: {', '.join(r2['legaturi_nascute'] or []) or '-'}")
        print(f"   noduri libere alocate acum (pentru runda 3): {'; '.join(r2['noduri_alocate'] or []) or '-'}")
    verdicte = {v: verdict(randuri, pasi, prag, v) for v in CU_PLASA}
    print(f"\nEfectul adaptării, plasa adaptivă: {verdicte['adaptiva']}")
    print(f"Efectul plasei păstrate, plasa veche: {verdicte['plasa5']}")

    iesire = configurari["adaptiva"].director_lucru / f"runda2_m3_{eticheta}.json"
    iesire.write_text(
        json.dumps(
            {
                "data": datetime.now().isoformat(timespec="seconds"),
                "runda1": str(cale_r1),
                "pasi": pasi,
                "prag_zgomot": prag,
                "randuri": randuri,
                "verdict_adaptiva": verdicte["adaptiva"],
                "verdict_plasa5": verdicte["plasa5"],
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
