"""Perechi în română traduse din engleză (15 octombrie 2026, hotărât de Adrian), pe procesor.

Perechile „zi” în engleză scrise de profesor (Qwen) și păstrate (nota ≥ 8, toate filtrele) se traduc cu
Helsinki-NLP/opus-mt-en-ro (licența pe fișa lui: Apache 2.0; revizia fixată mai jos): întrebarea și răspunsul separat,
fără întâmplare (căutare cu 4 raze). Rulează pe procesor (CUDA_VISIBLE_DEVICES=-1), ca pe placă să rămână o singură
sarcină. Traducătorul scrie uneori „ş/ţ” cu sedilă: se trec în „ș/ț” cu virgulă, ca în restul datelor.
Fiecare traducere ține minte originalul (grupul „en:<întrebarea>”), ca o pereche și traducerea ei să nu se despartă
între examen și antrenare. Se poate relua: perechile deja traduse se sar. Filtrul de ortografie se aplică la sfârșit,
odată cu celelalte surse (unelte/genereaza_conversatie.py --finalizeaza).

    CUDA_VISIBLE_DEVICES=-1 python unelte/traduce_conversatie.py --cel-mult 4000
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

MODEL = "Helsinki-NLP/opus-mt-en-ro"
REVIZIE = "96e8fea9e44dae942c2e8a9078dc1615dd871ed9"
SURSA = "date/conversatie/toate.jsonl"
IESIRE = "date/conversatie/traduceri.jsonl"
SEDILE = str.maketrans({"ş": "ș", "ţ": "ț", "Ş": "Ș", "Ţ": "Ț"})


def grupul(intrebare_en: str) -> str:
    from unelte.genereaza_conversatie import normalizat

    return "en:" + normalizat(intrebare_en)


def de_tradus(toate: list[dict], facute: set[str]) -> list[dict]:
    return [p for p in toate if p.get("ramane") and p["limba"] == "en" and p["fel"] == "zi"
            and grupul(p["intrebare"]) not in facute]


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Traduce în română perechile în engleză ale profesorului.")
    parser.add_argument("--cel-mult", type=int, default=4000, help="câte traduceri în total (cu cele de dinainte)")
    parser.add_argument("--lot", type=int, default=16)
    parser.add_argument("--fire", type=int, default=16)
    args = parser.parse_args(argv)

    import torch
    from transformers import MarianMTModel, MarianTokenizer

    torch.set_num_threads(args.fire)
    iesire = RADACINA / IESIRE
    facute = {json.loads(r)["grup"] for r in iesire.read_text(encoding="utf-8").splitlines() if r.strip()} \
        if iesire.exists() else set()
    toate = [json.loads(r) for r in (RADACINA / SURSA).read_text(encoding="utf-8").splitlines() if r.strip()]
    lista = de_tradus(toate, facute)[: max(0, args.cel_mult - len(facute))]
    print(f"De tradus: {len(lista)} perechi (deja traduse: {len(facute)}).", flush=True)
    if not lista:
        return 0
    tok = MarianTokenizer.from_pretrained(MODEL, revision=REVIZIE)
    model = MarianMTModel.from_pretrained(MODEL, revision=REVIZIE).eval()
    start = time.time()

    def traduce(texte: list[str]) -> list[str]:
        with torch.no_grad():
            intrare = tok(texte, return_tensors="pt", padding=True, truncation=True, max_length=256)
            iesiri = model.generate(**intrare, num_beams=4, max_new_tokens=256)
        return [t.translate(SEDILE).strip() for t in tok.batch_decode(iesiri, skip_special_tokens=True)]

    with iesire.open("a", encoding="utf-8") as f:
        for i in range(0, len(lista), args.lot):
            lot = lista[i:i + args.lot]
            intrebari = traduce([p["intrebare"] for p in lot])
            raspunsuri = traduce([p["raspuns"] for p in lot])
            for p, q, r in zip(lot, intrebari, raspunsuri):
                f.write(json.dumps({"fel": "zi", "limba": "ro", "intrebare": q, "raspuns": r,
                                    "profesor": f"{MODEL} (din {p.get('profesor', 'Qwen/Qwen3-4B-Instruct-2507')})",
                                    "sursa": "tradus din engleză", "grup": grupul(p["intrebare"]),
                                    "original": {"intrebare": p["intrebare"], "raspuns": p["raspuns"], "nota": p.get("nota")}},
                                   ensure_ascii=False) + "\n")
            f.flush()
            if (i // args.lot) % 10 == 0:
                print(f"   {i + len(lot)} din {len(lista)}, {time.time() - start:.0f} s", flush=True)
    print(f"Gata: {len(lista)} traduceri în {time.time() - start:.0f} s, în {iesire}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
