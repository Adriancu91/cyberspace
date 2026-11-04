"""Kronos-Cod: școala de cod, pregătirea (S72a, 4 noiembrie 2026) — exercițiile CU TEST care rulează în cutie.

Pornește de la exercițiile de antrenare din S69 (`lucru/kronos_cod/exercitii/exercitii.tsv`) care au marcajul (d)
(un exemplu `>>>` în explicație sau un `assert` din testele pachetului) și NU sunt în pachetele ținute deoparte.
Pentru fiecare:
    enunțul   = importurile de sus (regula blândă S68, `blande.tsv`) + antetul funcției + explicația;
    referința = corpul original (cu indentarea lui, ca răspunsul unui model);
    testele   = exemplele `>>>` (cu rezultat → `assert repr(_v) == … or str(_v) == …`) sau asserturile din
                fișierele de test ale aceluiași pachet care cheamă funcția (doar funcții de bază și module permise).
S69 avea o scăpare la exemplele pe mai multe rânduri: un comentariu la coada exemplului intra în paranteza
`_v = (… # comentariu)`, iar rândurile de continuare scrise cu `>>>` (în loc de `...`) își pierdeau indentarea.
Aici: expresia se pune pe rândul ei în paranteză, iar exemplele care continuă un bloc deschis se lipesc de el.
Un test bun trebuie să cheme funcția cu argumente și să aibă cel puțin un `assert`.

Fiecare exercițiu rulează în cutie (`cutie.py`, neschimbată), exact cum îl va rula `examen_cod.py noteaza`
(`enunt + corp`, apoi testele); se păstrează doar cele la care corpul original trece. În plus (scris în raport),
se scot cele la care și corpul greșit `return None` trece (testul n-ar deosebi un răspuns bun de unul gol).
Scurgerea (S53/S69): se scoate orice exercițiu (enunț + corp + teste) cu suprapunere de 13 simboluri sau cu soluția
întreagă din setul de probă, `ascuns2` sau S58 `examen_ascuns`; pentru cele ascunse doar numărul, SHA verificat.

Împărțirea pe pachete întregi (sămânța 0): P_verif = cel puțin 200 de exerciții (exact 200 dacă se poate, din cât mai
multe pachete), P_scoala = restul. În `lucru/kronos_cod/scoala/` (nimic în Git):
    P_verif/, P_scoala/   probleme.jsonl + info.json (SHA-256), formatul citit de `examen_cod.py --set ascuns --dosar`
    exercitii_test.tsv    un rând pe exercițiu încercat: pachet, nume, tip, starea în cutie, motivul
    scoala.json           cifrele (refuză să ruleze dacă există)

Comanda:  python -X utf8 -m unelte.kronos_cod.scoala teste [--procese 12] [--fire 16]
          python -X utf8 -m unelte.kronos_cod.scoala verifica [--cate 5]

S75 (comanda `corecte`): încercările scrise de `examen_cod.py model` pe P_scoala trec prin cutie cu testul exercițiului;
se păstrează corpurile corecte, fără `return <valoare fixă>` (regula (b) S72b) și fără duplicate după spații.
          python -X utf8 -m unelte.kronos_cod.scoala corecte [--raspunsuri …] [--dosar …] [--iesire …]
"""

from __future__ import annotations

import argparse
import ast
import json
import random
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

from unelte.kronos_cod import functii as fu  # noqa: E402
from unelte.kronos_cod import scurgere  # noqa: E402
from unelte.kronos_cod._cutie_interior import verifica_arborele  # noqa: E402
from unelte.kronos_cod.tokenizer_cod import COD, EXCLUS, citeste_excluse, loturi, parte  # noqa: E402

EXERCITII = RADACINA / "lucru" / "kronos_cod" / "exercitii"
IESIRE = RADACINA / "lucru" / "kronos_cod" / "scoala"
P_VERIF_TINTA = 200
PACHET_MIC = 5
CORP_GRESIT = "    return None\n"
_OPTIUNE = re.compile(r"#\s*doctest:")


# ---------------------------------------------------------------------------------------------------- exemplele `>>>`

def _complet(src: str) -> bool:
    """Instrucțiunea se poate citi singură (nu e un bloc deschis, de exemplu `for x in y:` fără corp)."""
    try:
        ast.parse(textwrap.dedent(src))
        return True
    except (SyntaxError, ValueError):
        return False


