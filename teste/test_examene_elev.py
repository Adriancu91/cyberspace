"""Examenele elevului din afara examenului oficial: examenul de fapte și examenul profesorului (nota pe 20 de povești)."""

from __future__ import annotations

import json
import re

import pytest

from module import profesor_qwen
from module.profesor_qwen import FAPTE, SUBIECTE
from teste.test_bucla_cinstita import config_mic, fise
from unelte import antrenare_lunga, examen_fapte, examen_profesor


def test_intrebarile_acopera_toate_faptele():
    assert set(examen_fapte.INTREBARI) == {subiect for subiect, _ in SUBIECTE}
    for subiect, (inceput, acceptate) in examen_fapte.INTREBARI.items():
        assert re.search(rf"\b{acceptate[0]}\b", FAPTE[subiect], re.IGNORECASE), subiect  # primul răspuns vine din fapt
        assert inceput == inceput.strip() and "___" not in inceput


def test_cele_trei_propozitii():
    assert [examen_fapte.intrebarea(cadru, "Birds have") for cadru in examen_fapte.CADRE] == [
        ("Birds have ___.", "Birds have"),
        ('Mom said, "Birds have ___."', 'Mom said, "Birds have'),
        ("Lily learned that birds have ___.", "Lily learned that birds have"),
    ]
    assert examen_fapte.intrebarea(examen_fapte.CADRE[2], "The Sun is a")[0] == "Lily learned that the Sun is a ___."


def test_ce_e_corect():
    assert examen_fapte.e_corect(" feathers.", ("feathers",)) and examen_fapte.e_corect(" feather", ("feathers",))
    assert examen_fapte.e_corect(" the clouds in the", ("clouds",))  # după „the”
    assert examen_fapte.e_corect(" Earth", ("earth",)) and not examen_fapte.e_corect(" wings", ("feathers",))
    assert not examen_fapte.e_corect("", ("feathers",)) and examen_fapte.raspunsul(" the") == "the"


class _Elev:
    """Un elev care știe doar două fapte."""

    tokenizer = "bpe"

    def completeaza(self, text: str, max_simboluri: int) -> str:
        return " feathers." if text.endswith("irds have") else " milk" if text.endswith("ows give") else " the big"


def test_examineaza_numara_raspunsurile_corecte():
    rezultate = examen_fapte.examineaza(_Elev())
    assert len(rezultate) == 150 and sum(r["corect"] for r in rezultate) == 6  # 2 fapte × 3 propoziții
    assert sum(r["corect_cuvantul_din_fapt"] for r in rezultate) == 6  # răspunsurile lui sunt chiar cuvintele din fapte
    assert {r["subiect"] for r in rezultate if r["corect"]} == {"birds", "cows"}
    assert rezultate[3]["intrebare"] == "Birds have ___." and rezultate[3]["raspuns"] == "feathers"


def test_examenele_pe_un_model_salvat(tmp_path, monkeypatch, capsys):
    pytest.importorskip("torch")
    monkeypatch.chdir(tmp_path)
    cale = config_mic(tmp_path, "antrenare_lunga_3", model=', cale_stare = "lucru/antrenare_lunga_3/gpt.pt"', spatiu="lot = [4]")
    assert antrenare_lunga.main(["--config", str(cale), "--ore", "1", "--pauza", "0", "--racire", "0", "--lungime", "20"]) == 0
    model_id = [f for f in fise(tmp_path) if f.get("model_salvat")][-1]["id"]

    assert examen_fapte.main(["--linie", "antrenare_lunga_3"]) == 0
    rezultat = json.loads(next((tmp_path / "lucru" / "examen_fapte").glob("experiment_*.json")).read_text(encoding="utf-8"))
    assert rezultat["experiment"] == model_id and rezultat["intrebari"] == 150 and len(rezultat["rezultate"]) == 150
    fisa = [f for f in fise(tmp_path) if f["linie"] == "examen_fapte"][-1]
    assert fisa["scoruri"]["intrebari"] == 150 and all(isinstance(v, int) for v in fisa["scoruri"].values())

    monkeypatch.setattr(profesor_qwen.ProfesorQwen, "pregateste", lambda self: None)
    monkeypatch.setattr(profesor_qwen.ProfesorQwen, "_raspunsuri",
                        lambda self, conversatii, max_simboluri, cu_intamplare: ["GRADE: 5\nREASON: Meh."
                                                                                 for _ in conversatii])
    validare = str(tmp_path / "tinystories" / "validare.txt")
    assert examen_profesor.main(["--experiment", str(model_id), "--povesti", "3", "--validare", validare]) == 0
    fisa = [f for f in fise(tmp_path) if f["linie"] == "examen_profesor"][-1]
    assert fisa["scoruri"]["nota_medie"] == 5 and fisa["scoruri"]["povesti"] == 3 and fisa["distributie_note"]["5"] == 3
    assert fisa["module"]["elev"]["experiment"] == model_id
    texte = next((tmp_path / "lucru" / "profesor").glob("examen_experiment_*")) / "povesti.jsonl"
    assert len(texte.read_text(encoding="utf-8").splitlines()) == 3
    assert "Meh." not in json.dumps(fisa)  # în jurnal, doar numere
    iesire = capsys.readouterr().out
    assert "Examenul de fapte" in iesire and "Media notelor: 5" in iesire


def test_sinonimele_se_numara_separat():
    class _Elev2(_Elev):
        def completeaza(self, text: str, max_simboluri: int) -> str:
            return " clean" if text.endswith("keep them") else " the big"

    rezultate = examen_fapte.examineaza(_Elev2())
    assert sum(r["corect"] for r in rezultate) == 3 and sum(r["corect_cuvantul_din_fapt"] for r in rezultate) == 0
