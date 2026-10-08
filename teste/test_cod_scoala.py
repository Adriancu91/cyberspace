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
    """O comandă greșită nu ajunge în jurnalul adevărat al școlii (pe 8 octombrie ajunsese de două ori, din acest test)."""
    jurnal_adevarat = scoala_cod.RADACINA / "lucru" / "cod" / "runde.jsonl"
    numara = lambda: jurnal_adevarat.read_text(encoding="utf-8").count("--nivel cere") if jurnal_adevarat.exists() else 0  # noqa: E731
    inainte = numara()
    assert scoala_cod.main(["--nivel", "0"]) == 1 and "--nivel cere --linie" in capsys.readouterr().out
    assert numara() == inainte
    assert scoala_cod.main(["--genereaza-sacru"]) == 1 and "există deja" in capsys.readouterr().out


# --- v0.2 ----------------------------------------------------------------------------------------------------------------

def scoala_v02(tmp_path, schimbari=None, senzori=None) -> Scoala:
    cale = worktree_de_proba(tmp_path, schimbari, config="config/scoala_cod_v02.toml")
    rad = cale.parent.parent
    s = Scoala(citeste_config(cale), radacina=rad, cale_config=cale, senzori=senzori or senzori_linistiti(),
               git_la_inghet=False, afiseaza=lambda text: None)
    paznic_cod.aproba(rad, s.lucru)
    return s


def test_v02_pregatirea_se_opreste_la_pierderea_tinta(tmp_path):
    s = scoala_v02(tmp_path, {"pregatire.pasi": 100})
    elevi = elevi_de_proba(s)
    s.pregateste()
    p = s.stare()["pregatire"]
    assert p["pasi"] == 30 and p["pierdere_abecedar"] == [[0, 2.0], [10, 1.4], [20, 0.9], [30, 0.45]]
    assert elevi["pornire"].cu_povesti == [(0.7, elevi["pornire"].cu_povesti[0][1])] * 3  # 70% povești, de 3 ori
    assert elevi["pornire"].cu_povesti[0][1] > 0 and "(ținta 0.5 atinsă)" in jurnal(s)[-1]["motiv"]
    assert (s.lucru / "cod_v02" / "pregatit.pt").exists() and s.cod == s.lucru / "cod_v02"
    neatinsa = scoala_v02(tmp_path / "2", {"pregatire.pasi": 20})
    elevi_de_proba(neatinsa)
    neatinsa.pregateste()
    assert neatinsa.stare()["pregatire"]["pasi"] == 20 and "neatinsă în 20 de pași" in jurnal(neatinsa)[-1]["motiv"]


def test_v02_povestile_raman_in_lectii_si_regresia_pe_povesti(tmp_path):
    s = scoala_v02(tmp_path)
    elevi = elevi_de_proba(s)
    elevi["pornire"] = ElevDeProba(solutiile(s, ("0a", "0b")))
    elevi["pornire"].bpo = 0.5  # pregătirea strică poveștile: liniile nu pornesc
    assert s.pilot() == {"pregatire": "regresie"}
    assert jurnal(s)[-1]["tip"] == "oprit" and "poveștile peste prag" in jurnal(s)[-1]["motiv"]
    s = scoala_v02(tmp_path / "2")
    elevi = elevi_de_proba(s)
    s.pregateste()
    elevi["A"] = ElevDeProba(solutiile(s, ("0a", "0b")))
    elevi["A"].bpo = 0.5  # trece nivelul de cod, dar poveștile trec de prag
    assert s.nivel("A", "0a") == "regresie"
    sl = s.stare()["linii"]["A"]
    assert sl["oprita"] and "povești 0.5 biți pe octet, peste pragul de 0.46" in sl["motiv_oprire"]
    assert sl["niveluri_trecute"]["0a"]["regresie_povesti"] is True and sl["ultimul_inghet"] is None
    assert elevi["A"].cu_povesti and all(f == 0.7 and n > 0 for f, n in elevi["A"].cu_povesti)


