"""S60: proba de 10 minute de la zero (unelte/proba_muon.py fără --porneste-din) și răspunsurile modelului pentru pass@k
(unelte/kronos_cod/examen_cod.py model + noteaza) — pe procesor, pe config/cod_c1.toml micșorat și pe setul de PROBĂ."""

from __future__ import annotations

import json

import pytest

torch = pytest.importorskip("torch")

from teste.test_model_gpt_cod import config_cod_c1_mic  # noqa: E402
from unelte.kronos_cod import examen_cod as ex  # noqa: E402


@pytest.fixture
def placa_falsa(monkeypatch):
    """nvidia-smi înlocuit: 40 °C, 500 MB (testul nu depinde de placa reală)."""
    from unelte import urmareste_placa

    monkeypatch.setattr(urmareste_placa, "citeste", lambda: (40, 500, 0))


def test_proba_de_la_zero_pe_cod_c1_mic(tmp_path, monkeypatch, placa_falsa):
    from unelte import proba_muon

    monkeypatch.chdir(tmp_path)
    cale = config_cod_c1_mic(tmp_path)
    dosar = tmp_path / "proba"
    assert proba_muon.main(["--config", str(cale), "--minute", "0.03", "--dosar", str(dosar)]) == 0
    rez = json.loads((dosar / "proba.json").read_text(encoding="utf-8"))
    assert rez["porneste_din"] is None and len(rez["rulari"]) == 1
    r = rez["rulari"][0]
    assert r["oprita"] is None and r["pasi"] > 0
    assert r["placa"]["memorie_max_mb"] == 500 and r["placa"]["temperatura_max"] == 40
    assert r["simboluri_pe_secunda"] > 0
    assert r["simboluri_pe_secunda"] == pytest.approx(r["loturi_pe_secunda"] * 8 * 16, rel=0.05)  # lot 8 × context 16
    assert not (tmp_path / "lucru" / "jurnal").exists()  # fără jurnal
    assert not (tmp_path / "lucru" / "cod_c1").exists()  # fără starea liniei
    assert sorted(p.name for p in dosar.iterdir()) == ["proba.json"]  # fără stare de pornire


def test_proba_de_la_zero_se_opreste_peste_memorie(tmp_path, monkeypatch, placa_falsa):
    from unelte import proba_muon

    monkeypatch.chdir(tmp_path)
    cale = config_cod_c1_mic(tmp_path)
    dosar = tmp_path / "proba"
    assert proba_muon.main(["--config", str(cale), "--minute", "0.03", "--memorie-max", "400",
                            "--dosar", str(dosar)]) == 1
    r = json.loads((dosar / "proba.json").read_text(encoding="utf-8"))["rulari"][0]
    assert "500 MB" in r["oprita"]


def test_taie_corp():
    assert ex.taie_corp("    return 1\n\n    x\ndef g():\n    pass\n") == "    return 1\n\n    x\n"
    assert ex.taie_corp("    a = 1\nprint(a)") == "    a = 1\n"
    assert ex.taie_corp("def f") == "" and ex.taie_corp("    return") == "    return"


@pytest.fixture
def model_mic(tmp_path, monkeypatch):
    """Un model cod_c1 micșorat, cu 2 pași (practic neantrenat), salvat în ambele feluri: starea liniei și salveaza."""
    from kronos.config import citeste_config
    from kronos.registru import Registru
    from module.date_cod import DateCod

    monkeypatch.chdir(tmp_path)
    cale = config_cod_c1_mic(tmp_path)
    cfg = citeste_config(cale)
    setari = {**cfg.setari_port("model"), "pasi_max": 2}
    model = Registru().creeaza("model", cfg.porturi["model"]["modul"], setari).instanta
    sd = cfg.setari_port("date")
    model.antreneaza(DateCod(director=sd["director"], context=sd["context"], sfarsit_de_fisier=sd["sfarsit_de_fisier"],
                             cale_tokenizer=sd["cale_tokenizer"]), 600.0)
    model.dupa_examen({"scor": 3.0})
    salvat = model.salveaza(str(tmp_path / "salvat" / "model"))
    return cale, tmp_path / "lucru" / "cod_c1" / "gpt.pt", salvat


