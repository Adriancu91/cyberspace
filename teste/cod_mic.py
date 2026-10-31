"""Un set mic de simboluri ca în lucru/kronos_cod/simboluri/ (uint16, sfârșit de fișier după fiecare fișier), pentru teste."""

from __future__ import annotations

from pathlib import Path

import numpy as np

ANTRENARE = [
    ["def aduna(a, b):\n    return a + b\n", "fn main() {\n    println!(\"salut\");\n}\n"] * 6,
    ["int patrat(int x) {\n    return x * x;\n}\n", "class Punct:\n    def __init__(self, x):\n        self.x = x\n"] * 6,
]
VALIDARE = [
    [("def scade(a, b):\n    return a - b\n", "python"), ("fn doi() -> u8 {\n    2\n}\n", "rust")],
    [("int zero(void) { return 0; }\n", "c")],
]


def scrie_simboluri(tmp_path: Path) -> dict:
    """Tokenizerul mic, două blocuri de antrenare și două de validare; dă setările pentru DateCod."""
    from module.tokenizer_bpe import antreneaza_bpe

    text = "".join(f for bloc in ANTRENARE for f in bloc) + "".join(f for bloc in VALIDARE for f, _ in bloc)
    tok = antreneaza_bpe(text, 320)
    tok.salveaza(tmp_path / "bpe_cod_mic.json")
    sfarsit = tok.speciale["<|endoftext|>"]
    d = tmp_path / "simboluri"
    d.mkdir()
    for k, bloc in enumerate(ANTRENARE):
        s = [x for f in bloc for x in tok.codifica_fara_speciale(f) + [sfarsit]]
        np.asarray(s, dtype=np.uint16).tofile(d / f"antrenare_{k:05d}.bin")
    for k, bloc in enumerate(VALIDARE):
        s = [x for f, _ in bloc for x in tok.codifica_fara_speciale(f) + [sfarsit]]
        np.asarray(s, dtype=np.uint16).tofile(d / f"validare_{k:05d}.bin")
    return {"director": str(d), "sfarsit_de_fisier": sfarsit, "cale_tokenizer": str(tmp_path / "bpe_cod_mic.json")}
