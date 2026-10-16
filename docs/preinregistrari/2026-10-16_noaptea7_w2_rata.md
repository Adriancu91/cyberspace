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
