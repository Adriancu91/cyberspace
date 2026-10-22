# S17 — E1: „întrebări născute de Kronos” — NECLAR ((b2) 13/50), fără regresie

*Scris la 22 oct 2026, 21:10, de executant (Claude Code, rularea automată a cozii). Pre-înregistrarea:
`docs/preinregistrari/2026-10-22_E1_intrebari_nascute.md` (închisă acum, cu „Ce a ieșit” și „Verdictul”).*

## Pe scurt

- Rularea a mers de la 15:29 la 20:57 (5 h 28 min), toți cei 6 pași cu cod 0. Placa: cel mult **6.274 MB** și **64 °C**.
- Kronos a scris singur 29.896 de întrebări; după filtre (toate fără LLM) au rămas **516**, cu **452 de tipuri distincte**
  (pe primele 4 cuvinte; 400 pe tipar).
- Antrenat 3 ore din #415 cu ele (+ cele 27.468 din `text_v3`) → **#425**.
- **(b2) tipuri nevăzute: 13/50** (de la 6/50 la #415). (e) 29/30. Fără regresie: noaptea 10 49/50 și 20/20, S4 40/60.
- **Verdict: NECLAR** — peste pragul de infirmare (≤ 9), sub cel de confirmare (≥ 16). Criteriul spune: o singură repetare
  cu 3× date, apoi decizie. **Aștept de la Adrian / supraveghetor:** dacă pun repetarea în coadă (S18?).

## Ce a rulat (o singură comandă, pornită de cascadă la 15:29:11, procesul 18480)

`.venv/Scripts/python.exe -X utf8 unelte/e1_intrebari_nascute.py noaptea`; pașii, din `lucru/e1/noaptea.json`:

| pas | de la | până la | cod |
|---|---|---|---|
| 1. generatorul (1 oră din #415, linia `w2_e1_generator`) → #422 | 15:29 | 16:32 | 0 |
| 2. generarea (60 min) | 16:32 | 17:33 | 0 |
| 3. filtrele (dus-întorsul a durat 9,1 min) | 17:33 | 17:42 | 0 |
| 4. antrenarea 3 ore din #415 (linia `w2_conv_auto_v1`) → #423, #424, #425 | 17:42 | 20:54 | 0 |
| 5. examenele S15, S4, noaptea 10 (verificatorul din S16) | 20:54 | 20:56 | 0 |
| 6. validările (română, cod, povești) → #426 | 20:56 | 20:57 | 0 |

Placa (fișierele `lucru/w2_e1_generator/placa_20261022_1529.csv` și `lucru/w2_conv_auto_v1/placa_20261022_1742.csv`):
generatorul cel mult 6.196 MB, antrenarea cel mult 6.274 MB; temperatura cel mult 64 °C. Sub 7.000 MB și 83 °C.

## 1. Generatorul (#422)

val_bpb 0,4438 (de la 0,4411 la #415), fapte 149, fapte noi 64, 21.277 de pași. E doar unealta care scrie întrebări.

## 2. Generarea

- 3.852 de bucăți posibile pe 2.000 de articole noi; în 60 de minute s-au făcut **3.737** (1.967 de articole atinse).
  **Au rămas neîncercate 115 bucăți** (limita de timp).
- **29.896 de întrebări-candidat** (8 pe bucată, temperatura 1,0, nucleu 0,9, sămânța 1022).

## 3. Filtrele (fără LLM) — câte au căzut la fiecare

| filtru | au căzut | au rămas |
|---|---|---|
| (început) | — | 29.896 |
| (0) formă | 2.250 | 27.646 |
| (iii) duplicate | 12.830 | 14.816 |
| (ii) noutate — primele 4 cuvinte | 4.188 | 10.628 |
| (ii) noutate — tiparul (mai strict) | 3.373 | 7.255 |
| (iv) motorul de română | 1.333 | 5.922 |
| (i) dus-întors (#415 răspunde, verificatorul ≥ 0,8) | 5.406 | **516** |

- Dus-întorsul: toate cele 5.922 încercate (0 neîncercate); trec 516 = 8,7 %.
- Păstrate: **516** (sub plafonul de 3.300). Tipuri distincte: **452 pe primele 4 cuvinte, 400 pe tipar**.
- Cele mai dese tipare: „în ce oraș se” 18, „ce e” 9, „în ce” 7, „toluca de” 5, „în ce provincie se” 5, „ce se află” 5,
  „ce sat are” 4, „ce tip de” 4, „ce nume are” 4, „ce importanță are” 3, „cine a lansat” 2, „când a fost ales” 2 …
- **De știut:** unele „tipare” sunt de fapt nume scrise cu literă mică la început de întrebare („toluca de”, „happy”,
  „bmw”, „pițigoiul cu obraji galbeni”), deci 400 e o numărătoare largă; tipurile reale sunt mai puține, dar sigur peste 20.
- Păstrate cu tipar din (b2): „în ce oraș se” 18, „cine a pictat” 1. Nu e scurgere (textele de examen: 0 în cele păstrate,
  verificat de unealtă; începuturi din antrenare: 0), dar spune de unde poate veni o parte din creștere.
- Datele de antrenare: `date/conversatie/auto_v1/antrenare.jsonl` = 27.468 (`text_v3`) + 516 = **27.984** de perechi.

## 4. Antrenarea (3 ore din #415, `config/conv_w2_auto_v1.toml`)

| ora | # | val_bpb | fapte | fapte noi | nota prof. | memorie |
|---|---|---|---|---|---|---|
| 0 (#415) | — | 0,4411 | 150 | 68 | 4,17 | — |
| 1 | 423 | 0,4430 | 150 | 72 | 4,17 | 5.308 MB |
| 2 | 424 | 0,4419 | 150 | 74 | 4,58 | 5.374 MB |
| 3 | 425 | 0,4436 | 149 | 72 | 4,33 | 5.374 MB |

Toate trei păstrate. 63.806 de pași, 392 M de simboluri.

## 5. Examenele pe #425 (notate de verificatorul din S16, fără Qwen)

| examen | #425 | #415 (baseline, același judecător) |
|---|---|---|
| S15 (b2), 50 de tipuri nevăzute | **13/50** | 6/50 |
| S15 (e), 30 din tipurile S11 | **29/30** | 30/30 |
| S4 (60) | **40/60** (a 11, b 4, c 14, d 11; „Nu scrie” pe nedrept 6/45) | 38/60 (a 11, b 2, c 13, d 12; 9/45) |
| noaptea 10 | **49/50, 20/20, refuz greșit 0/50** | 50/50, 20/20, 0/50 |

S15 (b2) pe tipuri, la #425: post 5/5, funcție 3/6, canal 2/4, pictor 2/3, personaj 1/2; **0** la țară (0/5), oraș (0/5),
premiu, actori, profesie (0/6), producător, câștigător, soț. „Nu scrie” pe nedrept la S15: 11.
Deci, deși 18 întrebări păstrate erau „în ce oraș se …”, tipurile țară/oraș din (b2) au rămas 0/5.

**De știut la citire:** câteva răspunsuri numărate corecte de verificator sunt lungi, cu răspunsul înăuntru, de exemplu
„Canal a avut premiera pe 16 decembrie 2012 pe Cartoon Network.” sau „Pictură în ulei pe pânză realizată în 1895 de
artistul francez Paul Cézanne.” Verificatorul (acoperire ≥ 0,8) le primește, așa cum s-a stabilit la S16. Un om ar putea
să nu le dea pe toate ca bune. Toate răspunsurile: `lucru/e1/examene_425_20261022_205650.json`.

## 6. Validările (#426, pe #425) și „să nu uite”

| ce | #425 | prag | |
|---|---|---|---|
| media română (bpb) | 1,3090 | ≤ 1,3133 | ✓ |
| media cod (bpb) | 0,7254 | ≤ 0,8174 | ✓ |
| povești (bpb) | 0,4436 | ≤ 0,47 | ✓ |
| fapte noi | 72 | ≥ 65 | ✓ |

(Fișierul: `lucru/examen_validari_ws/experiment_425_20261022_205706.json`.)

## Verdictul (strict după pragurile pre-înregistrării)

- CONFIRMAT cere (b2) ≥ 16/50 → **nu** (13).
- INFIRMAT cere (b2) ≤ 9/50 sau tipuri distincte < 20 → **nu** (13; 452 / 400 tipuri).
- (e) ≥ 27/30 → da (29). Fără regresie (noaptea 10 ≥ 45/50, ≥ 16/20, ≤ 5/50; S4 (a) ≥ 9, (c) ≥ 11) → da.

**NECLAR.** După criteriu: o singură repetare cu 3× date, apoi decizie.

Față de așteptările mele din pre-înregistrare: păstrate 516 (așteptam 500–2.000, la limita de jos; dus-întorsul a lăsat
doar 8,7 %, nu 20–35 %); (b2) 13 (așteptam 7–11 — a ieșit peste); verdictul neclar (îi dădeam ~35 %, infirmatului ~60 %).

## Testele

`CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -m pytest`: **886 trec, 1 sărit** (3 min 36 s).

## Ce urmează / ce aștept de la Adrian

1. **Repetarea cu 3× date** (cerută de criteriu). Observație pentru cine o scrie: la rata de acum (516 din ~30.000),
   3× date (~1.550 de întrebări) înseamnă ~90.000 de candidați, adică ~3 ore de generare pe placă, nu una; sau mai multe
   articole. O pune în coadă supraveghetorul, cu „da”-ul tău; eu n-o pornesc singur.
2. De hotărât, odată cu ea: dacă răspunsurile lungi „cu răspunsul înăuntru” (secțiunea 5) se numără bune, sau verificatorul
   se face mai strict pentru repetare (asta ar schimba și baseline-ul, deci trebuie hotărât **înainte**).
3. #425 nu înlocuiește #407 în interfață (nu s-a cerut).
