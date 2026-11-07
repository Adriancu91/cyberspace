# S91 — Cercetătorul cu model „trimis în avans” (C-85 pasul 4, partea a) — 7 nov 2026, 14:40

**Stare: `gata`.** Executantul din cascadă, rularea de la 14:28. Totul pe procesor (`CUDA_VISIBLE_DEVICES=-1`), fără placă,
fără antrenare reală, fără modelele #459/#477/#513/`gpt_24.pt`. Aprobat de Adrian (COMENZI.md C-85 pasul 4, 6 nov 17:56);
pașii scriși de supraveghetor 7 nov 14:15.

## Pe scurt (pentru Adrian)

- Unealta nouă `unelte/cercetator_avans.py` încearcă rețete pe un **model mic**, face clasamentul și scrie **o singură
  propunere** pentru modelul mare. Propunerea **nu se rulează** — pe placă merge doar printr-o sarcină separată, cu
  pre-înregistrare.
- `kronos/` **nu a trebuit schimbat**: unealta folosește platforma așa cum e (Orchestrator, Registru, Jurnal, paznicul).
- 12 teste noi; **toate cele 1318 teste trec, 1 sărit, 0 picate.**
- Rularea demonstrativă (GPT minuscul, 5 încercări × 1 minut, 5 min 20 s) a mers cap-coadă.
- **Lecție importantă pentru partea b:** unealta mută acum pe modelul mare valorile *exacte* găsite pe cel mic. În demonstrație
  a ieșit rata 0,003 — pe modelul mare (rata lui e 0,00001) asta ar fi de 300 de ori prea mult. Rata bună a unui model
  minuscul nu e rata bună a unuia mare. De aceea propun ca partea b să mute **schimbări relative** (de ex. „rata × 2”), nu
  valori, și să măsoare întâi dacă clasamentul mic prezice clasamentul mare (mai jos).

## 1. Ce am citit (doar citit)

- `kronos/orchestrator.py`: cercetătorul primește istoricul liniei și setările curente și dă o propunere; orchestratorul o
  trece prin cele 8 stări (verificat → aplicat → test rapid → antrenat → examinat → decis → înregistrat), cu paznicul la
  propunere, la examen (amprenta) și la consum. `ruleaza(n)` face întâi „punctul de plecare” pe o linie nouă, apoi n propuneri.
- `kronos/config.py`, `kronos/paznic.py`, `kronos/jurnal.py`: dosarul de lucru vine din configurare (`director_lucru`) —
  jurnalul, amprentele examenelor și butonul STOP stau acolo. Asta permite unei unelte să ruleze platforma într-un dosar
  separat fără nicio schimbare în nucleu.
- `unelte/antrenare_lunga.py`, `unelte/antrenare_recalcul.py`: pornesc antrenările lungi pe ore, tot prin Orchestrator.
  Unealta nouă nu le folosește (încercările mici sunt experimente obișnuite ale platformei, de câteva minute).

## 2. Unealta `unelte/cercetator_avans.py`

```
python -X utf8 unelte/cercetator_avans.py --config-mic <mic.toml> --config-mare <mare.toml> \
    --incercari N --minute-pe-incercare M --iesire <dosar> [--procesor] [--porneste]
```

- **Implicit e proba** (`--proba`): arată ce ar face și verifică setările; nu antrenează și nu scrie nimic (nici dosarul).
- **Înainte de orice antrenare** verifică spațiul cercetătorului din configurarea mică: fiecare setare pe care o poate
  schimba trebuie să aibă sens pe modelul mare. Refuză cu mesaj clar (cod 2):
  - setările de mărime/identitate a modelului (`n_straturi`, `n_capete`, `n_emb`, `context`, `tokenizer`, `cale_stare`…);
  - setările care nu există în aceeași secțiune a configurării mari;
  - `--minute-pe-incercare` peste limita de timp a paznicului din configurarea mică;
  - un model mic cu `cale_stare` în afara dosarului de ieșire (încercările ar putea scrie peste el) sau cu `porneste_din`.
- **Cu `--porneste`:** rulează platforma pe configurarea mică (punctul de plecare + N − 1 propuneri ale cercetătorului din
  ea, de ex. `cercetator_local`), fiecare cu M minute de antrenare și notată cu examenul din configurarea mică. Tot ce scrie
  platforma (jurnalul mic, amprentele, modelele păstrate, cache-ul) merge în `<iesire>/`, **nimic în `lucru/` în afara lui**
  și **nimic în jurnalul mare**. Amprentele examenelor aprobate se copiază din dosarul de lucru al configurării mici, ca un
  examen schimbat să fie refuzat de paznic și aici.
