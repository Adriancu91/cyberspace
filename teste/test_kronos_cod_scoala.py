"""Școala de cod, pregătirea (S72a): pe fișiere mici făcute aici, FĂRĂ rețea și fără datele reale; cutia e cea adevărată."""

import ast
import hashlib
import json

import pytest

from unelte.kronos_cod import functii as fu
from unelte.kronos_cod import scoala as sc
from unelte.kronos_cod.tokenizer_cod import PRAG_VALIDARE

PROBA = [{"id": "p01", "sablon": "p01", "functie": "inverseaza",
          "enunt": 'def inverseaza(s):\n    """Return the string backwards."""\n',
          "referinta": "    return s[::-1]\n", "teste": ["assert inverseaza('ab') == 'ba'"]}]


# ---------------------------------------------------------------- exemplele `>>>` (scăparea din S69 reparată)

def test_comentariul_la_coada_nu_mai_strica_expresia():
    randuri, sarite = sc.exemple_doctest(">>> f(1)  # unu\n2\n")
    assert sarite == 0 and randuri == ["_v = (\nf(1)  # unu\n)\nassert repr(_v) == '2' or str(_v) == '2'"]
    ast.parse(randuri[0])
    vechi, _ = fu.exemple_doctest(">>> f(1)  # unu\n2\n")  # S69: aceeași intrare dădea sintaxă greșită
    with pytest.raises(SyntaxError):
        ast.parse(vechi[0])


def test_blocurile_pe_mai_multe_randuri():
    doc = (">>> for x in [1, 2]:\n>>>   y = x\n>>> y\n2\n"         # continuare scrisă cu `>>>`
           ">>> def g(a):\n...     return a + 1\n>>> g(1)\n2\n"      # continuare corectă cu `...`
           ">>> t = (1,\n...      2)\n>>> len(t)\n2\n")
    randuri, sarite = sc.exemple_doctest(doc)
    assert sarite == 0 and len(randuri) == 6
    assert randuri[0] == "for x in [1, 2]:\n  y = x"
    assert randuri[2] == "def g(a):\n    return a + 1"
    spatiu = {}
    for r in randuri:
        exec(compile(r, "<t>", "exec"), spatiu)  # noqa: S102 — doar exemplele scrise aici


def test_exemplele_sarite():
    doc = ">>> f('a')\nTraceback (most recent call last):\nTypeError: x\n>>> f(2)  # doctest: +SKIP\n3\n>>> import x as\n"
    randuri, sarite = sc.exemple_doctest(doc)
    assert randuri == [] and sarite == 3


def test_testul_trebuie_sa_cheme_functia_cu_argumente():
    assert sc.cheama_cu_argumente("f", ["_v = (\nf(2)\n)\nassert _v == 4"])
    assert not sc.cheama_cu_argumente("f", ["assert f() == 1", "assert m.f(2) == 1"])
    assert sc.are_assert(["x = 1", "assert x"]) and not sc.are_assert(["x = f(1)"])


def test_enuntul_si_corpul_ca_la_examen():
    text = 'class C:\n    @staticmethod\n    def f(x):\n        """Dublul.\n\n        >>> f(2)\n        4\n        """\n        y = 2 * x\n        return y\n'
    nod = [n for n in fu.functiile(ast.parse(text))][0]
    enunt, corp = sc.imparte_functia(nod, text.splitlines())
    assert enunt.startswith("@staticmethod\ndef f(x):\n") and enunt.endswith('    """\n')
    assert corp == "    y = 2 * x\n    return y\n"
    from unelte.kronos_cod.examen_cod import taie_corp
    assert taie_corp(corp) == corp
    unul = ast.parse('def f(x):\n    """D."""; return x\n').body[0]
    assert sc.imparte_functia(unul, ['def f(x):', '    """D."""; return x']) is None
    margine = 'def f():\n    """D."""\n    s = """\nlinie\n"""\n    return s\n'
    assert sc.imparte_functia(ast.parse(margine).body[0], margine.splitlines()) is None


