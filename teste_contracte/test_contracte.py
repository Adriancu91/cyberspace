"""Examenul de contract: fiecare modul trebuie să treacă testele portului lui.

Un modul nou se adaugă în lista MODULE de mai jos. Dacă pică aici,
nu are voie să intre pe platformă.
"""

from __future__ import annotations

import importlib.util
import math
import time

import pytest

from kronos.contracte import CONTRACT_PENTRU_PORT, Propunere, RezultatRulare
from kronos.registru import Registru

ARE_TORCH = importlib.util.find_spec("torch") is not None
GPT_MIC = {"n_straturi": 1, "n_capete": 2, "n_emb": 32, "context": 32, "lot": 8, "dispozitiv": "cpu"}


def _profesor_gata() -> bool:
    """Profesorul adevărat (Qwen3-4B în 4 biți) se testează doar dacă are tot ce-i trebuie: pachetele, placa video și
    modelul deja descărcat (testul nu descarcă 8 GB)."""
    if not ARE_TORCH or any(importlib.util.find_spec(m) is None for m in ("transformers", "bitsandbytes")):
        return False
    import torch

    from module.profesor_qwen import e_descarcat

    return torch.cuda.is_available() and e_descarcat()


PROFESOR_GATA = _profesor_gata()

# (port, cale, setari)
MODULE = [
    ("model", "module.model_ngram:ModelNgram", {"ordin": 3}),
    pytest.param(
        "model", "module.model_gpt:ModelGPT", GPT_MIC,
        marks=pytest.mark.skipif(not ARE_TORCH, reason="PyTorch nu e instalat"),
    ),
    pytest.param(
        "model", "module.model_gpt:ModelGPT", {**GPT_MIC, "tokenizer": "bpe", "cale_tokenizer": "__tokenizer_mic__"},
        marks=pytest.mark.skipif(not ARE_TORCH, reason="PyTorch nu e instalat"),
    ),
    pytest.param(
        "model", "module.model_plasa:ModelPlasa", {**GPT_MIC, "n_ascuns_nod": 16, "cale_tokenizer": "__tokenizer_mic__"},
        marks=pytest.mark.skipif(not ARE_TORCH, reason="PyTorch nu e instalat"),
    ),
    pytest.param(
        "model", "module.model_plasa_adaptiva:ModelPlasaAdaptiva",
        {**GPT_MIC, "n_ascuns_nod": 16, "cale_tokenizer": "__tokenizer_mic__", "cale_plasa": "__plasa_temporara__"},
        marks=pytest.mark.skipif(not ARE_TORCH, reason="PyTorch nu e instalat"),
    ),
    pytest.param(
        "model", "module.model_continuu:ModelGPTContinuu", {**GPT_MIC, "tokenizer": "bpe", "cale_tokenizer": "__tokenizer_mic__"},
        marks=pytest.mark.skipif(not ARE_TORCH, reason="PyTorch nu e instalat"),
    ),
    pytest.param(
        "model", "module.model_racit:ModelGPTRacit", {**GPT_MIC, "tokenizer": "bpe", "cale_tokenizer": "__tokenizer_mic__"},
        marks=pytest.mark.skipif(not ARE_TORCH, reason="PyTorch nu e instalat"),
    ),
    pytest.param(
        "model", "module.model_plasa_mare:ModelPlasaMare",
        {**GPT_MIC, "n_ascuns_nod": 16, "cale_tokenizer": "__tokenizer_mic__"},
        marks=pytest.mark.skipif(not ARE_TORCH, reason="PyTorch nu e instalat"),
    ),
    ("date", "module.date_mostra:DateMostra", {"propozitii": 300}),
    pytest.param(
        "date", "module.date_wikipedia:DateWikipedia", {"director": "__wikipedia_mic__"},
        marks=pytest.mark.skipif(importlib.util.find_spec("pyarrow") is None, reason="pyarrow nu e instalat"),
    ),
    ("date", "module.date_fisier:DateFisier", {"cale": "__fisier_temporar__"}),
    ("date", "module.date_tinystories:DateTinyStories", {"director": "__tinystories_mic__"}),
    ("date", "module.date_amestec:DateAmestec", {"cale_antrenare": "__amestec_temporar__", "cale_validare": ""}),
    ("examen", "module.examen_bpb:ExamenBpb", {}),
    ("cercetator", "module.cercetator_aleator:CercetatorAleator", {"spatiu": {"model": {"ordin": [1, 2, 3]}}}),
    ("cercetator", "module.cercetator_local:CercetatorLocal", {"spatiu": {"model": {"ordin": [1, 2, 3]}}}),
    ("profesor", "module.jucarii:ProfesorGol", {}),
    pytest.param(
        "profesor", "module.profesor_qwen:ProfesorQwen", {"max_simboluri": 40, "doar_local": True},
        marks=pytest.mark.skipif(not PROFESOR_GATA, reason="transformers, bitsandbytes, placa video sau modelul lipsesc"),
    ),
    ("rulare", "module.rulare_locala:RulareLocala", {}),
    ("stocare", "module.stocare_disc:StocareDisc", {"director": "__director_temporar__"}),
    ("interfata", "module.interfata_consola:InterfataConsola", {"tacut": True}),
    ("traducere", "module.jucarii:TraducereIdentitate", {}),
    ("memorie", "module.jucarii:MemorieGoala", {}),
    ("memorie", "module.memorie_ierarhica:MemorieIerarhica", {"cale": "__biblioteca_mica__", "nivele": 6}),
]


