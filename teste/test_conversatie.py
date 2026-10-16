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
