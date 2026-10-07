"""Examenul de fapte nou: propoziții reformulate de profesor, verificate să nu apară (nici pe bucăți de 5 cuvinte) în
textele de antrenare; dat elevului ca examenul vechi. Fără placă video: un profesor și un elev de probă."""

from __future__ import annotations

import json

import pytest

pytest.importorskip("numpy")

from module import examene_elev  # noqa: E402
from module.examene_elev import INTREBARI  # noqa: E402
from teste.test_bucla_cinstita import config_mic, fise  # noqa: E402
from unelte import antrenare_lunga  # noqa: E402
from unelte import examen_fapte_nou as unealta  # noqa: E402
from unelte.examen_fapte_nou import IndexFragmente, cu_gol, genereaza, linii_curate, probleme  # noqa: E402


def index_din(text: str) -> IndexFragmente:
    index = IndexFragmente(5)
    index.adauga_text(text)
    return index.gata()


def test_indexul_gaseste_fragmentele_de_5_cuvinte():
    index = index_din("Once upon a time, when it is very cold, the water turns into ice. <|endoftext|> Birds fly.")
    assert index.gasite("When it is very cold, water turns into ice.") == ["when it is very cold"]  # fără semne
    assert index.gasite("A bird's body is covered with feathers.") == []
    assert index.gasite("Ice forms if it is very cold.") == []  # „it is very cold” singur are doar 4 cuvinte


def test_indexul_dintr_un_fisier_citit_pe_bucati(tmp_path):
    fisier = tmp_path / "povesti.txt"
    fisier.write_text("One day the little cat\nsaw a big red ball.\n<|endoftext|>\nThe dog ran home.\n", encoding="utf-8")
    index = IndexFragmente(5)
    index.adauga_fisier(fisier, octeti_pe_bucata=12)  # bucăți foarte mici: fragmentele trec de la una la alta
    index.gata()
    assert index.cuvinte == 15 and index.gasite("The little cat saw a big dog.") == ["the little cat saw a", "little cat saw a big"]
    assert index.gasite("A big red ball the dog ran.") == []  # peste granița dintre povești nu se lipesc cuvintele


def test_forma_propozitiilor():
    assert probleme("A bird's body is covered with feathers.", "birds", []) == []
    assert probleme("Birds have soft feathers.", "birds", []) == [
        "it has 4 words (it must have 6 to 14)", 'it starts with the same words as the fact ("birds have")']
    assert probleme("Every feather on a bird helps keep it warm.", "birds", []) == [
        'it does not end with the word "feathers"']
    assert probleme("Each wing keeps one feather and many more feathers.", "birds", []) == [
        '"feathers" appears before the end']  # „feather” = „feathers”
    assert probleme("A bird's body is covered with feathers.", "birds", ["A bird's body is covered with feathers!"]) == [
        "it is the same as another sentence"]
    assert probleme("A bird has many soft and warm feathers.", "birds", []) == []  # alt început: „a bird”
    assert probleme("The Sun is a big hot star.", "the Sun", []) == [
        'it starts with the same words as the fact ("the sun")']  # aproape faptul „The Sun is a star.”
    assert probleme("Little baby animals get milk from cows. milk.", "cows", [])[0].startswith("write only one sentence")
    assert probleme("Birds wear tiny soft things called feathers.", "birds", ["Birds wear soft things called feathers."]) == [
        "it is too similar to another sentence for the same fact: say it in a different way"]
    assert probleme("A dog's nose can find a bone by its...smell.", "dogs", []) == [
        '"smell" must come after a space and a normal word']


def test_golul_si_liniile_profesorului():
    assert cu_gol("When it is cold, water turns into ice.", "ice") == "When it is cold, water turns into ___."
    assert linii_curate('1. First one.\n2) "Second."\n\n- Third') == ["First one.", "Second.", "Third"]


# Șabloanele propozițiilor de probă; {n} = numărul faptului, ca fiecare propoziție cu gol să fie a unui singur fapt.
PRIMELE = ("Tiny fox number one read a book {n} about", "A brave green frog sang song {n} about",
           "Old grey wolves tell tale {n} of")
INLOCUIRI = ("A happy little owl once read page {n} about", "A calm old turtle once heard story {n} about",
             "A small red hen once wrote poem {n} about")
RELE = ("Tiny fox number one read note {n} about",) * 3


