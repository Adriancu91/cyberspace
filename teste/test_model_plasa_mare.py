"""Testul în trei trepte: GPT-ul care continuă și plasa mare (noduri în RAM, totul păstrat între experimente)."""

from __future__ import annotations

import copy
import json
import math

import pytest

torch = pytest.importorskip("torch")

from module.date_mostra import DateMostra  # noqa: E402
from module.memorie_ierarhica import MemorieIerarhica  # noqa: E402
from module.model_continuu import ModelGPTContinuu, simboluri_din_cache  # noqa: E402
from module.model_gpt import ModelGPT  # noqa: E402
from module.model_plasa_mare import ModelPlasaMare, _NoduriInRAM  # noqa: E402
from module.tokenizer_bpe import TokenizerBPE, antreneaza_bpe  # noqa: E402
from teste.biblioteca_mica import biblioteca_mica  # noqa: E402

MIC = dict(n_straturi=1, n_capete=2, n_emb=32, context=32, lot=8, dispozitiv="cpu")
TEXT = "the cat ran to the good horse. the bad cat and the horse ran back. " * 60


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


# --- GPT-ul care continuă -----------------------------------------------------------------------


def test_gpt_continuu_porneste_de_unde_a_ramas(tmp_path, tokenizer_mic):
    def nou():
        return ModelGPTContinuu(**MIC, tokenizer="bpe", cale_tokenizer=tokenizer_mic, pasi_max=30,
                                cale_stare=str(tmp_path / "gpt.pt"), director_cache=str(tmp_path / "cache"))

    primul = nou()
    statistici = primul.antreneaza(_Date(TEXT), 30.0)
    assert statistici["pasi_total"] == 30 and not statistici["continuat"]
    biti_1 = primul.biti_pentru("the cat ran.")
    assert not (tmp_path / "gpt.pt").exists()  # starea se scrie doar după examen
    assert primul.dupa_examen({"castig": None})["continuare"]["pasi_total"] == 30
    al_doilea = nou()
    statistici = al_doilea.antreneaza(_Date(TEXT), 30.0)
    assert statistici["pasi_total"] == 60 and statistici["continuat"]
    assert al_doilea.biti_pentru("the cat ran.") < biti_1  # a continuat să învețe, n-a pornit de la zero
    assert len(list((tmp_path / "cache").glob("simboluri_*.pt"))) == 1  # textul s-a împărțit o singură dată


def test_gpt_continuu_fara_stare_e_ca_gpt_ul(tokenizer_mic):
    simplu = ModelGPT(**MIC, tokenizer="bpe", cale_tokenizer=tokenizer_mic, pasi_max=5)
    continuu = ModelGPTContinuu(**MIC, tokenizer="bpe", cale_tokenizer=tokenizer_mic, pasi_max=5)
    simplu.antreneaza(_Date(TEXT), 30.0)
    continuu.antreneaza(_Date(TEXT), 30.0)
    assert continuu.biti_pentru("the cat ran.") == pytest.approx(simplu.biti_pentru("the cat ran."), rel=1e-5)
    assert continuu.dupa_examen({"castig": None}) is None


def test_cache_ul_de_simboluri_da_aceleasi_simboluri(tmp_path, tokenizer_mic):
    tok = TokenizerBPE.incarca(tokenizer_mic)
    prima = simboluri_din_cache(tok, TEXT, str(tmp_path), tokenizer_mic)
    a_doua = simboluri_din_cache(tok, TEXT, str(tmp_path), tokenizer_mic)
    assert prima.tolist() == a_doua.tolist() == tok.codifica(TEXT)


def test_starea_altui_model_nu_se_incarca(tmp_path, tokenizer_mic):
    model = ModelGPTContinuu(**MIC, tokenizer="bpe", cale_tokenizer=tokenizer_mic, pasi_max=2, cale_stare=str(tmp_path / "s.pt"))
    model.antreneaza(_Date(TEXT), 30.0)
    model.dupa_examen({})
    altul = ModelGPTContinuu(**{**MIC, "n_emb": 64}, tokenizer="bpe", cale_tokenizer=tokenizer_mic, pasi_max=2,
                             cale_stare=str(tmp_path / "s.pt"))
    with pytest.raises(ValueError, match="altui model"):
        altul.antreneaza(_Date(TEXT), 30.0)


# --- plasa mare -----------------------------------------------------------------------------------