@pytest.fixture
def date_mici():
    return Registru().creeaza("date", "module.date_mostra:DateMostra", {"propozitii": 300}).instanta


def _setari_reale(setari, tmp_path):
    setari = dict(setari)
    if setari.get("cale") == "__fisier_temporar__":
        fisier = tmp_path / "text.txt"
        fisier.write_text("To be, or not to be, that is the question.\n" * 100, encoding="utf-8")
        setari["cale"] = str(fisier)
    if setari.get("cale_antrenare") == "__amestec_temporar__":
        (tmp_path / "antrenare.txt").write_text("the cat sat on the mat.\n" * 100, encoding="utf-8")
        (tmp_path / "validare.txt").write_text("the dog ran to the tree.\n" * 20, encoding="utf-8")
        setari.update(cale_antrenare=str(tmp_path / "antrenare.txt"), cale_validare=str(tmp_path / "validare.txt"))
    if setari.get("cale_tokenizer") == "__tokenizer_mic__":
        from module.date_mostra import DateMostra
        from module.tokenizer_bpe import antreneaza_bpe

        antreneaza_bpe(DateMostra(propozitii=600).text_antrenare(), 320).salveaza(tmp_path / "bpe_mic.json")
        setari["cale_tokenizer"] = str(tmp_path / "bpe_mic.json")
    if setari.get("director") == "__tinystories_mic__":
        from teste.tinystories_mic import scrie_surse

        setari = scrie_surse(tmp_path)
    if setari.get("cale") == "__biblioteca_mica__":
        from teste.biblioteca_mica import biblioteca_mica

        setari["cale"] = biblioteca_mica(tmp_path)
    if setari.get("director") == "__director_temporar__":
        setari["director"] = str(tmp_path / "stocare")
    if setari.get("cale_plasa") == "__plasa_temporara__":  # nu atinge plasa din lucru/
        setari["cale_plasa"] = str(tmp_path / "plasa.json")
    if setari.get("director") == "__wikipedia_mic__":
        from teste.wikipedia_mic import scrie_wikipedia

        setari = scrie_wikipedia(tmp_path)
    return setari


@pytest.mark.parametrize("port,cale,setari", MODULE)
def test_modulul_respecta_contractul(port, cale, setari, tmp_path, date_mici):
    setari = _setari_reale(setari, tmp_path)

    def nou():
        return Registru().creeaza(port, cale, setari).instanta

    instanta = nou()
    assert isinstance(instanta, CONTRACT_PENTRU_PORT[port])
    VERIFICARI[port](instanta, tmp_path, date_mici, nou)


# --- verificările fiecărui port ---------------------------------------------


def _model(m, tmp_path, date, nou):
    statistici = m.antreneaza(date, 2.0)
    assert isinstance(statistici, dict)
    biti = m.biti_pentru("the cat sat on the mat.")
    assert isinstance(biti, float) and math.isfinite(biti) and biti > 0
    assert m.biti_pentru("caractere nemaivăzute: ăîșțâ ∑") > 0  # nu crapă la necunoscute
    continuare = m.genereaza("the ", 30)
    assert isinstance(continuare, str) and len(continuare) == 30
    fisier = m.salveaza(str(tmp_path / "model"))
    copie = nou()  # un model nou, neantrenat, citește fișierul salvat
    copie.incarca(fisier)
    assert copie.biti_pentru("the cat sat on the mat.") == pytest.approx(biti, rel=1e-4)


