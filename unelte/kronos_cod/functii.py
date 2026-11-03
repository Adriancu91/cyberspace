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


# ---------------------------------------------------------------------------------------------------------------
# S67 (3 noiembrie 2026): comanda `curata` — funcțiile (a+b+c) „cu adevărat ca la examen”.
#   pornește de la functii.tsv (S65): doar (a+b+c), fără duplicatele exacte (prima apariție a fiecărei sume);
#   (i)   simbolurile DOAR ale corpului (fără semnătură, fără docstring), cu tokenizerul S55;
#   (ii)  filtrul celor triviale (corpul = o singură instrucțiune `pass`, `...`, `raise …`, `return`, `return <nume
#         sau constantă>` sau doar un apel `super().…`);
#   (iii) proba definiției: textul funcției (cu decoratori) rulat în cutie (neschimbată) ca modul separat, fără apel
#         (doar pentru cele care trec (ii)); apoi cu `ast`: toate numele libere din corp sunt parametri, nume locale,
#         funcții de bază ale lui Python sau module permise de cutie.
#   „autonome” = trec (ii) și (iii). Rezultatele cutiei se scriu pe rând în cutie.jsonl, deci o rulare oprită se
#   reia de unde a rămas (`--pana-la HH:MM` oprește curat la ora dată).
# Comanda:  python -X utf8 -m unelte.kronos_cod.functii curata [--procese 12] [--fire 16] [--pana-la 08:40]
# ---------------------------------------------------------------------------------------------------------------

PRAG_A_DESTUL = 10_000_000
PRAG_A_PUTIN = 3_000_000
EXEMPLE_CURATA = 5
_BUILTINS = set(dir(__import__("builtins")))


def text_corp(nod, linii: list[str]) -> str:
    """Textul corpului (fără semnătură și fără docstring), dedentat; "" dacă nu are corp după docstring."""
    doc = ast.get_docstring(nod, clean=False)
    corp = nod.body[1:] if doc is not None and doc.strip() else nod.body
    if not corp:
        return ""
    bucata = linii[corp[0].lineno - 1:nod.end_lineno]
    prim = bucata[0]
    if prim[:corp[0].col_offset].strip():  # corpul începe pe același rând cu altceva (de ex. `def f(): return 1`)
        bucata[0] = " " * corp[0].col_offset + prim[corp[0].col_offset:]
    return textwrap.dedent("\n".join(bucata)) + "\n"


def e_triviala(nod) -> bool:
    doc = ast.get_docstring(nod, clean=False)
    corp = nod.body[1:] if doc is not None and doc.strip() else nod.body
    if len(corp) != 1:
        return not corp
    s = corp[0]
    if isinstance(s, (ast.Pass, ast.Raise)):
        return True
    if isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant) and s.value.value is Ellipsis:
        return True
    if isinstance(s, ast.Return) and (s.value is None or isinstance(s.value, (ast.Name, ast.Constant))):
        return True
    val = s.value if isinstance(s, (ast.Expr, ast.Return)) else None
    if isinstance(val, ast.Call) and isinstance(val.func, ast.Attribute):
        tinta = val.func.value
        if (isinstance(tinta, ast.Call) and isinstance(tinta.func, ast.Name) and tinta.func.id == "super"):
            return True
    return False


def nume_libere(nod) -> set[str]:
    """Numele citite în corp care nu sunt parametri, nume locale (atribuite, bucle, `with`, `except`, importuri,
    funcții/clase interioare și parametrii lor), funcții de bază sau module permise. `global`/`nonlocal` = libere."""
    doc = ast.get_docstring(nod, clean=False)
    corp = nod.body[1:] if doc is not None and doc.strip() else nod.body
    locale, citite, declarate = set(), set(), set()
    toate_arg = nod.args.posonlyargs + nod.args.args + nod.args.kwonlyargs + [
        x for x in (nod.args.vararg, nod.args.kwarg) if x]
    locale.update(a.arg for a in toate_arg)
    for s in corp:
        for n in ast.walk(s):
            if isinstance(n, ast.Name):
                (citite if isinstance(n.ctx, ast.Load) else locale).add(n.id)
            elif isinstance(n, ast.arg):
                locale.add(n.arg)
            elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                locale.add(n.name)
            elif isinstance(n, ast.ExceptHandler) and n.name:
                locale.add(n.name)
            elif isinstance(n, (ast.Import, ast.ImportFrom)):
                for al in n.names:
                    locale.add(al.asname or al.name.split(".")[0])
            elif isinstance(n, (ast.Global, ast.Nonlocal)):
                declarate.update(n.names)
            elif isinstance(n, (ast.MatchAs, ast.MatchStar)) and n.name:
                locale.add(n.name)
            elif isinstance(n, ast.MatchMapping) and n.rest:
                locale.add(n.rest)
    return (citite - (locale - declarate) - _BUILTINS - _PERMISE) | declarate


def module_neimportate(nod) -> bool:
    """Informativ: corpul folosește un modul permis (de ex. `math`) fără să-l importe el însuși."""
    doc = ast.get_docstring(nod, clean=False)
    corp = nod.body[1:] if doc is not None and doc.strip() else nod.body
    importate, citite = set(), set()
    for s in corp:
        for n in ast.walk(s):
            if isinstance(n, (ast.Import, ast.ImportFrom)):
                importate.update(al.asname or al.name.split(".")[0] for al in n.names)
            elif isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
                citite.add(n.id)
    return bool((citite & _PERMISE) - importate)


