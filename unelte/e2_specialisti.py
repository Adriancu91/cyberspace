"""E2 „3 specialiști + ruter” (S22, 23 octombrie 2026; E2 aprobat de Adrian pe 23 oct 10:20, strategia
docs/rapoarte/2026-10-22_0200_strategie_nucleu_fara_llm.md §4 H4 și §7 E2): pregătirea de pe procesor, ca S23 (placa)
să fie doar rularea. Nimic de aici nu încarcă un model.

Familiile, cu o regulă fixă (aceeași la antrenare și la examene), fără model:
  F2 „da/nu”                 răspunsul de referință e „Da.” sau „Nu.” (ca regula 2 din unelte/verificator_text.py);
  F3 „tipurile din S11”      perechea are un tip adăugat la S11 (date/conversatie/text_v3/tipuri_noi.jsonl) și nu e da/nu;
                             la examene asta înseamnă exact S15 (e) (verificat de `masoara-ruter`);
  F1 „fapte / nume / ani”    tot restul (și „Nu scrie în text.” al tipurilor vechi, și conversația simplă).

Comenzile:
    python -X utf8 unelte/e2_specialisti.py imparte        # f1/f2/f3/antrenare.jsonl, ruter_validare.jsonl, info.json
    python -X utf8 unelte/e2_specialisti.py ruter          # ruter.json (începuturi de 1–3 cuvinte, prag 5)
    python -X utf8 unelte/e2_specialisti.py masoara-ruter  # (i) pe ruter_validare; cu --examene, o dată: (ii) pe 210
    python -X utf8 unelte/e2_specialisti.py baseline       # #415 pe familii (verificatorul S16 și F1 ≥ 0,8)
    python -X utf8 unelte/e2_specialisti.py configurari    # config/conv_w2_spec_f1/f2/f3.toml din conv_w2_text_v3.toml
    python -X utf8 unelte/e2_specialisti.py sistem --specialisti F1=<examene> F2=<examene> F3=<examene> \
        [--monolit lucru/e1/examene_415_20261023_023327.json]

Ies: date/conversatie/e2/ și lucru/e2/. Nu atinge kronos/, examenul BPB, paznicul, datele de examen, text_v3, auto_v1,
auto_v2 sau unelte/verificator_text.py.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from unelte.verificator_text import cuvinte, normalizeaza, verifica  # noqa: E402

TEXT_V3 = "date/conversatie/text_v3/antrenare.jsonl"
TIPURI_NOI = "date/conversatie/text_v3/tipuri_noi.jsonl"
DOSAR = RADACINA / "date" / "conversatie" / "e2"
LUCRU = RADACINA / "lucru" / "e2"
EXAMENE = {"S15": "docs/conversatie/examen_generalizare_mare.json",
           "S4": "docs/conversatie/examen_generalizare_401.json",
           "noaptea10": "date/conversatie/text/examen.json"}
MONOLIT = "lucru/e1/examene_415_20261023_023327.json"
CONFIG_BAZA = "config/conv_w2_text_v3.toml"
FAMILII = ("F1", "F2", "F3")
SAMANTA = 1023
FRACTIE_VALIDARE = 0.10
LUNGIMI = (1, 2, 3)
PRAG = 5
PRAG_RUTER = 0.90


def _citeste_jsonl(cale: str | Path) -> list[dict[str, Any]]:
    return [json.loads(r) for r in (RADACINA / cale).read_text(encoding="utf-8").splitlines() if r.strip()]


def _scrie_jsonl(cale: Path, randuri: list[dict[str, Any]]) -> int:
    cale.parent.mkdir(parents=True, exist_ok=True)
    with cale.open("w", encoding="utf-8") as f:
        for r in randuri:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return len(randuri)


def _scrie_json(cale: Path, obiect: Any) -> None:
    cale.parent.mkdir(parents=True, exist_ok=True)
    cale.write_text(json.dumps(obiect, ensure_ascii=False, indent=1), encoding="utf-8")


def _relativ(cale: Path) -> str:
    try:
        return cale.relative_to(RADACINA).as_posix()
    except ValueError:
        return str(cale)


# ---- familiile -----------------------------------------------------------------------------------------------------

def tipuri_s11() -> set[str]:
    return {p["tip"] for p in _citeste_jsonl(TIPURI_NOI)}


def este_da_nu(raspuns: str) -> bool:
    return normalizeaza(raspuns) in ("da", "nu")


def familia(pereche: dict[str, Any], tipuri_noi: set[str]) -> str:
    """Regula fixă a familiilor (aceeași la antrenare și la examene)."""
    if este_da_nu(pereche["raspuns"]):
        return "F2"
    if pereche.get("tip") in tipuri_noi:
        return "F3"
    return "F1"


def imparte(perechi: list[dict[str, Any]], tipuri_noi: set[str], samanta: int = SAMANTA,
            fractie: float = FRACTIE_VALIDARE) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]], list[str]]:
    """(perechile pe familii — toate, specialiștii se antrenează pe tot —, validarea ruterului = perechile din 10 % din
    grupuri (articole), grupurile puse deoparte)."""
    pe_familii: dict[str, list[dict[str, Any]]] = {f: [] for f in FAMILII}
    for p in perechi:
        pe_familii[familia(p, tipuri_noi)].append(p)
    grupuri = sorted({p.get("grup", "") for p in perechi})
    random.Random(samanta).shuffle(grupuri)
    deoparte = sorted(grupuri[:round(len(grupuri) * fractie)])
    alese = set(deoparte)
    validare = [{**p, "familie": familia(p, tipuri_noi)} for p in perechi if p.get("grup", "") in alese]
    return pe_familii, validare, deoparte


# ---- ruterul -------------------------------------------------------------------------------------------------------

def inceputul(intrebare: str, n: int) -> str:
    """Primele n cuvinte, litere mici, fără semne (normalizeaza din verificator)."""
    return " ".join(cuvinte(intrebare)[:n])


def construieste_ruter(intrebari: list[tuple[str, str]], lungimi: tuple[int, ...] = LUNGIMI, prag: int = PRAG,
                       implicit: str = "F1") -> dict[str, Any]:
    """Din (întrebare, familie): pentru fiecare început de 1/2/3 cuvinte care apare de cel puțin `prag` ori, familia cea
    mai des întâlnită (la egalitate, ordinea F1, F2, F3)."""
    numarate: dict[int, dict[str, Counter[str]]] = {n: defaultdict(Counter) for n in lungimi}
    for q, f in intrebari:
        cuv = cuvinte(q)
        for n in lungimi:
            if len(cuv) >= n:
                numarate[n][" ".join(cuv[:n])][f] += 1
    tabel: dict[str, dict[str, str]] = {}
    for n in lungimi:
        tabel[str(n)] = {}
        for inc, c in sorted(numarate[n].items()):
            if sum(c.values()) >= prag:
                tabel[str(n)][inc] = max(FAMILII, key=lambda f: (c[f], -FAMILII.index(f)))
    return {"lungimi": list(lungimi), "prag": prag, "implicit": implicit, "intrebari": len(intrebari),
            "inceputuri": {k: len(v) for k, v in tabel.items()}, "tabel": tabel}


def ruteaza(ruter: dict[str, Any], intrebare: str) -> str:
    """Cel mai lung început găsit în tabel; altfel familia implicită (F1)."""
    cuv = cuvinte(intrebare)
    for n in sorted(ruter["lungimi"], reverse=True):
        if len(cuv) >= n:
            f = ruter["tabel"][str(n)].get(" ".join(cuv[:n]))
            if f:
                return f
    return ruter["implicit"]


def masoara(ruter: dict[str, Any], intrebari: list[dict[str, Any]], cheie_grup: str = "") -> dict[str, Any]:
    """Procentul corect, pe total, pe familie și (dacă e dat) pe grup; plus lista greșelilor."""
    bune, n = Counter(), Counter()
    gresite: list[dict[str, Any]] = []
    for p in intrebari:
        ales = ruteaza(ruter, p["intrebare"])
        for k in ("total", f"familie {p['familie']}") + ((f"{cheie_grup} {p[cheie_grup]}",) if cheie_grup else ()):
            n[k] += 1
            bune[k] += ales == p["familie"]
        if ales != p["familie"]:
            gresite.append({"intrebare": p["intrebare"], "familie": p["familie"], "ales": ales,
                            **({cheie_grup: p[cheie_grup]} if cheie_grup else {})})
    return {"corect": {k: f"{bune[k]}/{n[k]} = {100 * bune[k] / n[k]:.1f} %" for k in sorted(n)},
            "procent": round(100 * bune["total"] / max(1, n["total"]), 2), "gresite": gresite}


# ---- examenele (aceleași 210 ca la S17/S19: fără conversația simplă a nopții 10) -----------------------------------

def grup_examen(nume: str, p: dict[str, Any]) -> str:
    return f"{nume} {p.get('categorie') or p['fel']}"


def intrebari_examene(tipuri_noi: set[str]) -> list[dict[str, Any]]:
    toate: list[dict[str, Any]] = []
    for nume, cale in EXAMENE.items():
        for i, p in enumerate(json.loads((RADACINA / cale).read_text(encoding="utf-8"))["perechi"]):
            if p["fel"] != "conversatie":
                toate.append({**p, "examen": nume, "index": i, "grup_examen": grup_examen(nume, p),
                              "familie": familia(p, tipuri_noi)})
    return toate


def _lung(raspuns: str, referinta: str) -> bool:
    """„Lung” ca la S21 (analiza_b2): peste 2× cuvintele referinței."""
    return len(cuvinte(raspuns)) > 2 * len(cuvinte(referinta))


def raspunsurile(fisier_examene: dict[str, Any]) -> dict[tuple[str, int], dict[str, Any]]:
    """(examen, index) → răspunsul din fișierul `examene_<id>_*.json` (fără conversația simplă)."""
    rez: dict[tuple[str, int], dict[str, Any]] = {}
    for nume in EXAMENE:
        for i, p in enumerate(fisier_examene[nume]["raspunsuri"]):
            if p["fel"] != "conversatie":
                rez[(nume, i)] = p
    return rez


def noteaza_pe_familii(intrebari: list[dict[str, Any]], raspuns_pentru) -> dict[str, Any]:
    """Pe fiecare familie și pe fiecare grup de examen: corecte cu verificatorul S16, cu F1 ≥ 0,8, și câte din cele
    corecte sunt lungi. `raspuns_pentru(p)` dă răspunsul elevului la întrebarea p."""
    c: dict[str, Counter[str]] = defaultdict(Counter)
    for p in intrebari:
        r = raspuns_pentru(p)
        v = verifica(p["raspuns"], r)
        for k in ("total", f"familie {p['familie']}", p["grup_examen"]):
            c[k]["intrebari"] += 1
            c[k]["corecte"] += v["corect"]
            c[k]["corecte_f1"] += v["corect_f1"]
            c[k]["lungi_corecte"] += bool(v["corect"]) and _lung(r, p["raspuns"])
    return {k: dict(v) for k, v in sorted(c.items())}


def baseline(monolit: dict[str, Any], tipuri_noi: set[str]) -> dict[str, Any]:
    rasp = raspunsurile(monolit)
    intrebari = intrebari_examene(tipuri_noi)
    for p in intrebari:
        if rasp[(p["examen"], p["index"])]["intrebare"] != p["intrebare"]:
            raise ValueError(f"întrebarea {p['examen']} {p['index']} nu e aceeași în fișierul examenelor")
    return noteaza_pe_familii(intrebari, lambda p: rasp[(p["examen"], p["index"])]["raspuns_elev"])


def sistem(ruter: dict[str, Any], specialisti: dict[str, dict[str, Any]], tipuri_noi: set[str],
           monolit: dict[str, Any] | None = None, intrebari: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Nota sistemului (ruter + specialiști), fără model: la fiecare întrebare, răspunsul specialistului ales de ruter,
    notat cu verificatorul S16 (și F1). Plus „ruterul perfect” (specialistul familiei corecte), fiecare specialist pe
    toate întrebările (pentru criteriul A: specialistul k pe familia k) și, dacă e dat, monolitul."""
    intrebari = intrebari if intrebari is not None else intrebari_examene(tipuri_noi)
    rasp = {f: raspunsurile(e) for f, e in specialisti.items()}
    for f, r in rasp.items():
        for p in intrebari:
            if r[(p["examen"], p["index"])]["intrebare"] != p["intrebare"]:
                raise ValueError(f"{f}: întrebarea {p['examen']} {p['index']} nu e aceeași")

    def din(f: str):
        return lambda p: rasp[f][(p["examen"], p["index"])]["raspuns_elev"]

    def ales(p: dict[str, Any]) -> str:
        f = ruteaza(ruter, p["intrebare"])
        return f if f in rasp else ruter["implicit"]

    rez: dict[str, Any] = {
        "creat": datetime.now().isoformat(timespec="seconds"),
        "specialisti": {f: e.get("experiment") for f, e in specialisti.items()},
        "ruter": masoara(ruter, intrebari, "grup_examen")["corect"],
        "sistem": noteaza_pe_familii(intrebari, lambda p: din(ales(p))(p)),
        "sistem_ruter_perfect": noteaza_pe_familii(
            intrebari, lambda p: din(p["familie"] if p["familie"] in rasp else ruter["implicit"])(p)),
        "fiecare_specialist": {f: noteaza_pe_familii(intrebari, din(f)) for f in rasp},
    }
    if monolit is not None:
        rm = raspunsurile(monolit)
        rez["monolit"] = {"experiment": monolit.get("experiment"),
                          **noteaza_pe_familii(intrebari, lambda p: rm[(p["examen"], p["index"])]["raspuns_elev"])}
        rez["criteriul_A_examene"] = {
            f: {"specialist": rez["fiecare_specialist"][f].get(f"familie {f}", {}).get("corecte", 0),
                "monolit": rez["monolit"].get(f"familie {f}", {}).get("corecte", 0)} for f in rasp}
        rez["criteriul_B"] = {"sistem": rez["sistem"]["total"]["corecte"], "monolit": rez["monolit"]["total"]["corecte"]}
    return rez


