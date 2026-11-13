"""S110 revizuită (C-120, 13 nov 2026): config/conv_w2_mare_24z2.toml și cele două configurări de probă.

- 24z2 diferă de 24n doar prin ce cere sarcina; probele diferă de 24z2 doar prin nume, stare, buget și rate;
- `ModelGPTCod` fără `abatere_incorporari` = `ModelGPTConversatieMuon` bit cu bit (greutăți de pornire și antrenare pe
  calea cu text + conversație + hrană); cu ea diferă doar încorporările (și capul legat de ele);
- rata după o reluare din gpt.pt = rata socotită pe timpul total (52 h), fără încălzire nouă.
"""

from __future__ import annotations

import json
import math
import tomllib
from pathlib import Path

import pytest

torch = pytest.importorskip("torch")

from module.model_gpt_cod import ModelGPTCod  # noqa: E402
from module.model_muon import ModelGPTConversatieMuon  # noqa: E402

RADACINA = Path(__file__).resolve().parent.parent


def _config(nume: str) -> dict:
    return tomllib.loads((RADACINA / "config" / nume).read_text(encoding="utf-8"))


def _reteta() -> dict:
    return _config("conv_w2_mare_24z2.toml")["porturi"]["model"]["setari"]


def test_24z2_difera_de_24n_doar_prin_ce_cere_sarcina():
    n, z = _config("conv_w2_mare_24n.toml"), _config("conv_w2_mare_24z2.toml")
    sn, sz = n["porturi"]["model"]["setari"], z["porturi"]["model"]["setari"]
    diferite = {k for k in sn.keys() | sz.keys() if sn.get(k) != sz.get(k)}
    assert diferite == {"lot", "rata_invatare", "incalzire_pasi", "cale_stare", "samanta", "examene_suplimentare", "hrana",
                        "fractie_hrana", "conversatie", "fractie_conversatie", "durata_scaderii_secunde",
                        "adunare_loturi", "rata_muon", "abatere_incorporari"}
    assert z["porturi"]["model"]["modul"] == "module.model_gpt_cod:ModelGPTCod"
    assert sz["abatere_incorporari"] == 0.02 and sz["samanta"] == 24
    assert z["platforma"]["nume"] == "w2_mare_24z2" and sz["cale_stare"] == "lucru/w2_mare_24z2/gpt.pt"
    assert sz["lot"] == 6 and sz["adunare_loturi"] == 16 and sz["incalzire_pasi"] == 6400
    assert sz["durata_scaderii_secunde"] == 52 * 3600 and sz["racire_finala"] == 0.25 and sz["fractie_rata_finala"] == 1.0
    assert sz["optimizator"] == "muon" and sz["examene_suplimentare"] == []
    assert sz["conversatie"] == "lucru/romana_raspunsuri_r2/antrenare.jsonl" and sz["fractie_conversatie"] == 0.05
    assert (sz["hrana"], sz.get("fractie_hrana")) in {("date/ws/hrana_fineweb_rest/antrenare.txt", 0.55), ("", None)}
    assert z["porturi"]["date"] == _config("conv_w2_mare_24_bucati.toml")["porturi"]["date"]
    assert z["porturi"]["examen"] == n["porturi"]["examen"]
    assert z["porturi"]["examen"]["modul"] == "module.examen_romana:ExamenRomana"
    assert z["porturi"]["cercetator"]["setari"]["spatiu"] == {"model": {"lot": [6]}}
    for cheie in ("paznic", "criterii"):
        assert z[cheie] == n[cheie]
    for port in n["porturi"].keys() - {"model", "date", "cercetator"}:
        assert z["porturi"][port] == n["porturi"][port]
    assert {k: v for k, v in z["platforma"].items() if k != "nume"} == {k: v for k, v in n["platforma"].items() if k != "nume"}


@pytest.mark.parametrize("litera, rata_muon, rata_invatare", [("a", 0.02, 0.0006), ("b", 0.01, 0.0003)])
def test_probele_difera_de_24z2_doar_prin_nume_stare_buget_si_rate(litera, rata_muon, rata_invatare):
    z, p = _config("conv_w2_mare_24z2.toml"), _config(f"proba_24z2_{litera}.toml")
    sz, sp = z["porturi"]["model"]["setari"], p["porturi"]["model"]["setari"]
    assert {k for k in sz.keys() | sp.keys() if sz.get(k) != sp.get(k)} <= {"cale_stare", "rata_muon", "rata_invatare"}
    # proba refăcută cu hrana FineWeb-2 (supraveghetor, 13 nov 2026 20:20): linie și dosar noi, cu sufixul 2
    assert sp["cale_stare"] == f"lucru/proba_24z2/{litera}2/gpt.pt"
    assert sp["hrana"] == "date/ws/hrana_fineweb_rest/antrenare.txt" and sp["fractie_hrana"] == 0.55
    assert sp["rata_muon"] == rata_muon and sp["rata_invatare"] == rata_invatare
    assert p["platforma"] == {**z["platforma"], "nume": f"proba_24z2_{litera}2", "buget_antrenare_secunde": 1800}
    assert p["porturi"]["model"]["modul"] == z["porturi"]["model"]["modul"]
    for port in z["porturi"].keys() - {"model"}:
        assert p["porturi"][port] == z["porturi"][port]
    assert p["paznic"] == z["paznic"]


