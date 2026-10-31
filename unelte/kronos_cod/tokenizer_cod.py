"""Kronos-Cod: tokenizerul pe cod (S55, C-45, 31 octombrie 2026). Pre-înregistrarea:
docs/preinregistrari/2026-10-31_kronos_cod_tokenizer.md.

Datele: `lucru/kronos_cod/complet/cod.jsonl` (S46). Un fișier intră doar dacă e curat (nu e în `aproape_duplicate.json`)
și nu e în lista S53 (`lucru/kronos_cod/scurgere/fisiere_de_exclus.txt`, prima coloană = indicele din cod.jsonl, numărat
pe rândurile nevide, ca la S53). Din rest, partea de VALIDARE = fișierele cu primul octet al SHA-256 al textului (UTF-8)
mai mic decât 3 (3/256 ≈ 1,17 %); ea nu intră nici la tokenizer, nici, mai târziu, la antrenarea modelului. Eșantionul
tokenizerului = fișierele de antrenare cu al doilea octet al aceleiași sume mai mic decât 70 (70/256 ≈ 27 %, ~1 GB).

Tokenizerul: BPE pe octeți, regulile „cod” din module/tokenizer_bpe.py, 32.768 de simboluri (încape în uint16), cu
simbolurile speciale SPECIALE (primul = sfârșit de fișier). Bucățile care apar o singură dată în eșantion nu intră la
numărătoare (FRECVENTA_MINIMA).

Ce scrie (totul în `lucru/`, nimic în Git):
    lucru/kronos_cod/tokenizer/bpe_cod_32768.json (+ .sha256)  tokenizerul; se antrenează o singură dată
    lucru/kronos_cod/tokenizer/impartire.json                  câți octeți / fișiere pe parte, limbaj, sursă
    lucru/kronos_cod/tokenizer/masurare.json                   măsurătorile (a)–(c) și verdictul după praguri
    lucru/kronos_cod/simboluri/                                setul tokenizat: uint16, sfârșit de fișier între fișiere,
                                                               pe blocuri (reluare de unde a rămas) + rezumat.json

Comenzile:
    python -X utf8 -m unelte.kronos_cod.tokenizer_cod tot [--procese 12] [--limita-ore 9]   # toți pașii, cu reluare
    python -X utf8 -m unelte.kronos_cod.tokenizer_cod antreneaza | masoara | tokenizeaza
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import numpy as np

RADACINA = Path(__file__).resolve().parents[2]
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from module.tokenizer_bpe import TokenizerBPE, antreneaza_din_frecvente, frecvente_bucati  # noqa: E402
from unelte.kronos_cod.scurgere import EXAMEN, SHA_EXAMEN, sha256_fisier  # noqa: E402

COD = RADACINA / "lucru" / "kronos_cod" / "complet"
EXCLUS = RADACINA / "lucru" / "kronos_cod" / "scurgere" / "fisiere_de_exclus.txt"
DIR_TOK = RADACINA / "lucru" / "kronos_cod" / "tokenizer"
DIR_SIMB = RADACINA / "lucru" / "kronos_cod" / "simboluri"
W2 = RADACINA / "date" / "ws" / "bpe_16384.json"
MARIME = 32_768
SPECIALE = ("<|endoftext|>", "<|python|>", "<|rust|>", "<|c|>")  # sfârșit de fișier; etichetele de limbaj, rezervate
PRAG_VALIDARE = 3      # primul octet al sumei < 3 → validare
PRAG_ESANTION = 70     # al doilea octet < 70 → eșantionul tokenizerului (doar din antrenare)
FRECVENTA_MINIMA = 2
BLOC = 5_000           # rânduri din cod.jsonl pe bloc (lot de lucru și fișier de simboluri)
LIMBAJE = ("python", "rust", "c")
SPATIU_MINIM_GB = 40
PRAG_OCTETI = 3.0
PRAG_FATA_DE_W2 = 0.15


# --- împărțirea ---------------------------------------------------------------------------------------------------

def parte(i: int, text: str, aproape: set[int], scurgere: set[int]) -> str:
    """Partea unui fișier: „aproape_duplicat”, „scurgere”, „validare”, „antrenare” sau „esantion” (antrenare + eșantion)."""
    if i in aproape:
        return "aproape_duplicat"
    if i in scurgere:
        return "scurgere"
    h = hashlib.sha256(text.encode("utf-8")).digest()
    if h[0] < PRAG_VALIDARE:
        return "validare"
    return "esantion" if h[1] < PRAG_ESANTION else "antrenare"


def citeste_excluse(cod: Path = COD, exclus: Path = EXCLUS) -> tuple[set[int], set[int]]:
    f_ap = cod / "aproape_duplicate.json"
    aproape = set(json.loads(f_ap.read_text(encoding="utf-8"))) if f_ap.exists() else set()
    scurgere = {int(r.split("\t", 1)[0]) for r in exclus.read_text(encoding="utf-8").splitlines() if r.strip()}
    return aproape, scurgere


def loturi(f_cod: Path, marime: int = BLOC):
    """(indicele primului rând, rândurile) — indicii numără doar rândurile nevide, ca la S53."""
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


_STARE: dict = {}


def _init(stare: dict) -> None:
    global _STARE
    _STARE = stare
    if stare.get("cale_tok"):
        _STARE["tok"] = TokenizerBPE.incarca(stare["cale_tok"])
    if stare.get("cale_w2"):
        _STARE["w2"] = TokenizerBPE.incarca(stare["cale_w2"])


def _gol() -> dict:
    return {"fisiere": 0, "octeti": 0}


def _adauga(d: dict, cheie: str, octeti: int) -> None:
    x = d.setdefault(cheie, _gol())
    x["fisiere"] += 1
    x["octeti"] += octeti


def _numara_lot(lot) -> tuple[dict, Counter]:
    start, randuri = lot
    impartire: dict = {}
    frecvente: Counter = Counter()
    for j, rand in enumerate(randuri):
        r = json.loads(rand)
        p = parte(start + j, r["text"], _STARE["aproape"], _STARE["scurgere"])
        octeti = len(r["text"].encode("utf-8"))
        for cheie in (p, f"{p}/{r.get('limbaj', '?')}", f"{p}/{r.get('sursa', '?')}"):
            _adauga(impartire, cheie, octeti)
        if p == "esantion":
            frecvente.update(frecvente_bucati(r["text"], (), "cod"))
    return impartire, frecvente


def _uneste(a: dict, b: dict) -> None:
    for k, v in b.items():
        x = a.setdefault(k, _gol())
        x["fisiere"] += v["fisiere"]
        x["octeti"] += v["octeti"]


def antreneaza(cod: Path = COD, exclus: Path = EXCLUS, iesire: Path = DIR_TOK, procese: int = 12,
               marime: int = MARIME, jurnal=print) -> dict:
    """Împărțirea + numărătoarea bucăților din eșantion + antrenarea. Refuză dacă tokenizerul există deja."""
    f_tok = iesire / f"bpe_cod_{marime}.json"
    if f_tok.exists():
        raise SystemExit(f"{f_tok} există deja: tokenizerul se antrenează o singură dată")
    aproape, scurgere = citeste_excluse(cod, exclus)
    jurnal(f"aproape-duplicate {len(aproape)}, scurgere S53 {len(scurgere)}")
    t0 = time.time()
    impartire: dict = {}
    frecvente: Counter = Counter()
    fisiere = 0
    with Pool(procese, initializer=_init, initargs=({"aproape": aproape, "scurgere": scurgere},)) as pool:
        for imp, fr in pool.imap(_numara_lot, loturi(cod / "cod.jsonl"), chunksize=1):
            _uneste(impartire, imp)
            frecvente.update(fr)
            fisiere += sum(v["fisiere"] for k, v in imp.items() if "/" not in k)
            if fisiere % 50_000 < BLOC:
                jurnal(f"{fisiere} fișiere, {len(frecvente)} bucăți diferite, {time.time() - t0:.0f} s")
    t_numarare = time.time() - t0
    diferite = len(frecvente)
    frecvente_pastrate = {b: n for b, n in frecvente.items() if n >= FRECVENTA_MINIMA}
    del frecvente
    jurnal(f"numărătoarea gata în {t_numarare:.0f} s: {diferite} bucăți diferite, {len(frecvente_pastrate)} păstrate "
           f"(≥ {FRECVENTA_MINIMA}); antrenez {marime} simboluri")
    t1 = time.time()
    tok = antreneaza_din_frecvente(frecvente_pastrate, marime, SPECIALE, "cod")
    t_antrenare = time.time() - t1
    info = {"sarcina": "S55", "date": str(cod / "cod.jsonl"), "esantion": f"sha256[1] < {PRAG_ESANTION} din antrenare",
            "validare": f"sha256[0] < {PRAG_VALIDARE}", "frecventa_minima": FRECVENTA_MINIMA,
            "bucati_diferite": diferite, "bucati_pastrate": len(frecvente_pastrate)}
    iesire.mkdir(parents=True, exist_ok=True)
    tok.salveaza(f_tok, info)
    sha = sha256_fisier(f_tok)
    (iesire / f"bpe_cod_{marime}.json.sha256").write_text(f"{sha}  {f_tok.name}\n", encoding="utf-8")
    rez = {"impartire": dict(sorted(impartire.items())), "secunde_numarare": round(t_numarare, 1),
           "secunde_antrenare": round(t_antrenare, 1), "marime": tok.marime, "sha256": sha, **info}
    (iesire / "impartire.json").write_text(json.dumps(rez, ensure_ascii=False, indent=1), encoding="utf-8")
    jurnal(f"tokenizerul gata în {t_antrenare:.0f} s: {tok.marime} simboluri, sha {sha}")
    return rez


# --- măsurătorile -------------------------------------------------------------------------------------------------

def _masoara_lot(lot) -> dict:
    start, randuri = lot
    tok, w2 = _STARE["tok"], _STARE["w2"]
    rez = {"fisiere": 0, "identice": 0, "neidentice": [], "pe": {}}
    for j, rand in enumerate(randuri):
        r = json.loads(rand)
        text = r["text"]
        if parte(start + j, text, _STARE["aproape"], _STARE["scurgere"]) != "validare":
            continue
        octeti = text.encode("utf-8")
        simb = tok.codifica_fara_speciale(text)
        rez["fisiere"] += 1
        if b"".join(tok.octeti(s) for s in simb) == octeti:
            rez["identice"] += 1
        else:
            rez["neidentice"].append(start + j)
        n_w2 = len(w2.codifica_fara_speciale(text))
        for cheie in ("tot", r.get("limbaj", "?")):
            x = rez["pe"].setdefault(cheie, {"fisiere": 0, "octeti": 0, "simboluri": 0, "simboluri_w2": 0})
            x["fisiere"] += 1
            x["octeti"] += len(octeti)
            x["simboluri"] += len(simb)
            x["simboluri_w2"] += n_w2
    return rez


def verdict(identice_procent: float, octeti_pe_simbol: float, fata_de_w2: float) -> str:
    if identice_procent < 100.0:
        return "STRICAT"
    if octeti_pe_simbol >= PRAG_OCTETI and fata_de_w2 >= PRAG_FATA_DE_W2:
        return "BUN"
    return "SLAB"


def masoara(cod: Path = COD, exclus: Path = EXCLUS, dir_tok: Path = DIR_TOK, w2: Path = W2, procese: int = 12,
            marime: int = MARIME, jurnal=print) -> dict:
    """(a) octeți/simbol pe validare, pe tot și pe limbaj; (b) același lucru cu tokenizerul w2; (c) codare → decodare
    identică octet cu octet. O singură dată: refuză dacă masurare.json există."""
    f_rez = dir_tok / "masurare.json"
    if f_rez.exists():
        raise SystemExit(f"{f_rez} există deja: măsurarea se face o singură dată")
    aproape, scurgere = citeste_excluse(cod, exclus)
    t0 = time.time()
    tot = {"fisiere": 0, "identice": 0, "neidentice": [], "pe": {}}
    stare = {"aproape": aproape, "scurgere": scurgere, "cale_tok": str(dir_tok / f"bpe_cod_{marime}.json"),
             "cale_w2": str(w2)}
    with Pool(procese, initializer=_init, initargs=(stare,)) as pool:
        for r in pool.imap(_masoara_lot, loturi(cod / "cod.jsonl"), chunksize=1):
            tot["fisiere"] += r["fisiere"]
            tot["identice"] += r["identice"]
            tot["neidentice"] += r["neidentice"]
            for k, v in r["pe"].items():
                x = tot["pe"].setdefault(k, {"fisiere": 0, "octeti": 0, "simboluri": 0, "simboluri_w2": 0})
                for c in x:
                    x[c] += v[c]
    pe = {}
    for k, x in sorted(tot["pe"].items()):
        ops, ops_w2 = x["octeti"] / max(x["simboluri"], 1), x["octeti"] / max(x["simboluri_w2"], 1)
        pe[k] = {**x, "octeti_pe_simbol": round(ops, 4), "octeti_pe_simbol_w2": round(ops_w2, 4),
                 "fata_de_w2": round(ops / ops_w2 - 1, 4)}
    procent = 100.0 * tot["identice"] / max(tot["fisiere"], 1)
    v = verdict(procent, pe["tot"]["octeti_pe_simbol"], pe["tot"]["fata_de_w2"])
    rez = {"secunde": round(time.time() - t0, 1), "fisiere_validare": tot["fisiere"],
           "identice": tot["identice"], "identice_procent": round(procent, 4), "neidentice": tot["neidentice"][:100],
           "pe": pe, "praguri": {"octeti_pe_simbol": PRAG_OCTETI, "fata_de_w2": PRAG_FATA_DE_W2},
           "verdict": v}
    f_rez.write_text(json.dumps(rez, ensure_ascii=False, indent=1), encoding="utf-8")
    jurnal(json.dumps({k: rez[k] for k in ("fisiere_validare", "identice_procent", "verdict")}, ensure_ascii=False))
    jurnal(json.dumps(pe, ensure_ascii=False))
    return rez


# --- tokenizarea setului ------------------------------------------------------------------------------------------

def _tokenizeaza_lot(lot) -> dict:
    start, randuri = lot
    tok, iesire = _STARE["tok"], Path(_STARE["iesire"])
    sfarsit = tok.speciale[SPECIALE[0]]
    k = start // BLOC
    simb = {"antrenare": [], "validare": []}
    rez = {"bloc": k, "pe": {}}
    for j, rand in enumerate(randuri):
        r = json.loads(rand)
        p = parte(start + j, r["text"], _STARE["aproape"], _STARE["scurgere"])
        if p in ("aproape_duplicat", "scurgere"):
            continue
        p = "validare" if p == "validare" else "antrenare"
        s = tok.codifica_fara_speciale(r["text"])
        simb[p].extend(s)
        simb[p].append(sfarsit)
        for cheie in (p, f"{p}/{r.get('limbaj', '?')}", f"{p}/{r.get('sursa', '?')}"):
            x = rez["pe"].setdefault(cheie, {"fisiere": 0, "simboluri": 0})
            x["fisiere"] += 1
            x["simboluri"] += len(s)
    for p, s in simb.items():
        tmp = iesire / f"{p}_{k:05d}.bin.tmp"
        np.asarray(s, dtype=np.uint16).tofile(tmp)
        os.replace(tmp, iesire / f"{p}_{k:05d}.bin")
    tmp = iesire / f"bloc_{k:05d}.json.tmp"
    tmp.write_text(json.dumps(rez, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, iesire / f"bloc_{k:05d}.json")  # ultimul: blocul e întreg doar dacă json-ul există
    return rez


def tokenizeaza(cod: Path = COD, exclus: Path = EXCLUS, dir_tok: Path = DIR_TOK, iesire: Path = DIR_SIMB,
                procese: int = 12, marime: int = MARIME, limita_ore: float | None = None, jurnal=print) -> dict:
    """Tokenizează antrenarea și validarea, pe blocuri de BLOC rânduri; sare peste blocurile deja făcute. Se oprește
    curat la limita de ore sau dacă pe disc rămân sub SPATIU_MINIM_GB."""
    aproape, scurgere = citeste_excluse(cod, exclus)
    iesire.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    oprit = {"motiv": None}

    def de_facut():
        for start, randuri in loturi(cod / "cod.jsonl"):
            if (iesire / f"bloc_{start // BLOC:05d}.json").exists():
                continue
            if limita_ore is not None and time.time() - t0 > limita_ore * 3600:
                oprit["motiv"] = f"limita de {limita_ore} ore"
                return
            if shutil.disk_usage(iesire).free / 1e9 < SPATIU_MINIM_GB:
                oprit["motiv"] = f"sub {SPATIU_MINIM_GB} GB liberi pe disc"
                return
            yield start, randuri

    stare = {"aproape": aproape, "scurgere": scurgere, "cale_tok": str(dir_tok / f"bpe_cod_{marime}.json"),
             "iesire": str(iesire)}
    facute = 0
    with Pool(procese, initializer=_init, initargs=(stare,)) as pool:
        for r in pool.imap_unordered(_tokenizeaza_lot, de_facut(), chunksize=1):
            facute += 1
            if facute % 10 == 0:
                jurnal(f"blocul {r['bloc']} gata; {facute} blocuri în rularea asta, {time.time() - t0:.0f} s")
    total_blocuri = -(-sum(1 for _ in open(cod / "cod.jsonl", "rb") if _.strip()) // BLOC)
    blocuri = sorted(iesire.glob("bloc_*.json"))
    pe: dict = {}
    for f in blocuri:
        for k, v in json.loads(f.read_text(encoding="utf-8"))["pe"].items():
            x = pe.setdefault(k, {"fisiere": 0, "simboluri": 0})
            x["fisiere"] += v["fisiere"]
            x["simboluri"] += v["simboluri"]
    rez = {"tokenizer": f"bpe_cod_{marime}.json", "sha256_tokenizer": sha256_fisier(dir_tok / f"bpe_cod_{marime}.json"),
           "format": "uint16; <|endoftext|> după fiecare fișier; fișiere antrenare_NNNNN.bin / validare_NNNNN.bin",
           "sfarsit_de_fisier": TokenizerBPE.incarca(dir_tok / f"bpe_cod_{marime}.json").speciale[SPECIALE[0]],
           "blocuri_facute": len(blocuri), "blocuri_total": total_blocuri,
           "terminat": len(blocuri) == total_blocuri, "oprit": oprit["motiv"],
           "secunde_rularea_asta": round(time.time() - t0, 1), "pe": dict(sorted(pe.items()))}
    (iesire / "rezumat.json").write_text(json.dumps(rez, ensure_ascii=False, indent=1), encoding="utf-8")
    jurnal(json.dumps({k: rez[k] for k in ("blocuri_facute", "blocuri_total", "terminat", "oprit")},
                      ensure_ascii=False))
    return rez


# --- toți pașii ---------------------------------------------------------------------------------------------------

def verifica_examen(examen: Path = EXAMEN) -> str:
    sha = sha256_fisier(examen / "probleme.jsonl")
    if sha != SHA_EXAMEN:
        raise SystemExit(f"suma setului ascuns nu se potrivește: {sha}")
    return sha


def tot(procese: int = 12, limita_ore: float | None = None, jurnal=print) -> dict:
    t0 = time.time()
    jurnal(f"setul ascuns la început: {verifica_examen()} (neschimbat)")
    if not (DIR_TOK / f"bpe_cod_{MARIME}.json").exists():
        antreneaza(procese=procese, jurnal=jurnal)
    rez = (json.loads((DIR_TOK / "masurare.json").read_text(encoding="utf-8")) if (DIR_TOK / "masurare.json").exists()
           else masoara(procese=procese, jurnal=jurnal))
    jurnal(f"verdictul: {rez['verdict']}")
    if rez["verdict"] in ("BUN", "SLAB"):
        ramase = None if limita_ore is None else max(limita_ore - (time.time() - t0) / 3600, 0.0)
        tokenizeaza(procese=procese, limita_ore=ramase, jurnal=jurnal)
    else:
        jurnal("STRICAT: setul nu se tokenizează")
    jurnal(f"setul ascuns la sfârșit: {verifica_examen()} (neschimbat)")
    return rez


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="comanda", required=True)
    for nume in ("tot", "antreneaza", "masoara", "tokenizeaza"):
        p = sub.add_parser(nume)
        p.add_argument("--procese", type=int, default=12)
        if nume in ("tot", "tokenizeaza"):
            p.add_argument("--limita-ore", type=float, default=None)
    a = ap.parse_args(argv)
    j = lambda m: print(time.strftime("%H:%M:%S"), m, flush=True)  # noqa: E731
    if a.comanda == "tot":
        tot(a.procese, a.limita_ore, j)
    elif a.comanda == "antreneaza":
        antreneaza(procese=a.procese, jurnal=j)
    elif a.comanda == "masoara":
        masoara(procese=a.procese, jurnal=j)
    else:
        tokenizeaza(procese=a.procese, limita_ore=a.limita_ore, jurnal=j)
    return 0


if __name__ == "__main__":
    sys.exit(main())
