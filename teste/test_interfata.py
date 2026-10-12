"""Interfața v0 (module/interfata/): chat în browser, istoric în SQLite, module din registru, acces doar local și
prin Tailscale. Fără placă video și fără modele mari: creierul fals sau un n-gram antrenat pe loc, pe procesor."""

from __future__ import annotations

import json
import sqlite3
import urllib.error
import urllib.request
from contextlib import closing, contextmanager
from pathlib import Path
from typing import Any, Iterator

import pytest

from kronos.config import citeste_config
from kronos.jurnal import Jurnal
from module.date_mostra import DateMostra
from module.interfata import PORT_IMPLICIT, __main__ as pornire
from module.interfata.catalog import Catalog
from module.interfata.creiere import CreierFals, CreierKronos
from module.interfata.module_ui import lista_modulelor
from module.interfata.retea import adresa_permisa, adrese_de_ascultat
from module.interfata.server import LUNGIME_MAXIMA_MESAJ, Aplicatie, ServerInterfata, porneste
from module.model_ngram import ModelNgram

RADACINA = Path(__file__).resolve().parent.parent
RAU = 'Țară, șosea, înger, „mâță” & <script>alert("x")</script> <b>gras</b>'


@contextmanager
def server_pornit(baza: Path, **setari: Any) -> Iterator[tuple[str, Aplicatie]]:
    """Un server pe 127.0.0.1, pe un port liber, oprit la ieșire. Întoarce adresa lui și aplicația."""
    aplicatie = Aplicatie(Catalog(baza), setari.pop("creier", CreierFals()), **setari)
    servere = porneste(aplicatie, 0)
    try:
        yield servere.adrese[0].rstrip("/"), aplicatie
    finally:
        servere.opreste()


def cere(adresa: str, corp: Any = None, tip: str = "application/json") -> tuple[int, dict[str, str], bytes]:
    """O cerere GET (fără corp) sau POST (cu corp JSON). Întoarce codul, antetele și conținutul, și la erori."""
    date = None if corp is None else json.dumps(corp).encode("utf-8")
    cerere = urllib.request.Request(adresa, data=date, headers={"Content-Type": tip} if date else {})
    try:
        with urllib.request.urlopen(cerere, timeout=10) as raspuns:
            return raspuns.status, dict(raspuns.headers), raspuns.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()


def json_de_la(adresa: str, corp: Any = None) -> dict[str, Any]:
    cod, _, continut = cere(adresa, corp)
    assert cod == 200, continut.decode("utf-8")
    return json.loads(continut.decode("utf-8"))


def randuri_din_baza(baza: Path) -> list[tuple[str, str, str]]:
    with closing(sqlite3.connect(baza)) as legatura:
        return legatura.execute("SELECT rol, autor, text FROM mesaje ORDER BY id").fetchall()


def test_pagina_principala_se_serveste(tmp_path):
    with server_pornit(tmp_path / "c.db") as (adresa, _):
        cod, antete, continut = cere(adresa + "/")
        pagina = continut.decode("utf-8")
        assert cod == 200 and antete["Content-Type"].startswith("text/html")
        assert '<html lang="ro">' in pagina and "Conversație nouă" in pagina and 'src="aplicatie.js"' in pagina
        assert "http://" not in pagina and "https://" not in pagina  # nicio bibliotecă de pe internet
        assert cere(adresa + "/aplicatie.js")[0] == 200 and cere(adresa + "/stil.css")[0] == 200
        assert cere(adresa + "/nu-exista")[0] == 404 and cere(adresa + "/../server.py")[0] == 404
        assert json_de_la(adresa + "/api/stare")["creier"] == CreierFals.eticheta


