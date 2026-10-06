"""NEVOI (etapa 3): starea organismului → nevoi, fiecare cu tip, capacitate, urgență și motiv (secțiunea 4.3).

În v0 sunt doar trei nevoi; urgența e locul lor în [continuum] „ordinea_nevoilor”:
- **masoara**: ultimul model păstrat n-a dat toate examenele. Fiecare capacitate cu „masurare” trebuie să aibă o
  valoare pe el.
- **continua**: povestirile încă învață. Se cere dacă:
  - val_bpb a coborât în ultima oră cu cel puțin „castig_minim”; sau
  - ultima antrenare lungă e neterminată (linia ei are mai puține ore decât „experimente”).
- **dezvolta**: cea mai slabă capacitate (cel mai mic procent din maxim), cu ce se știe despre hrana ei.

Nevoile nu țin cont de nivel, de module sau de configurările care lipsesc. Asta o face ALEGE: sare peste ce nu se
poate face acum și spune de ce.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from module.continuum import cate, ro, ro_scurt
from module.continuum.evalueaza import StareaOrganismului, se_potriveste


@dataclass
class Nevoie:
    tip: str          # masoara / continua / dezvolta
    capacitate: str   # ex. „fapte”; la masoara, capacitățile nemăsurate, legate cu „+”
    urgenta: int      # 1 = cea mai urgentă
    motiv: str        # în română, pentru jurnal
    detalii: dict[str, Any] = field(default_factory=dict)

    @property
    def cheie(self) -> str:
        return f"{self.tip}:{self.capacitate}"


def nevoie_masoara(stare: StareaOrganismului, config: dict[str, Any], urgenta: int) -> Nevoie | None:
    if stare.ultimul_model is None:
        return None
    lipsa = [n for n, c in stare.capacitati.items() if config["capacitati"][n]["masurare"] and c.curent is None]
    if not lipsa:
        return None
    experiment = stare.ultimul_model["experiment"]
    return Nevoie("masoara", "+".join(lipsa), urgenta,
                  f"examenele n-au mai fost date pe ultimul model păstrat (#{experiment}): lipsesc {', '.join(lipsa)}",
                  {"capacitati": lipsa, "experiment": experiment})


def nevoie_continua(stare: StareaOrganismului, config: dict[str, Any], urgenta: int) -> Nevoie | None:
    reguli = config["nevoi"]["continua"]
    t = stare.tendinta
    if t and t["castig"] is not None and t["castig"] >= reguli["castig_minim"]:
        c = stare.capacitati[t["capacitate"]]
        directia = "crește" if c.mai_mare_e_mai_bine else "scade"
        motiv = (f"{c.metrica} încă {directia} de la o oră la alta: {ro(t['de_la']['valoare'], 4)} → "
                 f"{ro(t['la']['valoare'], 4)} (#{t['de_la']['experiment']} → #{t['la']['experiment']}, linia "
                 f"{t['linie']}), un câștig de {ro(t['castig'], 4)}, cel puțin pragul de {ro_scurt(reguli['castig_minim'])}")
    else:
        # Doar o antrenare lungă întreruptă; o linie pe hrană întreruptă se reia prin „dezvolta”.
        neterminate = [l for cale, l in stare.linii.items() if l.get("stare") == "ok" and t and l["linie"] == t["linie"]
                       and not l["terminata"] and se_potriveste(cale, reguli["configurari"])]
        if not neterminate:
            return None
        l = neterminate[0]
        motiv = (f"antrenarea de pe linia {l['linie']} e neterminată: {cate(l['ore_facute'], 'ore')} din "
                 f"{l['ore_planificate']}")
    return Nevoie("continua", reguli["capacitate"], urgenta, motiv, {"linie": t["linie"] if t else None})


def nevoie_dezvolta(stare: StareaOrganismului, config: dict[str, Any], urgenta: int) -> Nevoie | None:
    cu_procent = sorted((c for c in stare.capacitati.values() if c.procent is not None), key=lambda c: (c.procent, c.nume))
    if not cu_procent:
        return None
    slaba = cu_procent[0]
    motiv = f"{slaba.nume} = {ro(slaba.procent)}% ({ro_scurt(slaba.curent)} din {ro_scurt(slaba.maxim)}), cea mai slabă capacitate"
    if len(cu_procent) > 1:
        motiv += " (" + ", ".join(f"{c.nume} = {ro(c.procent)}%" for c in cu_procent[1:]) + ")"
    h = stare.hrana.get(slaba.nume)
    if h is None:
        motiv += "; n-are hrană în [hrana]"
    elif h.get("stare") != "ok":
        motiv += f"; hrana din {h['dosar']} nu se poate citi"
    elif h["nefolosita"]:
        motiv += f"; {cate(h['povesti'], 'povești')} nefolosite în {h['dosar']}"
    else:
        motiv += f"; hrana din {h['dosar']} ({cate(h['povesti'], 'povești')}) a fost folosită de {', '.join(h['folosita_de'])}"
    return Nevoie("dezvolta", slaba.nume, urgenta, motiv, {"procent": slaba.procent})


NEVOI = {"masoara": nevoie_masoara, "continua": nevoie_continua, "dezvolta": nevoie_dezvolta}


def nevoi(stare: StareaOrganismului, config: dict[str, Any]) -> list[Nevoie]:
    """Nevoile de acum, în ordinea urgenței. Doar tipurile configurate în [nevoi]."""
    rezultat = []
    for urgenta, tip in enumerate(config["continuum"]["ordinea_nevoilor"], start=1):
        if tip in config["nevoi"]:
            nevoie = NEVOI[tip](stare, config, urgenta)
            if nevoie is not None:
                rezultat.append(nevoie)
    return rezultat
