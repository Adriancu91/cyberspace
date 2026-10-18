# Raport final: Romanian Language Core (motorul lingvistic), prima livrare

Scris la 19 octombrie 2026, 02:50, de Claude (sesiunea pornită de Adrian pe 18 octombrie, 23:42). Ramura `limba-romana`,
folderul `module/limba_romana/`. Nimic din `kronos/`, `module/examen_bpb.py`, `lucru/` sau `config/` nu a fost atins.
Nu s-a făcut merge în `main`.

## 1. Ce am inspectat și ce am găsit

- Depozitul `Adriancu91/cyberspace` (commit de plecare `f50c839`): platforma Kronos cu 10 porturi; **nu exista nicio
  implementare Romanian Language Core**, nici date lingvistice; `docs/DATE_surse.md` nota că dicționarul Hunspell ro_RO
  nu fusese folosit la antrenare (licență GPL/LGPL/MPL). Portul `memorie` (Memorie ierarhică) e singurul apropiat ca idee;
  nu l-am legat de motor (regula 2 a lui Adrian: motorul rămâne un modul independent, cu o interfață simplă).
- Mediul: Linux, Python 3.13, 2 procesoare, 7,8 GB RAM; rețea doar prin proxy (GitHub, raw.githubusercontent, racai.ro,
  kaikki.org au mers). Calculatorul „kronos” (Windows) e legat la sesiune, dar nu i-am folosit fișierele.
- Sursele verificate (licența citită ÎNAINTE de descărcare, scrisă în `module/limba_romana/LICENTE.md`): Hunspell ro_RO
  (tri-licență GPL 2 / LGPL 2.1 / MPL 1.1), UD Romanian RRT (CC BY-SA 4.0), RoWordNet 3.0 oficial RACAI (CC BY-SA 4.0;
  antetul fișierului declară CC BY 4.0 — am aplicat varianta mai strictă), Wiktionary/kaikki (CC BY-SA + GFDL).
  Neutilizate, cu motiv: pachetul PyPI `rowordnet` (licența datelor nedeclarată; clona ștearsă), dexonline (regula lui
  Adrian: fără DEX; GPL ar fi contaminat baza), tezaurul rospell (proveniență nedocumentată).

## 2. Ce am implementat efectiv (6.175 de linii Python, doar biblioteca standard)

| Strat | Fișiere | Conținut |
|---|---|---|
| Date | `schema.py`, `baza.py`, `identificatori.py` | SQLite cu 16 tabele (lexeme, forme, proveniență, trăsături, concepte, sensuri, relații semantice/sintactice, reguli, exemple, ortografie, surse, validări, contexte), migrări numerotate, 13 verificări de integritate + detectarea ciclurilor, export/import JSONL reproductibil, id-uri deterministice (hash de lemă + categorie + nr. omonim) |
| Text | `text.py` | normalizare (sedile), tokenizare după convențiile UD RRT (clitice: s-a, și-l, nu-i; sigle + articol: ADN-ul; abrevieri; numere), segmentare |
| Importatoare | `importatoare/` (5 fișiere) | descărcare cu amprente sha256; Wiktionary (omonime după etimologie, 969.801 forme din tabele, sensuri, etimologii, registru, relații), UD RRT (9.524 propoziții, forme atestate doar din antrenare+dezvoltare, 485 expresii fixe, 49 relații), RoWordNet (59.348 concepte, 86.347 sensuri, 138.592 relații), Hunspell (interpretorul .aff: 1.027.111 forme generate cu regula de origine, infinitive derivate și confirmate), construirea bazei într-o comandă |
| Morfologie | `morfologie/` (6 fișiere) | inventarul de 71 trăsături (convenția UD); clasele închise scrise de mână (806 forme: pronume, articole al/a/ai/ale, cel, un, lui, demonstrative, nehotărâte, auxiliare, particule, 48 prepoziții cu cazul cerut + 36 locuțiuni, conjuncții, numerale); paradigmele explicite (substantive, adjective, cele 4 conjugări cu -ez/-esc/-ăsc, alternanțe) aplicate peste 134.258 lexeme → 1.469.922 forme generate; analizatorul unei forme (din bază, fără diacritice, ipoteze pentru necunoscute) |
| Dezambiguizare | `dezambiguizare.py` | 20 de reguli de context cu explicații (după „să”, „a”, „o”, auxiliare, „s-”, genitiv, acord cu vecinii, substantiv/verb, participiu/adjectiv, majusculă, subiect), frecvența din corpus ca dovadă; ambiguitatea rămâne marcată |
| Sintaxă | `sintaxa/` (6 fișiere) | grupuri nominale; acordul substantiv–determinant–adjectiv, subiect–predicat (cu subiect coordonat), al/a/ai/ale, numerale cu „de” (20+, 101–119), doi/două, regimul prepozițiilor cu genitiv/dativ; arbore de dependențe de bază (etichete UD, perfect compus, pasiv, copulă, subordonate, relative, atașări alternative); evaluare pe corpus |
| Semantică | `semantica.py` | sensuri/concepte (RoWN în română, Wiktionary în engleză), relații, lanțuri de hiperonime, animat/inanimat, roluri semantice (Agent, Pacient, Beneficiar, Instrument, Loc, Timp…), alegerea sensului din context cu dovezi |
| API / CLI | `motor.py`, `cli.py`, `__main__.py` | `Motor` (API v1: 20 de funcții, rezultate JSON), 12 comenzi din terminal |
| Rapoarte / teste | `acoperire.py`, `teste/` (5 fișiere + fixturi) | raportul de acoperire; 59 de teste |
| Documentație | `README.md`, `ARHITECTURA.md`, `LICENTE.md`, `LIMITARI.md` | instalare, API, decizii, licențe, limitări |

