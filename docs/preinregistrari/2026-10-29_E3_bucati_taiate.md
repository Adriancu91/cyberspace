# Pre-înregistrare: E3 — bucățile tăiate pe propozițiile utile (S44): încap mai multe în 448 de simboluri → răspunde mai bine?

<!-- scrisa: 2026-10-29T00:02:46 -->
*Scrisă la 2026-10-29 ~00:05, la S44 pasul 2, ÎNAINTE de examenul de la pasul 3 (din S44 pe placă nu s-a rulat nimic; pasul 1
a fost unealta + testele, iar estimarea de mai jos e doar o numărare pe procesor, fără model). După ce examenul începe, textul
de mai jos nu se mai schimbă; la închidere se adaugă doar „Ce a ieșit” și „Verdictul”. Nu e o antrenare: nimic nu se antrenează.*

## Cine a ales

Supraveghetorul a pus S44 în coadă la 28 oct 23:15 (granițele 2 și 5 din REGULI_CASCADA.md), din propunerea 2 a executantului
din raportul S42. Regula de tăiere și pragurile de mai jos sunt cele scrise de supraveghetor în coadă. Pre-înregistrarea,
unealta și examenul le face Claude Code (executantul).

## Întrebarea

Cu `rrf_reord`, răspunsul e în primele 3 bucăți aduse mult mai des decât în bucățile care încap în 512 − 64 = 448 de simboluri
(pe S26: 83 față de 72 din 100). **Dacă din fiecare bucată păstrăm doar propozițiile legate de întrebare, încap mai multe
bucăți — răspunde #438 corect mai des?**

## Regula de tăiere (pasul 1, `unelte/e3_taiere.py::taie`, fără model, fără întâmplare)

- Bucata se împarte în propoziții: după `.`, `!`, `?` urmate de spațiu și la rând nou.
- Scorul unei propoziții = câte rădăcini (`radacina()` din `unelte/e3_reordonare.py`) ale cuvintelor întrebării conține,
  fără cuvintele de legătură (`CUVINTE_DE_INTREBARE` din `unelte/e3_memorie.py`; dacă întrebarea n-are altele, toate cuvintele).
- Se păstrează, **în ordinea inițială**, prima propoziție (titlul/subiectul) și propozițiile cu scor ≥ 1, unite cu un spațiu.
- Dacă nicio propoziție n-are scor ≥ 1, sau dacă nu se scoate nimic, bucata rămâne exact cum era.
- Neschimbate: ordinea bucăților (`rrf_reord`, judecătorul #438), primele 3, regula „câte încap în 448” (numără textul dat
  modelului, deci bucățile tăiate), promptul S27, verificatorul S16.
- Teste fără placă: `teste/test_e3_taiere.py` (7 teste: despărțirea, ordinea, bucata neschimbată, cuvintele de legătură,
  determinismul, „câte încap” pe bucățile tăiate, examenul o singură dată).

## Ce rulează (pasul 3, o singură rulare)

`python -X utf8 unelte/e3_taiere.py examen --model 438` (refuză dacă ieșirea există deja) → `lucru/e3/examen_s44.json`:
- setul: cele 1.000 de întrebări din `validare_s29.json` (întâi 2048, apoi 1024), ca la S35; amprenta fișierului în ieșire;
- modelul: **#438** (linia `w2_conv_e3_memorie`), și ca judecător la `rrf_reord` în **ambele brațe** (aceeași ordine);
- pentru fiecare întrebare, în aceeași rulare: (i) **`intregi`** = primele 3 bucăți `rrf_reord` întregi (exact brațul (ii)
  de la S35); (ii) **`taiate`** = aceleași 3 bucăți, tăiate după regula de mai sus;
- răspunsul fără întâmplare, cel mult 80 de simboluri, nota cu verificatorul S16 (doar citit);
- se scriu: corecte, răspunsul în bucățile date, câte bucăți încap (și media), caracterele date, pe tipuri, reparate / stricate,
  la câte întrebări promptul e identic; separat 2048 (decide), 1024 (toate) și 1024 nevăzute; paznicul S17 la fiecare 50 de
  întrebări; peste 7.000 MB → oprire, `oprit`, cifrele în raport.