def test_mesajul_primeste_raspuns_si_amandoua_ajung_in_baza(tmp_path):
    baza = tmp_path / "interfata" / "c.db"
    with server_pornit(baza) as (adresa, _):
        primit = json_de_la(adresa + "/api/mesaj", {"conversatie": None, "text": "Salut, Kronos!"})
        asteptat = CreierFals().raspunde("Salut, Kronos!", 200)
        assert primit["eroare"] is None and primit["intrebare"]["text"] == "Salut, Kronos!"
        assert primit["raspuns"]["text"] == asteptat and primit["raspuns"]["autor"] == CreierFals.eticheta
        assert primit["raspuns"]["secunde"] >= 0  # timpul de răspuns se notează
        numar = primit["conversatie"]
        # al doilea mesaj intră în aceeași conversație
        json_de_la(adresa + "/api/mesaj", {"conversatie": numar, "text": "Încă unul"})
        mesaje = json_de_la(f"{adresa}/api/conversatii/{numar}")["mesaje"]
        assert [m["rol"] for m in mesaje] == ["om", "creier", "om", "creier"]
        lista = json_de_la(adresa + "/api/conversatii")["conversatii"]
        assert [(c["id"], c["titlu"], c["mesaje"]) for c in lista] == [(numar, "Salut, Kronos!", 4)]
    assert randuri_din_baza(baza)[:2] == [("om", "Tu", "Salut, Kronos!"), ("creier", CreierFals.eticheta, asteptat)]


def test_istoricul_ramane_dupa_repornire(tmp_path):
    baza = tmp_path / "c.db"
    with server_pornit(baza) as (adresa, _):
        numar = json_de_la(adresa + "/api/mesaj", {"text": "Ține minte asta"})["conversatie"]
    with server_pornit(baza) as (adresa, _):  # alt server, aceeași bază
        assert [c["id"] for c in json_de_la(adresa + "/api/conversatii")["conversatii"]] == [numar]
        mesaje = json_de_la(f"{adresa}/api/conversatii/{numar}")["mesaje"]
        assert [m["text"] for m in mesaje] == ["Ține minte asta", CreierFals().raspunde("Ține minte asta", 200)]
        alta = json_de_la(adresa + "/api/mesaj", {"text": "A doua conversație"})["conversatie"]
        assert alta != numar and len(json_de_la(adresa + "/api/conversatii")["conversatii"]) == 2


def test_lista_modulelor_vine_din_manifest(tmp_path):
    config = citeste_config(RADACINA / "config" / "proba.toml")
    module = lista_modulelor(config)
    assert sorted(m["port"] for m in module) == sorted(config.porturi)
    pe_port = {m["port"]: m for m in module}
    assert pe_port["model"]["nume"] == ModelNgram.MANIFEST["nume"] == "model_ngram"
    assert pe_port["model"]["versiune"] == ModelNgram.MANIFEST["versiune"]
    assert pe_port["model"]["cale"] == "module.model_ngram:ModelNgram"
    assert pe_port["interfata"]["nume"] == "interfata_consola" and pe_port["stocare"]["nume"] == "stocare_disc"
    assert all(m["eroare"] is None and m["nume"] and m["versiune"] for m in module)
    with server_pornit(tmp_path / "c.db", module=module, configurare=config.nume) as (adresa, _):
        primit = json_de_la(adresa + "/api/module")
        assert primit["configurare"] == "proba" and primit["module"] == module


def test_modulul_care_nu_se_poate_citi_apare_cu_eroare():
    config = citeste_config(RADACINA / "config" / "proba.toml")
    config.porturi["memorie"] = {"modul": "module.nu_exista:Nimic"}
    config.porturi["traducere"] = {"modul": "module.model_ngram:ModelNgram"}  # modul de pe alt port
    pe_port = {m["port"]: m for m in lista_modulelor(config)}
    assert "nu pot importa" in pe_port["memorie"]["eroare"] and pe_port["memorie"]["nume"] is None
    assert "portul „model”" in pe_port["traducere"]["eroare"]
    assert pe_port["model"]["eroare"] is None


@pytest.mark.parametrize(("adresa", "are_voie"), [
    ("127.0.0.1", True), ("::1", True), ("100.100.1.2", True), ("100.64.0.0", True), ("100.127.255.255", True),
    ("::ffff:127.0.0.1", True), ("::ffff:100.100.1.2", True),
    ("192.168.1.5", False), ("100.128.0.1", False), ("100.63.255.255", False), ("10.0.0.1", False),
    ("127.0.0.2", False), ("8.8.8.8", False), ("0.0.0.0", False), ("::", False), ("fe80::1", False),
    ("::ffff:192.168.1.5", False), ("", False), ("localhost", False), ("nu e adresa", False),
])
def test_verificarea_adresei(adresa, are_voie):
    assert adresa_permisa(adresa) is are_voie


