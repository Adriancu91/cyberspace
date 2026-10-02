"""Modelul GPT pe procesor, cu dimensiuni mici (se sare dacă lipsește PyTorch)."""

import math

import pytest

torch = pytest.importorskip("torch")

from module.date_mostra import DateMostra  # noqa: E402
from module.examen_bpb import ExamenBpb  # noqa: E402
from module.model_gpt import ModelGPT  # noqa: E402

MIC = dict(n_straturi=2, n_capete=2, n_emb=64, context=64, lot=16, rata_invatare=3e-3, dispozitiv="cpu")


def test_gpt_invata_ceva():
    date = DateMostra(propozitii=1500)
    examen = ExamenBpb(max_caractere=3000)

    putin = ModelGPT(**MIC)
    putin.antreneaza(date, 0.3)
    mult = ModelGPT(**MIC)
    statistici = mult.antreneaza(date, 8.0)

    scor_putin = examen.examineaza(putin, date)["val_bpb"]
    scor_mult = examen.examineaza(mult, date)["val_bpb"]
    assert statistici["pasi"] > 10
    assert math.isfinite(scor_mult)
    assert scor_mult < scor_putin, (scor_putin, scor_mult)


def test_setari_invalide():
    with pytest.raises(ValueError):
        ModelGPT(n_emb=30, n_capete=4)


def test_biti_pentru_text_scurt():
    date = DateMostra(propozitii=200)
    m = ModelGPT(**MIC)
    m.antreneaza(date, 0.5)
    assert m.biti_pentru("") == 0.0
    assert m.biti_pentru("a") > 0
    assert m.biti_pentru("x" * 200) > m.biti_pentru("x" * 20)
