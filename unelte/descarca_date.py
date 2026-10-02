"""Descarcă textul Shakespeare (~1 MB, domeniu public) în date/shakespeare.txt.

Rulează din folderul proiectului:
    python unelte/descarca_date.py
"""

from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

URL = "https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt"
DESTINATIE = Path(__file__).resolve().parent.parent / "date" / "shakespeare.txt"


def main() -> int:
    if DESTINATIE.exists() and DESTINATIE.stat().st_size > 1_000_000:
        print(f"Există deja: {DESTINATIE} ({DESTINATIE.stat().st_size:,} octeți)")
        return 0
    DESTINATIE.parent.mkdir(parents=True, exist_ok=True)
    print(f"Descarc {URL} ...")
    try:
        with urllib.request.urlopen(URL, timeout=60) as raspuns:
            continut = raspuns.read()
    except OSError as e:
        print(f"Nu am putut descărca: {e}\nVerifică internetul și încearcă din nou.", file=sys.stderr)
        return 1
    DESTINATIE.write_bytes(continut)
    print(f"Gata: {DESTINATIE} ({len(continut):,} octeți)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
