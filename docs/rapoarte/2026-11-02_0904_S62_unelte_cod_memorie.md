# S62 — uneltele de examen de cod se țin singure sub limita plăcii (raport, 2 nov 2026, 09:04)

Scris de executant (cascada). Sarcina: `plan/coada.md`, S62. Nu e antrenare, deci fără pre-înregistrare.

## Pe scurt
- **Gata.** Ambele măsurări pe placă au mers până la capăt (cod 0), **mult sub 6.500 MB**:
  (a) răspunsurile pe setul de probă: vârf **1.924 MB** (S58: 7.971 MB); (b) validarea întreagă: vârf **4.416 MB**.
- Cifra validării din `gpt.pt`: **0,51411 biți/octet** = exact 0,5141 de la S58. Calculul nu s-a schimbat.
- Teste: **1174 trec, 1 sărit**.
- **Uneltele pot fi folosite la S63** (`--lot 2 --memorie-max 6500`). S63 o pornește rularea următoare a executantului (o singură sarcină pe rulare).

## Ce s-a schimbat (commit 3d38dd4)
- `unelte/kronos_cod/memorie_placa.py` (nou): `Paza` — după fiecare lot golește memoria plăcii, citește vârful și, peste limită, aruncă `MemoriePeste`.
- `unelte/kronos_cod/examen_cod.py model`: `--lot` (implicit 2) și `--memorie-max` (implicit 6500 MB). Fiecare corp are sămânța lui
  (`samanta_corp`: sămânța de bază + problema + numărul corpului), deci răspunsurile sunt aceleași oricare ar fi `--lot`.
  Peste limită: unealta se oprește singură, cod de ieșire 3, scrie ce a apucat, marcat „incomplet”.
  **Atenție:** din cauza sămânței pe corp, răspunsurile NU mai sunt aceleași cu cele din S58 (alt șir de numere la întâmplare). Notarea, cutia, temperatura 0,8, `MAX_SIMBOLURI` 256 și seturile nu s-au schimbat.
- `unelte/kronos_cod/examen_validare.py`: citește și starea liniei (`lucru/cod_c1/gpt.pt`, prin `incarca_model`), cu aceeași oprire peste `--memorie-max`. Calculul biților neschimbat.
- `teste/test_s62_unelte_cod_memorie.py`: teste noi (commitul spune 7; în fișier sunt 6 funcții, una e probabil cu mai multe variante) (procesor, model mic, setul de probă): `--lot 1/2/10` dau răspunsuri identice; sămânța diferă pe corp și pe problemă; limita falsă mică oprește `examen_cod` cu cod ≠ 0 și fișier „incomplet”; `Paza` ține vârful și oprește; `examen_validare` dă aceeași cifră din `gpt.pt` și din modelul din jurnal; `examen_validare` se oprește peste limită.

## Măsurarea pe placă (2 nov, 08:37:57 – 08:48:36, proces 19520, cod 0)
Scriptul `lucru/cascada/S62_proba/s62.py`; `nvidia-smi` la 5 s în `placa.csv` (126 de citiri). Model: `lucru/cod_c1/gpt.pt`, config `config/cod_c1_init002.toml`. Setul ascuns NU a fost deschis.

| | (a) răspunsuri, setul de probă (20 × 10, `--lot 2`) | (b) validarea întreagă (5.686 fișiere, lot 16) | S58 (ii), referință |
|---|---|---|---|
| cod | 0 | 0 | — |
| durata | 91 s (96,7 s cu pornirea) | 534 s (S58: 370 s) | ~17 min la >7.000 MB |
| vârful măsurat de unealtă (torch) | 1.924 MB | 4.416 MB | — |
| vârful din `nvidia-smi` (la 5 s) | 1.395 MB | 3.968 MB | **7.971 MB** |
| temperatura maximă | 35 °C | 62 °C | — |
| cifra | — | **0,51411** biți/octet (Python 0,55475, Rust 0,43804, C 0,62223) | 0,5141 |

`nvidia-smi` arată mai puțin decât unealta pentru că citește doar la 5 s și poate rata vârfurile scurte; limita se aplică pe cifra uneltei, care e cea mai mare.

Validarea a durat 534 s față de 370 s la S58 (+44 %), probabil din cauza golirii memoriei și a citirii după fiecare lot. Pentru o rulare o singură dată pe noapte, nu contează.

## Durata estimată pentru 200 × 10 cu `--lot 2`
20 de probleme au durat 91 s, deci 200 de probleme ≈ **15 minute** (răspunsurile; notarea în cutie vine peste, pe procesor).
Cu validarea (~9 min), examenele S63 ar dura în total ~25–30 de minute, sub ora prevăzută.

## Testele
`CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -m pytest -q`: **1174 trec, 1 sărit** (4 min 46 s).

## Ce urmează
- S62 → `gata`. S63 (aprobată de Adrian, C-56, „imediat după S62 `gata` cu memoria sub 6.500 MB”) îndeplinește condiția:
  o pornește rularea următoare a executantului (pre-înregistrarea întâi, apoi setul ascuns nou, apoi cele 10 ore).
- De la tine, Adrian: nimic obligatoriu. De știut: pass@k din S63 se scrie cu sămânța pe corp, deci nu e aceeași tragere la sorți ca în S58 (era oricum alt set ascuns).
