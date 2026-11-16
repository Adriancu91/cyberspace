"""S116 (C-126 A1, 16 nov 2026): generatorul de chat fără text alături, examenul de chat și notarea lui, configurarea 24zch."""

from __future__ import annotations

import json
import random
import tomllib
from pathlib import Path
from types import SimpleNamespace

import pytest

from unelte import conversatie_chat as cc
from unelte import examen_chat as ec

RADACINA = Path(__file__).resolve().parent.parent
EXAMEN = RADACINA / cc.EXAMEN
DEOPARTE = RADACINA / cc.DEOPARTE


def _articol(**k):
    a = {"x": "Valea Mare", "tip": "loc", "verb": "este", "folosit_text": False,
         "prima": "Valea Mare este un sat în județul Alba, România.", "definitie": "Ce este Valea Mare?",
         "text": "Valea Mare este un sat în județul Alba, România. Are 1.204 locuitori."}
    a.update(k)
    return a


def test_fapte_din_articol_au_cheia_in_text_si_cel_putin_3_formulari():
    fapte = {f["tip"]: f for f in cc.fapte_din(_articol())}
    assert {"definitie", "judet", "locuitori"} <= set(fapte)
    assert fapte["definitie"]["cheie"] == "sat" and fapte["definitie"]["categorie"] == "ce_este"
    assert fapte["judet"]["cheie"] == "Alba" and fapte["judet"]["raspuns"] == "Valea Mare se află în județul Alba."
    assert fapte["locuitori"]["cheie"] == "1.204" and fapte["locuitori"]["categorie"] == "cati"
    for f in fapte.values():
        assert len(f["formulari"]) >= 3
        if f["tip"] != "definitie":
            assert cc.norm(f["cheie"]) in cc.norm(_articol()["text"])


def test_fiecare_tip_are_cel_putin_3_formulari_si_o_categorie():
    for tip, formulari in cc.FORMULARI.items():
        assert len(formulari) >= 3, tip
    assert set(cc.RASPUNS) <= set(cc.CATEGORIE)
    assert set(cc.CATEGORIE.values()) == set(cc.EXAMEN_COTE)
    assert sum(cc.EXAMEN_COTE.values()) == 150 and sum(cc.SOCIAL_EXAMEN_COTE.values()) == 50


def test_raspunsul_care_e_deja_in_intrebare_nu_intra():
    a = _articol(x="Comuna Leu", prima="Comuna Leu este o comună în județul Dolj, România.",
                 text="Comuna Leu este o comună în județul Dolj, România, formată din satul Leu.")
    assert all(cc.norm(f["cheie"]) not in cc.norm("Comuna Leu") for f in cc.fapte_din(a) if f["tip"] != "definitie")


def test_formularile_sociale_de_examen_nu_apar_in_generator_si_au_cuvinte_cheie():
    gen = {cc.norm(q) for qs in cc.SOCIAL_INTREBARI.values() for q in qs}
    for c, qs in cc.EXAMEN_SOCIAL.items():
        assert len(qs) >= cc.SOCIAL_EXAMEN_COTE[c]
        assert not {cc.norm(q) for q in qs} & gen, c
        assert cc.CUVINTE_CHEIE[c]
    # fiecare răspuns al generatorului e corect după cuvintele-cheie ale categoriei lui
    for c, rs in cc.SOCIAL_RASPUNSURI.items():
        for r in rs:
            assert any(cc.contine(r, k) for k in cc.CUVINTE_CHEIE[c]), (c, r)


def test_perechile_au_forma_filei_chat_fara_text():
    from module.model_conversatie import intrebarea

    p = cc.perechi_sociale(random.Random(0), ori=1)[0]
    assert "text" not in p and p["prompt"] == intrebarea(p["intrebare"]) and not p["prompt"].startswith("Text:")
    d = cc.perechi_dialog([{"intrebare": "Câți locuitori are X?", "raspuns": "X are 5 locuitori.", "subiect": "X"}],
                          random.Random(0), 3)
    assert {x["tip"] for x in d} == {"salut_fapt", "salut_fapt_multumesc", "fapt_multumesc"}
    assert all("\nRăspuns: " in x["intrebare"] and "\nÎntrebare: " in x["intrebare"] for x in d)


def test_scurgerile_se_scot():
    examen = [{"parte": "a", "intrebare": "Câți locuitori are Satul Nou de Sus?", "raspuns_asteptat": "x",
               "text_sursa": "unu doi trei patru cinci șase șapte opt nouă", "subiect": "Satul Nou de Sus"},
              {"parte": "c", "intrebare": "salut"}]
    perechi = [cc._pereche("chat_fapt", "t", "Câți locuitori are Satul Nou de Sus?", "Mulți."),
               cc._pereche("chat_fapt", "t", "Ce?", "unu doi trei patru cinci șase șapte opt"),
               cc._pereche("chat_social", "salut", "Salut!", "Bună!"),
               cc._pereche("chat_fapt", "t", "Ce este Y?", "Y este un lucru.")]
    bune, scoase = cc.scoate_scurgeri(perechi, examen)
    assert scoase == 2 and [p["intrebare"] for p in bune] == ["Salut!", "Ce este Y?"]  # (c) nu scoate „Salut!”


def test_ori_pentru_jumatate():
    assert cc.ori_pentru_jumatate(100, 500) == 5
    assert cc.ori_pentru_jumatate(1000, 10) == 1


