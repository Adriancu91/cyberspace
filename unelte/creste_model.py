"""S77a (C-64 R2, 5 nov 2026): Kronos crescut în adâncime din #477, cu straturi noi „neutre”.

Un strat nou e copia stratului vechi de dedesubt (ln1, atentie.in_proj, ln2, mlp[0]), dar cu atentie.out_proj și mlp[2]
(greutăți și bias) puse pe zero: atenția și MLP-ul lui adună exact 0 la fluxul rezidual, deci rețeaua crescută dă aceeași
ieșire ca cea veche (arhitectura e pre-LN, cu `ln` final). Straturile noi se împrăștie uniform printre cele vechi.

    python unelte/creste_model.py creste --din lucru/w2_reteta_A_cont3/gpt.pt --straturi 24 --iesire lucru/w2_mare/gpt_24.pt
    python unelte/creste_model.py taie --din lucru/w2_mare/gpt_24.pt --straturi 6 --iesire lucru/avans/mic6/gpt.pt  # S92
    python unelte/creste_model.py identic --straturi 24 30 --json lucru/w2_mare/identic.json     # procesor, fp32
    python unelte/creste_model.py masoara --straturi 12 24 30 36 42 --json lucru/w2_mare/masoara.json   # placa
    python unelte/creste_model.py romana --gpt lucru/w2_mare/gpt_24.pt --json ...   # română curat pe un fișier
    python unelte/creste_model.py kgr --vechi a_f32.kgr --nou b_f32.kgr --json ...  # greedy + logit-uri, fără PyTorch

Fișierul ieșit are forma lui cale_stare (ca starea de pornire a lui antrenare_lunga.py --porneste-din): setari, retea, un
AdamW gol (starea optimizatorului NU se copiază), pasi_total = 0 și minute = 0 (încălzirea ratei pornește din nou), scor.
Se încarcă de module.model_muon:ModelGPTConversatieMuon cu n_straturi = N și restul setărilor ca la S51, fără nicio
schimbare în module/. Unealta nu scrie peste un fișier existent.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

SURSA = "lucru/w2_reteta_A_cont3/gpt.pt"  # = #477 (aceleași greutăți, verificat 5 nov)
CONFIG_S51 = "config/conv_w2_reteta_A_cont3.toml"
TOKENIZER = "date/ws/bpe_16384.json"
VALIDARE_ROMANA = "date/ws/curat/wikipedia_ro/validare_curata.txt"
AMESTEC = "date/ws/amestec/antrenare.txt"
NULE = ("atentie.out_proj.weight", "atentie.out_proj.bias", "mlp.2.weight", "mlp.2.bias")
MEMORIE_MAX_MB = 7000
TEMPERATURA_MAX = 83


def sha256(cale: str | Path) -> str:
    h = hashlib.sha256()
    with Path(cale).open("rb") as f:
        for bucata in iter(lambda: f.read(1 << 20), b""):
            h.update(bucata)
    return h.hexdigest()


# ---- creșterea ------------------------------------------------------------------------------------------------------

def planul(vechi: int, nou: int) -> list[tuple[int, bool]]:
    """Pentru fiecare strat al rețelei crescute: (stratul vechi copiat, e nou?). Cele nou − vechi straturi noi se
    împart uniform: după stratul vechi j vin ⌊(j+1)k/v⌋ − ⌊jk/v⌋ straturi noi (la 12 → 24: câte unul după fiecare)."""
    if nou < vechi or vechi < 1:
        raise ValueError(f"cresc doar: {vechi} → {nou}")
    k = nou - vechi
    plan: list[tuple[int, bool]] = []
    for j in range(vechi):
        plan.append((j, False))
        plan += [(j, True)] * ((j + 1) * k // vechi - j * k // vechi)
    return plan


def creste_stare(stare: dict[str, Any], vechi: int, nou: int) -> dict[str, Any]:
    """state_dict-ul rețelei _GPT crescut de la `vechi` la `nou` straturi (tensori noi, sursa neatinsă)."""
    rezultat: dict[str, Any] = {k: v.clone() for k, v in stare.items() if not k.startswith("straturi.")}
    for i, (j, e_nou) in enumerate(planul(vechi, nou)):
        prefix = f"straturi.{j}."
        for cheie, t in stare.items():
            if cheie.startswith(prefix):
                rest = cheie[len(prefix):]
                rezultat[f"straturi.{i}.{rest}"] = t.clone().zero_() if e_nou and rest in NULE else t.clone()
    return rezultat


def citeste_sursa(cale: str | Path) -> tuple[dict[str, Any], dict[str, Any], float | None]:
    """(setari, state_dict, scor) din cale_stare (gpt.pt) sau dintr-un model salvat de Kronos (experiment_<id>.pt)."""
    import torch

    s = torch.load(cale, map_location="cpu", weights_only=True)
    return s["setari"], s["retea"] if "retea" in s else s["stare"], s.get("scor")


def stare_crescuta(din: str | Path, straturi: int) -> dict[str, Any]:
    import torch

    from module.model_gpt import _GPT

    setari, stare, scor = citeste_sursa(din)
    noi = {**setari, "n_straturi": straturi}
    retea = _GPT(stare["emb_token.weight"].shape[0], **noi)
    retea.load_state_dict(creste_stare(stare, setari["n_straturi"], straturi))
    optimizator = torch.optim.AdamW(retea.parameters(), lr=5e-5, weight_decay=0.1)  # gol: nu se copiază
    return {"setari": noi, "retea": retea.state_dict(), "optimizator": optimizator.state_dict(), "pasi_total": 0,
            "minute": 0.0, "scor": scor}


def creste(din: str, straturi: int, iesire: str) -> dict[str, Any]:
    import torch

    cale = Path(iesire)
    if cale.exists():
        raise FileExistsError(f"{cale} există deja: nu scriu peste el")
    inainte = sha256(din)
    stare = stare_crescuta(din, straturi)
    cale.parent.mkdir(parents=True, exist_ok=True)
    torch.save(stare, cale)
    info = {"din": din, "sha256_din": inainte, "sha256_din_dupa": sha256(din), "straturi": straturi,
            "plan": planul(stare_vechi_straturi(din), straturi), "iesire": str(cale), "sha256": sha256(cale),
            "parametri": sum(t.numel() for k, t in stare["retea"].items() if k != "cap.weight"),
            "pasi_total": 0, "minute": 0.0}
    cale.with_suffix(".json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    return info


def stare_vechi_straturi(din: str | Path) -> int:
    return int(citeste_sursa(din)[0]["n_straturi"])


# ---- tăierea (S92): modelul mic „trimis în avans”, din aceleași greutăți ------------------------------------------

def straturi_neutre(stare: dict[str, Any], n: int) -> list[int]:
    """Straturile care adună exact 0 la fluxul rezidual (atentie.out_proj și mlp[2] pe zero: cele puse de `creste`)."""
    return [i for i in range(n) if all(not stare[f"straturi.{i}.{rest}"].any() for rest in NULE)]


def alege_blocuri(stare: dict[str, Any], n: int, k: int) -> tuple[list[int], list[int], str]:
    """Ce `k` blocuri din `n` se păstrează: (alese, neutre, motivul). Straturile neutre nu fac nimic, deci se aleg
    întâi dintre cele care lucrează; dintre ele, k împrăștiate uniform, cu primul și ultimul păstrate."""
    if not 1 <= k < n:
        raise ValueError(f"tai doar la mai puține straturi: {n} → {k}")
    neutre = straturi_neutre(stare, n)
    active = [i for i in range(n) if i not in neutre]
    if len(active) >= k:
        baza, motiv = active, (f"{len(neutre)} din {n} straturi sunt neutre (adună 0): aleg {k} din cele "
                                f"{len(active)} care lucrează")
    else:
        baza, motiv = list(range(n)), f"doar {len(active)} straturi lucrează (< {k}): aleg din toate {n}"
    if k == 1:
        alese = [baza[-1]]
    else:
        alese = [baza[int(math.floor(i * (len(baza) - 1) / (k - 1) + 0.5))] for i in range(k)]
    return alese, neutre, motiv + ", împrăștiate uniform, cu primul și ultimul păstrate"


def taie_stare(stare: dict[str, Any], alese: list[int]) -> dict[str, Any]:
    """state_dict-ul cu doar blocurile `alese` (în ordine, renumerotate 0..k−1); încorporările, `ln` final și capul
    copiate. Tensori noi, sursa neatinsă."""
    rezultat: dict[str, Any] = {k: v.clone() for k, v in stare.items() if not k.startswith("straturi.")}
    for i, j in enumerate(alese):
        prefix = f"straturi.{j}."
        for cheie, t in stare.items():
            if cheie.startswith(prefix):
                rezultat[f"straturi.{i}.{cheie[len(prefix):]}"] = t.clone()
    return rezultat


def taie(din: str, straturi: int, iesire: str) -> dict[str, Any]:
    import torch

    from module.model_gpt import _GPT

    cale = Path(iesire)
    if cale.exists():
        raise FileExistsError(f"{cale} există deja: nu scriu peste el")
    inainte = sha256(din)
    setari, stare, _ = citeste_sursa(din)
    n = int(setari["n_straturi"])
    alese, neutre, motiv = alege_blocuri(stare, n, straturi)
    noi = {**setari, "n_straturi": straturi}
    retea = _GPT(stare["emb_token.weight"].shape[0], **noi)
    retea.load_state_dict(taie_stare(stare, alese))
    optimizator = torch.optim.AdamW(retea.parameters(), lr=5e-5, weight_decay=0.1)  # gol: nu se copiază
    cale.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"setari": noi, "retea": retea.state_dict(), "optimizator": optimizator.state_dict(), "pasi_total": 0,
                "minute": 0.0, "scor": None}, cale)
    info = {"din": din, "sha256_din": inainte, "sha256_din_dupa": sha256(din), "straturi_din": n,
            "straturi": straturi, "blocuri_pastrate": alese, "straturi_neutre_in_sursa": neutre, "motiv": motiv,
            "iesire": str(cale), "sha256": sha256(cale),
            "parametri": sum(t.numel() for k, t in retea.state_dict().items() if k != "cap.weight"),
            "pasi_total": 0, "minute": 0.0}
    cale.with_suffix(".json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    return info


# ---- aceeași ieșire (procesor, fp32) ---------------------------------------------------------------------------------

def paragrafe(cale: str | Path = VALIDARE_ROMANA, cate: int = 20) -> list[str]:
    """Primele `cate` paragrafe nevide (despărțite de un rând gol) din validare, fără separatorul de texte."""
    rezultat: list[str] = []
    with Path(cale).open(encoding="utf-8") as f:
        bucata = f.read(400_000)
    for p in bucata.replace("<|endoftext|>", "\n\n").split("\n\n"):
        if p.strip():
            rezultat.append(p.strip())
        if len(rezultat) == cate:
            break
    return rezultat


def retea_din(setari: dict[str, Any], stare: dict[str, Any]) -> Any:
    from module.model_gpt import _GPT

    retea = _GPT(stare["emb_token.weight"].shape[0], **setari)
    retea.load_state_dict(stare)
    return retea.eval()


def compara_retele(vechea: Any, noua: Any, siruri: list[list[int]]) -> dict[str, Any]:
    import torch

    dif, egale, total = 0.0, 0, 0
    for s in siruri:
        x = torch.tensor([s])
        with torch.no_grad():
            a, b = vechea(x)[0], noua(x)[0]
        dif = max(dif, float((a - b).abs().max()))
        egale += int((a.argmax(-1) == b.argmax(-1)).sum())
        total += len(s)
    return {"dif_max_logit": dif, "argmax_identic": egale / total, "pozitii": total, "siruri": len(siruri)}


def identic(straturi: list[int], din: str = SURSA, fire: int = 12) -> dict[str, Any]:
    import torch

    from module.tokenizer_bpe import TokenizerBPE
    from unelte.vectori_kgr1 import TEXTE

    torch.set_num_threads(fire)
    setari, stare, _ = citeste_sursa(din)
    tok = TokenizerBPE.incarca(RADACINA / TOKENIZER)
    ctx = setari["context"]
    seturi = {"kgr1": [tok.codifica(t) for t in TEXTE],
              "romana_wikipedia_curat_20": [tok.codifica(p)[:ctx] for p in paragrafe()]}
    vechea = retea_din(setari, stare)
    rezultat: dict[str, Any] = {"din": din, "sha256_din": sha256(din), "pe": {}}
    for n in straturi:
        noua = retea_din({**setari, "n_straturi": n}, creste_stare(stare, setari["n_straturi"], n))
        rezultat["pe"][str(n)] = {nume: compara_retele(vechea, noua, s) for nume, s in seturi.items()}
        del noua
    rezultat["sha256_din_dupa"] = sha256(din)
    return rezultat


# ---- română curat pe un fișier (echivalentul examen_validari_ws.py) -------------------------------------------------

def model_nou(straturi: int, dispozitiv: str, retea: dict[str, Any] | None = None) -> Any:
    """Modelul S51 (ModelGPTConversatieMuon, setările din config) cu `straturi` straturi, rețeaua construită. `retea`
    (n_capete, n_emb, context din fișier) înlocuiește mărimile din config (pentru modelele mici din teste)."""
    import tomllib

    from module.model_muon import ModelGPTConversatieMuon
    from module.tokenizer_bpe import TokenizerBPE

    config = tomllib.loads((RADACINA / CONFIG_S51).read_text(encoding="utf-8"))
    marimi = {k: v for k, v in (retea or {}).items() if k in ("n_capete", "n_emb", "context")}
    m = ModelGPTConversatieMuon(**{**config["porturi"]["model"]["setari"], **marimi, "n_straturi": straturi,
                                   "cale_stare": "", "dispozitiv": dispozitiv})
    m.tok = TokenizerBPE.incarca(RADACINA / TOKENIZER)
    m._construieste()
    return m


def model_din_gpt(gpt: str | Path, dispozitiv: str) -> Any:
    """Modelul S51 cu n_straturi și greutățile din fișier."""
    setari_fisier, stare, _ = citeste_sursa(gpt)
    m = model_nou(int(setari_fisier["n_straturi"]), dispozitiv, setari_fisier)
    m.retea.load_state_dict(stare)
    m.retea.eval()
    return m


def romana(gpt: str, dispozitiv: str = "cpu", fire: int = 12, caractere: int = 100_000) -> dict[str, Any]:
    import torch

    from unelte.examen_validari_ws import GRUPE, VALIDARI, examineaza, numere

    if dispozitiv == "cpu":
        torch.set_num_threads(fire)
    m = model_din_gpt(gpt, dispozitiv)
    validari = {k: VALIDARI[k] for k in GRUPE["romana_curat"]}
    r = examineaza(m, caractere, validari)
    return {"gpt": gpt, "sha256": sha256(gpt), "dispozitiv": dispozitiv, "caractere": caractere, **numere(r),
            "rezultate": r}


# ---- memorie și viteză pe placă -------------------------------------------------------------------------------------

def nvidia_smi() -> tuple[int, int] | None:
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=memory.used,temperature.gpu", "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=30)
        m, t = (int(x) for x in r.stdout.strip().split(","))
        return m, t
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None


def masoara_unul(straturi: int, recalcul: bool, pasi: int = 60, ultimii: int = 40, din: str = SURSA,
                 megaocteti_text: int = 4) -> dict[str, Any]:
    """În procesul acesta: modelul crescut pe placă, pasul adevărat al clasei (AdamW, bf16 prin _autocast, lot 12,
    context 512, adunare_loturi 8 ca la S51), `pasi` loturi; viteza pe ultimele `ultimii`. Nimic nu se salvează."""
    import torch
    from torch.utils.checkpoint import checkpoint

    # Placa: cel mult ~6.600 MB pentru tensori (restul e al Windows/CUDA): o măsurare prea mare cade cu „out of memory”
    total_mb = torch.cuda.get_device_properties(0).total_memory / 2**20
    torch.cuda.set_per_process_memory_fraction(min(1.0, (MEMORIE_MAX_MB - 400) / total_mb))
    setari, stare, _ = citeste_sursa(din)
    m = model_nou(straturi, "cuda")
    m.retea.load_state_dict(creste_stare(stare, setari["n_straturi"], straturi))
    del stare
    if recalcul:  # din afară: fiecare strat își recalculează activările la întoarcere (module/ neschimbat)
        for strat in m.retea.straturi:
            inainte = strat.forward
            strat.forward = lambda x, f=inainte: checkpoint(f, x, use_reentrant=False)
    with (RADACINA / AMESTEC).open(encoding="utf-8", errors="replace") as f:
        text = f.read(megaocteti_text * 1_000_000)
    date_t = torch.tensor(m.tok.codifica(text), dtype=torch.long)
    m.optimizator = m._optimizator_nou()
    m.retea.train()
    ctx, lot = m.setari["context"], m.lot
    g = torch.Generator().manual_seed(0)
    torch.cuda.reset_peak_memory_stats()
    timpi: list[float] = []
    pierderi: list[float] = []
    for _ in range(pasi):
        poz = torch.randint(len(date_t) - ctx - 1, (lot,), generator=g)
        x = torch.stack([date_t[p: p + ctx] for p in poz]).to("cuda")
        y = torch.stack([date_t[p + 1: p + ctx + 1] for p in poz]).to("cuda")
        t0 = time.perf_counter()
        pierderi.append(m._pas(x, y, None))  # .item() în _pas așteaptă placa
        timpi.append(time.perf_counter() - t0)
    secunde = sum(timpi[-ultimii:])
    return {"straturi": straturi, "recalcul": recalcul, "parametri": sum(p.numel() for p in m.retea.parameters()),
            "pasi": pasi, "pasi_pe_secunda": ultimii / secunde, "secunde_ultimii": secunde,
            "torch_max_rezervat_mb": round(torch.cuda.max_memory_reserved() / 2**20),
            "torch_max_alocat_mb": round(torch.cuda.max_memory_allocated() / 2**20),
            "pierdere_prima": pierderi[0], "pierdere_ultima": pierderi[-1], "adunare_loturi": m.adunare_loturi,
            "pasi_optimizator": m.pasi_optimizator, "simboluri_text": len(date_t)}


def masoara_in_proces_nou(straturi: int, recalcul: bool, dosar: Path, pas_urmarire: float = 0.5) -> dict[str, Any]:
    """Pornește masoara-unul într-un proces nou și urmărește nvidia-smi; peste 7.000 MB sau 83 °C îl oprește."""
    iesire = dosar / f"masoara_{straturi}{'_recalcul' if recalcul else ''}.json"
    if iesire.exists():
        iesire.unlink()  # măsurătoarea unui proces anterior întrerupt: se refac doar cifrele, nimic păstrat
    comanda = [sys.executable, "-X", "utf8", str(Path(__file__).resolve()), "masoara-unul", "--straturi", str(straturi),
               "--json", str(iesire)] + (["--recalcul"] if recalcul else [])
    p = subprocess.Popen(comanda, cwd=RADACINA)
    varf = {"mb": 0, "c": 0, "oprit": ""}

    def urmareste() -> None:
        while p.poll() is None:
            citire = nvidia_smi()
            if citire:
                varf["mb"], varf["c"] = max(varf["mb"], citire[0]), max(varf["c"], citire[1])
                if citire[0] > MEMORIE_MAX_MB or citire[1] >= TEMPERATURA_MAX:
                    varf["oprit"] = f"{citire[0]} MB, {citire[1]} °C"
                    p.kill()
            time.sleep(pas_urmarire)

    fir = threading.Thread(target=urmareste, daemon=True)
    inceput = time.perf_counter()
    fir.start()
    cod = p.wait()
    fir.join()
    rezultat: dict[str, Any] = {"straturi": straturi, "recalcul": recalcul, "cod": cod,
                                "secunde_proces": round(time.perf_counter() - inceput, 1),
                                "nvidia_smi_varf_mb": varf["mb"], "temperatura_max": varf["c"]}
    if varf["oprit"]:
        rezultat["oprit_de_paza"] = varf["oprit"]
    if cod == 0 and iesire.exists():
        rezultat.update(json.loads(iesire.read_text(encoding="utf-8")))
    return rezultat


def masoara(straturi: list[int], dosar: Path, prag_recalcul: int = 6500) -> list[dict[str, Any]]:
    rezultate = []
    for n in straturi:
        r = masoara_in_proces_nou(n, False, dosar)
        rezultate.append(r)
        print(json.dumps(r, ensure_ascii=False), flush=True)
        if r["nvidia_smi_varf_mb"] > prag_recalcul or r["cod"] != 0:
            r2 = masoara_in_proces_nou(n, True, dosar)
            rezultate.append(r2)
            print(json.dumps(r2, ensure_ascii=False), flush=True)
        time.sleep(20)  # placa se răcește puțin între măsurători
    return rezultate


def alege(rezultate: list[dict[str, Any]], prag_mb: int = 6500, prag_viteza: float = 2.0) -> dict[str, Any] | None:
    """Regula S77a pasul 4: cel mai mare N din {24, 30, 36, 42} cu vârful nvidia-smi ≤ 6.500 MB și ≥ 2,0 pași/s;
    dacă încape fără recalcul, fără."""
    bune = [r for r in rezultate if r["straturi"] in (24, 30, 36, 42) and r.get("cod") == 0
            and "pasi_pe_secunda" in r and r["nvidia_smi_varf_mb"] <= prag_mb and r["pasi_pe_secunda"] >= prag_viteza]
    if not bune:
        return None
    return max(bune, key=lambda r: (r["straturi"], not r["recalcul"]))


# ---- KGR1: greedy și logit-uri pe exporturi, fără PyTorch -----------------------------------------------------------

def compara_kgr(vechi: str, nou: str) -> dict[str, Any]:
    import numpy as np

    from unelte.inferenta_bruta import MotorBrut
    from unelte.vectori_kgr1 import TEXTE, vectori_text

    a, b = MotorBrut(vechi), MotorBrut(nou)
    texte = []
    for t in TEXTE:
        va, vb = vectori_text(a, t), vectori_text(b, t)
        texte.append({"text": t, "greedy_vechi": va["greedy_5"], "greedy_nou": vb["greedy_5"],
                      "greedy_identic": va["greedy_5"] == vb["greedy_5"],
                      "dif_max_logit_ultima": float(np.abs(np.asarray(va["logits_ultima_pozitie"])
                                                           - np.asarray(vb["logits_ultima_pozitie"])).max())})
    return {"vechi": vechi, "nou": nou, "sha256_vechi": sha256(vechi), "sha256_nou": sha256(nou),
            "straturi_vechi": a.chei["n_straturi"], "straturi_nou": b.chei["n_straturi"], "texte": texte,
            "greedy_identic_toate": all(x["greedy_identic"] for x in texte),
            "dif_max_logit_ultima": max(x["dif_max_logit_ultima"] for x in texte)}


def _scrie(cale: str, obiect: Any) -> None:
    if cale:
        Path(cale).parent.mkdir(parents=True, exist_ok=True)
        Path(cale).write_bytes(json.dumps(obiect, ensure_ascii=False, indent=1).encode("utf-8"))


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="ce", required=True)
    c = sub.add_parser("creste")
    c.add_argument("--din", default=SURSA)
    c.add_argument("--straturi", type=int, required=True)
    c.add_argument("--iesire", required=True)
    t = sub.add_parser("taie")
    t.add_argument("--din", required=True)
    t.add_argument("--straturi", type=int, required=True)
    t.add_argument("--iesire", required=True)
    i = sub.add_parser("identic")
    i.add_argument("--din", default=SURSA)
    i.add_argument("--straturi", type=int, nargs="+", required=True)
    i.add_argument("--fire", type=int, default=12)
    i.add_argument("--json", default="")
    r = sub.add_parser("romana")
    r.add_argument("--gpt", required=True)
    r.add_argument("--dispozitiv", default="cpu")
    r.add_argument("--fire", type=int, default=12)
    r.add_argument("--json", default="")
    m = sub.add_parser("masoara")
    m.add_argument("--straturi", type=int, nargs="+", required=True)
    m.add_argument("--json", required=True)
    u = sub.add_parser("masoara-unul")
    u.add_argument("--straturi", type=int, required=True)
    u.add_argument("--recalcul", action="store_true")
    u.add_argument("--json", required=True)
    k = sub.add_parser("kgr")
    k.add_argument("--vechi", required=True)
    k.add_argument("--nou", required=True)
    k.add_argument("--json", default="")
    a = p.parse_args(argv)
    if a.ce == "creste":
        rez: Any = creste(a.din, a.straturi, a.iesire)
    elif a.ce == "taie":
        try:
            rez = taie(a.din, a.straturi, a.iesire)
        except (FileExistsError, ValueError) as e:
            print(f"REFUZ: {e}", file=sys.stderr)
            return 2
    elif a.ce == "identic":
        rez = identic(a.straturi, a.din, a.fire)
    elif a.ce == "romana":
        rez = romana(a.gpt, a.dispozitiv, a.fire)
        rez = {k: v for k, v in rez.items()}
    elif a.ce == "masoara":
        if Path(a.json).exists():
            print(f"{a.json} există deja: măsurarea s-a făcut.")
            return 1
        rezultate = masoara(a.straturi, Path(a.json).parent)
        rez = {"rezultate": rezultate, "ales": alege(rezultate)}
    elif a.ce == "masoara-unul":
        rez = masoara_unul(a.straturi, a.recalcul)
    else:
        rez = compara_kgr(a.vechi, a.nou)
    _scrie(getattr(a, "json", ""), rez)
    if a.ce != "masoara-unul":
        print(json.dumps(rez if a.ce != "romana" else {k: v for k, v in rez.items() if k != "rezultate"},
                         ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
