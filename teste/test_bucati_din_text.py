"""S102 (C-85 pasul 5, partea c): unelte/bucati_din_text.py — bucățile de simboluri făcute direct din text, pe rând,
trebuie să dea exact șirul de la `codifica(textul întreg)` și exact formatul lui unelte/date_bucati.py."""

import hashlib
import json

import numpy as np
import pytest

from module.tokenizer_bpe import TokenizerBPE, antreneaza_bpe
from unelte import bucati_din_text as bt
from unelte import date_bucati as db

SF = "<|endoftext|>"
POVESTI = [
    "A fost odată o fată care mânca mere și pere în grădină.",
    "Țânțarul și știuca s-au întâlnit într-o seară; „Încotro?” a întrebat știuca.",
    "Ion are 12 oi, 345 de găini și 6789 de albine. Șapte îngeri râd.",
    "Un rând\nal doilea rând\n\nal treilea, cu ăîâșț ĂÎÂȘȚ și cu — linii.",
    "Scurt.",
]


def _text(repetari=6):
    return SF.join(POVESTI[i % len(POVESTI)] + f" ({i})" for i in range(repetari * len(POVESTI))) + SF


@pytest.fixture(scope="module")
def tok_cale(tmp_path_factory):
    cale = tmp_path_factory.mktemp("tok") / "bpe.json"
    antreneaza_bpe(_text(), marime=300).salveaza(cale)
    return cale


def _scrie_text(tmp_path, text, nume="text.txt"):
    cale = tmp_path / nume
    cale.write_bytes(text.encode("utf-8"))
    return cale


def _sir(dosar):
    return np.concatenate([np.asarray(a) for a in db.CititorBucati(dosar)])


def _asteptat(tok_cale, text):
    tok = TokenizerBPE.incarca(tok_cale)
    return np.array(tok.codifica(text), dtype="<i2")


@pytest.mark.parametrize("bloc", [1, 7, 16, 50, 333, 10_000_000], ids=lambda b: f"bloc{b}")
def test_acelasi_sir_ca_textul_intreg(tmp_path, tok_cale, bloc):
    text = _text()
    sursa = _scrie_text(tmp_path, text)
    rez = bt.scrie(sursa, tok_cale, tmp_path / "b", marime=97, bloc_octeti=bloc)
    asteptat = _asteptat(tok_cale, text)
    assert rez["terminat"] and rez["simboluri_total"] == len(asteptat)
    assert np.array_equal(_sir(tmp_path / "b"), asteptat)
    assert rez["sha256_tot"] == hashlib.sha256(asteptat.tobytes()).hexdigest()
    assert rez["sursa"]["litere"] == len(text)
    assert not list((tmp_path / "b").glob("rest_*.bin")) and not list((tmp_path / "b").glob("*.part"))


def test_acelasi_format_ca_date_bucati(tmp_path, tok_cale):
    """Indexul și bucățile sunt exact cele pe care le-ar scrie `date_bucati.py scrie` din cache-ul aceluiași șir."""
    torch = pytest.importorskip("torch")
    from module.date_bucati import DateBucati

    text = _text()
    sursa = _scrie_text(tmp_path, text)
    bt.scrie(sursa, tok_cale, tmp_path / "nou", marime=64, bloc_octeti=40)
    cache = tmp_path / "simboluri.pt"
    torch.save(torch.tensor(TokenizerBPE.incarca(tok_cale).codifica(text), dtype=torch.int16), cache)
    db.scrie(cache, tmp_path / "vechi", 64, tok_cale, 0.0)
    nou, vechi = db.citeste_index(tmp_path / "nou"), db.citeste_index(tmp_path / "vechi")
    for cheie in ("versiune", "tip", "ordine_octeti", "marime_bucata", "simboluri_total", "simboluri_sursa", "partial",
                  "sha256_tot", "bucati"):
        assert nou[cheie] == vechi[cheie], cheie
    assert set(vechi) <= set(nou)
    assert nou["tokenizer"]["sha256"] == vechi["tokenizer"]["sha256"]
    for b in nou["bucati"]:
        assert (tmp_path / "nou" / b["fisier"]).read_bytes() == (tmp_path / "vechi" / b["fisier"]).read_bytes()
    assert db.verifica(tmp_path / "nou")["ok"]
    proba = bt.identitate(tmp_path / "nou", tmp_path / "vechi")
    assert proba["verdict"] == "DA" and proba["identic"]
    date = DateBucati(director=str(tmp_path / "nou"), cale_validare=str(sursa), cale_tokenizer=str(tok_cale))
    assert len(date.sir_antrenare()) == nou["simboluri_total"]


