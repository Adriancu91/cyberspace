# Mutarea pe workstation (RTX 3070 8 GB, 128 GB RAM)

*Pachetul de mutare din planul joi–sâmbătă (faza 3b). Cuprinde doar planuri și liste; nu s-a descărcat nimic mare.
Ciornă scrisă joi, 8 octombrie, după-amiază, pe procesor, cât placa era a antrenării 7. Se completează vineri, iar
modelele nopților 1–2 se adaugă sâmbătă dimineață.*

## 1. Pe scurt

- **Ce câștigăm:**
  - 8 GB de memorie video în loc de 6, deci modele de 3–5 ori mai mari decât cel de acum (34 de milioane de
    parametri);
  - placa e cam de 1,6–2 ori mai rapidă (de măsurat în prima oră);
  - 128 GB RAM: tot TinyStories, plus textul în română, încap în memorie.
- **Ce rămâne la fel:** codul, examenele, jurnalele, regulile (`kronos/` neatins, examenul neatins, pre-înregistrare
  înainte de fiecare noapte).
- **Ce se schimbă:**
  - limitele paznicului (memoria video: 7 GB în loc de 5,5);
  - configurările noi pentru modelele mai mari;
  - un tokenizer nou (engleză + română + cod, cu numerele întregi) pentru linia nouă, care pornește de la zero;
  - ferestrele lui CONTINUUM, dacă workstation-ul e doar al lui Kronos.
- **Ordinea:** copiere (secțiunea 2) → mediul Python (secțiunea 3) → prima oră de verificări (secțiunea 7) → probele de
  memorie (secțiunea 4) → prima noapte pe workstation, cu pre-înregistrare.

## 2. Ce se copiază (cu mărimi)

| Ce | Unde e acum | Mărime | Cum |
|---|---|---|---|
| Depozitul, cu toate ramurile (main, kronos-cod, claude-cod, claude-continuum, claude-m1) | GitHub | ~1 MB | `git clone`, apoi `git fetch --all` |
| Tag-urile școlii (`cod/…`, 9 acum, toate locale) | doar pe laptop | — | înainte de mutare: `git push origin --tags` |
| Modelul #252 (punctul de plecare al școlii și al faptelor) | `lucru/stocare/modele/experiment_252.pt` + `.json` | 129 MB | copiere |
| Modelul #257 (cel mai bun pe povești) | `lucru/stocare/modele/experiment_257.pt` + `.json` | 129 MB | copiere |
| Modelul #262 (din care a pornit antrenarea 7) | `lucru/stocare/modele/experiment_262.pt` + `.json` | 129 MB | copiere |
| Cel mai bun model al nopților 1–2 | *(se completează sâmbătă)* | ~129 MB | copiere |
| Starea liniilor lungi (`gpt.pt` + `pornire.json`), pentru reluare | `lucru/antrenare_lunga_7/`, `_8/`, `fapte_zero/` | ~390 MB fiecare | copiere (doar ultimele) |
| Jurnalul Kronos | `lucru/jurnal/` | 0,9 MB | copiere (niciodată editat) |
| Jurnalele CONTINUUM | `lucru/continuum/`, `lucru/continuum_pe_bune/` | ~1 MB | copiere |
| Examenele date (fapte, sacru, profesor) | `lucru/examen_fapte_nou/`, `examen_sacru/`, `examen_fapte/`, `profesor/` | ~2,5 MB | copiere |
| Școala de cod: jurnale, stări, biblioteci | `cyberspace-cod/lucru/cod*/` (fără `inghet/`) | câțiva MB | copiere |
| Școala de cod: înghețurile | `cyberspace-cod/lucru/cod/inghet/` (v0.1), `cod_v02/inghet/`, `cod_v03/inghet/` | 3,7 GB + 4,2 GB + (v0.3) | copiere; sau doar cele de la începutul pilotului și cele finale |
| Faptele și hrana | `date/fapte/` (fapte.json, examen_nou.json, examen_sacru.json, povesti.txt, toate.jsonl, info.json; plus fapte_gresite.json, dacă există) | 14 MB | copiere |
| Școala: abecedarul și setul sacru | `date/cod/` | 12 KB | vin cu depozitul (sacru.json e adăugat cu `-f`) |
| Tokenizer-ul de acum | `date/tinystories/bpe_4096.json` | 48 KB | copiere |
| Validarea oficială (examenul) | `date/tinystories_r2/validare.txt` | parte din 175 MB | **copiere obligatorie**: aceiași octeți, ca val_bpb să rămână comparabil |
| Profesorul (Qwen3-4B-Instruct-2507) | `%USERPROFILE%\.cache\huggingface\hub\models--Qwen--Qwen3-4B-Instruct-2507` | 7,6 GB | copiere (la fel de mare ca descărcarea, dar fără rețea) |

