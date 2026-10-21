"""Re-notarea S16 (E0, 22 octombrie 2026): nota lui Qwen alături de verificatorul fără LLM, pe răspunsurile DEJA salvate.

Citește fișierele de rezultate din `lucru/examen_conversatie/` (nu le schimbă) și scrie unul nou,
`lucru/examen_conversatie/renotare_E0_<data>.json`, cu fiecare întrebare (nota Qwen, corect = nota ≥ 7; verdictul
verificatorului, regula principală și F1) și cu acordurile: pe S15, pe S4, împreună, pe model, pe fel.

    python -X utf8 unelte/renoteaza_text.py
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from datetime import datetime
from pathlib import Path

RADACINA = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RADACINA))

from unelte.verificator_text import verifica  # noqa: E402

DOSAR = RADACINA / "lucru" / "examen_conversatie"
NOTA_CORECT = 7
FISIERE = {
    "S15": ["experiment_401_20261022_001355.json", "experiment_407_20261022_001532.json",
            "experiment_415_20261022_001707.json"],
    "S4": ["experiment_401_20261020_105728.json", "experiment_405_20261021_083112.json",
           "experiment_406_20261021_083228.json", "experiment_407_20261021_000257.json",
           "experiment_415_20261021_223319.json"],
}


def fel(intrebare: dict) -> str:
    """Grupul pentru acord: categoria (a/b/c/d, b2/e); în S4 și „nu_scrie” când referința e „Nu scrie în text.”."""
    return intrebare.get("categorie") or "?"


def renoteaza(examen: str, nume: str) -> list[dict]:
    date = json.loads((DOSAR / nume).read_text(encoding="utf-8"))
    randuri = []
    for i, r in enumerate(date["raspunsuri"]):
        v = verifica(r["raspuns"], r["raspuns_elev"])
        nota = int(r["nota_elev"])
        randuri.append({
            "examen": examen, "fisier": nume, "model": int(date["experiment"]), "nr": i, "fel": fel(r),
            "nu_scrie": r["raspuns"].strip().lower().startswith("nu scrie"), "tip": r.get("tip"),
            "intrebare": r["intrebare"], "referinta": r["raspuns"], "raspuns_elev": r["raspuns_elev"],
            "nota_qwen": nota, "qwen_corect": nota >= NOTA_CORECT,
            "verificator_corect": v["corect"], "motiv": v["motiv"], "acoperire": v["acoperire"],
            "f1": v["f1"], "verificator_f1_corect": v["corect_f1"],
        })
    return randuri


def acord(randuri: list[dict], cheie: str = "verificator_corect") -> dict:
    n = len(randuri)
    la_fel = sum(r["qwen_corect"] == r[cheie] for r in randuri)
    return {"intrebari": n, "la_fel": la_fel, "acord": round(la_fel / n, 4) if n else None,
            "qwen_da_verificator_nu": sum(r["qwen_corect"] and not r[cheie] for r in randuri),
            "qwen_nu_verificator_da": sum(r[cheie] and not r["qwen_corect"] for r in randuri)}


def rezumat(randuri: list[dict]) -> dict:
    s15 = [r for r in randuri if r["examen"] == "S15"]
    s4 = [r for r in randuri if r["examen"] == "S4"]
    rez: dict = {}
    for cheie, nume in (("verificator_corect", "principala"), ("verificator_f1_corect", "f1")):
        bucati = {"S15": acord(s15, cheie), "S4": acord(s4, cheie), "impreuna": acord(randuri, cheie)}
        for examen, grup in (("S15", s15), ("S4", s4)):
            for m in sorted({r["model"] for r in grup}):
                bucati[f"{examen}_#{m}"] = acord([r for r in grup if r["model"] == m], cheie)
        for m in sorted({r["model"] for r in randuri}):
            bucati[f"model_#{m}"] = acord([r for r in randuri if r["model"] == m], cheie)
        for f in sorted({r["fel"] for r in s4}):
            bucati[f"S4_fel_{f}"] = acord([r for r in s4 if r["fel"] == f], cheie)
        bucati["S4_nu_scrie"] = acord([r for r in s4 if r["nu_scrie"]], cheie)
        bucati["S4_fara_nu_scrie"] = acord([r for r in s4 if not r["nu_scrie"]], cheie)
        for f in sorted({r["fel"] for r in s15}):
            bucati[f"S15_fel_{f}"] = acord([r for r in s15 if r["fel"] == f], cheie)
        rez[nume] = bucati
    scoruri = {}
    for m in sorted({r["model"] for r in s15}):
        for f in ("b2", "e"):
            g = [r for r in s15 if r["model"] == m and r["fel"] == f]
            scoruri[f"#{m}_{f}"] = {"din": len(g), "qwen": sum(r["qwen_corect"] for r in g),
                                    "verificator": sum(r["verificator_corect"] for r in g),
                                    "verificator_f1": sum(r["verificator_f1_corect"] for r in g)}
    rez["scoruri_S15"] = scoruri
    rez["scoruri_S4"] = {f"#{m}": {"din": len(g), "qwen": sum(r["qwen_corect"] for r in g),
                                    "verificator": sum(r["verificator_corect"] for r in g),
                                    "verificator_f1": sum(r["verificator_f1_corect"] for r in g)}
                         for m in sorted({r["model"] for r in s4}) for g in [[r for r in s4 if r["model"] == m]]}
    toate = rez["principala"]["impreuna"]["acord"]
    rez["regula_de_citire"] = {
        "acord_impreuna_principala": toate,
        "verdict": "verificatorul poate înlocui pe Qwen" if toate >= 0.90 else "încă nu",
        "modele_sub_85": [k for k, v in rez["principala"].items() if k.startswith("model_#") and v["acord"] < 0.85],
    }
    return rez


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--iesire", default=None, help="implicit: lucru/examen_conversatie/renotare_E0_<data>.json")
    p.add_argument("--samanta", type=int, default=1022)
    a = p.parse_args()
    randuri = [r for examen, nume in FISIERE.items() for f in nume for r in renoteaza(examen, f)]
    dezacord = [r for r in randuri if r["qwen_corect"] != r["verificator_corect"]]
    alese = dezacord if len(dezacord) <= 20 else random.Random(a.samanta).sample(dezacord, 20)
    iesire = Path(a.iesire) if a.iesire else DOSAR / f"renotare_E0_{datetime.now():%Y%m%d_%H%M%S}.json"
    if iesire.exists():
        sys.exit(f"{iesire} există deja; nu-l suprascriu")
    rez = {"creat": datetime.now().isoformat(timespec="seconds"), "fisiere": FISIERE, "nota_corect_qwen": NOTA_CORECT,
           "rezumat": rezumat(randuri), "dezacorduri_alese_1022": alese, "intrebari": randuri}
    iesire.write_text(json.dumps(rez, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: rez["rezumat"][k] for k in ("regula_de_citire", "scoruri_S15", "scoruri_S4")},
                     ensure_ascii=False, indent=1))
    print("scris:", iesire.relative_to(RADACINA))


if __name__ == "__main__":
    main()
