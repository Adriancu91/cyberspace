"""S135 (C-163): laboratorul treptelor — o antrenare DE LA ZERO, după ceas, cu `module/model_trepte.py`.

Două rețete, singura diferență fiind faza pe bucăți:
- (0) `--reteta 0`: rețeta de azi, pe simboluri tot timpul (K = 1);
- (1) `--reteta 1 --k 4 --minute-bucati 40`: primele 40 de minute pe bucăți de K simboluri, apoi pe simboluri.

Comun: rețeaua lui #513 (12 straturi, 12 capete, n_emb 768, context 512, vocabular 16.384, `date/ws/bpe_16384.json`,
capul legat), sămânța 1163 (aceeași inițializare și aceleași loturi trase la ambele), datele = doar textul W2 (amestecul
W2 gata tokenizat: `lucru/bucati/w2_amestec_be12`, fără conversații, fără hrană), lot 12 × 512 × adunare 8 = 49.152
simboluri pe pasul optimizatorului, AdamW (0,9/0,999, eps 1e-8, scăderea greutăților 0,1, tăierea 1,0), bf16 cu autocast
pe placă, rata de vârf 6e-4 după ceas (încălzire 3 min, constantă, răcire liniară la 0 în ultimele 15 min), încorporările
din N(0; 0,02) (ca `model_gpt_cod`, S61).

La fiecare minut, `progres.csv` (minutul, faza, pașii, simbolurile văzute, eroarea, memoria plăcii, temperatura). La
sfârșit: modelul DOAR în `<iesire>/model.pt` (nu în jurnalul de experimente, nu în lucru/stocare/, nu în interfață),
apoi examenele (doar folosite): `module/examen_romana.py` (română curat `romana_bpb` + R1 pe setul ascuns),
`module/examen_bpb.py` (`val_bpb`, martorul) — și `rezultat.json`. Paznicul: peste 7.000 MB sau 83 °C → oprește.

    python -X utf8 unelte/laborator_trepte.py --reteta 0 --minute 60 --dispozitiv cuda --iesire lucru/laborator/S135_0
    python -X utf8 unelte/laborator_trepte.py --reteta 1 --minute 60 --k 4 --minute-bucati 40 --dispozitiv cuda \
        --iesire lucru/laborator/S135_1
    # proba pe procesor (model mic):
    python -X utf8 unelte/laborator_trepte.py --reteta 1 --minute 2 --minute-bucati 1 --dispozitiv cpu \
        --straturi 2 --capete 2 --n-emb 64 --lot 4 --adunare 1 --iesire lucru/cascada/S135_proba/proba_1
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parents[1]
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

SAMANTA = 1163
BUCATI = "lucru/bucati/w2_amestec_be12"
VALIDARE = "date/tinystories_r2/validare.txt"
TOKENIZER = "date/ws/bpe_16384.json"
RATA_VARF = 6e-4
MEMORIE_MAXIMA_MB = 7000
TEMPERATURA_MAXIMA = 83
COLOANE = ["minut", "secunde", "faza", "pasi", "pasi_bucati", "pasi_simboluri", "simboluri_vazute", "eroare",
           "eroare_ultim_pas", "norma_gradient", "rata", "memorie_mb", "temperatura"]


def setari_model(a: argparse.Namespace) -> dict[str, Any]:
    """Setările modelului pentru rețeta aleasă (singura diferență între (0) și (1): k_bucata și minute_bucati)."""
    return {
        "n_straturi": a.straturi, "n_capete": a.capete, "n_emb": a.n_emb, "context": a.context, "lot": a.lot,
        "rata_invatare": a.rata, "dropout": 0.0, "tokenizer": "bpe", "cale_tokenizer": str(RADACINA / TOKENIZER),
        "dispozitiv": a.dispozitiv, "samanta": a.samanta, "adunare_loturi": a.adunare, "abatere_incorporari": 0.02,
        "incalzire_secunde": a.incalzire_minute * 60.0, "racire_secunde": a.racire_minute * 60.0,
        "k_bucata": a.k if a.reteta == 1 else 1, "minute_bucati": a.minute_bucati if a.reteta == 1 else 0.0,
    }


def paznic(memorie_maxima_mb: float = MEMORIE_MAXIMA_MB, temperatura_maxima: float = TEMPERATURA_MAXIMA):
    """Întoarce (citeste, verifica): citirea plăcii (nvidia-smi) și motivul opririi, dacă trece de limite."""
    from unelte.banc_antrenare import nvidia_smi

    def verifica(smi: dict[str, float] | None) -> str | None:
        if not smi:
            return None
        if smi["memorie_mb"] > memorie_maxima_mb:
            return f"memoria plăcii {smi['memorie_mb']:.0f} MB > {memorie_maxima_mb} MB"
        if smi["temperatura"] > temperatura_maxima:
            return f"placa la {smi['temperatura']:.0f} °C > {temperatura_maxima} °C"
        return None

    return nvidia_smi, verifica


def examene(model: Any, date: Any, cu_r1: bool) -> dict[str, Any]:
    """Aceleași examene ca la verdictele de azi, doar folosite: română curat (+ R1), apoi `examen_bpb` (martorul)."""
    import torch

    from module.examen_bpb import ExamenBpb
    from module.examen_romana import ExamenRomana

    r: dict[str, Any] = {}
    with torch.no_grad():
        t = time.perf_counter()
        r["romana"] = ExamenRomana(caractere=100_000, cu_r1=cu_r1).examineaza(model, date)
        r["examen_bpb"] = ExamenBpb().examineaza(model, date)
        r["secunde"] = round(time.perf_counter() - t, 1)
    return r


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--reteta", type=int, choices=[0, 1], required=True)
    p.add_argument("--minute", type=float, default=60.0)
    p.add_argument("--k", type=int, default=4)
    p.add_argument("--minute-bucati", type=float, default=40.0)
    p.add_argument("--samanta", type=int, default=SAMANTA)
    p.add_argument("--dispozitiv", choices=["cpu", "cuda"], default="cuda")
    p.add_argument("--iesire", required=True)
    p.add_argument("--straturi", type=int, default=12)
    p.add_argument("--capete", type=int, default=12)
    p.add_argument("--n-emb", type=int, default=768)
    p.add_argument("--context", type=int, default=512)
    p.add_argument("--lot", type=int, default=12)
    p.add_argument("--adunare", type=int, default=8)
    p.add_argument("--rata", type=float, default=RATA_VARF)
    p.add_argument("--incalzire-minute", type=float, default=3.0)
    p.add_argument("--racire-minute", type=float, default=15.0)
    p.add_argument("--secunde-intre-randuri", type=float, default=60.0)
    p.add_argument("--fara-r1", action="store_true", help="fără R1 (doar la probe; la (0) și (1) R1 se măsoară)")
    p.add_argument("--fara-examene", action="store_true", help="fără examene (doar la probe)")
    p.add_argument("--memorie-max-gb", type=float, default=5.9,
                   help="pe placă: plafonul PyTorch (set_per_process_memory_fraction); nvidia-smi rămâne sub 7.000 MB")
    a = p.parse_args(argv)
    iesire = Path(a.iesire)
    if not iesire.is_absolute():
        iesire = RADACINA / iesire
    if iesire.exists():
        raise SystemExit(f"{iesire} există deja: nu scriu peste el")
    if a.reteta == 1 and (a.k < 2 or a.minute_bucati <= 0):
        raise SystemExit("rețeta 1 cere --k ≥ 2 și --minute-bucati > 0")

    import torch

    if a.dispozitiv == "cuda":
        if not torch.cuda.is_available():
            raise SystemExit("placa nu e disponibilă (CUDA)")
        total = torch.cuda.get_device_properties(0).total_memory
        torch.cuda.set_per_process_memory_fraction(min(1.0, a.memorie_max_gb * 2**30 / total))

    from module.date_bucati import DateBucati
    from module.model_trepte import ModelTrepte
    from unelte.banc_antrenare import versiuni

    setari = setari_model(a)
    model = ModelTrepte(**setari)
    date = DateBucati(str(RADACINA / BUCATI), str(RADACINA / VALIDARE), str(RADACINA / TOKENIZER))
    from module.tokenizer_bpe import TokenizerBPE

    model.tok = TokenizerBPE.incarca(model.cale_tokenizer)
    sir = model._sirul(date)
    model._pregateste_reteaua()
    assert model.retea is not None
    iesire.mkdir(parents=True)
    citeste, verifica = paznic()
    pe_placa = a.dispozitiv == "cuda"
    placa_max = {"memorie_mb": 0.0, "temperatura": 0.0}
    fisier_csv = (iesire / "progres.csv").open("w", newline="", encoding="utf-8")
    scriitor = csv.DictWriter(fisier_csv, fieldnames=COLOANE)
    scriitor.writeheader()

    def la_fiecare(s: dict[str, Any]) -> str | None:
        smi = citeste() if pe_placa else None
        if smi:
            for k in placa_max:
                placa_max[k] = max(placa_max[k], smi[k])
        scriitor.writerow({"minut": round(s["secunde"] / 60, 2), "secunde": round(s["secunde"], 1), "faza": s["faza"],
                           "pasi": s["pasi"], "pasi_bucati": s["pasi_bucati"], "pasi_simboluri": s["pasi_simboluri"],
                           "simboluri_vazute": s["simboluri_vazute"], "eroare": round(s["pierdere"], 5),
                           "eroare_ultim_pas": round(s["pierdere_ultim_pas"], 5),
                           "norma_gradient": round(s["norma_gradient"], 4), "rata": f"{s['rata']:.3e}",
                           "memorie_mb": smi["memorie_mb"] if smi else "", "temperatura": smi["temperatura"] if smi else ""})
        fisier_csv.flush()
        print(f"[{s['secunde'] / 60:6.2f} min] {s['faza']:9s} pași {s['pasi']:6d}  eroare {s['pierdere']:.4f}  "
              f"{(smi or {}).get('memorie_mb', '-')} MB {(smi or {}).get('temperatura', '-')} °C", flush=True)
        return verifica(smi)

    if pe_placa:
        torch.cuda.reset_peak_memory_stats()
    smi_inainte = citeste() if pe_placa else None
    print(f"S135 rețeta ({a.reteta}): {a.minute} min, K = {setari['k_bucata']}, bucăți {setari['minute_bucati']} min, "
          f"{sum(t.numel() for t in model.retea.parameters()):,} parametri, {a.dispozitiv}", flush=True)
    try:
        bucla = model.bucla(sir, a.minute * 60.0, samanta_loturi=a.samanta, la_fiecare=la_fiecare,
                            secunde_intre_semnale=a.secunde_intre_randuri)
    finally:
        fisier_csv.close()
    rezultat: dict[str, Any] = {
        "ce_este": "S135 laboratorul treptelor: o antrenare de la zero, după ceas (nu intră în jurnal/interfață/export)",
        "reteta": a.reteta, "argumente": vars(a), "setari_model": {**setari, "cale_tokenizer": TOKENIZER},
        "parametri": sum(t.numel() for t in model.retea.parameters()),
        "date": {**date.descriere(), "director": BUCATI,
                 "nota": "doar textul W2 (amestecul W2 tokenizat), fără conversații și fără hrană"},
        "placa_inainte": smi_inainte, "bucla": bucla, "placa_max_nvidia_smi": placa_max if pe_placa else None,
    }
    if pe_placa:
        rezultat["memorie_pytorch"] = {"max_memory_allocated_mb": torch.cuda.max_memory_allocated() / 2**20,
                                       "max_memory_reserved_mb": torch.cuda.max_memory_reserved() / 2**20}
    rezultat["model"] = model.salveaza(str(iesire / "model"))
    if bucla["oprit"]:
        rezultat["examene"] = None
        print(f"OPRIT: {bucla['oprit']}", file=sys.stderr)
    elif not a.fara_examene:
        if pe_placa:
            torch.cuda.empty_cache()
        rezultat["examene"] = examene(model, date, cu_r1=not a.fara_r1)
        if pe_placa:
            smi = citeste()
            if smi:
                for k in placa_max:
                    placa_max[k] = max(placa_max[k], smi[k])
    rezultat["versiuni"] = versiuni(torch.device(a.dispozitiv))
    (iesire / "rezultat.json").write_text(json.dumps(rezultat, ensure_ascii=False, indent=1), encoding="utf-8")
    ex = rezultat.get("examene") or {}
    print(json.dumps({"iesire": iesire.as_posix(), "pasi": bucla["pasi"], "simboluri_vazute": bucla["simboluri_vazute"],
                      "pierdere_finala": bucla["pierdere_finala"], "oprit": bucla["oprit"],
                      "romana_bpb": (ex.get("romana") or {}).get("romana_bpb"),
                      "r1_instructiuni": (ex.get("romana") or {}).get("r1_instructiuni"),
                      "val_bpb": (ex.get("examen_bpb") or {}).get("val_bpb"), "placa_max": placa_max if pe_placa else None},
                     ensure_ascii=False))
    return 2 if bucla["oprit"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