def test_clientul_din_afara_primeste_403(tmp_path):
    baza = tmp_path / "c.db"
    with server_pornit(baza) as (adresa, aplicatie):
        aplicatie.adresa_permisa = lambda ip: adresa_permisa("192.168.1.5")  # ca și cum ar veni din rețeaua casei
        for cale in ("/", "/api/stare", "/api/conversatii", "/aplicatie.js"):
            cod, _, continut = cere(adresa + cale)
            assert cod == 403 and "Tailscale" in json.loads(continut.decode("utf-8"))["eroare"]
        assert cere(adresa + "/api/mesaj", {"text": "intrus"})[0] == 403
    assert randuri_din_baza(baza) == []  # nimic din ce a trimis nu a ajuns în bază


def test_serverul_nu_asculta_niciodata_pe_toate_adresele(tmp_path):
    aplicatie = Aplicatie(Catalog(tmp_path / "c.db"), CreierFals())
    for adresa in ("0.0.0.0", "", "::", "192.168.1.5"):
        with pytest.raises(ValueError):
            ServerInterfata(adresa, 0, aplicatie)
        with pytest.raises(ValueError):
            porneste(aplicatie, 0, ["127.0.0.1", adresa])
    assert adrese_de_ascultat(None) == ["127.0.0.1"]
    assert adrese_de_ascultat("100.90.1.2") == ["127.0.0.1", "100.90.1.2"]
    assert adrese_de_ascultat("0.0.0.0") == ["127.0.0.1"] and adrese_de_ascultat("192.168.1.5") == ["127.0.0.1"]
    assert PORT_IMPLICIT == 8787


