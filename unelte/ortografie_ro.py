"""Filtrul de ortografie pentru română (15 octombrie 2026, cerut de Adrian), pe procesor.

Dicționarul hunspell ro_RO (rospell) are licența GPL-2.0 / LGPL-2.1 / MPL-1.1, care nu e pe lista lui Adrian (Apache,
MIT, CC BY, ODC-BY, domeniu public): nu l-am descărcat. În locul lui, lista cuvintelor cunoscute se face din textele
românești pe care le avem deja, scrise și corectate de oameni: Wikipedia și Wikisource (date/ws/curat/, doar partea de
antrenare). Un cuvânt e cunoscut dacă apare acolo de cel puțin --minim ori (3: o greșeală de tipar rară nu intră).
Textul de pe web (FineWeb-2) nu intră: are des cuvinte fără diacritice („si”, „sa”), care ar lăsa să treacă greșeli.

Un cuvânt dintr-o pereche românească e necunoscut dacă nu e în listă (cu litere mici) și nu e:
- un nume propriu: începe cu literă mare și nu e primul cuvânt al propoziției;
- o excepție din date/conversatie/exceptii_ortografie.txt (termeni tehnici, câte unul pe rând);
- un număr.
Cuvintele cu cratimă („s-a”, „într-o”) se verifică pe bucăți.
Din 15 octombrie, 11:40: un cuvânt fără diacritice e socotit necunoscut și dacă aceeași formă cu diacritice e de cel
puțin 20 de ori mai deasă (ex. „si” față de „și”, „mananca” față de „mănâncă”): textele traduse automat le pierd uneori.

    python unelte/ortografie_ro.py --construieste      # o singură dată: date/conversatie/cuvinte_ro.txt
    python unelte/ortografie_ro.py --verifica "Iarna are temperaturi frisoase."
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

RADACINA = Path(__file__).resolve().parent.parent
SURSE = ["date/ws/curat/wikipedia_ro/antrenare.txt", "date/ws/curat/wikisource_ro/antrenare.txt"]
LISTA = "date/conversatie/cuvinte_ro.txt"
EXCEPTII = "date/conversatie/exceptii_ortografie.txt"
_CUVANT = re.compile(r"[A-Za-zĂÂÎȘȚăâîșțÁÉÍÓÚÜÖáéíóúüöÇçÑñ]+")
_PROPOZITIE = re.compile(r"(?<=[.!?…:])\s+|\n+")


def construieste(surse: list[Path], minim: int = 3, bucata: int = 64 * 2**20) -> dict[str, int]:
    numarate: Counter[str] = Counter()
    for sursa in surse:
        with sursa.open(encoding="utf-8") as f:
            while text := f.read(bucata):
                numarate.update(c.lower() for c in _CUVANT.findall(text))
    return {c: n for c, n in numarate.items() if n >= minim}


FARA_DIACRITICE = str.maketrans("ăâîșțĂÂÎȘȚ", "aaistAAIST")


class Cunoscute(set):
    """Cuvintele cunoscute, plus cele fără diacritice care sunt de fapt o formă cu diacritice scrisă greșit."""

    def __init__(self, numarate: dict[str, int], raport: int = 20) -> None:
        super().__init__(numarate)
        cele_mai_dese: dict[str, int] = {}
        for c, n in numarate.items():
            if c != c.translate(FARA_DIACRITICE):
                cheie = c.translate(FARA_DIACRITICE)
                cele_mai_dese[cheie] = max(cele_mai_dese.get(cheie, 0), n)
        self.fara_diacritice_gresit = {c for c, n in numarate.items() if c == c.translate(FARA_DIACRITICE)
                                       and cele_mai_dese.get(c, 0) >= raport * n}

    def __contains__(self, cuvant: object) -> bool:
        return super().__contains__(cuvant) and cuvant not in self.fara_diacritice_gresit


def citeste_lista(cale: str | Path = RADACINA / LISTA) -> Cunoscute:
    numarate = {}
    for r in Path(cale).read_text(encoding="utf-8").splitlines():
        if r.strip():
            c, _, n = r.partition("\t")
            numarate[c] = int(n or 1)
    return Cunoscute(numarate)


def citeste_exceptii(cale: str | Path = RADACINA / EXCEPTII) -> set[str]:
    fisier = Path(cale)
    if not fisier.exists():
        return set()
    return {r.strip().lower() for r in fisier.read_text(encoding="utf-8").splitlines() if r.strip() and not r.startswith("#")}


def necunoscute(text: str, cunoscute: set[str], exceptii: set[str] = frozenset()) -> list[str]:
    """Cuvintele necunoscute din text, în ordine, fără repetări."""
    gasite: list[str] = []
    for propozitie in _PROPOZITIE.split(text):
        for i, m in enumerate(_CUVANT.finditer(propozitie)):
            cuvant = m.group(0)
            if i > 0 and cuvant[0].isupper():  # nume propriu
                continue
            mic = cuvant.lower()
            if mic not in cunoscute and mic not in exceptii and cuvant not in gasite:
                gasite.append(cuvant)
    return gasite


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Filtrul de ortografie pentru română, din Wikipedia și Wikisource.")
    parser.add_argument("--construieste", action="store_true")
    parser.add_argument("--minim", type=int, default=3)
    parser.add_argument("--verifica", default=None)
    args = parser.parse_args(argv)
    if args.construieste:
        cuvinte = construieste([RADACINA / s for s in SURSE], args.minim)
        iesire = RADACINA / LISTA
        iesire.parent.mkdir(parents=True, exist_ok=True)
        iesire.write_text("".join(f"{c}\t{n}\n" for c, n in sorted(cuvinte.items())), encoding="utf-8")
        print(f"{len(cuvinte):,} de cuvinte cunoscute (cel puțin {args.minim} apariții) în {iesire}", flush=True)
    if args.verifica is not None:
        print(necunoscute(args.verifica, citeste_lista(), citeste_exceptii()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
