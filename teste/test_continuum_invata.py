"""CONTINUUM, ÎNVAȚĂ: încrederea fiecărei strategii și lista experimentelor; ciclurile simulate nu schimbă nimic."""

from __future__ import annotations

import copy

from module.continuum import ESEC, NECONCLUDENT, SUCCES
from module.continuum.alege import Alegere
from module.continuum.invata import invata
from module.continuum.stare import memorie_goala
from teste.test_continuum_masoara import antrenare

CONFIG = {"invatare": {"incredere_initiala": 0.5, "pas_incredere": 0.1}}


def test_invata_increderea_si_experimentele():
    memorie = memorie_goala()
    alegere = antrenare()
    invata(memorie, alegere, {"verdict": SUCCES, "fise": [11, 12], "motiv": "bine"}, CONFIG, 3, "t1")
    invata(memorie, alegere, {"verdict": ESEC, "motiv": "rău"}, CONFIG, 4, "t2")
    invata(memorie, alegere, {"verdict": ESEC, "motiv": "rău"}, CONFIG, 5, "t3")
    invata(memorie, alegere, {"verdict": NECONCLUDENT, "motiv": "?"}, CONFIG, 6, "t4")
    assert memorie["strategii"]["dezvolta:fapte:antrenare"] == {"incredere": 0.4, "succese": 1, "esecuri": 2,
                                                                "neconcludente": 1, "stare": "activa"}
    assert [e["verdict"] for e in memorie["experimente"]] == [SUCCES, ESEC, ESEC, NECONCLUDENT]
    assert memorie["experimente"][0]["fise"] == [11, 12] and memorie["experimente"][0]["ciclu"] == 3
    inainte = copy.deepcopy(memorie["strategii"])
    invata(memorie, alegere, {"verdict": None}, CONFIG, 7, "t5")  # simulat: nimic nou
    invata(memorie, Alegere(), {"verdict": None}, CONFIG, 8, "t6")
    assert memorie["strategii"] == inainte and len(memorie["experimente"]) == 4
