"""Examenele noi pentru română și cod (12 octombrie 2026): un model salvat, măsurat pe validările puse deoparte.

Validările sunt 1% din fiecare sursă curățată (date/ws/curat/<sursa>/validare.txt): pe ele nu s-a antrenat nimic, nici
modelele, nici tokenizer-ul. Examenul oficial (val_bpb pe validarea TinyStories R2) NU se schimbă și nu e atins; acesta
e un examen separat, ca examenul de fapte.

Pentru fiecare validare, pe primele --caractere litere (tăiate la un text întreg):
- **bpb** (biți pe octet, ca examenul oficial): câți biți îi trebuie modelului pentru fiecare octet de text nevăzut.
  Mai mic = mai bine. Nu depinde de tokenizer, deci modele cu tokenizere diferite se compară direct.
- **bucăți corecte**: din bucățile textului, câte a ghicit modelul din prima (bucata cea mai probabilă era cea
  adevărată). Depinde de tokenizer (o bucată mare e mai greu de ghicit), deci se compară doar între modele cu același
  tokenizer.
- **octeți ghiciți**: cât din text (în octeți) stă în bucățile ghicite din prima. Se poate compara și între tokenizere.

Rezultatul: pe ecran, în lucru/examen_validari_ws/ și, doar numere, pe o linie „examen_validari_ws” din jurnalul Kronos.

    python unelte/examen_validari_ws.py --experiment 295                    # pe placa video, dacă e liberă
    python unelte/examen_validari_ws.py --experiment 295 --dispozitiv cpu   # pe procesor (cât placa antrenează)
    python unelte/examen_validari_ws.py --linie ws_w2                        # ultimul model salvat al liniei
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from kronos.jurnal import Jurnal  # noqa: E402
from unelte.validari_text import SEPARATOR, inceput_de_text  # noqa: E402,F401  (S90: mutate aici, neschimbate)
# numele din raport → validarea pusă deoparte. „povesti” e validarea examenului oficial, ca reper.
VALIDARI = {
    "povesti": "date/tinystories_r2/validare.txt",
    "romana_wikipedia": "date/ws/curat/wikipedia_ro/validare.txt",
    "romana_web": "date/ws/curat/fineweb2_ro/validare.txt",
    "romana_carti": "date/ws/curat/wikisource_ro/validare.txt",
    "traducere": "date/ws/curat/europarl_en_ro/validare.txt",
    # până pe 17 octombrie 2026 se numea „cod”, ca grupa: în jurnal, media pe cod îi suprascria nota (rândurile vechi rămân așa)
    "cod_python": "date/ws/curat/cod_stack/validare.txt",
    "cod_sarcini": "date/ws/curat/cod_instruct/validare.txt",
}
# 18 octombrie 2026 (Adrian): fabulele ies din examen (scurse în antrenare: docs/scurgeri_examen_17oct.md), iar lângă
# fiecare validare vine varianta ei curată (unelte/validari_curate.py), sub nume noi: <validare>_curat.
VALIDARI.update({f"{nume}_curat": Path(cale).with_name("validare_curata.txt").as_posix() for nume, cale in list(VALIDARI.items())})
GRUPE = {"romana": ["romana_wikipedia", "romana_web", "romana_carti"], "cod": ["cod_python", "cod_sarcini"],
         "romana_curat": ["romana_wikipedia_curat", "romana_web_curat", "romana_carti_curat"],
         "cod_curat": ["cod_python_curat", "cod_sarcini_curat"]}


def masoara(model: Any, text: str) -> dict[str, Any]:
    """bpb, bucăți corecte și octeți ghiciți pe un text. Bucățile se dau modelului ca la examenul oficial (ferestre de
    câte un context), deci prima bucată a fiecărei ferestre nu are nimic în față și nu se socotește la ghicit."""
    import torch

    octeti = len(text.encode("utf-8"))
    bpb = float(model.biti_pentru(text)) / octeti
    if getattr(model, "tok", None) is None or getattr(model, "retea", None) is None:
        return {"bpb": bpb, "octeti": octeti}
    simboluri = model.tok.codifica(text)
    idx = torch.tensor(simboluri, dtype=torch.long, device=model.dispozitiv)
    lungimi = torch.tensor([len(model.tok.octeti(s)) for s in simboluri], dtype=torch.long, device=model.dispozitiv)
    ctx = model.setari["context"]
    deodata = model.bucati_deodata(ctx, model.tok.marime)
    starturi = list(range(0, len(idx) - 1, ctx))
    intregi = [s for s in starturi if s + ctx + 1 <= len(idx)]
    rest = [s for s in starturi if s + ctx + 1 > len(idx)]
    corecte = socotite = octeti_ghiciti = octeti_socotiti = 0
    model.retea.eval()
    with torch.no_grad():
        for grup in [intregi[i: i + deodata] for i in range(0, len(intregi), deodata)] + [[s] for s in rest]:
            n = min(ctx, len(idx) - 1 - grup[0])
            x = torch.stack([idx[s: s + n] for s in grup])
            y = torch.stack([idx[s + 1: s + n + 1] for s in grup])
            cat = torch.stack([lungimi[s + 1: s + n + 1] for s in grup])
            with model._autocast():
                ghicit = model.retea(x, None).argmax(dim=-1)
            bine = ghicit == y
            corecte += int(bine.sum())
            socotite += y.numel()
            octeti_ghiciti += int((cat * bine).sum())
            octeti_socotiti += int(cat.sum())
    return {"bpb": bpb, "octeti": octeti, "bucati": len(simboluri), "octeti_pe_bucata": octeti / len(simboluri),
            "bucati_corecte": corecte / max(1, socotite), "octeti_ghiciti": octeti_ghiciti / max(1, octeti_socotiti)}


def examineaza(model: Any, caractere: int, validari: dict[str, str] | None = None) -> dict[str, dict[str, Any]]:
    rezultate: dict[str, dict[str, Any]] = {}
    for nume, cale in (validari or VALIDARI).items():
        fisier = Path(cale)
        if not fisier.exists():
            rezultate[nume] = {"lipseste": cale}
            continue
        rezultate[nume] = masoara(model, inceput_de_text(fisier, caractere))
    return rezultate


def numere(rezultate: dict[str, dict[str, Any]]) -> dict[str, float]:
    """Doar numerele, pentru jurnal: bpb_<validare>, corecte_<validare>, ghiciti_<validare>, plus mediile pe română și
    pe cod (media pe octeți a validărilor din grupă)."""
    n: dict[str, float] = {}
    for nume, r in rezultate.items():
        if "bpb" in r:
            n[f"bpb_{nume}"] = round(r["bpb"], 4)
            if "bucati_corecte" in r:
                n[f"corecte_{nume}"] = round(r["bucati_corecte"], 4)
                n[f"ghiciti_{nume}"] = round(r["octeti_ghiciti"], 4)
    for grupa, parti in GRUPE.items():
        avem = [rezultate[p] for p in parti if "bpb" in rezultate.get(p, {})]
        if avem:
            octeti = sum(r["octeti"] for r in avem)
            n[f"bpb_{grupa}"] = round(sum(r["bpb"] * r["octeti"] for r in avem) / octeti, 4)
    return n


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Examenele pentru română și cod, pe validările puse deoparte.")
    care = parser.add_mutually_exclusive_group(required=True)
    care.add_argument("--experiment", type=int, help="modelul salvat de Kronos la acest experiment")
    care.add_argument("--linie", help="ultimul model salvat de pe această linie de jurnal")
    parser.add_argument("--caractere", type=int, default=100_000, help="câte litere din fiecare validare (ca examenul oficial)")
    parser.add_argument("--dispozitiv", default="", help="ex. cpu: pe procesor, cât placa video antrenează")
    parser.add_argument("--fire", type=int, default=12, help="pe procesor: cel mult atâtea fire")
    parser.add_argument("--director-lucru", default="lucru")
    args = parser.parse_args(argv)

    import torch

    from unelte.modele_salvate import fisa_modelului, incarca_modelul

    if args.dispozitiv == "cpu":
        torch.set_num_threads(max(1, args.fire))
    jurnal = Jurnal(Path(args.director_lucru))
    fisa = fisa_modelului(jurnal, args.experiment, args.linie)
    model = incarca_modelul(fisa, args.dispozitiv)
    rezultate = examineaza(model, args.caractere)
    scoruri = {**numere(rezultate), "caractere": args.caractere}
    eticheta = datetime.now().strftime("%Y%m%d_%H%M%S")
    dosar = Path(args.director_lucru) / "examen_validari_ws"
    dosar.mkdir(parents=True, exist_ok=True)
    iesire = dosar / f"experiment_{fisa['id']}_{eticheta}.json"
    tokenizer = (fisa.get("setari", {}).get("model", {}) or {}).get("cale_tokenizer")
    iesire.write_text(json.dumps({"experiment": fisa["id"], "linie": fisa["linie"], "tokenizer": tokenizer,
                                  "dispozitiv": str(model.dispozitiv), **scoruri, "rezultate": rezultate},
                                 ensure_ascii=False, indent=1), encoding="utf-8")
    jurnal.adauga({
        "id": jurnal.urmatorul_id(), "linie": "examen_validari_ws",
        "inceput": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "propunere": {"descriere": f"examenele pentru română și cod pe validările puse deoparte, modelul experimentului "
                                   f"#{fisa['id']} (toate cifrele: {iesire.as_posix()})", "modificari": {}},
        "module": {"elev": {"experiment": fisa["id"], "linie": fisa["linie"], "tokenizer": tokenizer}},
        "decizie": "masurat", "scoruri": scoruri,
    })
    print(f"=== Examenele pe validările puse deoparte: modelul experimentului #{fisa['id']} (linia „{fisa['linie']}”, "
          f"tokenizer {tokenizer}) ===")
    print(f"{'validarea':<24} {'bpb':>7} {'bucăți corecte':>15} {'octeți ghiciți':>15} {'octeți/bucată':>14}")
    for nume, r in rezultate.items():
        if "bpb" not in r:
            print(f"{nume:<24} lipsește ({r['lipseste']})")
            continue
        print(f"{nume:<24} {r['bpb']:>7.4f} {r.get('bucati_corecte', float('nan')):>14.1%} "
              f"{r.get('octeti_ghiciti', float('nan')):>14.1%} {r.get('octeti_pe_bucata', float('nan')):>14.2f}")
    for grupa in GRUPE:
        if f"bpb_{grupa}" in scoruri:
            print(f"media pe {grupa}: bpb {scoruri[f'bpb_{grupa}']:.4f}")
    print(f"Toate cifrele: {iesire}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
