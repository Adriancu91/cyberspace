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
"""

from __future__ import annotations

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


def nivel(observat: Any, config: dict[str, Any]) -> tuple[str, str]:
    """(nivelul, de ce) din ce s-a observat: ora, omul, placa. Motivul e o propoziție în română, pentru jurnal."""
    g = config["guvernator"]
    ora = observat.timp.time()
    if in_fereastra(ora, g["fereastra_invatare"]):
        nivel_ferestrei, fereastra = INVATARE, f"e fereastra de noapte ({text_fereastra(g['fereastra_invatare'])})"
    elif in_fereastra(ora, g["fereastra_intretinere"]):
        nivel_ferestrei, fereastra = INTRETINERE, f"e fereastra de zi ({text_fereastra(g['fereastra_intretinere'])})"
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
    motiv = f"{fereastra}, placa e liberă ({ro(libera)} MB liberi, {ro(placa['temperatura'])} °C), {despre_om}"
    if placa["temperatura"] > g["temperatura_max"]:
        mai_jos = coboara(nivel_ferestrei)
        return mai_jos, (f"{motiv}; dar placa are {ro(placa['temperatura'])} °C, peste {ro(g['temperatura_max'])} °C: "
                         f"cobor la {mai_jos}")
    return nivel_ferestrei, motiv
