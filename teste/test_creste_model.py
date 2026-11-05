"""S77a: creșterea în adâncime cu straturi „neutre” (unelte/creste_model.py)."""

import json

import pytest
import torch

from unelte import creste_model as cm

MIC = dict(n_straturi=2, n_capete=4, n_emb=32, context=64, dropout=0.0)
VOCAB = 16384  # tokenizerul adevărat (date/ws/bpe_16384.json), ca modelul să se poată încărca de clasa S51


def _retea_mica(samanta=7):
    """Ca vectori_kgr1.model_mic: greutăți la întâmplare, destul de mari ca straturile să conteze."""
    from module.model_gpt import _GPT

    torch.manual_seed(samanta)
    r = _GPT(VOCAB, **MIC)
    g = torch.Generator().manual_seed(samanta)
    with torch.no_grad():
        for nume, p in r.named_parameters():
            if nume == "emb_token.weight":
                p.copy_(0.3 * torch.randn(p.shape, generator=g))
            elif p.ndim == 2:
                p.copy_(torch.randn(p.shape, generator=g) / p.shape[1] ** 0.5)
            elif nume.split(".")[-2].startswith("ln"):
                p.copy_(1.0 + 0.1 * torch.randn(p.shape, generator=g) if nume.endswith("weight")
                        else 0.1 * torch.randn(p.shape, generator=g))
            else:
                p.copy_(0.1 * torch.randn(p.shape, generator=g))
    return r.eval()


def _sursa(tmp_path):
    r = _retea_mica()
    cale = tmp_path / "gpt.pt"
    opt = torch.optim.AdamW(r.parameters())
    torch.save({"setari": MIC, "retea": r.state_dict(), "optimizator": opt.state_dict(), "pasi_total": 1234,
                "minute": 56.0, "scor": 0.5}, cale)
    return r, cale


def test_planul_imprastie_uniform():
    assert cm.planul(12, 24) == [(j, e) for j in range(12) for e in (False, True)]
    for nou in (30, 36, 42):
        plan = cm.planul(12, nou)
        assert len(plan) == nou and [j for j, e in plan if not e] == list(range(12))
        dupa = [sum(1 for j, e in plan if e and j == k) for k in range(12)]
        assert max(dupa) - min(dupa) <= 1  # nu toate la capăt
        assert all(j == plan[i - 1][0] for i, (j, e) in enumerate(plan) if e)  # copia stratului de dedesubt
    assert cm.planul(12, 12) == [(j, False) for j in range(12)]
    with pytest.raises(ValueError):
        cm.planul(12, 6)


def test_forme_si_zerouri():
    r = _retea_mica()
    vechi = r.state_dict()
    nou = cm.creste_stare(vechi, 2, 4)
    assert set(nou) == {k for k in vechi if not k.startswith("straturi.")} | {
        k.replace("straturi.0.", f"straturi.{i}.") for k in vechi if k.startswith("straturi.0.") for i in range(4)}
    for i, (j, e_nou) in enumerate(cm.planul(2, 4)):
        for rest in ("ln1.weight", "atentie.in_proj_weight", "atentie.in_proj_bias", "ln2.bias", "mlp.0.weight"):
            assert torch.equal(nou[f"straturi.{i}.{rest}"], vechi[f"straturi.{j}.{rest}"])
        for rest in cm.NULE:
            t = nou[f"straturi.{i}.{rest}"]
            assert t.shape == vechi[f"straturi.{j}.{rest}"].shape
            assert (not t.any()) if e_nou else torch.equal(t, vechi[f"straturi.{j}.{rest}"])
    assert torch.equal(vechi["straturi.0.mlp.2.weight"], r.state_dict()["straturi.0.mlp.2.weight"])  # sursa neatinsă


def test_modelul_crescut_da_aceleasi_logituri():
    r = _retea_mica()
    noua = cm.retea_din({**MIC, "n_straturi": 4}, cm.creste_stare(r.state_dict(), 2, 4))
    siruri = [list(range(5, 45)), [3, 99, 1000, 16000, 7]]
    rez = cm.compara_retele(r, noua, siruri)
    assert rez["dif_max_logit"] <= 1e-5 and rez["argmax_identic"] == 1.0
    x = torch.tensor([siruri[0]])
    with torch.no_grad():
        assert float(r(x).abs().max()) > 1.0  # logit-urile nu sunt toate ~0 (testul spune ceva)


