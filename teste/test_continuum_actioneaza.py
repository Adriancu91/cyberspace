"""CONTINUUM, ACȚIONEAZĂ: comenzile pregătite din configurare și rularea lor (cu unelte de probă, pe procesor)."""

from __future__ import annotations

import json
import sys

import pytest

from module.continuum import INTRETINERE, citeste_config
from module.continuum.actioneaza import Plan, Refuz, actioneaza, completeaza, fisiere_lipsa, planifica, text_comanda
from module.continuum.evalueaza import evalueaza
from module.continuum.nevoi import Nevoie, nevoi
from module.continuum.observa import descopera_module, observa
from teste.continuum_proba import (Lume, config_continuum, config_kronos, fisa, noaptea_3, scrie_hrana, scrie_jurnal,
                                   scrie_unelte)


@pytest.fixture
def proiect(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    scrie_unelte(tmp_path)
    return tmp_path


def stare_si_config(radacina, lume=None):
    config = citeste_config(config_continuum(radacina))
    return evalueaza(observa(config, descopera_module(config), (lume or Lume()).senzori()), config), config


def test_completeaza_comanda():
    sablon = ["{python}", "unelte/antrenare_lunga.py", "--config", "{config}", "--porneste-din", "{model}", "--x"]
    assert completeaza(sablon, {"config": "c.toml", "model": 8}) == [sys.executable, "unelte/antrenare_lunga.py",
                                                                     "--config", "c.toml", "--porneste-din", "8", "--x"]
    assert completeaza(sablon, {"config": "c.toml", "model": None})[-3:] == ["--config", "c.toml", "--x"]
    with pytest.raises(KeyError, match="câmp necunoscut"):
        completeaza(["{necunoscut}"], {})
    assert text_comanda([sys.executable, "a b.py"]) == 'python "a b.py"'


def test_fisierele_care_lipsesc(proiect):
    assert fisiere_lipsa([sys.executable, "unelte/examen_fapte.py", "--config", "config/nu_exista.toml"]) == [
        "config/nu_exista.toml"]


def test_modelul_de_pornire_tine_cont_de_arhitectura(proiect):
    noaptea_3(proiect)
    scrie_hrana(proiect)
    nevoie = Nevoie("continua", "povesti", 2, "test")
    config_kronos(proiect, "laptop_antrenare_lunga_4.toml", "antrenare_lunga_4", straturi=12)  # alt model: de la zero
    stare, config = stare_si_config(proiect)
    plan = planifica(nevoie, stare, config)
    assert "--porneste-din" not in plan.comenzi[0] and plan.descriere.endswith("de la zero)")
    config_kronos(proiect, "laptop_antrenare_lunga_4.toml", "antrenare_lunga_4", model=", de_la_zero = true")
    stare, config = stare_si_config(proiect)
    assert "--porneste-din" not in planifica(nevoie, stare, config).comenzi[0]


def test_ziua_hrana_noua_cand_cea_veche_a_fost_folosita(proiect):
    noaptea_3(proiect)
    scrie_hrana(proiect)
    config_kronos(proiect, "laptop_fapte.toml", "fapte_1", date=', hrana = "date/fapte/povesti.txt"')
    examene = {"fapte_corecte": 60, "nota_profesor": 4.9}  # faptele (40%) rămân cea mai slabă capacitate
    scrie_jurnal(proiect, [fisa(i, "fapte_1", 0.45, criterii=examene, inceput="2026-10-07T21:00:00+00:00")
                           for i in range(11, 19)])
    stare, config = stare_si_config(proiect, Lume(ora="12:00"))
    dezvolta = next(n for n in nevoi(stare, config) if n.tip == "dezvolta")
    plan = planifica(dezvolta, stare, config)
    assert plan.fel == "hrana" and plan.comenzi[0][1:] == ["unelte/genereaza_fapte.py", "--povesti", "11000"]
    assert plan.descriere == ("hrană nouă de la profesor pentru fapte, până la 11.000 de povești scrise (hrana de acum a "
                              "fost folosită deja)")
    stare, config = stare_si_config(proiect)  # noaptea: hrana folosită nu se mai mănâncă o dată
    refuz = planifica(dezvolta, stare, config)
    assert isinstance(refuz, Refuz) and not refuz.indisponibila and "folosită deja (fapte_1)" in refuz.motiv


def test_simulat_nu_ruleaza_nimic(proiect):
    jurnal = scrie_jurnal(proiect, [])
    plan = Plan("masoara:fapte", "examene", "masoara:examene", "examenul de fapte",
                [[sys.executable, "unelte/examen_fapte.py", "--experiment", "8"]], 60)
    rezultat = actioneaza(plan, simuleaza=True, director=proiect / "lucru" / "continuum", ciclu=1)
    assert rezultat == {"simulat": True, "reusit": None, "comenzi": ["python unelte/examen_fapte.py --experiment 8"]}
    assert jurnal.read_text(encoding="utf-8") == "" and not (proiect / "lucru" / "continuum").exists()


def test_ruleaza_unealta_si_pastreaza_ce_scrie(proiect):
    jurnal = scrie_jurnal(proiect, [])
    plan = Plan("masoara:fapte", "examene", "masoara:examene", "examenul de fapte",
                [[sys.executable, "unelte/examen_fapte.py", "--experiment", "8"]], 60)
    rezultat = actioneaza(plan, simuleaza=False, director=proiect / "lucru" / "continuum", ciclu=7)
    assert rezultat["reusit"] and rezultat["comenzi"][0]["cod"] == 0
    assert rezultat["iesire"].endswith("lucru/continuum/actiuni/ciclu_00007_examene.log")
    fise = [json.loads(r) for r in jurnal.read_text(encoding="utf-8").splitlines()]
    assert fise == [{"id": 1, "linie": "examen_fapte", "decizie": "masurat", "module": {"elev": {"experiment": 8}},
                     "scoruri": {"corecte_doar_cuvantul_din_fapt": 33}}]  # scrisă de unealtă, nu de CONTINUUM


def test_o_unealta_care_cade_sau_dureaza_prea_mult(proiect):
    (proiect / "unelte" / "cade.py").write_text("import sys\nsys.exit(3)\n", encoding="utf-8")
    (proiect / "unelte" / "doarme.py").write_text("import time\ntime.sleep(30)\n", encoding="utf-8")
    director = proiect / "lucru" / "continuum"
    plan = Plan("x", "examene", "x", "x", [[sys.executable, "unelte/cade.py"], [sys.executable, "unelte/doarme.py"]], 60)
    rezultat = actioneaza(plan, simuleaza=False, director=director, ciclu=1)
    assert not rezultat["reusit"] and "a ieșit cu codul 3" in rezultat["motiv"]
    assert len(rezultat["comenzi"]) == 1  # se oprește la prima care nu reușește
    plan = Plan("x", "examene", "x", "x", [[sys.executable, "unelte/doarme.py"]], 1)
    rezultat = actioneaza(plan, simuleaza=False, director=director, ciclu=2)
    assert not rezultat["reusit"] and "a depășit timpul" in rezultat["motiv"] and rezultat["comenzi"][0]["secunde"] < 20


def test_masurarea_cere_ultimul_model(proiect):
    noaptea_3(proiect, masurat=False)
    stare, config = stare_si_config(proiect, Lume(ora="12:00"))
    assert stare.nivel == INTRETINERE
    masoara = next(n for n in nevoi(stare, config) if n.tip == "masoara")
    (proiect / "unelte" / "examen_profesor.py").unlink()
    plan = planifica(masoara, stare, config)
    assert plan.detalii == {"capacitati": ["fapte"], "experiment": 8}
    assert "sar peste sens: lipsește unelte/examen_profesor.py" in plan.descriere
