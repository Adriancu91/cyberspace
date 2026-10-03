"""Un TinyStories minuscul, scris local, pentru teste (fără internet).

Antrenarea începe cu o poveste care trebuie aruncată; validarea începe cu o poveste tăiată
(ca fișierul oficial) și conține o poveste identică cu una din antrenare.
"""

from __future__ import annotations

from pathlib import Path

SEP = "\n<|endoftext|>\n"


def poveste_antrenare(i: int) -> str:
    return f"Once upon a time, a little cat number {i} found a red ball. The cat was very happy and played all day."


def poveste_validare(i: int) -> str:
    return f"One day, a small dog number {i} saw a big tree. The dog ran to the tree and sat in the shade."


def scrie_surse(director: Path) -> dict:
    """Scrie cele două fișiere „oficiale” și întoarce setările pentru DateTinyStories."""
    director = Path(director)
    antrenare = SEP.join(["Poveste de început"] + [poveste_antrenare(i) for i in range(40)])
    validare = "o poveste tăiată la început." + SEP + SEP.join(
        [poveste_antrenare(5)] + [poveste_validare(i) for i in range(20)]
    )
    (director / "train.txt").write_text(antrenare, encoding="utf-8")
    (director / "valid.txt").write_text(validare, encoding="utf-8")
    return {
        "director": str(director / "tinystories"),
        "megaocteti": 0.004,  # 3.000 de octeți din antrenare, 1.000 din validare
        "procent_validare": 0.25,
        "url_antrenare": (director / "train.txt").as_uri(),
        "url_validare": (director / "valid.txt").as_uri(),
    }
