"""Numărătoarea funcțiilor scurte cu explicație (S65): pe fișiere mici făcute aici, FĂRĂ rețea și fără datele reale."""

import ast
import hashlib
import json

import pytest

from module.tokenizer_bpe import antreneaza_din_frecvente, frecvente_bucati
from unelte.kronos_cod import functii as fu
from unelte.kronos_cod.tokenizer_cod import PRAG_VALIDARE, SPECIALE

CU_DOC = '''import math


def aria(r):
    """Aria cercului de rază r.

    >>> round(aria(1), 2)
    3.14
    """
    return math.pi * r * r


def fara_doc(x):
    return x


def interzisa(p):
    """Citește un fișier (os nu e voie în cutie)."""
    import os
    return os.listdir(p)


def doar_doc():
    """Nimic altceva."""


class C:
    def metoda(self, x):
        """Dublul lui x."""
        return 2 * x

    def ascunsa(self):
        """Folosește un atribut cu _."""
        return self._x


def lunga(x):
    """Prea lungă."""
''' + "".join(f"    x = x + {k}\n" for k in range(31)) + "    return x\n"

TEST = "from pachet import metoda\n\n\ndef test_m():\n    assert C().metoda(2) == 4\n"
PROBA = [{"id": "p01", "sablon": "p01", "functie": "inverseaza",
          "enunt": 'def inverseaza(s):\n    """Return the string backwards."""\n',
          "referinta": "    return s[::-1]\n", "teste": ["assert inverseaza('ab') == 'ba'"]}]


def _gaseste(text):
    arbore = ast.parse(text)
    linii = text.splitlines()
    return {n.name: fu.descrie(n, linii) for n in fu.functiile(arbore)}


def test_marcajele_a_b_c_si_doctestul():
    d = _gaseste(CU_DOC)
    assert set(d) == {"aria", "fara_doc", "interzisa", "doar_doc", "metoda", "ascunsa", "lunga"}
    assert d["aria"]["a"] and d["aria"]["b"] and d["aria"]["c"] and d["aria"]["doctest"]
    assert not d["fara_doc"]["a"] and not d["fara_doc"]["b"]
    assert d["interzisa"]["b"] and not d["interzisa"]["c"]
    assert d["doar_doc"]["a"] and d["doar_doc"]["linii_corp"] == 0 and not d["doar_doc"]["b"]
    assert d["metoda"]["c"] and not d["metoda"]["doctest"]
    assert d["ascunsa"]["b"] and not d["ascunsa"]["c"]
    assert d["lunga"]["linii_corp"] == 32 and not d["lunga"]["b"]


def test_normalizarea_ignora_comentariile_si_spatiile():
    a = _gaseste('def f(x):\n    """D."""\n    return x+1  # unu\n')["f"]["sha"]
    b = _gaseste('def f(x):\n    """D."""\n\n    return   x + 1\n')["f"]["sha"]
    assert a == b


def test_fisierele_de_test_si_numele_din_assert():
    assert fu.e_fisier_de_test("p-1.0/tests/x.py") and fu.e_fisier_de_test("p/test_a.py")
    assert fu.e_fisier_de_test("p/a_test.py") and not fu.e_fisier_de_test("p/contest.py")
    a, u = fu.nume_din_assert(ast.parse("assert f(1) == g.h(2)\nself.assertEqual(k(1), 2)\n"))
    assert {"f", "g", "h"} <= a and "k" not in a and "k" in u


def test_verdictul_dupa_praguri():
    assert fu.verdict(20_000_000) == "DESTUL"
    assert fu.verdict(4_999_999) == "PUȚIN"
    assert fu.verdict(5_000_000) == "ÎNTRE"


def _antrenare(text):
    """Textul cu un comentariu la coadă care îl scoate din validare (prima cifră a sumei ≥ PRAG_VALIDARE)."""
    for k in range(1000):
        t = text + f"# {k}\n"
        if hashlib.sha256(t.encode("utf-8")).digest()[0] >= PRAG_VALIDARE:
            return t
    raise AssertionError


