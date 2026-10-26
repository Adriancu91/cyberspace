"""E3 „memoria” (S24, 23 octombrie 2026): tăierea în bucăți, indexul FTS5, documentele noi adăugate pe loc, variantele
de întrebare și măsurarea (pe un Wikipedia mic, inventat, fără model)."""

import json

import pytest

from unelte import e3_memorie as e3

ARTICOLE = [
    "Bilca este o comună în raionul Hliboca, regiunea Cernăuți, Ucraina.\nAre o biserică veche din lemn.",
    "Mărturie mortală este un film de acțiune american din 2006, regizat de Richard Donner. "
    "Rolurile principale sunt interpretate de Bruce Willis.",
    "Peştera Mondmilchloch este situată pe Muntele Pilat din Elveția.",
    "Podul Pupin este un pod peste Dunăre, la Belgrad, în Serbia. A fost deschis în 2014.",
]
TEXT_NOU = "Comitatul Exemplu este un comitat din statul Inventat. Reședința comitatului este orașul Nicăieri."


def _wikipedia(tmp_path):
    cale = tmp_path / "wiki.txt"
    cale.write_text("<|endoftext|>".join(ARTICOLE), encoding="utf-8")
    return cale


def _examene(tmp_path):
    s15 = {"perechi": [
        {"fel": "text", "categorie": "b2", "text": "Peştera Mondmilchloch este situată pe Muntele Pilat din Elveția.",
         "intrebare": "În ce țară se află Peștera Mondmilchloch?", "raspuns": "În Elveția."},
        {"fel": "text", "categorie": "e", "text": TEXT_NOU, "intrebare": "Care e reședința Comitatului Exemplu?",
         "raspuns": "Orașul Nicăieri."}]}
    s4 = {"perechi": [
        {"fel": "text", "categorie": "a", "text": TEXT_NOU, "intrebare": "În ce stat e Comitatul Exemplu?",
         "raspuns": "Statul Inventat."},
        {"fel": "text", "categorie": "c", "text": TEXT_NOU, "intrebare": "E în statul Inventat?", "raspuns": "Da."},
        {"fel": "nu_scrie", "categorie": "d", "text": TEXT_NOU, "intrebare": "Câți locuitori are?",
         "raspuns": "Nu scrie în text."}]}
    n10 = {"perechi": [
        {"fel": "text", "text": ARTICOLE[1].split(" Rolurile")[0], "intrebare": "Cine a regizat Mărturie mortală?",
         "raspuns": "Richard Donner."},
        {"fel": "conversatie", "intrebare": "Bună!", "raspuns": "Bună ziua!"}]}
    rez = {}
    for nume, obiect in (("S15", s15), ("S4", s4), ("noaptea10", n10)):
        cale = tmp_path / f"{nume}.json"
        cale.write_text(json.dumps(obiect, ensure_ascii=False), encoding="utf-8")
        rez[nume] = str(cale)
    return rez


def test_taie_la_sfarsit_de_propozitie_si_sub_maxim():
    text = " ".join(f"Propoziția numărul {i} are câteva cuvinte în ea." for i in range(40))
    bucati = e3.taie(text, maxim=200)
    assert all(len(b) <= 200 for b in bucati)
    assert all(b.endswith(".") for b in bucati)
    assert " ".join(bucati) == text
    lunga = "cuvânt " * 100
    assert all(len(b) <= 50 for b in e3.taie(lunga, maxim=50))
    assert e3.taie("Peştera e mare.") == ["Peștera e mare."]  # ş → ș


def test_interogarile_variantelor():
    assert e3.interogare("Cine a regizat Mărturie mortală?", "intreaga") == \
        '"cine" OR "a" OR "regizat" OR "mărturie" OR "mortală"'
    assert e3.interogare("Cine a regizat Mărturie mortală?", "fara_cuvinte") == '"regizat" OR "mărturie" OR "mortală"'
    assert e3.interogare("Cine a regizat Mărturie?", "fara_cuvinte_prefix5") == '"regiz"* OR "mărtu"*'
    assert e3.interogare("Cine a regizat Mărturie?", "fara_cuvinte_si") == '"regizat" AND "mărturie"'
    assert e3.interogare("Cine a regizat Mărturie?", "fara_cuvinte_perechi") == \
        '"regizat" OR "mărturie" OR "regizat mărturie"'
    assert e3.interogare("Cine e?", "fara_cuvinte") == '"cine" OR "e"'  # doar cuvinte de întrebare: rămân toate


