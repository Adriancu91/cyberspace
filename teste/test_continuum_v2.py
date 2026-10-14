"""CONTINUUM v2 (workstation): cel puțin două variante adevărate la fiecare alegere: continuă / prelungește linia
cea mai bună, remăsoară, sau pornește o linie nouă dintr-o configurare neîncepută. Fără placă video."""

import json
import sys
from pathlib import Path

import pytest

from module.continuum import EroareContinuum, citeste_config
from module.continuum.bucla import Bucla, main
from module.continuum.stare import citeste_cicluri
from teste.continuum_proba import Lume, config_continuum, config_kronos, fisa, scrie_jurnal, scrie_unelte

RADACINA = Path(__file__).resolve().parent.parent
V2 = {
    'ordinea_nevoilor = ["masoara", "continua", "dezvolta"]': 'ordinea_nevoilor = ["masoara", "continua", "linie_noua", "dezvolta"]',
    'configurari = ["config/laptop_antrenare_lunga*.toml", "config/laptop_fapte*.toml"]': 'configurari = ["config/ws_w*.toml"]',
    'configurari = ["config/laptop_antrenare_lunga*.toml"]\ntimeout_ore = 0.05':
        'configurari = ["config/ws_w*.toml"]\nprelungire_ore = 8\ntimeout_ore = 0.05\n\n[nevoi.linie_noua]\nnivel = "ÎNVĂȚARE"\n'
        'capacitate = "povesti"\nconfigurari = ["config/ws_w2.toml"]\ntimeout_ore = 0.05',
    'configurari = ["config/laptop_fapte*.toml"]': "configurari = []",
    # fără uneltele de examen: aici se încearcă doar alegerea antrenării
    'masurare = ["{python}", "unelte/examen_fapte.py", "--experiment", "{experiment}"]\n': "",
    'masurare = ["{python}", "unelte/examen_profesor.py", "--experiment", "{experiment}"]\n': "",
}
CRITERII = {"fapte_corecte": 60, "nota_profesor": 4.5}


def proiect(tmp_path, monkeypatch, scoruri_w1, ore_w1=10, inlocuiri=None):
    """Proiect mic: W1 cu orele date în jurnal (din 10 plănuite), W2 neîncepută, uneltele de probă."""
    monkeypatch.chdir(tmp_path)
    config_continuum(tmp_path, inlocuiri={**V2, **(inlocuiri or {})})
    config_kronos(tmp_path, "ws_w1.toml", "ws_w1", ore=ore_w1, straturi=12)
    config_kronos(tmp_path, "ws_w2.toml", "ws_w2", ore=10, straturi=12, model=", lot = 12")
    scrie_jurnal(tmp_path, [fisa(i, "ws_w1", s, criterii=CRITERII, straturi=12, minute=60)
                            for i, s in enumerate(scoruri_w1, start=1)])
    scrie_unelte(tmp_path, val_bpb=0.40, pas_val_bpb=-0.001)
    return tmp_path


def bucla(simuleaza=True, ora="23:30"):
    b = Bucla("config/continuum.toml", simuleaza=simuleaza, senzori=Lume(ora=ora).senzori(), dormi=lambda s: None,
              iesire=lambda s: None)
    b.redescopera()  # ca la pornirea buclei: modulele din [module]
    return b


def argumente(tmp_path):
    return json.loads((tmp_path / "lucru" / "jurnal" / "argumente.json").read_text(encoding="utf-8"))


SCADE = [0.58, 0.55, 0.53, 0.51, 0.49, 0.48, 0.47, 0.46, 0.45, 0.44]          # încă învață: 0,01 pe oră
SATURAT = [0.58, 0.55, 0.53, 0.51, 0.49, 0.48, 0.47, 0.46, 0.458, 0.457]      # două ore la rând sub 0,005


def test_linia_care_inca_invata_se_prelungeste_iar_linia_noua_e_alternativa(tmp_path, monkeypatch):
    proiect(tmp_path, monkeypatch, SCADE)
    rand = bucla().ciclu()
    assert rand["nevoie"] == "continua:povesti"
    assert "prelungită cu 8 ore, de la ora 11" in rand["actiune"] and "ws_w1" in rand["actiune"]
    assert "--ore 18" in rand["comenzi"][0] and "--porneste-din" not in rand["comenzi"][0]
    # a doua variantă adevărată e notată, cu ce ar fi pornit
    assert [a["nevoie"] for a in rand["alternative"]] == ["linie_noua:povesti"]
    assert "config/ws_w2.toml" in rand["alternative"][0]["actiune"] and "de la zero" in rand["alternative"][0]["actiune"]
    assert "Se putea și: linie_noua:povesti" in rand["pe_scurt"] and "ordinea din configurare" in rand["pe_scurt"]