def citeste_tsv_abc(f_tsv: Path) -> dict[int, list[dict]]:
    """Din functii.tsv: doar (a+b+c), prima apariție a fiecărei sume normalizate; grupate pe indicele fișierului."""
    vazute, pe_fisier = set(), {}
    with open(f_tsv, encoding="utf-8") as f:
        cap = f.readline().rstrip("\n").split("\t")
        for rand in f:
            r = dict(zip(cap, rand.rstrip("\n").split("\t")))
            if r["c"] != "1" or r["sha256_normalizat"] in vazute:
                continue
            vazute.add(r["sha256_normalizat"])
            pe_fisier.setdefault(int(r["i"]), []).append(
                {"linia": int(r["linia"]), "sha": r["sha256_normalizat"], "d": r["d"] == "1",
                 "doctest": r["doctest"] == "1", "simboluri": int(r["simboluri"]), "pachet": r["pachet"],
                 "cale": r["cale"]})
    return pe_fisier


def analizeaza_curata(r: dict, cerute: list[dict], tok, idx_proba: dict, idx_ascunse: dict) -> list[dict]:
    """Pentru funcțiile cerute dintr-un fișier: corpul, simbolurile lui, trivială?, numele libere, scurgerea."""
    try:
        arbore = ast.parse(r["text"])
    except (SyntaxError, ValueError, RecursionError, MemoryError):
        return [dict(f, gasita=False) for f in cerute]
    linii = r["text"].splitlines()
    pe_linie = {n.lineno: n for n in functiile(arbore)}
    out = []
    for f in cerute:
        f = dict(f, licenta=r.get("licenta", ""), gasita=False)
        nod = pe_linie.get(f["linia"])
        if nod is None:
            out.append(f)
            continue
        try:
            d = descrie(nod, linii)
            if d["sha"] != f["sha"]:
                out.append(f)
                continue
            corp = text_corp(nod, linii)
            f.update(gasita=True, nume=nod.name, text=d["text"], linii_corp=d["linii_corp"],
                     simboluri_corp=len(tok.codifica_fara_speciale(corp)) if corp else 0,
                     triviala=e_triviala(nod), libere=sorted(nume_libere(nod)),
                     modul_neimportat=module_neimportate(nod))
        except RecursionError:
            out.append(f)
            continue
        f["proba_atinse"], f["proba_exacte"], f["ascunse_exacte"] = {}, [], {}
        if not f["triviala"]:
            g = scurgere.scaneaza_text(d["text"], idx_proba)
            if g:
                f["proba_atinse"], f["proba_exacte"] = g["atinse"], sorted(g["exacte"])
            for nume, idx in idx_ascunse.items():
                g = scurgere.scaneaza_text(d["text"], idx)
                if g and g["exacte"]:
                    f["ascunse_exacte"][nume] = sorted(g["exacte"])
        out.append(f)
    return out


def _lot_curata(lot) -> list[dict]:
    start, randuri = lot
    out = []
    for j, rand in enumerate(randuri):
        cerute = _STARE["cerute"].get(start + j)
        if cerute:
            out.extend(analizeaza_curata(json.loads(rand), cerute, _STARE["tok"], _STARE["idx_proba"],
                                         _STARE["idx_ascunse"]))
    return out


def proba_in_cutie(text: str) -> dict:
    from unelte.kronos_cod import cutie
    r = cutie.ruleaza(text, [], limita_secunde=5.0, limita_mb=256)
    return {"stare": r.stare, "mesaj": r.mesaj[:200]}


def verdict_curata(simboluri_corp: int) -> str:
    if simboluri_corp >= PRAG_A_DESTUL:
        return "DESTUL PENTRU A"
    if simboluri_corp < PRAG_A_PUTIN:
        return "PUȚIN"
    return "ÎNTRE"


def _sume_curata(fs: list[dict]) -> dict:
    return {"functii": len(fs), "simboluri_intregi": sum(f["simboluri"] for f in fs),
            "simboluri_corp": sum(f.get("simboluri_corp", 0) for f in fs)}


def _cu_si_fara_d(fs: list[dict]) -> dict:
    return {"toate": _sume_curata(fs), "cu_d": _sume_curata([f for f in fs if f["d"]])}


def _ora_trecuta(pana_la: str | None) -> bool:
    return bool(pana_la) and time.strftime("%H:%M") >= pana_la


