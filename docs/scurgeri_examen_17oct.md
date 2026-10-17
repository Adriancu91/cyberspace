# Scurgeri în examen: cât din validări apare și în datele de antrenare (17 octombrie 2026)

*Unealta: `unelte/scurgeri_examen.py`, doar pe procesor, cu prioritate scăzută lângă W2. Toate cifrele sunt în
`lucru/scurgeri_examen/scurgeri_20261017_222611.json`, iar textele identice în întregime în
`identice_intregi_20261017.json`. Nimic din examen, din validări sau din jurnal nu s-a schimbat.*

## Ce s-a măsurat

- **Validările:** aceleași primele 100.000 de litere pe care le notează examenul pe validări
  (`unelte/examen_validari_ws.py`), plus validarea întreagă a examenului oficial (TinyStories R2, 2.457 de povești).
- **Antrenarea:** exact ce a văzut Kronos W2: amestecul `date/ws/amestec/antrenare.txt` (4,78 miliarde de litere) și
  hrana.
- **Bucățile:** orice șir de 50, respectiv 200 de litere la rând dintr-un text de validare se caută literă cu literă în
  antrenare. „Litere acoperite” înseamnă cât din validare stă într-o bucată găsită. „Text aproape copiat” înseamnă un
  text cu cel puțin jumătate din litere acoperite.
- **De ce două lungimi:** 50 de litere prind și expresiile-tipar („Once upon a time, there was a little girl named
  Lily”). 200 de litere la rând nu ies dintr-un tipar, ci doar dintr-o copiere.

## Rezultatul

| validarea | texte | litere acoperite, 50 | aproape copiate, 50 | litere acoperite, 200 | aproape copiate, 200 |
|---|---|---|---|---|---|
| povești (examen pe validări) | 118 | 35,5% | 28,0% | **0,0%** | 0,0% |
| **povești, examenul oficial întreg** | 2.457 | 34,4% | 26,0% | **0,1%** | **0,0%** |
| română: Wikipedia | 21 | 20,8% | 28,6% | 2,4% | 9,5% (2 texte) |
| română: web | 31 | 3,5% | 0,0% | 2,0% | 0,0% |
| română: cărți | 8 | 4,2% | 0,0% | 1,6% | 0,0% |
| **română: fabule** | 71 | **99,0%** | **100%** | **74,9%** | **87,3%** |
| traducere | 314 | 7,0% | 3,8% | 0,3% | 0,3% |
| cod Python | 9 | 14,2% | 22,2% | 1,8% | 11,1% (1 text) |
| sarcini de cod | 79 | 25,6% | 7,6% | 0,0% | 0,0% |

**Niciun text de validare nu apare întreg, identic, în antrenare** (0 din 3.108). Asta nici nu era de așteptat:
curățarea a scos dublurile exacte. Scurgerile de mai sus sunt copii aproape identice sau bucăți lungi comune.

## Ce înseamnă, pe fiecare

- **Examenul oficial (TinyStories R2): curat.** La 50 de litere se suprapune 34%, dar la 200 de litere aproape nimic
  (0,1%). Suprapunerea vine din frazele-tipar ale TinyStories, care se repetă în milioane de povești, nu din povești
  copiate. Propunerea mea: **nu schimbăm nimic** la `examen_bpb.py`.
- **Fabulele: scurse.** Trei sferturi din litere stau în bucăți de 200 de litere care există și în antrenare, iar 62
  din 71 de fabule sunt aproape copiate. Fabulele sunt 3 milioane de texte generate de alt model. Curățarea a scos
  664.231 de dubluri exacte, dar au rămas mii de variante aproape identice, care ajung și în validare. **De aici vine
  0,09.** E memorie, nu pricepere.
- **Wikipedia: puțin, și doar la paginile-listă.** Cele 2 texte aproape copiate la 200 de litere sunt pagini de ani și
  secole („Milenii: Mileniul I î.Hr. - Mileniul I - …”), care au aceeași navigație lungă ca vecinele lor din antrenare.
  Articolele obișnuite nu sunt copiate. La 50 de litere, 28,6% sunt tot pagini de felul ăsta și articole-șablon
  (sate, comune).
- **Codul Python: 1 fișier din 9.** Începe cu aceeași notă de licență lungă (Apache, Intel 2018) ca multe fișiere din
  antrenare. Restul e curat. Eșantionul e mic: 100.000 de litere înseamnă doar 9 fișiere.
