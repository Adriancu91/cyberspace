"""E3 cu antrenare, examenele (S27, 26 octombrie 2026, aprobat de Adrian 26 oct 16:10; pre-înregistrarea
docs/preinregistrari/2026-10-26_E3_memorie.md, pasul 5 din plan/coada.md).

O SINGURĂ rulare, pe ultimul model al liniei noi („w2_conv_e3_memorie”) și, în aceeași rulare, pe #415:
  (a) oficial: cele 100 de întrebări S26 (lucru/e3/examen_nou_4096.json, amprenta verificată). Sistemul primește doar
      întrebarea, caută în tot indexul (nicio bucată oprită) cu varianta aleasă la S25, ia primele 3 bucăți, câte încap
      după regula de la antrenare (`cate_incap`: întrebarea cu bucățile în 512 − 64 de simboluri), iar modelul răspunde;
  (b) în plus (umflate, nu decid): cele 160 de întrebări vechi (S15 b2/e, S4 a/b/d, noaptea 10 „text”), la fel;
  (c) regresia: noaptea 10 și S4 (și S15), CU textul dat, exact ca `examene` din unelte/e1_intrebari_nascute.py.
Răspunsurile: fără întâmplare, cel mult 80 de simboluri, tăiate la primul rând (`raspunde` din e1_intrebari_nascute.py);
nota: verificatorul S16 (unelte/verificator_text.py, doar citit). Căutarea se face o dată, pe procesor, pentru ambele modele.

    python -X utf8 unelte/e3_examen.py        # lucru/e3/examen_s27.json (+ examenele (c) în lucru/e3/examene_<id>_*.json)

Validările (d) se rulează separat: python unelte/examen_validari_ws.py --linie w2_conv_e3_memorie.
Nu atinge kronos/, examenul BPB, paznicul, jurnalul, indexul (doar citit), datele de examen, text_v3, lista S26.
"""

from __future__ import annotations

import argparse
import hashlib
import json
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
from unelte.verificator_text import verifica  # noqa: E402

LINIE = "w2_conv_e3_memorie"
BAZA = 415
IESIRE = "examen_s27.json"
PAZNIC_LA = 20  # la câte întrebări se uită paznicul la placă


def pregateste(con: Any, intrebari: list[dict[str, Any]], varianta: str, liste: dict[str, set[str]] | None,
               tok: Any) -> list[dict[str, Any]]:
    """Pentru fiecare întrebare: bucățile date modelului (primele 3 ale căutării, câte încap) și ce vede modelul."""
    from module.model_conversatie import intrebarea

    rez = []
    for q in intrebari:
        aduse = e3.bucati_e3(con, q["intrebare"], varianta, liste)
        cate = e3.cate_incap(tok, q["intrebare"], aduse)
        date = aduse[:cate]
        rez.append({**{k: q[k] for k in ("intrebare", "raspuns", "examen", "nr", "categorie", "tip", "grup") if k in q},
                    "aduse": len(aduse), "bucati_date": cate, "articole_date": [b["articol"] for b in date],
                    "raspuns_in_3_aduse": any(e3.bun(q["raspuns"], b["text"]) for b in aduse),
                    "raspuns_in_bucati_date": any(e3.bun(q["raspuns"], b["text"]) for b in date),
                    "prompt": intrebarea(q["intrebare"], e3.context_e3(date))})
    return rez


def raspunde_toate(model: Any, intrebari: list[dict[str, Any]], raspunde: Callable[[Any, str], str],
                   paznic: Callable[[], None] = lambda: None) -> list[dict[str, Any]]:
    """Răspunsul modelului la fiecare întrebare pregătită, notat cu verificatorul S16."""
    rez = []
    for i, q in enumerate(intrebari):
        if i % PAZNIC_LA == 0:
            paznic()
        elev = raspunde(model, q["prompt"])
        v = verifica(q["raspuns"], elev)
        rez.append({**{k: x for k, x in q.items() if k != "prompt"}, "raspuns_elev": elev, "corect": v["corect"],
                    "motiv": v["motiv"]})
    return rez


