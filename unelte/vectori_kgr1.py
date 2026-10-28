"""S39 (C-24): vectorii de control KGR1 pentru motorul Cyber Universe OS (scris de ei, în Rust, fără codul Kronos).

Un GPT minuscul cu arhitectura liniei w2 (aceleași nume de tensori, LayerNorm, cap legat), greutăți la întâmplare cu sămânță
fixă și tokenizerul nostru adevărat (date/ws/bpe_16384.json), scris în KGR1 F32 și Q8_0 cu exporta_model din
unelte/exporta_greutati.py. Pentru 3 texte fixe: simbolurile, logit-urile pe ultima poziție (tot vectorul), argmax-ul pe
fiecare poziție, primele 5 simboluri greedy (din unelte/inferenta_bruta.py) și, la F32, diferența față de PyTorch pe procesor.

Folosire:
    python unelte/vectori_kgr1.py vectori --iesire integrare/kronos          # partea A: vectori/*.kgr + vectori/vectori.json
    python unelte/vectori_kgr1.py model --kgr lucru/export/kronos_459_q8_0.kgr   # partea B: suma, mărimea, greedy pe cele 3 texte
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

RADACINA = Path(__file__).resolve().parents[1]
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from unelte.inferenta_bruta import MotorBrut  # noqa: E402

TEXTE = ["Ana are mere.", "Capitala României este", "def suma(a, b):"]
TOKENIZER = "date/ws/bpe_16384.json"
SAMANTA = 20261028
GREEDY = 5
# minuscul: n_emb = 32 e cel mai mic care merge cu Q8_0 (blocuri de 32 de coloane)
SETARI = dict(n_straturi=2, n_capete=4, n_emb=32, context=64)
FISIERE = {"f32": "mic_f32.kgr", "q8_0": "mic_q8_0.kgr"}
# cu N(0, 1) la intrare, ultimul simbol „se vede pe sine” și greedy repetă mereu același simbol (cache-ul k/v nu mai e
# pus la încercare); mai mic, straturile decid
SCARA_EMB = 0.3


def sha256(cale: str | Path) -> str:
    h = hashlib.sha256()
    with Path(cale).open("rb") as f:
        for bucata in iter(lambda: f.read(1 << 20), b""):
            h.update(bucata)
    return h.hexdigest()


def model_mic(cale_tokenizer: str = TOKENIZER, samanta: int = SAMANTA) -> Any:
    """ModelGPT (aceeași rețea _GPT ca w2) cu greutăți la întâmplare, destul de mari ca logit-urile să fie bine despărțite:
    tabelul de intrare N(0, 1), poziții N(0, 0,5), matricile N(0, 1/√intrări), LayerNorm 1 + N(0, 0,1), deplasări N(0, 0,1)."""
    import torch

    from module.model_gpt import ModelGPT
    from module.tokenizer_bpe import TokenizerBPE

    m = ModelGPT(**SETARI, tokenizer="bpe", cale_tokenizer=str(RADACINA / cale_tokenizer), dispozitiv="cpu",
                 samanta=samanta)
    m.tok = TokenizerBPE.incarca(RADACINA / cale_tokenizer)
    m._construieste()
    g = torch.Generator().manual_seed(samanta)
    with torch.no_grad():
        for nume, p in m.retea.named_parameters():
            if nume == "emb_token.weight":
                p.copy_(SCARA_EMB * torch.randn(p.shape, generator=g))
            elif nume == "emb_pozitie.weight":
                p.copy_(0.5 * torch.randn(p.shape, generator=g))
            elif p.ndim == 2:
                p.copy_(torch.randn(p.shape, generator=g) / p.shape[1] ** 0.5)
            elif nume.split(".")[-2].startswith("ln"):
                p.copy_(1.0 + 0.1 * torch.randn(p.shape, generator=g) if nume.endswith("weight")
                        else 0.1 * torch.randn(p.shape, generator=g))
            else:
                p.copy_(0.1 * torch.randn(p.shape, generator=g))
    m.retea.eval()
    return m


def _f(x: float) -> float:
    """Un float32 scris cu 9 cifre semnificative: se citește înapoi exact."""
    return float(f"{float(x):.9g}")


def _marje(lg: np.ndarray) -> np.ndarray:
    """Pe fiecare poziție: primul logit minus al doilea."""
    doi = np.sort(lg.astype(np.float64), axis=-1)[..., -2:]
    return doi[..., 1] - doi[..., 0]


def vectori_text(motor: MotorBrut, text: str) -> dict[str, Any]:
    s = motor.tok.codifica(text)
    lg = motor.logits(s)
    ultim = lg[-1]
    ordine = np.argsort(-ultim.astype(np.float64), kind="stable")
    greedy, _ = motor.completeaza_simboluri(s, GREEDY)
    # greedy (cu cache k/v) refăcut fără cache, pe tot șirul: aceleași simboluri, și marjele pașilor
    tot = motor.logits(s + greedy[:-1])[len(s) - 1:]
    if [int(x) for x in tot.argmax(axis=-1)] != greedy:
        raise RuntimeError(f"{text!r}: greedy cu cache ≠ fără cache")
    return {
        "text": text,
        "simboluri": [int(x) for x in s],
        "argmax_pe_pozitii": [int(x) for x in lg.argmax(axis=-1)],
        "primele_5_ultima_pozitie": [int(x) for x in ordine[:5]],
        "marja_top1_top2": _f(ultim[ordine[0]] - ultim[ordine[1]]),
        "marja_minima_pozitii": _f(_marje(lg).min()),
        "marja_minima_greedy": _f(_marje(tot).min()),
        "greedy_5": [int(x) for x in greedy],
        "greedy_5_text": motor.tok.decodeaza(greedy),
        "logits_ultima_pozitie": [_f(x) for x in ultim],
    }


def fa_vectori(iesire: str | Path) -> dict[str, Any]:
    import torch

    from unelte.exporta_greutati import exporta_model

    iesire = Path(iesire)
    dosar = iesire / "vectori"
    m = model_mic()
    sursa = f"vectori de control S39: greutăți la întâmplare, sămânța {SAMANTA}, tokenizer {TOKENIZER}"
    rezultat: dict[str, Any] = {
        "ce_e": "vectorii de control KGR1 (S39, C-24): model minuscul cu greutăți la întâmplare, NU un model antrenat",
        "samanta": SAMANTA, "tokenizer": TOKENIZER, "setari": {**SETARI, "vocabular": m.tok.marime},
        "texte": TEXTE, "fisiere": {},
    }
    motoare = {}
    for fel, nume in FISIERE.items():
        cale = dosar / nume
        octeti = exporta_model(m, cale, fel, sursa=sursa)
        rezultat["fisiere"][fel] = {"nume": f"vectori/{nume}", "octeti": octeti, "sha256": sha256(cale)}
        motoare[fel] = MotorBrut(cale)
    for fel, motor in motoare.items():
        rezultat[fel] = [vectori_text(motor, t) for t in TEXTE]
    # diferențele măsurate: F32 (motorul nostru) față de PyTorch pe procesor; Q8_0 față de F32
    dif_pt, dif_q8 = [], []
    for t in TEXTE:
        s = m.tok.codifica(t)
        with torch.no_grad():
            pt = m.retea(torch.tensor([s]))[0].numpy()
        f32 = motoare["f32"].logits(s)
        dif_pt.append(float(np.abs(f32 - pt).max()))
        dif_q8.append(float(np.abs(motoare["q8_0"].logits(s) - f32).max()))
    rezultat["diferente"] = {
        "f32_fata_de_pytorch_max": max(dif_pt), "f32_fata_de_pytorch_pe_texte": dif_pt,
        "q8_0_fata_de_f32_max": max(dif_q8), "q8_0_fata_de_f32_pe_texte": dif_q8,
        "logit_maxim_absolut": max(float(np.abs(np.asarray(v["logits_ultima_pozitie"])).max())
                                   for fel in FISIERE for v in rezultat[fel]),
    }
    (dosar / "vectori.json").write_bytes(json.dumps(rezultat, ensure_ascii=False, indent=1).encode("utf-8"))
    return rezultat


def verifica_model(kgr: str | Path) -> dict[str, Any]:
    """Partea B: suma, mărimea și primele 5 simboluri greedy pe cele 3 texte, cu motorul fără PyTorch."""
    motor = MotorBrut(kgr)
    return {
        "fisier": str(kgr), "octeti": Path(kgr).stat().st_size, "sha256": sha256(kgr),
        "sursa": motor.chei.get("sursa"), "fel": motor.chei.get("fel"),
        "setari": {k: motor.chei[k] for k in ("n_straturi", "n_capete", "n_emb", "context", "vocabular")},
        "texte": [{k: v for k, v in vectori_text(motor, t).items() if k != "logits_ultima_pozitie"} for t in TEXTE],
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="comanda", required=True)
    v = sub.add_parser("vectori")
    v.add_argument("--iesire", default="integrare/kronos")
    mo = sub.add_parser("model")
    mo.add_argument("--kgr", required=True)
    mo.add_argument("--json", default="")
    a = p.parse_args(argv)
    if a.comanda == "vectori":
        r = fa_vectori(a.iesire)
        print(json.dumps({"fisiere": r["fisiere"], "diferente": r["diferente"],
                          "greedy": {fel: [x["greedy_5"] for x in r[fel]] for fel in FISIERE},
                          "marje": {fel: [(x["marja_top1_top2"], x["marja_minima_pozitii"], x["marja_minima_greedy"])
                                          for x in r[fel]] for fel in FISIERE}},
                         ensure_ascii=False, indent=1))
    else:
        r = verifica_model(a.kgr)
        if a.json:
            Path(a.json).write_bytes(json.dumps(r, ensure_ascii=False, indent=1).encode("utf-8"))
        print(json.dumps(r, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
