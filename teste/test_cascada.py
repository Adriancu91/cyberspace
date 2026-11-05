"""Ajutorul executantului din cascadă (19 octombrie 2026): ferestrele plăcii, procesele grele, pornirea desprinsă."""

import json
import os
import subprocess
import sys
import time
import types
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


class _WindowsFals:
    """S80: `tasklist` și `Get-CimInstance` înlocuite — un singur proces cu PID-ul, imaginea și ora date."""

    def __init__(self, monkeypatch, imagine, ora=None, pid=19792):
        self.pid, self.imagine, self.ora, self.chemari = pid, imagine, ora, []
        monkeypatch.setattr(cascada, "os", types.SimpleNamespace(name="nt", kill=os.kill))
        monkeypatch.setattr(cascada.subprocess, "run", self.run)

    def run(self, argumente, **_):
        self.chemari.append(argumente[0])
        if argumente[0] == "tasklist":
            iesire = (f'"{self.imagine}","{self.pid}","Console","1","12.345 K"\n' if self.imagine
                      else "INFO: No tasks are running which match the specified criteria.\n")
        else:
            iesire = f"{self.ora}\n" if self.ora else ""
        return subprocess.CompletedProcess(argumente, 0, stdout=iesire, stderr="")


def test_pid_refolosit_de_alt_program_nu_merge(monkeypatch):
    _WindowsFals(monkeypatch, "dllhost.exe", "2026-11-05T09:12:00")
    assert cascada.traieste(19792, "2026-10-28T08:33:21") is False
    _WindowsFals(monkeypatch, None)
    assert cascada.traieste(19792, "2026-10-28T08:33:21") is False
    _WindowsFals(monkeypatch, "python.exe", pid=197920)  # doar cifra în text nu ajunge
    assert cascada.traieste(19792) is False


def test_python_pornit_inainte_merge_iar_cel_pornit_dupa_nu(monkeypatch):
    _WindowsFals(monkeypatch, "python.exe", "2026-10-28T08:33:21")
    assert cascada.traieste(19792, "2026-10-28T08:33:21") is True
    _WindowsFals(monkeypatch, "python.exe", "2026-10-28T08:33:20")
    assert cascada.traieste(19792, "2026-10-28T08:33:21") is True
    _WindowsFals(monkeypatch, "python.exe", "2026-10-28T10:33:21")  # 2 ore după
    assert cascada.traieste(19792, "2026-10-28T08:33:21") is False
    w = _WindowsFals(monkeypatch, "python.exe", None)  # ora nu se citește: hotărăște numele
    assert cascada.traieste(19792, "2026-10-28T08:33:21") is True
    assert w.chemari == ["tasklist", "powershell"]


def test_inregistrare_mutata_fara_cod_nu_blocheaza_liber(tmp_path, monkeypatch):
    s42 = {"sarcina": "S42", "comanda": ["x"], "pornita": "2026-10-28T08:33:21", "pid": 19792}
    (tmp_path / "S42_0833.json").write_text(json.dumps(s42), encoding="utf-8")
    w = _WindowsFals(monkeypatch, "python.exe", "2026-10-28T08:33:21")  # chiar dacă ar părea viu
    monkeypatch.setattr(cascada, "placa", lambda: None)
    monkeypatch.setattr(cascada, "procese_python", lambda: [])
    s = cascada.sarcina("S42_0833", tmp_path)
    assert s["merge"] is False and s["cod"] is None
    assert w.chemari == []  # nu mai întreabă Windows
    st = cascada.stare(datetime(2026, 11, 5, 17, 30), tmp_path)
    assert st["liber"] is True and st["sarcini_pornite"][0]["merge"] is False
    assert json.loads((tmp_path / "S42_0833.json").read_text(encoding="utf-8")) == s42  # neatinsă


def test_muta_vechea_fara_cod_scrie_cod_null(tmp_path, monkeypatch):
    s4 = {"sarcina": "S4", "comanda": ["x"], "pornita": "2026-10-20T10:55:56", "pid": 9392}
    (tmp_path / "S4.json").write_text(json.dumps(s4), encoding="utf-8")
    _WindowsFals(monkeypatch, None)
    assert cascada.muta_vechea("S4", tmp_path) is True
    mutata = json.loads((tmp_path / "S4_1055.json").read_text(encoding="utf-8"))
    assert mutata["cod"] is None and mutata["nota"] == "mutată fără cod" and mutata["terminata"]
    assert {k: mutata[k] for k in s4} == s4 and not (tmp_path / "S4.json").exists()


def test_din_nou_refuza_sarcina_care_merge(tmp_path):
    assert cascada.porneste("S0", [sys.executable, "-c", "import time; time.sleep(4)"], tmp_path) == 0
    inainte = (tmp_path / "S0.json").read_text(encoding="utf-8")
    assert cascada.porneste("S0", [sys.executable, "-c", "print(1)"], tmp_path, din_nou=True) == 1
    assert (tmp_path / "S0.json").read_text(encoding="utf-8") == inainte
    assert sorted(p.name for p in tmp_path.iterdir() if p.suffix == ".json") == ["S0.json"]
    assert _asteapta_sfarsitul("S0", tmp_path)["cod"] == 0
