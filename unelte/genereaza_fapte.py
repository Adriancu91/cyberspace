"""Hrana elevului (Faza 3, pasul 2): profesorul scrie povești cu câte un fapt adevărat, le notează pe loc și le păstrează
doar pe cele bune.

- Subiectele: cele 50 din module/profesor_qwen.py, fiecare cu faptul lui (câte un fapt pe poveste). Stilurile (STILURI)
  și personajele (PERSONAJE) se schimbă pe rând, ca poveștile despre același fapt să nu semene între ele.
- Până la --povesti scrise (9.000) sau --ore (5), ce vine primul. Pe bucăți: profesorul scrie o bucată, o notează pe
  loc, iar rezultatul se adaugă imediat pe disc. Se poate relua: continuă de unde a rămas.
- Se scot poveștile cu nota sub 8 și cele în care faptul apare de mai multe ori, cuvânt cu cuvânt (fără să conteze
  majusculele și semnele); ele rămân în toate.jsonl, cu motivul. Poveștile în care faptul nu apare cuvânt cu cuvânt
  (de obicei e spus altfel, ex. la trecut: „lava came out of volcanoes”) rămân și doar se numără.
Fișierele, în date/fapte/:
- toate.jsonl: fiecare poveste scrisă, cu subiectul, stilul, personajul, faptul, nota, motivul notei, de câte ori apare
  faptul și dacă a rămas;
- povesti.txt: poveștile rămase, despărțite de „<|endoftext|>” (ca TinyStories, gata de antrenare);
- fapte.json: fapt → numerele poveștilor rămase (a câta poveste din povesti.txt, de la 0);
- info.json: câte s-au scris, câte au rămas și de ce s-au scos, distribuția notelor, cuvinte, timp, viteză.
În jurnal, o fișă doar cu numere (linia „fapte”).

    python unelte/genereaza_fapte.py                            # până la 9.000 de povești sau 5 ore
    python unelte/genereaza_fapte.py --povesti 32 --ore 0.1     # probă
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from kronos.jurnal import Jurnal  # noqa: E402
from module.profesor_qwen import FAPTE, PERSONAJE, STILURI, SUBIECTE, ProfesorQwen  # noqa: E402

SEPARATOR = "\n<|endoftext|>\n"
NOTA_MINIMA = 8


def cererea(k: int) -> tuple[str, str, str]:
    """A k-a cerere: toate subiectele pe rând; apoi alt stil; după toate stilurile, alt personaj (apoi de la capăt)."""
    stiluri = list(STILURI)
    subiect = SUBIECTE[k % len(SUBIECTE)][0]
    stil = stiluri[k // len(SUBIECTE) % len(stiluri)]
    personaj = PERSONAJE[k // (len(SUBIECTE) * len(stiluri)) % len(PERSONAJE)]
    return subiect, stil, personaj


def normalizat(text: str) -> str:
    """Litere mici, fără semne (apostroful rămâne), cu spațiile strânse: ca să găsim faptul oricum ar fi scris."""
    text = text.lower().replace("’", "'").replace("‘", "'")
    return " ".join(re.sub(r"[^a-z0-9' ]+", " ", text).split())


def aparitii(poveste: str, fapt: str) -> int:
    """De câte ori apare faptul în poveste, cuvânt cu cuvânt."""
    return len(re.findall(r"(?<![a-z0-9'])" + re.escape(normalizat(fapt)) + r"(?![a-z0-9'])", normalizat(poveste)))


def de_ce_se_scoate(nota: int | None, ori: int) -> str | None:
    """None dacă povestea rămâne; altfel motivul (primul care se potrivește)."""
    if nota is None:
        return "fără notă"
    if nota < NOTA_MINIMA:
        return "nota sub 8"
    if ori > 1:
        return "faptul de mai multe ori"
    return None  # faptul o dată sau spus altfel (ex. la trecut: „lava came out”): rămâne, iar cele „altfel” se numără


def citeste_toate(fisier: Path) -> list[dict[str, Any]]:
    if not fisier.exists():
        return []
    return [json.loads(r) for r in fisier.read_text(encoding="utf-8").splitlines() if r.strip()]


def scrie_rezultatele(dosar: Path, toate: list[dict[str, Any]], secunde: float) -> dict[str, Any]:
    """povesti.txt, fapte.json și info.json, din toate poveștile scrise până acum."""
    ramase = [r for r in toate if r["ramane"]]
    (dosar / "povesti.txt").write_text(SEPARATOR.join(r["poveste"].strip() for r in ramase) + "\n", encoding="utf-8")
    fapte: dict[str, list[int]] = {fapt: [] for fapt in FAPTE.values()}
    for i, r in enumerate(ramase):
        fapte[r["fapt"]].append(i)
    (dosar / "fapte.json").write_text(json.dumps(fapte, ensure_ascii=False, indent=1), encoding="utf-8")
    note = Counter(r["nota"] for r in toate if r["nota"] is not None)
    pe_fapt = [len(v) for v in fapte.values()]
    info = {
        "data": datetime.now().isoformat(timespec="seconds"),
        "scrise": len(toate),
        "ramase": len(ramase),
        "scoase": dict(Counter(r["motiv_scoatere"] for r in toate if not r["ramane"])),
        "distributie_note": {str(n): note.get(n, 0) for n in range(1, 11)},
        "nota_medie": round(statistics.mean(r["nota"] for r in toate if r["nota"] is not None), 2) if note else None,
        "ramase_cu_faptul_spus_altfel": sum(1 for r in ramase if r["aparitii_fapt"] == 0),
        "cuvinte_ramase": sum(len(r["poveste"].split()) for r in ramase),
        "cuvinte_scrise": sum(len(r["poveste"].split()) for r in toate),
        "povesti_pe_fapt_min": min(pe_fapt),
        "povesti_pe_fapt_max": max(pe_fapt),
        "secunde": round(secunde, 1),
    }
    (dosar / "info.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
    return info


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Profesorul scrie povești cu fapte adevărate și le păstrează pe cele bune.")
    parser.add_argument("--dosar", default="date/fapte")
    parser.add_argument("--povesti", type=int, default=9000, help="câte povești scrie profesorul, în total")
    parser.add_argument("--ore", type=float, default=5.0, help="cât timp, cel mult (pentru rularea de acum)")
    parser.add_argument("--lot", type=int, default=16, help="câte povești scrie sau notează deodată")
    parser.add_argument("--bucata", type=int, default=64, help="după câte povești se salvează pe disc")
    parser.add_argument("--director-lucru", default="lucru", help="unde e jurnalul")
    parser.add_argument("--doar-local", action="store_true", help="nu descărca nimic (modelul trebuie să fie în cache)")
    args = parser.parse_args(argv)
    dosar = Path(args.dosar)
    dosar.mkdir(parents=True, exist_ok=True)
    fisier = dosar / "toate.jsonl"
    toate = citeste_toate(fisier)
    inceput = time.perf_counter()
    secunde_inainte = json.loads((dosar / "info.json").read_text(encoding="utf-8"))["secunde"] if toate else 0.0
    profesor = ProfesorQwen(lot=args.lot, doar_local=args.doar_local, samanta=len(toate))
    print(f"Profesorul scrie povești cu fapte: de la a {len(toate) + 1}-a, până la {args.povesti} sau {args.ore:g} ore "
          f"(câte {args.lot} deodată; în {dosar}).", flush=True)
    while len(toate) < args.povesti and time.perf_counter() - inceput < args.ore * 3600:
        cereri = [cererea(k) for k in range(len(toate), min(len(toate) + args.bucata, args.povesti))]
        povesti = profesor.genereaza_mai_multe(cereri)
        note = profesor.noteaza_mai_multe(povesti)
        noi = []
        for (subiect, stil, personaj), poveste, nota in zip(cereri, povesti, note):
            ori = aparitii(poveste, FAPTE[subiect])
            motiv = de_ce_se_scoate(nota["nota"], ori)
            noi.append({"subiect": subiect, "stil": stil, "personaj": personaj, "fapt": FAPTE[subiect],
                        "poveste": poveste, "nota": nota["nota"], "motiv_notei": nota["motiv"], "aparitii_fapt": ori,
                        "ramane": motiv is None, "motiv_scoatere": motiv})
        with fisier.open("a", encoding="utf-8") as f:
            f.write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in noi))
        toate += noi
        info = scrie_rezultatele(dosar, toate, secunde_inainte + time.perf_counter() - inceput)
        print(f"   {len(toate)} scrise, {info['ramase']} rămase ({info['nota_medie']} în medie), la {datetime.now():%H:%M}",
              flush=True)

    info = scrie_rezultatele(dosar, toate, secunde_inainte + time.perf_counter() - inceput)
    info["povesti_pe_minut"] = round(info["scrise"] / (info["secunde"] / 60), 1) if info["secunde"] else None
    info["memorie_gpu_rezervata_mb"] = profesor.memorie_video_mb().get("rezervata")
    (dosar / "info.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
    jurnal = Jurnal(Path(args.director_lucru))
    jurnal.adauga({
        "id": jurnal.urmatorul_id(), "linie": "fapte", "inceput": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "propunere": {"descriere": f"profesorul scrie povești cu fapte (textele: {dosar.as_posix()}/)", "modificari": {}},
        "module": {"profesor": {**ProfesorQwen.MANIFEST, "model": profesor.model}}, "decizie": "masurat",
        "scoruri": {k: info[k] for k in ("scrise", "ramase", "ramase_cu_faptul_spus_altfel", "nota_medie",
                                         "cuvinte_ramase", "cuvinte_scrise", "povesti_pe_fapt_min",
                                         "povesti_pe_fapt_max", "secunde", "povesti_pe_minut", "memorie_gpu_rezervata_mb")},
        "scoase": info["scoase"], "distributie_note": info["distributie_note"],
        "durata_totala_secunde": round(time.perf_counter() - inceput, 1),
    })
    print(f"\n=== Povești cu fapte ({dosar}) ===")
    print(f"Scrise: {info['scrise']:,}; rămase: {info['ramase']:,} ({info['ramase'] / max(info['scrise'], 1):.0%}). "
          f"Scoase: {', '.join(f'{m}: {c:,}' for m, c in info['scoase'].items()) or 'niciuna'}.")
    print("Notele (nota: câte):", ", ".join(f"{n}: {c:,}" for n, c in info["distributie_note"].items() if c))
    print(f"Cuvinte în poveștile rămase: {info['cuvinte_ramase']:,} (din {info['cuvinte_scrise']:,} scrise). Pe fapt: "
          f"între {info['povesti_pe_fapt_min']} și {info['povesti_pe_fapt_max']} povești rămase; în {info['ramase_cu_faptul_spus_altfel']:,} dintre ele, faptul e spus altfel.")
    print(f"Timp: {info['secunde'] / 3600:.2f} ore, {info['povesti_pe_minut']} povești pe minut (cu notatul); memoria video "
          f"rezervată: {info['memorie_gpu_rezervata_mb']} MB.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
