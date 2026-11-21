"""S132 (C-156): „pasul de aur” — 10 pași de antrenare făcuți în PyTorch pe procesor (F32) și exportați, ca motorul de
antrenare din OS (Cyber-GPU) să aibă cu ce se compara: aceleași intrări → aceeași eroare, același gradient pe fiecare
tensor, aceleași greutăți după 1 și după 10 pași.

Ce se fixează ca rularea să fie repetabilă: `torch.manual_seed`, `torch.use_deterministic_algorithms(True)`, F32,
procesorul, un număr fix de fire (implicit 1), dropout 0, un singur lot (fără adunare de loturi), rata de învățare
constantă (fără încălzire și fără scădere). Același lot fix la fiecare din cei 10 pași.

Ce se exportă (în dosarul `--iesire`, care NU trebuie să existe; nimic nu se scrie peste nimic):
- `reteta.json` — arhitectura, rețetele (optimizatorul cu toți parametrii), sămânța, forma lotului, ordinea și numele
  tensorilor, formele, SHA-256 și mărimea fiecărui fișier, erorile pe cei 10 pași, versiunile;
- `intrari.i32`, `tinte.i32` — lotul (int32 little-endian, [lot, context], pe rânduri);
- `initiale/<tensor>.f32` — greutățile de la început (aceleași pentru toate rețetele);
- `<reteta>/grad_pas1/<tensor>.f32` — gradientul la pasul 1 (înainte de tăierea gradientului, dacă rețeta o are);
- `<reteta>/dupa_pas1/<tensor>.f32`, `<reteta>/dupa_pas10/<tensor>.f32` — greutățile după pasul 1 și după pasul 10.
Fiecare `.f32` = numerele tensorului în F32 little-endian, fără antet, în ordinea din memorie a tensorului (C, pe rânduri).

Rețetele: `sgd` (SGD simplu, rata 0,01, fără momentum, fără scăderea greutăților, fără tăiere) și `adamw_513`
(optimizatorul liniei lui #513, `config/conv_w2_romana_r1.toml` cu `optimizator = "adamw"` → `module/model_muon.py`
`_optimizator_nou`: `torch.optim.AdamW(lr=rata_invatare=5e-5, weight_decay=0.1)`, beta/eps implicite, apoi
`clip_grad_norm_(…, 1.0)` înainte de fiecare pas).

    python -X utf8 unelte/pas_de_aur.py mic --iesire docs/integrare_kronos/pas_de_aur_mic
    python -X utf8 unelte/pas_de_aur.py model --experiment 513 --iesire lucru/pas_de_aur/513
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import platform
import random
import sys
from pathlib import Path
from typing import Any

import torch
import torch.nn.functional as F

RADACINA = Path(__file__).resolve().parents[1]
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

SAMANTA = 1132
PASI = 10
MIC = {"vocab": 256, "n_straturi": 2, "n_capete": 4, "n_emb": 64, "context": 32, "lot": 2}
MARIME_MAXIMA_MIC = 5 * 1024 * 1024
TEXT_ROMANA = "date/ws/curat/wikipedia_ro/validare.txt"

# Optimizatorul liniei lui #513 (citit din cod, nu ghicit): module/model_muon.py, _optimizator_nou (ramura „adamw”) +
# _pas_adunat (clip_grad_norm_ 1.0); rata = `rata_invatare` din config/conv_w2_romana_r1.toml.
RETETE: dict[str, dict[str, Any]] = {
    "sgd": {"optimizator": "SGD", "lr": 0.01, "momentum": 0.0, "dampening": 0.0, "weight_decay": 0.0,
            "nesterov": False, "taiere_gradient": None},
    "adamw_513": {"optimizator": "AdamW", "lr": 5e-5, "betas": [0.9, 0.999], "eps": 1e-8, "weight_decay": 0.1,
                  "amsgrad": False, "taiere_gradient": 1.0},
}


def sha256(cale: str | Path) -> str:
    h = hashlib.sha256()
    with open(cale, "rb") as f:
        for bucata in iter(lambda: f.read(1 << 20), b""):
            h.update(bucata)
    return h.hexdigest()


def fixeaza(fire: int = 1) -> None:
    """Totul repetabil: algoritmi deterministici, un număr fix de fire."""
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(fire)


def retea_mica(samanta: int = SAMANTA, **marimi: int) -> torch.nn.Module:
    """Aceeași arhitectură ca #513 (module/model_gpt.py `_GPT`), mică, cu greutățile inițiale din sămânță."""
    from module.model_gpt import _GPT

    m = {**MIC, **marimi}
    torch.manual_seed(samanta)
    return _GPT(vocab=m["vocab"], n_straturi=m["n_straturi"], n_capete=m["n_capete"], n_emb=m["n_emb"],
                context=m["context"], dropout=0.0).float()


