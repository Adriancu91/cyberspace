"""S64, pașii 3–4 (procesor): pass@k (k = 1, 10, 50, 100, 200) din pe_problema cu `pass_la_k` din examen_cod.py, și
„de ce pică” pe corpurile de la (a) T = 0,8: verificarea statică (aceeași `verifica_arborele` ca în cutie) pe toate corpurile,
iar corpurile cazut/timp/memorie/blocat se rulează din nou în cutie doar ca să li se citească mesajul. Doar setul de PROBĂ."""
import json
import sys
from collections import Counter
from pathlib import Path

RAD = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAD))
from unelte.kronos_cod import _cutie_interior as ci  # noqa: E402
from unelte.kronos_cod.cutie import ruleaza  # noqa: E402
from unelte.kronos_cod.examen_cod import pass_la_k, set_proba  # noqa: E402

IES = RAD / "lucru" / "kronos_cod" / "s64"
KS = (1, 10, 50, 100, 200)


def passk(nota):
    return {k: sum(pass_la_k(x["n"], x["c"], k) for x in nota["pe_problema"]) for k in KS}


def categorie(p):
    if p.startswith("sintaxă"):
        return p.split(" (rândul")[0]
    return p.split(":")[0] + ": " + p.split(":", 1)[1].strip().split(".")[0] if ":" in p else p


def main():
    rez = {}
    for nume in ("t08", "t04"):
        nota = json.loads((IES / f"nota_{nume}.json").read_text(encoding="utf-8"))
        rez[nume] = {"pass_k_din_20": passk(nota), "stari": nota["stari"],
                     "c_pe_problema": {x["id"]: x["c"] for x in nota["pe_problema"] if x["c"]}}
    probleme = {p.id: p for p in set_proba()}
    rasp = json.loads((IES / "t08.json").read_text(encoding="utf-8"))["raspunsuri"]
    permise = set(ci.MODULE_DE_BAZA)
    motive, motive_exacte, fara_compilare, exemple_sintaxa, exemple_interzis = Counter(), Counter(), 0, [], []
    total = 0
    for pid, corpuri in rasp.items():
        p = probleme[pid]
        for corp in corpuri:
            total += 1
            pr = ci.verifica_arborele(p.program(corp), permise)
            if not pr:
                continue
            if pr[0].startswith("sintaxă"):
                fara_compilare += 1
                if len(exemple_sintaxa) < 3:
                    exemple_sintaxa.append({"id": pid, "motiv": pr[0], "corp": corp[-400:]})
            elif len(exemple_interzis) < 3:
                exemple_interzis.append({"id": pid, "motiv": pr[0], "corp": corp[:400]})
            motive[categorie(pr[0])] += 1
            motive_exacte[pr[0] if not pr[0].startswith("sintaxă") else categorie(pr[0])] += 1
    # mesajele pentru stările rare (cazut/timp/memorie/blocat/eroare): rulare din nou în cutie, doar ele
    rare, exemple_rare = Counter(), []
    for pid, corpuri in rasp.items():
        p = probleme[pid]
        for corp in corpuri:
            if ci.verifica_arborele(p.program(corp), permise):
                continue
            r = ruleaza(p.program(corp), p.teste)
            if r.stare in ("ok", "picat"):
                continue
            msg = (r.mesaj or "; ".join(r.blocate[:2]) or "")[:120]
            rare[(r.stare, msg.split(":")[0] if msg else "")] += 1
            if len(exemple_rare) < 4:
                exemple_rare.append({"id": pid, "stare": r.stare, "mesaj": msg, "corp": corp[:300]})
    rez["de_ce_pica_t08"] = {
        "corpuri": total, "nu_se_compileaza": fara_compilare,
        "statice_pe_categorie": dict(motive.most_common(15)),
        "statice_exacte_top": dict(motive_exacte.most_common(15)),
        "rare_rerulate": {f"{a} | {b}": c for (a, b), c in rare.most_common(15)},
        "exemple_sintaxa": exemple_sintaxa, "exemple_interzis": exemple_interzis, "exemple_rare": exemple_rare,
    }
    ok = []
    for pid, corpuri in rasp.items():
        if rez["t08"]["c_pe_problema"].get(pid):
            p = probleme[pid]
            for corp in corpuri:
                if ruleaza(p.program(corp), p.teste).stare == "ok":
                    ok.append({"id": pid, "enunt": p.enunt[-300:], "corp": corp[:300]})
                    break
    rez["exemple_ok_t08"] = ok
    (IES / "analiza.json").write_text(json.dumps(rez, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(rez, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
