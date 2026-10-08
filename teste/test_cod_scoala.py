"""Școala de cod: bucla, pregătirea, pilotul, liniile A/B, regresia, paznicul în buclă și raportul.

Un test merge cap-coadă cu un model GPT minuscul (procesor). Celelalte folosesc un elev scris de mână (teste/cod_proba.py)
ca să treacă prin toate drumurile buclei: trecere, picare, regresie, trișat, STOP, configurare schimbată, placă
ocupată, baterie.
"""

from __future__ import annotations

import json

import pytest

from module.cod import paznic_cod
from module.cod.elev import model_de_proba
from teste.cod_proba import ElevDeProba, solutiile, worktree_de_proba
from unelte import raport_cod, scoala_cod
from unelte.ingheata_cod import ingheata, revino
from unelte.scoala_cod import Scoala, citeste_config, text_antrenare


def senzori_linistiti(**schimbari) -> paznic_cod.Senzori:
    valori = dict(temperatura=lambda: None, alte_procese=lambda: [], memorie_ocupata_mb=lambda: 0,
                  pe_baterie=lambda: False, placa=lambda: {"treapta": "P0", "mhz": 1425}, asteapta=lambda secunde: None)
    return paznic_cod.Senzori(**{**valori, **schimbari})


def scoala(tmp_path, schimbari=None, senzori=None, afiseaza=None) -> Scoala:
    cale = worktree_de_proba(tmp_path, schimbari)
    rad = cale.parent.parent
    s = Scoala(citeste_config(cale), radacina=rad, cale_config=cale, senzori=senzori or senzori_linistiti(),
               git_la_inghet=False, afiseaza=afiseaza or (lambda text: None))
    paznic_cod.aproba(rad, s.lucru)
    return s


def elevi_de_proba(s: Scoala) -> dict[str, ElevDeProba]:
    """Câte un elev scris de mână pentru pregătire („pornire”), linia A și linia B; toți știu toate sarcinile."""
    solutii = solutiile(s, tuple(s.cfg["pilot"]["niveluri"]))
    elevi: dict[str, ElevDeProba] = {}
    s.fabrica_elev = lambda cale: elevi.setdefault(cale.parent.name, ElevDeProba(solutii))
    return elevi


def jurnal(s: Scoala) -> list[dict]:
    return [json.loads(r) for r in (s.cod / "runde.jsonl").read_text(encoding="utf-8").splitlines()]


def test_pilot_cap_coada_cu_modelul_minuscul(tmp_path):
    """Modelul minuscul nu știe nimic: amândouă liniile pică la nivelul 0, cinstit, cu tot drumul în jurnal."""
    s = scoala(tmp_path, {"pilot.niveluri": ["0"], "buget.runde_pe_nivel": 1})
    model_de_proba(s.lucru / "cod" / "pornire" / "model.pt", s.abecedar.text, context=512)
    assert s.pilot() == {"A 0": "picat", "B 0": "picat"}
    randuri = jurnal(s)
    assert [r["tip"] for r in randuri] == ["pilot_inceput", "pregatire", "inghet", "nivel_inceput", "runda", "inghet",
                                           "nivel_picat", "nivel_inceput", "runda", "inghet", "nivel_picat",
                                           "pilot_gata"]
    assert all(isinstance(r["motiv"], str) and len(r["motiv"]) > 15 for r in randuri)  # fiecare decizie, explicată
    runda = randuri[4]
    for cheie in ("linie", "nivel", "runda", "temperatura", "incercari", "trecute", "unice_noi", "trisate",
                  "marime_biblioteca", "pasi_antrenare", "rata_vazut", "rata_nevazut", "secunde", "memorie_video_mb",
                  "temperatura_placa", "placa"):
        assert cheie in runda, cheie
    assert runda["incercari"] == 4 and runda["pasi_antrenare"] == 2 and runda["episoade_in_fata"] == 2
    assert randuri[3]["regula"] == "scurta" and "regula scurtată + 2 exemple" in randuri[3]["motiv"]
    pregatire = randuri[1]
    assert set(pregatire["nevazut_inainte"]) == {"0"} and pregatire["povesti_bpo_inainte"] > 0
    for linie in "AB":
        sl = s.stare()["linii"][linie]
        assert sl["oprita"] and sl["niveluri_picate"]["0"]["inghet"] == f"{linie}_0_picat"
        assert (s.cod / "inghet" / f"{linie}_0_picat.zip").exists()
        assert s.model_liniei(linie).read_bytes() != (s.cod / "pregatit.pt").read_bytes()  # s-a antrenat
        assert (s.cod / "respinse" / f"{linie}.jsonl").exists()
    assert (s.cod / "inghet" / "inainte_de_pilot.zip").exists()
    text = raport_cod.raport(s.cod)
    assert "**Linia A:** n-a trecut niciun nivel; **s-a rupt la 0**" in text and "| 0 | ✗" in text