def exemple_doctest(doc: str) -> tuple[list[str], int]:
    """Exemplele `>>>` ca instrucțiuni (S72a, cu scăparea din S69 reparată). Cele cu rezultat devin
    `_v = (\\n<expresie>\\n)` + `assert repr(_v) == … or str(_v) == …`; cele fără rezultat rămân instrucțiuni.
    Întoarce (instrucțiunile, câte exemple au fost sărite: eroare așteptată, opțiuni doctest, nu se pot transforma)."""
    import doctest

    try:
        exemple = doctest.DocTestParser().get_examples(doc)
    except ValueError:
        return [], 1
    grupe: list[list] = []  # [sursa, rezultatul, eroare?, opțiuni?]
    for ex in exemple:
        src = ex.source.rstrip("\n")
        if grupe and not grupe[-1][1] and grupe[-1][2] is None and (not _complet(grupe[-1][0]) or src[:1].isspace()):
            grupe[-1][0] += "\n" + src  # continuarea unui bloc scrisă cu `>>>` în loc de `...`
            grupe[-1][1], grupe[-1][2] = ex.want, ex.exc_msg
            grupe[-1][3] = grupe[-1][3] or bool(ex.options) or bool(_OPTIUNE.search(src))
            continue
        grupe.append([src, ex.want, ex.exc_msg, bool(ex.options) or bool(_OPTIUNE.search(src))])
    randuri, sarite = [], 0
    for src, want, exc, optiuni in grupe:
        src, want = textwrap.dedent(src).strip("\n"), want.strip()
        if exc is not None or optiuni:
            sarite += 1
            continue
        try:
            ast.parse(src)
        except (SyntaxError, ValueError):
            sarite += 1
            continue
        if not want:
            randuri.append(src)
            continue
        try:
            ast.parse(src, mode="eval")
        except SyntaxError:
            sarite += 1
            continue
        randuri.append(f"_v = (\n{src}\n)\nassert repr(_v) == {want!r} or str(_v) == {want!r}")
    return randuri, sarite


def cheama_cu_argumente(nume: str, teste: list[str]) -> bool:
    for t in teste:
        try:
            arbore = ast.parse(t)
        except SyntaxError:
            continue
        for n in ast.walk(arbore):
            if (isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == nume
                    and (n.args or n.keywords)):
                return True
    return False


def are_assert(teste: list[str]) -> bool:
    for t in teste:
        try:
            if any(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(t))):
                return True
        except SyntaxError:
            continue
    return False


# ---------------------------------------------------------------------------------------------------- enunțul și corpul

def imparte_functia(nod, linii: list[str]) -> tuple[str, str] | None:
    """(antetul + explicația, corpul) din textul funcției dedentat ca la S69; None dacă nu se poate tăia curat."""
    doc = ast.get_docstring(nod, clean=False)
    if doc is None or not doc.strip() or len(nod.body) < 2:
        return None
    sfarsit_doc, corp0 = nod.body[0].end_lineno, nod.body[1]
    if corp0.lineno <= sfarsit_doc:
        return None
    inceput = min([d.lineno for d in nod.decorator_list] + [nod.lineno])
    tot = textwrap.dedent("\n".join(linii[inceput - 1:nod.end_lineno])).split("\n")
    k = sfarsit_doc - inceput + 1
    enunt, corp = "\n".join(tot[:k]) + "\n", "\n".join(tot[k:]).strip("\n") + "\n"
    if not corp.strip() or any(r.strip() and not r[0].isspace() for r in corp.split("\n")):
        return None  # corpul are rânduri la marginea din stânga: `taie_corp` din examen l-ar tăia
    return enunt, corp


# ---------------------------------------------------------------------------------------------------- citirea (2 treceri)

_STARE: dict = {}


def _init(stare: dict) -> None:
    global _STARE
    _STARE = dict(stare)


def analizeaza_functii(i: int, r: dict, cerute: list[dict], importuri: dict) -> list[dict]:
    try:
        arbore = ast.parse(r["text"])
    except (SyntaxError, ValueError, RecursionError, MemoryError):
        return [dict(f, i=i, motiv="negasita") for f in cerute]
    linii = r["text"].splitlines()
    pe_linie = {n.lineno: n for n in fu.functiile(arbore)}
    out = []
    for f in cerute:
        f = dict(f, i=i)
        nod = pe_linie.get(f["linia"])
        try:
            if nod is None or fu.descrie(nod, linii)["sha"] != f["sha"]:
                out.append(dict(f, motiv="negasita"))
                continue
            f["nume"] = nod.name
            bucati = imparte_functia(nod, linii)
            if bucati is None:
                out.append(dict(f, motiv="corp_netaiat"))
                continue
            imp = importuri.get(f["sha"])
            enunt, corp = bucati
            f["enunt"] = ("\n".join(imp) + "\n\n\n" + enunt) if imp else enunt
            f["corp"] = corp
            doc = ast.get_docstring(nod) or ""
            f["exemple"], f["exemple_sarite"] = exemple_doctest(doc) if ">>>" in doc else ([], 0)
            f["motiv"] = ""
        except RecursionError:
            f = dict(f, motiv="negasita")
        out.append(f)
    return out


