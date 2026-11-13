"""S110 (C-120, 13 noiembrie 2026): restul FineWeb-2 românesc, deja descărcat, ca hrană pentru Kronos de 24 de straturi.

Amestecul W2 (`date/ws/amestec/antrenare.txt`) a luat doar ÎNCEPUTUL din `date/ws/curat/fineweb2_ro/antrenare.txt`
(funcția `inceputul` din `unelte/pregateste_amestec_ws.py`). Unealta asta:

1. recalculează tăietura cu ACEEAȘI funcție (importată), verifică lungimea ei cu `date/ws/amestec/info.json` și că
   bucata stă, octet cu octet, în amestec; restul începe imediat după tăietură, la granița unui text;
2. scoate din rest orice text (între două `<|endoftext|>`) care are o bucată de --lungime (50) litere la rând comună cu
   validările examenului de română (întregi), cu setul ascuns, cu examenele „răspuns din text” și cu validarea
   FineWeb-2 (amprentele din `unelte/scurgeri_examen.py`, importate; restul se citește pe blocuri, nu întreg în RAM);
3. scrie `date/ws/hrana_fineweb_rest/antrenare.txt` + `info.json` (dosar NOU; niciun fișier existent nu se schimbă);
4. `verifica`: aceeași căutare pe fișierul scris → trebuie 0 texte cu bucăți comune.

Doar pe procesor. Nimic descărcat, nimic șters.

    python unelte/hrana_fineweb_rest.py ruleaza
    python unelte/hrana_fineweb_rest.py verifica
"""

from __future__ import annotations

import argparse
import hashlib
import json
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

from unelte.pregateste_amestec_ws import SEPARATOR, inceputul  # noqa: E402
from unelte.scurgeri_examen import amprente, coduri, texte_validare  # noqa: E402

SURSA = "date/ws/curat/fineweb2_ro/antrenare.txt"
NUME_IN_AMESTEC = "fineweb2_ro"
AMESTEC = "date/ws/amestec/antrenare.txt"
INFO_AMESTEC = "date/ws/amestec/info.json"
IESIRE = "date/ws/hrana_fineweb_rest"
# cu ce NU are voie să aibă nimic comun (S110 pasul 1b): validările întregi, setul ascuns, examenele „răspuns din text”
DE_FERIT_TEXT = {
    "validare_wikipedia_ro": "date/ws/curat/wikipedia_ro/validare_curata.txt",
    "validare_fineweb2_ro_curata": "date/ws/curat/fineweb2_ro/validare_curata.txt",
    "validare_wikisource_ro": "date/ws/curat/wikisource_ro/validare_curata.txt",
    "validare_fineweb2_ro": "date/ws/curat/fineweb2_ro/validare.txt",
}
DE_FERIT_JSON = {
    "ascuns_romana_raspunsuri": "lucru/romana_raspunsuri/ascuns.jsonl",
    "examen_generalizare_mare": "docs/conversatie/examen_generalizare_mare.json",
    "examen_generalizare_401": "docs/conversatie/examen_generalizare_401.json",
    "examen_tipuri_noi": "docs/conversatie/examen_tipuri_noi.json",
}
LUNGIME = 50
PARTE_MAXIMA_SCOASA = 0.05
CAPAT = (SEPARATOR + "\n").encode()

_TOATE: np.ndarray | None = None
_SURSA_ID: np.ndarray | None = None


def ram_varf_mb() -> float | None:
    try:
        import psutil

        info = psutil.Process().memory_info()
        return round(getattr(info, "peak_wset", info.rss) / 1e6, 1)
    except Exception:  # noqa: BLE001 - doar informativ
        return None


def sha256_fisier(cale: Path, inceput: int = 0, octeti: int | None = None) -> str:
    h = hashlib.sha256()
    with cale.open("rb") as f:
        f.seek(inceput)
        ramas = octeti
        while ramas is None or ramas > 0:
            bucata = f.read(16_000_000 if ramas is None else min(16_000_000, ramas))
            if not bucata:
                break
            h.update(bucata)
            if ramas is not None:
                ramas -= len(bucata)
    return h.hexdigest()


