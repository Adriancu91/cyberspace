"""Măsoară încărcarea rafturilor WordNet pe TinyStories (Etapa M3, pasul 1, fără antrenare).

Pentru fiecare cuvânt terminat din textul de antrenare: raftul sensului lui principal (din memoria ierarhică)
sau „umplutură”: cuvintele pe care biblioteca nu le are și cuvintele de legătură (the, a, it, in, can...),
pe care WordNet le are doar cu alt sens (a = vitamina A, can = cutie de conserve). Arată:
- rafturile sortate după încărcare (procent din cuvintele cu sens) și cele mai dese cuvinte ale fiecăruia;
- câte rafturi acoperă 90% din cuvintele cu sens și câte trec de 0,5% (câte noduri ar avea plasa adaptivă);
- cele mai puternice asocieri între rafturi: de câte ori mai des decât întâmplător e urmat un cuvânt al unui
  raft de unul al altui raft (cuvinte vecine, cu ordine), doar pentru perechile văzute de cel puțin 100 de ori.

    python unelte/masoara_rafturi.py

Rezultatul: pe ecran și în lucru/rafturi_tinystories.json.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from module.memorie_ierarhica import MemorieIerarhica  # noqa: E402

UMPLUTURA = "umplutură"
PRAG_NOD = 0.005  # un raft cu cel puțin 0,5% din cuvintele cu sens primește un nod
ACOPERIRE = 0.9
MINIM_PERECHE = 100  # sub atâtea apariții, asocierea unei perechi e prea puțin sigură


def masoara(
    text: str, memorie: MemorieIerarhica, bruta: MemorieIerarhica | None = None, minim_pereche: int = MINIM_PERECHE
) -> dict[str, Any]:
    """memorie = cu fara_cuvinte_de_legatura; bruta (opțional) = fără, ca să vedem ce sens le dădea WordNet."""
    categorii: list[str] = []
    pe_raft: Counter[str] = Counter()
    exemple: defaultdict[str, Counter[str]] = defaultdict(Counter)
    negasite = de_legatura = 0
    legatura_cu_alt_sens: Counter[str] = Counter()
    for _, cuvant in memorie.cuvinte_terminate(text):
        cod = memorie.cod(cuvant)
        if 1 <= cod[0] <= 4:
            raft = memorie.rafturi[cod[1] - 1]
            pe_raft[raft] += 1
            exemple[raft][cuvant.lower()] += 1
            categorii.append(raft)
            continue
        categorii.append(UMPLUTURA)
        if memorie.este_cuvant_de_legatura(cuvant):
            de_legatura += 1
            if bruta is not None and 1 <= bruta.cod(cuvant)[0] <= 4:
                legatura_cu_alt_sens[cuvant.lower()] += 1  # WordNet îl avea, dar cu alt sens
        else:
            negasite += 1

    total, cu_sens = len(categorii), sum(pe_raft.values())
    rafturi, cumulat = [], 0
    for raft, n in pe_raft.most_common():
        cumulat += n
        rafturi.append({
            "raft": raft, "cuvinte": n, "procent": n / cu_sens, "procent_cumulat": cumulat / cu_sens,
            "exemple": [c for c, _ in exemple[raft].most_common(4)],
        })
    pentru_90 = next((k + 1 for k, r in enumerate(rafturi) if r["procent_cumulat"] >= ACOPERIRE), len(rafturi))

    # Asocierea: perechi de cuvinte vecine (cu ordine), pe tot textul; umplutura e și ea o categorie.
    frecventa = Counter(categorii)
    perechi = Counter(zip(categorii, categorii[1:]))
    asocieri = []
    for (a, b), n in perechi.items():
        if a != b and UMPLUTURA not in (a, b) and n >= minim_pereche:
            asteptat = (frecventa[a] / total) * (frecventa[b] / total)
            asocieri.append({"de_la": a, "la": b, "asociere": (n / (total - 1)) / asteptat, "apar": n})
    asocieri.sort(key=lambda x: -x["asociere"])

    return {
        "cuvinte": total,
        "cu_sens": cu_sens,
        "umplutura": {"total": total - cu_sens, "negasite": negasite, "de_legatura": de_legatura,
                      "de_legatura_cu_alt_sens_in_wordnet": dict(legatura_cu_alt_sens.most_common(15))},
        "rafturi": rafturi,
        "rafturi_pentru_90_la_suta": pentru_90,
        "rafturi_cu_nod": sum(1 for r in rafturi if r["procent"] >= PRAG_NOD),
        "asocieri": asocieri,
    }


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Încărcarea rafturilor WordNet pe TinyStories.")
    parser.add_argument("--biblioteca", default="date/biblioteca.json.gz")
    parser.add_argument("--date", default="date/tinystories", help="dosarul datelor TinyStories")
    args = parser.parse_args(argv)

    from module.date_tinystories import DateTinyStories

    text = DateTinyStories(director=args.date).text_antrenare()
    rezultat = masoara(
        text,
        MemorieIerarhica(args.biblioteca, fara_cuvinte_de_legatura=True),
        bruta=MemorieIerarhica(args.biblioteca),
    )
    u = rezultat["umplutura"]
    print(f"TinyStories (antrenare): {rezultat['cuvinte']:,} cuvinte")
    print(f"  umplutură: {u['total']:,} ({u['total'] / rezultat['cuvinte']:.1%}): negăsite {u['negasite']:,}, "
          f"de legătură {u['de_legatura']:,}")
    print(f"  cuvinte cu sens: {rezultat['cu_sens']:,} ({rezultat['cu_sens'] / rezultat['cuvinte']:.1%})")
    print("  cuvinte de legătură pe care WordNet le avea cu alt sens: "
          + ", ".join(f"{c} {n:,}" for c, n in u["de_legatura_cu_alt_sens_in_wordnet"].items()))
    print(f"\n{'raft':<22} {'cuvinte':>9} {'%':>6} {'% cumulat':>9}  cele mai dese")
    for r in rezultat["rafturi"]:
        print(f"{r['raft']:<22} {r['cuvinte']:>9,} {r['procent']:>6.1%} {r['procent_cumulat']:>9.1%}  {', '.join(r['exemple'])}")
    print(f"\nRafturi care acoperă 90% din cuvintele cu sens: {rezultat['rafturi_pentru_90_la_suta']} "
          f"din {len(rezultat['rafturi'])}")
    print(f"Rafturi cu cel puțin {PRAG_NOD:.1%} din cuvintele cu sens (un nod fiecare): {rezultat['rafturi_cu_nod']}; "
          f"restul ({len(rezultat['rafturi']) - rezultat['rafturi_cu_nod']}) ar merge la nodul „rar”")
    print(f"\nCele mai puternice 10 asocieri (cuvinte vecine, cu ordine, perechi văzute de cel puțin {MINIM_PERECHE} ori):")
    for a in rezultat["asocieri"][:10]:
        print(f"  {a['de_la']:<20} → {a['la']:<20} {a['asociere']:5.2f}×  ({a['apar']:,} de ori)")

    iesire = Path("lucru") / "rafturi_tinystories.json"
    iesire.parent.mkdir(parents=True, exist_ok=True)
    iesire.write_text(json.dumps(rezultat, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSalvat în {iesire}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
