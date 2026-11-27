# Oracolul PyTorch pe datele reale ale lui Kronos — primii 10 pași, lot 2 și lot 6 (S141 A, 27 nov 2026)

Pentru ce e: motorul de antrenare din OS poate acum să verifice că, pornind din #513 și trăgând **aceleași
ferestre din aceleași date reale**, primii 10 pași dau aceleași pierderi ca PyTorch-ul din Windows.

## Rețeta, în cuvinte simple

- **Modelul:** #513 (`experiment_513.pt`, SHA-256 `605c4084f0a5db125b1e6c2c037b8e3d96abd17c1d62ec76efe439ecaba58b2c`),
  98.032.128 parametri. Neschimbat după rulări (SHA verificat înainte și după, la fiecare rulare).
- **Datele:** textul liniei #513 (amestecul W2), deja tăiat în simboluri cu tokenizerul `bpe_16384.json`
  (SHA-256 `2fcb9937a02ae3fb23723399d8fb2fdbecad96b697e0c626109d53232974b546`), pus în **27 de bucăți**
  `bucata_00000.bin` … `bucata_00026.bin` (fiecare 50.000.000 de simboluri, ultima mai mică; `int16`, little-endian).
  Lipite una după alta în ordine, ele dau **șirul întreg**: 1.341.190.791 de simboluri.
  - SHA-256 al lui `index.json`: `792e69dde8408f79d10e4b10b9bfb9ec932953b72e25112fada780b71362be29` (5.436 o)
  - SHA-256 al șirului întreg (cheia `sha256_tot` din `index.json`): `560863a976b8d36ab1515ce5121868f994f2e2959591525d0060c9e14fb5d4af`
- **Sămânța:** 1134.
- **Regula de tragere** (= `DateBucati.lot`): `g = torch.Generator().manual_seed(1134)`; la fiecare pas
  `pozitii = torch.randint(1341190791 − 512 − 1, (lot,), generator=g)`. Același generator merge mai departe de la un pas
  la altul (nu se re-seminează).
- **Fereastra:** 512 + 1 simboluri. De la poziția `p`: intrarea = `sir[p : p+512]`, ținta = `sir[p+1 : p+513]`.
  Poziția e în șirul întreg; bucata în care începe e `p // 50.000.000` (o fereastră poate trece peste granița a două bucăți).
- **Pasul:** AdamW (lr 5e-5, betas 0,9/0,999, eps 1e-8, weight_decay 0,1), rată constantă, fără încălzire, tăierea
  gradientului la 1,0 (norma din tabel = **înainte** de tăiere), dropout 0. Ordinea: zero_grad → înainte →
  cross_entropy (media pe toate pozițiile) → înapoi → tăiere → AdamW.step. bf16 = `torch.autocast(bfloat16)` doar în jurul
  trecerii înainte și al pierderii; greutățile, gradientele și AdamW rămân F32.
- **Unde:** procesor (PyTorch 2.14.1, 18 fire, Python 3.12.10, Windows 11). Detaliile complete: `reteta.json` din fiecare dosar.

## Ce e în dosar

Câte un dosar pentru fiecare rulare: `S141_l2_f32`, `S141_l6_f32`, `S141_l2_bf16`, `S141_l6_bf16`, fiecare cu:

- `rezultat.json` — pierderea, norma gradientului și timpul la fiecare pas;
- `reteta.json` — rețeta de mai sus, cu versiunile;
- `loturi.i64` — pozițiile trase: numere `int64` little-endian, **un rând = un pas**, cu `lot` numere pe rând
  (lot 2: 10 × 2 = 20 de numere, 160 o; lot 6: 10 × 6 = 60 de numere, 480 o). Fiecare număr e poziția `p` de început a
  unei ferestre în șirul întreg. F32 și bf16 au trase exact aceleași poziții (fișiere identice).

## Pozițiile ferestrelor (ca OS-ul să verifice cu `antrenare date … --lot`)

| lot | pasul 1 | pasul 10 |
|---|---|---|
| 2 | 279145862, 518214093 | 349038848, 311586698 |
| 6 | 279145862, 518214093, 915399206, 352686366, 165793673, 1052688074 | 827259421, 577202571, 686667938, 1242539425, 141568109, 1173008144 |

(La pasul 1, primele două poziții de la lot 6 sunt aceleași ca la lot 2 — același generator, aceeași sămânță; de la
pasul 2 încolo diferă, pentru că la lot 6 generatorul consumă 6 numere pe pas, nu 2.)

## Tabelul: lot 2

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

## Tabelul: lot 6

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

Valorile întregi (toate zecimalele) sunt în `rezultat.json`.

## Verificările făcute (S141 A.2)

- (a) lot 2 F32 = S140 F32 la pașii 1–10: diferența maximă **0** (≤ 1e-6 cerut); `loturi.i64` = primele 10 rânduri din S140 ✓
- (b) pasul 1 F32 lot 2 = **1,067867** ✓
- (c) lot 6, pasul 1: 1,0107 (F32) și 1,0108 (bf16), între 1 și 3 → modelul e încărcat ✓
- (d) nicio valoare NaN/inf ✓
- SHA-256 înainte = după la 22 de fișiere (#513, #651, #736, `kronos/`, `module/examen_bpb.py`, examenele, `index.json`) ✓

## Comenzile

```
python unelte/banc_antrenare.py --dispozitiv cpu --lot 2 512 --pasi 10 --precizie f32  --samanta 1134 --iesire lucru/banc/S141_l2_f32
python unelte/banc_antrenare.py --dispozitiv cpu --lot 6 512 --pasi 10 --precizie f32  --samanta 1134 --iesire lucru/banc/S141_l6_f32
python unelte/banc_antrenare.py --dispozitiv cpu --lot 2 512 --pasi 10 --precizie bf16 --samanta 1134 --iesire lucru/banc/S141_l2_bf16
python unelte/banc_antrenare.py --dispozitiv cpu --lot 6 512 --pasi 10 --precizie bf16 --samanta 1134 --iesire lucru/banc/S141_l6_bf16
```

(cu `CUDA_VISIBLE_DEVICES=-1`; unealta neschimbată.) Datele însele (bucățile) NU sunt în niciun repo.
