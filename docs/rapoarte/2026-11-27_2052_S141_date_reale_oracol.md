# S141 — Datele reale ale lui Kronos + oracolul PyTorch pe primii 10 pași (lot 2 și lot 6)

*Raport scris de executant, 27 nov 2026, 20:52. Partea A (procesor) e GATA. Partea B (copierea pe stick) încă nu e
făcută: o încep la o trecere următoare, între 07:00 și 23:00, cu semnul laboratorului.*

## Pe scurt

- **Oracolul e gata și e valid.** Am rulat primii 10 pași de antrenare ai lui #513 pe textul real (bucățile #651),
  la lot 2 și la lot 6, o dată exact (F32) și o dată „mixt” (bf16), pe procesor. Toate cele 4 verificări de validitate trec.
- Fișierul mic pentru hub: `docs/integrare_kronos/oracol_date_reale/` (23 KB: cele 4 rulări +
  `ORACOL_DATE_REALE.md` cu rețeta, tabelele și pozițiile ferestrelor). Supraveghetorul îl copiază în hub.
- Modelele, nucleul `kronos/`, examenul și `index.json` neatinse (SHA 22/22 identice). Placa n-a fost folosită.
- **1605 teste trec, 1 sărit** (înainte și după).

## Ce a rulat

Unealta existentă `unelte/banc_antrenare.py`, **neschimbată**, cu `CUDA_VISIBLE_DEVICES=-1`, sămânța 1134, 10 pași,
fereastra 512 (lanțul `lucru/cascada/S141_proba/s141.py`, rulat direct, ~5 min în total):

| rulare | început | durată | ms/pas (pașii 2–10) | simb/s |
|---|---|---|---|---|
| lot 2 F32 | 20:38:25 | 43,6 s | 1.645 | 622,7 |
| lot 6 F32 | 20:39:09 | 64,4 s | 4.227 | 726,8 |
| lot 2 bf16 | 20:40:13 | 71,0 s | 4.974 | 205,9 |
| lot 6 bf16 | 20:41:24 | 137,3 s | 11.617 | 264,5 |

Toate cu cod 0. (Pe procesor bf16 e de ~3× mai lent decât F32 aici — doar ca informație, nu era o întrebare.)

## Tabelul: pierderea și norma gradientului (pașii 1–10)

**Lot 2**

| pas | pierderea F32 | pierderea bf16 | norma gradientului F32 |
|---|---|---|---|
| 1 | 1,067867 | 1,067842 | 3,689983 |
| 2 | 0,595912 | 0,596395 | 3,585722 |
| 3 | 1,426418 | 1,426466 | 4,587664 |
| 4 | 0,846728 | 0,847437 | 3,650727 |
| 5 | 1,336231 | 1,336999 | 4,423136 |
| 6 | 2,682398 | 2,683548 | 5,459188 |
| 7 | 2,421172 | 2,420856 | 5,396073 |
| 8 | 1,150661 | 1,150282 | 4,688322 |
| 9 | 1,808648 | 1,808391 | 4,397144 |
| 10 | 1,136150 | 1,135774 | 3,898686 |

**Lot 6**

| pas | pierderea F32 | pierderea bf16 | norma gradientului F32 |
|---|---|---|---|
| 1 | 1,010662 | 1,010767 | 2,188078 |
| 2 | 1,582327 | 1,582952 | 2,598375 |
| 3 | 1,740796 | 1,741258 | 2,716188 |
| 4 | 1,539529 | 1,539679 | 2,580114 |
| 5 | 1,312736 | 1,311884 | 2,560980 |
| 6 | 1,756398 | 1,756287 | 2,884518 |
| 7 | 1,239821 | 1,239583 | 2,257900 |
| 8 | 0,985408 | 0,985283 | 2,189422 |
| 9 | 1,643523 | 1,643094 | 2,450834 |
| 10 | 1,941751 | 1,941571 | 2,871647 |

Diferența F32–bf16 rămâne sub 0,0012 la toți pașii (cea mai mare: lot 2, pasul 6, 0,00115) — în banda găsită la S140.

**Pozițiile ferestrelor** (în șirul întreg de 1.341.190.791 simboluri):

| lot | pasul 1 | pasul 10 |
|---|---|---|
| 2 | 279145862, 518214093 | 349038848, 311586698 |
| 6 | 279145862, 518214093, 915399206, 352686366, 165793673, 1052688074 | 827259421, 577202571, 686667938, 1242539425, 141568109, 1173008144 |

## Validitatea (pragurile din coadă, A.2)

| prag | cerut | ce a ieșit | |
|---|---|---|---|
| (a) lot 2 F32 = S140 F32, pașii 1–10 | diferență ≤ 1e-6; `loturi.i64` = primele 10 rânduri S140 | diferență **0**; loturi identice | ✓ |
| (b) pasul 1 F32 lot 2 | 1,067867 | **1,067867** (1,0678666830…) | ✓ |
| (c) lot 6, pasul 1 | între 1 și 3 | **1,0107** (F32), 1,0108 (bf16) | ✓ |
| (d) NaN/inf | niciuna | niciuna | ✓ |

**Verdict: VALID.** În plus: F32 și bf16 au tras exact aceleași poziții (fișierele `loturi.i64` identice, la ambele loturi),
iar fiecare rulare a verificat că #513 e neschimbat după ea.

## Amprentele (SHA-256)

- Înainte (`lucru/cascada/S141_proba/sha_inainte.json`) și după (`sha_dupa.json`): **22/22 identice** — #513, #651, #736,
  cele 10 fișiere din `kronos/`, `module/examen_bpb.py`, cele 7 examene din `docs/conversatie/`, plus
  `lucru/bucati/w2_amestec_be12/index.json` (`792e69dd…62be29`). Se schimbă doar spațiul liber pe C: (144,92 → 144,67 GB).
- Șirul întreg (`sha256_tot` din `index.json`): `560863a9…d4af`; tokenizerul `bpe_16384.json`: `2fcb9937…b546`.

## Testele

`CUDA_VISIBLE_DEVICES=-1 python -m pytest`: **1605 trec, 1 sărit** — și înainte de rulări (8 min 52 s), și după (7 min 56 s).

## Ce am scris / schimbat

- Nou: `docs/integrare_kronos/oracol_date_reale/` (4 dosare × `rezultat.json`, `loturi.i64`, `reteta.json` +
  `ORACOL_DATE_REALE.md`), 23.074 o pentru cele 12 fișiere copiate — sub limita de 2 MB.
- Acest raport; un rând în `plan/pentru_adrian.md`; starea S141 în coadă.
- Nimic din date (bucăți) în repo; nimic în `kronos/`, `module/`, `config/`, examen, paznic, jurnal; unealta neschimbată.
  Scripturile mele de lucru sunt în `lucru/cascada/S141_proba/` (nu intră în git).

## Ce urmează

- **S141 partea B** (copierea pe stick): la o trecere următoare, între 07:00 și 23:00, dacă nu există
  `porneste-test.txt`. Rezultatul (locul pe `E:`, ce s-a copiat, verificarea SHA) îl adaug în acest raport.
- Apoi S142 A (procesor), S142 B (placa) — în ordinea din coadă.

## Ce aștept de la Adrian

Nimic nou pentru S141. (Rămân cele din `plan/pentru_adrian.md`, mai ales `claude auth login` până pe 28 nov.)