- **Web, cărți, traducere, sarcini de cod: curate** (cel mult 2% la 200 de litere).

## Propunerea de validare curată (nu am schimbat nimic)

**Regula** (aceeași peste tot): un text de validare e „curat” dacă **nicio bucată de 200 de litere nu e în antrenare**
și **sub jumătate din el e acoperit de bucăți de 50**. Pe primele 100.000 de litere de acum, ar rămâne:

| validarea | texte curate din primele 100.000 de litere |
|---|---|
| povești (oficial, întreg) | 1.809 din 2.457 |
| Wikipedia | 11 din 21 |
| web | 27 din 31 |
| cărți | 7 din 8 |
| **fabule** | **0 din 71** |
| traducere | 302 din 314 |
| cod Python | 5 din 9 |
| sarcini de cod | 73 din 79 |

Concret, propun:

1. **Examenul oficial (`examen_bpb.py`): neschimbat.** La 200 de litere e curat, iar schimbarea lui ar rupe toate
   comparațiile vechi. Dacă vrei totuși o variantă curată, se poate nota alături ca informație, fără să-l ating.
2. **Fabulele:** **scoase din concluzii pentru totdeauna** (deja nu intrau). Sau, dacă vrei să rămână, o
   `validare_curata.txt` făcută din tot fișierul de validare (35 MB, ~23.500 de fabule), cu regula de mai sus. Pe
   eșantionul de acum nu rămâne niciuna, deci probabil ar rămâne foarte puține. Recomand **scoaterea**.
3. **Wikipedia, cod Python și restul:** câte o `validare_curata.txt` lângă cea veche, făcută din **tot** fișierul de
   validare, cu regula de mai sus, din care examenul ia tot primele 100.000 de litere.
   - Examenul pe validări (`unelte/examen_validari_ws.py`, nu `kronos/` și nu `examen_bpb.py`) ar nota **amândouă**:
     notele vechi, ca rândurile vechi din jurnal să rămână comparabile, și notele curate, sub nume noi (de exemplu
     `bpb_romana_curat`).
   - Costă o trecere prin antrenare (~45 de minute pe procesor, ca acum), iar validările vechi rămân neatinse.
4. **Reperul natural îl dă examenul neutru:** aceeași căutare pe texte scrise după 12 octombrie 2026 arată cât se
   potrivește fără nicio scurgere, doar din expresii comune.

Pașii 2 și 3 îi fac doar după „da”-ul lui Adrian.

## Aplicat (duminică, 18 octombrie 2026, după „da”-ul lui Adrian)

- **Fabulele ies din examenul pe validări** și nu primesc variantă curată.
- **Validările curate sunt scrise** cu `unelte/validari_curate.py`, din **tot** fișierul fiecărei validări, cu regula de
  mai sus. Fiecare stă în `validare_curata.txt`, lângă `validare.txt`, care rămâne neatins. Raportul, cu amprentele
  (sha256), e în `date/ws/curat/validari_curate.json`.

| validarea | texte | texte curate | litere păstrate | sha256 (început) |
|---|---|---|---|---|
| povești (TinyStories R2) | 2.457 | 1.809 | 75,8% | `d2a6e8459406` |
| română: Wikipedia | 2.748 | 1.668 | 71,2% | `24916dc66a4e` |
| română: web | 8.858 | 8.034 | 84,1% | `9c5e4d2f6a15` |
| română: cărți | 98 | 96 | 94,0% | `9eaef8570113` |
| traducere | 3.882 | 3.712 | 95,5% | `69374134bf19` |
| cod Python | 1.454 | 1.220 | 78,0% | `3e3827ce3648` |
| sarcini de cod | 468 | 442 | 95,8% | `7b908ef68e8c` |

- **Examenul oficial (`module/examen_bpb.py`) și validarea lui nu se schimbă.** Varianta curată a poveștilor se
  notează doar în examenul pe validări, ca informație.
- **Examenul pe validări (`unelte/examen_validari_ws.py`)** notează, pe rândurile noi din jurnal, și variantele
  curate, sub nume noi: `bpb_<validare>_curat` și mediile `bpb_romana_curat`, `bpb_cod_curat`. Notele vechi
  (`bpb_romana`, `bpb_cod`) se socotesc exact ca înainte, iar rândurile vechi din jurnal nu se ating. Schimbarea intră
  după închiderea nopții 4 (18 octombrie, 07:45), ca examenul de dimineață al copiei răcite să rămână cel
  pre-înregistrat.