def taietura(sursa: Path, info_amestec: Path, nume: str = NUME_IN_AMESTEC, amestec: Path | None = None) -> dict[str, Any]:
    """Unde se termină partea luată de amestec din `sursa`: aceeași funcție ca la scrierea amestecului. Lungimea trebuie
    să fie exact `octeti` din info.json (minus ce a adăugat `scrie_amestecul` la capăt, dacă a adăugat); altfel refuză.
    Cu `amestec`: verifică și că bucata e, octet cu octet, în fișierul amestecului, la locul ei."""
    info = json.loads(info_amestec.read_text(encoding="utf-8"))["surse"]
    fisa = info[nume]
    inceput = inceputul(sursa, int(fisa["octeti_doriti"]))
    adaugat = b""  # exact ce face scrie_amestecul după inceputul()
    if not inceput.endswith(b"\n"):
        adaugat += b"\n"
    if not (inceput + adaugat).rstrip().endswith(SEPARATOR.encode()):
        adaugat += CAPAT
    if len(inceput) + len(adaugat) != int(fisa["octeti"]):
        raise ValueError(f"tăietura recalculată ({len(inceput)} + {len(adaugat)} adăugați) nu e cea din info.json "
                         f"({fisa['octeti']} octeți): nu pot ști ce a intrat în amestec")
    if len(inceput) < sursa.stat().st_size and not inceput.endswith(CAPAT):
        raise ValueError("tăietura nu cade la granița unui text (<|endoftext|> + rând nou)")
    rezultat = {"octeti_doriti": int(fisa["octeti_doriti"]), "octeti_taietura": len(inceput),
                "octeti_adaugati_de_amestec": len(adaugat), "octeti_in_info_amestec": int(fisa["octeti"]),
                "sha256_taietura": hashlib.sha256(inceput + adaugat).hexdigest()}
    if amestec is not None:
        inainte = 0
        for alta, f in info.items():
            if alta == nume:
                break
            inainte += int(f.get("octeti", 0))
        in_amestec = sha256_fisier(amestec, inainte, len(inceput) + len(adaugat))
        rezultat.update(pozitia_in_amestec=inainte, identica_in_amestec=in_amestec == rezultat["sha256_taietura"])
        if not rezultat["identica_in_amestec"]:
            raise ValueError(f"bucata de la octetul {inainte} din amestec nu e tăietura recalculată: nu pot ști ce a intrat")
    return rezultat


def siruri_din_json(valoare: Any) -> Iterator[str]:
    """Toate șirurile dintr-un JSON (textele, întrebările, răspunsurile), oricât de adânc."""
    if isinstance(valoare, str):
        yield valoare
    elif isinstance(valoare, dict):
        for v in valoare.values():
            yield from siruri_din_json(v)
    elif isinstance(valoare, list):
        for v in valoare:
            yield from siruri_din_json(v)


def texte_de_ferit(text: dict[str, str] | None = None, cu_json: dict[str, str] | None = None) -> dict[str, list[str]]:
    """Textele cu care restul nu are voie să aibă bucăți comune: nume → lista de texte. Un fișier lipsă e o eroare."""
    rezultat: dict[str, list[str]] = {}
    for nume, cale in (DE_FERIT_TEXT if text is None else text).items():
        rezultat[nume] = texte_validare(Path(cale), None)
    for nume, cale in (DE_FERIT_JSON if cu_json is None else cu_json).items():
        brut = Path(cale).read_text(encoding="utf-8")
        if cale.endswith(".jsonl"):
            valori: Any = [json.loads(rand) for rand in brut.splitlines() if rand.strip()]
        else:
            valori = json.loads(brut)
        rezultat[nume] = [s for s in siruri_din_json(valori) if s.strip()]
    return rezultat


