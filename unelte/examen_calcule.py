"""Examenul de calcule (S120, C-128 A, 16 nov 2026): 200 de întrebări de calcul simplu FĂRĂ text alături, în forma
filei Chat („Întrebare: …⏎Răspuns:”), notate automat. Scris ÎNAINTE de datele de antrenare cu calcule.

    python unelte/examen_calcule.py construieste            → docs/conversatie/examen_calcule.json (o singură dată)
    python unelte/examen_calcule.py model --experiment 651 --iesire lucru/conversatie_chat2/examen_calcule_651.json
                                                              [--dispozitiv cuda]

Examenul (`random.Random(128)`): adunare/scădere până la 1.000 (40 + 40), înmulțire până la 12 × 12 (70), împărțire
exactă cu rezultatul ≤ 100 (50). 40 % din întrebări (2 din 5, pe fiecare operație) au formulări care NU apar în
generator (`unelte/conversatie_chat.py`, FORMULARI_CALCULE) — verificat automat pe forma fără numere. Perechile de
numere (a, b, operația) din examen sunt interzise în generator.

Notarea: corect = rezultatul exact apare ca număr întreg în răspuns (cu/fără punct de mii) ȘI niciun alt număr diferit
nu e dat ca rezultat: toate numerele din răspuns sunt dintre {a, b, rezultatul} (numerele din întrebare au voie, ca în
„3 × 7 = 21.”), iar numărul de după fiecare „=” e rezultatul. Un număr cu virgulă („2,5”) e un alt număr → greșit.

Răspunsul modelului: ca fila Chat (`model.completeaza`, fără întâmplare, tăiat la primul rând nou sau la
<|endoftext|>), exact ca `unelte/examen_chat.py`. Refuză să scrie peste un fișier care există.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

EXAMEN = "docs/conversatie/examen_calcule.json"
SAMANTA = 128
COTE = {"adunare": 40, "scadere": 40, "inmultire": 70, "impartire": 50}
# Formulările NOI (nu sunt în generator): cel puțin 4 pe operație.
FORMULARI_NOI: dict[str, list[str]] = {
    "adunare": ["Calculează {a} + {b}.", "Cât dă {a} adunat cu {b}?", "Spune-mi suma lui {a} și {b}.",
                "Cât fac {a} și cu {b}?", "Dacă am {a} mere și mai primesc {b}, câte mere am?"],
    "scadere": ["Calculează {a} - {b}.", "Cât rămâne dacă din {a} scad {b}?", "Cât dă {a} fără {b}?",
                "Spune-mi cât e {a} scăzut cu {b}.", "Am {a} lei și cheltui {b}. Câți lei îmi rămân?"],
    "inmultire": ["Calculează {a} × {b}.", "Cât dă {a} înmulțit cu {b}?", "Spune-mi produsul lui {a} și {b}.",
                  "Cât înseamnă {a} luat de {b} ori?", "Dacă o cutie are {a} creioane, câte creioane sunt în {b} cutii?"],
    "impartire": ["Calculează {a} : {b}.", "Cât dă {a} împărțit la {b}?", "Spune-mi câtul dintre {a} și {b}.",
                  "Cât iese dacă împart {a} la {b}?", "Dacă împart {a} bomboane la {b} copii, câte primește fiecare?"],
}


def taie(text: str) -> str:
    """Ca în fila Chat: până la primul rând nou sau la <|endoftext|>."""
    return text.split("<|endoftext|>")[0].strip().split("\n")[0].strip()


_NUMAR = re.compile(r"(?<![\d.,])(\d{1,3}(?:\.\d{3})+|\d+)(,\d+)?(?![\d])")


def numere_din(raspuns: str) -> list[int | float]:
    """Numerele din răspuns: „1.000” / „1000” → 1000; „2,5” → 2.5 (alt număr, nu întreg)."""
    numere: list[int | float] = []
    for m in _NUMAR.finditer(raspuns):
        n = int(m.group(1).replace(".", ""))
        numere.append(float(f"{n}.{m.group(2)[1:]}") if m.group(2) else n)
    return numere


def corect(p: dict[str, Any], raspuns: str) -> bool:
    r, voie = p["rezultat"], {p["a"], p["b"], p["rezultat"]}
    numere = numere_din(raspuns)
    if r not in numere or any(n not in voie for n in numere):
        return False
    for bucata in raspuns.split("=")[1:]:
        dupa = numere_din(bucata)
        if not dupa or dupa[0] != r:
            return False
    return True


def noteaza(examen: dict[str, Any], raspunsuri: dict[str, str]) -> dict[str, Any]:
    pe_op: dict[str, list[int]] = {}
    pe_formulare: dict[str, list[int]] = {}
    for p in examen["perechi"]:
        ok = corect(p, raspunsuri.get(p["id"], ""))
        for d, k in ((pe_op, p["operatie"]), (pe_formulare, p["formulare"])):
            d.setdefault(k, [0, 0])
            d[k][1] += 1
            d[k][0] += ok
    total = sum(v[0] for v in pe_op.values())
    return {"total": total, "total_din": len(examen["perechi"]),
            "pe_operatie": {k: f"{v[0]}/{v[1]}" for k, v in pe_op.items()},
            "pe_formulare": {k: f"{v[0]}/{v[1]}" for k, v in pe_formulare.items()},
            "nu_scrie_in_text": sum(1 for p in examen["perechi"] if "nu scrie" in raspunsuri.get(p["id"], "").lower()),
            "fara_niciun_numar": sum(1 for p in examen["perechi"] if not numere_din(raspunsuri.get(p["id"], "")))}


# --- construirea -----------------------------------------------------------------------------------------------------
def construieste(rng: random.Random) -> list[dict[str, Any]]:
    from unelte.conversatie_chat import FORMULARI_CALCULE, numere_calcul, rezultat

    perechi: list[dict[str, Any]] = []
    for op, n in COTE.items():
        vazute: set[tuple[int, int]] = set()
        k = 0
        while len(vazute) < n:
            a, b = numere_calcul(op, rng, k)
            k += 1
            if (a, b) in vazute:
                continue
            vazute.add((a, b))
            i = len(vazute) - 1
            noua = i % 5 < 2
            q = rng.choice(FORMULARI_NOI[op] if noua else FORMULARI_CALCULE[op]).format(a=a, b=b)
            q = q[0].upper() + q[1:]
            perechi.append({"operatie": op, "a": a, "b": b, "rezultat": rezultat(op, a, b), "intrebare": q,
                            "formulare": "noua" if noua else "generator"})
    for i, p in enumerate(perechi):
        p["id"] = f"calc_{i:03d}"
    return perechi


def verificari(perechi: list[dict[str, Any]]) -> dict[str, Any]:
    from unelte.conversatie_chat import FORMULARI_CALCULE, formulare_fara_numere

    gen = {formulare_fara_numere(f.format(a=3, b=7)) for fs in FORMULARI_CALCULE.values() for f in fs}
    noi = [p for p in perechi if p["formulare"] == "noua"]
    return {"pe_operatie": dict(Counter(p["operatie"] for p in perechi)),
            "formulari_noi": len(noi), "procent_formulari_noi": round(100 * len(noi) / len(perechi), 1),
            "noi_care_apar_totusi_in_generator": [p["id"] for p in noi
                                                  if formulare_fara_numere(p["intrebare"]) in gen],
            "perechi_de_numere_repetate": len(perechi) - len({(p["a"], p["b"], p["operatie"]) for p in perechi}),
            "rezultate_gresite": [p["id"] for p in perechi if not corect(p, f"{p['rezultat']}.")]}


def interzise(examen: dict[str, Any]) -> set[tuple[int, int, str]]:
    """Perechile de numere ale examenului (a, b, operația), interzise în generator."""
    return {(p["a"], p["b"], p["operatie"]) for p in examen["perechi"]}


# --------------------------------------------------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Examenul de calcule (S120): fără text alături, notare automată.")
    sub = parser.add_subparsers(dest="comanda", required=True)
    c = sub.add_parser("construieste")
    c.add_argument("--iesire", default=str(RADACINA / EXAMEN))
    m = sub.add_parser("model")
    m.add_argument("--experiment", type=int, required=True)
    m.add_argument("--iesire", required=True)
    m.add_argument("--examen", default=EXAMEN)
    m.add_argument("--simboluri", type=int, default=80)
    m.add_argument("--dispozitiv", default="cpu")
    m.add_argument("--director-lucru", default="lucru")
    a = parser.parse_args(argv)
    iesire = Path(a.iesire)
    if iesire.exists():
        raise SystemExit(f"{iesire} există deja; nu scriu peste.")

    if a.comanda == "construieste":
        perechi = construieste(random.Random(SAMANTA))
        v = verificari(perechi)
        if (v["noi_care_apar_totusi_in_generator"] or v["perechi_de_numere_repetate"] or v["rezultate_gresite"]
                or v["procent_formulari_noi"] < 30 or len(perechi) != 200):
            raise SystemExit(f"verificarea examenului a picat: {v}")
        iesire.parent.mkdir(parents=True, exist_ok=True)
        iesire.write_bytes(json.dumps({
            "nota": "S120 (C-128 A, 16 nov 2026): examenul de calcule ținut deoparte, întrebări FĂRĂ text alături, în "
                    "forma filei Chat. Corect = rezultatul exact apare ca număr întreg în răspuns (cu/fără punct de "
                    "mii) și niciun alt număr diferit nu e dat ca rezultat (toate numerele din răspuns sunt dintre a, b "
                    "și rezultat; după fiecare „=” vine rezultatul). Perechile (a, b, operația) sunt interzise în "
                    "generator. Notarea: unelte/examen_calcule.py.",
            "samanta": SAMANTA, "cote": COTE, "formulari_noi": FORMULARI_NOI, "verificari": v, "perechi": perechi,
        }, ensure_ascii=False, indent=1).encode("utf-8"))
        print(json.dumps({"scris": str(iesire), **v}, ensure_ascii=False))
        return 0

    examen = json.loads((RADACINA / a.examen).read_text(encoding="utf-8"))
    from kronos.jurnal import Jurnal
    from module.model_conversatie import intrebarea
    from unelte.modele_salvate import fisa_modelului, incarca_modelul

    t0 = time.time()
    model = incarca_modelul(fisa_modelului(Jurnal(Path(a.director_lucru)), a.experiment), a.dispozitiv)
    raspunsuri: dict[str, str] = {}
    for p in examen["perechi"]:
        raspunsuri[p["id"]] = taie(str(model.completeaza(intrebarea(p["intrebare"]), a.simboluri)))
    nota = noteaza(examen, raspunsuri)
    iesire.parent.mkdir(parents=True, exist_ok=True)
    iesire.write_bytes(json.dumps({
        "experiment": a.experiment, "examen": a.examen, "dispozitiv": a.dispozitiv, "simboluri": a.simboluri,
        "nota": nota, "secunde": round(time.time() - t0),
        "raspunsuri": [{"id": p["id"], "operatie": p["operatie"], "formulare": p["formulare"],
                        "intrebare": p["intrebare"], "rezultat": p["rezultat"], "raspuns": raspunsuri[p["id"]],
                        "corect": corect(p, raspunsuri[p["id"]])} for p in examen["perechi"]],
    }, ensure_ascii=False, indent=1).encode("utf-8"))
    print(json.dumps({"experiment": a.experiment, "total": nota["total"], "pe_operatie": nota["pe_operatie"],
                      "secunde": round(time.time() - t0)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
