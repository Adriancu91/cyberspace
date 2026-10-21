# Raportul de dimineață — 21 octombrie 2026

*Scris de Claude Code, pornit singur de sarcina Windows „Kronos raport dimineata” (07:40), fără om de față, la 07:52.
Am doar citit jurnalele; n-am pornit nimic pe placă și n-am schimbat cod.*

## Pe scurt

- **Noaptea 11 (sarcina S7 din cascadă) a rulat cap-coadă, fără nicio eroare.** 3 ore de antrenare (20:47–23:58), apoi
  examenele pe ultimul model, **#407** (00:01–00:03). Toate s-au încheiat cu cod 0 (adică fără eroare).
- **Verdictul: PARȚIAL, fără regresie** (adică a ieșit ceva mai bine, dar nu tot ce ne propusesem, și n-a stricat nimic).
  L-a scris deja executantul la 00:05, în pre-înregistrare și în `docs/rapoarte/2026-10-21_0005_S7_noaptea11.md`.
  L-am verificat: cifrele din examen sunt aceleași.
- **Testele de azi-dimineață: 813 trecute, 1 sărit, 0 picate.**
- **După 00:20 n-a mai rulat nimic.** Executantul a verificat coada la fiecare jumătate de oră și n-a avut ce porni.
  Placa e liberă.

## Ce a rulat noaptea

