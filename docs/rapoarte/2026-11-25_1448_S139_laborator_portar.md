# S139 A — „Portarul” (amestecul de adâncimi): piesa, unealta și testele (procesor) — GATA

*Executantul cascadei, 25 noiembrie 2026, 14:48. Sarcina S139 partea A (C-167, aprobată de Adrian 25 nov 11:41, trecută
în coadă de supraveghetor la 14:15). Doar procesor, doar fișiere noi; placa n-a fost folosită.*

## Pe scurt

- Piesa nouă `module/model_portar.py` și unealta `unelte/laborator_portar.py` sunt gata, cu 12 teste noi
  (`teste/test_laborator_portar.py`) + modulul în lista contractelor (2 rânduri: fără și cu portar).
- **Toate testele trec: 1605 trec, 1 sărit** (înainte: 1590 trec, 1 sărit).
- **SHA înainte = după** la cele 21 de fișiere (#513, #651, #736, `kronos/*.py`, `module/examen_bpb.py`, examenele de
  conversație) — nimic atins.
- Proba de 2 minute pe procesor (model mic, datele W2 reale) **merge**: eroarea scade 8,89 → 5,39, selectorul învață
  (BCE 0,67 → 0,23), alegerea cauzală se potrivește cu top-k în 94 % din cazuri, iar la examen în modul cauzal trec
  ~55–59 % din simboluri.
- **Pre-înregistrarea pentru B e scrisă** (`docs/preinregistrari/2026-11-25_laborator_portar.md`), cu pragurile tale
  copiate întocmai și viteza lui (0) în minutele 5–45: **39.115 simboluri/s** → „și mai rapid” cere ≥ 41.071.
- **Partea B (o oră pe placă) poate porni de la următoarea trecere** (azi până la 21:15), dacă nu e test OS.

## Ce am construit

### `module/model_portar.py` (port `model`, `MANIFEST` 0.1.0, fișa `module/manifeste/model_portar.toml`)

- Moștenește `ModelTrepte` (S135), **fără să-l schimbe**. Aceeași rețea ca (0); setări noi: `portar` (da/nu),
  `capacitate` = 0,5, `straturi_portar` = 2, 4, 6, 8, 10, 12 (de la 1), `pondere_bce` = 0,01.
- **La un strat cu portar**: selectorul `Linear(n_emb, 1)` pe intrarea stratului dă scorul r.
  - **la antrenare (top-k)**: în fiecare text cei 256 din 512 cu scorul cel mai mare, puși în ordinea poziției
    (gather); întrebările (Q) doar de la ei, cheile/valorile (K, V) de la **toate** simbolurile, masca după poziția
    **originală**; ieșirea (atenție + MLP) × `sigmoid(r)`, pusă înapoi la locul ei (scatter) peste legătura directă;
    ceilalți neschimbați. Plus BCE (ținta = „a fost în top-k”, fără gradient), media pe cele 6 straturi, × 0,01;
  - **la examene și la scris (cauzal)**: alegerea e `sigmoid(r) > 0,5`, simbol cu simbol, ieșirea tot × `sigmoid(r)`.
    Calculul se face pe toate pozițiile și se păstrează doar la cei aleși (rândurile atenției sunt independente, deci
    e exact ca și cum ar trece doar cei aleși — doar că nu e mai rapid; la examen viteza nu contează).
- `portar = nu` → exact pasul S135 (0). **Selectorii se construiesc după restul rețelei** (și după încorporările din
  N(0; 0,02)), deci la sămânța 1163 toate greutățile comune pornesc **identic** cu (0).
- Eroarea raportată („pierdere”) rămâne doar cross-entropy, comparabilă cu (0); BCE se scrie separat.
- O alegere a mea, de știut: BCE-ul e **media** pe cele 6 straturi cu portar (nu suma), apoi × 0,01.

### `unelte/laborator_portar.py`

- Exact rețeta S135 (0) (aceleași setări prin `laborator_trepte.setari_model`, aceeași buclă `ModelTrepte.bucla`,
  aceleași loturi uniforme cu sămânța 1163, același paznic 7.000 MB / 83 °C) — singura diferență: portarul.
- `progres.csv`, în plus față de S135: `simboluri_pe_s` (de la rândul trecut), `bce`, `parte_aleasa_cauzal` (pe
  loturile de antrenare), `potrivire_topk` (%), `parte_trecuta` (= 0,5 la antrenare).
- `rezultat.json`: `viteza_minutele_5_45` (aceeași funcție `viteza_intre` am aplicat-o și pe `progres.csv` al lui (0));
  examenele: `examene.cauzal` = funcția `examene` din `unelte/laborator_trepte.py` (neschimbată) în modul cauzal;
  `romana_cauzal_parte_aleasa` = o trecere în plus a examenului de română (fără R1) doar ca să număr partea aleasă (dă
  aceeași notă — verificat la probă); `informativ_topk` = româna și `val_bpb` în modul top-k (scris „NU decide”);
  `validitate_parte_aleasa` (35–65 %).
