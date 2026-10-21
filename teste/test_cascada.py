"""Ajutorul executantului din cascadă (19 octombrie 2026): ferestrele plăcii, procesele grele, pornirea desprinsă."""

import json
import sys
import time
from datetime import datetime

from unelte import cascada


def test_ferestrele_placii():
    assert cascada.fereastra(datetime(2026, 10, 20, 8, 0)) == ("zi", 630)
    assert cascada.fereastra(datetime(2026, 10, 20, 18, 0)) == ("zi", 30)
    assert cascada.fereastra(datetime(2026, 10, 20, 19, 30)) == ("noapte", 690)
    assert cascada.fereastra(datetime(2026, 10, 21, 2, 0)) == ("noapte", 300)
    assert cascada.fereastra(datetime(2026, 10, 20, 18, 45)) == (None, 15)
    assert cascada.fereastra(datetime(2026, 10, 20, 7, 30)) == (None, 30)


def test_continuum_si_interfata_nu_tin_placa():
    procese = [
        {"pid": 1, "comanda": r'"C:\x\.venv\Scripts\python.exe" -X utf8 -m module.continuum.bucla --config c'},
        {"pid": 2, "comanda": r'"C:\x\.venv\Scripts\python.exe" -X utf8 -m module.interfata --port 8787'},
        {"pid": 3, "comanda": r'"C:\x\.venv\Scripts\python.exe" -X utf8 unelte/antrenare_lunga.py --ore 3'},
        {"pid": 4, "comanda": r'"C:\Python312\python.exe" -X utf8 unelte/antrenare_lunga.py --ore 3'},
    ]
    assert [p["pid"] for p in cascada.grele(procese)] == [3]


def test_pornirea_desprinsa_scrie_codul_si_jurnalul(tmp_path, monkeypatch):
    assert cascada.porneste("S0", [sys.executable, "-c", "print('salut'); raise SystemExit(3)"], tmp_path) == 0
    assert cascada.porneste("S0", [sys.executable, "-c", "print(1)"], tmp_path) == 1  # nu de două ori
    for _ in range(100):
        s = cascada.sarcina("S0", tmp_path)
        if not s["merge"] and s.get("cod") is not None:
            break
        time.sleep(0.2)
    assert s["cod"] == 3 and s["merge"] is False
    assert any("salut" in r for r in s["ultimele_randuri"])
    assert json.loads((tmp_path / "S0.json").read_text(encoding="utf-8"))["terminata"]


def test_python_din_proiect_cu_cale_relativa_si_comanda_lipsa(tmp_path):
    unelte = cascada.programul(["unelte/cascada.py", "stare"])
    assert unelte[0] == str(cascada.RADACINA / "unelte/cascada.py") and unelte[1:] == ["stare"]
    assert cascada.programul(["nu_exista_programul_asta_9"]) == ["nu_exista_programul_asta_9"]
    assert cascada.programul(["python", "-V"])[0] == sys.executable
    (tmp_path / "S9.json").write_text("{}", encoding="utf-8")
    assert cascada.ruleaza("S9", ["nu_exista_programul_asta_9"], tmp_path) == 127
    assert "Nu pot porni" in (tmp_path / "S9.log").read_text(encoding="utf-8")


def _asteapta_sfarsitul(nume, dosar):
    for _ in range(100):
        s = cascada.sarcina(nume, dosar)
        if not s["merge"] and s.get("cod") is not None:
            return s
        time.sleep(0.2)
    return s


def test_din_nou_muta_pornirea_terminata_si_porneste(tmp_path):
    """S9: a doua pornire după una terminată. Fără --din-nou refuză ca înainte; cu el mută ambele fișiere."""
    vechi = {"sarcina": "S0", "comanda": ["x"], "pornita": "2026-10-20T19:29:17", "pid": 0, "cod": 0}
    (tmp_path / "S0.json").write_text(json.dumps(vechi), encoding="utf-8")
    (tmp_path / "S0.log").write_text("prima\n", encoding="utf-8")
    (tmp_path / "S0_1929.json").write_text("{}", encoding="utf-8")  # numele e luat: vine _2
    assert cascada.porneste("S0", [sys.executable, "-c", "print(1)"], tmp_path) == 1
    assert json.loads((tmp_path / "S0.json").read_text(encoding="utf-8")) == vechi
    assert cascada.main(["porneste", "S0", "--din-nou", "--dosar", str(tmp_path), "--",
                         sys.executable, "-c", "print('a doua')"]) == 0
    assert json.loads((tmp_path / "S0_1929_2.json").read_text(encoding="utf-8")) == vechi
    assert (tmp_path / "S0_1929_2.log").read_text(encoding="utf-8") == "prima\n"
    assert (tmp_path / "S0_1929.json").read_text(encoding="utf-8") == "{}"
    s = _asteapta_sfarsitul("S0", tmp_path)
    assert s["cod"] == 0 and any("a doua" in r for r in s["ultimele_randuri"])


def test_din_nou_refuza_sarcina_care_merge(tmp_path):
    assert cascada.porneste("S0", [sys.executable, "-c", "import time; time.sleep(4)"], tmp_path) == 0
    inainte = (tmp_path / "S0.json").read_text(encoding="utf-8")
    assert cascada.porneste("S0", [sys.executable, "-c", "print(1)"], tmp_path, din_nou=True) == 1
    assert (tmp_path / "S0.json").read_text(encoding="utf-8") == inainte
    assert sorted(p.name for p in tmp_path.iterdir() if p.suffix == ".json") == ["S0.json"]
    assert _asteapta_sfarsitul("S0", tmp_path)["cod"] == 0
