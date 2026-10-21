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


def _amestec(n):
    """Sate, filme și oameni, ca să fie de toate șabloanele da/nu."""
    return _articole(n) + [
        {"x": f"Film{i}", "tip": "ce", "text": FILM.replace("Okinawa", f"Film{i}"), "prima": FILM, "definitie": f"Ce este Film{i}?"}
        for i in range(n)] + [
        {"x": f"Om{i}", "tip": "om", "text": OM.replace("Aurel Decei", f"Om{i}"), "prima": OM, "definitie": f"Cine a fost Om{i}?"}
        for i in range(n)]


def test_fara_formulari_perechile_sunt_ca_inainte():
    perechi = ct.perechi_pentru(_amestec(30), 0.2, random.Random(0), "text")
    assert all("x" not in p and not p["tip"].startswith("da_nu") for p in perechi)
    assert {p["intrebare"] for p in perechi if p["tip"] == "nascut"} == {f"În ce an s-a născut Om{i}?" for i in range(30)}


def test_formulari_si_da_nu():
    perechi = ct.perechi_pentru(_amestec(60), 0.2, random.Random(0), "text", formulari=random.Random(1))
    nascut = [p for p in perechi if p["tip"] == "nascut"]
    assert len({p["intrebare"].replace(p["text"].split(" (")[0], "{x}") for p in nascut}) >= 4
    assert all(p["raspuns"] == "În 1905." for p in nascut)
    da_nu = [p for p in perechi if p["tip"].startswith("da_nu")]
    assert abs(len(da_nu) / len(perechi) - 0.15) < 0.04
    assert abs(sum(p["raspuns"] == "Da." for p in da_nu) - len(da_nu) / 2) <= 1
    for p in da_nu:
        assert p["raspuns"] in ("Da.", "Nu.") and p["fel"] == "text"
        if p["tip"] in ("da_nu_nascut", "da_nu_murit", "da_nu_an"):
            an = next(c for c in p["intrebare"].rstrip("?").split() if c.isdigit())
            assert (an in p["text"]) == (p["raspuns"] == "Da.")
    feluri = [p["fel"] for p in perechi]
    assert abs(feluri.count("nu_scrie") / len(feluri) - 0.2) < 0.03
    an = [p for p in perechi if p["tip"] == "an"]
    assert all(p["raspuns"] == ("În 1952." if p["intrebare"].startswith(("Când", "Ce an", "Care e")) else "Din 1952.")
               for p in an)


def test_da_nu_nu_schimba_valoarea_in_una_din_text():
    rng = random.Random(3)
    for _ in range(50):
        nou = ct._alta_valoare("locuitori", "1.204 locuitori", SAT, {}, rng)
        assert nou and nou != "1.204 locuitori" and nou.split()[0] not in SAT and nou.endswith("locuitori")
    assert ct._alta_valoare("judet", "Tulcea", SAT, {"judet": ["Tulcea"]}, rng) is None


def test_formularile_nu_sunt_din_examenul_s4():
    interzise = ct.inceputuri_interzise()
    for tip, formulari in ct.FORMULARI.items():
        assert 5 <= len(formulari) <= 8, tip
        for f in formulari + list(ct._LIPSA_VECHI.values()):
            assert ct._inceput(f.format(x="Xyz", y="Yzx")) not in interzise, f
    for f in sum(ct.DA_NU.values(), []):
        assert ct._inceput(f.format(x="Xyz", v="1950")) not in interzise, f


# --tipuri-noi (S11)
RAU = "Râul Boca este un curs de apă, afluent al râului Siret. Râul Boca are o lungime de 11 km și izvorăște de lângă Hăbășești."
SPECIE = ("Naja philippinensis este o specie de șerpi din genul Naja, familia Elapidae, descrisă de William Randolph Taylor "
          "în anul 1922. A fost clasificată de IUCN ca specie amenințată.")
DEPUTAT = ("Nicolae Ionescu (n. 10 iunie 1944) este un fost deputat român în legislatura 1996-2000, ales în județul Argeș pe "
           "listele partidului PUNR.")
ORAS = "Zvolen este un oraș în Slovacia centrală, situat pe râul Hron. Are 42.000 locuitori."
SAT_MD = "Scoreni este un sat din raionul Strășeni, Republica Moldova."
MUZEU = "Muzeul Zanabazar este un muzeu de artă din Ulaanbaatar și a fost fondat în 1966."
BISERICA = "Biserica din Cărbuna este un lăcaș de cult din satul Cărbuna, construit în 1894."


def _noi(text, x, tip):
    return {q["tip"]: q["raspuns"] for q in ct.intrebari_noi(text, x, tip)}


