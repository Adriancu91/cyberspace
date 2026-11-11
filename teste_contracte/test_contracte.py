"""Examenul de contract: fiecare modul trebuie să treacă testele portului lui.

Un modul nou se adaugă în lista MODULE de mai jos. Dacă pică aici,
nu are voie să intre pe platformă.
"""

from __future__ import annotations

import importlib.util
import math
import time
from pathlib import Path

import pytest

from kronos.contracte import CONTRACT_PENTRU_PORT, Propunere, RezultatRulare
from kronos.registru import Registru

ARE_TORCH = importlib.util.find_spec("torch") is not None
KGR_MIC = Path(__file__).resolve().parents[1] / "integrare" / "kronos" / "vectori" / "mic_f32.kgr"  # din S39, în git
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
        "model", "module.model_conversatie:ModelGPTConversatie", {**GPT_MIC, "tokenizer": "bpe", "cale_tokenizer": "__tokenizer_mic__"},
        marks=pytest.mark.skipif(not ARE_TORCH, reason="PyTorch nu e instalat"),
    ),
    pytest.param(
        "model", "module.model_muon:ModelGPTConversatieMuon",
        {**GPT_MIC, "tokenizer": "bpe", "cale_tokenizer": "__tokenizer_mic__", "optimizator": "muon", "adunare_loturi": 2},
        marks=pytest.mark.skipif(not ARE_TORCH, reason="PyTorch nu e instalat"),
    ),
    pytest.param(
        "model", "module.model_gpt_cod:ModelGPTCod", {**GPT_MIC, "tokenizer": "bpe", "cale_tokenizer": "__tokenizer_mic__"},
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
    ("date", "module.date_cod:DateCod", {"director": "__simboluri_cod__", "context": 16, "previzualizare": True}),
    pytest.param(
        "date", "module.date_bucati:DateBucati", {"director": "__bucati_mici__", "previzualizare": True},
        marks=pytest.mark.skipif(not ARE_TORCH, reason="PyTorch nu e instalat"),
    ),
    ("examen", "module.examen_bpb:ExamenBpb", {}),
    ("examen", "module.examen_cod_validare:ExamenCodValidare", {}),
    ("examen", "module.examen_romana:ExamenRomana", {"validari": "__romana_mica__"}),
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
    ("cautare", "module.cautare_e3:CautareE3", {"cale_index": "__index_e3_mic__"}),
    ("inferenta", "module.inferenta_kgr1:InferentaKGR1", {"cale": str(KGR_MIC)}),
    ("inferenta", "module.inferenta_kgr1:InferentaKGR1", {"cale": str(KGR_MIC), "desfacere": "la_pas"}),
    ("inferenta", "module.inferenta_ccm:InferentaCCM", {"cale": str(KGR_MIC), "cale_reglaj": "__reglaj_mic__"}),
    ("inferenta", "module.inferenta_ccm:InferentaCCM", {"cale": str(KGR_MIC), "cale_reglaj": "__fara_reglaj__"}),
]

BUCATI_E3_MICI = [
    ("Orașul Brașov are o cetate veche pe deal.", "w0"),
    ("Orașele mari ale țării sunt București și Cluj.", "w1"),
    ("Satele din jurul Brașovului sunt mici.", "w2"),
    ("Brașov se poate referi la oraș sau la județ.", "w3"),
    ("Clujul are o universitate veche.", "w4"),
]


