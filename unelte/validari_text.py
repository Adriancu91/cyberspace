"""Bucata de text pe care se măsoară o validare (mutată aici din `unelte/examen_validari_ws.py`, S90, 7 nov 2026,
neschimbată), ca s-o poată folosi și `module/examen_romana.py` fără să importe jurnalul Kronos.
"""

from __future__ import annotations

from pathlib import Path

SEPARATOR = "<|endoftext|>"


def inceput_de_text(cale: Path, caractere: int) -> str:
    """Primele `caractere` litere din fișier, tăiate după ultimul text întreg (sau, dacă primul text e mai lung, la
    ultimul sfârșit de rând)."""
    with Path(cale).open(encoding="utf-8") as f:
        text = f.read(caractere + 1)
    if len(text) <= caractere:
        return text
    capat = text.rfind(SEPARATOR, 0, caractere)
    if capat > caractere // 2:
        return text[:capat]
    return text[: text.rfind("\n", 0, caractere) + 1] or text[:caractere]
