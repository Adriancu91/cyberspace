"""Inventarul trăsăturilor morfologice (structurat, nu text liber).

Convenție: aceleași chei și valori ca în corpusul UD Romanian RRT (Universal Dependencies), ca să putem
compara direct formele noastre cu cele atestate. Două adăugiri proprii, marcate:
  - `Gender=Neut` se folosește DOAR la nivel de lexem (genul din dicționar); la nivel de formă, neutrul
    urmează convenția UD pentru română: Masc la singular, Fem la plural;
  - `Polarity=Neg` pe o formă verbală înseamnă imperativ negativ (forma din tabelul Wiktionary), nu particula „nu”.

Tot aici sunt traducerile din etichetele altor surse (Wiktionary/kaikki, anotările Hunspell) în inventar.
"""

from __future__ import annotations

INVENTAR: list[tuple[str, str, str]] = [
    ("Abbr", "Yes", "abreviere"),
    ("AdpType", "Prep", "prepoziție"),
    ("Case", "Acc", "acuzativ (doar la pronume, unde se distinge de nominativ)"),
    ("Case", "Acc,Nom", "nominativ-acuzativ (sincretism nominal)"),
    ("Case", "Dat", "dativ (doar la pronume)"),
    ("Case", "Dat,Gen", "genitiv-dativ (sincretism nominal)"),
    ("Case", "Gen", "genitiv (doar la pronume/determinanți)"),
    ("Case", "Nom", "nominativ (doar la pronume)"),
    ("Case", "Voc", "vocativ"),
    ("Definite", "Def", "articulat hotărât"),
    ("Definite", "Ind", "nearticulat / articulat nehotărât"),
    ("Degree", "Cmp", "comparativ (formă sintetică rară; de regulă „mai” + adjectiv)"),
    ("Degree", "Pos", "grad pozitiv"),
    ("Degree", "Sup", "superlativ (formă sintetică rară; de regulă „cel mai” + adjectiv)"),
    ("ExtPos", "ADJ", "expresie fixă cu rol de adjectiv"),
    ("ExtPos", "ADP", "expresie fixă cu rol de prepoziție (locuțiune prepozițională)"),
    ("ExtPos", "ADV", "expresie fixă cu rol de adverb (locuțiune adverbială)"),
    ("ExtPos", "CCONJ", "expresie fixă cu rol de conjuncție coordonatoare"),
    ("ExtPos", "DET", "expresie fixă cu rol de determinant"),
    ("ExtPos", "INTJ", "expresie fixă cu rol de interjecție"),
    ("ExtPos", "PRON", "expresie fixă cu rol de pronume"),
    ("ExtPos", "SCONJ", "expresie fixă cu rol de conjuncție subordonatoare (locuțiune conjuncțională)"),
    ("Foreign", "Yes", "cuvânt străin"),
    ("Gender", "Fem", "feminin"),
    ("Gender", "Masc", "masculin"),
    ("Gender", "Neut", "neutru (doar la nivel de lexem)"),
    ("Mood", "Imp", "imperativ"),
    ("Mood", "Ind", "indicativ"),
    ("Mood", "Sub", "conjunctiv"),
    ("NumForm", "Combi", "numeral scris combinat (cifre + litere)"),
    ("NumForm", "Digit", "numeral scris cu cifre"),
    ("NumForm", "Roman", "numeral scris cu cifre romane"),
    ("NumForm", "Word", "numeral scris cu litere"),
    ("NumType", "Card", "numeral cardinal"),
    ("NumType", "Ord", "numeral ordinal"),
    ("Number", "Plur", "plural"),
    ("Number", "Sing", "singular"),
    ("Number[psor]", "Plur", "posesor la plural"),
    ("Number[psor]", "Sing", "posesor la singular"),
    ("PartType", "Inf", "particula infinitivului („a”)"),
    ("Person", "1", "persoana I"),
    ("Person", "2", "persoana a II-a"),
    ("Person", "3", "persoana a III-a"),
    ("Polarity", "Neg", "negativ"),
    ("Polarity", "Pos", "pozitiv"),
    ("Position", "Postnom", "determinant postpus substantivului (omul acesta)"),
    ("Position", "Prenom", "determinant antepus substantivului (acest om)"),
    ("Poss", "Yes", "posesiv"),
    ("PronType", "Art", "articol"),
    ("PronType", "Dem", "demonstrativ"),
    ("PronType", "Emp", "de întărire (însuși)"),
    ("PronType", "Ind", "nehotărât"),
    ("PronType", "Int,Rel", "interogativ-relativ"),
    ("PronType", "Neg", "negativ (nimeni, nimic, niciun)"),
    ("PronType", "Prs", "personal"),
    ("PronType", "Tot", "de totalitate (tot, fiecare)"),
    ("Reflex", "Yes", "reflexiv"),
    ("Strength", "Strong", "formă accentuată (pronume)"),
    ("Strength", "Weak", "formă neaccentuată / clitic (pronume)"),
    ("Tense", "Fut", "viitor (formă sintetică rară)"),
    ("Tense", "Imp", "imperfect"),
    ("Tense", "Past", "perfect simplu"),
    ("Tense", "Pqp", "mai-mult-ca-perfect"),
    ("Tense", "Pres", "prezent"),
    ("Typo", "Yes", "greșeală de scriere în sursă"),
    ("Variant", "Short", "formă scurtă / legată cu cratimă (s-, într-, -l)"),
    ("VerbForm", "Fin", "formă verbală personală"),
    ("VerbForm", "Ger", "gerunziu"),
    ("VerbForm", "Inf", "infinitiv"),
    ("VerbForm", "Part", "participiu"),
    ("VerbForm", "Sup", "supin (proprie: UD RRT îl notează ca participiu după „de”)"),
]

