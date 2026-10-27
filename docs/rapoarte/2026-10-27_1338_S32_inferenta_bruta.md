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

(se completează după măsurare)