def test_elevul_care_stie_trece_nivelurile_pe_ambele_linii(tmp_path):
    s = scoala(tmp_path)
    elevi = elevi_de_proba(s)
    assert s.pilot() == {"A 0": "trecut", "B 0": "trecut", "A 1": "trecut", "B 1": "trecut"}
    for linie in "AB":
        sl = s.stare()["linii"][linie]
        assert set(sl["niveluri_trecute"]) == {"0", "1"} and sl["ultimul_inghet"] == f"{linie}_1" and not sl["oprita"]
        assert all(i["adversarial"] == 1.0 and i["sacru"] == 1.0 and i["runda"] == 1
                   for i in sl["niveluri_trecute"].values())
    assert sorted(p.stem for p in (s.cod / "inghet").glob("*.zip")) == ["A_0", "A_1", "B_0", "B_1", "inainte_de_pilot"]
    # varianta 3: regula scurtată + 2 exemple + sarcina în față; aceeași regulă în pregătire și în antrenare
    scurta = "RULE: Survive.\nPLACE: Here, what you write happens. If you do not pass the test, you are deleted.\n"
    assert all(f.startswith(scurta + "\nEXAMPLES:\n\n") and f.count("TEST: ") == 3 for f, _, _ in elevi["A"].fete)
    assert elevi["pornire"].antrenari == [s.text_abecedar] and s.text_abecedar.startswith(scurta)
    assert "Here are some simple pieces of code" not in s.text_abecedar  # regula lungă rămâne doar în abecedar
    # A se antrenează doar pe abecedar; B pe abecedar și pe biblioteca ei
    assert elevi["A"].antrenari and all(t == s.text_abecedar for t in elevi["A"].antrenari)
    assert all(s.text_abecedar in t and "\nTEST: " in t[len(s.text_abecedar):] for t in elevi["B"].antrenari)
    # amândouă bibliotecile s-au umplut cu aceleași reușite, în format episod
    citeste = lambda l: [json.loads(r) for r in (s.cod / f"biblioteca_{l}.jsonl").read_text(encoding="utf-8").splitlines()]  # noqa: E731
    assert citeste("A") and [(i["test"], i["cod"]) for i in citeste("A")] == [(i["test"], i["cod"]) for i in citeste("B")]
    assert (s.cod / "biblioteca_B.txt").read_text(encoding="utf-8").startswith("TEST: ")
    # aceleași texte din față, aceleași semințe, aceleași temperaturi pe ambele linii
    assert elevi["A"].fete == elevi["B"].fete
    runde = [r for r in jurnal(s) if r["tip"] == "runda"]
    assert [(r["linie"], r["nivel"], r["temperatura"], r["temperatura_urmatoare"]) for r in runde] == \
        [("A", "0", 1.0, 0.5), ("B", "0", 1.0, 0.5), ("A", "1", 1.0, 0.5), ("B", "1", 1.0, 0.5)]
    assert "fără regresie" in [r for r in jurnal(s) if r["tip"] == "nivel_trecut"][-1]["motiv"]


def test_celelalte_variante_si_prea_putine_exemple(tmp_path):
    lunga = scoala(tmp_path / "1", {"mediu.regula": "lunga"})
    assert lunga.regula_test == lunga.abecedar.preambul and lunga.text_abecedar == lunga.abecedar.text
    fara = scoala(tmp_path / "2", {"mediu.regula": "fara"})
    assert fara.regula_test == "" and fara.text_abecedar == fara.abecedar.text
    # mai multe exemple decât există la nivelul 0: școala se oprește, nu dă testul cu mai puține fără să spună
    prea_multe = scoala(tmp_path / "3", {"mediu.episoade": 50})
    elevi_de_proba(prea_multe)
    with pytest.raises(RuntimeError, match="încap doar 8 exemple din 50"):  # nivelul 0 are 8 episoade în abecedar
        prea_multe.pregateste()
    with pytest.raises(ValueError, match="regula"):
        citeste_config(worktree_de_proba(tmp_path / "4", {"mediu.regula": "alta"}))


