"""S137: `module/date_harta.py` și `unelte/laborator_harta.py` — cu harta oprită ferestrele sunt exact ale rețetei (0),
pierderea pe fereastră, probabilitățile (tăierea 0,25×/4×, jumătate uniform) calculate de mână, regiunile nevăzute,
unealta cap-coadă."""

from __future__ import annotations

import json

import numpy as np
import pytest

torch = pytest.importorskip("torch")

from module.date_harta import HartaFerestre, probabilitati_regiuni, scoruri  # noqa: E402
from module.model_trepte import ModelTrepte  # noqa: E402
from unelte.laborator_harta import ModelHarta, ferestre_ref  # noqa: E402

MIC = {"n_straturi": 2, "n_capete": 2, "n_emb": 16, "context": 16, "lot": 3, "dispozitiv": "cpu", "samanta": 7,
       "tokenizer": "litere", "adunare_loturi": 2, "rata_invatare": 1e-3}
LITERE = list("abcdefghijklmnopqrstuvwxyz ")


def _gata(clasa, **setari):
    m = clasa(**{**MIC, **setari})
    m.vocabular = list(LITERE)
    m._pregateste_reteaua()
    return m


def _sir(n: int = 3000, samanta: int = 9) -> torch.Tensor:
    return torch.randint(len(LITERE), (n,), generator=torch.Generator().manual_seed(samanta))


