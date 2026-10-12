# Școala de cod v0.4: pregătirea pe tokenizer-ul nou (luni, 12 octombrie 2026, seara)

*Doar pregătire și teste, pe procesor. Școala NU a pornit și placa video n-a fost atinsă (pe ea rula noaptea W1).
Fișierele cu amprentă (abecedarul, setul sacru, generatorul de teste, sandbox-ul) NU s-au schimbat: paznicul școlii
nu are nimic de zis. Rezultatele negative sunt trecute la fel ca cele bune.*

## Ce s-a făcut

1. **Ramura `kronos-cod` a primit tot ce s-a făcut în main** (tokenizer-ul nou, datele, CONTINUUM v2, interfața), printr-o
   unire cu un singur conflict, în README (păstrate ambele părți). Ramura rămâne separată.
2. **`config/scoala_cod_v04.toml`**: aceeași școală ca v0.3 (aceleași niveluri, seturi, reguli), cu:
   - tokenizer-ul nou (`date/ws/bpe_16384.json`);
   - modelul de pornire = modelul liniei W2 (`lucru/cod_v04/pornire/model_w2.pt`), care **încă nu există**: W2 n-a pornit;
   - „poveștile” din lot = amestecul pe care învață W2;
   - paznicul la 7.000 MB și 83 °C;
   - `prag_regresie = 0,60`, pus provizoriu: se hotărăște după ce se știe val_bpb al lui W2.
3. **`unelte/vocabular_cod_ws.py`** (pasul 0, fără model): reface împărțirea în bucăți a abecedarului, a setului sacru
   și a seturilor de examen și verifică problema veche. Cifrele: `lucru/cod_v04/vocabular_ws.json`.
4. **`unelte/proba_copiere_cod.py`**: o încercare pe un model de jucărie, pe procesor (mai jos).
5. **Teste:** `teste/test_cod_v04.py` (7), între care: elevul școlii încarcă, scrie și antrenează un model cu tokenizer-ul nou.

## Împărțirea refăcută (tokenizer-ul nou față de cel vechi)

| | Nou | Vechi |
|---|---|---|
| Abecedarul trece prin tokenizer și iese identic | da | da |
| Abecedarul întreg, în bucăți | 4.584 | 6.195 |
| Un episod, în medie | 41,6 | 56,8 |
| Regula scurtă cu „EXAMPLES:” | 43 | 53 |
| Numerele 0–99 dintr-o singură bucată | 100 din 100 | 10 din 100 |
| Numerele 100–999 dintr-o singură bucată | 900 din 900 | 0 din 900 |
| Cuvintele nivelului 0w: cuvântul din răspuns e o singură bucată | 103 din 116 | 13 din 116 |
| Cuvintele lungi (adversarial): o singură bucată | 4 din 35 | 0 din 35 |

- **Contextul nu mai e o problemă.** W2 vede 512 bucăți. La toate cele 9 niveluri ale pilotului și la toate seturile
  (văzut, nevăzut, adversarial, sacru: 1.075 de sarcini), în față încap cele 2 exemple, iar cel mai lung text, cu tot
  cu cele 48 de bucăți pe care le poate scrie modelul, are 222 din 512 (la v0.1 era 256 din 256). E loc și de 4–5 exemple.
- **Numerele sunt rezolvate.** „show 46” = `show`, ` `, `46`, iar răspunsul e chiar bucata `46`: modelul are de unde
  s-o copieze. Cu tokenizer-ul vechi, „46” erau două bucăți.
- Cuvintele rămase rupte și cu tokenizer-ul nou (13 din 116): lamp, gum, hut, kid, lid, mop, toe, wig, goat, rose,
  shoe, snail, toad. Cele lungi sunt aproape toate rupte (elephant e întreg; dinosaur, umbrella, pancake nu).

## Problema veche: cuvintele între ghilimele

**Ce era:** în v0.3 școala s-a rupt la nivelul 0w. Sarcina e „show the word moon”, răspunsul e `"moon"`.

**Ce am găsit acum, numărând:** problema nu e doar tokenizer-ul.
- În sarcină, cuvântul are spațiu în față (` moon`); în răspuns nu (`moon`, între ghilimele). Pentru model sunt
  **bucăți diferite**, oricât de bun ar fi tokenizer-ul. Cu sarcina de acum, **0 din 116** cuvinte se pot copia bucată
  cu bucată din ce vede modelul. Asta e adevărat și cu tokenizer-ul vechi, și cu cel nou.
