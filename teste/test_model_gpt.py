"""Modelul GPT pe procesor, cu dimensiuni mici (se sare dacă lipsește PyTorch)."""

import math

import pytest

torch = pytest.importorskip("torch")

from module.date_mostra import DateMostra  # noqa: E402
from module.examen_bpb import ExamenBpb  # noqa: E402
from module.jucarii import MemorieGoala  # noqa: E402
from module.memorie_ierarhica import MemorieIerarhica  # noqa: E402
from module.model_gpt import ModelGPT  # noqa: E402
from module.tokenizer_bpe import antreneaza_bpe  # noqa: E402
from teste.biblioteca_mica import biblioteca_mica  # noqa: E402

MIC = dict(n_straturi=2, n_capete=2, n_emb=64, context=64, lot=16, rata_invatare=3e-3, dispozitiv="cpu")
MIC_MEMORIE = dict(
    n_straturi=1, n_capete=2, n_emb=32, context=32, lot=8, dispozitiv="cpu",
    memorie=True, adancime_memorie=4, n_emb_memorie=8,
)
MIC_BPE = dict(n_straturi=1, n_capete=2, n_emb=32, context=32, lot=8, dispozitiv="cpu", tokenizer="bpe")


@pytest.fixture
def tokenizer_mic(tmp_path):
    cale = tmp_path / "bpe_mic.json"
    antreneaza_bpe(DateMostra(propozitii=600).text_antrenare(), 320).salveaza(cale)
    return str(cale)


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


def test_categoriile_nevazute_la_antrenare_primesc_gol(tmp_path):
    """„horse” nu apare în textul de antrenare (dar „cat” da): nivelurile comune cu „cat”
    (substantiv, noun.animal, entity > organism > animal) sunt cunoscute, iar nivelul propriu
    lui „horse” primește 0, nu o descriere neantrenată (zgomot)."""
    memorie = MemorieIerarhica(cale=biblioteca_mica(tmp_path), nivele=6)
    model = ModelGPT(**{**MIC_MEMORIE, "adancime_memorie": 6, "pasi_max": 1})
    model.conecteaza_memorie(memorie)
    date = DateMostra(propozitii=300)
    assert "horse" not in date.text_antrenare() and "cat" in date.text_antrenare()
    model.antreneaza(date, 30.0)
    categorii = model._categorii(memorie.caracteristici("horse "))[5].tolist()  # la spațiu, „horse” e terminat
    assert all(c > 0 for c in categorii[:5]) and categorii[5] == 0
    assert model.retea is not None and all(
        c < emb.num_embeddings for c, emb in zip(categorii, model.retea.memorie)
    )


def test_pasi_max_opreste_antrenarea_la_numarul_cerut(tmp_path):
    date = DateMostra(propozitii=200)
    assert ModelGPT(**MIC, pasi_max=7).antreneaza(date, 60.0)["pasi"] == 7
    cu = ModelGPT(**MIC_MEMORIE, pasi_max=5)
    cu.conecteaza_memorie(MemorieIerarhica(cale=biblioteca_mica(tmp_path), nivele=6))
    statistici = cu.antreneaza(date, 60.0)
    assert statistici["pasi"] == 5 and statistici["pasi_max"] == 5
    with pytest.raises(ValueError, match="pasi_max"):
        ModelGPT(pasi_max=-1)


def test_memorie_fara_port_conectat_da_mesaj_clar():
    with pytest.raises(RuntimeError, match="memorie"):
        ModelGPT(**MIC_MEMORIE).antreneaza(DateMostra(propozitii=100), 1.0)


# --- pe bucăți de cuvinte (BPE) ------------------------------------------------------


def test_gpt_pe_bucati_de_cuvinte_invata_si_se_reincarca(tmp_path, tokenizer_mic):
    date = DateMostra(propozitii=300)
    model = ModelGPT(**MIC_BPE, cale_tokenizer=tokenizer_mic)
    statistici = model.antreneaza(date, 1.5)
    assert statistici["tokenizer"] == "bpe" and statistici["pasi"] > 0
    assert statistici["simboluri_antrenare"] < len(date.text_antrenare()) / 2  # mai puține simboluri decât litere
    text = "the cat sat on the mat. Diacritice: ășț 🐱"
    biti = model.biti_pentru(text)
    assert math.isfinite(biti) and biti > 0
    continuare = model.genereaza("the cat ", 25)
    assert isinstance(continuare, str) and len(continuare) == 25

    copie = ModelGPT(dispozitiv="cpu")  # tokenizerul vine din fișierul salvat
    copie.incarca(model.salveaza(str(tmp_path / "model")))
    assert copie.tokenizer == "bpe"
    assert copie.biti_pentru(text) == pytest.approx(biti, rel=1e-5)
    assert copie.genereaza("the cat ", 25) == continuare


def test_examenul_merge_la_fel_pe_litere_si_pe_bucati(tokenizer_mic):
    date = DateMostra(propozitii=300)
    examen = ExamenBpb(max_caractere=2000)
    for setari in ({**MIC_BPE, "tokenizer": "litere"}, {**MIC_BPE, "cale_tokenizer": tokenizer_mic}):
        model = ModelGPT(**setari)
        model.antreneaza(date, 0.5)
        scoruri = examen.examineaza(model, date)
        assert math.isfinite(scoruri["val_bpb"]) and scoruri["generare_ok"] == 1.0


def test_tokenizer_lipsa_sau_gresit_da_mesaj_clar(tmp_path):
    with pytest.raises(ValueError, match="antreneaza_tokenizer"):
        ModelGPT(**MIC_BPE, cale_tokenizer=str(tmp_path / "nu_exista.json")).antreneaza(DateMostra(propozitii=100), 0.5)
    with pytest.raises(ValueError, match="tokenizer"):
        ModelGPT(tokenizer="cuvinte")


def test_memoria_pe_simboluri_nu_vede_viitorul(tmp_path, tokenizer_mic):
    """Fiecare simbol primește codul ultimului cuvânt terminat până la el: nimic din simbolurile următoare."""
    model = ModelGPT(**MIC_BPE, cale_tokenizer=tokenizer_mic, memorie=True, adancime_memorie=4, n_emb_memorie=8, pasi_max=2)
    model.conecteaza_memorie(MemorieIerarhica(cale=biblioteca_mica(tmp_path), nivele=6))
    model.antreneaza(DateMostra(propozitii=300), 30.0)
    simboluri = model.tok.codifica("the cat ran to the horse. A cat's tail; ășț “the” cat")
    toate = model._coduri_memorie("", simboluri)
    assert len(toate) == len(simboluri)
    for t in range(1, len(simboluri) + 1):
        assert model._coduri_memorie("", simboluri[:t]) == toate[:t], f"scurgere din viitor la simbolul {t}"
    assert math.isfinite(model.biti_pentru("the cat ran."))
    assert len(model.genereaza("the cat ", 15)) == 15


def test_memoria_goala_nu_strica_nimic():
    model = ModelGPT(**MIC_MEMORIE)
    model.conecteaza_memorie(MemorieGoala())
    model.antreneaza(DateMostra(propozitii=200), 0.5)
    assert math.isfinite(model.biti_pentru("the cat sat."))
    assert len(model.genereaza("the ", 10)) == 10
