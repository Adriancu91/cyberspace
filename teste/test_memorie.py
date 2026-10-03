"""Memoria ierarhică: coduri corecte, plasa ține minte drumurile, iar modelul nu primește viitorul."""

from __future__ import annotations

import gzip
import json

import pytest

from module import memorie_ierarhica
from module.memorie_ierarhica import (
    ADVERBE_PREFERATE, EXCEPTII_FORME_VERB, GOL, INAINTE_DE_VERB, NECUNOSCUT, MemorieIerarhica,
)
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


# --- setarea sens_dupa_context (regulile a, b, c, d) --------------------------------------------


@pytest.fixture
def context(tmp_path):
    """Memoria cu sensul ales după context și cuvintele de legătură ca umplutură (ca la măsurarea rafturilor)."""
    return MemorieIerarhica(
        cale=biblioteca_mica(tmp_path), nivele=8, fara_cuvinte_de_legatura=True, sens_dupa_context=True
    )


def _raft(memorie, cod):
    return None if cod[0] == NECUNOSCUT else memorie.rafturi[cod[1] - 1]


def test_fara_setare_ramane_sensul_din_dictionar(memorie):
    coduri = memorie.coduri_cuvinte("Horse saw Horse back, horsing. ")
    assert [_raft(memorie, c) for c in coduri] == ["noun.animal", "noun.artifact", "noun.animal", "noun.body", "noun.animal"]


def test_regula_a_formele_de_verb(memorie, context):
    assert _raft(context, context.cod("saw")) == "verb.perception"  # forma listată a lui „see”, nu fierăstrăul
    assert _raft(context, context.cod("horsing")) == "verb.motion"  # -ing cu baza verb: verbul „horse”, nu calul
    assert context.cod("horsed") == context.cod("horsing")
    assert _raft(context, context.cod("seeing")) == "verb.perception"
    assert context.cod("galloped") == context.cod("gallop")
    assert context._verbe_din_baza("seed") == []  # „-eed” fără vocală înainte nu e formă de verb (seed, need)
    assert context._verbe_din_baza("sing") == []  # nici „-ing” fără vocală în bază (sing, thing)
    assert context.cod("horse") == memorie.cod("horse")  # cuvântul de bază rămâne cum era


def test_regula_c_adverbele_din_lista(memorie, context):
    assert "back" in ADVERBE_PREFERATE and "little" not in ADVERBE_PREFERATE
    assert _raft(memorie, memorie.cod("back")) == "noun.body"
    assert _raft(context, context.cod("back")) == "adv.all"
    assert context.cauta("back")[0]["parte_de_vorbire"] == "adverb"  # căutarea arată întâi sensul ales


def test_inceputul_propozitiei_se_vede_doar_in_urma():
    text = 'Tom ran. Tom saw Tom, "Tom ran," Tom said!\nTom '
    assert [(c, la_inceput) for _, c, la_inceput in MemorieIerarhica.cuvinte_terminate(text)] == [
        ("Tom", True), ("ran", False), ("Tom", True), ("saw", False), ("Tom", False),
        ("Tom", True), ("ran", False), ("Tom", False), ("said", False), ("Tom", True),
    ]


def test_regula_b_numele_din_mijlocul_propozitiei(context):
    coduri = context.coduri_cuvinte("Horse saw Horse with Timmy and Girl. ")
    assert [_raft(context, c) for c in coduri] == [
        "noun.animal", "verb.perception", "noun.person", None, "noun.person", None, "noun.person"
    ]
    persoana = coduri[2]
    assert coduri[4] == persoana  # „Timmy” nu e în bibliotecă, dar e tot un nume
    assert persoana[2:] == context.cod("person")[2:]  # drumul lui „person”, pus pe raftul noun.person
    assert coduri[6] == context.cod("girl")  # stătea deja pe noun.person: își păstrează codul
    assert context.cod("Horse") == context.cod("horse")  # luat singur, cuvântul e ca la început de propoziție


