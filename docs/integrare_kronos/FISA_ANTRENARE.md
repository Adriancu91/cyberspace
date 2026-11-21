# Fișa de antrenare Kronos — pentru motorul de antrenare propriu din OS

S133 (comanda lui Adrian C-162, 21 nov 2026). **Doar citit**: cod, configurări, jurnalul Kronos, fișierele din `lucru/`.
Nimic rulat pe placă, nicio antrenare, niciun examen nou, nicio măsurătoare nouă de viteză (pauza C-156).
Completează `PAS_DE_AUR.md` (S132): acolo e un pas „curat” (F32, procesor, un lot, fără adunare); aici e tot ce face
**pasul adevărat** de antrenare în plus.

Fiecare cifră e marcată:
- **MĂSURAT** = scrisă în jurnal / log / fișier de rezultate în timpul rulării (cu fișierul și rândul);
- **DEDUS** = socotită acum din cifre MĂSURATE (socoteala e scrisă);
- **CITIT** = citit acum dintr-un fișier care există (mărime, SHA, conținut), nu e o măsurătoare de rulare;
- **NU E ÎN JURNAL** = nu există nicăieri; n-am măsurat-o (ar cere „da”-ul lui Adrian).

Cele două linii:

| | linia lui #513 | linia lui #651 |
|---|---|---|
| linia (nume) | `w2_romana_r1` | `w2_mare_24zc` |
| sarcina / data | S76b, 4→5 nov 2026, 23:32–04:56 | S111, 16 nov 2026, 04:10–11:19 |
| configurarea | `config/conv_w2_romana_r1.toml` | `config/conv_w2_mare_24zc.toml` |
| comanda | `python unelte/antrenare_lunga.py --config config/conv_w2_romana_r1.toml --ore 5 --porneste-din 477` (`lucru/cascada/S76b.log` rândul 3) | `python unelte/antrenare_recalcul.py --config config/conv_w2_mare_24zc.toml --ore 7 --porneste-din 641 --pauza 5` (`lucru/cascada/S111_0410.log` rândul 2) |
| clasa modelului | `module.model_muon:ModelGPTConversatieMuon` | `module.model_gpt_cod:ModelGPTCod` (= aceeași buclă; vezi mai jos) |
| porturi „date” | `module.date_amestec:DateAmestec` (text, simbolurile din `lucru/cache`) | `module.date_bucati:DateBucati` (simboluri gata făcute, `lucru/bucati/w2_amestec_be12`) |
| modelul final | #513 = ora 5 din 5 | #651 = ora 7 din 7 |
| fișa din jurnal | `lucru/jurnal/experimente.jsonl` rândul **513** | `lucru/jurnal/experimente.jsonl` rândul **651** |

## 1. Viteza de antrenare în Windows / PyTorch pe RTX 3070 Ti

O „oră” = un experiment Kronos cu bugetul de 3.600 s de antrenare (`buget_antrenare_secunde = 3600`).
„Lot” (= „pas” în jurnal) = o trecere înainte + înapoi pe `lot × 512` simboluri; **pasul optimizatorului** vine o dată la
`adunare_loturi` loturi.

