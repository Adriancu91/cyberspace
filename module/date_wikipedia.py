"""Date Simple English Wikipedia (Etapa M3, testul în trei trepte: textul R3, mai greu și mai mare).

Sursa: wikimedia/wikipedia, ediția 20231101.simple, pe Hugging Face; licență CC BY-SA 4.0 și GFDL (liberă).
De ce acest text: e mai greu decât TinyStories (fapte, nume, cifre, cuvinte rare, propoziții mai lungi), dar tot în
engleză simplă, deci memoria (WordNet) și tokenizerul rămân folositoare; și e mai mare decât setul R2.

La prima folosire descarcă fișierul oficial (~157 MB, parquet) și pregătește în dosarul dat antrenare.txt și
validare.txt: articolele se împart după numărul lor (id), la întâmplare dar mereu la fel; cam 1 din 100 merge la
validare (din care se păstrează primii megaocteti_validare MB), restul la antrenare, deci examenul e pe articole pe care
modelul nu le-a văzut. Articolele sunt despărțite de un rând „<|endoftext|>”, ca poveștile din TinyStories.
Pregătirea cere pachetul pyarrow (pip install pyarrow); după aceea modulul doar citește fișierele.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import urllib.request
from pathlib import Path
from typing import Any

URL = "https://huggingface.co/datasets/wikimedia/wikipedia/resolve/main/20231101.simple/train-00000-of-00001.parquet"
SEPARATOR = "<|endoftext|>"
VERSIUNE_PREGATIRE = 1
LA_VALIDARE = 100  # 1 articol din 100


def _descarca(url: str, destinatie: Path) -> None:
    if destinatie.exists():
        return
    destinatie.parent.mkdir(parents=True, exist_ok=True)
    temporar = destinatie.with_name(destinatie.name + ".part")
    cerere = urllib.request.Request(url, headers={"User-Agent": "cyberspace"})
    try:
        with urllib.request.urlopen(cerere, timeout=300) as raspuns, open(temporar, "wb") as f:
            shutil.copyfileobj(raspuns, f, 1 << 24)
    except OSError as e:
        raise ValueError(f"Nu am putut descărca Wikipedia de la {url}: {e}. Verifică internetul.") from e
    temporar.replace(destinatie)


def _la_validare(id_articol: str) -> bool:
    return int(hashlib.md5(id_articol.encode("utf-8")).hexdigest(), 16) % LA_VALIDARE == 0


def _scrie(cale: Path, articole: list[str]) -> int:
    text = f"\n{SEPARATOR}\n".join(articole) + "\n"
    temporar = cale.with_name(cale.name + ".part")
    temporar.write_text(text, encoding="utf-8")
    temporar.replace(cale)
    return len(text.encode("utf-8"))


def pregateste(director: Path, cerute: dict[str, Any]) -> dict[str, Any]:
    """Descarcă fișierul oficial și scrie antrenare.txt, validare.txt și info.json."""
    try:
        import pyarrow.parquet as pq
    except ImportError as e:
        raise ValueError("Pregătirea Wikipedia cere pachetul pyarrow: python -m pip install pyarrow") from e
    print("Pregătesc Simple English Wikipedia...", flush=True)
    sursa = director / "sursa.parquet"
    _descarca(cerute["url"], sursa)
    tabel = pq.read_table(sursa, columns=["id", "text"])
    antrenare: list[str] = []
    validare: list[str] = []
    for id_articol, text in zip(tabel.column("id").to_pylist(), tabel.column("text").to_pylist()):
        text = (text or "").strip()
        if text:
            (validare if _la_validare(str(id_articol)) else antrenare).append(text)
    limita = cerute["megaocteti_validare"] * 1_000_000
    pastrate, octeti = [], 0
    for articol in validare:  # primii megaocteti_validare MB din articolele de validare
        if octeti >= limita:
            break
        pastrate.append(articol)
        octeti += len(articol.encode("utf-8"))
    if not antrenare or not pastrate:
        raise ValueError("Fișierul Wikipedia nu are destule articole.")
    info = {
        **cerute,
        "sursa": "wikimedia/wikipedia 20231101.simple (Hugging Face), licență CC BY-SA 4.0 și GFDL",
        "articole_antrenare": len(antrenare),
        "articole_validare": len(pastrate),
        "octeti_antrenare": _scrie(director / "antrenare.txt", antrenare),
        "octeti_validare": _scrie(director / "validare.txt", pastrate),
    }
    (director / "info.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Gata: {info['articole_antrenare']:,} articole de antrenare ({info['octeti_antrenare'] / 1e6:.1f} MB), "
          f"{info['articole_validare']:,} de validare ({info['octeti_validare'] / 1e6:.1f} MB)", flush=True)
    return info


class DateWikipedia:
    MANIFEST = {
        "nume": "date_wikipedia",
        "port": "date",
        "versiune": "0.1.0",
        "versiune_contract": 1,
        "resurse": {"disc_mb": 600},
        "permisiuni": ["internet", "citire_fisier", "scriere_fisier"],
    }

    def __init__(self, director: str = "date/wikipedia_simpla", url: str = URL, megaocteti_validare: float = 2.0) -> None:
        if not 0 < megaocteti_validare <= 50:
            raise ValueError("megaocteti_validare trebuie să fie între 0 și 50")
        self.director = Path(director)
        cerute = {"versiune": VERSIUNE_PREGATIRE, "url": url, "megaocteti_validare": megaocteti_validare}
        fisier_info = self.director / "info.json"
        info = json.loads(fisier_info.read_text(encoding="utf-8")) if fisier_info.exists() else {}
        gata = all(info.get(k) == v for k, v in cerute.items()) and all(
            (self.director / nume).exists() for nume in ("antrenare.txt", "validare.txt")
        )
        self.director.mkdir(parents=True, exist_ok=True)
        self.info = info if gata else pregateste(self.director, cerute)
        self._antrenare = (self.director / "antrenare.txt").read_text(encoding="utf-8")
        self._validare = (self.director / "validare.txt").read_text(encoding="utf-8")

    def text_antrenare(self) -> str:
        return self._antrenare

    def text_validare(self) -> str:
        return self._validare


if __name__ == "__main__":
    date = DateWikipedia()
    print(json.dumps(date.info, ensure_ascii=False, indent=2))
