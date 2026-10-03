"""Plasa adaptivă: un nod pe raft, nodurile libere ajută rafturile încărcate, fiecare simbol calculează doar nodurile lui."""

from __future__ import annotations

import copy
import json
import math
from collections import Counter

import pytest

torch = pytest.importorskip("torch")

from module.date_mostra import DateMostra  # noqa: E402
from module.memorie_ierarhica import MemorieIerarhica  # noqa: E402
from module.model_gpt import ModelGPT  # noqa: E402
from module.model_plasa_adaptiva import (  # noqa: E402
    MINIM_PERECHE, NOD_RAR, PRAG_ASOCIERE, UMPLUTURA, ModelPlasaAdaptiva, StareAdaptiva, _GPTCuNoduriRare, _jumatate,
)
from module.tokenizer_bpe import antreneaza_bpe  # noqa: E402
from teste.biblioteca_mica import biblioteca_mica  # noqa: E402

MIC = dict(n_straturi=1, n_capete=2, n_emb=32, context=32, lot=8, dispozitiv="cpu", n_ascuns_nod=16)


class _Date:
    def __init__(self, text: str) -> None:
        self.text = text

    def text_antrenare(self) -> str:
        return self.text

    def text_validare(self) -> str:
        return self.text[:300]


@pytest.fixture
def tokenizer_mic(tmp_path):
    cale = tmp_path / "bpe_mic.json"
    antreneaza_bpe(DateMostra(propozitii=600).text_antrenare() + "horse sword good bad Tom Timmy ", 320).salveaza(cale)
    return str(cale)


@pytest.fixture
def memorie(tmp_path):
    return MemorieIerarhica(cale=biblioteca_mica(tmp_path), nivele=6, fara_cuvinte_de_legatura=True, sens_dupa_context=True)


@pytest.fixture
def nou(tmp_path, memorie, tokenizer_mic):
    def fa(**setari):
        model = ModelPlasaAdaptiva(**{**MIC, "cale_tokenizer": tokenizer_mic, "cale_plasa": str(tmp_path / "stare.json"),
                                      "pasi_max": 3, **setari})
        model.conecteaza_memorie(memorie)
        return model

    return fa


# La fiecare repetiție: 4 animale (cat, horse), 2 verbe (ran), 2 însușiri (good, bad), 1 adverb (back).
TEXT = "the cat ran to the good horse. the bad cat and the horse ran back. " * 60


def test_un_nod_pe_raft_peste_0_5_la_suta_restul_la_rar_si_nu_se_muta(nou, tmp_path):
    # 300 de pisici și 300 de „ran”, o singură sabie: noun.artifact are 0,17% din cuvintele cu sens → nodul „rar”
    model = nou()
    model.antreneaza(_Date("the cat ran. " * 300 + "the sword. "), 30.0)
    assert model.nume_noduri == ["noun.animal", "verb.motion", NOD_RAR]
    assert model._incarcari == [300, 300, 1]
    model.dupa_examen({"castig": None})
    # La experimentul următor, cu alt text, nodurile rămân pe rafturile lor: sabia tot la „rar” merge.
    alt = nou()
    alt.antreneaza(_Date("the sword. " * 300), 30.0)
    assert alt.nume_noduri == ["noun.animal", "verb.motion", NOD_RAR] and alt._incarcari == [0, 0, 300]


def test_umplutura_ramane_pe_trunchi(nou):
    model = nou()
    model.antreneaza(_Date(TEXT), 30.0)
    simboluri = model.tok.codifica("the and the a cat ")
    noduri = model._pozitii("", simboluri).view(-1).tolist()
    assert noduri[-1] == model._index["noun.animal"]  # după „cat” terminat, simbolul următor merge la nodul lui
    assert all(n == UMPLUTURA for n in noduri[:-2])  # cuvintele de legătură n-au nod


def test_drumul_simbolurilor_nu_vede_viitorul(nou):
    model = nou()
    model.antreneaza(_Date(TEXT), 30.0)
    simboluri = model.tok.codifica("Tom ran to the cat. Tom saw the good horse back! “the” sword. Timmy")
    toate = model._pozitii("", simboluri)
    for t in range(1, len(simboluri) + 1):
        assert torch.equal(model._pozitii("", simboluri[:t]), toate[:t]), f"scurgere din viitor la simbolul {t}"


def test_la_inceput_e_identic_cu_gpt_ul(nou, tokenizer_mic):
    """Nodurile pornesc tăcute: neantrenată, plasa adaptivă dă exact ce dă GPT-ul simplu, cu aceeași sămânță."""
    setari = {k: v for k, v in MIC.items() if k != "n_ascuns_nod"}
    gpt = ModelGPT(**setari, tokenizer="bpe", cale_tokenizer=tokenizer_mic)
    plasa = nou(pasi_max=0)
    assert gpt.antreneaza(_Date(TEXT), 0.0)["pasi"] == 0 and plasa.antreneaza(_Date(TEXT), 0.0)["pasi"] == 0
    text = "the cat ran to the horse. a good sword."
    assert plasa.biti_pentru(text) == pytest.approx(gpt.biti_pentru(text), rel=1e-6)


