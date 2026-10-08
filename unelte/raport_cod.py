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

LINII = ("A", "B", "D")


def citeste_jsonl(cale: Path) -> list[dict[str, Any]]:
    if not cale.exists():
        return []
    return [json.loads(r) for r in cale.read_text(encoding="utf-8").splitlines() if r.strip()]


def procent(x: float | None) -> str:
    return "—" if x is None else f"{x:.0%}"


CATEGORII = (("SyntaxError", "nu e Python valid"), ("IndentationError", "nu e Python valid"),
             ("NameError", "nume necunoscute (de ex. cuvinte din povești)"), ("a ieșit", "alt rezultat"),
             ("rezultat corect, dar", "rezultat corect, fără forma cerută"), ("a depășit timpul", "timp depășit"))


def categoria(respins: dict[str, Any]) -> str:
    """De ce a picat o încercare, în câteva cuvinte."""
    if respins["verdict"] == "trișat":
        return "prinse trișând"
    for inceput, nume in CATEGORII:
        if respins["motiv"].startswith(inceput):
            return nume
    if respins["motiv"].startswith("<w>"):  # Python a dat întâi un avertisment (ex. la `9(2)`), apoi eroarea
        return "eroare la rulare"
    return respins["motiv"].split(":")[0]  # alt fel de eroare (ex. TypeError)


