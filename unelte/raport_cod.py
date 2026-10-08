"""Raportul școlii de cod (planul, secțiunea 10), din jurnalul lucru/cod/runde.jsonl, starea și bibliotecile.

Ce scoate:
- unde se rupe lanțul, pe fiecare linie;
- tabelul nivel × linie (văzut / nevăzut / adversarial / sacru);
- pregătirea (nevăzut înainte și după, poveștile);
- timpul pe nivel;
- temperatura pe runde;
- încercările prinse trișând;
- primele soluții găsite de B (și de A) cu o formă care nu e în abecedar, cu runda la care au apărut;
- ce a rămas din povești (biți pe octet) la fiecare îngheț;
- înghețurile și rollback-urile;
- observații, fără decizii: ce ar putea schimba omul.

Rezultatele slabe se raportează la fel ca cele bune.

    python unelte/raport_cod.py                # scrie și lucru/cod/raport.md
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from module.cod import ordinea  # noqa: E402

LINII = ("A", "B")


def citeste_jsonl(cale: Path) -> list[dict[str, Any]]:
    if not cale.exists():
        return []
    return [json.loads(r) for r in cale.read_text(encoding="utf-8").splitlines() if r.strip()]


def procent(x: float | None) -> str:
    return "—" if x is None else f"{x:.0%}"


def comprima(valori: list[float]) -> str:
    """1,0 1,0 0,7 0,5 0,5 → „1 ×2 → 0.7 ×1 → 0.5 ×2”."""
    grupuri: list[list[Any]] = []
    for v in valori:
        if grupuri and grupuri[-1][0] == v:
            grupuri[-1][1] += 1
        else:
            grupuri.append([v, 1])
    return " → ".join(f"{v:g} ×{n}" for v, n in grupuri)


def raport(cod: Path) -> str:
    jurnal = citeste_jsonl(cod / "runde.jsonl")
    stare = json.loads((cod / "stare.json").read_text(encoding="utf-8")) if (cod / "stare.json").exists() else {}
    stari = stare.get("linii", {})
    runde: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for r in jurnal:
        if r.get("tip") == "runda":
            runde[(r["linie"], r["nivel"])].append(r)
    linii = [l for l in LINII if l in stari or any(k[0] == l for k in runde)]
    niveluri = sorted({n for _, n in runde} | {n for l in linii for c in ("niveluri_trecute", "niveluri_picate")
                                                for n in stari.get(l, {}).get(c, {})}, key=ordinea)
    biblioteci = {l: citeste_jsonl(cod / f"biblioteca_{l}.jsonl") for l in LINII}
    o: list[str] = [f"# Școala de cod: raportul\n",
                    f"*Scris la {datetime.now():%Y-%m-%d %H:%M}, din lucru/cod/runde.jsonl ({len(jurnal)} rânduri, "
                    f"{sum(len(v) for v in runde.values())} runde) și lucru/cod/stare.json.*\n"]

    def oprire(linie: str) -> dict[str, Any] | None:
        """Ultima oprire de paznic/STOP a liniei, dacă a venit după ultima ei rundă."""
        ultima = None
        for r in jurnal:
            if r.get("linie") == linie and r.get("tip") in ("oprit", "runda", "nivel_trecut", "nivel_picat", "regresie"):
                ultima = r
        return ultima if ultima and ultima["tip"] == "oprit" else None

    # --- unde se rupe lanțul
    o.append("## Unde se rupe lanțul\n")
    if not linii:
        o.append("Nicio rundă încă.\n")
    for linie in linii:
        sl = stari.get(linie, {})
        trecute = sorted(sl.get("niveluri_trecute", {}), key=ordinea)
        picate = sl.get("niveluri_picate", {})
        text = f"- **Linia {linie}:** " + (f"a trecut {', '.join(trecute)}" if trecute else "n-a trecut niciun nivel")
        if picate:
            nivel, info = next(iter(picate.items()))
            text += (f"; **s-a rupt la {nivel}**: buget epuizat ({info['runde']} runde, {info['secunde'] / 60:.0f} "
                     f"minute), cu nevăzut {procent(info['nevazut'])} la ultima rundă")
        elif sl.get("oprita"):
            text += f"; **oprită**: {sl.get('motiv_oprire')}"
        elif sl.get("nivel_curent"):
            opr = oprire(linie)
            text += f"; în lucru la {sl['nivel_curent']}" + (f" ({opr['motiv']})" if opr else "")
        o.append(text + ".")
    o.append("")

    # --- tabelul
    o.append("## Nivel × linie\n")
    o.append("Văzut și nevăzut: la runda în care s-a trecut nivelul, sau la ultima rundă. Adversarial și sacru: doar la "
             "îngheț (nivel trecut sau picat), doar pentru raport, niciodată la selecție. ✓ trecut, ✗ picat, … în lucru."
             "\n")
    o.append("| Nivel | " + " | ".join(f"{l}: văzut / nevăzut / advers. / sacru" for l in linii) + " |")
    o.append("|---|" + "---|" * len(linii))
    for nivel in niveluri:
        celule = []
        for linie in linii:
            sl = stari.get(linie, {})
            info = sl.get("niveluri_trecute", {}).get(nivel) or sl.get("niveluri_picate", {}).get(nivel)
            semn = "✓" if nivel in sl.get("niveluri_trecute", {}) else "✗" if nivel in sl.get("niveluri_picate", {}) \
                else "…" if runde.get((linie, nivel)) else ""
            if info:
                celule.append(f"{semn} {procent(info.get('vazut'))} / {procent(info.get('nevazut'))} / "
                              f"{procent(info.get('adversarial'))} / {procent(info.get('sacru'))}")
            elif runde.get((linie, nivel)):
                u = runde[(linie, nivel)][-1]
                celule.append(f"{semn} {procent(u['rata_vazut'])} / {procent(u['rata_nevazut'])} / — / —")
            else:
                celule.append("—")
        o.append(f"| {nivel} | " + " | ".join(celule) + " |")
    o.append("")

    # --- pregătirea
    pregatire = stare.get("pregatire")
    if pregatire:
        o.append("## Pregătirea (din #252, pe abecedar)\n")
        o.append(f"{pregatire['pasi']} de pași, rata {pregatire['rata']:g}, pierderea la final {pregatire['pierdere']}. "
                 "Nevăzut înainte → după: " + ", ".join(
                     f"{n} {procent(pregatire['nevazut_inainte'][n])} → {procent(pregatire['nevazut_dupa'][n])}"
                     for n in sorted(pregatire["nevazut_inainte"], key=ordinea)) + ".")
        if pregatire.get("povesti_bpo_inainte") is not None:
            o.append(f"Povești (biți pe octet, mai mic = mai bine): {pregatire['povesti_bpo_inainte']} → "
                     f"{pregatire['povesti_bpo_dupa']}.")
        o.append("")

    # --- timpul și temperatura
    o.append("## Timpul pe nivel\n")
    o.append("| Nivel | " + " | ".join(f"{l}: runde, minute" for l in linii) + " |")
    o.append("|---|" + "---|" * len(linii))
    for nivel in niveluri:
        celule = []
        for linie in linii:
            b = stari.get(linie, {}).get("buget", {}).get(nivel)
            celule.append(f"{b['runde']}, {b['secunde'] / 60:.1f}" if b else "—")
        o.append(f"| {nivel} | " + " | ".join(celule) + " |")
    o.append("")
    o.append("## Temperatura pe runde\n")
    for (linie, nivel), rr in sorted(runde.items(), key=lambda k: (ordinea(k[0][1]), k[0][0])):
        o.append(f"- {linie} {nivel}: {comprima([r['temperatura'] for r in rr])}")
    o.append("")

    # --- trișatul
    o.append("## Încercări prinse trișând\n")
    total = sum(r["trisate"] for rr in runde.values() for r in rr)
    din = sum(r["incercari"] for rr in runde.values() for r in rr)
    o.append(f"În total: {total} din {din} de încercări ({procent(total / din if din else None)}). Ele nu se rulează și "
             f"nu intră niciodată în antrenare.")
    for (linie, nivel), rr in sorted(runde.items(), key=lambda k: (ordinea(k[0][1]), k[0][0])):
        t = sum(r["trisate"] for r in rr)
        raportate = [r["runda"] for r in rr if r.get("trisat_raportat")]
        if t:
            motive = Counter(m for r in rr for m in r.get("exemple_trisate", []))
            o.append(f"- {linie} {nivel}: {t} din {sum(r['incercari'] for r in rr)}"
                     + (f"; runde cu peste 50% trișat: {', '.join(map(str, raportate))}" if raportate else "")
                     + (f"; de exemplu: {'; '.join(m for m, _ in motive.most_common(3))}" if motive else ""))
    o.append("")

    # --- forme noi
    o.append("## Soluții cu o formă care nu e în abecedar\n")
    o.append("„Formă” = codul cu numerele, cuvintele și numele cutiilor puse deoparte („x = 7” → „V = N”). Fiecare formă "
             "nouă apare o singură dată, cu prima soluție și runda la care a apărut.\n")
    for linie in LINII:
        intrari = biblioteci[linie]
        if not intrari and linie not in linii:
            continue
        prime: dict[str, dict[str, Any]] = {}
        for i in sorted(intrari, key=lambda i: (ordinea(i["nivel"]), i["runda"])):
            if i["forma_noua"] and i["schelet"] not in prime:
                prime[i["schelet"]] = i
        o.append(f"**Linia {linie}** ({'se antrenează pe ele' if linie == 'B' else 'biblioteca se umple, dar nu se antrenează pe ea'}): "
                 f"{len(intrari)} reușite unice, {sum(i['forma_noua'] for i in intrari)} cu formă nouă, "
                 f"{len(prime)} forme noi diferite.")
        if prime:
            o.append("\n| Nivel | Runda | Sarcina | Codul |\n|---|---|---|---|")
            for i in list(prime.values())[:15]:
                o.append(f"| {i['nivel']} | {i['runda']} | {i['test']} | `{i['cod'].replace(chr(10), ' ⏎ ')}` |")
        o.append("")

    # --- ce știa
    o.append("## Ce a rămas din povești\n")
    randuri = []
    if pregatire and pregatire.get("povesti_bpo_inainte") is not None:
        randuri.append(f"- #252, înainte de școală: {pregatire['povesti_bpo_inainte']}; după pregătire: "
                       f"{pregatire['povesti_bpo_dupa']}")
    for linie in linii:
        sl = stari.get(linie, {})
        for nivel, info in sorted({**sl.get("niveluri_trecute", {}), **sl.get("niveluri_picate", {})}.items(),
                                  key=lambda kv: ordinea(kv[0])):
            if info.get("povesti_bpo") is not None:
                randuri.append(f"- {linie}, la înghețul „{info['inghet']}”: {info['povesti_bpo']}")
    o.extend(randuri or ["Nemăsurat încă."])
    o.append("\nBiți pe octet pe aceeași bucată din validarea poveștilor (mai mic = mai bine). Faptele (cele 72 ale lui "
             "#252) nu se măsoară în buclă.\n")

    # --- înghețuri
    o.append("## Înghețuri și rollback-uri\n")
    evenimente = [r for r in jurnal if r.get("tip") in ("inghet", "rollback")]
    o.extend([f"- {r['timp']} {r['tip']}: {r['motiv']}" for r in evenimente] or ["Niciunul."])
    o.append("")

    # --- observații
    o.append("## Observații (fără decizii: alege omul)\n")
    for linie in linii:
        for nivel, info in stari.get(linie, {}).get("niveluri_picate", {}).items():
            rr = runde.get((linie, nivel), [])
            n = sum(r["incercari"] for r in rr) or 1
            cel_mai_bun = max(rr, key=lambda r: r["rata_nevazut"]) if rr else None
            o.append(f"- **{linie} {nivel}** (picat): pe văzut au trecut {sum(r['trecute'] for r in rr)} din {n} "
                     f"încercări; {sum(r['aproape'] for r in rr)} aveau rezultatul corect, dar nu forma cerută; "
                     f"{sum(r['fara_result'] for r in rr)} nu au ajuns la „RESULT:”; {sum(r['trisate'] for r in rr)} "
                     f"prinse trișând."
                     + (f" Cel mai bun nevăzut: {procent(cel_mai_bun['rata_nevazut'])}, în runda "
                        f"{cel_mai_bun['runda']}." if cel_mai_bun else ""))
    picate = {n for l in linii for n in stari.get(l, {}).get("niveluri_picate", {})}
    if picate:
        o.append("- Ce s-ar putea schimba (planul, secțiunea 12; decide omul): un abecedar mai mare la "
                 + ", ".join(sorted(picate, key=ordinea)) + "; trepte intermediare înainte de "
                 + ", ".join(sorted(picate, key=ordinea)) + "; un vocabular nou sau o linie de la zero, cu povești și "
                 "cod (Kronos-Code-Zero); textul din față (varianta 1 sau 2).")
    trecute = {l: stari.get(l, {}).get("niveluri_trecute", {}) for l in linii}
    if len(linii) == 2:
        comune = sorted(set(trecute["A"]) & set(trecute["B"]), key=ordinea)
        if comune:
            o.append("- Rundele până la trecere, A față de B: " + ", ".join(
                f"{n} {trecute['A'][n]['runda']} / {trecute['B'][n]['runda']}" for n in comune)
                + ". Dacă B urcă și A stă, feedback-ul mediului a produs ceva; dacă A ≈ B, progresul venea din "
                  "abecedar.")
    if o[-1].startswith("## Observații"):
        o.append("Niciuna încă.")
    return "\n".join(o) + "\n"


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Raportul școlii de cod.")
    parser.add_argument("--director-lucru", default=str(RADACINA / "lucru"))
    args = parser.parse_args(argv)
    cod = Path(args.director_lucru) / "cod"
    text = raport(cod)
    if cod.exists():
        (cod / "raport.md").write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
