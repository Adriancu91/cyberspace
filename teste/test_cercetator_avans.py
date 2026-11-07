"""S91: cercetătorul cu model trimis în avans (unelte/cercetator_avans.py), pe modele minuscule, pe procesor."""

from __future__ import annotations

import ast
import json
import tomllib

import pytest

from kronos.config import citeste_config
from teste.test_cap_coada import RADACINA
from unelte import cercetator_avans as ca

CERCETATOR_PROBA = """[porturi.cercetator]
modul = "module.cercetator_aleator:CercetatorAleator"
[porturi.cercetator.setari]
samanta = 1
[porturi.cercetator.setari.spatiu.model]
ordin = [1, 2, 3, 4, 5, 6]
netezire = [0.01, 0.1, 0.5, 1.0, 2.0]
"""


def _text_proba() -> str:
    return (RADACINA / "config" / "proba.toml").read_text(encoding="utf-8").replace(
        'modul = "module.interfata_consola:InterfataConsola"',
        'modul = "module.interfata_consola:InterfataConsola"\nsetari = { tacut = true }').replace(
        "propozitii = 4000", "propozitii = 300")


def _configurari(tmp_path, monkeypatch, spatiu='{ model = { netezire = [0.1, 0.5, 2.0], ordin = [2, 3] } }'):
    monkeypatch.chdir(tmp_path)
    text = _text_proba()
    assert CERCETATOR_PROBA in text
    mic = text.replace(CERCETATOR_PROBA, '[porturi.cercetator]\nmodul = "module.cercetator_local:CercetatorLocal"\n'
                       f'setari = {{ amesteca = false, strangere = true, spatiu = {spatiu} }}\n')
    mic = mic.replace('nume = "proba"', 'nume = "avans_mic"')
    mare = text.replace('nume = "proba"', 'nume = "avans_mare"').replace(
        "propozitii = 300", "propozitii = 2000")
    (tmp_path / "mic.toml").write_text(mic, encoding="utf-8")
    (tmp_path / "mare.toml").write_text(mare, encoding="utf-8")
    return citeste_config(tmp_path / "mic.toml"), citeste_config(tmp_path / "mare.toml")


def test_proba_nu_antreneaza_si_nu_scrie(tmp_path, monkeypatch, capsys):
    _configurari(tmp_path, monkeypatch)
    cod = ca.main(["--config-mic", "mic.toml", "--config-mare", "mare.toml", "--incercari", "4",
                   "--minute-pe-incercare", "0.05", "--iesire", "iesire"])
    assert cod == 0
    assert "PROBA (nimic antrenat, nimic scris)" in capsys.readouterr().out
    assert sorted(p.name for p in tmp_path.iterdir()) == ["mare.toml", "mic.toml"]  # nici iesire/, nici lucru/


def test_n_incercari_clasament_castigator_si_propunere(tmp_path, monkeypatch):
    mic, mare = _configurari(tmp_path, monkeypatch)
    r = ca.ruleaza(mic, mare, 5, 0.05, tmp_path / "iesire")
    cl = r["clasament"]
    assert r["incercari_facute"] == 5 and len(cl) == 5
    assert len({json.dumps(x["setari"], sort_keys=True) for x in cl}) == 5  # nicio rețetă repetată
    assert cl[-1]["schimbari"] == {} or any(x["schimbari"] == {} for x in cl)  # punctul de plecare e în clasament
    scoruri = [x["scor"] for x in cl if x["scor"] is not None]
    assert r["mai_mic_e_mai_bun"] is True and cl[0]["scor"] == min(scoruri) and r["castigator"] == cl[0]["id"]
    assert r["pornire"]["descriere"] == ca.FARA_PORNIRE
    # propunerea = configurarea mare cu DOAR setările câștigătorului
    iesire = tmp_path / "iesire"
    propusa = tomllib.loads((iesire / "propunere_mare.toml").read_text(encoding="utf-8"))
    asteptat = tomllib.loads((tmp_path / "mare.toml").read_text(encoding="utf-8"))
    for port, setari in cl[0]["schimbari"].items():
        asteptat["porturi"][port]["setari"].update(setari)
    assert propusa == asteptat
    assert cl[0]["schimbari"], "cu netezire 0,1 / ordin 2–3 câștigătorul nu e punctul de plecare (ordin 1)"
    diff = (iesire / "propunere_mare.diff").read_text(encoding="utf-8")
    schimbate = [l for l in diff.splitlines() if l[:1] in "+-" and not l.startswith(("+++", "---", "+#"))]
    assert len(schimbate) == 2 and all("setari = {" in l for l in schimbate)  # o singură linie scoasă + pusă
    md = (iesire / "clasament.md").read_text(encoding="utf-8")
    assert "NU a fost rulată" in md and md.count("\n| ") == 6  # antetul + 5 rânduri
    assert json.loads((iesire / "clasament.json").read_text(encoding="utf-8"))["castigator"] == r["castigator"]


