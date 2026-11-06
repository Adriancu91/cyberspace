# S77c — prima noapte a lui Kronos de 24 de straturi: OPRIT după ora 2 (memorie plină la ora 3)

*Scris de executant (cascada), 6 nov 2026 01:59. Pre-înregistrarea: `docs/preinregistrari/2026-11-05_w2_mare_24b.md` (închisă).*

## Pe scurt

- Antrenarea a mers **2 ore din 5**. La începutul orei 3 (01:43), testul rapid al lui Kronos a dat **CUDA out of memory**
  (PyTorch ținea 5,56 GiB din 5,66 GiB permise de plafonul de 5.800 MB și a cerut încă 18 MiB). Experimentul #519 a fost
  anulat; unealta a ieșit totuși cu cod 0, iar lanțul a făcut examenele pe **#518 (ora 2)**.
- **Verdictul: NEMĂSURAT** — pragurile erau pentru modelul de la ora 5, care nu există.
- Informativ, pe #518 (ora 2): română curat **1,2268** (mai rău decât #513 1,2060 și decât pornirea 1,2096), cod curat **0,7413**,
  R2 **0,4155** — după aceleași praguri ar fi fost **STRICĂ** (cod și R2). R1 a rămas foarte bun (instrucțiuni 99,20, vechi 100).