# ---- configurările -------------------------------------------------------------------------------------------------

def configurare(baza: str, f: str) -> str:
    """Copia lui conv_w2_text_v3.toml; diferă doar `nume`, `conversatie` și `cale_stare`, fiecare înlocuit exact o dată
    (2 rânduri: `conversatie` și `cale_stare` stau amândouă în `setari = { … }`); restul e identic, verificat."""
    x = f.lower()
    inlocuiri = (('nume = "w2_conv_text_v3"', f'nume = "w2_spec_{x}"'),
                 ('conversatie = "date/conversatie/text_v3/antrenare.jsonl"',
                  f'conversatie = "date/conversatie/e2/{x}/antrenare.jsonl"'),
                 ('cale_stare = "lucru/w2_conv_text_v3/gpt.pt"', f'cale_stare = "lucru/w2_spec_{x}/gpt.pt"'))
    nou = baza
    for vechi, cu in inlocuiri:
        if baza.count(vechi) != 1:
            raise ValueError(f"„{vechi}” trebuie să apară o dată în {CONFIG_BAZA}")
        nou = nou.replace(vechi, cu)
    inapoi = nou
    for vechi, cu in inlocuiri:
        inapoi = inapoi.replace(cu, vechi)
    diferite = sum(a != b for a, b in zip(baza.splitlines(), nou.splitlines()))
    if inapoi != baza or diferite != 2 or len(baza.splitlines()) != len(nou.splitlines()):
        raise ValueError(f"{f}: trebuiau să difere doar cele 3 valori (2 rânduri), diferă {diferite} rânduri")
    return nou


