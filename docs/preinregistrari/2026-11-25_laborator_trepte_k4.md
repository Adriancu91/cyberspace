# Pre-înregistrare: S135 B — laboratorul treptelor: (0) rețeta de azi vs (1) bucăți K = 4, câte 60 de minute de la zero

<!-- scrisa: 2026-11-25T07:29:58 -->
*Scrisă la 2026-11-25 07:29, înainte de rulare. După ce rularea a început, textul de mai jos nu se mai schimbă; la închidere
se adaugă doar secțiunea „Ce a ieșit” (python unelte/preinregistrare.py --inchide laborator_trepte_k4).*

## Întrebarea

La aceeași oră de ceas pe placă, de la zero, iese o notă mai bună dacă în primele 40 de minute rețeaua învață pe
**bucăți de 4 simboluri** (media încorporărilor, ghicește bucata următoare — Patch-Level Training, ICLR 2025,
arXiv 2407.12665) și abia apoi simbol cu simbol? (Sarcina S135, C-163, aprobată de Adrian în hub 24 nov 2026 17:35.)

## Ce rulează

- Cine: executantul cascadei, pe RTX 3070 Ti 8 GB, doar în fereastra 07:00–23:00 (ultima pornire 21:15), cu
  `C:\Kronos\cyber-test\laborator-ocupat.txt` scris înainte și șters după; niciodată cât există `porneste-test.txt`.
- Întâi o probă de 3 minute pe placă (memoria și că eroarea scade), apoi, în ordine:
  - **(0)** `.venv/Scripts/python -X utf8 unelte/laborator_trepte.py --reteta 0 --minute 60 --dispozitiv cuda --iesire lucru/laborator/S135_0`
  - **(1)** `.venv/Scripts/python -X utf8 unelte/laborator_trepte.py --reteta 1 --minute 60 --k 4 --minute-bucati 40 --dispozitiv cuda --iesire lucru/laborator/S135_1`
    (după răcirea plăcii sub 50 °C, același protocol).
- Aceeași rețea ca #513 (12 straturi, 12 capete, n_emb 768, context 512, vocabular 16.384, `date/ws/bpe_16384.json`,
  capul legat), **de la zero**, sămânța 1163 la ambele (aceeași inițializare, aceleași loturi), datele = doar textul W2
  (`lucru/bucati/w2_amestec_be12`, același amestec deja tokenizat, sha 560863a9…), lot 12 × 512 × adunare 8 = 49.152
  simboluri pe pas, AdamW (0,9/0,999, eps 1e-8, scăderea greutăților 0,1, tăierea 1,0), bf16 cu autocast.
- **Rata de vârf 6e-4**, nu 5e-5: 6e-4 e rata de la zero a aceleiași mărimi (din `config/cod_c1.toml` / raportul S57);
  5e-5 de azi e pentru continuarea unui model deja antrenat, nu pentru pornirea de la zero. Program după ceas:
  încălzire liniară 3 min, constantă, răcire liniară la 0 în minutele 45–60 — același la ambele.
- Singura diferență: (1) are faza pe bucăți K = 4 în primele 40 de minute; apoi pasul de azi, cu aceleași greutăți și
  același AdamW (nerepornit).
- Examenele (aceleași ca la verdictele de azi, rulate de unealtă la sfârșit, nimic schimbat): **română curat
  (`romana_bpb`, judecătorul)**, **`examen_bpb` / `val_bpb` (martorul)**, **R1 instrucțiuni** (+ R1 ascuns).
- Modelele rămân **doar** în `lucru/laborator/S135_<reteta>/` (nu în jurnal, nu în interfață, nu în export).
- SHA-256 înainte/după pe aceleași 21 de fișiere ca la S135 A (#513, #651, #736, `kronos/*.py`, `module/examen_bpb.py`,
  `docs/conversatie/examen*.json`).

## Pragurile (ale supraveghetorului, copiate întocmai din coadă)

