# Etapa 2 pe workstation: datele, tokenizer-ul nou și proba W2 (luni, 12 octombrie 2026)

*Totul pe procesor, în afară de probele de câteva minute. Nu s-a pornit nicio antrenare lungă. Rezultatele negative
sunt trecute la fel ca cele bune.*

## Datele

Lista completă, cu licențe, obligații, revizii și amprente: `docs/DATE_surse.md` (scris de unealtă din
`date/ws/brut/surse.json`).

- **Descărcat: 7,01 GB** (limita lui Adrian: 60 GB). După curățare: 7,58 GB de text de antrenare și 75 MB de validare
  pusă deoparte (1% din fiecare sursă). Tot `date/ws/` ocupă ~18 GB, cu amestecul.
- Licența se citește de pe fișa oficială înainte de fiecare descărcare; o sursă cu altă licență sau cu acces pe bază
  de cont e refuzată.

**Ce nu s-a descărcat și de ce:**
- **The Stack smol** (cod Python): fișa nu are nicio licență și cere cont cu termeni acceptați pe site. Trebuie făcut
  de Adrian, cu contul lui Hugging Face. Fără el avem doar **65 MB de cod** (self-oss-instruct).

**Alegeri făcute (cele mai prudente), de știut:**
- Wikipedia și Wikisource: varianta gata curățată publicată de Wikimedia pe Hugging Face (copiile din noiembrie și
  decembrie 2023), nu arhiva brută de pe dumps.wikimedia.org. E același text, fără marcajele wiki.
- Wikipedia și Wikisource sunt CC BY-SA (cer atribuire și aceeași licență la redistribuire), nu CC BY simplu. Sunt
  pe lista cerută de Adrian; obligația e notată.
- Tatoeba și Europarl: prin OPUS (fișiere aliniate rând cu rând). Europarl nu are licență formală; Parlamentul
  European permite reutilizarea cu sursa menționată.
- Din self-oss-instruct s-au luat sarcina și răspunsul, nu și fragmentul de cod din care a pornit fiecare sarcină.

**Ce am aflat despre date (și negativ):**
- **Fabulele (ds-tf3-ro-3m) sunt foarte repetitive.** Din 3.000.000, 664.231 (22%) sunt duplicate exacte, iar în
  394 MB de text sunt doar 4.273 de cuvinte și semne diferite (Wikipedia are 1,4 milioane în tot atâta text). Un
  exemplu începe cu aceeași propoziție spusă de trei ori. Sunt bune ca româna simplă, dar puțin variate.
- Wikipedia: 158.105 articole din 442.389 sunt sub 300 de caractere (cioturi) și au fost scoase.
- FineWeb-2: 13,1 milioane de litere cu sedilă înlocuite în felia de 3 GB; fără asta, aceleași cuvinte ar fi avut
  două scrieri.

## Tokenizer-ul nou

`date/ws/bpe_16384.json` (sha256 `dfdcc25cd2ca7fc3…`), 16.384 de simboluri, regulile „ws” din
`module/tokenizer_bpe.py`. Învățat în 2 minute de `unelte/antreneaza_tokenizer_ws.py`, din amestecul 45% engleză
simplă, 35% română, 15% cod, 5% numere și calcule, doar din textele de antrenare.

**Alegeri făcute:**
- Făcut cu algoritmul proiectului, nu cu biblioteca `tokenizers` din plan: modelul îl folosește direct, fără nicio
  conversie. Regulile vechi și tokenizer-ul de 4.096 rămân neschimbate.
- Numerele 0–999 (și „07”, „007”) sunt simboluri fixe, primele din vocabular. Spațiul dinaintea unui număr nu se
  lipește de el, deci „46” e același simbol oriunde.
- Ca un cuvânt să rămână întreg și fără spațiu în față, forma fără spațiu primește 30% din aparițiile formei cu
  spațiu. Încercat cu 10%, 30% și 100%:

| Pondere | `"moon"` | Cuvinte englezești dese întregi fără spațiu (din 2.000) | Româna: mai puține bucăți decât cu cel vechi |
|---|---|---|---|
| 10% | „m” + „oon” | 888 | 54,2% |
| **30% (ales)** | „moon” | 1.308 (1.972 în cel mult 2 bucăți) | 53,5% |
| 100% | „moon” | 1.897 | 52,2%; pierde cuvinte românești întregi cu spațiu (883 față de 1.175) |

**Verificările cerute, cu exemple** (toate în `lucru/tokenizer_ws_verificare.json`):

| Text | Tokenizer-ul nou | Tokenizer-ul vechi |
|---|---|---|
| `46` | 1: `46` | 2: `4`, `6` |
| `37 + 58 = 95` | 7: `37`, ` +`, ` `, `58`, ` =`, ` `, `95` | 12 |
| `1234` | 2: `123`, `4` | 4 |
| `"moon"` | 3: `"`, `moon`, `"` | 4: `"`, `m`, `oon`, `"` |
| `print(moon)` | 4: `print`, `(`, `moon`, `)` | 8 |
| `Pisica doarme pe covor, iar câinele aleargă prin grădină.` | 15 | 35 |
| `def aduna(a, b):` + `return a + b` | 13 | 19 |

