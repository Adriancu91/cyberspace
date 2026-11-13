# S108 — Câte exemple din fiecare tip de întrebare a văzut linia lui #513 și câte s-ar putea face din datele deja descărcate

*Scris de executant (Claude Code) pe 13 noiembrie 2026, 08:14. Sarcina S108 din `plan/coada.md`, aprobată de supraveghetor
(13 nov 02:15; granița 2: analize, granița 3: doar citire pe date deja descărcate). Doar procesor, doar citire. Nimic
antrenat, nimic scris ca date de antrenare, niciun generator schimbat, nimic descărcat sau șters, nimic pe placă.*

## Pe scurt

- **Linia modelului în uz (#513) n-a văzut aproape deloc tipurile de întrebări la care greșește.** Din cele 13 tipuri (b2) ale
  examenului S15, 11 au **0 exemple** în toate cele patru fișiere de antrenare ale liniei. Singurele excepții: „țară” (223 de
  instrucțiuni „Spune în ce județ se află X și din ce țară face parte.”, doar România / Republica Moldova) și „oraș” (4
  întrebări „Ce oraș are X drept capitală?”).
- **Tipurile care merg (e: 29 din 30 corecte) au fost văzute de zeci–sute de ori** (de la 14 la 719 exemple pe tip). Chiar și
  „gen”, cu doar 14 exemple, are 3 din 3 corecte.
- **Din Wikipedia RO deja descărcată s-ar putea face, după o estimare, ~6.000 de întrebări noi** pe texte nefolosite încă
  (~11.000 dacă se folosesc și textele deja văzute, cu întrebări noi). Dar foarte inegal: „profesie” ~2.900, „țară” ~1.200,
  „funcție” ~600, „actori” ~500 — și doar ~30 la „pictor” și „câștigător”, ~50 la „soț”.
- **Varianta (b) în cifre:** un generator nou (cod, pe procesor), apoi o rulare scurtă de **2–3 ore pe placă** din #513 (plus
  ~20 min examene). **Varianta (a)** (S101): ~7 nopți întregi pe placă, de la zero.
- Testele: 1412 trec, 1 sărit, înainte și după.

## Ce am făcut

0. `python -m pytest`: **1412 trec, 1 sărit** (6 min 40 s), înainte de orice.
1. **Fișierele de antrenare ale liniei**, luate din jurnalul Kronos (cheia `conversatie` din fișele modelelor), nu ghicite:

   | modelele | fișierul de conversație („răspuns din text”) | perechi | SHA-256 |
   |---|---|---|---|
   | #401 (noaptea 10) | `date/conversatie/text/antrenare.jsonl` | 19.668 | `391dbea4…5c65` |
   | #407 (noaptea 11) | `date/conversatie/text_v2/antrenare.jsonl` | 24.149 | `8c47defb…0302` |
   | #415, #441, #459, #477 | `date/conversatie/text_v3/antrenare.jsonl` | 27.468 | `59eeb057…9c63` |
   | **#513** (S76b) | `lucru/romana_raspunsuri/antrenare.jsonl` | 23.251 | `3d8ac5a3…00b0` |

   Lanțul: #385 → #401 → #407 → #415 → #441 → #459 → #477 → #513. Toate patru fișierele au câmpul `tip`.
2. **Tipurile (b2)** nu sunt scrise în fișierele de antrenare (au fost făcute de mână la S15, tocmai ca să nu existe în
   antrenare). Le-am numărat cu **o regulă pe forma întrebării** pentru fiecare tip (de ex. „țară” = „ce țară” / „și țara”;
   „profesie” = „profesie / meserie / ocupație / cu ce se ocupa”), cu literă mică, ca titlurile („Actorul și sălbaticii”,
   „Producătorii”) să nu conteze. **Verificare:** regulile prind 50 din 50 de întrebări (b2) din S15, fiecare doar la tipul ei,
   și 0 din cele 30 (e). Regulile întregi sunt în `lucru/cascada/S108/numara.py`.
   **Tipurile (e)** sunt scrise în fișiere (`nou_familie` etc.; în fișierul S76a unele apar și fără „nou_”, le-am adunat).