- **(1) CÂȘTIGĂ** = română(1) ≤ română(0) − **0,010** **și** `examen_bpb`(1) ≤ `examen_bpb`(0) + **0,005**;
- **LA FEL** = |română(1) − română(0)| < 0,010; **PIERDE** = română(1) ≥ română(0) + 0,010;
- **R1:** după o oră de la zero, doar pe text, **niciunul nu va atinge 90** (n-a văzut nicio instrucțiune) — se măsoară
  și se raportează la ambele, nu decide (scrii așteptarea ta); judecătorul e română curat, ca în decizie;
- **validitate:** (0) trebuie să ajungă sub **2,0** bpb română (altfel rețeta de la zero e stricată și comparația nu
  spune nimic → raportezi „probă nevalidă”, nu „pierde”); ambele sub 7.000 MB și 83 °C; SHA înainte = după.
- Paznicul: peste 7.000 MB sau 83 °C → oprire; NaN sau eroare care urcă fără oprire în primele 10 minute ale lui (0) →
  oprire, **fără reglarea ratei de către executant** (decide supraveghetorul).

## Așteptările, în cifre (ghicirea executantului, înainte de orice probă pe placă)

Viteza pe placă nu e încă măsurată pentru mărimea asta (banca S134 B n-a rulat); ghicesc ~25.000 simboluri/s la (0).

| | (0) rețeta de azi | (1) bucăți K = 4 |
|---|---|---|
| simboluri văzute în 60 min | ~90 milioane (±30 %) | ~250 milioane (~3,3× pe bucăți în 40 min ≈ 220 mil. + ~30 mil. pe simboluri) |
| română curat (`romana_bpb`) | ~1,80 (între 1,6 și 1,95 — validă) | ~1,76 (cu ~0,04 sub (0)) |
| `examen_bpb` (`val_bpb`) | ~1,15 | ~1,12 |
| R1 instrucțiuni | aproape 0 (sub 5; departe de 90) | aproape 0 (sub 5) |
| memoria maximă a plăcii | ~5.500 MB (sub 7.000) | ~5.500 MB |

Ghicirea mea pentru verdict: **(1) CÂȘTIGĂ, la limită** (lucrarea arată ~același câștig la jumătate din cost; la
aceeași oră aștept ceva mai bine, dar ultimele 20 de minute pe simboluri pot fi prea scurte ca să recupereze trecerea).
Încredere mică: pe un model de 124 milioane de parametri și o singură oră, ±0,010 poate fi și zgomot (S138 (0′) ar
măsura asta; nu e aprobată).

## Ce ar infirma așteptările

- română(1) ≥ română(0) + 0,010 → **PIERDE** (faza pe bucăți nu ajută la ora asta; ne oprim, cum cere Adrian);
- |română(1) − română(0)| < 0,010 → **LA FEL** (nu câștigă; ne oprim);
- română(1) mai bună cu ≥ 0,010, dar `examen_bpb`(1) > `examen_bpb`(0) + 0,005 → nu e câștig (martorul a urcat);
- română(0) ≥ 2,0 → **probă nevalidă** (rețeta de la zero stricată), nu „pierde”;
- simbolurile văzute la (1) sub 2× cele de la (0) → faza pe bucăți n-a mers de ~4 ori mai repede cum promite rețeta
  (scriu de ce, dacă se vede din `progres.csv`).

## Să nu uit

- Probele la ore diferite din zi pot avea placa la altă temperatură; scriu temperatura și memoria maximă la ambele.
- Dacă o probă e întreruptă de o repornire, o reiau de la zero (nu e `oprit`); ieșirea veche o mut, nu o șterg.
- Șterg `laborator-ocupat.txt` după fiecare probă; între (0) și (1) aștept placa sub 50 °C.
- Rezultatul negativ se scrie la fel de clar ca cel pozitiv; după verdict completez al doilea tabel din
  `docs/integrare_kronos/BANC_ANTRENARE.md` și un rând sus în `plan/pentru_adrian.md`.
