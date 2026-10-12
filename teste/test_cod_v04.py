"""Școala de cod v0.4 (pregătire, fără placă): configurarea, vocabularul cu tokenizer-ul nou și proba de copiere."""

from __future__ import annotations

import random
from pathlib import Path

import pytest

from module.cod import PILOT_V03, PILOT_V04, examen_cod, ordinea, paznic_cod
from module.cod.sandbox import ruleaza_in_proces
from module.cod.examen_cod import CUVINTE_0W
from module.tokenizer_bpe import TokenizerBPE, antreneaza_bpe, antreneaza_din_frecvente, frecvente_bucati
from unelte import proba_copiere_cod, vocabular_cod_ws
from unelte.scoala_cod import citeste_config

RADACINA = Path(__file__).resolve().parent.parent
TOKENIZER_NOU = RADACINA / "../cyberspace/date/ws/bpe_16384.json"
TOKENIZER_VECHI = RADACINA / "../cyberspace/date/tinystories/bpe_4096.json"
TEXT = "".join(proba_copiere_cod.episod(w, "show the word {w}") for w in CUVINTE_0W) * 3


def tokenizer_ws() -> TokenizerBPE:
    """Un tokenizer mic cu regulile „ws”, în care și forma fără spațiu a cuvintelor e învățată."""
    f = frecvente_bucati(TEXT, reguli="ws")
    return antreneaza_din_frecvente({**f, **{b[1:]: n for b, n in f.items() if b[:1] == " " and b[1:].isalpha()}},
                                    256 + 1100 + 700 + 1, reguli="ws")


def test_configurarea_v04_se_citeste_si_foloseste_tokenizer_ul_nou():
    cfg = citeste_config(RADACINA / "config" / "scoala_cod_v04.toml")
    v03 = citeste_config(RADACINA / "config" / "scoala_cod_v03.toml")
    assert cfg["scoala"]["versiune"] == "v0.4" and cfg["scoala"]["dosar"] == "cod_v04"
    assert cfg["povesti"]["tokenizer"].endswith("date/ws/bpe_16384.json")
    assert cfg["paznic"]["memorie_video_max_mb"] == 7000 and cfg["paznic"]["temperatura_max"] == 83
    # aceleași fișiere cu amprentă și aceleași seturi ca v0.3: rezultatele se compară sarcină cu sarcină
    for cheie in ("abecedar", "sacru"):
        assert cfg["scoala"][cheie] == v03["scoala"][cheie]
    assert cfg["examen"] == v03["examen"] and cfg["mediu"] == v03["mediu"] and cfg["pilot"]["linii"] == v03["pilot"]["linii"]
    # singura schimbare în pilot: nivelul nou 0q, înaintea lui 0w (aprobat de Adrian pe 12 octombrie)
    assert cfg["pilot"]["niveluri"] == list(PILOT_V04) and [n for n in PILOT_V04 if n != "0q"] == list(PILOT_V03)


def test_nivelul_0q_arata_cuvantul_intre_ghilimele_iar_0w_ramane_cum_era():
    rng = random.Random(0)
    q = examen_cod.generator("0q")(rng, False)
    cuvant = q.solutie.strip('"')
    assert q.nivel == "0q" and q.text == f'show the word "{cuvant}"' and q.asteptat == ruleaza_in_proces(q.solutie)
    assert cuvant in examen_cod.CUVINTE_0W and q.doar_valoare
    lung = examen_cod.generator("0q")(rng, True)
    assert lung.solutie.strip('"') in examen_cod.CUVINTE_LUNGI_0W
    w = examen_cod.generator("0w")(random.Random(0), False)
    assert w.text.startswith("show the word ") and '"' not in w.text  # nivelul vechi: fără ghilimele în sarcină
    assert ordinea("0n") < ordinea("0w") < ordinea("0q") < ordinea("1a")


