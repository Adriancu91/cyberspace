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
