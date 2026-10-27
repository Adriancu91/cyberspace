# Pre-înregistrare: Proba de control (S34): #415 + 2 ore cu rețeta veche (C) față de rețeta A (#441)

<!-- scrisa: 2026-10-27T09:00:09 -->
*Scrisă la 2026-10-27 09:00, la S34, ÎNAINTE de antrenare (nicio antrenare S34 nu a pornit; `lucru/w2_reteta_C/` nu există).
După ce rularea a început, textul de mai jos nu se mai schimbă; la închidere se adaugă doar „Ce a ieșit” și „Verdictul”
(`python unelte/preinregistrare.py --inchide reteta_control`).*

## Cine a ales

Supraveghetorul (S34, 27 oct 08:15, granițele 1 și 2 din REGULI_CASCADA.md), cu pragul de mai jos. Configurarea și această
pre-înregistrare: Claude Code (executantul).

## Întrebarea

La S31, A (#441: AdamW + gradient adunat pe 8 loturi + răcire liniară la 0 în ultimele 25 %, 2 ore din #415) a dat română
curat **1,2332**, față de #415 **1,2858**. **Vine câștigul din rețeta A sau doar din cele 2 ore de antrenare în plus?** C = aceleași
2 ore din #415, cu rețeta veche a lui #415 (fără adunare, fără răcire, rata 0,00005 constantă), e reperul care lipsea.

## Ce rulează

Un singur proces, prin cascadă (`cascada.py porneste S34 -- python lucru/cascada/S34_proba/s34.py`), pașii pe rând, oprire la
primul cod diferit de 0:
1. **C:** `python unelte/antrenare_lunga.py --config config/conv_w2_reteta_C.toml --ore 2 --porneste-din 415`.
   `config/conv_w2_reteta_C.toml` = copie exactă a `config/conv_w2_text_v3.toml` (rețeta lui #415, `module.model_conversatie`),
   cu doar `nume`, `cale_stare`, eticheta și antetul schimbate (diff-urile în raport).
2. **Examenele, o singură rulare:** `unelte/examen_validari_ws.py --linie w2_reteta_C` (ultimul model, ora 2), apoi, în același
   proces, `unelte/examen_validari_ws.py --linie w2_muon_A` (#441, re-măsurat ca reper; la S31: 1,2332).
   Din antrenare (examenele lui Kronos de la fiecare oră): val_bpb pe TinyStories R2 și faptele noi (din 150).

Ora estimată de sfârșit: **~11:15** (2 ore + pauzele dintre ore + ~1 minut de examene; la S31, A a durat 2 h 07 min). Placa: A
a mers la 5.374 MB; rețeta veche are același lot (12) și aceeași rețea; paznicul oprește peste 7.000 MB sau 83 °C.

## Măsurile (fixate acum)

- **română** = `bpb_romana_curat` din `unelte/examen_validari_ws.py` (media pe validările curate Wikipedia / web / cărți, fără
  textele scurse în antrenare). Reperele: #415 **1,2858**; #441 (A) **1,2332** la S31.
- **Δ = C − A**, cu A = #441 **re-măsurat în aceeași rulare** (dacă iese altceva decât 1,2332, contează cifra din rulare și o spun).
- Alături (NU decid): TinyStories R2 (val_bpb oficial, ora 2; #415 0,4411, #441 0,4154), `bpb_cod_curat` (#415 0,7920, #441 0,7460),
  fapte noi din 150 (#415 68, #441 76), pentru A, C și #415. Plus `bpb_romana` (necurățat), tot fără să decidă.

## Pragurile (din S34, cuvânt cu cuvânt)

- **CONFIRMAT** (rețeta A aduce câștig real) dacă **Δ ≥ 0,010**;
- **INFIRMAT** (câștigul vine din cele 2 ore, nu din rețetă) dacă **Δ < 0,005**;
- **între ele: NECLAR**.

## Să nu uite

- O singură sămânță și o singură rulare pe fiecare rețetă: o diferență mică poate fi și noroc; NECLAR e NECLAR.
- Rețeta A schimbă trei lucruri odată (AdamW prin `module.model_muon`, adunare pe 8 loturi, răcire 25 %); CONFIRMAT spune doar
  că pachetul ajută, nu care dintre ele. Cu adunarea pe 8 loturi, A a făcut de ~8 ori mai puțini pași de optimizator decât C.
- Un singur set de examene; nu se aleg orele după rezultat (ora 2, ultimul model, la C; #441 la A).
- Dacă pică un pas, lanțul se oprește; nu se repornește pe ascuns (de 2 ori aceeași eroare → `oprit`). Peste 7.000 MB → `oprit`.
- Modelul nou NU intră în interfață. Nu se ating `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, datele de examen, #415, #441,
  linia `w2_conv_text_v3` și configurările S31.

## Așteptările mele (în cifre)

- C (rețeta veche, 2 ore): română curat **~1,265** (coboară de la 1,2858, dar fără răcirea finală mai puțin decât A); TinyStories R2
  **~0,435**; cod curat **~0,78**; fapte noi **~68–72**.
- A re-măsurat: 1,2332 (aceeași cifră ca la S31; examenul nu are nimic întâmplător).
- Δ așteptat: **~+0,03**. Șansele: CONFIRMAT ~70 %, NECLAR ~10 %, INFIRMAT ~20 %.

## Ce ar infirma așteptările

- C ≤ 1,2382 pe română (Δ < 0,005): câștigul lui A vine din orele în plus, nu din rețetă → INFIRMAT.
- C sub A pe română (Δ < 0): rețeta veche e chiar mai bună în 2 ore.