def test_intrebarile_de_examen_fara_da_nu_si_nu_scrie(tmp_path):
    q = e3.intrebari_examen(_examene(tmp_path))
    assert [(x["examen"], x["categorie"]) for x in q] == [("S15", "b2"), ("S15", "e"), ("S4", "a"), ("noaptea10", None)]
    texte = e3.texte_examen(_examene(tmp_path))
    assert len(texte) == 3 and texte[1]["examene"] == ["S15", "S4"]


def test_index_adauga_si_masoara(tmp_path):
    lucru = tmp_path / "e3"
    examene = _examene(tmp_path)
    info = e3.cmd_index(_wikipedia(tmp_path), lucru, examene)
    assert info["articole"] == 4 and info["bucati"] >= 4
    assert info["texte_examen"] == 3 and info["texte_examen_deja_in_wikipedia"] == 2  # Mondmilchloch și Mărturie

    con = e3.deschide(lucru / "index.sqlite")
    assert e3.cauta(con, "Ce comitat e în statul Inventat?", "fara_cuvinte") == []  # încă nu e învățat
    con.close()
    adaugat = e3.cmd_adauga(lucru)
    assert adaugat["adaugate"] == 1 and adaugat["deja_in_wikipedia"] == 2
    with pytest.raises(SystemExit):
        e3.cmd_adauga(lucru)

    con = e3.deschide(lucru / "index.sqlite")
    gasite = e3.cauta(con, "Care e reședința Comitatului Exemplu?", "fara_cuvinte")
    assert gasite and gasite[0]["sursa"] == "examen"  # document nou = găsit pe loc, fără antrenare
    assert e3.primul_bun(gasite, "Orașul Nicăieri.") == 1
    # regula verificatorului: „În Elveția.” nu e acoperit de „… din Elveția.” (1 din 2 cuvinte < 0,8)
    gasite = e3.cauta(con, "În ce țară se află Peștera Mondmilchloch?", "fara_cuvinte")
    assert gasite[0]["articol"] == "w2" and e3.primul_bun(gasite, "În Elveția.") is None
    gasite = e3.cauta(con, "Unde e podul Pupin regizat?", "fara_cuvinte_si", k=3)  # AND: nimic → completat cu OR
    assert [g["articol"] for g in gasite] == ["w3", "w1"]
    con.close()

    v3 = tmp_path / "v3.jsonl"
    v3.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in [
        {"fel": "text", "text": ARTICOLE[0], "intrebare": "În ce raion se află Bilca?", "raspuns": "În raionul Hliboca."},
        {"fel": "text", "text": ARTICOLE[3], "intrebare": "Peste ce râu e Podul Pupin?", "raspuns": "Peste Dunăre."},
        {"fel": "text", "text": ARTICOLE[3], "intrebare": "E podul în Serbia?", "raspuns": "Da."},
        {"fel": "nu_scrie", "text": ARTICOLE[3], "intrebare": "Cine l-a construit?", "raspuns": "Nu scrie în text."},
        {"fel": "text", "text": ARTICOLE[3], "intrebare": "Cine l-a proiectat?", "raspuns": "Un inginer chinez."}]),
        encoding="utf-8")
    val = e3.cmd_validare(lucru, v3)
    assert val["intrebari"] == 2 and val["aleasa"] in e3.VARIANTE
    assert val["variante"][val["aleasa"]]["k5"]["bune"] == 2

    ex = e3.cmd_examene(lucru, examene)
    assert ex["intrebari"] == 4 and ex["total"]["i_cautare"]["k5"]["bune"] == 3
    assert ex["raspuns_in_textul_examenului"] == 3 and ex["total_raspuns_in_text"]["i_cautare"]["k5"]["bune"] == 3
    assert ex["total"]["ii_articol_la_5"]["bune"] == 4 and ex["greseli_la_5"] == 1
    assert ex["pe_examen"]["noaptea10_text"]["intrebari"] == 1
    with pytest.raises(SystemExit):
        e3.cmd_examene(lucru, examene)  # o singură rulare

    # S25: paginile-listă, validarea pe două eșantioane, rularea unică pe examene
    liste = e3.cmd_liste(_wikipedia(tmp_path), lucru)
    assert liste["articole"] == 4 and liste["fraze_lista"] == [] and liste["randuri_scurte"] == []
    val = e3.cmd_validare_s25(lucru, v3)
    assert val["intrebari"] == {"s1024": 2, "s2048": 0} and val["comune_intre_esantioane"] == 0
    assert val["aleasa"] in e3.VARIANTE_S25 and val["varianta_s24_reprodusa_pe_1024"]
    assert set(val["variante"]) == {e3.VARIANTA_S24, *e3.VARIANTE_S25}
    ex = e3.cmd_examene_s25(lucru, examene)
    assert ex["intrebari"] == 4 and ex["varianta_s24_reprodusa"]
    assert ex["rulari"]["s24"]["s16"]["total"]["i_cautare"]["k5"]["bune"] == 3
    # „În Elveția.” rămâne nepotrivit și cu numărul gol (nu e număr): aceleași cifre în ambele potriviri
    assert ex["rulari"]["s24"]["numar"]["total"]["i_cautare"]["k5"]["bune"] == 3
    assert ex["schimbari_fata_de_s24"]["s16"]["greseli_s24_la_5"] == 1
    with pytest.raises(SystemExit):
        e3.cmd_examene_s25(lucru, examene)  # o singură rulare


