"""Construiește baza lingvistică de la zero, din sursele descărcate (`descarca_surse.py`).

Ordinea importului contează:
  1. Wiktionary/kaikki (singura sursă care distinge omonimele → numerotarea omonimelor se stabilește prima);
  2. UD RRT (forme atestate în corpus, exemple, relații de dependență);
  3. RoWordNet (concepte, sensuri, relații semantice);
  4. Hunspell (forme generate de reguli de afixare; confirmă formele celorlalte surse);
  5. inventarul trăsăturilor, regulile explicite (paradigmele proprii), fuziunea formelor fără trăsături,
     recalcularea statutului formelor (atestat / generat / validat), verificarea integrității.

Folosire:
    python -m module.limba_romana.importatoare.construieste_baza [--proaspat] [--fara hunspell rown ...] [--cale fisier.sqlite]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from .. import VERSIUNE
from ..baza import CALE_IMPLICITA, Baza
from ..morfologie.trasaturi import INVENTAR
from . import importa_hunspell, importa_kaikki, importa_rown, importa_ud

PASI = (("kaikki", importa_kaikki.importa), ("ud_rrt", importa_ud.importa), ("rown", importa_rown.importa), ("hunspell", importa_hunspell.importa))


def construieste(cale: Path | None = None, fara: set[str] | None = None, proaspat: bool = False, verbos: bool = True, doar_finalizare: bool = False) -> dict:
    fara = fara or set()
    cale = Path(cale) if cale else CALE_IMPLICITA
    if proaspat:
        for suf in ("", "-wal", "-shm", "-journal"):
            p = Path(str(cale) + suf)
            if p.exists():
                p.unlink()
    raport: dict = {"versiune_motor": VERSIUNE, "pasi": {}, "durate_secunde": {}}
    with Baza(cale) as b:
        b.seteaza_trasaturi(INVENTAR)
        for nume, functie in PASI:
            if nume in fara:
                raport["pasi"][nume] = "sărit (--fara)"
                continue
            if doar_finalizare:
                raport["pasi"][nume] = "păstrat (--continua)"
                continue
            t0 = time.time()
            raport["pasi"][nume] = functie(b, verbos=verbos)
            raport["durate_secunde"][nume] = round(time.time() - t0, 1)
        # regulile explicite (paradigmele proprii) se aplică peste lexicon, dacă modulul e disponibil
        try:
            from ..morfologie import paradigme
            t0 = time.time()
            raport["pasi"]["paradigme"] = paradigme.aplica_peste_baza(b, verbos=verbos)
            raport["durate_secunde"]["paradigme"] = round(time.time() - t0, 1)
        except ImportError:
            raport["pasi"]["paradigme"] = "modulul paradigme lipsește"
        try:
            from ..morfologie import inchise
            raport["pasi"]["clase_inchise"] = inchise.scrie_in_baza(b, verbos=verbos)
        except ImportError:
            raport["pasi"]["clase_inchise"] = "modulul inchise lipsește"
        try:
            from ..sintaxa import reguli as reguli_sintaxa
            raport["pasi"]["reguli_sintaxa"] = reguli_sintaxa.scrie_in_baza(b)
        except ImportError:
            raport["pasi"]["reguli_sintaxa"] = "modulul reguli lipsește"
        t0 = time.time()
        raport["pasi"]["fuziune_forme"] = b.fuzioneaza_forme_fara_trasaturi()
        raport["pasi"]["statut_forme"] = b.recalculeaza_statut_forme()
        raport["durate_secunde"]["finalizare"] = round(time.time() - t0, 1)
        raport["integritate"] = b.verifica_integritate()
        raport["statistici"] = b.statistici()
        b.adauga_validare("construire_baza", VERSIUNE, {k: v for k, v in raport.items() if k != "statistici"})
        b.commit()
        b.con.execute("VACUUM")
    if verbos:
        print(json.dumps({k: raport[k] for k in ("durate_secunde", "statistici")}, ensure_ascii=False, indent=1, default=str))
        print("integritate OK" if raport["integritate"]["ok"] else "integritate: PROBLEME → " + json.dumps(
            {k: v for k, v in raport["integritate"]["verificari"].items() if v["probleme"]}, ensure_ascii=False, default=str))
    return raport


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--cale", default=None, help="fișierul SQLite (implicit: _baza/limba_romana.sqlite)")
    p.add_argument("--fara", nargs="*", default=[], help="surse de sărit: kaikki ud_rrt rown hunspell")
    p.add_argument("--proaspat", action="store_true", help="șterge baza existentă înainte")
    p.add_argument("--continua", action="store_true", help="nu reimportă sursele; rulează doar paradigmele, clasele închise, regulile și finalizarea")
    a = p.parse_args(argv)
    raport = construieste(a.cale, set(a.fara), a.proaspat, doar_finalizare=a.continua)
    return 0 if raport["integritate"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
