"""Memoria de cod a lui Kronos-Cod („rege / regat”, S71, C-60 pasul D; aprobat de Adrian 3 nov 2026 11:45).

Întrebarea: dacă înaintea problemei îi punem modelului cele mai asemănătoare 2–4 funcții din exercițiile S69, scrie
corpuri mai bune? Nimic de aici nu antrenează, nu descarcă și nu schimbă modelele, examenul sau cutia.

Alegerile:
  - indexul: exercițiile S69 de la antrenare (`exercitii.tsv`, `deoparte = 0`; cele ținute deoparte NU intră), cu textul
    refăcut din `complet/cod.jsonl` exact ca la S69 (`functii.descrie`, suma normalizată trebuie să fie aceeași; la
    funcțiile S68 cu importuri, rândurile de import în față);
  - căutarea: SQLite FTS5 cu BM25 (ca la E3, `unelte/e3_memorie.py`), tokenizerul `unicode61` (desparte și la „_”).
    Se caută după antet + explicație: numele funcției, argumentele și docstringul; întrebarea = cuvintele din enunț
    (antetul + docstringul problemei), fiecare o dată, legate cu OR;
  - ce primește modelul: <|endoftext|> + funcțiile alese (fiecare urmată de un rând gol) + enunțul, ca un fișier de cod.
    Cea mai asemănătoare stă ultima, lângă problemă. Problema are întâietate: memoria primește doar ce rămâne din
    contextul de 512 după enunț, simbolul de început și `REZERVA` simboluri pentru corp; o funcție care nu încape e
    sărită (se trece la următoarea), cel mult `MAX_FUNCTII`. Dacă corpul scris trece de rezervă, fereastra de 512 taie
    întâi din memorie (de la stânga), niciodată din enunț cât timp corpul are sub 512 − enunț simboluri;
  - scurgerea: fiecare funcție găsită trece prin `scurgere.scaneaza_text` pe problemele setului; cele cu o suprapunere
    de 13 simboluri sau cu soluția întreagă sunt scoase (și numărate) ÎNAINTE de alegere.

Comenzile:
    python -X utf8 unelte/kronos_cod/memorie.py index                 # lucru/kronos_cod/memorie/index.sqlite (+ .json)
    python -X utf8 unelte/kronos_cod/memorie.py scurgere              # setul de probă (cu detalii) + ascuns2 (doar numărul)
    python -X utf8 unelte/kronos_cod/memorie.py model --config C --stare S --iesire J [--lot 2 --memorie-max 6500]
        # ca `examen_cod.py model --set proba`, dar cu memoria în față; se notează cu `examen_cod.py noteaza`

Ies doar în lucru/kronos_cod/memorie/ (nu în Git: codul descărcat are licențele lui).
"""

from __future__ import annotations

import argparse
import ast
import csv
import dataclasses
import json
import re
import sqlite3
import sys
import time
from multiprocessing import Pool
from pathlib import Path

RADACINA = Path(__file__).resolve().parents[2]
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from unelte.kronos_cod import scurgere  # noqa: E402
from unelte.kronos_cod.functii import (ASCUNSE, EXERCITII, IESIRE as FUNCTII, citeste_blande,  # noqa: E402
                                        descrie, functiile)
from unelte.kronos_cod.tokenizer_cod import COD, loturi  # noqa: E402

IESIRE = RADACINA / "lucru" / "kronos_cod" / "memorie"
INDEX = IESIRE / "index.sqlite"
CONTEXT = 512
REZERVA = 128
MAX_FUNCTII = 4
CANDIDATI = 30
csv.field_size_limit(1 << 30)

_CUVANT = re.compile(r"[A-Za-z][A-Za-z0-9]*")


# ---------------------------------------------------------------------------------------------------- indexul

