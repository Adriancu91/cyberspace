# S77b — prima noapte a lui Kronos crescut la 24 de straturi: OPRIT (memorie insuficientă pe placă, după ~1 minut)

*Scris de executant (cascada), 5 nov 2026, 21:15.*

## Pe scurt

- **Verdict: OPRIT / NEMĂSURAT.** Antrenarea (experimentul **#516**) a căzut la **20:42:41**, la circa un minut după pornire,
  cu „CUDA out of memory”. Nicio oră de antrenare făcută, niciun examen rulat, niciun model nou.
- Cauza: unealta nouă `unelte/antrenare_recalcul.py` pune un **plafon PyTorch de 5.800 MB** (implicit). Antrenarea adevărată a
  cerut mai mult: avea deja **5,39 GiB** folosiți de PyTorch (+ 0,25 GiB rezervați) și a cerut încă **384 MiB**, peste limita de 5,66 GiB.
- Nu am reparat și nu am repornit nimic (regula: dacă pică, `oprit` și raport). Placa e liberă acum (353 MB, 29 °C).
- Testele: **1238 trec, 1 sărit** (`CUDA_VISIBLE_DEVICES=-1`, 5 min 35 s).

## Ce a rulat

Lanțul `lucru/cascada/S77b_proba/s77b.py`, pornit prin cascadă la 20:39:41 (PID 20416), încheiat la 20:42:42 cu **codul 1**.

| ora | pasul | rezultat |
|---|---|---|
| 20:39:48 | `creste_model.py romana` pe `lucru/w2_mare_24/gpt.pt` (procesor) | SHA-256 `d35e3dbe…92cc` ✓ (copia lui `gpt_24.pt`); română curat **1,2096** (= #477 1,2097 ± 0,001 ✓) |
| 20:41:28 | `antrenare_recalcul.py --config config/conv_w2_mare_24.toml --ore 5` | rețeta **24×768** ✓ în log; recalcul pe 24 de straturi; **#516 ANULAT la 20:42:41 — OutOfMemoryError** |
| — | examenele (`examen_validari_ws.py` S77b/#477/#513, `romana_raspunsuri.py reper`) | **nu au rulat** (lanțul s-a oprit la primul pas care a picat) |

Verificările de la pornire (pasul 3 din sarcină) au trecut: rețeta 24×768 și scorul de pornire = #477. Problema a apărut abia la antrenare.

## Cifrele plăcii (fișierul `lucru/w2_mare_24/placa_20261105_2041.csv`, la 10 secunde)

| ora | °C | MB |
|---|---|---|
| 20:41:32 – 20:42:12 | 27 | 748 |
| 20:42:22 | 32 | 4.755 |
| 20:42:32 | 29 | 4.755 |

Vârful văzut de `nvidia-smi`: **4.755 MB** (măsurare la 10 s; vârful real dinaintea erorii n-a fost prins). Temperatura max. **32 °C**.
Paznicul n-a avut de intervenit (eroarea vine din plafonul PyTorch, care a funcționat cum trebuia: n-a lăsat placa să treacă de prag).

## De ce nu a încăput, deși S77a spunea „6.010 MB”

- La S77a, măsurătoarea pentru N = 24 cu recalcul a avut plafonul **6.600 MB** (`creste_model.py`: 7.000 − 400) și a ajuns la
  **5.160 MB** în PyTorch / 6.010 MB în `nvidia-smi`, pe 60 de pași simpli.
- Antrenarea adevărată (`antrenare_lunga` prin Kronos) are în plus lucruri pe care măsurătoarea nu le avea. Un semn: rândul
  „Recalculul activărilor: 24 straturi împachetate” apare **de două ori** în log, adică se construiește **încă o copie a rețelei**
  (probabil reperul/copia de la oră; 183M parametri ≈ 0,7 GB în fp32). Asta e o presupunere, nu am verificat-o în cod.
- Cu plafonul de 5.800 MB ales în S77b (ca `nvidia-smi` să rămână sub 6.700), nu mai rămâne loc pentru acest plus.

## Ce n-am atins

`kronos/`, `module/`, examenul BPB, paznicul, jurnalul: neatinse. #477, #513, `lucru/w2_mare/gpt_24.pt`: doar citite. Nimic descărcat, nimic instalat.
**Atenție pentru o reluare:** folderul `lucru/w2_mare_24/` există acum (cu `gpt.pt` = copia lui `gpt_24.pt`, fișierul plăcii și un
`ruleaza.lock` gol rămas de la proces). Sarcina cere ca folderul să NU existe înainte (capcana S42). Nu l-am șters (nu am voie să șterg
modele); trebuie decis de supraveghetor/Adrian (de ex. o linie cu nume nou, sau mutarea folderului cu aprobare).

## Pre-înregistrarea

`docs/preinregistrari/2026-11-05_w2_mare_24.md` — închisă (`--inchide w2_mare_24`), cu verdictul **NEMĂSURAT**: nicio categorie
(MAI MARE = MAI BUN / LA FEL / MAI SLAB / STRICĂ) nu se poate aplica, fiindcă nu există nicio oră și niciun examen.

## Testele

`CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -m pytest -q` → **1238 passed, 1 skipped** (335,6 s).

## Ce urmează (variante pentru supraveghetor / Adrian)

1. **Lot 6 cu `adunare_loturi = 16`** (varianta scrisă deja în sarcină pentru „nu încape”): același lot efectiv (96), mai puțină
   memorie pentru activări; plafonul de 5.800 MB rămâne. Cere o schimbare în `config/conv_w2_mare_24.toml` și o pre-înregistrare nouă.
2. **Plafon mai mare** (de ex. `--memorie-max-mb 6.300`) — mai riscant: la S77a, `nvidia-smi` a sărit scurt peste plafon cu ~0,6–0,8 GB,
   deci ar putea atinge pragul de 7.000 MB al paznicului.

Recomandarea mea: varianta 1, întâi cu o probă scurtă de 15 minute pe placă, apoi noaptea întreagă (6→7 nov, de la 19:00).
În noaptea asta (5→6 nov) nu mai pornesc nimic pe S77b: sarcina e `oprit` și o reluare are nevoie de o sarcină nouă/aprobată.
