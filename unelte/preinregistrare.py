"""Pre-înregistrarea unei nopți. E lecția SANDBOX-7 din planul joi–sâmbătă: așteptările se scriu înainte.

    python unelte/preinregistrare.py --nume noaptea1 --titlu "Noaptea 1: CONTINUUM pe bune"   # din șablon
    python unelte/preinregistrare.py --inchide noaptea1                                        # „Ce a ieșit”, din jurnal

- **Fișierul:** docs/preinregistrari/<data>_<nume>.md (data de azi, sau --data).
- **Șablonul** cere întrebarea, ce rulează, așteptările în cifre și ce le-ar infirma. Se completează înainte de noapte;
  după ce noaptea a început, nu se mai schimbă.
- **Închiderea** adaugă la final secțiunea „Ce a ieșit”, cu:
  - experimentele Kronos începute după scrierea pre-înregistrării (lucru/jurnal/experimente.jsonl): tabelul pe ore și, pentru
    fiecare linie, cel mai bun păstrat;
  - ciclurile CONTINUUM pe bune din aceeași perioadă (lucru/continuum_pe_bune/cicluri.jsonl), cu fiecare acțiune și
    rezultatul ei.

  Verdictul (confirmat sau infirmat) se scrie apoi dedesubt, de om sau de Claude Code.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from kronos.jurnal import Jurnal  # noqa: E402  doar citire

DOSAR = RADACINA / "docs" / "preinregistrari"
SEMN = re.compile(r"<!-- scrisa: (\S+) -->")
INCHISA = "## Ce a ieșit"

SABLON = """# Pre-înregistrare: {titlu}

<!-- scrisa: {acum} -->
*Scrisă la {acum_ro}, înainte de rulare. După ce rularea a început, textul de mai jos nu se mai schimbă; la închidere
se adaugă doar secțiunea „Ce a ieșit” (python unelte/preinregistrare.py --inchide {nume}).*

## Întrebarea

(ce vrem să aflăm, într-o propoziție)

## Ce rulează

(configurarea, cine o pornește, de la ce oră la ce oră, din ce model)

## Așteptările, în cifre

(pentru fiecare variantă: ce cifre așteptăm și ce ar însemna fiecare rezultat)

## Ce ar infirma așteptările