def test_nimic_in_lucru_in_afara_iesirii_si_refuz_a_doua_oara(tmp_path, monkeypatch):
    mic, mare = _configurari(tmp_path, monkeypatch)
    ca.ruleaza(mic, mare, 2, 0.05, tmp_path / "iesire")
    assert not (tmp_path / "lucru").exists()
    assert sorted(p.name for p in tmp_path.iterdir()) == ["iesire", "mare.toml", "mic.toml"]
    assert (tmp_path / "iesire" / "kronos_lucru" / "jurnal" / "experimente.jsonl").exists()
    with pytest.raises(ca.Refuz, match="există deja"):
        ca.ruleaza(mic, mare, 2, 0.05, tmp_path / "iesire")


def test_amprentele_examenului_se_copiaza(tmp_path, monkeypatch):
    mic, mare = _configurari(tmp_path, monkeypatch)
    (tmp_path / "lucru").mkdir()
    (tmp_path / "lucru" / "amprente.json").write_text(json.dumps({"module.examen_bpb.ExamenBpb": "0" * 64}),
                                                      encoding="utf-8")
    # examenul „schimbat” față de amprenta copiată → paznicul anulează toate încercările → nimic de propus
    with pytest.raises(ca.Refuz, match="nicio încercare"):
        ca.ruleaza(mic, mare, 2, 0.05, tmp_path / "iesire")
    fise = (tmp_path / "iesire" / "kronos_lucru" / "jurnal" / "experimente.jsonl").read_text(encoding="utf-8")
    assert "s-a schimbat de la ultima aprobare" in fise
    assert not (tmp_path / "iesire" / "propunere_mare.toml").exists()


@pytest.mark.parametrize("spatiu, mesaj", [
    ('{ model = { n_emb = [64, 128] } }', "mărimea/identitatea modelului"),
    ('{ model = { lot = [8, 16] } }', "nu există în configurarea mare"),
    ('{ date = { propozitii = [100, 200] } }', None),
], ids=["marime", "lipsa_in_mare", "alt_port_permis"])
def test_setarile_fara_sens_pe_mare_sunt_refuzate(tmp_path, monkeypatch, spatiu, mesaj):
    mic, mare = _configurari(tmp_path, monkeypatch, spatiu)
    if mesaj is None:
        assert ca.verifica_spatiu(mic, mare) == [("date", "propozitii")]
        return
    with pytest.raises(ca.Refuz, match=mesaj):
        ca.verifica_spatiu(mic, mare)
    cod = ca.main(["--config-mic", "mic.toml", "--config-mare", "mare.toml", "--incercari", "3",
                   "--minute-pe-incercare", "0.05", "--iesire", "iesire", "--porneste"])
    assert cod == 2 and not (tmp_path / "iesire").exists() and not (tmp_path / "lucru").exists()