def curata(cod: Path = COD, iesire: Path = IESIRE, cale_tok: Path = TOKENIZER, ascunse: dict | None = None,
           probleme_proba: list[dict] | None = None, procese: int = 12, fire: int = 16, pana_la: str | None = None,
           cutia=proba_in_cutie, jurnal=print) -> dict | None:
    """S67. Întoarce rezultatul (și scrie curata.json), sau None dacă s-a oprit la `pana_la` (se reia)."""
    from concurrent.futures import ThreadPoolExecutor

    cod, iesire = Path(cod), Path(iesire)
    f_rez = iesire / "curata.json"
    if f_rez.exists():
        raise SystemExit(f"{f_rez} există deja: curățarea se face o singură dată")
    ascunse = ASCUNSE if ascunse is None else ascunse
    proba = probleme_proba if probleme_proba is not None else _probleme_proba()
    idx_proba = scurgere.indexeaza(proba)
    idx_ascunse, sha_inainte, n_ascunse = {}, {}, {}
    for nume, dosar in ascunse.items():
        probleme, sha_inainte[nume] = _probleme_ascunse(Path(dosar))
        idx_ascunse[nume] = scurgere.indexeaza(probleme)
        n_ascunse[nume] = len(probleme)
        del probleme
    cerute = citeste_tsv_abc(iesire / "functii.tsv")
    n_cerute = sum(len(v) for v in cerute.values())
    jurnal(f"(a+b+c) fără duplicate: {n_cerute} funcții în {len(cerute)} fișiere; ascunse {n_ascunse}")
    t0 = time.time()
    functii_g: list[dict] = []
    stare = {"cerute": cerute, "cale_tok": str(cale_tok), "idx_proba": idx_proba, "idx_ascunse": idx_ascunse}
    with Pool(procese, initializer=_init, initargs=(stare,)) as pool:
        for k, r in enumerate(pool.imap(_lot_curata, loturi(cod / "cod.jsonl"), chunksize=1), 1):
            functii_g.extend(r)
            if k % 20 == 0:
                jurnal(f"{k} loturi citite, {len(functii_g)} funcții, {time.time() - t0:.0f} s")
    jurnal(f"partea fără cutie gata: {len(functii_g)} funcții, {time.time() - t0:.0f} s")

    # proba definiției în cutie, cu reluare din cutie.jsonl
    f_cutie = iesire / "cutie.jsonl"
    facute = {}
    if f_cutie.exists():
        for rand in f_cutie.read_text(encoding="utf-8").splitlines():
            if rand.strip():
                x = json.loads(rand)
                facute[x["sha"]] = x
    de_facut = [f for f in functii_g if f["gasita"] and not f["triviala"] and f["sha"] not in facute]
    jurnal(f"cutia: {len(facute)} deja făcute, {len(de_facut)} de făcut, {fire} fire")
    t1, oprita = time.time(), False
    with open(f_cutie, "a", encoding="utf-8", newline="\n") as fo, ThreadPoolExecutor(fire) as ex:
        for k0 in range(0, len(de_facut), 2000):
            if _ora_trecuta(pana_la):
                oprita = True
                break
            bucata = de_facut[k0:k0 + 2000]
            for f, rc in zip(bucata, ex.map(lambda f: cutia(f["text"]), bucata)):
                x = {"sha": f["sha"], **rc}
                facute[f["sha"]] = x
                fo.write(json.dumps(x, ensure_ascii=False) + "\n")
            fo.flush()
            jurnal(f"cutia: {k0 + len(bucata)}/{len(de_facut)}, {time.time() - t1:.0f} s")
    if oprita:
        jurnal(f"oprită curat la {time.strftime('%H:%M')} (--pana-la {pana_la}); se reia cu aceeași comandă")
        return None
    sha_dupa = {nume: scurgere.sha256_fisier(Path(d) / "probleme.jsonl") for nume, d in ascunse.items()}

    gasite = [f for f in functii_g if f["gasita"]]
    netriv = [f for f in gasite if not f["triviala"]]
    for f in netriv:
        f["cutie"] = facute[f["sha"]]["stare"]
    defin = [f for f in netriv if f["cutie"] == "ok"]
    auto = [f for f in defin if not f["libere"]]
    pasi = {"a+b+c fără duplicate": _cu_si_fara_d(gasite), "(ii) netriviale": _cu_si_fara_d(netriv),
            "(iii) definiția trece în cutie": _cu_si_fara_d(defin), "(iii) + fără nume libere = autonome": _cu_si_fara_d(auto)}
    nume_lipsa = Counter()
    for f in netriv:
        if f["cutie"] != "ok":
            m = re.match(r"NameError: name '([^']+)'", facute[f["sha"]].get("mesaj", ""))
            if m:
                nume_lipsa[m.group(1)] += 1
    libere_top = Counter(n for f in defin for n in f["libere"])
    lungimi = Counter()
    for f in auto:
        n = f["linii_corp"]
        lungimi["1" if n <= 1 else "2–3" if n <= 3 else "4–8" if n <= 8 else "9–15" if n <= 15 else "16–30"] += 1
    simb_corp = Counter()
    for f in auto:
        s = f["simboluri_corp"]
        simb_corp["≤16" if s <= 16 else "17–64" if s <= 64 else "65–256" if s <= 256 else ">256"] += 1
    pe_pachet, simb_pachet = Counter(f["pachet"] for f in auto), Counter()
    for f in auto:
        simb_pachet[f["pachet"]] += f["simboluri_corp"]

    pe_prob = []
    for k, p in enumerate(proba):
        sup = [f["proba_atinse"][k] for f in auto if k in f["proba_atinse"]]
        pe_prob.append({"id": p["id"], "functii_suprapunere": len(sup), "cea_mai_lunga": max(sup, default=0),
                        "functii_solutie_exacta": sum(1 for f in auto if k in f["proba_exacte"])})
    scurgere_proba = {"probleme": len(proba),
                      "probleme_cu_suprapunere": sum(1 for x in pe_prob if x["functii_suprapunere"]),
                      "probleme_cu_solutia_exacta": sum(1 for x in pe_prob if x["functii_solutie_exacta"]),
                      "functii_atinse": sum(1 for f in auto if f["proba_atinse"] or f["proba_exacte"]),
                      "pe_problema": [x for x in pe_prob if x["functii_suprapunere"] or x["functii_solutie_exacta"]]}
    scurgere_asc = {}
    for nume in ascunse:
        cu = [f for f in auto if nume in f["ascunse_exacte"]]
        scurgere_asc[nume] = {"probleme": n_ascunse[nume], "functii_cu_solutia_intreaga": len(cu),
                              "probleme_atinse": len({p for f in cu for p in f["ascunse_exacte"][nume]}),
                              "sha_neschimbat": sha_inainte[nume] == sha_dupa[nume]}
    scurte = [f for f in auto if 3 <= f["linii_corp"] <= 8]
    scurte.sort(key=lambda f: hashlib.sha256(f"{f['cale']}:{f['linia']}".encode()).hexdigest())
    exemple = [{k: f[k] for k in ("pachet", "licenta", "cale", "linia", "nume", "d", "simboluri_corp", "text")}
               for f in scurte[:EXEMPLE_CURATA]]
    v = verdict_curata(pasi["(iii) + fără nume libere = autonome"]["toate"]["simboluri_corp"])
    rez = {"sarcina": "S67", "secunde": round(time.time() - t0, 1), "cerute": n_cerute,
           "negasite": len(functii_g) - len(gasite), "pasi": pasi,
           "cutie_stari": dict(Counter(f["cutie"] for f in netriv).most_common()),
           "cutie_nume_lipsa_top20": nume_lipsa.most_common(20),
           "nume_libere_top20 (definiția trece, dar corpul cere nume din afară)": libere_top.most_common(20),
           "autonome_cu_modul_permis_neimportat (informativ)": sum(1 for f in auto if f["modul_neimportat"]),
           "autonome_linii_corp": dict(lungimi), "autonome_simboluri_corp": dict(simb_corp),
           "primele_20_pachete": [{"pachet": p, "functii": n, "simboluri_corp": simb_pachet[p]}
                                  for p, n in pe_pachet.most_common(20)],
           "licente_autonome": dict(Counter(f["licenta"] for f in auto).most_common()),
           "scurgere_proba": scurgere_proba, "scurgere_ascunse": scurgere_asc,
           "praguri": {"DESTUL PENTRU A": PRAG_A_DESTUL, "PUTIN": PRAG_A_PUTIN}, "verdict": v, "exemple": exemple}
    with open(iesire / "autonome.tsv", "w", encoding="utf-8", newline="\n") as fo:
        fo.write("i\tlinia\tsha256_normalizat\td\tdoctest\tlinii_corp\tsimboluri\tsimboluri_corp\tmodul_neimportat\t"
                 "pachet\tcale\n")
        idx_fisier = {(f["cale"], f["linia"], f["sha"]): i for i, v_ in cerute.items() for f in v_}
        for f in auto:
            fo.write(f"{idx_fisier[(f['cale'], f['linia'], f['sha'])]}\t{f['linia']}\t{f['sha']}\t{int(f['d'])}\t"
                     f"{int(f['doctest'])}\t{f['linii_corp']}\t{f['simboluri']}\t{f['simboluri_corp']}\t"
                     f"{int(f['modul_neimportat'])}\t{f['pachet']}\t{f['cale']}\n")
    f_rez.write_text(json.dumps(rez, ensure_ascii=False, indent=1), encoding="utf-8")
    jurnal(json.dumps({"pasi": pasi, "verdict": v, "scurgere_ascunse": scurgere_asc}, ensure_ascii=False))
    return rez


