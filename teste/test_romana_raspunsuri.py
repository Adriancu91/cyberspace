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


def test_numar_intreg_cu_despartitor_de_mii():
    """S76c: „1,091” și „1.091” se citesc întregi (1091), ca „1091”; numerele zecimale nu sunt întregi."""
    assert rr.numar_intreg("1,091") == rr.numar_intreg("1.091") == rr.numar_intreg("1091") == 1091
    assert rr.numar_intreg("3.671.032") == 3671032 and rr.numar_intreg("122,000.") == 122000
    assert rr.numar_intreg("2,5") is None and rr.numar_intreg("492,04") is None and rr.numar_intreg("abc") is None
    assert rr.numere("Are 1,091 de locuitori (în 2011).") == [1091, 2011]
    assert rr.cu_puncte(122000) == "122.000" and rr.cu_puncte(984) == "984"


def test_repara_numar_cheia_taiata():
    text = "Dunedin este un oraș din Noua Zeelandă. În 2005 avea o populație de 122,000 locuitori."
    p = {"id": "x1", "fel": "instr_numar", "tip": "locuitori", "text": text, "intrebare": "Scrie doar numărul de "
         "locuitori din Dunedin.", "raspuns": "000.", "cheie": ["000"], "subiect": "Dunedin", "prompt": "?"}
    q = rr.repara_numar(p)
    assert q["numar"] == 122000 and q["cheie"] == ["122.000"] and q["raspuns"] == "122.000." and q["reparat"] == "000"
    assert p["cheie"] == ["000"]  # originalul neatins
    assert rr.nota_corect(q, "122,000.") and rr.nota_corect(q, "122.000") and rr.nota_corect(q, "122000 de locuitori.")
    assert not rr.nota_corect(q, "122.") and not rr.nota_corect(q, "000.") and rr.nota_in_tema(q, "122,000")
    bun = dict(p, text="Satul are 1.204 locuitori.", raspuns="1.204.", cheie=["1.204"])
    qb = rr.repara_numar(bun)
    assert qb["numar"] == 1204 and "reparat" not in qb and qb["cheie"] == ["1.204"]
    ns = dict(p, fel="instr_nu_scrie", raspuns=rr.NU_SCRIE, cheie=[rr.NU_SCRIE])
    assert "numar" not in rr.repara_numar(ns)
    re_ = rr.renoteaza_reparat([p, dict(bun, id="x2")], {"x1": "122,000.", "x2": "1204"})
    assert [r["id"] for r in re_["reparate"]] == ["x1"] and re_["toate"]["corect"] == 100.0


def test_reformuleaza_toate_felurile():
    cazuri = {
        "Spune într-o propoziție cine a fost Ion Pop.": "Cine a fost Ion Pop? Explică într-o singură propoziție.",
        "Rezumă textul într-o propoziție.": "Care e ideea textului, pe scurt? O propoziție.",
        "Scrie doar anul în care s-a născut Ion Pop.": "În ce an s-a născut Ion Pop? Doar anul, te rog.",
        "Scrie numele celui care a regizat Filmul X.": "Cine a regizat Filmul X? Dă doar numele.",
        "Scrie numele capitalei pentru Țara Y.": "Care este capitala pentru Țara Y? Dă doar numele.",
        "Scrie doar numărul de locuitori din Lazu.": "Câți locuitori are Lazu? Răspunde numai cu numărul.",
        "Scrie doar suprafața pe care o are Lazu.": "Ce suprafață are Lazu? Doar cifra și unitatea.",
        "Spune în ce județ se află Lazu și din ce țară face parte.": "Lazu — județul și țara?",
        "Răspunde cu da sau nu: Ion Pop a murit în 1943?": "Da sau nu: Ion Pop a murit în 1943?",
    }
    for vechi, nou in cazuri.items():
        q, sablon = rr.reformuleaza(vechi, 0)
        assert q == nou and rr.regula_sablonului(sablon).fullmatch(q)
        assert rr.reformuleaza(vechi, 1)[0] != q  # cel puțin 2 formulări
        assert not rr.regula_sablonului(sablon).fullmatch(vechi)
    assert rr.reformuleaza("Spune în ce raion se află Ciuciuleni și din ce țară face parte.", 0)[0] == \
        "Ciuciuleni — raionul și țara?"
    import pytest

    with pytest.raises(ValueError):
        rr.reformuleaza("Ce este Lazu?", 0)


def test_main_reformulat_pe_set_mic(tmp_path, monkeypatch):
    monkeypatch.setattr(rr, "RADACINA", tmp_path)
    dosar = tmp_path / "d"
    dosar.mkdir()
    intrebari = {"instr_propozitie": "Spune într-o propoziție ce este Lazu.", "instr_rezuma": "Rezumă textul într-o propoziție.",
                 "instr_an": "Scrie doar anul în care a apărut Lazu.", "instr_nume": "Scrie numele celui care a scris Lazu.",
                 "instr_numar": "Scrie doar numărul de locuitori din Lazu.",
                 "instr_judet_tara": "Spune în ce județ se află Lazu și din ce țară face parte.",
                 "instr_da_nu": "Răspunde cu da sau nu: Lazu e un sat?", "instr_nu_scrie": "Scrie doar anul în care a apărut Lazu."}
    ascuns = []
    for fel, intr in intrebari.items():
        for k in range(3):
            p = _p(fel, "1.204." if fel == "instr_numar" else "Da.", ["1.204"] if fel == "instr_numar" else ["Da"],
                   id_=f"x{fel}{k}")
            p.update(intrebare=intr, tip="locuitori" if fel == "instr_numar" else fel)
            ascuns.append(p)
    ascuns.append(_p("text", "Da.", ["Da"], id_="xt"))
    antr = [dict(_p("instr_an", "1968.", ["1968"], id_="a1"), intrebare="Scrie doar anul în care a apărut Filmul Z.")]
    for nume, lista in (("ascuns.jsonl", ascuns), ("antrenare.jsonl", antr)):
        (dosar / nume).write_text("".join(json.dumps(p, ensure_ascii=False) + "\n" for p in lista), encoding="utf-8")
    assert rr.main(["reformulat", "--dosar", "d"]) == 0
    info = json.loads((dosar / "info_reformulat.json").read_text(encoding="utf-8"))
    noi = rr.citeste(dosar / "ascuns_reformulat.jsonl")
    assert len(noi) == 24 and info["s76a_neschimbat"] and info["verificari"]["formulari_noi_gasite_in_antrenare"] == 0
    assert all(v >= 2 for v in info["sabloane_pe_fel"].values())
    assert all(q["prompt"].endswith(f"\nÎntrebare: {q['intrebare']}\nRăspuns:") for q in noi)
    assert {q["id_s76a"] for q in noi} == {p["id"] for p in ascuns if p["fel"] != "text"}
    assert all(q["numar"] == 1204 for q in noi if q["fel"] == "instr_numar")
    assert info["exemple_din_antrenare"][0]["reformulat"] == "În ce an a apărut Filmul Z? Doar anul, te rog."
    import pytest

    with pytest.raises(SystemExit):
        rr.main(["reformulat", "--dosar", "d"])  # nu se face a doua oară


def test_alege_ascuns_o_pereche_pe_articol():
    import random

    cand = [{"a": [{"id": i, "fel": "a"}], "b": [{"id": i, "fel": "b"}]} for i in range(10)]
    alese = rr.alege_ascuns(cand, {"a": 3, "b": 20}, random.Random(0))
    assert len(alese) == 10 and len({p["id"] for p in alese}) == 10
    assert sum(p["fel"] == "a" for p in alese) == 3
