"""S139 (C-167): `module/model_portar.py` și `unelte/laborator_portar.py` — fără portar pasul e exact S135 (0); cu
capacitate 1 și fără sigmoid stratul e cel obișnuit; masca (nimic de după); gather/scatter de mână; gradientul ajunge la
selector; unealta cap-coadă."""

from __future__ import annotations

import csv
import json

import pytest

torch = pytest.importorskip("torch")

from module.model_portar import ModelPortar, alege_topk, masca_alesi, pune_inapoi, strange  # noqa: E402
from module.model_trepte import ModelTrepte  # noqa: E402

MIC = {"n_straturi": 2, "n_capete": 2, "n_emb": 16, "context": 16, "lot": 3, "dispozitiv": "cpu", "samanta": 7,
       "tokenizer": "litere", "abatere_incorporari": 0.02}
LITERE = list("abcdefghijklmnopqrstuvwxyz ")


def _gata(clasa, **setari):
    m = clasa(**{**MIC, **setari})
    m.vocabular = list(LITERE)
    m._pregateste_reteaua()
    return m


def _fereastra(lot: int, lungime: int, samanta: int = 0) -> torch.Tensor:
    g = torch.Generator().manual_seed(samanta)
    return torch.randint(len(LITERE), (lot, lungime), generator=g)


def test_a_fara_portar_pasul_e_exact_S135_0():
    """portar = nu: aceeași inițializare, aceeași pierdere și aceleași greutăți ca ModelTrepte pe 3 pași (F32, procesor)."""
    zero = _gata(ModelTrepte)
    nou = _gata(ModelPortar)
    assert nou.retea.selectori is None
    for a, b in zip(zero.retea.state_dict().values(), nou.retea.state_dict().values(), strict=True):
        assert torch.equal(a, b)
    for i in range(3):
        f = _fereastra(3, 17, samanta=i)
        assert nou.pas_optimizator([f], "simboluri")["pierdere"] == zero.pas_optimizator([f], "simboluri")["pierdere"]
    for a, b in zip(zero.retea.parameters(), nou.retea.parameters(), strict=True):
        assert torch.equal(a, b)


def test_a_cu_portar_partea_comuna_porneste_la_fel():
    """Selectorii se fac după rest: la aceeași sămânță, toate greutățile comune sunt cele ale lui (0)."""
    zero = _gata(ModelTrepte)
    nou = _gata(ModelPortar, portar=True, straturi_portar=[2])
    stare_noua = nou.retea.state_dict()
    for nume, v in zero.retea.state_dict().items():
        assert torch.equal(v, stare_noua[nume])
    assert set(stare_noua) - set(zero.retea.state_dict()) == {"selectori.2.weight", "selectori.2.bias"}


@pytest.mark.parametrize("mod", ["topk", "cauzal"])
def test_b_capacitate_1_fara_sigmoid_e_stratul_obisnuit(mod):
    m = _gata(ModelPortar, portar=True, capacitate=1.0, straturi_portar=[1, 2])
    r = m.retea
    r.cu_sigmoid = False
    with torch.no_grad():
        for s in r.selectori.values():
            s.bias.fill_(50.0)  # în modul cauzal: toți aleși (sigmoid > 0,5)
    x = torch.randn(3, 16, 16, generator=torch.Generator().manual_seed(1))
    if mod == "topk":
        r.train()
    else:
        r.eval()
    for i, strat in enumerate(r.straturi, start=1):
        asteptat = strat(x)
        obtinut = r._strat_portar(strat, r.selectori[str(i)], x)
        assert torch.allclose(obtinut, asteptat, atol=1e-5)
    # rețeaua întreagă: aceleași ieșiri ca fără selectori
    idx = _fereastra(2, 16, samanta=4)
    cu = r(idx)
    selectori, r.selectori = r.selectori, None
    fara = r(idx)
    r.selectori = selectori
    assert torch.allclose(cu, fara, atol=1e-5)


def test_c_masca_la_antrenare_nimic_de_dupa():
    """Pozițiile alese 1, 3, 5 din 8: schimbi x după 5 → nimic nu se schimbă; schimbi x la 4 → doar 5 se schimbă."""
    m = _gata(ModelPortar, portar=True, straturi_portar=[1])
    r = m.retea
    strat = r.straturi[0]
    x = torch.randn(1, 8, 16, generator=torch.Generator().manual_seed(2))
    pozitii = torch.tensor([[1, 3, 5]])

    def delta(xx):
        with torch.no_grad():
            return r.delta_alesi(strat, xx, strat.ln1(xx), pozitii)

    baza = delta(x)
    zgomot = torch.randn(1, 8, 16, generator=torch.Generator().manual_seed(3))  # nu o constantă: LayerNorm o șterge
    dupa = x.clone()
    dupa[:, 6:] += zgomot[:, 6:]
    assert torch.allclose(delta(dupa), baza, atol=1e-6)
    la_4 = x.clone()
    la_4[:, 4] += zgomot[:, 4]
    d4 = delta(la_4)
    assert torch.allclose(d4[:, :2], baza[:, :2], atol=1e-6) and not torch.allclose(d4[:, 2], baza[:, 2], atol=1e-4)
    # K/V vin de la TOATE simbolurile (și cele nealese): schimbi poziția 0 (nealeasă) → se schimbă toți cei aleși
    la_0 = x.clone()
    la_0[:, 0] += zgomot[:, 0]
    d0 = delta(la_0)
    assert all(not torch.allclose(d0[:, i], baza[:, i], atol=1e-4) for i in range(3))


