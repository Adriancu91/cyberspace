"""Antrenările lungi din 8 octombrie 2026: hrana cu fapte 5% e implicită (lecția 6a) și configurarea 7 (din #262,
8 ore, rata cel mult 0,0001, fără repornire la 0,0002; criterii: val_bpb principal 0,005, fapte_noi −10, nota −1,0)."""

from __future__ import annotations

import json
import tomllib

import pytest

from kronos.config import citeste_config
from teste.test_cap_coada import RADACINA
from unelte import antrenare_lunga


def config_cu(tmp_path, setari_model: str):
    text = (RADACINA / "config" / "proba.toml").read_text(encoding="utf-8")
    text = text.replace('modul = "module.model_ngram:ModelNgram"\nsetari = { ordin = 1, netezire = 1.0 }',
                        'modul = "teste.module_spion:ModelCuCriterii"\nsetari = { n_straturi = 2, n_capete = 2, '
                        f'n_emb = 8, context = 8, lot = 2, rata_invatare = 0.001{setari_model} }}')
    (tmp_path / "linie.toml").write_text(text, encoding="utf-8")
    return tmp_path / "linie.toml"


@pytest.mark.parametrize("setari, primeste", [
    ("", True),  # nu pomenește hrana: o primește pe cea implicită
    (', hrana = ""', False),  # fără hrană, spus explicit
    (', hrana = "alta.txt", fractie_hrana = 0.1', False),  # altă hrană: rămâne a ei
])
def test_hrana_implicita(tmp_path, setari, primeste):
    config = citeste_config(config_cu(tmp_path, setari))
    inainte = config.setari_port("model")
    assert antrenare_lunga.cu_hrana_implicita(config) is primeste
    dupa = config.setari_port("model")
    assert dupa == ({**inainte, **antrenare_lunga.HRANA_IMPLICITA} if primeste else inainte)
    assert antrenare_lunga.HRANA_IMPLICITA == {"hrana": "date/fapte/povesti.txt", "fractie_hrana": 0.05}


