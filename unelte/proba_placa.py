"""Proba pe placă a legării datelor pe bucăți (S104, C-110): modelul adevărat al unei configurări, pornit din starea ei
(`cale_stare`), antrenat un număr fix de pași de optimizare — de două ori cu datele vechi (V1, V2: cât diferă placa de la
o rulare la alta) și o dată cu `module.date_bucati:DateBucati` (B). Dacă legarea e bună, loturile sunt aceleași, iar
pierderile diferă cel mult cât diferă placa de la sine.

Nu e un experiment Kronos: nimic în jurnal, niciun examen, nicio stare salvată (unealta nu cheamă `dupa_examen`; starea de
pornire e doar citită, SHA înainte = după). Bucla de antrenare e cea din module/ (`antreneaza`), neschimbată; ca la
antrenările liniei de 24, straturile sunt împachetate cu recalculul activărilor (unelte/antrenare_recalcul.py).

Comenzi:
  tot  --iesire <dosar> [--config-vechi config/proba_placa_vechi.toml] [--config-bucati config/proba_placa_bucati.toml]
       [--pasi-optimizare 300] [--paza-mb 6700] [--temperatura-max 83] [--placa-goala-max 800] [--disc-minim-gb 10]
       Rulează V1, V2 (datele vechi) și B (bucăți), fiecare într-un proces nou, cu paza plăcii: nvidia-smi la 5 secunde
       (<dosar>/smi.jsonl); peste --paza-mb sau la --temperatura-max grade oprește rularea și iese cu cod 3. Scrie
       <dosar>/V1.json, V2.json, B.json și <dosar>/s104.json (cu „verdict”). Refuză dacă s104.json există.
  _rulare  (folosită de „tot”) o singură rulare, într-un proces.

Verdictul (pragurile sarcinii S104): DA = aceleași loturi V1 = B și max |B − V1| ≤ max(2 × max |V2 − V1|, 1e-5), pe
pierderile pașilor de optimizare (media loturilor adunate într-un pas). Aceeași comparație lot cu lot e scrisă alături,
informativ.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shutil
import statistics
import subprocess
import sys
import time
import tomllib
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parents[1]
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from unelte.date_bucati import ram_varf_mb  # noqa: E402
from unelte.proba_legare import _sha_tensori, _stare_dosar  # noqa: E402

RULARI = ("V1", "V2", "B")
PASI_TABEL = (1, 50, 100, 200, 300)
PRAG_MINIM = 1e-5
BUGET_SECUNDE = 2 * 3600.0  # mult peste o rulare: antrenarea se oprește la pasi_max, nu după timp
COD_PAZA = 3


class PazaPlacii(RuntimeError):
    """Placa a trecut de pragul de memorie sau de temperatură în timpul unei rulări."""


def sha_fisier(cale: str | Path) -> str | None:
    fisier = Path(cale)
    if not cale or not fisier.is_file():
        return None
    h = hashlib.sha256()
    with open(fisier, "rb") as f:
        for bucata in iter(lambda: f.read(1 << 20), b""):
            h.update(bucata)
    return h.hexdigest()


def feluri_de_randuri(model: Any, pas_model: int) -> list[str]:
    """Din ce vine fiecare rând al lotului de la pasul dat al modelului (numărat cu pașii de dinainte), în ordinea în
    care îl lipește bucla din module/model_conversatie.py."""
    lot = model.lot
    f = model.fractie_conversatie * lot
    k_conv = math.floor(f * (pas_model + 1) + 1e-9) - math.floor(f * pas_model + 1e-9)
    k_hrana = model.bucati_din_hrana(pas_model) if model.hrana else 0
    return ["conversatie"] * k_conv + ["hrana"] * k_hrana + ["text"] * (lot - k_conv - k_hrana)


def pe_pasi(pierderi: list[float], adunare: int) -> list[float]:
    """Pierderea fiecărui pas de optimizare: media loturilor adunate în el (cele rămase la sfârșit nu fac un pas)."""
    return [statistics.fmean(pierderi[i:i + adunare]) for i in range(0, len(pierderi) - adunare + 1, adunare)]


def o_rulare(config: Path, pasi_optimizare: int, in_plus: dict[str, Any] | None = None, recalcul: bool = True,
             memorie_max_mb: int = 5800) -> dict[str, Any]:
    """Antrenează modelul configurării `pasi_optimizare` pași de optimizare, cu portul `date` al ei, din starea de
    pornire (`cale_stare`, doar citită); notează fiecare lot și fiecare pierdere."""
    import torch

    from kronos.registru import Registru
    from unelte import antrenare_recalcul

    inceput = time.perf_counter()
    c = tomllib.loads(Path(config).read_text(encoding="utf-8"))
    port = c["porturi"]["model"]
    setari = dict(port["setari"]) | (in_plus or {})
    adunare = int(setari.get("adunare_loturi", 1))
    setari["pasi_max"] = pasi_optimizare * adunare
    cale_stare = setari.get("cale_stare") or ""
    sha_stare_inainte = sha_fisier(cale_stare)
    fractie = None
    if recalcul:
        fractie = antrenare_recalcul.plafon_placa(memorie_max_mb)
        antrenare_recalcul.instaleaza()
    try:
        date = Registru().creeaza("date", c["porturi"]["date"]["modul"], c["porturi"]["date"]["setari"]).instanta
        model = Registru().creeaza("model", port["modul"], setari).instanta
        pierderi: list[float] = []
        loturi: list[str] = []
        feluri = {"conversatie": 0, "hrana": 0, "text": 0}
        repere: dict[str, Any] = {}
        peste_tot = hashlib.sha256()
        pas_mascat = model._pas_mascat

        def cu_nota(x: Any, y: Any) -> float:
            if not pierderi:  # primul lot: datele sunt încărcate și modelul e pe placă
                repere["ram_varf_mb_la_primul_lot"] = ram_varf_mb()
                repere["secunde_pana_la_primul_lot"] = round(time.perf_counter() - inceput, 2)
                repere["pasi_total_la_pornire"] = model._pasi_anteriori()
                repere["continuat"] = model.continuat
            xc, yc = x.detach().cpu().contiguous(), y.detach().cpu().contiguous()
            peste_tot.update(xc.numpy().tobytes())
            peste_tot.update(yc.numpy().tobytes())
            loturi.append(_sha_tensori(xc, yc)[:16])
            for fel in feluri_de_randuri(model, model._pasi_anteriori() + len(pierderi)):
                feluri[fel] += 1
            pierderi.append(pas_mascat(x, y))
            if len(pierderi) % (adunare * 25) == 0:
                print(f"   [{time.strftime('%H:%M:%S')}] pasul de optimizare {len(pierderi) // adunare}: lotul "
                      f"{len(pierderi)}, pierderea {pierderi[-1]:.4f}", flush=True)
            return pierderi[-1]

        model._pas_mascat = cu_nota
        statistici = model.antreneaza(date, BUGET_SECUNDE)
        greutati = _sha_tensori(*[v for _, v in sorted(model.retea.state_dict().items())])
        grupuri = [{"rata": g["lr"] * g.get("multiplicator_lr", 1.0), "muon": bool(g.get("muon", False)),
                    "tensori": len(g["params"])} for g in model.optimizator.param_groups]
        optimizator = type(model.optimizator).__name__
        placa: dict[str, Any] = {"dispozitiv": str(model.dispozitiv), "plafon_fractie": fractie}
        if model.dispozitiv.type == "cuda":
            placa.update(pytorch_rezervat_max_mb=round(torch.cuda.max_memory_reserved() / 2**20),
                         pytorch_folosit_max_mb=round(torch.cuda.max_memory_allocated() / 2**20),
                         nume=torch.cuda.get_device_name(0))
        impachetate = sum(antrenare_recalcul.e_impachetat(s) for s in model.retea.straturi)
    finally:
        if recalcul:
            antrenare_recalcul.dezinstaleaza()
    secunde_bucla = statistici["secunde_bucla"]
    simboluri = len(pierderi) * int(setari.get("lot", 1)) * int(setari.get("context", 1))
    return {
        "config": str(config).replace("\\", "/"), "date_modul": c["porturi"]["date"]["modul"], "model_modul": port["modul"],
        "setari_model": setari, "adunare_loturi": adunare, "loturi_facute": len(pierderi),
        "pasi_optimizare": len(pierderi) // adunare,
        "pierderi": pierderi, "pierderi_hex": [float(p).hex() for p in pierderi],
        "pierderi_pe_pas": pe_pasi(pierderi, adunare), "loturi": loturi, "randuri": feluri,
        "sha256_loturi": peste_tot.hexdigest(), "sha256_greutati": greutati,
        "statistici": statistici, "optimizator": optimizator, "grupuri": grupuri, "straturi_cu_recalcul": impachetate,
        "cale_stare": cale_stare, "sha256_stare_inainte": sha_stare_inainte, "sha256_stare_dupa": sha_fisier(cale_stare),
        "placa": placa, "secunde_bucla": secunde_bucla,
        "loturi_pe_secunda": round(len(pierderi) / secunde_bucla, 3) if secunde_bucla else None,
        "simboluri_pe_secunda": round(simboluri / secunde_bucla, 1) if secunde_bucla else None,
        "secunde_total": round(time.perf_counter() - inceput, 2),
        "ram_varf_mb": ram_varf_mb(), **repere,
    }


def _dif_max(a: list[float], b: list[float]) -> dict[str, Any]:
    """Cea mai mare diferență între două șiruri de pierderi și unde e (numărat de la 1); primul loc diferit."""
    n = min(len(a), len(b))
    dif = [abs(a[i] - b[i]) for i in range(n)]
    unde = max(range(n), key=dif.__getitem__) if n else None
    primul = next((i for i in range(n) if a[i] != b[i]), None)
    return {"comparate": n, "maxima": dif[unde] if n else 0.0, "la": None if unde is None else unde + 1,
            "primul_diferit": None if primul is None else primul + 1, "identice": n > 0 and primul is None}


def compara(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    """Două rulări: aceleași loturi? cât diferă pierderile, pe pașii de optimizare și lot cu lot?"""
    primul_lot = next((i for i, (x, y) in enumerate(zip(a["loturi"], b["loturi"])) if x != y), None)
    aceleasi_pasi = a["loturi_facute"] == b["loturi_facute"]
    return {
        "loturi_facute": [a["loturi_facute"], b["loturi_facute"]],
        "loturi_identice": aceleasi_pasi and primul_lot is None and a["sha256_loturi"] == b["sha256_loturi"],
        "primul_lot_diferit": None if primul_lot is None else primul_lot + 1,
        "primul_pas_de_optimizare_cu_lot_diferit": None if primul_lot is None else primul_lot // a["adunare_loturi"] + 1,
        "pe_pasi": _dif_max(a["pierderi_pe_pas"], b["pierderi_pe_pas"]),
        "pe_loturi": _dif_max(a["pierderi"], b["pierderi"]),
        "greutati_identice": a["sha256_greutati"] == b["sha256_greutati"],
    }


def verdict(v1_b: dict[str, Any], v1_v2: dict[str, Any], cheie: str = "pe_pasi") -> dict[str, Any]:
    """Pragurile sarcinii: DA = loturi identice V1 = B și max |B − V1| ≤ max(2 × max |V2 − V1|, 1e-5)."""
    prag = max(2 * v1_v2[cheie]["maxima"], PRAG_MINIM)
    sub_prag = v1_b[cheie]["maxima"] <= prag
    return {"verdict": "DA" if v1_b["loturi_identice"] and sub_prag else "NU", "prag": prag,
            "zgomotul_placii_max_v2_v1": v1_v2[cheie]["maxima"], "max_b_v1": v1_b[cheie]["maxima"],
            "loturi_identice_v1_b": v1_b["loturi_identice"], "diferenta_sub_prag": sub_prag}


def nvidia_smi() -> tuple[int, int] | None:
    """(memoria folosită în MB, temperatura) după nvidia-smi; None dacă nu se poate citi."""
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=memory.used,temperature.gpu", "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=30)
        m, t = (int(x) for x in r.stdout.strip().splitlines()[0].split(","))
        return m, t
    except (OSError, ValueError, IndexError, subprocess.TimeoutExpired):
        return None


def _in_proces_nou(nume: str, config: Path, pasi_optimizare: int, dosar: Path, paza_mb: int, temperatura_max: int,
                   citeste: Any = nvidia_smi, pauza: float = 5.0) -> tuple[dict[str, Any], dict[str, Any]]:
    """O rulare într-un proces nou, cu paza plăcii. Întoarce rezultatul rulării și vârfurile plăcii (nvidia-smi)."""
    iesire = dosar / f"{nume}.json"
    mediu = os.environ | {"PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True", "PYTHONIOENCODING": "utf-8"}
    proces = subprocess.Popen(
        [sys.executable, "-X", "utf8", str(Path(__file__).resolve()), "_rulare", "--config", str(config),
         "--pasi-optimizare", str(pasi_optimizare), "--iesire", str(iesire)], cwd=RADACINA, env=mediu)
    varf = {"memorie_max_mb": 0, "temperatura_max": 0, "citiri": 0}
    with open(dosar / "smi.jsonl", "a", encoding="utf-8") as smi:
        while proces.poll() is None:
            citire = citeste()
            if citire is not None:
                m, t = citire
                varf.update(memorie_max_mb=max(varf["memorie_max_mb"], m), temperatura_max=max(varf["temperatura_max"], t),
                            citiri=varf["citiri"] + 1)
                smi.write(json.dumps({"rulare": nume, "ora": time.strftime("%H:%M:%S"), "mb": m, "grade": t}) + "\n")
                smi.flush()
                if m > paza_mb or t >= temperatura_max:
                    proces.terminate()
                    proces.wait(timeout=120)
                    raise PazaPlacii(f"rularea {nume}: placa la {m} MB, {t} °C (paza: {paza_mb} MB, {temperatura_max} °C) "
                                     f"la {time.strftime('%H:%M:%S')} — rularea a fost oprită")
            try:
                proces.wait(timeout=pauza)
            except subprocess.TimeoutExpired:
                pass
    if proces.returncode != 0:
        raise RuntimeError(f"rularea {nume} a picat (cod {proces.returncode}); vezi mesajele de mai sus")
    return json.loads(iesire.read_text(encoding="utf-8")), varf


def tot(config_vechi: Path, config_bucati: Path, dosar: Path, pasi_optimizare: int = 300, in_proces: bool = False,
        in_plus: dict[str, Any] | None = None, paza_mb: int = 6700, temperatura_max: int = 83,
        placa_goala_max: int = 800, disc_minim_gb: float = 10.0) -> dict[str, Any]:
    """V1, V2, B și comparațiile. `in_proces` (doar pentru teste): fără procese noi, fără placă, fără pază."""
    rezumat = dosar / "s104.json"
    if rezumat.exists():
        raise FileExistsError(f"{rezumat} există deja: proba se face o singură dată")
    c_vechi = tomllib.loads(Path(config_vechi).read_text(encoding="utf-8"))
    c_bucati = tomllib.loads(Path(config_bucati).read_text(encoding="utf-8"))
    if c_bucati["porturi"]["date"]["modul"] != "module.date_bucati:DateBucati":
        raise ValueError(f"{config_bucati}: portul date nu e module.date_bucati:DateBucati")
    if c_vechi["porturi"]["date"]["modul"] == "module.date_bucati:DateBucati":
        raise ValueError(f"{config_vechi}: portul date trebuie să fie cel vechi (text), nu datele pe bucăți")
    rez: dict[str, Any] = {"config_vechi": str(config_vechi).replace("\\", "/"),
                           "config_bucati": str(config_bucati).replace("\\", "/"), "pasi_optimizare": pasi_optimizare,
                           "inceput": time.strftime("%Y-%m-%dT%H:%M:%S")}
    if not in_proces:
        liber_gb = shutil.disk_usage(RADACINA).free / 2**30
        citire = nvidia_smi()
        rez["inainte"] = {"disc_liber_gb": round(liber_gb, 1), "placa_goala_mb": citire[0] if citire else None,
                          "temperatura": citire[1] if citire else None}
        if liber_gb < disc_minim_gb:
            raise SystemExit(f"discul are doar {liber_gb:.1f} GB liberi (minim {disc_minim_gb:g}); nu pornesc")
        if citire is None or citire[0] >= placa_goala_max:
            raise SystemExit(f"placa nu e goală (nvidia-smi: {citire}; limita {placa_goala_max} MB); nu pornesc")
    dosar.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    paznite = {nume: Path(d) for nume, d in (
        ("cache", c_vechi["porturi"]["model"]["setari"].get("director_cache") or ""),
        ("bucati", c_bucati["porturi"]["date"]["setari"]["director"])) if d}
    inainte = {nume: _stare_dosar(d if d.is_absolute() else RADACINA / d) for nume, d in paznite.items()}
    rulari: dict[str, dict[str, Any]] = {}
    placa: dict[str, Any] = {}
    try:
        for nume in RULARI:
            config = config_bucati if nume == "B" else config_vechi
            print(f"[{time.strftime('%H:%M:%S')}] {nume} ({config}) …", flush=True)
            if in_proces:
                r = o_rulare(config, pasi_optimizare, in_plus, recalcul=True)
                (dosar / f"{nume}.json").write_text(json.dumps(r, indent=1, ensure_ascii=False), encoding="utf-8")
            else:
                r, placa[nume] = _in_proces_nou(nume, config, pasi_optimizare, dosar, paza_mb, temperatura_max)
            rulari[nume] = r
            print(f"[{time.strftime('%H:%M:%S')}] {nume}: {r['pasi_optimizare']} pași de optimizare ({r['loturi_facute']} "
                  f"loturi), ultima pierdere {r['pierderi_pe_pas'][-1]:.6f}, RAM de vârf {r['ram_varf_mb']} MB, "
                  f"{r['simboluri_pe_secunda']} simboluri/s, {r['secunde_total']} s", flush=True)
    except PazaPlacii as e:
        rez.update(verdict="NEMĂSURAT", oprit=str(e), placa=placa, rulari_terminate=sorted(rulari),
                   secunde=round(time.perf_counter() - start, 1))
        rezumat.write_text(json.dumps(rez, indent=1, ensure_ascii=False), encoding="utf-8")
        raise
    dupa = {nume: _stare_dosar(d if d.is_absolute() else RADACINA / d) for nume, d in paznite.items()}
    v1_b, v1_v2, v2_b = (compara(rulari[a], rulari[b]) for a, b in (("V1", "B"), ("V1", "V2"), ("V2", "B")))
    pe_pasi_v, pe_loturi_v = verdict(v1_b, v1_v2, "pe_pasi"), verdict(v1_b, v1_v2, "pe_loturi")
    minim = min(r["pasi_optimizare"] for r in rulari.values())
    de_pastrat = ("date_modul", "model_modul", "adunare_loturi", "loturi_facute", "pasi_optimizare", "randuri",
                  "sha256_loturi", "sha256_greutati", "optimizator", "grupuri", "straturi_cu_recalcul", "cale_stare",
                  "sha256_stare_inainte", "sha256_stare_dupa", "placa", "secunde_bucla", "loturi_pe_secunda",
                  "simboluri_pe_secunda", "secunde_total", "ram_varf_mb", "ram_varf_mb_la_primul_lot",
                  "secunde_pana_la_primul_lot", "pasi_total_la_pornire", "continuat", "statistici")
    rez.update(
        verdict=pe_pasi_v["verdict"], pe_pasi_de_optimizare=pe_pasi_v, pe_loturi_informativ=pe_loturi_v,
        V1_fata_de_B=v1_b, V1_fata_de_V2=v1_v2, V2_fata_de_B=v2_b,
        tabel={str(p): {n: r["pierderi_pe_pas"][p - 1] for n, r in rulari.items()}
               for p in sorted(set(PASI_TABEL + (pasi_optimizare,))) if p <= minim},
        rulari={n: {k: r.get(k) for k in de_pastrat} for n, r in rulari.items()},
        placa_nvidia_smi=placa, doar_citite_neschimbate={nume: inainte[nume] == dupa[nume] for nume in paznite},
        starea_de_pornire_neschimbata=all(r["sha256_stare_inainte"] == r["sha256_stare_dupa"] for r in rulari.values()),
        aceeasi_stare_de_pornire=len({r["sha256_stare_inainte"] for r in rulari.values()}) == 1,
        secunde=round(time.perf_counter() - start, 1), sfarsit=time.strftime("%Y-%m-%dT%H:%M:%S"))
    rezumat.write_text(json.dumps(rez, indent=1, ensure_ascii=False), encoding="utf-8")
    return rez


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="comanda", required=True)
    s = sub.add_parser("tot")
    s.add_argument("--config-vechi", type=Path, default=Path("config/proba_placa_vechi.toml"))
    s.add_argument("--config-bucati", type=Path, default=Path("config/proba_placa_bucati.toml"))
    s.add_argument("--iesire", required=True, type=Path)
    s.add_argument("--pasi-optimizare", type=int, default=300)
    s.add_argument("--paza-mb", type=int, default=6700)
    s.add_argument("--temperatura-max", type=int, default=83)
    s.add_argument("--placa-goala-max", type=int, default=800)
    s.add_argument("--disc-minim-gb", type=float, default=10.0)
    s.add_argument("--in-proces", action="store_true", help="fără procese noi și fără pază (doar pentru teste)")
    s = sub.add_parser("_rulare")
    s.add_argument("--config", required=True, type=Path)
    s.add_argument("--pasi-optimizare", type=int, default=300)
    s.add_argument("--iesire", required=True, type=Path)
    a = p.parse_args(argv)

    if a.comanda == "_rulare":
        r = o_rulare(a.config, a.pasi_optimizare)
        a.iesire.parent.mkdir(parents=True, exist_ok=True)
        a.iesire.write_text(json.dumps(r, indent=1, ensure_ascii=False), encoding="utf-8")
        return 0
    try:
        rez = tot(a.config_vechi, a.config_bucati, a.iesire, a.pasi_optimizare, a.in_proces, None, a.paza_mb,
                  a.temperatura_max, a.placa_goala_max, a.disc_minim_gb)
    except PazaPlacii as e:
        print(f"OPRIT de paza plăcii: {e}", flush=True)
        return COD_PAZA
    scurt = {k: v for k, v in rez.items() if k != "rulari"}
    print(json.dumps(scurt, indent=1, ensure_ascii=False))
    return 0 if rez["verdict"] == "DA" else 1


if __name__ == "__main__":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    sys.exit(main())
