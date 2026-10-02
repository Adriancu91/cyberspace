"""Registrul refuză modulele care nu respectă regulile."""

import pytest

from nucleu.registru import EroareModul, Registru


@pytest.mark.parametrize(
    "cale,mesaj",
    [
        ("teste.module_stricate:FaraManifest", "MANIFEST"),
        ("teste.module_stricate:PortGresit", "portul"),
        ("teste.module_stricate:ContractVechi", "contractul v0"),
        ("teste.module_stricate:MetodaLipsa", "text_validare"),
        ("teste.module_stricate:NuExista", "nu există clasa"),
        ("pachet.inexistent:Clasa", "Nu pot importa"),
        ("fara_doua_puncte", "pachet.fisier:Clasa"),
    ],
)
def test_registrul_refuza_modulele_stricate(cale, mesaj):
    with pytest.raises(EroareModul, match=mesaj):
        Registru().creeaza("date", cale)


def test_port_inexistent():
    with pytest.raises(EroareModul, match="nu există"):
        Registru().creeaza("telepatie", "module.jucarii:ProfesorGol")


def test_setari_gresite_dau_mesaj_clar():
    with pytest.raises(EroareModul, match="Setări greșite"):
        Registru().creeaza("model", "module.model_ngram:ModelNgram", {"ordin": 0})
    with pytest.raises(EroareModul, match="Setări greșite"):
        Registru().creeaza("model", "module.model_ngram:ModelNgram", {"setare_inventata": 1})


def test_pune_si_ia():
    r = Registru()
    r.pune("profesor", "module.jucarii:ProfesorGol")
    assert r.ia("profesor").genereaza_exercitii("x", 1) == []
    assert r.descriere()["profesor"]["nume"] == "profesor_gol"
    with pytest.raises(EroareModul):
        r.ia("model")
