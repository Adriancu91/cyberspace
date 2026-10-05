"""Tokenizer pe bucăți de cuvinte (BPE pe octeți), scris de la 0 (Etapa M2).

Cum funcționează:
1. Textul se taie în „bucăți”, ca la GPT-2: un cuvânt cu spațiul dinaintea lui, un număr, semne de
   punctuație, spații. Bucățile nu se lipesc niciodată între ele.
2. Fiecare bucată se scrie ca octeți (UTF-8): 256 de simboluri de bază, deci ORICE text se poate
   codifica, fără simbol „necunoscut”.
3. La antrenare se caută perechea de simboluri vecine care apare cel mai des și se lipește într-un
   simbol nou („ t” + „he” → „ the”), până se ajunge la mărimea vocabularului (implicit 4.096).
4. La codificare se aplică aceleași lipiri, în aceeași ordine.
Simbolurile speciale (ex. „<|endoftext|>”) primesc câte un număr propriu și nu se taie niciodată.

Pentru memoria ierarhică: capete_caractere() spune, pentru fiecare simbol, câte litere COMPLETE
s-au scris până la el inclusiv, ca memoria să dea codul ultimului cuvânt terminat per simbol.

Nu e un modul de port: îl folosește GPT-ul (setarea tokenizer = "bpe"). Se antrenează cu:
    python unelte/antreneaza_tokenizer.py
"""

from __future__ import annotations

import codecs
import heapq
import json
import re
from collections import Counter, defaultdict
from itertools import accumulate
from pathlib import Path
from typing import Any, Iterable, Iterator

VERSIUNE = 1
SPECIALE_IMPLICITE = ("<|endoftext|>",)
# Bucățile, ca la GPT-2: terminații ('s, 't, 're...), cuvânt cu spațiul dinainte, număr, semne, spații.
# Fiecare literă din text intră în exact o bucată (testul test_bucatile_acopera_tot_textul verifică).
BUCATI = re.compile(r"""'(?:[sdmt]|ll|ve|re)| ?[^\W\d_]+| ?\d+| ?(?:[^\s\w]|_)+|\s+(?!\S)|\s+""")
_FARA_RANG = float("inf")


def _imbina(simboluri: list[int], pereche: tuple[int, int], nou: int) -> list[int]:
    """Înlocuiește, de la stânga la dreapta, fiecare apariție a perechii cu simbolul nou."""
    rezultat: list[int] = []
    i = 0
    while i < len(simboluri):
        if i + 1 < len(simboluri) and simboluri[i] == pereche[0] and simboluri[i + 1] == pereche[1]:
            rezultat.append(nou)
            i += 2
        else:
            rezultat.append(simboluri[i])
            i += 1
    return rezultat


def _taietor(speciale: Iterable[str]) -> re.Pattern[str] | None:
    """Taie textul în jurul simbolurilor speciale (le păstrează în listă, ca să le putem recunoaște)."""
    speciale = sorted(speciale, key=len, reverse=True)
    return re.compile("(" + "|".join(re.escape(s) for s in speciale) + ")") if speciale else None


