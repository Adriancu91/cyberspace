"""S142 (C-168 p.7): viteza la scris a unui model salvat de Kronos în PyTorch, CU memoria de context (KV cache).

Încarcă modelul exact ca `unelte/viteza_inferenta.py` (S130): fișa din jurnal, aceleași greutăți, tokenizerul din model.
Rețeaua `_GPT` din `module/model_gpt.py` n-are memoria pașilor, deci aici e scrisă o funcție proprie de „pas înainte”
(`pas_inainte`) care REFOLOSEȘTE greutățile rețelei încărcate (aceleași straturi, aceleași matrice; `module/` nu se
schimbă): la primul pas trece tot textul și păstrează cheile și valorile atenției (K, V) din fiecare strat; la fiecare
simbol nou trece doar simbolul acela, cu poziția lui, și îl lasă să se uite la K, V păstrate.

Opțiuni: `--dispozitiv cpu|cuda`, `--precizie f32|f16|bf16` (o copie în memorie, nimic salvat), `--cache da|nu`,
`--simboluri N`, `--text "Buna ziua"`, `--iesire <dosar>` (scrie `<dosar>/rezultat.json`). Măsurarea, ca la S130: o rulare
de încălzire, apoi `--repetari` rulări (implicit 5), mediana; pe placă `torch.cuda.synchronize()` înainte de oprirea
ceasului. SHA-256 al modelului (și al `--kgr`, dacă e dat) înainte și după.

    python -X utf8 unelte/viteza_scris_kv.py --dispozitiv cpu --precizie f32 --cache da --simboluri 16 \
        --iesire lucru/s142/proba_cpu_f32_cache --kgr lucru/export/kronos_513_q8_0.kgr
"""

from __future__ import annotations

import argparse
import copy
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Any

import torch
import torch.nn.functional as F

RADACINA = Path(__file__).resolve().parents[1]
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from unelte.viteza_inferenta import compara, sha256, versiuni  # noqa: E402

PRECIZII = {"f32": torch.float32, "f16": torch.float16, "bf16": torch.bfloat16}
ASTEPTAT_513 = [44, 10, 73, 2524, 10766, 1438, 1505, 1428, 1765, 99, 1547, 3644, 44, 10, 15879, 1505]

Memorie = list[tuple[torch.Tensor, torch.Tensor]]


def _sincron(dispozitiv: str) -> None:
    if dispozitiv.startswith("cuda"):
        torch.cuda.synchronize()


def _atentie_cu_memorie(bloc: Any, h: torch.Tensor, kv: tuple[torch.Tensor, torch.Tensor] | None
                        ) -> tuple[torch.Tensor, tuple[torch.Tensor, torch.Tensor]]:
    """Atenția din `bloc.atentie` (nn.MultiheadAttention, batch_first), cu aceleași greutăți, plus K, V păstrate."""
    mha = bloc.atentie
    if mha.bias_k is not None or mha.add_zero_attn or not mha._qkv_same_embed_dim:
        raise ValueError("atenția are o formă pe care unealta n-o știe (bias_k / add_zero_attn / kdim≠vdim)")
    b, t, c = h.shape
    nh = mha.num_heads
    d = c // nh
    q, k, v = F.linear(h, mha.in_proj_weight, mha.in_proj_bias).split(c, dim=-1)
    q = q.view(b, t, nh, d).transpose(1, 2)
    k = k.view(b, t, nh, d).transpose(1, 2)
    v = v.view(b, t, nh, d).transpose(1, 2)
    if kv is not None:
        k = torch.cat([kv[0], k], dim=2)
        v = torch.cat([kv[1], v], dim=2)
    trecut = k.size(2) - t
    if t == 1:  # simbolul nou se uită la tot ce e înainte și la el însuși
        y = F.scaled_dot_product_attention(q, k, v)
    elif trecut == 0:
        y = F.scaled_dot_product_attention(q, k, v, is_causal=True)
    else:
        i = torch.arange(t, device=h.device).unsqueeze(1)
        j = torch.arange(trecut + t, device=h.device).unsqueeze(0)
        y = F.scaled_dot_product_attention(q, k, v, attn_mask=j <= trecut + i)
    y = y.transpose(1, 2).reshape(b, t, c)
    return mha.out_proj(y), (k, v)


