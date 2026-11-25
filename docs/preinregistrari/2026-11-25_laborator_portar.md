# Pre-înregistrare: S139 B — laboratorul, portarul (amestecul de adâncimi): (P) vs S135 (0), 60 de minute de la zero

<!-- scrisa: 2026-11-25T14:40:44 -->
*Scrisă la 2026-11-25 14:40, înainte de rulare. După ce rularea a început, textul de mai jos nu se mai schimbă; la închidere
se adaugă doar secțiunea „Ce a ieșit” (python unelte/preinregistrare.py --inchide laborator_portar).*

## Întrebarea

La aceeași oră de ceas pe placă, de la zero, iese o notă mai bună la română dacă la jumătate din straturi (2, 4, …, 12)
un „portar” (un selector liniar mic) lasă doar ~50 % din simboluri să treacă prin strat, iar ceilalți merg pe legătura
directă — mai puțin calcul pe pas, deci mai mulți pași în aceeași oră (ideea „Mixture-of-Depths”, Raposo et al., 2024,
arXiv 2404.02258)? (Sarcina S139, a patra probă a laboratorului, aprobată de Adrian în hub `COMENZI.md` C-167 și
`DECIZII.md`, 25 nov 2026 11:41.)

## Ce rulează

- Cine: executantul cascadei, pe RTX 3070 Ti 8 GB, în fereastra 07:00–23:00 (ultima pornire 21:15), cu
  `C:\Kronos\cyber-test\laborator-ocupat.txt` scris înainte („S139 (P)”, început + 1 h 40 min) și golit după;
  niciodată cât există `porneste-test.txt`; placa sub 1.000 MB și 50 °C la pornire.
- Întâi o probă de 3 minute pe placă (memoria, viteza, eroarea scade, partea aleasă ~50 %), în
  `lucru/cascada/S139_proba/placa_3min_P/`, apoi:
  **(P)** `.venv/Scripts/python -X utf8 unelte/laborator_portar.py --minute 60 --dispozitiv cuda --iesire lucru/laborator/S139_P`
- **Exact rețeta S135 (0)**: aceeași rețea ca #513 (12 straturi, 12 capete, n_emb 768, context 512, vocabular 16.384,
  `date/ws/bpe_16384.json`, capul legat), de la zero, sămânța 1163 (partea comună a greutăților pornește identic cu (0) —
  selectorii se fac după; verificat în `teste/test_laborator_portar.py`), datele = doar textul W2
  (`lucru/bucati/w2_amestec_be12`), loturile trase uniform ca la (0), lot 12 × 512 × adunare 8 = 49.152 simboluri pe
  pas, AdamW (0,9/0,999, eps 1e-8, scăderea greutăților 0,1, tăierea 1,0), bf16 cu autocast, rata de vârf 6e-4,
  încălzire 3 min, constantă, răcire liniară la 0 în minutele 45–60, 60 de minute pe ceas.
- **Singura diferență: portarul** (`module/model_portar.py`): la straturile 2, 4, 6, 8, 10, 12 un `Linear(768, 1)` dă
  scorul r; la antrenare top-k pe text (256 din 512), Q doar de la cei aleși, K/V de la toți, masca după poziția
  originală, ieșirea × `sigmoid(r)`; plus BCE (ponderea 0,01) ca selectorul să prezică top-k. 6 × 769 = 4.614 parametri
  în plus. Selectorii primesc aceeași rată ca restul.
- Examenele (aceleași ca la S135, funcția `examene` din `unelte/laborator_trepte.py`, nimic schimbat), **în modul
  cauzal** (`sigmoid(r) > 0,5`, simbol cu simbol): **română curat (`romana_bpb`, judecătorul)**, **`examen_bpb` /
  `val_bpb` (martorul)**, **R1 instrucțiuni** (+ R1 ascuns). Separat: partea aleasă în modul cauzal la examenul de română
  (o trecere în plus a examenului de română; trebuie să dea aceeași notă) și, doar informativ, româna și `examen_bpb` în
  modul top-k (nu decide).
- Modelul rămâne **doar** în `lucru/laborator/S139_P/` (nu în jurnal, nu în interfață, nu în export).
- SHA-256 înainte/după pe aceleași 21 de fișiere ca la S135/S137 (#513, #651, #736, `kronos/*.py`,
  `module/examen_bpb.py`, `docs/conversatie/examen*.json`).
- **Baza = S135 (0)** (`lucru/laborator/S135_0/rezultat.json`, validă): română 1,5343, `examen_bpb` 0,5394, R1
  instrucțiuni 42,07, 140.820.480 simboluri văzute, 2.865 pași, placa max 5.952 MB / 65 °C. **Viteza lui (0) între
  minutele 5 și 45** (din `lucru/laborator/S135_0/progres.csv`, rândurile 5,01 → 44,01, aceeași funcție `viteza_intre`
  ca la (P)): **39.114,9 simboluri/s** (91.521.024 simboluri în 2.339,8 s).

