from pathlib import Path


def test_raportul_de_dimineata_face_git_pull_inainte_de_instructiune():
    """S14 (21 octombrie 2026): unelte/raport_dimineata.ps1 face `git pull --ff-only` înainte să citească
    unelte/raport_dimineata.txt, ca raportul de la 07:40 să folosească instrucțiunea de pe GitHub."""
    script = (Path(__file__).resolve().parents[1] / "unelte" / "raport_dimineata.ps1").read_text(encoding="utf-8")
    pull = script.find("git pull --ff-only")
    citire = script.find('Get-Content (Join-Path $PSScriptRoot "raport_dimineata.txt")')
    assert pull != -1 and citire != -1
    assert pull < citire
    assert "continui cu fisierul local" in script
