"""Date pe bucăți (S96, C-85 pasul 5): simbolurile gata făcute din lucru/cache, tăiate în bucăți de mărime fixă și
citite pe rând, fără să stea tot șirul în memorie. NU e legată de nicio configurare (legarea în antrenare = altă sarcină).

Comenzi:
  scrie       --sursa lucru/cache/simboluri_<cheie>.pt --iesire lucru/bucati/<nume> [--marime 50000000]
              [--tokenizer date/ws/bpe_16384.json] [--minim-liber-gb 20]
              Scrie bucata_00000.bin, … (simbolurile brute, little-endian, tipul din sursă) și index.json (ordinea,
              mărimea, SHA-256 pe fiecare bucată și pe tot șirul, tokenizerul și sursa). Sursa e doar citită (mmap).
              Refuză dacă index.json există. Dacă discul ar coborî sub --minim-liber-gb, scrie doar primele bucăți
              care încap și notează „partial” în index.
  citeste     --dosar lucru/bucati/<nume>   Trece prin toate bucățile, pe rând: numărul de simboluri, SHA-ul șirului
              întreg, RAM-ul de vârf și timpul (JSON).
  verifica    --dosar lucru/bucati/<nume>   Recalculează SHA-urile și le compară cu indexul (cod 1 la nepotrivire).
  identitate  --sursa … --dosar … [--config config/conv_w2_mare_24r.toml] [--iesire <fisier.json>]
              Proba: în procese separate (ca RAM-ul să fie al fiecăruia) măsoară (a) încărcarea de acum
              (torch.load întreg, ca antrenarea), (b) cititorul pe bucăți, (c) cu --config, încărcarea întreagă de la
              pornirea liniei (textul din portul date + amprenta + simbolurile din cache), și compară SHA-ul șirului.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Iterator

import numpy as np

RADACINA = Path(__file__).resolve().parents[1]
VERSIUNE = 1
TIPURI = {"int16": np.int16, "int32": np.int32}


def _sha256_fisier(cale: Path, bloc: int = 64 * 2**20) -> str:
    h = hashlib.sha256()
    with cale.open("rb") as f:
        while b := f.read(bloc):
            h.update(b)
    return h.hexdigest()


def ram_varf_mb() -> int | None:
    """RAM-ul de vârf al procesului (Windows: peak working set), în MB; None dacă nu se poate afla."""
    try:
        import psutil

        info = psutil.Process().memory_info()
        varf = getattr(info, "peak_wset", None)
        if varf is None:
            import resource  # pragma: no cover - doar pe Linux

            return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024)
        return int(varf // 2**20)
    except Exception:  # pragma: no cover
        return None


def _deschide_sursa(sursa: Path) -> np.ndarray:
    """Tensorul 1D din cache, deschis prin mmap (nu se încarcă în memorie), ca tablou numpy."""
    import torch

    t = torch.load(sursa, weights_only=True, mmap=True)
    if not isinstance(t, torch.Tensor) or t.dim() != 1:
        raise ValueError(f"{sursa}: aștept un tensor cu o singură dimensiune")
    if t.dtype not in (torch.int16, torch.int32):
        raise ValueError(f"{sursa}: tip neașteptat {t.dtype}")
    return t.contiguous().numpy()


def _octeti(a: np.ndarray) -> memoryview:
    """Octeții tabloului în ordinea little-endian (fără copie pe Windows/x86)."""
    if a.dtype.byteorder == ">" or (a.dtype.byteorder == "=" and sys.byteorder == "big"):  # pragma: no cover
        a = a.astype(a.dtype.newbyteorder("<"))
    return memoryview(np.ascontiguousarray(a)).cast("B")


def scrie(sursa: Path, iesire: Path, marime: int, tokenizer: Path | None, minim_liber_gb: float) -> dict[str, Any]:
    index_cale = iesire / "index.json"
    if index_cale.exists():
        raise FileExistsError(f"{index_cale} există deja: nu scriu peste bucăți făcute")
    if marime <= 0:
        raise ValueError("--marime trebuie să fie pozitivă")
    inceput = time.perf_counter()
    simboluri = _deschide_sursa(sursa)
    tip = str(simboluri.dtype)
    total = len(simboluri)
    nr_bucati = (total + marime - 1) // marime
    iesire.mkdir(parents=True, exist_ok=True)
    liber = shutil.disk_usage(iesire).free
    pe_simbol = simboluri.dtype.itemsize
    incap = max(0, int((liber - minim_liber_gb * 2**30) // (marime * pe_simbol)))
    partial = incap < nr_bucati
    de_scris = min(nr_bucati, incap)
    tot = hashlib.sha256()
    bucati = []
    for i in range(de_scris):
        felie = simboluri[i * marime:(i + 1) * marime]
        octeti = _octeti(felie)
        nume = f"bucata_{i:05d}.bin"
        temporar = iesire / (nume + ".part")
        with temporar.open("wb") as f:
            f.write(octeti)
        temporar.replace(iesire / nume)
        bucati.append({"fisier": nume, "inceput": i * marime, "simboluri": len(felie),
                       "sha256": hashlib.sha256(octeti).hexdigest()})
        tot.update(octeti)
    scrise = sum(b["simboluri"] for b in bucati)
    index = {
        "versiune": VERSIUNE,
        "tip": tip,
        "ordine_octeti": "little",
        "marime_bucata": marime,
        "simboluri_total": scrise,
        "simboluri_sursa": total,
        "partial": partial,
        "sha256_tot": tot.hexdigest(),
        "sursa": {"fisier": str(sursa).replace("\\", "/"), "octeti": sursa.stat().st_size},
        "tokenizer": ({"fisier": str(tokenizer).replace("\\", "/"), "sha256": _sha256_fisier(tokenizer)}
                      if tokenizer else None),
        "bucati": bucati,
        "scris_la": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "secunde": round(time.perf_counter() - inceput, 2),
        "ram_varf_mb": ram_varf_mb(),
    }
    if partial:
        index["nota_partial"] = (f"scrise {de_scris}/{nr_bucati} bucăți: restul ar fi lăsat discul sub "
                                 f"{minim_liber_gb} GB liberi")
    index_cale.write_text(json.dumps(index, indent=1, ensure_ascii=False), encoding="utf-8")
    return index


def citeste_index(dosar: Path) -> dict[str, Any]:
    return json.loads((dosar / "index.json").read_text(encoding="utf-8"))


class CititorBucati:
    """Dă simbolurile bucată cu bucată (tablouri numpy, doar citire, prin mmap), în ordinea din index.
    În memorie stă cel mult o bucată odată (paginile pe care le atingi)."""

    def __init__(self, dosar: str | Path) -> None:
        self.dosar = Path(dosar)
        self.index = citeste_index(self.dosar)
        if self.index.get("versiune") != VERSIUNE:
            raise ValueError(f"index de versiune necunoscută: {self.index.get('versiune')}")
        self.tip = TIPURI[self.index["tip"]]

    def __len__(self) -> int:
        return int(self.index["simboluri_total"])

    @property
    def numar_bucati(self) -> int:
        return len(self.index["bucati"])

    def bucata(self, i: int) -> np.ndarray:
        b = self.index["bucati"][i]
        a = np.memmap(self.dosar / b["fisier"], dtype=np.dtype(self.tip).newbyteorder("<"), mode="r")
        if len(a) != b["simboluri"]:
            raise ValueError(f"{b['fisier']}: {len(a)} simboluri, indexul zice {b['simboluri']}")
        return a

    def __iter__(self) -> Iterator[np.ndarray]:
        for i in range(self.numar_bucati):
            a = self.bucata(i)
            yield a
            del a


def citeste(dosar: Path) -> dict[str, Any]:
    inceput = time.perf_counter()
    cititor = CititorBucati(dosar)
    h = hashlib.sha256()
    n = 0
    for a in cititor:
        h.update(_octeti(a))
        n += len(a)
    return {"simboluri": n, "bucati": cititor.numar_bucati, "sha256_tot": h.hexdigest(),
            "secunde": round(time.perf_counter() - inceput, 2), "ram_varf_mb": ram_varf_mb()}


def verifica(dosar: Path) -> dict[str, Any]:
    index = citeste_index(dosar)
    gresite = []
    tot = hashlib.sha256()
    for b in index["bucati"]:
        cale = dosar / b["fisier"]
        if not cale.exists():
            gresite.append({"fisier": b["fisier"], "problema": "lipsește"})
            continue
        octeti = cale.read_bytes()
        tot.update(octeti)
        if hashlib.sha256(octeti).hexdigest() != b["sha256"]:
            gresite.append({"fisier": b["fisier"], "problema": "SHA diferit"})
    if tot.hexdigest() != index["sha256_tot"]:
        gresite.append({"fisier": "(tot șirul)", "problema": "SHA diferit"})
    return {"bucati": len(index["bucati"]), "gresite": gresite, "ok": not gresite}


def masoara_incarcare(sursa: Path) -> dict[str, Any]:
    """Încărcarea de acum: torch.load întreg (ca module/model_continuu.simboluri_din_cache), apoi SHA-ul șirului."""
    import torch

    inceput = time.perf_counter()
    t = torch.load(sursa, weights_only=True)
    secunde_incarcare = time.perf_counter() - inceput
    ram = ram_varf_mb()
    sha = hashlib.sha256(_octeti(t.numpy())).hexdigest()
    return {"simboluri": len(t), "tip": str(t.dtype).replace("torch.", ""), "sha256_tot": sha,
            "secunde_incarcare": round(secunde_incarcare, 2), "ram_varf_mb_dupa_incarcare": ram,
            "ram_varf_mb": ram_varf_mb()}


def masoara_pornire(config: Path) -> dict[str, Any]:
    """Încărcarea întreagă de la pornirea liniei, partea de date: textul din portul date (read_text), amprenta lui și
    simbolurile din cache (torch.load întreg). Fără placă, fără model."""
    import tomllib

    import torch

    sys.path.insert(0, str(RADACINA))
    from module.model_continuu import cale_simboluri

    c = tomllib.loads(config.read_text(encoding="utf-8"))
    setari_date = c["porturi"]["date"]["setari"]
    model = c["porturi"]["model"]["setari"]
    pasi: dict[str, Any] = {}
    t0 = time.perf_counter()
    text = Path(setari_date["cale_antrenare"]).read_text(encoding="utf-8")
    pasi["text_secunde"] = round(time.perf_counter() - t0, 2)
    pasi["text_caractere"] = len(text)
    pasi["ram_varf_mb_dupa_text"] = ram_varf_mb()
    t1 = time.perf_counter()
    fisier = cale_simboluri(text, model["director_cache"], model["cale_tokenizer"])
    pasi["amprenta_secunde"] = round(time.perf_counter() - t1, 2)
    pasi["fisier_cache"] = str(fisier).replace("\\", "/")
    pasi["ram_varf_mb_dupa_amprenta"] = ram_varf_mb()
    t2 = time.perf_counter()
    simboluri = torch.load(fisier, weights_only=True)
    pasi["simboluri_secunde"] = round(time.perf_counter() - t2, 2)
    pasi["simboluri"] = len(simboluri)
    pasi["secunde_total"] = round(time.perf_counter() - t0, 2)
    pasi["ram_varf_mb"] = ram_varf_mb()
    return pasi


def _in_proces_nou(*argumente: str) -> dict[str, Any]:
    rezultat = subprocess.run([sys.executable, "-X", "utf8", str(Path(__file__).resolve()), *argumente],
                              capture_output=True, text=True, encoding="utf-8", cwd=RADACINA)
    if rezultat.returncode != 0:
        raise RuntimeError(f"{argumente[0]} a picat (cod {rezultat.returncode}): {rezultat.stderr[-2000:]}")
    return json.loads(rezultat.stdout.strip().splitlines()[-1])


def identitate(sursa: Path, dosar: Path, config: Path | None) -> dict[str, Any]:
    rez: dict[str, Any] = {"sursa": str(sursa).replace("\\", "/"), "dosar": str(dosar).replace("\\", "/")}
    rez["acum"] = _in_proces_nou("_incarcare", "--sursa", str(sursa))
    rez["cititor"] = _in_proces_nou("citeste", "--dosar", str(dosar))
    if config is not None:
        rez["pornire_linie"] = _in_proces_nou("_pornire", "--config", str(config))
    index = citeste_index(dosar)
    rez["index_sha256_tot"] = index["sha256_tot"]
    rez["identic"] = (not index["partial"] and rez["acum"]["sha256_tot"] == rez["cititor"]["sha256_tot"]
                      == index["sha256_tot"] and rez["acum"]["simboluri"] == rez["cititor"]["simboluri"])
    rez["partial"] = index["partial"]
    return rez


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="comanda", required=True)
    s = sub.add_parser("scrie")
    s.add_argument("--sursa", required=True, type=Path)
    s.add_argument("--iesire", required=True, type=Path)
    s.add_argument("--marime", type=int, default=50_000_000)
    s.add_argument("--tokenizer", type=Path, default=None)
    s.add_argument("--minim-liber-gb", type=float, default=20.0)
    for nume in ("citeste", "verifica"):
        s = sub.add_parser(nume)
        s.add_argument("--dosar", required=True, type=Path)
    s = sub.add_parser("identitate")
    s.add_argument("--sursa", required=True, type=Path)
    s.add_argument("--dosar", required=True, type=Path)
    s.add_argument("--config", type=Path, default=None)
    s.add_argument("--iesire", type=Path, default=None)
    s = sub.add_parser("_incarcare")
    s.add_argument("--sursa", required=True, type=Path)
    s = sub.add_parser("_pornire")
    s.add_argument("--config", required=True, type=Path)
    a = p.parse_args(argv)

    cod = 0
    if a.comanda == "scrie":
        rez = scrie(a.sursa, a.iesire, a.marime, a.tokenizer, a.minim_liber_gb)
        rez = {k: v for k, v in rez.items() if k != "bucati"} | {"numar_bucati": len(rez["bucati"])}
    elif a.comanda == "citeste":
        rez = citeste(a.dosar)
    elif a.comanda == "verifica":
        rez = verifica(a.dosar)
        cod = 0 if rez["ok"] else 1
    elif a.comanda == "identitate":
        if a.iesire is not None and a.iesire.exists():
            raise FileExistsError(f"{a.iesire} există deja")
        rez = identitate(a.sursa, a.dosar, a.config)
        if a.iesire is not None:
            a.iesire.parent.mkdir(parents=True, exist_ok=True)
            a.iesire.write_text(json.dumps(rez, indent=1, ensure_ascii=False), encoding="utf-8")
        cod = 0 if rez["identic"] else 1
    elif a.comanda == "_incarcare":
        rez = masoara_incarcare(a.sursa)
    else:
        rez = masoara_pornire(a.config)
    print(json.dumps(rez, ensure_ascii=False))
    return cod


if __name__ == "__main__":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    sys.exit(main())