- Scrie `clasament.json` + `clasament.md` (rețeta = schimbările față de configurarea mică, scorul, decizia lui Kronos,
  timpul de antrenare și total, amprenta modelului de pornire: SHA-256 al `cale_stare` sau „de la zero”), apoi
  `propunere_mare.toml` = configurarea mare **copiată literă cu literă**, cu doar valorile câștigătorului înlocuite (+ un
  antet de 4 rânduri de comentariu „NU a fost rulată”) și `propunere_mare.diff`. Înainte să scrie, citește propunerea înapoi
  și verifică că e identică cu configurarea mare + schimbările; altfel refuză.
- Câștigătorul = cel mai bun scor (după `mai_mic_e_mai_bun` al examenului), nu decizia „păstrat” a lui Kronos.
- Refuză să scrie peste o rulare veche (`clasament.json` existent).
- Nu importă nimic din `module/` (modulele vin doar prin configurare/registru).

Fișiere noi: `unelte/cercetator_avans.py`, `teste/test_cercetator_avans.py`, `config/avans_proba_mic.toml` (configurarea
modelului minuscul din demonstrație). Nimic schimbat în `kronos/`, `module/`, configurările existente, paznic, jurnal.

## 3. Testele (`teste/test_cercetator_avans.py`, 12 teste, ~5 s)

Pe modele minuscule (n-gram pe 300 de propoziții), în dosare temporare:

| test | ce verifică |
|---|---|
| proba | nu antrenează și nu creează nimic (nici `iesire/`, nici `lucru/`) |
| N încercări | 5 încercări → 5 rânduri, nicio rețetă repetată, câștigătorul = scorul minim, `propunere_mare.toml` = configurarea mare + doar setările câștigătorului (citit cu tomllib), diff-ul = o singură linie de setări schimbată |
| nimic în `lucru/` | după rulare există doar `iesire/`; a doua rulare în același dosar e refuzată |
| amprentele | o amprentă de examen diferită, copiată din `lucru/amprente.json` → paznicul anulează încercările → refuz, nicio propunere |
| setări fără sens (3) | `n_emb` → refuz „mărimea”; `lot` (lipsește la cel mare) → refuz; alt port permis → acceptat; `main` dă cod 2 și nu scrie nimic |
| minute / `cale_stare` | M peste paznic → refuz; `cale_stare = lucru/w2_mare/gpt_24.pt` → refuz |
| direcția scorului | `mai_mic_e_mai_bun` adevărat/fals schimbă câștigătorul; încercările anulate merg la coadă; rețetă repetată → refuz |
| înlocuirea în TOML | în tabelul pe un rând și în secțiunea `[porturi.X.setari]`; cheie inexistentă → refuz |
| linia mare reală | pe `config/conv_w2_mare_24f.toml` (doar citit): rata + încălzirea schimbă exact o linie; `n_straturi` → refuz |
| importuri | unealta nu importă din `module/` |

**Toate testele:** `CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -m pytest` → **1318 trec, 1 sărit, 0 picate** (5 min 51 s).

## 4. Rularea demonstrativă (procesor)

```
python -X utf8 unelte/cercetator_avans.py --config-mic config/avans_proba_mic.toml \
    --config-mare config/conv_w2_mare_24f.toml --incercari 5 --minute-pe-incercare 1 \
    --iesire lucru/avans/s91_demo --procesor --porneste
```

Modelul mic: GPT 2 straturi × 64, context 64, pe Shakespeare, de la zero, doar procesor. Cercetătorul `cercetator_local`
(în ordine, fără amestec) pe `rata_invatare ∈ {0,003; 0,0003}` și `incalzire_pasi ∈ {10; 400}` — setări care există și pe
linia mare. Configurarea mare `conv_w2_mare_24f.toml` a fost **doar citită**. Cod 0, **320 s** în total (5 × ~63 s).

| loc | # | rețeta (schimbări față de configurarea mică) | val_bpb | decizia Kronos | antrenare (s) |
|---|---|---|---|---|---|
| 1 | 5 | rata 0,003, încălzire 400 | **2,6091** | păstrat | 60,3 |
| 2 | 3 | rata 0,003, încălzire 10 | 2,6117 | păstrat | 60,3 |
| 3 | 2 | rata 0,003 | 2,6285 | păstrat | 60,3 |
| 4 | 1 | punctul de plecare (rata 0,001, încălzire 100) | 2,7320 | păstrat | 60,3 |
| 5 | 4 | rata 0,0003, încălzire 10 | 3,1361 | respins | 60,3 |

