"""S40: porturile opționale „cautare” și „inferenta” (acceptate, dar necerute) și modulul KGR1 față de MotorBrut."""

from pathlib import Path

import numpy as np
import pytest

from kronos.config import EroareConfig, citeste_config
from kronos.contracte import CONTRACT_PENTRU_PORT, PORTURI, PORTURI_OPTIONALE
from kronos.registru import EroareModul, Registru
from unelte.inferenta_bruta import MotorBrut

RADACINA = Path(__file__).resolve().parents[1]
VECTORI = RADACINA / "integrare" / "kronos" / "vectori"
PROBA = (RADACINA / "config" / "proba.toml").read_text(encoding="utf-8")


def test_porturile_optionale_sunt_separate():
    assert PORTURI_OPTIONALE == ("cautare", "inferenta")
    assert not set(PORTURI) & set(PORTURI_OPTIONALE)
    assert set(CONTRACT_PENTRU_PORT) == set(PORTURI) | set(PORTURI_OPTIONALE)


def test_configurarea_veche_merge_fara_porturile_noi():
    config = citeste_config(RADACINA / "config" / "proba.toml")
    assert not set(config.porturi) & set(PORTURI_OPTIONALE)


def test_configurarea_poate_avea_porturile_noi(tmp_path):
    cale = tmp_path / "cu_inferenta.toml"
    cale.write_text(PROBA + '\n[porturi.inferenta]\nmodul = "module.inferenta_kgr1:InferentaKGR1"\n', encoding="utf-8")
    assert citeste_config(cale).porturi["inferenta"]["modul"] == "module.inferenta_kgr1:InferentaKGR1"


def test_portul_necunoscut_tot_e_refuzat(tmp_path):
    cale = tmp_path / "rau.toml"
    cale.write_text(PROBA + '\n[porturi.cautari]\nmodul = "x:Y"\n', encoding="utf-8")
    with pytest.raises(EroareConfig, match="necunoscute: cautari"):
        citeste_config(cale)
    with pytest.raises(EroareModul, match="nu există"):
        Registru().creeaza("cautari", "module.cautare_e3:CautareE3")


@pytest.mark.parametrize("fisier,desfacere", [("mic_f32.kgr", "la_incarcare"), ("mic_q8_0.kgr", "la_incarcare"),
                                               ("mic_q8_0.kgr", "la_pas")])
def test_inferenta_kgr1_da_exact_ce_da_motorul(fisier, desfacere):
    modul = Registru().creeaza("inferenta", "module.inferenta_kgr1:InferentaKGR1",
                               {"cale": str(VECTORI / fisier), "desfacere": desfacere}).instanta
    motor = MotorBrut(VECTORI / fisier, desfacere)
    for simboluri in ([5], [1, 2, 3, 40, 500], list(range(100, 100 + motor.context))):
        lg = np.asarray(modul.logits(simboluri), dtype=np.float32)
        assert np.array_equal(lg, motor.logits(simboluri)[-1])
        assert modul.genereaza(simboluri, 6) == motor.completeaza_simboluri(simboluri, 6)[0]
    assert modul.statistici()["format"] == ("F32" if "f32" in fisier else "Q8_0")


def test_inferenta_kgr1_refuza_lista_goala():
    modul = Registru().creeaza("inferenta", "module.inferenta_kgr1:InferentaKGR1",
                               {"cale": str(VECTORI / "mic_f32.kgr")}).instanta
    with pytest.raises(ValueError):
        modul.logits([])
    with pytest.raises(ValueError):
        modul.genereaza([], 3)


def test_cautare_e3_varianta_necunoscuta_si_baza_lipsa(tmp_path):
    with pytest.raises(EroareModul, match="Setări greșite"):
        Registru().creeaza("cautare", "module.cautare_e3:CautareE3", {"cale_index": str(tmp_path / "nu_exista.sqlite")})
    with pytest.raises(EroareModul, match="Setări greșite"):
        Registru().creeaza("cautare", "module.cautare_e3:CautareE3", {"varianta": "nu_exista"})