def test_c_masca_modul_cauzal_toata_reteaua():
    """În modul cauzal (examen, scris), ieșirea la poziția p nu depinde de simbolurile de după p."""
    m = _gata(ModelPortar, portar=True, straturi_portar=[1, 2])
    r = m.retea.eval()
    with torch.no_grad():
        for s in r.selectori.values():
            s.weight.normal_(0.0, 1.0)  # alegere amestecată (nu toți / niciunul)
        idx = _fereastra(1, 16, samanta=5)
        baza = r(idx)
        alt = idx.clone()
        alt[:, 9:] = (alt[:, 9:] + 7) % len(LITERE)
        schimbat = r(alt)
    assert torch.allclose(schimbat[:, :9], baza[:, :9], atol=1e-6)
    assert not torch.allclose(schimbat[:, 9:], baza[:, 9:], atol=1e-4)
    st = r.citeste_statistici()
    assert 0.0 < st["parte_aleasa_cauzal"] < 1.0


def test_d_gather_scatter_topk_de_mana():
    r = torch.tensor([[0.1, 0.9, 0.3, 0.8, 0.0], [5.0, -1.0, 4.0, 3.0, 2.0]])
    pozitii = alege_topk(r, 2)
    assert pozitii.tolist() == [[1, 3], [0, 2]]  # în ordinea poziției, nu a scorului
    x = torch.arange(2 * 5 * 2, dtype=torch.float32).view(2, 5, 2)
    alesi = strange(x, pozitii)
    assert alesi.tolist() == [[[2.0, 3.0], [6.0, 7.0]], [[10.0, 11.0], [14.0, 15.0]]]
    y = pune_inapoi(x, pozitii, -alesi)
    asteptat = x.clone()
    asteptat[0, 1], asteptat[0, 3] = -x[0, 1], -x[0, 3]
    asteptat[1, 0], asteptat[1, 2] = -x[1, 0], -x[1, 2]
    assert torch.equal(y, asteptat)  # cei nealeși rămân neschimbați
    assert masca_alesi(torch.tensor([[1, 3]]), 5).tolist() == [[[False, False, True, True, True],
                                                                 [False, False, False, False, True]]]


def test_e_gradientul_ajunge_la_selector():
    m = _gata(ModelPortar, portar=True, straturi_portar=[1, 2])
    r = m.retea.double().train()
    f = _fereastra(2, 17, samanta=6)

    def pierdere():
        r.pierderi_bce = []
        logits = r(f[:, :16])
        ce = torch.nn.functional.cross_entropy(logits.reshape(-1, logits.size(-1)), f[:, 1:].reshape(-1))
        return ce + m.pondere_bce * torch.stack(r.pierderi_bce).mean()

    r.zero_grad()
    pierdere().backward()
    h = 1e-6
    alese = [(r.selectori["1"].weight, (0, 3)), (r.selectori["1"].bias, (0,)), (r.selectori["2"].weight, (0, 11)),
             (r.selectori["2"].weight, (0, 0)), (r.selectori["2"].bias, (0,))]
    for parametru, loc in alese:
        analitic = parametru.grad[loc].item()
        assert analitic != 0.0
        with torch.no_grad():
            vechi = parametru[loc].item()
            parametru[loc] = vechi + h
            sus = pierdere().item()
            parametru[loc] = vechi - h
            jos = pierdere().item()
            parametru[loc] = vechi
        assert analitic == pytest.approx((sus - jos) / (2 * h), rel=1e-4, abs=1e-9)


def test_pasul_cu_portar_raporteaza_bce_si_statistici():
    m = _gata(ModelPortar, portar=True, straturi_portar=[2])
    m.retea.goleste_statistici()
    r = m.pas_optimizator([_fereastra(3, 17, 1), _fereastra(3, 17, 2)], "simboluri")
    assert r["bce"] > 0 and m.bce_recente == [r["bce"]]
    st = m.retea.citeste_statistici()
    assert st["simboluri"] == 2 * 3 * 16 and st["parte_trecuta"] == 0.5
    assert 0.0 <= st["parte_aleasa_cauzal"] <= 1.0 and 0.0 <= st["potrivire_topk"] <= 1.0


