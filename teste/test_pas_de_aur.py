"""S132 (C-156): unealta „pasul de aur” (unelte/pas_de_aur.py), pe modelul mic de probă, doar procesor."""

from __future__ import annotations

import json
import math
import re
import tomllib
from pathlib import Path

import numpy as np
import pytest
import torch

from unelte import pas_de_aur as pda

RAD = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def determinist():
    """Unealta fixează algoritmii deterministici și firele; testele celelalte rămân cum erau."""
    era_det, fire = torch.are_deterministic_algorithms_enabled(), torch.get_num_threads()
    pda.fixeaza(1)
    yield
    torch.use_deterministic_algorithms(era_det)
    torch.set_num_threads(fire)


def _mic():
    retea = pda.retea_mica(pda.SAMANTA)
    x, y = pda.lot_din_samanta(pda.SAMANTA, pda.MIC["vocab"], pda.MIC["lot"], pda.MIC["context"])
    return retea, x, y


def _citeste_f32(cale: Path, forma) -> torch.Tensor:
    return torch.from_numpy(np.fromfile(cale, dtype="<f4").reshape(forma).copy())


def test_doua_rulari_dau_fisiere_identice(tmp_path):
    rezultate = []
    for k in (1, 2):
        retea, x, y = _mic()
        m = pda.exporta(retea, x, y, tmp_path / f"r{k}", pda.RETETE, {"samanta": pda.SAMANTA}, fire=1)
        rezultate.append(m)
    f1, f2 = rezultate[0]["fisiere"], rezultate[1]["fisiere"]
    assert f1 == f2
    for nume, despre in f1.items():  # SHA din reteta.json = SHA-ul fișierului de pe disc
        assert pda.sha256(tmp_path / "r1" / nume) == despre["sha256"]
    assert rezultate[0]["retete"]["sgd"]["pierderi"] == rezultate[1]["retete"]["sgd"]["pierderi"]


def test_eroarea_scade_in_10_pasi_la_ambele_retete():
    for nume, reteta in pda.RETETE.items():
        retea, x, y = _mic()
        r = pda.ruleaza_pasi(retea, x, y, reteta)
        assert len(r["pierderi"]) == 10
        assert r["pierderi"][-1] < r["pierderi"][0], nume
        assert all(b < a for a, b in zip(r["pierderi"], r["pierderi"][1:])), nume  # același lot: scade la fiecare pas
    assert all(math.isfinite(v) for v in pda.ruleaza_pasi(*_mic(), pda.RETETE["sgd"])["pierderi"])


def test_gradientul_exportat_e_gradientul_pytorch(tmp_path):
    retea, x, y = _mic()
    m = pda.exporta(retea, x, y, tmp_path / "e", pda.RETETE, {"samanta": pda.SAMANTA}, fire=1)
    proaspata, x2, y2 = _mic()
    pda.pierdere(proaspata, x2, y2).backward()
    for t in m["ordinea_tensorilor"]:
        param = dict(proaspata.named_parameters())[t["nume"]]
        for reteta in pda.RETETE:
            citit = _citeste_f32(tmp_path / "e" / reteta / "grad_pas1" / t["fisier"], t["forma"])
            assert torch.equal(citit, param.grad), (reteta, t["nume"])
        assert torch.equal(_citeste_f32(tmp_path / "e" / "initiale" / t["fisier"], t["forma"]), param.detach())
    intrari = np.fromfile(tmp_path / "e" / "intrari.i32", dtype="<i4").reshape(2, 32)
    assert (intrari == x.numpy()).all()


def test_diferente_finite_pe_5_elemente():
    """Verificare independentă, în F64: (L(w+h) − L(w−h)) / 2h față de gradientul analitic; toleranța relativă 1e-5."""
    retea, x, y = _mic()
    retea = retea.double()

    def pierdere64(r, x, y):  # ca pda.pierdere, dar fără trecerea prin F32
        logits = r(x)
        return torch.nn.functional.cross_entropy(logits.view(-1, logits.size(-1)), y.reshape(-1))

    pierdere64(retea, x, y).backward()
    params = dict(retea.named_parameters())
    alese = [("emb_token.weight", (y[0, 3].item(), 5)), ("straturi.0.atentie.in_proj_weight", (70, 11)),
             ("straturi.1.mlp.0.weight", (100, 40)), ("straturi.0.ln1.weight", (7,)), ("ln.bias", (33,))]
    h = 1e-6
    for nume, idx in alese:
        p = params[nume]
        analitic = p.grad[idx].item()
        with torch.no_grad():
            vechi = p[idx].item()
            p[idx] = vechi + h
            sus = pierdere64(retea, x, y).item()
            p[idx] = vechi - h
            jos = pierdere64(retea, x, y).item()
            p[idx] = vechi
        numeric = (sus - jos) / (2 * h)
        assert abs(numeric - analitic) <= 1e-5 * max(abs(analitic), 1e-3), (nume, numeric, analitic)
    # gradientul F32 (cel exportat) față de cel F64: toleranța 1e-4 relativ la norma tensorului
    retea32, x, y = _mic()
    pda.pierdere(retea32, x, y).backward()
    for n, p in retea32.named_parameters():
        d = (p.grad.double() - params[n].grad).norm().item()
        assert d <= 1e-4 * params[n].grad.norm().item() + 1e-9, n


