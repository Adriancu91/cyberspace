"""CONTINUUM, bucla întreagă (fără placă video, cu module și unelte de probă):
- simulat și pe bune;
- cu 0 module, 1 modul și un modul care cade sau e scos și reintrodus în timpul rulării;
- cu omul la laptop, cu o etapă care cade și cu butonul STOP.
"""

from __future__ import annotations

import json
import sys
import uuid

import pytest

from module.continuum import INVATARE, REPAUS, SUCCES
from module.continuum import bucla as bucla_continuum
from module.continuum.bucla import Bucla, main
from teste.continuum_proba import (Lume, ModulCareCade, config_continuum, config_kronos, noaptea_3, scrie_hrana,
                                   scrie_unelte)


@pytest.fixture
def proiect(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    scrie_unelte(tmp_path)
    return tmp_path


def dupa_fiecare_ciclu(*actiuni):
    """În pauza de după ciclul k rulează a k-a acțiune (dacă există): schimbă lumea în timpul rulării."""
    pasi = iter(actiuni)

    def dormi(_secunde):
        actiune = next(pasi, None)
        if actiune:
            actiune()
    return dormi


def ruleaza(radacina, cicluri, lume=None, simuleaza=True, dormi=None, **setari):
    iesire: list[str] = []
    bucla = Bucla(config_continuum(radacina, **setari), simuleaza=simuleaza, senzori=(lume or Lume()).senzori(),
                  dormi=dormi or dupa_fiecare_ciclu(), iesire=iesire.append)
    assert bucla.ruleaza(cicluri) == 0
    randuri = [json.loads(r) for r in (radacina / "lucru" / "continuum" / "cicluri.jsonl").read_text(
        encoding="utf-8").splitlines()]
    return bucla, randuri, iesire


def test_o_noapte_simulata_spune_doar_ce_ar_alege(proiect):
    noaptea_3(proiect)
    scrie_hrana(proiect)
    config_kronos(proiect, "laptop_fapte.toml", "fapte_1", date=', hrana = "date/fapte/povesti.txt"')
    jurnal_kronos = (proiect / "lucru" / "jurnal" / "experimente.jsonl").read_bytes()
    bucla, randuri, iesire = ruleaza(proiect, 2)
    assert [r["ciclu"] for r in randuri] == [1, 2] and all(r["simulat"] and "eroare" not in r for r in randuri)
    rand = randuri[0]
    assert rand["nivel"] == INVATARE and rand["nevoie"] == "dezvolta:fapte"
    assert rand["comenzi"][0].startswith("python unelte/antrenare_lunga.py --config config/laptop_fapte.toml")
    assert rand["pe_scurt"] == (
        "ÎNVĂȚARE: e fereastra de învățare (22:00–07:00), placa e liberă (5.800 MB liberi, 50 °C), omul n-a mai atins "
        "laptopul de 60 min; azi 0,0 ore pe placă din 20. Aleg dezvolta:fapte: fapte = 27% (41 din 150), cea mai slabă "
        "capacitate (sens = 47%); "
        "7.520 de povești nefolosite în date/fapte. [simulat] Aș porni: antrenare lungă cu config/laptop_fapte.toml "
        "(linia fapte_1, 8 × 60 min, din modelul #8).")
    assert iesire[0].startswith("[23:30] #1 ÎNVĂȚARE:")
    # Nimic pornit: jurnalul Kronos e neatins, nu există ieșiri de unelte, iar încrederea nu s-a schimbat.
    assert (proiect / "lucru" / "jurnal" / "experimente.jsonl").read_bytes() == jurnal_kronos
    assert not (proiect / "lucru" / "continuum" / "actiuni").exists()
    stare = json.loads((proiect / "lucru" / "continuum" / "stare.json").read_text(encoding="utf-8"))
    assert stare["ciclu"] == 2 and stare["strategii"] == {} and stare["experimente"] == []
    assert stare["capacitati"]["fapte"]["linie_de_baza"] == 41 and stare["capacitati"]["fapte"]["experiment_baza"] == 8


def test_cu_zero_module_merge_dar_n_are_ce_alege(proiect):
    _, randuri, _ = ruleaza(proiect, 3, module={})
    assert len(randuri) == 3 and all("eroare" not in r for r in randuri)
    assert randuri[-1]["pe_scurt"].endswith("Nicio nevoie acum.")


def test_cu_un_singur_modul(proiect):
    noaptea_3(proiect, masurat=False)
    _, randuri, _ = ruleaza(proiect, 1, lume=Lume(ora="12:00"), module={"model": "teste.continuum_proba:ModulSanatos"})
    rand = randuri[0]
    assert "eroare" not in rand and rand.get("nevoie") is None
    assert rand["organism"]["capacitati"]["povesti"]["disponibila"]
    assert rand["sarite"][0]["de_ce_nu"].startswith("capacitate_indisponibila: niciun examen nu se poate da")


def test_un_modul_care_cade_in_timpul_rularii(proiect):
    noaptea_3(proiect)

    def strica():
        ModulCareCade.cade = True

    def repara():
        ModulCareCade.cade = False

    try:
        bucla, randuri, _ = ruleaza(proiect, 3, dormi=dupa_fiecare_ciclu(strica, repara))
    finally:
        ModulCareCade.cade = False
    stari = [r["observat"]["module"]["profesor"]["stare"] for r in randuri]
    assert stari == ["ok", "cazut", "ok"] and all("eroare" not in r for r in randuri)
    assert randuri[1]["organism"]["capacitati"]["sens"]["disponibila"] is False
    problema = bucla.memorie["probleme"][0]
    assert problema["cheie"] == "modul:profesor" and "placa a dispărut" in problema["ce"]
    assert (problema["de_la"], problema["rezolvata"]) == (randuri[1]["timp"], randuri[2]["timp"])


def test_un_modul_scos_si_reintrodus_in_timpul_rularii(proiect, monkeypatch):
    pachet = f"pachet_bucla_{uuid.uuid4().hex[:8]}"
    (proiect / pachet).mkdir()
    (proiect / pachet / "__init__.py").write_text("", encoding="utf-8")
    fisier = proiect / pachet / "profesor.py"
    fisier.write_text('class Profesor:\n    MANIFEST = {"nume": "p", "port": "profesor", "versiune": "1", '
                      '"versiune_contract": 1}\n', encoding="utf-8")
    monkeypatch.syspath_prepend(str(proiect))
    module = {"model": "teste.continuum_proba:ModulSanatos", "profesor": f"{pachet}.profesor:Profesor"}
    try:
        _, randuri, _ = ruleaza(proiect, 3, module=module, dormi=dupa_fiecare_ciclu(
            lambda: fisier.rename(proiect / "deoparte.py"), lambda: (proiect / "deoparte.py").rename(fisier)))
    finally:
        for nume in [n for n in sys.modules if n.startswith(pachet)]:
            del sys.modules[nume]
    assert [r["observat"]["module"]["profesor"]["stare"] for r in randuri] == ["ok", "indisponibil", "ok"]
    assert all("eroare" not in r for r in randuri)


def test_omul_la_laptop_pune_bucla_in_repaus(proiect):
    noaptea_3(proiect, masurat=False)
    lume = Lume()

    def vine_omul():
        lume.om_minute = 1

    def pleaca_omul():
        lume.om_minute = 30

    _, randuri, _ = ruleaza(proiect, 3, lume=lume, dormi=dupa_fiecare_ciclu(vine_omul, pleaca_omul))
    assert [r["nivel"] for r in randuri] == [INVATARE, REPAUS, INVATARE]
    assert randuri[1]["pe_scurt"].startswith("REPAUS: omul folosește laptopul")
    assert randuri[1]["pe_scurt"].endswith("Nevoi în așteptare: masoara:fapte+sens, continua:povesti.")


def test_stop_opreste_bucla_ca_pe_kronos(proiect, capsys):
    noaptea_3(proiect)
    stop = proiect / "lucru" / "STOP"
    _, randuri, iesire = ruleaza(proiect, None, dormi=dupa_fiecare_ciclu(lambda: stop.write_text("", encoding="utf-8")))
    assert len(randuri) == 2 and randuri[-1]["oprit"] and randuri[-1]["pe_scurt"].startswith("Oprit: butonul STOP")
    config = str(proiect / "config" / "continuum.toml")
    assert main(["--config", config, "--simuleaza"]) == 1  # cu STOP apăsat nici nu pornește
    assert "python -m kronos porneste" in capsys.readouterr().out


def test_o_etapa_care_cade_nu_opreste_bucla(proiect, monkeypatch):
    noaptea_3(proiect)
    adevarata, apeluri = bucla_continuum.nevoi, []

    def nevoi_care_cad_o_data(*argumente):
        apeluri.append(1)
        if len(apeluri) == 1:
            raise ValueError("bum în nevoi")
        return adevarata(*argumente)

    monkeypatch.setattr(bucla_continuum, "nevoi", nevoi_care_cad_o_data)
    bucla, randuri, _ = ruleaza(proiect, 2)
    assert randuri[0]["eroare"] == {"etapa": "nevoi", "mesaj": "ValueError: bum în nevoi"}
    assert randuri[0]["pe_scurt"] == "Ciclul s-a încheiat la etapa nevoi: ValueError: bum în nevoi. Urmează ciclul următor."
    assert "eroare" not in randuri[1]
    problema = bucla.memorie["probleme"][0]
    assert problema["cheie"] == "etapa:nevoi" and not problema["deschisa"]


def test_o_configurare_stricata_in_timpul_rularii(proiect):
    noaptea_3(proiect)
    cale = proiect / "config" / "continuum.toml"
    _, randuri, _ = ruleaza(proiect, 2, dormi=dupa_fiecare_ciclu(lambda: cale.write_text("[continuum\n", encoding="utf-8")))
    assert all("eroare" not in r for r in randuri)  # merge mai departe cu configurarea de dinainte
    stare = json.loads((proiect / "lucru" / "continuum" / "stare.json").read_text(encoding="utf-8"))
    assert stare["probleme"][0]["cheie"] == "configurare" and stare["probleme"][0]["deschisa"]


def test_o_zi_pe_bune_examenele_lipsa(proiect):
    noaptea_3(proiect, masurat=False)
    scrie_hrana(proiect)
    bucla, randuri, _ = ruleaza(proiect, 2, lume=Lume(ora="12:00"), simuleaza=False)
    rand = randuri[0]
    assert rand["nevoie"] == "masoara:fapte+sens" and rand["verdict"] == SUCCES
    assert rand["fise"] == [9, 10] and rand["motiv_verdict"] == "modelul #8 are acum: fapte 33, sens 5,1"
    assert [c["cod"] for c in rand["rezultat"]["comenzi"]] == [0, 0]
    assert randuri[1].get("nevoie") is None  # măsurat; hrana e gata, iar antrenarea se face noaptea
    assert bucla.memorie["strategii"]["masoara:examene"]["succese"] == 1


def test_o_noapte_pe_bune_pe_fapte(proiect):
    """Trei cicluri pe bune (v1). 1: antrenarea pe fapte iese mai bună (41 → 57 în 8 ore); fiecare oră e confirmată de
    ora păstrată de după ea, deci încrederea urcă, iar linia de bază ajunge la 55 (#17); ultima oră (#18) rămâne
    candidat. 2: remăsurarea lui #18 (unealta de examen dă 33, nu 57) îl infirmă. 3: cu 33, faptele sunt în zona roșie
    și omul primește un raport, cu modelul #17 la care s-ar întoarce."""
    noaptea_3(proiect)
    scrie_hrana(proiect)
    config_kronos(proiect, "laptop_fapte.toml", "fapte_1", date=', hrana = "date/fapte/povesti.txt"')
    bucla, randuri, _ = ruleaza(proiect, 3, simuleaza=False)
    rand = randuri[0]
    assert rand["nevoie"] == "dezvolta:fapte" and rand["verdict"] == SUCCES and rand["fise"] == list(range(11, 19))
    assert rand["inainte"]["fapte"] == 41 and rand["dupa"]["fapte"] == 57  # 41 + 2 pe oră, 8 ore
    assert rand["motiv_verdict"] == ("fapte: 41 → 57, mai bine cu mai mult decât pragul de 3; orele #12 … #17 (6) "
                                     "sunt confirmate de orele păstrate de după: linia de bază e acum 55 (#17)")
    assert rand["cost"]["ore_placa"] < 0.01 and rand["castig_pe_ora"] > 0  # unealta de probă durează o clipă
    argumente = json.loads((proiect / "lucru" / "jurnal" / "argumente.json").read_text(encoding="utf-8"))
    assert argumente == ["--config", "config/laptop_fapte.toml", "--ore", "8", "--porneste-din", "8"]
    experiment = bucla.memorie["experimente"][0]
    assert experiment["strategie"] == "dezvolta:fapte:antrenare" and experiment["model_inainte"] == 8
    assert experiment["cel_mai_bun_inainte"] == {"povesti": 8, "fapte": 8, "sens": 8}  # de unde se poate reveni
    assert experiment["confirmare"] is None  # confirmat pe loc, de orele de după
    # A doua oară: remăsurarea care ar confirma ultima oră (hrana e folosită, iar val_bpb nu mai scade destul).
    assert randuri[1]["nevoie"] == "remasoara:fapte" and randuri[1]["verdict"] == SUCCES
    assert randuri[1]["actiune"] == "remăsurare (confirmare): examenul fapte din nou pe modelul #18"
    candidat = next(k for k in bucla.memorie["candidati"] if k["capacitate"] == "fapte" and k["experiment"] == 18)
    assert candidat["stare"] == "neconfirmat" and candidat["infirmat_de"] == "a doua măsurătoare a modelului #18"
    strategie = bucla.memorie["strategii"]["dezvolta:fapte:antrenare"]
    assert (strategie["succese"], strategie["neconcludente"], strategie["in_asteptare"], strategie["incredere"]) == (1, 0, 0, 0.6)
    baza = bucla.memorie["capacitati"]["fapte"]
    assert (baza["linie_de_baza"], baza["experiment_baza"]) == (55, 17)  # nu urcă la 57: #18 n-a fost confirmat
    # A treia oară: faptele (33 pe #18) sunt cu 22 sub linia de bază, peste 2 praguri de 3: zona roșie, raport.
    assert randuri[2]["nevoie"] == "repara:fapte" and randuri[2]["fel"] == "raport"
    raport = proiect / randuri[2]["rezultat"]["raport"]
    assert raport.name == "ciclu_00003_repara_fapte.md" and "Modelul păstrat la care s-ar întoarce: #17" in raport.read_text(
        encoding="utf-8")
    assert bucla.memorie["rapoarte"][0]["deschis"] and "racire" not in randuri[2]  # „repara” n-are răcire


def test_jurnalul_ciclurilor_se_citeste_pe_scurt(proiect, capsys):
    noaptea_3(proiect)
    ruleaza(proiect, 2)
    assert main(["--config", str(proiect / "config" / "continuum.toml"), "--jurnal", "1"]) == 0
    iesire = capsys.readouterr().out.strip().splitlines()
    assert len(iesire) == 1 and iesire[0].startswith("#2  2026-10-07 23:30  ÎNVĂȚARE:")


def test_aceeasi_pauza_pe_orice_nivel(proiect):
    noaptea_3(proiect)
    pauze: list[float] = []
    bucla = Bucla(config_continuum(proiect), simuleaza=True, senzori=Lume(om_minute=1).senzori(), dormi=pauze.append,
                  iesire=lambda _: None, pauza_minute=15)
    bucla.ruleaza(2)
    assert pauze == [900]  # o zi simulată, un ciclu la 15 minute (în REPAUS, configurarea de probă are 0)


def test_configurarea_adevarata():
    from module.continuum import citeste_config
    from teste.continuum_proba import RADACINA

    config = citeste_config(RADACINA / "config" / "continuum.toml")
    # Fișierul are ordinea din v0; v1 pune singur „repara” prima și „remasoara” după „masoara”.
    assert config["continuum"]["ordinea_nevoilor"] == ["repara", "masoara", "remasoara", "dezvolta", "continua"]
    assert config["guvernator"]["fereastra_invatare"][0].hour == 0  # laptopul e al lui Kronos toată ziua
    assert config["guvernator"]["minute_fara_om"] == 10 and config["guvernator"]["buget_ore_placa_pe_zi"] == 20
    assert (config["zgomot"], config["zone"], config["stabilitate"], config["eficienta"], config["anti_bucla"]) == (
        {"perechi_minime": 3, "factor": 1.0, "minute_minime": 60}, {"galben": 1.0, "rosu": 2.0}, {"confirmari": 1},
        {"fractie_scump": 0.5}, {"racire_cicluri": 6, "max_esecuri": 5})
    assert config["capacitati"]["sens"]["povesti"] == 40
    assert config["nevoi"]["continua"]["ore_tendinta"] == 3
    assert {n: c["prag_zgomot"] for n, c in config["capacitati"].items()} == {"povesti": 0.005, "fapte": 10, "sens": 0.5}
    assert "40" in config["capacitati"]["sens"]["masurare"]


def test_ca_la_o_ora_de_noapte_fara_om(proiect, monkeypatch):
    noaptea_3(proiect)
    scrie_hrana(proiect)
    config_kronos(proiect, "laptop_fapte.toml", "fapte_1", date=', hrana = "date/fapte/povesti.txt"')
    config = str(config_continuum(proiect))
    monkeypatch.setattr("module.continuum.observa.citeste_placa", Lume().placa)  # fără nvidia-smi în teste
    assert main(["--config", config, "--ca-la", "23:00"]) == 1  # nu merge pe bune
    assert main(["--config", config, "--simuleaza", "--ca-la", "25:00"]) == 1
    assert main(["--config", config, "--simuleaza", "--ca-la", "23"]) == 0  # „23” înseamnă 23:00
    rand = json.loads((proiect / "lucru" / "continuum" / "cicluri.jsonl").read_text(encoding="utf-8").splitlines()[-1])
    assert rand["ca_la"] == "23:00" and rand["nevoie"] == "dezvolta:fapte"
    assert rand["pe_scurt"].startswith("[ca la 23:00, fără om] ÎNVĂȚARE: e fereastra de învățare")
