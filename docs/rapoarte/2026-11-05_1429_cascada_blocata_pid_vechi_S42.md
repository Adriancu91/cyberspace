# Cascada blocată: o înregistrare veche S42 apare „în lucru” (PID refolosit de Windows) — 5 nov 2026, 14:29

Scris de executant (rularea programată de la 14:28). Nu am pornit nimic.

## Ce am văzut
- `git pull --rebase`: fără conflicte (ultimul commit: e161efe, supraveghetor 14:20 — „S77a → S78 → S79”).
- `unelte/cascada.py stare` la 14:28: fereastra „zi”, 241 de minute rămase; placa liberă (750 MB, 28 °C, încărcare 2 %);
  niciun proces greu; **dar `"liber": false`**.
- Singurul motiv: înregistrarea `lucru/cascada/S42_0833.json` (prima pornire S42, 28 oct 08:33, PID 19792) nu are „cod”
  (a fost mutată deoparte de `porneste --din-nou` înainte să-și scrie codul), așa că `cascada.py` întreabă Windows dacă
  PID-ul 19792 mai trăiește. Trăiește — dar e alt proces: `tasklist` arată **`dllhost.exe`**, 16 MB, fereastra
  „OleMainThreadWndName” (un proces COM al Windows, nu Python, nu antrenarea).
- Aceeași situație și la trecerea de la 13:59 (nota mea de atunci: dacă se repetă, raport, nu ocolesc). S-a repetat.
- În coadă nimic nu e `in_lucru`. Prima sarcină `aprobat` potrivită ar fi **S77a** (după 14:00, procesor ~3 h + placă ≤ 1,5 h,
  gata până la 18:30) — **nepornită**, pentru că regula cere „liber”: true.

## Ce NU am făcut
- N-am pornit S77a și n-am schimbat nicio stare în `plan/coada.md`.
- N-am editat `S42_0833.json` și n-am schimbat `unelte/cascada.py` (ar fi „reparat pe ascuns” regula de „liber”).
- N-am oprit procesul 19792 (e al Windows).

## Ce propun (alegerea e a supraveghetorului / a lui Adrian)
1. **Repede (recomandat):** în `lucru/cascada/S42_0833.json` se adaugă `"cod": null` și
   `"terminata": "2026-10-28T12:29:00"` plus o notă („pid refolosit de dllhost.exe, 5 nov”) — exact ce scrie și `cascada.py`
   singur când procesul nu mai există. Nu se șterge nimic. Dacă primesc „da” în coadă, o fac eu la trecerea următoare.
2. **Durabil:** `traieste()` din `unelte/cascada.py` să verifice și numele procesului (`python.exe`) sau ora pornirii lui
   față de „pornita”; cu test nou. (Aceeași capcană a mai apărut pe 4 nov la 18:58 cu PID-ul vechi S45 14764.)

Altfel, cascada rămâne blocată cât trăiește `dllhost.exe` 19792 (poate ore întregi), iar S77a riscă să nu fie gata până la 18:30
(noaptea S77b depinde de cifrele ei).

## Teste
Nu am schimbat cod; testele nu au fost rulate în această trecere.

## Ce aștept
Un „da” pentru varianta 1 (sau 2) în coadă / în `COMENZI.md`. Imediat după, pornesc S77a.
