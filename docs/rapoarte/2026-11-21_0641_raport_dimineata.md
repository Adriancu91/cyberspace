# Raportul de dimineață — 21 noiembrie 2026

*Scris de Claude Code (sarcina „Kronos raport dimineata”), 21 noiembrie 2026, 06:41. Am doar citit: jurnalele din
`lucru/` (cascada, raportul de dimineață, CONTINUUM), raportul S129 (`docs/rapoarte/2026-11-21_0130_S129_formulari_d.md`),
pre-înregistrarea nopții, `lucru/jurnal/experimente.jsonl`, `plan/coada.md`, git log și placa video. N-am pornit nimic
și n-am schimbat cod.*

## Pe scurt

- **Noaptea a mers fără erori.** S-a rulat **S129**: Kronos a învățat 4 ore pornind din #720, pe date în care exemplele
  „răspunde din text” sunt puse de 2 ori și înmulțirile sunt mai multe (800 în loc de 500). Apoi examenele. Toți pașii s-au
  terminat normal (cod 0). Modelul nou e **#736**.
- **Verdict: rămâne #651** — de data asta **la un singur răspuns**. #736 a trecut **pentru prima dată pragul la întrebările
  formulate altfel: 54,0 %** (pragul 48,0 %), dar la răspunsurile „din text” a luat **217**, iar pragul e **218**.
- #736 e cel mai bun model de până acum la chat (51), la calcule (90) și la formulări (54 %).
- **Testele: 1.556 trec, 1 sărit, 0 picate.**
- **Discul C: ~146 GB liberi.** Placa video e liberă acum (487 MB, 30 °C).

## Ce a rulat noaptea

| ce | când | cât a durat | placa video maxim | s-a terminat bine? |
|---|---|---|---|---|
| S129 pașii 0–3 (procesor, făcuți ziua): datele noi `conversatie_chat5` (141.070 de rânduri, 0 suprapuneri cu examenele) | 20 nov 07:59 – 11:39 | | — | da (cod 0) |
| verificarea discului înainte de pornire: 154,10 GB liberi (trebuiau ≥ 30) | 20 nov 19:00 | | — | da |
| S129 antrenarea: 4 ore din #720 (configurarea nouă `24zci`) | 20 nov 19:00 – 23:05 | 4 h 5 min | 6.428 MB / 64 °C | da (cod 0) |
| modele salvate | #733, #734, #735, **#736** (ultimul) | | | |
| S129 examenele pe #651, #736, #720 (și #680 la calcule și formulări) | 23:30 – 01:16 | 1 h 47 min | 4.126 MB / 64 °C | da (cod 0, toți cei 29 de pași) |
| executantul cascadei (verificări la 30 de minute) | toată noaptea, ultima la 06:29 | | | da; „nimic aprobat de făcut acum” |

- În jurnalul antrenării apare „Pornesc din modelul experimentului #720” — deci a pornit de unde trebuia.
- Scorul de validare pe ore: 1,0905 / 1,0901 / 1,0901 / 1,0899 (a plecat de la 1,0906) — prima dată pe linia asta când
  coboară puțin, adică datele noi nu strică româna.
