# S59 — Kronos-Cod: modelul citește simbolurile direct + examenul pe ore în biți pe octet

Executant, 31 octombrie 2026, 20:30–20:48. Doar cod și teste, pe procesor. Nimic pe placă, nimic descărcat, nimic
instalat, nicio antrenare. `kronos/`, `module/examen_bpb.py`, `module/model_gpt.py`, `module/model_muon.py`, paznicul,
jurnalul, modelele, linia română (#477) și setul ascuns: neatinse. Datele din `lucru/kronos_cod/`: doar citite.

## Pe scurt

- **Modelul nou** `module/model_gpt_cod.py` (`ModelGPTCod`, urmaș al `ModelGPTConversatieMuon`): dacă datele au
  `simboluri_antrenare()`, le ia direct (o copie în RAM ca int32, ~4,3 GB pe setul întreg; pe placă urcă doar lotul),
  fără tokenizare și fără să citească textul. Pe date text se poartă **bit cu bit** ca `ModelGPTConversatieMuon` (test).
- **Examenul nou de la fiecare oră** `module/examen_cod_validare.py` (`ExamenCodValidare`, scorul `val_bpb`): biți pe
  octet cu `unelte/kronos_cod/examen_validare.py`, pe un eșantion fix de **1.000 de fișiere** din cele 5.686 (sămânța 0).
- **`config/cod_c1.toml`** trece pe ele. Tot nepornită (nici proba de 10 minute).
- Ambele module trec `teste_contracte/` (adăugate în `MODULE`), au fișele în `module/manifeste/`.
- **Testele: 1159 trec, 1 sărit** (`CUDA_VISIBLE_DEVICES=-1 pytest`), față de 1145 la S57.
- **S58 NU poate porni chiar așa cum e scrisă**: antrenarea de noapte da, dar pașii 2 (proba de 10 minute) și 4(ii)
  (pass@k) n-au încă unealta potrivită. Detaliile și propunerea mai jos.

## Ce fișiere

| fișier | ce |
|---|---|
| `module/model_gpt_cod.py` (nou) | `ModelGPTCod`: simbolurile direct; refuză clar simboluri peste vocabular, tokenizer ≠ bpe, memorie/hrană/conversație |
| `module/examen_cod_validare.py` (nou) | `ExamenCodValidare(fisiere=1000, samanta=0, lot=8)`; pe date text / model fără rețea face ca examen_bpb (pentru contract) |
| `module/manifeste/model_gpt_cod.toml`, `examen_cod_validare.toml` (noi) | fișele, din `unelte/module_toml.py` |
| `teste/test_model_gpt_cod.py` (nou) | 10 teste (mai jos) |
| `teste_contracte/test_contracte.py` | cele două module noi în `MODULE` |
| `unelte/kronos_cod/examen_validare.py` | `pierderi()` socotește pierderea acolo unde sunt răspunsurile (pe placă) și urcă pe procesor doar sumele |
| `config/cod_c1.toml` | modelul `model_gpt_cod`, examenul `examen_cod_validare`, `previzualizare = true` la date, `hrana = ""` la model |

De ce s-a schimbat `examen_validare.py`: înainte, toate răspunsurile modelului (lot × 512 × 32.768 numere) coborau pe
procesor la fiecare lot — ~1 GB pe lot; pe eșantion ar fi fost zeci de GB mutați. Cifrele sunt aceleași (testul S57 cu
modelul „care nu știe nimic” trece neschimbat).

Două lucruri găsite pe drum, care ar fi oprit S58 din prima minută:
1. **Testul rapid al lui Kronos** (`kronos/orchestrator.py`, pasul 4) cere `date.text_validare()`, iar `date_cod` dă
   text doar cu `previzualizare = true` → am pus-o în configurare. Modelul nou nu folosește textul de antrenare (ia
   simbolurile); testul rapid ia doar începutul validării, decodat. **Fără nicio schimbare în `kronos/`.**
2. **`antrenare_lunga.py` pune singur „hrana implicită”** (poveștile cu fapte, în engleză, 5 % din lot) dacă setările
   modelului nu pomenesc `hrana` → modelul de cod ar fi refuzat-o. Am pus `hrana = ""` (cum cere chiar unealta).

## Testele noi (`teste/test_model_gpt_cod.py`, pe procesor, setul mic din `teste/cod_mic.py`)

1. învață din simboluri fără să citească textul (datele fără previzualizare refuză textul): pierderea după 40 de pași
   e cu peste 0,5 sub cea de la primul pas, același prim lot;
2. simbolurile stau în RAM, int32, identice cu cele din fișiere;
3. refuză simboluri peste vocabular, tokenizer „litere”, hrana;
4. pe date text: aceleași greutăți, bit cu bit, ca `ModelGPTConversatieMuon` (12 pași, adunare 2);
5. starea se salvează după examen și ora următoare continuă din ea;
6. eșantionul e același la două rulări și la două examene noi; altă sămânță → alt eșantion;
7. nota examenului = suma pierderilor / ln 2 / octeții textului **adevărat** al fișierelor (din `cod_mic`); aceeași
   notă la a doua rulare;
8. fără simboluri / fără rețea: biți pe octet pe text, prin `biti_pentru`;
9. `cod_c1.toml` se încarcă, construiește modelul și examenul nou fără să pornească;
10. **cap-coadă prin comanda din S58** (`antrenare_lunga.main` pe `cod_c1.toml` micșorat: rețea mică, context 16,
    setul mic, 2 secunde pe „oră”, procesor; restul configurării neschimbat): 2 ore, niciuna anulată, hrana goală,
    examenul pe eșantion la fiecare oră, starea salvată, ora a doua continuă din prima.

`python -m pytest`: **1159 passed, 1 skipped** (4 min 28 s).

## Eșantionul examenului pe datele reale (doar citire, procesor, 3,8 s)

Scriptul `lucru/cascada/S59_proba/esantion.py` → `esantion.json`:

| | toată validarea | eșantionul (1.000 de fișiere, sămânța 0) |
|---|---|---|
| fișiere | 5.686 | 1.000 (primele: 1, 12, 18, 25, 26, …) |
| simboluri | 12.619.825 | 2.099.455 (16,6 %) |
| octeți (textul decodat, UTF-8) | 43.685.786 | 7.184.891 |
| octeți pe simbol | **3,4617** (= S55 / S57, deci octeții prin decodare sunt corecți) | 3,4223 |
| bucăți de 512 | — | 4.654 (2,38 mil. poziții, cu umplutura) |

Eșantionul e același la două examene noi (`true`).

**Cât durează examenul pe eșantion (estimare, nu măsurare — S59 n-are voie pe placă):** 4.654 de bucăți, în loturi de
8 → 582 de loturi; un lot = 4.096 de poziții printr-un model de ~110 mil. parametri, în bf16 → **~30–90 de secunde**
pe RTX 3070 Ti, plus ~4 s pe procesor la prima oră (decodarea pentru octeți; apoi ține minte). Memoria plăcii la
examen: răspunsurile unui lot ~0,5 GB (bf16) + ~1 GB la pierdere; antrenarea (5,3–5,8 GB estimat la S57) rămâne vârful.
Cifra reală iese din prima oră a S58 (`secunde_examen` în fișa experimentului).

## Poate porni S58 așa cum e scrisă?

**Pasul 3 (antrenarea de noapte, 10 ore): da**, cu `python unelte/antrenare_lunga.py --config config/cod_c1.toml --ore 10`
(drumul întreg e testat cap-coadă pe setul mic). Recomand `--inceput "def "` (implicit e „Once upon a time”: povestea
de la final ar fi în engleză, nu cod; nu schimbă nimic altceva).

**Pasul 2 (proba de 10 minute): încă nu.** Unealta de probă de la S30, `unelte/proba_muon.py`, cere obligatoriu
`--porneste-din <experiment>`; `cod_c1` pornește de la zero. Propun o schimbare mică în `unelte/proba_muon.py`:
`--porneste-din` opțional (fără el: de la zero, fără stare de pornire) + un test. Fără `kronos/`, fără placă.

**Pasul 4(ii) (pass@1 / pass@10 pe cele 200 de probleme ascunse): încă nu.** `unelte/kronos_cod/examen_cod.py` știe să
noteze răspunsurile (`noteaza`, în cutie), dar nu are comanda care face modelul să **scrie** răspunsurile: n = 10 corpuri
pe problemă (cu temperatură, oprire la sfârșitul funcției), din modelul salvat. Propun o comandă `model` în
`examen_cod.py` (cu teste pe setul de PROBĂ, nu pe cel ascuns, care rămâne nedeschis până la S58) — tot doar cod și teste.

Pasul 4(i) (examenul întreg, 5.686 de fișiere, pe tot și pe Python / Rust / C): **da**, cu
`python -X utf8 -m unelte.kronos_cod.examen_validare model --config config/cod_c1.toml --stare lucru/cod_c1/gpt.pt`
(acum mult mai rapid, cu pierderea pe placă).

Propunerea mea: o sarcină scurtă **S60** (procesor, ~1–2 ore) cu cele două unelte de mai sus, înainte de S58. Decizia
e a supraveghetorului / a lui Adrian. S58 rămâne oricum „propus — necesită Adrian”.

## De știut

- Paznicul îi memorează examenului nou amprenta **la prima rulare** (fișierul `module/examen_cod_validare.py`). Amprenta
  nu acoperă `unelte/kronos_cod/examen_validare.py`, pe care examenul îl folosește: o schimbare acolo n-ar fi văzută de
  paznic. După pornirea S58, `examen_validare.py` ar trebui tratat ca examenul (neatins fără aprobare).
- RAM la antrenare: ~2,2 GB simbolurile (uint16, în date) + ~4,3 GB copia int32 a modelului; la testul rapid se face o
  copie în plus, care se eliberează după el.

## Ce aștept

- De la supraveghetor: verificarea S59 și decizia despre S60 (proba de la zero + răspunsurile pentru pass@k).
- De la Adrian: „da S58”, când crede (după S60, dacă e aprobată).