@pytest.fixture
def mare(tmp_path, memorie, tokenizer_mic):
    def fa(**setari):
        model = ModelPlasaMare(**{**MIC, "n_ascuns_nod": 16, "noduri_libere": 2, "cale_tokenizer": tokenizer_mic,
                                  "cale_stare": str(tmp_path / "plasa.pt"), "director_cache": str(tmp_path / "cache"),
                                  "pasi_max": 20, **setari})
        model.conecteaza_memorie(memorie)
        return model

    return fa


def test_nodurile_stau_in_ram_si_urca_doar_cele_cerute(mare):
    model = mare()
    statistici = model.antreneaza(_Date(TEXT), 30.0)
    parametri_retea = {id(p) for p in model.retea.parameters()}
    assert all(id(t) not in parametri_retea for t in model.noduri_ram.greutati.values())  # nodurile nu sunt în rețea
    assert statistici["parametri_noduri"] == model.noduri_ram.parametri() > 0
    assert statistici["parametri_total"] == statistici["parametri_trunchi"] + statistici["parametri_noduri"]
    # 4 rafturi + „rar” + 2 libere = 7 locuri; în text apar doar cele 4 rafturi: doar ele urcă (nici „rar”, nici liberele)
    assert len(model.nume_noduri) == 7 and statistici["mutare_noduri"]["noduri_urcate_pe_pas"] <= 4
    assert set(statistici["mutare_noduri"]) >= {"secunde_sus", "secunde_jos", "secunde_optimizator_ram", "parte_din_antrenare"}


def test_la_inceput_e_identica_cu_gpt_ul(mare, tokenizer_mic):
    gpt = ModelGPT(**MIC, tokenizer="bpe", cale_tokenizer=tokenizer_mic, pasi_max=0)
    plasa = mare(pasi_max=0)
    gpt.antreneaza(_Date(TEXT), 0.0)
    plasa.antreneaza(_Date(TEXT), 0.0)
    text = "the cat ran to the horse. a good sword."
    assert plasa.biti_pentru(text) == pytest.approx(gpt.biti_pentru(text), rel=1e-6)


def test_drumul_simbolurilor_nu_vede_viitorul(mare):
    model = mare()
    model.antreneaza(_Date(TEXT), 30.0)
    simboluri = model.tok.codifica("Tom ran to the cat. Tom saw the good horse back! “the” sword. Timmy")
    toate = model._pozitii("", simboluri)
    for t in range(1, len(simboluri) + 1):
        assert torch.equal(model._pozitii("", simboluri[:t]), toate[:t]), f"scurgere din viitor la simbolul {t}"


def test_totul_se_pastreaza_intre_experimente(mare, tmp_path):
    primul = mare(noduri_libere=1)
    primul.antreneaza(_Date(TEXT), 30.0)
    biti_1 = primul.biti_pentru("the cat ran to the good horse.")
    rezultat = primul.dupa_examen({"castig": 0.01})
    assert rezultat["noduri"]["alocate"][0]["ajuta"] == "noun.animal"  # cat + horse: cel mai încărcat
    alocat = primul._index["liber1"]
    ajutat = primul._index["noun.animal"]
    for nume, t in primul.noduri_ram.greutati.items():  # ajutorul pornește ca o copie a nodului ajutat
        assert torch.equal(t[alocat], t[ajutat]), nume
    plasa = json.loads((tmp_path / "plasa.plasa.json").read_text(encoding="utf-8"))
    assert plasa["ajutoare"][0]["nume"] == "liber1"

    al_doilea = mare(noduri_libere=1)
    statistici = al_doilea.antreneaza(_Date(TEXT), 30.0)
    assert statistici["continuat"] and statistici["pasi_total"] == 40
    assert statistici["noduri"]["ajutoare"][0]["nod"] == "liber1"  # alocarea a rămas
    assert al_doilea.biti_pentru("the cat ran to the good horse.") < biti_1  # a continuat să învețe


def test_cererea_se_ajusteaza_cand_se_schimba_taria(mare):
    model = mare()
    model.antreneaza(_Date(TEXT), 30.0)
    a, b = model._index["adj.all"], model._index["noun.animal"]
    with torch.no_grad():  # o cerere mare: legătura se naște (asocierea „good horse” e peste 3×, de 120 de ori)
        model.retea.cerere[a, b] = 0.2
    model._cereri[a][b] = 0.2
    inainte = model.retea.amestec()[a, b].item()
    rezultat = model.dupa_examen({"castig": None})
    assert {"de_la": "adj.all", "la": "noun.animal"} in rezultat["plasa"]["nascute_acum"]
    model.retea.legaturi[a, b] = model.stare.legaturi[("adj.all", "noun.animal")]["tarie"]
    assert model.retea.amestec()[a, b].item() == pytest.approx(inainte)  # rețeaua nu sare