def _lot_functii(lot) -> list[dict]:
    start, randuri = lot
    out = []
    for j, rand in enumerate(randuri):
        cerute = _STARE["cerute"].get(start + j)
        if cerute:
            out.extend(analizeaza_functii(start + j, json.loads(rand), cerute, _STARE["importuri"]))
    return out


def _lot_asserturi(lot) -> dict:
    """Asserturile din fișierele de test (antrenare/eșantion) ale pachetelor cerute, doar cele care pomenesc
    unul din numele căutate în pachetul lor."""
    start, randuri = lot
    out: dict[str, list] = {}
    for j, rand in enumerate(randuri):
        r = json.loads(rand)
        cheie = f"{r.get('sursa', '?')}:{r.get('pachet', '?')}"
        nume = _STARE["nume_pe_pachet"].get(cheie)
        if (not nume or r.get("limbaj") != "python" or not fu.e_fisier_de_test(r.get("cale", ""))
                or parte(start + j, r["text"], _STARE["aproape"], _STARE["scurgere"]) not in ("antrenare", "esantion")):
            continue
        try:
            a = fu.asserturi_fisier(ast.parse(r["text"]))
        except (SyntaxError, ValueError, RecursionError, MemoryError):
            continue
        a = [x for x in a if x[0] & nume]
        if a:
            out.setdefault(cheie, []).extend(a)
    return out


def citeste_cerute(f_tsv: Path) -> dict[int, list[dict]]:
    """Din exercitii.tsv (S69): exercițiile de antrenare (deoparte = 0) cu (d) = 1, grupate pe fișier."""
    pe_fisier: dict[int, list[dict]] = {}
    with open(f_tsv, encoding="utf-8") as f:
        cap = f.readline().rstrip("\n").split("\t")
        for rand in f:
            r = dict(zip(cap, rand.rstrip("\n").split("\t")))
            if r["d"] != "1" or r["deoparte"] != "0":
                continue
            pe_fisier.setdefault(int(r["i"]), []).append(
                {"linia": int(r["linia"]), "sha": r["sha256_normalizat"], "autonoma": r["autonoma"] == "1",
                 "pachet": r["pachet"], "cale": r["cale"]})
    return pe_fisier


# ---------------------------------------------------------------------------------------------------- cutia și motivele

def motiv_cadere(stare: str, mesaj: str) -> str:
    if stare == "ok":
        return "ok"
    if stare == "interzis":
        if mesaj.startswith("sintaxă"):
            return "sintaxa"
        return "import_nepermis" if "import" in mesaj else "interzis_altceva"
    if stare == "blocat":
        return "import_nepermis" if "import" in mesaj or not mesaj else "blocat_altceva"
    if stare in ("timp", "memorie", "cazut"):
        return stare
    tip = mesaj.split(":", 1)[0].strip()
    if tip == "AssertionError":
        return "rezultat_gresit"
    if tip in ("NameError", "ImportError", "ModuleNotFoundError", "AttributeError", "TypeError"):
        return tip
    return f"{stare}_altceva"


def ruleaza_in_cutie(enunt: str, corp: str, teste: list[str]) -> dict:
    from unelte.kronos_cod import cutie

    r = cutie.ruleaza(enunt + corp, teste)  # aceleași limite implicite ca `examen_cod.noteaza`
    return {"stare": r.stare, "trecut": r.trecut, "mesaj": (r.mesaj or "; ".join(r.blocate))[:200]}


# ---------------------------------------------------------------------------------------------------- împărțirea

