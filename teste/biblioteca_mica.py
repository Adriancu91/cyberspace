"""Un WordNet minuscul, cu aceeași structură ca fișierul real, și biblioteca construită din el.

Testele îl folosesc ca să nu descarce WordNet-ul adevărat (13 MB).
Ierarhia:  entity > organism > animal > {horse, cat}
           entity > artifact > {sword, horse (calul de gimnastică)}
           entity > {hoof, herd, CAT, horse racing}
           run > gallop (verbe), horse (verb), good / bad (adjective opuse), o'clock (adverb)
           entity > artifact > can (cutia de conserve: în text, „can” e de obicei verbul modal)
           organism > person (raftul noun.Tops, ca în WordNet) > girl (noun.person)
           see (verb, cu forma „saw”) și saw (fierăstrăul, sub artifact); back (spatele, sub entity) și back (adverb)
           bite (verb, cu forma „bit”) și bit (burghiul, sub artifact)
"""

from __future__ import annotations

import gzip
from pathlib import Path

from unelte.construieste_biblioteca import citeste_wordnet, construieste, scrie_biblioteca

XML_MIC = """<?xml version="1.0" encoding="UTF-8"?>
<LexicalResource xmlns:dc="https://globalwordnet.github.io/schemas/dc/">
  <Lexicon id="test" label="WordNet de test" language="en" email="x@y" license="CC-BY 4.0" version="1" url="https://example.org">
    <LexicalEntry id="t-entity-n"><Lemma writtenForm="entity" partOfSpeech="n"/><Sense id="t-entity-1" synset="t-01-n"/></LexicalEntry>
    <LexicalEntry id="t-organism-n"><Lemma writtenForm="organism" partOfSpeech="n"/><Sense id="t-organism-1" synset="t-02-n"/></LexicalEntry>
    <LexicalEntry id="t-animal-n"><Lemma writtenForm="animal" partOfSpeech="n"/><Sense id="t-animal-1" synset="t-03-n"/></LexicalEntry>
    <LexicalEntry id="t-horse-n"><Lemma writtenForm="horse" partOfSpeech="n"/>
      <Sense id="t-horse-1" synset="t-04-n"/><Sense id="t-horse-2" synset="t-10-n"/></LexicalEntry>
    <LexicalEntry id="t-horse-v"><Lemma writtenForm="horse" partOfSpeech="v"/><Form writtenForm="horse"/><Sense id="t-horse-v1" synset="t-15-v"/></LexicalEntry>
    <LexicalEntry id="t-cat-n"><Lemma writtenForm="cat" partOfSpeech="n"/><Sense id="t-cat-1" synset="t-05-n"/></LexicalEntry>
    <LexicalEntry id="t-CAT-n"><Lemma writtenForm="CAT" partOfSpeech="n"/><Sense id="t-CAT-1" synset="t-16-n"/></LexicalEntry>
    <LexicalEntry id="t-hoof-n"><Lemma writtenForm="hoof" partOfSpeech="n"><Pronunciation>huːf</Pronunciation></Lemma>
      <Form writtenForm="hooves"/><Sense id="t-hoof-1" synset="t-06-n"/></LexicalEntry>
    <LexicalEntry id="t-herd-n"><Lemma writtenForm="herd" partOfSpeech="n"/><Sense id="t-herd-1" synset="t-07-n"/></LexicalEntry>
    <LexicalEntry id="t-artifact-n"><Lemma writtenForm="artifact" partOfSpeech="n"/><Sense id="t-artifact-1" synset="t-08-n"/></LexicalEntry>
    <LexicalEntry id="t-sword-n"><Lemma writtenForm="sword" partOfSpeech="n"/><Sense id="t-sword-1" synset="t-09-n"/></LexicalEntry>
    <LexicalEntry id="t-horse_racing-n"><Lemma writtenForm="horse racing" partOfSpeech="n"/><Sense id="t-hr-1" synset="t-17-n"/></LexicalEntry>
    <LexicalEntry id="t-run-v"><Lemma writtenForm="run" partOfSpeech="v"/><Form writtenForm="ran"/><Sense id="t-run-1" synset="t-11-v"/></LexicalEntry>
    <LexicalEntry id="t-gallop-v"><Lemma writtenForm="gallop" partOfSpeech="v"/><Sense id="t-gallop-1" synset="t-12-v"/></LexicalEntry>
    <LexicalEntry id="t-good-a"><Lemma writtenForm="good" partOfSpeech="a"/>
      <Sense id="t-good-1" synset="t-13-a"><SenseRelation relType="antonym" target="t-bad-1"/></Sense></LexicalEntry>
    <LexicalEntry id="t-bad-a"><Lemma writtenForm="bad" partOfSpeech="a"/>
      <Sense id="t-bad-1" synset="t-14-a"><SenseRelation relType="antonym" target="t-good-1"/></Sense></LexicalEntry>
    <LexicalEntry id="t-oclock-r"><Lemma writtenForm="o'clock" partOfSpeech="r"/><Sense id="t-oclock-1" synset="t-18-r"/></LexicalEntry>
    <LexicalEntry id="t-can-n"><Lemma writtenForm="can" partOfSpeech="n"/><Sense id="t-can-1" synset="t-19-n"/></LexicalEntry>
    <LexicalEntry id="t-person-n"><Lemma writtenForm="person" partOfSpeech="n"/><Sense id="t-person-1" synset="t-20-n"/></LexicalEntry>
    <LexicalEntry id="t-girl-n"><Lemma writtenForm="girl" partOfSpeech="n"/><Sense id="t-girl-1" synset="t-21-n"/></LexicalEntry>
    <LexicalEntry id="t-see-v"><Lemma writtenForm="see" partOfSpeech="v"/><Form writtenForm="saw"/><Sense id="t-see-1" synset="t-22-v"/></LexicalEntry>
    <LexicalEntry id="t-saw-n"><Lemma writtenForm="saw" partOfSpeech="n"/><Sense id="t-saw-1" synset="t-23-n"/></LexicalEntry>
    <LexicalEntry id="t-back-n"><Lemma writtenForm="back" partOfSpeech="n"/><Sense id="t-back-1" synset="t-24-n"/></LexicalEntry>
    <LexicalEntry id="t-back-r"><Lemma writtenForm="back" partOfSpeech="r"/><Sense id="t-back-2" synset="t-25-r"/></LexicalEntry>
    <LexicalEntry id="t-bit-n"><Lemma writtenForm="bit" partOfSpeech="n"/><Sense id="t-bit-1" synset="t-26-n"/></LexicalEntry>
    <LexicalEntry id="t-bite-v"><Lemma writtenForm="bite" partOfSpeech="v"/><Form writtenForm="bit"/><Sense id="t-bite-1" synset="t-27-v"/></LexicalEntry>
    <Synset id="t-01-n" members="t-entity-n" partOfSpeech="n" lexfile="noun.Tops"/>
    <Synset id="t-02-n" members="t-organism-n" partOfSpeech="n" lexfile="noun.Tops">
      <SynsetRelation relType="hypernym" target="t-01-n"/></Synset>
    <Synset id="t-03-n" members="t-animal-n" partOfSpeech="n" lexfile="noun.Tops">
      <SynsetRelation relType="hypernym" target="t-02-n"/></Synset>
    <Synset id="t-04-n" members="t-horse-n" partOfSpeech="n" lexfile="noun.animal">
      <Definition>solid-hoofed herbivorous quadruped</Definition>
      <SynsetRelation relType="hypernym" target="t-03-n"/>
      <SynsetRelation relType="mero_part" target="t-06-n"/>
      <SynsetRelation relType="holo_member" target="t-07-n"/>
      <SynsetRelation relType="hyponym" target="t-99-n"/></Synset>
    <Synset id="t-05-n" members="t-cat-n" partOfSpeech="n" lexfile="noun.animal">
      <SynsetRelation relType="hypernym" target="t-03-n"/></Synset>
    <Synset id="t-06-n" members="t-hoof-n" partOfSpeech="n" lexfile="noun.body">
      <SynsetRelation relType="hypernym" target="t-01-n"/><SynsetRelation relType="holo_part" target="t-04-n"/></Synset>
    <Synset id="t-07-n" members="t-herd-n" partOfSpeech="n" lexfile="noun.group">
      <SynsetRelation relType="hypernym" target="t-01-n"/><SynsetRelation relType="mero_member" target="t-04-n"/></Synset>
    <Synset id="t-08-n" members="t-artifact-n" partOfSpeech="n" lexfile="noun.Tops">
      <SynsetRelation relType="hypernym" target="t-01-n"/></Synset>
    <Synset id="t-09-n" members="t-sword-n" partOfSpeech="n" lexfile="noun.artifact">
      <SynsetRelation relType="hypernym" target="t-08-n"/></Synset>
    <Synset id="t-10-n" members="t-horse-n" partOfSpeech="n" lexfile="noun.artifact">
      <SynsetRelation relType="hypernym" target="t-08-n"/></Synset>
    <Synset id="t-11-v" members="t-run-v" partOfSpeech="v" lexfile="verb.motion"/>
    <Synset id="t-12-v" members="t-gallop-v" partOfSpeech="v" lexfile="verb.motion">
      <SynsetRelation relType="hypernym" target="t-11-v"/></Synset>
    <Synset id="t-13-a" members="t-good-a" partOfSpeech="a" lexfile="adj.all"/>
    <Synset id="t-14-a" members="t-bad-a" partOfSpeech="s" lexfile="adj.all"/>
    <Synset id="t-15-v" members="t-horse-v" partOfSpeech="v" lexfile="verb.motion"/>
    <Synset id="t-16-n" members="t-CAT-n" partOfSpeech="n" lexfile="noun.act">
      <SynsetRelation relType="hypernym" target="t-01-n"/></Synset>
    <Synset id="t-17-n" members="t-horse_racing-n" partOfSpeech="n" lexfile="noun.act">
      <SynsetRelation relType="instance_hypernym" target="t-01-n"/></Synset>
    <Synset id="t-18-r" members="t-oclock-r" partOfSpeech="r" lexfile="adv.all"/>
    <Synset id="t-19-n" members="t-can-n" partOfSpeech="n" lexfile="noun.artifact">
      <SynsetRelation relType="hypernym" target="t-08-n"/></Synset>
    <Synset id="t-20-n" members="t-person-n" partOfSpeech="n" lexfile="noun.Tops">
      <SynsetRelation relType="hypernym" target="t-02-n"/></Synset>
    <Synset id="t-21-n" members="t-girl-n" partOfSpeech="n" lexfile="noun.person">
      <SynsetRelation relType="hypernym" target="t-20-n"/></Synset>
    <Synset id="t-22-v" members="t-see-v" partOfSpeech="v" lexfile="verb.perception"/>
    <Synset id="t-23-n" members="t-saw-n" partOfSpeech="n" lexfile="noun.artifact">
      <SynsetRelation relType="hypernym" target="t-08-n"/></Synset>
    <Synset id="t-24-n" members="t-back-n" partOfSpeech="n" lexfile="noun.body">
      <SynsetRelation relType="hypernym" target="t-01-n"/></Synset>
    <Synset id="t-25-r" members="t-back-r" partOfSpeech="r" lexfile="adv.all"/>
    <Synset id="t-26-n" members="t-bit-n" partOfSpeech="n" lexfile="noun.artifact">
      <SynsetRelation relType="hypernym" target="t-08-n"/></Synset>
    <Synset id="t-27-v" members="t-bite-v" partOfSpeech="v" lexfile="verb.contact"/>
  </Lexicon>
</LexicalResource>
"""


def wordnet_mic(director: Path) -> Path:
    """Scrie WordNet-ul minuscul ca .xml.gz (exact ca fișierul descărcat)."""
    cale = Path(director) / "wordnet_mic.xml.gz"
    with gzip.open(cale, "wt", encoding="utf-8") as f:
        f.write(XML_MIC)
    return cale


def biblioteca_mica(director: Path) -> str:
    """Construiește biblioteca din WordNet-ul minuscul, cu scriptul adevărat. Întoarce calea ei."""
    cale = Path(director) / "biblioteca_mica.json.gz"
    scrie_biblioteca(construieste(citeste_wordnet(wordnet_mic(director))), cale)
    return str(cale)
