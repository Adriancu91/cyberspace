"""S135 (C-163): `module/model_trepte.py` și `unelte/laborator_trepte.py` — pasul pe simboluri = pasul de azi, faza pe
bucăți (media încorporărilor, eroarea pe K ținte, gradientul), trecerea între faze, rata după ceas, unealta cap-coadă."""

from __future__ import annotations

import json
import math

import pytest

torch = pytest.importorskip("torch")

from module.model_gpt import ModelGPT  # noqa: E402
from module.model_trepte import ModelTrepte, pierdere_bucati  # noqa: E402

MIC = {"n_straturi": 2, "n_capete": 2, "n_emb": 16, "context": 16, "lot": 3, "dispozitiv": "cpu", "samanta": 7,
       "tokenizer": "litere"}
LITERE = list("abcdefghijklmnopqrstuvwxyz ")


def _gata(clasa, **setari):
    m = clasa(**{**MIC, **setari})
    m.vocabular = list(LITERE)
    m._pregateste_reteaua()
    return m


def _fereastra(lot: int, lungime: int, samanta: int = 0) -> torch.Tensor:
    g = torch.Generator().manual_seed(samanta)
    return torch.randint(len(LITERE), (lot, lungime), generator=g)


def test_k1_e_pasul_de_azi():
    """K = 1: aceeași inițializare, aceeași pierdere și aceleași greutăți după pas ca ModelGPT._pas (F32, procesor)."""
    azi = _gata(ModelGPT, rata_invatare=1e-3)
    nou = _gata(ModelTrepte, rata_invatare=1e-3)
    for a, b in zip(azi.retea.state_dict().values(), nou.retea.state_dict().values()):
        assert torch.equal(a, b)
    f = _fereastra(3, 17)
    for _ in range(3):
        pierdere_azi = azi._pas(f[:, :16].contiguous(), f[:, 1:].contiguous(), None)
        pierdere_noua = nou.pas_optimizator([f], "simboluri")["pierdere"]
        assert pierdere_noua == pytest.approx(pierdere_azi, rel=1e-6, abs=1e-7)
    for a, b in zip(azi.retea.parameters(), nou.retea.parameters()):
        assert torch.allclose(a, b, atol=1e-6)


def test_media_incorporarilor_si_eroarea_pe_k_tinte_de_mana():
    """Rețea fără straturi, LN identitate, poziții zero, cap = încorporările: logits = media(E[bucată]) · Eᵀ."""
    m = ModelTrepte(**{**MIC, "n_emb": 2, "context": 4, "n_capete": 1, "k_bucata": 2})
    m.vocabular = ["a", "b", "c", "d"]
    m._pregateste_reteaua()
    r = m.retea
    r.straturi = torch.nn.ModuleList()
    r.ln = torch.nn.Identity()
    with torch.no_grad():
        r.emb_token.weight.copy_(torch.tensor([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0], [0.0, 0.0]]))
        r.emb_pozitie.weight.zero_()
    # fereastra de context + K = 6 simboluri: bucățile (a,b) (c,d) (b,c); intrări = primele 2, ținte = ultimele 2
    f = torch.tensor([[0, 1, 2, 3, 1, 2]])
    logits = r.inainte_bucati(f[:, :4].reshape(1, 2, 2))
    # media(a,b) = (0,5; 0,5) → logits = (0,5; 0,5; 1; 0); media(c,d) = (0,5; 0,5) → aceleași
    asteptat = torch.tensor([0.5, 0.5, 1.0, 0.0])
    assert torch.allclose(logits[0, 0], asteptat) and torch.allclose(logits[0, 1], asteptat)
    lse = math.log(2 * math.exp(0.5) + math.exp(1.0) + 1.0)
    # ținte: bucata 1 → (c, d): −(1 − lse) și −(0 − lse); bucata 2 → (b, c): −(0,5 − lse) și −(1 − lse)
    de_mana = ((lse - 1.0) + (lse - 0.0) + (lse - 0.5) + (lse - 1.0)) / 4
    assert m.pierdere_pe_bucati(f, 2).item() == pytest.approx(de_mana, rel=1e-6)
    assert pierdere_bucati(logits, torch.tensor([[[2, 3], [1, 2]]])).item() == pytest.approx(de_mana, rel=1e-6)


def test_gradientul_fazei_pe_bucati_fata_de_diferente_finite():
    m = _gata(ModelTrepte, k_bucata=4)
    m.retea.double()
    f = _fereastra(2, 16 + 4, samanta=3)
    m.retea.zero_grad()
    m.pierdere_pe_bucati(f, 4).backward()
    h = 1e-6
    alese = [(m.retea.emb_token.weight, (3, 5)), (m.retea.emb_pozitie.weight, (1, 2)),
             (m.retea.straturi[0].mlp[0].weight, (7, 4)), (m.retea.straturi[1].atentie.in_proj_weight, (20, 9)),
             (m.retea.ln.weight, (11,))]
    for parametru, loc in alese:
        analitic = parametru.grad[loc].item()
        with torch.no_grad():
            vechi = parametru[loc].item()
            parametru[loc] = vechi + h
            sus = m.pierdere_pe_bucati(f, 4).item()
            parametru[loc] = vechi - h
            jos = m.pierdere_pe_bucati(f, 4).item()
            parametru[loc] = vechi
        assert analitic == pytest.approx((sus - jos) / (2 * h), rel=1e-5, abs=1e-8)


