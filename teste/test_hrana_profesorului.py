"""Hrana elevului: povești cu fapte, păstrate doar cele bune (nota ≥ 8, faptul o singură dată); fără modelul mare."""

from __future__ import annotations

import json

from module import profesor_qwen
from module.profesor_qwen import FAPTE, PERSONAJE, SUBIECTE
from unelte import genereaza_fapte


def test_cererile_trec_prin_subiecte_apoi_stiluri_apoi_personaje():
    assert genereaza_fapte.cererea(0) == ("snow", "simplu", PERSONAJE[0])
    assert genereaza_fapte.cererea(1)[0] == "birds" and genereaza_fapte.cererea(49)[0] == SUBIECTE[49][0]
    assert genereaza_fapte.cererea(50) == ("snow", "dialog", PERSONAJE[0])
    assert genereaza_fapte.cererea(400) == ("snow", "simplu", PERSONAJE[1])  # după 50 de subiecte × 8 stiluri
    assert len({genereaza_fapte.cererea(k) for k in range(3200)}) == 3200  # 50 × 8 × 8 cereri diferite


def test_de_cate_ori_apare_faptul():
    fapt = "Birds have feathers."
    assert genereaza_fapte.aparitii('Mom said, "Birds have feathers!" All birds have feathers.', fapt) == 2
    assert genereaza_fapte.aparitii("Lily knew that birds have feathers. Then she slept.", fapt) == 1
    assert genereaza_fapte.aparitii("Blackbirds have feathers too.", fapt) == 0  # nu în mijlocul altui cuvânt
    assert genereaza_fapte.aparitii("It’s cold. Water freezes into ice when it is very cold!",
                                    "Water freezes into ice when it is very cold.") == 1
    assert genereaza_fapte.de_ce_se_scoate(9, 1) is None and genereaza_fapte.de_ce_se_scoate(7, 1) == "nota sub 8"
    assert genereaza_fapte.de_ce_se_scoate(9, 2) == "faptul de mai multe ori"
    assert genereaza_fapte.de_ce_se_scoate(9, 0) is None and genereaza_fapte.de_ce_se_scoate(None, 1) == "fără notă"  # spus altfel: rămâne


def test_scrie_noteaza_pastreaza_si_se_reia(tmp_path, monkeypatch, capsys):
    varianta = iter(range(1000))

    def raspunsuri(self, conversatii, max_simboluri, cu_intamplare):  # profesorul de probă
        if not cu_intamplare:
            return ["GRADE: 7\nREASON: Weak." if "bad story" in c[-1]["content"] else "GRADE: 9\nREASON: Good."
                    for c in conversatii]
        povesti = []
        for c in conversatii:
            fapt = c[-1]["content"].split('learns it): "')[1].split('" Do not')[0]
            povesti.append([f"A story. {fapt} The end.", f"A story. {fapt} Again, {fapt.lower()}",
                            "A story without it. The end.", f"A bad story. {fapt}"][next(varianta) % 4])
        return povesti

    monkeypatch.setattr(profesor_qwen.ProfesorQwen, "pregateste", lambda self: None)
    monkeypatch.setattr(profesor_qwen.ProfesorQwen, "_raspunsuri", raspunsuri)
    dosar = tmp_path / "fapte"
    argumente = ["--dosar", str(dosar), "--lot", "3", "--bucata", "4", "--director-lucru", str(tmp_path / "lucru")]
    assert genereaza_fapte.main(argumente + ["--povesti", "10"]) == 0

    toate = [json.loads(r) for r in (dosar / "toate.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(toate) == 10 and [r["subiect"] for r in toate[:3]] == ["snow", "birds", "the Sun"]
    assert [r["ramane"] for r in toate] == [True, False, True, False] * 2 + [True, False]  # a treia: faptul spus altfel, rămâne
    info = json.loads((dosar / "info.json").read_text(encoding="utf-8"))
    assert info["scrise"] == 10 and info["ramase"] == 5 and info["ramase_cu_faptul_spus_altfel"] == 2
    assert info["scoase"] == {"faptul de mai multe ori": 3, "nota sub 8": 2}
    assert info["distributie_note"]["9"] == 8 and info["distributie_note"]["7"] == 2
    povesti = (dosar / "povesti.txt").read_text(encoding="utf-8").strip().split(genereaza_fapte.SEPARATOR.strip())
    assert len(povesti) == 5 and FAPTE["snow"] in povesti[0]
    fapte = json.loads((dosar / "fapte.json").read_text(encoding="utf-8"))
    assert len(fapte) == 50 and fapte[FAPTE["snow"]] == [0] and fapte[FAPTE["birds"]] == [] and fapte[FAPTE["the Sun"]] == [1]

    assert genereaza_fapte.main(argumente + ["--povesti", "12"]) == 0  # se reia: încă 2, de unde a rămas
    toate = [json.loads(r) for r in (dosar / "toate.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(toate) == 12 and [r["subiect"] for r in toate[10:]] == [SUBIECTE[10][0], SUBIECTE[11][0]]
    fise = [json.loads(r) for r in (tmp_path / "lucru" / "jurnal" / "experimente.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [f["linie"] for f in fise] == ["fapte", "fapte"] and fise[-1]["scoruri"]["scrise"] == 12
    assert all(v is None or isinstance(v, (int, float)) for v in fise[-1]["scoruri"].values())  # doar numere
    assert "A story" not in json.dumps(fise)
    assert "Scrise: 12" in capsys.readouterr().out
