"""Clasele închise ale limbii române, scrise explicit: pronume, determinanți și articole, numerale, verbe auxiliare,
particule, prepoziții (cu cazul cerut), conjuncții.

Fiecare formă are trăsături în convenția UD RRT (vezi `trasaturi.py`), ca să se compare direct cu corpusul.
Sursa de documentare: gramatica standard a limbii române (GALR, Academia Română, 2005/2008) și convențiile
corpusului UD RRT; tabelele de mai jos sunt scrise de mână (nu copiate) și au statutul „atestare:tabel_propriu”.
Când o formă apare și în corpus, statutul ei devine „validat”.

Formele pronominale neaccentuate (cliticele) primesc automat variantele cu cratimă, ca în UD RRT:
  - după verb: „spune-mi”, „dă-l” → „-mi”, „-l” (Variant=Short);
  - înaintea verbului, cu elidare: „mi-a spus”, „l-am văzut”, „s-a dus” → „mi-”, „l-”, „s-” (Variant=Short).
"""

from __future__ import annotations

import json

from ..baza import Baza, canonic_trasaturi
from ..importatoare.comun import lexeme_tinta
from ..text import normalizeaza

SURSA_ID = "rlc_reguli"

P = "PronType=Prs"

# ---- pronume personale: (lemă UD, formă, trăsături) ----------------------------------------------------------
PRONUME_PERSONALE: list[tuple[str, str, str]] = [
    ("eu", "eu", f"Case=Nom|Number=Sing|Person=1|{P}|Strength=Strong"),
    ("eu", "mine", f"Case=Acc|Number=Sing|Person=1|{P}|Strength=Strong"),
    ("eu", "mie", f"Case=Dat|Number=Sing|Person=1|{P}|Strength=Strong"),
    ("eu", "mă", f"Case=Acc|Number=Sing|Person=1|{P}|Strength=Weak"),
    ("eu", "îmi", f"Case=Dat|Number=Sing|Person=1|{P}|Strength=Weak"),
    ("eu", "mi", f"Case=Dat|Number=Sing|Person=1|{P}|Strength=Weak"),
    ("eu", "noi", f"Case=Acc,Nom|Number=Plur|Person=1|{P}|Strength=Strong"),
    ("eu", "nouă", f"Case=Dat|Number=Plur|Person=1|{P}|Strength=Strong"),
    ("eu", "ne", f"Case=Acc|Number=Plur|Person=1|{P}|Strength=Weak"),
    ("eu", "ne", f"Case=Dat|Number=Plur|Person=1|{P}|Strength=Weak"),
    ("eu", "ni", f"Case=Dat|Number=Plur|Person=1|{P}|Strength=Weak"),
    ("tu", "tu", f"Case=Nom|Number=Sing|Person=2|{P}|Strength=Strong"),
    ("tu", "tine", f"Case=Acc|Number=Sing|Person=2|{P}|Strength=Strong"),
    ("tu", "ție", f"Case=Dat|Number=Sing|Person=2|{P}|Strength=Strong"),
    ("tu", "te", f"Case=Acc|Number=Sing|Person=2|{P}|Strength=Weak"),
    ("tu", "îți", f"Case=Dat|Number=Sing|Person=2|{P}|Strength=Weak"),
    ("tu", "ți", f"Case=Dat|Number=Sing|Person=2|{P}|Strength=Weak"),
    ("tu", "voi", f"Case=Acc,Nom|Number=Plur|Person=2|{P}|Strength=Strong"),
    ("tu", "vouă", f"Case=Dat|Number=Plur|Person=2|{P}|Strength=Strong"),
    ("tu", "vă", f"Case=Acc|Number=Plur|Person=2|{P}|Strength=Weak"),
    ("tu", "vă", f"Case=Dat|Number=Plur|Person=2|{P}|Strength=Weak"),
    ("tu", "vi", f"Case=Dat|Number=Plur|Person=2|{P}|Strength=Weak"),
    ("el", "el", f"Case=Acc,Nom|Gender=Masc|Number=Sing|Person=3|{P}|Strength=Strong"),
    ("el", "lui", f"Case=Dat,Gen|Gender=Masc|Number=Sing|Person=3|{P}|Strength=Strong"),
    ("el", "îl", f"Case=Acc|Gender=Masc|Number=Sing|Person=3|{P}|Strength=Weak"),
    ("el", "îi", f"Case=Dat|Number=Sing|Person=3|{P}|Strength=Weak"),
    ("el", "i", f"Case=Dat|Number=Sing|Person=3|{P}|Strength=Weak"),
    ("el", "ea", f"Case=Acc,Nom|Gender=Fem|Number=Sing|Person=3|{P}|Strength=Strong"),
    ("el", "ei", f"Case=Dat,Gen|Gender=Fem|Number=Sing|Person=3|{P}|Strength=Strong"),
    ("el", "o", f"Case=Acc|Gender=Fem|Number=Sing|Person=3|{P}|Strength=Weak"),
    ("el", "ei", f"Case=Acc,Nom|Gender=Masc|Number=Plur|Person=3|{P}|Strength=Strong"),
    ("el", "îi", f"Case=Acc|Gender=Masc|Number=Plur|Person=3|{P}|Strength=Weak"),
    ("el", "ele", f"Case=Acc,Nom|Gender=Fem|Number=Plur|Person=3|{P}|Strength=Strong"),
    ("el", "le", f"Case=Acc|Gender=Fem|Number=Plur|Person=3|{P}|Strength=Weak"),
    ("el", "lor", f"Case=Dat,Gen|Number=Plur|Person=3|{P}|Strength=Strong"),
    ("el", "le", f"Case=Dat|Number=Plur|Person=3|{P}|Strength=Weak"),
    ("el", "li", f"Case=Dat|Number=Plur|Person=3|{P}|Strength=Weak"),
    ("sine", "sine", f"Case=Acc|Person=3|{P}|Reflex=Yes|Strength=Strong"),
    ("sine", "sieși", f"Case=Dat|Person=3|{P}|Reflex=Yes|Strength=Strong"),
    ("sine", "se", f"Case=Acc|Person=3|{P}|Reflex=Yes|Strength=Weak"),
    ("sine", "își", f"Case=Dat|Person=3|{P}|Reflex=Yes|Strength=Weak"),
    ("sine", "și", f"Case=Dat|Person=3|{P}|Reflex=Yes|Strength=Weak"),
    ("dumneavoastră", "dumneavoastră", f"Person=2|{P}|Strength=Strong"),
    ("dumneata", "dumneata", f"Case=Acc,Nom|Number=Sing|Person=2|{P}|Strength=Strong"),
    ("dumneata", "dumitale", f"Case=Dat,Gen|Number=Sing|Person=2|{P}|Strength=Strong"),
    ("dumnealui", "dumnealui", f"Gender=Masc|Number=Sing|Person=3|{P}|Strength=Strong"),
    ("dumnealui", "dumneaei", f"Gender=Fem|Number=Sing|Person=3|{P}|Strength=Strong"),
    ("dumnealui", "dumnealor", f"Number=Plur|Person=3|{P}|Strength=Strong"),
    ("dânsul", "dânsul", f"Case=Acc,Nom|Gender=Masc|Number=Sing|Person=3|{P}|Strength=Strong"),
    ("dânsul", "dânsa", f"Case=Acc,Nom|Gender=Fem|Number=Sing|Person=3|{P}|Strength=Strong"),
    ("dânsul", "dânșii", f"Case=Acc,Nom|Gender=Masc|Number=Plur|Person=3|{P}|Strength=Strong"),
    ("dânsul", "dânsele", f"Case=Acc,Nom|Gender=Fem|Number=Plur|Person=3|{P}|Strength=Strong"),
    ("dânsul", "dânsului", f"Case=Dat,Gen|Gender=Masc|Number=Sing|Person=3|{P}|Strength=Strong"),
    ("dânsul", "dânsei", f"Case=Dat,Gen|Gender=Fem|Number=Sing|Person=3|{P}|Strength=Strong"),
    ("dânsul", "dânșilor", f"Case=Dat,Gen|Gender=Masc|Number=Plur|Person=3|{P}|Strength=Strong"),
    ("dânsul", "dânselor", f"Case=Dat,Gen|Gender=Fem|Number=Plur|Person=3|{P}|Strength=Strong"),
]

