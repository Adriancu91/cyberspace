"""Un set mic de bucăți ca în lucru/bucati/ (scris cu unelte/date_bucati.py dintr-un tensor mic), pentru teste."""

from __future__ import annotations

from pathlib import Path

TEXT = ("the cat sat on the mat. the dog ran to the tree. a bird sang in the old garden.\n"
        "pisica doarme pe covor, iar câinele aleargă spre copac.\n") * 40
VALIDARE = "the dog ran to the tree and the cat looked at the bird.\n" * 20


def scrie_bucati(tmp_path: Path, marime: int = 64) -> dict:
    """Tokenizerul mic, simbolurile textului tăiate în bucăți de `marime` și validarea; dă setările pentru DateBucati."""
    import torch

    from module.tokenizer_bpe import antreneaza_bpe
    from unelte import date_bucati as db

    tok = antreneaza_bpe(TEXT, 320)
    cale_tok = tmp_path / "bpe_bucati_mic.json"
    tok.salveaza(cale_tok)
    sursa = tmp_path / "simboluri_mici.pt"
    torch.save(torch.tensor(tok.codifica(TEXT), dtype=torch.int16), sursa)
    dosar = tmp_path / "bucati"
    db.scrie(sursa, dosar, marime, cale_tok, 0.0)
    validare = tmp_path / "validare_bucati.txt"
    validare.write_text(VALIDARE, encoding="utf-8")
    return {"director": str(dosar), "cale_validare": str(validare), "cale_tokenizer": str(cale_tok)}
