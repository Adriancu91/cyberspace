"""Biblioteca curățată după corectitudine (planul joi–sâmbătă, lecția SANDBOX-7).

**Problema.** O soluție poate trece testul sarcinii ei fără să fie o soluție bună. Exemplu din v0.2: la „show 0”,
soluția `t = 0 ⏎ print(t+0)` dă 0, dar logica ei e greșită. Pe biblioteca liniei B, astfel de soluții învață modelul
lucruri greșite.

**Verificarea.** La fiecare regresie, fiecare soluție din bibliotecă se mută pe sarcinile nevăzute de aceeași formă
ale nivelului ei: valorile sarcinii ei se înlocuiesc cu valorile sarcinii nevăzute. „show 46” → `46` devine
„show 17” → `17`. `t = 0 ⏎ print(t+0)` devine `t = 17 ⏎ print(t+17)`, care dă 34 și pică.

Soluția mutată trece prin sandbox și prin verificator, adică prin același rezultat și aceeași formă ca la examen.
- Dacă pică pe vreuna, iese din bibliotecă: în lucru/cod*/respinse/, cu motivul.
- Sarcinile nevăzute de altă formă (altă propoziție) sau pe care valorile nu se pot muta fără ambiguitate (ex.
  „add 6 and 6” pe „add 3 and 7”) nu se folosesc. O soluție fără nicio sarcină potrivită rămâne.

Modelul nu vede nimic din asta. Doar biblioteca din care învață se curăță.
"""

from __future__ import annotations

import re
from typing import Any, Callable

from module.cod.examen_cod import (CUTII, CUTII_LUNGI, CUVINTE, CUVINTE_0W, CUVINTE_LUNGI, CUVINTE_LUNGI_0W, Sarcina,
                                   judeca)
from module.cod.sandbox import Rulare

BUCATA = re.compile(r"\w+|[^\w\s]")
VOCABULAR = set(CUVINTE) | set(CUVINTE_LUNGI) | set(CUTII) | set(CUTII_LUNGI) | set(CUVINTE_0W) | set(CUVINTE_LUNGI_0W)


def _valoare(bucata: str) -> bool:
    """O bucată de sarcină care poate fi o valoare: un număr, un cuvânt de sarcină sau numele unei cutii."""
    return bucata.isdigit() or bucata in VOCABULAR


def potrivire(sarcina: str, alta: str) -> dict[str, str] | None:
    """Ce valoare a sarcinii devine ce valoare a celeilalte, dacă au aceeași formă; altfel None. Aceeași formă = același
    număr de bucăți, iar acolo unde diferă, amândouă sunt valori. O valoare care ar deveni două valori diferite face
    potrivirea ambiguă (None)."""
    a, b = BUCATA.findall(sarcina), BUCATA.findall(alta)
    if len(a) != len(b):
        return None
    harta: dict[str, str] = {}
    for x, y in zip(a, b):
        if x == y:
            continue
        if not (_valoare(x) and _valoare(y)) or x.isdigit() != y.isdigit() or harta.get(x, y) != y:
            return None
        harta[x] = y
    return harta


def mutata(cod: str, harta: dict[str, str]) -> str:
    """Codul cu valorile înlocuite deodată, pe cuvinte întregi (2→3 și 3→7 nu se încurcă)."""
    if not harta:
        return cod
    model = re.compile(r"\b(?:" + "|".join(re.escape(k) for k in sorted(harta, key=len, reverse=True)) + r")\b")
    return model.sub(lambda m: harta[m.group(0)], cod)


def verifica(intrari: list[dict[str, Any]], nevazut: list[Sarcina], ruleaza: Callable[[list[str]], list[Rulare]],
             cel_mult: int = 5) -> list[tuple[dict[str, Any], str]]:
    """(intrarea, motivul) pentru fiecare soluție care pică pe o sarcină nevăzută de aceeași formă (cel mult `cel_mult`
    sarcini pe soluție). `ruleaza` rulează în sandbox o listă de coduri."""
    perechi: list[tuple[int, Sarcina, str]] = []
    for i, intrare in enumerate(intrari):
        gasite = 0
        for sarcina in nevazut:
            harta = potrivire(intrare["test"], sarcina.text)
            if harta is None:
                continue
            perechi.append((i, sarcina, mutata(intrare["cod"], harta)))
            gasite += 1
            if gasite >= cel_mult:
                break
    rulari = ruleaza([cod for _, _, cod in perechi])
    picate: dict[int, str] = {}
    for (i, sarcina, cod), rulare in zip(perechi, rulari):
        verdict, motiv = judeca(sarcina, cod, rulare)
        if verdict != "trecut" and i not in picate:
            picate[i] = (f"mutată pe sarcina nevăzută „{sarcina.text}” ca `{cod.replace(chr(10), ' ⏎ ')}`: {verdict} "
                         f"({motiv})")
    return [(intrari[i], motiv) for i, motiv in sorted(picate.items())]