## Pragurile (ale supraveghetorului, copiate întocmai din coadă)

- **(P) CÂȘTIGĂ** = română(P) ≤ **1,5243** **și** `examen_bpb`(P) ≤ **0,5444**; **LA FEL** = română(P) între 1,5243 și
  1,5443; **PIERDE** = română(P) ≥ **1,5443**;
- română câștigă dar `examen_bpb` > 0,5444 → **„câștig strâmb”** — nu e câștig;
- **viteza** (cerută de Adrian): scrii simbolurile/s ale lui (P) față de (0), măsurate pe placă între minutele 5 și 45
  (fără încălzire și răcire); (P) e „și mai rapid” doar dacă e ≥ **1,05×**; altfel scrii „câștigul (dacă e) vine doar
  din calitate”. Viteza nu schimbă verdictul de mai sus;
- **R1** se măsoară, nu decide;
- **validitate:** examenele în modul **cauzal**; în modul cauzal, la examenul de română, partea de simboluri alese la
  straturile cu portar e între **35 % și 65 %** (altfel (P) a folosit alt calcul decât cel aprobat → scrii „probă
  nevalidă”, nu verdict); (P) sub 7.000 MB și 83 °C; SHA înainte = după; nicio NaN. Simbolurile văzute **nu** au
  fereastra ±5 % (portarul trebuie să facă mai mulți pași) — doar le scrii.
- Paznicul: peste 7.000 MB sau 83 °C → oprire; NaN sau eroare care urcă fără oprire → oprire, fără să reglez nimic
  singur (decide supraveghetorul).

Cu cifrele lui (0): „și mai rapid” cere ≥ **41.071 simboluri/s** (1,05 × 39.114,9).

## Așteptările, în cifre (ghicirea executantului, înainte de proba pe placă)

| | S135 (0) (măsurat) | (P) ghicit |
|---|---|---|
| simboluri/s, minutele 5–45 | 39.115 | ~43.000 (~1,10×; între 1,00× și 1,20×) |
| simboluri văzute în 60 min | 140.820.480 | ~153 milioane |
| pași | 2.865 | ~3.110 |
| **română curat (`romana_bpb`)** | **1,5343** | **~1,545** (între 1,525 și 1,565) |
| `examen_bpb` (`val_bpb`) | 0,5394 | ~0,545 |
| R1 instrucțiuni | 42,07 | ~38 (între 28 și 48; nu decide) |
| memoria maximă a plăcii | 5.952 MB | ~5.800 MB (mai puține activări la straturile cu portar) |
| partea aleasă, modul cauzal, la română | — | ~50 % (între 40 % și 60 %) |
| potrivirea cauzal ↔ top-k la antrenare (sfârșit) | — | ~90 % (la proba de procesor: 94 %) |

De ce viteza doar ~1,10×: la straturile cu portar atenția și MLP-ul trec doar jumătate din simboluri, dar cheile și
valorile se calculează pentru toți, iar capul (16.384 × 768) și cele 6 straturi întregi rămân; calculul ideal scade la
~80 % (≈ 1,23×), din care se pierde o parte pe top-k, gather/scatter și masca pe fiecare text (fără nucleele „flash”).

Ghicirea mea pentru verdict: **LA FEL, înclinat spre PIERDE** (română ~1,545). De ce: la capacitate 50 % pe jumătate din
straturi, fiecare simbol pierde în medie ~25 % din calculul pe care îl primea; câștigul de ~10 % în pași probabil nu
acoperă asta într-o singură oră; în plus, la examen alegerea e cauzală (prezisă de selector), nu top-k — o mică
nepotrivire față de antrenare. Încredere mică: o singură rulare.

## Ce ar infirma așteptările

- română(P) ≤ 1,5243 și `examen_bpb`(P) ≤ 0,5444 → **CÂȘTIGĂ** (ghicirea mea e greșită; după, fișa
  `docs/integrare_kronos/PORTAR_FISA.md` pentru Cyber-GPU);
- română(P) ≤ 1,5243 dar `examen_bpb`(P) > 0,5444 → **câștig strâmb** (nu e câștig);
- română(P) ≥ 1,5443 → **PIERDE** (ne oprim acolo, cum cere Adrian);
- viteza ≥ 1,20× sau < 1,00× → ghicirea mea despre viteză e greșită (în sus: calculul ideal a ajuns aproape întreg; în
  jos: top-k, gather/scatter și masca costă mai mult decât economisesc);
- partea aleasă în modul cauzal la română în afara 35–65 % → **probă nevalidă** (fără verdict);
- potrivirea cauzal ↔ top-k sub 75 % la sfârșit → selectorul nu a învățat să prezică top-k (examenul cauzal folosește
  alt calcul decât antrenarea; de scris lângă verdict).
