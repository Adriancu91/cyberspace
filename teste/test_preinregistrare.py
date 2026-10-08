"""Unealta de pre-înregistrare (planul joi–sâmbătă, lecția SANDBOX-7): șablonul înainte, „Ce a ieșit” din jurnal după."""

from __future__ import annotations

import json
from datetime import date, datetime

import pytest

from unelte import preinregistrare as pre


def experiment(id_: int, linie: str, ora: datetime, val_bpb: float, decizie: str, fapte_noi: int, **extra) -> dict:
    return {"id": id_, "linie": linie, "inceput": ora.astimezone().isoformat(), "decizie": decizie,
            "scoruri": {"val_bpb": val_bpb}, "criterii": {"fapte_noi": fapte_noi, "fapte_corecte": 140,
                                                         "nota_profesor": 4.5},
            "motiv": "scorul e mai bun" if decizie == "pastrat" else "scorul nu e mai bun", **extra}


def test_sablonul_si_inchiderea(tmp_path):
    dosar, lucru, continuum = tmp_path / "pre", tmp_path / "lucru", tmp_path / "lucru" / "continuum_pe_bune"
    cale = pre.scrie("noaptea1", "Noaptea 1", date(2026, 10, 8), datetime(2026, 10, 8, 22, 30), dosar)
    assert cale.name == "2026-10-08_noaptea1.md"
    text = cale.read_text(encoding="utf-8")
    for parte in ("## Întrebarea", "## Așteptările, în cifre", "## Ce ar infirma", "<!-- scrisa: 2026-10-08T22:30:00 -->"):
        assert parte in text
    with pytest.raises(FileExistsError):
        pre.scrie("noaptea1", "din nou", date(2026, 10, 8), dosar=dosar)
    with pytest.raises(ValueError):
        pre.scrie("noaptea 1!", "nume rău", dosar=dosar)

    (lucru / "jurnal").mkdir(parents=True)
    fise = [experiment(278, "antrenare_lunga_7", datetime(2026, 10, 8, 21, 10), 0.431, "pastrat", 66),  # înainte
            experiment(279, "antrenare_lunga_8", datetime(2026, 10, 8, 23, 20), 0.4300, "respins", 68,
                       fata_de_pornire=278, scor_anterior=0.431),
            experiment(280, "antrenare_lunga_8", datetime(2026, 10, 9, 0, 25), 0.4240, "pastrat", 69)]
    (lucru / "jurnal" / "experimente.jsonl").write_text("".join(json.dumps(f) + "\n" for f in fise), encoding="utf-8")
    continuum.mkdir()
    cicluri = [{"ciclu": 1, "timp": "2026-10-08T22:00:00", "nivel": "ÎNTREȚINERE"},  # înainte: nu intră
               {"ciclu": 2, "timp": "2026-10-08T23:05:00", "nivel": "ÎNVĂȚARE", "nevoie": "continua:povesti",
                "actiune": "antrenare lungă cu config/laptop_antrenare_lunga_8.toml", "motiv": "val_bpb încă scade",
                "rezultat": {"reusit": True}},
               {"ciclu": 3, "timp": "2026-10-09T06:40:00", "nivel": "REPAUS"}]
    (continuum / "cicluri.jsonl").write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in cicluri),
                                             encoding="utf-8")
    pre.inchide("noaptea1", lucru, continuum, datetime(2026, 10, 9, 7, 35), dosar)
    inchisa = cale.read_text(encoding="utf-8")
    assert inchisa.startswith(text)  # ce era scris înainte a rămas exact cum era
    adaos = inchisa[len(text):]
    assert "| 279 | antrenare_lunga_8 |" in adaos and "| 280 |" in adaos and "| 278 |" not in adaos
    assert "**antrenare_lunga_8:** 2 ore, 1 păstrate; val_bpb de la 0,4300 la 0,4240" in adaos
    assert "cel mai bun păstrat: #280 (0,4240); pornită din #278 (0,4310)" in adaos
    assert "2 cicluri (ÎNVĂȚARE: 1, REPAUS: 1), 1 cu o acțiune" in adaos
    assert "continua:povesti: antrenare lungă cu config/laptop_antrenare_lunga_8.toml (reușită)" in adaos
    with pytest.raises(ValueError, match="deja închisă"):
        pre.inchide("noaptea1", lucru, continuum, dosar=dosar)


def test_linia_de_comanda(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(pre, "DOSAR", tmp_path / "pre")
    monkeypatch.setattr(pre.scrie, "__defaults__", (None, None, tmp_path / "pre"))
    monkeypatch.setattr(pre.inchide, "__defaults__", (None, tmp_path / "pre"))
    monkeypatch.setattr(pre.gaseste, "__defaults__", (tmp_path / "pre",))
    assert pre.main(["--nume", "proba", "--titlu", "Proba", "--data", "2026-10-09"]) == 0
    assert (tmp_path / "pre" / "2026-10-09_proba.md").exists()
    assert pre.main(["--nume", "proba", "--data", "2026-10-09"]) == 1 and "există deja" in capsys.readouterr().out
    (tmp_path / "lucru" / "jurnal").mkdir(parents=True)
    (tmp_path / "lucru" / "jurnal" / "experimente.jsonl").write_text("", encoding="utf-8")
    assert pre.main(["--inchide", "proba", "--director-lucru", str(tmp_path / "lucru"),
                     "--continuum", str(tmp_path / "nimic")]) == 0
    assert "Niciun experiment Kronos" in (tmp_path / "pre" / "2026-10-09_proba.md").read_text(encoding="utf-8")
