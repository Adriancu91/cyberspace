# Pre-înregistrare: S137 B — laboratorul, harta greutății textului: (H) vs S135 (0), 60 de minute de la zero

<!-- scrisa: 2026-11-25T10:59:50 -->
*Scrisă la 2026-11-25 10:59, înainte de rulare. După ce rularea a început, textul de mai jos nu se mai schimbă; la închidere
se adaugă doar secțiunea „Ce a ieșit” (python unelte/preinregistrare.py --inchide laborator_harta).*

## Întrebarea

La aceeași oră de ceas pe placă, de la zero, iese o notă mai bună la română dacă ferestrele de text nu sunt trase la
întâmplare, ci mai des din regiunile unde „mai e ceva de învățat” — scorul = pierderea de acum minus pierderea lui #513
pe aceeași regiune (ideea RHO-LOSS, Mindermann et al. 2022, arXiv 2206.07137)? (Sarcina S137, a treia probă a
laboratorului C-163, aprobată de Adrian în hub `DECIZII.md` 24 nov 2026 21:39 — „da harta”.)

## Ce rulează

- Cine: executantul cascadei, pe RTX 3070 Ti 8 GB, în fereastra 07:00–23:00 (ultima pornire 21:15), cu
  `C:\Kronos\cyber-test\laborator-ocupat.txt` scris înainte („S137 (H)”, început + 1 h 40 min) și golit după;
  niciodată cât există `porneste-test.txt`; placa sub 1.000 MB și 50 °C la pornire.
- Întâi o probă de 3 minute pe placă (memoria și că eroarea scade), apoi:
  **(H)** `.venv/Scripts/python -X utf8 unelte/laborator_harta.py --minute 60 --dispozitiv cuda --iesire lucru/laborator/S137_H`
- **Exact rețeta S135 (0)**: aceeași rețea ca #513 (12 straturi, 12 capete, n_emb 768, context 512, vocabular 16.384,
  `date/ws/bpe_16384.json`, capul legat), de la zero, sămânța 1163, datele = doar textul W2
  (`lucru/bucati/w2_amestec_be12`, sha 560863a9…), lot 12 × 512 × adunare 8 = 49.152 simboluri pe pas, AdamW
  (0,9/0,999, eps 1e-8, scăderea greutăților 0,1, tăierea 1,0), bf16 cu autocast, rata de vârf 6e-4, încălzire 3 min,
  constantă, răcire liniară la 0 în minutele 45–60, 60 de minute pe ceas.
- **Singura diferență: ferestrele vin din `module/date_harta.py`**: primele 5 minute la întâmplare (ca (0)); apoi
  regiuni de 1.048.576 simboluri (1.280), `p_acum` = EMA (α = 0,05) a pierderii pe fereastră, scorul
  `max(p_acum − ref, 0)`, probabilitatea = ½ uniform + ½ după scor, ponderea tăiată între 0,25× și 4× din partea
  uniformă. Harta de referință #513 e deja făcută în A pe procesor (`lucru/laborator/harta_ref_513.npy`, media 1,560) —
  nu intră în ora de ceas.
- Examenele (aceleași ca la S135, funcția `examene` din `unelte/laborator_trepte.py`, nimic schimbat): **română curat
  (`romana_bpb`, judecătorul)**, **`examen_bpb` / `val_bpb` (martorul)**, **R1 instrucțiuni** (+ R1 ascuns).
- Modelul rămâne **doar** în `lucru/laborator/S137_H/` (nu în jurnal, nu în interfață, nu în export).
- SHA-256 înainte/după pe aceleași 21 de fișiere ca la S135 (#513, #651, #736, `kronos/*.py`, `module/examen_bpb.py`,
  `docs/conversatie/examen*.json`).
- **Baza = S135 (0)** (`lucru/laborator/S135_0/rezultat.json`): română 1,5343, `examen_bpb` 0,5394, R1 instrucțiuni
  42,07, 140.820.480 simboluri văzute, 2.865 pași, placa max 5.952 MB / 65 °C. (0) e validă (1,5343 < 2,0).

## Pragurile (ale supraveghetorului, copiate întocmai din coadă)

- **(H) CÂȘTIGĂ** = română(H) ≤ română(0) − **0,010** **și** `examen_bpb`(H) ≤ `examen_bpb`(0) + **0,005**;
- **LA FEL** = |română(H) − română(0)| < 0,010; **PIERDE** = română(H) ≥ română(0) + 0,010;
- dacă română câștigă dar `examen_bpb` urcă cu > 0,005 → verdict **„câștig strâmb”** (harta a mutat modelul spre o parte
  a textului) — nu e câștig;
