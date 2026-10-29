"""S49: variantele CCM pe placa video (module/calcul/variante/placa.py) și alegerea procesor/placă din reglaj.

Testele rulează fără placă (CUDA_VISIBLE_DEVICES=-1): același motor PyTorch pe `dispozitiv="cpu"` trebuie să dea ce dă
referința; fără CUDA, variantele de placă refuză să se încarce, iar `inferenta_ccm` rămâne pe procesor."""

import json

import numpy as np
import pytest

from module.calcul import banc, reglaj
from module.calcul import variante
from module.calcul.variante import placa
from module.inferenta_ccm import InferentaCCM
from module.inferenta_kgr1 import InferentaKGR1
from teste.test_ccm_banc import TEXTE, _scrie_sintetic

torch = pytest.importorskip("torch")

SIMBOLURI = [1, 5, 9, 60, 2]


@pytest.fixture(scope="module")
def fisiere(tmp_path_factory):
    d = tmp_path_factory.mktemp("ccm_placa")
    return [_scrie_sintetic(d / "f32.kgr", "f32"), _scrie_sintetic(d / "q8.kgr", "q8_0")]


def _pe_procesor(precizie):
    return lambda cale: placa.MotorPlaca(cale, precizie, "cpu")


def test_motorul_pytorch_fp32_e_acceptat_de_banc(fisiere):
    # 5 + 20 > context 16: și ramura fără cache
    v = banc.verifica(_pe_procesor("fp32"), fisiere, TEXTE, simboluri=20)
    assert v["acceptata"], v["motive"]
    assert v["dif_logits_max"] < 1e-4


@pytest.mark.parametrize("precizie", ["fp16", "bf16"])
def test_preciziile_mici_ruleaza_si_se_abat_mai_mult(fisiere, precizie):
    v32 = banc.verifica(_pe_procesor("fp32"), fisiere[:1], TEXTE, simboluri=8)
    v = banc.verifica(_pe_procesor(precizie), fisiere[:1], TEXTE, simboluri=8)
    assert len(v["cazuri"]) == 2 and v["dif_logits_max"] > v32["dif_logits_max"]
    m = placa.MotorPlaca(fisiere[0], precizie, "cpu")
    assert m.logits(SIMBOLURI).dtype == np.float32 and m.logits(SIMBOLURI).shape == (5, 64)
    assert m.octeti_greutati() > 0 and m.memorie_placa_mb() is None


def test_fara_placa_variantele_de_placa_refuza(fisiere, monkeypatch):
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)
    assert not placa.placa_disponibila()
    with pytest.raises(RuntimeError, match="fără placă"):
        variante.VARIANTE_PLACA["placa_fp32"](fisiere[0])
    with pytest.raises(ValueError):
        placa.MotorPlaca(fisiere[0], "fp8", "cpu")


def test_listele_de_variante():
    assert set(variante.VARIANTE_PLACA) == {"placa_fp32", "placa_fp16", "placa_bf16"}
    assert not set(variante.VARIANTE) & set(variante.VARIANTE_PLACA)
    assert variante.TOATE == {**variante.VARIANTE, **variante.VARIANTE_PLACA}


def _rezultat(v, fire_, total, acceptata=True):
    m = {"total": {"median": total}, "simboluri_pe_secunda": {"median": 64 / total}}
    return {"varianta": v, "fire": fire_, "acceptata": acceptata, "masurare": m,
            "verificare_model": {"dif_logits_max": 0.0}, "memorie_placa_mb": None}


def test_bancul_alege_separat_pe_procesor_si_pe_placa(monkeypatch):
    rez = {("referinta", "1"): _rezultat("referinta", "1", 2.5), ("referinta", "toate"): _rezultat("referinta", "toate", 3.4),
           ("placa_fp32", "toate"): _rezultat("placa_fp32", "toate", 1.5),
           ("placa_fp16", "toate"): _rezultat("placa_fp16", "toate", 1.0, acceptata=False)}
    monkeypatch.setattr(banc, "in_proces_nou", lambda v, f, *a, **k: dict(rez[(v, f)]))
    r = banc.toate("x.kgr", combinatii=list(rez))
    assert r["cea_mai_rapida_pe_procesor"] == {"varianta": "referinta", "fire": "1"}
    assert r["cea_mai_rapida_pe_placa"] == {"varianta": "placa_fp32", "fire": "toate"}  # fp16 respinsă, deși mai rapidă
    assert r["cea_mai_rapida_pe_total"] == {"varianta": "placa_fp32", "fire": "toate"}
    respinsa = next(x for x in r["rezultate"] if not x["acceptata"])
    assert "fata_de_referinta_total" not in respinsa
    assert r["rezultate"][2]["fata_de_referinta_total"] == pytest.approx(3.4 / 1.5)


