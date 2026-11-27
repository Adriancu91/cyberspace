# S141 — Datele reale ale lui Kronos + oracolul PyTorch pe primii 10 pași (lot 2 și lot 6)

*Raport scris de executant, 27 nov 2026, 20:52 (partea A). Completat la 21:16 cu partea B (copierea pe stick), tot GATA:
vezi secțiunea „Partea B” de la sfârșit.*

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

- ~~S141 partea B~~ — făcută la 21:00–21:06, vezi mai jos.
- Apoi S142 A (procesor), S142 B (placa) — în ordinea din coadă.

## Ce aștept de la Adrian

Nimic nou pentru S141. (Rămân cele din `plan/pentru_adrian.md`, mai ales `claude auth login` până pe 28 nov.)

---

## Partea B — datele reale pe stick (executant, 27 nov 2026, 21:16) — GATA

**Pe scurt: stickul avea loc din belșug; cele 27 de bucăți, `index.json` și tokenizerul sunt acum în
`E:\antrenare\date\`, neschimbate, și fiecare a fost citită înapoi de pe stick cu SHA-256 corect, din prima.
Nimic din ce era deja pe stick n-a fost atins. Placa n-a fost folosită.**

### Protocolul laboratorului

- La 20:59 **nu exista** `C:\Kronos\cyber-test\porneste-test.txt` (ultimul test OS folosit: `porneste-test-folosit-20261127-194153.txt`).
- 20:59: semnul `laborator-ocupat.txt` = „OCUPAT — S141 copiere pe stick”, început 20:59, sfârșit estimat 21:44.
- 21:07: semnul rescris „LIBER” (copierea încheiată la 21:06).

### Stickul și locul (pasul B.2–B.3)

- `E:` e stickul OS-ului: există `E:\EFI\BOOT\` și `E:\BOOT\LIMINE\limine.conf` (doar citite).
- Sistemul de fișiere: **FAT32** (fiecare fișier de copiat are cel mult 100 MB, deci limita FAT32 de 4 GB nu contează).
- Mărimea stickului: 32.195.477.504 o (~32,2 GB); folosit înainte 486.490.112 o.
- **Liber înainte: 31.708.987.392 o (~30.240 MB).**
- **Necesar: 2.892.318.259 o (~2.758 MB)** = 27 bucăți 2.682.381.582 o + `index.json` 5.436 o + `bpe_16384.json`
  216.041 o + rezerva 200 MB. → **ajunge** (lipsesc 0 MB).
- `E:\antrenare\date\` nu exista înainte (l-am creat eu).

### Ce s-a copiat (pasul B.4)

- Unealta: un script mic al meu, `lucru/cascada/S141_proba/stick.py` (Python `shutil.copyfile`; refuză dacă ținta există
  deja sau dacă nu ajunge locul; nu scrie peste nimic), pornit prin cascadă (`cascada.py porneste S141`, procesul 21100,
  jurnal `lucru/cascada/S141.log`, rezultatul pe fișier în `lucru/cascada/S141_proba/stick_copiere.json`).
- Interval: **21:00:01 → 21:06:32 (6 min 31 s)**, cod 0.
- Copiate: **29 de fișiere, 2.682.603.059 o (~2,68 GB)**: `bucata_00000.bin` … `bucata_00026.bin`, `index.json`,
  `bpe_16384.json`. Câte ~13–22 s pe bucată de 100 MB.

### Verificarea de pe stick

- După fiecare copiere, scriptul a citit fișierul **înapoi de pe `E:`** și i-a calculat SHA-256:
  - cele 27 de bucăți față de `sha256` din `index.json`: **27/27 corecte**;
  - `index.json` față de originalul de pe C: (`792e69dd…62be29`): corect;
  - `bpe_16384.json` față de `2fcb9937…b546`: corect.
- **Nicio a doua încercare** n-a fost nevoie (niciun fișier greșit, nimic șters).
- O precizare cinstită: Windows poate servi citirea înapoi din memoria lui (cache), nu neapărat de pe cipul stickului.
  Verificarea finală adevărată o face OS-ul când citește bucățile de pe stick și compară cu `index.json`.

### Spațiul rămas (pasul B.5)

- **Liber după: 29.026.107.392 o (~27.681 MB).** Diferența față de înainte: 2.682.880.000 o (fișierele + rotunjirea la clustere FAT32).

### Testele (după B)

`CUDA_VISIBLE_DEVICES=-1 python -m pytest`: **1605 trec, 1 sărit** (8 min 4 s).

### Ce n-am făcut (granițele B)

- Nimic din date în vreun repo (nici aici, nici în hub); nimic mutat, modificat sau șters de pe stick din ce era deja acolo.
- Placa, `kronos/`, examenul, paznicul, jurnalul, `config/`, `module/` — neatinse; unealta `banc_antrenare.py` neschimbată;
  nimic descărcat sau instalat. S131 rămâne pe pauză (C-156).

### Ce urmează

- **S141 e `gata` (A și B).** Pentru OS: datele sunt în `E:\antrenare\date\` (aceeași structură ca
  `lucru/bucati/w2_amestec_be12/`, cu `index.json` lângă bucăți, plus tokenizerul); oracolul în
  `docs/integrare_kronos/oracol_date_reale/`.
- Următoarea din coadă: **S142 A** (procesor, unealta `viteza_scris_kv.py`), apoi S142 B (placa, 07:00–23:00, cu pre-înregistrarea).

### Ce aștept de la Adrian

Nimic nou pentru S141 B. Rămân cele din `plan/pentru_adrian.md` (mai ales `claude auth login` până pe 28 nov).
