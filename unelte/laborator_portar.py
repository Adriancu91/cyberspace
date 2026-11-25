"""S139 (C-167, laboratorul, a patra probă): „portarul” (amestecul de adâncimi) — exact rețeta S135 (0), de la zero, după
ceas; singura diferență: `module/model_portar.py` cu portar la straturile 2, 4, 6, 8, 10, 12 (capacitate 0,5).

Comun cu (0) (`unelte/laborator_trepte.py`): rețeaua lui #513 (12 straturi, 12 capete, n_emb 768, context 512, vocabular
16.384, capul legat), sămânța 1163 (aceeași inițializare a părții comune, aceleași loturi trase uniform), datele doar W2
(`lucru/bucati/w2_amestec_be12`), lot 12 × 512 × adunare 8, AdamW (0,9/0,999, eps 1e-8, scăderea greutăților 0,1,
tăierea 1,0), bf16 cu autocast pe placă, vârf 6e-4 (încălzire 3 min, constantă, răcire liniară la 0 în ultimele 15),
60 de minute pe ceas, încorporările din N(0; 0,02). Selectorii primesc aceeași rată ca restul.

În `progres.csv`, în plus față de S135: simboluri/s (de la rândul trecut), eroarea BCE a selectorului, partea de
simboluri care ar fi alese în modul cauzal (pe loturile de antrenare de la rândul trecut) și potrivirea alegerii cauzale
cu top-k. La sfârșit: modelul DOAR în `<iesire>/model.pt` (nu în jurnal, nu în lucru/stocare/, nu în interfață), apoi
examenele (funcția `examene` din `unelte/laborator_trepte.py`, neschimbată) **în modul cauzal**; separat, partea aleasă
în modul cauzal la examenul de română (o trecere în plus a examenului de română, fără R1) și, doar informativ, româna și
`examen_bpb` în modul top-k (necauzal — nu decide). Paznicul: peste 7.000 MB sau 83 °C → oprește.

    python -X utf8 unelte/laborator_portar.py --minute 60 --dispozitiv cuda --iesire lucru/laborator/S139_P
    # proba pe procesor (model mic):
    python -X utf8 unelte/laborator_portar.py --minute 2 --dispozitiv cpu --straturi 2 --capete 2 --n-emb 64 --lot 4 \
        --adunare 1 --straturi-portar 2 --incalzire-minute 0.2 --racire-minute 0.5 --iesire lucru/cascada/S139_proba/proba
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

from unelte import laborator_trepte as lt  # noqa: E402

SAMANTA = lt.SAMANTA
COLOANE = lt.COLOANE + ["simboluri_pe_s", "bce", "parte_aleasa_cauzal", "potrivire_topk", "parte_trecuta"]
PARTE_MIN, PARTE_MAX = 0.35, 0.65


def cale_absoluta(cale: str) -> Path:
    p = Path(cale)
    return p if p.is_absolute() else RADACINA / p


def viteza_intre(randuri: list[dict[str, Any]], de_la: float = 5.0, pana_la: float = 45.0) -> dict[str, Any] | None:
    """Simboluri/s între primul rând cu minutul ≥ de_la și ultimul cu minutul ≤ pana_la (din progres.csv)."""
    alese = [r for r in randuri if de_la <= float(r["minut"]) <= pana_la]
    if len(alese) < 2:
        return None
    a, b = alese[0], alese[-1]
    secunde = float(b["secunde"]) - float(a["secunde"])
    simboluri = int(b["simboluri_vazute"]) - int(a["simboluri_vazute"])
    return {"de_la_minut": float(a["minut"]), "pana_la_minut": float(b["minut"]), "secunde": round(secunde, 1),
            "simboluri": simboluri, "simboluri_pe_s": round(simboluri / secunde, 1) if secunde > 0 else None}


def citeste_progres(cale: Path) -> list[dict[str, Any]]:
    with cale.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def examene_portar(model: Any, date: Any, cu_r1: bool) -> dict[str, Any]:
    """Examenele (0) în modul cauzal, apoi partea aleasă la română (cauzal) și cifrele informative în modul top-k."""
    import torch

    from module.examen_bpb import ExamenBpb
    from module.examen_romana import ExamenRomana

    retea = model.retea
    retea.mod_examen = "cauzal"
    retea.goleste_statistici()
    r: dict[str, Any] = {"cauzal": lt.examene(model, date, cu_r1=cu_r1)}
    r["statistici_toate_examenele"] = retea.citeste_statistici()
    if retea.selectori is None:
        return r
    with torch.no_grad():
        t = time.perf_counter()
        retea.goleste_statistici()
        romana = ExamenRomana(caractere=100_000, cu_r1=False).examineaza(model, date)
        r["romana_cauzal_parte_aleasa"] = {**retea.citeste_statistici(), "romana_bpb": romana.get("romana_bpb"),
                                           "secunde": round(time.perf_counter() - t, 1)}
        t = time.perf_counter()
        retea.mod_examen = "topk"
        retea.goleste_statistici()
        try:
            romana_topk = ExamenRomana(caractere=100_000, cu_r1=False).examineaza(model, date)
            bpb_topk = ExamenBpb().examineaza(model, date)
        finally:
            retea.mod_examen = "cauzal"
        r["informativ_topk"] = {"nota": "modul top-k se uită la scorurile de după: NU e cinstit, NU decide",
                                "romana_bpb": romana_topk.get("romana_bpb"), "val_bpb": bpb_topk.get("val_bpb"),
                                "statistici": retea.citeste_statistici(), "secunde": round(time.perf_counter() - t, 1)}
    parte = r["romana_cauzal_parte_aleasa"]["parte_aleasa_cauzal"]
    r["validitate_parte_aleasa"] = {"parte": parte, "interval": [PARTE_MIN, PARTE_MAX],
                                    "valida": parte is not None and PARTE_MIN <= parte <= PARTE_MAX}
    return r


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--minute", type=float, default=60.0)
    p.add_argument("--samanta", type=int, default=SAMANTA)
    p.add_argument("--dispozitiv", choices=["cpu", "cuda"], default="cuda")
    p.add_argument("--iesire", required=True)
    p.add_argument("--fara-portar", action="store_true", help="portar = nu (= rețeta (0)); doar la probe")
    p.add_argument("--capacitate", type=float, default=0.5)
    p.add_argument("--straturi-portar", type=int, nargs="+", default=None,
                   help="numerotate de la 1; implicit straturile pare (2, 4, …, 12 la 12 straturi)")
    p.add_argument("--pondere-bce", type=float, default=0.01)
    p.add_argument("--straturi", type=int, default=12)
    p.add_argument("--capete", type=int, default=12)
    p.add_argument("--n-emb", type=int, default=768)
    p.add_argument("--context", type=int, default=512)
    p.add_argument("--lot", type=int, default=12)
    p.add_argument("--adunare", type=int, default=8)
    p.add_argument("--rata", type=float, default=lt.RATA_VARF)
    p.add_argument("--incalzire-minute", type=float, default=3.0)
    p.add_argument("--racire-minute", type=float, default=15.0)
    p.add_argument("--secunde-intre-randuri", type=float, default=60.0)
    p.add_argument("--fara-r1", action="store_true", help="fără R1 (doar la probe; la (P) R1 se măsoară)")
    p.add_argument("--fara-examene", action="store_true", help="fără examene (doar la probe)")
    p.add_argument("--memorie-max-gb", type=float, default=5.9)
    a = p.parse_args(argv)
    iesire = cale_absoluta(a.iesire)
    if iesire.exists():
        raise SystemExit(f"{iesire} există deja: nu scriu peste el")
    straturi_portar = a.straturi_portar or list(range(2, a.straturi + 1, 2))

    import torch

    if a.dispozitiv == "cuda":
        if not torch.cuda.is_available():
            raise SystemExit("placa nu e disponibilă (CUDA)")
        total = torch.cuda.get_device_properties(0).total_memory
        torch.cuda.set_per_process_memory_fraction(min(1.0, a.memorie_max_gb * 2**30 / total))

    from module.date_bucati import DateBucati
    from module.model_portar import ModelPortar
    from module.tokenizer_bpe import TokenizerBPE
    from unelte.banc_antrenare import versiuni

    a.reteta, a.k, a.minute_bucati = 0, 1, 0.0  # rețeta (0): setările comune identice cu S135 (0)
    setari = lt.setari_model(a)
    setari_portar = {} if a.fara_portar else {"portar": True, "capacitate": a.capacitate,
                                              "straturi_portar": straturi_portar, "pondere_bce": a.pondere_bce}
    model = ModelPortar(**setari, **setari_portar)
    date = DateBucati(str(cale_absoluta(lt.BUCATI)), str(cale_absoluta(lt.VALIDARE)), str(cale_absoluta(lt.TOKENIZER)))
    model.tok = TokenizerBPE.incarca(model.cale_tokenizer)
    sir = model._sirul(date)
    model._pregateste_reteaua()
    assert model.retea is not None
    retea = model.retea
    iesire.mkdir(parents=True)
    citeste, verifica = lt.paznic()
    pe_placa = a.dispozitiv == "cuda"
    placa_max = {"memorie_mb": 0.0, "temperatura": 0.0}
    fisier_csv = (iesire / "progres.csv").open("w", newline="", encoding="utf-8")
    scriitor = csv.DictWriter(fisier_csv, fieldnames=COLOANE)
    scriitor.writeheader()
    inainte = {"secunde": 0.0, "simboluri": 0}

    def la_fiecare(s: dict[str, Any]) -> str | None:
        smi = citeste() if pe_placa else None
        if smi:
            for k in placa_max:
                placa_max[k] = max(placa_max[k], smi[k])
        secunde = s["secunde"] - inainte["secunde"]
        viteza = (s["simboluri_vazute"] - inainte["simboluri"]) / secunde if secunde > 0 else float("nan")
        inainte.update(secunde=s["secunde"], simboluri=s["simboluri_vazute"])
        st = retea.citeste_statistici()
        retea.goleste_statistici()
        bce = sum(model.bce_recente) / len(model.bce_recente) if model.bce_recente else None
        model.bce_recente = []

        def rot(v: float | None, n: int = 4) -> Any:
            return "" if v is None else round(v, n)

        scriitor.writerow({"minut": round(s["secunde"] / 60, 2), "secunde": round(s["secunde"], 1), "faza": s["faza"],
                           "pasi": s["pasi"], "pasi_bucati": s["pasi_bucati"], "pasi_simboluri": s["pasi_simboluri"],
                           "simboluri_vazute": s["simboluri_vazute"], "eroare": round(s["pierdere"], 5),
                           "eroare_ultim_pas": round(s["pierdere_ultim_pas"], 5),
                           "norma_gradient": round(s["norma_gradient"], 4), "rata": f"{s['rata']:.3e}",
                           "memorie_mb": smi["memorie_mb"] if smi else "", "temperatura": smi["temperatura"] if smi else "",
                           "simboluri_pe_s": round(viteza, 1), "bce": rot(bce, 5),
                           "parte_aleasa_cauzal": rot(st["parte_aleasa_cauzal"]),
                           "potrivire_topk": rot(st["potrivire_topk"]), "parte_trecuta": rot(st["parte_trecuta"])})
        fisier_csv.flush()
        print(f"[{s['secunde'] / 60:6.2f} min] pași {s['pasi']:6d}  eroare {s['pierdere']:.4f}  {viteza:8.0f} simb/s  "
              f"bce {rot(bce)}  cauzal {rot(st['parte_aleasa_cauzal'])}  potrivire {rot(st['potrivire_topk'])}  "
              f"{(smi or {}).get('memorie_mb', '-')} MB {(smi or {}).get('temperatura', '-')} °C", flush=True)
        return verifica(smi)

    if pe_placa:
        torch.cuda.reset_peak_memory_stats()
    smi_inainte = citeste() if pe_placa else None
    parametri = sum(t.numel() for t in retea.parameters())
    parametri_selectori = sum(t.numel() for t in retea.selectori.parameters()) if retea.selectori is not None else 0
    print(f"S139 (P): {a.minute} min, portar {'oprit' if a.fara_portar else f'la straturile {straturi_portar}'}, "
          f"capacitate {a.capacitate}, {parametri:,} parametri (selectori {parametri_selectori}), {a.dispozitiv}",
          flush=True)
    try:
        bucla = model.bucla(sir, a.minute * 60.0, samanta_loturi=a.samanta, la_fiecare=la_fiecare,
                            secunde_intre_semnale=a.secunde_intre_randuri)
    finally:
        fisier_csv.close()
    rezultat: dict[str, Any] = {
        "ce_este": "S139 laboratorul, proba (P): rețeta S135 (0) + portarul (amestecul de adâncimi) "
                   "(nu intră în jurnal/interfață/export)",
        "argumente": vars(a), "setari_model": {**setari, **setari_portar, "cale_tokenizer": lt.TOKENIZER},
        "parametri": parametri, "parametri_selectori": parametri_selectori,
        "date": {**date.descriere(), "director": lt.BUCATI,
                 "nota": "doar textul W2 (amestecul W2 tokenizat), fără conversații și fără hrană"},
        "placa_inainte": smi_inainte, "bucla": bucla, "placa_max_nvidia_smi": placa_max if pe_placa else None,
        "viteza_minutele_5_45": viteza_intre(citeste_progres(iesire / "progres.csv")),
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
        rezultat["examene"] = examene_portar(model, date, cu_r1=not a.fara_r1)
        if pe_placa:
            smi = citeste()
            if smi:
                for k in placa_max:
                    placa_max[k] = max(placa_max[k], smi[k])
    rezultat["versiuni"] = versiuni(torch.device(a.dispozitiv))
    (iesire / "rezultat.json").write_text(json.dumps(rezultat, ensure_ascii=False, indent=1), encoding="utf-8")
    ex = (rezultat.get("examene") or {}).get("cauzal") or {}
    print(json.dumps({"iesire": iesire.as_posix(), "pasi": bucla["pasi"], "simboluri_vazute": bucla["simboluri_vazute"],
                      "pierdere_finala": bucla["pierdere_finala"], "oprit": bucla["oprit"],
                      "viteza_5_45": (rezultat["viteza_minutele_5_45"] or {}).get("simboluri_pe_s"),
                      "romana_bpb": (ex.get("romana") or {}).get("romana_bpb"),
                      "r1_instructiuni": (ex.get("romana") or {}).get("r1_instructiuni"),
                      "val_bpb": (ex.get("examen_bpb") or {}).get("val_bpb"),
                      "validitate": (rezultat.get("examene") or {}).get("validitate_parte_aleasa"),
                      "placa_max": placa_max if pe_placa else None}, ensure_ascii=False))
    return 2 if bucla["oprit"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
