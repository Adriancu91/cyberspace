# S139 B — laboratorul, „portarul” (amestecul de adâncimi): verdictul (P) față de S135 (0)

*Scris de executant (cascada) la 25 nov 2026, 16:29. Partea A: `docs/rapoarte/2026-11-25_1448_S139_laborator_portar.md`.*

## Pe scurt

**Verdict: „LA FEL”.** Cu portarul, româna curată (judecătorul) a ieșit **1,5286** față de **1,5343** la (0) — cu 0,0057
mai bună, dar sub pragul de 0,010 cerut pentru „câștigă”. Martorul `examen_bpb` 0,5426 (+0,0032, în toleranță).
**Viteza: 1,062×** (41.527 față de 39.115 simboluri/s în minutele 5–45) → peste pragul de 1,05×, deci „și mai rapid”;
viteza nu schimbă verdictul. Proba e validă. După regula din coadă: (P) nu câștigă → **ne oprim cu portarul**, fără fișa
pentru Cyber-GPU.

## Ce a rulat

- Proba de 3 minute (15:00, `lucru/cascada/S139_proba/placa_3min_P(.log)`, `--fara-examene`): 5.971 MB / 63 °C,
  ~41.250 simb/s, eroarea 7,86 → 5,94; partea aleasă cauzal atunci doar ~22 % (selectorul abia începuse să învețe).
- Comanda: `.venv/Scripts/python -X utf8 unelte/laborator_portar.py --minute 60 --dispozitiv cuda --iesire lucru/laborator/S139_P`,
  pornită prin cascadă la 15:03:05 (procesul 22852), terminată la 16:09:26 cu **cod 0**, fără oprire de la paznic.
- La pornire: fără `porneste-test.txt`, `laborator-ocupat.txt` = „OCUPAT”. Unealta a notat placa la începutul ei
  1.027 MB / 47 °C (după proba de 3 min; citirea e făcută de unealtă după ce și-a deschis placa — la (0) a notat la fel
  1.008 MB, la (H) 1.029 MB).
  După: `laborator-ocupat.txt` rescris „LIBER” (ștergerea îmi e refuzată — te rog șterge-l de mână).
