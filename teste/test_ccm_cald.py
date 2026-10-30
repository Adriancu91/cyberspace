"""S50: bancul CCM măsoară „rece” (primul răspuns dintr-un motor nou) și „cald” (răspunsurile 2–6 din același motor);
alegerea pe procesor și procesor/placă se face după „cald”; un reglaj vechi (fără câmpurile noi) rămâne bun.
Modele mici sintetice, fără rețea, fără placă."""

import json
import statistics

import pytest

from module.calcul import banc, fire, reglaj
from module.calcul.variante import VARIANTE
from teste.test_ccm_banc import TEXTE, _scrie_sintetic
from teste.test_ccm_placa import _rezultat
from unelte.inferenta_bruta import MotorBrut


@pytest.fixture(scope="module")
def kgr(tmp_path_factory):
    return _scrie_sintetic(tmp_path_factory.mktemp("ccm_cald") / "q8.kgr", "q8_0")


class _StricatDupaPrimul(MotorBrut):
    """Bun la primul răspuns, apoi greșit (o stare care se strică în motorul ținut deschis)."""

    def __init__(self, cale):
        super().__init__(cale, "la_incarcare")
        self.raspunsuri = 0

    def completeaza_simboluri(self, simboluri, max_simboluri):
        self.raspunsuri += 1
        if self.raspunsuri == 2:
            self.t["ln.bias"] = self.t["ln.bias"] + 50.0 * (self.t["emb_token.weight"][7] - self.t["emb_token.weight"][3])
        return super().completeaza_simboluri(simboluri, max_simboluri)


def test_cald_se_masoara_in_acelasi_motor(kgr):
    motoare = []

    def fabrica(cale):
        motoare.append(VARIANTE["transpus"](cale))
        return motoare[-1]

    m = banc.masoara_cald(fabrica, kgr, TEXTE[1], simboluri=8, raspunsuri=6)
    assert len(motoare) == 1  # un singur motor, toate cele 6 răspunsuri din el
    assert m["raspunsuri"] == 6 and len(m["pe_raspuns"]) == 6 and m["pornire_secunde"] > 0
    assert m["rece"] == m["pe_raspuns"][0]
    cald = [r["total"] for r in m["pe_raspuns"][1:]]
    assert m["cald"]["total"]["median"] == pytest.approx(statistics.median(cald))
    assert m["cald"]["total"]["min"] == min(cald) and m["cald"]["total"]["max"] == max(cald)
    for r in m["pe_raspuns"]:
        assert r["total"] == pytest.approx(r["inceput"] + r["restul"])  # fără încărcare
    v = m["verificare"]
    assert v["acceptata"], v["motive"]
    assert v["simboluri_identice"] == [True] * 6 and len(v["dif_logits_max"]) == 6
    with pytest.raises(ValueError):
        banc.masoara_cald(fabrica, kgr, TEXTE[0], raspunsuri=1)


def test_simbolurile_se_verifica_la_fiecare_raspuns(kgr):
    m = banc.masoara_cald(_StricatDupaPrimul, kgr, TEXTE[1], simboluri=8, raspunsuri=4)
    v = m["verificare"]
    assert v["simboluri_identice"][0] and not v["acceptata"]
    assert any(x.startswith("răspunsul 2") for x in v["motive"])


def test_procesul_nou_scrie_rece_si_cald(kgr):
    r = banc.in_proces_nou("referinta", "1", kgr, simboluri=4, repetari=1, vectori=False, raspunsuri=3)
    c = r["masurare_cald"]
    assert r["acceptata"] and c["raspunsuri"] == 3 and len(c["pe_raspuns"]) == 3 and c["verificare"]["acceptata"]


