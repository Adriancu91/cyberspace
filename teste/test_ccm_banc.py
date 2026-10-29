"""S47: bancul CCM (module/calcul/) pe modele mici sintetice scrise direct în KGR1 (fără PyTorch, fără rețea): variantele
corecte sunt acceptate, cele greșite respinse, măsurarea e repetabilă, profilul face același calcul ca referința."""

import numpy as np
import pytest

from module.calcul import banc
from module.calcul.profil import OPERATII, profil
from module.calcul.variante import REFERINTA, VARIANTE
from unelte.exporta_greutati import cuantizeaza_q8, scrie
from unelte.inferenta_bruta import MotorBrut

SETARI = dict(n_straturi=2, n_capete=4, n_emb=32, context=16, vocabular=64)
TEXTE = [[1, 5, 9], [60, 2, 33, 7, 7]]


def _scrie_sintetic(cale, fel, samanta=11):
    r = np.random.default_rng(samanta)
    e, v, c = SETARI["n_emb"], SETARI["vocabular"], SETARI["context"]

    def m(a, b):
        return (r.standard_normal((a, b)) / b ** 0.5).astype(np.float32)

    def vec(n, baza=0.0):
        return (baza + 0.1 * r.standard_normal(n)).astype(np.float32)

    t = {"emb_token.weight": (0.3 * r.standard_normal((v, e))).astype(np.float32),
         "emb_pozitie.weight": (0.5 * r.standard_normal((c, e))).astype(np.float32)}
    for i in range(SETARI["n_straturi"]):
        p = f"straturi.{i}."
        t.update({p + "ln1.weight": vec(e, 1.0), p + "ln1.bias": vec(e),
                  p + "atentie.in_proj_weight": m(3 * e, e), p + "atentie.in_proj_bias": vec(3 * e),
                  p + "atentie.out_proj.weight": m(e, e), p + "atentie.out_proj.bias": vec(e),
                  p + "ln2.weight": vec(e, 1.0), p + "ln2.bias": vec(e),
                  p + "mlp.0.weight": m(4 * e, e), p + "mlp.0.bias": vec(4 * e),
                  p + "mlp.2.weight": m(e, 4 * e), p + "mlp.2.bias": vec(e)})
    t.update({"ln.weight": vec(e, 1.0), "ln.bias": vec(e)})
    if fel == "q8_0":
        t = {k: cuantizeaza_q8(w) if w.ndim == 2 else w for k, w in t.items()}
    chei = {"arhitectura": "kronos_gpt", "fel": fel, "sursa": "test S47", "ln_eps": 1e-5, "cap_legat": 1,
            "tokenizer.bpe": "", **SETARI}
    scrie(cale, chei, t)
    return cale


@pytest.fixture(scope="module")
def fisiere(tmp_path_factory):
    d = tmp_path_factory.mktemp("ccm")
    return [_scrie_sintetic(d / "f32.kgr", "f32"), _scrie_sintetic(d / "q8.kgr", "q8_0")]


class _Stricat(MotorBrut):
    """Greșit: o greutate din MLP cu zgomot mare → alte simboluri (o deplasare egală ar fi ștearsă de LayerNorm)."""

    def __init__(self, cale, zgomot=2.0):
        super().__init__(cale, "la_incarcare")
        w = self.t["straturi.1.mlp.2.weight"]
        r = np.random.default_rng(5)
        self.t["straturi.1.mlp.2.weight"] = (w + zgomot * r.standard_normal(w.shape)).astype(np.float32)


class _Deplasat(MotorBrut):
    """Aceleași simboluri (argmax nu se schimbă la o deplasare egală), dar logit-urile cu 0,01 mai mari."""

    def _cap(self, x):
        return super()._cap(x) + 0.01


class _Neliniștit(MotorBrut):
    """Altă alegere la fiecare încărcare: măsurarea trebuie să refuze."""

    n = 0

    def __init__(self, cale):
        super().__init__(cale, "la_incarcare")
        _Neliniștit.n += 1
        self.t["emb_token.weight"] = self.t["emb_token.weight"] * (1.0 + 0.5 * _Neliniștit.n)
        self.t["ln.bias"] = self.t["ln.bias"] + _Neliniștit.n


