"""Textul cu numere al amestecului (unelte/numere_ws.py): variat și adevărat."""

import re
from datetime import date

from unelte.numere_ws import (
    FELURI, LUNI_EN, LUNI_RO, SEPARATOR, ZILE_EN, ZILE_RO, cu_de, in_litere_en, in_litere_ro, ordinal_en, text_numere,
)

TEXT = text_numere(600_000, samanta=1)


def test_acelasi_text_la_aceeasi_samanta_si_bucati_despartite():
    assert text_numere(50_000, samanta=4) == text_numere(50_000, samanta=4) != text_numere(50_000, samanta=5)
    bucati = TEXT.split(f"\n{SEPARATOR}\n")
    assert bucati[-1] == "" and len(bucati) > 300
    assert all(6 <= len(b.split("\n")) for b in bucati[:-1])
    assert len(TEXT.encode("utf-8")) >= 600_000


def test_numerele_in_litere():
    assert [in_litere_ro(n) for n in (0, 1, 12, 14, 16, 20, 21, 60, 99, 100, 101, 200, 345, 999)] == [
        "zero", "unu", "doisprezece", "paisprezece", "șaisprezece", "douăzeci", "douăzeci și unu", "șaizeci",
        "nouăzeci și nouă", "o sută", "o sută unu", "două sute", "trei sute patruzeci și cinci",
        "nouă sute nouăzeci și nouă"]
    assert [in_litere_en(n) for n in (0, 13, 20, 21, 40, 100, 110, 345, 999)] == [
        "zero", "thirteen", "twenty", "twenty-one", "forty", "one hundred", "one hundred ten",
        "three hundred forty-five", "nine hundred ninety-nine"]
    assert len({in_litere_ro(n) for n in range(1000)}) == 1000 and len({in_litere_en(n) for n in range(1000)}) == 1000
    assert [ordinal_en(n) for n in (1, 2, 3, 4, 11, 12, 13, 21, 22, 101, 111, 112)] == [
        "1st", "2nd", "3rd", "4th", "11th", "12th", "13th", "21st", "22nd", "101st", "111th", "112th"]
    assert [cu_de(n, "mere") for n in (5, 19, 20, 100, 101, 119, 120)] == [
        "5 mere", "19 mere", "20 de mere", "100 de mere", "101 mere", "119 mere", "120 de mere"]


def test_calculele_sunt_corecte():
    verificate = 0
    for rand in TEXT.splitlines():
        m = re.fullmatch(r"(\d+) ([-+*x×/:÷]) (\d+) = (\d+)", rand)
        if m:
            a, semn, b, c = int(m[1]), m[2], int(m[3]), int(m[4])
            assert c == (a + b if semn == "+" else a - b if semn == "-" else a * b if semn in "*x×" else a // b), rand
            assert semn not in "/:÷" or a % b == 0, rand
            verificate += 1
        m = re.fullmatch(r"(\d+)% (?:din|of) (\d+) (?:=|is) (\d+)", rand)
        if m:
            assert int(m[1]) * int(m[2]) == 100 * int(m[3]), rand
            verificate += 1
        m = re.fullmatch(r"(\d+) = (\d+) \* (\d+) \+ (\d+); .*", rand)
        if m:
            assert int(m[1]) == int(m[2]) * int(m[3]) + int(m[4]) and int(m[4]) < int(m[2]), rand
            verificate += 1
        m = re.fullmatch(r"sum\(\[([\d, ]+)\]\) = (\d+); max = (\d+); min = (\d+); len = (\d+)", rand)
        if m:
            valori = [int(x) for x in m[1].split(",")]
            assert (sum(valori), max(valori), min(valori), len(valori)) == tuple(int(m[k]) for k in (2, 3, 4, 5)), rand
            verificate += 1
    assert verificate > 400


def test_zilele_saptamanii_si_numerele_in_litere_din_text_sunt_adevarate():
    zile = litere = 0
    for rand in TEXT.splitlines():
        m = re.fullmatch(r"(\d+) (\w+) (\d{4}) a fost într-o zi de (\w+)\.", rand)
        if m:
            assert ZILE_RO[date(int(m[3]), LUNI_RO.index(m[2]) + 1, int(m[1])).weekday()] == m[4], rand
            zile += 1
        m = re.fullmatch(r"(\w+) (\d+), (\d{4}) was a (\w+)\.", rand)
        if m:
            assert ZILE_EN[date(int(m[3]), LUNI_EN.index(m[1]) + 1, int(m[2])).weekday()] == m[4], rand
            zile += 1
        m = re.fullmatch(r"(\d+) = ([^=]+) = ([^=]+)", rand)
        if m and not m[2][0].isdigit():
            assert in_litere_ro(int(m[1])) == m[2] and in_litere_en(int(m[1])) == m[3], rand
            litere += 1
    assert zile > 80 and litere > 40


def test_masurile_si_sortarile_sunt_adevarate():
    masuri = sortari = 0
    for rand in TEXT.splitlines():
        m = re.fullmatch(r"(\d+) km = ([\d.]+) m; (\d+) m = (\d+) cm; (\d+) cm = (\d+) mm", rand)
        if m:
            assert int(m[2].replace(".", "")) == int(m[1]) * 1000 and int(m[4]) == int(m[3]) * 100, rand
            masuri += 1
        m = re.fullmatch(r"\[([\d, ]+)\] sortat crescător: \[([\d, ]+)\]", rand)
        if m:
            assert sorted(int(x) for x in m[1].split(",")) == [int(x) for x in m[2].split(",")], rand
            sortari += 1
    assert masuri > 20 and sortari > 20


def test_textul_e_variat():
    """Multe feluri de rânduri, nu câteva tipare: se numără formele rândurilor, cu cifrele și numele scoase."""
    forme = {re.sub(r"\d+", "0", rand) for rand in TEXT.splitlines() if rand != SEPARATOR}
    assert len(forme) > 1000  # generatorul vechi avea 14 tipare
    assert sum(g for _, _, g in FELURI) == 1.0 and len(FELURI) == 6
    for semn in ("lei", "km", "kg", "°C", "%", "sortat", "locul", "este un număr", "was a", "a fost într-o zi de",
                 "hundred", "sute", "²", "rest", "etajul"):
        assert semn in TEXT, semn
    assert "1 mere" not in TEXT and " 1 de " not in TEXT
