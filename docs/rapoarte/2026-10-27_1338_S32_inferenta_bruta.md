# S32 (C-21.3): motorul de inferență fără PyTorch (fp32 + Q8_0), doar pe procesor

Executantul, 27 octombrie 2026, 13:38. Sarcina S32 din `plan/coada.md` (aprobată de Adrian, C-21, 26 oct 17:45).
Modelul: #415 (`w2_conv_text_v3`, 12 straturi, 12 capete, 768, context 512, vocabular 16.384), doar citit.

## Ce s-a făcut până la măsurare (commit 190bd38)

1. **Formatul KGR1** și exportul: `unelte/exporta_greutati.py`; descrierea (contractul pentru Cyber Universe OS):
   `docs/format_greutati.md`. Antet cu chei-valori, little-endian, aliniere 32; variantele **F32** și **Q8_0** (doar pe
   tensorii cu 2 dimensiuni = greutățile; LayerNorm și deplasările rămân F32; blocuri de 32, o scară `f32` pe bloc,
   36 de octeți pe bloc). Tokenizerul intră în fișier (text JSON), deci fișierul e singur de ajuns.
2. **Motorul**: `unelte/inferenta_bruta.py` (Python + numpy, fără PyTorch: testul verifică că `torch` nu se încarcă).
   **Nu e modul pe platformă:** portul „model” din `kronos/contracte.py` cere și `antreneaza`, iar motorul doar
   citește; un port nou („inferenta”) ar schimba `kronos/`, deci rămâne la Adrian. Motorul e în `unelte/`, cum spunea sarcina.
   Q8_0 se poate rula în două feluri: desfăcut o dată la încărcare (aceeași viteză ca F32) sau ținut pe un octet și
   desfăcut la fiecare înmulțire („la_pas”, memorie de ~4 ori mai mică).
3. **Testele** `teste/test_inferenta_bruta.py` (8, fără placă): pe un GPT mic cu greutăți la întâmplare, motorul iese ca
   PyTorch strat cu strat (< 1e-5), la logits pe 3 texte fixe (< 1e-4), la biți (pe texte mai lungi decât contextul)
   și la completare (și după ce trece de context); Q8_0: eroarea ≤ jumătate de scară; `erf`/GELU ca PyTorch.
   Toate testele: **960 trec, 1 sărit**.

## Pragurile (scrise și urcate ÎNAINTE de măsurare)

Pe #415, pe procesor (`CUDA_VISIBLE_DEVICES=-1`), o singură rulare: `lucru/cascada/S32_proba/s32.py` → `lucru/s32/s32.json`.

- **fp32:** pe 3 texte fixe, diferența maximă dintre logits-urile motorului și cele din PyTorch (pe procesor, fp32)
  **< 1e-4** → TRECE; altfel NU TRECE.
- **Q8_0:** val_bpb pe validarea românească curată (grupa `romana_curat` din `unelte/examen_validari_ws.py`: Wikipedia,
  web, cărți, câte 100.000 de litere, media pe octeți) crește față de fp32 (același motor) cu **cel mult 0,005** → TRECE;
  altfel NU TRECE. Alături (nu decide): fiecare validare în parte și bpb-ul din PyTorch, ca reper.
- Alături (nu decid): simboluri pe secundă la completarea fără întâmplare (64 de simboluri după un început scurt), pentru
  F32, Q8_0 desfăcut la încărcare, Q8_0 „la_pas” și PyTorch pe procesor; mărimea fișierelor; memoria greutăților.

**Așteptările mele în cifre:** fp32 diferența maximă ~1e-5 (trece); Q8_0 bpb +0,001 … +0,002 (trece); fișierul F32
~390 MB, Q8_0 ~110 MB; F32 10–30 simboluri/s, Q8_0 „la_pas” de 3–6 ori mai încet decât F32.

## Ce a ieșit

Completat de executant la 14:03. Rularea: `lucru/cascada/S32_proba/s32.py`, pornită prin cascadă la 13:39:47 (procesul
20664), încheiată la 13:53:55 cu **cod 0** (~14 minute, procesor, 18 fire). Rezultatul: `lucru/s32/s32.json` (nu e în Git).
RAM-ul procesului la final: 1.299 MB. Placa nefolosită (400 MB, 28 °C la verificare).

