"""Cercetătorul aleator: primul „agent cercetător”, fără AI.

Alege la întâmplare o singură setare din spațiul permis și îi schimbă
valoarea, pornind mereu de la cea mai bună rețetă de până acum.
Nu repetă combinații deja încercate (le citește din jurnal).

E un punct de plecare simplu și verificabil. În Etapa N5 îl înlocuim
cu un cercetător care folosește Claude Code, pe același port.
"""

from __future__ import annotations

import copy
import json
import random
from typing import Any

from nucleu.contracte import Propunere


def _cheie(setari: dict[str, dict[str, Any]]) -> str:
    return json.dumps(setari, sort_keys=True)


class CercetatorAleator:
    MANIFEST = {
        "nume": "cercetator_aleator",
        "port": "cercetator",
        "versiune": "0.1.0",
        "versiune_contract": 1,
        "resurse": {},
        "permisiuni": [],
    }

    def __init__(self, spatiu: dict[str, dict[str, list[Any]]], samanta: int = 0, incercari: int = 200) -> None:
        if not spatiu or not all(isinstance(v, dict) and v for v in spatiu.values()):
            raise ValueError("spatiu trebuie să fie de forma {port: {setare: [valori posibile]}}")
        for port, setari in spatiu.items():
            for nume, valori in setari.items():
                if not isinstance(valori, list) or not valori:
                    raise ValueError(f"spatiu.{port}.{nume} trebuie să fie o listă nevidă de valori")
        self.spatiu = spatiu
        self.rng = random.Random(samanta)
        self.incercari = incercari

    def propune(self, istoric: list[dict[str, Any]], setari_curente: dict[str, dict[str, Any]]) -> Propunere:
        incercate = {_cheie(f["setari"]) for f in istoric if isinstance(f.get("setari"), dict)}
        incercate.add(_cheie(setari_curente))
        for _ in range(self.incercari):
            port = self.rng.choice(sorted(self.spatiu))
            setare = self.rng.choice(sorted(self.spatiu[port]))
            valoare = self.rng.choice(self.spatiu[port][setare])
            veche = setari_curente.get(port, {}).get(setare)
            if valoare == veche:
                continue
            candidat = copy.deepcopy(setari_curente)
            candidat.setdefault(port, {})[setare] = valoare
            if _cheie(candidat) in incercate:
                continue
            return Propunere(f"{port}.{setare}: {veche} → {valoare}", {port: {setare: valoare}})
        return Propunere("am încercat toate variațiile din jurul celei mai bune rețete", {})
