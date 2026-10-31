"""Tokenizerul pe cod (S55): regulile „cod” și unealta, pe texte mici făcute aici, FĂRĂ rețea și fără datele reale."""

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from module.tokenizer_bpe import (BUCATI_COD, TokenizerBPE, antreneaza_din_frecvente, frecvente_bucati,
                                  imbinari_spatii, tabel_spatii)
from unelte.kronos_cod import tokenizer_cod as tc

RADACINA = Path(__file__).resolve().parent.parent
PY = 'class A:\n    def __init__(self, x_1=10):\n        self.x_1 = x_1  # comentariu\n\n\tif x:\n\t\treturn "ș"\n'
RS = "fn main() {\r\n    let v: Vec<u32> = vec![1, 2, 3];\r\n    println!(\"{}\", v.len());\r\n}\r\n"
C = "#include <stdio.h>\nint main(void) {\n        printf(\"%d\\n\", 12345);   \n  return 0;\n}\n"


def _tok(texte, marime=600):
    fr = sum((frecvente_bucati(t, (), "cod") for t in texte), start=__import__("collections").Counter())
    return antreneaza_din_frecvente(fr, marime, tc.SPECIALE, "cod")


def test_bucatile_cod_acopera_tot_textul_si_pastreaza_indentarea():
    for text in (PY, RS, C, "  \t \n\n   x", "<|endoftext|>a  b"):
        assert "".join(BUCATI_COD.findall(text)) == text
    bucati = BUCATI_COD.findall(PY)
    assert "        " in bucati and " __init__" in bucati and "x_1" in bucati and "\n\n" in bucati and "\t\t" in bucati
    assert "\r\n" in BUCATI_COD.findall(RS) and "    " in BUCATI_COD.findall(RS)


def test_spatiile_si_taburile_sunt_simboluri_intregi():
    tok = _tok([PY, RS, C])
    assert tok.imbinari[:len(imbinari_spatii())] == imbinari_spatii()
    for n in (1, 2, 4, 8, 12, 16):
        (s,) = tok.codifica_fara_speciale("\n" + " " * n + "x")[1:2]
        assert tok.octeti(s) == b" " * n
    for n in (1, 2, 8):
        assert tok.octeti(tok.codifica_fara_speciale("\n" + "\t" * n + "x")[1]) == b"\t" * n
    lung = tok.codifica_fara_speciale(" " * 100)
    assert [len(tok.octeti(s)) for s in lung] == [16] * 6 + [4]
    assert tabel_spatii()[" " * 20] == [270, 258]


def test_codare_decodare_identica_si_simbolurile_speciale():
    tok = _tok([PY, RS, C], marime=340)
    assert tok.marime == 340 and list(tok.speciale) == list(tc.SPECIALE)
    eof = tok.speciale["<|endoftext|>"]
    assert eof == 336
    for text in (PY, RS, C, "ăîșțâ 🙂\x00\r", " " * 70 + "\t" * 20):
        s = tok.codifica_fara_speciale(text)
        assert b"".join(tok.octeti(x) for x in s) == text.encode("utf-8")
    # în cod, „<|endoftext|>” scris în fișier rămâne text; codifica îl recunoaște ca simbol
    assert eof not in tok.codifica_fara_speciale("a<|endoftext|>b")
    assert eof in tok.codifica("a<|endoftext|>b")
    tok2 = TokenizerBPE.din_dictionar(json.loads(json.dumps(tok.ca_dictionar())))
    assert tok2.codifica_fara_speciale(PY) == tok.codifica_fara_speciale(PY) and tok2.reguli == "cod"


def test_tokenizerul_w2_codeaza_la_fel_ca_inainte():
    vectori = RADACINA / "integrare" / "kronos" / "vectori" / "vectori.json"
    w2 = RADACINA / "date" / "ws" / "bpe_16384.json"
    if not (vectori.exists() and w2.exists()):
        pytest.skip("lipsesc vectorii sau tokenizerul w2")
    tok = TokenizerBPE.incarca(w2)
    v = json.loads(vectori.read_text(encoding="utf-8"))
    assert v["f32"]
    for x in v["f32"]:
        assert tok.codifica(x["text"]) == x["simboluri"]
        assert tok.codifica_fara_speciale(x["text"]) == x["simboluri"]