def test_trecerea_bucati_simboluri_pastreaza_greutatile_si_adamw():
    m = _gata(ModelTrepte, k_bucata=4, adunare_loturi=2)
    opt = m.optimizator
    for _ in range(2):
        m.pas_optimizator([_fereastra(3, 20, 1), _fereastra(3, 20, 2)], "bucati")
    greutati = {n: p.detach().clone() for n, p in m.retea.named_parameters()}
    stari = {id(p): {k: v.clone() for k, v in opt.state[p].items()} for p in m.retea.parameters()}
    assert all(int(s["step"]) == 2 for s in stari.values())
    # pasul pe simboluri pornește din aceleași greutăți și aceeași stare AdamW (nu se repornește nimic)
    for n, p in m.retea.named_parameters():
        assert torch.equal(p, greutati[n])
    m.pas_optimizator([_fereastra(3, 17, 4), _fereastra(3, 17, 5)], "simboluri")
    assert m.optimizator is opt
    for p in m.retea.parameters():
        assert int(opt.state[p]["step"]) == 3
        # exp_avg nou = 0,9 · vechi + 0,1 · grad (deci vechiul a fost păstrat)
        asteptat = 0.9 * stari[id(p)]["exp_avg"] + 0.1 * p.grad
        assert torch.allclose(opt.state[p]["exp_avg"], asteptat, atol=1e-7)


def test_bucla_trece_prin_ambele_faze_si_scrie_semnale():
    m = _gata(ModelTrepte, k_bucata=4, minute_bucati=0.75 / 60, incalzire_secunde=0.2, racire_secunde=0.3)
    sir = torch.randint(len(LITERE), (2000,), generator=torch.Generator().manual_seed(9))
    semnale = []
    r = m.bucla(sir, 1.5, la_fiecare=lambda s: semnale.append(s) or None, secunde_intre_semnale=0.25)
    assert r["oprit"] is None
    assert r["pe_faza"]["bucati"]["pasi"] > 0 and r["pe_faza"]["simboluri"]["pasi"] > 0
    assert r["simboluri_vazute"] == r["pasi"] * 3 * 16
    faze = [s["faza"] for s in semnale]
    assert faze[0] == "bucati" and faze[-1] == "simboluri" and faze == sorted(faze)  # „bucati” < „simboluri”
    assert r["rata_la_final"] < m.rata_invatare  # răcirea a lucrat


def test_paznicul_opreste_bucla():
    m = _gata(ModelTrepte)
    sir = torch.randint(len(LITERE), (500,), generator=torch.Generator().manual_seed(1))
    r = m.bucla(sir, 30.0, la_fiecare=lambda s: "prea cald", secunde_intre_semnale=0.0)
    assert r["oprit"] == "prea cald" and r["pasi"] == 1


def test_rata_dupa_ceas():
    m = ModelTrepte(**{**MIC, "rata_invatare": 6e-4, "incalzire_secunde": 180, "racire_secunde": 900})
    assert m.rata_dupa_ceas(0, 3600) == 0.0
    assert m.rata_dupa_ceas(90, 3600) == pytest.approx(3e-4)
    assert m.rata_dupa_ceas(1000, 3600) == pytest.approx(6e-4)
    assert m.rata_dupa_ceas(2700, 3600) == pytest.approx(6e-4)
    assert m.rata_dupa_ceas(3150, 3600) == pytest.approx(3e-4)
    assert m.rata_dupa_ceas(3600, 3600) == 0.0
    assert ModelTrepte(**MIC).rata_dupa_ceas(5, 10) == MIC.get("rata_invatare", 1e-3)


def test_setari_gresite_refuzate():
    with pytest.raises(ValueError):
        ModelTrepte(**{**MIC, "k_bucata": 3})  # 16 nu se împarte la 3
    with pytest.raises(ValueError):
        ModelTrepte(**{**MIC, "rata_care_scade": True})


def test_unealta_cap_coada(tmp_path, monkeypatch):
    from teste.bucati_mici import scrie_bucati
    from unelte import laborator_trepte as lt

    s = scrie_bucati(tmp_path / "date")
    monkeypatch.setattr(lt, "BUCATI", s["director"])
    monkeypatch.setattr(lt, "VALIDARE", s["cale_validare"])
    monkeypatch.setattr(lt, "TOKENIZER", s["cale_tokenizer"])
    iesire = tmp_path / "S135_1"
    cod = lt.main(["--reteta", "1", "--minute", str(2 / 60), "--minute-bucati", str(1 / 60), "--dispozitiv", "cpu",
                   "--straturi", "1", "--capete", "2", "--n-emb", "16", "--context", "32", "--lot", "2", "--adunare", "2",
                   "--incalzire-minute", "0.002", "--racire-minute", "0.005", "--secunde-intre-randuri", "0.5",
                   "--fara-examene", "--iesire", str(iesire)])
    assert cod == 0
    r = json.loads((iesire / "rezultat.json").read_text(encoding="utf-8"))
    assert r["setari_model"]["k_bucata"] == 4 and r["bucla"]["pe_faza"]["bucati"]["pasi"] > 0
    assert r["bucla"]["pe_faza"]["simboluri"]["pasi"] > 0
    assert (iesire / "model.pt").exists()
    randuri = (iesire / "progres.csv").read_text(encoding="utf-8").splitlines()
    assert randuri[0].startswith("minut,") and len(randuri) >= 3
    with pytest.raises(SystemExit):  # nu scrie peste o ieșire existentă
        lt.main(["--reteta", "0", "--dispozitiv", "cpu", "--iesire", str(iesire)])
    # modelul salvat se citește înapoi ca un model obișnuit
    copie = ModelTrepte(**{**MIC, "n_straturi": 1, "context": 32, "tokenizer": "bpe", "cale_tokenizer": s["cale_tokenizer"]})
    copie.incarca(str(iesire / "model.pt"))
    assert copie.biti_pentru("the cat sat on the mat.") > 0
