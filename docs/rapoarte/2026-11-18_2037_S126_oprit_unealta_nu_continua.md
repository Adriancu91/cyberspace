# S126 — OPRIT înainte de placă: unealta nu poate porni „din #692” pe aceeași linie

*Executantul, 18 noiembrie 2026, 20:37. Nimic nu a rulat pe placă, nimic șters, nimic schimbat în configurare sau în `kronos/`.*

## Pe scurt

Coada cerea (pasul 3): `python unelte/antrenare_recalcul.py --config config/conv_w2_mare_24zcf.toml --ore 4 --porneste-din 692`.
Pe linia `w2_mare_24zcf`, care are deja 4 ore făcute (#689–#692, de la S124), comanda asta **nu ar antrena nimic**:
ar sări direct la tabelul și povestea de la final, cu cod 0. Sarcina spune: „Dacă unealta refuză să continue din #692 pe
aceeași configurare: te oprești, scrii eroarea exactă în raport, `oprit` — fără schimbări în `kronos/` sau în configurare.”
Asta am făcut. **S126 e `oprit`; placa a rămas liberă.**

## Ce am verificat (doar citire, n-am pornit comanda)

1. `git pull` (49abee1): nota supraveghetorului de la 20:15 — `os-306` terminat, „pornești pasul 3 acum”.
2. `cascada.py stare` (20:29): fereastra „noapte”, 630 minute rămase, placa 618 MB / 30 °C / 0 %, niciun proces greu, „liber”: true.
3. Am pus S126 `in_lucru` (commit 01e57fc, urcat) și am început să copiez lanțul S124 (`lucru/cascada/S124_proba/s124.py`).
   Lanțul S124 cerea ca dosarul liniei să NU existe; aici există (`lucru/w2_mare_24zcf/`: `gpt.pt` 2,197 GB din 17 nov 23:05,
   `pornire.json` cu „experiment”: 680, `rezultat.json`, `placa_20261117_1900.csv`). Așa că m-am uitat cum tratează unealta
   `--porneste-din` pe o linie care are deja ore.
4. `unelte/antrenare_lunga.py` (pe care `antrenare_recalcul.py` doar o învelește):
   - rândul 427: `if args.porneste_din is not None and not args.raport and facute == 0 and not cale_stare.exists():` —
     pornirea dintr-un experiment se face **doar** pe o linie cu 0 ore și fără stare salvată. Aici `facute` = 4 și
     `lucru/w2_mare_24zcf/gpt.pt` există, deci `--porneste-din 692` e **ignorat, fără niciun mesaj**; „Pornesc din #692”
     nu ar apărea niciodată în jurnal.
   - rândul 453: `if not args.raport and facute < args.ore:` — cu `--ore 4` și 4 ore făcute, bucla de antrenare nu
     începe deloc.
   - Deci „eroarea exactă” nu e un mesaj de eroare, ci o tăcere: comanda s-ar fi încheiat fără nicio oră nouă.
5. Mai e un lucru: configurarea are `racire_finala = 0.25` (copia răcită). La S124, examenele s-au dat pe copia răcită
   (#692), iar linia „rămâne nerăcită” — deci `gpt.pt` din dosar e, cel mai probabil, starea **nerăcită** de după ora 4,
   nu chiar #692. Chiar și cu `--ore 8` (continuarea liniei) n-ar porni din #692, iar rata ar fi la capătul scăderii de
   4 h (`durata_scaderii_secunde = 14400`), nu repornită ca la S124. Ar fi alt experiment decât cel pre-înregistrat.

## Testele

`CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -m pytest -o addopts="" -q` → **1529 passed, 1 skipped** (6 min 59 s).

## Discul

C: 165 GB liberi (df, 20:37); nimic scris pe disc în afară de dosarul gol `lucru/cascada/S126_proba/`.

## Pre-înregistrarea

`docs/preinregistrari/2026-11-18_w2_mare_24zcf_b.md` rămâne **deschisă** (nu am închis-o: experimentul n-a rulat; se
poate folosi neschimbată dacă S126 pornește pe una din variantele de mai jos, cu o notă datată despre comandă).

## Ce propun (alege supraveghetorul sau Adrian; eu nu schimb nimic singur)

- **(a) recomandat — o configurare nouă, copie fidelă:** `config/conv_w2_mare_24zcf_b.toml` = `conv_w2_mare_24zcf.toml` cu
  doar `nume = "w2_mare_24zcf_b"` și `cale_stare = "lucru/w2_mare_24zcf_b/gpt.pt"` (aceleași date, aceeași rețetă), apoi
  `antrenare_recalcul.py --config config/conv_w2_mare_24zcf_b.toml --ore 4 --porneste-din 692`. Asta e exact ce cere
  S126: 4 h din #692, rata repornește, „Pornesc din #692” în jurnal. E o configurare nouă (sarcina interzicea schimbări
  „în configurare”), deci trebuie scrisă în coadă ca permisă. Discul: ~2,2 GB în plus pentru `gpt.pt` nou, marja rămâne ≥ 160 GB.
- **(b) continuarea liniei:** `--ore 8` pe aceeași configurare — pornește din starea nerăcită de după ora 4, cu rata la
  capătul scăderii. Nu e „din #692” și nu se potrivește cu pre-înregistrarea; nu o recomand.

Dacă (a) e aprobată la trecerea de 23:15, pot porni până la 01:00 (4 h + ~2 h examene → gata înainte de 07:00, cum cere
nota pentru ziua de 19 nov). Mai târziu de 01:00 nu pornesc; rămâne pentru noaptea 19 → 20.

## Ce aștept

- de la supraveghetor: alegerea (a) sau (b) scrisă în coadă, cu S126 pus iar `aprobat`;
- de la Adrian: nimic urgent; dacă vrei, „da S126 a” în hub.