@pytest.fixture
def date(tmp_path):
    cod = tmp_path / "cod"
    cod.mkdir()
    sol = 'def invers(s):\n    """Inversul."""\n    return s[::-1]\n'
    randuri = [
        {"sursa": "pypi", "pachet": "pachet", "limbaj": "python", "licenta": "MIT", "cale": "pachet/a.py",
         "text": _antrenare(CU_DOC)},
        {"sursa": "pypi", "pachet": "pachet", "limbaj": "python", "licenta": "MIT", "cale": "pachet/tests/test_a.py",
         "text": _antrenare(TEST)},
        {"sursa": "pypi", "pachet": "altul", "limbaj": "python", "licenta": "MIT", "cale": "altul/b.py",
         "text": _antrenare(sol)},
        {"sursa": "pypi", "pachet": "altul", "limbaj": "python", "licenta": "MIT", "cale": "altul/c.py",
         "text": _antrenare(sol)},  # aproape-duplicat: nu intră
        {"sursa": "crates", "pachet": "r", "limbaj": "rust", "licenta": "MIT", "cale": "r/lib.rs",
         "text": _antrenare("fn main() {}\n")},
    ]
    (cod / "cod.jsonl").write_text("".join(json.dumps(r) + "\n" for r in randuri), encoding="utf-8")
    (cod / "aproape_duplicate.json").write_text("[3]", encoding="utf-8")
    exclus = tmp_path / "exclus.txt"
    exclus.write_text("", encoding="utf-8")
    fr = frecvente_bucati(CU_DOC + TEST + sol, (), "cod")
    tok = antreneaza_din_frecvente(dict(fr), 300, SPECIALE, "cod")
    cale_tok = tmp_path / "tok.json"
    tok.salveaza(cale_tok, {})
    return cod, exclus, cale_tok


def test_rularea_cap_coada_si_refuzul_a_doua_oara(tmp_path, date):
    cod, exclus, cale_tok = date
    iesire = tmp_path / "iesire"
    rez = fu.ruleaza(cod, exclus, iesire, cale_tok, ascunse={}, probleme_proba=PROBA, procese=2,
                     jurnal=lambda m: None)
    assert rez["fisiere"] == 4 and rez["python"] == 3 and rez["fisiere_test"] == 1
    n = rez["niveluri"]
    # a: aria, interzisa, doar_doc, metoda, ascunsa, lunga, invers = 7
    assert n["a"]["functii"] == 7
    assert n["a+b"]["functii"] == 5 and n["a+b+c"]["functii"] == 3  # aria, metoda, invers
    assert n["a+b+c+d"]["functii"] == 2  # aria (>>>) și metoda (assert în tests/ din același pachet)
    assert n["a+b+c"]["simboluri"] > 0 and rez["verdict"] == "PUȚIN"
    assert rez["scurgere_proba"]["probleme_cu_solutia_exacta"] == 1
    assert rez["scurgere_proba"]["functii_atinse"] == 1
    assert (iesire / "functii.tsv").read_text(encoding="utf-8").count("\n") == 8
    with pytest.raises(SystemExit):
        fu.ruleaza(cod, exclus, iesire, cale_tok, ascunse={}, probleme_proba=PROBA, procese=1,
                   jurnal=lambda m: None)


def test_seturile_ascunse_dau_doar_numere(tmp_path, date, monkeypatch):
    cod, exclus, cale_tok = date
    dosar = tmp_path / "ascuns"
    dosar.mkdir()
    (dosar / "probleme.jsonl").write_text("x", encoding="utf-8")
    monkeypatch.setattr(fu, "_probleme_ascunse", lambda d: (PROBA, "sha"))
    monkeypatch.setattr(fu.scurgere, "sha256_fisier",
                        lambda c: "sha" if str(c).endswith("probleme.jsonl") else "t")
    rez = fu.ruleaza(cod, exclus, tmp_path / "ies", cale_tok, ascunse={"x": dosar}, probleme_proba=PROBA,
                     procese=1, jurnal=lambda m: None)
    s = rez["scurgere_ascunse"]["x"]
    assert s == {"probleme": 1, "functii_cu_solutia_intreaga": 1, "probleme_atinse": 1, "sha_neschimbat": True}


