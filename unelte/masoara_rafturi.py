"""Măsoară încărcarea rafturilor WordNet pe TinyStories (Etapa M3, pasul 1, fără antrenare).

Pentru fiecare cuvânt terminat din textul de antrenare: raftul sensului lui principal (din memoria ierarhică)
sau „umplutură”: cuvintele pe care biblioteca nu le are și cuvintele de legătură (the, a, it, in, can...),
pe care WordNet le are doar cu alt sens (a = vitamina A, can = cutie de conserve). Arată:
- rafturile sortate după încărcare (procent din cuvintele cu sens) și cele mai dese cuvinte ale fiecăruia;
- câte rafturi acoperă 90% din cuvintele cu sens și câte trec de 0,5% (câte noduri ar avea plasa adaptivă);
- cele mai puternice asocieri între rafturi: de câte ori mai des decât întâmplător e urmat un cuvânt al unui
  raft de unul al altui raft (cuvinte vecine, cu ordine), doar pentru perechile văzute de cel puțin 100 de ori.

    python unelte/masoara_rafturi.py                       # sensul principal din dicționar
    python unelte/masoara_rafturi.py --sens-dupa-context   # cu regulile a, b, c ale memoriei, comparat cu cel de sus

Rezultatul: pe ecran și în lucru/rafturi_tinystories.json (cu --sens-dupa-context: rafturi_tinystories_context.json).
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

from module.memorie_ierarhica import ADVERBE_PREFERATE, MemorieIerarhica  # noqa: E402

UMPLUTURA = "umplutură"
PRAG_NOD = 0.005  # un raft cu cel puțin 0,5% din cuvintele cu sens primește un nod
ACOPERIRE = 0.9
MINIM_PERECHE = 100  # sub atâtea apariții, asocierea unei perechi e prea puțin sigură
PRAGURI_ASOCIERE = (2, 3, 5)  # câte perechi trec de fiecare, ca să alegem pragul de naștere al legăturilor


def _categorie(memorie: MemorieIerarhica, cod: tuple[int, ...]) -> str:
    """Raftul codului sau, pentru cuvintele fără sens în bibliotecă, umplutura."""
    return memorie.rafturi[cod[1] - 1] if 1 <= cod[0] <= 4 else UMPLUTURA


def _regula(cuvant: str, la_inceput: bool, raft_nou: str) -> str:
    """Ce regulă a setării sens_dupa_context a mutat cuvântul (memoria le încearcă în ordinea b, c, a)."""
    if raft_nou == "noun.person" and not la_inceput and cuvant.lstrip("'")[:1].isupper():
        return "b_nume"
    if cuvant.lower().strip("'") in ADVERBE_PREFERATE:
        return "c_adverbe"
    return "a_forme_de_verb"


def masoara(
    text: str,
    memorie: MemorieIerarhica,
    bruta: MemorieIerarhica | None = None,
    veche: MemorieIerarhica | None = None,
    minim_pereche: int = MINIM_PERECHE,
) -> dict[str, Any]:
    """memorie = cu fara_cuvinte_de_legatura; bruta (opțional) = fără, ca să vedem ce sens le dădea WordNet;
    veche (opțional) = memoria unei măsurători de dinainte, ca să numărăm cuvintele care și-au schimbat raftul."""
    categorii: list[str] = []
    pe_raft: Counter[str] = Counter()
    exemple: defaultdict[str, Counter[str]] = defaultdict(Counter)
    negasite = de_legatura = 0
    legatura_cu_alt_sens: Counter[str] = Counter()
    schimbari: Counter[tuple[str, str, str]] = Counter()
    pe_reguli: Counter[str] = Counter()
    for _, cuvant, la_inceput in memorie.cuvinte_terminate(text):
        categorie = _categorie(memorie, memorie.cod(cuvant, la_inceput))
        categorii.append(categorie)
        if categorie != UMPLUTURA:
            pe_raft[categorie] += 1
            exemple[categorie][cuvant.lower()] += 1
        elif memorie.este_cuvant_de_legatura(cuvant):
            de_legatura += 1
            if bruta is not None and _categorie(bruta, bruta.cod(cuvant)) != UMPLUTURA:
                legatura_cu_alt_sens[cuvant.lower()] += 1  # WordNet îl avea, dar cu alt sens
        else:
            negasite += 1
        if veche is not None:
            inainte = _categorie(veche, veche.cod(cuvant))
            if inainte != categorie:
                schimbari[(cuvant.lower(), inainte, categorie)] += 1
                pe_reguli[_regula(cuvant, la_inceput, categorie)] += 1

    total, cu_sens = len(categorii), sum(pe_raft.values())
    rafturi, cumulat = [], 0
    for raft, n in pe_raft.most_common():
        cumulat += n
        rafturi.append({
            "raft": raft, "cuvinte": n, "procent": n / cu_sens, "procent_cumulat": cumulat / cu_sens,
            "exemple": [c for c, _ in exemple[raft].most_common(5)],
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

    rezultat: dict[str, Any] = {
        "cuvinte": total,
        "cu_sens": cu_sens,
        "umplutura": {"total": total - cu_sens, "negasite": negasite, "de_legatura": de_legatura,
                      "de_legatura_cu_alt_sens_in_wordnet": dict(legatura_cu_alt_sens.most_common(15))},
        "rafturi": rafturi,
        "rafturi_pentru_90_la_suta": pentru_90,
        "rafturi_cu_nod": sum(1 for r in rafturi if r["procent"] >= PRAG_NOD),
        "asocieri": asocieri,
        "asocieri_peste": {f"{prag}x": sum(1 for a in asocieri if a["asociere"] > prag) for prag in PRAGURI_ASOCIERE},
    }
    if veche is not None:
        rezultat["schimbari"] = {
            "total": sum(schimbari.values()),
            "cuvinte_diferite": len({c for c, _, _ in schimbari}),
            "din_umplutura": sum(n for (_, inainte, _), n in schimbari.items() if inainte == UMPLUTURA),
            "pe_reguli": dict(pe_reguli.most_common()),
            "cele_mai_dese": [{"cuvant": c, "de_la": a, "la": b, "de_ori": n}
                              for (c, a, b), n in schimbari.most_common(40)],
        }
    return rezultat


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Încărcarea rafturilor WordNet pe TinyStories.")
    parser.add_argument("--biblioteca", default="date/biblioteca.json.gz")
    parser.add_argument("--date", default="date/tinystories", help="dosarul datelor TinyStories")
    parser.add_argument("--sens-dupa-context", action="store_true",
                        help="regulile a, b, c ale memoriei (verbe, nume, adverbe), comparat cu măsurătoarea fără ele")
    args = parser.parse_args(argv)

    from module.date_tinystories import DateTinyStories

    text = DateTinyStories(director=args.date).text_antrenare()
    rezultat = masoara(
        text,
        MemorieIerarhica(args.biblioteca, fara_cuvinte_de_legatura=True, sens_dupa_context=args.sens_dupa_context),
        bruta=MemorieIerarhica(args.biblioteca),
        veche=MemorieIerarhica(args.biblioteca, fara_cuvinte_de_legatura=True) if args.sens_dupa_context else None,
    )
    u = rezultat["umplutura"]
    print(f"TinyStories (antrenare): {rezultat['cuvinte']:,} cuvinte")
    print(f"  umplutură: {u['total']:,} ({u['total'] / rezultat['cuvinte']:.1%}): negăsite {u['negasite']:,}, "
          f"de legătură {u['de_legatura']:,}")
    print(f"  cuvinte cu sens: {rezultat['cu_sens']:,} ({rezultat['cu_sens'] / rezultat['cuvinte']:.1%})")
    print("  cuvinte de legătură pe care WordNet le avea cu alt sens: "
          + ", ".join(f"{c} {n:,}" for c, n in u["de_legatura_cu_alt_sens_in_wordnet"].items()))
    if "schimbari" in rezultat:
        s = rezultat["schimbari"]
        print(f"\nSens după context. Lista fixă de adverbe (regula c): {', '.join(sorted(ADVERBE_PREFERATE))}")
        print(f"Și-au schimbat raftul față de măsurătoarea fără reguli: {s['total']:,} cuvinte "
              f"({s['total'] / rezultat['cuvinte']:.1%} din toate; {s['cuvinte_diferite']:,} cuvinte diferite), "
              f"din care {s['din_umplutura']:,} erau umplutură")
        print("  pe reguli: " + ", ".join(f"{r} {n:,}" for r, n in s["pe_reguli"].items()))
        print("  cele mai dese schimbări:")
        for x in s["cele_mai_dese"]:
            print(f"    {x['cuvant']:<12} {x['de_la']:<20} → {x['la']:<20} {x['de_ori']:>7,}")
    print(f"\n{'raft':<22} {'cuvinte':>9} {'%':>6} {'% cumulat':>9}  cele mai dese")
    for r in rezultat["rafturi"]:
        print(f"{r['raft']:<22} {r['cuvinte']:>9,} {r['procent']:>6.1%} {r['procent_cumulat']:>9.1%}  {', '.join(r['exemple'])}")
    print(f"\nRafturi care acoperă 90% din cuvintele cu sens: {rezultat['rafturi_pentru_90_la_suta']} "
          f"din {len(rezultat['rafturi'])}")
    print(f"Rafturi cu cel puțin {PRAG_NOD:.1%} din cuvintele cu sens (un nod fiecare): {rezultat['rafturi_cu_nod']}; "
          f"restul ({len(rezultat['rafturi']) - rezultat['rafturi_cu_nod']}) ar merge la nodul „rar”")
    print(f"\nCele mai puternice 20 de asocieri (cuvinte vecine, cu ordine, perechi văzute de cel puțin {MINIM_PERECHE} ori):")
    for a in rezultat["asocieri"][:20]:
        print(f"  {a['de_la']:<20} → {a['la']:<20} {a['asociere']:6.2f}×  ({a['apar']:,} de ori)")
    print(f"Perechi măsurate: {len(rezultat['asocieri'])}; cu asocierea peste "
          + ", ".join(f"{p}: {n}" for p, n in rezultat["asocieri_peste"].items()))

    nume = "rafturi_tinystories_context.json" if args.sens_dupa_context else "rafturi_tinystories.json"
    iesire = Path("lucru") / nume
    iesire.parent.mkdir(parents=True, exist_ok=True)
    iesire.write_text(json.dumps(rezultat, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSalvat în {iesire}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
