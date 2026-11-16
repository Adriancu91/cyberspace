"""S120 (C-128 A, 16 nov 2026): examenul de calcule (notarea, construirea), perechile de calcule, scurgerile, amestecul
și configurarea 24zcc."""

from __future__ import annotations

import json
import random
import tomllib
from pathlib import Path

import pytest

from unelte import conversatie_chat as cc
from unelte import examen_calcule as ek

RADACINA = Path(__file__).resolve().parent.parent
EXAMEN = RADACINA / ek.EXAMEN


def _p(a, b, op):
    return {"id": "x", "a": a, "b": b, "operatie": op, "rezultat": cc.rezultat(op, a, b)}


def test_notarea_unui_raspuns():
    p = _p(3, 7, "inmultire")
    assert ek.corect(p, "21.")
    assert ek.corect(p, "3 × 7 = 21.")
    assert ek.corect(p, "Rezultatul este 21.")
    assert not ek.corect(p, "3 × 7 = 24.")          # alt număr ca rezultat
    assert not ek.corect(p, "21 sau 24.")            # alt număr diferit
    assert not ek.corect(p, "21 = 3 + 18.")          # după „=” nu e rezultatul
    assert not ek.corect(p, "Nu scrie în text.")
    assert not ek.corect(p, "21,5.")                 # număr cu virgulă = alt număr
    assert not ek.corect(p, "210.")                  # număr întreg, nu bucată
    # ecoul întrebării nu e rezultat, chiar dacă rezultatul e un număr din întrebare
    assert not ek.corect(_p(2, 1, "scadere"), "2 lei și 1. Câți bani îmi rămân?")
    assert ek.corect(_p(2, 1, "scadere"), "2 - 1 = 1.") and ek.corect(_p(2, 1, "scadere"), "1.")
    assert ek.corect(_p(1, 11, "inmultire"), "1 × 11 = 11.") and not ek.corect(_p(1, 11, "inmultire"), "1 × 11.")
    assert ek.corect(_p(7, 3, "inmultire"), "3 × 7 = 21.")
    m = _p(400, 600, "adunare")
    assert ek.corect(m, "1.000.") and ek.corect(m, "400 + 600 = 1000.")
    assert ek.numere_din("Am 1.204 mere și 3,5 kg.") == [1204, 3.5]


def test_noteaza_pe_operatii():
    examen = {"perechi": [dict(_p(3, 7, "inmultire"), id="1", formulare="noua"),
                          dict(_p(56, 8, "impartire"), id="2", formulare="generator")]}
    nota = ek.noteaza(examen, {"1": "21.", "2": "Nu scrie în text."})
    assert nota["total"] == 1 and nota["pe_operatie"] == {"inmultire": "1/1", "impartire": "0/1"}
    assert nota["nu_scrie_in_text"] == 1 and nota["fara_niciun_numar"] == 1
    assert ek.taie("21.\nÎntrebare: x") == "21."


def test_numerele_calculelor_respecta_limitele():
    rng = random.Random(0)
    for k in range(600):
        for op in cc.FORMULARI_CALCULE:
            a, b = cc.numere_calcul(op, rng, k)
            r = cc.rezultat(op, a, b)
            if op in ("adunare", "scadere"):
                assert 0 < a <= 1000 and 0 < b <= 1000 and 0 < r <= 1000
            elif op == "inmultire":
                assert 1 <= a <= 12 and 1 <= b <= 12
            else:
                assert a % b == 0 and 1 <= r <= 100 and 2 <= b <= 12


def test_formularile_noi_ale_examenului_nu_sunt_in_generator():
    gen = {cc.formulare_fara_numere(f.format(a=3, b=7)) for fs in cc.FORMULARI_CALCULE.values() for f in fs}
    for op, fs in ek.FORMULARI_NOI.items():
        assert len(fs) >= 4 and len(cc.FORMULARI_CALCULE[op]) >= 5
        for f in fs:
            assert cc.formulare_fara_numere(f.format(a=3, b=7)) not in gen, f
    assert cc.formulare_fara_numere("Cât face 3x7?") == "cat face n x n"


def test_perechile_de_calcule_ocolesc_examenul_si_sunt_corecte():
    interzise = {(3, 7, "inmultire"), (56, 8, "impartire")}
    perechi = cc.perechi_calcule(random.Random(1), interzise, {"inmultire": 300, "impartire": 200, "adunare": 50})
    assert len(perechi) == 550
    for p in perechi:
        a, b = p["numere"]
        assert (a, b, p["tip"]) not in interzise
        assert "text" not in p and p["fel"] == "chat_calcul" and p["prompt"].startswith("Întrebare: ")
        assert ek.corect(dict(_p(a, b, p["tip"]), id="x"), p["raspuns"]), p
        assert cc.NU_SCRIE not in cc.norm(p["raspuns"])
    assert len({tuple(p["numere"]) for p in perechi if p["tip"] == "inmultire"}) == 143


