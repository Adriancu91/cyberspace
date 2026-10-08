"""Faptele hranei, de verificat de om (planul joi–sâmbătă, lecția SANDBOX-7: faptele profesorului le verifică omul).

    python unelte/fapte_de_verificat.py                       # docs/fapte_de_verificat.md, cu traducerile salvate
    python unelte/fapte_de_verificat.py --traduce             # profesorul traduce din nou (pe placa video), apoi la fel
    python unelte/fapte_de_verificat.py --aplica 3,17,42      # DOAR după răspunsul lui Adrian: date/fapte/fapte_gresite.json

Traducerile stau în date/fapte/traduceri.json:
- „profesor”, traducerea automată cerută de plan. Pe 8 octombrie a ieșit adesea greșită, de ex. „Birds have feathers” →
  „Păsări au pălării”.
- „claude”, traducerea lui Claude Code, pentru citit.

Adrian răspunde cu numerele faptelor greșite. Până atunci nu se schimbă nimic. După --aplica:
- faptele marcate ies din generarea de hrană viitoare;
- în examene se marchează și se numără separat, fără să se șteargă (module/fapte_gresite.py).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from module.fapte_gresite import CALE_FAPTE_GRESITE, numerotate  # noqa: E402

CALE_DOC = RADACINA / "docs" / "fapte_de_verificat.md"
CALE_TRADUCERI = RADACINA / "date" / "fapte" / "traduceri.json"
CERERE = ("Translate this sentence into Romanian, as simply and literally as possible. Answer with the Romanian sentence "
          "only, nothing else.\n\n{fapt}")


def traduceri(fapte: list[str]) -> list[str]:
    """Traducerea profesorului (Qwen, fără întâmplare), câte o propoziție, pe placa video."""
    from module.profesor_qwen import ProfesorQwen

    profesor = ProfesorQwen(lot=10, doar_local=True)
    try:
        raspunsuri = profesor.raspunde_mai_multe([[{"role": "user", "content": CERERE.format(fapt=f)}] for f in fapte], 80,
                                                 cu_intamplare=False)
    finally:
        profesor.elibereaza()
    return [r.strip().splitlines()[0].strip() if r.strip() else "" for r in raspunsuri]


def citeste_traduceri(cale: Path = CALE_TRADUCERI) -> dict:
    """{"profesor": {...}, "claude": {...}} sau {}; fiecare cu "traduceri" în ordinea faptelor."""
    if not cale.exists():
        return {}
    date = json.loads(cale.read_text(encoding="utf-8"))
    fapte = [fapt for _, _, fapt in numerotate()]
    if date.get("fapte") != fapte:
        raise ValueError(f"{cale} e pentru alte fapte decât cele de acum: traducerile trebuie refăcute")
    return date


def salveaza_profesorul(traduse: list[str], cale: Path = CALE_TRADUCERI, acum: datetime | None = None) -> None:
    """Traducerea nouă a profesorului; traducerea lui Claude, dacă există, rămâne."""
    date = citeste_traduceri(cale) if cale.exists() else {}
    date.update({"fapte": [fapt for _, _, fapt in numerotate()],
                 "profesor": {"de_la": "Qwen/Qwen3-4B-Instruct-2507 (profesorul), fără întâmplare",
                              "data": (acum or datetime.now()).isoformat(timespec="minutes"), "traduceri": traduse}})
    cale.parent.mkdir(parents=True, exist_ok=True)
    cale.write_text(json.dumps(date, ensure_ascii=False, indent=1), encoding="utf-8")


def text_doc(profesor: list[str] | None = None, claude: list[str] | None = None, acum: datetime | None = None) -> str:
    acum = acum or datetime.now()
    o = ["# Faptele hranei, de verificat de Adrian\n",
         f"*Scris la {acum:%Y-%m-%d %H:%M}. Sunt cele 50 de fapte din care profesorul a scris hrana "
         f"(`date/fapte/povesti.txt`). Pe ele le învață modelul și tot pe ele le întreabă examenele de fapte.*\n",
         "**Ce ai de făcut:** citește-le și trimite-mi numerele celor greșite (de exemplu: „3, 17, 42”). Până atunci nu "
         "se schimbă nimic.",
         "",
         "**După ce primesc numerele:**",
         "- faptele greșite ies din hrana viitoare;",
         "- în examene se marchează și se numără separat, fără să se șteargă (`python unelte/fapte_de_verificat.py "
         "--aplica …`).",
         ""]
    if claude or profesor:
        o.append("**Cum se citește tabelul.** Faptul verificat e cel din engleză.")
        if claude:
            o.append("- **Traducere (Claude Code):** o traducere atentă, ca să citești ușor.")
        if profesor:
            o.append("- **Traducere automată (profesorul):**")
            o.append("  - planul a cerut-o;")
            o.append("  - profesorul (Qwen3-4B) traduce slab în română: multe rânduri sunt greșite, de exemplu „Birds "
                     "have feathers” → „Păsări au pălării”;")
            o.append("  - **nu judeca faptele după ea**: e aici doar ca să se vadă cât de slab traduce profesorul.")
        o.append("")
    coloane = ["Nr.", "Faptul (engleză)"] + (["Traducere (Claude Code)"] if claude else []) \
        + (["Traducere automată (profesorul)"] if profesor else []) + ["Subiectul"]
    o += ["| " + " | ".join(coloane) + " |", "|" + "---|" * len(coloane)]
    for k, (i, subiect, fapt) in enumerate(numerotate()):
        celule = [str(i), fapt] + ([claude[k]] if claude else []) + ([profesor[k]] if profesor else []) + [subiect]
        o.append("| " + " | ".join(celule) + " |")
    return "\n".join(o) + "\n"


def aplica(numere: list[int], cale: Path, acum: datetime | None = None) -> dict:
    valide = {i for i, _, _ in numerotate()}
    gresite = [n for n in numere if n not in valide]
    if gresite:
        raise ValueError(f"numere care nu există (1–{len(valide)}): {gresite}")
    date = {"numere": sorted(set(numere)), "de_la": "Adrian", "data": (acum or datetime.now()).isoformat(timespec="seconds"),
            "nota": "Faptele greșite după verificarea omului (docs/fapte_de_verificat.md): ies din hrana viitoare și se "
                    "marchează în examene, fără să se șteargă."}
    cale.parent.mkdir(parents=True, exist_ok=True)
    cale.write_text(json.dumps(date, ensure_ascii=False, indent=1), encoding="utf-8")
    return date


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Faptele hranei, de verificat de om.")
    parser.add_argument("--traduce", action="store_true", help="cu traducerea automată a profesorului (placa video)")
    parser.add_argument("--aplica", metavar="NUMERE", help="numerele faptelor greșite, cu virgulă (doar de la Adrian)")
    args = parser.parse_args(argv)
    if args.aplica:
        try:
            date = aplica([int(n) for n in args.aplica.replace(" ", "").split(",") if n], RADACINA / CALE_FAPTE_GRESITE)
        except ValueError as e:
            print(f"Oprit: {e}")
            return 1
        print(f"Scris {CALE_FAPTE_GRESITE}: faptele {date['numere']} ies din hrana viitoare și se marchează în examene.")
        return 0
    if args.traduce:
        salveaza_profesorul(traduceri([fapt for _, _, fapt in numerotate()]))
    date = citeste_traduceri()
    profesor = (date.get("profesor") or {}).get("traduceri")
    claude = (date.get("claude") or {}).get("traduceri")
    CALE_DOC.write_text(text_doc(profesor, claude), encoding="utf-8")
    print(f"Scris {CALE_DOC}" + (f" (traduceri: {', '.join(k for k, v in (('Claude', claude), ('profesor', profesor)) if v)})"
                                 if profesor or claude else "") + ".")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
