"""Pornirea interfeței din linia de comandă. Oprirea: Ctrl+C.

    python -m module.interfata --config config/laptop_antrenare_lunga_8.toml --experiment 295 --port 8787
    python -m module.interfata --config config/proba.toml --fals        # fără niciun model, doar de probă
    python -m module.interfata --config config/ws_w1.toml --experiment 312 --experiment-text 407  # cu fila „Întreabă din text”
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from kronos.config import EroareConfig, citeste_config

from . import PORT_IMPLICIT, retea
from .catalog import Catalog
from .creiere import Creier, CreierFals, CreierKronos, CreierText
from .module_ui import lista_modulelor
from .server import LUNGIME_RASPUNS_IMPLICITA, Aplicatie, Servere, porneste

NUME_BAZA = "conversatii.db"


def _argumente(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m module.interfata",
        description="Interfața v0: chat în browser cu Kronos, doar de pe acest calculator și prin Tailscale.",
    )
    parser.add_argument("--config", required=True, help="configurarea Kronos din care se citesc modulele")
    parser.add_argument("--experiment", type=int, help="numărul experimentului cu modelul salvat care răspunde")
    parser.add_argument("--experiment-text", type=int,
                        help="modelul care răspunde în fila „Întreabă din text” (fără el, fila nu apare)")
    parser.add_argument("--fals", action="store_true", help="creier de probă, fără niciun model")
    parser.add_argument("--port", type=int, default=PORT_IMPLICIT, help=f"portul (implicit {PORT_IMPLICIT})")
    parser.add_argument("--dispozitiv", default="cpu", help="pe ce rulează modelul (implicit cpu, adică procesorul)")
    parser.add_argument("--lungime", type=int, default=LUNGIME_RASPUNS_IMPLICITA,
                        help=f"lungimea unui răspuns (implicit {LUNGIME_RASPUNS_IMPLICITA})")
    parser.add_argument("--baza", help=f"fișierul SQLite cu conversațiile (implicit lucru/interfata/{NUME_BAZA})")
    parser.add_argument("--detaliat", action="store_true", help="scrie pe ecran fiecare cerere primită")
    args = parser.parse_args(argv)
    if args.fals == (args.experiment is not None):
        parser.error("alege una: --experiment NUMĂR (modelul lui Kronos) sau --fals (creierul de probă)")
    if not 0 <= args.port <= 65535:
        parser.error("portul trebuie să fie între 0 și 65535")
    return args


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    args = _argumente(argv)
    try:
        config = citeste_config(args.config)
    except EroareConfig as e:
        print(f"Nu pot porni: {e}")
        return 2

    creier: Creier = CreierFals() if args.fals else CreierKronos(args.experiment, config.director_lucru, args.dispozitiv)
    baza = Path(args.baza) if args.baza else config.director_lucru / "interfata" / NUME_BAZA
    creier_text = (CreierText(args.experiment_text, config.director_lucru, args.dispozitiv)
                   if args.experiment_text is not None else None)
    aplicatie = Aplicatie(Catalog(baza), creier, lista_modulelor(config), config.nume, args.lungime, creier_text)

    tailscale = retea.adresa_tailscale()
    try:
        servere: Servere = porneste(aplicatie, args.port, retea.adrese_de_ascultat(tailscale), args.detaliat)
    except OSError as e:
        print(f"Nu pot porni pe portul {args.port}: {e}")
        print("Poate interfața e deja pornită în altă fereastră. Închide-o pe aceea sau alege alt port cu --port.")
        return 1

    print("Interfața Cyberspace v0 a pornit.")
    lenes = "" if args.fals else f", pe „{args.dispozitiv}”; se încarcă la prima întrebare"
    print(f"   Răspunde: {creier.eticheta}{lenes}")
    if creier_text is not None:
        print(f"   Fila „Întreabă din text”: {creier_text.eticheta}")
    print(f"   Module:   din configurarea „{config.nume}” ({len(aplicatie.module)} porturi)")
    print(f"   Istoric:  {baza}")
    for adresa in servere.adrese:
        print(f"   Deschide în browser: {adresa}")
    if tailscale is None:
        print("   Tailscale nu a fost găsit sau nu e pornit: interfața merge doar de pe acest calculator.")
    for adresa, motiv in servere.neascultate:
        print(f"   Atenție: nu pot asculta pe {adresa} ({motiv}); pe celelalte adrese merge.")
    print("Oprire: Ctrl+C.", flush=True)

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nOpresc interfața…")
    finally:
        servere.opreste()
    print("Interfața s-a oprit. Conversațiile au rămas în istoric.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
