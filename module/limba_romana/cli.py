"""Linia de comandă a motorului. Exemple:

    python -m module.limba_romana analizeaza "Copiii frumoși au plecat la școală."
    python -m module.limba_romana verifica "Copii frumoasă a plecat."
    python -m module.limba_romana forma casei
    python -m module.limba_romana lema casă
    python -m module.limba_romana forme casă NOUN
    python -m module.limba_romana sensuri carte
    python -m module.limba_romana explica "Am văzut o fată." 3
    python -m module.limba_romana reguli acord
    python -m module.limba_romana statistici
    python -m module.limba_romana integritate
    python -m module.limba_romana acoperire [--fisier raport.json]
    python -m module.limba_romana exporta director_export [--sursa ud_rrt]
"""

from __future__ import annotations

import argparse
import json
import sys

from .motor import Motor


def _json(obiect) -> str:
    return json.dumps(obiect, ensure_ascii=False, indent=1, default=str)


def _tipareste_analiza(rez: dict) -> None:
    for d in rez["propozitii"]:
        print(f"Propoziție: {d['text']}")
        for c in d["cuvinte"]:
            ales = c["candidati"][c["ales"]] if c["ales"] is not None and c["candidati"] else None
            if ales is None:
                print(f"  {c['idx']:>2}. {c['text']}")
                continue
            tr = ales["trasaturi"]
            print(f"  {c['idx']:>2}. {c['text']:<16} {ales['pos']:<6} lema={ales['lema']:<14} {'|'.join(f'{k}={v}' for k, v in sorted(tr.items()))}"
                  f"  [{ales['incredere']}{'/' + ales['statut'] if ales['statut'] else ''}] cap={c['cap']} {c['rel']}{'  AMBIGUU' if c['ambiguu'] else ''}")
        if d.get("roluri"):
            print("  Roluri: " + "; ".join(f"{r['text']} → {r['rol']} ({r['verb_text']})" for r in d["roluri"]))
        for idx, s in (d.get("sensuri") or {}).items():
            if s["ales"]:
                print(f"  Sens „{s['text']}”: {s['ales']['definitie'][:100]} — dovezi: {', '.join(s['ales']['dovezi'][:3])}")
        for p in d["probleme"]:
            print(f"  ! {p['tip']}: {p['mesaj']}" + (f" Sugestie: {p['sugestie']}" if p.get("sugestie") else "") + f" [{p['regula']}, {p['certitudine']}]")
        for a in d["ambiguitati"]:
            print(f"  ? ambiguitate la „{a['text']}”: " + ", ".join(f"{l} ({pos}, {sc})" for l, pos, sc in a["variante"]))
        for alt in d["analize_alternative"]:
            print(f"  ~ {alt['motiv']}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python -m module.limba_romana", description="Romanian Language Core — motorul lingvistic simbolic pentru limba română")
    p.add_argument("--baza", default=None, help="fișierul SQLite al bazei (implicit: _baza/limba_romana.sqlite)")
    p.add_argument("--json", action="store_true", help="rezultatul în JSON")
    sub = p.add_subparsers(dest="comanda", required=True)
    sub.add_parser("analizeaza", help="analiza completă a unui text").add_argument("text")
    sub.add_parser("verifica", help="greșelile de acord, numeralele, necunoscutele").add_argument("text")
    sub.add_parser("forma", help="analizele unei forme").add_argument("forma")
    s = sub.add_parser("lema", help="lexemele unei leme"); s.add_argument("lema"); s.add_argument("pos", nargs="?")
    s = sub.add_parser("forme", help="formele unui lexem"); s.add_argument("lema"); s.add_argument("pos", nargs="?")
    s = sub.add_parser("sensuri", help="sensurile și conceptele unui cuvânt"); s.add_argument("lema"); s.add_argument("pos", nargs="?")
    s = sub.add_parser("explica", help="de ce a ales motorul analiza unui cuvânt"); s.add_argument("text"); s.add_argument("pozitie", type=int)
    sub.add_parser("reguli", help="regulile explicite").add_argument("tip", nargs="?")
    sub.add_parser("statistici", help="statisticile bazei")
    sub.add_parser("integritate", help="verificarea integrității bazei")
    sub.add_parser("acoperire", help="raportul de acoperire").add_argument("--fisier", default=None)
    s = sub.add_parser("exporta", help="exportă baza în JSONL"); s.add_argument("director"); s.add_argument("--sursa", default=None)
    a = p.parse_args(argv)
    m = Motor(a.baza)
    try:
        if a.comanda == "analizeaza":
            rez = m.analizeaza(a.text)
            print(_json(rez)) if a.json else _tipareste_analiza(rez)
        elif a.comanda == "verifica":
            rez = m.verifica_text(a.text)
            if a.json:
                print(_json(rez))
            else:
                print(f"{rez['numar_probleme']} probleme")
                for pr in rez["probleme"]:
                    print(f"  ! {pr['tip']}: {pr['mesaj']}" + (f" Sugestie: {pr['sugestie']}" if pr.get("sugestie") else "") + f" [{pr['regula']}, {pr['certitudine']}]")
                for n in rez["necunoscute"]:
                    print(f"  ? {n['text']}: {n['stare']} — {'; '.join(n['detalii'][:2])}")
        elif a.comanda == "forma":
            rez = m.analiza_morfologica(a.forma)
            if a.json:
                print(_json(rez))
            else:
                for r in rez:
                    print(f"  {r['pos']:<6} lema={r['lema']:<16} {'|'.join(f'{k}={v}' for k, v in sorted(r['trasaturi'].items()))}  [{r['incredere']}{'/' + r['statut'] if r['statut'] else ''}] {'; '.join(r['dovezi'][:2])}")
        elif a.comanda == "lema":
            print(_json(m.cauta_lema(a.lema, a.pos)))
        elif a.comanda == "forme":
            rez = m.forme_lema(a.lema, a.pos)
            if a.json:
                print(_json(rez))
            else:
                for r in rez:
                    lx = r["lexem"]
                    print(f"{lx['lema']} ({lx['pos']}, gen={lx['gen']}, omonim={lx['omonim']}, id={lx['id']})")
                    for f in r["forme"]:
                        print(f"  {f['forma']:<20} {f['trasaturi']:<70} {f['statut']:<8} {', '.join(sorted({p['sursa_id'] for p in f['provenienta']}))}")
        elif a.comanda == "sensuri":
            rez = m.sensuri(a.lema, a.pos)
            if a.json:
                print(_json(rez))
            else:
                for r in rez:
                    print(f"{r['lexem']['lema']} ({r['lexem']['pos']}, omonim {r['lexem']['omonim']})")
                    for s_ in r["sensuri"]:
                        print(f"  [{s_['sursa']}] {s_['definitie']}" + (f"  sinonime: {', '.join(s_['sinonime'][:6])}" if s_.get("sinonime") else ""))
        elif a.comanda == "explica":
            print(_json(m.explica(a.text, a.pozitie)))
        elif a.comanda == "reguli":
            for r in m.reguli(a.tip):
                print(f"  [{r['tip']}/{r['statut']}] {r['nume']}: {r['descriere']}")
        elif a.comanda == "statistici":
            print(_json(m.statistici()))
        elif a.comanda == "integritate":
            rez = m.integritate()
            print(_json(rez))
            return 0 if rez["ok"] else 1
        elif a.comanda == "acoperire":
            rez = m.acoperire()
            text = _json(rez)
            if a.fisier:
                with open(a.fisier, "w", encoding="utf8") as f:
                    f.write(text)
                print(f"raport scris în {a.fisier}")
            else:
                print(text)
        elif a.comanda == "exporta":
            print(_json(m.exporta(a.director, a.sursa)))
    finally:
        m.inchide()
    return 0


if __name__ == "__main__":
    sys.exit(main())
