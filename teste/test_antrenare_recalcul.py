"""S77b: recalculul activărilor din afara module/ (unelte/antrenare_recalcul.py), pe procesor."""

import copy

import torch

from unelte import antrenare_recalcul as ar

MIC = dict(n_straturi=3, n_capete=2, n_emb=16, context=8, dropout=0.0)
VOCAB = 40


def _retea(samanta=3):
    from module.model_gpt import _GPT

    torch.manual_seed(samanta)
    return _GPT(VOCAB, **MIC)


def _pierdere_si_gradiente(retea, x, y):
    retea.zero_grad(set_to_none=True)
    logits = retea(x)
    loss = torch.nn.functional.cross_entropy(logits.reshape(-1, VOCAB), y.reshape(-1))
    loss.backward()
    return loss.item(), {n: p.grad.detach().clone() for n, p in retea.named_parameters() if p.grad is not None}


def _lot(samanta=0):
    g = torch.Generator().manual_seed(samanta)
    return torch.randint(VOCAB, (4, 8), generator=g), torch.randint(VOCAB, (4, 8), generator=g)


def test_aceeasi_pierdere_si_aceleasi_gradiente():
    simpla, cu_recalcul = _retea(), _retea()
    cu_recalcul.load_state_dict(simpla.state_dict())
    assert ar.impacheteaza(cu_recalcul) == MIC["n_straturi"]
    simpla.train(), cu_recalcul.train()
    x, y = _lot()
    p1, g1 = _pierdere_si_gradiente(simpla, x, y)
    p2, g2 = _pierdere_si_gradiente(cu_recalcul, x, y)
    assert abs(p1 - p2) <= 1e-5
    assert g1.keys() == g2.keys() and len(g1) > 0
    assert max(float((g1[k] - g2[k]).abs().max()) for k in g1) <= 1e-5


def test_straturile_sunt_impachetate_si_trec_prin_checkpoint(monkeypatch):
    retea = _retea()
    ar.impacheteaza(retea)
    assert all(ar.e_impachetat(s) for s in retea.straturi)
    chemari = []
    import torch.utils.checkpoint as cp

    adevarat = cp.checkpoint

    def numara(*a, **k):
        chemari.append(k.get("use_reentrant"))
        return adevarat(*a, **k)

    monkeypatch.setattr(cp, "checkpoint", numara)
    retea.train()
    x, y = _lot()
    _pierdere_si_gradiente(retea, x, y)
    assert chemari == [False] * MIC["n_straturi"]
    chemari.clear()
    with torch.no_grad():  # la examen: fără checkpoint
        retea.eval()
        retea(x)
    assert chemari == []


def test_state_dict_neschimbat_si_copia_ramane_impachetata():
    simpla, cu_recalcul = _retea(), _retea()
    ar.impacheteaza(cu_recalcul)
    assert list(simpla.state_dict()) == list(cu_recalcul.state_dict())
    copia = copy.deepcopy(cu_recalcul)
    for s_copie, s_orig in zip(copia.straturi, cu_recalcul.straturi):
        assert ar.e_impachetat(s_copie)
        assert s_copie.forward.__self__ is s_copie and s_copie.forward.__self__ is not s_orig
    assert ar.impacheteaza(cu_recalcul) == MIC["n_straturi"]  # a doua oară: nimic nou


def test_instaleaza_pe_clasa_si_dezinstaleaza():
    class Baza:
        def _pregateste_reteaua(self):
            self.retea = _retea()

    class Model(Baza):
        pass

    ar.instaleaza(Model)
    ar.instaleaza(Model)  # a doua chemare nu împachetează de două ori
    m = Model()
    m._pregateste_reteaua()
    assert all(ar.e_impachetat(s) for s in m.retea.straturi)
    b = Baza()
    b._pregateste_reteaua()
    assert not any(ar.e_impachetat(s) for s in b.retea.straturi)  # doar clasa aleasă
    ar.dezinstaleaza(Model)
    assert "_pregateste_reteaua" not in Model.__dict__
    m2 = Model()
    m2._pregateste_reteaua()
    assert not any(ar.e_impachetat(s) for s in m2.retea.straturi)


def test_clasa_adevarata_se_reface_dupa_dezinstalare():
    from module.model_muon import ModelGPTConversatieMuon as M

    inainte = M.__dict__["_pregateste_reteaua"]
    ar.instaleaza(M)
    try:
        assert getattr(M.__dict__["_pregateste_reteaua"], "_cu_recalcul", False)
    finally:
        ar.dezinstaleaza(M)
    assert M.__dict__["_pregateste_reteaua"] is inainte


def test_main_trimite_restul_argumentelor_la_antrenare_lunga(monkeypatch):
    from module.model_muon import ModelGPTConversatieMuon as M
    from unelte import antrenare_lunga

    primite = {}

    def fals(argv):
        primite["argv"] = argv
        primite["instalat"] = getattr(M._pregateste_reteaua, "_cu_recalcul", False)
        return 0

    monkeypatch.setattr(antrenare_lunga, "main", fals)
    try:
        assert ar.main(["--memorie-max-mb", "0", "--config", "x.toml", "--ore", "5"]) == 0
    finally:
        ar.dezinstaleaza(M)
    assert primite == {"argv": ["--config", "x.toml", "--ore", "5"], "instalat": True}