Interfața cerută pentru Kronos: `Motor.verifica_text(text)` → greșelile de acord, numeralele, necunoscutele, diacriticele,
fiecare cu mesaj, regulă, poziții, sugestie, certitudine. Nicio dependență de `kronos/`.

## 3. Sursele importate și volumul

| Sursa | Licența | Ce a intrat în bază |
|---|---|---|
| Hunspell ro_RO 3.3.10 (LibreOffice, commit 67032ee) | GPL 2 / LGPL 2.1 / MPL 1.1 | 181.357 intrări → 112.328 lexeme (81.495 substantive cu gen, 27.562 adjective, 4.638 verbe cu infinitiv confirmat, 644 nume), 157.035 forme atestate, 1.027.111 forme generate de regulile .aff; 33.110 cuvinte doar ortografice; 3.113 verbe neimportate (infinitiv neconfirmat) |
| UD Romanian RRT (commit ee6055b) | CC BY-SA 4.0 | 9.524 propoziții / 218.464 cuvinte (8.043 antrenare, 752 dezvoltare, 729 evaluare); 17.166 lexeme; 34.565 forme atestate (258.079 apariții); 485 expresii fixe; 49 relații de dependență |
| RoWordNet 3.0 (RACAI, rown-3.0.json) | CC BY-SA 4.0 | 59.348 concepte cu definiție în română, 53.244 lexeme (17.862 expresii), 86.347 sensuri, 138.592 relații (hiperonimie 48.320, meronimie 16.000+, antonimie 3.816, similar 4.838…); 1 ciclu în ierarhie (eroare a sursei, raportată) |
| Wiktionary/kaikki (extracție 3 oct. 2026) | CC BY-SA + GFDL | 99.750 lexeme (829 omonime distinse), 880.626 forme atestate din tabele de flexiune, 115.192 sensuri (glose în engleză), 94.521 etimologii (moștenit / împrumut din…), 8.006 lexeme cu registru, 19.520 relații lexicale |
| Tabelele și regulile proprii | ale proiectului | 335 lexeme de clasă închisă / 806 forme; 52 de reguli descrise; 1.469.922 forme generate de paradigme |

**Baza rezultată** (`_baza/limba_romana.sqlite`, 1,1 GB, nu intră în Git, se reconstruiește în ≈ 6–8 minute):
193.676 lexeme (118.246 substantive, 33.489 adjective, 25.931 nume proprii, 10.867 verbe, 3.859 adverbe, clasele închise),
1.767.669 forme cu 3.759.061 proveniențe, 201.539 sensuri, 158.112 relații semantice, 71 trăsături, 532 combinații de trăsături.
Integritatea bazei: toate cele 13 verificări + `integrity_check` + chei străine trec.