3. **Datele posibile:** am trecut prin toată Wikipedia RO descărcată, aceeași sursă ca generatorul
   (`date/ws/curat/wikipedia_ro/antrenare.txt`, 277.357 articole, SHA `e27c66ba…0353`), cu **aceleași filtre de text ca
   generatorul** `unelte/conversatie_text.py` (funcțiile lui `pereche_din`, `text_din`, 150–700 litere, începutul curat, fără
   alte alfabete, fără subiect repetat, fără bucăți din validări, fără cuvinte necunoscute). Generatorul nu știe tipurile (b2),
   deci n-am scris generator nou: am numărat doar **câte texte au informația**, cu câte o regulă pe text pentru fiecare tip
   (estimare).
4. **Excluderea examenelor:** pe lângă regula generatorului (validările), am scos orice text care are **o bucată de 8 cuvinte
   la rând** din: S15 (`examen_generalizare_mare.json`), S4 (`examen_generalizare_401.json`), examenele `text*/examen.json`,
   setul ascuns S76a (și cel reformulat) și examenul neutru (`date/neutru/*/validare.txt`, toate cinci) — plus orice text
   identic cu unul din S15. Așa au ieșit **4.092** texte (mai mult decât ar fi strict nevoie: probabil multe au doar formule
   comune ca „este o comună în raionul …”; am preferat să scot prea mult decât prea puțin) și încă 226 după regula
   generatorului.
5. Prima trecere a avut reguli prea largi (de ex. „Limba română” la „țară”, „Calea Griviței și Șoseaua…” la „actori”). Le-am
   strâns — doar am **scos** variante, nu le-am potrivit după examen — și am refăcut trecerea (`numara_v2.json`; prima e
   păstrată în `numara.json`). Fiecare trecere: ~1 minut, un singur nucleu.
6. Pentru fiecare tip, **10 texte alese la întâmplare** (`random.Random(108)`) dintre cele găsite, citite de mine: câte au
   într-adevăr răspunsul. Asta e o judecată de mână, doar ca să se vadă cât de bună e estimarea.

## Cifrele

### Tabelul cerut: tipurile (b2) — slabe la #513

„La antrenare” = întrebări de acel tip în toată linia (unice, toate cele 4 fișiere). „Texte cu informația” = din Wikipedia
descărcată, după filtre și excluderi: **noi** = texte nefolosite încă la antrenare / **deja** = texte deja folosite (cu alte
întrebări). „Mostra” = din 10 texte citite, câte au cu adevărat răspunsul. „Estimat” = noi × mostra/10.

| tipul | întrebări S15 | la antrenare | corecte S106 #513 | texte noi / deja | mostra | **estimat (noi)** | regula prinde textele S15 |
|---|---|---|---|---|---|---|---|
| actori | 5 | 0 | 0 | 660 / 803 | 8/10 | **~530** | 5/5 |
| canal | 4 | 0 | 0 | 146 / 87 | 10/10 | **~150** | 3/4 |
| câștigător | 2 | 0 | 0 | 43 / 30 | 7/10 | **~30** | 0/2 |
| funcție | 6 | 0 | 2 | 740 / 624 | 8/10 | **~590** | 6/6 |
| oraș | 5 | 4 (doar „Ce oraș are X drept capitală?”) | 1 | 248 / 200 | 7/10 | **~170** | 2/5 |
| personaj | 2 | 0 | 1 | 112 / 68 | 6/10 | **~70** | 2/2 |
| pictor | 3 | 0 | 2 | 37 / 20 | 8/10 | **~30** | 2/3 |
| premiu | 3 | 0 | 1 | 134 / 132 | 9/10 | **~120** | 0/3 |
| producător | 3 | 0 | 0 | 368 / 237 | 8/10 | **~290** | 3/3 |
| profesie | 6 | 0 | 0 | 2.898 / 2.410 | 10/10 | **~2.900** | 6/6 |
| soț | 1 | 0 | 0 | 93 / 58 | 5/10 | **~50** | 1/1 |
| țară | 5 | 223 (instrucțiuni S76a, doar România / R. Moldova, împreună cu județul) | 1 | 1.748 / 1.169 | 7/10 | **~1.220** | 3/5 |
| **total** | 45 | | **8 din 45** | 7.227 / 5.838 | | **~6.150** | |