def lot_din_samanta(samanta: int, vocab: int, lot: int, context: int) -> tuple[torch.Tensor, torch.Tensor]:
    g = torch.Generator().manual_seed(samanta)
    s = torch.randint(0, vocab, (lot, context + 1), generator=g, dtype=torch.int64)
    return s[:, :-1].contiguous(), s[:, 1:].contiguous()


def tensori(retea: torch.nn.Module) -> list[tuple[str, torch.nn.Parameter]]:
    """Parametrii în ordinea `named_parameters()`; `cap.weight` e legat de `emb_token.weight` și apare o singură dată."""
    return list(retea.named_parameters())


def verifica_fara_dropout(retea: torch.nn.Module) -> None:
    for nume, m in retea.named_modules():
        p = getattr(m, "dropout", None) if isinstance(m, torch.nn.MultiheadAttention) else getattr(m, "p", None)
        if isinstance(m, (torch.nn.Dropout, torch.nn.MultiheadAttention)) and p:
            raise ValueError(f"{nume}: dropout {p} ≠ 0")


def optimizator(reteta: dict[str, Any], parametri: list[torch.nn.Parameter]) -> torch.optim.Optimizer:
    if reteta["optimizator"] == "SGD":
        return torch.optim.SGD(parametri, lr=reteta["lr"], momentum=reteta["momentum"], dampening=reteta["dampening"],
                               weight_decay=reteta["weight_decay"], nesterov=reteta["nesterov"], foreach=False)
    if reteta["optimizator"] == "AdamW":
        return torch.optim.AdamW(parametri, lr=reteta["lr"], betas=tuple(reteta["betas"]), eps=reteta["eps"],
                                 weight_decay=reteta["weight_decay"], amsgrad=reteta["amsgrad"], foreach=False)
    raise ValueError(reteta["optimizator"])


