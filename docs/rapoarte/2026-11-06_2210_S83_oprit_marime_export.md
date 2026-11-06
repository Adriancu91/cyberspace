# S83 — #513 în locul lui #477: OPRIT la pasul 1 (mărimea exportului diferă cu 32 de octeți)

Executantul, 6 nov 2026, 22:00–22:10, doar pe procesor (`CUDA_VISIBLE_DEVICES=-1`), fără placă; nimic descărcat,
instalat sau șters.

## Pe scurt

- Exportul #513 a ieșit cu **110.859.008 octeți**, nu cu **110.859.040** cât cere sarcina („altfel oprești și scrii
  de ce”). Am oprit după pasul 1: pașii 2–7 (vectori, MODEL.md, Release, modelul în uz) **nu sunt făcuți**.
- **De ce:** arhitectura e aceeași. Am comparat antetul și tensorii celor două fișiere (`lucru/cascada/S83_proba/compara.py`,
  doar citire): aceiași tensori, în aceeași ordine, cu aceleași forme; singura cheie diferită e textul `sursa`:
  `"#477 w2_reteta_A_cont3"` (22 de octeți) față de `"#513 w2_romana_r1"` (17 octeți). Antetul se completează cu zerouri
  până la un multiplu de 32 (`ALINIERE = 32` în `unelte/exporta_greutati.py`), deci 5 octeți mai puțin în text au trecut
  antetul sub o graniță de 32 → fișierul are exact 32 de octeți mai puțin. Nu e o greșeală a modelului sau a exportului.
- Teste: **1247 trec, 1 sărit, 0 pică**.

## Sumele (pasul 0 și după)

| fișier | SHA-256 înainte | după |
|---|---|---|
| `lucru/stocare/modele/experiment_513.pt` | `605c4084…8b2c` | la fel |
| `lucru/export/kronos_477_q8_0.kgr` | `bcbe8187…3963` | la fel |
| `lucru/export/kronos_459_q8_0.kgr` | `e80618b4…382e` | la fel |

Fișierul nou: `lucru/export/kronos_513_q8_0.kgr`, 110.859.008 octeți, SHA-256
`66f734b3136206d1be8825b1188b1a90f0c5b00c2e19746547f327f9b95c5859` (în `lucru/`, nu în Git; nu l-am șters).
`kronos_513_q8_0.kgr.sha256` NU l-am scris încă (vine cu reluarea).

Comanda rulată: `python unelte/exporta_greutati.py --experiment 513 --fel q8_0 --iesire lucru/export/kronos_513_q8_0.kgr`
→ `{"experiment": 513, "fel": "q8_0", "octeti": 110859008}`.

## Ce n-am atins

`kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, checkpoint-urile (doar citite), S77e și liniile `w2_mare_24*`,
modulele de inferență (căile implicite rămân pe #477), hub-ul.

## Variante pentru reluare (decide supraveghetorul sau Adrian)

1. **Accept mărimea 110.859.008** (recomand): pragul era „aceeași arhitectură ca #477”, iar asta e verificat tensor cu
   tensor; cei 32 de octeți vin doar din textul `sursa`. Reluarea face pașii 1 (doar fișierul `.sha256`) până la 7, cu
   fișierul deja exportat; în MODEL.md scriu mărimea reală și de ce diferă de #477.
2. Reexport cu un text `sursa` de aceeași lungime (ar cere o opțiune nouă în `exporta_greutati.py`), ca mărimea să fie
   exact 110.859.040 — fără câștig real, doar ca să se potrivească cifra.

Coada: S83 → `oprit`. Următoarea, S84, e „după ce S83 e `gata` sau `oprit`” → poate porni la trecerea următoare.
