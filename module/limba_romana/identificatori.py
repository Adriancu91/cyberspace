"""Identificatori stabili și deterministici.

Identitatea unui lexem NU depinde doar de ortografie: cheia e (lemă normalizată, categorie, număr de omonim).
Același șir („bancă”) poate fi două lexeme (omonime) sau un lexem cu două sensuri (polisemie) — decizia o ia
sursa care distinge omonimele (Wiktionary, prin numărul de etimologie); celelalte surse se leagă la toate
omonimele, cu notă de proveniență.

Identificatorii sunt hash-uri (sha1, 12 caractere hexa) ale cheii, cu prefix de tip, ca să fie:
  - stabili între rulări (aceeași cheie → același id),
  - imposibil de confundat (un id de sens nu arată ca unul de lexem),
  - independenți de ordinea importului.
"""

from __future__ import annotations

import hashlib

from .text import normalizeaza


def _hash(*parti: str) -> str:
    return hashlib.sha1("|".join(parti).encode("utf8")).hexdigest()[:12]


def id_lexem(lema: str, pos: str, omonim: int = 0) -> str:
    return "L" + _hash("lexem", normalizeaza(lema), pos, str(omonim))


def id_concept(sursa: str, id_extern: str) -> str:
    """Conceptele păstrează identificatorul sursei (de ex. `rown-00006269-n`), ca să fie trasabile."""
    return f"C-{sursa}-{id_extern}"


def id_sens(lexem_id: str, concept_id: str | None, nr: int) -> str:
    return "S" + _hash("sens", lexem_id, concept_id or "", str(nr))


def id_exemplu(sursa: str, id_extern: str) -> str:
    return f"E-{sursa}-{id_extern}"


def id_regula(tip: str, nume: str) -> str:
    return f"R-{tip}-{nume}"
