"""Datele workstation-ului: curățarea surselor, validarea pusă deoparte, amestecul și modulul date_amestec."""

import json
import zipfile

import pytest

from module.date_amestec import DateAmestec
from unelte import curata_date_ws as curata
from unelte import descarca_date_ws as descarca
from unelte.pregateste_amestec_ws import bucati_intre_texte, inceputul, scrie_hrana, simboluri_in_paralel

pq = pytest.importorskip("pyarrow.parquet")
pa = pytest.importorskip("pyarrow")
SEP = "<|endoftext|>"


def test_sedilele_devin_virgule_si_textul_e_curatat():
    text, sedile = curata.normalizeaza("Ştefan şi Ţuţu\r\nau  plecat.\x00\n\n\n\nGata <|endoftext|> aici.  \n")
    assert text == "Ștefan și Țuțu\nau  plecat.\n\nGata  aici." and sedile == 4
    assert curata.normalizeaza("a\u0306")[0] == "ă"  # litera din două semne devine una (NFC)


def test_textele_stricate_se_recunosc():
    bun = "Pisica doarme pe covor, iar câinele aleargă prin grădină după o minge roșie. " * 5
    assert not curata.e_stricat(bun, "proza")
    assert curata.e_stricat(bun + "\ufffd", "proza")
    assert curata.e_stricat("AceastÄƒ paginÄƒ este Ã®n limba romÃ¢nÄƒ È™i e stricatÄƒ. " * 5, "proza")
    assert curata.e_stricat("1234 | 5678 | 9012 || 3456 ### 7890 *** 1111 --- " * 10, "proza")  # prea puține litere
    assert not curata.e_stricat("x = [1, 2, 3]\nfor i in x:\n    print(i * 2)\n" * 5, "cod")


def _surse(tmp_path, monkeypatch, texte, nume="wikipedia_ro"):
    brut, curat = tmp_path / "brut", tmp_path / "curat"
    (brut / nume).mkdir(parents=True)
    pq.write_table(pa.table({"text": texte}), brut / nume / "a.parquet")
    monkeypatch.setattr(curata, "BRUT", brut)
    monkeypatch.setattr(curata, "CURAT", curat)
    return curat / nume


def test_curatarea_scoate_scurte_stricate_si_duplicate_si_pune_deoparte_validarea(tmp_path, monkeypatch):
    bune = [f"Articolul numărul {k} vorbește despre orașul cu numărul {k}, care are multe case şi străzi. " * 6
            for k in range(600)]
    texte = bune + ["prea scurt", bune[0].upper() + "  ", bune[1] + "\ufffd"]
    tinta = _surse(tmp_path, monkeypatch, texte)
    info = curata.curata("wikipedia_ro")
    assert info["citite"] == 603 and info["prea_scurte"] == 1 and info["duplicate"] == 1 and info["stricate"] == 1
    assert info["texte_antrenare"] + info["texte_validare"] == 600 and info["sedile_inlocuite"] == 600 * 6
    antrenare = (tinta / "antrenare.txt").read_text(encoding="utf-8").split(f"\n{SEP}\n")
    validare = (tinta / "validare.txt").read_text(encoding="utf-8").split(f"\n{SEP}\n")
    assert antrenare[-1] == "" and len(antrenare) - 1 == info["texte_antrenare"]
    assert 0 < info["texte_validare"] < 30                       # în jur de 1%
    assert not set(antrenare[:-1]) & set(validare[:-1])          # validarea nu apare în antrenare
    assert "ş" not in "".join(antrenare) and b"\r" not in (tinta / "antrenare.txt").read_bytes()
    assert info["octeti_antrenare"] == (tinta / "antrenare.txt").stat().st_size
    primul = (tinta / "validare.txt").read_bytes()
    curata.curata("wikipedia_ro")
    assert (tinta / "validare.txt").read_bytes() == primul       # aceleași texte în validare, la fiecare rulare


def test_limita_opreste_felia(tmp_path, monkeypatch):
    texte = [f"Textul {k} are destule litere ca să fie socotit proză bună de păstrat aici. " * 20 for k in range(300)]
    _surse(tmp_path, monkeypatch, texte, "fineweb2_ro")
    monkeypatch.setitem(curata.SURSE["fineweb2_ro"], "limita_gb", 0.0001)  # 100.000 de octeți
    info = curata.curata("fineweb2_ro")
    assert 100_000 <= info["octeti_antrenare"] + info["octeti_validare"] < 110_000 and info["citite"] < 300


def test_perechile_engleza_romana(tmp_path, monkeypatch):
    brut = tmp_path / "brut"
    (brut / "tatoeba_en_ro").mkdir(parents=True)
    with zipfile.ZipFile(brut / "tatoeba_en_ro" / "en-ro.txt.zip", "w") as z:
        z.writestr("Tatoeba.en-ro.en", "I see a cat.\nHello.\nThis one is aligned badly.\nI see a cat.\n")
        z.writestr("Tatoeba.en-ro.ro", "Văd o pisică.\nSalut.\nNu.\nVăd o pisică.\n")
    monkeypatch.setattr(curata, "BRUT", brut)
    monkeypatch.setattr(curata, "CURAT", tmp_path / "curat")
    info = curata.curata("tatoeba_en_ro")
    assert info["citite"] == 3 and info["duplicate"] == 1  # perechea aliniată greșit nici nu se citește
    tot = "".join((tmp_path / "curat" / "tatoeba_en_ro" / f).read_text(encoding="utf-8") for f in ("antrenare.txt", "validare.txt"))
    assert "EN: I see a cat.\nRO: Văd o pisică." in tot and "aligned badly" not in tot


