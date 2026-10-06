"""CONTINUUM, STARE: memoria (stare.json) și jurnalul ciclurilor (cicluri.jsonl), cu rotire și probleme."""

from __future__ import annotations

import json

from module.continuum.stare import (actualizeaza_probleme, citeste_cicluri, incarca, memorie_goala, salveaza,
                                    scrie_ciclu)


def test_memoria_se_pastreaza_intre_porniri(tmp_path):
    director = tmp_path / "continuum"
    assert incarca(director) == memorie_goala()
    memorie = memorie_goala()
    memorie["ciclu"] = 12
    memorie["strategii"]["continua:povesti:antrenare"] = {"incredere": 0.6}
    salveaza(director, memorie)
    assert incarca(director) == memorie and not (director / "stare.json.tmp").exists()


def test_o_memorie_stricata_se_muta_deoparte(tmp_path):
    director = tmp_path / "continuum"
    director.mkdir()
    (director / "stare.json").write_text("{ stricat", encoding="utf-8")
    memorie = incarca(director)
    assert memorie["ciclu"] == 0 and "stare.json era stricat" in memorie["probleme"][0]["ce"]
    assert len(list(director.glob("stare_stricata_*.json"))) == 1  # nimic nu se șterge


def test_problemele_se_deschid_si_se_inchid_singure():
    memorie = memorie_goala()
    actualizeaza_probleme(memorie, {"modul:profesor": "modulul profesor e cazut"}, "t1")
    actualizeaza_probleme(memorie, {"modul:profesor": "modulul profesor e cazut"}, "t2")  # tot ea, nu una nouă
    assert len(memorie["probleme"]) == 1 and memorie["probleme"][0]["deschisa"]
    actualizeaza_probleme(memorie, {}, "t3")
    assert memorie["probleme"][0] | {} == {"cheie": "modul:profesor", "ce": "modulul profesor e cazut",
                                          "deschisa": False, "de_la": "t1", "rezolvata": "t3"}
    actualizeaza_probleme(memorie, {"modul:profesor": "modulul profesor e cazut"}, "t4")  # a căzut din nou
    assert [p["deschisa"] for p in memorie["probleme"]] == [False, True]


def test_jurnalul_ciclurilor_creste_si_se_roteste(tmp_path):
    director = tmp_path / "continuum"
    for ciclu in range(1, 4):
        scrie_ciclu(director, {"ciclu": ciclu, "pe_scurt": "ÎNVĂȚARE: totul în regulă"}, max_mb=20)
    assert [r["ciclu"] for r in citeste_cicluri(director, 2)] == [2, 3]
    assert json.loads((director / "cicluri.jsonl").read_text(encoding="utf-8").splitlines()[0])["pe_scurt"] == \
        "ÎNVĂȚARE: totul în regulă"
    scrie_ciclu(director, {"ciclu": 4}, max_mb=0.0001)  # peste limită: fișierul vechi se mută deoparte
    assert [r["ciclu"] for r in citeste_cicluri(director, 10)] == [4]
    vechi = list(director.glob("cicluri_*.jsonl"))
    assert len(vechi) == 1 and len(vechi[0].read_text(encoding="utf-8").splitlines()) == 3