def test_primul_pas_dupa_formule():
    """SGD: w1 = w0 − 0,01·g. AdamW (pasul 1, cu tăierea la 1,0): w1 = w0·(1 − lr·wd) − lr·m̂/(√v̂ + eps)."""
    retea, x, y = _mic()
    w0 = {n: p.detach().clone() for n, p in retea.named_parameters()}
    r = pda.ruleaza_pasi(retea, x, y, pda.RETETE["sgd"], pasi=1)
    for n in w0:
        assert torch.allclose(r["dupa_pas1"][n], w0[n] - 0.01 * r["grad_pas1"][n], rtol=1e-6, atol=1e-7), n
    retea, x, y = _mic()
    a = pda.RETETE["adamw_513"]
    r = pda.ruleaza_pasi(retea, x, y, a, pasi=1)
    norma = torch.linalg.vector_norm(torch.stack([torch.linalg.vector_norm(g) for g in r["grad_pas1"].values()]))
    factor = min(1.0, a["taiere_gradient"] / (norma.item() + 1e-6))
    b1, b2 = a["betas"]
    for n in w0:
        g = r["grad_pas1"][n] * factor
        m_hat, v_hat = (1 - b1) * g / (1 - b1), (1 - b2) * g * g / (1 - b2)
        asteptat = w0[n] * (1 - a["lr"] * a["weight_decay"]) - a["lr"] * m_hat / (v_hat.sqrt() + a["eps"])
        assert torch.allclose(r["dupa_pas1"][n], asteptat, rtol=1e-6, atol=1e-7), n


def test_reteta_adamw_e_cea_a_liniei_lui_513():
    cfg = tomllib.loads((RAD / "config/conv_w2_romana_r1.toml").read_text(encoding="utf-8"))
    setari = cfg["porturi"]["model"]["setari"]
    assert cfg["porturi"]["model"]["modul"] == "module.model_muon:ModelGPTConversatieMuon"
    assert setari["optimizator"] == "adamw" and setari["rata_invatare"] == pda.RETETE["adamw_513"]["lr"]
    cod = (RAD / "module/model_muon.py").read_text(encoding="utf-8")
    assert "torch.optim.AdamW(self.retea.parameters(), lr=self.rata_invatare, weight_decay=0.1)" in cod
    assert len(re.findall(r"clip_grad_norm_\(self\.retea\.parameters\(\), 1\.0\)", cod)) == 2
    implicit = torch.optim.AdamW([torch.nn.Parameter(torch.zeros(1))]).defaults
    a = pda.RETETE["adamw_513"]
    assert list(implicit["betas"]) == a["betas"] and implicit["eps"] == a["eps"] and implicit["amsgrad"] == a["amsgrad"]
    assert a["weight_decay"] == 0.1 and a["taiere_gradient"] == 1.0


def test_refuza_dosar_existent_si_reteta_json(tmp_path):
    retea, x, y = _mic()
    (tmp_path / "e").mkdir()
    with pytest.raises(SystemExit):
        pda.exporta(retea, x, y, tmp_path / "e", pda.RETETE, {}, fire=1)
    assert pda.main(["mic", "--iesire", str(tmp_path / "m")]) == 0
    m = json.loads((tmp_path / "m" / "reteta.json").read_text(encoding="utf-8"))
    assert m["marime_totala_octeti"] < pda.MARIME_MAXIMA_MIC
    assert m["ordinea_tensorilor"][0]["nume"] == "emb_token.weight"
    assert not any(t["nume"].startswith("cap.") for t in m["ordinea_tensorilor"])  # legat de emb_token
    assert set(m["retete"]) == {"sgd", "adamw_513"}
    assert len(m["fisiere"]) == 2 + len(m["ordinea_tensorilor"]) * 7
