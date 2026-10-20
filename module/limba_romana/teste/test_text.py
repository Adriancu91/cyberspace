"""Tokenizare, segmentare, normalizare (convențiile UD RRT pentru cratimă)."""

from ..text import are_diacritice, fara_diacritice, normalizeaza, segmenteaza_propozitii, tokenizeaza


def tok(t: str) -> list[str]:
    return [x.text for x in tokenizeaza(t)]


def test_sedile_si_normalizare():
    assert normalizeaza("Şcoală ŢARĂ") == "școală țară"
    assert fara_diacritice("Măgură șțâî") == "magura stai"
    assert are_diacritice("mașină") and not are_diacritice("masina")


def test_clitice_ca_in_ud():
    assert tok("s-a dus într-un oraș") == ["s-", "a", "dus", "într-", "un", "oraș"]
    assert tok("n-am văzut-o") == ["n-", "am", "văzut", "-o"]
    assert tok("Dă-mi-l") == ["Dă", "-mi", "-l"]
    assert tok("mi-a spus și-l vede") == ["mi-", "a", "spus", "și", "-l", "vede"]
    assert tok("nu-i să-și") == ["nu", "-i", "să", "-și"]
    assert tok("ce-a zis") == ["ce", "-a", "zis"]
    assert tok("de-a lungul") == ["de-", "a", "lungul"]


def test_sigle_si_articole_legate():
    assert tok("ADN-ul lui") == ["ADN", "-ul", "lui"]
    assert tok("site-ul pH-ului") == ["site", "-ul", "pH", "-ului"]
    assert tok("al 3-lea") == ["al", "3", "-lea"]
    assert tok("H7N3 L-Dopa bine-cunoscut într-adevăr") == ["H7N3", "L-Dopa", "bine-cunoscut", "într-adevăr"]


def test_numere_abrevieri_punctuatie():
    assert tok("Costă 3,5% din 1.000 lei la 14:30.") == ["Costă", "3,5%", "din", "1.000", "lei", "la", "14:30", "."]
    assert tok("dr. Pop și Penelope Cruz.") == ["dr.", "Pop", "și", "Penelope", "Cruz", "."]
    assert tok("S.A. a venit") == ["S.A.", "a", "venit"]
    assert tok("4. Se adaugă") == ["4.", "Se", "adaugă"]
    assert tok("prin 1878–1879, anii ’70") == ["prin", "1878–1879", ",", "anii", "’70"]
    assert tok("György și Škoda") == ["György", "și", "Škoda"]


def test_spatiu_dupa():
    t = tokenizeaza("Vine, pleacă.")
    assert [(x.text, x.spatiu_dupa) for x in t] == [("Vine", False), (",", True), ("pleacă", False), (".", False)]


def test_segmentare():
    p = segmenteaza_propozitii("A venit dr. Pop. Apoi a plecat! Unde? Acolo.")
    assert [x[2] for x in p] == ["A venit dr. Pop.", "Apoi a plecat!", "Unde?", "Acolo."]
    assert p[1][0] == 17 and p[1][1] == 31
