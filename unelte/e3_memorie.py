"""E3 „memoria în loc de parametri”, pregătirea de pe procesor (S24, 23 octombrie 2026; aprobat de Adrian pe 23 oct
10:20, punctul 3; strategia docs/rapoarte/2026-10-22_0200_strategie_nucleu_fara_llm.md §4 H2 și §7 E3).

Întrebarea: dacă îi dăm lui Kronos o întrebare, găsește indexul nostru, fără niciun model, bucata de text în care e
răspunsul? Nimic de aici nu încarcă un model și nu folosește placa sau rețeaua.

Alegerile (scrise și în raportul S24):
  - bucățile: textele de la „răspuns din text” (unelte/conversatie_text.py) au 150–700 de caractere, tăiate la sfârșit
    de propoziție; aici fiecare articol se taie la fel: propoziții întregi (aceeași regulă `_PROPOZITII`), adunate până
    la cel mult 700 de caractere; o propoziție mai lungă de 700 se taie între cuvinte;
  - căutarea: SQLite FTS5 cu BM25 (k1 = 1,2, b = 0,75, cele din SQLite), tokenizerul `unicode61` (scoate și
    diacriticele, la fel în text și în întrebare); ş/ţ → ș/ț înainte de indexare, în text și în întrebare;
  - „bună la k”: printre primele k bucăți e una care conține răspunsul de referință, cu regula principală a
    verificatorului S16 (unelte/verificator_text.py, doar citit): ≥ 80 % din cuvintele referinței sunt în bucată.

Comenzile (în ordinea din S24):
    python -X utf8 unelte/e3_memorie.py index                    # lucru/e3/index.sqlite + texte_examen.json
    python -X utf8 unelte/e3_memorie.py adauga                   # textele de examen care nu sunt deja în Wikipedia
    python -X utf8 unelte/e3_memorie.py masoara --set validare   # ≤ 6 variante de întrebare, alege la k = 5
    python -X utf8 unelte/e3_memorie.py masoara --set examene    # O SINGURĂ DATĂ, cu varianta aleasă
    python -X utf8 unelte/e3_memorie.py lungimi                  # documentele lungi față de contextul de 512

S25 (23 octombrie 2026, căutarea mai bună; ideile au venit din greșelile S24 pe examene, deci regulile sunt generale,
ajustate doar pe validare, iar examenele se rulează o singură dată):
  - (a) potrivirea „număr gol”, doar aici: din referință se scot cuvintele de umplutură (`UMPLUTURA`); dacă rămâne un
    singur număr, bucata e bună și când conține numărul ca număr întreg. Se raportează ambele potriviri (S16 și nouă);
  - (b) numele proprii (cuvintele cu majusculă care nu sunt primul cuvânt al întrebării) repetate în interogare
    (`nume_repetate`) sau obligatorii (`nume_obligatorii`, completat cu interogarea S24 când aduce prea puțin);
  - (c) paginile-listă și de dezambiguizare coborâte după celelalte (`liste`): în primele 300 de caractere „poate să
    însemne”, „se poate referi la”, „se mai poate referi”, „(dezambiguizare)”, „este o listă”, sau articolul începe cu
    „Listă ”/„Lista ”; `liste_randuri` adaugă paginile cu ≥ 20 de rânduri din care ≥ 90 % sub 50 de caractere.
    python -X utf8 unelte/e3_memorie.py liste                                # lucru/e3/liste_s25.json
    python -X utf8 unelte/e3_memorie.py masoara --set validare --runda s25   # 2 × 500 de întrebări, ≤ 6 variante noi
    python -X utf8 unelte/e3_memorie.py masoara --set examene --runda s25    # O SINGURĂ DATĂ

S26 (24 octombrie 2026, examenul nou neatins): 100 de întrebări din text_v3 (sămânța 4096), fără nicio întrebare, text,
grup sau articol comun cu eșantioanele 1024/2048 și cu examenele; fără nicio schimbare de reguli; k = 3 în plus.
    python -X utf8 unelte/e3_memorie.py examen-nou                   # lucru/e3/examen_nou_4096.json (+ _info, sha256)
    python -X utf8 unelte/e3_memorie.py masoara --set examen_nou     # O SINGURĂ DATĂ, după ce așteptările sunt urcate

Ies doar în lucru/e3/ (nu în Git: Wikipedia e CC BY-SA). Nu atinge kronos/, examenul BPB, paznicul, datele de examen
(doar citite), text_v3, e2/ sau unelte/verificator_text.py.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import sqlite3
import statistics
import sys
import time
import unicodedata
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from unelte.verificator_text import _fel_special, cuvinte, normalizeaza, verifica  # noqa: E402

WIKIPEDIA = "date/ws/curat/wikipedia_ro/antrenare.txt"
TEXT_V3 = "date/conversatie/text_v3/antrenare.jsonl"
TOKENIZER = "date/ws/bpe_16384.json"
EXAMENE = {"S15": "docs/conversatie/examen_generalizare_mare.json",
           "S4": "docs/conversatie/examen_generalizare_401.json",
           "noaptea10": "date/conversatie/text/examen.json"}
CATEGORII = {"S15": {"b2", "e"}, "S4": {"a", "b", "d"}, "noaptea10": {None}}
LUCRU = RADACINA / "lucru" / "e3"
MAX_BUCATA = 700
SAMANTA = 1024
CATE_VALIDARE = 500
K = (1, 5, 20)
CONTEXT = 512
PREFIX_POTRIVIRE = 40

_CEDILE = str.maketrans({"ş": "ș", "ţ": "ț", "Ş": "Ș", "Ţ": "Ț"})
_PROPOZITII = re.compile(r"(?<=[.!?])\s+(?=[A-ZĂÂÎȘȚ„])")  # ca în unelte/conversatie_wikipedia.py
CUVINTE_DE_INTREBARE = frozenset(
    "cine ce când unde cum care cât câți câte câtă în a al ai ale la de din pe cu și s i este e sunt fost au lui lor "
    "o un una unei unui se mai despre pentru prin după spre sau ca că fi era avea are acest această".split())
VARIANTE = ("intreaga", "fara_cuvinte", "fara_cuvinte_prefix5", "fara_cuvinte_si", "fara_cuvinte_perechi")

# S25
VARIANTA_S24 = "fara_cuvinte_perechi"
VARIANTE_S25 = ("nume_repetate", "nume_obligatorii", "liste", "liste_randuri", "nume_repetate_liste",
                "nume_obligatorii_liste")
SAMANTA_NOUA = 2048
REPETARI_NUME = 2  # de câte ori în plus intră un nume propriu în interogare
CATE_PENTRU_LISTE = 100  # câte bucăți se aduc înainte de a coborî paginile-listă
UMPLUTURA = frozenset(
    "în din de la pe cu spre până peste sub circa aproximativ cca anul anii an anului locuitori locuitorii "
    "km kilometri m metri ha hectare kg grade".split())
_FRAZE_LISTA = re.compile(r"poate să însemne|se poate referi la|se mai poate referi|\(dezambiguizare\)|este o listă",
                          re.IGNORECASE)
RANDURI_MINIM, RANDURI_SCURTE, RAND_SCURT = 20, 0.9, 50
_NUMAR = re.compile(r"\d+(?:[.,  ]\d{3})*(?:,\d+)?")

# S26
SAMANTA_EXAMEN_NOU = 4096
CATE_EXAMEN_NOU = 100
K_S26 = (1, 3, 5, 20)


def _scrie_json(cale: Path, obiect: Any) -> None:
    cale.parent.mkdir(parents=True, exist_ok=True)
    cale.write_text(json.dumps(obiect, ensure_ascii=False, indent=1), encoding="utf-8")


def _relativ(cale: Path) -> str:
    try:
        return cale.relative_to(RADACINA).as_posix()
    except ValueError:
        return str(cale)


def _ram_maxim_mb() -> float | None:
    try:
        import psutil
        info = psutil.Process().memory_info()
        return round(getattr(info, "peak_wset", info.rss) / 2**20, 1)
    except Exception:  # noqa: BLE001 — doar o cifră în raport
        return None


def curata(text: str) -> str:
    """NFC și ş/ţ → ș/ț (în text și în întrebare)."""
    return unicodedata.normalize("NFC", text).translate(_CEDILE)


def taie(articol: str, maxim: int = MAX_BUCATA) -> list[str]:
    """Bucăți de cel mult `maxim` caractere, din propoziții întregi; o propoziție prea lungă se taie între cuvinte."""
    propozitii: list[str] = []
    for paragraf in curata(articol).split("\n"):
        paragraf = " ".join(paragraf.split())
        if paragraf:
            propozitii += _PROPOZITII.split(paragraf)
    bucati: list[str] = []
    curent = ""
    for p in propozitii:
        while len(p) > maxim:
            taietura = p.rfind(" ", 0, maxim + 1)
            taietura = taietura if taietura > 0 else maxim
            if curent:
                bucati.append(curent)
                curent = ""
            bucati.append(p[:taietura].strip())
            p = p[taietura:].strip()
        if not p:
            continue
        if curent and len(curent) + 1 + len(p) > maxim:
            bucati.append(curent)
            curent = p
        else:
            curent = f"{curent} {p}" if curent else p
    if curent:
        bucati.append(curent)
    return bucati


def articole(cale: Path) -> Iterable[str]:
    from unelte.conversatie_wikipedia import articole as _articole
    for a in _articole(cale):
        if a.strip():
            yield a


def deschide(cale: Path) -> sqlite3.Connection:
    return sqlite3.connect(cale)


def creeaza(cale: Path) -> sqlite3.Connection:
    cale.parent.mkdir(parents=True, exist_ok=True)
    if cale.exists():
        cale.unlink()
    con = deschide(cale)
    con.execute("PRAGMA journal_mode=OFF")
    con.execute("PRAGMA synchronous=OFF")
    con.execute("CREATE VIRTUAL TABLE bucati USING fts5(text, articol UNINDEXED, nr UNINDEXED, sursa UNINDEXED, "
                "tokenize='unicode61')")
    return con


def adauga_text(con: sqlite3.Connection, articol: str, text: str, sursa: str) -> int:
    randuri = [(b, articol, i, sursa) for i, b in enumerate(taie(text))]
    con.executemany("INSERT INTO bucati(text, articol, nr, sursa) VALUES (?, ?, ?, ?)", randuri)
    return len(randuri)


# ---------------------------------------------------------------- examenele (doar citite)

def texte_examen(examene: dict[str, str] = EXAMENE) -> list[dict[str, Any]]:
    """Textele distincte din cele trei examene, fiecare cu id-ul lui de document („examen_<n>”)."""
    vazute: dict[str, dict[str, Any]] = {}
    for nume, cale in examene.items():
        for p in json.loads((RADACINA / cale).read_text(encoding="utf-8"))["perechi"]:
            if p.get("text"):
                t = vazute.setdefault(p["text"], {"text": p["text"], "examene": []})
                if nume not in t["examene"]:
                    t["examene"].append(nume)
    return [{"id": f"examen_{i}", **t} for i, t in enumerate(vazute.values())]


def intrebari_examen(examene: dict[str, str] = EXAMENE) -> list[dict[str, Any]]:
    """Întrebările care au răspunsul în text: categoriile din S24, fără „Nu scrie în text.” și fără da/nu."""
    rez: list[dict[str, Any]] = []
    for nume, cale in examene.items():
        for i, p in enumerate(json.loads((RADACINA / cale).read_text(encoding="utf-8"))["perechi"]):
            if p.get("fel") != "text" or p.get("categorie") not in CATEGORII.get(nume, {p.get("categorie")}):
                continue
            if _fel_special(p["raspuns"]) is not None:
                continue
            rez.append({"examen": nume, "nr": i, "categorie": p.get("categorie"), "tip": p.get("tip"),
                        "text": p["text"], "intrebare": p["intrebare"], "raspuns": p["raspuns"]})
    return rez


def candidate_validare(cale: Path) -> list[dict]:
    """Din text_v3: „text”, fără da/nu / „Nu scrie”, cu răspunsul găsit în text (regula S16)."""
    bune = []
    for r in cale.read_text(encoding="utf-8").splitlines():
        if not r.strip():
            continue
        p = json.loads(r)
        if p.get("fel") == "text" and _fel_special(p["raspuns"]) is None and verifica(p["raspuns"], p["text"])["corect"]:
            bune.append({"intrebare": p["intrebare"], "raspuns": p["raspuns"], "text": p["text"], "tip": p.get("tip"),
                         "grup": p.get("grup")})
    return bune


def intrebari_validare(cale: Path, cate: int = CATE_VALIDARE, samanta: int = SAMANTA) -> tuple[list[dict], int]:
    """`cate` întrebări la întâmplare din text_v3 (eșantionul S24)."""
    bune = candidate_validare(cale)
    return random.Random(samanta).sample(bune, min(cate, len(bune))), len(bune)


def intrebari_validare_s25(cale: Path, cate: int = CATE_VALIDARE) -> tuple[list[dict], list[dict], int]:
    """Eșantionul S24 (sămânța 1024) și unul nou (sămânța 2048), fără nicio întrebare din primul."""
    bune = candidate_validare(cale)
    vechi = random.Random(SAMANTA).sample(bune, min(cate, len(bune)))
    luate = {(q["intrebare"], q["text"]) for q in vechi}  # nici dublurile aceleiași perechi
    rest = [q for q in bune if (q["intrebare"], q["text"]) not in luate]
    return vechi, random.Random(SAMANTA_NOUA).sample(rest, min(cate, len(rest))), len(bune)


# ---------------------------------------------------------------- căutarea

def _ghilimele(cuv: str) -> str:
    return '"' + cuv.replace('"', '""') + '"'


def nume_proprii(intrebare: str) -> tuple[list[str], list[str]]:
    """(b) Cuvintele cu majusculă care nu sunt primul cuvânt al întrebării (normalizate) și perechile lor alăturate."""
    nume: list[str] = []
    perechi: list[str] = []
    anterior: list[str] = []
    for i, bucata in enumerate(curata(intrebare).split()):
        litere = [x for x in bucata if x.isalpha()]
        parti = [c for c in cuvinte(bucata) if c not in CUVINTE_DE_INTREBARE and any(x.isalnum() for x in c)]
        if i == 0 or not litere or not litere[0].isupper() or not parti:
            anterior = []
            continue
        if anterior:
            perechi.append(f"{anterior[-1]} {parti[0]}")
        perechi += [f"{a} {b}" for a, b in zip(parti, parti[1:])]
        nume += [p for p in parti if p not in nume]
        anterior = parti
    return nume, list(dict.fromkeys(perechi))


def _parti(varianta: str) -> tuple[str, str]:
    """Varianta S25 → (partea b: „”, „nume_repetate”, „nume_obligatorii”; partea c: „”, „liste”, „liste_randuri”)."""
    if varianta in VARIANTE:
        return "", ""
    for b in ("nume_repetate", "nume_obligatorii"):
        if varianta.startswith(b):
            rest = varianta[len(b):].lstrip("_")
            break
    else:
        b, rest = "", varianta
    if rest not in ("", "liste", "liste_randuri"):
        raise ValueError(f"varianta necunoscută: {varianta}")
    return b, rest


def interogare(intrebare: str, varianta: str) -> str:
    """Interogarea FTS5 pentru o variantă (cuvintele normalizate ca la verificator, fiecare între ghilimele)."""
    if varianta not in VARIANTE:
        b, _ = _parti(varianta)
        baza = interogare(intrebare, VARIANTA_S24)
        nume, perechi = nume_proprii(intrebare)
        if not nume or not b:
            return baza
        if b == "nume_repetate":
            return " OR ".join([baza] + [_ghilimele(c) for c in nume + perechi] * REPETARI_NUME)
        return " AND ".join(_ghilimele(c) for c in nume) + f" AND ({baza})"
    toate = [c for c in cuvinte(curata(intrebare)) if any(x.isalnum() for x in c)]
    fara = [c for c in toate if c not in CUVINTE_DE_INTREBARE] or toate
    if varianta == "intreaga":
        return " OR ".join(_ghilimele(c) for c in toate)
    if varianta == "fara_cuvinte":
        return " OR ".join(_ghilimele(c) for c in fara)
    if varianta == "fara_cuvinte_prefix5":
        return " OR ".join(_ghilimele(c[:5]) + "*" if len(c) > 5 else _ghilimele(c) for c in fara)
    if varianta == "fara_cuvinte_si":
        return " AND ".join(_ghilimele(c) for c in fara)
    if varianta == "fara_cuvinte_perechi":
        perechi = [_ghilimele(f"{a} {b}") for a, b in zip(fara, fara[1:])]
        return " OR ".join([_ghilimele(c) for c in fara] + perechi)
    raise ValueError(f"varianta necunoscută: {varianta}")


def cauta(con: sqlite3.Connection, intrebare: str, varianta: str, k: int = max(K),
          liste: dict[str, set[str]] | None = None) -> list[dict[str, Any]]:
    """Primele k bucăți după BM25. La „fara_cuvinte_si” și „nume_obligatorii”, dacă AND aduce prea puțin, se completează
    cu OR (varianta de bază). Cu partea (c), se aduc `CATE_PENTRU_LISTE` și paginile-listă trec după celelalte."""
    b, c = ("", "") if varianta in VARIANTE else _parti(varianta)
    cate = max(k, CATE_PENTRU_LISTE) if c else k
    sql = "SELECT rowid, text, articol, sursa FROM bucati WHERE bucati MATCH ? ORDER BY rank LIMIT ?"
    gasite = con.execute(sql, (interogare(intrebare, varianta), cate)).fetchall()
    completare = {"fara_cuvinte_si": "fara_cuvinte", "nume_obligatorii": VARIANTA_S24}.get(varianta if not b else b)
    if completare and len(gasite) < cate:
        vazute = {g[0] for g in gasite}
        gasite += [g for g in con.execute(sql, (interogare(intrebare, completare), cate)).fetchall()
                   if g[0] not in vazute][: cate - len(gasite)]
    if c:
        if liste is None:
            raise ValueError("varianta cu liste cere liste_s25.json (comanda `liste`)")
        coborate = liste["fraze_lista"] | (liste["randuri_scurte"] if c == "liste_randuri" else set())
        gasite = sorted(gasite, key=lambda g: g[2] in coborate)[:k]  # sortare stabilă: ordinea BM25 rămâne
    return [{"rowid": g[0], "text": g[1], "articol": g[2], "sursa": g[3]} for g in gasite]


def numar_gol(raspuns: str) -> str | None:
    """(a) Numărul din referință, dacă după ce scoți cuvintele de umplutură rămâne doar el („În 1966.” → „1966”)."""
    text = curata(raspuns)
    numere = _NUMAR.findall(text)
    if len(numere) != 1 or [c for c in cuvinte(_NUMAR.sub(" ", text)) if c not in UMPLUTURA]:
        return None
    return numere[0]


def contine_numar(numar: str, text: str) -> bool:
    """Numărul ca număr întreg (nu bucată din alt număr); separatorul de mii poate fi punct, virgulă sau spațiu."""
    grupe = re.split(r"[.,  ]", numar)
    tipar = r"(?<!\d)(?<!\d[.,])" + r"[.,  ]".join(grupe) + r"(?!\d)(?![.,]\d)"
    return re.search(tipar, curata(text)) is not None


def bun(raspuns: str, text: str, potrivire: str = "s16") -> bool:
    """Bucata conține răspunsul: „s16” = regula principală a verificatorului S16; „numar” = S16 sau numărul gol (a)."""
    if verifica(raspuns, text)["corect"]:
        return True
    if potrivire == "numar":
        numar = numar_gol(raspuns)
        return numar is not None and contine_numar(numar, text)
    return False


def primul_bun(gasite: list[dict[str, Any]], raspuns: str, potrivire: str = "s16") -> int | None:
    """Locul (de la 1) primei bucăți care conține răspunsul (implicit: regula principală a verificatorului S16)."""
    for i, g in enumerate(gasite, 1):
        if bun(raspuns, g["text"], potrivire):
            return i
    return None


def procente(locuri: list[int | None], k: Iterable[int] | None = None) -> dict[str, Any]:
    k = K if k is None else k
    n = len(locuri)
    return {f"k{x}": {"bune": sum(1 for l in locuri if l is not None and l <= x),
                      "procent": round(100 * sum(1 for l in locuri if l is not None and l <= x) / n, 1) if n else 0.0}
            for x in k}


def masoara_intrebari(con: sqlite3.Connection, intrebari: list[dict[str, Any]], varianta: str,
                      liste: dict[str, set[str]] | None = None) -> list[dict[str, Any]]:
    """Pentru fiecare întrebare: `loc` (potrivirea S16), `loc_numar` (S16 sau numărul gol), timpul căutării."""
    rez = []
    for q in intrebari:
        t = time.perf_counter()
        gasite = cauta(con, q["intrebare"], varianta, liste=liste)
        secunde = time.perf_counter() - t
        rez.append({**q, "loc": primul_bun(gasite, q["raspuns"]), "loc_numar": primul_bun(gasite, q["raspuns"], "numar"),
                    "secunde": secunde, "gasite": gasite})
    return rez


# ---------------------------------------------------------------- comenzile

def cmd_index(wikipedia: Path, lucru: Path, examene: dict[str, str] = EXAMENE) -> dict[str, Any]:
    start = time.time()
    con = creeaza(lucru / "index.sqlite")
    texte = texte_examen(examene)
    norm_ex = [normalizeaza(t["text"]) for t in texte]
    prefixe: dict[str, list[int]] = {}
    for i, t in enumerate(texte):
        prefixe.setdefault(" ".join(curata(t["text"]).split())[:PREFIX_POTRIVIRE], []).append(i)
    exact: dict[int, str] = {}
    probabil: dict[int, list[str]] = {}
    n_art = n_buc = 0
    for n, a in enumerate(articole(wikipedia)):
        aid = f"w{n}"
        n_buc += adauga_text(con, aid, a, "wikipedia")
        n_art += 1
        cap = " ".join(curata(a[:3000]).split())
        for prefix, idx in prefixe.items():
            if prefix in cap:
                na = normalizeaza(a)
                for i in idx:
                    probabil.setdefault(i, []).append(aid)
                    if norm_ex[i] in na and i not in exact:
                        exact[i] = aid
        if n_art % 50_000 == 0:
            con.commit()
            print(f"{datetime.now():%H:%M:%S} {n_art} articole, {n_buc} bucăți", flush=True)
    con.commit()
    con.execute("INSERT INTO bucati(bucati) VALUES ('optimize')")
    con.commit()
    con.close()
    for i, t in enumerate(texte):
        t["in_wikipedia"] = exact.get(i)
        t["articole_probabile"] = probabil.get(i, [])
    _scrie_json(lucru / "texte_examen.json", texte)
    info = {"articole": n_art, "bucati": n_buc, "marime_mb": round((lucru / "index.sqlite").stat().st_size / 2**20, 1),
            "ram_maxim_mb": _ram_maxim_mb(), "secunde": round(time.time() - start, 1), "max_bucata": MAX_BUCATA,
            "texte_examen": len(texte), "texte_examen_deja_in_wikipedia": len(exact),
            "texte_examen_cu_articol_probabil": len(probabil), "scris": datetime.now().isoformat(timespec="seconds")}
    _scrie_json(lucru / "index.json", info)
    return info


def cmd_adauga(lucru: Path) -> dict[str, Any]:
    texte = json.loads((lucru / "texte_examen.json").read_text(encoding="utf-8"))
    con = deschide(lucru / "index.sqlite")
    if con.execute("SELECT count(*) FROM bucati WHERE sursa = 'examen'").fetchone()[0]:
        raise SystemExit("textele de examen sunt deja adăugate în index")
    timpi: list[float] = []
    bucati = 0
    for t in texte:
        if t["in_wikipedia"]:
            continue
        s = time.perf_counter()
        bucati += adauga_text(con, t["id"], t["text"], "examen")
        con.commit()
        timpi.append(time.perf_counter() - s)
    con.close()
    info = {"texte_examen": len(texte), "deja_in_wikipedia": sum(1 for t in texte if t["in_wikipedia"]),
            "adaugate": len(timpi), "bucati_adaugate": bucati,
            "ms_pe_text_median": round(1000 * statistics.median(timpi), 2) if timpi else None,
            "ms_pe_text_maxim": round(1000 * max(timpi), 2) if timpi else None,
            "scris": datetime.now().isoformat(timespec="seconds")}
    _scrie_json(lucru / "adauga.json", info)
    return info


def _fara_gasite(r: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in r.items() if k not in ("gasite", "text")}


def _timpi(rez: list[dict[str, Any]]) -> dict[str, float]:
    s = [r["secunde"] for r in rez]
    return {"ms_median": round(1000 * statistics.median(s), 1), "ms_maxim": round(1000 * max(s), 1)} if s else {}


def cmd_validare(lucru: Path, text_v3: Path, variante: Iterable[str] = VARIANTE) -> dict[str, Any]:
    variante = list(variante)
    if len(variante) > 6:
        raise SystemExit("cel mult 6 variante pe validare")
    intrebari, candidate = intrebari_validare(text_v3)
    con = deschide(lucru / "index.sqlite")
    pe_variante = {}
    for v in variante:
        rez = masoara_intrebari(con, intrebari, v)
        pe_variante[v] = {**procente([r["loc"] for r in rez]), **_timpi(rez)}
        print(v, pe_variante[v], flush=True)
    con.close()
    aleasa = max(variante, key=lambda v: (pe_variante[v]["k5"]["bune"], pe_variante[v]["k1"]["bune"]))
    info = {"intrebari": len(intrebari), "candidate_in_text_v3": candidate, "samanta": SAMANTA,
            "variante": pe_variante, "aleasa": aleasa, "criteriu": "cele mai multe bune la k = 5 (la egalitate, k = 1)",
            "scris": datetime.now().isoformat(timespec="seconds")}
    _scrie_json(lucru / "validare.json", info)
    return info


def _marcheaza_articol(rez: list[dict[str, Any]], lucru: Path) -> None:
    """(ii) articolul corect în primele 5 și dacă verificatorul găsește răspunsul măcar în textul examenului."""
    texte = {t["text"]: t for t in json.loads((lucru / "texte_examen.json").read_text(encoding="utf-8"))}
    for r in rez:
        t = texte[r["text"]]
        corecte = set(t["articole_probabile"]) | ({t["in_wikipedia"]} if t["in_wikipedia"] else set()) | {t["id"]}
        r["articol_gasit_la_5"] = any(g["articol"] in corecte for g in r["gasite"][:5])
        r["raspuns_in_textul_examenului"] = verifica(r["raspuns"], r["text"])["corect"]


def _rezumat(parte: list[dict[str, Any]], loc: str = "loc", k: Iterable[int] | None = None) -> dict[str, Any]:
    return {"intrebari": len(parte), "i_cautare": procente([r[loc] for r in parte], k),
            "ii_articol_la_5": {"bune": sum(r["articol_gasit_la_5"] for r in parte),
                                "procent": round(100 * sum(r["articol_gasit_la_5"] for r in parte) / len(parte), 1)
                                if parte else 0.0}}


def _pe_examen(rez: list[dict[str, Any]], examene: dict[str, str], loc: str = "loc") -> dict[str, Any]:
    pe_examen = {f"{n}_{c}": _rezumat([r for r in rez if r["examen"] == n and (r["categorie"] or "text") == c], loc)
                 for n, c in sorted({(r["examen"], r["categorie"] or "text") for r in rez}, key=str)}
    for n in examene:
        pe_examen[n] = _rezumat([r for r in rez if r["examen"] == n], loc)
    return pe_examen


def cmd_examene(lucru: Path, examene: dict[str, str] = EXAMENE) -> dict[str, Any]:
    if (lucru / "examene.json").exists():
        raise SystemExit("examenele s-au măsurat deja (o singură rulare, regula S24)")
    varianta = json.loads((lucru / "validare.json").read_text(encoding="utf-8"))["aleasa"]
    intrebari = intrebari_examen(examene)
    con = deschide(lucru / "index.sqlite")
    rez = masoara_intrebari(con, intrebari, varianta)
    con.close()
    _marcheaza_articol(rez, lucru)
    rezumat = _rezumat
    pe_examen = _pe_examen(rez, examene)
    gresite = [r for r in rez if r["loc"] is None or r["loc"] > 5]
    alese = random.Random(SAMANTA).sample(gresite, min(20, len(gresite)))
    info = {"varianta": varianta, "intrebari": len(rez),
            "raspuns_in_textul_examenului": sum(r["raspuns_in_textul_examenului"] for r in rez),
            "total": rezumat(rez), "total_raspuns_in_text": rezumat([r for r in rez if r["raspuns_in_textul_examenului"]]),
            "pe_examen": pe_examen, **_timpi(rez),
            "greseli_la_5": len(gresite),
            "greseli_alese": [{"examen": r["examen"], "intrebare": r["intrebare"], "raspuns": r["raspuns"],
                               "loc": r["loc"], "primele_3": [g["text"][:200] for g in r["gasite"][:3]]} for r in alese],
            "toate": [_fara_gasite(r) for r in rez], "scris": datetime.now().isoformat(timespec="seconds")}
    _scrie_json(lucru / "examene.json", info)
    return info


# ---------------------------------------------------------------- S25

def fel_lista(articol: str) -> tuple[bool, bool]:
    """(c) (pagină-listă / de dezambiguizare după fraze sau titlu, pagină cu aproape numai rânduri scurte)."""
    s = curata(articol).strip()
    fraze = bool(_FRAZE_LISTA.search(s[:300])) or s.startswith(("Listă ", "Lista "))
    randuri = [r.strip() for r in s.split("\n") if r.strip()]
    scurte = len(randuri) >= RANDURI_MINIM and sum(len(r) < RAND_SCURT for r in randuri) / len(randuri) >= RANDURI_SCURTE
    return fraze, scurte


def cmd_liste(wikipedia: Path, lucru: Path) -> dict[str, Any]:
    """Paginile-listă din Wikipedia, cu aceleași id-uri ca în index („w<n>”, în ordinea din `cmd_index`)."""
    start = time.time()
    fraze: list[str] = []
    scurte: list[str] = []
    n = 0
    for n, a in enumerate(articole(wikipedia), 1):
        f, s = fel_lista(a)
        if f:
            fraze.append(f"w{n - 1}")
        if s:
            scurte.append(f"w{n - 1}")
    info = {"articole": n, "fraze_lista_cate": len(fraze), "randuri_scurte_cate": len(scurte),
            "oricare_cate": len(set(fraze) | set(scurte)),
            "reguli": {"fraze_in_primele_300": _FRAZE_LISTA.pattern, "incepe_cu": ["Listă ", "Lista "],
                       "randuri_scurte": f">= {RANDURI_MINIM} rânduri, >= {RANDURI_SCURTE:.0%} sub {RAND_SCURT} caractere"},
            "secunde": round(time.time() - start, 1), "scris": datetime.now().isoformat(timespec="seconds"),
            "fraze_lista": fraze, "randuri_scurte": scurte}
    _scrie_json(lucru / "liste_s25.json", info)
    return info


def incarca_liste(lucru: Path) -> dict[str, set[str]]:
    info = json.loads((lucru / "liste_s25.json").read_text(encoding="utf-8"))
    return {"fraze_lista": set(info["fraze_lista"]), "randuri_scurte": set(info["randuri_scurte"])}


def _bune(procent: dict[str, Any], k: int) -> int:
    return procent[f"k{k}"]["bune"]


def cmd_validare_s25(lucru: Path, text_v3: Path, variante: Iterable[str] = VARIANTE_S25) -> dict[str, Any]:
    """Varianta S24 și cel mult 6 variante noi, pe eșantionul S24 (1024) și pe unul nou (2048); alege după k = 5 pe
    ambele luate împreună (la egalitate k = 1), cu potrivirea S16."""
    variante = list(variante)
    if len(variante) > 6:
        raise SystemExit("cel mult 6 variante noi pe validare")
    vechi, noi, candidate = intrebari_validare_s25(text_v3)
    liste = incarca_liste(lucru)
    con = deschide(lucru / "index.sqlite")
    pe_variante: dict[str, Any] = {}
    for v in [VARIANTA_S24] + variante:
        pe_variante[v] = {}
        for nume, intrebari in (("s1024", vechi), ("s2048", noi), ("impreuna", vechi + noi)):
            if nume == "impreuna":
                rez = pe_variante[v].pop("_rez1024") + pe_variante[v].pop("_rez2048")
            else:
                rez = masoara_intrebari(con, intrebari, v, liste)
                pe_variante[v][f"_rez{nume[1:]}"] = rez
            pe_variante[v][nume] = {"s16": procente([r["loc"] for r in rez]),
                                    "numar": procente([r["loc_numar"] for r in rez]), **_timpi(rez)}
        print(v, {n: pe_variante[v][n]["s16"]["k5"] for n in ("s1024", "s2048")}, flush=True)
    con.close()
    aleasa = max(variante, key=lambda v: (_bune(pe_variante[v]["impreuna"]["s16"], 5),
                                          _bune(pe_variante[v]["impreuna"]["s16"], 1)))
    nou = lambda v: pe_variante[v]["s2048"]["s16"]["k5"]["procent"]  # noqa: E731
    s24 = json.loads((lucru / "validare.json").read_text(encoding="utf-8"))["variante"].get(VARIANTA_S24, {})
    reprodus = all(_bune(pe_variante[VARIANTA_S24]["s1024"]["s16"], k) == s24.get(f"k{k}", {}).get("bune") for k in K)
    info = {"intrebari": {"s1024": len(vechi), "s2048": len(noi)}, "candidate_in_text_v3": candidate,
            "comune_intre_esantioane": len({(q["intrebare"], q["text"]) for q in vechi}
                                           & {(q["intrebare"], q["text"]) for q in noi}),
            "varianta_s24_reprodusa_pe_1024": reprodus, "variante": pe_variante, "aleasa": aleasa,
            "criteriu": "cele mai multe bune la k = 5 pe ambele eșantioane împreună, potrivirea S16 (la egalitate k = 1)",
            "castig_k5_pe_2048_puncte": round(nou(aleasa) - nou(VARIANTA_S24), 1),
            "castig_real": nou(aleasa) - nou(VARIANTA_S24) >= 3,
            "prag_supraveghetor": "câștig real = aleasa urcă (i) k = 5 cu ≥ 3 puncte pe sămânța 2048 față de S24, potrivirea S16",
            "scris": datetime.now().isoformat(timespec="seconds")}
    _scrie_json(lucru / "validare_s25.json", info)
    return info


def cmd_examene_s25(lucru: Path, examene: dict[str, str] = EXAMENE) -> dict[str, Any]:
    """O SINGURĂ rulare: varianta S24 (din nou, ca reper în ambele potriviri) și varianta aleasă la validarea S25."""
    if (lucru / "examene_s25.json").exists():
        raise SystemExit("examenele S25 s-au măsurat deja (o singură rulare)")
    aleasa = json.loads((lucru / "validare_s25.json").read_text(encoding="utf-8"))["aleasa"]
    intrebari = intrebari_examen(examene)
    liste = incarca_liste(lucru)
    con = deschide(lucru / "index.sqlite")
    rulari = {"s24": masoara_intrebari(con, intrebari, VARIANTA_S24, liste),
              "aleasa": masoara_intrebari(con, intrebari, aleasa, liste)}
    con.close()
    for rez in rulari.values():
        _marcheaza_articol(rez, lucru)
    vechi = {(r["examen"], r["nr"]): r["loc"]
             for r in json.loads((lucru / "examene.json").read_text(encoding="utf-8"))["toate"]}
    la5 = lambda loc: loc is not None and loc <= 5  # noqa: E731
    nou = rulari["aleasa"]
    pe_rulari = {}
    for nume, rez in rulari.items():
        pe_rulari[nume] = {pot: {"total": _rezumat(rez, loc),
                                 "total_raspuns_in_text": _rezumat([r for r in rez if r["raspuns_in_textul_examenului"]],
                                                                   loc),
                                 "pe_examen": _pe_examen(rez, examene, loc)}
                           for pot, loc in (("s16", "loc"), ("numar", "loc_numar"))}
        pe_rulari[nume].update(_timpi(rez))
    schimbari = {}
    for pot, loc in (("s16", "loc"), ("numar", "loc_numar")):
        reparate = [r for r in nou if not la5(vechi[(r["examen"], r["nr"])]) and la5(r[loc])]
        stricate = [r for r in nou if la5(vechi[(r["examen"], r["nr"])]) and not la5(r[loc])]
        schimbari[pot] = {"greseli_s24_la_5": sum(1 for v in vechi.values() if not la5(v)),
                          "reparate": len(reparate), "stricate": len(stricate),
                          "lista_reparate": [{"examen": r["examen"], "intrebare": r["intrebare"], "raspuns": r["raspuns"],
                                              "loc_vechi": vechi[(r["examen"], r["nr"])], "loc_nou": r[loc]}
                                             for r in reparate],
                          "lista_stricate": [{"examen": r["examen"], "intrebare": r["intrebare"], "raspuns": r["raspuns"],
                                              "loc_vechi": vechi[(r["examen"], r["nr"])], "loc_nou": r[loc]}
                                             for r in stricate]}
    nepotrivite = sum(1 for r in rulari["s24"] if r["loc"] != vechi[(r["examen"], r["nr"])])
    info = {"aleasa": aleasa, "intrebari": len(nou), "varianta_s24_reprodusa": nepotrivite == 0,
            "varianta_s24_locuri_diferite": nepotrivite, "rulari": pe_rulari,
            "schimbari_fata_de_s24": schimbari,
            "toate": {n: [_fara_gasite(r) for r in rez] for n, rez in rulari.items()},
            "primele_3_aleasa": [{"examen": r["examen"], "nr": r["nr"], "primele_3": [g["text"][:200] for g in r["gasite"][:3]]}
                                 for r in nou if not la5(r["loc"])],
            "scris": datetime.now().isoformat(timespec="seconds")}
    _scrie_json(lucru / "examene_s25.json", info)
    return info


# ---------------------------------------------------------------- S26

def articole_text(con: sqlite3.Connection, text: str) -> list[str]:
    """Articolele din index cu o bucată care conține începutul textului (primele 40 de caractere, ca la
    „articole_probabile” din S24); căutate cu fraza exactă a cuvintelor întregi din acest început."""
    tot = " ".join(curata(text).split())
    prefix = tot[:PREFIX_POTRIVIRE]
    cuv = cuvinte(prefix)
    if len(tot) > PREFIX_POTRIVIRE:
        cuv = cuv[:-1]  # ultimul cuvânt poate fi tăiat
    if not cuv:
        return []
    randuri = con.execute("SELECT text, articol FROM bucati WHERE bucati MATCH ? LIMIT 500",
                          (_ghilimele(" ".join(cuv)),)).fetchall()
    return sorted({a for t, a in randuri if prefix in t})


def _articole_examen(lucru: Path) -> set[str]:
    rez: set[str] = set()
    for t in json.loads((lucru / "texte_examen.json").read_text(encoding="utf-8")):
        rez |= {t["id"], *t["articole_probabile"], *([t["in_wikipedia"]] if t["in_wikipedia"] else [])}
    return rez


def cmd_examen_nou(lucru: Path, text_v3: Path, examene: dict[str, str] = EXAMENE,
                   cate: int = CATE_EXAMEN_NOU) -> dict[str, Any]:
    """Pasul 1 din S26: `cate` întrebări din text_v3 (sămânța 4096, filtrele validării), fără nicio întrebare, niciun
    text, niciun grup și niciun articol comun cu eșantioanele 1024 și 2048 și cu examenele. Listă fixă; nu măsoară nimic."""
    cale = lucru / "examen_nou_4096.json"
    if cale.exists():
        raise SystemExit("examenul nou e deja ales (listă fixă, nu se mai alege)")
    bune = candidate_validare(text_v3)
    vechi, noi, _ = intrebari_validare_s25(text_v3)
    folosite = vechi + noi + intrebari_examen(examene)
    intrebari_luate = {normalizeaza(q["intrebare"]) for q in folosite}
    texte_luate = {normalizeaza(q["text"]) for q in folosite}
    grupuri_luate = {q["grup"] for q in vechi + noi if q.get("grup")}
    con = deschide(lucru / "index.sqlite")
    articole_luate = _articole_examen(lucru)
    for q in vechi + noi:
        articole_luate |= set(articole_text(con, q["text"]))
    rest = [q for q in bune if normalizeaza(q["intrebare"]) not in intrebari_luate
            and normalizeaza(q["text"]) not in texte_luate and q.get("grup") not in grupuri_luate]
    alese: list[dict[str, Any]] = []
    vazute: set[str] = set()
    respinse_articol = 0
    for q in random.Random(SAMANTA_EXAMEN_NOU).sample(rest, len(rest)):
        if len(alese) >= cate:
            break
        if normalizeaza(q["intrebare"]) in vazute:
            continue
        art = articole_text(con, q["text"])
        if set(art) & articole_luate:
            respinse_articol += 1
            continue
        vazute.add(normalizeaza(q["intrebare"]))
        alese.append({**q, "articole_corecte": art})
    con.close()
    _scrie_json(cale, alese)
    info = {"intrebari": len(alese), "samanta": SAMANTA_EXAMEN_NOU, "candidate_in_text_v3": len(bune),
            "candidate_dupa_excluderi": len(rest), "respinse_pentru_articol_comun": respinse_articol,
            "grupuri_distincte": len({q["grup"] for q in alese}),
            "texte_distincte": len({normalizeaza(q["text"]) for q in alese}),
            "articole_wikipedia_distincte": len({a for q in alese for a in q["articole_corecte"]}),
            "fara_articol_gasit": sum(1 for q in alese if not q["articole_corecte"]),
            "tipuri": dict(Counter(q["tip"] for q in alese).most_common()),
            "articole_excluse": len(articole_luate), "fisier": _relativ(cale),
            "sha256": hashlib.sha256(cale.read_bytes()).hexdigest(),
            "regula": "nu se folosesc la nicio ajustare și nicio antrenare (S27 le scoate, cu tot cu articolele lor)",
            "scris": datetime.now().isoformat(timespec="seconds")}
    _scrie_json(lucru / "examen_nou_4096_info.json", info)
    return info


def _pe_tip(rez: list[dict[str, Any]], loc: str) -> dict[str, Any]:
    return {t: procente([r[loc] for r in rez if r["tip"] == t], K_S26)
            for t, _ in Counter(r["tip"] for r in rez).most_common()}


def cmd_examen_nou_masoara(lucru: Path, text_v3: Path) -> dict[str, Any]:
    """Pasul 4 din S26, O SINGURĂ rulare: varianta S24 și aleasa S25 pe cele 100 noi (k = 1/3/5/20, ambele potriviri,
    (ii) articolul la 5); plus k = 3 pentru aleasă pe cele 160 de examene (din examene_s25.json, doar numărare) și pe
    validarea 2048 (aleasa rulată din nou, cu verificarea că k = 1/5/20 ies la fel ca în S25)."""
    iesire = lucru / "examen_nou_s26.json"
    if iesire.exists():
        raise SystemExit("examenul nou s-a măsurat deja (o singură rulare)")
    cale = lucru / "examen_nou_4096.json"
    sha = hashlib.sha256(cale.read_bytes()).hexdigest()
    if sha != json.loads((lucru / "examen_nou_4096_info.json").read_text(encoding="utf-8"))["sha256"]:
        raise SystemExit("lista examenului nou nu mai are amprenta de la alegere")
    intrebari = json.loads(cale.read_text(encoding="utf-8"))
    val25 = json.loads((lucru / "validare_s25.json").read_text(encoding="utf-8"))
    aleasa = val25["aleasa"]
    liste = incarca_liste(lucru)
    potriviri = (("s16", "loc"), ("numar", "loc_numar"))
    con = deschide(lucru / "index.sqlite")
    rulari = {"s24": masoara_intrebari(con, intrebari, VARIANTA_S24, liste),
              "aleasa": masoara_intrebari(con, intrebari, aleasa, liste)}
    _, noi, _ = intrebari_validare_s25(text_v3)
    rez2048 = masoara_intrebari(con, noi, aleasa, liste)
    con.close()
    for rez in rulari.values():
        for r in rez:
            r["articol_gasit_la_5"] = any(g["articol"] in set(r["articole_corecte"]) for g in r["gasite"][:5])
            r["raspuns_in_textul_examenului"] = verifica(r["raspuns"], r["text"])["corect"]
    pe_rulari = {}
    for nume, rez in rulari.items():
        cu_articol = [r for r in rez if r["articole_corecte"]]
        pe_rulari[nume] = {pot: {"total": _rezumat(rez, loc, K_S26),
                                 "cu_articol_gasit": _rezumat(cu_articol, loc, K_S26),
                                 "pe_tip": _pe_tip(rez, loc)} for pot, loc in potriviri}
        pe_rulari[nume].update(_timpi(rez))
    ex25 = json.loads((lucru / "examene_s25.json").read_text(encoding="utf-8"))["toate"]["aleasa"]
    vechi160 = {pot: procente([r[loc] for r in ex25], K_S26) for pot, loc in potriviri}
    v2048 = {pot: procente([r[loc] for r in rez2048], K_S26) for pot, loc in potriviri}
    s25_2048 = val25["variante"][aleasa]["s2048"]
    reprodus = all(_bune(v2048[pot], k) == _bune(s25_2048[pot], k) for pot, _ in potriviri for k in K)
    oficial = pe_rulari["aleasa"]["s16"]["total"]
    diferenta = round(vechi160["s16"]["k5"]["procent"] - oficial["i_cautare"]["k5"]["procent"], 1)
    info = {"aleasa": aleasa, "intrebari": len(intrebari), "sha256": sha,
            "raspuns_in_textul_examenului": sum(r["raspuns_in_textul_examenului"] for r in rulari["aleasa"]),
            "rulari": pe_rulari, "k3_examene_160_aleasa": vechi160, "k3_validare_2048_aleasa": v2048,
            "validare_2048_reprodusa_k1_5_20": reprodus,
            "cifra_oficiala": {"i_k5": oficial["i_cautare"]["k5"], "ii_articol_la_5": oficial["ii_articol_la_5"]},
            "plafon_e3_k3": oficial["i_cautare"]["k3"],
            "puncte_sub_cele_160_la_k5": diferenta, "cele_160_umflate": diferenta >= 5,
            "toate": {n: [_fara_gasite(r) for r in rez] for n, rez in rulari.items()},
            "primele_3_aleasa": [{"intrebare": r["intrebare"], "raspuns": r["raspuns"], "loc": r["loc"],
                                  "primele_3": [g["text"][:200] for g in r["gasite"][:3]]} for r in rulari["aleasa"]],
            "scris": datetime.now().isoformat(timespec="seconds")}
    _scrie_json(iesire, info)
    return info


def cmd_lungimi(wikipedia: Path, lucru: Path, tokenizer: Path, examene: dict[str, str] = EXAMENE) -> dict[str, Any]:
    from module.tokenizer_bpe import TokenizerBPE
    tok = TokenizerBPE.incarca(tokenizer)
    pe_text = [len(tok.codifica(t["text"])) / CONTEXT for t in texte_examen(examene)]
    praguri = (1, 2, 5, 10)
    peste: Counter[int] = Counter()
    n = 0
    start = time.time()
    for a in articole(wikipedia):
        n += 1
        if len(a.encode("utf-8")) <= CONTEXT:  # un simbol are cel puțin un octet
            continue
        simb = len(tok.codifica(a))
        for p in praguri:
            if simb > p * CONTEXT:
                peste[p] += 1
    info = {"context": CONTEXT, "tokenizer": _relativ(tokenizer),
            "texte_examen": {"cate": len(pe_text), "ori_contextul_min": round(min(pe_text), 3),
                             "ori_contextul_median": round(statistics.median(pe_text), 3),
                             "ori_contextul_max": round(max(pe_text), 3),
                             "peste_context": sum(1 for x in pe_text if x > 1)},
            "articole_wikipedia": n, "articole_peste": {f"{p}x{CONTEXT}": peste[p] for p in praguri},
            "secunde": round(time.time() - start, 1), "scris": datetime.now().isoformat(timespec="seconds")}
    _scrie_json(lucru / "lungimi.json", info)
    return info


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="E3: indexul de memorie peste Wikipedia (S24).")
    parser.add_argument("--lucru", default=_relativ(LUCRU))
    parser.add_argument("--wikipedia", default=WIKIPEDIA)
    sub = parser.add_subparsers(dest="pas", required=True)
    sub.add_parser("index")
    sub.add_parser("adauga")
    m = sub.add_parser("masoara")
    m.add_argument("--set", choices=("validare", "examene", "examen_nou"), required=True)
    m.add_argument("--runda", choices=("s24", "s25"), default="s24")
    sub.add_parser("lungimi")
    sub.add_parser("liste")
    sub.add_parser("examen-nou")
    args = parser.parse_args(argv)
    lucru, wikipedia = RADACINA / args.lucru, RADACINA / args.wikipedia
    if args.pas == "index":
        info = cmd_index(wikipedia, lucru)
    elif args.pas == "adauga":
        info = cmd_adauga(lucru)
    elif args.pas == "lungimi":
        info = cmd_lungimi(wikipedia, lucru, RADACINA / TOKENIZER)
    elif args.pas == "liste":
        info = {k: v for k, v in cmd_liste(wikipedia, lucru).items() if k not in ("fraze_lista", "randuri_scurte")}
    elif args.pas == "examen-nou":
        info = cmd_examen_nou(lucru, RADACINA / TEXT_V3)
    elif args.set == "examen_nou":
        info = cmd_examen_nou_masoara(lucru, RADACINA / TEXT_V3)
        info = {k: v for k, v in info.items() if k not in ("toate", "primele_3_aleasa")}
    elif args.runda == "s25" and args.set == "validare":
        info = cmd_validare_s25(lucru, RADACINA / TEXT_V3)
        info = {**info, "variante": {v: {n: x[n]["s16"] for n in ("s1024", "s2048")} for v, x in info["variante"].items()}}
    elif args.runda == "s25":
        info = cmd_examene_s25(lucru)
        info = {k: v for k, v in info.items() if k not in ("toate", "primele_3_aleasa")}
    elif args.set == "validare":
        info = cmd_validare(lucru, RADACINA / TEXT_V3)
    else:
        info = cmd_examene(lucru)
        info = {k: v for k, v in info.items() if k not in ("toate", "greseli_alese")}
    print(json.dumps(info, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
