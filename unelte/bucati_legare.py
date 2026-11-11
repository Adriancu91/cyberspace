"""Legarea datelor pe bucăți (S98, C-85 pasul 5, partea b): proba că module/date_bucati.py dă aceleași loturi ca
tensorul întreg din lucru/cache și măsurarea pornirii părții de date. Doar procesor, fără model, fără placă.

Comenzi:
  identitate  --config config/conv_w2_mare_24_bucati.toml [--loturi 1000] --iesire <fisier.json>
              Cu sămânța, lotul și contextul din configurare: primele `--loturi` loturi din calea veche (tensorul întreg
              din cache, cu rândurile din bucla de antrenare) și din modulul nou (`lot()` și, separat, șirul pe bucăți pus
              în aceleași rânduri) — SHA-256 pe fiecare lot și pe toate. Plus 3 loturi puse anume la granițe de bucată și
              unul la capetele șirului. Refuză dacă fișierul de ieșire există. Cod 1 dacă ceva diferă.
  pornire     --config config/conv_w2_mare_24_bucati.toml --iesire <fisier.json> [--reper lucru/bucati/s96_identitate.json]
              Într-un proces nou: timpul și RAM-ul de vârf ale pornirii părții de date cu modulul nou (verificarea
              bucăților, amprenta, validarea, primul lot), lângă cifrele căii vechi din S96.
"""

from __future__ import annotations

import argparse
import hashlib
import json
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