def test_impartirea_pe_pachete():
    pe_pachet = {f"p{i}": 1 + (i % 4) for i in range(200)} | {"mare": 300}
    v = sc.imparte(pe_pachet, 200)
    assert sum(pe_pachet[p] for p in v) == 200 and "mare" not in v
    assert v == sc.imparte(dict(reversed(list(pe_pachet.items()))), 200)  # doar sămânța contează
    v = sc.imparte({"a": 150, "b": 120, "c": 30}, 200)
    assert sum({"a": 150, "b": 120, "c": 30}[p] for p in v) >= 200


def test_motivele():
    assert sc.motiv_cadere("eroare", "NameError: name 'x' is not defined") == "NameError"
    assert sc.motiv_cadere("picat", "AssertionError: ") == "rezultat_gresit"
    assert sc.motiv_cadere("interzis", "sintaxă: invalid syntax (rândul 3)") == "sintaxa"
    assert sc.motiv_cadere("interzis", "import nepermis: os") == "import_nepermis"
    assert sc.motiv_cadere("timp", "depășit 5.0 s") == "timp"


# ---------------------------------------------------------------- cap-coadă, cu cutia adevărată

PA = '''import math


def dublu(x):
    """Dublul.

    >>> dublu(2)  # comentariu
    4
    """
    return 2 * x


def adun(a, b):
    """Suma."""
    return a + b


def gol(x):
    """Nimic.

    >>> gol(1) is None
    True
    """
    y = x
    return None


def cere_nume(x):
    """Cere un nume din alt fișier.

    >>> cere_nume(1)
    2
    """
    return ALTA + x


def fara_arg():
    """Fără argumente.

    >>> fara_arg()
    1
    """
    return 1


def radical(x):
    """Rădăcina.

    >>> radical(9)
    3.0
    """
    return math.sqrt(x)
'''
TEST_PA = "from pa.m import adun\n\n\ndef test_adun():\n    assert adun(1, 2) == 3\n"
PB = 'def patrat(x):\n    """Pătratul.\n\n    >>> patrat(3)\n    9\n    """\n    return x * x\n'
PC = ('def inverseaza(s):\n    """Return the string backwards.\n\n    >>> inverseaza(\'ab\')\n    \'ba\'\n    """\n'
      '    return s[::-1]\n')
PD = 'def tripla(x):\n    """Tripla.\n\n    >>> tripla(1)\n    3\n    """\n    return 3 * x\n'


def _antrenare(text):
    for k in range(1000):
        t = text + f"# {k}\n"
        if hashlib.sha256(t.encode("utf-8")).digest()[0] >= PRAG_VALIDARE:
            return t
    raise AssertionError


@pytest.fixture
def date(tmp_path):
    cod = tmp_path / "cod"
    cod.mkdir()
    fisiere = [("pa", "pa/m.py", PA), ("pa", "pa/tests/test_m.py", TEST_PA), ("pb", "pb/b.py", PB),
               ("pc", "pc/c.py", PC), ("pd", "pd/d.py", PD)]
    randuri = [{"sursa": "pypi", "pachet": p, "limbaj": "python", "licenta": "MIT", "cale": c, "text": _antrenare(t)}
               for p, c, t in fisiere]
    (cod / "cod.jsonl").write_text("".join(json.dumps(r) + "\n" for r in randuri), encoding="utf-8")
    (cod / "aproape_duplicate.json").write_text("[]", encoding="utf-8")
    exclus = tmp_path / "exclus.txt"
    exclus.write_text("", encoding="utf-8")
    ex_dir, f_dir = tmp_path / "exercitii", tmp_path / "functii"
    ex_dir.mkdir()
    f_dir.mkdir()
    tsv = ["i\tlinia\tsha256_normalizat\tautonoma\td\tsimboluri\trepetari\tdeoparte\tpachet\tcale"]
    blande = ["sha256_normalizat\timporturi"]
    for i, r in enumerate(randuri):
        if "tests/" in r["cale"]:
            continue
        linii = r["text"].splitlines()
        for nod in fu.functiile(ast.parse(r["text"])):
            d = fu.descrie(nod, linii)
            deoparte = int(r["pachet"] == "pd")  # pachetul ținut deoparte la S69: nu intră
            tsv.append(f"{i}\t{d['linia']}\t{d['sha']}\t0\t1\t10\t4\t{deoparte}\tpypi:{r['pachet']}\t{r['cale']}")
            if nod.name == "radical":
                blande.append(f"{d['sha']}\timport math")
    (ex_dir / "exercitii.tsv").write_text("\n".join(tsv) + "\n", encoding="utf-8")
    (f_dir / "blande.tsv").write_text("\n".join(blande) + "\n", encoding="utf-8")
    return cod, ex_dir, f_dir, exclus


