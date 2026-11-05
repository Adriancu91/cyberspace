# S77a — Kronos crescut din #477 în adâncime: aceeași ieșire + memoria și viteza pe placă

Executant, 5 nov 2026, 17:52. Sarcina S77a (C-64 R2 pasul 1; aprobată de supraveghetor 07:40, fereastra mutată la 17:15).
Am pornit-o imediat după S80 (cascada deblocată). Fără antrenare; nimic din măsurători nu e păstrat ca model.

**Verdict: GATA** — ieșirea e identică (diferența 0, nu doar sub prag) la pașii 2 și 5, iar regula alege **N = 24 cu recalcul**.

## Ce am făcut

1. **Unealta nouă `unelte/creste_model.py`** (commit 2a15d6d) cu comenzile `creste`, `identic`, `masoara`
   (+ `masoara-unul`, procesul de măsurare), `romana`, `kgr`; teste noi în `teste/test_creste_model.py` (7).
   - Straturile noi se împrăștie uniform: după stratul vechi j vin ⌊(j+1)k/12⌋ − ⌊jk/12⌋ straturi noi (la 24: câte unul după
     fiecare; la 30/36/42: 1–2 / 2 / 2–3 după fiecare, nu la capăt).
   - Fiecare strat nou = copia stratului vechi de dedesubt (ln1, `atentie.in_proj`, ln2, `mlp[0]`), cu `atentie.out_proj` și
     `mlp[2]` (greutăți și bias) = 0.
   - Fișierul ieșit are forma lui `cale_stare` (exact ca starea de pornire a lui `antrenare_lunga.py --porneste-din`):
     `setari` (n_straturi = N), `retea`, un AdamW **gol** (starea optimizatorului nu se copiază), `pasi_total = 0`,
     `minute = 0.0`, `scor` = al sursei (0,4060).
   - Se încarcă de `module.model_muon:ModelGPTConversatieMuon` cu `n_straturi = N` și restul setărilor ca la S51, **fără
     nicio schimbare în `module/`** (verificat în test: `_pregateste_reteaua()` pornește din fișier, `continuat = True`).
   - **Numărătoarea pașilor la încărcare:** `pasi_total = 0` și `minute = 0` → la noapte încălzirea ratei se face din nou
     (primele `incalzire_pasi = 100` de loturi), iar `durata_scaderii_secunde` / `racire_finala` se socotesc de la 0, ca la
     orice `--porneste-din`. (Dacă am fi păstrat pașii lui #477 — 137.824 și 360 minute — încălzirea s-ar fi sărit, iar cu
     `racire_finala = 0.25` și progresul > 1 rata ar fi fost 0 de la început.) Optimizatorul pornește gol, deci AdamW își
     face din nou mediile (primele zeci de pași sunt mai „zgomotoși”).
   - Sursa: `lucru/w2_reteta_A_cont3/gpt.pt` = #477 (am verificat: aceleași greutăți ca `experiment_477.pt`, diferența 0).
2. **`unelte/exporta_greutati.py`**: opțiunea nouă `--gpt <fișier gpt.pt>` (alternativă la `--experiment`; implicitul
   neschimbat).

## Pasul 2 — aceeași ieșire (procesor, fp32)

