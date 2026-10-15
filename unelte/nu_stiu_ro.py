"""Întrebările „nu știu” în română (15 octombrie 2026, cerute de Adrian): scrise de Claude Code din șabloane scurte,
nu de profesor. Răspunsul e mereu „Nu știu sigur.”. Fiecare întrebare e despre ceva ce nimeni nu poate ști sigur:
oameni obișnuiți cu nume inventate, ce se întâmplă acum sau azi, viitorul, cel care întreabă, amănunte prea mărunte.
Numele sunt alese ca să nu fie oameni cunoscuți. Formele sunt alese ca să nu ceară acorduri după gen.

    python unelte/nu_stiu_ro.py --cate 400
"""

from __future__ import annotations

import argparse
import itertools
import json
import random
import sys
from pathlib import Path

RADACINA = Path(__file__).resolve().parent.parent
IESIRE = "date/conversatie/nu_stiu_ro.jsonl"
RASPUNS = "Nu știu sigur."
NUME = ["Ionel Vasilescu", "Maria Dobrescu", "Andrei Tănase", "Elena Grigore", "Mihai Stoica", "Ana Bucur", "Vlad Ene",
        "Ioana Sima", "Radu Marin", "Cristina Lupu", "Sorin Dragomir", "Gabriela Toma", "Florin Neagu", "Simona Pătru",
        "Dan Bălan", "Irina Costache", "Paul Olteanu", "Diana Matei", "Tudor Iancu", "Alina Voicu"]
ORASE = ["Iași", "Cluj-Napoca", "Timișoara", "Brașov", "Constanța", "Craiova", "Galați", "Oradea", "Sibiu", "Suceava",
         "Bacău", "Pitești", "Arad", "Baia Mare", "Botoșani", "Focșani", "Târgu Mureș", "Ploiești", "Buzău", "Brăila"]
DESPRE_OM = ["Ce a mâncat {n} ieri la prânz?", "La ce oră s-a trezit {n} azi-dimineață?", "Câți ani are {n}?",
             "Ce carte citește acum {n}?", "Unde își petrece {n} vacanța anul acesta?",
             "Cum se numește câinele pe care îl are {n}?", "Ce culoare are mașina pe care o conduce {n}?",
             "Ce a visat {n} azi-noapte?", "Câți bani are {n} în portofel acum?", "Ce face {n} chiar în clipa asta?",
             "Cu cine a vorbit {n} la telefon ieri seară?", "Ce cadou a primit {n} de ziua de naștere?",
             "Ce mâncare preferă {n} dimineața?", "În ce zi s-a născut {n}?", "Pe ce stradă locuiește {n}?"]
DESPRE_ORAS = ["Ce temperatură este acum în {o}?", "Plouă acum în {o}?", "Cât costă azi un kilogram de mere la piața din {o}?",
               "Câte mașini sunt acum pe străzile din {o}?", "Va ninge în {o} pe 3 martie anul viitor?",
               "Cine a câștigat aseară meciul de fotbal din {o}?", "Câți oameni au intrat azi în gara din {o}?",
               "Câte păsări zboară acum deasupra orașului {o}?", "La ce oră se va opri mâine ploaia în {o}?",
               "Câte felii de pâine s-au vândut azi într-o brutărie din {o}?"]
SINGURE = ["Ce oră este acum?", "Ce zi a săptămânii este azi?", "Ce număr va ieși la loto sâmbăta viitoare?",
           "Cine va câștiga următorul campionat mondial de fotbal?", "Cum mă cheamă?", "Ce am în buzunar acum?",
           "Unde locuiesc eu?", "Ce am mâncat azi la micul dejun?", "Câți frați am?", "Ce culoare are bluza mea?",
           "Câte frunze are acum stejarul din curtea școlii mele?", "Câte fire de nisip sunt pe plaja de la Mamaia?",
           "Ce notă voi lua mâine la școală?", "Ce vreme va fi peste o lună, într-o zi de marți?",
           "Câte stele se văd în noaptea asta din curtea mea?", "Cine va suna primul la ușa mea mâine?",
           "Câți pași am făcut ieri?", "Ce film vor da la televizor peste trei săptămâni, la ora opt seara?",
           "Câte mere sunt acum în frigiderul meu?", "Ce gândește acum vecinul meu?"]


def intrebari(cate: int, samanta: int = 0) -> list[str]:
    toate = ([s.format(n=n) for s, n in itertools.product(DESPRE_OM, NUME)]
             + [s.format(o=o) for s, o in itertools.product(DESPRE_ORAS, ORASE)])
    random.Random(samanta).shuffle(toate)
    return SINGURE + toate[: max(0, cate - len(SINGURE))]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Întrebările „nu știu” în română, din șabloane.")
    parser.add_argument("--cate", type=int, default=400)
    args = parser.parse_args(argv)
    iesire = RADACINA / IESIRE
    iesire.parent.mkdir(parents=True, exist_ok=True)
    lista = intrebari(args.cate)
    with iesire.open("w", encoding="utf-8") as f:
        for i, q in enumerate(lista):
            f.write(json.dumps({"fel": "nu_stiu", "limba": "ro", "intrebare": q, "raspuns": RASPUNS,
                                "profesor": "Claude Code (șabloane)", "sursa": "scrise de Claude Code",
                                "grup": f"nu_stiu_ro_{i}"}, ensure_ascii=False) + "\n")
    print(f"{len(lista)} întrebări „nu știu” în {iesire}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