# ---------------------------------------------------------------------------------------------------------------
# S68 (3 noiembrie 2026): comanda `bland` — regula mai blândă la importuri + „chemabile”.
#   pornește de la ieșirile S67: functii.tsv (aceleași funcții cerute), cutie.jsonl (definiția a trecut în cutie);
#   regula blândă: un nume liber din corp e acceptat și dacă e un modul (sau alias de modul) legat la nivelul de sus al
#     fișierului cu `import M` / `import M as A` (și în blocurile `if`/`try` de sus) și rădăcina lui M e în
#     MODULE_DE_BAZA (neschimbat). `from M import x` NU leagă un modul → nu intră (numărat doar informativ).
#     Funcția blândă = rândurile de import necesare + textul funcției; rulată din nou DOAR ca definiție în cutie.
#   S67 scădea modulele permise din numele libere chiar neimportate: „autonome” care folosesc de ex. `math` primesc
#     aici importul de sus dacă există (tot rulate în cutie), iar cele fără niciun import sunt numărate separat.
#   chemabile = funcții de nivel de sus sau `@staticmethod`, primul parametru nu e self/cls/ctx și nu e folosit ca
#     obiect (atribut citit fără apel sau atribut scris); varianta „strictă” = niciun atribut pe primul parametru.
# Comanda:  python -X utf8 -m unelte.kronos_cod.functii bland [--procese 12] [--fire 16] [--pana-la 18:20]
# ---------------------------------------------------------------------------------------------------------------

PRIMI_METODA = {"self", "cls", "ctx"}


