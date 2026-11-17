"""S124 (C-132, 17 nov 2026): examenul de formulări (notarea, construirea, verificările)."""

from __future__ import annotations

import json
import random
from pathlib import Path

import pytest

from unelte import conversatie_chat as cc
from unelte import examen_formulari as ef

RADACINA = Path(__file__).resolve().parent.parent
EXAMEN = RADACINA / ef.EXAMEN


def test_cotele_si_listele():
    assert sum(ef.COTE_CALCULE.values()) == 120 and sum(ef.COTE_SOCIALE.values()) == 80
    assert set(ef.COTE_SOCIALE) == set(cc.CUVINTE_CHEIE) == set(ef.SOCIALE)
    for c, n in ef.COTE_SOCIALE.items():
        assert len(ef.SOCIALE[c]) >= n
    for op, s in ef.SABLOANE_CALCULE.items():
        assert len(s) == 6 and len({ef.forma(x) for x in s}) == 6, op


def test_sabloanele_nu_sunt_in_generatoare_si_examene_vechi():
    perechi = ef.construieste(random.Random(0), set(), [(a, b) for a in range(1, 13) for b in range(1, 13)])
    assert not any(ef.sabloane_in(perechi, ef.sabloane_vechi()).values())


def test_construirea_respecta_interdictiile_si_cotele():
    interzise = {(a, b, "adunare") for a in range(1, 20) for b in range(1, 20)}
    inm = [(3, 7), (4, 5), (6, 6)] + [(a, 12) for a in range(1, 13)] + [(12, b) for b in range(1, 12)] + \
          [(a, 11) for a in range(1, 11)] + [(11, b) for b in range(1, 11)] + [(2, 2), (5, 5)]
    perechi = ef.construieste(random.Random(1), interzise, inm)
    calc = [p for p in perechi if p["parte"] == "calcul"]
    assert {k: sum(p["operatie"] == k for p in calc) for k in ef.COTE_CALCULE} == ef.COTE_CALCULE
    assert all((p["a"], p["b"], p["operatie"]) not in interzise for p in calc)
    assert all((p["a"], p["b"]) in set(inm) for p in calc if p["operatie"] == "inmultire")
    assert all(p["rezultat"] == cc.rezultat(p["operatie"], p["a"], p["b"]) for p in calc)
    assert sum(p["parte"] == "social" for p in perechi) == 80 and len({p["id"] for p in perechi}) == 200
    v = ef.verificari(perechi, interzise)
    assert not v["rezultate_gresite"] and not v["perechi_de_numere_repetate"] and not v["sociale_repetate"]


def test_bucatile_comune_se_gasesc():
    perechi = [{"id": "f1", "parte": "calcul", "intrebare": "Ana are 37 timbre, iar Mihai are 45. Câte timbre?"},
               {"id": "f2", "parte": "social", "intrebare": "Bine te-am găsit!"}]
    texte = ["Știm că ana are 37 timbre iar mihai are mult.", "Salut!\nRăspuns: Bună!\nÎntrebare: Bine te-am găsit!",
             "Altceva cu totul."]
    r = ef.bucati_comune(perechi, texte)
    assert r["cu_bucata_de_6"] == ["f1"] and r["sociale_identice"] == ["f2"] and r["texte_comparate"] == 3


def test_notarea():
    examen = {"cuvinte_cheie": cc.CUVINTE_CHEIE,
              "perechi": [{"id": "1", "parte": "calcul", "categorie": "inmultire", "operatie": "inmultire",
                           "a": 3, "b": 7, "rezultat": 21},
                          {"id": "2", "parte": "calcul", "categorie": "scadere", "operatie": "scadere",
                           "a": 9, "b": 4, "rezultat": 5},
                          {"id": "3", "parte": "social", "categorie": "multumesc"},
                          {"id": "4", "parte": "social", "categorie": "nu_stiu"}]}
    nota = ef.noteaza(examen, {"1": "3 × 7 = 21.", "2": "9 - 4 = 6.", "3": "Cu plăcere!", "4": "Nu scrie în text."})
    assert (nota["total"], nota["calcule"], nota["sociale"], nota["procent"]) == (2, 1, 1, 50.0)
    assert nota["pe_categorie"]["calcul_scadere"] == "0/1" and nota["nu_scrie_in_text"] == 1
    assert ef.taie("21.\nÎntrebare: x") == "21."


def test_refuza_sa_scrie_peste(tmp_path):
    f = tmp_path / "e.json"
    f.write_text("{}", encoding="utf-8")
    with pytest.raises(SystemExit):
        ef.main(["model", "--experiment", "1", "--iesire", str(f)])
    with pytest.raises(SystemExit):
        ef.main(["construieste", "--iesire", str(f)])


@pytest.mark.skipif(not EXAMEN.exists(), reason="examenul de formulări nu e scris")
def test_examenul_scris():
    ex = json.loads(EXAMEN.read_text(encoding="utf-8"))
    perechi = ex["perechi"]
    assert len(perechi) == 200 and ex["samanta"] == ef.SAMANTA and ex["cuvinte_cheie"] == cc.CUVINTE_CHEIE
    v = ex["verificari"]
    assert not any(v["sabloane_care_exista_deja"].values())
    assert not v["antrenare_existenta"]["cu_bucata_de_6"] and not v["antrenare_existenta"]["sociale_identice"]
    # numerele de înmulțire vin din examenul de calcule (deja interzise în generatoare)
    ex_calc = json.loads((RADACINA / "docs/conversatie/examen_calcule.json").read_text(encoding="utf-8"))
    inm = {(p["a"], p["b"]) for p in ex_calc["perechi"] if p["operatie"] == "inmultire"}
    assert all((p["a"], p["b"]) in inm for p in perechi if p.get("operatie") == "inmultire")
    calc_ex = {(p["a"], p["b"], p["operatie"]) for p in ex_calc["perechi"]}
    assert not any((p["a"], p["b"], p["operatie"]) in calc_ex for p in perechi
                   if p["parte"] == "calcul" and p["operatie"] != "inmultire")