def test_rata_mare_e_una_dintre_cele_doua_probe():
    s = _reteta()
    assert (s["rata_muon"], s["rata_invatare"]) in {(0.02, 0.0006), (0.01, 0.0003)}


@pytest.fixture
def mic(tmp_path):
    from module.tokenizer_bpe import antreneaza_bpe

    text = ("Once upon a time there was a dog. " * 200) + "<|endoftext|>"
    hrana = ("A fost odată un câine care lătra la lună. " * 200) + "<|endoftext|>"
    (tmp_path / "hrana.txt").write_text(hrana, encoding="utf-8")
    (tmp_path / "conv.jsonl").write_text("\n".join(json.dumps({"intrebare": f"Ce face cățelul {i}?", "raspuns": "Latră."})
                                                   for i in range(20)), encoding="utf-8")
    antreneaza_bpe(text + hrana + " Întrebare: Răspuns: Ce face cățelul? Latră.", 300).salveaza(tmp_path / "bpe.json")

    class Date:
        def text_antrenare(self):
            return text

    r = _reteta()
    setari = dict(n_straturi=2, n_capete=2, n_emb=32, context=32, lot=r["lot"], dispozitiv="cpu", tokenizer="bpe",
                  cale_tokenizer=str(tmp_path / "bpe.json"), conversatie=str(tmp_path / "conv.jsonl"),
                  fractie_conversatie=r["fractie_conversatie"], hrana=str(tmp_path / "hrana.txt"), fractie_hrana=0.55,
                  samanta=r["samanta"], pasi_max=12, rata_invatare=r["rata_invatare"], rata_care_scade=True,
                  incalzire_pasi=20, fractie_rata_finala=r["fractie_rata_finala"],
                  durata_scaderii_secunde=r["durata_scaderii_secunde"], optimizator="muon", rata_muon=r["rata_muon"],
                  adunare_loturi=2, racire_finala=r["racire_finala"])
    return setari, Date()


def _pornire(clasa, setari: dict, **in_plus) -> dict:
    from module.tokenizer_bpe import TokenizerBPE

    model = clasa(**setari, **in_plus)
    model.tok = TokenizerBPE.incarca(setari["cale_tokenizer"])
    model._construieste()
    return {k: v.detach().clone() for k, v in model.retea.state_dict().items()}


def test_model_gpt_cod_schimba_doar_incorporarile(mic):
    setari, _ = mic
    muon = _pornire(ModelGPTConversatieMuon, setari)
    cod = _pornire(ModelGPTCod, setari)
    assert muon.keys() == cod.keys() and all(torch.equal(muon[k], cod[k]) for k in muon)  # bit cu bit
    cu = _pornire(ModelGPTCod, setari, abatere_incorporari=0.02)
    diferite = {k for k in muon if not torch.equal(muon[k], cu[k])}
    assert diferite == {"emb_token.weight", "emb_pozitie.weight", "cap.weight"}
    assert torch.equal(cu["emb_token.weight"], cu["cap.weight"])  # capul rămâne legat
    assert 0.015 < float(cu["emb_token.weight"].std()) < 0.025 and float(muon["emb_token.weight"].std()) > 0.5


def test_fara_abatere_antrenarea_e_cea_a_modelului_muon(mic):
    """Calea folosită la S110 (date fără `simboluri_antrenare`, cu conversație și hrană): ModelGPTCod fără
    `abatere_incorporari` face exact aceiași pași ca ModelGPTConversatieMuon."""
    setari, date = mic
    a = ModelGPTConversatieMuon(**setari)
    sa = a.antreneaza(date, 600.0)
    b = ModelGPTCod(**setari)
    sb = b.antreneaza(date, 600.0)
    assert "simboluri_direct" not in sb and sa["ferestre"] == sb["ferestre"]
    assert sa["pierdere_finala"] == sb["pierdere_finala"]  # după 12 pași, aceeași pierdere bit cu bit
    f = sb["ferestre"]  # 12 loturi × 6: hrana 0,55, conversația 0,05, restul text
    assert f["hrana"] + f["conversatie"] + f["text"] == 72
    assert f["hrana"] == math.floor(0.55 * 72 + 1e-9) and f["conversatie"] == math.floor(0.05 * 72 + 1e-9)


