# Școala de cod v0.4: pregătirea pe tokenizer-ul nou (luni, 12 octombrie 2026, seara)

*Doar pregătire și teste, pe procesor. Școala NU a pornit și placa video n-a fost atinsă (pe ea rula noaptea W1).
Dintre fișierele cu amprentă s-a schimbat doar generatorul de teste (nivelul nou 0q, aprobat de Adrian); abecedarul,
setul sacru și sandbox-ul sunt neatinse, iar paznicul școlii nu are nimic de zis. Rezultatele negative sunt trecute la fel ca cele bune.*

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
5. **Teste:** `teste/test_cod_v04.py` (10), între care: elevul școlii încarcă, scrie și antrenează un model cu tokenizer-ul nou;
   nivelul 0q și verdictele lui; seturile vechi neschimbate.

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

## Hotărât de Adrian (12 octombrie, 19:30): varianta (c), un nivel nou lângă cel vechi

- **Nivelul nou „0q”**: aceleași cuvinte ca 0w, dar sarcina arată cuvântul gata pus între ghilimele
  (`show the word "moon"`), exact cum trebuie scris în răspuns. Răspunsul cerut e același: `"moon"` sau `print("moon")`.
- **0w rămâne cum era**, cu seturile și setul lui sacru. Verificat: toate cele 27 de seturi ale nivelurilor vechi (din
  v0.1, v0.2 și v0.3) sunt identice, sarcină cu sarcină, înainte și după schimbare; setul sacru și abecedarul au
  aceleași amprente.
- **Amprenta generatorului de teste a fost aprobată** la 19:37, cu motivul „v0.4: nivel nou cu ghilimele, tokenizer
  ws, aprobat de Adrian 12 oct” (în jurnalul școlii v0.4). Doar ea s-a schimbat (`4f74bed7…` → `62927c4a…`); celelalte
  trei amprente sunt cele din 8 octombrie.
- **În pilotul v0.4, 0q stă înaintea lui 0w:** 0n, 0q, 0w, 1a, 1b, 2A, 2B, 2C, 3A, 3B.
- Cu tokenizer-ul nou, la 0q răspunsul se poate copia din sarcină la toate cele 100 de sarcini (60 văzute, 20
  nevăzute, 20 adversariale); la 0w, la niciuna din 120; la numere (0n), la toate 115.

### Rezultatul negativ al probei de jucărie (de ținut minte)

- La modelul de jucărie, **cu sarcina cu ghilimele, tokenizer-ul nou a copiat mai slab decât cel vechi: 28 din 116
  cuvinte nevăzute, față de 81 din 116.** La cuvintele lungi: 0 din 35, față de 4 din 35.
- Deci nivelul 0q rezolvă ce se putea rezolva din formularea sarcinii, dar **nu e dovedit că W2 va trece de el**. Proba
  spune doar că sarcina veche nu se putea învăța prin copiere (0–2 din 116) și că cea nouă se poate.
- Dacă W2 pică la 0q, prima bănuială e aceasta: cuvintele întregi sunt bucăți rare, mai greu de copiat decât bucățile
  mici. Atunci merită încercat același pilot cu tokenizer-ul vechi, pe un model de aceeași mărime, înainte de alte
  schimbări.

## Ce a rămas de hotărât (înainte de pilotul v0.4)

1. **Setul sacru al lui 0q.** Nivelul nou nu are încă cele 20 de sarcini sacre, iar școala nu pornește un nivel fără
   ele. Se adaugă cu `python unelte/scoala_cod.py --genereaza-sacru --config config/scoala_cod_v04.toml` (nivelurile
   vechi rămân neatinse, sarcină cu sarcină), dar fișierul `date/cod/sacru.json` are amprentă, deci **cere aprobarea
   ta pentru amprenta setului sacru**. Nu l-am atins: ai aprobat doar generatorul de teste.

   **Luni, 21:00: Adrian a aprobat amprenta, cu condiții. Setul NU a fost generat, fiindcă o condiție nu se poate
   respecta cuvânt cu cuvânt.** Proba, fără nicio scriere în fișier:
   - cele 20 de cuvinte pe care le-ar alege unealta: van, fig, bike, tree, tent, owl, zoo, egg, web, car, fan, puppy,
     pig, foot, cloud, book, hen, rose, cake, goat;
   - **în abecedar: niciunul** (din toate cele 116 cuvinte ale nivelului, doar „apple” apare în abecedar);
   - **în sarcinile de antrenare ale lui 0q (cele 60 văzute): niciunul**; nici în cele 20 nevăzute sau 20 adversariale;
   - **în hrana lui W2** (`date/ws/hrana_fapte_abecedar.txt`: povești cu fapte + abecedarul): **17 din 20 apar**, ca
     orice cuvânt obișnuit dintr-o poveste („tree” de 1.731 de ori, „puppy” de 1.088). Lipsesc doar van, fig și bike;
   - din toate cele 116 cuvinte, doar 15 nu apar deloc în hrană: nu ajung pentru 20 de sarcini, oricum le-am alege;
   - **între ghilimele sau într-o sarcină „show the word …”: niciunul din cele 20 nu apare în hrană.** Singurele
     sarcini „show the word” din hrană sunt cele ale abecedarului (cat, dog, red, big, hi, yes…);
   - sarcinile sacre ale nivelurilor vechi: neatinse, fișierul are aceeași amprentă (`81b03acb…`).

   De hotărât de Adrian: (a) condiția se citește „niciunul între ghilimele sau într-o sarcină, în hrană” (atunci setul
   de mai sus o respectă); (b) set sacru de doar 15 sarcini, din cuvintele care lipsesc din hrană, ceea ce cere o
   schimbare în generatorul de teste și o nouă aprobare a amprentei lui; (c) cuvinte noi, pe care W2 nu le-a văzut
   nicăieri, tot cu schimbarea generatorului. Și cele 15 cuvinte de la (b) apar în poveștile din amestecul lui W2.
2. **Abecedarul nu are niciun exemplu cu ghilimele în sarcină.** Exemplele din fața modelului vin din abecedar, deci la
   0q modelul va vedea exemple de alt fel (numere, cuvinte fără ghilimele în sarcină). Liniile B și D își adaugă singure
   reușitele; linia A, nu. Câteva episoade de felul 0q în abecedar ar ajuta, dar abecedarul are și el amprentă.
3. **0w mai rămâne în pilot?** Dacă pică (probabil, după cifrele de mai sus), școala se oprește acolo și nu ajunge la
   1a. Variantele: îl scoatem din pilotul v0.4 (se schimbă doar configurarea) sau îl lăsăm ca martor.
4. **Pragul de regresie pe povești** (acum provizoriu 0,60): după noaptea W2.
5. **Câte exemple în față:** rămân 2 (ca v0.3) sau urcăm la 4, acum că e loc.

## Ce nu s-a făcut

- Școala nu a rulat deloc (nici pregătirea pe abecedar): nu există încă modelul W2 din care pornește.
- Abecedarul și setul sacru n-au fost rescrise: „împărțirea refăcută” înseamnă doar felul în care tokenizer-ul nou
  taie aceleași texte. Pilotul nu a pornit și nu pornește cât rulează W1.
