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


# ---- S92: modul relativ (factori față de rețetă) --------------------------------------------------------------------

SPATIU_RELATIV = '{ model = { netezire = [0.1, 0.5, 2.0], ordin = [2, 3] } }'


def _configurari_relative(tmp_path, monkeypatch, netezire_mare="0.5", spatiu=SPATIU_RELATIV):
    mic, _ = _configurari(tmp_path, monkeypatch, spatiu)
    text = (tmp_path / "mare.toml").read_text(encoding="utf-8")
    assert "netezire = 1.0" in text
    (tmp_path / "mare.toml").write_text(text.replace("netezire = 1.0", f"netezire = {netezire_mare}"), encoding="utf-8")
    return mic, citeste_config(tmp_path / "mare.toml")


def test_aplica_factor_rotunjeste():
    assert ca.aplica_factor(1000, 0.5) == 500 and ca.aplica_factor(1000, 2.0) == 2000
    assert ca.aplica_factor(3, 0.5) == 2 and ca.aplica_factor(1, 0.1) == 1  # întreg, cel puțin 1
    assert ca.aplica_factor(0.00001, 4.0) == 4e-05 and ca.aplica_factor(0.00003, 1 / 3) == 1e-05  # 3 cifre
    assert isinstance(ca.aplica_factor(1000, 0.5), int) and isinstance(ca.aplica_factor(1.0, 2), float)


def test_relativ_factorul_pe_ambele_modele_si_propunerea(tmp_path, monkeypatch):
    mic, mare = _configurari_relative(tmp_path, monkeypatch)
    r = ca.ruleaza(mic, mare, 6, 0.05, tmp_path / "iesire", relativ=True, scara=("netezire",))
    cl = r["clasament"]
    assert r["relativ"]["model.netezire"]["mic"] == 1.0 and r["relativ"]["model.netezire"]["mare"] == 0.5
    for x in cl:  # pe modelul mic s-a încercat valoarea mică × factor; pe cel mare ar fi valoarea mare × factor
        info = x["relativ"]["model.netezire"]
        assert x["setari"]["model"]["netezire"] == info["mic"] == ca.aplica_factor(1.0, info["factor"])
        assert info["mare"] == ca.aplica_factor(0.5, info["factor"]) and info["factor"] in (1.0, 0.1, 0.5, 2.0)
    assert {x["relativ"]["model.netezire"]["factor"] for x in cl} == {1.0, 0.1, 0.5, 2.0}
    castigator = cl[0]
    asteptat_mare = {}
    for port, setari in castigator["schimbari"].items():
        for k, v in setari.items():
            asteptat_mare.setdefault(port, {})[k] = (castigator["relativ"]["model.netezire"]["mare"]
                                                     if k == "netezire" else v)  # ordin: mutat ca valoare
    assert r["propunere"]["schimbari"] == asteptat_mare and r["propunere"]["schimbari_pe_mic"] == castigator["schimbari"]
    propusa = tomllib.loads((tmp_path / "iesire" / "propunere_mare.toml").read_text(encoding="utf-8"))
    asteptat = tomllib.loads((tmp_path / "mare.toml").read_text(encoding="utf-8"))
    for port, setari in asteptat_mare.items():
        asteptat["porturi"][port]["setari"].update(setari)
    assert propusa == asteptat  # restul fișierului identic
    md = (tmp_path / "iesire" / "clasament.md").read_text(encoding="utf-8")
    assert "×0.1 (mic 0.1, mare 0.05)" in md


def test_relativ_refuza_factor_si_valoare_lipsa(tmp_path, monkeypatch):
    mic, mare = _configurari_relative(tmp_path, monkeypatch, spatiu='{ model = { netezire = [0.5, -1.0] } }')
    with pytest.raises(ca.Refuz, match="nu e un număr pozitiv"):
        ca.setari_relative(mic, mare, ("netezire",))
    mic, mare = _configurari_relative(tmp_path, monkeypatch, spatiu='{ model = { netezire = [0.5, 0] } }')
    with pytest.raises(ca.Refuz, match="nu e un număr pozitiv"):
        ca.setari_relative(mic, mare, ("netezire",))
    mic, mare = _configurari_relative(tmp_path, monkeypatch, netezire_mare='"multa"')
    with pytest.raises(ca.Refuz, match="valoare numerică"):
        ca.setari_relative(mic, mare, ("netezire",))
    cod = ca.main(["--config-mic", "mic.toml", "--config-mare", "mare.toml", "--incercari", "3",
                   "--minute-pe-incercare", "0.05", "--iesire", "iesire", "--relativ", "--scara", "netezire",
                   "--porneste"])
    assert cod == 2 and not (tmp_path / "iesire").exists()
    mare.porturi["model"]["setari"] = {"ordin": 1}  # setarea lipsește cu totul din configurarea mare
    with pytest.raises(ca.Refuz, match="nu există în configurarea mare"):
        ca.verifica_spatiu(mic, mare)
    with pytest.raises(ca.Refuz, match="valoare numerică"):
        ca.setari_relative(mic, mare, ("netezire",))