def test_variantele_corecte_sunt_acceptate(fisiere):
    assert REFERINTA in VARIANTE and len(VARIANTE) >= 2
    for nume, fabrica in VARIANTE.items():
        v = banc.verifica(fabrica, fisiere, TEXTE, simboluri=8)
        assert v["acceptata"], (nume, v["motive"])
        assert all(c["simboluri_identice"] for c in v["cazuri"]) and len(v["cazuri"]) == 4


def test_varianta_cu_alte_simboluri_e_respinsa(fisiere):
    v = banc.verifica(_Stricat, fisiere, TEXTE, simboluri=8)
    assert not v["acceptata"]
    assert any("alte simboluri" in m for m in v["motive"])


def test_varianta_peste_toleranta_e_respinsa_chiar_cu_aceleasi_simboluri(fisiere):
    v = banc.verifica(_Deplasat, fisiere, TEXTE, simboluri=8)
    assert all(c["simboluri_identice"] for c in v["cazuri"])
    assert not v["acceptata"] and any("Δ logit" in m for m in v["motive"])
    assert banc.verifica(_Deplasat, fisiere, TEXTE, simboluri=8, toleranta=0.02)["acceptata"]


def test_simbolurile_scrise_dinainte_trebuie_sa_se_potriveasca(fisiere):
    ref = MotorBrut(fisiere[0])
    bune = [[int(x) for x in ref.completeaza_simboluri(t, 5)[0]] for t in TEXTE]
    assert banc.verifica(VARIANTE["la_pas"], fisiere[:1], TEXTE, 5, asteptate={"f32.kgr": bune})["acceptata"]
    rele = [[(b[0] + 1) % SETARI["vocabular"]] + b[1:] for b in bune]
    v = banc.verifica(VARIANTE["la_pas"], fisiere[:1], TEXTE, 5, asteptate={"f32.kgr": rele})
    assert not v["acceptata"] and any("vectori.json" in m for m in v["motive"])


def test_masurarea_e_repetabila(fisiere):
    m = banc.masoara(VARIANTE["transpus"], fisiere[1], TEXTE[1], simboluri=8, repetari=5)
    assert m["repetari"] == 5 and len(m["pe_repetare"]) == 5
    for k in ("incarcare", "inceput", "restul", "total"):
        assert m[k]["min"] <= m[k]["median"] <= m[k]["max"] and m[k]["min"] > 0
    for r in m["pe_repetare"]:
        assert r["total"] >= r["incarcare"] + r["inceput"] + r["restul"] - 1e-9
    with pytest.raises(RuntimeError, match="aceleași simboluri"):
        banc.masoara(_Neliniștit, fisiere[0], TEXTE[0], simboluri=8, repetari=3)
    with pytest.raises(ValueError):
        banc.masoara(VARIANTE["referinta"], fisiere[0], TEXTE[0], repetari=0)


@pytest.mark.parametrize("desfacere", ["la_incarcare", "la_pas"])
def test_profilul_face_acelasi_calcul(fisiere, desfacere):
    r = profil(fisiere[1], TEXTE[0], simboluri=20, desfacere=desfacere)  # 3 + 20 > context 16: și ramura fără cache
    assert r["simboluri_noi"] == 20
    assert set(r["ms_pe_operatie"]) == set(OPERATII) | {"restul"}
    assert sum(r["ms_pe_operatie"].values()) == pytest.approx(r["ms_completare"])
    assert (r["ms_pe_operatie"]["desfacere_q8"] > 0) == (desfacere == "la_pas")


def test_incearca_pe_vectorii_kgr1_din_depozit():
    if not banc._asteptate_vectori():
        pytest.skip("lipsesc vectorii KGR1")
    r = banc.incearca("transpus", banc.VECTORI / "mic_q8_0.kgr", simboluri=5, repetari=1)
    assert r["acceptata"], (r["verificare_vectori"]["motive"], r["verificare_model"]["motive"])
    assert all(c["ca_in_vectori"] for c in r["verificare_vectori"]["cazuri"])
    assert r["masurare"]["repetari"] == 1


def test_procesul_nou_cu_un_fir(fisiere):
    r = banc.in_proces_nou("la_pas", "1", fisiere[1], simboluri=4, repetari=1, vectori=False)
    assert r["fire"] == "1" and r["acceptata"] and r["verificare_vectori"] is None
