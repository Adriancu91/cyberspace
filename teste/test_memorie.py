"""Memoria ierarhică: coduri corecte, plasa ține minte drumurile, iar modelul nu primește viitorul."""

from __future__ import annotations

import gzip
import json

import pytest

from module.memorie_ierarhica import GOL, NECUNOSCUT, MemorieIerarhica
from teste.biblioteca_mica import biblioteca_mica


@pytest.fixture
def memorie(tmp_path):
    return MemorieIerarhica(cale=biblioteca_mica(tmp_path), nivele=8)


def test_codul_e_locul_din_biblioteca(memorie):
    cod = memorie.cod("horse")
    assert len(cod) == 8
    assert cod[0] == 1  # substantiv
    assert cod[6:] == (GOL, GOL)  # entity > organism > animal > horse: 2 + 4 niveluri, restul gol
    assert memorie.cod("HORSE") == cod


def test_cuvintele_inrudite_impart_inceputul_codului(memorie):
    cal, pisica, sabie = memorie.cod("horse"), memorie.cod("cat"), memorie.cod("sword")
    assert cal[:5] == pisica[:5]  # același raft (noun.animal) și aceiași strămoși
    assert cal[5] != pisica[5]
    assert cal[1] != sabie[1]  # rafturi diferite


@pytest.mark.parametrize(
    "forma,baza",
    [
        ("horses", "horse"), ("horse's", "horse"), ("Horses", "horse"), ("swords", "sword"),
        ("hooves", "hoof"), ("ran", "run"),  # forme neregulate, din bibliotecă
        ("running", "run"), ("runneth", "run"), ("galloping", "gallop"), ("galloped", "gallop"),
        ("gallopeth", "gallop"), ("gallop'st", "gallop"), ("gallop'd", "gallop"),
    ],
)
def test_formele_ajung_la_cuvantul_de_baza(memorie, forma, baza):
    assert memorie.cod(forma) == memorie.cod(baza)
    assert memorie.cod(forma)[0] != NECUNOSCUT


def test_cuvant_necunoscut(memorie):
    assert memorie.cod("thee") == (NECUNOSCUT,) + (GOL,) * 7
    assert memorie.cauta("thee") == []


def test_cauta_arata_drumul_si_relatiile(memorie):
    sensuri = memorie.cauta("horses")
    assert len(sensuri) == 3  # animalul, calul de gimnastică, verbul
    cal = sensuri[0]
    assert cal["drum"] == ["entity", "organism", "animal", "horse"]
    assert cal["raft"] == "noun.animal" and cal["parte_de_vorbire"] == "substantiv"
    assert {"tip": "are_parte", "catre": "hoof"} in cal["relatii"]
    assert {"tip": "membru_din", "catre": "herd"} in cal["relatii"]
    assert sensuri[2]["parte_de_vorbire"] == "verb"


def test_plasa_tine_minte_drumurile_si_folosirile(memorie):
    memorie.caracteristici("the horse and the horse ran ")
    stat = memorie.statistici()
    assert stat["cautari"] == 6  # the, horse, and, the, horse, ran
    assert stat["drumuri_in_plasa"] == 4  # the, horse, and, ran: fiecare drum ținut minte o singură dată
    assert stat["acoperire"] == pytest.approx(3 / 6)  # horse de două ori și ran; the și and nu sunt în WordNet
    assert set(stat["cele_mai_folosite"][:2]) == {"the", "horse"}
    assert stat["necunoscute_frecvente"][0] == "the"


def test_un_cod_pe_fiecare_litera(memorie):
    text = "A horse ran, a cat ran.\n"
    coduri = memorie.caracteristici(text)
    assert len(coduri) == len(text)
    assert all(len(c) == memorie.nivele for c in coduri)


def test_memoria_nu_dezvaluie_viitorul(memorie):
    """Cel mai important test: codul de la litera i depinde DOAR de literele 0..i.

    Dacă ar depinde de ce urmează (de ex. de cuvântul în curs de scriere), modelul ar trișa la examen.
    """
    text = "The horse ran to the sword. A cat's tail, horses' hooves! gallop'st 42times\n'tis HORSE--o'clock''x run"
    complet = memorie.caracteristici(text)
    for i in range(len(text) + 1):
        assert memorie.caracteristici(text[:i]) == complet[:i], f"scurgere din viitor la poziția {i}"


def test_cuvantul_intra_doar_dupa_ce_s_a_terminat(memorie):
    coduri = memorie.caracteristici("horse ran")
    gol = (GOL,) * 8
    assert coduri[:5] == [gol] * 5  # „horse” încă se scrie
    assert coduri[5:] == [memorie.cod("horse")] * 4  # la spațiu e gata; „ran” nu s-a terminat încă


def test_apostroful_din_interior_si_de_la_final(memorie):
    coduri = memorie.caracteristici("gallop'st horses' x")
    assert coduri[6] == coduri[0]  # apostroful: încă nu știm dacă cuvântul continuă
    assert coduri[9] == memorie.cod("gallop")  # „gallop'st” s-a terminat la spațiu
    assert coduri[17] == memorie.cod("horse")  # „horses'”: apostroful era la final


def test_lipsa_bibliotecii_da_mesaj_clar(tmp_path):
    with pytest.raises(ValueError, match="construieste_biblioteca"):
        MemorieIerarhica(cale=str(tmp_path / "nu_exista.json.gz"))


def test_biblioteca_veche_da_mesaj_clar(tmp_path):
    cale = tmp_path / "veche.json.gz"
    with gzip.open(cale, "wt", encoding="utf-8") as f:
        json.dump({"versiune": 99}, f)
    with pytest.raises(ValueError, match="versiunea 99"):
        MemorieIerarhica(cale=str(cale))


def test_nivele_invalide(tmp_path):
    with pytest.raises(ValueError, match="nivele"):
        MemorieIerarhica(cale=biblioteca_mica(tmp_path), nivele=0)


def test_coduri_cuvinte_da_cuvintele_terminate_in_ordine(memorie):
    coduri = memorie.coduri_cuvinte("the horse ran, the cat's tail; gallop'st no")
    asteptat = [memorie.cod(c) for c in ("the", "horse", "ran", "the", "cat", "tail", "gallop")]
    assert coduri == asteptat  # „no” e încă în curs: nu intră