def amprente_de_ferit(texte: dict[str, list[str]], lungime: int) -> tuple[np.ndarray, np.ndarray, dict[str, int]]:
    """Amprentele (ordonate, fără repetări) ale tuturor bucăților de `lungime` litere din textele de ferit, cu numărul
    sursei pentru fiecare (prima sursă care o are) și câte bucăți are fiecare sursă."""
    parti, surse, cate = [], [], {}
    for k, (nume, lista) in enumerate(texte.items()):
        h = [amprente(coduri(t), lungime) for t in lista]
        toate = np.concatenate(h) if h else np.zeros(0, dtype=np.uint64)
        cate[nume] = int(len(toate))
        parti.append(toate)
        surse.append(np.full(len(toate), k, dtype=np.uint8))
    toate = np.concatenate(parti) if parti else np.zeros(0, dtype=np.uint64)
    sursa_id = np.concatenate(surse) if surse else np.zeros(0, dtype=np.uint8)
    unice, primul = np.unique(toate, return_index=True)
    return unice, sursa_id[primul], cate


def _porneste(cale_amprente: str, cale_surse: str) -> None:
    global _TOATE, _SURSA_ID
    _TOATE = np.load(cale_amprente, mmap_mode="r")
    _SURSA_ID = np.load(cale_surse, mmap_mode="r")


def cauta_in_bloc(bloc: bytes, lungime: int, toate: np.ndarray, sursa_id: np.ndarray) -> dict[str, Any]:
    """Un bloc de texte întregi (fiecare încheiat cu <|endoftext|> + rând nou; ultimul poate fi neîncheiat, la capătul
    fișierului): care texte au o bucată de `lungime` litere printre amprentele de ferit. Întoarce textele păstrate
    (octeții lor, neschimbați) și, pentru cele scoase, sursele cu care se potrivesc."""
    bucati = bloc.split(CAPAT)
    neincheiat = bucati.pop()  # b"" când blocul se termină la o graniță
    if neincheiat:
        bucati.append(neincheiat)
    text = bloc.decode("utf-8", errors="replace")
    parti = text.split(SEPARATOR + "\n")
    if not parti[-1]:
        parti.pop()
    if len(parti) != len(bucati):
        raise ValueError("împărțirea pe texte diferă între octeți și litere")
    lungimi = np.array([len(p) for p in parti], dtype=np.int64) + len(SEPARATOR) + 1
    inceputuri = np.concatenate([[0], np.cumsum(lungimi)[:-1]]) if len(parti) else np.zeros(0, dtype=np.int64)
    scoase: dict[int, set[int]] = {}
    exemple: list[dict[str, Any]] = []
    if len(toate) and len(text) + 1 >= lungime:
        # Rândul nou de după <|endoftext|> ține de textul care URMEAZĂ (e „între două <|endoftext|>”): o bucată care
        # începe pe el și continuă cu primele litere ale textului e a acelui text, nu a celui de dinainte. De aceea
        # blocul se caută cu un rând nou în față (blocul începe mereu după un <|endoftext|> + rând nou sau la capăt de
        # fișier), iar o bucată de la poziția q (în textul cu rândul nou în față) e a textului cu inceput ≤ q.
        cu_rand = "\n" + text
        h = amprente(coduri(cu_rand), lungime)
        poz = np.searchsorted(toate, h)
        poz[poz >= len(toate)] = 0
        unde = np.nonzero(toate[poz] == h)[0]
        if len(unde):
            care = np.searchsorted(inceputuri, unde, side="right") - 1
            de_unde = np.asarray(sursa_id[poz[unde]])
            for i, s, q in zip(care.tolist(), de_unde.tolist(), unde.tolist()):
                if i not in scoase:
                    scoase[i] = set()
                    if len(exemple) < 3:
                        exemple.append({"sursa": s, "bucata": cu_rand[q: q + lungime], "inceput_text": parti[i][:120]})
                scoase[i].add(s)
    pastrate = b"".join(b + CAPAT for i, b in enumerate(bucati) if i not in scoase)
    return {"texte": len(bucati), "pastrate": pastrate, "scoase": [sorted(s) for s in scoase.values()],
            "exemple": exemple, "ram_mb": ram_varf_mb()}


