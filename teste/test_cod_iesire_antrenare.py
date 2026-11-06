"""S81 (6 nov 2026): antrenarea lungă iese cu cod 1 când o oră e anulată sau rularea se oprește înainte de vreme, ca un
lanț să nu meargă mai departe la examene pe alt model decât cel așteptat (la S77c, ora 3 anulată dădea cod 0)."""

from __future__ import annotations

import pytest

from kronos.jurnal import Jurnal
from teste.test_bucla_cinstita import config_mic
from unelte import antrenare_lunga, antrenare_recalcul

ARGUMENTE = ["--pauza", "0", "--racire", "0", "--lungime", "20"]


@pytest.fixture
def linie_cu_o_ora(tmp_path, monkeypatch):
    """O linie minusculă pe procesor, cu o oră reușită (cod 0)."""
    pytest.importorskip("torch")
    monkeypatch.chdir(tmp_path)
    cale = config_mic(tmp_path, "linie")
    argumente = ["--config", str(cale)] + ARGUMENTE
    assert antrenare_lunga.main(argumente + ["--ore", "1"]) == 0  # toate orele bune → cod 0
    return tmp_path, argumente


def test_ora_anulata_da_cod_1_cu_motivul(linie_cu_o_ora, monkeypatch, capsys):
    tmp_path, argumente = linie_cu_o_ora
    jurnal = Jurnal(tmp_path / "lucru")

    def anulata(config, linie, *a, **o):
        jurnal.adauga({"id": jurnal.urmatorul_id(), "linie": linie, "decizie": "anulat",
                       "motiv": "testul rapid: CUDA out of memory"})
        return None

    monkeypatch.setattr(antrenare_lunga, "ruleaza", anulata)
    capsys.readouterr()
    assert antrenare_lunga.main(argumente + ["--ore", "3"]) == 1
    iesire = capsys.readouterr().out
    assert "oprit înainte de vreme: ora 2 anulată — testul rapid: CUDA out of memory" in iesire
    assert "Salvat în" in iesire  # tabelul și rezultat.json se scriu în continuare, din orele făcute


def test_oprirea_de_la_buton_sau_paznic_da_cod_1(linie_cu_o_ora, monkeypatch, capsys):
    _, argumente = linie_cu_o_ora
    monkeypatch.setattr(antrenare_lunga, "ruleaza", lambda *a, **o: None)
    capsys.readouterr()
    assert antrenare_lunga.main(argumente + ["--ore", "2"]) == 1
    assert "oprit înainte de vreme: ora 2 nu s-a făcut — butonul de oprire sau paznicul" in capsys.readouterr().out


def test_anularea_veche_nu_se_ia_drept_motiv(tmp_path):
    jurnal = Jurnal(tmp_path / "lucru")
    jurnal.adauga({"id": 1, "linie": "linie", "decizie": "anulat", "motiv": "de ieri"})
    primul = jurnal.urmatorul_id()
    assert "butonul de oprire" in antrenare_lunga.motivul_opririi(jurnal, "linie", 4, primul)
    jurnal.adauga({"id": primul, "linie": "alta", "decizie": "anulat", "motiv": "altă linie"})
    assert "butonul de oprire" in antrenare_lunga.motivul_opririi(jurnal, "linie", 4, primul)
    jurnal.adauga({"id": primul + 1, "linie": "linie", "decizie": "anulat", "motiv": "memorie"})
    assert antrenare_lunga.motivul_opririi(jurnal, "linie", 4, primul) == "ora 4 anulată — memorie"


def test_raportul_si_reluarea_fara_ore_noi_raman_cod_0(linie_cu_o_ora, monkeypatch):
    _, argumente = linie_cu_o_ora
    monkeypatch.setattr(antrenare_lunga, "ruleaza", lambda *a, **o: pytest.fail("nu trebuie să antreneze"))
    assert antrenare_lunga.main(argumente + ["--raport"]) == 0
    assert antrenare_lunga.main(argumente + ["--ore", "1"]) == 0  # nimic de făcut: doar raportul


def test_recalculul_transmite_codul(monkeypatch):
    pytest.importorskip("torch")
    from module.model_muon import ModelGPTConversatieMuon as M

    try:
        for cod in (0, 1):
            monkeypatch.setattr(antrenare_lunga, "main", lambda rest, cod=cod: cod)
            assert antrenare_recalcul.main(["--memorie-max-mb", "0", "--config", "x.toml", "--ore", "1"]) == cod
    finally:
        antrenare_recalcul.dezinstaleaza(M)
