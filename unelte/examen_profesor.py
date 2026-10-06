"""Examenul profesorului (Faza 3, pasul 2): nota profesorului pe aceleași 20 de povești nevăzute, pentru orice model
salvat, ca măsura din testul profesorului (elevul 10 × 512: 4,7 din 10) să se poată repeta pe modelele viitoare.

- Aceleași 20 de povești din validarea R2, alese cu aceeași sămânță ca în unelte/test_profesor.py.
- Elevul pornește din prima propoziție a fiecăreia și scrie cam cât povestea originală (între 200 și 1.000 de litere);
  povestea lui se taie la ultima propoziție întreagă.
- Profesorul (module/profesor_qwen.py) dă note fără întâmplare, pe aceleași loturi, deci aceeași poveste ia aceeași notă.
Textele, cu notele și motivele, merg în lucru/profesor/examen_experiment_<nr>_<data>/. În jurnal, o fișă doar cu numere
(linia „examen_profesor”).

    python unelte/examen_profesor.py --experiment 226
    python unelte/examen_profesor.py --linie antrenare_lunga_3      # ultimul model salvat de pe linie
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from kronos.jurnal import Jurnal  # noqa: E402
from module.profesor_qwen import ProfesorQwen  # noqa: E402
from unelte.modele_salvate import fisa_modelului, incarca_modelul  # noqa: E402
from unelte.test_profesor import alege_povesti, distributie, medie, povesti_elevului, scrie_jsonl  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Nota profesorului pe aceleași 20 de povești nevăzute, pentru un model salvat.")
    alegere = parser.add_mutually_exclusive_group(required=True)
    alegere.add_argument("--experiment", type=int, help="numărul experimentului cu modelul salvat")
    alegere.add_argument("--linie", help="ultimul model salvat de pe această linie de jurnal")
    parser.add_argument("--validare", default="date/tinystories_r2/validare.txt", help="poveștile TinyStories nevăzute")
    parser.add_argument("--povesti", type=int, default=20, help="câte povești (aceleași ca în testul profesorului)")
    parser.add_argument("--lot", type=int, default=8, help="câte povești notează profesorul deodată")
    parser.add_argument("--director-lucru", default="lucru")
    parser.add_argument("--doar-local", action="store_true", help="nu descărca nimic (modelul trebuie să fie în cache)")
    args = parser.parse_args(argv)
    import torch

    jurnal = Jurnal(Path(args.director_lucru))
    fisa = fisa_modelului(jurnal, args.experiment, args.linie)
    originale = alege_povesti(Path(args.validare).read_text(encoding="utf-8"), args.povesti)
    elev = incarca_modelul(fisa)
    povesti = povesti_elevului(elev, originale)
    del elev
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    profesor = ProfesorQwen(lot=args.lot, doar_local=args.doar_local)
    note = profesor.noteaza_mai_multe([p["poveste"] for p in povesti])
    profesor.elibereaza()

    eticheta = datetime.now().strftime("%Y%m%d_%H%M%S")
    dosar = Path(args.director_lucru) / "profesor" / f"examen_experiment_{fisa['id']}_{eticheta}"
    dosar.mkdir(parents=True, exist_ok=True)
    scrie_jsonl(dosar / "povesti.jsonl", [{**p, **n} for p, n in zip(povesti, note)])
    valori = [n["nota"] for n in note]
    scoruri = {"nota_medie": medie(valori), "povesti": len(povesti), "note_lipsa": sum(v is None for v in valori),
               "cuvinte_pe_poveste": round(statistics.mean(len(p["poveste"].split()) for p in povesti), 1)}
    jurnal.adauga({
        "id": jurnal.urmatorul_id(), "linie": "examen_profesor",
        "inceput": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "propunere": {"descriere": f"examenul profesorului pentru modelul experimentului #{fisa['id']} "
                                   f"(textele: {dosar.as_posix()}/)", "modificari": {}},
        "module": {"elev": {"experiment": fisa["id"], "linie": fisa["linie"]},
                   "profesor": {**ProfesorQwen.MANIFEST, "model": profesor.model}},
        "decizie": "masurat", "scoruri": scoruri, "distributie_note": distributie(valori),
    })
    print(f"=== Examenul profesorului: modelul experimentului #{fisa['id']} (linia „{fisa['linie']}”) ===")
    print(f"Media notelor: {scoruri['nota_medie']} din 10, pe {len(povesti)} povești (~{scoruri['cuvinte_pe_poveste']:.0f} "
          f"de cuvinte); notele (nota: câte): "
          + ", ".join(f"{n}: {c}" for n, c in distributie(valori).items() if c) + ".")
    print(f"Textele: {dosar}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
