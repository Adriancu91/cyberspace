"""Runda 2 (pornește din plasele rundei 1, pe a doua jumătate a validării) și comparația la timp egal."""

from __future__ import annotations

import json

import pytest

from teste.test_compara_plasa_adaptiva import _configurari
from unelte import compara_plasa_adaptiva, compara_timp_egal, runda2_plasa_adaptiva


def test_runda2_porneste_din_plasele_rundei_1(tmp_path, monkeypatch, capsys):
    pytest.importorskip("torch")
    monkeypatch.chdir(tmp_path)
    argumente = _configurari(tmp_path)
    assert compara_plasa_adaptiva.main(argumente + ["--seminte", "1", "--pasi", "3", "--pauza", "0", "--racire", "0"]) == 0
    runda1 = next((tmp_path / "lucru").glob("comparatie_m3_*.json"))
    plase_r1 = {p.name: p.read_text(encoding="utf-8") for p in (tmp_path / "lucru" / "plase").glob("*.json")}
    assert len(plase_r1) == 2  # plasa veche și cea adaptivă, la sămânța 1

    assert runda2_plasa_adaptiva.main(["--runda1", str(runda1), "--pauza", "0", "--racire", "0"]) == 0

    rezultat = json.loads(next((tmp_path / "lucru").glob("runda2_m3_*.json")).read_text(encoding="utf-8"))
    rand = rezultat["randuri"][0]
    assert rand["samanta"] == 1 and all(rand[v]["r2"]["pasi"] == 3 for v in ("simplu", "adaptiva", "plasa5"))
    assert rand["simplu"]["r1"]["scor"] != rand["simplu"]["r2"]["scor"]  # același model, altă jumătate de validare
    # Câștigul primit de plasa adaptivă e cât a bătut-o pe GPT-ul simplu, pe aceeași jumătate.
    assert rand["adaptiva"]["r2"]["castig_primit"] == pytest.approx(rand["simplu"]["r2"]["scor"] - rand["adaptiva"]["r2"]["scor"])
    # Plasele din runda 1 au rămas neatinse; runda 2 a lucrat pe copii, care au acum încă un experiment.
    assert {p.name: p.read_text(encoding="utf-8") for p in (tmp_path / "lucru" / "plase").glob("m3_2*.json")} == plase_r1
    copii = sorted((tmp_path / "lucru" / "plase").glob("m3_runda2_*.json"))
    assert len(copii) == 2 and all(json.loads(c.read_text(encoding="utf-8"))["experimente"] == 2 for c in copii)
    # Cele trei rulări ale sămânței stau pe aceeași linie, cu GPT-ul simplu primul.
    fise = [json.loads(r) for r in (tmp_path / "lucru" / "jurnal" / "experimente.jsonl").read_text(encoding="utf-8").splitlines()]
    runda2 = [f for f in fise if f["linie"].startswith("m3_runda2_")]
    assert len(runda2) == 3 and len({f["linie"] for f in runda2}) == 1
    assert [f["propunere"]["descriere"].split(",")[0] for f in runda2] == ["GPT simplu", "plasa adaptivă", "plasa veche (5 noduri)"]
    # În 3 pași, runda 1 n-a născut legături și n-a avut ce împărți: verdictul refuză concluziile.
    assert rezultat["verdict_adaptiva"].startswith("NECONCLUDENT: plasa a pornit goală")
    assert "Efectul adaptării, plasa adaptivă: NECONCLUDENT" in capsys.readouterr().out


def test_runda2_fara_runda1_nu_porneste(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert runda2_plasa_adaptiva.main([]) == 1
    assert "Nu găsesc rezultatul rundei 1" in capsys.readouterr().out


def _rand(samanta, simplu, adaptiva, pasi=(100, 100, 100, 100), legaturi=3, ajutoare=("liber1 → noun.person",)):
    """simplu, adaptiva = (scor R1, scor R2)."""
    def rulare(scor, p, plasa):
        return {"scor": scor, "pasi": p, **({"legaturi_la_start": legaturi, "ajutoare_la_start": list(ajutoare)} if plasa else {})}

    return {
        "samanta": samanta,
        "simplu": {"r1": rulare(simplu[0], pasi[0], False), "r2": rulare(simplu[1], pasi[1], False)},
        "adaptiva": {"r1": rulare(adaptiva[0], pasi[2], False), "r2": rulare(adaptiva[1], pasi[3], True)},
    }


@pytest.mark.parametrize(
    "randuri,inceput",
    [
        ([_rand(0, (1.0, 1.0), (1.0, 0.98), pasi=(100, 100, 100, 90))], "NECONCLUDENT: pași diferiți"),
        ([_rand(0, (1.0, 1.0), (1.0, 0.98), legaturi=0, ajutoare=())], "NECONCLUDENT: plasa a pornit goală"),
        ([_rand(s, (1.0, 1.01), (1.0, 0.99)) for s in range(3)], "MARE (merge)"),
        ([_rand(s, (1.0, 0.99), (1.0, 1.01)) for s in range(3)], "MARE, dar în rău"),
        ([_rand(0, (1.0, 1.0), (1.0, 1.001)), _rand(1, (1.0, 1.0), (1.0, 0.998))], "MICĂ (noroc)"),
        ([_rand(0, (1.0, 1.0), (1.0, 0.98)), _rand(1, (1.0, 1.0), (1.0, 1.04))], "NECONCLUDENT: efectul nu are"),
    ],
)
def test_verdictul_rundei_2(randuri, inceput):
    assert runda2_plasa_adaptiva.verdict(randuri, 100, 0.005).startswith(inceput)


def test_plasa_cu_ajutoare_dar_fara_legaturi_nu_e_goala():
    rand = _rand(0, (1.0, 1.01), (1.0, 0.99), legaturi=0)
    assert runda2_plasa_adaptiva.verdict([rand], 100, 0.005).startswith("MARE (merge)")


def test_timp_egal(tmp_path, monkeypatch, capsys):
    pytest.importorskip("torch")
    monkeypatch.chdir(tmp_path)
    argumente = _configurari(tmp_path)
    doar_doua = [a for i, a in enumerate(argumente) if "plasa5" not in argumente[i - (i % 2)]]
    assert compara_timp_egal.main(doar_doua + ["--seminte", "1", "--minute", "0.005", "--pauza", "0", "--racire", "0"]) == 0
    rezultat = json.loads(next((tmp_path / "lucru").glob("timp_egal_m3_*.json")).read_text(encoding="utf-8"))
    rand = rezultat["randuri"][0]
    assert rand["simplu"]["pasi"] > 0 and rand["adaptiva"]["pasi"] > 0 and rezultat["verdict"]
    fise = [json.loads(r) for r in (tmp_path / "lucru" / "jurnal" / "experimente.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(fise) == 2 and all(f["setari"]["model"]["pasi_max"] == 0 for f in fise)  # fără limită de pași: doar timpul
    assert "Verdict:" in capsys.readouterr().out


@pytest.mark.parametrize(
    "diferente,inceput",
    [((-0.01, -0.02), "MARE (merge)"), ((0.01, 0.02), "MARE, dar în rău"), ((0.001, -0.002), "MICĂ (noroc)"),
     ((-0.02, 0.03), "NECONCLUDENT")],
)
def test_verdictul_la_timp_egal(diferente, inceput):
    randuri = [{"simplu": {"scor": 1.0}, "adaptiva": {"scor": 1.0 + d}} for d in diferente]
    assert compara_timp_egal.verdict(randuri, 0.005).startswith(inceput)
