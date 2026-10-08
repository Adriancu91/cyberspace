"""Testele ascunse ale școlii de cod (planul, secțiunea 5).

**Sarcinile.** Fiecare nivel (0, 1, 2A, 2B, 2C, 3A, 3B; din v0.2 și treptele 0a, 0b, 1a, 1b) are un generator de
sarcini cu parametri: numere, nume de cutii, cuvinte. Formulările sunt chiar cele din abecedar (unelte/fa_abecedar.py),
cu alte valori. Rezultatul așteptat se calculează rulând soluția noastră (ca în fa_abecedar.py). Soluția nu ajunge în
fața modelului. Singura excepție e linia D (control, v0.2): ea primește în antrenare soluțiile noastre la sarcini
văzute, nu propriile descoperiri.

**Seturile.** Patru pe nivel, cu semințe diferite, fără nicio sarcină comună între ele sau cu abecedarul:
- **văzut:** sarcinile rundelor de antrenare;
- **nevăzut:** aceleași forme, alte valori. Aici se decide trecerea nivelului;
- **adversarial:** valori alese să prindă scurtăturile: numere mari, neîntâlnite în abecedar (37 + 58), nume de cutii
  lungi, cuvinte lungi;
- **sacru:** 20 de sarcini fixe pe nivel, generate o dată în date/cod/sacru.json și amprentate de paznic. Se măsoară
  doar la îngheț, pentru raport, niciodată la selecție.

**Verificarea de formă**, pe lângă rezultat (altfel `print(5)` ar trece la „use print to show 2 plus 3”):
- de la nivelul 2: conține „print(”;
- la expresii: conține operatorul cerut;
- la cutii: conține „=” după numele fiecărei cutii.

**Verdictul unei încercări:** „trișat” (cod interzis, nici nu s-a rulat), „picat” (eroare, alt rezultat sau altă
formă) sau „trecut”.
"""

from __future__ import annotations

import json
import random
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from module.cod import PILOT
from module.cod.sandbox import Rulare, la_fel, ruleaza_in_proces

CUVINTE = ("ball", "tree", "fish", "milk", "book", "star", "rain", "frog", "cake", "bird", "lamp", "boat", "corn", "duck",
           "kite", "moon", "nest", "pear", "ring", "sock", "toy", "jam", "egg", "hat", "bee", "pig", "fox", "owl", "cup",
           "bus")
CUVINTE_LUNGI = ("elephant", "rainbow", "dinosaur", "umbrella", "butterfly", "pancake", "giraffe", "mountain", "pumpkin",
                 "treasure")
CUTII = tuple("abcdefghijkmnpqrstuvwxyz") + ("box", "bag", "pot", "jar", "can")
CUTII_LUNGI = ("apples", "basket", "pocket", "number", "counter", "biggest", "total", "candy", "garden", "rocket")
SETURI = ("vazut", "nevazut", "adversarial", "sacru")


@dataclass(frozen=True)
class Sarcina:
    nivel: str
    text: str                       # ce vede modelul după „TEST: ”
    asteptat: str                   # rezultatul corect (din rularea soluției)
    solutie: str                    # doar pentru noi: rezultatul așteptat și testele; niciodată în fața modelului
    cu_print: bool = False          # trebuie să conțină „print(”
    operator: str | None = None     # trebuie să conțină operatorul
    cutii: tuple[str, ...] = field(default_factory=tuple)  # trebuie să atribuie fiecare cutie („x = ...”)

    def ca_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def din_dict(cls, date: dict[str, Any]) -> Sarcina:
        return cls(**{**date, "cutii": tuple(date.get("cutii") or ())})


def _sarcina(nivel: str, text: str, solutie: str, **forma: Any) -> Sarcina:
    return Sarcina(nivel, text, ruleaza_in_proces(solutie), solutie, **forma)


# --- generatoarele (mare = valorile setului adversarial) -----------------------------------------------------------

def _numar(rng: random.Random, mare: bool) -> int:
    return rng.randint(100, 999) if mare else rng.randint(0, 99)


def _doua(rng: random.Random, mare: bool) -> tuple[int, int]:
    return (rng.randint(30, 99), rng.randint(30, 99)) if mare else (rng.randint(1, 12), rng.randint(1, 12))