## 4. Testele

`python -m pytest module/limba_romana/teste -q` → **59 trecute, 0 picate** (19 octombrie 2026, 02:30), pe:
- unitare, pe fixturi scrise de mână în formatele surselor (tokenizare: 6; trăsături/paradigme/clase închise/Hunspell/id-uri: 11;
  baza mică: importuri, statut, integritate, cicluri, referințe lipsă, export/import reproductibil, lanț de hiperonime, relații: 7);
- integrare și regresie pe baza completă: API v1 (contract), determinism, 16 propoziții corecte fără alarme false, 9 propoziții
  greșite detectate cu sugestia corectă (acord subst–adj, subiect–predicat, al/a/ai/ale, „de” la numerale, doi/două, determinant),
  necunoscute și ipoteze, lexicon și forme, text fără diacritice, ambiguitate păstrată, sensuri și relații, roluri, explicații,
  integritatea bazei complete.

## 5. Acoperirea măsurată (raportul complet: `docs/rapoarte/2026-10-19_0230_acoperire_limba_romana.json`)

Numitorii sunt sursele și seturile de test; nu există un inventar al „întregii limbi române”, deci nu dau procente din limbă.

1. Leme importate: 193.676 (pe surse și categorii mai sus); 58.196 confirmate de ≥ 2 surse; 98.522 substantive cu gen, 19.724 fără.
2. Forme atestate: 956.903 (Wiktionary 880.626, Hunspell 157.035, UD 34.565, tabele proprii 839).
3. Forme generate de reguli: 1.650.891 (Hunspell 1.027.111, paradigme 1.469.922; se suprapun).
4. Forme validate independent (o atestare + o a doua sursă): **857.707**; atestate de o singură sursă: 99.196; doar generate,
   neconfirmate: 810.766. Paradigmele proprii, acolo unde sursele permit verificarea: 809.339 forme confirmate, 22.712 contrazise
   (de ex. genitiv-dativul feminin 94 %, articolul masculin 96 %, prezentul conj. I cu -ez 97 %, prezentul conj. IV în -i fără -esc 67 %,
   imperfectul conj. IV în -i 47 % — alternanțele neregulate; cifre pe fiecare regulă în raport).
5. Categorii gramaticale: toate cele 14 UPOS + X; 6. trăsături: 71 valori în inventar, 68 folosite (nefolosite: Gender=Neut pe forme — prin convenție, NumForm=Digit la lexeme, VerbForm=Sup).
7. Reguli: 52 descrise (16 morfologie, 9 acord, 17 sintaxă, 10 dezambiguizare); 23 evaluate pe corpus, 29 implementate cu teste unitare.
8. Sensuri: 201.539; 127.308 lexeme cu ≥ 1 sens, 53.239 cu sens în română (RoWN), 13.457 polisemantice în RoWN; 66.368 fără sens.
9. Relații semantice: 158.112 (138.592 între concepte, 19.520 între lexeme).
10. Expresii și locuțiuni: 25.671 lexeme multicuvânt (RoWN 17.864, Wiktionary 8.924, UD 366, tabele proprii 68).
11. Evaluare pe UD RRT **setul de test** (729 propoziții, 12.992 tokeni nepunctuație, tokenizare identică în 94,8 % din propoziții):
    categorie 93,16 %, lemă 94,09 %, categorie + trăsături 89,05 %, analiză completă 88,51 %, UAS 67,13 %, LAS 58,13 %;
    cuvinte necunoscute 0,41 % din tokeni; alarme false de acord: 48 (6,6 la 100 de propoziții). Pe setul de dezvoltare:
    categorie 94,15 %, lemă 94,49 %, trăsături 91,24 %, UAS 68,31 %, LAS 59,39 %.