- Dacă sarcina ar arăta cuvântul gata pus între ghilimele (`show the word "moon"`), **116 din 116** s-ar putea copia,
  cu oricare tokenizer.
- Tokenizer-ul nou ajută altfel: răspunsul e scurt (`"`, `moon`, `"`: 3 bucăți, față de 4) și cuvântul e întreg.

**Ce am găsit încercând** (un model de jucărie, 2 straturi, pornit de la zero, pe procesor; învață sarcina pe 3.000 de
cuvinte din povești și e testat pe cuvintele nivelului 0w, pe care nu le-a văzut):

| Varianta | Cuvinte nevăzute nimerite (din 116) | Nevăzute lungi (din 35) |
|---|---|---|
| tokenizer vechi, sarcina de acum | 2 | 0 |
| tokenizer nou, sarcina de acum | 0 | 0 |
| tokenizer vechi, sarcina cu ghilimele | **81** | 4 |
| tokenizer nou, sarcina cu ghilimele | **28** | 0 |

- **Sarcina de acum nu se poate învăța prin copiere**, cu niciun tokenizer: 0–2 din 116. Modelul scrie un alt cuvânt
  între ghilimele (`"pencil"` pentru „train”).
- **Cu ghilimele în sarcină, copierea apare.**
- **Rezultat negativ pentru tokenizer-ul nou:** la modelul de jucărie, copierea merge mai slab cu el (28) decât cu cel
  vechi (81). Explicația cea mai probabilă: cu tokenizer-ul vechi cuvintele sunt făcute din puține bucăți mici, văzute
  de mii de ori; cu cel nou fiecare cuvânt e bucata lui, văzută rar, iar un model pornit de la zero n-a apucat s-o
  învețe. W2 nu pornește de la zero la școală (a văzut cuvintele de milioane de ori), deci cifra asta nu spune ce va
  face W2; spune doar că tokenizer-ul nou nu e un câștig garantat aici.
- Cu doar 80 de cuvinte de învățat, modelul le ține minte și nu copiază în nicio variantă (0 din 36); de aceea
  încercarea folosește 3.000.
- E un model de jucărie, nu Kronos: arată mecanismul, nu rezultatul școlii.

## Ce trebuie să hotărască Adrian (înainte de pilotul v0.4)

1. **Sarcina nivelului 0w.** Variantele:
   - **(a) rămâne „show the word moon”** (nicio amprentă schimbată). După cifrele de mai sus, modelul trebuie să învețe
     pentru fiecare cuvânt legătura dintre ` moon` și `moon`; pe cuvinte nevăzute, încercarea a dat 0–2 din 116.
   - **(b) devine `show the word "moon"`** (recomandat de mine). Cere schimbarea generatorului de teste
     (`module/cod/examen_cod.py`), a episoadelor cu cuvinte din abecedar și a setului sacru pentru nivelurile cu cuvinte.
     **Toate trei au amprentă: nu le-am atins și nu le ating fără „da”-ul tău.** După schimbare, amprentele se aprobă
     din nou (`python unelte/scoala_cod.py --aproba-amprente --motiv "..."`), iar rezultatele la 0w nu se mai compară
     direct cu v0.3.
   - **(c)** un nivel nou, „0q” (cuvântul arătat între ghilimele), lângă 0w, care rămâne cum e. Cere tot schimbarea
     generatorului de teste (deci aprobare), dar nivelurile vechi și setul lor sacru rămân neatinse.
2. **Pragul de regresie pe povești** pentru v0.4 (acum provizoriu 0,60): după noaptea W2.
3. **Câte exemple în față:** rămân 2 (ca v0.3, pentru comparație) sau urcăm la 4, acum că e loc.

## Ce nu s-a făcut

- Școala nu a rulat deloc (nici pregătirea pe abecedar): nu există încă modelul W2 din care pornește.
- Nu s-a refăcut textul niciunui fișier cu amprentă: „împărțirea refăcută” înseamnă doar felul în care tokenizer-ul
  nou taie aceleași texte.
