"""Examenul pe validare al lui Kronos-Cod (S57): biți pe octet pe cele 5.686 fișiere de validare, pe tot și pe limbaj.

Biții pe octet nu depind de tokenizer, deci se pot compara modele cu tokenizere diferite:

    biți pe octet = pierderea medie pe simbol (nats) / ln 2 / (octeți pe simbol)
                  = suma pierderilor (nats) / ln 2 / suma octeților,

cu octeții și simbolurile măsurate pe ACELEAȘI fișiere (octeții = textul fișierului în UTF-8, simbolurile = cele din
`validare_*.bin`, fără sfârșitul de fișier). Fiecare fișier se notează singur: modelul vede întâi sfârșitul de fișier
(ca în antrenare, unde fișierele vin după el), apoi ghicește fiecare simbol al fișierului. Un fișier mai lung decât
contextul se taie în bucăți de `context` simboluri, una după alta; fiecare bucată pornește din nou (cu simbolul de
dinaintea ei), deci fiecare simbol se notează o singură dată.

Limbajul și octeții fiecărui fișier vin din `lucru/kronos_cod/complet/cod.jsonl`, cu aceeași împărțire ca la
tokenizare (`unelte/kronos_cod/tokenizer_cod.py`, doar citire); numărul fișierelor trebuie să fie același cu cel din
`validare_*.bin`, altfel examenul se oprește. `module/examen_bpb.py` NU se folosește și nu se atinge.

    python -X utf8 -m unelte.kronos_cod.examen_validare index                 # doar octeții / limbajele (fără model)
    python -X utf8 -m unelte.kronos_cod.examen_validare model --config config/cod_c1.toml --stare <model .pt>
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from multiprocessing import Pool
from pathlib import Path
from typing import Callable

import numpy as np

RADACINA = Path(__file__).resolve().parents[2]
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from module.date_cod import DateCod  # noqa: E402
from unelte.kronos_cod import tokenizer_cod as tc  # noqa: E402

LIMBAJE = tc.LIMBAJE


# --- octeții și limbajele fișierelor de validare -----------------------------------------------------------------

_STARE: dict = {}


def _init(stare: dict) -> None:
    global _STARE
    _STARE = stare


def _index_lot(lot) -> list[tuple[str, int]]:
    start, randuri = lot
    rez = []
    for j, rand in enumerate(randuri):
        r = json.loads(rand)
        if tc.parte(start + j, r["text"], _STARE["aproape"], _STARE["scurgere"]) == "validare":
            rez.append((r.get("limbaj", "?"), len(r["text"].encode("utf-8"))))
    return rez


def index_validare(cod: Path = tc.COD, exclus: Path = tc.EXCLUS, procese: int = 12) -> list[tuple[str, int]]:
    """(limbajul, octeții) fiecărui fișier de validare, în ordinea din validare_*.bin (blocurile, apoi rândurile)."""
    aproape, scurgere = tc.citeste_excluse(cod, exclus)
    rez: list[tuple[str, int]] = []
    with Pool(procese, initializer=_init, initargs=({"aproape": aproape, "scurgere": scurgere},)) as pool:
        for parte in pool.imap(_index_lot, tc.loturi(cod / "cod.jsonl"), chunksize=1):
            rez.extend(parte)
    return rez


# --- pierderea și biții pe octet ------------------------------------------------------------------------------------

def bucati_fisier(simboluri: np.ndarray, context: int, sfarsit: int) -> list[tuple[np.ndarray, np.ndarray]]:
    """(intrarea, ținta) pentru fiecare bucată a unui fișier: ținta = toate simbolurile fișierului, o singură dată."""
    s = np.concatenate(([sfarsit], simboluri)).astype(np.int64)
    return [(s[i : i + context], s[i + 1 : i + context + 1]) for i in range(0, len(simboluri), context)]


def pierderi(logits: Callable, fisiere: list[np.ndarray], context: int, sfarsit: int, lot: int = 16) -> list[float]:
    """Suma pierderilor (nats) pe fiecare fișier. `logits(x)` primește un tensor (lot, lungime) și dă
    (lot, lungime, vocabular); bucățile mai scurte se completează la dreapta (umplutura nu se notează). Pierderea se
    socotește unde sunt răspunsurile (pe placă, dacă modelul e pe placă): pe procesor urcă doar sumele."""
    import torch
    import torch.nn.functional as F

    toate = [(k, x, y) for k, f in enumerate(fisiere) for x, y in bucati_fisier(f, context, sfarsit)]
    suma = [0.0] * len(fisiere)
    with torch.no_grad():
        for i in range(0, len(toate), lot):
            grup = toate[i : i + lot]
            t = max(len(x) for _, x, _ in grup)
            x = torch.full((len(grup), t), sfarsit, dtype=torch.long)
            y = torch.full((len(grup), t), -100, dtype=torch.long)
            for r, (_, xi, yi) in enumerate(grup):
                x[r, : len(xi)] = torch.from_numpy(xi)
                y[r, : len(yi)] = torch.from_numpy(yi)
            iesire = logits(x).float()
            y = y.to(iesire.device)
            p = F.cross_entropy(iesire.reshape(-1, iesire.size(-1)), y.reshape(-1), ignore_index=-100, reduction="none")
            p = p.view(len(grup), t).sum(dim=1).cpu()
            for r, (k, _, _) in enumerate(grup):
                suma[k] += float(p[r])
    return suma


def biti_pe_octet(pierderi_nats: list[float], simboluri: list[int], index: list[tuple[str, int]]) -> dict:
    """Pe tot și pe fiecare limbaj: fișiere, octeți, simboluri, octeți pe simbol, pierderea medie, biți pe octet."""
    if not len(pierderi_nats) == len(simboluri) == len(index):
        raise ValueError(f"numere diferite de fișiere: {len(pierderi_nats)} pierderi, {len(simboluri)} în simboluri, "
                         f"{len(index)} în index")
    rez = {}
    for cheie in ("tot", *LIMBAJE):
        ales = [k for k, (limbaj, _) in enumerate(index) if cheie == "tot" or limbaj == cheie]
        if not ales:
            continue
        nats = sum(pierderi_nats[k] for k in ales)
        octeti = sum(index[k][1] for k in ales)
        simb = sum(simboluri[k] for k in ales)
        rez[cheie] = {"fisiere": len(ales), "octeti": octeti, "simboluri": simb,
                      "octeti_pe_simbol": round(octeti / simb, 4), "pierdere_medie": round(nats / simb, 5),
                      "biti_pe_octet": round(nats / math.log(2) / octeti, 5)}
    return rez


def examineaza(logits: Callable, date: DateCod, index: list[tuple[str, int]], lot: int = 16) -> dict:
    fisiere = date.fisiere_validare()
    p = pierderi(logits, fisiere, date.context, date.sfarsit_de_fisier, lot)
    return biti_pe_octet(p, [len(f) for f in fisiere], index)


# --- linia de comandă ------------------------------------------------------------------------------------------------

def _model(config: str, stare: str) -> tuple[Callable, dict]:
    from kronos.config import citeste_config
    from kronos.registru import Registru

    cfg = citeste_config(config)
    model = Registru().creeaza("model", cfg.porturi["model"]["modul"], cfg.setari_port("model")).instanta
    model.incarca(stare)
    model.retea.eval()
    return (lambda x: model.retea(x.to(model.dispozitiv))), cfg.setari_port("date")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="comanda", required=True)
    sub.add_parser("index").add_argument("--procese", type=int, default=12)
    m = sub.add_parser("model")
    m.add_argument("--config", required=True)
    m.add_argument("--stare", required=True)
    m.add_argument("--lot", type=int, default=16)
    m.add_argument("--procese", type=int, default=12)
    m.add_argument("--iesire", default=None, help="fișierul .json cu rezultatul (implicit doar afișat)")
    a = ap.parse_args(argv)
    t0 = time.time()
    index = index_validare(procese=a.procese)
    if a.comanda == "index":
        date = DateCod()
        simb = [len(f) for f in date.fisiere_validare()]
        rez = biti_pe_octet([0.0] * len(simb), simb, index)
        rez = {k: {c: v[c] for c in ("fisiere", "octeti", "simboluri", "octeti_pe_simbol")} for k, v in rez.items()}
    else:
        logits, setari_date = _model(a.config, a.stare)
        date = DateCod(**{k: v for k, v in setari_date.items() if k != "previzualizare"})
        rez = examineaza(logits, date, index, a.lot)
    rez = {"secunde": round(time.time() - t0, 1), "pe": rez}
    text = json.dumps(rez, ensure_ascii=False, indent=1)
    print(text)
    if getattr(a, "iesire", None):
        Path(a.iesire).parent.mkdir(parents=True, exist_ok=True)
        Path(a.iesire).write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
