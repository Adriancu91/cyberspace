# S80 — `unelte/cascada.py`: un PID refolosit de Windows nu mai blochează cascada

Executant, 5 nov 2026, 17:36. Sarcina S80 (aprobată de supraveghetor la 17:15, granițele 5 și 6). Doar procesor, fără placă.

## Ce era stricat

`lucru/cascada/S42_0833.json` (o pornire veche S42, mutată deoparte de `porneste --din-nou`, fără „cod”) are PID-ul 19792.
Windows a dat între timp acest număr lui `dllhost.exe`. `traieste()` căuta doar cifra în ieșirea lui `tasklist`, deci credea
că S42 „merge” → `"liber": false` → S77a, S78, S79 n-au putut porni între 14:00 și 17:30. Aceeași capcană pe 4 nov la 18:58
(PID-ul vechi S45 14764).

## Ce s-a schimbat (doar `unelte/cascada.py` și `teste/test_cascada.py`)

1. **`traieste(pid, pornita=None)`**: pe Windows, procesul contează ca „al nostru” doar dacă
   - numele programului e `python.exe` (citit din `tasklist /FI "PID eq <pid>" /FO CSV /NH`, coloana PID comparată exact,
     nu căutată în text), **și**
   - când e dată ora înregistrării, procesul n-a pornit cu mai mult de 5 minute după ea (ora din
     `Get-CimInstance Win32_Process` → `CreationDate`). Dacă ora nu se poate citi, hotărăște doar numele.
   - Pe alte sisteme rămâne `os.kill(pid, 0)`. `sarcina()` îi dă și `s["pornita"]`.
2. **Înregistrările mutate deoparte** (`<sarcina>_<HHMM>[_n].json`, recunoscute după câmpul „sarcina” diferit de numele
   fișierului) sunt socotite terminate (`merge = false`, `cod = null`) fără să mai fie întrebat Windows.
   `muta_vechea`, când mută o înregistrare fără „cod”, scrie acum în ea `"cod": null`, `"terminata"` (ora mutării) și
   `"nota": "mutată fără cod"`.
3. Înregistrările vechi din `lucru/cascada/` (inclusiv `S42_0833.json`) **nu au fost editate**; codul le tratează corect.
   Procesul 19792 (al Windows) n-a fost atins.

## Testele noi (în `teste/test_cascada.py`, cu `tasklist`/PowerShell înlocuite, fără Windows adevărat)

- `test_pid_refolosit_de_alt_program_nu_merge`: PID viu dar `dllhost.exe` → nu merge; PID inexistent → nu merge;
  alt PID care conține cifrele (197920) → nu merge.
- `test_python_pornit_inainte_merge_iar_cel_pornit_dupa_nu`: `python.exe` pornit la/înainte de `pornita` → merge; pornit
  la 2 ore după → nu merge; ora necitibilă → hotărăște numele (merge).
- `test_inregistrare_mutata_fara_cod_nu_blocheaza_liber`: `S42_0833.json` fără cod → `merge = false`, Windows nu e întrebat,
  `stare()` dă `liber: true`, fișierul rămâne neschimbat.
- `test_muta_vechea_fara_cod_scrie_cod_null`: mutarea unei înregistrări fără cod scrie `cod: null`, `terminata`, `nota`.

Testele vechi ale cascadei trec neschimbate (10/10 în fișier).

**Toate testele:** `CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -m pytest -o addopts="" -q` → **1225 trec, 1 sărit**
(5 min 33 s).

## `cascada.py stare` înainte și după

Înainte (17:28):

```
  "sarcina": "S42", "pid": 19792, "pornita": "2026-10-28T08:33:21", "merge": true, "cod": null
 "procese_grele": [],  placa 879 MB, 27 °C
 "liber": false
```

După (17:36):

```
  "sarcina": "S42", "pid": 19792, "pornita": "2026-10-28T08:33:21", "merge": false, "cod": null
 "procese_grele": [],  placa 643 MB
 "liber": true
```

(Ieșirea întreagă de după: `lucru/cascada/S80_stare_dupa.txt`.)

## Ce urmează

S80 → `gata`. Următoarea: **S77a** (pașii 1–2 pe procesor imediat; măsurătorile pe placă până la 18:30 sau de la 19:00;
totul până la 23:30). Apoi S78 → S79. De la Adrian nu aștept nimic pentru S80.
