"""S32: fișierul KGR1 (unelte/exporta_greutati.py) și motorul fără PyTorch (unelte/inferenta_bruta.py), pe un GPT mic cu
greutăți la întâmplare: strat cu strat, logits, biți și completarea, față de PyTorch."""

import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

torch = pytest.importorskip("torch")

from module.date_mostra import DateMostra  # noqa: E402
from module.model_gpt import ModelGPT  # noqa: E402
from module.tokenizer_bpe import TokenizerBPE, antreneaza_bpe  # noqa: E402
from unelte.exporta_greutati import (  # noqa: E402
    ALINIERE, BLOC_Q8, TensorQ8, citeste, cuantizeaza_q8, exporta_model, scrie,
)
from unelte.inferenta_bruta import MotorBrut, erf, gelu, layer_norm, softmax  # noqa: E402

RADACINA = Path(__file__).resolve().parents[1]
TEXTE = ["Ana are mere și pere.", "Once upon a time, a little dog ran to the park.", "Capitala României este București."]


@pytest.fixture(scope="module")
def model_mic(tmp_path_factory):
    cale = tmp_path_factory.mktemp("tok") / "tok.json"
    antreneaza_bpe(DateMostra(propozitii=600).text_antrenare() + " ".join(TEXTE), 320).salveaza(cale)
    m = ModelGPT(n_straturi=2, n_capete=4, n_emb=64, context=16, tokenizer="bpe", cale_tokenizer=str(cale),
                 dispozitiv="cpu", samanta=7)
    m.tok = TokenizerBPE.incarca(cale)
    m._construieste()
    g = torch.Generator().manual_seed(3)
    with torch.no_grad():  # LayerNorm și deplasările nu mai sunt 1 și 0: testul vede dacă motorul le folosește
        for p in m.retea.parameters():
            p.add_(0.05 * torch.randn(p.shape, generator=g))
    return m


@pytest.fixture(scope="module")
def fisiere(model_mic, tmp_path_factory):
    d = tmp_path_factory.mktemp("kgr")
    exporta_model(model_mic, d / "f32.kgr", "f32")
    exporta_model(model_mic, d / "q8.kgr", "q8_0")
    return d / "f32.kgr", d / "q8.kgr"


def test_fisierul_dus_intors_si_aliniat(tmp_path):
    w = np.arange(64 * 2, dtype=np.float32).reshape(2, 64) / 7
    chei = {"n": 3, "x": 0.5, "s": "ăîșț"}
    marime = scrie(tmp_path / "a.kgr", chei, {"b": np.ones(5, np.float32), "w": w, "q": cuantizeaza_q8(w)})
    assert marime == (tmp_path / "a.kgr").stat().st_size and marime % ALINIERE == 0
    chei2, t = citeste(tmp_path / "a.kgr")
    assert chei2 == chei
    assert np.array_equal(t["b"], np.ones(5)) and np.array_equal(t["w"], w)
    assert isinstance(t["q"], TensorQ8) and t["q"].forma == (2, 64)
    with pytest.raises(ValueError, match="KGR1"):
        (tmp_path / "rau.kgr").write_bytes(b"GGUF" + bytes(40))
        citeste(tmp_path / "rau.kgr")


def test_q8_eroarea_e_cel_mult_jumatate_de_scara():
    w = np.random.default_rng(0).normal(size=(3, 4 * BLOC_Q8)).astype(np.float32)
    w[1, :BLOC_Q8] = 0.0  # un bloc gol: scara 0, fără împărțire la 0
    q = cuantizeaza_q8(w)
    assert q.numere.dtype == np.int8 and q.scari.shape == (3, 4)
    eroare = np.abs(q.desfa() - w).reshape(3, 4, BLOC_Q8).max(axis=2)
    assert np.all(eroare <= q.scari / 2 + 1e-7) and q.scari[1, 0] == 0
    with pytest.raises(ValueError):
        cuantizeaza_q8(np.ones((2, 33), np.float32))


def test_erf_si_gelu_ca_pytorch():
    x = np.linspace(-6, 6, 2001, dtype=np.float32)
    assert np.abs(erf(x) - torch.erf(torch.from_numpy(x).double()).numpy()).max() < 2e-7
    assert np.abs(gelu(x) - torch.nn.functional.gelu(torch.from_numpy(x)).numpy()).max() < 1e-6


