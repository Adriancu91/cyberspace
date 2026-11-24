# S135 — laboratorul treptelor: partea A (procesor) GATA

*Scris de executant, 24 noiembrie 2026, 21:24. Sarcina: C-163 (aprobată de Adrian 24 nov 17:35, trecută în coadă de supraveghetor la 20:15).*

## Pe scurt

- Partea A e **gata**: piesa care antrenează „pe bucăți de 4 simboluri” (`module/model_trepte.py`), unealta laboratorului
  (`unelte/laborator_trepte.py`) și 9 teste noi. **1.581 de teste trec, 1 sărit.**
- Proba pe procesor (model mic, 2 minute) merge la ambele rețete și eroarea scade. Pe bucăți, pașii merg de ~3,4 ori mai
  repede (924 de pași în 59 s față de 270 în 60 s pe simboluri).
- Amprentele (SHA-256) ale celor 21 de fișiere păzite sunt **identice** înainte și după.
- Partea B (cele două antrenări de câte o oră pe placă) **n-a pornit**: azi trecuse ora-limită 21:15, deci începe
  **mâine de la 07:00**, după ce scriu pre-înregistrarea `laborator_trepte_k4`.

Notă: lucrul a fost făcut în două treceri. Trecerea de la 20:29 a scris codul, testele și proba (0), dar s-a încheiat
înainte de examenele probei (1) și fără commit. Trecerea de la 21:09 (aceasta) a verificat codul față de sarcină, a rulat
toate testele, a refăcut proba (1) complet (`proba_1b`), a calculat SHA-ul de după și face commit-ul.

## Ce am construit

