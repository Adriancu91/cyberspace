"""Verificatorul fără LLM pentru „răspuns din text” (S16, E0; direcția aprobată de Adrian pe 22 octombrie 2026, 01:45).

Notează un răspuns față de referință doar cu reguli scrise de noi, fără Qwen și fără niciun model:
  1. exact: textul normalizat al răspunsului = cel al referinței → corect;
  2. referințe scurte speciale („Nu scrie în text.”, „Da.”, „Nu.”, sau care încep cu „Da,” / „Nu,”): corect doar dacă
     răspunsul începe cu același „nu scrie în text” / „da” / „nu”;
  3. suprapunere (regula principală): acoperirea = câte cuvinte ale referinței (multiset) se găsesc în răspuns ÷ câte
     cuvinte are referința; corect dacă acoperirea ≥ 0,8 și răspunsul nu e „Nu scrie în text.”.
Varianta a doua (doar raportată, nu decide): aceleași reguli 1–2, iar la 3 F1 pe cuvinte ≥ 0,8.

Alegeri care nu scriu anume în sarcină (spuse și în raportul S16):
  - semnele de punctuație se înlocuiesc cu spațiu (așa „într-un” → „într un” la ambele, la fel);
  - la referința „Nu.” / „Nu, …”, răspunsul „Nu scrie în text.” NU contează ca „nu” (e refuz, nu negație);
  - „răspunsul e «Nu scrie în text.»” = răspunsul normalizat începe cu „nu scrie în text”.

    from unelte.verificator_text import verifica
    verifica("Pe 28 mai 1991.", "Pe 28 mai 1991, în Luanda.")  # {'corect': True, 'motiv': 'suprapunere', ...}
"""

from __future__ import annotations

import unicodedata
from collections import Counter

PRAG = 0.8
NU_SCRIE = "nu scrie în text"
_CEDILE = str.maketrans({"ş": "ș", "ţ": "ț", "Ş": "ș", "Ţ": "ț"})


def normalizeaza(text: str) -> str:
    """Litere mici, ş/ţ → ș/ț, ghilimele și punctuație scoase, spații comprimate. Diacriticele rămân."""
    text = unicodedata.normalize("NFC", text or "").translate(_CEDILE).lower()
    curat = "".join(" " if unicodedata.category(c).startswith("P") else c for c in text)
    return " ".join(curat.split())


def cuvinte(text: str) -> list[str]:
    return normalizeaza(text).split()


def _incepe_cu(cuv: list[str], prefix: list[str]) -> bool:
    return cuv[: len(prefix)] == prefix


def _fel_special(referinta: str) -> str | None:
    """„nu_scrie”, „da”, „nu” dacă referința e una din cele scurte speciale; altfel None."""
    brut = " ".join((referinta or "").split()).translate(_CEDILE).lower()
    norm = normalizeaza(referinta)
    if norm == NU_SCRIE:
        return "nu_scrie"
    if norm == "da" or brut.startswith("da,"):
        return "da"
    if norm == "nu" or brut.startswith("nu,"):
        return "nu"
    return None


def _comune(ref: list[str], rasp: list[str]) -> int:
    return sum((Counter(ref) & Counter(rasp)).values())


def verifica(referinta: str, raspuns: str) -> dict:
    """Verdictul pentru un răspuns: corect (regula principală), motiv, scor (= acoperirea), plus varianta F1."""
    ref, rasp = cuvinte(referinta), cuvinte(raspuns)
    refuz = _incepe_cu(rasp, NU_SCRIE.split())
    comune = _comune(ref, rasp)
    acoperire = comune / len(ref) if ref else 0.0
    precizie = comune / len(rasp) if rasp else 0.0
    f1 = 2 * precizie * acoperire / (precizie + acoperire) if precizie + acoperire else 0.0
    rezultat = {"acoperire": round(acoperire, 4), "f1": round(f1, 4), "scor": round(acoperire, 4)}

    if ref and rasp == ref:
        return {**rezultat, "corect": True, "motiv": "exact", "corect_f1": True, "motiv_f1": "exact"}
    fel = _fel_special(referinta)
    if fel is not None:
        if fel == "nu_scrie":
            bun = refuz
        elif fel == "da":
            bun = _incepe_cu(rasp, ["da"])
        else:
            bun = _incepe_cu(rasp, ["nu"]) and not refuz
        motiv = f"special_{fel}"
        return {**rezultat, "corect": bun, "motiv": motiv, "corect_f1": bun, "motiv_f1": motiv}
    corect = bool(ref) and acoperire >= PRAG and not refuz
    corect_f1 = bool(ref) and f1 >= PRAG and not refuz
    motiv = "refuz" if refuz else "suprapunere"
    return {**rezultat, "corect": corect, "motiv": motiv, "corect_f1": corect_f1, "motiv_f1": motiv}
