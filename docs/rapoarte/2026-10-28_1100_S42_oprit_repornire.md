# S42 — oprită: antrenarea a fost întreruptă de repornirea workstation-ului (fereastra OS/GPU)

Executantul (cascada), 28 octombrie 2026, ~11:00.

## Pe scurt
- S42 (cititorul E3 refăcut din #459 cu rețeta A) a pornit la **08:33:21** (procesul 19792), după pre-înregistrare (e77a0eb).
- **Ora 1 din 3 s-a terminat normal**: experimentul **#462** salvat la 09:37 (detalii mai jos).
- Placa a lucrat normal până la **09:59:16** (ultimul rând din jurnalul plăcii). Apoi procesul a dispărut **fără cod de ieșire**:
  workstation-ul a intrat în **fereastra OS/GPU anunțată de centrul de comandă** (28 oct, ~10:05–12:00, Adrian de față, repornire în
  Cyber Universe OS). Windows a pornit din nou la **10:50:12**.
- Antrenarea **nu s-a terminat** (ar fi trebuit ~11:50) și **examenele nu au rulat** → **nu există verdict**. Pre-înregistrarea
  `docs/preinregistrari/2026-10-28_E3_reteta_A.md` rămâne **deschisă** (n-am închis-o, pentru că n-am măsurat nimic din ce cere).
- Am pus S42 pe **`oprit`**. N-am repornit nimic: fereastra spune că nu pornește nicio sarcină nouă de placă până după ~12:00,
  iar reluarea e o decizie pentru supraveghetor/Adrian.

## Cifrele (doar ce s-a măsurat)
| | #462 (ora 1 din 3) |
|---|---|
| val_bpb (examenul obișnuit) | 0,4158 (#459 la plecare: 0,4084 → „câștig” −0,0074, așteptat: amestecul E3 diferă de cel al lui #459) |
| fapte | 150 / 150 |
| fapte noi | 77 (80 cu sinonime) |
| nota profesorului | 4,47 (± 0,28) |
| pași | 22.961 (6,4 pași/s), 2.870 pași de optimizator, 1 lot aruncat |
| memoria plăcii | max 6.264 MB în jurnalul plăcii (rezervat de PyTorch 5.306 MB) — sub 7.000 MB ✓ |
| temperatura | max 64 °C — sub 83 °C ✓ |

Răcirea (ultimele 25 % din 3 ore) **nu a apucat să înceapă**, deci #462 nu e modelul pe care îl cerea pre-înregistrarea.

## Ce a rămas pe disc (n-am șters nimic)
- `lucru/w2_e3_reteta_A/gpt.pt` (salvat la 09:34, starea de după ora 1), `pornire.json`, jurnalul plăcii.
- `lucru/w2_e3_reteta_A/ruleaza.lock` a rămas de la procesul oprit (procesul nu mai există). **Nu l-am șters**; dacă o reluare se plânge
  de el, trebuie șters de cine aprobă reluarea.
- `lucru/stocare/modele/experiment_462.pt` (în jurnal, ca de obicei).

## Testele
`CUDA_VISIBLE_DEVICES=-1 python -m pytest -q`: **965 trec, 1 sărit** (270 s). Nimic schimbat în cod.

## Ce propun (alegeți una)
1. **Reluare de la zero după fereastră** (cea mai curată): aceeași comandă, aceeași pre-înregistrare (pragurile nu s-au uitat la nimic),
   cu `lucru/w2_e3_reteta_A/` mutat deoparte (ex. `w2_e3_reteta_A_intrerupt_1028`) ca regula „dosarul nu există” să fie respectată.
   ~3 ore + ~1 oră examene; încape azi în fereastra de zi dacă pornește până pe la ~14:00.
2. **Continuare din #462** cu încă 2 ore: mai rapid, dar răcirea a fost programată pe 3 ore (10.800 s) de la pornire și nu e sigur că
   unealta o reia corect; ar trebui o notă în pre-înregistrare înainte. O recomand mai puțin.

Până la decizie, următoarea sarcină `aprobat` din coadă este S41 (doar procesor); o iau la următoarea rulare dacă placa e liberă.
