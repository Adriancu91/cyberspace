"""Raportul buclei de auto-îmbunătățire: tabelul, cel mai bun scor, direcțiile și cele două comparații curate."""

from __future__ import annotations

from unelte.raport_bucla import de, mii, raport, randuri_din, schimbarea

BAZA = {"n_straturi": 10, "n_capete": 8, "n_emb": 640, "context": 256, "lot": 16, "rata_invatare": 0.0003}


def _fisa(id_, descriere, model, scor, decizie, castig=None, scor_la_pornire=None, minute=5.0):
    return {
        "id": id_, "inceput": f"2026-10-04T13:{id_ * 7:02d}:00+00:00", "durata_totala_secunde": 420,
        "propunere": {"descriere": descriere, "modificari": {}}, "setari": {"model": {**BAZA, **model}},
        "statistici_antrenare": {"parametri": 52_000_000, "continuat": scor_la_pornire is not None,
                                 "scor_la_pornire": scor_la_pornire, "minute_total": minute, "pasi": 1000,
                                 "pasi_total": int(200 * minute), "memorie_rezervata_mb": 3000 + id_},
        "scoruri": {"val_bpb": scor}, "castig": castig, "decizie": decizie,
    }


FISE = [
    _fisa(1, "punct de plecare (setările din configurare)", {}, 1.50, "pastrat"),
    _fisa(2, "lista: model.rata_invatare: 0.0003 → 0.0005", {"rata_invatare": 0.0005}, 1.40, "pastrat", 0.10, 1.50, 10.0),
    _fisa(3, "lista: model.n_emb: 640 → 768", {"n_emb": 768, "rata_invatare": 0.0005}, 1.45, "respins", -0.05),
    _fisa(4, "lista: model.lot: 16 → 24", {"lot": 24, "rata_invatare": 0.0005}, 1.38, "pastrat", 0.02, 1.40, 15.0),
    _fisa(5, "lista: model.lot: 24 → 8", {"lot": 8, "rata_invatare": 0.0005}, 1.39, "respins", -0.01, 1.38, 20.0),
    _fisa(6, "strângere în jurul locului 3 (#2, scor 1.4000): model.rata_invatare: 0.0005 → 0.0004",
          {"rata_invatare": 0.0004}, 1.37, "pastrat", 0.01, 1.38, 20.0),
]


def test_schimbarea_din_descriere():
    assert schimbarea(FISE[0]) == {"faza": "pornire", "setare": None, "veche": None, "noua": None, "baza": None}
    assert schimbarea(FISE[1]) == {"faza": "lista", "setare": "rata_invatare", "veche": 0.0003, "noua": 0.0005, "baza": None}
    assert schimbarea(FISE[5]) == {"faza": "strângere", "setare": "rata_invatare", "veche": 0.0005, "noua": 0.0004, "baza": 2}


def test_castigul_fata_de_baza_si_de_stare():
    randuri = {r["id"]: r for r in randuri_din(FISE)}
    assert randuri[2]["fata_de_baza"] == 0.10  # lista: față de cea mai bună rețetă de atunci (câștigul lui Kronos)
    assert abs(randuri[6]["fata_de_baza"] - 0.03) < 1e-9  # strângere: față de #2, rețeta din jurul căreia a căutat
    assert abs(randuri[6]["fata_de_stare"] - 0.01) < 1e-9 and randuri[3]["fata_de_stare"] is None  # #3: de la zero


def test_raportul():
    text = raport(FISE, "bucla_gpt")
    assert "- 6 experimente în 0,7 ore; 4 păstrate; lista s-a epuizat înainte de #6" in text
    assert "- Păstrate, dintre continuări (din starea arhitecturii lor): 3 din 4." in text
    assert "- Păstrate, dintre rețete pornite de la zero: 0 din 1." in text  # fără punctul de plecare
    assert "Cel mai bun scor: **1,3700** val_bpb (#6: 10×640 · c256 · lot 16 · 0,0004, 52,0 M; 20 minute" in text
    assert "20 minute de antrenare în spate, 4.000 pași), față de 1,5000 la punctul de plecare (#1): -0,1300." in text
    assert ("| 3 | lista | lățime: 640 → 768 | 10×768 · c256 · lot 16 · 0,0005 | 52,0 M | de la zero | 1.000 (4,1 M) "
            "| 5 | 1,4500 | -0,0500 | respins |") in text  # 1.000 pași × lot 16 × context 256 = 4,1 M simboluri
    assert "| 2 | lista | rata: 0,0003 → 0,0005 |" in text
    assert "| din starea cu 1,5000 | 1.000 (4,1 M) | 10 | 1,4000 | +0,1000 | **păstrat** |" in text
    assert "| rata ↑ | 1 | 0 | 1 (#2) | 1 | +0,1000 (#2: rata: 0,0003 → 0,0005) |" in text
    assert "| lățime ↑ | 1 | 1 | 0 | 0 | -0,0500 (#3: lățime: 640 → 768) |" in text
    assert "| 1 | 3 | 10×768 · c256 · lot 16 · 0,0005 | 52,0 M | 1.000 (4,1 M) | 1,4500 |" in text  # #3 înaintea lui #1
    assert "- 10×640 · c256, din starea cu 1,3800: #6 lot 16, rata 0,0004 → 1,3700 (+0,0100); #5 lot 8, rata 0,0005 → 1,3900 (-0,0100)" in text
    assert "Memoria video rezervată, cel mai mult: 3.006 MB." in text


def test_jurnal_gol_plural_si_mii():
    assert "nu are încă experimente" in raport([], "bucla_gpt")
    assert (de(7), de(19), de(20), de(21), de(101), de(120)) == ("", "", "de ", "de ", "", "de ")
    assert (mii(23368), mii(999), mii(None), mii(True)) == ("23.368", "999", "–", "–")
