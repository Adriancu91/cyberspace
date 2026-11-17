"""S118 pasul 2: lecțiile din conversații (👍 și corecturile), fără dubluri, cu 20 % deoparte stabil."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from module.interfata.catalog import ROL_CREIER, ROL_OM, Catalog
from unelte import lectii_din_conversatii as L

RADACINA = Path(__file__).resolve().parents[1]


def _intreaba(catalog: Catalog, intrebare: str, raspuns: str) -> int:
    conv = catalog.conversatie_noua(intrebare)
    catalog.adauga_mesaj(conv, ROL_OM, "Tu", intrebare)
    return catalog.adauga_mesaj(conv, ROL_CREIER, "Kronos", raspuns)["id"]


def _baza(tmp_path: Path) -> Path:
    baza = tmp_path / "c.db"
    c = Catalog(baza)
    c.apreciaza(_intreaba(c, "Cine ești?", "Sunt Kronos."), 1)                          # 👍 → lecție
    c.apreciaza(_intreaba(c, "Cât face 3x7?", "Face 20."), -1, "3 x 7 = 21.")             # 👎 + corectură → lecție
    c.apreciaza(_intreaba(c, "Unde e Iașiul?", "Pe Lună."), -1)                           # 👎 fără corectură → ignorat
    c.apreciaza(_intreaba(c, "Ce faci?", "Bine."), None)                                  # fără nimic → ignorat
    t = c.adauga_intrebare_text("Satul X are 500 de locuitori.", "Câți locuitori are X?", "300.", "Kronos")
    c.apreciaza_text(t["id"], None, "X are 500 de locuitori.")                            # corectură fără notă → lecție
    return baza


def test_doar_aprecierile_si_corecturile_devin_lectii(tmp_path):
    info = L.ruleaza(_baza(tmp_path), tmp_path / "lectii", procent=0)
    lectii = [json.loads(r) for r in (tmp_path / "lectii" / L.LECTII).read_text(encoding="utf-8").splitlines()]
    pe_intrebare = {l["intrebare"]: l for l in lectii}
    assert set(pe_intrebare) == {"Cine ești?", "Cât face 3x7?", "Câți locuitori are X?"}
    assert pe_intrebare["Cine ești?"]["raspuns"] == "Sunt Kronos." and pe_intrebare["Cine ești?"]["tip"] == "apreciat"
    assert pe_intrebare["Cât face 3x7?"]["raspuns"] == "3 x 7 = 21." and pe_intrebare["Cât face 3x7?"]["tip"] == "corectat"
    # forma S116: chat fără text în față; „din text” cu paragraful
    assert pe_intrebare["Cine ești?"]["prompt"] == "Întrebare: Cine ești?\nRăspuns:" and "text" not in pe_intrebare["Cine ești?"]
    din_text = pe_intrebare["Câți locuitori are X?"]
    assert din_text["prompt"] == "Text: Satul X are 500 de locuitori.\nÎntrebare: Câți locuitori are X?\nRăspuns:"
    assert din_text["text"] == "Satul X are 500 de locuitori." and din_text["fel"] == "lectie_text"
    assert info["lectii"] == 3 and info["corectate"] == 2 and info["apreciate_fara_corectura"] == 1
    assert info["ignorate"] == {"nu_fara_corectura": 1, "fara_nota": 1}
    # info are doar numere, niciun text din conversații
    text_info = (tmp_path / "lectii" / L.INFO).read_text(encoding="utf-8")
    assert "Kronos" not in text_info and "Cine" not in text_info


def test_fara_dubluri_corectura_bate_aprecierea(tmp_path):
    randuri = [
        {"fila": "chat", "intrebare": "Cât face 2+2?", "paragraf": "", "raspuns": "4.", "nota": 1, "corectura": None,
         "creata": "2026-11-17T10:00:00"},
        {"fila": "chat", "intrebare": "  cât face  2+2? ", "paragraf": "", "raspuns": "5.", "nota": -1,
         "corectura": "2 + 2 = 4.", "creata": "2026-11-17T09:00:00"},
        {"fila": "chat", "intrebare": "Cât face 2+2?", "paragraf": "", "raspuns": "4", "nota": 1, "corectura": None,
         "creata": "2026-11-17T11:00:00"},
    ]
    lectii, numere = L.strange(randuri)
    assert len(lectii) == 1 and lectii[0]["raspuns"] == "2 + 2 = 4." and numere["dubluri"] == 2
    # între două de același fel câștigă cea mai nouă
    lectii, _ = L.strange([randuri[0], randuri[2]])
    assert lectii[0]["raspuns"] == "4"
    # aceeași întrebare, dar cu alt paragraf, e altă lecție
    alta = dict(randuri[0], fila="text", paragraf="Un paragraf.")
    assert len(L.strange([randuri[0], alta])[0]) == 2


def test_deoparte_e_stabil_si_aproape_20_la_suta():
    randuri = [{"fila": "chat", "intrebare": f"Întrebarea {i}?", "raspuns": "Da.", "nota": 1} for i in range(1000)]
    lectii, _ = L.strange(randuri)
    antrenare, deoparte = L.imparte(lectii)
    assert len(antrenare) + len(deoparte) == 1000 and 150 <= len(deoparte) <= 250
    assert not {l["id"] for l in antrenare} & {l["id"] for l in deoparte}
    # cu lecții noi adăugate, cele vechi rămân de aceeași parte
    mai_multe, _ = L.strange(randuri + [{"fila": "chat", "intrebare": f"Nouă {i}?", "raspuns": "Da.", "nota": 1}
                                        for i in range(300)])
    _, deoparte2 = L.imparte(mai_multe)
    vechi = {l["id"] for l in lectii}
    assert {l["id"] for l in deoparte2 if l["id"] in vechi} == {l["id"] for l in deoparte}


def test_rularea_e_repetabila_si_linia_de_comanda(tmp_path, capsys):
    baza = _baza(tmp_path)
    dosar = tmp_path / "lectii"
    assert L.main(["--baza", str(baza), "--dosar", str(dosar)]) == 0
    prima = {f: (dosar / f).read_bytes() for f in (L.LECTII, L.EXAMEN, L.INFO)}
    iesire = capsys.readouterr().out
    assert '"lectii": 3' in iesire and "Cine ești" not in iesire   # pe ecran doar numere
    assert L.main(["--baza", str(baza), "--dosar", str(dosar)]) == 0
    assert {f: (dosar / f).read_bytes() for f in prima} == prima
    assert L.main(["--baza", str(tmp_path / "lipsa.db"), "--dosar", str(dosar)]) == 2


def test_lectiile_stau_in_afara_git():
    try:
        rezultat = subprocess.run(["git", "check-ignore", "-q", "lucru/lectii/lectii.jsonl"], cwd=RADACINA,
                                  capture_output=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        pytest.skip("git nu e disponibil")
    assert rezultat.returncode == 0