| Cifra | #513 (ora 5, `w2_romana_r1`) | #651 (ora 7, `w2_mare_24zc`) | Marcaj și dovada |
|---|---:|---:|---|
| arhitectura | 12 straturi, 12 capete, n_emb 768, context 512, vocabular 16.384 | 24 straturi, 12 capete, n_emb 768, context 512, vocabular 16.384 | MĂSURAT — rândul 513 / 651, `"setari"`; `rezultat.json` rândurile 5–8 |
| parametri | 98.032.128 | 183.086.592 | MĂSURAT — rândul 513 / 651, `"parametri"` |
| lot × context | 12 × 512 | 6 × 512 | MĂSURAT — rândul 513 / 651, `"lot"`, `"context"` |
| adunarea gradientului | 8 loturi | 16 loturi | MĂSURAT — rândul 513 / 651, `"adunare_loturi"` |
| simboluri pe pasul optimizatorului | 49.152 (12 × 512 × 8) | 49.152 (6 × 512 × 16) | DEDUS (lot × context × adunare) |
| secunde de antrenare în oră | 3.600,04 | 3.600,18 | MĂSURAT — `"secunde_bucla"` |
| loturi în oră | 23.007 | 18.176 | MĂSURAT — `"pasi"`; și `lucru/w2_romana_r1/rezultat.json` rândul 144, `lucru/w2_mare_24zc/rezultat.json` rândul 140 |
| pași ai optimizatorului în oră | 2.875 (+ 7 loturi aruncate la sfârșit) | 1.136 (0 aruncate) | MĂSURAT — `"pasi_optimizator"`, `"loturi_aruncate"` |
| simboluri în oră | 141.355.008 | 55.836.672 | MĂSURAT — `rezultat.json` rândul 147 / 143 (scrise de `antrenare_lunga.py` ca loturi × lot × context, rândul 210) |
| **loturi / s** | **6,391** | **5,049** | DEDUS (loturi ÷ secunde) |
| **pași ai optimizatorului / s** | **0,7986** (1,252 s pe pas) | **0,3155** (3,169 s pe pas) | DEDUS |
| **simboluri / s** (toate pozițiile, și cele mascate) | **39.265** | **15.509** | DEDUS (simboluri ÷ secunde) |
| ms pe lot | 156,5 | 198,1 | DEDUS |
| celelalte ore ale liniei | 22.993–23.010 loturi/oră | 18.165–18.431 loturi/oră | MĂSURAT — `rezultat.json` (toate orele) |
| memoria PyTorch, vârf alocat | 5.187 MB | 5.186 MB | MĂSURAT — `"consum"."memorie_gpu_max_mb"` = `torch.cuda.max_memory_allocated()` (`module/rulare_locala.py` rândul 62) |
| memoria PyTorch, vârf rezervat | 5.374 MB | 5.730 MB | MĂSURAT — `"memorie_rezervata_mb"` = `torch.cuda.max_memory_reserved()` |
| plafonul PyTorch pe placă | fără plafon | 5.800 MB (fracția 0,708) | MĂSURAT — `S111_0410.log` rândul 3 |
| memoria plăcii după nvidia-smi, maxim pe toată rularea (antrenare + examene + tot ce rula pe placă) | 5.936 MB | 6.922 MB | MĂSURAT — `lucru/w2_romana_r1/placa_20261104_2332.csv` rândul 1818; `lucru/w2_mare_24zc/placa_20261116_0410.csv` rândul 2482 (citire la 10 s) |
| temperatura maximă | 63 °C | 64 °C | MĂSURAT — aceleași CSV, rândul 142 / 114 |
| încărcarea plăcii (medie, cât memoria > 3 GB) | 97,9 % | 96,8 % | DEDUS din aceleași CSV |
| precizia | bf16 (autocast) la calcul; greutăți, gradiente, AdamW în F32 | la fel | din cod (secțiunea 2); `"dispozitiv": "cuda"` MĂSURAT |
| recalculul activărilor (checkpoint pe strat) | **nu** | **da**, toate cele 24 de straturi (~30 % mai încet, după `unelte/antrenare_recalcul.py` rândul 5) | MĂSURAT — `S111_0410.log` rândul 9 |
| durata unei ore întregi (antrenare + test rapid + examen + salvare) | 3.741,8 s | 3.657,7 s | MĂSURAT — `"durata_totala_secunde"` |
| viteza fără recalcul pentru 24 de straturi | — | NU E ÎN JURNAL | |
| viteza pe pas separată pe înainte / înapoi / optimizator | NU E ÎN JURNAL | NU E ÎN JURNAL | |
| viteza în F32 curat (fără bf16) | NU E ÎN JURNAL | NU E ÎN JURNAL | |

**Cifra de bătut (pe scurt):** linia #513 face **~39.300 simboluri/s** (0,80 pași de optimizator/s cu 49.152 simboluri
pe pas); linia #651 face **~15.500 simboluri/s** (0,32 pași/s), cu recalculul activărilor pornit ca să încapă în ~5,8 GB.
Ambele DEDUSE din cifrele MĂSURATE de mai sus (o oră întreagă de antrenare, nu o probă scurtă).

Atenție la comparație: „simboluri/s” socotește toate cele 512 poziții ale fiecărei ferestre; la ferestrele de
conversație pierderea se socotește doar pe o parte din ele (secțiunea 2.4), dar calculul înainte/înapoi se face pe toate.

## 2. Pasul adevărat față de „pasul de aur”

