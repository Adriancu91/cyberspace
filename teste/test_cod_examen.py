"""Școala de cod: testele ascunse (generatoarele, cele patru seturi, verificarea de formă, setul sacru)."""

from __future__ import annotations

import json

import pytest

from module.cod import PILOT
from module.cod.examen_cod import (CUTII_LUNGI, CUVINTE_LUNGI, Sarcina, citeste_sacru, generator, genereaza_sacru,
                                   judeca, seturi, verifica_forma)
from module.cod.mediu import citeste_abecedar
from module.cod.sandbox import la_fel, ruleaza, ruleaza_in_proces
from teste.cod_proba import RADACINA

ABECEDAR = citeste_abecedar(RADACINA / "date" / "cod" / "abecedar.txt")
TEXTE_ABECEDAR = {e.test for e in ABECEDAR.episoade}
SACRU_MIC = {n: [Sarcina.din_dict(s) for s in lista] for n, lista in genereaza_sacru(TEXTE_ABECEDAR, 5, "t")["niveluri"].items()}


@pytest.mark.parametrize("nivel", PILOT)
def test_fiecare_solutie_trece_propriul_test(nivel):
    """Toate sarcinile tuturor seturilor: soluția noastră dă rezultatul așteptat și are forma cerută."""
    s = seturi(nivel, TEXTE_ABECEDAR, SACRU_MIC[nivel])
    for sarcina in s.vazut + s.nevazut + s.adversarial + s.sacru:
        assert la_fel(ruleaza_in_proces(sarcina.solutie), sarcina.asteptat), sarcina
        assert verifica_forma(sarcina, sarcina.solutie) is None, sarcina
    # și prin sandbox-ul adevărat (proces separat), pe câteva
    for sarcina in (s.nevazut[0], s.adversarial[0]):
        assert judeca(sarcina, sarcina.solutie, ruleaza(sarcina.solutie))[0] == "trecut"


@pytest.mark.parametrize("nivel", PILOT)
def test_seturile_sunt_separate_si_mereu_aceleasi(nivel):
    s = seturi(nivel, TEXTE_ABECEDAR, SACRU_MIC[nivel])
    texte = s.toate_textele()
    assert [len(texte[n]) for n in ("vazut", "nevazut", "adversarial", "sacru")] == [60, 20, 20, 5]
    for a in texte:
        assert not texte[a] & TEXTE_ABECEDAR, f"{a}: sarcini din abecedar"
        for b in texte:
            assert a == b or not texte[a] & texte[b], f"{a} și {b} au sarcini comune"
    assert seturi(nivel, TEXTE_ABECEDAR, SACRU_MIC[nivel]).toate_textele() == texte
    assert seturi(nivel, TEXTE_ABECEDAR, SACRU_MIC[nivel], samanta="alta").toate_textele()["nevazut"] != texte["nevazut"]


def test_adversarialul_cauta_scurtaturile():
    for nivel in ("1", "2B", "2C"):
        for sarcina in seturi(nivel, TEXTE_ABECEDAR, SACRU_MIC[nivel]).adversarial:
            numere = [int(c) for c in sarcina.text.split() if c.isdigit()]
            assert numere and min(numere) >= 10 and max(numere) >= 30, sarcina.text
    for sarcina in seturi("3B", TEXTE_ABECEDAR, SACRU_MIC["3B"]).adversarial:
        assert all(c in CUTII_LUNGI for c in sarcina.cutii)
    cuvinte = [s for s in seturi("0", TEXTE_ABECEDAR, SACRU_MIC["0"]).adversarial if "word" in s.text]
    assert all(s.asteptat in CUVINTE_LUNGI for s in cuvinte)


def test_verificarea_de_forma():
    plus = Sarcina("2B", "use print to show 2 plus 3", "5", "print(2+3)", cu_print=True, operator="+")
    assert judeca(plus, "print(5)", ruleaza("print(5)")) == ("picat", "rezultat corect, dar lipsește operatorul „+”")
    afisare = Sarcina("2A", "use print to show 9", "9", "print(9)", cu_print=True)
    assert judeca(afisare, "9", ruleaza("9"))[1] == "rezultat corect, dar lipsește „print(”"
    cutie = Sarcina("3A", "put 7 in a box called x, then show x", "7", "x = 7\nprint(x)", cu_print=True, cutii=("x",))
    assert judeca(cutie, "print(7)", ruleaza("print(7)"))[1] == "rezultat corect, dar lipsește cutia „x” (cu „=”)"
    assert verifica_forma(cutie, "x=7\nprint(x)") is None
    assert verifica_forma(cutie, "y = 7\nprint(x == 7)") is not None


def test_verdictele():
    s = Sarcina("1", "add 2 and 3", "5", "2+3", operator="+")
    assert judeca(s, "2+3", ruleaza("2+3"))[0] == "trecut"
    assert judeca(s, "import os", ruleaza("import os")) == ("trișat", "cod interzis: „import”")
    assert judeca(s, "2+4", ruleaza("2+4")) == ("picat", "a ieșit '6', trebuia '5'")
    assert judeca(s, "2+", ruleaza("2+"))[0] == "picat"


def test_nivelurile_de_dupa_pilot_nu_sunt_active():
    with pytest.raises(ValueError, match="nu e activ"):
        generator("4")


def test_setul_sacru_mic():
    date = genereaza_sacru(TEXTE_ABECEDAR, 5, "t")
    assert set(date["niveluri"]) == set(PILOT) and all(len(v) == 5 for v in date["niveluri"].values())
    assert not {s["text"] for v in date["niveluri"].values() for s in v} & TEXTE_ABECEDAR
    assert genereaza_sacru(TEXTE_ABECEDAR, 5, "t")["niveluri"] == date["niveluri"]


def test_setul_sacru_din_proiect():
    """date/cod/sacru.json: 20 de sarcini fixe pe nivel, generat o dată, fără sarcini din abecedar sau din celelalte
    seturi, cu soluțiile corecte."""
    cale = RADACINA / "date" / "cod" / "sacru.json"
    sacru = citeste_sacru(cale)
    assert json.loads(cale.read_text(encoding="utf-8"))["versiune"] == 1
    for nivel in PILOT:
        assert len(sacru[nivel]) == 20
        s = seturi(nivel, TEXTE_ABECEDAR, sacru[nivel])
        assert not s.toate_textele()["sacru"] & (TEXTE_ABECEDAR | s.toate_textele()["vazut"] | s.toate_textele()["nevazut"]
                                                 | s.toate_textele()["adversarial"])
        assert all(la_fel(ruleaza_in_proces(x.solutie), x.asteptat) for x in sacru[nivel])
