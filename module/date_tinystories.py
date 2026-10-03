"""Date TinyStories: povești scurte în engleză, cu vocabularul unui copil mic (Etapa M2).

Sursa: roneneldan/TinyStories pe Hugging Face, licență CDLA-Sharing-1.0.
La prima folosire descarcă doar ÎNCEPUTUL fișierelor oficiale (cât e nevoie, nu tot setul de
2,2 GB) și pregătește în date/tinystories/ două fișiere: antrenare.txt și validare.txt.
- antrenarea vine din fișierul oficial de antrenare, validarea din cel oficial de validare;
- poveștile rămân întregi: prima și ultima poveste din fiecare bucată descărcată se aruncă,
  pentru că pot fi tăiate la mijloc (fișierul oficial de validare chiar începe cu o poveste tăiată);
- orice poveste de validare care apare identic și în antrenare e scoasă, deci validarea nu
  conține povești din antrenare.
Poveștile sunt despărțite de un rând „<|endoftext|>”, ca în fișierele originale.

Setarea runda împarte poveștile de validare în două jumătăți (pentru testul plasei în două runde):
0 = toată validarea, 1 = prima jumătate, 2 = a doua jumătate. Antrenarea rămâne aceeași.

Pregătirea se face o singură dată; după aceea modulul doar citește fișierele. Se poate porni și
de mână: python -m module.date_tinystories
"""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path
from typing import Any

URL_ANTRENARE = "https://huggingface.co/datasets/roneneldan/TinyStories/resolve/main/TinyStoriesV2-GPT4-train.txt"
URL_VALIDARE = "https://huggingface.co/datasets/roneneldan/TinyStories/resolve/main/TinyStoriesV2-GPT4-valid.txt"
SEPARATOR = "<|endoftext|>"
VERSIUNE_PREGATIRE = 1


def _descarca_inceput(url: str, octeti: int) -> bytes:
    """Primii `octeti` din fișier. Cerem doar bucata asta (Range); chiar dacă serverul trimite tot, citim doar cât ne trebuie."""
    cerere = urllib.request.Request(url, headers={"Range": f"bytes=0-{octeti - 1}", "User-Agent": "cyberspace"})
    try:
        with urllib.request.urlopen(cerere, timeout=120) as raspuns:
            return raspuns.read(octeti)
    except OSError as e:
        raise ValueError(f"Nu am putut descărca TinyStories de la {url}: {e}. Verifică internetul.") from e


def _povesti_intregi(octeti: bytes) -> list[str]:
    """Poveștile dintr-o bucată descărcată, fără prima și ultima (pot fi tăiate)."""
    bucati = octeti.decode("utf-8", errors="ignore").split(SEPARATOR)
    return [p.strip() for p in bucati[1:-1] if p.strip()]


def _scrie(cale: Path, povesti: list[str]) -> int:
    text = f"\n{SEPARATOR}\n".join(povesti) + "\n"
    temporar = cale.with_name(cale.name + ".part")
    temporar.write_text(text, encoding="utf-8")
    temporar.replace(cale)
    return len(text.encode("utf-8"))


def pregateste(director: Path, cerute: dict[str, Any]) -> dict[str, Any]:
    """Descarcă începutul fișierelor oficiale și scrie antrenare.txt, validare.txt și info.json."""
    total = cerute["megaocteti"] * 1_000_000
    p = cerute["procent_validare"]
    print(f"Pregătesc TinyStories (~{cerute['megaocteti']:g} MB de text)...", flush=True)
    antrenare = _povesti_intregi(_descarca_inceput(cerute["url_antrenare"], int(total * (1 - p))))
    validare_bruta = _povesti_intregi(_descarca_inceput(cerute["url_validare"], int(total * p)))
    din_antrenare = set(antrenare)
    validare = [poveste for poveste in validare_bruta if poveste not in din_antrenare]
    if not antrenare or not validare:
        raise ValueError("Bucata descărcată din TinyStories nu are destule povești întregi; mărește megaocteti.")
    director.mkdir(parents=True, exist_ok=True)
    info = {
        **cerute,
        "sursa": "roneneldan/TinyStories (Hugging Face), licență CDLA-Sharing-1.0",
        "povesti_antrenare": len(antrenare),
        "povesti_validare": len(validare),
        "scoase_din_validare": len(validare_bruta) - len(validare),
        "octeti_antrenare": _scrie(director / "antrenare.txt", antrenare),
        "octeti_validare": _scrie(director / "validare.txt", validare),
    }
    (director / "info.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"Gata: {info['povesti_antrenare']:,} povești de antrenare ({info['octeti_antrenare'] / 1e6:.1f} MB), "
        f"{info['povesti_validare']:,} de validare ({info['octeti_validare'] / 1e6:.1f} MB)",
        flush=True,
    )
    return info


class DateTinyStories:
    MANIFEST = {
        "nume": "date_tinystories",
        "port": "date",
        "versiune": "0.2.0",
        "versiune_contract": 1,
        "resurse": {"disc_mb": 25},
        "permisiuni": ["internet", "citire_fisier", "scriere_fisier"],
    }

    def __init__(
        self,
        director: str = "date/tinystories",
        megaocteti: float = 20.0,
        procent_validare: float = 0.1,
        url_antrenare: str = URL_ANTRENARE,
        url_validare: str = URL_VALIDARE,
        runda: int = 0,
    ) -> None:
        if not 0 < megaocteti <= 2000:
            raise ValueError("megaocteti trebuie să fie între 0 și 2000")
        if not 0 < procent_validare < 0.5:
            raise ValueError("procent_validare trebuie să fie între 0 și 0.5")
        if runda not in (0, 1, 2):
            raise ValueError("runda trebuie să fie 0 (toată validarea), 1 sau 2 (o jumătate din povești)")
        self.director = Path(director)
        cerute = {
            "versiune": VERSIUNE_PREGATIRE,
            "megaocteti": megaocteti,
            "procent_validare": procent_validare,
            "url_antrenare": url_antrenare,
            "url_validare": url_validare,
        }
        fisier_info = self.director / "info.json"
        info = json.loads(fisier_info.read_text(encoding="utf-8")) if fisier_info.exists() else {}
        gata = all(info.get(k) == v for k, v in cerute.items()) and all(
            (self.director / nume).exists() for nume in ("antrenare.txt", "validare.txt")
        )
        self.info = info if gata else pregateste(self.director, cerute)
        self._antrenare = (self.director / "antrenare.txt").read_text(encoding="utf-8")
        self._validare = (self.director / "validare.txt").read_text(encoding="utf-8")
        self.runda = runda
        if runda:  # jumătatea de povești de validare a rundei
            despartitor = f"\n{SEPARATOR}\n"
            povesti = self._validare.rstrip("\n").split(despartitor)
            jumatate = len(povesti) // 2
            self._validare = despartitor.join(povesti[:jumatate] if runda == 1 else povesti[jumatate:]) + "\n"

    def text_antrenare(self) -> str:
        return self._antrenare

    def text_validare(self) -> str:
        return self._validare


if __name__ == "__main__":
    date = DateTinyStories()
    print(json.dumps(date.info, ensure_ascii=False, indent=2))
