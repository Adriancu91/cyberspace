"""Școala de conversație (15 octombrie 2026): generatorul de perechi, modelul care învață doar pe răspunsuri și examenul.
Fără placă video și fără profesor."""

from __future__ import annotations

import json

import pytest

from unelte import examen_conversatie as ex
from unelte import genereaza_conversatie as gc


def pereche(fel="zi", limba="ro", nota=9, q="Ce este ploaia?", r="Ploaia este apă care cade din nori."):
    return {"fel": fel, "limba": limba, "nota": nota, "intrebare": q, "raspuns": r}


def test_cererile_au_felurile_si_limbile_cerute():
    fapte = [("snow", "Water freezes."), ("birds", "Birds have feathers.")]
    cereri = [gc.cererea(k, fapte) for k in range(400)]
    feluri = [c["fel"] for c in cereri]
    assert feluri.count("zi") == 300 and feluri.count("fapte") == 80 and feluri.count("nu_stiu") == 20
    assert sum(c["limba"] == "ro" for c in cereri) == 320  # 80% în română
    assert {c["fapt"] for c in cereri if c["fel"] == "fapte"} == {"Water freezes.", "Birds have feathers."}
    assert all(c["tema"] in gc.TEME for c in cereri if c["fel"] == "zi")
    assert "Nu știu sigur." in gc.mesaje_cerere(next(c for c in cereri if c["fel"] == "nu_stiu" and c["limba"] == "ro"))[1]["content"]


def test_perechile_si_notele_se_citesc():
    text = "Î: Ce este ploaia?\nR: Apă care cade din nori.\n\n2. Q: Why is the sky blue?\nA: Because of sunlight.\nalt text"
    assert gc.citeste_perechi(text) == [("Ce este ploaia?", "Apă care cade din nori."),
                                        ("Why is the sky blue?", "Because of sunlight.")]
    assert gc.citeste_nota("GRADE: 9\nREASON: bine") == {"nota": 9, "motiv": "bine"}
    assert gc.citeste_nota("NOTA: 12")["nota"] == 10 and gc.citeste_nota("nimic")["nota"] is None
    assert "diacritics" in gc.mesaje_nota(pereche())[1]["content"] and "Be strict" in gc.mesaje_nota(pereche())[1]["content"]


@pytest.mark.parametrize("p, motiv", [
    (pereche(), None),
    (pereche(nota=7), "nota sub 8"),
    (pereche(nota=None), "fără notă"),
    (pereche(fel="nu_stiu", r="Nu știu sigur."), None),
    (pereche(fel="nu_stiu", limba="en", r="I don't know for sure."), None),
    (pereche(fel="nu_stiu", r="Poate mâine."), "„nu știu” cu alt răspuns"),
    (pereche(r="Nu știu sigur."), "„nu știu” la o întrebare care se știe"),
    (pereche(q="Ce  este ploaia ?!"), "întrebare repetată"),
    (pereche(r="Once upon a time there was a little girl named Lily who"), "bucată dintr-un examen sau dintr-o validare"),
])
def test_ce_se_scoate(p, motiv):
    vazute = {gc.normalizat("ce este ploaia")} if motiv == "întrebare repetată" else set()
    interzise = gc.bucati("Once upon a time there was a little girl named Lily who loved")
    if motiv == "întrebare repetată":
        p = {**p}
    assert gc.de_ce_se_scoate(p, vazute, interzise) == motiv


def test_normalizat_fara_diacritice_si_semne():
    assert gc.normalizat("Ce ȘTII despre „țară”?") == "ce stii despre tara"