# ---- comenzile -----------------------------------------------------------------------------------------------------

def cmd_imparte() -> int:
    perechi = _citeste_jsonl(TEXT_V3)
    tn = tipuri_s11()
    pe_familii, validare, deoparte = imparte(perechi, tn)
    suma = sum(len(v) for v in pe_familii.values())
    for f, v in pe_familii.items():
        _scrie_jsonl(DOSAR / f.lower() / "antrenare.jsonl", v)
    _scrie_jsonl(DOSAR / "ruter_validare.jsonl", validare)
    info = {"creat": datetime.now().isoformat(timespec="seconds"), "sursa": TEXT_V3, "perechi": len(perechi),
            "pe_familie": {f: len(v) for f, v in pe_familii.items()}, "suma": suma, "suma_ok": suma == len(perechi),
            "pe_familie_si_fel": {f: dict(Counter(p["fel"] for p in v)) for f, v in pe_familii.items()},
            "sub_2000": [f for f, v in pe_familii.items() if len(v) < 2000],
            "ruter_validare": {"grupuri_total": len({p.get("grup", "") for p in perechi}), "grupuri_deoparte": len(deoparte),
                               "perechi": len(validare), "pe_familie": dict(Counter(p["familie"] for p in validare)),
                               "samanta": SAMANTA, "fractie": FRACTIE_VALIDARE},
            "regula": "F2: răspunsul normalizat e „da”/„nu”; F3: tip din text_v3/tipuri_noi.jsonl și nu da/nu; F1: restul"}
    _scrie_json(DOSAR / "info.json", info)
    print(json.dumps(info, ensure_ascii=False, indent=1))
    return 0 if info["suma_ok"] else 1


