"""Trăsături, paradigme, clase închise, cititorul Hunspell, identificatori."""

from ..baza import canonic_trasaturi, desparte_trasaturi
from ..identificatori import id_lexem, id_sens
from ..morfologie import inchise, paradigme
from ..morfologie.hunspell import citeste
from ..morfologie.trasaturi import INVENTAR, canonic_pentru_pos, din_hunspell, din_kaikki, valideaza
from .conftest import FIXTURI


def forme(lista):
    return {(f, canonic_trasaturi(t)) for f, t, _ in lista}


def test_canonic_trasaturi():
    assert canonic_trasaturi("Number=Sing|Case=Acc,Nom") == "Case=Acc,Nom|Number=Sing"
    assert canonic_trasaturi({"b": "2", "a": "1"}) == "a=1|b=2"
    assert canonic_trasaturi("_") == "" and desparte_trasaturi("") == {}


def test_inventar_valid():
    assert not valideaza({"Case": "Dat,Gen", "Number": "Plur"})
    assert valideaza({"Case": "Abl"}) == ["valoare necunoscută: Case=Abl"]
    assert valideaza({"Culoare": "roșu"}) == ["cheie necunoscută: Culoare"]
    assert len({(c, v) for c, v, _ in INVENTAR}) == len(INVENTAR)


def test_traducere_kaikki():
    tr, rest = din_kaikki(["accusative", "definite", "nominative", "singular"], "NOUN")
    assert tr == {"Case": "Acc,Nom", "Definite": "Def", "Number": "Sing"} and rest == []
    tr, _ = din_kaikki(["first-person", "indicative", "present", "singular"], "VERB")
    assert tr == {"Person": "1", "Mood": "Ind", "Tense": "Pres", "Number": "Sing", "VerbForm": "Fin"}
    tr, _ = din_kaikki(["feminine", "neuter", "plural"], "ADJ")
    assert tr["Gender"] == "Fem" and tr["Number"] == "Plur"


def test_traducere_hunspell():
    assert din_hunspell("s.f.sg.art.") == {"Gender": "Fem", "Number": "Sing", "Definite": "Def", "Case": "Acc,Nom"}
    assert din_hunspell("s.f.sg.dat.") == {"Gender": "Fem", "Number": "Sing", "Case": "Dat,Gen", "Definite": "Def"}
    assert din_hunspell("s. m. pl. neart.")["Definite"] == "Ind"


def test_conventia_canonica():
    # neutru: Masc la singular, Fem la plural; fără Case la nearticulat sincretic; Degree=Pos implicit la adjective
    assert canonic_pentru_pos("NOUN", {"Number": "Sing", "Definite": "Ind", "Case": "Acc,Nom"}, "Neut") == {"Number": "Sing", "Definite": "Ind", "Gender": "Masc"}
    assert canonic_pentru_pos("NOUN", {"Number": "Plur", "Definite": "Def", "Case": "Acc,Nom"}, "Neut")["Gender"] == "Fem"
    assert canonic_pentru_pos("ADJ", {"Gender": "Fem", "Number": "Sing", "Definite": "Ind", "Case": "Acc,Nom"})["Degree"] == "Pos"
    assert canonic_pentru_pos("VERB", {"VerbForm": "Inf"}) == {"VerbForm": "Inf", "Tense": "Pres"}
    assert canonic_pentru_pos("VERB", {"VerbForm": "Part"}) == {"VerbForm": "Part", "Gender": "Masc", "Number": "Sing"}


def test_declinare_substantive():
    f = forme(paradigme.declina_substantiv("casă", "Fem", "case"))
    assert ("casa", "Case=Acc,Nom|Definite=Def|Gender=Fem|Number=Sing") in f
    assert ("casei", "Case=Dat,Gen|Definite=Def|Gender=Fem|Number=Sing") in f
    assert ("caselor", "Case=Dat,Gen|Definite=Def|Gender=Fem|Number=Plur") in f
    f = forme(paradigme.declina_substantiv("om", "Masc", "oameni"))
    assert ("omului", "Case=Dat,Gen|Definite=Def|Gender=Masc|Number=Sing") in f and ("oamenii", "Case=Acc,Nom|Definite=Def|Gender=Masc|Number=Plur") in f
    f = forme(paradigme.declina_substantiv("scaun", "Neut"))
    assert ("scaunul", "Case=Acc,Nom|Definite=Def|Gender=Masc|Number=Sing") in f and ("scaunele", "Case=Acc,Nom|Definite=Def|Gender=Fem|Number=Plur") in f
    f = forme(paradigme.declina_substantiv("familie", "Fem"))
    assert ("familiei", "Case=Dat,Gen|Definite=Def|Gender=Fem|Number=Sing") in f and ("familiile", "Case=Acc,Nom|Definite=Def|Gender=Fem|Number=Plur") in f
    f = forme(paradigme.declina_substantiv("frate", "Masc"))
    assert ("fratele", "Case=Acc,Nom|Definite=Def|Gender=Masc|Number=Sing") in f and not any(x[0] == "frateule" for x in f)


