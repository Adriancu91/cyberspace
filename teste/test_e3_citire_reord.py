"""S33: E3 citește cu căutarea nouă — tabelul pe tipuri, examenul (o singură rulare, amprenta), verdictul după prag
(fără model adevărat, fără placă)."""

import hashlib
import json

import pytest

from unelte import e3_citire_reord as c
from unelte import e3_reordonare as r

from teste.test_e3_reordonare import _Tok, _index


def _rand(tip, s25, reord):
    return {"tip": tip, "loc": {"s25": s25, "rrf_reord": reord}}


def test_tabelul_pe_tipuri():
    rez = [_rand("definitie", 1, 1), _rand("definitie", 5, 2), _rand("nascut", None, 3), _rand("murit", 2, 9),
           _rand(None, 4, 4)]
    t = c.tabel_tipuri(rez)
    assert t["definitie"] == {"intrebari": 2, "procent_din_esantion": 40.0, "s25_k3": 1, "rrf_reord_k3": 2,
                              "castig": 1, "castig_puncte": 50.0}
    assert t["nascut"]["castig"] == 1 and t["an"]["intrebari"] == 0
    assert t["rest"]["intrebari"] == 2 and t["rest"]["castig"] == -1  # „murit” și fără tip intră la rest


def test_amestecul_din_fisiere(tmp_path):
    lucru = tmp_path / "e3"
    lucru.mkdir()
    (lucru / r.IESIRE_VALIDARE).write_text(json.dumps({"toate": {"s1024": [_rand("an", 1, 1)],
                                                                 "s2048": [_rand("regizat", 4, 1)]}}), encoding="utf-8")
    (lucru / r.IESIRE_EXAMEN).write_text(json.dumps({"toate": [_rand("definitie", 1, 1)]}), encoding="utf-8")
    info = c.cmd_amestec(lucru)
    assert info["impreuna"]["regizat"]["castig"] == 1 and info["s26_100"]["definitie"]["procent_din_esantion"] == 100.0
    assert (lucru / c.IESIRE_AMESTEC).exists()


def test_verdictul_dupa_prag():
    assert c.verdict(65, 60)["verdict"] == "CONFIRMAT"
    assert c.verdict(64, 60)["verdict"] == "NECLAR"
    assert c.verdict(62, 60)["verdict"] == "NECLAR"
    assert c.verdict(61, 60)["verdict"] == "INFIRMAT"
    assert c.verdict(55, 60) == {"verdict": "INFIRMAT", "diferenta": -5}


def test_examenul_o_singura_rulare_si_amprenta(tmp_path):
    lucru = tmp_path / "e3"
    randuri = [("Satele din Brașov sunt mici.", "w2"), ("Orașul Brașov are o cetate veche din 1400.", "w1"),
               ("Cluj are o universitate mare.", "w3")]
    _index(lucru / "index.sqlite", randuri).close()
    r.cmd_index_radacini(lucru)
    intrebari = [{"intrebare": "Ce are orașul Brașov?", "raspuns": "o cetate veche", "tip": "definitie"},
                 {"intrebare": "Ce are Cluj?", "raspuns": "o universitate", "tip": "an"}]
    (lucru / "examen_nou_4096.json").write_text(json.dumps(intrebari, ensure_ascii=False), encoding="utf-8")
    (lucru / "validare_s25.json").write_text(json.dumps({"aleasa": "nume_obligatorii_liste"}), encoding="utf-8")
    (lucru / "liste_s25.json").write_text(json.dumps({"fraze_lista": [], "randuri_scurte": []}), encoding="utf-8")
    sha = hashlib.sha256((lucru / "examen_nou_4096.json").read_bytes()).hexdigest()

    class Model:
        tok = _Tok()

    def raspunde(model, prompt):  # „modelul” spune prima bucată primită
        return prompt[len("Text: "):].split("\n")[0]

    paznic = []
    argumente = dict(incarca=lambda exp: (Model(), {"id": exp, "linie": "proba"}), raspunde=raspunde,
                     paznic=lambda: paznic.append(1),
                     judecator=lambda q, texte: [(float("cetate" in t), 1) for t in texte])  # cetatea urcă sus
    with pytest.raises(SystemExit):
        c.cmd_examen(lucru, 438, sha_examen="altceva", **argumente)
    info = c.cmd_examen(lucru, 438, sha_examen=sha, **argumente)
    assert info["intrebari"] == 2 and info["model"] == 438 and paznic == [1]
    s25, reord = info["variante"]["s25"], info["variante"]["rrf_reord"]
    assert reord["total"]["corecte"] >= s25["total"]["corecte"]
    assert reord["total"]["corecte"] == 2 and reord["pe_tip"]["definitie"] == {"intrebari": 1, "corecte": 1}
    assert info["verdict"] in {"INFIRMAT", "NECLAR"}  # pe 2 întrebări diferența e cel mult 2
    assert info["diferenta"] == reord["total"]["corecte"] - s25["total"]["corecte"]
    assert info["reper_s27"] is None and "prompt" not in info["toate"][0]["s25"]
    assert (lucru / c.IESIRE_EXAMEN).exists()
    with pytest.raises(SystemExit):
        c.cmd_examen(lucru, 438, sha_examen=sha, **argumente)