def nume_libere_stricte(nod) -> set[str]:
    """Ca `nume_libere`, dar fără să scadă modulele permise (un `math` neimportat rămâne liber)."""
    doc = ast.get_docstring(nod, clean=False)
    corp = nod.body[1:] if doc is not None and doc.strip() else nod.body
    locale, citite, declarate = set(), set(), set()
    toate_arg = nod.args.posonlyargs + nod.args.args + nod.args.kwonlyargs + [
        x for x in (nod.args.vararg, nod.args.kwarg) if x]
    locale.update(a.arg for a in toate_arg)
    for s in corp:
        for n in ast.walk(s):
            if isinstance(n, ast.Name):
                (citite if isinstance(n.ctx, ast.Load) else locale).add(n.id)
            elif isinstance(n, ast.arg):
                locale.add(n.arg)
            elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                locale.add(n.name)
            elif isinstance(n, ast.ExceptHandler) and n.name:
                locale.add(n.name)
            elif isinstance(n, (ast.Import, ast.ImportFrom)):
                for al in n.names:
                    locale.add(al.asname or al.name.split(".")[0])
            elif isinstance(n, (ast.Global, ast.Nonlocal)):
                declarate.update(n.names)
            elif isinstance(n, (ast.MatchAs, ast.MatchStar)) and n.name:
                locale.add(n.name)
            elif isinstance(n, ast.MatchMapping) and n.rest:
                locale.add(n.rest)
    return (citite - (locale - declarate) - _BUILTINS) | declarate


def importuri_sus(arbore: ast.Module) -> tuple[dict, dict]:
    """Numele legate la nivelul de sus: (module, din). module: nume -> (modulul, rândul `import ...`) pentru
    `import M [as A]`; din: nume -> (modulul, rândul `from ...`) pentru `from M import x [as y]`. Prima legare câștigă."""
    module, din = {}, {}

    def parcurge(corp):
        for s in corp:
            if isinstance(s, ast.Import):
                for al in s.names:
                    if al.asname:
                        module.setdefault(al.asname, (al.name, f"import {al.name} as {al.asname}"))
                    else:
                        module.setdefault(al.name.split(".")[0], (al.name, f"import {al.name}"))
            elif isinstance(s, ast.ImportFrom) and not s.level and s.module:
                for al in s.names:
                    if al.name != "*":
                        rand = f"from {s.module} import {al.name}" + (f" as {al.asname}" if al.asname else "")
                        din.setdefault(al.asname or al.name, (s.module, rand))
            elif isinstance(s, ast.If):
                parcurge(s.body)
                parcurge(s.orelse)
            elif isinstance(s, (ast.Try, getattr(ast, "TryStar", ast.Try))):
                parcurge(s.body)
                for h in s.handlers:
                    parcurge(h.body)
                parcurge(s.orelse)
                parcurge(s.finalbody)

    parcurge(arbore.body)
    return module, din


def _radacina_permisa(modul: str) -> bool:
    return modul.split(".")[0] in _PERMISE


def locul_functiilor(arbore: ast.Module) -> dict[int, dict]:
    """linia -> {in_clasa, static, clasa_metoda} pentru funcțiile date de `functiile`."""
    def decor(nod, nume):
        return any((isinstance(d, ast.Name) and d.id == nume) or (isinstance(d, ast.Attribute) and d.attr == nume)
                   for d in nod.decorator_list)
    loc = {}
    for nod in arbore.body:
        if isinstance(nod, (ast.FunctionDef, ast.AsyncFunctionDef)):
            loc[nod.lineno] = {"in_clasa": False, "static": decor(nod, "staticmethod"), "nod": nod}
        elif isinstance(nod, ast.ClassDef):
            for m in nod.body:
                if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    loc[m.lineno] = {"in_clasa": True, "static": decor(m, "staticmethod"), "nod": m}
    return loc


def chemabila(nod, in_clasa: bool, static: bool) -> tuple[bool, bool]:
    """(chemabilă, chemabilă strict). Nivel de sus sau @staticmethod; primul parametru nu e self/cls/ctx și nu e
    folosit ca obiect (atribut citit fără apel / atribut scris). Strict: niciun atribut pe primul parametru."""
    if in_clasa and not static:
        return False, False
    if any((isinstance(d, ast.Name) and d.id == "classmethod") or (isinstance(d, ast.Attribute)
           and d.attr == "classmethod") for d in nod.decorator_list):
        return False, False
    params = nod.args.posonlyargs + nod.args.args
    if not params:
        return True, True
    p = params[0].arg
    if p in PRIMI_METODA:
        return False, False
    apelate, orice, obiect = set(), False, False
    for n in ast.walk(nod):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
            apelate.add(id(n.func))
    for n in ast.walk(nod):
        if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == p:
            orice = True
            if not isinstance(n.ctx, ast.Load) or id(n) not in apelate:
                obiect = True
    return not obiect, not orice


