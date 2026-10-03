"""Construiește biblioteca de sensuri pentru memoria ierarhică (Etapa M1).

Descarcă Open English WordNet 2024 (licență CC-BY 4.0, ~13 MB) și scrie
date/biblioteca.json.gz, fișierul citit de module/memorie_ierarhica.py.

Ce pune în bibliotecă, pentru fiecare SENS (nu cuvânt: „horse” are mai multe sensuri):
- părintele (hypernym: „horse” → „equine”) și raftul (lexfile, ex. noun.animal);
- un cod pe niveluri, ca o cotă de bibliotecă: parte de vorbire, raft, apoi
  poziția fiecărui strămoș în nivelul lui, de la rădăcină până la sens;
- relațiile: parte din / are parte, membru din / are membru, opus.
Plus formele cuvintelor: lema și formele neregulate (geese → goose, ran → run).

Rulează din folderul proiectului:
    python unelte/construieste_biblioteca.py
"""

from __future__ import annotations

import argparse
import gzip
import json
import re
import shutil
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from typing import Any

URL = "https://github.com/globalwordnet/english-wordnet/releases/download/2024-edition/english-wordnet-2024.xml.gz"
RADACINA = Path(__file__).resolve().parent.parent
SURSA = RADACINA / "date" / "english-wordnet-2024.xml.gz"
DESTINATIE = RADACINA / "date" / "biblioteca.json.gz"
VERSIUNE_BIBLIOTECA = 1

# Primul nivel al codului. „s” (adjectiv „satelit”) e tot un adjectiv.
PARTI_DE_VORBIRE = ["substantiv", "verb", "adjectiv", "adverb"]
COD_PARTE = {"n": 1, "v": 2, "a": 3, "s": 3, "r": 4}
ORDINE_PARTE = {"n": 0, "v": 1, "a": 2, "s": 2, "r": 3}  # cine e „sensul principal” la egalitate
PARINTI = ("hypernym", "instance_hypernym")  # „instance”: Paris este un oraș
RELATII = {"holo_part": "parte_din", "mero_part": "are_parte", "holo_member": "membru_din", "mero_member": "are_membru"}
# Doar formele dintr-un singur cuvânt pot apărea în text („o'clock” da, „horse racing” nu).
FORMA_CUVANT = re.compile(r"[a-z]+(?:'[a-z]+)*")


def descarca(url: str, destinatie: Path) -> None:
    """Descarcă într-un fișier temporar, ca o întrerupere să nu lase un fișier stricat."""
    destinatie.parent.mkdir(parents=True, exist_ok=True)
    temporar = destinatie.with_name(destinatie.name + ".part")
    with urllib.request.urlopen(url, timeout=120) as raspuns, temporar.open("wb") as f:
        shutil.copyfileobj(raspuns, f)
    temporar.replace(destinatie)


def citeste_wordnet(cale: Path) -> dict[str, Any]:
    """Citește fișierul WordNet (XML în format LMF, .xml.gz) și păstrează doar ce ne trebuie."""
    intrari: list[tuple[str, str, list[str], list[str]]] = []  # (lemă, parte, forme, synset-uri în ordinea sensurilor)
    lema_intrarii: dict[str, str] = {}
    sens_la_synset: dict[str, str] = {}
    antonime: list[tuple[str, str]] = []  # (synset, id-ul sensului opus)
    synseturi: dict[str, dict[str, Any]] = {}
    sursa = "WordNet"

    with gzip.open(cale, "rb") as f:
        for _, el in ET.iterparse(f, events=("end",)):
            if el.tag == "LexicalEntry":
                lema = el.find("Lemma")
                sensuri = []
                for sens in el.findall("Sense"):
                    synset = sens.get("synset")
                    sens_la_synset[sens.get("id")] = synset
                    sensuri.append(synset)
                    antonime += [(synset, r.get("target")) for r in sens.findall("SenseRelation")
                                 if r.get("relType") == "antonym"]
                forme = [fo.get("writtenForm") for fo in el.findall("Form")]
                intrari.append((lema.get("writtenForm"), lema.get("partOfSpeech"), forme, sensuri))
                lema_intrarii[el.get("id")] = lema.get("writtenForm")
                el.clear()
            elif el.tag == "Synset":
                parinte, relatii = None, []
                for rel in el.findall("SynsetRelation"):
                    tip = rel.get("relType")
                    if tip in PARINTI and parinte is None:
                        parinte = rel.get("target")
                    elif tip in RELATII:
                        relatii.append((RELATII[tip], rel.get("target")))
                synseturi[el.get("id")] = {
                    "parte": el.get("partOfSpeech"),
                    "raft": el.get("lexfile", "necunoscut"),
                    "parinte": parinte,
                    "membri": el.get("members", "").split(),
                    "relatii": relatii,
                }
                el.clear()
            elif el.tag == "Lexicon":
                sursa = f"{el.get('label')} {el.get('version')}, licență {el.get('license')}, {el.get('url')}"

    return {
        "sursa": sursa,
        "intrari": intrari,
        "lema_intrarii": lema_intrarii,
        "sens_la_synset": sens_la_synset,
        "antonime": antonime,
        "synseturi": synseturi,
    }