def test_unealta_trimite_hrana_implicita_lui_kronos(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    config_cu(tmp_path, "")
    primite = []
    monkeypatch.setattr(antrenare_lunga, "ruleaza", lambda config, *a, **o: primite.append(config.setari_port("model")))
    assert antrenare_lunga.main(["--config", "linie.toml", "--ore", "1"]) == 1  # nicio oră făcută (ruleaza de probă)
    assert primite[0]["hrana"] == "date/fapte/povesti.txt" and primite[0]["fractie_hrana"] == 0.05
    assert "Hrana e cea implicită (configurarea n-o pomenește" in capsys.readouterr().out


def test_configurarea_7():
    config = citeste_config(RADACINA / "config" / "laptop_antrenare_lunga_7.toml")
    model = config.setari_port("model")
    assert (config.nume, config.experimente, config.buget_antrenare_secunde, config.prag_zgomot) == (
        "antrenare_lunga_7", 8, 3600, 0.005)
    assert model["rata_invatare"] <= 0.0001 and model["rata_invatare"] * model["fractie_rata_finala"] == pytest.approx(1e-5)
    assert model["durata_scaderii_secunde"] == 8 * 3600 and model["cale_stare"] == "lucru/antrenare_lunga_7/gpt.pt"
    assert (model["hrana"], model["fractie_hrana"]) == ("date/fapte/povesti.txt", 0.05)
    assert config.criterii == {"fapte_noi": {"mai_mare_e_mai_bine": True, "prag": 10.0},
                               "nota_profesor": {"mai_mare_e_mai_bine": True, "prag": 1.0}}  # val_bpb rămâne principalul
    assert "--porneste-din 262" in config.cale_fisier.read_text(encoding="utf-8")
    # Până pe 8 octombrie la 13:09 testul cerea și „n-a pornit încă”; atunci a pornit-o Adrian (planul joi–sâmbătă).


@pytest.mark.parametrize("fisier", ["laptop_antrenare_lunga_5", "laptop_antrenare_lunga_6b", "laptop_masurare_6c_restart",
                                    "laptop_masurare_6c_continuare"])
def test_rularile_gandite_fara_hrana_raman_fara(fisier):
    config = citeste_config(RADACINA / "config" / f"{fisier}.toml")
    assert config.setari_port("model")["hrana"] == "" and not antrenare_lunga.cu_hrana_implicita(config)


def test_pornire_json_e_citit_de_continuum(tmp_path):
    from module.continuum.observa import experimentul_de_pornire

    (tmp_path / "pornire.json").write_text(json.dumps({"experiment": 262}), encoding="utf-8")
    assert experimentul_de_pornire(tmp_path / "gpt.pt") == 262
    assert experimentul_de_pornire(tmp_path / "alta" / "gpt.pt") is None and experimentul_de_pornire(None) is None


# --- criteriile implicite (8 octombrie 2026): ca în configurarea 7 --------------------------------------------------------

EXAMENE = ', examene_suplimentare = ["fapte", "fapte_noi", "profesor"]'


def criterii_puse(tmp_path, setari_model="", coada="", fara_prag=False):
    import tomllib

    cale = config_cu(tmp_path, setari_model)
    text = cale.read_text(encoding="utf-8") + coada
    if fara_prag:
        text = text.replace("prag_zgomot = 0.002            # câștig minim ca o schimbare să fie păstrată\n", "")
    cale.write_text(text, encoding="utf-8")
    config = citeste_config(cale)
    return antrenare_lunga.cu_criterii_implicite(config, tomllib.loads(text)), config


def test_criteriile_implicite_doar_pentru_examenele_de_la_ora(tmp_path):
    puse, config = criterii_puse(tmp_path, EXAMENE)
    assert puse == ["fapte_noi", "nota_profesor"] and config.criterii == {
        "fapte_noi": {"mai_mare_e_mai_bine": True, "prag": 10.0},
        "nota_profesor": {"mai_mare_e_mai_bine": True, "prag": 1.0}}
    assert config.criteriu_principal() is None and config.prag_zgomot == 0.002  # pragul spus în fișier rămâne
    puse, config = criterii_puse(tmp_path, ', examene_suplimentare = ["fapte_noi"]')
    assert puse == ["fapte_noi"] and list(config.criterii) == ["fapte_noi"]
    assert criterii_puse(tmp_path)[0] == []  # fără examene la oră: niciun criteriu


def test_criteriile_spuse_in_fisier_raman(tmp_path):
    puse, config = criterii_puse(tmp_path, EXAMENE, "\n[criterii]\n")  # gol = fără criterii, spus explicit
    assert puse == [] and config.criterii == {}
    puse, config = criterii_puse(tmp_path, EXAMENE, "\n[criterii.nota_profesor]\nmai_mare_e_mai_bine = true\nprag = 0.3\n")
    assert puse == [] and config.criterii == {"nota_profesor": {"mai_mare_e_mai_bine": True, "prag": 0.3}}


def test_prag_zgomot_implicit(tmp_path):
    assert criterii_puse(tmp_path, EXAMENE, fara_prag=True)[1].prag_zgomot == 0.005


def test_unealta_trimite_criteriile_implicite_lui_kronos(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    config_cu(tmp_path, EXAMENE)
    primite = []
    monkeypatch.setattr(antrenare_lunga, "ruleaza", lambda config, *a, **o: primite.append(config.criterii))
    assert antrenare_lunga.main(["--config", "linie.toml", "--ore", "1"]) == 1
    assert sorted(primite[0]) == ["fapte_noi", "nota_profesor"] and primite[0]["nota_profesor"]["prag"] == 1.0
    assert "Criteriile sunt cele implicite (configurarea n-are [criterii]" in capsys.readouterr().out


@pytest.mark.parametrize("fisier", ["laptop_antrenare_lunga", "laptop_antrenare_lunga_2", "laptop_antrenare_lunga_3",
                                    "laptop_antrenare_lunga_4", "laptop_antrenare_lunga_5", "laptop_masurare_6c_restart",
                                    "laptop_masurare_6c_continuare"])
def test_configurarile_vechi_raman_cum_au_fost(fisier):
    """Fără hrană și fără criterii, cum au rulat: întrebările vechi rămân aceleași la o reluare."""
    import tomllib

    cale = RADACINA / "config" / f"{fisier}.toml"
    config = citeste_config(cale)
    assert antrenare_lunga.cu_criterii_implicite(config, tomllib.loads(cale.read_text(encoding="utf-8"))) == []
    assert config.criterii == {} and not antrenare_lunga.cu_hrana_implicita(config)
    assert config.setari_port("model")["hrana"] == ""


@pytest.mark.parametrize("fisier, ore, rata, durata, din_zero", [("laptop_antrenare_lunga_8", 8, 0.00005, 8 * 3600, False),
                                                                 ("laptop_fapte_zero", 7, 0.001, 8 * 3600, True)])
def test_configurarile_noptii_1(fisier, ore, rata, durata, din_zero):
    """Planul joi–sâmbătă: antrenarea 8 (lista albă a lui CONTINUUM) și fapte-zero (plasa de siguranță). Amândouă cu
    hrana 5%, examenele de fiecare oră și criteriile implicite (fără [criterii]). Antrenarea 8 are 8 ore din noaptea 2
    (faza 3c); în noaptea 1 n-a rulat."""
    config = citeste_config(RADACINA / "config" / f"{fisier}.toml")
    model = config.setari_port("model")
    assert (config.experimente, model["rata_invatare"], model["durata_scaderii_secunde"]) == (ore, rata, durata)
    assert model["rata_invatare"] * model["fractie_rata_finala"] == pytest.approx(rata / 10)
    assert (model["hrana"], model["fractie_hrana"]) == ("date/fapte/povesti.txt", 0.05)
    assert model["examene_suplimentare"] == ["fapte", "fapte_noi", "profesor"] and model["povesti_profesor"] == 40
    assert not model.get("de_la_zero")  # „de_la_zero = true” ar porni de la zero în fiecare oră, nu doar în prima
    assert "criterii" not in tomllib.loads(config.cale_fisier.read_text(encoding="utf-8"))  # deci cele implicite
    assert ("--porneste-din" in config.cale_fisier.read_text(encoding="utf-8").split("\n#   python")[0]) != din_zero
