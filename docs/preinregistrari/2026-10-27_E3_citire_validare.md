# Pre-înregistrare: E3 citește cu `rrf_reord` pe validare (S35) — cât din +6 de la S33 rămâne pe un set cu alt amestec?

<!-- scrisa: 2026-10-27T12:35:00 -->
*Scrisă la 2026-10-27 ~12:35, la S35 pasul 2, ÎNAINTE de examenul de la pasul 3 (din S35 pe placă nu s-a rulat nimic;
pasul 1 a fost doar o numărare pe procesor). După ce examenul începe, textul de mai jos nu se mai schimbă; la închidere se
adaugă doar „Ce a ieșit” și „Verdictul”. Nu e o antrenare: nimic nu se antrenează.*

## Cine a ales

Supraveghetorul a pus S35 în coadă la 27 oct 11:15 (granița 2 din REGULI_CASCADA.md), din propunerea 2 a executantului din
raportul S33 (`docs/rapoarte/2026-10-27_0842_S33_E3_citire_reord.md`). Pragurile de mai jos sunt cele scrise de supraveghetor
în coadă. Pre-înregistrarea și examenul le face Claude Code (executantul).

## Întrebarea

La S33, #438 a răspuns corect la 66 din cele 100 S26 cu bucățile `rrf_reord`, față de 60 cu căutarea S25 simplă (+6, la
limită), aproape tot câștigul din definiții. **Rămâne câștigul la citire și pe un set cu alt amestec de tipuri — validarea
S29 — sau era în mare parte de la setul S26?**

## Pasul 1 (procesor, deja făcut): câte întrebări din validare a văzut #438 la antrenare

