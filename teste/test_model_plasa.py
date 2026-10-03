"""Plasa de noduri: fiecare simbol merge la nodul potrivit, fără viitor; la început e identică cu GPT-ul."""

from __future__ import annotations

import copy
import math

import pytest

torch = pytest.importorskip("torch")

from module.date_mostra import DateMostra  # noqa: E402
from module.memorie_ierarhica import MemorieIerarhica  # noqa: E402
from module.model_gpt import ModelGPT  # noqa: E402
from module.model_plasa import (  # noqa: E402
    NUME_NODURI, PRAG_ASOCIERE, REZERVA, TARIE_NASTERE, ModelPlasa, Plasa, nod_pentru_raft,
)
from module.tokenizer_bpe import antreneaza_bpe  # noqa: E402
from teste.biblioteca_mica import biblioteca_mica  # noqa: E402

MIC = dict(n_straturi=1, n_capete=2, n_emb=32, context=32, lot=8, dispozitiv="cpu", n_ascuns_nod=16)


@pytest.fixture
def tokenizer_mic(tmp_path):
    cale = tmp_path / "bpe_mic.json"
    antreneaza_bpe(DateMostra(propozitii=600).text_antrenare(), 320).salveaza(cale)
    return str(cale)


@pytest.fixture
def memorie(tmp_path):
    return MemorieIerarhica(cale=biblioteca_mica(tmp_path), nivele=6)


def _nod(nume: str) -> int:
    return NUME_NODURI.index(nume)


def test_rafturile_merg_la_grupurile_cerute():
    assert nod_pentru_raft("noun.animal") == _nod("fiinte") == nod_pentru_raft("noun.person")
    assert nod_pentru_raft("noun.artifact") == _nod("locuri_obiecte") == nod_pentru_raft("noun.location")
    assert nod_pentru_raft("verb.motion") == _nod("actiuni") == nod_pentru_raft("verb.emotion")
    assert nod_pentru_raft("adj.all") == _nod("insusiri") == nod_pentru_raft("adv.all")
    assert nod_pentru_raft("noun.group") == REZERVA  # rafturile nepuse în alt grup


def test_fiecare_cuvant_merge_la_nodul_raftului_lui(memorie, tokenizer_mic):
    model = ModelPlasa(**MIC, cale_tokenizer=tokenizer_mic)
    model.conecteaza_memorie(memorie)
    asteptat = {
        "horse": "fiinte", "cat": "fiinte", "sword": "locuri_obiecte", "gallop": "actiuni", "ran": "actiuni",
        "good": "insusiri", "bad": "insusiri", "o'clock": "insusiri", "herd": "rezerva", "thee": "rezerva",
    }
    for cuvant, nod in asteptat.items():
        assert model._nod(memorie.cod(cuvant)) == _nod(nod), cuvant


def test_drumul_simbolurilor_nu_vede_viitorul(memorie, tokenizer_mic):
    model = ModelPlasa(**MIC, cale_tokenizer=tokenizer_mic, pasi_max=1)
    model.conecteaza_memorie(memorie)
    model.antreneaza(DateMostra(propozitii=200), 30.0)
    simboluri = model.tok.codifica("the horse ran to the good cat. A sword! “the” herd")
    toate = model._pozitii("", simboluri)
    assert toate.shape == (len(simboluri), 1)
    for t in range(1, len(simboluri) + 1):
        assert torch.equal(model._pozitii("", simboluri[:t]), toate[:t]), f"scurgere din viitor la simbolul {t}"


def test_la_inceput_e_identic_cu_gpt_ul(memorie, tokenizer_mic):
    """Nodurile pornesc tăcute: neantrenată, plasa dă exact ce dă GPT-ul simplu, cu aceeași sămânță."""
    date = DateMostra(propozitii=300)
    setari = {k: v for k, v in MIC.items() if k != "n_ascuns_nod"}
    gpt = ModelGPT(**setari, tokenizer="bpe", cale_tokenizer=tokenizer_mic)
    plasa = ModelPlasa(**MIC, cale_tokenizer=tokenizer_mic)
    plasa.conecteaza_memorie(memorie)
    assert gpt.antreneaza(date, 0.0)["pasi"] == 0 and plasa.antreneaza(date, 0.0)["pasi"] == 0
    text = "the cat ran to the horse. a good sword."
    assert plasa.biti_pentru(text) == pytest.approx(gpt.biti_pentru(text), rel=1e-6)