def test_model_scrie_10_raspunsuri_aceleasi_la_aceeasi_samanta_si_noteaza_le_primeste(model_mic, tmp_path):
    cale, stare, _ = model_mic
    baza = ["model", "--config", str(cale), "--stare", str(stare), "--set", "proba", "--max-simboluri", "24"]
    assert ex.main(baza + ["--iesire", str(tmp_path / "a.json")]) == 0
    assert ex.main(baza + ["--iesire", str(tmp_path / "b.json")]) == 0
    a = json.loads((tmp_path / "a.json").read_text(encoding="utf-8"))
    b = json.loads((tmp_path / "b.json").read_text(encoding="utf-8"))
    assert a["raspunsuri"] == b["raspunsuri"]
    assert a["meta"]["n"] == 10 and a["meta"]["temperatura"] == 0.8 and a["meta"]["samanta"] == 0
    assert set(a["raspunsuri"]) == {p.id for p in ex.set_proba()}
    assert all(len(v) == 10 for v in a["raspunsuri"].values())
    assert all(ex.taie_corp(c) == c for v in a["raspunsuri"].values() for c in v)
    with pytest.raises(SystemExit, match="există deja"):
        ex.main(baza + ["--iesire", str(tmp_path / "a.json")])
    # modelul aproape neantrenat pune ~toată probabilitatea pe „\n”: sămânța se vede doar la temperatură mare
    for nume, samanta in (("c.json", "0"), ("e.json", "1")):
        assert ex.main(baza + ["--iesire", str(tmp_path / nume), "--samanta", samanta, "--temperatura", "5"]) == 0
    c, e = (json.loads((tmp_path / n).read_text(encoding="utf-8"))["raspunsuri"] for n in ("c.json", "e.json"))
    assert c != e

    # notarea: doar primele 2 probleme (20 de rulări în cutie), drumul cap-coadă; pass@k poate fi 0
    assert ex.main(baza + ["--iesire", str(tmp_path / "d.json"), "--probleme", "2"]) == 0
    assert ex.main(["noteaza", "--raspunsuri", str(tmp_path / "d.json"), "--nota", str(tmp_path / "nota.json")]) == 0
    nota = json.loads((tmp_path / "nota.json").read_text(encoding="utf-8"))
    assert nota["set"] == "proba" and nota["complet"] is False and nota["probleme"] == 2
    assert sum(nota["stari"].values()) == 20 and all(x["n"] == 10 for x in nota["pe_problema"])
    assert 0.0 <= nota["pass@1"] <= nota["pass@10"] <= 1.0
    with pytest.raises(SystemExit, match="există deja"):
        ex.main(["noteaza", "--raspunsuri", str(tmp_path / "d.json"), "--nota", str(tmp_path / "nota.json")])


def test_model_salvat_in_jurnal_da_aceleasi_raspunsuri(model_mic, tmp_path):
    """Același model, încărcat din starea liniei sau din fișierul salveaza → aceleași corpuri."""
    cale, stare, salvat = model_mic
    for nume, s in (("x.json", stare), ("y.json", salvat)):
        assert ex.main(["model", "--config", str(cale), "--stare", str(s), "--set", "proba", "--probleme", "3",
                        "--max-simboluri", "16", "--iesire", str(tmp_path / nume)]) == 0
    x, y = (json.loads((tmp_path / n).read_text(encoding="utf-8"))["raspunsuri"] for n in ("x.json", "y.json"))
    assert x == y and len(x) == 3


def test_setul_ascuns_cere_sha_ul_din_info(tmp_path):
    """Pe un set ascuns FALS (din cel de probă), nu pe cel adevărat: fără SHA-ul potrivit, nu-l folosește."""
    sha = ex.scrie_jsonl(ex.set_proba()[:2], tmp_path / "probleme.jsonl")
    (tmp_path / "info.json").write_text(json.dumps({"sha256": sha}), encoding="utf-8")
    assert [p.id for p in ex.probleme_setului("ascuns", tmp_path)] == [p.id for p in ex.set_proba()[:2]]
    (tmp_path / "info.json").write_text(json.dumps({"sha256": "0" * 64}), encoding="utf-8")
    with pytest.raises(SystemExit, match="SHA-256"):
        ex.probleme_setului("ascuns", tmp_path)
