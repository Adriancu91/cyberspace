"""E3: bucățile tăiate pe propozițiile utile (S44, 29 octombrie 2026; aprobat de supraveghetor 28 oct 23:15, granițele 2
și 5; pre-înregistrarea docs/preinregistrari/2026-10-29_E3_bucati_taiate.md; pașii din plan/coada.md).

S42 (propunerea 2) a arătat unde se pierde: cu `rrf_reord` răspunsul e în primele 3 bucăți aduse la 83 din cele 100 S26,
dar în bucățile care încap în 512 − 64 de simboluri doar la 72. Aici din fiecare bucată se păstrează doar propozițiile
legate de întrebare, ca să încapă mai multe:
  taie(bucata, intrebare)  împarte bucata în propoziții (după `.`, `!`, `?` urmate de spațiu și la rând nou); scorul unei
                           propoziții = câte rădăcini (`radacina()` din e3_reordonare) ale întrebării conține, fără cuvintele
                           de legătură; păstrează, în ordinea inițială, prima propoziție și propozițiile cu scor ≥ 1; dacă
                           nicio propoziție n-are scor ≥ 1, bucata rămâne întreagă. Fără model, fără întâmplare.
  examen (placa, O SINGURĂ rulare) #438 pe validarea S29 (eșantioanele 2048 și 1024, ca la S35), ordinea `rrf_reord`
                           (judecătorul #438) în ambele brațe: (i) bucățile întregi, (ii) bucățile tăiate. Aceeași regulă:
                           primele 3 bucăți, câte încap în 448 de simboluri (numărate pe textul dat modelului, deci tăiat);
                           același prompt S27, aceeași notă (verificatorul S16).

    python -X utf8 unelte/e3_taiere.py examen --model 438    # O SINGURĂ DATĂ → lucru/e3/examen_s44.json

Decide Δ în puncte procentuale (tăiate − întregi) pe eșantionul 2048 fără întrebările văzute de #438: CONFIRMAT dacă
Δ ≥ +2,0, INFIRMAT dacă Δ < +0,5, altfel NECLAR. Nu atinge kronos/, examenul BPB, paznicul, jurnalul, datele de examen,
text_v3, lista S26, validare_s29.json și indexurile (doar citite), unelte/verificator_text.py, modelele.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from unelte import e3_citire_reord as c  # noqa: E402
from unelte import e3_memorie as e3  # noqa: E402
from unelte import e3_reordonare as r  # noqa: E402
from unelte.verificator_text import cuvinte, verifica  # noqa: E402

IESIRE_EXAMEN = "examen_s44.json"
BRATE = ("intregi", "taiate")
_PROPOZITII = re.compile(r"(?<=[.!?])\s+|\s*\n\s*")


def radacini_intrebare(intrebare: str) -> set[str]:
    """Rădăcinile cuvintelor din întrebare, fără cuvintele de legătură (dacă rămâne nimic: toate cuvintele)."""
    toate = [x for x in cuvinte(e3.curata(intrebare)) if any(ch.isalnum() for ch in x)]
    fara = [x for x in toate if x not in e3.CUVINTE_DE_INTREBARE] or toate
    return {r.radacina(x) for x in fara}


def propozitii(bucata: str) -> list[str]:
    return [p for p in (x.strip() for x in _PROPOZITII.split(bucata)) if p]


def scor(propozitie: str, radacini: set[str]) -> int:
    """Câte rădăcini ale întrebării apar în propoziție."""
    return len(radacini & {r.radacina(x) for x in cuvinte(e3.curata(propozitie))})


def taie(bucata: str, intrebare: str) -> str:
    """Prima propoziție plus propozițiile cu scor ≥ 1, în ordinea inițială; bucata întreagă dacă nicio propoziție nu se
    potrivește sau dacă nu se scoate nimic."""
    prop = propozitii(bucata)
    radacini = radacini_intrebare(intrebare)
    scoruri = [scor(p, radacini) for p in prop]
    if not any(s >= 1 for s in scoruri):
        return bucata
    pastrate = [p for i, (p, s) in enumerate(zip(prop, scoruri)) if i == 0 or s >= 1]
    return bucata if len(pastrate) == len(prop) else " ".join(pastrate)


# ---------------------------------------------------------------- examenul, o singură rulare

def pregateste(con: sqlite3.Connection, con_r: sqlite3.Connection, q: dict[str, Any], varianta: str,
               liste: dict[str, set[str]], judecator: Callable[[str, list[str]], list[tuple[float, int]]],
               tok: Any) -> dict[str, Any]:
    """Pentru o întrebare: ordinea `rrf_reord` (ca la S35), apoi primele 3 bucăți întregi și aceleași 3 tăiate; din
    fiecare braț, câte încap în 448 de simboluri și promptul."""
    from module.model_conversatie import intrebarea

    t0 = time.perf_counter()
    simpla, unite = r.cauta_rrf(con, con_r, q["intrebare"], varianta, liste)
    t1 = time.perf_counter()
    de_notat = {g["rowid"]: g["text"] for g in simpla[:r.CATE_REORDONATE] + unite[:r.CATE_REORDONATE]}
    ids = list(de_notat)
    scoruri = dict(zip(ids, judecator(q["intrebare"], [de_notat[x] for x in ids])))
    t2 = time.perf_counter()
    ordine = r.reordoneaza(unite, scoruri)
    aduse = ordine[:e3.K_E3]
    brate = {"intregi": aduse, "taiate": [{**b, "text": taie(b["text"], q["intrebare"])} for b in aduse]}
    pe = {}
    for v, bucati in brate.items():
        cate = e3.cate_incap(tok, q["intrebare"], bucati)
        date = bucati[:cate]
        prompt = intrebarea(q["intrebare"], e3.context_e3(date))
        pe[v] = {"loc": e3.primul_bun(ordine, q["raspuns"]), "bucati_date": cate,
                 "articole_date": [b["articol"] for b in date],
                 "raspuns_in_3_aduse": any(e3.bun(q["raspuns"], b["text"]) for b in bucati),
                 "raspuns_in_bucati_date": any(e3.bun(q["raspuns"], b["text"]) for b in date),
                 "caractere_date": sum(len(b["text"]) for b in date), "simboluri_prompt": len(tok.codifica(prompt)),
                 "prompt": prompt}
    pe["taiate"]["bucati_scurtate"] = sum(a["text"] != b["text"] for a, b in zip(brate["intregi"], brate["taiate"]))
    return {"pe": pe, "secunde_cautare": t1 - t0, "secunde_judecator": t2 - t1}


def _parte(rez: list[dict[str, Any]]) -> dict[str, Any]:
    """Pe o parte a validării: ambele brațe, procentele, reparate / stricate, câte bucăți încap în medie."""
    pe = {v: c.rezumat_varianta(rez, v) for v in BRATE}
    procent = {v: round(100 * pe[v]["total"]["corecte"] / len(rez), 2) if rez else 0.0 for v in BRATE}
    medie = {v: round(statistics.mean(x[v]["bucati_date"] for x in rez), 3) if rez else None for v in BRATE}
    return {"intrebari": len(rez), "brate": pe, "procent": procent,
            "diferenta_puncte": round(procent["taiate"] - procent["intregi"], 2), "bucati_date_medie": medie,
            "reparate": sum(1 for x in rez if x["taiate"]["corect"] and not x["intregi"]["corect"]),
            "stricate": sum(1 for x in rez if x["intregi"]["corect"] and not x["taiate"]["corect"]),
            "acelasi_prompt": sum(x["acelasi_prompt"] for x in rez)}


def cmd_examen(lucru: Path, model_exp: int, incarca: Callable[..., Any] | None = None,
               raspunde: Callable[[Any, str], str] | None = None, paznic: Callable[[], None] | None = None,
               judecator: Callable[[str, list[str]], list[tuple[float, int]]] | None = None) -> dict[str, Any]:
    from unelte import e1_intrebari_nascute as e1

    iesire = lucru / IESIRE_EXAMEN
    if iesire.exists():
        raise SystemExit("examenul S44 s-a rulat deja (o singură rulare)")
    intrebari, sursa = c.intrebari_validare(lucru)
    start = time.time()
    varianta = json.loads((lucru / "validare_s25.json").read_text(encoding="utf-8"))["aleasa"]
    liste = e3.incarca_liste(lucru)
    model, fisa = (incarca or e1.modelul)(model_exp)
    raspunde = raspunde or e1.raspunde
    paznic = paznic or e1.paznic_placa
    judecator = judecator or (lambda intrebare, texte: r.scoruri_intrebare(model, intrebare, texte))
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats()
    except ImportError:
        torch = None  # type: ignore[assignment]
    con = sqlite3.connect(f"file:{(lucru / 'index.sqlite').as_posix()}?mode=ro", uri=True)
    con_r = sqlite3.connect(f"file:{(lucru / 'index_radacini.sqlite').as_posix()}?mode=ro", uri=True)
    rez = []
    for i, q in enumerate(intrebari):
        if i % c.PAZNIC_LA_VALIDARE == 0:
            paznic()
        p = pregateste(con, con_r, q, varianta, liste, judecator, model.tok)
        rand = {"intrebare": q["intrebare"], "raspuns": q["raspuns"], "tip": q.get("tip"),
                **{k: q[k] for k in ("esantion", "vazuta_de_438")},
                "secunde_cautare": p["secunde_cautare"], "secunde_judecator": p["secunde_judecator"],
                "acelasi_prompt": p["pe"]["intregi"]["prompt"] == p["pe"]["taiate"]["prompt"]}
        for v in BRATE:
            t0 = time.perf_counter()
            elev = raspunde(model, p["pe"][v]["prompt"])
            nota = verifica(q["raspuns"], elev)
            rand[v] = {**{k: x for k, x in p["pe"][v].items() if k != "prompt"}, "raspuns_elev": elev,
                       "corect": nota["corect"], "motiv": nota["motiv"], "secunde_raspuns": time.perf_counter() - t0}
        rez.append(rand)
        if (i + 1) % c.PAZNIC_LA_VALIDARE == 0:
            print(f"{datetime.now():%H:%M:%S} {i + 1}/{len(intrebari)}: "
                  + ", ".join(f"{v} {sum(x[v]['corect'] for x in rez)}" for v in BRATE), flush=True)
    con.close()
    con_r.close()
    memorie = None
    if torch is not None and torch.cuda.is_available():
        memorie = round(torch.cuda.max_memory_allocated() / 2**20, 1)
    decide = [x for x in rez if x["esantion"] == "s2048" and not x["vazuta_de_438"]]
    parti = {"s2048_decide": _parte(decide),
             "s2048_toate": _parte([x for x in rez if x["esantion"] == "s2048"]),
             "s1024_toate": _parte([x for x in rez if x["esantion"] == "s1024"]),
             "s1024_nevazute": _parte([x for x in rez if x["esantion"] == "s1024" and not x["vazuta_de_438"]])}
    d = parti["s2048_decide"]["procent"]
    secunde = lambda cheie: {"median": round(statistics.median(x[cheie] for x in rez), 3),  # noqa: E731
                             "maxim": round(max(x[cheie] for x in rez), 3)} if rez else None
    info = {"set": "validare S29 (eșantioanele 2048 și 1024)", "sursa": sursa, "intrebari": len(rez),
            "vazute_de_438": {es: sum(x["vazuta_de_438"] for x in rez if x["esantion"] == es)
                              for es in ("s2048", "s1024")},
            "varianta_s25": varianta, "ordine": "rrf_reord", "model": fisa["id"], "model_linie": fisa.get("linie"),
            **c.verdict_validare(d["taiate"], d["intregi"]), "parti": parti,
            "secunde_cautare": secunde("secunde_cautare"), "secunde_judecator": secunde("secunde_judecator"),
            "memorie_placa_max_mb": memorie, "ram_maxim_mb": e3._ram_maxim_mb(),
            "secunde": round(time.time() - start, 1), "scris": datetime.now().isoformat(timespec="seconds"),
            "toate": rez}
    e3._scrie_json(iesire, info)
    return info


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="E3: bucățile tăiate pe propozițiile utile (S44).")
    parser.add_argument("--lucru", default=e3._relativ(e3.LUCRU))
    sub = parser.add_subparsers(dest="pas", required=True)
    x = sub.add_parser("examen")
    x.add_argument("--model", type=int, required=True)
    args = parser.parse_args(argv)
    info = {k: v for k, v in cmd_examen(RADACINA / args.lucru, args.model).items() if k != "toate"}
    print(json.dumps(info, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
