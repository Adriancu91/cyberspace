# Arhitectura motorului Romanian Language Core (RLC)

Modul al platformei Cyberspace (`module/limba_romana/`). Nucleul platformei rămâne Kronos; motorul nu importă nimic din
`kronos/` și nu depinde de niciun model neuronal. Alte module îl pot folosi prin `Motor` (vezi README.md, secțiunea API).

## Principiul: simbolic, inspectabil, cu proveniență

```
 text ──► tokenizare (text.py) ──► analize morfologice (morfologie/analizator.py: din bază + ipoteze)
      ──► dezambiguizare explicată (dezambiguizare.py: scoruri = dovezi numite)
      ──► grupuri nominale + acord (sintaxa/acord.py) ──► dependențe de bază (sintaxa/dependente.py)
      ──► sensuri și roluri (semantica.py) ──► rezultat structurat (motor.py, JSON)
```

Fiecare pas păstrează alternativele: cuvintele au `candidati` (toate analizele) + `ales` + `ambiguu`; sintaxa
păstrează `analize_alternative` (atașări posibile); semantica listează toate sensurile cu dovezile lor.

## Straturile și fișierele

| Strat | Fișiere | Ce conține |
|---|---|---|
| Date | `schema.py`, `baza.py`, `identificatori.py` | schema SQLite (migrări numerotate), integritate (referințe lipsă, cicluri), export/import JSONL, identificatori deterministici |
| Text | `text.py` | normalizare (sedile), tokenizare după convențiile UD RRT (clitice, sigle + articol, abrevieri), segmentare |
| Lexicon | `importatoare/*` | importatoarele celor 4 surse + construirea bazei; fiecare rând are `sursa_id` și proveniență |
| Morfologie | `morfologie/trasaturi.py`, `inchise.py`, `paradigme.py`, `hunspell.py`, `analizator.py` | inventarul trăsăturilor, clasele închise scrise de mână, paradigmele explicite, interpretorul .aff, analiza unei forme |
| Dezambiguizare | `dezambiguizare.py` | reguli de context cu explicații; frecvențe din corpus ca dovezi (nu probabilități) |
| Sintaxă | `sintaxa/structuri.py`, `acord.py`, `dependente.py`, `reguli.py`, `analiza.py`, `evaluare.py` | grupuri, acord (subst–det–adj, subiect–predicat, al/a/ai/ale, numerale cu „de”, regim prepozițional), dependențe UD de bază, registrul regulilor, evaluarea pe UD |
| Semantică | `semantica.py` | sensuri/concepte, relații, lanțuri de hiperonime, animat/inanimat, roluri semantice, alegerea sensului (Lesk explicabil) |
| API | `motor.py`, `cli.py`, `__main__.py` | clasa `Motor` (versiunea API 1) și linia de comandă |
| Rapoarte | `acoperire.py` | raportul de acoperire (cifre cu numitor cunoscut) |
| Teste | `teste/` | unitare (fixturi scrise de mână), integrare/regresie (baza completă), evaluare |

## Modelul de date (SQLite, `_baza/limba_romana.sqlite`)

- `lexeme` (id stabil = hash(lemă, categorie, nr. omonim)) — lemă, categorie UPOS, gen, clasă, multicuvânt, statut, atribute (etimologie, registru);
- `forme` — (formă, lexem, trăsături canonice) unic; `statut`: `atestat` / `generat` / `validat`;
- `forme_provenienta` — pentru fiecare formă: sursa, originea (`atestare:ud_rrt:antrenare`, `atestare:kaikki:tabel`,
  `regula:hunspell:SFX A 7`, `regula:paradigma:subst_fem_sg_art`, `atestare:tabel_propriu`), detalii, frecvență;
- `trasaturi` — inventarul cheie=valoare (convenția UD RRT; `Gender=Neut` doar la lexem);
- `concepte` (synseturi RoWN, cu ILI) ↔ `sensuri` (lexem ↔ concept, sau glosă Wiktionary) ↔ `relatii_semantice`
  (nivel concept / lexem; tipurile RoWN + synonym/antonym/derived/related din Wiktionary);
- `reguli` — registrul regulilor explicite (morfologie, acord, sintaxă, dezambiguizare) cu statut;
- `exemple` + `exemple_cuvinte` — corpusul UD RRT, cu setul (antrenare / dezvoltare / evaluare);
- `relatii_sintactice` — inventarul relațiilor de dependență (cu descrieri în română);
- `ortografie` — cuvinte cunoscute doar ortografic (Hunspell fără clasă), fără lemă/categorie;
- `surse`, `validari`, `migratii`, `contexte`.

Statutul formelor (`baza.recalculeaza_statut_forme`): `validat` = cel puțin o atestare + o a doua sursă diferită;
`atestat` = o singură sursă care o atestă; `generat` = doar reguli. Două reguli care coincid nu validează.

## Convenții luate (decizii documentate)

1. **Trăsăturile urmează UD RRT** (nu Wiktionary, nu Hunspell), ca să putem compara direct cu corpusul: neutrul e Masc la
   singular / Fem la plural pe forme; `Case` lipsește la nearticulatul sincretic (masculin singular, toate pluralele);
   `Degree=Pos` implicit la adjective; infinitivul are `Tense=Pres`; auxiliarele perfectului/viitorului/condiționalului
   au doar Person/Number (`am` = `Person=1`).
2. **Omonimele** sunt distinse doar de Wiktionary (numărul de etimologie); celelalte surse se leagă de toate omonimele,
   cu notă de proveniență. Clasele închise (pronume, determinanți etc.) nu se despart în omonime.
3. **Lemele verbelor** = infinitivul fără „a” (ca în UD și Wiktionary). Hunspell listează persoana I singular; infinitivul
   e derivat prin regulă și acceptat doar dacă e confirmat de o intrare din dicționar sau de altă sursă (3.113 neconfirmate, numărate).
4. **Formele cu prefix** (re-, ne-, auto-) și cele cu clitice lipite din Hunspell nu se materializează: sunt derivări,
   respectiv tokenizare (cliticele se despart).
5. **Setul de evaluare UD (test) nu alimentează lexiconul**; exemplele lui sunt stocate ca `evaluare` și folosite doar la măsurare.
6. **Scorurile dezambiguizării** sunt sume de dovezi numite (+3 decisiv, +2 puternic, +1 slab, frecvența din corpus
   logaritmic plafonată la +3); nu sunt probabilități. Ambiguitatea rămâne marcată când scorurile sunt apropiate.
7. **Verificările de acord sunt conservatoare**: se reclamă doar când nicio analiză plauzibilă a cuvintelor implicate nu se
   acordă; subiectul postpus se acceptă doar la verbe intranzitive/copulative; la persoanele I/II subiectul trebuie să fie pronume.
8. **Gradele de comparație, timpurile compuse, diateza pasivă** sunt sintactice (nu forme): „mai bun”, „am citit”, „a fost citit”.

## Surse de documentare pentru reguli

Gramatica Academiei (GALR, 2005/2008) pentru paradigme și acord (regulile limbii nu sunt protejate; nu s-a copiat text);
convențiile UD (universaldependencies.org, treebank ro_rrt) pentru etichete și relații; Hunspell: formatul .aff/.dic.
