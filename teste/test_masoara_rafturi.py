"""Măsurarea rafturilor: umplutura, încărcarea fiecărui raft și asocierea cuvintelor vecine."""

from __future__ import annotations

import pytest

from module.memorie_ierarhica import NECUNOSCUT, MemorieIerarhica
from teste.biblioteca_mica import biblioteca_mica
from unelte.masoara_rafturi import UMPLUTURA, masoara


@pytest.fixture
def cale(tmp_path):
    return biblioteca_mica(tmp_path)


def test_cuvintele_de_legatura_devin_umplutura(cale):
    bruta, filtrata = MemorieIerarhica(cale), MemorieIerarhica(cale, fara_cuvinte_de_legatura=True)
    assert bruta.cod("can")[0] == 1  # WordNet: „can” = cutie de conserve
    assert filtrata.cod("can")[0] == NECUNOSCUT and filtrata.cod("Can")[0] == NECUNOSCUT
    assert filtrata.cod("it's")[0] == NECUNOSCUT  # „it” + „'s”
    assert filtrata.cod("cat") == bruta.cod("cat")  # cuvintele cu sens rămân la fel
    assert not bruta.este_cuvant_de_legatura("the") and filtrata.este_cuvant_de_legatura("the")


def test_masoara_rafturile_si_umplutura(cale):
    text = "the good cat ran to the sword. a cat can run."
    r = masoara(text, MemorieIerarhica(cale, fara_cuvinte_de_legatura=True), bruta=MemorieIerarhica(cale), minim_pereche=1)
    assert r["cuvinte"] == 11 and r["cu_sens"] == 6
    assert r["umplutura"] == {"total": 5, "negasite": 0, "de_legatura": 5, "de_legatura_cu_alt_sens_in_wordnet": {"can": 1}}
    pe_raft = {x["raft"]: x["cuvinte"] for x in r["rafturi"]}
    assert pe_raft == {"noun.animal": 2, "verb.motion": 2, "adj.all": 1, "noun.artifact": 1}
    assert r["rafturi"][-1]["procent_cumulat"] == pytest.approx(1.0)
    assert r["rafturi_pentru_90_la_suta"] == 4 and r["rafturi_cu_nod"] == 4
    # „good” e urmat de „cat”: 1 din 10 perechi, față de (1/11)·(2/11) cât ar fi întâmplător
    asociere = next(a for a in r["asocieri"] if (a["de_la"], a["la"]) == ("adj.all", "noun.animal"))
    assert asociere["asociere"] == pytest.approx((1 / 10) / ((1 / 11) * (2 / 11)))
    assert all(UMPLUTURA not in (a["de_la"], a["la"]) for a in r["asocieri"])


def test_perechile_rare_nu_intra_la_asocieri(cale):
    r = masoara("the good cat ran. ", MemorieIerarhica(cale, fara_cuvinte_de_legatura=True))  # prag implicit: 100
    assert r["asocieri"] == []


def test_masoara_schimbarile_fata_de_masuratoarea_veche(cale):
    text = "the cat saw Horse back. a cat can run. "
    veche = MemorieIerarhica(cale, fara_cuvinte_de_legatura=True)
    noua = MemorieIerarhica(cale, fara_cuvinte_de_legatura=True, sens_dupa_context=True)
    r = masoara(text, noua, veche=veche, minim_pereche=1)
    s = r["schimbari"]
    assert s["total"] == 3 and s["cuvinte_diferite"] == 3 and s["din_umplutura"] == 0
    assert s["pe_reguli"] == {"a_forme_de_verb": 1, "b_nume": 1, "c_adverbe": 1}
    assert {(x["cuvant"], x["de_la"], x["la"]) for x in s["cele_mai_dese"]} == {
        ("saw", "noun.artifact", "verb.perception"),
        ("horse", "noun.animal", "noun.person"),
        ("back", "noun.body", "adv.all"),
    }
    peste = r["asocieri_peste"]
    assert list(peste) == ["2x", "3x", "5x"] and peste["2x"] >= peste["3x"] >= peste["5x"]
    assert peste["2x"] == sum(1 for a in r["asocieri"] if a["asociere"] > 2)
    assert "schimbari" not in masoara(text, veche)