def test_a_harta_oprita_trage_exact_ferestrele_retetei_0():
    """Primii 20 de pași: aceleași locuri ca `torch.randint(len − context − 1)` din bucla (0), în aceeași ordine, și
    aceleași greutăți la final ca ModelTrepte.bucla (deci și aceleași ferestre)."""
    sir = _sir()
    zero = _gata(ModelTrepte, pasi_max=20)
    r0 = zero.bucla(sir, 600.0, samanta_loturi=1163)
    for cu_harta, ref in ((False, None), (True, np.ones(-(-len(sir) // 256))), (True, None)):
        h = _gata(ModelHarta, pasi_max=20)
        harta = HartaFerestre(len(sir), 16, marime_regiune=256, ref=ref)
        # cu harta pornită dar „uniform” mai lung decât proba: tot ferestrele lui (0)
        rh = h.bucla_harta(sir, harta, 600.0, secunde_uniform=10_000.0, samanta_loturi=1163, cu_harta=cu_harta)
        assert rh["pasi"] == r0["pasi"] == 20 and rh["pasi_cu_harta"] == 0
        g = torch.Generator().manual_seed(1163)
        asteptat = torch.cat([torch.randint(len(sir) - 16 - 1, (3,), generator=g) for _ in range(20 * 2)])
        assert torch.equal(torch.cat(h.pozitii_trase), asteptat)
        for a, b in zip(zero.retea.parameters(), h.retea.parameters()):
            assert torch.allclose(a, b, atol=1e-5)
        assert rh["pierdere_finala"] == pytest.approx(r0["pierdere_finala"], rel=1e-5)
        assert harta.trase.sum() == 20 * 2 * 3


def test_b_media_pierderilor_pe_fereastra_e_pierderea_lotului():
    m = _gata(ModelHarta)
    azi = _gata(ModelTrepte)
    f = _sir(5 * 17, 3).view(5, 17)
    m.pierderi_ferestre = []
    lot = m.pierdere_simboluri(f[:, :16], f[:, 1:])
    pe_fereastra = m.pierderi_ferestre[0]
    assert pe_fereastra.shape == (5,)
    assert pe_fereastra.mean().item() == pytest.approx(lot.item(), rel=1e-6)
    assert lot.item() == pytest.approx(azi.pierdere_simboluri(f[:, :16], f[:, 1:]).item(), rel=1e-6)
    # fiecare fereastră singură dă aceeași pierdere ca în lot
    for i in range(5):
        singura = azi.pierdere_simboluri(f[i : i + 1, :16], f[i : i + 1, 1:]).item()
        assert pe_fereastra[i].item() == pytest.approx(singura, rel=1e-5)


def test_c_probabilitatile_de_mana():
    u = np.full(4, 0.25)
    # fără tăiere: q = 0,5 · u + 0,5 · s/Σs
    assert np.allclose(probabilitati_regiuni(u, np.array([1.0, 1.0, 0.0, 0.0])), [0.375, 0.375, 0.125, 0.125])
    # tăierea de sus (4×): u = (0,1; 0,3; 0,3; 0,3), s = (1, 0, 0, 0) → q = (0,55; 0,15; 0,15; 0,15); 0,55 > 0,4 →
    # 0,4, iar restul de 0,6 se împarte proporțional pe celelalte → 0,2 fiecare
    q = probabilitati_regiuni(np.array([0.1, 0.3, 0.3, 0.3]), np.array([1.0, 0.0, 0.0, 0.0]))
    assert np.allclose(q, [0.4, 0.2, 0.2, 0.2])
    # tăierea de jos (0,25×), vizibilă doar fără partea uniformă: s = (1, 1, 1, 0) → (1/3, 1/3, 1/3, 0); 0 < 0,0625 →
    # 0,0625, iar 0,9375 rămâne pentru primele trei → 0,3125
    q = probabilitati_regiuni(u, np.array([1.0, 1.0, 1.0, 0.0]), parte_uniforma=0.0)
    assert np.allclose(q, [0.3125, 0.3125, 0.3125, 0.0625])
    # toate scorurile 0 → uniform
    assert np.allclose(probabilitati_regiuni(u, np.zeros(4)), u)
    # cu jumătate uniform, nicio regiune nu coboară sub 0,5 · u și nu urcă peste 4 · u
    rng = np.random.default_rng(0)
    u = rng.random(50)
    u /= u.sum()
    q = probabilitati_regiuni(u, rng.random(50) ** 8)
    assert q.sum() == pytest.approx(1.0) and np.all(q >= 0.5 * u - 1e-12) and np.all(q <= 4 * u + 1e-12)


def test_d_regiunile_nevazute_primesc_media():
    s = scoruri(np.array([3.0, 0.0, 5.0, 0.0]), np.array([1.0, 9.0, 6.0, 0.0]), np.array([True, False, True, False]))
    assert np.allclose(s, [2.0, 1.0, 0.0, 1.0])  # (2 + 0) / 2 = 1 pentru cele nevăzute; max(5 − 6, 0) = 0
    assert np.allclose(scoruri(np.zeros(3), np.zeros(3), np.zeros(3, bool)), 0.0)


def test_harta_regiunile_ema_tragerea_si_sferturile():
    h = HartaFerestre(1000, 16, marime_regiune=300, ref=np.array([1.0, 2.0, 0.5, 3.0]))
    assert h.regiuni == 4 and h.starturi == 983
    assert list(h.valide) == [300, 300, 300, 83]  # ultima: doar locurile de start ale lui (0)
    h.actualizeaza([10, 20, 310], [4.0, 2.0, 5.0])
    assert h.p_acum[0] == pytest.approx(4.0 + 0.05 * (2.0 - 4.0)) and h.p_acum[1] == 5.0
    assert list(h.vazut) == [True, True, False, False]
    h.actualizeaza([0], [float("nan")])  # pierderile care nu sunt numere nu intră
    assert h.p_acum[0] == pytest.approx(3.9)
    h.recalculeaza()
    g = torch.Generator().manual_seed(3)
    p = h.trage(2000, g, uniform=False).numpy()
    assert p.min() >= 0 and p.max() < h.starturi
    parti = np.bincount(p // 300, minlength=4) / 2000
    assert np.allclose(parti, h._q, atol=0.04)
    assert list(h.sferturi()) == [1, 2, 0, 3]
    assert sum(h.trase_pe_sferturi()) == 2000


def test_ferestrele_de_referinta():
    h = HartaFerestre(5000, 16, marime_regiune=1024)
    a, b = ferestre_ref(h, 1163), ferestre_ref(h, 1163)
    assert a.shape == (5, 2) and np.array_equal(a, b)
    for r in range(5):
        assert np.all(a[r] >= h.inceputuri[r]) and np.all(a[r] < h.inceputuri[r] + h.valide[r])


def _scrie_ref(cale, date, context: int, ref=None) -> None:
    ref = np.linspace(1.0, 3.0, date.numar_regiuni()) if ref is None else ref
    np.save(cale, ref)
    cale.with_suffix(".json").write_text(json.dumps({"date": {"sha256_tot": date.index["sha256_tot"]},
                                                     "marime_regiune": date.marime_regiune, "context": context}),
                                         encoding="utf-8")


def test_e_unealta_cap_coada(tmp_path, monkeypatch):
    """Cap-coadă pe un model mic, procesor, cu timpii probei scalați (2 min, încălzire 0,2, răcire 0,5, uniform 0,5)
    împărțiți la 60, ca testul să ia câteva secunde; refuză să scrie peste o ieșire existentă."""
    from module.date_harta import DateHarta
    from teste.bucati_mici import scrie_bucati
    from unelte import laborator_harta as lh
    from unelte import laborator_trepte as lt

    s = scrie_bucati(tmp_path / "date")
    monkeypatch.setattr(lt, "BUCATI", s["director"])
    monkeypatch.setattr(lt, "VALIDARE", s["cale_validare"])
    monkeypatch.setattr(lt, "TOKENIZER", s["cale_tokenizer"])
    date = DateHarta(s["director"], s["cale_validare"], s["cale_tokenizer"], marime_regiune=128)
    cale_ref = tmp_path / "harta_ref.npy"
    _scrie_ref(cale_ref, date, 32)
    iesire = tmp_path / "S137_H"
    argumente = ["--minute", str(2 / 60), "--minute-uniform", str(0.5 / 60), "--incalzire-minute", str(0.2 / 60),
                 "--racire-minute", str(0.5 / 60), "--dispozitiv", "cpu", "--straturi", "1", "--capete", "2",
                 "--n-emb", "16", "--context", "32", "--lot", "2", "--adunare", "2", "--secunde-intre-randuri", "0.5",
                 "--marime-regiune", "128", "--cale-ref", str(cale_ref), "--fara-examene"]
    assert lh.main(argumente + ["--iesire", str(iesire)]) == 0
    r = json.loads((iesire / "rezultat.json").read_text(encoding="utf-8"))
    assert r["setari_model"]["k_bucata"] == 1 and r["setari_model"]["minute_bucati"] == 0.0
    assert r["bucla"]["pasi"] > r["bucla"]["pasi_cu_harta"] > 0
    assert sum(r["harta"]["trase_pe_sferturi"]) == r["bucla"]["pasi"] * 2 * 2
    assert (iesire / "model.pt").exists()
    final = json.loads((iesire / "harta_final.json").read_text(encoding="utf-8"))
    assert final["regiuni"] == date.numar_regiuni() and sum(final["trase"]) == r["bucla"]["pasi"] * 4
    randuri = (iesire / "progres.csv").read_text(encoding="utf-8").splitlines()
    assert randuri[0].startswith("minut,") and "sfert_4_greu" in randuri[0] and len(randuri) >= 3
    assert any(",harta," in x for x in randuri[1:]) and any(",uniform," in x for x in randuri[1:])
    with pytest.raises(SystemExit):  # nu scrie peste o ieșire existentă
        lh.main(argumente + ["--iesire", str(iesire)])
    # o hartă de referință făcută pentru alt context e refuzată
    _scrie_ref(cale_ref, date, 64)
    with pytest.raises(SystemExit):
        lh.main(argumente + ["--iesire", str(tmp_path / "alta")])
