# S79 (C-76) — Raport de spațiu pe workstation + verificarea arhivei de mutare + propunere de curățenie

*Executantul, 6 noiembrie 2026, 03:11. Doar procesor și disc. **Nimic șters, mutat sau dezarhivat pe disc.***

## Pe scurt

- **Discul C:** 510,6 GB în total, **33,46 GB liberi** (la fel înainte și după — n-am scris nimic mare).
- **Arhiva de mutare `cyberspace_mutare_2026-10-10.zip` (26,20 GB) nu are nimic important în plus:** toate cele 218 fișiere de date din ea există pe disc, iar la cele mari (43 de fișiere, 28,05 GB) sumele SHA-256 sunt **identice, 0 diferențe**. Singurele lucruri care sunt doar în arhivă: un fișier text cu instrucțiuni (`CITESTE.txt`), lista pachetelor de pe laptop (`pip_freeze_laptop.txt`, 44 de rânduri) și un pachet git de 0,79 MB ale cărui commit-uri **există toate** în repo. → **Se poate șterge (26,20 GB).**
- **Ce se poate elibera, pe grupuri (Adrian alege):** până la **~166 GB** cu riscul cel mai mic (grupurile A–D de mai jos), încă ~55 GB din grupuri unde trebuie să decizi tu (E–H).
- **Atenție, o diferență față de comandă:** arhiva nu era în `Desktop\de sters\proiect\`, ci în **`Desktop\proiect\`** (dosarul `de sters` e gol). Am folosit-o de acolo, doar citire.

## 1. Cât ocupă fiecare dosar mare

**`C:\Kronos\` în total: 186,39 GB.** Pe dosare:

| Dosar | GB | Fișiere |
|---|---:|---:|
| `cyberspace\lucru\` | 115,27 | 6.226 |
| ↳ `lucru\stocare\modele\` (modelele salvate, 124 de fișiere `.pt`) | 49,05 | 124 |
| ↳ `lucru\cache\` (simboluri gata tăiate, 9 fișiere) | 11,05 | 9 |
| ↳ `lucru\kronos_cod\` (cod descărcat 4,73, simboluri 2,19, exerciții 2,02, restul ~1) | 9,96 | 676 |
| ↳ `lucru\e3\` (două indexuri sqlite: 1,21 + 1,04) | 2,31 | 39 |
| ↳ `lucru\w2_mare_24b\` (S77c) | 2,20 | 4 |
| ↳ `lucru\w2_mare\` (S77a, `gpt_24.pt` + altele) | 1,86 | 14 |
| ↳ 38 de dosare de linii cu câte un `gpt.pt` (0,39–1,33 GB fiecare) | ~38,6 | — |
| `cyberspace-cod\` (vechea școală de cod, octombrie; e un „worktree” git al ramurii `kronos-cod`) | 40,06 | 5.083 |
| `cyberspace\date\` (din care `date\ws\` 21,25; `tinystories_tot` 2,24) | 24,35 | 177 |
| `cyberspace\.venv\` | 3,61 | 32.495 |
| `arhiva\` (Mini Brain, S78) | 1,54 | 3.264 |
| `cyberspace\module\` | 1,52 | 259 |
| `cyberspace\.git\` | 0,01 | 299 |

Pe tipuri de fișiere în `C:\Kronos\`: `.pt` (modele) **114,27 GB** în 994 de fișiere; `.zip` 27,01 GB (înghețurile școlii vechi de cod); `.txt` 16,28; `.parquet` 7,73; `.jsonl` 6,23; `.bin` 4,18; `.sqlite` 4,13; `.kgr` (exporturi) 1,86.

**În afara `C:\Kronos\`:**

| Loc | GB |
|---|---:|
| `Desktop\test ai brain v13 clean` | 73,36 |
| `Desktop\proiect\` (doar arhiva de mutare) | 26,20 |
| `Desktop\test ai brain` | 4,71 |
| Cache Hugging Face `~\.cache\huggingface` | 26,21 |
| ↳ Qwen3-8B 16,40 · Qwen3-4B-Instruct 8,06 · opus-mt-en-ro 0,61 · gpt-neo-romanian-125m 0,60 · gpt2 0,55 | |
| Cache pip `AppData\Local\pip\Cache` | 4,08 |
| `AppData\Local\Temp` | 0,17 |
| Cache torch | nu există |

Ce am măsurat ajunge la ~321 GB; restul de ~156 GB ocupați pe C: sunt Windows, programele și alte dosare pe care C-76 nu le cere (nu le-am măsurat).

**Cele mai mari 30 de fișiere din `C:\Kronos\`** (GB):

| # | Fișier | GB |
|---:|---|---:|
| 1 | `cyberspace\date\ws\amestec\antrenare.txt` | 4,886 |
| 2 | `cyberspace\date\ws\brut\fineweb2_ro\...\000_00000.parquet` | 4,845 |
| 3 | `cyberspace\lucru\kronos_cod\complet\cod.jsonl` | 4,702 |
| 4 | `cyberspace\date\ws\curat\fabule_ro\antrenare.txt` | 3,524 |
| 5 | `cyberspace\date\ws\curat\fineweb2_ro\antrenare.txt` | 2,970 |
| 6 | `cyberspace\lucru\cache\simboluri_205dbb5f81d7f911.pt` | 2,707 |
| 7 | `cyberspace\lucru\cache\simboluri_be12c6d88276d79d.pt` | 2,682 |
| 8 | `cyberspace\lucru\cache\simboluri_7b6399781ae0ba22.pt` | 2,467 |
| 9 | `cyberspace\date\tinystories_tot\antrenare.txt` | 2,241 |
| 10 | `cyberspace\lucru\w2_mare_24b\gpt.pt` | 2,197 |
| 11 | `cyberspace\lucru\cache\simboluri_0b147aa558d5a2b7.pt` | 2,068 |
| 12 | `cyberspace-cod\lucru\cod_v03\inghet\v03_final.zip` | 1,621 |
| 13 | `cyberspace-cod\lucru\cod_v03\inghet\v03_inainte_de_pilot.zip` | 1,621 |
| 14 | `cyberspace-cod\lucru\cod_v02\inghet\v02_inainte_de_pilot.zip` | 1,621 |
| 15 | `cyberspace-cod\lucru\cod_v04\inghet\v04_inainte_de_pilot.zip` | 1,570 |
| 16 | `cyberspace-cod\lucru\cod_v04_noapte\inghet\v04n_inainte_de_pilot.zip` | 1,570 |
| 17 | `cyberspace\lucru\cod_c1_sc\gpt.pt` | 1,328 |
| 18 | `cyberspace\lucru\cod_c1_ex\gpt.pt` | 1,328 |
| 19 | `cyberspace\lucru\cod_c1\gpt.pt` | 1,328 |
| 20 | `cyberspace-cod\lucru\cod\inghet\inainte_de_pilot.zip` | 1,216 |
| 21 | `cyberspace\lucru\e3\index.sqlite` | 1,211 |
| 22 | `cyberspace-cod\lucru\cod_v04_noapte\inghet\v04n_D_0w_picat.zip` | 1,177 |
| 23 | `cyberspace-cod\lucru\cod_v04_noapte\inghet\v04n_D_0w_dupa_repornire.zip` | 1,177 |
| 24 | `cyberspace-cod\lucru\cod_v04_noapte\inghet\v04n_B_0w_picat.zip` | 1,177 |
| 25 | `cyberspace-cod\lucru\cod_v04\inghet\v04_D_0w_picat.zip` | 1,177 |
| 26 | `cyberspace-cod\lucru\cod_v04\inghet\v04_B_0w_picat.zip` | 1,177 |
| 27 | `cyberspace-cod\lucru\cod_v04_noapte\inghet\v04n_A_0w_picat.zip` | 1,177 |
| 28 | `cyberspace-cod\lucru\cod_v04\inghet\v04_D_0q.zip` | 1,177 |
| 29 | `cyberspace-cod\lucru\cod_v04\inghet\v04_B_0q.zip` | 1,177 |
| 30 | `cyberspace-cod\lucru\cod_v04\inghet\v04_D_0n.zip` | 1,177 |

Lista completă a celor 470 de fișiere peste 10 MB e în `lucru/cascada/S79_proba/rezultat.json` (cheia `fisiere_peste_10mb`; nu e în Git).

## 2. Arhiva de mutare comparată cu ce e pe disc

Arhiva: `C:\Users\Computer\Desktop\proiect\cyberspace_mutare_2026-10-10.zip`, 26,20 GB comprimată, 221 de fișiere, 28,14 GB necomprimat. Am citit-o direct din zip (nimic scos pe disc). Fiecare dosar de sus l-am comparat cu locul în care l-a pus mutarea (cum scrie în `CITESTE.txt` din arhivă):

| Din arhivă | Comparat cu | Fișiere | GB | Doar în arhivă | Mărime diferită | SHA-256 pe cele ≥ 50 MB |
|---|---|---:|---:|---:|---:|---|
| `cyberspace/` | `C:\Kronos\cyberspace` | 128 | 4,81 | **0** | 3 (vezi mai jos) | 12 egale (4,75 GB), 0 diferite |
| `cyberspace-cod/` | `C:\Kronos\cyberspace-cod` | 71 | 15,27 | **0** | 0 | 28 egale (15,26 GB), 0 diferite |
| `huggingface/` (Qwen3-4B) | `~\.cache\huggingface` | 19 | 8,06 | **0** | 0 | 3 egale (8,05 GB), 0 diferite |
| `git/cyberspace_toate_ramurile.bundle` | — | 1 | 0,0008 | 1 | — | — |
| `CITESTE.txt`, `pip_freeze_laptop.txt` | — | 2 | 0,00 | 2 | — | — |

Cele 3 fișiere cu mărime diferită sunt fișiere care **au crescut** de la mutare; am verificat că versiunea din arhivă e exact **începutul** celei de pe disc:
- `lucru/jurnal/experimente.jsonl`: arhiva 295 de rânduri, discul 522 — începutul identic ✓;
- `lucru/examen_sacru/rezultate.jsonl`: 7 rânduri în arhivă, 19 pe disc — începutul identic ✓;
- `lucru/amprente.json`: aceeași amprentă a examenului (`0ca9cf74…3028`) în ambele; pe disc s-a adăugat amprenta examenului de cod (alt sfârșit de rând, de aceea nu e „început” la octet).

Pachetul git din arhivă: are ramurile `master`, `kronos-cod`, `claude-cod`, `claude-continuum`, `claude-m1` și 16 tag-uri `cod/...`; **toate cele 9 commit-uri diferite spre care arată există în repo** (verificat cu `git cat-file`). Tag-urile `cod/...` ca nume nu le-am verificat (doar commit-urile lor, care există).

Verificarea mea inițială a avut o greșeală (compara totul cu `cyberspace\`, deci arăta 23,3 GB „doar în arhivă”); am refăcut comparația cu locurile corecte — cifrele de mai sus sunt cele refăcute (`lucru/cascada/S79_proba/zip2.json`).

**Concluzie:** arhiva e o copie a ce există deja. Dacă vrei să păstrezi ceva din ea, sunt doar `CITESTE.txt` și `pip_freeze_laptop.txt` (câțiva KB) — le pot scoate în `C:\Kronos\arhiva\mutare\` la „da”-ul tău.

## 3. Propunerea de curățenie (pe grupuri; nimic șters — tu alegi)

**Păstrate obligatoriu, în nicio propunere:** #459, #477, #513, `lucru/cod_c1/gpt.pt`, `lucru/w2_mare/` (S77a, inclusiv `gpt_24.pt`), examenele și seturile ascunse, jurnalul, datele brute (`date/ws/brut`, `lucru/kronos_cod/complet`), amprentele paznicului. Am mai păstrat din prudență: `lucru/w2_mare_24b/` și #517/#518 (S77d se compară cu ora 1 din S77c), `lucru/w2_romana_r1/` (linia lui #513), `lucru/w2_reteta_A_cont3/` (linia lui #477), `lucru/ws_w2/`, datele curățate și amestecul de antrenare.

### Risc mic

| Grup | Ce | GB | De ce e sigur |
|---|---|---:|---|
| **A** | `Desktop\test ai brain v13 clean` + `Desktop\test ai brain` | **78,07** | S78 le-a salvat: 1,54 GB în `C:\Kronos\arhiva\mini-brain\`, 0 diferențe SHA-256 („Mini Brain salvat — Adrian poate șterge ambele foldere”). |
| **B** | `Desktop\proiect\cyberspace_mutare_2026-10-10.zip` | **26,20** | Tot ce e în ea e pe disc, SHA-256 identic (secțiunea 2). |
| **C** | Modelele intermediare din `lucru\stocare\modele\` (orele din mijlocul fiecărei linii) — 82 de fișiere | **~33,0** | Rămâne ultimul model din fiecare linie + reperele. Lista mai jos. |
| **D** | `gpt.pt` din dosarele liniilor închise (starea de continuare a liniei; ultimul ei model rămâne în `stocare\modele`) — 28 de dosare | **~29,3** | O linie închisă nu se mai continuă; dacă trebuie, se pornește din model cu `--porneste-din`. Lista mai jos. |
| | **Total A–D** | **~166,6** | |

**Grupul C** — se șterg (păstrez ultimul din linie + #385, #415, #425, #438, #441, #489, #459, #477, #513):
- `ws_w1_repetitie` #297; `ws_w1` #303–#311 (9) → 10 × 354 MB = 3,54 GB;
- `ws_w2_proba` #298; `ws_w2_repetitie` #315; `ws_w2` #327, #328, #329, #330, #331, #333, #343, #345; `w2_conv` #394, #395; `w2_conv_text` #399, #400; `w2_conv_text_v2` #405, #406; `w2_conv_text_v3` #413, #414; `w2_conv_auto_v1` #423, #424; `w2_spec_f1/f2/f3` #427, #429, #431; `w2_conv_e3_memorie` #436, #437; `w2_muon_A` #440; `w2_muon_B` #442; `w2_reteta_C` #446; `w2_reteta_D` #450; `w2_reteta_A_cont` #454–#458; `w2_e3_reteta_A2` #464, #465; `w2_reteta_A_cont2` #469, #470; `w2_reteta_A_cont3` #472–#476; `w2_romana_r1` #509–#512 → 47 × 392 MB = 18,42 GB;
- `cod_c1` #480–#498 fără #489 (18); `cod_c1_ex` #500–#506 (7) → 25 × 443 MB = 11,08 GB.
- Rămân 42 de modele (~16 GB).

**Grupul D** — `gpt.pt` din: `w2_conv`, `w2_conv_auto_v1`, `w2_conv_e3_memorie`, `w2_conv_text`, `w2_conv_text_v2`, `w2_conv_text_v3`, `w2_e1_generator`, `w2_e3_reteta_A`, `w2_e3_reteta_A2`, `w2_e3_reteta_A_intrerupt_1028`, `w2_muon_A`, `w2_reteta_A_cont`, `w2_reteta_A_cont2`, `w2_reteta_C`, `w2_reteta_D`, `w2_spec_f1`, `w2_spec_f2`, `w2_spec_f3`, `ws_w2_proba`, `ws_w2_proba3`, `ws_w2_repetitie` (21 × 1,177 = 24,72 GB) + `w2_muon_B` 0,84, `ws_w1` 1,06, `ws_w1_repetitie` 1,06, `antrenare_lunga_7` 0,41, `antrenare_lunga_8` 0,41, `conv_fum` 0,39, `fapte_zero` 0,41 (4,57 GB) → **29,28 GB**.
Notă: `antrenare_lunga_7/8` și `fapte_zero` sunt și în arhiva de mutare; dacă ștergi și grupul B și grupul D, ele dispar de tot (ultimul lor model rămâne totuși în `stocare\modele`: #295, #286).

### Trebuie să decizi tu (risc mai mare sau folosite de unelte)

| Grup | Ce | GB | De ce nu e „sigur” |
|---|---|---:|---|
| **E** | `C:\Kronos\cyberspace-cod\lucru\` (școala veche de cod v01–v04, 9–16 oct, înghețuri `.zip`) | **~40,0** | Experiment încheiat, dar e singurul loc cu înghețurile v04 (24,7 GB). 15,3 GB din el sunt și în arhiva de mutare (B) — **dacă ștergi B, aici rămâne singura copie**. Dosarul e un „worktree” git: dacă îl ștergi întreg, trebuie și `git worktree prune`. |
| **F** | Cache Hugging Face: Qwen3-8B (16,40), Qwen3-4B (8,06), opus-mt-en-ro, gpt-neo-romanian, gpt2 (1,75) | **26,21** | Sunt folosite de unelte vechi (`module/profesor_qwen.py`, `unelte/genereaza_conversatie.py`, `compara_externe.py`, `traduce_conversatie.py`, `fapte_de_verificat.py`). Sarcinile recente nu folosesc alt AI; la nevoie se descarcă din nou (descărcare = aprobarea ta). |
| **G** | `lucru\cache\simboluri_*.pt` (9 fișiere, 12–15 oct) | **11,05** | Se refac singure la prima antrenare care le cere, dar asta ia timp la pornire. Nu știu care e folosit de liniile de acum (numele e un hash). |
| **H** | Cache pip | **4,08** | Se golește cu `pip cache purge`; costă doar o descărcare mai lungă la o reinstalare. |
| | `gpt.pt` din `cod_c1_ex` și `cod_c1_sc` (S70, S72b; ultimele modele #507, #508 rămân) | 2,66 | Liniile de cod sunt în pauză, nu închise oficial. |
| | **Total E–H** | **~84,0** | |

**Ce aș face eu întâi:** A + B (104 GB, fără nicio pierdere) — singure duc discul de la 33 la ~137 GB liberi și rezolvă testul care pică din cauza discului. C și D după aceea, când ești de acord cu listele.

## Testele

`CUDA_VISIBLE_DEVICES=-1 python -m pytest`: **1236 trec, 1 sărit, 2 pică**:
- `teste/test_kronos_cod_tokenizer.py::test_unealta_cap_coada_fara_excluse_si_fara_validare_la_antrenare` — **cunoscut**: cere 40 GB liberi pe C: (sunt 33,5). Pleacă după curățenie.
- `teste/test_interfata.py::test_cererile_gresite_sunt_refuzate_pe_inteles` — **instabil**: a picat o dată în rularea mare; rulat singur imediat după, tot fișierul trece (37/37). Același fel de cădere ca la S33 (`test_interfata`, eroare de conexiune). N-am schimbat nimic în cod la S79 (doar scripturi de măsurare în `lucru/`), deci nu vine de la mine; nu l-am reparat.

## Ce am rulat și cât a durat

Toate scripturile sunt în `lucru/cascada/S79_proba/` (în afara Git), doar citire:
- `s79.py` (prin cascadă, procesul 16724, cod 0, 42 s) → `rezultat.json` (mărimi, top 30, cache-uri, prima comparație — cea greșită la arhivă);
- `s79_zip2.py` (171 s) → `zip2.json` (comparația corectă, SHA-256 pe 43 de fișiere, 28,05 GB citiți din zip);
- `s79_verif3.py` → `verif3.json` (începuturile fișierelor crescute, commit-urile din pachetul git);
- `s79_detalii.py`, `s79_jurnal.py` → `detalii.json` (detalii pe dosare, modelele pe linii din jurnal, doar citit).
Total ~10 minute cu tot cu verificările. Spațiul liber: 33,46 GB înainte și după.

## Ce aștept de la tine

Spune ce grupuri se șterg (de exemplu „A, B da; C, D da; E–H nu”). Ștergerea o face omul sau o sarcină nouă aprobată de tine — executantul nu are voie să șteargă modele sau date fără „da”-ul tău. Dacă vrei, pune și unde să păstrez `CITESTE.txt` și `pip_freeze_laptop.txt` din arhivă înainte să o ștergi.