def _scadere(rng: random.Random, mare: bool) -> tuple[int, int]:
    a = rng.randint(50, 99) if mare else rng.randint(2, 20)
    return a, (rng.randint(10, a - 1) if mare else rng.randint(1, a - 1))


def _cuvant(rng: random.Random, mare: bool) -> str:
    return rng.choice(CUVINTE_LUNGI if mare else CUVINTE)


def _cutie(rng: random.Random, mare: bool, fara: tuple[str, ...] = ()) -> str:
    return rng.choice([c for c in (CUTII_LUNGI if mare else CUTII) if c not in fara])


def _nivel_0(rng: random.Random, mare: bool) -> Sarcina:
    if rng.random() < 0.7:
        n = _numar(rng, mare)
        return _sarcina("0", f"show {n}", f"{n}")
    w = _cuvant(rng, mare)
    return _sarcina("0", f"show the word {w}", f'"{w}"')


def _nivel_1(rng: random.Random, mare: bool) -> Sarcina:
    fel = rng.choice("+-*")
    if fel == "-":
        a, b = _scadere(rng, mare)
        return _sarcina("1", f"take {b} from {a}", f"{a}-{b}", operator="-")
    a, b = _doua(rng, mare)
    if fel == "+":
        return _sarcina("1", f"add {a} and {b}", f"{a}+{b}", operator="+")
    return _sarcina("1", f"{a} times {b}", f"{a}*{b}", operator="*")


def _nivel_2a(rng: random.Random, mare: bool) -> Sarcina:
    if rng.random() < 0.7:
        n = _numar(rng, mare)
        return _sarcina("2A", f"use print to show {n}", f"print({n})", cu_print=True)
    w = _cuvant(rng, mare)
    return _sarcina("2A", f"use print to show the word {w}", f'print("{w}")', cu_print=True)


def _nivel_2b(rng: random.Random, mare: bool) -> Sarcina:
    a, b = _doua(rng, mare)
    return _sarcina("2B", f"use print to show {a} plus {b}", f"print({a}+{b})", cu_print=True, operator="+")


def _nivel_2c(rng: random.Random, mare: bool) -> Sarcina:
    a, b = _scadere(rng, mare)
    return _sarcina("2C", f"use print to show {a} minus {b}", f"print({a}-{b})", cu_print=True, operator="-")


def _nivel_3a(rng: random.Random, mare: bool) -> Sarcina:
    x = _cutie(rng, mare)
    n = rng.randint(30, 99) if mare else rng.randint(1, 20)
    fel = rng.choice(("", "", "+", "-", "*"))
    if not fel:
        return _sarcina("3A", f"put {n} in a box called {x}, then show {x}", f"{x} = {n}\nprint({x})",
                        cu_print=True, cutii=(x,))
    d = rng.randint(1, min(5, n - 1)) if fel == "-" and n > 1 else rng.randint(1, 5)
    cuvant = {"+": "plus", "-": "minus", "*": "times"}[fel]
    return _sarcina("3A", f"put {n} in {x}, then show {x} {cuvant} {d}", f"{x} = {n}\nprint({x}{fel}{d})",
                    cu_print=True, operator=fel, cutii=(x,))


def _nivel_3b(rng: random.Random, mare: bool) -> Sarcina:
    x = _cutie(rng, mare)
    y = _cutie(rng, mare, fara=(x,))
    fel = rng.choice("+-*")
    a, b = _scadere(rng, mare) if fel == "-" else _doua(rng, mare)
    cuvant = {"+": "plus", "-": "minus", "*": "times"}[fel]
    return _sarcina("3B", f"put {a} in {x} and {b} in {y}, then show {x} {cuvant} {y}",
                    f"{x} = {a}\n{y} = {b}\nprint({x}{fel}{y})", cu_print=True, operator=fel, cutii=(x, y))


# --- treptele intermediare (v0.2): numere de o cifră, apoi de două cifre --------------------------------------------
# Tokenizer-ul lui #252 taie orice număr în cifre: o cifră = o bucată, două cifre = două bucăți, trei cifre = trei.

def _nivel_0a(rng: random.Random, mare: bool) -> Sarcina:
    """Doar numere de o cifră. Sunt doar 10, iar 4 și 8 sunt în abecedar: seturile lui 0a sunt mici. Adversarial: trei
    cifre."""
    n = rng.randint(100, 999) if mare else rng.randint(0, 9)
    return _sarcina("0a", f"show {n}", f"{n}")


