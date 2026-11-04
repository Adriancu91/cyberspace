"""S76a: unealta unelte/romana_raspunsuri.py (perechi prin reguli, nota automată, proba notei) — fără date mari, fără placă."""

from __future__ import annotations

import json

from unelte import romana_raspunsuri as rr

CUNOSCUTE = {"se", "află", "în", "județul", "este", "un", "sat", "din", "nu", "scrie", "text", "da", "orașul", "și",
             "comuna", "film", "românesc", "regizat", "de", "locuitori"}

SAT = {"x": "Lazu", "tip": "loc",
       "text": "Lazu este un sat în comuna Agigea din județul Constanța, Dobrogea, România. Are 1.204 locuitori.",
       "prima": "Lazu este un sat în comuna Agigea din județul Constanța, Dobrogea, România.",
       "definitie": "Ce este Lazu?"}
FILM = {"x": "Balul de sâmbătă seara", "tip": "ce",
        "text": "Balul de sâmbătă seara este un film românesc din 1968 regizat de Geo Saizescu. Filmul are o poveste simplă.",
        "prima": "Balul de sâmbătă seara este un film românesc din 1968 regizat de Geo Saizescu.",
        "definitie": "Ce este Balul de sâmbătă seara?"}


def _p(fel: str, raspuns: str, cheie: list[str], subiect: str = "Lazu", id_: str = "x1") -> dict:
    return {"id": id_, "fel": fel, "tip": fel, "prompt": f"Text: {SAT['text']}\nÎntrebare: ?\nRăspuns:", "text": SAT["text"],
            "intrebare": "?", "raspuns": raspuns, "cheie": cheie, "subiect": subiect, "articol": "wikipedia_ro: Lazu"}


def test_norm_si_contine():
    assert rr.norm("Județul Constanța, 1.204 locuitori") == "judetul constanta 1204 locuitori"
    assert rr.contine("Are 1204 de locuitori.", "1.204")
    assert rr.contine("În județul CONSTANTA.", "Constanța")
    assert not rr.contine("Constanța de Sus", "Constanța de Jos")
    assert not rr.contine("12045", "1204")  # cuvinte întregi


def test_valoare_cheie_si_substantiv():
    assert rr.valoare_cheie("În județul Alba.") == "Alba"
    assert rr.valoare_cheie("1.204 locuitori.") == "1.204"
    assert rr.valoare_cheie("În 1950.") == "1950"
    assert rr.valoare_cheie("Pe malul stâng al râului Mureș.") == "Mureș"
    assert rr.substantiv(SAT["prima"]) == "sat"
    assert rr.substantiv("Ion Pop a fost un celebru actor român.") == "actor"
    assert rr.substantiv("Ceva fără verb.") == ""


def test_scurtata():
    assert rr.scurtata("X (n. 1950) este un sat, în comuna Y, din județul Z.") == "X este un sat, în comuna Y, din județul Z."
    lunga = "Lazu este un sat foarte mic, cu case vechi, " + " ".join(["cuvânt"] * 30) + "."
    s = rr.scurtata(lunga)
    assert s is not None and len(s.split()) <= 30 and s.endswith(".")
    assert rr.scurtata("Prea scurt.") is None


def test_instructiuni_din_sat_si_film():
    sat = rr.instructiuni_din(SAT)
    assert sat["instr_judet_tara"][0]["raspuns"] == "Lazu se află în județul Constanța, în România."
    assert sat["instr_judet_tara"][0]["cheie"] == ["Constanța", "România"]
    assert sat["instr_numar"][0]["cheie"] == ["1.204"]
    assert sat["instr_propozitie"][0]["intrebare"] == "Spune într-o propoziție ce este Lazu."
    assert sat["instr_propozitie"][0]["prompt"].startswith("Text: Lazu este") and sat["instr_propozitie"][0][
        "prompt"].endswith("\nÎntrebare: Spune într-o propoziție ce este Lazu.\nRăspuns:")
    film = rr.instructiuni_din(FILM)
    assert film["instr_nume"][0]["intrebare"] == "Scrie numele celui care a regizat Balul de sâmbătă seara."
    assert film["instr_nume"][0]["cheie"] == ["Geo Saizescu"]
    assert film["instr_an"][0]["raspuns"] == "1968."
    assert film["instr_rezuma"][0]["intrebare"] == "Rezumă textul într-o propoziție."
    for fel, lista in {**sat, **film}.items():
        for p in lista:
            assert p["fel"] == fel and 1 <= len(p["cheie"]) <= 3
            assert p["intrebare"].split()[0] in ("Spune", "Scrie", "Rezumă", "Răspunde")


def test_inceputuri_noi():
    assert rr.inceputuri_noi_in(["Scrie doar anul în care s-a născut X.", "Ce este X?", "Spune în ce județ e X"]) == 2


