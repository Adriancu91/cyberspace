"""CONTINUUM, guvernatorul: nivelul permis după oră, om și placă (fără placă video: semnale de probă)."""

from __future__ import annotations

from datetime import time as Ora
from types import SimpleNamespace

import pytest

from module.continuum import INTRETINERE, INVATARE, REPAUS, citeste_config
from module.continuum.guvernator import coboara, in_fereastra, nivel, permite, procese_grele
from teste.continuum_proba import Lume, config_continuum


@pytest.fixture
def config(tmp_path):
    return citeste_config(config_continuum(tmp_path))


def observat(lume: Lume):
    return SimpleNamespace(timp=lume.timp(), placa=lume.placa(), om=lume.om())


def test_ferestrele_trec_peste_miezul_noptii():
    noaptea, ziua = (Ora(22), Ora(7)), (Ora(7), Ora(22))
    assert in_fereastra(Ora(23, 30), noaptea) and in_fereastra(Ora(6, 59), noaptea)
    assert not in_fereastra(Ora(7), noaptea) and in_fereastra(Ora(7), ziua)
    assert in_fereastra(Ora(12), ziua) and not in_fereastra(Ora(22), ziua)


def test_nivelurile_se_permit_in_ordine():
    assert permite(INVATARE, INTRETINERE) and permite(INTRETINERE, INTRETINERE)
    assert not permite(INTRETINERE, INVATARE) and not permite(REPAUS, INTRETINERE)
    assert coboara(INVATARE) == INTRETINERE and coboara(REPAUS) == REPAUS


def test_noaptea_cu_placa_libera_si_omul_plecat_e_invatare(config):
    ales, motiv = nivel(observat(Lume(ora="23:30")), config)
    assert ales == INVATARE
    assert "fereastra de învățare (22:00–07:00)" in motiv and "5.800 MB liberi" in motiv and "de 60 min" in motiv
    assert motiv.endswith("; azi 0,0 ore pe placă din 20")  # v1: bugetul zilnic, din jurnal (aici, fără fișe)


def test_ziua_e_intretinere(config):
    assert nivel(observat(Lume(ora="12:00")), config)[0] == INTRETINERE


def test_omul_la_laptop_inseamna_repaus(config):
    ales, motiv = nivel(observat(Lume(ora="23:30", om_minute=2)), config)
    assert ales == REPAUS and motiv.startswith("omul folosește laptopul")


def test_fara_semnal_de_la_om_nu_blocheaza(config):
    ales, motiv = nivel(observat(Lume(ora="23:30", om_minute=None)), config)
    assert ales == INVATARE and "nu pot vedea dacă omul folosește laptopul" in motiv


def test_o_singura_sarcina_grea_pe_placa(config):
    antrenarea = [{"pid": 14844, "nume": r"C:\Python312\python.exe"}]
    ales, motiv = nivel(observat(Lume(ora="23:30", procese=antrenarea)), config)
    assert ales == REPAUS and "ocupată" in motiv and "python.exe (14844)" in motiv
    # Un program obișnuit pe placă (ex. WPS Office) nu e o sarcină grea.
    birou = [{"pid": 22612, "nume": r"C:\Users\XyZ\AppData\Local\Kingsoft\WPS Office\office6\et.exe"}]
    assert procese_grele({"procese": birou}, ["python"]) == []
    assert nivel(observat(Lume(ora="23:30", procese=birou)), config)[0] == INVATARE


def test_memorie_video_putina_sau_placa_necitita_inseamna_repaus(config):
    ales, motiv = nivel(observat(Lume(ora="23:30", libera_mb=3692)), config)
    assert ales == REPAUS and "3.692 MB" in motiv
    ales, motiv = nivel(observat(Lume(ora="23:30", placa_citita=False)), config)
    assert ales == REPAUS and "nu pot citi placa" in motiv


def test_placa_fierbinte_coboara_un_nivel(config):
    ales, motiv = nivel(observat(Lume(ora="23:30", temperatura=87)), config)
    assert ales == INTRETINERE and "peste 85 °C" in motiv
    assert nivel(observat(Lume(ora="12:00", temperatura=87)), config)[0] == REPAUS


def test_in_afara_ferestrelor_e_repaus(tmp_path):
    config = citeste_config(config_continuum(tmp_path, inlocuiri={'"07:00-22:00"': '"09:00-21:00"'}))
    ales, motiv = nivel(observat(Lume(ora="08:00")), config)
    assert ales == REPAUS and "în afara ferestrelor" in motiv
