# S95 — 5 ore din #536 cu rata ×0,5, judecat pe română: **LA FEL** (fără STRICĂ, fără „crește încă”)

*Scris de executant (cascada), 10 nov 2026 02:30, la prima trecere după ce lanțul s-a terminat (02:13:01, cod 0).*

## Pe scurt

- Modelul de 24 de straturi a mai învățat 5 ore din #536, cu rata la jumătate (5e-6) și răcirea la final. Toate 5 orele s-au terminat
  (#550–#554), examenele și nota R1 la fel. Nimic oprit, nimic anulat.
- **Română curat (scorul de decizie, C-88): S95 = 1,2040**, #513 = 1,2060, #536 = 1,2063 (re-măsurate în aceeași rulare).
- **Verdict strict după praguri: LA FEL** (−0,0020 față de #513; trebuia ≤ −0,005 pentru MAI BUN). Nu strică nimic. „Crește încă”:
  **NU** (−0,0023 față de #536; trebuia ≤ −0,003).
- E cel mai bun model la română măsurat până acum, dar diferența e sub pragul hotărât dinainte, deci **nu contează ca „mai bun”**.
  Modelul nou nu înlocuiește #513 nicăieri.
- De la Adrian: nimic de făcut acum.

## Ce a rulat

Lanțul `lucru/cascada/S95_proba/s95.py`, pornit prin cascadă la 20:38:43 (proces 19320), terminat 02:13:01, cod 0.

| pasul | de la | până la | cod |
|---|---|---|---|
| rata la pornire (copia #536 cu `minute = 0`) | 20:39:01 | 20:39:06 | 0 |
| română pe copie (procesor) | 20:39:06 | 20:40:50 | 0 |
| antrenarea, 5 ore (`antrenare_recalcul.py --config config/conv_w2_mare_24s.toml --ore 5`) | 20:40:50 | 02:03:33 | 0 |
| validări #554 / #513 / #536 (`examen_validari_ws.py`) | 02:03:33 | 02:04:25 | 0 |
| nota R1 (`romana_raspunsuri.py reper --experiment 554 --iesire lucru/romana_raspunsuri/reper_s95`) | 02:04:25 | 02:12:53 | 0 |

Verificările de pornire: copia SHA `838e0d52…0b6c`, #536 (`lucru/w2_mare_24g/gpt.pt`) `7e5f841d…3bd6`; singura cheie diferită
`minute` (`copie.json`, din 20:30). Rata socotită pe copie: 5e-6 la primul pas / la 10 min / la sfârșitul orei 1 ✓. Română pe copie
**1,2062** (= #536 1,2063 ± 0,001 ✓). C: 55,9 GB liberi.

Diff-ul configurării (`config/conv_w2_mare_24r.toml` → `config/conv_w2_mare_24s.toml`, deja în commit 3e7c723): doar antetul,
`nume = "w2_mare_24s"`, `cale_stare = "lucru/w2_mare_24s/gpt.pt"`, `rata_invatare` 0.00001 → **0.000005** și eticheta.

## Tabelul pe ore

| ora | exp. | română curat | pași | pași total | simboluri (oră) | rata la sfârșit | memorie rezervată | vârf placă (paza) |
|---|---|---|---|---|---|---|---|---|
| 1 | #550 | 1,2065 | 23.207 | 138.978 | 47,5 M | 5e-6 | 5.180 MB | 5.890 MB |
| 2 | #551 | 1,2062 | 23.161 | 162.139 | 47,4 M | 5e-6 | 5.200 MB | 6.462 MB |
| 3 | #552 | 1,2062 | 23.144 | 185.283 | 47,4 M | 5e-6 | 5.220 MB | 6.490 MB |
| 4 | #553 | 1,2056 | 23.126 | 208.409 | 47,4 M | 4e-6 | 5.220 MB | 6.490 MB |
| 5 | #554 | **1,2040** | 23.079 | 231.488 | 47,3 M | 0 | 5.220 MB | 6.470 MB |

- Rata efectivă (citită din starea optimizatorului la fiecare salvare): 5e-6 / 5e-6 / 5e-6 / 4e-6 / 0 — exact programul.
- 6,4 pași/s în fiecare oră; 237 M simboluri văzute în total (0,18 treceri prin text).
- `val_bpb` pe povești pe fiecare oră nu-l dă unealta (examenul de decizie e acum româna); povești doar la final, mai jos.
- Placa: vârf total **6.496 MB** (în pornirea validărilor, 02:03:30), sub 6.700 / 7.000; **max 62 °C**; 3.779 citiri nvidia-smi la 5 s.
  După golire, între ore, ~3.758 MB (nu crește de la o oră la alta).

## Validările, una lângă alta (re-măsurate în aceeași rulare)

| validarea | S95 (#554) | #513 | #536 |
|---|---|---|---|
| **română curat (decide)** | **1,2040** | 1,2060 | 1,2063 |
| română wikipedia curat | 1,0100 | 1,0115 | 1,0120 |
| română web curat | 1,2987 | 1,3008 | 1,3013 |
| română cărți curat | 1,3381 | 1,3408 | 1,3403 |
| povești (R2) | 0,4039 | 0,4049 | 0,4052 |
| cod curat | 0,7228 | 0,7247 | 0,7243 |
| traducere curat | 0,7040 | 0,7039 | 0,7062 |
| română (necurat) | 1,2217 | 1,2237 | 1,2238 |
| cod (necurat) | 0,6567 | 0,6590 | 0,6582 |

#513 re-măsurat = 1,2060, identic cu reperul (pragurile rămân 1,2010 / 1,2110).

**R1** (#554, 500 de întrebări din setul ascuns, 8 min, placa max 2.110 MB / 63 °C): toate **99,53**; instrucțiuni **99,20**
(#513: 98,97); felurile vechi **100,0** (#513: 99,68). Cele mai slabe feluri: `instr_numar` 97,5, `instr_nume` 98,33.

## Verdictul (strict după pragurile pre-înregistrate)

- Română 1,2040: nu e ≤ 1,2010 (MAI BUN), nu e ≥ 1,2110 (MAI SLAB) → **LA FEL**.
- STRICĂ: povești 0,4039 ≤ 0,4100 ✓; cod curat 0,7228 ≤ 0,7297 ✓; R1 instrucțiuni 99,20 ≥ 90 ✓; felurile vechi 100 ≥ 98 ✓ → **nu**.
- „Crește încă” (≤ 1,2033): 1,2040 → **nu**.

Față de așteptările scrise înainte: ghicisem 1,2058 (interval 1,2040–1,2075) → a ieșit la capătul bun. LA FEL (88 % ghicit) — confirmat;
„crește încă” (20 %) — nu. Orele 1–3 cu rată constantă au ținut modelul pe loc, iar câștigul a venit iar la răcire (orele 4–5: −0,0022),
ca la S89. Pre-înregistrarea e închisă, cu „Ce a ieșit” și „Verdictul”: `docs/preinregistrari/2026-11-09_w2_mare_24s.md`.

## „Eroarea după examen” (nota supraveghetorului din 8 nov)

A apărut **la fiecare oră (#550–#554)**, ca la S89 și S94b:

- Unde: în orchestrator, pasul 8, `Orchestrator._dupa_examen` → `model.dupa_examen(...)` (`kronos/orchestrator.py:295–303`), adică
  DUPĂ ce modelul a fost examinat și decizia luată. Eroarea e prinsă acolo și scrisă în fișă ca `eroare_dupa_examen`.
- Ce: `OutOfMemoryError: CUDA out of memory. Tried to allocate 46–58 MiB … 5.66 GiB allowed; 5.47–5.53 GiB allocated by PyTorch`
  — adică plafonul PyTorch (5.800 MB) e atins; nvidia-smi arăta atunci ~6.460–6.496 MB.
- Modelul (`lucru/stocare/modele/experiment_550…554.pt`) și nota fiecărei ore **există** → toate orele contează normal (nu e anulare).
- Nu am reparat nimic (locul e în `kronos/` și în modulul modelului). Variante propuse:
  (a) în modulul modelului (`dupa_examen` moștenit de `model_gpt_conversatie_muon`; definit în `module/model_plasa_mare.py:522`
  și înrudite — de verificat care e cel chemat): `gc.collect()` + `torch.cuda.empty_cache()` la începutul lui
  `dupa_examen`, ca paza dinaintea testului rapid; (b) `dupa_examen` să ruleze pe procesor (sau să fie sărit) pentru modelele mari,
  când nu folosește rezultatul — trebuie văzut întâi ce face acolo modelul cu conversație.

## Siguranța

- SHA-256 înainte = după: #513 (`experiment_513.pt` `605c4084…8b2c`), #536 (`experiment_536.pt` `f484e022…bd5a12`,
  `w2_mare_24g/gpt.pt` `7e5f841d…3bd6`), `gpt_24.pt` `d35e3dbe…92cc` ✓. `lucru/cache`: lista fișierelor (mărime + dată) înainte = după ✓.
- Nimic descărcat, instalat sau șters; `kronos/`, `module/`, examenele, paznicul, jurnalul — neatinse (jurnalul doar prin platformă).
- Fișier rămas: `lucru/w2_mare_24s/ruleaza.lock` (gol, din unealta de antrenare; nu l-am șters).

## Testele

`CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -m pytest -q`: **1343 trec, 1 sărit** (5 min 41 s).

## Ce urmează (scris dinainte de supraveghetor)

„LA FEL fără «crește încă» → curba e plată la rata asta; următoarea idee e mai multe date pe noapte (C-85 pasul 5, date pe bucăți,
S98) sau Muon ca rețetă.” Hotărârea e a supraveghetorului. Observația mea: și la S89 și la S95 câștigul vine aproape tot din răcire;
orele cu rată constantă țin modelul pe loc.

S95 în coadă: `gata`.
