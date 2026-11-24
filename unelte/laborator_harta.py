"""S137 (laboratorul, a treia probă): „harta greutății textului” — exact rețeta S135 (0), de la zero, după ceas; singura
diferență: ferestrele vin din `module/date_harta.py` (harta „ce se mai poate învăța”, RHO-LOSS).

Două feluri de rulare:

1. **Harta de referință** (o singură dată): pierderea medie a lui #513 (doar citit) pe fiecare regiune de 1.048.576
   simboluri din W2 (`lucru/bucati/w2_amestec_be12`), pe 2 ferestre de 512 trase cu `numpy.random.default_rng(1163)`.
   Scrie `lucru/laborator/harta_ref_513.npy` + `.json` (SHA-ul datelor, sămânța, media, cele mai ușoare/grele 10 regiuni
   cu începutul textului decodat). Dacă estimarea după primele 50 de regiuni trece de `--max-minute-ref` (90), se oprește
   (cod 3): harta se face atunci pe placă, în partea B, înaintea probei.

       python -X utf8 unelte/laborator_harta.py --harta-ref --dispozitiv cpu

2. **Proba (H)**: aceleași setări ca S135 (0) (`unelte/laborator_trepte.py`: rețeaua lui #513, sămânța 1163, lot 12 × 512
   × adunare 8, AdamW, bf16 pe placă, vârf 6e-4, încălzire 3 min, răcire în ultimele 15, 60 min pe ceas, aceleași examene
   — funcția `examene` de acolo). Primele `--minute-uniform` (5) minute ferestrele se trag exact ca la (0); apoi harta.
   În plus față de `progres.csv` al S135: la fiecare minut, partea din ferestrele trase (de la rândul trecut) din fiecare
   sfert de regiuni (după `ref`, sfertul 1 = cel mai ușor); la sfârșit `harta_final.json`. Modelul DOAR în
   `<iesire>/model.pt` (nu în jurnal, nu în lucru/stocare/, nu în interfață).

       python -X utf8 unelte/laborator_harta.py --minute 60 --dispozitiv cuda --iesire lucru/laborator/S137_H

Pierderea pe fereastră se ia din aceeași trecere a pasului (`ModelHarta`, o subclasă aici; `module/model_trepte.py`
rămâne neschimbat). Paznicul: peste 7.000 MB sau 83 °C → oprește.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import time
from pathlib import Path
from typing import Any, Callable

RADACINA = Path(__file__).resolve().parents[1]
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

import numpy as np  # noqa: E402
import torch  # noqa: E402
import torch.nn.functional as F  # noqa: E402

from module.date_harta import MARIME_REGIUNE, DateHarta, HartaFerestre  # noqa: E402
from module.model_trepte import ModelTrepte  # noqa: E402
from unelte import laborator_trepte as lt  # noqa: E402

SAMANTA = lt.SAMANTA
CALE_REF = "lucru/laborator/harta_ref_513.npy"
EXPERIMENT_REF = 513
FERESTRE_PE_REGIUNE = 2
COLOANE = lt.COLOANE + ["mod", "sfert_1_usor", "sfert_2", "sfert_3", "sfert_4_greu"]


class ModelHarta(ModelTrepte):
    """ModelTrepte cu rețeta (0) (K = 1), care păstrează pierderea pe fiecare fereastră din trecerea pasului și trage
    ferestrele dintr-o `HartaFerestre`. Clasa e doar a uneltei (nu e modul înregistrat)."""

    def __init__(self, **setari: Any) -> None:
        super().__init__(**setari)
        if self.k_bucata != 1:
            raise ValueError("ModelHarta e doar pentru rețeta (0): k_bucata = 1")
        self.pierderi_ferestre: list[torch.Tensor] = []

    def pierdere_simboluri(self, x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        """Aceeași pierdere ca ModelTrepte (cross-entropy pe toate pozițiile), luată ca medie a pierderilor pe fereastră
        (toate ferestrele au aceeași lungime) — pierderea pe fereastră rămâne în `pierderi_ferestre`."""
        assert self.retea is not None
        with self._autocast():
            logits = self.retea(x)
            pe_simbol = F.cross_entropy(logits.float().view(-1, logits.size(-1)), y.reshape(-1), reduction="none")
            pe_fereastra = pe_simbol.view(y.shape).mean(dim=1)
            self.pierderi_ferestre.append(pe_fereastra.detach().float().cpu())
            return pe_fereastra.mean()

    def bucla_harta(self, sir: Any, harta: HartaFerestre, buget_secunde: float, secunde_uniform: float,
                    samanta_loturi: int | None = None, cu_harta: bool = True,
                    la_fiecare: Callable[[dict[str, Any]], str | None] | None = None,
                    secunde_intre_semnale: float = 60.0) -> dict[str, Any]:
        """Bucla rețetei (0) din `ModelTrepte.bucla` (aceeași rată după ceas, aceleași semnale), cu ferestrele din hartă:
        uniform (exact ca (0)) până la `secunde_uniform` sau mereu dacă `cu_harta` e fals; harta se recalculează o dată
        pe pas de optimizator și se actualizează după fiecare pas din pierderile pe fereastră."""
        assert self.retea is not None and self.optimizator is not None
        ctx = self.setari["context"]
        if harta.starturi != len(sir) - ctx - 1 or harta.context != ctx:
            raise ValueError("harta nu e făcută pentru acest șir / context")
        generator = torch.Generator(device="cpu").manual_seed(self.samanta if samanta_loturi is None else samanta_loturi)
        self.retea.train()
        start = time.perf_counter()
        urmatorul_semnal = secunde_intre_semnale
        pe_faza = {f: {"pasi": 0, "simboluri": 0, "secunde": 0.0} for f in ("bucati", "simboluri")}
        pierderi_recente: list[float] = []
        ultim: dict[str, float] = {"pierdere": float("nan"), "norma_gradient": float("nan")}
        oprit = None
        rata = self.rata_invatare
        pasi = 0
        pasi_harta = 0
        mod = "uniform"
        self.pozitii_trase: list[torch.Tensor] = []

        def stare(secunde: float, faza: str) -> dict[str, Any]:
            return {"secunde": secunde, "faza": faza, "pasi": pasi, "rata": rata, "mod": mod,
                    "pasi_bucati": 0, "pasi_simboluri": pe_faza["simboluri"]["pasi"],
                    "simboluri_vazute": pe_faza["simboluri"]["simboluri"],
                    "pierdere": (sum(pierderi_recente) / len(pierderi_recente)) if pierderi_recente else float("nan"),
                    "pierdere_ultim_pas": ultim["pierdere"], "norma_gradient": ultim["norma_gradient"]}

        faza = "simboluri"
        while True:
            acum = time.perf_counter() - start
            if acum >= buget_secunde or (self.pasi_max and pasi >= self.pasi_max):
                break
            mod = "harta" if cu_harta and harta.ref is not None and acum >= secunde_uniform else "uniform"
            if mod == "harta":
                harta.recalculeaza()
                pasi_harta += 1
            loturi, pozitii_pas = [], []
            for _ in range(self.adunare_loturi):
                pozitii = harta.trage(self.lot, generator, uniform=(mod == "uniform"))
                pozitii_pas.append(pozitii)
                loturi.append(torch.stack([torch.as_tensor(sir[int(p) : int(p) + ctx + 1]) for p in pozitii])
                              .to(self.dispozitiv, torch.long))
            rata = self.rata_dupa_ceas(acum, buget_secunde)
            t0 = time.perf_counter()
            self.pierderi_ferestre = []
            ultim = self.pas_optimizator(loturi, faza, rata)
            harta.actualizeaza(torch.cat(pozitii_pas).numpy(), torch.cat(self.pierderi_ferestre).numpy())
            self.pozitii_trase.append(torch.cat(pozitii_pas))
            pasi += 1
            pe_faza[faza]["pasi"] += 1
            pe_faza[faza]["simboluri"] += self.adunare_loturi * self.lot * ctx
            pe_faza[faza]["secunde"] += time.perf_counter() - t0
            pierderi_recente.append(ultim["pierdere"])
            if not math.isfinite(ultim["pierdere"]):
                oprit = f"pierderea nu e un număr finit la pasul {pasi}"
                if la_fiecare is not None:
                    la_fiecare(stare(time.perf_counter() - start, faza))
                break
            dupa = time.perf_counter() - start
            if la_fiecare is not None and dupa >= urmatorul_semnal:
                motiv = la_fiecare(stare(dupa, faza))
                pierderi_recente = []
                if secunde_intre_semnale > 0:
                    urmatorul_semnal += secunde_intre_semnale
                    while urmatorul_semnal <= dupa:
                        urmatorul_semnal += secunde_intre_semnale
                if motiv:
                    oprit = motiv
                    break
        secunde = time.perf_counter() - start
        if la_fiecare is not None and oprit is None and pierderi_recente:
            la_fiecare(stare(secunde, faza))
        return {"pasi": pasi, "pasi_cu_harta": pasi_harta, "secunde_bucla": round(secunde, 2), "pe_faza": pe_faza,
                "simboluri_vazute": pe_faza["simboluri"]["simboluri"], "pierdere_finala": ultim["pierdere"],
                "rata_la_final": rata, "oprit": oprit}


# --- harta de referință ------------------------------------------------------------------------


def cale_absoluta(cale: str) -> Path:
    p = Path(cale)
    return p if p.is_absolute() else RADACINA / p


def ferestre_ref(harta: HartaFerestre, samanta: int = SAMANTA, pe_regiune: int = FERESTRE_PE_REGIUNE) -> np.ndarray:
    """Locurile de start ale ferestrelor de referință: pentru fiecare regiune, în ordine, `pe_regiune` locuri cu
    `numpy.random.default_rng(samanta).integers(0, valide[r])`. Formă [regiuni, pe_regiune]."""
    rng = np.random.default_rng(samanta)
    return np.stack([harta.inceputuri[r] + rng.integers(0, harta.valide[r], size=pe_regiune)
                     for r in range(harta.regiuni)])


def pierderi_ferestre(retea: torch.nn.Module, sir: Any, pozitii: np.ndarray, context: int,
                      dispozitiv: torch.device) -> np.ndarray:
    """Pierderea medie (cross-entropy, nats) a rețelei pe fiecare fereastră [p, p + context + 1)."""
    f = torch.stack([torch.as_tensor(sir[int(p) : int(p) + context + 1]) for p in pozitii]).to(dispozitiv, torch.long)
    with torch.no_grad():
        logits = retea(f[:, :context]).float()
        pe_simbol = F.cross_entropy(logits.reshape(-1, logits.size(-1)), f[:, 1:].reshape(-1), reduction="none")
    return pe_simbol.view(len(pozitii), context).mean(dim=1).double().cpu().numpy()


def text_regiune(tok: Any, sir: Any, inceput: int, simboluri: int = 80, caractere: int = 200) -> str:
    return tok.decodeaza(int(x) for x in sir[inceput : inceput + simboluri])[:caractere]


def fa_harta_ref(a: argparse.Namespace) -> int:
    from kronos.cai import gaseste_model
    from kronos.jurnal import Jurnal
    from unelte.modele_salvate import fisa_modelului, incarca_modelul

    cale = cale_absoluta(a.cale_ref)
    if cale.exists() and not a.peste:
        raise SystemExit(f"{cale} există deja: nu scriu peste ea")
    dispozitiv = torch.device(a.dispozitiv)
    date = DateHarta(str(cale_absoluta(lt.BUCATI)), str(cale_absoluta(lt.VALIDARE)), str(cale_absoluta(lt.TOKENIZER)),
                     marime_regiune=a.marime_regiune)
    sir = date.sir_antrenare()
    harta = date.harta(a.context)
    fisa = fisa_modelului(Jurnal(RADACINA / "lucru"), a.experiment_ref)
    model = incarca_modelul(fisa, a.dispozitiv)
    retea = model.retea.float().eval()
    if getattr(retea, "memorie", None) is not None:
        raise SystemExit("rețeaua de referință are memorie: nu e cazul lui #513")
    if model.setari["context"] != a.context:
        raise SystemExit(f"contextul modelului de referință e {model.setari['context']}, nu {a.context}")
    pozitii = ferestre_ref(harta, a.samanta)
    ref = np.zeros(harta.regiuni)
    regiuni_pe_lot = max(1, a.lot_ref // FERESTRE_PE_REGIUNE)
    print(f"Harta de referință: {harta.regiuni} regiuni × {FERESTRE_PE_REGIUNE} ferestre de {a.context}, #{fisa['id']}, "
          f"{a.dispozitiv}, {torch.get_num_threads()} fire", flush=True)
    t0 = time.perf_counter()
    estimare_min = None
    for r0 in range(0, harta.regiuni, regiuni_pe_lot):
        r1 = min(harta.regiuni, r0 + regiuni_pe_lot)
        p = pierderi_ferestre(retea, sir, pozitii[r0:r1].reshape(-1), a.context, dispozitiv)
        ref[r0:r1] = p.reshape(r1 - r0, FERESTRE_PE_REGIUNE).mean(axis=1)
        if estimare_min is None and r1 >= min(50, harta.regiuni):
            estimare_min = (time.perf_counter() - t0) / r1 * harta.regiuni / 60
            print(f"  estimare după {r1} regiuni: {estimare_min:.1f} min în total", flush=True)
            if estimare_min > a.max_minute_ref:
                print(f"OPRIT: estimarea {estimare_min:.1f} min > {a.max_minute_ref} min — harta se face pe placă (B)",
                      file=sys.stderr)
                return 3
        if (r1 // regiuni_pe_lot) % 40 == 0:
            print(f"  {r1}/{harta.regiuni} regiuni, {(time.perf_counter() - t0) / 60:.1f} min", flush=True)
    secunde = time.perf_counter() - t0
    ordine = np.argsort(ref, kind="stable")

    def fisa_regiune(r: int) -> dict[str, Any]:
        return {"regiune": int(r), "pierdere_ref": round(float(ref[r]), 4), "inceput": int(harta.inceputuri[r]),
                "text": text_regiune(model.tok, sir, int(pozitii[r][0]))}

    cale.parent.mkdir(parents=True, exist_ok=True)
    np.save(cale, ref)
    descriere = {
        "ce_este": "S137: harta de referință — pierderea medie (nats/simbol) a lui #513 pe fiecare regiune din W2",
        "experiment_ref": int(fisa["id"]), "model_salvat": Path(gaseste_model(fisa["model_salvat"])).as_posix(),
        "date": {**date.descriere(), "director": lt.BUCATI}, "context": a.context, "samanta": a.samanta,
        "ferestre_pe_regiune": FERESTRE_PE_REGIUNE, "regiuni": harta.regiuni, "marime_regiune": harta.marime_regiune,
        "dispozitiv": a.dispozitiv, "precizie": "F32", "fire": torch.get_num_threads(), "secunde": round(secunde, 1),
        "estimare_dupa_50_min": round(estimare_min or 0.0, 2),
        "medie": float(ref.mean()), "mediana": float(np.median(ref)), "min": float(ref.min()), "max": float(ref.max()),
        "sferturi_praguri": [float(x) for x in np.quantile(ref, [0.25, 0.5, 0.75])],
        "cele_mai_usoare_10": [fisa_regiune(r) for r in ordine[:10]],
        "cele_mai_grele_10": [fisa_regiune(r) for r in ordine[::-1][:10]],
    }
    cale.with_suffix(".json").write_text(json.dumps(descriere, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"cale": cale.as_posix(), "regiuni": harta.regiuni, "medie": round(descriere["medie"], 4),
                      "min": round(descriere["min"], 4), "max": round(descriere["max"], 4),
                      "minute": round(secunde / 60, 2)}, ensure_ascii=False))
    return 0


def citeste_ref(cale: Path, date: DateHarta, context: int) -> np.ndarray:
    """Harta de referință, doar dacă e pentru aceleași date (SHA), aceleași regiuni și același context."""
    if not cale.exists():
        raise SystemExit(f"Lipsește harta de referință {cale}: întâi `--harta-ref`")
    d = json.loads(cale.with_suffix(".json").read_text(encoding="utf-8"))
    if d["date"]["sha256_tot"] != date.index["sha256_tot"]:
        raise SystemExit("harta de referință e pentru alte date (SHA diferit)")
    if d["marime_regiune"] != date.marime_regiune or d["context"] != context:
        raise SystemExit("harta de referință are alte regiuni sau alt context")
    ref = np.load(cale)
    if ref.shape != (date.numar_regiuni(),) or not np.isfinite(ref).all():
        raise SystemExit("harta de referință are altă formă sau valori care nu sunt numere")
    return ref


# --- proba (H) ----------------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--harta-ref", action="store_true", help="doar harta de referință cu #513, apoi ieșire")
    p.add_argument("--cale-ref", default=CALE_REF)
    p.add_argument("--experiment-ref", type=int, default=EXPERIMENT_REF)
    p.add_argument("--lot-ref", type=int, default=16, help="ferestre pe trecere la harta de referință")
    p.add_argument("--max-minute-ref", type=float, default=90.0)
    p.add_argument("--peste", action="store_true", help="la --harta-ref: scrie peste o hartă existentă")
    p.add_argument("--marime-regiune", type=int, default=MARIME_REGIUNE)
    p.add_argument("--minute", type=float, default=60.0)
    p.add_argument("--minute-uniform", type=float, default=5.0)
    p.add_argument("--fara-harta", action="store_true", help="tot uniform (= rețeta (0)); doar la probe")
    p.add_argument("--samanta", type=int, default=SAMANTA)
    p.add_argument("--dispozitiv", choices=["cpu", "cuda"], default="cuda")
    p.add_argument("--iesire")
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
    p.add_argument("--fara-r1", action="store_true")
    p.add_argument("--fara-examene", action="store_true")
    p.add_argument("--memorie-max-gb", type=float, default=5.9)
    a = p.parse_args(argv)
    if a.harta_ref:
        return fa_harta_ref(a)
    if not a.iesire:
        raise SystemExit("--iesire e obligatoriu la probă")
    iesire = cale_absoluta(a.iesire)
    if iesire.exists():
        raise SystemExit(f"{iesire} există deja: nu scriu peste el")

    if a.dispozitiv == "cuda":
        if not torch.cuda.is_available():
            raise SystemExit("placa nu e disponibilă (CUDA)")
        total = torch.cuda.get_device_properties(0).total_memory
        torch.cuda.set_per_process_memory_fraction(min(1.0, a.memorie_max_gb * 2**30 / total))

    from module.tokenizer_bpe import TokenizerBPE
    from unelte.banc_antrenare import versiuni

    a.reteta, a.k, a.minute_bucati = 0, 1, 0.0  # rețeta (0): setările modelului identice cu S135 (0)
    setari = lt.setari_model(a)
    model = ModelHarta(**setari)
    date = DateHarta(str(cale_absoluta(lt.BUCATI)), str(cale_absoluta(lt.VALIDARE)), str(cale_absoluta(lt.TOKENIZER)),
                     marime_regiune=a.marime_regiune)
    ref = None if a.fara_harta else citeste_ref(cale_absoluta(a.cale_ref), date, a.context)
    harta = date.harta(a.context, ref)
    sferturi = harta.sferturi()
    model.tok = TokenizerBPE.incarca(model.cale_tokenizer)
    sir = model._sirul(date)
    model._pregateste_reteaua()
    assert model.retea is not None
    iesire.mkdir(parents=True)
    citeste, verifica = lt.paznic()
    pe_placa = a.dispozitiv == "cuda"
    placa_max = {"memorie_mb": 0.0, "temperatura": 0.0}
    fisier_csv = (iesire / "progres.csv").open("w", newline="", encoding="utf-8")
    scriitor = csv.DictWriter(fisier_csv, fieldnames=COLOANE)
    scriitor.writeheader()
    trase_inainte = np.zeros(4)

    def la_fiecare(s: dict[str, Any]) -> str | None:
        nonlocal trase_inainte
        smi = citeste() if pe_placa else None
        if smi:
            for k in placa_max:
                placa_max[k] = max(placa_max[k], smi[k])
        acum = np.bincount(sferturi, weights=harta.trase, minlength=4)
        noi = acum - trase_inainte
        trase_inainte = acum
        parti = noi / noi.sum() if noi.sum() > 0 else noi
        scriitor.writerow({"minut": round(s["secunde"] / 60, 2), "secunde": round(s["secunde"], 1), "faza": s["faza"],
                           "pasi": s["pasi"], "pasi_bucati": 0, "pasi_simboluri": s["pasi_simboluri"],
                           "simboluri_vazute": s["simboluri_vazute"], "eroare": round(s["pierdere"], 5),
                           "eroare_ultim_pas": round(s["pierdere_ultim_pas"], 5),
                           "norma_gradient": round(s["norma_gradient"], 4), "rata": f"{s['rata']:.3e}",
                           "memorie_mb": smi["memorie_mb"] if smi else "", "temperatura": smi["temperatura"] if smi else "",
                           "mod": s["mod"], "sfert_1_usor": round(parti[0], 4), "sfert_2": round(parti[1], 4),
                           "sfert_3": round(parti[2], 4), "sfert_4_greu": round(parti[3], 4)})
        fisier_csv.flush()
        print(f"[{s['secunde'] / 60:6.2f} min] {s['mod']:7s} pași {s['pasi']:6d}  eroare {s['pierdere']:.4f}  "
              f"sferturi {' '.join(f'{x:.2f}' for x in parti)}  "
              f"{(smi or {}).get('memorie_mb', '-')} MB {(smi or {}).get('temperatura', '-')} °C", flush=True)
        return verifica(smi)

    if pe_placa:
        torch.cuda.reset_peak_memory_stats()
    smi_inainte = citeste() if pe_placa else None
    print(f"S137 (H): {a.minute} min, uniform primele {a.minute_uniform} min, harta {'oprită' if ref is None else 'pornită'}, "
          f"{harta.regiuni} regiuni, {sum(t.numel() for t in model.retea.parameters()):,} parametri, {a.dispozitiv}",
          flush=True)
    try:
        bucla = model.bucla_harta(sir, harta, a.minute * 60.0, a.minute_uniform * 60.0, samanta_loturi=a.samanta,
                                  cu_harta=ref is not None, la_fiecare=la_fiecare,
                                  secunde_intre_semnale=a.secunde_intre_randuri)
    finally:
        fisier_csv.close()
    stare_harta = harta.stare()
    (iesire / "harta_final.json").write_text(json.dumps(
        {**stare_harta, "ref": None if ref is None else [round(float(x), 5) for x in ref],
         "sfert": [int(x) for x in sferturi]}, ensure_ascii=False), encoding="utf-8")
    rezultat: dict[str, Any] = {
        "ce_este": "S137 laboratorul, proba (H): rețeta S135 (0), ferestrele din harta „ce se mai poate învăța” "
                   "(nu intră în jurnal/interfață/export)",
        "argumente": vars(a), "setari_model": {**setari, "cale_tokenizer": lt.TOKENIZER},
        "parametri": sum(t.numel() for t in model.retea.parameters()),
        "date": {**date.descriere(), "director": lt.BUCATI,
                 "nota": "doar textul W2 (amestecul W2 tokenizat), fără conversații și fără hrană"},
        "harta": {"cale_ref": None if ref is None else a.cale_ref, "regiuni": harta.regiuni,
                  "vazute": stare_harta["vazute"], "trase_pe_sferturi": stare_harta["trase_pe_sferturi"]},
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
        rezultat["examene"] = lt.examene(model, date, cu_r1=not a.fara_r1)
        if pe_placa:
            smi = citeste()
            if smi:
                for k in placa_max:
                    placa_max[k] = max(placa_max[k], smi[k])
    rezultat["versiuni"] = versiuni(torch.device(a.dispozitiv))
    (iesire / "rezultat.json").write_text(json.dumps(rezultat, ensure_ascii=False, indent=1), encoding="utf-8")
    ex = rezultat.get("examene") or {}
    print(json.dumps({"iesire": iesire.as_posix(), "pasi": bucla["pasi"], "pasi_cu_harta": bucla["pasi_cu_harta"],
                      "simboluri_vazute": bucla["simboluri_vazute"], "pierdere_finala": bucla["pierdere_finala"],
                      "oprit": bucla["oprit"], "trase_pe_sferturi": stare_harta["trase_pe_sferturi"],
                      "romana_bpb": (ex.get("romana") or {}).get("romana_bpb"),
                      "r1_instructiuni": (ex.get("romana") or {}).get("r1_instructiuni"),
                      "val_bpb": (ex.get("examen_bpb") or {}).get("val_bpb"), "placa_max": placa_max if pe_placa else None},
                     ensure_ascii=False))
    return 2 if bucla["oprit"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
