"""S131 (supraveghetor, 21 nov 2026): pasul `formulari4` din `conversatie_chat.py` (r2 × 3) și configurarea liniei 24zcj."""

from __future__ import annotations

import json
import random
from collections import Counter
from pathlib import Path

import pytest

from unelte import conversatie_chat as cc

RADACINA = Path(__file__).resolve().parent.parent


def test_singura_schimbare_fata_de_s129_e_r2_de_3_ori():
    assert cc.ORI_R2_6 == 3 and cc.ORI_R2_5 == 2  # S129 rămâne neschimbat
    assert (cc.ORI_CHAT5, cc.ORI_CALCULE5) == (5, 4)
    assert cc.COTE_CALCULE5 == {"adunare": 800, "scadere": 800, "inmultire": 800, "impartire": 800}
    assert cc.SAMANTA_FORMULARI4 == 1131 and cc.SAMANTA_FORMULARI3 == 1129
    assert cc.DOSAR6 == "lucru/conversatie_chat6" and cc.DOSAR5 == "lucru/conversatie_chat5"


def test_aceeasi_samanta_da_aceeasi_iesire():
    def gen():
        return cc.perechi_calcule_s124(random.Random(cc.SAMANTA_FORMULARI4), {(3, 7, "adunare"), (4, 9, "inmultire")},
                                       {"adunare": 30, "inmultire": 50, "impartire": 30}, cc.formulari_calcule_s127())
    a = gen()
    assert a == gen()
    assert Counter(p["tip"] for p in a) == {"adunare": 30, "inmultire": 50, "impartire": 30}
    # altă sămânță decât S129: alte perechi
    b = cc.perechi_calcule_s124(random.Random(cc.SAMANTA_FORMULARI3), {(3, 7, "adunare"), (4, 9, "inmultire")},
                                {"adunare": 30, "inmultire": 50, "impartire": 30}, cc.formulari_calcule_s127())
    assert a != b


def test_r2_apare_de_3_ori_iar_chat_5_si_calcule_4():
    r2 = [json.dumps({"id": f"r{i}", "intrebare": "Ce?", "raspuns": "x", "text": "t"}) for i in range(3)]
    chat = [cc._pereche("chat", "x", "Salut!", "Salut.")]
    calc = [dict(cc._pereche("chat_calcul", "adunare", "Cât face 2 + 2?", "4.", "4"), numere=[2, 2])]
    randuri = cc.randuri_amestec_s131(r2, chat, calc)
    n = Counter(randuri)
    assert all(n[r] == 3 for r in r2)
    assert n[json.dumps(chat[0], ensure_ascii=False)] == 5
    assert n[json.dumps(calc[0], ensure_ascii=False)] == 4
    assert len(randuri) == 3 * 3 + 5 + 4
    # S129 (r2 × 2) neschimbat
    assert len(cc.randuri_amestec_s129(r2, chat, calc)) == 3 * 2 + 5 + 4


def test_zero_scurgeri_pe_un_exemplu_mic():
    examen = [{"id": "f1", "parte": "calcul", "operatie": "adunare", "a": 12, "b": 9,
               "intrebare": "Ana are 12 mere și primește încă 9 mere de la bunica. Câte mere are acum?"}]
    b6 = cc.bucati_examene_s127([examen])
    perechi = [dict(cc._pereche("chat_calcul", "adunare", "Cât face 3 + 5?", "8.", "8"), numere=[3, 5]),
               cc._pereche("din_text", "x", "Ce?", "Ea primește încă 9 mere de la bunica, deci are 21.")]
    rau = cc.indici_bucati_s127(perechi, b6)
    assert rau == {1}
    curate = [p for i, p in enumerate(perechi) if i not in rau]
    assert cc.indici_bucati_s127(curate, b6) == set()


def test_formulari4_refuza_daca_dosarul_exista(tmp_path):
    (tmp_path / cc.DOSAR6).mkdir(parents=True)
    with pytest.raises(SystemExit):
        cc.main(["formulari4", "--radacina", str(tmp_path)])


# --- configurarea S131 (linia „24zcj”) ------------------------------------------------------------------------------
CONFIG_NOU = RADACINA / "config" / "conv_w2_mare_24zcj.toml"


@pytest.mark.skipif(not CONFIG_NOU.exists(), reason="configurarea 24zcj nu e scrisă")
def test_24zcj_difera_de_24zci_doar_prin_ce_cere_sarcina():
    import tomllib

    vechi = (RADACINA / "config" / "conv_w2_mare_24zci.toml").read_text(encoding="utf-8").splitlines()
    nou = CONFIG_NOU.read_text(encoding="utf-8").splitlines()
    f = tomllib.loads("\n".join(vechi))
    g = tomllib.loads("\n".join(nou))
    assert g["platforma"]["nume"] == "w2_mare_24zcj"
    sf, sg = f["porturi"]["model"]["setari"], g["porturi"]["model"]["setari"]
    assert {k for k in sf.keys() | sg.keys() if sf.get(k) != sg.get(k)} == {"cale_stare", "conversatie"}
    assert sg["cale_stare"] == "lucru/w2_mare_24zcj/gpt.pt"
    assert sg["conversatie"] == "lucru/conversatie_chat6/antrenare.jsonl"
    assert sg["fractie_conversatie"] == 0.45
    fp, gp = dict(f["platforma"]), dict(g["platforma"])
    fp.pop("nume"), gp.pop("nume")
    assert fp == gp and f["paznic"] == g["paznic"] and f["criterii"] == g["criterii"]
    assert f["antrenare_lunga"] == g["antrenare_lunga"]
    for port in f["porturi"]:
        if port != "model":
            assert f["porturi"][port] == g["porturi"][port], port

    def corp(r):
        return r[next(i for i, x in enumerate(r) if x == "[platforma]"):]
    cv, cn = corp(vechi), corp(nou)
    assert len(cv) == len(cn)
    assert len([1 for a, b in zip(cv, cn) if a != b]) == 2
