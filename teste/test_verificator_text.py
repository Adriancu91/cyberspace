"""Verificatorul fără LLM pentru „răspuns din text” (S16, 22 octombrie 2026): regulile exacte din coadă."""

from unelte.verificator_text import normalizeaza, verifica


def test_normalizarea():
    assert normalizeaza("  „Ştefan”   cel  Mare, din Ţara! ") == "ștefan cel mare din țara"
    assert normalizeaza("Pe 28 mai 1991.") == "pe 28 mai 1991"


def test_exact():
    v = verifica("Pe 28 mai 1991.", "pe 28 mai 1991")
    assert v["corect"] and v["motiv"] == "exact" and v["corect_f1"]


def test_diacritice_cu_sedila_si_virgula_sunt_la_fel():
    assert verifica("În Țara Românească.", "În Ţara Românească.")["motiv"] == "exact"


def test_diacriticele_raman():
    v = verifica("În Brașov.", "In Brasov.")
    assert not v["corect"] and v["acoperire"] == 0.0


def test_punctuatia_si_ghilimelele_nu_conteaza():
    assert verifica("Romanul „Ion”, de Liviu Rebreanu.", "Romanul Ion de Liviu Rebreanu")["corect"]


def test_raspuns_lung_care_contine_referinta():
    v = verifica("În Elveția.", "Peștera se află în Elveția, în cantonul Berna, la mare altitudine.")
    assert v["corect"] and v["acoperire"] == 1.0
    assert not v["corect_f1"]  # F1 pedepsește răspunsul lung


def test_repetarea_intrebarii_nu_ajunge():
    v = verifica("Pe 28 mai 1991.", "Când a venit pe lume Magda Alfredo Cazanga?")
    assert not v["corect"] and v["acoperire"] == 0.25  # doar „pe” se potrivește


def test_acoperire_partiala_sub_prag():
    v = verifica("Pe 28 mai 1991.", "În 1991.")
    assert not v["corect"] and v["acoperire"] == 0.25


def test_acoperirea_numara_repetitiile():
    v = verifica("Ana și Ana au plecat.", "Ana au plecat.")
    assert v["acoperire"] == 0.6 and not v["corect"]


def test_nu_scrie_in_text_corect():
    v = verifica("Nu scrie în text.", "Nu scrie în text.")
    assert v["corect"]
    assert verifica("Nu scrie în text.", "nu scrie in text")["corect"] is False  # fără diacritice nu e același text
    assert verifica("Nu scrie în text.", "Nu scrie în text, din păcate.")["corect"]


def test_nu_scrie_in_text_pe_nedrept():
    v = verifica("Pe 28 mai 1991.", "Nu scrie în text.")
    assert not v["corect"] and not v["corect_f1"] and v["motiv"] == "refuz"


def test_refuz_cu_cuvintele_referintei_ramane_greseala():
    v = verifica("Nu scrie.", "Nu scrie în text.")
    assert not v["corect"]


def test_referinta_nu_scrie_si_raspuns_inventat():
    v = verifica("Nu scrie în text.", "În 2019.")
    assert not v["corect"] and v["motiv"] == "special_nu_scrie"


def test_da_si_nu():
    assert verifica("Da.", "Da, a câștigat medalia.")["corect"]
    assert not verifica("Da.", "Nu.")["corect"]
    assert verifica("Nu.", "Nu, nu a participat.")["corect"]
    assert not verifica("Nu.", "Nu scrie în text.")["corect"]
    assert verifica("Da, în 1990.", "Da.")["corect"]
    assert not verifica("Nu, în Franța.", "Da, în Franța.")["corect"]


def test_referinta_de_un_cuvant():
    assert verifica("Bucureștiului.", "Este capitala Bucureștiului.")["corect"]
    assert not verifica("Bucureștiului.", "Este capitala Clujului.")["corect"]


def test_raspuns_gol():
    v = verifica("Pe 28 mai 1991.", "")
    assert not v["corect"] and not v["corect_f1"] and v["scor"] == 0.0
    assert not verifica("Da.", "   ")["corect"]


def test_f1_scurt_si_bun():
    v = verifica("Prințesa Maria a fost mama împăratului Carol.", "Maria a fost mama împăratului Carol.")
    assert v["corect"] and v["corect_f1"]