12. Ambiguități: 9.588 tokeni cu ≥ 2 candidați, 8.809 cu categoria aleasă corect (91,9 %); 1.570 marcați „ambiguu”, din care 1.180 cu categoria corectă.
13. Neacoperite (măsurate): 19.724 substantive fără gen, 133 lexeme cu categorie necunoscută, 33.110 cuvinte doar ortografice,
    66.368 lexeme fără sens, 810.766 forme neconfirmate, 22.712 forme contrazise, 292 verbe cu grup de conjugare nedeterminat;
    plus lista declarată din `LIMITARI.md` (verbe neregulate, valență, coreferință, context conversațional, restricții de selecție).

## 6. Ce poate face acum motorul pe exemple reale

```
$ python -m module.limba_romana analizeaza "Copiii frumoși au plecat la școală, dar mama lor a rămas acasă."
   1. Copiii    NOUN  lema=copil   Case=Acc,Nom|Definite=Def|Gender=Masc|Number=Plur [baza/validat] cap=4 nsubj
   2. frumoși   ADJ   lema=frumos  Definite=Ind|Degree=Pos|Gender=Masc|Number=Plur   [baza/validat] cap=1 amod
   3. au        AUX   lema=avea    Number=Plur|Person=3                              [baza/validat] cap=4 aux
   4. plecat    VERB  lema=pleca   Gender=Masc|Number=Sing|VerbForm=Part             [baza/validat] cap=0 root
   5. la        ADP   lema=la      AdpType=Prep|Case=Acc                              [baza/validat] cap=6 case
   6. școală    NOUN  lema=școală  Case=Acc,Nom|Definite=Ind|Gender=Fem|Number=Sing  [baza/validat] cap=4 obl
   8. dar       CCONJ lema=dar     … cap=12 cc      9. mama NOUN lema=mamă … cap=12 nsubj     10. lor PRON lema=el … cap=9 nmod
  11. a         AUX   lema=avea    Number=Sing|Person=3 cap=12 aux   12. rămas VERB lema=rămâne … cap=4 conj   13. acasă ADV … cap=12 advmod
  Roluri: Copiii → Agent (plecat); școală → Loc/Țintă (plecat); mama → Agent (rămas)

$ python -m module.limba_romana verifica "Copii frumoasă a plecat la școală cu 25 mere."
3 probleme
  ! acord_subst_adj: Adjectivul „frumoasă” (feminin singular) nu se acordă cu substantivul „Copii” (masculin plural). Sugestie: frumoși
  ! numeral_de: De la 20 în sus numeralul se leagă de substantiv prin „de”: „25 de mere”. Sugestie: 25 de mere
  ! acord_subiect_predicat: Predicatul „a” (persoana 3, singular) nu se acordă cu subiectul „Copii” (persoana 3, plural). Sugestie: au

$ python -m module.limba_romana sensuri carte NOUN
  [rown] Scriere publicată, cu un anumit subiect, ce a fost tipărită și legată sau broșată în volum.  sinonime: volum
  [rown] Fiecare dintre cele 52 sau 32 de cartoane dreptunghiulare … întrebuințate la unele jocuri de noroc.  sinonime: carte de joc
  [rown] (figurativ) Cunoștințe de scriere și de citire …

$ python -m module.limba_romana explica "Am văzut o fată." 3   → „o”: DET (articol), motive: urmează un nume feminin singular (+3), frecvența în corpus…
```
Alte exemple (din teste): „Cărțile al elevului sunt bune.” → `acord_al`, sugestie „ale”; „Maria și Ion merge la piață.” →
subiect coordonat, sugestie „merg” (certitudine „posibilă”); „Doi fete au venit.” → „două”; „Fata a mâncat un xyzabcul.” →
necunoscut, cu ipoteza „substantiv articulat (-ul)”; „masina” → recunoscut ca „mașină” scris fără diacritice.

## 7. Ce nu poate încă și de ce (detaliat în `module/limba_romana/LIMITARI.md`)

- Arborele sintactic e de bază (UAS 67 %): fără valență verbală și coreferință, atașarea prepozițională rămâne ambiguă (raportată).
- ≈ 6,6 alarme false de acord la 100 de propoziții de corpus (texte juridice/literare/poezie): subiecte postpuse, coordonări
  ambigue, nume compuse. Pe propoziții obișnuite, cum sunt cele din teste, nu apar.