def test_la_0q_trece_doar_cuvantul_cerut():
    from module.cod.sandbox import ruleaza

    s = examen_cod._sarcina("0q", 'show the word "moon"', '"moon"', doar_valoare=True)
    for cod, verdict in (('"moon"', "trecut"), ("'moon'", "trecut"), ('print("moon")', "trecut"), ('"sun"', "picat"),
                         ('x = "moon"\nx', "picat"), ("moon", "picat")):
        assert examen_cod.judeca(s, cod, ruleaza(cod, 2.0, ("import",), 2000))[0] == verdict, cod


def test_seturile_lui_0q_sunt_despartite_si_au_ghilimele():
    cfg = citeste_config(RADACINA / "config" / "scoala_cod_v04.toml")
    e = cfg["examen"]
    seturi = examen_cod.seturi("0q", set(), [], e["vazut"], e["nevazut"], e["adversarial"], e["samanta_seturi"])
    texte = seturi.toate_textele()
    assert len(texte["vazut"]) == 60 and len(texte["nevazut"]) == 20 and len(texte["adversarial"]) == 20
    assert not texte["vazut"] & texte["nevazut"] and not texte["nevazut"] & texte["adversarial"]
    assert all(t.startswith('show the word "') and t.endswith('"') for nume in texte for t in texte[nume])


def test_setul_sacru_si_abecedarul_nu_s_au_schimbat_pentru_v04():
    """v0.4 schimbă generatorul de teste (nivelul 0q, aprobat de Adrian); setul sacru, abecedarul și sandbox-ul sunt
    cele din Git."""
    import subprocess

    neschimbate = [cale for nume, cale in paznic_cod.AMPRENTATE.items() if nume != "generatorul de teste"]
    schimbate = subprocess.run(["git", "status", "--porcelain", "--", *neschimbate], cwd=RADACINA,
                               capture_output=True, text=True).stdout.strip()
    assert schimbate == ""


def test_cuvantul_din_raspuns_se_poate_copia_doar_daca_sarcina_il_arata_la_fel():
    tok = tokenizer_ws()
    acum = vocabular_cod_ws.cuvant_in_sarcina_si_raspuns(tok, "moon", "show the word {w}")
    ghilimele = vocabular_cod_ws.cuvant_in_sarcina_si_raspuns(tok, "moon", 'show the word "{w}"')
    assert acum["bucati_cuvant_in_raspuns"] == 1 and ghilimele["bucati_cuvant_in_raspuns"] == 1
    assert acum["se_copiaza"] is False      # în sarcină e „ moon” (cu spațiu), în răspuns „moon”: bucăți diferite
    assert ghilimele["se_copiaza"] is True  # „"moon"” în sarcină și în răspuns: aceleași bucăți
    rezumat = vocabular_cod_ws.cuvintele(tok, CUVINTE_0W)
    assert rezumat["cuvinte"] == len(CUVINTE_0W) and rezumat["se_copiaza_cu_sarcina_de_acum"] == 0
    assert rezumat["se_copiaza_cu_sarcina_cu_ghilimele"] == len(CUVINTE_0W)


def test_numerele_se_copiaza_cu_regulile_noi_dar_nu_toate_cu_cele_vechi():
    nou, vechi = tokenizer_ws(), antreneaza_bpe(TEXT, 400)
    assert vocabular_cod_ws.numerele(nou) == {"0_99_o_bucata": 100, "0_99_se_copiaza": 100, "100_999_o_bucata": 900,
                                              "100_999_se_copiaza": 900}
    assert vocabular_cod_ws.numerele(vechi)["0_99_o_bucata"] < 100


