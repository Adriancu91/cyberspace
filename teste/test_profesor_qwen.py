"""Profesorul: subiectele cu fapte, cererile, citirea notei și lucrul pe loturi, fără modelul mare (un motor de probă)."""

from __future__ import annotations

import pytest

from module.profesor_qwen import FAPTE, STILURI, SUBIECTE, ProfesorQwen, cerere_nota, cerere_poveste, citeste_nota


def test_cele_50_de_subiecte_au_cate_un_fapt():
    assert len(SUBIECTE) == 50 and len(FAPTE) == 50  # 50 de subiecte diferite
    assert all(fapt.endswith(".") and len(fapt.split()) >= 3 for _, fapt in SUBIECTE)


def test_cererea_de_poveste_are_subiectul_stilul_si_faptul():
    text = cerere_poveste("birds", "dialog")[-1]["content"]
    assert ") about birds." in text and STILURI["dialog"] in text and '"Birds have feathers."' in text
    liber = cerere_poveste("volcanic glass", "a funny rhyme")[-1]["content"]  # subiect din afara listei, stil liber
    assert "one true, simple fact about volcanic glass" in liber and "Style: a funny rhyme." in liber


def test_cererea_de_nota_are_povestea_si_forma_raspunsului():
    text = cerere_nota("  Tom had a red ball.  ")[-1]["content"]
    assert '"""\nTom had a red ball.\n"""' in text and "GRADE:" in text and "REASON:" in text
    assert all(cuvant in text for cuvant in ("coherence", "sense", "grammar"))


def test_citeste_nota():
    assert citeste_nota("GRADE: 7\nREASON: Clear, one small mistake.") == {"nota": 7, "motiv": "Clear, one small mistake."}
    assert citeste_nota("grade : 12\nreason: x")["nota"] == 10 and citeste_nota("GRADE: 0")["nota"] == 1
    assert citeste_nota("I think it is fine.") == {"nota": None, "motiv": "I think it is fine."}


class _Motor:
    """În locul modelului mare: ține minte loturile și răspunde pe loc."""

    def __init__(self) -> None:
        self.loturi: list[tuple[int, int, bool]] = []

    def __call__(self, conversatii, max_simboluri, cu_intamplare):
        self.loturi.append((len(conversatii), max_simboluri, cu_intamplare))
        if cu_intamplare:
            return [f"Story about {c[-1]['content'].split(') about ')[1].split('. Style')[0]}." for c in conversatii]
        return ["GRADE: 8\nREASON: Good." for _ in conversatii]


def test_pe_loturi_si_contractul(monkeypatch):
    profesor = ProfesorQwen(lot=3, max_simboluri=100)
    motor = _Motor()
    monkeypatch.setattr(profesor, "_raspunsuri", motor)
    povesti = profesor.genereaza_mai_multe([(subiect, "simplu") for subiect, _ in SUBIECTE[:7]])
    assert povesti[:2] == ["Story about snow.", "Story about birds."] and len(povesti) == 7
    assert motor.loturi == [(3, 100, True), (3, 100, True), (1, 100, True)]  # loturi de câte 3, cu întâmplare
    assert profesor.genereaza("cats") == "Story about cats."
    assert profesor.noteaza("A story.") == {"nota": 8, "motiv": "Good."} and motor.loturi[-1] == (1, 60, False)
    exercitii = profesor.genereaza_exercitii("bees", 4)
    assert [e["stil"] for e in exercitii] == ["simplu", "dialog", "morala", "problema"]
    assert all(e == {"subiect": "bees", "stil": e["stil"], "fapt": FAPTE["bees"], "poveste": "Story about bees."}
               for e in exercitii)


def test_setari_invalide():
    for setari in ({"lot": 0}, {"max_simboluri": 0}, {"temperatura": 0.0}):
        with pytest.raises(ValueError):
            ProfesorQwen(**setari)


def test_personajul_intra_in_cerere():
    text = cerere_poveste("owls", "seara", "a curious puppy")[-1]["content"]
    assert "The main character is a curious puppy." in text and STILURI["seara"] in text
    assert "main character" not in cerere_poveste("owls", "seara")[-1]["content"]
