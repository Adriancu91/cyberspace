# Pre-înregistrare: Noaptea 7 (16–17 octombrie): W2, a treia noapte, cu rata constantă 0,00025. Iese de pe plafon?

<!-- scrisa: 2026-10-16T17:11:07 -->
*Scrisă la 2026-10-16 17:11, înainte de rulare. După ce rularea a început, textul de mai jos nu se mai schimbă; la închidere
se adaugă doar secțiunea „Ce a ieșit” (python unelte/preinregistrare.py --inchide noaptea7_w2_rata).*

## Întrebarea

**Scoate o rată constantă mai mică W2 de pe plafon?** În noaptea 2 (14–15 octombrie), româna a scăzut doar cu 0,029
(1,3775 → 1,3488), sub pragul de plafon de 0,03. Adrian a hotărât să încercăm o noapte cu **o singură schimbare**:
rata constantă 0,00025 în loc de 0,0005. Restul rămâne identic.

## Ce rulează

- **Configurarea:** `config/ws_w2_r025.toml` = copia exactă a lui `config/ws_w2.toml`, cu o singură diferență:
  `rata_invatare = 0.00025` (verificat cu `diff`; în rest sunt doar rândurile de comentariu de sus). Linia rămâne
  „ws_w2”: aceeași stare, același jurnal, aceleași examene. `config/ws_w2.toml` nu se schimbă.
