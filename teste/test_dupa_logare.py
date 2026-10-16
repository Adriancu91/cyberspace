"""unelte/dupa_logare_ws.ps1 (16 octombrie 2026): după logare, Claude Code se pornește cu calea adevărată a lui
claude.exe. Până atunci, variabila cu calea avea același nume ca parametrul -Claude și rămânea „True”."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

RADACINA = Path(__file__).resolve().parent.parent
SCRIPT = RADACINA / "unelte" / "dupa_logare_ws.ps1"
pytestmark = pytest.mark.skipif(sys.platform != "win32" or shutil.which("powershell") is None, reason="doar pe Windows")


def ruleaza(tmp_path, *argumente):
    jurnal = tmp_path / "dupa_logare.log"
    subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SCRIPT), "-Jurnal", str(jurnal),
                    *argumente], check=True, capture_output=True, timeout=120)
    return jurnal.read_text(encoding="utf-8-sig")


def test_proba_scrie_calea_adevarata_a_lui_claude(tmp_path):
    exe = tmp_path / "claude.exe"
    exe.write_bytes(b"")
    jurnal = ruleaza(tmp_path, "-Claude", "-Proba", "-Exe", str(exe), "-Nume", "Proba")
    assert "Nu gasesc True" not in jurnal
    assert f"& '{exe}' --continue --remote-control 'Proba'" in jurnal and "Proba (nu pornesc nimic)" in jurnal


def test_fara_claude_exe_spune_calea_care_lipseste(tmp_path):
    jurnal = ruleaza(tmp_path, "-Claude", "-Proba", "-Exe", str(tmp_path / "lipseste.exe"))
    assert f"Nu gasesc {tmp_path / 'lipseste.exe'} : Claude Code nu a pornit." in jurnal
