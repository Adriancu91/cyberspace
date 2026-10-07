"""ALEGE (etapa 4): o singură nevoie pe ciclu (secțiunea 4.4 din plan).

Nevoile se iau în ordinea urgenței: „repara” întâi, apoi ordinea din [continuum] „ordinea_nevoilor”; când povestirile
sunt saturate, „dezvolta” trece înaintea lui „continua” (nevoi.py). Prima care se poate face acum e aleasă. Pentru
celelalte, jurnalul spune de ce nu, în ordinea asta:
- nivelul de acum nu o permite (de ex. o antrenare cere ÎNVĂȚARE, cu placa liberă);
- ACȚIONEAZĂ n-are cu ce o face („capacitate_indisponibila”) ori nu e cazul acum;
- e în **răcire** (v1, anti-buclă): o nevoie tratată nu se reia [anti_bucla] racire_cicluri cicluri; „repara” nu are
  răcire;
- strategia ei e **blocată** (v1, anti-buclă): după prea multe eșecuri la rând, omul a primit un raport.
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


def alege(nevoi: list[Nevoie], stare: StareaOrganismului, config: dict[str, Any], memorie: dict[str, Any] | None = None,
          ciclu: int | None = None) -> Alegere:
    alegere = Alegere()
    racire = (memorie or {}).get("racire") or {}
    strategii = (memorie or {}).get("strategii") or {}
    for nevoie in sorted(nevoi, key=lambda n: n.urgenta):
        cerut = config["nevoi"][nevoie.tip]["nivel"]
        if not guvernator.permite(stare.nivel, cerut):
            alegere.sarite.append({"nevoie": nevoie.cheie, "de_ce_nu": f"nivelul {stare.nivel} nu o permite (cere {cerut})"})
            continue
        plan = planifica(nevoie, stare, config, memorie)
        if isinstance(plan, Refuz):
            eticheta = "capacitate_indisponibila: " if plan.indisponibila else "nu acum: "
            alegere.sarite.append({"nevoie": nevoie.cheie, "de_ce_nu": eticheta + plan.motiv})
            continue
        pana_la = racire.get(nevoie.cheie)
        if nevoie.tip != "repara" and ciclu is not None and pana_la is not None and ciclu <= pana_la:
            alegere.sarite.append({"nevoie": nevoie.cheie, "de_ce_nu": f"în răcire până la ciclul {pana_la} (a fost "
                                                                       f"tratată de curând)"})
            continue
        strategie = strategii.get(plan.strategie) or {}
        if strategie.get("stare") == "blocată":
            alegere.sarite.append({"nevoie": nevoie.cheie, "de_ce_nu": (
                f"strategia {plan.strategie} e blocată după {strategie.get('esecuri_la_rand')} eșecuri la rând; omul "
                f"a primit un raport")})
            continue
        alegere.nevoie, alegere.plan = nevoie, plan
        break
    return alegere
