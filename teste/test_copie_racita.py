"""Rețeta liniei W2 (13 octombrie 2026): rata constantă, copia răcită de la sfârșitul nopții („modelul zilei”), limita de
oră a antrenării și eticheta „nerăcit” a orelor."""

from __future__ import annotations

import json
from datetime import datetime, timedelta

import pytest

from teste.test_bucla_cinstita import config_mic, fise
from unelte import antrenare_lunga, copie_racita

REGULI = '\n[antrenare_lunga]\ncopie_racita = true\nminute_racire = 0.005\nrata_finala_racire = 0.0002\neticheta = "nerăcit"\n'
ARGUMENTE = ["--pauza", "0", "--racire", "0", "--lungime", "40"]


def test_rata_copiei_scade_liniar_si_copia_nu_scrie_nicio_stare():
    pytest.importorskip("torch")
    from module.model_racit import ModelGPTRacit

    mic = {"n_straturi": 1, "n_capete": 2, "n_emb": 8, "context": 8, "lot": 2, "dispozitiv": "cpu"}
    m = ModelGPTRacit(rata_invatare=0.0005, rata_finala=0.00005, **mic)
    assert m.rata_acum(0, 0.0) == pytest.approx(0.0005) and m.rata_acum(7, 0.5) == pytest.approx(0.000275)
    assert m.rata_acum(9, 1.0) == pytest.approx(0.00005) == m.rata_acum(9, 3.0)
    assert m._progres(5, 450.0, 440.0, 1800.0) == 0.25  # pe bugetul copiei, nu pe orele liniei
    assert ModelGPTRacit(rata_invatare=0.0005, **mic).rata_finala == pytest.approx(0.00005)  # implicit: o zecime
    with pytest.raises(ValueError, match="nu scrie nicio stare"):
        ModelGPTRacit(cale_stare="lucru/linie/gpt.pt", **mic)
    with pytest.raises(ValueError, match="rata_finala"):
        ModelGPTRacit(rata_invatare=0.0005, rata_finala=0.001, **mic)


def test_limita_de_ora():
    acum = datetime(2026, 10, 13, 19, 0, 5)
    assert antrenare_lunga.limita_urmatoare("06:45", acum) == datetime(2026, 10, 14, 6, 45)
    assert antrenare_lunga.limita_urmatoare("19:30", acum) == datetime(2026, 10, 13, 19, 30)
    limita = datetime(2026, 10, 14, 6, 45)
    buget = antrenare_lunga.buget_pana_la
    assert buget(None, acum, 3600) == 3600 and buget(limita, acum, 3600) == 3600
    assert buget(limita, datetime(2026, 10, 14, 5, 41), 3600, pauza=60) == 3600  # încape la limită: 64 de minute
    assert buget(limita, datetime(2026, 10, 14, 6, 0), 3600, pauza=60) == 45 * 60 - 60 - 180  # scurtată
    assert buget(limita, datetime(2026, 10, 14, 6, 33), 3600) is None  # ar rămâne sub 10 minute
    assert buget(limita, datetime(2026, 10, 14, 7, 0), 3600) is None  # limita a trecut


