"""Școala de cod: înghețul și rollback-ul (arhivă + tag Git; jurnalul doar crește)."""

from __future__ import annotations

import json
import subprocess
import zipfile

import pytest

from unelte import ingheata_cod
from unelte.ingheata_cod import exista, ingheata, lista, revino


def lucru_cu_linii(tmp_path):
    cod = tmp_path / "lucru" / "cod"
    for linie in ("A", "B"):
        (cod / "linii" / linie).mkdir(parents=True)
        (cod / "linii" / linie / "model.pt").write_bytes(f"model {linie} v1".encode())
        (cod / f"biblioteca_{linie}.txt").write_text(f"TEST: show 1\nWRITE:\n1\nRESULT:\n1\npassed\n\n", encoding="utf-8")
        (cod / f"biblioteca_{linie}.jsonl").write_text('{"cod": "1"}\n', encoding="utf-8")
    (cod / "pregatit.pt").write_bytes(b"pregatit")
    (cod / "stare.json").write_text(json.dumps({"linii": {"A": {"temperatura": 1.0}, "B": {"temperatura": 0.7}}}),
                                    encoding="utf-8")
    (cod / "runde.jsonl").write_text('{"tip": "runda", "runda": 1}\n', encoding="utf-8")
    return tmp_path / "lucru"


def jurnal(lucru):
    return [json.loads(r) for r in (lucru / "cod" / "runde.jsonl").read_text(encoding="utf-8").splitlines()]


def test_rollback_pune_inapoi_tot_in_afara_de_jurnal(tmp_path):
    lucru = lucru_cu_linii(tmp_path)
    cod = lucru / "cod"
    arhiva = ingheata(lucru, "proba", "înainte de o schimbare", git=False)
    with zipfile.ZipFile(arhiva) as z:
        assert {"linii/A/model.pt", "linii/B/model.pt", "biblioteca_A.txt", "biblioteca_B.jsonl", "stare.json",
                "runde.jsonl", "pregatit.pt", "inghet.json"} <= set(z.namelist())
    assert json.loads((cod / "stare.json").read_text(encoding="utf-8"))["inghetat_dupa_ultima_runda"] is True
    # după îngheț, totul se schimbă
    (cod / "linii" / "A" / "model.pt").write_bytes(b"model A v2, stricat")
    (cod / "biblioteca_A.txt").write_text("altceva", encoding="utf-8")
    (cod / "stare.json").write_text(json.dumps({"linii": {"A": {"temperatura": 0.5}}}), encoding="utf-8")
    with (cod / "runde.jsonl").open("a", encoding="utf-8") as f:
        f.write('{"tip": "runda", "runda": 2}\n')
    puse = revino(lucru, "proba", "proba uneltei")
    assert "linii/A/model.pt" in puse and "runde.jsonl" not in puse
    assert (cod / "linii" / "A" / "model.pt").read_bytes() == b"model A v1"
    assert (cod / "biblioteca_A.txt").read_text(encoding="utf-8").startswith("TEST: show 1")
    assert json.loads((cod / "stare.json").read_text(encoding="utf-8"))["linii"]["A"]["temperatura"] == 1.0
    randuri = jurnal(lucru)  # jurnalul n-a fost suprascris: runda 2 e tot acolo, plus înghețul și rollback-ul
    assert [r["tip"] for r in randuri] == ["runda", "inghet", "runda", "rollback"]
    assert randuri[-1]["motiv"] == "rollback la proba, motiv: proba uneltei"


def test_inghetul_unei_linii_nu_atinge_cealalta_linie(tmp_path):
    lucru = lucru_cu_linii(tmp_path)
    cod = lucru / "cod"
    arhiva = ingheata(lucru, "doar_A", "linia A a trecut nivelul 0", ["A"], git=False)
    with zipfile.ZipFile(arhiva) as z:
        nume = set(z.namelist())
    assert "linii/A/model.pt" in nume and "linii/B/model.pt" not in nume and "pregatit.pt" not in nume
    (cod / "linii" / "B" / "model.pt").write_bytes(b"model B v2")
    stare = json.loads((cod / "stare.json").read_text(encoding="utf-8"))
    stare["linii"]["A"]["temperatura"], stare["linii"]["B"]["temperatura"] = 0.5, 0.5
    (cod / "stare.json").write_text(json.dumps(stare), encoding="utf-8")
    revino(lucru, "doar_A", "proba")
    stare = json.loads((cod / "stare.json").read_text(encoding="utf-8"))
    assert stare["linii"]["A"]["temperatura"] == 1.0 and stare["linii"]["B"]["temperatura"] == 0.5
    assert (cod / "linii" / "B" / "model.pt").read_bytes() == b"model B v2"


def test_un_nume_nu_se_refoloseste_si_lista(tmp_path):
    lucru = lucru_cu_linii(tmp_path)
    ingheata(lucru, "unu", "primul", git=False)
    with pytest.raises(FileExistsError):
        ingheata(lucru, "unu", "iar", git=False)
    with pytest.raises(FileNotFoundError):
        revino(lucru, "nu_exista", "x")
    assert [i["eticheta"] for i in lista(lucru)] == ["unu"]


def test_tagul_git(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    for comanda in (["git", "init", "-q"], ["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q",
                                                "--allow-empty", "-m", "start"]):
        subprocess.run(comanda, cwd=repo, check=True, capture_output=True)
    lucru = lucru_cu_linii(tmp_path)
    ingheata(lucru, "cu_tag", "proba", git=True, radacina=repo)  # fără nume și email în Git, ca pe laptop
    taguri = subprocess.run(["git", "tag", "-l", "cod/*"], cwd=repo, capture_output=True, text=True).stdout.split()
    assert taguri == ["cod/cu_tag"] and exista(lucru, "cu_tag", True, repo)
    (lucru / "cod" / "inghet" / "cu_tag.zip").unlink()
    with pytest.raises(FileExistsError):  # tag-ul rămâne: numele tot nu se refolosește
        ingheata(lucru, "cu_tag", "iar", git=True, radacina=repo)
    assert jurnal(lucru)[-1]["tag_git"] == "cod/cu_tag"


def test_tag_ul_esuat_nu_lasa_inghet_pe_jumatate(tmp_path):
    """Un depozit Git fără niciun commit: tag-ul nu are pe ce să stea, deci eșuează (fără să atingă depozitul proiectului,
    chiar dacă dosarul temporar e în el)."""
    lucru = lucru_cu_linii(tmp_path)
    gol = tmp_path / "depozit_gol"
    gol.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=gol, check=True, capture_output=True)
    with pytest.raises(RuntimeError, match="înghețul nu s-a făcut"):
        ingheata(lucru, "rupt", "proba", git=True, radacina=gol)
    assert not list((lucru / "cod" / "inghet").glob("rupt*"))
    assert [r["tip"] for r in jurnal(lucru)] == ["runda"]  # nimic în jurnal
    ingheata(lucru, "rupt", "a doua încercare", git=False)  # numele rămâne liber


def test_linia_de_comanda(tmp_path, capsys):
    lucru = lucru_cu_linii(tmp_path)
    assert ingheata_cod.main(["--eticheta", "cli", "--motiv", "proba", "--fara-git", "--director-lucru", str(lucru)]) == 0
    assert ingheata_cod.main(["--revino", "cli", "--director-lucru", str(lucru)]) == 1  # fără motiv: refuzat
    assert ingheata_cod.main(["--revino", "cli", "--motiv", "proba", "--director-lucru", str(lucru)]) == 0
    assert ingheata_cod.main(["--lista", "--director-lucru", str(lucru)]) == 0
    assert "cli" in capsys.readouterr().out