- Placa a stat tot timpul sub limita de 7.000 MB și s-a eliberat la 01:16.
- Modelele vechi și examenele n-au fost schimbate (amprentele celor 38 de fișiere păzite sunt aceleași înainte și după).
- **CONTINUUM** (paznicul automat) doar a urmărit toată noaptea, în „repaus”, și n-a pornit nimic, cum trebuie. Ultima
  înregistrare: 06:35 (ciclul #10581).
- **Supraveghetorul** a verificat verdictul la 02:15: corect, rămâne #651.

## Cifrele (S129)

| | #651 (modelul din chat) | #680 | #720 (de ieri) | **#736 (nou)** | pragul scris dinainte | trece? |
|---|---|---|---|---|---|---|
| româna (cât de bine prezice textul; mai mic = mai bine) | 1,0878 | | 1,0906 | **1,0899** | ≤ 1,0978 | da |
| răspunsuri corecte „din text” (S15 + S4 + tipuri noi, din 320) | 228 | | 218 | **217** | **≥ 218** | **NU** (cu 1) |
| respectarea instrucțiunilor (R1) | 99,31 | | 97,82 | **98,05** | ≥ 90 | da |
| chat (fapte + conversație socială) | 25 | | 50 | **51** | ≥ 30 | da |
| examenul de calcule | 1 | 51 | 80 | **90** | ≥ 61 | da |
| **întrebări formulate altfel (examenul de formulări)** | 20,5 % | 33,0 % | 46,0 % | **54,0 %** (108 din 200) | ≥ 48,0 % | **da** (prima dată) |
| — din care adunare + scădere + împărțire (din 78) | 0 | 1 | 8 | **22** | | |
| — din care înmulțire (din 42) | 2 | 4 | 13 | **16** | | |

**Verdictul, strict după pragurile scrise dinainte: rămâne #651** (cinci condiții din șase trec; „din text” 217 < 218).
Interfața de chat nu se schimbă.

Pre-înregistrarea nopții (`docs/preinregistrari/2026-11-20_w2_mare_24zci.md`) a fost deja închisă de executant la 01:30,
cu „Ce a ieșit” și „Verdictul” (același: rămâne #651). N-am mai avut nimic de închis. (Pre-înregistrarea
`2026-11-21_w2_mare_24zcj.md` e pentru noaptea care vine, S131 — rămâne deschisă.)

Pe înțeles: datele noi **au mers foarte bine la calcule întrebate altfel** — împărțirea a sărit de la 2 la 11 din 30,
adunarea de la 4 la 8. Dar la „din text” n-a urcat înapoi, deși i-am dat de două ori mai multe exemple: în ultimele patru
runde a coborât 222 → 219 → 218 → **217**, câte un răspuns pe rundă. Al doilea notator (martorul) îl vede pe #736 chiar
puțin peste #720 (210 față de 208), deci diferența de 1 față de prag e la limita „zgomotului” de notare — dar pragul e pragul.
La fapte fără text (ani, locuri, oameni) tot inventează.

## Cele 20 de răspunsuri alese la întâmplare

Noaptea a avut examenul de conversație (în lanțul S129, la 00:12). Ultimul model e **#736**, iar fișierul e
`lucru/examen_conversatie/experiment_736_20261121_001209.json`. Pe tot examenul: 180 de întrebări, nota medie **6,60 din
10**, **108** răspunsuri corecte, **47** de „Nu scrie în text.” (adică modelul a zis că răspunsul nu e în textul primit, deși
era). Comparație în aceeași noapte: #720 6,49 / 106 / 49; #651 6,94 / 115 / 39.

Am ales cu sămânța **20261121** (`random.Random(20261121).sample`, 20 din 180). „Referința” e răspunsul corect, iar nota e
dată de profesor (1 = greșit, 10 = corect).

| # | fel | întrebarea | răspunsul lui Kronos | referința | nota | e bine? (tu) |
|---|---|---|---|---|---|---|
| 1 | gen_muzical | Ce gen de muzică face The Moody Blues? | Cântec. | rock | 3 | |
| 2 | oras | Care e orașul în care se află Casa lui Mihalache Cațica? | În Chișinău. | Chișinău | 10 | |
| 3 | premiu | Ce premiu a primit Poartă-ți plugul peste oasele morților? | Premiul Alfred Bauer. | Premiul Alfred Bauer | 10 | |
| 4 | producator | Cine a produs The Iron Horse? | Fox Film. | Fox Film | 10 | |
| 5 | instrument | La ce instrument cântă Doug Ingle? | Nu scrie în text. | orgă | 1 | |
| 6 | castigator | Cine a câștigat Cupa României 2018-2019? | FC Viitorul. | FC Viitorul | 10 | |
| 7 | producator | Cine semnează producția lui Hero Elementary? | Twin Cities PBS. | Twin Cities PBS | 10 | |
| 8 | canal | Pe ce canal a avut premiera Spirala? | Pe Syfy. | Syfy | 10 | |
| 9 | actori | Cine sunt actorii principali din Audrey Rose? | Marsha Mason și Anthony Hopkins. | Marsha Mason și Anthony Hopkins | 10 | |
| 10 | oras | Ce oraș găzduiește sediul lui League of the South? | În Killen. | Killen | 10 | |
| 11 | oras | Care e orașul în care își are sediul Brussels Airlines? | În Bruxelles. | Bruxelles | 10 | |
| 12 | profesie | Ce ocupație a avut Robert Klein? | Nu scrie în text. | filozof și istoric | 1 | |
| 13 | oras | În ce oraș se află sediul lui Meebo? | În Mountain View. | Mountain View | 10 | |
| 14 | oras | Ce oraș găzduiește sediul lui Atromitos FC? | În Peristeri. | Peristeri | 10 | |
| 15 | continent | Pe ce continent se află Tibetul? | Nu scrie în text. | Asia | 1 | |
| 16 | profesie | Ce face Loïc Rémy de meserie? | Fotbalist. | fotbalist | 10 | |
| 17 | sot | Rosanna Lauren Arquette s-a căsătorit cu cine? | Cu John Sidel. | John Sidel | 10 | |
| 18 | producator | Cui îi aparține producția lui Jiefang C-30 sau Jiefang CA 30? | FAW Jiefang. | FAW Jiefang | 10 | |
| 19 | gen_muzical | Ce gen de muzică face Heaven Upside Down? | Cântăreț. | rock | 2 | |
| 20 | castigator | Cine a fost câștigătorul în Cupa UEFA 1978-1979? | Borussia Mönchengladbach. | Borussia Mönchengladbach | 10 | |

Din cele 20: **15 note de 10**, o notă de 3, o notă de 2 și 3 note de 1. **Toate cele 3 note de 1 sunt „Nu scrie în
text.”**, deși răspunsul era în textul primit — aceeași slăbiciune ca în zilele trecute. Celelalte două greșeli sunt
răspunsuri de felul greșit: la „ce gen de muzică” a zis „Cântec.” / „Cântăreț.” în loc de „rock”.
(Eșantionul de azi a ieșit mai bun decât media examenului — 15 din 20 corecte, față de 108 din 180 pe tot examenul; e
doar norocul tragerii.)

## Testele

`CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -m pytest`: **1.556 trec, 1 sărit, 0 picate** (7 min 22 s).

## Ce urmează (din coadă)

- **S131** (aprobată de supraveghetor la 02:15, nu de tine): încă o rundă, de data asta din **#736**, cu exemplele „din
  text” puse de **3 ori** (linia nouă „24zcj”). Pregătirea pe procesor e deja făcută (02:45). Învățarea pe placă **doar la
  noapte (21 → 22 nov), de la 19:00**, pornire cel târziu la 00:30, placa liberă la 07:00. Ziua de azi placa rămâne liberă.

## Ce aștept de la tine

1. **Nimic urgent.** Verdictul e după pragul scris dinainte, nimic n-a căzut.
2. **O decizie, dacă vrei:** #736 e primul model care trece pragul de formulări și e cel mai bun la chat (51 față de 25 la
   #651) și la calcule (90 față de 1), dar îi lipsește **un singur răspuns** la „din text” (217 față de pragul 218; #651 are
   228). Dacă totuși îl vrei în chat, ar fi o decizie nouă a ta. Altfel rămâne #651.
3. **S131 la noapte** e aprobată de supraveghetor, nu de tine. Dacă nu vrei încă o rundă, spune „nu S131” până diseară
   la 19:00.
4. **Git (tot de rezolvat, ca ieri):** pe calculator a rămas din 17 noiembrie o operație Git neterminată (o „rebazare”).
   Codul e la zi cu GitHub, dar comenzile automate dau eroare din cauza ei (azi la 06:40, la pornirea sarcinii asta:
   `git pull` a picat cu „You are not currently on a branch”). Când ai un minut, în dosarul `C:\Kronos\cyberspace` rulează:
   `git rebase --continue`
5. Dacă ai timp: coloana „e bine? (tu)” de la cele 20 de răspunsuri.
