"""Descarcă sursele de date ale workstation-ului (docs/MUTARE_workstation.md, secțiunea 6), cu licența verificată.

Înainte de fiecare descărcare, licența se citește din nou de pe fișa oficială a sursei (Hugging Face) și se compară cu
cea așteptată; dacă diferă, sau dacă sursa cere cont, nu se descarcă nimic din ea. Pentru sursele OPUS (fără fișă cu
licență care să se poată citi automat) licența e cea verificată de om și notată aici.

Surse cu licență pe fișier (The Stack): fișa nu are o licență unică, fiecare fișier de cod are licența lui, iar
accesul cere cont și termeni acceptați pe site. Se descarcă doar dacă pe acest calculator e logat un cont Hugging Face
care a acceptat termenii (hf auth login; cheia NU se scrie în proiect). La curățare se păstrează doar fișierele cu
licențe permisive (unelte/curata_date_ws.py), iar atribuirile lor (depozit, cale, licență) se scriu alături.

Totul ajunge în date/ws/brut/<sursa>/ (date/ nu intră în Git), iar ce s-a descărcat se notează în
date/ws/brut/surse.json: sursa, licența, data, revizia, mărimea și amprenta sha256 a fiecărui fișier. Din el se scrie
docs/DATE_surse.md (unelte/curata_date_ws.py).

    python unelte/descarca_date_ws.py              # toate sursele
    python unelte/descarca_date_ws.py --doar tatoeba europarl
    python unelte/descarca_date_ws.py --verifica   # doar licențele, fără descărcare
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

DIRECTOR = Path("date/ws/brut")
LIMITA_GB = 60.0  # datele noi, în total (hotărât de Adrian, 12 octombrie 2026)

# hf: depozitul de pe Hugging Face; fisiere: prefixul fișierelor luate (toate cele care încep așa) sau lista lor.
SURSE: dict[str, dict[str, Any]] = {
    "wikipedia_ro": {
        "hf": "wikimedia/wikipedia", "prefix": "20231101.ro/", "licenta": ["cc-by-sa-3.0", "gfdl"],
        "descriere": "Wikipedia în română, copia din 1 noiembrie 2023, curățată de Wikimedia",
        "obligatii": "atribuire; ce redistribuim din ea rămâne sub aceeași licență (CC BY-SA)",
    },
    "wikisource_ro": {
        "hf": "wikimedia/wikisource", "prefix": "20231201.ro/", "licenta": ["cc-by-sa-3.0", "gfdl"],
        "descriere": "Wikisource în română, copia din 1 decembrie 2023, curățată de Wikimedia",
        "obligatii": "atribuire; aceeași licență la redistribuire; operele sunt mai ales în domeniul public",
    },
    "fineweb2_ro": {
        "hf": "HuggingFaceFW/fineweb-2", "fisiere": ["data/ron_Latn/train/000_00000.parquet"], "licenta": "odc-by",
        "descriere": "FineWeb-2, ron_Latn: un fișier din 20 (din el se taie o felie de 3 GB de text)",
        "obligatii": "atribuire; textele rămân ale site-urilor de unde au fost luate (termenii Common Crawl)",
    },
    "fabule_ro": {
        "hf": "klusai/ds-tf3-ro-3m", "prefix": "data/", "licenta": "apache-2.0",
        "descriere": "ds-tf3-ro-3m: 3 milioane de fabule în română, generate de alt model",
        "obligatii": "atribuire; dacă modelul se publică vreodată, se reverifică termenii modelului care le-a generat",
    },
    "cod_instruct": {
        "hf": "bigcode/self-oss-instruct-sc2-exec-filter-50k", "prefix": "data/", "licenta": "odc-by",
        "descriere": "self-oss-instruct-sc2-exec-filter-50k: 50.000 de perechi sarcină–cod Python, verificate prin rulare",
        "obligatii": "atribuire",
    },
    "cod_stack_smol": {
        "hf": "bigcode/the-stack-smol", "fisiere": ["data/python/data.json"], "licenta": "pe-fisier",
        "licenta_pe_fisier": True,
        "descriere": "The Stack smol, Python: 10.000 de fișiere de cod, fiecare cu licența lui",
        "obligatii": "termenii The Stack, acceptați de Adrian cu contul lui; se păstrează doar fișierele cu licențe "
                     "permisive, cu atribuirea lor (depozit, cale, licență)",
    },
    "cod_stack_dedup": {
        "hf": "bigcode/the-stack-dedup", "licenta": "pe-fisier", "licenta_pe_fisier": True,
        "fisiere": [f"data/python/data-{k:05d}-of-00144.parquet" for k in range(3)],
        "descriere": "The Stack dedup, Python: 3 fișiere din 144 (din ele se taie o felie de cod curat)",
        "obligatii": "termenii The Stack, acceptați de Adrian cu contul lui; se păstrează doar fișierele cu licențe "
                     "permisive, cu atribuirea lor (depozit, cale, licență)",
    },
    "tatoeba_en_ro": {
        "url": "https://object.pouta.csc.fi/OPUS-Tatoeba/v2023-04-12/moses/en-ro.txt.zip", "licenta": "cc-by-2.0-fr",
        "descriere": "Tatoeba engleză–română, prin OPUS (versiunea 2023-04-12)",
        "obligatii": "atribuire (tatoeba.org)", "licenta_de_la": "https://tatoeba.org/en/terms_of_use",
    },
    "europarl_en_ro": {
        "url": "https://object.pouta.csc.fi/OPUS-Europarl/v8/moses/en-ro.txt.zip", "licenta": "fara-licenta-formala",
        "descriere": "Europarl v8 engleză–română, prin OPUS",
        "obligatii": "sursa se menționează (Parlamentul European permite reutilizarea)",
        "licenta_de_la": "https://www.statmt.org/europarl/",
    },
}


def sha256(cale: Path) -> str:
    h = hashlib.sha256()
    with cale.open("rb") as f:
        while bucata := f.read(1 << 24):
            h.update(bucata)
    return h.hexdigest()


def fisier_notat(cale: Path) -> dict[str, Any]:
    return {"fisier": cale.resolve().relative_to(DIRECTOR.resolve()).as_posix(), "octeti": cale.stat().st_size,
            "sha256": sha256(cale)}


def verifica_hf(sursa: dict[str, Any]) -> tuple[str | None, dict[str, Any]]:
    """(de ce nu se poate descărca, sau None; ce spune fișa acum)."""
    from huggingface_hub import HfApi

    info = HfApi().dataset_info(sursa["hf"], files_metadata=True)
    licenta = (info.card_data.to_dict() if info.card_data else {}).get("license")
    fisa = {"licenta_pe_fisa": licenta, "cere_cont": bool(info.gated), "revizie": info.sha,
            "fisiere": {s.rfilename: s.size or 0 for s in info.siblings}}
    if sursa.get("licenta_pe_fisier"):
        # fiecare fișier are licența lui (filtrată la curățare); accesul cere un cont logat aici, cu termenii acceptați
        from huggingface_hub import get_token

        if not get_token():
            return "sursa cere cont și termeni acceptați pe site (niciun cont logat: hf auth login)", fisa
        return None, fisa
    if info.gated:
        return "sursa cere cont și termeni acceptați pe site", fisa
    if licenta is None or licenta != sursa["licenta"]:
        return f"licența de pe fișă ({licenta}) nu e cea așteptată ({sursa['licenta']})", fisa
    return None, fisa


def descarca(nume: str, sursa: dict[str, Any], doar_verifica: bool) -> dict[str, Any]:
    acum = datetime.now().isoformat(timespec="seconds")
    rand: dict[str, Any] = {"sursa": nume, "descriere": sursa["descriere"], "licenta": sursa["licenta"],
                            "obligatii": sursa["obligatii"], "verificat": acum, "fisiere": []}
    tinta = DIRECTOR / nume
    if "hf" in sursa:
        rand["de_unde"] = f"https://huggingface.co/datasets/{sursa['hf']}"
        motiv, fisa = verifica_hf(sursa)
        rand.update(licenta_pe_fisa=fisa["licenta_pe_fisa"], revizie=fisa["revizie"])
        if motiv:
            return {**rand, "stare": "nedescarcat", "motiv": motiv}
        de_luat = sursa.get("fisiere") or sorted(f for f in fisa["fisiere"] if f.startswith(sursa["prefix"]))
        rand["gb_de_descarcat"] = round(sum(fisa["fisiere"][f] for f in de_luat) / 1e9, 2)
        if doar_verifica:
            return {**rand, "stare": "verificat"}
        from huggingface_hub import hf_hub_download

        for f in de_luat:
            cale = Path(hf_hub_download(sursa["hf"], f, repo_type="dataset", revision=fisa["revizie"], local_dir=tinta))
            rand["fisiere"].append(fisier_notat(cale))
            print(f"   {cale.name}: {cale.stat().st_size / 1e6:,.0f} MB", flush=True)
    else:
        rand.update(de_unde=sursa["url"], licenta_de_la=sursa["licenta_de_la"])
        if doar_verifica:
            return {**rand, "stare": "verificat"}
        tinta.mkdir(parents=True, exist_ok=True)
        cale = tinta / sursa["url"].rsplit("/", 1)[1]
        if not cale.exists():
            partial = cale.with_name(cale.name + ".part")
            with urllib.request.urlopen(sursa["url"], timeout=120) as raspuns, partial.open("wb") as f:
                shutil.copyfileobj(raspuns, f, 1 << 20)
            partial.replace(cale)
        rand["fisiere"].append(fisier_notat(cale))
        print(f"   {cale.name}: {cale.stat().st_size / 1e6:,.1f} MB", flush=True)
    rand["octeti"] = sum(f["octeti"] for f in rand["fisiere"])
    return {**rand, "stare": "descarcat", "descarcat": datetime.now().isoformat(timespec="seconds")}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Descarcă sursele de date ale workstation-ului, cu licența verificată.")
    parser.add_argument("--doar", nargs="*", choices=list(SURSE), help="doar aceste surse")
    parser.add_argument("--verifica", action="store_true", help="doar licențele, fără descărcare")
    args = parser.parse_args(argv)

    DIRECTOR.mkdir(parents=True, exist_ok=True)
    fisier = DIRECTOR / "surse.json"
    notate: dict[str, Any] = json.loads(fisier.read_text(encoding="utf-8")) if fisier.exists() else {}
    for nume in args.doar or list(SURSE):
        ocupat = sum(f.stat().st_size for f in Path("date/ws").rglob("*") if f.is_file()) / 1e9
        if ocupat > LIMITA_GB:
            print(f"Opresc: datele noi ocupă deja {ocupat:.1f} GB (limita e {LIMITA_GB:.0f} GB).")
            return 1
        print(f"{nume}: {SURSE[nume]['descriere']}", flush=True)
        try:
            rand = descarca(nume, SURSE[nume], args.verifica)
        except Exception as e:  # noqa: BLE001 - o sursă căzută nu le oprește pe celelalte
            rand = {"sursa": nume, "stare": "eroare", "motiv": f"{type(e).__name__}: {e}",
                    "verificat": datetime.now().isoformat(timespec="seconds")}
        print(f"   → {rand['stare']}" + (f": {rand['motiv']}" if rand.get("motiv") else ""), flush=True)
        if not args.verifica:
            notate[nume] = rand
            fisier.write_text(json.dumps(notate, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
