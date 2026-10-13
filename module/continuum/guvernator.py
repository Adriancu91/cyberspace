"""Guvernatorul: ce nivel de activitate e permis acum (secțiunea 9 din plan). Separat de buclă și simplu.

Nu înlocuiește paznicul: paznicul oprește un experiment în curs (temperatură, memorie video, timp), iar guvernatorul
decide doar dacă se poate porni unul. Ferestrele și pragurile sunt toate în config/continuum.toml, la [guvernator].

Nivelurile din v0, de la cel mai liniștit:
- REPAUS: doar observă. Se ajunge aici dacă:
  - omul folosește laptopul;
  - placa e ocupată de altă sarcină sau nu poate fi citită;
  - ora e în afara ferestrelor.
- ÎNTREȚINERE: în fereastra de zi, cu placa liberă. Se pot da examene și se poate cere hrană de la profesor, dar nu
  se pornesc antrenări.
- ÎNVĂȚARE: în fereastra de noapte, cu placa liberă. Se pot porni și antrenări lungi.

Placa prea caldă coboară un nivel. „O singură sarcină grea pe placă odată”: placa e ocupată dacă un program din
„procese_grele” (de ex. python, adică Kronos sau profesorul) o folosește, sau dacă are prea puțină memorie liberă.

v1, anti-buclă: **bugetul zilnic de ore pe placă** ([guvernator] buget_ore_placa_pe_zi). Orele de azi se adună din
jurnalul Kronos (cât au durat experimentele începute azi, oricine le-a pornit); peste buget, REPAUS până mâine.
"""

from __future__ import annotations

from datetime import date, datetime
from datetime import time as Ora
from pathlib import PureWindowsPath
from typing import Any

from module.continuum import INTRETINERE, INVATARE, NIVELURI, REPAUS, ro


def in_fereastra(ora: Ora, fereastra: tuple[Ora, Ora]) -> bool:
    """Ora e în fereastră? O fereastră ca 22:00–07:00 trece peste miezul nopții."""
    inceput, sfarsit = fereastra
    if inceput <= sfarsit:
        return inceput <= ora < sfarsit
    return ora >= inceput or ora < sfarsit


def secunde_pana_la_fereastra(acum: datetime, config: dict[str, Any]) -> float:
    """Câte secunde mai sunt până la cel mai apropiat început de fereastră (de învățare sau de întreținere)."""
    g = config["guvernator"]
    asteptari = []
    for inceput, _ in (g["fereastra_invatare"], g["fereastra_intretinere"]):
        secunde = (datetime.combine(acum.date(), inceput) - acum).total_seconds()
        asteptari.append(secunde if secunde > 0 else secunde + 86400)
    return min(asteptari)


def text_fereastra(fereastra: tuple[Ora, Ora]) -> str:
    return f"{fereastra[0]:%H:%M}–{fereastra[1]:%H:%M}"


def coboara(nivel: str) -> str:
    return NIVELURI[max(0, NIVELURI.index(nivel) - 1)]


def permite(nivel: str, nivel_cerut: str) -> bool:
    """Nivelul de acum permite ce cere nivelul dat? (ÎNVĂȚARE permite tot ce permite ÎNTREȚINERE.)"""
    return NIVELURI.index(nivel) >= NIVELURI.index(nivel_cerut)


def procese_grele(placa: dict[str, Any], nume_grele: list[str]) -> list[str]:
    """Programele de pe placă care contează ca sarcini grele (după nume, de ex. „python”)."""
    gasite = []
    for proces in placa.get("procese") or []:
        nume = PureWindowsPath(str(proces.get("nume", ""))).name.lower()
        if any(n.lower() in nume for n in nume_grele):
            gasite.append(f"{nume} ({proces.get('pid', '?')})")
    return gasite


def ore_placa_azi(fise: list[dict[str, Any]], azi: date) -> float:
    """Câte ore au durat experimentele începute azi (după ceasul laptopului), din jurnalul Kronos."""
    secunde = 0.0
    for fisa in fise:
        try:
            inceput = datetime.fromisoformat(str(fisa.get("inceput")))
        except ValueError:
            continue
        local = inceput.astimezone().date() if inceput.tzinfo else inceput.date()
        durata = fisa.get("durata_totala_secunde")
        if local == azi and isinstance(durata, (int, float)) and not isinstance(durata, bool):
            secunde += durata
    return secunde / 3600


def nivel(observat: Any, config: dict[str, Any]) -> tuple[str, str]:
    """(nivelul, de ce) din ce s-a observat: ora, omul, placa. Motivul e o propoziție în română, pentru jurnal."""
    g = config["guvernator"]
    ora = observat.timp.time()
    if in_fereastra(ora, g["fereastra_invatare"]):
        nivel_ferestrei, fereastra = INVATARE, f"e fereastra de învățare ({text_fereastra(g['fereastra_invatare'])})"
    elif in_fereastra(ora, g["fereastra_intretinere"]):
        nivel_ferestrei, fereastra = INTRETINERE, (f"e fereastra de întreținere "
                                                   f"({text_fereastra(g['fereastra_intretinere'])})")
    else:
        return REPAUS, f"ora {ora:%H:%M} e în afara ferestrelor de lucru: doar observ"

    om = observat.om
    if om.get("stare") == "ok":
        minute = float(om["minute_de_la_ultima_atingere"])
        if minute < g["minute_fara_om"]:
            return REPAUS, (f"omul folosește laptopul (a atins tastatura sau mouse-ul acum {ro(minute)} min, sub pragul "
                            f"de {ro(g['minute_fara_om'])} min): doar observ")
        despre_om = f"omul n-a mai atins laptopul de {ro(minute)} min"
    else:
        despre_om = "nu pot vedea dacă omul folosește laptopul"

    ore_azi = ore_placa_azi(getattr(observat, "fise", []), observat.timp.date())
    if ore_azi >= g["buget_ore_placa_pe_zi"]:
        return REPAUS, (f"bugetul de azi pe placă e consumat ({ro(ore_azi, 1)} ore din {ro(g['buget_ore_placa_pe_zi'])}): "
                        f"nu mai pornesc nimic până mâine, doar observ")
    placa = observat.placa
    if placa.get("stare") != "ok":
        return REPAUS, f"nu pot citi placa video ({placa.get('eroare', 'motiv necunoscut')}): nu pornesc nimic pe ea"
    ocupata = procese_grele(placa, g["procese_grele"])
    if ocupata:
        return REPAUS, (f"placa e ocupată de altă sarcină ({', '.join(ocupata)}): o singură sarcină grea odată, "
                        f"doar observ")
    libera = placa["memorie_libera_mb"]
    if libera < g["memorie_video_libera_min_mb"]:
        return REPAUS, (f"placa are doar {ro(libera)} MB liberi (trebuie cel puțin "
                        f"{ro(g['memorie_video_libera_min_mb'])}): e ocupată, doar observ")
    motiv = (f"{fereastra}, placa e liberă ({ro(libera)} MB liberi, {ro(placa['temperatura'])} °C), {despre_om}; azi "
             f"{ro(ore_azi, 1)} ore pe placă din {ro(g['buget_ore_placa_pe_zi'])}")
    if placa["temperatura"] > g["temperatura_max"]:
        mai_jos = coboara(nivel_ferestrei)
        return mai_jos, (f"{motiv}; dar placa are {ro(placa['temperatura'])} °C, peste {ro(g['temperatura_max'])} °C: "
                         f"cobor la {mai_jos}")
    return nivel_ferestrei, motiv
