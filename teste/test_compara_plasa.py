"""Testul plasei în două runde: trece prin Kronos, plasa primește doar câștigul și e păstrată între runde."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from teste.biblioteca_mica import biblioteca_mica
from teste.tinystories_mic import scrie_surse
from unelte.compara_plasa import asteapta_racirea, main, verdict

CONFIG = """
[platforma]
nume = "test_plasa"
director_lucru = "lucru"
buget_antrenare_secunde = 0.3
prag_zgomot = 0.005

[paznic]
porturi_modificabile = ["model"]

[porturi.model]
modul = "module.model_plasa:ModelPlasa"
setari = {{ n_straturi = 1, n_capete = 2, n_emb = 32, context = 16, lot = 4, dispozitiv = "cpu", n_ascuns_nod = 8, tokenizer = "bpe", cale_tokenizer = "{tokenizer}", plasa = true }}

[porturi.date]
modul = "module.date_tinystories:DateTinyStories"
setari = {{ director = "{director}", megaocteti = 0.004, procent_validare = 0.25, url_antrenare = "{url_antrenare}", url_validare = "{url_validare}" }}

[porturi.examen]
modul = "module.examen_bpb:ExamenBpb"

[porturi.cercetator]
modul = "module.cercetator_aleator:CercetatorAleator"
setari = {{ spatiu = {{ model = {{ n_ascuns_nod = [8, 16] }} }} }}

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
setari = {{ cale = "{biblioteca}", nivele = 6 }}
"""


def test_doua_runde_cu_plasa_pastrata(tmp_path, monkeypatch, capsys):
    pytest.importorskip("torch")
    from module.tokenizer_bpe import antreneaza_bpe

    monkeypatch.chdir(tmp_path)
    surse = scrie_surse(tmp_path)
    tokenizer = tmp_path / "bpe.json"
    antreneaza_bpe((tmp_path / "train.txt").read_text(encoding="utf-8"), 300).salveaza(tokenizer)
    cale = tmp_path / "plasa.toml"
    cale.write_text(CONFIG.format(
        tokenizer=tokenizer.as_posix(), director=Path(surse["director"]).as_posix(),
        url_antrenare=surse["url_antrenare"], url_validare=surse["url_validare"],
        biblioteca=Path(biblioteca_mica(tmp_path)).as_posix(),
    ), encoding="utf-8")

    assert main(["--config", str(cale), "--seminte", "1", "2", "--pasi", "3", "--racire", "0"]) == 0

    rezultat = json.loads(next((tmp_path / "lucru").glob("comparatie_plasa_*.json")).read_text(encoding="utf-8"))
    serii = rezultat["serii"]
    assert [s["samanta"] for s in serii] == [1, 2]
    for s in serii:
        rulari = [s[v][str(r)] for v in ("fara", "cu") for r in (1, 2)]  # JSON: cheile rundelor devin text
        assert all(r["pasi"] == 3 for r in rulari)  # toate rulările se opresc exact la același număr de pași
        assert s["fara"]["1"]["plasa"] is None and s["cu"]["1"]["plasa"] is not None
        for runda in ("1", "2"):  # câștigul primit de plasă = scor fără plasă − scor cu plasă, aceeași rundă și sămânță
            assert s["cu"][runda]["castig_primit"] == pytest.approx(s["fara"][runda]["scor"] - s["cu"][runda]["scor"])
        assert s["cu"]["1"]["plasa"]["experimente"] == 1 and s["cu"]["2"]["plasa"]["experimente"] == 2  # aceeași plasă
    # În 3 pași nu se poate naște nicio legătură: verdictul trebuie să refuze concluziile.
    assert rezultat["verdict"].startswith("NECONCLUDENT: plasa goală la runda 2")
    assert len(list((tmp_path / "lucru" / "plase").glob("*.json"))) == 2  # o plasă pentru fiecare sămânță

    fise = [json.loads(rand) for rand in (tmp_path / "lucru" / "jurnal" / "experimente.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(fise) == 8 and len({f["linie"] for f in fise}) == 4  # o linie pentru fiecare rundă și sămânță
    assert all(f["setari"]["model"]["pasi_max"] == 3 for f in fise)
    assert all("plasa" in f["dupa_examen"] for f in fise if f["setari"]["model"]["plasa"])  # starea plasei, în jurnal
    assert "Verdict: NECONCLUDENT" in capsys.readouterr().out


def _serie(samanta, fara, cu, pasi=(100, 100, 100, 100), legaturi_r2=3):
    return {
        "samanta": samanta,
        "fara": {1: {"scor": fara[0], "pasi": pasi[0]}, 2: {"scor": fara[1], "pasi": pasi[1]}},
        "cu": {
            1: {"scor": cu[0], "pasi": pasi[2], "legaturi_la_start": 0},
            2: {"scor": cu[1], "pasi": pasi[3], "legaturi_la_start": legaturi_r2},
        },
    }


@pytest.mark.parametrize(
    "serii,inceput",
    [
        ([_serie(0, (1.0, 1.0), (1.0, 0.98), pasi=(100, 100, 100, 90))], "NECONCLUDENT: pași diferiți"),
        ([_serie(0, (1.0, 1.0), (1.0, 0.98)), _serie(1, (1.0, 1.0), (1.0, 0.98), legaturi_r2=0)],
         "NECONCLUDENT: plasa goală la runda 2"),
        ([_serie(s, (1.0, 1.01), (1.0, 0.99)) for s in range(3)], "MARE (merge)"),
        ([_serie(s, (1.0, 0.99), (1.0, 1.01)) for s in range(3)], "MARE, dar în rău"),
        ([_serie(0, (1.0, 1.0), (1.0, 1.001)), _serie(1, (1.0, 1.0), (1.0, 0.998))], "MICĂ (noroc)"),
        ([_serie(0, (1.0, 1.0), (1.0, 0.98)), _serie(1, (1.0, 1.0), (1.0, 1.04))], "NECONCLUDENT: efectul nu are"),
    ],
)
def test_verdictul(serii, inceput):
    assert verdict(serii, 100, 0.005).startswith(inceput)


def test_pasii_altii_decat_cei_ceruti_sunt_neconcludenti():
    assert verdict([_serie(0, (1.0, 1.0), (1.0, 0.98), pasi=(90, 90, 90, 90))], 100, 0.005).startswith(
        "NECONCLUDENT: pași diferiți"
    )


def test_pauza_de_racire_asteapta_pana_la_tinta():
    temperaturi = iter([80.0, 76.0, 69.0])
    pauze = []
    asteapta_racirea(lambda: next(temperaturi), 70, asteapta=pauze.append)
    assert pauze == [10, 10]  # 80 → 76 → 69: două pauze
    pauze.clear()
    asteapta_racirea(lambda: 90.0, 0, asteapta=pauze.append)  # 0 = fără pauze
    asteapta_racirea(lambda: None, 70, asteapta=pauze.append)  # temperatura necunoscută: nu aștept
    assert pauze == []