def test_creste_scrie_starea_de_pornire_si_nu_scrie_peste(tmp_path):
    _, sursa = _sursa(tmp_path)
    iesire = tmp_path / "mare" / "gpt_4.pt"
    info = cm.creste(str(sursa), 4, str(iesire))
    assert info["sha256_din"] == info["sha256_din_dupa"] and info["straturi"] == 4
    s = torch.load(iesire, map_location="cpu", weights_only=True)
    assert s["setari"] == {**MIC, "n_straturi": 4} and s["pasi_total"] == 0 and s["minute"] == 0.0
    assert not s["optimizator"]["state"]  # starea optimizatorului nu se copiază
    assert json.loads(iesire.with_suffix(".json").read_text(encoding="utf-8"))["sha256"] == cm.sha256(iesire)
    with pytest.raises(FileExistsError):
        cm.creste(str(sursa), 4, str(iesire))


def test_clasa_S51_incarca_fisierul_fara_schimbari(tmp_path):
    """ModelGPTConversatieMuon cu cale_stare = fișierul crescut: pornește din el, cu pașii de la 0."""
    from module.model_muon import ModelGPTConversatieMuon
    from module.tokenizer_bpe import TokenizerBPE

    r, sursa = _sursa(tmp_path)
    iesire = tmp_path / "gpt_4.pt"
    cm.creste(str(sursa), 4, str(iesire))
    m = ModelGPTConversatieMuon(**{**MIC, "n_straturi": 4}, tokenizer="bpe",
                                cale_tokenizer=str(cm.RADACINA / cm.TOKENIZER), cale_stare=str(iesire),
                                dispozitiv="cpu", adunare_loturi=8)
    m.tok = TokenizerBPE.incarca(cm.RADACINA / cm.TOKENIZER)
    m._pregateste_reteaua()
    assert m.continuat and m.pasi_total == 0 and m.minute_total == 0.0
    assert not m.optimizator.state_dict()["state"]
    m.retea.eval()
    x = torch.tensor([list(range(10, 40))])
    with torch.no_grad():
        assert float((m.retea(x) - r(x)).abs().max()) <= 1e-5
    # și calea uneltei (model_din_gpt, folosită de export și de examenul de română)
    m2 = cm.model_din_gpt(iesire, "cpu")
    with torch.no_grad():
        assert float((m2.retea(x) - r(x)).abs().max()) <= 1e-5


def test_exportul_kgr1_al_fisierului_crescut(tmp_path):
    from unelte import exporta_greutati

    r, sursa = _sursa(tmp_path)
    iesire = tmp_path / "gpt_4.pt"
    cm.creste(str(sursa), 4, str(iesire))
    mic = cm.model_din_gpt(sursa, "cpu")
    exporta_greutati.exporta_model(mic, tmp_path / "vechi.kgr", "f32")
    assert exporta_greutati.main(["--gpt", str(iesire), "--fel", "f32", "--iesire", str(tmp_path / "nou.kgr")]) == 0
    rez = cm.compara_kgr(str(tmp_path / "vechi.kgr"), str(tmp_path / "nou.kgr"))
    assert rez["straturi_vechi"] == 2 and rez["straturi_nou"] == 4
    assert rez["greedy_identic_toate"] and rez["dif_max_logit_ultima"] <= 1e-4


def test_alegerea_dupa_regula():
    def r(n, mb, v, rec=False, cod=0):
        return {"straturi": n, "nvidia_smi_varf_mb": mb, "pasi_pe_secunda": v, "recalcul": rec, "cod": cod}

    rez = [r(12, 3000, 6.4), r(24, 4800, 3.3), r(30, 5600, 2.7), r(36, 6900, 2.3), r(36, 5200, 1.8, True),
           r(42, 7100, 0, cod=1), r(42, 5900, 1.5, True)]
    assert cm.alege(rez)["straturi"] == 30
    assert cm.alege([r(24, 6400, 3.0), r(24, 5000, 2.5, True)])["recalcul"] is False
    assert cm.alege([r(24, 6600, 3.0), r(24, 5000, 2.5, True)])["recalcul"] is True
    assert cm.alege([r(12, 3000, 6.4), r(24, 6600, 1.9)]) is None
