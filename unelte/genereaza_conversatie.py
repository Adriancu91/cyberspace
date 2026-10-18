"""Școala de conversație (15 octombrie 2026, cerută de Adrian): profesorul scrie perechi întrebare → răspuns pentru Kronos,
le notează pe loc și le păstrează doar pe cele bune.

Trei feluri de perechi (~80% în română, ~20% în engleză):
- **zi**: întrebări simple de zi cu zi și explicații scurte („Ce este fotosinteza?”, „Cum fac o omletă?”), pe temele din
  TEME, cu răspunsuri de 1–4 propoziții, corecte și simple;
- **fapte**: întrebări despre cele 50 de fapte ale hranei (date/fapte/), doar cele nemarcate greșite de om
  (module/fapte_gresite.py), ca modelul să le lege de răspunsuri;
- **nu_stiu**: întrebări la care răspunsul corect e „Nu știu sigur.” (în engleză: „I don't know for sure.”): oameni sau
  locuri inventate, amănunte prea mărunte, lucruri despre azi și acum. Așa nu învață să inventeze.
Profesorul notează fiecare pereche 1–10 (corectitudine și limbă corectă); rămân doar cele cu cel puțin 8.

Se scot și (rămân în toate.jsonl, cu motivul):
- întrebările repetate (aceeași întrebare, fără să conteze majusculele și semnele);
- perechile care au o bucată de 8 cuvinte la rând din examenul de fapte nou, din setul sacru sau din validările puse
  deoparte (poveștile, româna, traducerea, codul): examenele rămân nevăzute;
- din 15 octombrie, 10:50 (Adrian): perechile românești cu un cuvânt necunoscut (unelte/ortografie_ro.py: lista din
  Wikipedia și Wikisource; nume proprii și excepții permise). Cu --refiltreaza, filtrul se aplică și perechilor deja
  scrise (toate.jsonl se rescrie; cel vechi rămâne alături, cu data).

La sfârșit (sau cu --finalizeaza): 300 de perechi bune puse deoparte ca examen de conversație nevăzut (cu ~10% „nu
știu”), restul pentru antrenare, și 30 alese la întâmplare în docs/conversatie_de_verificat.md, pentru Adrian.
Fișierele, în date/conversatie/: toate.jsonl (fiecare pereche scrisă), antrenare.jsonl, examen.json, antrenare.txt
(„Întrebare: … / Răspuns: …”, despărțite de „<|endoftext|>”), info.json. În jurnalul Kronos, o fișă doar cu numere.

    python unelte/genereaza_conversatie.py --pana-la 18:20 --perechi 15000 --doar-local
    python unelte/genereaza_conversatie.py --cereri 16 --doar-local          # probă
    python unelte/genereaza_conversatie.py --finalizeaza                      # doar împărțirea și fișierele de la sfârșit
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
import time
import unicodedata
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from kronos.jurnal import Jurnal  # noqa: E402

DOSAR = "date/conversatie"
NOTA_MINIMA = 8
PERECHI_PE_CERERE = 5
EXAMEN, EXAMEN_NU_STIU, VERIFICAT = 300, 30, 30
NU_STIU = {"ro": "Nu știu sigur.", "en": "I don't know for sure."}
FRAGMENT = 8  # cuvinte la rând: o pereche cu o astfel de bucată dintr-un examen sau dintr-o validare e scoasă
SEPARATOR = "\n<|endoftext|>\n"
# Textele care trebuie să rămână nevăzute (din ele se iau toate bucățile de FRAGMENT cuvinte).
INTERZISE_JSON = ["date/fapte/examen_nou.json", "date/fapte/examen_sacru.json"]
INTERZISE_TEXT = ["date/tinystories_r2/validare.txt", "date/ws/curat/wikipedia_ro/validare.txt",
                  "date/ws/curat/fineweb2_ro/validare.txt", "date/ws/curat/wikisource_ro/validare.txt",
                  "date/ws/curat/fabule_ro/validare.txt", "date/ws/curat/europarl_en_ro/validare.txt",
                  "date/ws/curat/cod_stack/validare.txt", "date/ws/curat/cod_instruct/validare.txt"]
CARACTERE_VALIDARE = 400_000  # din fiecare validare (examenele folosesc primele 100.000)

# Ordinea cererilor, pe cicluri de 20: 15 „zi”, 4 „fapte”, 1 „nu_stiu”; în fiecare fel, 4 din 5 în română.
CICLU = ["zi"] * 15 + ["fapte"] * 4 + ["nu_stiu"]
TEME = [
    "vremea și anotimpurile", "plantele", "animalele de companie", "animalele sălbatice", "corpul omenesc", "sănătatea",
    "igiena", "mâncarea sănătoasă", "gătitul simplu", "bucătăria românească", "fructele și legumele", "apa",
    "focul și siguranța", "electricitatea în casă", "casa și curățenia", "grădinăritul", "școala și învățatul",
    "cititul și cărțile", "matematica de zi cu zi", "banii și cumpărăturile", "timpul și ceasul", "calendarul",
    "transportul", "bicicleta", "mașinile", "trenurile și avioanele", "orașul", "satul", "munții", "marea și râurile",
    "cerul, Soarele și Luna", "stelele și planetele", "pământul și rocile", "vulcanii și cutremurele", "ploaia și norii",
    "zăpada și gheața", "lumina și culorile", "sunetul și muzica", "sportul", "jocurile copiilor", "prietenia",
    "politețea", "emoțiile", "somnul", "îmbrăcămintea", "meseriile", "medicul și farmacia", "dinții", "ochii și vederea",
    "insectele", "păsările", "peștii și apa", "pădurea", "reciclarea și natura", "energia", "magneții",
    "telefonul și calculatorul", "internetul în siguranță", "geografia simplă", "România", "Europa", "limbile lumii",
    "istoria pe scurt", "inventatori și invenții", "corpul și mișcarea", "primul ajutor simplu", "animalele de fermă",
    "pâinea și grâul", "laptele și brânza", "ouăle", "cafeaua și ceaiul", "zahărul", "sarea", "căldura și frigul",
    "vântul", "curcubeul", "umbra", "oglinda", "roata", "hârtia",
]
UNGHIURI = ["ce este", "de ce", "cum se face", "care e diferența dintre două lucruri", "un sfat practic", "cum funcționează"]
FELURI_NU_STIU = [
    "despre o persoană inventată, cu nume și prenume, care nu e cunoscută (ex. ce a mâncat ieri)",
    "despre un loc inventat (un sat, o stradă, un magazin) și amănunte despre el",
    "despre azi și acum (vremea de azi dintr-un oraș, prețul de azi al unui lucru, ce oră e acum)",
    "despre amănunte prea mărunte, pe care nu le știe nimeni sigur (ex. câte frunze are un anume copac)",
    "despre viitor (cine va câștiga un meci, ce număr va ieși)",
    "despre cel care întreabă (cum îl cheamă, ce are în buzunar, unde locuiește)",
]

SISTEM_RO = ("Ești un profesor răbdător care scrie întrebări și răspunsuri pentru un copil isteț. Scrii într-o română "
             "corectă, cu diacritice (ă, â, î, ș, ț), în propoziții simple. Răspunsurile sunt adevărate.")
SISTEM_EN = ("You are a patient teacher who writes questions and answers for a bright child, in simple, correct English. "
             "The answers are true.")
SISTEM_NOTA = "You are a strict but fair teacher who checks question-and-answer pairs written for children."
_PERECHE = re.compile(r"^\s*(?:\d+[.)]\s*)?(Î|I|Q|Întrebare|Question)\s*:\s*(.+?)\s*\n\s*(R|A|Răspuns|Answer)\s*:\s*(.+?)\s*$",
                      re.IGNORECASE | re.MULTILINE)
_NOTA = re.compile(r"(?:GRADE|NOTA|NOTĂ)\s*:\s*(\d+)", re.IGNORECASE)
_MOTIV = re.compile(r"(?:REASON|MOTIV)\s*:\s*(.+)", re.IGNORECASE)


# --- cererile -------------------------------------------------------------------------------------------------------

def cererea(k: int, fapte: list[tuple[str, str]], doar_engleza: bool = False) -> dict[str, Any]:
    """A k-a cerere (de la 0): felul (după CICLU), limba (4 din 5 în română; cu doar_engleza, toate în engleză) și ce se
    cere."""
    fel = CICLU[k % len(CICLU)]
    limba = "en" if doar_engleza or (k // len(CICLU) + k) % 5 == 4 else "ro"
    runda = k // len(CICLU)
    if fel == "zi":
        tema = TEME[(k * 7 + runda) % len(TEME)]
        return {"fel": fel, "limba": limba, "tema": tema, "unghi": UNGHIURI[(k + runda) % len(UNGHIURI)]}
    if fel == "fapte":
        subiect, fapt = fapte[(k // len(CICLU) * 4 + CICLU[: k % len(CICLU)].count("fapte")) % len(fapte)]
        return {"fel": fel, "limba": limba, "subiect": subiect, "fapt": fapt}
    return {"fel": fel, "limba": limba, "tip": FELURI_NU_STIU[runda % len(FELURI_NU_STIU)]}


def mesaje_cerere(c: dict[str, Any], n: int = PERECHI_PE_CERERE) -> list[dict[str, str]]:
    ro = c["limba"] == "ro"
    forma = (f"Scrie exact {n} perechi, fiecare pe două rânduri:\nÎ: <întrebarea>\nR: <răspunsul>\nFără numerotare și "
             "fără alt text." if ro else
             f"Write exactly {n} pairs, each on two lines:\nQ: <the question>\nA: <the answer>\nNo numbering and no other "
             "text.")
    if c["fel"] == "zi":
        cerinta = (f"Scrie {n} întrebări diferite, simple, de zi cu zi, despre: {c['tema']} (mai ales „{c['unghi']}”). "
                   "Răspunsul are 1–4 propoziții scurte, corecte și ușor de înțeles." if ro else
                   f"Write {n} different simple everyday questions about this topic (in English): {c['tema']} (mostly "
                   f"„{c['unghi']}”). Each answer has 1–4 short sentences, correct and easy to understand.")
    elif c["fel"] == "fapte":
        cerinta = (f"Faptul adevărat: „{c['fapt']}” Scrie {n} întrebări diferite, puse în feluri diferite, la care "
                   "răspunsul e acest fapt, spus în română în 1–2 propoziții simple (traducere fidelă, fără alte fapte)."
                   if ro else
                   f"The true fact: \"{c['fapt']}\" Write {n} different questions, asked in different ways, whose answer "
                   "is this fact, said in 1–2 simple sentences (no other facts).")
    else:
        cerinta = (f"Scrie {n} întrebări la care nimeni nu poate ști sigur răspunsul, {c['tip']}. La toate, răspunsul "
                   f"este exact: {NU_STIU['ro']}" if ro else
                   f"Write {n} questions that nobody can answer for sure, {c['tip']} (write them in English). For all of "
                   f"them the answer is exactly: {NU_STIU['en']}")
    return [{"role": "system", "content": SISTEM_RO if ro else SISTEM_EN}, {"role": "user", "content": cerinta + "\n\n" + forma}]


def citeste_perechi(text: str) -> list[tuple[str, str]]:
    return [(m.group(2).strip(), m.group(4).strip()) for m in _PERECHE.finditer(text)]


def mesaje_nota(p: dict[str, Any]) -> list[dict[str, str]]:
    limba = "Romanian" if p["limba"] == "ro" else "English"
    nu_stiu = (f" This is a question nobody can answer for sure; the expected answer is \"{NU_STIU[p['limba']]}\". Give a "
               "high grade only if the question really cannot be known for sure." if p["fel"] == "nu_stiu" else "")
    return [{"role": "system", "content": SISTEM_NOTA}, {"role": "user", "content": (
        f"Grade this question-and-answer pair (in {limba}) from 1 to 10.{nu_stiu}\n"
        "Check: is the answer true and does it answer the question? Is it short and simple (1–4 sentences)? Is the "
        f"{limba} correct (grammar, spelling" + (", diacritics ă â î ș ț" if p["limba"] == "ro" else "") + ")?\n"
        "Be strict. Give 8 or more ONLY if every sentence is true and the language is natural, as a careful native "
        "speaker writes it. Any false or doubtful statement, any made-up or wrong word, any grammar or agreement "
        "mistake, or an answer that does not really answer the question: at most 6.\n"
        "10 = perfect. 8 = correct and natural, only a tiny stylistic flaw. 5 = partly wrong or clumsy. 1 = wrong.\n\n"
        f"Question: {p['intrebare']}\nAnswer: {p['raspuns']}\n\n"
        "Answer in exactly two lines:\nGRADE: <a whole number from 1 to 10>\nREASON: <one short sentence>")}]


def citeste_nota(text: str) -> dict[str, Any]:
    nota, motiv = _NOTA.search(text), _MOTIV.search(text)
    return {"nota": min(10, max(1, int(nota.group(1)))) if nota else None,
            "motiv": motiv.group(1).strip() if motiv else text.strip()[:200]}


# --- filtrele -------------------------------------------------------------------------------------------------------

def normalizat(text: str) -> str:
    """Litere mici, fără semne și fără diacritice, cu spațiile strânse."""
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return " ".join(re.sub(r"[^a-z0-9 ]+", " ", text).split())


def bucati(text: str, n: int = FRAGMENT) -> set[str]:
    cuvinte = normalizat(text).split()
    return {" ".join(cuvinte[i:i + n]) for i in range(len(cuvinte) - n + 1)}


def texte_din_json(valoare: Any) -> list[str]:
    if isinstance(valoare, str):
        return [valoare]
    if isinstance(valoare, dict):
        return [t for v in valoare.values() for t in texte_din_json(v)]
    if isinstance(valoare, list):
        return [t for v in valoare for t in texte_din_json(v)]
    return []


def bucati_interzise(radacina: Path = RADACINA) -> set[str]:
    interzise: set[str] = set()
    for cale in INTERZISE_JSON:
        fisier = radacina / cale
        if fisier.exists():
            for t in texte_din_json(json.loads(fisier.read_text(encoding="utf-8"))):
                interzise |= bucati(t)
    for cale in INTERZISE_TEXT:
        fisier = radacina / cale
        if fisier.exists():
            with fisier.open(encoding="utf-8") as f:
                interzise |= bucati(f.read(CARACTERE_VALIDARE))
    return interzise


def de_ce_se_scoate(p: dict[str, Any], vazute: set[str], interzise: set[str],
                    ortografie: tuple[set[str], set[str]] | None = None) -> str | None:
    if p.get("nota") is None:
        return "fără notă"
    if p["nota"] < NOTA_MINIMA:
        return "nota sub 8"
    if p.get("profesor", "").startswith("Qwen/") and p["limba"] == "ro" and p["fel"] in ("zi", "nu_stiu"):
        return "română liberă de la Qwen (scoasă de Adrian, 15 octombrie)"
    if p["fel"] == "nu_stiu" and normalizat(p["raspuns"]) != normalizat(NU_STIU[p["limba"]]):
        return "„nu știu” cu alt răspuns"
    if p["fel"] != "nu_stiu" and normalizat(p["raspuns"]) in {normalizat(x) for x in NU_STIU.values()}:
        return "„nu știu” la o întrebare care se știe"
    if normalizat(p["intrebare"]) in vazute:
        return "întrebare repetată"
    if bucati(p["intrebare"] + " " + p["raspuns"]) & interzise:
        return "bucată dintr-un examen sau dintr-o validare"
    if ortografie is not None and p["limba"] == "ro":
        from unelte.ortografie_ro import necunoscute

        gresite = necunoscute(p["intrebare"] + chr(10) + p["raspuns"], *ortografie)
        if gresite:
            return "cuvânt necunoscut: " + ", ".join(gresite[:3])
    return None


# --- sfârșitul: examenul, antrenarea, fișa de verificat ---------------------------------------------------------------

def text_antrenare(p: dict[str, Any]) -> str:
    return f"Întrebare: {p['intrebare']}\nRăspuns: {p['raspuns']}"


# Din 15 octombrie, 11:20 (Adrian): sursele românești noi, lângă perechile profesorului (doar engleză și fapte).
SURSE_EXTRA = ["wikipedia.jsonl", "traduceri.jsonl", "nu_stiu_ro.jsonl"]


def grup(p: dict[str, Any]) -> str:
    """O pereche și traducerea ei au același grup (nu se despart între examen și antrenare)."""
    if p.get("grup"):
        return p["grup"]
    if p["limba"] == "en" and p["fel"] == "zi":
        return "en:" + normalizat(p["intrebare"])
    return f"{p.get('profesor', '')}:{p.get('cerere')}:{normalizat(p['intrebare'])}"


def surse_extra(dosar: Path, vazute: set[str], interzise: set[str],
                ortografie: tuple[set[str], set[str]] | None) -> list[dict[str, Any]]:
    """Perechile din SURSE_EXTRA (Wikipedia, traduceri, „nu știu” în română), cu filtrele: întrebările repetate,
    bucățile din examene și validări, ortografia. Fiecare primește „ramane” și „motiv_scos”, ca în toate.jsonl."""
    rezultat: list[dict[str, Any]] = []
    # 15 octombrie, 15:00 (Adrian): o sursă cu peste 2 greșite din 15 la verificare iese din antrenare; numele ei se
    # scrie în surse_excluse.txt (câte unul pe rând), după răspunsul lui
    excluse_f = dosar / "surse_excluse.txt"
    excluse = {r.strip() for r in excluse_f.read_text(encoding="utf-8").splitlines() if r.strip()} if excluse_f.exists() else set()
    for nume in SURSE_EXTRA:
        fisier = dosar / nume
        if not fisier.exists() or nume in excluse:
            continue
        for rand in fisier.read_text(encoding="utf-8").splitlines():
            if not rand.strip():
                continue
            p = json.loads(rand)
            motiv = None
            if normalizat(p["intrebare"]) in vazute:
                motiv = "întrebare repetată"
            elif bucati(p["intrebare"] + " " + p["raspuns"]) & interzise:
                motiv = "bucată dintr-un examen sau dintr-o validare"
            elif ortografie is not None and p["limba"] == "ro":
                from unelte.ortografie_ro import necunoscute

                gresite = necunoscute(p["intrebare"] + chr(10) + p["raspuns"], *ortografie)
                if gresite:
                    motiv = "cuvânt necunoscut: " + ", ".join(gresite[:3])
            p.update(ramane=motiv is None, motiv_scos=motiv, sursa_fisier=nume)
            if motiv is None:
                vazute.add(normalizat(p["intrebare"]))
            rezultat.append(p)
    return rezultat


def imparte(bune: list[dict[str, Any]], samanta: int = 0) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """(examen, antrenare): EXAMEN perechi nevăzute, dintre care EXAMEN_NU_STIU „nu știu” (dacă sunt), restul la
    întâmplare. Tot grupul unei perechi din examen (ex. originalul ei în engleză) iese din antrenare."""
    rng = random.Random(samanta)
    nu_stiu = [p for p in bune if p["fel"] == "nu_stiu"]
    altele = [p for p in bune if p["fel"] != "nu_stiu"]
    rng.shuffle(nu_stiu)
    rng.shuffle(altele)
    k = min(EXAMEN_NU_STIU, len(nu_stiu))
    examen = nu_stiu[:k] + altele[: max(0, EXAMEN - k)]
    grupuri = {grup(p) for p in examen}
    in_examen = {id(p) for p in examen}
    return examen, [p for p in bune if id(p) not in in_examen and grup(p) not in grupuri]


# 18 octombrie 2026 (Adrian): examenul lui W2-conv. 50 de întrebări din Wikipedia v3 pe care Adrian nu le-a văzut în
# fișe, 20 „nu știu” despre lucruri inventate și 10 de conversație, scrise de mână (SCRISE_DE_MANA). Nimic din examen
# (nici aceeași întrebare, nici același grup) nu intră în antrenare.
EXAMEN_WIKI = 50
SCRISE_DE_MANA = "docs/conversatie/examen_scris_de_mana.json"
VAZUTE_IN_FISE = ["docs/conversatie/verificate_pana_la_17oct.json", "docs/conversatie_de_verificat.md"]
# perechile găsite greșite de Adrian în fișa v3 (17 octombrie, #1 și #9): nu intră nici în antrenare, nici în examen
GRESITE_IN_FISE = ["Cine a fost Infantele Gabriel al Spaniei?", "Ce este Împărțirea la zero?"]


def intrebari_din_fise(radacina: Path = RADACINA) -> set[str]:
    """Întrebările pe care Adrian le-a văzut deja: lista JSON a celor verificate și fișa de acum („- Întrebare: …”)."""
    vazute: set[str] = set()
    for nume in VAZUTE_IN_FISE:
        cale = radacina / nume
        if not cale.exists():
            continue
        text = cale.read_text(encoding="utf-8")
        lista = json.loads(text) if cale.suffix == ".json" else re.findall(r"^- Întrebare: (.+)$", text, re.MULTILINE)
        vazute |= {normalizat(q) for q in lista}
    return vazute


def imparte_v3(bune: list[dict[str, Any]], vazute_in_fise: set[str], scrise: dict[str, Any],
               samanta: int = 1018) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """(examen, antrenare) pentru W2-conv: EXAMEN_WIKI perechi Wikipedia nevăzute în fișe, la întâmplare, plus cele
    scrise de mână. Din antrenare ies grupurile și întrebările din examen."""
    wiki = [p for p in bune if p.get("sursa_fisier") == "wikipedia.jsonl" and normalizat(p["intrebare"]) not in vazute_in_fise]
    random.Random(samanta).shuffle(wiki)
    de_mana = [{"fel": "nu_stiu", "limba": p["limba"], "intrebare": p["intrebare"], "raspuns": NU_STIU[p["limba"]],
                "sursa": "scrise de Claude Code (lucruri inventate)", "grup": f"examen_nu_stiu_{k}"}
               for k, p in enumerate(scrise["nu_stiu"])]
    de_mana += [{"fel": "conversatie", "limba": p["limba"], "intrebare": p["intrebare"], "raspuns": p["raspuns"],
                 "sursa": "scrise de Claude Code", "grup": f"examen_conversatie_{k}"} for k, p in enumerate(scrise["conversatie"])]
    examen = wiki[:EXAMEN_WIKI] + de_mana
    grupuri = {grup(p) for p in examen}
    intrebari = {normalizat(p["intrebare"]) for p in examen} | {normalizat(q) for q in GRESITE_IN_FISE}
    return examen, [p for p in bune if grup(p) not in grupuri and normalizat(p["intrebare"]) not in intrebari]


def fisa_de_verificat(antrenare: list[dict[str, Any]], samanta: int = 0, titlu: str | None = None) -> str:
    alese = antrenare if titlu else random.Random(samanta).sample(antrenare, min(VERIFICAT, len(antrenare)))
    randuri = ["# Conversația de verificat (pentru Adrian)", "",
               f"*{titlu or f'{len(alese)} perechi alese la întâmplare din cele {len(antrenare)} de antrenare'} "
               f"(date/conversatie/). Spune-mi numerele celor greșite și ce e greșit (faptul, româna sau forma).*", ""]
    for i, p in enumerate(alese, start=1):
        sursa = p.get("sursa") or p.get("profesor") or "profesor"
        litera = {"wikipedia.jsonl": "W", "traduceri.jsonl": "T"}.get(p.get("sursa_fisier", ""), "")
        randuri += [f"**{i}. {litera}**" if litera else f"**{i}.**", "",
                    f"({p['fel']}, {'română' if p['limba'] == 'ro' else 'engleză'}, {sursa})", "",
                    f"- Întrebare: {p['intrebare']}", f"- Răspuns: {p['raspuns']}", ""]
    return "\n".join(randuri)


def refiltreaza(dosar: Path, interzise: set[str], ortografie: tuple[set[str], set[str]]) -> dict[str, int]:
    """Filtrele de acum, pe toate perechile scrise, în ordinea lor (o întrebare repetată rămâne prima oară). Fișierul
    vechi rămâne alături. Întoarce câte au ieșit, pe motive (doar cele care rămâneau înainte)."""
    fisier = dosar / "toate.jsonl"
    randuri = [json.loads(r) for r in fisier.read_text(encoding="utf-8").splitlines() if r.strip()]
    fisier.replace(dosar / f"toate_inainte_{datetime.now():%Y%m%d_%H%M%S}.jsonl")
    vazute: set[str] = set()
    iesite: Counter[str] = Counter()
    with fisier.open("w", encoding="utf-8") as f:
        for p in randuri:
            p.setdefault("profesor", "Qwen/Qwen3-4B-Instruct-2507")  # perechile scrise înainte de câmpul „profesor”
            motiv = de_ce_se_scoate(p, vazute, interzise, ortografie)
            if p.get("ramane") and motiv is not None:
                iesite[motiv.split(":")[0]] += 1
            p.update(ramane=motiv is None, motiv_scos=motiv)
            if motiv is None:
                vazute.add(normalizat(p["intrebare"]))
            f.write(json.dumps(p, ensure_ascii=False) + chr(10))
    return dict(iesite)


def toate_bune(dosar: Path, interzise: set[str] | None = None,
               ortografie: tuple[set[str], set[str]] | None = None) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """(toate perechile, cele bune): ale profesorului (toate.jsonl, filtrate deja) și ale surselor noi (filtrate acum)."""
    if interzise is None:
        interzise = bucati_interzise()
    if ortografie is None:
        from unelte.ortografie_ro import citeste_exceptii, citeste_lista

        ortografie = (citeste_lista(), citeste_exceptii())
    toate = [json.loads(r) for r in (dosar / "toate.jsonl").read_text(encoding="utf-8").splitlines() if r.strip()]
    vazute = {normalizat(p["intrebare"]) for p in toate if p.get("ramane")}
    toate += surse_extra(dosar, vazute, interzise, ortografie)
    return toate, [p for p in toate if p.get("ramane")]


def scrie_fisa_wikipedia(dosar: Path, docs: Path, samanta: int = 1, cate: int = 30,
                         fara: set[str] | None = None) -> int:
    """Fișa din 16 octombrie, 12:00 (Adrian): 30 de perechi doar din Wikipedia (după toate filtrele), toate „W”.
    Din 17 octombrie, 11:00: aceeași fișă, pe Wikipedia v3 (doar prima propoziție), fără întrebările din `fara` (cele
    verificate deja, în fișe sau la mână)."""
    _, bune = toate_bune(dosar)
    vazute = {normalizat(q) for q in fara or ()}
    wiki = [p for p in bune if p.get("sursa_fisier") == "wikipedia.jsonl" and normalizat(p["intrebare"]) not in vazute]
    alese = random.Random(samanta).sample(wiki, min(cate, len(wiki)))
    docs.parent.mkdir(parents=True, exist_ok=True)
    docs.write_text(fisa_de_verificat(alese, samanta, titlu=(
        f"{len(alese)} de perechi alese la întâmplare doar din Wikipedia (W), din {len(wiki)} bune"
        f"{', altele decât cele verificate deja' if vazute else ''} (sămânța {samanta}), după curățarea "
        f"v3 din 17 octombrie (răspunsul = doar prima propoziție, cel mult 30 de cuvinte, fără liste). Regula: cel mult "
        f"3 greșite din 30 → W2-conv poate porni")), encoding="utf-8")
    return len(wiki)


def scrie_fisa(dosar: Path, docs: Path, samanta: int = 0, interzise: set[str] | None = None,
               ortografie: tuple[set[str], set[str]] | None = None) -> dict[str, int]:
    """Fișa pentru Adrian (15 octombrie, 16:00): 30 de perechi românești bune, la întâmplare, 15 din Wikipedia și 15
    din traducere (după toate filtrele)."""
    _, bune = toate_bune(dosar, interzise, ortografie)
    rng = random.Random(samanta)
    wiki = [p for p in bune if p.get("sursa_fisier") == "wikipedia.jsonl"]
    trad = [p for p in bune if p.get("sursa_fisier") == "traduceri.jsonl"]
    alese = rng.sample(wiki, min(15, len(wiki))) + rng.sample(trad, min(15, len(trad)))
    docs.parent.mkdir(parents=True, exist_ok=True)
    docs.write_text(fisa_de_verificat(alese, samanta, titlu=(
        f"30 de perechi românești alese la întâmplare după toate filtrele: W = din Wikipedia ({min(15, len(wiki))}, din "
        f"{len(wiki)} bune), T = traduse din engleză cu opus-mt-en-ro ({min(15, len(trad))}, din {len(trad)} bune). Se "
        f"judecă fiecare sursă separat: peste 2 greșite din 15 = sursa iese din antrenarea de la noapte")),
        encoding="utf-8")
    return {"wikipedia": len(wiki), "traduceri": len(trad)}


def finalizeaza(dosar: Path, docs: Path, jurnal: Jurnal | None, extra: dict[str, Any] | None = None,
                v3: bool = False) -> dict[str, Any]:
    toate, bune = toate_bune(dosar)
    if v3:
        scrise = json.loads((RADACINA / SCRISE_DE_MANA).read_text(encoding="utf-8"))
        examen, antrenare = imparte_v3(bune, intrebari_din_fise(), scrise)
    else:
        examen, antrenare = imparte(bune)
    (dosar / "examen.json").write_text(json.dumps({
        "nota": "examenul de conversație: nevăzut la antrenare; nu intră în nicio altă hrană",
        "perechi": examen}, ensure_ascii=False, indent=1), encoding="utf-8")
    with (dosar / "antrenare.jsonl").open("w", encoding="utf-8") as f:
        for p in antrenare:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    (dosar / "antrenare.txt").write_text(SEPARATOR.join(text_antrenare(p) for p in antrenare) + SEPARATOR,
                                         encoding="utf-8")
    if not docs.exists():  # fișa scrisă mai devreme (ex. la 13:00, pentru Adrian) nu se înlocuiește
        docs.parent.mkdir(parents=True, exist_ok=True)
        docs.write_text(fisa_de_verificat(antrenare), encoding="utf-8")
    numere = lambda lista: dict(Counter(f"{p.get('sursa_fisier', 'profesor')}_{p['fel']}_{p['limba']}" for p in lista))  # noqa: E731
    info = {"data": datetime.now().isoformat(timespec="seconds"), "scrise": len(toate), "bune": len(bune),
            "antrenare": len(antrenare), "examen": len(examen), "pe_feluri_antrenare": numere(antrenare),
            "pe_feluri_examen": numere(examen),
            "scoase": dict(Counter(p["motiv_scos"] for p in toate if not p.get("ramane"))),
            "note": dict(sorted(Counter(p.get("nota") for p in toate if p.get("nota")).items())), **(extra or {})}
    (dosar / "info.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    if jurnal is not None:
        jurnal.adauga({"id": jurnal.urmatorul_id(), "linie": "conversatie",
                       "inceput": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                       "propunere": {"descriere": "școala de conversație: perechi întrebare → răspuns scrise și notate "
                                                  "de profesor (date/conversatie/)", "modificari": {}},
                       "decizie": "masurat", "scoruri": {k: v for k, v in info.items() if isinstance(v, (int, float))}})
    return info


# --- bucla ----------------------------------------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Perechi întrebare → răspuns pentru Kronos, scrise și notate de profesor.")
    parser.add_argument("--perechi", type=int, default=15000, help="se oprește la atâtea perechi bune")
    parser.add_argument("--pana-la", default="", help="ex. 18:20: nicio cerere nouă după ora asta")
    parser.add_argument("--cereri", type=int, default=0, help="cel mult atâtea cereri în rularea asta (probă)")
    parser.add_argument("--lot", type=int, default=8)
    parser.add_argument("--samanta", type=int, default=0)
    parser.add_argument("--doar-local", action="store_true")
    parser.add_argument("--finalizeaza", action="store_true", help="doar examenul, antrenarea și fișa de verificat")
    parser.add_argument("--finalizeaza-v3", action="store_true",
                        help="18 octombrie: examenul lui W2-conv (50 Wikipedia nevăzute în fișe, 20 „nu știu”, 10 de conversație)")
    parser.add_argument("--refiltreaza", action="store_true", help="filtrele de acum, pe toate perechile scrise")
    parser.add_argument("--fisa", action="store_true", help="doar fișa de verificat (30 de perechi bune de acum)")
    parser.add_argument("--fisa-wikipedia", action="store_true", help="fișa din 16 octombrie: 30 doar din Wikipedia")
    parser.add_argument("--fara", default="", help="cu --fisa-wikipedia: fișier JSON cu întrebările verificate deja")
    parser.add_argument("--profesor", default="Qwen/Qwen3-4B-Instruct-2507")
    parser.add_argument("--fara-ortografie", action="store_true")
    parser.add_argument("--doar-engleza", action="store_true", help="din 15 octombrie, 11:20: profesorul scrie doar în engleză")
    parser.add_argument("--dosar", default=DOSAR)
    parser.add_argument("--director-lucru", default="lucru")
    args = parser.parse_args(argv)

    dosar = Path(args.dosar)
    dosar.mkdir(parents=True, exist_ok=True)
    jurnal = Jurnal(Path(args.director_lucru))
    docs = RADACINA / "docs" / "conversatie_de_verificat.md"
    if args.finalizeaza or args.finalizeaza_v3:
        info = finalizeaza(dosar, docs, jurnal, v3=args.finalizeaza_v3)
        print(json.dumps(info, ensure_ascii=False), flush=True)
        return 0
    if args.fisa_wikipedia:
        fara = set(json.loads(Path(args.fara).read_text(encoding="utf-8"))) if args.fara else None
        bune = scrie_fisa_wikipedia(dosar, docs, samanta=args.samanta or 1, fara=fara)
        print(f"Fișa: 30 de perechi din Wikipedia (bune: {bune}), în {docs}", flush=True)
        return 0
    if args.fisa:
        print(f"Fișa: 30 de perechi românești (bune de acum: {scrie_fisa(dosar, docs)}), în {docs}", flush=True)
        return 0
    from unelte.ortografie_ro import citeste_exceptii, citeste_lista

    ortografie = None if args.fara_ortografie else (citeste_lista(), citeste_exceptii())
    if args.refiltreaza:
        iesite = refiltreaza(dosar, bucati_interzise(), ortografie)
        print(f"Refiltrat: au ieșit {sum(iesite.values())} perechi care rămăseseră înainte: {iesite}", flush=True)
        return 0

    from module.fapte_gresite import subiectele_gresite
    from module.profesor_qwen import SUBIECTE, ProfesorQwen

    gresite = subiectele_gresite()
    fapte = [(s, f) for s, f in SUBIECTE if s not in gresite]
    toate_f = dosar / "toate.jsonl"
    vechi = [json.loads(r) for r in toate_f.read_text(encoding="utf-8").splitlines() if r.strip()] if toate_f.exists() else []
    k = max((p["cerere"] for p in vechi), default=-1) + 1
    bune = sum(1 for p in vechi if p.get("ramane"))
    vazute = {normalizat(p["intrebare"]) for p in vechi if p.get("ramane")}
    print(f"Pornesc de la cererea {k} ({bune} perechi bune deja). Citesc textele care trebuie să rămână nevăzute…", flush=True)
    interzise = bucati_interzise()
    limita = None
    if args.pana_la:
        h, m = (int(x) for x in args.pana_la.split(":"))
        limita = datetime.now().replace(hour=h, minute=m, second=0, microsecond=0)
        if limita <= datetime.now():
            limita += timedelta(days=1)
    profesor = ProfesorQwen(model=args.profesor, lot=args.lot, max_simboluri=600, max_simboluri_nota=60, temperatura=0.6,
                            samanta=args.samanta, doar_local=args.doar_local)
    start, facute = time.monotonic(), 0
    while bune < args.perechi and (limita is None or datetime.now() < limita) and (not args.cereri or facute < args.cereri):
        if (RADACINA / args.director_lucru / "STOP").exists():
            print("Oprit: butonul STOP (lucru/STOP).", flush=True)
            break
        cereri = [cererea(k + i, fapte, args.doar_engleza) for i in range(args.lot)]
        texte = profesor.raspunde_mai_multe([mesaje_cerere(c) for c in cereri], 600)
        perechi = [{**c, "cerere": k + i, "intrebare": q, "raspuns": r, "profesor": args.profesor}
                   for i, (c, t) in enumerate(zip(cereri, texte)) for q, r in citeste_perechi(t)]
        note = [citeste_nota(t) for t in profesor.raspunde_mai_multe([mesaje_nota(p) for p in perechi], 60,
                                                                   cu_intamplare=False)] if perechi else []
        with toate_f.open("a", encoding="utf-8") as f:
            for p, n in zip(perechi, note):
                p.update(n)
                motiv = de_ce_se_scoate(p, vazute, interzise, ortografie)
                p.update(ramane=motiv is None, motiv_scos=motiv)
                if motiv is None:
                    vazute.add(normalizat(p["intrebare"]))
                    bune += 1
                f.write(json.dumps(p, ensure_ascii=False) + "\n")
        k += args.lot
        facute += args.lot
        if facute % (args.lot * 10) == 0 or args.cereri:
            minute = (time.monotonic() - start) / 60
            print(f"[{datetime.now():%H:%M}] cererea {k}: {bune} perechi bune; {facute} cereri în {minute:.1f} minute; "
                  f"memorie video {profesor.memorie_video_mb()}", flush=True)
    extra = {"secunde_rulare": round(time.monotonic() - start), "cereri_rulare": facute, **profesor.statistici(),
             "memorie_video_mb": profesor.memorie_video_mb().get("rezervata")}
    profesor.elibereaza()
    info = finalizeaza(dosar, docs, jurnal, extra)
    print(f"Gata: {info['bune']} perechi bune din {info['scrise']}; examen {info['examen']}, antrenare {info['antrenare']}. "
          f"Scoase: {info['scoase']}. Fișa pentru Adrian: {docs}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
