# Pre-înregistrare: S94: prezice modelul mic de 6 straturi clasamentul rețetelor pe modelul de 24? (Spearman pe 5 rețete)

<!-- scrisa: 2026-11-08T08:33:23 -->
*Scrisă la 2026-11-08 08:33, înainte de rulare. După ce rularea a început, textul de mai jos nu se mai schimbă; la închidere
se adaugă doar secțiunea „Ce a ieșit” (python unelte/preinregistrare.py --inchide avans_spearman).*

Acoperă AMBELE părți: S94a (modelul mic, ziua de 8 nov) și S94b (modelul de 24, noaptea 8→9 nov). Sarcina: S94 din
`plan/coada.md` (C-85 pasul 4, aprobat de Adrian 6 nov 2026; pașii scriși de supraveghetor 8 nov 2026 02:15).

> 8 nov 11:15: repornire cu cache-ul `lucru/cache` (varianta a, oprirea din 08:52); pragurile, rețetele și minutele
> neschimbate. (Rând adăugat de executant la 11:36, înainte de placă; lanțul nou `lucru/cascada/S94_proba/s94a2.py`, jurnalul
> reparării `lucru/avans/s94_reparare2/`; încercările mici în `lucru/avans/s94_mic/`.)
>
> 8 nov 19:32 (executant, înainte de placa S94b; pragurile, rețetele și minutele neschimbate): lanțul
> `lucru/cascada/S94_proba/s94b.py`; configurările mari `lucru/avans/s94_mare/<k>/config.toml` (copii ale
> `conv_w2_mare_24r.toml` cu doar nume, cale_stare, eticheta, rata, încălzirea), liniile `avans_s94_mare_<k>`, fiecare
> dintr-o copie proaspătă a `gpt_24.pt`; cache `lucru/cache` doar citit; scorul = scorul orei (`romana_bpb`) din
> `lucru/avans_s94_mare_<k>/rezultat.json`; `val_bpb`/cod din `examen_validari_ws.py --linie`.

## Întrebarea

Ordinea în care modelul MIC (6 straturi, tăiat din `gpt_24.pt`, 15 min pe rețetă) clasează 5 rețete de antrenare după
română curat (`romana_bpb`) seamănă cu ordinea lor pe modelul de 24 de straturi (1 oră pe rețetă)? Dacă da, rețetele se
pot alege de acum pe modelul mic (C-85 pasul 4).

## Ce rulează

**Cele 5 rețete** (strict separate: fiecare = rețeta de bază cu O SINGURĂ schimbare, fiecare pornită din același fișier;
aceeași ordine pe ambele modele; `unelte/cercetator_avans.py --relativ --separat`):

| # | rețeta | rata mic / mare | încălzire mic / mare |
|---|---|---|---|
| 1 | bază (e1) | 1e-5 / 1e-5 | 1000 / 1000 |
| 2 | rata ×0,5 | 5e-6 / 5e-6 | 1000 / 1000 |
| 3 | rata ×2 | 2e-5 / 2e-5 | 1000 / 1000 |
| 4 | rata ×4 | 4e-5 / 4e-5 | 1000 / 1000 |
| 5 | încălzire ×2 | 1e-5 / 1e-5 | 2000 / 2000 |

Restul rețetei = `config/conv_w2_mare_24r.toml` (lot 4 × 24 adunate, AdamW, rata care scade pe 18.000 s, răcire finală
0,25, amestec cu 45 % conversație).

**S94a (placa, ziua de 8 nov, pornire ~08:45, sfârșit estimat ~11:30)** — lanțul `lucru/cascada/S94_proba/s94a.py`:
- (a) **Repararea, o singură dată:** 45 min de antrenare cu rețeta de bază pe `lucru/avans/mic6/gpt.pt` (doar citit,
  SHA înainte = după) → `lucru/avans/mic6r/gpt.pt`, prin platformă (jurnalul mic în `lucru/avans/s94_reparare/`).
  Română curat înainte: 2,7783 (S92). După: se notează.
- (b) **Cele 5 încercări, câte 15 min FIX** (nu se ajustează după viteză; viteza și simbolurile văzute doar se notează),
  fiecare din `mic6r/gpt.pt` (`stare_de_pornire`, nu se scrie), configurarea `config/avans_24_mic6r.toml`, ieșirea
  `lucru/avans/s94_mic/` (fiecare încercare în `incercari/<k>/`). Scorul: `romana_bpb` (portul `examen` =
  `module.examen_romana:ExamenRomana`, 100.000 de caractere), după fiecare încercare.
