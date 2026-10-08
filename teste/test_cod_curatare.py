"""Biblioteca curățată după corectitudine (planul joi–sâmbătă, lecția SANDBOX-7): soluția mutată pe sarcinile nevăzute
de aceeași formă trebuie să treacă și acolo."""

from __future__ import annotations

from module.cod.curatare import mutata, potrivire, verifica
from module.cod.examen_cod import Sarcina
from module.cod.sandbox import ruleaza


def ruleaza_toate(coduri: list[str]):
    return [ruleaza(c) for c in coduri]


def test_potrivirea_formelor():
    assert potrivire("show 0", "show 17") == {"0": "17"}
    assert potrivire("put 5 in a box called a, then show a", "put 9 in a box called n, then show n") == {"5": "9",
                                                                                                         "a": "n"}
    assert potrivire("put 4 in t, then show t plus 1", "put 10 in k, then show k plus 3") == {"4": "10", "t": "k",
                                                                                               "1": "3"}
    assert potrivire("show the word kite", "show the word fish") == {"kite": "fish"}
    assert potrivire("add 6 and 6", "add 3 and 7") is None           # 6 ar deveni și 3 și 7: ambiguu
    assert potrivire("add 3 and 7", "take 3 from 7") is None          # altă propoziție
    assert potrivire("show 7", "show the word kite") is None          # altă lungime
    assert potrivire("put 4 in t, then show t plus 1", "put 4 in t, then show t minus 1") is None
    assert potrivire("show 12", "show kite") is None                  # un număr nu devine cuvânt


def test_mutarea_codului():
    assert mutata("t = 0\nprint(t+0)", {"0": "17"}) == "t = 17\nprint(t+17)"
    assert mutata("2+3", {"2": "3", "3": "7"}) == "3+7"               # deodată, fără să se încurce
    assert mutata("a = 5\nprint(a)", {"5": "9", "a": "n"}) == "n = 9\nprint(n)"
    assert mutata("print(12)", {"1": "5"}) == "print(12)"             # doar numere întregi, nu bucăți din ele
    assert mutata('print("kite")', {"kite": "fish"}) == 'print("fish")'


def test_iese_doar_ce_nu_merge_si_pe_sarcinile_noi():
    nevazut = [Sarcina("0", "show 17", "17", "17"), Sarcina("0", "show 42", "42", "42"),
               Sarcina("1", "add 3 and 4", "7", "3+4", operator="+")]
    intrari = [{"test": "show 0", "cod": "t = 0\nprint(t+0)"},     # 0 joacă două roluri: pe 17 dă 34
               {"test": "show 46", "cod": "46"},                    # generală
               {"test": "show 9", "cod": "k = 20\nprint(9)"},       # ciudată, dar mutată dă tot numărul cerut
               {"test": "show the word kite", "cod": '"kite"'},     # nicio sarcină nevăzută de aceeași formă: rămâne
               {"test": "add 2 and 5", "cod": "7"}]                 # rezultatul scris direct: pe 3+4 dă 7 corect... dar
    scoase = verifica(intrari, nevazut, ruleaza_toate)              # fără „+” pică forma
    assert [i["cod"] for i, _ in scoase] == ["t = 0\nprint(t+0)", "7"]
    motiv = dict((i["cod"], m) for i, m in scoase)["t = 0\nprint(t+0)"]
    assert "„show 17”" in motiv and "34" in motiv
    assert "lipsește operatorul" in dict((i["cod"], m) for i, m in scoase)["7"]
