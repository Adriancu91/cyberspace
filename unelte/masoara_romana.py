"""S2 (cascada, aprobat de Adrian pe 19 octombrie 2026): motorul de română măsoară greșelile din datele de conversație.

DOAR MĂSOARĂ: citește perechile, trece răspunsurile și textele prin `Motor().verifica_text` și numără problemele.
Nu șterge și nu schimbă nimic în date (filtrul vine abia într-o sarcină separată, după „da”-ul lui Adrian).

    python unelte/masoara_romana.py                        # cele două fișiere de antrenare, raportul în lucru/
    python unelte/masoara_romana.py --cate 200             # repetiție pe primele 200 de perechi din fiecare

Perechile în engleză nu se măsoară (motorul e doar pentru română); se numără separat.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter
from pathlib import Path

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

FISIERE = {"raspuns_din_text": "date/conversatie/text/antrenare.jsonl", "vechi": "date/conversatie/antrenare.jsonl"}
# Felurile de probleme ale motorului, pe grupele cerute în S2.
GRUPE = {"acord_subst_adj": "acord", "acord_subst_det": "acord", "acord_subiect_predicat": "acord", "acord_numeral": "acord",
         "regim_prepozitie": "acord", "acord_al": "al/a", "numeral_de": "numeral cu „de”", "necunoscut": "necunoscute",
         "ortografie": "diacritice", "ipoteza": "necunoscute"}


def grupa(tip: str) -> str:
    return GRUPE.get(tip, tip)


def bucati(pereche: dict) -> list[tuple[str, str]]:
    """Ce se verifică dintr-o pereche: textul din față (dacă are) și răspunsul."""
    return [(camp, pereche[camp]) for camp in ("text", "raspuns") if str(pereche.get(camp) or "").strip()]


def masoara(perechi: list[dict], verifica, cache: dict | None = None) -> dict:
    """`verifica(text) -> dict` ca `Motor.verifica_text`. Textele care se repetă se verifică o singură dată."""
    cache = {} if cache is None else cache
    pe_grupe, pe_certitudine, pe_tip_pereche = Counter(), Counter(), Counter()
    cu_probleme, fara_necunoscute, exemple, engleza = 0, 0, [], 0
    for i, p in enumerate(perechi):
        if p.get("limba", "ro") != "ro":
            engleza += 1
            continue
        gasite = []
        for camp, text in bucati(p):
            if text not in cache:
                cache[text] = verifica(text)["probleme"]
            gasite += [(camp, pr) for pr in cache[text]]
        if gasite:
            cu_probleme += 1
            fara_necunoscute += any(grupa(pr["tip"]) != "necunoscute" for _, pr in gasite)
            pe_tip_pereche[p.get("fel", "?")] += 1
        for g in {grupa(pr["tip"]) for _, pr in gasite}:
            pe_grupe[g] += 1
        for c in {pr.get("certitudine", "?") for _, pr in gasite}:
            pe_certitudine[c] += 1
        for camp, pr in gasite:
            exemple.append({"pereche": i, "camp": camp, "intrebare": p.get("intrebare", ""), "propozitie": pr.get("propozitie", ""),
                            "tip": pr["tip"], "grupa": grupa(pr["tip"]), "cuvinte": pr.get("cuvinte", []),
                            "mesaj": pr.get("mesaj", ""), "sugestie": pr.get("sugestie"), "certitudine": pr.get("certitudine")})
    romana = len(perechi) - engleza
    return {"perechi": len(perechi), "romana": romana, "engleza_nemasurate": engleza, "cu_probleme": cu_probleme,
            "fractie_cu_probleme": round(cu_probleme / romana, 4) if romana else None,
            "cu_probleme_fara_necunoscute": fara_necunoscute,
            "pe_grupe": dict(pe_grupe.most_common()), "pe_certitudine": dict(pe_certitudine.most_common()),
            "pe_felul_perechii": dict(pe_tip_pereche.most_common()), "probleme": exemple}


def alese(probleme: list[dict], cate: int, samanta: int) -> list[dict]:
    return random.Random(samanta).sample(probleme, min(cate, len(probleme)))


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Motorul de română măsoară problemele din datele de conversație.")
    parser.add_argument("--cate", type=int, default=0, help="doar primele atâtea perechi din fiecare fișier")
    parser.add_argument("--exemple", type=int, default=30)
    parser.add_argument("--samanta", type=int, default=1020)
    parser.add_argument("--iesire", default="lucru/masoara_romana/rezultat.json")
    args = parser.parse_args(argv)

    from module.limba_romana.motor import Motor

    motor = Motor()
    cache: dict = {}
    rezultat = {"samanta": args.samanta}
    for nume, cale in FISIERE.items():
        perechi = [json.loads(r) for r in (RADACINA / cale).read_text(encoding="utf-8").splitlines() if r.strip()]
        if args.cate:
            perechi = perechi[:args.cate]
        r = masoara(perechi, motor.verifica_text, cache)
        r["exemple"] = alese(r["probleme"], args.exemple, args.samanta)
        # Necunoscutele (mai ales nume proprii) acoperă aproape tot; ca supraveghetorul să poată număra alarmele false
        # la gramatică, încă 20 alese doar dintre celelalte.
        r["exemple_gramatica"] = alese([x for x in r["probleme"] if x["grupa"] != "necunoscute"], 20, args.samanta)
        r["toate_problemele"] = len(r.pop("probleme"))
        rezultat[nume] = {"fisier": cale, **r}
        print(f"{nume} ({cale}): {r['romana']} perechi în română ({r['engleza_nemasurate']} în engleză, nemăsurate); "
              f"cu cel puțin o problemă: {r['cu_probleme']} ({r['fractie_cu_probleme']:.1%}); fără să numărăm necunoscutele: "
              f"{r['cu_probleme_fara_necunoscute']}")
        print(f"   pe grupe: {r['pe_grupe']}\n   pe certitudine: {r['pe_certitudine']}")
    motor.inchide()
    iesire = RADACINA / args.iesire
    iesire.parent.mkdir(parents=True, exist_ok=True)
    iesire.write_text(json.dumps(rezultat, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Toate cifrele și exemplele: {iesire}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