# cliticele: forma plină → (forma de după verb cu cratimă, forma de dinaintea verbului cu cratimă)
CLITICE: dict[str, tuple[str, str]] = {
    "mă": ("-mă", "m-"), "îmi": ("-mi", "mi-"), "mi": ("-mi", "mi-"), "ne": ("-ne", "ne-"), "ni": ("-ni", "ni-"),
    "te": ("-te", "te-"), "îți": ("-ți", "ți-"), "ți": ("-ți", "ți-"), "vă": ("-vă", "v-"), "vi": ("-vi", "vi-"),
    "îl": ("-l", "l-"), "îi": ("-i", "i-"), "i": ("-i", "i-"), "o": ("-o", "o-"), "le": ("-le", "le-"), "li": ("-li", "li-"),
    "se": ("-se", "s-"), "își": ("-și", "și-"), "și": ("-și", "și-"),
}

# ---- posesive (DET și PRON au aceleași forme; UD le pune la DET când însoțesc un substantiv) ---------------------
POSESIVE: list[tuple[str, str, str]] = []
for lema, pers, forme in (
    ("meu", "1", {"Sing": ("meu", "mea", "mei", "mele"), "Plur": ("nostru", "noastră", "noștri", "noastre")}),
    ("tău", "2", {"Sing": ("tău", "ta", "tăi", "tale"), "Plur": ("vostru", "voastră", "voștri", "voastre")}),
    ("său", "3", {"Sing": ("său", "sa", "săi", "sale")}),
):
    for psor, (m_sg, f_sg, m_pl, f_pl) in forme.items():
        baza_tr = f"Number[psor]={psor}|Person={pers}|Poss=Yes|{P}"
        POSESIVE += [
            (lema, m_sg, f"Gender=Masc|Number=Sing|{baza_tr}"),
            (lema, f_sg, f"Case=Acc,Nom|Gender=Fem|Number=Sing|{baza_tr}"),
            (lema, f_pl, f"Case=Dat,Gen|Gender=Fem|Number=Sing|{baza_tr}"),
            (lema, m_pl, f"Gender=Masc|Number=Plur|{baza_tr}"),
            (lema, f_pl, f"Gender=Fem|Number=Plur|{baza_tr}"),
        ]

# ---- demonstrative: (lemă, [(formă, Gender, Number, Case)], tip, poziție) ---------------------------------------
def _dem(lema: str, forme: list[tuple[str, str, str, str]], pozitie: str | None, pos: str, tip: str = "Dem") -> list[tuple[str, str, str, str]]:
    rez = []
    for forma, gen, numar, caz in forme:
        tr = {"Case": caz, "Person": "3", "PronType": tip}
        if gen:
            tr["Gender"] = gen
        if numar:
            tr["Number"] = numar
        if pozitie:
            tr["Position"] = pozitie
        rez.append((pos, lema, forma, canonic_trasaturi(tr)))
    return rez