def test_examenul_si_antrenarea_nu_se_suprapun(tmp_path):
    toate = ([{**pereche(q=f"Întrebarea {i}?"), "ramane": True, "motiv_scos": None, "cerere": i} for i in range(400)]
             + [{**pereche(fel="nu_stiu", q=f"Nu se știe {i}?", r="Nu știu sigur."), "ramane": True, "motiv_scos": None,
                 "cerere": 500 + i} for i in range(50)]
             + [{**pereche(nota=5, q="Rea?"), "ramane": False, "motiv_scos": "nota sub 8", "cerere": 999}])
    (tmp_path / "toate.jsonl").write_text("\n".join(json.dumps(p, ensure_ascii=False) for p in toate), encoding="utf-8")
    info = gc.finalizeaza(tmp_path, tmp_path / "docs" / "de_verificat.md", None)
    examen = json.loads((tmp_path / "examen.json").read_text(encoding="utf-8"))["perechi"]
    antrenare = [json.loads(r) for r in (tmp_path / "antrenare.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(examen) == 300 and sum(p["fel"] == "nu_stiu" for p in examen) == 30 and len(antrenare) == 150
    assert not {p["intrebare"] for p in examen} & {p["intrebare"] for p in antrenare}
    assert info["bune"] == 450 and info["scoase"] == {"nota sub 8": 1}
    text = (tmp_path / "antrenare.txt").read_text(encoding="utf-8")
    assert text.startswith("Întrebare: ") and "\nRăspuns: " in text and text.count("<|endoftext|>") == 150
    fisa = (tmp_path / "docs" / "de_verificat.md").read_text(encoding="utf-8")
    assert fisa.count("- Întrebare: ") == 30 and "**30.**" in fisa


# --- modelul de conversație ---------------------------------------------------------------------------------------

def test_pierderea_se_socoteste_doar_pe_raspunsuri():
    torch = pytest.importorskip("torch")
    from module.model_conversatie import IGNORAT, ModelGPTConversatie

    perechi = [([1, 2, 3], [7, 8]), ([4, 5], [9])]
    x, y = ModelGPTConversatie.fereastra_conversatie(perechi, 16, torch.Generator().manual_seed(0))
    assert len(x) == len(y) == 16
    lista_x, lista_y = x.tolist(), y.tolist()
    for i, simbol in enumerate(lista_y):  # ținta e simbolul următor, doar dacă e într-un răspuns
        if simbol != IGNORAT:
            assert simbol in (7, 8, 9)
    assert all(lista_y[i] == IGNORAT for i in range(15) if lista_x[i + 1] in (1, 2, 3, 4, 5) if i + 1 < 16)
    assert any(s != IGNORAT for s in lista_y)


def test_modelul_invata_pe_amestec(tmp_path, monkeypatch):
    pytest.importorskip("torch")
    from module.model_conversatie import ModelGPTConversatie, intrebarea
    from module.tokenizer_bpe import antreneaza_bpe

    text = ("Once upon a time there was a dog. " * 200) + "<|endoftext|>"
    (tmp_path / "hrana.txt").write_text("Birds have feathers. " * 200, encoding="utf-8")
    (tmp_path / "conv.jsonl").write_text("\n".join(json.dumps({"intrebare": f"Ce face cățelul {i}?", "raspuns": "Latră."})
                                                   for i in range(20)), encoding="utf-8")
    antreneaza_bpe(text + " Întrebare: Răspuns: Ce face cățelul? Latră.", 300).salveaza(tmp_path / "bpe.json")

    class Date:
        def text_antrenare(self):
            return text

    model = ModelGPTConversatie(n_straturi=1, n_capete=2, n_emb=32, context=32, lot=20, dispozitiv="cpu",
                                tokenizer="bpe", cale_tokenizer=str(tmp_path / "bpe.json"), rata_invatare=3e-3,
                                pasi_max=60, conversatie=str(tmp_path / "conv.jsonl"), fractie_conversatie=0.75,
                                hrana=str(tmp_path / "hrana.txt"), fractie_hrana=0.05)
    s = model.antreneaza(Date(), 60.0)
    assert s["pasi"] == 60 and s["perechi_conversatie"] == 20
    assert s["ferestre"] == {"conversatie": 900, "hrana": 60, "text": 240}  # 75% / 5% / 20% din 60 × 20
    assert model.completeaza(intrebarea("Ce face cățelul 3?"), 3).strip().startswith("Lat")
    with pytest.raises(ValueError):
        ModelGPTConversatie(conversatie="a.jsonl", fractie_conversatie=0.0)


# --- examenul -------------------------------------------------------------------------------------------------------

def test_examenul_taie_raspunsul_si_recunoaste_nu_stiu():
    assert ex.taie(" Latră.\nÎntrebare: alta") == "Latră." and ex.taie("Da.<|endoftext|>Once") == "Da."
    assert ex.spune_nu_stiu("Nu știu sigur.") and ex.spune_nu_stiu("I don't know for sure.")
    assert not ex.spune_nu_stiu("Ploaia cade din nori.")
    intrebari = [{"fel": "zi", "raspuns_elev": "Da.", "nota_elev": 8, "nu_stiu_corect": False},
                 {"fel": "zi", "raspuns_elev": "Nu știu.", "nota_elev": 2, "nu_stiu_corect": False},
                 {"fel": "nu_stiu", "raspuns_elev": "Nu știu sigur.", "nota_elev": 10, "nu_stiu_corect": True},
                 {"fel": "nu_stiu", "raspuns_elev": "Mâine.", "nota_elev": None, "nu_stiu_corect": False}]
    s = ex.scoruri(intrebari)
    assert s["nota_medie"] == round((8 + 2 + 10) / 3, 3) and s["nota_medie_fara_nu_stiu"] == 5.0
    assert (s["nu_stiu_corecte"], s["nu_stiu_fractie"], s["nu_stiu_la_stiute"], s["note_neciteite"]) == (1, 0.5, 0.5, 1)


def test_ortografia_scoate_cuvintele_necunoscute(tmp_path):
    from unelte import ortografie_ro as orto

    (tmp_path / "ro.txt").write_text("Iarna este rece. Apa îngheață când e frig. Vara e cald. " * 5, encoding="utf-8")
    cunoscute = set(orto.construieste([tmp_path / "ro.txt"], minim=3))
    assert {"iarna", "îngheață", "vara"} <= cunoscute
    # „Ana” la început de propoziție nu se poate deosebi de un cuvânt obișnuit: e verificat (și iese)
    assert orto.necunoscute("Iarna este frisoasă. Ana spune că vara e cald.", cunoscute) == ["frisoasă", "Ana", "spune", "că"]
    assert orto.necunoscute("Iarna e rece, spune Ana.", cunoscute) == ["spune"]  # „Ana” în mijloc: nume propriu
    assert orto.necunoscute("Iarna este frisoasă.", cunoscute, {"frisoasă"}) == []  # excepție
    ortografie = (cunoscute, set())
    assert gc.de_ce_se_scoate(pereche(q="Iarna este rece?", r="Apa îngheață."), set(), set(), ortografie) is None
    assert gc.de_ce_se_scoate(pereche(q="Iarna este rece?", r="Apa se răcosește."), set(), set(),
                              ortografie) == "cuvânt necunoscut: se, răcosește"
    assert gc.de_ce_se_scoate(pereche(limba="en", q="Is it cold?", r="Yes, it is."), set(), set(), ortografie) is None


def test_sursele_noi_si_traducerea_nu_se_despart_de_original(tmp_path):
    en = [{**pereche(limba="en", q=f"What is thing {i}?", r="It is a thing."), "ramane": True, "motiv_scos": None,
           "cerere": i, "profesor": "Qwen/Qwen3-4B-Instruct-2507"} for i in range(400)]
    (tmp_path / "toate.jsonl").write_text("\n".join(json.dumps(p) for p in en), encoding="utf-8")
    trad = [{"fel": "zi", "limba": "ro", "intrebare": f"Ce este lucrul {i}?", "raspuns": "Este un lucru.",
             "grup": gc.grup(en[i])} for i in range(400)]
    wiki = [{"fel": "wiki", "limba": "ro", "intrebare": "Ce este lucrul 1?", "raspuns": "Repetat.", "grup": "wiki_0"},
            {"fel": "wiki", "limba": "ro", "intrebare": "Ce este frisoasa?", "raspuns": "Frisoasă.", "grup": "wiki_1"}]
    (tmp_path / "traduceri.jsonl").write_text("\n".join(json.dumps(p, ensure_ascii=False) for p in trad), encoding="utf-8")
    (tmp_path / "wikipedia.jsonl").write_text("\n".join(json.dumps(p, ensure_ascii=False) for p in wiki), encoding="utf-8")
    cunoscute = {"ce", "este", "lucrul", "un", "lucru", "repetat"}
    toate, bune = gc.toate_bune(tmp_path, interzise=set(), ortografie=(cunoscute, set()))
    scoase = {p["intrebare"]: p["motiv_scos"] for p in toate if not p["ramane"]}
    assert scoase == {"Ce este lucrul 1?": "întrebare repetată", "Ce este frisoasa?": "cuvânt necunoscut: frisoasa, Frisoasă"}
    examen, antrenare = gc.imparte(bune)
    in_examen = {gc.grup(p) for p in examen}
    assert len(examen) == 300 and not in_examen & {gc.grup(p) for p in antrenare}  # originalul și traducerea: împreună


def test_o_sursa_scoasa_de_adrian_nu_mai_intra(tmp_path):
    (tmp_path / "toate.jsonl").write_text("", encoding="utf-8")
    for nume, q in (("wikipedia.jsonl", "Ce este lucrul?"), ("traduceri.jsonl", "Ce este un lucru?")):
        (tmp_path / nume).write_text(json.dumps({"fel": "zi", "limba": "ro", "intrebare": q, "raspuns": "Este un lucru."},
                                                ensure_ascii=False), encoding="utf-8")
    ortografie = ({"ce", "este", "lucrul", "un", "lucru"}, set())
    assert len(gc.toate_bune(tmp_path, set(), ortografie)[1]) == 2
    (tmp_path / "surse_excluse.txt").write_text("traduceri.jsonl\n", encoding="utf-8")
    bune = gc.toate_bune(tmp_path, set(), ortografie)[1]
    assert [p["sursa_fisier"] for p in bune] == ["wikipedia.jsonl"]
    docs = tmp_path / "fisa.md"
    (tmp_path / "surse_excluse.txt").unlink()
    gc.scrie_fisa(tmp_path, docs, interzise=set(), ortografie=ortografie)
    text = docs.read_text(encoding="utf-8")
    assert "**1. W**" in text and "**2. T**" in text and "peste 2 greșite din 15" in text


@pytest.mark.parametrize("propozitie, rupta", [
    ("A fost dezvoltat în ComitatulWestchester, New York.", True),
    ("Este un film realizat de soții și după povestirea „Casa” a lui.", True),
    ("S-a specializat în scene maritime din.", True),
    ("În, a devenit campion mondial în Formula 1.", True),
    ("Are o culoare albă: .", True),
    ("A fost distins cu Ordinul „Sf.", True),
    ("Matcha, ceaiul verde ( ), e preparat așa.", True),
    ("Libretul a fost scris de Alfred Maria Willner.", False),
    ("Bergen este un oraș în provincia Vestland, din vestul Norvegiei.", False),
    ("Orașul are aproximativ 239.209 de locuitori.", False),
])
def test_wikipedia_propozitiile_rupte_ies(propozitie, rupta):
    from unelte.conversatie_wikipedia import propozitie_rupta

    assert (propozitie_rupta(propozitie) is not None) is rupta


def test_wikipedia_greselile_de_tipar_si_oamenii():
    from unelte.conversatie_wikipedia import greseala_de_tipar, pereche_din

    assert greseala_de_tipar("Aceast film e bun.", {"aceast": 231, "această": 104618, "film": 9000}) == "aceast"
    assert greseala_de_tipar("Acest film e bun.", {"acest": 112196, "această": 104618}) is None
    om = pereche_din("Ion Voicu (n. 1923 – d. 1997) a fost un violonist român, elev al lui George Enescu.\nCorp.")
    assert om["tip"] == "om" and om["intrebare"] == "Cine a fost Ion Voicu?" and om["raspuns"].startswith("Ion Voicu a fost")
    emisiune = pereche_din("Cronica este o emisiune de televiziune, difuzată miercurea. Au prezentat-o mai mulți (2001-2010).\nX")
    assert emisiune is None or emisiune["tip"] != "om"
    assert pereche_din("Un cookie este un text trimis de un server unui navigator web.\nCorp.") is None


@pytest.mark.parametrize("propozitie, lista", [
    ("Tătăranu este o comună în județul Vrancea, Muntenia, România, formată din satele Bordeasca Nouă, Bordeasca Veche, "
     "Mărtinești, Tătăranu și Vâjâitoarea.", True),
    ("Grupul e unul dintre cele 8, celelalte fiind dislocate în Estonia, Letonia, Lituania, Polonia.", True),
    ("Rolurile au fost interpretate de actorii Iurie Darie, Alexandru Munte, Alexandru Repan și Melania Cîrje.", True),
    ("Costișa este o comună în județul Neamț, Moldova, România, formată din satele Costișa, Dornești, Frunzeni și "
     "Mănoaia.", True),
    ("Cleja este o comună în județul Bacău, Moldova, România, formată din satele Cleja, Somușca și Valea Mică.", False),
    ("André Henri Lavrillier a fost un artist plastic, gravor de monede și medalist francez.", False),
])
def test_wikipedia_v3_listele_ies(propozitie, lista):
    from unelte.conversatie_wikipedia import are_lista

    assert are_lista(propozitie) is lista


def test_wikipedia_v3_numeralele_si_acordul():
    from unelte.conversatie_wikipedia import _ACORD, numeral_fara_de

    assert numeral_fara_de("Sezonul include peste cincizeci turnee.") == "cincizeci turnee"
    assert numeral_fara_de("Sezonul include 25 turnee.") == "25 turnee"
    assert numeral_fara_de("Clubul are 100 membri.") == "100 membri"
    for bun in ("A câștigat 24 de titluri.", "Are 101 membri.", "Un film din 1963 regizat de el.", "Timp de 19 sezoane.",
                "Lansat pe 15 noiembrie 1995.", "Un râu de 20 km lungime.", "Folosit de 85-90% din vorbitori."):
        assert numeral_fara_de(bun) is None, bun
    assert _ACORD.search("A fost cel de-al 52-lea sezon a celei de-a doua competiții.")
    assert _ACORD.search("A fost cea de-a 3-a ediție al unui turneu.")
    assert not _ACORD.search("A fost cel de-al 52-lea sezon al celei de-a doua competiții.")
    assert not _ACORD.search("Sezonul a fost bun.")


def test_wikipedia_v3_doar_prima_propozitie_si_oamenii():
    from unelte.conversatie_wikipedia import pereche_din

    p = pereche_din("Konrad Bercovici (n. 22 iunie 1882, Brăila – d. 27 decembrie 1961, New York) a fost un prozator și "
                    "dramaturg american de origine evreiască din România. A scris multe romane.\nCorp.")
    assert p["intrebare"] == "Cine a fost Konrad Bercovici?" and p["raspuns"].endswith("din România.")
    p = pereche_din("Carol Stanciu (n. 1937) este un medic, gastroenterolog, membru de onoare al Academiei Române.\nx")
    assert p["intrebare"] == "Cine este Carol Stanciu?"
    razboi = pereche_din("Primul Război Mondial (1914–1918) a fost un conflict militar global care a început în Europa.\nx")
    assert razboi["tip"] == "ce" and razboi["intrebare"] == "Ce a fost Primul Război Mondial?"
    p = pereche_din("Sorin Babii este un fost trăgător de tir român, laureat cu aur la Seul 1988.\nx")
    assert p["intrebare"] == "Cine este Sorin Babii?"
    p = pereche_din("Horia Agarici a fost un maior aviator al Forțelor Aeriene Române.\nx")
    assert p["intrebare"] == "Cine a fost Horia Agarici?"
    lung = " ".join(["cuvânt"] * 30)
    assert pereche_din(f"Lucrul este un obiect {lung}.\nx") is None  # peste 30 de cuvinte
    assert pereche_din(f"Lucrul este un obiect {lung}.\nx", max_cuvinte=40) is not None


def test_wikipedia_v3_oamenii_dupa_prenume():
    from unelte.conversatie_wikipedia import oamenii_dupa_prenume, pereche_din

    oameni = [pereche_din(f"John Smith{i} (n. 1900) a fost un pictor englez din Londra.\nx") for i in range(3)]
    constable = pereche_din("John Constable a fost un remarcabil pictor peisagist englez de factură romantică.\nx")
    film = pereche_din("John Wick este un film american de acțiune din 2014, regizat de Chad Stahelski.\nx")
    rar = pereche_din("Zorbas Constable a fost un remarcabil pictor peisagist englez de factură romantică.\nx")
    assert constable["tip"] == "ce" and film["tip"] == "ce"
    assert oamenii_dupa_prenume(oameni + [constable, film, rar]) == 1
    assert constable["intrebare"] == "Cine a fost John Constable?" and constable["tip"] == "om"
    assert film["intrebare"] == "Ce este John Wick?" and rar["tip"] == "ce"  # „Zorbas”: prenume nevăzut la oameni


def test_wikipedia_v3_lucrurile_nu_devin_oameni():
    from unelte.conversatie_wikipedia import oamenii_dupa_prenume, pereche_din

    medalia = pereche_din("Medalia „Răsplata Muncii” este o medalie românească instituită prin decret regal în 1898.\nx")
    assert medalia["tip"] == "ce"
    assert pereche_din("În geometrie un segment de cerc este o zonă dintr-un disc tăiată de o coardă.\nx") is None
    assert pereche_din("Adrian Gurzău este un politician român, deputat de din partea PDL.\nx") is None
    oameni = [pereche_din(f"The Edge{i} (n. 1961) este un chitarist irlandez din trupa U2.\nx") for i in range(3)]
    filme = [pereche_din(f"The Film{i} este un film american din 1990, regizat de John Ford.\nx") for i in range(2)]
    album = pereche_din("The Fame Monster este un disc pop al unei cântărețe americane, lansat în anul 2009.\nx")
    assert album["poate_om"] and oamenii_dupa_prenume(oameni + filme + [album]) == 0  # 3 la oameni, 2 la filme


def test_wikipedia_v3_litera_straina_iese():
    from unelte.conversatie_wikipedia import pereche_din

    assert pereche_din("Cruciada norvegiană a fost o cruciadă, întreprinsǎ de regele Sigurd I între 1107 și 1110.\nx") is None
    assert pereche_din("Cruciada norvegiană a fost o cruciadă, întreprinsă de regele Sigurd I între 1107 și 1110.\nx")
