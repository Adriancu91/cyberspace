"""Lucruri comune importatoarelor: directoare, înregistrarea surselor, alegerea lexemului-țintă.

Regula omonimelor: dacă pentru (lemă, categorie) există lexeme numerotate (omonime distinse de Wiktionary),
o sursă care NU distinge omonimele își leagă dovezile de TOATE omonimele, cu detaliul „atribuit tuturor omonimelor”.
Altfel se folosește (și se creează la nevoie) lexemul cu numărul 0.
"""

from __future__ import annotations

import json
from pathlib import Path

from ..baza import Baza
from ..identificatori import id_lexem
from ..text import normalizeaza

RADACINA = Path(__file__).resolve().parent.parent
DIR_SURSE = RADACINA / "_surse"


def manifest_sursa(prefix: str) -> dict:
    """Intrările din `_surse/manifest.json` ale unei surse (pentru data descărcării și amprente)."""
    cale = DIR_SURSE / "manifest.json"
    if not cale.exists():
        return {}
    m = json.loads(cale.read_text("utf8"))
    return {k: v for k, v in m.items() if v.get("sursa") == prefix}


def lexeme_tinta(baza: Baza, lema: str, pos: str, sursa_id: str, statut: str = "importat", gen: str | None = None,
                 clasa: str | None = None, multicuvant: bool = False, atribute: dict | None = None, detalii: str = "") -> list[str]:
    """Întoarce id-urile lexemelor la care se leagă o dovadă pentru (lemă, categorie)."""
    norm = normalizeaza(lema)
    omonime = [r[0] for r in baza.con.execute("SELECT id FROM lexeme WHERE lema_norm = ? AND pos = ? AND omonim > 0", (norm, pos))]
    if omonime:
        for lid in omonime:
            baza.adauga_lexem(lid, lema, pos, 0, statut, sursa_id, gen=gen, clasa=clasa, multicuvant=multicuvant, atribute=atribute,
                              detalii_sursa=(detalii + "; " if detalii else "") + "atribuit tuturor omonimelor (sursa nu le distinge)")
        return omonime
    lid = id_lexem(lema, pos, 0)
    baza.adauga_lexem(lid, lema, pos, 0, statut, sursa_id, gen=gen, clasa=clasa, multicuvant=multicuvant, atribute=atribute, detalii_sursa=detalii)
    return [lid]


class Numarator:
    """Contor simplu pentru rapoartele de import."""

    def __init__(self) -> None:
        self.c: dict[str, int] = {}

    def __call__(self, cheie: str, n: int = 1) -> None:
        self.c[cheie] = self.c.get(cheie, 0) + n

    def dict(self) -> dict[str, int]:
        return dict(sorted(self.c.items()))