def test_linia_saturata_nu_se_mai_continua_si_porneste_linia_noua_de_la_zero(tmp_path, monkeypatch):
    proiect(tmp_path, monkeypatch, SATURAT)
    rand = bucla().ciclu()
    assert rand["nevoie"] == "linie_noua:povesti"
    assert "saturată" in rand["motiv"] and "config/ws_w2.toml" in rand["motiv"]
    assert "de la zero" in rand["actiune"] and "--ore 10" in rand["comenzi"][0]
    # aceeași arhitectură ca W1 (12 straturi), dar o linie nouă nu pornește din modelul altei linii
    assert "--porneste-din" not in rand["comenzi"][0]
    assert "alternative" not in rand  # „continua” nici nu e cerută: linia e saturată


def test_ordinea_din_configurare_hotaraste_intre_cele_doua_variante(tmp_path, monkeypatch):
    proiect(tmp_path, monkeypatch, SCADE, inlocuiri={
        'ordinea_nevoilor = ["masoara", "continua", "linie_noua", "dezvolta"]':
            'ordinea_nevoilor = ["masoara", "linie_noua", "continua", "dezvolta"]'})
    rand = bucla().ciclu()
    assert rand["nevoie"] == "linie_noua:povesti"
    assert [a["nevoie"] for a in rand["alternative"]] == ["continua:povesti"]


def test_linia_neterminata_se_reia_nu_se_prelungeste(tmp_path, monkeypatch):
    proiect(tmp_path, monkeypatch, SCADE[:6])  # 6 ore din 10 (ex. după o repornire de Windows)
    rand = bucla().ciclu()
    assert rand["nevoie"] == "continua:povesti" and "reluată de la ora 7" in rand["actiune"]
    assert "--ore 10" in rand["comenzi"][0]


def test_continua_nu_porneste_linii_neincepute_cand_exista_linie_noua(tmp_path, monkeypatch):
    """Cu [nevoi.linie_noua], W2 (neîncepută, în lista albă a lui „continua” prin ws_w*) nu e pornită de „continua”."""
    proiect(tmp_path, monkeypatch, SCADE, inlocuiri={"prelungire_ore = 8": "prelungire_ore = 0"})
    rand = bucla().ciclu()
    assert rand["nevoie"] == "linie_noua:povesti"
    sarita = next(s for s in rand["sarite"] if s["nevoie"] == "continua:povesti")
    assert "toate configurările potrivite sunt încheiate" in sarita["de_ce_nu"] and "ws_w2" not in sarita["de_ce_nu"]


def test_fara_nimic_neinceput_nevoia_linie_noua_nu_apare(tmp_path, monkeypatch):
    proiect(tmp_path, monkeypatch, SATURAT)
    scrie_jurnal(tmp_path, [fisa(50, "ws_w2", 0.60, criterii=CRITERII, straturi=12, minute=60,
                                 inceput="2026-10-05T20:00:00+00:00")])
    rand = bucla().ciclu()
    assert all(not n["nevoie"].startswith("linie_noua") for n in rand["nevoi"])


def test_ziua_la_workstation_fereastra_de_invatare_e_toata_ziua(tmp_path, monkeypatch):
    proiect(tmp_path, monkeypatch, SCADE, inlocuiri={
        'fereastra_invatare = "22:00-07:00"': 'fereastra_invatare = "00:00-23:59"',
        'fereastra_intretinere = "07:00-22:00"': 'fereastra_intretinere = "00:00-23:59"'})
    for ora in ("03:00", "11:15", "16:40", "23:58"):
        rand = bucla(ora=ora).ciclu()
        assert rand["nivel"] == "ÎNVĂȚARE" and rand["nevoie"] == "continua:povesti", ora