(„post”, 3 din 5 corecte, nu intră — sarcina cere doar tipurile cu 0–2 corecte. Și el are 0 exemple la antrenare.)

De citit cu grijă:
- La „țară”, 408 din textele noi sunt despre România, 1.340 despre alte țări.
- „Câștigător” și „premiu”: regula mea nu prinde nici unul din textele S15 de acest tip (0/2, 0/3) — scriu altfel acolo
  („a câștigat Paris-Roubaix…”) → la aceste două tipuri cifra e probabil **mai mică decât** ce există de fapt.
- Cifrele sunt texte, nu întrebări gata: un generator ar mai pierde o parte (răspunsul trebuie să iasă curat din text).

### Tipurile (e) — văzute la antrenare (29 din 30 corecte la #513)

| tipul (e) | exemple în linie (unice) | text_v3 cu răspuns / da-nu / „Nu scrie” | S76a cu răspuns / da-nu / „Nu scrie” | corecte S106 #513 |
|---|---|---|---|---|
| familie | 670 | 360 / 61 / 45 | 164 / 36 / 24 | 5/5 |
| descris (cine) | 657 | 237 / 58 / 135 | 154 / 15 / 80 | 4/4 |
| descris (an) | 171 | 115 / 22 / 0 | 34 / 2 / 0 | 3/3 |
| gen | **14** | 8 / 4 / 0 | 1 / 1 / 0 | 3/3 |
| raion | 682 | 356 / 83 / 41 | 163 / 43 / 14 | 5/5 |
| afluent | 90 | 51 / 13 / 3 | 17 / 6 / 3 | 1/1 |
| legislatură | 358 | 248 / 58 / 20 | 24 / 7 / 6 | 3/3 |
| partid | 423 | 283 / 72 / 30 | 30 / 3 / 9 | 3/3 |
| bazin | **3** | 2 / 0 / 0 | 1 / 0 / 0 | **0/1** |
| construit (an) | 144 | 59 / 17 / 1 | 58 / 11 / 1 | 1/1 |
| fondat (an) | 719 | 319 / 85 / 16 | 283 / 35 / 12 | 1/1 |

**Ce se vede:** un tip văzut la antrenare, chiar și de puține ori (gen: 14), merge pe texte noi; cu 3 exemple (bazin) nu.
Tipurile nevăzute (b2) merg doar când întrebarea seamănă cu ceva știut (de ex. „pictor”: „Cine a pictat X?” e aproape de „Cine a
regizat X?”). **Atenție la comparație:** întrebările (e) din S15 au formulările de la antrenare; la un tip nou, modelul ar
trebui să învețe și formulări diferite.

## Ce înseamnă (a) și (b), în cifre (pentru Adrian)

**(a) S101 — modelul de 24 de straturi, de la zero:** cam **7 nopți întregi pe placă** (~80 de ore). Ce știm deja: modelul de 24
de straturi crescut din #513 (#554) a ieșit **la fel** cu #513 pe toate cele patru măsurători (S105, S106), inclusiv la
tipurile nevăzute (13 față de 11 din 50). Un model mai mare nu a reparat tipurile nevăzute.

