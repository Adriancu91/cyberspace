"""Bucăți de simboluri făcute DIRECT din text (S102, C-85 pasul 5, partea c): citește fișierul de text pe rând, în
blocuri, fără să țină vreodată tot textul sau tot șirul de simboluri în memorie, și scrie bucățile în exact formatul
lui `unelte/date_bucati.py scrie` (aceleași fișiere bucata_00000.bin, …, același index.json), ca `module/date_bucati.py`
și `date_bucati.py verifica` să le primească neschimbate. NU e legată de nicio configurare și de nicio antrenare.

Regula tăieturii e cea din `TokenizerBPE.codifica_pe_bucati`: un bloc de text se taie imediat după un simbol special
(aici: după ULTIMUL din bloc; restul trece în blocul următor). Peste un simbol special nu se lipește nimic, deci
simbolurile puse cap la cap sunt exact cele de la `codifica(textul întreg)`. Un bloc fără niciun simbol special se
lipește de următorul (și se notează în jurnal.jsonl). Textul se citește ca `Path.read_text(encoding="utf-8")`: UTF-8
strict, iar sfârșiturile de rând „\\r\\n” și „\\r” devin „\\n” (așa a fost citit și textul din care s-a făcut cache-ul).

Comenzi:
  masoara     --sursa <text> --tokenizer <bpe.json> [--octeti 200000000] [--bloc-octeti 50000000] [--iesire <f.json>]
              Codifică doar începutul textului (nu scrie bucăți): octeți/s, litere/s, simboluri/s, RAM de vârf și
              estimarea pentru tot fișierul.
  scrie       --sursa <text> --tokenizer <bpe.json> --iesire lucru/bucati/<nume> [--marime 50000000]
              [--bloc-octeti 50000000] [--minim-liber-gb 15] [--limita-ore H] [--opreste-dupa-blocuri N]
              Rularea întreagă. După fiecare bloc scrie bucățile pline, restul (rest_<n>.bin) și progres.json; la
              repornire continuă de la ultimul bloc terminat. Refuză dacă index.json există. Coduri: 0 = terminat,
              2 = oprit din lipsă de loc pe disc, 3 = oprit la limită (de timp sau de blocuri); după 2 și 3 aceeași
              comandă continuă.
  identitate  --dosar <bucățile noi> --referinta <bucățile vechi> [--iesire <f.json>]
              Proba: SHA-ul șirului întreg, numărul de simboluri și SHA-ul fiecărei bucăți, față de referință. La
              diferență: prima poziție diferită, blocul de text din care vine și dacă e lângă o tăietură. Cod 1 la NU.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Any, BinaryIO, Iterator

import numpy as np

RADACINA = Path(__file__).resolve().parents[1]
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from module.tokenizer_bpe import TokenizerBPE  # noqa: E402  (doar folosit)
from unelte.date_bucati import TIPURI, VERSIUNE, citeste_index, ram_varf_mb  # noqa: E402  (doar folosite)

VERSIUNE_PROGRES = 1
BLOC_OCTETI = 50_000_000
MARIME = 50_000_000


def _sha256_fisier(cale: Path, bloc: int = 64 * 2**20) -> str:
    h = hashlib.sha256()
    with cale.open("rb") as f:
        while b := f.read(bloc):
            h.update(b)
    return h.hexdigest()


def _scrie_atomic(cale: Path, octeti: bytes | memoryview) -> None:
    temporar = cale.with_name(cale.name + ".part")
    with temporar.open("wb") as f:
        f.write(octeti)
    temporar.replace(cale)


def _scrie_json(cale: Path, date: dict[str, Any]) -> None:
    _scrie_atomic(cale, json.dumps(date, indent=1, ensure_ascii=False).encode("utf-8"))


def _octeti(a: np.ndarray) -> memoryview:
    """Octeții tabloului, little-endian (ca în unelte/date_bucati.py)."""
    if a.dtype.byteorder == ">" or (a.dtype.byteorder == "=" and sys.byteorder == "big"):  # pragma: no cover
        a = a.astype(a.dtype.newbyteorder("<"))
    return memoryview(np.ascontiguousarray(a)).cast("B")


def speciale_octeti(tok: TokenizerBPE) -> list[bytes]:
    """Simbolurile speciale ca octeți. Refuză tokenizerele la care tăietura pe octeți n-ar fi sigură: fără simboluri
    speciale (n-ar exista niciun loc de tăiat) sau cu simboluri speciale care se pot suprapune între ele."""
    speciale = [s.encode("utf-8") for s in tok.speciale]
    if not speciale:
        raise ValueError("tokenizerul nu are niciun simbol special: nu am unde tăia textul în blocuri")
    for a in speciale:
        for b in speciale:
            if a is not b and a in b:
                raise ValueError(f"simbolul special {a!r} e cuprins în {b!r}: tăietura n-ar fi sigură")
            if any(a[-k:] == b[:k] for k in range(1, min(len(a), len(b)))):
                raise ValueError(f"simbolurile speciale {a!r} și {b!r} se pot suprapune: tăietura n-ar fi sigură")
    return speciale


def taietura(octeti: bytes, speciale: list[bytes]) -> int:
    """Locul imediat de după ultimul simbol special din bloc (0 = blocul n-are niciunul)."""
    return max((p + len(s) for s in speciale if (p := octeti.rfind(s)) >= 0), default=0)


def ca_la_read_text(octeti: bytes) -> str:
    """Textul, ca la Path.read_text(encoding="utf-8"): UTF-8 strict, „\\r\\n” și „\\r” devin „\\n”."""
    text = octeti.decode("utf-8")
    if "\r" in text:
        text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text


def blocuri(f: BinaryIO, speciale: list[bytes], bloc_octeti: int) -> Iterator[tuple[bytes, int]]:
    """Bucățile de text (ca octeți), una după alta, de la poziția de acum a fișierului: fiecare se termină imediat după
    un simbol special (ultima: la sfârșitul fișierului). Dă (octeții, câte citiri fără simbol special s-au lipit)."""
    amanat = b""
    lipite = 0
    while True:
        citit = f.read(bloc_octeti)
        sfarsit = len(citit) < bloc_octeti
        date = amanat + citit if amanat else citit
        if sfarsit:
            if date:
                yield date, lipite
            return
        taie = taietura(date, speciale)
        if taie == 0:
            amanat = date
            lipite += 1
            continue
        amanat = date[taie:]
        yield date[:taie], lipite
        lipite = 0


def _tip(tok: TokenizerBPE) -> str:
    return "int16" if tok.marime < 2**15 else "int32"


def masoara(sursa: Path, tokenizer: Path, octeti: int, bloc_octeti: int) -> dict[str, Any]:
    tok = TokenizerBPE.incarca(tokenizer)
    speciale = speciale_octeti(tok)
    tip = TIPURI[_tip(tok)]
    total = sursa.stat().st_size
    facuti = litere = simboluri = nr = 0
    inceput = time.perf_counter()
    with sursa.open("rb") as f:
        for bucata, _ in blocuri(f, speciale, bloc_octeti):
            text = ca_la_read_text(bucata)
            a = np.array(tok.codifica(text), dtype=tip)
            facuti += len(bucata)
            litere += len(text)
            simboluri += len(a)
            nr += 1
            del text, a
            if facuti >= octeti:
                break
    secunde = time.perf_counter() - inceput
    return {
        "sursa": str(sursa).replace("\\", "/"), "octeti_sursa": total, "octeti_masurati": facuti, "blocuri": nr,
        "bloc_octeti": bloc_octeti, "litere": litere, "simboluri": simboluri, "secunde": round(secunde, 2),
        "octeti_pe_secunda": round(facuti / secunde), "litere_pe_secunda": round(litere / secunde),
        "simboluri_pe_secunda": round(simboluri / secunde),
        "octeti_pe_simbol": round(facuti / max(simboluri, 1), 4),
        "estimare_tot_secunde": round(total / (facuti / secunde)) if facuti else None,
        "estimare_tot_ore": round(total / (facuti / secunde) / 3600, 2) if facuti else None,
        "estimare_simboluri": round(simboluri * total / facuti) if facuti else None,
        "ram_varf_mb": ram_varf_mb(),
    }


def _progres_nou(sursa: Path, tokenizer: Path, tip: str, marime: int) -> dict[str, Any]:
    return {
        "versiune": VERSIUNE_PROGRES,
        "sursa": {"fisier": str(sursa).replace("\\", "/"), "octeti": sursa.stat().st_size},
        "tokenizer": {"fisier": str(tokenizer).replace("\\", "/"), "sha256": _sha256_fisier(tokenizer)},
        "tip": tip, "marime_bucata": marime,
        "octeti_facuti": 0, "litere": 0, "simboluri": 0, "blocuri": 0, "blocuri_fara_special": 0,
        "bucati": [], "rest": None, "secunde": 0.0, "porniri": 0, "ram_varf_mb": 0, "terminat": False,
    }


def _reia(iesire: Path, nou: dict[str, Any]) -> tuple[dict[str, Any], np.ndarray]:
    """Progresul salvat (verificat că e al aceleiași surse, al aceluiași tokenizer și al aceleiași mărimi) și restul
    de simboluri care nu umpluseră încă o bucată."""
    progres = json.loads((iesire / "progres.json").read_text(encoding="utf-8"))
    for cheie in ("versiune", "sursa", "tip", "marime_bucata"):
        if progres[cheie] != nou[cheie]:
            raise ValueError(f"progres.json e al altei rulări („{cheie}”: {progres[cheie]} față de {nou[cheie]})")
    if progres["tokenizer"]["sha256"] != nou["tokenizer"]["sha256"]:
        raise ValueError("progres.json e făcut cu alt tokenizer")
    tip = np.dtype(TIPURI[progres["tip"]]).newbyteorder("<")
    for b in progres["bucati"]:
        cale = iesire / b["fisier"]
        if not cale.exists() or cale.stat().st_size != b["simboluri"] * tip.itemsize:
            raise ValueError(f"{b['fisier']}: lipsește sau are altă mărime decât în progres.json")
    rest = np.zeros(0, dtype=tip)
    if progres["rest"]:
        octeti = (iesire / progres["rest"]["fisier"]).read_bytes()
        if hashlib.sha256(octeti).hexdigest() != progres["rest"]["sha256"]:
            raise ValueError(f"{progres['rest']['fisier']}: SHA diferit de cel din progres.json")
        rest = np.frombuffer(octeti, dtype=tip)
    return progres, rest


def _scrie_bucata(iesire: Path, progres: dict[str, Any], felie: np.ndarray) -> None:
    i = len(progres["bucati"])
    nume = f"bucata_{i:05d}.bin"
    octeti = _octeti(felie)
    _scrie_atomic(iesire / nume, octeti)
    progres["bucati"].append({"fisier": nume, "inceput": i * progres["marime_bucata"], "simboluri": len(felie),
                              "sha256": hashlib.sha256(octeti).hexdigest()})


def _sterge_resturi(iesire: Path, pastreaza: str | None) -> None:
    """Șterge fișierele de lucru rest_*.bin ale uneltei (nu bucățile), mai puțin pe cel din progres.json."""
    for cale in iesire.glob("rest_*.bin"):
        if cale.name != pastreaza:
            cale.unlink()


def scrie(sursa: Path, tokenizer: Path, iesire: Path, marime: int = MARIME, bloc_octeti: int = BLOC_OCTETI,
          minim_liber_gb: float = 15.0, limita_ore: float | None = None,
          opreste_dupa_blocuri: int | None = None) -> dict[str, Any]:
    index_cale = iesire / "index.json"
    if index_cale.exists():
        raise FileExistsError(f"{index_cale} există deja: nu scriu peste bucăți făcute")
    if marime <= 0 or bloc_octeti <= 0:
        raise ValueError("--marime și --bloc-octeti trebuie să fie pozitive")
    inceput = time.perf_counter()
    tok = TokenizerBPE.incarca(tokenizer)
    speciale = speciale_octeti(tok)
    progres = _progres_nou(sursa, tokenizer, _tip(tok), marime)
    tip = np.dtype(TIPURI[progres["tip"]]).newbyteorder("<")
    iesire.mkdir(parents=True, exist_ok=True)
    rest = np.zeros(0, dtype=tip)
    if (iesire / "progres.json").exists():
        progres, rest = _reia(iesire, progres)
    secunde_dinainte = progres["secunde"]
    progres["porniri"] += 1
    jurnal = (iesire / "jurnal.jsonl").open("a", encoding="utf-8")
    oprit: str | None = None
    blocuri_acum = 0

    def salveaza() -> None:
        progres["secunde"] = round(secunde_dinainte + time.perf_counter() - inceput, 2)
        progres["ram_varf_mb"] = max(progres["ram_varf_mb"], ram_varf_mb() or 0)
        _scrie_json(iesire / "progres.json", progres)

    with sursa.open("rb") as f:
        f.seek(progres["octeti_facuti"])
        for bucata, lipite in blocuri(f, speciale, bloc_octeti):
            t0 = time.perf_counter()
            text = ca_la_read_text(bucata)
            litere = len(text)
            nou = np.array(tok.codifica(text), dtype=tip)
            del text
            tot = np.concatenate([rest, nou]) if len(rest) else nou
            pline = len(tot) // marime
            liber = shutil.disk_usage(iesire).free
            if liber - len(tot) * tip.itemsize < minim_liber_gb * 2**30:
                oprit = f"discul ar coborî sub {minim_liber_gb} GB liberi (acum {liber / 2**30:.1f} GB)"
                break
            for k in range(pline):
                _scrie_bucata(iesire, progres, tot[k * marime:(k + 1) * marime])
            rest = tot[pline * marime:].copy()
            de_la = progres["octeti_facuti"]
            progres["octeti_facuti"] += len(bucata)
            progres["litere"] += litere
            progres["simboluri"] += len(nou)
            progres["blocuri"] += 1
            progres["blocuri_fara_special"] += lipite
            if len(rest):
                nume_rest = f"rest_{progres['blocuri']:06d}.bin"
                octeti_rest = _octeti(rest)
                _scrie_atomic(iesire / nume_rest, octeti_rest)
                progres["rest"] = {"fisier": nume_rest, "simboluri": len(rest),
                                   "sha256": hashlib.sha256(octeti_rest).hexdigest()}
            else:
                progres["rest"] = None
            salveaza()
            _sterge_resturi(iesire, progres["rest"]["fisier"] if progres["rest"] else None)
            rand = {"bloc": progres["blocuri"], "octeti_de_la": de_la, "octeti_pana_la": progres["octeti_facuti"],
                    "litere": litere, "simboluri": len(nou), "simboluri_pana_la": progres["simboluri"],
                    "citiri_fara_special_lipite": lipite, "secunde": round(time.perf_counter() - t0, 2),
                    "ram_varf_mb": ram_varf_mb()}
            jurnal.write(json.dumps(rand, ensure_ascii=False) + "\n")
            jurnal.flush()
            print(json.dumps(rand, ensure_ascii=False), flush=True)
            del nou, tot
            blocuri_acum += 1
            if opreste_dupa_blocuri is not None and blocuri_acum >= opreste_dupa_blocuri:
                oprit = f"limita de {opreste_dupa_blocuri} blocuri"
                break
            if limita_ore is not None and time.perf_counter() - inceput >= limita_ore * 3600:
                oprit = f"limita de {limita_ore} ore"
                break
        else:
            oprit = None
    jurnal.close()
    if oprit is None and progres["octeti_facuti"] != progres["sursa"]["octeti"]:
        raise RuntimeError(f"am ajuns la {progres['octeti_facuti']} octeți, sursa are {progres['sursa']['octeti']}")
    if oprit is not None and progres["octeti_facuti"] != progres["sursa"]["octeti"]:
        salveaza()
        return {"terminat": False, "oprit": oprit, "pe_disc": "disc" in oprit,
                **{k: progres[k] for k in ("octeti_facuti", "litere", "simboluri", "blocuri", "secunde",
                                           "ram_varf_mb", "porniri")},
                "bucati_pline": len(progres["bucati"])}

    # Sfârșitul textului: restul devine ultima bucată (mai scurtă), apoi SHA-ul șirului întreg, recitind bucățile.
    if len(rest):
        _scrie_bucata(iesire, progres, rest)
        progres["rest"] = None
    tot_sha = hashlib.sha256()
    for b in progres["bucati"]:
        h = hashlib.sha256()
        with (iesire / b["fisier"]).open("rb") as g:
            while octeti := g.read(64 * 2**20):
                h.update(octeti)
                tot_sha.update(octeti)
        if h.hexdigest() != b["sha256"]:
            raise RuntimeError(f"{b['fisier']}: pe disc e altceva decât am scris (SHA diferit)")
    progres["terminat"] = True
    salveaza()
    index = {
        "versiune": VERSIUNE,
        "tip": progres["tip"],
        "ordine_octeti": "little",
        "marime_bucata": marime,
        "simboluri_total": progres["simboluri"],
        "simboluri_sursa": progres["simboluri"],
        "partial": False,
        "sha256_tot": tot_sha.hexdigest(),
        "sursa": progres["sursa"] | {"fel": "text", "litere": progres["litere"]},
        "tokenizer": progres["tokenizer"],
        "bucati": progres["bucati"],
        "scris_la": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "secunde": progres["secunde"],
        "ram_varf_mb": progres["ram_varf_mb"],
        "facut_de": {"unealta": "unelte/bucati_din_text.py", "bloc_octeti": bloc_octeti, "blocuri": progres["blocuri"],
                     "citiri_fara_special_lipite": progres["blocuri_fara_special"], "porniri": progres["porniri"]},
    }
    _scrie_json(index_cale, index)
    _sterge_resturi(iesire, None)
    return {"terminat": True} | {k: v for k, v in index.items() if k != "bucati"} | {
        "numar_bucati": len(index["bucati"])}


def _prima_diferenta(nou: Path, vechi: Path, tip: np.dtype) -> int | None:
    a = np.memmap(nou, dtype=tip, mode="r")
    b = np.memmap(vechi, dtype=tip, mode="r")
    n = min(len(a), len(b))
    pas = 4_000_000
    for i in range(0, n, pas):
        diferite = np.nonzero(a[i:i + pas] != b[i:i + pas])[0]
        if len(diferite):
            return i + int(diferite[0])
    return n if len(a) != len(b) else None


def identitate(dosar: Path, referinta: Path) -> dict[str, Any]:
    nou, vechi = citeste_index(dosar), citeste_index(referinta)
    rez: dict[str, Any] = {
        "dosar": str(dosar).replace("\\", "/"), "referinta": str(referinta).replace("\\", "/"),
        "sha256_tot": nou["sha256_tot"], "sha256_tot_referinta": vechi["sha256_tot"],
        "simboluri": nou["simboluri_total"], "simboluri_referinta": vechi["simboluri_total"],
        "bucati": len(nou["bucati"]), "bucati_referinta": len(vechi["bucati"]),
        "tip": nou["tip"], "tip_referinta": vechi["tip"],
        "tokenizer_acelasi": (nou.get("tokenizer") or {}).get("sha256") == (vechi.get("tokenizer") or {}).get("sha256"),
    }
    diferite = [i for i, (a, b) in enumerate(zip(nou["bucati"], vechi["bucati"]))
                if a["sha256"] != b["sha256"] or a["simboluri"] != b["simboluri"]]
    rez["bucati_diferite"] = diferite[:50]
    rez["numar_bucati_diferite"] = len(diferite) + abs(len(nou["bucati"]) - len(vechi["bucati"]))
    rez["identic"] = (not diferite and not nou.get("partial") and not vechi.get("partial")
                      and rez["sha256_tot"] == rez["sha256_tot_referinta"]
                      and rez["simboluri"] == rez["simboluri_referinta"] and rez["bucati"] == rez["bucati_referinta"]
                      and rez["tip"] == rez["tip_referinta"])
    rez["verdict"] = "DA" if rez["identic"] else "NU"
    if diferite and rez["tip"] == rez["tip_referinta"] and nou["marime_bucata"] == vechi["marime_bucata"]:
        i = diferite[0]
        tip = np.dtype(TIPURI[nou["tip"]]).newbyteorder("<")
        loc = _prima_diferenta(dosar / nou["bucati"][i]["fisier"], referinta / vechi["bucati"][i]["fisier"], tip)
        if loc is not None:
            pozitie = nou["bucati"][i]["inceput"] + loc
            prima: dict[str, Any] = {"pozitie_simbol": pozitie, "bucata": i}
            jurnal = dosar / "jurnal.jsonl"
            if jurnal.exists():
                inainte = 0
                for rand in map(json.loads, jurnal.read_text(encoding="utf-8").splitlines()):
                    if pozitie < rand["simboluri_pana_la"]:
                        prima |= {"bloc_text": rand["bloc"], "octeti_de_la": rand["octeti_de_la"],
                                  "octeti_pana_la": rand["octeti_pana_la"],
                                  "simboluri_de_la_taietura_dinainte": pozitie - inainte,
                                  "simboluri_pana_la_taietura_urmatoare": rand["simboluri_pana_la"] - pozitie,
                                  "langa_taietura": min(pozitie - inainte, rand["simboluri_pana_la"] - pozitie) < 64}
                        break
                    inainte = rand["simboluri_pana_la"]
            rez["prima_diferenta"] = prima
    return rez


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="comanda", required=True)
    s = sub.add_parser("masoara")
    s.add_argument("--sursa", required=True, type=Path)
    s.add_argument("--tokenizer", required=True, type=Path)
    s.add_argument("--octeti", type=int, default=200_000_000)
    s.add_argument("--bloc-octeti", type=int, default=BLOC_OCTETI)
    s.add_argument("--iesire", type=Path, default=None)
    s = sub.add_parser("scrie")
    s.add_argument("--sursa", required=True, type=Path)
    s.add_argument("--tokenizer", required=True, type=Path)
    s.add_argument("--iesire", required=True, type=Path)
    s.add_argument("--marime", type=int, default=MARIME)
    s.add_argument("--bloc-octeti", type=int, default=BLOC_OCTETI)
    s.add_argument("--minim-liber-gb", type=float, default=15.0)
    s.add_argument("--limita-ore", type=float, default=None)
    s.add_argument("--opreste-dupa-blocuri", type=int, default=None)
    s = sub.add_parser("identitate")
    s.add_argument("--dosar", required=True, type=Path)
    s.add_argument("--referinta", required=True, type=Path)
    s.add_argument("--iesire", type=Path, default=None)
    a = p.parse_args(argv)

    cod = 0
    if a.comanda in ("masoara", "identitate") and a.iesire is not None and a.iesire.exists():
        raise FileExistsError(f"{a.iesire} există deja")
    if a.comanda == "masoara":
        rez = masoara(a.sursa, a.tokenizer, a.octeti, a.bloc_octeti)
    elif a.comanda == "scrie":
        rez = scrie(a.sursa, a.tokenizer, a.iesire, a.marime, a.bloc_octeti, a.minim_liber_gb, a.limita_ore,
                    a.opreste_dupa_blocuri)
        cod = 0 if rez["terminat"] else (2 if rez["pe_disc"] else 3)
    else:
        rez = identitate(a.dosar, a.referinta)
        cod = 0 if rez["identic"] else 1
    if a.comanda != "scrie" and a.iesire is not None:
        a.iesire.parent.mkdir(parents=True, exist_ok=True)
        a.iesire.write_text(json.dumps(rez, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(rez, ensure_ascii=False))
    return cod


if __name__ == "__main__":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    sys.exit(main())
