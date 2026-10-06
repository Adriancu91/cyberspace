"""Regula 4 (nou ≠ mai bun): criterii suplimentare la decizie, date de model prin dupa_examen, doar cu [criterii]."""

from __future__ import annotations

import pytest

from kronos.config import EroareConfig, citeste_config
from kronos.contracte import Propunere
from kronos.orchestrator import Orchestrator
from teste.test_cap_coada import RADACINA

CRITERII = """
[criterii.fapte_corecte]
mai_mare_e_mai_bine = true
prag = 2

[criterii.nota_profesor]
mai_mare_e_mai_bine = true
prag = 0.5
"""


def _config(tmp_path, monkeypatch, criterii: str = CRITERII, tacut: bool = True):
    """Configurarea de probă, cu modelul care dă criterii (scorul și criteriile din setări) și [criterii] la final."""
    monkeypatch.chdir(tmp_path)
    text = (RADACINA / "config" / "proba.toml").read_text(encoding="utf-8")
    text = text.replace('modul = "module.model_ngram:ModelNgram"\nsetari = { ordin = 1, netezire = 1.0 }',
                        'modul = "teste.module_spion:ModelCuCriterii"\nsetari = { biti = 5.0, fapte = 10, nota = 5.0 }')
    text = text.replace('propozitii = 4000', 'propozitii = 300')
    if tacut:
        text = text.replace('modul = "module.interfata_consola:InterfataConsola"',
                            'modul = "module.interfata_consola:InterfataConsola"\nsetari = { tacut = true }')
    fisier = tmp_path / "criterii.toml"
    fisier.write_text(text + criterii, encoding="utf-8")
    return citeste_config(fisier)


def _propune(**model):
    return Propunere("încercare", {"model": model})


def test_criteriul_care_cade_respinge_desi_val_bpb_e_mai_bun(tmp_path, monkeypatch):
    o = Orchestrator(_config(tmp_path, monkeypatch))
    prima = o.experiment(Propunere("punct de plecare"))
    assert prima["decizie"] == "pastrat" and prima["criterii"] == {"fapte_corecte": 10, "nota_profesor": 5.0}
    a_doua = o.experiment(_propune(biti=4.0, fapte=5))  # val_bpb mult mai bun, dar faptele scad cu 5 (pragul e 2)
    assert a_doua["castig"] == pytest.approx(1.0) and a_doua["decizie"] == "respins"
    assert a_doua["motiv"] == f"a pierdut fapte_corecte: 5 față de 10 la #{prima['id']} (a scăzut cu 5, pragul e 2)"
    assert "model_salvat" not in a_doua and o.cel_mai_bun["id"] == prima["id"]  # cel mai bun rămâne cel vechi
    assert a_doua["dupa_examen"]["am_primit"]["decizie"] == "pastrat"  # ce ar fi decis val_bpb singur
    assert a_doua["criterii"] == {"fapte_corecte": 5, "nota_profesor": 5.0}  # doar numere („text” a fost lăsat afară)


def test_criteriul_stabil_pastreaza(tmp_path, monkeypatch):
    o = Orchestrator(_config(tmp_path, monkeypatch))
    o.experiment(Propunere("punct de plecare"))
    a_doua = o.experiment(_propune(biti=4.0, fapte=9, nota=4.6))  # scad, dar sub prag (1 ≤ 2; 0,4 ≤ 0,5)
    assert a_doua["decizie"] == "pastrat" and "model_salvat" in a_doua and o.cel_mai_bun["id"] == a_doua["id"]
    a_treia = o.experiment(_propune(biti=3.0, fapte=7, nota=4.6))  # exact cât pragul (2) față de cel mai bun: trece
    assert a_treia["decizie"] == "pastrat"


def test_referinta_e_cel_mai_bun_experiment_pastrat(tmp_path, monkeypatch):
    o = Orchestrator(_config(tmp_path, monkeypatch))
    o.experiment(Propunere("punct de plecare"))  # fapte 10
    o.experiment(_propune(biti=4.0, fapte=9))  # păstrat; de acum, referința e 9
    respins = o.experiment(_propune(biti=4.5, fapte=20))  # val_bpb mai slab: respins pentru scor, nu pentru criterii
    assert respins["decizie"] == "respins" and respins["motiv"] == "scorul nu e mai bun"
    a_patra = o.experiment(_propune(biti=3.0, fapte=6))  # 9 → 6: a scăzut cu 3 față de cel mai bun PĂSTRAT (nu de 20)
    assert a_patra["decizie"] == "respins" and a_patra["motiv"].startswith("a pierdut fapte_corecte: 6 față de 9")
    reluat = Orchestrator(o.config)  # și după reluare, din jurnal
    assert reluat.cel_mai_bun["criterii"]["fapte_corecte"] == 9
    assert reluat.experiment(_propune(biti=3.0, fapte=6))["motiv"].startswith("a pierdut fapte_corecte")


def test_directia_mai_mic_e_mai_bine_si_criteriile_lipsa(tmp_path, monkeypatch):
    criterii = """
[criterii.nota_profesor]
mai_mare_e_mai_bine = false
prag = 0.5

[criterii.lipseste]
mai_mare_e_mai_bine = true
prag = 0
"""
    o = Orchestrator(_config(tmp_path, monkeypatch, criterii))
    prima = o.experiment(Propunere("punct de plecare"))
    assert prima["criterii_lipsa"] == ["lipseste"]  # nu-l dă modelul: se notează, dar nu oprește nimic
    assert o.experiment(_propune(biti=4.0, nota=4.0))["decizie"] == "pastrat"  # aici, o notă mai mică e mai bună
    urcat = o.experiment(_propune(biti=3.0, nota=5.0))  # „scade” cu 1 (urcă la 5), pragul e 0,5
    assert urcat["decizie"] == "respins" and urcat["motiv"].startswith("a pierdut nota_profesor: 5 față de 4")


def test_fara_criterii_totul_e_ca_inainte(tmp_path, monkeypatch):
    o = Orchestrator(_config(tmp_path, monkeypatch, criterii=""))
    assert o.config.criterii == {}
    o.experiment(Propunere("punct de plecare"))
    a_doua = o.experiment(_propune(biti=4.0, fapte=1))  # faptele cad, dar fără [criterii] contează doar val_bpb
    assert a_doua["decizie"] == "pastrat" and "criterii" not in a_doua and "criterii_lipsa" not in a_doua
    assert a_doua["dupa_examen"]["am_primit"]["decizie"] == "pastrat"  # chemat după decizie, ca înainte


@pytest.mark.parametrize("criterii", [
    "[criterii.x]\nprag = 1\n",
    "[criterii.x]\nmai_mare_e_mai_bine = true\n",
    "[criterii.x]\nmai_mare_e_mai_bine = true\nprag = -1\n",
    '[criterii.x]\nmai_mare_e_mai_bine = "da"\nprag = 1\n',
    "[criterii.x]\nmai_mare_e_mai_bine = true\nprag = true\n",
])
def test_criterii_gresite_in_configurare(tmp_path, monkeypatch, criterii):
    with pytest.raises(EroareConfig, match="criteriul „x”"):
        _config(tmp_path, monkeypatch, criterii)


def test_consola_arata_criteriul_pierdut(tmp_path, monkeypatch, capsys):
    o = Orchestrator(_config(tmp_path, monkeypatch, tacut=False))
    o.experiment(Propunere("punct de plecare"))
    o.experiment(_propune(biti=4.0, fapte=5))
    iesire = capsys.readouterr().out
    assert "respins" in iesire and "motiv: a pierdut fapte_corecte: 5 față de 10" in iesire
