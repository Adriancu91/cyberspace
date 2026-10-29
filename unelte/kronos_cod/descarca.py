"""Kronos-Cod, etapa 1b: descărcarea codului sursă, în flux, cu filtrele din `docs/kronos_cod/SURSE.md` (S43a, 28 octombrie 2026).

Modul `pilot` (aprobat de Adrian la 28 oct 18:00, doar pilotul): 500 de pachete PyPI + 500 de crate-uri + trei depozite
mari (numpy, tokio, libuv), apoi un rezumat JSON cu GB brut → curat, fișiere, simboluri estimate, cât a aruncat fiecare
filtru și de ce au fost respinse pachetele la licență.

Modul `complet` (S46a, 29 oct; pornirea cere „da”-ul lui Adrian, S46): toate cele 6 surse din SURSE.md, cu aceleași
filtre, licențe, dată, ritm și oprire sub 40 GB: depozitele Git din rândurile 3, 4, 6 la un tag dinainte de dată,
FreeBSD `release/13.0.0` (doar fișierele cu antet SPDX BSD, fără `contrib/` și `gnu/`), apoi PyPI top 30.000, apoi toate
crate-urile din dump-ul public `db-dump.tar.gz` (ultima versiune dinainte de dată, cele mai descărcate întâi). Ține 2–3
nopți: se reia de unde a rămas, `--limita-ore N` o oprește curat; o eroare de rețea trecătoare nu închide pachetul (se
reîncearcă la reluare), iar după 10 erori de rețea la rând se oprește singură.

Regulile (din SURSE.md):
- licențe doar MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause (și combinațiile lor), verificate de DOUĂ ori: metadatele
  (clasificatorii PyPI / câmpul `license` SPDX de la crates.io / licența declarată a depozitului) ȘI fișierul
  LICENSE/COPYING din arhivă; dacă nu se potrivesc sau lipsește fișierul, pachetul nu intră. Fișierele cu antet
  `SPDX-License-Identifier:` cu altă licență (sau cu text GPL/LGPL/MPL/ISC în antet) se aruncă;
- data-limită: doar versiuni publicate înainte de 29 iunie 2021 (ora 00:00 UTC);
- fișierele generate, cele copiate (`vendor/`, `third_party/`…), cele mari sau „de date”, cele care nu se citesc ca
  UTF-8 sau nu trec analiza sintactică, duplicatele exacte (SHA-256 pe textul normalizat) și, la final, aproape-duplicatele
  (MinHash pe 5-grame, 128 de permutări, 16 benzi × 8 rânduri, Jaccard ≥ 0,85; în grup rămâne cel mai lung).
- politețe: crates.io ≤ 1 cerere/s, PyPI ≤ 5 cereri/s, GitHub ≤ 1 cerere/s, un User-Agent care spune cine descarcă;
- în flux: arhivele se citesc din memorie, nu se scriu pe disc; pe disc ajung doar fișierele de cod care trec filtrele;
- se oprește singură dacă spațiul liber pe disc scade sub 40 GB; se poate relua de unde a rămas.

Ce scrie, în dosarul de ieșire (implicit `lucru/kronos_cod/pilot/` sau `lucru/kronos_cod/complet/`, nimic în Git):
    cod.jsonl          un rând pe fișier păstrat: sursa, pachetul, versiunea, calea, licența, sha256, textul
    pachete.jsonl      un rând pe pachet încheiat (păstrat / respins și de ce), cu poziția din cod.jsonl (pentru reluare)
    aproape_duplicate.json   ce a scos MinHash la final (indicii rândurilor din cod.jsonl)
    rezumat.json       cifrele pilotului

Comenzile:
    python unelte/kronos_cod/descarca.py pilot                       # tot pilotul (rețea!); se reia singur de unde a rămas
    python unelte/kronos_cod/descarca.py complet --limita-ore 10     # descărcarea întreagă, pe bucăți (rețea! cere „da”)
    python unelte/kronos_cod/descarca.py rezumat                     # doar refacerea rezumatului din ce e pe disc (fără rețea)
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import shutil
import sys
import tarfile
import time
import urllib.error
import urllib.request
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Callable, Iterable, Iterator

RADACINA = Path(__file__).resolve().parents[2]
IESIRE_PILOT = RADACINA / "lucru" / "kronos_cod" / "pilot"

DATA_LIMITA = datetime(2021, 6, 29, tzinfo=timezone.utc)
SPATIU_MINIM = 40 * 1024**3
OCTETI_PE_SIMBOL = 3.5
USER_AGENT = "Kronos-Cod-pilot/0.1 (cercetare personala, descarcare politicoasa; +https://github.com/Adriancu91)"

# câte cereri pe secundă, pe gazdă
RITM = {
    "pypi.org": 5.0,
    "files.pythonhosted.org": 5.0,
    "hugovk.github.io": 1.0,
    "crates.io": 1.0,
    "static.crates.io": 1.0,
    "codeload.github.com": 1.0,
}

LISTA_PYPI = "https://hugovk.github.io/top-pypi-packages/top-pypi-packages-30-days.min.json"
PILOT_PYPI = 500
PILOT_CRATES = 500

# depozitele mari ale pilotului: tag-ul dinainte de dată și licența declarată (din SURSE.md). Data commit-ului se
# verifică din arhivă (GitHub pune data commit-ului pe fiecare fișier), nu ne bazăm pe ce scrie aici.
DEPOZITE_PILOT = [
    {"nume": "numpy", "depozit": "numpy/numpy", "tag": "v1.21.0", "licenta": "BSD-3-Clause", "limbaj": "python"},
    {"nume": "tokio", "depozit": "tokio-rs/tokio", "tag": "tokio-1.7.0", "licenta": "MIT", "limbaj": "rust"},
    {"nume": "libuv", "depozit": "libuv/libuv", "tag": "v1.41.0", "licenta": "MIT", "limbaj": "c"},
]

IESIRE_COMPLET = RADACINA / "lucru" / "kronos_cod" / "complet"
COMPLET_PYPI = 30_000
DUMP_CRATES = "https://static.crates.io/db-dump.tar.gz"
DUMP_MAX = 4 * 1024**3  # dump-ul bazei crates.io, citit din memorie (~1 GB comprimat)
ARHIVA_MAX_DEPOZIT = 1024**3  # depozitele mari (FreeBSD, rust) trec de 300 MB comprimat
DESPACHETAT_MAX_DEPOZIT = 4 * 1024**3
ERORI_RETEA_LA_RAND = 10

# Rândurile 3–6 din SURSE.md, în ordinea de acolo (contează la duplicate: depozitele mari întâi). Tag-urile sunt dinainte
# de 29 iunie 2021; data se verifică oricum din arhivă (un tag greșit = pachet respins, se vede în rezumat).
#   dosar            doar fișierele de sub acest dosar (și fișierul de licență din el): lz4 = BSD-2 doar în `lib/`
#   fara_dosare      dosare sărite înainte de citire (oriunde în cale): FreeBSD `contrib/`, `gnu/`; redis `deps/` (copiate)
#   fisiere_licenta  doar aceste fișiere de licență contează: zstd e „BSD sau GPLv2” → îl luăm ca BSD (SURSE.md)
#   licenta_pe_fisier  FreeBSD: licența se ia din antetul SPDX al fiecărui fișier; fără antet BSD, fișierul nu intră
_PY, _RS, _C = "git_py", "git_rs", "git_c"
DEPOZITE_COMPLET = [
    {"sursa": _PY, "nume": "numpy", "depozit": "numpy/numpy", "tag": "v1.21.0", "licenta": "BSD-3-Clause"},
    {"sursa": _PY, "nume": "scipy", "depozit": "scipy/scipy", "tag": "v1.6.3", "licenta": "BSD-3-Clause"},
    {"sursa": _PY, "nume": "pandas", "depozit": "pandas-dev/pandas", "tag": "v1.2.5", "licenta": "BSD-3-Clause"},
    {"sursa": _PY, "nume": "scikit-learn", "depozit": "scikit-learn/scikit-learn", "tag": "0.24.2", "licenta": "BSD-3-Clause"},
    {"sursa": _PY, "nume": "sympy", "depozit": "sympy/sympy", "tag": "sympy-1.8", "licenta": "BSD-3-Clause"},
    {"sursa": _PY, "nume": "networkx", "depozit": "networkx/networkx", "tag": "networkx-2.5.1", "licenta": "BSD-3-Clause"},
    {"sursa": _PY, "nume": "django", "depozit": "django/django", "tag": "3.2.4", "licenta": "BSD-3-Clause"},
    {"sursa": _PY, "nume": "flask", "depozit": "pallets/flask", "tag": "2.0.1", "licenta": "BSD-3-Clause"},
    {"sursa": _PY, "nume": "click", "depozit": "pallets/click", "tag": "8.0.1", "licenta": "BSD-3-Clause"},
    {"sursa": _PY, "nume": "jinja", "depozit": "pallets/jinja", "tag": "3.0.1", "licenta": "BSD-3-Clause"},
    {"sursa": _PY, "nume": "httpx", "depozit": "encode/httpx", "tag": "0.18.2", "licenta": "BSD-3-Clause"},
    {"sursa": _PY, "nume": "scrapy", "depozit": "scrapy/scrapy", "tag": "2.5.0", "licenta": "BSD-3-Clause"},
    {"sursa": _PY, "nume": "tornado", "depozit": "tornadoweb/tornado", "tag": "v6.1.0", "licenta": "Apache-2.0"},
    {"sursa": _PY, "nume": "requests", "depozit": "psf/requests", "tag": "v2.25.1", "licenta": "Apache-2.0"},
    {"sursa": _PY, "nume": "pytest", "depozit": "pytest-dev/pytest", "tag": "6.2.4", "licenta": "MIT"},
    {"sursa": _PY, "nume": "black", "depozit": "psf/black", "tag": "21.6b0", "licenta": "MIT"},
    {"sursa": _PY, "nume": "attrs", "depozit": "python-attrs/attrs", "tag": "21.2.0", "licenta": "MIT"},
    {"sursa": _PY, "nume": "rich", "depozit": "Textualize/rich", "tag": "v10.4.0", "licenta": "MIT"},
    {"sursa": _PY, "nume": "sqlalchemy", "depozit": "sqlalchemy/sqlalchemy", "tag": "rel_1_4_18", "licenta": "MIT"},
    {"sursa": _PY, "nume": "pydantic", "depozit": "pydantic/pydantic", "tag": "v1.8.2", "licenta": "MIT"},
    {"sursa": _PY, "nume": "twisted", "depozit": "twisted/twisted", "tag": "twisted-21.2.0", "licenta": "MIT"},
    {"sursa": _PY, "nume": "pytorch", "depozit": "pytorch/pytorch", "tag": "v1.9.0", "licenta": "BSD-3-Clause"},
    {"sursa": _RS, "nume": "rust", "depozit": "rust-lang/rust", "tag": "1.53.0", "licenta": "MIT OR Apache-2.0"},
    {"sursa": _RS, "nume": "cargo", "depozit": "rust-lang/cargo", "tag": "0.54.0", "licenta": "MIT OR Apache-2.0"},
    {"sursa": _RS, "nume": "tokio", "depozit": "tokio-rs/tokio", "tag": "tokio-1.7.0", "licenta": "MIT"},
    {"sursa": _RS, "nume": "serde", "depozit": "serde-rs/serde", "tag": "v1.0.126", "licenta": "MIT OR Apache-2.0"},
    {"sursa": _RS, "nume": "rust-analyzer", "depozit": "rust-lang/rust-analyzer", "tag": "2021-06-21", "licenta": "MIT OR Apache-2.0"},
    {"sursa": _RS, "nume": "bevy", "depozit": "bevyengine/bevy", "tag": "v0.5.0", "licenta": "MIT"},
    {"sursa": _RS, "nume": "alacritty", "depozit": "alacritty/alacritty", "tag": "v0.8.0", "licenta": "Apache-2.0"},
    {"sursa": _RS, "nume": "deno", "depozit": "denoland/deno", "tag": "v1.11.2", "licenta": "MIT"},
    {"sursa": _RS, "nume": "ripgrep", "depozit": "BurntSushi/ripgrep", "tag": "13.0.0", "licenta": "MIT"},
    {"sursa": "freebsd", "nume": "freebsd", "depozit": "freebsd/freebsd-src", "tag": "release/13.0.0",
     "licenta": "BSD-2-Clause OR BSD-3-Clause", "licenta_pe_fisier": True, "fara_dosare": ["contrib", "gnu"]},
    {"sursa": _C, "nume": "libuv", "depozit": "libuv/libuv", "tag": "v1.41.0", "licenta": "MIT"},
    {"sursa": _C, "nume": "lua", "depozit": "lua/lua", "tag": "v5.4.3", "licenta": "MIT"},
    {"sursa": _C, "nume": "jq", "depozit": "jqlang/jq", "tag": "jq-1.6", "licenta": "MIT"},
    {"sursa": _C, "nume": "cjson", "depozit": "DaveGamble/cJSON", "tag": "v1.7.14", "licenta": "MIT"},
    {"sursa": _C, "nume": "redis", "depozit": "redis/redis", "tag": "6.2.4", "licenta": "BSD-3-Clause", "fara_dosare": ["deps"]},
    {"sursa": _C, "nume": "zstd", "depozit": "facebook/zstd", "tag": "v1.5.0", "licenta": "BSD-3-Clause",
     "fisiere_licenta": ["LICENSE"]},
    {"sursa": _C, "nume": "lz4", "depozit": "lz4/lz4", "tag": "v1.9.3", "licenta": "BSD-2-Clause", "dosar": "lib"},
]
for _d in DEPOZITE_COMPLET:
    _d.setdefault("arhiva_max", ARHIVA_MAX_DEPOZIT)
    _d.setdefault("despachetat_max", DESPACHETAT_MAX_DEPOZIT)

EXTENSII = {".py": "python", ".pyi": "python", ".rs": "rust", ".c": "c", ".h": "c"}
PERMISE = {"MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause"}
ARHIVA_MAX = 300 * 1024**2  # o arhivă mai mare nu se descarcă (pilotul nu are nevoie)
DESPACHETAT_MAX = 2 * 1024**3  # bombă de arhivă: ne oprim după atâția octeți citiți dintr-o arhivă
FISIER_MAX = 1024**2

DOSARE_COPIATE = {"vendor", "_vendor", "vendored", "third_party", "thirdparty", "third-party", "site-packages",
                  "node_modules"}
DOSARE_DATE_TEST = {"fixtures", "testdata", "test_data"}
SEMNE_GENERAT = ("generated by", "auto-generated", "autogenerated", "do not edit", "@generated", "code generated",
                 "this file was automatically")
NUME_GENERATE = (re.compile(r".*_pb2(_grpc)?\.pyi?$"), re.compile(r".*\.pb\.rs$"), re.compile(r"(^|/)migrations/0[^/]*\.py$"),
                 re.compile(r"(^|/)(parsetab|lextab)\.py$"), re.compile(r"(^|/)bindings\.rs$"))
SEMNE_GENERAT_SPECIAL = ("generated by cython", "generated by swig", "automatically generated by rust-bindgen")

# textele de licență care NU intră (în fișierele LICENSE și în antetele fișierelor de cod)
NEPERMISE_TEXT = {
    "GPL": re.compile(r"gnu (affero |lesser |library )?general public license", re.I),
    "MPL": re.compile(r"mozilla public license", re.I),
    "ISC": re.compile(r"permission to use, copy, modify, and(/or)? distribute this software for any purpose", re.I),
}

FILTRE = ["extensie", "copiat", "generat_nume", "prea_mare", "utf8", "generat_antet", "licenta_fisier", "rand_lung",
          "rand_mediu", "alfanumeric", "date_test", "sintaxa", "antet_bsd", "duplicat_exact"]


class OprireSpatiu(RuntimeError):
    """Spațiul liber pe disc a scăzut sub prag; pilotul se oprește (se reia cu aceeași comandă)."""


class OprireTimp(RuntimeError):
    """A trecut `--limita-ore`: oprire curată, cu rezumatul scris (se reia cu aceeași comandă)."""


class OprireRetea(RuntimeError):
    """Prea multe erori de rețea la rând: rețeaua pare căzută (se reia cu aceeași comandă)."""


# ---------------------------------------------------------------- rețeaua (politicoasă) -----------------------------------

class Ritm:
    """Cel mult `pe_secunda` cereri pe secundă pentru fiecare gazdă. Ceasul și somnul se pot înlocui (teste)."""

    def __init__(self, limite: dict[str, float], ceas: Callable[[], float] = time.monotonic,
                 doarme: Callable[[float], None] = time.sleep):
        self.limite, self.ceas, self.doarme = limite, ceas, doarme
        self.ultima: dict[str, float] = {}

    def asteapta(self, gazda: str) -> None:
        pas = 1.0 / self.limite.get(gazda, 1.0)
        acum = self.ceas()
        if gazda in self.ultima and acum - self.ultima[gazda] < pas:
            self.doarme(pas - (acum - self.ultima[gazda]))
            acum = self.ceas()
        self.ultima[gazda] = acum


class EroareRetea(RuntimeError):
    def __init__(self, url: str, cod: int | None, mesaj: str):
        super().__init__(f"{url}: {cod} {mesaj}")
        self.cod = cod
        # lipsește sau e prea mare: nu se rezolvă la o nouă încercare
        self.permanenta = cod in (403, 404, 410) or mesaj.startswith("prea mare")


class Retea:
    """Cereri HTTP GET cu User-Agent, ritm pe gazdă, limită de mărime și 3 încercări. Totul în memorie."""

    def __init__(self, ritm: Ritm | None = None, incercari: int = 3,
                 deschide: Callable | None = None):
        self.ritm = ritm or Ritm(RITM)
        self.incercari = incercari
        self.deschide = deschide or urllib.request.urlopen
        self.cereri = 0
        self.octeti = 0

    def ia(self, url: str, maxim: int = ARHIVA_MAX) -> bytes:
        gazda = url.split("/")[2]
        for incercare in range(self.incercari):
            self.ritm.asteapta(gazda)
            self.cereri += 1
            try:
                cerere = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
                with self.deschide(cerere, timeout=60) as r:
                    lungime = r.headers.get("Content-Length") if getattr(r, "headers", None) else None
                    if lungime and int(lungime) > maxim:
                        raise EroareRetea(url, None, f"prea mare ({lungime} octeți)")
                    date = r.read(maxim + 1)
                    if len(date) > maxim:
                        raise EroareRetea(url, None, "prea mare")
                    self.octeti += len(date)
                    return date
            except urllib.error.HTTPError as e:
                if e.code == 404 or e.code == 403 or e.code == 410:
                    raise EroareRetea(url, e.code, "lipsește") from None
                eroare = EroareRetea(url, e.code, str(e.reason))
                if e.code == 429:
                    self.ritm.doarme(30.0 * (incercare + 1))
            except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
                eroare = EroareRetea(url, None, str(e))
            self.ritm.doarme(2.0 ** incercare)
        raise eroare

    def json(self, url: str):
        return json.loads(self.ia(url, maxim=50 * 1024**2))


# ---------------------------------------------------------------- licențele -----------------------------------------------

def licente_din_spdx(expresie: str | None) -> set[str] | None:
    """Licențele permise alese dintr-o expresie SPDX (crates.io). None = expresia nu permite folosirea.

    `A OR B` (și vechiul `A/B`): ajunge o ramură permisă; `A AND B` / `A WITH x`: toate trebuie permise.
    """
    if not expresie or not expresie.strip():
        return None
    text = expresie.replace("/", " OR ").replace("(", " ").replace(")", " ")
    alese: set[str] = set()
    for ramura in re.split(r"\s+OR\s+", text.strip()):
        parti = [p.strip() for p in re.split(r"\s+AND\s+", ramura)]
        nume = set()
        for p in parti:
            p = p.split(" WITH ")[0].strip()
            p = {"Apache-2.0+": "Apache-2.0", "MIT/X11": "MIT"}.get(p, p)
            nume.add(p)
        if nume and nume <= PERMISE:
            alese |= nume
    return alese or None


CLASIFICATORI = {
    "License :: OSI Approved :: MIT License": "MIT",
    "License :: OSI Approved :: MIT No Attribution License (MIT-0)": None,
    "License :: OSI Approved :: Apache Software License": "Apache-2.0",
    "License :: OSI Approved :: BSD License": "BSD",
}
CAMP_LICENTA = {
    "mit": "MIT", "mit license": "MIT", "the mit license": "MIT", "expat": "MIT",
    "apache": "Apache-2.0", "apache 2": "Apache-2.0", "apache 2.0": "Apache-2.0", "apache-2.0": "Apache-2.0",
    "apache license 2.0": "Apache-2.0", "apache license, version 2.0": "Apache-2.0", "apache software license": "Apache-2.0",
    "apache license version 2.0": "Apache-2.0", "asl 2": "Apache-2.0", "asl 2.0": "Apache-2.0",
    "bsd": "BSD", "bsd license": "BSD", "new bsd": "BSD-3-Clause", "new bsd license": "BSD-3-Clause", "modified bsd": "BSD-3-Clause",
    "bsd-3-clause": "BSD-3-Clause", "3-clause bsd": "BSD-3-Clause", "bsd 3-clause": "BSD-3-Clause", "bsd-3": "BSD-3-Clause",
    "bsd-2-clause": "BSD-2-Clause", "2-clause bsd": "BSD-2-Clause", "simplified bsd": "BSD-2-Clause", "bsd 2-clause": "BSD-2-Clause",
}


def licente_pypi(info: dict) -> tuple[set[str] | None, str]:
    """Licențele din metadatele PyPI ale versiunii alese. Întoarce (familiile, motivul dacă nu)."""
    clasif = [c for c in info.get("classifiers") or [] if c.startswith("License ::") and c != "License :: OSI Approved"]
    if clasif:
        fam = {CLASIFICATORI.get(c) for c in clasif}
        if None in fam:
            return None, "metadate_nepermise"
        return fam, ""
    camp = (info.get("license") or "").strip()
    if not camp:
        return None, "metadate_lipsa"
    scurt = camp.lower().rstrip(".")
    if scurt in CAMP_LICENTA:
        return {CAMP_LICENTA[scurt]}, ""
    spdx = licente_din_spdx(camp) if len(camp) < 80 else None
    if spdx:
        return spdx, ""
    din_text = licente_din_text(camp)
    if din_text[0] and not din_text[1]:
        return din_text[0], ""
    return None, "metadate_nepermise"


def licente_din_text(text: str) -> tuple[set[str], set[str]]:
    """Ce licențe recunoaște în textul unui fișier LICENSE/COPYING: (permise, nepermise)."""
    t = " ".join(text.split()).lower()
    permise: set[str] = set()
    if "permission is hereby granted, free of charge" in t:
        permise.add("MIT")
    if "apache license" in t and ("version 2.0" in t or "licenses/license-2.0" in t):
        permise.add("Apache-2.0")
    if "redistribution and use in source and binary forms" in t:
        if re.search(r"neither the name|names of (its|the) contributors|name of the copyright holder", t):
            permise.add("BSD-3-Clause")
        else:
            permise.add("BSD-2-Clause")
    nepermise = {nume for nume, rx in NEPERMISE_TEXT.items() if rx.search(t)}
    return permise, nepermise


def se_potrivesc(metadate: set[str], fisiere: set[str]) -> bool:
    """Metadatele și fișierele LICENSE spun aceeași licență? „BSD” din clasificatori = BSD-2 sau BSD-3."""
    for m in metadate:
        if m == "BSD" and fisiere & {"BSD-2-Clause", "BSD-3-Clause"}:
            return True
        if m in fisiere:
            return True
    return False


def e_fisier_licenta(cale: str) -> bool:
    parti = PurePosixPath(cale).parts
    if len(parti) > 2:  # doar în rădăcina pachetului (primul dosar din arhivă)
        return False
    nume = parti[-1].upper()
    return nume.startswith(("LICENSE", "LICENCE", "COPYING"))


SPDX_ANTET = re.compile(r"SPDX-License-Identifier:\s*([^\n*]+)")


# variantele BSD-2 folosite de FreeBSD/NetBSD (același text, plus o propoziție de declinare); doar la `licenta_pe_fisier`
VARIANTE_BSD = {"BSD-2-Clause-FreeBSD": "BSD-2-Clause", "BSD-2-Clause-NetBSD": "BSD-2-Clause",
                "BSD-2-Clause-Views": "BSD-2-Clause"}
BSD = {"BSD-2-Clause", "BSD-3-Clause"}


def _spdx_din_antet(text: str, variante_bsd: bool = False) -> str | None:
    antet = "\n".join(text.split("\n", 40)[:40])
    m = SPDX_ANTET.search(antet)
    if not m:
        return None
    expr = m.group(1).strip().rstrip("*/ ").strip()
    if variante_bsd:
        for vechi, nou in VARIANTE_BSD.items():
            expr = expr.replace(vechi, nou)
    return expr


def licenta_fisier_ok(text: str, variante_bsd: bool = False) -> bool:
    """Antetul fișierului (primele 40 de rânduri): SPDX cu altă licență sau text GPL/MPL/ISC ⇒ fișierul se aruncă."""
    antet = "\n".join(text.split("\n", 40)[:40])
    expr = _spdx_din_antet(text, variante_bsd)
    if expr is not None and licente_din_spdx(expr) is None:
        return False
    return not any(rx.search(" ".join(antet.split())) for rx in NEPERMISE_TEXT.values())


def licenta_antet_bsd(text: str) -> str | None:
    """FreeBSD: licența fișierului din antetul SPDX, doar dacă e BSD-2/BSD-3 (cu variantele lor). Altfel None."""
    expr = _spdx_din_antet(text, variante_bsd=True)
    lic = licente_din_spdx(expr) if expr else None
    if not lic or not lic <= BSD:
        return None
    return " OR ".join(sorted(lic))


def reguli_depozit(d: dict) -> tuple[Callable[[str], bool] | None, Callable[[str], bool]]:
    """(pastreaza, e_licenta) din opțiunile `dosar`, `fara_dosare`, `fisiere_licenta` ale unui depozit.

    Fără opțiuni: (None, e_fisier_licenta), adică exact ca la pilot. Căile din arhivă încep cu dosarul de sus al ei.
    """
    if not any(d.get(k) for k in ("dosar", "fara_dosare", "fisiere_licenta")):
        return None, e_fisier_licenta
    dosar = PurePosixPath(d["dosar"]).parts if d.get("dosar") else ()
    fara = {x.lower() for x in d.get("fara_dosare") or ()}
    numai = {x.upper() for x in d.get("fisiere_licenta") or ()}

    def pastreaza(cale: str) -> bool:
        rel = PurePosixPath(cale).parts[1:]
        if rel[:len(dosar)] != dosar:
            return False
        return not ({p.lower() for p in rel[len(dosar):-1]} & fara)

    def e_licenta(cale: str) -> bool:
        rel = PurePosixPath(cale).parts[1:]
        if len(rel) != len(dosar) + 1 or rel[:len(dosar)] != dosar:
            return False
        nume = rel[-1].upper()
        return nume in numai if numai else nume.startswith(("LICENSE", "LICENCE", "COPYING"))

    return pastreaza, e_licenta


# ---------------------------------------------------------------- filtrele pe fișier --------------------------------------

def normalizeaza(text: str) -> str:
    randuri = [r.rstrip() for r in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    while randuri and not randuri[-1]:
        randuri.pop()
    return "\n".join(randuri) + "\n"


SIR = re.compile(r'"(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\\n])*\'')
NUMAR = re.compile(r"\b\d[\w.]*")


def parte_literali(text: str) -> float:
    plin = sum(1 for c in text if not c.isspace())
    if not plin:
        return 0.0
    lit = sum(len(m.group(0)) for m in SIR.finditer(text)) + sum(len(m.group(0)) for m in NUMAR.finditer(text))
    return lit / plin


def sintaxa_python(text: str) -> bool:
    import ast
    try:
        ast.parse(text)
        return True
    except (SyntaxError, ValueError, RecursionError, MemoryError, OverflowError):
        return False


_PERECHI = {")": "(", "]": "[", "}": "{"}
_C_CURAT = re.compile(r"/\*.*?\*/|//[^\n]*|\"(?:\\.|[^\"\\\n])*\"|'(?:\\.|[^'\\\n])+'", re.S)
_RUST_CURAT = re.compile(r"/\*.*?\*/|//[^\n]*|b?r(#*)\".*?\"\1|b?\"(?:\\.|[^\"\\])*\"|b?'(?:\\.[^']*|[^'\\\n])'", re.S)


def paranteze_echilibrate(text: str, limbaj: str) -> bool:
    """Verificarea simplă pentru Rust/C: fără comentarii, șiruri și caractere, parantezele se închid în ordine."""
    curat = (_RUST_CURAT if limbaj == "rust" else _C_CURAT).sub(" ", text)
    stiva: list[str] = []
    for c in curat:
        if c in "([{":
            stiva.append(c)
        elif c in _PERECHI:
            if not stiva or stiva.pop() != _PERECHI[c]:
                return False
    return not stiva


def filtreaza(cale: str, date: bytes | None, variante_bsd: bool = False) -> tuple[str | None, str | None]:
    """Aplică filtrele din SURSE.md pe un fișier. Întoarce (textul, None) dacă rămâne, altfel (None, filtrul).

    `date` = None înseamnă un fișier prea mare, necitit din arhivă. `variante_bsd` (doar FreeBSD): antetele SPDX
    `BSD-2-Clause-FreeBSD`/`-NetBSD` se citesc ca BSD-2-Clause.
    """
    p = PurePosixPath(cale)
    limbaj = EXTENSII.get(p.suffix.lower())
    if not limbaj:
        return None, "extensie"
    dosare = {d.lower() for d in p.parts[:-1]}
    if dosare & DOSARE_COPIATE:
        return None, "copiat"
    if any(rx.search(cale) for rx in NUME_GENERATE):
        return None, "generat_nume"
    if date is None or len(date) > FISIER_MAX:
        return None, "prea_mare"
    try:
        text = date.decode("utf-8")
    except UnicodeDecodeError:
        return None, "utf8"
    if "\x00" in text:
        return None, "utf8"
    antet = "\n".join(text.split("\n", 20)[:20]).lower()
    if any(s in antet for s in SEMNE_GENERAT) or any(s in antet for s in SEMNE_GENERAT_SPECIAL):
        return None, "generat_antet"
    if not licenta_fisier_ok(text, variante_bsd):
        return None, "licenta_fisier"
    randuri = text.split("\n")
    if max((len(r) for r in randuri), default=0) > 1000:
        return None, "rand_lung"
    if len(text) / max(1, len(randuri)) > 100:
        return None, "rand_mediu"
    plin = sum(1 for c in text if not c.isspace())
    if plin and sum(1 for c in text if c.isalnum()) / len(text) < 0.25:
        return None, "alfanumeric"
    if dosare & DOSARE_DATE_TEST and parte_literali(text) > 0.5:
        return None, "date_test"
    ok = sintaxa_python(text) if limbaj == "python" else paranteze_echilibrate(text, limbaj)
    if not ok:
        return None, "sintaxa"
    return text, None


# ---------------------------------------------------------------- arhivele, din memorie -----------------------------------

def fisiere_din_arhiva(date: bytes, nume: str, pastreaza: Callable[[str], bool] | None = None,
                       e_licenta: Callable[[str], bool] = e_fisier_licenta,
                       despachetat_max: int = DESPACHETAT_MAX) -> Iterator[tuple[str, bytes | None, float | None, int]]:
    """(calea, conținutul, data modificării, mărimea) pentru fișierele de cod și de licență din arhivă.

    Totul din memorie, nimic pe disc. Un fișier de cod mai mare de 1 MB nu se citește deloc (conținutul = None).
    `pastreaza` (opțiunile unui depozit) sare fișierele înainte să fie citite.
    """
    def de_citit(cale: str) -> bool:
        if pastreaza is not None and not pastreaza(cale):
            return False
        return PurePosixPath(cale).suffix.lower() in EXTENSII or e_licenta(cale)

    citit = 0
    if nume.endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(date)) as z:
            for info in z.infolist():
                if info.is_dir() or not de_citit(info.filename):
                    continue
                if info.file_size > FISIER_MAX:
                    yield info.filename, None, None, info.file_size
                    continue
                citit += info.file_size
                if citit > despachetat_max:
                    raise ValueError("arhivă prea mare la despachetare")
                yield info.filename, z.read(info), None, info.file_size
        return
    with tarfile.open(fileobj=io.BytesIO(date), mode="r:*") as t:
        for m in t:
            if not m.isfile() or not de_citit(m.name):
                continue
            if m.size > FISIER_MAX:
                yield m.name, None, float(m.mtime), m.size
                continue
            citit += m.size
            if citit > despachetat_max:
                raise ValueError("arhivă prea mare la despachetare")
            f = t.extractfile(m)
            if f is not None:
                yield m.name, f.read(), float(m.mtime), m.size


# ---------------------------------------------------------------- pilotul -------------------------------------------------

def spatiu_liber(cale: Path) -> int:
    ancora = cale
    while not ancora.exists():
        ancora = ancora.parent
    return shutil.disk_usage(ancora).free


def _data(text: str) -> datetime:
    d = datetime.fromisoformat(text.replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def _prerelease(versiune: str) -> bool:
    from packaging.version import InvalidVersion, Version
    try:
        return Version(versiune).is_prerelease
    except InvalidVersion:
        return True


def _data_dump(text: str) -> datetime:
    """Data din dump-ul crates.io („2021-06-01 12:34:56.123456+00”, mereu UTC)."""
    return datetime.strptime(text.strip()[:19].replace("T", " "), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)


def citeste_dump_crates(date: bytes, data_limita: datetime = DATA_LIMITA) -> dict:
    """Din `db-dump.tar.gz` (în memorie): pentru fiecare crate, ultima versiune nescoasă (nu yanked), nu pre-lansare,
    publicată înainte de data-limită, cu licența ei SPDX și mărimea. Cele mai descărcate întâi.

    Citește doar `crates.csv`, `versions.csv` și (în dump-urile noi) `crate_downloads.csv`; restul se sare.
    """
    csv.field_size_limit(2**31 - 1)
    nume: dict[str, str] = {}
    descarcari: Counter = Counter()
    descarcari_versiuni: Counter = Counter()
    alese: dict[str, dict] = {}
    with tarfile.open(fileobj=io.BytesIO(date), mode="r:*") as t:
        for m in t:
            baza = PurePosixPath(m.name).name
            if not m.isfile() or baza not in ("crates.csv", "versions.csv", "crate_downloads.csv"):
                continue
            text = io.TextIOWrapper(t.extractfile(m), encoding="utf-8", newline="")
            for r in csv.DictReader(text):
                if baza == "crates.csv":
                    nume[r["id"]] = r["name"]
                    if r.get("downloads"):
                        descarcari[r["id"]] = int(r["downloads"])
                elif baza == "crate_downloads.csv":
                    descarcari[r["crate_id"]] = int(r["downloads"])
                else:
                    cid = r["crate_id"]
                    if r.get("downloads"):
                        descarcari_versiuni[cid] += int(r["downloads"])
                    if (r.get("yanked") or "f").strip().lower() in ("t", "true"):
                        continue
                    creat = _data_dump(r["created_at"])
                    if creat >= data_limita or _prerelease(r["num"]):
                        continue
                    vechi = alese.get(cid)
                    if vechi is None or creat > vechi["creat"]:
                        alese[cid] = {"num": r["num"], "license": r.get("license") or "",
                                      "crate_size": int(r.get("crate_size") or 0), "creat": creat}
    if not descarcari:
        descarcari = descarcari_versiuni
    lista = [{"nume": nume[cid], "num": v["num"], "license": v["license"], "crate_size": v["crate_size"],
              "creat": v["creat"].isoformat(), "descarcari": descarcari.get(cid, 0)}
             for cid, v in alese.items() if cid in nume]
    lista.sort(key=lambda e: (-e["descarcari"], e["nume"]))
    return {"total_crates": len(nume), "fara_versiune_inainte_de_data": len(nume) - len(lista), "crates": lista}


class Pilot:
    """Descărcarea în flux, cu reluare. `retea`, `spatiu` și `ceas` se pot înlocui (testele nu ating rețeaua).

    Numele a rămas de la pilot; aceeași clasă face și descărcarea întreagă (`ruleaza_complet`).
    """

    def __init__(self, iesire: Path, retea: Retea | None = None, spatiu: Callable[[Path], int] = spatiu_liber,
                 data_limita: datetime = DATA_LIMITA, spatiu_minim: int = SPATIU_MINIM, scrie: Callable[[str], None] = print,
                 ceas: Callable[[], float] = time.monotonic):
        self.iesire = Path(iesire)
        self.retea = retea or Retea()
        self.spatiu, self.data_limita, self.spatiu_minim, self.scrie = spatiu, data_limita, spatiu_minim, scrie
        self.ceas = ceas
        self.termen: float | None = None  # --limita-ore, doar la `complet`
        self.limita_ore: float | None = None
        self.complet = False  # la `complet`: erorile trecătoare nu închid pachetul, iar o eroare neașteptată nu oprește tot
        self.erori_la_rand = 0
        self.amanate = 0  # pachete lăsate pentru reluare (erori de rețea trecătoare) în rularea asta
        self.iesire.mkdir(parents=True, exist_ok=True)
        self.f_cod = self.iesire / "cod.jsonl"
        self.f_pachete = self.iesire / "pachete.jsonl"
        self.gata: set[str] = set()
        self.hashuri: set[str] = set()
        self._reia()

    # -- reluarea: ce s-a încheiat rămâne; ce era pe jumătate se taie din cod.jsonl
    def _reia(self) -> None:
        pozitie = 0
        if self.f_pachete.exists():
            for rand in self.f_pachete.read_text(encoding="utf-8").splitlines():
                if not rand.strip():
                    continue
                try:
                    r = json.loads(rand)
                except json.JSONDecodeError:
                    break
                self.gata.add(r["cheie"])
                pozitie = r["pozitie_cod"]
        if self.f_cod.exists():
            if self.f_cod.stat().st_size > pozitie:
                with open(self.f_cod, "r+b") as f:
                    f.truncate(pozitie)
            with open(self.f_cod, encoding="utf-8") as f:
                for rand in f:
                    self.hashuri.add(json.loads(rand)["sha256"])

    def _verifica_spatiul(self) -> None:
        liber = self.spatiu(self.iesire)
        if liber < self.spatiu_minim:
            raise OprireSpatiu(f"spațiul liber {liber / 1024**3:.1f} GB < {self.spatiu_minim / 1024**3:.0f} GB: mă opresc")

    def _verifica_timpul(self) -> None:
        if self.termen is not None and self.ceas() >= self.termen:
            raise OprireTimp(f"au trecut cele {self.limita_ore:g} ore (--limita-ore): mă opresc curat; aceeași comandă reia")

    def _incheie(self, rezultat: dict) -> None:
        rezultat["pozitie_cod"] = self.f_cod.stat().st_size if self.f_cod.exists() else 0
        with open(self.f_pachete, "a", encoding="utf-8") as f:
            f.write(json.dumps(rezultat, ensure_ascii=False) + "\n")
        self.gata.add(rezultat["cheie"])

    # -- un pachet: licența, apoi fiecare fișier prin filtre
    def proceseaza(self, sursa: str, nume: str, versiune: str, metadate: set[str] | None, date: bytes,
                   nume_arhiva: str, verifica_data_fisiere: bool = False, pastreaza: Callable[[str], bool] | None = None,
                   e_licenta: Callable[[str], bool] = e_fisier_licenta, licenta_pe_fisier: bool = False,
                   despachetat_max: int = DESPACHETAT_MAX) -> dict:
        """`licenta_pe_fisier` (FreeBSD): fără fișierul LICENSE al pachetului; fiecare fișier intră doar cu antet SPDX BSD."""
        rez = {"cheie": f"{sursa}:{nume}", "sursa": sursa, "pachet": nume, "versiune": versiune,
               "octeti_arhiva": len(date), "octeti_cod_brut": 0, "fisiere_cod_brut": 0,
               "pastrate": 0, "octeti_pastrati": 0, "aruncate": {}, "aruncate_octeti": {}}
        lic_permise: set[str] = set()
        lic_nepermise: set[str] = set()
        are_licenta = False
        candidati = []
        data_maxima = 0.0
        try:
            for cale, continut, mtime, marime in fisiere_din_arhiva(date, nume_arhiva, pastreaza, e_licenta, despachetat_max):
                if mtime:
                    data_maxima = max(data_maxima, mtime)
                if e_licenta(cale) and continut is not None:
                    are_licenta = True
                    p, n = licente_din_text(continut.decode("utf-8", "replace"))
                    lic_permise |= p
                    lic_nepermise |= n
                if PurePosixPath(cale).suffix.lower() in EXTENSII:
                    candidati.append((cale, continut, marime))
        except (tarfile.TarError, zipfile.BadZipFile, ValueError, EOFError, OSError) as e:
            rez.update(stare="respins", motiv="arhiva_stricata", detaliu=str(e)[:200])
            return rez
        if verifica_data_fisiere and data_maxima and datetime.fromtimestamp(data_maxima, timezone.utc) >= self.data_limita:
            rez.update(stare="respins", motiv="dupa_data_limita")
            return rez
        rez["licente_fisiere"] = sorted(lic_permise | lic_nepermise)
        if metadate is None:
            rez.update(stare="respins", motiv="metadate_nepermise")
            return rez
        if not licenta_pe_fisier:
            if not are_licenta:
                rez.update(stare="respins", motiv="fara_fisier_licenta")
                return rez
            if lic_nepermise:
                rez.update(stare="respins", motiv="fisier_licenta_nepermisa")
                return rez
            if not se_potrivesc(metadate, lic_permise):
                rez.update(stare="respins", motiv="licente_nepotrivite")
                return rez
        licenta = " OR ".join(sorted(metadate))
        aruncate, aruncate_oct = Counter(), Counter()
        randuri = []
        for cale, continut, marime in candidati:
            rez["fisiere_cod_brut"] += 1
            rez["octeti_cod_brut"] += marime
            text, filtru = filtreaza(cale, continut, variante_bsd=licenta_pe_fisier)
            lic_fisier = licenta
            if text is not None and licenta_pe_fisier:
                lic_fisier = licenta_antet_bsd(text)
                if lic_fisier is None:
                    text, filtru = None, "antet_bsd"
            if text is not None:
                sha = hashlib.sha256(normalizeaza(text).encode("utf-8")).hexdigest()
                if sha in self.hashuri:
                    text, filtru = None, "duplicat_exact"
            if text is None:
                aruncate[filtru] += 1
                aruncate_oct[filtru] += marime
                continue
            self.hashuri.add(sha)
            randuri.append(json.dumps({"sursa": sursa, "pachet": nume, "versiune": versiune, "cale": cale,
                                       "limbaj": EXTENSII[PurePosixPath(cale).suffix.lower()], "licenta": lic_fisier,
                                       "sha256": sha, "text": text}, ensure_ascii=False))
            rez["pastrate"] += 1
            rez["octeti_pastrati"] += len(text.encode("utf-8"))
        if randuri:
            with open(self.f_cod, "a", encoding="utf-8", newline="\n") as f:
                f.write("\n".join(randuri) + "\n")
        rez.update(stare="pastrat", licenta=licenta, aruncate=dict(aruncate), aruncate_octeti=dict(aruncate_oct))
        return rez

    def _ruleaza_pachet(self, cheie: str, functie: Callable[[], dict]) -> None:
        if cheie in self.gata:
            return
        self._verifica_timpul()
        self._verifica_spatiul()
        sursa, nume = cheie.split(":", 1)
        try:
            rez = functie()
        except EroareRetea as e:
            if self.complet and not e.permanenta:
                # trecătoare: pachetul nu se închide, se reîncearcă la reluare; multe la rând = rețeaua e căzută
                self.erori_la_rand += 1
                self.amanate += 1
                self.scrie(f"{cheie}: eroare de rețea, rămâne pentru reluare ({str(e)[:150]})")
                if self.erori_la_rand >= ERORI_RETEA_LA_RAND:
                    raise OprireRetea(f"{self.erori_la_rand} erori de rețea la rând: mă opresc; aceeași comandă reia") from None
                return
            rez = {"cheie": cheie, "sursa": sursa, "pachet": nume, "stare": "respins", "motiv": "retea",
                   "detaliu": str(e)[:200]}
        except Exception as e:  # noqa: BLE001 — la `complet` o arhivă ciudată nu oprește 2–3 nopți de descărcare
            if not self.complet:
                raise
            rez = {"cheie": cheie, "sursa": sursa, "pachet": nume, "stare": "respins", "motiv": "eroare",
                   "detaliu": f"{type(e).__name__}: {e}"[:200]}
        self.erori_la_rand = 0
        rez["cheie"] = cheie
        self._incheie(rez)
        self.scrie(f"{cheie}: {rez['stare']}" + (f" ({rez.get('motiv')})" if rez["stare"] != "pastrat" else
                                                 f", {rez['pastrate']} fișiere"))

    # -- sursele
    def depozit(self, d: dict) -> dict:
        url = f"https://codeload.github.com/{d['depozit']}/tar.gz/refs/tags/{d['tag']}"
        date = self.retea.ia(url, maxim=d.get("arhiva_max", ARHIVA_MAX))
        pastreaza, e_licenta = reguli_depozit(d)
        return self.proceseaza(d.get("sursa", "git"), d["nume"], d["tag"], licente_din_spdx(d["licenta"]), date, url,
                               verifica_data_fisiere=True, pastreaza=pastreaza, e_licenta=e_licenta,
                               licenta_pe_fisier=d.get("licenta_pe_fisier", False),
                               despachetat_max=d.get("despachetat_max", DESPACHETAT_MAX))

    def alege_pypi(self, date_json: dict) -> tuple[str, dict] | None:
        """Ultima versiune (nu pre-lansare) cu sdist publicat înainte de data-limită."""
        alese = []
        for versiune, fisiere in (date_json.get("releases") or {}).items():
            if _prerelease(versiune):
                continue
            for f in fisiere:
                if f.get("packagetype") != "sdist" or f.get("yanked"):
                    continue
                cand = _data(f.get("upload_time_iso_8601") or f["upload_time"])
                if cand < self.data_limita:
                    alese.append((cand, versiune, f))
        if not alese:
            return None
        alese.sort(key=lambda x: x[0])
        _, versiune, f = alese[-1]
        return versiune, f

    def pypi(self, nume: str) -> dict:
        tot = self.retea.json(f"https://pypi.org/pypi/{nume}/json")
        ales = self.alege_pypi(tot)
        if ales is None:
            return {"sursa": "pypi", "pachet": nume, "stare": "respins", "motiv": "fara_versiune_inainte_de_data"}
        versiune, fisier = ales
        info = self.retea.json(f"https://pypi.org/pypi/{nume}/{versiune}/json").get("info") or {}
        metadate, motiv = licente_pypi(info)
        if metadate is None:
            return {"sursa": "pypi", "pachet": nume, "versiune": versiune, "stare": "respins", "motiv": motiv}
        if fisier.get("size", 0) > ARHIVA_MAX:
            return {"sursa": "pypi", "pachet": nume, "versiune": versiune, "stare": "respins", "motiv": "arhiva_prea_mare"}
        date = self.retea.ia(fisier["url"])
        return self.proceseaza("pypi", nume, versiune, metadate, date, fisier["filename"])

    def alege_crate(self, versiuni: list[dict]) -> dict | None:
        bune = [v for v in versiuni if not v.get("yanked") and not _prerelease(v["num"])
                and _data(v["created_at"]) < self.data_limita]
        if not bune:
            return None
        return max(bune, key=lambda v: _data(v["created_at"]))

    def crate(self, nume: str) -> dict:
        versiuni = self.retea.json(f"https://crates.io/api/v1/crates/{nume}/versions").get("versions") or []
        v = self.alege_crate(versiuni)
        if v is None:
            return {"sursa": "crates", "pachet": nume, "stare": "respins", "motiv": "fara_versiune_inainte_de_data"}
        return self._crate_versiune(nume, v)

    def crate_din_dump(self, e: dict) -> dict:
        """Un crate din lista scoasă din dump: versiunea e deja aleasă, rămâne o singură cerere (arhiva)."""
        return self._crate_versiune(e["nume"], {"num": e["num"], "license": e["license"], "crate_size": e["crate_size"]})

    def _crate_versiune(self, nume: str, v: dict) -> dict:
        metadate = licente_din_spdx(v.get("license"))
        if metadate is None:
            return {"sursa": "crates", "pachet": nume, "versiune": v["num"], "stare": "respins",
                    "motiv": "metadate_nepermise", "detaliu": v.get("license")}
        if (v.get("crate_size") or 0) > ARHIVA_MAX:
            return {"sursa": "crates", "pachet": nume, "versiune": v["num"], "stare": "respins", "motiv": "arhiva_prea_mare"}
        date = self.retea.ia(f"https://static.crates.io/crates/{nume}/{nume}-{v['num']}.crate")
        return self.proceseaza("crates", nume, v["num"], metadate, date, f"{nume}-{v['num']}.crate")

    def lista_pypi(self, n: int) -> list[str]:
        f = self.iesire / "lista_pypi.json"
        if not f.exists():
            date = self.retea.json(LISTA_PYPI)
            f.write_text(json.dumps([r["project"] for r in date["rows"]][:n]), encoding="utf-8")
        return json.loads(f.read_text(encoding="utf-8"))[:n]

    def lista_crates(self, n: int) -> list[str]:
        f = self.iesire / "lista_crates.json"
        if not f.exists():
            nume: list[str] = []
            pagina = 1
            while len(nume) < n:
                date = self.retea.json(f"https://crates.io/api/v1/crates?sort=downloads&per_page=100&page={pagina}")
                bucata = [c["id"] for c in date.get("crates") or []]
                if not bucata:
                    break
                nume += bucata
                pagina += 1
            f.write_text(json.dumps(nume[:n]), encoding="utf-8")
        return json.loads(f.read_text(encoding="utf-8"))[:n]

    def ruleaza(self, depozite: Iterable[dict] = DEPOZITE_PILOT, n_pypi: int = PILOT_PYPI, n_crates: int = PILOT_CRATES) -> dict:
        """Ordinea din SURSE.md (contează la duplicate): depozitele mari, apoi PyPI, apoi crates."""
        inceput = time.time()
        try:
            for d in depozite:
                self._ruleaza_pachet(f"git:{d['nume']}", lambda d=d: self.depozit(d))
            for nume in self.lista_pypi(n_pypi):
                self._ruleaza_pachet(f"pypi:{nume}", lambda nume=nume: self.pypi(nume))
            for nume in self.lista_crates(n_crates):
                self._ruleaza_pachet(f"crates:{nume}", lambda nume=nume: self.crate(nume))
        except OprireSpatiu as e:
            self.scrie(str(e))
            rez = rezumat(self.iesire, aproape=False)
            rez["oprit"] = str(e)
            (self.iesire / "rezumat.json").write_text(json.dumps(rez, ensure_ascii=False, indent=1), encoding="utf-8")
            return rez
        rez = rezumat(self.iesire, aproape=True)
        rez["secunde_rularea_asta"] = round(time.time() - inceput)
        rez["cereri_rularea_asta"] = self.retea.cereri
        rez["octeti_descarcati_rularea_asta"] = self.retea.octeti
        (self.iesire / "rezumat.json").write_text(json.dumps(rez, ensure_ascii=False, indent=1), encoding="utf-8")
        return rez

    # -- descărcarea întreagă
    def lista_crates_dump(self, n: int | None = None) -> list[dict]:
        """Lista crate-urilor din dump-ul public (o singură cerere, o dată; apoi din `lista_crates_dump.json`)."""
        f = self.iesire / "lista_crates_dump.json"
        if not f.exists():
            info = citeste_dump_crates(self.retea.ia(DUMP_CRATES, maxim=DUMP_MAX), self.data_limita)
            f.write_text(json.dumps(info, ensure_ascii=False), encoding="utf-8")
        lista = json.loads(f.read_text(encoding="utf-8"))["crates"]
        return lista[:n] if n is not None else lista

    def _info_liste(self) -> dict:
        info = {}
        f_p = self.iesire / "lista_pypi.json"
        if f_p.exists():
            info["pypi_in_lista"] = len(json.loads(f_p.read_text(encoding="utf-8")))
        f_c = self.iesire / "lista_crates_dump.json"
        if f_c.exists():
            c = json.loads(f_c.read_text(encoding="utf-8"))
            info["crates_din_dump"] = {"total": c["total_crates"], "cu_versiune_inainte_de_data": len(c["crates"]),
                                       "fara_versiune_inainte_de_data": c["fara_versiune_inainte_de_data"]}
        return info

    def ruleaza_complet(self, depozite: Iterable[dict] = DEPOZITE_COMPLET, n_pypi: int = COMPLET_PYPI,
                        n_crates: int | None = None, limita_ore: float | None = None) -> dict:
        """Toate sursele, în ordinea din SURSE.md: depozitele (rândurile 3–6), PyPI, crates. Duplicatele exacte se scot
        peste toate sursele (și peste reluări); aproape-duplicatele, o singură dată, când s-a terminat tot."""
        inceput = time.time()
        self.complet = True
        self.limita_ore = limita_ore
        self.termen = self.ceas() + limita_ore * 3600 if limita_ore else None
        try:
            for d in depozite:
                self._ruleaza_pachet(f"{d.get('sursa', 'git')}:{d['nume']}", lambda d=d: self.depozit(d))
            self._verifica_timpul()
            self._verifica_spatiul()
            for nume in self.lista_pypi(n_pypi) if n_pypi else []:
                self._ruleaza_pachet(f"pypi:{nume}", lambda nume=nume: self.pypi(nume))
            self._verifica_timpul()
            self._verifica_spatiul()
            for e in self.lista_crates_dump(n_crates) if n_crates != 0 else []:
                self._ruleaza_pachet(f"crates:{e['nume']}", lambda e=e: self.crate_din_dump(e))
            oprit = None
            if self.amanate:
                oprit = f"{self.amanate} pachete amânate după erori de rețea: nu e gata; aceeași comandă le reia"
        except (OprireSpatiu, OprireTimp, OprireRetea, EroareRetea) as e:
            oprit = str(e) if not isinstance(e, EroareRetea) else f"lista nu s-a putut lua: {e}; aceeași comandă reia"
        if oprit:
            self.scrie(oprit)
        rez = rezumat(self.iesire, aproape=oprit is None)
        if oprit:
            rez["oprit"] = oprit
        rez["terminat"] = oprit is None
        rez.update(self._info_liste())
        rez["secunde_rularea_asta"] = round(time.time() - inceput)
        rez["cereri_rularea_asta"] = self.retea.cereri
        rez["octeti_descarcati_rularea_asta"] = self.retea.octeti
        (self.iesire / "rezumat.json").write_text(json.dumps(rez, ensure_ascii=False, indent=1), encoding="utf-8")
        return rez


# ---------------------------------------------------------------- aproape-duplicatele (MinHash) ----------------------------

PRIM = (1 << 31) - 1
SIMBOL = re.compile(r"\w+|[^\w\s]")


def semnatura(text: str, a, b):
    import numpy as np
    simb = SIMBOL.findall(text)
    if len(simb) < 5:
        grame = [" ".join(simb)]
    else:
        grame = {" ".join(simb[i:i + 5]) for i in range(len(simb) - 4)}
    h = np.fromiter((int.from_bytes(hashlib.blake2b(g.encode("utf-8"), digest_size=4).digest(), "little") % PRIM
                     for g in grame), dtype=np.int64)
    return ((np.outer(h, a) + b) % PRIM).min(axis=0)


def aproape_duplicate(texte: Iterable[str], prag: float = 0.85, benzi: int = 16, randuri: int = 8, samanta: int = 0) -> list[int]:
    """Indicii de scos: în fiecare grup cu Jaccard estimat ≥ prag rămâne cel mai lung text.

    `texte` se parcurge o singură dată (poate fi un generator peste cod.jsonl): în memorie rămân doar semnăturile.
    """
    import numpy as np
    rng = np.random.default_rng(samanta)
    n_perm = benzi * randuri
    a = rng.integers(1, PRIM, n_perm, dtype=np.int64)
    b = rng.integers(0, PRIM, n_perm, dtype=np.int64)
    sem, lungimi = [], []
    for t in texte:
        sem.append(semnatura(t, a, b))
        lungimi.append(len(t))
    parinte = list(range(len(sem)))

    def radacina(i: int) -> int:
        while parinte[i] != i:
            parinte[i] = parinte[parinte[i]]
            i = parinte[i]
        return i

    for banda in range(benzi):
        galeti: dict[bytes, list[int]] = {}
        for i, s in enumerate(sem):
            galeti.setdefault(s[banda * randuri:(banda + 1) * randuri].tobytes(), []).append(i)
        for membri in galeti.values():
            for j in membri[1:]:
                i = membri[0]
                if radacina(i) != radacina(j) and float(np.mean(sem[i] == sem[j])) >= prag:
                    parinte[radacina(j)] = radacina(i)
    grupuri: dict[int, list[int]] = {}
    for i in range(len(sem)):
        grupuri.setdefault(radacina(i), []).append(i)
    scoase = []
    for membri in grupuri.values():
        if len(membri) > 1:
            pastrat = max(membri, key=lambda i: (lungimi[i], -i))
            scoase += [i for i in membri if i != pastrat]
    return sorted(scoase)


# ---------------------------------------------------------------- rezumatul -----------------------------------------------

def _randuri_cod(f_cod: Path) -> Iterator[dict]:
    with open(f_cod, encoding="utf-8") as f:
        for rand in f:
            if rand.strip():
                yield json.loads(rand)


def rezumat(iesire: Path, aproape: bool = True) -> dict:
    iesire = Path(iesire)
    pachete = []
    f_p = iesire / "pachete.jsonl"
    if f_p.exists():
        pachete = [json.loads(r) for r in f_p.read_text(encoding="utf-8").splitlines() if r.strip()]
    pe_sursa: dict[str, dict] = {}
    aruncate, aruncate_oct, motive = Counter(), Counter(), Counter()
    for p in pachete:
        s = pe_sursa.setdefault(p["sursa"], {"pachete": 0, "pastrate": 0, "respinse": 0, "octeti_arhive": 0,
                                             "octeti_cod_brut": 0, "fisiere_cod_brut": 0, "octeti_curat": 0,
                                             "fisiere_curat": 0, "respinse_motive": Counter()})
        s["pachete"] += 1
        s["octeti_arhive"] += p.get("octeti_arhiva", 0)
        if p["stare"] == "pastrat":
            s["pastrate"] += 1
            s["octeti_cod_brut"] += p["octeti_cod_brut"]
            s["fisiere_cod_brut"] += p["fisiere_cod_brut"]
            s["octeti_curat"] += p["octeti_pastrati"]
            s["fisiere_curat"] += p["pastrate"]
            aruncate.update(p.get("aruncate", {}))
            aruncate_oct.update(p.get("aruncate_octeti", {}))
        else:
            s["respinse"] += 1
            s["respinse_motive"][p["motiv"]] += 1
            motive[p["motiv"]] += 1
    scoase_aproape, oct_aproape = [], 0
    f_cod = iesire / "cod.jsonl"
    if aproape and f_cod.exists():
        scoase_aproape = aproape_duplicate(r["text"] for r in _randuri_cod(f_cod))
        (iesire / "aproape_duplicate.json").write_text(json.dumps(scoase_aproape), encoding="utf-8")
        de_scos = set(scoase_aproape)
        if de_scos:
            for i, r in enumerate(_randuri_cod(f_cod)):
                if i in de_scos:
                    marime = len(r["text"].encode("utf-8"))
                    oct_aproape += marime
                    s = pe_sursa[r["sursa"]]
                    s["octeti_curat"] -= marime
                    s["fisiere_curat"] -= 1
        aruncate["aproape_duplicat"] = len(scoase_aproape)
        aruncate_oct["aproape_duplicat"] = oct_aproape
    brut = sum(s["octeti_cod_brut"] for s in pe_sursa.values())
    curat = sum(s["octeti_curat"] for s in pe_sursa.values())
    fis_brut = sum(s["fisiere_cod_brut"] for s in pe_sursa.values())
    for s in pe_sursa.values():
        s["respinse_motive"] = dict(s["respinse_motive"])
        s["simboluri_estimate"] = round(s["octeti_curat"] / OCTETI_PE_SIMBOL)
    return {
        "data_limita": DATA_LIMITA.isoformat(),
        "pachete": len(pachete),
        "gb_arhive_descarcate": round(sum(s["octeti_arhive"] for s in pe_sursa.values()) / 1e9, 4),
        "gb_cod_brut": round(brut / 1e9, 4),
        "gb_curat": round(curat / 1e9, 4),
        "fisiere_cod_brut": fis_brut,
        "fisiere_curat": sum(s["fisiere_curat"] for s in pe_sursa.values()),
        "simboluri_estimate": round(curat / OCTETI_PE_SIMBOL),
        "octeti_pe_simbol_presupusi": OCTETI_PE_SIMBOL,
        "aruncate_fisiere": dict(aruncate),
        "aruncate_procent_din_brut": {k: round(100 * v / max(1, brut), 2) for k, v in aruncate_oct.items()},
        "pachete_respinse": dict(motive),
        "pe_sursa": pe_sursa,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="comanda", required=True)
    p = sub.add_parser("pilot", help="pilotul: 500 PyPI + 500 crates + numpy, tokio, libuv (folosește rețeaua)")
    p.add_argument("--iesire", type=Path, default=IESIRE_PILOT)
    p.add_argument("--pypi", type=int, default=PILOT_PYPI)
    p.add_argument("--crates", type=int, default=PILOT_CRATES)
    c = sub.add_parser("complet", help="descărcarea întreagă: toate cele 6 surse din SURSE.md (folosește rețeaua; cere „da”)")
    c.add_argument("--iesire", type=Path, default=IESIRE_COMPLET)
    c.add_argument("--pypi", type=int, default=COMPLET_PYPI, help="câte pachete din lista PyPI (implicit 30.000)")
    c.add_argument("--crates", type=int, default=None, help="câte crate-uri din dump (implicit toate)")
    c.add_argument("--limita-ore", type=float, default=None, help="oprire curată după N ore; aceeași comandă reia")
    r = sub.add_parser("rezumat", help="refă rezumatul din ce e deja pe disc (fără rețea)")
    r.add_argument("--iesire", type=Path, default=IESIRE_PILOT)
    a = ap.parse_args(argv)
    if a.comanda == "pilot":
        rez = Pilot(a.iesire).ruleaza(n_pypi=a.pypi, n_crates=a.crates)
    elif a.comanda == "complet":
        rez = Pilot(a.iesire).ruleaza_complet(n_pypi=a.pypi, n_crates=a.crates, limita_ore=a.limita_ore)
    else:
        rez = rezumat(a.iesire)
        (a.iesire / "rezumat.json").write_text(json.dumps(rez, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in rez.items() if k != "pe_sursa"}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
