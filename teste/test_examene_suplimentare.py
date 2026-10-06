"""GPT-ul dă criteriile suplimentare ale deciziei (regula 4) prin dupa_examen, cu setarea examene_suplimentare."""

from __future__ import annotations

import pytest

torch = pytest.importorskip("torch")

from kronos.config import citeste_config  # noqa: E402
from kronos.contracte import Propunere  # noqa: E402
from kronos.orchestrator import Orchestrator  # noqa: E402
from module import profesor_qwen  # noqa: E402
from module.model_continuu import ModelGPTContinuu  # noqa: E402
from module.model_gpt import ModelGPT  # noqa: E402
from teste.test_bucla_cinstita import config_mic  # noqa: E402
from teste.test_model_plasa_mare import MIC, TEXT, _Date, tokenizer_mic  # noqa: E402, F401  (tokenizer_mic: fixture)


def _gpt(cls, tokenizer, **setari):
    model = cls(**MIC, tokenizer="bpe", cale_tokenizer=tokenizer, pasi_max=10, **setari)
    model.antreneaza(_Date(TEXT), 30.0)
    return model


def test_fara_examene_suplimentare_gpt_ul_e_ca_inainte():
    assert not hasattr(ModelGPT(**MIC), "dupa_examen")  # fără ușa dupa_examen: fișele lui rămân neschimbate
    with pytest.raises(ValueError, match="examene_suplimentare"):
        ModelGPT(**MIC, examene_suplimentare=["necunoscut"])


def test_faptele_ies_doar_ca_numere(tokenizer_mic):
    raspuns = _gpt(ModelGPT, tokenizer_mic, examene_suplimentare=["fapte"]).dupa_examen({"scor": 3.0})
    assert set(raspuns) == {"criterii"}
    assert set(raspuns["criterii"]) == {"fapte_corecte", "fapte_corecte_cu_sinonime", "fapte_stiute"}
    assert all(isinstance(v, int) and 0 <= v <= 150 for v in raspuns["criterii"].values())


def test_continuu_salveaza_intai_starea_apoi_criteriile(tmp_path, tokenizer_mic, monkeypatch):
    model = _gpt(ModelGPTContinuu, tokenizer_mic, cale_stare=str(tmp_path / "gpt.pt"), examene_suplimentare=["fapte"])
    raspuns = model.dupa_examen({"scor": 3.0})
    assert raspuns["continuare"]["salvat"] and "fapte_corecte" in raspuns["criterii"]
    (tmp_path / "gpt.pt").unlink()

    def crapa():
        raise RuntimeError("examenul suplimentar a căzut")

    monkeypatch.setattr(model, "ruleaza_examene_suplimentare", crapa)
    with pytest.raises(RuntimeError):
        model.dupa_examen({"scor": 3.0})
    assert (tmp_path / "gpt.pt").exists()  # starea s-a salvat înainte: antrenamentul nu se pierde


def test_nota_profesorului_iese_ca_numar(tmp_path, tokenizer_mic, monkeypatch):
    validare = tmp_path / "validare.txt"
    validare.write_text("\n<|endoftext|>\n".join(f"Once upon a time, a cat number {i} ran. It was fun." for i in range(25)),
                        encoding="utf-8")
    monkeypatch.setattr(profesor_qwen.ProfesorQwen, "pregateste", lambda self: None)
    monkeypatch.setattr(profesor_qwen.ProfesorQwen, "_raspunsuri",
                        lambda self, conversatii, max_simboluri, cu_intamplare: ["GRADE: 6\nREASON: Ok." for _ in conversatii])
    model = _gpt(ModelGPT, tokenizer_mic, examene_suplimentare=["profesor"], validare_examene=str(validare))
    assert model.dupa_examen({"scor": 3.0}) == {"criterii": {"nota_profesor": 6}}


def test_prin_kronos_cu_criterii(tmp_path, monkeypatch):
    cale = config_mic(tmp_path, "cu_criterii", model=', examene_suplimentare = ["fapte"]')
    cale.write_text(cale.read_text(encoding="utf-8") + "\n[criterii.fapte_corecte]\nmai_mare_e_mai_bine = true\nprag = 0\n",
                    encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    o = Orchestrator(citeste_config(cale))
    prima = o.experiment(Propunere("punct de plecare"))
    assert prima["decizie"] == "pastrat" and isinstance(prima["criterii"]["fapte_corecte"], int)
    a_doua = o.experiment(Propunere("altă sămânță", {"model": {"samanta": 1}}))
    assert isinstance(a_doua["criterii"]["fapte_corecte"], int)
    if a_doua["decizie"] == "respins" and a_doua["castig"] > o.config.prag_zgomot:  # scorul era mai bun: a pierdut faptele
        assert a_doua["motiv"].startswith("a pierdut fapte_corecte")
