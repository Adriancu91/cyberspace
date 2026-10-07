"""CONTINUUM v1, punct cu punct (fără placă video, cu proiectul de probă din teste/continuum_proba.py):
1. zgomotul învățat; 2. cele trei zone; 3. stabilitatea pe două niveluri; 4. verdictul cu eficiență;
5. vectorul capacităților; 6. regula „continuă” cu temei; 7. anti-bucla. La final: configurarea veche merge neschimbată.
"""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from module.continuum import (ESEC, GALBENA, INTRETINERE, REPAUS, ROSIE, SUCCES, SUCCES_SCUMP, VERDE, EroareContinuum,
                              citeste_config)
from module.continuum.alege import alege
from module.continuum.bucla import Bucla
from module.continuum.evalueaza import Capacitate, evalueaza, zona
from module.continuum.guvernator import nivel
from module.continuum.invata import dupa_confirmare, invata
from module.continuum.masoara import masoara
from module.continuum.nevoi import nevoi
from module.continuum.observa import descopera_module, observa
from module.continuum.stare import memorie_goala
from module.continuum import stabilitate
from teste.continuum_proba import (CONFIG_CONTINUUM, Lume, config_continuum, config_kronos, fisa, fisa_unealta,
                                   noaptea_3, scrie_hrana, scrie_jurnal, scrie_unelte)
from teste.test_continuum_masoara import REUSIT, antrenare
from teste.test_continuum_masoara import stare as stare_de_proba


