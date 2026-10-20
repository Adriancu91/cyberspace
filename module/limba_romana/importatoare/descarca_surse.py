"""Descarcă (reproductibil) sursele lingvistice ale motorului, în `_surse/`.

Licențele au fost verificate înainte de descărcare și sunt scrise în `LICENTE.md`.
Fiecare fișier descărcat se verifică cu amprenta sha256 de acolo; dacă amprenta diferă, sursa s-a
schimbat față de versiunea documentată și scriptul o spune (nu o ascunde).

Folosire:
    python -m module.limba_romana.importatoare.descarca_surse            # toate sursele
    python -m module.limba_romana.importatoare.descarca_surse --doar ud_rrt rown
    python -m module.limba_romana.importatoare.descarca_surse --verifica   # doar verifică amprentele
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

RADACINA = Path(__file__).resolve().parent.parent
DIR_SURSE = RADACINA / "_surse"

# (sursa, fișier local, URL, sha256 așteptat sau None)
FISIERE: list[tuple[str, str, str, str | None]] = [
    # 1. Hunspell ro_RO — tri-licență GPL 2.0 / LGPL 2.1 / MPL 1.1 (Rospell Team), pachetul LibreOffice, commit 67032ee
    ("hunspell", "hunspell/ro_RO.aff",
     "https://raw.githubusercontent.com/LibreOffice/dictionaries/67032ee957631908098a72edf48dc81cac27e369/ro/ro_RO.aff",
     "0c83a02f0ac5202c068e60e1aef5ce99e13d7f6c92ae8e68ca8b9e06829edfd1"),
    ("hunspell", "hunspell/ro_RO.dic",
     "https://raw.githubusercontent.com/LibreOffice/dictionaries/67032ee957631908098a72edf48dc81cac27e369/ro/ro_RO.dic",
     "c26a9356f598a0ae89e7be650f6bdd9ba70acce66b41d7ab14c0c68639b6ed33"),
    ("hunspell", "hunspell/README_EN.txt",
     "https://raw.githubusercontent.com/LibreOffice/dictionaries/67032ee957631908098a72edf48dc81cac27e369/ro/README_EN.txt", None),
    ("hunspell", "hunspell/COPYING.MPL",
     "https://raw.githubusercontent.com/LibreOffice/dictionaries/67032ee957631908098a72edf48dc81cac27e369/ro/COPYING.MPL", None),
    ("hunspell", "hunspell/COPYING.LGPL",
     "https://raw.githubusercontent.com/LibreOffice/dictionaries/67032ee957631908098a72edf48dc81cac27e369/ro/COPYING.LGPL", None),
    ("hunspell", "hunspell/COPYING.GPL",
     "https://raw.githubusercontent.com/LibreOffice/dictionaries/67032ee957631908098a72edf48dc81cac27e369/ro/COPYING.GPL", None),
    # 2. UD Romanian RRT — CC BY-SA 4.0, commit ee6055b
    ("ud_rrt", "ud_rrt/ro_rrt-ud-train.conllu",
     "https://raw.githubusercontent.com/UniversalDependencies/UD_Romanian-RRT/ee6055b4b1f725eb48d9436bc5902a5685be7d96/ro_rrt-ud-train.conllu",
     "15c7a90a45f8a7ae809c09f6ec9cf2250bf4cf323cf0cbfcda7cfc4dbac4ea19"),
    ("ud_rrt", "ud_rrt/ro_rrt-ud-dev.conllu",
     "https://raw.githubusercontent.com/UniversalDependencies/UD_Romanian-RRT/ee6055b4b1f725eb48d9436bc5902a5685be7d96/ro_rrt-ud-dev.conllu",
     "b81e3848e9e9fb06afd32867a8795208edc3305df981aedc361c8273dc84a3bf"),
    ("ud_rrt", "ud_rrt/ro_rrt-ud-test.conllu",
     "https://raw.githubusercontent.com/UniversalDependencies/UD_Romanian-RRT/ee6055b4b1f725eb48d9436bc5902a5685be7d96/ro_rrt-ud-test.conllu",
     "32a2f7b9fc82c1e82d9959ce8c5ec7b7840f725177aa06b497b51f6834801989"),
    ("ud_rrt", "ud_rrt/README.md",
     "https://raw.githubusercontent.com/UniversalDependencies/UD_Romanian-RRT/ee6055b4b1f725eb48d9436bc5902a5685be7d96/README.md", None),
    ("ud_rrt", "ud_rrt/LICENSE.txt",
     "https://raw.githubusercontent.com/UniversalDependencies/UD_Romanian-RRT/ee6055b4b1f725eb48d9436bc5902a5685be7d96/LICENSE.txt", None),
    # 3. RoWordNet 3.0 — CC BY-SA 4.0 (pagina oficială RACAI RoLLOD)
    ("rown", "rown/rown-3.0.json", "https://www.racai.ro/p/llod/resources/rown-3.0.json",
     "8cdaac317ba5b96a175a631ed1ca4e2dfde19388bd22d776b16991d868eca374"),
    # 4. Wiktionary (en), intrările în română, extrase de kaikki.org — CC BY-SA + GFDL
    ("kaikki", "kaikki/kaikki.org-dictionary-Romanian.jsonl",
     "https://kaikki.org/dictionary/Romanian/kaikki.org-dictionary-Romanian.jsonl",
     "9eed987bef2d4137f1c455eb24f1731e850147273bd7126f42527de9a6c68cfa"),
]


def sha256_fisier(cale: Path) -> str:
    h = hashlib.sha256()
    with open(cale, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


def descarca(url: str, cale: Path) -> None:
    cale.parent.mkdir(parents=True, exist_ok=True)
    cerere = urllib.request.Request(url, headers={"User-Agent": "limba_romana/descarca_surse"})
    with urllib.request.urlopen(cerere, timeout=600) as r, open(cale, "wb") as f:
        while True:
            bloc = r.read(1 << 20)
            if not bloc:
                break
            f.write(bloc)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--doar", nargs="*", default=None, help="sursele de descărcat (hunspell, ud_rrt, rown, kaikki)")
    p.add_argument("--verifica", action="store_true", help="nu descarcă nimic, verifică doar amprentele")
    a = p.parse_args(argv)

    manifest_cale = DIR_SURSE / "manifest.json"
    manifest = json.loads(manifest_cale.read_text("utf8")) if manifest_cale.exists() else {}
    probleme = 0
    for sursa, local, url, sha in FISIERE:
        if a.doar and sursa not in a.doar:
            continue
        cale = DIR_SURSE / local
        if not cale.exists():
            if a.verifica:
                print(f"LIPSĂ      {local}")
                probleme += 1
                continue
            print(f"descarc    {local} <- {url}")
            try:
                descarca(url, cale)
            except Exception as e:  # noqa: BLE001 - raportăm orice eroare de rețea, fără să o ascundem
                print(f"EROARE     {local}: {e}")
                probleme += 1
                continue
        amprenta = sha256_fisier(cale)
        stare = "ok"
        if sha and amprenta != sha:
            stare = "AMPRENTĂ DIFERITĂ față de LICENTE.md (sursa s-a schimbat?)"
            probleme += 1
        print(f"{stare:10} {local} sha256={amprenta[:16]}…")
        manifest[local] = {
            "sursa": sursa, "url": url, "sha256": amprenta, "octeti": cale.stat().st_size,
            "data": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "amprenta_asteptata": sha, "stare": stare,
        }
    DIR_SURSE.mkdir(parents=True, exist_ok=True)
    manifest_cale.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), "utf8")
    print(f"manifest scris: {manifest_cale} ({'fără probleme' if not probleme else f'{probleme} probleme'})")
    return 1 if probleme else 0


if __name__ == "__main__":
    sys.exit(main())
