"""Construiește biblioteca de sensuri pentru memoria ierarhică.

Descarcă Open English WordNet 2024 (licență CC-BY 4.0, ~13 MB) și îl
transformă în date/biblioteca.json.gz, fișierul pe care îl citește
modulul module/memorie_ierarhica.py.

Ce conține biblioteca:
- fiecare SENS (nu cuvânt!) are un loc fix în ierarhie: parte de vorbire →
  raft (una din 45 de categorii mari, ex. „noun.animal”) → lanțul de
  categorii din WordNet (ex. organism → animal → mamifer → cal);
- fiecare loc primește un cod pe niveluri, ca la bibliotecă (ex. 1.05.3.2.1);
- relațiile dintre sensuri: parte-din, membru-din, opus, domeniu.

Rulează din folderul proiectului:
    python unelte/construieste_biblioteca.py
"""

from __future__ import annotations

import gzip
import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

URL = "https://github.com/globalwordnet/english-wordnet/releases/download/2024-edition/english-wordnet-2024.xml.gz"
RADACINA = Path(__file__).resolve().parent.parent
SURSA = RADACINA / "date" / "english-wordnet-2024.xml.gz"
DESTINATIE = RADACINA / "date" / "biblioteca.json.gz"

PARTI_DE_VORBIRE = {"n": 1, "v": 2, "a": 3, "s": 3, "r": 4}  # s = adjectiv „satelit” → tot adjectiv
NUME_PARTI = {1: "substantiv", 2: "verb", 3: "adjectiv", 4: "adverb"}
RELATII_PASTRATE = {
    "mero_part": "are_parte",
    "holo_part": "parte_din",
    "mero_member": "are_membru",
    "holo_member": "membru_din",
    "mero_substance": "facut_din",
    "antonym": "opus",
    "domain_topic": "domeniu",
    "entails": "implica",
    "causes": "cauzeaza",
    "similar": "asemanator",
    "attribute": "atribut",
}


def descarca() -> None:
    if SURSA.exists() and SURSA.stat().st_size > 10_000_000:
        print(f"Există deja: {SURSA.name}")
        return
    SURSA.parent.mkdir(parents=True, exist_ok=True)
    print(f"Descarc Open English WordNet 2024 (~13 MB)...")
    with urllib.request.urlopen(URL, timeout=120) as raspuns:
        SURSA.write_bytes(raspuns.read())
    print(f"Gata: {SURSA}")


def citeste() -> tuple[dict, dict, dict]:
    """Întoarce: synseturi {id: info}, forme {cuvant: [id sens, ...]}, relații {id: [(tip, id)]}."""
    synseturi: dict[str, dict] = {}
    # forme[cuvant] = [(prioritate, ordine, synset)]; prioritatea alege sensul principal:
    # 0 = cuvântul de bază scris cu literă mică, 1 = nume proprii, 2 = forme flexionate (ex. „rose” de la „rise”)
    forme: dict[str, list[tuple[int, int, str]]] = defaultdict(list)
    ordine = 0
    relatii: dict[str, list[tuple[str, str]]] = defaultdict(list)
    sens_la_synset: dict[str, str] = {}
    relatii_sens: list[tuple[str, str, str]] = []

    with gzip.open(SURSA, "rb") as f:
        for _, el in ET.iterparse(f, events=("end",)):
            if el.tag == "LexicalEntry":
                lemma = el.find("Lemma").get("writtenForm")
                cuvinte = [(lemma, 0 if lemma == lemma.lower() else 1)]
                cuvinte += [(fo.get("writtenForm"), 2) for fo in el.findall("Form")]
                for sens in el.findall("Sense"):
                    sens_la_synset[sens.get("id")] = sens.get("synset")
                    for cuv, prioritate in cuvinte:
                        ordine += 1
                        forme[cuv.lower().replace(" ", "_")].append((prioritate, ordine, sens.get("synset")))
                    for rel in sens.findall("SenseRelation"):
                        if rel.get("relType") == "antonym":
                            relatii_sens.append((sens.get("synset"), "antonym", rel.get("target")))
                el.clear()
            elif el.tag == "Synset":
                hiper = [r.get("target") for r in el.findall("SynsetRelation")
                         if r.get("relType") in ("hypernym", "instance_hypernym")]
                membri = el.get("members", "").split()
                nume = membri[0].removeprefix("oewn-").rsplit("-", 1)[0] if membri else el.get("id")
                synseturi[el.get("id")] = {
                    "pos": PARTI_DE_VORBIRE.get(el.get("partOfSpeech"), 1),
                    "raft": el.get("lexfile", "necunoscut"),
                    "parinte": hiper[0] if hiper else None,
                    "nume": nume,
                }
                for r in el.findall("SynsetRelation"):
                    if r.get("relType") in RELATII_PASTRATE:
                        relatii[el.get("id")].append((RELATII_PASTRATE[r.get("relType")], r.get("target")))
                el.clear()

    for sursa, _, tinta_sens in relatii_sens:
        tinta = sens_la_synset.get(tinta_sens)
        if tinta and ("opus", tinta) not in relatii[sursa]:
            relatii[sursa].append(("opus", tinta))
    # Între sensurile la fel de „principale”, substantivele și verbele au întâietate (ex. „rose” = trandafir).
    ordine_pos = {"n": 0, "v": 1, "a": 2, "s": 2, "r": 3}
    forme_ordonate: dict[str, list[str]] = {}
    for cuv, lista in forme.items():
        unice: list[str] = []
        for _, _, synset in sorted(lista, key=lambda t: (t[0], ordine_pos.get(t[2][-1], 4), t[1])):
            if synset not in unice:
                unice.append(synset)
        forme_ordonate[cuv] = unice
    return synseturi, forme_ordonate, relatii


