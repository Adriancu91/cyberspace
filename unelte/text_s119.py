"""S119 (C-127, 17 noiembrie 2026): textul românesc nou (FineWeb-2 `ron_Latn`, fișierele 000_00001 și 000_00002;
OpenAssistant oasst2 doar `lang = ro`) — curățare, dubluri, scurgeri, într-o singură trecere, apoi a doua verificare
și tokenizarea. Doar pe procesor; nimic descărcat, nimic șters, niciun fișier existent schimbat.

Pașii (`tot` îi face pe toți; fiecare pas sare dacă e deja făcut):
1. `curata`: fiecare text trece prin aceleași filtre ca FineWeb-2 la `unelte/curata_date_ws.py` (normalizarea, minim
   300 de litere, „stricate”), apoi:
   - **dubluri identice**: amprenta textului (fără spații și litere mari, ca la curățarea veche) față de TOT textul
     românesc pe care îl avem (`date/ws/curat/{wikipedia_ro,wikisource_ro,fineweb2_ro,fabule_ro}`, antrenare +
     validare) și față de textele noi deja păstrate;
   - **dubluri aproape identice**: din fiecare text se iau bucățile de 50 de litere cu amprenta divizibilă cu 64
     (mereu aceleași, pentru același text); dacă cel puțin jumătate din ele (și cel puțin 4) se găsesc în textul vechi
     sau în textele noi deja păstrate, textul e o copie aproape identică și se scoate;
   - **scurgeri**: orice text cu o bucată de 50 de litere la rând comună cu o validare sau un examen (lista DE_FERIT_*,
     ca la S110 plus `examen_chat.json`, `examen_calcule.json` și celelalte examene) se scoate;
   - 1 % din textele rămase (după amprentă, ca la curățarea veche) merge în `validare.txt`.
   Scrie `date/ws/s119/antrenare.txt`, `validare.txt`, `info.json`. Se oprește la --limita-gb octeți scriși sau dacă
   C: ar coborî sub pragul de disc (cu loc pentru simboluri).
2. `verifica`: a doua căutare de scurgeri pe `antrenare.txt` scris (cu `trece` din `unelte/hrana_fineweb_rest.py`):
   trebuie 0 texte cu bucăți comune și același SHA-256.
3. `tokenizeaza`: `unelte/bucati_din_text.py scrie` cu tokenizer-ul vechi (`date/ws/bpe_16384.json`), în
   `date/ws/bucati_s119/`.

    python unelte/text_s119.py tot [--limita-gb 8] [--procese 8] [--minim-liber-gb 30]
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import shutil
import subprocess
import sys
import time
from collections import Counter, deque
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

import numpy as np

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from unelte.curata_date_ws import SEPARATOR, amprenta, e_stricat, normalizeaza  # noqa: E402  (doar folosite)
from unelte.hrana_fineweb_rest import (amprente_de_ferit, ram_varf_mb, sha256_fisier, texte_de_ferit,  # noqa: E402
                                       trece)
from unelte.scurgeri_examen import amprente, coduri  # noqa: E402

LUNGIME = 50
PAS_ESANTION = 64        # bucățile cu amprenta % 64 == 0 (pentru dublurile aproape identice)
PRAG_APROAPE = 0.5       # partea din bucățile-eșantion găsite în altă parte
MINIM_ESANTIOANE = 4
MINIM_CARACTERE = 300    # ca FineWeb-2 la curata_date_ws.py
MINIM_OASST = 30
SIMBOLURI_PE_OCTET = 0.6  # octeți de simboluri (int16) la un octet de text: amestecul W2 a dat 2,68 GB / 4,89 GB ≈ 0,55

BRUT_FINEWEB = Path("date/ws/brut/fineweb2_ro_s119")
BRUT_OASST = Path("date/ws/brut/oasst2")
IESIRE = Path("date/ws/s119")
BUCATI = Path("date/ws/bucati_s119")
TOKENIZER = Path("date/ws/bpe_16384.json")
LUCRU = Path("lucru/text_s119")
VECHI = [f"date/ws/curat/{s}/{f}.txt" for s in ("wikipedia_ro", "wikisource_ro", "fineweb2_ro", "fabule_ro")
         for f in ("antrenare", "validare")]

# Toate validările (întregi și curate) și toate examenele: nimic din textul nou nu are voie să aibă bucăți comune cu ele.
DE_FERIT_TEXT = {"validare_povesti_r2": "date/tinystories_r2/validare.txt"}
for _s in ("wikipedia_ro", "fineweb2_ro", "wikisource_ro", "fabule_ro", "europarl_en_ro", "tatoeba_en_ro",
           "cod_stack", "cod_instruct"):
    DE_FERIT_TEXT[f"validare_{_s}"] = f"date/ws/curat/{_s}/validare.txt"
    if _s not in ("fabule_ro", "tatoeba_en_ro"):
        DE_FERIT_TEXT[f"validare_{_s}_curata"] = f"date/ws/curat/{_s}/validare_curata.txt"
DE_FERIT_JSON = {
    "ascuns_romana_raspunsuri": "lucru/romana_raspunsuri/ascuns.jsonl",
    "ascuns_romana_reformulat": "lucru/romana_raspunsuri/ascuns_reformulat.jsonl",
    "examen_chat": "docs/conversatie/examen_chat.json",
    "examen_calcule": "docs/conversatie/examen_calcule.json",
    "examen_generalizare_mare": "docs/conversatie/examen_generalizare_mare.json",
    "examen_generalizare_401": "docs/conversatie/examen_generalizare_401.json",
    "examen_tipuri_noi": "docs/conversatie/examen_tipuri_noi.json",
    "examen_scris_de_mana": "docs/conversatie/examen_scris_de_mana.json",
    "chat_deoparte_titluri": "docs/conversatie/chat_deoparte_titluri.json",
    "examen_fapte_sacru": "date/fapte/examen_sacru.json",
    "examen_fapte_nou": "date/fapte/examen_nou.json",
}

_FERIT: np.ndarray | None = None
_FERIT_SURSA: np.ndarray | None = None
_VECHI: np.ndarray | None = None


def esantion(text: str) -> np.ndarray:
    """Amprentele bucăților de 50 de litere ale textului, doar cele divizibile cu PAS_ESANTION (ordonate, unice)."""
    h = amprente(coduri(text), LUNGIME)
    return np.unique(h[h % np.uint64(PAS_ESANTION) == 0])


def _porneste(ferit: str, ferit_sursa: str, vechi: str) -> None:
    global _FERIT, _FERIT_SURSA, _VECHI
    _FERIT = np.load(ferit, mmap_mode="r")
    _FERIT_SURSA = np.load(ferit_sursa, mmap_mode="r")
    _VECHI = np.load(vechi, mmap_mode="r")


def _in(sortat: np.ndarray, h: np.ndarray) -> np.ndarray:
    if not len(sortat) or not len(h):
        return np.zeros(len(h), dtype=bool)
    poz = np.searchsorted(sortat, h)
    poz[poz >= len(sortat)] = 0
    return np.asarray(sortat[poz]) == h


def judeca_texte(texte: list[tuple[str, int]], ferit: np.ndarray, ferit_sursa: np.ndarray,
                 vechi: np.ndarray) -> list[dict[str, Any]]:
    """Pentru fiecare (text brut, minim de litere): textul curățat sau de ce a căzut, amprenta, sursele de scurgere,
    eșantionul și câte din eșantion sunt în textul vechi."""
    rezultat = []
    for brut, minim in texte:
        text, sedile = normalizeaza(brut)
        if len(text) < minim:
            rezultat.append({"cade": "prea_scurte"})
            continue
        if e_stricat(text, "proza"):
            rezultat.append({"cade": "stricate"})
            continue
        h = amprente(coduri("\n" + text), LUNGIME)
        scurs = _in(ferit, h)
        surse = sorted({int(s) for s in np.asarray(ferit_sursa[np.searchsorted(ferit, h[scurs])])}) if scurs.any() else []
        es = np.unique(h[h % np.uint64(PAS_ESANTION) == 0])
        rezultat.append({"text": text, "sedile": sedile, "cheie": amprenta(text), "scurgeri": surse,
                         "bucata_scursa": ("\n" + text)[int(np.argmax(scurs)): int(np.argmax(scurs)) + LUNGIME]
                         if surse else None,
                         "esantion": es, "in_vechi": int(_in(vechi, es).sum())})
    return rezultat


def _judeca_in_proces(texte: list[tuple[str, int]]) -> list[dict[str, Any]]:
    assert _FERIT is not None and _FERIT_SURSA is not None and _VECHI is not None
    return judeca_texte(texte, _FERIT, _FERIT_SURSA, _VECHI)


def texte_oasst(director: Path, numar: dict[str, Any]) -> Iterator[tuple[str, int]]:
    """Mesajele oasst2 cu `lang = ro`, nesterse, scrise de oameni (nu `synthetic`), cu recenzia trecută dacă are una.
    Numără și arborii în care toate mesajele sunt `ro`."""
    pe_arbore: dict[str, list[int]] = {}
    for fisier in sorted(director.glob("*.jsonl.gz")):
        with gzip.open(fisier, "rt", encoding="utf-8") as f:
            for rand in f:
                if not rand.strip():
                    continue
                d = json.loads(rand)
                numar["mesaje_total"] = numar.get("mesaje_total", 0) + 1
                a = pe_arbore.setdefault(str(d.get("message_tree_id")), [0, 0])
                a[0] += 1
                if d.get("lang") != "ro":
                    continue
                a[1] += 1
                numar["mesaje_ro"] = numar.get("mesaje_ro", 0) + 1
                if d.get("deleted") or d.get("synthetic") or d.get("review_result") is False:
                    numar["mesaje_ro_aruncate"] = numar.get("mesaje_ro_aruncate", 0) + 1
                    continue
                if isinstance(d.get("text"), str):
                    yield d["text"], MINIM_OASST
    numar["arbori"] = len(pe_arbore)
    numar["arbori_doar_ro"] = sum(1 for t, r in pe_arbore.values() if t and t == r)
    numar["arbori_cu_ro"] = sum(1 for _, r in pe_arbore.values() if r)


def texte_fineweb(director: Path, numar: dict[str, Any], grupe_pe_lot: int = 1) -> Iterator[list[tuple[str, int]]]:
    import pyarrow.parquet as pq

    for fisier in sorted(director.rglob("*.parquet")):
        if ".cache" in fisier.parts:
            continue
        tabel = pq.ParquetFile(fisier)
        lot: list[tuple[str, int]] = []
        for grupa in range(tabel.metadata.num_row_groups):
            date = tabel.read_row_group(grupa, columns=["text", "minhash_cluster_size"]).to_pydict()
            for text, grup in zip(date["text"], date["minhash_cluster_size"]):
                if isinstance(text, str):
                    numar["minhash_cluster_size"][min(int(grup or 1), 10)] += 1
                    lot.append((text, MINIM_CARACTERE))
            numar["grupe_citite"][fisier.name] = grupa + 1
            if (grupa + 1) % grupe_pe_lot == 0:
                yield lot
                lot = []
        if lot:
            yield lot


def loturi(texte: Iterator[tuple[str, int]], marime: int = 1000) -> Iterator[list[tuple[str, int]]]:
    lot: list[tuple[str, int]] = []
    for t in texte:
        lot.append(t)
        if len(lot) >= marime:
            yield lot
            lot = []
    if lot:
        yield lot


def _vechi_bloc(sarcina: tuple[str, int, int]) -> tuple[list[bytes], np.ndarray]:
    """Un bloc dintr-un fișier vechi (de la octetul a la b, la granițe de text): amprentele textelor și eșantionul."""
    cale, a, b = sarcina
    with open(cale, "rb") as f:
        f.seek(a)
        bloc = f.read(b - a).decode("utf-8", errors="replace")
    chei, es = [], []
    for t in bloc.split(SEPARATOR):
        t = t.strip("\n")
        if t.strip():
            chei.append(amprenta(t))
            es.append(esantion(t))
    return chei, (np.unique(np.concatenate(es)) if es else np.zeros(0, dtype=np.uint64))


def granite(cale: Path, octeti_pe_bloc: int) -> list[tuple[str, int, int]]:
    marime, capat = cale.stat().st_size, SEPARATOR.encode()
    rez, a = [], 0
    with cale.open("rb") as f:
        while a < marime:
            b = min(marime, a + octeti_pe_bloc)
            if b < marime:
                f.seek(b)
                urma = f.read(1_000_000)
                k = urma.find(capat)
                b = marime if k < 0 else b + k + len(capat)
            rez.append((cale.as_posix(), a, b))
            a = b
    return rez


def textul_vechi(fisiere: list[str], procese: int, spune: Any = print) -> tuple[set[bytes], np.ndarray, dict[str, Any]]:
    """Amprentele tuturor textelor vechi și eșantionul lor de bucăți (pentru dubluri)."""
    start = time.monotonic()
    sarcini = [s for f in fisiere for s in granite(Path(f), 64_000_000)]
    chei: set[bytes] = set()
    parti: list[np.ndarray] = []
    with ProcessPoolExecutor(procese) as grup:
        for k, (c, e) in enumerate(grup.map(_vechi_bloc, sarcini)):
            chei.update(c)
            parti.append(e)
            if (k + 1) % 20 == 0:
                spune(f"  textul vechi: {k + 1}/{len(sarcini)} blocuri, {time.monotonic() - start:.0f} s", flush=True)
    es = np.unique(np.concatenate(parti)) if parti else np.zeros(0, dtype=np.uint64)
    return chei, es, {"fisiere": {f: Path(f).stat().st_size for f in fisiere}, "texte": len(chei),
                      "esantioane": int(len(es)), "secunde": round(time.monotonic() - start, 1)}


def liber_gb(cale: Path) -> float:
    return shutil.disk_usage(cale.resolve().anchor).free / 1e9


def curata(iesire: Path = IESIRE, procese: int = 8, limita_gb: float = 8.0, minim_liber_gb: float = 30.0,
           brut_fineweb: Path = BRUT_FINEWEB, brut_oasst: Path = BRUT_OASST, vechi: list[str] | None = None,
           de_ferit: dict[str, list[str]] | None = None, lucru: Path = LUCRU, spune: Any = print) -> dict[str, Any]:
    tinta = iesire / "antrenare.txt"
    if (iesire / "info.json").exists():
        raise FileExistsError(f"{iesire / 'info.json'} există deja: nu scriu peste el")
    start = time.monotonic()
    disc_inainte = liber_gb(Path("."))
    spune(f"C: liber la pornire: {disc_inainte:.1f} GB.", flush=True)
    texte = texte_de_ferit(DE_FERIT_TEXT, DE_FERIT_JSON) if de_ferit is None else de_ferit
    ferit, ferit_sursa, cate = amprente_de_ferit(texte, LUNGIME)
    nume_ferit = list(texte)
    spune(f"De ferit: {len(ferit):,} bucăți diferite din {len(texte)} validări și examene, "
          f"{time.monotonic() - start:.0f} s.", flush=True)
    chei_vechi, es_vechi, info_vechi = textul_vechi(VECHI if vechi is None else vechi, procese, spune)
    spune(f"Textul vechi: {info_vechi['texte']:,} texte, {info_vechi['esantioane']:,} bucăți-eșantion, "
          f"{info_vechi['secunde']:.0f} s.", flush=True)
    lucru.mkdir(parents=True, exist_ok=True)
    fisiere = [lucru / "ferit.npy", lucru / "ferit_sursa.npy", lucru / "vechi.npy"]
    np.save(fisiere[0], ferit)
    np.save(fisiere[1], ferit_sursa)
    np.save(fisiere[2], es_vechi)
    del es_vechi

    surse: dict[str, dict[str, Any]] = {}
    vazute: set[bytes] = set(chei_vechi)
    del chei_vechi
    es_noi: set[int] = set()
    exemple_scurgeri: list[dict[str, Any]] = []
    bucati_scurse: Counter[str] = Counter()
    scrisi = 0
    oprit: str | None = None
    iesire.mkdir(parents=True, exist_ok=True)
    partial = tinta.with_name("antrenare.txt.part")
    h_ant, h_val = hashlib.sha256(), hashlib.sha256()

    def sursa_noua(nume: str) -> dict[str, Any]:
        return surse.setdefault(nume, {"citite": 0, "prea_scurte": 0, "stricate": 0, "dubluri_identice_vechi": 0,
                                       "dubluri_identice_noi": 0, "dubluri_aproape_vechi": 0,
                                       "dubluri_aproape_noi": 0, "scurgeri": 0, "scurgeri_pe_sursa": Counter(),
                                       "sedile_inlocuite": 0, "texte_antrenare": 0, "texte_validare": 0,
                                       "octeti_antrenare": 0, "octeti_validare": 0, "litere_antrenare": 0})

    try:
        with partial.open("w", encoding="utf-8", newline="\n") as ant, \
                (iesire / "validare.txt").open("w", encoding="utf-8", newline="\n") as val, \
                ProcessPoolExecutor(procese, initializer=_porneste, initargs=tuple(str(f) for f in fisiere)) as grup:

            def aplica(nume: str, rezultate: list[dict[str, Any]]) -> None:
                nonlocal scrisi
                n = sursa_noua(nume)
                for r in rezultate:
                    n["citite"] += 1
                    if "cade" in r:
                        n[r["cade"]] += 1
                        continue
                    if r["cheie"] in vazute:
                        n["dubluri_identice_noi" if r["cheie"] not in surse_vechi_marcate else "dubluri_identice_vechi"] += 1
                        continue
                    es = r["esantion"]
                    if len(es) >= MINIM_ESANTIOANE:
                        if r["in_vechi"] >= PRAG_APROAPE * len(es):
                            n["dubluri_aproape_vechi"] += 1
                            continue
                        in_noi = sum(1 for x in es.tolist() if x in es_noi)
                        if r["in_vechi"] + in_noi >= PRAG_APROAPE * len(es):
                            n["dubluri_aproape_noi"] += 1
                            continue
                    if r["scurgeri"]:
                        n["scurgeri"] += 1
                        n["scurgeri_pe_sursa"][" + ".join(nume_ferit[k] for k in r["scurgeri"])] += 1
                        bucati_scurse[r["bucata_scursa"]] += 1
                        if len(exemple_scurgeri) < 12:
                            exemple_scurgeri.append({"sursa": nume, "cu": [nume_ferit[k] for k in r["scurgeri"]],
                                                     "bucata": r["bucata_scursa"], "inceput_text": r["text"][:120]})
                        continue
                    vazute.add(r["cheie"])
                    es_noi.update(es.tolist())
                    n["sedile_inlocuite"] += r["sedile"]
                    care = "validare" if int.from_bytes(r["cheie"][:4], "big") % 100 == 0 else "antrenare"
                    bloc = f"{r['text']}\n{SEPARATOR}\n"
                    octeti = bloc.encode("utf-8")
                    (val if care == "validare" else ant).write(bloc)
                    (h_val if care == "validare" else h_ant).update(octeti)
                    n[f"texte_{care}"] += 1
                    n[f"octeti_{care}"] += len(octeti)
                    if care == "antrenare":
                        n["litere_antrenare"] += len(r["text"])
                    scrisi += len(octeti)

            surse_vechi_marcate = vazute.copy()  # amprentele vechi (dublurile cu ele = „vechi”)
            numar_oasst: dict[str, Any] = {}
            spune("oasst2: încep.", flush=True)
            for lot in loturi(texte_oasst(brut_oasst, numar_oasst)):
                aplica("oasst2_ro", grup.submit(_judeca_in_proces, lot).result())
            sursa_noua("oasst2_ro").update(numar_oasst)
            spune(f"oasst2: {numar_oasst}", flush=True)

            numar_fw: dict[str, Any] = {"minhash_cluster_size": Counter(), "grupe_citite": {}}
            in_lucru: deque[Any] = deque()
            facute = 0

            def ia_primul() -> None:
                nonlocal facute
                aplica("fineweb2_ro_s119", in_lucru.popleft().result())
                facute += 1
                if facute % 50 == 0:
                    n = surse["fineweb2_ro_s119"]
                    spune(f"  FineWeb-2: {facute} grupe, {n['citite']:,} citite, {n['texte_antrenare']:,} păstrate "
                          f"({scrisi / 1e9:.2f} GB), scurgeri {n['scurgeri']:,}, dubluri "
                          f"{n['dubluri_identice_vechi'] + n['dubluri_identice_noi']:,} identice / "
                          f"{n['dubluri_aproape_vechi'] + n['dubluri_aproape_noi']:,} aproape, C: "
                          f"{liber_gb(Path('.')):.1f} GB, {time.monotonic() - start:.0f} s", flush=True)

            for lot in texte_fineweb(brut_fineweb, numar_fw):
                if scrisi >= limita_gb * 1e9:
                    oprit = f"limita de {limita_gb} GB de text scris"
                    break
                if liber_gb(Path(".")) - SIMBOLURI_PE_OCTET * scrisi / 1e9 < minim_liber_gb + 1:
                    oprit = f"paza de disc: C: ar coborî sub {minim_liber_gb} GB cu simbolurile"
                    break
                in_lucru.append(grup.submit(_judeca_in_proces, lot))
                if len(in_lucru) >= 2 * procese:
                    ia_primul()
            while in_lucru:
                ia_primul()
            if "fineweb2_ro_s119" in surse:
                surse["fineweb2_ro_s119"]["minhash_cluster_size"] = dict(sorted(numar_fw["minhash_cluster_size"].items()))
                surse["fineweb2_ro_s119"]["grupe_citite"] = numar_fw["grupe_citite"]
        partial.replace(tinta)
    finally:
        for f in fisiere:  # fișierele temporare ale uneltei (nu date): nu rămân pe disc
            f.unlink(missing_ok=True)
    for n in surse.values():
        n["scurgeri_pe_sursa"] = dict(n["scurgeri_pe_sursa"].most_common())
    total = sum(n["citite"] - n["prea_scurte"] - n["stricate"] for n in surse.values())
    scurgeri = sum(n["scurgeri"] for n in surse.values())
    info = {"facut": datetime.now().isoformat(timespec="seconds"), "unealta": "unelte/text_s119.py (S119, C-127)",
            "lungime": LUNGIME, "pas_esantion": PAS_ESANTION, "prag_aproape": PRAG_APROAPE,
            "minim_esantioane": MINIM_ESANTIOANE, "limita_gb": limita_gb, "minim_liber_gb": minim_liber_gb,
            "oprit": oprit, "c_liber_inainte_gb": round(disc_inainte, 2), "c_liber_dupa_gb": round(liber_gb(Path(".")), 2),
            "de_ferit": {n: {"texte": len(texte[n]), "bucati": cate[n]} for n in texte},
            "bucati_de_ferit_diferite": int(len(ferit)), "textul_vechi": info_vechi, "surse": surse,
            "parte_scoasa_scurgeri": round(scurgeri / max(1, total), 6),
            "bucati_scurse_cele_mai_dese": [{"bucata": b, "texte": c} for b, c in bucati_scurse.most_common(25)],
            "exemple_scurgeri": exemple_scurgeri,
            "octeti_antrenare": tinta.stat().st_size, "sha256_antrenare": h_ant.hexdigest(),
            "octeti_validare": (iesire / "validare.txt").stat().st_size, "sha256_validare": h_val.hexdigest(),
            "ram_varf_proces_principal_mb": ram_varf_mb(), "procese": procese,
            "secunde": round(time.monotonic() - start, 1)}
    (iesire / "info.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    return info


def verifica(iesire: Path = IESIRE, procese: int = 8, de_ferit: dict[str, list[str]] | None = None,
             lucru: Path = LUCRU, spune: Any = print) -> dict[str, Any]:
    """A doua căutare de scurgeri pe fișierul scris: 0 texte cu bucăți comune și același SHA-256."""
    cale_info = iesire / "info.json"
    info = json.loads(cale_info.read_text(encoding="utf-8"))
    texte = texte_de_ferit(DE_FERIT_TEXT, DE_FERIT_JSON) if de_ferit is None else de_ferit
    ferit, ferit_sursa, _ = amprente_de_ferit(texte, LUNGIME)
    tinta = iesire / "antrenare.txt"
    texte_scrise = sum(n["texte_antrenare"] for n in info["surse"].values())
    r = trece(tinta, 0, LUNGIME, ferit, ferit_sursa, list(texte), procese, 32_000_000, lucru, spune=spune)
    sha = sha256_fisier(tinta)
    v = {"facuta": datetime.now().isoformat(timespec="seconds"), "texte": r["texte"],
         "texte_cu_bucati_comune": r["texte_scoase"], "pe_motiv": r["scoase_pe_motiv"], "sha256": sha,
         "sha256_ca_in_info": sha == info["sha256_antrenare"], "texte_ca_in_info": r["texte"] == texte_scrise,
         "secunde": r["secunde"]}
    v["curat"] = v["texte_cu_bucati_comune"] == 0 and v["sha256_ca_in_info"] and v["texte_ca_in_info"]
    info["verificare"] = v
    cale_info.write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    return v


def tokenizeaza(iesire: Path = IESIRE, bucati: Path = BUCATI, minim_liber_gb: float = 30.0) -> int:
    comanda = [sys.executable, "-X", "utf8", str(RADACINA / "unelte" / "bucati_din_text.py"), "scrie",
               "--sursa", str(iesire / "antrenare.txt"), "--tokenizer", str(TOKENIZER), "--iesire", str(bucati),
               "--minim-liber-gb", str(minim_liber_gb)]
    print("Tokenizarea:", " ".join(comanda), flush=True)
    return subprocess.call(comanda)


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    p = argparse.ArgumentParser(description="S119: textul românesc nou — curățare, dubluri, scurgeri, simboluri.")
    p.add_argument("comanda", choices=["curata", "verifica", "tokenizeaza", "tot"])
    p.add_argument("--iesire", type=Path, default=IESIRE)
    p.add_argument("--bucati", type=Path, default=BUCATI)
    p.add_argument("--procese", type=int, default=8)
    p.add_argument("--limita-gb", type=float, default=8.0)
    p.add_argument("--minim-liber-gb", type=float, default=30.0)
    a = p.parse_args(argv)
    if a.comanda in ("curata", "tot") and not (a.iesire / "info.json").exists():
        info = curata(a.iesire, a.procese, a.limita_gb, a.minim_liber_gb)
        print("Curățarea gata:", json.dumps({k: info[k] for k in ("oprit", "octeti_antrenare", "parte_scoasa_scurgeri",
                                                                    "c_liber_dupa_gb", "secunde")}, ensure_ascii=False),
              flush=True)
    if a.comanda in ("verifica", "tot"):
        info = json.loads((a.iesire / "info.json").read_text(encoding="utf-8"))
        if "verificare" not in info or a.comanda == "verifica":
            v = verifica(a.iesire, a.procese)
            print("A doua verificare:", json.dumps(v, ensure_ascii=False), flush=True)
            if not v["curat"]:
                print("A doua verificare NU e curată: nu tokenizez.", flush=True)
                return 1
        elif not info["verificare"]["curat"]:
            print("A doua verificare NU e curată: nu tokenizez.", flush=True)
            return 1
    if a.comanda in ("tokenizeaza", "tot") and not (a.bucati / "index.json").exists():
        return tokenizeaza(a.iesire, a.bucati, a.minim_liber_gb)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
