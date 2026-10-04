"""Testul în trei trepte: treptele trec prin Kronos, pe bucăți, iar modelele continuă de la o treaptă la alta."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from teste.biblioteca_mica import biblioteca_mica
from teste.tinystories_mic import scrie_surse
from unelte.trepte_plasa_mare import _plasa_intre_runde, cu_samanta, main, verdict

CONFIG = """
[platforma]
nume = "test_{varianta}"
director_lucru = "lucru"
buget_antrenare_secunde = 0.3
prag_zgomot = 0.005

[paznic]
porturi_modificabile = ["model"]

[porturi.model]
modul = "{modul}"
setari = {{ n_straturi = 1, n_capete = 2, n_emb = 32, context = 16, lot = 4, dispozitiv = "cpu", tokenizer = "bpe", cale_tokenizer = "{tokenizer}", cale_stare = "{stare}", director_cache = "{cache}"{extra} }}

[porturi.date]
modul = "module.date_tinystories:DateTinyStories"
setari = {{ director = "{director}" }}

[porturi.examen]
modul = "module.examen_bpb:ExamenBpb"

[porturi.cercetator]
modul = "module.cercetator_aleator:CercetatorAleator"
setari = {{ spatiu = {{ model = {{ lot = [4, 8] }} }} }}

[porturi.profesor]
modul = "module.jucarii:ProfesorGol"

[porturi.rulare]
modul = "module.rulare_locala:RulareLocala"

[porturi.stocare]
modul = "module.stocare_disc:StocareDisc"
setari = {{ director = "lucru/stocare" }}

[porturi.interfata]
modul = "module.interfata_consola:InterfataConsola"
setari = {{ tacut = true }}

[porturi.traducere]
modul = "module.jucarii:TraducereIdentitate"

