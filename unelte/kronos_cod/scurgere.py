"""Kronos-Cod: verificarea scurgerii setului ascuns în codul descărcat (S53, 31 octombrie 2026).

Întrebarea: apare ceva din cele 200 de probleme ale setului ascuns (S41) în codul curat descărcat la S46? Dacă da, un
scor pass@k de mai târziu n-ar mai însemna nimic pentru fișierele atinse, care trebuie excluse la pasul tokenizerului.

Cum caută:
- textul se normalizează: comentariile `# …` scoase, litere mici, apoi se taie în simboluri (nume, numere, câte un semn;
  spațiile nu contează, deci „spații comprimate” e implicit);
- pentru fiecare problemă: enunțul (semnătura + docstring-ul), soluția de referință și testele, puse cap la cap, dau
  n-gramele de 13 simboluri; un fișier „se suprapune” cu problema dacă are măcar o n-gramă comună;
- „soluția întreagă apare exact”: șirul de simboluri al soluției de referință se găsește întreg, la rând, în fișier;
- `def <numele funcției>` se numără separat, doar ca informație.

Ce scrie (în `lucru/kronos_cod/scurgere/`, nimic în Git; acolo ajung doar cifrele din raport):
    rezultat.json         cifrele pe problemă (fișiere atinse, cea mai lungă suprapunere, soluția exactă) și totalurile
    fisiere_de_exclus.txt un rând pe fișier atins: indicele din cod.jsonl, sha256, sursa, calea
Nu șterge și nu mută nimic din date. Rulează o singură dată: refuză dacă `rezultat.json` există.

Comanda:
    python -m unelte.kronos_cod.scurgere ruleaza [--procese 12]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from multiprocessing import Pool
from pathlib import Path

N = 13
RADACINA = Path(__file__).resolve().parents[2]
EXAMEN = RADACINA / "lucru" / "kronos_cod" / "examen_ascuns"
COD = RADACINA / "lucru" / "kronos_cod" / "complet"
IESIRE = RADACINA / "lucru" / "kronos_cod" / "scurgere"
SHA_EXAMEN = "90fc64cdebefc143f414474170eb9e9c936506204f9abfe0cff0268ddbdc3749"

_COMENTARIU = re.compile(r"#[^\n]*")
_SIMBOL = re.compile(r"[a-z_][a-z0-9_]*|\d+|\S")
_DEF = re.compile(r"def\s+([A-Za-z_][A-Za-z0-9_]*)")


def simboluri(text: str) -> list[str]:
    return _SIMBOL.findall(_COMENTARIU.sub("", text).lower())


def ngrame(simb: list[str], n: int = N) -> set[tuple]:
    return set(zip(*[simb[i:] for i in range(n)]))


def sha256_fisier(cale: Path) -> str:
    h = hashlib.sha256()
    with open(cale, "rb") as f:
        for bucata in iter(lambda: f.read(1 << 20), b""):
            h.update(bucata)
    return h.hexdigest()


def citeste_probleme(dosar: Path) -> list[dict]:
    f = Path(dosar) / "probleme.jsonl"
    return [json.loads(r) for r in f.read_text(encoding="utf-8").splitlines() if r.strip()]


def indexeaza(probleme: list[dict]) -> dict:
    """Ce caută lucrătorii: n-gramă → problemele ei, soluțiile (ca șir de simboluri) și numele funcțiilor."""
    gram_la_prob: dict[tuple, list[int]] = {}
    solutii = []
    for i, p in enumerate(probleme):
        tot = p["enunt"] + p["referinta"] + "\n" + "\n".join(p["teste"]) + "\n"
        for g in ngrame(simboluri(tot)):
            gram_la_prob.setdefault(g, []).append(i)
        solutii.append(tuple(simboluri(p["referinta"])))
    scurte: dict[int, dict[tuple, list[int]]] = {}  # soluțiile sub N simboluri: căutate pe lungimea lor
    for i, s in enumerate(solutii):
        if 0 < len(s) < N:
            scurte.setdefault(len(s), {}).setdefault(s, []).append(i)
    nume = {}
    for i, p in enumerate(probleme):
        nume.setdefault(p["functie"].lower(), []).append(i)
    return {"grame": gram_la_prob, "solutii": solutii, "scurte": scurte, "nume": nume}


def _contine(simb: list[str], cautat: tuple) -> bool:
    sep = "\x00"
    return (sep + sep.join(cautat) + sep) in (sep + sep.join(simb) + sep)


def scaneaza_text(text: str, idx: dict) -> dict | None:
    """Ce problemă atinge un fișier: {problema: cea mai lungă suprapunere}, soluțiile exacte, numele din `def`."""
    simb = simboluri(text)
    grame = idx["grame"]
    atinse: dict[int, int] = {}
    exacte: set[int] = set()
    if len(simb) >= N:
        potrivite = [k for k, g in enumerate(zip(*[simb[i:] for i in range(N)])) if g in grame]
        if potrivite:
            # cea mai lungă suprapunere ≈ cel mai lung șir de n-grame potrivite la rând, pe problemă
            pe_prob: dict[int, list[int]] = {}
            for k in potrivite:
                for p in grame[tuple(simb[k:k + N])]:
                    pe_prob.setdefault(p, []).append(k)
            for p, poz in pe_prob.items():
                cel_mai, sir = 1, 1
                for a, b in zip(poz, poz[1:]):
                    sir = sir + 1 if b == a + 1 else 1
                    cel_mai = max(cel_mai, sir)
                atinse[p] = cel_mai + N - 1
                sol = idx["solutii"][p]
                if len(sol) >= N and _contine(simb, sol):
                    exacte.add(p)
    for lung, sol_la_prob in idx["scurte"].items():
        if len(simb) >= lung:
            for g in sol_la_prob.keys() & set(zip(*[simb[i:] for i in range(lung)])):
                exacte.update(sol_la_prob[g])
    defuri = {m.lower() for m in _DEF.findall(text)} & idx["nume"].keys()
    nume = sorted({p for d in defuri for p in idx["nume"][d]})
    if not atinse and not exacte and not nume:
        return None
    return {"atinse": atinse, "exacte": sorted(exacte), "nume": nume}


_IDX = None
_EXCLUSE: set[int] = set()


def _initializeaza(idx, excluse):
    global _IDX, _EXCLUSE
    _IDX, _EXCLUSE = idx, excluse


def _lucreaza(lot: tuple[int, list[bytes]]):
    start, randuri = lot
    gasite, octeti, octeti_curat, fisiere_curat = [], 0, 0, 0
    for j, rand in enumerate(randuri):
        i = start + j
        r = json.loads(rand)
        marime = len(r["text"].encode("utf-8"))
        octeti += marime
        curat = i not in _EXCLUSE
        if curat:
            octeti_curat += marime
            fisiere_curat += 1
        g = scaneaza_text(r["text"], _IDX)
        if g:
            gasite.append({"i": i, "curat": curat, "octeti": marime, "sha256": r.get("sha256", ""),
                           "sursa": r.get("sursa", ""), "cale": r.get("cale", ""), **g})
    return len(randuri), octeti, octeti_curat, fisiere_curat, gasite


def _loturi(f_cod: Path, marime: int = 2000):
    lot, start, i = [], 0, 0
    with open(f_cod, "rb") as f:
        for rand in f:
            if rand.strip():
                lot.append(rand)
                i += 1
                if len(lot) >= marime:
                    yield start, lot
                    lot, start = [], i
    if lot:
        yield start, lot


def ruleaza(examen: Path = EXAMEN, cod: Path = COD, iesire: Path = IESIRE, procese: int = 12,
            sha_asteptat: str | None = SHA_EXAMEN, jurnal=print) -> dict:
    examen, cod, iesire = Path(examen), Path(cod), Path(iesire)
    f_rez = iesire / "rezultat.json"
    if f_rez.exists():
        raise SystemExit(f"{f_rez} există deja: verificarea se face o singură dată")
    sha_inainte = sha256_fisier(examen / "probleme.jsonl")
    if sha_asteptat and sha_inainte != sha_asteptat:
        raise SystemExit(f"suma setului ascuns nu se potrivește: {sha_inainte}")
    probleme = citeste_probleme(examen)
    idx = indexeaza(probleme)
    f_ap = cod / "aproape_duplicate.json"
    excluse = set(json.loads(f_ap.read_text(encoding="utf-8"))) if f_ap.exists() else set()
    jurnal(f"{len(probleme)} probleme, {len(idx['grame'])} n-grame de {N}; aproape-duplicate scoase: {len(excluse)}")
    t0 = time.time()
    fisiere = octeti = octeti_curat = fisiere_curat = 0
    gasite: list[dict] = []
    with Pool(procese, initializer=_initializeaza, initargs=(idx, excluse)) as pool:
        for n, o, oc, fc, g in pool.imap(_lucreaza, _loturi(cod / "cod.jsonl"), chunksize=1):
            fisiere += n
            octeti += o
            octeti_curat += oc
            fisiere_curat += fc
            gasite.extend(g)
            if fisiere % 100000 < n:
                jurnal(f"{fisiere} fișiere, {octeti / 1e9:.2f} GB, {time.time() - t0:.0f} s, găsite {len(gasite)}")
    sha_dupa = sha256_fisier(examen / "probleme.jsonl")

    pe_prob = []
    for k, p in enumerate(probleme):
        def numara(curat_doar):
            fs = [g for g in gasite if (g["curat"] or not curat_doar)]
            sup = [g["atinse"][k] for g in fs if k in g["atinse"]]
            return {"fisiere_suprapunere": len(sup), "cea_mai_lunga": max(sup, default=0),
                    "fisiere_solutie_exacta": sum(1 for g in fs if k in g["exacte"]),
                    "fisiere_def_nume": sum(1 for g in fs if k in g["nume"])}
        pe_prob.append({"id": p["id"], "sablon": p["sablon"], "simboluri_solutie": len(idx["solutii"][k]),
                        "curat": numara(True), "tot": numara(False)})

    def totaluri(cheie):
        c = [x[cheie] for x in pe_prob]
        return {"probleme_cu_suprapunere": sum(1 for x in c if x["fisiere_suprapunere"]),
                "probleme_cu_solutia_exacta": sum(1 for x in c if x["fisiere_solutie_exacta"]),
                "probleme_cu_def_nume": sum(1 for x in c if x["fisiere_def_nume"])}

    de_exclus = [g for g in gasite if g["atinse"] or g["exacte"]]
    de_exclus_curat = [g for g in de_exclus if g["curat"]]
    t = totaluri("curat")
    if t["probleme_cu_solutia_exacta"] > 50:
        verdict = "examenul compromis"
    elif t["probleme_cu_solutia_exacta"] == 0 and t["probleme_cu_suprapunere"] <= 10:
        verdict = "curat"
    else:
        verdict = "de curățat"
    pe_sablon: dict[str, dict] = {}
    for x in pe_prob:
        s = pe_sablon.setdefault(x["sablon"], {"probleme": 0, "cu_suprapunere": 0, "cu_solutia_exacta": 0})
        s["probleme"] += 1
        s["cu_suprapunere"] += bool(x["curat"]["fisiere_suprapunere"])
        s["cu_solutia_exacta"] += bool(x["curat"]["fisiere_solutie_exacta"])
    rez = {
        "n": N, "secunde": round(time.time() - t0, 1),
        "sha256_inainte": sha_inainte, "sha256_dupa": sha_dupa, "sha_neschimbat": sha_inainte == sha_dupa,
        "fisiere_scanate": fisiere, "gb_scanati": round(octeti / 1e9, 4),
        "fisiere_curat": fisiere_curat, "gb_curat": round(octeti_curat / 1e9, 4),
        "totaluri_curat": t, "totaluri_tot": totaluri("tot"),
        "de_exclus_curat": {"fisiere": len(de_exclus_curat),
                            "octeti": sum(g["octeti"] for g in de_exclus_curat),
                            "procent_din_curat": round(100 * sum(g["octeti"] for g in de_exclus_curat)
                                                       / max(octeti_curat, 1), 4)},
        "de_exclus_tot": {"fisiere": len(de_exclus), "octeti": sum(g["octeti"] for g in de_exclus)},
        "verdict": verdict, "pe_sablon": pe_sablon, "pe_problema": pe_prob,
        "fisiere_atinse": [{k: g[k] for k in ("i", "curat", "octeti", "sursa", "cale", "exacte", "nume")}
                           | {"atinse": {probleme[p]["id"]: v for p, v in g["atinse"].items()}} for g in gasite],
    }
    iesire.mkdir(parents=True, exist_ok=True)
    with open(iesire / "fisiere_de_exclus.txt", "w", encoding="utf-8", newline="\n") as f:
        for g in de_exclus:
            f.write(f"{g['i']}\t{g['sha256']}\t{g['sursa']}\t{g['cale']}\n")
    f_rez.write_text(json.dumps(rez, ensure_ascii=False, indent=1), encoding="utf-8")
    return rez


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="comanda", required=True)
    r = sub.add_parser("ruleaza", help="verificarea, o singură dată")
    r.add_argument("--examen", default=str(EXAMEN))
    r.add_argument("--cod", default=str(COD))
    r.add_argument("--iesire", default=str(IESIRE))
    r.add_argument("--procese", type=int, default=12)
    a = ap.parse_args(argv)
    rez = ruleaza(Path(a.examen), Path(a.cod), Path(a.iesire), a.procese, jurnal=lambda m: print(m, flush=True))
    print(json.dumps({k: rez[k] for k in ("secunde", "fisiere_scanate", "gb_curat", "totaluri_curat",
                                          "de_exclus_curat", "sha_neschimbat", "verdict")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