def test_adamw_din_ram_e_ca_adamw_din_torch_si_nu_atinge_nodurile_neurcate():
    torch.manual_seed(0)
    greutati = {k: torch.randn(3, 3, 4) for k in ("ln_pondere", "ln_deplasare", "sus", "sus_deplasare", "jos", "jos_deplasare")}
    noduri = _NoduriInRAM({k: v.clone() for k, v in greutati.items()})
    referinta = [torch.nn.Parameter(v[:2].clone()) for v in greutati.values()]
    optimizator = torch.optim.AdamW(referinta, lr=0.01, weight_decay=0.1)
    for _ in range(3):
        gradiente = {k: torch.randn(2, 3, 4) for k in greutati}
        for p, g in zip(referinta, gradiente.values()):
            p.grad = g.clone()
        optimizator.step()
        noduri.pas([0, 1], gradiente, 1.0, 0.01, 0.1)  # nodul 2 n-a urcat: rămâne neatins
    for p, (nume, t) in zip(referinta, noduri.greutati.items()):
        assert torch.allclose(p.detach(), t[:2], atol=1e-6)
        assert torch.equal(t[2], greutati[nume][2])
    copie = _NoduriInRAM.din_stare(copy.deepcopy(noduri.stare()))  # starea (cu optimizatorul) se reface la fel
    gradiente = {k: torch.randn(2, 3, 4) for k in greutati}
    noduri.pas([0, 1], gradiente, 1.0, 0.01, 0.1)
    copie.pas([0, 1], gradiente, 1.0, 0.01, 0.1)
    assert all(torch.allclose(noduri.greutati[k], copie.greutati[k]) for k in greutati)


def test_se_salveaza_si_se_reincarca(mare, tmp_path, memorie, tokenizer_mic):
    model = mare()
    model.antreneaza(_Date(TEXT), 30.0)
    biti = model.biti_pentru("the cat ran to the horse.")
    assert math.isfinite(biti) and len(model.genereaza("the cat ", 20)) == 20
    copie = ModelPlasaMare(dispozitiv="cpu", cale_tokenizer=tokenizer_mic)
    copie.conecteaza_memorie(memorie)
    copie.incarca(model.salveaza(str(tmp_path / "model")))
    assert copie.biti_pentru("the cat ran to the horse.") == pytest.approx(biti, rel=1e-5)


def test_testul_rapid_nu_scrie_starea(mare, tmp_path):
    model = mare()
    model.antreneaza(_Date(TEXT), 30.0)
    model.biti_pentru("the cat ran.")
    assert not (tmp_path / "plasa.pt").exists()  # doar dupa_examen (experimentul adevărat) o scrie


# --- GPT-ul care continuă, în bucla de auto-îmbunătățire (o stare pentru fiecare arhitectură) ----------


def test_fiecare_arhitectura_isi_continua_cea_mai_buna_stare(tmp_path, tokenizer_mic):
    def nou(**setari):
        return ModelGPTContinuu(**{**MIC, **setari}, tokenizer="bpe", cale_tokenizer=tokenizer_mic, pasi_max=20,
                                director_stari=str(tmp_path / "stari"))

    primul = nou()
    primul.antreneaza(_Date(TEXT), 30.0)
    assert primul.dupa_examen({"scor": 2.0})["continuare"]["salvat"]  # prima stare a arhitecturii
    alta_arhitectura = nou(n_emb=64)
    assert not alta_arhitectura.antreneaza(_Date(TEXT), 30.0)["continuat"]  # pornește de la zero, în fișierul ei
    alta_arhitectura.dupa_examen({"scor": 2.5})
    assert len(list((tmp_path / "stari").glob("gpt_*.pt"))) == 2

    continuare = nou(rata_invatare=0.0005, lot=4)  # aceeași arhitectură, alt lot și altă rată
    statistici = continuare.antreneaza(_Date(TEXT), 30.0)
    assert statistici["continuat"] and statistici["pasi_total"] == 40 and statistici["scor_la_pornire"] == 2.0
    assert continuare.optimizator.param_groups[0]["lr"] == 0.0005  # rata rețetei de acum, nu a celei salvate
    assert not continuare.dupa_examen({"scor": 2.1})["continuare"]["salvat"]  # mai slab: starea bună rămâne
    al_treilea = nou()
    assert al_treilea.antreneaza(_Date(TEXT), 30.0)["pasi_total"] == 40  # pornește tot din starea cu scorul 2,0
    assert al_treilea.dupa_examen({"scor": 1.9})["continuare"]["salvat"]  # mai bun: starea se înlocuiește
    assert nou().antreneaza(_Date(TEXT), 30.0)["scor_la_pornire"] == 1.9


