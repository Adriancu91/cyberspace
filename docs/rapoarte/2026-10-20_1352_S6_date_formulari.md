# S6 — Datele pentru noaptea 11: aceleași întrebări, formulate în mai multe feluri, plus da/nu

*Scris la 2026-10-20 13:52 de Claude Code (executantul din cascadă). Sarcina S6 din `plan/coada.md`, aprobată de
supraveghetor pe 20 octombrie, 11:20. Pornită la 13:28, gata la 13:52. Totul pe procesor; placa n-a fost folosită.*

## Pe scurt

- Datele noi sunt în `date/conversatie/text_v2/` (nu intră în Git): **24.149 de perechi** (noaptea 10: 19.668), din
  aceleași 16.000 de articole, cu aceleași răspunsuri, dar întrebările sunt spuse în **5–6 feluri** pe șablon, plus
  **3.585 de perechi da/nu** (1.793 „Da.”, 1.792 „Nu.”).
- **Verificarea 3.(ii): 0** întrebări de antrenare care încep cu primele 4 cuvinte ale unei întrebări din S4.
  **Verificarea 3.(iii): 0** texte din examenul nopții 10 sau din S4 în antrenare.
- Datele nopții 10 nu s-au atins: fără `--formulari`, unealta le scoate din nou **byte cu byte la fel** (verificat).
- `config/conv_w2_text_v2.toml` e gata; pre-înregistrarea S7 e scrisă:
  `docs/preinregistrari/2026-10-20_noaptea11_formulari.md`.
- **Testele: 813 trec, 1 sărit** (înainte: 809; 4 teste noi).
- **O abatere de semnalat** (detalii mai jos): ca verificarea (ii) să dea 0, cu `--formulari` au ieșit și trei formulări
  vechi din noaptea 10 („În ce an a murit / a apărut / a fost atestat documentar X?”), pentru că încep la fel ca „În
  ce an a venit pe lume X?” din S4.

**S7 așteaptă acum „perechi verificate: da” de la supraveghetor** (în coadă, la S7).

## Ce am făcut, pe pași (după „ce faci” din S6)

1. **`--formulari` și `--dosar`** în `unelte/conversatie_text.py` (`--dosar` exista deja, implicit
   `date/conversatie/text`). `--formulari` e implicit oprită. Formulările și da/nu folosesc o întâmplare separată
   (sămânța 1019 + 1 = 1020), deci alegerea articolelor și examenul rămân exact ca în noaptea 10.
   Formulările pe șablon (lista întreagă e în `FORMULARI`, în unealtă):

   | șablon | câte | exemple |
   |---|---|---|
   | născut | 6 | „În ce an s-a născut X?”, „Când s-a născut X?”, „Care e anul nașterii lui X?”, „Ce an de naștere are X?”, „X s-a născut în ce an?”, „În ce an e născut X?” |
   | murit | 5 | „În ce an moare X?”, „Când a murit X?”, „Care e anul morții lui X?”, „Când a decedat X?”, „X a murit în ce an?” |
   | locuitori | 6 | „Câți locuitori are X?”, „Câte persoane locuiesc în X?”, „Câți locuitori sunt în X?”, „Câți locuitori numără X?”, „Câtă lume locuiește în X?”, „X câți locuitori are?” |
   | județ / comună / regiune | 5 fiecare | „În ce județ se află X?”, „În ce județ este X?”, „X se află în ce județ?”, „În ce județ se găsește X?”, „În ce județ e X?” |
   | regizat | 5 | „Cine a regizat X?”, „Cine e regizorul lui X?”, „Sub ce regie e X?”, „Cine a făcut regia pentru X?”, „Cine semnează regia lui X?” |
   | scris | 5 | „Cine a scris X?”, „Cine semnează X?”, „Cine e cel care a scris X?”, „Cine a fost cel care a scris X?”, „Cine a pus pe hârtie X?” |
   | an (operă) | 6 | „Din ce an este X?”, „Din ce an e X?”, „Când a apărut X?” (→ „În 1952.”), „Ce an de apariție are X?”, „Care e anul apariției lui X?”, „X e din ce an?” |
   | fondat, dezvoltat, distanță, capitală, suprafață | 5 fiecare | „Cine a înființat X?”, „Cine e dezvoltatorul lui X?”, „La câți kilometri de Y se află X?”, „Unde își are capitala X?”, „Ce întindere are X?” |
   | „Nu scrie”: unde a murit, părinți, altitudine, atestat | 5 fiecare | „În ce localitate a murit X?”, „Cum se numeau părinții lui X?”, „La ce înălțime se află X?”, „Când apare X prima dată în documente?” |

   „Ce este X?” / „Cine este X?” / „Unde se află X?” (definițiile, 7.767) au rămas neschimbate: S6 dă exemple doar
   pentru celelalte șabloane, iar jumătate din examenul nopții 10 sunt definiții.
   La „Nu scrie în text.” despre același subiect se folosesc aceleași formulări (de exemplu „Cine a regizat X?” la un
   film fără regizor în text apare și ca „Sub ce regie e X?”).
