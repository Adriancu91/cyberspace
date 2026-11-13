"""S110 (C-119 E2): programul ratei continuă corect după o reluare din gpt.pt (nu repornește încălzirea, iar scăderea
se socotește pe timpul total de antrenare din stare), cu rețeta din config/conv_w2_mare_24z.toml."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

import pytest

torch = pytest.importorskip("torch")

from module.model_muon import ModelGPTConversatieMuon  # noqa: E402

RADACINA = Path(__file__).resolve().parent.parent


def _reteta_24z() -> dict:
    brut = tomllib.loads((RADACINA / "config" / "conv_w2_mare_24z.toml").read_text(encoding="utf-8"))
    return brut["porturi"]["model"]["setari"]


@pytest.fixture
def mic(tmp_path):
    from module.tokenizer_bpe import antreneaza_bpe

    text = ("Once upon a time there was a dog. " * 200) + "<|endoftext|>"
    (tmp_path / "conv.jsonl").write_text("\n".join(json.dumps({"intrebare": f"Ce face cățelul {i}?", "raspuns": "Latră."})
                                                   for i in range(20)), encoding="utf-8")
    antreneaza_bpe(text + " Întrebare: Răspuns: Ce face cățelul? Latră.", 300).salveaza(tmp_path / "bpe.json")

    class Date:
        def text_antrenare(self):
            return text

    r = _reteta_24z()
    setari = dict(n_straturi=2, n_capete=2, n_emb=32, context=32, lot=6, dispozitiv="cpu", tokenizer="bpe",
                  cale_tokenizer=str(tmp_path / "bpe.json"), conversatie=str(tmp_path / "conv.jsonl"),
                  fractie_conversatie=r["fractie_conversatie"], samanta=r["samanta"], pasi_max=12,
                  rata_invatare=r["rata_invatare"], rata_care_scade=True, incalzire_pasi=20,
                  fractie_rata_finala=r["fractie_rata_finala"], durata_scaderii_secunde=r["durata_scaderii_secunde"],
                  optimizator="muon", rata_muon=r["rata_muon"], adunare_loturi=2, racire_finala=r["racire_finala"])
    return setari, Date()


def test_reteta_24z_e_cea_ceruta():
    r = _reteta_24z()
    assert r["durata_scaderii_secunde"] == 54 * 3600 and r["racire_finala"] == 0.25 and r["incalzire_pasi"] == 1000
    assert r["fractie_rata_finala"] == 1.0 and r["optimizator"] == "muon" and r["samanta"] == 24
    assert r["cale_stare"] == "lucru/w2_mare_24z/gpt.pt"


def test_rata_continua_dupa_reluare_fara_incalzire_noua(mic, tmp_path):
    setari, date = mic
    cale = tmp_path / "gpt.pt"
    primul = ModelGPTConversatieMuon(**setari, cale_stare=str(cale))
    s1 = primul.antreneaza(date, 600.0)
    assert not s1["continuat"] and s1["pasi"] == 12
    primul._salveaza_starea({"scor": 1.0})

    def cu_inregistrare(model):
        rate = []
        original = model.rata_acum

        def rata_acum(pasi, progres):
            rata = original(pasi, progres)
            rate.append((pasi, progres, rata))
            return rata

        model.rata_acum = rata_acum
        return rate

    reluat = ModelGPTConversatieMuon(**setari, cale_stare=str(cale))
    rate = cu_inregistrare(reluat)
    s2 = reluat.antreneaza(date, 600.0)
    assert s2["continuat"] and s2["pasi_total"] == 24
    assert reluat.minute_total > primul.minute_total
    pasi, progres, rata = rate[0]
    # încălzirea continuă de la pasul 12 din 20, nu de la 0; progresul pornește din minutele salvate
    assert pasi == 0 and rata == pytest.approx(setari["rata_invatare"] * 13 / 20)
    assert progres == pytest.approx(primul.minute_total * 60 / setari["durata_scaderii_secunde"], abs=1e-6)
    # un model nou (fără stare) ar fi luat-o de la capăt: 1/20 din rată
    nou = ModelGPTConversatieMuon(**setari, cale_stare=str(tmp_path / "altul.pt"))
    rate_nou = cu_inregistrare(nou)
    nou.antreneaza(date, 600.0)
    assert rate_nou[0][2] == pytest.approx(setari["rata_invatare"] / 20)


@pytest.mark.parametrize("ore, factor", [(1, 1.0), (12, 1.0), (24, 1.0), (40.5, 1.0), (47.25, 0.5), (54, 0.0)])
def test_rata_dupa_reluare_la_ora_data(tmp_path, ore, factor):
    """Stare salvată după `ore` ore de antrenare (cu încălzirea gata): rata = vârful × forma pe timpul total."""
    r = _reteta_24z()
    setari = dict(n_straturi=1, n_capete=1, n_emb=8, context=8, lot=2, dispozitiv="cpu",
                  rata_invatare=r["rata_invatare"], rata_care_scade=True, incalzire_pasi=r["incalzire_pasi"],
                  fractie_rata_finala=r["fractie_rata_finala"], durata_scaderii_secunde=r["durata_scaderii_secunde"],
                  racire_finala=r["racire_finala"], optimizator="muon", rata_muon=r["rata_muon"],
                  adunare_loturi=r["adunare_loturi"])
    model = ModelGPTConversatieMuon(**setari)
    model.pasi_total, model.minute_total = 50_000, ore * 60  # ce pune _pregateste_reteaua din stare
    progres = model._progres(0, 0.0, 0.0, 3600.0)
    assert progres == pytest.approx(ore / 54)
    assert model.rata_acum(0, progres) == pytest.approx(r["rata_invatare"] * factor, abs=1e-12)
