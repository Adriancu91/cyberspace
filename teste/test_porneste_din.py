"""kronos (aprobat de Adrian, 8 octombrie 2026): o linie care pornește dintr-un model păstrat (porneste_din, ex.
--porneste-din la antrenarea lungă) își judecă primul experiment cu regula 4 față de scorurile acelui model, în loc să-l
păstreze din oficiu. Fără porneste_din, primul experiment al liniei e păstrat, ca înainte (teste/test_criterii.py)."""

from __future__ import annotations

import copy

import pytest

from kronos.config import EroareConfig, citeste_config
from kronos.contracte import Propunere
from kronos.orchestrator import Orchestrator
from teste.test_cap_coada import RADACINA
from teste.test_criterii import CRITERII, _config, _propune
from teste.test_criteriu_principal import PRINCIPAL


def _linie_noua(config, porneste_din, nume="linia_noua"):
    noua = copy.deepcopy(config)
    noua.nume, noua.porneste_din = nume, porneste_din
    return noua


def _model_de_pornire(tmp_path, monkeypatch, criterii=CRITERII):
    """Un model păstrat pe altă linie (punctul ei de plecare): val_bpb 5, fapte 10, nota 5."""
    config = _config(tmp_path, monkeypatch, criterii)
    fisa = Orchestrator(config).experiment(Propunere("punct de plecare"))
    assert fisa["decizie"] == "pastrat"
    return config, fisa


def test_primul_experiment_se_judeca_fata_de_modelul_de_pornire(tmp_path, monkeypatch):
    config, pornire = _model_de_pornire(tmp_path, monkeypatch)
    o = Orchestrator(_linie_noua(config, pornire["id"]))
    assert o.cel_mai_bun is o.pornire and o.pornire["id"] == pornire["id"]
    assert o.setari_curente == {"model": config.setari_port("model")}  # rețeta rămâne cea din configurare
    la_fel = o.experiment(Propunere("prima oră"))  # aceleași scoruri ca modelul de pornire: nu e mai bun
    assert la_fel["decizie"] == "respins" and la_fel["motiv"] == "scorul nu e mai bun"
    assert la_fel["fata_de_pornire"] == pornire["id"] and la_fel["scor_anterior"] == 5.0
    mai_bun = o.experiment(_propune(biti=4.9))
    assert mai_bun["decizie"] == "pastrat" and mai_bun["fata_de_pornire"] == pornire["id"] and "model_salvat" in mai_bun
    urmatorul = o.experiment(_propune(biti=4.8))  # de acum, referința e linia însăși
    assert "fata_de_pornire" not in urmatorul and urmatorul["scor_anterior"] == 4.9
    reluat = Orchestrator(o.config)  # la reluare, linia are un păstrat: modelul de pornire nu mai contează
    assert reluat.pornire is None and reluat.cel_mai_bun["id"] == urmatorul["id"]


def test_fara_porneste_din_primul_e_pastrat_ca_inainte(tmp_path, monkeypatch):
    config, pornire = _model_de_pornire(tmp_path, monkeypatch)
    o = Orchestrator(_linie_noua(config, None))
    assert o.pornire is None and o.cel_mai_bun is None
    prima = o.experiment(_propune(biti=6.0))  # mult mai slab decât celălalt model, dar primul din linia lui
    assert prima["decizie"] == "pastrat" and "fata_de_pornire" not in prima and prima["scor_anterior"] is None


def test_criteriile_se_compara_cu_modelul_de_pornire(tmp_path, monkeypatch):
    config, pornire = _model_de_pornire(tmp_path, monkeypatch)
    o = Orchestrator(_linie_noua(config, pornire["id"]))
    fisa = o.experiment(_propune(biti=4.0, nota=4.0))  # val_bpb mult mai bun, dar nota scade cu 1 (pragul 0,5)
    assert fisa["decizie"] == "respins" and fisa["motiv"] == (
        f"a pierdut nota_profesor: 4 față de 5 la #{pornire['id']} (a scăzut cu 1, pragul e 0.5)")


def test_modelul_de_pornire_are_criteriile_doar_in_dupa_examen(tmp_path, monkeypatch):
    """Ca #257: linia lui n-avea [criterii], deci criteriile lui sunt doar în răspunsul dupa_examen."""
    fara = _config(tmp_path, monkeypatch, criterii="")
    pornire = Orchestrator(fara).experiment(Propunere("punct de plecare"))
    assert "criterii" not in pornire and pornire["dupa_examen"]["criterii"]["nota_profesor"] == 5.0
    o = Orchestrator(_linie_noua(_config(tmp_path, monkeypatch), pornire["id"]))
    fisa = o.experiment(_propune(biti=4.0, fapte=7))  # faptele scad cu 3 (pragul 2)
    assert fisa["decizie"] == "respins" and fisa["motiv"] == (
        f"a pierdut fapte_corecte: 7 față de 10 la #{pornire['id']} (a scăzut cu 3, pragul e 2)")