**Fără înghețurile școlii:** cam 1,5 GB. **Cu ele:** cam 10 GB. **Cu profesorul:** cam 17 GB. Încape pe un stick USB 3
de 32 GB.

**Ce nu se copiază** (experimente vechi, de arhivat pe un disc extern, dacă vrea Adrian):
- `lucru/stocare/modele/`: 45 GB, 158 de fișiere, mai ales modelele mari m3 de 1,3 GB; se copiază doar cele din tabel;
- `lucru/bucla/` (7,9 GB), `lucru/m3_mare/` (6,3 GB), `lucru/bucla_cinstita/` (2 GB);
- `lucru/teste_tmp/`.

## 3. Ce se regenerează (și ce e mai ieftin)

| Ce | Mărime | Copiere | Regenerare | Alegerea |
|---|---|---|---|---|
| Textul TinyStories întreg (`date/tinystories_tot`) | 2,1 GB | ~1 minut pe USB 3 | descărcare de ~2 GB de pe Hugging Face | copiere |
| `date/tinystories_r2` (antrenare + validare R2) | 175 MB | secunde | — | copiere (validarea trebuie să fie identică) |
| Simbolurile gata împărțite (`lucru/cache`) | 2,5 GB | ~1 minut | singură, la prima antrenare (tokenizer-ul pe 2,2 GB de text, zeci de minute pe procesor, de măsurat) | regenerare; verifică și drumul datelor |
| Rafturile TinyStories (`lucru/rafturi_tinystories*.json`) | 0,2 MB | secunde | singure | copiere |
| Hrana (`date/fapte/povesti.txt`, 7.520 de povești) | 14 MB | secunde | ore de profesor pe placă | **copiere** (și comparația cu nopțile de pe laptop cere aceeași hrană) |
| Mediul Python (`.venv`) | ~5 GB | nu (căile din .venv sunt ale laptopului) | `pip install` cu versiunile de mai jos (PyTorch cu CUDA e ~2,5 GB) | regenerare |

**Versiunile de pe laptop** (de pus într-un `requirements.txt` la mutare): Python 3.12.10, torch 2.14.1+cu132 (CUDA
13.2), torchvision 0.29.1+cu132, transformers 5.18.0, tokenizers 0.23.2, accelerate 1.15.0, bitsandbytes 0.50.2,
safetensors 0.8.0, huggingface_hub 1.33.0, numpy 2.5.2, pytest 9.1.1. Lista completă: `pip freeze`, 44 de pachete.

## 4. Configurările pentru RTX 3070 8 GB

**Cum am estimat memoria video.** Formula e calibrată pe antrenarea 7 de pe laptop: 33.753.088 de parametri, lot 24 ×
context 256, 10 straturi × 512, vocabular 4.096, bf16, AdamW. Acolo a măsurat 2.030 MB, plus ~350 MB contextul CUDA,
adică 2.375 MB în `nvidia-smi`, cât arată formula:

> memoria ≈ 0,35 GB + 16 octeți × parametri + 39 octeți × (lot × context × straturi × emb) + 10 octeți × (lot × context × vocabular)

La fiecare cifră se adaugă ~10% pentru fragmentare. Ținta e sub 7 GB, ca să rămână ~1 GB pentru Windows.

| Nume | Straturi × emb (capete) | Context | Lot | Vocabular | Parametri | Memorie estimată (+10%) | Simboluri pe pas | Rata (de la zero) |
|---|---|---|---|---|---|---|---|---|
| **W1** (continuitate) | 12 × 768 (12) | 256 | 24 | 4.096 (tokenizer-ul de acum) | 88,4 M | 4,2 GB (4,6) | 6.144 | 0,0006 → 0,00006 |
| **W2** (principal) | 12 × 768 (12) | 512 | 12 | 16.384 (tokenizer nou) | 98,0 M | 5,1 GB (5,6) | 6.144 | 0,0006 → 0,00006 |
| **W3** (mai adânc) | 16 × 768 (12) | 512 | 8 | 16.384 | 126,4 M | 5,0 GB (5,5) | 4.096 | 0,0005 → 0,00005 |