def rezumat(rez: list[dict[str, Any]], cheie: str | None = None) -> dict[str, Any]:
    """Câte corecte în total, pe cele cu răspunsul în bucățile date / fără și, cu `cheie`, pe grupuri."""
    def numar(parte: list[dict[str, Any]]) -> dict[str, int]:
        return {"intrebari": len(parte), "corecte": sum(r["corect"] for r in parte)}

    out = {"total": numar(rez),
           "cu_raspunsul_in_bucatile_date": numar([r for r in rez if r["raspuns_in_bucati_date"]]),
           "fara_raspunsul_in_bucatile_date": numar([r for r in rez if not r["raspuns_in_bucati_date"]])}
    if cheie:
        grupuri = Counter(str(r.get(cheie)) for r in rez)
        out["pe_" + cheie] = {g: numar([r for r in rez if str(r.get(cheie)) == g]) for g in grupuri}
    return out


def regresia(rez: dict[str, Any]) -> dict[str, Any]:
    """Din examenele (c): noaptea 10 = „text” + „Nu scrie” (fără conversația simplă), S4 = a+b+c+d, S15 = b2+e."""
    def suma(nume: str, grupe: tuple[str, ...]) -> dict[str, int]:
        return {"intrebari": sum(rez[nume]["intrebari"].get(g, 0) for g in grupe),
                "corecte": sum(rez[nume]["corecte"].get(g, 0) for g in grupe)}

    return {"noaptea10": suma("noaptea10", ("text", "nu_scrie")), "S4": suma("S4", ("a", "b", "c", "d")),
            "S15": suma("S15", ("b2", "e")),
            "pe_grupuri": {n: rez[n]["corecte"] for n in ("S15", "S4", "noaptea10")}}


def verdict(a_nou: int, n10_nou: int, n10_baza: int, s4_nou: int, s4_baza: int) -> str:
    """Pragurile pre-înregistrării (în întrebări corecte): CONFIRMAT = (a) ≥ 60 și noaptea 10 ≥ #415 − 2 și
    S4 ≥ #415 − 2; INFIRMAT = (a) ≤ 44; altfel NECLAR."""
    if a_nou <= 44:
        return "INFIRMAT"
    if a_nou >= 60 and n10_nou >= n10_baza - 2 and s4_nou >= s4_baza - 2:
        return "CONFIRMAT"
    return "NECLAR"