def _nivel_0b(rng: random.Random, mare: bool) -> Sarcina:
    """Numere de două cifre și cuvinte: nivelul 0 din v0.1, fără numerele de o cifră. Adversarial: ca la nivelul 0."""
    if rng.random() < 0.7:
        n = rng.randint(100, 999) if mare else rng.randint(10, 99)
        return _sarcina("0b", f"show {n}", f"{n}")
    w = _cuvant(rng, mare)
    return _sarcina("0b", f"show the word {w}", f'"{w}"')


def _aritmetica(nivel: str, rng: random.Random, operanzi: Callable[[random.Random], tuple[int, int]],
                scadere: Callable[[random.Random], tuple[int, int]]) -> Sarcina:
    fel = rng.choice("+-*")
    if fel == "-":
        a, b = scadere(rng)
        return _sarcina(nivel, f"take {b} from {a}", f"{a}-{b}", operator="-")
    a, b = operanzi(rng)
    if fel == "+":
        return _sarcina(nivel, f"add {a} and {b}", f"{a}+{b}", operator="+")
    return _sarcina(nivel, f"{a} times {b}", f"{a}*{b}", operator="*")


def _intre(lo: int, hi: int) -> tuple[Callable[[random.Random], tuple[int, int]],
                                      Callable[[random.Random], tuple[int, int]]]:
    """(doi operanzi între lo și hi; o scădere a − b cu amândoi între lo și hi și b < a)."""
    def operanzi(r: random.Random) -> tuple[int, int]:
        return r.randint(lo, hi), r.randint(lo, hi)

    def scadere(r: random.Random) -> tuple[int, int]:
        a = r.randint(lo + 1, hi)
        return a, r.randint(lo, a - 1)

    return operanzi, scadere


def _nivel_1a(rng: random.Random, mare: bool) -> Sarcina:
    """Operanzi de o cifră. Adversarial: ca la nivelul 1 din v0.1 (30–99)."""
    if mare:
        return _aritmetica("1a", rng, lambda r: _doua(r, True), lambda r: _scadere(r, True))
    return _aritmetica("1a", rng, *_intre(1, 9))


def _nivel_1b(rng: random.Random, mare: bool) -> Sarcina:
    """Operanzi de două cifre. Adversarial: trei cifre (două cifre e aici mărimea obișnuită)."""
    return _aritmetica("1b", rng, *(_intre(100, 999) if mare else _intre(10, 99)))


GENERATOARE: dict[str, Callable[[random.Random, bool], Sarcina]] = {
    "0": _nivel_0, "0a": _nivel_0a, "0b": _nivel_0b, "1": _nivel_1, "1a": _nivel_1a, "1b": _nivel_1b, "2A": _nivel_2a,
    "2B": _nivel_2b, "2C": _nivel_2c, "3A": _nivel_3a, "3B": _nivel_3b}


def generator(nivel: str) -> Callable[[random.Random, bool], Sarcina]:
    if nivel not in GENERATOARE:
        raise ValueError(f"nivelul {nivel} nu e activ (active: {', '.join(GENERATOARE)}); se activează de mână")
    return GENERATOARE[nivel]


def sarcini_unice(nivel: str, cate: int, samanta: str, mare: bool, fara: set[str]) -> list[Sarcina]:
    """`cate` sarcini diferite ale nivelului, fără textele din `fara` (abecedarul și celelalte seturi)."""
    rng, gen = random.Random(samanta), generator(nivel)
    alese: dict[str, Sarcina] = {}
    for _ in range(200 * cate):
        if len(alese) >= cate:
            break
        s = gen(rng, mare)
        if s.text not in fara and s.text not in alese:
            alese[s.text] = s
    if len(alese) < cate:
        raise ValueError(f"nivelul {nivel}: doar {len(alese)} sarcini diferite, din {cate} cerute")
    return list(alese.values())


# --- setul sacru (o singură dată, în date/cod/sacru.json) ------------------------------------------------------------

