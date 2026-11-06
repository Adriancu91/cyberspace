"""S76a (C-64 R1, 4 noiembrie 2026): răspunsuri în română — exerciții „întrebare/instrucțiune → răspuns”, un set
ascuns și o notă automată, fără alt AI (profesorul Qwen NU se folosește aici).

- **construieste**: perechi „Text: …⏎Întrebare: …⏎Răspuns: …” (același format ca la antrenarea liniei w2,
  `module.model_conversatie.intrebarea`), făcute doar prin reguli, doar din datele românești de pe disc: primul paragraf al
  articolelor Wikipedia RO (aceleași filtre ca `unelte/conversatie_text.py`) și conversația simplă scrisă de mână
  (`docs/conversatie/conversatie_simpla.json`, doar la antrenare: toate perechile ei sunt deja în `text_v3`).
  Felurile vechi (ca în `text_v3`): „text” (răspunsul în text), „nu_scrie” („Nu scrie în text.”), „da_nu”, „conversatie”.
  Felurile noi, la imperativ (nu există în `text_v3` și nici în examenele vechi; verificat în `info.json`):
  „instr_propozitie” (Spune într-o propoziție ce este X.), „instr_rezuma” (Rezumă textul într-o propoziție.),
  „instr_an” (Scrie doar anul în care …), „instr_nume” (Scrie numele celui care …), „instr_numar” (Scrie doar numărul
  de locuitori / suprafața …), „instr_judet_tara” (Spune în ce județ / raion se află X și din ce țară face parte.),
  „instr_da_nu” (Răspunde cu da sau nu: …) și „instr_nu_scrie” (aceleași instrucțiuni, când răspunsul lipsește din text).
  Fiecare pereche: `id`, `fel`, `tip`, `prompt` (exact ce vede modelul), `text`, `intrebare`, `raspuns` (referința),
  `cheie` (1–3 bucăți care trebuie să apară într-un răspuns corect), `subiect` (X), `articol` (sursa).
  Setul ascuns vine din articole care nu intră deloc în antrenare și nu apar în `text`, `text_v2`, `text_v3` sau în
  examenele vechi; scurgerile (bucăți de 8 cuvinte) se numără și trebuie să fie 0.
- **noteaza** (deterministă): pentru fiecare răspuns (tăiat la primul rând nou) trei note 0/1 — corect, în temă, limbă
  curată — și scorul R1 = media celor trei procente.
- **proba**: proba notei (referințele însele, răspuns gol, referința altei întrebări, de două ori la fel).
- **reper**: un model salvat de Kronos (#477) scrie răspunsurile la setul ascuns pe placă (cea mai probabilă bucată,
  cel mult 64 de simboluri), apoi `noteaza`. Greutățile doar citite (SHA-256 înainte și după).

- **reformulat** (S76c, 6 nov 2026): instrucțiunile setului ascuns (aceleași articole, referințe și chei), cu
  întrebarea spusă altfel (`REFORMULARI`, cel puțin 2 șabloane pe fel, niciunul găsit în `antrenare.jsonl`) →
  `ascuns_reformulat.jsonl` + `info_reformulat.json`. La „locuitori”, numărul se citește întreg (`numar`: „1,091” =
  „1.091” = 1091) și cheia tăiată din S76a („000” din „122,000”) se repară. `reper --set …` îl examinează;
  `renoteaza-reparat` re-notează răspunsurile vechi pe S76a doar cu perechea reparată.

    python unelte/romana_raspunsuri.py construieste
    python unelte/romana_raspunsuri.py reformulat
    python unelte/romana_raspunsuri.py proba
    python unelte/romana_raspunsuri.py reper --experiment 477 --iesire lucru/romana_raspunsuri/reper_477
    python unelte/romana_raspunsuri.py noteaza --raspunsuri <raspunsuri.json> --iesire <nota.json>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import subprocess
import sys
import threading
import time
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

DOSAR = "lucru/romana_raspunsuri"
NU_SCRIE = "Nu scrie în text."
CONVERSATIE = "docs/conversatie/conversatie_simpla.json"
# Examenele vechi de conversație (nicio bucată de 8 cuvinte din ele nu intră nici în antrenare, nici în setul ascuns).
EXAMENE_VECHI = ["date/conversatie/examen.json", "date/conversatie/examen_15oct.json",
                 "date/conversatie/text/examen.json", "date/conversatie/text_v2/examen.json",
                 "date/conversatie/text_v3/examen.json", "docs/conversatie/examen_generalizare_401.json",
                 "docs/conversatie/examen_generalizare_mare.json", "docs/conversatie/examen_scris_de_mana.json",
                 "lucru/e3/examen_nou_4096.json"]
# Datele „text” vechi: niciun articol al lor nu intră în setul ascuns.
TEXTE_VECHI = ["date/conversatie/text/antrenare.jsonl", "date/conversatie/text_v2/antrenare.jsonl",
               "date/conversatie/text_v3/antrenare.jsonl"]
FELURI_VECHI = ("text", "nu_scrie", "da_nu", "conversatie")
INSTRUCTIUNI = ("instr_propozitie", "instr_rezuma", "instr_an", "instr_nume", "instr_numar", "instr_judet_tara",
                "instr_da_nu", "instr_nu_scrie")
REFUZ = ("nu_scrie", "instr_nu_scrie")
DA_NU = ("da_nu", "instr_da_nu")
# Începuturile instrucțiunilor noi (fără diacritice, litere mici): nu trebuie să existe în text_v3 și în examenele vechi.
INCEPUTURI_NOI = ("spune intr o propozitie", "rezuma textul", "scrie doar", "scrie numele", "spune in ce",
                  "raspunde cu da sau nu")
# Cotele setului ascuns (o pereche pe articol; felurile rare se aleg întâi). Refuzurile („Nu scrie în text.”) sunt
# 15 % și da/nu 10 %: un răspuns luat la întâmplare de la altă întrebare nimerește din întâmplare cam
# 0,15² + 2 × 0,05² ≈ 2,75 % (proba notei cere ≤ 5 %; pe setul de probă cu 21 % + 17 % ieșea 6,84 %).
COTE_ASCUNS = {"instr_judet_tara": 40, "instr_nume": 40, "instr_numar": 40, "instr_an": 40, "instr_propozitie": 40,
               "instr_rezuma": 40, "instr_nu_scrie": 25, "instr_da_nu": 25, "da_nu": 25, "nu_scrie": 25,
               "nu_scrie_alt": 25, "text": 135}


# --- textul ---------------------------------------------------------------------------------------------------------

def fara_diacritice(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in s if not unicodedata.combining(ch))


def norm(s: str) -> str:
    """Litere mici, fără diacritice, fără semne; numerele cu despărțitor de mii lipite („1.204” → „1204”)."""
    s = fara_diacritice(s.lower())
    s = re.sub(r"(?<=\d)[.\s](?=\d{3}\b)", "", s)
    s = re.sub(r"(?<=\d),(?=\d)", "_", s)  # „2,5” rămâne un singur număr
    return " ".join(re.sub(r"[^a-z0-9_ ]+", " ", s).split())


def contine(raspuns: str, bucata: str) -> bool:
    """Bucata apare în răspuns, ca cuvinte întregi (fără diacritice, fără majuscule, numerele ca cifre)."""
    b = norm(bucata)
    return bool(b) and f" {b} " in f" {norm(raspuns)} "


def cuvant_principal(x: str) -> str:
    """Cuvântul principal al subiectului: cel mai lung cuvânt din X (fără paranteze)."""
    cuvinte = re.findall(r"[\wăâîșțĂÂÎȘȚ'-]+", re.sub(r"\([^)]*\)", "", x))
    cuvinte = [c for c in cuvinte if len(c) >= 3] or cuvinte
    return max(cuvinte, key=len) if cuvinte else x


_COPULA = re.compile(r"\b(?:este|era|e|a fost|sunt|au fost)\s+(?:(?:un|o|unul|una|cel|cea|niște)\s+)?([^\s,.;()]+)"
                     r"(?:\s+([^\s,.;()]+))?")


def substantiv(propozitie: str) -> str:
    """Primul cuvânt după „este (un/o)” (sărind „fost”, „important”, „celebru”…): „municipiu”, „film”, „actor”."""
    from unelte.conversatie_wikipedia import ADJECTIVE_INAINTE

    m = _COPULA.search(re.sub(r"\([^)]*\)", "", propozitie))
    if m is None:
        return ""
    c = m.group(1)
    if c in ADJECTIVE_INAINTE and m.group(2):
        c = m.group(2)
    return c if len(c) >= 3 and c.isalpha() and c.islower() else ""


def scurtata(propozitie: str, max_cuvinte: int = 30, la_virgula: bool = False) -> str | None:
    """Propoziția fără paranteze; prea lungă (sau `la_virgula`) → tăiată la prima virgulă de după al 6-lea cuvânt."""
    s = " ".join(re.sub(r"\s*\([^()]*\)", "", propozitie).split()).rstrip(".!? ")
    s = re.sub(r"\s+,", ",", s)
    cuvinte = s.split()
    if la_virgula or len(cuvinte) > max_cuvinte:
        for i in range(6, len(cuvinte)):
            if cuvinte[i - 1].endswith(","):
                cuvinte = cuvinte[:i]
                break
        s = " ".join(cuvinte).rstrip(",;: ")
    if not 4 <= len(s.split()) <= max_cuvinte:
        return None
    return s + "."


def valoare_cheie(raspuns: str) -> str:
    """Ce trebuie să apară dintr-un răspuns „text” vechi: „În județul Alba.” → „Alba”, „1.204 locuitori.” → „1.204”,
    „În 1950.” → „1950”, „Pe malul stâng al râului Mureș.” → „Mureș”."""
    r = raspuns.strip().rstrip(".")
    m = re.match(r"^(?:La |În |Din )?(\d[\d.,]*)", r)
    if m:
        return m.group(1).rstrip(".,")
    cuvinte = r.split()
    for i, c in enumerate(cuvinte):
        if c[:1].isupper() and (i > 0 or len(cuvinte) == 1):
            return " ".join(cuvinte[i:])
    return r


def pereche(fel: str, tip: str, a: dict[str, Any], intrebare: str, raspuns: str, cheie: list[str],
            subiect: str | None = None) -> dict[str, Any]:
    from module.model_conversatie import intrebarea

    text = a.get("text", "")
    cheie = [c for i, c in enumerate(cheie) if c and c not in cheie[:i]][:3]
    return {"fel": fel, "tip": tip, "prompt": intrebarea(intrebare, text), "text": text, "intrebare": intrebare,
            "raspuns": raspuns, "cheie": cheie, "subiect": a.get("x", "") if subiect is None else subiect,
            "articol": f"wikipedia_ro: {a['x']}" if text else a.get("articol", "")}


# --- felurile -------------------------------------------------------------------------------------------------------

def _articolul(articole: list[dict[str, Any]], grup: str) -> dict[str, Any]:
    return articole[int(grup.rsplit("_", 1)[1])]


def vechi_pentru(articole: list[dict[str, Any]], samanta: int, prefix: str) -> list[dict[str, Any]]:
    """Felurile din `text_v3` (aceleași funcții: perechi_pentru cu formulări și da/nu + perechi_noi), cu cheia lor."""
    from unelte.conversatie_text import perechi_noi, perechi_pentru

    brute = perechi_pentru(articole, 0.2, random.Random(samanta), prefix, formulari=random.Random(samanta + 1),
                           da_nu=0.15)
    brute += perechi_noi(articole, 0.2, 0.15, random.Random(samanta + 2), prefix)
    perechi = []
    for p in brute:
        a = _articolul(articole, p["grup"])
        if p["tip"].startswith("da_nu"):
            perechi.append(pereche("da_nu", p["tip"], a, p["intrebare"], p["raspuns"], [p["raspuns"].rstrip(".")]))
        elif p["fel"] == "nu_scrie":
            fel = "nu_scrie_alt" if p["tip"] == "alt_subiect" else "nu_scrie"
            perechi.append(pereche(fel, p["tip"], a, p["intrebare"], NU_SCRIE, [NU_SCRIE]))
        elif p["tip"] == "definitie":
            cheie = substantiv(p["raspuns"])
            if cheie:
                perechi.append(pereche("text", "definitie", a, p["intrebare"], p["raspuns"], [cheie]))
        else:
            perechi.append(pereche("text", p["tip"], a, p["intrebare"], p["raspuns"], [valoare_cheie(p["raspuns"])]))
    return perechi


_AN_INSTR = {"nascut": "Scrie doar anul în care s-a născut {x}.", "murit": "Scrie doar anul în care a murit {x}.",
             "an": "Scrie doar anul în care a apărut {x}.", "atestat": "Scrie doar anul în care a fost atestat documentar {x}."}
_NUME_INSTR = {"regizat": "Scrie numele celui care a regizat {x}.", "scris": "Scrie numele celui care a scris {x}.",
               "fondat": "Scrie numele celui care a fondat {x}.", "dezvoltat": "Scrie numele celui care a dezvoltat {x}.",
               "capitala": "Scrie numele capitalei pentru {x}.", "descris_cine": "Scrie numele celui care a descris specia {x}.",
               "creat": "Scrie numele celui care a creat {x}."}


def instructiuni_din(a: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Toate instrucțiunile posibile pentru un articol, pe feluri (fără instr_da_nu, care vine din da/nu)."""
    from unelte.conversatie_text import _subiect, intrebari_din_text, intrebari_noi, lipsa_din_text, lipsa_noi
    from unelte.conversatie_wikipedia import _PROPOZITII

    x, text, tip = a["x"], a["text"], a["tip"]
    q = {p["tip"]: p for p in intrebari_din_text(text, x, tip, a["prima"], a["definitie"])}
    noi = {p["tip"].removeprefix("nou_"): p for p in intrebari_noi(text, x, tip)}
    lipsa = {p["tip"].removeprefix("lipsa_"): p for p in lipsa_din_text(text, x, tip)}
    lipsa_n = {p["tip"].removeprefix("lipsa_nou_"): p for p in lipsa_noi(text, x, tip)}
    r: dict[str, list[dict[str, Any]]] = {f: [] for f in INSTRUCTIUNI}
    nume = substantiv(a["prima"])
    if nume and (s := scurtata(a["prima"])):
        cine = "cine" if tip == "om" else "ce"
        verb = "a fost" if re.search(r"^[^,]*?\ba fost\b", re.sub(r"\([^)]*\)", "", a["prima"])) and tip == "om" else "este"
        r["instr_propozitie"].append(pereche("instr_propozitie", "propozitie", a,
                                             f"Spune într-o propoziție {cine} {verb} {x}.", s, [nume]))
    if nume and len(_PROPOZITII.split(text)) >= 2 and (s := scurtata(a["prima"], 20, la_virgula=True)):
        r["instr_rezuma"].append(pereche("instr_rezuma", "rezuma", a, "Rezumă textul într-o propoziție.", s,
                                         [cuvant_principal(x), nume]))
    for t in ("nascut", "murit", "an"):
        if t in q:
            an = valoare_cheie(q[t]["raspuns"])
            r["instr_an"].append(pereche("instr_an", t, a, _AN_INSTR[t].format(x=x), f"{an}.", [an]))
    for t in ("fondat_an", "construit_an", "descris_an"):
        if t in noi:
            p = noi[t]
            r["instr_an"].append(pereche("instr_an", t, a, f"Scrie doar anul în care a fost {p['f']} {_subiect(x)}.",
                                         f"{p['valoare']}.", [p["valoare"]]))
    for t in ("regizat", "scris", "fondat", "dezvoltat", "capitala"):
        if t in q:
            v = q[t]["raspuns"].rstrip(".")
            r["instr_nume"].append(pereche("instr_nume", t, a, _NUME_INSTR[t].format(x=x), f"{v}.", [v]))
    if "descris_cine" in noi:
        v = noi["descris_cine"]["valoare"].rstrip(".")
        r["instr_nume"].append(pereche("instr_nume", "descris_cine", a, _NUME_INSTR["descris_cine"].format(x=x),
                                       f"{v}.", [v]))
    if "locuitori" in q:
        n = valoare_cheie(q["locuitori"]["raspuns"])
        r["instr_numar"].append(pereche("instr_numar", "locuitori", a, f"Scrie doar numărul de locuitori din {x}.",
                                        f"{n}.", [n]))
    if "suprafata" in q:
        v = q["suprafata"]["raspuns"].rstrip(".")
        r["instr_numar"].append(pereche("instr_numar", "suprafata", a, f"Scrie doar suprafața pe care o are {x}.",
                                        f"{v}.", [valoare_cheie(v)]))
    if "judet" in q and "România" in text:
        j = q["judet"]["raspuns"].removeprefix("În județul ").rstrip(".")
        r["instr_judet_tara"].append(pereche("instr_judet_tara", "judet_tara", a,
                                             f"Spune în ce județ se află {x} și din ce țară face parte.",
                                             f"{x} se află în județul {j}, în România.", [j, "România"]))
    if "raion" in noi and "Republica Moldova" in text:
        j = noi["raion"]["valoare"]
        r["instr_judet_tara"].append(pereche("instr_judet_tara", "raion_tara", a,
                                             f"Spune în ce raion se află {x} și din ce țară face parte.",
                                             f"{x} se află în raionul {j}, în Republica Moldova.", [j, "Republica Moldova"]))
    for t in ("nascut", "an", "atestat"):
        if t in lipsa:
            r["instr_nu_scrie"].append(pereche("instr_nu_scrie", f"lipsa_{t}", a, _AN_INSTR[t].format(x=x), NU_SCRIE,
                                               [NU_SCRIE]))
    if "locuitori" in lipsa:
        r["instr_nu_scrie"].append(pereche("instr_nu_scrie", "lipsa_locuitori", a,
                                           f"Scrie doar numărul de locuitori din {x}.", NU_SCRIE, [NU_SCRIE]))
    if "regizat" in lipsa:
        r["instr_nu_scrie"].append(pereche("instr_nu_scrie", "lipsa_regizat", a, _NUME_INSTR["regizat"].format(x=x),
                                           NU_SCRIE, [NU_SCRIE]))
    if "fondat" in lipsa:
        r["instr_nu_scrie"].append(pereche("instr_nu_scrie", "lipsa_creat", a, _NUME_INSTR["creat"].format(x=x),
                                           NU_SCRIE, [NU_SCRIE]))
    for t in ("fondat_an", "construit_an"):
        if t in lipsa_n:
            r["instr_nu_scrie"].append(pereche("instr_nu_scrie", f"lipsa_{t}", a,
                                               f"Scrie doar anul în care a fost {lipsa_n[t]['f']} {_subiect(x)}.",
                                               NU_SCRIE, [NU_SCRIE]))
    return r