2. **Da/nu** (`DA_NU`, `da_nu_pentru`): cam 15% din perechile cu text, doar pe șabloanele an (născut, murit, operă),
   locuitori, județ, comună, regizat, scris; câte una pe articol, cel mult. „Da.” cu valoarea din text; „Nu.” cu alt
   an (±1–30), alt număr de locuitori sau alt nume de același fel (al altui articol), **niciodată unul care apare în
   text**. 3 forme pe șablon (de exemplu „S-a născut X în 1966?”, „X s-a născut în 1966?”, „E adevărat că X s-a născut
   în 1966?”). Răspunsul e doar „Da.” sau „Nu.”.
3. **Ce e interzis** (ca S4 să rămână cinstit):
   - (i) **niciun tip nou** de întrebare: nicio țară, meserie, trupă, club, loc al nașterii, nume științific;
   - (ii) **verificat automat** (în unealtă, `verificari`, rezultatul e în `date/conversatie/text_v2/info.json`):
     întrebări de antrenare care încep cu primele 4 cuvinte ale unei întrebări din S4: **0**. Întrebări identice cu
     cele din S4: **0**;
   - (iii) texte din examenul nopții 10 sau din S4 în antrenare: **0**. Toate cele 60 de texte din S4 sunt din
     examenul nopții 10, iar articolele puse deoparte pentru examen (280) sunt exact cele din noaptea 10.
4. **Rularea:** `python unelte/conversatie_text.py --articole 16000 --formulari --dosar date/conversatie/text_v2`,
   cod 0, câteva minute pe procesor. `date/conversatie/text/` nu s-a suprascris.
5. **Teste noi** în `teste/test_conversatie_text.py` (4): fără `--formulari` perechile sunt ca înainte; cu
   `--formulari` sunt cel puțin 4 formulări la „născut”, ~15% da/nu jumătate-jumătate, „Da.” doar când anul e în text,
   ~20% „Nu scrie”, „Din”→„În” la „Când a apărut”; valoarea schimbată la „Nu.” nu apare în text; nicio formulare nu
   începe ca o întrebare din S4.
6. **`config/conv_w2_text_v2.toml`**: copie a lui `config/conv_w2_text.toml`; diferă doar `conversatie =
   "date/conversatie/text_v2/antrenare.jsonl"` și `cale_stare = "lucru/w2_conv_text_v2/gpt.pt"` (verificat cu diff).
   Linia rămâne `w2_conv_text`.
7. **Pre-înregistrarea S7**: `docs/preinregistrari/2026-10-20_noaptea11_formulari.md`, cu pragurile copiate exact din
   S7 și așteptările mele în cifre (S4 (a) 9–12 din 15, (b) 3–6, „Nu scrie” pe nedrept 8–16 din 45; mai degrabă
   PARȚIAL decât CONFIRMAT).

## Cifrele

| | noaptea 10 (`text`) | noaptea 11 (`text_v2`) |
|---|---|---|
| articole de antrenare | 16.000 | 16.000 (aceleași) |
| perechi în total | 19.668 | **24.149** |
| cu răspunsul în text | 15.534 | 15.534 (aceleași, reformulate) |
| da/nu | — | **3.585** (1.793 Da, 1.792 Nu) = 15,0% din perechile cu text |
| „Nu scrie în text.” | 3.884 | 4.780 = 20,0% din perechile cu text |
| conversație simplă | 250 | 250 |
| cea mai lungă pereche | 300 bucăți | 300 bucăți (fereastra: 512) |
| examenul | 80 | **identic** (același fișier, byte cu byte) |

Da/nu pe șabloane: născut 1.319, murit 363, an 454, locuitori 449, regizat 427, comună 258, județ 202, scris 113.