def test_setari_gresite_refuzate():
    with pytest.raises(ValueError):
        ModelPortar(**{**MIC, "portar": True, "straturi_portar": [3]})  # doar 2 straturi
    with pytest.raises(ValueError):
        ModelPortar(**{**MIC, "portar": True, "capacitate": 0.0})
    with pytest.raises(ValueError):
        ModelPortar(**{**MIC, "k_bucata": 2})


def test_f_unealta_cap_coada(tmp_path, monkeypatch):
    from teste.bucati_mici import scrie_bucati
    from unelte import laborator_portar as lp
    from unelte import laborator_trepte as lt

    s = scrie_bucati(tmp_path / "date")
    monkeypatch.setattr(lt, "BUCATI", s["director"])
    monkeypatch.setattr(lt, "VALIDARE", s["cale_validare"])
    monkeypatch.setattr(lt, "TOKENIZER", s["cale_tokenizer"])
    iesire = tmp_path / "S139_P"
    cod = lp.main(["--minute", str(6 / 60), "--dispozitiv", "cpu", "--straturi", "2", "--capete", "2", "--n-emb", "64",
                   "--context", "32", "--lot", "4", "--adunare", "1", "--incalzire-minute", "0.01",
                   "--racire-minute", "0.025", "--secunde-intre-randuri", "1", "--rata", "3e-3", "--fara-examene",
                   "--iesire", str(iesire)])
    assert cod == 0
    r = json.loads((iesire / "rezultat.json").read_text(encoding="utf-8"))
    assert r["setari_model"]["portar"] is True and r["setari_model"]["straturi_portar"] == [2]
    assert r["parametri_selectori"] == 65 and r["bucla"]["pasi"] > 0
    with (iesire / "progres.csv").open(encoding="utf-8", newline="") as f:
        randuri = list(csv.DictReader(f))
    assert len(randuri) >= 3 and float(randuri[-1]["eroare"]) < float(randuri[0]["eroare"])  # eroarea scade
    assert all(x["bce"] != "" and x["parte_aleasa_cauzal"] != "" and float(x["simboluri_pe_s"]) > 0 for x in randuri)
    with pytest.raises(SystemExit):  # nu scrie peste o ieșire existentă
        lp.main(["--dispozitiv", "cpu", "--iesire", str(iesire)])
    # modelul salvat se citește înapoi, cu portarul, și scrie/examinează în modul cauzal
    copie = ModelPortar(**{**MIC, "tokenizer": "bpe", "cale_tokenizer": s["cale_tokenizer"]})
    copie.incarca(str(iesire / "model.pt"))
    assert copie.portar and copie.retea.selectori is not None
    assert copie.biti_pentru("the cat sat on the mat.") > 0
    assert copie.retea.citeste_statistici()["parte_aleasa_cauzal"] is not None


def test_f_examenele_portar_pe_model_mic(tmp_path, monkeypatch):
    """`examene_portar`: examenele (0) în modul cauzal + partea aleasă la română + top-k informativ (date mici)."""
    from unelte import laborator_portar as lp

    from module.model_gpt import NECUNOSCUT

    m = ModelPortar(**{**MIC, "portar": True, "straturi_portar": [1, 2]})
    m.vocabular = LITERE + [NECUNOSCUT]
    m._pregateste_reteaua()
    chemari = []

    def examene_false(model, date, cu_r1):
        chemari.append(model.retea.mod_examen)
        model.biti_pentru("abc def")
        return {"romana": {"romana_bpb": 1.0}, "examen_bpb": {"val_bpb": 0.5}}

    class Romana:
        def __init__(self, **k):
            pass

        def examineaza(self, model, date):
            model.biti_pentru("abc def ghi")
            return {"romana_bpb": 1.0}

    class Bpb:
        def examineaza(self, model, date):
            return {"val_bpb": 0.5}

    import module.examen_bpb as eb
    import module.examen_romana as er

    monkeypatch.setattr(lp.lt, "examene", examene_false)
    monkeypatch.setattr(er, "ExamenRomana", Romana)
    monkeypatch.setattr(eb, "ExamenBpb", Bpb)
    r = lp.examene_portar(m, None, cu_r1=False)
    assert chemari == ["cauzal"] and m.retea.mod_examen == "cauzal"
    assert r["romana_cauzal_parte_aleasa"]["simboluri"] > 0
    assert r["informativ_topk"]["statistici"]["parte_trecuta"] == pytest.approx(0.5, abs=0.1)
    assert r["validitate_parte_aleasa"]["valida"] in (True, False)