def test_trisorul_e_prins_numarat_si_raportat(tmp_path):
    s = scoala(tmp_path, {"buget.runde_pe_nivel": 1})
    elevi = elevi_de_proba(s)
    s.pregateste()
    elevi["A"] = ElevDeProba({})
    elevi["A"].trisor = True
    assert s.nivel("A", "0") == "picat"
    runda = next(r for r in jurnal(s) if r["tip"] == "runda")
    assert runda["trisate"] == runda["incercari"] == 4 and runda["trecute"] == 0 and runda["trisat_raportat"]
    assert "RAPORTAT" in runda["motiv"] and runda["exemple_trisate"] == ["cod interzis: „import”"]
    assert not (s.cod / "biblioteca_A.jsonl").exists()  # nimic trișat nu intră în bibliotecă
    respinse = [json.loads(r) for r in (s.cod / "respinse" / "A.jsonl").read_text(encoding="utf-8").splitlines()]
    assert {r["verdict"] for r in respinse} == {"trișat"}
    assert "prinse trișând" in raport_cod.raport(s.cod)


def test_regresia_opreste_linia_si_pastreaza_modelul_principal(tmp_path):
    s = scoala(tmp_path)
    elevi = elevi_de_proba(s)
    s.pregateste()
    assert s.nivel("A", "0") == "trecut"
    elevi["A"].gresit = {x.text for x in s.seturi("0").nevazut}  # „uită” nivelul 0
    assert s.nivel("A", "1") == "regresie"
    sl = s.stare()["linii"]["A"]
    assert sl["oprita"] and sl["ultimul_inghet"] == "A_0" and "regresie după nivelul 1" in sl["motiv_oprire"]
    assert sl["niveluri_trecute"]["1"]["regresii"] == {"0": {"atunci": 1.0, "acum": 0.0}}
    ultimul = jurnal(s)[-1]
    assert ultimul["tip"] == "regresie" and "REGRESIE" in ultimul["motiv"] and "--revino A_0" in ultimul["motiv"]
    with pytest.raises(RuntimeError, match="e oprită"):
        s.nivel("A", "2A")
    revino(s.lucru, "A_0", "după regresie: înapoi la modelul principal")  # omul decide
    sl = s.stare()["linii"]["A"]
    assert not sl["oprita"] and set(sl["niveluri_trecute"]) == {"0"}


def test_regresia_inseamna_peste_15_puncte(tmp_path):
    s = scoala(tmp_path, {"examen.nevazut": 20})
    elevi = elevi_de_proba(s)
    s.pregateste()
    nevazut_0 = [x.text for x in s.seturi("0").nevazut]
    for linie, gresite, asteptat in (("A", 3, "trecut"), ("B", 4, "regresie")):  # 100% → 85% (15 puncte) / 80% (20)
        assert s.nivel(linie, "0") == "trecut"
        elevi[linie].gresit = set(nevazut_0[:gresite])
        assert s.nivel(linie, "1") == asteptat


