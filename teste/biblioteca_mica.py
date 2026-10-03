"""O bibliotecă de sensuri minusculă, pentru teste (fără să descarce WordNet)."""

from __future__ import annotations

import gzip
import json
from pathlib import Path

# noduri: p = părinte, pos = parte de vorbire, raft, n = nume, cod = locul în bibliotecă
NODURI = [
    {"p": -1, "pos": 1, "raft": 1, "n": "entity", "cod": [1, 1, 1]},
    {"p": 0, "pos": 1, "raft": 2, "n": "animal", "cod": [1, 2, 1, 1]},
    {"p": 1, "pos": 1, "raft": 2, "n": "horse", "cod": [1, 2, 1, 1, 1]},
    {"p": 1, "pos": 1, "raft": 2, "n": "cat", "cod": [1, 2, 1, 1, 2]},
    {"p": 0, "pos": 1, "raft": 3, "n": "artifact", "cod": [1, 3, 1, 2]},
    {"p": 4, "pos": 1, "raft": 3, "n": "sword", "cod": [1, 3, 1, 2, 1]},
    {"p": -1, "pos": 2, "raft": 4, "n": "run", "cod": [2, 4, 1]},
]
FORME = {"entity": [0], "animal": [1], "horse": [2], "cat": [3], "artifact": [4], "sword": [5], "run": [6]}
RELATII = {"2": [["are_membru", 3]], "5": [["parte_din", 4]]}


def scrie_biblioteca(director: Path) -> str:
    cale = Path(director) / "biblioteca_mica.json.gz"
    with gzip.open(cale, "wt", encoding="utf-8") as f:
        json.dump({
            "sursa": "test",
            "parti_de_vorbire": {"1": "substantiv", "2": "verb"},
            "rafturi": ["noun.Tops", "noun.animal", "noun.artifact", "verb.motion"],
            "noduri": NODURI,
            "forme": FORME,
            "relatii": RELATII,
        }, f)
    return str(cale)