def test_layer_norm_si_softmax_aduna_in_float64():
    """S37: pe valori mari cu abateri mici, adunarea în float32 pierde cifre; motorul trebuie să dea ce dă float64."""
    rng = np.random.default_rng(1)
    x = (3000.0 + 0.05 * rng.normal(size=(4, 768))).astype(np.float32)
    w = rng.normal(size=768).astype(np.float32)
    b = rng.normal(size=768).astype(np.float32)
    x64 = x.astype(np.float64)
    m = x64.mean(-1, keepdims=True)
    asteptat = (x64 - m) / np.sqrt(((x64 - m) ** 2).mean(-1, keepdims=True) + 1e-5) * w + b
    y = layer_norm(x, w, b, 1e-5)
    assert y.dtype == np.float32
    assert np.abs(y - asteptat).max() < 1e-5
    m32 = x.mean(-1, keepdims=True)  # ce dădea adunarea în float32 (S32): testul chiar deosebește cele două
    vechi = (x - m32) / np.sqrt(((x - m32) ** 2).mean(-1, keepdims=True) + 1e-5) * w + b
    assert np.abs(vechi - asteptat).max() > 1e-3
    s = softmax(rng.normal(size=(2, 50)).astype(np.float32))
    assert s.dtype == np.float64 and np.allclose(s.sum(-1), 1.0, atol=1e-15)


def test_q8_doar_pe_greutati(fisiere):
    _, t = citeste(fisiere[1])
    for nume, v in t.items():
        forma = v.forma if isinstance(v, TensorQ8) else v.shape
        assert isinstance(v, TensorQ8) == (len(forma) == 2), nume
    assert "cap.weight" not in t and "straturi.0.atentie.in_proj_weight" in t


def test_strat_cu_strat_ca_pytorch(model_mic, fisiere):
    motor = MotorBrut(fisiere[0])
    simboluri = model_mic.tok.codifica(TEXTE[1])[:16]
    idx = torch.tensor([simboluri])
    retea = model_mic.retea.eval()
    with torch.no_grad():
        x = retea.emb_token(idx) + retea.emb_pozitie(torch.arange(len(simboluri)))
        asteptate = [x[0].numpy()]
        for strat in retea.straturi:
            x = strat(x)
            asteptate.append(x[0].numpy())
    stari = motor.straturi(simboluri)
    assert len(stari) == len(asteptate) == 3
    for a, b in zip(stari, asteptate):
        assert np.abs(a - b).max() < 1e-5


def test_logits_biti_si_completarea_ca_pytorch(model_mic, fisiere):
    motor = MotorBrut(fisiere[0])
    for text in TEXTE:
        s = model_mic.tok.codifica(text)[:16]
        with torch.no_grad():
            asteptat = model_mic.retea.eval()(torch.tensor([s]))[0].numpy()
        assert np.abs(motor.logits(s) - asteptat).max() < 1e-4
        # biți pe un text mai lung decât contextul (mai multe ferestre + rest), ca examenul
        lung = text * 4
        assert motor.biti_pentru(lung) == pytest.approx(model_mic.biti_pentru(lung), rel=1e-5)
        # completarea trece de context: cache-ul, apoi fereastra care alunecă
        assert motor.completeaza(text, 20) == model_mic.completeaza(text, 20)


def test_q8_aproape_de_f32_si_cele_doua_desfaceri_la_fel(model_mic, fisiere):
    f32, q8 = MotorBrut(fisiere[0]), MotorBrut(fisiere[1])
    pas = MotorBrut(fisiere[1], desfacere="la_pas")
    s = model_mic.tok.codifica(TEXTE[2])[:16]
    asteptat = f32.logits(s)  # Q8_0: abaterea mică față de mărimea logits-urilor (pragul adevărat e pe bpb, la #415)
    assert np.abs(q8.logits(s) - asteptat).max() < 0.05 * np.abs(asteptat).max()
    assert np.array_equal(q8.logits(s), pas.logits(s))
    assert pas.octeti_greutati() < q8.octeti_greutati() / 2
    with pytest.raises(ValueError):
        MotorBrut(fisiere[0], desfacere="altfel")


def test_motorul_nu_incarca_pytorch(fisiere):
    cod = ("import sys; sys.path.insert(0, sys.argv[1]); from unelte.inferenta_bruta import MotorBrut; "
           "m = MotorBrut(sys.argv[2]); m.completeaza('Ana', 3); print('torch' in sys.modules)")
    iesire = subprocess.run([sys.executable, "-c", cod, str(RADACINA), str(fisiere[1])], capture_output=True, text=True,
                            check=True).stdout
    assert iesire.strip() == "False"
