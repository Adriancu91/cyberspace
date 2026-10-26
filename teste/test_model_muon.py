"""S30 (C-21.2): Muon, gradientul adunat și răcirea de la final (module/model_muon.py), pe procesor."""

from __future__ import annotations

import json

import pytest

torch = pytest.importorskip("torch")

from module.model_conversatie import ModelGPTConversatie  # noqa: E402
from module.model_muon import ModelGPTConversatieMuon, MuonCuAdamW, grupuri_muon, newton_schulz  # noqa: E402


@pytest.fixture
def mic(tmp_path):
    """Un text, o hrană, perechi și un tokenizer mic: setările unui model de conversație mic, pe procesor."""
    from module.tokenizer_bpe import antreneaza_bpe

    text = ("Once upon a time there was a dog. " * 200) + "<|endoftext|>"
    (tmp_path / "hrana.txt").write_text("Birds have feathers. " * 200, encoding="utf-8")
    (tmp_path / "conv.jsonl").write_text("\n".join(json.dumps({"intrebare": f"Ce face cățelul {i}?", "raspuns": "Latră."})
                                                   for i in range(20)), encoding="utf-8")
    antreneaza_bpe(text + " Întrebare: Răspuns: Ce face cățelul? Latră.", 300).salveaza(tmp_path / "bpe.json")

    class Date:
        def text_antrenare(self):
            return text

    setari = dict(n_straturi=2, n_capete=2, n_emb=32, context=32, lot=6, dispozitiv="cpu", tokenizer="bpe",
                  cale_tokenizer=str(tmp_path / "bpe.json"), rata_invatare=3e-3, rata_care_scade=True,
                  incalzire_pasi=5, fractie_rata_finala=1.0, pasi_max=24, conversatie=str(tmp_path / "conv.jsonl"),
                  fractie_conversatie=0.45, hrana=str(tmp_path / "hrana.txt"), fractie_hrana=0.05, samanta=0)
    return setari, Date()


def test_fara_optiunile_noi_face_exact_aceiasi_pasi(mic):
    """Valorile implicite: AdamW, fără adunare, fără răcire → aceleași greutăți, bit cu bit, ca ModelGPTConversatie."""
    setari, date = mic
    vechi, nou = ModelGPTConversatie(**setari), ModelGPTConversatieMuon(**setari)
    s_vechi = vechi.antreneaza(date, 600.0)
    a = {k: v.clone() for k, v in vechi.retea.state_dict().items()}  # al doilea model o eliberează (ia_placa)
    s_nou = nou.antreneaza(date, 600.0)
    assert s_vechi["pasi"] == s_nou["pasi"] == s_nou["pasi_optimizator"] == 24
    assert s_vechi["pierdere_finala"] == s_nou["pierdere_finala"]
    assert s_vechi["rata_la_final"] == s_nou["rata_la_final"]
    b = nou.retea.state_dict()
    assert a.keys() == b.keys() and all(torch.equal(a[k], b[k]) for k in a)


def test_fara_conversatie_face_exact_aceiasi_pasi(mic):
    setari, date = mic
    setari = {**setari, "conversatie": "", "fractie_conversatie": 0.0}
    vechi, nou = ModelGPTConversatie(**setari), ModelGPTConversatieMuon(**setari)
    vechi.antreneaza(date, 600.0)
    a = {k: v.clone() for k, v in vechi.retea.state_dict().items()}
    nou.antreneaza(date, 600.0)
    b = nou.retea.state_dict()
    assert all(torch.equal(a[k], b[k]) for k in a)


# O matrice pătrată la întâmplare are valori singulare aproape de 0, pe care 5 pași nu le urcă până la 0,6 (măsurat: 0,59);
# gradienții din straturi și matricile dreptunghiulare (MLP-ul: 768 × 3.072) intră în ~[0,6; 1,2].
@pytest.mark.parametrize("forma", [(32, 96), (96, 32), (48, 192)])
def test_newton_schulz_aduce_valorile_singulare_spre_1(forma):
    g = torch.randn(*forma, generator=torch.Generator().manual_seed(1))
    s = torch.linalg.svdvals(newton_schulz(g).float())
    assert 0.6 <= s.min().item() and s.max().item() <= 1.2


def test_muon_scade_pierderea_pe_un_mlp_mic_si_updateul_e_ortogonal():
    torch.manual_seed(0)
    mlp = torch.nn.Sequential(torch.nn.Linear(16, 64), torch.nn.GELU(), torch.nn.Linear(64, 1))
    x = torch.randn(256, 16)
    y = (x[:, :1] * x[:, 1:2]).sin()
    rata = 0.02
    opt = MuonCuAdamW([{"params": [mlp[0].weight], "muon": True, "weight_decay": 0.0},
                       {"params": [mlp[0].bias, mlp[2].weight, mlp[2].bias]}], lr=rata)
    pierderi = []
    for pas in range(200):
        loss = torch.nn.functional.mse_loss(mlp(x), y)
        opt.zero_grad()
        loss.backward()
        inainte = mlp[0].weight.detach().clone()
        opt.step()
        pierderi.append(loss.item())
        if pas in (0, 100):  # update-ul matricii Muon, fără rată și scară (64 × 16: √(64/16) = 2)
            update = (inainte - mlp[0].weight.detach()) / (rata * 2.0)
            s = torch.linalg.svdvals(update)
            assert 0.6 <= s.min().item() and s.max().item() <= 1.2
    assert pierderi[-1] < 0.5 * pierderi[0]