def test_fara_setari_cu_scara_relativ_da_aceleasi_rezultate(tmp_path, monkeypatch):
    mic, mare = _configurari(tmp_path, monkeypatch)
    vechi = ca.ruleaza(mic, mare, 4, 0.05, tmp_path / "a")
    nou = ca.ruleaza(mic, mare, 4, 0.05, tmp_path / "b", relativ=True, scara=())
    assert vechi["incercari_facute"] == nou["incercari_facute"] == 4
    assert [(x["schimbari"], x["scor"]) for x in vechi["clasament"]] == [(x["schimbari"], x["scor"]) for x in nou["clasament"]]
    assert vechi["propunere"]["schimbari"] == nou["propunere"]["schimbari"]
    assert (tmp_path / "a" / "propunere_mare.toml").read_text(encoding="utf-8").split("\n", 4)[4] == \
        (tmp_path / "b" / "propunere_mare.toml").read_text(encoding="utf-8").split("\n", 4)[4]


def test_relativ_porneste_mereu_din_acelasi_fisier(tmp_path, monkeypatch):
    mic, mare = _configurari_relative(tmp_path, monkeypatch)
    mic.porturi["model"]["setari"] = {**mic.setari_port("model"), "cale_stare": "lucru/w2_mare/gpt_24.pt"}
    relative = ca.setari_relative(mic, mare, ("netezire",))
    noua = ca.pregateste_relativ(mic, (tmp_path / "iesire").resolve(), relative)
    model = noua.setari_port("model")
    assert model["stare_de_pornire"] == "lucru/w2_mare/gpt_24.pt"
    assert ca._sub(ca.Path(model["cale_stare"]), tmp_path / "iesire")
    assert noua.setari_port("cercetator")["spatiu"]["model"]["netezire"] == [0.1, 0.5, 2.0]
    assert mic.setari_port("model")["cale_stare"] == "lucru/w2_mare/gpt_24.pt"  # originalul neatins
    ca.pregateste_config_mic(noua, (tmp_path / "iesire").resolve(), 0.05)  # nu mai e refuzat
    with pytest.raises(ca.Refuz, match="nu există"):  # fișierul de pornire lipsește → nu pornește de la zero
        ca.ruleaza(mic, mare, 2, 0.05, tmp_path / "iesire", relativ=True, scara=("netezire",))


def test_proba_relativ_arata_retetele_si_nu_scrie(tmp_path, monkeypatch, capsys):
    _configurari_relative(tmp_path, monkeypatch)
    cod = ca.main(["--config-mic", "mic.toml", "--config-mare", "mare.toml", "--incercari", "4",
                   "--minute-pe-incercare", "0.05", "--iesire", "iesire", "--relativ", "--scara", "netezire"])
    out = capsys.readouterr().out
    assert cod == 0 and "modul RELATIV" in out
    assert "1. punct de plecare: model.netezire ×1 (mic 1.0, mare 0.5)" in out
    assert "model.netezire ×0.1 (mic 0.1, mare 0.05)" in out and out.count("\n    ") >= 5
    assert sorted(p.name for p in tmp_path.iterdir()) == ["mare.toml", "mic.toml"]
    assert ca.main(["--config-mic", "mic.toml", "--config-mare", "mare.toml", "--incercari", "4",
                    "--minute-pe-incercare", "0.05", "--iesire", "iesire", "--scara", "netezire"]) == 2