class ProfesorDeProba:
    """Prima oară, câte 3 propoziții diferite pe fapt; prima are un fragment din „povești” (dacă indexul îl conține),
    deci se regenerează. La „e același fapt?” spune DA, în afară de propozițiile cu textul din `nu_e_acelasi`; golul îl
    completează corect, în afară de propozițiile cu textul din `gol_neclar`."""

    def __init__(self, mereu_rau: bool = False, nu_e_acelasi: str = "", gol_neclar: str = "") -> None:
        self.cereri: list[int] = []
        self.mereu_rau = mereu_rau
        self.nu_e_acelasi = nu_e_acelasi
        self.gol_neclar = gol_neclar
        self.raspunsuri_scrise: dict[str, str] = {}  # propoziția cu gol → răspunsul ei
        self.numere: dict[str, int] = {}  # faptul → numărul lui

    def _scrie(self, sabloane: tuple[str, ...], fapt: str, raspuns: str) -> str:
        n = self.numere.setdefault(fapt, len(self.numere))
        inceputuri = [s.format(n=n) for s in sabloane]
        for inceput in inceputuri:
            self.raspunsuri_scrise[f"{inceput} ___."] = raspuns
        return "\n".join(f"{inceput} {raspuns}." for inceput in inceputuri)

    def raspunde_mai_multe(self, conversatii, max_simboluri, cu_intamplare=True):
        self.cereri.append(len(conversatii))
        raspunsuri = []
        for conversatie in conversatii:
            cerere = conversatie[-1]["content"]
            if "Does the sentence clearly say the same fact" in cerere:
                propozitie = cerere.split('Sentence: "')[1].split('"')[0]
                raspunsuri.append("NO" if self.nu_e_acelasi and self.nu_e_acelasi in propozitie else "YES")
            elif "Fill in the blank" in cerere:
                propozitie = cerere.split('ONE word: "')[1].split('"')[0]
                gresit = self.gol_neclar and self.gol_neclar in propozitie
                raspunsuri.append("banana" if gresit else self.raspunsuri_scrise[propozitie])
            else:
                raspuns = cerere.split('Answer word: "')[1].split('"')[0]
                fapt = cerere.split('Fact: "')[1].split('"')[0]
                sabloane = PRIMELE if "Write 3 different quiz sentences" in cerere else RELE if self.mereu_rau else INLOCUIRI
                raspunsuri.append(self._scrie(sabloane, fapt, raspuns))
        return raspunsuri


def test_generarea_regenereaza_ce_apare_in_povesti():
    profesor = ProfesorDeProba()
    indexuri = {"povestile cu fapte": index_din("Tiny fox number one read a book."), "TinyStories": index_din("")}
    rezultat = genereaza(profesor, indexuri, runde=3)
    numere = rezultat["numere"]
    assert numere["propozitii"] == 150 and numere["regenerate"] == 50 and numere["runde"] == 1 and numere["esuate"] == 0
    assert numere["respingeri_povestile_cu_fapte"] == 50 and numere["respingeri_tinystories"] == 0
    assert numere["respingeri_sens"] == 0
    assert profesor.cereri == [50, 100, 100, 50, 50, 50]  # 50 de fapte; cele 2 verificări pe 100; 50 noi; din nou
    pasare = next(i for i in rezultat["intrebari"] if i["subiect"] == "birds")
    assert pasare == {"subiect": "birds", "fapt": "Birds have feathers.", "raspuns": "feathers", "acceptate": ["feathers"],
                      "propozitie": "A happy little owl once read page 1 about ___.", "incercari": 2,
                      "propozitie_intreaga": "A happy little owl once read page 1 about feathers."}
    istoric = rezultat["istoric"]["birds/1"]
    assert istoric[0]["respinsa_pentru"] == "povestile cu fapte" and "tiny fox number one read" in istoric[0]["motiv"]


def test_ce_nu_spune_acelasi_fapt_se_regenereaza():
    indexuri = {"povestile cu fapte": index_din(""), "TinyStories": index_din("")}
    rezultat = genereaza(ProfesorDeProba(nu_e_acelasi="green frog"), indexuri, runde=3)
    assert rezultat["numere"]["respingeri_sens"] == 50 and rezultat["numere"]["regenerate"] == 50
    istoric = rezultat["istoric"]["birds/2"]
    assert istoric[0]["respinsa_pentru"] == "sens" and "does not clearly say the same fact" in istoric[0]["motiv"]
    assert istoric[1]["motiv"] is None and istoric[1]["completarea_profesorului"] == "feathers"


def test_un_gol_neclar_se_regenereaza():
    indexuri = {"povestile cu fapte": index_din(""), "TinyStories": index_din("")}
    rezultat = genereaza(ProfesorDeProba(gol_neclar="grey wolves"), indexuri, runde=3)
    assert rezultat["numere"]["respingeri_gol_neclar"] == 50
    istoric = rezultat["istoric"]["birds/3"]
    assert istoric[0]["respinsa_pentru"] == "gol" and 'a reader would write "banana"' in istoric[0]["motiv"]