def _bloc_in_proces(sarcina: tuple[bytes, int]) -> dict[str, Any]:
    assert _TOATE is not None and _SURSA_ID is not None
    return cauta_in_bloc(sarcina[0], sarcina[1], _TOATE, _SURSA_ID)


def blocuri(cale: Path, inceput: int, octeti_pe_bloc: int) -> Iterator[bytes]:
    """Fișierul de la `inceput`, pe blocuri de ~octeti_pe_bloc, tăiate după un text întreg."""
    rest = b""
    with cale.open("rb") as f:
        f.seek(inceput)
        while True:
            nou = f.read(octeti_pe_bloc)
            if not nou:
                break
            date = rest + nou
            capat = date.rfind(CAPAT)
            if capat < 0:
                rest = date
                continue
            yield date[: capat + len(CAPAT)]
            rest = date[capat + len(CAPAT):]
    if rest:
        yield rest


def trece(cale: Path, inceput: int, lungime: int, toate: np.ndarray, sursa_id: np.ndarray, nume_surse: list[str],
          procese: int, octeti_pe_bloc: int, dosar_lucru: Path, scrie: Any = None, spune: Any = print) -> dict[str, Any]:
    """O trecere prin fișier, de la `inceput`: numără textele cu bucăți comune; cu `scrie` (un fișier deschis), scrie
    textele păstrate, în ordine."""
    start = time.monotonic()
    texte = scoase = octeti = scrisi = 0
    motive: Counter[str] = Counter()
    exemple: list[dict[str, Any]] = []
    ram_copii: list[float] = []
    h = hashlib.sha256()

    def aduna(r: dict[str, Any]) -> None:
        nonlocal texte, scoase, scrisi
        texte += r["texte"]
        scoase += len(r["scoase"])
        for s in r["scoase"]:
            motive[" + ".join(nume_surse[k] for k in s)] += 1
        for e in r["exemple"]:
            if len(exemple) < 12:
                exemple.append({**e, "sursa": nume_surse[e["sursa"]]})
        if r["ram_mb"]:
            ram_copii.append(r["ram_mb"])
        if scrie is not None:
            scrie.write(r["pastrate"])
            h.update(r["pastrate"])
        scrisi += len(r["pastrate"])

    if procese <= 1:
        for k, bloc in enumerate(blocuri(cale, inceput, octeti_pe_bloc)):
            octeti += len(bloc)
            aduna(cauta_in_bloc(bloc, lungime, toate, sursa_id))
            spune(f"  blocul {k + 1}: {octeti / 1e9:.2f} GB, {scoase} texte scoase din {texte}, "
                  f"{time.monotonic() - start:.0f} s", flush=True)
    else:
        dosar_lucru.mkdir(parents=True, exist_ok=True)
        fisiere = dosar_lucru / "amprente_de_ferit.npy", dosar_lucru / "surse_de_ferit.npy"
        np.save(fisiere[0], toate)
        np.save(fisiere[1], sursa_id)
        try:
            with ProcessPoolExecutor(procese, initializer=_porneste, initargs=tuple(str(f) for f in fisiere)) as grup:
                in_lucru: deque[Any] = deque()
                facute = 0

                def ia_primul() -> None:
                    nonlocal facute
                    aduna(in_lucru.popleft().result())
                    facute += 1
                    if facute % 10 == 0:
                        spune(f"  {facute} blocuri: {scoase} texte scoase din {texte}, "
                              f"{time.monotonic() - start:.0f} s", flush=True)

                for bloc in blocuri(cale, inceput, octeti_pe_bloc):
                    octeti += len(bloc)
                    in_lucru.append(grup.submit(_bloc_in_proces, (bloc, lungime)))
                    if len(in_lucru) >= 2 * procese:
                        ia_primul()
                while in_lucru:
                    ia_primul()
        finally:
            for f in fisiere:  # fișierele temporare ale uneltei (nu date): nu rămân pe disc
                f.unlink(missing_ok=True)
    return {"octeti_cititi": octeti, "texte": texte, "texte_scoase": scoase, "texte_pastrate": texte - scoase,
            "parte_scoasa": round(scoase / max(1, texte), 6), "octeti_pastrati": scrisi,
            "scoase_pe_motiv": dict(motive.most_common()), "exemple_scoase": exemple,
            "sha256_pastrate": h.hexdigest() if scrie is not None else None,
            "secunde": round(time.monotonic() - start, 1), "ram_varf_proces_copil_mb": max(ram_copii, default=None)}