| ora | ce | rezultat |
|---|---|---|
| 20:47–23:58 | antrenarea „răspuns din text” cu formulări diferite, din #401 (linia `w2_conv_text_v2`) | cod 0; 3 modele păstrate: #405, #406, #407 |
| 00:01 | examenul nopții 10 pe #407 (#408) | 80 de întrebări, nota medie 9,36 |
| 00:02 | examenul S4 „formulări diferite” pe #407 (#409) | 60 de întrebări |
| 00:03 | validările pentru română și cod (#410) + setul sacru | gata |
| 00:05–00:20 | testele, rulate de executant | 813 trecute, 1 sărit |
| 00:20–07:28 | executantul, la fiecare 30 de minute | „nimic aprobat de făcut acum” |

- **Placa în timpul nopții:** cel mult 6.303 MB și 63 °C, sub limitele de 7.000 MB și 83 °C.
- **Placa acum (07:45):** 712 MB folosiți, 0% ocupată, 28 °C. Niciun program greu nu merge pe ea.
- **CONTINUUM** (bucla care observă singură): doar privește, cum ai cerut. Ultimul ciclu, #2069 la 07:35: „REPAUS:
  placa e a executantului”. Așteaptă două lucruri: „repara:povesti” și „dezvolta:sens”. N-a pornit nimic.
- **Jurnalul de experimente** se oprește la #410. Nu există nimic nou după examene.
- `lucru/noapte_conversatie.log` n-a mai fost scris din 19 octombrie. E normal: noaptea asta a pornit-o cascada, nu sarcina
  veche de noapte.

## Cifrele (modelul #407, față de #401 de ieri)

„Corect” = profesorul (alt model AI, care dă note) a dat cel puțin 7 din 10.

| ce se măsoară | pragul | #407 | #401 | |
|---|---|---|---|---|
| aceeași informație, întrebată altfel (a) | confirmat ≥ 10/15 | **11/15** | 7/15 | trece |
| tipuri noi de întrebări (b) | confirmat ≥ 5/15 | **2/15** | 3/15 | NU trece |
| „Nu scrie în text.” spus pe nedrept | confirmat ≤ 10/45 | **11/45** | 22/45 | NU trece (la una) |
| examenul nopții 10: răspuns din text | ≥ 45/50 | **49/50** | 50/50 | trece |
| examenul nopții 10: „Nu scrie” la locul lui | ≥ 16/20 | **19/20** | 20/20 | trece |
| examenul nopții 10: refuz greșit | ≤ 5/50 | **0/50** | 0/50 | trece |
| româna (mai mic = mai bine) | ≤ 1,3133 | **1,2818** | 1,2769 | trece |
| codul (mai mic = mai bine) | ≤ 0,8174 | **0,7882** | 0,7852 | trece |
| poveștile (mai mic = mai bine) | ≤ 0,47 | **0,4395** | 0,4357 | trece |
| fapte noi | ≥ 65 | **75** | 74 | trece |
| urmărit: întrebări da/nu (c) | — | **13/15** | 0/15 | — |
| urmărit: întrebări fără răspuns în text (d) | — | **12/15** | 11/15 | — |
| urmărit: setul sacru | — | **27/50** | 24/50 | — |
| conversația simplă | — | 6/10 | 7/10 | — |

## Verdictul

Pre-înregistrarea `docs/preinregistrari/2026-10-20_noaptea11_formulari.md` era deja închisă, cu „Ce a ieșit” și cu
„Verdictul” scrise de executant la 00:04–00:05. **N-am mai închis-o o dată și n-am schimbat-o.**

Am refăcut verdictul strict după pragurile scrise în ea și iese la fel: **PARȚIAL, fără regresie.**
- Nu e CONFIRMAT, pentru că tipurile noi (b) au 2/15 (trebuia ≥ 5) și refuzul pe nedrept e 11/45 (trebuia ≤ 10).
- Nu e INFIRMAT, pentru că (a) e 11/15, nu ≤ 7.
- „Fără să strice noaptea 10” și „să nu uite”: trec toate.

Pe înțeles: dacă pui aceeași întrebare cu alte cuvinte, Kronos înțelege acum mult mai des. A învățat și să răspundă
„Da.”/„Nu.”. Dar la întrebări de un fel pe care nu l-a văzut niciodată tot nu se descurcă. Uneori răspunde „Da.” sau „Nu.”
și unde nu e o întrebare cu da/nu, de exemplu „La ce club evoluează…?” → „Da.”.

## Cele 20 de răspunsuri alese la întâmplare

Din `lucru/examen_conversatie/experiment_407_20261021_000129.json` (modelul #407, examenul nopții 10), cu
`random.Random(1019).sample(…, 20)`. Le-am scos eu din nou, azi-dimineață, și sunt aceleași ca în raportul executantului.
Examenul și numărul de pornire al alegerii (1019) sunt aceleași ca ieri, deci sunt **exact aceleași 20 de întrebări ca
ieri**. Așa poți compara, dar nu vezi întrebări noi.

„text” = răspunsul se află în paragraful dat; „nu_scrie” = răspunsul corect e „Nu scrie în text.”.

| nr. | felul | întrebarea | răspunsul lui Kronos | referința | nota profesorului | e bine? (verificat de centrul de comandă la cererea lui Adrian, 21 oct 10:10) |
|---|---|---|---|---|---|---|
| 1 | text | Ce este sosul? | Sosul este un preparat culinar lichid sau vâscos alcătuit dintr-un amestec de ingrediente și care acompaniază preparatele alimentare. | Sosul este un preparat culinar lichid sau vâscos alcătuit dintr-un amestec de ingrediente și care acompaniază preparatele alimentare. | 10 | da |
| 2 | text | În ce an s-a născut Nicolae Daniel Balauru? | În 1980. | În 1980. | 10 | da |
| 3 | text | Din ce an este Necruțătorul? | Din 1992. | Din 1992. | 10 | da |
| 4 | text | Ce este Râul Tazlăul Mare? | Râul Tazlăul Mare este un curs de apă, din bazinul râului Trotuș. | Râul Tazlăul Mare este un curs de apă, din bazinul râului Trotuș. | 10 | da |
| 5 | text | În ce an s-a născut Patrick Jørgensen? | În 1991. | În 1991. | 10 | da |
| 6 | nu_scrie | Câți locuitori are Briceni? | Nu scrie în text. | Nu scrie în text. | 10 | da |
| 7 | nu_scrie | Ce este Punct de evaporare? | Nu scrie în text. | Nu scrie în text. | 10 | da |
| 8 | text | Din ce an este Trick? | Din 2019. | Din 2019. | 10 | da |
| 9 | text | Din ce an este Amenințarea? | Din 1976. | Din 1976. | 10 | da |
| 10 | text | În ce an s-a născut Jaka Štromajer? | În 1983. | În 1983. | 10 | da |
| 11 | text | Câți locuitori are Lalevići? | 154 de locuitori. | 154 de locuitori. | 10 | da |
| 12 | text | În ce an s-a născut Laura Elizabeth Metcalf? | În 1955. | În 1955. | 10 | da |
| 13 | text | Cine a scris Ciuta? | Victor Ion Popa. | Victor Ion Popa. | 10 | da |
| 14 | text | Câți locuitori are Comitatul Washington? | 238.136 de locuitori. | 238.136 de locuitori. | 10 | da |
| 15 | nu_scrie | Ce este Moselle Open 2023? | Nu scrie în text. | Nu scrie în text. | 10 | da |
| 16 | text | Cine este Barrie "Barriemore" Barlow? | Barriemore "Barriemore" Barlow este un muzician englez, cel mai cunoscut ca baterist și percuționist în trupa rock, Jethro Tull din mai 1971 până în iunie 1980. | Barrie "Barriemore" Barlow este un muzician englez, cel mai cunoscut ca baterist și percuționist în trupa rock, Jethro Tull din mai 1971 până în iunie 1980. | 9 | aproape: numele e greșit („Barriemore” de două ori, corect „Barrie”); restul propoziției e identic |
| 17 | text | Câți locuitori are Bartula? | 355 de locuitori. | 355 de locuitori. | 10 | da |
| 18 | text | În ce an s-a născut Magda Alfredo Cazanga? | În 1991. | În 1991. | 10 | da |
| 19 | text | Cine a fost Flavius Valerius Severus? | Flavius Valerius Severus a fost un împărat roman între 306-307. | Flavius Valerius Severus a fost un împărat roman între 306-307. | 10 | da |
| 20 | text | Ce este Sphaerodactylus richardi? | Sphaerodactylus richardi este o specie de șopârle din genul Sphaerodactylus, familia Gekkonidae, descrisă de S.Blair Hedges și Garrido 1993. | Sphaerodactylus richardi este o specie de șopârle din genul Sphaerodactylus, familia Gekkonidae, descrisă de S.Blair Hedges și Garrido 1993. | 10 | da |

**Verificarea celor 20 (centrul de comandă, la cererea lui Adrian):** 19 din 20 identice cu referința; nr. 16 are o greșeală mică
de nume (prenumele repetat), nota 9 a profesorului e corectă. Verdictul „fără regresie pe noaptea 10” e confirmat pe acest eșantion.

Greșelile lui #407 la acest examen nu au ieșit printre cele 20:
- „Cine a scris Pasărea albastră?” → „Maurice Tourneur.” Acesta e regizorul, nu autorul; nota 2.
- „Unde a murit Jean-Luc Dehaene?” → a copiat prima propoziție, deși trebuia „Nu scrie în text.”.
- Conversația simplă: 4 din 10 greșite, de exemplu „What is your name?” → „M-a și puțină engleză.”.

Toate cele 60 de răspunsuri din examenul S4 sunt în raportul executantului.

## Testele

`CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -m pytest -q`, pe procesor, la 07:44–07:51: **813 trecute, 1 sărit,
0 picate** (cod 0, 3 minute și 28 de secunde). Testul sărit e cel care are nevoie de profesor pe placă, ca de obicei.

## Ce aștept de la tine

1. **Hotărăști dacă #407 îl înlocuiește pe #401 în fila „Întreabă din text”.**
   - Pentru: înțelege mai bine întrebările puse altfel și răspunde la da/nu.
   - Contra: la câteva întrebări care nu cer da/nu răspunde totuși „Da.”/„Nu.” și a pierdut 1–2 întrebări pe care #401 le
     știa.
2. **Te uiți la cele 20 de răspunsuri** de mai sus și completezi coloana „e bine? (tu)”. Sunt aceleași întrebări ca ieri.
   Dacă vrei întrebări noi data viitoare, spune-mi și schimb numărul de pornire al alegerii (1019).
3. **Azi, în coadă, de la 08:00:** S8, S9, S10 și S11 sunt aprobate și le pornește executantul.
   - S12 (noaptea 12) pornește diseară doar după ce S11 e gata și supraveghetorul scrie „perechi verificate: da”.
   - S13 așteaptă „da”-ul tău.
4. **Nimic stricat în noaptea asta.** N-a căzut nimic și n-a picat niciun test.

Fișierul: `docs/rapoarte/2026-10-21_0752_raport_dimineata.md`