def test_cele_care_nu_reusesc_raman_pe_dinafara():
    indexuri = {"povestile cu fapte": index_din("Tiny fox number one read a book."), "TinyStories": index_din("")}
    rezultat = genereaza(ProfesorDeProba(mereu_rau=True), indexuri, runde=2)
    assert rezultat["numere"]["esuate"] == 50 and rezultat["numere"]["propozitii"] == 100 and rezultat["numere"]["runde"] == 2


def scrie_examen(cale, intrebari):
    cale.write_text(json.dumps({"versiune": 1, "intrebari": intrebari}), encoding="utf-8")
    return cale


EXAMEN_MIC = [
    {"subiect": "birds", "fapt": "Birds have feathers.", "propozitie": "A bird's body is covered with ___.",
     "raspuns": "feathers", "acceptate": ["feathers"]},
    {"subiect": "teeth", "fapt": "x", "propozitie": "Clean teeth stay ___.", "raspuns": "healthy",
     "acceptate": ["healthy", "clean"]},
]


class ElevDeProba:
    tokenizer = "bpe"

    def completeaza(self, text: str, max_simboluri: int) -> str:
        return " feathers." if text.endswith("covered with") else " clean"


def test_examenul_nou_pe_un_elev(tmp_path):
    rezultate = examene_elev.examineaza_fapte_noi(ElevDeProba(), scrie_examen(tmp_path / "examen.json", EXAMEN_MIC))
    assert [r["intrebare"] for r in rezultate] == ["A bird's body is covered with ___.", "Clean teeth stay ___."]
    assert examene_elev.scor_fapte_noi(rezultate) == {"fapte_noi": 1, "fapte_noi_cu_sinonime": 2, "fapte_noi_stiute": 2}


def test_examenul_nou_pe_un_model_salvat(tmp_path, monkeypatch, capsys):
    pytest.importorskip("torch")
    monkeypatch.chdir(tmp_path)
    cale = config_mic(tmp_path, "antrenare_lunga_3", model=', cale_stare = "lucru/antrenare_lunga_3/gpt.pt"', spatiu="lot = [4]")
    assert antrenare_lunga.main(["--config", str(cale), "--ore", "1", "--pauza", "0", "--racire", "0", "--lungime", "20"]) == 0
    model_id = [f for f in fise(tmp_path) if f.get("model_salvat")][-1]["id"]
    examen = scrie_examen(tmp_path / "examen.json", EXAMEN_MIC)
    assert unealta.main(["--experiment", str(model_id), "--examen", str(examen), "--dispozitiv", "cpu"]) == 0
    fisa = [f for f in fise(tmp_path) if f["linie"] == "examen_fapte_nou"][-1]
    assert fisa["module"]["elev"]["experiment"] == model_id and fisa["scoruri"]["intrebari"] == 2
    assert set(fisa["scoruri"]) == {"fapte_noi", "fapte_noi_cu_sinonime", "fapte_noi_stiute", "intrebari"}
    assert "fapte_noi (doar cu cuvântul din fapt):" in capsys.readouterr().out


def test_raspunsurile_vin_din_examenul_vechi():
    assert unealta.raspunsul_faptului("birds") == "feathers" and len(INTREBARI) == 50


def test_golul_profesorului_se_umple_cu_raspunsul():
    assert unealta.umple("A whale breathes through a hole called a ___ .", "blowhole") == (
        "A whale breathes through a hole called a blowhole.")
    assert unealta.umple("No blank here, just blood.", "blood") == "No blank here, just blood."


def test_completarea_pastreaza_ce_e_bun():
    profesor = ProfesorDeProba()
    indexuri = {"povestile cu fapte": index_din(""), "TinyStories": index_din("")}
    pastrate = {s: ["A brave green frog sang song 99 about x.", "Old grey wolves tell tale 98 of x."] for s in INTREBARI}
    pastrate["birds"] = ["A bird's body is covered with feathers.", "Every bird keeps warm with its many feathers.",
                         "Soft and light, a bird's coat is made of feathers."]
    rezultat = genereaza(profesor, indexuri, runde=2, pastrate=pastrate)
    numere = rezultat["numere"]
    assert numere["propozitii"] == 150 and numere["regenerate"] == 49 and numere["esuate"] == 0  # păsările erau complete
    pasari = [i["propozitie_intreaga"] for i in rezultat["intrebari"] if i["subiect"] == "birds"]
    assert pasari == pastrate["birds"]  # neatinse
    assert profesor.cereri[0] == 49  # doar cele care lipseau (câte una pentru fiecare fapt, nu 3)