Din `lucru/e3/validare_s29.json` (eșantioanele 2048 și 1024, câte 500 de întrebări, nicio întrebare comună între ele),
comparate cu `lucru/e3/date_antrenare_s27.jsonl` (cele 14.540 de exemple E3 ale lui #438, S27):

| eșantion | întrebări | văzute de #438 (aceeași întrebare, literă cu literă) | după normalizare (litere mici, fără semne) | perechea întrebare + răspuns |
|---|---|---|---|---|
| **2048** | 500 | **0** | 0 | 0 |
| 1024 | 500 | **485** | 485 | 485 |

Verificat și în amestecul complet al antrenării S27 (`amestec_s27.jsonl`, 37.092 de rânduri, cu perechile vechi): 2048 → 0,
1024 → 487. **Deci eșantionul 1024 e aproape tot văzut de #438** (a intrat în datele E3 la S27), iar **2048 e curat față de
antrenarea lui #438**. Din măsura care decide nu se scoate nicio întrebare: decid toate cele **500** din 2048.

Amestecul pe 2048 (pentru comparație cu S26, unde definițiile erau 54 % și „restul” 19 %): definiții 252 (50,4 %), născut 45,
an 21, regizat 23, **rest 159 (31,8 %)**.

## Ce rulează (pasul 3, o singură rulare)

`python -X utf8 unelte/e3_citire_reord.py examen --model 438 --set validare` (opțiune nouă, cu test fără placă,
`teste/test_e3_citire_reord.py::test_examenul_pe_validare_scoate_cele_vazute`; refuză dacă ieșirea există deja) →
`lucru/e3/examen_s35.json`:
- setul: cele 1.000 de întrebări din `validare_s29.json` (întâi 2048, apoi 1024), amprenta fișierului scrisă în ieșire;
- modelul: **#438** (linia `w2_conv_e3_memorie`), care e și judecătorul la reordonare (ca la S29 și S33);
- pentru fiecare întrebare, în aceeași rulare: (i) **`s25`** = primele 3 bucăți ale căutării S25 simple
  (`nume_obligatorii_liste`); (ii) **`rrf_reord`** = RRF cu indexul cu rădăcini + primele 20 reordonate după judecătorul #438;
- același cod și aceeași notare ca la S33: din primele 3, câte încap în 448 de simboluri, promptul S27, răspunsul fără
  întâmplare, cel mult 80 de simboluri, verificatorul S16 (`unelte/verificator_text.py`, doar citit);
- se scriu: corecte, corecte dintre cele cu răspunsul în bucățile care încap și dintre cele fără, pe tipuri, reparate /
  stricate, timpi, memoria plăcii; separat pentru 2048 (decide), 1024 (toate) și 1024 nevăzute (15); paznicul S17 la fiecare
  50 de întrebări; peste 7.000 MB → oprire, `oprit`, cifrele în raport;
- verificarea reperului: locul primului răspuns bun la fiecare variantă trebuie să iasă la fel ca în `validare_s29.json`
  (căutarea și judecătorul sunt fără întâmplare).

Placa: estimat 10–20 de minute (S33: 100 de întrebări în 77 s), sub 1.500 MB (S33: 732 MB alocați).

## Criteriile (din coadă, cuvânt cu cuvânt)

Măsura care decide: pe eșantionul **2048** (fără cele văzute de #438 — aici niciuna), Δ = procentul de răspunsuri corecte cu
`rrf_reord` − procentul cu `s25`, **în aceeași rulare**.
- **CONFIRMAT** (reordonarea ajută la citire și în afara S26) dacă **Δ ≥ +2,0 puncte**;
- **INFIRMAT** dacă **Δ < +0,5 puncte** (inclusiv negativ);
- **între ele: NECLAR.**

În întrebări, pe 500: CONFIRMAT = cel puțin **+10** corecte; NECLAR = +3 … +9; INFIRMAT = **+2 sau mai puțin** (inclusiv
negativ). Alături (nu decide): eșantionul 1024, pe tipuri (definiții, născut, an, regizat, rest), reparate / stricate.

## Spus cinstit, înainte

1. **Alegerea `rrf_reord` s-a făcut pe validare** (782 față de 778 la k = 3, pe 1.000), deci validarea nu e complet curată
   pentru variantă — și totuși acolo câștigul la găsire a fost mic.
2. **Validarea vine din `text_v3`, pe care #415 (deci și #438) l-a văzut** ca text; întrebările din 2048 nu le-a văzut.
3. **Eșantionul 1024 e aproape tot văzut de #438 ca întrebare + răspuns** (485 din 500): acolo cititul e „ajutat” și cifra nu
   spune mare lucru despre citirea adevărată; o scriu doar alături.
4. **Plafonul pe 2048 abia se mișcă** (din locurile S29, „răspunsul în bucățile care încap”): S25 simplă **343**, `rrf_reord`
   **352** (+9, +1,8 puncte). Definițiile urcă 158 → 181, regizat 10 → 16, dar „restul” scade 125 → 113, născut 38 → 36,
   an 12 → 6. Deci chiar dacă #438 citește perfect, Δ e aproape de pragul de confirmare doar dacă cititul e la fel de bun pe
   bucățile noi.
5. Cu 500 de întrebări, 1 întrebare = 0,2 puncte; zgomotul e de ordinul ±1 punct.

## Așteptările mele, în cifre

- Reperul S29: același loc la (aproape) toate cele 1.000 de întrebări, la ambele variante.
- (i) `s25` pe 2048: plafon 343; corecte **~320 (64 %)** (~93 % din plafon, ca la S33).
- (ii) `rrf_reord` pe 2048: plafon 352; corecte **~325 (65 %)**, cititul cam la fel sau puțin mai slab pe bucățile urcate.
- **Δ cel mai probabil ~+1,0 punct (+5 întrebări), între −1,0 și +2,5**; reparate ~35, stricate ~30.
- Pe tipuri: câștig la definiții (~+15) și regizat (~+4), pierdere la rest (~−9) și an (~−4).
- 1024 (văzute): ambele variante mult peste 2048 (~75–85 %), Δ în jur de 0 (plafonul `rrf_reord` e chiar mai mic: 345 față de 352).
- Timpi ca la S33 (căutarea ~0,1 s, judecătorul ~0,14 s, răspunsul ~0,2 s); placa < 1.500 MB.
- **Verdictul așteptat: NECLAR ~50 %, INFIRMAT ~35 %, CONFIRMAT ~15 %.**

## Ce a ieșit

*Adăugat la 2026-10-27 13:03, din jurnalul Kronos (lucru/jurnal/experimente.jsonl) și din jurnalul CONTINUUM pe bune. Verdictul se scrie dedesubt.*

Niciun experiment Kronos în perioada asta.

Niciun ciclu CONTINUUM pe bune în perioada asta.

**Examenul** (o singură rulare, 12:36:26–12:48:16, 708 s, cod 0, `unelte/e3_citire_reord.py examen --model 438 --set validare`
→ `lucru/e3/examen_s35.json`; amprenta `validare_s29.json` `d036774a…2dca`; #438, linia `w2_conv_e3_memorie`; văzute de #438:
2048 → 0, 1024 → 485):

| eșantion | varianta | corecte din 500 | răspunsul în bucățile care încap | corecte dintre acestea | corecte dintre celelalte |
|---|---|---|---|---|---|
| **2048 (decide)** | (i) `s25` | **331 (66,2 %)** | 343 | 323 | 8 din 157 |
| **2048 (decide)** | (ii) `rrf_reord` | **336 (67,2 %)** | 352 | 329 | 7 din 148 |
| 1024 (văzute) | (i) `s25` | 365 (73,0 %) | 352 | 338 | 27 din 148 |
| 1024 (văzute) | (ii) `rrf_reord` | 345 (69,0 %) | 345 | 334 | 11 din 155 |

- Reperul S29: **același loc la toate 1.000 de întrebări**, la ambele variante (1000 / 1000).
- 2048: **69 reparate, 64 stricate** (net +5); la 113 întrebări bucățile date sunt aceleași.
- Pe tipuri, 2048 (corecte, (i) → (ii)): definiții 151 → **169** din 252 (+18); născut 36 → 36 din 45; an 12 → 10 din 21;
  regizat 9 → 15 din 23 (+6); **rest 123 → 106 din 159 (−17)**.
- 1024: Δ = **−4,0 puncte** (49 reparate, 69 stricate); cele 15 nevăzute: 11 → 10.
- Timpi (mediane): căutarea 0,075 s, judecătorul 0,136 s, răspunsul 0,132 s (i) / 0,142 s (ii). Placa: 734 MB alocați
  de PyTorch; RAM 1,1 GB.

## Verdictul

**NECLAR:** pe eșantionul 2048 (500 de întrebări, niciuna văzută de #438), #438 cu `rrf_reord` răspunde corect la **336**,
față de **331** cu `s25`, în aceeași rulare: **Δ = +1,0 punct (+5 întrebări)**, între +0,5 și +2,0.

Ce trebuie spus la fel de clar:
- **Câștigul de la S33 (+6 din 100) nu se păstrează la aceeași mărime pe validare:** aici e +1 punct, de 6 ori mai mic,
  exact cât am așteptat (~+1,0).
- Reordonarea **mută mult**: 69 reparate și 64 stricate. Câștigă la definiții (+18) și regizat (+6), pierde aproape tot
  înapoi la „rest” (−17) și an (−2). Pe un set cu mai puțin de jumătate definiții, câștigul se topește.
- #438 citește bine ce primește (94 % din cele cu răspunsul în bucăți, la ambele variante); limita e tot plafonul găsirii.
- Pe 1024 (văzute de #438 la antrenare) reordonarea pierde 4 puncte, dar setul nu spune mare lucru despre cititul adevărat.
