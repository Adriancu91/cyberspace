# Pre-înregistrare: S87: crește memoria plăcii de la o oră la alta?

<!-- scrisa: 2026-11-07T08:31:18 -->
*Scrisă la 2026-11-07 08:31, înainte de rulare. După ce rularea a început, textul de mai jos nu se mai schimbă; la închidere
se adaugă doar secțiunea „Ce a ieșit” (python unelte/preinregistrare.py --inchide memorie_ore).*

## Întrebarea

Când „orele” se fac în aceeași ordine ca în `kronos/orchestrator.py` (test rapid → antrenare → validare, cu `model_test`
ținut în memorie tot timpul orei), crește memoria ținută pe placă de la o oră la alta (cum sugerează căderile S77c și S85
de la testul rapid al orei 3) și o oprește o golire `gc.collect()` + `torch.cuda.empty_cache()` la începutul fiecărei ore?

## Ce rulează

- Sarcina S87 din plan/coada.md (aprobată de supraveghetor 7 nov 05:15, în cadrul C-85 pasul 2 aprobat de Adrian 6 nov
  17:56), pornită de executant prin cascadă în ziua de 7 nov, după 08:30 (Adrian inactiv la workstation de ~11 ore).
- Unealta `unelte/masoara_memorie_mare.py ore` (comanda nouă; refuză a doua oară dacă există `lucru/memorie_ore/s87.json`).
  Modelul de 24 de straturi construit ca în S86 (`unelte/antrenare_recalcul.py`: recalcul pe straturi, plafon PyTorch
  5.800 MB), setările din `config/conv_w2_mare_24f.toml`, varianta (b) Muon lot 4 × 24, din COPII ale
  `lucru/w2_mare/gpt_24.pt` în `lucru/memorie_ore/<varianta>/` (originalul doar citit; SHA-256 înainte și după).
- O „oră” = o funcție, exact în ordinea orchestratorului: `model_test` nou → test rapid (`antreneaza(date, 2)` +
  `biti_pentru` pe 500 de caractere) → `model` nou → antrenare (50 de pași de optimizator, ca în S86) → validare
  (`ExamenBpb().examineaza`, doar chemat, + `dupa_examen`), cu `model_test` încă ținut. Nimic nu se șterge explicit; la
  ieșirea din funcție variabilele se eliberează singure (ca la ieșirea din experimentul orchestratorului).
- Trei variante, fiecare în proces nou, câte 3 ore: (b_orch) fără golire; (b_orch_gc) cu `gc.collect()` +
  `empty_cache()` la începutul fiecărei ore; (b_orch_del) ca (b_orch_gc) plus `del model_test` + `gc.collect()` +
  `empty_cache()` înainte de construirea lui `model` (doar informativ; în orchestratorul real ar cere o schimbare în
  `kronos/`, deci „da”-ul lui Adrian).
- Se scrie `memory_allocated`, `memory_reserved`, nvidia-smi la începutul fiecărei ore (și după golire, la variantele cu
  golire) și înainte/după/vârf pe fiecare fază. Procesul părinte oprește copilul peste 7.000 MB sau la 83 °C; copilul se
  oprește la out of memory (se notează ora și faza). Nimic în jurnal, niciun model păstrat în afara copiilor.
- Durata estimată (din S86: test rapid ~25 s, antrenare ~215 s, validare ~178 s pe oră): ~22 min pe variantă, ~70 min
  pe placă în total.

## Așteptările, în cifre

- „Creșterea” = `memory_allocated` la începutul orei 3 minus la începutul orei 1, la intrarea în oră (pentru variantele
  cu golire: valoarea de după golirea de la începutul orei; la (b_orch) e chiar valoarea de început). Ora 1 începe de la
  ~0 MB (nimic încărcat pe placă înainte).
- Repere din S86 (ordinea inversă, (b), ora 1): antrenare vârf 3.057 MB PyTorch, validare vârf 5.444 MB (nvidia-smi
  6.373), test rapid vârf 3.066 MB; după antrenare modelul ține ~2.204 MB. În proba S86 de la 03:05 vârful la antrenare
  a urcat 2.289 → 4.390 MB de la ora 1 la ora 2, apoi out of memory la validarea orei 2.
- Mă aștept la **P1 = DA**: ceva rămâne ținut de la o oră la alta (proba S86 o arată), deci creșterea la (b_orch)
  ≥ 300 MB sau (b_orch) cade înainte de sfârșitul orei 3. Mă aștept ca vârful nvidia-smi la validare să fie ~6.300–6.500
  MB la ora 1 (aproape de pragul de 6.700).
