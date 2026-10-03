"""Antrenează tokenizerul BPE (bucăți de cuvinte) pe TinyStories (Etapa M2).

    python unelte/antreneaza_tokenizer.py                 # 4.096 simboluri → date/tinystories/bpe_4096.json
    python unelte/antreneaza_tokenizer.py --marime 8192   # alt vocabular

Învață doar din textul de ANTRENARE (niciodată din validare). Pe validare doar verifică:
textul se poate rescrie exact din simboluri și câți octeți încap, în medie, într-un simbol.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from module.date_tinystories import DateTinyStories  # noqa: E402
from module.tokenizer_bpe import antreneaza_bpe  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Antrenează tokenizerul BPE pe TinyStories.")
    parser.add_argument("--marime", type=int, default=4096, help="câte simboluri are vocabularul")
    parser.add_argument("--director", default="date/tinystories", help="unde stau datele TinyStories")
    parser.add_argument("--destinatie", default=None, help="implicit: <director>/bpe_<marime>.json")
    args = parser.parse_args(argv)
    destinatie = Path(args.destinatie or Path(args.director) / f"bpe_{args.marime}.json")

    date = DateTinyStories(director=args.director)  # pregătește datele, dacă lipsesc
    text = date.text_antrenare()
    print(f"Antrenez tokenizerul: {args.marime:,} simboluri, pe {len(text.encode('utf-8')) / 1e6:.1f} MB de text...", flush=True)
    start = time.perf_counter()
    tokenizer = antreneaza_bpe(text, args.marime)
    durata = time.perf_counter() - start

    validare = date.text_validare()
    simboluri = tokenizer.codifica(validare)
    if tokenizer.decodeaza(simboluri) != validare:
        print("EROARE: textul de validare nu se rescrie exact din simboluri.", file=sys.stderr)
        return 1
    octeti_pe_simbol = len(validare.encode("utf-8")) / len(simboluri)
    tokenizer.salveaza(destinatie, {
        "antrenat_pe": f"{args.director}/antrenare.txt",
        "octeti_antrenare": len(text.encode("utf-8")),
        "octeti_pe_simbol_validare": round(octeti_pe_simbol, 3),
    })
    print(f"Gata în {durata:.0f} s: {destinatie} ({tokenizer.marime:,} simboluri)")
    print(f"Pe validare: {octeti_pe_simbol:.2f} octeți pe simbol (pe litere ar fi ~1); textul se rescrie exact.")
    exemple = [tokenizer.decodeaza([256 + k]) for k in range(12)]
    print("Primele lipiri învățate:", ", ".join(repr(e) for e in exemple))
    lungi = sorted(range(256, tokenizer.marime), key=lambda s: -len(tokenizer.octeti(s)))[:8]
    print("Cele mai lungi simboluri:", ", ".join(repr(tokenizer.decodeaza([s])) for s in lungi))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
