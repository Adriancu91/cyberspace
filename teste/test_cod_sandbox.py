"""Școala de cod: sandbox-ul (proces separat, timeout, semantica REPL a abecedarului, cod interzis)."""

from __future__ import annotations

import pytest

from module.cod import sandbox
from module.cod.sandbox import cod_interzis, la_fel, ruleaza, ruleaza_in_proces


@pytest.mark.parametrize("cod, asteptat", [
    ("4", "4"), ("2+3", "5"), ('"dog"', "dog"), ("print(7)", "7"), ("print(2+3)", "5"),
    ("x = 7\nprint(x)", "7"), ("x = 2\ny = 3\nprint(x+y)", "5"), ("print(1)\nprint(2)", "1\n2"),
    ("x = 5", ""),  # o atribuire nu afișează nimic
])
def test_semantica_repl(cod, asteptat):
    rulare = ruleaza(cod)
    assert rulare.a_mers and rulare.iesire == asteptat
    assert ruleaza_in_proces(cod) == asteptat  # aceeași regulă și în proces, pentru soluțiile noastre


def test_aceeasi_regula_ca_abecedarul():
    """Fiecare episod din abecedar dă, prin sandbox, exact rezultatul scris în el."""
    from module.cod.mediu import citeste_abecedar
    from teste.test_cap_coada import RADACINA

    abecedar = citeste_abecedar(RADACINA / "date" / "cod" / "abecedar.txt")
    gresite = [e.test for e in abecedar.episoade if not la_fel(ruleaza(e.cod).iesire, e.rezultat)]
    assert gresite == [] and len(abecedar.episoade) == 105


@pytest.mark.parametrize("cod, gasit", [
    ("import os\nprint(1)", "import"), ('open("x")', "open("), ("print(__name__)", "__"), ("exec('1')", "exec"),
    ("eval('1')", "eval"), ("os.getcwd()", "os."), ("sys.exit()", "sys."), ("subprocess", "subprocess"),
    ("input()", "input("), ("while True:\n    pass", "while True"),
])
def test_codul_interzis_nu_se_ruleaza(cod, gasit):
    assert cod_interzis(cod) == gasit
    rulare = ruleaza(cod)
    assert rulare.trisat == gasit and not rulare.a_mers and rulare.iesire == "" and rulare.secunde == 0.0


def test_timeout_opreste_codul():
    rulare = ruleaza("for i in range(10**12):\n    pass", timeout=0.5)
    assert rulare.eroare == "a depășit timpul (0.5 s)" and not rulare.a_mers


def test_erorile_si_iesirea_prea_lunga():
    assert ruleaza("print(x)").eroare == "NameError: name 'x' is not defined"
    assert ruleaza("1/0").eroare.startswith("ZeroDivisionError")
    assert ruleaza("print(1").eroare.startswith("SyntaxError")
    assert ruleaza("print('a' * 5000)").eroare == "RuntimeError: a scris prea mult"


def test_dosarul_e_gol_si_mediul_curat():
    """Încercarea nu vede fișierele proiectului: dosarul de lucru e unul temporar, gol, iar mediul e curățat. (Codul
    încercărilor n-ar putea verifica asta singur: „import” e interzis; aici rulăm mecanismul fără lista interzisă.)"""
    assert ruleaza("import os\nprint(len(os.listdir('.')))", interzis=()).iesire == "0"
    variabile = ruleaza("import os\nprint(sorted(os.environ))", interzis=()).iesire
    assert variabile in ("[]", "['SYSTEMROOT']")
    assert ruleaza("print(len(list(globals())))").iesire == "1"  # doar funcțiile de bază ale lui Python


def test_comparatia_exacta():
    assert la_fel(" 5\n", "5") and la_fel("1\n2", "1\n2") and not la_fel("1 2", "1\n2") and not la_fel("5.0", "5")