def test_fiecare_simbol_calculeaza_doar_nodul_lui_si_vecinii():
    retea = _GPTCuNoduriRare(50, 1, 2, 16, 8, 0.0, n_ascuns_nod=4, vecini=[[0], [1, 2], [2]])
    noduri = torch.tensor([[0, 1, UMPLUTURA, 2, 1]])
    simbol, nod_simbol, nod, loc, cap = retea._plan(noduri)
    perechi = sorted(zip(simbol.tolist(), nod.tolist()))
    assert perechi == [(0, 0), (1, 1), (1, 2), (3, 2), (4, 1), (4, 2)]  # umplutura (simbolul 2): nimic
    assert cap == 3  # cea mai lungă coadă: nodul 2 (simbolurile 1, 3, 4)
    assert retea._plan(torch.full((1, 4), UMPLUTURA)) is None
    assert retea(torch.zeros((1, 5), dtype=torch.long), noduri.unsqueeze(-1)).shape == (1, 5, 50)


def test_jumatate_imparte_cuvintele_intregi():
    assert _jumatate(Counter({"tim": 400, "mom": 300, "lily": 200, "tom": 100})) == ["tim", "tom"]  # 500 din 1000


def test_nodul_incarcat_primeste_un_ajutor_care_preia_jumatate():
    stare = StareAdaptiva(noduri_libere=2)
    stare.rafturi = ["noun.person", "adj.all"]
    rezultat = stare.actualizeaza_alocarile(
        {"noun.person": 1000, "adj.all": 100, NOD_RAR: 50},  # media 383: noun.person trece de 2× media
        {"noun.person": Counter({"tim": 400, "mom": 300, "lily": 200, "tom": 100}), "adj.all": Counter({"big": 100})},
    )
    assert [(a["nod"], a["ajuta"], a["preia"]) for a in rezultat["alocate"]] == [("liber1", "noun.person", 0.5)]
    assert stare.noduri() == ["noun.person", "adj.all", NOD_RAR, "liber1"]  # nodurile alocate nu se mută
    assert stare.ajutoare[0]["cuvinte"] == ["tim", "tom"] and rezultat["libere"] == 1


def test_rezerva_se_termina_si_un_singur_cuvant_nu_se_imparte():
    stare = StareAdaptiva(noduri_libere=1)
    stare.rafturi = ["a", "b", "c", "d", "e"]
    rezultat = stare.actualizeaza_alocarile(  # media 325: „a” și „b” trec amândouă de 2× media
        {"a": 1000, "b": 900, "c": 10, "d": 10, "e": 30, NOD_RAR: 0},
        {"a": Counter({"x": 1000}), "b": Counter({"y": 500, "z": 400}), "c": Counter({"w": 10})},
    )
    # „a” are un singur cuvânt (n-are ce împărți), „b” ia singurul nod liber
    assert [a["ajuta"] for a in rezultat["alocate"]] == ["b"] and rezultat["libere"] == 0


def test_ajutorul_se_intoarce_dupa_3_examene_la_rand_sub_medie():
    stare = StareAdaptiva(noduri_libere=2)
    stare.rafturi = ["a", "b"]
    stare.actualizeaza_alocarile({"a": 1000, "b": 10, NOD_RAR: 10}, {"a": Counter({"x": 600, "y": 400})})
    stare.legaturi[("liber1", "b")] = {"tarie": 0.3, "stare": "activa", "nascuta_la": 1, "sub_prag": 0}
    sub = {"a": 5, "b": 400, NOD_RAR: 400, "liber1": 5}  # raftul „a” (a + liber1) sub medie
    assert stare.actualizeaza_alocarile(sub, {})["eliberate"] == []
    assert stare.actualizeaza_alocarile({"a": 900, "b": 10, NOD_RAR: 10, "liber1": 900}, {})["eliberate"] == []  # reia
    for _ in range(2):
        assert stare.actualizeaza_alocarile(sub, {})["eliberate"] == []
    rezultat = stare.actualizeaza_alocarile(sub, {})  # a treia oară la rând
    assert rezultat["eliberate"] == [{"nod": "liber1", "raft": "a"}] and rezultat["libere"] == 2
    assert stare.noduri() == ["a", "b", NOD_RAR] and not stare.legaturi  # legăturile lui pleacă și ele


