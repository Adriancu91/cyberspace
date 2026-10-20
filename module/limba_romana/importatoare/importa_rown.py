"""Importă RoWordNet 3.0 (RACAI, forma JSON după schema Global WordNet) în bază.

Ce intră:
  - `concepte`: synseturile, cu definiția lor în română, categoria și identificatorul interlingual (ILI);
  - `lexeme`: literalele (lemele) synseturilor — un literal cu „_” e o expresie multicuvânt;
  - `sensuri`: perechea lexem ↔ concept (un sens pe fiecare literal al unui synset);
  - `relatii_semantice` între concepte: hypernym, hyponym, meronimie/holonimie (parte, membru, substanță),
    antonym, similar, domain_topic, attribute, entails, causes, instance_hypernym/hyponym.
Antonimia în RoWN e înregistrată între synseturi (nu între literale); o păstrăm la nivel de concept.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from ..baza import Baza
from ..identificatori import id_concept, id_sens
from ..text import normalizeaza
from .comun import DIR_SURSE, Numarator, lexeme_tinta, manifest_sursa

SURSA_ID = "rown"
POS_ROWN = {"n": "NOUN", "v": "VERB", "a": "ADJ", "r": "ADV"}
DESCRIERI_RELATII = {
    "hypernym": "hiperonim (este un fel de)", "hyponym": "hiponim (fel de)", "instance_hypernym": "instanță a (clasa unei entități)",
    "instance_hyponym": "instanță (entitate a clasei)", "holo_part": "întreg (din părți)", "mero_part": "parte a",
    "holo_member": "grup (al membrilor)", "mero_member": "membru al", "holo_substance": "substanță din care e făcut",
    "mero_substance": "substanță a", "similar": "asemănător (adjective)", "antonym": "antonim", "domain_topic": "domeniu",
    "has_domain_topic": "termen al domeniului", "has_domain_region": "termen al regiunii", "attribute": "atribut",
    "entails": "implică", "causes": "cauzează",
}


def importa(baza: Baza, cale: Path | None = None, verbos: bool = True) -> dict:
    cale = cale or (DIR_SURSE / "rown" / "rown-3.0.json")
    n = Numarator()
    m = manifest_sursa("rown")
    baza.adauga_sursa(
        SURSA_ID, "RoWordNet 3.0 (Romanian WordNet), RACAI — Institutul de Cercetări pentru Inteligență Artificială „Mihai Drăgănescu”, Academia Română",
        licenta="CC BY-SA 4.0 (pagina oficială RoLLOD); antetul fișierului declară CC BY 4.0", url="https://www.racai.ro/p/llod/",
        versiune="rown-3.0.json (descărcat 18 octombrie 2026)",
        atribuire="Dan Tufiș, Verginica Barbu Mititelu. The Lexical Ontology for Romanian. Springer, 2014; RACAI",
        obligatii="atribuire; datele derivate rămân sub CC BY-SA 4.0", fisiere=[k for k in m] or [cale.name],
        transformari="JSON (schema Global WordNet) → concepte, lexeme (literale), sensuri, relații între concepte",
        limitari="fără relații la nivel de literal (antonimia e între synseturi); glosele unor synseturi pot fi scurte",
        data_descarcarii=next((v["data"] for v in m.values()), ""),
    )
    with open(cale, encoding="utf-8-sig") as f:
        date = json.load(f)
    lexicon = date["@graph"][0]
    concepte_existente = {s["@id"] for s in lexicon["synset"]}
    for s in lexicon["synset"]:
        pos = POS_ROWN.get(s.get("partOfSpeech"), "X")
        definitie = "; ".join(d.get("gloss", "") for d in s.get("definition", []) if d.get("gloss"))
        baza.adauga_concept(id_concept("rown", s["@id"].removeprefix("rown-")), pos, definitie or None, SURSA_ID, ili=s.get("ili"))
        n("concepte")
    baza.commit()
    sensuri_pe_lexem: dict[str, int] = defaultdict(int)
    cache: dict[tuple[str, str], list[str]] = {}
    for e in lexicon["entry"]:
        lema = e["lemma"]["writtenForm"].replace("_", " ")
        pos = POS_ROWN.get(e.get("partOfSpeech"), "X")
        cheie = (normalizeaza(lema), pos)
        if cheie not in cache:
            cache[cheie] = lexeme_tinta(baza, lema, pos, SURSA_ID, multicuvant=" " in lema, detalii="literal RoWordNet")
            n("lexeme")
            if " " in lema:
                n("lexeme_multicuvant")
        for sens in e.get("sense", []):
            if sens["synsetRef"] not in concepte_existente:
                n("sensuri_cu_synset_lipsa"); continue
            cid = id_concept("rown", sens["synsetRef"].removeprefix("rown-"))
            for lid in cache[cheie]:
                sensuri_pe_lexem[lid] += 1
                baza.adauga_sens(id_sens(lid, cid, sensuri_pe_lexem[lid]), lid, cid, None, sensuri_pe_lexem[lid], SURSA_ID, "importat", ["definiție în română (RoWordNet)"])
                n("sensuri")
    baza.commit()
    for s in lexicon["synset"]:
        de_la = id_concept("rown", s["@id"].removeprefix("rown-"))
        for r in s.get("relations", []) or []:
            if r["target"] not in concepte_existente:
                n("relatii_cu_tinta_lipsa"); continue
            baza.adauga_relatie_semantica(r["relType"], "concept", de_la, id_concept("rown", r["target"].removeprefix("rown-")), SURSA_ID)
            n("relatii"); n(f"relatii_{r['relType']}")
    baza.commit()
    if verbos:
        print("RoWordNet:", json.dumps(n.dict(), ensure_ascii=False))
    return n.dict()


if __name__ == "__main__":
    with Baza() as b:
        importa(b)