def index_e3_mic(tmp_path) -> dict[str, str]:
    """Cele două baze E3 (obișnuită și cu rădăcini) și listele, pe câteva bucăți; fără bazele mari din lucru/."""
    import json

    from unelte import e3_memorie as e3
    from unelte import e3_reordonare as r

    lucru = tmp_path / "e3"
    con = e3.creeaza(lucru / "index.sqlite")
    con.executemany("INSERT INTO bucati(rowid, text, articol, nr, sursa) VALUES (?, ?, ?, ?, ?)",
                    [(i, t, a, 0, "wikipedia") for i, (t, a) in enumerate(BUCATI_E3_MICI, 1)])
    con.commit()
    con.close()
    r.cmd_index_radacini(lucru)
    (lucru / "liste_s25.json").write_text(json.dumps({"fraze_lista": ["w3"], "randuri_scurte": []}), encoding="utf-8")
    return {"cale_index": str(lucru / "index.sqlite"), "cale_index_radacini": str(lucru / "index_radacini.sqlite"),
            "cale_liste": str(lucru / "liste_s25.json")}


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
    if setari.get("director") == "__simboluri_cod__":  # simboluri uint16 mici, nu cele din lucru/kronos_cod/
        from teste.cod_mic import scrie_simboluri

        setari.update(scrie_simboluri(tmp_path))
    if setari.get("director") == "__bucati_mici__":  # bucăți mici de simboluri, nu cele din lucru/bucati/
        from teste.bucati_mici import scrie_bucati

        setari.update(scrie_bucati(tmp_path))
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
    if setari.get("cale_index") == "__index_e3_mic__":
        setari.update(index_e3_mic(tmp_path))
    if setari.get("director") == "__wikipedia_mic__":
        from teste.wikipedia_mic import scrie_wikipedia

        setari = scrie_wikipedia(tmp_path)
    if setari.get("cale_reglaj") == "__reglaj_mic__":  # reglaj CCM pentru modelul mic, pe calculatorul acesta
        import json

        from module.calcul import reglaj

        banc = {"kgr": setari["cale"], "toleranta_logits": 1e-3, "cea_mai_rapida_pe_total": {"varianta": "transpus", "fire": "toate"},
                "rezultate": [{"varianta": "transpus", "fire": "toate", "acceptata": True,
                               "masurare": {"total": {"median": 1.0}, "simboluri_pe_secunda": {"median": 1.0}},
                               "verificare_model": {"dif_logits_max": 0.0}}]}
        (tmp_path / "reglaj.json").write_text(json.dumps(reglaj.din_banc(banc, "test")), encoding="utf-8")
        setari["cale_reglaj"] = str(tmp_path / "reglaj.json")
    if setari.get("validari") == "__romana_mica__":  # o validare mică, cu amprenta ei (nu cele din date/ws/)
        from module.examen_romana import sha256

        fisier = tmp_path / "romana_mica.txt"
        fisier.write_text("Orașul are o cetate veche pe deal.\n<|endoftext|>\nSatele sunt mici.\n" * 40, encoding="utf-8")
        setari.update(validari={"romana_mica": str(fisier)}, amprente={str(fisier): sha256(fisier)})
    if setari.get("cale_reglaj") == "__fara_reglaj__":  # rezerva: calea inferenta_kgr1
        setari["cale_reglaj"] = str(tmp_path / "nu_exista.json")
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


def _cautare(c, tmp_path, _, nou):
    intrebare = "Ce are orașul Brașov?"
    gasite = c.cauta(intrebare, 3)
    assert isinstance(gasite, list) and 0 < len(gasite) <= 3
    assert all(isinstance(g, dict) and isinstance(g["text"], str) and isinstance(g["scor"], float) for g in gasite)
    scoruri = [g["scor"] for g in gasite]
    assert scoruri == sorted(scoruri, reverse=True)  # de la cea mai potrivită în jos
    assert c.cauta(intrebare, 3) == gasite and nou().cauta(intrebare, 3) == gasite  # aceeași ordine
    assert len(c.cauta(intrebare, 1)) == 1 and c.cauta(intrebare, 0) == []
    assert c.cauta("?!", 3) == []  # nu crapă la o întrebare fără cuvinte
    assert isinstance(c.statistici(), dict)


def _inferenta(m, tmp_path, _, nou):
    st = m.statistici()
    assert isinstance(st, dict) and {"vocabular", "context", "format"} <= set(st)
    simboluri = [1, 2, 3, 40, 500]
    lg = m.logits(simboluri)
    assert isinstance(lg, list) and len(lg) == st["vocabular"] and all(isinstance(x, float) and math.isfinite(x) for x in lg)
    noi = m.genereaza(simboluri, 4)
    assert isinstance(noi, list) and len(noi) == 4 and all(isinstance(x, int) and 0 <= x < st["vocabular"] for x in noi)
    assert noi[0] == max(range(len(lg)), key=lg.__getitem__)  # greedy: primul e cel mai probabil
    assert m.genereaza(simboluri, 4) == noi and nou().genereaza(simboluri, 4) == noi  # fără întâmplare
    assert m.genereaza(simboluri, 0) == []
    assert len(m.logits(list(range(st["context"] + 5)))) == st["vocabular"]  # peste context nu crapă


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
    "cautare": _cautare,
    "inferenta": _inferenta,
}


def test_fiecare_port_are_verificari():
    assert set(VERIFICARI) == set(CONTRACT_PENTRU_PORT)
