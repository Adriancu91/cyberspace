"""Examenul de conversație (15 octombrie 2026): un model salvat răspunde la cele 300 de întrebări nevăzute din
date/conversatie/examen.json, iar profesorul îi notează fiecare răspuns 1–10, față de răspunsul de referință.

- Întrebarea se dă exact ca la antrenare: „Întrebare: …⏎Răspuns:”. Modelul scrie cel mult --simboluri bucăți, fără
  întâmplare (mereu bucata cea mai probabilă); răspunsul se taie la primul rând nou sau la <|endoftext|>.
- La întrebările „nu știu”: corect dacă răspunsul spune că nu știe („Nu știu…”, „I don't know…”).
- Scorurile: nota medie (toate întrebările), nota medie fără cele „nu știu”, „nu știu” corecte (din câte), și cât de des
  a spus „nu știu” la o întrebare care se știe.
Rezultatul: lucru/examen_conversatie/experiment_<N>_<data>.json (cu fiecare răspuns) și, doar numere, o fișă pe linia
„examen_conversatie” din jurnalul Kronos. Elevul se scoate de pe placă înainte să vină profesorul.

    python unelte/examen_conversatie.py --experiment 360 --doar-local
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from kronos.jurnal import Jurnal  # noqa: E402

SISTEM = "You are a strict but fair teacher who grades a student's short answers to simple questions."
_NOTA = re.compile(r"(?:GRADE|NOTA)\s*:\s*(\d+)", re.IGNORECASE)
_NU_STIU = re.compile(r"\b(nu stiu|nu sunt sigur|i don t know|i do not know|i m not sure)\b")


def taie(text: str) -> str:
    """Răspunsul până la primul rând nou sau la <|endoftext|>."""
    return text.split("<|endoftext|>")[0].strip().split("\n")[0].strip()


def spune_nu_stiu(raspuns: str) -> bool:
    from unelte.genereaza_conversatie import normalizat

    return bool(_NU_STIU.search(normalizat(raspuns)))


def mesaje_nota(intrebare: str, referinta: str, raspuns: str, limba: str) -> list[dict[str, str]]:
    return [{"role": "system", "content": SISTEM}, {"role": "user", "content": (
        f"Question ({'Romanian' if limba == 'ro' else 'English'}): {intrebare}\nReference answer: {referinta}\n"
        f"Student's answer: {raspuns or '(nothing)'}\n\n"
        "Grade the student's answer from 1 to 10: is it true, does it answer the question, is the language correct? "
        "It does not need to match the reference word for word. 10 = correct and clear. 5 = partly right. "
        "1 = wrong, off-topic or nonsense.\nAnswer in exactly one line:\nGRADE: <a whole number from 1 to 10>")}]


def scoruri(intrebari: list[dict[str, Any]]) -> dict[str, Any]:
    note = [p["nota_elev"] for p in intrebari if p.get("nota_elev") is not None]
    fara = [p["nota_elev"] for p in intrebari if p["fel"] != "nu_stiu" and p.get("nota_elev") is not None]
    nu_stiu = [p for p in intrebari if p["fel"] == "nu_stiu"]
    stiute = [p for p in intrebari if p["fel"] != "nu_stiu"]
    return {
        "intrebari": len(intrebari), "nota_medie": round(statistics.mean(note), 3) if note else None,
        "nota_medie_fara_nu_stiu": round(statistics.mean(fara), 3) if fara else None,
        "nu_stiu_intrebari": len(nu_stiu), "nu_stiu_corecte": sum(p["nu_stiu_corect"] for p in nu_stiu),
        "nu_stiu_fractie": round(sum(p["nu_stiu_corect"] for p in nu_stiu) / len(nu_stiu), 3) if nu_stiu else None,
        "nu_stiu_la_stiute": round(sum(spune_nu_stiu(p["raspuns_elev"]) for p in stiute) / len(stiute), 3) if stiute else None,
        "note_neciteite": sum(1 for p in intrebari if p.get("nota_elev") is None),
    }


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Examenul de conversație: 300 de întrebări nevăzute, notate de profesor.")
    parser.add_argument("--experiment", type=int, required=True)
    parser.add_argument("--examen", default="date/conversatie/examen.json")
    parser.add_argument("--simboluri", type=int, default=80, help="cel mult atâtea bucăți în răspuns")
    parser.add_argument("--cate", type=int, default=0, help="doar primele atâtea întrebări (repetiție)")
    parser.add_argument("--dispozitiv", default="")
    parser.add_argument("--doar-local", action="store_true")
    parser.add_argument("--director-lucru", default="lucru")
    args = parser.parse_args(argv)

    import torch

    from module.model_conversatie import intrebarea
    from module.profesor_qwen import ProfesorQwen
    from unelte.modele_salvate import fisa_modelului, incarca_modelul

    jurnal = Jurnal(Path(args.director_lucru))
    fisa = fisa_modelului(jurnal, args.experiment)
    intrebari = [dict(p) for p in json.loads(Path(args.examen).read_text(encoding="utf-8"))["perechi"]]
    intrebari = intrebari[: args.cate] if args.cate else intrebari
    model = incarca_modelul(fisa, args.dispozitiv)
    for p in intrebari:
        p["raspuns_elev"] = taie(model.completeaza(intrebarea(p["intrebare"]), args.simboluri))
        p["nu_stiu_corect"] = p["fel"] == "nu_stiu" and spune_nu_stiu(p["raspuns_elev"])
    del model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    profesor = ProfesorQwen(lot=16, doar_local=args.doar_local)
    raspunsuri = profesor.raspunde_mai_multe(
        [mesaje_nota(p["intrebare"], p["raspuns"], p["raspuns_elev"], p["limba"]) for p in intrebari], 12,
        cu_intamplare=False)
    for p, r in zip(intrebari, raspunsuri):
        m = _NOTA.search(r)
        p["nota_elev"] = min(10, max(1, int(m.group(1)))) if m else None
    profesor.elibereaza()
    s = scoruri(intrebari)
    dosar = Path(args.director_lucru) / "examen_conversatie"
    dosar.mkdir(parents=True, exist_ok=True)
    iesire = dosar / f"experiment_{fisa['id']}_{datetime.now():%Y%m%d_%H%M%S}.json"
    iesire.write_text(json.dumps({"experiment": fisa["id"], "linie": fisa["linie"], **s, "raspunsuri": intrebari},
                                 ensure_ascii=False, indent=1), encoding="utf-8")
    jurnal.adauga({"id": jurnal.urmatorul_id(), "linie": "examen_conversatie",
                   "inceput": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                   "propunere": {"descriere": f"examenul de conversație pe modelul experimentului #{fisa['id']} "
                                              f"(toate răspunsurile: {iesire.as_posix()})", "modificari": {}},
                   "module": {"elev": {"experiment": fisa["id"], "linie": fisa["linie"]}},
                   "decizie": "masurat", "scoruri": {k: v for k, v in s.items() if isinstance(v, (int, float))}})
    print(f"=== Examenul de conversație: modelul #{fisa['id']} (linia „{fisa['linie']}”) ===\n{json.dumps(s, ensure_ascii=False)}\n"
          f"Toate răspunsurile: {iesire}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