def test_stop_reluarea_si_configurarea_schimbata(tmp_path):
    stop = {"dupa_runda": True}

    def afiseaza(text):
        if stop["dupa_runda"] and " runda: " in text:
            (s.lucru / "STOP").touch()

    s = scoala(tmp_path, {"buget.runde_pe_nivel": 3}, afiseaza=afiseaza)
    elevi = elevi_de_proba(s)
    s.pregateste()
    elevi["A"] = ElevDeProba({})  # nu știe nimic
    assert s.nivel("A", "0") == "oprit" and "STOP" in jurnal(s)[-1]["motiv"]
    sl = s.stare()["linii"]["A"]
    assert sl["buget"]["0"]["runde"] == 1 and sl["nivel_curent"] == "0" and sl["temperatura"] == 1.0
    # configurarea se schimbă fără îngheț înainte: paznicul refuză
    (s.lucru / "STOP").unlink()
    stop["dupa_runda"] = False
    s.cale_config.write_text(s.cale_config.read_text(encoding="utf-8").replace("lot = 2", "lot = 3"), encoding="utf-8")
    assert s.nivel("A", "0") == "oprit" and "configurarea s-a schimbat" in jurnal(s)[-1]["motiv"]
    # după un îngheț, merge mai departe de unde a rămas, cu bugetul consumat
    ingheata(s.lucru, "inainte_de_lot_3", "înainte de schimbarea lotului", git=False)
    assert s.nivel("A", "0") == "picat"
    assert s.stare()["linii"]["A"]["buget"]["0"]["runde"] == 3
    assert [r["reluat"] for r in jurnal(s) if r["tip"] == "nivel_inceput"] == [False, True, True]


def test_pilotul_nu_porneste_cu_placa_ocupata(tmp_path):
    s = scoala(tmp_path, senzori=senzori_linistiti(alte_procese=lambda: ["4321 python.exe 3000 MiB"]))
    with pytest.raises(RuntimeError, match="placa nu e liberă"):
        s.pilot()
    s = scoala(tmp_path / "2", senzori=senzori_linistiti(memorie_ocupata_mb=lambda: 3100))
    with pytest.raises(RuntimeError, match="3100 MB"):
        s.pilot()


def test_pe_baterie_asteapta_apoi_se_opreste(tmp_path):
    s = scoala(tmp_path, senzori=senzori_linistiti(pe_baterie=lambda: True))
    elevi_de_proba(s)
    s.pregateste()
    assert s.nivel("A", "0") == "oprit" and "pe baterie" in jurnal(s)[-1]["motiv"]
    assert s.stare()["linii"]["A"]["buget"]["0"]["runde"] == 0  # nicio rundă pe baterie


def test_temperatura_doar_scade(tmp_path):
    s = scoala(tmp_path)
    assert s.temperatura_de_start("0") == 1.0 and s.temperatura_de_start("3A") == 0.7
    assert [s.temperatura_noua(1.0, r) for r in (0.0, 0.1, 0.11, 0.5, 0.51)] == [1.0, 1.0, 0.7, 0.7, 0.5]
    assert s.temperatura_noua(0.5, 0.2) == 0.5


def test_abecedarul_ramane_cel_putin_5_la_suta():
    abecedar = "A" * 1000
    assert text_antrenare(abecedar, "", 0.05) == abecedar
    for biblioteca in ("B" * 100, "B" * 50_000, "B" * 1_000_000):
        text = text_antrenare(abecedar, biblioteca, 0.05)
        assert text.count("A") / len(text) >= 0.05 and biblioteca in text


def test_raportul_spune_unde_se_rupe_lantul(tmp_path):
    s = scoala(tmp_path)
    elevi = elevi_de_proba(s)
    s.pregateste()
    elevi["A"] = ElevDeProba(solutiile(s, ("0",)))  # A știe doar nivelul 0
    assert s.pilot() == {"A 0": "trecut", "B 0": "trecut", "A 1": "picat", "B 1": "trecut"}
    text = raport_cod.raport(s.cod)
    assert "**Linia A:** a trecut 0; **s-a rupt la 1**" in text and "**Linia B:** a trecut 0, 1." in text
    assert "| 1 | ✗ 0% / 0% / 0% / 0% | ✓ 100% / 100% / 100% / 100% |" in text
    assert "- A 1: 1 ×2" in text and "abecedar mai mare la 1" in text
    assert "## Soluții cu o formă care nu e în abecedar" in text and "## Timpul pe nivel" in text
    assert raport_cod.main(["--director-lucru", str(s.lucru)]) == 0
    assert (s.cod / "raport.md").read_text(encoding="utf-8").startswith("# Școala de cod: raportul")


def test_linia_de_comanda_refuza_ce_nu_trebuie(capsys):
    assert scoala_cod.main(["--nivel", "0"]) == 1 and "--nivel cere --linie" in capsys.readouterr().out
    assert scoala_cod.main(["--genereaza-sacru"]) == 1 and "există deja" in capsys.readouterr().out