def _date(tmp_path, n=800):
    texte = [f"def f{k}(x):\n    return x + {k}\n" if k % 3 else
             f"fn g{k}() -> u32 {{\n    {k}\n}}\n" for k in range(n)]
    limbaje = ["python" if k % 3 else "rust" for k in range(n)]
    cod = tmp_path / "cod"
    cod.mkdir()
    with open(cod / "cod.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for k, (t, lim) in enumerate(zip(texte, limbaje)):
            f.write(json.dumps({"sursa": "test", "limbaj": lim, "cale": f"f{k}", "text": t}) + "\n")
    (cod / "aproape_duplicate.json").write_text("[1, 2]", encoding="utf-8")
    exclus = tmp_path / "exclus.txt"
    exclus.write_text("5\tabc\ttest\tf5\n7\tdef\ttest\tf7\n", encoding="utf-8")
    return texte, cod, exclus


def test_partea_dupa_suma_si_excluderile():
    t = "x = 1\n"
    h = hashlib.sha256(t.encode()).digest()
    asteptat = "validare" if h[0] < 3 else "esantion" if h[1] < 70 else "antrenare"
    assert tc.parte(9, t, {1}, {5}) == asteptat
    assert tc.parte(1, t, {1}, {5}) == "aproape_duplicat" and tc.parte(5, t, {1}, {5}) == "scurgere"


def test_unealta_cap_coada_fara_excluse_si_fara_validare_la_antrenare(tmp_path):
    texte, cod, exclus = _date(tmp_path)
    tok_dir, simb_dir = tmp_path / "tok", tmp_path / "simb"
    rez = tc.antreneaza(cod, exclus, tok_dir, procese=2, marime=500, jurnal=lambda m: None)
    imp = rez["impartire"]
    assert imp["aproape_duplicat"]["fisiere"] == 2 and imp["scurgere"]["fisiere"] == 2
    assert sum(imp[k]["fisiere"] for k in ("validare", "antrenare", "esantion") if k in imp) == len(texte) - 4
    assert imp["validare"]["fisiere"] > 0
    with pytest.raises(SystemExit):
        tc.antreneaza(cod, exclus, tok_dir, procese=2, marime=500, jurnal=lambda m: None)

    m = tc.masoara(cod, exclus, tok_dir, RADACINA / "date" / "ws" / "bpe_16384.json", procese=2, marime=500,
                   jurnal=lambda m: None) if (RADACINA / "date" / "ws" / "bpe_16384.json").exists() else None
    if m:
        assert m["identice_procent"] == 100.0 and m["verdict"] in ("BUN", "SLAB")
        assert m["fisiere_validare"] == imp["validare"]["fisiere"] and "python" in m["pe"]

    r = tc.tokenizeaza(cod, exclus, tok_dir, simb_dir, procese=2, marime=500, jurnal=lambda m: None)
    assert r["terminat"] and r["pe"]["validare"]["fisiere"] == imp["validare"]["fisiere"]
    assert r["pe"]["antrenare"]["fisiere"] == len(texte) - 4 - imp["validare"]["fisiere"]
    tok = TokenizerBPE.incarca(tok_dir / "bpe_cod_500.json")
    eof = tok.speciale["<|endoftext|>"]
    s = np.fromfile(simb_dir / "antrenare_00000.bin", dtype=np.uint16).tolist()
    fisiere, cur = [], []
    for x in s:
        if x == eof:
            fisiere.append(tok.decodeaza(cur))
            cur = []
        else:
            cur.append(x)
    aproape, scurgere = {1, 2}, {5, 7}
    antr = [t for k, t in enumerate(texte) if tc.parte(k, t, aproape, scurgere) in ("antrenare", "esantion")]
    assert fisiere == antr and texte[1] not in fisiere and texte[5] not in fisiere
    # reluarea: blocurile făcute nu se refac
    r2 = tc.tokenizeaza(cod, exclus, tok_dir, simb_dir, procese=2, marime=500, jurnal=lambda m: None)
    assert r2["terminat"] and r2["pe"] == r["pe"]
