"""Căile modelelor salvate (kronos/cai.py): jurnalul rămâne bun și după mutarea proiectului pe alt calculator."""

import json
from pathlib import Path

from kronos.cai import gaseste_model, relativ_la_proiect
from kronos.config import citeste_config
from kronos.orchestrator import Orchestrator

RADACINA = Path(__file__).resolve().parent.parent
CALE_LAPTOP = r"C:\Users\XyZ\Desktop\ProjectX\cyberspace\lucru\stocare\modele\experiment_262.pt"


def test_calea_care_exista_ramane_neschimbata(tmp_path):
    fisier = tmp_path / "altundeva" / "experiment_7.pt"
    fisier.parent.mkdir()
    fisier.write_bytes(b"x")
    assert gaseste_model(str(fisier), tmp_path / "lucru") == str(fisier)


def test_calea_de_pe_alt_calculator_se_cauta_dupa_nume_in_stocarea_de_aici(tmp_path):
    aici = tmp_path / "lucru" / "stocare" / "modele" / "experiment_262.pt"
    aici.parent.mkdir(parents=True)
    aici.write_bytes(b"x")
    assert Path(gaseste_model(CALE_LAPTOP, tmp_path / "lucru")) == aici
    assert Path(gaseste_model(CALE_LAPTOP.replace("\\", "/"), tmp_path / "lucru")) == aici  # și cu „/”


def test_modelul_care_nu_e_nicaieri_intoarce_calea_din_jurnal(tmp_path):
    (tmp_path / "lucru" / "stocare" / "modele").mkdir(parents=True)
    assert gaseste_model(CALE_LAPTOP, tmp_path / "lucru") == CALE_LAPTOP  # eroarea de la încărcare arată ce s-a căutat


def test_implicit_cauta_in_lucru_din_folderul_proiectului(tmp_path, monkeypatch):
    aici = tmp_path / "lucru" / "stocare" / "modele" / "experiment_262.pt"
    aici.parent.mkdir(parents=True)
    aici.write_bytes(b"x")
    monkeypatch.chdir(tmp_path)
    assert Path(gaseste_model(CALE_LAPTOP)).resolve() == aici.resolve()


def test_relativ_la_proiect(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    inauntru = tmp_path / "lucru" / "stocare" / "modele" / "experiment_1.json"
    assert relativ_la_proiect(str(inauntru)) == "lucru/stocare/modele/experiment_1.json"
    afara = str(tmp_path.parent / "altundeva" / "experiment_1.json")
    assert relativ_la_proiect(afara) == afara  # în afara proiectului: rămâne cum e


def test_modelele_noi_se_noteaza_relativ_si_se_gasesc_dupa_mutare(tmp_path, monkeypatch):
    """Kronos notează modelul păstrat cu calea relativă la proiect; după ce proiectul se mută, fișa veche (cu orice
    cale ar avea) duce tot la fișierul din stocarea de aici, fără ca jurnalul să se schimbe."""
    (tmp_path / "config").mkdir()
    text = (RADACINA / "config" / "proba.toml").read_text(encoding="utf-8")
    (tmp_path / "config" / "proba.toml").write_text(text, encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.syspath_prepend(str(RADACINA))
    fise = Orchestrator(citeste_config("config/proba.toml")).ruleaza(3)
    pastrate = [f for f in fise if f.get("model_salvat")]
    assert pastrate, "proba ar fi trebuit să păstreze măcar un model"
    for f in pastrate:
        assert not Path(f["model_salvat"]).is_absolute() and f["model_salvat"].startswith("lucru/stocare/modele/")
        assert Path(f["model_salvat"]).exists()

    jurnal = tmp_path / "lucru" / "jurnal" / "experimente.jsonl"
    inainte = jurnal.read_bytes()
    nume = Path(pastrate[0]["model_salvat"]).name
    vechi = rf"D:\AltCalculator\cyberspace\lucru\stocare\modele\{nume}"
    assert Path(gaseste_model(vechi)).resolve() == (tmp_path / pastrate[0]["model_salvat"]).resolve()
    assert jurnal.read_bytes() == inainte
    assert all(json.loads(rand) for rand in inainte.decode("utf-8").splitlines())