def test_declinare_adjective():
    f = forme(paradigme.declina_adjectiv("frumos"))
    assert ("frumoasă", "Case=Acc,Nom|Definite=Ind|Degree=Pos|Gender=Fem|Number=Sing") in f
    assert ("frumoși", "Definite=Ind|Degree=Pos|Gender=Masc|Number=Plur") in f
    assert ("frumoasei", "Case=Dat,Gen|Definite=Def|Degree=Pos|Gender=Fem|Number=Sing") in f
    assert {x[0] for x in forme(paradigme.declina_adjectiv("mic"))} >= {"mic", "mică", "mici", "micul", "micii"}
    assert [x[0] for x in paradigme.declina_adjectiv("gri")] == ["gri"]


def test_conjugare():
    f = forme(paradigme.conjuga("cânta", "I-a"))
    assert ("cânt", "Mood=Ind|Number=Sing|Person=1|Tense=Pres|VerbForm=Fin") in f
    assert ("cântă", "Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin") in f
    assert ("cânte", "Mood=Sub|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin") in f
    assert ("cântasem", "Mood=Ind|Number=Sing|Person=1|Tense=Pqp|VerbForm=Fin") in f
    assert ("cântând", "VerbForm=Ger") in f and ("cântată", "Gender=Fem|Number=Sing|VerbForm=Part") in f
    f = forme(paradigme.conjuga("lucra", "I-ez"))
    assert ("lucrează", "Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin") in f and ("lucreze", "Mood=Sub|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin") in f
    f = forme(paradigme.conjuga("citi", "IV-esc"))
    assert ("citesc", "Mood=Ind|Number=Sing|Person=1|Tense=Pres|VerbForm=Fin") in f and ("citească", "Mood=Sub|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin") in f
    f = forme(paradigme.conjuga("hotărî", "IV-ăsc"))
    assert ("hotărăște", "Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin") in f and ("hotărât", "Gender=Masc|Number=Sing|VerbForm=Part") in f
    f = forme(paradigme.conjuga("merge", "III-e", "mers"))
    assert ("mersei", "Mood=Ind|Number=Sing|Person=1|Tense=Past|VerbForm=Fin") in f
    assert paradigme.grup_conjugare("lucra", "lucrează") == "I-ez" and paradigme.grup_conjugare("citi", "citește") == "IV-esc"
    assert paradigme.grup_conjugare("cânta").endswith("?")


def test_clase_inchise_valide():
    randuri = inchise.toate_formele()
    assert len(randuri) > 700
    for pos, lema, forma, tr, _ in randuri:
        assert not valideaza(desparte_trasaturi(tr)), (forma, tr)
    assert ("PRON", "el", "l-", "Case=Acc|Gender=Masc|Number=Sing|Person=3|PronType=Prs|Strength=Weak|Variant=Short", "clitic înaintea verbului") in randuri
    assert any(r[1] == "al" and r[2] == "ale" for r in randuri)
    assert any(r[0] == "ADP" and r[1] == "asupra" and "Case=Gen" in r[3] for r in randuri)


def test_cititor_hunspell():
    d = citeste(FIXTURI / "mic.aff", FIXTURI / "mic.dic")
    assert len(d.intrari) == 6
    f = {forma: r.anotare for forma, r in d.forme("casă", "A")}
    assert f["casa"] == "s.f.sg.art." and f["caselor"] == "s.f.pl.dat."
    assert {x for x, _ in d.forme("lucrez", "B")} == {"lucrezi", "lucrează", "lucrăm"}
    assert not any(x.startswith("re") for x, _ in d.forme("lucrez", "B"))   # fără prefixe


def test_identificatori_deterministi():
    assert id_lexem("Casă", "NOUN") == id_lexem("casă", "NOUN") == id_lexem("CASĂ", "NOUN", 0)
    assert id_lexem("casă", "NOUN") != id_lexem("casă", "VERB") != id_lexem("casă", "NOUN", 1)
    assert id_lexem("bancă", "NOUN", 1) != id_lexem("bancă", "NOUN", 2)
    assert id_sens("L1", "C1", 1) == id_sens("L1", "C1", 1) != id_sens("L1", "C1", 2)
