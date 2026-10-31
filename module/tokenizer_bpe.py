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

Regulile „ws” (tokenizer-ul workstation-ului, 12 octombrie 2026; docs/MUTARE_workstation.md, secțiunea 5):
- numerele 0–999 (și formele cu zerouri în față: „07”, „007”) sunt simboluri întregi, puse în vocabular de la început;
  un număr mai lung se taie în grupe de cel mult 3 cifre, de la stânga („1234” = „123” + „4”). Spațiul dinaintea unui
  număr nu se lipește de el: „46” e același simbol oriunde ar sta (după „=”, după „(”, la început de rând);
- restul bucăților sunt ca la regulile vechi. Ca un cuvânt să rămână întreg și fără spațiu în față (după ghilimele sau
  paranteze), la antrenare forma fără spațiu primește o parte din numărul de apariții al formei cu spațiu.
Regulile vechi („gpt2”) și fișierele lor rămân exact cum erau.

Regulile „cod” (Kronos-Cod, S55, 31 octombrie 2026), pentru Python / Rust / C:
- sfârșitul de rând e o bucată separată (unul sau mai multe sfârșituri de rând la rând, și cele de Windows);
  indentarea de la început de rând e o bucată separată, întreagă (cuvântul de după ea nu primește spațiu în față);
- șirurile de spații (1–16) și de tab-uri (1–8) sunt simboluri întregi, puse în vocabular de la început; un șir mai
  lung se taie în bucăți de 16 spații / 8 tab-uri, de la stânga, iar șirurile acestea nu intră în învățare;
- un identificator e o bucată întreagă (litere, cifre, „_”: „__init__”, „snake_case”), cu spațiul dinainte; numerele
  sunt grupe de cel mult 3 cifre, fără spațiul dinainte (ca la „ws”, dar lipirile lor se învață ca restul).

Nu e un modul de port: îl folosește GPT-ul (setarea tokenizer = "bpe"). Se antrenează cu:
    python unelte/antreneaza_tokenizer.py        # regulile vechi, pe TinyStories
    python unelte/antreneaza_tokenizer_ws.py     # regulile „ws”, pe amestecul engleză + română + cod + numere
    python unelte/kronos_cod/tokenizer_cod.py    # regulile „cod”, pe codul descărcat la S46
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
# Regulile „ws”: la fel, dar un număr e o grupă de cel mult 3 cifre, fără spațiul dinainte.
BUCATI_WS = re.compile(r"""'(?:[sdmt]|ll|ve|re)| ?[^\W\d_]+|\d{1,3}| ?(?:[^\s\w]|_)+|\s+(?!\S)|\s+""")
# Regulile „cod”: sfârșituri de rând, indentarea de la început de rând, identificator întreg cu spațiul dinainte, grupe
# de cel mult 3 cifre, semne cu spațiul dinainte, spații (ultimul spațiu rămâne lângă ce urmează, ca la GPT-2).
BUCATI_COD = re.compile(r"""(?:\r?\n)+|(?<![^\n])[^\S\n]+| ?[^\W\d]\w*|\d{1,3}| ?[^\s\w]+|[^\S\n]+(?!\S)|\s+""")
REGULI = {"gpt2": BUCATI, "ws": BUCATI_WS, "cod": BUCATI_COD}
VERSIUNI = {"gpt2": 1, "ws": 2, "cod": 3}
_CIFRE = "0123456789"
_FARA_RANG = float("inf")
SPATII_MAX, TABURI_MAX = 16, 8


def imbinari_spatii() -> list[tuple[int, int]]:
    """Lipirile fixe ale regulilor „cod”, primele din vocabular: 2–16 spații (simbolurile 256–270), apoi 2–8 tab-uri
    (simbolurile 271–277), fiecare = cel de dinainte + încă unul."""
    spatii = [(32, 32)] + [(256 + k, 32) for k in range(SPATII_MAX - 2)]
    t0 = 256 + len(spatii)
    return spatii + [(9, 9)] + [(t0 + k, 9) for k in range(TABURI_MAX - 2)]


def _simbol_sir(caracter: str, k: int) -> int:
    if k == 1:
        return ord(caracter)
    return 256 + k - 2 if caracter == " " else 256 + SPATII_MAX - 1 + k - 2


def tabel_spatii(maxim: int = 64) -> dict[str, list[int]]:
    """Fiecare șir de 1–`maxim` spații sau tab-uri → simbolurile lui (bucăți de 16 spații / 8 tab-uri, de la stânga)."""
    tabel: dict[str, list[int]] = {}
    for caracter, plafon in ((" ", SPATII_MAX), ("\t", TABURI_MAX)):
        for n in range(1, maxim + 1):
            tabel[caracter * n] = [_simbol_sir(caracter, plafon)] * (n // plafon) + (
                [_simbol_sir(caracter, n % plafon)] if n % plafon else [])
    return tabel


def _doar_spatii(bucata: str) -> bool:
    return bool(bucata) and (set(bucata) == {" "} or set(bucata) == {"\t"})


def imbinari_numere() -> list[tuple[int, int]]:
    """Lipirile fixe ale regulilor „ws”, primele din vocabular: cele 100 de perechi de cifre („00”–„99”, simbolurile
    256–355), apoi cele 1.000 de grupe de trei („000”–„999”, simbolurile 356–1355)."""
    doua = [(ord(a), ord(b)) for a in _CIFRE for b in _CIFRE]
    return doua + [(256 + k, ord(c)) for k in range(100) for c in _CIFRE]


def _tabel_numere() -> dict[str, list[int]]:
    """Fiecare grupă de 1–3 cifre → simbolul ei (direct, fără lipiri: „123” nu poate ieși „1” + „23”)."""
    tabel = {c: [ord(c)] for c in _CIFRE}
    tabel.update({f"{k:02d}": [256 + k] for k in range(100)})
    tabel.update({f"{k:03d}": [356 + k] for k in range(1000)})
    return tabel


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
    def __init__(self, imbinari: Iterable[Iterable[int]], speciale: Iterable[str] = SPECIALE_IMPLICITE,
                 reguli: str = "gpt2") -> None:
        if reguli not in REGULI:
            raise ValueError(f"reguli trebuie să fie una din: {', '.join(REGULI)}")
        self.reguli = reguli
        self._bucati = REGULI[reguli]
        self.imbinari: list[tuple[int, int]] = [(int(a), int(b)) for a, b in imbinari]
        if reguli == "ws" and self.imbinari[:1100] != imbinari_numere():
            raise ValueError("Tokenizerul cu regulile „ws” trebuie să înceapă cu lipirile fixe ale numerelor")
        fixe_cod = imbinari_spatii()
        if reguli == "cod" and self.imbinari[:len(fixe_cod)] != fixe_cod:
            raise ValueError("Tokenizerul cu regulile „cod” trebuie să înceapă cu lipirile fixe ale spațiilor")
        self.speciale: dict[str, int] = {s: 256 + len(self.imbinari) + k for k, s in enumerate(speciale)}
        self.marime = 256 + len(self.imbinari) + len(self.speciale)
        self._rang = {p: k for k, p in enumerate(self.imbinari)}
        self._octeti: list[bytes] = [bytes([b]) for b in range(256)]
        for a, b in self.imbinari:
            self._octeti.append(self._octeti[a] + self._octeti[b])
        self._octeti += [s.encode("utf-8") for s in self.speciale]
        self._taietor = _taietor(self.speciale)
        self._memorie: dict[str, list[int]] = {}  # bucăți deja codificate
        if reguli == "ws":
            self._memorie.update(_tabel_numere())
        if reguli == "cod":
            self._memorie.update(tabel_spatii())

    # --- codificare ---------------------------------------------------------------

    def _bucata(self, bucata: str) -> list[int]:
        cod = self._memorie.get(bucata)
        if cod is None and self.reguli == "cod" and _doar_spatii(bucata):
            cod = tabel_spatii(len(bucata))[bucata]
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
                for bucata in self._bucati.findall(segment):
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

    def codifica_fara_speciale(self, text: str) -> list[int]:
        """Ca codifica, dar un simbol special scris în text (ex. „<|endoftext|>” într-un fișier de cod) rămâne text."""
        simboluri: list[int] = []
        for bucata in self._bucati.findall(text):
            simboluri.extend(self._bucata(bucata))
        return simboluri

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
        baza = {"versiune": VERSIUNI[self.reguli], "imbinari": [list(p) for p in self.imbinari],
                "speciale": list(self.speciale)}
        return baza if self.reguli == "gpt2" else {**baza, "reguli": self.reguli}  # fișierele vechi rămân la fel

    @classmethod
    def din_dictionar(cls, date: dict[str, Any]) -> TokenizerBPE:
        reguli = date.get("reguli", "gpt2")
        if reguli not in REGULI or date.get("versiune") != VERSIUNI[reguli]:
            raise ValueError(f"Tokenizerul are versiunea {date.get('versiune')} și regulile „{reguli}”; "
                             f"știu: {VERSIUNI}")
        return cls(date["imbinari"], date["speciale"], reguli)

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


def frecvente_bucati(text: str, speciale: Iterable[str] = SPECIALE_IMPLICITE, reguli: str = "gpt2") -> Counter[str]:
    """Bucățile textului (fără simbolurile speciale) și de câte ori apare fiecare."""
    speciale = list(speciale)
    taietor = _taietor(speciale)
    frecvente: Counter[str] = Counter()
    for segment in taietor.split(text) if taietor else [text]:
        if segment not in speciale:
            frecvente.update(REGULI[reguli].findall(segment))
    return frecvente


def antreneaza_bpe(text: str, marime: int = 4096, speciale: Iterable[str] = SPECIALE_IMPLICITE) -> TokenizerBPE:
    """Învață lipirile din text, până la `marime` simboluri (256 de octeți + lipiri + speciale)."""
    return antreneaza_din_frecvente(frecvente_bucati(text, speciale), marime, speciale)


def antreneaza_din_frecvente(frecvente: dict[str, float], marime: int = 4096,
                             speciale: Iterable[str] = SPECIALE_IMPLICITE, reguli: str = "gpt2") -> TokenizerBPE:
    """Învață lipirile dintr-un tabel bucată → de câte ori apare (pentru texte mari, numărate pe bucăți, în paralel).
    Cu regulile „ws”, lipirile fixe ale numerelor sunt primele, iar grupele de cifre nu intră în învățare."""
    speciale = list(speciale)
    fixe = imbinari_numere() if reguli == "ws" else imbinari_spatii() if reguli == "cod" else []
    numar_imbinari = marime - 256 - len(speciale)
    if numar_imbinari < len(fixe):
        raise ValueError(f"marime trebuie să fie cel puțin {256 + len(fixe) + len(speciale)}")
    if reguli == "ws":
        frecvente = {b: n for b, n in frecvente.items() if not (b.isascii() and b.isdigit())}
    if reguli == "cod":
        frecvente = {b: n for b, n in frecvente.items() if not _doar_spatii(b)}
    deja = set(fixe) if reguli == "cod" else set()  # o pereche fixă (ex. două spații între tab-uri) nu se învață a doua oară

    # 1. Bucățile, scrise ca octeți, și de câte ori apare fiecare.
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
    imbinari: list[tuple[int, int]] = list(fixe)
    while len(imbinari) < numar_imbinari and coada:
        minus_n, pereche = heapq.heappop(coada)
        if minus_n == 0 or -minus_n != perechi.get(pereche, 0) or pereche in deja:
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
    return TokenizerBPE(imbinari, speciale, reguli)