- **Viteza** (estimare, de măsurat): acum, 7,5 pași pe secundă × 6.144 ≈ 46.000 de simboluri pe secundă. Pe 3070,
  cu parametrii de 2,6–3,7 ori mai mulți:
  - W1: ~110 milioane de simboluri pe oră;
  - W2: ~95 milioane pe oră;
  - W3: ~80 milioane pe oră.
  O noapte de 10 ore înseamnă ~1 miliard de simboluri, adică ~2 treceri prin TinyStories.
- **Orele pe noapte:**
  - 19:00–07:30 lasă 10 ore de antrenare cu examenele orare (val_bpb, fapte, fapte noi, nota profesorului pe 40 de
    povești);
  - dimineața, înainte de 07:30, rămâne timp pentru raport.
- **Alegerea:** prima oră pe workstation rulează câte 5 minute din fiecare și notează memoria (`memorie_gpu_max_mb` în
  jurnal) și pașii pe secundă. Linia nouă pornește cu W2. Dacă W2 trece de 6,5 GB în realitate, lotul scade la 8.
- **Paznicul** (în fiecare configurare nouă, nu în `kronos/`):
  - `memorie_gpu_max_mb = 7000` (pe laptop, 5500);
  - `temperatura_gpu_max = 83`: 3070 își reduce singură viteza pe la 83 °C; pe laptop limita era 85;
  - `timp_max_secunde` rămâne 4500 (o oră + examenele).
  - Regula din CLAUDE.md, „memoria video sub ~5,5 GB”, devine „sub ~7 GB” doar cu acordul lui Adrian.

## 5. Tokenizer nou (plan; linia nouă pornește de la zero pe workstation)

**De ce:**
- tokenizer-ul de acum (BPE 4.096, învățat pe TinyStories în engleză) taie orice număr în cifre: „46” = două bucăți.
  Școala de cod v0.1–v0.2 s-a rupt chiar la numere;
- nu știe româna: „ăâîșț” și cuvintele românești s-ar tăia în bucăți foarte mici.

**Propunerea:**
- **Mărimea:** 16.384 de simboluri (W2/W3). Încorporările lor sunt ~12,6 M parametri, adică 13% din W2.
- **Numerele:**
  - toate numerele 0–999 sunt simboluri întregi (cele 1.000 de numere se pun în vocabular de la început);
  - numerele mai lungi se taie în grupe de cel mult 3 cifre, de la stânga (ca la tokenizer-ele mari de azi);
  - „46” e o bucată; „1234” = „123” + „4”.
- **Româna:**
  - ș/ț cu virgulă; ş/ţ cu sedilă se transformă înainte de antrenare, pentru că amândouă apar în textele din internet;
  - diacriticele rămân (nu se scot).
- **Textul de învățare a tokenizer-ului** (~1–2 GB, eșantion):
  - ~45% engleză simplă (TinyStories);
  - ~35% română (sursele din secțiunea 6);
  - ~15% cod Python cu licență permisivă;
  - ~5% numere și calcule scrise în text.
- **Unealta:** `tokenizers` de la Hugging Face (instalat deja, 0.23.2), cu antrenorul BPE pe octeți. E rapid pe 128 GB
  RAM.
- **Comparabilitatea:**
  - val_bpb e în biți pe octet, deci nu depinde de tokenizer: linia nouă se compară direct cu cea veche;
  - examenele de fapte sunt pe text, deci merg la fel;
  - școala de cod trebuie doar să-și refacă împărțirea în simboluri.
- **Liniile:**
  - linia veche (34 M, BPE 4.096) rămâne ca reper; W1 o poate continua pe workstation, pe același tokenizer;
  - linia nouă (W2, tokenizer nou) pornește de la zero, cu fapte (5%) de la început, ca fapte-zero.

## 6. Surse de date în română și pentru traducere (licențe verificate)

*(Se completează: lista cu licențele verificate pe paginile oficiale.)*

## 7. Ce depinde de Windows și de laptop, și ce rulează în prima oră

**Codul care depinde de Windows** (are ramuri pentru alte sisteme sau valori implicite):
- `module/continuum/observa.py`: `GetLastInputInfo`, „când a atins omul ultima dată tastatura”. Pe alt sistem sau
  într-un proces fără ecran întoarce „nu se știe” (None).