def genereaza_sacru(texte_abecedar: set[str], cate: int = 20, samanta: str = "sacru-v0.1",
                    niveluri: tuple[str, ...] = PILOT, marimi: dict[str, int] | None = None) -> dict[str, Any]:
    """`cate` sarcini fixe pe nivel (sau marimi[nivel], unde pool-ul e mic: 0a are doar 8 sarcini, deci 0 sacre)."""
    marimi = marimi or {}
    return {"versiune": 1, "data": datetime.now().isoformat(timespec="seconds"), "samanta": samanta,
            "nota": "Setul sacru al școlii de cod: se măsoară doar la îngheț, pentru raport; nu se folosește niciodată "
                    "la selecție și nu intră în antrenare.",
            "niveluri": {nivel: [s.ca_dict() for s in sarcini_unice(nivel, marimi.get(nivel, cate), f"{samanta}:{nivel}",
                                                                     False, texte_abecedar)] for nivel in niveluri}}


def adauga_sacru(date: dict[str, Any], texte_abecedar: set[str], niveluri: tuple[str, ...], cate: int, samanta: str,
                 marimi: dict[str, int] | None = None) -> list[str]:
    """Adaugă în setul sacru nivelurile care lipsesc. Cele existente rămân neatinse, sarcină cu sarcină. Întoarce
    nivelurile adăugate."""
    lipsa = tuple(n for n in niveluri if n not in date["niveluri"])
    if lipsa:
        date["niveluri"].update(genereaza_sacru(texte_abecedar, cate, samanta, lipsa, marimi)["niveluri"])
        date.setdefault("adaugari", []).append({"data": datetime.now().isoformat(timespec="seconds"),
                                                "samanta": samanta, "niveluri": list(lipsa)})
    return list(lipsa)


def citeste_sacru(cale: str | Path) -> dict[str, list[Sarcina]]:
    date = json.loads(Path(cale).read_text(encoding="utf-8"))
    return {nivel: [Sarcina.din_dict(s) for s in lista] for nivel, lista in date["niveluri"].items()}


# --- cele patru seturi ----------------------------------------------------------------------------------------------

@dataclass
class Seturi:
    vazut: list[Sarcina]
    nevazut: list[Sarcina]
    adversarial: list[Sarcina]
    sacru: list[Sarcina]

    def toate_textele(self) -> dict[str, set[str]]:
        return {nume: {s.text for s in getattr(self, nume)} for nume in SETURI}


def seturi(nivel: str, texte_abecedar: set[str], sacru: list[Sarcina], vazut: int = 60, nevazut: int = 20,
           adversarial: int = 20, samanta: str = "v0.1") -> Seturi:
    """Seturile unui nivel, mereu aceleași pentru aceeași sămânță: întâi sacrul (fix), apoi nevăzutul, adversarialul și
    văzutul, fiecare fără textele celor de dinainte și ale abecedarului."""
    fara = set(texte_abecedar) | {s.text for s in sacru}
    n = sarcini_unice(nivel, nevazut, f"{samanta}:nevazut:{nivel}", False, fara)
    fara |= {s.text for s in n}
    a = sarcini_unice(nivel, adversarial, f"{samanta}:adversarial:{nivel}", True, fara)
    fara |= {s.text for s in a}
    v = sarcini_unice(nivel, vazut, f"{samanta}:vazut:{nivel}", False, fara)
    return Seturi(v, n, a, list(sacru))


# --- verificarea și verdictul ---------------------------------------------------------------------------------------

def verifica_forma(sarcina: Sarcina, cod: str) -> str | None:
    """De ce nu are codul forma cerută de nivel, sau None."""
    if sarcina.cu_print and "print(" not in cod:
        return "lipsește „print(”"
    if sarcina.operator and sarcina.operator not in cod:
        return f"lipsește operatorul „{sarcina.operator}”"
    for cutie in sarcina.cutii:
        if not re.search(rf"(?<![\w.]){re.escape(cutie)}\s*=(?!=)", cod):
            return f"lipsește cutia „{cutie}” (cu „=”)"
    return None


def judeca(sarcina: Sarcina, cod: str, rulare: Rulare) -> tuple[str, str]:
    """(„trecut” / „picat” / „trișat”, motivul, în română)."""
    if rulare.trisat:
        return "trișat", f"cod interzis: „{rulare.trisat}”"
    if rulare.eroare:
        return "picat", rulare.eroare
    if not la_fel(rulare.iesire, sarcina.asteptat):
        return "picat", f"a ieșit {rulare.iesire.strip()[:40]!r}, trebuia {sarcina.asteptat!r}"
    forma = verifica_forma(sarcina, cod)
    if forma:
        return "picat", f"rezultat corect, dar {forma}"
    return "trecut", "rezultat corect și forma cerută"