class TokenizerBPE:
    def __init__(self, imbinari: Iterable[Iterable[int]], speciale: Iterable[str] = SPECIALE_IMPLICITE) -> None:
        self.imbinari: list[tuple[int, int]] = [(int(a), int(b)) for a, b in imbinari]
        self.speciale: dict[str, int] = {s: 256 + len(self.imbinari) + k for k, s in enumerate(speciale)}
        self.marime = 256 + len(self.imbinari) + len(self.speciale)
        self._rang = {p: k for k, p in enumerate(self.imbinari)}
        self._octeti: list[bytes] = [bytes([b]) for b in range(256)]
        for a, b in self.imbinari:
            self._octeti.append(self._octeti[a] + self._octeti[b])
        self._octeti += [s.encode("utf-8") for s in self.speciale]
        self._taietor = _taietor(self.speciale)
        self._memorie: dict[str, list[int]] = {}  # bucăți deja codificate

    # --- codificare ---------------------------------------------------------------

    def _bucata(self, bucata: str) -> list[int]:
        cod = self._memorie.get(bucata)
        if cod is None:
            simboluri = list(bucata.encode("utf-8"))
            while len(simboluri) > 1:
                pereche = min(zip(simboluri, simboluri[1:]), key=lambda p: self._rang.get(p, _FARA_RANG))
                if pereche not in self._rang:
                    break
                simboluri = _imbina(simboluri, pereche, 256 + self._rang[pereche])
            cod = simboluri
            if len(self._memorie) < 500_000:
                self._memorie[bucata] = cod
        return cod

    def codifica(self, text: str) -> list[int]:
        simboluri: list[int] = []
        for segment in self._taietor.split(text) if self._taietor else [text]:
            if segment in self.speciale:
                simboluri.append(self.speciale[segment])
            elif segment:
                for bucata in BUCATI.findall(segment):
                    simboluri.extend(self._bucata(bucata))
        return simboluri

    def codifica_pe_bucati(self, text: str, marime: int = 50_000_000) -> Iterator[list[int]]:
        """Ca codifica, dar pe bucăți de ~marime litere, tăiate imediat după un simbol special: acolo nu se lipește nimic
        peste tăietură, deci simbolurile puse cap la cap sunt exact cele de la codifica(text). Pentru texte foarte mari
        (ex. TinyStories întreg), fără o listă uriașă în memorie."""
        start = 0
        while start < len(text):
            capat = len(text)
            if start + marime < len(text):
                taieturi = [p + len(s) for s in self.speciale if (p := text.find(s, start + marime)) >= 0]
                if taieturi:
                    capat = min(taieturi)
            yield self.codifica(text[start:capat])
            start = capat

    def decodeaza(self, simboluri: Iterable[int]) -> str:
        return b"".join(self._octeti[s] for s in simboluri).decode("utf-8", errors="replace")

    def octeti(self, simbol: int) -> bytes:
        return self._octeti[simbol]

    def capete_caractere(self, simboluri: list[int]) -> tuple[str, list[int]]:
        """Textul și, pentru fiecare simbol, câte litere COMPLETE s-au scris până la el inclusiv.

        O literă scrisă pe mai mulți octeți (ex. „ș”, „“”) se numără abia la simbolul care o
        încheie, deci ce primește un simbol de la memorie nu depinde de nimic de după el.
        """
        bucati = [self._octeti[s] for s in simboluri]
        if all(b.isascii() for b in bucati):
            return b"".join(bucati).decode("ascii"), list(accumulate(len(b) for b in bucati))
        decodor = codecs.getincrementaldecoder("utf-8")(errors="replace")
        parti: list[str] = []
        capete: list[int] = []
        scrise = 0
        for b in bucati:
            parte = decodor.decode(b)
            parti.append(parte)
            scrise += len(parte)
            capete.append(scrise)
        parti.append(decodor.decode(b"", final=True))
        return "".join(parti), capete

    # --- salvare -----------------------------------------------------------------

    def ca_dictionar(self) -> dict[str, Any]:
        return {"versiune": VERSIUNE, "imbinari": [list(p) for p in self.imbinari], "speciale": list(self.speciale)}

    @classmethod
    def din_dictionar(cls, date: dict[str, Any]) -> TokenizerBPE:
        if date.get("versiune") != VERSIUNE:
            raise ValueError(f"Tokenizerul are versiunea {date.get('versiune')}, aștept {VERSIUNE}")
        return cls(date["imbinari"], date["speciale"])

    def salveaza(self, cale: str | Path, info: dict[str, Any] | None = None) -> None:
        fisier = Path(cale)
        fisier.parent.mkdir(parents=True, exist_ok=True)
        fisier.write_text(json.dumps({**self.ca_dictionar(), "info": info or {}}, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def incarca(cls, cale: str | Path) -> TokenizerBPE:
        fisier = Path(cale)
        if not fisier.exists():
            raise ValueError(
                f"Nu găsesc tokenizerul „{cale}”. Antrenează-l întâi: python unelte/antreneaza_tokenizer.py"
            )
        return cls.din_dictionar(json.loads(fisier.read_text(encoding="utf-8")))


def antreneaza_bpe(text: str, marime: int = 4096, speciale: Iterable[str] = SPECIALE_IMPLICITE) -> TokenizerBPE:
    """Învață lipirile din text, până la `marime` simboluri (256 de octeți + lipiri + speciale)."""
    speciale = list(speciale)
    numar_imbinari = marime - 256 - len(speciale)
    if numar_imbinari < 0:
        raise ValueError(f"marime trebuie să fie cel puțin {256 + len(speciale)}")

    # 1. Bucățile textului (fără simbolurile speciale) și de câte ori apare fiecare.
    taietor = _taietor(speciale)
    frecvente: Counter[str] = Counter()
    for segment in taietor.split(text) if taietor else [text]:
        if segment not in speciale:
            frecvente.update(BUCATI.findall(segment))
    cuvinte = [list(bucata.encode("utf-8")) for bucata in frecvente]
    numar = list(frecvente.values())

    # 2. De câte ori apare fiecare pereche de simboluri vecine și în ce bucăți.
    perechi: defaultdict[tuple[int, int], int] = defaultdict(int)
    unde: defaultdict[tuple[int, int], set[int]] = defaultdict(set)
    for i, cuvant in enumerate(cuvinte):
        for p in zip(cuvant, cuvant[1:]):
            perechi[p] += numar[i]
            unde[p].add(i)
    coada = [(-n, p) for p, n in perechi.items()]  # cea mai deasă pereche iese prima; la egalitate, cea mai mică
    heapq.heapify(coada)

    # 3. Lipim, pe rând, perechea cea mai deasă și actualizăm doar bucățile atinse.
    imbinari: list[tuple[int, int]] = []
    while len(imbinari) < numar_imbinari and coada:
        minus_n, pereche = heapq.heappop(coada)
        if minus_n == 0 or -minus_n != perechi.get(pereche, 0):
            continue  # intrare veche din coadă
        nou = 256 + len(imbinari)
        imbinari.append(pereche)
        atinse: set[tuple[int, int]] = set()
        for i in unde.pop(pereche, set()):
            cuvant = cuvinte[i]
            for p in zip(cuvant, cuvant[1:]):
                perechi[p] -= numar[i]
                atinse.add(p)
            cuvant = cuvinte[i] = _imbina(cuvant, pereche, nou)
            for p in zip(cuvant, cuvant[1:]):
                perechi[p] += numar[i]
                unde[p].add(i)
                atinse.add(p)
        for p in atinse:
            if perechi[p] > 0:
                heapq.heappush(coada, (-perechi[p], p))
    return TokenizerBPE(imbinari, speciale)
