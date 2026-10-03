"""Testul plasei în două runde: trece prin Kronos, plasa primește doar câștigul și e păstrată între runde."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from teste.biblioteca_mica import biblioteca_mica
from teste.tinystories_mic import scrie_surse
from unelte.compara_plasa import main, verdict

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

    assert main(["--config", str(cale), "--seminte", "1", "2"]) == 0

    rezultat = json.loads(next((tmp_path / "lucru").glob("comparatie_plasa_*.json")).read_text(encoding="utf-8"))
    assert len(rezultat["rezultate"]) == 8
    cu = [r for r in rezultat["rezultate"] if r["plasa_pornita"]]
    fara = [r for r in rezultat["rezultate"] if not r["plasa_pornita"]]
    assert all(r["plasa"] is None for r in fara) and all(r["plasa"] is not None for r in cu)
    for r in cu:  # câștigul primit de plasă = scor fără plasă − scor cu plasă, pe aceeași rundă și sămânță
        pereche = next(f for f in fara if (f["samanta"], f["runda"]) == (r["samanta"], r["runda"]))
        assert r["castig_primit"] == pytest.approx(pereche["scor"] - r["scor"])
    for samanta in (1, 2):  # plasa e păstrată între rundele aceleiași semințe
        r1, r2 = (next(r for r in cu if (r["samanta"], r["runda"]) == (samanta, k)) for k in (1, 2))
        assert r1["plasa"]["experimente"] == 1 and r2["plasa"]["experimente"] == 2
    assert len(list((tmp_path / "lucru" / "plase").glob("*.json"))) == 2  # o plasă pentru fiecare sămânță

    fise = [json.loads(rand) for rand in (tmp_path / "lucru" / "jurnal" / "experimente.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(fise) == 8 and len({f["linie"] for f in fise}) == 4  # o linie pentru fiecare rundă și sămânță
    assert all("plasa" in f["dupa_examen"] for f in fise if f["setari"]["model"]["plasa"])  # starea plasei, în jurnal
    assert "Verdict:" in capsys.readouterr().out


@pytest.mark.parametrize("diferenta,inceput", [(-0.02, "Plasa a AJUTAT"), (0.02, "Plasa a ÎNCURCAT"), (0.001, "NEHOTĂRÂT")])
def test_verdictul(diferenta, inceput):
    assert verdict(diferenta, 0.005, 3).startswith(inceput)
    assert "orientativ" in verdict(diferenta, 0.005, 2)