- **Zgomotul** între două rulări identice **nu e măsurat** ((0′) din S138, neaprobată): o diferență de ~0,01 la română
  poate fi și întâmplare.

## Să nu uit

- Proba de 3 minute merge în `lucru/cascada/S139_proba/placa_3min_P/` (nu în `lucru/laborator/S139_P/`), ca ieșirea
  oficială să fie goală la pornire (unealta refuză să scrie peste); la probă `--fara-examene`.
- Verific `porneste-test.txt` IMEDIAT înainte de `porneste`.
- Viteza lui (P) o iau din `rezultat.json` → `viteza_minutele_5_45` (aceeași funcție ca la (0)).
- Partea aleasă la română: `examene.romana_cauzal_parte_aleasa.parte_aleasa_cauzal`; trebuie ca
  `romana_cauzal_parte_aleasa.romana_bpb` = `examene.cauzal.romana.romana_bpb` (aceeași notă).
- Dacă proba e întreruptă de o repornire (ciclul de test OS), o reiau de la zero (nu e `oprit`); ieșirea veche o mut, nu
  o șterg.
- După: golesc `laborator-ocupat.txt` (ștergerea e refuzată → îl rescriu „LIBER”), SHA după, `--inchide
  laborator_portar` + „Verdictul”, rândul (P) în al doilea tabel din `docs/integrare_kronos/BANC_ANTRENARE.md` (cu
  simboluri/s), un rând sus în `plan/pentru_adrian.md`, coada → `gata`.
- Rezultatul negativ se scrie la fel de clar ca cel pozitiv.

## Ce a ieșit

*Adăugat la 2026-11-25 16:29, din jurnalul Kronos (lucru/jurnal/experimente.jsonl) și din jurnalul CONTINUUM pe bune. Verdictul se scrie dedesubt.*

Niciun experiment Kronos în perioada asta.

Niciun ciclu CONTINUUM pe bune în perioada asta.

(Modelul din laborator nu intră în jurnal — cifrele sunt din `lucru/laborator/S139_P/rezultat.json`.)

| | S135 (0) | (P) portarul | ghicirea mea |
|---|---|---|---|
| simboluri/s, minutele 5–45 | 39.114,9 | **41.527,1 (1,062×)** | ~43.000 (1,10×) |
| simboluri văzute | 140.820.480 | 149.520.384 (+6,2 %) | ~153 mil. |
| pași | 2.865 | 3.042 | ~3.110 |
| **română curat** | 1,5343 | **1,5286** (−0,0057) | ~1,545 |
| `examen_bpb` | 0,5394 | **0,5426** (+0,0032) | ~0,545 |
| R1 instrucțiuni | 42,07 | 26,44 | ~38 (28–48) |
| placa max | 5.952 MB / 65 °C | 5.997 MB / 65 °C | ~5.800 MB |
| partea aleasă, cauzal, la română | — | 38,9 % | ~50 % (40–60 %) |
| potrivirea cauzal ↔ top-k la sfârșit | — | 88,3 % (antrenare), 89,1 % (examen) | ~90 % |

Informativ (top-k, NU decide): română 1,5229, `examen_bpb` 0,5370. Nota cauzală la română dată de a doua trecere =
1,52856 = nota examenului (aceeași). SHA-256 înainte = după (21/21). Nicio NaN; cod 0.

## Verdictul

*Scris la 2026-11-25 16:29, strict după pragurile de mai sus.*

- **Validitate:** partea aleasă în modul cauzal la română 38,9 % ∈ [35 %, 65 %]; placa 5.997 MB / 65 °C (sub 7.000 MB și
  83 °C); SHA înainte = după; nicio NaN → **probă validă**.
- română(P) 1,5286: nu e ≤ 1,5243 și nu e ≥ 1,5443 → **LA FEL**. (P) nu câștigă (și nu pierde).
- **Viteza:** 41.527,1 / 39.114,9 = **1,062×** ≥ 1,05× → (P) e **„și mai rapid”** (prag 41.071). Viteza nu schimbă verdictul.
- R1 instrucțiuni 26,44 față de 42,07 (−15,6) — se măsoară, nu decide, dar e o scădere mare.
- Potrivirea cauzal ↔ top-k 88–89 % ≥ 75 % → selectorul a învățat să prezică top-k.
- Ghicirile mele: verdictul LA FEL — corect (dar înclinarea spre PIERDE greșită: româna a ieșit puțin mai bună); viteza
  1,06× în intervalul 1,00–1,20× (sub ghicirea 1,10×); memoria mai mare decât ghicisem; partea aleasă cauzal 38,9 %
  sub intervalul ghicit 40–60 % (dar în pragul de validitate); R1 sub intervalul ghicit.
- Zgomotul între două rulări identice nu e măsurat: −0,0057 la română poate fi și întâmplare.