@pytest.mark.skipif(not (TOKENIZER_NOU.exists() and TOKENIZER_VECHI.exists()), reason="tokenizerele adevărate lipsesc")
def test_vocabularul_adevarat_al_scolii_v04():
    cfg = citeste_config(RADACINA / "config" / "scoala_cod_v04.toml")
    r = vocabular_cod_ws.verifica(cfg, TOKENIZER_NOU.resolve(), TOKENIZER_VECHI.resolve(), 512)
    assert r["abecedar"]["nou"]["iese_identic"] and r["abecedar"]["nou"]["simboluri"] < r["abecedar"]["vechi"]["simboluri"]
    scurte = r["cuvinte"]["0w_scurte"]
    assert scurte["nou"]["cuvantul_din_raspuns_o_bucata"] > 0.8 * scurte["nou"]["cuvinte"]
    assert scurte["nou"]["cuvantul_din_raspuns_o_bucata"] > scurte["vechi"]["cuvantul_din_raspuns_o_bucata"]
    assert r["numere"]["nou"]["0_99_se_copiaza"] == 100 and r["numere"]["nou"]["100_999_se_copiaza"] == 900
    for nivel in cfg["pilot"]["niveluri"]:
        assert r["incape"][nivel]["exemple_minime"] == cfg["mediu"]["episoade"]
        assert r["incape"][nivel]["cel_mai_lung_text_cu_raspuns"] <= 512
    # problema veche, exact: la 0w nimic nu se poate copia din sarcină; la 0q și la numere, tot
    assert r["incape"]["0w"]["raspunsul_se_poate_copia_din_sarcina"] == 0
    assert r["incape"]["0q"]["raspunsul_se_poate_copia_din_sarcina"] == r["incape"]["0q"]["sarcini"]
    assert r["incape"]["0n"]["raspunsul_se_poate_copia_din_sarcina"] == r["incape"]["0n"]["sarcini"]
    assert "solutii_care_nu_incap" not in r["incape"]


def test_elevul_merge_cu_un_model_pe_tokenizer_ul_nou(tmp_path):
    """Un model minuscul cu tokenizer cu regulile „ws”, salvat ca la Kronos: elevul școlii îl încarcă, numără și scrie."""
    pytest.importorskip("torch")
    from module.cod.elev import ElevCod
    from module.model_gpt import ModelGPT

    tok = tokenizer_ws()
    tok.salveaza(tmp_path / "ws.json")
    model = ModelGPT(n_straturi=1, n_capete=2, n_emb=32, context=128, tokenizer="bpe", cale_tokenizer=str(tmp_path / "ws.json"),
                     dispozitiv="cpu", samanta=0)
    model.tok = TokenizerBPE.incarca(tmp_path / "ws.json")
    model._construieste()
    cale = model.salveaza(str(tmp_path / "model_w2"))
    elev = ElevCod(cale, "cpu")
    assert elev.context == 128 and elev.model.tok.reguli == "ws" and elev.tokenizer_ca(tmp_path / "ws.json")
    assert elev.numara("show 46") == 3 and elev.numara('"moon"') == 3
    scris = elev.genereaza('TEST: show the word moon\nWRITE:\n', n=2, temperatura=0.0, max_simboluri=5, samanta=0)
    assert len(scris) == 2 and all(isinstance(s, str) for s in scris)
    rezultat = elev.antreneaza(TEXT, pasi=2, rata=1e-4, lot=4, samanta=0)
    assert rezultat["pasi"] == 2
    elev.salveaza(tmp_path / "linie.pt")
    assert ElevCod(tmp_path / "linie.pt", "cpu").model.tok.reguli == "ws"


def test_proba_de_copiere_ruleaza_si_spune_cate_a_nimerit():
    pytest.importorskip("torch")
    r = proba_copiere_cod.incearca(tokenizer_ws(), proba_copiere_cod.SARCINI["cu_ghilimele"], list(CUVINTE_0W[:20]),
                                   {"nevazute": list(CUVINTE_0W[20:24])}, pasi=3, context=64, lot=4)
    assert r["pasi"] == 3 and r["nevazute"]["din"] == 4 and 0 <= r["nevazute"]["corecte"] <= 4
