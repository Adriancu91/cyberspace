# S135 B — laboratorul treptelor: (0) rețeta de azi vs (1) bucăți K = 4 — verdictul: **(1) PIERDE**

*Scris de executantul cascadei, 25 noiembrie 2026, 10:30. Partea A: `docs/rapoarte/2026-11-24_2124_S135_laborator_trepte.md`.*

## Pe scurt

Am antrenat de la zero, câte **o oră** pe placă, aceeași rețea ca #513, în două feluri: (0) ca azi, simbol cu simbol;
(1) primele 40 de minute pe „bucăți” de câte 4 simboluri, apoi 20 de minute simbol cu simbol. (1) a văzut de **2,4 ori
mai mult text**, dar la româna curată (judecătorul) a ieșit **mai slab cu 0,0195** — peste pragul de 0,010.
După pragurile scrise dinainte: **(1) PIERDE**. Proba e **validă**. Martorul (`examen_bpb`) și R1 au ieșit mai bune
la (1), dar nu ele decid. Cum a cerut Adrian: dacă nu câștigă, ne oprim aici.

## Ce a rulat

| | (0) | (1) |
|---|---|---|
| comanda | `.venv/Scripts/python -X utf8 unelte/laborator_trepte.py --reteta 0 --minute 60 --dispozitiv cuda --iesire lucru/laborator/S135_0` | `.venv/Scripts/python -X utf8 unelte/laborator_trepte.py --reteta 1 --minute 60 --k 4 --minute-bucati 40 --dispozitiv cuda --iesire lucru/laborator/S135_1` |
| pornită → terminată (cu examenele) | 07:34:56 → 08:39:40, cod 0 | 08:59:44 → 10:04:34, cod 0 |
| placa înainte | 1.008 MB, 46 °C | 1.006 MB, 33 °C |
| proces | 24108 | 23472 |

Înainte: proba de 3 minute pe placă (5.935 MB, 62 °C, eroarea 7,87 → 5,06), pre-înregistrarea
`docs/preinregistrari/2026-11-25_laborator_trepte_k4.md` (urcată 5014ebb, înainte de pornire), SHA înainte 21/21.

## Cifrele (din `lucru/laborator/S135_<rețetă>/rezultat.json`)

| | (0) rețeta de azi | (1) bucăți K = 4 | diferența (1) − (0) |
|---|---|---|---|
| pași | 2.865 | 6.895 (5.940 pe bucăți + 955 pe simboluri) | |
| simboluri văzute | 140.820.480 | 338.903.040 (291,96 mil. + 46,94 mil.) | × 2,41 |
| **română curat (judecătorul)** | **1,5343** | **1,5538** | **+0,0195** (mai rău) |
| — wikipedia | 1,3644 | 1,3701 | +0,0057 |
| — web | 1,6337 | 1,6511 | +0,0174 |
| — cărți | 1,6316 | 1,6712 | +0,0397 |
| `examen_bpb` (martorul) | 0,5394 | 0,5144 | −0,0251 (mai bun) |
| R1 instrucțiuni (ascuns / vechi) | 42,07 (46,47 / 52,54) | 60,12 (60,87 / 61,91) | +18,05 |
| pierderea finală la antrenare | 2,0012 | 2,0761 | |
| placa maximă (nvidia-smi) | 5.952 MB, 65 °C | 6.018 MB, 65 °C | |
| memoria PyTorch (alocat / rezervat max) | 4.976 / 5.308 MB | 4.967 / 5.372 MB | |
| examenele au durat | 263 s | 265 s | |

## Verdictul (strict după pragurile pre-înregistrate)

- **Validitate: DA** — (0) are româna 1,5343 < 2,0; ambele sub 7.000 MB și 83 °C; SHA înainte = după (21/21 identice:
  #513, #651, #736, `kronos/*.py`, `module/examen_bpb.py`, `docs/conversatie/examen*.json`;
  `lucru/cascada/S135_proba/sha_inainte_B.json` vs `sha_dupa_B.json`).
- **română(1) ≥ română(0) + 0,010** (1,5538 ≥ 1,5443) → **(1) PIERDE.**
- R1: niciuna nu atinge 90 (42 și 60) — cum a spus supraveghetorul; nu decide.
- Ce notez, fără să schimbe verdictul: martorul și R1 merg în sens opus judecătorului. O explicație posibilă (nemăsurată):
  pe bucăți modelul a văzut mult mai mult text în engleză/TinyStories și cel de examen, dar româna de cărți și web (texte
  lungi, rare) a pierdut cel mai mult (+0,04 la cărți). O singură pereche de rulări; zgomotul nu e măsurat (ar fi S138 (0′)).
- Ghicirea mea („CÂȘTIGĂ, la limită”) a fost **greșită**. Și cifrele absolute le-am ghicit prost: placa a mers ~39.000
  simboluri/s (nu 25.000), româna ~1,53 (nu ~1,80), `examen_bpb` ~0,52 (nu ~1,15), R1 42/60 (nu „sub 5”).

## Testele

`CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -m pytest -o addopts="" --basetemp=lucru/teste_tmp -q`: **1590 trec, 1 sărit, 0 picate** (491 s). Nimic din cod nu s-a schimbat în partea B.

## Ce n-a mers / ce trebuie făcut de mână

- **`C:\Kronos\cyber-test\laborator-ocupat.txt` NU l-am putut șterge**: permisiunile executantului refuză `rm` și `mv` pe
  acel dosar. Am scris în el „LIBER — S135 (1) s-a terminat la 10:04:34”. **Te rog șterge-l de mână** (sau supraveghetorul),
  altfel testele OS pot crede că laboratorul e încă ocupat. La S137 B se va scrie din nou (cu Write merge).
- Nimic altceva oprit; paznicul n-a intervenit; nicio NaN.

## Ce urmează

- După regula din coadă: (1) nu câștigă → ne oprim cu faza pe bucăți (nu K = 2, nu ieșirea pe eșantion).
- Următoarea pe placă, după coadă: **S137 B (H)** „harta greutății textului” — comparată tot cu (0) (1,5343 / 0,5394 / 42,07).
  Condițiile ei: S135 B `gata` ✓, (0) validă ✓, S137 A `gata` ✓, plus pre-înregistrarea `laborator_harta` (o scrie
  executantul la trecerea care o pornește). Placa acum: 435 MB, 31 °C.
- Tabelul e completat în `docs/integrare_kronos/BANC_ANTRENARE.md` (al doilea tabel) — supraveghetorul îl copiază în hub.

## Ce aștept de la Adrian

- Să șteargă `C:\Kronos\cyber-test\laborator-ocupat.txt`.
- Nimic de decis pentru S135; opțional „da probele v2 (S138)” — (0′) ar spune cât de mare e zgomotul între două rulări.
