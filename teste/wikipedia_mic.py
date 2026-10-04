"""O Wikipedia minusculă, scrisă local ca fișier parquet (ca cel oficial), pentru teste fără internet."""

from __future__ import annotations

from pathlib import Path


def articol(i: int) -> str:
    return f"Town number {i} is a small town in a green valley. It has {i} people and an old bridge over the river."


def scrie_wikipedia(director: Path, articole: int = 1000) -> dict:
    """Scrie fișierul „oficial” și întoarce setările pentru DateWikipedia."""
    import pyarrow as pa
    import pyarrow.parquet as pq

    director = Path(director)
    cale = director / "wiki_mic.parquet"
    tabel = pa.table({
        "id": [str(i) for i in range(articole)],
        "url": [f"https://simple.wikipedia.org/wiki?curid={i}" for i in range(articole)],
        "title": [f"Town {i}" for i in range(articole)],
        "text": [articol(i) for i in range(articole)],
    })
    pq.write_table(tabel, cale)
    return {"director": str(director / "wikipedia"), "url": cale.as_uri(), "megaocteti_validare": 0.001}
