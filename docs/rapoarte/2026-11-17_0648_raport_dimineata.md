# Raportul de dimineață — 17 noiembrie 2026, 06:48

*Scris de Claude Code, pornit de sarcina „Kronos raport dimineata”, fără om de față. Am doar citit: n-am pornit nimic pe
placă și n-am schimbat cod, configurare sau jurnal.*

## Pe scurt

- **Noaptea a mers curat.** S-au terminat S117 (00:00–01:06), S123 / E0 (01:29–02:46), iar la 03:00 a pornit S121.
- **S117: rămâne #651.** Modelul nou #668 a luat 42/200 la chat, sub pragul de 55.
- **S123 (E0, testul de memorare):** la întrebările „sociale” diferența A−B a ieșit +37,5 puncte procentuale, adică un semnal
  puternic că modelul a memorat răspunsurile. La total a ieșit +14,7, rezultat neconcludent.
- **S121 încă rulează** (chat + calcule, 4 ore, pornit din #651). Ora 3 din 4 e gata. Antrenarea se termină pe la 07:07,
  apoi urmează examenele, până pe la ~08:45. **Verdictul nu se poate da încă.**
- **Testele: toate trec** (1488 trec, 1 sărit, 0 picate).
- **Nimic urgent de la tine.**

## Ce a rulat noaptea, pe rând

| Ora | Ce | Cum s-a terminat |
|---|---|---|
| 16 nov 19:29 → 17 nov 01:06 | **S117**: chat pornit din #651, apoi examenele (#668 antrenat, gata la 00:00) | Gata. Rămâne #651. Raport: `2026-11-17_0100_S117_chat.md` |
| 01:29 → 01:38 | **S123 (E0)**, prima încercare | Oprită înainte de rulare: două verificări de pregătire au picat. Întrebarea către tine e în `2026-11-17_0140_E0_memorare.md` |
| 02:15 | Supraveghetorul | După răspunsul tău (C-131, B = 197) a aprobat din nou S123 |
| 02:29 → 02:46 | **S123 (E0)**, a doua încercare | Gata. Sociale +37,5 pp (memorare puternică), total +14,7 pp (neconcludent). Raport: `2026-11-17_0240_E0_memorare.md` |
| 02:59 → acum | **S121**: chat + calcule, 4 ore, din #651 | Rulează normal (vezi mai jos) |

Toate pornirile executantului din noapte s-au încheiat cu „cod 0”, adică fără erori.

## S121 acum (ce rulează pe placă)

- Pre-înregistrarea a fost scrisă și urcată pe GitHub la 03:00, **înainte** de pornire:
  `docs/preinregistrari/2026-11-17_w2_mare_24zcc.md`.
- Am văzut în jurnal că a pornit din modelul #651, cum se cerea.
- Modelele salvate din oră în oră. Scorul „val_bpb” arată cât de bine prezice modelul textul românesc; **cu cât e mai mic,
  cu atât mai bine**. #651, modelul de pornire, are 1,0878.

  | Ora | Model | val_bpb |
  |---|---|---|
  | 1 (04:01) | #677 | 1,0900 |
  | 2 (05:03) | #678 | 1,0901 |
  | 3 (06:05) | #679 | 1,0902 |
  | 4 | — | se termină pe la 07:07 |

  Scorul e puțin mai slab decât la #651, dar încă în limita pragului (verdictul cere cel mult 1,0978, adică #651 + 0,01).
  Contează însă doar cifrele re-măsurate la final.
- **Placa video:** 6.568 MB (limita: 7.000 MB), 63–64 °C (limita: 83 °C). **Discul C:** 55 GB liberi (paza oprește
  la 15 GB).

## Pre-înregistrarea și verdictul

Pre-înregistrarea nopții, `2026-11-17_w2_mare_24zcc`, **n-am închis-o**. Experimentul nu s-a terminat: antrenarea mai are o
oră, iar examenele (calcule, chat, română, „din text”, instrucțiuni) n-au rulat încă. Dacă o închideam acum, ar fi rămas
fără cifre. Niciun prag nu se poate măsura încă. La fel s-a procedat și pe 16 noiembrie cu S111. O închide executantul
când se termină S121, cu raportul lui.

Pragurile de verificat atunci, copiate din pre-înregistrare: **CALCULE CÂȘTIGĂ** dacă română curat ≤ #651 + 0,01 **și**
corecte S15 + S4 + tipuri noi ≥ #651 − 10 **și** R1 ≥ 90 **și** chat (a)+(b) ≥ #651 + 5 **și** sociale (b) ≥ #651 − 3
**și** calcule ≥ #651 + 60 (din 200). Altfel rămâne #651.

## CONTINUUM

A stat toată noaptea în „repaus” (ultimul ciclu: #9457, la 06:35). Doar a observat și n-a pornit nimic, pentru că placa e a
executantului din cascadă. Așa trebuie. Lucrurile pe care le are în așteptare sunt aceleași ca până acum: „repara:povesti” și
„dezvolta:sens”.

## Cele 20 de răspunsuri alese la întâmplare

Noaptea a avut examenul de conversație (în lanțul S117, la 00:34). Ultimul model examinat a fost **#668**, iar fișierul e
`lucru/examen_conversatie/experiment_668_20261117_003448.json`. Pe tot examenul: 180 de întrebări, nota medie 6,81 din 10,
113 răspunsuri corecte, 44 de răspunsuri „Nu scrie în text.” (adică modelul a zis că răspunsul nu e în text).

Am ales cu sămânța **20261117** (`random.Random(20261117).sample`, 20 din 180). „Referința” e răspunsul corect, iar nota e
dată de profesor (1 = greșit, 10 = corect).

| # | Întrebarea | Răspunsul lui Kronos | Referința | Nota profesorului | e bine? (tu) |
|---|---|---|---|---|---|
| 1 | Care a fost funcția lui Guri Ivanovici Marciuk? | Președinte al Academiei Ruse de Științe. | Președinte al Academiei Ruse de Științe. | 10 | |
| 2 | Ce actori apar în Mitică Popescu? | Micaela Caracaș, Mircea Jida și Remus Mărgineanu. | Micaela Caracaș, Mircea Jida și Remus Mărgineanu. | 10 | |
| 3 | Ce rol a avut Patrick Warburton în Seinfeld? | David Puddy. | David Puddy. | 10 | |
| 4 | Pe cine a întruchipat Avan Tudor Jogia în O fată ca mine? | Ben Kingsley. | Danny Araujo. | 1 | |
| 5 | Pe cine a jucat Nikita Mihailovici Efremov în Tetris care a avut premiera la 31 martie 2023? | Alexei Pajitnov. | Alexei Pajitnov. | 10 | |
| 6 | Cine e producătorul lui Bounty? | Mars. | Mars. | 10 | |
| 7 | Ce premiu a obținut Toate păsările din cer? | Premiul Nebula. | Premiul Nebula. | 10 | |
| 8 | Cui îi aparține producția lui Jiefang C-30 sau Jiefang CA 30? | FAW Jiefang. | FAW Jiefang. | 10 | |
| 9 | În care țară se află Mănăstirea Nechit? | În România. | În România. | 10 | |
| 10 | Pe ce canal a rulat Sheena? | Pe Antena 1. | Pe Antena 1. | 10 | |
| 11 | Cine joacă în rolurile principale din De ce eu? sau Cristian? | Emilian Oprea, Andreea Vasile și Mihai Constantin. | Emilian Oprea, Andreea Vasile și Mihai Constantin. | 10 | |
| 12 | Care e profesia lui Juan Eduardo Esnáider? | Fotbalist. | Fotbalist. | 10 | |
| 13 | Ce distincție a primit Electric Velocipede? | Nu scrie în text. | Premiul Hugo. | 1 | |
| 14 | Ce premiu a câștigat Elizabeth Ann Scarborough? | Nebula. | Premiul Nebula. | 10 | |
| 15 | Pe ce poziție joacă Rade Krunić? | Mijlocaș. | Mijlocaș. | 10 | |
| 16 | Ce funcție a ocupat Michel Camdessus? | Director general al Fondului Monetar Internațional. | Director general al Fondului Monetar Internațional. | 10 | |
| 17 | Ce naționalitate are Cerasela Iosifescu? | Nu scrie în text. | Română. | 1 | |
| 18 | Cine i-a fost partener de viață lui Erika Sawajiri? | Nu scrie în text. | Cu Tsuyoshi Takashiro. | 1 | |
| 19 | Pe ce poziție joacă María Gomes Da Costa? | Nu scrie în text. | Intermediar stânga. | 1 | |
| 20 | Care e orașul în care se află Casa lui Mihalache Cațica? | În Chișinău. | În Chișinău. | 10 | |

Din cele 20: profesorul a dat 15 de 10 și 5 de 1. Patru dintre greșeli sunt „Nu scrie în text.” la întrebări al căror
răspuns era în text. Asta e problema cunoscută: modelul zice „nu scrie” pe nedrept. A cincea greșeală (#4) e un nume
inventat. Notă: #668 **nu** e modelul folosit acum (rămâne #651). Tabelul arată doar cum a răspuns modelul încercat azi-noapte.

## Testele

Comanda: `CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -m pytest -o addopts="" --basetemp=lucru/teste_tmp -q`, doar pe
procesor, ca să nu atingă placa.

Rezultat: **1488 trec, 1 sărit, 0 picate** (7 minute și 11 secunde). Ieri picase un test care cere 40 GB liberi pe disc.
Azi nu mai pică, iar C: are 55 GB liberi.

## Ce aștept de la tine

- **Nimic urgent.** S121 merge singură, iar executantul scrie verdictul după examene (pe la ~08:45–09:00), în raportul lui.
- Dacă vrei, uită-te la raportul E0 (`2026-11-17_0240_E0_memorare.md`). Semnalul de memorare la întrebările „sociale” e
  puternic și poate schimba ce alegi mai departe.
- Coloana „e bine? (tu)” de la cele 20 de răspunsuri, dacă ai timp.