[porturi.memorie]
modul = "module.memorie_ierarhica:MemorieIerarhica"
setari = {{ cale = "{biblioteca}", nivele = 6, fara_cuvinte_de_legatura = true, sens_dupa_context = true }}
"""


def test_trei_trepte_cap_coada(tmp_path, monkeypatch, capsys):
    pytest.importorskip("torch")
    pytest.importorskip("pyarrow")
    from module.tokenizer_bpe import antreneaza_bpe
    from teste.wikipedia_mic import scrie_wikipedia

    monkeypatch.chdir(tmp_path)
    r1 = scrie_surse(tmp_path)
    tokenizer = tmp_path / "bpe.json"
    antreneaza_bpe((tmp_path / "train.txt").read_text(encoding="utf-8"), 300).salveaza(tokenizer)
    comune = dict(tokenizer=tokenizer.as_posix(), cache=(tmp_path / "cache").as_posix(),
                  director=Path(r1["director"]).as_posix(), biblioteca=Path(biblioteca_mica(tmp_path)).as_posix())
    argumente = []
    for varianta, modul, extra in (("gpt", "module.model_continuu:ModelGPTContinuu", ""),
                                   ("plasa", "module.model_plasa_mare:ModelPlasaMare", ", n_ascuns_nod = 8, noduri_libere = 2")):
        cale = tmp_path / f"{varianta}.toml"
        cale.write_text(CONFIG.format(varianta=varianta, modul=modul, extra=extra,
                                      stare=(tmp_path / "stari" / f"{varianta}.pt").as_posix(), **comune), encoding="utf-8")
        argumente += [f"--config-{varianta}", str(cale)]
    trepte = {
        1: {"minute": 0.01, "text": "mic", "intrebare": "învață?", "date": {"modul": "module.date_tinystories:DateTinyStories", "setari": r1}},
        2: {"minute": 0.02, "text": "mic 2", "intrebare": "ține pasul?", "date": {"modul": "module.date_tinystories:DateTinyStories",
            "setari": {**r1, "director": str(tmp_path / "r2"), "decalaj_antrenare_mo": 0.002, "decalaj_validare_mo": 0.001,
                       "fara_povestile_din": [r1["director"]]}}},
        3: {"minute": 0.01, "text": "wiki", "intrebare": "scade?", "date": {"modul": "module.date_wikipedia:DateWikipedia",
            "setari": scrie_wikipedia(tmp_path)}},
    }
    assert main(argumente + ["--trepte", "1", "2", "3", "--minute-pe-bucata", "0.01", "--pauza", "0", "--racire", "0",
                             "--iesire", str(tmp_path / "rezultate")], trepte=trepte) == 0

    rezultate = {t: json.loads((tmp_path / "rezultate" / f"treapta_{t}.json").read_text(encoding="utf-8")) for t in (1, 2, 3)}
    assert [len(rezultate[t]["plasa"]) for t in (1, 2, 3)] == [1, 2, 1]  # bucăți de câte 0,01 minute
    assert all(len(rezultate[t]["gpt"]) == len(rezultate[t]["plasa"]) for t in (1, 2, 3))
    totaluri = [b["pasi_total"] for t in (1, 2, 3) for b in rezultate[t]["plasa"]]
    assert totaluri == sorted(totaluri) and len(set(totaluri)) == len(totaluri)  # plasa continuă, nu pornește de la zero
    gpt = [b["pasi_total"] for t in (1, 2, 3) for b in rezultate[t]["gpt"]]
    assert gpt == sorted(gpt) and len(set(gpt)) == len(gpt)
    assert all(rezultate[t]["verdict"] for t in (1, 2, 3))
    assert (tmp_path / "stari" / "plasa_s0.pt").exists() and (tmp_path / "stari" / "gpt_s0.pt").exists()
    assert (tmp_path / "stari" / "plasa_s0.plasa.json").exists()  # plasa, ca text, după fiecare examen
    fise = [json.loads(r) for r in (tmp_path / "lucru" / "jurnal" / "experimente.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(fise) == 8 and all(f["decizie"] != "anulat" for f in fise)
    assert "Verdict, treapta 3" in capsys.readouterr().out


def test_fiecare_samanta_are_starea_ei():
    assert cu_samanta("lucru/m3_mare/plasa_mare.pt", 1).replace("\\", "/") == "lucru/m3_mare/plasa_mare_s1.pt"


def _punct(minut, scor, rezervata=4000):
    return {"minut": minut, "scor": scor, "memorie_rezervata_mb": rezervata}


@pytest.mark.parametrize(
    "treapta,plasa,gpt,inceput",
    [
        (1, [_punct(10, 2.0), _punct(20, 1.9)], [], "DA: funcționează și învață"),
        (1, [_punct(10, 2.0), _punct(20, 1.998)], [], "PARȚIAL"),
        (1, [_punct(10, 2.0), _punct(20, 2.1)], [], "NU: scorul nu scade"),
        (1, [_punct(10, 2.0, 6000), _punct(20, 1.9)], [], "NU: memoria video"),
        (2, [_punct(10, 1.5), _punct(20, 1.4)], [_punct(10, 1.45), _punct(20, 1.402)], "DA: ține pasul"),
        (2, [_punct(10, 1.5), _punct(20, 1.4)], [_punct(10, 1.45), _punct(20, 1.3)], "NU: rămâne în urmă"),
        (2, [_punct(10, 1.5), _punct(20, 1.3)], [_punct(10, 1.45), _punct(20, 1.4)], "DA, chiar o întrece"),
        (3, [_punct(10, 2.0), _punct(20, 1.9), _punct(30, 1.85)], [], "DA: scorul scade la fiecare"),
        (3, [_punct(10, 2.0), _punct(20, 1.9), _punct(30, 1.95)], [], "PARȚIAL"),
        (3, [_punct(10, 2.0), _punct(20, 2.0), _punct(30, 2.001)], [], "NU"),
    ],
)
def test_verdictul_treptelor(treapta, plasa, gpt, inceput):
    assert verdict(treapta, plasa, gpt, 0.005, 5500).startswith(inceput)


def test_plasa_intre_runde():
    plasa = [
        {"legaturi_la_start": [{"de_la": "a", "la": "b", "tarie": 0.1, "folosire": 0.2}, {"de_la": "b", "la": "c", "tarie": 0.1, "folosire": 0.0}],
         "legaturi_dupa": {"a → b": 0.3}, "legaturi_nascute": ["c → a"], "ajutoare_la_start": [], "ajutoare_dupa": [],
         "noduri_alocate": ["liber1 → a (preia 50%: x)"]},
        {"legaturi_la_start": [], "legaturi_dupa": {"a → b": 0.5, "c → a": 0.1}, "legaturi_nascute": [], "ajutoare_la_start": [],
         "ajutoare_dupa": [{"nod": "liber1", "ajuta": "a", "raft": "a"}], "noduri_alocate": []},
    ]
    intre = _plasa_intre_runde(plasa)
    assert intre["legaturi_la_inceput"] == 2 and intre["folosite_in_prima_bucata"] == 1
    assert intre["taria_la_final"] == {"a → b": 0.5, "c → a": 0.1} and intre["nascute_in_treapta"] == ["c → a"]
    assert intre["alocate_in_treapta"] == ["liber1 → a (preia 50%: x)"]
