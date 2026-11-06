"""S84 (6 nov 2026, C-85 pasul 1): lista punctelor de salvare `.pt` — doar listă, nimic șters sau schimbat."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path

import pytest

from unelte import puncte_salvare as ps


def _scrie(cale: Path, continut: bytes) -> None:
    cale.parent.mkdir(parents=True, exist_ok=True)
    cale.write_bytes(continut)


def _fisa(id_: int, linie: str, val: float, decizie: str = "pastrat", **alte) -> dict:
    return {"id": id_, "linie": linie, "decizie": decizie, "scoruri": {"val_bpb": val},
            "model_salvat": f"lucru/stocare/modele/experiment_{id_}.pt",
            "setari": {"model": {"cale_stare": f"lucru/{linie}/gpt.pt"}}, **alte}


@pytest.fixture
def proiect(tmp_path):
    r = tmp_path
    fise = [
        _fisa(1, "linia_a", 0.50),
        _fisa(2, "linia_a", 0.45),                       # câștigătorul liniei a
        _fisa(3, "linia_a", 0.60, decizie="respins"),
        _fisa(4, "linia_b", 0.70),                       # rezervă numită în config
        _fisa(5, "linia_b", 0.40),                       # câștigătorul liniei b
        _fisa(6, "linia_c", 0.80),                       # numit într-o pre-înregistrare deschisă
        _fisa(7, "linia_c", 0.30),
        _fisa(8, "linia_c", 0.90),                       # numit într-o pre-înregistrare ÎNCHISĂ → nu contează
        _fisa(9, "linia_c", 0.95),                       # numit într-o sarcină aprobat
        _fisa(10, "linia_c", 0.96),                      # numit într-o sarcină gata → nu contează
        {"id": 11, "linie": "examen_validari_ws", "decizie": "masurat",
         "module": {"elev": {"experiment": 1}}, "scoruri": {"bpb_romana_curat": 1.21, "bpb_cod_curat": 0.72}},
    ]
    _scrie(r / "lucru" / "jurnal" / "experimente.jsonl",
           "".join(json.dumps(f) + "\n" for f in fise).encode("utf-8"))
    for f in fise[:10]:
        _scrie(r / f["model_salvat"], f"model {f['id']}".encode() * 10)
    _scrie(r / "lucru" / "linia_a" / "gpt.pt", b"stare a")
    _scrie(r / "lucru" / "rezerva" / "gpt.pt", b"rezerva")          # rezervă numită pe cale
    _scrie(r / "lucru" / "fara_jurnal" / "ciudat.pt", b"necunoscut")
    _scrie(r / "lucru" / "stocare" / "modele" / "experiment_99.pt", b"fara fisa")
    _scrie(r / "lucru" / "cache" / "simboluri_abc.pt", b"cache")
    _scrie(r / "config" / "puncte_salvare.toml",
           b'experimente = [4]\nmodel_in_uz = 7\nfisiere = ["lucru/rezerva/gpt.pt"]\n')
    _scrie(r / "docs" / "preinregistrari" / "2026-11-01_deschisa.md", "# Deschisă\nfolosim #6\n".encode())
    _scrie(r / "docs" / "preinregistrari" / "2026-11-02_inchisa.md",
           "# Închisă\nfolosim #8\n\n## Ce a ieșit\nnimic\n".encode())
    _scrie(r / "plan" / "coada.md", (
        "# Coada\n\n### S1 — veche\n- stare: gata\n- ce faci: #10\n\n"
        "### S2 — vie\n- stare: **aprobat** (Adrian)\n- ce faci: examen pe experimentul #9\n").encode())
    return r


def _sume(radacina: Path) -> dict[str, str]:
    return {p.relative_to(radacina).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(radacina.rglob("*")) if p.is_file()}


def _lista(r: Path) -> dict:
    tinta = ps.lista(r, r / "config" / "puncte_salvare.toml", acum=datetime(2026, 11, 6, 22, 40))
    return {x["cale"]: x for x in json.loads(tinta.read_text(encoding="utf-8"))["fisiere"]}


def test_rezervele_numite_ies_mereu_pastreaza(proiect):
    l = _lista(proiect)
    assert l["lucru/stocare/modele/experiment_4.pt"]["clasa"] == ps.PASTREAZA   # din config, deși nu e câștigător
    assert l["lucru/stocare/modele/experiment_7.pt"]["clasa"] == ps.PASTREAZA   # modelul în uz
    assert "în uz" in l["lucru/stocare/modele/experiment_7.pt"]["motiv"]
    assert l["lucru/rezerva/gpt.pt"]["clasa"] == ps.PASTREAZA                   # cale din config


def test_castigatorii_si_cele_numite_in_texte_vii(proiect):
    l = _lista(proiect)
    assert l["lucru/stocare/modele/experiment_2.pt"]["clasa"] == ps.PASTREAZA   # câștigătorul liniei a
    assert l["lucru/stocare/modele/experiment_5.pt"]["clasa"] == ps.PASTREAZA   # câștigătorul liniei b
    assert l["lucru/stocare/modele/experiment_6.pt"]["clasa"] == ps.PASTREAZA   # pre-înregistrare deschisă
    assert l["lucru/stocare/modele/experiment_9.pt"]["clasa"] == ps.PASTREAZA   # sarcină aprobat
    for n in (1, 3, 8, 10):                                                      # închisă / gata nu contează
        assert l[f"lucru/stocare/modele/experiment_{n}.pt"]["clasa"] == ps.SE_POATE_STERGE, n
    assert l["lucru/linia_a/gpt.pt"]["clasa"] == ps.SE_POATE_STERGE
    assert l["lucru/stocare/modele/experiment_1.pt"]["scoruri"]["bpb_romana_curat"] == 1.21


def test_fara_jurnal_iese_necunoscut(proiect):
    l = _lista(proiect)
    for cale in ("lucru/fara_jurnal/ciudat.pt", "lucru/stocare/modele/experiment_99.pt", "lucru/cache/simboluri_abc.pt"):
        assert l[cale]["clasa"] == ps.NECUNOSCUT, cale


def test_mărimea_si_suma_fiecarui_fisier(proiect):
    l = _lista(proiect)
    p = proiect / "lucru" / "stocare" / "modele" / "experiment_1.pt"
    assert l["lucru/stocare/modele/experiment_1.pt"]["octeti"] == p.stat().st_size
    assert l["lucru/stocare/modele/experiment_1.pt"]["sha256"] == hashlib.sha256(p.read_bytes()).hexdigest()


def test_nu_sterge_si_nu_modifica_nimic(proiect):
    inainte = _sume(proiect)
    tinta = ps.lista(proiect, proiect / "config" / "puncte_salvare.toml", acum=datetime(2026, 11, 6, 22, 40))
    dupa = _sume(proiect)
    nou = tinta.relative_to(proiect).as_posix()
    assert set(dupa) - set(inainte) == {nou}          # singurul fișier nou e lista
    assert {k: v for k, v in dupa.items() if k != nou} == inainte
    with pytest.raises(FileExistsError):              # nu scrie peste o listă veche
        ps.lista(proiect, proiect / "config" / "puncte_salvare.toml", acum=datetime(2026, 11, 6, 22, 40))
    assert not hasattr(ps, "sterge")


def test_cap_coada_main_si_tabel(proiect, monkeypatch, capsys):
    monkeypatch.chdir(proiect)
    assert ps.main(["lista"]) == 0
    iesire = capsys.readouterr().out
    assert "Lista scrisă" in iesire and ps.SE_POATE_STERGE in iesire
    (fisier,) = (proiect / "lucru" / "puncte_salvare").glob("lista_*.json")
    assert ps.main(["tabel", str(fisier)]) == 0
    assert "experiment_1.pt" in capsys.readouterr().out


def test_configurarea_reala_are_rezervele_cerute():
    c = ps.citeste_config(Path(__file__).resolve().parents[1] / "config" / "puncte_salvare.toml")
    assert {459, 477, 513} <= set(c["experimente"]) and c["model_in_uz"] == 513
    assert {"lucru/cod_c1/gpt.pt", "lucru/w2_mare/gpt_24.pt"} <= set(c["fisiere"])
