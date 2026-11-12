"""Proba cap-coadă a legării datelor pe bucăți (S103, C-110): un model MIC antrenat pe procesor, aceiași pași, o dată cu
datele vechi (textul întreg → simbolurile din lucru/cache, calea de până acum) și o dată cu `module.date_bucati:DateBucati`
(șirul pe bucăți, prin `sir_antrenare()`). Dacă legarea e bună, loturile și pierderile sunt aceleași, bit cu bit.

Doar procesor (`CUDA_VISIBLE_DEVICES=-1`, `torch.use_deterministic_algorithms(True)`, 1 fir). Nimic nu se scrie în
jurnalul lui Kronos, niciun model nu se salvează; lucru/cache și bucățile sunt doar citite.

Comenzi:
  tot  --iesire <dosar> [--config-vechi config/conv_w2_mare_24r.toml] [--config-bucati config/conv_w2_mare_24_bucati.toml]
       [--pasi 200] [--context 64]
       Rulează, fiecare într-un proces nou: felul „conversatie” (verdictul): A1, A2 (datele vechi, de două ori: procesorul
       dă același rezultat de la o rulare la alta?) și B (bucăți); informativ, felul „muon24” (rețeta liniei 24n: Muon,
       gradient adunat pe 24 de loturi) și felul „simplu” (fără conversație: calea din module/model_gpt.py), câte un A și
       un B. Scrie <dosar>/<fel>_<rulare>.json și <dosar>/s103.json (cu „verdict”). Refuză dacă s103.json există.
  _rulare  (folosită de „tot”) o singură rulare, într-un proces.

Modelul mic (ales la S103): 2 straturi, 2 capete, n_emb 64, context 64, lot 4, de la zero (fără stare), rata fixă 0,001
(fără încălzire și fără scădere: rata după ceas ar face rulările să difere între ele). Din configurare rămân: clasa
modelului, tokenizerul, sămânța, hrana și conversația cu fracțiile lor, director_cache.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
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

FELURI = ("conversatie", "muon24", "simplu")
MIC = {"n_straturi": 2, "n_capete": 2, "n_emb": 64, "lot": 4, "rata_invatare": 0.001, "rata_care_scade": False,
       "incalzire_pasi": 0, "durata_scaderii_secunde": 0, "racire_finala": 0.0, "cale_stare": "",
       "examene_suplimentare": [], "dispozitiv": "cpu"}
DOAR_MUON = ("optimizator", "rata_muon", "scadere_muon", "adunare_loturi", "racire_finala", "fractie_dupa_racire")
PASI_TABEL = (1, 10, 50, 100, 200)


def setarile_modelului(config: dict[str, Any], fel: str, pasi: int, context: int) -> tuple[str, dict[str, Any]]:
    """Clasa și setările modelului mic pentru felul cerut, pornind de la portul model al configurării."""
    port = config["porturi"]["model"]
    setari = dict(port["setari"]) | MIC | {"context": context, "pasi_max": pasi}
    if fel == "conversatie":  # ca linia de 24 (conversație + hrană + text), un pas de optimizator la fiecare lot
        return port["modul"], setari | {"optimizator": "adamw", "adunare_loturi": 1}
    if fel == "muon24":  # rețeta liniei 24n: Muon cu rata 0,0001, gradientul adunat pe 24 de loturi
        return port["modul"], setari | {"optimizator": "muon", "rata_muon": 0.0001, "adunare_loturi": 24}
    if fel == "simplu":  # fără conversație: bucla din module/model_gpt.py (prin model_continuu), cu hrană
        for cheie in DOAR_MUON + ("conversatie", "fractie_conversatie"):
            setari.pop(cheie, None)
        return "module.model_continuu:ModelGPTContinuu", setari
    raise ValueError(f"fel necunoscut: {fel}")


def _sha_tensori(*tensori: Any) -> str:
    h = hashlib.sha256()
    for t in tensori:
        h.update(t.detach().cpu().contiguous().numpy().tobytes())
    return h.hexdigest()


def feluri_de_ferestre(model: Any, fel: str, pas: int) -> list[str]:
    """Din ce vine fiecare rând al lotului de la pasul dat (în ordinea în care îl lipește bucla de antrenare)."""
    lot = model.lot
    k_hrana = model.bucati_din_hrana(pas) if model.hrana else 0
    if fel == "simplu":
        return ["text"] * (lot - k_hrana) + ["hrana"] * k_hrana
    f = model.fractie_conversatie * lot
    k_conv = math.floor(f * (pas + 1) + 1e-9) - math.floor(f * pas + 1e-9)
    return ["conversatie"] * k_conv + ["hrana"] * k_hrana + ["text"] * (lot - k_conv - k_hrana)


def o_rulare(config: Path, fel: str, pasi: int, context: int, fire: int = 1) -> dict[str, Any]:
    """Antrenează modelul mic `pasi` pași cu portul `date` din configurare și notează fiecare lot și fiecare pierdere."""
    import torch

    import module.model_continuu as mc
    from kronos.registru import Registru

    inceput = time.perf_counter()
    c = tomllib.loads(config.read_text(encoding="utf-8"))
    modul, setari = setarile_modelului(c, fel, pasi, context)
    determinist, fire_inainte = torch.are_deterministic_algorithms_enabled(), torch.get_num_threads()
    cale_veche = mc.cale_simboluri
    cache_folosit: list[str] = []

    def cale_spion(*a: Any, **k: Any) -> Path:
        fisier = cale_veche(*a, **k)
        cache_folosit.append(fisier.name)
        return fisier

    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(fire)
    mc.cale_simboluri = cale_spion
    try:
        date = Registru().creeaza("date", c["porturi"]["date"]["modul"], c["porturi"]["date"]["setari"]).instanta
        ram_dupa_date = ram_varf_mb()
        model = Registru().creeaza("model", modul, setari).instanta
        pierderi: list[float] = []
        loturi: list[dict[str, Any]] = []
        peste_tot = hashlib.sha256()

        def noteaza(x: Any, y: Any) -> None:
            peste_tot.update(x.detach().cpu().contiguous().numpy().tobytes())
            peste_tot.update(y.detach().cpu().contiguous().numpy().tobytes())
            loturi.append({"sha": _sha_tensori(x, y)[:16],
                           "randuri": [_sha_tensori(x[i], y[i])[:12] for i in range(x.shape[0])],
                           "feluri": feluri_de_ferestre(model, fel, len(loturi))})

        pas_mascat, pas_simplu = getattr(model, "_pas_mascat", None), model._pas  # cel mascat: doar cu conversație

        def cu_nota_mascat(x: Any, y: Any) -> float:
            noteaza(x, y)
            pierderi.append(pas_mascat(x, y))
            return pierderi[-1]

        def cu_nota(x: Any, y: Any, m: Any) -> float:
            noteaza(x, y)
            pierderi.append(pas_simplu(x, y, m))
            return pierderi[-1]

        model._pas = cu_nota
        if pas_mascat is not None:
            model._pas_mascat = cu_nota_mascat
        t0 = time.perf_counter()
        statistici = model.antreneaza(date, 3600.0)
        secunde_antrenare = time.perf_counter() - t0
        greutati = _sha_tensori(*[v for _, v in sorted(model.retea.state_dict().items())])
    finally:
        mc.cale_simboluri = cale_veche
        torch.use_deterministic_algorithms(determinist)
        torch.set_num_threads(fire_inainte)
    return {
        "config": str(config).replace("\\", "/"), "fel": fel, "date_modul": c["porturi"]["date"]["modul"],
        "model_modul": modul, "setari_model": setari, "fire": fire, "pasi": len(pierderi),
        "pierderi": pierderi, "pierderi_hex": [float(p).hex() for p in pierderi],
        "loturi": loturi, "sha256_loturi": peste_tot.hexdigest(), "sha256_greutati": greutati,
        "statistici": statistici, "cache_folosit": cache_folosit,
        "secunde_antrenare": round(secunde_antrenare, 2), "secunde_total": round(time.perf_counter() - inceput, 2),
        "ram_varf_mb_dupa_date": ram_dupa_date, "ram_varf_mb": ram_varf_mb(),
    }


def compara(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    """Două rulări, pas cu pas: aceleași loturi și aceleași pierderi (bit cu bit)?"""
    primul_lot = next((i for i, (x, y) in enumerate(zip(a["loturi"], b["loturi"])) if x["sha"] != y["sha"]), None)
    primul = next((i for i, (x, y) in enumerate(zip(a["pierderi_hex"], b["pierderi_hex"])) if x != y), None)
    rez: dict[str, Any] = {
        "pasi": [a["pasi"], b["pasi"]],
        "pierderi_identice": a["pasi"] == b["pasi"] and primul is None,
        "loturi_identice": a["pasi"] == b["pasi"] and primul_lot is None and a["sha256_loturi"] == b["sha256_loturi"],
        "greutati_identice": a["sha256_greutati"] == b["sha256_greutati"],
        "primul_pas_cu_pierdere_diferita": None if primul is None else primul + 1,
        "primul_pas_cu_lot_diferit": None if primul_lot is None else primul_lot + 1,
        "diferenta_maxima": max((abs(x - y) for x, y in zip(a["pierderi"], b["pierderi"])), default=0.0),
    }
    if primul_lot is not None:
        la, lb = a["loturi"][primul_lot], b["loturi"][primul_lot]
        rez["randuri_diferite"] = [{"rand": i, "fel": la["feluri"][i]} for i, (x, y)
                                   in enumerate(zip(la["randuri"], lb["randuri"])) if x != y]
    rez["identic"] = rez["pierderi_identice"] and rez["loturi_identice"] and rez["greutati_identice"]
    return rez


def _stare_dosar(dosar: Path) -> dict[str, list[int]]:
    return {p.name: [p.stat().st_size, p.stat().st_mtime_ns] for p in sorted(dosar.iterdir())} if dosar.is_dir() else {}


def _in_proces_nou(config: Path, fel: str, pasi: int, context: int, iesire: Path) -> dict[str, Any]:
    proces = subprocess.run(
        [sys.executable, "-X", "utf8", str(Path(__file__).resolve()), "_rulare", "--config", str(config), "--fel", fel,
         "--pasi", str(pasi), "--context", str(context), "--iesire", str(iesire)],
        capture_output=True, text=True, encoding="utf-8", cwd=RADACINA, env=os.environ | {"CUDA_VISIBLE_DEVICES": "-1"})
    if proces.returncode != 0:
        raise RuntimeError(f"rularea {iesire.name} a picat (cod {proces.returncode}): {proces.stderr[-3000:]}")
    return json.loads(iesire.read_text(encoding="utf-8"))


def tot(config_vechi: Path, config_bucati: Path, dosar: Path, pasi: int = 200, context: int = 64,
        feluri: tuple[str, ...] = FELURI, in_proces: bool = False) -> dict[str, Any]:
    """Toate rulările și comparațiile. Verdictul (DA/NU) e pe felul „conversatie”: A1 = B, pierderi și loturi."""
    rezumat = dosar / "s103.json"
    if rezumat.exists():
        raise FileExistsError(f"{rezumat} există deja: proba se face o singură dată")
    dosar.mkdir(parents=True, exist_ok=True)
    inceput = time.perf_counter()
    c_vechi = tomllib.loads(config_vechi.read_text(encoding="utf-8"))
    c_bucati = tomllib.loads(config_bucati.read_text(encoding="utf-8"))
    if c_bucati["porturi"]["date"]["modul"] != "module.date_bucati:DateBucati":
        raise ValueError(f"{config_bucati}: portul date nu e module.date_bucati:DateBucati")
    if c_vechi["porturi"]["date"]["modul"] == "module.date_bucati:DateBucati":
        raise ValueError(f"{config_vechi}: portul date trebuie să fie cel vechi (text), nu datele pe bucăți")
    paznite = {nume: Path(d) for nume, d in (
        ("cache", c_vechi["porturi"]["model"]["setari"].get("director_cache") or ""),
        ("bucati", c_bucati["porturi"]["date"]["setari"]["director"])) if d}
    inainte = {nume: _stare_dosar(RADACINA / d if not d.is_absolute() else d) for nume, d in paznite.items()}

    def una(nume: str, config: Path, fel: str) -> dict[str, Any]:
        iesire = dosar / f"{fel}_{nume}.json"
        print(f"[{time.strftime('%H:%M:%S')}] {fel} {nume} …", flush=True)
        if in_proces:
            r = o_rulare(config, fel, pasi, context)
            iesire.write_text(json.dumps(r, indent=1, ensure_ascii=False), encoding="utf-8")
        else:
            r = _in_proces_nou(config, fel, pasi, context, iesire)
        print(f"[{time.strftime('%H:%M:%S')}] {fel} {nume}: {r['pasi']} pași, ultima pierdere {r['pierderi'][-1]:.6f}, "
              f"RAM de vârf {r['ram_varf_mb']} MB, {r['secunde_total']} s", flush=True)
        return r

    rez: dict[str, Any] = {"config_vechi": str(config_vechi).replace("\\", "/"),
                           "config_bucati": str(config_bucati).replace("\\", "/"), "pasi": pasi, "context": context,
                           "feluri": {}}
    for fel in feluri:
        rulari = {"A1": una("A1", config_vechi, fel)}
        if fel == "conversatie":
            rulari["A2"] = una("A2", config_vechi, fel)
        rulari["B"] = una("B", config_bucati, fel)
        f: dict[str, Any] = {
            "model_modul": rulari["A1"]["model_modul"], "setari_model": rulari["A1"]["setari_model"],
            "A1_fata_de_B": compara(rulari["A1"], rulari["B"]),
            "tabel": {str(p): {n: r["pierderi"][p - 1] for n, r in rulari.items()}
                      for p in PASI_TABEL + (pasi,) if p <= min(r["pasi"] for r in rulari.values())},
            "rulari": {n: {k: r[k] for k in ("date_modul", "pasi", "sha256_loturi", "sha256_greutati", "cache_folosit",
                                             "secunde_antrenare", "secunde_total", "ram_varf_mb_dupa_date",
                                             "ram_varf_mb", "statistici")} for n, r in rulari.items()},
            "ferestre": {k: sum(lot["feluri"].count(k) for lot in rulari["A1"]["loturi"])
                         for k in ("conversatie", "hrana", "text")},
        }
        if "A2" in rulari:
            f["A1_fata_de_A2"] = compara(rulari["A1"], rulari["A2"])
        rez["feluri"][fel] = f
    dupa = {nume: _stare_dosar(RADACINA / d if not d.is_absolute() else d) for nume, d in paznite.items()}
    rez["doar_citite_neschimbate"] = {nume: inainte[nume] == dupa[nume] for nume in paznite}
    principal = rez["feluri"].get("conversatie")
    if principal is not None:
        ab = principal["A1_fata_de_B"]
        rez["verdict"] = "DA" if ab["pierderi_identice"] and ab["loturi_identice"] else "NU"
        rez["procesorul_se_repeta"] = principal["A1_fata_de_A2"]["identic"]
    rez["toate_identice"] = all(f["A1_fata_de_B"]["identic"] for f in rez["feluri"].values())
    rez["secunde"] = round(time.perf_counter() - inceput, 1)
    rezumat.write_text(json.dumps(rez, indent=1, ensure_ascii=False), encoding="utf-8")
    return rez


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="comanda", required=True)
    s = sub.add_parser("tot")
    s.add_argument("--config-vechi", type=Path, default=Path("config/conv_w2_mare_24r.toml"))
    s.add_argument("--config-bucati", type=Path, default=Path("config/conv_w2_mare_24_bucati.toml"))
    s.add_argument("--iesire", required=True, type=Path)
    s.add_argument("--pasi", type=int, default=200)
    s.add_argument("--context", type=int, default=64)
    s.add_argument("--feluri", nargs="+", choices=FELURI, default=list(FELURI))
    s.add_argument("--in-proces", action="store_true", help="fără procese noi (doar pentru teste: RAM-ul nu se mai separă)")
    s = sub.add_parser("_rulare")
    s.add_argument("--config", required=True, type=Path)
    s.add_argument("--fel", required=True, choices=FELURI)
    s.add_argument("--pasi", type=int, default=200)
    s.add_argument("--context", type=int, default=64)
    s.add_argument("--iesire", required=True, type=Path)
    a = p.parse_args(argv)

    if a.comanda == "_rulare":
        r = o_rulare(a.config, a.fel, a.pasi, a.context)
        a.iesire.parent.mkdir(parents=True, exist_ok=True)
        a.iesire.write_text(json.dumps(r, indent=1, ensure_ascii=False), encoding="utf-8")
        return 0
    rez = tot(a.config_vechi, a.config_bucati, a.iesire, a.pasi, a.context, tuple(a.feluri), a.in_proces)
    scurt = {k: v for k, v in rez.items() if k != "feluri"}
    scurt["feluri"] = {fel: {k: f[k] for k in f if k.startswith("A1_")} for fel, f in rez["feluri"].items()}
    print(json.dumps(scurt, indent=1, ensure_ascii=False))
    if "verdict" in rez:
        return 0 if rez["verdict"] == "DA" else 1
    return 0 if rez["toate_identice"] else 1


if __name__ == "__main__":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    sys.exit(main())