- **R1** se măsoară, nu decide; **validitate:** S135 (0) validă, (H) sub 7.000 MB și 83 °C, SHA înainte = după,
  simbolurile văzute de (H) în ±5 % față de (0) (altfel harta a încetinit pasul și o scrii).
- Dacă S135 a arătat deja că (1) câștigă, compari (H) tot cu (0) (nu cu (1)); combinarea lor vine abia după, cu „da”.
  (S135 a ieșit: (1) PIERDE — deci comparația e oricum cu (0).)
- Paznicul: peste 7.000 MB sau 83 °C → oprire; NaN sau eroare care urcă fără oprire → oprire, fără să reglez nimic
  singur (decide supraveghetorul).

Cu cifrele lui (0): CÂȘTIGĂ cere română(H) ≤ **1,5243** și `examen_bpb`(H) ≤ **0,5444**; PIERDE = română(H) ≥ **1,5443**;
fereastra de simboluri valide = **133,78 – 147,86 milioane**.

## Așteptările, în cifre (ghicirea executantului, înainte de proba pe placă)

| | S135 (0) (măsurat) | (H) ghicit |
|---|---|---|
| simboluri văzute în 60 min | 140.820.480 | ~138 milioane (−2 %: alegerea ferestrelor pe procesor la fiecare pas; în ±5 %) |
| pași | 2.865 | ~2.810 |
| **română curat (`romana_bpb`)** | **1,5343** | **~1,530** (între 1,515 și 1,545) |
| `examen_bpb` (`val_bpb`) | 0,5394 | ~0,545 (puțin mai rău: TinyStories și textul ușor vin mai rar) |
| R1 instrucțiuni | 42,07 | ~40 (între 30 și 50; nu decide) |
| memoria maximă a plăcii | 5.952 MB | ~5.960 MB (harta e doar câțiva KB în RAM) |

Ghicirea mea pentru verdict: **LA FEL** (|Δ română| < 0,010), cu o ușoară înclinare spre câștig. De ce: la o singură
oră de la zero modelul e departe de #513 peste tot, deci scorul `p_acum − ref` e mare la aproape toate regiunile și
harta seamănă mult cu tragerea uniformă (mai ales cu jumătatea uniformă și tăierea 0,25×–4×); la proba de procesor din
A, sferturile au fost trase aproape egal (1.158 / 1.074 / 1.125 / 987). Încredere mică: o singură rulare, zgomotul
între două rulări identice nu e măsurat (ar fi S138 (0′), neaprobată).

## Ce ar infirma așteptările

- română(H) ≤ 1,5243 și `examen_bpb`(H) ≤ 0,5444 → **CÂȘTIGĂ** (harta ajută deja în prima oră; ghicirea mea „la fel” e greșită);
- română(H) ≤ 1,5243 dar `examen_bpb`(H) > 0,5444 → **câștig strâmb** (nu e câștig);
- română(H) ≥ 1,5443 → **PIERDE** (harta strică; ne oprim, cum cere Adrian);
- simbolurile văzute în afara 133,78–147,86 milioane → probă cu pas încetinit/schimbat (o scriu; verdictul nu e curat);
- sfertul cel mai ușor (după `ref`) tras de > 2× mai rar sau mai des decât cel mai greu, la sfârșit, în `progres.csv` →
  harta s-a depărtat mult de uniform (ghicirea mea „seamănă cu uniform” e greșită).

## Să nu uit

- Proba de 3 minute merge în `lucru/cascada/S137_proba/placa_3min_H/` (nu în `lucru/laborator/S137_H/`), ca ieșirea
  oficială să fie goală la pornire (unealta refuză să scrie peste).
- Scriu temperatura și memoria maximă; S135 (0) a rulat dimineața (07:35), (H) la prânz — placa poate fi mai caldă.
- Dacă proba e întreruptă de o repornire (ciclul de test OS), o reiau de la zero (nu e `oprit`); ieșirea veche o mut, nu o șterg.
- După: golesc `laborator-ocupat.txt` (ștergerea e refuzată de permisiuni → îl rescriu „LIBER”), SHA după,
  `--inchide laborator_harta` + „Verdictul”, rândul (H) în al doilea tabel din `docs/integrare_kronos/BANC_ANTRENARE.md`,
  cât s-a tras din fiecare sfert, un rând sus în `plan/pentru_adrian.md`, coada → `gata`.
- Rezultatul negativ se scrie la fel de clar ca cel pozitiv.
