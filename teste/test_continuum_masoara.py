"""CONTINUUM, MĂSOARĂ: verdictul doar din măsurători, cu pragul de zgomot al fiecărei capacități și regula 4."""

from __future__ import annotations

from module.continuum import ESEC, NECONCLUDENT, SUCCES, INVATARE
from module.continuum.actioneaza import Plan
from module.continuum.alege import Alegere
from module.continuum.evalueaza import Capacitate, StareaOrganismului
from module.continuum.masoara import masoara
from module.continuum.nevoi import Nevoie


def stare(ultimul_id, model, povesti=None, fapte=None, sens=None, hrana=None):
    capacitati = {
        "povesti": Capacitate("povesti", "val_bpb", False, 0.02, None, True, None, curent=povesti),
        "fapte": Capacitate("fapte", "fapte_corecte", True, 3, 150, True, None, curent=fapte),
        "sens": Capacitate("sens", "nota_profesor", True, 0.3, 10, True, None, curent=sens),
    }
    return StareaOrganismului("2026-10-07T23:30:00", INVATARE, "test", ultimul_id,
                              {"experiment": model, "linie": "fapte_1", "arhitectura": {}} if model else None,
                              capacitati=capacitati, hrana=hrana or {})


def antrenare(tinta="fapte"):
    plan = Plan(f"dezvolta:{tinta}", "antrenare", f"dezvolta:{tinta}:antrenare", "antrenare lungă cu config/laptop_fapte.toml",
                [["python"]], 60, linie="fapte_1")
    return Alegere(Nevoie("dezvolta", tinta, 3, "test"), plan)


REUSIT = {"simulat": False, "reusit": True, "motiv": None}


def test_fara_actiune_sau_simulat_nu_e_verdict():
    inainte = stare(10, 8, 0.4567, 41, 4.7)
    assert masoara(Alegere(), inainte, None, None)["verdict"] is None
    assert masoara(antrenare(), inainte, None, {"simulat": True})["verdict"] is None


def test_antrenarea_reusita():
    rezultat = masoara(antrenare(), stare(10, 8, 0.4567, 41, 4.7), stare(18, 18, 0.4450, 70, 4.8), REUSIT)
    assert rezultat["verdict"] == SUCCES and rezultat["fise"] == list(range(11, 19)) and rezultat["model_dupa"] == 18
    assert rezultat["motiv"] == "fapte: 41 → 70, mai bine cu mai mult decât pragul de 3"
    assert rezultat["inainte"] == {"povesti": 0.4567, "fapte": 41, "sens": 4.7}


def test_regula_4_un_castig_care_pierde_altceva_e_esec():
    rezultat = masoara(antrenare(), stare(10, 8, 0.4567, 41, 4.7), stare(18, 18, 0.4950, 70, 4.8), REUSIT)
    assert rezultat["verdict"] == ESEC
    assert rezultat["motiv"] == "fapte: 41 → 70, dar a pierdut povesti (0,4567 → 0,495, pragul e 0,02)"


def test_sub_pragul_de_zgomot_sau_fara_ora_noua_e_neconcludent():
    inainte = stare(10, 8, 0.4567, 41, 4.7)
    assert masoara(antrenare(), inainte, stare(18, 18, 0.4560, 43, 4.7), REUSIT)["verdict"] == NECONCLUDENT
    fara_ora = masoara(antrenare(), inainte, stare(12, 8, 0.4567, 41, 4.7), REUSIT)
    assert fara_ora["verdict"] == NECONCLUDENT and fara_ora["motiv"] == "nicio oră păstrată nouă pe linia fapte_1"
    nemasurat = masoara(antrenare(), inainte, stare(18, 18, 0.4450, None, 4.8), REUSIT)
    assert nemasurat["verdict"] == NECONCLUDENT and "nu e măsurat" in nemasurat["motiv"]


def test_unealta_cazuta_e_esec():
    rezultat = masoara(antrenare(), stare(10, 8, 0.4567, 41, 4.7), stare(10, 8, 0.4567, 41, 4.7),
                       {"simulat": False, "reusit": False, "motiv": "„x” a ieșit cu codul 3"})
    assert rezultat["verdict"] == ESEC and rezultat["motiv"] == "„x” a ieșit cu codul 3"


def test_examenele_si_hrana():
    plan = Plan("masoara:fapte+sens", "examene", "masoara:examene", "examene", [["python"]], 60,
                detalii={"capacitati": ["fapte", "sens"], "experiment": 8})
    alegere = Alegere(Nevoie("masoara", "fapte+sens", 1, "test"), plan)
    inainte = stare(10, 8, 0.4567)
    reusit = masoara(alegere, inainte, stare(12, 8, 0.4567, 41, 4.7), REUSIT)
    assert reusit["verdict"] == SUCCES and reusit["motiv"] == "modelul #8 are acum: fapte 41, sens 4,7"
    assert masoara(alegere, inainte, stare(11, 8, 0.4567, 41), REUSIT)["verdict"] == ESEC
    plan = Plan("dezvolta:fapte", "hrana", "dezvolta:fapte:hrana", "hrană", [["python"]], 60,
                detalii={"povesti_inainte": 7520})
    alegere = Alegere(Nevoie("dezvolta", "fapte", 3, "test"), plan)
    crescut = stare(11, 8, hrana={"fapte": {"stare": "ok", "povesti": 9400}})
    assert masoara(alegere, inainte, crescut, REUSIT)["verdict"] == SUCCES

