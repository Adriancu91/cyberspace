"""Examenele pentru română și cod pe validările puse deoparte (unelte/examen_validari_ws.py)."""

from __future__ import annotations

import math

import pytest

from teste.test_bucla_cinstita import config_mic, fise
from unelte import antrenare_lunga
from unelte import examen_validari_ws as unealta

SEP = "<|endoftext|>"


def test_inceputul_se_taie_la_un_text_intreg(tmp_path):
    fisier = tmp_path / "v.txt"
    fisier.write_text("".join(f"textul numărul {k} are câteva cuvinte.\n{SEP}\n" for k in range(200)), encoding="utf-8")
    text = unealta.inceput_de_text(fisier, 2000)
    assert 1000 < len(text) <= 2000 and text.endswith(".\n") and text.startswith("textul numărul 0")
    assert unealta.inceput_de_text(fisier, 10**7) == fisier.read_text(encoding="utf-8")
    lung = tmp_path / "lung.txt"  # un singur text, mai lung decât bucata cerută: se taie la sfârșit de rând
    lung.write_text("un rând de cod\n" * 500, encoding="utf-8")
    assert unealta.inceput_de_text(lung, 1000).endswith("\n") and len(unealta.inceput_de_text(lung, 1000)) <= 1000


def test_numerele_pentru_jurnal_si_mediile_pe_grupe():
    rezultate = {
        "romana_wikipedia": {"bpb": 1.0, "octeti": 100, "bucati_corecte": 0.5, "octeti_ghiciti": 0.4},
        "romana_web": {"bpb": 2.0, "octeti": 300, "bucati_corecte": 0.25, "octeti_ghiciti": 0.2},
        "cod": {"bpb": 0.5, "octeti": 50},
        "cod_sarcini": {"lipseste": "date/x"},
    }
    n = unealta.numere(rezultate)
    assert n["bpb_romana"] == 1.75 and n["bpb_cod"] == 0.5          # media pe octeți
    assert n["corecte_romana_web"] == 0.25 and n["ghiciti_romana_wikipedia"] == 0.4
    assert "corecte_cod" not in n and "bpb_cod_sarcini" not in n


def test_examenul_pe_un_model_salvat(tmp_path, monkeypatch, capsys):
    """Un model mic, antrenat pe loc pe procesor și salvat de Kronos: examenul dă numere cu sens și le notează."""
    pytest.importorskip("torch")
    monkeypatch.chdir(tmp_path)
    cale = config_mic(tmp_path, "antrenare_lunga_3", model=', cale_stare = "lucru/antrenare_lunga_3/gpt.pt"', spatiu="lot = [4]")
    assert antrenare_lunga.main(["--config", str(cale), "--ore", "1", "--pauza", "0", "--racire", "0", "--lungime", "20"]) == 0
    model_id = [f for f in fise(tmp_path) if f.get("model_salvat")][-1]["id"]
    (tmp_path / "ro.txt").write_text(f"Pisica doarme pe covor, iar câinele aleargă prin grădină.\n{SEP}\n" * 40, encoding="utf-8")
    (tmp_path / "cod.txt").write_text(f"def aduna(a, b):\n    return a + b\n{SEP}\n" * 40, encoding="utf-8")
    monkeypatch.setattr(unealta, "VALIDARI", {"romana_wikipedia": str(tmp_path / "ro.txt"), "cod": str(tmp_path / "cod.txt"),
                                               "cod_sarcini": str(tmp_path / "lipsa.txt")})
    capsys.readouterr()
    assert unealta.main(["--experiment", str(model_id), "--dispozitiv", "cpu", "--caractere", "1500", "--fire", "2"]) == 0
    fisa = [f for f in fise(tmp_path) if f["linie"] == "examen_validari_ws"][-1]
    s = fisa["scoruri"]
    assert fisa["decizie"] == "masurat" and fisa["module"]["elev"]["experiment"] == model_id
    assert {"bpb_romana_wikipedia", "bpb_cod", "bpb_romana", "caractere"} <= set(s) and "bpb_cod_sarcini" not in s
    assert all(math.isfinite(v) and v > 0 for k, v in s.items() if k.startswith("bpb_"))
    assert all(0 <= v <= 1 for k, v in s.items() if k.startswith(("corecte_", "ghiciti_")))
    iesire = capsys.readouterr().out
    assert "media pe romana" in iesire and "lipsește" in iesire
    assert len(list((tmp_path / "lucru" / "examen_validari_ws").glob("experiment_*.json"))) == 1
