"""S118 (C-126 B): 👍 / 👎 și „răspunsul corect ar fi…” în interfață; totul rămâne local, în baza din lucru/."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from module.interfata.catalog import Catalog
from module.interfata.creiere import CreierFals
from teste.test_interfata import cere, creier_text_fals, json_de_la, server_pornit

RADACINA = Path(__file__).resolve().parents[1]


def test_aprecierea_in_chat_se_pastreaza_si_se_schimba(tmp_path):
    baza = tmp_path / "c.db"
    with server_pornit(baza) as (adresa, _):
        primit = json_de_la(adresa + "/api/mesaj", {"text": "Câți ani are Ion?"})
        raspuns = primit["raspuns"]
        assert raspuns["nota"] is None and raspuns["corectura"] is None
        numar = raspuns["id"]
        salvat = json_de_la(adresa + "/api/apreciere", {"mesaj": numar, "nota": -1, "corectura": "  Ion are 12 ani. "})
        assert salvat["mesaj"]["nota"] == -1 and salvat["mesaj"]["corectura"] == "Ion are 12 ani."
        # a doua apreciere o înlocuiește pe prima (o singură apreciere pe răspuns)
        salvat = json_de_la(adresa + "/api/apreciere", {"mesaj": numar, "nota": 1, "corectura": ""})
        assert salvat["mesaj"]["nota"] == 1 and salvat["mesaj"]["corectura"] is None
        mesaje = json_de_la(f"{adresa}/api/conversatii/{primit['conversatie']}")["mesaje"]
        assert [(m["rol"], m["nota"]) for m in mesaje] == [("om", None), ("creier", 1)]
    # după repornire, aprecierea e tot acolo
    apreciate = Catalog(baza).apreciate()
    assert [(a["fila"], a["intrebare"], a["nota"]) for a in apreciate] == [("chat", "Câți ani are Ion?", 1)]
    assert apreciate[0]["raspuns"] == CreierFals().raspunde("Câți ani are Ion?", 200)


def test_aprecierile_gresite_sunt_refuzate(tmp_path):
    with server_pornit(tmp_path / "c.db") as (adresa, _):
        primit = json_de_la(adresa + "/api/mesaj", {"text": "Salut"})
        om, creier = primit["intrebare"]["id"], primit["raspuns"]["id"]
        assert cere(adresa + "/api/apreciere", {"mesaj": om, "nota": 1})[0] == 400        # mesajul omului nu se notează
        assert cere(adresa + "/api/apreciere", {"mesaj": 9999, "nota": 1})[0] == 404
        assert cere(adresa + "/api/apreciere", {"mesaj": creier, "nota": 5})[0] == 400
        assert cere(adresa + "/api/apreciere", {"mesaj": creier, "nota": True})[0] == 400
        assert cere(adresa + "/api/apreciere", {"mesaj": "1", "nota": 1})[0] == 400
        assert cere(adresa + "/api/apreciere", {"mesaj": creier, "nota": 1, "corectura": 7})[0] == 400
        assert cere(adresa + "/api/apreciere", {"mesaj": creier, "nota": 1, "corectura": "x" * 2001})[0] == 400
        assert cere(adresa + "/api/apreciere", [1])[0] == 400
        assert cere(adresa + "/api/apreciere", {"mesaj": creier, "nota": 1}, tip="text/plain")[0] == 415
        assert cere(adresa + "/api/apreciere-text", {"intrebare": 1, "nota": 1})[0] == 404


def test_intrebarile_din_text_se_pastreaza_si_se_noteaza(tmp_path):
    baza = tmp_path / "c.db"
    creier, _ = creier_text_fals()
    with server_pornit(baza, creier_text=creier) as (adresa, _):
        primit = json_de_la(adresa + "/api/din-text", {"text": "Satul X are 500 de locuitori.",
                                                        "intrebare": "Câți locuitori are X?"})
        assert isinstance(primit["id"], int)
        salvat = json_de_la(adresa + "/api/apreciere-text", {"intrebare": primit["id"], "nota": -1,
                                                              "corectura": "X are 500 de locuitori."})
        assert salvat["intrebare"]["nota"] == -1 and salvat["intrebare"]["paragraf"] == "Satul X are 500 de locuitori."
        # fără notă și fără corectură: rândul rămâne, dar fără nimic de învățat
        a_doua = json_de_la(adresa + "/api/din-text", {"text": "Râul Y e lung.", "intrebare": "Cum e Y?"})
        json_de_la(adresa + "/api/apreciere-text", {"intrebare": a_doua["id"], "nota": None})
    apreciate = Catalog(baza).apreciate()
    assert [(a["fila"], a["nota"], a["corectura"]) for a in apreciate] == [
        ("text", -1, "X are 500 de locuitori."), ("text", None, None)]
    assert apreciate[0]["intrebare"] == "Câți locuitori are X?" and apreciate[0]["autor"] == creier.eticheta


def test_baza_veche_primeste_tabelele_noi(tmp_path):
    """O bază scrisă înainte de S118 (fără tabelele de aprecieri) se deschide și merge mai departe."""
    import sqlite3
    from contextlib import closing
    baza = tmp_path / "veche.db"
    with closing(sqlite3.connect(baza)) as legatura, legatura:
        legatura.executescript(
            "CREATE TABLE conversatii (id INTEGER PRIMARY KEY AUTOINCREMENT, titlu TEXT NOT NULL, creata TEXT NOT NULL);"
            "CREATE TABLE mesaje (id INTEGER PRIMARY KEY AUTOINCREMENT, conversatie INTEGER NOT NULL, rol TEXT NOT NULL,"
            " autor TEXT NOT NULL, text TEXT NOT NULL, creat TEXT NOT NULL, secunde REAL);"
            "INSERT INTO conversatii (titlu, creata) VALUES ('veche', '2026-11-01T10:00:00');"
            "INSERT INTO mesaje (conversatie, rol, autor, text, creat) VALUES (1, 'om', 'Tu', 'Salut', '2026-11-01T10:00:00');"
            "INSERT INTO mesaje (conversatie, rol, autor, text, creat) VALUES (1, 'creier', 'K', 'Bună', '2026-11-01T10:00:01');")
    catalog = Catalog(baza)
    assert [m["nota"] for m in catalog.mesaje(1)] == [None, None]
    catalog.apreciaza(2, 1)
    assert [(a["intrebare"], a["raspuns"], a["nota"]) for a in catalog.apreciate()] == [("Salut", "Bună", 1)]


def test_pagina_are_butoanele_si_lucru_e_in_afara_git():
    js = (RADACINA / "module" / "interfata" / "static" / "aplicatie.js").read_text(encoding="utf-8")
    assert "👍" in js and "👎" in js and "Răspunsul corect ar fi" in js
    assert "/api/apreciere" in js and "/api/apreciere-text" in js
    assert "innerHTML" not in js  # textul omului și al modelului intră doar ca text
    # conversațiile lui Adrian nu ajung în Git: baza stă în lucru/, iar lucru/ e ignorat
    try:
        rezultat = subprocess.run(["git", "check-ignore", "-q", "lucru/interfata/conversatii.db"], cwd=RADACINA,
                                  capture_output=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        pytest.skip("git nu e disponibil")
    assert rezultat.returncode == 0
