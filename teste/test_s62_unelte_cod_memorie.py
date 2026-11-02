"""S62: uneltele de examen de cod se țin singure sub limita plăcii (`--lot`, `--memorie-max`) și `examen_validare.py`
citește și starea liniei (`gpt.pt`). Pe procesor, pe config/cod_c1.toml micșorat și pe setul de PROBĂ; memoria plăcii
e simulată (pe procesor nu e nimic de citit)."""

from __future__ import annotations

import json

import pytest

torch = pytest.importorskip("torch")

from teste.test_s60_unelte_cod import model_mic  # noqa: E402,F401  (fixture)
from unelte.kronos_cod import examen_cod as ex  # noqa: E402
from unelte.kronos_cod import examen_validare as ev  # noqa: E402
from unelte.kronos_cod import memorie_placa  # noqa: E402


def _raspunsuri(cale, stare, iesire, *extra) -> dict:
    assert ex.main(["model", "--config", str(cale), "--stare", str(stare), "--set", "proba", "--probleme", "4",
                    "--max-simboluri", "12", "--temperatura", "5", "--iesire", str(iesire), *extra]) == 0
    return json.loads(iesire.read_text(encoding="utf-8"))


def test_lotul_nu_schimba_raspunsurile(model_mic, tmp_path):
    """(a) --lot 1, 2 și 10 dau aceleași corpuri (fiecare corp are sămânța lui); temperatura 5, ca să varieze."""
    cale, stare, _ = model_mic
    r = {lot: _raspunsuri(cale, stare, tmp_path / f"lot{lot}.json", "--lot", str(lot)) for lot in (1, 2, 10)}
    assert r[1]["raspunsuri"] == r[2]["raspunsuri"] == r[10]["raspunsuri"]
    assert all(len(v) == 10 for v in r[1]["raspunsuri"].values()) and len(r[1]["raspunsuri"]) == 4
    assert len({c for v in r[1]["raspunsuri"].values() for c in v}) > 4  # corpurile chiar diferă între ele
    assert r[2]["meta"]["lot"] == 2 and r[2]["meta"]["memorie_max_mb"] == 6500
    assert r[2]["meta"]["memorie_varf_mb"] is None and "incomplet" not in r[2]["meta"]  # procesor: nimic de citit
    # implicitul e --lot 2
    implicit = _raspunsuri(cale, stare, tmp_path / "implicit.json")
    assert implicit["meta"]["lot"] == 2 and implicit["raspunsuri"] == r[2]["raspunsuri"]


def test_samanta_corp_diferita_pe_corp_si_problema():
    s = {ex.samanta_corp(b, k, j) for b in (0, 1) for k in range(200) for j in range(10)}
    assert len(s) == 2 * 200 * 10


def test_memoria_peste_limita_opreste_examen_cod(model_mic, tmp_path, monkeypatch):
    """(b) o memorie simulată care trece de limită după câteva citiri: cod 3, fișier „incomplet” cu ce s-a apucat
    (doar problemele întregi)."""
    cale, stare, _ = model_mic
    citiri = []

    def memorie_falsa(dispozitiv):
        citiri.append(1)
        return 300.0 if len(citiri) <= 6 else 9000.0  # 1 la pornire + 5 loturi de 2 = prima problemă întreagă

    monkeypatch.setattr(memorie_placa, "memorie_folosita_mb", memorie_falsa)
    iesire = tmp_path / "oprit.json"
    assert ex.main(["model", "--config", str(cale), "--stare", str(stare), "--set", "proba", "--probleme", "4",
                    "--max-simboluri", "8", "--lot", "2", "--memorie-max", "500", "--iesire", str(iesire)]) == 3
    d = json.loads(iesire.read_text(encoding="utf-8"))
    m = d["meta"]
    assert m["incomplet"] is True and "9000 MB" in m["oprit"] and m["memorie_varf_mb"] == 9000
    assert m["probleme"] == 1 and m["probleme_cerute"] == 4
    assert list(d["raspunsuri"]) == [ex.set_proba()[0].id] and len(d["raspunsuri"][ex.set_proba()[0].id]) == 10


def test_paza_tine_varful_si_opreste():
    valori = iter([100.0, 400.0, 200.0, 700.0])
    p = memorie_placa.Paza("cuda", 500, citeste=lambda d: next(valori))
    assert [p.verifica() for _ in range(3)] == [100.0, 400.0, 200.0] and p.varf == 400.0
    with pytest.raises(memorie_placa.MemoriePeste, match="700 MB"):
        p.verifica()
    assert p.varf == 700.0
    assert memorie_placa.Paza("cpu", 1).verifica() is None  # pe procesor nu oprește nimic
    assert memorie_placa.memorie_folosita_mb("cpu") is None


def _date_mici(cale):
    from kronos.config import citeste_config
    from module.date_cod import DateCod

    sd = citeste_config(cale).setari_port("date")
    return DateCod(director=sd["director"], context=sd["context"], sfarsit_de_fisier=sd["sfarsit_de_fisier"],
                   cale_tokenizer=sd["cale_tokenizer"])


def test_examen_validare_aceeasi_cifra_din_gpt_pt_si_din_jurnal(model_mic):
    """(c) același model mic: biții pe validare din starea liniei (gpt.pt) = cei din modelul salvat în jurnal."""
    from teste.cod_mic import VALIDARE

    cale, stare, salvat = model_mic
    date = _date_mici(cale)
    index = [(limbaj, len(f.encode("utf-8"))) for bloc in VALIDARE for f, limbaj in bloc]
    rez = {}
    for nume, s in (("gpt", stare), ("jurnal", salvat)):
        logits, _, dispozitiv = ev._model(str(cale), str(s))
        assert str(dispozitiv) == "cpu"
        rez[nume] = ev.examineaza(logits, date, index, lot=2)
    assert rez["gpt"] == rez["jurnal"]
    assert rez["gpt"]["tot"]["fisiere"] == 3 and rez["gpt"]["tot"]["biti_pe_octet"] > 0


def test_examen_validare_se_opreste_peste_memorie(model_mic):
    cale, stare, _ = model_mic
    date = _date_mici(cale)
    logits, _, _ = ev._model(str(cale), str(stare))
    valori = iter([100.0, 9000.0])
    paza = memorie_placa.Paza("cuda", 6500, citeste=lambda d: next(valori))
    with pytest.raises(memorie_placa.MemoriePeste) as e:
        ev.pierderi(logits, date.fisiere_validare(), date.context, date.sfarsit_de_fisier, lot=1, paza=paza)
    assert e.value.bucati_facute == 2 and e.value.bucati_total >= 3