- La **P2** nu am o așteptare sigură: dacă ce rămâne ținut e un ciclu de referințe, `gc.collect()` îl eliberează (P2 = DA);
  dacă e ținut de o referință vie (de ex. un registru global, cârligul de recalcul, `ExamenBpb`), nu (P2 = NU).

## Pragurile (scrise de supraveghetor în coadă la S87, DA/NU)

- **P1 „memoria crește”:** la (b_orch), creșterea ≥ **300 MB**, sau (b_orch) cade cu out of memory / trece de 6.700 MB
  nvidia-smi înainte de sfârșitul orei 3 → DA; altfel NU.
- **P2 „golirea ajută”:** (b_orch_gc) termină toate 3 orele, cu vârful nvidia-smi ≤ **6.600 MB** și creșterea sub
  **100 MB** → DA; altfel NU.
- Informativ (fără prag): cât scad vârfurile la antrenare și la validare la (b_orch_del) față de (b_orch_gc).
- După verdict (din coadă): P2 = DA → `gc.collect()` înaintea lui `empty_cache()` în paza din
  `unelte/antrenare_recalcul.py`, cu test; P2 = NU și (b_orch_del) trece → nimic schimbat, propunerea pentru
  `kronos/orchestrator.py` în raport; niciuna nu trece → ce se vede + 1–2 variante.

## Ce ar infirma așteptările

- P1 = NU: la (b_orch) alocatul la începutul orei 3 e sub cel de la ora 1 + 300 MB și toate 3 orele trec sub 6.700 MB →
  memoria nu crește în ordinea orchestratorului; căderile S77c/S85 ar avea altă cauză (de ex. vârful din validare cu
  examenele suplimentare, sau fragmentarea, nu memoria ținută).
- P2 = NU cu (b_orch_gc) căzută: golirea de la începutul orei nu e de ajuns; ce ține memoria e o referință vie.

## Ce a ieșit

*Adăugat la 2026-11-07 10:04, din jurnalul Kronos (lucru/jurnal/experimente.jsonl) și din jurnalul CONTINUUM pe bune. Verdictul se scrie dedesubt.*

Niciun experiment Kronos în perioada asta.

Niciun ciclu CONTINUUM pe bune în perioada asta.

Cifrele măsurării (`lucru/memorie_ore/s87.json`, rularea 08:46:45–09:50:36, cod 0; adăugate de executant la 10:04):

- `memory_allocated` la intrarea în oră (după golire, la variantele cu golire): (b_orch) 0 → 1.341 → **1.355 MB**
  (creștere 1.355 MB); (b_orch_gc) 0 → 16 → **16 MB** (înainte de golire 1.343 / 1.346); (b_orch_del) 0 → 16 → 16 MB.
- (b_orch) a căzut cu **out of memory la ora 3, în antrenare** (PyTorch a cerut încă 64 MiB), după vârful 3.949 MB
  PyTorch; vârful nvidia-smi 6.439 MB. Exact locul căderilor S77c/S85 (ora 3).
- (b_orch_gc) a terminat toate 3 orele; vârful nvidia-smi **6.399 MB** (la validare, orele 2–3).
- (b_orch_del) a terminat toate 3 orele; vârful nvidia-smi 6.441 MB.
- Placa: maxim 62 °C. SHA-256 `gpt_24.pt` înainte = după (`d35e3dbe…92cc`).

## Verdictul

*Scris de executant la 2026-11-07 10:04, strict după pragurile de mai sus.*

- **P1 „memoria crește”: DA** — creșterea la (b_orch) e 1.355 MB ≥ 300 MB, iar (b_orch) a căzut cu out of memory
  înainte de sfârșitul orei 3.
- **P2 „golirea ajută”: DA** — (b_orch_gc) a terminat toate 3 orele, vârful nvidia-smi 6.399 MB ≤ 6.600 MB, creșterea
  16 MB < 100 MB.
- Informativ, (b_orch_del) față de (b_orch_gc) la orele 2–3: vârful la antrenare scade 4.378 → 3.050 MB PyTorch
  (nvidia-smi 5.577 → 4.201), dar vârful la validare nu scade (5.509 → 5.454 / 5.477 PyTorch; nvidia-smi 6.399 →
  6.415 / 6.441). Deci `del model_test` nu mută vârful total, care e la validare.
- Ambele așteptări (P1 = DA, vârful validării ~6.300–6.500 MB) s-au confirmat; la P2 nu aveam o așteptare sigură — a ieșit
  că memoria rămasă e ținută de cicluri de obiecte (pe care le eliberează `gc.collect()`), nu de o referință vie.
