"""S129 (supraveghetor, 20 nov 2026): pasul `formulari3` din `conversatie_chat.py` (configurarea așteaptă un nume nou de linie: 24zch e al lui S117)."""

from __future__ import annotations

import json
import random
from collections import Counter
from pathlib import Path

import pytest

from unelte import conversatie_chat as cc
from unelte import examen_calcule as ek

RADACINA = Path(__file__).resolve().parent.parent


def test_doar_inmultirea_creste_la_800():
    assert cc.COTE_CALCULE5 == {**cc.COTE_CALCULE4, "inmultire": 800}
    assert cc.COTE_CALCULE4["inmultire"] == 500  # S127 rămâne neschimbat
    assert (cc.ORI_CHAT5, cc.ORI_CALCULE5, cc.ORI_R2_5) == (5, 4, 2)
    trei = sum(v for k, v in cc.COTE_CALCULE5.items() if k != "inmultire")
    assert 3 * trei >= 2 * sum(cc.COTE_CALCULE5.values())  # adunare + scădere + împărțire ≥ 2/3


def test_aceeasi_samanta_da_aceeasi_iesire():
    def gen():
        return cc.perechi_calcule_s124(random.Random(cc.SAMANTA_FORMULARI3), {(3, 7, "adunare"), (4, 9, "inmultire")},
                                       {"adunare": 30, "inmultire": 200, "impartire": 30}, cc.formulari_calcule_s127())
    a = gen()
    assert a == gen()
    assert Counter(p["tip"] for p in a)["inmultire"] == 200


def test_inmultirile_sunt_corecte_si_ocolesc_interzisele():
    interz = cc.interzise_s127({(4, 9, "inmultire"), (7, 8, "inmultire")})
    perechi = cc.perechi_calcule_s124(random.Random(cc.SAMANTA_FORMULARI3), interz, {"inmultire": 800},
                                      cc.formulari_calcule_s127())
    assert len(perechi) == 800
    for p in perechi:
        a, b = p["numere"]
        assert (a, b, "inmultire") not in interz
        assert ek.corect({"a": a, "b": b, "rezultat": a * b}, p["raspuns"]), p


def test_r2_apare_de_2_ori_iar_chat_5_si_calcule_4():
    r2 = [json.dumps({"id": f"r{i}", "intrebare": "Ce?", "raspuns": "x", "text": "t"}) for i in range(3)]
    chat = [cc._pereche("chat", "x", "Salut!", "Salut.")]
    calc = [dict(cc._pereche("chat_calcul", "adunare", "Cât face 2 + 2?", "4.", "4"), numere=[2, 2])]
    randuri = cc.randuri_amestec_s129(r2, chat, calc)
    n = Counter(randuri)
    assert all(n[r] == 2 for r in r2)
    assert n[json.dumps(chat[0], ensure_ascii=False)] == 5
    assert n[json.dumps(calc[0], ensure_ascii=False)] == 4
    assert len(randuri) == 3 * 2 + 5 + 4


def test_zero_scurgeri_pe_un_exemplu_mic():
    examen = [{"id": "f1", "parte": "calcul", "operatie": "inmultire", "a": 6, "b": 7,
               "intrebare": "O cutie are 6 rânduri a câte 7 bomboane fiecare. Câte bomboane sunt?"}]
    b6 = cc.bucati_examene_s127([examen])
    perechi = [dict(cc._pereche("chat_calcul", "inmultire", "Cât face 3 x 5?", "15.", "15"), numere=[3, 5]),
               cc._pereche("din_text", "x", "Ce?", "Avem 6 rânduri a câte 7 bomboane fiecare, deci 42.")]
    assert cc.indici_bucati_s127(perechi, b6) == {1}
    curate = [p for i, p in enumerate(perechi) if i not in cc.indici_bucati_s127(perechi, b6)]
    assert cc.indici_bucati_s127(curate, b6) == set()


def test_formulari3_refuza_daca_dosarul_exista(tmp_path):
    (tmp_path / cc.DOSAR5).mkdir(parents=True)
    with pytest.raises(SystemExit):
        cc.main(["formulari3", "--radacina", str(tmp_path)])
