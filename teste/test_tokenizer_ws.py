"""Tokenizer-ul workstation-ului (regulile „ws” din module/tokenizer_bpe.py) și unealta care îl antrenează."""

import re

import pytest

from module.tokenizer_bpe import (
    BUCATI_WS, TokenizerBPE, antreneaza_bpe, antreneaza_din_frecvente, frecvente_bucati, imbinari_numere,
)
from unelte.antreneaza_tokenizer_ws import acoperire, cu_forma_fara_spatiu, text_numere

TEXT = ('She said "moon" and (stars). x=1234, 46 + 007 = 53.\n'
        "În România sunt 19053815 de oameni, ș.a.m.d.\n"
        '  print("hi", a_b[12])  # ٣٤ și ½ și 😀\n') * 30


def tokenizer(marime_invatata: int = 200) -> TokenizerBPE:
    return antreneaza_din_frecvente(frecvente_bucati(TEXT, reguli="ws"), 256 + 1100 + marime_invatata + 1, reguli="ws")


def bucati(tok: TokenizerBPE, text: str) -> list[str]:
    return [tok.octeti(s).decode("utf-8") for s in tok.codifica(text)]


def test_bucatile_ws_acopera_tot_textul():
    assert "".join(BUCATI_WS.findall(TEXT)) == TEXT


def test_numerele_0_999_sunt_cate_un_simbol():
    tok = tokenizer()
    for k in range(1000):
        assert bucati(tok, str(k)) == [str(k)]
    assert bucati(tok, "007") == ["007"] and bucati(tok, "05") == ["05"]  # și cu zerouri în față


def test_numerele_lungi_se_taie_in_grupe_de_trei_de_la_stanga():
    tok = tokenizer()
    assert bucati(tok, "1234") == ["123", "4"]
    assert bucati(tok, "19053815") == ["190", "538", "15"]


def test_numarul_e_acelasi_simbol_oriunde_ar_sta():
    tok = tokenizer()
    patruzeci_si_sase = tok.codifica("46")
    assert len(patruzeci_si_sase) == 1
    for text in ("x = 46", "(46)", "=46", "a\n46", '"46"', "x 46"):
        assert patruzeci_si_sase[0] in tok.codifica(text)
        assert sum(1 for b in bucati(tok, text) if re.fullmatch(r"\d+", b)) == 1  # spațiul nu se lipește de număr


def test_textul_se_rescrie_exact():
    tok = tokenizer()
    assert tok.decodeaza(tok.codifica(TEXT)) == TEXT
    assert 256 + 1100 + 1 < tok.marime <= 256 + 1100 + 200 + 1  # textul mic poate avea mai puține lipiri de învățat


def test_salvat_si_incarcat_ramane_la_fel(tmp_path):
    tok = tokenizer()
    tok.salveaza(tmp_path / "ws.json")
    copie = TokenizerBPE.incarca(tmp_path / "ws.json")
    assert copie.reguli == "ws" and copie.codifica(TEXT) == tok.codifica(TEXT)
    assert copie.ca_dictionar()["versiune"] == 2 and copie.ca_dictionar()["reguli"] == "ws"


def test_regulile_vechi_raman_cum_erau(tmp_path):
    vechi = antreneaza_bpe(TEXT, 400)
    assert vechi.reguli == "gpt2" and list(vechi.ca_dictionar()) == ["versiune", "imbinari", "speciale"]
    assert vechi.ca_dictionar()["versiune"] == 1
    assert bucati(vechi, " 46") != [" ", "46"]  # la regulile vechi spațiul rămâne în bucata numărului
    vechi.salveaza(tmp_path / "vechi.json")
    assert TokenizerBPE.incarca(tmp_path / "vechi.json").codifica(TEXT) == vechi.codifica(TEXT)


def test_ws_fara_lipirile_numerelor_e_refuzat():
    with pytest.raises(ValueError, match="numerelor"):
        TokenizerBPE([(104, 105)], reguli="ws")
    with pytest.raises(ValueError, match="reguli"):
        TokenizerBPE([], reguli="altceva")
    assert len(imbinari_numere()) == 1100
    with pytest.raises(ValueError, match="cel puțin"):
        antreneaza_din_frecvente({"abc": 3}, 1000, reguli="ws")


def test_forma_fara_spatiu_primeste_o_parte_din_aparitii():
    f = cu_forma_fara_spatiu({" moon": 100.0, " a": 50.0, " x1": 40.0, "rar": 1.0}, 0.5)
    assert f[" moon"] == 100.0 and f["moon"] == 50.0
    assert "a" not in f and "x1" not in f  # doar cuvintele din litere, de cel puțin 2 litere
    assert "rar" not in f                  # sub frecvența minimă


def test_cuvantul_ramane_intreg_si_dupa_ghilimele():
    text = "the moon is far. the moon is big. look at the moon tonight. " * 40
    cu = antreneaza_din_frecvente(cu_forma_fara_spatiu(frecvente_bucati(text, reguli="ws"), 1.0), 256 + 1100 + 60 + 1, reguli="ws")
    assert bucati(cu, '"moon"') == ['"', "moon", '"']
    assert acoperire(cu, ["moon"]) == {"cuvinte": 1, "o_bucata_cu_spatiu": 1, "o_bucata_fara_spatiu": 1,
                                        "cel_mult_2_bucati_fara_spatiu": 1}


def test_calculele_din_textul_cu_numere_sunt_corecte():
    text = text_numere(200_000, samanta=3)
    assert text == text_numere(200_000, samanta=3)  # aceeași sămânță, același text
    verificate = 0
    for rand in text.splitlines():
        m = re.fullmatch(r"(\d+) ([-+*/]) (\d+) = (\d+)", rand)
        if m:
            a, semn, b, c = int(m[1]), m[2], int(m[3]), int(m[4])
            assert c == (a + b if semn == "+" else a - b if semn == "-" else a * b if semn == "*" else a // b)
            verificate += 1
    assert verificate > 60  # adunările, scăderile, înmulțirile și împărțirile simple sunt doar unul din multe feluri