def test_examenul_nou_s26(tmp_path, monkeypatch):
    bistrita = "Râul Bistrița este un râu din România. Izvorăște din Munții Rodnei."
    turda = "Turda este un municipiu în județul Cluj, România. Are o salină veche."
    wiki = tmp_path / "wiki.txt"
    wiki.write_text("<|endoftext|>".join(ARTICOLE + [bistrita, turda]), encoding="utf-8")
    lucru = tmp_path / "e3"
    examene = _examene(tmp_path)
    e3.cmd_index(wiki, lucru, examene)
    e3.cmd_adauga(lucru)
    v3 = tmp_path / "v3.jsonl"
    v3.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in [
        {"fel": "text", "grup": "g0", "text": ARTICOLE[0], "intrebare": "În ce raion se află Bilca?",
         "raspuns": "În raionul Hliboca."},
        {"fel": "text", "grup": "g3", "text": ARTICOLE[3], "intrebare": "Peste ce râu e Podul Pupin?",
         "raspuns": "Peste Dunăre."},
        {"fel": "text", "grup": "g9", "text": "Podul Pupin este un pod peste Dunăre, la Belgrad, în Serbia.",
         "intrebare": "În ce oraș e Podul Pupin?", "raspuns": "La Belgrad."},  # alt grup, același articol (w3)
        {"fel": "text", "grup": "g0", "text": ARTICOLE[0], "intrebare": "Ce are Bilca?",
         "raspuns": "O biserică veche din lemn."},  # același grup ca o întrebare de validare
        {"fel": "text", "grup": "g7", "text": "Peştera Mondmilchloch este situată pe Muntele Pilat din Elveția.",
         "intrebare": "Pe ce munte e Peștera Mondmilchloch?", "raspuns": "Pe Muntele Pilat."},  # textul unui examen
        {"fel": "text", "grup": "g4", "text": bistrita, "intrebare": "Din ce munți izvorăște râul Bistrița?",
         "raspuns": "Din Munții Rodnei."},
        {"fel": "text", "grup": "g5", "text": turda, "intrebare": "În ce județ e Turda?", "raspuns": "În județul Cluj."},
    ]), encoding="utf-8")
    bune = e3.candidate_validare(v3)
    monkeypatch.setattr(e3, "intrebari_validare_s25", lambda cale, cate=500: ([bune[0]], [bune[1]], len(bune)))
    con = e3.deschide(lucru / "index.sqlite")
    assert e3.articole_text(con, bune[2]["text"]) == ["w3"]
    con.close()

    ales = e3.cmd_examen_nou(lucru, v3, examene, cate=10)
    assert ales["intrebari"] == 2 and ales["respinse_pentru_articol_comun"] == 1
    assert ales["articole_wikipedia_distincte"] == 2 and ales["fara_articol_gasit"] == 0
    lista = json.loads((lucru / "examen_nou_4096.json").read_text(encoding="utf-8"))
    assert sorted(q["grup"] for q in lista) == ["g4", "g5"]
    assert sorted(a for q in lista for a in q["articole_corecte"]) == ["w4", "w5"]
    with pytest.raises(SystemExit):
        e3.cmd_examen_nou(lucru, v3, examene)  # listă fixă

    e3.cmd_liste(wiki, lucru)
    e3.cmd_validare(lucru, v3)
    e3.cmd_validare_s25(lucru, v3)
    e3.cmd_examene(lucru, examene)
    e3.cmd_examene_s25(lucru, examene)
    rez = e3.cmd_examen_nou_masoara(lucru, v3)
    assert rez["intrebari"] == 2 and rez["validare_2048_reprodusa_k1_5_20"]
    assert set(rez["rulari"]["aleasa"]["s16"]["total"]["i_cautare"]) == {"k1", "k3", "k5", "k20"}
    assert rez["plafon_e3_k3"]["bune"] == 2 and rez["cifra_oficiala"]["ii_articol_la_5"]["bune"] == 2
    assert set(rez["k3_examene_160_aleasa"]["s16"]) == {"k1", "k3", "k5", "k20"}
    with pytest.raises(SystemExit):
        e3.cmd_examen_nou_masoara(lucru, v3)  # o singură rulare

    # S27: datele de antrenare E3 (un „tokenizer” de cuvinte, ca să nu încarce BPE-ul)
    import module.tokenizer_bpe as tb

    class Cuvinte:
        def codifica(self, text):
            return text.split()

    monkeypatch.setattr(tb.TokenizerBPE, "incarca", staticmethod(lambda cale: Cuvinte()))
    sha = json.loads((lucru / "examen_nou_4096_info.json").read_text(encoding="utf-8"))["sha256"]
    with pytest.raises(SystemExit):
        e3.cmd_date_antrenare(lucru, v3, tmp_path / "tok.json", examene)  # altă amprentă decât cea S26 reală
    info = e3.cmd_date_antrenare(lucru, v3, tmp_path / "tok.json", examene, sha_examen_nou=sha)
    assert info["candidate_in_text_v3"] == 7
    assert info["scoase"] == {"grup": 3, "text": 1, "vechi_oprite": 3}  # g3 (2048), g4 și g5 (S26); textul unui examen
    assert info["exemple"] == 3 and info["perechi_vechi"] == 4
    exemple = [json.loads(r) for r in (lucru / "date_antrenare_s27.jsonl").read_text(encoding="utf-8").splitlines()]
    oprite = {"w1", "w2", "w4", "w5"} | {t["id"] for t in json.loads(
        (lucru / "texte_examen.json").read_text(encoding="utf-8"))}
    assert all(not set(e["articole"]) & oprite and 1 <= e["bucati"] <= 3 for e in exemple)
    bilca = next(e for e in exemple if e["intrebare"] == "În ce raion se află Bilca?")
    assert bilca["articole"][0] == "w0" and bilca["raspuns_in_bucati"]
    assert bilca["text"] == "\n".join(b["text"] for b in e3.bucati_e3(
        e3.deschide(lucru / "index.sqlite"), bilca["intrebare"], info["varianta"], e3.incarca_liste(lucru), oprite))
    amestec = (lucru / e3.AMESTEC_S27).read_text(encoding="utf-8").splitlines()
    assert len(amestec) == 3 + info["perechi_vechi_puse"]
    bucati = [{"text": "unu doi trei"}, {"text": "patru cinci"}]
    assert e3.cate_incap(Cuvinte(), "Ce?", bucati, maxim=100) == 2
    assert e3.cate_incap(Cuvinte(), "Ce?", bucati, maxim=7) == 1  # „Text: unu doi trei Întrebare: Ce? Răspuns:”
    assert e3.cate_incap(Cuvinte(), "Ce?", bucati, maxim=6) == 0
    assert len(e3._repeta([1, 2, 3, 4], 1.5, 0)) == 6