def test_pe_bune_prelungirea_porneste_unealta_cu_orele_noi_si_se_masoara(tmp_path, monkeypatch):
    proiect(tmp_path, monkeypatch, SCADE)
    b = bucla(simuleaza=False)
    rand = b.ciclu()
    assert rand["nevoie"] == "continua:povesti" and rand["rezultat"]["reusit"]
    args = argumente(tmp_path)
    assert args[args.index("--config") + 1] == "config/ws_w1.toml" and args[args.index("--ore") + 1] == "18"
    assert rand["verdict"] in ("SUCCES", "NECONCLUDENT", "SUCCES SCUMP")
    assert citeste_cicluri(b.director, 1)[0]["alternative"][0]["nevoie"] == "linie_noua:povesti"


def test_pe_bune_linia_noua_porneste_w2(tmp_path, monkeypatch):
    proiect(tmp_path, monkeypatch, SATURAT)
    rand = bucla(simuleaza=False).ciclu()
    assert rand["nevoie"] == "linie_noua:povesti" and rand["rezultat"]["reusit"]
    args = argumente(tmp_path)
    assert args[args.index("--config") + 1] == "config/ws_w2.toml" and "--porneste-din" not in args


def test_configurarea_v2_gresita_e_refuzata_cu_mesaj(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    config_continuum(tmp_path, inlocuiri={**V2, 'capacitate = "povesti"\nconfigurari = ["config/ws_w2.toml"]':
                                          'configurari = ["config/ws_w2.toml"]'})
    with pytest.raises(EroareContinuum, match="capacitate"):
        citeste_config("config/continuum.toml")
    config_continuum(tmp_path, inlocuiri={**V2, "prelungire_ore = 8": "prelungire_ore = -1"})
    with pytest.raises(EroareContinuum, match="prelungire_ore"):
        citeste_config("config/continuum.toml")


def test_configurarea_v1_merge_neschimbata(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    config = citeste_config(config_continuum(tmp_path))
    assert "linie_noua" not in config["nevoi"] and config["nevoi"]["continua"]["prelungire_ore"] == 0


def test_configurarea_adevarata_a_workstation_ului():
    """config/continuum_ws.toml: se citește, are ferestrele și limitele workstation-ului și două variante de antrenare."""
    config = citeste_config(RADACINA / "config" / "continuum_ws.toml")
    g = config["guvernator"]
    # din 13 octombrie 2026 (v3, teste/test_continuum_v3.py): noaptea se pornește între 19:00 și 21:00, ziua 07:45–18:50
    assert f"{g['fereastra_invatare'][0]:%H:%M}-{g['fereastra_invatare'][1]:%H:%M}" == "19:00-21:00"
    assert f"{g['fereastra_intretinere'][0]:%H:%M}-{g['fereastra_intretinere'][1]:%H:%M}" == "07:45-18:15"
    assert g["temperatura_max"] == 83 and g["memorie_video_libera_min_mb"] == 4500 and g["buget_ore_placa_pe_zi"] == 20
    assert config["continuum"]["ordinea_nevoilor"] == ["repara", "masoara", "remasoara", "deprinde", "continua",
                                                       "linie_noua", "dezvolta"]
    assert config["linii"]["configurari"] == ["config/ws_w*.toml"]
    assert config["nevoi"]["continua"]["prelungire_ore"] == 10 and config["nevoi"]["continua"]["configurari"] == ["config/ws_w2.toml"]
    assert config["nevoi"]["linie_noua"]["configurari"] == ["config/ws_w2.toml"]
    assert config["nevoi"]["dezvolta"]["configurari"] == []
    for cale in ("config/ws_w1.toml", "config/ws_w2.toml"):
        assert (RADACINA / cale).exists()


def test_simularea_din_linia_de_comanda(tmp_path, monkeypatch, capsys):
    proiect(tmp_path, monkeypatch, SCADE)
    monkeypatch.setattr(sys, "argv", ["bucla"])
    assert main(["--config", "config/continuum.toml", "--simuleaza", "--ca-la", "23:30", "--placa-libera",
                 "--stare", "lucru/continuum_ws"]) == 0
    iesire = capsys.readouterr().out
    assert "Aleg continua:povesti" in iesire and "Se putea și: linie_noua:povesti" in iesire
    assert (tmp_path / "lucru" / "continuum_ws" / "cicluri.jsonl").exists()
    assert not (tmp_path / "lucru" / "continuum").exists()  # jurnalele celuilalt CONTINUUM rămân neatinse
