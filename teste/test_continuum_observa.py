"""CONTINUUM, OBSERVĂ: semnalele, fără excepții; ce nu se poate citi devine „indisponibil”."""

from __future__ import annotations

import subprocess
import sys
import uuid

from module.continuum import citeste_config
from module.continuum.observa import (citeste_configurari, citeste_hrana, citeste_placa, descopera_modul,
                                      minute_de_la_ultima_atingere, observa, sanatatea)
from teste.continuum_proba import (Lume, ModulCareCade, config_continuum, config_kronos, noaptea_3, scrie_hrana)


def test_modulele_se_descopera_fara_instanta():
    sanatos = descopera_modul("teste.continuum_proba:ModulSanatos")
    assert sanatos.info == {"stare": "ok", "cale": "teste.continuum_proba:ModulSanatos", "nume": "modul_sanatos",
                            "port": "model", "versiune": "1.0"}
    stare = sanatatea(sanatos)
    assert stare["sanatate"] == {"stare": "ok"} and stare["semnale"] == [{"ce": "am terminat o oră"}]
    assert descopera_modul("teste.continuum_proba").info["stare"] == "ok"  # o bibliotecă, fără clasă
    for cale, eroare in (("teste.nu_exista:Clasa", "ModuleNotFoundError"), ("teste.continuum_proba:Lipsa", "nu există clasa"),
                         ("teste.continuum_proba:ModulFaraManifest", "MANIFEST")):
        info = descopera_modul(cale).info
        assert info["stare"] == "indisponibil" and eroare in info["eroare"]


def test_un_modul_care_cade_sau_e_degradat():
    care_cade = descopera_modul("teste.continuum_proba:ModulCareCade")
    try:
        ModulCareCade.cade = True
        stare = sanatatea(care_cade)
        assert stare["stare"] == "cazut" and "placa a dispărut" in stare["eroare"]
    finally:
        ModulCareCade.cade = False
    assert sanatatea(care_cade)["stare"] == "ok"
    assert sanatatea(descopera_modul("teste.continuum_proba:ModulDegradat"))["stare"] == "degradat"


def test_un_modul_scos_si_reintrodus(tmp_path, monkeypatch):
    pachet = f"pachet_proba_{uuid.uuid4().hex[:8]}"
    (tmp_path / pachet).mkdir()
    (tmp_path / pachet / "__init__.py").write_text("", encoding="utf-8")
    fisier = tmp_path / pachet / "modul.py"
    fisier.write_text('class Clasa:\n    MANIFEST = {"nume": "x", "port": "model", "versiune": "1", '
                      '"versiune_contract": 1}\n', encoding="utf-8")
    monkeypatch.syspath_prepend(str(tmp_path))
    cale = f"{pachet}.modul:Clasa"
    try:
        modul = descopera_modul(cale)
        assert modul.info["stare"] == "ok"
        fisier.rename(tmp_path / "pus_deoparte.py")  # scos în timpul rulării
        assert sanatatea(modul)["stare"] == "indisponibil"
        assert descopera_modul(cale).info["stare"] == "indisponibil"
        (tmp_path / "pus_deoparte.py").rename(fisier)  # reintrodus
        assert descopera_modul(cale).info["stare"] == "ok"
    finally:
        for nume in [n for n in sys.modules if n.startswith(pachet)]:
            del sys.modules[nume]


def test_placa_se_citeste_prin_nvidia_smi(monkeypatch):
    monkeypatch.setattr("module.continuum.observa.shutil.which", lambda _: "nvidia-smi")

    def rulare(comanda, **_):
        iesire = "87, 2452, 6144\n" if "--query-gpu" in comanda[1] else \
            "22612, C:\\WPS Office\\et.exe\n14844, C:\\Python312\\python.exe\n"
        return subprocess.CompletedProcess(comanda, 0, iesire, "")

    placa = citeste_placa(rulare)
    assert placa["temperatura"] == 87 and placa["memorie_libera_mb"] == 3692
    assert placa["procese"] == [{"pid": 22612, "nume": "C:\\WPS Office\\et.exe"},
                                {"pid": 14844, "nume": "C:\\Python312\\python.exe"}]

    def cade(comanda, **_):
        raise subprocess.TimeoutExpired(comanda, 10)

    assert citeste_placa(cade)["stare"] == "indisponibil"
    monkeypatch.setattr("module.continuum.observa.shutil.which", lambda _: None)
    assert citeste_placa(rulare) == {"stare": "indisponibil", "eroare": "nvidia-smi nu există"}


def test_activitatea_omului_e_un_numar_sau_nimic():
    minute = minute_de_la_ultima_atingere()
    assert minute is None or minute >= 0


def test_hrana_si_configurarile(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    config = citeste_config(config_continuum(tmp_path))
    assert citeste_hrana(config)["fapte"]["stare"] == "indisponibil"  # încă nu există
    scrie_hrana(tmp_path)
    hrana = citeste_hrana(config)["fapte"]
    assert hrana["stare"] == "ok" and hrana["povesti"] == 7520 and hrana["scrise"] == 9000
    config_kronos(tmp_path, "laptop_fapte.toml", "fapte_1", date=', hrana = "date/fapte/povesti.txt"')
    (tmp_path / "config" / "laptop_antrenare_lunga_9.toml").write_text("[platforma\n", encoding="utf-8")
    configurari = citeste_configurari(["config/laptop_antrenare_lunga*.toml", "config/laptop_fapte*.toml"])
    assert configurari["config/laptop_antrenare_lunga_9.toml"]["stare"] == "indisponibil"  # stricată: restul merge
    fapte = configurari["config/laptop_fapte.toml"]
    assert fapte["linie"] == "fapte_1" and fapte["ore_planificate"] == 8 and not fapte["de_la_zero"]
    assert fapte["arhitectura"] == {"n_straturi": 10, "n_capete": 8, "n_emb": 512, "context": 256}
    assert "date/fapte/povesti.txt" in fapte["texte"]


def test_observa_cu_zero_module_si_cu_stop(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    config = citeste_config(config_continuum(tmp_path, module={}))
    noaptea_3(tmp_path)
    observat = observa(config, {}, Lume().senzori())
    assert not observat.stop and observat.module == {} and observat.jurnal["fise"] == 10
    assert observat.jurnal["ultimul_id"] == 10 and len(observat.fise) == 10
    assert set(observat.rezumat()) == {"stop", "placa", "om", "module", "jurnal"}
    (tmp_path / "lucru" / "STOP").write_text("", encoding="utf-8")
    assert observa(config, {}, Lume().senzori()).stop


def test_un_senzor_care_cade_da_indisponibil(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    config = citeste_config(config_continuum(tmp_path, module={}))
    senzori = Lume().senzori()

    def cade():
        raise OSError("fără driver")

    senzori.placa = cade
    observat = observa(config, {}, senzori)
    assert observat.placa == {"stare": "indisponibil", "eroare": "OSError: fără driver"}