def test_cu_abatere_primul_lot_e_aproape_de_hazard(mic):
    from module.tokenizer_bpe import TokenizerBPE

    setari, date = mic
    hazard = math.log(TokenizerBPE.incarca(setari["cale_tokenizer"]).marime)
    cu = ModelGPTCod(**{**setari, "pasi_max": 1}, abatere_incorporari=0.02).antreneaza(date, 600.0)["pierdere_finala"]
    fara = ModelGPTCod(**{**setari, "pasi_max": 1}).antreneaza(date, 600.0)["pierdere_finala"]
    assert cu < hazard + 1.0 < fara  # C1: pornirea implicită (N(0,1) legată de ieșire) dă o pierdere uriașă


def test_rata_continua_dupa_reluare_fara_incalzire_noua(mic, tmp_path):
    setari, date = mic
    cale = tmp_path / "gpt.pt"
    primul = ModelGPTCod(**setari, cale_stare=str(cale), abatere_incorporari=0.02)
    s1 = primul.antreneaza(date, 600.0)
    assert not s1["continuat"] and s1["pasi"] == 12
    primul._salveaza_starea({"scor": 1.0})
    greutati = {k: v.detach().clone() for k, v in primul.retea.state_dict().items()}

    def cu_inregistrare(model):
        rate = []
        original = model.rata_acum

        def rata_acum(pasi, progres):
            rata = original(pasi, progres)
            rate.append((pasi, progres, rata))
            return rata

        model.rata_acum = rata_acum
        return rate

    reluat = ModelGPTCod(**{**setari, "pasi_max": 1}, cale_stare=str(cale), abatere_incorporari=0.02)
    reluat.tok = primul.tok
    reluat._pregateste_reteaua()  # la reluare, starea salvată înlocuiește încorporările pornite din nou
    assert all(torch.equal(v, greutati[k]) for k, v in reluat.retea.state_dict().items())

    reluat = ModelGPTCod(**setari, cale_stare=str(cale), abatere_incorporari=0.02)
    rate = cu_inregistrare(reluat)
    s2 = reluat.antreneaza(date, 600.0)
    assert s2["continuat"] and s2["pasi_total"] == 24
    assert reluat.minute_total > primul.minute_total
    pasi, progres, rata = rate[0]
    # încălzirea continuă de la pasul 12 din 20, nu de la 0; progresul pornește din minutele salvate
    assert pasi == 0 and rata == pytest.approx(setari["rata_invatare"] * 13 / 20)
    assert progres == pytest.approx(primul.minute_total * 60 / setari["durata_scaderii_secunde"], abs=1e-6)
    nou = ModelGPTCod(**setari, cale_stare=str(tmp_path / "altul.pt"), abatere_incorporari=0.02)
    rate_nou = cu_inregistrare(nou)
    nou.antreneaza(date, 600.0)
    assert rate_nou[0][2] == pytest.approx(setari["rata_invatare"] / 20)


@pytest.mark.parametrize("ore, factor", [(1, 1.0), (12, 1.0), (24, 1.0), (39, 1.0), (45.5, 0.5), (52, 0.0)])
def test_rata_dupa_reluare_la_ora_data(ore, factor):
    """Stare salvată după `ore` ore (încălzirea gata): rata = vârful × forma pe timpul total de 52 h (vârf până la ora 39,
    apoi răcirea din ultimele 25 %)."""
    r = _reteta()
    setari = dict(n_straturi=1, n_capete=1, n_emb=8, context=8, lot=2, dispozitiv="cpu",
                  rata_invatare=r["rata_invatare"], rata_care_scade=True, incalzire_pasi=r["incalzire_pasi"],
                  fractie_rata_finala=r["fractie_rata_finala"], durata_scaderii_secunde=r["durata_scaderii_secunde"],
                  racire_finala=r["racire_finala"], optimizator="muon", rata_muon=r["rata_muon"],
                  adunare_loturi=r["adunare_loturi"], abatere_incorporari=r["abatere_incorporari"])
    model = ModelGPTCod(**setari)
    model.pasi_total, model.minute_total = 500_000, ore * 60  # ce pune _pregateste_reteaua din stare
    progres = model._progres(0, 0.0, 0.0, 3600.0)
    assert progres == pytest.approx(ore / 52)
    assert model.rata_acum(0, progres) == pytest.approx(r["rata_invatare"] * factor, abs=1e-12)