# ---------------------------------------------------------------- S67: comanda `curata` (funcțiile autonome)

AUTONOME = '''import math


def suma_patrate(xs):
    """Suma pătratelor."""
    total = 0
    for x in xs:
        total += x * x
    return total


def cu_math(r):
    """Folosește math fără import (modul permis)."""
    return math.sqrt(r) + 1


def foloseste_global(x):
    """Cere un nume din restul fișierului."""
    return AJUTOR(x) + 1


def doar_pass(self):
    """Trivială."""
    pass


def doar_return(self):
    """Trivială."""
    return self


def doar_super(self, x):
    """Trivială."""
    return super().f(x)


def adnotata(x: Necunoscut) -> int:
    """Adnotarea cere un nume din afară: definiția pică în cutie."""
    y = x + 1
    return y


def cu_global(x):
    """global = nume liber."""
    global CONTOR
    CONTOR = x
    return x + 1
'''


def _arbore(text):
    arbore = ast.parse(text)
    return {n.name: n for n in fu.functiile(arbore)}, text.splitlines()


def test_corpul_triviale_si_numele_libere():
    n, linii = _arbore(AUTONOME)
    assert fu.text_corp(n["suma_patrate"], linii).startswith("total = 0\nfor x in xs:\n")
    assert '"""' not in fu.text_corp(n["suma_patrate"], linii)
    assert {k for k in n if fu.e_triviala(n[k])} == {"doar_pass", "doar_return", "doar_super"}
    assert fu.nume_libere(n["suma_patrate"]) == set()
    assert fu.nume_libere(n["cu_math"]) == set() and fu.module_neimportate(n["cu_math"])
    assert fu.nume_libere(n["foloseste_global"]) == {"AJUTOR"}
    assert fu.nume_libere(n["cu_global"]) == {"CONTOR"}
    linie = ["def f(x): return x + 1"]
    nod = ast.parse(linie[0]).body[0]
    assert fu.text_corp(nod, linie) == "return x + 1\n"
    assert fu.verdict_curata(10_000_000) == "DESTUL PENTRU A"
    assert fu.verdict_curata(2_999_999) == "PUȚIN" and fu.verdict_curata(3_000_000) == "ÎNTRE"


def test_proba_definitiei_in_cutia_adevarata():
    n, linii = _arbore(AUTONOME)
    bun = fu.descrie(n["suma_patrate"], linii)["text"]
    rau = fu.descrie(n["adnotata"], linii)["text"]
    assert fu.proba_in_cutie(bun)["stare"] == "ok"
    r = fu.proba_in_cutie(rau)
    assert r["stare"] == "eroare" and "NameError" in r["mesaj"]


def _cutia_falsa(text):
    if "Necunoscut" in text:
        return {"stare": "eroare", "mesaj": "NameError: name 'Necunoscut' is not defined"}
    return {"stare": "ok", "mesaj": ""}


