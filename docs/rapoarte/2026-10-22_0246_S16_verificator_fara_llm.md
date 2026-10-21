# S16 — E0: verificatorul fără LLM pentru „răspuns din text” (22 octombrie 2026, 02:46)

Scris de executant (Claude Code pe workstation), pornit de cascadă. Sarcina: S16 din `plan/coada.md`, aprobată de
supraveghetor la 02:15 (categoriile 2 și 5), din direcția aprobată de Adrian pe 22 oct 01:45.

## Pe scurt

- **Acordul împreună (S15 + S4), regula principală: 527/540 = 97,6 % ≥ 90 % → „verificatorul poate înlocui pe Qwen”.**
- Niciun model nu are acord sub 85 % (cel mai mic: #401 și #415, 97,1 %).
- Varianta F1 (doar raportată): 507/540 = 93,9 %; acolo #401 pe S15 cade la 82,5 % (F1 pedepsește răspunsurile lungi).
- Scorurile S15 după verificator: (b2) 7/9/6 din 50 și (e) 13/4/30 din 30 pe #401/#407/#415 (Qwen: 6/9/6 și 14/4/30).
  Concluzia din S15 („tipurile văzute s-au învățat, dar nu se transferă”) rămâne aceeași cu judecătorul nou.
- N-a rulat niciun model (nici Qwen, nici Kronos), placa n-a fost folosită. Fișierele vechi n-au fost atinse.
- Teste: **868 trec, 1 sărit** (851 înainte + 17 noi).

## Ce am făcut

1. `unelte/verificator_text.py` — funcția `verifica(referinta, raspuns)` întoarce `corect`, `motiv`, `scor` (= acoperirea),
   plus `acoperire`, `f1`, `corect_f1`. Regulile sunt cele din coadă, în ordinea: exact → referințe scurte speciale →
   suprapunere (acoperire ≥ 0,8 și răspunsul nu e „Nu scrie în text.”). F1 ≥ 0,8 e varianta a doua (aceleași reguli exact
   și speciale, doar ultimul pas cu F1 în loc de acoperire).
2. `teste/test_verificator_text.py` — 17 teste (cerute: cel puțin 12): normalizarea, exact, ş/ș și ţ/ț, diacriticele
   rămân (In ≠ În), punctuație și ghilimele, răspuns lung care conține referința, repetarea întrebării, acoperire parțială,
   repetiții (multiset), „Nu scrie în text.” corect și pe nedrept, referința „Nu scrie în text.” cu răspuns inventat,
   da/nu (inclusiv „Da, …” și „Nu, …”), referință de un cuvânt, răspuns gol, F1.
3. `unelte/renoteaza_text.py` — citește fișierele de mai jos, pune alături nota Qwen (`nota_elev`, corect = ≥ 7) și
   verdictul verificatorului pe `raspuns` (referința) și `raspuns_elev`. Scrie DOAR un fișier nou:
   **`lucru/examen_conversatie/renotare_E0_20261022_023102.json`** (refuză să suprascrie ceva existent).

### Alegeri care nu scriau anume în sarcină (le spun ca să fie văzute)
- Semnele de punctuație (categoria Unicode „P”, inclusiv ghilimelele „ ”) se înlocuiesc cu spațiu, nu se lipesc:
  „într-un” → „într un”, la fel în referință și în răspuns. Simbolurile (%, °) rămân.
- „Răspunsul e «Nu scrie în text.»” = răspunsul normalizat **începe** cu „nu scrie în text”.
- La referința „Nu.” / „Nu, …”, răspunsul „Nu scrie în text.” **nu** contează ca „nu” (e refuz, nu negație).
- Dezacordurile de mai jos sunt toate pe suprapunere sau pe referința „Da.”; niciunul nu vine dintr-un „Nu.” cu răspunsul
  „Nu scrie în text.” (n-am măsurat separat cât ar fi schimbat celelalte alegeri).

### Fișierele, exact
- S15 (examen_generalizare_mare, 80 fiecare, 240 în total): `experiment_401_20261022_001355.json`,
  `experiment_407_20261022_001532.json`, `experiment_415_20261022_001707.json`.
- S4 (examen_generalizare_401, 60 fiecare, 300 în total): `experiment_401_20261020_105728.json`,
  `experiment_405_20261021_083112.json`, `experiment_406_20261021_083228.json`,
  **`experiment_407_20261021_000257.json`** (cel de 60 cu grupurile a/b/c/d; celălalt de la 00:01, `…_000129`, are 80 și
  e examenul nopții 10) și **`experiment_415_20261021_223319.json`** (la fel; `…_223154` are 80, e examenul nopții 10).
- Verificare: cifrele Qwen recalculate din fișiere = cele din raportul S15 ((b2) 6/9/6, (e) 14/4/30).

## Acordul (regula principală: acoperire ≥ 0,8)

| bucata | acord | Qwen corect, verificator greșit | Qwen greșit, verificator corect |
|---|---|---|---|
| **S15** | 234/240 = 97,5 % | 3 | 3 |
| **S4** | 293/300 = 97,7 % | 6 | 1 |
| **împreună** | **527/540 = 97,6 %** | **9** | **4** |
| model #401 (S15 + S4) | 136/140 = 97,1 % | 3 | 1 |
| model #405 (doar S4) | 59/60 = 98,3 % | 1 | 0 |
| model #406 (doar S4) | 59/60 = 98,3 % | 1 | 0 |
| model #407 (S15 + S4) | 137/140 = 97,9 % | 2 | 1 |
| model #415 (S15 + S4) | 136/140 = 97,1 % | 2 | 2 |
| S15 #401 / #407 / #415 | 78/80 fiecare = 97,5 % | 1 / 1 / 1 | 1 / 1 / 1 |
| S4 #401 / #405 / #406 / #407 / #415 | 58 / 59 / 59 / 59 / 58 din 60 | 2 / 1 / 1 / 1 / 1 | 0 / 0 / 0 / 0 / 1 |
| S4 fel a | 70/75 = 93,3 % | 4 | 1 |
| S4 fel b | 75/75 = 100 % | 0 | 0 |
| S4 fel c | 73/75 = 97,3 % | 2 | 0 |
| S4 fel d | 75/75 = 100 % | 0 | 0 |
| S4 „nu_scrie” (referința „Nu scrie în text.”, 75) | 75/75 = 100 % | 0 | 0 |
| S4 fără „nu_scrie” (225) | 218/225 = 96,9 % | 6 | 1 |
| S15 fel b2 | 145/150 = 96,7 % | 2 | 3 |
| S15 fel e | 89/90 = 98,9 % | 1 | 0 |

## Acordul, varianta F1 (doar raportată, nu decide)

| bucata | acord | Qwen corect, F1 greșit | Qwen greșit, F1 corect |
|---|---|---|---|
| S15 | 213/240 = 88,8 % | 25 | 2 |
| S4 | 294/300 = 98,0 % | 6 | 0 |
| **împreună** | **507/540 = 93,9 %** | 31 | 2 |
| model #401 / #405 / #406 / #407 / #415 | 88,6 / 98,3 / 98,3 / 94,3 / 95,0 % | 16 / 1 / 1 / 7 / 6 | 0 / 0 / 0 / 1 / 1 |
| S15 #401 / #407 / #415 | 82,5 / 91,2 / 92,5 % | 14 / 6 / 5 | 0 / 1 / 1 |
| S4 fel a / b / c / d | 94,7 / 100 / 97,3 / 100 % | 4 / 0 / 2 / 0 | 0 |
| S15 fel b2 / e | 91,3 / 84,4 % | 11 / 14 | 2 / 0 |

Cu F1, #401 pe S15 ar fi sub 85 %: #401 copiază des propoziția întreagă din text, iar Qwen o primește ca bună. F1 e prea
aspru cu asta; regula principală nu.

## Scorurile cu judecătorul nou

| | Qwen (≥ 7) | verificator (principal) | verificator F1 |
|---|---|---|---|
| S15 #401 (b2) / 50 | 6 | 7 | 2 |
| S15 #407 (b2) / 50 | 9 | 9 | 6 |
| S15 #415 (b2) / 50 | 6 | **6** | 4 |
| S15 #401 (e) / 30 | 14 | 13 | 4 |
| S15 #407 (e) / 30 | 4 | 4 | 2 |
| S15 #415 (e) / 30 | 30 | **30** | 28 |
| S4 #401 / 60 | 23 | 21 | 21 |
| S4 #405 / 60 | 35 | 34 | 34 |
| S4 #406 / 60 | 33 | 32 | 32 |
| S4 #407 / 60 | 38 | 37 | 37 |
| S4 #415 / 60 | 38 | 38 | 37 |

**Baseline-ul #415 pentru S17, cu verificatorul: (b2) 6/50, (e) 30/30, S4 38/60** — identic cu Qwen la (b2) și (e).

## Toate dezacordurile (13; sunt sub 20, deci le pun pe toate, fără tragere cu `random.Random(1022)`)

**Qwen corect, verificator greșit (9):**

| examen, model | întrebarea | referința | răspunsul elevului | nota Qwen | acoperirea |
|---|---|---|---|---|---|
| S15 #401 (e) | Bilca se află în ce raion? | În raionul Storojineț. | Bilca este o arie protejată … din raionul Storojineț, regiunea Cernăuți, … | 10 | 0,67 |
| S15 #407 (b2) | În ce oraș își are sediul Interpol? | În Lyon, Franța. | În Lyon. | 8 | 0,67 |
| S15 #415 (b2) | Ce companie a produs A Million Bid? | Vitagraph Company of America. | Vitagraph Company. | 9 | 0,50 |
| S4 #401 (c) | Are Ljubljana o populație de 279.653 de locuitori? | Da. | 279.653 de locuitori. | 8 | 0 (special „da”) |
| S4 #401 (c) | Este Barrie Barlow un muzician englez? | Da. | Barrie Barlow un muzician englez este un muzician englez, … | 9 | 0 (special „da”) |
| S4 #405 (a) | Când a venit pe lume Magda Alfredo Cazanga? | Pe 28 mai 1991. | În 1991. | 8 | 0,25 |
| S4 #406 (a) | (aceeași) | Pe 28 mai 1991. | În 1991. | 8 | 0,25 |
| S4 #407 (a) | (aceeași) | Pe 28 mai 1991. | În 1991. | 8 | 0,25 |
| S4 #415 (a) | (aceeași) | Pe 28 mai 1991. | În 1991. | 8 | 0,25 |

**Qwen greșit, verificator corect (4):**

| examen, model | întrebarea | referința | răspunsul elevului | nota Qwen | acoperirea |
|---|---|---|---|---|---|
| S15 #401 (b2) | Ce post are Nuri Șahin în echipă? | Mijlocaș. | Nuri Șahin în echipă este un fotbalist turc, care joacă pe post de mijlocaș … | 5 | 1,0 |
| S15 #407 (b2) | În ce oraș își are sediul Industria Vehiculelor Elene? | În Salonic. | În comuna Salonic. | 4 | 1,0 |
| S15 #415 (b2) | (aceeași) | În Salonic. | În județul Salonic. | 4 | 1,0 |
| S4 #415 (a) | Cine este regizorul filmului Neveste perfecte? | Bryan Forbes. | Bryan Forbes, scris de William Goldman, cu actorii … | 5 | 1,0 |

Ce se vede în ele:
- 4 din 9 sunt aceeași întrebare („În 1991” față de „Pe 28 mai 1991”): Qwen dă 8 unui răspuns incomplet (lipsesc ziua
  și luna); verificatorul îl dă greșit. Aici verificatorul e mai cinstit decât Qwen.
- 2 sunt „Da.” la care elevul n-a spus „da”, ci a repetat afirmația: Qwen le-a primit, verificatorul nu (după regulă).
- 3 sunt răspunsuri bune, dar mai scurte decât referința („În Lyon.”, „Vitagraph Company.”) sau cu altă prepoziție
  („din raionul” față de „În raionul”): aici verificatorul greșește prin asprime.
- Cele 4 inverse: răspunsul conține referința, dar cu ceva în plus greșit sau ciudat („comuna/județul Salonic”, o
  propoziție lungă, actori adăugați). Qwen le pedepsește; verificatorul nu se uită la ce e în plus.

## Verdictul, după regula de citire scrisă de supraveghetor înainte (pasul 4 din S16)

**Acordul împreună (S15 + S4), regula principală: 97,6 % (527/540) ≥ 90 % → „verificatorul poate înlocui pe Qwen”.**
Niciun model sub 85 % (regula principală). Semnalez doar: cu F1, #401 pe S15 ar avea 82,5 %, dar F1 nu decide.

Nu e antrenare, deci nu e o pre-înregistrare de închis; regula de citire din coadă a ținut loc de praguri.

## Ce n-am atins
`kronos/`, `module/examen_bpb.py`, paznicul, `unelte/examen_conversatie.py`, `docs/conversatie/`, datele de antrenare,
rezultatele vechi din `lucru/` (doar citite). Nicio descărcare, nicio instalare, placa nefolosită.

## Teste
`CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -m pytest`: **868 passed, 1 skipped** (3 min 35 s).

## Ce urmează
- După regula din coadă, S17 (E1, „întrebări născute de Kronos”) poate trece pe `aprobat` — asta o face supraveghetorul,
  nu eu. Ținta din coadă: noaptea 22→23 octombrie. Baseline-ul cu verificatorul e în tabelul de mai sus.
- De la Adrian nu aștept nimic acum; dacă vrea, se poate uita la cele 13 dezacorduri (mai ales „În 1991”, unde Qwen a
  fost îngăduitor).
