"""Regula 4, criteriul principal: un criteriu marcat principal = true hotărăște; scorul examenului (val_bpb) devine un
criteriu ca celelalte, cu pragul prag_zgomot. Fără „principal”, totul e ca înainte (vezi teste/test_criterii.py)."""

from __future__ import annotations

import pytest

from kronos.config import EroareConfig
from kronos.contracte import Propunere
from kronos.orchestrator import Orchestrator
from teste.test_criterii import CRITERII, _config, _propune

# În config/proba.toml, prag_zgomot = 0.002: atât poate scădea val_bpb când nu mai e el principalul.
PRINCIPAL = """
[criterii.fapte_corecte]
mai_mare_e_mai_bine = true
prag = 10
principal = true

[criterii.nota_profesor]
mai_mare_e_mai_bine = true
prag = 0.5
"""


def test_principalul_hotaraste_chiar_daca_val_bpb_nu_e_mai_bun(tmp_path, monkeypatch):
    o = Orchestrator(_config(tmp_path, monkeypatch, PRINCIPAL))
    assert o.config.criteriu_principal() == "fapte_corecte"
    prima = o.experiment(Propunere("punct de plecare"))  # primul din linie: păstrat, ca înainte
    assert prima["decizie"] == "pastrat"
    a_doua = o.experiment(_propune(fapte=25, biti=5.001))  # +15 fapte (peste 10); val_bpb scade cu 0,001 ≤ 0,002
    assert a_doua["decizie"] == "pastrat" and a_doua["castig_principal"] == 15 and "model_salvat" in a_doua
    assert o.cel_mai_bun["id"] == a_doua["id"]
    a_treia = o.experiment(_propune(fapte=30, biti=4.0))  # val_bpb mult mai bun, dar faptele cresc doar cu 5
    assert a_treia["decizie"] == "respins" and a_treia["motiv"] == (
        f"criteriul principal fapte_corecte: 30 față de 25 la #{a_doua['id']} (câștig +5, trebuie peste 10)")
    egal = o.experiment(_propune(fapte=35, biti=5.001))  # exact pragul (10) nu ajunge: trebuie PESTE prag
    assert egal["decizie"] == "respins" and egal["castig_principal"] == 10


def test_principalul_mai_bun_dar_alt_criteriu_cade(tmp_path, monkeypatch):
    o = Orchestrator(_config(tmp_path, monkeypatch, PRINCIPAL))
    prima = o.experiment(Propunere("punct de plecare"))  # val_bpb 5, fapte 10, nota 5
    val_bpb = o.experiment(_propune(fapte=40, biti=5.01))  # faptele +30, dar val_bpb scade cu 0,01 (pragul 0,002)
    assert val_bpb["decizie"] == "respins" and val_bpb["motiv"] == (
        f"a pierdut val_bpb: 5.01 față de 5 la #{prima['id']} (a scăzut cu 0.01, pragul e 0.002)")
    nota = o.experiment(_propune(fapte=40, nota=4.0))  # nota scade cu 1 (pragul 0,5)
    assert nota["decizie"] == "respins" and nota["motiv"] == (
        f"a pierdut nota_profesor: 4 față de 5 la #{prima['id']} (a scăzut cu 1, pragul e 0.5)")
    assert o.cel_mai_bun["id"] == prima["id"]


def test_referinta_e_cel_mai_bun_dupa_principal_si_la_reluare(tmp_path, monkeypatch):
    o = Orchestrator(_config(tmp_path, monkeypatch, PRINCIPAL))
    o.experiment(Propunere("punct de plecare"))  # val_bpb 5, fapte 10
    al_doilea = o.experiment(_propune(fapte=25, biti=5.001))  # păstrat după fapte, deși val_bpb e puțin mai slab
    reluat = Orchestrator(o.config)  # din jurnal: după val_bpb ar fi fost primul; după fapte e al doilea
    assert reluat.cel_mai_bun["id"] == al_doilea["id"]
    assert reluat.experiment(_propune(fapte=30, biti=5.001))["motiv"].startswith("criteriul principal fapte_corecte: 30 față de 25")


def test_principalul_lipsa_nu_se_poate_compara(tmp_path, monkeypatch):
    criterii = PRINCIPAL.replace("[criterii.fapte_corecte]", "[criterii.fapte_lipsa]")
    o = Orchestrator(_config(tmp_path, monkeypatch, criterii))
    prima = o.experiment(Propunere("punct de plecare"))
    a_doua = o.experiment(_propune(biti=4.0))
    assert a_doua["decizie"] == "respins" and a_doua["motiv"] == (
        f"criteriul principal fapte_lipsa nu se poate compara cu #{prima['id']} (lipsește)")


def test_fara_principal_e_ca_inainte(tmp_path, monkeypatch):
    o = Orchestrator(_config(tmp_path, monkeypatch, CRITERII))
    assert o.config.criteriu_principal() is None
    assert o.config.criterii == {"fapte_corecte": {"mai_mare_e_mai_bine": True, "prag": 2.0},
                                 "nota_profesor": {"mai_mare_e_mai_bine": True, "prag": 0.5}}
    o.experiment(Propunere("punct de plecare"))
    a_doua = o.experiment(_propune(fapte=40, biti=5.01))  # faptele urcă mult, dar val_bpb e mai slab: respins
    assert a_doua["decizie"] == "respins" and a_doua["motiv"] == "scorul nu e mai bun" and "castig_principal" not in a_doua


@pytest.mark.parametrize("criterii, mesaj", [
    (PRINCIPAL.replace("prag = 0.5", "prag = 0.5\nprincipal = true"), "un singur criteriu poate fi principal"),
    (PRINCIPAL.replace("principal = true", 'principal = "da"'), "principal e true sau false"),
])
def test_principal_gresit_in_configurare(tmp_path, monkeypatch, criterii, mesaj):
    with pytest.raises(EroareConfig, match=mesaj):
        _config(tmp_path, monkeypatch, criterii)


def test_consola_arata_motivul_principalului(tmp_path, monkeypatch, capsys):
    o = Orchestrator(_config(tmp_path, monkeypatch, PRINCIPAL, tacut=False))
    o.experiment(Propunere("punct de plecare"))
    o.experiment(_propune(fapte=12))
    assert "motiv: criteriul principal fapte_corecte: 12 față de 10" in capsys.readouterr().out