def test_curata_cap_coada_cu_reluare(tmp_path, date, monkeypatch):
    cod, exclus, cale_tok = date
    # adaug fișierul cu funcțiile S67 și refac numărătoarea S65 pe toate
    randuri = (cod / "cod.jsonl").read_text(encoding="utf-8")
    nou = {"sursa": "pypi", "pachet": "auto", "limbaj": "python", "licenta": "BSD", "cale": "auto/f.py",
           "text": _antrenare(AUTONOME)}
    (cod / "cod.jsonl").write_text(randuri + json.dumps(nou) + "\n", encoding="utf-8")
    iesire = tmp_path / "iesire"
    fu.ruleaza(cod, exclus, iesire, cale_tok, ascunse={}, probleme_proba=PROBA, procese=1, jurnal=lambda m: None)
    arg = dict(ascunse={}, probleme_proba=PROBA, procese=1, fire=2, cutia=_cutia_falsa, jurnal=lambda m: None)

    # oprire curată imediat: nimic scris în curata.json, se reia
    monkeypatch.setattr(fu, "_ora_trecuta", lambda p: True)
    assert fu.curata(cod, iesire, cale_tok, pana_la="00:00", **arg) is None
    assert not (iesire / "curata.json").exists()
    monkeypatch.setattr(fu, "_ora_trecuta", lambda p: False)
    rez = fu.curata(cod, iesire, cale_tok, **arg)
    p = rez["pasi"]
    # (a+b+c) fără duplicate: aria, metoda, invers + cele 8 de aici (toate trec c) = 11
    assert rez["cerute"] == 11 and rez["negasite"] == 0
    assert p["a+b+c fără duplicate"]["toate"]["functii"] == 11
    assert p["(ii) netriviale"]["toate"]["functii"] == 8
    assert p["(iii) definiția trece în cutie"]["toate"]["functii"] == 7
    # autonome: aria (math), metoda, invers, suma_patrate, cu_math = 5; cu (d): aria și metoda
    a = p["(iii) + fără nume libere = autonome"]
    assert a["toate"]["functii"] == 5 and a["cu_d"]["functii"] == 2
    assert 0 < a["toate"]["simboluri_corp"] < a["toate"]["simboluri_intregi"]
    assert [tuple(x) for x in rez["cutie_nume_lipsa_top20"]] == [("Necunoscut", 1)]
    assert rez["scurgere_proba"]["probleme_cu_solutia_exacta"] == 1
    assert (iesire / "autonome.tsv").read_text(encoding="utf-8").count("\n") == 6
    assert len((iesire / "cutie.jsonl").read_text(encoding="utf-8").splitlines()) == 8
    with pytest.raises(SystemExit):
        fu.curata(cod, iesire, cale_tok, **arg)


# ---------------------------------------------------------------- S68: comanda `bland` (importuri de sus + chemabile)

BLANDE = '''import math
import re as expresii
import numpy as np
from collections import deque

try:
    import json
except ImportError:
    json = None


def curata_spatii(s):
    """Alias de modul permis, importat sus: blândă."""
    return expresii.sub(r"\\s+", " ", s).strip()


def radical(x):
    """math importat sus: autonomă la S67, primește importul."""
    y = abs(x)
    return math.sqrt(y)


def cu_statistics(xs):
    """statistics nu e importat nicăieri: autonomă fără import."""
    m = len(xs)
    return statistics.mean(xs) + m


def cu_numpy(xs):
    """numpy nu e permis de cutie: respinsă."""
    a = np.array(xs)
    return a.sum()


def cu_deque(xs):
    """from collections import deque nu leagă un modul: respinsă (doar informativ)."""
    d = deque(xs)
    return d.pop()


def cu_json(o):
    """json din blocul try de sus: blândă."""
    t = json.dumps(o)
    return len(t)


def din_obiect(nod):
    """Primul parametru folosit ca obiect: nu e chemabilă."""
    v = nod.valoare
    return v + 1


class K:
    def metoda(self, x):
        """Metodă cu self."""
        y = x * 2
        return y + 1

    @staticmethod
    def statica(s):
        """Statică, cu apel de metodă pe parametru: chemabilă (nu strict)."""
        t = s.strip()
        return expresii.escape(t)
'''


