"""S48: modulul `inferenta_ccm` și reglajul CCM (module/calcul/reglaj.py, fire.py): reglajul bun e folosit și dă aceleași
simboluri ca `inferenta_kgr1`; la orice nepotrivire, rezerva = exact calea `inferenta_kgr1`."""

import json

import numpy as np
import pytest

from module.calcul import fire, reglaj
from module.inferenta_ccm import InferentaCCM
from module.inferenta_kgr1 import InferentaKGR1
from teste.test_ccm_banc import _scrie_sintetic

SIMBOLURI = [1, 5, 9, 60, 2]


@pytest.fixture(scope="module")
def kgr(tmp_path_factory):
    return _scrie_sintetic(tmp_path_factory.mktemp("ccm_reglaj") / "q8.kgr", "q8_0")


def _banc(kgr, varianta="referinta", fire_="1", acceptata=True):
    """Ca ieșirea `banc toate` (S47), cu o singură variantă."""
    m = {k: {"median": 1.0} for k in ("total", "simboluri_pe_secunda")}
    return {"kgr": str(kgr), "toleranta_logits": 1e-3,
            "cea_mai_rapida_pe_total": {"varianta": varianta, "fire": fire_} if acceptata else None,
            "rezultate": [{"varianta": varianta, "fire": fire_, "acceptata": acceptata, "masurare": m,
                           "verificare_model": {"dif_logits_max": 0.0}, "fata_de_referinta_total": 1.2}]}


def _scrie_reglaj(cale, kgr, **schimbari):
    r = reglaj.din_banc(_banc(kgr, schimbari.pop("varianta", "referinta"), schimbari.pop("fire", "1")), "test")
    for cheie, valoare in schimbari.items():
        if cheie == "inmultire":
            r["operatii"]["inmultire"].update(valoare)
        else:
            r[cheie] = valoare
    cale.write_text(json.dumps(r, ensure_ascii=False), encoding="utf-8")
    return cale


def test_reglajul_din_banc(kgr):
    r = reglaj.din_banc(_banc(kgr, "transpus", "4"), "lucru/ccm/s47.json")
    assert r["format"] == reglaj.FORMAT and r["versiune"] == reglaj.VERSIUNE
    assert r["calculator"] == reglaj.nume_calculator() and r["model"]["sha256"] == reglaj.sha256(kgr)
    assert r["operatii"]["inmultire"]["varianta"] == "transpus" and r["operatii"]["inmultire"]["fire"] == "4"
    assert reglaj.motive_nepotrivire(r, kgr) == [] or not fire.disponibil()
    with pytest.raises(ValueError, match="nicio variantă"):
        reglaj.din_banc(_banc(kgr, acceptata=False), "test")


@pytest.mark.parametrize("varianta,fire_", [("referinta", "1"), ("transpus", "4"), ("la_pas", "toate")])
def test_reglajul_bun_e_folosit_si_da_ce_da_referinta(kgr, tmp_path, varianta, fire_):
    if fire_ != "toate" and not fire.disponibil():
        pytest.skip("firele OpenBLAS nu se pot schimba aici")
    m = InferentaCCM(str(kgr), str(_scrie_reglaj(tmp_path / "r.json", kgr, varianta=varianta, fire=fire_)))
    ref = InferentaKGR1(str(kgr))
    st = m.statistici()["ccm"]
    assert st["folosit"] and st["varianta"] == varianta and st["fire"] == fire_ and st["motive"] == []
    assert m.genereaza(SIMBOLURI, 12) == ref.genereaza(SIMBOLURI, 12)
    assert np.allclose(m.logits(SIMBOLURI), ref.logits(SIMBOLURI), atol=1e-4)


