# Kronos → Cyber Universe OS: pachetul KGR1 (S39, comanda C-24)

Pentru motorul KGR1 scris de OS (Rust), ca să-l poată verifica fără codul Kronos. Pregătit de executant în
`Adriancu91/cyberspace`; supraveghetorul îl copiază în hub, în `integrare/kronos/`.

Notă de așezare: `format_greutati.md` și `vectori/` sunt în `integrare/kronos/`; acest `README.md` și `MODEL.md` sunt
în `docs/integrare_kronos/`, fiindcă regula executantului care apără nucleul (`Edit(kronos/**)`) prinde și
`integrare/kronos/`. În hub, toate stau împreună în `integrare/kronos/`.

## Ce e aici

| fișier | ce e |
|---|---|
| `format_greutati.md` | contractul: formatul KGR1 (antet, chei, tensori, F32/Q8_0), calculul rețelei și tokenizerul, descris complet. Copie exactă a `docs/format_greutati.md` |
| `vectori/mic_f32.kgr` | model **minuscul, cu greutăți la întâmplare** (nu e antrenat, scrie prostii): 2 straturi, 4 capete, n_emb 32, context 64, sămânța 20261028, cu tokenizerul adevărat al liniei w2 (16.384 de simboluri), totul F32. 2.424.160 octeți |
| `vectori/mic_q8_0.kgr` | același model, cu matricile în Q8_0. 840.288 octeți |
| `vectori/vectori.json` | pentru 3 texte („Ana are mere.”, „Capitala României este”, „def suma(a, b):”), pe fiecare fișier: simbolurile, logit-urile pe ultima poziție (toate cele 16.384), argmax-ul pe fiecare poziție, primele 5 simboluri greedy (și textul lor), marjele; plus sumele SHA-256 și diferențele măsurate |
| `MODEL.md` | modelul adevărat (Release privat): numele, mărimea, suma, testul de pe hardware |

De ce F32 are peste 1 MB: tokenizerul nostru are 16.384 de simboluri, iar tabelul de intrare are 16.384 × n_emb numere.
Cel mai mic n_emb care merge cu Q8_0 e 32 (blocuri de 32), deci tabelul singur are 16.384 × 32 × 4 = 2 MB în F32
(plus 216 KB tokenizerul). Un tokenizer mai mic n-ar mai verifica tokenizerul adevărat, așa că am păstrat mărimea.
Fișierul Q8_0 încape (0,84 MB).

## Cum se verifică un motor

Pentru fiecare fișier `.kgr` și fiecare text din `vectori.json` (`f32` → `mic_f32.kgr`, `q8_0` → `mic_q8_0.kgr`):

1. suma SHA-256 a fișierului = `fisiere.<fel>.sha256` (altfel fișierul s-a stricat la copiere);
2. tokenizerul din fișier codează textul exact în `simboluri`, iar `simboluri` se decodează înapoi exact în text;
3. logit-urile pe ultima poziție, față de `logits_ultima_pozitie`: diferența absolută maximă ≤ **toleranța** de mai jos;
4. argmax-ul pe fiecare poziție = `argmax_pe_pozitii` (identic);
5. 5 simboluri generate greedy (argmax, fără întâmplare) = `greedy_5` (identic), iar textul lor = `greedy_5_text`.
   Recomandat: o dată cu cache k/v, o dată fără, pe tot șirul (la noi dau la fel).

## Toleranța declarată (propunerea executantului)

| fișier | logit-uri (abatere absolută maximă) | argmax, greedy |
|---|---|---|
| F32 | **≤ 1e-4** | identice |
| Q8_0 | **≤ 1e-3** (față de vectorii Q8_0 de aici, nu de cei F32) | identice |

Pe ce se sprijină (măsurat pe aceste fișiere):
- motorul nostru fără PyTorch (`unelte/inferenta_bruta.py`) față de PyTorch pe procesor, F32: **4,0e-6** maxim, cu
  logit-uri de până la 8,4 în valoare absolută. 1e-4 lasă de 25 de ori loc pentru altă ordine a adunărilor (ex. float32
  peste tot, fără float64 la LayerNorm/softmax);
- la Q8_0, valorile sunt `scara × număr`, exacte în f32; abaterile vin tot din adunări, dar matricile Q8_0 se pot
  înmulți și pe blocuri (sume parțiale pe bloc), de aici 1e-3. Q8_0 față de F32 diferă cu 0,133 maxim — de aceea Q8_0
  se compară cu vectorii Q8_0, nu cu cei F32;
- marja cea mai mică dintre primul și al doilea logit, pe toate pozițiile și pașii greedy: 0,047 (F32) și 0,028 (Q8_0),
  de peste 25 de ori toleranța, deci argmax-ul nu se poate schimba cinstit în interiorul ei.

**Pragul pentru modelul mare rămâne întrebarea deschisă către Adrian din S37**: pe #415, motorul nostru dă 1,36e-4
față de PyTorch (peste pragul 1e-4 din C-21), deși argmax-ul și textul sunt identice. Toleranța de aici e doar pentru
modelul minuscul; pentru modelul mare, testul pe hardware din `MODEL.md` cere simbolurile greedy identice.

Vectorii se fac din nou cu `python unelte/vectori_kgr1.py vectori --iesire integrare/kronos` (ies la fel, bit cu bit);
testul `teste/test_vectori_kgr1.py` îi recitește.
