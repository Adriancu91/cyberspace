"""Tokenizerul BPE: rescrie exact orice text, învață bucățile dese, se salvează, iar memoria vede doar trecutul."""

from __future__ import annotations

import random

import pytest

from module.date_mostra import DateMostra
from module.tokenizer_bpe import BUCATI, TokenizerBPE, antreneaza_bpe

TEXT = DateMostra(propozitii=600).text_antrenare()
EXEMPLE = [
    "",
    "the cat sat on the mat.",
    "Once upon a time, “Lily” said: «hello»!\n\n  two  spaces\ttab_underscore 42 x2",
    "Diacritice: ăîșțâ ĂÎȘȚÂ, emoji 🐱🐶, chineză 猫, ½ și ²",
    "a<|endoftext|>b <|endoftext|>\n<|endoftext|>",
    "<|endoftext|>",
    "don't, we'll, it's, I'M, you're",
]


@pytest.fixture(scope="module")
def tok():
    return antreneaza_bpe(TEXT, 320)


@pytest.mark.parametrize("text", EXEMPLE)
def test_rescrie_exact_orice_text(tok, text):
    assert tok.decodeaza(tok.codifica(text)) == text


def test_bucatile_acopera_tot_textul():
    rng = random.Random(1)
    litere = "aZ09_ ,.!?'’“\n\tăș🐱猫½²-—"
    for _ in range(300):
        text = "".join(rng.choice(litere) for _ in range(rng.randint(0, 30)))
        assert "".join(BUCATI.findall(text)) == text


def test_marimea_vocabularului_si_simbolul_special(tok):
    assert tok.marime == 320 and len(tok.imbinari) == 320 - 256 - 1
    special = tok.speciale["<|endoftext|>"]
    assert special == 319
    assert tok.codifica("a<|endoftext|>b").count(special) == 1  # special, întreg, nu tăiat în bucăți


def test_bucatile_dese_devin_un_simbol(tok):
    assert len(tok.codifica(" the")) == 1
    assert len(tok.codifica(TEXT)) < len(TEXT.encode("utf-8")) / 2  # cel puțin 2 octeți pe simbol


def test_antrenarea_e_reproductibila():
    assert antreneaza_bpe(TEXT, 300).imbinari == antreneaza_bpe(TEXT, 300).imbinari


def test_salveaza_si_incarca(tok, tmp_path):
    tok.salveaza(tmp_path / "bpe.json", {"proba": True})
    copie = TokenizerBPE.incarca(tmp_path / "bpe.json")
    assert copie.imbinari == tok.imbinari and copie.speciale == tok.speciale
    for text in EXEMPLE:
        assert copie.codifica(text) == tok.codifica(text)


def test_lipsa_fisierului_da_mesaj_clar(tmp_path):
    with pytest.raises(ValueError, match="antreneaza_tokenizer"):
        TokenizerBPE.incarca(tmp_path / "nu_exista.json")


def test_marime_prea_mica():
    with pytest.raises(ValueError, match="marime"):
        antreneaza_bpe(TEXT, 100)


@pytest.mark.parametrize("text", EXEMPLE + ["ș" * 5, "a🐱b", "“Hi,” she said."])
def test_capetele_numara_doar_literele_complete(tok, text):
    """Pentru fiecare simbol: câte litere sunt scrise complet până la el inclusiv, nimic din viitor."""
    simboluri = tok.codifica(text)
    rescris, capete = tok.capete_caractere(simboluri)
    assert rescris == text
    octeti = 0
    for simbol, cap in zip(simboluri, capete):
        octeti += len(tok.octeti(simbol))
        assert len(text[:cap].encode("utf-8")) <= octeti  # literele numărate sunt scrise complet
        if cap < len(text):
            assert len(text[: cap + 1].encode("utf-8")) > octeti  # următoarea literă nu e încă completă
    assert capete == sorted(capete)