1. **`module/model_trepte.py`** (modul nou, port `model`, versiunea 0.1.0, contractul 1; nu schimbă niciun modul existent):
   - moștenește `ModelGPT` (aceeași rețea ca #513: straturile, LayerNorm, GELU, capul legat de încorporări);
   - `k_bucata` (1 = rețeta de azi) și `minute_bucati`;
   - **faza pe bucăți**: fereastra de 512 + K simboluri se taie în bucăți de K; intrarea unei poziții = media încorporărilor
     celor K simboluri + încorporarea de poziție (ca la o secvență de 128); eroarea = media cross-entropy față de cele K
     simboluri ale bucății următoare (ca în lucrare);
   - **faza pe simboluri**: exact pasul de azi; aceleași greutăți și **același AdamW** (nu se repornește);
   - rata **după ceas** (încălzire liniară, constantă, răcire liniară la 0 la sfârșit), adunarea loturilor, încorporările
     din N(0; 0,02) ca la `model_gpt_cod` (S61);
   - trecut în lista `MODULE` din `teste_contracte/test_contracte.py` (două variante: K = 1 și K = 4), cu fișa
     `module/manifeste/model_trepte.toml`; testele de contract trec.
2. **`unelte/laborator_trepte.py`**: `--reteta 0|1`, `--minute 60`, `--k 4`, `--minute-bucati 40`, `--samanta 1163`,
   `--dispozitiv cpu|cuda`, `--iesire ...`. De la zero, aceeași inițializare și aceleași loturi la ambele rețete; lot
   12 × 512 × adunare 8 = 49.152 simboluri pe pas; AdamW 0,9/0,999, eps 1e-8, scăderea greutăților 0,1, tăierea 1,0;
   bf16 cu autocast pe placă; rata de vârf 6e-4 (încălzire 3 min, răcire 15 min). La fiecare minut `progres.csv`
   (minut, fază, pași, simboluri văzute, eroare, memoria plăcii, temperatura); paznicul (peste 7.000 MB sau 83 °C →
   oprește); la sfârșit modelul **doar** în `<iesire>/model.pt` + `rezultat.json`; refuză să scrie peste o ieșire existentă.
3. **`teste/test_laborator_trepte.py`** (9 teste): K = 1 dă exact pasul de azi (aceeași pierdere și aceleași greutăți ca
   `ModelGPT._pas`, F32, procesor); media încorporărilor și eroarea pe K ținte pe un exemplu calculat de mână; gradientul
   fazei pe bucăți = PyTorch față de diferențe finite pe 5 elemente (F64); trecerea bucăți → simboluri păstrează greutățile
   și starea AdamW; bucla trece prin ambele faze; paznicul oprește bucla; rata după ceas; setări greșite refuzate; unealta
   cap-coadă (scrie, refuză a doua oară, modelul se citește înapoi ca model obișnuit).

## Datele (de știut)

Sarcina spune „doar textul W2 `date/ws/amestec/antrenare.txt`”. Unealta citește **același amestec W2, deja tokenizat**:
`lucru/bucati/w2_amestec_be12` (1.341.190.791 simboluri, sha tot 560863a9…, tokenizerul `date/ws/bpe_16384.json`) — e
portul `date` folosit în locul lui `amestec/antrenare.txt` de configurările `conv_w2_mare_24_bucati` … `24zci` (DEDUS din
configurări: e același text, fără conversații și fără hrană — conversațiile vin acolo din altă setare, care aici lipsește).
Motivul: textul brut ar trebui tokenizat la fiecare pornire, ceea ce ar mânca din ora de ceas.

## Examenele (doar folosite, nimic schimbat)

Aceleași ca la verdictele de azi (portul `examen` din `config/conv_w2_mare_24zci.toml` + R1 pe setul ascuns):

```
ExamenRomana(caractere=100_000, cu_r1=True).examineaza(model, date)   # romana_bpb (judecătorul), r1_instructiuni, r1_ascuns
ExamenBpb().examineaza(model, date)                                    # val_bpb (martorul)
```

Le rulează unealta singură la sfârșit (funcția `examene` din `unelte/laborator_trepte.py`). Comenzile pentru partea B:

```
.venv/Scripts/python -X utf8 unelte/laborator_trepte.py --reteta 0 --minute 60 --dispozitiv cuda --iesire lucru/laborator/S135_0
.venv/Scripts/python -X utf8 unelte/laborator_trepte.py --reteta 1 --minute 60 --k 4 --minute-bucati 40 --dispozitiv cuda --iesire lucru/laborator/S135_1
```

## Proba pe procesor

Model mic (2 straturi, 2 capete, n_emb 64, context 512, lot 4 × adunare 2; 1.181.440 parametri), 2 minute, încălzire
0,2 min, răcire 0,5 min, sămânța 1163. Rețeta (1): `--k 4 --minute-bucati 1`. Ieșirile: `lucru/cascada/S135_proba/proba_0/`
și `proba_1b/` (`proba_1/` = încercarea întreruptă, fără examene; n-o folosesc).

| minut | (0) fază | (0) pași | (0) eroare | (1) fază | (1) pași | (1) eroare |
|---|---|---|---|---|---|---|
| 0,25 | simboluri | 68 | 9,238 | bucăți | 234 | 8,395 |
| 0,50 | simboluri | 136 | 7,685 | bucăți | 460 | 6,691 |
| 1,00 | simboluri | 273 | 6,675 | bucăți | 924 | 6,379 |
| 1,25 | simboluri | 342 | 6,419 | simboluri | 992 | 6,272 |
| 1,50 | simboluri | 410 | 6,154 | simboluri | 1.060 | 6,011 |
| 2,00 | simboluri | 545 | 5,808 | simboluri | 1.194 | 5,749 |

| | (0) | (1) |
|---|---|---|
| simboluri văzute | 2.232.320 | 4.890.624 (3.784.704 pe bucăți + 1.105.920 pe simboluri) |
| română curat (`romana_bpb`) | 3,015 | 2,967 |
| `examen_bpb` (`val_bpb`) | 1,787 | 1,740 |
| R1 instrucțiuni / R1 ascuns | 0,11 / 0,07 | 0,00 / 0,00 |
| examenele au durat | 98 s | 102 s |

Eroarea pe bucăți (prima jumătate a lui (1)) nu se compară direct cu cea pe simboluri: e eroarea de a ghici 4 simboluri
dintr-o singură distribuție. **Proba arată doar că merge și că eroarea scade** — un model de 1 milion de parametri timp
de 2 minute nu spune nimic despre întrebarea de mâine.

## SHA înainte / după

`lucru/cascada/S135_proba/sha_inainte.json` (20:30) și `sha_dupa.json` (21:2x): 21 de fișiere — #513, #651, #736,
`kronos/*.py`, `module/examen_bpb.py`, `docs/conversatie/examen*.json` — **identice**. Disc C: liber 148 GB.

## Testele

`CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -m pytest -o addopts="" --basetemp=lucru/teste_tmp -q`:
**1581 passed, 1 skipped** (8 min 41 s).

## Ce urmează

- **Partea B, mâine de la 07:00** (fereastra 07:00–23:00, ultima pornire la 21:15): întâi pre-înregistrarea
  `laborator_trepte_k4` (ghicirile mele + pragurile supraveghetorului copiate întocmai), apoi, la fiecare probă: verific
  `C:\Kronos\cyber-test\porneste-test.txt`, scriu `laborator-ocupat.txt`, placa sub 1.000 MB și 50 °C, proba de 3 minute
  pe placă, (0), examenele, șterg semnul; după răcire, (1) la fel. Apoi al doilea tabel în
  `docs/integrare_kronos/BANC_ANTRENARE.md` și raportul completat.
- **S136** (fișa „calitate”, procesor) poate începe la o trecere următoare, după ce supraveghetorul vede S135 A.
- **De la Adrian:** nimic nou pentru S135 A.
