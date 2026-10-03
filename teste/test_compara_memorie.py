"""Comparația cu / fără memorie trece prin Kronos și dă un verdict (pe procesor, în câteva secunde)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from teste.biblioteca_mica import biblioteca_mica
from unelte.compara_memorie import main, verdict

CONFIG = """
[platforma]
nume = "test_memorie"
director_lucru = "lucru"
buget_antrenare_secunde = 0.5
prag_zgomot = 0.005

[paznic]
porturi_modificabile = ["model"]

[porturi.model]
modul = "module.model_gpt:ModelGPT"
setari = {{ n_straturi = 1, n_capete = 2, n_emb = 32, context = 32, lot = 8, dispozitiv = "cpu", memorie = true, adancime_memorie = 4, n_emb_memorie = 8 }}

[porturi.date]
modul = "module.date_mostra:DateMostra"
setari = {{ propozitii = 300 }}

[porturi.examen]
modul = "module.examen_bpb:ExamenBpb"

[porturi.cercetator]
modul = "module.cercetator_aleator:CercetatorAleator"
setari = {{ spatiu = {{ model = {{ lot = [8, 16] }} }} }}

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


def test_comparatia_trece_prin_kronos(tmp_path, monkeypatch, capsys):
    pytest.importorskip("torch")
    monkeypatch.chdir(tmp_path)
    cale = tmp_path / "comparatie.toml"
    cale.write_text(CONFIG.format(biblioteca=Path(biblioteca_mica(tmp_path)).as_posix()), encoding="utf-8")

    assert main(["--config", str(cale), "--seminte", "1", "2"]) == 0

    rezultat = json.loads((tmp_path / "lucru" / "comparatie_memorie.json").read_text(encoding="utf-8"))
    assert [p["samanta"] for p in rezultat["perechi"]] == [1, 2]
    for p in rezultat["perechi"]:
        assert p["fara"]["parametri_memorie"] == 0 and p["cu"]["parametri_memorie"] > 0
        assert p["castig"] == pytest.approx(p["fara"]["scor"] - p["cu"]["scor"])
    iesire = capsys.readouterr().out
    assert "Rezultatul comparației" in iesire and "Verdict:" in iesire

    # Totul a trecut prin Kronos și a intrat în jurnal, pe o linie separată.
    linii = (tmp_path / "lucru" / "jurnal" / "experimente.jsonl").read_text(encoding="utf-8").splitlines()
    fise = [json.loads(rand) for rand in linii]
    assert len(fise) == 4 and {f["linie"] for f in fise} == {"test_memorie_comparatie"}
    assert [f["setari"]["model"]["memorie"] for f in fise] == [False, True, True, False]  # ordinea alternează
    assert all(f["setari"]["model"]["lot"] == 8 for f in fise)  # aceeași rețetă de fiecare dată


@pytest.mark.parametrize(
    "diferente,inceput",
    [
        ([0.02, 0.03, 0.01], "Memoria AJUTĂ"),
        ([-0.02, -0.03], "Memoria STRICĂ"),
        ([0.02, -0.01, 0.03], "NEHOTĂRÂT"),
        ([0.001, 0.002, 0.004], "NEHOTĂRÂT"),
        ([0.05], "O singură pereche"),
    ],
)
def test_verdictul(diferente, inceput):
    assert verdict(diferente, 0.005).startswith(inceput)