def _config(cale: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    c = tomllib.loads(cale.read_text(encoding="utf-8"))
    date = c["porturi"]["date"]
    if date["modul"] != "module.date_bucati:DateBucati":
        raise ValueError(f"{cale}: portul date nu e module.date_bucati:DateBucati")
    return date, c["porturi"]["model"]["setari"]


def _modul(date: dict[str, Any]) -> Any:
    """Modulul, încărcat ca pe platformă (registrul verifică fișa și contractul)."""
    from kronos.registru import Registru

    return Registru().creeaza("date", date["modul"], date["setari"]).instanta


def _sha_lot(x: Any, y: Any) -> str:
    h = hashlib.sha256()
    h.update(x.numpy().tobytes())
    h.update(y.numpy().tobytes())
    return h.hexdigest()


def _stare_fisier(cale: Path) -> dict[str, Any]:
    s = cale.stat()
    return {"octeti": s.st_size, "schimbat_la": s.st_mtime_ns}


def loturi_la_granita(index: dict[str, Any], lot: int, ctx: int) -> list[dict[str, Any]]:
    """3 loturi cu ferestrele puse anume peste o graniță de bucată (prima, cea din mijloc, ultima) și unul cu ferestrele
    de la capetele șirului."""
    inceputuri = [b["inceput"] for b in index["bucati"]][1:]
    if not inceputuri:
        raise ValueError("o singură bucată: nu există graniță de verificat")
    total = index["simboluri_total"]
    alese = [inceputuri[0], inceputuri[len(inceputuri) // 2], inceputuri[-1]]
    loturi = []
    for g in alese:
        # fereastra are ctx + 1 simboluri: ultima ei poziție cade pe primul simbol al bucății următoare, la mijloc, …
        pozitii = [g - ctx, g - ctx // 2, g - 1, g][:lot]
        loturi.append({"granita": g, "pozitii": [max(0, min(p, total - ctx - 2)) for p in pozitii]})
    capete = [0, 1, total - ctx - 3, total - ctx - 2][:lot]  # randint dă cel mult total - ctx - 2
    loturi.append({"granita": None, "pozitii": capete})
    return loturi


def identitate(config: Path, loturi: int) -> dict[str, Any]:
    import torch

    inceput = time.perf_counter()
    date, model = _config(config)
    ctx, lot, samanta = int(model["context"]), int(model["lot"]), int(model["samanta"])
    d = _modul(date)
    sir = d.sir_antrenare()
    cache = RADACINA / d.index["sursa"]["fisier"]
    cache_inainte = _stare_fisier(cache)
    # Calea veche: tensorul întreg, cum îl încarcă module/model_continuu.simboluri_din_cache.
    date_t = torch.as_tensor(torch.load(cache, weights_only=True))
    rez: dict[str, Any] = {
        "config": str(config).replace("\\", "/"), "context": ctx, "lot": lot, "samanta": samanta, "loturi": loturi,
        "cache": d.index["sursa"]["fisier"], "simboluri_cache": len(date_t), "simboluri_bucati": len(sir),
        "tip_cache": str(date_t.dtype).replace("torch.", ""), "date": d.descriere(),
    }
    if len(date_t) != len(sir):
        rez.update(identic=False, motiv="alt număr de simboluri în cache decât în bucăți")
        return rez

    g_vechi = torch.Generator(device="cpu").manual_seed(samanta)
    g_nou = torch.Generator(device="cpu").manual_seed(samanta)
    g_sir = torch.Generator(device="cpu").manual_seed(samanta)
    tot = {nume: hashlib.sha256() for nume in ("vechi", "nou", "sir")}
    primul_diferit: dict[str, Any] | None = None
    ferestre_la_granita = 0
    for k in range(loturi):
        # rândurile din bucla de antrenare (module/model_gpt.py), pe tensorul întreg
        pozitii = torch.randint(len(date_t) - ctx - 1, (lot,), generator=g_vechi)
        x = torch.stack([date_t[p: p + ctx] for p in pozitii]).long()
        y = torch.stack([date_t[p + 1: p + ctx + 1] for p in pozitii]).long()
        vechi = _sha_lot(x, y)
        nou = _sha_lot(*d.lot(lot, ctx, g_nou))
        # aceleași rânduri, cu șirul pe bucăți în locul tensorului
        pozitii_sir = torch.randint(len(sir) - ctx - 1, (lot,), generator=g_sir)
        x_sir = torch.stack([sir[p: p + ctx] for p in pozitii_sir]).long()
        y_sir = torch.stack([sir[p + 1: p + ctx + 1] for p in pozitii_sir]).long()
        prin_sir = _sha_lot(x_sir, y_sir)
        ferestre_la_granita += sum(len(sir.bucati_atinse(int(p), int(p) + ctx + 1)) > 1 for p in pozitii)
        for nume, sha in (("vechi", vechi), ("nou", nou), ("sir", prin_sir)):
            tot[nume].update(bytes.fromhex(sha))
        if primul_diferit is None and not (vechi == nou == prin_sir):
            primul_diferit = {"lot": k, "pozitii": [int(p) for p in pozitii], "sha_vechi": vechi, "sha_nou": nou,
                              "sha_sir": prin_sir}
        if k == 0:
            rez["primul_lot"] = {"pozitii": [int(p) for p in pozitii], "sha256": vechi}
    rez["sha256_loturi"] = {nume: h.hexdigest() for nume, h in tot.items()}
    rez["ferestre_la_granita_in_loturile_trase"] = ferestre_la_granita
    rez["primul_lot_diferit"] = primul_diferit

    granite = []
    for g in loturi_la_granita(d.index, lot, ctx):
        pozitii = g["pozitii"]
        x = torch.stack([date_t[p: p + ctx] for p in pozitii]).long()
        y = torch.stack([date_t[p + 1: p + ctx + 1] for p in pozitii]).long()
        vechi = _sha_lot(x, y)
        nou = _sha_lot(*d.ferestre(pozitii, ctx))
        prin_sir = _sha_lot(torch.stack([sir[p: p + ctx] for p in pozitii]).long(),
                            torch.stack([sir[p + 1: p + ctx + 1] for p in pozitii]).long())
        granite.append({"granita": g["granita"], "pozitii": pozitii,
                        "bucati_atinse": [sir.bucati_atinse(p, p + ctx + 1) for p in pozitii],
                        "sha_vechi": vechi, "sha_nou": nou, "sha_sir": prin_sir, "identic": vechi == nou == prin_sir})
    rez["loturi_la_granita"] = granite
    rez["cache_neschimbat"] = _stare_fisier(cache) == cache_inainte
    rez["identic"] = (primul_diferit is None and all(g["identic"] for g in granite)
                      and len(set(rez["sha256_loturi"].values())) == 1)
    rez["verdict"] = "DA" if rez["identic"] else "NU"
    rez["secunde"] = round(time.perf_counter() - inceput, 2)
    rez["ram_varf_mb"] = ram_varf_mb()
    return rez


def masoara_pornire(config: Path) -> dict[str, Any]:
    """Pornirea părții de date cu modulul nou, pas cu pas (secundele și RAM-ul de vârf de până atunci)."""
    pasi: dict[str, Any] = {"ram_varf_mb_la_inceput": ram_varf_mb()}
    t0 = time.perf_counter()
    date, model = _config(config)
    d = _modul(date)  # verificarea bucăților (SHA pe toate) + citirea validării sunt în constructor
    pasi["modul_secunde"] = round(time.perf_counter() - t0, 2)
    pasi["ram_varf_mb_dupa_modul"] = ram_varf_mb()
    pasi["verificare"] = d.verificare
    t1 = time.perf_counter()
    pasi["amprenta"] = d.amprenta()
    pasi["amprenta_secunde"] = round(time.perf_counter() - t1, 4)
    pasi["simboluri"] = d.numar_simboluri()
    pasi["validare_caractere"] = len(d.text_validare())
    t2 = time.perf_counter()
    import torch

    pasi["torch_secunde"] = round(time.perf_counter() - t2, 2)
    pasi["ram_varf_mb_dupa_torch"] = ram_varf_mb()
    t3 = time.perf_counter()
    generator = torch.Generator(device="cpu").manual_seed(int(model["samanta"]))
    x, y = d.lot(int(model["lot"]), int(model["context"]), generator)
    pasi["primul_lot_secunde"] = round(time.perf_counter() - t3, 4)
    pasi["primul_lot_sha256"] = _sha_lot(x, y)
    t4 = time.perf_counter()
    for _ in range(999):
        d.lot(int(model["lot"]), int(model["context"]), generator)
    pasi["urmatoarele_999_loturi_secunde"] = round(time.perf_counter() - t4, 2)
    pasi["secunde_total"] = round(time.perf_counter() - t0, 2)
    pasi["secunde_pana_la_primul_lot"] = round(t3 - t0 + pasi["primul_lot_secunde"], 2)
    pasi["ram_varf_mb"] = ram_varf_mb()
    return pasi


def pornire(config: Path, reper: Path | None) -> dict[str, Any]:
    proces = subprocess.run([sys.executable, "-X", "utf8", str(Path(__file__).resolve()), "_pornire", "--config",
                             str(config)], capture_output=True, text=True, encoding="utf-8", cwd=RADACINA,
                            env=os.environ | {"CUDA_VISIBLE_DEVICES": "-1"})
    if proces.returncode != 0:
        raise RuntimeError(f"măsurarea pornirii a picat (cod {proces.returncode}): {proces.stderr[-2000:]}")
    rez: dict[str, Any] = {"config": str(config).replace("\\", "/"),
                           "nou": json.loads(proces.stdout.strip().splitlines()[-1])}
    if reper is not None and reper.exists():
        vechi = json.loads(reper.read_text(encoding="utf-8")).get("pornire_linie")
        if vechi:
            rez["vechi_s96"] = vechi
            rez["ram_de_cate_ori_mai_putin"] = round(vechi["ram_varf_mb"] / max(1, rez["nou"]["ram_varf_mb"]), 1)
            rez["secunde_vechi_fata_de_nou"] = [vechi["secunde_total"], rez["nou"]["secunde_pana_la_primul_lot"]]
    rez["asteptare_sub_4000_mb"] = rez["nou"]["ram_varf_mb"] < 4000
    return rez


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="comanda", required=True)
    s = sub.add_parser("identitate")
    s.add_argument("--config", required=True, type=Path)
    s.add_argument("--loturi", type=int, default=1000)
    s.add_argument("--iesire", required=True, type=Path)
    s = sub.add_parser("pornire")
    s.add_argument("--config", required=True, type=Path)
    s.add_argument("--iesire", required=True, type=Path)
    s.add_argument("--reper", type=Path, default=None)
    s = sub.add_parser("_pornire")
    s.add_argument("--config", required=True, type=Path)
    a = p.parse_args(argv)

    if a.comanda == "_pornire":
        print(json.dumps(masoara_pornire(a.config), ensure_ascii=False))
        return 0
    if a.iesire.exists():
        raise FileExistsError(f"{a.iesire} există deja")
    if a.comanda == "identitate":
        rez = identitate(a.config, a.loturi)
        cod = 0 if rez["identic"] else 1
    else:
        rez = pornire(a.config, a.reper)
        cod = 0
    a.iesire.parent.mkdir(parents=True, exist_ok=True)
    a.iesire.write_text(json.dumps(rez, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(rez, ensure_ascii=False))
    return cod


if __name__ == "__main__":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    sys.exit(main())
