# Kronos v2 — fișa comună „Kronos croit pe placă” (C-164)

Comanda: `COMENZI.md` C-164 (Adrian, 24 nov 17:35). Fișă comună Kronos + Cyber-GPU. **Doar proiect și simulare acum**: nicio
schimbare în `kronos/`; modelul nou vine ca modul care trece `teste_contracte/`; antrenarea lungă în OS = „da” separat al lui Adrian.

Fiecare proiect își completează coloana. Cyber-GPU a scris partea „placă” (sesiunea 212, 24 nov 2026, SIMULARE / numărare);
coloanele „calitate” sunt ale lui Kronos (laboratorul C-163, probe de o oră).

Detalii Cyber-GPU: `cyber-gpu/docs/C-164_KRONOS_V2_PLACA.md`, cod `gpu_compute::v2` + T218 (numărătoarea pentru Kronos de azi =
listele planului de pe placă).

## Candidații (pasul #513, lot 2 × 512; timpii mici măsurați în os-410, pasul 483 ms)

| Candidat | Placa: ce dispare / se schimbă (Cyber-GPU) | Lansări / pas | Câștig azi (DEDUS) | Calitate: risc (Kronos) | Probă C-163 (Kronos) |
|---|---|---|---|---|---|
| azi (GELU, LayerNorm, deplasări) | — | 385 | — | — | — |
| **ReLU²** în loc de GELU | `gelu_tr` → `relu2` mai simplu; oracol cu **aceiași biți** (fără toleranță); lipirea în înmulțire devine ușoară | 385 | ~0 ms (programul e mic) | *de completat* | *de completat* |
| **Fără deplasări** (bias) | 48 de sume pe coloane dispar (4 pe strat) | 337 | **−15,9 ms (−3,3 %)** | *de completat* | *de completat* |
| **RMS cu γ** în loc de LayerNorm | normele devin variante fără medie; dγ = programul `colsum` de azi cu media 0 (nimic nou) | 385 | <0,5 ms | *de completat* | *de completat* |
| **RMS fără γ** | toate sumele pe coloane ale normelor dispar | (cu fără deplasări:) 312 | (împreună:) **−24,3 ms (−5,0 %)** | *de completat* | *de completat* |
| **Lățimi ÷ 64** | #513 le are deja (C 768, 3C, 4C, V 16 384, T 512 — și ÷ 128); de păstrat: C multiplu de 128, capul de atenție d = 64, V multiplu de 128 | — | 0 (deja) | — | — |
| **Capul** | legat de `emb_token` = 12,9 % din munca înmulțirilor; dezlegat = același calcul, +12,6 M parametri (~200 MB cu AdamW); V 8 192 ar tăia −6,5 % din înmulțiri | — | doar prin V | *de completat (tokenizatorul)* | *de completat* |

Cu toți candidații **și** cele două lipiri care există deja (normă înapoi + rezidual, activarea înapoi în înmulțire): **276** lansări
în loc de 385 (−25,4 ms); cu o lipire nouă a activării și înainte: 264.

## Ce trebuie știut cinstit (Cyber-GPU)

1. **Azi câștigul e mic (≤ 5 %)** și vine aproape tot din sumele pe coloane (`colsum`). `colsum` împărțit (gata în SIMULARE, T216,
   de legat de OS) le aduce oricum la ~2,5–5 ms; după el candidații mai dau ~1 %. Cifra „+10–20 %” din idee devine reală **doar după**
   ce înmulțirile se fac mult mai repede (pista A, tensor cores): atunci programele mici ajung ~1/4 din pas.
2. **Felurile de programe nu scad la ~5**: rămân ~14 (atenția, încorporările, eroarea, optimizatorul nu se schimbă). Scad **lansările**
   (385 → 264–312) și programele noi sunt toate variante mici ale celor de azi.
3. Programele noi de scris doar dacă se aleg candidații: `rms_fwd`, `rms_back(_res)`, `relu2`, `mm_train_relu2`. Oracolele lor pe
   procesor există deja (`gpu_compute::v2`, verificate cu diferențe finite).

## Nu evaluate încă

Poziții rotative, QK-norm (din `idei/2026-11-24-centru-viteza-peste-windows.md`) — de socotit dacă Kronos le propune.

## Decizia

*De completat de Kronos (recomandarea pe calitate) și de Adrian.*
