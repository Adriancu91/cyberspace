"""S142: unelte/viteza_scris_kv.py — memoria de context (KV cache) scrisă în unealtă, pe procesor, F32.

(i) cu memorie = fără memorie: aceleași logit-uri la fiecare poziție (diferența maximă ≤ 1e-4), pe 16 simboluri;
(ii) pe #513 (doar dacă modelul e pe disc): cele 16 simboluri = cele din OS și S130.
"""

from pathlib import Path

import pytest

torch = pytest.importorskip("torch")

from module.model_gpt import _GPT  # noqa: E402
from unelte.viteza_inferenta import greedy  # noqa: E402
from unelte.viteza_scris_kv import (  # noqa: E402
    ASTEPTAT_513,
    compara_logit_uri,
    greedy_cu_memorie,
    masoara,
    pas_inainte,
    pregateste,
)

RADACINA = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def retea():
    torch.manual_seed(7)
    r = _GPT(vocab=60, n_straturi=3, n_capete=4, n_emb=32, context=32, dropout=0.0).eval()
    with torch.no_grad():  # LayerNorm-uri nebanale, ca diferențele să se vadă dacă ar exista
        for p in r.parameters():
            p.add_(0.05 * torch.randn_like(p))
    return r


def test_cu_memorie_aceleasi_logit_uri_ca_fara(retea):
    r = compara_logit_uri(retea, [3, 7, 1, 12], 16, "cpu")
    assert len(r["dif_max_pe_pozitie"]) == 16
    assert r["dif_max"] <= 1e-4
    assert r["identice"] and len(r["simboluri_cu"]) == 16


def test_cu_memorie_e_acelasi_greedy_ca_s130(retea):
    assert greedy_cu_memorie(retea, [5, 2], 12, "cpu") == greedy(retea, [5, 2], 12, "cpu", 32)


def test_pas_inainte_in_bucati_da_acelasi_rezultat_ca_dintr_o_data(retea):
    idx = torch.tensor([[4, 9, 1, 30, 2, 8, 11]])
    tot, _ = pas_inainte(retea, idx, None)
    l1, mem = pas_inainte(retea, idx[:, :3], None)
    l2, mem = pas_inainte(retea, idx[:, 3:6], mem)  # bucată de mai multe simboluri peste memorie
    l3, mem = pas_inainte(retea, idx[:, 6:], mem)
    bucati = torch.cat([l1, l2, l3], dim=1)
    assert float((bucati - tot).abs().max()) <= 1e-5
    with torch.no_grad():
        assert float((tot - retea(idx)).abs().max()) <= 1e-5
    assert mem[0][0].shape[2] == 7


def test_peste_context_refuza(retea):
    with pytest.raises(ValueError, match="contextul"):
        pas_inainte(retea, torch.zeros(1, 33, dtype=torch.long), None)


def test_masoara_si_preciziile(retea):
    r = masoara(retea, [3, 7, 1], 4, "cpu", cache=True, repetari=3)
    assert r["simboluri"] == greedy(retea, [3, 7, 1], 4, "cpu", 32)
    assert len(r["secunde_rulari"]) == 3 and r["simb_pe_s"] > 0
    copie = pregateste(retea, "cpu", "bf16")
    assert copie.emb_token.weight.dtype == torch.bfloat16
    assert retea.emb_token.weight.dtype == torch.float32  # originalul neatins
    assert len(greedy_cu_memorie(copie, [3, 7, 1], 4, "cpu")) == 4


@pytest.mark.skipif(not (RADACINA / "lucru/stocare/modele/experiment_513.pt").exists(), reason="#513 nu e pe disc")
def test_513_cele_16_simboluri_si_logit_uri():
    from kronos.jurnal import Jurnal
    from unelte.modele_salvate import fisa_modelului, incarca_modelul

    model = incarca_modelul(fisa_modelului(Jurnal(RADACINA / "lucru"), 513), "cpu")
    retea = model.retea.float().to("cpu").eval()
    intrare = list(model.tok.codifica("Buna ziua"))
    r = compara_logit_uri(retea, intrare, 16, "cpu")
    assert r["simboluri_cu"] == ASTEPTAT_513
    assert r["simboluri_fara"] == ASTEPTAT_513
    assert r["dif_max"] <= 1e-4
