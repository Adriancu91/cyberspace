"""S39 (C-24): vectorii de control din integrare/kronos/vectori/ (făcuți cu unelte/vectori_kgr1.py) se recitesc și dau
aceleași simboluri, logit-uri (± toleranța declarată în integrare/kronos/README.md), argmax și greedy. Fără PyTorch."""

import json
from pathlib import Path

import numpy as np
import pytest

from unelte.inferenta_bruta import MotorBrut
from unelte.vectori_kgr1 import sha256

DOSAR = Path(__file__).resolve().parents[1] / "integrare" / "kronos"
VECTORI = json.loads((DOSAR / "vectori" / "vectori.json").read_text(encoding="utf-8"))
TOLERANTA = {"f32": 1e-4, "q8_0": 1e-3}  # aceleași cifre ca în README.md


@pytest.mark.parametrize("fel", ["f32", "q8_0"])
def test_vectorii_se_refac_din_fisier(fel):
    info = VECTORI["fisiere"][fel]
    cale = DOSAR / info["nume"]
    assert cale.stat().st_size == info["octeti"] and sha256(cale) == info["sha256"]
    motor = MotorBrut(cale)
    for v in VECTORI[fel]:
        s = motor.tok.codifica(v["text"])
        assert s == v["simboluri"] and motor.tok.decodeaza(s) == v["text"]
        lg = motor.logits(s)
        assert np.abs(lg[-1] - np.asarray(v["logits_ultima_pozitie"], dtype=np.float32)).max() <= TOLERANTA[fel]
        assert [int(x) for x in lg.argmax(axis=-1)] == v["argmax_pe_pozitii"]
        greedy, _ = motor.completeaza_simboluri(s, len(v["greedy_5"]))
        assert greedy == v["greedy_5"] and motor.tok.decodeaza(greedy) == v["greedy_5_text"]
        # toleranța lasă argmax-ul neschimbat: marja cea mai mică e mult peste ea
        assert min(v["marja_minima_pozitii"], v["marja_minima_greedy"]) > 10 * TOLERANTA[fel]


def test_format_greutati_e_copie_exacta():
    docs = Path(__file__).resolve().parents[1] / "docs" / "format_greutati.md"
    assert (DOSAR / "format_greutati.md").read_bytes() == docs.read_bytes()


def test_diferenta_masurata_e_sub_toleranta():
    d = VECTORI["diferente"]
    assert d["f32_fata_de_pytorch_max"] < TOLERANTA["f32"] / 10
