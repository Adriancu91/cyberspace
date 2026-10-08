"""Școala de cod (Kronos Code Bootstrapping v0.1; specificația: docs/KRONOS_COD_plan.md).

Întrebarea: poate modelul Kronos de ~34 M de parametri, pornit din povești (#252), să dobândească o abilitate mică de
programare prin execuție, selecție și antrenare pe propriile reușite, fără să piardă ce știa?

Piesele, toate în afara lui kronos/ (nucleul rămâne neatins):
- sandbox.py: rularea unei încercări: proces separat, timeout, semantica REPL, cod interzis = „prins trișând”;
- examen_cod.py: sarcinile pe niveluri, cele patru seturi (văzut, nevăzut, adversarial, sacru), verificarea de formă;
- mediu.py: abecedarul, textul din fața modelului, încercarea din ce a scris modelul;
- elev.py: Kronos (rețeaua GPT a lui #252) la școală: generare cu temperatură, antrenare scurtă, salvare;
- paznic_cod.py: amprentele, placa (temperatură, alt proces pe ea), alimentarea, STOP.
Bucla e în unelte/scoala_cod.py, înghețul și rollback-ul în unelte/ingheata_cod.py, raportul în unelte/raport_cod.py.
Toate pragurile stau în config/scoala_cod.toml.

Sandbox-ul și examenul joacă rolul porturilor „rulare” și „examen” ale planului, dar nu sunt module Kronos cu MANIFEST:
școala nu rulează prin orchestrator (ca bucla uneltei de antrenare lungă), iar contractele porturilor cer alte
interfețe. Așa nu trebuie atins kronos/.
"""

# Scara (planul, secțiunea 5), în ordine. v0.2 adaugă trepte intermediare acolo unde s-a rupt lanțul în pilotul v0.1:
# 0a / 1a cu numere de o cifră, 0b / 1b cu numere de două cifre (0b are și cuvintele nivelului 0). v0.3: 0n (numerele 0–99,
# nivelul 0 al planului fără cuvinte), apoi 0w (cuvintele).
NIVELURI = ("0", "0n", "0w", "0a", "0b", "1", "1a", "1b", "2A", "2B", "2C", "3A", "3B", "4", "4.5", "5", "5.5", "6", "7", "8")
PILOT = ("0", "1", "2A", "2B", "2C", "3A", "3B")                       # pilotul v0.1
PILOT_V02 = ("0a", "0b", "1a", "1b", "2A", "2B", "2C", "3A", "3B")     # pilotul v0.2
PILOT_V03 = ("0n", "0w", "1a", "1b", "2A", "2B", "2C", "3A", "3B")     # pilotul v0.3: 0n = nivelul 0 al planului (numerele 0–99)


def ordinea(nivel: str) -> int:
    """Locul nivelului pe scară (0 = primul)."""
    if nivel not in NIVELURI:
        raise ValueError(f"nivelul {nivel!r} nu e pe scara v0.1 ({', '.join(NIVELURI)})")
    return NIVELURI.index(nivel)