Cum se împart formulările (exemple): la „născut” — „În ce an s-a/e născut” 773, „Ce an de naștere” 410, „Care e anul
nașterii” 410, „Când s-a născut” 399, „X s-a născut în ce an?” restul; la „regizat” — 192–208 pe fiecare din cele 5.

**Numărul de perechi:** S6 spune „cam același număr de perechi”. Am păstrat toate perechile nopții 10 și am adăugat
da/nu, iar „Nu scrie” am ținut-o la 20% din total, deci sunt cu 23% mai multe (24.149 față de 19.668). Ca să fie același
număr ar fi trebuit scoase cam 4.500 de perechi (de exemplu definiții), ceea ce ar fi schimbat și partea „Ce este X?”,
jumătate din examenul nopții 10. Noaptea are oricum 3 ore fixe, deci contează doar de câte ori trece prin fiecare pereche.

## Abaterea: trei formulări vechi au ieșit

Prima rulare a dat la verificarea (ii) **286, nu 0**: toate de la începutul „în ce an a”, din formulările vechi ale
nopții 10 „În ce an a murit X?” (176), „În ce an a apărut X?” (la „Nu scrie”, 91) și „În ce an a fost atestat
documentar X?” (19). Ele încep cu aceleași 4 cuvinte ca „În ce an a venit pe lume X?” și „În ce an a început să emită
X?” din S4. (Și datele nopții 10 ar da peste 1.300 la aceeași verificare.)

Pentru că S6 cere 0, am scos aceste trei formulări din datele noi și le-am înlocuit cu „În ce an moare X?”, respectiv
„În ce an e atestat documentar X?” (iar la „Nu scrie” pentru operă se folosesc formulările de la „an”). A doua rulare:
**0**. Riscul: examenul nopții 10 are 2 întrebări „În ce an a murit X?” și 1 „În ce an a apărut X?”, a căror formulare
exactă nu mai e în antrenare (pragul permite până la 5 greșeli din 50). L-am scris și în pre-înregistrare.

Alte lucruri de știut pentru verdictul de mâine:
- „Ce populație are X?” (sugerată în S6) e **exact** o formulare din S4 (a), așa că n-am folosit-o. „Cine e regizorul
  lui X?” (tot din S6) am folosit-o: seamănă cu „Cine este regizorul filmului X?” din S4, dar începe altfel.
- Câteva întrebări da/nu din S4 (c) au forma celor din antrenare („S-a născut X în 1966?”, „Se află X în județul
  Suceava?”), pentru că S6 cere da/nu pe șabloanele existente. (c) e oricum doar urmărit.

## 20 de perechi alese la întâmplare (sămânța 1020; primele 5 sunt da/nu)