def test_scurgerile_calculelor():
    ex_calc = [dict(_p(3, 7, "inmultire"), intrebare="Cât face 3 x 7?")]
    ex_chat = [{"parte": "b", "intrebare": "Cu cine vorbesc?"}]
    perechi = [dict(cc._pereche("chat_calcul", "inmultire", "Cât face 3 x 7?", "21.", "21"), numere=[3, 7]),
               dict(cc._pereche("chat_calcul", "inmultire", "Cât face 7 x 3?", "21.", "21"), numere=[7, 3]),
               dict(cc._pereche("chat_calcul", "adunare", "Cât face 3 + 7?", "10.", "10"), numere=[3, 7]),
               cc._pereche("din_text", "x", "Cu cine vorbesc?", "Cu Kronos.")]
    s = cc.scurgeri_calcule(perechi, ex_chat, ex_calc)
    assert s["pereche_de_numere_din_examen_calcule"] == 1  # doar (3, 7, înmulțire); 7×3 și 3+7 au voie
    assert s["intrebare_identica_cu_examenul"] == 2        # „Cât face 3 x 7?” și „Cu cine vorbesc?”


def test_ori_calcule():
    ori_h, ori_c = cc.ori_calcule(s_chat=600_000, s_calc=50_000, s_vechi=3_200_000)
    total = 600_000 * ori_h + 50_000 * ori_c
    assert 0.10 <= 50_000 * ori_c / total <= 0.15
    assert 0.45 <= total / (total + 3_200_000) <= 0.55


@pytest.mark.skipif(not EXAMEN.exists(), reason="examenul de calcule nu e scris")
def test_examenul_de_calcule_scris():
    ex = json.loads(EXAMEN.read_text(encoding="utf-8"))
    perechi = ex["perechi"]
    assert len(perechi) == 200 and ex["samanta"] == 128
    assert {k: sum(p["operatie"] == k for p in perechi) for k in ek.COTE} == ek.COTE
    assert sum(p["formulare"] == "noua" for p in perechi) >= 60
    assert all(p["rezultat"] == cc.rezultat(p["operatie"], p["a"], p["b"]) for p in perechi)
    assert len({(p["a"], p["b"], p["operatie"]) for p in perechi}) == 200
    assert ex["verificari"] == ek.verificari(perechi)
    # examenul se reface identic din sămânță (scris o singură dată, dar verificabil)
    assert [p["intrebare"] for p in ek.construieste(random.Random(ek.SAMANTA))] == [p["intrebare"] for p in perechi]


def test_examen_calcule_refuza_sa_scrie_peste(tmp_path):
    f = tmp_path / "e.json"
    f.write_text("{}", encoding="utf-8")
    with pytest.raises(SystemExit):
        ek.main(["model", "--experiment", "1", "--iesire", str(f)])
    with pytest.raises(SystemExit):
        ek.main(["construieste", "--iesire", str(f)])


# --- configurarea S121 -----------------------------------------------------------------------------------------------
def _config(nume: str) -> dict:
    return tomllib.loads((RADACINA / "config" / nume).read_text(encoding="utf-8"))


def test_24zcc_difera_de_24zch_doar_prin_ce_cere_sarcina():
    h, c = _config("conv_w2_mare_24zch.toml"), _config("conv_w2_mare_24zcc.toml")
    sh, sc = h["porturi"]["model"]["setari"], c["porturi"]["model"]["setari"]
    assert {k for k in sh.keys() | sc.keys() if sh.get(k) != sc.get(k)} == {"cale_stare", "conversatie"}
    assert sc["cale_stare"] == "lucru/w2_mare_24zcc/gpt.pt"
    assert sc["conversatie"] == "lucru/conversatie_chat2/antrenare.jsonl"
    assert c["platforma"]["nume"] == "w2_mare_24zcc"
    hp, cp = dict(h["platforma"]), dict(c["platforma"])
    hp.pop("nume"), cp.pop("nume")
    assert hp == cp and h["paznic"] == c["paznic"]
    for port in h["porturi"]:
        if port != "model":
            assert h["porturi"][port] == c["porturi"][port], port
    assert h["porturi"]["model"]["modul"] == c["porturi"]["model"]["modul"]
