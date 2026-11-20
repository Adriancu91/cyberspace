"""S130 (C-153): viteza unui model salvat de Kronos în PyTorch, simbol cu simbol, greedy.

Încarcă modelul exact ca exportul KGR1 (`unelte/exporta_greutati.py --experiment N`: fișa din jurnal, aceleași greutăți,
tokenizerul din model), codifică textul și generează `--simboluri` simboluri noi, fără întâmplare (argmax). Fiecare simbol
recalculează tot textul (rețeaua n-are memoria pașilor). Pentru fiecare variantă: o rulare de încălzire, apoi `--repetari`
rulări cu ceasul `time.perf_counter()` (pe placă, `torch.cuda.synchronize()` înainte de oprire); se scrie mediana.

Variantele: a = placa FP32, b = memoria pașilor (doar dacă rețeaua o are; altfel „nu are”), c = procesorul FP32,
d16 = placa FP16 (o copie în memorie, nimic salvat). Nimic nu se scrie peste model: SHA-256 înainte și după.

    python -X utf8 unelte/viteza_inferenta.py --experiment 513 --iesire lucru/s130/s130.json \
        --asteptat 44,10,73,2524,10766,1438,1505,1428,1765,99,1547,3644,44,10,15879,1505 --kgr lucru/export/kronos_513_q8_0.kgr
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import platform
import statistics
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any

import torch

RADACINA = Path(__file__).resolve().parents[1]
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))


def sha256(cale: str | Path) -> str:
    h = hashlib.sha256()
    with open(cale, "rb") as f:
        for bucata in iter(lambda: f.read(1 << 20), b""):
            h.update(bucata)
    return h.hexdigest()


def _sincron(dispozitiv: str) -> None:
    if dispozitiv.startswith("cuda"):
        torch.cuda.synchronize()


@torch.no_grad()
def greedy(retea: Any, intrare: list[int], n: int, dispozitiv: str, context: int) -> list[int]:
    """n simboluri noi, fiecare = argmax pe ultima poziție; la fiecare pas tot textul (ultimele `context`) prin rețea."""
    noi: list[int] = []
    for _ in range(n):
        toate = intrare + noi
        idx = torch.tensor([toate[-context:]], dtype=torch.long, device=dispozitiv)
        noi.append(int(retea(idx)[0, -1].float().argmax().item()))
    return noi


def masoara(retea: Any, intrare: list[int], n: int, dispozitiv: str, context: int, repetari: int = 5,
            incalzire: int = 1) -> dict[str, Any]:
    retea.eval()
    for _ in range(incalzire):
        greedy(retea, intrare, n, dispozitiv, context)
    _sincron(dispozitiv)
    timpi: list[float] = []
    simboluri: list[int] = []
    for _ in range(repetari):
        _sincron(dispozitiv)
        t0 = time.perf_counter()
        simboluri = greedy(retea, intrare, n, dispozitiv, context)
        _sincron(dispozitiv)
        timpi.append(time.perf_counter() - t0)
    mediana = statistics.median(timpi)
    return {
        "simboluri": simboluri,
        "secunde_rulari": [round(t, 6) for t in timpi],
        "secunde_mediana": round(mediana, 6),
        "simb_pe_s": round(n / mediana, 2),
        "ms_pe_simbol": round(1000 * mediana / n, 3),
    }


def compara(simboluri: list[int], asteptat: list[int] | None) -> dict[str, Any]:
    if not asteptat:
        return {"identice": None}
    diferente = [{"pozitie": i, "asteptat": a, "iesit": s} for i, (a, s) in enumerate(zip(asteptat, simboluri)) if a != s]
    if len(simboluri) != len(asteptat):
        diferente.append({"lungime_asteptata": len(asteptat), "lungime_iesita": len(simboluri)})
    return {"identice": not diferente, "diferente": diferente}


def are_memoria_pasilor(retea: Any) -> bool:
    """Rețeaua primește/întoarce o memorie a pașilor (past_key_values, kv_cache)? _GPT de acum: nu."""
    import inspect

    parametri = inspect.signature(retea.forward).parameters
    return any(p in parametri for p in ("past_key_values", "kv_cache", "cache", "memorie_pasi"))


def _nvidia_smi(argumente: list[str]) -> str:
    try:
        return subprocess.run(["nvidia-smi", *argumente], capture_output=True, text=True, timeout=60).stdout
    except (OSError, subprocess.SubprocessError) as e:
        return f"nvidia-smi n-a mers: {e}"


def _placa_in_timpul(retea: Any, intrare: list[int], n: int, context: int) -> str:
    """`nvidia-smi -q -d PERFORMANCE,CLOCK` cât timp varianta (a) generează (rulări în plus, necronometrate)."""
    iesire: dict[str, str] = {}
    fir = threading.Thread(target=lambda: iesire.update(t=_nvidia_smi(["-q", "-d", "PERFORMANCE,CLOCK"])))
    fir.start()
    while fir.is_alive():
        greedy(retea, intrare, n, "cuda", context)
    fir.join()
    return iesire.get("t", "")


def ruleaza(model: Any, text: str, n: int, asteptat: list[int] | None, variante: list[str], repetari: int) -> dict[str, Any]:
    intrare = list(model.tok.codifica(text))
    context = int(model.setari["context"])
    retea_cpu = model.retea.float().to("cpu").eval()
    rezultat: dict[str, Any] = {"text": text, "intrare": intrare, "simboluri_noi": n, "repetari": repetari,
                                "incalzire": 1, "variante": {}}
    placa = torch.cuda.is_available()
    if "a" in variante or "d16" in variante:
        if not placa:
            raise RuntimeError("PyTorch nu vede placa (CUDA)")
        retea_placa = copy.deepcopy(retea_cpu).to("cuda").eval()
    if "a" in variante:
        torch.cuda.reset_peak_memory_stats()
        r = masoara(retea_placa, intrare, n, "cuda", context, repetari)
        r["memorie_max_mb"] = round(torch.cuda.max_memory_allocated() / 2**20, 1)
        r["nvidia_smi_performance_clock"] = _placa_in_timpul(retea_placa, intrare, n, context)
        rezultat["variante"]["a"] = {"dispozitiv": "cuda", "precizie": "fp32", **r, **compara(r["simboluri"], asteptat)}
    if "b" in variante:
        rezultat["variante"]["b"] = {"dispozitiv": "cuda", "precizie": "fp32",
                                     "nu_are": not are_memoria_pasilor(retea_cpu),
                                     "nota": "rețeaua _GPT n-are memoria pașilor (KV cache); nu s-a scris acum"}
    if "c" in variante:
        r = masoara(retea_cpu, intrare, n, "cpu", context, repetari)
        r["fire_torch"] = torch.get_num_threads()
        rezultat["variante"]["c"] = {"dispozitiv": "cpu", "precizie": "fp32", **r, **compara(r["simboluri"], asteptat)}
    if "d16" in variante:
        retea16 = copy.deepcopy(retea_placa).half().eval()
        torch.cuda.reset_peak_memory_stats()
        r = masoara(retea16, intrare, n, "cuda", context, repetari)
        r["memorie_max_mb"] = round(torch.cuda.max_memory_allocated() / 2**20, 1)
        rezultat["variante"]["d16"] = {"dispozitiv": "cuda", "precizie": "fp16", **r, **compara(r["simboluri"], asteptat)}
        del retea16
    return rezultat


def versiuni() -> dict[str, Any]:
    v: dict[str, Any] = {"python": platform.python_version(), "torch": torch.__version__, "cuda_torch": torch.version.cuda,
                         "cudnn": torch.backends.cudnn.version(), "procesor": platform.processor(),
                         "procesor_fire_logice": __import__("os").cpu_count(), "sistem": platform.platform()}
    if torch.cuda.is_available():
        v["placa"] = torch.cuda.get_device_name(0)
    v["nvidia_smi"] = _nvidia_smi(["--query-gpu=name,driver_version,memory.used,memory.total,temperature.gpu,"
                                   "pstate,clocks.sm,clocks.max.sm", "--format=csv"]).strip()
    return v


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--experiment", type=int, required=True)
    p.add_argument("--text", default="Buna ziua")
    p.add_argument("--simboluri", type=int, default=16)
    p.add_argument("--repetari", type=int, default=5)
    p.add_argument("--variante", default="a,b,c,d16")
    p.add_argument("--asteptat", default="", help="simbolurile așteptate, despărțite prin virgulă")
    p.add_argument("--kgr", default="", help="un fișier .kgr doar citit: SHA-256 înainte și după")
    p.add_argument("--iesire", required=True)
    a = p.parse_args(argv)
    iesire = Path(a.iesire)
    if iesire.exists():
        raise SystemExit(f"{iesire} există deja: nu scriu peste el")
    from kronos.cai import gaseste_model
    from kronos.jurnal import Jurnal
    from unelte.modele_salvate import fisa_modelului, incarca_modelul

    fisa = fisa_modelului(Jurnal(RADACINA / "lucru"), a.experiment)
    cale_model = Path(gaseste_model(fisa["model_salvat"]))
    if not cale_model.exists():
        cale_model = cale_model.with_suffix(".pt")
    fisiere = [cale_model] + ([Path(a.kgr)] if a.kgr else [])
    sha_inainte = {f.as_posix(): sha256(f) for f in fisiere}
    model = incarca_modelul(fisa, "cpu")  # ca la export; apoi copii pe placă
    asteptat = [int(x) for x in a.asteptat.split(",") if x.strip()] or None
    t0 = time.time()
    rezultat = ruleaza(model, a.text, a.simboluri, asteptat, [v.strip() for v in a.variante.split(",")], a.repetari)
    rezultat["text_generat_a"] = model.tok.decodeaza(rezultat["variante"].get("a", {}).get("simboluri", [])) \
        if "a" in rezultat["variante"] else ""
    sha_dupa = {f.as_posix(): sha256(f) for f in fisiere}
    rezultat.update({
        "experiment": fisa["id"], "linie": fisa.get("linie", ""), "clasa": fisa["module"]["model"]["cale"],
        "model_salvat": cale_model.as_posix(), "asteptat": asteptat, "versiuni": versiuni(),
        "sha256_inainte": sha_inainte, "sha256_dupa": sha_dupa, "sha_neschimbate": sha_inainte == sha_dupa,
        "secunde_total": round(time.time() - t0, 1), "comanda": " ".join(sys.argv),
    })
    iesire.parent.mkdir(parents=True, exist_ok=True)
    iesire.write_text(json.dumps(rezultat, ensure_ascii=False, indent=1), encoding="utf-8")
    sumar = {k: {c: v.get(c) for c in ("simb_pe_s", "ms_pe_simbol", "identice", "nu_are")} for k, v in rezultat["variante"].items()}
    print(json.dumps({"iesire": iesire.as_posix(), "sha_neschimbate": rezultat["sha_neschimbate"], **sumar}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
