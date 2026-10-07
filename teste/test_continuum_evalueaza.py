"""CONTINUUM, EVALUEAZĂ: liniile de bază doar din experimente păstrate, scorul curent, tendința, hrana, modulele."""

from __future__ import annotations

from datetime import datetime

import pytest

from module.continuum import INVATARE, citeste_config
from module.continuum.evalueaza import evalueaza
from module.continuum.observa import descopera_module, observa
from teste.continuum_proba import (Lume, config_continuum, config_kronos, fisa, fisa_unealta, noaptea_3, scrie_hrana,
                                   scrie_jurnal)


@pytest.fixture
def proiect(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path


def stare_din(radacina, module=None, lume=None):
    config = citeste_config(config_continuum(radacina, module=module))
    return evalueaza(observa(config, descopera_module(config), (lume or Lume()).senzori()), config)


def test_noaptea_a_treia(proiect):
    noaptea_3(proiect)
    stare = stare_din(proiect)
    assert stare.nivel == INVATARE and stare.ultimul_id == 10
    assert stare.ultimul_model == {"experiment": 8, "linie": "antrenare_lunga_3",
                                   "arhitectura": {"n_straturi": 10, "n_capete": 8, "n_emb": 512, "context": 256}}
    povesti, fapte, sens = (stare.capacitati[n] for n in ("povesti", "fapte", "sens"))
    assert (povesti.curent, povesti.linie_de_baza, povesti.experiment_baza) == (0.4567, 0.4567, 8)
    assert (fapte.curent, fapte.procent, fapte.experiment_baza) == (41, 27.3, 8)  # din fișa uneltei de examen
    assert (sens.curent, sens.procent) == (4.7, 47.0)
    assert all(c.disponibila and not c.degradata for c in stare.capacitati.values())
    assert stare.tendinta["castig"] == pytest.approx(0.0069) and stare.tendinta["de_la"]["experiment"] == 7
    linie = stare.linii["config/laptop_antrenare_lunga_3.toml"]
    assert (linie["ore_facute"], linie["ore_planificate"], linie["terminata"], linie["urmarita"]) == (8, 8, True, True)


def test_linia_de_baza_doar_din_experimente_pastrate_si_linii_urmarite(proiect):
    noaptea_3(proiect)
    scrie_jurnal(proiect, [fisa(11, "antrenare_lunga_3", 0.40, decizie="respins"),   # mai bun, dar respins
                           fisa(12, "bucla_gpt", 0.30),                              # altă linie, alt examen
                           fisa(13, "antrenare_lunga_3", 0.48, criterii={"fapte_corecte": 30})])
    stare = stare_din(proiect)
    povesti, fapte = stare.capacitati["povesti"], stare.capacitati["fapte"]
    assert (povesti.linie_de_baza, povesti.experiment_baza, povesti.curent) == (0.4567, 8, 0.48)
    assert povesti.degradata  # 0,48 e mai rău decât 0,4567 cu mai mult decât pragul de 0,02
    assert (fapte.linie_de_baza, fapte.curent, fapte.degradata) == (41, 30, True)  # din criteriile orei
    assert stare.capacitati["sens"].curent is None  # nemăsurat pe ultimul model
    assert stare.tendinta["castig"] == pytest.approx(0.40 - 0.48)  # între ultimele două ore reușite (#11 → #13)


def test_hrana_folosita_si_nefolosita(proiect):
    noaptea_3(proiect)
    scrie_hrana(proiect)
    assert stare_din(proiect).hrana["fapte"] | {"schimbata": None} == {
        "stare": "ok", "dosar": "date/fapte", "povesti": 7520, "scrise": 9000, "schimbata": None, "folosita_de": [],
        "nefolosita": True, "destula": True, "minima": 5000}
    config_kronos(proiect, "laptop_fapte.toml", "fapte_1", date=', hrana = "date/fapte/povesti.txt"')
    scrie_jurnal(proiect, [fisa(11, "fapte_1", 0.45, inceput="2026-10-07T20:00:00+00:00")])
    hrana = stare_din(proiect).hrana["fapte"]
    assert hrana["folosita_de"] == ["fapte_1"] and not hrana["nefolosita"]
    scrie_hrana(proiect, povesti=9400, scrise=11000, schimbata=datetime(2026, 10, 8, 12, 0))  # hrană nouă, după
    hrana = stare_din(proiect).hrana["fapte"]
    assert hrana["nefolosita"] and hrana["povesti"] == 9400


def test_capacitatile_depind_de_modulele_lor(proiect):
    noaptea_3(proiect)
    stare = stare_din(proiect, module={"model": "teste.continuum_proba:ModulSanatos"})
    assert stare.capacitati["povesti"].disponibila
    assert stare.capacitati["fapte"].motiv_indisponibila == "modulul „examene” nu e în [module]"
    stare = stare_din(proiect, module={"model": "teste.continuum_proba:ModulSanatos",
                                       "examene": "teste.continuum_proba:ModulDegradat",
                                       "profesor": "teste.nu_exista:Profesor"})
    assert stare.capacitati["fapte"].disponibila  # degradat: încă merge
    assert not stare.capacitati["sens"].disponibila and "indisponibil" in stare.capacitati["sens"].motiv_indisponibila


def test_fara_jurnal_si_fara_module(proiect):
    stare = stare_din(proiect, module={})
    assert stare.ultimul_model is None and stare.tendinta is None and stare.ultimul_id == 0
    assert all(c.curent is None and not c.disponibila for c in stare.capacitati.values())
    rezumat = stare.rezumat()
    assert rezumat["nivel"] == INVATARE and set(rezumat["capacitati"]) == {"povesti", "fapte", "sens"}


def test_o_singura_ora_n_are_tendinta(proiect):
    config_kronos(proiect, "laptop_antrenare_lunga_4.toml", "antrenare_lunga_4")
    scrie_jurnal(proiect, [fisa(1, "antrenare_lunga_4", 0.5048)])
    stare = stare_din(proiect)
    assert stare.tendinta["castig"] is None and stare.tendinta["la"] == {"experiment": 1, "valoare": 0.5048}
    assert not stare.linii["config/laptop_antrenare_lunga_4.toml"]["terminata"]
    scrie_jurnal(proiect, [fisa_unealta(2, "examen_profesor", 1, {"nota_medie": 3.55})])
    assert stare_din(proiect).capacitati["sens"].curent == 3.55


def test_masurarea_cu_unealta_e_mai_noua_decat_cea_de_la_ora(proiect):
    config_kronos(proiect, "laptop_antrenare_lunga_4.toml", "antrenare_lunga_4")
    scrie_jurnal(proiect, [fisa(1, "antrenare_lunga_4", 0.4389, criterii={"nota_profesor": 4.5}),
                           fisa_unealta(2, "examen_profesor", 1, {"nota_medie": 4.4, "povesti": 40})])
    assert stare_din(proiect).capacitati["sens"].curent == 4.4  # pe 40 de povești, după oră
