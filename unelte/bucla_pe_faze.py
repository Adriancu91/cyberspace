"""Bucla de auto-îmbunătățire cinstită, în două faze: cele două feluri de comparații nu se amestecă în aceeași decizie.

Faza 1, arhitecturile (config/laptop_bucla.toml, linia „bucla_arhitecturi”): fiecare arhitectură din listă pornește de
la zero și are același timp (10 minute); Kronos o compară doar cu celelalte arhitecturi pornite de la zero. Starea de la
final a fiecăreia se păstrează (lucru/bucla_cinstita/arhitecturi/).
Faza 2, lotul și rata (config/laptop_bucla_lot_rata.toml): starea arhitecturii câștigătoare se copiază o dată
(lucru/bucla_cinstita/stari_de_pornire/din_<nr.>.pt), iar toate experimentele pornesc din ea, câte 5 minute, pe linia lor
(„bucla_lot_rata_din_<nr.>”): Kronos le compară doar între ele. Primul e rețeta câștigătoare neschimbată, ca reper.
Faza 2 primește timpul rămas din --minute (câte experimente încap).
Butonul de oprire (python -m kronos opreste --config config/laptop_bucla.toml) oprește oricare fază. Se poate relua:
fiecare fază continuă din jurnal, fără să repete ce s-a încercat.

    python unelte/bucla_pe_faze.py --minute 60

Rezumatul (care arhitectură câștigă la 10 minute; lotul și rata din aceeași stare): pe ecran și în
lucru/bucla_cinstita/rezultat_<data>.json.
"""

from __future__ import annotations

import argparse
import json
import shutil
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
from kronos.orchestrator import Orchestrator  # noqa: E402

ARHITECTURA = ("n_straturi", "n_capete", "n_emb", "context")
SECUNDE_IN_PLUS = 20  # pe experiment, pe lângă antrenare: testul rapid, pregătirea, examenul, salvarea


def rand(fisa: dict[str, Any], scor_principal: str) -> dict[str, Any]:
    """Ce arată rezumatul despre un experiment."""
    model = (fisa.get("setari") or {}).get("model", {})
    statistici = fisa.get("statistici_antrenare") or {}
    pasi = statistici.get("pasi")
    return {
        "experiment": fisa["id"],
        "propunere": fisa["propunere"]["descriere"],
        "arhitectura": f"{model.get('n_straturi')}×{model.get('n_emb')}, context {model.get('context')}",
        "lot": model.get("lot"),
        "rata_invatare": model.get("rata_invatare"),
        "parametri_m": round(statistici["parametri"] / 1e6, 1) if statistici.get("parametri") else None,
        "pasi": pasi,
        "simboluri_m": round(pasi * model["lot"] * model["context"] / 1e6, 1) if pasi else None,
        "continuat": statistici.get("continuat"),
        "memorie_rezervata_mb": statistici.get("memorie_rezervata_mb"),
        "scor": (fisa.get("scoruri") or {}).get(scor_principal),
        "decizie": fisa.get("decizie"),
        "motiv": fisa.get("motiv"),
    }


def _scor(r: dict[str, Any]) -> str:
    return f"{r['scor']:.4f}" if isinstance(r["scor"], (int, float)) else "–"


def tabel_arhitecturi(randuri: list[dict[str, Any]]) -> list[str]:
    linii = [f"{'nr':>4}  {'arhitectura':<22} {'parametri':>9}  {'pași':>6}  {'simboluri':>9}  {'val_bpb':>7}  decizie"]
    for r in randuri:
        linii.append(f"{r['experiment']:>4}  {r['arhitectura']:<22} {str(r['parametri_m']) + ' M':>9}  {r['pasi'] or 0:>6,}  "
                     f"{str(r['simboluri_m']) + ' M':>9}  {_scor(r):>7}  {r['decizie']}")
    return linii


def tabel_lot_rata(randuri: list[dict[str, Any]]) -> list[str]:
    linii = [f"{'nr':>4}  {'lot':>4}  {'rata':>8}  {'pași':>6}  {'val_bpb':>7}  decizie"]
    for r in randuri:
        linii.append(f"{r['experiment']:>4}  {r['lot']:>4}  {r['rata_invatare']:>8g}  {r['pasi'] or 0:>6,}  {_scor(r):>7}  "
                     f"{r['decizie']}")
    return linii


