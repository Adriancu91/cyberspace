"""Amestecul de antrenare al liniei noi de pe workstation (W2) și simbolurile lui, o singură dată.

1. Scrie date/ws/amestec/antrenare.txt din textele de ANTRENARE ale surselor (niciodată din validările lor), cu părțile
   din AMESTEC (unelte/antreneaza_tokenizer_ws.py): ~45% engleză simplă (TinyStories întreg), ~35% română, ~15% cod,
   ~5% numere. TinyStories intră tot și dă mărimea totală; din celelalte se ia de la început, până la partea lor,
   tăiat între texte. O sursă mai mică decât partea ei intră toată, fără repetare (se vede în info.json).
2. Scrie hrana liniei: poveștile cu fapte + abecedarul școlii de cod, repetat cât să fie 1 parte la 5 părți de fapte.
   Cu fractie_hrana = 0.06, lotul are în medie 5% fapte și 1% abecedar.
3. Împarte amestecul în simboluri cu tokenizer-ul nou, în paralel, și le ține minte în director_cache, sub amprenta pe
   care o caută modelul (ca unelte/pregateste_tinystories_tot.py): antrenarea le găsește gata.

    python unelte/pregateste_amestec_ws.py --config config/ws_w2.toml
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from array import array
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from kronos.config import citeste_config  # noqa: E402
from module.tokenizer_bpe import TokenizerBPE  # noqa: E402
from unelte.antreneaza_tokenizer_ws import AMESTEC, CURAT, cale_sursa, scrie_numere  # noqa: E402

SEPARATOR = "<|endoftext|>"
_TOK: TokenizerBPE | None = None


def inceputul(cale: Path, octeti: int) -> bytes:
    """Începutul fișierului, cel mult `octeti`, tăiat după ultimul text întreg (sau, fără despărțitoare, după ultimul
    rând întreg)."""
    with cale.open("rb") as f:
        date = f.read(octeti + 1)
    if len(date) <= octeti:
        return date
    capat = date.rfind(SEPARATOR.encode() + b"\n", 0, octeti)
    if capat >= 0:
        return date[: capat + len(SEPARATOR) + 1]
    # un text fără despărțitoare (ex. numerele generate): se taie la ultimul sfârșit de rând
    return date[: date.rfind(b"\n", 0, octeti) + 1]


def scrie_amestecul(director: Path) -> dict[str, Any]:
    director.mkdir(parents=True, exist_ok=True)
    scrie_numere(CURAT / "numere" / "antrenare.txt")
    baza = cale_sursa("date/tinystories_tot/antrenare.txt")
    total = baza.stat().st_size / AMESTEC["engleza_simpla"][0]
    info: dict[str, Any] = {"surse": {}}
    with (director / "antrenare.txt").open("wb") as iesire:
        for categorie, (parte, surse) in AMESTEC.items():
            for sursa, parte_sursa in surse.items():
                cale = cale_sursa(sursa)
                if not cale.exists():
                    info["surse"][sursa] = {"categorie": categorie, "octeti": 0, "lipseste": True}
                    continue
                dorit = int(total * parte * parte_sursa)
                date = cale.read_bytes() if categorie == "engleza_simpla" else inceputul(cale, dorit)
                if not date.endswith(b"\n"):
                    date += b"\n"
                if not date.rstrip().endswith(SEPARATOR.encode()):
                    date += SEPARATOR.encode() + b"\n"
                iesire.write(date)
                info["surse"][sursa] = {"categorie": categorie, "octeti": len(date), "octeti_doriti": dorit,
                                        "toata_sursa": len(date) >= cale.stat().st_size}
    scris = sum(s["octeti"] for s in info["surse"].values())
    for s in info["surse"].values():
        s["parte_reala"] = round(s["octeti"] / scris, 4)
    info["octeti"] = scris
    info["parti_pe_categorii"] = {
        c: round(sum(s["octeti"] for s in info["surse"].values() if s["categorie"] == c) / scris, 4) for c in AMESTEC}
    (director / "info.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    return info


def scrie_hrana(cale: Path, fapte: Path, abecedar: Path) -> dict[str, Any]:
    """Poveștile cu fapte + abecedarul repetat: abecedarul e 1/6 din fișier (5 părți fapte, 1 parte abecedar)."""
    text_fapte, text_abecedar = fapte.read_bytes(), abecedar.read_bytes()
    repetari = max(1, round(len(text_fapte) / 5 / len(text_abecedar)))
    cale.parent.mkdir(parents=True, exist_ok=True)
    capat = b"" if text_fapte.endswith(b"\n") else b"\n"
    bucata = text_abecedar + (b"" if text_abecedar.endswith(b"\n") else b"\n") + SEPARATOR.encode() + b"\n"
    cale.write_bytes(text_fapte + capat + bucata * repetari)
    total = cale.stat().st_size
    return {"fisier": cale.as_posix(), "octeti": total, "repetari_abecedar": repetari,
            "parte_abecedar": round(len(bucata) * repetari / total, 4)}


def _porneste(cale_tokenizer: str) -> None:
    global _TOK
    _TOK = TokenizerBPE.incarca(cale_tokenizer)


def _codifica(text: str) -> bytes:
    assert _TOK is not None
    return array("h", _TOK.codifica(text)).tobytes()


def bucati_intre_texte(text: str, marime: int = 8_000_000) -> list[str]:
    """Textul tăiat în bucăți de ~marime litere, imediat după un separator: simbolurile puse cap la cap sunt exact cele
    ale textului întreg (peste un simbol special nu se lipește nimic)."""
    bucati, start = [], 0
    while start < len(text):
        capat = len(text)
        if start + marime < len(text):
            p = text.find(SEPARATOR, start + marime)
            if p >= 0:
                capat = p + len(SEPARATOR)
        bucati.append(text[start:capat])
        start = capat
    return bucati


def simboluri_in_paralel(text: str, cale_tokenizer: str, procese: int) -> Any:
    import torch

    with ProcessPoolExecutor(procese, initializer=_porneste, initargs=(cale_tokenizer,)) as grup:
        parti = [torch.frombuffer(bytearray(b), dtype=torch.int16) for b in
                 grup.map(_codifica, bucati_intre_texte(text), chunksize=1)]
    return torch.cat(parti) if parti else torch.zeros(0, dtype=torch.int16)


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Amestecul liniei noi de pe workstation și simbolurile lui.")
    parser.add_argument("--config", default="config/ws_w2.toml")
    parser.add_argument("--procese", type=int, default=16)
    parser.add_argument("--reface", action="store_true", help="rescrie amestecul chiar dacă există (ex. după surse noi)")
    parser.add_argument("--fapte", default="date/fapte/povesti.txt")
    parser.add_argument("--abecedar", default="date/cod/abecedar.txt")
    args = parser.parse_args(argv)
    config = citeste_config(args.config)
    date, model = config.setari_port("date"), config.setari_port("model")
    start = time.perf_counter()

    fisier = Path(date["cale_antrenare"])
    if fisier.exists() and not args.reface:
        print(f"Amestecul există deja: {fisier} ({fisier.stat().st_size / 1e9:.2f} GB). Nu-l rescriu.", flush=True)
    else:
        info = scrie_amestecul(fisier.parent)
        print(f"Amestec: {info['octeti'] / 1e9:.2f} GB în {fisier}; părțile: {info['parti_pe_categorii']}", flush=True)
    hrana = scrie_hrana(Path(model["hrana"]), Path(args.fapte), Path(args.abecedar))
    print(f"Hrana: {hrana['fisier']} ({hrana['octeti'] / 1e6:.1f} MB; abecedarul de {hrana['repetari_abecedar']} ori, "
          f"{hrana['parte_abecedar']:.1%} din fișier).", flush=True)

    import torch

    from module.model_continuu import cale_simboluri, salveaza_atomic

    if TokenizerBPE.incarca(model["cale_tokenizer"]).marime >= 2**15:
        print("Tokenizer-ul are peste 32.767 de simboluri: nu încap în int16. Mă opresc.")
        return 1
    for nume, cale in (("amestecul", fisier), ("hrana", Path(model["hrana"]))):
        text = cale.read_text(encoding="utf-8")
        tinta = cale_simboluri(text, model["director_cache"], model["cale_tokenizer"])
        if tinta.exists():
            simboluri = torch.load(tinta, weights_only=True)
            print(f"Simbolurile pentru {nume} erau deja în {tinta}: {len(simboluri):,}.", flush=True)
            continue
        inceput = time.perf_counter()
        simboluri = simboluri_in_paralel(text, model["cale_tokenizer"], args.procese)
        salveaza_atomic(simboluri, tinta)
        print(f"Simboluri pentru {nume}: {len(simboluri):,} ({len(text.encode('utf-8')) / len(simboluri):.2f} octeți pe "
              f"simbol), împărțite în {time.perf_counter() - inceput:.0f} s, în {tinta}.", flush=True)
    print(f"Gata în {(time.perf_counter() - start) / 60:.1f} minute.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