def da_nu_instr(articole: list[dict[str, Any]], samanta: int, prefix: str) -> list[dict[str, Any]]:
    """„Răspunde cu da sau nu: …” — întrebările da/nu ale lui `text_v3` (da_nu_pentru), câte una pe articol."""
    from unelte.conversatie_text import da_nu_pentru, intrebari_din_text

    pozitive = []
    for i, a in enumerate(articole):
        for q in intrebari_din_text(a["text"], a["x"], a["tip"], a["prima"], a["definitie"]):
            if q["tip"] != "definitie":
                pozitive.append({"fel": "text", "grup": f"{prefix}_{i}", "text": a["text"], "x": a["x"], **q})
    perechi = []
    for p in da_nu_pentru(pozitive, len(articole), random.Random(samanta)):
        a = _articolul(articole, p["grup"])
        perechi.append(pereche("instr_da_nu", p["tip"], a, f"Răspunde cu da sau nu: {p['intrebare']}", p["raspuns"],
                               [p["raspuns"].rstrip(".")]))
    return perechi


def conversatie(la_examen: set[str], ori: int) -> list[dict[str, Any]]:
    """Conversația simplă scrisă de mână (doar la antrenare), fără întrebările din examenele vechi."""
    from unelte.genereaza_conversatie import normalizat

    simple = json.loads((RADACINA / CONVERSATIE).read_text(encoding="utf-8"))["perechi"]
    perechi = []
    for p in simple:
        if p["limba"] != "ro" or normalizat(p["intrebare"]) in la_examen:
            continue
        cheie = "Kronos" if "Kronos" in p["raspuns"] else max(re.findall(r"[\wăâîșțĂÂÎȘȚ]+", p["raspuns"]), key=len)
        perechi.append(pereche("conversatie", "conversatie", {"x": "", "articol": CONVERSATIE}, p["intrebare"],
                               p["raspuns"], [cheie], subiect=""))
    return perechi * ori