def analizeaza_bland(i: int, r: dict, cerute: list[dict], defin: set, tok, idx_proba: dict,
                     idx_ascunse: dict) -> list[dict]:
    """Doar pentru funcțiile a căror definiție a trecut în cutie la S67 (`defin` = sume): categoria blândă, textul
    blând (importuri + funcție), chemabilă, scurgerea pe textul blând."""
    cerute = [f for f in cerute if f["sha"] in defin]
    if not cerute:
        return []
    out = []
    try:
        arbore = ast.parse(r["text"])
    except (SyntaxError, ValueError, RecursionError, MemoryError):
        return [dict(f, i=i, gasita=False) for f in cerute]
    module, din = importuri_sus(arbore)
    loc = locul_functiilor(arbore)
    for f in analizeaza_curata(r, cerute, tok, idx_proba, idx_ascunse):
        f["i"] = i
        if not f["gasita"]:
            out.append(f)
            continue
        l_ = loc[f["linia"]]
        try:
            stricte = nume_libere_stricte(l_["nod"])
            f["chemabila"], f["chemabila_strict"] = chemabila(l_["nod"], l_["in_clasa"], l_["static"])
        except RecursionError:
            f["gasita"] = False
            out.append(f)
            continue
        f["in_clasa"], f["static"] = l_["in_clasa"], l_["static"]
        rezolvate = {n for n in stricte if n in module and _radacina_permisa(module[n][0])}
        rest = stricte - rezolvate
        f["importuri"] = sorted({module[n][1] for n in rezolvate})
        autonoma = not f["libere"]
        if autonoma:
            f["categorie"] = ("autonoma_fara_import" if rest else
                              "autonoma_cu_import" if f["importuri"] else "autonoma_curata")
        elif not rest:
            f["categorie"] = "bland_candidat"
        else:
            f["categorie"] = "respinsa"
            # informativ: ce ar mai trece cu `from M import x` (M permis) sau dacă cutia ar permite orice modul
            rest_din = {n for n in rest if not (n in din and _radacina_permisa(din[n][0]))}
            f["ar_trece_cu_from"] = not rest_din
            f["module_nepermise"] = sorted({module[n][0].split(".")[0] for n in rest if n in module})
            f["ar_trece_cu_orice_modul"] = all(n in module for n in rest)
            f["rest"] = sorted(rest)
        if f["importuri"] and f["categorie"] in ("autonoma_cu_import", "bland_candidat"):
            f["text_bland"] = "\n".join(f["importuri"]) + "\n\n\n" + f["text"]
            if f["categorie"] == "bland_candidat":
                f["proba_atinse"], f["proba_exacte"], f["ascunse_exacte"] = {}, [], {}
                g = scurgere.scaneaza_text(f["text_bland"], idx_proba)
                if g:
                    f["proba_atinse"], f["proba_exacte"] = g["atinse"], sorted(g["exacte"])
                for nume, idx in idx_ascunse.items():
                    g = scurgere.scaneaza_text(f["text_bland"], idx)
                    if g and g["exacte"]:
                        f["ascunse_exacte"][nume] = sorted(g["exacte"])
        if f["categorie"] == "respinsa":
            f.pop("text", None)  # nu le mai trebuie textul (memoria)
        out.append(f)
    return out


def _lot_bland(lot) -> list[dict]:
    start, randuri = lot
    out = []
    for j, rand in enumerate(randuri):
        cerute = _STARE["cerute"].get(start + j)
        if cerute:
            out.extend(analizeaza_bland(start + j, json.loads(rand), cerute, _STARE["defin"], _STARE["tok"],
                                        _STARE["idx_proba"], _STARE["idx_ascunse"]))
    return out


def _lungime(n: int) -> str:
    return "1" if n <= 1 else "2–3" if n <= 3 else "4–8" if n <= 8 else "9–15" if n <= 15 else "16–30"


def _sume_bland(fs: list[dict]) -> dict:
    return {"functii": len(fs), "simboluri_corp": sum(f["simboluri_corp"] for f in fs),
            "simboluri_intregi": sum(f["simboluri"] for f in fs)}


def _chem(fs: list[dict]) -> dict:
    """toate / chemabile / metode, fiecare cu și fără (d)."""
    def cu_d(xs):
        return {"toate": _sume_bland(xs), "cu_d": _sume_bland([f for f in xs if f["d"]])}
    return {"toate": cu_d(fs), "chemabile": cu_d([f for f in fs if f["chemabila"]]),
            "metode": cu_d([f for f in fs if not f["chemabila"]]),
            "chemabile_strict (informativ)": cu_d([f for f in fs if f["chemabila_strict"]])}


