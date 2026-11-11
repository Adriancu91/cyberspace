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


def test_doar_in_configurarile_aprobate():
    """S90: examenul nu era în nicio configurare. S93 (C-88 „Română da”, Adrian 7 nov 2026): doar în conv_w2_mare_24r.
    O configurare nouă cu examenul de română se adaugă aici doar cu sarcina care o cere."""
    pus = {c.name for c in (RADACINA / "config").rglob("*.toml") if "examen_romana" in c.read_text(encoding="utf-8")}
    assert pus == {"conv_w2_mare_24r.toml", "avans_24_mic6r.toml",  # S94 (8 nov 2026): modelul mic al testului Spearman
                   "conv_w2_mare_24s.toml",  # S95 (9 nov 2026): continuarea #536
                   "conv_w2_mare_24m.toml",  # S99 (10 nov 2026): Muon din #554
                   "conv_w2_mare_24n.toml",  # S100 (10 nov 2026): Muon ×20 din #554
                   "conv_w2_mare_24_bucati.toml"}  # S98 (11 nov 2026): copia de probă a lui 24r, nu se antrenează cu ea


# --- S93: portul `examen` = examen_romana prin orchestrator, paznicul, configurarea 24r ---------------------------

AMPRENTA_EXAMEN_BPB = "0ca9cf74498438062f9bb92b828c3c6a8c60c879393b2093d2ab7f5e441d3028"  # 8 nov 2026, înainte de S93


def _config_proba_romana(tmp_path: Path, monkeypatch, modul: str = "module.examen_romana:ExamenRomana"):
    """config/proba.toml (model n-gram, procesor) cu portul examen = examen_romana pe validări mici din tmp_path."""
    from kronos.config import citeste_config

    monkeypatch.chdir(tmp_path)
    validari, amprente = _validari(tmp_path)
    val = ", ".join(f'{n} = "{Path(c).as_posix()}"' for n, c in validari.items())
    amp = ", ".join(f'"{Path(c).as_posix()}" = "{h}"' for c, h in amprente.items())
    text = (RADACINA / "config" / "proba.toml").read_text(encoding="utf-8")
    vechi = 'modul = "module.examen_bpb:ExamenBpb"\n'
    assert text.count(vechi) == 1
    text = text.replace(vechi, f'modul = "{modul}"\nsetari = {{ caractere = 300, validari = {{ {val} }}, '
                               f'amprente = {{ {amp} }} }}\n')
    text = text.replace("buget_antrenare_secunde = 10", "buget_antrenare_secunde = 1")
    text = text.replace("propozitii = 4000", "propozitii = 600")
    text = text.replace('modul = "module.interfata_consola:InterfataConsola"',
                        'modul = "module.interfata_consola:InterfataConsola"\nsetari = { tacut = true }')
    fisier = tmp_path / "proba_romana.toml"
    fisier.write_text(text, encoding="utf-8")
    return citeste_config(fisier)


def test_portul_examen_decide_dupa_romana_bpb(tmp_path, monkeypatch):
    from kronos.orchestrator import Orchestrator

    config = _config_proba_romana(tmp_path, monkeypatch)
    o = Orchestrator(config)
    assert type(o.examen).__name__ == "ExamenRomana"
    assert (o.examen.scor_principal, o.examen.mai_mic_e_mai_bun) == ("romana_bpb", True)
    fise = o.ruleaza(3)
    masurate = [f for f in fise if f["decizie"] != "anulat"]
    assert len(masurate) >= 2, [f.get("motiv") for f in fise]
    assert all("romana_bpb" in f["scoruri"] and "val_bpb" not in f["scoruri"] for f in masurate)
    assert masurate[0]["decizie"] == "pastrat"
    for f in masurate[1:]:  # decizia: câștig = anterior − romana_bpb (mai mic = mai bun), peste prag_zgomot
        assert f["castig"] == pytest.approx(f["scor_anterior"] - f["scoruri"]["romana_bpb"])
        assert (f["decizie"] == "pastrat") == (f["castig"] > config.prag_zgomot)
    amprente = json.loads((config.director_lucru / "amprente.json").read_text(encoding="utf-8"))
    assert amprente == {"module.examen_romana.ExamenRomana": sha256(RADACINA / "module" / "examen_romana.py")}


def test_paznicul_refuza_examenul_de_romana_schimbat(tmp_path, monkeypatch):
    """O copie a clasei (alt pachet, în tmp_path): prima rulare îi memorează amprenta; după o schimbare → anulat."""
    import shutil

    from kronos.contracte import Propunere
    from kronos.orchestrator import Orchestrator

    pachet = tmp_path / "pachet_s93"
    pachet.mkdir()
    (pachet / "__init__.py").write_text("", encoding="utf-8")
    copie = pachet / "examen_romana_copie.py"
    shutil.copyfile(RADACINA / "module" / "examen_romana.py", copie)
    monkeypatch.syspath_prepend(str(tmp_path))
    config = _config_proba_romana(tmp_path, monkeypatch, "pachet_s93.examen_romana_copie:ExamenRomana")
    o = Orchestrator(config)
    assert o.experiment(Propunere("prima"))["decizie"] == "pastrat"
    assert o.experiment(Propunere("a doua", {"model": {"ordin": 2}}))["decizie"] != "anulat"
    with copie.open("a", encoding="utf-8") as f:
        f.write("\n# schimbare\n")
    fisa = Orchestrator(config).experiment(Propunere("după schimbare", {"model": {"ordin": 3}}))
    assert fisa["decizie"] == "anulat"
    assert "pachet_s93.examen_romana_copie.ExamenRomana" in fisa["motiv"] and "s-a schimbat" in fisa["motiv"]


def test_config_24r_difera_de_24g_doar_prin_campurile_s93():
    import tomllib

    g = tomllib.loads((RADACINA / "config" / "conv_w2_mare_24g.toml").read_text(encoding="utf-8"))
    r = tomllib.loads((RADACINA / "config" / "conv_w2_mare_24r.toml").read_text(encoding="utf-8"))
    assert r["platforma"]["nume"] == "w2_mare_24r"
    assert r["porturi"]["model"]["setari"]["cale_stare"] == "lucru/w2_mare_24r/gpt.pt"
    assert "C-88" in r["antrenare_lunga"]["eticheta"]
    assert r["porturi"]["examen"] == {"modul": "module.examen_romana:ExamenRomana",
                                      "setari": {"caractere": 100000, "cu_r1": False}}
    assert (g["platforma"]["nume"], g["porturi"]["model"]["setari"]["cale_stare"]) == \
        ("w2_mare_24g", "lucru/w2_mare_24g/gpt.pt")
    for d in (g, r):
        d["platforma"].pop("nume")
        d["porturi"]["model"]["setari"].pop("cale_stare")
        d["antrenare_lunga"].pop("eticheta")
        d["porturi"].pop("examen")
    assert g == r
    antet = (RADACINA / "config" / "conv_w2_mare_24r.toml").read_text(encoding="utf-8").split("[platforma]")[0]
    assert "examen de decizie: română, C-88" in antet


def test_examen_bpb_neschimbat():
    assert sha256(RADACINA / "module" / "examen_bpb.py") == AMPRENTA_EXAMEN_BPB
    import tomllib

    g = tomllib.loads((RADACINA / "config" / "conv_w2_mare_24g.toml").read_text(encoding="utf-8"))
    assert g["porturi"]["examen"]["modul"] == "module.examen_bpb:ExamenBpb"  # S89 neatins
