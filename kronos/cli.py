"""Linia de comandă a platformei.

Exemple:
    python -m kronos verifica --config config/proba.toml
    python -m kronos ruleaza  --config config/proba.toml --experimente 5
    python -m kronos jurnal   --config config/proba.toml
    python -m kronos scrie    --config config/proba.toml --inceput "the cat"
    python -m kronos opreste  --config config/proba.toml
    python -m kronos cauta horse --config config/laptop_gpt_memorie.toml
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import EroareConfig, citeste_config
from .contracte import PORTURI
from .jurnal import Jurnal
from .paznic import Paznic
from .registru import EroareModul, Registru


def _pregateste_consola() -> None:
    for flux in (sys.stdout, sys.stderr):
        try:
            flux.reconfigure(encoding="utf-8")  # diacriticele și pe Windows
        except (AttributeError, ValueError):
            pass
    # Modulele se încarcă din folderul proiectului, oricum ai porni comanda.
    radacina = str(Path(__file__).resolve().parent.parent)
    if radacina not in sys.path:
        sys.path.insert(0, radacina)


def cmd_verifica(args: argparse.Namespace) -> int:
    config = citeste_config(args.config)
    registru = Registru()
    toate_ok = True
    for port in PORTURI:
        cale = config.porturi[port]["modul"]
        try:
            modul = registru.creeaza(port, cale, config.setari_port(port))
            print(f"  ✓ {port:<11} {modul.nume} v{modul.versiune}")
        except EroareModul as e:
            toate_ok = False
            print(f"  ✗ {port:<11} {e}")
    print("Toate modulele sunt în regulă." if toate_ok else "Unele module au probleme (vezi mai sus).")
    return 0 if toate_ok else 1


def cmd_ruleaza(args: argparse.Namespace) -> int:
    from .orchestrator import Orchestrator

    config = citeste_config(args.config)
    orchestrator = Orchestrator(config)
    orchestrator.ruleaza(args.experimente)
    return 0


def cmd_jurnal(args: argparse.Namespace) -> int:
    config = citeste_config(args.config)
    fise = Jurnal(config.director_lucru).istoric(config.nume)
    if not fise:
        print("Jurnalul e gol pentru această configurare.")
        return 0
    examen = Registru().creeaza("examen", config.porturi["examen"]["modul"], config.setari_port("examen")).instanta
    print(f"Scor: {examen.scor_principal} ({'mai mic' if examen.mai_mic_e_mai_bun else 'mai mare'} = mai bun)\n")
    print(f"{'nr':>4}  {'decizie':<8} {'scor':>8}  {'secunde':>7}  propunere")
    for f in fise[-args.ultimele :]:
        scor = (f.get("scoruri") or {}).get(examen.scor_principal)
        scor_text = f"{scor:.4f}" if isinstance(scor, (int, float)) else "-"
        print(
            f"{f['id']:>4}  {f.get('decizie') or '-':<8} {scor_text:>8}  "
            f"{f.get('durata_totala_secunde', 0):>7}  {f['propunere']['descriere']}"
        )
        if f.get("decizie") == "anulat" and f.get("motiv"):
            print(f"{'':>15}motiv: {f['motiv']}")
    return 0


def cmd_scrie(args: argparse.Namespace) -> int:
    """Încarcă cel mai bun model păstrat și îl pune să continue un text."""
    config = citeste_config(args.config)
    registru = Registru()
    examen = registru.creeaza("examen", config.porturi["examen"]["modul"], config.setari_port("examen")).instanta
    cel_mai_bun = Jurnal(config.director_lucru).cel_mai_bun(
        config.nume, examen.scor_principal, examen.mai_mic_e_mai_bun
    )
    if cel_mai_bun is None or "model_salvat" not in cel_mai_bun:
        print("Nu există încă un model păstrat. Rulează întâi: python -m kronos ruleaza --config ...")
        return 1
    model = registru.creeaza("model", config.porturi["model"]["modul"], cel_mai_bun["setari"].get("model", {})).instanta
    if hasattr(model, "conecteaza_memorie"):
        model.conecteaza_memorie(
            registru.creeaza("memorie", config.porturi["memorie"]["modul"], config.setari_port("memorie")).instanta
        )
    model.incarca(cel_mai_bun["model_salvat"])
    print(f"Modelul din experimentul {cel_mai_bun['id']} (scor {cel_mai_bun['scoruri'][examen.scor_principal]:.4f}):\n")
    print(args.inceput + model.genereaza(args.inceput, args.lungime))
    return 0


def cmd_cauta(args: argparse.Namespace) -> int:
    """Arată unde stă un cuvânt în memoria ierarhică."""
    config = citeste_config(args.config)
    memorie = Registru().creeaza("memorie", config.porturi["memorie"]["modul"], config.setari_port("memorie")).instanta
    sensuri = memorie.cauta(args.cuvant)
    if not sensuri:
        print(f"„{args.cuvant}” nu e în memorie.")
        return 0
    cod = ".".join(str(x) for x in memorie.cod(args.cuvant))
    print(f"„{args.cuvant}”: {len(sensuri)} sensuri în memorie. Modelul primește codul sensului 1: {cod}\n")
    for nr, sens in enumerate(sensuri[: args.sensuri], start=1):
        print(f"Sensul {nr}: {sens.get('parte_de_vorbire', '?')}, raftul {sens.get('raft', '?')}, cod {sens.get('cod', '?')}")
        if sens.get("drum"):
            print("   " + " > ".join(sens["drum"]))
        for relatie in sens.get("relatii", [])[:6]:
            print(f"   {relatie['tip']}: {relatie['catre']}")
    return 0


def cmd_opreste(args: argparse.Namespace) -> int:
    config = citeste_config(args.config)
    paznic = Paznic(config.paznic, config.director_lucru)
    paznic.cere_oprire()
    print(f"Am cerut oprirea. Experimentul în curs se termină, apoi Kronos se oprește.\n"
          f"Ca să poată porni din nou: python -m kronos porneste --config {args.config}")
    return 0


def cmd_porneste(args: argparse.Namespace) -> int:
    config = citeste_config(args.config)
    Paznic(config.paznic, config.director_lucru).anuleaza_oprire()
    print("Butonul de oprire a fost resetat. Kronos poate porni din nou.")
    return 0


def cmd_aproba_examen(args: argparse.Namespace) -> int:
    config = citeste_config(args.config)
    examen = Registru().creeaza("examen", config.porturi["examen"]["modul"], config.setari_port("examen")).instanta
    nume = Paznic(config.paznic, config.director_lucru).aproba_examen(examen)
    print(f"Am aprobat versiunea actuală a examenului „{nume}”.")
    return 0


def main(argv: list[str] | None = None) -> int:
    _pregateste_consola()
    parser = argparse.ArgumentParser(prog="kronos", description="Cyberspace: Kronos (nucleul) + module")
    sub = parser.add_subparsers(dest="comanda", required=True)

    def adauga(nume: str, ajutor: str, functie) -> argparse.ArgumentParser:
        p = sub.add_parser(nume, help=ajutor)
        p.add_argument("--config", default="config/proba.toml", help="fișierul de configurare")
        p.set_defaults(functie=functie)
        return p

    adauga("verifica", "verifică dacă toate modulele se încarcă", cmd_verifica)
    p = adauga("ruleaza", "rulează bucla de experimente", cmd_ruleaza)
    p.add_argument("--experimente", type=int, default=None, help="câte experimente (implicit: din configurare)")
    p = adauga("jurnal", "arată ultimele experimente", cmd_jurnal)
    p.add_argument("--ultimele", type=int, default=30)
    p = adauga("scrie", "cel mai bun model continuă un text", cmd_scrie)
    p.add_argument("--inceput", default="the ")
    p.add_argument("--lungime", type=int, default=300)
    p = adauga("cauta", "unde stă un cuvânt în memoria ierarhică", cmd_cauta)
    p.add_argument("cuvant")
    p.add_argument("--sensuri", type=int, default=3, help="câte sensuri să arate")
    adauga("opreste", "butonul de oprire", cmd_opreste)
    adauga("porneste", "resetează butonul de oprire", cmd_porneste)
    adauga("aproba-examen", "aprobă o schimbare făcută de tine în examen", cmd_aproba_examen)

    args = parser.parse_args(argv)
    try:
        return args.functie(args)
    except (EroareConfig, EroareModul) as e:
        print(f"Eroare: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nOprit cu Ctrl+C. Experimentul întrerupt nu a fost înregistrat.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
