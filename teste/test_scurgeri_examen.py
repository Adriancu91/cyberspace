"""Scurgeri în examen (unelte/scurgeri_examen.py): bucățile identice dintre validări și antrenare."""

from __future__ import annotations

import json

import numpy as np
import pytest

from unelte import scurgeri_examen as se

SEP = "<|endoftext|>"


def test_amprentele_sunt_ale_bucatilor_nu_ale_pozitiei():
    a = se.amprente(se.coduri("abcdeXabcde"), 5)
    assert len(a) == 7 and a[0] == a[6] and len(set(a.tolist())) == 6
    assert len(se.amprente(se.coduri("abc"), 5)) == 0
    assert se.amprente(se.coduri("ăîșțâ"), 5)[0] != se.amprente(se.coduri("aisța"), 5)[0]


def test_alte_seturi_in_locul_validarilor(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    nou = tmp_path / "nou.txt"
    nou.write_text(f"un articol scris după 12 octombrie, pe care nu-l are nimeni\n{SEP}\n", encoding="utf-8")
    ant = tmp_path / "ant.txt"
    ant.write_text("cu totul altceva, deloc la fel", encoding="utf-8")
    seturi = tmp_path / "seturi.json"
    seturi.write_text(json.dumps({"wikipedia_ro_nou": str(nou)}), encoding="utf-8")
    assert se.main(["--lungime", "10", "--antrenare", str(ant), "--validari", str(seturi)]) == 0
    raport = json.loads(next((tmp_path / "lucru" / "scurgeri_examen").glob("*.json")).read_text(encoding="utf-8"))
    assert list(raport["validari"]) == ["wikipedia_ro_nou"] and raport["validari"]["wikipedia_ro_nou"]["bucati_gasite"] == 0


def test_amprentele_compuse_sunt_cele_ale_bucatilor_lungi():
    litere = se.coduri("Vulpea și corbul stăteau sub un copac bătrân, departe de sat, într-o zi de vară." * 3)
    assert (se.compune(se.amprente(litere, 10), 10, 4) == se.amprente(litere, 40)).all()
    assert len(se.compune(se.amprente(se.coduri("abc" * 5), 10), 10, 4)) == 0


def test_mai_multe_lungimi_intr_o_singura_trecere(tmp_path):
    comun = "Once upon a time, there was a little girl named Lily. "
    copiat = comun + "She found a shiny red ball under the old oak tree near her small house by the river."
    tipar = comun + "Something entirely different happened next, and nobody had ever written this before."
    antrenare = tmp_path / "antrenare.txt"
    antrenare.write_text(f"{copiat}\n{SEP}\n", encoding="utf-8")
    r = se.cauta_lungimi({"v": [copiat, tipar]}, [antrenare], [20, 60], litere_pe_bucata=41, spune=lambda *a, **k: None)
    assert r[20]["v"]["acoperire_pe_text"][0] == 1.0 and r[60]["v"]["acoperire_pe_text"][0] == 1.0
    assert 0 < r[20]["v"]["acoperire_pe_text"][1] < 1 and r[60]["v"]["acoperire_pe_text"][1] == 0.0  # tiparul scurt nu e copiere
    with pytest.raises(ValueError):
        se.cauta_lungimi({"v": [copiat]}, [antrenare], [20, 50])


def test_bucatile_de_antrenare_nu_pierd_nicio_fereastra(tmp_path):
    fisier = tmp_path / "a.txt"
    text = "".join(chr(ord("a") + i % 26) for i in range(1000))
    fisier.write_text(text, encoding="utf-8")
    vazute = set()
    for b in se.bucati_antrenare(fisier, 97, 10):
        vazute.update(se.amprente(b, 10).tolist())
    assert vazute == set(se.amprente(se.coduri(text), 10).tolist())


def test_cauta_numara_bucatile_literele_si_textele_copiate(tmp_path):
    copiat = "Vulpea și corbul stăteau sub un copac bătrân, departe de sat, într-o zi de vară."
    nou = "Un text pe care antrenarea nu l-a văzut niciodată, cu totul altceva decât acolo."
    jumatate = "Ursul doarme iarna. " + copiat[:40] + " apoi altceva care nu exista deloc în date."
    antrenare = tmp_path / "antrenare.txt"
    antrenare.write_text(f"ceva înainte\n{SEP}\n{copiat}\n{SEP}\nfinal", encoding="utf-8")
    r = se.cauta({"v": [copiat, nou, jumatate]}, [antrenare], 20, litere_pe_bucata=37, spune=lambda *a, **k: None)["v"]
    assert r["texte"] == 3 and r["texte_aproape_copiate"] == round(1 / 3, 4) and r["exemple_copiate"] == [copiat]
    ferestre = sum(len(t) - 19 for t in (copiat, nou, jumatate))
    assert r["bucati_gasite"] == round((len(copiat) - 19 + 40 - 19) / ferestre, 4)
    assert r["litere_acoperite"] == round((len(copiat) + 40) / sum(map(len, (copiat, nou, jumatate))), 4)


def test_rularea_scrie_raportul(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    val = tmp_path / "val.txt"
    val.write_text(f"primul text din validare, destul de lung ca să conteze aici\n{SEP}\nal doilea text, altul\n{SEP}\n",
                   encoding="utf-8")
    ant = tmp_path / "ant.txt"
    ant.write_text("primul text din validare, destul de lung ca să conteze aici", encoding="utf-8")
    monkeypatch.setattr(se, "VALIDARI", {"romana_wikipedia": str(val)})
    monkeypatch.setattr(se, "OFICIAL", {})
    assert se.main(["--lungime", "10", "--antrenare", str(ant)]) == 0
    raport = json.loads(next((tmp_path / "lucru" / "scurgeri_examen").glob("*.json")).read_text(encoding="utf-8"))
    r = raport["validari"]["romana_wikipedia"]
    assert r["texte"] == 2 and r["texte_aproape_copiate"] == 0.5 and 0 < r["litere_acoperite"] < 1
    assert "romana_wikipedia" in capsys.readouterr().out
    assert np.isclose(r["bucati_gasite"], (59 - 9) / (59 - 9 + 21 - 9), atol=1e-4)
