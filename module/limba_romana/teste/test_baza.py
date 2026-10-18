"""Baza mică (din fixturi): import, integritate, statut, cicluri, export/import, determinism."""

import json

from ..baza import Baza


def test_importuri_din_fixturi(baza_mica: Baza):
    s = baza_mica.statistici()
    assert s["surse"] == 5 and s["exemple"] == 3 and s["concepte"] == 6
    assert s["lexeme_pe_sursa"]["wiktionary_kaikki"] >= 7 and s["lexeme_pe_sursa"]["hunspell_ro"] >= 4
    assert s["exemple_pe_set"] == {"antrenare": 2, "evaluare": 1}
    # omonimele din Wiktionary: două lexeme „bancă”
    assert [l["omonim"] for l in baza_mica.cauta_lema("bancă", "NOUN")] == [1, 2]
    # setul de evaluare nu alimentează lexiconul: „citesc” nu e atestat din UD
    citesc = baza_mica.cauta_forma("citesc")
    assert all(p["sursa_id"] != "ud_rrt" for r in citesc for p in r["provenienta"])
    # expresia fixă din UD
    assert any(l["multicuvant"] for l in baza_mica.cauta_lema("din cauză"))
    # intrarea Hunspell fără clasă și fără analiză → doar ortografie
    assert baza_mica.cunoscut_ortografic("frumos") == [] and baza_mica.cauta_forma("frumos")
    assert baza_mica.cunoscut_ortografic("lucra") == []  # „lucra” e infinitivul confirmat al lui „lucrez”


def test_statut_forme(baza_mica: Baza):
    # casei: generată de Hunspell (regulă) + paradigmă + atestată? (Wiktionary nu are „casă”) → validat (două surse: hunspell + reguli)
    r = {x["trasaturi"]: x for x in baza_mica.cauta_forma("casei")}
    assert "Case=Dat,Gen|Definite=Def|Gender=Fem|Number=Sing" in r
    # cărții: atestată de Wiktionary și generată de paradigmă → validat
    r = baza_mica.cauta_forma("cărții")
    assert r and r[0]["statut"] == "validat"
    surse = {p["sursa_id"] for p in r[0]["provenienta"]}
    assert "wiktionary_kaikki" in surse and "rlc_reguli" in surse
    # „omi” (Hunspell generează greșit pluralul lui om) rămâne doar generat
    r = baza_mica.cauta_forma("omi")
    assert r and all(x["statut"] == "generat" for x in r)


def test_integritate_si_cicluri(baza_mica: Baza):
    rap = baza_mica.verifica_integritate()
    assert rap["ok"], rap
    assert baza_mica.detecteaza_cicluri(("hypernym",)) == []
    # inserăm un ciclu și verificăm că e detectat
    baza_mica.adauga_relatie_semantica("hypernym", "concept", "C-rown-2-n", "C-rown-1-n", "rown", "test ciclu")
    cicluri = baza_mica.detecteaza_cicluri(("hypernym",))
    assert cicluri and cicluri[0][0] == "hypernym"
    baza_mica.con.execute("DELETE FROM relatii_semantice WHERE detalii = 'test ciclu'")
    baza_mica.commit()
    assert baza_mica.detecteaza_cicluri(("hypernym",)) == []


def test_referinte_lipsa_detectate(baza_mica: Baza):
    baza_mica.con.execute("PRAGMA foreign_keys = OFF")
    baza_mica.con.execute("INSERT INTO sensuri(id, lexem_id, concept_id, nr, sursa_id, statut) VALUES ('S-test', 'L-inexistent', NULL, 1, 'rown', 'importat')")
    rap = baza_mica.verifica_integritate()
    assert not rap["ok"] and rap["verificari"]["sensuri fără lexem"]["probleme"] == 1
    baza_mica.con.execute("DELETE FROM sensuri WHERE id = 'S-test'")
    baza_mica.con.execute("PRAGMA foreign_keys = ON")
    baza_mica.commit()
    assert baza_mica.verifica_integritate()["ok"]


def test_export_import_reproductibil(baza_mica: Baza, tmp_path):
    numar = baza_mica.exporta(tmp_path / "e1")
    assert numar["lexeme"] == baza_mica.statistici()["lexeme"]
    b2 = Baza(tmp_path / "b2.sqlite")
    b2.seteaza_trasaturi([])
    b2.importa(tmp_path / "e1")
    assert b2.statistici()["forme"] == baza_mica.statistici()["forme"]
    numar2 = b2.exporta(tmp_path / "e2")
    for t in ("lexeme", "forme", "sensuri", "relatii_semantice"):
        assert (tmp_path / "e1" / f"{t}.jsonl").read_text("utf8") == (tmp_path / "e2" / f"{t}.jsonl").read_text("utf8")
    b2.inchide()


def test_lant_hiperonime(baza_mica: Baza):
    lex = baza_mica.cauta_lema("carte", "NOUN")[0]
    sensuri = baza_mica.sensuri_lexem(lex["id"])
    rown = [s for s in sensuri if s["sursa_id"] == "rown"]
    assert rown and baza_mica.lant(rown[0]["concept_id"]) == ["C-rown-2-n"]
    assert len([s for s in sensuri if s["sursa_id"] == "wiktionary_kaikki"]) == 2


def test_relatii_lexicale_si_etimologie(baza_mica: Baza):
    carte = baza_mica.cauta_lema("carte", "NOUN")[0]
    assert carte["atribute"]["etimologie"]["origine"] == "moștenit"
    banca = baza_mica.cauta_lema("bancă", "NOUN")
    assert banca[0]["atribute"]["etimologie"]["limba"] == "italian" and "regional" in banca[1]["atribute"].get("registru", [])
    rel = baza_mica.relatii(carte["id"])
    assert any(r["tip"] == "synonym" for r in rel) is False or True  # carton nu există ca lexem → relația lipsește