def test_bloc_fara_simbol_special_se_lipeste(tmp_path, tok_cale):
    lunga = "o poveste foarte lungă, fără niciun sfârșit de poveste, " * 20
    text = "Scurt." + SF + lunga + SF + "Coada fără sfârșit"
    sursa = _scrie_text(tmp_path, text)
    rez = bt.scrie(sursa, tok_cale, tmp_path / "b", marime=1000, bloc_octeti=64)
    assert np.array_equal(_sir(tmp_path / "b"), _asteptat(tok_cale, text))
    assert rez["facut_de"]["citiri_fara_special_lipite"] > 5
    randuri = [json.loads(r) for r in (tmp_path / "b" / "jurnal.jsonl").read_text(encoding="utf-8").splitlines()]
    assert any(r["citiri_fara_special_lipite"] > 5 for r in randuri)
    assert randuri[-1]["octeti_pana_la"] == sursa.stat().st_size


def test_caractere_romanesti_taiate_la_granita_blocului(tmp_path, tok_cale):
    """Cu blocuri de 1–5 octeți, literele de 2 și 3 octeți (ș, ț, „, —) cad mereu peste granița blocului."""
    text = "șțăîâ„—”" * 3 + SF + "ȘȚĂÎÂ" + SF + "€ș"
    sursa = _scrie_text(tmp_path, text)
    for bloc in (1, 2, 3, 5):
        bt.scrie(sursa, tok_cale, tmp_path / f"b{bloc}", marime=11, bloc_octeti=bloc)
        assert np.array_equal(_sir(tmp_path / f"b{bloc}"), _asteptat(tok_cale, text)), bloc


def test_sfarsituri_de_rand_ca_la_read_text(tmp_path, tok_cale):
    """Textul se citește ca Path.read_text: „\\r\\n” și „\\r” devin „\\n”, și când „\\r” și „\\n” cad în blocuri diferite."""
    brut = "un rând\r\nal doilea\ral treilea\n" + SF + "\r\n\r\nalt text\r" + SF + "coada\r\n"
    sursa = _scrie_text(tmp_path, brut)
    citit = sursa.read_text(encoding="utf-8")
    assert "\r" not in citit
    for bloc in (1, 4, 9, 1000):
        rez = bt.scrie(sursa, tok_cale, tmp_path / f"b{bloc}", marime=1000, bloc_octeti=bloc)
        assert np.array_equal(_sir(tmp_path / f"b{bloc}"), _asteptat(tok_cale, citit)), bloc
        assert rez["sursa"]["litere"] == len(citit)


@pytest.mark.parametrize("opriri", [1, 2, 3], ids=lambda n: f"cate{n}")
def test_reluarea_dupa_oprire_da_acelasi_rezultat(tmp_path, tok_cale, opriri):
    text = _text()
    sursa = _scrie_text(tmp_path, text)
    intreg = bt.scrie(sursa, tok_cale, tmp_path / "intreg", marime=53, bloc_octeti=120)
    porniri = 0
    while True:
        rez = bt.scrie(sursa, tok_cale, tmp_path / "reluat", marime=53, bloc_octeti=120, opreste_dupa_blocuri=opriri)
        porniri += 1
        if rez["terminat"]:
            break
        assert rez["oprit"] and not rez["pe_disc"]
        assert not (tmp_path / "reluat" / "index.json").exists()
        progres = json.loads((tmp_path / "reluat" / "progres.json").read_text(encoding="utf-8"))
        assert 0 < progres["octeti_facuti"] < sursa.stat().st_size and not progres["terminat"]
    assert porniri > 2 and rez["facut_de"]["porniri"] == porniri
    nou, vechi = db.citeste_index(tmp_path / "reluat"), db.citeste_index(tmp_path / "intreg")
    assert nou["sha256_tot"] == vechi["sha256_tot"] == intreg["sha256_tot"]
    assert nou["bucati"] == vechi["bucati"]
    assert np.array_equal(_sir(tmp_path / "reluat"), _asteptat(tok_cale, text))
    assert db.verifica(tmp_path / "reluat")["ok"]


