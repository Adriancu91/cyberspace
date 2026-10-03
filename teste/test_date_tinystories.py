"""Datele TinyStories: povești întregi, validarea separată de antrenare, fără descărcări inutile."""

from __future__ import annotations

import pytest

from module.date_tinystories import DateTinyStories
from teste.tinystories_mic import SEP, poveste_antrenare, poveste_validare, scrie_surse


def _povesti(text: str) -> list[str]:
    return [p.strip() for p in text.split(SEP)]


def test_povesti_intregi_si_validare_separata(tmp_path):
    date = DateTinyStories(**scrie_surse(tmp_path))
    antrenare, validare = _povesti(date.text_antrenare()), _povesti(date.text_validare())
    assert len(antrenare) >= 20 and len(validare) >= 5
    assert set(antrenare) <= {poveste_antrenare(i) for i in range(40)}  # doar povești întregi
    assert set(validare) <= {poveste_validare(i) for i in range(20)}
    assert not set(antrenare) & set(validare)  # validarea nu conține povești din antrenare
    assert date.info["scoase_din_validare"] == 1  # povestea comună a fost scoasă din validare
    assert "Poveste de început" not in date.text_antrenare()  # prima poveste se aruncă mereu
    assert "tăiată" not in date.text_validare()


def test_foloseste_fisierele_deja_pregatite(tmp_path):
    setari = scrie_surse(tmp_path)
    prima = DateTinyStories(**setari).text_antrenare()
    (tmp_path / "train.txt").unlink()  # dacă ar mai descărca, ar crăpa
    (tmp_path / "valid.txt").unlink()
    assert DateTinyStories(**setari).text_antrenare() == prima


def test_alta_marime_pregateste_din_nou(tmp_path):
    setari = scrie_surse(tmp_path)
    mica = DateTinyStories(**setari).text_antrenare()
    mare = DateTinyStories(**{**setari, "megaocteti": 0.006}).text_antrenare()
    assert len(mare) > len(mica)


def test_fara_internet_da_mesaj_clar(tmp_path):
    setari = scrie_surse(tmp_path)
    setari["url_antrenare"] = (tmp_path / "nu_exista.txt").as_uri()
    with pytest.raises(ValueError, match="Nu am putut descărca"):
        DateTinyStories(**setari)


def test_setari_invalide():
    with pytest.raises(ValueError, match="procent_validare"):
        DateTinyStories(procent_validare=0.7)
