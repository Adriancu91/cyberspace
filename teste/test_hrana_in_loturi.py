"""Hrana în loturi: o fracție din bucățile fiecărui lot vine dintr-un text în plus (ex. poveștile cu fapte), restul din
textul de antrenare. Fără hrană, antrenarea e exact ca înainte."""

from __future__ import annotations

import pytest

torch = pytest.importorskip("torch")

from module.model_continuu import ModelGPTContinuu  # noqa: E402
from module.model_gpt import ModelGPT  # noqa: E402
from teste.test_model_plasa_mare import MIC, TEXT, _Date, tokenizer_mic  # noqa: E402, F401  (tokenizer_mic: fixture)

HRANA = "Birds have feathers. Water freezes when it is cold. The sun is a star. " * 40


@pytest.fixture
def hrana(tmp_path):
    cale = tmp_path / "povesti.txt"
    cale.write_text(HRANA, encoding="utf-8")
    return str(cale)


def test_lotul_ia_pe_rand_2_sau_3_bucati_din_hrana():
    model = ModelGPT(**{**MIC, "lot": 24}, hrana="x.txt", fractie_hrana=0.1)
    pasi = [model.bucati_din_hrana(p) for p in range(10)]
    assert pasi[:5] == [2, 2, 3, 2, 3] and sum(pasi) == 24  # 10 loturi × 24 × 10% = 24: media e exact 10%


def test_antrenarea_cu_hrana_numara_bucatile(tokenizer_mic, hrana):
    model = ModelGPT(**{**MIC, "lot": 10}, tokenizer="bpe", cale_tokenizer=tokenizer_mic, pasi_max=6, hrana=hrana,
                     fractie_hrana=0.1)
    statistici = model.antreneaza(_Date(TEXT), 60.0)
    assert statistici["pasi"] == 6 and statistici["secvente_hrana"] == 6 and statistici["secvente_total"] == 60
    assert statistici["simboluri_hrana"] > 0


def test_fara_hrana_totul_e_ca_inainte(tokenizer_mic):
    def antreneaza():
        model = ModelGPT(**MIC, tokenizer="bpe", cale_tokenizer=tokenizer_mic, pasi_max=4)
        statistici = model.antreneaza(_Date(TEXT), 60.0)
        return statistici, model.biti_pentru(TEXT[:200])

    (statistici, biti), (_, biti_din_nou) = antreneaza(), antreneaza()
    assert "secvente_hrana" not in statistici and biti == biti_din_nou  # aceleași loturi, același model


def test_continuarea_numara_de_la_primul_pas_al_modelului(tmp_path, tokenizer_mic, hrana):
    setari = dict(**{**MIC, "lot": 24}, tokenizer="bpe", cale_tokenizer=tokenizer_mic, pasi_max=3, hrana=hrana,
                  fractie_hrana=0.1, cale_stare=str(tmp_path / "gpt.pt"))
    primul = ModelGPTContinuu(**setari)
    assert primul.antreneaza(_Date(TEXT), 60.0)["secvente_hrana"] == 2 + 2 + 3
    primul.dupa_examen({"scor": 3.0})  # starea se salvează: experimentul următor continuă
    al_doilea = ModelGPTContinuu(**setari)
    assert al_doilea.antreneaza(_Date(TEXT), 60.0)["secvente_hrana"] == 2 + 3 + 2  # pașii 3, 4, 5 ai modelului


@pytest.mark.parametrize("setari", [{"hrana": "x.txt"}, {"fractie_hrana": 0.1}, {"hrana": "x.txt", "fractie_hrana": 1.0},
                                    {"hrana": "x.txt", "fractie_hrana": 0.1, "memorie": True},
                                    {"povesti_profesor": 1}])
def test_setari_gresite(setari):
    with pytest.raises(ValueError):
        ModelGPT(**MIC, **setari)
