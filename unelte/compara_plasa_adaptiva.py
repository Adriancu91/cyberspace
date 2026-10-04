"""Comparația din Etapa M3, pasul 3: GPT simplu / plasa veche (5 noduri) / plasa adaptivă, la același număr de pași.

Pentru fiecare sămânță rulează prin Kronos (același examen, paznicul veghează, totul în jurnal) câte un experiment
pentru fiecare variantă, pe toată validarea (o singură rundă), fiecare oprit la EXACT același număr de pași (--pasi):
    GPT simplu (config/laptop_tinystories.toml), plasa veche (config/laptop_plasa.toml),
    plasa adaptivă (config/laptop_plasa_adaptiva.toml)
Rețeta comună (straturi, lot, rata de învățare, tokenizer) trebuie să fie aceeași în cele trei configurări. Cu aceeași
sămânță, cele trei văd exact aceleași bucăți de text, în aceeași ordine: diferă doar rețeaua de deasupra trunchiului.
Fiecare plasă pornește goală (fără legături, fără ajutoare), într-un fișier al ei. Legăturile născute și nodurile
libere alocate la examen lucrează abia de la experimentul următor: într-o singură rundă se vede ce s-a hotărât, nu și
efectul lor.

Verdictul compară plasa adaptivă cu fiecare din celelalte două, sămânță cu sămânță, cu pragul de zgomot din
configurare (0,005 val_bpb); e NECONCLUDENT dacă rulările nu au toate exact numărul de pași cerut.

    python unelte/compara_plasa_adaptiva.py                          # semințele 0, 1, 2; 25.000 de pași; ~1 oră
    python unelte/compara_plasa_adaptiva.py --seminte 0 --pasi 300   # probă rapidă

Între rulări: o pauză de --pauza secunde (implicit 30), apoi placa se răcește până la --racire grade (implicit 70).
Rezultatul apare pe ecran și în lucru/comparatie_m3_<data>.json.
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
from typing import Any

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from kronos.config import citeste_config  # noqa: E402
from kronos.contracte import Propunere  # noqa: E402
from kronos.orchestrator import Orchestrator  # noqa: E402
from unelte.compara_plasa import asteapta_racirea  # noqa: E402

SEMINTE = [0, 1, 2]
PASI = 25_000
VARIANTE = ("simplu", "plasa5", "adaptiva")
NUME = {"simplu": "GPT simplu", "plasa5": "plasa veche (5 noduri)", "adaptiva": "plasa adaptivă"}
CONFIGURARI = {
    "simplu": "config/laptop_tinystories.toml",
    "plasa5": "config/laptop_plasa.toml",
    "adaptiva": "config/laptop_plasa_adaptiva.toml",
}
RETETA_COMUNA = ("n_straturi", "n_capete", "n_emb", "context", "lot", "rata_invatare", "dropout", "tokenizer", "cale_tokenizer")


def rezultatul(fisa: dict[str, Any], scor_principal: str) -> dict[str, Any]:
    """Ce păstrăm dintr-o fișă: scorul, pașii, viteza (doar pașii, fără pregătire) și ce a hotărât plasa la examen."""
    statistici = fisa.get("statistici_antrenare") or {}
    bucla = statistici.get("secunde_bucla") or 0
    dupa = fisa.get("dupa_examen") or {}
    plasa = dupa.get("plasa") or {}
    nascute = plasa.get("nascute_acum", plasa.get("lista", []))  # plasa veche: toate legăturile sunt noi la start
    noduri = statistici.get("noduri")
    adaptiva = isinstance(noduri, dict) and "active" in noduri
    return {
        "experiment": fisa["id"],
        "scor": fisa["scoruri"][scor_principal],
        "pasi": statistici.get("pasi"),
        "pasi_pe_secunda": round(statistici["pasi"] / bucla, 1) if bucla else None,
        "secunde_antrenare": (fisa.get("consum") or {}).get("durata_antrenare_secunde"),
        "memorie_gpu_mb": (fisa.get("consum") or {}).get("memorie_gpu_max_mb"),
        "noduri_active": noduri["active"] if adaptiva else None,
        "legaturi_nascute": [f"{l['de_la']} → {l['la']}" for l in nascute] if plasa else None,
        "noduri_alocate": [
            f"{a['nod']} → {a['ajuta']} (preia {a['preia']:.0%}: {', '.join(a['exemple'][:3])})"
            for a in (dupa.get("noduri") or {}).get("alocate", [])
        ] if "noduri" in dupa else None,
        # Pentru runda 2: cu ce a pornit plasa, cât a primit fiecare ajutor și cum arată legăturile după examen.
        "legaturi_la_start": (statistici.get("plasa") or {}).get("legaturi_la_start"),
        "legaturi_folosite": (statistici.get("plasa") or {}).get("legaturi"),  # plasa adaptivă: tăria și folosirea
        "ajutoare_la_start": [
            f"{a['nod']} → {a['ajuta']} ({noduri['cuvinte_pe_nod'].get(a['nod'], 0):.1%} din cuvinte)"
            for a in noduri.get("ajutoare", [])
        ] if adaptiva else None,
        "legaturi_dupa": {f"{l['de_la']} → {l['la']}": l["tarie"] for l in plasa.get("lista", [])} if plasa else None,
        "castig_primit": plasa.get("castig_primit"),
    }


def citeste_configurari(cai: dict[str, str]) -> tuple[dict[str, Any], dict[str, dict[str, Any]], list[str]]:
    """Configurările variantelor, rețetele lor de model și setările din rețeta comună care diferă (ar trebui: niciuna)."""
    configurari = {v: citeste_config(cale) for v, cale in cai.items()}
    retete = {v: c.setari_port("model") for v, c in configurari.items()}
    diferite = [k for k in RETETA_COMUNA if len({json.dumps(retete[v].get(k)) for v in retete}) > 1]
    return configurari, retete, diferite


def limita_de_timp(config: Any, buget: float | None) -> None:
    """Bugetul de timp: cel dat sau, implicit, dublul celui obișnuit, sub limita paznicului (la pași fixați e doar o
    plasă de siguranță)."""
    if buget is not None:
        config.buget_antrenare_secunde = buget
    else:
        timp_max = float(config.paznic.get("timp_max_secunde", 600))
        config.buget_antrenare_secunde = min(2 * config.buget_antrenare_secunde, 0.9 * timp_max)


def ruleaza(
    config: Any, linie: str, descriere: str, modificari: dict[str, Any], runda: int = 0,
    pauza: float = 0.0, racire: float = 0.0, cu_fisa: bool = False,
) -> dict[str, Any] | None:
    """Un experiment prin Kronos, pe linia de jurnal dată și pe partea de validare dată (0 = toată, 1 sau 2 = o
    jumătate). Întâi pauza și răcirea plăcii. Întoarce rezultatul (cu_fisa: și fișa întreagă, sub „fisa”), sau None
    dacă s-a oprit ori a fost anulat."""
    config = copy.deepcopy(config)
    config.nume = linie
    if runda:
        config.porturi["date"].setdefault("setari", {})["runda"] = runda
    o = Orchestrator(config)
    time.sleep(pauza)
    asteapta_racirea(o.paznic.temperatura_gpu, racire)
    if o._opreste():  # butonul de oprire și pauzele obișnuite ale paznicului
        print("S-a oprit înainte de final (motivul e scris mai sus).", flush=True)
        return None
    temperatura = o.paznic.temperatura_gpu()
    o.setari_curente = {"model": dict(config.setari_port("model"))}
    fisa = o.experiment(Propunere(descriere, {"model": modificari}))
    if fisa["decizie"] == "anulat":
        print(f"Experimentul #{fisa['id']} a fost anulat: {fisa.get('motiv')}", flush=True)
        return None
    rezultat = {**rezultatul(fisa, o.examen.scor_principal), "temperatura_la_start": temperatura}
    if cu_fisa:
        rezultat["fisa"] = fisa
    return rezultat


def verdict(randuri: list[dict[str, Any]], pasi_ceruti: int | None, prag: float, fata_de: str) -> str:
    """Cinstit: întâi verifică dacă rulările se pot compara, abia apoi spune dacă diferența e mare, mică sau neclară.

    randuri: pentru fiecare sămânță, {"samanta", "simplu": rulare, "plasa5": rulare, "adaptiva": rulare}.
    """
    pasi = sorted({r[v]["pasi"] for r in randuri for v in VARIANTE})
    if len(pasi) > 1 or (pasi_ceruti is not None and pasi != [pasi_ceruti]):
        return f"NECONCLUDENT: pași diferiți ({', '.join(f'{p:,}' for p in pasi)}); scorurile nu se pot compara."
    diferente = [r["adaptiva"]["scor"] - r[fata_de]["scor"] for r in randuri]  # negativ = plasa adaptivă e mai bună
    medie = statistics.mean(diferente)
    text = f"diferență medie {medie:+.4f}, pe semințe: {', '.join(f'{d:+.4f}' for d in diferente)}"
    if all(d < -prag for d in diferente):
        return f"MARE (merge): plasa adaptivă e mai bună la fiecare sămânță, peste pragul de zgomot {prag} ({text})."
    if all(d > prag for d in diferente):
        return f"MARE, dar în rău: plasa adaptivă e mai slabă la fiecare sămânță, peste pragul de zgomot {prag} ({text})."
    if abs(medie) <= prag:
        semn = (
            " La toate semințele în același sens, dar sub prag." if all(d < 0 for d in diferente) or all(d > 0 for d in diferente)
            else " Semnul diferă de la o sămânță la alta."
        )
        return f"MICĂ (noroc): diferența e sub pragul de zgomot {prag} ({text}).{semn}"
    return f"NECONCLUDENT: diferența nu are același semn la toate semințele ({text})."


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="GPT simplu / plasa veche / plasa adaptivă, la același număr de pași.")
    for varianta in VARIANTE:
        parser.add_argument(f"--config-{varianta}", default=CONFIGURARI[varianta], help=f"configurarea: {NUME[varianta]}")
    parser.add_argument("--seminte", type=int, nargs="+", default=SEMINTE, help="câte o rulare din fiecare variantă")
    parser.add_argument("--pasi", type=int, default=PASI, help="câți pași de antrenare face fiecare rulare")
    parser.add_argument("--buget", type=float, default=None, help="limita de siguranță în secunde (implicit: din configurare)")
    parser.add_argument("--pauza", type=float, default=30, help="pauza dintre rulări, în secunde")
    parser.add_argument("--racire", type=float, default=70, help="după pauză, aștept placa până la atâtea grade (0 = fără)")
    args = parser.parse_args(argv)
    if args.pasi < 1:
        parser.error("--pasi trebuie să fie cel puțin 1")

    configurari, retete, diferite = citeste_configurari({v: getattr(args, f"config_{v}") for v in VARIANTE})
    if diferite:
        print(f"Rețetele nu sunt la fel ({', '.join(diferite)}): comparația n-ar fi cinstită. Nu pornesc.", flush=True)
        return 1
    for config in configurari.values():
        limita_de_timp(config, args.buget)
    eticheta = datetime.now().strftime("%Y%m%d_%H%M%S")
    prag = configurari["adaptiva"].prag_zgomot
    print(
        f"Comparația M3: semințele {args.seminte}, câte {args.pasi:,} de pași pe rulare; variante: "
        f"{', '.join(NUME[v] for v in VARIANTE)}.\nRețeta comună: { {k: retete['adaptiva'].get(k) for k in RETETA_COMUNA} }",
        flush=True,
    )

    randuri: list[dict[str, Any]] = []
    prima = True
    for samanta in args.seminte:
        rand: dict[str, Any] = {"samanta": samanta}
        for varianta in VARIANTE:
            config = configurari[varianta]
            modificari: dict[str, Any] = {"samanta": samanta, "pasi_max": args.pasi}
            if varianta != "simplu":  # fiecare plasă pornește goală, în fișierul ei
                modificari["cale_plasa"] = str(config.director_lucru / "plase" / f"m3_{eticheta}_{varianta}_s{samanta}.json")
            rulare = ruleaza(
                config, f"{config.nume}_m3_{eticheta}_s{samanta}",  # o linie de jurnal pe rulare
                f"{NUME[varianta]}, sămânța {samanta}, {args.pasi:,} de pași", modificari,
                pauza=0 if prima else args.pauza, racire=args.racire,
            )
            prima = False
            if rulare is None:
                return 1
            rand[varianta] = rulare
            print(
                f"   sămânța {samanta}, {NUME[varianta]}: val_bpb {rulare['scor']:.4f}, {rulare['pasi']:,} de pași, "
                f"{rulare['pasi_pe_secunda']} pași/s" + (f"; legături născute: {len(rulare['legaturi_nascute'])}"
                                                          if rulare["legaturi_nascute"] is not None else "")
                + (f"; noduri libere alocate: {len(rulare['noduri_alocate'])}" if rulare["noduri_alocate"] is not None else ""),
                flush=True,
            )
        randuri.append(rand)

    print(f"\n=== Rezultatul (val_bpb, mai mic = mai bine; {args.pasi:,} de pași fiecare) ===")
    print(f"{'sămânța':>7}  {'simplu':>7}  {'plasa 5':>7}  {'adaptivă':>8}  {'Δ față de simplu':>16}  "
          f"{'Δ față de plasa 5':>17}  {'pași/s simplu / plasa 5 / adaptivă':>34}")
    for r in randuri:
        viteze = " / ".join(f"{r[v]['pasi_pe_secunda'] or 0:.0f}" for v in VARIANTE)
        print(f"{r['samanta']:>7}  {r['simplu']['scor']:>7.4f}  {r['plasa5']['scor']:>7.4f}  {r['adaptiva']['scor']:>8.4f}  "
              f"{r['adaptiva']['scor'] - r['simplu']['scor']:>+16.4f}  {r['adaptiva']['scor'] - r['plasa5']['scor']:>+17.4f}  "
              f"{viteze:>34}")
    for r in randuri:
        print(f"Sămânța {r['samanta']}: legături născute în plasa veche: {', '.join(r['plasa5']['legaturi_nascute'] or []) or '-'}")
        print(f"           legături născute în plasa adaptivă: {', '.join(r['adaptiva']['legaturi_nascute'] or []) or '-'}")
        print(f"           noduri libere alocate: {'; '.join(r['adaptiva']['noduri_alocate'] or []) or '-'}")
    verdicte = {fata_de: verdict(randuri, args.pasi, prag, fata_de) for fata_de in ("simplu", "plasa5")}
    print(f"\nPlasa adaptivă față de GPT-ul simplu: {verdicte['simplu']}")
    print(f"Plasa adaptivă față de plasa veche: {verdicte['plasa5']}")

    iesire = configurari["adaptiva"].director_lucru / f"comparatie_m3_{eticheta}.json"
    iesire.parent.mkdir(parents=True, exist_ok=True)
    iesire.write_text(
        json.dumps(
            {
                "data": datetime.now().isoformat(timespec="seconds"),
                "configurari": {v: str(getattr(args, f"config_{v}")) for v in VARIANTE},
                "pasi": args.pasi,
                "prag_zgomot": prag,
                "reteta_comuna": {k: retete["adaptiva"].get(k) for k in RETETA_COMUNA},
                "randuri": randuri,
                "verdict_fata_de_simplu": verdicte["simplu"],
                "verdict_fata_de_plasa5": verdicte["plasa5"],
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