AN, DG = "Acc,Nom", "Dat,Gen"
DEMONSTRATIVE: list[tuple[str, str, str, str]] = (
    _dem("acest", [("acest", "Masc", "Sing", AN), ("această", "Fem", "Sing", AN), ("acești", "Masc", "Plur", AN), ("aceste", "Fem", "Plur", AN),
                   ("acestui", "Masc", "Sing", DG), ("acestei", "Fem", "Sing", DG), ("acestor", "", "Plur", DG)], "Prenom", "DET")
    + _dem("acesta", [("acesta", "Masc", "Sing", AN), ("aceasta", "Fem", "Sing", AN), ("aceștia", "Masc", "Plur", AN), ("acestea", "Fem", "Plur", AN),
                      ("acestuia", "Masc", "Sing", DG), ("acesteia", "Fem", "Sing", DG), ("acestora", "", "Plur", DG),
                      ("ăsta", "Masc", "Sing", AN), ("asta", "Fem", "Sing", AN), ("ăștia", "Masc", "Plur", AN), ("astea", "Fem", "Plur", AN),
                      ("ăstuia", "Masc", "Sing", DG), ("ăsteia", "Fem", "Sing", DG), ("ăstora", "", "Plur", DG)], "Postnom", "DET")
    + _dem("acesta", [("acesta", "Masc", "Sing", AN), ("aceasta", "Fem", "Sing", AN), ("aceștia", "Masc", "Plur", AN), ("acestea", "Fem", "Plur", AN),
                      ("acestuia", "Masc", "Sing", DG), ("acesteia", "Fem", "Sing", DG), ("acestora", "", "Plur", DG),
                      ("ăsta", "Masc", "Sing", AN), ("asta", "Fem", "Sing", AN), ("ăștia", "Masc", "Plur", AN), ("astea", "Fem", "Plur", AN)], None, "PRON")
    + _dem("acel", [("acel", "Masc", "Sing", AN), ("acea", "Fem", "Sing", AN), ("acei", "Masc", "Plur", AN), ("acele", "Fem", "Plur", AN),
                    ("acelui", "Masc", "Sing", DG), ("acelei", "Fem", "Sing", DG), ("acelor", "", "Plur", DG)], "Prenom", "DET")
    + _dem("acela", [("acela", "Masc", "Sing", AN), ("aceea", "Fem", "Sing", AN), ("aceia", "Masc", "Plur", AN), ("acelea", "Fem", "Plur", AN),
                     ("aceluia", "Masc", "Sing", DG), ("aceleia", "Fem", "Sing", DG), ("acelora", "", "Plur", DG),
                     ("ăla", "Masc", "Sing", AN), ("aia", "Fem", "Sing", AN), ("ăia", "Masc", "Plur", AN), ("alea", "Fem", "Plur", AN),
                     ("ăluia", "Masc", "Sing", DG), ("ăleia", "Fem", "Sing", DG), ("ălora", "", "Plur", DG)], "Postnom", "DET")
    + _dem("acela", [("acela", "Masc", "Sing", AN), ("aceea", "Fem", "Sing", AN), ("aceia", "Masc", "Plur", AN), ("acelea", "Fem", "Plur", AN),
                     ("aceluia", "Masc", "Sing", DG), ("aceleia", "Fem", "Sing", DG), ("acelora", "", "Plur", DG),
                     ("ăla", "Masc", "Sing", AN), ("aia", "Fem", "Sing", AN), ("ăia", "Masc", "Plur", AN), ("alea", "Fem", "Plur", AN),
                     ("cel", "Masc", "Sing", AN), ("cea", "Fem", "Sing", AN), ("cei", "Masc", "Plur", AN), ("cele", "Fem", "Plur", AN),
                     ("celui", "Masc", "Sing", DG), ("celei", "Fem", "Sing", DG), ("celor", "", "Plur", DG), ("ceea", "Fem", "Sing", AN)], None, "PRON")
    + _dem("același", [("același", "Masc", "Sing", AN), ("aceeași", "Fem", "Sing", AN), ("aceiași", "Masc", "Plur", AN), ("aceleași", "Fem", "Plur", AN),
                       ("aceluiași", "Masc", "Sing", DG), ("aceleiași", "Fem", "Sing", DG), ("acelorași", "", "Plur", DG)], "Prenom", "DET")
    + _dem("același", [("același", "Masc", "Sing", AN), ("aceeași", "Fem", "Sing", AN), ("aceiași", "Masc", "Plur", AN), ("aceleași", "Fem", "Plur", AN),
                       ("aceluiași", "Masc", "Sing", DG), ("aceleiași", "Fem", "Sing", DG), ("acelorași", "", "Plur", DG)], None, "PRON")
    + _dem("celălalt", [("celălalt", "Masc", "Sing", AN), ("cealaltă", "Fem", "Sing", AN), ("ceilalți", "Masc", "Plur", AN), ("celelalte", "Fem", "Plur", AN),
                        ("celuilalt", "Masc", "Sing", DG), ("celeilalte", "Fem", "Sing", DG), ("celorlalți", "Masc", "Plur", DG), ("celorlalte", "Fem", "Plur", DG)], None, "DET")
    + _dem("celălalt", [("celălalt", "Masc", "Sing", AN), ("cealaltă", "Fem", "Sing", AN), ("ceilalți", "Masc", "Plur", AN), ("celelalte", "Fem", "Plur", AN),
                        ("celuilalt", "Masc", "Sing", DG), ("celeilalte", "Fem", "Sing", DG), ("celorlalți", "Masc", "Plur", DG), ("celorlalte", "Fem", "Plur", DG)], None, "PRON")
)

# articolul demonstrativ (adjectival) „cel” și articolul posesiv-genitival „al”: DET fără Person, ca în UD
ARTICOLE: list[tuple[str, str, str, str]] = [
    ("DET", "cel", "cel", "Case=Acc,Nom|Gender=Masc|Number=Sing|PronType=Dem"),
    ("DET", "cel", "cea", "Case=Acc,Nom|Gender=Fem|Number=Sing|PronType=Dem"),
    ("DET", "cel", "cei", "Case=Acc,Nom|Gender=Masc|Number=Plur|PronType=Dem"),
    ("DET", "cel", "cele", "Case=Acc,Nom|Gender=Fem|Number=Plur|PronType=Dem"),
    ("DET", "cel", "celui", "Case=Dat,Gen|Gender=Masc|Number=Sing|PronType=Dem"),
    ("DET", "cel", "celei", "Case=Dat,Gen|Gender=Fem|Number=Sing|PronType=Dem"),
    ("DET", "cel", "celor", "Case=Dat,Gen|Number=Plur|PronType=Dem"),
    ("DET", "al", "al", f"Gender=Masc|Number=Sing|Poss=Yes|{P}"),
    ("DET", "al", "a", f"Gender=Fem|Number=Sing|Poss=Yes|{P}"),
    ("DET", "al", "ai", f"Gender=Masc|Number=Plur|Poss=Yes|{P}"),
    ("DET", "al", "ale", f"Gender=Fem|Number=Plur|Poss=Yes|{P}"),
    ("DET", "al", "alor", f"Case=Dat,Gen|Number=Plur|Poss=Yes|{P}"),
    ("DET", "un", "un", "Case=Acc,Nom|Gender=Masc|Number=Sing|PronType=Ind"),
    ("DET", "un", "o", "Case=Acc,Nom|Gender=Fem|Number=Sing|PronType=Ind"),
    ("DET", "un", "unui", "Case=Dat,Gen|Gender=Masc|Number=Sing|PronType=Ind"),
    ("DET", "un", "unei", "Case=Dat,Gen|Gender=Fem|Number=Sing|PronType=Ind"),
    ("DET", "un", "unor", "Case=Dat,Gen|Number=Plur|PronType=Ind"),
    ("DET", "un", "unii", "Case=Acc,Nom|Gender=Masc|Number=Plur|Person=3|Position=Prenom|PronType=Ind"),
    ("DET", "un", "unele", "Case=Acc,Nom|Gender=Fem|Number=Plur|Person=3|Position=Prenom|PronType=Ind"),
    ("DET", "niște", "niște", "Person=3|PronType=Ind"),
    ("DET", "lui", "lui", "Case=Dat,Gen|Definite=Def|Number=Sing|PronType=Art"),
]