def test_importurile_de_sus_si_chemabilele():
    arbore = ast.parse(BLANDE)
    module, din = fu.importuri_sus(arbore)
    assert module["expresii"] == ("re", "import re as expresii") and module["np"][0] == "numpy"
    assert module["json"] == ("json", "import json") and "deque" in din and "deque" not in module
    loc = fu.locul_functiilor(arbore)
    pe_nume = {v["nod"].name: v for v in loc.values()}
    assert fu.nume_libere_stricte(pe_nume["radical"]["nod"]) == {"math"}
    assert fu.nume_libere(pe_nume["radical"]["nod"]) == set()
    ch = {k: fu.chemabila(v["nod"], v["in_clasa"], v["static"]) for k, v in pe_nume.items()}
    assert ch["curata_spatii"] == (True, True) and ch["metoda"] == (False, False)
    assert ch["din_obiect"] == (False, False) and ch["statica"] == (True, False)


def test_textul_bland_trece_in_cutia_adevarata():
    text = 'import re as expresii\n\n\ndef f(s):\n    """x"""\n    return expresii.sub("a", "b", s)\n'
    assert fu.proba_in_cutie(text)["stare"] == "ok"
    assert fu.proba_in_cutie("import numpy as np\n\n\ndef f(x):\n    return np.x\n")["stare"] == "interzis"


def test_bland_cap_coada_cu_reluare(tmp_path, date, monkeypatch):
    cod, exclus, cale_tok = date
    randuri = (cod / "cod.jsonl").read_text(encoding="utf-8")
    nou = {"sursa": "pypi", "pachet": "bl", "limbaj": "python", "licenta": "MIT", "cale": "bl/f.py",
           "text": _antrenare(BLANDE)}
    (cod / "cod.jsonl").write_text(randuri + json.dumps(nou) + "\n", encoding="utf-8")
    iesire = tmp_path / "iesire"
    fu.ruleaza(cod, exclus, iesire, cale_tok, ascunse={}, probleme_proba=PROBA, procese=1, jurnal=lambda m: None)
    arg = dict(ascunse={}, probleme_proba=PROBA, procese=1, fire=2, cutia=_cutia_falsa, jurnal=lambda m: None)
    fu.curata(cod, iesire, cale_tok, **arg)

    monkeypatch.setattr(fu, "_ora_trecuta", lambda p: True)
    assert fu.bland(cod, iesire, cale_tok, pana_la="00:00", **arg) is None
    assert not (iesire / "bland.json").exists()
    monkeypatch.setattr(fu, "_ora_trecuta", lambda p: False)
    rez = fu.bland(cod, iesire, cale_tok, **arg)
    c = rez["categorii"]
    # S67 autonome (modulele permise scăzute): aria, radical, cu_json (modul permis importat sus), cu_statistics
    # (neimportat), metoda (C), invers, din_obiect, K.metoda = 8
    assert c["autonoma_cu_import"] == 3 and c["autonoma_fara_import"] == 1
    assert c["autonoma_curata"] == 4
    assert c["blanda"] == 2  # curata_spatii, statica (aliasul `expresii`)
    assert c["respinsa"] == 2  # cu_numpy, cu_deque
    m = rez["multimi"]
    assert m["autonome S67"]["toate"]["toate"]["functii"] == rez["autonome_s67_din_tsv"] == 8
    assert m["autonome + blânde"]["toate"]["toate"]["functii"] == 10
    # chemabile: aria, invers, radical, cu_statistics, cu_json, curata_spatii, statica = 7
    assert m["autonome + blânde"]["chemabile"]["toate"]["functii"] == 7
    assert m["autonome + blânde"]["metode"]["toate"]["functii"] == 3
    assert m["autonome + blânde, fără autonomele cu modul neimportat (strict, informativ)"]["toate"]["toate"][
        "functii"] == 9
    inf = rez["informativ_respinse"]
    assert inf["ar_trece_si_cu_from_M_import_x (M permis)"]["functii"] == 1
    assert [tuple(x) for x in inf["modulele_nepermise_top20"]] == [("numpy", 1)]
    assert rez["cutie_bland_stari"] == {"ok": 5}
    assert rez["scurgere_proba"]["probleme_cu_solutia_exacta"] == 1
    assert (iesire / "blande.tsv").read_text(encoding="utf-8").count("\n") == 11
    assert len((iesire / "cutie_bland.jsonl").read_text(encoding="utf-8").splitlines()) == 5
    with pytest.raises(SystemExit):
        fu.bland(cod, iesire, cale_tok, **arg)