NEPOTRIVIRI = [
    ("alt_calculator", {"calculator": "alt-calculator"}, "alt calculator"),
    ("alte_nuclee", {"nuclee": 10_000}, "alte nuclee"),
    ("alt_model", {"model": {"nume": "altul.kgr", "sha256": "0" * 64}}, "alt model"),
    ("alt_format", {"versiune": 99}, "alt format"),
    ("varianta_necunoscuta", {"inmultire": {"varianta": "nu_exista"}}, "variantă necunoscută"),
    ("neacceptata", {"inmultire": {"acceptata": False}}, "nu e acceptată"),
    ("fire_stricate", {"inmultire": {"fire": "multe"}}, "fire necunoscute"),
    ("operatie_necunoscuta", {"operatii": {"softmax": {}}}, "operații necunoscute"),
]


@pytest.mark.parametrize("schimbari,motiv", [(s, m) for _, s, m in NEPOTRIVIRI], ids=[n for n, _, _ in NEPOTRIVIRI])
def test_orice_nepotrivire_duce_la_rezerva(kgr, tmp_path, schimbari, motiv):
    m = InferentaCCM(str(kgr), str(_scrie_reglaj(tmp_path / "r.json", kgr, **schimbari)))
    st = m.statistici()["ccm"]
    assert not st["folosit"] and any(motiv in x for x in st["motive"]), st["motive"]
    assert m.motor.desfacere == "la_incarcare" and m._fire is None
    assert m.genereaza(SIMBOLURI, 8) == InferentaKGR1(str(kgr)).genereaza(SIMBOLURI, 8)


def test_fara_reglaj_sau_reglaj_stricat_duce_la_rezerva(kgr, tmp_path):
    assert InferentaCCM(str(kgr), str(tmp_path / "nu_exista.json")).statistici()["ccm"]["motive"] == [
        "fără reglaj: nu_exista.json"]
    (tmp_path / "stricat.json").write_text("{nu e json", encoding="utf-8")
    st = InferentaCCM(str(kgr), str(tmp_path / "stricat.json")).statistici()["ccm"]
    assert not st["folosit"] and "nu se poate citi" in st["motive"][0]


def test_varianta_care_crapa_la_incarcare_duce_la_rezerva(kgr, tmp_path, monkeypatch):
    from module.calcul import variante

    def crapa(cale):
        raise MemoryError("prea mare")

    monkeypatch.setitem(variante.VARIANTE, "referinta", crapa)
    monkeypatch.setitem(variante.TOATE, "referinta", crapa)
    st = InferentaCCM(str(kgr), str(_scrie_reglaj(tmp_path / "r.json", kgr))).statistici()["ccm"]
    assert not st["folosit"] and "nu s-a încărcat" in st["motive"][0]


def test_firele_se_pun_inapoi_dupa_calcul():
    if not fire.disponibil():
        pytest.skip("firele OpenBLAS nu se pot schimba aici")
    inainte = fire.citeste()
    with fire.cu_fire(1):
        assert fire.citeste() == 1
    assert fire.citeste() == inainte
    with pytest.raises(ZeroDivisionError), fire.cu_fire(1):
        1 / 0
    assert fire.citeste() == inainte
    with fire.cu_fire(None):
        assert fire.citeste() == inainte
    assert fire.din_text("toate") is None and fire.din_text("4") == 4
    for rau in ("0", "-1", "multe"):
        with pytest.raises(ValueError):
            fire.din_text(rau)


def test_linia_de_comanda_scrie_si_verifica(kgr, tmp_path):
    (tmp_path / "banc.json").write_text(json.dumps(_banc(kgr, "referinta", "toate")), encoding="utf-8")
    iesire = tmp_path / "reglaj.json"
    assert reglaj.main(["scrie", "--banc", str(tmp_path / "banc.json"), "--iesire", str(iesire)]) == 0
    with pytest.raises(SystemExit, match="există deja"):
        reglaj.main(["scrie", "--banc", str(tmp_path / "banc.json"), "--iesire", str(iesire)])
    assert reglaj.main(["verifica", "--kgr", str(kgr), "--reglaj", str(iesire)]) == 0
    assert reglaj.main(["verifica", "--kgr", str(kgr), "--reglaj", str(tmp_path / "lipsa.json")]) == 1
