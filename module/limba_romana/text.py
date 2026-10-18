"""Text: normalizare ortografică, segmentare în propoziții și cuvinte (tokenizare).

Reguli explicite, fără model neuronal:
  - sedilele vechi (ş, ţ) devin virgulele standard (ș, ț); â/î rămân cum sunt (ambele ortografii sunt în uz);
  - `normalizeaza` = minuscule + sedile corectate (așa se caută în bază);
  - `fara_diacritice` = forma „plată” (a, i, s, t, a) pentru texte scrise fără diacritice; potrivirea pe ea e
    raportată separat (nu e aceeași certitudine);
  - cliticele legate cu cratimă se despart ca în corpusul UD RRT: „s-o” → „s-” + „o”; „într-un” → „într-” + „un”;
    „dă-mi-l” → „dă” + „-mi” + „-l”; „ADN-ul”, „cd-ul” rămân întregi (cratimă în interiorul flexiunii);
  - numerele, datele, abrevierile cu punct și punctuația sunt tokeni separați.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

SEDILE = str.maketrans({"ş": "ș", "ţ": "ț", "Ş": "Ș", "Ţ": "Ț"})
PLAT = str.maketrans({"ă": "a", "â": "a", "î": "i", "ș": "s", "ț": "t", "Ă": "A", "Â": "A", "Î": "I", "Ș": "S", "Ț": "T"})

LITERE_RO = "a-zA-ZăâîșțĂÂÎȘȚ"


def corecteaza_sedile(text: str) -> str:
    return text.translate(SEDILE)


def normalizeaza(forma: str) -> str:
    """Minuscule + sedile corectate + NFC. Așa se caută formele în bază."""
    return unicodedata.normalize("NFC", corecteaza_sedile(forma)).casefold()


def fara_diacritice(forma: str) -> str:
    return normalizeaza(forma).translate(PLAT)


def are_diacritice(text: str) -> bool:
    return any(c in "ăâîșțĂÂÎȘȚşţŞŢ" for c in text)


# Cliticele care se leagă cu cratimă de alt cuvânt (după corpusul UD RRT: se despart, cratima rămâne pe clitic).
CLITICE_DUPA = {"mi", "ți", "i", "l", "o", "le", "ne", "vă", "se", "și", "mă", "te", "mi-l", "ți-l", "i-l", "ni", "vi", "li"}
CLITICE_INAINTE = {"s", "într", "dintr", "printr", "n", "m", "ți", "mi", "i", "l", "v", "ne", "le", "ș", "c", "d", "ne-", "v-"}
# Forme prescurtate care rămân lipite de cratimă în stânga: „s-” (să/se), „într-”, „dintr-”, „printr-”, „n-” (nu), „m-” (mă),
# „ți-”, „mi-”, „i-”, „l-”, „v-” (vă), „ne-”, „le-”, „ș-” (și), „c-” (că), „d-” (de). Alte legături cu cratimă rămân întregi.
PRESCURTATE_STANGA = {"s", "într", "dintr", "printr", "n", "m", "ți", "mi", "i", "l", "v", "ne", "le", "ș", "c", "d", "să", "se", "nu"}

RE_TOKEN = re.compile(
    r"(?P<ora>\d{1,2}:\d{2})"                                   # ore
    r"|(?P<numar>\d+(?:[.,]\d+)*(?:%|‰)?)"                      # numere: 12, 3,5, 1.000.000, 25%
    r"|(?P<abrev>(?:[A-ZĂÂÎȘȚ][a-zăâîșț]{0,3}\.)+)"               # abrevieri cu punct: dr. S.A. etc.
    r"|(?P<cuvant>[" + LITERE_RO + r"0-9]+(?:[-'’][" + LITERE_RO + r"0-9]+)*)"   # cuvinte, cu cratimă/apostrof în interior
    r"|(?P<cratima_clitic>-[" + LITERE_RO + r"]+)"               # clitic după cratimă rămas singur (rar)
    r"|(?P<punct>\.\.\.|…|[.,;:!?()\[\]{}„“”«»\"'’‘\-–—/%&+*=<>§@#])"
    r"|(?P<altceva>\S)"
)

RE_PROPOZITIE = re.compile(r"(?<=[.!?…])\s+(?=[„“\"(]?[A-ZĂÂÎȘȚ0-9])")
ABREVIERI_FARA_PAUZA = {"dr.", "prof.", "nr.", "str.", "etc.", "ex.", "pag.", "p.", "art.", "alin.", "lit.", "cca.", "aprox.", "sec.", "jud.", "sat.", "com.", "mun.", "bd.", "av."}


@dataclass
class Token:
    text: str
    inceput: int
    sfarsit: int
    tip: str                       # numar | ora | abrev | cuvant | clitic | punct | altceva
    spatiu_dupa: bool = True
    note: list[str] = field(default_factory=list)

    @property
    def norm(self) -> str:
        return normalizeaza(self.text)


def _desparte_cratima(text: str) -> list[str] | None:
    """Împarte un cuvânt cu cratimă în bucăți ca în UD RRT, sau None dacă rămâne întreg."""
    if "-" not in text or text.startswith("-") or text.endswith("-"):
        return None
    parti = text.split("-")
    rezultat: list[str] = []
    stanga = parti[0]
    # legături cu cratimă în interiorul flexiunii (ADN-ul, cd-ul, X-ului, pH-ul): rămân întregi
    if (stanga.isupper() and len(stanga) >= 2) or any(ch.isdigit() for ch in stanga):
        return None
    jos = normalizeaza(stanga)
    if jos in PRESCURTATE_STANGA and len(parti) >= 2:
        # s-o, într-un, n-am, m-a, i-a, l-am, v-am, ne-a, le-a, ș-apoi, c-un, d-aia, să-l, se-nvârte, nu-i
        rezultat.append(stanga + "-")
        rest = "-".join(parti[1:])
        sub = _desparte_cratima(rest)
        rezultat.extend(sub if sub else [rest])
        return rezultat
    # dă-mi, spune-mi-l, du-te, întreabă-l, face-se-va: clitice după verb
    if all(normalizeaza(p) in CLITICE_DUPA or normalizeaza(p) in {"va", "vei", "voi", "vom", "veți", "vor", "ar", "aș", "ai", "am", "ați", "ne", "ni", "vi", "li"} for p in parti[1:]):
        rezultat.append(stanga)
        for p in parti[1:]:
            rezultat.append("-" + p)
        return rezultat
    return None


def tokenizeaza(text: str) -> list[Token]:
    text = corecteaza_sedile(text)
    tokeni: list[Token] = []
    for m in RE_TOKEN.finditer(text):
        tip = m.lastgroup or "altceva"
        s, e = m.start(), m.end()
        bucata = m.group(0)
        if tip == "cuvant":
            parti = _desparte_cratima(bucata)
            if parti:
                poz = s
                for i, p in enumerate(parti):
                    tokeni.append(Token(p, poz, poz + len(p), "clitic" if (p.startswith("-") or p.endswith("-")) else "cuvant", spatiu_dupa=False))
                    poz += len(p)
                continue
        if tip == "abrev" and bucata.endswith(".") and bucata.lower() not in ABREVIERI_FARA_PAUZA and len(bucata) <= 2:
            # „A.” poate fi inițială; rămâne abreviere
            pass
        tokeni.append(Token(bucata, s, e, tip, spatiu_dupa=False))
    # spațiul după fiecare token (util la reconstruirea textului și la clitice)
    for i, t in enumerate(tokeni):
        urm = tokeni[i + 1].inceput if i + 1 < len(tokeni) else len(text)
        t.spatiu_dupa = any(ch.isspace() for ch in text[t.sfarsit:urm])
    return tokeni


def segmenteaza_propozitii(text: str) -> list[tuple[int, int, str]]:
    """Întoarce (început, sfârșit, text) pentru fiecare propoziție. Abrevierile uzuale nu rup propoziția."""
    text = corecteaza_sedile(text)
    rezultat: list[tuple[int, int, str]] = []
    inceput = 0
    for m in RE_PROPOZITIE.finditer(text):
        taietura = m.start()
        inainte = text[inceput:taietura].rstrip()
        ultimul = inainte.split()[-1].lower() if inainte.split() else ""
        if ultimul in ABREVIERI_FARA_PAUZA or (len(ultimul) == 2 and ultimul[0].isalpha() and ultimul.endswith(".")):
            continue
        bucata = text[inceput:taietura].strip()
        if bucata:
            rezultat.append((inceput, taietura, bucata))
        inceput = m.end()
    bucata = text[inceput:].strip()
    if bucata:
        rezultat.append((inceput, len(text), bucata))
    return rezultat