def test_tipurile_noi_iau_raspunsul_din_text():
    assert _noi(RAU, "Râul Boca", "ce") == {"nou_afluent": "Al râului Siret.", "nou_lungime": "11 km."}
    assert _noi(SPECIE, "Naja philippinensis", "ce") == {  # genul e chiar în nume, deci nu se întreabă
        "nou_familie": "Din familia Elapidae.", "nou_descris_cine": "William Randolph Taylor.", "nou_descris_an": "În 1922."}
    assert _noi(DEPUTAT, "Nicolae Ionescu", "om") == {"nou_legislatura": "În legislatura 1996-2000.",
                                                     "nou_partid": "Pe listele partidului PUNR."}
    assert _noi(ORAS, "Zvolen", "loc") == {"nou_rau": "Pe râul Hron."}
    assert _noi(SAT_MD, "Scoreni", "loc") == {"nou_raion": "În raionul Strășeni."}
    assert _noi(MUZEU, "Muzeul Zanabazar", "ce") == {"nou_fondat_an": "În 1966."}
    assert _noi(BISERICA, "Biserica din Cărbuna", "ce") == {"nou_construit_an": "În 1894."}
    for text, x, tip in [(RAU, "Râul Boca", "ce"), (SPECIE, "Naja philippinensis", "ce"), (DEPUTAT, "Nicolae Ionescu", "om")]:
        for q in ct.intrebari_noi(text, x, tip):
            assert q["valoare"] in text


def test_tipurile_noi_cu_mai_multi_autori_si_acord():
    text = "Sphaerodactylus scaber este o specie de șopârle din familia Gekkonidae, descrisă de Thomas Barbour și Ramsden 1919."
    assert _noi(text, "Sphaerodactylus scaber", "ce")["nou_descris_cine"] == "Thomas Barbour și Ramsden."
    p = {"tip": "nou_descris_cine", "x": "Sphaerodactylus scaber", "f": "descrisă"}
    for samanta in range(5):
        assert " a descris" not in ct._intrebare_noua(p, random.Random(samanta), "Thomas Barbour și Ramsden")
    assert ct._acord("construit", "Biserica din Cărbuna") == "construită"
    assert ct._acord("fondată", "Muzeul Zanabazar") == "fondat"
    assert ct.intrebari_noi(BISERICA, "Biserica din Cărbuna", "ce")[0]["f"] == "construită"


def test_tipurile_noi_nu_iau_alt_subiect():
    familie = "Silviile (Sylviidae) sunt o familie de păsări cântătoare, la fel ca și cele din familia Muscicapidae."
    assert "nou_familie" not in _noi(familie, "Silviile", "ce")
    boala = "Cenuroza este o parazitoză a unor specii de viermi plați paraziți din genul Taenia."
    assert "nou_gen" not in _noi(boala, "Cenuroza", "ce")
    afluent = "Chetriș este un sat din Republica Moldova. Localitatea este situată pe malul râului Camenca, afluent al râului Prut."
    assert "nou_afluent" not in _noi(afluent, "Chetriș", "loc")
    doi = "Ludovic Rákóczi este un fost deputat român în legislatura 1992-1996 și în legislatura 1996-2000, ales pe listele UDMR."
    assert "nou_legislatura" not in _noi(doi, "Ludovic Rákóczi", "om")


def test_nu_scrie_la_tipurile_noi_doar_ce_lipseste():
    def lipsa(text, x, tip):
        return {q["tip"] for q in ct.lipsa_noi(text, x, tip)}

    assert "lipsa_nou_afluent" not in lipsa(RAU, "Râul Boca", "ce")
    assert "lipsa_nou_afluent" in lipsa("Râul Cerna este un râu din România, care izvorăște din Munții Godeanu.", "Râul Cerna", "ce")
    assert not {"lipsa_nou_familie", "lipsa_nou_descris_cine"} & lipsa(SPECIE, "Naja philippinensis", "ce")
    homo = "Homo ergaster este o specie umanoidă preistorică, posibil precursor al oamenilor moderni."
    assert {"lipsa_nou_familie", "lipsa_nou_descris_cine"} <= lipsa(homo, "Homo ergaster", "ce")
    assert "lipsa_nou_descris_cine" not in lipsa("Ballota este un gen de plante din familia Lamiaceae.", "Ballota", "ce")
    assert not {"lipsa_nou_legislatura", "lipsa_nou_partid"} & lipsa(DEPUTAT, "Nicolae Ionescu", "om")
    fost = "Teodora Mihăilescu (n. 17 septembrie 1960) este o economistă română, fost deputat."
    assert {"lipsa_nou_legislatura", "lipsa_nou_partid"} <= lipsa(fost, "Teodora Mihăilescu", "om")
    assert "lipsa_nou_partid" not in lipsa("Alexandru Alexandrini a fost membru al P.N.L., deputat.", "Alexandru Alexandrini", "om")
    assert "lipsa_nou_construit_an" not in lipsa("Arcul lui Severus este un arc. A fost construit în 203.", "Arcul lui Severus", "ce")
    assert "lipsa_nou_fondat_an" not in lipsa("Clubul X este un club. A fost fondat la în districtul Rímac.", "Clubul X", "ce")
    assert "lipsa_nou_rau" not in lipsa(ORAS, "Zvolen", "loc")
    assert all(q["raspuns"] == ct.NU_SCRIE for q in ct.lipsa_noi(homo, "Homo ergaster", "ce"))


