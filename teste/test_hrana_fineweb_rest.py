"""S110 (C-120): restul FineWeb-2 ca hrană — tăietura e cea a amestecului, textele cu bucăți din examene se scot, iar
verificarea a doua pe fișierul scris dă 0."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")

from unelte import hrana_fineweb_rest as hr  # noqa: E402
from unelte.pregateste_amestec_ws import SEPARATOR, inceputul  # noqa: E402

CAPAT = SEPARATOR + "\n"


def _text(i: int) -> str:
    return f"Textul numărul {i} vorbește despre orașul {i} și despre râul care trece prin el, cu ș și ț. " * 3


@pytest.fixture
def lume(tmp_path: Path) -> dict:
    texte = [_text(i) for i in range(40)]
    sursa = tmp_path / "sursa.txt"
    sursa.write_bytes("".join(t + CAPAT for t in texte).encode())
    dorit = len("".join(t + CAPAT for t in texte[:10]).encode()) + 25  # tăietura cade în textul 10 → se iau 10 texte
    luat = inceputul(sursa, dorit)
    inainte = b"alta sursa" + CAPAT.encode()
    amestec = tmp_path / "amestec.txt"
    amestec.write_bytes(inainte + luat + b"si ce urmeaza")
    info = tmp_path / "info_amestec.json"
    info.write_text(json.dumps({"surse": {"alta": {"octeti": len(inainte)},
                                          "fineweb2_ro": {"octeti": len(luat), "octeti_doriti": dorit}}}), encoding="utf-8")
    return {"texte": texte, "sursa": sursa, "amestec": amestec, "info": info, "luat": luat, "dosar": tmp_path}


def test_taietura_e_cea_a_amestecului(lume):
    t = hr.taietura(lume["sursa"], lume["info"], amestec=lume["amestec"])
    assert t["octeti_taietura"] == len(lume["luat"]) == len("".join(x + CAPAT for x in lume["texte"][:10]).encode())
    assert t["octeti_adaugati_de_amestec"] == 0 and t["identica_in_amestec"]
    assert t["pozitia_in_amestec"] == len(b"alta sursa" + CAPAT.encode())


def test_taietura_refuza_cand_nu_se_potriveste(lume):
    info = json.loads(lume["info"].read_text(encoding="utf-8"))
    info["surse"]["fineweb2_ro"]["octeti"] += 1
    lume["info"].write_text(json.dumps(info), encoding="utf-8")
    with pytest.raises(ValueError, match="nu e cea din info.json"):
        hr.taietura(lume["sursa"], lume["info"])


def test_taietura_refuza_cand_amestecul_are_altceva(lume):
    date = bytearray(lume["amestec"].read_bytes())
    date[40] ^= 1
    lume["amestec"].write_bytes(bytes(date))
    with pytest.raises(ValueError, match="nu e tăietura recalculată"):
        hr.taietura(lume["sursa"], lume["info"], amestec=lume["amestec"])


def test_sirurile_din_json():
    assert list(hr.siruri_din_json({"a": "x", "b": [{"c": "y"}, 3, None, ["z"]]})) == ["x", "y", "z"]


def test_texte_de_ferit_din_fisiere(tmp_path):
    (tmp_path / "v.txt").write_text("unu" + CAPAT + "doi" + CAPAT, encoding="utf-8")
    (tmp_path / "a.jsonl").write_text('{"text": "trei", "n": 1}\n{"text": "patru"}\n', encoding="utf-8")
    (tmp_path / "e.json").write_text('{"intrebari": [{"text": "cinci"}]}', encoding="utf-8")
    t = hr.texte_de_ferit({"v": str(tmp_path / "v.txt")}, {"a": str(tmp_path / "a.jsonl"), "e": str(tmp_path / "e.json")})
    assert t == {"v": ["unu", "doi"], "a": ["trei", "patru"], "e": ["cinci"]}


@pytest.mark.parametrize("procese", [1, 2], ids=["un_proces", "doua_procese"])
def test_scoate_textele_cu_bucati_comune_si_verificarea_da_zero(lume, procese):
    texte = lume["texte"]
    # o bucată de 60 de litere din textul 17 (în rest) într-o validare; una din textul 30 într-un examen;
    # una din textul 3 (în partea luată de amestec: nu contează); una de doar 40 de litere din textul 20 (prea scurtă)
    de_ferit = {"validare": ["ceva înainte " + texte[17][30:90] + " ceva după", "alt text fără legătură " * 5],
                "examen": [texte[30][5:70], texte[3][0:80], texte[20][10:50]]}
    iesire = lume["dosar"] / "hrana"
    info = hr.ruleaza(lume["sursa"], lume["info"], lume["amestec"], iesire, procese=procese, octeti_pe_bloc=2000,
                      dosar_lucru=lume["dosar"] / "lucru", de_ferit=de_ferit, spune=lambda *a, **k: None)
    scris = (iesire / "antrenare.txt").read_bytes()
    asteptat = "".join(t + CAPAT for i, t in enumerate(texte) if i >= 10 and i not in (17, 30)).encode()
    assert scris == asteptat
    assert info["texte"] == 30 and info["texte_scoase"] == 2 and info["texte_pastrate"] == 28
    assert info["scoase_pe_motiv"] == {"validare": 1, "examen": 1}
    assert info["sha256"] == hashlib.sha256(scris).hexdigest() and info["octeti"] == len(scris)
    assert info["rest_octeti"] == lume["sursa"].stat().st_size - len(lume["luat"])
    assert info["parte_scoasa"] == pytest.approx(2 / 30, abs=1e-6) and not info["se_foloseste"]  # 6,7 % > 5 %
    assert not list((lume["dosar"] / "lucru").glob("*.npy")) if procese > 1 else True
    with pytest.raises(FileExistsError):
        hr.ruleaza(lume["sursa"], lume["info"], lume["amestec"], iesire, procese=1, de_ferit=de_ferit)
    v = hr.verifica(iesire, procese=procese, octeti_pe_bloc=2000, dosar_lucru=lume["dosar"] / "lucru",
                    de_ferit=de_ferit, spune=lambda *a, **k: None)
    assert v["curat"] and v["texte_cu_bucati_comune"] == 0 and v["texte"] == 28
    assert json.loads((iesire / "info.json").read_text(encoding="utf-8"))["verificare"]["curat"]


@pytest.mark.parametrize("bloc", [2000, 10_000_000], ids=["blocuri_mici", "un_bloc"])
def test_bucata_care_incepe_pe_randul_nou_e_a_textului_care_urmeaza(lume, bloc):
    """Greșeala găsită la prima rulare pe datele adevărate (13 nov 2026): validarea are, la mijloc, un rând care începe
    cu aceleași 49 de litere ca un text din rest; bucata „rând nou + 49 de litere” trebuie să scoată ACEL text, nu pe cel
    de dinaintea lui (și verificarea a doua trebuie să dea 0). Se încearcă și primul text din rest și primul din bloc."""
    texte = lume["texte"]
    de_ferit = {"validare": ["un rând de început\n" + texte[25][:49] + " și apoi altceva decât în textul acela",
                             "alt început\n" + texte[10][:49] + " — primul text din rest",
                             texte[33][:49] + " fără rând nou în față: doar 49 de litere comune, nu se scoate"]}
    iesire = lume["dosar"] / "hrana"
    info = hr.ruleaza(lume["sursa"], lume["info"], None, iesire, procese=1, octeti_pe_bloc=bloc, de_ferit=de_ferit,
                      spune=lambda *a, **k: None)
    asteptat = "".join(t + CAPAT for i, t in enumerate(texte) if i >= 10 and i not in (10, 25)).encode()
    assert (iesire / "antrenare.txt").read_bytes() == asteptat and info["texte_scoase"] == 2
    for alt_bloc in (1500, 10_000_000):
        v = hr.verifica(iesire, procese=1, octeti_pe_bloc=alt_bloc, de_ferit=de_ferit, spune=lambda *a, **k: None)
        assert v["curat"] and v["texte_cu_bucati_comune"] == 0


def test_reface_cere_un_motiv_si_il_scrie(lume):
    de_ferit = {"validare": [lume["texte"][17][30:90]]}
    iesire = lume["dosar"] / "hrana"
    primul = hr.ruleaza(lume["sursa"], lume["info"], None, iesire, procese=1, de_ferit=de_ferit, spune=lambda *a, **k: None)
    with pytest.raises(FileExistsError):
        hr.ruleaza(lume["sursa"], lume["info"], None, iesire, procese=1, de_ferit=de_ferit, spune=lambda *a, **k: None)
    al_doilea = hr.ruleaza(lume["sursa"], lume["info"], None, iesire, procese=1, de_ferit=de_ferit,
                           spune=lambda *a, **k: None, reface="greșeală a uneltei")
    assert al_doilea["refacut"]["motiv"] == "greșeală a uneltei" and al_doilea["refacut"]["sha256_vechi"] == primul["sha256"]
    assert al_doilea["sha256"] == primul["sha256"]


def test_verificarea_prinde_un_text_strecurat(lume):
    de_ferit = {"validare": [lume["texte"][17][30:90]]}
    iesire = lume["dosar"] / "hrana"
    hr.ruleaza(lume["sursa"], lume["info"], None, iesire, procese=1, de_ferit=de_ferit, spune=lambda *a, **k: None)
    with (iesire / "antrenare.txt").open("ab") as f:
        f.write((lume["texte"][17] + CAPAT).encode())
    v = hr.verifica(iesire, procese=1, de_ferit=de_ferit, spune=lambda *a, **k: None)
    assert not v["curat"] and v["texte_cu_bucati_comune"] == 1 and not v["sha256_ca_in_info"]
    assert not json.loads((iesire / "info.json").read_text(encoding="utf-8"))["se_foloseste"]


def test_fara_nimic_de_scos_restul_e_neschimbat(lume):
    iesire = lume["dosar"] / "hrana"
    info = hr.ruleaza(lume["sursa"], lume["info"], None, iesire, procese=1, octeti_pe_bloc=1500,
                      de_ferit={"validare": ["nimic comun cu textele acelea, doar altceva scris aici, destul de lung"]},
                      spune=lambda *a, **k: None)
    assert (iesire / "antrenare.txt").read_bytes() == lume["sursa"].read_bytes()[len(lume["luat"]):]
    assert info["texte_scoase"] == 0 and info["se_foloseste"]


def test_ultimul_text_neincheiat_se_pastreaza_incheiat(tmp_path):
    toate, sursa_id, _ = hr.amprente_de_ferit({"v": ["x" * 60]}, 50)
    r = hr.cauta_in_bloc(("primul" + CAPAT + "al doilea, fără capăt").encode(), 50, toate, sursa_id)
    assert r["texte"] == 2 and r["pastrate"] == ("primul" + CAPAT + "al doilea, fără capăt" + CAPAT).encode()