def test_comanda_bland_din_linia_de_comanda(monkeypatch):
    primite = {}
    monkeypatch.setattr(fu, "bland", lambda **k: primite.update(k) or {"ok": 1})
    assert fu.main(["bland", "--procese", "3", "--fire", "4", "--pana-la", "18:20"]) == 0
    assert primite["procese"] == 3 and primite["fire"] == 4 and primite["pana_la"] == "18:20"
    monkeypatch.setattr(fu, "bland", lambda **k: None)
    assert fu.main(["bland"]) == 3


# ---------------------------------------------------------------- S69: comanda `exercitii` (setul + amestecul)

def test_exemplele_doctest_si_asserturile():
    doc = "Aria.\n\n>>> round(aria(1), 2)\n3.14\n>>> x = 2\n>>> aria(x) > 0\nTrue\n>>> aria('a')\nTraceback (most recent call last):\nTypeError: x\n"
    randuri, sarite = fu.exemple_doctest(doc)
    assert sarite == 1 and len(randuri) == 3 and randuri[1] == "x = 2"
    assert randuri[0].startswith("_v = (round(aria(1), 2))\nassert repr(_v) == '3.14'")
    a = fu.asserturi_fisier(ast.parse("def test():\n    assert f(2) == 4\n    assert f(np.x)\n    assert math.floor(f(1)) == 1\n"))
    assert fu.asserturi_pentru("f", a) == ["assert f(2) == 4", "import math\nassert math.floor(f(1)) == 1"]
    assert fu.asserturi_pentru("g", a) == []


def test_programul_doctest_trece_in_cutia_adevarata():
    n, linii = _arbore(CU_DOC)
    text = "import math\n\n\n" + fu.descrie(n["aria"], linii)["text"]
    ex, _ = fu.exemple_doctest(ast.get_docstring(n["aria"]))
    tip, prog, nr = fu.program_d({"exemple": ex, "text": text, "nume": "aria", "doctest": True}, [])
    assert tip == "doctest" and nr == 1 and fu.proba_in_cutie(prog)["stare"] == "ok"
    rau = prog.replace("3.14", "3.15")
    assert fu.proba_in_cutie(rau)["stare"] != "ok"
    tip, prog, nr = fu.program_d({"exemple": [], "text": text, "nume": "aria", "doctest": False}, [])
    assert tip == "assert" and prog is None and nr == 0


def test_repetarile_si_plafonul():
    import numpy as np
    r, k = fu.repetari(np.array([10, 10]), np.array([1.0, 2.0]), 1000, 6)
    assert k == 6 and r.tolist() == [6, 12]
    r, k = fu.repetari(np.array([10, 10, 10, 10]), np.array([1.0, 1.0, 1.0, 1.0]), 100, 6)
    assert k == 2.5 and set(r.tolist()) <= {2, 3}
    assert fu.alege_deoparte({"a", "b", "c"}, 0.02) == fu.alege_deoparte({"c", "b", "a"}, 0.02)
    assert len(fu.alege_deoparte({f"p{i}" for i in range(500)}, 0.02)) == 10


