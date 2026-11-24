"""S134: bancul de antrenare (unelte/banc_antrenare.py), pe un model mic și bucăți mici, doar procesor."""

from __future__ import annotations

import json

import numpy as np
import pytest
import torch

from module.date_bucati import DateBucati
from teste.bucati_mici import scrie_bucati
from unelte import banc_antrenare as ba
from unelte import pas_de_aur as pda

CPU = torch.device("cpu")


@pytest.fixture(autouse=True)
def fire_fixe():
    fire = torch.get_num_threads()
    torch.set_num_threads(1)
    yield
    torch.set_num_threads(fire)


@pytest.fixture
def date(tmp_path):
    return DateBucati(**scrie_bucati(tmp_path, marime=64))


def _retea(vocab: int):
    return pda.retea_mica(pda.SAMANTA, vocab=vocab, context=16)


def test_pozitiile_sunt_cele_din_DateBucati_lot(date):
    pasi, lot, context = 5, 3, 16
    poz, perechi = ba.loturi(date, pasi, lot, context, ba.SAMANTA)
    assert poz.shape == (pasi, lot) and poz.dtype == torch.int64
    g = torch.Generator().manual_seed(ba.SAMANTA)
    for k in range(pasi):
        x, y = date.lot(lot, context, g)
        assert torch.equal(x, perechi[k][0]) and torch.equal(y, perechi[k][1])
        assert torch.equal(x, date.ferestre(poz[k], context)[0])
    assert torch.equal(perechi[0][0][:, 1:], perechi[0][1][:, :-1])  # ținta = intrarea mutată cu 1


def test_doua_rulari_f32_dau_aceeasi_pierdere(date):
    vocab = date.sir_antrenare()[:].max().item() + 1
    _, perechi = ba.loturi(date, 3, 2, 16, ba.SAMANTA)
    r1 = ba.ruleaza(_retea(max(vocab, 320)), perechi, "f32", CPU)
    r2 = ba.ruleaza(_retea(max(vocab, 320)), perechi, "f32", CPU)
    assert [p["pierdere"] for p in r1["pasi"][:2]] == [p["pierdere"] for p in r2["pasi"][:2]]
    assert len(r1["pasi"]) == 3 and r1["oprit"] is None
    assert r1["media_pasi_2_n"]["pasi"] == 2 and r1["pas1"]["pas"] == 1
    assert all(p["ms"] > 0 and p["simb_s"] > 0 and p["norma_gradient"] > 0 for p in r1["pasi"])


def test_bf16_fata_de_f32_la_pasul_1_cel_mult_2_la_suta(date):
    _, perechi = ba.loturi(date, 1, 2, 16, ba.SAMANTA)
    f32 = ba.ruleaza(_retea(320), perechi, "f32", CPU)["pasi"][0]["pierdere"]
    bf16 = ba.ruleaza(_retea(320), perechi, "bf16", CPU)["pasi"][0]["pierdere"]
    assert f32 != bf16
    assert abs(bf16 - f32) / f32 <= 0.02


def test_pasul_e_adamw_513_si_schimba_greutatile(date):
    _, perechi = ba.loturi(date, 2, 2, 16, ba.SAMANTA)
    retea = _retea(320)
    inainte = {n: p.detach().clone() for n, p in retea.named_parameters()}
    opt = ba.optimizator(retea)
    g = opt.defaults
    assert type(opt).__name__ == "AdamW" and g["lr"] == 5e-5 and g["weight_decay"] == 0.1
    assert list(g["betas"]) == [0.9, 0.999] and g["eps"] == 1e-8
    ba.ruleaza(retea, perechi, "f32", CPU)
    assert any(not torch.equal(inainte[n], p) for n, p in retea.named_parameters())


def test_iesirea_si_refuzul(date, tmp_path):
    poz, perechi = ba.loturi(date, 2, 2, 16, ba.SAMANTA)
    r = ba.ruleaza(_retea(320), perechi, "f32", CPU)
    dosar = tmp_path / "iesire"
    ba.scrie_iesire(dosar, poz, r, {"x": 1})
    citit = np.fromfile(dosar / "loturi.i64", dtype="<i8").reshape(2, 2)
    assert (citit == poz.numpy()).all()
    reteta = json.loads((dosar / "reteta.json").read_text(encoding="utf-8"))
    assert reteta["loturi.i64"]["forma"] == [2, 2]
    assert json.loads((dosar / "rezultat.json").read_text(encoding="utf-8"))["pasi"][0]["pas"] == 1
    with pytest.raises(SystemExit):
        ba.main(["--iesire", str(dosar)])


def test_precizie_necunoscuta():
    with pytest.raises(ValueError):
        ba.autocast(CPU, "f16")
