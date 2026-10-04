"""Plafonul GPT-ului simplu pe acest laptop (Etapa M3, testul în trei trepte, pregătirea).

Cel mai mare GPT (cel mai mult parametri) care se antrenează pe placa video sub 5,5 GB, cu lot 8 și context 256:
pentru fiecare lățime (n_emb, cu capete de câte 64), caută câte straturi încap, făcând de fiecare dată 20 de pași de
antrenare adevărați (AdamW, bf16, ca în model_gpt), fiecare încercare într-un proces separat (o placă plină nu strică
încercările următoare). Măsoară memoria rezervată de PyTorch (ce ia de fapt de pe placă; mai strictă decât cea ocupată,
pe care o verifică paznicul). Modelele cu mai puțin de 4 straturi nu intră în alegere (n-ar fi un GPT cu sens).

    python unelte/plafon_gpt.py           # ~10 minute; rezultatul și în lucru/plafon_gpt.json

Simbolurile sunt din tokenizerul TinyStories (4.096); memoria nu depinde de textul ales, deci se folosesc simboluri
la întâmplare.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

LIMITA_MB = 5500  # sub 5,5 GB (aceeași unitate ca paznicul: MB = 2**20 octeți)
LOT, CONTEXT, PASI, VOCAB = 8, 256, 20, 4096
LATIMI = (512, 768, 1024, 1280, 1536, 2048)
MINIM_STRATURI = 4


def parametri(n_emb: int, n_straturi: int, vocab: int = VOCAB, context: int = CONTEXT) -> int:
    """Câți parametri are GPT-ul nostru (aceeași tabelă la intrare și ieșire)."""
    pe_strat = 4 * n_emb * n_emb + 4 * n_emb + 8 * n_emb * n_emb + 5 * n_emb + 4 * n_emb
    return vocab * n_emb + context * n_emb + n_straturi * pe_strat + 2 * n_emb


def proba(n_emb: int, n_straturi: int) -> dict[str, Any]:
    """20 de pași de antrenare cu modelul dat; câtă memorie a luat și cât a durat un pas."""
    import torch
    import torch.nn.functional as F

    from module.model_gpt import _GPT

    torch.manual_seed(0)
    rezultat: dict[str, Any] = {"n_emb": n_emb, "n_straturi": n_straturi, "n_capete": n_emb // 64}
    try:
        retea = _GPT(VOCAB, n_straturi, n_emb // 64, n_emb, CONTEXT, 0.0).cuda()
        rezultat["parametri"] = sum(p.numel() for p in retea.parameters())
        optimizator = torch.optim.AdamW(retea.parameters(), lr=3e-4, weight_decay=0.1)
        torch.cuda.reset_peak_memory_stats()
        start = None
        for pas in range(PASI):
            if pas == 2:  # primii pași încălzesc placa
                torch.cuda.synchronize()
                start = time.perf_counter()
            x = torch.randint(VOCAB, (LOT, CONTEXT), device="cuda")
            y = torch.randint(VOCAB, (LOT, CONTEXT), device="cuda")
            with torch.autocast("cuda", dtype=torch.bfloat16):
                logits = retea(x)
                loss = F.cross_entropy(logits.float().view(-1, VOCAB), y.view(-1))
            optimizator.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(retea.parameters(), 1.0)
            optimizator.step()
        torch.cuda.synchronize()
        rezultat["secunde_pe_pas"] = round((time.perf_counter() - start) / (PASI - 2), 4)
        rezultat["memorie_ocupata_mb"] = round(torch.cuda.max_memory_allocated() / 2**20)
        rezultat["memorie_rezervata_mb"] = round(torch.cuda.max_memory_reserved() / 2**20)
        rezultat["incape"] = rezultat["memorie_rezervata_mb"] <= LIMITA_MB
    except torch.cuda.OutOfMemoryError:
        rezultat.update(parametri=parametri(n_emb, n_straturi), incape=False, eroare="placa s-a umplut")
    return rezultat


def _in_proces(n_emb: int, n_straturi: int) -> dict[str, Any]:
    iesire = subprocess.run(
        [sys.executable, __file__, "--proba", str(n_emb), str(n_straturi)],
        capture_output=True, text=True, encoding="utf-8", cwd=RADACINA,
    )
    linii = [l for l in iesire.stdout.splitlines() if l.startswith("{")]
    if not linii:
        return {"n_emb": n_emb, "n_straturi": n_straturi, "parametri": parametri(n_emb, n_straturi), "incape": False,
                "eroare": (iesire.stderr.strip().splitlines() or ["procesul a căzut"])[-1]}
    return json.loads(linii[-1])


def cauta_latimea(n_emb: int, incearca=_in_proces) -> tuple[int, list[dict[str, Any]]]:
    """Câte straturi încap la lățimea dată (0 = niciunul): dublez până nu mai încape, apoi caut la mijloc."""
    probe: list[dict[str, Any]] = []

    def incape(n: int) -> bool:
        rezultat = incearca(n_emb, n)
        probe.append(rezultat)
        print(f"   n_emb {n_emb}, {n} straturi: {rezultat.get('parametri', 0) / 1e6:6.1f} M parametri, "
              f"{rezultat.get('memorie_rezervata_mb', '-')} MB rezervați → {'încape' if rezultat['incape'] else 'NU încape'}",
              flush=True)
        return bool(rezultat["incape"])

    if not incape(1):
        return 0, probe
    jos, sus = 1, 2
    while incape(sus):
        jos, sus = sus, sus * 2
        if sus > 128:
            return jos, probe
    while sus - jos > 1:
        mijloc = (jos + sus) // 2
        if incape(mijloc):
            jos = mijloc
        else:
            sus = mijloc
    return jos, probe


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Cel mai mare GPT care se antrenează sub 5,5 GB (lot 8, context 256).")
    parser.add_argument("--proba", type=int, nargs=2, metavar=("N_EMB", "N_STRATURI"), help="o singură încercare (intern)")
    parser.add_argument("--latimi", type=int, nargs="+", default=list(LATIMI))
    args = parser.parse_args(argv)
    if args.proba:
        print(json.dumps(proba(*args.proba)), flush=True)
        return 0

    print(f"Plafonul GPT-ului: lot {LOT}, context {CONTEXT}, {PASI} de pași, limita {LIMITA_MB} MB rezervați.", flush=True)
    toate: list[dict[str, Any]] = []
    cele_mai_mari: list[dict[str, Any]] = []
    for n_emb in args.latimi:
        straturi, probe = cauta_latimea(n_emb)
        toate += probe
        if straturi:
            cele_mai_mari.append(next(p for p in probe if p["n_straturi"] == straturi and p["incape"]))
    alese = [p for p in cele_mai_mari if p["n_straturi"] >= MINIM_STRATURI]
    if not alese:
        print("Niciun model cu cel puțin 4 straturi nu încape.")
        return 1
    plafon = max(alese, key=lambda p: p["parametri"])
    print("\nCel mai mare model la fiecare lățime:")
    for p in cele_mai_mari:
        print(f"   n_emb {p['n_emb']:>5}, {p['n_straturi']:>3} straturi, {p['n_capete']:>2} capete: {p['parametri'] / 1e6:7.1f} M "
              f"parametri, {p['memorie_ocupata_mb']} MB ocupați / {p['memorie_rezervata_mb']} MB rezervați, "
              f"{1 / p['secunde_pe_pas']:.1f} pași/s")
    print(f"\nPlafonul: n_emb {plafon['n_emb']}, {plafon['n_straturi']} straturi, {plafon['n_capete']} capete: "
          f"{plafon['parametri']:,} de parametri ({plafon['memorie_rezervata_mb']} MB rezervați).")
    iesire = Path("lucru") / "plafon_gpt.json"
    iesire.parent.mkdir(parents=True, exist_ok=True)
    iesire.write_text(json.dumps({"lot": LOT, "context": CONTEXT, "pasi": PASI, "limita_mb": LIMITA_MB, "plafon": plafon,
                                  "cele_mai_mari": cele_mai_mari, "toate_probele": toate}, ensure_ascii=False, indent=2),
                      encoding="utf-8")
    print(f"Salvat în {iesire}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