def test_numele_tinute_minte_doar_din_acelasi_text(context):
    text = 'Timmy ran. Horse ran with Timmy. Timmy ran. She said, "Horse ran," Horse said. Horse\'s cat ran. '
    assert [_raft(context, c) for c in context.coduri_cuvinte(text)] == [
        None, "verb.motion",  # Timmy ran: încă nu știm că e un nume
        "noun.animal", "verb.motion", None, "noun.person",  # Horse ran with Timmy: acum știm
        "noun.person", "verb.motion",  # Timmy ran: ținut minte
        None, None, "noun.animal", "verb.motion",  # She said, "Horse ran,": „Horse” încă n-a fost nume
        "noun.person", None,  # Horse said
        "noun.person", "noun.animal", "verb.motion",  # Horse's cat ran: ținut minte și cu „'s”
    ]
    assert _raft(context, context.coduri_cuvinte("Timmy ran. ")[0]) is None  # alt text: nu ține minte nimic
    # Povești lipite în același text: numele se țin minte doar până la separatorul dintre ele.
    povesti = "Horse ran with Timmy. Timmy ran.\n<|endoftext|>\nTimmy ran. "
    assert [_raft(context, c) for c in context.coduri_cuvinte(povesti)] == [
        "noun.animal", "verb.motion", None, "noun.person", "noun.person", "verb.motion", None, None, "verb.motion"
    ]


def test_majusculele_si_cuvintele_de_legatura_nu_sunt_nume(context):
    coduri = context.coduri_cuvinte("the cat ran with TV and CAT. I ran. ")
    assert [_raft(context, c) for c in coduri] == [
        None, "noun.animal", "verb.motion", None, None, None, "noun.animal", None, "verb.motion"
    ]


def test_regula_d_verbul_dupa_to_i_you(context):
    text = "they horse. we. horse the horse, to horse; let's horse don't horse I back. "
    coduri = context.coduri_cuvinte(text)
    assert [_raft(context, c) for c in coduri] == [
        None, "verb.motion",  # they horse
        None, "noun.animal",  # we. horse: altă propoziție, regula nu se aplică
        None, "noun.animal",  # the horse
        None, "verb.motion", None, "verb.motion", None, "verb.motion",  # to / let's / don't horse
        None, "adv.all",  # I back: adverbele din listă rămân adverbe
    ]
    assert INAINTE_DE_VERB == {"to", "will", "can", "let's", "don't", "i", "you", "we", "they"}


def test_regula_a_exceptiile_raman_pe_sensul_din_dictionar(tmp_path, monkeypatch):
    cale = biblioteca_mica(tmp_path)
    assert EXCEPTII_FORME_VERB == {"ground", "feed", "wound", "bit"}
    context = MemorieIerarhica(cale=cale, nivele=8, sens_dupa_context=True)
    assert _raft(context, context.cod("bit")) == "noun.artifact"  # burghiul, nu trecutul lui „bite”
    monkeypatch.setattr(memorie_ierarhica, "EXCEPTII_FORME_VERB", frozenset())
    fara_exceptii = MemorieIerarhica(cale=cale, nivele=8, sens_dupa_context=True)
    assert _raft(fara_exceptii, fara_exceptii.cod("bit")) == "verb.contact"  # fără excepție, regula a) l-ar muta


def test_regulile_spun_ce_au_ales(context):
    text = "Horse saw Horse. Horse ran back, they horse. "
    assert [regula for _, _, _, regula in context.cuvinte_cu_coduri(text)] == [
        "", "a_forma_de_verb", "b_nume", "b_nume_tinut_minte", "a_forma_de_verb", "c_adverb", "", "d_verb_dupa"
    ]


def test_sensul_dupa_context_nu_dezvaluie_viitorul(context):
    text = (
        "Horse saw Timmy. \"Back, Horse!\" said Girl, horsing back; seeing Cat ran.\nTimmy's horses' hooves, "
        "Horse to horse, they bit TV and CAT. Timmy ran, I saw.\n<|endoftext|>\nTimmy ran. Let's horse"
    )
    complet = context.caracteristici(text)
    for i in range(len(text) + 1):
        assert context.caracteristici(text[:i]) == complet[:i], f"scurgere din viitor la poziția {i}"


def test_sensul_dupa_context_cere_formele_de_verb(tmp_path):
    with gzip.open(biblioteca_mica(tmp_path), "rt", encoding="utf-8") as f:
        biblioteca = json.load(f)
    del biblioteca["forme_verb"]  # o bibliotecă construită înainte de regula a)
    cale = tmp_path / "fara_forme_verb.json.gz"
    with gzip.open(cale, "wt", encoding="utf-8") as f:
        json.dump(biblioteca, f)
    MemorieIerarhica(cale=str(cale))  # fără setare merge ca înainte
    with pytest.raises(ValueError, match="construieste_biblioteca"):
        MemorieIerarhica(cale=str(cale), sens_dupa_context=True)