# nehotărâte, negative, interogativ-relative, de întărire (DET prenominal și PRON)
def _ind(lema: str, forme: list[tuple[str, str, str, str]], pos: str, tip: str, pozitie: str | None = "Prenom") -> list[tuple[str, str, str, str]]:
    return _dem(lema, forme, pozitie if pos == "DET" else None, pos, tip)

NEHOTARATE: list[tuple[str, str, str, str]] = (
    _ind("alt", [("alt", "Masc", "Sing", AN), ("altă", "Fem", "Sing", AN), ("alți", "Masc", "Plur", AN), ("alte", "Fem", "Plur", AN),
                 ("altui", "Masc", "Sing", DG), ("altei", "Fem", "Sing", DG), ("altor", "", "Plur", DG)], "DET", "Ind")
    + _ind("altul", [("altul", "Masc", "Sing", AN), ("alta", "Fem", "Sing", AN), ("alții", "Masc", "Plur", AN), ("altele", "Fem", "Plur", AN),
                     ("altuia", "Masc", "Sing", DG), ("alteia", "Fem", "Sing", DG), ("altora", "", "Plur", DG)], "PRON", "Ind")
    + _ind("unul", [("unul", "Masc", "Sing", AN), ("una", "Fem", "Sing", AN), ("unii", "Masc", "Plur", AN), ("unele", "Fem", "Plur", AN),
                    ("unuia", "Masc", "Sing", DG), ("uneia", "Fem", "Sing", DG), ("unora", "", "Plur", DG)], "PRON", "Ind")
    + _ind("tot", [("tot", "Masc", "Sing", AN), ("toată", "Fem", "Sing", AN), ("toți", "Masc", "Plur", AN), ("toate", "Fem", "Plur", AN),
                   ("tuturor", "", "Plur", DG)], "DET", "Ind", None)
    + _ind("tot", [("tot", "Masc", "Sing", AN), ("totul", "Masc", "Sing", AN), ("toată", "Fem", "Sing", AN), ("toți", "Masc", "Plur", AN),
                   ("toate", "Fem", "Plur", AN), ("tuturor", "", "Plur", DG), ("tuturora", "", "Plur", DG)], "PRON", "Ind")
    + _ind("fiecare", [("fiecare", "", "Sing", AN), ("fiecărui", "Masc", "Sing", DG), ("fiecărei", "Fem", "Sing", DG)], "DET", "Ind")
    + _ind("fiecare", [("fiecare", "", "Sing", AN), ("fiecăruia", "Masc", "Sing", DG), ("fiecăreia", "Fem", "Sing", DG)], "PRON", "Ind")
    + _ind("orice", [("orice", "", "", AN)], "DET", "Ind") + _ind("orice", [("orice", "", "Sing", AN)], "PRON", "Ind")
    + _ind("oricare", [("oricare", "", "", AN), ("oricărui", "Masc", "Sing", DG), ("oricărei", "Fem", "Sing", DG), ("oricăror", "", "Plur", DG)], "DET", "Ind")
    + _ind("oricare", [("oricare", "", "", AN), ("oricăruia", "Masc", "Sing", DG), ("oricăreia", "Fem", "Sing", DG), ("oricărora", "", "Plur", DG)], "PRON", "Ind")
    + _ind("vreun", [("vreun", "Masc", "Sing", AN), ("vreo", "Fem", "Sing", AN), ("vreunui", "Masc", "Sing", DG), ("vreunei", "Fem", "Sing", DG)], "DET", "Ind")
    + _ind("vreunul", [("vreunul", "Masc", "Sing", AN), ("vreuna", "Fem", "Sing", AN), ("vreunuia", "Masc", "Sing", DG), ("vreuneia", "Fem", "Sing", DG)], "PRON", "Ind")
    + _ind("câtva", [("câtva", "Masc", "Sing", AN), ("câtăva", "Fem", "Sing", AN), ("câțiva", "Masc", "Plur", AN), ("câteva", "Fem", "Plur", AN), ("câtorva", "", "Plur", DG)], "DET", "Ind", None)
    + _ind("mult", [("mult", "Masc", "Sing", AN), ("multă", "Fem", "Sing", AN), ("mulți", "Masc", "Plur", AN), ("multe", "Fem", "Plur", AN), ("multor", "", "Plur", DG)], "DET", "Ind", None)
    + _ind("puțin", [("puțin", "Masc", "Sing", AN), ("puțină", "Fem", "Sing", AN), ("puțini", "Masc", "Plur", AN), ("puține", "Fem", "Plur", AN), ("puținor", "", "Plur", DG)], "DET", "Ind", None)
    + _ind("atât", [("atât", "Masc", "Sing", AN), ("atâta", "", "Sing", AN), ("atâția", "Masc", "Plur", AN), ("atâtea", "Fem", "Plur", AN), ("atâtor", "", "Plur", DG)], "DET", "Ind", None)
    + _ind("anumit", [("anumit", "Masc", "Sing", AN), ("anumită", "Fem", "Sing", AN), ("anumiți", "Masc", "Plur", AN), ("anumite", "Fem", "Plur", AN), ("anumitor", "", "Plur", DG)], "DET", "Ind", None)
    + _ind("destul", [("destul", "Masc", "Sing", AN), ("destulă", "Fem", "Sing", AN), ("destui", "Masc", "Plur", AN), ("destule", "Fem", "Plur", AN)], "DET", "Ind", None)
    + _ind("cutare", [("cutare", "", "", AN)], "DET", "Ind") + _ind("oarecare", [("oarecare", "", "", AN)], "DET", "Ind", None)
    + _ind("cineva", [("cineva", "", "Sing", AN), ("cuiva", "", "Sing", DG)], "PRON", "Ind")
    + _ind("ceva", [("ceva", "", "Sing", AN)], "PRON", "Ind") + _ind("altceva", [("altceva", "", "Sing", AN)], "PRON", "Ind")
    + _ind("altcineva", [("altcineva", "", "Sing", AN), ("altcuiva", "", "Sing", DG)], "PRON", "Ind")
    + _ind("oricine", [("oricine", "", "Sing", AN), ("oricui", "", "Sing", DG)], "PRON", "Ind")
    + _ind("niciun", [("niciun", "Masc", "Sing", AN), ("nicio", "Fem", "Sing", AN), ("niciunui", "Masc", "Sing", DG), ("niciunei", "Fem", "Sing", DG)], "DET", "Neg")
    + _ind("niciunul", [("niciunul", "Masc", "Sing", AN), ("niciuna", "Fem", "Sing", AN), ("niciunuia", "Masc", "Sing", DG), ("niciuneia", "Fem", "Sing", DG)], "PRON", "Neg")
    + _ind("nimeni", [("nimeni", "", "Sing", AN), ("nimănui", "", "Sing", DG)], "PRON", "Neg")
    + _ind("nimic", [("nimic", "", "Sing", AN)], "PRON", "Neg")
    + _ind("care", [("care", "", "", AN), ("cărui", "Masc", "Sing", DG), ("cărei", "Fem", "Sing", DG), ("căror", "", "Plur", DG)], "DET", "Int,Rel")
    + _ind("care", [("care", "", "", AN), ("căruia", "Masc", "Sing", DG), ("căreia", "Fem", "Sing", DG), ("cărora", "", "Plur", DG)], "PRON", "Int,Rel")
    + _ind("ce", [("ce", "", "", AN)], "DET", "Int,Rel") + _ind("ce", [("ce", "", "", AN)], "PRON", "Int,Rel")
    + _ind("cine", [("cine", "", "", AN), ("cui", "", "Sing", DG)], "PRON", "Int,Rel")
    + _ind("cât", [("cât", "Masc", "Sing", AN), ("câtă", "Fem", "Sing", AN), ("câți", "Masc", "Plur", AN), ("câte", "Fem", "Plur", AN), ("câtor", "", "Plur", DG)], "DET", "Int,Rel", None)
    + _ind("cât", [("cât", "Masc", "Sing", AN), ("câtă", "Fem", "Sing", AN), ("câți", "Masc", "Plur", AN), ("câte", "Fem", "Plur", AN)], "PRON", "Int,Rel")
)
INTARIRE: list[tuple[str, str, str, str]] = [
    ("DET", "însumi", "însumi", "Gender=Masc|Number=Sing|Person=1|PronType=Emp"), ("DET", "însumi", "însămi", "Gender=Fem|Number=Sing|Person=1|PronType=Emp"),
    ("DET", "însumi", "înșine", "Gender=Masc|Number=Plur|Person=1|PronType=Emp"), ("DET", "însumi", "însene", "Gender=Fem|Number=Plur|Person=1|PronType=Emp"),
    ("DET", "însuți", "însuți", "Gender=Masc|Number=Sing|Person=2|PronType=Emp"), ("DET", "însuți", "însăți", "Gender=Fem|Number=Sing|Person=2|PronType=Emp"),
    ("DET", "însuți", "înșivă", "Gender=Masc|Number=Plur|Person=2|PronType=Emp"), ("DET", "însuți", "însevă", "Gender=Fem|Number=Plur|Person=2|PronType=Emp"),
    ("DET", "însuși", "însuși", "Gender=Masc|Number=Sing|Person=3|PronType=Emp"), ("DET", "însuși", "însăși", "Case=Acc,Nom|Gender=Fem|Number=Sing|Person=3|PronType=Emp"),
    ("DET", "însuși", "înseși", "Case=Dat,Gen|Gender=Fem|Number=Sing|Person=3|PronType=Emp"), ("DET", "însuși", "înșiși", "Gender=Masc|Number=Plur|Person=3|PronType=Emp"),
    ("DET", "însuși", "însele", "Gender=Fem|Number=Plur|Person=3|PronType=Emp"),
]