def test_un_singur_proces_pe_linie(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cale = config_mic(tmp_path, "linie")
    zavor = antrenare_lunga.tine_linia(tmp_path / "lucru" / "linie")
    assert zavor is not None and antrenare_lunga.tine_linia(tmp_path / "lucru" / "linie") is None
    pornite = []
    monkeypatch.setattr(antrenare_lunga, "ruleaza", lambda *a, **o: pornite.append(a))
    assert antrenare_lunga.main(["--config", str(cale), "--ore", "1"] + ARGUMENTE) == 1  # altcineva ține linia
    assert pornite == [] and "e deja antrenată de alt proces" in capsys.readouterr().out
    zavor.close()
    assert antrenare_lunga.main(["--config", str(cale), "--ore", "1"] + ARGUMENTE) == 1 and len(pornite) == 1
    assert antrenare_lunga.main(["--config", str(cale), "--ore", "1"] + ARGUMENTE) == 1 and len(pornite) == 2  # eliberat


def test_regulile_din_configurare():
    assert antrenare_lunga.reguli_rulare({}) == {"pana_la": "", "copie_racita": False, "minute_racire": 30.0,
                                                 "rata_finala_racire": 0.00005, "eticheta": ""}
    with pytest.raises(ValueError, match="nu știu copie"):
        antrenare_lunga.reguli_rulare({"antrenare_lunga": {"copie": True}})


def test_ultima_ora_se_scurteaza_la_limita(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cale = config_mic(tmp_path, "linie", buget=3600)
    cerute = []
    monkeypatch.setattr(antrenare_lunga, "ruleaza", lambda config, linie, descriere, *a, **o: cerute.append(
        (config.buget_antrenare_secunde, descriere)))
    peste_20 = f"{datetime.now() + timedelta(minutes=20):%H:%M}"
    assert antrenare_lunga.main(["--config", str(cale), "--ore", "3", "--pana-la", peste_20] + ARGUMENTE) == 1
    (buget, descriere), = cerute  # ruleaza de probă întoarce None: rularea se oprește după prima oră
    assert 600 <= buget <= 20 * 60 - 180 and "scurtată la" in descriere and f"limita {peste_20}" in descriere
    cerute.clear()
    peste_5 = f"{datetime.now() + timedelta(minutes=5):%H:%M}"
    assert antrenare_lunga.main(["--config", str(cale), "--ore", "3", "--pana-la", peste_5] + ARGUMENTE) == 1
    assert cerute == [] and "nu mai începe" in capsys.readouterr().out


def test_noaptea_cu_rata_constanta_si_copia_racita(tmp_path, monkeypatch, capsys):
    torch = pytest.importorskip("torch")
    monkeypatch.chdir(tmp_path)
    cale = config_mic(tmp_path, "linie", model=', cale_stare = "lucru/linie/gpt.pt", fractie_rata_finala = 1.0')
    cale.write_text(cale.read_text(encoding="utf-8") + REGULI, encoding="utf-8")
    examene = []
    monkeypatch.setattr(copie_racita, "examen_separat", lambda comanda, minute: examene.append(comanda))
    argumente = ["--config", str(cale)] + ARGUMENTE
    stare = tmp_path / "lucru" / "linie" / "gpt.pt"

    assert antrenare_lunga.main(argumente + ["--ore", "2"]) == 0
    ora1, ora2, copia = fise(tmp_path)
    for ora in (ora1, ora2):  # linia: rata constantă, orele notate „nerăcit”
        assert ora["linie"] == "linie" and ora["propunere"]["descriere"].endswith("(nerăcit)")
        assert ora["statistici_antrenare"]["rata_la_final"] == pytest.approx(0.002)
    assert copia["linie"] == "linie_racit_002" and copia["decizie"] == "pastrat" and copia["model_salvat"]
    assert copia["module"]["model"]["cale"] == copie_racita.MODUL_RACIT
    s = copia["statistici_antrenare"]
    assert s["racit"] and s["continuat"] and s["pornit_din"] == "lucru/linie/gpt.pt"
    assert 0.0002 <= s["rata_la_final"] < 0.002 and s["rata_la_inceput"] == 0.002
    assert s["pasi_total"] == ora2["statistici_antrenare"]["pasi_total"] + s["pasi"]  # copia a pornit din starea orei 2
    assert "cale_stare" not in copia["setari"]["model"] and "dupa_examen" not in copia or not (copia.get("dupa_examen") or {}).get("continuare")
    # starea liniei e cea de dinainte de răcire
    assert torch.load(stare, weights_only=True)["pasi_total"] == ora2["statistici_antrenare"]["pasi_total"]
    zi = json.loads((tmp_path / "lucru" / "linie" / "modelul_zilei.json").read_text(encoding="utf-8"))
    assert (zi["experiment"], zi["ore"], zi["linia_copiei"]) == (copia["id"], 2, "linie_racit_002")
    assert zi["starea_liniei_neatinsa"] is True and zi["val_bpb"] == copia["scoruri"]["val_bpb"]
    # setul sacru și validările se cer pe modelul copiei
    assert [c[3] for c in examene] == ["unelte/examen_fapte_nou.py", "unelte/examen_validari_ws.py"]
    assert all(str(copia["id"]) in c for c in examene) and "--sacru" in examene[0]
    assert "Modelul zilei: copia răcită după ora 2" in capsys.readouterr().out

    assert antrenare_lunga.main(argumente + ["--ore", "2"]) == 0  # reluat: copia există, nu se mai antrenează nimic
    assert len(fise(tmp_path)) == 3
    assert antrenare_lunga.main(argumente + ["--ore", "2", "--fara-copie-racita"]) == 0

    assert antrenare_lunga.main(argumente + ["--ore", "3"]) == 0  # noaptea următoare: linia continuă din starea nerăcită
    ora3, copia3 = fise(tmp_path)[3:]
    assert ora3["linie"] == "linie" and copia3["linie"] == "linie_racit_003"
    assert ora3["statistici_antrenare"]["pasi_total"] == ora2["statistici_antrenare"]["pasi_total"] + ora3["statistici_antrenare"]["pasi"]
    randuri = (tmp_path / "lucru" / "linie" / "modelele_zilei.jsonl").read_text(encoding="utf-8").splitlines()
    assert [json.loads(r)["ore"] for r in randuri] == [2, 2, 3]


def test_copia_racita_cere_o_linie_cu_stare(tmp_path, monkeypatch, capsys):
    pytest.importorskip("torch")
    monkeypatch.chdir(tmp_path)
    fara_stare = config_mic(tmp_path, "fara")
    assert copie_racita.main(["--config", str(fara_stare)]) == 1
    neinceputa = config_mic(tmp_path, "linie", model=', cale_stare = "lucru/linie/gpt.pt"')
    assert copie_racita.main(["--config", str(neinceputa)]) == 1
    assert "n-are cale_stare" in (iesire := capsys.readouterr().out) and "n-are nicio oră făcută" in iesire
    assert not (tmp_path / "lucru" / "jurnal" / "experimente.jsonl").exists()  # nu s-a pornit niciun experiment


def test_configurarea_w2_are_reteta_noua():
    import tomllib

    from kronos.config import citeste_config
    from teste.test_cap_coada import RADACINA

    cale = RADACINA / "config" / "ws_w2.toml"
    model = citeste_config(cale).setari_port("model")
    assert model["rata_invatare"] == 0.0005 and model["rata_care_scade"] and model["fractie_rata_finala"] == 1.0
    assert 1500 <= model["incalzire_pasi"] <= 2000  # ~5 minute la ~5,9 pași pe secundă
    assert (model["lot"], model["context"], model["fractie_hrana"]) == (12, 512, 0.06)
    reguli = antrenare_lunga.reguli_rulare(tomllib.loads(cale.read_text(encoding="utf-8")))
    assert reguli == {"pana_la": "06:45", "copie_racita": True, "minute_racire": 30.0, "rata_finala_racire": 0.00005,
                      "eticheta": "nerăcit"}
