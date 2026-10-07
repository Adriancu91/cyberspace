"""Zgomotul învățat (v1, punctul 1): cât diferă de obicei două măsurători ale aceluiași lucru, din jurnalul Kronos.

**Perechile de măsurători:**
- **același model examinat de două ori:** aceeași capacitate, același experiment, din surse diferite. Sursele sunt
  scorurile fișei, criteriile de la oră și fișele uneltelor de examen; fiecare două măsurători la rând fac o pereche.
- **două semințe ale aceleiași configurări:** experimente reușite care au, pe rând:
  - aceleași setări ale modelului (în afară de sămânță și de fișierele stării);
  - același text de antrenare;
  - aceeași durată (în minute);
  - dar semințe diferite.

  În fiecare grup se ia prima măsurătoare a fiecărei semințe, iar perechile sunt semințele vecine.

**Zgomotul învățat** e rădăcina mediei pătratelor diferențelor (cât diferă de obicei două măsurători), înmulțit cu
[zgomot] factor. **Pragul folosit** = max(podea, zgomot învățat), unde podeaua e prag_zgomot din [capacitati]. Sub
[zgomot] perechi_minime perechi rămâne podeaua, iar jurnalul spune „neînvățat încă”.

**Zgomotul de remăsurare** se învață la fel, dar doar din perechile „același model examinat de două ori”. El contează
între două ore ale aceleiași antrenări (regula „continuă”): acolo sămânța e aceeași, deci zgomotul dintre semințe nu se
aplică.
"""

from __future__ import annotations

import json
import math
from collections import defaultdict
from typing import Any

from module.continuum.masuratori import REUSITE, criterii_din, masuratori_unelte, numar, valoare

# Setările care nu schimbă „configurarea” unei semințe: sămânța însăși și unde își ține modelul starea.
NU_CONTEAZA = ("samanta", "cale_stare", "director_stari", "stare_de_pornire", "de_la_zero", "director_cache")
NEINVATAT = "neînvățat încă"
INVATAT = "învățat"


def masuratori_pe_experiment(fise: list[dict[str, Any]], cap: dict[str, Any]) -> dict[int, list[float]]:
    """Toate măsurătorile capacității pe modelul fiecărui experiment, în ordinea în care au fost făcute."""
    rezultat: dict[int, list[float]] = defaultdict(list)
    linie_unealta = cap["unealta"]["linie"] if cap["unealta"] else None
    for fisa in sorted(fise, key=lambda f: f.get("id", 0)):
        if fisa.get("decizie") in REUSITE:
            for sursa in ((fisa.get("scoruri") or {}), criterii_din(fisa)):
                if numar(sursa.get(cap["metrica"])):
                    rezultat[fisa["id"]].append(float(sursa[cap["metrica"]]))
        elif linie_unealta and fisa.get("linie") == linie_unealta:
            experiment = ((fisa.get("module") or {}).get("elev") or {}).get("experiment")
            scor = (fisa.get("scoruri") or {}).get(cap["unealta"]["scor"])
            if isinstance(experiment, int) and numar(scor):
                rezultat[experiment].append(float(scor))
    return rezultat


def perechi_acelasi_model(fise: list[dict[str, Any]], cap: dict[str, Any]) -> list[float]:
    return [b - a for valori in masuratori_pe_experiment(fise, cap).values() for a, b in zip(valori, valori[1:])]


def _configuratia(fisa: dict[str, Any]) -> str | None:
    model = (fisa.get("setari") or {}).get("model") or {}
    if "samanta" not in model:
        return None
    statistici = fisa.get("statistici_antrenare") or {}
    minute = round(((fisa.get("consum") or {}).get("durata_antrenare_secunde") or 0) / 60)
    return json.dumps([{k: v for k, v in sorted(model.items()) if k not in NU_CONTEAZA},
                       statistici.get("simboluri_antrenare"), minute], sort_keys=True, default=str)


def perechi_seminte(fise: list[dict[str, Any]], cap: dict[str, Any]) -> list[float]:
    unelte = masuratori_unelte(fise, {"capacitati": {"x": cap}})
    grupe: dict[str, dict[Any, float]] = defaultdict(dict)
    for fisa in sorted(fise, key=lambda f: f.get("id", 0)):
        if fisa.get("decizie") not in REUSITE:
            continue
        cheie, v = _configuratia(fisa), valoare(fisa, cap, unelte)
        if cheie is not None and v is not None:
            grupe[cheie].setdefault(fisa["setari"]["model"]["samanta"], v)  # prima măsurătoare a fiecărei semințe
    perechi = []
    for pe_samanta in grupe.values():
        valori = [pe_samanta[s] for s in sorted(pe_samanta, key=str)]
        perechi += [b - a for a, b in zip(valori, valori[1:])]
    return perechi


def _rms(diferente: list[float], reguli: dict[str, Any]) -> float | None:
    """Cât diferă de obicei două măsurători (× factor); None sub perechi_minime perechi."""
    if len(diferente) < reguli["perechi_minime"]:
        return None
    return round(reguli["factor"] * math.sqrt(sum(d * d for d in diferente) / len(diferente)), 6)


def zgomot_invatat(fise: list[dict[str, Any]], cap: dict[str, Any], reguli: dict[str, Any]) -> dict[str, Any]:
    """{"perechi", "zgomot" (sau None), "podea", "prag" (cel folosit), "stare" (învățat / neînvățat încă),
    "perechi_remasurare", "zgomot_remasurare" (doar din „același model de două ori”, sau None)}."""
    acelasi_model = perechi_acelasi_model(fise, cap)
    diferente = acelasi_model + perechi_seminte(fise, cap)
    podea, zgomot = cap["prag_zgomot"], _rms(diferente, reguli)
    return {"perechi": len(diferente), "zgomot": zgomot, "podea": podea,
            "prag": podea if zgomot is None else max(podea, zgomot), "stare": NEINVATAT if zgomot is None else INVATAT,
            "perechi_remasurare": len(acelasi_model), "zgomot_remasurare": _rms(acelasi_model, reguli)}