def test_modelul_citeste_perechi_fara_text(tmp_path):
    from module.model_conversatie import ModelGPTConversatie, intrebarea, raspunsul
    from module.tokenizer_bpe import TokenizerBPE

    tok = TokenizerBPE.incarca(RADACINA / "date/ws/bpe_16384.json")
    f = tmp_path / "a.jsonl"
    f.write_text(json.dumps({"intrebare": "Salut!", "raspuns": "Bună!"}, ensure_ascii=False) + "\n"
                 + json.dumps({"intrebare": "Ce?", "raspuns": "Nu.", "text": "Un text."}, ensure_ascii=False) + "\n",
                 encoding="utf-8")
    perechi = ModelGPTConversatie.perechi_codificate(SimpleNamespace(tok=tok, conversatie=str(f)))
    assert perechi[0] == (tok.codifica(intrebarea("Salut!")), tok.codifica(raspunsul("Bună!")))
    assert perechi[1][0] == tok.codifica(intrebarea("Ce?", "Un text."))


# --- examenul scris ------------------------------------------------------------------------------------------------
@pytest.mark.skipif(not EXAMEN.exists(), reason="examenul de chat nu e scris")
def test_examenul_de_chat_scris():
    ex = json.loads(EXAMEN.read_text(encoding="utf-8"))
    perechi = ex["perechi"]
    parti = [p["parte"] for p in perechi]
    assert parti.count("a") == 150 and parti.count("b") == 50 and parti.count("c") == 4
    deoparte = {cc.cheie_subiect(t) for t in json.loads(DEOPARTE.read_text(encoding="utf-8"))["titluri"]}
    a = [p for p in perechi if p["parte"] == "a"]
    assert all(cc.cheie_subiect(p["subiect"]) in deoparte for p in a)
    assert len({p["subiect"] for p in a}) == 150
    assert all(p["tip"] == "definitie" or cc.norm(p["cheie"]) in cc.norm(p["text_sursa"]) for p in a)
    assert ex["cuvinte_cheie"] == cc.CUVINTE_CHEIE
    assert [p["intrebare"] for p in perechi if p["parte"] == "c"] == cc.INFORMATIVE
    assert len({p["id"] for p in perechi}) == len(perechi)


def test_notarea():
    examen = {"cuvinte_cheie": {"salut": ["salut", "buna"], "nu_stiu": ["nu stiu"]},
              "perechi": [{"id": "1", "parte": "a", "categorie": "cati", "cheie": "1.204"},
                          {"id": "2", "parte": "a", "categorie": "ce_este", "cheie": "sat"},
                          {"id": "3", "parte": "b", "categorie": "salut"},
                          {"id": "4", "parte": "b", "categorie": "nu_stiu"},
                          {"id": "5", "parte": "c", "categorie": "informativ"}]}
    nota = ec.noteaza(examen, {"1": "Are 1204 de locuitori.", "2": "Satul e frumos.", "3": "Bună ziua!",
                               "4": "Nu știu asta.", "5": "orice"})
    assert (nota["a"], nota["b"], nota["total"], nota["total_din"]) == (1, 2, 3, 4)
    assert nota["pe_categorie"]["a_ce_este"] == "0/1"  # „satul” ≠ „sat”: cuvinte întregi
    assert ec.taie("Bună!<|endoftext|>Întrebare") == "Bună!" and ec.taie("Da.\nÎntrebare: x") == "Da."


def test_examen_chat_refuza_sa_scrie_peste(tmp_path):
    f = tmp_path / "e.json"
    f.write_text("{}", encoding="utf-8")
    with pytest.raises(SystemExit):
        ec.main(["--experiment", "1", "--iesire", str(f)])


# --- configurarea S117 -----------------------------------------------------------------------------------------------
def _config(nume: str) -> dict:
    return tomllib.loads((RADACINA / "config" / nume).read_text(encoding="utf-8"))


def test_24zch_difera_de_24zc_doar_prin_ce_cere_sarcina():
    c, h = _config("conv_w2_mare_24zc.toml"), _config("conv_w2_mare_24zch.toml")
    sc, sh = c["porturi"]["model"]["setari"], h["porturi"]["model"]["setari"]
    assert {k for k in sc.keys() | sh.keys() if sc.get(k) != sh.get(k)} == {"cale_stare", "conversatie",
                                                                            "durata_scaderii_secunde"}
    assert sh["cale_stare"] == "lucru/w2_mare_24zch/gpt.pt"
    assert sh["conversatie"] == "lucru/conversatie_chat/antrenare.jsonl"
    assert sh["durata_scaderii_secunde"] == 14400
    assert sh["optimizator"] == "adamw" and sh["rata_invatare"] == 0.00001
    assert sh["fractie_conversatie"] == 0.45 and sh["fractie_hrana"] == 0.30 and sh["lot"] == 6
    assert sh["adunare_loturi"] == 16
    assert h["platforma"]["nume"] == "w2_mare_24zch"
    cp, hp = dict(c["platforma"]), dict(h["platforma"])
    cp.pop("nume"), hp.pop("nume")
    assert cp == hp and c["paznic"] == h["paznic"]
    for port in c["porturi"]:
        if port != "model":
            assert c["porturi"][port] == h["porturi"][port], port
    assert c["porturi"]["model"]["modul"] == h["porturi"]["model"]["modul"]
