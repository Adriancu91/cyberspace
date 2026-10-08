"""Școala de cod: testele ascunse (generatoarele, cele patru seturi, verificarea de formă, setul sacru)."""

from __future__ import annotations

import json
import random

import pytest

from module.cod import PILOT
from module.cod.examen_cod import (CUTII_LUNGI, CUVINTE_0W, CUVINTE_LUNGI, CUVINTE_LUNGI_0W, Sarcina, adauga_sacru,
                                   citeste_sacru, generator, genereaza_sacru, judeca, seturi, verifica_forma)
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


# --- v0.2: treptele 0a, 0b, 1a, 1b --------------------------------------------------------------------------------------

def numerele(text: str) -> list[str]:
    return [cuvant for cuvant in text.replace(",", " ").split() if cuvant.isdigit()]


SACRU_V02 = {n: [Sarcina.din_dict(s) for s in lista] for n, lista in
             genereaza_sacru(TEXTE_ABECEDAR, 5, "t", ("0a", "0b", "1a", "1b"), {"0a": 0})["niveluri"].items()}


@pytest.mark.parametrize("nivel, cifre, cifre_adversarial, cuvinte", [
    ("0a", {1}, {3}, False), ("0b", {2}, {3}, True), ("1a", {1}, {2}, False), ("1b", {2}, {3}, False)])
def test_treptele_cu_o_cifra_apoi_cu_doua(nivel, cifre, cifre_adversarial, cuvinte):
    marimi = {"vazut": 4, "nevazut": 4} if nivel == "0a" else {}
    s = seturi(nivel, TEXTE_ABECEDAR, SACRU_V02[nivel], **marimi)
    obisnuite = s.vazut + s.nevazut + s.sacru
    assert {len(n) for x in obisnuite for n in numerele(x.text)} == cifre
    assert {len(n) for x in s.adversarial for n in numerele(x.text)} == cifre_adversarial
    assert any("the word" in x.text for x in obisnuite) == cuvinte
    for sarcina in obisnuite + s.adversarial:  # soluția noastră trece propriul test
        assert la_fel(ruleaza_in_proces(sarcina.solutie), sarcina.asteptat) and verifica_forma(sarcina, sarcina.solutie) is None


def test_0a_are_doar_opt_sarcini():
    """Numere de o cifră sunt 10, iar 4 și 8 sunt în abecedar: 8 sarcini, împărțite 4 văzute + 4 nevăzute, fără sacru."""
    s = seturi("0a", TEXTE_ABECEDAR, [], vazut=4, nevazut=4)
    texte = s.toate_textele()
    assert len(texte["vazut"]) == len(texte["nevazut"]) == 4 and not texte["vazut"] & texte["nevazut"]
    assert texte["vazut"] | texte["nevazut"] == {f"show {n}" for n in range(10) if n not in (4, 8)}
    with pytest.raises(ValueError, match="doar 8 sarcini diferite"):
        seturi("0a", TEXTE_ABECEDAR, [], vazut=60, nevazut=20)


def test_setul_sacru_se_completeaza_fara_sa_atinga_nivelurile_vechi():
    date = genereaza_sacru(TEXTE_ABECEDAR, 5, "vechi")
    vechi = json.loads(json.dumps(date["niveluri"]))
    adaugate = adauga_sacru(date, TEXTE_ABECEDAR, ("0", "0a", "0b", "1b"), 5, "nou", {"0a": 0})
    assert adaugate == ["0a", "0b", "1b"] and date["niveluri"]["0a"] == [] and len(date["niveluri"]["1b"]) == 5
    assert json.loads(json.dumps({n: date["niveluri"][n] for n in vechi})) == vechi  # cele vechi, sarcină cu sarcină
    assert adauga_sacru(date, TEXTE_ABECEDAR, ("0", "0a"), 5, "nou") == []  # nimic de adăugat


def test_setul_sacru_din_proiect_pentru_v02():
    """Nivelurile v0.2, adăugate o dată (0a nu are: toate cele 8 sarcini ale lui sunt în celelalte seturi), separate de
    seturile v0.2 și de abecedar."""
    sacru = citeste_sacru(RADACINA / "date" / "cod" / "sacru.json")
    for nivel, marime in (("0a", 0), ("0b", 20), ("1a", 20), ("1b", 20)):
        assert len(sacru[nivel]) == marime
        s = seturi(nivel, TEXTE_ABECEDAR, sacru[nivel], samanta="v0.2",
                   **({"vazut": 4, "nevazut": 4} if nivel == "0a" else {}))
        texte = s.toate_textele()
        assert not texte["sacru"] & (TEXTE_ABECEDAR | texte["vazut"] | texte["nevazut"] | texte["adversarial"])
        assert all(la_fel(ruleaza_in_proces(x.solutie), x.asteptat) for x in sacru[nivel])