def test_ajutoarele_se_folosesc_de_la_experimentul_urmator(nou, tmp_path):
    model = nou(noduri_libere=1)
    model.antreneaza(_Date(TEXT), 30.0)
    assert NOD_RAR in model.nume_noduri and len(model.nume_noduri) == 5  # animal, motion, adj, adv, rar
    rezultat = model.dupa_examen({"castig": 0.01})
    alocat = rezultat["noduri"]["alocate"][0]
    assert alocat["nod"] == "liber1" and alocat["ajuta"] == "noun.animal"  # cat + horse: cel mai încărcat
    json.loads((tmp_path / "stare.json").read_text(encoding="utf-8"))  # starea s-a păstrat
    urmator = nou(noduri_libere=1)
    statistici = urmator.antreneaza(_Date(TEXT), 30.0)
    assert urmator.nume_noduri[-1] == "liber1" and statistici["noduri"]["ajutoare"][0]["ajuta"] == "noun.animal"
    preluate = set(urmator.stare.ajutoare[0]["cuvinte"])
    cuvinte = urmator._cuvinte_pe_nod[urmator._index["liber1"]]
    assert set(cuvinte) == preluate and cuvinte  # ajutorul primește exact cuvintele preluate


def test_se_pot_naste_doar_perechile_peste_3x_vazute_de_100_de_ori(nou):
    model = nou()
    model.antreneaza(_Date(TEXT), 30.0)
    # „good horse” și „bad cat”: însușirea e urmată mereu de un animal (de 120 de ori, 3,75× mai des ca întâmplător)
    animal, adjectiv = model._index["noun.animal"], model._index["adj.all"]
    assert model._asociere[adjectiv][animal] >= PRAG_ASOCIERE
    assert animal in model._vecini[adjectiv] and adjectiv not in model._vecini[animal]
    rar = nou()
    rar.antreneaza(_Date("the good horse ran. " * (MINIM_PERECHE - 1)), 30.0)  # aceeași pereche, de 99 de ori
    adjectiv = rar._index["adj.all"]
    assert rar._asociere[adjectiv][rar._index["noun.animal"]] >= PRAG_ASOCIERE and rar._vecini[adjectiv] == [adjectiv]


def test_legaturile_vin_din_starea_pastrata(nou, tmp_path):
    stare = StareAdaptiva()
    stare.rafturi = ["noun.animal", "verb.motion", "adj.all", "adv.all"]
    stare.legaturi[("noun.animal", "verb.motion")] = {"tarie": 0.5, "stare": "activa", "nascuta_la": 1, "sub_prag": 0}
    stare.salveaza(tmp_path / "stare.json")
    model = nou()
    statistici = model.antreneaza(_Date(TEXT), 30.0)
    a, b = model._index["noun.animal"], model._index["verb.motion"]
    assert statistici["plasa"]["legaturi_la_start"] == 1 and b in model._vecini[a]
    assert model.retea.legaturi[a, b].item() == pytest.approx(0.5)  # legătura din fișier intră în rețea
    rezultat = model.dupa_examen({"castig": 0.02})["plasa"]
    for cheie in ("legaturi", "nascute", "nascute_acum", "intarite", "slabite", "taiate", "castig_primit"):
        assert cheie in rezultat


def test_nu_vede_textul_de_examen(nou, tmp_path):
    model = nou()
    model.antreneaza(_Date(TEXT), 30.0)
    inainte = copy.deepcopy((model._cereri, model._folosire, model._incarcari, model._vecini))
    model.biti_pentru("the bad sword ran to the cat. " * 20)
    model.genereaza("the ", 30)
    assert (model._cereri, model._folosire, model._incarcari, model._vecini) == inainte
    assert not (tmp_path / "stare.json").exists()  # starea se scrie doar după examen


def test_invata_si_se_reincarca(nou, tmp_path, memorie, tokenizer_mic):
    model = nou(pasi_max=20)
    statistici = model.antreneaza(_Date(TEXT), 30.0)
    assert statistici["pasi"] == 20 and statistici["noduri"]["noduri_calculate_pe_simbol"] >= 1
    text = "the cat ran to the horse."
    biti = model.biti_pentru(text)
    assert math.isfinite(biti) and len(model.genereaza("the cat ", 20)) == 20
    copie = ModelPlasaAdaptiva(dispozitiv="cpu", cale_tokenizer=tokenizer_mic)
    copie.conecteaza_memorie(memorie)
    copie.incarca(model.salveaza(str(tmp_path / "model")))
    assert copie.nume_noduri == model.nume_noduri and copie.biti_pentru(text) == pytest.approx(biti, rel=1e-5)


def test_fara_memorie_totul_ramane_pe_trunchi(tmp_path, tokenizer_mic):
    model = ModelPlasaAdaptiva(**MIC, cale_tokenizer=tokenizer_mic, cale_plasa=str(tmp_path / "s.json"), pasi_max=2)
    statistici = model.antreneaza(_Date(TEXT), 30.0)
    assert statistici["noduri"]["simboluri_pe_trunchi"] == 1.0 and model.nume_noduri == [NOD_RAR]
    assert math.isfinite(model.biti_pentru("the cat."))