def cmd_ruter(lungimi: tuple[int, ...], prag: int) -> int:
    validare = _citeste_jsonl(DOSAR / "ruter_validare.jsonl")
    deoparte = {p.get("grup", "") for p in validare}
    tn = tipuri_s11()
    intrebari = [(p["intrebare"], familia(p, tn)) for p in _citeste_jsonl(TEXT_V3) if p.get("grup", "") not in deoparte]
    ruter = construieste_ruter(intrebari, lungimi, prag)
    ruter["creat"] = datetime.now().isoformat(timespec="seconds")
    ruter["fara_grupurile_de_validare"] = len(deoparte)
    _scrie_json(DOSAR / "ruter.json", ruter)
    print(json.dumps({k: v for k, v in ruter.items() if k != "tabel"}, ensure_ascii=False), f"(validare: {len(validare)} perechi)")
    return 0


def cmd_masoara(pe_examene: bool) -> int:
    ruter = json.loads((DOSAR / "ruter.json").read_text(encoding="utf-8"))
    if not pe_examene:
        rez = masoara(ruter, _citeste_jsonl(DOSAR / "ruter_validare.jsonl"), "fel")
        rez["gresite_exemple"] = rez.pop("gresite")[:40]
        _scrie_json(LUCRU / "ruter_validare.json", rez)
        print(json.dumps(rez["corect"], ensure_ascii=False, indent=1))
        print(json.dumps(Counter((g["familie"], g["ales"]) for g in rez["gresite_exemple"]).most_common(), ensure_ascii=False))
        return 0
    tn = tipuri_s11()
    intrebari = intrebari_examene(tn)
    f3 = [p for p in intrebari if p["familie"] == "F3"]
    verificare = {"intrebari": len(intrebari), "F3_numai_S15_e": all(p["grup_examen"] == "S15 e" for p in f3)
                  and len(f3) == sum(p["grup_examen"] == "S15 e" for p in intrebari)}
    rez = masoara(ruter, intrebari, "grup_examen")
    rez["verificare"] = verificare
    rez["pe_familie_examene"] = dict(Counter(p["familie"] for p in intrebari))
    rez["poarta"] = "trece (≥ 90 %)" if rez["procent"] >= 100 * PRAG_RUTER else "NU trece (< 90 %): S23 nu pornește"
    rez["ruter"] = {k: ruter[k] for k in ("lungimi", "prag", "implicit", "inceputuri")}
    _scrie_json(LUCRU / "ruter_examene.json", rez)
    print(json.dumps({k: v for k, v in rez.items() if k != "gresite"}, ensure_ascii=False, indent=1))
    for g in rez["gresite"]:
        print(f"  {g['grup_examen']}: {g['familie']} → {g['ales']}: {g['intrebare']}")
    return 0 if verificare["intrebari"] == 210 and verificare["F3_numai_S15_e"] else 1