# --- v0.3 ----------------------------------------------------------------------------------------------------------------

def test_v03_nivelurile_0n_si_0w():
    """0n = numerele 0–99 împreună (adversarial: trei cifre); 0w = doar cuvintele (adversarial: cuvinte lungi)."""
    gen_n, gen_w, rng = generator("0n"), generator("0w"), random.Random(1)
    numere = [gen_n(rng, False) for _ in range(1000)]
    assert {int(s.solutie) for s in numere} == set(range(100))
    assert all(s.text == f"show {s.solutie}" and s.asteptat == s.solutie and s.doar_valoare for s in numere)
    assert all(100 <= int(gen_n(rng, True).solutie) <= 999 for _ in range(100))
    cuvinte = [gen_w(rng, False) for _ in range(3000)]
    assert {s.asteptat for s in cuvinte} == set(CUVINTE_0W)
    assert all(s.solutie == f'"{s.asteptat}"' and s.doar_valoare for s in cuvinte)
    assert {gen_w(rng, True).asteptat for _ in range(1000)} == set(CUVINTE_LUNGI_0W)
    assert len(set(CUVINTE_0W)) == len(CUVINTE_0W) >= 100 and len(set(CUVINTE_LUNGI_0W)) == len(CUVINTE_LUNGI_0W) >= 20
    assert not set(CUVINTE_0W) & set(CUVINTE_LUNGI_0W) and not {"dog", "sun", "red"} & set(CUVINTE_0W)  # abecedarul


@pytest.mark.parametrize("nivel", ("0n", "0w"))
def test_v03_solutiile_trec_si_seturile_sunt_separate(nivel):
    sacru = [Sarcina.din_dict(x) for x in genereaza_sacru(TEXTE_ABECEDAR, 5, "t", niveluri=(nivel,))["niveluri"][nivel]]
    s = seturi(nivel, TEXTE_ABECEDAR, sacru, **({"vazut": 55} if nivel == "0n" else {}))
    texte = s.toate_textele()
    assert not texte["sacru"] & (TEXTE_ABECEDAR | texte["vazut"] | texte["nevazut"] | texte["adversarial"])
    for sarcina in s.vazut + s.nevazut + s.adversarial + s.sacru:
        assert la_fel(ruleaza_in_proces(sarcina.solutie), sarcina.asteptat), sarcina
        assert verifica_forma(sarcina, sarcina.solutie) is None, sarcina


def test_v03_forma_doar_valoarea():
    """La 0n și 0w codul e doar valoarea sau print(valoarea): `t = 0 ⏎ print(t+0)` nu mai trece la „show 0”."""
    numar = Sarcina("0n", "show 46", "46", "46", doar_valoare=True)
    cuvant = Sarcina("0w", "show the word kite", "kite", '"kite"', doar_valoare=True)
    for sarcina, cod, verdict in (
            (numar, "46", "trecut"), (numar, "print(46)", "trecut"), (numar, "print( 46 )\n", "trecut"),
            (numar, '"46"', "picat"), (numar, "46+0", "picat"), (numar, "t = 46\nprint(t)", "picat"),
            (numar, "print(46)\nprint(46)", "picat"),
            (cuvant, '"kite"', "trecut"), (cuvant, "'kite'", "trecut"), (cuvant, 'print("kite")', "trecut"),
            (cuvant, 'w = "kite"\nprint(w)', "picat"), (cuvant, '"ki" + "te"', "picat"), (cuvant, "kite", "picat")):
        assert judeca(sarcina, cod, ruleaza(cod))[0] == verdict, cod
    assert "doar valoarea" in judeca(numar, "t = 46\nprint(t)", ruleaza("t = 46\nprint(t)"))[1]
    vechi = Sarcina("0", "show 46", "46", "46")  # nivelurile v0.1 și v0.2: neschimbate
    assert judeca(vechi, "t = 46\nprint(t)", ruleaza("t = 46\nprint(t)"))[0] == "trecut"


def test_setul_sacru_din_proiect_pentru_v03():
    """0n și 0w, adăugate o dată (20 fiecare), separate de seturile v0.3 și de abecedar."""
    sacru = citeste_sacru(RADACINA / "date" / "cod" / "sacru.json")
    for nivel, vazut in (("0n", 55), ("0w", 60)):
        assert len(sacru[nivel]) == 20 and all(x.doar_valoare for x in sacru[nivel])
        s = seturi(nivel, TEXTE_ABECEDAR, sacru[nivel], vazut=vazut, samanta="v0.3")
        texte = s.toate_textele()
        assert not texte["sacru"] & (TEXTE_ABECEDAR | texte["vazut"] | texte["nevazut"] | texte["adversarial"])
        assert all(la_fel(ruleaza_in_proces(x.solutie), x.asteptat) for x in sacru[nivel])