def test_raportul_surselor(tmp_path, monkeypatch):
    tinta = _surse(tmp_path, monkeypatch, ["Un articol destul de lung ca să rămână după curățare, cu multe cuvinte. " * 8] * 3)
    curata.curata("wikipedia_ro")
    (tmp_path / "brut" / "surse.json").write_text(json.dumps({
        "wikipedia_ro": {"sursa": "wikipedia_ro", "stare": "descarcat", "descriere": "Wikipedia", "licenta": ["cc-by-sa-3.0", "gfdl"],
                         "obligatii": "atribuire", "de_unde": "https://exemplu", "revizie": "abcdef0123456", "octeti": 5_000_000,
                         "descarcat": "2026-10-12T12:00:00", "fisiere": [{"fisier": "a", "octeti": 1, "sha256": "ab" * 32}]},
        "cod_stack_smol": {"sursa": "cod_stack_smol", "stare": "nedescarcat", "motiv": "sursa cere cont", "descriere": "The Stack"},
    }), encoding="utf-8")
    curata.raport(tmp_path / "DATE_surse.md")
    text = (tmp_path / "DATE_surse.md").read_text(encoding="utf-8")
    assert "cc-by-sa-3.0 + gfdl" in text and "sursa cere cont" in text and "| wikipedia_ro | 3 |" in text
    assert tinta.exists()


def test_sursa_cu_alta_licenta_sau_cu_cont_nu_se_descarca(monkeypatch):
    class Card:
        def __init__(self, licenta):
            self.licenta = licenta

        def to_dict(self):
            return {"license": self.licenta}

    class Info:
        def __init__(self, licenta, gated):
            self.card_data, self.gated, self.sha, self.siblings = Card(licenta), gated, "abc", []

    import huggingface_hub

    raspuns = {}
    monkeypatch.setattr(huggingface_hub.HfApi, "dataset_info", lambda self, nume, files_metadata=True: raspuns["info"])
    sursa = {"hf": "x/y", "licenta": "apache-2.0"}
    raspuns["info"] = Info("apache-2.0", False)
    assert descarca.verifica_hf(sursa)[0] is None
    raspuns["info"] = Info("cc-by-nc-4.0", False)
    assert "nu e cea așteptată" in descarca.verifica_hf(sursa)[0]
    raspuns["info"] = Info("apache-2.0", "auto")
    assert "cere cont" in descarca.verifica_hf(sursa)[0]
    raspuns["info"] = Info(None, False)
    assert descarca.verifica_hf({"hf": "x/y", "licenta": None})[0] is not None  # fără licență pe fișă: nu


def test_date_amestec(tmp_path):
    (tmp_path / "a.txt").write_text("un text de antrenare. " * 100, encoding="utf-8")
    (tmp_path / "v.txt").write_text("un text de validare. " * 10, encoding="utf-8")
    date = DateAmestec(str(tmp_path / "a.txt"), str(tmp_path / "v.txt"))
    assert date.text_antrenare().startswith("un text de antrenare") and date.text_validare().startswith("un text de validare")
    with pytest.raises(ValueError, match="pregateste_amestec_ws"):
        DateAmestec(str(tmp_path / "lipsa.txt"), str(tmp_path / "v.txt"))


def test_inceputul_se_taie_intre_texte(tmp_path):
    fisier = tmp_path / "s.txt"
    fisier.write_bytes(b"".join(f"textul {k}\n{SEP}\n".encode() for k in range(100)))
    bucata = inceputul(fisier, 500)
    assert 0 < len(bucata) <= 500 and bucata.endswith(f"{SEP}\n".encode()) and bucata.startswith(b"textul 0\n")
    assert inceputul(fisier, 10**9) == fisier.read_bytes()


def test_hrana_are_abecedarul_o_parte_la_cinci_parti_de_fapte(tmp_path):
    (tmp_path / "fapte.txt").write_bytes(b"o poveste cu fapte\n" * 5000)
    (tmp_path / "abecedar.txt").write_bytes(b"TASK: x = 1\nWRITE:\nx = 1\n" * 10)
    info = scrie_hrana(tmp_path / "hrana.txt", tmp_path / "fapte.txt", tmp_path / "abecedar.txt")
    assert 0.15 < info["parte_abecedar"] < 0.18  # 1/6
    assert (tmp_path / "hrana.txt").read_bytes().startswith(b"o poveste cu fapte\n")


def test_simbolurile_in_paralel_sunt_cele_de_la_codificarea_intreaga(tmp_path):
    from module.tokenizer_bpe import antreneaza_din_frecvente, frecvente_bucati

    text = "".join(f"Povestea {k}: pisica a văzut {k * 37} de stele.\n{SEP}\n" for k in range(400))
    tok = antreneaza_din_frecvente(frecvente_bucati(text, reguli="ws"), 256 + 1100 + 80 + 1, reguli="ws")
    tok.salveaza(tmp_path / "ws.json")
    bucati = bucati_intre_texte(text, 2000)
    assert len(bucati) > 5 and "".join(bucati) == text and all(b.endswith(SEP) for b in bucati[:-1])
    assert simboluri_in_paralel(text, str(tmp_path / "ws.json"), 2).tolist() == tok.codifica(text)
