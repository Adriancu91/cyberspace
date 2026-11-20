"""S130: unelte/viteza_inferenta.py pe un GPT minuscul, pe procesor: greedy = argmax pas cu pas, cifrele ies, compararea
cu simbolurile așteptate arată poziția diferită."""

import pytest

torch = pytest.importorskip("torch")

from module.model_gpt import _GPT  # noqa: E402
from unelte.viteza_inferenta import are_memoria_pasilor, compara, greedy, masoara  # noqa: E402


@pytest.fixture(scope="module")
def retea():
    torch.manual_seed(5)
    return _GPT(vocab=50, n_straturi=2, n_capete=2, n_emb=16, context=8, dropout=0.0).eval()


def test_greedy_e_argmax_pas_cu_pas(retea):
    intrare = [3, 7, 1]
    noi = greedy(retea, intrare, 6, "cpu", 8)
    assert len(noi) == 6
    toate = list(intrare)
    with torch.no_grad():
        for s in noi:
            asteptat = int(retea(torch.tensor([toate[-8:]]))[0, -1].argmax())
            assert s == asteptat
            toate.append(s)


def test_masoara_intoarce_simbolurile_si_cifrele(retea):
    r = masoara(retea, [3, 7, 1], 4, "cpu", 8, repetari=3)
    assert r["simboluri"] == greedy(retea, [3, 7, 1], 4, "cpu", 8)
    assert len(r["secunde_rulari"]) == 3
    assert r["simb_pe_s"] > 0 and r["ms_pe_simbol"] > 0


def test_compara_arata_pozitia():
    assert compara([1, 2, 3], [1, 2, 3]) == {"identice": True, "diferente": []}
    r = compara([1, 9, 3], [1, 2, 3])
    assert r["identice"] is False and r["diferente"] == [{"pozitie": 1, "asteptat": 2, "iesit": 9}]
    assert compara([1], None) == {"identice": None}


def test_reteaua_de_acum_n_are_memoria_pasilor(retea):
    assert are_memoria_pasilor(retea) is False
