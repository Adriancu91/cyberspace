"""Antrenarea lungă, peste noapte (după bucla cinstită): rețeta câștigătoare, cu continuare, câte un experiment Kronos
pe oră.

Configurarea: config/laptop_antrenare_lunga.toml (rețeta; starea în lucru/antrenare_lunga/gpt.pt). Fiecare oră e un
experiment Kronos: o oră de antrenare din starea de la finalul orei dinainte, apoi examenul oficial și salvarea stării.
Rata de învățare scade singură pe toată durata plănuită (durata_scaderii_secunde din configurare: 8 ore), nu pe fiecare
oră: încălzire în primii 100 de pași, apoi cosinus până la 10%.
Înainte de fiecare oră: pauză și răcire (până la --racire grade); paznicul verifică temperatura, memoria video și
butonul de oprire. Se poate relua: orele făcute se citesc din jurnal. Cât rulează, Windows nu intră în somn.

    python unelte/antrenare_lunga.py --ore 8
    python unelte/antrenare_lunga.py --raport      # doar tabelul și povestea, din orele făcute

Rezultatul: pe ecran și în lucru/antrenare_lunga/rezultat.json: scorul pe ore, pașii și textul văzut (în total și de
câte ori a trecut prin tot textul de antrenare), o poveste scrisă de modelul de la final.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from kronos.config import citeste_config  # noqa: E402
from kronos.jurnal import Jurnal  # noqa: E402
from kronos.registru import Registru  # noqa: E402
from unelte.compara_plasa_adaptiva import ruleaza  # noqa: E402

LITERE_PE_SIMBOL = 4.0  # măsurat pe TinyStories, cu tokenizerul BPE de 4.096 de simboluri


def tine_treaz(da: bool) -> None:
    """Windows: cât rulează, laptopul nu intră în somn (cererea se anulează oricum când procesul se termină)."""
    if sys.platform != "win32":
        return
    try:
        import ctypes

        es_continuous, es_system_required = 0x80000000, 0x00000001
        ctypes.windll.kernel32.SetThreadExecutionState(es_continuous | (es_system_required if da else 0))
    except (AttributeError, OSError):
        pass


def ore_din_jurnal(fise: list[dict[str, Any]], scor_principal: str) -> list[dict[str, Any]]:
    """Câte un rând pe oră (experimentele reușite ale liniei, în ordine), cu textul văzut adunat de la început."""
    ore: list[dict[str, Any]] = []
    simboluri_total = 0
    for fisa in fise:
        if fisa.get("decizie") not in ("pastrat", "respins"):
            continue
        model = fisa["setari"]["model"]
        s = fisa.get("statistici_antrenare") or {}
        simboluri = s["pasi"] * model["lot"] * model["context"]
        simboluri_total += simboluri
        ore.append({
            "ora": len(ore) + 1, "experiment": fisa["id"], "scor": fisa["scoruri"][scor_principal], "pasi": s["pasi"],
            "pasi_total": s.get("pasi_total"), "minute_total": s.get("minute_total"), "simboluri": simboluri,
            "simboluri_total": simboluri_total,
            "treceri_prin_text": simboluri_total / s["simboluri_antrenare"] if s.get("simboluri_antrenare") else None,
            "rata_la_final": s.get("rata_la_final"), "memorie_rezervata_mb": s.get("memorie_rezervata_mb"),
            "decizie": fisa["decizie"], "model_salvat": fisa.get("model_salvat"),
        })
    return ore


def tabel(ore: list[dict[str, Any]]) -> list[str]:
    linii = [f"{'ora':>3}  {'val_bpb':>7}  {'pași':>7}  {'pași total':>10}  {'text văzut':>10}  {'treceri':>7}  "
             f"{'rata la final':>13}  {'memorie':>8}"]
    for o in ore:
        linii.append(f"{o['ora']:>3}  {o['scor']:>7.4f}  {o['pasi']:>7,}  {o['pasi_total'] or 0:>10,}  "
                     f"{o['simboluri_total'] / 1e6:>8.0f} M  {o['treceri_prin_text'] or 0:>7.1f}  "
                     f"{o['rata_la_final'] or 0:>13.6f}  {o['memorie_rezervata_mb'] or 0:>5} MB")
    return linii


def poveste(config: Any, fisa: dict[str, Any], inceput: str, lungime: int) -> str:
    """O poveste scrisă de modelul salvat la experimentul dat (ca python -m kronos scrie)."""
    model = Registru().creeaza("model", config.porturi["model"]["modul"], fisa["setari"]["model"]).instanta
    model.incarca(fisa["model_salvat"])
    return inceput + model.genereaza(inceput, lungime)


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Antrenarea lungă: câte un experiment Kronos pe oră, cu continuare.")
    parser.add_argument("--config", default="config/laptop_antrenare_lunga.toml")
    parser.add_argument("--ore", type=int, default=8, help="câte ore de antrenare, în total (cu cele deja făcute)")
    parser.add_argument("--pauza", type=float, default=60, help="pauza dintre ore, în secunde")
    parser.add_argument("--racire", type=float, default=70, help="înainte de fiecare oră, aștept placa până la atâtea grade")
    parser.add_argument("--raport", action="store_true", help="nu antrena; doar tabelul și povestea, din orele făcute")
    parser.add_argument("--inceput", default="Once upon a time", help="începutul poveștii de la final")
    parser.add_argument("--lungime", type=int, default=600, help="câte litere scrie modelul")
    args = parser.parse_args(argv)

    config = citeste_config(args.config)
    examen = Registru().creeaza("examen", config.porturi["examen"]["modul"], config.setari_port("examen")).instanta
    jurnal = Jurnal(config.director_lucru)
    facute = len(ore_din_jurnal(jurnal.istoric(config.nume), examen.scor_principal))
    if not args.raport and facute < args.ore:
        reteta = config.setari_port("model")
        print(f"Antrenarea lungă: orele {facute + 1}–{args.ore}, rețeta {reteta['n_straturi']}×{reteta['n_emb']}, context "
              f"{reteta['context']}, lot {reteta['lot']}, rata {reteta['rata_invatare']:g} care scade pe "
              f"{reteta.get('durata_scaderii_secunde', 0) / 3600:g} ore (linia „{config.nume}”).", flush=True)
        tine_treaz(True)
        try:
            for ora in range(facute + 1, args.ore + 1):
                rulare = ruleaza(
                    config, config.nume, f"antrenare lungă, ora {ora} din {args.ore}", {"samanta": reteta.get("samanta", 0)},
                    pauza=0 if ora == facute + 1 else args.pauza, racire=args.racire,
                )
                if rulare is None:
                    break
                print(f"   ora {ora}: val_bpb {rulare['scor']:.4f}, {rulare['pasi']:,} de pași "
                      f"({rulare['pasi_pe_secunda']} pași/s), la {datetime.now():%H:%M}", flush=True)
        finally:
            tine_treaz(False)

    ore = ore_din_jurnal(jurnal.istoric(config.nume), examen.scor_principal)
    if not ore:
        print("Nicio oră făcută încă.", flush=True)
        return 1
    print("\n=== Antrenarea lungă: scorul pe ore (val_bpb, mai mic = mai bine) ===")
    print("\n".join(tabel(ore)))
    ultima = ore[-1]
    print(f"\nÎn total: {ultima['pasi_total']:,} de pași, {ultima['simboluri_total'] / 1e6:,.0f} M de simboluri văzute "
          f"(≈ {ultima['simboluri_total'] * LITERE_PE_SIMBOL / 1e9:.1f} miliarde de litere), adică de "
          f"{ultima['treceri_prin_text'] or 0:.1f} ori tot textul de antrenare.")
    cu_model = [o for o in ore if o["model_salvat"]]
    text = None
    if cu_model:
        fisa = next(f for f in jurnal.istoric(config.nume) if f["id"] == cu_model[-1]["experiment"])
        text = poveste(config, fisa, args.inceput, args.lungime)
        print(f"\nPovestea modelului de după ora {cu_model[-1]['ora']}:\n{text}")
    iesire = config.director_lucru / "antrenare_lunga" / "rezultat.json"
    iesire.parent.mkdir(parents=True, exist_ok=True)
    iesire.write_text(json.dumps({
        "data": datetime.now().isoformat(timespec="seconds"), "linie": config.nume, "reteta": config.setari_port("model"),
        "ore": ore, "litere_pe_simbol": LITERE_PE_SIMBOL,
        "poveste": {"ora": cu_model[-1]["ora"], "text": text} if text else None,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSalvat în {iesire}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
