"""Memoria ierarhică: coduri corecte, plasa ține minte drumurile, iar modelul nu primește viitorul."""

from __future__ import annotations

import pytest

from module.memorie_ierarhica import FARA_CUVANT, NECUNOSCUT, PRIMUL_COD, MemorieIerarhica
from teste.biblioteca_mica import scrie_biblioteca


@pytest.fixture
def memorie(tmp_path):
    return MemorieIerarhica(cale=scrie_biblioteca(tmp_path), nivele=6)


def test_codul_unui_cuvant_e_locul_lui_in_biblioteca(memorie):
    assert memorie.cod("horse") == tuple(PRIMUL_COD + x for x in [1, 2, 1, 1, 1]) + (FARA_CUVANT,)
    assert memorie.cod("HORSE") == memorie.cod("horse")


def test_cuvintele_inrudite_impart_inceputul_codului(memorie):
    cal, pisica, sabie = memorie.cod("horse"), memorie.cod("cat"), memorie.cod("sword")
    assert cal[:4] == pisica[:4]  # același raft (animal), aceleași categorii de sus
    assert cal[4] != pisica[4]
    assert cal[1] != sabie[1]  # rafturi diferite


@pytest.mark.parametrize("forma", ["horses", "horse's", "swords", "running", "runneth"])
def test_formele_flexionate_ajung_la_cuvantul_de_baza(memorie, forma):
    assert memorie.cod(forma)[0] != NECUNOSCUT


def test_cuvant_necunoscut(memorie):
    assert memorie.cod("thee")[0] == NECUNOSCUT


def test_cauta_arata_drumul_si_relatiile(memorie):
    sens = memorie.cauta("horses")[0]
    assert sens["drum"] == ["entity", "animal", "horse"]
    assert sens["raft"] == "noun.animal"
    assert {"tip": "are_membru", "catre": "cat"} in sens["relatii"]
    assert memorie.cauta("thee") == []


def test_plasa_tine_minte_drumurile(memorie):
    memorie.caracteristici("the horse and the horse and the cat ")
    stat = memorie.statistici()
    assert stat["cautari"] == 8
    assert stat["drumuri_in_plasa"] == 4  # the, horse, and, cat
    assert stat["cele_mai_folosite"][0] in ("the", "horse", "and")
    assert stat["acoperire"] == pytest.approx(3 / 8)


def test_un_cod_pe_fiecare_litera(memorie):
    text = "a horse ran, a cat ran.\n"
    assert len(memorie.caracteristici(text)) == len(text)


def test_memoria_nu_dezvaluie_viitorul(memorie):
    """Cel mai important test: codul de la litera i depinde DOAR de literele 0..i.

    Dacă ar depinde de ce urmează (de ex. cuvântul în curs de scriere), modelul ar trișa la examen.
    """
    text = "the horse ran to the sword. A cat, horses'! run running\nhorse"
    complet = memorie.caracteristici(text)
    for i in range(1, len(text) + 1):
        assert memorie.caracteristici(text[:i]) == complet[:i], f"scurgere din viitor la poziția {i}"


def test_cuvantul_intra_doar_dupa_ce_s_a_terminat(memorie):
    text = "horse "
    coduri = memorie.caracteristici(text)
    assert all(c[0] == FARA_CUVANT for c in coduri[:5])  # „horse” încă nu e terminat
    assert coduri[5] == memorie.cod("horse")  # la spațiu, cuvântul e complet


def test_lipsa_bibliotecii_da_mesaj_clar(tmp_path):
    with pytest.raises(ValueError, match="construieste_biblioteca"):
        MemorieIerarhica(cale=str(tmp_path / "nu_exista.json.gz"))


def test_gpt_cu_memorie_invata_si_se_reincarca(tmp_path, memorie):
    pytest.importorskip("torch")
    from module.date_mostra import DateMostra
    from module.model_gpt import ModelGPT

    setari = dict(n_straturi=1, n_capete=2, n_emb=32, context=32, lot=8, dispozitiv="cpu", memorie=True, adancime_memorie=4)
    date = DateMostra(propozitii=300)
    model = ModelGPT(**setari)
    model.conecteaza_memorie(memorie)
    statistici = model.antreneaza(date, 2.0)
    assert statistici["parametri_memorie"] > 0
    biti = model.biti_pentru("the cat sat on the mat.")
    assert len(model.genereaza("the cat ", 20)) == 20

    copie = ModelGPT(dispozitiv="cpu")
    copie.conecteaza_memorie(memorie)
    copie.incarca(model.salveaza(str(tmp_path / "m")))
    assert copie.foloseste_memorie
    assert copie.biti_pentru("the cat sat on the mat.") == pytest.approx(biti, rel=1e-4)


def test_gpt_cu_memorie_fara_port_conectat_da_mesaj_clar():
    pytest.importorskip("torch")
    from module.date_mostra import DateMostra
    from module.model_gpt import ModelGPT

    model = ModelGPT(n_straturi=1, n_capete=2, n_emb=32, context=32, dispozitiv="cpu", memorie=True)
    with pytest.raises(RuntimeError, match="memorie"):
        model.antreneaza(DateMostra(propozitii=100), 1.0)