Propunerea scrisă (`lucru/avans/s91_demo/propunere_mare.toml`, NU rulată): pe linia mare, doar
`rata_invatare 0.00001 → 0.003` și `incalzire_pasi 1000 → 400`; restul fișierului identic (diff-ul: 4 rânduri de antet +
o singură linie de setări schimbată).

**Cum se citește:** unealta funcționează (clasament, câștigător, propunere curată). Dar propunerea în sine **nu ar trebui
rulată**: rata găsită pe un model de 2 straturi × 64, antrenat 1 minut de la zero, e de 300 de ori rata liniei mari. Asta
e partea de demonstrație, nu o recomandare.

## 5. Planul pentru partea b (doar propunere; sarcină separată, cu pre-înregistrare)

**Modelul trimis în avans.**
- Pentru linia de 24 de straturi (`gpt_24.pt`, 24 × 768): o copie de **6 straturi × 768** din aceleași date, cu același
  tokenizer și aceeași rețetă — de preferat **tăiată** din `gpt_24.pt` (primele 6 blocuri + încorporările + capul), ca să
  pornească din aceleași greutăți; altfel 6 × 768 de la zero. Pentru #513 (linia de 12 straturi): la fel, 3–4 straturi
  × 768 tăiate din #513. Nu le creez acum.
- Pentru siguranța modelelor: modelul mic se copiază în dosarul de ieșire (`cale_stare` acolo), cum cere deja unealta.

**Mutarea relativă, nu absolută (schimbare propusă la unealtă).** Spațiul cercetătorului pe modelul mic ar fi în factori
față de rețeta liniei mari (rata × {0,5; 2; 4}, încălzire × {0,5; 2}), iar propunerea mare = rețeta mare × factorul
câștigător. Setările fără scară (optimizatorul, `racire_finala`) se mută ca valori. Asta e o schimbare mică în unealtă,
cu teste, în aceeași sarcină b.

**Câte încercări încap.** Modelul mare face o încercare pe oră (S77a/S85: ~5–6 pași/s). Unul de 6 straturi e ~3–4× mai
rapid → o încercare comparabilă (aceleași simboluri văzute) ≈ **15–20 min**. Într-o fereastră de zi de ~8 ore: **~20–24
încercări mici** (fără examenele lungi), față de ~7 pe modelul mare.

**Testul care arată dacă metoda merge.** Aceleași **5 rețete** (punctul de plecare + 4 schimbări relative) rulate pe:
- modelul mic: 5 × ~20 min (o zi, ~2 ore);
- modelul mare: 5 × 1 oră din același punct (o noapte, cu paza de memorie din S87).
Apoi **corelația de rang Spearman (ρ)** între cele două clasamente (pe val_bpb sau pe română curat — se alege în
pre-înregistrare, unul singur). Praguri propuse:
- **ρ ≥ 0,7 = DA** (metoda prezice; cu 5 rețete, o pereche vecină inversată dă 0,9, două dau 0,8, iar o rețetă mutată
  peste două locuri dă 0,6) **și** câștigătorul
  mic e în primele 2 pe modelul mare;
- **ρ ≤ 0,3 = NU** (modelul mic nu spune nimic despre cel mare);
- între ele = NECLAR (atunci 5 rețete noi, nu altă interpretare).
Atenție de scris în pre-înregistrare: cu doar 5 puncte, ρ e zgomotos (pragul 0,6 din coadă ar lăsa să treacă și o
rețetă mutată peste două locuri) — de aceea propun 0,7; diferențele mai mici decât zgomotul de la o rulare la alta (~0,002 la română) se
socotesc egalitate.

## 6. Ce n-am atins

`kronos/`, `module/examen_bpb.py`, `module/examen_romana.py`, paznicul, jurnalul mare, configurările existente, modelele
#459/#477/#513/`gpt_24.pt`, `lucru/w2_mare_24*/`. Nimic descărcat, instalat sau șters. Nimic din `lucru/` în Git. Placa
nu a fost folosită (450 MB / 25 °C la pornire).

## Ce aștept de la tine

Nimic urgent. Dacă îți place planul pentru partea b (modelul mic tăiat din cel mare, schimbări relative, testul Spearman
cu ρ ≥ 0,7), supraveghetorul o poate scrie ca sarcină cu pre-înregistrare.
