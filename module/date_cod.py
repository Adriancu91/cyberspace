"""Date pentru Kronos-Cod: simbolurile gata făcute de tokenizerul de cod (S55), nu text.

Citește `lucru/kronos_cod/simboluri/`: `antrenare_NNNNN.bin` și `validare_NNNNN.bin` (uint16, cu simbolul de sfârșit de
fișier, 32.764, după fiecare fișier de cod). Antrenarea și validarea stau în fișiere separate, deci validarea (cele
5.686 de fișiere) nu ajunge niciodată în bucățile de antrenare.

- `bucati_antrenare(numar, generator)`: `numar` bucăți alese la întâmplare, fiecare de `context` + 1 simboluri
  (intrarea = primele `context`, ținta = aceleași, mutate cu unu).
- `bucati_validare()`: validarea tăiată în bucăți de `context` + 1, una după alta, fără suprapunere (pentru pierderea
  din timpul antrenării); `fisiere_validare()`: simbolurile fiecărui fișier de validare, separat (pentru examen).
- `text_antrenare()` / `text_validare()` (contractul portului „date”): setul are ~3,7 GB de cod, deci nu se dă ca text.
  Cu `previzualizare = true` dau doar începutul, decodat (pentru teste și privit); altfel spun clar că modelul trebuie
  să citească simbolurile, ca o antrenare să nu învețe din greșeală doar din previzualizare.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

SFARSIT_DE_FISIER = 32_764


class DateCod:
    MANIFEST = {
        "nume": "date_cod",
        "port": "date",
        "versiune": "0.1.0",
        "versiune_contract": 1,
        "resurse": {},
        "permisiuni": ["citire_fisier"],
    }

    def __init__(self, director: str = "lucru/kronos_cod/simboluri", context: int = 512,
                 sfarsit_de_fisier: int = SFARSIT_DE_FISIER, cale_tokenizer: str = "", previzualizare: bool = False,
                 simboluri_previzualizare: int = 20_000) -> None:
        d = Path(director)
        if not d.is_dir():
            raise ValueError(f"Nu găsesc „{director}”. Simbolurile le face: python -m unelte.kronos_cod.tokenizer_cod tot")
        if context < 1:
            raise ValueError("context trebuie să fie cel puțin 1")
        self.director = d
        self.context = context
        self.sfarsit_de_fisier = sfarsit_de_fisier
        self.cale_tokenizer = cale_tokenizer
        self.previzualizare = previzualizare
        self.simboluri_previzualizare = simboluri_previzualizare
        self.fisiere_antrenare = sorted(d.glob("antrenare_*.bin"))
        self.fisiere_validare_bin = sorted(d.glob("validare_*.bin"))
        if not self.fisiere_antrenare or not self.fisiere_validare_bin:
            raise ValueError(f"În „{director}” lipsesc antrenare_*.bin sau validare_*.bin")
        self._antrenare: np.ndarray | None = None
        self._validare: np.ndarray | None = None
        if len(self._simboluri_antrenare_brute()) <= context + 1:
            raise ValueError("antrenarea e mai scurtă decât contextul")

    # --- simbolurile ------------------------------------------------------------

    def _simboluri_antrenare_brute(self) -> np.ndarray:
        if self._antrenare is None:
            self._antrenare = _uneste(self.fisiere_antrenare)
        return self._antrenare

    def simboluri_antrenare(self) -> np.ndarray:
        """Toate simbolurile de antrenare, unul după altul (uint16; ~2,2 GB în memorie pe setul întreg)."""
        return self._simboluri_antrenare_brute()

    def simboluri_validare(self) -> np.ndarray:
        if self._validare is None:
            self._validare = _uneste(self.fisiere_validare_bin)
        return self._validare

    def bucati_antrenare(self, numar: int, generator: np.random.Generator) -> np.ndarray:
        """`numar` bucăți la întâmplare din antrenare, fiecare de context + 1 simboluri (int64)."""
        s = self.simboluri_antrenare()
        pozitii = generator.integers(0, len(s) - self.context - 1, size=numar)
        return np.stack([s[p : p + self.context + 1] for p in pozitii]).astype(np.int64)

    def bucati_validare(self) -> np.ndarray:
        """Validarea în bucăți de context + 1, una după alta (ultimul simbol al unei bucăți e primul din următoarea)."""
        s = self.simboluri_validare()
        n = (len(s) - 1) // self.context
        return np.stack([s[k * self.context : (k + 1) * self.context + 1] for k in range(n)]).astype(np.int64)

    def fisiere_validare(self) -> list[np.ndarray]:
        """Simbolurile fiecărui fișier de validare, în ordine, fără sfârșitul de fișier."""
        s = self.simboluri_validare()
        capete = np.flatnonzero(s == self.sfarsit_de_fisier)
        inceputuri = np.concatenate(([0], capete[:-1] + 1))
        return [s[a:b] for a, b in zip(inceputuri, capete)]

    # --- contractul portului „date” ---------------------------------------------

    def _text(self, simboluri: np.ndarray) -> str:
        if not self.previzualizare:
            raise RuntimeError("date_cod dă simboluri, nu text: modelul trebuie să folosească simboluri_antrenare() / "
                               "bucati_antrenare(). Textul e doar o previzualizare (setarea previzualizare = true).")
        from module.tokenizer_bpe import TokenizerBPE

        tok = TokenizerBPE.incarca(self.cale_tokenizer)
        bucata = simboluri[: self.simboluri_previzualizare]
        return tok.decodeaza(int(x) for x in bucata if x != self.sfarsit_de_fisier)

    def text_antrenare(self) -> str:
        return self._text(self.simboluri_antrenare())

    def text_validare(self) -> str:
        return self._text(self.simboluri_validare())


def _uneste(fisiere: list[Path]) -> np.ndarray:
    return np.concatenate([np.fromfile(f, dtype=np.uint16) for f in fisiere])