def ruleaza(sursa: Path, info_amestec: Path, amestec: Path | None, iesire: Path, lungime: int = LUNGIME,
            procese: int = 8, octeti_pe_bloc: int = 32_000_000, dosar_lucru: Path = Path("lucru/hrana_fineweb_rest"),
            de_ferit: dict[str, list[str]] | None = None, spune: Any = print, reface: str = "") -> dict[str, Any]:
    """`reface` = motivul scris pentru care fișierul făcut de unealtă se scrie din nou (ex. o greșeală a uneltei);
    fără el, un fișier existent nu se atinge."""
    tinta = iesire / "antrenare.txt"
    inlocuit = None
    if tinta.exists():
        if not reface:
            raise FileExistsError(f"{tinta} există deja: nu scriu peste el")
        vechi = json.loads((iesire / "info.json").read_text(encoding="utf-8")) if (iesire / "info.json").exists() else {}
        inlocuit = {"motiv": reface, "sha256_vechi": vechi.get("sha256"), "octeti_vechi": vechi.get("octeti"),
                    "texte_scoase_vechi": vechi.get("texte_scoase"), "facut_vechi": vechi.get("facut"),
                    "verificare_veche": vechi.get("verificare")}
    start = time.monotonic()
    t = taietura(sursa, info_amestec, amestec=amestec)
    spune(f"Tăietura: {t['octeti_taietura']:,} octeți (info.json: {t['octeti_in_info_amestec']:,}); restul: "
          f"{sursa.stat().st_size - t['octeti_taietura']:,} octeți.", flush=True)
    texte = texte_de_ferit() if de_ferit is None else de_ferit
    toate, sursa_id, cate = amprente_de_ferit(texte, lungime)
    spune(f"De ferit: {len(toate):,} bucăți diferite de {lungime} litere din {len(texte)} surse, "
          f"{time.monotonic() - start:.0f} s.", flush=True)
    iesire.mkdir(parents=True, exist_ok=True)
    partial = tinta.with_name(tinta.name + ".part")
    with partial.open("wb") as f:
        r = trece(sursa, t["octeti_taietura"], lungime, toate, sursa_id, list(texte), procese, octeti_pe_bloc,
                  dosar_lucru, scrie=f, spune=spune)
    partial.replace(tinta)
    info = {"facut": datetime.now().isoformat(timespec="seconds"), "unealta": "unelte/hrana_fineweb_rest.py (S110, C-120)",
            "sursa": sursa.as_posix(), "octeti_sursa": sursa.stat().st_size, "sha256_sursa": sha256_fisier(sursa),
            "taietura": t, "rest_octeti": sursa.stat().st_size - t["octeti_taietura"], "lungime": lungime,
            "de_ferit": {n: {"texte": len(texte[n]), "bucati": cate[n]} for n in texte},
            "bucati_de_ferit_diferite": int(len(toate)), **r, "octeti": tinta.stat().st_size,
            "sha256": r["sha256_pastrate"], "ram_varf_proces_principal_mb": ram_varf_mb(), "procese": procese,
            "secunde_total": round(time.monotonic() - start, 1)}
    del info["sha256_pastrate"]
    if inlocuit:
        info["refacut"] = inlocuit
    info["se_foloseste"] = info["parte_scoasa"] <= PARTE_MAXIMA_SCOASA
    info["de_ce_nu"] = [] if info["se_foloseste"] else [f"scoase {info['parte_scoasa']:.2%} din texte (> 5 %)"]
    (iesire / "info.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    return info


def verifica(iesire: Path, lungime: int | None = None, procese: int = 8, octeti_pe_bloc: int = 32_000_000,
             dosar_lucru: Path = Path("lucru/hrana_fineweb_rest"), de_ferit: dict[str, list[str]] | None = None,
             spune: Any = print) -> dict[str, Any]:
    """A doua verificare, pe fișierul scris: trebuie 0 texte cu bucăți comune și același SHA-256 ca în info.json."""
    cale_info = iesire / "info.json"
    info = json.loads(cale_info.read_text(encoding="utf-8"))
    lungime = lungime or int(info["lungime"])
    texte = texte_de_ferit() if de_ferit is None else de_ferit
    toate, sursa_id, _ = amprente_de_ferit(texte, lungime)
    tinta = iesire / "antrenare.txt"
    r = trece(tinta, 0, lungime, toate, sursa_id, list(texte), procese, octeti_pe_bloc, dosar_lucru, spune=spune)
    sha = sha256_fisier(tinta)
    v = {"facuta": datetime.now().isoformat(timespec="seconds"), "texte": r["texte"],
         "texte_cu_bucati_comune": r["texte_scoase"], "pe_motiv": r["scoase_pe_motiv"], "sha256": sha,
         "sha256_ca_in_info": sha == info["sha256"], "texte_ca_in_info": r["texte"] == info["texte_pastrate"],
         "secunde": r["secunde"], "ram_varf_proces_principal_mb": ram_varf_mb(),
         "ram_varf_proces_copil_mb": r["ram_varf_proces_copil_mb"]}
    v["curat"] = v["texte_cu_bucati_comune"] == 0 and v["sha256_ca_in_info"] and v["texte_ca_in_info"]
    info["verificare"] = v
    if not v["curat"]:
        info["se_foloseste"] = False
        info.setdefault("de_ce_nu", []).append("a doua verificare nu e curată")
    cale_info.write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    return v


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Restul FineWeb-2 românesc (nefolosit în amestec), fără scurgeri.")
    parser.add_argument("comanda", choices=["ruleaza", "verifica"])
    parser.add_argument("--sursa", default=SURSA)
    parser.add_argument("--info-amestec", default=INFO_AMESTEC)
    parser.add_argument("--amestec", default=AMESTEC)
    parser.add_argument("--iesire", default=IESIRE)
    parser.add_argument("--lungime", type=int, default=LUNGIME)
    parser.add_argument("--procese", type=int, default=8)
    parser.add_argument("--bloc-mb", type=int, default=32)
    parser.add_argument("--reface", default="", help="motivul pentru care fișierul făcut de unealtă se scrie din nou")
    args = parser.parse_args(argv)
    if args.comanda == "ruleaza":
        info = ruleaza(Path(args.sursa), Path(args.info_amestec), Path(args.amestec) if args.amestec else None,
                       Path(args.iesire), args.lungime, args.procese, args.bloc_mb * 1_000_000, reface=args.reface)
        print(f"Scris {args.iesire}/antrenare.txt: {info['octeti']:,} octeți, {info['texte_pastrate']:,} texte păstrate, "
              f"{info['texte_scoase']:,} scoase ({info['parte_scoasa']:.3%}); pe motive: {info['scoase_pe_motiv']}; "
              f"SHA-256 {info['sha256']}; {info['secunde_total']} s; se folosește: {info['se_foloseste']}", flush=True)
        return 0 if info["se_foloseste"] else 2
    v = verifica(Path(args.iesire), None, args.procese, args.bloc_mb * 1_000_000)
    print(f"Verificarea a doua: {v['texte']:,} texte, {v['texte_cu_bucati_comune']} cu bucăți comune; SHA ca în "
          f"info.json: {v['sha256_ca_in_info']}; curat: {v['curat']}; {v['secunde']} s", flush=True)
    return 0 if v["curat"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