def test_diacriticele_si_html_ul_raman_text(tmp_path):
    baza = tmp_path / "c.db"
    with server_pornit(baza) as (adresa, _):
        primit = json_de_la(adresa + "/api/mesaj", {"text": RAU})
        assert primit["intrebare"]["text"] == RAU and RAU in primit["raspuns"]["text"]
        numar = primit["conversatie"]
        cod, antete, continut = cere(f"{adresa}/api/conversatii/{numar}")
        assert antete["Content-Type"] == "application/json; charset=utf-8"  # JSON, nu HTML: browserul nu-l execută
        assert antete["X-Content-Type-Options"] == "nosniff"
        assert json.loads(continut.decode("utf-8"))["mesaje"][0]["text"] == RAU
        # pagina e aceeași oricâte mesaje ar fi: textul oamenilor nu e lipit niciodată în HTML
        cod, antete, pagina = cere(adresa + "/")
        assert "alert(" not in pagina.decode("utf-8") and "gras" not in pagina.decode("utf-8")
        politica = antete["Content-Security-Policy"]
        assert "script-src 'self'" in politica and "unsafe-inline" not in politica and "default-src 'none'" in politica
        cod, _, cod_pagina = cere(adresa + "/aplicatie.js")
    assert randuri_din_baza(baza)[0] == ("om", "Tu", RAU)  # în bază: exact ce a scris omul
    js = cod_pagina.decode("utf-8")
    # codul paginii pune textul doar cu textContent; nicio cale prin care un text ar deveni HTML sau cod
    for interzis in ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write", "eval("):
        assert interzis not in js
    assert "textContent" in js
    html = (RADACINA / "module" / "interfata" / "static" / "index.html").read_text(encoding="utf-8")
    assert "<script>" not in html and " onclick" not in html and "style=" not in html  # niciun cod scris în pagină


def test_cererile_gresite_sunt_refuzate_pe_inteles(tmp_path):
    baza = tmp_path / "c.db"
    with server_pornit(baza) as (adresa, _):
        assert cere(adresa + "/api/mesaj", {"text": "   "})[0] == 400
        assert cere(adresa + "/api/mesaj", {"text": "x" * (LUNGIME_MAXIMA_MESAJ + 1)})[0] == 400
        assert cere(adresa + "/api/mesaj", {"text": "bun", "conversatie": 99})[0] == 404
        assert cere(adresa + "/api/mesaj", ["nu", "obiect"])[0] == 400
        assert cere(adresa + "/api/mesaj", {"text": "formular"}, tip="text/plain")[0] == 415  # doar JSON
        assert cere(adresa + "/api/conversatii/99")[0] == 404
        assert cere(adresa + "/api/altceva", {"text": "x"})[0] == 404
    assert randuri_din_baza(baza) == []


def test_eroarea_creierului_se_spune_cinstit_si_intrebarea_ramane(tmp_path):
    class CreierStricat:
        eticheta = "Creier stricat"

        def raspunde(self, text: str, lungime: int) -> str:
            raise RuntimeError("modelul nu a fost antrenat sau încărcat")

    baza = tmp_path / "c.db"
    with server_pornit(baza, creier=CreierStricat()) as (adresa, _):
        primit = json_de_la(adresa + "/api/mesaj", {"text": "Ești acolo?"})
        assert primit["raspuns"] is None and "Creier stricat n-a putut răspunde" in primit["eroare"]
    assert randuri_din_baza(baza) == [("om", "Tu", "Ești acolo?")]  # niciun răspuns inventat


def test_creierul_fals_e_determinist():
    creier = CreierFals()
    assert creier.raspunde("ceva", 200) == creier.raspunde("ceva", 200) != creier.raspunde("altceva", 200)
    assert len(creier.raspunde("un text lung " * 50, 40)) == 40


def test_creier_kronos_raspunde_cu_un_model_mic_incarcat_lenes(tmp_path):
    """Un n-gram antrenat pe loc, pe procesor, salvat și notat într-un jurnal Kronos din tmp_path: CreierKronos îl
    găsește după numărul experimentului, îl încarcă abia la prima întrebare și răspunde cu textul generat de el."""
    setari = {"ordin": 3, "netezire": 0.5}
    model = ModelNgram(**setari)
    model.antreneaza(DateMostra(propozitii=300), buget_secunde=2)
    salvat = model.salveaza(str(tmp_path / "lucru" / "stocare" / "modele" / "experiment_7"))
    jurnal = Jurnal(tmp_path / "lucru")
    jurnal.adauga({"id": 6, "linie": "proba", "decizie": "respins", "setari": {"model": setari},
                   "module": {"model": {"cale": "module.model_ngram:ModelNgram"}}})  # fără model salvat
    jurnal.adauga({"id": 7, "linie": "proba", "decizie": "pastrat", "model_salvat": salvat, "setari": {"model": setari},
                   "module": {"model": {"cale": "module.model_ngram:ModelNgram"}}})

    creier = CreierKronos(7, tmp_path / "lucru")
    assert creier.dispozitiv == "cpu" and not creier.incarcat and "#7" in creier.eticheta  # nimic încărcat la creare
    raspuns = creier.raspunde("The ", 40)
    assert creier.incarcat and isinstance(raspuns, str) and len(raspuns) == 40
    assert raspuns == model.genereaza("The ", 40)  # exact ce spune modelul, fără nimic adăugat

    with server_pornit(tmp_path / "c.db", creier=creier, lungime_raspuns=30) as (adresa, _):
        primit = json_de_la(adresa + "/api/mesaj", {"text": "The "})
        assert primit["raspuns"]["text"] == model.genereaza("The ", 30) and primit["raspuns"]["autor"] == creier.eticheta

    with pytest.raises(ValueError, match="#6"):  # experiment fără model salvat: eroare pe înțeles, la prima întrebare
        CreierKronos(6, tmp_path / "lucru").raspunde("The ", 10)


def test_linia_de_comanda_cere_un_creier_si_o_configurare_buna(tmp_path, capsys):
    config = str(RADACINA / "config" / "proba.toml")
    for argumente in (["--config", config], ["--config", config, "--fals", "--experiment", "3"]):
        with pytest.raises(SystemExit):
            pornire.main(argumente)
    capsys.readouterr()
    assert pornire.main(["--config", str(tmp_path / "lipsa.toml"), "--fals"]) == 2
    assert "Nu pot porni" in capsys.readouterr().out
