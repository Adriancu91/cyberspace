"""E3, căutarea v2 (S29, 26 octombrie 2026; comanda C-21 punctul 1 a lui Adrian, 26 oct 17:45; pașii din plan/coada.md).

Azi răspunsul e în primele 3 bucăți la 72 % și în primele 5 la 80 % (S26), iar în context încap de obicei doar 2 bucăți
(S27): ordinea contează. Aici:
  (a) rădăcini românești: un index NOU, separat (`lucru/e3/index_radacini.sqlite`), cu aceleași bucăți (același rowid)
      dar fiecare cuvânt trecut prin `radacina`; căutarea aleasă la S25 rulează pe ambele indexuri (pe cel nou, cu
      cuvintele interogării trecute prin `radacina`) și listele se unesc cu RRF (Reciprocal Rank Fusion), k = 60;
  (b) reordonarea „probabilitatea întrebării”: primele 20 de bucăți se ordonează după log p(întrebare | bucată), dat de
      modelul nostru (judecătorul), cu promptul fix „Text: …⏎Întrebare:”, fără întâmplare.

Rădăcinile: scrise de noi după DESCRIEREA publică a algoritmului Snowball pentru română (Martin Porter și colaboratorii,
snowballstem.org/algorithms/romanian/stemmer.html: regiunile RV, R1, R2 și pașii 0–4); niciun cod copiat.

Codul stă în unelte/: portul „memorie” din kronos/contracte.py e memoria cuvintelor (cod, caracteristici), nu căutarea de
bucăți; un port „cautare” (intrebare → bucăți ordonate) ar fi o schimbare în kronos/ și rămâne la Adrian.

    python -X utf8 unelte/e3_reordonare.py index-radacini          # lucru/e3/index_radacini.sqlite (+ .json)
    python -X utf8 unelte/e3_reordonare.py validare --judecator 438  # lucru/e3/validare_s29.json (placa, scurt)

Nu atinge kronos/, examenul BPB, paznicul, jurnalul, datele de examen, text_v3, listele S26/S27, lucru/e3/index.sqlite
(doar citire), unelte/verificator_text.py, modelele.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import statistics
import sys
import time
from collections import Counter
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Iterable

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from unelte import e3_memorie as e3  # noqa: E402
from unelte.verificator_text import cuvinte  # noqa: E402

K_RRF = 60
CATE_REORDONATE = 20
LOT_JUDECATOR = 10
K_S29 = (1, 3, 5, 20)
VARIANTE_S29 = ("s25", "rrf", "s25_reord", "rrf_reord")  # de la cea mai simplă la cea mai complicată
IESIRE_VALIDARE = "validare_s29.json"

# ---------------------------------------------------------------- (a) rădăcinile românești

VOCALE = frozenset("aăâeiîou")


def _vocala(c: str) -> bool:
    return c in VOCALE


def _dupa_prima(cuv: str, de_la: int) -> int:
    """Poziția de după prima consoană care urmează unei vocale, căutând de la `de_la` (R1 / R2)."""
    for i in range(max(de_la, 1), len(cuv)):
        if not _vocala(cuv[i]) and _vocala(cuv[i - 1]):
            return i + 1
    return len(cuv)


def regiuni(cuv: str) -> tuple[int, int, int]:
    """(RV, R1, R2), ca poziții de început, pe cuvântul cu i/u dintre vocale deja marcate (I/U = consoane)."""
    n = len(cuv)
    rv = n
    if n >= 2:
        if not _vocala(cuv[1]):  # a doua literă e consoană: după următoarea vocală
            rv = next((i + 1 for i in range(2, n) if _vocala(cuv[i])), n)
        elif _vocala(cuv[0]):  # primele două sunt vocale: după următoarea consoană
            rv = next((i + 1 for i in range(2, n) if not _vocala(cuv[i])), n)
        else:  # consoană + vocală: după a treia literă
            rv = min(3, n)
    r1 = _dupa_prima(cuv, 1)
    r2 = _dupa_prima(cuv, r1)
    return rv, r1, r2


def _cea_mai_lunga(cuv: str, sufixe: Iterable[str]) -> str | None:
    gasite = [s for s in sufixe if cuv.endswith(s)]
    return max(gasite, key=len) if gasite else None


_PAS0 = {"ul": "", "ului": "", "aua": "a", "ea": "e", "ele": "e", "elor": "e", "ii": "i", "iua": "i", "iei": "i",
         "iile": "i", "iilor": "i", "ilor": "i", "ile": "i", "atei": "at", "ație": "ați", "ația": "ați"}
_PAS1 = {**{s: "abil" for s in ("abilitate", "abilitati", "abilităi", "abilități")},
         "ibilitate": "ibil",
         **{s: "iv" for s in ("ivitate", "ivitati", "ivităi", "ivități")},
         **{s: "ic" for s in ("icitate", "icitati", "icităi", "icități", "icator", "icatori", "iciv", "iciva", "icive",
                              "icivi", "icivă", "ical", "icala", "icale", "icali", "icală")},
         **{s: "at" for s in ("ativ", "ativa", "ative", "ativi", "ativă", "ațiune", "atoare", "ator", "atori", "ătoare",
                              "ător", "ători")},
         **{s: "it" for s in ("itiv", "itiva", "itive", "itivi", "itivă", "ițiune", "itoare", "itor", "itori")}}
_PAS2_STERGE = frozenset(
    "at ata ată ati ate ut uta ută uti ute it ita ită iti ite ic ica ice ici ică abil abila abile abili abilă ibil ibila "
    "ibile ibili ibilă oasa oasă oase os osi oși ant anta ante anti antă ator atori itate itati ităi ități iv iva ive ivi "
    "ivă".split())
_PAS2_IST = frozenset("ism isme ist ista iste isti istă iști".split())
_PAS2_IUNE = frozenset(("iune", "iuni"))
_PAS3_DUPA_CONSOANA = frozenset(
    "are ere ire âre ind ând indu ându eze ească ez ezi ează esc ești ește ăsc ăști ăște am ai au eam eai ea eați eau "
    "iam iai ia iați iau ui ași arăm arăți ară uși urăm urăți ură iși irăm irăți iră âi âși ârăm ârăți âră asem aseși "
    "ase aserăm aserăți aseră isem iseși ise iserăm iserăți iseră âsem âseși âse âserăm âserăți âseră usem useși use "
    "userăm userăți useră".split())
_PAS3_STERGE = frozenset(
    "ăm ați em eți im iți âm âți seși serăm serăți seră sei se sesem seseși sese seserăm seserăți seseră".split())
_PAS4 = ("a", "e", "i", "ie", "ă")


def _marcheaza(cuv: str) -> str:
    """i și u între două vocale devin I și U (se poartă ca niște consoane)."""
    litere = list(cuv)
    for i in range(1, len(litere) - 1):
        if litere[i] in "iu" and _vocala(litere[i - 1]) and _vocala(litere[i + 1]):
            litere[i] = litere[i].upper()
    return "".join(litere)


@lru_cache(maxsize=None)
def radacina(cuvant: str) -> str:
    """Rădăcina unui cuvânt românesc (litere mici; ş/ţ cu sedilă trec în ș/ț). Pașii descrierii Snowball:
    0 (pluraluri, articolul hotărât), 1 (sufixe compuse, repetat), 2 (sufixe obișnuite), 3 (sufixele verbelor, doar dacă
    1 și 2 n-au scos nimic), 4 (vocala de la sfârșit)."""
    cuv = _marcheaza(cuvant.lower().translate(e3._CEDILE))
    rv, r1, r2 = regiuni(cuv)

    s = _cea_mai_lunga(cuv, _PAS0)
    if s and len(cuv) - len(s) >= r1 and not (s == "ile" and cuv[:-3].endswith("ab")):
        cuv = cuv[: -len(s)] + _PAS0[s]

    scos = False
    while True:
        s = _cea_mai_lunga(cuv, _PAS1)
        if not s or len(cuv) - len(s) < r1:
            break
        cuv = cuv[: -len(s)] + _PAS1[s]
        scos = True

    s = _cea_mai_lunga(cuv, _PAS2_STERGE | _PAS2_IST | _PAS2_IUNE)
    if s and len(cuv) - len(s) >= r2:
        if s in _PAS2_STERGE:
            cuv, scos = cuv[: -len(s)], True
        elif s in _PAS2_IST:
            cuv, scos = cuv[: -len(s)] + "ist", True
        elif cuv[: -len(s)].endswith("ț"):
            cuv, scos = cuv[: -len(s) - 1] + "t", True

    if not scos:
        in_rv = [x for x in _PAS3_DUPA_CONSOANA | _PAS3_STERGE if cuv.endswith(x) and len(cuv) - len(x) >= rv]
        if in_rv:
            s = max(in_rv, key=len)
            inainte = len(cuv) - len(s) - 1
            if s in _PAS3_STERGE:
                cuv = cuv[: -len(s)]
            elif inainte >= rv and (not _vocala(cuv[inainte]) or cuv[inainte] == "u"):
                cuv = cuv[: -len(s)]

    s = _cea_mai_lunga(cuv, _PAS4)
    if s and len(cuv) - len(s) >= rv:
        cuv = cuv[: -len(s)]
    return cuv.lower() or cuvant


def text_radacini(text: str) -> str:
    """Textul pentru indexul cu rădăcini: cuvintele (ca la verificator) trecute prin `radacina`, despărțite de spații."""
    return " ".join(radacina(c) for c in cuvinte(e3.curata(text)))


_IN_GHILIMELE = re.compile(r'"((?:[^"]|"")*)"')


def interogare_radacini(interogare: str) -> str:
    """Aceeași interogare FTS5, cu fiecare cuvânt dintre ghilimele trecut prin `radacina` (operatorii rămân)."""
    def schimba(m: re.Match[str]) -> str:
        cuv = m.group(1).replace('""', '"').split()
        return '"' + " ".join(radacina(c) for c in cuv).replace('"', '""') + '"'
    return _IN_GHILIMELE.sub(schimba, interogare)


def cmd_index_radacini(lucru: Path) -> dict[str, Any]:
    """Indexul nou, separat: aceleași bucăți (același rowid, articol, nr, sursă), textul trecut prin rădăcini.
    `index.sqlite` se deschide doar pentru citire."""
    cale = lucru / "index_radacini.sqlite"
    if cale.exists():
        raise SystemExit("indexul cu rădăcini există deja")
    start = time.time()
    sursa = sqlite3.connect(f"file:{(lucru / 'index.sqlite').as_posix()}?mode=ro", uri=True)
    con = e3.creeaza(cale)
    lot: list[tuple[int, str, str, int, str]] = []
    n = 0
    for rowid, text, articol, nr, sursa_ in sursa.execute("SELECT rowid, text, articol, nr, sursa FROM bucati"):
        lot.append((rowid, text_radacini(text), articol, nr, sursa_))
        n += 1
        if len(lot) >= 50_000:
            con.executemany("INSERT INTO bucati(rowid, text, articol, nr, sursa) VALUES (?, ?, ?, ?, ?)", lot)
            con.commit()
            lot = []
            print(f"{datetime.now():%H:%M:%S} {n} bucăți, {radacina.cache_info().currsize} cuvinte distincte", flush=True)
    con.executemany("INSERT INTO bucati(rowid, text, articol, nr, sursa) VALUES (?, ?, ?, ?, ?)", lot)
    con.commit()
    con.execute("INSERT INTO bucati(bucati) VALUES ('optimize')")
    con.commit()
    con.close()
    sursa.close()
    info = {"bucati": n, "cuvinte_distincte": radacina.cache_info().currsize,
            "marime_mb": round(cale.stat().st_size / 2**20, 1), "ram_maxim_mb": e3._ram_maxim_mb(),
            "secunde": round(time.time() - start, 1), "scris": datetime.now().isoformat(timespec="seconds")}
    e3._scrie_json(lucru / "index_radacini.json", info)
    return info


# ---------------------------------------------------------------- RRF

def rrf(liste: list[list[int]], k: int = K_RRF) -> list[int]:
    """Reciprocal Rank Fusion: scorul = suma 1 / (k + loc) pe liste (loc de la 1); la egalitate, ordinea primei apariții
    (întâi prima listă)."""
    scor: dict[int, float] = {}
    ordine: dict[int, int] = {}
    for lista in liste:
        for loc, x in enumerate(lista, 1):
            scor[x] = scor.get(x, 0.0) + 1.0 / (k + loc)
            ordine.setdefault(x, len(ordine))
    return sorted(scor, key=lambda x: (-scor[x], ordine[x]))


def coboara_liste(gasite: list[dict[str, Any]], liste: dict[str, set[str]]) -> list[dict[str, Any]]:
    """Ca în varianta aleasă la S25 („_liste”): paginile-listă trec după celelalte, ordinea rămâne (sortare stabilă)."""
    return sorted(gasite, key=lambda g: g["articol"] in liste["fraze_lista"])


def cauta_rrf(con: sqlite3.Connection, con_r: sqlite3.Connection, intrebare: str, varianta: str,
              liste: dict[str, set[str]], cate: int = e3.CATE_PENTRU_LISTE) -> tuple[list[dict], list[dict]]:
    """(lista S25 simplă, lista unită RRF) — ambele de cel mult `cate` bucăți, cu textul ORIGINAL al bucăților."""
    simpla = e3.cauta(con, intrebare, varianta, k=cate, liste=liste)
    rad = e3.cauta(con_r, intrebare, varianta, k=cate, liste=liste, transforma=interogare_radacini)
    dupa_id = {g["rowid"]: g for g in simpla}
    lipsa = [g["rowid"] for g in rad if g["rowid"] not in dupa_id]
    for i in range(0, len(lipsa), 500):
        parte = lipsa[i:i + 500]
        for rowid, text, articol, sursa in con.execute(
                f"SELECT rowid, text, articol, sursa FROM bucati WHERE rowid IN ({','.join('?' * len(parte))})", parte):
            dupa_id[rowid] = {"rowid": rowid, "text": text, "articol": articol, "sursa": sursa}
    unite = [dupa_id[x] for x in rrf([[g["rowid"] for g in simpla], [g["rowid"] for g in rad]])]
    return simpla, coboara_liste(unite, liste)[:cate]


# ---------------------------------------------------------------- (b) judecătorul

def prompt_judecator(bucata: str) -> str:
    return f"Text: {bucata.strip()}\nÎntrebare:"


def scoruri_intrebare(model: Any, intrebare: str, texte: list[str]) -> list[tuple[float, int]]:
    """Pentru fiecare bucată: (log p(întrebare | bucată), câte simboluri are întrebarea). Un singur lot, fără
    întâmplare; dacă nu încape în context, din bucată se păstrează sfârșitul (lângă întrebare)."""
    import torch
    import torch.nn.functional as F

    if not texte:
        return []
    tok, ctx = model.tok, model.setari["context"]
    q = tok.codifica(" " + intrebare.strip())[: ctx - 1]
    secvente, inceputuri = [], []
    for t in texte:
        p = tok.codifica(prompt_judecator(t))[-(ctx - len(q)):]
        secvente.append(p + q)
        inceputuri.append(len(p))
    model.retea.eval()
    tinta = torch.tensor(q, dtype=torch.long, device=model.dispozitiv)
    rez = []
    with torch.no_grad():
        for j in range(0, len(secvente), LOT_JUDECATOR):  # loturi mici: placa sub 7.000 MB (S29, prima rulare: 7.942)
            lot = secvente[j:j + LOT_JUDECATOR]
            x = torch.zeros((len(lot), max(len(s) for s in lot)), dtype=torch.long)
            for i, s in enumerate(lot):
                x[i, : len(s)] = torch.tensor(s, dtype=torch.long)
            logits = model.retea(x.to(model.dispozitiv), None)
            for i, start in enumerate(inceputuri[j:j + LOT_JUDECATOR]):
                logp = F.log_softmax(logits[i, start - 1: start - 1 + len(q)].float(), dim=-1)  # doar pozițiile întrebării
                rez.append((float(logp.gather(-1, tinta[:, None]).sum()), len(q)))
            del logits
    if model.dispozitiv.type == "cuda":
        torch.cuda.empty_cache()  # loturile au lungimi diferite; altfel memoria păstrată crește
    return rez


def reordoneaza(gasite: list[dict[str, Any]], scoruri: dict[int, tuple[float, int]], normalizat: bool = True,
                cate: int = CATE_REORDONATE) -> list[dict[str, Any]]:
    """Primele `cate` bucăți ordonate după scor (mare = mai bine; la egalitate ordinea căutării), restul neatins."""
    def scor(g: dict[str, Any]) -> float:
        s, n = scoruri[g["rowid"]]
        return s / n if normalizat else s
    sus = sorted(gasite[:cate], key=lambda g: -scor(g))
    return sus + gasite[cate:]


# ---------------------------------------------------------------- măsurarea pe validare

def _bucati_incap(tok: Any, intrebare: str, gasite: list[dict[str, Any]]) -> int:
    return e3.cate_incap(tok, intrebare, gasite[: e3.K_E3]) if tok is not None else 0


def masoara(con: sqlite3.Connection, con_r: sqlite3.Connection, intrebari: list[dict[str, Any]], varianta: str,
            liste: dict[str, set[str]], judecator: Callable[[str, list[str]], list[tuple[float, int]]],
            tok: Any = None, paznic: Callable[[], None] = lambda: None) -> list[dict[str, Any]]:
    """Pentru fiecare întrebare și fiecare variantă (plus reordonarea nenormalizată): locul primei bucăți bune
    (potrivirea S16), câte bucăți încap în 448 de simboluri (regula S27) și timpii."""
    rez = []
    for i, q in enumerate(intrebari):
        if i % 20 == 0:
            paznic()
        t0 = time.perf_counter()
        simpla, unite = cauta_rrf(con, con_r, q["intrebare"], varianta, liste)
        t1 = time.perf_counter()
        de_notat = {g["rowid"]: g["text"] for g in simpla[:CATE_REORDONATE] + unite[:CATE_REORDONATE]}
        ids = list(de_notat)
        scoruri = dict(zip(ids, judecator(q["intrebare"], [de_notat[x] for x in ids])))
        t2 = time.perf_counter()
        ordini = {"s25": simpla, "rrf": unite,
                  "s25_reord": reordoneaza(simpla, scoruri), "rrf_reord": reordoneaza(unite, scoruri),
                  "s25_reord_nenorm": reordoneaza(simpla, scoruri, False),
                  "rrf_reord_nenorm": reordoneaza(unite, scoruri, False)}
        rez.append({"intrebare": q["intrebare"], "raspuns": q["raspuns"], "tip": q.get("tip"),
                    "loc": {v: e3.primul_bun(o, q["raspuns"]) for v, o in ordini.items()},
                    "incap": {v: _bucati_incap(tok, q["intrebare"], o) for v, o in ordini.items()},
                    "ordine_nenorm_diferita": [g["rowid"] for g in ordini["rrf_reord"][:CATE_REORDONATE]]
                    != [g["rowid"] for g in ordini["rrf_reord_nenorm"][:CATE_REORDONATE]],
                    "secunde_cautare": t1 - t0, "secunde_judecator": t2 - t1, "bucati_notate": len(ids)})
    return rez


def rezumat(rez: list[dict[str, Any]]) -> dict[str, Any]:
    variante = list(rez[0]["loc"]) if rez else []
    return {v: {**e3.procente([r["loc"][v] for r in rez], K_S29),
                "incap": dict(sorted(Counter(r["incap"][v] for r in rez).items()))} for v in variante}


def alege(pe_variante: dict[str, Any], variante: Iterable[str] = VARIANTE_S29) -> str:
    """Cea mai bună la k = 3 (bune); la egalitate, cea mai simplă (ordinea din VARIANTE_S29)."""
    variante = list(variante)
    return max(variante, key=lambda v: (pe_variante[v]["k3"]["bune"], -variante.index(v)))


def cmd_validare(lucru: Path, text_v3: Path, judecator_exp: int, incarca: Callable[..., Any] | None = None,
                 paznic: Callable[[], None] | None = None) -> dict[str, Any]:
    from unelte import e1_intrebari_nascute as e1

    start = time.time()
    vechi, noi, candidate = e3.intrebari_validare_s25(text_v3)
    val25 = json.loads((lucru / "validare_s25.json").read_text(encoding="utf-8"))
    varianta = val25["aleasa"]
    liste = e3.incarca_liste(lucru)
    model, fisa = (incarca or e1.modelul)(judecator_exp)
    paznic = paznic or e1.paznic_placa
    judecator = lambda intrebare, texte: scoruri_intrebare(model, intrebare, texte)  # noqa: E731
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats()
    except ImportError:
        torch = None  # type: ignore[assignment]
    con = sqlite3.connect(f"file:{(lucru / 'index.sqlite').as_posix()}?mode=ro", uri=True)
    con_r = sqlite3.connect(f"file:{(lucru / 'index_radacini.sqlite').as_posix()}?mode=ro", uri=True)
    rez = {}
    for nume, intrebari in (("s1024", vechi), ("s2048", noi)):
        rez[nume] = masoara(con, con_r, intrebari, varianta, liste, judecator, model.tok, paznic)
        print(f"{datetime.now():%H:%M:%S} {nume}: " + json.dumps(
            {v: x["k3"] for v, x in rezumat(rez[nume]).items()}, ensure_ascii=False), flush=True)
    con.close()
    con_r.close()
    toate = rez["s1024"] + rez["s2048"]
    pe = {"s1024": rezumat(rez["s1024"]), "s2048": rezumat(rez["s2048"]), "impreuna": rezumat(toate)}
    reprodus = all(pe[n]["s25"][f"k{k}"]["bune"] == val25["variante"][varianta][n]["s16"][f"k{k}"]["bune"]
                   for n in ("s1024", "s2048") for k in e3.K)
    aleasa = alege(pe["impreuna"])
    memorie = None
    if torch is not None and torch.cuda.is_available():
        memorie = round(torch.cuda.max_memory_allocated() / 2**20, 1)
    secunde = lambda cheie: {"median": round(statistics.median(r[cheie] for r in toate), 3),  # noqa: E731
                             "maxim": round(max(r[cheie] for r in toate), 3)}
    info = {"varianta_s25": varianta, "judecator": fisa["id"], "judecator_linie": fisa.get("linie"),
            "intrebari": {"s1024": len(vechi), "s2048": len(noi)}, "candidate_in_text_v3": candidate,
            "s25_reprodusa_k1_5_20": reprodus, "variante": pe, "aleasa": aleasa,
            "criteriu": "cele mai multe bune la k = 3 pe 1024 + 2048 împreună, potrivirea S16; la egalitate cea mai simplă "
                        f"({' < '.join(VARIANTE_S29)})",
            "k_rrf": K_RRF, "reordonate": CATE_REORDONATE, "prompt_judecator": prompt_judecator("…") + " <întrebarea>",
            "ordine_nenorm_diferita": sum(r["ordine_nenorm_diferita"] for r in toate),
            "secunde_cautare": secunde("secunde_cautare"), "secunde_judecator": secunde("secunde_judecator"),
            "memorie_placa_max_mb": memorie, "ram_maxim_mb": e3._ram_maxim_mb(),
            "secunde": round(time.time() - start, 1), "scris": datetime.now().isoformat(timespec="seconds"),
            "toate": rez}
    e3._scrie_json(lucru / IESIRE_VALIDARE, info)
    return info


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="E3, căutarea v2 (S29): rădăcini + RRF și reordonarea cu judecătorul.")
    parser.add_argument("--lucru", default=e3._relativ(e3.LUCRU))
    sub = parser.add_subparsers(dest="pas", required=True)
    sub.add_parser("index-radacini")
    v = sub.add_parser("validare")
    v.add_argument("--judecator", type=int, required=True)
    args = parser.parse_args(argv)
    lucru = RADACINA / args.lucru
    if args.pas == "index-radacini":
        info = cmd_index_radacini(lucru)
    else:
        info = cmd_validare(lucru, RADACINA / e3.TEXT_V3, args.judecator)
        info = {k: x for k, x in info.items() if k != "toate"}
    print(json.dumps(info, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