@torch.no_grad()
def pas_inainte(retea: Any, idx: torch.Tensor, memorie: Memorie | None) -> tuple[torch.Tensor, Memorie]:
    """Logit-urile pentru `idx` (forma [1, t]), știind K, V ale simbolurilor de dinainte; întoarce și memoria nouă."""
    if getattr(retea, "memorie", None) is not None:
        raise ValueError("rețeaua folosește memoria ierarhică (portul „memorie”); unealta n-o știe")
    trecut = 0 if not memorie else memorie[0][0].size(2)
    t = idx.size(1)
    if trecut + t > retea.context:
        raise ValueError(f"textul ({trecut + t} simboluri) trece de contextul rețelei ({retea.context})")
    poz = torch.arange(trecut, trecut + t, device=idx.device)
    x = retea.emb_token(idx) + retea.emb_pozitie(poz)
    noua: Memorie = []
    for k, strat in enumerate(retea.straturi):
        a, kv = _atentie_cu_memorie(strat, strat.ln1(x), memorie[k] if memorie else None)
        x = x + a
        x = x + strat.mlp(strat.ln2(x))
        noua.append(kv)
    return retea.cap(retea.ln(x)), noua


@torch.no_grad()
def greedy_cu_memorie(retea: Any, intrare: list[int], n: int, dispozitiv: str,
                      logit_uri: list[torch.Tensor] | None = None) -> list[int]:
    """n simboluri noi, argmax; întâi tot textul o dată, apoi câte un simbol, cu K, V păstrate."""
    noi: list[int] = []
    memorie: Memorie | None = None
    urmatorul = torch.tensor([intrare], dtype=torch.long, device=dispozitiv)
    for _ in range(n):
        logits, memorie = pas_inainte(retea, urmatorul, memorie)
        ultim = logits[0, -1].float()
        if logit_uri is not None:
            logit_uri.append(ultim.cpu())
        s = int(ultim.argmax().item())
        noi.append(s)
        urmatorul = torch.tensor([[s]], dtype=torch.long, device=dispozitiv)
    return noi


@torch.no_grad()
def greedy_fara_memorie(retea: Any, intrare: list[int], n: int, dispozitiv: str,
                        logit_uri: list[torch.Tensor] | None = None) -> list[int]:
    """Ca `viteza_inferenta.greedy` (S130): la fiecare simbol tot textul (ultimele `context`) prin rețea."""
    noi: list[int] = []
    for _ in range(n):
        toate = intrare + noi
        idx = torch.tensor([toate[-retea.context:]], dtype=torch.long, device=dispozitiv)
        ultim = retea(idx)[0, -1].float()
        if logit_uri is not None:
            logit_uri.append(ultim.cpu())
        noi.append(int(ultim.argmax().item()))
    return noi


def compara_logit_uri(retea: Any, intrare: list[int], n: int, dispozitiv: str) -> dict[str, Any]:
    """Cu memorie și fără: simbolurile și diferența maximă a logit-urilor la fiecare poziție."""
    cu: list[torch.Tensor] = []
    fara: list[torch.Tensor] = []
    s_cu = greedy_cu_memorie(retea, intrare, n, dispozitiv, cu)
    s_fara = greedy_fara_memorie(retea, intrare, n, dispozitiv, fara)
    dif = [float((a - b).abs().max()) for a, b in zip(cu, fara)]
    return {"simboluri_cu": s_cu, "simboluri_fara": s_fara, "identice": s_cu == s_fara,
            "dif_max_pe_pozitie": dif, "dif_max": max(dif) if dif else 0.0}


def masoara(retea: Any, intrare: list[int], n: int, dispozitiv: str, cache: bool, repetari: int = 5,
            incalzire: int = 1) -> dict[str, Any]:
    retea.eval()
    gen = greedy_cu_memorie if cache else greedy_fara_memorie
    for _ in range(incalzire):
        gen(retea, intrare, n, dispozitiv)
    _sincron(dispozitiv)
    timpi: list[float] = []
    simboluri: list[int] = []
    for _ in range(repetari):
        _sincron(dispozitiv)
        t0 = time.perf_counter()
        simboluri = gen(retea, intrare, n, dispozitiv)
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


