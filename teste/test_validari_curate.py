"""Validările curate (unelte/validari_curate.py): textele scurse în antrenare ies, restul rămân în aceeași ordine."""

from __future__ import annotations

import json

from unelte import validari_curate as vc

SEP = "<|endoftext|>"


def test_regula():
    assert vc.curate([0.1, 0.6, 0.0, 0.49], [0.0, 0.0, 0.3, 0.0]) == [True, False, False, True]


def test_scrie_varianta_curata_langa_cea_veche(tmp_path):
    copiat = "Vulpea și corbul stăteau sub un copac bătrân, departe de sat, într-o zi de vară. " * 4
    nou = "Un text pe care antrenarea nu l-a văzut niciodată, scris acum, cu totul altceva decât acolo."
    al_doilea = "Și încă unul, la fel de nou, despre un munte, o cabană și un câine care latră la lună."
    dosar = tmp_path / "wiki"
    dosar.mkdir()
    veche = dosar / "validare.txt"
    veche.write_text(f"{nou}\n{SEP}\n{copiat}\n{SEP}\n{al_doilea}\n{SEP}\n", encoding="utf-8")
    inainte = veche.read_bytes()
    ant = tmp_path / "ant.txt"
    ant.write_text(f"ceva\n{SEP}\n{copiat}\n{SEP}\n", encoding="utf-8")
    seturi = tmp_path / "seturi.json"
    seturi.write_text(json.dumps({"romana_wikipedia": str(veche)}), encoding="utf-8")
    raport = tmp_path / "raport.json"
    argv = ["--antrenare", str(ant), "--validari", str(seturi), "--raport", str(raport)]
    assert vc.main(argv) == 0
    assert (dosar / "validare_curata.txt").read_text(encoding="utf-8") == f"{nou}\n{SEP}\n{al_doilea}\n{SEP}\n"
    assert veche.read_bytes() == inainte
    r = json.loads(raport.read_text(encoding="utf-8"))["validari"]["romana_wikipedia"]
    assert r["texte"] == 3 and r["texte_curate"] == 2 and len(r["sha256"]) == 64
    assert vc.main(argv) == 1  # nu rescrie fără --rescrie
    assert vc.main(argv + ["--rescrie"]) == 0


def test_fabulele_nu_primesc_varianta_curata():
    assert not any("fabule" in v or "fabule" in c for v, c in vc.DE_CURATAT.items())
