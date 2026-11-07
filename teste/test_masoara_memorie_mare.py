"""S86: unealta unelte/masoara_memorie_mare.py (fără placă)."""

from __future__ import annotations

from pathlib import Path

import pytest

from unelte import masoara_memorie_mare as mm


def test_variantele_sunt_cele_din_sarcina():
    assert mm.VARIANTE == {
        "a": {"optimizator": "adamw", "lot": 4, "adunare_loturi": 24},
        "b": {"optimizator": "muon", "lot": 4, "adunare_loturi": 24},
        "c": {"optimizator": "muon", "lot": 6, "adunare_loturi": 16},
        "d": {"optimizator": "muon", "lot": 12, "adunare_loturi": 8},
    }


@pytest.mark.parametrize("varianta", ["a", "b", "c", "d"])
def test_setarile_modelului_vin_din_config_cu_copia(varianta, tmp_path):
    copie = tmp_path / "gpt.pt"
    s = mm.setari_model(varianta, copie, 100)
    assert s["n_straturi"] == 24 and s["n_emb"] == 768 and s["context"] == 512
    assert s["cale_stare"] == str(copie)
    assert s["pasi_max"] == 100 * mm.VARIANTE[varianta]["adunare_loturi"]
    assert s["optimizator"] == mm.VARIANTE[varianta]["optimizator"]
    assert s["lot"] * s["adunare_loturi"] == 96  # același număr de secvențe pe pas de optimizator


def test_originalul_nu_e_cale_stare():
    s = mm.setari_model("a", Path("x/gpt.pt"), 1)
    assert "w2_mare" not in s["cale_stare"]


@pytest.mark.parametrize("alocat,asteptat", [([], False), ([3000], False), ([3000, 3050, 3090], False),
                                             ([3000, 3500, 4000], True), ([3000, 3101], True)],
                         ids=["gol", "una", "sub_prag", "creste", "la_limita"])
def test_creste(alocat, asteptat):
    assert mm.creste(alocat) is asteptat


def test_urmaritorul_tine_varful_pe_faza():
    citiri = iter([(1000, 40), (5000, 60), (3000, 50)])
    u = mm.Urmaritor(citeste=lambda: next(citiri, None))
    u.faza = "1_antrenare"
    assert u.citeste_acum() == 1000
    assert u.citeste_acum() == 5000
    u.faza = "1_test_rapid"
    assert u.citeste_acum() == 3000
    assert u.varfuri == {"1_antrenare": 5000, "1_test_rapid": 3000}
    assert u.temperatura_max == 60
    assert u.citeste_acum() is None


def test_toate_refuza_a_doua_oara(tmp_path, monkeypatch):
    monkeypatch.setattr(mm, "DOSAR", tmp_path)
    (tmp_path / "s86.json").write_text("{}", encoding="utf-8")
    with pytest.raises(SystemExit):
        mm.toate(1, 5800)


def test_toate_ruleaza_golirea_doar_daca_memoria_creste(tmp_path, monkeypatch):
    monkeypatch.setattr(mm, "DOSAR", tmp_path)
    chemari = []

    def fals(varianta, repetari, pasi, goleste, eticheta, memorie):
        chemari.append((eticheta, repetari, goleste))
        return {"memoria_creste": eticheta == "a"}

    monkeypatch.setattr(mm, "in_proces_nou", fals)
    r = mm.toate(5, 5800)
    assert chemari == [("a", 3, False), ("b", 1, False), ("c", 1, False), ("d", 1, False), ("a_golit", 3, True)]
    assert (tmp_path / "s86.json").exists() and "a_golit" in r["variante"]


def test_main_toate_merge_cap_coada(tmp_path, monkeypatch):
    monkeypatch.setattr(mm, "DOSAR", tmp_path)
    monkeypatch.setattr(mm, "in_proces_nou", lambda *a, **k: {"memoria_creste": False})
    assert mm.main(["toate", "--pasi-optimizator", "2"]) == 0
    assert (tmp_path / "s86.json").exists()
