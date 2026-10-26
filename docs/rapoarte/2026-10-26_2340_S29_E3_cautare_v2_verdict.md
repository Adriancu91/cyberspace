# S29 — memoria E3 mai bună (C-21.1), pașii 5–7: **CONFIRMAT** (+11 puncte la k = 3), dar mult peste validare

Executantul, 26 octombrie 2026, 23:40. Sarcina S29 din `plan/coada.md`, doar pașii 5–7. Setul decisiv = **cele 100 de
întrebări S26** (varianta 1, aleasă de supraveghetor la 23:15). Pașii 0–3 sunt în
`docs/rapoarte/2026-10-26_2158_S29_E3_cautare_v2.md`.

## Pe scurt

- **Verdictul după pragurile C-21: CONFIRMAT.** Căutarea nouă (`rrf_reord`: rădăcini + RRF + reordonarea cu #438) aduce
  răspunsul în primele 3 bucăți la **83 din 100**, față de **72** la căutarea S25 simplă, în aceeași rulare: **+11 puncte**
  (pragul era ≥ +5). La k = 20 are **95 față de 94**, deci nu scade.
- **Mă așteptam la INFIRMAT.** Pe validarea de 1.000 de întrebări câștigul fusese doar +1,2 puncte. Rezultatul pe cele 100
  e mult peste. Cred că efectul adevărat e mai mic decât +11 (detalii mai jos).
- **Pentru E3 contează:** răspunsul ajunge în bucățile care chiar încap în context la **72 din 100, față de 64**. La S27,
  #438 a răspuns corect la 60 din cele 64.
- **Placa:** o singură rulare de 36 de secunde, cel mult ~1.070 MB și 45 °C. Totul a rămas departe de limite.
- **Teste:** 930 trec, 1 sărit.

## Ce am făcut

1. **23:29 — `in_lucru`** în coadă (commit 496e6b5).
2. **Pasul 5 — pre-înregistrarea** `docs/preinregistrari/2026-10-26_E3_cautare_v2.md`. Conține:
   - pragul C-21 cuvânt cu cuvânt;
   - baza: S25 simplă din aceeași rulare;
   - cele 4 lucruri spuse cinstit dinainte (setul folosit deja la S26/S27, #415 a văzut `text_v3`, validarea +1,2 → aștept
     INFIRMAT, zgomotul pe 100);
   - așteptările mele în cifre.

   Tot la pasul 5 am scris comanda nouă `examen` în `unelte/e3_reordonare.py`, cu 2 teste noi:
   - verdictul pe praguri;
   - o rulare mică fără placă: verifică amprenta și refuză a doua rulare.

   Totul a fost urcat în **commit-ul c381094, la 23:35:21, ÎNAINTE de măsurare**.
3. **Pasul 6 — măsurarea, o singură dată:** `unelte/e3_reordonare.py examen --judecator 438`, pornită prin cascadă la
   23:35:30, gata la 23:36:06, cod 0. Ieșirea e în `lucru/e3/examen_s29.json`. Amprenta listei S26 (`3501f307…f523`) a fost
   verificată înainte.
4. **Pasul 7:** testele, închiderea pre-înregistrării cu verdictul, acest raport.

## Cifrele (cele 100 S26, potrivirea S16, judecătorul #438)

| varianta | k = 1 | k = 2 | k = 3 | k = 5 | k = 20 | încap 1 / 2 / 3 | răspunsul în bucățile care încap |
|---|---|---|---|---|---|---|---|
| S25 simplă (`s25`, baza) | 55 | 66 | **72** | 80 | **94** | 17 / 64 / 19 | 64 |
| + RRF (`rrf`) | 53 | 65 | 72 | 80 | 95 | 17 / 62 / 21 | 63 |
| + reordonare (`s25_reord`) | 58 | 75 | 84 | 86 | 94 | 19 / 65 / 16 | 73 |
| **RRF + reordonare (`rrf_reord`, aleasa)** | **57** | **74** | **83** | **86** | **95** | 19 / 67 / 14 | **72** |

- **Baza** a ieșit exact ca la S26 (55 / 72 / 80 / 94), deci căutarea n-a schimbat nimic.
- **Față de S25 la k = 3**, `rrf_reord` repară 14 întrebări și strică 3. Cele 3 stricate sunt „Ce este Palatul Camerei
  Deputaților?” (locul 1 → 7), „Ce este Comunitatea maronită din Liban?” (2 → 5) și „Cine este Anda Saltelechi?” (2 → 4).
- **RRF singur nu face nimic la k = 3 aici** (0 reparate, 0 stricate). Tot câștigul vine din **reordonare**. `s25_reord`
  (doar reordonarea, fără rădăcini) are chiar cu 1 mai mult (84). Alegerea pe validare dintre ele s-a făcut la diferențe
  mici (782 față de 778).
- **Pe tipuri, la k = 3:**
  - definiții („Ce este X?”): **32 → 40 din 54**;
  - an: 1 → 3 din 4;
  - regizat: 6 → 7 din 8;
  - născut: 14 → 14 din 15;
  - restul: neschimbat (toate erau deja găsite).
- **Normalizat față de nenormalizat:** aceeași ordine la toate 100, ca pe validare.
- **Timpi pe întrebare (mediane):** căutarea 0,091 s, judecătorul 0,138 s (maxim 0,56 s și 0,32 s).
- **Memoria:** pe placă 732 MB alocați de PyTorch, cel mult ~1.070 MB văzuți de nvidia-smi, cel mult 45 °C. RAM: 1,1 GB.

## Verdictul (strict după pre-înregistrare)

**CONFIRMAT:** Δ3 = 83 − 72 = **+11 ≥ +5**, iar k = 20: 95 ≥ 94.

Ce trebuie spus la fel de clar:
- **+11 pe 100 e mult peste ce a arătat validarea:** +1,2 pe 1.000, +2,4 pe eșantionul 2048. Cu 100 de întrebări, o
  întrebare înseamnă un punct. Cred că efectul adevărat e între aceste cifre, mai aproape de câteva puncte decât de +11.
- **O explicație probabilă:** setul S26 are **54 % definiții**, iar câștigul e aproape tot la definiții. Nu am numărat încă
  amestecul de tipuri din validare (se poate face pe procesor, în câteva minute, din `validare_s29.json`).
- **Contaminarea:** #415, deci și #438, a văzut cele 100 de întrebări în `text_v3`, cu textul lor, și le poate „recunoaște”.
  Validarea vine tot din `text_v3`, deci are același risc, și acolo câștigul a fost mic. Setul S26 a mai fost măsurat la S26
  și S27, dar nimic din S29 nu s-a ales pe el.
- **O greșeală a mea:** în antetul pre-înregistrării am scris „23:35–23:45” / „scrisa 23:40”. De fapt am scris-o între
  ~23:30 și 23:35. Dovada că a fost înaintea măsurării e în Git: c381094 la 23:35:21, măsurarea la 23:35:30. N-am schimbat
  antetul după măsurare; greșeala e notată în „Ce a ieșit”.

## Teste

`CUDA_VISIBLE_DEVICES=-1 python -m pytest`: **930 trec, 1 sărit** (23:39, după măsurare).

La prima rulare, înainte de măsurare, `teste/test_interfata.py::test_fila_din_text_pe_server` a picat o dată cu
„ConnectionAborted” (serverul local de probă). Rulat din nou singur: 37/37 trec. Apoi toată suita a trecut. N-am schimbat
nimic la el. Pare un test care pică uneori la întâmplare și merită urmărit.

## Ce n-am atins

`kronos/`, examenul, paznicul, jurnalul, `text_v3`, listele S26/S27, `lucru/e3/index.sqlite` (doar citire),
`unelte/verificator_text.py`, modelele. Nimic antrenat, descărcat sau instalat. Nimic nou în interfață și nimic din
`lucru/e3/` în Git.

## Ce urmează

- **S29 e `gata`.** Următoarea în coadă e **S30** (Muon + răcire lungă: codul, testul pe procesor și proba de 10 minute pe
  placă). Pornește la o verificare următoare a cozii, cu placa liberă.
- **Propun** (decide supraveghetorul sau Adrian):
  1. o numărătoare pe procesor, de câteva minute: amestecul de tipuri din validare și câștigul pe tip acolo, ca să vedem
     dacă +11 vine din definiții;
  2. mai departe, ca E3 să citească cu căutarea nouă: examenul S27 refăcut cu `rrf_reord` (#438 răspunde din bucățile
     reordonate). Plafonul urcă de la 64 la 72, deci ar trebui să urce și răspunsurile corecte (azi 60).
- **Portul `cautare`** (în `kronos/`) rămâne decizia ta, ca în raportul de la 21:58.

## Fișiere

- **În Git:**
  - `unelte/e3_reordonare.py` (comanda `examen`, `verdict_s29`);
  - `teste/test_e3_reordonare.py` (+2 teste);
  - pre-înregistrarea închisă;
  - acest raport.
- **Nu în Git:**
  - `lucru/e3/examen_s29.json` (toate locurile, pe întrebare; nu se mai rulează);
  - jurnalul `lucru/cascada/S29.log`;
  - scripturile de citire din `lucru/cascada/S29_proba/`.
