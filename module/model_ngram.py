"""Modelul n-gram pe caractere: primul model „de la 0”, fără placă video.

Numără ce caracter urmează după fiecare context de 1..(ordin-1) caractere
și combină ordinele (netezire Dirichlet). E simplu, rapid și învață real,
deci bucla de auto-îmbunătățire are ceva de optimizat din prima seară.

Setări pe care Cercetătorul le poate schimba:
- ordin: câte caractere „vede” înapoi (1 = niciunul, 5 = patru)
- netezire: cât de mult se bazează pe ordinele mai mici (mai mare = mai prudent)
"""

from __future__ import annotations

import json
import math
import random
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

NECUNOSCUT = "�"


class ModelNgram:
    MANIFEST = {
        "nume": "model_ngram",
        "port": "model",
        "versiune": "0.1.0",
        "versiune_contract": 1,
        "resurse": {"gpu": False},
        "permisiuni": [],
    }

    def __init__(self, ordin: int = 2, netezire: float = 1.0, samanta: int = 1337) -> None:
        if not isinstance(ordin, int) or not 1 <= ordin <= 8:
            raise ValueError("ordin trebuie să fie un număr întreg între 1 și 8")
        if not netezire > 0:
            raise ValueError("netezire trebuie să fie mai mare ca 0")
        self.ordin = ordin
        self.netezire = float(netezire)
        self.samanta = samanta
        self.vocabular: list[str] = [NECUNOSCUT]
        self._index: set[str] = {NECUNOSCUT}
        # numaratori[n][context de n caractere][caracter] = de câte ori
        self.numaratori: list[dict[str, Counter]] = [defaultdict(Counter) for _ in range(ordin)]
        self.totaluri: list[dict[str, int]] = [{} for _ in range(ordin)]

    # --- antrenare -------------------------------------------------------

    def antreneaza(self, date: Any, buget_secunde: float) -> dict[str, Any]:
        text = date.text_antrenare()
        start = time.perf_counter()
        self.vocabular = sorted(set(text)) + [NECUNOSCUT]
        self._index = set(self.vocabular)
        numaratori: list[dict[str, Counter]] = [defaultdict(Counter) for _ in range(self.ordin)]
        oprit_de_buget = False
        vazute = 0
        for i, c in enumerate(text):
            for n in range(self.ordin):
                if i - n < 0:
                    break
                numaratori[n][text[i - n : i]][c] += 1
            vazute = i + 1
            if i % 20_000 == 0 and time.perf_counter() - start > buget_secunde:
                oprit_de_buget = True
                break
        self.numaratori = numaratori
        self.totaluri = [{ctx: sum(t.values()) for ctx, t in nivel.items()} for nivel in numaratori]
        return {
            "caractere_vazute": vazute,
            "vocabular": len(self.vocabular),
            "contexte": sum(len(n) for n in numaratori),
            "oprit_de_buget": oprit_de_buget,
        }

    # --- probabilități -------------------------------------------------------

    def _probabilitate(self, context: str, c: str) -> float:
        if c not in self._index:
            c = NECUNOSCUT
        p = 1.0 / len(self.vocabular)
        for n in range(self.ordin):
            if n > len(context):
                break
            ctx = context[len(context) - n :] if n else ""
            tabel = self.numaratori[n].get(ctx)
            if tabel is None:
                break  # contextul ăsta n-a fost văzut, deci nici cele mai lungi
            p = (tabel.get(c, 0) + self.netezire * p) / (self.totaluri[n][ctx] + self.netezire)
        return p

    def distributie(self, context: str) -> dict[str, float]:
        """Probabilitatea fiecărui caracter din vocabular (suma = 1)."""
        return {c: self._probabilitate(context, c) for c in self.vocabular}

    def biti_pentru(self, text: str) -> float:
        biti = 0.0
        for i, c in enumerate(text):
            context = text[max(0, i - self.ordin + 1) : i]
            biti -= math.log2(self._probabilitate(context, c))
        return biti

    def genereaza(self, inceput: str, lungime: int) -> str:
        rng = random.Random(self.samanta)
        text = inceput
        candidati = [c for c in self.vocabular if c != NECUNOSCUT] or [" "]
        for _ in range(lungime):
            context = text[max(0, len(text) - self.ordin + 1) :]
            ponderi = [self._probabilitate(context, c) for c in candidati]
            text += rng.choices(candidati, weights=ponderi, k=1)[0]
        return text[len(inceput) :]

    # --- salvare ---------------------------------------------------------------

    def salveaza(self, cale: str) -> str:
        fisier = Path(cale).with_suffix(".json")
        fisier.parent.mkdir(parents=True, exist_ok=True)
        stare = {
            "ordin": self.ordin,
            "netezire": self.netezire,
            "vocabular": self.vocabular,
            "numaratori": [{ctx: dict(t) for ctx, t in nivel.items()} for nivel in self.numaratori],
        }
        fisier.write_text(json.dumps(stare, ensure_ascii=False), encoding="utf-8")
        return str(fisier)

    def incarca(self, cale: str) -> None:
        fisier = Path(cale)
        if not fisier.exists():
            fisier = fisier.with_suffix(".json")
        stare = json.loads(fisier.read_text(encoding="utf-8"))
        self.ordin = stare["ordin"]
        self.netezire = stare["netezire"]
        self.vocabular = stare["vocabular"]
        self._index = set(self.vocabular)
        self.numaratori = [
            defaultdict(Counter, {ctx: Counter(t) for ctx, t in nivel.items()}) for nivel in stare["numaratori"]
        ]
        self.totaluri = [{ctx: sum(t.values()) for ctx, t in nivel.items()} for nivel in self.numaratori]