def cmd_examen(lucru: Path, tokenizer: Path, sha_examen_nou: str = e3.SHA_EXAMEN_NOU,
               examene: dict[str, str] = e3.EXAMENE, linie: str = LINIE, baza: int = BAZA,
               incarca: Callable[..., tuple[Any, dict[str, Any]]] | None = None,
               raspunde: Callable[[Any, str], str] | None = None,
               examene_text: Callable[..., dict[str, Any]] | None = None,
               paznic: Callable[[], None] | None = None) -> dict[str, Any]:
    from module.tokenizer_bpe import TokenizerBPE
    from unelte import e1_intrebari_nascute as e1

    iesire = lucru / IESIRE
    if iesire.exists():
        raise SystemExit("examenul S27 s-a rulat deja (o singură rulare)")
    incarca = incarca or e1.modelul
    raspunde = raspunde or e1.raspunde
    paznic = paznic or e1.paznic_placa
    if examene_text is None:
        e1.LUCRU = lucru  # examenele (c) se scriu lângă celelalte fișiere S27
        examene_text = e1.examene
    start = time.time()
    cale_s26 = lucru / "examen_nou_4096.json"
    sha = hashlib.sha256(cale_s26.read_bytes()).hexdigest()
    if sha != sha_examen_nou:
        raise SystemExit(f"lista S26 nu are amprenta așteptată ({sha})")
    s26 = json.loads(cale_s26.read_text(encoding="utf-8"))
    s26_loc = [r["loc"] for r in json.loads((lucru / "examen_nou_s26.json").read_text(encoding="utf-8"))["toate"]["aleasa"]]
    vechi = e3.intrebari_examen(examene)
    varianta = json.loads((lucru / "validare_s25.json").read_text(encoding="utf-8"))["aleasa"]
    tok = TokenizerBPE.incarca(tokenizer)
    con = e3.deschide(lucru / "index.sqlite")
    seturi = {"a_s26": pregateste(con, s26, varianta, e3.incarca_liste(lucru), tok),
              "b_vechi160": pregateste(con, vechi, varianta, e3.incarca_liste(lucru), tok)}
    con.close()
    for q, loc in zip(seturi["a_s26"], s26_loc):
        q["in_primele_3_la_s26"] = loc is not None and loc <= e3.K_E3
    pregatire = round(time.time() - start, 1)
    print(f"{datetime.now():%H:%M:%S} căutarea gata ({pregatire} s)", flush=True)

    modele: dict[str, Any] = {}
    for cine, (exp, lin) in (("nou", (None, linie)), ("baza", (baza, None))):
        model, fisa = incarca(exp, lin)
        rez = {nume: raspunde_toate(model, q, raspunde, paznic) for nume, q in seturi.items()}
        del model
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass
        a = rez["a_s26"]
        modele[cine] = {"experiment": fisa["id"], "linie": fisa.get("linie"),
                        "a_s26": {**rezumat(a, "tip"),
                                  "din_cele_72_la_s26": {"intrebari": sum(r["in_primele_3_la_s26"] for r in a),
                                                         "corecte": sum(r["corect"] for r in a if r["in_primele_3_la_s26"])},
                                  "din_cele_28_la_s26": {"intrebari": sum(not r["in_primele_3_la_s26"] for r in a),
                                                         "corecte": sum(r["corect"] for r in a
                                                                        if not r["in_primele_3_la_s26"])}},
                        "b_vechi160": rezumat(rez["b_vechi160"], "examen"),
                        "raspunsuri": rez}
        print(f"#{fisa['id']} (a) {modele[cine]['a_s26']['total']['corecte']}/100, (b) "
              f"{modele[cine]['b_vechi160']['total']['corecte']}/{len(rez['b_vechi160'])}", flush=True)
        c = examene_text(fisa["id"])
        modele[cine]["c_regresia"] = regresia(c)
        print(f"#{fisa['id']} (c) noaptea 10 {modele[cine]['c_regresia']['noaptea10']}, "
              f"S4 {modele[cine]['c_regresia']['S4']}", flush=True)

    nou, b = modele["nou"], modele["baza"]
    a = seturi["a_s26"]
    info = {"varianta": varianta, "sha256_s26": sha, "linie": linie, "baza": baza,
            "plafon": {"raspuns_in_3_aduse": sum(q["raspuns_in_3_aduse"] for q in a),
                       "raspuns_in_bucatile_date": sum(q["raspuns_in_bucati_date"] for q in a),
                       "in_primele_3_la_s26": sum(q["in_primele_3_la_s26"] for q in a),
                       "bucati_date": dict(Counter(q["bucati_date"] for q in a)),
                       "vechi160_raspuns_in_bucatile_date": sum(q["raspuns_in_bucati_date"] for q in seturi["b_vechi160"]),
                       "vechi160_bucati_date": dict(Counter(q["bucati_date"] for q in seturi["b_vechi160"]))},
            "modele": modele,
            "verdict": verdict(nou["a_s26"]["total"]["corecte"], nou["c_regresia"]["noaptea10"]["corecte"],
                               b["c_regresia"]["noaptea10"]["corecte"], nou["c_regresia"]["S4"]["corecte"],
                               b["c_regresia"]["S4"]["corecte"]),
            "secunde_cautare": pregatire, "secunde": round(time.time() - start, 1),
            "scris": datetime.now().isoformat(timespec="seconds")}
    e3._scrie_json(iesire, info)
    return info


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="E3 cu antrenare: examenele S27 (o singură rulare).")
    parser.add_argument("--lucru", default=e3._relativ(e3.LUCRU))
    args = parser.parse_args(argv)
    info = cmd_examen(RADACINA / args.lucru, RADACINA / e3.TOKENIZER)
    print(json.dumps({**info, "modele": {c: {k: v for k, v in m.items() if k != "raspunsuri"}
                                         for c, m in info["modele"].items()}}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