def configurare_faza_2(config_b: Any, castigator: dict[str, Any], pornire: Path) -> None:
    """Faza 2 pe linia ei, cu arhitectura, lotul și rata câștigătoare, din starea de pornire copiată."""
    reteta = castigator["setari"]["model"]
    config_b.nume = f"{config_b.nume}_din_{castigator['id']}"
    config_b.porturi["model"]["setari"] = {
        **config_b.setari_port("model"),
        **{k: reteta[k] for k in (*ARHITECTURA, "lot", "rata_invatare")},
        "stare_de_pornire": str(pornire),
    }


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Bucla cinstită: arhitecturile de la zero, apoi lotul și rata din aceeași stare.")
    parser.add_argument("--config-arhitecturi", default="config/laptop_bucla.toml", help="faza 1")
    parser.add_argument("--config-lot-rata", default="config/laptop_bucla_lot_rata.toml", help="faza 2")
    parser.add_argument("--minute", type=float, default=60, help="timpul pentru amândouă fazele, în minute")
    args = parser.parse_args(argv)
    inceput = time.monotonic()
    eticheta = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Faza 1: arhitecturile, de la zero, la timp egal. Cercetătorul se oprește singur când a încercat toată lista.
    config_a = citeste_config(args.config_arhitecturi)
    o_a = Orchestrator(config_a)
    scor_principal, mai_mic = o_a.examen.scor_principal, o_a.examen.mai_mic_e_mai_bun
    print(f"Faza 1: arhitecturile, de la zero, câte {config_a.buget_antrenare_secunde / 60:g} minute "
          f"(linia „{config_a.nume}”).", flush=True)
    o_a.ruleaza()
    del o_a
    jurnal = Jurnal(config_a.director_lucru)
    castigator = jurnal.cel_mai_bun(config_a.nume, scor_principal, mai_mic)
    if castigator is None:
        print("Faza 1 n-are niciun experiment reușit: nu am din ce stare porni faza 2.", flush=True)
        return 1
    stare = ((castigator.get("dupa_examen") or {}).get("continuare") or {}).get("fisier")
    if not stare or not Path(stare).exists():
        print(f"Starea arhitecturii câștigătoare (#{castigator['id']}) lipsește: nu pornesc faza 2.", flush=True)
        return 1
    pornire = config_a.director_lucru / "bucla_cinstita" / "stari_de_pornire" / f"din_{castigator['id']}.pt"
    if not pornire.exists():  # o copie, ca toate experimentele fazei 2 să pornească din exact aceeași stare
        pornire.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(stare, pornire)

    # Faza 2: lotul și rata, toate din aceeași stare, în timpul rămas.
    config_b = citeste_config(args.config_lot_rata)
    configurare_faza_2(config_b, castigator, pornire)
    ramas = args.minute * 60 - (time.monotonic() - inceput)
    incap = int(ramas // (config_b.buget_antrenare_secunde + SECUNDE_IN_PLUS))
    print(f"\nFaza 2: lotul și rata, din starea lui #{castigator['id']} ({pornire.name}), câte "
          f"{config_b.buget_antrenare_secunde / 60:g} minute (linia „{config_b.nume}”); încap {max(incap, 0)} experimente.",
          flush=True)
    if incap >= 1:
        o_b = Orchestrator(config_b)
        o_b.ruleaza(incap - 1 if o_b.cel_mai_bun is None else incap)  # pe o linie nouă, primul e reperul
        del o_b

    # Rezumatul.
    faza1 = [rand(f, scor_principal) for f in jurnal.istoric(config_a.nume)]
    faza2 = [rand(f, scor_principal) for f in jurnal.istoric(config_b.nume)]
    castigator_2 = jurnal.cel_mai_bun(config_b.nume, scor_principal, mai_mic)
    print("\n=== Faza 1: arhitecturile, de la zero, la timp egal (val_bpb, mai mic = mai bine) ===")
    print("\n".join(tabel_arhitecturi(faza1)))
    r1 = rand(castigator, scor_principal)
    print(f"Câștigă: #{r1['experiment']}, {r1['arhitectura']}, val_bpb {_scor(r1)}.")
    if faza2:
        print(f"\n=== Faza 2: lotul și rata, toate din starea lui #{castigator['id']} ===")
        print("\n".join(tabel_lot_rata(faza2)))
        if castigator_2 is not None:
            r2 = rand(castigator_2, scor_principal)
            print(f"Câștigă: #{r2['experiment']}, lot {r2['lot']}, rata {r2['rata_invatare']:g}, val_bpb {_scor(r2)}.")
    minute = (time.monotonic() - inceput) / 60
    iesire = config_a.director_lucru / "bucla_cinstita" / f"rezultat_{eticheta}.json"
    iesire.parent.mkdir(parents=True, exist_ok=True)
    iesire.write_text(json.dumps({
        "data": datetime.now().isoformat(timespec="seconds"), "minute": round(minute, 1),
        "linia_1": config_a.nume, "linia_2": config_b.nume, "stare_de_pornire": str(pornire),
        "faza1": faza1, "castigator_1": castigator["id"], "faza2": faza2,
        "castigator_2": castigator_2["id"] if castigator_2 else None,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nGata în {minute:.0f} minute. Salvat în {iesire}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
