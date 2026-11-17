"""S124 (C-132, 17 nov 2026): generatorul de formulări (`conversatie_chat.py formulari`) și configurarea 24zcf."""

from __future__ import annotations

import json
import random
import tomllib
from pathlib import Path

import pytest

from unelte import conversatie_chat as cc
from unelte import examen_calcule as ek
from unelte import examen_formulari as ef

RADACINA = Path(__file__).resolve().parent.parent
EX_FORM = RADACINA / cc.EXAMEN_FORMULARI


def _forma(s: str) -> str:
    return cc.formulare_fara_numere(s.format(a=3, b=7))


def test_cel_putin_de_3_ori_mai_multe_sabloane():
    calc, soc = cc.formulari_calcule_s124(), cc.sociale_s124()
    for op, fs in calc.items():
        assert len({_forma(s) for s in fs}) >= 3 * len({_forma(s) for s in cc.FORMULARI_CALCULE[op]}), op
        assert {_forma(s) for s in cc.FORMULARI_CALCULE[op]} <= {_forma(s) for s in fs}  # cele vechi rămân
    for c, qs in soc.items():
        assert len({cc.norm(q) for q in qs}) >= 3 * len({cc.norm(q) for q in cc.SOCIAL_INTREBARI[c]}), c


def test_pasii_vechi_raman_la_fel():
    # listele vechi neschimbate (ieșirile S116/S120 se refac din ele)
    assert len(cc.FORMULARI_CALCULE["adunare"]) == 8 and len(cc.SOCIAL_INTREBARI["salut"]) == 17
    p = cc.perechi_calcule(random.Random(1), set(), {"adunare": 3})
    assert all(q["fel"] == "chat_calcul" for q in p)


def test_sabloanele_din_examene_se_scot():
    ex = {"sabloane_calcule": {"adunare": ["Cât face {a} plus {b}?"]},
          "perechi": [{"parte": "social", "intrebare": "Salut!"}]}
    calc, soc, scoase = cc.scoate_sabloane_examen({"adunare": ["Cât face {a} plus {b}?", "Adună {a} și {b}."]},
                                                  {"salut": ["Salut!", "Hei!", "Salutări!"]}, ex)
    assert calc == {"adunare": ["Adună {a} și {b}."]} and soc == {"salut": ["Hei!"]}
    assert sorted(scoase) == ["Cât face {a} plus {b}?", "Salut!", "Salutări!"]  # „Salutări!” e în examenul S116


def test_perechile_noi_sunt_corecte_si_ocolesc_interzisele():
    interzise = {(3, 7, "inmultire"), (56, 8, "impartire")}
    perechi = cc.perechi_calcule_s124(random.Random(2), interzise, {"inmultire": 200, "impartire": 100},
                                      cc.formulari_calcule_s124())
    for p in perechi:
        a, b = p["numere"]
        assert (a, b, p["tip"]) not in interzise
        assert ek.corect({"a": a, "b": b, "rezultat": cc.rezultat(p["tip"], a, b)}, p["raspuns"]), p
    soc = cc.perechi_sociale_s124(random.Random(3), cc.sociale_s124())
    pe_tip = {}
    for p in soc:
        pe_tip[p["tip"]] = pe_tip.get(p["tip"], 0) + 1
        assert "text" not in p and p["fel"] == "chat_social"
    assert pe_tip["salut_ce_faci"] == 170
    for c, qs in cc.SOCIAL_INTREBARI.items():
        assert pe_tip[c] >= 15 * len(qs)
    # fiecare întrebare nouă apare măcar o dată
    assert {p["intrebare"] for p in soc if p["tip"] == "nu_stiu"} == set(cc.sociale_s124()["nu_stiu"])