def imparte(pe_pachet: dict[str, int], tinta: int = P_VERIF_TINTA, samanta: int = 0,
            mic: int = PACHET_MIC) -> set[str]:
    """Pachetele din P_verif: amestecate cu sămânța; întâi cele mici (≤ `mic` exerciții), cât încap fără să treacă
    de țintă, apoi oricare încape; dacă tot nu e ținta, cel mai mic pachet care o depășește."""
    ordine = sorted(pe_pachet)
    random.Random(samanta).shuffle(ordine)
    ales, n = [], 0
    for doar_mici in (True, False):
        for p in ordine:
            if p in ales or (doar_mici and pe_pachet[p] > mic):
                continue
            if n + pe_pachet[p] <= tinta:
                ales.append(p)
                n += pe_pachet[p]
            if n == tinta:
                return set(ales)
    rest = [p for p in ordine if p not in ales]
    if rest and n < tinta:
        ales.append(min(rest, key=lambda p: (pe_pachet[p], ordine.index(p))))
    return set(ales)


def scrie_dosar(dosar: Path, exercitii: list[dict], prefix: str) -> dict:
    from unelte.kronos_cod.examen_cod import Problema, scrie_jsonl

    dosar.mkdir(parents=True, exist_ok=True)
    probleme = [Problema(id=f"{prefix}{k:05d}", sablon=f["pachet"], varianta=f["sha"], functie=f["nume"],
                         enunt=f["enunt"], referinta=f["corp"], teste=f["teste"]) for k, f in enumerate(exercitii)]
    sha = scrie_jsonl(probleme, dosar / "probleme.jsonl")
    info = {"probleme": len(probleme), "pachete": len({f["pachet"] for f in exercitii}),
            "autonome": sum(f["autonoma"] for f in exercitii), "sha256": sha, "sarcina": "S72a"}
    (dosar / "info.json").write_text(json.dumps(info, indent=1, ensure_ascii=False), encoding="utf-8")
    return info


# ---------------------------------------------------------------------------------------------------- comanda `teste`

