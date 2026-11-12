"""Renotarea examenului de conversație (S107, 12 noiembrie 2026): refuzul cinstit „Nu scrie în text.” numărat corect.

La întrebările „nu știu” (fel == "nu_stiu"), unealta oficială `unelte/examen_conversatie.py` numără drept corect doar
„Nu știu…”. Modelele antrenate cu text alături refuză cinstit cu „Nu scrie în text.”, iar refuzul acela era numărat
greșit. Aici, la „nu_stiu”, corect = spune_nu_stiu(r) sau spune_nu_scrie(r) (funcțiile sunt importate din unealta
oficială, nu copiate). La celelalte feluri, nota și „corect”-ul rămân exact cele din fișier.

Doar citește fișierele de rezultate și scrie un JSON nou în lucru/examen_conversatie/renotat/. Nu schimbă fișierul de
intrare, unealta oficială sau jurnalul Kronos.

    python unelte/renoteaza_conversatie.py lucru/examen_conversatie/experiment_513_20261112_195256.json ...
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from unelte.examen_conversatie import REFUZURI, scoruri, spune_nu_scrie, spune_nu_stiu  # noqa: E402


def refuza(raspuns: str) -> bool:
    """Un refuz cinstit: „Nu știu…” sau „Nu scrie în text.”"""
    return spune_nu_stiu(raspuns) or spune_nu_scrie(raspuns)


def renoteaza(intrebari: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Întoarce (întrebările renotate — copie, intrarea rămâne neatinsă; scorurile)."""
    noi = copy.deepcopy(intrebari)
    vechi = sum(bool(p.get("nu_stiu_corect")) for p in intrebari if p["fel"] == "nu_stiu")
    for p in noi:
        if p["fel"] == "nu_stiu":
            p["nu_stiu_corect_vechi"] = bool(p.get("nu_stiu_corect"))
            p["nu_stiu_corect"] = refuza(p["raspuns_elev"])
    s = scoruri(noi)
    stiute = [p for p in noi if p["fel"] not in REFUZURI]
    s["nu_stiu_corecte_vechi"] = vechi
    s["nu_stiu_corecte_nou"] = sum(bool(p["nu_stiu_corect"]) for p in noi if p["fel"] == "nu_stiu")
    s["refuzuri_la_stiute"] = sum(refuza(p["raspuns_elev"]) for p in stiute)
    s["nu_scrie_la_stiute"] = sum(spune_nu_scrie(p["raspuns_elev"]) for p in stiute)
    s["stiute"] = len(stiute)
    return noi, s


def renoteaza_fisier(cale: Path, dosar_iesire: Path) -> tuple[Path, dict[str, Any]]:
    date = json.loads(cale.read_text(encoding="utf-8"))
    noi, s = renoteaza(date["raspunsuri"])
    dosar_iesire.mkdir(parents=True, exist_ok=True)
    iesire = dosar_iesire / f"renotat_{cale.stem}.json"
    iesire.write_text(json.dumps({"sursa": cale.as_posix(), "experiment": date.get("experiment"),
                                  "linie": date.get("linie"), **s, "raspunsuri": noi},
                                 ensure_ascii=False, indent=1), encoding="utf-8")
    return iesire, s


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Renotează examenul de conversație: „Nu scrie în text.” corect la „nu știu”.")
    parser.add_argument("fisiere", nargs="+")
    parser.add_argument("--iesire", default="lucru/examen_conversatie/renotat")
    args = parser.parse_args(argv)
    for f in args.fisiere:
        iesire, s = renoteaza_fisier(Path(f), Path(args.iesire))
        print(json.dumps({"fisier": f, "iesire": iesire.as_posix(), **s}, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
