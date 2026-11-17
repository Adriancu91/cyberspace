"""S118 pasul 3: bucla care învață din lecțiile din conversații (unelte/invata_din_conversatii.py)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from unelte import invata_din_conversatii as idc

RADACINA = Path(__file__).resolve().parent.parent


def test_modelul_din_interfata_si_schimbarea_lui_pe_scriptul_real():
    text = (RADACINA / idc.INTERFATA_PS1).read_text(encoding="utf-8")
    config, exp, exp_text = idc.modelul_din_interfata(text)
    assert config.startswith("config/") and exp > 0 and exp_text > 0
    nou = idc.schimba_interfata(text, "lucru/invatare_conversatii/x/config_w2_lectii_x.toml", 999, "nota de proba")
    assert idc.modelul_din_interfata(nou) == ("lucru/invatare_conversatii/x/config_w2_lectii_x.toml", 999, 999)
    assert "# nota de proba\nparam(" in nou
    # restul scriptului neschimbat
    assert nou.replace("# nota de proba\n", "").count("\n") == text.count("\n")


def test_config_noua_schimba_doar_ce_trebuie():
    baza = (RADACINA / idc.CONFIG_BAZA).read_text(encoding="utf-8")
    nou = idc.config_noua(baza, "w2_lectii_t", "lucru/invatare_conversatii/t/antrenare.jsonl", 3600, "S118: proba")
    linii_baza, linii_nou = baza.splitlines(), nou.splitlines()[3:]
    diferite = [(a, b) for a, b in zip(linii_baza, linii_nou) if a != b]
    assert len(linii_baza) == len(linii_nou)
    assert len(diferite) == 3  # nume, linia cu setările modelului (cale_stare, conversatie, durata), eticheta
    setari = next(b for a, b in diferite if "cale_stare" in b)
    assert 'cale_stare = "lucru/w2_lectii_t/gpt.pt"' in setari
    assert 'conversatie = "lucru/invatare_conversatii/t/antrenare.jsonl"' in setari
    assert "durata_scaderii_secunde = 3600" in setari and "rata_invatare = 0.00001" in setari
    assert 'optimizator = "adamw"' in setari and "fractie_conversatie = 0.45" in setari


def test_repetari_cel_mult_3_si_cel_mult_5_la_suta():
    assert idc.repetari_lectii(0, 1000) == 0
    assert idc.repetari_lectii(10, 100_000) == 3
    assert idc.repetari_lectii(1000, 50_000) == 2     # 3 × 1000 = 5,66 % (peste 5); 2 × 1000 = 3,85 %
    assert idc.repetari_lectii(10_000, 1000) == 1      # oricât de multe, tot o dată


def test_amestecul_pastreaza_baza_si_adauga_lectiile(tmp_path):
    baza = tmp_path / "baza.jsonl"
    baza.write_text("".join(json.dumps({"prompt": f"Întrebare: {i}?\nRăspuns:", "raspuns": str(i)}) + "\n"
                            for i in range(1000)), encoding="utf-8")
    lectii = [{"fel": "lectie_chat", "tip": "corectat", "prompt": "Întrebare: Cine ești?\nRăspuns:",
               "intrebare": "Cine ești?", "raspuns": "Sunt Kronos.", "id": "lectie_ab"}]
    info = idc.scrie_amestecul(baza, lectii, tmp_path / "out" / "a.jsonl")
    randuri = (tmp_path / "out" / "a.jsonl").read_text(encoding="utf-8").splitlines()
    assert info == {"randuri_baza": 1000, "lectii": 1, "repetari": 3, "randuri_lectii": 3,
                    "procent_lectii": round(300 / 1003, 3)}
    assert randuri[:1000] == baza.read_text(encoding="utf-8").splitlines()
    assert [json.loads(r)["raspuns"] for r in randuri[1000:]] == ["Sunt Kronos."] * 3
    assert all("tip" not in json.loads(r) for r in randuri[1000:])


def _conditii(**nou):
    vechi = {"romana": 1.10, "corecte": 228, "r1": 98.0, "chat": 25, "lectii": 4}
    return vechi, {**vechi, **nou}


def test_verdictul_strict():
    assert idc.verdict(*_conditii())["trece"]
    assert idc.verdict(*_conditii(romana=1.11, corecte=218, chat=20, r1=90.0))["trece"]  # exact la praguri
    for schimbare, cheie in [({"romana": 1.1101}, "romana_curat"), ({"corecte": 217}, "corecte_profesor"),
                             ({"r1": 89.9}, "R1_instructiuni"), ({"r1": None}, "R1_instructiuni"),
                             ({"chat": 19}, "chat_a_b"), ({"lectii": 3}, "lectii_deoparte")]:
        v = idc.verdict(*_conditii(**schimbare))
        assert not v["trece"] and v["pica"] == [cheie] and v["verdict"] == "rămâne modelul din interfață"


def test_rularea_se_opreste_fara_lectii_si_nu_antreneaza(tmp_path, monkeypatch):
    pasi: list[str] = []
    dosar_lectii = tmp_path / "lectii"
    dosar_lectii.mkdir()
    (dosar_lectii / "info.json").write_text(json.dumps({"lectii": 0, "antrenare": 0, "deoparte": 0}), encoding="utf-8")
    (dosar_lectii / "lectii.jsonl").write_text("", encoding="utf-8")
    rulare = idc.Rulare(tmp_path / "r", executa=lambda nume, comanda: pasi.append(nume) or 0)
    rez = idc.pregateste("t", tmp_path / "r", dosar_lectii=dosar_lectii, rulare=rulare)
    assert rez["prea_putine"] and pasi == ["lectii_din_conversatii"]
    assert not (tmp_path / "r" / "antrenare.jsonl").exists()
    with pytest.raises(SystemExit):
        idc.Rulare(tmp_path / "r2", executa=lambda n, c: 1).pas("x", ["x"])
    assert "codul 1" in json.loads((tmp_path / "r2" / "jurnal.json").read_text(encoding="utf-8"))["oprit"]


def test_lectiile_deoparte_notate_cu_un_model_mic_pe_procesor(tmp_path):
    pytest.importorskip("torch")
    from module.model_conversatie import ModelGPTConversatie
    from module.tokenizer_bpe import antreneaza_bpe

    text = ("Once upon a time there was a dog. " * 200) + "<|endoftext|>"
    perechi = [{"intrebare": f"Ce face cățelul {i}?", "raspuns": "Latră."} for i in range(20)]
    (tmp_path / "conv.jsonl").write_text("\n".join(json.dumps(p) for p in perechi), encoding="utf-8")
    antreneaza_bpe(text + " Întrebare: Răspuns: Ce face cățelul? Latră. Miaună.", 300).salveaza(tmp_path / "bpe.json")

    class Date:
        def text_antrenare(self):
            return text

    model = ModelGPTConversatie(n_straturi=1, n_capete=2, n_emb=32, context=32, lot=20, dispozitiv="cpu",
                                tokenizer="bpe", cale_tokenizer=str(tmp_path / "bpe.json"), rata_invatare=3e-3,
                                pasi_max=60, conversatie=str(tmp_path / "conv.jsonl"), fractie_conversatie=0.8)
    model.antreneaza(Date(), 60.0)
    lectii = [{"id": "lectie_1", "fel": "lectie_chat", "intrebare": "Ce face cățelul 3?", "raspuns": "Latră."},
              {"id": "lectie_2", "fel": "lectie_chat", "intrebare": "Ce face cățelul 5?", "raspuns": "Miaună."}]
    nota = idc.noteaza_lectii(model, lectii, simboluri=3)
    assert nota["din"] == 2 and [r["corect"] for r in nota["raspunsuri"]] == [True, False] and nota["corecte"] == 1
