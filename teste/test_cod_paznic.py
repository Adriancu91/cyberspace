"""Școala de cod: paznicul (amprente, placa, alimentarea)."""

from __future__ import annotations

import shutil

from module.cod import paznic_cod
from module.cod.paznic_cod import (AMPRENTATE, Senzori, aproba, asteapta_incarcatorul, asteapta_racirea,
                                   de_ce_nu_e_libera, verifica)
from teste.cod_proba import RADACINA


def senzori(temperaturi=(60,), baterie=(False,), alte=(), memorie=500):
    temperaturi, baterie = list(temperaturi), list(baterie)
    asteptari = []

    def urmatoarea(lista):
        return lista.pop(0) if len(lista) > 1 else lista[0]

    s = Senzori(temperatura=lambda: urmatoarea(temperaturi), alte_procese=lambda: list(alte),
                memorie_ocupata_mb=lambda: memorie, pe_baterie=lambda: urmatoarea(baterie), asteapta=asteptari.append)
    return s, asteptari


def test_amprentele(tmp_path):
    rad = tmp_path / "wt"
    for cale in AMPRENTATE.values():
        (rad / cale).parent.mkdir(parents=True, exist_ok=True)
        if (RADACINA / cale).exists():
            shutil.copyfile(RADACINA / cale, rad / cale)
        else:
            (rad / cale).write_text("{}", encoding="utf-8")
    lucru = rad / "lucru"
    assert "n-au fost aprobate" in verifica(rad, lucru)
    aproba(rad, lucru)
    assert verifica(rad, lucru) is None
    (rad / "date/cod/abecedar.txt").write_text("alt abecedar", encoding="utf-8")
    assert "abecedarul" in verifica(rad, lucru) and "--aproba-amprente" in verifica(rad, lucru)
    aproba(rad, lucru)  # schimbarea aprobată de om
    assert verifica(rad, lucru) is None
    # Git pe Windows rescrie sfârșitul de rând (LF ↔ CRLF): conținutul e același, paznicul nu oprește
    cale = rad / "module/cod/sandbox.py"
    cale.write_bytes(cale.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
    assert verifica(rad, lucru) is None
    cale.write_bytes(cale.read_bytes().replace(b"TIMEOUT_SECUNDE = 2.0", b"TIMEOUT_SECUNDE = 20.0"))
    assert "sandbox-ul" in verifica(rad, lucru)


def test_racirea():
    s, asteptari = senzori(temperaturi=(90, 80, 69))
    assert asteapta_racirea(85, 70, s, pauza=30) == "placa avea peste 85 °C: am așteptat 60 s, până la 69 °C"
    assert asteptari == [30, 30]
    s, asteptari = senzori(temperaturi=(84,))
    assert asteapta_racirea(85, 70, s) is None and asteptari == []


def test_alimentarea():
    s, _ = senzori(baterie=(False,))
    assert asteapta_incarcatorul(s) == (True, None)
    s, asteptari = senzori(baterie=(True, True, False))
    merge, motiv = asteapta_incarcatorul(s, pauza=30)
    assert merge and "am așteptat încărcătorul 30 s" in motiv
    s, _ = senzori(baterie=(True,))
    merge, motiv = asteapta_incarcatorul(s, pauza=30, maxim_secunde=60)
    assert not merge and "pe baterie" in motiv
    s, _ = senzori(baterie=(None,))  # nu se poate afla: nu oprim
    assert asteapta_incarcatorul(s) == (True, None)


def test_placa_libera():
    assert de_ce_nu_e_libera(senzori()[0]) is None
    assert "1234 python.exe" in de_ce_nu_e_libera(senzori(alte=("1234 python.exe 3000 MiB",))[0])
    assert "3000 MB" in de_ce_nu_e_libera(senzori(memorie=3000)[0])


def test_senzorii_adevarati_se_pot_citi():
    """Pe laptop: răspund cu tipul potrivit (sau None, unde nu se poate afla), fără să cadă."""
    alte = paznic_cod.alte_procese_pe_placa()
    assert alte is None or isinstance(alte, list)
    assert paznic_cod.pe_baterie() in (True, False, None)
    memorie = paznic_cod.memorie_ocupata_mb()
    assert memorie is None or memorie >= 0