def test_v02_linia_D_primeste_cat_a_gasit_B_si_nu_se_antreneaza_pe_ale_ei(tmp_path):
    s = scoala_v02(tmp_path, {"pilot.niveluri": ["0b"], "buget.runde_pe_nivel": 3})
    solutii = solutiile(s, ("0b",))
    nevazut = {x.text for x in s.seturi("0b").nevazut}
    elevi = {"A": ElevDeProba(solutii), "B": ElevDeProba(solutii),
             "D": ElevDeProba({k: f"print({v})" for k, v in solutii.items()})}  # D își scrie reușitele altfel
    for e in elevi.values():
        e.gresit = set(nevazut)  # nimeni nu trece: trei runde pe fiecare linie
    s.fabrica_elev = lambda cale: elevi.setdefault(cale.parent.name, ElevDeProba(solutii))
    assert s.pilot() == {"A 0b": "picat", "B 0b": "picat", "D 0b": "picat"}
    randuri = jurnal(s)
    assert [r["linie"] for r in randuri if r["tip"] == "nivel_inceput"] == ["A", "B", "D"]
    b = {r["runda"]: r["unice_noi"] for r in randuri if r["tip"] == "runda" and r["linie"] == "B"}
    d = {r["runda"]: (r["de_la_unealta"], r["cerute_de_la_unealta"]) for r in randuri
         if r["tip"] == "runda" and r["linie"] == "D"}
    assert sum(b.values()) > 0 and d == {runda: (n, n) for runda, n in b.items()}
    proprii = [json.loads(r) for r in (s.cod / "biblioteca_D.jsonl").read_text(encoding="utf-8").splitlines()]
    unealta = [json.loads(r) for r in (s.cod / "biblioteca_unealta_D.jsonl").read_text(encoding="utf-8").splitlines()]
    assert proprii and all(i["cod"].startswith("print(") for i in proprii)
    assert all(not i["cod"].startswith("print(") for i in unealta) and len(unealta) == sum(b.values())
    for i in proprii:  # reușitele lui D nu intră în antrenarea lui
        assert all(f"WRITE:\n{i['cod']}\nRESULT:" not in t for t in elevi["D"].antrenari)
    for i in unealta:  # soluțiile uneltei intră
        assert f"TEST: {i['test']}\nWRITE:\n{i['cod']}\nRESULT:" in elevi["D"].antrenari[-1]
    assert elevi["A"].fete == elevi["B"].fete == elevi["D"].fete  # aceleași texte, semințe, temperaturi
    text = raport_cod.raport(s.cod)
    assert "## Liniile pe aceleași runde (A, B, D)" in text and "B față de D la 0b" in text
    assert "Linia D se antrenează pe soluțiile date de unealtă: 0b:" in text


def test_v02_regresia_pe_cod_cere_doua_sarcini_pierdute(tmp_path):
    s = scoala_v02(tmp_path)
    elevi = elevi_de_proba(s)
    s.pregateste()
    nevazut_0a = [x.text for x in s.seturi("0a").nevazut]  # 4 sarcini: o sarcină = 25 de puncte
    for linie, gresite, asteptat in (("A", 1, "trecut"), ("B", 2, "regresie")):
        assert s.nivel(linie, "0a") == "trecut"
        elevi[linie].gresit = set(nevazut_0a[:gresite])
        assert s.nivel(linie, "0b") == asteptat


def test_v02_dosarul_versiunii_si_etichetele(tmp_path):
    s = scoala_v02(tmp_path)
    elevi_de_proba(s)
    assert s.pilot() == {"A 0a": "trecut", "B 0a": "trecut", "D 0a": "trecut", "A 0b": "trecut", "B 0b": "trecut",
                         "D 0b": "trecut"}
    etichete = sorted(f.stem for f in (s.lucru / "cod_v02" / "inghet").glob("*.zip"))
    assert etichete == ["v02_A_0a", "v02_A_0b", "v02_B_0a", "v02_B_0b", "v02_D_0a", "v02_D_0b", "v02_inainte_de_pilot"]
    assert not (s.lucru / "cod" / "runde.jsonl").exists() and (s.lucru / "cod_v02" / "runde.jsonl").exists()
    pornire = next(r for r in jurnal(s) if r["tip"] == "pilot_inceput")
    assert pornire["versiune"] == "v0.2" and pornire["fractie_povesti"] == 0.7
    assert raport_cod.main(["--director-lucru", str(s.lucru), "--dosar", "cod_v02"]) == 0
    assert "Versiunea v0.2, în lucru/cod_v02; 70% povești" in (s.lucru / "cod_v02" / "raport.md").read_text(encoding="utf-8")


def test_v02_un_nivel_fara_set_sacru_nu_arata_sacru_0(tmp_path):
    """0a n-are set sacru: la îngheț, sacrul e None („—”), nu 0%."""
    s = scoala_v02(tmp_path, {"buget.runde_pe_nivel": 1})
    elevi = elevi_de_proba(s)
    s.pregateste()
    elevi["A"] = ElevDeProba({})  # nu știe nimic: pică 0a după o rundă
    assert s.nivel("A", "0a") == "picat"
    picat = s.stare()["linii"]["A"]["niveluri_picate"]["0a"]
    assert picat["sacru"] is None and picat["adversarial"] == 0.0
    assert "sacru — (doar pentru raport)" in jurnal(s)[-1]["motiv"]
    assert "| 0a | ✗ 0% / 0% / 0% / — |" in raport_cod.raport(s.cod)
