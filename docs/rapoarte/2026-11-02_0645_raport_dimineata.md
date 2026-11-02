# Raportul de dimineață — 2 noiembrie 2026, 06:45

Scris automat de sarcina „Kronos raport dimineata”, fără om de față. Am doar citit jurnalele; n-am pornit nimic pe placă și n-am
schimbat cod.

## Pe scurt

- Noaptea a rulat **S58: prima antrenare Kronos-Cod** (modelul care învață să scrie cod), 10 ore, de la zero, cu
  `config/cod_c1_init002.toml`. **S-a terminat cum trebuie** (1 nov 19:00 → 2 nov 05:15, fără erori, toate cele 10 ore păstrate).
- După antrenare, executantul a dat examenele, o singură dată. **Verdictul după pragurile scrise dinainte: NECLAR.**
- **O problemă:** la examenul pe setul ascuns, memoria plăcii a urcat la **7.188–7.971 MB, peste limita de 7.000 MB**, cam
  17 minute. Nimic n-a căzut, temperatura a fost bună (52–55 °C). De aceea executantul a pus S58 pe `oprit`, nu pe `gata`.
- Testele: **1.168 trec, 1 sărit, 0 picate.**
- Raportul complet al executantului: `docs/rapoarte/2026-11-02_0608_S58_cod_c1.md`.

## 1. Ce a rulat noaptea

Antrenarea (experimentele #480–#489, linia `cod_c1`). „val_bpb” = câți biți îi trebuie modelului, în medie, ca să ghicească
fiecare octet de cod pe care nu l-a văzut; **cu cât e mai mic, cu atât mai bine**.

| ora | experiment | val_bpb |
|-----|-----|--------|
| 1 | #480 | 0,7086 |
| 2 | #481 | 0,6310 |
| 3 | #482 | 0,5910 |
| 4 | #483 | 0,5672 |
| 5 | #484 | 0,5473 |
| 6 | #485 | 0,5318 |
| 7 | #486 | 0,5187 |
| 8 | #487 | 0,5084 |
| 9 | #488 | 0,5007 |
| 10 | #489 | 0,4967 |

- A scăzut la fiecare oră, deci modelul a tot învățat; spre final scade tot mai încet.
- 1,2 miliarde de simboluri văzute (cam o singură trecere prin toate datele de cod).
- Placa la antrenare: maximum 6.205 MB, 64 °C — în regulă.

## 2. Examenele (o singură dată, 05:35–06:00)

- **(i) Validarea întreagă** (5.686 de fișiere de cod nevăzute): **0,514 biți pe octet**. Pe limbaje: Rust 0,438 (cel mai bun),
  Python 0,555, C 0,622.
- **(ii) Setul ascuns de 200 de probleme de programare**, câte 10 încercări pe problemă: modelul a rezolvat **3 probleme din 200**
  (pass@10 = 3/200). Din toate cele 2.000 de încercări, doar 3 au trecut (pass@1 = 0,15 %).
- Setul ascuns e acum folosit și nu se mai repetă.
- O pornire a căzut întâi după 10 secunde (unealta de validare nu știe să citească fișierul `gpt.pt`), înainte de a deschide
  setul ascuns. Executantul a folosit modelul salvat #489, verificat identic cu `gpt.pt` (149 din 149 de bucăți de greutăți la fel).

## 3. Verdictul (pre-înregistrarea `docs/preinregistrari/2026-10-31_cod_c1.md`)

Pre-înregistrarea **era deja închisă** de executant la 06:06–06:08 (are „Ce a ieșit” și „Verdictul”), așa că n-am mai închis-o
și n-am adăugat nimic în ea. Am verificat verdictul ei față de praguri:

- ÎNVAȚĂ cere biți/octet ≤ 1,10 **și** pass@10 ≥ 10/200 → 0,514 ✓, 3/200 ✗ → nu.
- NU ÎNVAȚĂ cere biți/octet > 1,40 **sau** pass@10 = 0/200 → ambele ✗ → nu.
- Pre-înregistrarea spune dinainte: biți ≤ 1,10 și pass@10 între 1 și 9 = **NECLAR**. Sunt de acord: **NECLAR**.

Pe înțeles: modelul a învățat bine **cum arată** codul (biții sunt mult sub prag), dar foarte rar scrie cod care chiar
**rezolvă** problema. O singură noapte, o singură sămânță.

## 4. Examenul de conversație

Noaptea asta **n-a avut examen de conversație** (a fost doar cod), deci nu există cele 20 de răspunsuri alese la întâmplare
de verificat azi.

## 5. Restul

- **CONTINUUM** (bucla automată): doar observă, „REPAUS” la fiecare 5 minute (ultimul ciclu #5199 la 06:35); n-a pornit nimic.
- **Placa acum** (06:40): 450 MB folosiți, 27 °C, 0 % lucru — liberă.
- **Executantul** a mai trecut la 06:28: nu rulează nimic și nu e nicio sarcină `aprobat` în coadă.
- **Git** de aseară: be0e828 (S58 pornit, 18:59), 82a4768 și eb7ff6d (supraveghetorul), 9bf2e75 (05:31, antrenarea gata),
  987643b (06:08, S58 `oprit` cu verdictul).

## 6. Testele

`CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -m pytest -q` → **1.168 trec, 1 sărit, 0 picate** (4 min 38 s).

## 7. Ce aștept de la tine, Adrian

1. **Contează cifrele S58** (NECLAR: 0,514 biți/octet, 3/200), deși placa a trecut de 7.000 MB la examenul ascuns?
   Executantul propune „da” (rezultatul e corect, nimic n-a căzut). Răspunde „da” sau „nu”.
2. **Cele două reparații mici propuse** (ca sarcini separate, doar cu aprobarea ta): (a) unealta de examen de cod să lucreze
   în loturi mai mici, ca placa să rămână sub 7.000 MB; (b) unealta de validare să știe să citească `gpt.pt`.
   Recomand să faci (a) **înainte** de orice alt examen de cod pe placă.
3. **A doua noapte pe linia `cod_c1`?** După pre-înregistrare, NECLAR înseamnă că pasul următor ar fi încă o noapte de
   antrenare. Nu pornește nimic fără „da”-ul tău.
4. De știut: paznicul Kronos nu supraveghează uneltele din `unelte/kronos_cod/`, iar executantul nu poate opri un proces
   (comanda de oprire e blocată de permisiuni). Asta a făcut ca depășirea de azi-noapte să nu poată fi oprită.