def cmd_baseline(cale: str) -> int:
    monolit = json.loads((RADACINA / cale).read_text(encoding="utf-8"))
    rez = {"fisier": cale, "experiment": monolit.get("experiment"), **baseline(monolit, tipuri_s11())}
    _scrie_json(LUCRU / "baseline_415.json", rez)
    print(json.dumps(rez, ensure_ascii=False, indent=1))
    return 0 if rez["total"]["corecte"] == 144 and rez["total"]["intrebari"] == 210 else 1


def cmd_configurari() -> int:
    baza = (RADACINA / CONFIG_BAZA).read_bytes().decode("utf-8")  # octeții exacți (și sfârșitul de rând)
    for f in FAMILII:
        if (RADACINA / "lucru" / f"w2_spec_{f.lower()}").exists():
            print(f"lucru/w2_spec_{f.lower()} există deja: --porneste-din 415 nu s-ar aplica — oprit")
            return 1
    for f in FAMILII:
        cale = RADACINA / "config" / f"conv_w2_spec_{f.lower()}.toml"
        cale.write_bytes(configurare(baza, f).encode("utf-8"))
        print("scris:", _relativ(cale))
    return 0


def cmd_sistem(specialisti: list[str], monolit: str, iesire: str) -> int:
    ruter = json.loads((DOSAR / "ruter.json").read_text(encoding="utf-8"))
    spec = {}
    for s in specialisti:
        f, cale = s.split("=", 1)
        spec[f] = json.loads((RADACINA / cale).read_text(encoding="utf-8"))
    m = json.loads((RADACINA / monolit).read_text(encoding="utf-8")) if monolit else None
    rez = sistem(ruter, spec, tipuri_s11(), m)
    rez["fisiere"] = {"specialisti": specialisti, "monolit": monolit}
    cale = RADACINA / iesire if iesire else LUCRU / f"sistem_{datetime.now():%Y%m%d_%H%M%S}.json"
    _scrie_json(cale, rez)
    print(json.dumps({k: rez[k] for k in ("specialisti", "criteriul_A_examene", "criteriul_B") if k in rez},
                     ensure_ascii=False, indent=1))
    print("sistem:", rez["sistem"]["total"], "| ruter perfect:", rez["sistem_ruter_perfect"]["total"])
    print("scris:", _relativ(cale))
    return 0


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="E2: 3 specialiști + ruter (S22).")
    sub = parser.add_subparsers(dest="pas", required=True)
    sub.add_parser("imparte")
    r = sub.add_parser("ruter")
    r.add_argument("--lungimi", type=int, nargs="*", default=list(LUNGIMI))
    r.add_argument("--prag", type=int, default=PRAG)
    m = sub.add_parser("masoara-ruter")
    m.add_argument("--examene", action="store_true", help="(ii): cele 210 întrebări de examen — o singură dată")
    b = sub.add_parser("baseline")
    b.add_argument("--monolit", default=MONOLIT)
    sub.add_parser("configurari")
    s = sub.add_parser("sistem")
    s.add_argument("--specialisti", nargs="+", required=True, help="F1=<examene_*.json> F2=… F3=…")
    s.add_argument("--monolit", default=MONOLIT)
    s.add_argument("--iesire", default="")
    args = parser.parse_args(argv)
    if args.pas == "imparte":
        return cmd_imparte()
    if args.pas == "ruter":
        return cmd_ruter(tuple(args.lungimi), args.prag)
    if args.pas == "masoara-ruter":
        return cmd_masoara(args.examene)
    if args.pas == "baseline":
        return cmd_baseline(args.monolit)
    if args.pas == "configurari":
        return cmd_configurari()
    return cmd_sistem(args.specialisti, args.monolit, args.iesire)


if __name__ == "__main__":
    raise SystemExit(main())
