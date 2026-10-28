"""S42, examenele (28 octombrie 2026; supraveghetor 28 oct 08:20 și 14:25, granițele 1 și 2; pre-înregistrarea
docs/preinregistrari/2026-10-28_E3_reteta_A2.md; pasul 5 din plan/coada.md).

O SINGURĂ rulare, în același proces, pe ultimul model al liniei „w2_e3_reteta_A2” (nou) și pe #438:
  (a) cele 100 S26 cu bucățile `rrf_reord` (judecătorul = modelul examinat, ca la S33) — DECIDE;
  (b) aceleași 100 cu bucățile S25 simple (nu decide);
  (c) noaptea 10 și S4 cu textul dat (ca la S27, `examene` din e1_intrebari_nascute.py) — DECIDE (paza „să nu uite”);
  (d) eșantionul 2048 al validării S29, ambele variante (ca la S35; nu decide).
Apoi (e) `unelte/examen_validari_ws.py` pe modelul nou și pe #459 (nu decide), după ce modelele de mai sus s-au eliberat.
Răspunsurile: fără întâmplare, cel mult 80 de simboluri; nota: verificatorul S16 (doar citit). Paznicul la 20 de întrebări.

    python -X utf8 unelte/e3_reteta_A.py      # O SINGURĂ DATĂ → lucru/e3/examen_s42.json (+ lucru/e3/s42/examene_<id>_*.json)

Nu atinge kronos/, examenul BPB, paznicul, jurnalul (doar examen_validari_ws adaugă, ca de obicei, rândul lui „măsurat”),
datele de examen, text_v3, lista S26, indexurile (doar citite), unelte/verificator_text.py, modelele.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from unelte import e3_citire_reord as cr  # noqa: E402
from unelte import e3_examen as ex  # noqa: E402
from unelte import e3_memorie as e3  # noqa: E402
from unelte import e3_reordonare as r  # noqa: E402
from unelte.verificator_text import verifica  # noqa: E402

LINIE = "w2_e3_reteta_A2"
BAZA = 438
ROMANA = 459
IESIRE = "examen_s42.json"
PAZNIC_LA = 20


def verdict(a_nou: int, a_baza: int, n10_nou: int, n10_baza: int, s4_nou: int, s4_baza: int) -> dict[str, Any]:
    """Pragurile pre-înregistrării (în întrebări corecte, aceeași rulare): Δ = (a) nou − (a) #438.
    CONFIRMAT dacă Δ ≥ +5 și noaptea 10 nou ≥ #438 − 2 și S4 nou ≥ #438 − 2; INFIRMAT dacă Δ ≤ +1; altfel NECLAR."""
    d = a_nou - a_baza
    if d <= 1:
        v = "INFIRMAT"
    elif d >= 5 and n10_nou >= n10_baza - 2 and s4_nou >= s4_baza - 2:
        v = "CONFIRMAT"
    else:
        v = "NECLAR"
    return {"verdict": v, "diferenta": d, "noaptea10_pierdere": n10_baza - n10_nou, "S4_pierdere": s4_baza - s4_nou}


def citeste(model: Any, intrebari: list[dict[str, Any]], con: Any, con_r: Any, varianta: str,
            liste: dict[str, set[str]], raspunde: Callable[[Any, str], str], paznic: Callable[[], None],
            eticheta: str, extra: tuple[str, ...] = ()) -> list[dict[str, Any]]:
    """Ca cmd_examen din e3_citire_reord.py: pe fiecare întrebare, bucățile ambelor variante (judecătorul = modelul
    examinat) și răspunsul modelului, notat cu verificatorul S16."""
    judecator = lambda intrebare, texte: r.scoruri_intrebare(model, intrebare, texte)  # noqa: E731
    rez = []
    for i, q in enumerate(intrebari):
        if i % PAZNIC_LA == 0:
            paznic()
        p = cr.pregateste(con, con_r, q, varianta, liste, judecator, model.tok)
        rand = {"intrebare": q["intrebare"], "raspuns": q["raspuns"], "tip": q.get("tip"),
                "secunde_cautare": p["secunde_cautare"], "secunde_judecator": p["secunde_judecator"],
                **{k: q[k] for k in extra if k in q}}
        for v in cr.VARIANTE:
            t0 = time.perf_counter()
            elev = raspunde(model, p["pe"][v]["prompt"])
            nota = verifica(q["raspuns"], elev)
            rand[v] = {**{k: x for k, x in p["pe"][v].items() if k != "prompt"}, "raspuns_elev": elev,
                       "corect": nota["corect"], "motiv": nota["motiv"], "secunde_raspuns": time.perf_counter() - t0}
        rez.append(rand)
        if (i + 1) % PAZNIC_LA == 0:
            print(f"{datetime.now():%H:%M:%S} {eticheta} {i + 1}/{len(intrebari)}: "
                  + ", ".join(f"{v} {sum(x[v]['corect'] for x in rez)}" for v in cr.VARIANTE), flush=True)
    return rez


