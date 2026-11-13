"""S109: generatorul tipurilor (b2) și examenul ținut deoparte (`unelte/conversatie_tipuri.py`), pe texte scrise aici."""
from __future__ import annotations

import random
import re

import pytest

from unelte import conversatie_tipuri as ct

FILM = ("Sărutul este un film românesc din 1965 regizat de Lucian Bratu. Rolurile principale au fost interpretate de "
        "actorii Graziela Albini, Emanoil Petruț și Maria Cupcea.")
FOTBALIST = ("Libor Kozák (n. 30 mai 1989) este un fotbalist profesionist ceh care joacă pe postul de atacant pentru Sparta "
             "Praga din Prima Ligă din Cehia.")
PICTURA = ("Al nouălea val este o pictură în ulei realizată în anul 1850 de pictorul rus Ivan Aivazovski. Ea este una "
           "dintre cele mai cunoscute picturi ale artistului.")
SERIAL = ("Băieți buni este un serial TV de producție românească din anul 2005. Serialul surprinde viața de stradă din "
          "România și a fost difuzat de postul de televiziune PRO TV.")
SOTIE = ("Jane Pierce (n. 12 martie 1806 - d. 2 decembrie 1863) a fost soția lui Franklin Pierce, al paisprezecelea "
         "Președinte al Statelor Unite ale Americii.")
ORAS = "Fangoria Films este o companie de producție și distribuție a filmului, cu sediul în New York City, New York."
TARA = "Kiruna este cel mai nordic oraș din Suedia, situat în provincia Lappland. În 2010 avea 18.148 locuitori."


@pytest.mark.parametrize("tip,text,x,subiect,verb,cheie", [
    ("actori", FILM, "Sărutul", "ce", "este", "Graziela Albini, Emanoil Petruț și Maria Cupcea"),
    ("post", FOTBALIST, "Libor Kozák", "om", "este", "atacant"),
    ("profesie", FOTBALIST, "Libor Kozák", "om", "este", "fotbalist"),
    ("pictor", PICTURA, "Al nouălea val", "ce", "este", "Ivan Aivazovski"),
    ("canal", SERIAL, "Băieți buni", "ce", "este", "PRO TV"),
    ("sot", SOTIE, "Jane Pierce", "om", "a fost", "Franklin Pierce"),
    ("oras", ORAS, "Fangoria Films", "ce", "este", "New York City"),
    ("tara", TARA, "Kiruna", "loc", "este", "Suedia"),
], ids=["actori", "post", "profesie", "pictor", "canal", "sot", "oras", "tara"])
def test_extrage_raspunsul_care_e_intocmai_in_text(tip, text, x, subiect, verb, cheie):
    r = ct.extrage(tip, text, x, subiect, verb)
    assert r is not None and r["cheie"] == cheie
    assert r["cheie"] in text


def test_nu_extrage_cand_subiectul_premiului_e_altcineva():
    text = ("John Locke este unul dintre personajele principale din serialul de televiziune american Lost. În 2007, "
            "O'Quinn a câștigat Premiul Primetime Emmy pentru cel mai bun actor.")
    assert ct.extrage("premiu", text, "John Locke", "ce") is None
    assert ct.extrage("premiu", "Timothy Zahn este un scriitor american. A câștigat Premiul Hugo în 1984.",
                      "Timothy Zahn", "om")["cheie"] == "Premiul Hugo"


def test_sotia_sa_nu_e_luata_ca_sot():
    text = ("Gisela de Suabia (n. 989 – d. 1043) a fost fiica ducelui Herman al II-lea de Suabia cu soția sa, Gerberga "
            "de Burgundia.")
    assert ct.extrage("sot", text, "Gisela de Suabia", "om", "a fost") is None


def test_orasul_nu_e_o_tara():
    text = "Superbet Betting este o companie din industria jocurilor de noroc, cu sediul în România."
    assert ct.extrage("oras", text, "Superbet Betting", "ce") is None


def test_formularile_cel_putin_trei_pe_tip_si_cele_de_examen_nu_sunt_in_generator():
    gen = {s for f in ct.GENERATOR.values() for l in f.values() for s in l}
    for tip in ct.TIPURI_B2:
        assert set(ct.GENERATOR[tip]) == set(ct.EXAMEN_NOI[tip])
        for fel, lista in ct.GENERATOR[tip].items():
            assert len(set(lista)) >= 3, (tip, fel)
            assert ct.EXAMEN_NOI[tip][fel] and not set(ct.EXAMEN_NOI[tip][fel]) & gen
    for tip, fel in ct.FEL_NU_SCRIE.items():
        assert fel in ct.GENERATOR[tip]