# ---- auxiliare și particule (convenția UD RRT: auxiliarul perfectului compus / condiționalului nu are Mood/Tense) ----
AUXILIARE: list[tuple[str, str, str, str]] = [
    ("AUX", "avea", "am", "Person=1"), ("AUX", "avea", "ai", "Number=Sing|Person=2"), ("AUX", "avea", "a", "Number=Sing|Person=3"),
    ("AUX", "avea", "ați", "Number=Plur|Person=2"), ("AUX", "avea", "au", "Number=Plur|Person=3"),
    ("AUX", "avea", "aș", "Number=Sing|Person=1"), ("AUX", "avea", "ar", "Person=3"),
    ("AUX", "avea", "aveam", "Mood=Ind|Person=1|Tense=Imp|VerbForm=Fin"), ("AUX", "avea", "aveai", "Mood=Ind|Number=Sing|Person=2|Tense=Imp|VerbForm=Fin"),
    ("AUX", "avea", "avea", "Mood=Ind|Number=Sing|Person=3|Tense=Imp|VerbForm=Fin"), ("AUX", "avea", "aveați", "Mood=Ind|Number=Plur|Person=2|Tense=Imp|VerbForm=Fin"),
    ("AUX", "avea", "aveau", "Mood=Ind|Number=Plur|Person=3|Tense=Imp|VerbForm=Fin"),
    ("AUX", "vrea", "voi", "Number=Sing|Person=1"), ("AUX", "vrea", "vei", "Number=Sing|Person=2"), ("AUX", "vrea", "va", "Number=Sing|Person=3"),
    ("AUX", "vrea", "vom", "Number=Plur|Person=1"), ("AUX", "vrea", "veți", "Number=Plur|Person=2"), ("AUX", "vrea", "vor", "Number=Plur|Person=3"),
    ("AUX", "vrea", "oi", "Number=Sing|Person=1"), ("AUX", "vrea", "oi", "Number=Sing|Person=2"), ("AUX", "vrea", "o", "Number=Sing|Person=3"),
    ("AUX", "vrea", "om", "Number=Plur|Person=1"), ("AUX", "vrea", "ăți", "Number=Plur|Person=2"), ("AUX", "vrea", "or", "Number=Plur|Person=3"),
    ("AUX", "fi", "sunt", "Mood=Ind|Number=Sing|Person=1|Tense=Pres|VerbForm=Fin"), ("AUX", "fi", "ești", "Mood=Ind|Number=Sing|Person=2|Tense=Pres|VerbForm=Fin"),
    ("AUX", "fi", "este", "Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin"), ("AUX", "fi", "e", "Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin"),
    ("AUX", "fi", "suntem", "Mood=Ind|Number=Plur|Person=1|Tense=Pres|VerbForm=Fin"), ("AUX", "fi", "sunteți", "Mood=Ind|Number=Plur|Person=2|Tense=Pres|VerbForm=Fin"),
    ("AUX", "fi", "sunt", "Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin"),
    ("AUX", "fi", "eram", "Mood=Ind|Person=1|Tense=Imp|VerbForm=Fin"), ("AUX", "fi", "erai", "Mood=Ind|Number=Sing|Person=2|Tense=Imp|VerbForm=Fin"),
    ("AUX", "fi", "era", "Mood=Ind|Number=Sing|Person=3|Tense=Imp|VerbForm=Fin"), ("AUX", "fi", "erați", "Mood=Ind|Number=Plur|Person=2|Tense=Imp|VerbForm=Fin"),
    ("AUX", "fi", "erau", "Mood=Ind|Number=Plur|Person=3|Tense=Imp|VerbForm=Fin"),
    ("AUX", "fi", "fui", "Mood=Ind|Number=Sing|Person=1|Tense=Past|VerbForm=Fin"), ("AUX", "fi", "fuși", "Mood=Ind|Number=Sing|Person=2|Tense=Past|VerbForm=Fin"),
    ("AUX", "fi", "fu", "Mood=Ind|Number=Sing|Person=3|Tense=Past|VerbForm=Fin"), ("AUX", "fi", "furăm", "Mood=Ind|Number=Plur|Person=1|Tense=Past|VerbForm=Fin"),
    ("AUX", "fi", "furăți", "Mood=Ind|Number=Plur|Person=2|Tense=Past|VerbForm=Fin"), ("AUX", "fi", "fură", "Mood=Ind|Number=Plur|Person=3|Tense=Past|VerbForm=Fin"),
    ("AUX", "fi", "fusesem", "Mood=Ind|Number=Sing|Person=1|Tense=Pqp|VerbForm=Fin"), ("AUX", "fi", "fuseseși", "Mood=Ind|Number=Sing|Person=2|Tense=Pqp|VerbForm=Fin"),
    ("AUX", "fi", "fusese", "Mood=Ind|Number=Sing|Person=3|Tense=Pqp|VerbForm=Fin"), ("AUX", "fi", "fuseserăm", "Mood=Ind|Number=Plur|Person=1|Tense=Pqp|VerbForm=Fin"),
    ("AUX", "fi", "fuseserăți", "Mood=Ind|Number=Plur|Person=2|Tense=Pqp|VerbForm=Fin"), ("AUX", "fi", "fuseseră", "Mood=Ind|Number=Plur|Person=3|Tense=Pqp|VerbForm=Fin"),
    ("AUX", "fi", "fiu", "Mood=Sub|Number=Sing|Person=1|Tense=Pres|VerbForm=Fin"), ("AUX", "fi", "fii", "Mood=Sub|Number=Sing|Person=2|Tense=Pres|VerbForm=Fin"),
    ("AUX", "fi", "fie", "Mood=Sub|Person=3|Tense=Pres|VerbForm=Fin"), ("AUX", "fi", "fim", "Mood=Sub|Number=Plur|Person=1|Tense=Pres|VerbForm=Fin"),
    ("AUX", "fi", "fiți", "Mood=Sub|Number=Plur|Person=2|Tense=Pres|VerbForm=Fin"),
    ("AUX", "fi", "fii", "Mood=Imp|Number=Sing|Person=2|VerbForm=Fin"), ("AUX", "fi", "fiți", "Mood=Imp|Number=Plur|Person=2|VerbForm=Fin"),
    ("AUX", "fi", "fi", "Tense=Pres|VerbForm=Inf"), ("AUX", "fi", "fiind", "VerbForm=Ger"), ("AUX", "fi", "fost", "Gender=Masc|Number=Sing|VerbForm=Part"),
    ("PART", "a", "a", "PartType=Inf"), ("PART", "să", "să", "Mood=Sub"), ("PART", "să", "s-", "Mood=Sub|Variant=Short"),
    ("PART", "nu", "nu", "Polarity=Neg"), ("PART", "nu", "n-", "Polarity=Neg|Variant=Short"), ("PART", "o", "o", "Tense=Fut"),
]
CLITICE_AUX: dict[str, list[tuple[str, str, str]]] = {  # (lemă, formă scurtă, trăsături) pentru auxiliarele legate cu cratimă
    "avea": [("avea", "-a", "Number=Sing|Person=3|Variant=Short"), ("avea", "-am", "Person=1|Variant=Short"), ("avea", "-ai", "Number=Sing|Person=2|Variant=Short"),
             ("avea", "-au", "Number=Plur|Person=3|Variant=Short"), ("avea", "-ați", "Number=Plur|Person=2|Variant=Short"),
             ("avea", "-aș", "Number=Sing|Person=1|Variant=Short"), ("avea", "-ar", "Person=3|Variant=Short")],
    "fi": [("fi", "-i", "Mood=Ind|Number=Sing|Person=3|Tense=Pres|Variant=Short|VerbForm=Fin"), ("fi", "-s", "Mood=Ind|Number=Plur|Person=3|Tense=Pres|Variant=Short|VerbForm=Fin"),
           ("fi", "e-", "Mood=Ind|Number=Sing|Person=3|Tense=Pres|Variant=Short|VerbForm=Fin")],
    "vrea": [("vrea", "-oi", "Number=Sing|Person=1|Variant=Short"), ("vrea", "-o", "Number=Sing|Person=3|Variant=Short"), ("vrea", "-or", "Number=Plur|Person=3|Variant=Short")],
}