- Paza: nvidia-smi la 5 s; peste 6.700 MB sau 83 °C pasul e oprit (încercarea NEMĂSURATĂ).

**S94b (placa, noaptea 8→9 nov, de la 19:00, gata până la 07:00 luni)** — doar dacă S94a are toate 5 încercările
măsurate: aceleași 5 rețete pe modelul de 24 de straturi, câte **1 oră** fiecare, FIECARE dintr-o copie proaspătă a lui
`lucru/w2_mare/gpt_24.pt` (SHA `d35e3dbe…92cc` înainte = după), restul exact ca `conv_w2_mare_24r.toml`, paza cu
`gc.collect`. Scor `romana_bpb` după fiecare oră (aceeași măsură). Dacă nu poate porni până la 00:30, rămâne pentru
noaptea 9→10.

## Pragurile (copiate exact din sarcină, S91/S92)

- ρ Spearman între clasamentul mic și cel mare pe cele 5 rețete; diferențe sub **0,002** biți/octet = egalitate (rang mediu).
- **DA** = ρ ≥ **0,7** ȘI câștigătorul mic e în primele 2 pe cel mare;
- **NU** = ρ ≤ **0,3**;
- altfel **NECLAR**.
- O încercare anulată de pază = NEMĂSURATĂ, celelalte continuă; cu mai puțin de 4 măsurate pe cel mare, verdictul e
  **NEMĂSURAT**.
