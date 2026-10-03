"""Biblioteca de sensuri: codurile, formele și relațiile ies corect din WordNet."""

from __future__ import annotations

import gzip
import json

import pytest

from teste.biblioteca_mica import wordnet_mic
from unelte.construieste_biblioteca import citeste_wordnet, construieste, main


@pytest.fixture
def bib(tmp_path):
    return construieste(citeste_wordnet(wordnet_mic(tmp_path)))


def _sens(bib, cuvant, nr=0):
    return bib["forme"][cuvant][nr]


def _drum(bib, i):
    drum = []
    while i != -1:
        drum.append(bib["nume"][i])
        i = bib["parinte"][i]
    return drum[::-1]


def test_fiecare_sens_are_parinte_cod_si_nume(bib):
    n = len(bib["cod"])
    assert n == 19
    assert len(bib["nume"]) == len(bib["parinte"]) == n
    assert bib["versiune"] == 1 and "WordNet de test" in bib["sursa"]
    for i in range(n):
        assert bib["parinte"][i] == -1 or 0 <= bib["parinte"][i] < n
        assert all(isinstance(x, int) and x >= 1 for x in bib["cod"][i])  # 0 rămâne pentru „gol”


def test_codul_urmeaza_ierarhia(bib):
    cal, pisica, sabie = _sens(bib, "horse"), _sens(bib, "cat"), _sens(bib, "sword")
    assert _drum(bib, cal) == ["entity", "organism", "animal", "horse"]
    assert len(bib["cod"][cal]) == 2 + 4  # parte de vorbire, raft, apoi un număr pe fiecare nivel
    assert bib["cod"][cal][:5] == bib["cod"][pisica][:5]  # același raft și aceiași strămoși
    assert bib["cod"][cal][5] != bib["cod"][pisica][5]  # frați diferiți
    assert bib["rafturi"][bib["cod"][cal][1] - 1] == "noun.animal"
    assert bib["cod"][cal][1] != bib["cod"][sabie][1]  # rafturi diferite


def test_partea_de_vorbire_e_primul_nivel(bib):
    parte = {c: bib["parti_de_vorbire"][bib["cod"][_sens(bib, c)][0] - 1] for c in ("horse", "gallop", "good", "bad", "o'clock")}
    assert parte == {"horse": "substantiv", "gallop": "verb", "good": "adjectiv", "bad": "adjectiv", "o'clock": "adverb"}


def test_formele_si_sensul_principal(bib):
    assert bib["nume"][_sens(bib, "hooves")] == "hoof"
    assert bib["nume"][_sens(bib, "ran")] == "run"
    assert "o'clock" in bib["forme"]
    assert not any(" " in f for f in bib["forme"])  # „horse racing” nu poate apărea ca un singur cuvânt
    # „cat” (animalul) înaintea lui „CAT” (nume propriu); la „horse”, substantivele înaintea verbului
    assert [bib["rafturi"][bib["cod"][i][1] - 1] for i in bib["forme"]["cat"]] == ["noun.animal", "noun.act"]
    assert [bib["cod"][i][0] for i in bib["forme"]["horse"]] == [1, 1, 2]


def test_relatiile(bib):
    def relatii(cuvant):
        return {(tip, bib["nume"][tinta]) for tip, tinta in bib["relatii"].get(str(_sens(bib, cuvant)), [])}

    assert relatii("horse") == {("are_parte", "hoof"), ("membru_din", "herd")}
    assert relatii("hoof") == {("parte_din", "horse")}
    assert relatii("herd") == {("are_membru", "horse")}
    assert relatii("good") == {("opus", "bad")} and relatii("bad") == {("opus", "good")}


def test_construirea_e_reproductibila(tmp_path):
    cale = wordnet_mic(tmp_path)
    assert json.dumps(construieste(citeste_wordnet(cale))) == json.dumps(construieste(citeste_wordnet(cale)))


def test_scriptul_scrie_biblioteca(tmp_path, capsys):
    destinatie = tmp_path / "bib.json.gz"
    assert main(["--sursa", str(wordnet_mic(tmp_path)), "--destinatie", str(destinatie)]) == 0
    with gzip.open(destinatie, "rt", encoding="utf-8") as f:
        assert len(json.load(f)["cod"]) == 19
    assert "19 sensuri" in capsys.readouterr().out
