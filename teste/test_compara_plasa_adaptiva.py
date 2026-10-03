"""Comparația M3: cele trei variante trec prin Kronos cu aceeași rețetă și același număr de pași; verdictul e cinstit."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from teste.biblioteca_mica import biblioteca_mica
from teste.tinystories_mic import scrie_surse
from unelte.compara_plasa_adaptiva import main, rezultatul, verdict

RETETA = 'n_straturi = 1, n_capete = 2, n_emb = 32, context = 16, lot = 4, dispozitiv = "cpu", tokenizer = "bpe", cale_tokenizer = "{tokenizer}"'
MODELE = {
    "simplu": ("module.model_gpt:ModelGPT", ""),
    "plasa5": ("module.model_plasa:ModelPlasa", ", n_ascuns_nod = 8, plasa = true"),
    "adaptiva": ("module.model_plasa_adaptiva:ModelPlasaAdaptiva", ", n_ascuns_nod = 8, noduri_libere = 2"),
}
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
setari = {{ {reteta}{extra} }}

[porturi.date]
modul = "module.date_tinystories:DateTinyStories"
setari = {{ director = "{director}", megaocteti = 0.004, procent_validare = 0.25, url_antrenare = "{url_antrenare}", url_validare = "{url_validare}" }}

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


def _configurari(tmp_path: Path, reteta: str = RETETA) -> list[str]:
    from module.tokenizer_bpe import antreneaza_bpe

    surse = scrie_surse(tmp_path)
    tokenizer = tmp_path / "bpe.json"
    antreneaza_bpe((tmp_path / "train.txt").read_text(encoding="utf-8"), 300).salveaza(tokenizer)
    argumente = []
    for varianta, (modul, extra) in MODELE.items():
        cale = tmp_path / f"{varianta}.toml"
        cale.write_text(CONFIG.format(
            varianta=varianta, modul=modul, reteta=reteta.format(tokenizer=tokenizer.as_posix()), extra=extra,
            director=Path(surse["director"]).as_posix(), url_antrenare=surse["url_antrenare"],
            url_validare=surse["url_validare"], biblioteca=Path(biblioteca_mica(tmp_path)).as_posix(),
        ), encoding="utf-8")
        argumente += [f"--config-{varianta}", str(cale)]
    return argumente


def test_cele_trei_variante_la_acelasi_numar_de_pasi(tmp_path, monkeypatch, capsys):
    pytest.importorskip("torch")
    monkeypatch.chdir(tmp_path)
    argumente = _configurari(tmp_path)
    assert main(argumente + ["--seminte", "1", "2", "--pasi", "3", "--pauza", "0", "--racire", "0"]) == 0

    rezultat = json.loads(next((tmp_path / "lucru").glob("comparatie_m3_*.json")).read_text(encoding="utf-8"))
    randuri = rezultat["randuri"]
    assert [r["samanta"] for r in randuri] == [1, 2]
    for r in randuri:
        assert all(r[v]["pasi"] == 3 and r[v]["pasi_pe_secunda"] for v in ("simplu", "plasa5", "adaptiva"))
        assert r["simplu"]["legaturi_nascute"] is None and r["simplu"]["noduri_alocate"] is None  # GPT-ul n-are plasă
        assert isinstance(r["plasa5"]["legaturi_nascute"], list) and r["plasa5"]["noduri_alocate"] is None
        assert isinstance(r["adaptiva"]["legaturi_nascute"], list) and isinstance(r["adaptiva"]["noduri_alocate"], list)
    assert rezultat["verdict_fata_de_simplu"] and rezultat["verdict_fata_de_plasa5"]
    assert len(list((tmp_path / "lucru" / "plase").glob("m3_*.json"))) == 4  # fiecare plasă, goală, în fișierul ei

    jurnal = (tmp_path / "lucru" / "jurnal" / "experimente.jsonl").read_text(encoding="utf-8").splitlines()
    fise = [json.loads(rand) for rand in jurnal]
    assert len(fise) == 6 and len({f["linie"] for f in fise}) == 6
    assert all(f["setari"]["model"]["pasi_max"] == 3 for f in fise)
    adaptive = [f for f in fise if f["linie"].startswith("test_adaptiva")]
    assert all("noduri" in f["dupa_examen"] and "plasa" in f["dupa_examen"] for f in adaptive)  # alocările, în jurnal
    assert "Plasa adaptivă față de GPT-ul simplu:" in capsys.readouterr().out


def test_retete_diferite_nu_pornesc(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    argumente = _configurari(tmp_path)
    simplu = Path(argumente[1])
    simplu.write_text(simplu.read_text(encoding="utf-8").replace("lot = 4", "lot = 8"), encoding="utf-8")
    assert main(argumente + ["--seminte", "1", "--pasi", "3"]) == 1
    assert "Rețetele nu sunt la fel (lot)" in capsys.readouterr().out
    assert not (tmp_path / "lucru" / "jurnal").exists()  # nimic rulat


def _rand(samanta, simplu, plasa5, adaptiva, pasi=(100, 100, 100)):
    return {
        "samanta": samanta,
        **{v: {"scor": s, "pasi": p} for v, s, p in zip(("simplu", "plasa5", "adaptiva"), (simplu, plasa5, adaptiva), pasi)},
    }


@pytest.mark.parametrize(
    "randuri,inceput",
    [
        ([_rand(0, 1.0, 1.0, 0.98, pasi=(100, 100, 90))], "NECONCLUDENT: pași diferiți"),
        ([_rand(s, 1.0, 1.0, 0.99) for s in range(3)], "MARE (merge)"),
        ([_rand(s, 1.0, 1.0, 1.01) for s in range(3)], "MARE, dar în rău"),
        ([_rand(0, 1.0, 1.0, 0.998), _rand(1, 1.0, 1.0, 0.997)], "MICĂ (noroc)"),
        ([_rand(0, 1.0, 1.0, 0.98), _rand(1, 1.0, 1.0, 1.04)], "NECONCLUDENT: diferența nu are"),
    ],
)
def test_verdictul(randuri, inceput):
    assert verdict(randuri, 100, 0.005, "simplu").startswith(inceput)


def test_verdictul_spune_daca_diferenta_mica_are_acelasi_semn():
    assert "același sens" in verdict([_rand(0, 1.0, 1.0, 0.998), _rand(1, 1.0, 1.0, 0.997)], 100, 0.005, "simplu")
    assert "diferă" in verdict([_rand(0, 1.0, 1.0, 0.998), _rand(1, 1.0, 1.0, 1.001)], 100, 0.005, "simplu")
    assert verdict([_rand(0, 1.0, 1.0, 0.98)], 90, 0.005, "simplu").startswith("NECONCLUDENT: pași diferiți")


def test_rezultatul_ia_din_fisa_ce_a_hotarat_plasa():
    fisa = {
        "id": 7, "scoruri": {"val_bpb": 0.95}, "consum": {"durata_antrenare_secunde": 300, "memorie_gpu_max_mb": 350},
        "statistici_antrenare": {"pasi": 25_000, "secunde_bucla": 250, "noduri": {"active": 34}},
        "dupa_examen": {
            "plasa": {"nascute_acum": [{"de_la": "noun.person", "la": "verb.communication"}], "lista": []},
            "noduri": {"alocate": [{"nod": "liber1", "ajuta": "noun.person", "preia": 0.5, "exemple": ["tim", "mom"]}]},
        },
    }
    r = rezultatul(fisa, "val_bpb")
    assert r["scor"] == 0.95 and r["pasi_pe_secunda"] == 100.0 and r["noduri_active"] == 34
    assert r["legaturi_nascute"] == ["noun.person → verb.communication"]
    assert r["noduri_alocate"] == ["liber1 → noun.person (preia 50%: tim, mom)"]
