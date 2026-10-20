# S2: motorul de română, adus în `main`, a măsurat datele de conversație — mai ales alarme false

*Scris de Claude Code (executantul, de mână) pe 20 octombrie 2026, la 11:20. Sarcina S2 din `plan/coada.md`, aprobată
de Adrian pe 19 octombrie, la 19:45. Doar am măsurat: n-am șters și n-am schimbat nimic în date.*

## Pe scurt

- **Pașii 1–3 sunt făcuți:** merge, testele care se sar fără bază, descărcarea și baza.
- **Pasul 4, măsurarea:**
  - **„răspuns din text”:** 88,8% din perechi au cel puțin o semnalare. Fără cuvintele necunoscute rămân **3.642 din
    19.618 (18,6%)**.
  - **perechile vechi:** **571 din 8.587 (6,6%)** fără cuvintele necunoscute.
- **Dar cele mai multe semnalări sunt alarme false.**
  - Cuvintele „necunoscute” sunt aproape toate nume proprii străine (Schocken, Innsbruck, Disney).
  - Din cele 20 de semnalări de gramatică alese la întâmplare, eu cred că doar **2** sunt greșeli adevărate.
- **Concluzia mea:** motorul, așa cum e acum, **nu e bun ca filtru** pe datele astea. Ar scoate mai ales texte bune.
  Pasul 5 (filtrul) rămâne oricum la hotărârea ta.

## Pașii

1. **Merge-ul ramurii `limba-romana` în `main`** (commit `665c44e`).
   - Au intrat 52 de fișiere, toate în `module/limba_romana/`, plus cele 2 rapoarte ale ei din `docs/rapoarte/`.
   - Am verificat înainte de commit: **nimic din `kronos/`** și nimic din afara modulului.
2. **Testele motorului se sar fără bază.**
   - Ramura le avea deja: cele 35 care cer baza completă trec prin fixtura `motor_complet`, care face `pytest.skip`
     când baza lipsește.
   - Nu intrau însă în `python -m pytest`. Am adăugat `module/limba_romana/teste` la `testpaths` în
     `pyproject.toml`, ca să ruleze mereu.
   - **Fără bază:** 769 trecute, 36 sărite. **Cu baza:** 806 trecute, 1 sărit (cel vechi, care se sărea și înainte).
3. **Descărcarea și baza:**
   - `python -m module.limba_romana.importatoare.descarca_surse` a descărcat **366 MB**: Hunspell ro_RO, UD Romanian
     RRT, RoWordNet 3.0 și Wiktionary prin kaikki.org.
   - Fiecare fișier are amprenta sha256 la fel ca în `LICENTE.md`; manifestul a ieșit „fără probleme”.
   - `construieste_baza --proaspat` a făcut `_baza/limba_romana.sqlite` (**1,1 GB**), cu verificarea „integritate OK”.
   - Sursele și baza nu intră în Git (`module/limba_romana/.gitignore`).
4. **Măsurarea, cu unealta nouă `unelte/masoara_romana.py`** (cu teste noi în `teste/test_masoara_romana.py`):
   - trece prin `Motor().verifica_text` textul din față și răspunsul fiecărei perechi;
   - textele care se repetă le verifică o singură dată;
   - perechile în engleză nu le măsoară (motorul e doar pentru română), dar le numără;
   - a durat 2 minute, pe procesor.

## Cifrele

| | „răspuns din text” (19.668) | vechi (13.446) |
|---|---|---|
| perechi în română măsurate | 19.618 (50 în engleză) | 8.587 (4.859 în engleză) |
| cu cel puțin o semnalare | 17.429 (88,8%) | 5.493 (64,0%) |
| **cu cel puțin o semnalare, fără necunoscute** | **3.642 (18,6%)** | **571 (6,6%)** |
| necunoscute | 16.984 | 5.286 |
| acord | 1.359 | 289 |
| diacritice | 1.173 | 218 |
| numeral cu „de” | 1.163 | 42 |
| al/a | 227 | 41 |
| certitudine „sigură” | 5.833 | 1.197 |
| certitudine „probabilă” | 1.978 | 367 |
| certitudine „posibilă” | 16.552 | 5.039 |

