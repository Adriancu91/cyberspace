"""Validările curate (18 octombrie 2026, aprobat de Adrian): lângă fiecare validare, o variantă fără textele scurse în
antrenare.

Regula (din docs/scurgeri_examen_17oct.md): un text de validare e „curat” dacă **nicio bucată de 200 de litere la rând
nu apare în antrenare** și **sub jumătate din literele lui stau în bucăți de 50 de litere găsite în antrenare**.
Antrenarea e cea văzută de Kronos W2 (unelte/scurgeri_examen.py: amestecul și hrana).

Se citește **tot** fișierul de validare (nu doar primele 100.000 de litere), iar textele curate se scriu, în aceeași
ordine, în validare_curata.txt, lângă validare.txt. Validarea veche nu se atinge, nici examenul oficial
(module/examen_bpb.py), nici jurnalul. Fabulele nu primesc variantă curată: au ieșit din examen.

Doar pe procesor. Un fișier curat deja scris nu se rescrie (decât cu --rescrie).

    python unelte/validari_curate.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from unelte.examen_validari_ws import SEPARATOR  # noqa: E402
from unelte.scurgeri_examen import ANTRENARE, cauta_lungimi, texte_validare  # noqa: E402

# numele din examen → validarea veche; varianta curată stă lângă ea, în validare_curata.txt
DE_CURATAT = {
    "povesti": "date/tinystories_r2/validare.txt",
    "romana_wikipedia": "date/ws/curat/wikipedia_ro/validare.txt",
    "romana_web": "date/ws/curat/fineweb2_ro/validare.txt",
    "romana_carti": "date/ws/curat/wikisource_ro/validare.txt",
    "traducere": "date/ws/curat/europarl_en_ro/validare.txt",
    "cod_python": "date/ws/curat/cod_stack/validare.txt",
    "cod_sarcini": "date/ws/curat/cod_instruct/validare.txt",
}
SCURT, LUNG = 50, 200
PRAG_SCURT = 0.5
RAPORT = "date/ws/curat/validari_curate.json"


def cale_curata(cale: str | Path) -> Path:
    return Path(cale).with_name("validare_curata.txt")


def curate(acoperire_scurt: list[float], acoperire_lung: list[float]) -> list[bool]:
    """Care texte trec regula: nimic găsit la bucăți lungi și sub prag la bucăți scurte."""
    return [lung == 0 and scurt < PRAG_SCURT for scurt, lung in zip(acoperire_scurt, acoperire_lung)]


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Lângă fiecare validare, varianta fără textele scurse în antrenare.")
    parser.add_argument("--antrenare", nargs="*", default=ANTRENARE)
    parser.add_argument("--validari", help="un JSON nume → validare.txt, în locul celor din examen")
    parser.add_argument("--raport", default=RAPORT)
    parser.add_argument("--rescrie", action="store_true", help="rescrie fișierele curate deja făcute")
    args = parser.parse_args(argv)

    alese = json.loads(Path(args.validari).read_text(encoding="utf-8")) if args.validari else DE_CURATAT
    alese = {v: c for v, c in alese.items() if Path(c).is_file()}
    deja = [str(cale_curata(c)) for c in alese.values() if cale_curata(c).exists()]
    if deja and not args.rescrie:
        print(f"Există deja: {', '.join(deja)}. Nu le rescriu (doar cu --rescrie).")
        return 1
    validari = {v: texte_validare(Path(c), None) for v, c in alese.items()}
    pe_lungime = cauta_lungimi(validari, [Path(c) for c in args.antrenare], [SCURT, LUNG])
    raport: dict[str, Any] = {"scris": datetime.now().isoformat(timespec="seconds"), "antrenare": args.antrenare,
                              "regula": f"nicio bucată de {LUNG} de litere în antrenare și sub {PRAG_SCURT:.0%} din "
                                        f"litere acoperite de bucăți de {SCURT}", "validari": {}}
    print(f"{'validarea':<18} {'texte':>7} {'curate':>7} {'litere curate':>14}")
    for v, texte in validari.items():
        bune = curate(pe_lungime[SCURT][v]["acoperire_pe_text"], pe_lungime[LUNG][v]["acoperire_pe_text"])
        pastrate = [t for t, b in zip(texte, bune) if b]
        continut = "".join(f"{t}\n{SEPARATOR}\n" for t in pastrate)
        iesire = cale_curata(alese[v])
        iesire.write_text(continut, encoding="utf-8", newline="\n")
        raport["validari"][v] = {"validare": alese[v], "curata": iesire.as_posix(), "texte": len(texte),
                                 "texte_curate": len(pastrate), "litere": sum(map(len, texte)),
                                 "litere_curate": sum(map(len, pastrate)),
                                 "sha256": hashlib.sha256(continut.encode("utf-8")).hexdigest()}
        r = raport["validari"][v]
        print(f"{v:<18} {r['texte']:>7} {r['texte_curate']:>7} {r['litere_curate']:>14,}")
    Path(args.raport).parent.mkdir(parents=True, exist_ok=True)
    Path(args.raport).write_text(json.dumps(raport, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Raportul: {args.raport}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