def bland(cod: Path = COD, iesire: Path = IESIRE, cale_tok: Path = TOKENIZER, ascunse: dict | None = None,
          probleme_proba: list[dict] | None = None, procese: int = 12, fire: int = 16, pana_la: str | None = None,
          cutia=proba_in_cutie, jurnal=print) -> dict | None:
    """S68. Întoarce rezultatul (și scrie bland.json), sau None dacă s-a oprit la `pana_la` (se reia)."""
    from concurrent.futures import ThreadPoolExecutor

    cod, iesire = Path(cod), Path(iesire)
    f_rez = iesire / "bland.json"
    if f_rez.exists():
        raise SystemExit(f"{f_rez} există deja: numărătoarea blândă se face o singură dată")
    ascunse = ASCUNSE if ascunse is None else ascunse
    proba = probleme_proba if probleme_proba is not None else _probleme_proba()
    idx_proba = scurgere.indexeaza(proba)
    idx_ascunse, sha_inainte, n_ascunse = {}, {}, {}
    for nume, dosar in ascunse.items():
        probleme, sha_inainte[nume] = _probleme_ascunse(Path(dosar))
        idx_ascunse[nume] = scurgere.indexeaza(probleme)
        n_ascunse[nume] = len(probleme)
        del probleme
    cerute = citeste_tsv_abc(iesire / "functii.tsv")
    cutie_s67 = {}
    for rand in (iesire / "cutie.jsonl").read_text(encoding="utf-8").splitlines():
        if rand.strip():
            x = json.loads(rand)
            cutie_s67[x["sha"]] = x["stare"]
    defin = {s for s, st in cutie_s67.items() if st == "ok"}
    n_auto_s67 = sum(1 for _ in open(iesire / "autonome.tsv", encoding="utf-8")) - 1
    jurnal(f"S67: {len(defin)} definiții trecute în cutie, {n_auto_s67} autonome; ascunse {n_ascunse}")
    t0 = time.time()
    fs: list[dict] = []
    stare = {"cerute": cerute, "defin": defin, "cale_tok": str(cale_tok), "idx_proba": idx_proba,
             "idx_ascunse": idx_ascunse}
    with Pool(procese, initializer=_init, initargs=(stare,)) as pool:
        for k, r in enumerate(pool.imap(_lot_bland, loturi(cod / "cod.jsonl"), chunksize=1), 1):
            fs.extend(r)
            if k % 20 == 0:
                jurnal(f"{k} loturi citite, {len(fs)} funcții, {time.time() - t0:.0f} s")
    jurnal(f"partea fără cutie gata: {len(fs)} funcții, {time.time() - t0:.0f} s")

    f_cutie = iesire / "cutie_bland.jsonl"
    facute = {}
    if f_cutie.exists():
        for rand in f_cutie.read_text(encoding="utf-8").splitlines():
            if rand.strip():
                x = json.loads(rand)
                facute[x["sha"]] = x
    de_facut = [f for f in fs if f.get("text_bland") and f["sha"] not in facute]
    jurnal(f"cutia: {len(facute)} deja făcute, {len(de_facut)} de făcut, {fire} fire")
    t1, oprita = time.time(), False
    with open(f_cutie, "a", encoding="utf-8", newline="\n") as fo, ThreadPoolExecutor(fire) as ex:
        for k0 in range(0, len(de_facut), 2000):
            if _ora_trecuta(pana_la):
                oprita = True
                break
            bucata = de_facut[k0:k0 + 2000]
            for f, rc in zip(bucata, ex.map(lambda f: cutia(f["text_bland"]), bucata)):
                x = {"sha": f["sha"], **rc}
                facute[f["sha"]] = x
                fo.write(json.dumps(x, ensure_ascii=False) + "\n")
            fo.flush()
            jurnal(f"cutia: {k0 + len(bucata)}/{len(de_facut)}, {time.time() - t1:.0f} s")
    if oprita:
        jurnal(f"oprită curat la {time.strftime('%H:%M')} (--pana-la {pana_la}); se reia cu aceeași comandă")
        return None
    sha_dupa = {nume: scurgere.sha256_fisier(Path(d) / "probleme.jsonl") for nume, d in ascunse.items()}

    gasite = [f for f in fs if f["gasita"]]
    for f in gasite:
        f["cutie_bland"] = facute[f["sha"]]["stare"] if f.get("text_bland") else None
    auto = [f for f in gasite if f["categorie"].startswith("autonoma")]
    cand = [f for f in gasite if f["categorie"] == "bland_candidat"]
    blande = [f for f in cand if f["cutie_bland"] == "ok"]
    for f in blande:
        f["categorie"] = "blanda"
    cat = Counter(f["categorie"] for f in gasite)
    noua = auto + blande
    stricta = [f for f in noua if f["categorie"] != "autonoma_fara_import"]
    resp = [f for f in gasite if f["categorie"] == "respinsa"]
    chem = [f for f in noua if f["chemabila"]]

    lung = Counter(_lungime(f["linii_corp"]) for f in chem)
    simb = Counter("≤16" if f["simboluri_corp"] <= 16 else "17–64" if f["simboluri_corp"] <= 64
                   else "65–256" if f["simboluri_corp"] <= 256 else ">256" for f in chem)
    pe_pachet, simb_pachet = Counter(f["pachet"] for f in chem), Counter()
    for f in chem:
        simb_pachet[f["pachet"]] += f["simboluri_corp"]
    mod_nep = Counter(m for f in resp if f["ar_trece_cu_orice_modul"] for m in f["module_nepermise"])

    pe_prob = []
    for k, p in enumerate(proba):
        sup = [f["proba_atinse"][k] for f in noua if k in f["proba_atinse"]]
        pe_prob.append({"id": p["id"], "functii_suprapunere": len(sup), "cea_mai_lunga": max(sup, default=0),
                        "functii_solutie_exacta": sum(1 for f in noua if k in f["proba_exacte"])})
    scurgere_proba = {"probleme": len(proba),
                      "probleme_cu_suprapunere": sum(1 for x in pe_prob if x["functii_suprapunere"]),
                      "probleme_cu_solutia_exacta": sum(1 for x in pe_prob if x["functii_solutie_exacta"]),
                      "functii_atinse": sum(1 for f in noua if f["proba_atinse"] or f["proba_exacte"]),
                      "functii_atinse_chemabile": sum(1 for f in chem if f["proba_atinse"] or f["proba_exacte"]),
                      "pe_problema": [x for x in pe_prob if x["functii_suprapunere"] or x["functii_solutie_exacta"]]}
    scurgere_asc = {}
    for nume in ascunse:
        cu = [f for f in noua if nume in f["ascunse_exacte"]]
        scurgere_asc[nume] = {"probleme": n_ascunse[nume], "functii_cu_solutia_intreaga": len(cu),
                              "probleme_atinse": len({p for f in cu for p in f["ascunse_exacte"][nume]}),
                              "sha_neschimbat": sha_inainte[nume] == sha_dupa[nume]}
    scurte = [f for f in chem if 3 <= f["linii_corp"] <= 8]
    scurte.sort(key=lambda f: hashlib.sha256(f"{f['cale']}:{f['linia']}".encode()).hexdigest())
    alese = ([f for f in scurte if f["importuri"]][:2] + [f for f in scurte if not f["importuri"]])[:EXEMPLE_CURATA]
    exemple = [{"pachet": f["pachet"], "licenta": f["licenta"], "cale": f["cale"], "linia": f["linia"],
                "nume": f["nume"], "categorie": f["categorie"], "d": f["d"], "simboluri_corp": f["simboluri_corp"],
                "text": f.get("text_bland") or f["text"]} for f in alese]
    v = verdict_curata(_chem(noua)["chemabile"]["toate"]["simboluri_corp"])
    rez = {"sarcina": "S68", "secunde": round(time.time() - t0, 1), "definitii_s67": len(defin),
           "autonome_s67_din_tsv": n_auto_s67, "gasite": len(gasite), "negasite": len(fs) - len(gasite),
           "categorii": dict(cat.most_common()),
           "cutie_bland_stari": dict(Counter(f["cutie_bland"] for f in gasite if f["cutie_bland"]).most_common()),
           "cutie_bland_stari_candidati": dict(Counter(f["cutie_bland"] for f in cand).most_common()),
           "multimi": {"autonome S67": _chem(auto), "blânde (noi)": _chem(blande),
                       "autonome + blânde": _chem(noua),
                       "autonome + blânde, fără autonomele cu modul neimportat (strict, informativ)": _chem(stricta)},
           "chemabile_linii_corp": dict(lung), "chemabile_simboluri_corp": dict(simb),
           "primele_10_pachete_chemabile": [{"pachet": p, "functii": n, "simboluri_corp": simb_pachet[p]}
                                            for p, n in pe_pachet.most_common(10)],
           "licente_chemabile": dict(Counter(f["licenta"] for f in chem).most_common()),
           "informativ_respinse": {
               "respinse": _sume_bland(resp),
               "ar_trece_si_cu_from_M_import_x (M permis)": _sume_bland([f for f in resp if f["ar_trece_cu_from"]]),
               "ar_trece_daca_cutia_ar_permite_modulul (cutia NU se schimbă)": _sume_bland(
                   [f for f in resp if f["ar_trece_cu_orice_modul"]]),
               "modulele_nepermise_top20": mod_nep.most_common(20),
               "nume_ramase_top20": Counter(n for f in resp for n in f["rest"]).most_common(20)},
           "scurgere_proba": scurgere_proba, "scurgere_ascunse": scurgere_asc,
           "praguri": {"DESTUL PENTRU A": PRAG_A_DESTUL, "PUTIN": PRAG_A_PUTIN},
           "verdict (autonome + blânde) × chemabile": v, "exemple": exemple}
    with open(iesire / "blande.tsv", "w", encoding="utf-8", newline="\n") as fo:
        fo.write("i\tlinia\tsha256_normalizat\tcategorie\tchemabila\tchemabila_strict\td\tlinii_corp\tsimboluri_corp\t"
                 "importuri\tpachet\tcale\n")
        for f in noua:
            fo.write(f"{f['i']}\t{f['linia']}\t{f['sha']}\t{f['categorie']}\t{int(f['chemabila'])}\t"
                     f"{int(f['chemabila_strict'])}\t{int(f['d'])}\t{f['linii_corp']}\t{f['simboluri_corp']}\t"
                     f"{' | '.join(f['importuri'])}\t{f['pachet']}\t{f['cale']}\n")
    f_rez.write_text(json.dumps(rez, ensure_ascii=False, indent=1), encoding="utf-8")
    jurnal(json.dumps({"multimi": rez["multimi"]["autonome + blânde"], "verdict": v,
                       "scurgere_ascunse": scurgere_asc}, ensure_ascii=False))
    return rez


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="comanda", required=True)
    r = sub.add_parser("ruleaza", help="numărătoarea, o singură dată")
    r.add_argument("--procese", type=int, default=12)
    c = sub.add_parser("curata", help="S67: funcțiile autonome (cu reluare)")
    c.add_argument("--procese", type=int, default=12)
    c.add_argument("--fire", type=int, default=16)
    c.add_argument("--pana-la", default=None, help="HH:MM — oprire curată (se reia cu aceeași comandă)")
    b = sub.add_parser("bland", help="S68: regula blândă la importuri + chemabile (cu reluare)")
    b.add_argument("--procese", type=int, default=12)
    b.add_argument("--fire", type=int, default=16)
    b.add_argument("--pana-la", default=None, help="HH:MM — oprire curată (se reia cu aceeași comandă)")
    a = ap.parse_args(argv)
    j = lambda m: print(time.strftime("%H:%M:%S"), m, flush=True)  # noqa: E731
    if a.comanda == "bland":
        return 0 if bland(procese=a.procese, fire=a.fire, pana_la=a.pana_la, jurnal=j) is not None else 3
    if a.comanda == "curata":
        return 0 if curata(procese=a.procese, fire=a.fire, pana_la=a.pana_la, jurnal=j) is not None else 3
    ruleaza(procese=a.procese, jurnal=j)
    return 0


if __name__ == "__main__":
    sys.exit(main())