def _banc_cu_placa(kgr, total_procesor=2.5, total_placa=1.5):
    rez = [_rezultat("referinta", "toate", total_procesor), _rezultat("placa_fp32", "toate", total_placa)]
    return {"kgr": str(kgr), "toleranta_logits": 1e-3, "rezultate": rez,
            "cea_mai_rapida_pe_procesor": {"varianta": "referinta", "fire": "toate"},
            "cea_mai_rapida_pe_placa": {"varianta": "placa_fp32", "fire": "toate"}}


def test_reglajul_tine_si_placa(fisiere):
    r = reglaj.din_banc(_banc_cu_placa(fisiere[1]), "test")
    assert r["operatii"]["inmultire"]["varianta"] == "referinta"
    assert r["placa"]["varianta"] == "placa_fp32" and r["alegere"] == "placa"
    assert r["placa"]["fata_de_procesor_total"] == pytest.approx(2.5 / 1.5)
    assert reglaj.din_banc(_banc_cu_placa(fisiere[1], 1.0, 1.5), "test")["alegere"] == "procesor"
    assert "placa" not in reglaj.din_banc({**_banc_cu_placa(fisiere[1]), "cea_mai_rapida_pe_placa": None}, "test")


@pytest.mark.parametrize("cu_placa,placa_aleasa,cuda,dispozitiv,motiv", [
    (False, True, True, "procesor", None),
    (True, True, True, "placa", None),
    (True, False, True, "procesor", "procesorul e mai rapid"),
    (True, True, False, "procesor", "fără placă video"),
], ids=["implicit_procesor", "placa_ceruta", "placa_mai_lenta", "fara_cuda"])
def test_alegerea_procesor_sau_placa(fisiere, tmp_path, monkeypatch, cu_placa, placa_aleasa, cuda, dispozitiv, motiv):
    monkeypatch.setattr(placa, "placa_disponibila", lambda: cuda)
    monkeypatch.setitem(variante.TOATE, "placa_fp32", _pe_procesor("fp32"))
    b = _banc_cu_placa(fisiere[1], 2.5, 1.5 if placa_aleasa else 3.0)
    cale = tmp_path / "r.json"
    cale.write_text(json.dumps(reglaj.din_banc(b, "test")), encoding="utf-8")
    m = InferentaCCM(str(fisiere[1]), str(cale), placa=cu_placa)
    st = m.statistici()["ccm"]
    assert st["folosit"] and st["dispozitiv"] == dispozitiv
    assert st["varianta"] == ("placa_fp32" if dispozitiv == "placa" else "referinta")
    assert isinstance(m.motor, placa.MotorPlaca) == (dispozitiv == "placa")
    if motiv:
        assert any(motiv in x for x in st["motive_placa"]), st["motive_placa"]
    ref = InferentaKGR1(str(fisiere[1]))
    assert m.genereaza(SIMBOLURI, 12) == ref.genereaza(SIMBOLURI, 12)
    assert np.allclose(m.logits(SIMBOLURI), ref.logits(SIMBOLURI), atol=1e-4)


def test_reglaj_vechi_fara_placa_ramane_pe_procesor(fisiere, tmp_path):
    from teste.test_inferenta_ccm import _scrie_reglaj

    m = InferentaCCM(str(fisiere[1]), str(_scrie_reglaj(tmp_path / "r.json", fisiere[1], fire="toate")), placa=True)
    st = m.statistici()["ccm"]
    assert st["folosit"] and st["dispozitiv"] == "procesor" and "nu are variantă pe placă" in st["motive_placa"][0]


def test_varianta_de_placa_care_crapa_duce_la_rezerva(fisiere, tmp_path, monkeypatch):
    def crapa(cale):
        raise RuntimeError("out of memory")

    monkeypatch.setattr(placa, "placa_disponibila", lambda: True)
    monkeypatch.setitem(variante.TOATE, "placa_fp32", crapa)
    cale = tmp_path / "r.json"
    cale.write_text(json.dumps(reglaj.din_banc(_banc_cu_placa(fisiere[1]), "test")), encoding="utf-8")
    st = InferentaCCM(str(fisiere[1]), str(cale), placa=True).statistici()["ccm"]
    assert not st["folosit"] and st["dispozitiv"] == "procesor" and "nu s-a încărcat" in st["motive"][0]