def test_numar_gol_si_potrivirea_noua():
    assert e3.numar_gol("În 1966.") == "1966"
    assert e3.numar_gol("Din 2019.") == "2019"
    assert e3.numar_gol("238.136 de locuitori.") == "238.136"
    assert e3.numar_gol("În Elveția.") is None
    assert e3.numar_gol("În sezonul 2019–2020.") is None  # două numere și un cuvânt care nu e de umplutură
    assert e3.contine_numar("1966", "Cindy Crawford (n. 20 februarie 1966) este un fotomodel.")
    assert not e3.contine_numar("1966", "În 19661 sau 1.966 sau 21966.")
    assert e3.contine_numar("238.136", "Are 238 136 de locuitori.")
    assert not e3.contine_numar("238.136", "Are 238.1365 de locuitori.")
    text = "Specia a fost descrisă de Fitzsimons 1930."
    assert not e3.bun("În 1930.", text) and e3.bun("În 1930.", text, "numar")  # S16 nu, numărul gol da
    assert e3.bun("Fitzsimons.", text) and e3.bun("Fitzsimons.", text, "numar")


def test_nume_proprii_si_interogarile_s25():
    assert e3.nume_proprii("Ce populație are Comitatul Washington?") == (["comitatul", "washington"],
                                                                         ["comitatul washington"])
    nume, perechi = e3.nume_proprii("În ce an s-a născut Cynthia Ann „Cindy” Crawford?")
    assert nume == ["cynthia", "ann", "cindy", "crawford"] and "ann cindy" in perechi
    assert e3.nume_proprii("Cine a regizat filmul?") == ([], [])  # primul cuvânt nu e nume
    baza = e3.interogare("Cine a regizat Trick?", e3.VARIANTA_S24)
    assert baza == '"regizat" OR "trick" OR "regizat trick"'
    assert e3.interogare("Cine a regizat Trick?", "nume_repetate") == baza + ' OR "trick" OR "trick"'
    assert e3.interogare("Cine a regizat Trick?", "nume_obligatorii_liste") == f'"trick" AND ({baza})'
    assert e3.interogare("Cine a regizat filmul?", "nume_obligatorii") == \
        e3.interogare("Cine a regizat filmul?", e3.VARIANTA_S24)
    assert e3.interogare("Cine a regizat Trick?", "liste") == baza
    with pytest.raises(ValueError):
        e3.interogare("Cine?", "nume_ciudate")


