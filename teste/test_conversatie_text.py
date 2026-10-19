"""„Răspuns din text” (19 octombrie 2026): perechile Text / Întrebare / Răspuns și examenul lor."""

import json
import random

from module.model_conversatie import intrebarea
from unelte import conversatie_text as ct
from unelte.examen_conversatie import pe_feluri, scoruri, spune_nu_scrie

FILM = ("Okinawa este un film american de război din 1952 regizat de Leigh Jason și cu Pat O'Brien, Cameron Mitchell "
        "și Richard Denning în rolurile principale.")
SAT = "Cloșca este un sat în comuna Horia din județul Tulcea, Dobrogea, România. Are 1.204 locuitori."
OM = "Aurel Decei (n. 15 aprilie 1905, Gura Râului, Sibiu — d. 24 aprilie 1976) a fost un istoric și diplomat român."


def test_intrebarea_cu_text_in_fata():
    assert intrebarea("Ce este X?") == "Întrebare: Ce este X?\nRăspuns:"
    assert intrebarea("Ce este X?", "X este un sat.") == "Text: X este un sat.\nÎntrebare: Ce este X?\nRăspuns:"


def test_textul_se_opreste_la_propozitia_rupta_si_scoate_parantezele_rupte():
    articol = ("Baia Sprie (în , în trad. Baia de Sus, în ) este un oraș în județul Maramureș. Are o populație de "
               "locuitori (2011). A fost un centru minier.\nIstoric\n…")
    assert ct.text_din(articol) == "Baia Sprie este un oraș în județul Maramureș."
    assert ct.text_din("Alina Rotaru (născută Rotaru, ) este o atletă română.") == "Alina Rotaru este o atletă română."


def test_raspunsurile_se_iau_din_text():
    film = ct.intrebari_din_text(FILM, "Okinawa", "ce", FILM, "Ce este Okinawa?")
    assert {"tip": "regizat", "intrebare": "Cine a regizat Okinawa?", "raspuns": "Leigh Jason."} in film
    assert {"tip": "an", "intrebare": "Din ce an este Okinawa?", "raspuns": "Din 1952."} in film
    sat = {q["tip"]: q["raspuns"] for q in ct.intrebari_din_text(SAT, "Cloșca", "loc", SAT.split(". ")[0] + ".", "")}
    assert sat["judet"] == "În județul Tulcea." and sat["comuna"] == "În comuna Horia." and sat["locuitori"] == "1.204 locuitori."
    om = {q["tip"]: q["raspuns"] for q in ct.intrebari_din_text(OM, "Aurel Decei", "om", "", "")}
    assert om["nascut"] == "În 1905." and om["murit"] == "În 1976."
    for q in ct.intrebari_din_text(FILM, "Okinawa", "ce", FILM, "") + ct.intrebari_din_text(OM, "Aurel Decei", "om", "", ""):
        assert q["raspuns"].removeprefix("Din ").removeprefix("În ").rstrip(".") in FILM + OM


def test_nu_scrie_doar_ce_lipseste_din_text():
    lipsa = {q["tip"] for q in ct.lipsa_din_text(SAT, "Cloșca", "loc")}
    assert "lipsa_locuitori" not in lipsa and "lipsa_altitudine" in lipsa
    assert "lipsa_regizat" not in {q["tip"] for q in ct.lipsa_din_text(FILM, "Okinawa", "ce")}
    om = {q["tip"] for q in ct.lipsa_din_text(OM, "Aurel Decei", "om")}
    assert "lipsa_nascut" not in om and "lipsa_murit_unde" not in om and "lipsa_parinti" in om
    assert all(q["raspuns"] == ct.NU_SCRIE for q in ct.lipsa_din_text(SAT, "Cloșca", "loc"))


def _articole(n):
    return [{"x": f"Satul{i}", "tip": "loc", "text": f"Satul{i} este un sat în comuna Comuna{i} din județul Județ{i}.",
             "prima": f"Satul{i} este un sat în comuna Comuna{i} din județul Județ{i}.",
             "definitie": f"Unde se află Satul{i}?"} for i in range(n)]


def test_cam_o_cincime_nu_scrie_si_definitiile_cel_mult_jumatate():
    perechi = ct.perechi_pentru(_articole(100), 0.2, random.Random(0), "text")
    feluri = [p["fel"] for p in perechi]
    assert abs(feluri.count("nu_scrie") / len(feluri) - 0.2) < 0.02
    text = [p for p in perechi if p["fel"] == "text"]
    assert sum(p["tip"] == "definitie" for p in text) <= len(text) / 2 + 1
    for p in perechi:
        if p["tip"] == "alt_subiect":
            assert p["intrebare"].split()[-1].rstrip("?") not in p["text"]


def test_examenul_are_50_cu_text_si_20_fara():
    examen = ct.examenul(_articole(300), 50, 20, random.Random(0))
    feluri = [p["fel"] for p in examen]
    assert feluri.count("text") == 50 and feluri.count("nu_scrie") == 20
    assert len({p["text"] for p in examen if p["tip"] != "alt_subiect"}) == len([p for p in examen if p["tip"] != "alt_subiect"])


def test_nu_scrie_in_text_se_recunoaste_si_se_numara():
    assert spune_nu_scrie("Nu scrie în text.") and spune_nu_scrie("nu scrie in text") and not spune_nu_scrie("Nu știu.")
    intrebari = [
        {"fel": "nu_scrie", "raspuns_elev": "Nu scrie în text.", "nu_stiu_corect": True, "nota_elev": 9},
        {"fel": "nu_scrie", "raspuns_elev": "Leigh Jason.", "nu_stiu_corect": False, "nota_elev": 2},
        {"fel": "text", "raspuns_elev": "Nu scrie în text.", "nu_stiu_corect": False, "nota_elev": 1},
        {"fel": "text", "raspuns_elev": "Din 1952.", "nu_stiu_corect": False, "nota_elev": 10},
    ]
    assert pe_feluri(intrebari) == {"intrebari_nu_scrie": 2, "corecte_nu_scrie": 1, "intrebari_text": 2, "corecte_text": 1}
    s = scoruri(intrebari)
    assert s["nu_scrie_la_text"] == 1 and s["nota_medie_fara_nu_stiu"] == 5.5


def test_conversatia_simpla_nu_are_intrebarile_din_examen():
    from unelte.genereaza_conversatie import normalizat

    simple = json.loads((ct.RADACINA / ct.CONVERSATIE).read_text(encoding="utf-8"))["perechi"]
    examen = json.loads((ct.RADACINA / ct.SCRISE_DE_MANA).read_text(encoding="utf-8"))["conversatie"]
    assert len(simple) >= 40
    assert not {normalizat(p["intrebare"]) for p in simple} & {normalizat(p["intrebare"]) for p in examen}