def test_invata_si_se_reincarca(tmp_path, memorie, tokenizer_mic):
    model = ModelPlasa(**MIC, cale_tokenizer=tokenizer_mic)
    model.conecteaza_memorie(memorie)
    statistici = model.antreneaza(DateMostra(propozitii=300), 1.5)
    assert statistici["pasi"] > 0
    assert set(statistici["noduri"]) == set(NUME_NODURI) and sum(statistici["noduri"].values()) == pytest.approx(1)
    assert statistici["noduri"]["fiinte"] > 0 and statistici["noduri"]["actiuni"] > 0  # „cat”, „ran” din propoziții
    text = "the cat sat on the mat."
    biti = model.biti_pentru(text)
    assert math.isfinite(biti)
    assert len(model.genereaza("the cat ", 20)) == 20

    copie = ModelPlasa(dispozitiv="cpu", cale_tokenizer=tokenizer_mic)
    copie.conecteaza_memorie(memorie)
    copie.incarca(model.salveaza(str(tmp_path / "model")))
    assert copie.n_ascuns_nod == 16
    assert copie.biti_pentru(text) == pytest.approx(biti, rel=1e-5)


def test_fara_memorie_totul_merge_la_rezerva(tokenizer_mic):
    model = ModelPlasa(**MIC, cale_tokenizer=tokenizer_mic)
    statistici = model.antreneaza(DateMostra(propozitii=200), 0.5)
    assert statistici["noduri"]["rezerva"] == 1.0
    assert math.isfinite(model.biti_pentru("the cat."))


# --- regulile plasei -------------------------------------------------------------------------

LEGATURA = ("fiinte", "actiuni")


def _matrice(valori: dict[tuple[str, str], float]) -> list[list[float]]:
    m = [[0.0] * len(NUME_NODURI) for _ in NUME_NODURI]
    for (a, b), v in valori.items():
        m[NUME_NODURI.index(a)][NUME_NODURI.index(b)] = v
    return m


NIMIC = _matrice({})
FOLOSITA = _matrice({LEGATURA: 0.1})  # legătura a fost folosită din plin


def _plasa_cu(tarie: float, stare: str = "activa") -> Plasa:
    return Plasa(NUME_NODURI, {LEGATURA: {"tarie": tarie, "stare": stare, "nascuta_la": 1, "sub_prag": 0}})


ASOCIATE = _matrice(
    {LEGATURA: PRAG_ASOCIERE + 0.1, ("actiuni", "fiinte"): PRAG_ASOCIERE + 0.1, ("fiinte", "insusiri"): PRAG_ASOCIERE - 0.1}
)


def test_se_naste_doar_cu_cerere_si_asociere_peste_prag():
    plasa = Plasa(NUME_NODURI)
    cereri = _matrice({LEGATURA: 0.06, ("actiuni", "fiinte"): 0.04, ("fiinte", "insusiri"): 0.3})
    assert plasa.actualizeaza(cereri, NIMIC, castig=None, asociere=ASOCIATE)["nascute"] == 1
    assert plasa.legaturi[LEGATURA]["stare"] == "proba"
    assert plasa.legaturi[LEGATURA]["tarie"] == pytest.approx(TARIE_NASTERE * 0.99)
    assert ("actiuni", "fiinte") not in plasa.legaturi  # asociere destulă, dar cererea (0,04) e sub prag
    assert ("fiinte", "insusiri") not in plasa.legaturi  # cerere mare, dar asocierea e sub prag


def test_fara_asociere_masurata_nu_se_naste_nimic():
    plasa = Plasa(NUME_NODURI)
    assert plasa.actualizeaza(_matrice({LEGATURA: 0.5}), NIMIC, castig=None, asociere=None)["nascute"] == 0


def test_uitarea_e_1_la_suta_pe_experiment():
    plasa = _plasa_cu(0.5)
    plasa.actualizeaza(NIMIC, NIMIC, castig=None)
    assert plasa.legaturi[LEGATURA]["tarie"] == pytest.approx(0.495)


