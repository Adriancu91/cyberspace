"""Modelul GPT pe procesor, cu dimensiuni mici (se sare dacă lipsește PyTorch)."""

import math

import pytest

torch = pytest.importorskip("torch")

from module.date_mostra import DateMostra  # noqa: E402
from module.examen_bpb import ExamenBpb  # noqa: E402
from module.jucarii import MemorieGoala  # noqa: E402
from module.memorie_ierarhica import MemorieIerarhica  # noqa: E402
from module.model_gpt import ModelGPT  # noqa: E402
from teste.biblioteca_mica import biblioteca_mica  # noqa: E402

MIC = dict(n_straturi=2, n_capete=2, n_emb=64, context=64, lot=16, rata_invatare=3e-3, dispozitiv="cpu")
MIC_MEMORIE = dict(
    n_straturi=1, n_capete=2, n_emb=32, context=32, lot=8, dispozitiv="cpu",
    memorie=True, adancime_memorie=4, n_emb_memorie=8,
)


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


# --- cu memoria ierarhică ------------------------------------------------------


def test_gpt_cu_memorie_invata_si_se_reincarca(tmp_path):
    memorie = MemorieIerarhica(cale=biblioteca_mica(tmp_path), nivele=6)
    model = ModelGPT(**MIC_MEMORIE)
    model.conecteaza_memorie(memorie)
    statistici = model.antreneaza(DateMostra(propozitii=300), 1.5)
    assert statistici["pasi"] > 0 and statistici["parametri_memorie"] > 0
    assert len(statistici["categorii_memorie"]) == 4
    biti = model.biti_pentru("the cat sat on the mat.")
    assert math.isfinite(biti)
    assert len(model.genereaza("the cat ", 20)) == 20

    copie = ModelGPT(dispozitiv="cpu")  # setările și memoria vin din fișierul salvat
    copie.conecteaza_memorie(memorie)
    copie.incarca(model.salveaza(str(tmp_path / "model")))
    assert copie.foloseste_memorie
    assert copie.biti_pentru("the cat sat on the mat.") == pytest.approx(biti, rel=1e-5)


def test_la_inceput_memoria_nu_schimba_nimic(tmp_path):
    """Proiecția memoriei pornește de la zero: neantrenat, modelul cu memorie e identic cu cel fără."""
    date = DateMostra(propozitii=300)
    fara = ModelGPT(**{**MIC_MEMORIE, "memorie": False})
    cu = ModelGPT(**MIC_MEMORIE)
    cu.conecteaza_memorie(MemorieIerarhica(cale=biblioteca_mica(tmp_path), nivele=6))
    assert fara.antreneaza(date, 0.0)["pasi"] == 0
    assert cu.antreneaza(date, 0.0)["pasi"] == 0
    text = "the cat ran to the mat. the old man ran."
    assert cu.biti_pentru(text) == pytest.approx(fara.biti_pentru(text), rel=1e-6)


def test_memorie_fara_port_conectat_da_mesaj_clar():
    with pytest.raises(RuntimeError, match="memorie"):
        ModelGPT(**MIC_MEMORIE).antreneaza(DateMostra(propozitii=100), 1.0)


def test_memoria_goala_nu_strica_nimic():
    model = ModelGPT(**MIC_MEMORIE)
    model.conecteaza_memorie(MemorieGoala())
    model.antreneaza(DateMostra(propozitii=200), 0.5)
    assert math.isfinite(model.biti_pentru("the cat sat."))
    assert len(model.genereaza("the ", 10)) == 10
