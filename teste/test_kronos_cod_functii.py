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