def test_reluarea_reface_blocul_neterminat(tmp_path, tok_cale):
    """O oprire la jumătatea unui bloc (bucăți sau rest scrise, progresul nu): la repornire blocul se reface."""
    text = _text()
    sursa = _scrie_text(tmp_path, text)
    dosar = tmp_path / "b"
    bt.scrie(sursa, tok_cale, dosar, marime=53, bloc_octeti=120, opreste_dupa_blocuri=2)
    progres = json.loads((dosar / "progres.json").read_text(encoding="utf-8"))
    (dosar / f"bucata_{len(progres['bucati']):05d}.bin").write_bytes(b"\x01\x02" * 53)  # bucată scrisă, neînregistrată
    (dosar / "rest_999999.bin").write_bytes(b"\x07\x07")  # rest mai nou decât progresul
    (dosar / "bucata_99999.bin.part").write_bytes(b"x")
    rez = bt.scrie(sursa, tok_cale, dosar, marime=53, bloc_octeti=120)
    assert rez["terminat"]
    assert np.array_equal(_sir(dosar), _asteptat(tok_cale, text))
    assert db.verifica(dosar)["ok"] and not list(dosar.glob("rest_*.bin"))


def test_reluarea_refuza_alta_sursa_sau_rest_stricat(tmp_path, tok_cale):
    sursa = _scrie_text(tmp_path, _text())
    dosar = tmp_path / "b"
    bt.scrie(sursa, tok_cale, dosar, marime=53, bloc_octeti=120, opreste_dupa_blocuri=1)
    alta = _scrie_text(tmp_path, _text(7), "alta.txt")
    with pytest.raises(ValueError, match="altei rulări"):
        bt.scrie(alta, tok_cale, dosar, marime=53, bloc_octeti=120)
    with pytest.raises(ValueError, match="altei rulări"):
        bt.scrie(sursa, tok_cale, dosar, marime=54, bloc_octeti=120)
    progres = json.loads((dosar / "progres.json").read_text(encoding="utf-8"))
    assert progres["rest"]
    (dosar / progres["rest"]["fisier"]).write_bytes(b"\x00\x00")
    with pytest.raises(ValueError, match="SHA diferit"):
        bt.scrie(sursa, tok_cale, dosar, marime=53, bloc_octeti=120)


def test_refuza_index_existent(tmp_path, tok_cale):
    sursa = _scrie_text(tmp_path, _text())
    bt.scrie(sursa, tok_cale, tmp_path / "b", marime=53, bloc_octeti=120)
    inainte = (tmp_path / "b" / "index.json").read_bytes()
    with pytest.raises(FileExistsError):
        bt.scrie(sursa, tok_cale, tmp_path / "b", marime=53, bloc_octeti=120)
    assert (tmp_path / "b" / "index.json").read_bytes() == inainte


def test_se_opreste_cand_nu_e_loc_pe_disc(tmp_path, tok_cale):
    sursa = _scrie_text(tmp_path, _text())
    rez = bt.scrie(sursa, tok_cale, tmp_path / "b", marime=53, bloc_octeti=120, minim_liber_gb=10**9)
    assert not rez["terminat"] and rez["pe_disc"] and rez["octeti_facuti"] == 0
    assert not list((tmp_path / "b").glob("bucata_*")) and not (tmp_path / "b" / "index.json").exists()
    assert bt.scrie(sursa, tok_cale, tmp_path / "b", marime=53, bloc_octeti=120, minim_liber_gb=0)["terminat"]


def test_text_gol_si_text_fara_simbol_special(tmp_path, tok_cale):
    gol = _scrie_text(tmp_path, "", "gol.txt")
    rez = bt.scrie(gol, tok_cale, tmp_path / "gol", marime=10, bloc_octeti=5)
    assert rez["terminat"] and rez["simboluri_total"] == 0 and rez["numar_bucati"] == 0
    text = "doar o poveste, fără niciun simbol special, dar cu șțăîâ"
    sursa = _scrie_text(tmp_path, text)
    bt.scrie(sursa, tok_cale, tmp_path / "b", marime=10, bloc_octeti=5)
    assert np.array_equal(_sir(tmp_path / "b"), _asteptat(tok_cale, text))


