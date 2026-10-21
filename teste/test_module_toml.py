"""Descrierile `module/manifeste/<nume>.toml` (formatul comun modul-v0 din Cyber Hub) nu se desincronizează de MANIFEST."""

from __future__ import annotations

import importlib
import tomllib

import pytest

from unelte import module_toml as mt

MODULE = mt.descopera()


def _citeste(nume: str, radacina=mt.RADACINA) -> dict:
    return tomllib.loads((mt.dosar_manifeste(radacina) / f"{nume}.toml").read_text(encoding="utf-8"))


def test_gaseste_toate_modulele():
    assert len(MODULE) >= 24
    assert "module.examen_bpb:ExamenBpb" in {m.intrare for m in MODULE}


@pytest.mark.parametrize("modul", MODULE, ids=lambda m: m.intrare)
def test_fisierul_coincide_cu_manifest(modul):
    try:  # MANIFEST-ul adevărat, din clasă (dacă se poate importa), nu doar cel citit cu ast
        manifest = getattr(importlib.import_module(modul.pachet), modul.clasa).MANIFEST
    except ImportError:
        manifest = modul.manifest
    t = _citeste(str(manifest["nume"]))
    assert t["modul"]["nume"] == manifest["nume"]
    assert t["modul"]["versiune"] == manifest["versiune"]
    assert t["contract"]["port"] == manifest["port"]
    assert t["contract"]["versiune_contract"] == str(manifest["versiune_contract"])
    assert t["modul"]["proiect"] == "kronos" and t["modul"]["format"] == "modul-v0"
    assert t["modul"]["descriere"] and mt.DE_COMPLETAT not in t["modul"]["descriere"]
    assert t["rulare"] == {"limbaj": "python", "intrare": modul.intrare, "teste": mt.comanda_teste(modul)}
    assert isinstance(t["depinde"], dict) and isinstance(t["ofera"], dict) and t["ofera"]


def test_totul_e_la_zi():
    assert mt.probleme() == []


def _radacina_mica(tmp_path, versiune="0.1.0"):
    (tmp_path / "module").mkdir(exist_ok=True)
    (tmp_path / "teste").mkdir(exist_ok=True)
    (tmp_path / "module" / "baza.py").write_text(
        f'class Baza:\n    MANIFEST = {{"nume": "baza", "port": "model", "versiune": "{versiune}", "versiune_contract": 1}}\n',
        encoding="utf-8")
    (tmp_path / "module" / "urmas.py").write_text(
        "from module.baza import Baza\n\n\nclass Urmas(Baza):\n"
        '    MANIFEST = {"nume": "urmas", "port": "model", "versiune": "0.2.0", "versiune_contract": 1}\n',
        encoding="utf-8")
    return tmp_path


def test_unealta_scrie_si_pastreaza_ce_a_completat_omul(tmp_path):
    r = _radacina_mica(tmp_path)
    assert len(mt.scrie(r)) == 2
    assert _citeste("urmas", r)["depinde"] == {"baza": ">=0.1.0"}
    assert "antreneaza" in _citeste("baza", r)["ofera"]
    assert any("DE COMPLETAT" in p for p in mt.probleme(r))  # descrierea încă necompletată

    cale = mt.dosar_manifeste(r) / "baza.toml"
    text = cale.read_text(encoding="utf-8").replace('"DE COMPLETAT"', '"Modelul de bază."')
    cale.write_text(text.replace("\n[ofera]\n", '\n[ofera]\n"extra" = "ceva scris de om"\n'), encoding="utf-8")

    _radacina_mica(tmp_path, versiune="0.3.0")  # MANIFEST-ul se schimbă
    assert "baza.toml nu e la zi cu MANIFEST-ul" in mt.probleme(r)
    mt.scrie(r)
    t = _citeste("baza", r)
    assert t["modul"]["versiune"] == "0.3.0"
    assert t["modul"]["descriere"] == "Modelul de bază."
    assert t["ofera"]["extra"] == "ceva scris de om"


def test_unealta_semnaleaza_fisier_fara_clasa(tmp_path):
    r = _radacina_mica(tmp_path)
    mt.scrie(r)
    (mt.dosar_manifeste(r) / "disparut.toml").write_text("", encoding="utf-8")
    assert "disparut.toml nu mai are clasă cu MANIFEST" in mt.probleme(r)
    assert mt.main(["--verifica", "--radacina", str(r)]) == 1
