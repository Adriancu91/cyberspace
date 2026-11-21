# „Pasul de aur” — 10 pași de antrenare din PyTorch, pentru motorul de antrenare din OS

S132 (comanda lui Adrian C-156, 21 nov 2026). Unealta: `unelte/pas_de_aur.py` (teste: `teste/test_pas_de_aur.py`).

**Pe scurt:** am luat o rețea Kronos, un lot fix de simboluri și am făcut 10 pași de antrenare în PyTorch, pe procesor,
în F32, cu totul fixat ca rularea să iasă la fel de fiecare dată. Am scris în fișiere simple tot ce trebuie ca motorul
din OS să facă aceiași 10 pași și să se compare: greutățile de la început, lotul, eroarea la fiecare pas, gradientul
fiecărui tensor la pasul 1 și greutățile după pasul 1 și după pasul 10. Două rețete: **SGD simplu** (cel mai ușor de
verificat întâi) și **AdamW exact ca la antrenarea liniei lui #513**.

## Ce seturi există

| Set | Unde | Model | Lot | Parametri | Mărime totală | În git |
|---|---|---|---|---|---|---|
| mic | `docs/integrare_kronos/pas_de_aur_mic/` | aceeași arhitectură, 2 straturi, n_emb 64, 4 capete, vocabular 256, context 32; greutăți din `torch.manual_seed(1132)` | 2 × 32, simboluri din `torch.Generator().manual_seed(1132)` | 118.528 | 3.319.296 o (3,32 MB) | tot |
| #513 | `lucru/pas_de_aur/513/` (pe workstation) | #513 doar citit (12 straturi, n_emb 768, 12 capete, vocabular 16.384, context 512) | 1 × 64 simboluri din `date/ws/curat/wikipedia_ro/validare.txt`, de la caracterul 4.533.222 (ales cu `random.Random(1132)`) | 98.032.128 | 2.744.900.096 o (2,74 GB) | doar `reteta.json` (în `docs/integrare_kronos/pas_de_aur_513/`) |

SHA-256 al fișierelor `reteta.json`: mic `5e3c5824e61b9974aca527ee3c04237868f28cc28a2c0d04b742c81dce84e3a8`,
#513 `ce4150b8825ee9c4467385d09fd01fa21d5617de5600a98f900f17514fe3d0a4`. SHA-256 al fiecărui fișier de date e în
`reteta.json` → `fisiere`. Modelul #513 (`lucru/stocare/modele/experiment_513.pt`, SHA-256 `605c4084…8b2c`) a rămas
neschimbat (înainte = după).

## Ce conține fiecare dosar

| Fișier | Ce e |
|---|---|
| `reteta.json` | arhitectura, rețetele (cu toți parametrii optimizatorului), sămânța, forma lotului, ordinea/numele/formele tensorilor, SHA-256 și mărimea fiecărui fișier, erorile și normele gradientului pe cei 10 pași, versiunile |
| `intrari.i32`, `tinte.i32` | lotul: int32 little-endian, formă [lot, context], pe rânduri; `tinte[b, t]` = simbolul de după `intrari[b, t]` |
| `initiale/<tensor>.f32` | greutățile de la început (aceleași pentru ambele rețete) |
| `<rețetă>/grad_pas1/<tensor>.f32` | gradientul la pasul 1, **înainte** de tăierea gradientului |
| `<rețetă>/dupa_pas1/<tensor>.f32` | greutățile după pasul 1 |
| `<rețetă>/dupa_pas10/<tensor>.f32` | greutățile după pasul 10 |

`<rețetă>` = `sgd` sau `adamw_513`. Fiecare `.f32` = numerele tensorului în **F32 little-endian, fără antet**, în ordinea
C (pe rânduri: ultimul indice se schimbă cel mai repede). Forma e în `reteta.json` → `ordinea_tensorilor`.

## Ordinea tensorilor