CHEI = sorted({c for c, _, _ in INVENTAR})
VALORI: dict[str, set[str]] = {}
for _c, _v, _ in INVENTAR:
    VALORI.setdefault(_c, set()).add(_v)


def valideaza(trasaturi: dict[str, str]) -> list[str]:
    """Întoarce lista problemelor (goală = totul e în inventar)."""
    probleme = []
    for k, v in trasaturi.items():
        if k not in VALORI:
            probleme.append(f"cheie necunoscută: {k}")
        elif v not in VALORI[k]:
            probleme.append(f"valoare necunoscută: {k}={v}")
    return probleme


# ---- Wiktionary (kaikki) → inventar ------------------------------------------------------------------------
ETICHETE_KAIKKI_SIMPLE = {
    "singular": ("Number", "Sing"), "plural": ("Number", "Plur"),
    "definite": ("Definite", "Def"), "indefinite": ("Definite", "Ind"),
    "vocative": ("Case", "Voc"),
    "first-person": ("Person", "1"), "second-person": ("Person", "2"), "third-person": ("Person", "3"),
    "indicative": ("Mood", "Ind"), "subjunctive": ("Mood", "Sub"), "imperative": ("Mood", "Imp"),
    "present": ("Tense", "Pres"), "imperfect": ("Tense", "Imp"), "perfect": ("Tense", "Past"), "pluperfect": ("Tense", "Pqp"),
    "infinitive": ("VerbForm", "Inf"), "gerund": ("VerbForm", "Ger"), "participle": ("VerbForm", "Part"),
    "negative": ("Polarity", "Neg"),
}
ETICHETE_KAIKKI_IGNORATE = {"canonical", "table-tags", "inflection-template", "error-unrecognized-form", "romanization",
                            "alternative", "uppercase", "lowercase", "stressed", "past", "form-of", "error-unknown-tag"}
ETICHETE_REGISTRU = {"regional", "archaic", "obsolete", "dated", "rare", "informal", "colloquial", "dialectal", "nonstandard",
                     "literary", "poetic", "slang", "humorous", "vulgar", "derogatory", "uncommon", "neologism", "proscribed",
                     "misspelling", "Transylvania", "Moldavia", "Bukovina", "Northern", "historical", "figuratively", "idiomatic",
                     "Internet", "abbreviation", "diminutive", "augmentative", "Latinism", "pronunciation-spelling"}


def din_kaikki(etichete: list[str], pos: str) -> tuple[dict[str, str], list[str]]:
    """Traduce etichetele unei forme din Wiktionary în trăsături. Întoarce (trăsături, etichete netraduse)."""
    t: dict[str, str] = {}
    rest: list[str] = []
    e = set(etichete)
    if "nominative" in e or "accusative" in e:
        t["Case"] = "Acc,Nom"
    if "genitive" in e or "dative" in e:
        t["Case"] = "Dat,Gen"
    gen_m, gen_f, gen_n = "masculine" in e, "feminine" in e, "neuter" in e
    numar = "Plur" if "plural" in e else ("Sing" if "singular" in e else None)
    for et in etichete:
        if et in ("nominative", "accusative", "genitive", "dative", "masculine", "feminine", "neuter"):
            continue
        if et in ETICHETE_KAIKKI_SIMPLE:
            k, v = ETICHETE_KAIKKI_SIMPLE[et]
            t[k] = v
        elif et in ETICHETE_KAIKKI_IGNORATE or et in ETICHETE_REGISTRU:
            continue
        else:
            rest.append(et)
    # genul la nivel de formă, în convenția UD (neutru = Masc la sg, Fem la pl)
    if pos in ("NOUN", "PROPN"):
        pass  # genul substantivului e pe lexem; forma îl moștenește la căutare
    elif gen_m and not gen_f and not gen_n:
        t["Gender"] = "Masc"
    elif gen_f and not gen_m and not gen_n:
        t["Gender"] = "Fem"
    elif gen_n and not gen_m and not gen_f:
        t["Gender"] = "Masc" if numar == "Sing" else ("Fem" if numar == "Plur" else "Neut")
    elif gen_m and gen_n and not gen_f:
        t["Gender"] = "Masc"
    elif gen_f and gen_n and not gen_m:
        t["Gender"] = "Fem"
    # etichete de mod/timp fără „VerbForm”: formele personale sunt finite
    if "Mood" in t and "VerbForm" not in t:
        t["VerbForm"] = "Fin"
    if "Mood" in t and t["Mood"] == "Sub" and "Tense" not in t:
        t["Tense"] = "Pres"
    if "Mood" in t and t["Mood"] == "Imp":
        t.setdefault("Person", "2")
        t.pop("Tense", None)
    if t.get("VerbForm") in ("Inf", "Ger"):
        t.pop("Person", None); t.pop("Number", None); t.pop("Tense", None); t.pop("Mood", None)
    return t, rest


