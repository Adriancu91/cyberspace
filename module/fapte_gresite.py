"""Faptele greșite, după verificarea omului (planul joi–sâmbătă, lecția SANDBOX-7: faptele profesorului le verifică omul).

Adrian citește docs/fapte_de_verificat.md, adică cele 50 de fapte ale hranei, numerotate, și dă numerele celor
greșite. Ele se scriu în date/fapte/fapte_gresite.json: {"numere": [...], "data": "...", "de_la": "Adrian"}.

Din acel moment:
- generarea de hrană (unelte/genereaza_fapte.py) nu mai scrie povești cu ele, iar povesti.txt (hrana) le lasă afară.
  toate.jsonl le păstrează;
- examenele de fapte (module/examene_elev.py) le marchează („fapt_gresit”) și dau, pe lângă scorurile obișnuite, și
  scorurile fără ele. Nimic nu se șterge.

Fără fișier, totul merge exact ca înainte.
"""

from __future__ import annotations

import json
from pathlib import Path

from module.profesor_qwen import SUBIECTE

CALE_FAPTE_GRESITE = "date/fapte/fapte_gresite.json"


def numerotate() -> list[tuple[int, str, str]]:
    """(numărul de la 1, subiectul, faptul), în ordinea profesorului: numerele din docs/fapte_de_verificat.md."""
    return [(i, subiect, fapt) for i, (subiect, fapt) in enumerate(SUBIECTE, start=1)]


def subiectele_gresite(cale: str | Path = CALE_FAPTE_GRESITE) -> set[str]:
    """Subiectele faptelor marcate greșite de om (mulțime goală dacă fișierul lipsește)."""
    fisier = Path(cale)
    if not fisier.exists():
        return set()
    numere = json.loads(fisier.read_text(encoding="utf-8"))["numere"]
    dupa_numar = {i: subiect for i, subiect, _ in numerotate()}
    necunoscute = [n for n in numere if n not in dupa_numar]
    if necunoscute:
        raise ValueError(f"{fisier}: numere de fapte care nu există (1–{len(dupa_numar)}): {necunoscute}")
    return {dupa_numar[n] for n in numere}