- Model **doar** în `<iesire>/model.pt`; refuză să scrie peste o ieșire existentă.

## Testele (`teste/test_laborator_portar.py`, 12)

| cerut | test | rezultat |
|---|---|---|
| (a) `portar = nu` = pasul S135 (0) | aceeași inițializare, aceeași pierdere (egalitate exactă) și aceleași greutăți pe 3 pași, F32, procesor; + cu portar, partea comună pornește identic | trece |
| (b) capacitate 1,0, fără sigmoid = stratul obișnuit | pe fiecare strat și pe toată rețeaua, în modul top-k și în modul cauzal | trece |
| (c) masca | la antrenare: aleși 1, 3, 5 din 8 — schimbi x după 5 → nimic; la 4 → doar 5; la 0 (nealeasă) → toți (K/V de la toate); în modul cauzal, rețeaua întreagă: schimbi simbolurile de după 9 → ieșirile până la 9 identice | trece |
| (d) gather/scatter de mână | top-k în ordinea poziției, strângerea, punerea înapoi (cei nealeși neschimbați), masca | trece |
| (e) gradientul ajunge la selector | diferențe finite (F64) pe 5 elemente ale celor 2 selectori | trece |
| (f) unealta cap-coadă | model mic (2 straturi, n_emb 64), procesor: merge, eroarea scade, coloanele noi completate, refuză să scrie peste, modelul se citește înapoi cu portarul; + `examene_portar` cu examene de probă | trece (vezi nota) |
| în plus | pasul raportează BCE și statisticile; setări greșite refuzate | trece |

Nota la (f): coada cerea `--minute 2`; în suita de teste l-am pus la 6 secunde (ca testul S135, ca suita să nu se
lungească cu 2 minute), iar **proba de exact 2 minute** am rulat-o separat, pe datele W2 reale (mai jos).

Pe drum am găsit și corectat două greșeli (înainte de commit, nu ascuns): testul (c) adăuga o constantă, pe care
LayerNorm o șterge (testul nu verifica nimic) → acum zgomot; BCE-ul se calcula în F32 chiar la testul în F64 → acum
rămâne F64 la test (pe placă e tot F32).

**Toată suita:** `CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -m pytest` → **1605 trec, 1 sărit** (8 min 03 s);
înainte de schimbări: 1590 trec, 1 sărit. Lista `MODULE` din `teste_contracte/test_contracte.py`: 2 rânduri noi
(fără portar; cu portar pe stratul 1, adunare 2, încălzire/răcire) — trec.

## Proba pe procesor (pasul 4; viteza nu contează — placa decide)

`unelte/laborator_portar.py --minute 2 --dispozitiv cpu --straturi 2 --capete 2 --n-emb 64 --lot 4 --adunare 1
--incalzire-minute 0.2 --racire-minute 0.5 --fara-r1` → `lucru/cascada/S139_proba/proba/` (log `proba.log`):

| minut | pași | eroare | BCE | aleși cauzal | potrivire cu top-k |
|---|---|---|---|---|---|
| 0,25 | 130 | 8,887 | 0,675 | 58,6 % | 60,5 % |
| 1,00 | 521 | 6,203 | 0,271 | 51,5 % | 93,5 % |
| 2,00 | 1.041 | 5,391 | 0,233 | 47,7 % | 93,7 % |

Examenele (modul cauzal, model mic, deci note proaste — doar că merg): română 2,9156, `val_bpb` 1,6114; partea aleasă
la română 58,5 % (în 35–65 %); trecerea separată de română dă **exact aceeași notă** (2,915605); informativ top-k:
română 2,9157, `val_bpb` 1,6109. **Merge.**

## SHA

`lucru/cascada/S139_proba/sha_inainte.json` (identic cu `S137_proba/sha_dupa_B.json`) și `sha_dupa.json`: 21/21
identice, nimic lipsă. C: 146 GB liberi.

## Ce n-am atins

Nimic în `kronos/`, `module/examen_bpb.py`, `module/model_trepte.py`, `module/date_harta.py`,
`unelte/laborator_trepte.py`, `unelte/laborator_harta.py`, paznic, jurnal, `config/`. Nimic șters, nimic descărcat,
placa nefolosită. S131, S134 B, S138 neatinse.

## Ce urmează

- **S139 B** (placa, ~1 h 40 min, azi până la 21:15 sau mâine de la 07:00): protocolul S137 B — `porneste-test.txt`
  verificat imediat înainte, `laborator-ocupat.txt` „S139 (P)”, placa < 1.000 MB și < 50 °C, proba de 3 minute în
  `lucru/cascada/S139_proba/placa_3min_P/`, apoi (P) prin cascadă, examenele, verdictul strict după pragurile din
  pre-înregistrare; raportul `…_S139_laborator_portar_B.md`.
- **De la Adrian:** nimic nou pentru partea A. (Cele de dinainte rămân: `laborator-ocupat.txt` de șters de mână,
  `claude auth login` până pe 29 nov, `rebase --continue`, opțional „da (0′)”.)