**(b) Mai multe tipuri de întrebări pe modelul în uz:** din Wikipedia pe care o avem deja, ~6.000 de întrebări noi pentru cele 12
tipuri slabe (fără nicio descărcare). Ar cere: (1) un generator nou pentru aceste tipuri (cod, pe procesor, cu formulări diferite
și cu „Nu scrie în text.”), (2) **un examen nou, nevăzut**, cu alte tipuri decât acestea — pentru că după (b) tipurile din S15
(b2) nu mai sunt „nevăzute”, iar întrebarea „învață modelul tipuri noi singur?” trebuie măsurată pe altele, (3) **o rulare de
2–3 ore pe placă** din #513 (ca S76b, care a durat 5 ore), apoi ~20 de minute de examene.
Socoteala pentru (3): la S76b placa a văzut ~124.000 de perechi de conversație pe oră (115.026 de pași în 5 ore, lot 12, 45 %
conversație). Cu cele ~6.000 noi plus cele 23.251 vechi (ca să nu uite), ~29.000 de perechi: în 2 ore fiecare pereche e văzută
de ~8–9 ori, în 3 ore de ~13 ori (la S76b: ~27 de ori în 5 ore). **Doar estimare; nu o propun ca sarcină aprobată.**
La 4 tipuri (pictor, câștigător, soț, personaj) ar fi doar 30–70 de exemple — la „gen” 14 au ajuns, dar fără garanție.

## Testele

`CUDA_VISIBLE_DEVICES=-1 python -m pytest`: înainte **1412 trec, 1 sărit**; după: **1412 trec, 1 sărit** (6 min 40 s, ambele).

## Modelele #513 și #554 există încă (adaosul supraveghetorului, 08:15; doar citire)

| model | fișierul | mărime | SHA-256 |
|---|---|---|---|
| #513 | `lucru/stocare/modele/experiment_513.pt` | 392.400.973 B | `605c4084f0a5db125b1e6c2c037b8e3d96abd17c1d62ec76efe439ecaba58b2c` (= cel din S106 ✓) |
| #513 | `lucru/w2_romana_r1/gpt.pt` (starea liniei) | 1.176.555.593 B | `b9214d729b1b2f1996e077facdbe82e1d0eb6b99e996ee58d8899d80a61acda3` |
| #554 | `lucru/stocare/modele/experiment_554.pt` | 732.670.301 B | `6a6d97d0a6808be56e23c4ef8a940da397b3d04cda85727460a6d379aa2923fd` (= cel din S106 ✓) |
| #554 | `lucru/w2_mare_24s/gpt.pt` (starea liniei) | 2.197.380.401 B | `ee39471fade93c5c019f360cfad1dca7506cb9bb17ae893c67b67b0b0c194e5e` |

Testul `test_kronos_cod_examen` (picat o dată în raportul de dimineață) a trecut în ambele rulări complete de azi (08:00 și
08:30). N-am reparat nimic.

## Fișierele

- Scripturile și rezultatele, doar în `lucru/cascada/S108/` (nu sunt în Git): `numara.py` (unealta de numărat, doar citire),
  `numara.json` (prima trecere, reguli largi), **`numara_v2.json`** (cifrele din raport, cu mostrele de 10),
  `partea1_proba.json`, `rezumat1.py`, `rezumat2.py`, `priveste.py`, `tipuri.py`, `lant.py`, jurnalele `*.log`.
- N-am atins: `kronos/`, `module/`, generatoarele, configurările, examenele, jurnalul, modelele. Nimic scris în `date/`.

## Ce aștept de la Adrian

Doar alegerea direcției, când ai timp: **(a)** modelul de 24 de straturi de la zero (~7 nopți) sau **(b)** tipuri noi de întrebări
pe modelul în uz (generator + examen nou + 2–3 ore de placă). Cifrele de mai sus sunt pentru alegerea asta; nimic nu pornește
fără „da”-ul tău.
