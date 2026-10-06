"""ALEGE (etapa 4): o singură nevoie pe ciclu (secțiunea 4.4 din plan).

Nevoile se iau în ordinea urgenței (măsurare, apoi învățare, apoi dezvoltare, cum spune [continuum]
„ordinea_nevoilor”). Prima care se poate face acum e aleasă. Pentru celelalte, jurnalul spune de ce nu:
- nivelul de acum nu o permite (de ex. o antrenare cere ÎNVĂȚARE, adică noaptea, cu placa liberă);
- sau ACȚIONEAZĂ n-are cu ce o face („capacitate_indisponibila”) ori nu e cazul acum.
Regulile anti-buclă (răcire, limită de reîncercări) sunt pentru v1.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from module.continuum import guvernator
from module.continuum.actioneaza import Plan, Refuz, planifica
from module.continuum.evalueaza import StareaOrganismului
from module.continuum.nevoi import Nevoie


@dataclass
class Alegere:
    nevoie: Nevoie | None = None
    plan: Plan | None = None
    sarite: list[dict[str, str]] = field(default_factory=list)  # [{"nevoie", "de_ce_nu"}]


def alege(nevoi: list[Nevoie], stare: StareaOrganismului, config: dict[str, Any]) -> Alegere:
    alegere = Alegere()
    for nevoie in sorted(nevoi, key=lambda n: n.urgenta):
        cerut = config["nevoi"][nevoie.tip]["nivel"]
        if not guvernator.permite(stare.nivel, cerut):
            alegere.sarite.append({"nevoie": nevoie.cheie, "de_ce_nu": f"nivelul {stare.nivel} nu o permite (cere {cerut})"})
            continue
        plan = planifica(nevoie, stare, config)
        if isinstance(plan, Refuz):
            eticheta = "capacitate_indisponibila: " if plan.indisponibila else "nu acum: "
            alegere.sarite.append({"nevoie": nevoie.cheie, "de_ce_nu": eticheta + plan.motiv})
            continue
        alegere.nevoie, alegere.plan = nevoie, plan
        break
    return alegere
