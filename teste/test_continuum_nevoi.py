"""CONTINUUM, NEVOI: masoara, continua și dezvolta (v0), plus repara și remasoara (v1), fiecare cu motivul ei în
română. Testele v1 punct cu punct sunt în test_continuum_v1.py."""

from __future__ import annotations

import pytest

from module.continuum import citeste_config
from module.continuum.evalueaza import evalueaza
from module.continuum.nevoi import nevoi
from module.continuum.observa import descopera_module, observa
from teste.continuum_proba import (Lume, config_continuum, config_kronos, fisa, noaptea_3, scrie_hrana, scrie_jurnal)


@pytest.fixture
def proiect(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path


def nevoile(radacina, **setari):
    config = citeste_config(config_continuum(radacina, **setari))
    stare = evalueaza(observa(config, descopera_module(config), Lume().senzori()), config)
    return {n.tip: n for n in nevoi(stare, config)}


def test_dupa_noaptea_a_treia(proiect):
    noaptea_3(proiect)
    scrie_hrana(proiect)
    gasite = nevoile(proiect)
    assert list(gasite) == ["continua", "dezvolta"]  # ultimul model e măsurat: nu trebuie examene
    assert gasite["continua"].motiv == ("val_bpb încă scade: în ultima oră 0,4636 → 0,4567 (#7 → #8, linia "
                                        "antrenare_lunga_3), un câștig de 0,0069, peste pragul de 0,005; pe ultimele 3 "
                                        "ore tendința e bună (0,0102 pe oră)")
    # urgența: repara 1, masoara 2, remasoara 3, continua 4, dezvolta 5
    assert gasite["dezvolta"].cheie == "dezvolta:fapte" and gasite["dezvolta"].urgenta == 5
    assert gasite["dezvolta"].motiv == ("fapte = 27% (41 din 150), cea mai slabă capacitate (sens = 47%); "
                                        "7.520 de povești nefolosite în date/fapte")


def test_examenele_lipsa_pe_ultimul_model(proiect):
    noaptea_3(proiect, masurat=False)
    masoara = nevoile(proiect)["masoara"]
    assert masoara.cheie == "masoara:fapte+sens" and masoara.urgenta == 2  # „repara” e mereu prima
    assert masoara.detalii == {"capacitati": ["fapte", "sens"], "experiment": 8}
    assert masoara.motiv == "examenele n-au mai fost date pe ultimul model păstrat (#8): lipsesc fapte, sens"


def test_o_linie_neterminata_fara_castig_nu_se_mai_continua(proiect):
    """v1 (punctul 6): în v0, o linie neterminată se continua oricum; acum doar cu câștig peste prag și tendință bună."""
    config_kronos(proiect, "laptop_antrenare_lunga_4.toml", "antrenare_lunga_4")
    scrie_jurnal(proiect, [fisa(1, "antrenare_lunga_4", 0.4500), fisa(2, "antrenare_lunga_4", 0.4499)])
    assert "continua" not in nevoile(proiect)


def test_cea_mai_slaba_capacitate_fara_hrana(proiect):
    noaptea_3(proiect)
    assert nevoile(proiect)["dezvolta"].motiv.endswith("; hrana din date/fapte nu se poate citi")
    gasite = nevoile(proiect, inlocuiri={"[hrana.fapte]": "[hrana.sens]"})
    assert gasite["dezvolta"].motiv.endswith("; n-are hrană în [hrana]")


def test_ordinea_si_nevoile_neconfigurate(proiect):
    noaptea_3(proiect, masurat=False)
    gasite = nevoile(proiect, inlocuiri={'ordinea_nevoilor = ["masoara", "continua", "dezvolta"]':
                                         'ordinea_nevoilor = ["dezvolta", "masoara", "continua"]'})
    # repara 1, dezvolta 2, masoara 3, remasoara 4, continua 5; fapte nemăsurat: fără %, deci fără „dezvolta”
    assert [(t, n.urgenta) for t, n in gasite.items()] == [("masoara", 3), ("continua", 5)]
    fara_continua = nevoile(proiect, inlocuiri={"[nevoi.continua]": "[nevoi_oprite.continua]"})
    assert "continua" not in fara_continua


def test_fara_nimic_nicio_nevoie(proiect):
    assert nevoile(proiect, module={}) == {}
