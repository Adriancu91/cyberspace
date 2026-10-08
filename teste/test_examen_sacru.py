"""Setul sacru de fapte (8 octombrie 2026): o a patra formulare pentru fiecare fapt, cu aceleași verificări ca examenul
nou și diferită de cele 3 ale lui. Se dă doar manual; nu intră în jurnalul Kronos și nu-l folosește nicio decizie
automată. Fără placă video: profesorul și elevul de probă din teste/test_examen_fapte_nou.py."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("numpy")

from module.examene_elev import INTREBARI  # noqa: E402
from teste.test_cap_coada import RADACINA  # noqa: E402
from teste.test_examen_fapte_nou import (EXAMEN_MIC, PRIMELE, ElevDeProba, ProfesorDeProba, index_din,  # noqa: E402
                                         scrie_examen)
from unelte import examen_fapte_nou as unealta  # noqa: E402
from unelte.examen_fapte_nou import FAPTE, cuvinte, genereaza, umple  # noqa: E402


def test_a_patra_formulare_e_diferita_de_cele_trei():
    profesor = ProfesorDeProba()
    # Examenul nou de probă: exact ce scrie profesorul la prima cerere, deci prima variantă a setului sacru e la fel.
    existente = {s: [umple(linie, unealta.raspunsul_faptului(s))
                     for linie in profesor._scrie(PRIMELE, FAPTE[s], unealta.raspunsul_faptului(s)).splitlines()]
                 for s in INTREBARI}
    indexuri = {"povestile cu fapte": index_din(""), "TinyStories": index_din("")}
    rezultat = genereaza(profesor, indexuri, runde=3, pe_fapt=1, existente=existente)
    assert rezultat["numere"]["propozitii"] == 50 and rezultat["numere"]["esuate"] == 0
    for intrebare in rezultat["intrebari"]:
        noua = cuvinte(intrebare["propozitie_intreaga"])
        assert all(noua != cuvinte(veche) for veche in existente[intrebare["subiect"]])
        assert intrebare["propozitie"].endswith("___.")
    istoric = rezultat["istoric"]["birds/1"]
    assert istoric[0]["motiv"] == "it is the same as another sentence"  # prima: la fel ca una din examenul nou


def test_cererea_spune_de_ce_formulari_sa_difere():
    cerere = unealta.cerere_trei("birds", ["A bird's body is covered with feathers."])[-1]["content"]
    assert "They must be different from these sentences: A bird's body is covered with feathers." in cerere
    assert "must be different" not in unealta.cerere_trei("birds")[-1]["content"]


def test_examenul_sacru_nu_scrie_in_jurnalul_kronos(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("unelte.modele_salvate.fisa_modelului",
                        lambda jurnal, experiment, linie: {"id": experiment, "linie": "antrenare_lunga_6a"})
    monkeypatch.setattr("unelte.modele_salvate.incarca_modelul", lambda fisa, dispozitiv: ElevDeProba())
    examen = scrie_examen(tmp_path / "sacru.json", EXAMEN_MIC)
    assert unealta.main(["--sacru", "--experiment", "262", "--examen", str(examen)]) == 0
    assert not (tmp_path / "lucru" / "jurnal" / "experimente.jsonl").exists()  # nimic în jurnalul Kronos
    randuri = (tmp_path / "lucru" / "examen_sacru" / "rezultate.jsonl").read_text(encoding="utf-8").splitlines()
    rand = json.loads(randuri[0])
    assert len(randuri) == 1 and (rand["experiment"], rand["fapte_sacre"], rand["fapte_sacre_cu_sinonime"]) == (262, 1, 2)
    assert "Nu se folosește la selecție; nu intră în jurnalul Kronos." in capsys.readouterr().out


def test_fara_sacru_implicit_e_examenul_nou(monkeypatch):
    vazute = []
    monkeypatch.setattr(unealta, "main_examen", lambda args: vazute.append((args.examen, args.sacru)) or 0)
    unealta.main(["--experiment", "1"])
    unealta.main(["--sacru", "--experiment", "1"])
    assert vazute == [(unealta.CALE_EXAMEN_NOU, False), (unealta.CALE_EXAMEN_SACRU, True)]


def test_nicio_parte_automata_nu_pomeneste_setul_sacru():
    """Modelele, kronos, CONTINUUM (cod și configurare), unealta de antrenare lungă și lanțul nu știu de setul sacru."""
    surse = [*(RADACINA / "module").rglob("*.py"), *(RADACINA / "kronos").rglob("*.py"),
             RADACINA / "config" / "continuum.toml", RADACINA / "unelte" / "antrenare_lunga.py",
             RADACINA / "unelte" / "lant_antrenare.py"]
    pomenit = [p.relative_to(RADACINA).as_posix() for p in surse
               if any(cuvant in p.read_text(encoding="utf-8") for cuvant in ("examen_sacru", "fapte_sacre", "sacru"))]
    assert pomenit == []
    from module import model_gpt
    assert "sacru" not in model_gpt.EXAMENE_SUPLIMENTARE


def test_setul_sacru_din_depozit():
    cale = RADACINA / unealta.CALE_EXAMEN_SACRU
    if not cale.exists():
        pytest.skip("setul sacru încă nu e generat")
    date = json.loads(cale.read_text(encoding="utf-8"))
    assert date["sacru"] is True and "nu se folosește la selecție" in date["nota"]
    assert sorted(i["subiect"] for i in date["intrebari"]) == sorted(INTREBARI)  # câte una pentru fiecare fapt
    existente = unealta.propozitiile_examenului(RADACINA / unealta.CALE_EXAMEN_NOU)
    for i in date["intrebari"]:
        # golul e la capăt (uneori fără punct, ca la 6 din cele 150 ale examenului nou: elevul primește textul dinainte)
        assert i["propozitie"].rstrip(".").endswith("___") and i["raspuns"] == unealta.raspunsul_faptului(i["subiect"])
        assert not any(unealta.prea_asemanatoare(cuvinte(i["propozitie_intreaga"]), cuvinte(e))
                       for e in existente[i["subiect"]])