def gen_lexem_din_kaikki(etichete: list[str]) -> str | None:
    e = set(etichete)
    if "neuter" in e:
        return "Neut"
    if "feminine" in e and "masculine" not in e:
        return "Fem"
    if "masculine" in e and "feminine" not in e:
        return "Masc"
    return None


# ---- anotările din Hunspell ro_RO.aff (de ex. „s.f.sg.art.”, „s.f.pl.dat.”) → inventar ----------------------
def din_hunspell(anotare: str) -> dict[str, str]:
    t: dict[str, str] = {}
    bucati = [b.strip() for b in anotare.lower().replace(" ", ".").split(".") if b.strip()]
    for b in bucati:
        if b == "sg":
            t["Number"] = "Sing"
        elif b == "pl":
            t["Number"] = "Plur"
        elif b == "art":
            t["Definite"] = "Def"
        elif b == "neart":
            t["Definite"] = "Ind"
        elif b in ("dat", "gen", "gd"):
            t["Case"] = "Dat,Gen"
        elif b in ("nom", "ac", "na"):
            t["Case"] = "Acc,Nom"
        elif b == "voc":
            t["Case"] = "Voc"
        elif b == "f":
            t["Gender"] = "Fem"
        elif b == "m":
            t["Gender"] = "Masc"
        elif b == "n":
            t["Gender"] = "Neut"
    if "Definite" not in t and "Number" in t:
        # în anotările rospell „dat.” singur înseamnă forma articulată de genitiv-dativ („casei”); nearticulatul e marcat „neart.”
        t["Definite"] = "Def" if t.get("Case") == "Dat,Gen" else "Ind"
    if "Case" not in t and "Number" in t and ("Definite" in t):
        t["Case"] = "Acc,Nom"
    return t


# ---- convenția canonică pe categorii (aceeași pentru toate sursele) ---------------------------------------
def canonic_pentru_pos(pos: str, trasaturi: dict[str, str], gen_lexem: str | None = None) -> dict[str, str]:
    """Aduce trăsăturile unei forme la convenția corpusului UD RRT, ca să fie comparabile între surse:
    - substantive/adjective: genul formei vine din lexem (neutru → Masc la sg, Fem la pl); `Case` se omite
      la formele nearticulate sincretice (masculin singular și toate pluralele), ca în UD;
    - adjective: `Degree=Pos` implicit;
    - participii: Gender/Number implicite Masc/Sing (forma de dicționar)."""
    t = {k: v for k, v in trasaturi.items() if k != "ExtPos"}   # ExtPos e proprietatea expresiei fixe, nu a formei
    if pos == "PROPN" and t.get("Case") not in ("Dat,Gen", "Voc") and t.get("Definite") != "Def":
        return {k: v for k, v in t.items() if k in ("Abbr", "Foreign")}   # UD RRT: numele proprii au trăsături doar când sunt flexionate
    if pos in ("NOUN", "PROPN", "ADJ", "NUM", "DET"):
        if "Gender" not in t and gen_lexem in ("Masc", "Fem", "Neut") and pos in ("NOUN", "PROPN"):
            if gen_lexem == "Neut":
                if t.get("Number") == "Sing":
                    t["Gender"] = "Masc"
                elif t.get("Number") == "Plur":
                    t["Gender"] = "Fem"
            else:
                t["Gender"] = gen_lexem
        if t.get("Gender") == "Neut":
            if t.get("Number") == "Sing":
                t["Gender"] = "Masc"
            elif t.get("Number") == "Plur":
                t["Gender"] = "Fem"
            else:
                t.pop("Gender")
        if t.get("Definite") == "Ind" and "Case" in t and t["Case"] != "Voc":
            if t.get("Gender") == "Masc" or t.get("Number") == "Plur":
                t.pop("Case")
        if pos == "ADJ" and t and "Degree" not in t:
            t["Degree"] = "Pos"
        if pos in ("NOUN", "ADJ") and "Number" in t and "Definite" not in t and t.get("Case") != "Voc":
            t["Definite"] = "Ind"
    if pos in ("VERB", "AUX") and t.get("VerbForm") == "Inf":
        t["Tense"] = "Pres"   # convenția UD RRT pentru infinitiv
        t.pop("Person", None); t.pop("Number", None); t.pop("Mood", None)
    if pos == "VERB" and "Person" in t and "VerbForm" not in t and t.get("Tense"):
        t["VerbForm"] = "Fin"
        t.setdefault("Mood", "Ind")
    if pos in ("VERB", "AUX") and t.get("VerbForm") == "Part":
        t.setdefault("Gender", "Masc")
        t.setdefault("Number", "Sing")
        t.pop("Tense", None)
        t.pop("Mood", None)
    return t
