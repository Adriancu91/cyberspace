"""CONTINUUM, ALEGE: o singură nevoie pe ciclu, după urgență, nivel și ce se poate face acum (cu motiv pentru rest)."""

from __future__ import annotations

import pytest

from module.continuum import citeste_config
from module.continuum.alege import alege
from module.continuum.evalueaza import evalueaza
from module.continuum.nevoi import nevoi
from module.continuum.observa import descopera_module, observa
from teste.continuum_proba import (Lume, config_continuum, config_kronos, fisa, noaptea_3, scrie_hrana, scrie_jurnal,
                                   scrie_unelte)


@pytest.fixture
def proiect(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    scrie_unelte(tmp_path)
    return tmp_path


def alegerea(radacina, lume=None, **setari):
    config = citeste_config(config_continuum(radacina, **setari))
    stare = evalueaza(observa(config, descopera_module(config), (lume or Lume()).senzori()), config)
    return alege(nevoi(stare, config), stare, config)


def de_ce_nu(alegere):
    return {s["nevoie"]: s["de_ce_nu"] for s in alegere.sarite}


def test_in_repaus_nu_alege_nimic(proiect):
    noaptea_3(proiect, masurat=False)
    alegere = alegerea(proiect, Lume(om_minute=1))
    assert alegere.nevoie is None and alegere.plan is None
    assert de_ce_nu(alegere)["masoara:fapte+sens"] == "nivelul REPAUS nu o permite (cere ÎNTREȚINERE)"


def test_ziua_examenele_dar_nu_antrenarea(proiect):
    noaptea_3(proiect, masurat=False)
    scrie_hrana(proiect)
    alegere = alegerea(proiect, Lume(ora="12:00"))
    assert alegere.nevoie.cheie == "masoara:fapte+sens" and alegere.plan.fel == "examene"
    assert [c[1:] for c in alegere.plan.comenzi] == [["unelte/examen_fapte.py", "--experiment", "8"],
                                                    ["unelte/examen_profesor.py", "--experiment", "8"]]
    assert alegere.sarite == []  # o singură nevoie pe ciclu: restul nici nu se mai cântăresc


def test_ziua_cu_hrana_gata_nu_e_nimic_de_facut(proiect):
    noaptea_3(proiect)
    scrie_hrana(proiect)
    alegere = alegerea(proiect, Lume(ora="12:00"))
    assert alegere.nevoie is None
    motive = de_ce_nu(alegere)
    assert motive["continua:povesti"] == "nivelul ÎNTREȚINERE nu o permite (cere ÎNVĂȚARE)"
    assert motive["dezvolta:fapte"] == ("nu acum: hrana pentru fapte e gata (7.520 de povești nefolosite în date/fapte); "
                                        "antrenarea pe ea se face noaptea (ÎNVĂȚARE)")


def test_noaptea_fara_configurari_noi_spune_ce_lipseste(proiect):
    noaptea_3(proiect)
    scrie_hrana(proiect)
    alegere = alegerea(proiect)
    assert alegere.nevoie is None
    motive = de_ce_nu(alegere)
    assert motive["continua:povesti"] == (
        "capacitate_indisponibila: toate configurările potrivite sunt încheiate: config/laptop_antrenare_lunga_3.toml "
        "(8 din 8); pentru încă o noapte trebuie pregătită una nouă")
    assert motive["dezvolta:fapte"] == ("capacitate_indisponibila: nu există nicio configurare potrivită "
                                        "(config/laptop_fapte*.toml)")


def test_noaptea_alege_faptele_cand_exista_configurarea(proiect):
    noaptea_3(proiect)
    scrie_hrana(proiect)
    config_kronos(proiect, "laptop_fapte.toml", "fapte_1", date=', hrana = "date/fapte/povesti.txt"')
    alegere = alegerea(proiect)
    assert alegere.nevoie.cheie == "dezvolta:fapte" and alegere.plan.fel == "antrenare"
    assert alegere.plan.comenzi[0][1:] == ["unelte/antrenare_lunga.py", "--config", "config/laptop_fapte.toml",
                                          "--ore", "8", "--porneste-din", "8"]
    assert alegere.plan.descriere == ("antrenare lungă cu config/laptop_fapte.toml (linia fapte_1, 8 ore, din "
                                      "modelul #8)")
    assert alegere.plan.strategie == "dezvolta:fapte:antrenare" and alegere.plan.linie == "fapte_1"


def test_noaptea_continuarea_are_intaietate_fata_de_dezvoltare(proiect):
    noaptea_3(proiect)
    scrie_hrana(proiect)
    config_kronos(proiect, "laptop_fapte.toml", "fapte_1", date=', hrana = "date/fapte/povesti.txt"')
    config_kronos(proiect, "laptop_antrenare_lunga_4.toml", "antrenare_lunga_4")
    alegere = alegerea(proiect)
    assert alegere.nevoie.cheie == "continua:povesti"
    assert alegere.plan.comenzi[0][3] == "config/laptop_antrenare_lunga_4.toml"


def test_masurarea_e_prima_si_noaptea(proiect):
    noaptea_3(proiect, masurat=False)
    config_kronos(proiect, "laptop_antrenare_lunga_4.toml", "antrenare_lunga_4")
    assert alegerea(proiect).nevoie.tip == "masoara"


def test_o_linie_intrerupta_se_reia(proiect):
    noaptea_3(proiect)
    config_kronos(proiect, "laptop_antrenare_lunga_4.toml", "antrenare_lunga_4")
    examene = {"fapte_corecte": 28, "nota_profesor": 3.75}  # ca azi-noapte: toate trei examenele la fiecare oră
    scrie_jurnal(proiect, [fisa(11, "antrenare_lunga_4", 0.5048, criterii=examene),
                           fisa(12, "antrenare_lunga_4", 0.4976, criterii=examene),
                           fisa(13, "antrenare_lunga_4", 0.4880, criterii=examene)])
    alegere = alegerea(proiect)
    assert alegere.nevoie.cheie == "continua:povesti" and "(#12 → #13" in alegere.nevoie.motiv
    assert alegere.plan.descriere.endswith("reluată de la ora 4)")
    assert "--porneste-din" not in alegere.plan.comenzi[0]  # linia începută își are starea ei


def test_o_noapte_pe_fapte_intrerupta_se_reia_prin_dezvoltare(proiect):
    noaptea_3(proiect)
    scrie_hrana(proiect)
    config_kronos(proiect, "laptop_fapte.toml", "fapte_1", date=', hrana = "date/fapte/povesti.txt"')
    examene = {"fapte_corecte": 50, "nota_profesor": 4.8}
    scrie_jurnal(proiect, [fisa(11, "fapte_1", 0.4560, criterii=examene, inceput="2026-10-07T21:00:00+00:00"),
                           fisa(12, "fapte_1", 0.4559, criterii=examene, inceput="2026-10-07T22:00:00+00:00")])
    alegere = alegerea(proiect)
    assert alegere.nevoie.cheie == "dezvolta:fapte" and alegere.plan.descriere.endswith("reluată de la ora 3)")
    assert alegere.sarite == []  # „continua” nu se cere: linia întreruptă e una pe hrană, iar val_bpb nu mai scade


def test_capacitatea_indisponibila_se_sare(proiect):
    noaptea_3(proiect, masurat=False)
    alegere = alegerea(proiect, Lume(ora="12:00"), module={"model": "teste.continuum_proba:ModulSanatos",
                                                           "examene": "teste.continuum_proba:ModulSanatos"})
    assert alegere.plan.descriere == ("examenele care lipsesc pe modelul #8: fapte (sar peste sens: modulul "
                                      "„profesor” nu e în [module])")
    alegere = alegerea(proiect, Lume(ora="12:00"), module={})
    assert de_ce_nu(alegere)["masoara:fapte+sens"].startswith("capacitate_indisponibila: niciun examen nu se poate da")