def teste(cod: Path = COD, exercitii_dir: Path = EXERCITII, functii_dir: Path = fu.IESIRE, iesire: Path = IESIRE,
          exclus: Path = EXCLUS, ascunse: dict | None = None, probleme_proba: list[dict] | None = None,
          procese: int = 12, fire: int = 16, cutia=ruleaza_in_cutie, tinta: int = P_VERIF_TINTA,
          jurnal=print) -> dict:
    from concurrent.futures import ThreadPoolExecutor

    cod, iesire = Path(cod), Path(iesire)
    f_rez = iesire / "scoala.json"
    if f_rez.exists():
        raise SystemExit(f"{f_rez} există deja: setul școlii se face o singură dată")
    t0 = time.time()
    ascunse = fu.ASCUNSE if ascunse is None else ascunse
    proba = probleme_proba if probleme_proba is not None else fu._probleme_proba()
    idx_proba = scurgere.indexeaza(proba)
    idx_ascunse, sha_inainte, n_ascunse = {}, {}, {}
    for nume, dosar in ascunse.items():
        probleme, sha_inainte[nume] = fu._probleme_ascunse(Path(dosar))
        idx_ascunse[nume] = scurgere.indexeaza(probleme)
        n_ascunse[nume] = len(probleme)
        del probleme
    cerute = citeste_cerute(Path(exercitii_dir) / "exercitii.tsv")
    n_cerute = sum(len(v) for v in cerute.values())
    importuri = {s: v for s, v in fu.citeste_blande(Path(functii_dir) / "blande.tsv").items() if v}
    aproape, scurg = citeste_excluse(cod, Path(exclus))
    jurnal(f"exerciții de antrenare cu (d): {n_cerute}, în {len(cerute)} fișiere")

    stare = {"cerute": cerute, "importuri": importuri}
    fs: list[dict] = []
    with Pool(procese, initializer=_init, initargs=(stare,)) as pool:
        for r in pool.imap(_lot_functii, loturi(cod / "cod.jsonl"), chunksize=1):
            fs.extend(r)
    jurnal(f"trecerea 1 (funcțiile) gata: {len(fs)}, {time.time() - t0:.0f} s")

    nume_pe_pachet: dict[str, set] = {}
    for f in fs:
        if not f["motiv"] and not f["exemple"]:
            nume_pe_pachet.setdefault(f["pachet"], set()).add(f["nume"])
    stare = {"nume_pe_pachet": nume_pe_pachet, "aproape": aproape, "scurgere": scurg}
    asserturi: dict[str, list] = {}
    with Pool(procese, initializer=_init, initargs=(stare,)) as pool:
        for r in pool.imap(_lot_asserturi, loturi(cod / "cod.jsonl"), chunksize=1):
            for c, v in r.items():
                asserturi.setdefault(c, []).extend(v)
    jurnal(f"trecerea 2 (asserturile) gata: {sum(len(v) for v in asserturi.values())} în {len(asserturi)} pachete, "
           f"{time.time() - t0:.0f} s")

    # testele fiecărui exercițiu
    exemple_sarite = 0
    for f in fs:
        if f["motiv"]:
            continue
        exemple_sarite += f.get("exemple_sarite", 0)
        if f["exemple"]:
            f["tip"], f["teste"] = "doctest", f["exemple"]
        else:
            f["tip"], f["teste"] = "assert", fu.asserturi_pentru(f["nume"], asserturi.get(f["pachet"], []))
        if not f["teste"]:
            f["motiv"] = "fara_test"
        elif not cheama_cu_argumente(f["nume"], f["teste"]):
            f["motiv"] = "test_fara_apel_cu_argumente"
        elif not are_assert(f["teste"]):
            f["motiv"] = "test_fara_assert"
        elif any(verifica_arborele(t, fu._PERMISE) for t in f["teste"]):
            f["motiv"] = "test_interzis"
    # scurgerea: pe tot exercițiul (enunț + corp + teste)
    for f in fs:
        if f["motiv"]:
            continue
        text = f["enunt"] + f["corp"] + "\n" + "\n".join(f["teste"]) + "\n"
        g = scurgere.scaneaza_text(text, idx_proba)
        f["scurgere"] = {}
        if g and (g["atinse"] or g["exacte"]):
            f["scurgere"]["proba"] = {"atinse": bool(g["atinse"]), "exacte": bool(g["exacte"])}
        for nume, idx in idx_ascunse.items():
            g = scurgere.scaneaza_text(text, idx)
            if g and (g["atinse"] or g["exacte"]):
                f["scurgere"][nume] = {"atinse": bool(g["atinse"]), "exacte": bool(g["exacte"])}
        if f["scurgere"]:
            f["motiv"] = "scurgere"
    sha_dupa = {nume: scurgere.sha256_fisier(Path(d) / "probleme.jsonl") for nume, d in ascunse.items()}

    de_rulat = [f for f in fs if not f["motiv"]]
    jurnal(f"în cutie: {len(de_rulat)} exerciții (corpul original), {time.time() - t0:.0f} s")
    with ThreadPoolExecutor(fire) as ex:
        rez_orig = list(ex.map(lambda f: cutia(f["enunt"], f["corp"], f["teste"]), de_rulat))
    trec = []
    for f, rc in zip(de_rulat, rez_orig):
        f["cutie"] = rc
        if rc["trecut"]:
            trec.append(f)
        else:
            f["motiv"] = motiv_cadere(rc["stare"], rc["mesaj"])
    jurnal(f"corpul original trece: {len(trec)}; cu `return None`: {time.time() - t0:.0f} s")
    with ThreadPoolExecutor(fire) as ex:
        rez_gresit = list(ex.map(lambda f: cutia(f["enunt"], CORP_GRESIT, f["teste"]), trec))
    bune = []
    for f, rc in zip(trec, rez_gresit):
        if rc["trecut"]:
            f["motiv"] = "trece_si_return_none"
        else:
            bune.append(f)
    # duplicatele exacte (după sumă) și împărțirea
    vazute, unice = set(), []
    for f in bune:
        if f["sha"] in vazute:
            f["motiv"] = "duplicat"
            continue
        vazute.add(f["sha"])
        unice.append(f)
    pe_pachet = Counter(f["pachet"] for f in unice)
    verif_p = imparte(dict(pe_pachet), tinta)
    p_verif = [f for f in unice if f["pachet"] in verif_p]
    p_scoala = [f for f in unice if f["pachet"] not in verif_p]
    iesire.mkdir(parents=True, exist_ok=True)
    info_v = scrie_dosar(iesire / "P_verif", p_verif, "v")
    info_s = scrie_dosar(iesire / "P_scoala", p_scoala, "s")
    with open(iesire / "exercitii_test.tsv", "w", encoding="utf-8", newline="\n") as fo:
        fo.write("i\tlinia\tsha256_normalizat\tautonoma\tpachet\tnume\ttip\tteste\tstare_cutie\tmotiv\tparte\n")
        id_unice = {id(f) for f in unice}
        for f in fs:
            parte_ = ("P_verif" if f["pachet"] in verif_p else "P_scoala") if id(f) in id_unice else ""
            fo.write(f"{f['i']}\t{f['linia']}\t{f['sha']}\t{int(f['autonoma'])}\t{f['pachet']}\t{f.get('nume', '')}\t"
                     f"{f.get('tip', '')}\t{len(f.get('teste') or [])}\t{f.get('cutie', {}).get('stare', '')}\t"
                     f"{f['motiv'] or 'bun'}\t{parte_}\n")

    def pe_tip(xs):
        return dict(Counter(f.get("tip", "?") for f in xs).most_common())

    incercate = [f for f in fs if f.get("tip")]
    rez = {
        "sarcina": "S72a", "secunde": round(time.time() - t0, 1), "cerute": n_cerute,
        "motive_toate": dict(Counter(f["motiv"] or "bun" for f in fs).most_common()),
        "inainte_de_cutie": {"cu_test": len(incercate) - sum(f["motiv"] in ("fara_test", "test_fara_apel_cu_argumente",
                                                                           "test_fara_assert", "test_interzis")
                                                             for f in incercate),
                             "pe_tip": pe_tip(incercate), "exemple_doctest_sarite": exemple_sarite},
        "cutie_corp_original": {"rulate": len(de_rulat), "trec": len(trec), "pe_tip_trec": pe_tip(trec),
                                "stari": dict(Counter(r["stare"] for r in rez_orig).most_common()),
                                "caderi_pe_motiv": dict(Counter(motiv_cadere(r["stare"], r["mesaj"])
                                                                for r in rez_orig if not r["trecut"]).most_common())},
        "trec_si_cu_return_none": len(trec) - len(bune),
        "duplicate_scoase": len(bune) - len(unice),
        "exercitii_cu_test_bune": {"total": len(unice), "autonome": sum(f["autonoma"] for f in unice),
                                   "pachete": len(pe_pachet), "pe_tip": pe_tip(unice)},
        "scurgere": {"proba_scoase": sum(1 for f in fs if "proba" in (f.get("scurgere") or {})),
                     "ascunse": {nume: {"atinse_13": sum(1 for f in fs if (f.get("scurgere") or {}).get(nume, {}).get("atinse")),
                                        "solutia_intreaga": sum(1 for f in fs if (f.get("scurgere") or {}).get(nume, {}).get("exacte")),
                                        "probleme": n_ascunse[nume], "sha_neschimbat": sha_inainte[nume] == sha_dupa[nume]}
                                 for nume in ascunse}},
        "P_verif": info_v, "P_scoala": info_s, "samanta": 0, "tinta_P_verif": tinta,
    }
    f_rez.write_text(json.dumps(rez, ensure_ascii=False, indent=1), encoding="utf-8")
    jurnal(json.dumps({k: rez[k] for k in ("exercitii_cu_test_bune", "P_verif", "P_scoala", "scurgere")},
                      ensure_ascii=False))
    return rez


