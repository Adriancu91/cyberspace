"""Testul în trei trepte pentru plasa adaptivă mare (Etapa M3, propus de Adrian).

Plasa mare (config/laptop_m3_plasa_mare.toml: ~1,5× cel mai mare GPT care încape, nodurile în RAM) și martorul, GPT-ul la
plafon (config/laptop_m3_gpt_plafon.toml), se antrenează pe bucăți de câte 10 minute, fiecare bucată un experiment Kronos
cu examenul oficial la final: scorul la fiecare 10 minute. Între bucăți și între trepte se păstrează TOT: fiecare model
continuă din starea lui (greutăți, optimizator; la plasă și legăturile cu tăria lor, alocările nodurilor libere).
Treptele, pe trei texte fără suprapunere, din ce în ce mai mari; examenul pe o bucată nevăzută din textul fiecăreia:
    1 (R1): TinyStories de acum (18 MB), 20 de minute — funcționează și învață?
    2 (R2): TinyStories de 10× mai mult (180 MB, bucata de după R1), 40 de minute — ține pasul cu GPT-ul la limită?
    3 (R3): Simple English Wikipedia (270 MB), 60 de minute — scade scorul constant pe un text mai greu și mai mare?
În fiecare interval de 10 minute rulează întâi martorul, apoi plasa; înainte de fiecare: pauză și răcire. Verdictele
folosesc pragul de zgomot din configurare (0,005 val_bpb); cu o singură sămânță, pragul e singura măsură a zgomotului.

    python unelte/trepte_plasa_mare.py --trepte 1        # ~50 de minute
    python unelte/trepte_plasa_mare.py --trepte 2        # ~1 oră și 40 de minute
    python unelte/trepte_plasa_mare.py --trepte 3        # ~2 ore și 30 de minute

Starea modelelor: lucru/m3_mare/ (câte un fișier pe model și sămânță). Rezultatele: lucru/m3_trepte/treapta_<n>.json.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from unelte.compara_plasa_adaptiva import citeste_configurari, ruleaza  # noqa: E402

VARIANTE = ("gpt", "plasa")
NUME = {"gpt": "GPT la plafon", "plasa": "plasa mare"}
CONFIGURARI = {"gpt": "config/laptop_m3_gpt_plafon.toml", "plasa": "config/laptop_m3_plasa_mare.toml"}
TREPTE: dict[int, dict[str, Any]] = {
    1: {"minute": 20, "text": "TinyStories de acum (18 MB)", "intrebare": "funcționează și învață?",
        "date": {"modul": "module.date_tinystories:DateTinyStories", "setari": {"director": "date/tinystories", "megaocteti": 20.0}}},
    2: {"minute": 40, "text": "TinyStories de 10× mai mult (180 MB)", "intrebare": "ține pasul cu GPT-ul la limită?",
        "date": {"modul": "module.date_tinystories:DateTinyStories", "setari": {
            "director": "date/tinystories_r2", "megaocteti": 182.0, "procent_validare": 0.011, "decalaj_antrenare_mo": 18.0,
            "decalaj_validare_mo": 2.0, "fara_povestile_din": ["date/tinystories"]}}},
    3: {"minute": 60, "text": "Simple English Wikipedia (270 MB)", "intrebare": "scade scorul constant?",
        "date": {"modul": "module.date_wikipedia:DateWikipedia", "setari": {"director": "date/wikipedia_simpla"}}},
}


def cu_samanta(cale: str, samanta: int) -> str:
    """lucru/m3_mare/plasa_mare.pt → lucru/m3_mare/plasa_mare_s0.pt: fiecare sămânță cu starea ei."""
    p = Path(cale)
    return str(p.with_name(f"{p.stem}_s{samanta}{p.suffix}"))


def bucata(rezultat: dict[str, Any], minut: float) -> dict[str, Any]:
    """Ce păstrăm dintr-o bucată de 10 minute: scorul, viteza, memoria video, mutatul nodurilor și ce a făcut plasa."""
    fisa = rezultat["fisa"]
    statistici = fisa.get("statistici_antrenare") or {}
    dupa = fisa.get("dupa_examen") or {}
    plasa = statistici.get("plasa") or {}
    noduri = statistici.get("noduri") if isinstance(statistici.get("noduri"), dict) else {}
    return {
        "minut": minut,
        "experiment": rezultat["experiment"],
        "scor": rezultat["scor"],
        "pasi": rezultat["pasi"],
        "pasi_total": statistici.get("pasi_total"),
        "pasi_pe_secunda": rezultat["pasi_pe_secunda"],
        "memorie_ocupata_mb": rezultat["memorie_gpu_mb"],
        "memorie_rezervata_mb": statistici.get("memorie_rezervata_mb"),
        "temperatura_la_start": rezultat.get("temperatura_la_start"),
        "parametri": statistici.get("parametri_total", statistici.get("parametri")),
        "mutare_noduri": statistici.get("mutare_noduri"),
        "legaturi_la_start": plasa.get("legaturi") if plasa else None,  # cu tăria și folosirea fiecăreia
        "ajutoare_la_start": noduri.get("ajutoare") if noduri else None,
        "legaturi_nascute": [f"{l['de_la']} → {l['la']}" for l in (dupa.get("plasa") or {}).get("nascute_acum", [])] if dupa.get("plasa") else None,
        "legaturi_dupa": {f"{l['de_la']} → {l['la']}": l["tarie"] for l in (dupa.get("plasa") or {}).get("lista", [])}
        if dupa.get("plasa") else None,
        "castig_primit": (dupa.get("plasa") or {}).get("castig_primit"),
        "noduri_alocate": [f"{a['nod']} → {a['ajuta']} (preia {a['preia']:.0%}: {', '.join(a['exemple'][:3])})"
                           for a in (dupa.get("noduri") or {}).get("alocate", [])] if dupa.get("noduri") else None,
        "ajutoare_dupa": (dupa.get("noduri") or {}).get("ajutoare") if dupa.get("noduri") else None,
    }


def verdict(treapta: int, plasa: list[dict[str, Any]], gpt: list[dict[str, Any]], prag: float, limita_mb: float) -> str:
    """Răspunsul cinstit la întrebarea treptei, cu pragul de zgomot."""
    scoruri = [b["scor"] for b in plasa]
    scaderi = [b - a for a, b in zip(scoruri, scoruri[1:])]  # negativ = a scăzut
    peste_limita = [b["minut"] for b in plasa if (b["memorie_rezervata_mb"] or 0) > limita_mb]
    if peste_limita:
        return f"NU: memoria video a trecut de {limita_mb:.0f} MB (la minutele {peste_limita})."
    text_scaderi = ", ".join(f"{d:+.4f}" for d in scaderi) or "—"
    if treapta == 1:
        if scaderi and all(d < -prag for d in scaderi):
            raspuns = f"DA: funcționează și învață (scorul scade la fiecare 10 minute, peste pragul {prag}: {text_scaderi})."
        elif scoruri[-1] < scoruri[0]:
            raspuns = f"PARȚIAL: funcționează, scorul scade, dar nu de fiecare dată peste pragul {prag} ({text_scaderi})."
        else:
            raspuns = f"NU: scorul nu scade ({text_scaderi})."
    elif treapta == 2:
        diferente = [p["scor"] - g["scor"] for p, g in zip(plasa, gpt)]
        text = ", ".join(f"{d:+.4f}" for d in diferente)
        if diferente[-1] < -prag:
            raspuns = f"DA, chiar o întrece: la final e mai bună decât GPT-ul cu {-diferente[-1]:.4f} (diferențele la 10 minute: {text})."
        elif diferente[-1] <= prag:
            raspuns = f"DA: ține pasul, diferența finală e sub pragul de zgomot {prag} (diferențele la 10 minute: {text})."
        else:
            raspuns = f"NU: rămâne în urmă cu {diferente[-1]:.4f} la final, peste pragul {prag} (diferențele la 10 minute: {text})."
    else:
        if scaderi and all(d < 0 for d in scaderi):
            peste = sum(d < -prag for d in scaderi)
            raspuns = (f"DA: scorul scade la fiecare 10 minute ({text_scaderi}); {peste} din {len(scaderi)} scăderi trec de "
                       f"pragul {prag}; în total {scoruri[-1] - scoruri[0]:+.4f}.")
        elif scoruri[-1] < scoruri[0] - prag:
            raspuns = f"PARȚIAL: în total scade ({scoruri[-1] - scoruri[0]:+.4f}), dar nu la fiecare 10 minute ({text_scaderi})."
        else:
            raspuns = f"NU: scorul nu scade constant ({text_scaderi})."
    if gpt:
        raspuns += f" Martorul (GPT la plafon) la final: {gpt[-1]['scor']:.4f}; plasa: {plasa[-1]['scor']:.4f}."
    return raspuns


def _plasa_intre_runde(plasa: list[dict[str, Any]]) -> dict[str, Any]:
    """Legăturile la începutul treptei (câte, câte folosite, tăria) și la sfârșit; nodurile libere alocate."""
    la_start = plasa[0]["legaturi_la_start"] or []
    dupa = plasa[-1]["legaturi_dupa"] or {}
    folosite = [l for l in la_start if l["folosire"] > 0]
    return {
        "legaturi_la_inceput": len(la_start),
        "folosite_in_prima_bucata": len(folosite),
        "taria_la_inceput": {f"{l['de_la']} → {l['la']}": l["tarie"] for l in la_start},
        "legaturi_la_final": len(dupa),
        "taria_la_final": dupa,
        "nascute_in_treapta": [l for b in plasa for l in (b["legaturi_nascute"] or [])],
        "noduri_libere_la_inceput": plasa[0]["ajutoare_la_start"],
        "noduri_libere_la_final": plasa[-1]["ajutoare_dupa"],
        "alocate_in_treapta": [a for b in plasa for a in (b["noduri_alocate"] or [])],
    }


def main(argv: list[str] | None = None, trepte: dict[int, dict[str, Any]] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    trepte = trepte or TREPTE
    parser = argparse.ArgumentParser(description="Testul în trei trepte pentru plasa adaptivă mare.")
    for varianta in VARIANTE:
        parser.add_argument(f"--config-{varianta}", default=CONFIGURARI[varianta], help=f"configurarea: {NUME[varianta]}")
    parser.add_argument("--trepte", type=int, nargs="+", default=[1], choices=sorted(trepte))
    parser.add_argument("--samanta", type=int, default=0)
    parser.add_argument("--minute-pe-bucata", type=float, default=10, help="cât durează o bucată de antrenare (un examen)")
    parser.add_argument("--fara-martor", action="store_true", help="doar plasa (fără GPT-ul la plafon)")
    parser.add_argument("--pauza", type=float, default=20, help="pauza dinaintea fiecărei bucăți, în secunde")
    parser.add_argument("--racire", type=float, default=70, help="înainte de fiecare bucată, aștept placa până la atâtea grade")
    parser.add_argument("--iesire", default="lucru/m3_trepte", help="unde se scriu rezultatele")
    args = parser.parse_args(argv)

    configurari, _, _ = citeste_configurari({v: getattr(args, f"config_{v}") for v in VARIANTE})
    prag = configurari["plasa"].prag_zgomot
    limita = float(configurari["plasa"].paznic.get("memorie_gpu_max_mb", 5500))
    variante = ("plasa",) if args.fara_martor else VARIANTE
    for treapta in args.trepte:
        definitie = trepte[treapta]
        bucati = max(1, round(definitie["minute"] / args.minute_pe_bucata))
        print(f"\n=== Treapta {treapta}: {definitie['text']}, {bucati} × {args.minute_pe_bucata:g} minute — "
              f"{definitie['intrebare']} ===", flush=True)
        puncte: dict[str, list[dict[str, Any]]] = {v: [] for v in variante}
        for b in range(1, bucati + 1):
            for varianta in variante:
                config = copy.deepcopy(configurari[varianta])
                config.porturi["date"] = copy.deepcopy(definitie["date"])
                config.buget_antrenare_secunde = args.minute_pe_bucata * 60
                cale_stare = cu_samanta(config.setari_port("model")["cale_stare"], args.samanta)
                rezultat = ruleaza(
                    config, f"m3_trepte_{varianta}_s{args.samanta}_R{treapta}",
                    f"{NUME[varianta]}, treapta {treapta}, minutele {(b - 1) * args.minute_pe_bucata:g}–{b * args.minute_pe_bucata:g}",
                    {"samanta": args.samanta, "cale_stare": cale_stare, "pasi_max": 0},
                    pauza=args.pauza, racire=args.racire, cu_fisa=True,
                )
                if rezultat is None:
                    return 1
                punct = bucata(rezultat, b * args.minute_pe_bucata)
                puncte[varianta].append(punct)
                mutare = punct["mutare_noduri"] or {}
                print(f"   minutul {punct['minut']:g}, {NUME[varianta]}: val_bpb {punct['scor']:.4f}, {punct['pasi']:,} de pași "
                      f"({punct['pasi_pe_secunda']} pași/s), memorie video {punct['memorie_ocupata_mb'] or 0:.0f} MB ocupați / "
                      f"{punct['memorie_rezervata_mb'] or 0} rezervați"
                      + (f", mutarea nodurilor {mutare.get('parte_din_antrenare', 0):.0%} din timp" if mutare else ""), flush=True)
        rezultat_treapta = {
            "treapta": treapta,
            "data": datetime.now().isoformat(timespec="seconds"),
            "text": definitie["text"],
            "intrebare": definitie["intrebare"],
            "samanta": args.samanta,
            "minute_pe_bucata": args.minute_pe_bucata,
            "prag_zgomot": prag,
            "plasa": puncte["plasa"],
            "gpt": puncte.get("gpt", []),
            "plasa_intre_runde": _plasa_intre_runde(puncte["plasa"]),
            "verdict": verdict(treapta, puncte["plasa"], puncte.get("gpt", []), prag, limita),
        }
        print(f"\n{'minutul':>7}  {'plasa':>7}  {'GPT':>7}  {'pași/s plasa / GPT':>18}  {'mutarea nodurilor':>17}")
        for i, p in enumerate(puncte["plasa"]):
            g = puncte.get("gpt", [])[i] if puncte.get("gpt") else None
            print(f"{p['minut']:>7g}  {p['scor']:>7.4f}  {(g['scor'] if g else float('nan')):>7.4f}  "
                  f"{p['pasi_pe_secunda'] or 0:>8.2f} / {(g['pasi_pe_secunda'] or 0) if g else 0:>7.2f}  "
                  f"{(p['mutare_noduri'] or {}).get('parte_din_antrenare', 0):>16.0%}")
        intre = rezultat_treapta["plasa_intre_runde"]
        print(f"Plasa: {intre['legaturi_la_inceput']} legături la început ({intre['folosite_in_prima_bucata']} folosite), "
              f"{intre['legaturi_la_final']} la final; născute: {len(intre['nascute_in_treapta'])}; "
              f"noduri libere alocate în treaptă: {intre['alocate_in_treapta'] or '-'}")
        print(f"Verdict, treapta {treapta} ({definitie['intrebare']}): {rezultat_treapta['verdict']}", flush=True)
        iesire = Path(args.iesire) / f"treapta_{treapta}.json"
        iesire.parent.mkdir(parents=True, exist_ok=True)
        iesire.write_text(json.dumps(rezultat_treapta, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Salvat în {iesire}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
