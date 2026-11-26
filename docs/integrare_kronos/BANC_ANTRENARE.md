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
| (H) harta (S137) | 0 / 60 (harta din min 5) | 139.542.528 | 2.839 (2.602 cu harta) | **1,5085** | 0,5485 | 43,33 | 6.005 MB, 65 °C | **CÂȘTIG STRÂMB** (română −0,0258, dar `examen_bpb` +0,0091 > +0,005) — nu e câștig |
| (P) portarul (S139) | 0 / 60 (portar la straturile 2, 4, …, 12, capacitate 50 %) | 149.520.384 | 3.042 | **1,5286** | 0,5426 | 26,44 | 5.997 MB, 65 °C | **LA FEL** (română −0,0057, între 1,5243 și 1,5443); viteza min 5–45 **41.527 simb/s = 1,062×** (0) 39.115 → „și mai rapid” |

- Judecătorul (româna curată) dă PIERDE; martorul `examen_bpb` și R1 sunt mai bune la (1) (−0,025, +18 puncte), dar nu
  decid. Pre-înregistrarea: `docs/preinregistrari/2026-11-25_laborator_trepte_k4.md`.
- (H) (S137, unealta `unelte/laborator_harta.py`, ieșirea `lucru/laborator/S137_H/`): ferestre trase pe sferturi după `ref`
  #513 (ușor → greu) 22,7 / 23,8 / 25,7 / 27,7 %. Pre-înregistrarea: `docs/preinregistrari/2026-11-25_laborator_harta.md`.
- (P) (S139, unealta `unelte/laborator_portar.py`, modulul `module/model_portar.py`, ieșirea `lucru/laborator/S139_P/`):
  examenele în modul cauzal (`sigmoid(r) > 0,5`); partea aleasă la română 38,9 % (validă: 35–65 %), potrivirea cu top-k
  88–89 %. Informativ top-k (nu decide): română 1,5229, `examen_bpb` 0,5370. Pre-înregistrarea:
  `docs/preinregistrari/2026-11-25_laborator_portar.md`.

## S140 — F32 vs bf16, 300 de pași (26 nov 2026, procesor, aceleași loturi)

Din #513, `unelte/banc_antrenare.py` neschimbată, `--dispozitiv cpu --lot 2 512 --pasi 300 --samanta 1134`, o dată
`--precizie f32` și o dată `--precizie bf16` (autocast bf16 la trecerea înainte și la pierdere; greutățile, gradientele și
AdamW în F32). AdamW lr 5e-5 constantă, tăierea 1,0. Loturile identice: SHA-256 `loturi.i64` = `82023c5d…3737` la amândouă.
Ieșirile: `lucru/banc/S140_f32/`, `lucru/banc/S140_bf16/` (`rezultat.json` cu toți pașii). Norma = înainte de tăiere.

| pas | pierdere F32 | pierdere bf16 | bf16 − F32 | relativ | norma gradient F32 | norma bf16 | ms/pas F32 | ms/pas bf16 |
|---|---|---|---|---|---|---|---|---|
| 1 | 1,067867 | 1,067842 | −2,43e-5 | 0,002 % | 3,690 | 3,690 | 1.428 | 2.872 |
| 10 | 1,136150 | 1,135774 | −3,76e-4 | 0,033 % | 3,899 | 3,888 | 1.284 | 2.661 |
| 50 | 2,266573 | 2,267512 | +9,39e-4 | 0,041 % | 4,909 | 4,902 | 1.339 | 2.915 |
| 100 | 1,625381 | 1,626824 | +1,44e-3 | 0,089 % | 4,766 | 4,794 | 1.335 | 2.659 |
| 200 | 2,206031 | 2,207622 | +1,59e-3 | 0,072 % | 4,978 | 4,986 | 1.310 | 2.678 |
| 300 | 0,894853 | 0,897521 | +2,67e-3 | 0,298 % | 3,593 | 3,609 | 1.275 | 2.646 |

- **Diferența maximă pe pașii 1–300: 5,11e-2 la pasul 291** (F32 1,2271, bf16 1,1760; 4,16 %). Maximul pe bucăți:
  1–50 1,42e-3 (pas 21) · 51–100 5,69e-3 (93) · 101–150 7,79e-3 (101) · 151–200 8,40e-3 (181) · 201–250 3,55e-2 (208) ·
  251–300 5,11e-2 (291). Pași cu |bf16 − F32| > 1e-3: 123 din 300; > 7,2e-3: 12 din 300 (toți după pasul 100).
- Media |bf16 − F32|: pașii 1–50 4,55e-4 · 101–150 1,20e-3 · 251–300 3,73e-3 · 1–300 1,93e-3.
- Media pierderii pe 251–300: F32 1,66611, bf16 1,66466 (−0,087 %). Pe 1–300: 1,67876 / 1,67884.
- Norma gradientului: la cei 6 pași diferă cu 0,01–0,57 %, dar la 40 din 300 de pași cu > 1 % (cel mai mult la pasul 275:
  5,09 vs 10,84). Tăierea la 1,0 face pasul AdamW mai puțin sensibil la normă decât arată cifra.
- ms/pas (media pașilor 2–300): F32 1.311 (781 simb/s), bf16 2.673 (383 simb/s) — bf16 de 2,04× mai lent pe procesor.
- Banda propusă pentru OS (pragul (c), |bf16 − F32| la pașii 1/10/50/100/200/300):
  **[2,4e-5; 3,8e-4; 9,4e-4; 1,4e-3; 1,6e-3; 2,7e-3]**. Atenție: e o singură pereche de rulări și diferența sare mult de la
  un pas la altul (până la 5,1e-2); banda la 6 pași e mică doar fiindcă pașii aceia au ieșit liniștiți. bf16 (8 biți de
  mantisă) e mai grosier decât f16 (11 biți) din OS.
- Verdict (pre-înregistrarea `docs/preinregistrari/2026-11-25_banc_f32_vs_bf16_300.md`): (a) valid; (b) **„bf16 nu strică
  învățarea pe 300 de pași”** (−0,087 %, în ±1 %); (c) banda de mai sus; (d) SHA înainte = după (21/21).