# ---------------------------------------------------------------------------------------------------- comanda `verifica`

def verifica(iesire: Path = IESIRE, cate: int = 5) -> dict:
    """Pe primele `cate` exerciții din P_verif: `examen_cod.py noteaza` dă „ok” pentru corpul original și „picat”
    pentru un corp greșit. Scrie răspunsurile și notele în `iesire/verificare/` (refuză dacă există)."""
    from unelte.kronos_cod import examen_cod

    dosar = Path(iesire) / "P_verif"
    v = Path(iesire) / "verificare"
    if v.exists():
        raise SystemExit(f"{v} există deja")
    v.mkdir(parents=True)
    probleme = examen_cod.probleme_setului("ascuns", dosar)[:cate]
    rez = {}
    for eticheta, corp in (("original", None), ("gresit", CORP_GRESIT)):
        raspunsuri = {p.id: [p.referinta if corp is None else corp] for p in probleme}
        f_r, f_n = v / f"raspunsuri_{eticheta}.json", v / f"nota_{eticheta}.json"
        f_r.write_text(json.dumps({"meta": {"set": "ascuns", "n": 1}, "raspunsuri": raspunsuri}, ensure_ascii=False),
                       encoding="utf-8")
        examen_cod.main(["noteaza", "--raspunsuri", str(f_r), "--nota", str(f_n), "--dosar", str(dosar)])
        nota = json.loads(f_n.read_text(encoding="utf-8"))
        rez[eticheta] = {"stari": nota["stari"], "pass@1": nota["pass@1"],
                         "corecte": [x["c"] for x in nota["pe_problema"]]}
    rez["probleme"] = [p.id for p in probleme]
    rez["bun"] = (rez["original"]["corecte"] == [1] * len(probleme) and rez["gresit"]["corecte"] == [0] * len(probleme))
    (v / "verificare.json").write_text(json.dumps(rez, ensure_ascii=False, indent=1), encoding="utf-8")
    return rez