def test_utf8_stricat_e_refuzat(tmp_path, tok_cale):
    sursa = tmp_path / "stricat.txt"
    sursa.write_bytes("bun".encode() + SF.encode() + b"\xff\xfe rau" + SF.encode())
    with pytest.raises(UnicodeDecodeError):
        bt.scrie(sursa, tok_cale, tmp_path / "b", marime=10, bloc_octeti=1000)


def test_taietura_si_simboluri_speciale_nesigure():
    sf = SF.encode()
    assert bt.taietura(b"abc" + sf + b"de" + sf + b"f<|endof", [sf]) == len(b"abc" + sf + b"de" + sf)
    assert bt.taietura(b"fara nimic <|endoftext", [sf]) == 0
    imbinari = antreneaza_bpe("a b c a b c", marime=258).imbinari
    assert bt.speciale_octeti(TokenizerBPE(imbinari, [SF, "<|alt|>"])) == [sf, b"<|alt|>"]
    with pytest.raises(ValueError, match="niciun simbol special"):
        bt.speciale_octeti(TokenizerBPE(imbinari, []))
    with pytest.raises(ValueError, match="suprapune"):
        bt.speciale_octeti(TokenizerBPE(imbinari, ["<a>", ">b<"]))
    with pytest.raises(ValueError, match="suprapune"):
        bt.speciale_octeti(TokenizerBPE(imbinari, ["|x|"]))
    with pytest.raises(ValueError, match="cuprins"):
        bt.speciale_octeti(TokenizerBPE(imbinari, ["<a>", "x<a>y"]))


def test_identitate_gaseste_prima_diferenta(tmp_path, tok_cale):
    text = _text()
    sursa = _scrie_text(tmp_path, text)
    bt.scrie(sursa, tok_cale, tmp_path / "a", marime=53, bloc_octeti=120)
    bt.scrie(sursa, tok_cale, tmp_path / "b", marime=53, bloc_octeti=120)
    cale = tmp_path / "b" / "bucata_00002.bin"
    a = np.fromfile(cale, dtype="<i2")
    a[10] += 1
    cale.write_bytes(a.tobytes())
    index = db.citeste_index(tmp_path / "b")
    index["bucati"][2]["sha256"] = hashlib.sha256(a.tobytes()).hexdigest()
    (tmp_path / "b" / "index.json").write_text(json.dumps(index), encoding="utf-8")
    proba = bt.identitate(tmp_path / "b", tmp_path / "a")
    assert proba["verdict"] == "NU" and proba["bucati_diferite"] == [2]
    assert proba["prima_diferenta"]["pozitie_simbol"] == 2 * 53 + 10
    assert proba["prima_diferenta"]["octeti_de_la"] < proba["prima_diferenta"]["octeti_pana_la"]


def test_comenzile_cap_coada(tmp_path, tok_cale, capsys):
    text = _text()
    sursa = _scrie_text(tmp_path, text)
    assert bt.main(["masoara", "--sursa", str(sursa), "--tokenizer", str(tok_cale), "--octeti", "300",
                    "--bloc-octeti", "100", "--iesire", str(tmp_path / "m.json")]) == 0
    m = json.loads((tmp_path / "m.json").read_text(encoding="utf-8"))
    assert 300 <= m["octeti_masurati"] < sursa.stat().st_size and m["simboluri"] > 0 and m["estimare_tot_secunde"] >= 0
    with pytest.raises(FileExistsError):
        bt.main(["masoara", "--sursa", str(sursa), "--tokenizer", str(tok_cale), "--iesire", str(tmp_path / "m.json")])
    comanda = ["scrie", "--sursa", str(sursa), "--tokenizer", str(tok_cale), "--iesire", str(tmp_path / "b"),
               "--marime", "53", "--bloc-octeti", "120", "--minim-liber-gb", "0"]
    assert bt.main(comanda + ["--opreste-dupa-blocuri", "2"]) == 3
    assert bt.main(comanda + ["--limita-ore", "0"]) == 3
    assert bt.main(comanda) == 0
    assert db.main(["verifica", "--dosar", str(tmp_path / "b")]) == 0
    assert bt.main(["identitate", "--dosar", str(tmp_path / "b"), "--referinta", str(tmp_path / "b"),
                    "--iesire", str(tmp_path / "i.json")]) == 0
    assert json.loads((tmp_path / "i.json").read_text(encoding="utf-8"))["verdict"] == "DA"
    assert np.array_equal(_sir(tmp_path / "b"), _asteptat(tok_cale, text))
    capsys.readouterr()
