"""Platforma rulează cap-coadă, iar Paznicul își face treaba."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from kronos.cli import main as cli
from kronos.config import EroareConfig, citeste_config
from kronos.contracte import Propunere
from kronos.orchestrator import Orchestrator

RADACINA = Path(__file__).resolve().parent.parent

STARI_COMPLETE = [
    "propus", "verificat", "aplicat", "testat_rapid", "antrenat", "examinat", "decis", "inregistrat",
]


@pytest.fixture
def config(tmp_path, monkeypatch):
    """Configurarea de probă, dar cu folderul de lucru în afara proiectului."""
    monkeypatch.chdir(tmp_path)
    text = (RADACINA / "config" / "proba.toml").read_text(encoding="utf-8")
    text = text.replace('buget_antrenare_secunde = 10', 'buget_antrenare_secunde = 2')
    text = text.replace('propozitii = 4000', 'propozitii = 800')
    text = text.replace('modul = "module.interfata_consola:InterfataConsola"',
                        'modul = "module.interfata_consola:InterfataConsola"\nsetari = { tacut = true }')
    fisier = tmp_path / "proba.toml"
    fisier.write_text(text, encoding="utf-8")
    return citeste_config(fisier)


def test_bucla_cap_coada(config):
    fise = Orchestrator(config).ruleaza(5)
    assert len(fise) == 6  # punctul de plecare + 5 experimente
    assert fise[0]["decizie"] == "pastrat"
    assert all(f["stari"] == STARI_COMPLETE for f in fise if f["decizie"] != "anulat")
    assert any(f["decizie"] == "pastrat" for f in fise[1:]), "nicio îmbunătățire în 5 încercări"

    linii = (config.director_lucru / "jurnal" / "experimente.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(linii) == 6
    fisa = json.loads(linii[-1])
    for cheie in ("id", "propunere", "module", "setari", "scoruri", "consum", "decizie"):
        assert cheie in fisa
    assert fisa["module"]["model"]["nume"] == "model_ngram"

    pastrate = [f for f in fise if f["decizie"] == "pastrat"]
    assert all(Path(f["model_salvat"]).exists() for f in pastrate)


def test_reluarea_porneste_de_la_cel_mai_bun(config):
    Orchestrator(config).ruleaza(3)
    o = Orchestrator(config)
    assert o.cel_mai_bun is not None
    assert o.setari_curente == o.cel_mai_bun["setari"]
    fise = o.ruleaza(2)
    assert "punct de plecare" not in fise[0]["propunere"]["descriere"]


def test_paznicul_refuza_schimbarea_examenului(config):
    o = Orchestrator(config)
    o.ruleaza(0)  # memorează amprenta examenului
    amprente_fisier = config.director_lucru / "amprente.json"
    amprente = json.loads(amprente_fisier.read_text())
    amprente[next(iter(amprente))] = "amprenta-falsa"
    amprente_fisier.write_text(json.dumps(amprente))

    fisa = o.experiment(Propunere("orice", {"model": {"ordin": 2}}))
    assert fisa["decizie"] == "anulat"
    assert "Examenul" in fisa["motiv"]


def test_paznicul_refuza_porturile_interzise(config):
    o = Orchestrator(config)
    fisa = o.experiment(Propunere("vreau alt examen", {"examen": {"max_caractere": 10}}))
    assert fisa["decizie"] == "anulat" and "examen" in fisa["motiv"]
    fisa = o.experiment(Propunere("valoare ciudată", {"model": {"ordin": [1, 2]}}))
    assert fisa["decizie"] == "anulat" and "tip nepermis" in fisa["motiv"]


def test_setarile_invalide_sunt_anulate_nu_crapa(config):
    fisa = Orchestrator(config).experiment(Propunere("ordin imposibil", {"model": {"ordin": 99}}))
    assert fisa["decizie"] == "anulat"
    assert "Setări greșite" in fisa["motiv"]


def test_modelul_care_crapa_e_anulat(config):
    config.porturi["model"]["modul"] = "teste.module_stricate:ModelCareCrapa"
    fisa = Orchestrator(config).experiment(Propunere("model stricat"))
    assert fisa["decizie"] == "anulat"
    assert "bum" in fisa["motiv"]
    assert fisa["stari"][-2:] == ["anulat", "inregistrat"]


def test_orchestratorul_da_memoria_modelului(config):
    config.porturi["model"]["modul"] = "teste.module_spion:ModelSpion"
    fisa = Orchestrator(config).experiment(Propunere("spion"))
    assert fisa["decizie"] != "anulat", fisa.get("motiv")
    assert fisa["statistici_antrenare"] == {"memorie_conectata": True, "nivele": 1}
    assert fisa["module"]["memorie"]["nume"] == "memorie_goala"


def test_modelul_primeste_rezultatul_examenului_doar_ca_numere(config):
    config.porturi["model"]["modul"] = "teste.module_spion:ModelCareInvataDupaExamen"
    o = Orchestrator(config)
    prima = o.experiment(Propunere("primul"))
    a_doua = o.experiment(Propunere("al doilea"))
    primit = a_doua["dupa_examen"]["am_primit"]
    assert set(primit) == {"id", "scor", "scor_anterior", "castig", "decizie"}
    assert primit["id"] == a_doua["id"] and primit["scor_anterior"] == prima["scoruri"]["val_bpb"]
    assert all(v is None or isinstance(v, (int, float, str)) for v in primit.values())  # numere, nu text
    assert prima["dupa_examen"]["am_primit"]["castig"] is None  # primul experiment nu are cu ce se compara


def test_o_eroare_dupa_examen_nu_strica_experimentul(config):
    config.porturi["model"]["modul"] = "teste.module_spion:ModelCuEroareDupaExamen"
    fisa = Orchestrator(config).experiment(Propunere("spion"))
    assert fisa["decizie"] in ("pastrat", "respins")
    assert "bum după examen" in fisa["eroare_dupa_examen"]


def test_butonul_de_oprire(config):
    o = Orchestrator(config)
    o.paznic.cere_oprire()
    assert o.ruleaza(5) == []
    o.paznic.anuleaza_oprire()
    assert len(o.ruleaza(1)) == 2


def test_pauza_de_racire_apoi_oprire(config, monkeypatch):
    pauze = []
    o = Orchestrator(config, asteapta=pauze.append)
    monkeypatch.setattr(o.paznic, "temperatura_gpu", lambda: 95.0)
    assert o.ruleaza(3) == []
    assert len(pauze) == o.paznic.incercari_racire


def test_limita_de_memorie(config):
    from kronos.contracte import RezultatRulare

    o = Orchestrator(config)
    motiv = o.paznic.verifica_consum(RezultatRulare(True, None, 1.0, memorie_gpu_max_mb=99999))
    assert motiv and "memorie video" in motiv


def test_config_cu_port_lipsa(tmp_path):
    fisier = tmp_path / "rau.toml"
    fisier.write_text('[platforma]\nnume = "x"\n[porturi.model]\nmodul = "a:B"\n', encoding="utf-8")
    with pytest.raises(EroareConfig, match="lipsesc porturile"):
        citeste_config(fisier)


def test_comenzile_din_consola(config, capsys):
    cale = str(config.cale_fisier)
    assert cli(["verifica", "--config", cale]) == 0
    assert cli(["ruleaza", "--config", cale, "--experimente", "2"]) == 0
    assert cli(["jurnal", "--config", cale]) == 0
    assert cli(["scrie", "--config", cale, "--inceput", "the cat", "--lungime", "40"]) == 0
    assert cli(["cauta", "horse", "--config", cale]) == 0
    iesire = capsys.readouterr().out
    assert "Toate modulele sunt în regulă" in iesire
    assert "val_bpb" in iesire
    assert "„horse” nu e în memorie" in iesire  # configurația de probă are MemorieGoala
    assert cli(["opreste", "--config", cale]) == 0
    assert cli(["porneste", "--config", cale]) == 0
    assert cli(["aproba-examen", "--config", cale]) == 0