@pytest.fixture
def proiect(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    scrie_unelte(tmp_path)
    return tmp_path


def evaluat(radacina, lume=None, memorie=None, **setari):
    config = citeste_config(config_continuum(radacina, **setari))
    return config, evalueaza(observa(config, descopera_module(config), (lume or Lume()).senzori()), config, memorie)


def nevoile(radacina, lume=None, memorie=None, **setari):
    config, stare = evaluat(radacina, lume, memorie, **setari)
    return {n.cheie: n for n in nevoi(stare, config, memorie)}


def ruleaza(radacina, cicluri, lume=None, simuleaza=True, dupa_ciclu=(), **setari):
    pasi = iter(dupa_ciclu)

    def dormi(_secunde):
        actiune = next(pasi, None)
        if actiune:
            actiune()

    bucla = Bucla(config_continuum(radacina, **setari), simuleaza=simuleaza, senzori=(lume or Lume()).senzori(),
                  dormi=dormi, iesire=lambda _: None)
    assert bucla.ruleaza(cicluri) == 0
    randuri = [json.loads(r) for r in (radacina / "lucru" / "continuum" / "cicluri.jsonl").read_text(
        encoding="utf-8").splitlines()]
    return bucla, randuri


def seminte(radacina, valori, linie="cautare", id_de_la=101):
    """Aceeași configurare, semințe diferite (pe o linie neurmărită: doar zgomotul le folosește)."""
    scrie_jurnal(radacina, [fisa(id_de_la + i, linie, v, decizie="respins", samanta=i + 1) for i, v in enumerate(valori)])


def linia_4(radacina, *ore, id_de_la=11):
    """Ore noi pe linia antrenare_lunga_4: (val_bpb, fapte_corecte, nota_profesor) pentru fiecare."""
    config_kronos(radacina, "laptop_antrenare_lunga_4.toml", "antrenare_lunga_4")
    scrie_jurnal(radacina, [fisa(id_de_la + i, "antrenare_lunga_4", v, criterii={"fapte_corecte": f, "nota_profesor": n})
                            for i, (v, f, n) in enumerate(ore)])


ANTI_BUCLA = {"[comenzi]": "[anti_bucla]\nracire_cicluri = 0\nmax_esecuri = 2\n\n[comenzi]"}


# --- 1. Zgomotul învățat --------------------------------------------------------------------------------------------

def test_sub_perechile_minime_ramane_podeaua(proiect):
    noaptea_3(proiect)
    _, stare = evaluat(proiect)
    vector = stare.vector()
    assert {k: vector["povesti"][k] for k in ("prag_folosit", "podea", "zgomot_invatat", "stare_zgomot", "perechi_zgomot")} \
        == {"prag_folosit": 0.02, "podea": 0.02, "zgomot_invatat": None, "stare_zgomot": "neînvățat încă", "perechi_zgomot": 0}
    seminte(proiect, [0.50, 0.53, 0.49])  # 2 perechi, sub minimul de 3
    _, stare = evaluat(proiect)
    assert (stare.capacitati["povesti"].perechi_zgomot, stare.capacitati["povesti"].stare_zgomot) == (2, "neînvățat încă")
    assert stare.capacitati["povesti"].prag_zgomot == 0.02


def test_zgomotul_din_seminte_ridica_pragul_si_schimba_zona(proiect):
    noaptea_3(proiect)
    linia_4(proiect, (0.4867, 41, 4.7))  # cu 0,03 peste linia de bază 0,4567: 1,5 praguri de 0,02 = zona galbenă
    assert evaluat(proiect)[1].capacitati["povesti"].zona == GALBENA
    seminte(proiect, [0.50, 0.53, 0.49, 0.52])  # diferențe +0,03, −0,04, +0,03: zgomotul ≈ 0,0337
    c = evaluat(proiect)[1].capacitati["povesti"]
    assert (c.perechi_zgomot, c.stare_zgomot, c.zgomot_invatat, c.prag_zgomot) == (3, "învățat", 0.033665, 0.033665)
    assert c.zona == VERDE  # 0,03 e sub pragul învățat: nu mai e de remăsurat


def test_zgomotul_sub_podea_lasa_podeaua(proiect):
    noaptea_3(proiect)
    seminte(proiect, [0.500, 0.501, 0.500, 0.501])
    c = evaluat(proiect)[1].capacitati["povesti"]
    assert (c.stare_zgomot, c.zgomot_invatat, c.prag_zgomot) == ("învățat", 0.001, 0.02)  # prag = max(podea, zgomot)


def test_acelasi_model_examinat_de_mai_multe_ori(proiect):
    noaptea_3(proiect)  # #10: nota 4,7 pe modelul #8
    scrie_jurnal(proiect, [fisa_unealta(11, "examen_profesor", 8, {"nota_medie": 4.2}),
                           fisa_unealta(12, "examen_profesor", 8, {"nota_medie": 4.9}),
                           fisa_unealta(13, "examen_profesor", 8, {"nota_medie": 4.4})])
    c = evaluat(proiect)[1].capacitati["sens"]
    assert (c.perechi_zgomot, c.zgomot_invatat, c.prag_zgomot, c.zgomot_remasurare) == (3, 0.574456, 0.574456, 0.574456)
    assert c.curent == 4.4 and c.masuratori == 4  # ultima măsurătoare a uneltei; modelul a fost măsurat de 4 ori


def test_regula_continua_nu_foloseste_zgomotul_dintre_seminte(proiect):
    """Două ore ale aceleiași antrenări au aceeași sămânță: pragul regulii rămâne castig_minim (0,005)."""
    noaptea_3(proiect)
    seminte(proiect, [0.50, 0.53, 0.49, 0.52])
    config, stare = evaluat(proiect)
    assert stare.capacitati["povesti"].prag_zgomot == 0.033665 and stare.tendinta["prag"] == 0.005
    assert "continua:povesti" in {n.cheie for n in nevoi(stare, config)}


# --- 2. Cele trei zone ----------------------------------------------------------------------------------------------

def test_cele_trei_zone_fata_de_linia_de_baza():
    reguli = {"galben": 1.0, "rosu": 2.0}

    def fapte(curent):
        return Capacitate("fapte", "fapte_corecte", True, 3, 150, True, None, linie_de_baza=41, curent=curent)

    assert [zona(fapte(v), reguli) for v in (50, 41, 38, 37, 35, 34)] == [VERDE, VERDE, VERDE, GALBENA, GALBENA, ROSIE]
    povesti = Capacitate("povesti", "val_bpb", False, 0.005, None, True, None, linie_de_baza=0.45, curent=0.47)
    assert zona(povesti, reguli) == ROSIE  # val_bpb mai mare = mai rău: 4 praguri
    assert zona(fapte(None), reguli) is None  # nemăsurată
    assert zona(fapte(38), {"galben": 0.5, "rosu": 1.5}) == GALBENA  # pragurile zonelor vin din configurare


def test_zona_galbena_cere_o_remasurare_o_singura_data(proiect):
    noaptea_3(proiect)
    linia_4(proiect, (0.4567, 36, 4.7))  # fapte: 5 sub 41, între 1 și 2 praguri de 3
    gasite = nevoile(proiect)
    assert "repara:fapte" not in gasite
    assert gasite["remasoara:fapte"].urgenta == 3 and gasite["remasoara:fapte"].motiv == (
        "zona galbenă: fapte = 36, sub linia de bază 41 (#8) cu 5, adică 1,67 praguri (pragul folosit: 3); cer o "
        "remăsurare, nu o acțiune")
    config, stare = evaluat(proiect, Lume(ora="12:00"))
    alegere = alege(nevoi(stare, config), stare, config)
    assert alegere.plan.descriere == "remăsurare (zona galbenă): examenul fapte din nou pe modelul #11"
    assert alegere.plan.comenzi[0][1:] == ["unelte/examen_fapte.py", "--experiment", "11"]
    scrie_jurnal(proiect, [fisa_unealta(12, "examen_fapte", 11, {"corecte_doar_cuvantul_din_fapt": 36})])
    assert "remasoara:fapte" not in nevoile(proiect)  # remăsurat: rămâne galben, dar nu se cere din nou


def test_zona_rosie_raport_catre_om_o_singura_data(proiect):
    noaptea_3(proiect)
    linia_4(proiect, (0.4567, 28, 4.7))  # fapte: 13 sub 41, peste 2 praguri de 3
    gasite = nevoile(proiect)
    repara = gasite["repara:fapte"]
    assert repara.urgenta == 1 and repara.detalii["model_de_intoarcere"] == 8
    assert repara.motiv == ("zona roșie: fapte = 28, sub linia de bază 41 (#8) cu 13, adică 4,33 praguri (pragul folosit: "
                            "3); modelul păstrat la care s-ar întoarce: #8")
    # Pe bune, în REPAUS (omul e la laptop): raportul se scrie oricum, o singură dată; altceva nu pornește.
    fapte_bune = lambda: scrie_jurnal(proiect, [fisa(12, "antrenare_lunga_4", 0.4567,  # noqa: E731
                                                     criterii={"fapte_corecte": 41, "nota_profesor": 4.7})])
    bucla, randuri = ruleaza(proiect, 3, lume=Lume(om_minute=1), simuleaza=False, dupa_ciclu=(None, fapte_bune))
    assert randuri[0]["nivel"] == REPAUS and randuri[0]["nevoie"] == "repara:fapte"
    raport = (proiect / randuri[0]["rezultat"]["raport"]).read_text(encoding="utf-8")
    assert "Scorul acum: 28 (fapte_corecte), pe modelul #11 (linia antrenare_lunga_4)" in raport
    assert "Modelul păstrat la care s-ar întoarce: #8, salvat de Kronos." in raport
    assert randuri[1].get("nevoie") is None
    assert {s["nevoie"]: s["de_ce_nu"] for s in randuri[1]["sarite"]}["repara:fapte"].startswith(
        "nu acum: raportul pentru fapte e trimis (ciclul 1")
    # Faptele revin (41 pe #12): raportul se închide; o nouă cădere ar aduce unul nou.
    trimis = bucla.memorie["rapoarte"][0]
    assert (trimis["deschis"], trimis["inchis"], trimis["zona_la_inchidere"]) == (False, randuri[2]["timp"], VERDE)


# --- 3. Stabilitatea pe două niveluri -------------------------------------------------------------------------------

def test_un_scor_mai_bun_e_intai_candidat_apoi_confirmat(proiect):
    noaptea_3(proiect)
    config_kronos(proiect, "laptop_antrenare_lunga_4.toml", "antrenare_lunga_4")
    ora_11 = lambda: scrie_jurnal(proiect, [fisa(11, "antrenare_lunga_4", 0.4567,  # noqa: E731
                                                 criterii={"fapte_corecte": 50, "nota_profesor": 4.7})])
    ora_12 = lambda: scrie_jurnal(proiect, [fisa(12, "antrenare_lunga_4", 0.4567,  # noqa: E731
                                                 criterii={"fapte_corecte": 49, "nota_profesor": 4.7})])
    bucla, randuri = ruleaza(proiect, 3, dupa_ciclu=(ora_11, ora_12))
    stare_json = lambda: json.loads((proiect / "lucru" / "continuum" / "stare.json").read_text(encoding="utf-8"))  # noqa: E731
    # Ciclul 2: 50 de fapte pe #11, cu 9 peste linia de bază 41: candidat, iar linia de bază nu se mută încă.
    assert randuri[1]["candidati"] == ["fapte = 50 pe #11, peste linia de bază 41 (#8) cu 9, mai mult decât pragul 3; "
                                       "aștept o a doua măsurătoare"]
    # Ciclul 3: #12, o oră păstrată mai nouă de pe aceeași linie, are 49: confirmă; linia de bază e cea mai slabă (49).
    candidat = stare_json()["candidati"][0]
    assert (candidat["stare"], candidat["confirmat_de"], candidat["de_la"]) == (
        "confirmat", "modelul păstrat mai nou #12", randuri[1]["timp"])
    assert candidat["motiv"].endswith("confirmat de modelul păstrat mai nou #12 (49); linia de bază: 49")
    baza = stare_json()["capacitati"]["fapte"]
    assert (baza["linie_de_baza"], baza["experiment_baza"], baza["sursa_bazei"]) == (
        49, 11, "confirmată de modelul păstrat mai nou #12")


def test_un_candidat_infirmat_nu_muta_linia_de_baza(proiect):
    noaptea_3(proiect)
    config_kronos(proiect, "laptop_antrenare_lunga_4.toml", "antrenare_lunga_4")
    ore = lambda: scrie_jurnal(proiect, [  # noqa: E731
        fisa(11, "antrenare_lunga_4", 0.4567, criterii={"fapte_corecte": 50, "nota_profesor": 4.7}),
        fisa(12, "antrenare_lunga_4", 0.4567, criterii={"fapte_corecte": 42, "nota_profesor": 4.7})])
    bucla, _ = ruleaza(proiect, 2, dupa_ciclu=(ore,))
    # #12 e ultimul model (42): nu e candidat; #11 (50) n-a fost văzut ca ultim model, deci nici el.
    assert bucla.memorie["candidati"] == [] and bucla.memorie["capacitati"]["fapte"]["linie_de_baza"] == 41
    memorie = memorie_goala()
    memorie["candidati"].append({"capacitate": "fapte", "experiment": 11, "linie": "antrenare_lunga_4", "valoare": 50,
                                 "referinta": 41, "experiment_referinta": 8, "prag": 3, "muta_baza": True,
                                 "stare": "candidat", "motiv": "50 pe #11; aștept o a doua măsurătoare"})
    config = citeste_config(proiect / "config" / "continuum.toml")
    fise = [json.loads(r) for r in (proiect / "lucru" / "jurnal" / "experimente.jsonl").read_text(
        encoding="utf-8").splitlines()]
    schimbari = stabilitate.actualizeaza(memorie, fise, config, "t")
    assert schimbari[0]["stare"] == "neconfirmat" and schimbari[0]["motiv"] == (
        "50 pe #11; neconfirmat: modelul păstrat mai nou #12 are 42")
    assert memorie["capacitati"] == {}  # linia de bază nu s-a mutat


def test_increderea_urca_doar_dupa_confirmare(proiect):
    """Pe bune, o antrenare de o singură oră: 41 → 51 de fapte. N-are o oră de după care s-o confirme, deci încrederea
    așteaptă; la ciclul următor, remăsurarea dă tot 51 și confirmă: abia atunci urcă încrederea și linia de bază."""
    scrie_unelte(proiect, pas_fapte=10, fapte_examen=51)
    noaptea_3(proiect)
    scrie_hrana(proiect)
    config_kronos(proiect, "laptop_fapte.toml", "fapte_1", ore=1, date=', hrana = "date/fapte/povesti.txt"')
    bucla, randuri = ruleaza(proiect, 1, simuleaza=False)
    assert randuri[0]["nevoie"] == "dezvolta:fapte" and randuri[0]["verdict"] == SUCCES
    assert randuri[0]["motiv_verdict"].endswith("; e un candidat: încrederea urcă după a doua măsurătoare")
    strategie = bucla.memorie["strategii"]["dezvolta:fapte:antrenare"]
    assert (strategie["succese"], strategie["in_asteptare"], strategie["incredere"]) == (0, 1, 0.5)
    assert bucla.memorie["experimente"][0]["confirmare"] == "în așteptarea unei a doua măsurători"
    assert bucla.memorie["capacitati"]["fapte"]["linie_de_baza"] == 41
    bucla, randuri = ruleaza(proiect, 1, simuleaza=False)  # o buclă nouă: pornește din stare.json
    assert randuri[1]["nevoie"] == "remasoara:fapte" and randuri[1]["verdict"] == SUCCES
    strategie = bucla.memorie["strategii"]["dezvolta:fapte:antrenare"]
    assert (strategie["succese"], strategie["in_asteptare"], strategie["incredere"]) == (1, 0, 0.6)
    assert (bucla.memorie["capacitati"]["fapte"]["linie_de_baza"], bucla.memorie["capacitati"]["fapte"]["experiment_baza"]) \
        == (51, 11)
    assert "confirmat de a doua măsurătoare a modelului #11 (51); linia de bază: 51" in randuri[1]["pe_scurt"]


# --- 4. Verdictul cu eficiență ------------------------------------------------------------------------------------

def test_masoara_ia_costul_actiunii():
    fise = [{"id": 11, "decizie": "pastrat", "statistici_antrenare": {"pasi": 27000, "secunde_bucla": 3600,
                                                                      "memorie_rezervata_mb": 2226}},
            {"id": 12, "decizie": "pastrat", "statistici_antrenare": {"pasi": 25200, "secunde_bucla": 3600,
                                                                      "memorie_rezervata_mb": 2300}},
            {"id": 9, "decizie": "pastrat", "statistici_antrenare": {"pasi": 1, "secunde_bucla": 1}}]  # de dinainte
    rezultat = {**REUSIT, "comenzi": [{"comanda": "python", "cod": 0, "secunde": 7200.0}]}
    m = masoara(antrenare(), stare_de_proba(10, 8, 0.4567, 41, 4.7), stare_de_proba(12, 12, 0.4500, 50, 4.7), rezultat,
                fise)
    assert m["cost"] == {"secunde_placa": 7200.0, "ore_placa": 2.0, "pasi_pe_secunda": 7.25, "memorie_video_mb": 2300}
    assert m["verdict"] == SUCCES and m["castig_pe_ora"] == 4.5  # 9 fapte în 2 ore


def test_succes_scump_nu_urca_increderea():
    config = {"invatare": {"incredere_initiala": 0.5, "pas_incredere": 0.1}, "eficienta": {"fractie_scump": 0.5},
              "anti_bucla": {"racire_cicluri": 6, "max_esecuri": 5}}
    memorie = memorie_goala()
    memorie["strategii"]["dezvolta:fapte:antrenare"] = {"incredere": 0.6, "succese": 2, "esecuri": 0, "neconcludente": 0,
                                                       "stare": "activa", "castiguri_pe_ora": [10.0, 12.0]}
    rezultat = {**REUSIT, "comenzi": [{"secunde": 7200.0}]}
    m = masoara(antrenare(), stare_de_proba(10, 8, 0.4567, 41, 4.7), stare_de_proba(12, 12, 0.4567, 50, 4.7), rezultat,
                [], memorie, config)
    assert m["verdict"] == SUCCES_SCUMP and m["castig_pe_ora"] == 4.5  # sub 50% din media 11
    assert m["motiv"] == ("fapte: 41 → 50, mai bine cu mai mult decât pragul de 3; dar câștigul pe oră de placă (4,5) e "
                          "sub 50% din media strategiei (11): SUCCES SCUMP, încrederea nu urcă")
    invata(memorie, antrenare(), m, config, 5, "t")
    strategie = memorie["strategii"]["dezvolta:fapte:antrenare"]
    assert (strategie["incredere"], strategie["succese"], strategie["succese_scumpe"]) == (0.6, 2, 1)
    assert strategie["castiguri_pe_ora"] == [10.0, 12.0, 4.5]
    ieftin = masoara(antrenare(), stare_de_proba(10, 8, 0.4567, 41, 4.7), stare_de_proba(12, 12, 0.4567, 60, 4.7),
                     rezultat, [], memorie, config)
    assert ieftin["verdict"] == SUCCES  # 9,5 pe oră: peste 50% din media 8,83


# --- 5. Vectorul capacităților -------------------------------------------------------------------------------------

def test_vectorul_are_toate_capacitatile_si_cele_nemasurate(proiect):
    noaptea_3(proiect, masurat=False)
    bucla, _ = ruleaza(proiect, 1)
    vector = bucla.memorie["vector_capacitati"]
    assert list(vector) == ["povesti", "fapte", "sens"]
    assert {k: vector["fapte"][k] for k in ("masurata", "scor", "zona", "procent", "prag_folosit")} == {
        "masurata": False, "scor": None, "zona": "nemăsurată", "procent": None, "prag_folosit": 3}
    assert {k: vector["povesti"][k] for k in ("masurata", "scor", "linie_de_baza", "zona", "prag_folosit")} == {
        "masurata": True, "scor": 0.4567, "linie_de_baza": 0.4567, "zona": VERDE, "prag_folosit": 0.02}


def test_cea_mai_slaba_capacitate_iese_din_vector(proiect):
    noaptea_3(proiect)
    scrie_jurnal(proiect, [fisa_unealta(11, "examen_profesor", 8, {"nota_medie": 1.0})])
    _, stare = evaluat(proiect)
    vector = stare.vector()
    assert (vector["sens"]["procent"], vector["fapte"]["procent"]) == (10.0, 27.3)
    dezvolta = nevoile(proiect)["dezvolta:sens"]
    assert dezvolta.motiv == "sens = 10% (1 din 10), cea mai slabă capacitate (fapte = 27%); n-are hrană în [hrana]"


# --- 6. Regula „continuă” cu temei ---------------------------------------------------------------------------------

def test_continua_cere_castig_peste_prag_si_tendinta_buna(proiect):
    linia_4(proiect, (0.50, 41, 4.7), (0.45, 41, 4.7), (0.47, 41, 4.7), (0.46, 41, 4.7))
    config, stare = evaluat(proiect)
    assert stare.tendinta["castig"] == pytest.approx(0.01) and stare.tendinta["panta"] == pytest.approx(-0.005)
    assert "continua:povesti" not in nevoile(proiect)  # ultima oră a câștigat, dar pe 3 ore val_bpb a urcat


def test_fara_destule_ore_nu_se_stie_tendinta(proiect):
    linia_4(proiect, (0.50, 41, 4.7), (0.49, 41, 4.7))
    _, stare = evaluat(proiect)
    assert stare.tendinta["castig"] == pytest.approx(0.01) and stare.tendinta["panta"] is None
    assert "continua:povesti" not in nevoile(proiect)


def test_doua_ore_sub_prag_inseamna_saturat_si_dezvolta_trece_in_fata(proiect):
    scrie_hrana(proiect)
    linia_4(proiect, (0.50, 41, 4.7), (0.48, 41, 4.7), (0.478, 41, 4.7), (0.477, 41, 4.7))
    _, stare = evaluat(proiect)
    assert stare.tendinta["saturat"] and stare.tendinta["castiguri"] == pytest.approx([0.02, 0.002, 0.001])
    gasite = nevoile(proiect)
    assert "continua:povesti" not in gasite
    assert gasite["dezvolta:fapte"].urgenta == 4  # înaintea lui „continua” (repara 1, masoara 2, remasoara 3)
    assert gasite["dezvolta:fapte"].motiv.endswith(
        "; povestirile sunt saturate (două ore la rând sub prag), deci dezvoltarea trece în față")


# --- 7. Anti-bucla ----------------------------------------------------------------------------------------------

def test_racirea_nu_reia_o_nevoie_tratata(proiect):
    noaptea_3(proiect, masurat=False)
    config, stare = evaluat(proiect, Lume(ora="12:00"))
    memorie = {**memorie_goala(), "racire": {"masoara:fapte+sens": 7}}
    alegere = alege(nevoi(stare, config), stare, config, memorie, ciclu=5)
    assert alegere.plan is None and alegere.sarite[0] == {
        "nevoie": "masoara:fapte+sens", "de_ce_nu": "în răcire până la ciclul 7 (a fost tratată de curând)"}
    assert alege(nevoi(stare, config), stare, config, memorie, ciclu=8).nevoie.cheie == "masoara:fapte+sens"
    bucla, _ = ruleaza(proiect, 1, lume=Lume(ora="12:00"), simuleaza=False)
    assert bucla.memorie["racire"] == {"masoara:fapte+sens": 7}  # ciclul 1 + 6 cicluri (implicit)


def test_repara_nu_are_racire(proiect):
    noaptea_3(proiect)
    linia_4(proiect, (0.4567, 28, 4.7))
    config, stare = evaluat(proiect)
    memorie = {**memorie_goala(), "racire": {"repara:fapte": 99}}
    assert alege(nevoi(stare, config), stare, config, memorie, ciclu=5).nevoie.cheie == "repara:fapte"


def test_strategia_blocata_dupa_prea_multe_esecuri(proiect):
    noaptea_3(proiect, masurat=False)
    (proiect / "unelte" / "examen_fapte.py").write_text("raise SystemExit(1)\n", encoding="utf-8")
    bucla, randuri = ruleaza(proiect, 3, lume=Lume(ora="12:00"), simuleaza=False, inlocuiri=ANTI_BUCLA)
    assert [r.get("verdict") for r in randuri[:2]] == [ESEC, ESEC]
    strategie = bucla.memorie["strategii"]["masoara:examene"]
    assert (strategie["stare"], strategie["esecuri_la_rand"]) == ("blocată", 2)
    raport = proiect / randuri[1]["rapoarte"][0]
    assert raport.name == "ciclu_00002_blocata_masoara_examene.md"
    assert "A eșuat de 2 ori la rând (limita: 2)" in raport.read_text(encoding="utf-8")
    assert randuri[2].get("nevoie") is None and randuri[2]["sarite"][0] == {
        "nevoie": "masoara:fapte+sens",
        "de_ce_nu": "strategia masoara:examene e blocată după 2 eșecuri la rând; omul a primit un raport"}


def test_bugetul_zilnic_de_ore_pe_placa(proiect):
    config = citeste_config(config_continuum(proiect))
    lume = Lume(ora="23:30")
    azi = [fisa(1, "a", 0.5, inceput="2026-10-07T10:00:00+00:00", durata=36000),
           fisa(2, "a", 0.5, inceput="2026-10-07T11:00:00+00:00", durata=35000)]
    ieri = [fisa(3, "a", 0.5, inceput="2026-10-06T10:00:00+00:00", durata=36000)]

    def observat(fise):
        return SimpleNamespace(timp=lume.timp(), placa=lume.placa(), om=lume.om(), fise=fise)

    ales, motiv = nivel(observat(azi[:1] + ieri), config)
    assert ales != REPAUS and motiv.endswith("; azi 10,0 ore pe placă din 20")
    ales, motiv = nivel(observat(azi + ieri), config)
    assert ales != REPAUS and motiv.endswith("; azi 19,7 ore pe placă din 20")  # ieri nu se pune
    plin = azi + [fisa(4, "a", 0.5, inceput="2026-10-07T12:00:00+00:00", durata=1200)]
    assert nivel(observat(plin), config) == (
        REPAUS, "bugetul de azi pe placă e consumat (20,1 ore din 20): nu mai pornesc nimic până mâine, doar observ")
    assert nivel(observat(plin), citeste_config(config_continuum(proiect, inlocuiri={
        "procese_grele = [\"python\"]": "procese_grele = [\"python\"]\nbuget_ore_placa_pe_zi = 24"})))[0] != REPAUS


# --- Configurarea ----------------------------------------------------------------------------------------------

def test_configurarea_veche_merge_neschimbata(tmp_path):
    """Configurarea de probă e una din v0 (fără nimic din v1): se citește, cu valorile implicite din v1."""
    assert "[zgomot]" not in CONFIG_CONTINUUM and "[nevoi.repara]" not in CONFIG_CONTINUUM
    config = citeste_config(config_continuum(tmp_path))
    assert config["continuum"]["ordinea_nevoilor"] == ["repara", "masoara", "remasoara", "continua", "dezvolta"]
    assert (config["zgomot"], config["zone"], config["stabilitate"], config["eficienta"], config["anti_bucla"]) == (
        {"perechi_minime": 3, "factor": 1.0}, {"galben": 1.0, "rosu": 2.0}, {"confirmari": 1}, {"fractie_scump": 0.5},
        {"racire_cicluri": 6, "max_esecuri": 5})
    assert config["guvernator"]["buget_ore_placa_pe_zi"] == 20 and config["nevoi"]["continua"]["ore_tendinta"] == 3
    assert config["nevoi"]["repara"]["nivel"] == REPAUS
    assert config["nevoi"]["remasoara"] == config["nevoi"]["masoara"]


@pytest.mark.parametrize("inlocuiri, mesaj", [
    ({"[comenzi]": "[zone]\ngalben = 2.0\nrosu = 1.0\n\n[comenzi]"}, "0 < galben < rosu"),
    ({"[comenzi]": "[zgomot]\nperechi_minime = 0\n\n[comenzi]"}, "perechi_minime"),
    ({"[comenzi]": "[anti_bucla]\nmax_esecuri = 0\n\n[comenzi]"}, "max_esecuri"),
    ({'ordinea_nevoilor = ["masoara", "continua", "dezvolta"]': 'ordinea_nevoilor = ["masoara", "reparatii"]'},
     "ordinea_nevoilor"),
])
def test_configurarea_v1_se_verifica(tmp_path, inlocuiri, mesaj):
    with pytest.raises(EroareContinuum, match=mesaj):
        citeste_config(config_continuum(tmp_path, inlocuiri=inlocuiri))


def test_repara_e_mereu_prima(tmp_path):
    config = citeste_config(config_continuum(tmp_path, inlocuiri={
        'ordinea_nevoilor = ["masoara", "continua", "dezvolta"]':
            'ordinea_nevoilor = ["masoara", "repara", "remasoara", "dezvolta", "continua"]'}))
    assert config["continuum"]["ordinea_nevoilor"] == ["repara", "masoara", "remasoara", "dezvolta", "continua"]
    assert config["nevoi"]["repara"]["nivel"] == REPAUS and INTRETINERE in config["nevoi"]["remasoara"]["nivel"]


def test_linia_de_baza_nu_coboara_niciodata():
    """Un candidat vechi, confirmat după ce linia de bază a urcat deja mai sus, n-o trage înapoi în jos."""
    config = {"capacitati": {"fapte": {"metrica": "fapte_corecte", "mai_mare_e_mai_bine": True, "unealta": None}},
              "stabilitate": {"confirmari": 1}}
    memorie = memorie_goala()
    memorie["capacitati"]["fapte"] = {"linie_de_baza": 60, "experiment_baza": 20, "baza_confirmata": True}
    memorie["candidati"].append({"capacitate": "fapte", "experiment": 11, "linie": "l", "valoare": 50, "referinta": 41,
                                 "experiment_referinta": 8, "prag": 3, "muta_baza": True, "stare": "candidat",
                                 "motiv": "50 pe #11; aștept o a doua măsurătoare"})
    fise = [{"id": 11, "linie": "l", "decizie": "pastrat", "criterii": {"fapte_corecte": 50}},
            {"id": 12, "linie": "l", "decizie": "pastrat", "criterii": {"fapte_corecte": 52}}]
    schimbari = stabilitate.actualizeaza(memorie, fise, config, "t")
    assert schimbari[0]["stare"] == "confirmat" and schimbari[0]["motiv"].endswith(
        "confirmat de modelul păstrat mai nou #12 (52); linia de bază rămâne 60 (e deja mai bună)")
    assert memorie["capacitati"]["fapte"]["linie_de_baza"] == 60


def test_pragurile_nu_tin_cont_de_resturile_de_rotunjire():
    """4,4 − 3,4 = 1,0000000000000004 în calculator: exact 2 praguri de 0,5 sub linia de bază e zona galbenă, nu roșie."""
    sens = Capacitate("sens", "nota_profesor", True, 0.5, 10, True, None, linie_de_baza=4.4, curent=3.4)
    assert 4.4 - 3.4 > 1.0 and zona(sens, {"galben": 1.0, "rosu": 2.0}) == GALBENA
    povesti = Capacitate("povesti", "val_bpb", False, 0.005, None, True, None, linie_de_baza=0.4389, curent=0.4489)
    assert 0.4489 - 0.4389 > 0.01 and zona(povesti, {"galben": 1.0, "rosu": 2.0}) == GALBENA  # exact 2 praguri


def test_candidat_fara_linie_de_baza_in_memorie_la_val_bpb():
    """O capacitate „mai mic = mai bine”, confirmată când memoria n-are încă linie de bază pentru ea."""
    config = {"capacitati": {"povesti": {"metrica": "val_bpb", "mai_mare_e_mai_bine": False, "unealta": None}},
              "stabilitate": {"confirmari": 1}}
    memorie = memorie_goala()
    memorie["candidati"].append({"capacitate": "povesti", "experiment": 11, "linie": "l", "valoare": 0.43,
                                 "referinta": 0.45, "experiment_referinta": 8, "prag": 0.005, "muta_baza": True,
                                 "stare": "candidat", "motiv": "0,43 pe #11; aștept o a doua măsurătoare"})
    fise = [{"id": 11, "linie": "l", "decizie": "pastrat", "scoruri": {"val_bpb": 0.43}},
            {"id": 12, "linie": "l", "decizie": "pastrat", "scoruri": {"val_bpb": 0.42}}]
    assert stabilitate.actualizeaza(memorie, fise, config, "t")[0]["stare"] == "confirmat"
    assert memorie["capacitati"]["povesti"]["linie_de_baza"] == 0.43  # cea mai slabă dintre 0,43 și 0,42