def test_configurarea_mica_de_6_straturi():
    mic = citeste_config(RADACINA / "config" / "avans_24_mic6.toml")
    mare = citeste_config(RADACINA / "config" / "conv_w2_mare_24f.toml")
    relative = ca.setari_relative(mic, mare)
    assert [aplica for aplica in ca.spatiu_absolut(ca._spatiu_cercetator(mic), relative)["model"].values()] == [
        [5e-06, 2e-05, 4e-05], [500, 2000]]
    a = tomllib.loads((RADACINA / "config" / "avans_24_mic6.toml").read_text(encoding="utf-8"))
    b = tomllib.loads((RADACINA / "config" / "conv_w2_mare_24f.toml").read_text(encoding="utf-8"))
    for t in (a, b):
        t["platforma"].pop("nume"), t["antrenare_lunga"].pop("eticheta"), t["porturi"].pop("cercetator")
    ma, mb = a["porturi"]["model"].pop("setari"), b["porturi"]["model"].pop("setari")
    assert a == b and {k for k in ma if ma[k] != mb.get(k)} == {"n_straturi", "cale_stare"} and set(ma) == set(mb)
    assert ma["n_straturi"] == 6 and ma["cale_stare"] == "lucru/avans/mic6/gpt.pt"


# ---- S94: rețete strict separate (--separat) ------------------------------------------------------------------------


def test_separat_fiecare_reteta_o_singura_schimbare(tmp_path, monkeypatch):
    mic, mare = _configurari_relative(tmp_path, monkeypatch)
    relative = ca.setari_relative(mic, mare, ("netezire",))
    retete = ca.retete_separate(ca.pregateste_relativ(mic, (tmp_path / "iesire").resolve(), relative))
    baza = retete[0]["setari"]["model"]
    assert [(r["setari"]["model"]["netezire"], r["setari"]["model"]["ordin"]) for r in retete] == [
        (1.0, 1), (0.1, 1), (0.5, 1), (2.0, 1), (1.0, 2), (1.0, 3)]
    for r in retete[1:]:
        assert len([k for k in baza if r["setari"]["model"][k] != baza[k]]) == 1


def test_separat_ruleaza_fiecare_din_baza_si_refuza_alt_numar(tmp_path, monkeypatch):
    mic, mare = _configurari_relative(tmp_path, monkeypatch)
    with pytest.raises(ca.Refuz, match="--incercari 6"):
        ca.ruleaza_separat(mic, mare, 5, 0.05, tmp_path / "iesire", relativ=True, scara=("netezire",))
    assert not (tmp_path / "iesire" / "incercari").exists()
    r = ca.ruleaza_separat(mic, mare, 6, 0.05, tmp_path / "iesire", relativ=True, scara=("netezire",))
    cl = r["clasament"]
    assert r["separat"] and r["incercari_facute"] == 6 and sorted(x["id"] for x in cl) == [1, 2, 3, 4, 5, 6]
    for x in cl:  # nicio rețetă combinată: față de bază, cel mult o schimbare
        n = sum(len(s) for s in x["schimbari"].values())
        assert n == (0 if x["id"] == 1 else 1)
    for k in range(1, 7):  # fiecare cu jurnalul propriu, un singur experiment
        jurnale = list((tmp_path / "iesire" / "incercari" / str(k) / "kronos_lucru").glob("*"))
        assert jurnale
    assert (tmp_path / "iesire" / "propunere_mare.toml").exists()
    with pytest.raises(ca.Refuz, match="există deja"):
        ca.ruleaza_separat(mic, mare, 6, 0.05, tmp_path / "iesire", relativ=True, scara=("netezire",))
    assert not (tmp_path / "lucru").exists()  # nimic scris în afara ieșirii


def test_separat_proba_si_main(tmp_path, monkeypatch, capsys):
    _configurari_relative(tmp_path, monkeypatch)
    argv = ["--config-mic", "mic.toml", "--config-mare", "mare.toml", "--minute-pe-incercare", "0.05",
            "--iesire", "iesire", "--relativ", "--scara", "netezire", "--separat"]
    assert ca.main(argv + ["--incercari", "6"]) == 0
    out = capsys.readouterr().out
    assert "--separat" in out and "6. o singură schimbare: model.ordin = 3" in out
    assert sorted(p.name for p in tmp_path.iterdir()) == ["mare.toml", "mic.toml"]
    assert ca.main(argv + ["--incercari", "4", "--porneste"]) == 2 and not (tmp_path / "iesire").exists()


class _OrchestratorCache:
    """Orchestrator de jucărie (S94, --cache): notează director_cache din fiecare încercare și dă un scor."""
    vazute: list[str] = []

    def __init__(self, config):
        self.config = config
        self.cel_mai_bun = None
        self.examen = type("E", (), {"scor_principal": "scor", "mai_mic_e_mai_bun": True})()

    def ruleaza(self, numar_experimente=0):
        model = self.config.setari_port("model")
        _OrchestratorCache.vazute.append(model["director_cache"])
        return [{"setari": {"model": dict(model)}, "scoruri": {"scor": float(len(_OrchestratorCache.vazute))}}]


