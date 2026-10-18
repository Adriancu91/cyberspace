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

def corecteaza_sedile(text: str) -> str:
    return text.translate(SEDILE)


def normalizeaza(forma: str) -> str:
    """Minuscule + sedile corectate + NFC. Așa se caută formele în bază."""
    return unicodedata.normalize("NFC", corecteaza_sedile(forma)).casefold()


def fara_diacritice(forma: str) -> str:
    return normalizeaza(forma).translate(PLAT)


def are_diacritice(text: str) -> bool:
    return any(c in "ăâîșțĂÂÎȘȚşţŞŢ" for c in text)


LITERA = r"[^\W\d_]"                       # orice literă Unicode (inclusiv ö, š…), fără cifre și _
LITERE_RO = r"^\W\d_"                       # același lucru, pentru clase de caractere construite în alte module
L = "(?:" + LITERA + ")"

# Convențiile de despărțire a cratimei (după corpusul UD RRT):
#   - formă elidată în stânga (s-a, n-am, l-am, într-un, p-ăsta): cratima rămâne pe stânga: „s-”, „a”;
#   - clitic pronominal în stânga + alt clitic pronominal în dreapta (și-l, mi-l): cratima trece pe dreapta: „și”, „-l”;
#   - cuvânt întreg în stânga (nu-i, să-și, ce-a, ca-n, la-nceput, dă-mi): cratima trece pe dreapta: „nu”, „-i”;
#   - sigle/cifre + articol (ADN-ul, pH-ului, 3-lea): cuvântul + „-ul”.
ELIDATE_STANGA = {"s", "n", "m", "l", "v", "c", "d", "p", "într", "dintr", "printr", "de"}
CLITICE_STANGA = {"ne", "le", "mi", "ți", "și", "i", "li", "ni", "vi", "te", "se", "mă", "vă"}   # clitice întregi: mi-a (mi-), și-l (și, -l), se-mbarcă (se, -mbarcă)
CLITICE_PRONOMINALE = {"l", "o", "le", "i", "mi", "ți", "ne", "vă", "se", "și", "mă", "te", "ni", "vi", "li"}
INTREGI_CU_CRATIMA = {"de-abia", "dintr-odată", "într-adevăr", "de-a", "vreo-"}  # rămân întregi (lexicalizate) — „de-a” se tratează separat
ARTICOLE_LEGATE = {"ul", "ului", "lui", "le", "lea", "a", "i", "ii", "ilor", "uri", "urile", "urilor", "ele", "elor", "lor", "u"}
ABREVIERI = {"dr", "nr", "str", "tel", "etc", "ex", "pag", "pg", "p", "pp", "art", "alin", "lit", "cca", "aprox", "sec", "jud", "com", "mun", "bd", "bld", "av",
             "prof", "ing", "dl", "dna", "dlui", "sf", "lt", "col", "vol", "cap", "fig", "tab", "op", "cit", "ed", "sos", "ș", "a", "m", "d", "e", "î",
             "s", "r", "l", "o", "u", "n", "c", "b", "f", "g", "h", "i", "j", "k", "t", "v", "w", "x", "y", "z", "mr", "mrs", "ms", "st", "jr", "sr", "no", "max", "min",
             "mil", "mld", "obs", "ro", "en", "pct", "lect", "conf", "univ", "acad", "dpdv", "resp", "cf", "vs", "ş", "prep", "th", "al", "gh", "ch", "sg", "pl"}