Ordinea lui PyTorch `named_parameters()`. Pentru modelul mic (la #513 e la fel, cu `straturi.0` … `straturi.11`,
în total 148 de tensori; formele cu 768 / 2304 / 3072 / 16.384 / 512 în loc de 64 / 192 / 256 / 256 / 32):

| # | Nume | Formă | Elemente |
|---|---|---|---|
| 0 | `emb_token.weight` | 256 × 64 | 16.384 |
| 1 | `emb_pozitie.weight` | 32 × 64 | 2.048 |
| 2 | `straturi.0.ln1.weight` | 64 | 64 |
| 3 | `straturi.0.ln1.bias` | 64 | 64 |
| 4 | `straturi.0.atentie.in_proj_weight` | 192 × 64 | 12.288 |
| 5 | `straturi.0.atentie.in_proj_bias` | 192 | 192 |
| 6 | `straturi.0.atentie.out_proj.weight` | 64 × 64 | 4.096 |
| 7 | `straturi.0.atentie.out_proj.bias` | 64 | 64 |
| 8 | `straturi.0.ln2.weight` | 64 | 64 |
| 9 | `straturi.0.ln2.bias` | 64 | 64 |
| 10 | `straturi.0.mlp.0.weight` | 256 × 64 | 16.384 |
| 11 | `straturi.0.mlp.0.bias` | 256 | 256 |
| 12 | `straturi.0.mlp.2.weight` | 64 × 256 | 16.384 |
| 13 | `straturi.0.mlp.2.bias` | 64 | 64 |
| 14–25 | `straturi.1.…` | la fel ca 2–13 | |
| 26 | `ln.weight` | 64 | 64 |
| 27 | `ln.bias` | 64 | 64 |

**Ieșirea (`cap.weight`) nu are fișier:** e **același tensor** cu `emb_token.weight` (greutăți legate). Gradientul din
`emb_token.weight` e deci **suma** celor două contribuții (încorporarea la intrare + proiecția la ieșire).
Greutățile Linear sunt [ieșiri, intrări] (y = x·Wᵀ + b), ca în PyTorch.

## Rețeaua (înainte)

1. `x = emb_token[intrari] + emb_pozitie[0..T−1]`
2. pentru fiecare strat: `x = x + Atenție(LN1(x))`, apoi `x = x + MLP(LN2(x))`
3. `logits = LN(x) · emb_tokenᵀ` (fără deplasare)