def citeste_cerute(f_tsv: Path) -> dict[int, list[dict]]:
    """Din exercitii.tsv (S69): rândul din cod.jsonl → exercițiile de la antrenare (deoparte = 0) din el."""
    out: dict[int, list[dict]] = {}
    with open(f_tsv, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            if r["deoparte"] != "0":
                continue
            out.setdefault(int(r["i"]), []).append({"linia": int(r["linia"]), "sha": r["sha256_normalizat"],
                                                   "pachet": r["pachet"], "cale": r["cale"]})
    return out


def text_cautare(nod) -> str:
    """Ce se caută: numele, argumentele și docstringul funcției."""
    try:
        arg = ast.unparse(nod.args)
    except Exception:  # noqa: BLE001
        arg = ""
    return f"{nod.name} {arg}\n{ast.get_docstring(nod) or ''}"


def exercitii_din_fisier(text: str, cerute: list[dict], importuri: dict) -> tuple[list[dict], int]:
    """(exercițiile găsite cu textul lor, câte n-au mai fost găsite)."""
    try:
        arbore = ast.parse(text)
    except (SyntaxError, ValueError, RecursionError, MemoryError):
        return [], len(cerute)
    linii = text.splitlines()
    pe_linie = {n.lineno: n for n in functiile(arbore)}
    out, lipsa = [], 0
    for f in cerute:
        nod = pe_linie.get(f["linia"])
        try:
            d = descrie(nod, linii) if nod is not None else None
        except RecursionError:
            d = None
        if d is None or d["sha"] != f["sha"]:
            lipsa += 1
            continue
        imp = importuri.get(f["sha"])
        out.append({"sha": f["sha"], "pachet": f["pachet"], "cale": f["cale"], "cautare": text_cautare(nod),
                    "text": ("\n".join(imp) + "\n\n\n" + d["text"]) if imp else d["text"]})
    return out, lipsa


_STARE: dict = {}


def _init(stare: dict) -> None:
    global _STARE
    _STARE = stare


def _lot(lot) -> tuple[list[dict], int]:
    start, randuri = lot
    out, lipsa = [], 0
    for j, rand in enumerate(randuri):
        cerute = _STARE["cerute"].get(start + j)
        if cerute:
            g, l = exercitii_din_fisier(json.loads(rand)["text"], cerute, _STARE["importuri"])
            out.extend(g)
            lipsa += l
    return out, lipsa


def creeaza_tabel(con: sqlite3.Connection) -> None:
    con.execute("CREATE VIRTUAL TABLE functii USING fts5(cautare, text UNINDEXED, sha UNINDEXED, pachet UNINDEXED, "
                "cale UNINDEXED, tokenize='unicode61')")


def index(cod: Path = COD, exercitii: Path = EXERCITII, functii_dir: Path = FUNCTII, cale: Path = INDEX,
          procese: int = 12, jurnal=print) -> dict:
    cale = Path(cale)
    if cale.exists():
        raise SystemExit(f"{cale} există deja: indexul se face o singură dată")
    t0 = time.time()
    cerute = citeste_cerute(Path(exercitii) / "exercitii.tsv")
    n_cerute = sum(len(v) for v in cerute.values())
    importuri = {s: v for s, v in citeste_blande(Path(functii_dir) / "blande.tsv").items() if v}
    jurnal(f"exerciții de la antrenare cerute: {n_cerute} (din {len(cerute)} fișiere)")
    cale.parent.mkdir(parents=True, exist_ok=True)
    tmp = cale.with_suffix(".tmp")
    tmp.unlink(missing_ok=True)
    con = sqlite3.connect(tmp)
    creeaza_tabel(con)
    gasite, lipsa, vazute = 0, 0, set()
    with Pool(procese, initializer=_init, initargs=({"cerute": cerute, "importuri": importuri},)) as pool:
        for k, (fs, l) in enumerate(pool.imap(_lot, loturi(Path(cod) / "cod.jsonl"), chunksize=1), 1):
            lipsa += l
            noi = [f for f in fs if f["sha"] not in vazute]
            vazute.update(f["sha"] for f in noi)
            con.executemany("INSERT INTO functii (cautare, text, sha, pachet, cale) VALUES (?, ?, ?, ?, ?)",
                            [(f["cautare"], f["text"], f["sha"], f["pachet"], f["cale"]) for f in noi])
            gasite += len(noi)
            if k % 20 == 0:
                jurnal(f"{k} loturi, {gasite} funcții în index, {time.time() - t0:.0f} s")
    con.commit()
    con.close()
    tmp.replace(cale)
    rez = {"cerute": n_cerute, "in_index": gasite, "negasite": lipsa, "secunde": round(time.time() - t0, 1),
           "fisier": str(cale), "octeti": cale.stat().st_size}
    cale.with_suffix(".json").write_text(json.dumps(rez, ensure_ascii=False, indent=1), encoding="utf-8")
    return rez


# ---------------------------------------------------------------------------------------------------- căutarea

def intrebare(enunt: str) -> str:
    """Interogarea FTS5: cuvintele din enunț (desparte la „_” și la ce nu e literă/cifră), fiecare o dată, cu OR."""
    cuvinte = []
    for c in _CUVANT.findall(enunt):
        c = c.lower()
        if c not in cuvinte and c not in ("def",):
            cuvinte.append(c)
    return " OR ".join(f'"{c}"' for c in cuvinte)


def cauta(con: sqlite3.Connection, enunt: str, k: int = CANDIDATI) -> list[dict]:
    q = intrebare(enunt)
    if not q:
        return []
    rez = con.execute("SELECT text, sha, pachet, bm25(functii) FROM functii WHERE functii MATCH ? "
                      "ORDER BY bm25(functii) LIMIT ?", (q, k)).fetchall()
    return [{"text": t, "sha": s, "pachet": p, "scor": round(-b, 4)} for t, s, p, b in rez]


def e_scurgere(text: str, idx: dict) -> bool:
    g = scurgere.scaneaza_text(text, idx)
    return bool(g and (g["atinse"] or g["exacte"]))


def alege(candidati: list[dict], enunt: str, idx: dict, numara, context: int = CONTEXT, rezerva: int = REZERVA,
          max_functii: int = MAX_FUNCTII) -> tuple[list[dict], int]:
    """(funcțiile alese, în ordinea găsirii; câte au fost scoase pentru scurgere). `numara(text)` = câte simboluri."""
    buget = context - 1 - numara(enunt) - rezerva
    alese, scoase = [], 0
    for c in candidati:
        if len(alese) >= max_functii:
            break
        if e_scurgere(c["text"], idx):
            scoase += 1
            continue
        n = numara(c["text"] + "\n")
        if n <= buget:
            alese.append(dict(c, simboluri=n))
            buget -= n
    return alese, scoase


def inceput(alese: list[dict]) -> str:
    """Textul pus înaintea enunțului: cea mai asemănătoare ultima, lângă problemă."""
    return "".join(c["text"] + "\n" for c in reversed(alese))


def _numarator():
    from module.tokenizer_bpe import TokenizerBPE
    from unelte.kronos_cod.functii import TOKENIZER

    tok = TokenizerBPE.incarca(str(TOKENIZER))
    return lambda t: len(tok.codifica_fara_speciale(t))


def cmd_scurgere(cale: Path = INDEX, iesire: Path = IESIRE, numara=None) -> dict:
    from dataclasses import asdict

    from unelte.kronos_cod.examen_cod import probleme_setului, set_proba

    numara = numara or _numarator()
    con = sqlite3.connect(cale)
    proba = [asdict(p) for p in set_proba()]
    idx = scurgere.indexeaza(proba)
    detalii, tot_scoase, tot_alese = [], 0, 0
    for p in proba:
        alese, scoase = alege(cauta(con, p["enunt"]), p["enunt"], idx, numara)
        detalii.append({"id": p["id"], "scoase": scoase, "alese": len(alese),
                        "simboluri_memorie": sum(c["simboluri"] for c in alese),
                        "functii": [{"sha": c["sha"][:12], "pachet": c["pachet"], "scor": c["scor"]} for c in alese]})
        tot_scoase += scoase
        tot_alese += len(alese)
    rez = {"proba": {"probleme": len(proba), "scoase": tot_scoase, "alese": tot_alese, "detalii": detalii}}
    dosar = Path(ASCUNSE["ascuns2"])
    sha0 = scurgere.sha256_fisier(dosar / "probleme.jsonl")
    asc = [asdict(p) for p in probleme_setului("ascuns", dosar)]
    idx = scurgere.indexeaza(asc)
    scoase_a = sum(alege(cauta(con, p["enunt"]), p["enunt"], idx, numara)[1] for p in asc)
    rez["ascuns2"] = {"probleme": len(asc), "scoase": scoase_a,
                      "sha_neschimbat": sha0 == scurgere.sha256_fisier(dosar / "probleme.jsonl")}
    del asc
    Path(iesire).mkdir(parents=True, exist_ok=True)
    (Path(iesire) / "scurgere.json").write_text(json.dumps(rez, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"proba": {k: v for k, v in rez["proba"].items() if k != "detalii"}, "ascuns2": rez["ascuns2"]}


# ---------------------------------------------------------------------------------------------------- modelul

def cmd_model(a) -> dict:
    """Ca `examen_cod.py model --set proba` (aceleași semințe, aceeași scriere a corpurilor), cu memoria în față."""
    from dataclasses import asdict

    import torch

    from unelte.kronos_cod import examen_cod, memorie_placa

    if a.iesire.exists():
        raise SystemExit(f"{a.iesire} există deja: răspunsurile se scriu o singură dată.")
    probleme = examen_cod.probleme_setului("proba", examen_cod.RADACINA)[: a.probleme or None]
    model = examen_cod.incarca_model(a.config, a.stare, a.dispozitiv)
    numara = (lambda t: len(model.tok.codifica_fara_speciale(t)))
    con = sqlite3.connect(a.index)
    idx = scurgere.indexeaza([asdict(p) for p in examen_cod.set_proba()])
    paza = memorie_placa.Paza(model.dispozitiv, a.memorie_max)
    t0 = time.perf_counter()
    raspunsuri, memorie, oprit = {}, {}, None
    try:
        paza.verifica()
        for k, p in enumerate(probleme):
            alese, scoase = alege(cauta(con, p.enunt), p.enunt, idx, numara, model.setari["context"], a.rezerva)
            cu_memorie = dataclasses.replace(p, enunt=inceput(alese) + p.enunt)
            memorie[p.id] = {"alese": len(alese), "scoase": scoase, "simboluri": sum(c["simboluri"] for c in alese),
                             "sha": [c["sha"][:12] for c in alese]}
            corpuri: list[str] = []
            for j0 in range(0, a.n, a.lot):
                generatoare = [torch.Generator(device="cpu").manual_seed(examen_cod.samanta_corp(a.samanta, k, j))
                               for j in range(j0, min(j0 + a.lot, a.n))]
                corpuri += examen_cod.scrie_corpuri(model, cu_memorie, generatoare, a.temperatura, a.max_simboluri,
                                                    paza)
                paza.verifica()
            raspunsuri[p.id] = corpuri
    except memorie_placa.MemoriePeste as e:
        oprit = str(e)
    meta = {"set": "proba", "probleme": len(raspunsuri), "n": a.n, "temperatura": a.temperatura,
            "samanta": a.samanta, "max_simboluri": a.max_simboluri, "lot": a.lot, "memorie_max_mb": a.memorie_max,
            "memorie_varf_mb": None if paza.varf is None else round(paza.varf), "config": str(a.config),
            "stare": str(a.stare), "dispozitiv": str(model.dispozitiv), "secunde": round(time.perf_counter() - t0, 1),
            "memorie_cod": {"index": str(a.index), "rezerva": a.rezerva, "max_functii": MAX_FUNCTII,
                            "pe_problema": memorie}}
    if oprit:
        meta.update({"incomplet": True, "oprit": oprit, "probleme_cerute": len(probleme)})
    a.iesire.parent.mkdir(parents=True, exist_ok=True)
    a.iesire.write_text(json.dumps({"meta": meta, "raspunsuri": raspunsuri}, ensure_ascii=False, indent=1),
                        encoding="utf-8")
    return {k: v for k, v in meta.items() if k != "memorie_cod"}


def main(argv=None) -> int:
    from unelte.kronos_cod import examen_cod, memorie_placa

    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("index")
    i.add_argument("--procese", type=int, default=12)
    sub.add_parser("scurgere")
    m = sub.add_parser("model")
    m.add_argument("--config", type=Path, required=True)
    m.add_argument("--stare", type=Path, required=True)
    m.add_argument("--iesire", type=Path, required=True)
    m.add_argument("--index", type=Path, default=INDEX)
    m.add_argument("--rezerva", type=int, default=REZERVA)
    m.add_argument("--n", type=int, default=examen_cod.RASPUNSURI_PE_PROBLEMA)
    m.add_argument("--temperatura", type=float, default=examen_cod.TEMPERATURA)
    m.add_argument("--samanta", type=int, default=examen_cod.SAMANTA_RASPUNSURI)
    m.add_argument("--max-simboluri", type=int, default=examen_cod.MAX_SIMBOLURI)
    m.add_argument("--probleme", type=int, default=0)
    m.add_argument("--dispozitiv", default="")
    m.add_argument("--lot", type=int, default=2)
    m.add_argument("--memorie-max", type=float, default=memorie_placa.MEMORIE_MAX_MB)
    a = ap.parse_args(argv)
    if a.cmd == "index":
        rez = index(procese=a.procese)
    elif a.cmd == "scurgere":
        rez = cmd_scurgere()
    else:
        rez = cmd_model(a)
    print(json.dumps(rez, ensure_ascii=False, indent=1))
    return 3 if isinstance(rez, dict) and rez.get("incomplet") else 0


if __name__ == "__main__":
    raise SystemExit(main())
