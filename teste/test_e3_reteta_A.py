"""Pragurile S42 (docs/preinregistrari/2026-10-28_E3_reteta_A2.md), fără placă."""

from unelte.e3_reteta_A import verdict


def test_confirmat_cand_castiga_5_si_nu_uita():
    assert verdict(71, 66, 67, 69, 37, 39)["verdict"] == "CONFIRMAT"


def test_neclar_cand_castiga_5_dar_uita():
    assert verdict(71, 66, 66, 69, 39, 39)["verdict"] == "NECLAR"
    assert verdict(71, 66, 69, 69, 36, 39)["verdict"] == "NECLAR"


def test_neclar_intre_praguri():
    assert verdict(68, 66, 69, 69, 39, 39)["verdict"] == "NECLAR"
    assert verdict(70, 66, 69, 69, 39, 39)["verdict"] == "NECLAR"


def test_infirmat_la_plus_unu_sau_mai_putin():
    assert verdict(67, 66, 70, 69, 40, 39)["verdict"] == "INFIRMAT"
    assert verdict(60, 66, 70, 69, 40, 39)["verdict"] == "INFIRMAT"
    assert verdict(67, 66, 70, 69, 40, 39)["diferenta"] == 1
