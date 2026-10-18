# Sursele lingvistice și licențele lor — Romanian Language Core

Regula (Adrian, 18 octombrie 2026): licența fiecărei surse se verifică **înainte** de descărcare și se
scrie aici, cu sursa și autorul. Datele mari nu intră în Git: intră doar scripturile care le descarcă
(`importatoare/descarca_surse.py`) și amprentele (sha256) din `_surse/manifest.json`.

Nu se folosesc definiții din dexonline / DEX sau din alte dicționare protejate (regula lui Adrian,
19 octombrie 2026). Tezaurul `th_ro_RO_v2.dat` din pachetul rospell nu se folosește (proveniența
conținutului lui nu e documentată în pachet).

## Surse folosite

| # | Sursa | Autor / deținător | Versiune folosită | Licența verificată | Ce se importă | Obligații |
|---|---|---|---|---|---|---|
| 1 | **Hunspell ro_RO** (dicționarul ortografic „rospell”, pachetul LibreOffice `dictionaries/ro`) | Rospell Team, 2005–2013: Lucian Constantin, Andrei Cipu, Sorin Sbârnea, Alexandru Szasz, Ionuț Păduraru, Adrian Stoica, Nicu Buculei, Cătălin Frâncu, Ionel Mugurel Ciobică, Mihai Budiu — http://rospell.sourceforge.net | word list 3.3.10; depozitul `LibreOffice/dictionaries`, commit `67032ee957631908098a72edf48dc81cac27e369` (12 octombrie 2026) | **tri-licență GPL 2.0 / LGPL 2.1 / MPL 1.1** (fișierul `README_EN.txt` și antetul `ro_RO.aff`) | `ro_RO.dic` (181.357 intrări), `ro_RO.aff` (regulile de flexiune, clasele de flaguri) | se alege o licență din cele trei; formele generate din dicționar sunt o lucrare derivată din el: dacă se redistribuie, rămân sub licența aleasă (recomandat: MPL 1.1, copyleft doar la nivel de fișier). Se păstrează notița de copyright și autorii. |
| 2 | **UD Romanian RRT** (RoRefTrees, corpus de referință adnotat, Universal Dependencies) | Verginica Barbu Mititelu, Elena Irimia, Cenel-Augusto Perez, Radu Ion, Radu Simionescu, Martin Popel și colaboratorii UD — https://universaldependencies.org/treebanks/ro_rrt/ | depozitul `UniversalDependencies/UD_Romanian-RRT`, commit `ee6055b4b1f725eb48d9436bc5902a5685be7d96` (6 mai 2026) | **CC BY-SA 4.0** (`LICENSE.txt` și `README.md`) | `ro_rrt-ud-train/dev/test.conllu`: 9.524 propoziții, 218.464 cuvinte-token cu lemă, categorie (UPOS), etichetă MSD, trăsături și relații de dependență | atribuire; orice redistribuire a datelor derivate (forme atestate, exemple) rămâne sub CC BY-SA 4.0. Observație din README: lemele sunt „automatic”, trăsăturile „converted with corrections”, relațiile „manual native”. |
| 3 | **RoWordNet (RoWN 3.0)**, forma JSON (schema Global WordNet) | Institutul de Cercetări pentru Inteligență Artificială „Mihai Drăgănescu” al Academiei Române (RACAI); Dan Tufiș, Verginica Barbu Mititelu și colab. — https://www.racai.ro/p/llod/ | fișierul `rown-3.0.json` de pe pagina RoLLOD (descărcat 18 octombrie 2026) | **CC BY-SA 4.0** conform paginii oficiale https://www.racai.ro/p/llod/index_en.html („RoWN is available under the license CC BY-SA 4.0”). Antetul fișierului JSON declară `https://creativecommons.org/licenses/by/4.0/` (CC BY 4.0). Se aplică varianta mai strictă (CC BY-SA 4.0). | 59.348 synseturi (concepte) cu definiții, 85.277 intrări lemă–sens, 18 tipuri de relații semantice | atribuire (RACAI; citarea: Tufiș & Barbu Mititelu, 2014); datele derivate rămân sub CC BY-SA 4.0. |
| 4 | **Wiktionary (ediția engleză), intrările în limba română, extrase de kaikki.org** | contribuitorii Wiktionary; extracția: Tatu Ylonen (wiktextract) — https://kaikki.org/dictionary/Romanian/ | extracție din 3 octombrie 2026, din dump-ul enwiktionary din 2 septembrie 2026; fișierul `kaikki.org-dictionary-Romanian.jsonl` | **CC BY-SA + GFDL** („This data is made available under the same licenses as Wiktionary - both CC-BY-SA and GFDL”, pagina https://kaikki.org/dictionary/); Wiktionary: CC BY-SA 4.0 (textele mai vechi: 3.0) | 130.512 intrări (cuvânt + categorie): tabele de flexiune (1.382.851 forme etichetate), sensuri cu glose în engleză, etichete de registru (regional, arhaic, învechit, colocvial), etimologie (moșteniri/împrumuturi), sinonime/antonime | atribuire (Wiktionary, kaikki.org); datele derivate rămân sub CC BY-SA. |

