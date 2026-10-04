"""Cercetătorul în două faze: întâi lista, apoi strânge căutarea în jurul celor mai bune 3 rețete.

Faza 1, lista: fiecare valoare din spațiul dat se încearcă o dată, ca singură schimbare față de cea mai bună rețetă de
atunci (cea păstrată de Kronos). Perechile (setare, valoare) vin într-o ordine amestecată, mereu aceeași pentru aceeași
sămânță; nicio rețetă nu se repetă (le citește din jurnal).
Faza 2, strângerea: când fiecare valoare din listă a fost încercată (lista s-a epuizat), ia cele mai bune 3 rețete
încercate (după scor) și caută între valori: pentru fiecare setare, jumătatea drumului spre valorile vecine deja
cunoscute (ex. rata 0,0003 între 0,0002 și 0,0005 → 0,00025 și 0,0004), rotunjită la valori valide (setarea „pasi”: ex.
n_emb din 32 în 32). Întâi golurile cele mai mari, din jurul oricăreia din cele 3 rețete; fiecare valoare nouă intră
între cele cunoscute, deci căutarea devine tot mai fină, până la schimbări de 10%.
Dacă și asta se epuizează, propunerea e goală și Kronos se oprește singur.
"""

from __future__ import annotations

import copy
import json
import math
import random
from typing import Any

from kronos.contracte import Propunere

PRAG_FIN = 0.1  # la strângere, o valoare nouă trebuie să difere cu cel puțin 10% de cea de la care pornește


def _cheie(setari: dict[str, dict[str, Any]]) -> str:
    return json.dumps(setari, sort_keys=True)


def _rotunjeste(valoare: float, exemplu: Any, pas: float | None) -> Any:
    """La un număr întreg (multiplu de `pas`) dacă setarea e întreagă; altfel la 3 cifre semnificative."""
    if isinstance(exemplu, int) and not isinstance(exemplu, bool):
        pas = int(pas or 1)
        return max(pas, int(round(valoare / pas)) * pas)
    if valoare == 0:
        return 0.0
    return float(f"{valoare:.3g}")


class CercetatorLocal:
    MANIFEST = {
        "nume": "cercetator_local",
        "port": "cercetator",
        "versiune": "0.1.0",
        "versiune_contract": 1,
        "resurse": {},
        "permisiuni": [],
    }

    def __init__(
        self,
        spatiu: dict[str, dict[str, list[Any]]],
        samanta: int = 0,
        pasi: dict[str, float] | None = None,
        scor: str = "val_bpb",
        mai_mic_e_mai_bun: bool = True,
        cele_mai_bune: int = 3,
    ) -> None:
        if not spatiu or not all(isinstance(v, dict) and v for v in spatiu.values()):
            raise ValueError("spatiu trebuie să fie de forma {port: {setare: [valori posibile]}}")
        for port, setari in spatiu.items():
            for nume, valori in setari.items():
                if not isinstance(valori, list) or not valori:
                    raise ValueError(f"spatiu.{port}.{nume} trebuie să fie o listă nevidă de valori")
        self.spatiu = spatiu
        self.pasi = pasi or {}
        self.scor = scor
        self.mai_mic_e_mai_bun = mai_mic_e_mai_bun
        self.cele_mai_bune = cele_mai_bune
        perechi = [(port, s, v) for port in sorted(spatiu) for s in sorted(spatiu[port]) for v in spatiu[port][s]]
        random.Random(samanta).shuffle(perechi)
        self._ordine = perechi

    def _scorul(self, fisa: dict[str, Any]) -> float | None:
        valoare = (fisa.get("scoruri") or {}).get(self.scor)
        return valoare if isinstance(valoare, (int, float)) and math.isfinite(valoare) else None

    def propune(self, istoric: list[dict[str, Any]], setari_curente: dict[str, dict[str, Any]]) -> Propunere:
        retete = [f["setari"] for f in istoric if isinstance(f.get("setari"), dict)]
        incercate = {_cheie(r) for r in retete} | {_cheie(setari_curente)}
        # Faza 1: fiecare valoare din listă, o dată, ca singură schimbare față de cea mai bună rețetă de atunci.
        for port, setare, valoare in self._ordine:
            veche = setari_curente.get(port, {}).get(setare)
            if valoare == veche or any(r.get(port, {}).get(setare) == valoare for r in retete):
                continue  # valoarea a fost deja încercată (sau e chiar cea de acum)
            candidat = copy.deepcopy(setari_curente)
            candidat.setdefault(port, {})[setare] = valoare
            if _cheie(candidat) not in incercate:
                return Propunere(f"lista: {port}.{setare}: {veche} → {valoare}", {port: {setare: valoare}})
        # Faza 2: între valorile cunoscute, în jurul celor mai bune 3 rețete încercate.
        cu_scor = [(s, f) for f in istoric if isinstance(f.get("setari"), dict) and (s := self._scorul(f)) is not None]
        cu_scor.sort(key=lambda x: x[0], reverse=not self.mai_mic_e_mai_bun)
        alese: list[tuple[float, dict[str, Any]]] = []
        for s, f in cu_scor:
            if _cheie(f["setari"]) not in {_cheie(a["setari"]) for _, a in alese}:
                alese.append((s, f))
            if len(alese) == self.cele_mai_bune:
                break
        cunoscute = {
            (port, setare): sorted({*valori, *(f["setari"].get(port, {}).get(setare) for f in istoric
                                              if isinstance(f.get("setari"), dict)
                                              and isinstance(f["setari"].get(port, {}).get(setare), (int, float)))})
            for port, setari in self.spatiu.items() for setare, valori in setari.items()
        }
        candidati = []  # (golul relativ, locul, setarea, rețeta nouă...): întâi golurile cele mai mari
        for loc, (scor, fisa) in enumerate(alese, start=1):
            reteta = fisa["setari"]
            for port, setare in sorted({(p, s) for p, s, _ in self._ordine}):
                actuala = reteta.get(port, {}).get(setare)
                if not isinstance(actuala, (int, float)) or isinstance(actuala, bool):
                    continue
                valori = cunoscute[(port, setare)]
                vecini = [v for v in (max((v for v in valori if v < actuala), default=None),
                                      min((v for v in valori if v > actuala), default=None)) if v is not None]
                for vecin in vecini:
                    noua = _rotunjeste((actuala + vecin) / 2, actuala, self.pasi.get(setare))
                    if noua in (actuala, vecin) or abs(noua - actuala) < PRAG_FIN * abs(actuala):
                        continue  # nimic nou între ele, sau o schimbare prea mică să conteze
                    candidat = copy.deepcopy(reteta)
                    candidat.setdefault(port, {})[setare] = noua
                    if _cheie(candidat) not in incercate:
                        gol = abs(vecin - actuala) / max(abs(actuala), 1e-12)
                        candidati.append((-gol, loc, port, setare, actuala, noua, fisa.get("id"), scor, candidat))
        if candidati:
            _, loc, port, setare, actuala, noua, id_fisa, scor, candidat = min(candidati, key=lambda c: c[:4])
            return Propunere(
                f"strângere în jurul locului {loc} (#{id_fisa}, scor {scor:.4f}): {port}.{setare}: {actuala} → {noua}",
                {port: candidat[port]},
            )
        return Propunere("am încercat toată lista și tot ce e între valori în jurul celor mai bune rețete", {})