# ---------------------------------------------------------------------------------------------------- comanda `corecte` (S75)

PACHETE_MARI = ("pypi:fluids", "pypi:chemicals")


def dupa_spatii(corp: str) -> str:
    """Forma „după spații” (S75): toate spațiile, tab-urile și rândurile goale strânse într-un singur spațiu."""
    return " ".join(corp.split())


def _doar_constante(nod) -> bool:
    if isinstance(nod, ast.Constant):
        return True
    if isinstance(nod, ast.UnaryOp) and isinstance(nod.op, (ast.USub, ast.UAdd)):
        return _doar_constante(nod.operand)
    if isinstance(nod, (ast.List, ast.Tuple, ast.Set)):
        return all(_doar_constante(x) for x in nod.elts)
    if isinstance(nod, ast.Dict):
        return all(k is not None and _doar_constante(k) for k in nod.keys) and all(_doar_constante(v) for v in nod.values)
    return False


def e_return_fix(corp: str) -> bool:
    """Regula (b) din nota S72b: corpul e doar `return <valoare fixă>` — un singur rând de cod, în arbore un `Return`
    cu o constantă sau o listă/tuplă/mulțime/dicționar doar de constante (și `-constantă`)."""
    randuri = [r for r in corp.splitlines() if r.strip() and not r.strip().startswith("#")]
    if len(randuri) != 1:
        return False
    try:
        arbore = ast.parse(textwrap.dedent(randuri[0]))
    except (SyntaxError, ValueError):
        return False
    if len(arbore.body) != 1 or not isinstance(arbore.body[0], ast.Return):
        return False
    v = arbore.body[0].value
    return v is not None and _doar_constante(v)


