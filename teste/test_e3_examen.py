"""E3 cu antrenare, examenele S27 (26 octombrie 2026): căutarea pentru ambele modele, bucățile care încap, nota S16,
regresia și verdictul după pragurile pre-înregistrării (pe un Wikipedia mic, inventat, cu un „model” fals)."""

import json

import pytest

from unelte import e3_examen as ex
from unelte import e3_memorie as e3

from teste.test_e3_memorie import ARTICOLE, _examene


class Cuvinte:
    def codifica(self, text):
        return text.split()


def _lucru(tmp_path, monkeypatch):
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
        {"fel": "text", "grup": "g4", "text": bistrita, "intrebare": "Din ce munți izvorăște râul Bistrița?",
         "raspuns": "Din Munții Rodnei."},
        {"fel": "text", "grup": "g5", "text": turda, "intrebare": "În ce județ e Turda?", "raspuns": "În județul Cluj."},
    ]), encoding="utf-8")
    bune = e3.candidate_validare(v3)
    monkeypatch.setattr(e3, "intrebari_validare_s25", lambda cale, cate=500: ([bune[0]], [bune[1]], len(bune)))
    e3.cmd_examen_nou(lucru, v3, examene, cate=10)
    e3.cmd_liste(wiki, lucru)
    e3.cmd_validare(lucru, v3)
    e3.cmd_validare_s25(lucru, v3)
    e3.cmd_examene(lucru, examene)
    e3.cmd_examene_s25(lucru, examene)
    e3.cmd_examen_nou_masoara(lucru, v3)
    import module.tokenizer_bpe as tb
    monkeypatch.setattr(tb.TokenizerBPE, "incarca", staticmethod(lambda cale: Cuvinte()))
    return lucru, examene


def _raspunde(model, prompt):
    """Modelul „nou” spune prima propoziție a textului dat; „baza” spune mereu „Nu scrie în text.”."""
    if model == "baza" or not prompt.startswith("Text: "):
        return "Nu scrie în text."
    return prompt[len("Text: "):].split("\n")[0]


def _examene_text(experiment):
    n10 = {"text": 50, "nu_scrie": 20} if experiment == 415 else {"text": 49, "nu_scrie": 18}
    return {"S15": {"intrebari": {"b2": 50, "e": 30}, "corecte": {"b2": 6, "e": 30}},
            "S4": {"intrebari": {"a": 15, "b": 15, "c": 15, "d": 15}, "corecte": {"a": 11, "b": 2, "c": 13, "d": 12}},
            "noaptea10": {"intrebari": {"text": 50, "nu_scrie": 20, "conversatie": 10}, "corecte": n10}}


def test_examenul_s27(tmp_path, monkeypatch):
    lucru, examene = _lucru(tmp_path, monkeypatch)
    sha = json.loads((lucru / "examen_nou_4096_info.json").read_text(encoding="utf-8"))["sha256"]
    incarcate = []

    def incarca(exp, linie):
        incarcate.append((exp, linie))
        return ("nou", {"id": 438, "linie": linie}) if linie else ("baza", {"id": exp, "linie": "w2_conv_text_v3"})

    paznic = []
    argumente = dict(examene=examene, incarca=incarca, raspunde=_raspunde, examene_text=_examene_text,
                     paznic=lambda: paznic.append(1))
    with pytest.raises(SystemExit):
        ex.cmd_examen(lucru, tmp_path / "tok.json", **argumente)  # altă amprentă decât cea S26 reală
    info = ex.cmd_examen(lucru, tmp_path / "tok.json", sha_examen_nou=sha, **argumente)
    assert incarcate == [(None, ex.LINIE), (415, None)] and paznic
    nou, baza = info["modele"]["nou"], info["modele"]["baza"]
    assert nou["experiment"] == 438 and baza["experiment"] == 415
    assert nou["a_s26"]["total"] == {"intrebari": 2, "corecte": 2}  # Bistrița și Turda: răspunsul în prima bucată
    assert baza["a_s26"]["total"] == {"intrebari": 2, "corecte": 0}
    assert info["plafon"]["raspuns_in_bucatile_date"] == 2 and info["plafon"]["in_primele_3_la_s26"] == 2
    assert nou["a_s26"]["din_cele_72_la_s26"] == {"intrebari": 2, "corecte": 2}
    assert nou["b_vechi160"]["total"]["intrebari"] == len(e3.intrebari_examen(examene))
    assert set(nou["b_vechi160"]["pe_examen"]) <= {"S15", "S4", "noaptea10"}
    assert nou["c_regresia"]["noaptea10"] == {"intrebari": 70, "corecte": 67}  # fără conversația simplă
    assert baza["c_regresia"]["noaptea10"]["corecte"] == 70 and baza["c_regresia"]["S4"] == {"intrebari": 60,
                                                                                            "corecte": 38}
    assert info["verdict"] == "INFIRMAT"  # 2/100 ≤ 44
    r = nou["raspunsuri"]["a_s26"][0]
    assert "prompt" not in r and r["corect"] and r["bucati_date"] >= 1
    with pytest.raises(SystemExit):
        ex.cmd_examen(lucru, tmp_path / "tok.json", sha_examen_nou=sha, **argumente)  # o singură rulare


def test_verdictul_dupa_prag():
    assert ex.verdict(44, 70, 70, 38, 38) == "INFIRMAT"
    assert ex.verdict(45, 70, 70, 38, 38) == "NECLAR"
    assert ex.verdict(60, 68, 70, 36, 38) == "CONFIRMAT"
    assert ex.verdict(60, 67, 70, 38, 38) == "NECLAR"  # 3 puncte pierdute pe noaptea 10
    assert ex.verdict(75, 70, 70, 35, 38) == "NECLAR"  # 3 puncte pierdute pe S4