def test_criteriul_principal_fata_de_modelul_de_pornire(tmp_path, monkeypatch):
    config, pornire = _model_de_pornire(tmp_path, monkeypatch, PRINCIPAL)  # fapte 10
    o = Orchestrator(_linie_noua(config, pornire["id"]))
    putin = o.experiment(_propune(fapte=15))
    assert putin["decizie"] == "respins" and putin["motiv"] == (
        f"criteriul principal fapte_corecte: 15 față de 10 la #{pornire['id']} (câștig +5, trebuie peste 10)")
    destul = o.experiment(_propune(fapte=25))
    assert destul["decizie"] == "pastrat" and destul["castig_principal"] == 15


def test_ruleaza_judeca_si_punctul_de_plecare(tmp_path, monkeypatch):
    config, pornire = _model_de_pornire(tmp_path, monkeypatch)
    fise = Orchestrator(_linie_noua(config, pornire["id"])).ruleaza(0)
    assert len(fise) == 1 and fise[0]["propunere"]["descriere"].startswith("punct de plecare")
    assert fise[0]["decizie"] == "respins" and fise[0]["fata_de_pornire"] == pornire["id"]


@pytest.mark.parametrize("cum", ["lipsește", "respins"])
def test_porneste_din_trebuie_sa_fie_un_model_pastrat(tmp_path, monkeypatch, cum):
    config, _ = _model_de_pornire(tmp_path, monkeypatch)
    tinta = Orchestrator(config).experiment(_propune(biti=6.0))["id"] if cum == "respins" else 999
    with pytest.raises(EroareConfig, match=f"porneste_din = {tinta}: în jurnal nu e un experiment păstrat"):
        Orchestrator(_linie_noua(config, tinta))


def test_porneste_din_in_configurare(tmp_path):
    text = (RADACINA / "config" / "proba.toml").read_text(encoding="utf-8")
    fisier = tmp_path / "proba.toml"
    fisier.write_text(text, encoding="utf-8")
    assert citeste_config(fisier).porneste_din is None
    fisier.write_text(text.replace("[platforma]\n", "[platforma]\nporneste_din = 7\n"), encoding="utf-8")
    assert citeste_config(fisier).porneste_din == 7
    for gresit in ("true", "0", '"7"'):
        fisier.write_text(text.replace("[platforma]\n", f"[platforma]\nporneste_din = {gresit}\n"), encoding="utf-8")
        with pytest.raises(EroareConfig, match="porneste_din"):
            citeste_config(fisier)


def test_unealta_de_antrenare_lunga_judeca_prima_ora_fata_de_pornire(tmp_path, monkeypatch):
    """Cap-coadă, cu unealta: prima oră a unei linii pornite cu --porneste-din e judecată față de modelul de pornire;
    dacă nu e păstrată, povestea de la final o scrie starea de la final."""
    pytest.importorskip("torch")
    import json

    from teste.test_bucla_cinstita import config_mic, fise
    from unelte import antrenare_lunga

    monkeypatch.chdir(tmp_path)
    comun = ["--pauza", "0", "--racire", "0", "--lungime", "30"]
    prima = config_mic(tmp_path, "sursa", model=', cale_stare = "lucru/sursa/gpt.pt"', spatiu="lot = [4]")
    assert antrenare_lunga.main(["--config", str(prima), "--ore", "1"] + comun) == 0
    sursa = [f for f in fise(tmp_path) if f["linie"] == "sursa"][0]
    a_doua = config_mic(tmp_path, "din_sursa", model=', cale_stare = "lucru/din_sursa/gpt.pt"', spatiu="lot = [4]")
    assert antrenare_lunga.main(["--config", str(a_doua), "--ore", "1", "--porneste-din", str(sursa["id"]),
                                 "--inceput", "Once upon a time"] + comun) == 0
    ora = [f for f in fise(tmp_path) if f["linie"] == "din_sursa"][0]
    assert ora["fata_de_pornire"] == sursa["id"] and ora["scor_anterior"] == sursa["scoruri"]["val_bpb"]
    rezultat = json.loads((tmp_path / "lucru" / "din_sursa" / "rezultat.json").read_text(encoding="utf-8"))
    assert rezultat["poveste"]["text"].startswith("Once upon a time")  # și când ora nu e păstrată