def test_teste_cap_coada_si_verifica(tmp_path, date):
    cod, ex_dir, f_dir, exclus = date
    iesire = tmp_path / "scoala"
    rez = sc.teste(cod, ex_dir, f_dir, iesire, exclus, ascunse={}, probleme_proba=PROBA, procese=1, fire=4, tinta=2,
                   jurnal=lambda m: None)
    m = rez["motive_toate"]
    assert rez["cerute"] == 8  # pd e deoparte
    assert m["bun"] == 4 and m["trece_si_return_none"] == 1 and m["NameError"] == 1
    assert m["test_fara_apel_cu_argumente"] == 1 and m["scurgere"] == 1
    assert rez["scurgere"]["proba_scoase"] == 1
    bune = rez["exercitii_cu_test_bune"]
    assert bune["total"] == 4 and bune["pachete"] == 2 and bune["pe_tip"] == {"doctest": 3, "assert": 1}
    assert rez["P_verif"]["probleme"] >= 2 and rez["P_verif"]["probleme"] + rez["P_scoala"]["probleme"] == 4
    from unelte.kronos_cod.examen_cod import probleme_setului
    v = probleme_setului("ascuns", iesire / "P_verif")
    s = probleme_setului("ascuns", iesire / "P_scoala")
    assert not ({p.sablon for p in v} & {p.sablon for p in s})
    toate = {p.functie: p for p in v + s}
    assert toate["radical"].enunt.startswith("import math\n\n\ndef radical(x):")
    assert toate["adun"].teste == ["assert adun(1, 2) == 3"]
    assert toate["dublu"].referinta == "    return 2 * x\n"
    with pytest.raises(SystemExit):
        sc.teste(cod, ex_dir, f_dir, iesire, exclus, ascunse={}, probleme_proba=PROBA, procese=1, tinta=2,
                 jurnal=lambda m: None)
    ver = sc.verifica(iesire, cate=2)
    assert ver["bun"] and ver["original"]["corecte"] == [1, 1] and ver["gresit"]["corecte"] == [0, 0]
    assert (iesire / "exercitii_test.tsv").read_text(encoding="utf-8").count("\tbun\t") == 4


def test_comanda_din_linia_de_comanda(monkeypatch):
    primite = {}
    monkeypatch.setattr(sc, "teste", lambda **k: primite.update(k) or {})
    assert sc.main(["teste", "--procese", "3"]) == 0
    assert primite["procese"] == 3 and primite["fire"] == 16
    monkeypatch.setattr(sc, "verifica", lambda **k: {"bun": False, **k})
    assert sc.main(["verifica", "--cate", "5"]) == 1


# ---------------------------------------------------------------- S75: comanda `corecte`