def test_paginile_lista_coborate(tmp_path):
    assert e3.fel_lista("Bilca se poate referi la:\n Bilca, Suceava\n Bilca, Cernăuți") == (True, False)
    assert e3.fel_lista("Listă de râuri din România\nRâul A") == (True, False)
    assert e3.fel_lista("Orașe\n" + "\n".join(f"Oraș {i}" for i in range(25))) == (False, True)
    assert e3.fel_lista(ARTICOLE[1]) == (False, False)
    wiki = tmp_path / "wiki.txt"
    wiki.write_text("<|endoftext|>".join(["Bilca se poate referi la:\nBilca, sat în Suceava.\nBilca, sat în Ucraina.",
                                          ARTICOLE[0]]), encoding="utf-8")
    lucru = tmp_path / "e3"
    e3.cmd_index(wiki, lucru, _examene(tmp_path))
    assert e3.cmd_liste(wiki, lucru)["fraze_lista"] == ["w0"]
    liste = e3.incarca_liste(lucru)
    con = e3.deschide(lucru / "index.sqlite")
    simplu = e3.cauta(con, "Unde se află Bilca?", e3.VARIANTA_S24)
    coborat = e3.cauta(con, "Unde se află Bilca?", "liste", liste=liste)
    assert simplu[0]["articol"] == "w0" and coborat[0]["articol"] == "w1"
    assert sorted(g["rowid"] for g in simplu) == sorted(g["rowid"] for g in coborat)  # aceleași bucăți, altă ordine
    with pytest.raises(ValueError):
        e3.cauta(con, "Unde se află Bilca?", "liste")  # fără liste_s25.json
    con.close()
