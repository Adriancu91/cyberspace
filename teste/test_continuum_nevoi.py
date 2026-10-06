"""CONTINUUM, NEVOI: doar trei în v0 (masoara, continua, dezvolta), fiecare cu motivul ei în română."""

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
    assert gasite["continua"].motiv == ("val_bpb încă scade de la o oră la alta: 0,4636 → 0,4567 (#7 → #8, linia "
                                        "antrenare_lunga_3), un câștig de 0,0069, cel puțin pragul de 0,005")
    assert gasite["dezvolta"].cheie == "dezvolta:fapte" and gasite["dezvolta"].urgenta == 3
    assert gasite["dezvolta"].motiv == ("fapte = 27% (41 din 150), cea mai slabă capacitate (sens = 47%); "
                                        "7.520 de povești nefolosite în date/fapte")


def test_examenele_lipsa_pe_ultimul_model(proiect):
    noaptea_3(proiect, masurat=False)
    masoara = nevoile(proiect)["masoara"]
    assert masoara.cheie == "masoara:fapte+sens" and masoara.urgenta == 1
    assert masoara.detalii == {"capacitati": ["fapte", "sens"], "experiment": 8}
    assert masoara.motiv == "examenele n-au mai fost date pe ultimul model păstrat (#8): lipsesc fapte, sens"


def test_continua_cand_linia_e_neterminata_desi_nu_mai_castiga(proiect):
    config_kronos(proiect, "laptop_antrenare_lunga_4.toml", "antrenare_lunga_4")
    scrie_jurnal(proiect, [fisa(1, "antrenare_lunga_4", 0.4500), fisa(2, "antrenare_lunga_4", 0.4499)])
    assert nevoile(proiect)["continua"].motiv == "antrenarea de pe linia antrenare_lunga_4 e neterminată: 2 ore din 8"
    scrie_jurnal(proiect, [fisa(i, "antrenare_lunga_4", 0.4499) for i in range(3, 9)])
    assert "continua" not in nevoile(proiect)  # terminată și fără câștig: nimic de continuat


def test_cea_mai_slaba_capacitate_fara_hrana(proiect):
    noaptea_3(proiect)
    assert nevoile(proiect)["dezvolta"].motiv.endswith("; hrana din date/fapte nu se poate citi")
    gasite = nevoile(proiect, inlocuiri={"[hrana.fapte]": "[hrana.sens]"})
    assert gasite["dezvolta"].motiv.endswith("; n-are hrană în [hrana]")


def test_ordinea_si_nevoile_neconfigurate(proiect):
    noaptea_3(proiect, masurat=False)
    gasite = nevoile(proiect, inlocuiri={'ordinea_nevoilor = ["masoara", "continua", "dezvolta"]':
                                         'ordinea_nevoilor = ["dezvolta", "masoara", "continua"]'})
    assert [(t, n.urgenta) for t, n in gasite.items()] == [("masoara", 2), ("continua", 3)]  # fapte nemăsurat: fără %
    fara_continua = nevoile(proiect, inlocuiri={"[nevoi.continua]": "[nevoi_oprite.continua]"})
    assert "continua" not in fara_continua


def test_fara_nimic_nicio_nevoie(proiect):
    assert nevoile(proiect, module={}) == {}