def test_return_fix_si_dupa_spatii():
    assert sc.e_return_fix("    return 3\n")
    assert sc.e_return_fix("    return 'x=(1, 2, 3)'\n")
    assert sc.e_return_fix("    # doar\n    return [1, -2, (3, 'a'), {'k': None}]\n")
    assert not sc.e_return_fix("    return x\n")
    assert not sc.e_return_fix("    return [x, 1]\n")
    assert not sc.e_return_fix("    y = 1\n    return 1\n")
    assert not sc.e_return_fix("    return\n")
    assert not sc.e_return_fix("    print(1)\n")
    assert sc.dupa_spatii("    return  a+b\n\n") == sc.dupa_spatii("  return a+b")
    assert sc.dupa_spatii("return a + b") != sc.dupa_spatii("return a+b")


def test_corecte_cap_coada(tmp_path):
    from unelte.kronos_cod.examen_cod import Problema, scrie_jsonl

    dosar = tmp_path / "P_scoala"
    dosar.mkdir()
    probleme = [
        Problema(id="s00000", sablon="pypi:fluids", varianta="a", functie="dublu",
                 enunt='def dublu(x):\n    """Twice x. dublu(2) -> 4"""\n', referinta="    return 2 * x\n",
                 teste=["assert dublu(2) == 4", "assert dublu(3) == 6"]),
        Problema(id="s00001", sablon="pypi:altul", varianta="b", functie="patru",
                 enunt='def patru(x):\n    """Always 4."""\n', referinta="    return 4\n", teste=["assert patru(1) == 4"]),
        Problema(id="s00002", sablon="pypi:altul", varianta="c", functie="minus",
                 enunt='def minus(x):\n    """Negative."""\n', referinta="    return -x\n", teste=["assert minus(2) == -2"]),
    ]
    sha = scrie_jsonl(probleme, dosar / "probleme.jsonl")
    (dosar / "info.json").write_text(json.dumps({"sha256": sha}), encoding="utf-8")
    raspunsuri = tmp_path / "raspunsuri.jsonl"
    raspunsuri.write_text(json.dumps({"meta": {"set": "ascuns", "n": 4}, "raspunsuri": {
        "s00000": ["    return 2 * x\n", "    return  2 * x\n\n", "    return x + x\n", "    return 4\n"],
        "s00001": ["    return 4\n", "    return 4\n", "    return 5\n", "    return x + 3\n"],
        "s00002": ["    return x\n", "    return nume_lipsa\n", "    return 0 - x\n", "    return -x\n"],
    }}), encoding="utf-8")
    iesire = tmp_path / "runda1"
    num = sc.corecte(raspunsuri, dosar, iesire, fire=4, jurnal=lambda m: None)
    assert num["incercari"] == 12 and num["corecte_toate"] == 8
    assert num["exercitii_cu_corecte_toate"] == 3
    assert num["scoase_return_fix"] == 2 and num["exercitii_doar_cu_return_fix"] == 0
    assert num["duplicate_dupa_spatii_scoase"] == 1
    assert num["corpuri_corecte_diferite"] == 5 and num["exercitii_cu_corpuri_pastrate"] == 3
    assert num["identice_cu_originalul"] == 2  # `return 2 * x` (s00000) și `return -x` (s00002)
    assert num["din_pachetele_mari"]["pypi:fluids"] == {"corpuri": 2, "exercitii": 1}
    assert num["verdict"] == "PREA PUȚINE"
    assert num["control_noteaza"]["la_fel"] and num["control_noteaza"]["ok"] == 8
    assert num["caderi_pe_motiv"] == {"rezultat_gresit": 3, "NameError": 1}
    randuri = [json.loads(r) for r in (iesire / "corecte.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [(r["id"], r["corp"]) for r in randuri] == [
        ("s00000", "    return 2 * x\n"), ("s00000", "    return x + x\n"),
        ("s00001", "    return x + 3\n"), ("s00002", "    return 0 - x\n"), ("s00002", "    return -x\n")]
    assert [r["copiat"] for r in randuri] == [True, False, False, False, True]
    assert all(r["enunt"] and r["pachet"] for r in randuri)
    with pytest.raises(SystemExit):
        sc.corecte(raspunsuri, dosar, iesire, fire=4, jurnal=lambda m: None)