def test_minute_peste_paznic_si_cale_stare_in_afara_refuzate(tmp_path, monkeypatch):
    mic, mare = _configurari(tmp_path, monkeypatch)
    with pytest.raises(ca.Refuz, match="timp_max_secunde"):
        ca.pregateste_config_mic(mic, tmp_path / "iesire", 60)
    mic.porturi["model"]["setari"] = {**mic.setari_port("model"), "cale_stare": "lucru/w2_mare/gpt_24.pt"}
    with pytest.raises(ca.Refuz, match="cale_stare"):
        ca.pregateste_config_mic(mic, tmp_path / "iesire", 0.05)


def test_castigatorul_respecta_directia_scorului():
    fise = [{"id": i, "setari": {"model": {"a": i}}, "scoruri": {"nota": s}, "decizie": "pastrat"}
            for i, s in [(1, 0.5), (2, 0.9), (3, 0.1)]] + [{"id": 4, "setari": {"model": {"a": 4}}, "decizie": "anulat"}]
    baza = {"model": {"a": 1}}
    assert [x["id"] for x in ca.clasament(fise, baza, "nota", mai_mic_e_mai_bun=True)] == [3, 1, 2, 4]
    sus = ca.clasament(fise, baza, "nota", mai_mic_e_mai_bun=False)
    assert [x["id"] for x in sus] == [2, 1, 3, 4] and sus[-1]["loc"] is None
    assert sus[0]["schimbari"] == {"model": {"a": 2}} and sus[1]["schimbari"] == {}
    with pytest.raises(ca.Refuz, match="repetat"):
        ca.clasament(fise + [{"id": 5, "setari": {"model": {"a": 3}}, "scoruri": {"nota": 1.0}}], baza, "nota", True)


def test_inlocuieste_setare_in_tabel_inline_si_in_sectiune():
    text = ('[porturi.model]\nmodul = "m:M"\nsetari = { lot = 4, rata_invatare = 0.00001, optimizator = "adamw" }\n'
            '[porturi.date.setari]\nlot = 9\n')
    nou = ca.inlocuieste_setare(text, "model", "rata_invatare", 2e-5)
    nou = ca.inlocuieste_setare(nou, "model", "optimizator", "muon")
    nou = ca.inlocuieste_setare(nou, "date", "lot", 12)
    assert nou == ('[porturi.model]\nmodul = "m:M"\nsetari = { lot = 4, rata_invatare = 2e-05, optimizator = "muon" }\n'
                   '[porturi.date.setari]\nlot = 12\n')
    with pytest.raises(ca.Refuz, match="exact o dată"):
        ca.inlocuieste_setare(text, "model", "nu_exista", 1)


def test_propunerea_pe_linia_mare_reala_schimba_doar_rata():
    mare = citeste_config(RADACINA / "config" / "conv_w2_mare_24f.toml")
    text, diff = ca.scrie_propunere(mare, {"model": {"rata_invatare": 2e-5, "incalzire_pasi": 500}}, "antet")
    assert tomllib.loads(text)["porturi"]["model"]["setari"]["rata_invatare"] == 2e-5
    schimbate = [l for l in diff.splitlines() if l[:1] in "+-" and not l.startswith(("+++", "---", "+#"))]
    assert len(schimbate) == 2
    with pytest.raises(ca.Refuz, match="mărimea"):
        ca.scrie_propunere(mare, {"model": {"n_straturi": 6}}, "antet")


def test_unealta_nu_importa_din_module():
    arbore = ast.parse((RADACINA / "unelte" / "cercetator_avans.py").read_text(encoding="utf-8"))
    importuri = [n.module for n in ast.walk(arbore) if isinstance(n, ast.ImportFrom)] + [
        a.name for n in ast.walk(arbore) if isinstance(n, ast.Import) for a in n.names]
    assert not [m for m in importuri if m and (m == "module" or m.startswith("module."))]
