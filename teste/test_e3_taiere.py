"""S44: bucățile tăiate pe propozițiile utile — tăierea (ordinea, bucata neschimbată, determinismul), regula „câte încap
în 448” pe bucățile tăiate și examenul (o singură rulare, cele văzute de #438 scoase), fără model adevărat, fără placă."""

import json

import pytest

from unelte import e3_memorie as e3
from unelte import e3_reordonare as r
from unelte import e3_taiere as t

from teste.test_e3_citire_reord import c
from teste.test_e3_reordonare import _Tok, _index

BUCATA = ("Brașov este un municipiu din România. Are multe parcuri. Orașul are o cetate veche. "
          "Clima e blândă.\nCetatea a fost ridicată în 1400.")


def test_propozitiile_se_despart_la_semne_si_rand_nou():
    assert t.propozitii(BUCATA) == ["Brașov este un municipiu din România.", "Are multe parcuri.",
                                    "Orașul are o cetate veche.", "Clima e blândă.", "Cetatea a fost ridicată în 1400."]
    assert t.propozitii("Anul 1.400 e vechi. Bine") == ["Anul 1.400 e vechi.", "Bine"]  # punctul din număr rămâne


def test_taierea_pastreaza_prima_si_ordinea():
    taiat = t.taie(BUCATA, "Când a fost ridicată cetatea?")
    # prima propoziție (subiectul) + cele cu „cetate” / „ridicată”, în ordinea din bucată
    assert taiat == ("Brașov este un municipiu din România. Orașul are o cetate veche. "
                     "Cetatea a fost ridicată în 1400.")
    assert len(taiat) < len(BUCATA)


def test_bucata_neschimbata_cand_nu_se_potriveste_nimic():
    assert t.taie(BUCATA, "Cine a scris Luceafărul?") == BUCATA
    assert t.taie("O singură propoziție despre Brașov.", "Ce e Brașov?") == "O singură propoziție despre Brașov."
    toate = "Brașov e mare. Brașov e vechi."
    assert t.taie(toate, "Ce e Brașov?") == toate  # nu se scoate nimic → textul rămâne exact


def test_cuvintele_de_legatura_nu_dau_scor():
    r_ = t.radacini_intrebare("Când a fost ridicată cetatea?")
    assert r.radacina("când") not in r_ and r.radacina("cetatea") in r_
    assert t.scor("Are multe parcuri.", r_) == 0
    assert t.radacini_intrebare("Ce este?")  # doar cuvinte de legătură → toate rămân


def test_taierea_e_determinista():
    q = "Când a fost ridicată cetatea?"
    assert len({t.taie(BUCATA, q) for _ in range(5)}) == 1


def test_cate_incap_numara_bucatile_taiate():
    q = "Când a fost ridicată cetatea?"
    bucati = [{"text": BUCATA}] * 3
    taiate = [{"text": t.taie(b["text"], q)} for b in bucati]
    tok = _Tok()
    from module.model_conversatie import intrebarea
    maxim = len(tok.codifica(intrebarea(q, e3.context_e3(taiate))))  # exact cât iau cele 3 tăiate
    assert e3.cate_incap(tok, q, taiate, maxim=maxim) == 3
    assert e3.cate_incap(tok, q, bucati, maxim=maxim) < 3


def test_examenul_o_singura_rulare(tmp_path):
    lucru = tmp_path / "e3"
    randuri = [("Satele din Brașov sunt mici. Au case vechi. Drumurile sunt bune.", "w2"),
               ("Orașul Brașov are multe străzi. Ploua des. Brașov are o cetate veche din 1400.", "w1"),
               ("Cluj are o universitate mare.", "w3")]
    _index(lucru / "index.sqlite", randuri).close()
    r.cmd_index_radacini(lucru)
    q1 = {"intrebare": "Ce cetate are orașul Brașov?", "raspuns": "o cetate veche", "tip": "definitie", "loc": {}}
    q2 = {"intrebare": "Ce are Cluj?", "raspuns": "o universitate", "tip": "an", "loc": {}}
    (lucru / r.IESIRE_VALIDARE).write_text(json.dumps({"toate": {"s2048": [q1, q2], "s1024": [q2]}},
                                                      ensure_ascii=False), encoding="utf-8")
    (lucru / c.DATE_438).write_text(json.dumps({"intrebare": "Ce are Cluj?"}, ensure_ascii=False) + "\n",
                                    encoding="utf-8")
    (lucru / "validare_s25.json").write_text(json.dumps({"aleasa": "nume_obligatorii_liste"}), encoding="utf-8")
    (lucru / "liste_s25.json").write_text(json.dumps({"fraze_lista": [], "randuri_scurte": []}), encoding="utf-8")

    class Model:
        tok = _Tok()

    paznic, prompturi = [], []

    def raspunde(model, prompt):
        prompturi.append(prompt)
        return prompt[len("Text: "):].split("\n")[0]

    argumente = dict(incarca=lambda exp: (Model(), {"id": exp, "linie": "proba"}), raspunde=raspunde,
                     paznic=lambda: paznic.append(1),
                     judecator=lambda q, texte: [(float("cetate" in x), 1) for x in texte])
    info = t.cmd_examen(lucru, 438, **argumente)
    assert info["intrebari"] == 3 and paznic == [1] and len(prompturi) == 6  # 2 brațe pe întrebare
    assert info["parti"]["s2048_decide"]["intrebari"] == 1  # „Cluj” văzută de #438 → scoasă din decizie
    d = info["parti"]["s2048_decide"]["procent"]
    assert info["diferenta_puncte"] == round(d["taiate"] - d["intregi"], 4)
    assert info["verdict"] in {"CONFIRMAT", "NECLAR", "INFIRMAT"} and info["ordine"] == "rrf_reord"
    rand = info["toate"][0]
    assert rand["taiate"]["bucati_scurtate"] >= 1 and not rand["acelasi_prompt"]
    assert rand["taiate"]["caractere_date"] < rand["intregi"]["caractere_date"]
    assert "Ploua des." in prompturi[0] and "Ploua des." not in prompturi[1]  # aceeași bucată, tăiată
    assert (lucru / t.IESIRE_EXAMEN).exists() and not (lucru / c.IESIRE_EXAMEN_VALIDARE).exists()
    with pytest.raises(SystemExit):
        t.cmd_examen(lucru, 438, **argumente)