RE_TOKEN = re.compile(
    r"(?P<ora>\d{1,2}:\d{2})"                                       # ore
    r"|(?P<cuvant_cifre>\d+(?:[-]" + L + r"+)+)"                     # 17-beta, 3-lea, 2020-ul (cifre + cratimă + litere)
    r"|(?P<numar>(?:\d+(?:[.,]\d+)+\.?|\d+[–-]\d+|’\d+|\d+)(?:%|‰)?)"   # 3,5  1.000  3.4.2.2.  1878–1879  ’70  25%  1,5%
    r"|(?P<abrev>(?:" + L + r"\.){2,}" + L + r"?\.?)"                # S.A., ș.a.m.d., a.c.
    r"|(?P<cuvant>(?:" + L + r"|\d)+(?:[-'’](?:" + L + r"|\d)+)*\.?)"   # cuvinte și coduri (H7N3, pH), cu cratimă/apostrof; punctul final → abrevieri
    r"|(?P<cratima_clitic>-" + L + r"+)"                             # clitic după cratimă rămas singur (rar)
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
    if normalizeaza(text) in INTREGI_CU_CRATIMA and normalizeaza(text) != "de-a":
        return None
    parti = text.split("-")
    stanga, rest = parti[0], parti[1:]
    jos = normalizeaza(stanga)
    # sigle / cifre / cuvinte străine + articol legat (ADN-ul, pH-ului, 3-lea, site-ul): cuvântul + „-ul”
    if len(parti) == 2 and normalizeaza(parti[1]) in ARTICOLE_LEGATE and jos not in ELIDATE_STANGA and jos not in CLITICE_STANGA and len(stanga) >= 2:
        return [stanga, "-" + parti[1]]
    if any(ch.isupper() for ch in stanga[1:]) or any(ch.isdigit() for ch in stanga) or (stanga.isupper() and len(stanga) >= 2):
        return None
    if jos == "de" and len(parti) == 2 and normalizeaza(parti[1]) == "a":
        return ["de-", "a"]                                     # de-a lungul (UD RRT)
    if len(stanga) == 1 and rest and rest[0][:1].isupper():
        return None                                             # L-Dopa, T-shirt
    if jos in ELIDATE_STANGA and len(rest) >= 1:
        rez = [stanga + "-"]                                    # s-a, s-o, n-am, l-am, într-o, dintr-un, p-ăsta
        sub = _desparte_cratima("-".join(rest))
        rez.extend(sub if sub else ["-".join(rest)])
        return rez
    if jos in CLITICE_STANGA and len(rest) >= 1 and normalizeaza(rest[0]) in FORME_AUX - CLITICE_PRONOMINALE | {"a", "am", "ai", "au", "ați", "aș", "ar", "o", "oi", "or", "om", "va", "vei", "voi", "vom", "veți", "vor"}:
        rez = [stanga + "-"]                                    # mi-a, și-a, ne-am, le-am, te-am (clitic + auxiliar: cratima pe clitic)
        sub = _desparte_cratima("-".join(rest))
        rez.extend(sub if sub else ["-".join(rest)])
        return rez
    if jos in CLITICE_STANGA and len(rest) >= 1:
        return [stanga] + ["-" + r for r in rest]               # și-l, mi-l, ți-l, se-mbarcă (al doilea element ia cratima)
    # cuvânt întreg în stânga: cliticele / auxiliarele / forma elidată de după iau cratima (nu-i, să-și, ce-a, ca-n, la-nceput, dă-mi-l)
    if all(_este_clitic_sau_elidat(r) for r in rest):
        return [stanga] + ["-" + r for r in rest]
    return None


FORME_AUX = {"a", "am", "ai", "au", "ați", "aș", "ar", "o", "oi", "or", "om", "va", "vei", "voi", "vom", "veți", "vor", "i", "s", "l", "n", "mi", "ți", "și"}
DEMONSTRATIVE_POPULARE = {"ăsta", "asta", "ăla", "aia", "astea", "ăștia", "ăia", "alea", "așa", "acasă", "atât", "atâta", "aici"}


def _este_clitic_sau_elidat(bucata: str) -> bool:
    b = normalizeaza(bucata)
    if b in CLITICE_PRONOMINALE or b in FORME_AUX or b in DEMONSTRATIVE_POPULARE:
        return True
    # formă cu î elidat la început (-nceput, -mpotriva, -n) sau cuvânt care începe cu vocală (ce-a, și-abia, toate-așa: eliziunea stângii)
    if len(b) >= 1 and b[0] in "nm" and (len(b) == 1 or b[1] not in "aeiouăâî"):
        return True
    return len(b) >= 1 and b[0] in "aeiouăâî"


def tokenizeaza(text: str) -> list[Token]:
    text = corecteaza_sedile(text)
    tokeni: list[Token] = []
    m0 = re.match(r"\s*(\d+\.)(?=\s+\S)", text)
    if m0:
        tokeni.append(Token(m0.group(1), m0.start(1), m0.end(1), "numar", spatiu_dupa=True))
    for m in RE_TOKEN.finditer(text, m0.end(1) if m0 else 0):
        tip = m.lastgroup or "altceva"
        s, e = m.start(), m.end()
        bucata = m.group(0)
        if tip == "cuvant_cifre":
            tip = "cuvant"
        if tip == "cuvant" and bucata.endswith("."):
            # „Cruz.” = nume + punct; „dr.”, „nr.”, „tel.” = abrevieri cunoscute; „A.” = inițială
            radacina = bucata[:-1]
            if normalizeaza(radacina) in ABREVIERI or (len(radacina) == 1 and radacina.isupper()):
                tip = "abrev"
            else:
                bucata = radacina
                e = s + len(radacina)
                tokeni.append(Token(bucata, s, e, "cuvant", spatiu_dupa=False)) if not _desparte_cratima(bucata) else None
                if _desparte_cratima(bucata):
                    poz = s
                    for p_ in _desparte_cratima(bucata):
                        tokeni.append(Token(p_, poz, poz + len(p_), "clitic" if (p_.startswith("-") or p_.endswith("-")) else "cuvant", spatiu_dupa=False))
                        poz += len(p_)
                tokeni.append(Token(".", e, e + 1, "punct", spatiu_dupa=False))
                continue
        if tip == "cuvant":
            parti = _desparte_cratima(bucata)
            if parti:
                poz = s
                for i, p in enumerate(parti):
                    tokeni.append(Token(p, poz, poz + len(p), "clitic" if (p.startswith("-") or p.endswith("-")) else "cuvant", spatiu_dupa=False))
                    poz += len(p)
                continue
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
