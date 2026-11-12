"""S107: renotarea examenului de conversație — „Nu scrie în text.” corect la întrebările „nu știu”."""

import hashlib
import json

from unelte.renoteaza_conversatie import renoteaza, renoteaza_fisier


def _p(fel, raspuns, nota, corect=False):
    return {"fel": fel, "intrebare": "?", "raspuns": "ref", "raspuns_elev": raspuns, "nota_elev": nota,
            "nu_stiu_corect": corect, "limba": "ro"}


def test_nu_scrie_la_nu_stiu_e_corect():
    noi, s = renoteaza([_p("nu_stiu", "Nu scrie în text.", 1)])
    assert noi[0]["nu_stiu_corect"] is True and noi[0]["nu_stiu_corect_vechi"] is False
    assert s["nu_stiu_corecte_vechi"] == 0 and s["nu_stiu_corecte_nou"] == 1


def test_nu_stiu_ramane_corect():
    _, s = renoteaza([_p("nu_stiu", "Nu știu.", 1, corect=True)])
    assert s["nu_stiu_corecte_vechi"] == 1 and s["nu_stiu_corecte_nou"] == 1


def test_raspuns_inventat_e_gresit():
    _, s = renoteaza([_p("nu_stiu", "Capitala este Brașovul, fondată în 1200.", 1)])
    assert s["nu_stiu_corecte_nou"] == 0


def test_la_intrebari_stiute_nota_nu_se_schimba():
    intrare = [_p("wiki", "Nu scrie în text.", 1), _p("wiki", "București.", 9), _p("conversatie", "Bună!", 8)]
    noi, s = renoteaza(intrare)
    assert [p["nota_elev"] for p in noi] == [1, 9, 8]
    assert [p["nu_stiu_corect"] for p in noi] == [False, False, False]
    assert s["corecte_wiki"] == 1 and s["refuzuri_la_stiute"] == 1 and s["nu_scrie_la_stiute"] == 1
    assert s["nota_medie_fara_nu_stiu"] == 6.0


def test_fisierul_de_intrare_ramane_neschimbat(tmp_path):
    cale = tmp_path / "experiment_1.json"
    cale.write_text(json.dumps({"experiment": 1, "linie": "x", "raspunsuri": [
        _p("nu_stiu", "Nu scrie în text.", 1), _p("wiki", "Da.", 7)]}, ensure_ascii=False), encoding="utf-8")
    inainte = hashlib.sha256(cale.read_bytes()).hexdigest()
    iesire, s = renoteaza_fisier(cale, tmp_path / "renotat")
    assert hashlib.sha256(cale.read_bytes()).hexdigest() == inainte
    assert iesire.exists() and json.loads(iesire.read_text(encoding="utf-8"))["nu_stiu_corecte_nou"] == 1