- **„46” e o bucată: da.** Toate numerele 0–999 sunt câte o bucată.
- **`"moon"` între ghilimele: cuvântul e o singură bucată, dar cu ghilimelele sunt 3, nu „cel mult 2”.** Cerința
  cuvânt cu cuvânt nu e îndeplinită: ghilimelele rămân bucăți separate, ca un cuvânt să fie același simbol oriunde
  apare. Înainte erau 4, iar cuvântul era rupt în două.
- **Româna are cu cel puțin 30% mai puține bucăți: da, cu 53,5%** (pe validările Wikipedia, Wikisource, FineWeb-2 și
  fabule; pe fiecare în parte, între 46% și 65%).
- Codul: cu 41% mai puține bucăți. Engleza simplă (TinyStories): cu 2,2% mai puține, deci aproape la fel.
- Toate textele de validare se rescriu exact din simboluri.
- Din cele mai dese 2.000 de cuvinte românești, doar 1.175 sunt o singură bucată cu spațiu în față (la engleză,
  1.999): româna are multe forme ale aceluiași cuvânt.
- Tokenizer-ul nu schimbă sedilele: „Ştefan” scris cu sedilă se rupe în multe bucăți. Sedilele se înlocuiesc la
  curățarea datelor, nu la citirea unui text nou.

## Amestecul W2 și configurarea

- `config/ws_w2.toml`: 12 × 768, context 512, lot 12, rata 0,0006 → 0,00006 pe 10 ore, de la zero, paznicul la
  7.000 MB și 83 °C. Examenul oficial rămâne val_bpb pe validarea TinyStories R2, deci se compară cu liniile vechi.
- **Amestecul** (`date/ws/amestec/antrenare.txt`, 4,00 GB, 1,03 miliarde de simboluri, împărțite în 85 de secunde):
  56,0% engleză simplă (TinyStories întreg), 41,4% română, **1,6% cod**, 1,0% numere.
  - Codul e 1,6%, nu 15%: atât avem fără The Stack. Am preferat să nu repet de 9 ori aceleași 65 MB.
  - Numerele sunt 1%, nu 5%: e text generat, repetitiv.
- **Hrana:** 6% din fiecare lot din `date/ws/hrana_fapte_abecedar.txt`, adică 5% povești cu fapte + 1% abecedar
  (abecedarul e repetat de 102 ori în fișier, cât să fie 1 parte la 5). Modelul n-a trebuit schimbat pentru asta.

## Proba W2 pe text adevărat (5 minute, linia separată „ws_w2_proba”)

| | Proba pe text adevărat | Proba de dimineață (simboluri la întâmplare) |
|---|---|---|
| Pași pe secundă | **5,9** | 5,93 |
| Memoria video maximă, cum o măsoară paznicul | **4.792 MB** | 4.793 MB |
| Toată placa în timpul antrenării, cu Windows | 6.278–6.324 MB | 6.465 MB |
| Temperatura maximă | **63 °C** | 63 °C |
| Milioane de simboluri pe oră | ~130 | 131 |

- Examenele de la oră (fapte, fapte noi, nota profesorului) merg și cu tokenizer-ul nou.
- **Problemă găsită și reparată:** la trecerea de la antrenare la examenul oficial, placa a urcat pentru câteva
  secunde la **7.874 MB din 8.192**. Examenul evalua 64 de bucăți de text deodată, ceea ce la context 512 și
  vocabular 16.384 cere ~2,5 GB în plus. Acum `module/model_gpt.py` ia mai puține bucăți deodată la modelele mari
  (8 la W2); la modelele de până acum rămân 64, deci scorurile lor nu se schimbă. După reparație, vârful e 6.324 MB.
  Examenul (`module/examen_bpb.py`) și `kronos/` nu s-au atins.
- Cifrele de scor ale probei (val_bpb 1,43 după 5 minute, 1,14 după 10) nu spun nimic despre linie.
- Proba a rulat pe linia „ws_w2_proba” (rândurile #298 și #300 din jurnal), nu pe „ws_w2”: linia adevărată e
  neîncepută.

## Repetiția nopții W1 (2 minute, linia separată „ws_w1_repetitie”)

- Tot drumul unei ore merge pe workstation: antrenare, examenul oficial, fapte, fapte noi, nota profesorului
  (Qwen din ce s-a adus de pe laptop), comparația „alături de fapte-zero”. Rândurile #297 și #299.
- 6,8 pași pe secundă, 3.906 MB la paznic, 62 °C; toată placa urcă cel mult la 5.852 MB, cu profesorul încărcat.
- Examenele durează ~2 minute, deci o oră întreagă are ~63 de minute.
- Pornirea programată din Windows, fără fereastră, a fost încercată pe repetiție și merge
  (`unelte/programeaza_noapte_ws.ps1`, `unelte/noapte_ws.ps1`).

## Ce rămâne de hotărât

- The Stack smol: Adrian acceptă termenii cu contul lui, sau rămânem cu 1,6% cod, sau luăm altă sursă de cod.
- Cât din fabule intră în antrenare, știind că sunt repetitive (acum: 20% din partea de română a amestecului).
- Cerința „`"moon"` în cel mult 2 bucăți” cu ghilimele cu tot: se poate doar lipind ghilimeaua de cuvânt, ceea ce ar
  face din nou „moon” și „"moon” simboluri diferite. Nu am făcut asta.