Amprentele sha256 ale fișierelor descărcate (18–19 octombrie 2026):

```
0c83a02f0ac5202c068e60e1aef5ce99e13d7f6c92ae8e68ca8b9e06829edfd1  hunspell/ro_RO.aff
c26a9356f598a0ae89e7be650f6bdd9ba70acce66b41d7ab14c0c68639b6ed33  hunspell/ro_RO.dic
15c7a90a45f8a7ae809c09f6ec9cf2250bf4cf323cf0cbfcda7cfc4dbac4ea19  ud_rrt/ro_rrt-ud-train.conllu
b81e3848e9e9fb06afd32867a8795208edc3305df981aedc361c8273dc84a3bf  ud_rrt/ro_rrt-ud-dev.conllu
32a2f7b9fc82c1e82d9959ce8c5ec7b7840f725177aa06b497b51f6834801989  ud_rrt/ro_rrt-ud-test.conllu
8cdaac317ba5b96a175a631ed1ca4e2dfde19388bd22d776b16991d868eca374  rown/rown-3.0.json
9eed987bef2d4137f1c455eb24f1731e850147273bd7126f42527de9a6c68cfa  kaikki/kaikki.org-dictionary-Romanian.jsonl
```

## Cum stau licențele una lângă alta

- Codul motorului (`module/limba_romana/`) este al proiectului Cyberspace (Adrian). Nu conține text din surse,
  decât regulile gramaticale scrise de mână (regulile limbii nu sunt protejate; sursele de documentare sunt
  citate în `ARHITECTURA.md`).
- Baza generată (`_baza/limba_romana.sqlite`) este o lucrare derivată din sursele de mai sus. Fiecare rând
  poartă `sursa_id`, deci se poate reconstrui o bază fără oricare dintre surse (`construieste_baza.py --fara hunspell`).
  Dacă baza se redistribuie, părțile derivate din RRT, RoWN și Wiktionary rămân sub CC BY-SA 4.0, iar cele
  derivate din Hunspell sub GPL 2.0 / LGPL 2.1 / MPL 1.1 (la alegere). Deocamdată baza NU se redistribuie
  (nu intră în Git).
- CC BY-SA 4.0 este compatibilă într-un singur sens cu GPLv3 (nu cu GPLv2). Nu amestecăm într-un singur fișier
  date din Hunspell cu date din sursele CC BY-SA: tabelele păstrează sursa pe fiecare rând, iar exportul
  (`exporta`) poate scrie câte un fișier pe sursă.

## Surse verificate și neutilizate

| Sursa | Motiv |
|---|---|
| pachetul Python `rowordnet` (PyPI / GitHub dumitrescustefan/RoWordNet) | licența datelor din pachet nu e declarată (codul: MIT în `LICENSE`, GPLv3 în `setup.py`); am folosit în schimb fișierul oficial RACAI, cu licență clară. Depozitul clonat a fost șters. |
| dexonline (`dex-database.sql.gz`, 382 MB) | regula lui Adrian: fără definiții din dexonline/DEX; licența bazei (GPL 2) ar fi impus GPL întregii baze derivate. Neutilizat. |
| tezaurul `th_ro_RO_v2.dat` din pachetul rospell | proveniența conținutului (sinonime cu etichete de registru) nu e documentată; neutilizat. |
| `hyph_ro_RO.dic` (despărțirea în silabe, rospell) | nu e necesar motorului; neutilizat. |
| UD_Romanian-Nonstandard, UD_Romanian-SiMoNERo (CC BY-SA 4.0) | neimportate încă (româna veche, respectiv texte medicale); importatorul CoNLL-U le poate citi fără modificări. |
