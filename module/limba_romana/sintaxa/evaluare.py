"""Evaluarea motorului pe corpusul UD RRT (setul de EVALUARE = test, nefolosit la construirea lexiconului sau a regulilor).

Metrici (definiții precise, numitor cunoscut):
  - tokenizare: propoziții în care tokenizarea noastră coincide exact cu cea a corpusului / total propoziții;
  - pe tokenii aliniați (propozițiile cu tokenizare identică): acuratețea categoriei (UPOS), a lemei (comparare exactă,
    normalizată), a trăsăturilor (identice ca mulțime după convenția canonică; fără ExtPos, care e al expresiei; fără Number
    când gold îl omite la formele sincretice), UAS (capul corect) și LAS (capul și relația corecte, fără subtipurile după „:”);
  - ambiguitate: tokenii cu ≥ 2 candidați; dintre ei câți au categoria aleasă corect, câți au fost marcați „ambiguu”;
  - necunoscute: tokenii fără analiză în bază;
  - acord: numărul de probleme de acord semnalate pe propozițiile corpusului (care sunt corecte) = alarme false.
Rulare: python -m module.limba_romana.sintaxa.evaluare [--set evaluare|dezvoltare] [--limita N]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter

from .. import VERSIUNE
from ..baza import Baza, canonic_trasaturi, desparte_trasaturi
from ..morfologie.analizator import Analizator
from ..morfologie.trasaturi import canonic_pentru_pos
from ..text import normalizeaza
from .analiza import analizeaza_propozitie


def evalueaza(baza: Baza, set_: str = "evaluare", limita: int | None = None, verbos: bool = True, cu_dependente: bool = True) -> dict:
    an = Analizator(baza)
    exemple = [dict(r) for r in baza.con.execute("SELECT id, text, cuvinte FROM exemple WHERE set_ = ? ORDER BY id", (set_,))]
    if limita:
        exemple = exemple[:limita]
    c = Counter()
    greseli_pos: Counter = Counter()
    greseli_rel: Counter = Counter()
    greseli_lema_ex: list[tuple[str, str, str]] = []
    alarme_false: Counter = Counter()
    exemple_alarme: list[dict] = []
    t0 = time.time()
    for ex in exemple:
        gold = json.loads(ex["cuvinte"])
        c["propozitii"] += 1
        c["tokeni_gold"] += len(gold)
        prop = analizeaza_propozitie(baza, an, ex["text"], cu_dependente=cu_dependente)
        for p in prop.probleme:
            if p.tip.startswith("acord") or p.tip in ("numeral_de", "regim_prepozitie"):
                alarme_false[p.tip] += 1
                if len(exemple_alarme) < 40:
                    exemple_alarme.append({"id": ex["id"], "text": ex["text"], "problema": p.mesaj, "regula": p.regula})
        c["necunoscute"] += sum(1 for w in prop.cuvinte if w.necunoscut)
        c["tokeni_nostri"] += len(prop.cuvinte)
        if [w.text for w in prop.cuvinte] != [g["forma"] for g in gold]:
            c["propozitii_tokenizare_diferita"] += 1
            continue
        c["propozitii_aliniate"] += 1
        for w, g in zip(prop.cuvinte, gold):
            if g["upos"] == "PUNCT":
                c["tokeni_punct"] += 1
                continue
            c["tokeni_aliniati"] += 1
            pos_ok = w.pos == g["upos"] or (w.pos == "ABBR" and "Abbr=Yes" in g["trasaturi"]) or (w.pos == "X" and g["upos"] in ("X", "SYM"))
            if pos_ok:
                c["pos_corect"] += 1
            else:
                greseli_pos[(g["upos"], w.pos)] += 1
            lema_ok = normalizeaza(w.a.lema) == normalizeaza(g["lema"]) or (w.pos == "NUM" and w.a.incredere == "special")
            if lema_ok:
                c["lema_corecta"] += 1
            elif len(greseli_lema_ex) < 30:
                greseli_lema_ex.append((w.text, w.a.lema, g["lema"]))
            d_gold = canonic_pentru_pos(g["upos"], desparte_trasaturi(g["trasaturi"]), None)
            d_noi = canonic_pentru_pos(w.pos, w.a.trasaturi, w.a.gen_lexem)
            # UD RRT omite Number la formele verbale sincretice de persoana a III-a (bazează = sg/pl) și la unele determinante; nu îl cerem când lipsește din gold
            if "Number" not in d_gold:
                d_noi.pop("Number", None)
            tr_gold, tr_noi = canonic_trasaturi(d_gold), canonic_trasaturi(d_noi)
            if pos_ok and tr_gold == tr_noi:
                c["trasaturi_corecte"] += 1
            if pos_ok and lema_ok and tr_gold == tr_noi:
                c["analiza_completa_corecta"] += 1
            if len(w.candidati) >= 2:
                c["tokeni_ambigui"] += 1
                if pos_ok:
                    c["ambigui_pos_corect"] += 1
                if w.ambiguu:
                    c["ambigui_marcati"] += 1
                    if pos_ok:
                        c["ambigui_marcati_pos_corect"] += 1
            if cu_dependente:
                if w.cap == g["cap"]:
                    c["cap_corect"] += 1
                    if w.rel.split(":")[0] == g["rel"].split(":")[0]:
                        c["cap_si_relatie_corecte"] += 1
                    else:
                        greseli_rel[(g["rel"].split(":")[0], w.rel.split(":")[0])] += 1
    durata = time.time() - t0
    n = c["tokeni_aliniati"] or 1
    rez = {
        "set": set_, "versiune_motor": VERSIUNE, "propozitii": c["propozitii"], "durata_secunde": round(durata, 1),
        "tokenizare": {"propozitii_identice": c["propozitii_aliniate"], "propozitii_diferite": c["propozitii_tokenizare_diferita"],
                       "procent_identice": round(100 * c["propozitii_aliniate"] / max(1, c["propozitii"]), 1)},
        "tokeni_evaluati": c["tokeni_aliniati"],
        "acuratete": {
            "categorie_upos": round(100 * c["pos_corect"] / n, 2), "lema": round(100 * c["lema_corecta"] / n, 2),
            "trasaturi_si_categorie": round(100 * c["trasaturi_corecte"] / n, 2), "analiza_completa": round(100 * c["analiza_completa_corecta"] / n, 2),
            "UAS": round(100 * c["cap_corect"] / n, 2) if cu_dependente else None, "LAS": round(100 * c["cap_si_relatie_corecte"] / n, 2) if cu_dependente else None,
        },
        "ambiguitate": {"tokeni_cu_mai_multi_candidati": c["tokeni_ambigui"], "din_care_categorie_corecta": c["ambigui_pos_corect"],
                        "marcati_ambigui": c["ambigui_marcati"], "marcati_ambigui_cu_categorie_corecta": c["ambigui_marcati_pos_corect"]},
        "necunoscute": {"tokeni": c["necunoscute"], "procent_din_tokenii_nostri": round(100 * c["necunoscute"] / max(1, c["tokeni_nostri"]), 2)},
        "alarme_false_acord": dict(alarme_false), "alarme_false_la_100_propozitii": round(100 * sum(alarme_false.values()) / max(1, c["propozitii"]), 2),
        "greseli_categorie_frecvente": [{"gold": g, "al_nostru": a, "numar": k} for (g, a), k in greseli_pos.most_common(12)],
        "greseli_relatie_frecvente": [{"gold": g, "a_noastra": a, "numar": k} for (g, a), k in greseli_rel.most_common(12)],
        "exemple_greseli_lema": [{"forma": f, "a_noastra": a, "gold": g} for f, a, g in greseli_lema_ex[:20]],
        "exemple_alarme_false": exemple_alarme[:15],
        "definitii": "acuratețile sunt pe tokenii nepunctuație din propozițiile cu tokenizare identică cu a corpusului; LAS ignoră subtipurile relațiilor (după „:”)",
    }
    if verbos:
        print(json.dumps({k: v for k, v in rez.items() if k not in ("exemple_alarme_false", "exemple_greseli_lema")}, ensure_ascii=False, indent=1))
    return rez


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--set", default="evaluare", choices=["evaluare", "dezvoltare", "antrenare"])
    p.add_argument("--limita", type=int, default=None)
    p.add_argument("--fara-dependente", action="store_true")
    p.add_argument("--scrie", action="store_true", help="scrie rezultatul în tabela validari")
    a = p.parse_args(argv)
    with Baza(doar_citire=not a.scrie) as b:
        rez = evalueaza(b, a.set, a.limita, cu_dependente=not a.fara_dependente)
        if a.scrie:
            b.adauga_validare(f"evaluare_{a.set}", VERSIUNE, rez)
            b.commit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