def _date(d, tmp_path, _, nou):
    antrenare, validare = d.text_antrenare(), d.text_validare()
    assert isinstance(antrenare, str) and len(antrenare) > 100
    assert isinstance(validare, str) and len(validare) > 10
    assert d.text_antrenare() == antrenare  # mereu același text


def _examen(e, tmp_path, date, nou):
    assert isinstance(e.scor_principal, str) and isinstance(e.mai_mic_e_mai_bun, bool)
    model = Registru().creeaza("model", "module.model_ngram:ModelNgram", {"ordin": 2}).instanta
    model.antreneaza(date, 2.0)
    scoruri = e.examineaza(model, date)
    assert e.scor_principal in scoruri and math.isfinite(scoruri[e.scor_principal])


def _cercetator(c, tmp_path, _, nou):
    p = c.propune([], {"model": {"ordin": 1}})
    assert isinstance(p, Propunere) and isinstance(p.modificari, dict) and isinstance(p.descriere, str)


def _profesor(p, tmp_path, _, nou):
    exercitii = p.genereaza_exercitii("aritmetică", 3)
    assert isinstance(exercitii, list) and all(isinstance(e, dict) for e in exercitii)


def _rulare(r, tmp_path, _, nou):
    bun = r.executa(lambda: 42, 5)
    assert isinstance(bun, RezultatRulare) and bun.reusit and bun.valoare == 42
    gresit = r.executa(lambda: 1 / 0, 5)
    assert not gresit.reusit and "ZeroDivisionError" in gresit.eroare
    lent = r.executa(lambda: time.sleep(3), 0.5)
    assert not lent.reusit and "limita" in lent.eroare


def _stocare(s, tmp_path, _, nou):
    s.salveaza_json("proba/a", {"x": 1, "text": "ăîșț"})
    assert s.incarca_json("proba/a") == {"x": 1, "text": "ăîșț"}
    assert s.incarca_json("nu_exista") is None
    with pytest.raises(ValueError):
        s.cale_pentru("../../in_afara")


def _interfata(i, tmp_path, _, nou):
    for eveniment in ("start", "stare", "experiment", "final", "altceva"):
        i.anunta(eveniment, {"configurare": "t", "experimente": 1, "id": 1, "stare": "propus", "decizie": "pastrat",
                             "propunere": "p", "scor": 1.0, "experimente_rulate": 1, "pastrate": 1,
                             "cel_mai_bun_scor": 1.0, "setari_castigatoare": {}})


def _traducere(t, tmp_path, _, nou):
    assert isinstance(t.traduce("hello", "en", "ro"), str)


def _memorie(m, tmp_path, _, nou):
    assert isinstance(m.nivele, int) and m.nivele >= 1
    text = "The horse ran, the cat's tail; know'st thou?\nhorse"
    coduri = m.caracteristici(text)
    assert len(coduri) == len(text)  # un cod pentru fiecare literă
    assert all(isinstance(c, tuple) and len(c) == m.nivele and all(isinstance(x, int) for x in c) for c in coduri)
    for i in range(len(text) + 1):  # regula de aur: memoria nu dezvăluie viitorul
        assert m.caracteristici(text[:i]) == coduri[:i], f"scurgere din viitor la poziția {i}"
    cod = m.cod("horse")
    assert isinstance(cod, tuple) and len(cod) == m.nivele
    assert m.cod("HORSE") == cod
    sensuri = m.cauta("horse")
    assert isinstance(sensuri, list) and all(isinstance(s, dict) for s in sensuri)
    assert isinstance(m.statistici(), dict)


VERIFICARI = {
    "model": _model,
    "date": _date,
    "examen": _examen,
    "cercetator": _cercetator,
    "profesor": _profesor,
    "rulare": _rulare,
    "stocare": _stocare,
    "interfata": _interfata,
    "traducere": _traducere,
    "memorie": _memorie,
}


def test_fiecare_port_are_verificari():
    assert set(VERIFICARI) == set(CONTRACT_PENTRU_PORT)