Pe grupe și pe certitudine se numără perechile, nu semnalările: o pereche cu două feluri de probleme intră la amândouă.
Toate cifrele și exemplele: `lucru/masoara_romana/rezultat.json`.

## Ce am văzut în exemple (părerea mea; supraveghetorul le numără)

- **Cele 30 alese dintre toate:** 24 sunt nume proprii sau cuvinte străine luate drept necunoscute (Schocken, Panther,
  Disney, LGBTQ). Doar unul e o problemă adevărată: „rîul” (ortografia veche, azi „râul”). Celelalte sunt alarme
  false de gramatică sau cuvinte reale lipsă din bază („maronită”, „ministru-șef”).
- **Cele 20 alese doar dintre gramatică:** cred că doar 2 sunt greșeli adevărate:
  - **#17:** „una dintre cele mai importante figuri **al** literaturii” → „ale” (corect semnalat);
  - **#19:** „Magurele” → „Măgurele”.
- **Restul sunt alarme false.** Felurile care se repetă:
  - **anul luat drept numeral:** „din 1924 scris de” → „1924 de scris”;
  - **adverbul luat drept adjectiv:** „justifica economic exploatarea”, „înființată oficial”;
  - **nume proprii „corectate”:** Lesnic → Leșnic, Split → șplit, Margarita → mărgărita, S.A. → ș.a.;
  - **construcții corecte luate drept greșite:** „unor mari sărbători”, „lăcașuri de cult clujene”, „indo-ariană”.
- **Pentru un filtru, ar trebui cel puțin:**
  - să nu se ia în seamă necunoscutele cu majusculă (nume proprii);
  - să se păstreze doar certitudinea „sigură”;
  - să se arunce felurile cu cele mai multe alarme false (numeralul lângă un an, adverbele).
  Asta e o sarcină separată, după „da”-ul tău.

## Testele

`python -m pytest`: **806 trecute, 1 sărit**, cu baza construită.

## Ce aștept de la tine

Nimic acum. Filtrul (pasul 5) nu-l pornesc. Supraveghetorul numără alarmele false din exemplele de mai jos și îți
propune ce urmează.

## Exemplele

### 30 de exemple alese la întâmplare dintre toate problemele (sămânța 1020; 15 din fiecare fișier)

