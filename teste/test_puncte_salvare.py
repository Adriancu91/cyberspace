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
    # (S88, C-86: `sterge` există acum, aprobat de Adrian; `lista` tot nu șterge nimic — verificat mai sus.)


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


# --- S88 (7 nov 2026, C-86): comanda `sterge` --------------------------------------------------------------------

def _lista_fisier(r: Path) -> Path:
    return ps.lista(r, r / "config" / "puncte_salvare.toml", acum=datetime(2026, 11, 6, 22, 40))


def _sterge(r: Path, lista: Path, **k):
    return ps.sterge(r, lista, r / "config" / "puncte_salvare.toml", acum=datetime(2026, 11, 7, 11, 0), **k)


def test_sterge_proba_nu_sterge_nimic(proiect):
    lista = _lista_fisier(proiect)
    inainte = _sume(proiect)
    rez = _sterge(proiect, lista)
    assert _sume(proiect) == inainte                       # nimic șters, nimic scris
    rezultate = {i["cale"]: i["rezultat"] for i in rez["fisiere"]}
    for n in (1, 3, 8, 10):
        assert rezultate[f"lucru/stocare/modele/experiment_{n}.pt"] == "s-ar șterge (proba)", n
    assert rezultate["lucru/linia_a/gpt.pt"].startswith("refuzat")
    assert rez["total"]["sterse_sau_de_sters"] == 4 and rez["proba"] is True


def test_sterge_refuza_rezervele_gpt_pt_export_si_numitele(proiect):
    lista = _lista_fisier(proiect)
    date = json.loads(lista.read_text(encoding="utf-8"))
    _scrie(proiect / "lucru" / "export" / "experiment_1.pt", b"export")
    _scrie(proiect / "lucru" / "altundeva" / "experiment_3.pt", b"altundeva")
    extra = [{"cale": c, "octeti": 1, "sha256": "x", "clasa": ps.SE_POATE_STERGE}
             for c in ("lucru/export/experiment_1.pt", "lucru/altundeva/experiment_3.pt")]
    for r in date["fisiere"]:
        r["clasa"] = ps.SE_POATE_STERGE                    # o listă „stricată”: totul pare de șters
    date["fisiere"] += extra
    lista.write_text(json.dumps(date), encoding="utf-8")
    rez = _sterge(proiect, lista, da_sterge=True)
    rezultate = {i["cale"]: i["rezultat"] for i in rez["fisiere"]}
    pastrate = {
        "lucru/stocare/modele/experiment_4.pt": "rezervă",           # din config
        "lucru/stocare/modele/experiment_7.pt": "în uz",
        "lucru/stocare/modele/experiment_2.pt": "câștigătorul",
        "lucru/stocare/modele/experiment_5.pt": "câștigătorul",
        "lucru/stocare/modele/experiment_6.pt": "pre-înregistrarea deschisă",
        "lucru/stocare/modele/experiment_9.pt": "aprobat",
        "lucru/stocare/modele/experiment_99.pt": "jurnal",
        "lucru/linia_a/gpt.pt": "afara",
        "lucru/rezerva/gpt.pt": "afara",
        "lucru/export/experiment_1.pt": "afara",
        "lucru/altundeva/experiment_3.pt": "afara",
    }
    for cale, semn in pastrate.items():
        assert (proiect / cale).exists(), cale
        assert rezultate[cale].startswith("refuzat"), cale
        if semn != "afara":
            assert semn in rezultate[cale], (cale, rezultate[cale])
    for n in (1, 3, 8, 10):
        assert not (proiect / f"lucru/stocare/modele/experiment_{n}.pt").exists(), n
        assert rezultate[f"lucru/stocare/modele/experiment_{n}.pt"] == "șters"


