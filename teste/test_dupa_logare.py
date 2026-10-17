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


def conversatii(tmp_path, folder=None):
    """Un dosar ca ~/.claude/projects; cu `folder`, acel folder are o conversație salvată."""
    proiecte = tmp_path / "projects"
    proiecte.mkdir(exist_ok=True)
    if folder:
        dosar = proiecte / "".join(c if c.isascii() and c.isalnum() else "-" for c in folder)
        dosar.mkdir()
        (dosar / "conversatie.jsonl").write_text("{}\n", encoding="utf-8")
    return proiecte


def test_proba_scrie_calea_adevarata_a_lui_claude(tmp_path):
    exe = tmp_path / "claude.exe"
    exe.write_bytes(b"")
    jurnal = ruleaza(tmp_path, "-Claude", "-Proba", "-Exe", str(exe), "-Nume", "Proba", "-Folder", r"C:\Kronos\cyberspace",
                     "-Conversatii", str(conversatii(tmp_path, r"C:\Kronos\cyberspace")))
    assert "Nu gasesc True" not in jurnal
    assert f"& '{exe}' --continue --remote-control 'Proba'" in jurnal and "Proba (nu pornesc nimic" in jurnal
    # dacă --continue se oprește în primul minut („No conversation found”), pornește o sesiune nouă
    assert f"-lt 60) {{ & '{exe}' --remote-control 'Proba' }}" in jurnal


def test_fara_conversatie_porneste_o_sesiune_noua(tmp_path):
    """17 octombrie 2026: „claude --continue” fără conversație în folder răspunde „No conversation found”."""
    exe = tmp_path / "claude.exe"
    exe.write_bytes(b"")
    jurnal = ruleaza(tmp_path, "-Claude", "-Proba", "-Exe", str(exe), "-Nume", "Proba", "-Folder", r"C:\Kronos\cyberspace",
                     "-Conversatii", str(conversatii(tmp_path)))
    assert "--continue" not in jurnal
    assert f"Set-Location 'C:\\Kronos\\cyberspace'; & '{exe}' --remote-control 'Proba'\"" in jurnal
    assert "nu are nicio conversatie de continuat" in jurnal


def test_fara_claude_exe_spune_calea_care_lipseste(tmp_path):
    jurnal = ruleaza(tmp_path, "-Claude", "-Proba", "-Exe", str(tmp_path / "lipseste.exe"))
    assert f"Nu gasesc {tmp_path / 'lipseste.exe'} : Claude Code nu a pornit." in jurnal


def test_paznicul_pe_uscat_spune_ce_ar_porni(tmp_path):
    """unelte/paznic_procese_ws.ps1 -Proba: nu pornește nimic, dar spune pentru fiecare din cele trei ce ar face."""
    exe = tmp_path / "claude.exe"
    exe.write_bytes(b"")
    jurnal = tmp_path / "paznic.log"
    subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                    str(RADACINA / "unelte" / "paznic_procese_ws.ps1"), "-Proba", "-Jurnal", str(jurnal), "-Exe", str(exe),
                    "-Nume", "Proba", "-Conversatii", str(conversatii(tmp_path)), "-Port", "65431"],
                   check=True, capture_output=True, timeout=120)
    text = jurnal.read_text(encoding="utf-8-sig")
    assert f"& '{exe}' --remote-control 'Proba'" in text
    assert "interfata nu asculta pe portul 65431; as porni unelte\\interfata_ws.ps1 -Port 65431" in text
    assert "CONTINUUM" in text