def pregateste(retea: Any, dispozitiv: str, precizie: str) -> Any:
    """O copie a rețelei pe dispozitiv, în precizia cerută (nimic salvat)."""
    return copy.deepcopy(retea).to(dispozitiv).to(PRECIZII[precizie]).eval()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--experiment", type=int, default=513)
    p.add_argument("--dispozitiv", choices=("cpu", "cuda"), default="cpu")
    p.add_argument("--precizie", choices=tuple(PRECIZII), default="f32")
    p.add_argument("--cache", choices=("da", "nu"), default="da")
    p.add_argument("--simboluri", type=int, default=16)
    p.add_argument("--text", default="Buna ziua")
    p.add_argument("--repetari", type=int, default=5)
    p.add_argument("--asteptat", default=",".join(map(str, ASTEPTAT_513)),
                   help="simbolurile așteptate, despărțite prin virgulă (implicit cele 16 ale lui #513; gol = fără)")
    p.add_argument("--compara-logit-uri", action="store_true",
                   help="în plus: cu memorie față de fără, diferența maximă a logit-urilor (necronometrat)")
    p.add_argument("--kgr", default="", help="un fișier .kgr doar citit: SHA-256 înainte și după")
    p.add_argument("--iesire", required=True, help="dosarul; se scrie <dosar>/rezultat.json")
    a = p.parse_args(argv)
    iesire = Path(a.iesire) / "rezultat.json"
    if iesire.exists():
        raise SystemExit(f"{iesire} există deja: nu scriu peste el")
    if a.dispozitiv == "cuda" and not torch.cuda.is_available():
        raise SystemExit("PyTorch nu vede placa (CUDA)")
    from kronos.cai import gaseste_model
    from kronos.jurnal import Jurnal
    from unelte.modele_salvate import fisa_modelului, incarca_modelul

    fisa = fisa_modelului(Jurnal(RADACINA / "lucru"), a.experiment)
    cale_model = Path(gaseste_model(fisa["model_salvat"]))
    if not cale_model.exists():
        cale_model = cale_model.with_suffix(".pt")
    fisiere = [cale_model] + ([Path(a.kgr)] if a.kgr else [])
    sha_inainte = {f.as_posix(): sha256(f) for f in fisiere}
    model = incarca_modelul(fisa, "cpu")  # ca la S130; apoi copia pe dispozitiv
    intrare = list(model.tok.codifica(a.text))
    asteptat = [int(x) for x in a.asteptat.split(",") if x.strip()] or None
    t0 = time.time()
    retea = pregateste(model.retea.float().to("cpu"), a.dispozitiv, a.precizie)
    if a.dispozitiv == "cuda":
        torch.cuda.reset_peak_memory_stats()
    r = masoara(retea, intrare, a.simboluri, a.dispozitiv, a.cache == "da", a.repetari)
    if a.dispozitiv == "cuda":
        r["memorie_max_mb"] = round(torch.cuda.max_memory_allocated() / 2**20, 1)
    else:
        r["fire_torch"] = torch.get_num_threads()
    asteptat_cmp = asteptat[: a.simboluri] if asteptat else None
    rezultat: dict[str, Any] = {
        "text": a.text, "intrare": intrare, "simboluri_noi": a.simboluri, "repetari": a.repetari, "incalzire": 1,
        "dispozitiv": a.dispozitiv, "precizie": a.precizie, "cache": a.cache == "da", **r,
        **compara(r["simboluri"][: len(asteptat_cmp)] if asteptat_cmp else r["simboluri"], asteptat_cmp),
        "text_generat": model.tok.decodeaza(r["simboluri"]),
    }
    if a.compara_logit_uri:
        rezultat["logit_uri"] = compara_logit_uri(retea, intrare, a.simboluri, a.dispozitiv)
    del retea
    sha_dupa = {f.as_posix(): sha256(f) for f in fisiere}
    rezultat.update({
        "experiment": fisa["id"], "linie": fisa.get("linie", ""), "clasa": fisa["module"]["model"]["cale"],
        "model_salvat": cale_model.as_posix(), "asteptat": asteptat_cmp, "versiuni": versiuni(),
        "sha256_inainte": sha_inainte, "sha256_dupa": sha_dupa, "sha_neschimbate": sha_inainte == sha_dupa,
        "secunde_total": round(time.time() - t0, 1), "comanda": " ".join(sys.argv),
    })
    iesire.parent.mkdir(parents=True, exist_ok=True)
    iesire.write_text(json.dumps(rezultat, ensure_ascii=False, indent=1), encoding="utf-8")
    sumar = {c: rezultat.get(c) for c in ("simb_pe_s", "ms_pe_simbol", "identice", "memorie_max_mb", "sha_neschimbate")}
    if "logit_uri" in rezultat:
        sumar["dif_max_logit_uri"] = rezultat["logit_uri"]["dif_max"]
    print(json.dumps({"iesire": iesire.as_posix(), **sumar}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
