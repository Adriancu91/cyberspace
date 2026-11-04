"""Memoria de cod (S71): indexul din exercițiile S69, căutarea, scurgerea și bugetul de context. Fără rețea, fără placă."""

import ast
import json
import sqlite3

import pytest

from unelte.kronos_cod import functii as fu
from unelte.kronos_cod import memorie as me
from unelte.kronos_cod import scurgere

FISIER = '''import math


def count_divisible(numbers, k):
    """Return how many numbers in the list are divisible by k."""
    return sum(1 for n in numbers if n % k == 0)


def reverse_words(text):
    """Reverse the order of the words in a sentence."""
    return " ".join(reversed(text.split()))


def circle_area(r):
    """Area of a circle with radius r."""
    return math.pi * r * r
'''


def _date(tmp_path, deoparte_reverse=False):
    cod = tmp_path / "complet"
    cod.mkdir()
    randuri = [{"sursa": "pypi", "pachet": "p", "limbaj": "python", "cale": "p/f.py", "text": "x = 1\n"},
               {"sursa": "pypi", "pachet": "p", "limbaj": "python", "cale": "p/g.py", "text": FISIER}]
    (cod / "cod.jsonl").write_text("".join(json.dumps(r) + "\n" for r in randuri), encoding="utf-8")
    arbore = ast.parse(FISIER)
    linii = FISIER.splitlines()
    ex = tmp_path / "exercitii"
    ex.mkdir()
    rand = ["i\tlinia\tsha256_normalizat\tautonoma\td\tsimboluri\trepetari\tdeoparte\tpachet\tcale"]
    sume = {}
    for nod in fu.functiile(arbore):
        d = fu.descrie(nod, linii)
        sume[nod.name] = d["sha"]
        dep = "1" if (deoparte_reverse and nod.name == "reverse_words") else "0"
        rand.append(f"1\t{nod.lineno}\t{d['sha']}\t1\t0\t10\t4\t{dep}\tpypi:p\tp/g.py")
    rand.append(f"1\t999\t{'0' * 64}\t0\t0\t10\t4\t0\tpypi:p\tp/g.py")  # nu mai există: numărat la „negăsite”
    (ex / "exercitii.tsv").write_text("\n".join(rand) + "\n", encoding="utf-8")
    fd = tmp_path / "functii"
    fd.mkdir()
    (fd / "blande.tsv").write_text("sha256_normalizat\timporturi\n" + f"{sume['circle_area']}\timport math\n",
                                   encoding="utf-8")
    return cod, ex, fd


def test_index_si_cautare(tmp_path):
    cod, ex, fd = _date(tmp_path, deoparte_reverse=True)
    cale = tmp_path / "m" / "index.sqlite"
    rez = me.index(cod, ex, fd, cale, procese=1, jurnal=lambda m: None)
    assert rez["cerute"] == 3 and rez["in_index"] == 2 and rez["negasite"] == 1
    assert json.loads(cale.with_suffix(".json").read_text(encoding="utf-8"))["in_index"] == 2
    con = sqlite3.connect(cale)
    gasite = me.cauta(con, 'def count_multiples(values, k):\n    """Count values divisible by k."""\n')
    assert gasite[0]["text"].startswith("def count_divisible")
    # cea ținută deoparte nu e în index
    assert not any("reverse_words" in g["text"] for g in me.cauta(con, "reverse words sentence order"))
    # importurile din S68 vin în față, ca la exercițiu
    arie = me.cauta(con, "area circle radius")[0]["text"]
    assert arie.startswith("import math\n\n\ndef circle_area")
    with pytest.raises(SystemExit):
        me.index(cod, ex, fd, cale, procese=1, jurnal=lambda m: None)


def test_intrebarea():
    q = me.intrebare('def count_div(nums, k):\n    """Count the nums: "k" divides."""\n')
    assert q == '"count" OR "div" OR "nums" OR "k" OR "the" OR "divides"'
    assert me.intrebare("  ") == ""


def _numara(t):
    return len(t.split())


def test_alege_bugetul_si_scurgerea():
    referinta = "    total = 0\n    for value in values:\n        if value % k == 0:\n            total = total + 1\n" \
                "    return total\n"
    p = {"id": "x", "enunt": "def f(values, k):\n    \"\"\"Doc.\"\"\"\n", "referinta": referinta,
         "teste": ["assert f([1, 2], 2) == 1"], "functie": "f"}
    idx = scurgere.indexeaza([p])
    scurs = {"text": "def g(values, k):\n" + referinta, "sha": "a", "pachet": "p", "scor": 3.0}
    mare = {"text": "x " * 400, "sha": "b", "pachet": "p", "scor": 2.0}
    mici = [{"text": f"def h{i}():\n    return {i}\n", "sha": f"c{i}", "pachet": "p", "scor": 1.0} for i in range(6)]
    alese, scoase = me.alege([scurs, mare] + mici, p["enunt"], idx, _numara)
    assert scoase == 1
    assert [c["sha"] for c in alese] == ["c0", "c1", "c2", "c3"]  # cel mult 4, cea prea mare sărită
    # bugetul: 512 − 1 − enunț − rezervă
    alese, _ = me.alege(mici, p["enunt"], idx, _numara, context=1 + _numara(p["enunt"]) + 128 + 8)
    assert len(alese) == 2
    assert me.inceput(alese) == mici[1]["text"] + "\n" + mici[0]["text"] + "\n"  # cea mai asemănătoare ultima
