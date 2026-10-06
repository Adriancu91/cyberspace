"""Examenul de fapte (Faza 3, pasul 2): separat de examenul oficial (val_bpb), pe care nu-l atinge.

Pentru fiecare din cele 50 de fapte ale profesorului (module/profesor_qwen.py), 3 propoziții cu un gol la capăt, unde
lipsește cuvântul-cheie al faptului (golul e la capăt, ca elevul să-l poată completa scriind de la stânga la dreapta):
    1. faptul însuși:       Birds have ___.
    2. spus de mama:        Mom said, "Birds have ___."
    3. învățat de Lily:     Lily learned that birds have ___.
Elevul completează fără întâmplare (cuvântul cel mai probabil, ModelGPT.completeaza). Răspunsul e corect dacă primul lui
cuvânt (după un „the/a/an”, dacă începe cu unul) e printre cele acceptate; majusculele nu contează, iar singularul și
pluralul se socotesc la fel („feather” = „feathers”). 150 de întrebări; scorul = câte răspunsuri sunt corecte, numărat
în două feluri: cu răspunsurile acceptate (unde un sinonim e la fel de adevărat, ex. „clean” la dinți) și doar cu
cuvântul din fapt.
Rezultatul: pe ecran, în lucru/examen_fapte/ (cu toate răspunsurile) și în jurnal (doar numere, linia „examen_fapte”).

    python unelte/examen_fapte.py --linie antrenare_lunga_3     # ultimul model salvat de pe linie
    python unelte/examen_fapte.py --experiment 226 --dispozitiv cpu    # pe procesor, cât placa video lucrează
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from kronos.jurnal import Jurnal  # noqa: E402
from module.profesor_qwen import SUBIECTE  # noqa: E402
from unelte.modele_salvate import fisa_modelului, incarca_modelul  # noqa: E402

# subiect → (începutul propoziției, până la gol; răspunsurile acceptate). Primul răspuns e cuvântul din fapt.
INTREBARI: dict[str, tuple[str, tuple[str, ...]]] = {
    "snow": ("Water freezes into", ("ice",)),
    "birds": ("Birds have", ("feathers",)),
    "the Sun": ("The Sun is a", ("star",)),
    "plants": ("Plants need water and sunlight to", ("grow",)),
    "the Moon": ("The Moon goes around the", ("earth",)),
    "bees": ("Bees make", ("honey",)),
    "fish": ("Fish breathe through their", ("gills",)),
    "rain": ("Rain falls from", ("clouds",)),
    "spiders": ("Spiders have eight", ("legs",)),
    "frogs": ("Frogs start their lives as", ("tadpoles",)),
    "butterflies": ("A caterpillar changes into a", ("butterfly",)),
    "cows": ("Cows give", ("milk",)),
    "teeth": ("Brushing your teeth helps keep them", ("healthy", "clean")),
    "rainbows": ("A rainbow can appear when sunlight shines through", ("raindrops", "rain")),
    "autumn": ("Many trees lose their leaves in", ("autumn", "fall")),
    "the sea": ("Sea water is", ("salty",)),
    "magnets": ("Magnets pull things made of", ("iron", "metal")),
    "the heart": ("The heart pumps", ("blood",)),
    "bats": ("Bats are mammals that can", ("fly",)),
    "penguins": ("Penguins are birds that cannot", ("fly",)),
    "volcanoes": ("Hot melted rock called", ("lava",)),
    "shadows": ("A shadow forms when something blocks the", ("light", "sun", "sunlight")),
    "boiling water": ("Water boils when it gets very", ("hot",)),
    "owls": ("Many owls hunt at", ("night",)),
    "camels": ("Camels can go a long time without drinking", ("water",)),
    "elephants": ("Elephants use their", ("trunks",)),
    "stars": ("Stars are very", ("far",)),
    "wind": ("Wind is moving", ("air",)),
    "ants": ("Ants live and work together in big groups called", ("colonies", "colony")),
    "seeds": ("A big tree can grow from a small", ("seed",)),
    "snakes": ("Snakes have no", ("legs",)),
    "whales": ("Whales breathe air through a", ("blowhole",)),
    "ice cream": ("Ice cream melts when it gets", ("warm", "hot")),
    "night": ("It gets dark at night because our side of the Earth turns away from the", ("sun",)),
    "sleep": ("Our bodies need sleep to stay", ("healthy",)),
    "bread": ("Bread is made from", ("flour", "wheat")),
    "chickens": ("Hens lay", ("eggs",)),
    "turtles": ("A turtle carries its", ("shell",)),
    "thunderstorms": ("We see lightning before we hear the", ("thunder",)),
    "mountains": ("At the top of a high mountain, it is usually", ("colder", "cold")),
    "dogs": ("Dogs have a very good sense of", ("smell",)),
    "cats": ("Cats can see well when there is little", ("light",)),
    "apples": ("Apples grow on", ("trees",)),
    "the Earth": ("The Earth goes around the", ("sun",)),
    "squirrels": ("Squirrels hide", ("nuts", "acorns")),
    "bears": ("Some bears sleep through most of the", ("winter",)),
    "carrots": ("Carrots grow under the", ("ground", "soil", "dirt")),
    "clouds": ("Clouds are made of tiny drops of", ("water",)),
    "sand": ("Sand is made of tiny pieces of", ("rock", "stone", "shells")),
    "washing hands": ("Washing your hands with soap helps wash away", ("germs",)),
}
CADRE = ("{p} ___.", 'Mom said, "{p} ___."', "Lily learned that {pm} ___.")
ARTICOLE = ("the", "a", "an")


def intrebarea(cadru: str, inceput: str) -> tuple[str, str]:
    """(propoziția cu gol, textul pe care îl primește elevul: tot ce e înainte de gol)."""
    propozitie = cadru.format(p=inceput, pm=inceput[0].lower() + inceput[1:])
    return propozitie, propozitie.split(" ___")[0]


def _singular(cuvant: str) -> str:
    return cuvant[:-1] if cuvant.endswith("s") and len(cuvant) > 3 else cuvant


def raspunsul(completare: str) -> str:
    """Primul cuvânt al completării, cu litere mici, după un „the/a/an” de la început (dacă e)."""
    cuvinte = re.findall(r"[A-Za-z]+", completare)
    if len(cuvinte) > 1 and cuvinte[0].lower() in ARTICOLE:
        cuvinte = cuvinte[1:]
    return cuvinte[0].lower() if cuvinte else ""


def e_corect(completare: str, acceptate: tuple[str, ...]) -> bool:
    raspuns = raspunsul(completare)
    return bool(raspuns) and any(_singular(raspuns) == _singular(a) for a in acceptate)


def examineaza(model: Any) -> list[dict[str, Any]]:
    """Cele 150 de întrebări (50 de fapte × 3 propoziții), cu completarea elevului și dacă e corectă."""
    max_simboluri = 4 if getattr(model, "tokenizer", "") == "bpe" else 16  # pe litere: un cuvânt are mai multe semne
    rezultate = []
    for subiect, fapt in SUBIECTE:
        inceput, acceptate = INTREBARI[subiect]
        for k, cadru in enumerate(CADRE, start=1):
            propozitie, text = intrebarea(cadru, inceput)
            completare = model.completeaza(text, max_simboluri)
            rezultate.append({"subiect": subiect, "fapt": fapt, "propozitie": k, "intrebare": propozitie,
                              "completare": completare, "raspuns": raspunsul(completare),
                              "acceptate": list(acceptate), "corect": e_corect(completare, acceptate),
                              "corect_cuvantul_din_fapt": e_corect(completare, acceptate[:1])})
    return rezultate


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Examenul de fapte: 50 de fapte × 3 propoziții cu un gol.")
    alegere = parser.add_mutually_exclusive_group(required=True)
    alegere.add_argument("--experiment", type=int, help="numărul experimentului cu modelul salvat")
    alegere.add_argument("--linie", help="ultimul model salvat de pe această linie de jurnal")
    parser.add_argument("--director-lucru", default="lucru")
    parser.add_argument("--dispozitiv", default="", help="ex. cpu: elevul pe procesor, cât placa video e ocupată")
    args = parser.parse_args(argv)
    jurnal = Jurnal(Path(args.director_lucru))
    fisa = fisa_modelului(jurnal, args.experiment, args.linie)
    rezultate = examineaza(incarca_modelul(fisa, args.dispozitiv))
    corecte = sum(r["corect"] for r in rezultate)
    corecte_strict = sum(r["corect_cuvantul_din_fapt"] for r in rezultate)
    pe_propozitie = {str(k): sum(r["corect"] for r in rezultate if r["propozitie"] == k) for k in (1, 2, 3)}
    fapte_stiute = sum(1 for s, _ in SUBIECTE if any(r["corect"] for r in rezultate if r["subiect"] == s))

    eticheta = datetime.now().strftime("%Y%m%d_%H%M%S")
    dosar = Path(args.director_lucru) / "examen_fapte"
    dosar.mkdir(parents=True, exist_ok=True)
    iesire = dosar / f"experiment_{fisa['id']}_{eticheta}.json"
    iesire.write_text(json.dumps({"experiment": fisa["id"], "linie": fisa["linie"], "corecte": corecte,
                                  "intrebari": len(rezultate), "rezultate": rezultate}, ensure_ascii=False, indent=1),
                      encoding="utf-8")
    jurnal.adauga({
        "id": jurnal.urmatorul_id(), "linie": "examen_fapte", "inceput": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "propunere": {"descriere": f"examenul de fapte pentru modelul experimentului #{fisa['id']} "
                                   f"(răspunsurile: {iesire.as_posix()})", "modificari": {}},
        "module": {"elev": {"experiment": fisa["id"], "linie": fisa["linie"]}}, "decizie": "masurat",
        "scoruri": {"corecte": corecte, "corecte_doar_cuvantul_din_fapt": corecte_strict, "intrebari": len(rezultate),
                    "fapte_cu_macar_un_raspuns_corect": fapte_stiute,
                    **{f"corecte_propozitia_{k}": v for k, v in pe_propozitie.items()}},
    })

    print(f"=== Examenul de fapte: modelul experimentului #{fisa['id']} (linia „{fisa['linie']}”) ===")
    print(f"Corecte: {corecte} din {len(rezultate)} ({corecte / len(rezultate):.0%}); pe propoziții: faptul însuși "
          f"{pe_propozitie['1']}, spus de mama {pe_propozitie['2']}, învățat de Lily {pe_propozitie['3']} (din 50 fiecare).")
    print(f"Doar cu cuvântul din fapt (fără sinonime): {corecte_strict} din {len(rezultate)} "
          f"({corecte_strict / len(rezultate):.0%}). Fapte cu măcar un răspuns corect: {fapte_stiute} din {len(SUBIECTE)}.")
    for r in [r for r in rezultate if r["corect"]][:10]:
        print(f"   corect: {r['intrebare']} → „{r['completare'].strip()}”")
    for r in [r for r in rezultate if not r["corect"] and r["propozitie"] == 1][:10]:
        print(f"   greșit: {r['intrebare']} → „{r['completare'].strip()}” (se aștepta: {r['acceptate'][0]})")
    print(f"Toate răspunsurile: {iesire}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