# --- GPT-ul care continuă, în bucla cinstită: de la zero, din aceeași stare, rata care scade între experimente -------


def test_de_la_zero_nu_incarca_dar_isi_scrie_starea(tmp_path, tokenizer_mic):
    def nou():
        return ModelGPTContinuu(**MIC, tokenizer="bpe", cale_tokenizer=tokenizer_mic, pasi_max=10,
                                director_stari=str(tmp_path / "stari"), de_la_zero=True)

    for _ in range(2):  # a doua oară, aceeași arhitectură pornește tot de la zero (și își scrie din nou starea)
        model = nou()
        statistici = model.antreneaza(_Date(TEXT), 30.0)
        assert statistici["pasi_total"] == 10 and not statistici["continuat"] and statistici["pornit_din"] is None
        assert model.dupa_examen({"scor": 2.0})["continuare"]["salvat"]
    assert len(list((tmp_path / "stari").glob("gpt_*.pt"))) == 1


def test_stare_de_pornire_e_aceeasi_pentru_fiecare_experiment(tmp_path, tokenizer_mic):
    comun = dict(**MIC, tokenizer="bpe", cale_tokenizer=tokenizer_mic, pasi_max=10)
    sursa = ModelGPTContinuu(**comun, cale_stare=str(tmp_path / "pornire.pt"))
    sursa.antreneaza(_Date(TEXT), 30.0)
    sursa.dupa_examen({"scor": 2.0})
    continut = (tmp_path / "pornire.pt").read_bytes()
    for setari in ({"lot": 4}, {"rata_invatare": 5e-4}):  # lotul și rata se schimbă, starea de pornire nu
        model = ModelGPTContinuu(**{**comun, **setari}, stare_de_pornire=str(tmp_path / "pornire.pt"))
        statistici = model.antreneaza(_Date(TEXT), 30.0)
        assert statistici["continuat"] and statistici["pasi_total"] == 20  # 10 din stare + 10 acum, de fiecare dată
        assert statistici["pornit_din"] == str(tmp_path / "pornire.pt")
        assert model.dupa_examen({"scor": 1.0}) is None  # nu scrie nicăieri
    assert (tmp_path / "pornire.pt").read_bytes() == continut  # fișierul de pornire a rămas neatins
    lipsa = ModelGPTContinuu(**comun, stare_de_pornire=str(tmp_path / "nu_exista.pt"))
    with pytest.raises(FileNotFoundError, match="nu pornesc de la zero"):
        lipsa.antreneaza(_Date(TEXT), 30.0)
    with pytest.raises(ValueError, match="de_la_zero"):
        ModelGPTContinuu(**comun, de_la_zero=True, stare_de_pornire=str(tmp_path / "pornire.pt"))


def test_rata_care_scade_continua_intre_experimente(tmp_path, tokenizer_mic):
    def nou():
        return ModelGPTContinuu(**MIC, tokenizer="bpe", cale_tokenizer=tokenizer_mic, pasi_max=10,
                                cale_stare=str(tmp_path / "gpt.pt"), rata_care_scade=True, incalzire_pasi=5,
                                durata_scaderii_secunde=3600.0)

    primul = nou()
    assert primul.rata_acum(0, 0.0) == pytest.approx(primul.rata_invatare / 5)  # încălzirea, doar la început
    primul.antreneaza(_Date(TEXT), 30.0)
    primul.dupa_examen({"scor": 2.0})
    al_doilea = nou()
    al_doilea.antreneaza(_Date(TEXT), 30.0)  # citește starea: pașii și minutele de dinainte
    al_doilea.pasi_total, al_doilea.minute_total = 10, primul.minute_total  # cum erau în timpul antrenării lui
    assert al_doilea._pasi_anteriori() == 10 and al_doilea.rata_acum(0, 0.0) == pytest.approx(al_doilea.rata_invatare)
    # Scăderea continuă de unde a rămas: progresul pornește din secundele de antrenare de dinainte, pe cele 3.600.
    assert al_doilea._progres(0, 0.0, 0.0, 30.0) == pytest.approx(primul.minute_total * 60 / 3600)
    assert al_doilea._progres(0, 0.0, 1800.0, 30.0) == pytest.approx((primul.minute_total * 60 + 1800) / 3600)
