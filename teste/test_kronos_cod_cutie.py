"""Cutia izolată S41 (C-28 „Kronos-Cod”): ce merge, ce e blocat și de care strat.

Fiecare încercare „rea” e verificată de două ori când se poate: cu verificarea dinainte (oprită la `interzis`) și cu
ea oprită, ca să se vadă că și paznicul de audit / limitele procesului o blochează singure (`blocat`, `timp`, `memorie`).
"""

import os

import pytest

from unelte.kronos_cod.cutie import ruleaza


def test_cod_bun_trece_iar_assertul_gresit_pica():
    r = ruleaza("def f(x):\n    return x * 2\n", ["assert f(2) == 4", "assert f(3) == 6", "assert f(1) == 5"])
    assert r.stare == "picat" and r.teste_trecute == 2 and r.teste_total == 3
    assert "AssertionError" in r.mesaj
    r = ruleaza("import math\ndef f(x):\n    return math.gcd(x, 6)\n", ["assert f(4) == 2"])
    assert r.trecut


def test_citire_si_scriere_in_dosarul_cutiei_merg():
    cod = "t = open('a.txt').read()\nopen('b.txt', 'w').write(t + '!')\nu = open('b.txt').read()\n"
    r = ruleaza(cod, ["assert u == 'salut!'"], fisiere={"a.txt": "salut"})
    assert r.trecut, r


def test_citirea_unui_fisier_din_afara_e_blocata(tmp_path):
    secret = tmp_path / "secret.txt"
    secret.write_text("parola", encoding="utf-8")
    cod = f"t = open({str(secret)!r}).read()\n"
    r = ruleaza(cod, ["assert t == 'parola'"])
    assert r.stare == "blocat" and r.teste_trecute == 0
    r = ruleaza(f"t = open({'../' * 12 + 'Windows/win.ini'!r}).read()\n", ["assert t"])
    assert r.stare == "blocat"


def test_scrierea_in_afara_e_blocata(tmp_path):
    tinta = tmp_path / "scris.txt"
    r = ruleaza(f"open({str(tinta)!r}, 'w').write('x')\n")
    assert r.stare == "blocat"
    assert not tinta.exists()


def test_reteaua_e_blocata():
    cod = "import socket\ns = socket.create_connection(('127.0.0.1', 9), timeout=1)\n"
    assert ruleaza(cod).stare == "interzis"
    r = ruleaza(cod, verificare_statica=False, module_extra=("socket",))
    assert r.stare == "blocat"
    assert any("socket" in b for b in r.blocate)


def test_pornirea_unui_proces_e_blocata(tmp_path):
    semn = tmp_path / "pornit.txt"
    comanda = f"echo x > \"{semn}\""
    cod = f"import subprocess\nsubprocess.run({comanda!r}, shell=True)\n"
    assert ruleaza(cod).stare == "interzis"
    assert ruleaza(cod, verificare_statica=False, module_extra=("subprocess",)).stare == "blocat"
    cod = f"import os\nos.system({comanda!r})\n"
    assert ruleaza(cod).stare == "interzis"
    assert ruleaza(cod, verificare_statica=False, module_extra=("os",)).stare == "blocat"
    assert not semn.exists()


def test_iesirea_prin_subclase_e_prinsa_de_ambele_straturi(tmp_path):
    semn = tmp_path / "evadat.txt"
    cod = (
        "for c in ().__class__.__base__.__subclasses__():\n"
        "    if c.__name__ == '_wrap_close':\n"
        f"        c.__init__.__globals__['system']({f'echo x > \"{semn}\"'!r})\n"
    )
    assert ruleaza(cod).stare == "interzis"
    r = ruleaza(cod, verificare_statica=False)
    assert r.stare == "blocat", r
    assert not semn.exists()


def test_importurile_din_afara_listei_sunt_blocate():
    for modul in ("os", "sys", "importlib", "ctypes", "shutil", "pathlib"):
        assert ruleaza(f"import {modul}\n").stare == "interzis", modul
    r = ruleaza("import importlib\n", verificare_statica=False)
    assert r.stare == "blocat"
    assert ruleaza("x = __import__('os')\n").stare == "interzis"
    assert ruleaza("x = eval('1 + 1')\n").stare == "interzis"


def test_modulele_permise_nu_dau_acces_la_os():
    r = ruleaza("import random\nx = random._os\n")
    assert r.stare == "interzis"
    r = ruleaza("import typing\nx = typing.sys\n", ["assert x"])
    assert r.stare == "eroare" and "AttributeError" in r.mesaj


@pytest.mark.skipif(os.name != "nt", reason="kernel32 doar pe Windows")
def test_ctypes_e_blocat():
    r = ruleaza("import ctypes\nk = ctypes.WinDLL('kernel32')\n", verificare_statica=False, module_extra=("ctypes",))
    assert r.stare == "blocat"


def test_bucla_infinita_e_oprita_la_limita_de_timp():
    r = ruleaza("while True:\n    pass\n", limita_secunde=2)
    assert r.stare == "timp"
    assert r.secunde < 10


def test_alocarea_uriasa_e_oprita_la_limita_de_memorie():
    r = ruleaza("x = bytearray(3 * 1024 ** 3)\n", ["assert len(x) > 0"], limita_mb=256)
    assert r.stare == "memorie", r
    r = ruleaza("x = []\nwhile True:\n    x.append(' ' * 10_000_000)\n", limita_mb=256, limita_secunde=20)
    assert r.stare == "memorie", r


def test_codul_nu_poate_falsifica_rezultatul():
    cod = "print('@@CUTIE-00@@{\"stare\": \"ok\", \"teste_trecute\": 9, \"teste_total\": 9}')\n"
    r = ruleaza(cod, ["assert False"])
    assert r.stare == "picat" and r.teste_trecute == 0