def construieste(wn: dict[str, Any]) -> dict[str, Any]:
    """Transformă WordNet-ul citit în biblioteca de sensuri (doar liste și dicționare, gata de JSON)."""
    synseturi = wn["synseturi"]
    ids = sorted(synseturi)  # ordine fixă: aceleași numere la fiecare construire
    index = {s: i for i, s in enumerate(ids)}
    rafturi = sorted({info["raft"] for info in synseturi.values()})
    nr_raft = {r: i + 1 for i, r in enumerate(rafturi)}

    def nume(s: str) -> str:
        for membru in synseturi[s]["membri"]:
            if membru in wn["lema_intrarii"]:
                return wn["lema_intrarii"][membru]
        return s

    nume_sens = {s: nume(s) for s in ids}

    def parinte(s: str) -> str | None:
        p = synseturi[s]["parinte"]
        return p if p in synseturi else None

    # Pozițiile, ca la bibliotecă: frații (copiii aceluiași părinte), în ordine alfabetică, primesc 1, 2, 3...
    # Sensurile fără părinte (rădăcinile) se numără separat pentru fiecare parte de vorbire.
    frati: dict[Any, list[str]] = defaultdict(list)
    for s in ids:
        p = parinte(s)
        frati[p if p is not None else ("radacina", COD_PARTE.get(synseturi[s]["parte"], 1))].append(s)
    pozitie: dict[str, int] = {}
    for grup in frati.values():
        for k, s in enumerate(sorted(grup, key=lambda x: (nume_sens[x].lower(), x)), start=1):
            pozitie[s] = k

    def drum(s: str) -> list[str]:
        """Strămoșii lui s, de la rădăcină până la el (cu pază împotriva cercurilor)."""
        lant: list[str] = []
        vazute: set[str] = set()
        curent: str | None = s
        while curent is not None and curent not in vazute:
            vazute.add(curent)
            lant.append(curent)
            curent = parinte(curent)
        return lant[::-1]

    coduri = []
    for s in ids:
        info = synseturi[s]
        coduri.append([COD_PARTE.get(info["parte"], 1), nr_raft[info["raft"]]] + [pozitie[x] for x in drum(s)])

    # Formele: pentru fiecare cuvânt, sensurile lui în ordine, cel principal primul.
    # Prioritate: lema scrisă cu litere mici, apoi numele proprii („cat” înaintea lui „CAT”),
    # apoi formele flexionate; la egalitate substantiv, verb, adjectiv, adverb; apoi ordinea din WordNet.
    candidati: dict[str, list[tuple[int, int, int, list[str]]]] = defaultdict(list)
    for nr, (lema, parte, forme, sensuri) in enumerate(wn["intrari"]):
        variante = [(lema, 0 if lema == lema.lower() else 1)] + [(fo, 2) for fo in forme]
        for forma, prioritate in variante:
            cheie = forma.lower()
            if FORMA_CUVANT.fullmatch(cheie):
                candidati[cheie].append((prioritate, ORDINE_PARTE.get(parte, 4), nr, sensuri))
    forme_finale: dict[str, list[int]] = {}
    for cheie in sorted(candidati):
        lista: list[int] = []
        for _, _, _, sensuri in sorted(candidati[cheie], key=lambda c: c[:3]):
            for s in sensuri:
                i = index.get(s)
                if i is not None and i not in lista:
                    lista.append(i)
        if lista:
            forme_finale[cheie] = lista

    relatii: dict[int, list[list[Any]]] = defaultdict(list)

    def leaga(sursa: str, tip: str, tinta: str | None) -> None:
        if sursa in index and tinta in index and [tip, index[tinta]] not in relatii[index[sursa]]:
            relatii[index[sursa]].append([tip, index[tinta]])

    for s in ids:
        for tip, tinta in synseturi[s]["relatii"]:
            leaga(s, tip, tinta)
    for s, sens_opus in wn["antonime"]:
        leaga(s, "opus", wn["sens_la_synset"].get(sens_opus))

    return {
        "versiune": VERSIUNE_BIBLIOTECA,
        "sursa": wn["sursa"],
        "parti_de_vorbire": PARTI_DE_VORBIRE,
        "rafturi": rafturi,
        "nume": [nume_sens[s] for s in ids],
        "parinte": [index[p] if (p := parinte(s)) is not None else -1 for s in ids],
        "cod": coduri,
        "forme": forme_finale,
        "relatii": {str(i): relatii[i] for i in sorted(relatii)},
    }


def scrie_biblioteca(biblioteca: dict[str, Any], cale: Path) -> None:
    cale.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(cale, "wt", encoding="utf-8") as f:
        json.dump(biblioteca, f, ensure_ascii=False, separators=(",", ":"))


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Construiește biblioteca de sensuri din Open English WordNet 2024.")
    parser.add_argument("--sursa", type=Path, default=SURSA, help="fișierul WordNet .xml.gz (se descarcă dacă lipsește)")
    parser.add_argument("--destinatie", type=Path, default=DESTINATIE, help="unde se scrie biblioteca")
    args = parser.parse_args(argv)

    if not args.sursa.exists():
        print("Descarc Open English WordNet 2024 (~13 MB, licență CC-BY 4.0)...")
        try:
            descarca(URL, args.sursa)
        except OSError as e:
            print(f"Nu am putut descărca: {e}\nVerifică internetul și încearcă din nou.", file=sys.stderr)
            return 1
    print("Citesc WordNet și construiesc biblioteca (durează cam un minut)...")
    start = time.perf_counter()
    biblioteca = construieste(citeste_wordnet(args.sursa))
    scrie_biblioteca(biblioteca, args.destinatie)
    niveluri = max(len(c) for c in biblioteca["cod"]) - 2
    print(f"Gata în {time.perf_counter() - start:.0f} s: {args.destinatie}")
    print(
        f"  {len(biblioteca['cod']):,} sensuri, {len(biblioteca['forme']):,} forme de cuvinte, "
        f"{len(biblioteca['rafturi'])} rafturi, {sum(map(len, biblioteca['relatii'].values())):,} relații; "
        f"ierarhia are cel mult {niveluri} niveluri"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