**Exportul** (#415, 98.032.128 de parametri):

| varianta | fișierul | mărime | timp export | memoria greutăților în motor |
|---|---|---|---|---|
| F32 | `lucru/s32/experiment_415_f32.kgr` | 392,4 MB | 0,3 s | 374,0 MB |
| Q8_0 | `lucru/s32/experiment_415_q8_0.kgr` | 110,9 MB | 0,8 s | 374,0 MB (desfăcut la încărcare) / 105,5 MB („la_pas”) |

**fp32 — logits pe cele 3 texte fixe, față de PyTorch pe procesor:**

| text | simboluri | logit maxim (abs) | dif. maximă F32 | dif. maximă Q8_0 | argmax la fel F32 / Q8_0 |
|---|---|---|---|---|---|
| „Capitala României este București…” | 17 | 15,89 | **1,23e-4** | 0,159 | 100 % / 100 % |
| „Întrebare: Cine a scris poezia „Luceafărul”?…” | 21 | 16,67 | **1,34e-4** | 0,154 | 100 % / 100 % |
| „Once upon a time…” | 21 | 17,28 | 9,7e-5 | 0,162 | 100 % / 95,2 % |

Diferența maximă F32: **1,335e-4** (prag < 1e-4).

**Q8_0 — val_bpb pe română curat** (media pe octeți; același motor):

| validarea | octeți | PyTorch | motor F32 | motor Q8_0 | timp PyTorch / F32 / Q8_0 |
|---|---|---|---|---|---|
| Wikipedia | 103.501 | 1,095326 | 1,095327 | 1,095389 | 9,3 / 150,9 / 150,3 s |
| web | 98.395 | 1,381078 | 1,381078 | 1,381076 | 8,8 / 132,7 / 132,6 s |
| cărți | 80.259 | 1,414674 | 1,414675 | 1,414664 | 6,6 / 106,9 / 107,0 s |
| **total** | 282.155 | **1,285814** | **1,285815** | **1,285833** | |

Creșterea Q8_0 față de F32: **+0,0000187** (prag ≤ +0,005). Motorul F32 față de PyTorch la bpb: +0,0000005.

**Viteza** (completare fără întâmplare, 64 de simboluri după „Ana a mers la piață să cumpere”):

| | simboluri/s | text identic cu PyTorch |
|---|---|---|
| motor F32 | 42,4 | da |
| motor Q8_0 desfăcut la încărcare | 43,2 | da |
| motor Q8_0 „la_pas” | 2,2 | da |
| PyTorch pe procesor (fără cache) | 36,1 | — |

Toate patru dau același text (o repetiție: „…o mașină de lux, care a fost cumpărată de la un preț de 5 lei…”).

## Verdictul (strict după pragurile de mai sus)

- **fp32: NU TRECE.** Diferența maximă e 1,34e-4, peste pragul de 1e-4 (pe 2 din 3 texte). Spus cinstit, ce înseamnă:
  diferența e ~8 milionimi din mărimea logits-urilor (până la ~17), argmax-ul e identic pe toate pozițiile, bpb-ul diferă
  cu 0,0000005, iar textul generat e identic cu PyTorch. Cel mai probabil e ordinea adunărilor în fp32 (numpy față de
  PyTorch, 12 straturi); pe modelul mic din teste diferența era < 1e-4. Dar pragul scris înainte era 1e-4 și nu e atins;
  nu l-am mutat după măsurare.
- **Q8_0: TRECE**, cu mult: +0,00002 bpb față de pragul de +0,005.

Față de așteptările mele: fp32 am așteptat ~1e-5 (a ieșit de ~13 ori mai mult); Q8_0 am așteptat +0,001…+0,002 (a ieșit
de ~50–100 de ori mai puțin); fișierele exact cât am așteptat (392 / 111 MB); F32 42 simboluri/s, peste intervalul de
10–30 așteptat; „la_pas” de ~19 ori mai încet decât F32 (am așteptat 3–6 ori).

## Testele

`CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -m pytest -q`: **960 trec, 1 sărit** (226 s).

## Ce aștept de la Adrian / ce propun

1. **fp32**: decide dacă pragul de 1e-4 (absolut) rămâne. Variante: (a) îl păstrezi și cer o sarcină nouă: motorul
   adună în float64 la LayerNorm / softmax și remăsor o dată (pragul rămâne 1e-4); (b) accepți ca prag un criteriu
   relativ (de ex. dif. maximă < 1e-5 × logitul maxim, plus argmax identic) — dar asta ar fi un prag nou, pentru o
   măsurare nouă, nu pentru aceasta.
2. **Contractul pentru Cyber Universe OS** (`docs/format_greutati.md` + fișierul Q8_0 de 111 MB) e gata de folosit:
   Q8_0 nu pierde practic nimic la bpb. Varianta „la_pas” e prea încetă în numpy (2,2 simboluri/s); în motorul lor
   (cod nativ) înmulțirea pe un octet ar trebui să fie rapidă.
3. Portul „inferenta” în `kronos/` (ca motorul să devină modul) rămâne la tine.
