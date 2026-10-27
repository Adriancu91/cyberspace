# Raport S35 — Citirea cu `rrf_reord` pe validare: **NECLAR** (Δ +1,0 punct)

*Scris de executant (Claude Code), 27 octombrie 2026, 13:03.*

## Pe scurt

Am verificat dacă felul nou de a aduce bucățile de text (`rrf_reord`) îl ajută pe #438 să răspundă mai bine și pe un alt set
de întrebări decât cel de la S33. Pe cele 500 de întrebări din eșantionul 2048 (niciuna văzută de #438 la antrenare):
**331 corecte cu căutarea veche, 336 cu cea nouă: +5 întrebări, +1,0 punct.** Pragul de confirmare era +2,0, cel de
infirmare +0,5, deci verdictul e **NECLAR**. Câștigul de +6 din 100 de la S33 venea mai ales din setul S26 (multe definiții).

## Ce a rulat

1. **Pasul 1 (procesor, înainte):** numărarea întrebărilor văzute de #438 la antrenare: 2048 → **0** din 500, 1024 → **485**
   din 500. Deci decide 2048 întreg.
2. **Pasul 2:** pre-înregistrarea `docs/preinregistrari/2026-10-27_E3_citire_validare.md`, urcată înainte (commit `14cd40e`),
   cu opțiunea nouă `examen --set validare` și testul ei fără placă.
3. **Pasul 3, examenul, o singură rulare** prin cascadă: `unelte/e3_citire_reord.py examen --model 438 --set validare`,
   12:36:26–12:48:16 (**708 s**, cod 0) → `lucru/e3/examen_s35.json` (nu e în Git). Placa: **734 MB** (sub 7.000), RAM 1,1 GB.

## Cifrele

| eșantion | varianta | corecte din 500 | răspunsul în bucățile care încap | corecte dintre acestea | corecte dintre celelalte |
|---|---|---|---|---|---|
| **2048 (decide)** | (i) `s25` | **331 (66,2 %)** | 343 | 323 | 8 din 157 |
| **2048 (decide)** | (ii) `rrf_reord` | **336 (67,2 %)** | 352 | 329 | 7 din 148 |
| 1024 (văzute) | (i) `s25` | 365 (73,0 %) | 352 | 338 | 27 din 148 |
| 1024 (văzute) | (ii) `rrf_reord` | 345 (69,0 %) | 345 | 334 | 11 din 155 |

- Reperul S29: același loc la **toate cele 1.000** de întrebări, la ambele variante (căutarea e fără întâmplare, cum trebuia).
- 2048: **69 reparate, 64 stricate** (net +5); la 113 bucățile date sunt aceleași.
- Pe tipuri, 2048 (`s25` → `rrf_reord`): definiții 151 → **169** din 252 (+18); născut 36 → 36 din 45; an 12 → 10 din 21;
  regizat 9 → 15 din 23 (+6); **rest 123 → 106 din 159 (−17)**.
- 1024 (văzute de #438): Δ = **−4,0 puncte** (49 reparate, 69 stricate); cele 15 nevăzute: 11 → 10.
- Timpi (mediane): căutarea 0,075 s, judecătorul 0,136 s, răspunsul 0,132 / 0,142 s.

Așteptările mele (scrise înainte): `s25` ~320, `rrf_reord` ~325, **Δ ~+1,0**; a ieșit 331 / 336, **Δ +1,0**. Am greșit la
reparate/stricate (am spus ~35 / ~30, au ieșit 69 / 64) și la mărimea pierderii pe „rest” (am spus ~−9, a ieșit −17).

## Verdictul (strict după pre-înregistrare)

**NECLAR:** Δ = +1,0 punct (+5 din 500), între +0,5 și +2,0.

- Câștigul de la S33 **nu se păstrează la aceeași mărime** pe validare: de 6 ori mai mic.
- Reordonarea ajută clar la **definiții** (+18) și **regizat** (+6), dar strică la **„rest”** (−17) și **an** (−2).
- #438 citește bine ce primește (~94 % din cele cu răspunsul în bucăți); limita e găsirea, nu cititul.
- Spus cinstit: alegerea `rrf_reord` s-a făcut pe validare, iar validarea vine din `text_v3`, pe care #415/#438 l-a văzut.

## Testele

`CUDA_VISIBLE_DEVICES=-1 python -m pytest -q`: **952 trec, 1 sărit**, 224 s.

## Ce propun mai departe

1. **Reordonarea doar la definiții** (și regizat): pe tipul întrebării, `rrf_reord` doar unde ajută, `s25` în rest. Din
   cifrele de aici ar da în jur de +24 față de `s25` pe 2048, dar e ales pe aceleași date, deci ar trebui verificat pe alt
   set (lista de întrebări nefolosite e aproape goală, deci cere întâi un set nou).
2. Altfel, S32 (motorul fără PyTorch) e următoarea în coadă și nu depinde de asta.

## Ce aștept de la tine (Adrian)

Nimic urgent. Dacă vrei pasul 1 de mai sus, spune „da” și supraveghetorul îl pune în coadă.
