# Pre-înregistrare: S55 — Kronos-Cod, tokenizerul pe cod (32.768 de simboluri)

<!-- scrisa: 2026-10-31T14:34 -->
*Scrisă la 2026-10-31 14:34, înainte de antrenarea tokenizerului, de Claude Code (executantul), fără să mă fi uitat la
vreo măsurătoare a lui. Singura probă făcută înainte: viteza numărării bucăților pe ~80 MB din partea de antrenare
(10 s, 536.189 bucăți diferite) — nimic din validare, nicio antrenare. După pornire, textul de mai jos nu se mai schimbă;
la închidere se adaugă doar „Ce a ieșit” și „Verdictul”.*

## Ce este și ce NU este

- Prima piesă a liniei noi **Kronos-Cod**: un tokenizer doar pentru cod (Python / Rust / C). Aprobat de Adrian (C-45,
  31 oct 13:50, „da tokenizer cod”); pașii și pragurile de la supraveghetor (sarcina S55 din `plan/coada.md`, 14:15).
- **NU** e o antrenare de model, **NU** folosește placa, **NU** atinge linia română (#477, tokenizerul w2 de 16.384),
  **NU** deschide setul ascuns (`lucru/kronos_cod/examen_ascuns/`, suma `90fc64cd…3749`, verificată la început și la
  sfârșit). Nimic descărcat, nimic instalat, nimic șters.

## Datele

- Sursa: `lucru/kronos_cod/complet/cod.jsonl` (S46): 548.361 de fișiere, din care **494.973 curate** (3,87 GB) — cele din
  `aproape_duplicate.json` nu intră.
- **Minus toată lista S53** (`lucru/kronos_cod/scurgere/fisiere_de_exclus.txt`, 4.245 de rânduri, din care 3.821 curate,
  ~118 MB). Indicele unui fișier = numărul rândului nevid din cod.jsonl, numărat de la 0 (ca la S53).
- **Validarea (regula exactă):** se calculează SHA-256 pe textul fișierului (UTF-8); dacă **primul octet < 3**, fișierul e
  în validare (3/256 ≈ 1,17 %). Validarea nu intră la antrenarea tokenizerului și nu va intra nici la antrenarea modelului.
- **Eșantionul tokenizerului:** fișierele de antrenare cu **al doilea octet** al aceleiași sume **< 70** (70/256 ≈ 27 %,
  ~1 GB). Bucățile care apar o singură dată în eșantion nu intră la numărătoare.
- **Amestecul pe limbaje** = cât e în date, fără reponderare. După surse (rezumatul S46, partea curată): ~44 % Python
  (PyPI 1,55 GB + depozite git 0,15 GB), ~53 % Rust (crates 1,98 GB + depozite 0,06 GB), ~3 % C (FreeBSD 0,12 GB +
  depozite 0,01 GB). Procentele exacte pe câmpul „limbaj” (un pachet PyPI sau un crate poate avea și fișiere .c/.h) se
  scriu în raport din `impartire.json`.

## Tokenizerul

- BPE pe octeți (256 de simboluri de bază, deci orice text se poate scrie), **32.768 de simboluri** (încape în uint16),
  `module/tokenizer_bpe.py` cu regulile noi **„cod”** (variantă nouă; „gpt2” și „ws” neschimbate — test pe vectorii KGR1):
  - sfârșitul de rând e bucată separată (și mai multe la rând, și `\r\n`);
  - indentarea de la început de rând e bucată separată; **1–16 spații și 1–8 tab-uri sunt simboluri întregi, puse în
    vocabular de la început** (22 de lipiri fixe); un șir mai lung se taie în bucăți de 16 spații / 8 tab-uri;
  - identificatorul e bucată întreagă (`__init__`, `snake_case`), cu spațiul dinainte; numerele în grupe de ≤ 3 cifre.
- **Simbolurile speciale:** `<|endoftext|>` = **sfârșit de fișier** (32.764), apoi `<|python|>`, `<|rust|>`, `<|c|>`
  (rezervate pentru etichete de limbaj; nefolosite acum). Un `<|endoftext|>` scris în textul unui fișier rămâne text.
- Se antrenează **o singură dată** → `lucru/kronos_cod/tokenizer/bpe_cod_32768.json` (+ `.sha256`).

## Ce rulează

`python -X utf8 -m unelte.kronos_cod.tokenizer_cod tot --procese 12 --limita-ore 9`, prin
`unelte/cascada.py porneste S55`: împărțirea + numărătoarea + antrenarea → măsurătorile pe validare → (doar la BUN/SLAB)
tokenizarea întregului set în `lucru/kronos_cod/simboluri/` (uint16, sfârșit de fișier între fișiere, blocuri de 5.000 de
rânduri, reluare de unde a rămas, oprire curată la limita de ore sau sub 40 GB liberi pe C:).

## Cum se măsoară (pe validarea de ~1,17 %, NU pe setul ascuns)

- **(a)** octeți pe simbol (octeții UTF-8 ai textului / simbolurile, fără sfârșitul de fișier), pe tot și separat pe
  Python / Rust / C;
- **(b)** aceeași măsură cu tokenizerul w2 (`date/ws/bpe_16384.json`), pe aceleași fișiere, ca reper;
  „față de w2” = (a) / (b) − 1;
- **(c)** codare → decodare identică **octet cu octet**, pe 100 % din fișierele de validare;
- **(d)** câte simboluri are tot setul de antrenare tokenizat (din `simboluri/rezumat.json`).

## Pragurile (copiate neschimbate din sarcină)

- **BUN** = (c) 100 % identic **și** (a) pe tot ≥ 3,0 **și** (a) cu ≥ 15 % mai mult decât (b) pe aceleași fișiere;
- **SLAB** = (c) 100 %, dar una din celelalte două condiții nu e atinsă → raportez și propun 16.384 sau 49.152 (nu le fac);
- **STRICAT** = (c) sub 100 % → mă opresc, setul nu se tokenizează.

## Așteptările mele în cifre (înainte de rulare)

- (c): 100 % (BPE pe octeți cu tabelul de octeți complet nu are cum să piardă ceva).
- (a) pe tot: **~3,6** (cred între 3,2 și 4,0); Python ~3,8, Rust ~3,5, C ~3,3.
- (b) w2: **~2,8** pe tot (w2 a văzut doar ~15 % cod și taie indentarea în spații mici) → față de w2 **~+28 %**.
- Verdictul așteptat: **BUN**.
- (d): ~3,7 GB de antrenare / ~3,6 ≈ **~1,0 miliarde** de simboluri.
- Timpul: numărătoarea ~5–10 min, antrenarea BPE ~0,5–2 ore, măsurarea ~10 min, tokenizarea ~1–3 ore; RAM sub 30 GB.

## Să nu uit

- Suma setului ascuns la început și la sfârșit (unealta o verifică; o scriu în raport).
- Nimic din `lucru/` în Git; datele din `lucru/kronos_cod/complet/` doar citite.
- Dacă un pas pică de 2 ori la rând cu aceeași eroare: `oprit`, eroarea în raport.
- Propunerea pentru prima antrenare pe placă o scriu în raport, **nu o pornesc**.

## Ce a ieșit

*Adăugat la 2026-10-31 15:04, din jurnalul Kronos (lucru/jurnal/experimente.jsonl) și din jurnalul CONTINUUM pe bune. Verdictul se scrie dedesubt.*

Niciun experiment Kronos în perioada asta.

Niciun ciclu CONTINUUM pe bune în perioada asta.

Cifrele (din `lucru/kronos_cod/tokenizer/masurare.json`, `impartire.json`, `lucru/kronos_cod/simboluri/rezumat.json`;
rularea 14:39:19 → 14:57:13, cod 0):

- **(c)** codare → decodare identică: **5.686 / 5.686 fișiere de validare (100 %)**.
- **(a)** octeți pe simbol, tokenizerul de cod: **tot 3,4617**; Python 3,7179; Rust 3,3499; C 3,0954.
- **(b)** tokenizerul w2 pe aceleași fișiere: tot 2,8344; Python 3,2107; Rust 2,6892; C 2,3425.
- față de w2: **tot +22,1 %**; Python +15,8 %; Rust +24,6 %; C +32,1 %.
- **(d)** setul de antrenare tokenizat: **1.080.537.399 de simboluri** (485.466 fișiere); validarea 12.619.825 (5.686).
- Timpul: numărătoarea 37 s, antrenarea BPE 768 s, măsurarea 27 s, tokenizarea 241 s (în total ~18 minute).
- Setul ascuns: `90fc64cd…3749` la început și la sfârșit (neschimbat).

Față de așteptări: (a) 3,46 față de ~3,6 (în intervalul 3,2–4,0, dar mai jos pe fiecare limbaj); w2 2,83 ≈ 2,8; câștigul
+22 % față de ~+28 %; (d) 1,08 miliarde ≈ ~1,0; timpul mult mai scurt decât credeam (18 min față de 2–5 ore).

## Verdictul

**BUN** — strict după praguri: (c) 100 % ✓; (a) pe tot 3,46 ≥ 3,0 ✓; față de w2 +22,1 % ≥ 15 % ✓. Setul s-a tokenizat.
De știut: Python trece doar la limită (+15,8 %), dar pragul e pe tot, nu pe limbaj.