def scurt(cod: str, n: int = 70) -> str:
    text = cod.replace("\n", " ⏎ ").replace("|", "¦").replace("`", "'")
    return (text[:n] + "…") if len(text) > n else text


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
                    f"*Scris la {datetime.now():%Y-%m-%d %H:%M}, din lucru/{cod.name}/runde.jsonl ({len(jurnal)} rânduri, "
                    f"{sum(len(v) for v in runde.values())} runde) și lucru/{cod.name}/stare.json.*\n"]
    pornire_pilot = next((r for r in reversed(jurnal) if r.get("tip") == "pilot_inceput"), None)
    if pornire_pilot:
        o.append(f"Versiunea {pornire_pilot.get('versiune', 'v0.1')}, în lucru/{cod.name}"
                 + (f"; {pornire_pilot['fractie_povesti']:.0%} povești în fiecare lot de antrenare"
                    if pornire_pilot.get("fractie_povesti") else "") + ".\n")
    variante = sorted({(r.get("regula"), r.get("episoade")) for r in jurnal if r.get("tip") == "nivel_inceput"},
                      key=str)
    descriere = {"scurta": "regula scurtată", "lunga": "regula lungă (preambulul)", "fara": "fără regulă"}
    if variante:
        o.append("Textul din fața modelului: " + "; ".join(
            f"{descriere.get(regula, regula)} + {episoade} exemple + sarcina" for regula, episoade in variante) + ".\n")

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
    cale_sacru = RADACINA / "date" / "cod" / "sacru.json"
    fara_sacru = {n for n, lista in json.loads(cale_sacru.read_text(encoding="utf-8"))["niveluri"].items() if not lista} \
        if cale_sacru.exists() else set()
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
                sacru = None if nivel in fara_sacru else info.get("sacru")  # 0a n-are set sacru (v0.2 a scris 0%)
                celule.append(f"{semn} {procent(info.get('vazut'))} / {procent(info.get('nevazut'))} / "
                              f"{procent(info.get('adversarial'))} / {procent(sacru)}")
            elif runde.get((linie, nivel)):
                u = runde[(linie, nivel)][-1]
                celule.append(f"{semn} {procent(u['rata_vazut'])} / {procent(u['rata_nevazut'])} / — / —")
            else:
                celule.append("—")
        o.append(f"| {nivel} | " + " | ".join(celule) + " |")
    o.append("")

    # --- liniile pe aceleași runde: singura comparație curată
    comune = [n for n in niveluri if sum(bool(runde.get((l, n))) for l in linii) >= 2]
    if comune:
        o.append("## Liniile pe aceleași runde (A, B" + (", D" if "D" in linii else "") + ")\n")
        o.append("La aceeași rundă, liniile au aceleași sarcini, aceleași texte din față și aceleași semințe. Diferă doar "
                 "textul de antrenare:\n- A: doar abecedarul;\n- B: abecedarul și propriile reușite;"
                 + ("\n- D: abecedarul și tot atâtea soluții corecte câte a găsit B în aceeași rundă, date de unealtă "
                    "(sarcini văzute alese la întâmplare), nu descoperite de D." if "D" in linii else "")
                 + "\n\nUn set de 20 de sarcini are o eroare de aproximativ ±11 puncte pe măsurare (o abatere standard, "
                   "la 50%); unul de 4 sarcini (0a), de ±25.\n")
        for nivel in comune:
            cu = [l for l in linii if runde.get((l, nivel))]
            lung = max(len(runde[(l, nivel)]) for l in cu)
            n = min(lung, 12)
            celule = []
            for i in range(n):
                valori = [procent(runde[(l, nivel)][i]["rata_nevazut"]) if i < len(runde[(l, nivel)]) else "—" for l in cu]
                celule.append(f"{i + 1}: {' / '.join(valori)}")
            dupa = [f"{l} a mai avut {len(runde[(l, nivel)]) - n} runde (cel mai bun: "
                    f"{procent(max(r['rata_nevazut'] for r in runde[(l, nivel)][n:]))})"
                    for l in cu if len(runde[(l, nivel)]) > n]
            o.append(f"- Nivelul {nivel}, nevăzut pe runde ({' / '.join(cu)}): " + ", ".join(celule)
                     + (f"; apoi {'; '.join(dupa)}" if dupa else "") + ".")
            if "B" in cu and "D" in cu:
                bb, dd = runde[("B", nivel)], runde[("D", nivel)]
                primite = sum(r.get("de_la_unealta", 0) for r in dd)
                cerute = sum(r.get("cerute_de_la_unealta", 0) for r in dd)
                o.append(f"  - B față de D la {nivel}: B a trecut în runda {bb[-1]['runda']} " if
                         stari.get("B", {}).get("niveluri_trecute", {}).get(nivel) else f"  - B față de D la {nivel}: ")
                o[-1] += (f"D a primit de la unealtă {primite} soluții din {cerute} câte a găsit B"
                          + (" (n-au mai rămas sarcini văzute noi pentru restul)" if primite < cerute else "") + ".")
        o.append("")

    # --- pregătirea
    pregatire = stare.get("pregatire")
    if pregatire:
        o.append("## Pregătirea (din #252, pe abecedar)\n")
        if pregatire.get("pierdere_abecedar"):
            pierderi = pregatire["pierdere_abecedar"]
            o.append(f"Pierderea pe abecedar (nats pe simbol), măsurată la fiecare câțiva pași: "
                     + ", ".join(f"{pas}: {v}" for pas, v in pierderi) + f"; ținta {pregatire.get('pierdere_tinta')}"
                     + (" atinsă." if pierderi[-1][1] <= (pregatire.get("pierdere_tinta") or 0) else " neatinsă.")
                     + (f" {pregatire['fractie_povesti']:.0%} povești în fiecare lot." if pregatire.get("fractie_povesti")
                        else ""))
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

    # --- placa: rundele în care a mers mai încet (ex. alimentarea care sare: P8, 210 MHz pe 8 octombrie)
    o.append("## Placa video\n")
    toate = [r for rr in runde.values() for r in rr]
    citite = [r for r in toate if r.get("placa")]
    incete = [r for r in citite if r["placa"].get("treapta") != "P0" or (r["placa"].get("mhz") or 0) < 1000]
    durate = [r["secunde"] for r in toate]
    if citite:
        o.append(f"Citită după {len(citite)} din {len(toate)} runde: frecvența între "
                 f"{min(r['placa']['mhz'] for r in citite)} și {max(r['placa']['mhz'] for r in citite)} MHz; "
                 f"o rundă a durat între {min(durate):.0f} și {max(durate):.0f} s. "
                 + (f"**{len(incete)} runde cu placa încetinită** (nu în P0 sau sub 1000 MHz): "
                    + ", ".join(f"{r['linie']} {r['nivel']} runda {r['runda']}" for r in incete[:10])
                    if incete else "Nicio rundă cu placa încetinită."))
    else:
        o.append("Necitită.")
    alimentare = [r for r in jurnal if r.get("tip") in ("alimentare", "racire")]
    o.extend(f"- {r['timp']} {r['tip']}: {r['motiv']}" for r in alimentare)
    o.append("")

    # --- trișatul
    o.append("## Încercări prinse trișând\n")
    total = sum(r["trisate"] for rr in runde.values() for r in rr)
    din = sum(r["incercari"] for rr in runde.values() for r in rr)
    o.append(f"În total: {total} din {din} de încercări ({procent(total / din if din else None)}). Ele nu se rulează și "
             f"nu intră niciodată în antrenare.")
    respinse = {l: citeste_jsonl(cod / "respinse" / f"{l}.jsonl") for l in LINII}
    for (linie, nivel), rr in sorted(runde.items(), key=lambda k: (ordinea(k[0][1]), k[0][0])):
        t = sum(r["trisate"] for r in rr)
        raportate = [r["runda"] for r in rr if r.get("trisat_raportat")]
        if t:
            motive = Counter(m for r in rr for m in r.get("exemple_trisate", []))
            exemple = [r["cod"] for r in respinse[linie] if r["nivel"] == nivel and r["verdict"] == "trișat"][:2]
            o.append(f"- {linie} {nivel}: {t} din {sum(r['incercari'] for r in rr)}"
                     + (f"; runde cu peste 50% trișat: {', '.join(map(str, raportate))}" if raportate else "")
                     + (f"; motivele: {'; '.join(m for m, _ in motive.most_common(3))}" if motive else "")
                     + (f"; de exemplu: {'; '.join(f'`{scurt(c)}`' for c in exemple)}" if exemple else ""))
    o.append("")

    # --- primele reușite
    o.append("## Primele reușite pe văzut\n")
    for (linie, nivel), rr in sorted(runde.items(), key=lambda k: (ordinea(k[0][1]), k[0][0])):
        prima = next((r for r in rr if r["trecute"]), None)
        o.append(f"- {linie} {nivel}: " + (f"runda {prima['runda']} ({prima['trecute']} din {prima['incercari']}), de "
                                           f"exemplu `{scurt(prima['exemple_trecute'][0])}`"
                                           if prima and prima.get("exemple_trecute") else "niciuna"))
    o.append("")

    # --- forme noi
    o.append("## Soluții cu o formă care nu e în abecedar\n")
    o.append("„Formă” = codul cu numerele, cuvintele și numele cutiilor puse deoparte („x = 7” → „V = N”). Fiecare formă "
             "nouă apare o singură dată, cu prima soluție și runda la care a apărut.\n")
    for linie in LINII:
        intrari = biblioteci[linie]
        if not intrari and linie not in linii:
            continue
        if not intrari and linie == "D" and not (cod / "biblioteca_unealta_D.jsonl").exists() and linie not in linii:
            continue
        prime: dict[str, dict[str, Any]] = {}
        for i in sorted(intrari, key=lambda i: (ordinea(i["nivel"]), i["runda"])):
            if i["forma_noua"] and i["schelet"] not in prime:
                prime[i["schelet"]] = i
        o.append(f"**Linia {linie}** ({'se antrenează pe ele' if linie == 'B' else 'biblioteca se umple, dar nu se antrenează pe ea'}): "
                 f"{len(intrari)} reușite unice, {sum(i['forma_noua'] for i in intrari)} cu formă nouă, "
                 f"{len(prime)} forme noi diferite.")
        if linie == "D":
            unealta = citeste_jsonl(cod / "biblioteca_unealta_D.jsonl")
            pe_nivel = Counter(i["nivel"] for i in unealta)
            o.append("Linia D se antrenează pe soluțiile date de unealtă: " + (", ".join(
                f"{n}: {pe_nivel[n]}" for n in sorted(pe_nivel, key=ordinea)) if unealta else "niciuna") + ".")
        if prime:
            o.append("\n| Nivel | Runda | Sarcina | Codul (formă nouă) |\n|---|---|---|---|")
            for i in list(prime.values())[:15]:
                o.append(f"| {i['nivel']} | {i['runda']} | {i['test']} | `{scurt(i['cod'])}` |")
        if intrari:  # sarcinile văzute nu sunt din abecedar: fiecare soluție de aici e găsită de model, nu copiată
            o.append(f"\nPrimele soluții găsite de linia {linie} (niciuna nu e în abecedar), cu runda:\n\n"
                     "| Nivel | Runda | Sarcina | Codul |\n|---|---|---|---|")
            for i in sorted(intrari, key=lambda i: (ordinea(i["nivel"]), i["runda"]))[:8]:
                o.append(f"| {i['nivel']} | {i['runda']} | {i['test']} | `{scurt(i['cod'])}` |")
            pe_nivel = Counter(i["nivel"] for i in intrari)
            ultima_crestere = {n: max(i["runda"] for i in intrari if i["nivel"] == n) for n in pe_nivel}
            o.append("\nPe niveluri: " + ", ".join(f"{n}: {pe_nivel[n]} soluții, ultima nouă în runda {ultima_crestere[n]}"
                                                   for n in sorted(pe_nivel, key=ordinea)) + ".")
        o.append("")

    # --- ce știa
    o.append("## Ce a rămas din povești\n")
    randuri = []
    if pregatire and pregatire.get("povesti_bpo_inainte") is not None:
        randuri.append(f"- #252, înainte de școală: {pregatire['povesti_bpo_inainte']}; după pregătire: "
                       f"{pregatire['povesti_bpo_dupa']}" + (" (peste prag: regresie)"
                                                             if pregatire.get("regresie_povesti") else ""))
    for linie in linii:
        sl = stari.get(linie, {})
        for nivel, info in sorted({**sl.get("niveluri_trecute", {}), **sl.get("niveluri_picate", {})}.items(),
                                  key=lambda kv: ordinea(kv[0])):
            if info.get("povesti_bpo") is not None:
                randuri.append(f"- {linie}, la înghețul „{info['inghet']}”: {info['povesti_bpo']}"
                               + (" (peste prag: regresie)" if info.get("regresie_povesti") else ""))
    o.extend(randuri or ["Nemăsurat încă."])
    o.append("\nBiți pe octet pe aceeași bucată din validarea poveștilor (mai mic = mai bine). Faptele (cele 72 ale lui "
             "#252) nu se măsoară în buclă.\n")
    pornire = pregatire.get("povesti_bpo_inainte") if pregatire else None
    finale = [info["povesti_bpo"] for l in linii for c in ("niveluri_trecute", "niveluri_picate")
              for info in stari.get(l, {}).get(c, {}).values() if info.get("povesti_bpo") is not None]
    if pornire and finale:
        o.append(f"Cel mai rău: {max(finale)}, adică de {max(finale) / pornire:.1f} ori biții lui #252 ({pornire}).\n")

    # --- curățarea bibliotecii (v0.3, lecția SANDBOX-7)
    curatari = [r for r in jurnal if r.get("tip") == "curatare"]
    if curatari:
        o.append("## Biblioteca curățată după corectitudine (la regresie)\n")
        o.append("Fiecare soluție din bibliotecă, mutată pe sarcinile nevăzute de aceeași formă ale nivelului ei; cele care "
                 "pică ies în respinse/curatare_<linie>.jsonl.\n")
        for r in curatari:
            o.append(f"- {r['timp']} linia {r['linie']}, la regresia după {r['nivel']}: {r['scoase']} soluții scoase"
                     + ("; de exemplu " + "; ".join(f"„{e['test']}” → `{scurt(e['cod'])}`" for e in r["exemple"][:3])
                        if r.get("exemple") else "") + ".")
        o.append("")

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
            picate_aici = [r for r in respinse[linie] if r["nivel"] == nivel]
            if picate_aici:
                categorii = Counter(categoria(r) for r in picate_aici)
                ultima = max(r["runda"] for r in picate_aici)
                exemple = [r for r in picate_aici if r["runda"] == ultima][:3]
                o.append("  - De ce au picat încercările: " + ", ".join(
                    f"{nume} {n / len(picate_aici):.0%}" for nume, n in categorii.most_common(5)) + ".")
                o.append(f"  - Ce scria modelul în ultima rundă ({ultima}): " + "; ".join(
                    f"„{r['test']}” → `{scurt(r['cod'])}`" for r in exemple) + ".")
    picate = {n for l in linii for n in stari.get(l, {}).get("niveluri_picate", {})}
    if picate:
        variante = ["ce s-ar putea schimba (decide omul):"]
        if pornire and finale and max(finale) > 1.1 * pornire:
            variante.append(f"hrană din povești în antrenarea școlii, ca hrana din 6a care a păstrat faptele (poveștile au "
                            f"ajuns de la {pornire} la {max(finale)} biți pe octet)")
        for linie in linii:
            for nivel in stari.get(linie, {}).get("niveluri_picate", {}):
                rr = runde.get((linie, nivel), [])
                if len(rr) >= 6:
                    cel_mai_bun = max(rr, key=lambda r: r["rata_nevazut"])
                    final = sum(r["rata_nevazut"] for r in rr[-5:]) / 5
                    if cel_mai_bun["runda"] <= len(rr) // 3 and cel_mai_bun["rata_nevazut"] - final >= 0.1:
                        variante.append(f"mai puțini pași pe rundă sau o rată mai mică la {linie} {nivel} (cel mai bun "
                                        f"nevăzut, {procent(cel_mai_bun['rata_nevazut'])}, a fost în runda "
                                        f"{cel_mai_bun['runda']}; în ultimele 5 runde, în medie {procent(final)})")
                    vazut = sum(r["rata_vazut"] for r in rr[-5:]) / 5
                    if vazut - final >= 0.25:
                        variante.append(f"sarcini văzute mai multe și mai variate la {linie} {nivel} (în ultimele 5 "
                                        f"runde: văzut {procent(vazut)}, nevăzut {procent(final)}: a învățat sarcinile "
                                        f"văzute, nu regula)")
        variante.append("un abecedar mai mare la " + ", ".join(sorted(picate, key=ordinea)) + "; trepte intermediare "
                        "(de ex. numere mici, apoi mari); un vocabular nou sau o linie de la zero, cu povești și cod "
                        "(Kronos-Code-Zero); liniile C și D din plan (D: contează descoperirea sau doar expunerea "
                        "la mai multe exemple?)")
        o.append("- " + variante[0].capitalize() + "\n" + ";\n".join(f"  - {v}" for v in variante[1:]) + ".")
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
    parser.add_argument("--dosar", default="cod", help="dosarul versiunii școlii, în lucru/ (v0.1: cod, v0.2: cod_v02)")
    args = parser.parse_args(argv)
    cod = Path(args.director_lucru) / args.dosar
    text = raport(cod)
    if cod.exists():
        (cod / "raport.md").write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
