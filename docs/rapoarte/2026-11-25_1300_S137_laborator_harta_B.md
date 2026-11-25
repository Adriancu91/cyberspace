# S137 B — laboratorul, „harta greutății textului”: verdictul (H) față de S135 (0)

*Scris de executant (cascada) la 25 nov 2026, 13:00. Partea A: `docs/rapoarte/2026-11-25_0005_S137_laborator_harta.md`.*

## Pe scurt

**Verdict: „CÂȘTIG STRÂMB” — nu e câștig.** Cu harta, româna curată (judecătorul) a ieșit mult mai bună: **1,5085** față de
**1,5343** la (0) (−0,0258, de 2,6 ori pragul de 0,010). Dar examenul-martor `examen_bpb` a urcat la **0,5485** față de
0,5394 (+0,0091, peste toleranța de +0,005). După regula ta, asta înseamnă că harta a mutat modelul spre o parte a
textului — nu se numără ca un câștig. Proba e validă.

## Ce a rulat

- Comanda: `.venv/Scripts/python -X utf8 unelte/laborator_harta.py --minute 60 --dispozitiv cuda --iesire lucru/laborator/S137_H`,
  pornită prin cascadă la 11:29:46 (procesul 15904), terminată la 12:34:47 cu **cod 0**, fără oprire de la paznic.
- Exact rețeta S135 (0) (aceeași rețea ca #513, de la zero, sămânța 1163, doar textul W2, 60 min pe ceas); singura
  diferență: din minutul 5 ferestrele de text vin din harta „ce se mai poate învăța” (`module/date_harta.py`).
- Înainte de pornire: testul OS os-423 terminat, `porneste-test.txt` lipsea, placa 458 MB / 36 °C, `laborator-ocupat.txt`
  = „OCUPAT”. După: `laborator-ocupat.txt` rescris „LIBER” (ștergerea îmi e refuzată — te rog șterge-l de mână).
- Examenele: aceleași ca la S135 (funcția `examene` din `unelte/laborator_trepte.py`), ~4,6 min.
- Modelul e **doar** în `lucru/laborator/S137_H/model.pt` (nu în jurnal, interfață sau export). Tot acolo: `rezultat.json`,
  `progres.csv`, `harta_final.json`.

## Cifrele

| | S135 (0) | (H) harta | Δ (H) − (0) | ghicirea mea |
|---|---|---|---|---|
| **română curat (`romana_bpb`, judecătorul)** | 1,5343 | **1,5085** | **−0,0258** | ~1,530 |
| — Wikipedia / web / cărți | 1,3644 / 1,6337 / 1,6316 | 1,3343 / 1,6088 / 1,6102 | −0,030 / −0,025 / −0,021 | |
| **`examen_bpb` (martorul)** | 0,5394 | **0,5485** | **+0,0091** | ~0,545 |
| R1 instrucțiuni (nu decide) | 42,07 | 43,33 | +1,26 | ~40 |
| R1 ascuns / vechi | 46,47 / 52,54 | 48,60 / 55,87 | +2,13 / +3,33 | |
| simboluri văzute | 140.820.480 | 139.542.528 | −0,91 % | ~138 mil. |
| pași (din care cu harta) | 2.865 | 2.839 (2.602) | −26 | ~2.810 |
| pierderea la ultimul pas | 2,0012 | 1,9173 | −0,084 | |
| placa max (nvidia-smi) | 5.952 MB / 65 °C | 6.005 MB / 65 °C | | ~5.960 MB |

Româna e mai bună pe toate trei părțile (Wikipedia, web, cărți), nu doar pe una.

**Cât s-a tras din fiecare sfert** (regiunile împărțite după pierderea lui #513; sfertul 1 = textul cel mai ușor), toată ora:
61.976 / 64.947 / 70.148 / 75.473 ferestre = **22,7 % / 23,8 % / 25,7 % / 27,7 %**. Harta a tras mai des textul greu și mai
rar pe cel ușor, dar puțin: cel mai greu / cel mai ușor = 1,22× (sub pragul de 2× din pre-înregistrare → harta a rămas
aproape de uniform). Atenție: în proba de procesor din A se vedea invers (sfertul ușor puțin mai des) — pe placă, după o
oră, direcția s-a întors.

## Verdictul, strict după pragurile pre-înregistrate (`docs/preinregistrari/2026-11-25_laborator_harta.md`, închisă)

- română(H) 1,5085 ≤ 1,5243 → partea de română a lui CÂȘTIGĂ e îndeplinită;
- `examen_bpb`(H) 0,5485 > 0,5444 → a doua condiție a lui CÂȘTIGĂ **nu** e îndeplinită;
- regula „română câștigă dar `examen_bpb` urcă cu > 0,005” → **„câștig strâmb”** — nu e câștig;
- validitate: (0) validă (1,5343 < 2,0); (H) 6.005 MB / 65 °C (sub 7.000 MB și 83 °C); SHA-256 înainte = după pe toate
  cele 21 de fișiere (#513, #651, #736, `kronos/*.py`, `module/examen_bpb.py`, `docs/conversatie/examen*.json`;
  `lucru/cascada/S137_proba/sha_inainte_B.json` vs `sha_dupa_B.json`); simbolurile 139,54 mil. în fereastra 133,78–147,86 mil.
  → **probă validă**.

Ghicirile mele: verdictul „LA FEL” — **greșit** (româna a câștigat mult mai mult); `examen_bpb` puțin mai rău — corect;
simbolurile și memoria — corecte.

De știut cinstit: e o singură rulare; nu știm cât diferă două rulări identice (asta ar spune (0′), neaprobată). La S135
și la S137 româna și martorul au mers în direcții opuse — de aceea (0′) ar fi utilă înainte de alte probe.

## Testele

`CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -m pytest`: **1590 trec, 1 sărit** (8 min 39 s). Nicio schimbare de cod în
partea B.

## Ce am mai scris

- pre-înregistrarea închisă cu „Ce a ieșit” + „Verdictul”;
- rândul (H) în al doilea tabel din `docs/integrare_kronos/BANC_ANTRENARE.md`;
- un rând sus în `plan/pentru_adrian.md`;
- coada: S137 stare B → `gata`.

## Ce urmează / ce aștept de la tine

- După regula din coadă: (H) nu a câștigat curat → ne oprim aici cu harta; supraveghetorul nu propune combinarea.
- Decizia e la tine (prin supraveghetor): dacă vrei, „da (0′)” — aceeași oră cu altă sămânță, ca să știm dacă diferențele
  de 0,01–0,03 sunt peste zgomot (ar lămuri și S135, și S137).
- Te rog: șterge de mână `C:\Kronos\cyber-test\laborator-ocupat.txt` (acum scrie „LIBER”).
- Copia locală a repo-ului stă tot „în mijlocul rebase-ului” din 17 nov: `git -c core.editor=true rebase --continue` în
  `C:\Kronos\cyberspace`.