- **LayerNorm:** `(x − medie) / √(varianța pe n, nu pe n−1 + 1e-5) · weight + bias`.
- **MLP:** `mlp.0` (n_emb → 4·n_emb) → **GELU exact** `0,5·x·(1 + erf(x/√2))` → `mlp.2` (4·n_emb → n_emb).
- **Atenția** (`nn.MultiheadAttention`): `in_proj_weight` are rândurile **Q, apoi K, apoi V** (câte n_emb fiecare),
  la fel `in_proj_bias`. Capul i folosește coloanele `i·d … (i+1)·d − 1` din Q, K, V (d = n_emb / capete = 16 la mic,
  64 la #513). Scoruri `Q·Kᵀ / √d`; masca cauzală (poziția j > i → −∞) înainte de softmax; `softmax · V`; capetele
  lipite la loc în ordine, apoi `out_proj` (cu deplasare).
- **Dropout 0** peste tot (verificat de unealtă; dacă ar fi ≠ 0, unealta se oprește).

## Eroarea și pasul

- **Eroarea:** entropia încrucișată (logaritm natural), **media pe toate pozițiile** lotului (lot × context),
  calculată în F32: `F.cross_entropy(logits.view(−1, vocabular), tinte.view(−1))`.
- **Eroarea pasului k** e calculată pe greutățile **dinaintea** actualizării k (deci pierderea 1 = pe greutățile inițiale).
- **Ordinea unui pas:** gradient la zero → înainte → înapoi → (gradientul pasului 1 se exportă aici) → tăierea
  gradientului (doar la AdamW) → pasul optimizatorului.
- **Același lot** la toți cei 10 pași; **rata constantă** (fără încălzire, fără scădere); un singur lot (fără adunare).

## Formulele optimizatoarelor (cum le aplică PyTorch 2.14, pe fiecare tensor, implementarea „single tensor”)

**(a) `sgd`** — rata 0,01, fără momentum, fără scăderea greutăților, fără tăiere:

    w ← w − 0,01 · g

**(b) `adamw_513`** — `torch.optim.AdamW(lr = 5e-5, betas = (0,9; 0,999), eps = 1e-8, weight_decay = 0,1, amsgrad = False)`,
cu tăierea gradientului la norma 1,0 înainte de fiecare pas. Valorile sunt citite din cod, nu ghicite:
`config/conv_w2_romana_r1.toml` (linia lui #513: `optimizator = "adamw"`, `rata_invatare = 0.00005`) →
`module/model_muon.py` `_optimizator_nou` (`AdamW(…, weight_decay=0.1)`, restul implicit) și `_pas_adunat`
(`clip_grad_norm_(…, 1.0)`). La bucata B unealta a cerut chiar modelului #513 optimizatorul lui și a verificat că se
potrivește (clasa AdamW, lr 5e-05, betas [0,9; 0,999], eps 1e-08, weight_decay 0,1).

Tăierea gradientului (pe toți tensorii împreună):

    N = √( Σ_tensori Σ_elemente g² )          (norma totală, „norma normelor”)
    c = min(1; 1,0 / (N + 1e-6))
    g ← g · c                                  (la toți tensorii)

Apoi, la pasul t = 1, 2, …, 10 (m₀ = v₀ = 0, pe fiecare element):

    w ← w · (1 − lr · 0,1)                     (scăderea greutăților, decuplată, ÎNAINTE de restul)
    m ← 0,9 · m + 0,1 · g
    v ← 0,999 · v + 0,001 · g²
    b1 = 1 − 0,9^t ;  b2 = 1 − 0,999^t          (corecția de bias)
    w ← w − (lr / b1) · m / ( √v / √b2 + 1e-8 )

Atenție: **scăderea greutăților se aplică la toți tensorii** (și la LayerNorm, deplasări, încorporări), fiindcă
optimizatorul liniei are un singur grup. Rânduri cu gradient zero (de ex. pozițiile 64–511 din `emb_pozitie` la #513,
simbolurile care nu apar în lot) se schimbă totuși, prin `w · (1 − lr · 0,1)`.

Ce diferă de antrenarea reală a lui #513 (scris și în `reteta.json`): acolo erau 8 loturi de 12 × 512 adunate pe pas
(pierderea ÷ 8), încălzire 100 de pași și pierderea mascată la conversații. Aici: un lot mic, rata constantă, pierderea pe
toate pozițiile — ca să fie ușor de reprodus.

## Erorile pe cei 10 pași

| Set · rețetă | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| mic · sgd | 44,193802 | 43,037758 | 41,887100 | 40,740528 | 39,596748 | 38,454552 | 37,312939 | 36,171272 | 35,029324 | 33,886936 |
| mic · adamw_513 | 44,193802 | 44,085415 | 43,976913 | 43,868301 | 43,759567 | 43,650726 | 43,541763 | 43,432682 | 43,323475 | 43,214138 |
| #513 · sgd | 2,739111 | 1,206350 | 0,531199 | 0,233237 | 0,116129 | 0,072774 | 0,052402 | 0,040492 | 0,032794 | 0,027569 |
| #513 · adamw_513 | 2,739111 | 1,192299 | 0,393974 | 0,084657 | 0,027957 | 0,019688 | 0,002978 | 0,001675 | 0,001268 | 0,001056 |

Modelul mic pornește de la 44 (nu de la ln 256 ≈ 5,5): încorporările legate au la început valori N(0, 1), deci ieșirile
sunt mari. La #513 eroarea scade repede pentru că același lot de 64 de simboluri e văzut de 10 ori.

## Toleranțe recomandate pentru comparație (F32)

Am măsurat cât diferă **același calcul pe același procesor cu 1 fir față de 16 fire** (altă ordine a adunărilor) —
cea mai apropiată măsurătoare pe care o pot face de „alt procesor / altă placă”. Seturile oficiale sunt cu 1 fir.
Pe alt procesor n-am putut măsura (doar acest workstation, Intel64 Family 6 Model 85).

| Ce comparăm | Măsurat mic | Măsurat #513 | Recomandat |
|---|---|---|---|
| eroarea, relativ | ≤ 1,1e-7 | ≤ 6,5e-6 | ≤ 1e-5 |
| gradientul pasului 1, absolut pe element | ≤ 3,6e-7 | ≤ 2,7e-6 | ≤ 1e-5 |
| gradientul pasului 1, ‖Δ‖ / ‖g‖ pe tensor | ≤ 2,1e-7 | ≤ 7,0e-4 | ≤ 1e-3 |
| greutăți SGD după 1 și 10 pași, absolut | ≤ 1,2e-7 | ≤ 1,2e-7 | ≤ 1e-6 |
| greutăți AdamW după pasul 1, absolut | ≤ 1,8e-11 | ≤ 8,0e-6 | ≤ 1e-4 (= 2 · lr) |
| greutăți AdamW după pasul 10, absolut | ≤ 8,5e-6 | ≤ 1,0e-5 | ≤ 1e-4 |

De ce AdamW are toleranța mai largă: la pasul 1, `m / √v` ≈ semnul lui g, deci fiecare element se mișcă cu ≈ lr
(5e-5) în sus sau în jos. Unde gradientul e aproape zero, o diferență de rotunjire îi poate schimba semnul și elementul
se mișcă în cealaltă direcție: diferența poate ajunge la 2 · lr = 1e-4. **Ordinea recomandată:** întâi SGD pe modelul
mic (cel mai strict), apoi AdamW pe modelul mic, apoi #513.

Aproape niciun gradient nu iese identic bit cu bit între 1 și 16 fire la #513 (1,3 % din elemente), deci o comparație
„bit cu bit” între OS și PyTorch nu e de așteptat; comparația trebuie făcută cu toleranțele de mai sus.

## Verificări făcute (testele, `teste/test_pas_de_aur.py`, 7 teste)

- două rulări → fișiere identice (SHA-256) și aceleași erori; repetarea din linia de comandă a modelului mic a dat același
  dosar, octet cu octet;
- eroarea scade la fiecare din cei 10 pași, la ambele rețete;
- gradientul exportat = gradientul calculat de PyTorch (egal exact), greutățile inițiale și lotul la fel;
- **verificare numerică independentă (diferențe finite)** în F64 pe 5 elemente (`emb_token`, `in_proj_weight`,
  `mlp.0.weight`, `ln1.weight`, `ln.bias`): `(L(w+h) − L(w−h)) / 2h`, h = 1e-6, față de gradientul analitic —
  toleranța relativă 1e-5; gradientul F32 față de cel F64: ‖Δ‖ ≤ 1e-4 · ‖g‖ pe fiecare tensor;
- primul pas recalculat de mână după formulele de mai sus (SGD și AdamW cu tăiere): egal cu PyTorch (rtol 1e-6, atol 1e-7);
- rețeta `adamw_513` = configurarea liniei + codul modelului (citite în test).

## Comanda de reproducere

    CUDA_VISIBLE_DEVICES=-1 python -X utf8 unelte/pas_de_aur.py mic --iesire <dosar_nou>
    CUDA_VISIBLE_DEVICES=-1 python -X utf8 unelte/pas_de_aur.py model --experiment 513 --iesire <dosar_nou>

Opțiuni: `--fire N` (implicit 1; seturile oficiale sunt cu 1), `--lungime 64` (la `model`). Unealta refuză un dosar care
există. Versiuni: Python 3.12.10, PyTorch 2.14.1+cu132 (rulat pe procesor), numpy 2.5.2, Windows 11 (10.0.26300).
