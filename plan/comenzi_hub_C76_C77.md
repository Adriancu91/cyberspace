# Textul comenzilor C-76 și C-77 din Cyber Hub (copiat de supraveghetor)

Copiat întocmai din `Adriancu91/Cyber-hub`, `COMENZI.md` (commit 9100002), de supraveghetor, 5 nov 2026, 20:15,
pentru că executantul nu poate citi hub-ul de pe workstation (raportul `docs/rapoarte/2026-11-05_1830_S78_oprit_comenzi_inaccesibile.md`).
Acesta e textul la care trimit S78 și S79 din `plan/coada.md` când scriu „exact ce scrie în C-77 / C-76”. Liniile „stare:” sunt ale hub-ului.

### C-77 · kronos · Salvează și organizează ce e util din vechiul proiect „Mini Brain” (Desktop) înainte ca Adrian să-l șteargă
- data: 2026-11-05 13:40 · de la: centrul de comandă, la cererea lui Adrian („copiază și organizează ce ai nevoie de acolo, apoi șterg tot”)
- surse (pe workstation, doar CITIRE): `C:\Users\Computer\Desktop\test ai brain v13 clean` (68 GB, versiunea nouă, 101 commit-uri) și
  `C:\Users\Computer\Desktop\test ai brain` (4,4 GB, copie veche). Analiza completă: `C:\Users\Computer\Desktop\raport-test-ai-brain.md` (citește-o întâi).
- ce: copiază (NU muta) în `C:\Kronos\arhiva\mini-brain\` (în afara repo-ului git):
  1. istoria git a ambelor foldere ca `git bundle create <nume>.bundle --all` (doar obiectele folosite, câțiva zeci de MB — NU pachetul de 19,5 GB);
  2. din v13: `mini_ai_brain\`, `docs\` (cu `knowledge_phase1\`), cele 9 `.md` + scripturile din rădăcină (unele NU sunt în git!), `tests\`, `scripts\`, `config\`,
     `demo\`, `manual_exploratory\`, `examples\`, `integrity\`, `experiments\**\*.py` + rezultatele, toate `results*.json/csv` + `*_REPORT.md` din `benchmarks\`;
  3. datele create de Adrian: seturile `sealed\` și NONPROTECTED, indexul lexical `rlx01…`, `bnl01…\final_state.json`;
  4. baza de cunoștințe geografică ACTIVĂ (build `f8547edc…` din `derived` + `authoritative`) și `raw\`;
  5. cele 17 fișiere unice din folderul vechi (commit `864c70e`): `benchmarks\standard_v0_1\v1b_prime_env_qualification_v13\` + `docs\V1B_PRIME_RUN_V13_HARDWARE_QUALIFICATION.md`.
  NU copia: `*.pt`, `.venv*`, `.standard05-cache`, `__pycache__`, pachetul `.git` mare, cele 4 build-uri geografice vechi.
- după copiere: `MANIFEST.txt` (fiecare fișier + SHA-256) și verifică sursă = copie; scrie `C:\Kronos\arhiva\mini-brain\CITESTE-MA.md` (ce e unde, ce s-a lăsat).
- în repo `cyberspace`: un singur document `docs/studiu/2026-11-05_lectii-mini-brain.md` cu lecțiile pentru Kronos (test mic de format înaintea rulărilor lungi —
  greșeala „NONE”/null; păstrarea doar a câștigătorului și `*.pt` în `.gitignore`; maxim 2–3 încercări pe întrebare; ideea de modul „fapte verificate” — doar PROPUNERE,
  nu cod). Fără date mari în git. NU atinge `kronos/`, examenul sau paznicul. Commit + push.
- final: raport în `docs/rapoarte/` + rând în `plan/pentru_adrian.md`: „Mini Brain salvat (X GB în arhivă) — Adrian poate șterge ambele foldere”. **Nimic șters de agent.**
- prioritate: înaintea lui C-76 (eliberează ~72 GB). Nu oprește antrenarea în curs.
- stare: preluat (2026-11-05 13:45, supraveghetor) — **S78** în `plan/coada.md`, aprobat; după 14:00, imediat după S77a; paza discului: rămân ≥ 20 GB liberi, altfel baza geografică așteaptă (și v13 nu se șterge încă); nimic șters de agent

### C-76 · kronos · Workstation-ul are doar ~40 GB liberi din 475 — raport de spațiu + propunere de curățenie (fără ștergeri)
- data: 2026-11-05 13:15 · de la: centrul de comandă, la cererea lui Adrian (curățenie pe workstation)
- ce: executantul, pe procesor, fără să oprească nimic: (1) cât ocupă fiecare dosar mare din `C:\Kronos\` (lucru/, date de antrenare, puncte de salvare `.pt`, exporturi `.kgr`, cache-uri pip/HF)
  și cele mai mari 30 de fișiere; (2) **compară `Desktop\de sters\proiect\cyberspace_mutare_2026-10-10.zip` (25,6 GB, pachetul de mutare de pe laptopul ASUS)** cu ce există acum în
  `C:\Kronos\cyberspace` (listă de fișiere + SHA-256 pe cele mari): ce e DOAR în arhivă? (3) propune ce se poate șterge în siguranță (puncte de salvare vechi depășite, date
  intermediare care se pot regenera), cu GB eliberați, păstrând obligatoriu #459, #477, #513, `cod_c1/gpt.pt`, examenele, jurnalul, datele brute. Raport în `docs/rapoarte/`,
  rezumat în `plan/pentru_adrian.md`. **Nimic șters** — Adrian aprobă pe grupuri.
- stare: preluat (2026-11-05 13:45, supraveghetor) — **S79** în `plan/coada.md`, aprobat; după S78 (C-77 are prioritate); doar procesor și disc, nimic șters

