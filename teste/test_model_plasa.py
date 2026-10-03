"""Plasa de noduri: fiecare simbol merge la nodul potrivit, fără viitor; la început e identică cu GPT-ul."""

from __future__ import annotations

import math

import pytest

torch = pytest.importorskip("torch")

from module.date_mostra import DateMostra  # noqa: E402
from module.memorie_ierarhica import MemorieIerarhica  # noqa: E402
from module.model_gpt import ModelGPT  # noqa: E402
from module.model_plasa import NUME_NODURI, REZERVA, ModelPlasa, nod_pentru_raft  # noqa: E402
from module.tokenizer_bpe import antreneaza_bpe  # noqa: E402
from teste.biblioteca_mica import biblioteca_mica  # noqa: E402

MIC = dict(n_straturi=1, n_capete=2, n_emb=32, context=32, lot=8, dispozitiv="cpu", n_ascuns_nod=16)


@pytest.fixture
def tokenizer_mic(tmp_path):
    cale = tmp_path / "bpe_mic.json"
    antreneaza_bpe(DateMostra(propozitii=600).text_antrenare(), 320).salveaza(cale)
    return str(cale)


@pytest.fixture
def memorie(tmp_path):
    return MemorieIerarhica(cale=biblioteca_mica(tmp_path), nivele=6)


def _nod(nume: str) -> int:
    return NUME_NODURI.index(nume)


def test_rafturile_merg_la_grupurile_cerute():
    assert nod_pentru_raft("noun.animal") == _nod("fiinte") == nod_pentru_raft("noun.person")
    assert nod_pentru_raft("noun.artifact") == _nod("locuri_obiecte") == nod_pentru_raft("noun.location")
    assert nod_pentru_raft("verb.motion") == _nod("actiuni") == nod_pentru_raft("verb.emotion")
    assert nod_pentru_raft("adj.all") == _nod("insusiri") == nod_pentru_raft("adv.all")
    assert nod_pentru_raft("noun.group") == REZERVA  # rafturile nepuse în alt grup


def test_fiecare_cuvant_merge_la_nodul_raftului_lui(memorie, tokenizer_mic):
    model = ModelPlasa(**MIC, cale_tokenizer=tokenizer_mic)
    model.conecteaza_memorie(memorie)
    asteptat = {
        "horse": "fiinte", "cat": "fiinte", "sword": "locuri_obiecte", "gallop": "actiuni", "ran": "actiuni",
        "good": "insusiri", "bad": "insusiri", "o'clock": "insusiri", "herd": "rezerva", "thee": "rezerva",
    }
    for cuvant, nod in asteptat.items():
        assert model._nod(memorie.cod(cuvant)) == _nod(nod), cuvant


def test_drumul_simbolurilor_nu_vede_viitorul(memorie, tokenizer_mic):
    model = ModelPlasa(**MIC, cale_tokenizer=tokenizer_mic, pasi_max=1)
    model.conecteaza_memorie(memorie)
    model.antreneaza(DateMostra(propozitii=200), 30.0)
    simboluri = model.tok.codifica("the horse ran to the good cat. A sword! “the” herd")
    toate = model._pozitii("", simboluri)
    assert toate.shape == (len(simboluri), 1)
    for t in range(1, len(simboluri) + 1):
        assert torch.equal(model._pozitii("", simboluri[:t]), toate[:t]), f"scurgere din viitor la simbolul {t}"


def test_la_inceput_e_identic_cu_gpt_ul(memorie, tokenizer_mic):
    """Nodurile pornesc tăcute: neantrenată, plasa dă exact ce dă GPT-ul simplu, cu aceeași sămânță."""
    date = DateMostra(propozitii=300)
    setari = {k: v for k, v in MIC.items() if k != "n_ascuns_nod"}
    gpt = ModelGPT(**setari, tokenizer="bpe", cale_tokenizer=tokenizer_mic)
    plasa = ModelPlasa(**MIC, cale_tokenizer=tokenizer_mic)
    plasa.conecteaza_memorie(memorie)
    assert gpt.antreneaza(date, 0.0)["pasi"] == 0 and plasa.antreneaza(date, 0.0)["pasi"] == 0
    text = "the cat ran to the horse. a good sword."
    assert plasa.biti_pentru(text) == pytest.approx(gpt.biti_pentru(text), rel=1e-6)


def test_invata_si_se_reincarca(tmp_path, memorie, tokenizer_mic):
    model = ModelPlasa(**MIC, cale_tokenizer=tokenizer_mic)
    model.conecteaza_memorie(memorie)
    statistici = model.antreneaza(DateMostra(propozitii=300), 1.5)
    assert statistici["pasi"] > 0
    assert set(statistici["noduri"]) == set(NUME_NODURI) and sum(statistici["noduri"].values()) == pytest.approx(1)
    assert statistici["noduri"]["fiinte"] > 0 and statistici["noduri"]["actiuni"] > 0  # „cat”, „ran” din propoziții
    text = "the cat sat on the mat."
    biti = model.biti_pentru(text)
    assert math.isfinite(biti)
    assert len(model.genereaza("the cat ", 20)) == 20

    copie = ModelPlasa(dispozitiv="cpu", cale_tokenizer=tokenizer_mic)
    copie.conecteaza_memorie(memorie)
    copie.incarca(model.salveaza(str(tmp_path / "model")))
    assert copie.n_ascuns_nod == 16
    assert copie.biti_pentru(text) == pytest.approx(biti, rel=1e-5)


def test_fara_memorie_totul_merge_la_rezerva(tokenizer_mic):
    model = ModelPlasa(**MIC, cale_tokenizer=tokenizer_mic)
    statistici = model.antreneaza(DateMostra(propozitii=200), 0.5)
    assert statistici["noduri"]["rezerva"] == 1.0
    assert math.isfinite(model.biti_pentru("the cat."))
