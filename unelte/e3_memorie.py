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

Ies doar în lucru/e3/ (nu în Git: Wikipedia e CC BY-SA). Nu atinge kronos/, examenul BPB, paznicul, datele de examen
(doar citite), text_v3, e2/ sau unelte/verificator_text.py.
"""

from __future__ import annotations

import argparse
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


def intrebari_validare(cale: Path, cate: int = CATE_VALIDARE, samanta: int = SAMANTA) -> tuple[list[dict], int]:
    """`cate` întrebări la întâmplare din text_v3: „text”, fără da/nu / „Nu scrie”, cu răspunsul găsit în text."""
    bune = []
    for r in cale.read_text(encoding="utf-8").splitlines():
        if not r.strip():
            continue
        p = json.loads(r)
        if p.get("fel") == "text" and _fel_special(p["raspuns"]) is None and verifica(p["raspuns"], p["text"])["corect"]:
            bune.append({"intrebare": p["intrebare"], "raspuns": p["raspuns"], "text": p["text"], "tip": p.get("tip")})
    return random.Random(samanta).sample(bune, min(cate, len(bune))), len(bune)


# ---------------------------------------------------------------- căutarea

def _ghilimele(cuv: str) -> str:
    return '"' + cuv.replace('"', '""') + '"'


def interogare(intrebare: str, varianta: str) -> str:
    """Interogarea FTS5 pentru o variantă (cuvintele normalizate ca la verificator, fiecare între ghilimele)."""
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


def cauta(con: sqlite3.Connection, intrebare: str, varianta: str, k: int = max(K)) -> list[dict[str, Any]]:
    """Primele k bucăți după BM25. La „fara_cuvinte_si”, dacă AND aduce sub k, se completează cu OR."""
    sql = "SELECT rowid, text, articol, sursa FROM bucati WHERE bucati MATCH ? ORDER BY rank LIMIT ?"
    gasite = con.execute(sql, (interogare(intrebare, varianta), k)).fetchall()
    if varianta == "fara_cuvinte_si" and len(gasite) < k:
        vazute = {g[0] for g in gasite}
        gasite += [g for g in con.execute(sql, (interogare(intrebare, "fara_cuvinte"), k)).fetchall()
                   if g[0] not in vazute][: k - len(gasite)]
    return [{"rowid": g[0], "text": g[1], "articol": g[2], "sursa": g[3]} for g in gasite]


def primul_bun(gasite: list[dict[str, Any]], raspuns: str) -> int | None:
    """Locul (de la 1) primei bucăți care conține răspunsul (regula principală a verificatorului S16)."""
    for i, g in enumerate(gasite, 1):
        if verifica(raspuns, g["text"])["corect"]:
            return i
    return None


def procente(locuri: list[int | None], k: Iterable[int] = K) -> dict[str, Any]:
    n = len(locuri)
    return {f"k{x}": {"bune": sum(1 for l in locuri if l is not None and l <= x),
                      "procent": round(100 * sum(1 for l in locuri if l is not None and l <= x) / n, 1) if n else 0.0}
            for x in k}


def masoara_intrebari(con: sqlite3.Connection, intrebari: list[dict[str, Any]], varianta: str) -> list[dict[str, Any]]:
    rez = []
    for q in intrebari:
        t = time.perf_counter()
        gasite = cauta(con, q["intrebare"], varianta)
        rez.append({**q, "loc": primul_bun(gasite, q["raspuns"]), "secunde": time.perf_counter() - t,
                    "gasite": gasite})
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


def cmd_examene(lucru: Path, examene: dict[str, str] = EXAMENE) -> dict[str, Any]:
    if (lucru / "examene.json").exists():
        raise SystemExit("examenele s-au măsurat deja (o singură rulare, regula S24)")
    varianta = json.loads((lucru / "validare.json").read_text(encoding="utf-8"))["aleasa"]
    texte = {t["text"]: t for t in json.loads((lucru / "texte_examen.json").read_text(encoding="utf-8"))}
    intrebari = intrebari_examen(examene)
    con = deschide(lucru / "index.sqlite")
    rez = masoara_intrebari(con, intrebari, varianta)
    con.close()
    for r in rez:
        t = texte[r["text"]]
        corecte = set(t["articole_probabile"]) | ({t["in_wikipedia"]} if t["in_wikipedia"] else set()) | {t["id"]}
        r["articol_gasit_la_5"] = any(g["articol"] in corecte for g in r["gasite"][:5])
        r["raspuns_in_textul_examenului"] = verifica(r["raspuns"], r["text"])["corect"]

    def rezumat(parte: list[dict[str, Any]]) -> dict[str, Any]:
        return {"intrebari": len(parte), "i_cautare": procente([r["loc"] for r in parte]),
                "ii_articol_la_5": {"bune": sum(r["articol_gasit_la_5"] for r in parte),
                                    "procent": round(100 * sum(r["articol_gasit_la_5"] for r in parte) / len(parte), 1)
                                    if parte else 0.0}}

    pe_examen = {f"{n}_{c}": rezumat([r for r in rez if r["examen"] == n and (r["categorie"] or "text") == c])
                 for n, c in sorted({(r["examen"], r["categorie"] or "text") for r in rez}, key=str)}
    for n in examene:
        pe_examen[n] = rezumat([r for r in rez if r["examen"] == n])
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
    m.add_argument("--set", choices=("validare", "examene"), required=True)
    sub.add_parser("lungimi")
    args = parser.parse_args(argv)
    lucru, wikipedia = RADACINA / args.lucru, RADACINA / args.wikipedia
    if args.pas == "index":
        info = cmd_index(wikipedia, lucru)
    elif args.pas == "adauga":
        info = cmd_adauga(lucru)
    elif args.pas == "lungimi":
        info = cmd_lungimi(wikipedia, lucru, RADACINA / TOKENIZER)
    elif args.set == "validare":
        info = cmd_validare(lucru, RADACINA / TEXT_V3)
    else:
        info = cmd_examene(lucru)
        info = {k: v for k, v in info.items() if k not in ("toate", "greseli_alese")}
    print(json.dumps(info, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