| # | fel | textul (început) | întrebarea | răspunsul |
|---|---|---|---|---|
| 1 | da/nu locuitori | „Mueang Nakhon Sawan este un district (Amphoe) din provincia Nakhon Sawan, Thailanda, cu o populație de 238.760 de locuitori…” | Mueang Nakhon Sawan are 143.262 de locuitori? | Nu. |
| 2 | da/nu comună | „Kuti este un sat din comuna Andrijevica, Muntenegru. … are 49 de locuitori…” | Se află Kuti în comuna Andrijevica? | Da. |
| 3 | da/nu născut | „Ronald Brown (n. 7 septembrie 1921 – d. 27 iulie 2002) este un om politic britanic…” | Ronald Brown s-a născut în 1898? | Nu. |
| 4 | da/nu regizat | „Casshern (, transliterat Kyashān) este un film japonez din 2004… Este regizat de Kazuaki Kiriya…” | E adevărat că Geo Saizescu a regizat Casshern? | Nu. |
| 5 | da/nu născut | „Maricel Grădinariu (n. 17 noiembrie 1959) este un fost deputat român…” | E adevărat că Maricel Grădinariu s-a născut în 1959? | Da. |
| 6 | text locuitori | „Affligem este o comună în provincia Brabantul Flamand… avea o populație totală de 12.229 locuitori.” | Câte persoane locuiesc în Affligem? | 12.229 locuitori. |
| 7 | text definiție | „Filip Polášek (n. 21 iulie 1985) este un jucător profesionist de tenis din Slovacia, specializat în dublu…” | Cine este Filip Polášek? | Filip Polášek este un jucător profesionist de tenis din Slovacia, specializat în dublu. |
| 8 | text locuitori | „Valea Hotarului este un sat în comuna Dragoslavele din județul Argeș… Satul are cam 400 de locuitori…” | Câte persoane locuiesc în Valea Hotarului? | 400 de locuitori. |
| 9 | nu scrie (unde a murit) | „Cornel Nica (n. 2 octombrie 1956) este un fost deputat român în legislatura 1990-1992…” | În ce localitate a murit Cornel Nica? | Nu scrie în text. |
| 10 | nu scrie (alt subiect) | „Staro Selo este un sat din comuna Nikšić, Muntenegru…” | Cine a fost Beatrice de Bar? | Nu scrie în text. |
| 11 | text definiție | „Orja Luka este un sat din comuna Danilovgrad, Muntenegru…” | Unde se află Orja Luka? | Orja Luka este un sat din comuna Danilovgrad, Muntenegru. |
| 12 | text definiție | „Fester's Quest este un joc video pentru NES dezvoltat de Sunsoft în 1989…” | Ce este Fester's Quest? | Fester's Quest este un joc video pentru NES dezvoltat de Sunsoft în 1989, bazat pe celebrul serial TV Familia Addams din anii 60. |
| 13 | nu scrie (alt subiect) | „Suidele (Suidae) este o familie de mamifere ungulate…” | Ce este Caesar? | Nu scrie în text. |
| 14 | text regizat | „Pisici este un film documentar turcesc din 2016, regizat de Ceyda Torun…” | Cine semnează regia lui Pisici? | Ceyda Torun. |
| 15 | nu scrie (alt subiect) | „Austral Entomology (fostă Australian Journal of Entomology) este o peer-reviewed revistă științifică…” | Unde se află Rast? | Nu scrie în text. |
| 16 | text născut | „Ștefan Papadima (n. 7 martie 1953, București – d. 10 ianuarie 2018, București) a fost un matematician român…” | Când s-a născut Ștefan Papadima? | În 1953. |
| 17 | nu scrie (atestat) | „Mada este un sat în comuna Balșa din județul Hunedoara… Situată la 305m alt. …” | În ce an apare prima dată în documente Mada? | Nu scrie în text. |
| 18 | text locuitori | „Kaprijke este o comună neerlandofonă… avea o populație totală de 6.171 locuitori.” | Câtă lume locuiește în Kaprijke? | 6.171 locuitori. |
| 19 | text definiție | „Comedy Central Extra este un canal european de televiziune, deținut de Viacom…” | Ce este Comedy Central Extra? | Comedy Central Extra este un canal european de televiziune, deținut de Viacom, lansat în Regatul Unit și Irlanda în 2003. |
| 20 | text județ | „Huedin este un oraș în județul Cluj, Transilvania, România…” | În ce județ se găsește Huedin? | În județul Cluj. |

Ce am văzut citindu-le: toate cele 20 sunt corecte după text. Da/nu: #1 și #3 schimbă numărul/anul cu unul care nu
e în text, #4 pune un regizor real, dar greșit (al altui film), corect „Nu.”. Câteva texte au greșeli din Wikipedia
(„Repblica”, „intres”, „12.229 locuitori” fără „de”), la fel ca în noaptea 10.

## Testele

`CUDA_VISIBLE_DEVICES=-1 python -m pytest -q`: **813 trec, 1 sărit**, în 3 min 29 s (înainte: 809; +4 teste noi).

## Fișierele

- în Git: `unelte/conversatie_text.py`, `teste/test_conversatie_text.py`, `config/conv_w2_text_v2.toml`,
  `docs/preinregistrari/2026-10-20_noaptea11_formulari.md`, acest raport, `plan/coada.md`;
- doar pe calculator (nu intră în Git): `date/conversatie/text_v2/` (antrenare.jsonl, examen.json, info.json),
  `lucru/s6_verif_v1/` (copia de verificare a datelor nopții 10), `lucru/s6_exemple.py`, `lucru/s6_lungimi.py`.

## Ce urmează

- **Supraveghetorul** (trecerea de 14:15 sau 17:15): citește cele 20 de perechi și abaterea de mai sus; dacă sunt bune,
  scrie la S7 „perechi verificate: da”.
- **Executantul**, după 19:00: dacă S7 are „perechi verificate: da”, face pasul 0 (sarcina Windows) și pornește noaptea 11.
- **Adrian**: nimic de făcut acum; dacă vrei, uită-te la abaterea cu cele trei formulări vechi.