- Curba e **plată**: 0,4154 (ora 1) → 0,4155 (ora 2). Modelul mare, în 2 ore, a dat înapoi față de punctul de pornire (#477).
- Sarcina e pusă **`oprit`**. Nimic repornit.
- Testele: **1 picat** (1237 trec) — din cauza discului C: plin (34 GB liberi, sub pragul de 40 GB), nu din cauza S77c.

## Ce a rulat

Lanțul `lucru/cascada/S77c_proba/s77c.py`, pornit prin cascadă la 5 nov 23:30:50 (proces 13488), încheiat la 6 nov 01:52:29 (cod 0).

| pas | început | sfârșit | cod |
|---|---|---|---|
| verificări + scorul de pornire (procesor) | 23:30:58 | 23:32:37 | 0 |
| antrenare `antrenare_recalcul.py --config config/conv_w2_mare_24b.toml --ore 5` | 23:32:37 | 01:43:17 | 0 (dar ora 3 anulată) |
| validări linia `w2_mare_24b` (= #518) | 01:43:17 | 01:43:39 | 0 |
| validări #477 | 01:43:39 | 01:43:52 | 0 |
| validări #513 | 01:43:52 | 01:44:04 | 0 |
| nota R1 (`romana_raspunsuri.py reper --experiment 518`) | 01:44:04 | 01:52:26 | 0 |

Verificările de la pasul 0 au trecut: `lucru/w2_mare_24b/` nu exista; `gpt_24.pt` SHA `d35e3dbe…92cc`, copia identică; perechile
S76a neschimbate; scorul de pornire pe copie **1,2096** = #477 (diferență 0,0). În log: rețeta **24×768** și „Recalculul activărilor:
24 straturi împachetate” — ambele prezente.

## Cifrele

### Antrenarea

| ora | experiment | val_bpb (R2) | pași (lot 6) | simboluri văzute | memorie PyTorch |
|---|---|---|---|---|---|
| 1 | #517 | 0,4154 | 18.475 (5,1/s) | 57 M | 5.738 MB |
| 2 | #518 | 0,4155 | 18.447 (5,1/s) | 113 M total | 4.708 MB |
| 3 | #519 | — | — | — | **anulat: out of memory la testul rapid** |

- Pași/s: 5,1 loturi de 6 pe secundă ≈ **2,55 loturi de 12/s**, față de **2,80** la S77a (măsurat cu lot 12) → ~9 % mai lent.
- Simboluri: 113 M în 2 ore, față de **707 M** la #513 în 5 ore (16 %).
- Placa (nvidia-smi, din paza lanțului): vârf în primele 15 minute **6.391 MB**, vârf total **6.433 MB** (sub 6.700 și 7.000), **64 °C** max.
  Paza n-a apăsat oprirea. Căderea n-a venit de la paznic, ci de la plafonul PyTorch de 5.800 MB din `antrenare_recalcul.py`.
- Eroarea exactă: „Tried to allocate 18.00 MiB … 5.66 GiB allowed; 5.56 GiB is allocated by PyTorch, and 88.76 MiB is reserved
  by PyTorch but unallocated” — adică memoria s-a umplut până la plafon între ora 2 și testul rapid al orei 3 (la ora 1 PyTorch
  avea 5.738 MB, aproape de plafon).

### Examenele (re-măsurate în aceeași rulare)

| măsura | #518 (S77c, ora 2) | #513 | #477 |
|---|---|---|---|
| română curat (bpb) | **1,2268** | 1,2060 | 1,2097 |
| cod curat (bpb) | **0,7413** | 0,7247 | 0,7270 |
| R2 (val_bpb, jurnal) | **0,4155** | 0,4050 | 0,4060 |
| R1 instrucțiuni | 99,20 | 98,97 (S76b) | — |
| R1 felurile vechi | 100,0 | 99,68 (S76b) | — |
| R1 total | 99,53 | — | — |

Română pe surse, #518 vs #513: Wikipedia curat 1,0342 vs 1,0115; web curat 1,3207 vs 1,3008; cărți curat 1,3602 vs 1,3408.
Fișierele: `lucru/examen_validari_ws/experiment_518_20261106_014339.json`, `..._477_20261106_014351.json`, `..._513_20261106_014404.json`;
nota R1 în `lucru/romana_raspunsuri/reper_s77c/`.

SHA-256 înainte = după pentru #477 (`ae3d9046…`), #513 (`605c4084…`) și `gpt_24.pt` (`d35e3dbe…`): neschimbate.

## Verdictul (după pragurile pre-înregistrării)

**NEMĂSURAT.** Pragurile (MAI BUN / LA FEL / MAI SLAB / STRICĂ) sunt scrise pentru „ultimul model al liniei `w2_mare_24b` (ora 5)”.
Antrenarea s-a oprit după ora 2, deci modelul de comparat nu există.

Informativ (nu e verdictul): aplicate pe #518, pragurile dau **STRICĂ** — cod curat 0,7413 > 0,7320 și R2 0,4155 > 0,4110 — iar
română 1,2268 > 1,2110 ar fi MAI SLAB. Ce se vede, cinstit: în 2 ore, modelul mare a pierdut din ce știa #477 (română 1,2096 → 1,2268)
și curba nu coboară încă (0,4154 → 0,4155). Pre-înregistrarea avertiza că prima oră poate fi mai rea decât #477 și că o noapte scurtă
nu spune dacă mărimea ajută; cu 2 ore, nu putem spune nici atât.

## Ce a mers prost și de ce

1. **Memoria:** cu lot 6 × 16, PyTorch a stat la ~5,7 GB în ora 1 — aproape de plafonul de 5.800 MB. La trecerea spre ora 3 (când
   Kronos rulează testul rapid, cu modelul încărcat din nou) n-au mai încăput 18 MiB. Cauza probabilă: memorie rămasă ocupată de la
   ora anterioară sau fragmentare (PyTorch însuși sugerează `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`). Nu am verificat asta —
   e o ipoteză.
2. **Unealta a ieșit cu cod 0** deși ora 3 a fost anulată, iar lanțul a mers mai departe la examene. Lanțul se oprea doar la cod ≠ 0.
   Nu am reparat nimic.
3. Pre-înregistrarea permitea o reluare cu `lot = 4 × 24` (`w2_mare_24c`) **doar dacă** căderea era „în primele minute” și reluarea
   putea porni până la 01:00. Nu e cazul (căderea la 01:43, după 2 ore) → **nu am repornit nimic**.
4. În `lucru/w2_mare_24b/` a rămas `ruleaza.lock`. Nu l-am atins (ca la S45).

## Testele

`CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -m pytest`: **1 picat, 1237 trec, 1 sărit** (303 s).

Picat: `teste/test_kronos_cod_tokenizer.py::test_unealta_cap_coada_fara_excluse_si_fara_validare_la_antrenare` (pică și singur).
Cauza găsită: `tokenizeaza` se oprește când discul are sub `SPATIU_MINIM_GB = 40` GB liberi, iar **C: are acum doar 34 GB liberi**
(476 GB, 443 GB ocupați, 94 %; la 31 oct erau 59 GB). Testul cere `terminat` → pică. Nu e de la S77c (n-am schimbat cod) și **nu
l-am reparat** și nu am șters nimic. **Pentru Adrian:** discul C: se umple — trebuie decis ce se mută sau se șterge (S79 are
propunerea de curățenie); până atunci testul acesta va pica, iar uneltele cu prag de 40 GB se vor opri singure.

## Ce urmează / ce aștept de la Adrian (prin supraveghetor)

S77c e `oprit`. Variante, de ales de supraveghetor/Adrian:
- **(a)** O nouă noapte pe 24 de straturi, cu memorie mai multă de rezervă: `lot = 4`, `adunare_loturi = 24` (tot 96) și/sau
  `expandable_segments:True` — linie nouă, pre-înregistrare nouă, pornire de la #518 sau din nou de la `gpt_24.pt`.
- **(b)** Să ne uităm întâi la curbă: după 2 ore modelul mare e mai rău decât #477 și nu coboară. Poate rata 5e-5 constantă e prea
  mică/mare pentru straturile noi — de verificat înainte de o altă noapte întreagă.
Și: unealta `antrenare_recalcul.py` ar trebui să iasă cu cod ≠ 0 când o oră e anulată (altfel lanțurile merg mai departe pe un model
neașteptat). Schimbarea o aprobă supraveghetorul.

Placa e liberă. Următoarele din coadă: S78/S79 (procesor + disc), S76c (6 nov de la 08:00) — le ia cascada la trecerile următoare,
după regulile lor.
