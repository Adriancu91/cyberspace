"""Modelul n-gram: probabilitățile sunt corecte și învățarea chiar funcționează."""

import math

import pytest

from module.date_mostra import DateMostra
from module.examen_bpb import ExamenBpb
from module.model_ngram import ModelNgram


@pytest.fixture(scope="module")
def date():
    return DateMostra(propozitii=1500)


@pytest.mark.parametrize("ordin,netezire", [(1, 1.0), (3, 0.1), (5, 2.0)])
def test_probabilitatile_insumeaza_1(date, ordin, netezire):
    m = ModelNgram(ordin=ordin, netezire=netezire)
    m.antreneaza(date, 5)
    for context in ["", "th", "the c", "zzzz"]:
        assert sum(m.distributie(context).values()) == pytest.approx(1.0, abs=1e-9)


def test_mai_mult_context_inseamna_scor_mai_bun(date):
    examen = ExamenBpb()
    scoruri = {}
    for ordin in (1, 3, 5):
        m = ModelNgram(ordin=ordin, netezire=0.5)
        m.antreneaza(date, 5)
        scoruri[ordin] = examen.examineaza(m, date)["val_bpb"]
    assert scoruri[1] > scoruri[3] > scoruri[5]
    assert all(math.isfinite(s) for s in scoruri.values())


def test_modelul_neantrenat_e_uniform():
    m = ModelNgram(ordin=2)
    assert m.biti_pentru("ab") == pytest.approx(0.0)  # vocabular cu un singur simbol


def test_bugetul_de_timp_e_respectat(date):
    m = ModelNgram(ordin=3)
    statistici = m.antreneaza(date, 0.0)
    assert statistici["oprit_de_buget"] is True
    assert statistici["caractere_vazute"] < len(date.text_antrenare())
