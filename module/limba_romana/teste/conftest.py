"""Fixturi pytest: o bază mică (din fixturile scrise de mână) și, dacă există, baza completă."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from ..baza import CALE_IMPLICITA, Baza
from ..importatoare import importa_hunspell, importa_kaikki, importa_rown, importa_ud
from ..morfologie import inchise, paradigme
from ..morfologie.trasaturi import INVENTAR
from ..sintaxa import reguli as reguli_sintaxa

FIXTURI = Path(__file__).resolve().parent / "fixturi"


@pytest.fixture(scope="session")
def baza_mica(tmp_path_factory) -> Baza:
    """Bază construită din fixturile mici, cu toți importatorii, paradigmele și clasele închise."""
    d = tmp_path_factory.mktemp("surse")
    (d / "hunspell").mkdir(); (d / "ud_rrt").mkdir(); (d / "rown").mkdir(); (d / "kaikki").mkdir()
    shutil.copy(FIXTURI / "mic.aff", d / "hunspell" / "ro_RO.aff")
    shutil.copy(FIXTURI / "mic.dic", d / "hunspell" / "ro_RO.dic")
    shutil.copy(FIXTURI / "mic.conllu", d / "ud_rrt" / "ro_rrt-ud-train.conllu")
    shutil.copy(FIXTURI / "mic.conllu_test", d / "ud_rrt" / "ro_rrt-ud-test.conllu")
    cale = tmp_path_factory.mktemp("baza") / "mica.sqlite"
    b = Baza(cale)
    b.seteaza_trasaturi(INVENTAR)
    importa_kaikki.importa(b, cale=FIXTURI / "mic_kaikki.jsonl", verbos=False)
    importa_ud.importa(b, director=d / "ud_rrt", verbos=False)
    importa_rown.importa(b, cale=FIXTURI / "mic_rown.json", verbos=False)
    importa_hunspell.importa(b, director=d / "hunspell", verbos=False)
    paradigme.aplica_peste_baza(b, verbos=False)
    inchise.scrie_in_baza(b, verbos=False)
    reguli_sintaxa.scrie_in_baza(b)
    b.fuzioneaza_forme_fara_trasaturi()
    b.recalculeaza_statut_forme()
    yield b
    b.inchide()


@pytest.fixture(scope="session")
def motor_complet():
    """Motorul pe baza completă (construită cu construieste_baza). Testele care îl folosesc se sar dacă baza lipsește."""
    if not CALE_IMPLICITA.exists():
        pytest.skip("baza completă lipsește (rulați construieste_baza)")
    from ..motor import Motor
    m = Motor(CALE_IMPLICITA)
    yield m
    m.inchide()
