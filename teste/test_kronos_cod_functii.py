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
