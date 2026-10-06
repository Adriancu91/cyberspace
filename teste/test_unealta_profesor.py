"""Testul de calitate al profesorului: elevul scrie, profesorul (aici, unul de probă) scrie și notează; textele merg în
lucru/profesor/, iar în jurnal se scriu doar numere."""

from __future__ import annotations

import json

import pytest

from module import profesor_qwen
from teste.test_bucla_cinstita import config_mic, fise
from unelte import antrenare_lunga, test_profesor


def test_inceputul_dat_elevului():
    assert test_profesor.prima_propozitie("Once upon a time, Tom ran. He was happy.") == "Once upon a time, Tom ran."
    assert test_profesor.prima_propozitie('Lily said, "Hi!" Then she left.') == 'Lily said, "Hi!"'
    fara_punct = "a very long beginning with no full stop anywhere in it at all"
    assert test_profesor.prima_propozitie(fara_punct) == "a very long beginning with no full stop"


def test_povestea_elevului_se_taie_la_propozitie():
    assert test_profesor.taie_la_propozitie("Tom ran. He saw a dog<|endoftext|>Once") == "Tom ran."
    assert test_profesor.taie_la_propozitie('Tom ran. He said "hi." And then the') == 'Tom ran. He said "hi."'
    assert test_profesor.taie_la_propozitie("Tom ran. He was happy.\n") == "Tom ran. He was happy."
    assert test_profesor.taie_la_propozitie("no end at all") == "no end at all"


def test_alegerea_si_numerele():
    text = "\n<|endoftext|>\n".join(f"Story {i}." for i in range(30))
    alese = test_profesor.alege_povesti(text, 5)
    assert alese == test_profesor.alege_povesti(text, 5) and len(set(alese)) == 5  # aceleași de fiecare dată
    assert alese == sorted(alese, key=lambda p: int(p.split()[1][:-1]))  # în ordinea din text
    assert test_profesor.distributie([7, 7, 9, None]) == {**{str(n): 0 for n in range(1, 11)}, "7": 2, "9": 1}
    assert test_profesor.medie([7, 8, None]) == 7.5 and test_profesor.medie([None]) is None


def test_textele_in_lucru_si_doar_numere_in_jurnal(tmp_path, monkeypatch, capsys):
    pytest.importorskip("torch")
    monkeypatch.chdir(tmp_path)
    cale = config_mic(tmp_path, "antrenare_lunga_3", model=', cale_stare = "lucru/antrenare_lunga_3/gpt.pt"', spatiu="lot = [4]")
    assert antrenare_lunga.main(["--config", str(cale), "--ore", "1", "--pauza", "0", "--racire", "0", "--lungime", "20"]) == 0

    def raspunsuri(self, conversatii, max_simboluri, cu_intamplare):  # profesorul de probă: răspunde pe loc
        self.simboluri_generate += 10 * len(conversatii)
        self.secunde += 0.01
        if cu_intamplare:
            return [f"A short story number {k}. It is nice." for k in range(len(conversatii))]
        return ["GRADE: 7\nREASON: Fine." for _ in conversatii]

    monkeypatch.setattr(profesor_qwen.ProfesorQwen, "pregateste", lambda self: None)
    monkeypatch.setattr(profesor_qwen.ProfesorQwen, "_raspunsuri", raspunsuri)
    argumente = ["--config-elev", str(cale), "--elev-linie", "antrenare_lunga_3", "--povesti", "4", "--elev", "2",
                 "--lot", "3", "--validare", str(tmp_path / "tinystories" / "validare.txt")]
    assert test_profesor.main(argumente) == 0

    dosar = next((tmp_path / "lucru" / "profesor").glob("test_*"))
    citeste = lambda nume: [json.loads(r) for r in (dosar / nume).read_text(encoding="utf-8").splitlines()]  # noqa: E731
    profesor, elev, originale = citeste("povesti_profesor.jsonl"), citeste("povesti_elev.jsonl"), citeste("povesti_tinystories.jsonl")
    assert len(profesor) == 4 and profesor[0]["subiect"] == "snow" and profesor[0]["nota"] == 7
    assert profesor[0]["fapt"] == "Water freezes into ice when it is very cold."
    assert len(elev) == 2 and all(e["poveste"].startswith(e["inceput"]) and e["nota"] == 7 for e in elev)
    assert len(originale) == 2 and all(o["poveste"] and o["nota"] == 7 for o in originale)

    fisa = [f for f in fise(tmp_path) if f["linie"] == "profesor"][-1]
    assert fisa["decizie"] == "masurat" and fisa["module"]["elev"]["linie"] == "antrenare_lunga_3"
    assert fisa["scoruri"]["nota_medie_profesor"] == fisa["scoruri"]["nota_medie_elev"] == 7
    assert fisa["distributie_note_profesor"]["7"] == 4 and fisa["distributie_note_elev"]["7"] == 2
    numere = [*fisa["scoruri"].values(), *(v for k, d in fisa.items() if k.startswith("distributie") for v in d.values())]
    assert all(v is None or isinstance(v, (int, float)) for v in numere)  # rezultatele: doar numere
    assert "A short story" not in json.dumps(fisa) and "Fine." not in json.dumps(fisa)  # niciun text generat în jurnal
    assert "Media notelor" in capsys.readouterr().out
