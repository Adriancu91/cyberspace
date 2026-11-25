# Bancul de antrenare #513 (S134) — aceiași pași în PyTorch și în OS

Scopul (Adrian, hub `DECIZII.md`, 24 nov 2026 14:15): o măsurătoare cinstită Windows/PyTorch ↔ OS-ul nostru, în
aceleași condiții — același model (#513), același lot, aceeași precizie, aceleași date, același număr de pași. Partea
Windows o face unealta `unelte/banc_antrenare.py` (S134). Fișa completează `FISA_ANTRENARE.md` (S133, antrenarea reală)
și `PAS_DE_AUR.md` (S132, un lot fix, procesor).

## Rețeta, pe scurt

| Ce | Cum | Unde se vede |
|---|---|---|
| modelul de pornire | **#513** (linia `w2_romana_r1`), `lucru/stocare/modele/experiment_513.pt`, SHA-256 `605c4084f0a5db12…` (întreg în `reteta.json`); 98.032.128 parametri; doar citit, niciun model salvat | `reteta.json` → `model` |
| datele | șirul de simboluri al **textului** liniei #513 (amestecul W2, `date/ws/amestec/antrenare.txt` codificat cu `date/ws/bpe_16384.json`), tăiat în bucăți: `lucru/bucati/w2_amestec_be12/` (27 bucăți int16 little-endian, 1.341.190.791 simboluri, SHA-256 al șirului `560863a976b8d36ab1515ce5121868f994f2e2959591525d0060c9e14fb5d4af`; `index.json` → `sursa` = `lucru/cache/simboluri_be12c6d88276d79d.pt`, cache-ul liniei #513) | `reteta.json` → `date` |
| ce lipsește față de antrenarea reală | la #513 lotul avea și 45 % conversație și 5 % hrană (`FISA_ANTRENARE.md` §2); aici doar textul, ca OS-ul să tragă exact aceleași ferestre | — |
| sămânța | **1134** | `--samanta` |
| cum se trag loturile | exact ca `DateBucati.lot`: `g = torch.Generator().manual_seed(1134)` (MT19937, pe procesor); la fiecare pas `pozitii = torch.randint(1.341.190.791 − context − 1, (lot,), generator=g)`; fereastra de la p: intrarea = `sir[p : p+context]`, ținta = `sir[p+1 : p+context+1]`; un lot nou la fiecare pas | `loturi.i64` = pozițiile [pași, lot], int64 little-endian, pe rânduri |
| pasul | `zero_grad` → înainte → `cross_entropy(logits.float(), ținte)` (media pe **toate** pozițiile) → înapoi → `clip_grad_norm_(1,0)` → `AdamW.step()`; **AdamW la fiecare lot, fără adunare de loturi** | `reteta.json` → `pas` |
| AdamW | lr 5e-5 (constantă, fără încălzire), beta 0,9 / 0,999, eps 1e-8, scăderea greutăților 0,1, fără amsgrad; verificat pe optimizatorul pe care îl face #513 însuși | `pas.optimizator_citit_din_model` |
| dropout | 0 (verificat) | — |
| precizia | `f32`, sau `bf16` = `torch.autocast(bfloat16)` în jurul trecerii înainte și al pierderii, exact ca la antrenarea reală (`ModelGPT._autocast`); greutățile, gradientele și AdamW rămân în F32 | `--precizie` |
| ce se măsoară | pe fiecare pas: pierderea (înainte de actualizare), norma gradientului (înainte de tăiere), ms (de la `zero_grad` până după `step`, cu `torch.cuda.synchronize()` la ambele capete pe placă; loturile sunt deja pe dispozitiv, tragerea lor nu intră în timp), simb/s = lot × context ÷ timp. Pasul 1 (încălzirea) separat; media pe pașii 2..N. Pe placă: `max_memory_allocated`, `max_memory_reserved` și maximul `nvidia-smi` | `rezultat.json` |
| paza plăcii | peste 7.000 MB sau 83 °C → varianta se oprește singură, cu „nu încape în 7 GB” (fără recalcul sau alte trucuri) | `rezultat.json` → `oprit` |

## Comenzile

Fiecare variantă scrie într-un dosar nou (unealta refuză un dosar care există).

    # procesor (proba)
    .venv/Scripts/python -X utf8 unelte/banc_antrenare.py --dispozitiv cpu --lot 2 512 --pasi 3 --precizie f32 --iesire <dosar>
    .venv/Scripts/python -X utf8 unelte/banc_antrenare.py --dispozitiv cpu --lot 2 512 --pasi 3 --precizie bf16 --iesire <dosar>

    # placa (partea B, doar după „da”-ul lui Adrian), în ordinea asta:
    .venv/Scripts/python -X utf8 unelte/banc_antrenare.py --dispozitiv cuda --lot 2 512  --pasi 20 --precizie f32  --iesire lucru/banc_antrenare/v1_2x512_f32
    .venv/Scripts/python -X utf8 unelte/banc_antrenare.py --dispozitiv cuda --lot 2 512  --pasi 20 --precizie bf16 --iesire lucru/banc_antrenare/v2_2x512_bf16
    .venv/Scripts/python -X utf8 unelte/banc_antrenare.py --dispozitiv cuda --lot 12 512 --pasi 20 --precizie bf16 --iesire lucru/banc_antrenare/v3_12x512_bf16
    .venv/Scripts/python -X utf8 unelte/banc_antrenare.py --dispozitiv cuda --lot 12 512 --pasi 20 --precizie f32  --iesire lucru/banc_antrenare/v4_12x512_f32

Pentru OS: aceleași poziții din `loturi.i64` (sau aceeași sămânță prin `antrenare date … --lot`), aceleași greutăți de
pornire (#513), același pas. Fiind aceleași loturi, se compară și pierderea pas cu pas, nu doar viteza.

## Tabelul (Windows / PyTorch, RTX 3070 Ti 8 GB) — de completat la partea B

| # | lot × context | precizie | ms/pas (2..20) | simb/s (2..20) | pierderea pas 1 | pas 10 | pas 20 | memoria plăcii (alocat max / nvidia-smi max) |
|---|---|---|---|---|---|---|---|---|
| 1 | 2 × 512 | F32 | | | | | | |
| 2 | 2 × 512 | bf16 | | | | | | |
| 3 | 12 × 512 | bf16 | | | | | | |
| 4 | 12 × 512 | F32 | | | | | | |

## Proba pe procesor (24 nov 2026, partea A — doar ca să se vadă că merge)

Procesorul workstation-ului, PyTorch 2.14.1+cu132, 18 fire, `CUDA_VISIBLE_DEVICES=-1`, 3 pași, lot 2 × 512.

| precizie | pas | pierderea | norma gradientului | ms | simb/s |
|---|---|---|---|---|---|
| F32 | 1 | 1,067867 | 3,690 | 1.859,8 | 550,6 |
| F32 | 2 | 0,595912 | 3,586 | 1.596,9 | 641,2 |
| F32 | 3 | 1,426418 | 4,588 | 1.639,6 | 624,5 |
| F32 | media 2..3 | | | **1.618,3** | **632,9** |
| bf16 | 1 | 1,067842 | 3,690 | 5.148,4 | 198,9 |
| bf16 | 2 | 0,596395 | 3,586 | 4.823,5 | 212,3 |
| bf16 | 3 | 1,426466 | 4,586 | 4.896,1 | 209,1 |
| bf16 | media 2..3 | | | **4.859,8** | **210,7** |

- Pozițiile loturilor (`loturi.i64`, 3 × 2) au SHA-256 `c156e1cc9fb12878…`, aceleași în ambele rulări.
- bf16 față de F32 la pasul 1: 1,067842 vs 1,067867 (0,002 %). Pe procesor bf16 e de ~3 ori mai lent (procesorul n-are
  calcul bf16 nativ) — cifra de viteză care contează e cea de pe placă.
- **Pierderea ~1,07, nu „3–4”:** modelul e încărcat bine (ar fi fost ~9,70 = ln 16.384 dacă nu), dar amestecul W2 are
  multe povești TinyStories în engleză, pe care #513 le știe foarte bine (ambele ferestre ale pasului 1 sunt TinyStories).
  Pe 32 de ferestre la sorți (sămânța 777, fără antrenare) pierderea medie e 1,66, între 0,75 și 3,29.

## Al doilea tabel: laboratorul treptelor S135 (25 nov 2026, RTX 3070 Ti 8 GB, câte 60 de minute de la zero)

Aceeași rețea ca #513 (98.032.128 parametri), sămânța 1163, doar textul W2 (`lucru/bucati/w2_amestec_be12`), lot 12 × 512 ×
adunare 8 = 49.152 simboluri pe pas, AdamW, bf16, rata de vârf 6e-4 (încălzire 3 min, răcire minutele 45–60).
Unealta: `unelte/laborator_trepte.py`; rezultatele în `lucru/laborator/S135_<rețetă>/rezultat.json`.

| rețetă | minute bucăți / simboluri | simboluri văzute | pași | română curat | `examen_bpb` | R1 instrucțiuni | memoria maximă (nvidia-smi) | verdict |
|---|---|---|---|---|---|---|---|---|
| (0) rețeta de azi | 0 / 60 | 140.820.480 | 2.865 | **1,5343** | 0,5394 | 42,07 | 5.952 MB, 65 °C | baza (validă: < 2,0) |
| (1) bucăți K = 4 | 40 / 20 | 338.903.040 | 6.895 (5.940 + 955) | **1,5538** | 0,5144 | 60,12 | 6.018 MB, 65 °C | **PIERDE** (+0,0195 ≥ +0,010) |

- Judecătorul (româna curată) dă PIERDE; martorul `examen_bpb` și R1 sunt mai bune la (1) (−0,025, +18 puncte), dar nu
  decid. Pre-înregistrarea: `docs/preinregistrari/2026-11-25_laborator_trepte_k4.md`.