- Participiile adjectivizate (verb ↔ adjectiv) și omografele adverb ↔ prepoziție sunt principalele greșeli de categorie.
- Verbele neregulate și alternanțele neregulate nu sunt generate corect de paradigme (formele corecte vin din surse și sunt marcate).
- Sensurile: doar 53.239 lexeme au definiții în română; alegerea sensului din context nu e evaluată cantitativ (nu există corpus
  adnotat semantic în surse). Contextul conversației nu influențează încă analiza (infrastructura există).
- Nu am importat dexonline (regula lui Adrian) și nici UD SiMoNERo / Nonstandard (ar intra cu același importator).

## 8. Unde e codul și cum îl rulez

Ramura `limba-romana`, folderul `module/limba_romana/` (instrucțiuni complete în `module/limba_romana/README.md`):

```
python -m module.limba_romana.importatoare.descarca_surse            # ≈ 370 MB, licențele în LICENTE.md
python -m module.limba_romana.importatoare.construieste_baza --proaspat   # ≈ 6–8 min, 1,1 GB
python -m pytest module/limba_romana/teste -q                         # 59 de teste
python -m module.limba_romana verifica "Copii frumoasă a plecat."     # sau analizeaza / forma / forme / sensuri / explica / reguli
```
Din Python: `from module.limba_romana import Motor; Motor().verifica_text(text)`.

## 9. Commiturile (ramura `limba-romana`, împinse pe GitHub)

- `e4e5241` schelet, LICENTE.md, descărcarea surselor;
- `9e2aa29` stratul 1: schema bazei, tokenizare, importatoarele celor 4 surse;
- `2360255` stratul 2: morfologie, clase închise, analizator, acord, sintaxă de bază, semantică, API, CLI;
- `c55b8a6` stratul 3: teste, evaluare, raport de acoperire, documentație;
- commitul acestui raport (final) — vezi `git log` pe ramură.

## 10. Criteriile de acceptare

| Criteriu | Stare |
|---|---|
| motorul rulează efectiv | da (CLI + API; 59 de teste; evaluare pe 729 de propoziții reale) |
| datele provin din surse identificabile | da: fiecare rând are `sursa_id`, fiecare formă are originea (regulă sau atestare), amprente sha256 |
| licențele și proveniența sunt documentate | da: `LICENTE.md` + tabela `surse`; obligațiile de redistribuire notate (baza nu se redistribuie) |
| API-ul analizează texte reale | da (măsurat pe UD test: categorie 93 %, lemă 94 %, trăsături 89 %) |
| ambiguitatea e păstrată și tratată explicit | da: toți candidații, scoruri cu motive, marcaj `ambiguu`, atașări alternative, sensuri candidate |
| sensurile sunt distincte de formele lexicale | da: tabele separate `lexeme` / `forme` / `sensuri` / `concepte` |
| relațiile sunt verificabile | da: relații cu sursă, cicluri detectate, integritate referențială |
| testele sunt executate și raportate | da: 59/59 |
| acoperirea e măsurată reproductibil | da: `python -m module.limba_romana acoperire`, cu numitori |
| lipsurile sunt declarate | da: `LIMITARI.md` + secțiunea 13 a raportului de acoperire |
| instalarea și utilizarea sunt documentate | da: README.md, ARHITECTURA.md |
| livrare concretă | da: cod, bază reconstruibilă, teste, rapoarte, documentație |

**Neîndeplinite / parțiale, declarate**: „cea mai completă versiune realizabilă” nu înseamnă limba completă — straturile
sintaxă, semantică și dezambiguizare sunt la nivel de bază (cum a cerut Adrian la completare), cu infrastructura gata și
cifrele reale de mai sus. Formele generate neconfirmate (810.766) sunt marcate, nu declarate corecte.

## Ce aștept de la Adrian

1. Dacă vrea merge în `main` (nu am făcut); 2. dacă alegerea licenței pentru datele derivate din Hunspell (recomand MPL 1.1)
e în regulă — baza oricum nu se redistribuie; 3. dacă următoarea etapă să fie cea din finalul `LIMITARI.md` (genul substantivelor,
valența verbală, participiile adjectivizate, UD SiMoNERo/Nonstandard, contextul conversațional).