def cmd_examen(lucru: Path, linie: str = LINIE, baza: int = BAZA,
               incarca: Callable[..., tuple[Any, dict[str, Any]]] | None = None,
               raspunde: Callable[[Any, str], str] | None = None,
               examene_text: Callable[..., dict[str, Any]] | None = None,
               paznic: Callable[[], None] | None = None, sha_examen: str = e3.SHA_EXAMEN_NOU) -> dict[str, Any]:
    from unelte import e1_intrebari_nascute as e1

    iesire = lucru / IESIRE
    if iesire.exists():
        raise SystemExit("examenul S42 s-a rulat deja (o singură rulare)")
    incarca = incarca or e1.modelul
    raspunde = raspunde or e1.raspunde
    paznic = paznic or e1.paznic_placa
    if examene_text is None:
        e1.LUCRU = lucru / "s42"  # examenele (c) într-un dosar nou, lângă celelalte fișiere E3 (nu suprascriu S27)
        examene_text = e1.examene
    start = time.time()
    cale_s26 = lucru / "examen_nou_4096.json"
    sha = hashlib.sha256(cale_s26.read_bytes()).hexdigest()
    if sha != sha_examen:
        raise SystemExit(f"lista S26 nu are amprenta așteptată ({sha})")
    s26 = json.loads(cale_s26.read_text(encoding="utf-8"))
    validare, sursa_validare = cr.intrebari_validare(lucru)
    s2048 = [q for q in validare if q["esantion"] == "s2048"]
    varianta = json.loads((lucru / "validare_s25.json").read_text(encoding="utf-8"))["aleasa"]
    liste = e3.incarca_liste(lucru)
    try:
        import torch
    except ImportError:
        torch = None  # type: ignore[assignment]
    con = sqlite3.connect(f"file:{(lucru / 'index.sqlite').as_posix()}?mode=ro", uri=True)
    con_r = sqlite3.connect(f"file:{(lucru / 'index_radacini.sqlite').as_posix()}?mode=ro", uri=True)

    modele: dict[str, Any] = {}
    for cine, (exp, lin) in (("nou", (None, linie)), ("baza", (baza, None))):
        if torch is not None and torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats()
        model, fisa = incarca(exp, lin)
        a = citeste(model, s26, con, con_r, varianta, liste, raspunde, paznic, f"#{fisa['id']} S26")
        d = citeste(model, s2048, con, con_r, varianta, liste, raspunde, paznic, f"#{fisa['id']} 2048",
                    extra=("esantion", "vazuta_de_438"))
        del model
        memorie = None
        if torch is not None and torch.cuda.is_available():
            memorie = round(torch.cuda.max_memory_allocated() / 2**20, 1)
            torch.cuda.empty_cache()
        c = examene_text(fisa["id"])
        reg = ex.regresia(c)
        modele[cine] = {"experiment": fisa["id"], "linie": fisa.get("linie"),
                        "a_b_s26": {v: cr.rezumat_varianta(a, v) for v in cr.VARIANTE},
                        "d_s2048": cr._parte(d), "c_regresia": reg, "memorie_placa_max_mb": memorie,
                        "raspunsuri": {"s26": a, "s2048": d}}
        m = modele[cine]
        print(f"#{fisa['id']}: (a) rrf_reord {m['a_b_s26']['rrf_reord']['total']['corecte']}/100, (b) s25 "
              f"{m['a_b_s26']['s25']['total']['corecte']}/100, (c) noaptea 10 {reg['noaptea10']}, S4 {reg['S4']}, "
              f"(d) 2048 {m['d_s2048']['procent']}", flush=True)
    con.close()
    con_r.close()

    nou, b = modele["nou"], modele["baza"]
    corecte = lambda m, v: m["a_b_s26"][v]["total"]["corecte"]  # noqa: E731
    info = {"sarcina": "S42", "preinregistrare": "docs/preinregistrari/2026-10-28_E3_reteta_A2.md",
            "sha256_s26": sha, "validare": sursa_validare, "varianta_s25": varianta, "linie": linie, "baza": baza,
            **verdict(corecte(nou, "rrf_reord"), corecte(b, "rrf_reord"),
                      nou["c_regresia"]["noaptea10"]["corecte"], b["c_regresia"]["noaptea10"]["corecte"],
                      nou["c_regresia"]["S4"]["corecte"], b["c_regresia"]["S4"]["corecte"]),
            "alaturi": {"s25_diferenta": corecte(nou, "s25") - corecte(b, "s25"),
                        "s2048_rrf_reord_diferenta_puncte": round(nou["d_s2048"]["procent"]["rrf_reord"]
                                                                  - b["d_s2048"]["procent"]["rrf_reord"], 2),
                        "s2048_s25_diferenta_puncte": round(nou["d_s2048"]["procent"]["s25"]
                                                            - b["d_s2048"]["procent"]["s25"], 2)},
            "modele": modele, "ram_maxim_mb": e3._ram_maxim_mb(), "secunde": round(time.time() - start, 1),
            "scris": datetime.now().isoformat(timespec="seconds")}
    e3._scrie_json(iesire, info)
    return info


def validari(linie: str = LINIE, romana: int = ROMANA) -> None:
    """(e) examen_validari_ws.py pe modelul nou și pe #459 (fiecare își scrie fișierul în lucru/examen_validari_ws/)."""
    from unelte import examen_validari_ws as vw

    for args in (["--linie", linie], ["--experiment", str(romana)]):
        vw.main(args)


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="S42: examenele cititorului E3 refăcut (o singură rulare).")
    parser.add_argument("--lucru", default=e3._relativ(e3.LUCRU))
    args = parser.parse_args(argv)
    info = cmd_examen(RADACINA / args.lucru)
    print(json.dumps({**info, "modele": {c: {k: v for k, v in m.items() if k != "raspunsuri"}
                                         for c, m in info["modele"].items()}}, ensure_ascii=False, indent=1))
    validari()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