- Regula C-88 (în plus, nu schimbă verdictul): pe fiecare încercare se notează informativ și `val_bpb` (povești), dacă
  e măsurat; pe modelul mare, o încercare cu `val_bpb` peste **0,4100** (#513 0,4050 + 0,005) sau cod curat peste
  **0,7297** e marcată „strică poveștile/codul” — o rețetă așa nu poate fi propusă pentru cel mare.
- Informativ: `val_bpb`, cod curat, placa max MB/°C, pași/s, simboluri văzute pe încercare (mic vs mare).

## Să nu uite (scris înainte de rulare)

1. **Încălzirea ×2 pe modelul mic e aproape fără efect.** Încălzirea se face doar în primii pași AI MODELULUI
   (`pasi_total` din fișier). După repararea de 45 min, `mic6r` are zeci de mii de pași în spate, deci și 1.000, și
   2.000 de pași de încălzire sunt deja trecuți: rețeta 5 pe cel mic = rețeta 1 (aceleași date, aceeași rată), cu
   diferențe doar din zgomotul plăcii. Pe cel mare (`gpt_24.pt`, 0 pași) încălzirea chiar se face (~2,6 vs ~5,2 min din
   60). Asimetria e cunoscută dinainte; o egalitate 1 = 5 pe cel mic NU e un rezultat despre încălzire.
2. Modelul mic pornește și cu starea optimizatorului din reparare, iar cel mare cu cea din `gpt_24.pt`.
3. Rata absolută e aceeași pe ambele modele (1e-5); clasamentul compară factorii, nu valorile.
4. Orele pe cel mare pornesc toate din `gpt_24.pt`, nu din #536 și nu din încercarea dinainte.

## Așteptările, în cifre

- **Repararea (mic):** română curat de la 2,7783 la ~**1,60** (între 1,45 și 1,80) după 45 min.
- **Cele 5 pe cel mic (15 min după reparare):** toate în ~1,45–1,65; ordinea ghicită (cel mai bun primul):
  **4 (×4) < 3 (×2) < 1 ≈ 5 < 2 (×0,5)** — modelul mic, încă stricat după tăiere, câștigă cu rata mare; diferența dintre
  ×4 și ×0,5 ~0,03–0,08.
- **Cele 5 pe cel mare (1 oră din `gpt_24.pt`):** toate în ~1,205–1,215 (#513 1,2060, #536 1,2063 după 5 ore);
  ordinea ghicită: **3 (×2) < 1 < 5 < 2 (×0,5) < 4 (×4)** — la modelul bun, rata ×4 îl scutură prea tare; diferențele mici
  (0,002–0,008), deci câteva egalități.
- **ρ ghicit: ~0,3–0,5**; câștigătorul mic (×4) ghicit pe locul 4–5 pe cel mare.
- **Șanse:** DA 25 %, NECLAR 45 %, NU 30 %.

## Ce ar infirma așteptările

- ρ ≥ 0,7 cu ×4 câștigător și pe cel mare (sau ×2 câștigător pe ambele) → am subestimat cât de bine prezice modelul mic.
- Pe cel mic, ×0,5 câștigă sau toate 5 sunt la egalitate (sub 0,002) → modelul mic nu deosebește rețetele în 15 min.
- Repararea dă peste 2,0 după 45 min → modelul tăiat e mai stricat decât credeam (de spus în raport; clasamentul mic
  rămâne valid, dar mai puțin sigur).

## Ce a ieșit

*Adăugat la 2026-11-09 01:05, din jurnalul Kronos (lucru/jurnal/experimente.jsonl) și din jurnalul CONTINUUM pe bune. Verdictul se scrie dedesubt.*

| # | linia | început | val_bpb | decizia | fapte noi | fapte | nota | motivul |
|---|---|---|---|---|---|---|---|---|
| 540 | avans_s94_mare_1 | 08.11 19:34 | — | pastrat | — | — | — |  |
| 541 | examen_validari_ws | 08.11 20:38 | — | masurat | — | — | — |  |
| 542 | avans_s94_mare_2 | 08.11 20:38 | — | pastrat | — | — | — |  |
| 543 | examen_validari_ws | 08.11 21:42 | — | masurat | — | — | — |  |
| 544 | avans_s94_mare_3 | 08.11 21:43 | — | pastrat | — | — | — |  |
| 545 | examen_validari_ws | 08.11 22:46 | — | masurat | — | — | — |  |
| 546 | avans_s94_mare_4 | 08.11 22:47 | — | pastrat | — | — | — |  |
| 547 | examen_validari_ws | 08.11 23:50 | — | masurat | — | — | — |  |
| 548 | avans_s94_mare_5 | 08.11 23:51 | — | pastrat | — | — | — |  |
| 549 | examen_validari_ws | 09.11 00:55 | — | masurat | — | — | — |  |


Niciun ciclu CONTINUUM pe bune în perioada asta.

## Verdictul

*Scris de executant la 2026-11-09 01:05, strict după pragurile de mai sus. Raport: `docs/rapoarte/2026-11-09_0105_S94b_spearman.md`.*

Toate 5 încercările mari măsurate (niciuna anulată de pază), deci verdictul se poate da.

| rețeta | mic `romana_bpb` (15 min) | rang mic | mare `romana_bpb` (1 oră) | rang mare |
|---|---|---|---|---|
| 1 bază | 1,6311 | 3,5 | 1,21184 | 2 |
| 2 rata ×0,5 | 1,6441 | 5 | 1,21020 | 2 |
| 3 rata ×2 | 1,6116 | 2 | 1,21581 | 4 |
| 4 rata ×4 | 1,5892 | 1 | 1,22323 | 5 |
| 5 încălzire ×2 | 1,6312 | 3,5 | 1,21184 | 2 |

Pe cel mare, 2, 1 și 5 sunt toate la mai puțin de 0,002 una de alta (0,00165 și 0,000005) → egalitate, rang mediu 2.

- **ρ Spearman = −0,92** (cu egalitățile cerute; fără egalități pe cel mare ar fi −1,00).
- Câștigătorul mic (rata ×4) e pe **locul 5 (ultimul)** pe cel mare.
- ρ ≤ 0,3 → **NU**: modelul mic de 6 straturi NU prezice clasamentul rețetelor pe modelul de 24; îl prezice invers.
- Așteptarea mea (ρ 0,3–0,5, NU cu 30 %) a fost greșită în sensul „mai rău”: ordinea mare ghicită 3 < 1 < 5 < 2 < 4, cea reală 2 < 1 ≈ 5 < 3 < 4.
- Regula C-88: rata ×2 (cod curat 0,7314 > 0,7297) „strică codul”; rata ×4 (val_bpb 0,4135 > 0,4100, cod 0,7376) „strică poveștile și codul”.
- De reținut: niciuna din cele 5 ore nu a coborât sub pornirea `gpt_24.pt` (1,2096); cea mai bună (×0,5) 1,2102.
