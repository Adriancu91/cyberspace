"""Proba scurtă pe placă a unei configurări cu Muon (S30, C-21.2): memoria, temperatura și pierderea de la început.

Nu e un experiment Kronos: nu scrie în jurnal, nu dă examene și nu păstrează niciun model (proba nu e un rezultat).
Pornește din greutățile modelului salvat la experimentul dat (ca antrenare_lunga.py --porneste-din, cu optimizatorul
de la zero), antrenează câteva minute cu rețeta din configurare și notează pierderea la fiecare lot, memoria plăcii
(PyTorch și nvidia-smi, toată placa), temperatura și simbolurile pe secundă. Se oprește singură dacă placa trece de
--memorie-max MB sau ajunge la --temperatura-max grade. Starea de pornire și rezultatul stau în --dosar (sub lucru/, nu în Git).

Fără --porneste-din (S60, pentru S58): model nou, de la zero (`de_la_zero`, fără cale_stare): nu citește și nu scrie
starea liniei, nu deschide jurnalul și nu face examenul.

    python unelte/proba_muon.py --config config/conv_w2_muon_B.toml --porneste-din 415 --minute 10 \
        --minute-lr-mic 2 --rata-muon-mica 0.01 --dosar lucru/cascada/S30_proba
    python unelte/proba_muon.py --config config/cod_c1.toml --minute 10 --memorie-max 6500 --dosar lucru/cascada/S58_proba
"""

from __future__ import annotations

import argparse
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
from kronos.jurnal import Jurnal  # noqa: E402
from kronos.registru import Registru  # noqa: E402


class PlacaPreaPlina(RuntimeError):
    pass


def rezumat_pierderi(pierderi: list[float], adunare: int) -> dict[str, Any]:
    """Media pierderii pe fiecare pas al optimizatorului (câte `adunare` loturi), primele 20 și cele de la sfârșit."""
    pe_pas = [statistics.fmean(pierderi[i:i + adunare]) for i in range(0, len(pierderi) - adunare + 1, adunare)]
    return {"loturi": len(pierderi), "primul_lot": pierderi[0] if pierderi else None,
            "primii_pasi": [round(x, 4) for x in pe_pas[:20]],
            "media_primilor_100_loturi": round(statistics.fmean(pierderi[:100]), 4) if pierderi else None,
            "media_ultimilor_100_loturi": round(statistics.fmean(pierderi[-100:]), 4) if pierderi else None,
            "cea_mai_mare_in_primii_20_pasi": round(max(pe_pas[:20]), 4) if pe_pas else None}