def corecte(raspunsuri: Path, dosar: Path, iesire: Path, fire: int = 16, cutia=ruleaza_in_cutie,
            control: bool = True, jurnal=print) -> dict:
    """Fiecare încercare din `raspunsuri` (scrise de `examen_cod.py model`) rulează în cutie cu testul exercițiului ei,
    exact ca `examen_cod.py noteaza`. Scrie `iesire/corecte.jsonl` (corpurile corecte păstrate: fără `return <valoare
    fixă>`, fără duplicate după spații în același exercițiu) și `iesire/numaratoare.json` (refuză dacă există).
    `control`: rulează și `examen_cod.py noteaza` pe aceleași răspunsuri (`iesire/nota_control.json`)."""
    from concurrent.futures import ThreadPoolExecutor

    from unelte.kronos_cod import examen_cod

    iesire = Path(iesire)
    f_num, f_cor = iesire / "numaratoare.json", iesire / "corecte.jsonl"
    if f_num.exists():
        raise SystemExit(f"{f_num} există deja: numărătoarea se face o singură dată")
    t0 = time.time()
    date = json.loads(Path(raspunsuri).read_text(encoding="utf-8"))
    probleme = {p.id: p for p in examen_cod.probleme_setului("ascuns", Path(dosar))}
    lipsa = [i for i in date["raspunsuri"] if i not in probleme]
    if lipsa:
        raise SystemExit(f"{len(lipsa)} exerciții din răspunsuri nu sunt în {dosar} (de ex. {lipsa[0]})")
    sarcini = [(probleme[i], j, corp) for i, corpuri in date["raspunsuri"].items() for j, corp in enumerate(corpuri)]
    jurnal(f"încercări: {len(sarcini)} la {len(date['raspunsuri'])} exerciții")
    with ThreadPoolExecutor(fire) as ex:
        rez = list(ex.map(lambda s: cutia(s[0].enunt, s[2], s[0].teste), sarcini))
    jurnal(f"cutia gata: {time.time() - t0:.0f} s")
    ok = [(p, j, corp) for (p, j, corp), r in zip(sarcini, rez) if r["trecut"]]
    fixe = [(p, j, corp) for p, j, corp in ok if e_return_fix(corp)]
    pastrate, vazute, dubluri = [], set(), 0
    for p, j, corp in ok:
        if e_return_fix(corp):
            continue
        cheie = (p.id, dupa_spatii(corp))
        if cheie in vazute:
            dubluri += 1
            continue
        vazute.add(cheie)
        pastrate.append({"id": p.id, "pachet": p.sablon, "functie": p.functie, "incercarea": j, "enunt": p.enunt,
                         "corp": corp, "copiat": dupa_spatii(corp) == dupa_spatii(p.referinta)})
    iesire.mkdir(parents=True, exist_ok=True)
    with open(f_cor, "w", encoding="utf-8", newline="\n") as fo:
        for x in pastrate:
            fo.write(json.dumps(x, ensure_ascii=False) + "\n")
    pe_pachet = Counter(x["pachet"] for x in pastrate)
    num = {
        "sarcina": "S75", "raspunsuri": str(raspunsuri), "dosar": str(dosar), "meta_raspunsuri": date["meta"],
        "exercitii": len(date["raspunsuri"]), "incercari": len(sarcini),
        "stari": dict(Counter(r["stare"] for r in rez).most_common()),
        "caderi_pe_motiv": dict(Counter(motiv_cadere(r["stare"], r["mesaj"]) for r in rez if not r["trecut"]).most_common()),
        "corecte_toate": len(ok), "exercitii_cu_corecte_toate": len({p.id for p, _, _ in ok}),
        "scoase_return_fix": len(fixe), "exercitii_doar_cu_return_fix":
            len({p.id for p, _, _ in fixe} - {x["id"] for x in pastrate}),
        "duplicate_dupa_spatii_scoase": dubluri,
        "corpuri_corecte_diferite": len(pastrate), "exercitii_cu_corpuri_pastrate": len({x["id"] for x in pastrate}),
        "identice_cu_originalul": sum(x["copiat"] for x in pastrate),
        "exercitii_cu_copiat": len({x["id"] for x in pastrate if x["copiat"]}),
        "din_pachetele_mari": {n: {"corpuri": pe_pachet.get(n, 0),
                                   "exercitii": len({x["id"] for x in pastrate if x["pachet"] == n})}
                               for n in PACHETE_MARI},
        "pachete_cu_corpuri": len(pe_pachet), "pe_pachet_primele": dict(pe_pachet.most_common(10)),
        "prag_destule": 100,
    }
    num["verdict"] = "DESTULE" if num["corpuri_corecte_diferite"] >= 100 else "PREA PUȚINE"
    if control:
        f_nota = iesire / "nota_control.json"
        examen_cod.main(["noteaza", "--raspunsuri", str(raspunsuri), "--nota", str(f_nota), "--dosar", str(dosar)])
        nota = json.loads(f_nota.read_text(encoding="utf-8"))
        ok_control = sum(x["c"] for x in nota["pe_problema"])
        num["control_noteaza"] = {"ok": ok_control, "stari": nota["stari"], "pass@1": nota["pass@1"],
                                  "la_fel": ok_control == len(ok),
                                  "exercitii_cu_ok": sum(1 for x in nota["pe_problema"] if x["c"])}
    num["secunde"] = round(time.time() - t0, 1)
    f_num.write_text(json.dumps(num, ensure_ascii=False, indent=1), encoding="utf-8")
    return num


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="comanda", required=True)
    t = sub.add_parser("teste", help="S72a: exercițiile cu test bune + P_verif / P_scoala (o singură dată)")
    t.add_argument("--procese", type=int, default=12)
    t.add_argument("--fire", type=int, default=16)
    v = sub.add_parser("verifica", help="S72a: examen_cod noteaza pe câteva exerciții din P_verif")
    v.add_argument("--cate", type=int, default=5)
    c = sub.add_parser("corecte", help="S75: cutia verifică încercările modelului; păstrează corpurile corecte")
    c.add_argument("--raspunsuri", type=Path, default=IESIRE / "runda1" / "raspunsuri.jsonl")
    c.add_argument("--dosar", type=Path, default=IESIRE / "P_scoala")
    c.add_argument("--iesire", type=Path, default=IESIRE / "runda1")
    c.add_argument("--fire", type=int, default=16)
    a = ap.parse_args(argv)
    j = lambda m: print(time.strftime("%H:%M:%S"), m, flush=True)  # noqa: E731
    if a.comanda == "teste":
        teste(procese=a.procese, fire=a.fire, jurnal=j)
        return 0
    if a.comanda == "corecte":
        r = corecte(a.raspunsuri, a.dosar, a.iesire, fire=a.fire, jurnal=j)
        print(json.dumps(r, ensure_ascii=False, indent=1))
        return 0
    r = verifica(cate=a.cate)
    print(json.dumps(r, ensure_ascii=False, indent=1))
    return 0 if r["bun"] else 1


if __name__ == "__main__":
    sys.exit(main())