def test_scurgerile_formularilor():
    ex = [{"id": "f1", "parte": "calcul", "operatie": "adunare", "a": 37, "b": 45,
           "intrebare": "Ana are 37 timbre, iar Mihai are 45. Câte timbre au împreună?"},
          {"id": "f2", "parte": "social", "intrebare": "Bine te-am găsit!"}]
    perechi = [dict(cc._pereche("chat_calcul", "adunare", "Cât face 37 + 45?", "82.", "82"), numere=[37, 45]),
               cc._pereche("chat_social", "salut", "Bine te-am găsit!", "Bună!"),
               cc._pereche("din_text", "x", "Ce?", "Ana are 37 timbre, iar Mihai are 45."),
               cc._pereche("chat_social", "salut", "Salut!", "Bună!")]
    s = cc.scurgeri_formulari(perechi, ex)
    assert s["pereche_de_numere"] == [0] and s["intrebare_identica"] == [1] and s["bucata_de_6"] == [2]


def test_indicii_scurgerilor_vechi():
    ex_calc = [{"a": 3, "b": 7, "operatie": "inmultire", "intrebare": "Cât face 3 x 7?"}]
    ex_chat = [{"parte": "b", "intrebare": "Cu cine vorbesc?"}]
    perechi = [dict(cc._pereche("chat_calcul", "inmultire", "Cât face 7 x 3?", "21.", "21"), numere=[7, 3]),
               dict(cc._pereche("chat_calcul", "inmultire", "3 ori 7?", "21.", "21"), numere=[3, 7]),
               cc._pereche("din_text", "x", "Cu cine vorbesc?", "Cu Kronos.")]
    assert cc.indici_scurgeri_calcule(perechi, ex_chat, ex_calc) == {1, 2}
    assert sum(cc.scurgeri_calcule(perechi, ex_chat, ex_calc).values()) == 2  # aceleași reguli (identică + numere)


@pytest.mark.skipif(not EX_FORM.exists(), reason="examenul de formulări nu e scris")
def test_generatorul_nu_atinge_examenul_de_formulari():
    ex = json.loads(EX_FORM.read_text(encoding="utf-8"))
    calc, soc, _ = cc.scoate_sabloane_examen(cc.formulari_calcule_s124(), cc.sociale_s124(), ex)
    f_ex = {_forma(s) for fs in ex["sabloane_calcule"].values() for s in fs}
    assert not {_forma(s) for fs in calc.values() for s in fs} & f_ex
    q_ex = {cc.norm(p["intrebare"]) for p in ex["perechi"] if p["parte"] == "social"}
    assert not {cc.norm(q) for qs in soc.values() for q in qs} & q_ex
    assert ef.interzise_examen(ex)  # perechile de numere ale examenului se interzic în generator
    # și după ce se scot șabloanele examenelor rămân de cel puțin 3 ori mai multe
    for op, fs in calc.items():
        assert len({_forma(s) for s in fs}) >= 3 * len({_forma(s) for s in cc.FORMULARI_CALCULE[op]}), op
    for c, qs in soc.items():
        assert len({cc.norm(q) for q in qs}) >= 3 * len({cc.norm(q) for q in cc.SOCIAL_INTREBARI[c]}), c


# --- configurarea S124 -----------------------------------------------------------------------------------------------
def _config(nume: str) -> dict:
    return tomllib.loads((RADACINA / "config" / nume).read_text(encoding="utf-8"))


def test_24zcf_difera_de_24zcc_doar_prin_ce_cere_sarcina():
    c, f = _config("conv_w2_mare_24zcc.toml"), _config("conv_w2_mare_24zcf.toml")
    sc, sf = c["porturi"]["model"]["setari"], f["porturi"]["model"]["setari"]
    assert {k for k in sc.keys() | sf.keys() if sc.get(k) != sf.get(k)} == {"cale_stare", "conversatie"}
    assert sf["cale_stare"] == "lucru/w2_mare_24zcf/gpt.pt"
    assert sf["conversatie"] == "lucru/conversatie_chat3/antrenare.jsonl"
    assert f["platforma"]["nume"] == "w2_mare_24zcf"
    cp, fp = dict(c["platforma"]), dict(f["platforma"])
    cp.pop("nume"), fp.pop("nume")
    assert cp == fp and c["paznic"] == f["paznic"] and c["criterii"] == f["criterii"]
    for port in c["porturi"]:
        if port != "model":
            assert c["porturi"][port] == f["porturi"][port], port
    assert c["porturi"]["model"]["modul"] == f["porturi"]["model"]["modul"]
    assert set(c) == set(f)