Placa: estimat ~15–25 de minute (S35: 1.000 de întrebări × 2 brațe în 708 s), sub 1.500 MB (S35: 734 MB).

## Criteriile (din coadă, cuvânt cu cuvânt)

Măsura care decide: Δ = procentul de răspunsuri corecte cu bucăți **tăiate** − procentul cu bucăți **întregi**, **în aceeași
rulare**, pe eșantionul **2048** fără cele văzute de #438 (la S35: niciuna văzută → toate cele 500).
- **CONFIRMAT** dacă **Δ ≥ +2,0 puncte**;
- **INFIRMAT** dacă **Δ < +0,5 puncte** (inclusiv negativ);
- **între ele: NECLAR.**

În întrebări, pe 500: CONFIRMAT = cel puțin **+10** corecte; NECLAR = +3 … +9; INFIRMAT = **+2 sau mai puțin** (inclusiv negativ).
Alături (nu decid): „răspunsul în bucățile date” în ambele brațe; câte bucăți încap în medie; pe tipuri (definiții, născut, an,
regizat, rest); reparate / stricate; eșantionul 1024.

## Spus cinstit, înainte

1. **Validarea vine din `text_v3`** (văzut de #415, deci și de #438, ca text), **iar `rrf_reord` a fost ales pe validare**.
   Diferența dintre brațe e doar tăierea, deci asta atinge puțin comparația, dar setul nu e complet curat.
2. **Estimarea pe procesor (fără model) nu arată bine pentru tăiere.** Am numărat, pe cele 500 din 2048, cu ordinea RRF
   **fără reordonare** (reordonarea cere modelul pe placă, deci e doar o aproximare a brațelor de mâine):
   - bucăți date în medie: întregi **1,95**, tăiate **2,52** (încap mai multe, cum s-a vrut);
   - răspunsul în primele 3 aduse: 392; **în bucățile date: întregi 349, tăiate 313** (−36);
   - la **64** de întrebări răspunsul era în cele 3 bucăți întregi, dar tăierea a scos chiar propoziția cu răspunsul (răspunsul
     stă des într-o propoziție fără niciun cuvânt din întrebare, de ex. a doua jumătate a unei fraze despărțite);
   - din cele 3 × 500 = 1.500 de bucăți, 988 au fost scurtate.
   Regula de tăiere e cea din coadă; **n-am schimbat-o după estimare** (ar fi fost o alegere pe validare).
3. Cu 500 de întrebări, 1 întrebare = 0,2 puncte; zgomotul e de ordinul ±1 punct.
4. Brațul `intregi` e exact brațul `rrf_reord` de la S35 (același model, aceeași căutare, același cod de răspuns): ar trebui să
   iasă **336** corecte din 500, ca atunci. Dacă nu iese, o scriu.

## Așteptările mele, în cifre

- (i) `intregi` pe 2048: **336 (67,2 %)**, plafon (răspunsul în bucățile date) 352 — exact ca la S35.
- (ii) `taiate` pe 2048: plafon **~315**, bucăți date în medie ~2,5; corecte **~300 (60 %)**, dacă #438 citește la fel de bine
  (~94 %) textul tăiat (poate citi mai prost: propozițiile lipite nu mai seamănă cu textul de la antrenare).
- **Δ cel mai probabil ~−7 puncte (−35 de întrebări), între −12 și +1**; reparate ~25, stricate ~60.
- Pe tipuri: cele mai mari pierderi la „rest” și „an” (răspunsuri în propoziții fără cuvintele întrebării); definițiile cam la
  fel (prima propoziție rămâne mereu).
- 1024 (văzute): același semn, Δ negativ.
- Timpi ca la S35; placa < 1.500 MB.
- **Verdictul așteptat: INFIRMAT ~85 %, NECLAR ~10 %, CONFIRMAT ~5 %.**
