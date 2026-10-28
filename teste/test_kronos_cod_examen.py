"""Examenul de cod S41 (C-28 „Kronos-Cod”): referințele trec 100 %, corpurile goale/greșite 0 %, pass@k, setul ascuns."""

import json
import math

import pytest

from unelte.kronos_cod import examen_cod as ex


def test_setul_de_proba_are_cate_o_problema_pe_sablon_si_e_acelasi_mereu():
    a, b = ex.set_proba(), ex.set_proba()
    assert len(a) == len(ex.SABLOANE) == 20
    assert [x.teste for x in a] == [x.teste for x in b]
    assert len({p.sablon for p in a}) == 20
    assert all(len(p.teste) >= 4 for p in a)


def test_referintele_trec_toate_iar_golul_si_none_nu_trec_niciuna():
    rez = ex.verifica(ex.set_proba())
    assert rez["referinta"]["pass@1"] == 1.0, rez["referinta"]
    assert rez["gol"]["pass@1"] == 0.0, rez["gol"]
    assert rez["gresit"]["pass@1"] == 0.0, rez["gresit"]


def test_fiecare_sablon_are_destule_variante_diferite():
    probleme = ex.genereaza(123, ex.VARIANTE_ASCUNSE + 1)
    assert len(probleme) == 20 * (ex.VARIANTE_ASCUNSE + 1)
    assert len(ex.chei(probleme)) == len(probleme)
    assert len({p.enunt for p in probleme}) == len(probleme)


def test_pass_la_k():
    assert ex.pass_la_k(10, 0, 1) == 0.0
    assert ex.pass_la_k(10, 10, 10) == 1.0
    assert ex.pass_la_k(10, 3, 1) == pytest.approx(0.3)
    assert ex.pass_la_k(10, 1, 10) == 1.0
    assert ex.pass_la_k(20, 2, 10) == pytest.approx(1 - math.comb(18, 10) / math.comb(20, 10))
    with pytest.raises(ValueError):
        ex.pass_la_k(5, 1, 10)


def test_noteaza_cu_raspunsuri_amestecate():
    probleme = ex.set_proba()[:2]
    p0, p1 = probleme
    raspunsuri = {p0.id: [p0.referinta] * 3 + [ex.CORP_GOL] * 7, p1.id: [ex.CORP_GRESIT] * 9 + [p1.referinta]}
    nota = ex.noteaza(probleme, raspunsuri)
    assert nota["pass@1"] == pytest.approx((0.3 + 0.1) / 2)
    assert nota["pass@10"] == pytest.approx(1.0)
    assert nota["stari"]["ok"] == 4


def test_raspunsul_rau_e_prins_in_cutie_si_nu_trece():
    p = ex.set_proba()[0]
    nota = ex.noteaza([p], {p.id: ["    import os\n    return os.system('echo x')\n"]}, ks=(1,))
    assert nota["pass@1"] == 0.0 and nota["stari"] == {"interzis": 1}


def test_setul_ascuns_se_face_o_singura_data_si_ocoleste_setul_de_proba(tmp_path):
    info = ex.cmd_ascuns(tmp_path)
    assert info["probleme"] == 200
    probleme = ex.citeste_jsonl(tmp_path / "probleme.jsonl")
    assert len(probleme) == 200
    assert not ex.chei(probleme) & ex.chei(ex.set_proba())
    assert json.loads((tmp_path / "info.json").read_text())["sha256"] == info["sha256"]
    assert (tmp_path / "samanta.txt").exists()
    with pytest.raises(SystemExit):
        ex.cmd_ascuns(tmp_path)