def _articole_noi(n):
    partide, familii, raioane = ["PUNR", "FSN", "PSD", "PNL"], ["Elapidae", "Colubridae", "Viperidae"], ["Strășeni", "Cahul", "Orhei"]
    articole = []
    for i in range(n):
        ani = f"{1990 + i % 5 * 4}-{1994 + i % 5 * 4}"
        articole += [
            {"x": f"Deputat{i}", "tip": "om",
             "text": DEPUTAT.replace("Nicolae Ionescu", f"Deputat{i}").replace("1996-2000", ani).replace("PUNR", partide[i % 4])},
            {"x": f"Specia{i} rara", "tip": "ce",
             "text": SPECIE.replace("Naja philippinensis", f"Specia{i} rara").replace("Elapidae", familii[i % 3])},
            {"x": f"Satul{i}", "tip": "loc", "text": SAT_MD.replace("Scoreni", f"Satul{i}").replace("Strășeni", raioane[i % 3])},
            {"x": f"Teodora{i} Mihăilescu", "tip": "om", "text": f"Teodora{i} Mihăilescu (n. 1960) este o economistă română, fost deputat."},
        ]
    return articole


def test_perechi_noi_da_nu_si_nu_scrie():
    perechi = ct.perechi_noi(_articole_noi(60), 0.2, 0.15, random.Random(0), "text")
    feluri = [p["fel"] for p in perechi]
    assert abs(feluri.count("nu_scrie") / len(feluri) - 0.2) < 0.03
    da_nu = [p for p in perechi if p["tip"].startswith("da_nu_nou")]
    assert abs(len(da_nu) / len(perechi) - 0.15) < 0.04
    assert abs(sum(p["raspuns"] == "Da." for p in da_nu) - len(da_nu) / 2) <= 1
    deschise = {p["grup"] for p in perechi if p["fel"] == "text" and not p["tip"].startswith("da_nu")}
    for p in da_nu:  # perechea-soră: o întrebare deschisă despre același text
        assert p["grup"] in deschise
        if p["raspuns"] == "Nu." and p["tip"] in ("da_nu_nou_familie", "da_nu_nou_raion"):
            assert p["intrebare"].rstrip("?").split()[-1] not in p["text"]
        if p["raspuns"] == "Nu." and p["tip"] == "da_nu_nou_descris_an":
            assert next(c for c in p["intrebare"].rstrip("?").split() if c.isdigit()) not in p["text"]
    assert all(set(p) == {"fel", "limba", "grup", "text", "tip", "raspuns", "x", "intrebare"} for p in perechi)


def test_tipurile_noi_nu_sunt_din_examenul_s4():
    interzise = ct.inceputuri_interzise()
    for tip, formulari in ct.TIPURI_NOI.items():
        assert 3 <= len(formulari) <= 5, tip
    for f in sum(ct.TIPURI_NOI.values(), []) + sum(ct.DA_NU_NOI.values(), []):
        assert not ct.INTERZISE_S4_B.search(f.format(x="", f="", v="")), f
        assert ct._inceput(f.format(x="Xyz", f="fondat", v="1950")) not in interzise, f
    for interzis in ["În ce țară se află X?", "Cu ce trupă a cântat X?", "Unde s-a născut X?", "Ce meserie are X?",
                     "Cărui zeu îi este dedicat X?", "Ce firmă a lansat X?", "Care este reședința X?"]:
        assert ct.INTERZISE_S4_B.search(interzis.replace("X", "")), interzis
    noi = ct.perechi_noi(_articole_noi(20), 0.2, 0.15, random.Random(0), "text")
    v = ct.verificari_tipuri_noi([{k: x for k, x in p.items() if k != "x"} for p in noi], noi)
    assert v["i_sabloane_cu_tip_din_S4b"] == [] and v["i_intrebari_noi_cu_tip_din_S4b"] == 0
    assert v["ii_sabloane_noi_cu_inceput_din_S4"] == [] and v["ii_inceputuri_din_S4"] == 0
    assert v["iii_texte_din_examene"] == 0


def test_conversatia_simpla_nu_are_intrebarile_din_examen():
    from unelte.genereaza_conversatie import normalizat

    simple = json.loads((ct.RADACINA / ct.CONVERSATIE).read_text(encoding="utf-8"))["perechi"]
    examen = json.loads((ct.RADACINA / ct.SCRISE_DE_MANA).read_text(encoding="utf-8"))["conversatie"]
    assert len(simple) >= 40
    assert not {normalizat(p["intrebare"]) for p in simple} & {normalizat(p["intrebare"]) for p in examen}
