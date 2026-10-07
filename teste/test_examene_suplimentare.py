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
    # Toate notele 6: media 6, iar cât poate varia ea din întâmplare (eroarea standard a mediei) e 0.
    assert model.dupa_examen({"scor": 3.0}) == {"criterii": {"nota_profesor": 6, "nota_profesor_eroare": 0.0}}


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


def test_antrenarea_lunga_masoara_criteriile_pe_ore(tmp_path, monkeypatch, capsys):
    import json

    from teste.test_bucla_cinstita import fise
    from unelte import antrenare_lunga, examen_fapte

    monkeypatch.chdir(tmp_path)
    comun = ["--pauza", "0", "--racire", "0", "--lungime", "30"]
    sursa = config_mic(tmp_path, "antrenare_lunga_3", model=', cale_stare = "lucru/antrenare_lunga_3/gpt.pt"', spatiu="lot = [4]")
    assert antrenare_lunga.main(["--config", str(sursa), "--ore", "1"] + comun) == 0
    fisa_sursa = [f for f in fise(tmp_path) if f["linie"] == "antrenare_lunga_3" and f.get("model_salvat")][-1]
    assert examen_fapte.main(["--experiment", str(fisa_sursa["id"])]) == 0  # punctul de plecare stă în jurnal
    a_patra = config_mic(tmp_path, "antrenare_lunga_4", spatiu="lot = [4]", model=', cale_stare = '
                         '"lucru/antrenare_lunga_4/gpt.pt", examene_suplimentare = ["fapte"]')
    assert antrenare_lunga.main(["--config", str(a_patra), "--ore", "2", "--porneste-din", str(fisa_sursa["id"])] + comun) == 0

    rezultat = json.loads((tmp_path / "lucru" / "antrenare_lunga_4" / "rezultat.json").read_text(encoding="utf-8"))
    assert rezultat["pornire"]["scor"] == fisa_sursa["scoruri"]["val_bpb"]
    assert isinstance(rezultat["pornire"]["fapte_corecte"], int) and "nota_profesor" not in rezultat["pornire"]
    assert all(isinstance(o["criterii"]["fapte_corecte"], int) for o in rezultat["ore"])  # din dupa_examen, fără [criterii]
    assert set(rezultat["corelatii"]) == {"fapte_corecte", "nota_profesor"} and rezultat["corelatii"]["nota_profesor"] is None
    iesire = capsys.readouterr().out
    assert "(punctul de plecare)" in iesire and "nota prof." in iesire and ", fapte " in iesire


def test_examenul_de_fapte_nou_iese_ca_numere(tmp_path, tokenizer_mic):
    import json

    examen = tmp_path / "examen_nou.json"
    examen.write_text(json.dumps({"intrebari": [
        {"subiect": "birds", "fapt": "Birds have feathers.", "propozitie": "A bird's body is covered with ___.",
         "raspuns": "feathers", "acceptate": ["feathers"]}]}), encoding="utf-8")
    model = _gpt(ModelGPT, tokenizer_mic, examene_suplimentare=["fapte_noi"], examen_fapte_nou=str(examen))
    raspuns = model.dupa_examen({"scor": 3.0})
    assert set(raspuns["criterii"]) == {"fapte_noi", "fapte_noi_cu_sinonime", "fapte_noi_stiute"}
    assert all(isinstance(v, int) and 0 <= v <= 1 for v in raspuns["criterii"].values())


def test_coloana_faptelor_noi_apare_doar_cand_e_masurata():
    from unelte.antrenare_lunga import coloanele, corelatii

    ore = [{"ora": i, "scor": 0.5 - 0.01 * i, "criterii": {"fapte_corecte": 40 + i, "nota_profesor": 4.0}} for i in (1, 2, 3)]
    assert [c[0] for c in coloanele(ore, None)] == ["fapte_corecte", "nota_profesor"]
    for i, o in enumerate(ore):
        o["criterii"]["fapte_noi"] = 10 + 2 * i
    assert [c[0] for c in coloanele(ore, None)] == ["fapte_corecte", "fapte_noi", "nota_profesor"]
    assert corelatii(ore, None)["fapte_noi"] == -1.0  # val_bpb scade, faptele noi urcă