# --- scurgerile -----------------------------------------------------------------------------------------------------

def bucati_continut(p: dict[str, Any]) -> set[str]:
    """Bucățile de 8 cuvinte din conținutul perechii: textul și răspunsul (plus întrebarea, la perechile fără text).
    Întrebările cu text sunt șabloane + subiectul + o valoare din text: șabloanele sunt comune prin construcție
    („scrie doar anul în care s-a născut”), iar subiectul și valoarea sunt deja în text."""
    from unelte.genereaza_conversatie import bucati

    b = bucati(p.get("text", "")) | bucati(p["raspuns"])
    return b if p.get("text") else b | bucati(p["intrebare"])


def examene_vechi(radacina: Path = RADACINA) -> tuple[set[str], set[str], list[str]]:
    """(bucățile de 8 cuvinte din examenele vechi, întrebările lor normalizate, toate întrebările lor)."""
    from unelte.genereaza_conversatie import bucati, normalizat, texte_din_json

    b: set[str] = set()
    intrebari: list[str] = []
    for cale in EXAMENE_VECHI:
        f = radacina / cale
        if not f.exists():
            continue
        date = json.loads(f.read_text(encoding="utf-8"))
        for t in texte_din_json(date):
            b |= bucati(t)
        perechi = date.get("perechi", date.get("intrebari", [])) if isinstance(date, dict) else date
        intrebari += [p["intrebare"] for p in perechi if isinstance(p, dict) and "intrebare" in p]
    return b, {normalizat(i) for i in intrebari}, intrebari


def texte_vechi(radacina: Path = RADACINA) -> tuple[set[str], list[str]]:
    texte: set[str] = set()
    intrebari: list[str] = []
    for cale in TEXTE_VECHI:
        with (radacina / cale).open(encoding="utf-8") as f:
            for rand in f:
                p = json.loads(rand)
                if p.get("text"):
                    texte.add(p["text"])
                intrebari.append(p["intrebare"])
    return texte, intrebari


def inceputuri_noi_in(intrebari: list[str]) -> int:
    return sum(norm(i).startswith(INCEPUTURI_NOI) for i in intrebari)


# --- construirea ----------------------------------------------------------------------------------------------------

def alege_ascuns(candidati: list[dict[str, list[dict[str, Any]]]], cote: dict[str, int], rng: random.Random
                 ) -> list[dict[str, Any]]:
    """O pereche pe articol: pentru fiecare fel (întâi cele cu cote mai greu de umplut), articole încă nefolosite."""
    folosite: set[int] = set()
    alese: list[dict[str, Any]] = []
    ordine = sorted(cote, key=lambda f: sum(bool(c.get(f)) for c in candidati))
    for fel in ordine:
        idx = [i for i, c in enumerate(candidati) if c.get(fel) and i not in folosite]
        rng.shuffle(idx)
        for i in idx[: cote[fel]]:
            alese.append(rng.choice(candidati[i][fel]))
            folosite.add(i)
    return alese