- `unelte/antrenare_lunga.py`: `SetThreadExecutionState`, ca laptopul să nu adoarmă în timpul antrenării.
- `cyberspace-cod/module/cod/paznic_cod.py`: `GetSystemPowerStatus` (bateria). Pe un desktop fără baterie răspunde
  „pe priză” sau „nu se știe”. În ambele cazuri școala merge mai departe, fără să aștepte încărcătorul.
- `cyberspace-cod/module/cod/sandbox.py`: `SYSTEMROOT` în mediul proceselor sandbox-ului (cerut de Windows).
- `nvidia-smi`: `kronos/paznic.py`, `module/continuum/observa.py`, `unelte/lant_antrenare.py`, `paznic_cod.py`,
  `unelte/verifica_mediu.py`. Merge oriunde e instalat driverul NVIDIA.
- Alimentarea verificată din evenimentele Kernel-Power (PowerShell) e un pas manual al lui Claude Code, nu cod. Pe
  desktop rămâne doar „e în priză / UPS”.

**Testele care depind de temperatura plăcii** (configurarea `config/proba.toml` are limita 85 °C):
- `test_cap_coada`, `test_criterii`, `test_criteriu_principal`, `test_examene_suplimentare`, `test_porneste_din`;
- pe laptop, cu placa fierbinte (peste 85 °C, în timpul unei antrenări), dau 0 experimente;
- pe workstation se rulează cu placa liberă, ca acum.

**Prima oră pe workstation (lista de verificat):**
1. `python unelte/verifica_mediu.py`: driverul, CUDA, PyTorch, placa.
2. `python -m pytest` în ambele foldere (main și `cyberspace-cod`): toate trebuie să treacă. Se notează numărul
   (pe laptop, joi: 490 + 602, fără cele 5 de mai sus).
3. **Amprenta examenului.** Dacă paznicul spune că `module/examen_bpb.py` s-a schimbat, poate fi doar din cauza
   capetelor de rând (CRLF) la `git clone`.
   - Se verifică întâi `git diff` (trebuie să fie gol).
   - Abia apoi Adrian aprobă: `python -m kronos aproba-examen --config …`.
   - La fel pentru amprentele școlii: `python unelte/scoala_cod.py --aproba-amprente --motiv "mutare pe workstation"`.
4. **Reproducerea unei cifre:** val_bpb oficial și `python unelte/examen_fapte_nou.py --experiment 262` pe #262.
   Trebuie să iasă 0,4304 și 59 de fapte noi (± zgomotul plăcii). Asta dovedește că mutarea e fidelă.
5. Probele de memorie W1/W2/W3, câte 5 minute (secțiunea 4).
6. Simbolurile lui TinyStories (`lucru/cache`) se regenerează la prima probă; se notează cât durează.

## 8. CONTINUUM pe workstation

- **Ferestrele:**
  - dacă workstation-ul e doar al lui Kronos, învățarea poate fi toată ziua (`"00:00-23:59"`, ca pe 7 octombrie);
  - dacă școala de cod rulează ziua, rămâne împărțirea de acum (nopțile linia principală, zilele școala);
  - o singură sarcină grea pe placă odată rămâne regula.
- **`memorie_video_libera_min_mb = 4500`** (cât cere profesorul) rămâne. Pe 8 GB, placa liberă are ~7,5 GB.
- **`temperatura_max`:** 83 (ca paznicul de pe workstation).
- **`buget_ore_placa_pe_zi = 20`** rămâne. Desktop-ul se răcește mai bine, dar 4 ore de odihnă pe zi nu strică.
- **`[linii] configurari`** primește configurările noi (`config/ws_*.toml`), iar `[nevoi.continua] configurari` lista
  albă a nopții, ca acum.
- **`minute_fara_om`:** dacă nimeni nu lucrează pe workstation, rămâne fără efect. Dacă Adrian îl folosește ziua,
  rămâne 10.
- **Căile** sunt relative, deci nu se schimbă nimic.

## 9. Ce decide Adrian

1. Regula din CLAUDE.md pentru memoria video: 5,5 GB → 7 GB pe workstation.
2. Configurarea liniei noi (W2 propus), după probele din prima oră.
3. Ferestrele: workstation doar pentru Kronos, sau școala ziua și linia principală noaptea, ca acum.