- Exact rețeta S135 (0) (aceeași rețea ca #513, de la zero, sămânța 1163, doar textul W2, 60 min pe ceas); singura
  diferență: portarul la straturile 2, 4, 6, 8, 10, 12 (capacitate 50 % la antrenare, top-k pe text; BCE 0,01;
  4.614 parametri în plus, 98.036.742 în total).
- Examenele: aceleași ca la S135 (funcția `examene` din `unelte/laborator_trepte.py`), **în modul cauzal**
  (`sigmoid(r) > 0,5`, simbol cu simbol), ~6 min.
- Modelul e **doar** în `lucru/laborator/S139_P/model.pt` (nu în jurnal, interfață sau export). Tot acolo:
  `rezultat.json`, `progres.csv`. Logul: `lucru/cascada/S139.log`.

## Cifrele

| | S135 (0) | (P) portarul | Δ (P) − (0) | ghicirea mea |
|---|---|---|---|---|
| **română curat (`romana_bpb`, judecătorul)** | 1,5343 | **1,5286** | **−0,0057** | ~1,545 |
| — Wikipedia / web / cărți | 1,3644 / 1,6337 / 1,6316 | 1,3551 / 1,6288 / 1,6293 | −0,009 / −0,005 / −0,002 | |
| **`examen_bpb` (martorul)** | 0,5394 | **0,5426** | **+0,0032** | ~0,545 |
| R1 instrucțiuni (nu decide) | 42,07 | 26,44 | −15,63 | ~38 (28–48) |
| R1 ascuns / vechi | 46,47 / 52,54 | 34,40 / 45,40 | −12,07 / −7,14 | |
| **simboluri/s, minutele 5–45** | 39.114,9 | **41.527,1** | **1,062×** | ~43.000 (1,10×) |
| simboluri văzute | 140.820.480 | 149.520.384 | +6,2 % | ~153 mil. |
| pași | 2.865 | 3.042 | +177 | ~3.110 |
| pierderea la ultimul pas | 2,0012 | 1,9343 | −0,067 | |
| placa max (nvidia-smi) | 5.952 MB / 65 °C | 5.997 MB / 65 °C | +45 MB | ~5.800 MB |

Româna e puțin mai bună pe toate trei părțile, dar diferențele sunt mici (0,002–0,009).

**Portarul, în cifre:**

- partea de simboluri alese în modul cauzal la examenul de română: **38,9 %** (pe toate examenele 40,0 %) — în
  intervalul de validitate 35–65 %, dar sub 50 %: la examen selectorul lasă să treacă mai puțin decât la antrenare;
- a doua trecere a examenului de română (cea care numără partea aleasă) dă exact aceeași notă: 1,52856 = 1,52856;
- potrivirea alegerii cauzale cu top-k: **88,3 %** la sfârșitul antrenării (BCE 0,247), **89,1 %** la examen — peste
  75 %, deci selectorul a învățat să prezică top-k;
- **informativ, modul top-k** (se uită la viitor, NU e cinstit, NU decide): română 1,5229, `examen_bpb` 0,5370.
- memoria PyTorch maximă: 5.023 MB alocați / 5.320 MB rezervați.

## Verdictul, strict după pragurile pre-înregistrate (`docs/preinregistrari/2026-11-25_laborator_portar.md`, închisă)

- validitate: partea aleasă cauzal 38,9 % ∈ [35 %, 65 %]; 5.997 MB / 65 °C (sub 7.000 MB și 83 °C); SHA-256 înainte = după
  pe toate cele 21 de fișiere (#513, #651, #736, `kronos/*.py`, `module/examen_bpb.py`, `docs/conversatie/examen*.json`;
  `lucru/cascada/S139_proba/sha_inainte.json` vs `sha_dupa_B.json`); nicio NaN → **probă validă**;
- română(P) 1,5286 > 1,5243 și < 1,5443 → **LA FEL**;
- viteza 1,062× ≥ 1,05× → **„și mai rapid”** (nu schimbă verdictul);
- R1 se măsoară, nu decide.

Ghicirile mele: verdictul „LA FEL” — corect (dar înclinarea spre PIERDE a fost greșită: româna a ieșit puțin mai bună);
viteza 1,06× — în intervalul ghicit, dar sub 1,10×; memoria — mai mare decât ghicisem; partea aleasă cauzal 38,9 % — sub
intervalul meu 40–60 %; R1 — mult sub ce ghicisem.

De știut cinstit:

- e o singură rulare; nu știm cât diferă două rulări identice (asta ar spune (0′), neaprobată) — −0,006 la română poate
  fi și întâmplare;
- R1 instrucțiuni a scăzut mult (26 față de 42). Nu decide, dar e cea mai mare diferență din probă; o explicație
  posibilă (neverificată): la examen trec doar ~39 % din simboluri prin straturile cu portar, deci mai puțin calcul decât
  la antrenare.

## Testele

`CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -m pytest`: **1605 trec, 1 sărit** (8 min 7 s). Nicio schimbare de cod în partea B.

## Ce am mai scris

- pre-înregistrarea închisă cu „Ce a ieșit” + tabel + „Verdictul”;
- rândul (P) în al doilea tabel din `docs/integrare_kronos/BANC_ANTRENARE.md` (cu simboluri/s);
- un rând sus în `plan/pentru_adrian.md`;
- coada: S139 stare B → `gata`.

## Ce urmează / ce aștept de la tine

- După regula din coadă: (P) nu câștigă → ne oprim aici cu portarul; nu scriu `PORTAR_FISA.md`.
- Toate trei probele laboratorului (bucăți, hartă, portar) au dat diferențe de 0,006–0,026 la română. Decizia e la tine
  (prin supraveghetor): „da (0′)” — aceeași oră cu altă sămânță, ca să știm cât e zgomotul.
- Te rog: șterge de mână `C:\Kronos\cyber-test\laborator-ocupat.txt` (acum scrie „LIBER”).
- Copia locală a repo-ului stă tot „în mijlocul rebase-ului” din 17 nov: `git -c core.editor=true rebase --continue` în
  `C:\Kronos\cyberspace`.