def test_exercitii_cap_coada(tmp_path, date, monkeypatch):
    import numpy as np
    cod, exclus, cale_tok = date
    randuri = (cod / "cod.jsonl").read_text(encoding="utf-8")
    nou = {"sursa": "pypi", "pachet": "auto", "limbaj": "python", "licenta": "BSD", "cale": "auto/f.py",
           "text": _antrenare(AUTONOME)}
    (cod / "cod.jsonl").write_text(randuri + json.dumps(nou) + "\n", encoding="utf-8")
    functii_dir = tmp_path / "functii"
    fu.ruleaza(cod, exclus, functii_dir, cale_tok, ascunse={}, probleme_proba=PROBA, procese=1, jurnal=lambda m: None)
    arg = dict(ascunse={}, probleme_proba=PROBA, procese=1, fire=2, cutia=_cutia_falsa, jurnal=lambda m: None)
    fu.curata(cod, functii_dir, cale_tok, **arg)
    fu.bland(cod, functii_dir, cale_tok, **arg)
    simb = tmp_path / "simboluri"
    simb.mkdir()
    (np.arange(20_000) % 290).astype(np.uint16).tofile(simb / "antrenare_00000.bin")
    (np.arange(100) % 7).astype(np.uint16).tofile(simb / "validare_00000.bin")
    monkeypatch.setattr(fu, "alege_deoparte", lambda pachete, p: {"pypi:pachet"})
    rulate = []
    arg["cutia"] = lambda t: rulate.append(t) or {"stare": "ok", "mesaj": ""}
    iesire = tmp_path / "ex"
    rez = fu.exercitii(4000, cod, functii_dir, simb, iesire, cale_tok, exclus, bloc=16, simboluri_pe_fisier=512, **arg)
    # (a+b+c): aria, metoda (pachet, deoparte), invers (scurgere în proba), cele 8 din AUTONOME
    assert rez["cerute"] == 11 and rez["negasite"] == 0 and rez["scurgere"]["proba_functii_scoase"] == 1
    a = rez["antrenare"]
    assert a["toate"]["functii"] == 8 and a["autonome"]["functii"] == 2  # suma_patrate, cu_math
    assert rez["deoparte"]["toate"]["functii"] == 2 and rez["deoparte"]["cu_d"]["functii"] == 2
    assert rez["deoparte"]["d_pe_tip"] == {"doctest": {"functii": 1, "cu_program": 1, "ok": 1},
                                           "assert": {"functii": 1, "cu_program": 0, "ok": 0}}
    assert len(rulate) == 1 and rulate[0].startswith("import math\n") and "assert repr(_v) == '3.14'" in rulate[0]
    assert rez["repetari"]["maxim_restul"] <= 6 and rez["repetari"]["maxim_autonome"] <= 12
    am = rez["amestec"]
    tot = np.concatenate([np.fromfile(iesire / f, dtype=np.uint16) for f in am["fisiere"]])
    assert len(tot) == am["simboluri_scrise"] and len(am["fisiere"]) > 1
    assert int((tot == fu.SFARSIT).sum()) == sum(int(r.split("\t")[6]) for r in
                                                (iesire / "exercitii.tsv").read_text(encoding="utf-8").splitlines()[1:])
    assert 0.2 < am["procent_exercitii_real"] < 0.3
    assert (iesire / "validare_00000.bin").read_bytes() == (simb / "validare_00000.bin").read_bytes()
    dep = [json.loads(r) for r in (iesire / "deoparte.jsonl").read_text(encoding="utf-8").splitlines()]
    assert {d["nume"] for d in dep} == {"aria", "metoda"} and all(d["corp"] and d["text"] for d in dep)
    assert (simb / "antrenare_00000.bin").stat().st_size == 40_000  # sursa neatinsă
    from module.date_cod import DateCod
    d = DateCod(str(iesire), context=16)
    assert len(d.simboluri_antrenare()) == am["simboluri_scrise"]
    with pytest.raises(SystemExit):
        fu.exercitii(4000, cod, functii_dir, simb, iesire, cale_tok, exclus, bloc=16, **arg)


def test_comanda_exercitii_din_linia_de_comanda(monkeypatch):
    primite = {}
    monkeypatch.setattr(fu, "exercitii", lambda total, **k: primite.update(k, total=total) or {})
    assert fu.main(["exercitii", "--simboluri-total", "970000000", "--procese", "3"]) == 0
    assert primite["total"] == 970_000_000 and primite["procese"] == 3 and primite["procent"] == 0.25
    assert primite["max_rep"] == 6