# ---- prepoziții: (lemă, formă, cazul cerut) + variantele scurte --------------------------------------------------
PREPOZITII: list[tuple[str, str]] = [
    ("a", "Acc"), ("ca", "Acc"), ("cu", "Acc"), ("către", "Acc"), ("de", "Acc"), ("despre", "Acc"), ("din", "Acc"), ("dinspre", "Acc"), ("dintre", "Acc"),
    ("dintru", "Acc"), ("drept", "Acc"), ("după", "Acc"), ("fără", "Acc"), ("la", "Acc"), ("lângă", "Acc"), ("pe", "Acc"), ("pentru", "Acc"), ("per", "Acc"),
    ("peste", "Acc"), ("prin", "Acc"), ("printre", "Acc"), ("printru", "Acc"), ("privind", "Acc"), ("până", "Acc"), ("spre", "Acc"), ("sub", "Acc"), ("în", "Acc"),
    ("întru", "Acc"), ("înspre", "Acc"), ("între", "Acc"), ("ca", "Acc"), ("decât", "Acc"), ("versus", "Acc"), ("contra", "Gen"), ("asupra", "Gen"),
    ("deasupra", "Gen"), ("dedesubtul", "Gen"), ("dinaintea", "Gen"), ("împotriva", "Gen"), ("înaintea", "Gen"), ("înapoia", "Gen"), ("îndărătul", "Gen"),
    ("împrejurul", "Gen"), ("conform", "Dat"), ("contrar", "Dat"), ("datorită", "Dat"), ("grație", "Dat"), ("mulțumită", "Dat"), ("potrivit", "Dat"),
]
PREPOZITII_SCURTE: list[tuple[str, str, str]] = [("în", "-n", "Acc"), ("în", "într-", "Acc"), ("întru", "într-", "Acc"), ("dintru", "dintr-", "Acc"),
                                                 ("printru", "printr-", "Acc"), ("de", "de-", "Acc"), ("pe", "pe-", "Acc"), ("pe", "p-", "Acc"), ("cu", "cu-", "Acc"),
                                                 ("la", "la-", "Acc"), ("fără", "făr-", "Acc")]