def test_partea_adamw_e_ca_adamw_din_pytorch():
    torch.manual_seed(0)
    a = torch.nn.Linear(8, 4)
    b = torch.nn.Linear(8, 4)
    b.load_state_dict(a.state_dict())
    oa = torch.optim.AdamW(a.parameters(), lr=1e-2, weight_decay=0.1)
    ob = MuonCuAdamW([{"params": list(b.parameters())}], lr=1e-2, weight_decay=0.1)
    x = torch.randn(32, 8)
    for _ in range(20):
        for m, o in ((a, oa), (b, ob)):
            o.zero_grad()
            m(x).pow(2).mean().backward()
            o.step()
    for pa, pb in zip(a.parameters(), b.parameters()):
        assert torch.allclose(pa, pb, atol=1e-6)


def test_grupurile_si_rata_muon(mic):
    setari, date = mic
    model = ModelGPTConversatieMuon(**setari, optimizator="muon", rata_muon=0.02)
    model.antreneaza(date, 600.0)
    grupuri = model.optimizator.param_groups
    assert [g["muon"] for g in grupuri] == [False, True, True]
    assert grupuri[2]["bucati"] == 3 and len(grupuri[2]["params"]) == 2  # q/k/v combinate, câte una pe strat
    assert len(grupuri[1]["params"]) == 2 * 3  # out_proj + cele 2 din MLP, pe fiecare strat
    assert grupuri[1]["multiplicator_lr"] == pytest.approx(0.02 / 3e-3)
    restul = grupuri[0]["params"]
    assert any(p is model.retea.emb_token.weight for p in restul)  # intrarea (legată de ieșire) rămâne la AdamW
    assert all(p.ndim == 1 for p in restul if p is not model.retea.emb_token.weight
               and p is not model.retea.emb_pozitie.weight)


def test_adunarea_pe_8_loturi(mic):
    setari, date = mic
    model = ModelGPTConversatieMuon(**{**setari, "pasi_max": 20}, optimizator="muon", adunare_loturi=8)
    s = model.antreneaza(date, 600.0)
    assert s["pasi"] == 20 and s["pasi_optimizator"] == 2 and s["loturi_aruncate"] == 4
    assert s["optimizator"] == "muon" and s["adunare_loturi"] == 8


def test_raciera_de_la_final():
    model = ModelGPTConversatieMuon(n_straturi=1, n_capete=1, n_emb=8, context=8, lot=2, dispozitiv="cpu",
                                    rata_invatare=1e-3, rata_care_scade=True, incalzire_pasi=0, fractie_rata_finala=1.0,
                                    durata_scaderii_secunde=7200, racire_finala=0.25)
    assert model.rata_acum(10, 0.5) == pytest.approx(1e-3)
    assert model.rata_acum(10, 0.75) == pytest.approx(1e-3)
    assert model.rata_acum(10, 0.875) == pytest.approx(0.5e-3)
    assert model.rata_acum(10, 1.0) == pytest.approx(0.0)
    with pytest.raises(ValueError):  # răcirea cere toată durata antrenării
        ModelGPTConversatieMuon(rata_care_scade=True, racire_finala=0.25)
    with pytest.raises(ValueError):
        ModelGPTConversatieMuon(optimizator="sgd")


def test_starea_se_salveaza_si_se_reia(mic, tmp_path):
    setari, date = mic
    cale = tmp_path / "gpt.pt"
    model = ModelGPTConversatieMuon(**setari, optimizator="muon", adunare_loturi=4, cale_stare=str(cale))
    model.antreneaza(date, 600.0)
    model._salveaza_starea({"scor": 1.0})
    din_nou = ModelGPTConversatieMuon(**setari, optimizator="muon", adunare_loturi=4, cale_stare=str(cale))
    s = din_nou.antreneaza(date, 600.0)
    assert s["continuat"] and s["pasi_total"] == 48
    assert din_nou.optimizator.state  # momentum-ul și momentele AdamW s-au încărcat


def test_porneste_din_starea_cu_adamw_gol(mic, tmp_path):
    """Starea de pornire din antrenare_lunga.py --porneste-din are un AdamW gol: Muon pornește cu optimizatorul lui."""
    setari, date = mic
    sursa = ModelGPTConversatie(**setari)
    sursa.antreneaza(date, 600.0)
    gol = torch.optim.AdamW(sursa.retea.parameters(), lr=3e-3, weight_decay=0.1)
    cale = tmp_path / "pornire.pt"
    torch.save({"setari": sursa.setari, "retea": sursa.retea.state_dict(), "optimizator": gol.state_dict(),
                "pasi_total": 0, "minute": 0.0, "scor": 1.0}, cale)
    model = ModelGPTConversatieMuon(**setari, optimizator="muon", cale_stare=str(cale))
    s = model.antreneaza(date, 600.0)
    assert s["continuat"] and isinstance(model.optimizator, MuonCuAdamW)


def test_proba_rezuma_pierderea_pe_pasi():
    from unelte.proba_muon import rezumat_pierderi

    r = rezumat_pierderi([4.0, 2.0, 3.0, 1.0, 9.0], 2)
    assert r["loturi"] == 5 and r["primul_lot"] == 4.0
    assert r["primii_pasi"] == [3.0, 2.0] and r["cea_mai_mare_in_primii_20_pasi"] == 3.0


def test_grupuri_muon_fara_matrici():
    retea = torch.nn.Sequential(torch.nn.LayerNorm(4))
    assert len(grupuri_muon(retea, 1e-3, 0.02)) == 1
