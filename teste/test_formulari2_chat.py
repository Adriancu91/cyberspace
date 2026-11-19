"""S127 (supraveghetor, 19 nov 2026): pasul `formulari2` din `conversatie_chat.py` și configurarea 24zcg."""

from __future__ import annotations

import json
import random
import tomllib
from pathlib import Path

import pytest

from unelte import conversatie_chat as cc
from unelte import examen_calcule as ek

RADACINA = Path(__file__).resolve().parent.parent
EX_FORM = RADACINA / cc.EXAMEN_FORMULARI


def _forma(s: str) -> str:
    return cc.formulare_fara_numere(s.format(a=3, b=7))


def test_de_3_ori_mai_multe_sabloane_decat_s124_la_adunare_scadere_impartire():
    s124, s127 = cc.formulari_calcule_s124(), cc.formulari_calcule_s127()
    for op in ("adunare", "scadere", "impartire"):
        assert len({_forma(s) for s in s127[op]}) >= 3 * len({_forma(s) for s in s124[op]}), op
    for op in s124:  # cele S124 rămân
        assert {_forma(s) for s in s124[op]} <= {_forma(s) for s in s127[op]}, op


def test_pasul_s124_ramane_la_fel():
    s124 = cc.formulari_calcule_s124()
    assert {op: len({_forma(s) for s in fs}) for op, fs in s124.items()} == {
        "adunare": 47, "scadere": 45, "inmultire": 81, "impartire": 44}


def test_aceeasi_samanta_da_aceeasi_iesire():
    def gen():
        return cc.perechi_calcule_s124(random.Random(cc.SAMANTA_FORMULARI2), {(3, 7, "adunare")},
                                       {"adunare": 50, "scadere": 50, "impartire": 50}, cc.formulari_calcule_s127())
    assert gen() == gen()


def test_perechile_sunt_corecte_si_ocolesc_interzisele_si_intoarsele():
    interz = cc.interzise_s127({(3, 7, "adunare"), (56, 8, "impartire"), (4, 9, "inmultire")})
    assert (7, 3, "adunare") in interz and (9, 4, "inmultire") in interz and (8, 56, "impartire") not in interz
    perechi = cc.perechi_calcule_s124(random.Random(5), interz, {"adunare": 300, "scadere": 300, "impartire": 300},
                                      cc.formulari_calcule_s127())
    for p in perechi:
        a, b = p["numere"]
        assert (a, b, p["tip"]) not in interz
        assert ek.corect({"a": a, "b": b, "rezultat": cc.rezultat(p["tip"], a, b)}, p["raspuns"]), p
        assert "{" not in p["intrebare"]


def test_prefixul_nu_strica_numele_proprii():
    assert cc._cu_prefix("Kronos, ", "Ana are {a} lei.") == "Kronos, Ana are {a} lei."
    assert cc._cu_prefix("Te rog, ", "Am {a} mere.") == "Te rog, am {a} mere."
    assert cc._cu_prefix("Hai, ", "{a} lei se împart.") == "Hai, {a} lei se împart."


def test_zero_scurgeri_pe_un_exemplu_mic():
    examen = [{"id": "f1", "parte": "calcul", "operatie": "adunare", "a": 37, "b": 45,
               "intrebare": "Ana are 37 timbre si Mihai are 45 timbre. Cate au impreuna?"}]
    b6 = cc.bucati_examene_s127([examen])
    perechi = [dict(cc._pereche("chat_calcul", "adunare", "Cât face 12 + 5?", "17.", "17"), numere=[12, 5]),
               cc._pereche("din_text", "x", "Ce?", "Știm că Ana are 37 timbre si Mihai are 45 de ani.")]
    assert cc.indici_bucati_s127(perechi, b6) == {1}  # „ana are 37 timbre si mihai” = 6 cuvinte la rând
    curate = [p for i, p in enumerate(perechi) if i not in cc.indici_bucati_s127(perechi, b6)]
    assert cc.indici_bucati_s127(curate, b6) == set()


@pytest.mark.skipif(not EX_FORM.exists(), reason="examenul de formulări nu e scris")
def test_sabloanele_s127_nu_sunt_in_examen_dupa_scoatere():
    ex = json.loads(EX_FORM.read_text(encoding="utf-8"))
    calc, _, _ = cc.scoate_sabloane_examen(cc.formulari_calcule_s127(), cc.sociale_s124(), ex)
    f_ex = {_forma(s) for fs in ex["sabloane_calcule"].values() for s in fs}
    assert not {_forma(s) for fs in calc.values() for s in fs} & f_ex
    s124 = cc.scoate_sabloane_examen(cc.formulari_calcule_s124(), cc.sociale_s124(), ex)[0]
    for op in ("adunare", "scadere", "impartire"):
        assert len({_forma(s) for s in calc[op]}) >= 3 * len({_forma(s) for s in s124[op]}), op


def test_formulari2_refuza_daca_dosarul_exista(tmp_path):
    (tmp_path / cc.DOSAR4).mkdir(parents=True)
    with pytest.raises(SystemExit):
        cc.main(["formulari2", "--radacina", str(tmp_path)])


# --- configurarea S127 -----------------------------------------------------------------------------------------------
CONFIG_NOU = RADACINA / "config" / "conv_w2_mare_24zcg.toml"


@pytest.mark.skipif(not CONFIG_NOU.exists(), reason="configurarea 24zcg nu e scrisă")
def test_24zcg_difera_de_24zcf_doar_prin_ce_cere_sarcina():
    vechi = (RADACINA / "config" / "conv_w2_mare_24zcf.toml").read_text(encoding="utf-8").splitlines()
    nou = CONFIG_NOU.read_text(encoding="utf-8").splitlines()
    f = tomllib.loads("\n".join(vechi))
    g = tomllib.loads("\n".join(nou))
    assert g["platforma"]["nume"] == "w2_mare_24zcg"
    sf, sg = f["porturi"]["model"]["setari"], g["porturi"]["model"]["setari"]
    assert {k for k in sf.keys() | sg.keys() if sf.get(k) != sg.get(k)} == {"cale_stare", "conversatie"}
    assert sg["cale_stare"] == "lucru/w2_mare_24zcg/gpt.pt"
    assert sg["conversatie"] == "lucru/conversatie_chat4/antrenare.jsonl"
    fp, gp = dict(f["platforma"]), dict(g["platforma"])
    fp.pop("nume"), gp.pop("nume")
    assert fp == gp and f["paznic"] == g["paznic"] and f["criterii"] == g["criterii"]
    for port in f["porturi"]:
        if port != "model":
            assert f["porturi"][port] == g["porturi"][port], port
    # în afara antetului (comentariile de sus), doar 2 rânduri diferă: `nume` și rândul `setari` al modelului
    assert len(vechi) == len(nou)
    fara_antet = [(a, b) for a, b in zip(vechi, nou) if a != b and not a.startswith("#") and not b.startswith("#")]
    assert len(fara_antet) == 2