- **Pornește din punctul nerăcit:** `lucru/ws_w2/gpt.pt`, starea de după ora 20, scrisă pe 15 octombrie la 05:39 și
  neatinsă de atunci (școala de cod a lucrat pe copii ale lui #353). 425.968 de pași făcuți, deci fără încălzire nouă.
  Optimizatorul continuă din stare; rata se ia din configurare la reluare (`module/model_continuu.py`).
- **Orele 21–30** (`--ore 30`), cu oprirea antrenării la 06:45 (ultima oră se scurtează, dacă e nevoie), ca răcirea și
  examenele să încapă până la oprirea de siguranță de la 07:30. Lot 12 × 512, hrana 6%, același amestec.
- **La sfârșit, copia răcită de 30 de minute**, pe linia de jurnal `ws_w2_racit_030`, cu toate examenele: val_bpb,
  fapte, fapte noi, setul sacru, nota, româna, codul. **De știut:** răcirea pleacă de la rata liniei, deci acum
  merge liniar 0,00025 → 0,00005 (la #353 a fost 0,0005 → 0,00005). Durata și capătul sunt aceleași; asta decurge
  din singura schimbare și nu e o a doua schimbare.
- **Cine o pornește:** Windows, la 19:00, prin `unelte/programeaza_noapte_ws.ps1` (sarcina „Kronos noapte ws_w2_r025”),
  cu reluare după logare până la 07:30 și oprire de siguranță la 07:30. CONTINUUM doar observă până la 17
  octombrie, 07:45 (`om_decide_pana_la`), deci nu pornește nimic pe placă.
- Paznicul: 7.000 MB și 83 °C. Nicio altă sarcină pe placă în noaptea asta.

## Cu ce se compară

Cu copia răcită #353 (după ora 20, rata 0,0005):

| | #353 |
|---|---|
| povești (val_bpb) | 0,4552 |
| română (media Wikipedia, web, cărți) | 1,3488 |
| cod (media cod și sarcini) | 0,7529 |
| fapte noi | 75 |
| setul sacru | 25 din 50 |
| nota profesorului | 3,80 |

## Ce înseamnă confirmat sau infirmat (pragurile lui Adrian, pe copia răcită de după ora 30)

- **Confirmat:** româna scade cu cel puțin 0,03 față de #353, adică ajunge la **1,3188 sau mai jos**, **și** poveștile
  nu trec de **0,46**.
- **Infirmat:** româna scade cu mai puțin de 0,01, adică rămâne **peste 1,3388**.
- **Între cele două** (româna între 1,3188 și 1,3388), sau româna confirmată dar poveștile peste 0,46: **neconfirmat**.
  Se raportează așa, fără să fie rotunjit spre vreo parte.

## Așteptările lui Claude Code (dinainte, doar pentru raport; nu schimbă verdictul)

- Orele nerăcite: prima oră va coborî mai mult decât de obicei (0,517 la ora 20), pentru că rata mai mică are și efectul
  unei mici răciri. Aștept 0,50–0,51 la ora 21, apoi coborâri mici.
- Pe copia răcită: româna între 1,31 și 1,34 (cred că mai probabil „neconfirmat”: o parte din câștigul răcirii era deja
  luat la #353); poveștile 0,44–0,455; codul 0,73–0,75; fapte noi cel puțin 60; sacru cel puțin 22; nota 3,3–4,3.
- Placa: cam 5.400 MB (cât la orele 18–20), sub 70 °C, viteza ~5,8 pași pe secundă, nicio oprire de la paznic.

## Ce a ieșit

*Adăugat la 2026-10-17 06:41, din jurnalul Kronos (lucru/jurnal/experimente.jsonl) și din jurnalul CONTINUUM pe bune. Verdictul se scrie dedesubt.*

| # | linia | început | val_bpb | decizia | fapte noi | fapte | nota | motivul |
|---|---|---|---|---|---|---|---|---|
| 363 | ws_w2 | 16.10 19:00 | 0,4800 | pastrat | 67 | 149 | 3,45 |  |
| 364 | ws_w2 | 16.10 20:05 | 0,4804 | respins | 65 | 149 | 3,33 | scorul nu e mai bun |
| 365 | ws_w2 | 16.10 21:09 | 0,4810 | respins | 57 | 147 | 3,67 | scorul nu e mai bun |
| 366 | ws_w2 | 16.10 22:13 | 0,4822 | respins | 63 | 148 | 3,77 | scorul nu e mai bun |
| 367 | ws_w2 | 16.10 23:17 | 0,4834 | respins | 62 | 147 | 3,52 | scorul nu e mai bun |
| 368 | ws_w2 | 17.10 00:21 | 0,4826 | respins | 76 | 150 | 3,38 | scorul nu e mai bun |
| 369 | ws_w2 | 17.10 01:25 | 0,4822 | respins | 65 | 148 | 3,55 | scorul nu e mai bun |
| 370 | ws_w2 | 17.10 02:29 | 0,4828 | respins | 61 | 147 | 4,10 | scorul nu e mai bun |
| 371 | ws_w2 | 17.10 03:33 | 0,4826 | respins | 72 | 148 | 3,50 | scorul nu e mai bun |
| 372 | ws_w2 | 17.10 04:37 | 0,4803 | respins | 70 | 147 | 3,67 | scorul nu e mai bun |
| 373 | ws_w2_racit_030 | 17.10 05:41 | 0,4422 | pastrat | 74 | 150 | 3,90 |  |
| 374 | examen_validari_ws | 17.10 06:13 | — | masurat | — | — | — |  |

- **ws_w2:** 10 ore, 1 păstrate; val_bpb de la 0,4800 la 0,4803; cel mai bun păstrat: #363 (0,4800).
- **ws_w2_racit_030:** 1 ore, 1 păstrate; val_bpb de la 0,4422 la 0,4422; cel mai bun păstrat: #373 (0,4422).

Niciun ciclu CONTINUUM pe bune în perioada asta.

## Verdictul (scris sâmbătă, 17 octombrie, 06:41, de Claude Code): CONFIRMAT

Copia răcită #373 (după ora 30, `lucru/ws_w2/modelul_zilei.json`), față de #353:

| | #353 (rata 0,0005) | #373 (rata 0,00025) | schimbarea |
|---|---|---|---|
| **română** (media Wikipedia, web, cărți) | 1,3488 | **1,3102** | **−0,0386** |
| – Wikipedia | 1,0783 | 1,0345 | −0,044 |
| **povești** (val_bpb) | 0,4552 | **0,4422** | −0,013 |
| cod (media cod și sarcini) | 0,7529 | 0,7338 | −0,019 |
| fapte noi | 75 | 74 | −1 |
| setul sacru | 25 din 50 | 27 din 50 | +2 |
| nota profesorului | 3,80 | 3,90 | +0,10 |

- **Româna a scăzut cu 0,0386**, deci sub pragul de 1,3188, **iar poveștile au ajuns la 0,4422**, deci sub 0,46.
  După pragurile lui Adrian: **CONFIRMAT**.
- Așteptările lui Claude Code: româna 1,31–1,34 (a ieșit 1,3102, la marginea de jos; mă așteptam mai degrabă la
  „neconfirmat”, deci am greșit); poveștile 0,44–0,455 (în interval); codul 0,73–0,75 (în interval); fapte noi ≥ 60,
  sacru ≥ 22, nota 3,3–4,3 (toate în interval). Orele nerăcite: ora 21 a coborât la 0,4800, mai mult decât așteptam
  (0,50–0,51), apoi au stat pe loc (0,480–0,483).
- **Placa:** cel mult 6.004 MB pe toată placa, 62 °C, 5,9 pași pe secundă, nicio oprire de la paznic. Antrenarea s-a
  încheiat la 06:14 (cod 0); starea liniei e neatinsă de copia răcită.
- **De știut, cinstit:** e o singură noapte, fără martor. O parte din câștig ar fi venit oricum dintr-o a treia noapte
  la 0,0005: noaptea 2 adusese −0,029 la română. Deci câștigul care se poate pune pe seama ratei e mai mic decât
  −0,0386: probabil în jur de 0,01. Iar orele nerăcite au stat pe loc toată noaptea, ca la un nou plafon, mai jos.
- **Ce urmează (de hotărât de Adrian):** dacă linia W2 rămâne de acum la 0,00025 (config/ws_w2_r025.toml) sau dacă
  facem un martor (o noapte la 0,0005, din aceeași stare) ca să despărțim efectul ratei de efectul timpului.

## Decizia lui Adrian (sâmbătă, 17 octombrie, ~17:15)

- **W2 merge de acum cu rata constantă 0,00025, ca rețetă nouă**, fără o noapte de comparație (martor) la 0,0005.
  `config/ws_w2.toml` are de acum `rata_invatare = 0.00025` (în rest e neschimbat; față de `config/ws_w2_r025.toml`
  diferă doar comentariile). Răcirea de la sfârșitul nopții merge liniar 0,00025 → 0,00005, ca în noaptea 7.
- **Partea din câștig care vine din rată e nesigură.** Din −0,0386 la română (1,3488 → 1,3102), o parte ar fi venit
  oricum dintr-o a treia noapte la 0,0005 (noaptea 2 adusese −0,029). Fără martor nu se poate despărți efectul ratei de
  efectul timpului; estimarea de mai sus („probabil în jur de 0,01”) rămâne o estimare, nu o măsurătoare.
- **CONTINUUM** antrenează linia W2 doar prin `config/ws_w2.toml` (nevoile „continua”, „deprinde” și „linie_noua”),
  deci folosește de acum 0,00025. Perioada în care doar observă rămâne neschimbată: până pe **18 octombrie, 07:45**
  (`om_decide_pana_la`).