(cifrele care ar arăta că ne-am înșelat)
"""


def cale_pentru(nume: str, ziua: date | None = None, dosar: Path = DOSAR) -> Path:
    return dosar / f"{(ziua or date.today()).isoformat()}_{nume}.md"


def scrie(nume: str, titlu: str, ziua: date | None = None, acum: datetime | None = None, dosar: Path = DOSAR) -> Path:
    """Fișierul nou, din șablon. Unul existent nu se suprascrie."""
    if not re.fullmatch(r"[\w-]+", nume):
        raise ValueError("numele: doar litere, cifre, - și _ (ex. noaptea1)")
    cale = cale_pentru(nume, ziua, dosar)
    if cale.exists():
        raise FileExistsError(f"pre-înregistrarea există deja: {cale}")
    acum = acum or datetime.now()
    cale.parent.mkdir(parents=True, exist_ok=True)
    cale.write_text(SABLON.format(titlu=titlu, nume=nume, acum=acum.isoformat(timespec="seconds"),
                                  acum_ro=f"{acum:%Y-%m-%d %H:%M}"), encoding="utf-8")
    return cale


def gaseste(nume: str, dosar: Path = DOSAR) -> Path:
    gasite = sorted(dosar.glob(f"*_{nume}.md"))
    if len(gasite) != 1:
        raise FileNotFoundError(f"pre-înregistrarea „{nume}”: {len(gasite)} fișiere în {dosar}, trebuie exact unul")
    return gasite[0]


def momentul(text: str) -> datetime:
    """Când a fost scrisă (ora locală, din semnul din fișier)."""
    gasit = SEMN.search(text)
    if not gasit:
        raise ValueError("fișierul n-are semnul „<!-- scrisa: … -->”: nu știu de când să caut în jurnal")
    return datetime.fromisoformat(gasit.group(1))


def _local(text: str | None) -> datetime | None:
    """Ora din jurnal (UTC în jurnalul Kronos, locală în CONTINUUM), ca oră locală fără fus."""
    if not text:
        return None
    t = datetime.fromisoformat(text)
    return t.astimezone().replace(tzinfo=None) if t.tzinfo else t


def experimente_dupa(moment: datetime, director_lucru: Path) -> list[dict[str, Any]]:
    return [f for f in Jurnal(director_lucru).istoric() if (_local(f.get("inceput")) or moment) >= moment]


def cicluri_dupa(moment: datetime, dosar_continuum: Path) -> list[dict[str, Any]]:
    fisier = dosar_continuum / "cicluri.jsonl"
    if not fisier.exists():
        return []
    randuri = [json.loads(r) for r in fisier.read_text(encoding="utf-8").splitlines() if r.strip()]
    return [r for r in randuri if (_local(r.get("timp")) or moment) >= moment]


def _nr(x: Any, zecimale: int = 4) -> str:
    return "—" if x is None else f"{x:.{zecimale}f}".replace(".", ",") if isinstance(x, float) else str(x)


def ce_a_iesit(experimente: list[dict[str, Any]], cicluri: list[dict[str, Any]], acum: datetime) -> str:
    o = [f"\n{INCHISA}\n", f"*Adăugat la {acum:%Y-%m-%d %H:%M}, din jurnalul Kronos (lucru/jurnal/experimente.jsonl) și din "
                           f"jurnalul CONTINUUM pe bune. Verdictul se scrie dedesubt.*\n"]
    if experimente:
        o.append("| # | linia | început | val_bpb | decizia | fapte noi | fapte | nota | motivul |")
        o.append("|---|---|---|---|---|---|---|---|---|")
        for f in experimente:
            c = f.get("criterii") or {}
            o.append(f"| {f.get('id')} | {f.get('linie')} | {_local(f.get('inceput')):%d.%m %H:%M} | "
                     f"{_nr((f.get('scoruri') or {}).get('val_bpb'))} | {f.get('decizie')} | {_nr(c.get('fapte_noi'))} | "
                     f"{_nr(c.get('fapte_corecte'))} | {_nr(c.get('nota_profesor'), 2)} | {f.get('motiv') or ''} |")
        o.append("")
        for linie in dict.fromkeys(f.get("linie") for f in experimente):
            ale_ei = [f for f in experimente if f.get("linie") == linie and (f.get("scoruri") or {}).get("val_bpb")]
            pastrate = [f for f in ale_ei if f.get("decizie") == "pastrat"]
            if not ale_ei:
                continue
            cel_mai_bun = min(pastrate, key=lambda f: f["scoruri"]["val_bpb"]) if pastrate else None
            o.append(f"- **{linie}:** {len(ale_ei)} ore, {len(pastrate)} păstrate; val_bpb de la "
                     f"{_nr(ale_ei[0]['scoruri']['val_bpb'])} la {_nr(ale_ei[-1]['scoruri']['val_bpb'])}"
                     + (f"; cel mai bun păstrat: #{cel_mai_bun['id']} ({_nr(cel_mai_bun['scoruri']['val_bpb'])})"
                        if cel_mai_bun else "; niciunul păstrat")
                     + (f"; pornită din #{ale_ei[0]['fata_de_pornire']} ({_nr(ale_ei[0].get('scor_anterior'))})"
                        if ale_ei[0].get("fata_de_pornire") else "") + ".")
    else:
        o.append("Niciun experiment Kronos în perioada asta.")
    o.append("")
    if cicluri:
        actiuni = [r for r in cicluri if r.get("actiune")]
        niveluri: dict[str, int] = {}
        for r in cicluri:
            niveluri[r.get("nivel") or "oprit/eroare"] = niveluri.get(r.get("nivel") or "oprit/eroare", 0) + 1
        o.append(f"**CONTINUUM pe bune:** {len(cicluri)} cicluri (" + ", ".join(f"{n}: {k}" for n, k in niveluri.items())
                 + f"), {len(actiuni)} cu o acțiune.\n")
        for r in actiuni:
            rezultat = r.get("rezultat") or {}
            stare = ("reușită" if rezultat.get("reusit") else f"nereușită: {rezultat.get('motiv')}") if rezultat else "—"
            o.append(f"- ciclul {r.get('ciclu')}, {_local(r.get('timp')):%d.%m %H:%M}, {r.get('nevoie')}: {r.get('actiune')} "
                     f"({stare}). De ce: {r.get('motiv')}")
    else:
        o.append("Niciun ciclu CONTINUUM pe bune în perioada asta.")
    return "\n".join(o) + "\n"


def inchide(nume: str, director_lucru: Path, dosar_continuum: Path, acum: datetime | None = None,
            dosar: Path = DOSAR) -> Path:
    cale = gaseste(nume, dosar)
    text = cale.read_text(encoding="utf-8")
    if INCHISA in text:
        raise ValueError(f"pre-înregistrarea „{nume}” e deja închisă")
    moment = momentul(text)
    adaos = ce_a_iesit(experimente_dupa(moment, director_lucru), cicluri_dupa(moment, dosar_continuum),
                       acum or datetime.now())
    with cale.open("a", encoding="utf-8") as f:  # doar adaugă: ce era scris rămâne exact cum era
        f.write(adaos)
    return cale


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Pre-înregistrarea unei nopți (așteptările scrise înainte).")
    ce = parser.add_mutually_exclusive_group(required=True)
    ce.add_argument("--nume", help="creează docs/preinregistrari/<data>_<nume>.md din șablon")
    ce.add_argument("--inchide", metavar="NUME", help="adaugă „Ce a ieșit”, din jurnal")
    parser.add_argument("--titlu", default="", help="titlul (la --nume)")
    parser.add_argument("--data", default=None, help="ziua din numele fișierului (AAAA-LL-ZZ; implicit azi)")
    parser.add_argument("--director-lucru", default=str(RADACINA / "lucru"))
    parser.add_argument("--continuum", default=str(RADACINA / "lucru" / "continuum_pe_bune"),
                        help="dosarul CONTINUUM pe bune (cicluri.jsonl)")
    args = parser.parse_args(argv)
    try:
        if args.nume:
            cale = scrie(args.nume, args.titlu or args.nume, date.fromisoformat(args.data) if args.data else None)
            print(f"Scrisă: {cale}. Completează întrebarea, așteptările în cifre și ce le-ar infirma, înainte de rulare.")
        else:
            cale = inchide(args.inchide, Path(args.director_lucru), Path(args.continuum))
            print(f"Închisă: {cale} (secțiunea „Ce a ieșit” adăugată la final).")
    except (FileExistsError, FileNotFoundError, ValueError) as e:
        print(f"Oprit: {e}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