def test_intarirea_cere_si_castig_la_examen_si_folosire():
    cu_amandoua = _plasa_cu(0.5)
    assert cu_amandoua.actualizeaza(NIMIC, FOLOSITA, castig=0.02)["intarite"] == 1
    assert cu_amandoua.legaturi[LEGATURA]["tarie"] == pytest.approx(0.7 * 0.99)
    doar_folosita = _plasa_cu(0.5)
    doar_folosita.actualizeaza(NIMIC, FOLOSITA, castig=None)  # folosirea singură nu ajunge
    assert doar_folosita.legaturi[LEGATURA]["tarie"] == pytest.approx(0.495)
    doar_castig = _plasa_cu(0.5)
    doar_castig.actualizeaza(NIMIC, NIMIC, castig=0.02)  # nici câștigul fără folosire
    assert doar_castig.legaturi[LEGATURA]["tarie"] == pytest.approx(0.495)


def test_un_castig_negativ_slabeste_inmultind_cu_0_7():
    plasa = _plasa_cu(0.5)
    assert plasa.actualizeaza(NIMIC, FOLOSITA, castig=-0.02)["slabite"] == 1
    assert plasa.legaturi[LEGATURA]["tarie"] == pytest.approx(0.5 * 0.7 * 0.99)
    putin = _plasa_cu(0.5)
    putin.actualizeaza(NIMIC, FOLOSITA, castig=-0.005)  # câștig negativ mic → slăbire mică
    assert putin.legaturi[LEGATURA]["tarie"] == pytest.approx(0.5 * (1 - 0.3 * 0.5) * 0.99)


def test_peste_0_9_devine_definitiva_si_nu_mai_uita():
    plasa = _plasa_cu(0.85)
    assert plasa.actualizeaza(NIMIC, FOLOSITA, castig=0.02)["devenite_definitive"] == 1
    assert plasa.legaturi[LEGATURA]["stare"] == "definitiva"
    tarie = plasa.legaturi[LEGATURA]["tarie"]
    plasa.actualizeaza(NIMIC, FOLOSITA, castig=-0.02)
    assert plasa.legaturi[LEGATURA]["tarie"] == tarie  # definitivă: nu mai uită și nu mai slăbește


def test_un_castig_negativ_nu_taie_direct_legatura_noua():
    plasa = _plasa_cu(TARIE_NASTERE, "proba")
    assert plasa.actualizeaza(NIMIC, FOLOSITA, castig=-0.02)["taiate"] == 0
    assert plasa.legaturi[LEGATURA]["tarie"] == pytest.approx(0.1 * 0.7 * 0.99)  # 0,069: rămâne pentru runda 2


def test_taiata_doar_dupa_doua_experimente_la_rand_sub_0_05():
    plasa = _plasa_cu(TARIE_NASTERE, "proba")
    taiate = [plasa.actualizeaza(NIMIC, FOLOSITA, castig=-0.02)["taiate"] for _ in range(3)]
    # 0,1 → 0,069 (peste prag) → 0,048 (sub prag, 1) → 0,033 (sub prag, 2 la rând: tăiată)
    assert taiate == [0, 0, 1] and not plasa.legaturi


def test_revenirea_peste_prag_reia_numaratoarea():
    plasa = _plasa_cu(0.049)
    plasa.actualizeaza(NIMIC, NIMIC, castig=None)  # sub prag: 1
    assert plasa.legaturi[LEGATURA]["sub_prag"] == 1
    plasa.actualizeaza(NIMIC, FOLOSITA, castig=0.02)  # întărită peste prag: numărătoarea se reia
    assert plasa.legaturi[LEGATURA]["sub_prag"] == 0
    plasa.actualizeaza(NIMIC, FOLOSITA, castig=-0.02)
    assert LEGATURA in plasa.legaturi


def test_iese_din_proba_cand_trece_de_0_2():
    plasa = _plasa_cu(TARIE_NASTERE, "proba")
    plasa.actualizeaza(NIMIC, FOLOSITA, castig=0.02)
    assert plasa.legaturi[LEGATURA]["stare"] == "activa"


def test_plasa_se_salveaza_fara_legaturile_cu_centrul(tmp_path):
    plasa = _plasa_cu(0.5)
    plasa.actualizeaza(NIMIC, NIMIC, castig=None)
    plasa.salveaza(tmp_path / "plasa.json")
    copie = Plasa.incarca(tmp_path / "plasa.json", NUME_NODURI)
    assert copie.legaturi == plasa.legaturi and copie.experimente == 1
    assert all("centru" not in pereche for pereche in copie.legaturi)
    with pytest.raises(ValueError, match="alte noduri"):
        Plasa.incarca(tmp_path / "plasa.json", ["unu", "doi"])


# --- plasa în model ------------------------------------------------------------------------


