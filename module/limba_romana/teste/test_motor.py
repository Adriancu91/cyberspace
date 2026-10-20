"""Teste de integrare și regresie pe baza completă (se sar dacă baza lipsește).

Setul de propoziții de mai jos e setul de REGRESIE al motorului: propoziții corecte (fără probleme așteptate) și
propoziții cu greșeli (cu tipul problemei și sugestia așteptată). E separat de corpusul UD folosit la dezvoltare
(propozițiile sunt scrise de mână).
"""

import json

import pytest

from .. import VERSIUNE
from ..motor import VERSIUNE_API, Motor

CORECTE = [
    "Copiii frumoși au plecat la școală.",
    "Fata citește o carte veche în grădina bunicii.",
    "Cartea elevului este pe masă.",
    "O carte a elevului este pe masă.",
    "Doi băieți și două fete au venit.",
    "Am cumpărat douăzeci de mere și trei pere.",
    "Maria și Ion merg la piață.",
    "Nu știu dacă vine mâine.",
    "L-am văzut pe Ion în parc.",
    "Cartea a fost citită de toți elevii.",
    "Acești copii sunt cuminți.",
    "Datorită lui, am reușit.",
    "Mi-a spus că va veni.",
    "O să vină mâine.",
    "Copilul este obosit.",
    "În ciuda ploii, meciul a continuat.",
]
GRESITE = [
    ("Copii frumoasă a plecat.", "acord_subst_adj", "frumoși"),
    ("Eu merge acasă.", "acord_subiect_predicat", "merg"),
    ("Băieții a plecat.", "acord_subiect_predicat", "au"),
    ("Cărțile al elevului sunt bune.", "acord_al", "ale"),
    ("Am cumpărat 25 mere.", "numeral_de", "25 de mere"),
    ("Am cumpărat 3 de pere.", "numeral_de", "3 pere"),
    ("Acest fată este frumoasă.", "acord_subst_det", "această"),
    ("Doi fete au venit.", "acord_numeral", "două"),
    ("Maria și Ion merge la piață.", "acord_subiect_predicat", "merg"),
]


@pytest.fixture(scope="module")
def m(motor_complet: Motor) -> Motor:
    return motor_complet


def test_api_compatibila(m: Motor):
    """Contractul API versiunea 1: numele funcțiilor și forma rezultatelor."""
    assert VERSIUNE_API == 1
    for nume in ("cauta_forma", "cauta_lema", "forme_lema", "analiza_morfologica", "analizeaza", "verifica_text", "verifica_acord", "necunoscute",
                 "explica", "sensuri", "relatii", "lant_hiperonime", "concept", "reguli", "exemple", "statistici", "integritate", "exporta", "acoperire", "surse"):
        assert callable(getattr(m, nume)), nume
    rez = m.analizeaza("Copiii frumoși au plecat la școală.")
    assert rez["versiune_motor"] == VERSIUNE and rez["versiune_api"] == 1
    assert {"text", "baza", "propozitii", "probleme"} <= set(rez)
    p = rez["propozitii"][0]
    assert {"cuvinte", "grupuri", "probleme", "analize_alternative", "sensuri", "roluri", "ambiguitati", "necunoscute"} <= set(p)
    c = p["cuvinte"][0]
    assert {"idx", "text", "candidati", "ales", "ambiguu", "cap", "rel"} <= set(c)
    assert {"forma", "lema", "lexem_id", "pos", "trasaturi", "incredere", "statut", "scor", "motive", "dovezi"} <= set(c["candidati"][0])
    json.dumps(rez, ensure_ascii=False)  # serializabil


def test_determinism(m: Motor):
    a = m.analizeaza("Copiii frumoși au plecat la școală, iar fetele au rămas acasă.")
    b = m.analizeaza("Copiii frumoși au plecat la școală, iar fetele au rămas acasă.")
    assert json.dumps(a, sort_keys=True, ensure_ascii=False) == json.dumps(b, sort_keys=True, ensure_ascii=False)


@pytest.mark.parametrize("text", CORECTE)
def test_propozitii_corecte_fara_alarme(m: Motor, text: str):
    rez = m.verifica_text(text)
    acord = [p for p in rez["probleme"] if p["tip"].startswith("acord") or p["tip"] in ("numeral_de", "regim_prepozitie")]
    assert acord == [], acord
    assert rez["necunoscute"] == []


@pytest.mark.parametrize("text,tip,sugestie", GRESITE)
def test_propozitii_gresite_detectate(m: Motor, text: str, tip: str, sugestie: str):
    rez = m.verifica_text(text)
    gasite = [p for p in rez["probleme"] if p["tip"] == tip]
    assert gasite, rez["probleme"]
    assert any(p["sugestie"] == sugestie for p in gasite), gasite


def test_necunoscute_si_ipoteze(m: Motor):
    rez = m.verifica_text("Fata a mâncat un xyzabcul.")
    assert any(n["text"] == "xyzabcul" for n in rez["necunoscute"])
    an = m.analiza_morfologica("xyzabcul")
    assert any(a["incredere"] == "necunoscut" for a in an)
    assert any(a["trasaturi"].get("Definite") == "Def" for a in an)  # ipoteză din terminația -ul


def test_lexicon_si_forme(m: Motor):
    assert any(r["lema"] == "casă" and r["pos"] == "NOUN" for r in m.cauta_forma("casei"))
    forme = m.forme_lema("casă", "NOUN")
    assert forme and {f["forma"] for f in forme[0]["forme"]} >= {"casă", "casa", "case", "casei", "casele", "caselor"}
    statute = {f["forma"]: f["statut"] for f in forme[0]["forme"]}
    assert statute["casei"] == "validat"
    assert m.cauta_lema("bancă", "NOUN")[0]["omonim"] >= 1


def test_fara_diacritice(m: Motor):
    an = m.analiza_morfologica("masina")
    assert any(a["lema"] == "mașină" and a["incredere"] == "fara_diacritice" for a in an)


def test_ambiguitate_pastrata(m: Motor):
    rez = m.analizeaza("Vine mama.")
    p = rez["propozitii"][0]
    c = [x for x in p["cuvinte"] if x["text"] == "Vine"][0]
    assert len(c["candidati"]) >= 2  # verb (a veni) și substantiv (vină, plural)
    assert c["candidati"][c["ales"]]["pos"] == "VERB"


def test_sensuri_si_relatii(m: Motor):
    s = m.sensuri("carte", "NOUN")
    assert s and any(x["sursa"] == "rown" for x in s[0]["sensuri"])
    sens = next(x for x in s[0]["sensuri"] if x["sursa"] == "rown")
    assert sens["limba_definitiei"] == "ro" and sens["definitie"]
    lant = m.lant_hiperonime(sens["concept_id"])
    assert len(lant) >= 2
    rel = m.relatii(sens["concept_id"])
    assert "hypernym" in rel


def test_roluri_semantice(m: Motor):
    rez = m.analizeaza("Băiatul taie pâinea cu cuțitul.")
    roluri = {r["text"]: r["rol"] for r in rez["propozitii"][0]["roluri"]}
    assert roluri.get("Băiatul") == "Agent"
    assert roluri.get("cuțitul", "").startswith("Instrument")


def test_explica(m: Motor):
    e = m.explica("Am văzut o fată.", 3)
    assert e["cuvant"] == "o" and e["ales"]["pos"] == "DET"
    assert any("o_ambiguu" in mot for mot in e["ales"]["motive"])


def test_integritate_baza_completa(m: Motor):
    rap = m.integritate()
    assert rap["ok"], {k: v for k, v in rap["verificari"].items() if v["probleme"]}