def o_rulare(config: Any, setari: dict[str, Any], date: Any, minute: float, memorie_max: int, temperatura_max: int) -> dict[str, Any]:
    import torch

    from unelte.urmareste_placa import citeste

    model = Registru().creeaza("model", config.porturi["model"]["modul"], setari).instanta
    pierderi: list[float] = []
    placa = {"memorie_max_mb": 0, "temperatura_max": 0, "citiri": 0}
    pas_vechi = model._pas_adunat

    def pas_urmarit(loss: Any) -> float:
        valoare = pas_vechi(loss)
        pierderi.append(valoare)
        if len(pierderi) % 25 == 1:
            citire = citeste()
            if citire:
                t, m, _ = citire
                placa.update(memorie_max_mb=max(placa["memorie_max_mb"], m), temperatura_max=max(placa["temperatura_max"], t),
                             citiri=placa["citiri"] + 1)
                if m > memorie_max or t >= temperatura_max:
                    raise PlacaPreaPlina(f"placa: {m} MB, {t} °C (limitele: {memorie_max} MB, {temperatura_max} °C)")
            if len(pierderi) % 500 == 1:
                print(f"   lotul {len(pierderi)}: pierderea {valoare:.4f}, placa {placa['memorie_max_mb']} MB, "
                      f"{placa['temperatura_max']} °C, la {datetime.now():%H:%M:%S}", flush=True)
        return valoare

    model._pas_adunat = pas_urmarit
    inceput = time.perf_counter()
    oprita = None
    statistici: dict[str, Any] = {}
    try:
        statistici = model.antreneaza(date, minute * 60)
    except PlacaPreaPlina as e:
        oprita = str(e)
        print(f"   OPRITĂ: {oprita}", flush=True)
    secunde = time.perf_counter() - inceput
    simboluri_pe_lot = int(setari.get("lot", 1)) * int(setari.get("context", 1))
    rezultat = {
        "optimizator": setari.get("optimizator"), "rata_muon": setari.get("rata_muon"), "minute": minute,
        "secunde": round(secunde, 1), "oprita": oprita,
        "pasi": statistici.get("pasi", len(pierderi)), "pasi_optimizator": statistici.get("pasi_optimizator"),
        "loturi_pe_secunda": round(len(pierderi) / secunde, 2) if secunde else None,
        "simboluri_pe_secunda": round(len(pierderi) * simboluri_pe_lot / secunde) if secunde else None,
        "rata_la_final": statistici.get("rata_la_final"),
        "memorie_pytorch_max_mb": round(torch.cuda.max_memory_reserved() / 2**20) if torch.cuda.is_available() else None,
        "placa": placa, "pierdere": rezumat_pierderi(pierderi, int(setari.get("adunare_loturi", 1))),
    }
    model.elibereaza_placa()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
    return rezultat


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Proba scurtă pe placă a unei configurări cu Muon (fără jurnal, fără model păstrat).")
    parser.add_argument("--config", required=True)
    parser.add_argument("--porneste-din", type=int, default=None, help="fără el: model nou, de la zero")
    parser.add_argument("--minute", type=float, default=10)
    parser.add_argument("--minute-lr-mic", type=float, default=0, help="încă o rulare scurtă, cu --rata-muon-mica")
    parser.add_argument("--rata-muon-mica", type=float, default=0.01)
    parser.add_argument("--memorie-max", type=int, default=7000)
    parser.add_argument("--temperatura-max", type=int, default=83)
    parser.add_argument("--dosar", type=Path, default=Path("lucru/cascada/S30_proba"))
    args = parser.parse_args(argv)

    from module.model_continuu import salveaza_atomic
    from unelte.antrenare_lunga import cu_hrana_implicita, stare_de_pornire

    config = citeste_config(args.config)
    cu_hrana_implicita(config)
    args.dosar.mkdir(parents=True, exist_ok=True)
    if args.porneste_din is None:
        setari = {**config.setari_port("model"), "cale_stare": "", "de_la_zero": True}  # nimic citit, nimic scris
        de_unde = "de la zero"
    else:
        examen = Registru().creeaza("examen", config.porturi["examen"]["modul"], config.setari_port("examen")).instanta
        jurnal = Jurnal(config.director_lucru)  # doar citire: fișa experimentului de pornire
        pornire = args.dosar / f"pornire_{args.porneste_din}.pt"
        if not pornire.exists():
            stare, inainte = stare_de_pornire(config, jurnal, args.porneste_din, examen.scor_principal)
            salveaza_atomic(stare, pornire)
            print(f"Starea de pornire: #{inainte['experiment']} (val_bpb {inainte['scor']:.4f}) → {pornire}", flush=True)
        setari = {**config.setari_port("model"), "cale_stare": str(pornire)}  # se citește, nu se scrie (fără dupa_examen)
        de_unde = f"din #{args.porneste_din}"
    date = Registru().creeaza("date", config.porturi["date"]["modul"], config.setari_port("date")).instanta
    rulari = []
    print(f"Proba: {args.minute:g} minute, {setari.get('optimizator')} (rata Muon {setari.get('rata_muon')}), "
          f"adunare {setari.get('adunare_loturi', 1)}, {de_unde}.", flush=True)
    rulari.append(o_rulare(config, setari, date, args.minute, args.memorie_max, args.temperatura_max))
    if args.minute_lr_mic and not rulari[-1]["oprita"]:
        print(f"Proba 2: {args.minute_lr_mic:g} minute, rata Muon {args.rata_muon_mica:g}.", flush=True)
        rulari.append(o_rulare(config, {**setari, "rata_muon": args.rata_muon_mica}, date, args.minute_lr_mic,
                               args.memorie_max, args.temperatura_max))
    iesire = args.dosar / "proba.json"
    iesire.write_text(json.dumps({"data": datetime.now().isoformat(timespec="seconds"), "config": args.config,
                                  "porneste_din": args.porneste_din, "rulari": rulari}, ensure_ascii=False, indent=2),
                      encoding="utf-8")
    for r in rulari:
        print(f"{r['optimizator']} rata Muon {r['rata_muon']}: {r['pasi']} loturi ({r['pasi_optimizator']} pași), "
              f"{r['loturi_pe_secunda']} loturi/s ({r['simboluri_pe_secunda']} simboluri/s), PyTorch {r['memorie_pytorch_max_mb']} MB, placa "
              f"{r['placa']['memorie_max_mb']} MB, {r['placa']['temperatura_max']} °C; pierderea: primul lot "
              f"{r['pierdere']['primul_lot']}, primele 100 {r['pierdere']['media_primilor_100_loturi']}, ultimele 100 "
              f"{r['pierdere']['media_ultimilor_100_loturi']}" + (f"; OPRITĂ: {r['oprita']}" if r["oprita"] else ""),
              flush=True)
    print(f"Salvat în {iesire}", flush=True)
    return 1 if any(r["oprita"] for r in rulari) else 0


if __name__ == "__main__":
    raise SystemExit(main())
