"""Scurgeri în examen (17 octombrie 2026): cât din textul validărilor apare, literă cu literă, și în datele de antrenare.

Pentru fiecare validare din unelte/examen_validari_ws.py (pe aceleași primele --caractere litere pe care le măsoară
examenul) și pentru validarea întreagă a examenului oficial (TinyStories R2), fiecare bucată de --lungime litere la rând
(în interiorul unui text, la orice poziție) se caută în datele pe care le-a văzut Kronos: amestecul W2 și hrana.
Bucățile se compară prin amprente de 64 de biți (o potrivire întâmplătoare e practic imposibilă).

Pentru fiecare validare:
- **bucăți găsite**: din bucățile de --lungime litere ale validării, câte apar și în antrenare;
- **litere acoperite**: câte litere din validare stau în cel puțin o bucată găsită;
- **texte aproape copiate**: câte texte au cel puțin jumătate din litere acoperite.

Doar pe procesor; nu schimbă nimic, nici examenul, nici datele. Rezultatul: lucru/scurgeri_examen/.

    python unelte/scurgeri_examen.py
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

import numpy as np

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from unelte.examen_validari_ws import SEPARATOR, VALIDARI, inceput_de_text  # noqa: E402

ANTRENARE = ["date/ws/amestec/antrenare.txt", "date/ws/hrana_fapte_abecedar.txt"]
OFICIAL = {"povesti_oficial_tot": "date/tinystories_r2/validare.txt"}  # tot fișierul, cum îl citește examenul oficial
BAZA = np.uint64(1_000_003)


def amprente(litere: np.ndarray, lungime: int) -> np.ndarray:
    """Amprenta fiecărei bucăți de `lungime` litere la rând (litere = coduri Unicode), modulo 2^64."""
    n = len(litere) - lungime + 1
    if n <= 0:
        return np.zeros(0, dtype=np.uint64)
    x = litere.astype(np.uint64) + np.uint64(1)
    h = np.zeros(n, dtype=np.uint64)
    with np.errstate(over="ignore"):
        for k in range(lungime):
            h = h * BAZA + x[k: k + n]
    return h


def compune(h: np.ndarray, lungime: int, ori: int) -> np.ndarray:
    """Din amprentele bucăților de `lungime`, amprentele bucăților de `ori` × `lungime` (aceeași formulă, fără recalcul)."""
    n = len(h) - (ori - 1) * lungime
    if n <= 0:
        return np.zeros(0, dtype=np.uint64)
    pas = np.uint64(pow(int(BAZA), lungime, 2**64))
    rez = h[:n].copy()
    with np.errstate(over="ignore"):
        for k in range(1, ori):
            rez = rez * pas + h[k * lungime: k * lungime + n]
    return rez


def coduri(text: str) -> np.ndarray:
    return np.frombuffer(text.encode("utf-32-le"), dtype=np.uint32)


def texte_validare(cale: Path, caractere: int | None) -> list[str]:
    text = inceput_de_text(cale, caractere) if caractere else cale.read_text(encoding="utf-8")
    return [t.strip("\n") for t in text.split(SEPARATOR) if t.strip()]


def bucati_antrenare(cale: Path, litere: int, lungime: int) -> Iterator[np.ndarray]:
    """Fișierul de antrenare, pe bucăți de ~`litere` litere care se suprapun cu lungime-1 (nicio fereastră pierdută)."""
    rest = ""
    with cale.open(encoding="utf-8", errors="replace") as f:
        while True:
            nou = f.read(litere)
            if not nou:
                break
            text = rest + nou
            yield coduri(text)
            rest = text[-(lungime - 1):]


def cauta(validari: dict[str, list[str]], antrenare: list[Path], lungime: int, litere_pe_bucata: int = 50_000_000,
          spune=print) -> dict[str, Any]:
    return cauta_lungimi(validari, antrenare, [lungime], litere_pe_bucata, spune)[lungime]


def cauta_lungimi(validari: dict[str, list[str]], antrenare: list[Path], lungimi: list[int],
                  litere_pe_bucata: int = 50_000_000, spune=print) -> dict[int, dict[str, Any]]:
    """Ca `cauta`, pentru mai multe lungimi deodată, într-o singură trecere prin antrenare. Lungimile sunt multipli ai
    celei mai mici (ex. 50 și 200): amprentele lungi se compun din cele scurte."""
    baza = min(lungimi)
    if any(L % baza for L in lungimi):
        raise ValueError("lungimile trebuie să fie multipli ai celei mai mici")
    pe_lungime = {L: {v: [compune(amprente(coduri(t), baza), baza, L // baza) for t in texte]
                      for v, texte in validari.items()} for L in lungimi}
    toate = {L: np.unique(np.concatenate([h for lista in d.values() for h in lista] or [np.zeros(0, np.uint64)]))
             for L, d in pe_lungime.items()}
    gasite = {L: np.zeros(len(toate[L]), dtype=bool) for L in lungimi}
    citite = 0
    for cale in antrenare:
        inceput = time.monotonic()
        for bucata in bucati_antrenare(cale, litere_pe_bucata, max(lungimi)):
            hb = amprente(bucata, baza)
            for L in lungimi:
                if len(toate[L]) == 0:
                    continue
                h = compune(hb, baza, L // baza)
                poz = np.searchsorted(toate[L], h)
                poz[poz >= len(toate[L])] = 0
                gasite[L][poz[toate[L][poz] == h]] = True
            citite += len(bucata)
            spune(f"  {cale.name}: {citite / 1e9:.2f} miliarde de litere, {time.monotonic() - inceput:.0f} s", flush=True)
    return {L: _rezultate(validari, pe_lungime[L], toate[L], gasite[L], L) for L in lungimi}


def _rezultate(validari: dict[str, list[str]], pe_text: dict[str, list[np.ndarray]], toate: np.ndarray,
               gasite: np.ndarray, lungime: int) -> dict[str, Any]:
    rezultate: dict[str, Any] = {}
    for v, lista in pe_text.items():
        ferestre = gasit = litere = acoperite = copiate = 0
        exemple: list[str] = []
        pe_text_acoperire: list[float] = []
        for text, h in zip(validari[v], lista):
            if len(h) == 0:
                litere += len(text)
                pe_text_acoperire.append(0.0)
                continue
            bun = gasite[np.searchsorted(toate, h)]
            ferestre += len(h)
            gasit += int(bun.sum())
            # o literă e acoperită dacă stă într-o fereastră găsită
            acoperire = np.zeros(len(text) + 1, dtype=np.int32)
            start = np.nonzero(bun)[0]
            np.add.at(acoperire, start, 1)
            np.add.at(acoperire, start + lungime, -1)
            acop = int((np.cumsum(acoperire)[: len(text)] > 0).sum())
            litere += len(text)
            acoperite += acop
            pe_text_acoperire.append(round(acop / max(1, len(text)), 4))
            if acop >= len(text) / 2:
                copiate += 1
                if len(exemple) < 3:
                    exemple.append(text[:160])
        rezultate[v] = {"texte": len(validari[v]), "bucati": ferestre, "bucati_gasite": round(gasit / max(1, ferestre), 4),
                        "litere": litere, "litere_acoperite": round(acoperite / max(1, litere), 4),
                        "texte_aproape_copiate": round(copiate / max(1, len(validari[v])), 4), "exemple_copiate": exemple,
                        "acoperire_pe_text": pe_text_acoperire}
    return rezultate


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Cât din validări apare și în datele de antrenare.")
    parser.add_argument("--lungime", type=int, nargs="+", default=[50],
                        help="câte litere la rând trebuie să fie identice (mai multe: multipli ai celei mai mici)")
    parser.add_argument("--caractere", type=int, default=100_000, help="ca examenul: primele atâtea litere din validare")
    parser.add_argument("--antrenare", nargs="*", default=ANTRENARE)
    parser.add_argument("--director-lucru", default="lucru")
    args = parser.parse_args(argv)

    validari: dict[str, list[str]] = {}
    for v, cale in {**VALIDARI, **OFICIAL}.items():
        if Path(cale).is_file():
            validari[v] = texte_validare(Path(cale), None if v in OFICIAL else args.caractere)
    pe_lungime = cauta_lungimi(validari, [Path(c) for c in args.antrenare], args.lungime)
    dosar = Path(args.director_lucru) / "scurgeri_examen"
    dosar.mkdir(parents=True, exist_ok=True)
    iesire = dosar / f"scurgeri_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    iesire.write_text(json.dumps({"lungime": args.lungime, "caractere": args.caractere, "antrenare": args.antrenare,
                                  "validari": pe_lungime[args.lungime[0]],
                                  "pe_lungimi": {str(L): r for L, r in pe_lungime.items()}},
                                 ensure_ascii=False, indent=1), encoding="utf-8")
    for L, rezultate in pe_lungime.items():
        print(f"=== Bucăți de {L} litere din validări, găsite și în antrenare ===")
        print(f"{'validarea':<22} {'texte':>6} {'bucăți găsite':>14} {'litere acoperite':>17} {'texte aproape copiate':>22}")
        for v, r in rezultate.items():
            print(f"{v:<22} {r['texte']:>6} {r['bucati_gasite']:>14.1%} {r['litere_acoperite']:>17.1%} "
                  f"{r['texte_aproape_copiate']:>22.1%}")
    print(f"Toate cifrele: {iesire}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
