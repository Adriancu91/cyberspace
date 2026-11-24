"""S134: „bancul de antrenare” — aceiași pași de antrenare ai lui #513 în PyTorch, ca să-i comparăm cinstit cu motorul
de antrenare din OS (Cyber-GPU): același model, același lot, aceeași precizie, aceleași date, același număr de pași.

Ce face:
- pornește din greutățile unui model salvat de Kronos (implicit #513), doar citite; nu salvează niciun model și nu
  scrie în jurnalul de experimente (greutățile trăiesc doar în memorie);
- datele: șirul de simboluri al textului liniei #513 (amestecul W2), tăiat în bucăți (`lucru/bucati/w2_amestec_be12`,
  `index.json` → `sursa` = `lucru/cache/simboluri_be12c6d88276d79d.pt`, cache-ul liniei); loturile se trag EXACT ca
  `DateBucati.lot`: un `torch.Generator()` pe procesor cu sămânța dată (MT19937), apoi la fiecare pas
  `torch.randint(len(sir) − context − 1, (lot,), generator=g)` = pozițiile ferestrelor; un lot nou la fiecare pas;
- pasul (ca OS-ul): AdamW la FIECARE lot, fără adunare de loturi, parametrii liniei #513 (lr 5e-5, beta 0,9/0,999,
  eps 1e-8, scăderea greutăților 0,1 — verificați pe optimizatorul pe care îl face modelul însuși), tăierea gradientului
  1,0, rata constantă, fără încălzire, dropout 0, pierderea pe toate pozițiile;
- precizia: `f32` sau `bf16` = `torch.autocast(bfloat16)` în jurul trecerii înainte și al pierderii, exact ca la
  antrenarea reală (`ModelGPT._autocast`); greutățile, gradientele și AdamW rămân în F32;
- pentru fiecare pas: pierderea (înainte de actualizare), norma gradientului (înainte de tăiere), ms pe pas (cu
  `torch.cuda.synchronize()` pe placă; tragerea loturilor NU intră în timp — loturile sunt trase și puse pe dispozitiv
  înainte), simb/s = lot × context / timp. Pasul 1 (încălzirea) e raportat separat; media e pe pașii 2..N.

Ieșire (în dosarul `--iesire`, care NU trebuie să existe): `rezultat.json`, `loturi.i64` (pozițiile ferestrelor,
int64 little-endian, [pași, lot], pe rânduri — ca OS-ul să verifice că trage aceleași), `reteta.json` (versiunile și
toate setările).

    python -X utf8 unelte/banc_antrenare.py --dispozitiv cpu --lot 2 512 --pasi 3 --precizie f32 --iesire <dosar>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import torch
import torch.nn.functional as F

RADACINA = Path(__file__).resolve().parents[1]
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

SAMANTA = 1134
PASI = 20
EXPERIMENT = 513
BUCATI = "lucru/bucati/w2_amestec_be12"
VALIDARE = "date/tinystories_r2/validare.txt"
TOKENIZER = "date/ws/bpe_16384.json"
MEMORIE_MAXIMA_MB = 7000
TEMPERATURA_MAXIMA = 83
# Optimizatorul liniei #513 (același ca la S132, `unelte/pas_de_aur.py` RETETE["adamw_513"]).
RETETA = {"optimizator": "AdamW", "lr": 5e-5, "betas": [0.9, 0.999], "eps": 1e-8, "weight_decay": 0.1,
          "amsgrad": False, "taiere_gradient": 1.0, "adunare_loturi": 1, "rata": "constantă, fără încălzire"}


def sha256(cale: str | Path) -> str:
    h = hashlib.sha256()
    with open(cale, "rb") as f:
        for bucata in iter(lambda: f.read(1 << 22), b""):
            h.update(bucata)
    return h.hexdigest()


# --- loturile ------------------------------------------------------------------------------


def pozitii_loturi(lungime_sir: int, pasi: int, lot: int, context: int, samanta: int) -> torch.Tensor:
    """Pozițiile ferestrelor pentru fiecare pas [pasi, lot], trase exact ca `DateBucati.lot` (același generator)."""
    if lungime_sir <= context + 1:
        raise ValueError("șirul de antrenare e mai scurt decât contextul")
    g = torch.Generator().manual_seed(samanta)
    return torch.stack([torch.randint(lungime_sir - context - 1, (lot,), generator=g) for _ in range(pasi)])


def loturi(date: Any, pasi: int, lot: int, context: int, samanta: int) -> tuple[torch.Tensor, list]:
    """Pozițiile și loturile (intrare, țintă) pentru toți pașii, prin `DateBucati.ferestre`."""
    poz = pozitii_loturi(date.numar_simboluri(), pasi, lot, context, samanta)
    return poz, [date.ferestre(p, context) for p in poz]


# --- placa -----------------------------------------------------------------------------------


def nvidia_smi() -> dict[str, float] | None:
    """Memoria folosită (MB) și temperatura plăcii, citite cu nvidia-smi; None dacă nu se poate."""
    if shutil.which("nvidia-smi") is None:
        return None
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=memory.used,temperature.gpu", "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=20)
        mem, temp = (float(v) for v in r.stdout.strip().splitlines()[0].split(","))
        return {"memorie_mb": mem, "temperatura": temp}
    except Exception:  # noqa: BLE001 — citirea plăcii nu trebuie să oprească bancul
        return None


def sincronizeaza(dispozitiv: torch.device) -> None:
    if dispozitiv.type == "cuda":
        torch.cuda.synchronize(dispozitiv)


# --- pasul -----------------------------------------------------------------------------------


def optimizator(retea: torch.nn.Module) -> torch.optim.Optimizer:
    """Ca `ModelGPTConversatieMuon._optimizator_nou` (ramura „adamw”): AdamW cu implicitele PyTorch pentru restul."""
    return torch.optim.AdamW(retea.parameters(), lr=RETETA["lr"], betas=tuple(RETETA["betas"]), eps=RETETA["eps"],
                             weight_decay=RETETA["weight_decay"], amsgrad=RETETA["amsgrad"])


def autocast(dispozitiv: torch.device, precizie: str):
    if precizie == "bf16":
        return torch.autocast(dispozitiv.type, dtype=torch.bfloat16)
    if precizie == "f32":
        return torch.autocast(dispozitiv.type, enabled=False)
    raise ValueError(f"precizie necunoscută: {precizie}")


def ruleaza(retea: torch.nn.Module, perechi: list, precizie: str, dispozitiv: torch.device,
            memorie_maxima_mb: float = MEMORIE_MAXIMA_MB, temperatura_maxima: float = TEMPERATURA_MAXIMA,
            ) -> dict[str, Any]:
    """Pașii de antrenare, câte un lot pe pas. Se oprește (cu „oprit”) dacă placa trece de memorie/temperatură."""
    retea.to(dispozitiv).train()
    opt = optimizator(retea)
    perechi = [(x.to(dispozitiv), y.to(dispozitiv)) for x, y in perechi]
    if dispozitiv.type == "cuda":
        torch.cuda.reset_peak_memory_stats(dispozitiv)
    smi_max: dict[str, float] = {}
    pasi: list[dict[str, Any]] = []
    oprit = None
    for i, (x, y) in enumerate(perechi, start=1):
        sincronizeaza(dispozitiv)
        t0 = time.perf_counter()
        opt.zero_grad(set_to_none=True)
        with autocast(dispozitiv, precizie):
            logits = retea(x)
            loss = F.cross_entropy(logits.float().view(-1, logits.size(-1)), y.reshape(-1))
        loss.backward()
        norma = torch.nn.utils.clip_grad_norm_(retea.parameters(), RETETA["taiere_gradient"])
        opt.step()
        sincronizeaza(dispozitiv)
        secunde = time.perf_counter() - t0
        simboluri = x.numel()
        pasi.append({"pas": i, "pierdere": float(loss.item()), "norma_gradient": float(norma.item()),
                     "ms": secunde * 1000, "simb_s": simboluri / secunde})
        if dispozitiv.type == "cuda":
            smi = nvidia_smi()
            if smi:
                for k, v in smi.items():
                    smi_max[k] = max(smi_max.get(k, 0.0), v)
            alocat = torch.cuda.max_memory_allocated(dispozitiv) / 2**20
            if alocat > memorie_maxima_mb or smi_max.get("memorie_mb", 0) > memorie_maxima_mb:
                oprit = f"memoria plăcii peste {memorie_maxima_mb} MB la pasul {i}: nu încape în 7 GB"
            elif smi_max.get("temperatura", 0) > temperatura_maxima:
                oprit = f"placa peste {temperatura_maxima} °C la pasul {i}"
            if oprit:
                break
        if not math.isfinite(pasi[-1]["pierdere"]):
            oprit = f"pierderea nu e un număr finit la pasul {i}"
            break
    restul = pasi[1:]
    r: dict[str, Any] = {
        "pasi": pasi,
        "pas1": pasi[0] if pasi else None,
        "media_pasi_2_n": ({"ms": sum(p["ms"] for p in restul) / len(restul),
                            "simb_s": sum(p["simb_s"] for p in restul) / len(restul),
                            "simb_s_din_timpul_total": sum(x.numel() for x, _ in perechi[1:len(pasi)])
                            / (sum(p["ms"] for p in restul) / 1000), "pasi": len(restul)} if restul else None),
        "pierderi": {f"pas{p['pas']}": p["pierdere"] for p in pasi if p["pas"] in (1, 10, 20) or p["pas"] == len(pasi)},
        "oprit": oprit,
    }
    if dispozitiv.type == "cuda":
        r["memorie_placa"] = {"max_memory_allocated_mb": torch.cuda.max_memory_allocated(dispozitiv) / 2**20,
                              "max_memory_reserved_mb": torch.cuda.max_memory_reserved(dispozitiv) / 2**20,
                              "nvidia_smi_max": smi_max or None}
    return r


# --- ieșirea ---------------------------------------------------------------------------------


def scrie_i64(cale: Path, t: torch.Tensor) -> dict[str, Any]:
    octeti = t.detach().cpu().contiguous().to(torch.int64).numpy().astype("<i8").tobytes()
    cale.write_bytes(octeti)
    return {"sha256": hashlib.sha256(octeti).hexdigest(), "octeti": len(octeti), "forma": list(t.shape)}


def versiuni(dispozitiv: torch.device) -> dict[str, Any]:
    import numpy

    v = {"python": sys.version.split()[0], "pytorch": torch.__version__, "numpy": numpy.__version__,
         "cuda_pytorch": torch.version.cuda, "procesor": platform.processor(), "sistem": platform.platform(),
         "fire_pytorch": torch.get_num_threads()}
    if dispozitiv.type == "cuda":
        v["placa"] = torch.cuda.get_device_name(dispozitiv)
        v["cudnn"] = torch.backends.cudnn.version()
        v["tf32_matmul"] = torch.backends.cuda.matmul.allow_tf32
    return v


def scrie_iesire(iesire: Path, poz: torch.Tensor, rezultat: dict[str, Any], reteta: dict[str, Any]) -> None:
    iesire.mkdir(parents=True)
    reteta = {**reteta, "loturi.i64": scrie_i64(iesire / "loturi.i64", poz)}
    (iesire / "reteta.json").write_text(json.dumps(reteta, ensure_ascii=False, indent=1), encoding="utf-8")
    (iesire / "rezultat.json").write_text(json.dumps(rezultat, ensure_ascii=False, indent=1), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--pasi", type=int, default=PASI)
    p.add_argument("--lot", type=int, nargs=2, default=[2, 512], metavar=("B", "T"))
    p.add_argument("--precizie", choices=["f32", "bf16"], default="f32")
    p.add_argument("--dispozitiv", choices=["cpu", "cuda"], default="cpu")
    p.add_argument("--samanta", type=int, default=SAMANTA)
    p.add_argument("--experiment", type=int, default=EXPERIMENT)
    p.add_argument("--bucati", default=BUCATI)
    p.add_argument("--fire", type=int, default=0, help="firele PyTorch pe procesor (0 = cum sunt)")
    p.add_argument("--iesire", required=True)
    a = p.parse_args(argv)
    iesire = Path(a.iesire)
    if iesire.exists():
        raise SystemExit(f"{iesire} există deja: nu scriu peste el")
    if a.dispozitiv == "cuda" and not torch.cuda.is_available():
        raise SystemExit("placa nu e disponibilă (CUDA)")
    if a.fire:
        torch.set_num_threads(a.fire)
    dispozitiv = torch.device(a.dispozitiv)
    lot, context = a.lot

    from kronos.cai import gaseste_model
    from kronos.jurnal import Jurnal
    from module.date_bucati import DateBucati
    from unelte.modele_salvate import fisa_modelului, incarca_modelul
    from unelte.pas_de_aur import verifica_fara_dropout, verifica_optimizator_513

    fisa = fisa_modelului(Jurnal(RADACINA / "lucru"), a.experiment)
    cale_model = Path(gaseste_model(fisa["model_salvat"]))
    sha_inainte = sha256(cale_model)
    model = incarca_modelul(fisa, "cpu")
    optimizator_citit = verifica_optimizator_513(model)
    retea = model.retea.float()
    if retea.memorie is not None:
        raise SystemExit("rețeaua are memorie: nu e cazul lui #513")
    verifica_fara_dropout(retea)
    if context > retea.context:
        raise SystemExit(f"contextul {context} > contextul modelului {retea.context}")
    date = DateBucati(str(RADACINA / a.bucati), str(RADACINA / VALIDARE), str(RADACINA / TOKENIZER))
    poz, perechi = loturi(date, a.pasi, lot, context, a.samanta)
    torch.manual_seed(a.samanta)
    smi_inainte = nvidia_smi() if a.dispozitiv == "cuda" else None
    rezultat = ruleaza(retea, perechi, a.precizie, dispozitiv)
    sha_dupa = sha256(cale_model)
    rezultat = {"varianta": {"lot": lot, "context": context, "precizie": a.precizie, "dispozitiv": a.dispozitiv,
                             "pasi_cerute": a.pasi, "samanta": a.samanta},
                "placa_inainte": smi_inainte, **rezultat,
                "sha256_model": {"inainte": sha_inainte, "dupa": sha_dupa, "neschimbat": sha_inainte == sha_dupa}}
    reteta = {
        "ce_este": "S134 bancul de antrenare: pașii lui #513 în PyTorch, pentru comparația cinstită cu OS-ul",
        "model": {"experiment": fisa["id"], "linie": fisa.get("linie"), "fisier": cale_model.as_posix(),
                  "sha256": sha_inainte, "clasa": fisa["module"]["model"]["cale"],
                  "parametri": sum(t.numel() for t in retea.parameters())},
        "date": {**date.descriere(), "director": a.bucati,
                 "nota": "textul (amestecul W2) al liniei #513 — la antrenarea reală lotul avea și 45 % conversație și "
                         "5 % hrană (FISA_ANTRENARE.md §2); aici doar textul, ca OS-ul să tragă aceleași ferestre"},
        "loturi": {"cum": "g = torch.Generator().manual_seed(samanta); la fiecare pas pozitii = torch.randint("
                          "len(sir) − context − 1, (lot,), generator=g) (= DateBucati.lot); fereastra de la p: intrare = "
                          "sir[p : p+context], ținta = sir[p+1 : p+context+1]",
                   "samanta": a.samanta, "lot": lot, "context": context, "pasi": a.pasi, "lungime_sir": len(date._sir)},
        "pas": {**RETETA, "precizie": a.precizie,
                "bf16": "torch.autocast(bfloat16) în jurul trecerii înainte și al pierderii (ca ModelGPT._autocast); "
                        "greutățile, gradientele și AdamW în F32",
                "ordinea": "zero_grad → înainte → cross_entropy(logits.float(), media pe toate pozițiile) → înapoi → "
                           "clip_grad_norm_(1,0) (norma raportată = înainte de tăiere) → AdamW.step()",
                "timp": "de la zero_grad până după step, cu torch.cuda.synchronize() la ambele capete pe placă; "
                        "loturile sunt deja pe dispozitiv (tragerea lor nu intră în timp)",
                "dropout": 0.0, "optimizator_citit_din_model": optimizator_citit},
        "versiuni": versiuni(dispozitiv),
        "salvat": "niciun model; nimic în jurnalul de experimente",
    }
    scrie_iesire(iesire, poz, rezultat, reteta)
    print(json.dumps({"iesire": iesire.as_posix(), "pierderi": rezultat["pierderi"], "pas1_ms": rezultat["pas1"]["ms"],
                      "media_2_n": rezultat["media_pasi_2_n"], "oprit": rezultat["oprit"],
                      "sha_neschimbat": sha_inainte == sha_dupa}, ensure_ascii=False))
    if sha_inainte != sha_dupa:
        print("EROARE: modelul s-a schimbat pe disc", file=sys.stderr)
        return 3
    return 2 if rezultat["oprit"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