def test_cache_dat_e_folosit_de_toate_incercarile(tmp_path, monkeypatch, capsys):
    mic, mare = _configurari_relative(tmp_path, monkeypatch)
    mic.porturi["model"]["setari"] = {**mic.setari_port("model"), "director_cache": "cache_vechi"}
    iesire = (tmp_path / "iesire").resolve()
    cache = tmp_path / "cache_comun"
    cache.mkdir()
    # fără --cache: ca înainte, <iesire>/cache
    assert ca.pregateste_config_mic(mic, iesire, 0.05).setari_port("model")["director_cache"] == \
        str((iesire / "cache").resolve())
    assert ca.pregateste_config_mic(mic, iesire, 0.05, cache).setari_port("model")["director_cache"] == \
        str(cache.resolve())
    _OrchestratorCache.vazute = []
    ca.ruleaza_separat(mic, mare, 6, 0.05, iesire, orchestrator_cls=_OrchestratorCache, relativ=True,
                       scara=("netezire",), cache=cache)
    assert _OrchestratorCache.vazute == [str(cache.resolve())] * 6
    _OrchestratorCache.vazute = []
    ca.ruleaza_separat(mic, mare, 6, 0.05, tmp_path / "iesire2", orchestrator_cls=_OrchestratorCache, relativ=True,
                       scara=("netezire",))
    assert _OrchestratorCache.vazute == [str((tmp_path / "iesire2" / "cache").resolve())] * 6
    assert sorted(p.name for p in cache.iterdir()) == []  # unealta n-a scris nimic în cache-ul dat
    argv = ["--config-mic", "mic.toml", "--config-mare", "mare.toml", "--minute-pe-incercare", "0.05",
            "--iesire", "iesire3", "--relativ", "--scara", "netezire", "--separat", "--incercari", "6"]
    assert ca.main(argv + ["--cache", "nu_exista", "--porneste"]) == 2 and not (tmp_path / "iesire3").exists()
    assert ca.main(argv + ["--cache", "cache_comun"]) == 0
    assert f"cache-ul de simboluri: {cache.resolve()}" in capsys.readouterr().out


def test_configurarea_mica_s94():
    mic = citeste_config(RADACINA / "config" / "avans_24_mic6r.toml")
    mare = citeste_config(RADACINA / "config" / "conv_w2_mare_24r.toml")
    relative = ca.setari_relative(mic, mare)
    retete = ca.retete_separate(ca.pregateste_relativ(mic, RADACINA / "lucru" / "avans" / "s94_mic", relative))
    info = [ca.info_relativ(r["setari"], relative) for r in retete]
    assert [(i["model.rata_invatare"]["mic"], i["model.incalzire_pasi"]["mic"]) for i in info] == [
        (1e-05, 1000), (5e-06, 1000), (2e-05, 1000), (4e-05, 1000), (1e-05, 2000)]
    assert [(i["model.rata_invatare"]["mare"], i["model.incalzire_pasi"]["mare"]) for i in info] == [
        (1e-05, 1000), (5e-06, 1000), (2e-05, 1000), (4e-05, 1000), (1e-05, 2000)]
    a = tomllib.loads((RADACINA / "config" / "avans_24_mic6.toml").read_text(encoding="utf-8"))
    b = tomllib.loads((RADACINA / "config" / "avans_24_mic6r.toml").read_text(encoding="utf-8"))
    r24 = tomllib.loads((RADACINA / "config" / "conv_w2_mare_24r.toml").read_text(encoding="utf-8"))
    assert b["porturi"]["examen"] == r24["porturi"]["examen"]
    assert b["platforma"]["nume"] == "avans_24_mic6r"
    assert b["porturi"]["model"]["setari"]["cale_stare"] == "lucru/avans/mic6r/gpt.pt"
    for t in (a, b):
        t["platforma"].pop("nume"), t["antrenare_lunga"].pop("eticheta"), t["porturi"].pop("examen")
        t["porturi"]["model"]["setari"].pop("cale_stare"), t["porturi"]["cercetator"]["setari"].pop("spatiu")
    assert a == b


def test_unealta_nu_importa_din_module():
    arbore = ast.parse((RADACINA / "unelte" / "cercetator_avans.py").read_text(encoding="utf-8"))
    importuri = [n.module for n in ast.walk(arbore) if isinstance(n, ast.ImportFrom)] + [
        a.name for n in ast.walk(arbore) if isinstance(n, ast.Import) for a in n.names]
    assert not [m for m in importuri if m and (m == "module" or m.startswith("module."))]