| # | fișierul | câmpul | propoziția | problema | cuvintele | sugestia | certitudinea | alarmă falsă? (supraveghetor) |
|---|---|---|---|---|---|---|---|---|
| 1 | text | text | Der Jude (în traducere română Evreul) a fost o revistă lunară germană, înființată de Martin Buber și Salman Schocken, care a fost publicată din 1916 până în 1928. | ipoteza: Cuvântul „Schocken” nu e în bază ca formă; analiza e o ipoteză: majusculă inițială; nu e în bază ca nume propriu | Schocken | — | posibila | |
| 2 | text | text | 31 martie 1723 – d. 13 ianuarie/14 ianuarie 1766) a fost rege al Danemarcei și al Norvegiei din 1746, fiu al regelui Christian al VI-lea al Danemarcei și al Sofiei Magdalena de Brandenburg-Kulmbach. | ipoteza: Cuvântul „Brandenburg-Kulmbach” nu e în bază ca formă; analiza e o ipoteză: majusculă inițială; nu e în bază ca nume propriu | Brandenburg-Kulmbach | — | posibila | |
| 3 | text | raspuns | Castelul Ambras este un edificiu cultural istoric situat la sud-est de Innsbruck în apropierea comunei Amras. | ipoteza: Cuvântul „Innsbruck” nu e în bază ca formă; analiza e o ipoteză: majusculă inițială; nu e în bază ca nume propriu | Innsbruck | — | posibila | |
| 4 | text | text | Meike Schmelzer (n. | ipoteza: Cuvântul „Schmelzer” nu e în bază ca formă; analiza e o ipoteză: majusculă inițială; nu e în bază ca nume propriu | Schmelzer | — | posibila | |
| 5 | text | text | Pantera Roz contraatacă (titlu original: The Pink Panther Strikes Again) este un film american din 1976 regizat de Blake Edwards, al cincilea film din seria Pantera Roz. | ipoteza: Cuvântul „Panther” nu e în bază ca formă; analiza e o ipoteză: majusculă inițială; nu e în bază ca nume propriu | Panther | — | posibila | |
| 6 | text | text | Era văduva bancherului Hippolyte Jouberthon (cu care a avut un copil, Ana, în 1799), și cunoscută drept "Madame Jouberthon", când a devenit a doua soție a lui Lucien Bonaparte. | ipoteza: Cuvântul „Hippolyte” nu e în bază ca formă; analiza e o ipoteză: majusculă inițială; nu e în bază ca nume propriu | Hippolyte | — | posibila | |
| 7 | text | text | Ștefan Pete a fost membru în comisia economică, industrii și servicii precum și în comisia pentru agricultură, silvicultură și dezvoltare rurală. | acord_subiect_predicat: Predicatul „a” (persoana 3, singular) nu se acordă cu subiectul „Pete” (persoana 3, plural). | a, Pete | au | probabila | |
| 8 | text | text | Comuna se află pe valea Ialomiței și este străbătută de șoseaua națională DN71, care leagă Târgoviște de Sinaia. | ipoteza: Cuvântul „DN71” nu e în bază ca formă; analiza e o ipoteză: scris cu majuscule: siglă/abreviere | DN71 | — | posibila | |
| 9 | text | text | Se află pe Magistrala Brighton, la 42,8 km de London Bridge via Redhill. | ipoteza: Cuvântul „Redhill” nu e în bază ca formă; analiza e o ipoteză: majusculă inițială; nu e în bază ca nume propriu | Redhill | — | posibila | |
| 10 | text | text | Situat pe rîul Krka, orașul are o populație de 22.415 locuitori. | necunoscut: Cuvântul „rîul” nu e cunoscut (nu e în nicio sursă și nu se potrivește cu nicio regulă). | rîul | — | sigura | |
| 11 | text | text | A fost realizat în două versiuni, în limbile hindi și rusă, și este inspirat din jurnalul de călătorie al călătorului rus Afanasie Nikitin, intitulat Călătorie peste trei mări, care este acum considerat un monument liter | ipoteza: Cuvântul „Afanasie” nu e în bază ca formă; analiza e o ipoteză: majusculă inițială; nu e în bază ca nume propriu | Afanasie | — | posibila | |
| 12 | text | text | Hercules este un film de animație din 1997, produs de Walt Disney Feature Animation și lansat inițial de Walt Disney Pictures. | ipoteza: Cuvântul „Disney” nu e în bază ca formă; analiza e o ipoteză: majusculă inițială; nu e în bază ca nume propriu | Disney | — | posibila | |
| 13 | text | text | Mirciulică este un film românesc de comedie din 2022 scris și regizat de Cristi Ilișuan (debut regizoral) și produs de Bravo Films. | ipoteza: Cuvântul „Films” nu e în bază ca formă; analiza e o ipoteză: majusculă inițială; nu e în bază ca nume propriu | Films | — | posibila | |
| 14 | text | text | Ea a devenit celebră la sfârșitul anilor 1990, după o serie de filme care i-au pus în valoare sex appeal-ul, printre care Starship Troopers, Wild Things și The World Is Not Enough. | ipoteza: Cuvântul „Not” nu e în bază ca formă; analiza e o ipoteză: majusculă inițială; nu e în bază ca nume propriu | Not | — | posibila | |
| 15 | text | text | Are 52.000 de locuitori, fiind situat la vărsarea râului Teplá în Eger (Ohře). | ipoteza: Cuvântul „Teplá” nu e în bază ca formă; analiza e o ipoteză: majusculă inițială; nu e în bază ca nume propriu | Teplá | — | posibila | |
| 16 | vechi | raspuns | Strada Ermou este o stradă lungă de 1,5 kilometri din centrul orașului Atena, Grecia, ce face legătura între situl arheologic Kerameikos și Piața Syntagma prin Monastiraki, Psiri și Thiseio. | ipoteza: Cuvântul „Syntagma” nu e în bază ca formă; analiza e o ipoteză: majusculă inițială; nu e în bază ca nume propriu | Syntagma | — | posibila | |
| 17 | vechi | raspuns | Lucian-Ovidiu Burchel este un fost fotbalist român, care a jucat pe postul de atacant pentru echipe precum Sportul Studențesc și Inter Sibiu. | necunoscut: Cuvântul „-Ovidiu” nu e cunoscut (nu e în nicio sursă și nu se potrivește cu nicio regulă). | -Ovidiu | — | sigura | |
| 18 | vechi | raspuns | Géza Tabéry a fost un scriitor și jurnalist maghiar din România. | ipoteza: Cuvântul „Tabéry” nu e în bază ca formă; analiza e o ipoteză: majusculă inițială; nu e în bază ca nume propriu | Tabéry | — | posibila | |
| 19 | vechi | raspuns | Tokugawa Ienari a fost al unsprezecelea și cel mai longeviv shōgun al Shogunatului Tokugawa din Japonia, care a deținut funcția din 1787 până 1837. | ipoteza: Cuvântul „Ienari” nu e în bază ca formă; analiza e o ipoteză: majusculă inițială; nu e în bază ca nume propriu | Ienari | — | posibila | |
| 20 | vechi | raspuns | Catedrala Maronită Sfântul Gheorghe este o catedrală maronită, sediul arhiepiscopiei maronite din Beirut, Liban. | necunoscut: Cuvântul „maronită” nu e cunoscut (nu e în nicio sursă și nu se potrivește cu nicio regulă). | maronită | — | sigura | |
| 21 | vechi | raspuns | Catherine Élise "Cate" Blanchett este o actriță și director de teatru din Australia. | ipoteza: Cuvântul „Élise” nu e în bază ca formă; analiza e o ipoteză: majusculă inițială; nu e în bază ca nume propriu | Élise | — | posibila | |
| 22 | vechi | raspuns | Minereul uranifer este un minereu care conține uraniu în concentrații suficient de ridicate pentru a justifica economic exploatarea acestuia. | acord_subst_adj: Adjectivul „economic” (masculin singular) nu se acordă cu substantivul „exploatarea” (feminin singular). | economic, exploatarea | — | sigura | |
| 23 | vechi | raspuns | Etgar Keret este un scriitor israelian, foarte popular prin nuvelele sale, de asemenea autor de benzi desenate și scenarist de filme. | ipoteza: Cuvântul „Keret” nu e în bază ca formă; analiza e o ipoteză: majusculă inițială; nu e în bază ca nume propriu | Keret | — | posibila | |
| 24 | vechi | raspuns | Girls Aloud a fost o formație britanică formată în cadrul spectacolului de televiziune Popstars: The Rivals la finele anului 2002. | ipoteza: Cuvântul „Rivals” nu e în bază ca formă; analiza e o ipoteză: majusculă inițială; nu e în bază ca nume propriu | Rivals | — | posibila | |
| 25 | vechi | raspuns | Kevin Scott Nash este un wrestler american și un actor. | ipoteza: Cuvântul „Nash” nu e în bază ca formă; analiza e o ipoteză: majusculă inițială; nu e în bază ca nume propriu | Nash | — | posibila | |
| 26 | vechi | raspuns | Sînziana Bucura Nicola este actriță, scenaristă și regizoare română. | ipoteza: Cuvântul „Sînziana” nu e în bază ca formă; analiza e o ipoteză: majusculă inițială; nu e în bază ca nume propriu | Sînziana | — | posibila | |
| 27 | vechi | raspuns | Marco Minghetti a fost un economist și un politician italian. | ipoteza: Cuvântul „Minghetti” nu e în bază ca formă; analiza e o ipoteză: majusculă inițială; nu e în bază ca nume propriu | Minghetti | — | posibila | |
| 28 | vechi | raspuns | Mazarinetele au fost cele șapte nepoate ale cardinalului Jules Mazarin,, ministru-șef al regilor Ludovic al XIII-lea și Ludovic al XIV-lea ai Franței din 1642 până la moartea sa. | necunoscut: Cuvântul „ministru-șef” nu e cunoscut (nu e în nicio sursă și nu se potrivește cu nicio regulă). | ministru-șef | — | sigura | |
| 29 | vechi | raspuns | Andreas Weimann este un fotbalist profesionist austriac care joacă pe postul de atacant sau de extrema pentru Bristol City și echipa națională a Austriei. | ipoteza: Cuvântul „Weimann” nu e în bază ca formă; analiza e o ipoteză: majusculă inițială; nu e în bază ca nume propriu | Weimann | — | posibila | |
| 30 | vechi | raspuns | Cluj Pride este un festival dedicat promovării drepturilor LGBTQ+ și sporirii vizibilității comunității LGBT din Transilvania. | ipoteza: Cuvântul „LGBTQ” nu e în bază ca formă; analiza e o ipoteză: scris cu majuscule: siglă/abreviere | LGBTQ | — | posibila | |

### Încă 20, alese doar dintre problemele de gramatică (fără necunoscute; sămânța 1020; 10 din fiecare fișier)

| # | fișierul | câmpul | propoziția | problema | cuvintele | sugestia | certitudinea | alarmă falsă? (supraveghetor) |
|---|---|---|---|---|---|---|---|---|
| 1 | text | text | Rolurile principale au fost interpretate de actorii Mircea Silaghi, Cecilia Bârbora, Cosmina Păsărin. | ortografie: „Bârbora” pare scris fără diacritice: „barboră”. | Bârbora | barboră | probabila | |
| 2 | text | text | Este al doilea oraș ca populație (după Kaliningrad) al regiunii respective, cu 41,2 mii loc. | numeral_de: De la 20 în sus numeralul se leagă de substantiv prin „de”: „mii de loc”. | mii, loc | mii de loc | sigura | |
| 3 | text | raspuns | Irîna Bekeșkina a fost o sociologă ucraineană. | ortografie: „Irîna” pare scris fără diacritice: „Irina”. | Irîna | Irina | probabila | |
| 4 | text | text | Corabia zeiței Ishtar este un roman SF&F din 1924 scris de Abraham Merritt și publicat în foileton în revista Argosy. | numeral_de: De la 20 în sus numeralul se leagă de substantiv prin „de”: „1924 de scris”. | 1924, scris | 1924 de scris | sigura | |
| 5 | text | text | A înlocuit-o pe Cristina Lesnic, după ce Partidul Democrat din Moldova și-a retras miniștrii delegați din guvernul Ion Chicu. | ortografie: „Lesnic” pare scris fără diacritice: „Leșnic”. | Lesnic | Leșnic | probabila | |
| 6 | text | raspuns | Infanta Margarita Teresa în rochie roz este o pictură realizată în ulei pe pânză de către artistul spaniol Diego Velázquez în 1660, deși identificarea autorului nu este sigură. | ortografie: „Margarita” pare scris fără diacritice: „mărgărita”. | Margarita | mărgărita | probabila | |
| 7 | text | text | 11 septembrie 1968, Split) este un fost fotbalist croat, și actual antrenor care în prezent se află liber după despărțirea de West Ham. | ortografie: „Split” pare scris fără diacritice: „șplit”. | Split | șplit | probabila | |
| 8 | text | text | Este primul roman scris de Gala Galaction după ce în 1918 a publicat în revista Cartea vremii primele cinci capitole ale romanului său neterminat Margo. | acord_subst_det: Determinantul „său” (masculin singular) nu se acordă cu substantivul „Margo” (feminin singular). | său, Margo | — | sigura | |
| 9 | text | raspuns | Dupăprăznuirea sau prăznuirea prelungită este o perioadă de timp ce urmează unor mari sărbători ale anului bisericesc creștin. | acord_subst_det: Determinantul „unor” (plural) nu se acordă cu substantivul „sărbători” (feminin singular). | unor, sărbători | unei | sigura | |
| 10 | text | raspuns | Iagorlîc este o rezervație științifică din partea central-estică a Republicii Moldova, situată la gura râului Iagorlîc, pe malul stâng al Nistrului. | acord_subst_adj: Adjectivul „central” (masculin singular) nu se acordă cu substantivul „partea” (feminin singular). | central, partea | — | probabila | |
| 11 | vechi | raspuns | Vadul lui Vodă este un oraș din sectorul Ciocana, municipiul Chișinău, Republica Moldova. | ortografie: „Ciocana” pare scris fără diacritice: „ciocană”. | Ciocana | ciocană | probabila | |
| 12 | vechi | raspuns | One United Properties S.A. este o companie românească, specializată în dezvoltări imobiliare, fondată în 2007 de Andrei Diaconescu și Victor Căpitanu, care au pus bazele casei de investiții Capital Partners. | ortografie: „S.A.” pare scris fără diacritice: „ș.a.”. | S.A. | ș.a. | probabila | |
| 13 | vechi | raspuns | Colegiul Național „Cantemir Vodă” este o instituție de învățământ liceal înființată oficial la data de 27 octombrie 1868. | acord_subst_adj: Adjectivul „oficial” (masculin singular) nu se acordă cu substantivul „înființată” (feminin singular). | oficial, înființată | — | probabila | |
| 14 | vechi | raspuns | Marathi este o limbă indo-ariană vorbită de populația Marathi, care este grupată în vestul peninsulei India. | acord_subiect_predicat: Predicatul „indo” (persoana 3, plural) nu se acordă cu subiectul „limbă” (persoana 3, singular). | indo, limbă | îndoaie | probabila | |
| 15 | vechi | raspuns | Mănăstirea Dornelor este o mănăstire ortodoxă de călugări, pe stil vechi, situată într-o pădure din satul Neagra Șarului, comuna Șaru Dornei. | ortografie: „Șaru” pare scris fără diacritice: „Saru”. | Șaru | Saru | probabila | |
| 16 | vechi | raspuns | Jelly Jamm este un serial animat 3D generat de computer pentru copiii de 4-7 ani produs de Vodka și 737SHAKER CAPITAL, două companii spaniole din Madrid și Segovia. | numeral_de: De la 20 în sus numeralul se leagă de substantiv prin „de”: „737 de SHAKER”. | 737, SHAKER | 737 de SHAKER | sigura | |
| 17 | vechi | raspuns | William Butler Yeats a fost un poet și dramaturg irlandez, una dintre cele mai importante figuri al literaturii secolului XX, laureat al Premiului Nobel pentru Literatură în 1923. | acord_al: „al” nu se acordă cu „figuri” (feminin plural); al/a/ai/ale se acordă cu obiectul posedat. | al, figuri | ale | sigura | |
| 18 | vechi | raspuns | B.D. la munte și la mare este un film de comedie românesc din 1971, regizat de Mircea Drăgan. | acord_subst_adj: Adjectivul „românesc” (masculin singular) nu se acordă cu substantivul „comedie” (feminin singular). | românesc, comedie | — | sigura | |
| 19 | vechi | raspuns | Radioactiv Mineral Magurele este o companie de stat din România care din anul 2004 deține activitățile geologice pentru uraniu. | ortografie: „Magurele” pare scris fără diacritice: „Măgurele”. | Magurele | Măgurele | probabila | |
| 20 | vechi | raspuns | Biserica Franciscană din Cluj-Napoca este unul din cele mai vechi și mai semnificative lăcașuri de cult clujene, situat în actuala Piața Muzeului nr. 2. | acord_subst_adj: Adjectivul „clujene” (feminin plural) nu se acordă cu substantivul „cult” (masculin singular). | clujene, cult | clujean | sigura | |
