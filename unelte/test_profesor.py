"""Testul de calitate al profesorului (Faza 3, pasul 1): viteza, memoria video, poveștile și notele.

1. Profesorul (module/profesor_qwen.py) scrie 100 de povești: cele 50 de subiecte, fiecare în două stiluri (simplu și cu
   dialog). Se măsoară viteza (povești pe minut, simboluri pe secundă) și memoria video.
2. Profesorul își notează propriile povești: distribuția notelor de la 1 la 10.
3. Elevul (modelul nostru: ultimul model salvat de Kronos pe linia --elev-linie, implicit a treia antrenare lungă, 10 × 512)
   scrie 20 de povești, fiecare pornind din prima propoziție a unei povești din validarea R2 (nevăzută la antrenare),
   tăiate la sfârșitul ultimei propoziții întregi. Profesorul le notează și pe ele, și cele 20 de povești originale din
   TinyStories (aceleași 20, întregi). Media notelor pe fiecare: prima măsură a elevului care nu e val_bpb.
Textele (povești, note, motive) merg în lucru/profesor/test_<data>/. În jurnal se scriu doar numere: o fișă pe linia
„profesor” (ca la dupa_examen, fără niciun text generat).

    python unelte/test_profesor.py
    python unelte/test_profesor.py --povesti 8 --elev 4      # probă scurtă
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from kronos.config import citeste_config  # noqa: E402
from kronos.jurnal import Jurnal  # noqa: E402
from kronos.registru import Registru  # noqa: E402
from module.examene_elev import (  # noqa: E402  (nucleul examenelor e în module/, ca să-l poată folosi și GPT-ul)
    SEPARATOR, alege_povesti, distributie, medie, povesti_elevului, prima_propozitie, taie_la_propozitie,
)
from module.profesor_qwen import SUBIECTE, ProfesorQwen  # noqa: E402

STILURI_TEST = ("simplu", "dialog")










def model_elev(config: Any, jurnal: Jurnal, linie: str) -> tuple[Any, dict[str, Any]]:
    """Ultimul model salvat de Kronos pe linia elevului (ex. ora 8 a antrenării lungi a treia)."""
    fise = [f for f in jurnal.istoric(linie) if f.get("model_salvat")]
    if not fise:
        raise ValueError(f"Linia „{linie}” n-are niciun model salvat de Kronos.")
    fisa = fise[-1]
    model = Registru().creeaza("model", config.porturi["model"]["modul"], fisa["setari"]["model"]).instanta
    model.incarca(fisa["model_salvat"])
    return model, fisa






def scrie_jsonl(cale: Path, randuri: list[dict[str, Any]]) -> None:
    cale.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in randuri), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Testul de calitate al profesorului.")
    parser.add_argument("--config-elev", default="config/laptop_antrenare_lunga_3.toml", help="configurarea elevului")
    parser.add_argument("--elev-linie", default="antrenare_lunga_3", help="linia de jurnal a elevului")
    parser.add_argument("--validare", default="date/tinystories_r2/validare.txt", help="poveștile TinyStories nevăzute")
    parser.add_argument("--povesti", type=int, default=100, help="câte povești scrie profesorul (subiecte × 2 stiluri)")
    parser.add_argument("--elev", type=int, default=20, help="câte povești scrie elevul (și câte originale se notează)")
    parser.add_argument("--lot", type=int, default=8, help="câte povești scrie sau notează profesorul deodată")
    parser.add_argument("--model", default="", help="alt model pentru profesor (implicit cel din modul)")
    parser.add_argument("--doar-local", action="store_true", help="nu descărca nimic (modelul trebuie să fie în cache)")
    args = parser.parse_args(argv)
    inceput_tot = time.perf_counter()
    import torch

    config = citeste_config(args.config_elev)
    jurnal = Jurnal(config.director_lucru)
    eticheta = datetime.now().strftime("%Y%m%d_%H%M%S")
    dosar = config.director_lucru / "profesor" / f"test_{eticheta}"
    dosar.mkdir(parents=True, exist_ok=True)

    # 1. Elevul: 20 de povești din primele propoziții ale unor povești nevăzute (apoi iese de pe placă).
    originale = alege_povesti(Path(args.validare).read_text(encoding="utf-8"), args.elev)
    elev, fisa_elev = model_elev(config, jurnal, args.elev_linie)
    povesti_elev = povesti_elevului(elev, originale)
    del elev
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
    print(f"Elevul (experimentul #{fisa_elev['id']}, linia „{args.elev_linie}”) a scris {len(povesti_elev)} povești.",
          flush=True)

    # 2. Profesorul: se încarcă, scrie poveștile, apoi notează tot.
    profesor = ProfesorQwen(lot=args.lot, doar_local=args.doar_local, **({"model": args.model} if args.model else {}))
    t = time.perf_counter()
    profesor.pregateste()
    secunde_incarcare = time.perf_counter() - t
    cereri = [(subiect, STILURI_TEST[k // len(SUBIECTE) % len(STILURI_TEST)])
              for k, (subiect, _) in enumerate((SUBIECTE * (args.povesti // len(SUBIECTE) + 1))[: args.povesti])]
    t = time.perf_counter()
    povesti_profesor = profesor.genereaza_mai_multe(cereri)
    secunde_scris = time.perf_counter() - t
    simboluri_scris = profesor.simboluri_generate
    print(f"Profesorul a scris {len(povesti_profesor)} povești în {secunde_scris / 60:.1f} minute.", flush=True)
    t = time.perf_counter()
    note_profesor = profesor.noteaza_mai_multe(povesti_profesor)
    note_elev = profesor.noteaza_mai_multe([p["poveste"] for p in povesti_elev])
    note_originale = profesor.noteaza_mai_multe(originale)
    secunde_notat = time.perf_counter() - t
    memorie = profesor.memorie_video_mb()

    # 3. Textele, în lucru/profesor/; numerele, în jurnal.
    from module.profesor_qwen import FAPTE

    scrie_jsonl(dosar / "povesti_profesor.jsonl", [
        {"subiect": s, "stil": st, "fapt": FAPTE.get(s, ""), "poveste": p, **n}
        for (s, st), p, n in zip(cereri, povesti_profesor, note_profesor)])
    scrie_jsonl(dosar / "povesti_elev.jsonl", [{**p, **n} for p, n in zip(povesti_elev, note_elev)])
    scrie_jsonl(dosar / "povesti_tinystories.jsonl", [{"poveste": p, **n} for p, n in zip(originale, note_originale)])
    toate_notele = [n["nota"] for n in note_profesor + note_elev + note_originale]
    scoruri = {
        "povesti_profesor": len(povesti_profesor),
        "povesti_pe_minut": round(len(povesti_profesor) / (secunde_scris / 60), 1),
        "simboluri_pe_secunda_scris": round(simboluri_scris / secunde_scris, 1),
        "cuvinte_pe_poveste": round(statistics.mean(len(p.split()) for p in povesti_profesor), 1),
        "note_pe_minut": round(len(toate_notele) / (secunde_notat / 60), 1),
        "secunde_incarcare": round(secunde_incarcare, 1),
        "memorie_gpu_rezervata_mb": memorie.get("rezervata"),
        "memorie_gpu_folosita_mb": memorie.get("folosita"),
        "nota_medie_profesor": medie([n["nota"] for n in note_profesor]),
        "nota_medie_elev": medie([n["nota"] for n in note_elev]),
        "nota_medie_tinystories": medie([n["nota"] for n in note_originale]),
        "povesti_elev": len(povesti_elev),
        "note_lipsa": sum(1 for n in toate_notele if n is None),
    }
    rezumat = {"scoruri": scoruri, "distributie_note_profesor": distributie([n["nota"] for n in note_profesor]),
               "distributie_note_elev": distributie([n["nota"] for n in note_elev]),
               "distributie_note_tinystories": distributie([n["nota"] for n in note_originale])}
    (dosar / "rezumat.json").write_text(json.dumps(rezumat, ensure_ascii=False, indent=2), encoding="utf-8")
    jurnal.adauga({
        "id": jurnal.urmatorul_id(), "linie": "profesor",
        "inceput": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "propunere": {"descriere": f"testul de calitate al profesorului (textele: lucru/profesor/test_{eticheta}/)",
                      "modificari": {}},
        "module": {"profesor": {**ProfesorQwen.MANIFEST, "model": profesor.model},
                   "elev": {"experiment": fisa_elev["id"], "linie": args.elev_linie}},
        "decizie": "masurat", **rezumat, "durata_totala_secunde": round(time.perf_counter() - inceput_tot, 1),
    })

    # 4. Raportul.
    print(f"\n=== Profesorul ({profesor.model}, 4 biți) ===")
    print(f"Încărcare: {secunde_incarcare:.0f} s. Scris: {scoruri['povesti_pe_minut']} povești pe minut "
          f"({scoruri['simboluri_pe_secunda_scris']} simboluri pe secundă, câte {args.lot} deodată; "
          f"~{scoruri['cuvinte_pe_poveste']:.0f} de cuvinte pe poveste). Notat: {scoruri['note_pe_minut']} note pe minut.")
    print(f"Memoria video: {memorie.get('folosita')} MB folosită, {memorie.get('rezervata')} MB rezervată.")
    for k in range(0, len(povesti_profesor), max(1, len(povesti_profesor) // 5))[:5]:
        print(f"\n--- Exemplu: {cereri[k][0]} ({cereri[k][1]}); nota {note_profesor[k]['nota']}: {note_profesor[k]['motiv']}\n"
              f"{povesti_profesor[k]}")
    print("\nNotele profesorului pentru propriile povești (nota: câte):",
          ", ".join(f"{n}: {c}" for n, c in rezumat["distributie_note_profesor"].items() if c))
    print(f"Media notelor: profesorul {scoruri['nota_medie_profesor']}, elevul {scoruri['nota_medie_elev']}, "
          f"TinyStories {scoruri['nota_medie_tinystories']} (fără notă: {scoruri['note_lipsa']}).")
    print(f"\nTextele: {dosar}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