LOCUTIUNI_PREPOZITIONALE: list[tuple[str, str]] = [
    ("din cauza", "Gen"), ("din pricina", "Gen"), ("în fața", "Gen"), ("în spatele", "Gen"), ("în jurul", "Gen"), ("în urma", "Gen"), ("în locul", "Gen"),
    ("în mijlocul", "Gen"), ("în ciuda", "Gen"), ("în pofida", "Gen"), ("de-a lungul", "Gen"), ("de-a latul", "Gen"), ("în vederea", "Gen"), ("în privința", "Gen"),
    ("în cadrul", "Gen"), ("în interiorul", "Gen"), ("în afara", "Gen"), ("în loc de", "Acc"), ("în afară de", "Acc"), ("față de", "Acc"), ("de la", "Acc"),
    ("până la", "Acc"), ("pe la", "Acc"), ("de pe", "Acc"), ("de sub", "Acc"), ("de lângă", "Acc"), ("fără de", "Acc"), ("în legătură cu", "Acc"),
    ("împreună cu", "Acc"), ("potrivit cu", "Acc"), ("conform cu", "Acc"), ("în funcție de", "Acc"), ("cu privire la", "Acc"), ("în raport cu", "Acc"),
    ("referitor la", "Acc"), ("datorită", "Dat"),
]

# ---- conjuncții --------------------------------------------------------------------------------------------------
CONJUNCTII_COORDONATOARE: list[str] = ["și", "sau", "ori", "dar", "iar", "însă", "ci", "deci", "așadar", "nici", "fie", "adică", "căci", "numai", "precum"]
CONJUNCTII_SUBORDONATOARE: list[str] = ["că", "să", "dacă", "deși", "fiindcă", "deoarece", "întrucât", "încât", "căci", "cum", "când", "unde", "precum", "ca",
                                        "decât", "până", "cât", "de", "măcar", "parcă", "odată"]
LOCUTIUNI_CONJUNCTIONALE: list[str] = ["pentru că", "cu toate că", "chiar dacă", "de vreme ce", "din moment ce", "în caz că", "odată ce", "de parcă",
                                       "fără să", "înainte să", "după ce", "înainte ca", "ca să", "pentru ca", "numai să", "îndată ce", "ori de câte ori",
                                       "în timp ce", "pe măsură ce", "cu condiția să", "în loc să", "chiar și", "ca și cum", "ca și când", "cât timp",
                                       "atâta timp cât", "indiferent dacă", "doar că", "numai că", "ci și", "nu numai", "fie că", "măcar că"]

# ---- numerale ---------------------------------------------------------------------------------------------------
CARDINALE: list[tuple[str, str, str]] = [  # (lemă, formă, trăsături suplimentare)
    ("unu", "unu", "Gender=Masc|Number=Sing"), ("unu", "una", "Gender=Fem|Number=Sing"),
    ("doi", "doi", "Gender=Masc|Number=Plur"), ("doi", "două", "Gender=Fem|Number=Plur"),
] + [(n, n, "Number=Plur") for n in ("trei", "patru", "cinci", "șase", "șapte", "opt", "nouă", "zece", "unsprezece", "doisprezece", "treisprezece",
                                      "paisprezece", "cincisprezece", "șaisprezece", "șaptesprezece", "optsprezece", "nouăsprezece", "douăzeci", "treizeci",
                                      "patruzeci", "cincizeci", "șaizeci", "șaptezeci", "optzeci", "nouăzeci", "sută", "mie", "milion", "miliard", "zero")] + [
    ("doisprezece", "douăsprezece", "Gender=Fem|Number=Plur"), ("sută", "sute", "Number=Plur"), ("mie", "mii", "Number=Plur"),
    ("milion", "milioane", "Number=Plur"), ("miliard", "miliarde", "Number=Plur"),
]
ORDINALE: list[tuple[str, str, str]] = [
    ("prim", "primul", "Case=Acc,Nom|Definite=Def|Gender=Masc|Number=Sing"), ("prim", "prima", "Case=Acc,Nom|Definite=Def|Gender=Fem|Number=Sing"),
    ("prim", "primii", "Case=Acc,Nom|Definite=Def|Gender=Masc|Number=Plur"), ("prim", "primele", "Case=Acc,Nom|Definite=Def|Gender=Fem|Number=Plur"),
    ("prim", "primului", "Case=Dat,Gen|Definite=Def|Gender=Masc|Number=Sing"), ("prim", "primei", "Case=Dat,Gen|Definite=Def|Gender=Fem|Number=Sing"),
    ("prim", "primilor", "Case=Dat,Gen|Definite=Def|Gender=Masc|Number=Plur"), ("prim", "primelor", "Case=Dat,Gen|Definite=Def|Gender=Fem|Number=Plur"),
    ("întâi", "întâi", "Number=Sing"), ("întâi", "întâia", "Definite=Def|Gender=Fem|Number=Sing"), ("întâi", "întâiul", "Definite=Def|Gender=Masc|Number=Sing"),
] + [(lema, m, "Gender=Masc|Number=Sing") for lema, m in (("doi", "doilea"), ("trei", "treilea"), ("patru", "patrulea"), ("cinci", "cincilea"), ("șase", "șaselea"),
                                                           ("șapte", "șaptelea"), ("opt", "optulea"), ("nouă", "nouălea"), ("zece", "zecelea"), ("douăzeci", "douăzecilea"),
                                                           ("sută", "sutălea"), ("mie", "miilea"))] + \
    [(lema, f, "Gender=Fem|Number=Sing") for lema, f in (("doi", "doua"), ("trei", "treia"), ("patru", "patra"), ("cinci", "cincea"), ("șase", "șasea"), ("șapte", "șaptea"),
                                                          ("opt", "opta"), ("nouă", "noua"), ("zece", "zecea"), ("douăzeci", "douăzecea"), ("sută", "suta"), ("mie", "mia"))]