def construieste(synseturi: dict, forme: dict, relatii: dict) -> dict:
    # Ordinea fixă: mereu aceleași numere, oricând rulezi.
    ids = sorted(synseturi)
    index = {s: i for i, s in enumerate(ids)}

    # Rafturile (cele 45 de categorii mari), numerotate stabil.
    rafturi = sorted({s["raft"] for s in synseturi.values()})
    nr_raft = {r: i + 1 for i, r in enumerate(rafturi)}

    # Copiii fiecărui nod, ca să numerotăm locurile ca la bibliotecă.
    # Rădăcinile se numerotează separat pentru fiecare parte de vorbire.
    copii: dict[object, list[str]] = defaultdict(list)
    for s in ids:
        parinte = synseturi[s]["parinte"]
        if parinte not in synseturi:
            parinte = ("radacina", synseturi[s]["pos"])
        copii[parinte].append(s)
    pozitie = {}
    for parinte, lista in copii.items():
        for k, s in enumerate(sorted(lista, key=lambda x: synseturi[x]["nume"]), start=1):
            pozitie[s] = k

    def lant(s: str) -> list[str]:
        vazute, drum = set(), []
        while s is not None and s in synseturi and s not in vazute:
            vazute.add(s)
            drum.append(s)
            s = synseturi[s]["parinte"]
        return list(reversed(drum))

    noduri = []
    for s in ids:
        info = synseturi[s]
        drum = lant(s)
        noduri.append({
            "p": index[info["parinte"]] if info["parinte"] in index else -1,
            "pos": info["pos"],
            "raft": nr_raft[info["raft"]],
            "n": info["nume"],
            "cod": [info["pos"], nr_raft[info["raft"]]] + [pozitie[x] for x in drum],
        })

    return {
        "sursa": "Open English WordNet 2024, licență CC-BY 4.0, https://github.com/globalwordnet/english-wordnet",
        "parti_de_vorbire": NUME_PARTI,
        "rafturi": rafturi,
        "noduri": noduri,
        "forme": {f: [index[s] for s in lista if s in index] for f, lista in sorted(forme.items())},
        "relatii": {str(index[s]): [[t, index[x]] for t, x in lista if x in index]
                    for s, lista in sorted(relatii.items()) if s in index},
    }


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    try:
        descarca()
    except OSError as e:
        print(f"Nu am putut descărca WordNet: {e}", file=sys.stderr)
        return 1
    print("Citesc WordNet (durează ~1 minut)...")
    synseturi, forme, relatii = citeste()
    biblioteca = construieste(synseturi, forme, relatii)
    DESTINATIE.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(DESTINATIE, "wt", encoding="utf-8") as f:
        json.dump(biblioteca, f, ensure_ascii=False, separators=(",", ":"))
    print(
        f"Gata: {DESTINATIE.name} — {len(biblioteca['noduri']):,} sensuri, "
        f"{len(biblioteca['forme']):,} forme de cuvinte, {len(biblioteca['rafturi'])} rafturi, "
        f"{sum(len(v) for v in biblioteca['relatii'].values()):,} relații"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
