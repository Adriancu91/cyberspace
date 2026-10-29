"""S47: bancul CCM — verifică o variantă față de referință și o măsoară.

Reguli (docs/CCM_plan.md): o variantă e acceptată doar dacă dă ACELEAȘI simboluri greedy ca referința (`MotorBrut`,
desfacere la încărcare) pe fiecare fișier și text, iar logit-urile (pe tot șirul: început + simbolurile greedy) sunt în
toleranța scrisă înainte. Pe vectorii KGR1 se cer și simbolurile greedy scrise în `vectori.json`. Timpul se măsoară
complet (încărcarea fișierului + desfacere + început + completare), pe ≥ 5 repetări: median și împrăștiere.

Firele OpenBLAS se aleg doar la pornirea procesului (OPENBLAS_NUM_THREADS), așa că fiecare (variantă, fire) se încearcă
într-un proces nou: `incearca` face verificarea și măsurarea acolo; `toate` le pornește pe rând și scrie rezultatul.

Folosire:
    python -X utf8 -m module.calcul.banc toate --kgr lucru/export/kronos_459_q8_0.kgr --iesire lucru/ccm/s47.json
    python -X utf8 -m module.calcul.banc incearca --varianta transpus --kgr ...    # un singur proces, fără fire schimbate
    python -X utf8 -m module.calcul.banc placa --iesire lucru/ccm/s49.json        # S49: procesor (referința) + placa

S49: variantele pe placă (`placa_fp32/fp16/bf16`) trec prin aceeași verificare; una respinsă se măsoară totuși (ca
informație), dar nu poate fi aleasă. Memoria plăcii se notează la fiecare (PyTorch maxim + nvidia-smi la final).
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable

import numpy as np

RADACINA = Path(__file__).resolve().parents[2]
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from unelte.inferenta_bruta import MotorBrut  # noqa: E402

TOLERANTA_LOGITS = 1e-3  # |Δ logit| maxim, absolut (scrisă înainte în raportul S47)
TEXT_MASURARE = "Ana are mere."
SIMBOLURI = 64
REPETARI = 5
VECTORI = RADACINA / "integrare/kronos/vectori"
TEXTE_VERIFICARE = ["Ana are mere.", "Capitala României este", "def suma(a, b):"]
FIRE = ("1", "4", "toate")


def _referinta(cale: str | Path) -> MotorBrut:
    return MotorBrut(cale, "la_incarcare")


def _simboluri(motor: Any, text: str | list[int]) -> list[int]:
    """Fără tokenizer în fișier (modelele sintetice din teste): octeții textului, modulo vocabular."""
    if isinstance(text, list):
        return list(text)
    if motor.tok is None:
        return [b % motor.vocabular for b in text.encode("utf-8")]
    return list(motor.tok.codifica(text))


def verifica(fabrica: Callable[[Any], Any], fisiere: list[str | Path], texte: list[str | list[int]],
             simboluri: int = 16, toleranta: float = TOLERANTA_LOGITS,
             asteptate: dict[str, list[list[int]]] | None = None) -> dict[str, Any]:
    """Varianta față de referință: simbolurile greedy identice și |Δ logit| ≤ toleranța, pe fiecare (fișier, text).
    `asteptate`: pe nume de fișier, simbolurile greedy scrise dinainte (vectorii KGR1), câte o listă pe text."""
    cazuri, motive = [], []
    for cale in fisiere:
        ref, var = _referinta(cale), fabrica(cale)
        for j, text in enumerate(texte):
            s = _simboluri(ref, text)
            g_ref, _ = ref.completeaza_simboluri(s, simboluri)
            g_var, _ = var.completeaza_simboluri(s, simboluri)
            g_ref, g_var = [int(x) for x in g_ref], [int(x) for x in g_var]
            sir = (s + g_ref[:-1])[-ref.context:]
            dif = float(np.abs(np.asarray(var.logits(sir), dtype=np.float64)
                               - np.asarray(ref.logits(sir), dtype=np.float64)).max())
            caz = {"fisier": Path(cale).name, "text": text if isinstance(text, str) else f"{len(text)} simboluri",
                   "simboluri_identice": g_var == g_ref, "dif_logits_max": dif}
            if asteptate and Path(cale).name in asteptate:
                caz["ca_in_vectori"] = g_var[:len(asteptate[Path(cale).name][j])] == asteptate[Path(cale).name][j]
                if not caz["ca_in_vectori"]:
                    motive.append(f"{caz['fisier']} {caz['text']!r}: altfel decât vectori.json")
            if g_var != g_ref:
                motive.append(f"{caz['fisier']} {caz['text']!r}: alte simboluri greedy")
            if not dif <= toleranta:
                motive.append(f"{caz['fisier']} {caz['text']!r}: |Δ logit| {dif:.3g} > {toleranta:g}")
            cazuri.append(caz)
    return {"acceptata": not motive, "motive": motive, "toleranta": toleranta, "cazuri": cazuri,
            "dif_logits_max": max((c["dif_logits_max"] for c in cazuri), default=0.0)}


def masoara(fabrica: Callable[[Any], Any], cale: str | Path, text: str | list[int] = TEXT_MASURARE,
            simboluri: int = SIMBOLURI, repetari: int = REPETARI) -> dict[str, Any]:
    """Timpul complet pe repetări: încărcare (cu desfacerea) + început + completare. Median și împrăștiere."""
    if repetari < 1:
        raise ValueError("cel puțin o repetare")
    rand: list[dict[str, float]] = []
    noi_prima = None
    for _ in range(repetari):
        t0 = time.perf_counter()
        m = fabrica(cale)
        t1 = time.perf_counter()
        noi, timpi = m.completeaza_simboluri(_simboluri(m, text), simboluri)
        t2 = time.perf_counter()
        noi = [int(x) for x in noi]
        if noi_prima is None:
            noi_prima = noi
        elif noi != noi_prima:
            raise RuntimeError("varianta nu dă aceleași simboluri la fiecare repetare")
        rand.append({"incarcare": t1 - t0, "inceput": timpi["secunde_inceput"], "restul": timpi["secunde_restul"],
                     "total": t2 - t0, "simboluri_pe_secunda": timpi["simboluri_pe_secunda"]})

    def rezumat(cheie: str) -> dict[str, float]:
        v = [r[cheie] for r in rand]
        return {"median": statistics.median(v), "min": min(v), "max": max(v),
                "imprastiere_relativa": (max(v) - min(v)) / statistics.median(v) if statistics.median(v) else 0.0}

    return {"repetari": repetari, "simboluri": simboluri, "pe_repetare": rand,
            **{k: rezumat(k) for k in ("incarcare", "inceput", "restul", "total", "simboluri_pe_secunda")}}


def _asteptate_vectori() -> dict[str, list[list[int]]]:
    j = VECTORI / "vectori.json"
    if not j.exists():
        return {}
    v = json.loads(j.read_text(encoding="utf-8"))
    return {Path(v["fisiere"][fel]["nume"]).name: [x["greedy_5"] for x in v[fel]] for fel in v["fisiere"]}


def incearca(varianta: str, kgr: str | Path, simboluri: int = SIMBOLURI, repetari: int = REPETARI,
             vectori: bool = True) -> dict[str, Any]:
    """În procesul de acum: verificarea pe vectorii KGR1 (5 simboluri, ca în vectori.json) și pe `kgr`, apoi măsurarea
    (doar dacă e acceptată)."""
    from module.calcul.variante import TOATE, VARIANTE_PLACA

    fabrica = TOATE[varianta]
    asteptate = _asteptate_vectori() if vectori else {}
    v_vec = (verifica(fabrica, sorted(VECTORI.glob("*.kgr")), TEXTE_VERIFICARE, 5, asteptate=asteptate)
             if asteptate else None)
    v_kgr = verifica(fabrica, [kgr], TEXTE_VERIFICARE, simboluri)
    acceptata = v_kgr["acceptata"] and (v_vec is None or v_vec["acceptata"])
    rez = {"varianta": varianta, "fire": os.environ.get("OPENBLAS_NUM_THREADS", "toate"), "acceptata": acceptata,
           "verificare_vectori": v_vec, "verificare_model": v_kgr,
           # S49: o variantă de placă respinsă se măsoară totuși (doar ca informație, nu intră în alegere)
           "masurare": (masoara(fabrica, kgr, TEXT_MASURARE, simboluri, repetari)
                        if acceptata or varianta in VARIANTE_PLACA else None)}
    if varianta in VARIANTE_PLACA:
        rez["memorie_placa_mb"] = _memorie_placa()
    return rez


def _memorie_placa() -> dict[str, Any] | None:
    """S49: maximul PyTorch în procesul acesta + ce vede nvidia-smi pe toată placa (cu contextul CUDA), la final."""
    try:
        import torch
    except ImportError:
        return None
    if not torch.cuda.is_available():
        return None
    rez: dict[str, Any] = {"alocat_max": torch.cuda.max_memory_allocated() / 2 ** 20,
                           "rezervat_max": torch.cuda.max_memory_reserved() / 2 ** 20}
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=memory.used,temperature.gpu", "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=20)
        mem, temp = (float(x) for x in r.stdout.strip().splitlines()[0].split(","))
        rez.update(nvidia_smi_mb=mem, temperatura=temp)
    except (OSError, ValueError, IndexError, subprocess.SubprocessError):
        pass
    return rez


def in_proces_nou(varianta: str, fire: str, kgr: str | Path, simboluri: int = SIMBOLURI,
                  repetari: int = REPETARI, vectori: bool = True) -> dict[str, Any]:
    env = dict(os.environ)
    for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        env.pop(k, None)
        if fire != "toate":
            env[k] = str(fire)
    cmd = [sys.executable, "-X", "utf8", "-m", "module.calcul.banc", "incearca", "--varianta", varianta,
           "--kgr", str(kgr), "--simboluri", str(simboluri), "--repetari", str(repetari)]
    if not vectori:
        cmd.append("--fara-vectori")
    r = subprocess.run(cmd, cwd=RADACINA, env=env, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        raise RuntimeError(f"{varianta}/{fire}: cod {r.returncode}\n{r.stderr[-2000:]}")
    return json.loads(r.stdout)


def toate(kgr: str | Path, variante: list[str] | None = None, fire: tuple[str, ...] = FIRE,
          simboluri: int = SIMBOLURI, repetari: int = REPETARI,
          combinatii: list[tuple[str, str]] | None = None) -> dict[str, Any]:
    """`combinatii` (S49): perechile (variantă, fire) de încercat, în locul tuturor variantelor × toate firele."""
    from module.calcul.variante import REFERINTA, VARIANTE

    if combinatii is None:
        combinatii = [(v, f) for v in (variante or list(VARIANTE)) for f in fire]
    rez = [in_proces_nou(v, f, kgr, simboluri, repetari) for v, f in combinatii]
    ref = next((r for r in rez if r["varianta"] == REFERINTA and r["fire"] == "toate" and r["acceptata"]), None)
    for r in rez:
        if r["acceptata"] and ref is not None:
            r["fata_de_referinta_total"] = ref["masurare"]["total"]["median"] / r["masurare"]["total"]["median"]
            r["fata_de_referinta_simb_s"] = (r["masurare"]["simboluri_pe_secunda"]["median"]
                                             / ref["masurare"]["simboluri_pe_secunda"]["median"])
    from module.calcul.variante import VARIANTE_PLACA

    def cea_mai_rapida(lista: list[dict[str, Any]]) -> dict[str, str] | None:
        lista = [r for r in lista if r["acceptata"]]
        if not lista:
            return None
        r = min(lista, key=lambda r: r["masurare"]["total"]["median"])
        return {"varianta": r["varianta"], "fire": r["fire"]}

    return {"kgr": str(kgr), "text": TEXT_MASURARE, "simboluri": simboluri, "repetari": repetari,
            "toleranta_logits": TOLERANTA_LOGITS, "nuclee": os.cpu_count(), "rezultate": rez,
            "cea_mai_rapida_pe_total": cea_mai_rapida(rez),
            "cea_mai_rapida_pe_procesor": cea_mai_rapida([r for r in rez if r["varianta"] not in VARIANTE_PLACA]),
            "cea_mai_rapida_pe_placa": cea_mai_rapida([r for r in rez if r["varianta"] in VARIANTE_PLACA])}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="comanda", required=True)
    i = sub.add_parser("incearca")
    i.add_argument("--varianta", required=True)
    t = sub.add_parser("toate")
    t.add_argument("--iesire", required=True)
    t.add_argument("--profil", action="store_true", help="și profilul pe operații (la_incarcare și la_pas)")
    pl = sub.add_parser("placa", help="S49: referința pe procesor (1 fir, toate) și variantele pe placă, în aceeași rulare")
    pl.add_argument("--iesire", required=True)
    for x in (i, t, pl):
        x.add_argument("--kgr", default="lucru/export/kronos_459_q8_0.kgr")
        x.add_argument("--simboluri", type=int, default=SIMBOLURI)
        x.add_argument("--repetari", type=int, default=REPETARI)
    i.add_argument("--fara-vectori", action="store_true")
    a = p.parse_args(argv)
    if a.comanda == "incearca":
        sys.stdout.write(json.dumps(incearca(a.varianta, a.kgr, a.simboluri, a.repetari, not a.fara_vectori),
                                    ensure_ascii=False))
        return 0
    iesire = Path(a.iesire)
    if iesire.exists():
        raise SystemExit(f"{iesire} există deja: măsurarea se face o singură dată")
    if a.comanda == "placa":
        from module.calcul.variante import REFERINTA, VARIANTE_PLACA

        combinatii = [(REFERINTA, "1"), (REFERINTA, "toate")] + [(v, "toate") for v in VARIANTE_PLACA]
        rez = toate(a.kgr, simboluri=a.simboluri, repetari=a.repetari, combinatii=combinatii)
    else:
        rez = toate(a.kgr, simboluri=a.simboluri, repetari=a.repetari)
    if a.profil:
        from module.calcul.profil import profil

        rez["profil"] = [profil(a.kgr, TEXT_MASURARE, a.simboluri, d) for d in ("la_incarcare", "la_pas")]
    iesire.parent.mkdir(parents=True, exist_ok=True)
    iesire.write_bytes(json.dumps(rez, ensure_ascii=False, indent=1).encode("utf-8"))
    print(json.dumps({"cea_mai_rapida_pe_total": rez["cea_mai_rapida_pe_total"],
                      "cea_mai_rapida_pe_placa": rez["cea_mai_rapida_pe_placa"],
                      "pe_variante": [(r["varianta"], r["fire"], r["acceptata"],
                                       r["masurare"] and round(r["masurare"]["total"]["median"], 3),
                                       r["masurare"] and round(r["masurare"]["simboluri_pe_secunda"]["median"], 1))
                                      for r in rez["rezultate"]]}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
