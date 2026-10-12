"""Școala de cod v0.4: poate un model să copieze cuvântul pe care îl vede? O încercare mică, pe procesor.

Problema veche (v0.3): la nivelul cuvintelor (0w), sarcina e „show the word moon”, iar răspunsul e `"moon"`. În sarcină
cuvântul are spațiu în față, în răspuns nu: pentru model sunt bucăți diferite, deci nu are ce copia.

Încercarea: un model GPT minuscul (aceeași rețea ca Kronos, din module/model_gpt.py, 2 straturi × 96), pornit de la
zero, învață episoade de felul celor din abecedar pe multe cuvinte (implicit 3.000, luate din poveștile de validare,
ca să nu le poată ține minte pe toate) și e testat pe cuvintele nivelului 0w, pe care nu le-a văzut niciodată. Dacă le
nimerește, a învățat să COPIEZE; dacă nu, doar a memorat perechi. Cu `--cuvinte-antrenare 0` învață doar 80 de cuvinte
ale nivelului 0w: atunci memorează și nu copiază în nicio variantă (încercat pe 12 octombrie).
Trei variante, cu aceiași pași și aceeași sămânță:
- tokenizer-ul vechi, sarcina de acum;
- tokenizer-ul nou, sarcina de acum;
- tokenizer-ul nou, sarcina cu cuvântul între ghilimele (`show the word "moon"`).
A treia cere schimbarea generatorului de teste (fișier cu amprentă): aici doar se măsoară, pentru decizia lui Adrian.

Nu e Kronos și nu e școala: e un model de jucărie, doar ca să se vadă mecanismul. Doar pe procesor.

    python unelte/proba_copiere_cod.py --pasi 1500
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from module.cod.examen_cod import CUVINTE_0W, CUVINTE_LUNGI_0W  # noqa: E402
from module.tokenizer_bpe import TokenizerBPE  # noqa: E402

SARCINI = {"de_acum": "show the word {w}", "cu_ghilimele": 'show the word "{w}"'}


def episod(cuvant: str, sarcina: str) -> str:
    return f'TEST: {sarcina.format(w=cuvant)}\nWRITE:\n"{cuvant}"\nRESULT:\n{cuvant}\npassed\n\n'


def incearca(tok: TokenizerBPE, sarcina: str, de_invatat: list[str], de_testat: dict[str, list[str]], pasi: int,
             samanta: int = 0, context: int = 96, lot: int = 32) -> dict[str, Any]:
    """Antrenează modelul mic pe episoadele cuvintelor `de_invatat` și îl testează pe fiecare listă din `de_testat`:
    câte răspunsuri sunt exact `"cuvânt"` (fără întâmplare: mereu bucata cea mai probabilă)."""
    import torch
    import torch.nn.functional as F

    from module.model_gpt import _GPT

    torch.manual_seed(samanta)
    rng = random.Random(samanta)
    retea = _GPT(tok.marime, 2, 4, 96, context, 0.0)
    optimizator = torch.optim.AdamW(retea.parameters(), lr=1e-3, weight_decay=0.1)
    # Ca la școală (ElevCod.antreneaza): un singur text lung, tăiat în bucăți o singură dată, din care se iau ferestre
    # la întâmplare. Așa, bucățile de la granița dintre episoade sunt aceleași la antrenare și la test.
    text = "".join(episod(rng.choice(de_invatat), sarcina) for _ in range(4000))
    simboluri = torch.tensor(tok.codifica(text), dtype=torch.long)
    generator = torch.Generator().manual_seed(samanta)
    start = time.perf_counter()
    retea.train()
    pierdere = float("nan")
    for _ in range(pasi):
        pozitii = torch.randint(len(simboluri) - context - 1, (lot,), generator=generator)
        date = torch.stack([simboluri[p: p + context + 1] for p in pozitii])
        logits = retea(date[:, :-1])
        loss = F.cross_entropy(logits.reshape(-1, logits.size(-1)), date[:, 1:].reshape(-1))
        optimizator.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(retea.parameters(), 1.0)
        optimizator.step()
        pierdere = loss.item()
    retea.eval()

    def raspuns(cuvant: str) -> str:
        exemple = rng.sample(de_invatat, 2)
        fata = "".join(episod(e, sarcina) for e in exemple) + f"TEST: {sarcina.format(w=cuvant)}\nWRITE:\n"
        x = torch.tensor([tok.codifica(fata)], dtype=torch.long)
        noi: list[int] = []
        with torch.no_grad():
            for _ in range(12):
                urm = int(retea(x[:, -context:])[0, -1].argmax())
                noi.append(urm)
                x = torch.cat([x, torch.tensor([[urm]])], dim=1)
                if "\n" in tok.decodeaza(noi):
                    break
        return tok.decodeaza(noi).split("\n")[0]

    rezultat: dict[str, Any] = {"pasi": pasi, "pierdere_finala": round(pierdere, 4),
                                "secunde": round(time.perf_counter() - start, 1)}
    for nume, cuvinte in de_testat.items():
        raspunsuri = {w: raspuns(w) for w in cuvinte}
        corecte = [w for w, r in raspunsuri.items() if r == f'"{w}"']
        rezultat[nume] = {"corecte": len(corecte), "din": len(cuvinte),
                          "exemple_gresite": {w: r for w, r in list(raspunsuri.items()) if w not in corecte}}
        rezultat[nume]["exemple_gresite"] = dict(list(rezultat[nume]["exemple_gresite"].items())[:6])
    return rezultat


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Poate un model mic să copieze cuvântul pe care îl vede?")
    parser.add_argument("--nou", default="../cyberspace/date/ws/bpe_16384.json")
    parser.add_argument("--vechi", default="../cyberspace/date/tinystories/bpe_4096.json")
    parser.add_argument("--pasi", type=int, default=3000)
    parser.add_argument("--cuvinte-antrenare", type=int, default=3000,
                        help="câte cuvinte diferite învață (din --povesti); 0 = doar 80 de cuvinte ale nivelului 0w")
    parser.add_argument("--povesti", default="../cyberspace/date/tinystories_r2/validare.txt")
    parser.add_argument("--variante", default="", help="doar variantele al căror nume conține acest text")
    parser.add_argument("--fire", type=int, default=12)
    parser.add_argument("--iesire", default="lucru/cod_v04/proba_copiere.json")
    args = parser.parse_args(argv)

    import torch

    torch.set_num_threads(max(1, args.fire))
    cuvinte = list(CUVINTE_0W)
    random.Random(0).shuffle(cuvinte)
    if args.cuvinte_antrenare > 0:
        import re
        from collections import Counter

        text = (RADACINA / args.povesti).read_text(encoding="utf-8")[:3_000_000].lower()
        de_ocolit = set(CUVINTE_0W) | set(CUVINTE_LUNGI_0W)
        dese = Counter(w for w in re.findall(r"[a-z]{3,10}", text) if w not in de_ocolit)
        de_invatat, nevazute = [w for w, _ in dese.most_common(args.cuvinte_antrenare)], cuvinte
    else:
        de_invatat, nevazute = cuvinte[:80], cuvinte[80:]
    de_testat = {"invatate": de_invatat[:30], "nevazute": nevazute, "nevazute_lungi": list(CUVINTE_LUNGI_0W)}
    nou, vechi = TokenizerBPE.incarca(RADACINA / args.nou), TokenizerBPE.incarca(RADACINA / args.vechi)
    variante = [("tokenizer vechi, sarcina de acum", vechi, "de_acum"), ("tokenizer nou, sarcina de acum", nou, "de_acum"),
                ("tokenizer vechi, sarcina cu ghilimele", vechi, "cu_ghilimele"),
                ("tokenizer nou, sarcina cu ghilimele", nou, "cu_ghilimele")]
    rezultate = {}
    print(f"=== Proba de copiere: {len(de_invatat)} cuvinte învățate, {len(nevazute)} nevăzute, "
          f"{len(CUVINTE_LUNGI_0W)} nevăzute lungi; {args.pasi} pași, pe procesor ===")
    for nume, tok, sarcina in [v for v in variante if args.variante in v[0]]:
        r = incearca(tok, SARCINI[sarcina], de_invatat, de_testat, args.pasi)
        rezultate[nume] = r
        print(f"{nume}: învățate {r['invatate']['corecte']}/{r['invatate']['din']}, nevăzute "
              f"{r['nevazute']['corecte']}/{r['nevazute']['din']}, nevăzute lungi "
              f"{r['nevazute_lungi']['corecte']}/{r['nevazute_lungi']['din']} (pierderea {r['pierdere_finala']}, "
              f"{r['secunde']} s)", flush=True)
    iesire = RADACINA / args.iesire
    iesire.parent.mkdir(parents=True, exist_ok=True)
    iesire.write_text(json.dumps(rezultate, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Toate cifrele: {iesire}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
