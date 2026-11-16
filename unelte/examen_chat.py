"""Examenul de chat (S116, C-126 A1, 16 nov 2026): întrebări FĂRĂ text alături, în forma filei Chat a interfeței
(„Întrebare: …⏎Răspuns:”), notate automat, fără profesor.

Examenul: docs/conversatie/examen_chat.json (făcut de `unelte/conversatie_chat.py examen`, ținut deoparte).
- (a) 150 fapte: corect = cheia apare în răspuns (cuvinte întregi, după normalizare: fără diacritice, fără majuscule,
  fără punctuație, numerele cu/fără punct de mii — `unelte.romana_raspunsuri.contine`);
- (b) 50 sociale: corect = răspunsul conține o expresie din `cuvinte_cheie[categorie]` (scrise în examen înainte de
  orice rulare a modelului);
- (c) informativ: răspunsurile întocmai, fără notă.
Scorul = (a) + (b), din 200.

    python unelte/examen_chat.py --experiment 651 --iesire lucru/conversatie_chat/examen_651.json [--dispozitiv cuda]

Răspunsul: fără întâmplare (`model.completeaza`), cel mult --simboluri bucăți, tăiat la primul rând nou sau la
<|endoftext|> — exact ca fila Chat (module/interfata/creiere.py, S114). Refuză să scrie peste un fișier care există.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

EXAMEN = "docs/conversatie/examen_chat.json"


def taie(text: str) -> str:
    """Ca în fila Chat: până la primul rând nou sau la <|endoftext|>."""
    return text.split("<|endoftext|>")[0].strip().split("\n")[0].strip()


def corect(p: dict[str, Any], raspuns: str, cuvinte_cheie: dict[str, list[str]]) -> bool | None:
    from unelte.romana_raspunsuri import contine

    if p["parte"] == "a":
        return contine(raspuns, p["cheie"])
    if p["parte"] == "b":
        return any(contine(raspuns, c) for c in cuvinte_cheie[p["categorie"]])
    return None


def noteaza(examen: dict[str, Any], raspunsuri: dict[str, str]) -> dict[str, Any]:
    """Nota pe părți și pe categorii; `raspunsuri` = id → răspunsul tăiat al modelului."""
    cuvinte = examen["cuvinte_cheie"]
    a = b = 0
    pe_cat: dict[str, list[int]] = {}
    for p in examen["perechi"]:
        r = corect(p, raspunsuri.get(p["id"], ""), cuvinte)
        if r is None:
            continue
        cheie = f"{p['parte']}_{p['categorie']}"
        pe_cat.setdefault(cheie, [0, 0])
        pe_cat[cheie][1] += 1
        if r:
            pe_cat[cheie][0] += 1
            a += p["parte"] == "a"
            b += p["parte"] == "b"
    n_a = sum(p["parte"] == "a" for p in examen["perechi"])
    n_b = sum(p["parte"] == "b" for p in examen["perechi"])
    return {"a": a, "a_din": n_a, "b": b, "b_din": n_b, "total": a + b, "total_din": n_a + n_b,
            "pe_categorie": {k: f"{v[0]}/{v[1]}" for k, v in sorted(pe_cat.items())},
            "nu_scrie_pe_nedrept": sum(1 for p in examen["perechi"] if p["parte"] in ("a", "b")
                                       and "nu scrie" in raspunsuri.get(p["id"], "").lower())}


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Examenul de chat: întrebări fără text alături, notare automată.")
    parser.add_argument("--experiment", type=int, required=True)
    parser.add_argument("--iesire", required=True)
    parser.add_argument("--examen", default=EXAMEN)
    parser.add_argument("--simboluri", type=int, default=80)
    parser.add_argument("--dispozitiv", default="cpu")
    parser.add_argument("--director-lucru", default="lucru")
    a = parser.parse_args(argv)
    iesire = Path(a.iesire)
    if iesire.exists():
        raise SystemExit(f"{iesire} există deja; examenul nu se rulează a doua oară pe același fișier.")
    examen = json.loads((RADACINA / a.examen).read_text(encoding="utf-8"))

    from kronos.jurnal import Jurnal
    from module.model_conversatie import intrebarea
    from unelte.modele_salvate import fisa_modelului, incarca_modelul

    t0 = time.time()
    model = incarca_modelul(fisa_modelului(Jurnal(Path(a.director_lucru)), a.experiment), a.dispozitiv)
    raspunsuri: dict[str, str] = {}
    secunde: dict[str, float] = {}
    for p in examen["perechi"]:
        t = time.time()
        raspunsuri[p["id"]] = taie(str(model.completeaza(intrebarea(p["intrebare"]), a.simboluri)))
        secunde[p["id"]] = round(time.time() - t, 2)
    nota = noteaza(examen, raspunsuri)
    iesire.parent.mkdir(parents=True, exist_ok=True)
    iesire.write_bytes(json.dumps({
        "experiment": a.experiment, "examen": a.examen, "dispozitiv": a.dispozitiv, "simboluri": a.simboluri,
        "nota": nota, "secunde": round(time.time() - t0),
        "raspunsuri": [{"id": p["id"], "parte": p["parte"], "categorie": p["categorie"], "intrebare": p["intrebare"],
                        "raspuns": raspunsuri[p["id"]], "secunde": secunde[p["id"]],
                        "corect": corect(p, raspunsuri[p["id"]], examen["cuvinte_cheie"]),
                        **({"cheie": p["cheie"]} if "cheie" in p else {})} for p in examen["perechi"]],
    }, ensure_ascii=False, indent=1).encode("utf-8"))
    print(json.dumps({"experiment": a.experiment, **{k: nota[k] for k in ("a", "b", "total")},
                      "secunde": round(time.time() - t0)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