ADVERBE_UZUALE: list[str] = ["nu", "da", "mai", "foarte", "prea", "tot", "iar", "chiar", "doar", "numai", "așa", "aici", "acolo", "acum", "atunci", "azi", "astăzi",
                             "mâine", "ieri", "când", "unde", "cum", "cât", "bine", "rău", "mult", "puțin", "deja", "încă", "mereu", "niciodată", "nicăieri",
                             "undeva", "cândva", "cumva", "oricum", "oriunde", "oricând", "totuși", "poate", "desigur", "sigur", "probabil", "aproape", "departe",
                             "sus", "jos", "înainte", "înapoi", "afară", "înăuntru", "repede", "încet", "devreme", "târziu", "abia", "cam", "tocmai", "parcă",
                             "oare", "deloc", "destul", "altfel", "astfel", "apoi", "deci", "însă", "adică", "nici", "măcar", "decât", "aproape", "exact", "într-adevăr"]


def toate_formele() -> list[tuple[str, str, str, str, str]]:
    """Toate rândurile: (categorie, lemă, formă, trăsături canonice, detalii)."""
    rez: list[tuple[str, str, str, str, str]] = []
    for lema, forma, tr in PRONUME_PERSONALE:
        rez.append(("PRON", lema, forma, canonic_trasaturi(tr), "pronume personal/reflexiv"))
        if "Strength=Weak" in tr and forma in CLITICE:
            dupa, inainte = CLITICE[forma]
            rez.append(("PRON", lema, dupa, canonic_trasaturi(tr + "|Variant=Short"), "clitic după verb"))
            rez.append(("PRON", lema, inainte, canonic_trasaturi(tr + "|Variant=Short"), "clitic înaintea verbului"))
    for lema, forma, tr in POSESIVE:
        rez.append(("DET", lema, forma, canonic_trasaturi(tr), "posesiv (determinant)"))
        rez.append(("PRON", lema, forma, canonic_trasaturi(tr), "posesiv (pronume)"))
    for pos, lema, forma, tr in DEMONSTRATIVE + ARTICOLE + NEHOTARATE + INTARIRE:
        rez.append((pos, lema, forma, tr, "tabel propriu"))
    for pos, lema, forma, tr in AUXILIARE:
        rez.append((pos, lema, forma, canonic_trasaturi(tr), "auxiliar / particulă"))
    for lema, lista in CLITICE_AUX.items():
        for _, forma, tr in lista:
            rez.append(("AUX", lema, forma, canonic_trasaturi(tr), "auxiliar legat cu cratimă"))
    for lema, caz in PREPOZITII:
        rez.append(("ADP", lema, lema, canonic_trasaturi(f"AdpType=Prep|Case={caz}"), f"prepoziție; cere cazul {caz}"))
    for lema, forma, caz in PREPOZITII_SCURTE:
        rez.append(("ADP", lema, forma, canonic_trasaturi(f"AdpType=Prep|Case={caz}|Variant=Short"), "prepoziție, formă scurtă"))
    for lema, caz in LOCUTIUNI_PREPOZITIONALE:
        rez.append(("ADP", lema, lema, canonic_trasaturi(f"AdpType=Prep|Case={caz}"), f"locuțiune prepozițională; cere cazul {caz}"))
    for c in CONJUNCTII_COORDONATOARE:
        rez.append(("CCONJ", c, c, "Polarity=Pos" if c != "nici" else "Polarity=Neg", "conjuncție coordonatoare"))
    for c in CONJUNCTII_SUBORDONATOARE:
        rez.append(("SCONJ", c, c, "", "conjuncție subordonatoare"))
    for c in LOCUTIUNI_CONJUNCTIONALE:
        rez.append(("SCONJ", c, c, "", "locuțiune conjuncțională"))
    for lema, forma, tr in CARDINALE:
        rez.append(("NUM", lema, forma, canonic_trasaturi(tr + "|NumForm=Word|NumType=Card"), "numeral cardinal"))
    for lema, forma, tr in ORDINALE:
        rez.append(("NUM", lema, forma, canonic_trasaturi(tr + "|NumForm=Word|NumType=Ord"), "numeral ordinal"))
    for a in ADVERBE_UZUALE:
        rez.append(("ADV", a, a, "", "adverb uzual"))
    return rez


def asigura_sursa_reguli(baza: Baza) -> None:
    """Înregistrează sursa „rlc_reguli” (tabelele și paradigmele proprii) dacă lipsește."""
    if baza.con.execute("SELECT 1 FROM surse WHERE id = ?", (SURSA_ID,)).fetchone() is None:
        baza.adauga_sursa(SURSA_ID, "Regulile și tabelele proprii ale motorului (clase închise, paradigme, acord)",
                          licenta="a proiectului Cyberspace (Adrian); reguli ale limbii, scrise de mână",
                          atribuire="documentare: GALR (Academia Română, 2005/2008), convențiile UD RRT", obligatii="",
                          transformari="tabele scrise explicit în morfologie/inchise.py și morfologie/paradigme.py",
                          limitari="clasele închise sunt complete pentru formele standard uzuale; formele populare/regionale rare lipsesc")
        baza.commit()


def scrie_in_baza(baza: Baza, verbos: bool = True) -> dict:
    asigura_sursa_reguli(baza)
    n = 0
    lexeme: dict[tuple[str, str], list[str]] = {}
    for pos, lema, forma, tr, detalii in toate_formele():
        cheie = (normalizeaza(lema), pos)
        if cheie not in lexeme:
            lexeme[cheie] = lexeme_tinta(baza, lema, pos, SURSA_ID, multicuvant=" " in lema, detalii="clasă închisă (tabel propriu)")
        for lid in lexeme[cheie]:
            baza.adauga_forma(forma, lid, tr, "atestat", SURSA_ID, "atestare:tabel_propriu", detalii, 1)
        n += 1
    baza.commit()
    rez = {"forme_din_tabele": n, "lexeme": len(lexeme)}
    if verbos:
        print("Clase închise:", json.dumps(rez, ensure_ascii=False))
    return rez