`creste_model.py identic --straturi 24 30 36 42` (față de #477), pe cele 3 texte KGR1 și pe primele 20 de paragrafe din
validarea `romana_wikipedia_curat` (tăiate la 512 simboluri; 2.950 de poziții):

| N | dif. max. logit (KGR1) | argmax identic (KGR1) | dif. max. logit (20 paragrafe) | argmax identic (20 paragrafe) |
|---|---|---|---|---|
| 24 | 0,0 | 100 % (17/17) | 0,0 | 100 % (2.950/2.950) |
| 30 | 0,0 | 100 % | 0,0 | 100 % |
| 36 | 0,0 | 100 % | 0,0 | 100 % |
| 42 | 0,0 | 100 % | 0,0 | 100 % |

Pragul era ≤ 1e-4 și 100 %: **trece la toate**. Diferența e exact 0 pentru că straturile noi adună zerouri adevărate
(0 × greutate + bias 0) la fluxul rezidual.

**Română curat pe un fișier** (`creste_model.py romana`, echivalentul `examen_validari_ws.py` pe primele 100.000 de litere,
procesor fp32):

| model | wikipedia curat | web curat | cărți curat | **română curat** |
|---|---|---|---|---|
| #477 (12 straturi, re-măsurat la fel) | 1,0151 | 1,3044 | 1,3442 | **1,2096** |
| crescut N = 24 (`gpt_24.pt`) | 1,0151 | 1,3044 | 1,3442 | **1,2096** |

Față de reperul 1,2097: −0,0001, în toleranța ±0,0005 (diferența de 0,0001 vine de la procesor fp32 față de placa bf16 a
reperului; #477 re-măsurat pe procesor dă tot 1,2096).

## Pasul 3 — memoria și viteza pe placă

`creste_model.py masoara --straturi 12 24 30 36 42` (pornit prin cascadă la 17:41:56, încheiat 17:46:14, cod 0; ~4,5 minute
de placă). Pasul adevărat al clasei (`ModelGPTConversatieMuon._pas`: AdamW, bf16 prin `_autocast`, `adunare_loturi = 8`),
lot 12, context 512, 60 de loturi, viteza pe ultimele 40. Textul: primii 4 MB din amestecul S51
(`date/ws/amestec/antrenare.txt`, 990.455 simboluri; fără partea de conversație — viteza nu depinde de text). Fiecare
măsurare într-un proces nou; o pază proprie citește `nvidia-smi` la 0,5 s și oprește măsurarea peste 7.000 MB sau la 83 °C.

| N | parametri | recalcul | vârf `nvidia-smi` (MB) | torch max rezervat (MB) | pași/s | °C max | rezultat |
|---|---|---|---|---|---|---|---|
| 12 (#477) | 98,0 M | nu | 6.158 | 5.308 | **6,45** | 42 | ok |
| 24 | 183,1 M | nu | 7.234 | — | — | 34 | oprită de pază / out of memory |
| 24 | 183,1 M | **da** | **6.010** | 5.160 | **2,80** | 51 | ok |
| 30 | 225,6 M | nu | 7.328 | — | — | 40 | oprită / out of memory |
| 30 | 225,6 M | da | 6.874 | 6.024 | 2,27 | 56 | ok, dar > 6.500 MB |
| 36 | 268,1 M* | nu | 7.418 | — | — | 43 | oprită / out of memory |
| 36 | 268,1 M* | da | 7.090 | — | — | 54 | oprită / out of memory |
| 42 | 310,6 M* | nu | 7.440 | — | — | 44 | oprită / out of memory |
| 42 | 310,6 M* | da | 7.324 | — | — | 54 | oprită / out of memory |

\* parametrii la 36/42 sunt calculați (n-au ajuns să fie scriși de proces): +7.087.872 pe strat.

- **La N = 12: 6,45 pași/s**, ca în logul S76b (6,4 pași/s) — se numără la fel (loturi pe secundă).
- Vârful `nvidia-smi` include ~650 MB ținuți de Windows și ecran (placa avea 643–879 MB ocupați înainte).
- **Atenție, de știut:** la cele 6 măsurători care n-au încăput, `nvidia-smi` a urcat scurt (sub o secundă, până la oprire)
  la **7.090–7.440 MB**, peste pragul de 7.000 MB. Am pus PyTorch-ului o limită de ~6,6 GB (`set_per_process_memory_fraction`),
  dar contextul CUDA și memoria Windows vin peste ea. Fiecare măsurare a fost oprită (de paza mea sau de „out of memory”) și
  am trecut la următoarea, cum scrie în sarcină; temperatura n-a trecut de 56 °C. Pentru altă dată: limita PyTorch trebuie
  pusă la ~5,9 GB ca vârful total să rămână sub 7.000 MB.
- Recalculul (`torch.utils.checkpoint` pus din afară în jurul fiecărui strat) taie vârful la 24 de straturi de la > 7.234 la
  6.010 MB, cu prețul vitezei: 2,80 pași/s (≈ 43 % din 6,45, pentru dublul straturilor).

## Pasul 4 — alegerea (regula scrisă înainte)

Cel mai mare N din {24, 30, 36, 42} cu vârful `nvidia-smi` ≤ 6.500 MB și ≥ 2,0 pași/s:
- 42, 36: nu încap nici cu recalcul;
- 30 cu recalcul: 2,27 pași/s, dar 6.874 MB > 6.500 → nu;
- **24 cu recalcul: 6.010 MB și 2,80 pași/s → ALES.** (24 fără recalcul nu încape.)

**Ce înseamnă pentru o noapte de 6 ore:** 2,80 × 21.600 s ≈ **60.500 de loturi** (≈ 7.560 de pași ai optimizatorului cu
adunare 8) ≈ 60.500 × 12 × 512 ≈ **372 milioane de simboluri**, față de ~138.000 de loturi (~850 M simboluri) la 12 straturi
(S51: 137.824 de pași în 6 ore). Pentru noapte, recalculul trebuie să fie în clasa modelului (o setare opțională, cu
implicitul neschimbat) — asta o scrie supraveghetorul la S77b, cum spune sarcina; eu n-am atins `module/`.

## Pasul 5 — modelul pentru noapte și verificarea KGR1

- `creste_model.py creste --straturi 24 --iesire lucru/w2_mare/gpt_24.pt` → 183.086.592 parametri,
  SHA-256 `d35e3dbee4a27e01f5f3a2d877a146dff9d61f967719011a1b1f724f169392cc` (rămâne pentru S77b; alături `gpt_24.json`
  cu planul straturilor).
- Exporturi KGR1 **F32** (doar în `lucru/w2_mare/`, nu în Git, nu trimise nicăieri; pachetul KGR1 al OS rămâne pe #477):
  - `kronos_477_f32.kgr` (392.352.544 o, SHA-256 `de998412…1d83`) din `--experiment 477`;
  - `kronos_s77a_24_f32.kgr` (732.579.104 o, SHA-256 `58994c7c…7c28`) din `--gpt lucru/w2_mare/gpt_24.pt`.
- `creste_model.py kgr` (motorul fără PyTorch, aceeași funcție ca `vectori_kgr1.py`) și `vectori_kgr1.py model --kgr …` pe
  ambele:

| text | greedy 5 (#477) | greedy 5 (crescut 24) | identic | dif. max. logit ultima poziție |
|---|---|---|---|---|
| „Ana are mere.” | „ Acum are 1192” | „ Acum are 1192” | da | 0,0 |
| „Capitala României este” | „ orașul Bacău,” | „ orașul Bacău,” | da | 0,0 |
| „def suma(a, b):” | „\n    return a * b” | „\n    return a * b” | da | 0,0 |

Pragul (identic + ≤ 1e-3): **trece**.

## Ce n-am atins

`kronos/`, `module/`, examenul, paznicul, jurnalul, `config/`, linia `cod_c1*`, setul ascuns, ramura `limba-romana`.
SHA-256 înainte = după (`lucru/cascada/S77a_proba/sha_inainte.json` / `sha_dupa.json`):
`gpt.pt` (S51) c672705e…b49f, #477 ae3d9046…2a3f, #459 f28f1c79…14aa, #513 605c4084…8b2c. Nimic descărcat, nimic instalat.
Nimic din `lucru/` în Git. Interfața, KGR1-ul OS-ului și `integrare/kronos/MODEL.md` rămân pe #477.

## Testele

`CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -m pytest -o addopts="" -q` → **1232 trec, 1 sărit** (4 min 59 s;
înainte de S77a: 1225 + cele 7 noi din `teste/test_creste_model.py`: planul uniform, forme și zerouri, aceleași logit-uri
2 → 4 straturi ≤ 1e-5, `creste` scrie starea de pornire și refuză să scrie peste, clasa S51 încarcă fișierul fără schimbări,
exportul KGR1 `--gpt`, regula de alegere).

## Fișierele

`lucru/w2_mare/`: `masoara.json` (toate măsurătorile + „ales”), `masoara_*.json`, `identic.json`, `romana_24.json`,
`romana_477.json`, `gpt_24.pt` + `.json`, `kronos_477_f32.kgr`, `kronos_s77a_24_f32.kgr`, `kgr_24.json`, `vectori_477.json`,
`vectori_24.json`. Jurnalul măsurării: `lucru/cascada/S77a.log`.

## Ce urmează

S77b (prima noapte a modelului crescut din `lucru/w2_mare/gpt_24.pt`, linie nouă `w2_mare_24`) o scrie supraveghetorul;
are nevoie de recalcul în clasa modelului (setare opțională) ca să încapă. Eu trec la S78 → S79 (procesor și disc).
De la Adrian nu aștept nimic pentru S77a.
