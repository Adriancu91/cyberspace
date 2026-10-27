"""E3 citește cu căutarea nouă (S33, 27 octombrie 2026; aprobat de supraveghetor 27 oct 02:15, granițele 2 și 5;
pre-înregistrarea docs/preinregistrari/2026-10-27_E3_citire_reord.md; pașii din plan/coada.md).

S29 a arătat că `rrf_reord` (rădăcini + RRF + reordonarea cu judecătorul #438) pune răspunsul în primele 3 bucăți mai
des decât căutarea S25 simplă (83 față de 72 din cele 100 S26). Aici întrebarea e dacă #438, care citește bucățile,
răspunde corect mai des:
  amestec  (procesor, pasul 1): din validare_s29.json, câte întrebări de fiecare tip (definiție, născut, an, regizat,
           rest) au eșantioanele 1024 și 2048 și câștigul `rrf_reord` față de `s25` la k = 3 pe fiecare tip; alături,
           același tabel pe cele 100 S26 (din examen_s29.json, deja măsurat). Nu se alege nimic pe baza lui.
  examen   (placa, O SINGURĂ rulare): #438 pe cele 100 S26, (i) cu bucățile S25 simple (exact ca la S27), (ii) cu
           bucățile `rrf_reord` (judecătorul #438, ca la S29). Aceeași regulă ca la S27: primele 3 bucăți, câte încap
           în 512 − 64 de simboluri; răspunsul fără întâmplare, cel mult 80 de simboluri; nota: verificatorul S16.

    python -X utf8 unelte/e3_citire_reord.py amestec               # lucru/e3/amestec_s33.json
    python -X utf8 unelte/e3_citire_reord.py examen --model 438    # O SINGURĂ DATĂ → lucru/e3/examen_s33.json
    python -X utf8 unelte/e3_citire_reord.py examen --model 438 --set validare   # S35, O SINGURĂ DATĂ → examen_s35.json

S35 (27 oct 2026, supraveghetor 11:15, granița 2; pre-înregistrarea docs/preinregistrari/2026-10-27_E3_citire_validare.md):
`--set validare` face aceeași citire pe eșantioanele 2048 și 1024 din validare_s29.json (cele 1.000 de întrebări ale
validării S29). Întrebările văzute de #438 la antrenare (date_antrenare_s27.jsonl) se scot din măsura care decide; decide
Δ în puncte procentuale pe eșantionul 2048: CONFIRMAT dacă Δ ≥ +2,0, INFIRMAT dacă Δ < +0,5, altfel NECLAR.

Nu atinge kronos/, examenul BPB, paznicul, jurnalul, datele de examen, text_v3, lista S26, indexurile (doar citite),
unelte/verificator_text.py, modelele.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import statistics
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from unelte import e3_memorie as e3  # noqa: E402
from unelte import e3_reordonare as r  # noqa: E402
from unelte.verificator_text import verifica  # noqa: E402

TIPURI = ("definitie", "nascut", "an", "regizat")  # restul intră la „rest”
IESIRE_AMESTEC = "amestec_s33.json"
IESIRE_EXAMEN = "examen_s33.json"
IESIRE_EXAMEN_VALIDARE = "examen_s35.json"
DATE_438 = "date_antrenare_s27.jsonl"
VARIANTE = ("s25", "rrf_reord")
PAZNIC_LA = 20
PAZNIC_LA_VALIDARE = 50


def tip_grup(tip: str | None) -> str:
    return tip if tip in TIPURI else "rest"


# ---------------------------------------------------------------- pasul 1: amestecul de tipuri

def tabel_tipuri(rez: list[dict[str, Any]], baza: str = "s25", aleasa: str = "rrf_reord") -> dict[str, Any]:
    """Pe fiecare grup de tip: câte întrebări (și procentul din eșantion), bune la k = 3 cu `baza` și cu `aleasa`,
    câștigul în întrebări și în puncte procentuale (din grup)."""
    n = len(rez)
    out = {}
    for g in TIPURI + ("rest",):
        parte = [x for x in rez if tip_grup(x.get("tip")) == g]
        b = sum(1 for x in parte if (x["loc"][baza] or 99) <= 3)
        a = sum(1 for x in parte if (x["loc"][aleasa] or 99) <= 3)
        out[g] = {"intrebari": len(parte), "procent_din_esantion": round(100 * len(parte) / n, 1) if n else 0.0,
                  f"{baza}_k3": b, f"{aleasa}_k3": a, "castig": a - b,
                  "castig_puncte": round(100 * (a - b) / len(parte), 1) if parte else 0.0}
    return out


def cmd_amestec(lucru: Path) -> dict[str, Any]:
    val = json.loads((lucru / r.IESIRE_VALIDARE).read_text(encoding="utf-8"))["toate"]
    ex = json.loads((lucru / r.IESIRE_EXAMEN).read_text(encoding="utf-8"))["toate"]
    info = {"s1024": tabel_tipuri(val["s1024"]), "s2048": tabel_tipuri(val["s2048"]),
            "impreuna": tabel_tipuri(val["s1024"] + val["s2048"]), "s26_100": tabel_tipuri(ex),
            "nota": "k = 3, potrivirea S16; s26_100 vine din examen_s29.json (deja măsurat). Nu se alege nimic pe baza lui.",
            "scris": datetime.now().isoformat(timespec="seconds")}
    e3._scrie_json(lucru / IESIRE_AMESTEC, info)
    return info


# ---------------------------------------------------------------- pasul 3: examenul, o singură rulare

def pregateste(con: sqlite3.Connection, con_r: sqlite3.Connection, q: dict[str, Any], varianta: str,
               liste: dict[str, set[str]], judecator: Callable[[str, list[str]], list[tuple[float, int]]],
               tok: Any) -> dict[str, Any]:
    """Pentru o întrebare: bucățile date modelului cu fiecare variantă (primele 3, câte încap) și promptul."""
    from module.model_conversatie import intrebarea

    t0 = time.perf_counter()
    simpla, unite = r.cauta_rrf(con, con_r, q["intrebare"], varianta, liste)
    t1 = time.perf_counter()
    de_notat = {g["rowid"]: g["text"] for g in simpla[:r.CATE_REORDONATE] + unite[:r.CATE_REORDONATE]}
    ids = list(de_notat)
    scoruri = dict(zip(ids, judecator(q["intrebare"], [de_notat[x] for x in ids])))
    t2 = time.perf_counter()
    ordini = {"s25": simpla, "rrf_reord": r.reordoneaza(unite, scoruri)}
    pe = {}
    for v, o in ordini.items():
        aduse = o[:e3.K_E3]
        cate = e3.cate_incap(tok, q["intrebare"], aduse)
        date = aduse[:cate]
        pe[v] = {"loc": e3.primul_bun(o, q["raspuns"]), "bucati_date": cate,
                 "articole_date": [b["articol"] for b in date],
                 "raspuns_in_3_aduse": any(e3.bun(q["raspuns"], b["text"]) for b in aduse),
                 "raspuns_in_bucati_date": any(e3.bun(q["raspuns"], b["text"]) for b in date),
                 "prompt": intrebarea(q["intrebare"], e3.context_e3(date))}
    return {"pe": pe, "secunde_cautare": t1 - t0, "secunde_judecator": t2 - t1}


def numar(parte: list[dict[str, Any]], v: str) -> dict[str, int]:
    return {"intrebari": len(parte), "corecte": sum(x[v]["corect"] for x in parte)}


def rezumat_varianta(rez: list[dict[str, Any]], v: str) -> dict[str, Any]:
    return {"total": numar(rez, v),
            "cu_raspunsul_in_bucatile_date": numar([x for x in rez if x[v]["raspuns_in_bucati_date"]], v),
            "fara_raspunsul_in_bucatile_date": numar([x for x in rez if not x[v]["raspuns_in_bucati_date"]], v),
            "plafon_raspuns_in_bucatile_date": sum(x[v]["raspuns_in_bucati_date"] for x in rez),
            "raspuns_in_3_aduse": sum(x[v]["raspuns_in_3_aduse"] for x in rez),
            "bucati_date": dict(sorted(Counter(x[v]["bucati_date"] for x in rez).items())),
            "pe_tip": {g: numar([x for x in rez if tip_grup(x.get("tip")) == g], v) for g in TIPURI + ("rest",)},
            "secunde_raspuns": {"median": round(statistics.median(x[v]["secunde_raspuns"] for x in rez), 3),
                                "maxim": round(max(x[v]["secunde_raspuns"] for x in rez), 3)} if rez else None}


def verdict(corecte_reord: int, corecte_s25: int) -> dict[str, Any]:
    """Pragurile pre-înregistrării (în întrebări corecte, aceeași rulare): CONFIRMAT dacă rrf_reord are cel puțin 5
    mai mult decât S25 simplă; INFIRMAT dacă diferența e sub 2; între ele NECLAR."""
    d = corecte_reord - corecte_s25
    return {"verdict": "CONFIRMAT" if d >= 5 else "INFIRMAT" if d < 2 else "NECLAR", "diferenta": d}


def verdict_validare(procent_reord: float, procent_s25: float) -> dict[str, Any]:
    """Pragurile S35 (în puncte procentuale, aceeași rulare, eșantionul 2048 fără cele văzute de #438): CONFIRMAT dacă
    Δ ≥ +2,0; INFIRMAT dacă Δ < +0,5 (inclusiv negativ); între ele NECLAR."""
    d = round(procent_reord - procent_s25, 4)
    return {"verdict": "CONFIRMAT" if d >= 2.0 else "INFIRMAT" if d < 0.5 else "NECLAR", "diferenta_puncte": d}


def intrebari_validare(lucru: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Cele 1.000 de întrebări ale validării S29 (întâi 2048, apoi 1024), fiecare cu eșantionul ei, locurile din S29
    (pentru reper) și dacă a fost văzută de #438 la antrenare (aceeași întrebare, literă cu literă)."""
    cale = lucru / r.IESIRE_VALIDARE
    toate = json.loads(cale.read_text(encoding="utf-8"))["toate"]
    vazute = set()
    with open(lucru / DATE_438, encoding="utf-8") as f:
        for rand in f:
            vazute.add(json.loads(rand)["intrebare"])
    out = []
    for es in ("s2048", "s1024"):
        for q in toate[es]:
            out.append({"intrebare": q["intrebare"], "raspuns": q["raspuns"], "tip": q.get("tip"), "esantion": es,
                        "vazuta_de_438": q["intrebare"] in vazute, "loc_s29": q.get("loc", {})})
    return out, {"fisier": cale.name, "sha256": hashlib.sha256(cale.read_bytes()).hexdigest(),
                 "intrebari_438": len(vazute)}


def _parte(rez: list[dict[str, Any]]) -> dict[str, Any]:
    """Pe o parte a validării: ambele variante, procentele, reparate / stricate."""
    pe = {v: rezumat_varianta(rez, v) for v in VARIANTE}
    procent = {v: round(100 * pe[v]["total"]["corecte"] / len(rez), 2) if rez else 0.0 for v in VARIANTE}
    return {"intrebari": len(rez), "variante": pe, "procent": procent,
            "diferenta_puncte": round(procent["rrf_reord"] - procent["s25"], 2),
            "reparate": sum(1 for x in rez if x["rrf_reord"]["corect"] and not x["s25"]["corect"]),
            "stricate": sum(1 for x in rez if x["s25"]["corect"] and not x["rrf_reord"]["corect"]),
            "aceleasi_bucati": sum(x["s25"]["articole_date"] == x["rrf_reord"]["articole_date"] for x in rez)}


def _scrie_validare(iesire: Path, rez: list[dict[str, Any]], sursa: dict[str, Any], fisa: dict[str, Any],
                    varianta: str, memorie: float | None, start: float) -> dict[str, Any]:
    decide = [x for x in rez if x["esantion"] == "s2048" and not x["vazuta_de_438"]]
    parti = {"s2048_decide": _parte(decide),
             "s2048_toate": _parte([x for x in rez if x["esantion"] == "s2048"]),
             "s1024_toate": _parte([x for x in rez if x["esantion"] == "s1024"]),
             "s1024_nevazute": _parte([x for x in rez if x["esantion"] == "s1024" and not x["vazuta_de_438"]])}
    d = parti["s2048_decide"]["procent"]
    # reperul S29: același loc al primului răspuns bun în ordinea fiecărei variante (fără întâmplare, trebuie să fie toate)
    reper = {v: sum(x[v]["loc"] == x["loc_s29"].get(v) for x in rez) for v in VARIANTE}
    secunde = lambda cheie: {"median": round(statistics.median(x[cheie] for x in rez), 3),  # noqa: E731
                             "maxim": round(max(x[cheie] for x in rez), 3)} if rez else None
    info = {"set": "validare S29 (eșantioanele 2048 și 1024)", "sursa": sursa, "intrebari": len(rez),
            "vazute_de_438": {es: sum(x["vazuta_de_438"] for x in rez if x["esantion"] == es)
                              for es in ("s2048", "s1024")},
            "varianta_s25": varianta, "model": fisa["id"], "model_linie": fisa.get("linie"),
            **verdict_validare(d["rrf_reord"], d["s25"]), "parti": parti, "reper_s29_acelasi_loc": reper,
            "secunde_cautare": secunde("secunde_cautare"), "secunde_judecator": secunde("secunde_judecator"),
            "memorie_placa_max_mb": memorie, "ram_maxim_mb": e3._ram_maxim_mb(),
            "secunde": round(time.time() - start, 1), "scris": datetime.now().isoformat(timespec="seconds"),
            "toate": rez}
    e3._scrie_json(iesire, info)
    return info


def cmd_examen(lucru: Path, model_exp: int, incarca: Callable[..., Any] | None = None,
               raspunde: Callable[[Any, str], str] | None = None, paznic: Callable[[], None] | None = None,
               judecator: Callable[[str, list[str]], list[tuple[float, int]]] | None = None,
               sha_examen: str = e3.SHA_EXAMEN_NOU, set_: str = "s26") -> dict[str, Any]:
    from unelte import e1_intrebari_nascute as e1

    pe_validare = set_ == "validare"
    iesire = lucru / (IESIRE_EXAMEN_VALIDARE if pe_validare else IESIRE_EXAMEN)
    if iesire.exists():
        raise SystemExit(f"examenul {'S35' if pe_validare else 'S33'} s-a rulat deja (o singură rulare)")
    if pe_validare:
        intrebari, sursa = intrebari_validare(lucru)
        sha, paznic_la = sursa["sha256"], PAZNIC_LA_VALIDARE
    else:
        cale = lucru / "examen_nou_4096.json"
        sha, paznic_la = hashlib.sha256(cale.read_bytes()).hexdigest(), PAZNIC_LA
        if sha != sha_examen:
            raise SystemExit(f"lista S26 nu are amprenta așteptată ({sha})")
        intrebari = json.loads(cale.read_text(encoding="utf-8"))
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
        if i % paznic_la == 0:
            paznic()
        p = pregateste(con, con_r, q, varianta, liste, judecator, model.tok)
        rand = {"intrebare": q["intrebare"], "raspuns": q["raspuns"], "tip": q.get("tip"),
                "secunde_cautare": p["secunde_cautare"], "secunde_judecator": p["secunde_judecator"]}
        if pe_validare:
            rand.update({k: q[k] for k in ("esantion", "vazuta_de_438", "loc_s29")})
        for v in VARIANTE:
            t0 = time.perf_counter()
            elev = raspunde(model, p["pe"][v]["prompt"])
            nota = verifica(q["raspuns"], elev)
            rand[v] = {**{k: x for k, x in p["pe"][v].items() if k != "prompt"}, "raspuns_elev": elev,
                       "corect": nota["corect"], "motiv": nota["motiv"], "secunde_raspuns": time.perf_counter() - t0}
        rez.append(rand)
        if (i + 1) % paznic_la == 0:
            print(f"{datetime.now():%H:%M:%S} {i + 1}/{len(intrebari)}: "
                  + ", ".join(f"{v} {sum(x[v]['corect'] for x in rez)}" for v in VARIANTE), flush=True)
    con.close()
    con_r.close()
    memorie = None
    if torch is not None and torch.cuda.is_available():
        memorie = round(torch.cuda.max_memory_allocated() / 2**20, 1)
    if pe_validare:
        return _scrie_validare(iesire, rez, sursa, fisa, varianta, memorie, start)
    # reperul S27: aceleași bucăți la (i)? (articolele date, întrebare cu întrebare)
    reper = None
    cale27 = lucru / "examen_s27.json"
    if cale27.exists():
        a27 = json.loads(cale27.read_text(encoding="utf-8"))["modele"]["nou"]["raspunsuri"]["a_s26"]
        reper = {"corecte_s27": sum(x["corect"] for x in a27),
                 "aceleasi_bucati": sum(x["articole_date"] == y["s25"]["articole_date"] for x, y in zip(a27, rez)),
                 "acelasi_raspuns": sum(x["raspuns_elev"] == y["s25"]["raspuns_elev"] for x, y in zip(a27, rez))}
    pe = {v: rezumat_varianta(rez, v) for v in VARIANTE}
    schimbate = {"reparate": sum(1 for x in rez if x["rrf_reord"]["corect"] and not x["s25"]["corect"]),
                 "stricate": sum(1 for x in rez if x["s25"]["corect"] and not x["rrf_reord"]["corect"]),
                 "aceleasi_bucati": sum(x["s25"]["articole_date"] == x["rrf_reord"]["articole_date"] for x in rez)}
    secunde = lambda cheie: {"median": round(statistics.median(x[cheie] for x in rez), 3),  # noqa: E731
                             "maxim": round(max(x[cheie] for x in rez), 3)} if rez else None
    info = {"set": "examen_nou_4096 (cele 100 S26)", "sha256": sha, "intrebari": len(intrebari),
            "varianta_s25": varianta, "model": fisa["id"], "model_linie": fisa.get("linie"),
            "variante": pe, **verdict(pe["rrf_reord"]["total"]["corecte"], pe["s25"]["total"]["corecte"]),
            "schimbate": schimbate, "reper_s27": reper,
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
    parser = argparse.ArgumentParser(description="E3 citește cu căutarea nouă (S33).")
    parser.add_argument("--lucru", default=e3._relativ(e3.LUCRU))
    sub = parser.add_subparsers(dest="pas", required=True)
    sub.add_parser("amestec")
    x = sub.add_parser("examen")
    x.add_argument("--model", type=int, required=True)
    x.add_argument("--set", dest="set_", choices=("s26", "validare"), default="s26")
    args = parser.parse_args(argv)
    lucru = RADACINA / args.lucru
    if args.pas == "amestec":
        info = cmd_amestec(lucru)
    else:
        info = {k: v for k, v in cmd_examen(lucru, args.model, set_=args.set_).items() if k != "toate"}
    print(json.dumps(info, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