def pierdere(retea: torch.nn.Module, x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
    """Ca la antrenare (module/model_gpt.py): entropia încrucișată, media pe toate pozițiile lotului."""
    logits = retea(x)
    return F.cross_entropy(logits.float().view(-1, logits.size(-1)), y.reshape(-1))


def ruleaza_pasi(retea: torch.nn.Module, x: torch.Tensor, y: torch.Tensor, reteta: dict[str, Any],
                 pasi: int = PASI) -> dict[str, Any]:
    """`pasi` pași pe același lot. Eroarea pasului k = pe greutățile dinaintea actualizării k."""
    retea.train()
    perechi = tensori(retea)
    parametri = [p for _, p in perechi]
    opt = optimizator(reteta, parametri)
    r: dict[str, Any] = {"pierderi": [], "norme_gradient": []}
    for pas in range(1, pasi + 1):
        opt.zero_grad(set_to_none=True)
        loss = pierdere(retea, x, y)
        loss.backward()
        if pas == 1:
            r["grad_pas1"] = {n: p.grad.detach().clone() for n, p in perechi}
        if reteta.get("taiere_gradient"):
            norma = torch.nn.utils.clip_grad_norm_(parametri, reteta["taiere_gradient"])
        else:
            norma = torch.linalg.vector_norm(torch.stack([torch.linalg.vector_norm(p.grad) for p in parametri]))
        opt.step()
        r["pierderi"].append(float(loss.item()))
        r["norme_gradient"].append(float(norma.item()))
        if pas == 1:
            r["dupa_pas1"] = {n: p.detach().clone() for n, p in perechi}
    r[f"dupa_pas{pasi}"] = {n: p.detach().clone() for n, p in perechi}
    return r


def scrie_f32(cale: Path, t: torch.Tensor) -> dict[str, Any]:
    octeti = t.detach().cpu().contiguous().to(torch.float32).numpy().astype("<f4").tobytes()
    cale.parent.mkdir(parents=True, exist_ok=True)
    cale.write_bytes(octeti)
    return {"sha256": hashlib.sha256(octeti).hexdigest(), "octeti": len(octeti)}


def scrie_i32(cale: Path, t: torch.Tensor) -> dict[str, Any]:
    octeti = t.detach().cpu().contiguous().to(torch.int32).numpy().astype("<i4").tobytes()
    cale.write_bytes(octeti)
    return {"sha256": hashlib.sha256(octeti).hexdigest(), "octeti": len(octeti), "forma": list(t.shape)}


def arhitectura(retea: torch.nn.Module) -> dict[str, Any]:
    strat = retea.straturi[0]
    return {
        "clasa": "module.model_gpt._GPT",
        "vocabular": retea.emb_token.num_embeddings, "n_straturi": len(retea.straturi),
        "n_emb": retea.emb_token.embedding_dim, "n_capete": strat.atentie.num_heads,
        "dim_cap": retea.emb_token.embedding_dim // strat.atentie.num_heads, "context": retea.context,
        "mlp": "Linear(n_emb, 4·n_emb) → GELU exact (erf) → Linear(4·n_emb, n_emb)",
        "normalizare": f"LayerNorm (cu greutate și deplasare, eps {strat.ln1.eps}), înainte de atenție și de MLP "
                       "(pre-norm) + LayerNorm final `ln` înainte de ieșire",
        "bloc": "x = x + Atenție(LN1(x)); x = x + MLP(LN2(x))",
        "atentie": "nn.MultiheadAttention(batch_first): in_proj_weight [3·n_emb, n_emb] = rândurile Q, apoi K, apoi V; "
                   "in_proj_bias [3·n_emb]; capetele = bucăți consecutive de dim_cap din Q/K/V; scoruri Q·Kᵀ/√dim_cap; "
                   "masca cauzală (poziția j > i → −∞) înainte de softmax; out_proj (Linear cu deplasare)",
        "intrare": "emb_token[simbol] + emb_pozitie[poziție] (poziții 0..T−1)",
        "iesire": "cap = Linear(n_emb, vocabular, fără deplasare), greutatea LEGATĂ de emb_token.weight (același tensor: "
                  "gradientul lui emb_token.weight = suma din încorporare + din ieșire; exportat o singură dată)",
        "dropout": 0.0,
        "memorie": "fără (retea.memorie = None)",
    }


def versiuni(fire: int) -> dict[str, Any]:
    import numpy

    return {"python": sys.version.split()[0], "pytorch": torch.__version__, "numpy": numpy.__version__,
            "procesor": platform.processor(), "sistem": platform.platform(), "fire_pytorch": fire,
            "deterministic": torch.are_deterministic_algorithms_enabled()}


def exporta(retea: torch.nn.Module, x: torch.Tensor, y: torch.Tensor, iesire: Path, retete: dict[str, dict[str, Any]],
            extra: dict[str, Any], fire: int, pasi: int = PASI) -> dict[str, Any]:
    """Rulează fiecare rețetă pe o copie a rețelei de pornire și scrie tot. Refuză un dosar care există."""
    iesire = Path(iesire)
    if iesire.exists():
        raise SystemExit(f"{iesire} există deja: nu scriu peste el")
    verifica_fara_dropout(retea)
    iesire.mkdir(parents=True)
    fisiere: dict[str, Any] = {"intrari.i32": scrie_i32(iesire / "intrari.i32", x),
                               "tinte.i32": scrie_i32(iesire / "tinte.i32", y)}
    ordine = [{"nume": n, "forma": list(p.shape), "elemente": p.numel(), "fisier": f"{n}.f32"} for n, p in tensori(retea)]
    for n, p in tensori(retea):
        fisiere[f"initiale/{n}.f32"] = scrie_f32(iesire / "initiale" / f"{n}.f32", p)
    rezultate: dict[str, Any] = {}
    for nume_r, reteta in retete.items():
        copie = copy.deepcopy(retea)
        r = ruleaza_pasi(copie, x, y, reteta, pasi)
        for cheie in ("grad_pas1", "dupa_pas1", f"dupa_pas{pasi}"):
            for n, t in r[cheie].items():
                fisiere[f"{nume_r}/{cheie}/{n}.f32"] = scrie_f32(iesire / nume_r / cheie / f"{n}.f32", t)
        rezultate[nume_r] = {**reteta, "pierderi": r["pierderi"], "norme_gradient": r["norme_gradient"],
                             "scade": r["pierderi"][-1] < r["pierderi"][0]}
        del copie
    manifest = {
        "ce_este": "S132 „pasul de aur”: 10 pași de antrenare în PyTorch (procesor, F32), pentru comparația cu OS-ul",
        "samanta": extra.get("samanta", SAMANTA), "pasi": pasi,
        "lot": {"forma": list(x.shape), "intrari": "intrari.i32", "tinte": "tinte.i32",
                "nota": "tinte[b, t] = simbolul de după intrari[b, t]; același lot la fiecare pas"},
        "pierdere": "F.cross_entropy(logits.float().view(−1, vocabular), tinte.view(−1)), media pe lot × context "
                    "(logaritm natural); eroarea pasului k e calculată pe greutățile dinaintea actualizării k",
        "pas": "zero_grad → înainte → înapoi → [grad_pas1 exportat aici, înainte de tăiere] → tăierea gradientului "
               "(dacă rețeta o are) → optimizator.step()",
        "rata": "constantă la toți pașii (fără încălzire, fără scădere)",
        "format": {"f32": "F32 little-endian, fără antet, ordinea C (pe rânduri)", "i32": "int32 little-endian, fără antet",
                   "ordinea_octetilor": "little-endian"},
        "arhitectura": arhitectura(retea),
        "ordinea_tensorilor": ordine,
        "parametri_total": sum(t["elemente"] for t in ordine),
        "retete": rezultate,
        "fisiere": fisiere,
        "marime_totala_octeti": sum(f["octeti"] for f in fisiere.values()),
        "versiuni": versiuni(fire),
        **{k: v for k, v in extra.items() if k != "samanta"},
    }
    (iesire / "reteta.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    return manifest


def lot_romana(tok: Any, samanta: int, lungime: int) -> tuple[torch.Tensor, torch.Tensor, dict[str, Any]]:
    """1 × `lungime` simboluri din validarea română (Wikipedia), de la un loc ales cu random.Random(samanta)."""
    text = (RADACINA / TEXT_ROMANA).read_text(encoding="utf-8")
    start = random.Random(samanta).randrange(0, len(text) - 20_000)
    simboluri = tok.codifica(text[start:start + 20_000])[: lungime + 1]
    if len(simboluri) < lungime + 1:
        raise ValueError("prea puține simboluri")
    s = torch.tensor([simboluri], dtype=torch.int64)
    return s[:, :-1].contiguous(), s[:, 1:].contiguous(), {"fisier_text": TEXT_ROMANA, "start_caracter": start,
                                                             "text": tok.decodeaza(simboluri)}


def verifica_optimizator_513(model: Any) -> dict[str, Any]:
    """Optimizatorul pe care l-ar face modelul însuși (_optimizator_nou) trebuie să aibă exact parametrii din RETETE."""
    opt = model._optimizator_nou()
    g = opt.defaults
    r = RETETE["adamw_513"]
    citit = {"clasa": type(opt).__name__, "lr": g["lr"], "betas": list(g["betas"]), "eps": g["eps"],
             "weight_decay": g["weight_decay"], "amsgrad": g["amsgrad"], "optimizator_ales": model.optimizator_ales}
    potriveste = (citit["clasa"] == "AdamW" and citit["lr"] == r["lr"] and citit["betas"] == r["betas"]
                  and citit["eps"] == r["eps"] and citit["weight_decay"] == r["weight_decay"] and not citit["amsgrad"])
    if not potriveste:
        raise SystemExit(f"optimizatorul modelului diferă de rețeta adamw_513: {citit}")
    return citit


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="comanda", required=True)
    pm = sub.add_parser("mic", help="modelul mic de probă (bucata A)")
    pm.add_argument("--iesire", required=True)
    pm.add_argument("--fire", type=int, default=1)
    pe = sub.add_parser("model", help="un model salvat de Kronos, doar citit (bucata B)")
    pe.add_argument("--experiment", type=int, required=True)
    pe.add_argument("--iesire", required=True)
    pe.add_argument("--lungime", type=int, default=64)
    pe.add_argument("--fire", type=int, default=1)
    a = p.parse_args(argv)
    fixeaza(a.fire)
    iesire = Path(a.iesire)
    if a.comanda == "mic":
        retea = retea_mica(SAMANTA)
        x, y = lot_din_samanta(SAMANTA, MIC["vocab"], MIC["lot"], MIC["context"])
        m = exporta(retea, x, y, iesire, RETETE, {"samanta": SAMANTA, "model": "mic, greutăți din torch.manual_seed(1132)",
                                                  "lot_din": "torch.Generator().manual_seed(1132), randint(0, 256)"},
                    a.fire)
        if m["marime_totala_octeti"] > MARIME_MAXIMA_MIC:
            print(f"ATENȚIE: {m['marime_totala_octeti']} o > 5 MB", file=sys.stderr)
            return 2
    else:
        from kronos.cai import gaseste_model
        from kronos.jurnal import Jurnal
        from unelte.modele_salvate import fisa_modelului, incarca_modelul

        fisa = fisa_modelului(Jurnal(RADACINA / "lucru"), a.experiment)
        cale_model = Path(gaseste_model(fisa["model_salvat"]))
        if not cale_model.exists():
            cale_model = cale_model.with_suffix(".pt")
        sha_inainte = sha256(cale_model)
        model = incarca_modelul(fisa, "cpu")
        citit = verifica_optimizator_513(model)
        retea = model.retea.float()
        if retea.memorie is not None:
            raise SystemExit("rețeaua are memorie: nu e cazul lui #513")
        torch.manual_seed(SAMANTA)
        x, y, despre_lot = lot_romana(model.tok, SAMANTA, a.lungime)
        m = exporta(retea, x, y, iesire, RETETE, {
            "samanta": SAMANTA, "model": f"#{fisa['id']} (linia {fisa.get('linie', '')}), doar citit",
            "model_salvat": cale_model.as_posix(), "clasa_modelului": fisa["module"]["model"]["cale"],
            "optimizator_citit_din_model": citit, "lot_din": despre_lot,
            "fata_de_antrenarea_reala": "la antrenare: adunare_loturi = 8 (pierderea ÷ 8, un pas la 8 loturi de 12 × 512), "
                                        "încălzire 100 de pași, amestec mascat la conversații; aici: un lot, rata constantă, "
                                        "pierderea pe toate pozițiile"}, a.fire)
        sha_dupa = sha256(cale_model)
        m["sha256_model"] = {"inainte": sha_inainte, "dupa": sha_dupa, "neschimbat": sha_inainte == sha_dupa}
        (iesire / "reteta.json").write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
        if sha_inainte != sha_dupa:
            print("EROARE: modelul s-a schimbat pe disc", file=sys.stderr)
            return 3
    print(json.dumps({"iesire": iesire.as_posix(), "marime_totala_octeti": m["marime_totala_octeti"],
                      "parametri": m["parametri_total"],
                      **{k: {"pierderi": [round(v, 6) for v in r["pierderi"]], "scade": r["scade"]}
                         for k, r in m["retete"].items()}}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