def test_nota_corect_in_tema_limba():
    p = _p("instr_judet_tara", "Lazu se află în județul Constanța, în România.", ["Constanța", "România"])
    assert rr.nota_corect(p, "Lazu se află în județul Constanta, România.")
    assert not rr.nota_corect(p, "Lazu se află în județul Constanța.")  # lipsește țara
    assert rr.nota_in_tema(p, "Lazu e frumos.") and not rr.nota_in_tema(p, "Nu știu nimic.")
    dn = _p("instr_da_nu", "Da.", ["Da"])
    assert rr.nota_corect(dn, "Da, așa este.") and not rr.nota_corect(dn, "Nu.") and not rr.nota_corect(dn, "")
    ns = _p("instr_nu_scrie", rr.NU_SCRIE, [rr.NU_SCRIE])
    assert rr.nota_corect(ns, "Nu scrie in text.") and rr.nota_in_tema(ns, "Nu știu.") and not rr.nota_corect(ns, "Nu știu.")
    an = _p("instr_an", "1968.", ["1968"])
    assert not rr.nota_corect(an, "Nu scrie în text. 1968")  # refuzul nu e răspuns corect
    assert rr.nota_limba(an, "1968.", CUNOSCUTE, set())  # o singură bucată, ca referința
    assert not rr.nota_limba(an, "1968.", CUNOSCUTE, set(), minim=2)
    assert not rr.nota_limba(p, "sat sat sat din Lazu", CUNOSCUTE, set())  # de 3 ori la rând
    assert not rr.nota_limba(p, "Lazu <|endoftext|> sat", CUNOSCUTE, set())
    assert not rr.nota_limba(p, "zzqx qqwz wwqz este sat", CUNOSCUTE, set())  # sub 90 % cunoscute
    assert rr.nota_limba(p, "Lazu se află în județul Constanța.", CUNOSCUTE, set())


def test_noteaza_si_proba_pe_set_mic(monkeypatch):
    perechi = [_p("instr_judet_tara", "Lazu se află în județul Constanța, în România.", ["Constanța", "România"], id_="a"),
               _p("instr_numar", "1.204.", ["1.204"], id_="b"),
               _p("instr_an", "1968.", ["1968"], id_="c"),
               _p("text", "În comuna Agigea.", ["Agigea"], id_="d")]
    n = rr.noteaza(perechi, {"a": "Lazu se află în județul Constanța, în România.\nAlt rând", "b": "1204",
                             "c": "1969.", "d": ""}, CUNOSCUTE, set())
    assert n["toate"]["n"] == 4 and n["toate"]["corect"] == 50.0
    assert n["pe_fel"]["instr_an"]["corect"] == 0.0 and n["note"][0]["raspuns_model"].endswith("România.")
    assert n["scor_R1"] == round((n["toate"]["corect"] + n["toate"]["in_tema"] + n["toate"]["limba_curata"]) / 3, 2)
    assert rr.noteaza(perechi, {"a": "x"}, CUNOSCUTE, set()) == rr.noteaza(perechi, {"a": "x"}, CUNOSCUTE, set())
    monkeypatch.setattr("unelte.ortografie_ro.citeste_lista", lambda: CUNOSCUTE)
    monkeypatch.setattr("unelte.ortografie_ro.citeste_exceptii", lambda: set())
    pr = rr.proba(perechi)
    assert pr["referinte"]["toate"]["corect"] == 100.0 and pr["gol"]["toate"]["corect"] == 0.0
    assert pr["la_fel_de_doua_ori"]


def test_main_noteaza_din_fisiere(tmp_path, monkeypatch):
    monkeypatch.setattr(rr, "RADACINA", tmp_path)
    monkeypatch.setattr("unelte.ortografie_ro.citeste_lista", lambda: CUNOSCUTE)
    monkeypatch.setattr("unelte.ortografie_ro.citeste_exceptii", lambda: set())
    p = _p("instr_an", "1968.", ["1968"], id_="x0")
    (tmp_path / "set.jsonl").write_text(json.dumps(p, ensure_ascii=False) + "\n", encoding="utf-8")
    (tmp_path / "r.json").write_text(json.dumps({"raspunsuri": {"x0": " 1968.<|endoftext|>Text"}}), encoding="utf-8")
    assert rr.main(["noteaza", "--set", "set.jsonl", "--raspunsuri", "r.json", "--iesire", "o/nota.json"]) == 0
    nota = json.loads((tmp_path / "o" / "nota.json").read_text(encoding="utf-8"))
    assert nota["toate"]["corect"] == 100.0 and nota["note"][0]["raspuns_model"] == "1968."


def test_alege_ascuns_o_pereche_pe_articol():
    import random

    cand = [{"a": [{"id": i, "fel": "a"}], "b": [{"id": i, "fel": "b"}]} for i in range(10)]
    alese = rr.alege_ascuns(cand, {"a": 3, "b": 20}, random.Random(0))
    assert len(alese) == 10 and len({p["id"] for p in alese}) == 10
    assert sum(p["fel"] == "a" for p in alese) == 3