def test_sterge_refuza_rezervele_fixe_chiar_fara_config(proiect):
    leg = ps.legaturi_jurnal([_fisa(12, "x", 0.5, decizie="respins")] +
                             [_fisa(n, "x", 0.6, decizie="respins") for n in (459, 477, 513)])
    config = {"experimente": [], "model_in_uz": None, "fisiere": []}
    num = {"cai": {}, "experimente": {}, "dosare": {}}
    for n in (459, 477, 513):
        assert "rezervă" in ps.motiv_refuz(f"lucru/stocare/modele/experiment_{n}.pt", proiect, leg, config, num)
        assert "rezervă" in ps.motiv_refuz(f"lucru/stocare/modele/experiment_{n}.pt", proiect,
                                           ps.legaturi_jurnal([]), config, num)  # și fără fișă
    assert ps.motiv_refuz("lucru/stocare/modele/experiment_12.pt", proiect, leg, config, num) is None
    assert "jurnal" in ps.motiv_refuz("lucru/stocare/modele/experiment_12.pt", proiect,
                                      ps.legaturi_jurnal([]), config, num)
    for cale in ("lucru/cod_c1/gpt.pt", "lucru/w2_mare/gpt_24.pt", "lucru/stocare/modele/gpt.pt",
                 "lucru/stocare/modele/../../export/experiment_12.pt"):
        assert ps.motiv_refuz(cale, proiect, leg, config, num) is not None, cale


def test_sterge_sha_diferit_nu_sterge(proiect):
    lista = _lista_fisier(proiect)
    schimbat = proiect / "lucru" / "stocare" / "modele" / "experiment_1.pt"
    schimbat.write_bytes(b"alt continut")
    rez = _sterge(proiect, lista, da_sterge=True)
    rezultate = {i["cale"]: i["rezultat"] for i in rez["fisiere"]}
    assert schimbat.exists()
    assert rezultate["lucru/stocare/modele/experiment_1.pt"].startswith("nu șters: SHA-256 diferit")
    assert not (proiect / "lucru" / "stocare" / "modele" / "experiment_3.pt").exists()


def test_sterge_jurnalul_se_scrie_inainte_de_stergere(proiect, monkeypatch):
    lista = _lista_fisier(proiect)
    jurnal = proiect / "lucru" / "puncte_salvare" / "sterse_2026-11-07.json"
    vazute = []
    original = Path.unlink

    def unlink_verificat(self, *a, **k):
        if self.suffix != ".pt":
            return original(self, *a, **k)
        assert jurnal.exists(), "jurnalul ștergerii lipsește înainte de ștergere"
        date = json.loads(jurnal.read_text(encoding="utf-8"))
        intrare = next(i for i in date["fisiere"] if (proiect / i["cale"]).resolve() == self.resolve())
        assert intrare["rezultat"] == "urmează să fie șters"
        assert intrare["sha256"] and intrare["octeti"] > 0 and "val_bpb" in intrare
        vazute.append(self.name)
        return original(self, *a, **k)

    monkeypatch.setattr(Path, "unlink", unlink_verificat)
    rez = _sterge(proiect, lista, da_sterge=True)
    assert sorted(vazute) == sorted(f"experiment_{n}.pt" for n in (1, 3, 8, 10))
    final = json.loads(jurnal.read_text(encoding="utf-8"))
    assert final["total"]["sterse_sau_de_sters"] == 4 and rez["jurnal"] == str(jurnal)
    with pytest.raises(FileExistsError):                  # nu scrie peste un jurnal vechi
        _sterge(proiect, lista, da_sterge=True)


def test_sterge_cap_coada_main_e_proba_implicit(proiect, monkeypatch, capsys):
    monkeypatch.chdir(proiect)
    lista = _lista_fisier(proiect)
    inainte = _sume(proiect)
    assert ps.main(["sterge", "--lista", str(lista), "--doar", "intermediare"]) == 0
    assert _sume(proiect) == inainte
    assert '"sterse_sau_de_sters": 4' in capsys.readouterr().out