Bucla e aceeași la ambele linii: `ModelGPTCod` (linia #651) e o subclasă a `ModelGPTConversatieMuon` și, cu date fără
`simboluri_antrenare()` (cum e `DateBucati`, care are `sir_antrenare()`), merge pe exact aceeași cale
(`module/model_gpt_cod.py` rândurile 80–82). Lanțul de clase: `ModelGPT` (`module/model_gpt.py`) → `ModelGPTContinuu`
(`module/model_continuu.py`) → `ModelGPTConversatie` (`module/model_conversatie.py`) → `ModelGPTConversatieMuon`
(`module/model_muon.py`) → `ModelGPTCod` (`module/model_gpt_cod.py`).

| Ce | Pasul de aur (S132) | Pasul adevărat (liniile #513 și #651) | Unde în cod |
|---|---|---|---|
| bucla | 10 pași, un lot fix | până la 3.600 s pe oră; loturi trase la sorți | `ModelGPTConversatie.antreneaza`, `module/model_conversatie.py` rândurile 99–158 |
| adunarea gradientului | nu | 8 (#513) / 16 (#651) loturi; pierderea fiecărui lot ÷ `adunare_loturi`, apoi `backward()`; `zero_grad(set_to_none=True)` la primul lot din grup | `ModelGPTConversatieMuon._pas_adunat`, `module/model_muon.py` rândurile 189–208 |
| loturile rămase la sfârșitul orei | — | dacă ora se termină în mijlocul unui grup, gradientul adunat se **aruncă** (ora următoare reîncarcă starea salvată) | idem; `"loturi_aruncate"` în jurnal |
| tăierea gradientului | (ca în S132, înainte de pas) | `clip_grad_norm_(parametri, 1.0)` — norma L2 a tuturor gradientelor (tensorul legat `emb_token`/`cap` socotit o dată), **după** adunarea celor 8/16 loturi, înainte de pas | `module/model_muon.py` rândul 204 |
| optimizatorul | SGD / AdamW | `torch.optim.AdamW(retea.parameters(), lr=rata_invatare, weight_decay=0.1)`; betas (0,9; 0,999), eps 1e-8, amsgrad nu, `foreach`/`fused` implicite (None) — CITIT din `lucru/w2_mare_24zc/gpt.pt` | `ModelGPTConversatieMuon._optimizator_nou`, `module/model_muon.py` rândul 157 |
| scăderea greutăților | — | 0,1 pe **toți** parametrii (și LayerNorm, bias, încorporări), decuplată: `p ← p·(1 − lr·0,1)` înainte de pasul Adam | idem (un singur grup de parametri) |
| rata de vârf | — | #513: 5e-5; #651: 1e-5 | configurările |
| încălzirea | — | `rata × min(1, (pasi_total_anteriori + i + 1) / incalzire_pasi)`; **socotită în loturi**, nu în pași de optimizator: 100 loturi (#513) = ~12,5 pași; 1.000 loturi (#651) = ~62,5 pași. Linia pornește din #477/#641 cu `pasi_total = 0`, deci încălzirea se face o dată, în prima oră | `ModelGPT.rata_acum`, `module/model_gpt.py` rândurile 393–402; starea de pornire `unelte/antrenare_lunga.py` rândurile 365–387 |
| programul ratei | — | cosinus de la `rata` la `fractie_rata_finala × rata`; cu `fractie_rata_finala = 1,0` (ambele linii) **cosinusul nu schimbă nimic** (rata rămâne fixă); apoi **răcirea finală**: în ultimele 25 % din `durata_scaderii_secunde`, rata scade în linie dreaptă până la 0: `rata × (1 − parcurs)`, `parcurs = min(1, (progres − 0,75) / 0,25)` | `module/model_gpt.py` rândurile 393–402; `ModelGPTConversatieMuon.rata_acum`, `module/model_muon.py` rândurile 181–187 |
| „progresul” ratei | — | **după ceas, nu după pași**: `progres = (minute_total × 60 + secunde_de_la_începutul_orei) / durata_scaderii_secunde`; #513: 18.000 s (5 h), #651: 25.200 s (7 h). Verificare: #651 la sfârșitul orei 6, progres 0,857 → rata 1e-5 × 0,571 = 5,714e-6 = `rata_la_final` MĂSURAT (`rezultat.json` rândul 129) | `ModelGPT._progres`, `module/model_gpt.py` rândurile 383–391 |
| când se aplică rata | — | rata se scrie în optimizator la **fiecare lot**; contează cea scrisă la ultimul lot din grup (pasul vine atunci) | `module/model_conversatie.py` rândurile 135–139 |
| pierderea | cross-entropy pe tot lotul | cross-entropy cu `ignore_index = −100`, **media pe simbolurile nemascate din lot**; logits trecute în F32 (`logits.float()`) înainte de pierdere | `_pas_mascat`, `module/model_muon.py` rândurile 210–215 |
| precizia | F32, procesor | pe placă: `torch.autocast("cuda", dtype=torch.bfloat16)` la înainte (straturile liniare și atenția în bf16 după regulile autocast; LayerNorm și pierderea în F32), **fără GradScaler**; greutățile, gradientele și stările AdamW în F32 | `ModelGPT._autocast`, `module/model_gpt.py` rândurile 323–326 |
| dropout | 0 | 0 (`"dropout": 0.0` în `setari`, CITIT din `gpt.pt` și din `experiment_*.pt`) | `module/model_gpt.py` rândurile 75–79 |
| recalculul activărilor | nu | doar #651: fiecare strat în `torch.utils.checkpoint(..., use_reentrant=False)` la antrenare; matematic aceleași rezultate (dropout 0) | `unelte/antrenare_recalcul.py` rândurile 34–78 |
| atenția | | `nn.MultiheadAttention` (q/k/v într-o matrice `in_proj_weight` 3·768 × 768, cu bias), mască cauzală `triu(diagonal=1)`, pre-LN, GELU în MLP (4 × 768), încorporarea de ieșire **legată** de cea de intrare, fără bias la ieșire | `module/model_gpt.py` rândurile 71–132 |
| sămânța loturilor | fixă | un `torch.Generator` pe procesor, nou la fiecare oră: sămânța = `samanta` dacă `pasi_total == 0`, altfel `samanta × 1.000.003 + pasi_total` (#513: `samanta = 0`; #651: `samanta = 24`) | `ModelGPTContinuu._samanta_loturi`, `module/model_continuu.py` rândurile 165–167 |
| ora de antrenare în Kronos | — | fiecare oră: testul rapid (≤ 2 s, nu salvează), antrenarea 3.600 s, examenul, apoi salvarea stării; ora următoare reîncarcă starea de pe disc | `kronos/orchestrator.py`; `module/model_continuu.py` rândurile 185–212 |
| paza memoriei | — | doar #651: înainte de fiecare test rapid `gc.collect()` + `empty_cache()` și oprire dacă nvidia-smi > 6.700 MB | `unelte/antrenare_recalcul.py` rândurile 106–169 |

### 2.4 Ce simboluri contează în pierdere (conversația)

Fiecare lot e făcut din trei feluri de ferestre de 512 simboluri (`module/model_conversatie.py` rândurile 117–134):

1. **Conversație** — `fractie_conversatie = 0,45` din lot. Perechi întrebare → răspuns luate la sorți (cu repetare) din
   fișierul `.jsonl` și lipite una după alta până la 513 simboluri; fereastra începe mereu la începutul unei perechi.
   Întrebarea se scrie `Întrebare: …⏎Răspuns:` (cu `Text: …⏎` în față, dacă perechea are text), răspunsul
   ` <răspuns>⏎<|endoftext|>⏎`; cele două se codifică **separat**. Țintele simbolurilor din întrebare sunt −100 (nu
   intră în pierdere); contează doar răspunsul și `<|endoftext|>` de după el (rândurile 31–39 și 73–86).
2. **Hrană** — `fractie_hrana` din lot (#513: 0,05, poveștile cu fapte `date/fapte/povesti.txt`; #651: 0,30,
   `date/ws/hrana_fineweb_rest/antrenare.txt`). Ferestre la poziții la sorți, toate țintele contează.
3. **Text** — restul lotului, din amestecul W2 (1.341.190.791 simboluri). Ferestre la poziții la sorți, toate țintele contează.

Câte ferestre din fiecare: `k = floor(f × lot × (pas+1)) − floor(f × lot × pas)` (pas = `pasi_total_anteriori + i`),
deci media e exact fracția; ordinea în lot: întâi conversația, apoi hrana, apoi textul; pozițiile
`torch.randint(lungime − 512 − 1, (k,), generator=g)`, intrarea `s[p : p+512]`, ținta `s[p+1 : p+513]`.

| Ferestre într-o oră | #513 (lot 12) | #651 (lot 6) | Marcaj |
|---|---:|---:|---|
| conversație | 124.238 | 49.076 | MĂSURAT — `"ferestre"` în rândul 513 / 651 |
| hrană | 13.804 | 32.717 | MĂSURAT |
| text | 138.042 | 27.263 | MĂSURAT |
| perechi în fișierul de conversație | 23.251 | 26.596 | MĂSURAT — `"perechi_conversatie"` |

## 3. Datele

| | #513 | #651 | Marcaj |
|---|---|---|---|
| tokenizerul | `date/ws/bpe_16384.json` (BPE, 16.384 simboluri), 216.041 o, SHA-256 `2fcb9937a02ae3fb23723399d8fb2fdbecad96b697e0c626109d53232974b546` | același | CITIT |
| textul (amestecul W2) | `date/ws/amestec/antrenare.txt` (4.885.859.040 o), codificat o dată și ținut în `lucru/cache/simboluri_be12c6d88276d79d.pt` (`torch.save` al unui tensor int16, 2.682.383.363 o) | același șir, tăiat în 27 de bucăți: `lucru/bucati/w2_amestec_be12/bucata_00000.bin` … `bucata_00026.bin` | CITIT |
| simboluri în text | 1.341.190.791 | 1.341.190.791 | MĂSURAT — `"simboluri_antrenare"`; la #651 și `"date_pe_bucati"` |
| formatul bucăților (#651) | — | **int16 little-endian, fără antet**, 50.000.000 simboluri pe bucată (100.000.000 o; ultima 82.381.582 o); `index.json` (5.436 o, SHA-256 `792e69dd…be29`): versiune, tip, ordinea octeților, începutul și SHA-256 al fiecărei bucăți, SHA-256 al șirului întreg `560863a976b8d36ab1515ce5121868f994f2e2959591525d0060c9e14fb5d4af`, SHA-ul tokenizerului; citit prin `np.memmap` | CITIT (`index.json`); amprenta `2b2492ec78569c2b` MĂSURATĂ în rândul 651 |
| verificarea la pornire | — | `DateBucati` recalculează SHA-256 pe fiecare bucată și pe tot șirul și refuză să pornească la orice diferență | `module/date_bucati.py` rândurile 1–20 |
| conversația | `lucru/romana_raspunsuri/antrenare.jsonl` — 23.251 rânduri, 21.948.924 o, SHA-256 `3d8ac5a30a007368b07c3a8d22632bb55e6f75dc4e0e19292364aeb56bbc00b0` | `lucru/romana_raspunsuri_r2/antrenare.jsonl` — 26.596 rânduri, 25.068.340 o, SHA-256 `85174e8dd5f918cbd842f5ca0206ee59a6f8e054512c1a2266a2387aa358212f` | CITIT; JSON pe rând, cheile `intrebare`, `raspuns`, opțional `text`; codificate la pornire |
| hrana | `date/fapte/povesti.txt` — 4.904.823 o, SHA-256 `42900c80…7099`; simboluri: NU E ÎN JURNAL | `date/ws/hrana_fineweb_rest/antrenare.txt` — 1.926.715.965 o; codificată în `lucru/cache/simboluri_091ad4c5d9a38ff3.pt` = **536.494.994** simboluri int16 | CITIT (numărul de simboluri la #651 citit acum din fișierul din cache) |
| validarea (pentru examenul orei) | `date/tinystories_r2/validare.txt` | idem (doar pentru portul `date`; examenul orei e pe română, secțiunea 5) | configurările |
| ordinea / amestecarea | fără amestecare prealabilă și fără „epoci”: fiecare fereastră e trasă la sorți uniform din tot șirul, cu repetare; `treceri_prin_text` arată cât din text s-a văzut: #513 0,527 (după 5 ore), #651 0,293 (după 7 ore) | | MĂSURAT — `rezultat.json` rândul 149 / 145 |

## 4. Ce se salvează

Două feluri de fișiere:

| Fișier | Ce conține | #513 | #651 | Marcaj |
|---|---|---:|---:|---|
| **starea liniei** `lucru/<linie>/gpt.pt` (punctul de control, scris la sfârșitul fiecărei ore, atomic: `.part` apoi redenumire) | `setari` (straturi, capete, n_emb, context, dropout), `retea` (`state_dict`, F32; `cap.weight` = aceeași memorie ca `emb_token.weight`), `optimizator` (`state_dict` AdamW: pentru fiecare din cei 148 / 292 de tensori `step` (F32 scalar), `exp_avg`, `exp_avg_sq` în F32; `param_groups` cu lr, betas, eps, weight_decay…), `pasi_total`, `minute`, `scor` | **fișierul nu mai e pe disc** (`lucru/w2_romana_r1/` are doar `rezultat.json`, `pornire.json`, CSV-ul plăcii); DEDUS ~1,18 GB (3 × 392.128.512 o) | **2.197.380.401 o** (2,20 GB); `pasi_total` 127.803, `minute` 420,01, `step` AdamW 7.984 | #651 CITIT din `lucru/w2_mare_24zc/gpt.pt`; #513 DEDUS |
| **modelul experimentului** `lucru/stocare/modele/experiment_<N>.pt` | `setari`, `vocabular`, `stare` (`state_dict` F32), `tokenizer` — **fără** optimizator | 392.400.973 o | 732.670.301 o | CITIT |
| ce **nu** se salvează | starea generatorului de numere (RNG): nu se salvează; ora următoare îl refăce din sămânță + `pasi_total`. Nici gradientul adunat parțial (se aruncă). Rata nu se salvează: se recalculează din `minute` și `pasi_total` | | | din cod (`module/model_continuu.py` rândurile 165–212) |

## 5. Examenul

Toate examenele citesc modelul salvat `lucru/stocare/modele/experiment_<N>.pt` (doar citit). Pe placă, modelul
calculează în **bf16 (autocast)**, ca la antrenare; pe procesor în F32 — cifrele de mai jos sunt toate de pe placă.

### 5.1 Cifrele

| Examen | #513 | #651 | Dovada |
|---|---:|---:|---|
| **română curat** (bpb, mai mic = mai bine) | **1,2060** | **1,0878** | MĂSURAT — #513: `lucru/jurnal/experimente.jsonl` rândul 514 (`bpb_romana_curat`, S76b); #651: rândul 651 (`romana_bpb` = 1,0877770923975458, examenul orei din S111) și raportul S129 (`docs/rapoarte/2026-11-21_0130_S129_formulari_d.md` rândul 62, re-măsurat) |
| — Wikipedia / web / cărți curat | 1,0115 / 1,3008 / 1,3408 | 0,9413 / 1,1171 / 1,2406 | MĂSURAT — rândul 514; rândul 651 |
| corecte S15 + S4 + tipuri noi, din 320 (profesor) | 114 | 228 | MĂSURAT — S111, `docs/rapoarte/2026-11-16_1238_S111_E3_conversatie.md` rândul 66 (lanțul `lucru/cascada/S111/s111_examene.py`); #651 re-măsurat 228 la S129 (raportul S129 rândul 63) |
| — S15 /80 · S4 /60 · tipuri noi /180 | 40 · 40 · 34 | 70 · 43 · 115 | MĂSURAT — raportul S111 rândurile 60–63; S129 rândurile 93–95 |
| R1 instrucțiuni | 98,97 | 99,31 | MĂSURAT — raportul S111 rândul 58; S129 rândul 64 |
| chat (a)+(b), din 200 | NU E ÎN JURNAL (#513 n-a fost dat la examenul de chat) | 25 | MĂSURAT — S129 rândul 65 (`lucru/cascada/S129_proba/chat_651.json`) |
| calcule (S120), din 200 | NU E ÎN JURNAL | 1 | MĂSURAT — S129 rândul 66 |
| formulări (S124), din 200 | NU E ÎN JURNAL | 41 = 20,5 % | MĂSURAT — S129 rândul 67 |
| cod curat (bpb, informativ) | 0,7247 | 0,7405 | MĂSURAT — rândul 514; S129 rândul 113 |

### 5.2 Comenzile exacte (cum le rulează lanțul S129, `lucru/cascada/S129_proba/s129_examene.py`)

Toate cu `.venv/Scripts/python -X utf8`, din rădăcina proiectului, pe placa liberă:

| Examen | Comanda | Unde scrie |
|---|---|---|
| română (+ cod, R2, toate validările) | `unelte/examen_validari_ws.py --experiment <N>` | `lucru/examen_validari_ws/experiment_<N>_<data>.json` + **un rând în jurnalul Kronos** (`examen_validari_ws`) |
| română, examenul orei din linia #651 | `module.examen_romana:ExamenRomana` cu `caractere = 100000, cu_r1 = false` (portul `examen` din config; rulat de Kronos la fiecare oră) | în fișa experimentului |
| S15 / S4 / tipuri noi | `unelte/examen_conversatie.py --experiment <N> --examen <fișier> --doar-local` (o dată pentru fiecare din cele 3 fișiere); corect = nota profesorului ≥ 7 | `lucru/examen_conversatie/experiment_<N>_<data>.json` + rând în jurnal |
| R1 | `unelte/romana_raspunsuri.py reper --experiment <N> --iesire <dosar_nou>` | `<dosar>/nota.json` |
| chat | `unelte/examen_chat.py --experiment <N> --examen docs/conversatie/examen_chat.json --iesire <fișier_nou>.json --dispozitiv cuda` | fișierul dat |
| calcule | `unelte/examen_calcule.py model --experiment <N> --iesire <fișier_nou>.json --dispozitiv cuda` | fișierul dat |
| formulări | `unelte/examen_formulari.py model --experiment <N> --iesire <fișier_nou>.json --dispozitiv cuda` | fișierul dat |

Reguli comune (din codul uneltelor): răspunsul **fără întâmplare** (mereu simbolul cel mai probabil), cel mult 80 de
simboluri (R1: 64), tăiat la primul rând nou sau la `<|endoftext|>`; întrebarea dată ca la antrenare
(`Întrebare: …⏎Răspuns:`, cu `Text: …⏎` în față unde e cazul). Chat, calcule, formulări și R1 se notează automat (fără
alt AI). S15/S4/tipuri noi se notează de profesorul local **Qwen3-4B-Instruct-2507** (`module/profesor_qwen.py`,
`--doar-local` = nu descarcă nimic), 1–10, corect = nota ≥ 7; al doilea notator, fără AI, e `unelte/verificator_text.py`.
**Biți pe octet:** textul tăiat la primele 100.000 de litere (la un text întreg, `unelte/validari_text.py`), ferestre de
câte 512 simboluri una după alta; primul simbol socotit cu log2(16.384) biți; bpb = biți ÷ octeți UTF-8; „română curat”
= suma biților ÷ suma octeților pe cele trei validări (`unelte/examen_validari_ws.py` rândurile 56–125).

Un OS care vrea să repete întocmai: aceleași fișiere (SHA mai jos), aceeași tăiere la 100.000 de litere, ferestre de 512,
bf16 pe placă (sau F32, dar atunci cifrele pot diferi puțin — **diferența bf16/F32 la examen: NU E ÎN JURNAL**).

### 5.3 Fișierele citite de examene (SHA-256, CITIT acum)

| Fișier | Octeți | SHA-256 |
|---|---:|---|
| `docs/conversatie/examen_generalizare_mare.json` (S15) | 44.066 | `6daeff25fe14ee56b6e49f6ed5ab6ef877eb13a6bfca3f3b7d32b365cd8ebbe9` |
| `docs/conversatie/examen_generalizare_401.json` (S4) | 28.985 | `d7d8f0ec6e7a5072873df2de8dd26d15390e2f51dbe888db3341a06ded530db6` |
| `docs/conversatie/examen_tipuri_noi.json` | 117.826 | `68cb434ad5f1b66547b7996765742d1ee7971c15601aa78938af93a40e11ffaa` |
| `docs/conversatie/examen_chat.json` | 106.503 | `077a6329da5a43902ed6256824dda98bfba21612255f11dac0af52daf3a9372f` |
| `docs/conversatie/examen_calcule.json` | 35.793 | `574f42e18c59946ba8a0f1d77314badee89cc5faaa007c79a7e6d2cd3d99ff94` |
| `docs/conversatie/examen_formulari.json` | 50.000 | `1b9bd1a043fe81ed9e56e60c3a55f4bbe016a261cf7227a61a3b17d171869f02` |
| `lucru/romana_raspunsuri/ascuns.jsonl` (R1, setul ascuns) | 482.043 | `3a333657c91598d01d59418b244383e33d2c64f248c904b34f3af331bcb45c9e` |
| `date/ws/curat/wikipedia_ro/validare_curata.txt` | 4.856.684 | `24916dc66a4ecbe738b05fd04060c4f31f73eab80c623d734f56f7cb8bb71054` |
| `date/ws/curat/fineweb2_ro/validare_curata.txt` | 25.494.517 | `9c5e4d2f6a15a3f7239d1277045d338fa07481bae6ad0b90292e6d559e953dcf` |
| `date/ws/curat/wikisource_ro/validare_curata.txt` | 400.624 | `9eaef8570113f456b9a97470155bb2bc6a1a388967d237f3e30930c8927bc78f` |
| `date/tinystories_r2/validare.txt` (R2, examenul vechi `val_bpb`) | 2.013.211 | `fb1af2a208d120425a104d1fa76881b85ab906a633d93e9f24ce45c07693d491` |
| `date/neutru/seturi.json` (examenul neutru) | 362 | `da2d8bf6f9c8cb2adc683433ab4c60a8e92f9dac4ffe172297ffecfb4b738c6e` |
| `date/ws/bpe_16384.json` (tokenizerul) | 216.041 | `2fcb9937a02ae3fb23723399d8fb2fdbecad96b697e0c626109d53232974b546` |
| `module/examen_bpb.py` (neschimbat) | 1.599 | `0ca9cf74498438062f9bb92b828c3c6a8c60c879393b2093d2ab7f5e441d3028` |
| `module/examen_romana.py` | 7.338 | `e7ee1fa5114c1b720179f66aa51550f20a0d4c1cc6d7d2ec473e9b7b878f7b14` |
| `unelte/examen_validari_ws.py` | 10.161 | `e131f8c7b4a34de15c24458bc5705f5b54e5fd4f5cf2b7fb44c90b270d5c3157` |
| `unelte/validari_text.py` | 847 | `9ce20a233eb6fa4787e5b9b5e194e4fc5c60bd5e41a8f4e4646240119253426a` |
| `unelte/examen_conversatie.py` | 8.596 | `4bd13e5b42b85fdfb8f1f38dd12cdf4186f6c6a16e88e6ccd3f67962fddcd35f` |
| `unelte/examen_chat.py` | 5.545 | `a74a021c6ead6867457fdd59efcf0f001ec79478e5ed131d47193d66c66c5611` |
| `unelte/examen_calcule.py` | 11.818 | `01c49a5ea1ff0e9a803058910fb10578a2d48842179631b6c760d3eb70334d9b` |
| `unelte/examen_formulari.py` | 20.670 | `dbcfee001a3695975147877495748b398206bcff3edd2e8f552884a175a28897` |
| `unelte/romana_raspunsuri.py` | 56.467 | `6d87f236c4d99ecd892ca18ff6adb33f78fd584ff368534756af7e46573b3939` |
| `unelte/verificator_text.py` | 4.152 | `213bc2d31677a5d00c40792ef9438ed05d8658e787bd77028656fd96db2745d1` |
| `lucru/stocare/modele/experiment_513.pt` | 392.400.973 | `605c4084f0a5db125b1e6c2c037b8e3d96abd17c1d62ec76efe439ecaba58b2c` |
| `lucru/stocare/modele/experiment_651.pt` | 732.670.301 | `8a99fb8e790b29b3ba528da4d7244e7e8f149589def32e544a3af229b061d4da` |

## 6. Ce lipsește (NU E ÎN JURNAL) — de măsurat doar cu „da”-ul lui Adrian

1. Viteza liniei de 24 de straturi **fără** recalculul activărilor (și dacă încape în 7 GB).
2. Împărțirea timpului unui pas: înainte / înapoi / optimizator / tragerea loturilor de pe procesor.
3. Viteza în F32 curat (fără bf16) pe placă, pentru o comparație directă cu un motor F32.
4. Cât diferă cifrele de examen între bf16 și F32.
5. Numărul de simboluri ale hranei liniei #513 (`date/fapte/povesti.txt`).
6. Punctul de control al liniei #513 (`lucru/w2_romana_r1/gpt.pt`) nu mai e pe disc; mărimea e doar DEDUSĂ.