def pe_feluri(perechi: list[dict[str, Any]], articole: list[dict[str, Any]], samanta: int, prefix: str
              ) -> list[dict[str, list[dict[str, Any]]]]:
    """Pentru fiecare articol: perechile posibile, pe feluri (vechi + instrucțiuni)."""
    r: list[dict[str, list[dict[str, Any]]]] = [instructiuni_din(a) for a in articole]
    pe_x = {a["x"]: i for i, a in enumerate(articole)}
    for p in perechi + da_nu_instr(articole, samanta + 3, prefix):
        r[pe_x[p["subiect"]]].setdefault(p["fel"], []).append(p)
    return r


def echilibrat(pe_fel: dict[str, list[dict[str, Any]]], cate: int, rng: random.Random) -> list[dict[str, Any]]:
    """Cel mult `cate` perechi, luate pe rând din fiecare fel (ca niciun fel să nu le acopere pe celelalte)."""
    liste = {f: rng.sample(v, len(v)) for f, v in pe_fel.items() if v}
    alese: list[dict[str, Any]] = []
    while len(alese) < cate and any(liste.values()):
        for f in sorted(liste):
            if liste[f] and len(alese) < cate:
                alese.append(liste[f].pop())
    return alese


def construieste(args: argparse.Namespace) -> dict[str, Any]:
    from unelte.conversatie_text import articole_bune
    from unelte.conversatie_wikipedia import SURSA
    from unelte.genereaza_conversatie import bucati, bucati_interzise, normalizat
    from unelte.ortografie_ro import citeste_exceptii, citeste_lista

    t0 = time.time()
    dosar = RADACINA / args.dosar
    if (dosar / "ascuns.jsonl").exists() and not args.suprascrie:
        raise SystemExit(f"{dosar / 'ascuns.jsonl'} există deja: setul ascuns nu se face a doua oară.")
    rng = random.Random(args.samanta)
    validari = bucati_interzise()
    vechi_b, vechi_intrebari_norm, vechi_intrebari = examene_vechi()
    interzise = validari | vechi_b
    texte_v, intrebari_v = texte_vechi()
    motive: Counter[str] = Counter()
    bune = articole_bune(RADACINA / SURSA, interzise, citeste_lista(), citeste_exceptii(), 150, 700,
                         args.articole_ascuns + 2 * args.articole, motive, rng)
    rng.shuffle(bune)
    print(f"articole bune: {len(bune)} ({time.time() - t0:.0f} s)", flush=True)

    # setul ascuns: articole care nu sunt în text/text_v2/text_v3 (nici text, nici bucăți de 8 cuvinte)
    b_vechi_texte: set[str] = set()
    for t in texte_v:
        b_vechi_texte |= bucati(t)
    rezerva_ascuns: list[dict[str, Any]] = []
    rest: list[dict[str, Any]] = []
    for a in bune:
        if (len(rezerva_ascuns) < args.articole_ascuns and a["text"] not in texte_v
                and not (bucati(a["text"]) & b_vechi_texte)):
            rezerva_ascuns.append(a)
        else:
            rest.append(a)
    vechi_a = vechi_pentru(rezerva_ascuns, args.samanta + 10, "ascuns")
    candidati = pe_feluri(vechi_a, rezerva_ascuns, args.samanta + 10, "ascuns")
    ascuns = alege_ascuns(candidati, COTE_ASCUNS, random.Random(args.samanta + 20))
    for p in ascuns:
        if p["fel"] == "nu_scrie_alt":
            p["fel"] = "nu_scrie"
    random.Random(args.samanta + 21).shuffle(ascuns)
    # articolele din rezervă care n-au intrat în ascuns nu intră nici în antrenare (din ele vin și „Ce este Y?”)
    subiecte_rezerva = {normalizat(a["x"]) for a in rezerva_ascuns}
    b_ascuns: set[str] = set()
    for p in ascuns:
        b_ascuns |= bucati_continut(p)
    for a in rezerva_ascuns:
        b_ascuns |= bucati(a["text"])

    # antrenarea: articole fără nicio bucată de 8 cuvinte din setul ascuns (nici din rezerva lui)
    de_antrenare: list[dict[str, Any]] = []
    for a in rest:
        if len(de_antrenare) >= args.articole:
            break
        if normalizat(a["x"]) in subiecte_rezerva:
            motive["antrenare: subiect din rezerva setului ascuns"] += 1
        elif bucati(a["text"]) & b_ascuns:
            motive["antrenare: bucată de 8 cuvinte din setul ascuns"] += 1
        else:
            de_antrenare.append(a)
    vechi_t = vechi_pentru(de_antrenare, args.samanta + 30, "text")
    for p in vechi_t:
        if p["fel"] == "nu_scrie_alt":
            p["fel"] = "nu_scrie"
    cand_t = pe_feluri([], de_antrenare, args.samanta + 30, "text")
    instr_pe_fel: dict[str, list[dict[str, Any]]] = {f: [] for f in INSTRUCTIUNI}
    for c in cand_t:
        for f in INSTRUCTIUNI:
            instr_pe_fel[f] += c.get(f, [])
    conv = conversatie(vechi_intrebari_norm, args.conversatie_ori)
    cate_instr = round(args.instructiuni / (1 - args.instructiuni) * (len(vechi_t) + len(conv)))
    instr = echilibrat(instr_pe_fel, cate_instr, random.Random(args.samanta + 40))
    antrenare = vechi_t + conv + instr
    # ultima plasă: nicio pereche de antrenare cu o bucată de 8 cuvinte din ascuns / examenele vechi / validări
    scoase = Counter()
    curate = []
    for p in antrenare:
        b = bucati_continut(p)
        if b & b_ascuns:
            scoase["bucată din setul ascuns"] += 1
        elif b & interzise:
            scoase["bucată din examenele vechi sau din validări"] += 1
        else:
            curate.append(p)
    antrenare = curate
    random.Random(args.samanta + 41).shuffle(antrenare)
    for k, p in enumerate(antrenare):
        p["id"] = f"a{k:05d}"
    for k, p in enumerate(ascuns):
        p["id"] = f"x{k:04d}"

    # verificările (toate trebuie 0)
    b_antr: set[str] = set()
    for p in antrenare:
        b_antr |= bucati_continut(p)
    b_asc_final: set[str] = set()
    for p in ascuns:
        b_asc_final |= bucati_continut(p)
    texte_antr = {p["text"] for p in antrenare if p["text"]}
    verificari = {
        "scurgeri_antrenare_ascuns": len(b_antr & b_asc_final),
        "scurgeri_antrenare_examene_vechi": len(b_antr & vechi_b),
        "scurgeri_antrenare_validari": len(b_antr & validari),
        "scurgeri_ascuns_examene_vechi": len(b_asc_final & vechi_b),
        "scurgeri_ascuns_validari": len(b_asc_final & validari),
        "scurgeri_ascuns_texte_v3": len(b_asc_final & b_vechi_texte),
        "texte_ascuns_in_antrenare": sum(p["text"] in texte_antr for p in ascuns if p["text"]),
        "texte_ascuns_in_text_v3": sum(p["text"] in texte_v for p in ascuns if p["text"]),
        "intrebari_ascuns_in_examene_vechi": sum(normalizat(p["intrebare"]) in vechi_intrebari_norm for p in ascuns),
        "informativ_intrebari_ascuns_identice_cu_antrenare": len({normalizat(p["intrebare"]) for p in ascuns}
                                                                 & {normalizat(p["intrebare"]) for p in antrenare}),
        "inceputuri_noi_in_text_v3": inceputuri_noi_in(intrebari_v),
        "inceputuri_noi_in_examene_vechi": inceputuri_noi_in(vechi_intrebari),
    }
    dosar.mkdir(parents=True, exist_ok=True)
    for nume, perechi in (("antrenare.jsonl", antrenare), ("ascuns.jsonl", ascuns)):
        with (dosar / nume).open("w", encoding="utf-8", newline="\n") as f:
            for p in perechi:
                f.write(json.dumps(p, ensure_ascii=False) + "\n")
    n_instr = sum(p["fel"] in INSTRUCTIUNI for p in antrenare)
    n_instr_a = sum(p["fel"] in INSTRUCTIUNI for p in ascuns)
    info = {
        "facut": "unelte/romana_raspunsuri.py construieste", "argumente": {k: v for k, v in vars(args).items()
                                                                            if k != "functie"},
        "sursa": "wikipedia_ro (CC BY-SA 4.0) + docs/conversatie/conversatie_simpla.json; nimic descărcat, niciun model",
        "articole_antrenare": len(de_antrenare), "articole_rezerva_ascuns": len(rezerva_ascuns),
        "antrenare": len(antrenare), "antrenare_instructiuni": n_instr,
        "antrenare_instructiuni_procent": round(100 * n_instr / len(antrenare), 2),
        "antrenare_pe_fel": dict(sorted(Counter(p["fel"] for p in antrenare).items())),
        "antrenare_pe_tip": dict(sorted(Counter(p["tip"] for p in antrenare).items())),
        "ascuns": len(ascuns), "ascuns_instructiuni": n_instr_a,
        "ascuns_pe_fel": dict(sorted(Counter(p["fel"] for p in ascuns).items())),
        "ascuns_pe_tip": dict(sorted(Counter(p["tip"] for p in ascuns).items())),
        "feluri_noi": list(INSTRUCTIUNI), "scoase_articole": dict(motive), "scoase_antrenare": dict(scoase),
        "verificari": verificari,
        "sha256": {nume: sha256(dosar / nume) for nume in ("antrenare.jsonl", "ascuns.jsonl")},
        "secunde": round(time.time() - t0, 1),
    }
    (dosar / "info.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    return info


def sha256(cale: Path) -> str:
    h = hashlib.sha256()
    with Path(cale).open("rb") as f:
        while bucata := f.read(1 << 22):
            h.update(bucata)
    return h.hexdigest()


# --- nota -----------------------------------------------------------------------------------------------------------

_CUVANT = re.compile(r"[A-Za-zĂÂÎȘȚăâîșțÀ-ÖØ-öø-ÿ'’-]+|\d+(?:[.,]\d+)*")
_NU_SCRIE = re.compile(r"\b(nu scrie|nu se spune|nu apare|nu este scris|nu e scris|nu stiu|nu sunt sigur)\b")


def taie(text: str) -> str:
    """Răspunsul până la primul rând nou sau la <|endoftext|> (ca la examen_conversatie.py)."""
    return text.split("<|endoftext|>")[0].strip().split("\n")[0].strip()


def spune_nu_scrie(raspuns: str) -> bool:
    return bool(_NU_SCRIE.search(norm(raspuns)))


def nota_corect(p: dict[str, Any], raspuns: str) -> bool:
    if p["fel"] in DA_NU:
        cuvinte = norm(raspuns).split()
        return bool(cuvinte) and cuvinte[0] == norm(p["cheie"][0])
    if p["fel"] in REFUZ:
        return contine(raspuns, NU_SCRIE)
    if "numar" in p:  # S76c: numărul de locuitori citit întreg („1,091” = „1.091” = „1091”)
        return p["numar"] in numere(raspuns) and not spune_nu_scrie(raspuns)
    return all(contine(raspuns, c) for c in p["cheie"]) and not spune_nu_scrie(raspuns)


def nota_in_tema(p: dict[str, Any], raspuns: str) -> bool:
    if p["fel"] in REFUZ:
        return spune_nu_scrie(raspuns)
    if "numar" in p and p["numar"] in numere(raspuns):
        return True
    bucati = [p["subiect"], cuvant_principal(p["subiect"])] if p["subiect"] else []
    return any(contine(raspuns, b) for b in bucati + list(p["cheie"]))


def nota_limba(p: dict[str, Any], raspuns: str, cunoscute: Any, exceptii: set[str], minim: int | None = None
               ) -> bool:
    """2–60 de cuvinte (1 când referința însăși are un singur cuvânt: „1950.”, „Da.”), cel puțin 90 % cunoscute
    (lista de cuvinte a datelor românești; numerele, numele proprii din mijlocul propoziției și cuvintele din prompt
    contează cunoscute), niciun cuvânt de 3 ori la rând, fără bucăți <|…|>."""
    if "<|" in raspuns or "|>" in raspuns:
        return False
    cuvinte = _CUVANT.findall(raspuns)
    if minim is None:
        minim = min(2, len(_CUVANT.findall(p["raspuns"])))
    if not minim <= len(cuvinte) <= 60:
        return False
    din_prompt = {c.lower() for c in _CUVANT.findall(p["prompt"])}
    stiute = 0
    for i, c in enumerate(cuvinte):
        mic = c.lower().strip("'’-")
        if (c[0].isdigit() or mic in cunoscute or mic in exceptii or mic in din_prompt
                or (i > 0 and c[0].isupper())):
            stiute += 1
    if stiute < 0.9 * len(cuvinte):
        return False
    mici = [c.lower() for c in cuvinte]
    return not any(mici[i] == mici[i + 1] == mici[i + 2] for i in range(len(mici) - 2))


def noteaza(perechi: list[dict[str, Any]], raspunsuri: dict[str, str], cunoscute: Any = None,
            exceptii: set[str] | None = None) -> dict[str, Any]:
    """Cele trei note pentru fiecare răspuns și procentele (pe toate și pe fel) + scorul R1 = media celor trei."""
    if cunoscute is None:
        from unelte.ortografie_ro import citeste_exceptii, citeste_lista

        cunoscute, exceptii = citeste_lista(), citeste_exceptii()
    exceptii = exceptii or set()
    note = []
    for p in perechi:
        r = taie(raspunsuri.get(p["id"], ""))
        note.append({"id": p["id"], "fel": p["fel"], "raspuns_model": r, "corect": nota_corect(p, r),
                     "in_tema": nota_in_tema(p, r), "limba_curata": nota_limba(p, r, cunoscute, exceptii),
                     "limba_curata_min2": nota_limba(p, r, cunoscute, exceptii, minim=2)})

    def procente(lista: list[dict[str, Any]]) -> dict[str, Any]:
        n = len(lista)
        c = {k: round(100 * sum(x[k] for x in lista) / n, 2) if n else 0.0
             for k in ("corect", "in_tema", "limba_curata", "limba_curata_min2")}
        return {"n": n, **c, "R1": round((c["corect"] + c["in_tema"] + c["limba_curata"]) / 3, 2)}

    feluri = sorted({x["fel"] for x in note})
    instr = [x for x in note if x["fel"] in INSTRUCTIUNI]
    return {"toate": procente(note), "instructiuni": procente(instr),
            "vechi": procente([x for x in note if x["fel"] not in INSTRUCTIUNI]),
            "pe_fel": {f: procente([x for x in note if x["fel"] == f]) for f in feluri},
            "scor_R1": procente(note)["R1"], "note": note}


def citeste(cale: Path) -> list[dict[str, Any]]:
    with Path(cale).open(encoding="utf-8") as f:
        return [json.loads(r) for r in f if r.strip()]


def citeste_raspunsuri(cale: Path) -> dict[str, str]:
    date = json.loads(Path(cale).read_text(encoding="utf-8"))
    date = date.get("raspunsuri", date) if isinstance(date, dict) else date
    if isinstance(date, list):
        return {x["id"]: x["raspuns_model"] for x in date}
    return dict(date)


def proba(perechi: list[dict[str, Any]]) -> dict[str, Any]:
    """Proba notei: referințele → corect ≥ 95 %; gol → 0 %; referința altei întrebări (amestecate cu sămânța 0) →
    corect ≤ 5 %; de două ori pe aceleași răspunsuri → aceleași cifre."""
    from unelte.ortografie_ro import citeste_exceptii, citeste_lista

    cun, exc = citeste_lista(), citeste_exceptii()
    ref = {p["id"]: p["raspuns"] for p in perechi}
    gol = {p["id"]: "" for p in perechi}
    ordine = [p["raspuns"] for p in perechi]
    random.Random(0).shuffle(ordine)
    alta = {p["id"]: r for p, r in zip(perechi, ordine)}
    n_ref, n_gol, n_alta = noteaza(perechi, ref, cun, exc), noteaza(perechi, gol, cun, exc), noteaza(perechi, alta, cun, exc)
    din_nou = noteaza(perechi, alta, cun, exc)
    rez = {"referinte": {k: v for k, v in n_ref.items() if k != "note"},
           "gol": {k: v for k, v in n_gol.items() if k != "note"},
           "alta_referinta": {k: v for k, v in n_alta.items() if k != "note"},
           "la_fel_de_doua_ori": n_alta == din_nou,
           "referinte_gresite": [x for x in n_ref["note"] if not x["corect"]][:20]}
    rez["trecuta"] = {"referinte_corect_min_95": n_ref["toate"]["corect"] >= 95,
                      "gol_corect_0": n_gol["toate"]["corect"] == 0,
                      "alta_referinta_corect_max_5": n_alta["toate"]["corect"] <= 5,
                      "la_fel_de_doua_ori": rez["la_fel_de_doua_ori"]}
    rez["toate_trecute"] = all(rez["trecuta"].values())
    return rez


# --- S76c: numerele întregi și instrucțiunile formulate altfel ------------------------------------------------------

_NUMAR_TOT = re.compile(r"\d+(?:[.,]\d+)*")
_LOCUITORI = re.compile(r"(\d+(?:[.,]\d+)*)\s+(?:de\s+)?locuitori")


def numar_intreg(s: str) -> int | None:
    """Un număr scris cu sau fără despărțitor de mii, citit întreg: „1,091” = „1.091” = „1091” → 1091;
    „3.671.032” → 3671032. Un număr zecimal („2,5”, „492,04”) → None."""
    s = s.strip().rstrip(".,")
    if not re.fullmatch(r"\d+(?:[.,]\d+)*", s):
        return None
    grupuri = re.split(r"[.,]", s)
    if len(grupuri) == 1:
        return int(s)
    if 1 <= len(grupuri[0]) <= 3 and all(len(g) == 3 for g in grupuri[1:]):
        return int("".join(grupuri))
    return None


def numere(text: str) -> list[int]:
    """Toate numerele întregi dintr-un răspuns, citite întregi (fără cele zecimale)."""
    return [n for m in _NUMAR_TOT.finditer(text) if (n := numar_intreg(m.group(0))) is not None]


def cu_puncte(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def numar_locuitori(p: dict[str, Any]) -> int | None:
    """Numărul întreg de locuitori din textul perechii („… 122,000 locuitori”), cel care se termină cu cifrele cheii
    (în S76a cheia putea fi doar ultima grupă: „122,000” → „000”)."""
    cifre = re.sub(r"\D", "", p["cheie"][0])
    for m in _LOCUITORI.finditer(p.get("text", "")):
        n = numar_intreg(m.group(1))
        if n is not None and cifre and str(n).endswith(cifre):
            return n
    return numar_intreg(p["cheie"][0])


def repara_numar(p: dict[str, Any]) -> dict[str, Any]:
    """Copie a perechii. La „locuitori” (nu la refuzuri): câmpul `numar` (întreg, cu care se notează); dacă cheia
    S76a era tăiată („091” din „1,091”), cheia și referința primesc numărul întreg, iar `reparat` ține cheia veche."""
    q = dict(p)
    if p.get("tip") != "locuitori" or p["fel"] in REFUZ or not p.get("cheie"):
        return q
    n = numar_locuitori(p)
    if n is None:
        return q
    q["numar"] = n
    vechi = p["cheie"][0]
    if numar_intreg(vechi) != n:
        nou = cu_puncte(n)
        q["cheie"] = [nou] + list(p["cheie"][1:])
        q["raspuns"] = p["raspuns"].replace(vechi, nou, 1)
        q["reparat"] = vechi
    return q


def _mare(s: str) -> str:
    return s[:1].upper() + s[1:]


# Formulările noi (cel puțin 2 pe fel). Câmpurile: {x} subiectul, {rest} restul întrebării vechi, {q} întrebarea da/nu.
REFORMULARI: dict[str, list[str]] = {
    "propozitie": ["{Cine} {verb} {x}? Explică într-o singură propoziție.",
                   "Într-o singură frază, te rog: {cine} {verb} {x}?",
                   "Descrie pe scurt {x}, cu o singură propoziție."],
    "rezuma": ["Care e ideea textului, pe scurt? O propoziție.",
               "Despre ce e vorba în text? Răspunde într-o singură frază.",
               "Fă un rezumat al textului dintr-o singură propoziție."],
    "an": ["În ce an {rest}? Doar anul, te rog.",
           "Când {rest}? Răspunde numai cu anul.",
           "Anul în care {rest} — doar cifrele, fără alte cuvinte."],
    "nume": ["Cine {rest}? Dă doar numele.",
             "Numele persoanei care {rest}, fără altceva.",
             "Spune-mi doar numele: cine {rest}?"],
    "capitala": ["Care este capitala pentru {x}? Dă doar numele.",
                 "Capitala pentru {x}? Numai numele, te rog."],
    "locuitori": ["Câți locuitori are {x}? Răspunde numai cu numărul.",
                  "Populația din {x}, în cifre? Doar numărul, te rog.",
                  "Cât de populat e {x}? Scrie numai câți locuitori are."],
    "suprafata": ["Ce suprafață are {x}? Doar cifra și unitatea.",
                  "Cât de mare e {x}, ca suprafață? Răspunde numai cu suprafața."],
    "judet_tara": ["{x} — {unitatea} și țara?",
                   "În ce {unitate} și în ce țară se află {x}? Spune-le pe amândouă.",
                   "Unde e {x}: ce {unitate}, ce țară?"],
    "da_nu": ["Da sau nu: {q}",
              "{q} Spune doar da sau nu.",
              "Te rog, numai „da” sau „nu”: {q}"],
}

_VECHI = [
    ("propozitie", re.compile(r"^Spune într-o propoziție (?P<cine>cine|ce) (?P<verb>este|a fost) (?P<x>.+)\.$")),
    ("rezuma", re.compile(r"^Rezumă textul într-o propoziție\.$")),
    ("an", re.compile(r"^Scrie doar anul în care (?P<rest>.+)\.$")),
    ("capitala", re.compile(r"^Scrie numele capitalei pentru (?P<x>.+)\.$")),
    ("nume", re.compile(r"^Scrie numele celui care (?P<rest>.+)\.$")),
    ("locuitori", re.compile(r"^Scrie doar numărul de locuitori din (?P<x>.+)\.$")),
    ("suprafata", re.compile(r"^Scrie doar suprafața pe care o are (?P<x>.+)\.$")),
    ("judet_tara", re.compile(r"^Spune în ce (?P<unitate>județ|raion) se află (?P<x>.+) și din ce țară face parte\.$")),
    ("da_nu", re.compile(r"^Răspunde cu da sau nu: (?P<q>.+)$")),
]


def reformuleaza(intrebare: str, k: int) -> tuple[str, str]:
    """Instrucțiunea S76a spusă altfel: (întrebarea nouă, șablonul folosit). `k` alege șablonul (k mod câte sunt)."""
    for fel, model in _VECHI:
        m = model.match(intrebare.strip())
        if m is None:
            continue
        c = m.groupdict()
        if "cine" in c:
            c["Cine"] = _mare(c["cine"])
        if "unitate" in c:
            c["unitatea"] = c["unitate"] + "ul"
        sabloane = REFORMULARI[fel]
        sablon = sabloane[k % len(sabloane)]
        return sablon.format(**c), sablon
    raise ValueError(f"nu știu să reformulez: {intrebare!r}")


def regula_sablonului(sablon: str) -> re.Pattern[str]:
    """Expresia care recunoaște orice întrebare făcută cu șablonul (câmpurile = orice text)."""
    import string

    parti = []
    for literal, camp, _, _ in string.Formatter().parse(sablon):
        parti.append(re.escape(literal))
        if camp is not None:
            parti.append(".+?")
    return re.compile("".join(parti), re.IGNORECASE)


def reformulat(args: argparse.Namespace) -> dict[str, Any]:
    """Setul S76c: instrucțiunile setului ascuns S76a (aceleași articole, referințe și chei), cu întrebarea formulată
    altfel; numărul de locuitori citit întreg (cheia tăiată „091” reparată)."""
    from module.model_conversatie import intrebarea
    from unelte.genereaza_conversatie import normalizat

    t0 = time.time()
    dosar = RADACINA / args.dosar
    iesire = dosar / "ascuns_reformulat.jsonl"
    if iesire.exists() and not args.suprascrie:
        raise SystemExit(f"{iesire} există deja: setul reformulat nu se face a doua oară.")
    fisiere = {n: dosar / n for n in ("antrenare.jsonl", "ascuns.jsonl")}
    sha_inainte = {n: sha256(f) for n, f in fisiere.items()}
    ascuns, antrenare = citeste(fisiere["ascuns.jsonl"]), citeste(fisiere["antrenare.jsonl"])
    rng = random.Random(args.samanta)
    noi: list[dict[str, Any]] = []
    for fel in INSTRUCTIUNI:
        lista = [p for p in ascuns if p["fel"] == fel]
        rng.shuffle(lista)
        for k, p in enumerate(lista):
            intrebare, sablon = reformuleaza(p["intrebare"], k)
            q = repara_numar(p)
            q.update(id_s76a=p["id"], intrebare=intrebare, prompt=intrebarea(intrebare, p.get("text", "")),
                     sablon=sablon, intrebare_s76a=p["intrebare"])
            noi.append(q)
    rng.shuffle(noi)
    for k, q in enumerate(noi):
        q["id"] = f"r{k:04d}"

    # verificările
    sabloane = sorted({q["sablon"] for q in noi})
    reguli = {s: regula_sablonului(s) for s in sabloane}
    intrebari_antr = [p["intrebare"].strip() for p in antrenare]
    in_antrenare = {s: sum(bool(r.fullmatch(i)) for i in intrebari_antr) for s, r in reguli.items()}
    antr_norm = {normalizat(i) for i in intrebari_antr}
    asc_norm = {normalizat(p["intrebare"]) for p in ascuns}
    pe_fel = {f: sum(q["fel"] == f for q in noi) for f in INSTRUCTIUNI}
    sabloane_pe_fel = {f: len({q["sablon"] for q in noi if q["fel"] == f}) for f in INSTRUCTIUNI}
    minim = {f: 15 if f in ("instr_da_nu", "instr_nu_scrie") else 20 for f in INSTRUCTIUNI}
    verificari = {
        "formulari_noi_gasite_in_antrenare": sum(in_antrenare.values()),
        "intrebari_noi_identice_cu_antrenare": sum(normalizat(q["intrebare"]) in antr_norm for q in noi),
        "intrebari_noi_identice_cu_ascuns_s76a": sum(normalizat(q["intrebare"]) in asc_norm for q in noi),
        "total_min_200": len(noi) >= 200,
        "pe_fel_minim": all(pe_fel[f] >= minim[f] for f in INSTRUCTIUNI),
        "min_2_formulari_pe_fel": all(v >= 2 for v in sabloane_pe_fel.values()),
    }
    verificari["toate_trecute"] = (verificari["formulari_noi_gasite_in_antrenare"] == 0
                                   and verificari["intrebari_noi_identice_cu_antrenare"] == 0
                                   and verificari["total_min_200"] and verificari["pe_fel_minim"]
                                   and verificari["min_2_formulari_pe_fel"])
    # exemple din articolele de ANTRENARE (pentru raport; setul ascuns nu se arată)
    exemple, vazute = [], set()
    for p in antrenare:
        if p["fel"] in INSTRUCTIUNI and p["fel"] not in vazute and len(exemple) < args.exemple:
            nou, _ = reformuleaza(p["intrebare"], len(exemple))
            exemple.append({"fel": p["fel"], "s76a": p["intrebare"], "reformulat": nou, "raspuns": p["raspuns"]})
            vazute.add(p["fel"])
    with iesire.open("w", encoding="utf-8", newline="\n") as f:
        for q in noi:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")
    sha_dupa = {n: sha256(f) for n, f in fisiere.items()}
    info = {
        "facut": "unelte/romana_raspunsuri.py reformulat",
        "argumente": {k: v for k, v in vars(args).items() if k != "functie"},
        "sursa": "instrucțiunile setului ascuns S76a (aceleași articole, referințe, chei); nimic descărcat, niciun model",
        "intrebari": len(noi), "pe_fel": pe_fel, "sabloane_pe_fel": sabloane_pe_fel,
        "pe_sablon": dict(sorted(Counter(q["sablon"] for q in noi).items())),
        "sabloane_gasite_in_antrenare": in_antrenare, "verificari": verificari,
        "reparate": [{"id": q["id"], "id_s76a": q["id_s76a"], "cheie_veche": q["reparat"], "cheie": q["cheie"]}
                     for q in noi if "reparat" in q],
        "cu_numar_intreg": sum("numar" in q for q in noi),
        "exemple_din_antrenare": exemple,
        "sha256": {"ascuns_reformulat.jsonl": sha256(iesire)},
        "sha256_s76a_inainte": sha_inainte, "sha256_s76a_dupa": sha_dupa,
        "s76a_neschimbat": sha_inainte == sha_dupa, "secunde": round(time.time() - t0, 1),
    }
    (dosar / "info_reformulat.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    return info


def renoteaza_reparat(perechi: list[dict[str, Any]], raspunsuri: dict[str, str]) -> dict[str, Any]:
    """Nota setului S76a cu numărul reparat DOAR la perechile cu cheia tăiată (restul neatinse), pe răspunsuri vechi."""
    reparate, noi = [], []
    for p in perechi:
        q = repara_numar(p)
        if "reparat" in q:
            reparate.append({"id": p["id"], "cheie_veche": p["cheie"], "cheie": q["cheie"], "numar": q["numar"]})
            noi.append(q)
        else:
            noi.append(p)
    return {"reparate": reparate, **noteaza(noi, raspunsuri)}


# --- reperul pe placă -----------------------------------------------------------------------------------------------

class PazaPlacii(threading.Thread):
    """Citește nvidia-smi la câteva secunde și ține maximul (MB, °C)."""

    def __init__(self, la: float = 3.0) -> None:
        super().__init__(daemon=True)
        self.la, self.max_mb, self.max_c, self.oprit = la, 0, 0, threading.Event()

    def run(self) -> None:
        while not self.oprit.is_set():
            try:
                iesire = subprocess.run(["nvidia-smi", "--query-gpu=memory.used,temperature.gpu",
                                         "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=10)
                mb, c = (int(v) for v in iesire.stdout.strip().splitlines()[0].split(","))
                self.max_mb, self.max_c = max(self.max_mb, mb), max(self.max_c, c)
            except (OSError, ValueError, IndexError, subprocess.TimeoutExpired):
                pass
            self.oprit.wait(self.la)


def reper(args: argparse.Namespace) -> dict[str, Any]:
    import torch

    from kronos.cai import gaseste_model
    from kronos.jurnal import Jurnal
    from unelte.modele_salvate import fisa_modelului, incarca_modelul

    iesire = RADACINA / args.iesire
    if (iesire / "nota.json").exists():
        raise SystemExit(f"{iesire / 'nota.json'} există deja: reperul nu se reface.")
    fisier_set = RADACINA / args.set if args.set else RADACINA / args.dosar / "ascuns.jsonl"
    perechi = citeste(fisier_set)
    perechi = perechi[: args.cate] if args.cate else perechi
    fisa = fisa_modelului(Jurnal(RADACINA / "lucru"), args.experiment)
    fisiere = [Path(gaseste_model(fisa["model_salvat"]))] + [RADACINA / c for c in args.citit]
    sha_inainte = {str(f): sha256(f) for f in fisiere}
    paza = PazaPlacii()
    paza.start()
    t0 = time.time()
    model = incarca_modelul(fisa, args.dispozitiv)
    raspunsuri: dict[str, str] = {}
    with torch.no_grad():
        for k, p in enumerate(perechi):
            raspunsuri[p["id"]] = model.completeaza(p["prompt"], args.simboluri)
            if paza.max_mb > args.memorie_max:
                raise SystemExit(f"placa a trecut de {args.memorie_max} MB ({paza.max_mb} MB): opresc reperul.")
            if (k + 1) % 50 == 0:
                print(f"{k + 1}/{len(perechi)} ({time.time() - t0:.0f} s, placa max {paza.max_mb} MB / {paza.max_c} °C)",
                      flush=True)
    secunde = round(time.time() - t0, 1)
    memorie_torch = round(torch.cuda.max_memory_reserved() / 2**20) if torch.cuda.is_available() else 0
    del model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    paza.oprit.set()
    paza.join(timeout=15)
    sha_dupa = {str(f): sha256(f) for f in fisiere}
    iesire.mkdir(parents=True, exist_ok=True)
    (iesire / "raspunsuri.json").write_text(json.dumps({"experiment": fisa["id"], "linie": fisa["linie"],
                                                        "raspunsuri": raspunsuri}, ensure_ascii=False, indent=1),
                                            encoding="utf-8")
    nota = noteaza(perechi, raspunsuri)
    meta = {"experiment": fisa["id"], "linie": fisa["linie"], "intrebari": len(perechi), "simboluri": args.simboluri,
            "secunde": secunde, "placa_max_mb": paza.max_mb, "placa_max_c": paza.max_c,
            "torch_max_rezervat_mb": memorie_torch, "sha256_inainte": sha_inainte, "sha256_dupa": sha_dupa,
            "greutati_neschimbate": sha_inainte == sha_dupa, "set": sha256(fisier_set),
            "set_fisier": fisier_set.relative_to(RADACINA).as_posix() if fisier_set.is_relative_to(RADACINA)
            else str(fisier_set), "dispozitiv": args.dispozitiv or "implicit"}
    (iesire / "nota.json").write_text(json.dumps({"meta": meta, **nota}, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"meta": meta, **{k: v for k, v in nota.items() if k != "note"}}


# --- comanda --------------------------------------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="S76a: răspunsuri în română (exerciții, set ascuns, notă automată).")
    sub = parser.add_subparsers(dest="comanda", required=True)
    c = sub.add_parser("construieste", help="antrenare.jsonl, ascuns.jsonl, info.json")
    c.add_argument("--articole", type=int, default=7000, help="atâtea articole pentru antrenare")
    c.add_argument("--articole-ascuns", type=int, default=4000, help="rezerva din care se alege setul ascuns")
    c.add_argument("--instructiuni", type=float, default=0.5, help="partea instrucțiunilor în antrenare")
    c.add_argument("--conversatie-ori", type=int, default=5)
    c.add_argument("--samanta", type=int, default=7601)
    c.add_argument("--dosar", default=DOSAR)
    c.add_argument("--suprascrie", action="store_true", help="doar pentru teste: setul ascuns nu se reface")
    n = sub.add_parser("noteaza", help="nota automată pe un fișier de răspunsuri")
    n.add_argument("--raspunsuri", required=True)
    n.add_argument("--set", default=f"{DOSAR}/ascuns.jsonl")
    n.add_argument("--iesire", required=True)
    pr = sub.add_parser("proba", help="proba notei")
    pr.add_argument("--set", default=f"{DOSAR}/ascuns.jsonl")
    pr.add_argument("--iesire", default=f"{DOSAR}/proba_nota.json")
    r = sub.add_parser("reper", help="un model salvat scrie răspunsurile la setul ascuns, apoi nota")
    r.add_argument("--experiment", type=int, required=True)
    r.add_argument("--iesire", required=True)
    r.add_argument("--dosar", default=DOSAR)
    r.add_argument("--simboluri", type=int, default=64)
    r.add_argument("--cate", type=int, default=0)
    r.add_argument("--dispozitiv", default="")
    r.add_argument("--memorie-max", type=int, default=6800)
    r.add_argument("--citit", nargs="*", default=[], help="alte fișiere doar citite, cu SHA-256 înainte și după")
    r.add_argument("--set", default="", help="alt set decât <dosar>/ascuns.jsonl (ex. ascuns_reformulat.jsonl)")
    f = sub.add_parser("reformulat", help="S76c: instrucțiunile setului ascuns, formulate altfel")
    f.add_argument("--dosar", default=DOSAR)
    f.add_argument("--samanta", type=int, default=7603)
    f.add_argument("--exemple", type=int, default=5, help="exemple din articolele de antrenare, pentru raport")
    f.add_argument("--suprascrie", action="store_true", help="doar pentru teste: setul nu se reface")
    rn = sub.add_parser("renoteaza-reparat", help="S76c: nota S76a cu numărul reparat, pe răspunsuri vechi")
    rn.add_argument("--raspunsuri", required=True)
    rn.add_argument("--set", default=f"{DOSAR}/ascuns.jsonl")
    rn.add_argument("--iesire", required=True)
    args = parser.parse_args(argv)

    if args.comanda == "construieste":
        rez = construieste(args)
    elif args.comanda == "reformulat":
        rez = reformulat(args)
    elif args.comanda == "renoteaza-reparat":
        rez = renoteaza_reparat(citeste(RADACINA / args.set), citeste_raspunsuri(RADACINA / args.raspunsuri))
        Path(RADACINA / args.iesire).parent.mkdir(parents=True, exist_ok=True)
        (RADACINA / args.iesire).write_text(json.dumps(rez, ensure_ascii=False, indent=1), encoding="utf-8")
        rez = {k: v for k, v in rez.items() if k != "note"}
    elif args.comanda == "noteaza":
        perechi = citeste(RADACINA / args.set)
        rez = noteaza(perechi, citeste_raspunsuri(RADACINA / args.raspunsuri))
        Path(RADACINA / args.iesire).parent.mkdir(parents=True, exist_ok=True)
        (RADACINA / args.iesire).write_text(json.dumps(rez, ensure_ascii=False, indent=1), encoding="utf-8")
        rez = {k: v for k, v in rez.items() if k != "note"}
    elif args.comanda == "proba":
        rez = proba(citeste(RADACINA / args.set))
        (RADACINA / args.iesire).write_text(json.dumps(rez, ensure_ascii=False, indent=1), encoding="utf-8")
    else:
        rez = reper(args)
    print(json.dumps(rez, ensure_ascii=False, indent=1), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
