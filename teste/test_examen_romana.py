"""S90: examenul de română ca modul (`module/examen_romana.py`)."""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from module.examen_romana import AMPRENTE, VALIDARI_ROMANA_CURAT, AmprentaGresita, ExamenRomana, sha256

RADACINA = Path(__file__).resolve().parent.parent


class ModelFals:
    """biti_pentru depinde de text (litere „grele” costă mai mult); completeaza dă mereu referința primei perechi."""

    def __init__(self) -> None:
        self.chemari = 0

    def biti_pentru(self, text: str) -> float:
        self.chemari += 1
        return float(sum(3 if c in "ăîșțâ" else 1 for c in text))

    def completeaza(self, inceput: str, max_simboluri: int = 6) -> str:
        return "Da."


def _validari(tmp_path: Path) -> tuple[dict[str, str], dict[str, str]]:
    texte = {"a": "Orașul are o cetate veche.\n<|endoftext|>\n" * 30, "b": "Râul trece prin sat.\n" * 50,
             "c": "Cartea are șapte capitole.\n<|endoftext|>\n" * 20}
    validari, amprente = {}, {}
    for nume, text in texte.items():
        f = tmp_path / f"{nume}.txt"
        f.write_text(text, encoding="utf-8")
        validari[nume] = str(f)
        amprente[str(f)] = sha256(f)
    return validari, amprente


def test_amprenta_gresita_refuza(tmp_path):
    validari, amprente = _validari(tmp_path)
    e = ExamenRomana(validari=validari, amprente=amprente, caractere=200)
    e.examineaza(ModelFals(), None)
    Path(validari["b"]).write_text("Alt text.\n" * 50, encoding="utf-8")
    model = ModelFals()
    with pytest.raises(AmprentaGresita):
        e.examineaza(model, None)
    assert model.chemari == 0  # refuză înainte să noteze


def test_fisier_lipsa_refuza(tmp_path):
    validari, amprente = _validari(tmp_path)
    e = ExamenRomana(validari=validari, amprente=amprente)
    Path(validari["a"]).unlink()
    with pytest.raises(AmprentaGresita):
        e.examineaza(ModelFals(), None)


def test_cale_noua_fara_amprenta_nu_porneste(tmp_path):
    validari, _ = _validari(tmp_path)
    with pytest.raises(ValueError):
        ExamenRomana(validari=validari)


def test_acelasi_model_acelasi_scor(tmp_path):
    validari, amprente = _validari(tmp_path)
    e = ExamenRomana(validari=validari, amprente=amprente, caractere=300)
    model = ModelFals()
    a, b = e.examineaza(model, None), e.examineaza(model, None)
    assert a["romana_bpb"] == b["romana_bpb"]
    assert ExamenRomana(validari=validari, amprente=amprente, caractere=300).examineaza(ModelFals(), None)["romana_bpb"] \
        == a["romana_bpb"]


def test_aceeasi_regula_ca_examen_validari_ws(tmp_path):
    """romana_bpb = media pe octeți a celor trei, pe aceleași litere ca `examen_validari_ws.examineaza` + `numere`."""
    from unelte import examen_validari_ws as ws

    validari, amprente = _validari(tmp_path)
    numele = ws.GRUPE["romana_curat"]
    pe_nume = dict(zip(numele, validari.values()))
    e = ExamenRomana(validari=pe_nume, amprente=amprente, caractere=300)
    scor = e.examineaza(ModelFals(), None)["romana_bpb"]
    referinta = ws.numere(ws.examineaza(ModelFals(), 300, pe_nume))["bpb_romana_curat"]
    assert round(scor, 4) == referinta


def test_validarile_implicite_sunt_grupa_romana_curat():
    from unelte import examen_validari_ws as ws

    assert list(VALIDARI_ROMANA_CURAT) == ws.GRUPE["romana_curat"]
    assert all(ws.VALIDARI[n] == c for n, c in VALIDARI_ROMANA_CURAT.items())
    assert set(VALIDARI_ROMANA_CURAT.values()) < set(AMPRENTE)


def test_cu_r1_implicit_oprit(tmp_path):
    validari, amprente = _validari(tmp_path)
    e = ExamenRomana(validari=validari, amprente=amprente, set_ascuns=str(tmp_path / "nu_exista.jsonl"))
    assert e.cu_r1 is False
    scoruri = e.examineaza(ModelFals(), None)
    assert "r1_ascuns" not in scoruri  # setul (care nici nu există) nu se citește


def test_cu_r1_noteaza_setul(tmp_path):
    validari, amprente = _validari(tmp_path)
    perechi = [{"id": "d1", "fel": "da_nu", "prompt": "Este?", "raspuns": "Da.", "cheie": ["Da"], "subiect": "",
                "text": ""},
               {"id": "d2", "fel": "da_nu", "prompt": "Este?", "raspuns": "Nu.", "cheie": ["Nu"], "subiect": "",
                "text": ""}]
    s = tmp_path / "ascuns.jsonl"
    s.write_text("".join(json.dumps(p, ensure_ascii=False) + "\n" for p in perechi), encoding="utf-8")
    e = ExamenRomana(validari=validari, set_ascuns=str(s), cu_r1=True, amprente={**amprente, str(s): sha256(s)})
    scoruri = e.examineaza(ModelFals(), None)
    assert scoruri["r1_intrebari"] == 2 and 0 <= scoruri["r1_ascuns"] <= 100
    s.write_text("", encoding="utf-8")  # setul schimbat → refuz
    with pytest.raises(AmprentaGresita):
        e.examineaza(ModelFals(), None)


def test_modulul_nu_importa_din_kronos():
    arbore = ast.parse((RADACINA / "module" / "examen_romana.py").read_text(encoding="utf-8"))
    importuri = [n.module for n in ast.walk(arbore) if isinstance(n, ast.ImportFrom)]
    importuri += [a.name for n in ast.walk(arbore) if isinstance(n, ast.Import) for a in n.names]
    assert not [m for m in importuri if m and (m == "kronos" or m.startswith("kronos."))]


def test_nu_e_in_nicio_configurare():
    pus = [c.name for c in (RADACINA / "config").rglob("*.toml") if "examen_romana" in c.read_text(encoding="utf-8")]
    assert pus == []