def test_tipurile_ii_nu_seamana_cu_generatorul():
    gen = {s for f in ct.GENERATOR.values() for l in f.values() for s in l}
    prime = {re.sub(r"\{.\}", "", s).split()[0:3].__str__() for s in gen}
    for tip, f in ct.FORMULARI_II.items():
        assert tip not in ct.TIPURI_B2
        for s in f.values():
            assert s not in gen and str(re.sub(r"\{.\}", "", s).split()[0:3]) not in prime


def _cand():
    baza = [
        {"x": "Sărutul", "tip": "ce", "verb": "este", "text": FILM},
        {"x": "Libor Kozák", "tip": "om", "verb": "este", "text": FOTBALIST},
        {"x": "Al nouălea val", "tip": "ce", "verb": "este", "text": PICTURA},
        {"x": "Băieți buni", "tip": "ce", "verb": "este", "text": SERIAL},
        {"x": "Jane Pierce", "tip": "om", "verb": "a fost", "text": SOTIE},
        {"x": "Fangoria Films", "tip": "ce", "verb": "este", "text": ORAS},
        {"x": "Kiruna", "tip": "loc", "verb": "este", "text": TARA},
    ]
    alte = []
    for i in range(12):  # încă filme, ca să rămână ceva și pentru antrenare
        alte.append({"x": f"Filmul Numărul{i}", "tip": "ce", "verb": "este",
                     "text": f"Filmul Numărul{i} este un film românesc din 19{60 + i} regizat de Ion Popescu{i}. Rolurile "
                             f"principale au fost interpretate de actorii Ana Maria{i}, Dan Ionescu{i} și Radu Marin{i}."})
    return baza + alte


def test_examenul_si_antrenarea_nu_impart_texte_sau_subiecte():
    cand = _cand()
    ex = ct.construieste_examen(cand, random.Random(109), pe_tip=3, total_ii=0)
    perechi = ex["perechi"]
    assert perechi and all(p["cheie"][0] in p["text"] for p in perechi)
    v = ct.verifica_examen(perechi)
    assert not v["raspunsuri_care_nu_sunt_in_text"] and v["texte_repetate"] == 0
    assert not v["sabloane_noi_care_sunt_si_in_generator"]
    # cel puțin 1 din 3 întrebări (i) pe tip are o formulare nouă
    for tip, n in v["i_pe_tip"].items():
        assert v["i_formulari_noi_pe_tip"].get(tip, 0) >= n / 3
    noi, info = ct.construieste_antrenare(cand, perechi, random.Random(109))
    texte_ex = {p["text"] for p in perechi}
    subiecte_ex = {p["subiect"] for p in perechi}
    assert noi
    assert not {r["text"] for r in noi} & texte_ex
    assert not {r["subiect"] for r in noi} & subiecte_ex
    for r in noi:
        assert r["prompt"] == f"Text: {r['text']}\nÎntrebare: {r['intrebare']}\nRăspuns:"
        if r["fel"] == "text":
            assert r["cheie"][0] in r["text"]
        else:
            assert r["raspuns"] == ct.NU_SCRIE
    # textele examenului ies toate; filmele de probă au și bucăți de 8 cuvinte comune, deci ies și altele
    assert info["scoase_din_cauza_examenului"]["text din examen"] == len(texte_ex)
    assert sum(info["scoase_din_cauza_examenului"].values()) >= len(texte_ex)


def test_plafonul_pe_tip_si_fractia_nu_scrie():
    cand = []
    for i in range(60):
        cand.append({"x": f"Filmul Numărul{i}", "tip": "ce", "verb": "este",
                     "text": f"Filmul Numărul{i} este un film românesc din 19{40 + i} regizat de Ion Popescu{i}. Rolurile "
                             f"principale au fost interpretate de actorii Ana Maria{i}, Dan Ionescu{i} și Radu Marin{i}."})
        cand.append({"x": f"Filmul Altul{i}", "tip": "ce", "verb": "este",
                     "text": f"Filmul Altul{i} este un film mut din anii {i} despre viața la țară și despre "
                             f"munca grea a oamenilor de la munte."})
    noi, info = ct.construieste_antrenare(cand, [], random.Random(1), plafon=20, fractie=0.1)
    actori = info["pe_tip"]["actori"]
    assert actori["cu_raspuns"] + actori["nu_scrie"] <= 20
    assert actori["nu_scrie"] == 2 and actori["cu_raspuns"] == 18