def test_plasa_supravietuieste_intre_experimente(tmp_path, memorie, tokenizer_mic):
    cale = tmp_path / "plasa.json"
    _plasa_cu(0.5).salveaza(cale)  # plasa lăsată de un experiment de dinainte
    model = ModelPlasa(**MIC, cale_tokenizer=tokenizer_mic, plasa=True, cale_plasa=str(cale))
    model.conecteaza_memorie(memorie)
    statistici = model.antreneaza(DateMostra(propozitii=300), 1.0)
    assert statistici["plasa"]["legaturi_la_start"] == 1
    a, b = NUME_NODURI.index("fiinte"), NUME_NODURI.index("actiuni")
    assert model.retea.legaturi[a, b].item() == pytest.approx(0.5)  # legătura din fișier intră în rețea
    rezultat = model.dupa_examen({"castig": 0.02})["plasa"]
    for cheie in ("legaturi", "nascute", "intarite", "slabite", "taiate", "definitive", "in_proba", "experimente"):
        assert cheie in rezultat
    assert Plasa.incarca(cale, NUME_NODURI).experimente == 1  # starea nouă s-a păstrat în fișier


def test_plasa_nu_vede_textul_de_examen(tmp_path, memorie, tokenizer_mic):
    cale = tmp_path / "plasa.json"
    model = ModelPlasa(**MIC, cale_tokenizer=tokenizer_mic, plasa=True, cale_plasa=str(cale))
    model.conecteaza_memorie(memorie)
    model.antreneaza(DateMostra(propozitii=300), 1.0)
    cereri, folosire = copy.deepcopy(model._cereri), copy.deepcopy(model._folosire)
    model.biti_pentru("the cat ran to the horse. " * 20)
    model.genereaza("the ", 30)
    assert model._cereri == cereri and model._folosire == folosire  # examenul nu schimbă nimic în plasă
    assert not cale.exists()  # plasa se scrie doar după examen, din câștig


def test_fara_plasa_nu_invata_dupa_examen(memorie, tokenizer_mic):
    model = ModelPlasa(**MIC, cale_tokenizer=tokenizer_mic)
    model.conecteaza_memorie(memorie)
    model.antreneaza(DateMostra(propozitii=200), 0.5)
    assert model.dupa_examen({"castig": 0.05}) is None


def test_cu_plasa_se_salveaza_si_se_reincarca(tmp_path, memorie, tokenizer_mic):
    cale = tmp_path / "plasa.json"
    _plasa_cu(0.5).salveaza(cale)
    model = ModelPlasa(**MIC, cale_tokenizer=tokenizer_mic, plasa=True, cale_plasa=str(cale))
    model.conecteaza_memorie(memorie)
    model.antreneaza(DateMostra(propozitii=300), 1.0)
    biti = model.biti_pentru("the cat sat.")
    copie = ModelPlasa(dispozitiv="cpu", cale_tokenizer=tokenizer_mic)
    copie.conecteaza_memorie(memorie)
    copie.incarca(model.salveaza(str(tmp_path / "model")))
    assert copie.cu_plasa and copie.biti_pentru("the cat sat.") == pytest.approx(biti, rel=1e-5)


def test_asocierea_numara_cuvintele_vecine(memorie, tokenizer_mic):
    """În „good cat ran sword”, repetat, fiecare fel de cuvânt e urmat mereu de același fel: de 4× mai des ca întâmplător."""
    model = ModelPlasa(**MIC, cale_tokenizer=tokenizer_mic)
    model.conecteaza_memorie(memorie)
    asociere = model._masoara_asocierea("good cat ran sword " * 50)
    insusiri, fiinte, actiuni, locuri = (NUME_NODURI.index(n) for n in ("insusiri", "fiinte", "actiuni", "locuri_obiecte"))
    for a, b in ((insusiri, fiinte), (fiinte, actiuni), (actiuni, locuri), (locuri, insusiri)):
        assert asociere[a][b] == pytest.approx(4.0, rel=0.02)
    assert asociere[fiinte][insusiri] == 0.0  # în ordinea inversă nu apar niciodată
    assert model._masoara_asocierea("x") is None  # niciun cuvânt terminat: nimic de măsurat


def test_fara_memorie_nu_se_masoara_asocierea(tokenizer_mic):
    assert ModelPlasa(**MIC, cale_tokenizer=tokenizer_mic)._masoara_asocierea("good cat ran sword " * 5) is None
