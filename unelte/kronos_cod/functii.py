"""Kronos-Cod: câte „funcții scurte cu explicație (și teste)” avem deja în codul descărcat (S65, 3 noiembrie 2026).

Citește doar `lucru/kronos_cod/complet/cod.jsonl` și doar fișierele folosite la antrenare (aceeași împărțire ca la S55:
fără aproape-duplicate, fără lista S53, fără validarea de ~1,17 %). Pentru fișierele Python, cu `ast` (codul NU se
rulează), ia funcțiile de modul și metodele claselor de modul și le notează:
    (a) au explicație (docstring);
    (b) corpul (fără explicație) are 1–30 de linii;
    (c) textul funcției trece verificarea statică a cutiei (`verifica_arborele` din _cutie_interior.py, neschimbată);
    (d) marcaj separat: un exemplu `>>>` în explicație, sau numele funcției apare într-un `assert` dintr-un fișier de
        test din același pachet.
Simbolurile se numără cu tokenizerul de cod din S55, pentru funcțiile (a+b) (textul întreg al funcției).
Duplicatele exacte: după normalizare cu `ast.unparse` (fără comentarii, aceeași așezare).

Scurgerea (pe funcțiile a+b+c), cu regulile S53 (`scurgere.indexeaza` / `scaneaza_text`):
    - setul de PROBĂ (public): problemele cu suprapuneri de 13 simboluri și cu soluția întreagă, plus funcțiile atinse;
    - seturile ascunse (S58 `examen_ascuns`, `ascuns2`): DOAR numărul de funcții care conțin soluția de referință
      întreagă și numărul de probleme atinse așa; niciun text, niciun id. SHA-256 verificat înainte și după.

Ce scrie (în `lucru/kronos_cod/functii/`, nimic în Git):
    rezultat.json   cifrele (refuză să ruleze dacă există)
    functii.tsv     un rând pe funcție (a): indicele din cod.jsonl, linia, sha256 normalizat, marcajele b c d, simboluri
Nu șterge și nu mută nimic din date.

Comanda:
    python -X utf8 -m unelte.kronos_cod.functii ruleaza [--procese 12]
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
import textwrap
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

RADACINA = Path(__file__).resolve().parents[2]
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from module.tokenizer_bpe import TokenizerBPE  # noqa: E402
from unelte.kronos_cod import scurgere  # noqa: E402
from unelte.kronos_cod._cutie_interior import MODULE_DE_BAZA, verifica_arborele  # noqa: E402
from unelte.kronos_cod.tokenizer_cod import COD, DIR_TOK, EXCLUS, MARIME, citeste_excluse, loturi, parte  # noqa: E402

IESIRE = RADACINA / "lucru" / "kronos_cod" / "functii"
TOKENIZER = DIR_TOK / f"bpe_cod_{MARIME}.json"
ASCUNSE = {"s58": RADACINA / "lucru" / "kronos_cod" / "examen_ascuns",
           "ascuns2": RADACINA / "lucru" / "kronos_cod" / "ascuns2"}
LINII_MIN, LINII_MAX = 1, 30
PRAG_DESTUL = 20_000_000
PRAG_PUTIN = 5_000_000
EXEMPLE_PE_LOT = 2
_PERMISE = set(MODULE_DE_BAZA)
_TEST = re.compile(r"(^|/)(tests?|testing)/|(^|/)test_[^/]*\.py$|_test\.py$|(^|/)conftest\.py$")


def e_fisier_de_test(cale: str) -> bool:
    return bool(_TEST.search(cale.replace("\\", "/").lower()))


def nume_din_assert(arbore: ast.AST) -> tuple[set[str], set[str]]:
    """Numele (variabile și atribute) din instrucțiunile `assert`; separat, din apelurile `self.assert*(...)`."""
    din_assert, din_unittest = set(), set()
    for nod in ast.walk(arbore):
        if isinstance(nod, ast.Assert):
            tinta = din_assert
        elif (isinstance(nod, ast.Call) and isinstance(nod.func, ast.Attribute)
              and nod.func.attr.startswith("assert")):
            tinta = din_unittest
        else:
            continue
        for n in ast.walk(nod):
            if isinstance(n, ast.Name):
                tinta.add(n.id)
            elif isinstance(n, ast.Attribute):
                tinta.add(n.attr)
    return din_assert, din_unittest


def functiile(arbore: ast.Module):
    """Funcțiile de modul și metodele claselor de modul (fără funcțiile din alte funcții)."""
    for nod in arbore.body:
        if isinstance(nod, (ast.FunctionDef, ast.AsyncFunctionDef)):
            yield nod
        elif isinstance(nod, ast.ClassDef):
            for m in nod.body:
                if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    yield m


def descrie(nod, linii: list[str]) -> dict:
    """Marcajele (a), (b), (c), doctestul, textul funcției și suma normalizată, pentru o funcție."""
    doc = ast.get_docstring(nod, clean=False)
    are_doc = bool(doc and doc.strip())
    corp = nod.body[1:] if are_doc else nod.body
    n_linii = (nod.end_lineno - corp[0].lineno + 1) if corp else 0
    inceput = min([d.lineno for d in nod.decorator_list] + [nod.lineno])
    text = textwrap.dedent("\n".join(linii[inceput - 1:nod.end_lineno])) + "\n"
    try:
        norm = ast.unparse(nod)
    except Exception:  # noqa: BLE001 — orice construcție pe care unparse n-o știe
        norm = text
    b = are_doc and LINII_MIN <= n_linii <= LINII_MAX
    return {"nume": nod.name, "linia": nod.lineno, "a": are_doc, "b": b,
            "c": b and not verifica_arborele(text, _PERMISE),
            "doctest": are_doc and ">>>" in doc, "linii_corp": n_linii, "text": text,
            "sha": hashlib.sha256(norm.encode("utf-8")).hexdigest()}


_STARE: dict = {}


def _init(stare: dict) -> None:
    global _STARE
    _STARE = dict(stare)
    _STARE["tok"] = TokenizerBPE.incarca(stare["cale_tok"])


def analizeaza_fisier(i: int, r: dict, tok, idx_proba: dict, idx_ascunse: dict) -> dict:
    """Ce găsește într-un fișier de antrenare Python: funcțiile (a) și numele din assert (dacă e fișier de test)."""
    rez = {"functii_toate": 0, "functii": [], "assert": set(), "unittest": set(), "test": False, "sintaxa": False}
    try:
        arbore = ast.parse(r["text"])
    except (SyntaxError, ValueError, RecursionError, MemoryError):
        rez["sintaxa"] = True
        return rez
    cheie = f"{r.get('sursa', '?')}:{r.get('pachet', '?')}"
    rez["test"] = e_fisier_de_test(r.get("cale", ""))
    if rez["test"]:
        rez["assert"], rez["unittest"] = nume_din_assert(arbore)
    linii = r["text"].splitlines()
    for nod in functiile(arbore):
        rez["functii_toate"] += 1
        try:
            d = descrie(nod, linii)
        except RecursionError:
            continue
        if not d["a"]:
            continue
        f = {"i": i, "linia": d["linia"], "nume": d["nume"], "pachet": cheie, "licenta": r.get("licenta", ""),
             "cale": r.get("cale", ""), "b": d["b"], "c": d["c"], "doctest": d["doctest"], "in_test": rez["test"],
             "sha": d["sha"], "octeti": len(d["text"].encode("utf-8")), "linii_corp": d["linii_corp"],
             "simboluri": len(tok.codifica_fara_speciale(d["text"])) if d["b"] else 0,
             "proba_atinse": {}, "proba_exacte": [], "ascunse_exacte": {}}
        if d["c"]:
            g = scurgere.scaneaza_text(d["text"], idx_proba)
            if g:
                f["proba_atinse"], f["proba_exacte"] = g["atinse"], g["exacte"]
            for nume, idx in idx_ascunse.items():
                g = scurgere.scaneaza_text(d["text"], idx)
                if g and g["exacte"]:
                    f["ascunse_exacte"][nume] = g["exacte"]
            f["text"] = d["text"] if d["linii_corp"] <= 8 else None
        rez["functii"].append(f)
    return rez


def _lot(lot) -> dict:
    start, randuri = lot
    out = {"fisiere": 0, "python": 0, "sintaxa": 0, "functii_toate": 0, "functii": [], "assert": {}, "unittest": {},
           "fisiere_test": 0}
    for j, rand in enumerate(randuri):
        i = start + j
        r = json.loads(rand)
        if parte(i, r["text"], _STARE["aproape"], _STARE["scurgere"]) not in ("antrenare", "esantion"):
            continue
        out["fisiere"] += 1
        if r.get("limbaj") != "python":
            continue
        out["python"] += 1
        a = analizeaza_fisier(i, r, _STARE["tok"], _STARE["idx_proba"], _STARE["idx_ascunse"])
        out["sintaxa"] += a["sintaxa"]
        out["functii_toate"] += a["functii_toate"]
        out["fisiere_test"] += a["test"]
        cheie = f"{r.get('sursa', '?')}:{r.get('pachet', '?')}"
        if a["assert"]:
            out["assert"].setdefault(cheie, set()).update(a["assert"])
        if a["unittest"]:
            out["unittest"].setdefault(cheie, set()).update(a["unittest"])
        out["functii"].extend(a["functii"])
    # textele exemplelor: păstrez doar câteva pe lot (restul ar umple memoria degeaba)
    pastrate = {True: 0, False: 0}
    for f in out["functii"]:
        if f.get("text") and pastrate[f["doctest"]] < EXEMPLE_PE_LOT:
            pastrate[f["doctest"]] += 1
        else:
            f.pop("text", None)
    return out


def _sume(fs: list[dict]) -> dict:
    return {"functii": len(fs), "simboluri": sum(f["simboluri"] for f in fs), "octeti": sum(f["octeti"] for f in fs),
            "unice": len({f["sha"] for f in fs}), "duplicate_exacte": len(fs) - len({f["sha"] for f in fs})}


def simboluri_unice(fs: list[dict]) -> int:
    vazute, total = set(), 0
    for f in fs:
        if f["sha"] not in vazute:
            vazute.add(f["sha"])
            total += f["simboluri"]
    return total


def verdict(simboluri_abc: int) -> str:
    if simboluri_abc >= PRAG_DESTUL:
        return "DESTUL"
    if simboluri_abc < PRAG_PUTIN:
        return "PUȚIN"
    return "ÎNTRE"


def _probleme_proba() -> list[dict]:
    from dataclasses import asdict

    from unelte.kronos_cod.examen_cod import set_proba
    return [asdict(p) for p in set_proba()]


def _probleme_ascunse(dosar: Path) -> tuple[list[dict], str]:
    from dataclasses import asdict

    from unelte.kronos_cod.examen_cod import probleme_setului
    sha = scurgere.sha256_fisier(dosar / "probleme.jsonl")
    return [asdict(p) for p in probleme_setului("ascuns", dosar)], sha


def ruleaza(cod: Path = COD, exclus: Path = EXCLUS, iesire: Path = IESIRE, cale_tok: Path = TOKENIZER,
            ascunse: dict | None = None, probleme_proba: list[dict] | None = None, procese: int = 12,
            jurnal=print) -> dict:
    cod, iesire = Path(cod), Path(iesire)
    f_rez = iesire / "rezultat.json"
    if f_rez.exists():
        raise SystemExit(f"{f_rez} există deja: numărătoarea se face o singură dată")
    ascunse = ASCUNSE if ascunse is None else ascunse
    proba = probleme_proba if probleme_proba is not None else _probleme_proba()
    idx_proba = scurgere.indexeaza(proba)
    idx_ascunse, sha_inainte, n_ascunse = {}, {}, {}
    for nume, dosar in ascunse.items():
        probleme, sha_inainte[nume] = _probleme_ascunse(Path(dosar))
        idx_ascunse[nume] = scurgere.indexeaza(probleme)
        n_ascunse[nume] = len(probleme)
        del probleme
    aproape, scurg = citeste_excluse(cod, Path(exclus))
    jurnal(f"proba {len(proba)} probleme; ascunse {n_ascunse}; aproape-duplicate {len(aproape)}, scurgere S53 {len(scurg)}")
    t0 = time.time()
    tot = {"fisiere": 0, "python": 0, "sintaxa": 0, "functii_toate": 0, "fisiere_test": 0}
    functii: list[dict] = []
    asserturi: dict[str, set] = {}
    unittest: dict[str, set] = {}
    stare = {"aproape": aproape, "scurgere": scurg, "cale_tok": str(cale_tok), "idx_proba": idx_proba,
             "idx_ascunse": idx_ascunse}
    loturi_facute = 0
    with Pool(procese, initializer=_init, initargs=(stare,)) as pool:
        for r in pool.imap(_lot, loturi(cod / "cod.jsonl"), chunksize=1):
            for k in tot:
                tot[k] += r[k]
            functii.extend(r["functii"])
            for k, v in r["assert"].items():
                asserturi.setdefault(k, set()).update(v)
            for k, v in r["unittest"].items():
                unittest.setdefault(k, set()).update(v)
            loturi_facute += 1
            if loturi_facute % 10 == 0:
                jurnal(f"{loturi_facute} loturi, {tot['python']} fișiere Python, {len(functii)} funcții (a), "
                       f"{time.time() - t0:.0f} s")
    sha_dupa = {nume: scurgere.sha256_fisier(Path(d) / "probleme.jsonl") for nume, d in ascunse.items()}

    for f in functii:
        f["d_assert"] = f["nume"] in asserturi.get(f["pachet"], ())
        f["d_unittest"] = f["nume"] in unittest.get(f["pachet"], ())
        f["d"] = f["doctest"] or f["d_assert"]
    a = functii
    ab = [f for f in a if f["b"]]
    abc = [f for f in ab if f["c"]]
    abcd = [f for f in abc if f["d"]]
    niveluri = {"a": _sume(a), "a+b": _sume(ab), "a+b+c": _sume(abc), "a+b+c+d": _sume(abcd)}
    for nume, fs in (("a+b", ab), ("a+b+c", abc), ("a+b+c+d", abcd)):
        niveluri[nume]["simboluri_unice"] = simboluri_unice(fs)
    niveluri["a"].pop("simboluri")
    d_parti = {"doar_doctest": sum(1 for f in abcd if f["doctest"] and not f["d_assert"]),
               "doar_assert": sum(1 for f in abcd if f["d_assert"] and not f["doctest"]),
               "ambele": sum(1 for f in abcd if f["d_assert"] and f["doctest"]),
               "cu_unittest_in_loc_de_assert (informativ)": sum(
                   1 for f in abc if not f["d"] and f["d_unittest"])}
    pe_pachet = Counter(f["pachet"] for f in abc)
    simb_pachet = Counter()
    for f in abc:
        simb_pachet[f["pachet"]] += f["simboluri"]
    licente = Counter(f["licenta"] for f in abc)

    # scurgerea pe setul de probă
    pe_prob_proba = []
    for k, p in enumerate(proba):
        sup = [f["proba_atinse"][k] for f in abc if k in f["proba_atinse"]]
        pe_prob_proba.append({"id": p["id"], "functii_suprapunere": len(sup), "cea_mai_lunga": max(sup, default=0),
                              "functii_solutie_exacta": sum(1 for f in abc if k in f["proba_exacte"])})
    scurgere_proba = {
        "probleme": len(proba),
        "probleme_cu_suprapunere": sum(1 for x in pe_prob_proba if x["functii_suprapunere"]),
        "probleme_cu_solutia_exacta": sum(1 for x in pe_prob_proba if x["functii_solutie_exacta"]),
        "functii_atinse": sum(1 for f in abc if f["proba_atinse"] or f["proba_exacte"]),
        "functii_atinse_simboluri": sum(f["simboluri"] for f in abc if f["proba_atinse"] or f["proba_exacte"]),
        "pe_problema": pe_prob_proba}
    scurgere_ascunse = {}
    for nume in ascunse:
        cu = [f for f in abc if nume in f["ascunse_exacte"]]
        scurgere_ascunse[nume] = {"probleme": n_ascunse[nume], "functii_cu_solutia_intreaga": len(cu),
                                  "probleme_atinse": len({p for f in cu for p in f["ascunse_exacte"][nume]}),
                                  "sha_neschimbat": sha_inainte[nume] == sha_dupa[nume]}
    exemple = [{k: f[k] for k in ("pachet", "licenta", "cale", "linia", "nume", "doctest", "d_assert", "text")}
               for f in abcd if f.get("text")]
    exemple = sorted(exemple, key=lambda e: hashlib.sha256(f"{e['cale']}:{e['linia']}".encode()).hexdigest())[:20]
    v = verdict(niveluri["a+b+c"]["simboluri"])
    rez = {"sarcina": "S65", "secunde": round(time.time() - t0, 1), "tokenizer": str(cale_tok),
           "sha256_tokenizer": scurgere.sha256_fisier(Path(cale_tok)), **tot, "niveluri": niveluri,
           "d_parti": d_parti, "din_fisiere_de_test_abc": sum(1 for f in abc if f["in_test"]),
           "linii_corp_abc": dict(sorted(Counter(f["linii_corp"] for f in abc).items())),
           "primele_20_pachete": [{"pachet": p, "functii": n, "simboluri": simb_pachet[p]}
                                  for p, n in pe_pachet.most_common(20)],
           "licente_abc": dict(licente.most_common()), "scurgere_proba": scurgere_proba,
           "scurgere_ascunse": scurgere_ascunse,
           "praguri": {"DESTUL": PRAG_DESTUL, "PUTIN": PRAG_PUTIN}, "verdict": v, "exemple": exemple}
    iesire.mkdir(parents=True, exist_ok=True)
    with open(iesire / "functii.tsv", "w", encoding="utf-8", newline="\n") as fo:
        fo.write("i\tlinia\tsha256_normalizat\tb\tc\td\tdoctest\tsimboluri\tpachet\tcale\n")
        for f in a:
            fo.write(f"{f['i']}\t{f['linia']}\t{f['sha']}\t{int(f['b'])}\t{int(f['c'])}\t{int(f['d'])}\t"
                     f"{int(f['doctest'])}\t{f['simboluri']}\t{f['pachet']}\t{f['cale']}\n")
    f_rez.write_text(json.dumps(rez, ensure_ascii=False, indent=1), encoding="utf-8")
    jurnal(json.dumps({"niveluri": niveluri, "verdict": v, "scurgere_ascunse": scurgere_ascunse},
                      ensure_ascii=False))
    return rez


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="comanda", required=True)
    r = sub.add_parser("ruleaza", help="numărătoarea, o singură dată")
    r.add_argument("--procese", type=int, default=12)
    a = ap.parse_args(argv)
    j = lambda m: print(time.strftime("%H:%M:%S"), m, flush=True)  # noqa: E731
    ruleaza(procese=a.procese, jurnal=j)
    return 0


if __name__ == "__main__":
    sys.exit(main())