def test_alegerea_pe_procesor_si_placa_foloseste_cald(monkeypatch):
    # „toate” e cea mai rapidă rece (cu încărcarea), dar cea mai lentă caldă: se alege 1 fir
    rez = {("referinta", "1"): _rezultat("referinta", "1", 2.5, cald=1.8),
           ("referinta", "toate"): _rezultat("referinta", "toate", 2.0, cald=3.0),
           ("placa_fp32", "toate"): _rezultat("placa_fp32", "toate", 1.7, cald=2.2)}
    monkeypatch.setattr(banc, "in_proces_nou", lambda v, f, *a, **k: dict(rez[(v, f)]))
    b = banc.toate("x.kgr", combinatii=list(rez))
    assert b["alegere_dupa"] == "cald"
    assert b["cea_mai_rapida_pe_procesor"] == {"varianta": "referinta", "fire": "1"}
    assert b["cea_mai_rapida_pe_total"] == {"varianta": "placa_fp32", "fire": "toate"}  # doar informație
    assert b["rezultate"][0]["fata_de_referinta_cald"] == pytest.approx(3.0 / 1.8)


def _banc_cald(kgr, procesor_cald, placa_cald):
    rez = [_rezultat("referinta", "1", 2.5, cald=procesor_cald), _rezultat("placa_fp32", "toate", 1.5, cald=placa_cald)]
    return {"kgr": str(kgr), "toleranta_logits": 1e-3, "rezultate": rez, "alegere_dupa": "cald",
            "cea_mai_rapida_pe_procesor": {"varianta": "referinta", "fire": "1"},
            "cea_mai_rapida_pe_placa": {"varianta": "placa_fp32", "fire": "toate"}}


def test_reglajul_alege_procesor_sau_placa_dupa_cald(kgr):
    # pe total (rece, cu încărcarea) placa e mai rapidă (1,5 < 2,5), dar caldă e mai lentă: procesorul
    r = reglaj.din_banc(_banc_cald(kgr, 1.8, 2.2), "test")
    assert r["alegere_dupa"] == "cald" and r["alegere"] == "procesor"
    inm = r["operatii"]["inmultire"]
    assert inm["cald"]["total_secunde"] == 1.8 and inm["cald"]["rece_total_secunde"] == 2.5
    assert inm["cald"]["pornire_secunde"] == 0.1 and inm["fire"] == "1"
    assert r["placa"]["fata_de_procesor_cald"] == pytest.approx(1.8 / 2.2)
    assert reglaj.din_banc(_banc_cald(kgr, 1.8, 1.2), "test")["alegere"] == "placa"
    fara = _banc_cald(kgr, 1.8, 1.2)
    del fara["rezultate"][0]["masurare_cald"]
    with pytest.raises(ValueError, match="cald"):
        reglaj.din_banc(fara, "test")


def test_reglajul_vechi_ramane_bun(kgr, tmp_path):
    b = {"kgr": str(kgr), "toleranta_logits": 1e-3, "cea_mai_rapida_pe_total": {"varianta": "referinta", "fire": "toate"},
         "rezultate": [{"varianta": "referinta", "fire": "toate", "acceptata": True,
                        "masurare": {"total": {"median": 1.0}, "simboluri_pe_secunda": {"median": 40.0}},
                        "verificare_model": {"dif_logits_max": 0.0}}]}
    vechi = reglaj.din_banc(b, "lucru/ccm/s49.json")  # banc fără „alegere_dupa”: ca în S48/S49
    assert "alegere_dupa" not in vechi and "cald" not in vechi["operatii"]["inmultire"]
    cale = tmp_path / "reglaj.json"
    cale.write_text(json.dumps(vechi), encoding="utf-8")
    a = reglaj.alege(cale, kgr)
    assert a["folosit"] and a["motive"] == [] and a["varianta"] == "referinta" and a["fire"] == "toate"
    nou = reglaj.din_banc(_banc_cald(kgr, 1.8, 2.2), "test")
    cale.write_text(json.dumps(nou), encoding="utf-8")
    a = reglaj.alege(cale, kgr)
    if fire.disponibil():  # „1 fir” cere firele OpenBLAS schimbabile
        assert a["folosit"] and a["motive"] == [] and a["fire"] == "1"
