# Pre-înregistrare: Școala de cod v0.4, noaptea 15–16 octombrie: trece W2 (#353) de nivelul 0w dacă are mai mult timp?

<!-- scrisa: 2026-10-15T08:23:00 -->
*Scrisă joi, 15 octombrie, 08:23, înainte de rulare. Alegerea nopții e a lui Adrian, nu a lui CONTINUUM. După ce
pornește, textul nu se mai schimbă; la sfârșit se adaugă doar „Ce a ieșit” și verdictul.*

## Întrebarea

**Trece modelul de nivelul 0w** (cuvântul din răspuns nu apare în sarcină: din sarcină nu se poate copia), dacă are
patru ori mai mult timp decât ziua? Ziua, pe #337, după 30 de minute: B 15%, D 25% pe setul nevăzut.

## Ce rulează

- `config/scoala_cod_v04_noapte.toml` (ramura `kronos-cod`), dosarul `lucru/cod_v04_noapte/`.
- **Modelul de pornire:** o copie a lui **#353** (copia răcită a lui W2 după ora 20), sha256 `9a682909b7b930e2…`,
  identică cu originalul. Linia W2 nu se atinge.
- **Nivelurile:** 0w, apoi 1a, 1b, 2A, 2B, 2C, 3A, 3B (0n și 0q au fost trecute ziua, pe #337). Liniile A, B, D, pe
  rând la fiecare nivel; fiecare linie se oprește la primul nivel picat.
- **Bugetul pe nivel și linie: 120 de minute sau 100 de runde** (ziua: 30 și 60).
- **Pragul de regresie la povești:** #353 are 0,4552 pe bucata fixă (măsurat de școală); plus 0,03 = **0,49**.
- **Pornirea:** după linia W2-conv (aceeași noapte), din scriptul nopții. **Oprirea:** nicio rundă nouă între 06:45 și
  19:00 (`inceput_permis`, nou, cu test).
- Restul regulilor: ca la pilotul de ziua (abecedarul, examenul, sandbox-ul, setul sacru neschimbate; amprentele
  aprobate rămân; lotul de 24 pe bucăți de 8).

## Așteptările (scrise înainte)

- **0w pică pe toate liniile** și școala se oprește acolo. Destul de siguri: din sarcină nu se poate copia răspunsul,
  iar ziua niciuna n-a trecut de 25%. Mai mult timp ar putea urca D la 35–50%, dar nu la 80%.
- **Linia A** (fără lecții noi): sub 20% la 0w.
- **Poveștile:** sub 0,49 la fiecare îngheț.
- Placa: sub 5.500 MB pe toată placa, sub 70 °C.

## Ce ar confirma și ce ar infirma

- **Confirmat („mai mult timp ajută”):** 0w trece (nevăzut ≥ 80%) pe linia B sau D.
- **Infirmat:** 0w pică pe toate trei. Atunci pasul următor e o schimbare a felului de sarcină (nu mai mult timp).
- **Parțial:** pică, dar D sau B ajunge peste 50% (atunci timpul ajută, dar nu ajunge).
- **Ar strica rularea:** regresie pe povești, paznicul oprește școala, sau nu pornește până la 06:45.

## Adendum 1 (scris vineri, 16 octombrie, 09:52, înainte de reluare)

- **Rularea a fost întreruptă la 00:26** de o repornire făcută singură de Windows Update (nu de pană). Linia A și linia
  B terminaseră 0w (picat amândouă, bugetul de 120 de minute epuizat). Linia D era la runda 60 din 0w (75 de minute
  din 120); ultima rundă, la 00:25:30: văzut 85%, nevăzut 30%.
- **Reluarea, cerută de Adrian:** linia D continuă 0w ziua, până la 12:00 sau până trece. Pornește din starea salvată
  după runda 60 (aceeași cu înghețul nou `v04n_D_0w_dupa_repornire`, făcut înainte de schimbarea configurării, cum
  cere școala); bugetul rămas: 45 de minute sau 40 de runde.
- **Singura schimbare în configurare:** `oprire_la` 06:45 → **12:00** (nicio rundă nouă între 12:00 și 19:00).
- Așteptările și ce înseamnă confirmat sau infirmat nu se schimbă.

## Ce a ieșit și verdictul (scris vineri, 16 octombrie, 10:41)

Rularea: 19:00–00:25 (întreruptă de Windows Update la 00:26), apoi linia D reluată 09:53–10:40. Fiecare linie a avut
tot bugetul de 120 de minute pe 0w. Jurnalul: `lucru/cod_v04_noapte/runde.jsonl`; raportul școlii:
`lucru/cod_v04_noapte/raport.md`.

| Linia | Runde | Văzut (cel mai bun / la sfârșit) | Nevăzut (cel mai bun / la sfârșit) | Povești la îngheț |
|---|---|---|---|---|
| A (martorul) | 93 | 9% / 6% | 5% / 5% | 0,4405 |
| B | 97 | 65% / 54% | 35% / 35% | 0,4402 |
| D | 97 | 85% / 69% | 35% / 30% | 0,4402 |

- **Verdictul: INFIRMAT.** 0w pică pe toate trei liniile (cel mult 35% pe nevăzut, față de 80% cerut), deci nici
  „parțial” (peste 50%). **Mai mult timp nu ajunge:** ziua, în 30 de minute, B avea 15% și D 25%; în 120 de minute, 35%.
  Pasul următor, cum scria dinainte, e o schimbare a felului de sarcină, nu mai mult timp.
- **Văzut urcă, nevăzut nu:** D trece până la 85% din sarcinile văzute, dar rămâne la ~30% pe cele nevăzute: învață
  sarcinile, nu regula (cuvântul care nu apare în sarcină).
- **Așteptările:** A sub 20% (5%): da. D între 35% și 50%: la margine (35% cel mai bun, 30% la sfârșit). Poveștile sub
  0,49: da, chiar mai bune decât la pornire (0,4402 față de 0,4552), din cauza poveștilor din lot. Placa: cel mult
  5.193 MB pe toată placa (reluarea; noaptea, ~5.170 MB), 62 °C. Nicio oprire de la paznic.
- **De știut:** înainte de orice lecție, #353 trecea deja pe nevăzut 70% la 1a, 70% la 1b, 75% la 2A, 100% la 2B, 90%
  la 2C și 75% la 3A (doar 0w, 5%, și 3B, 5%, rămân jos). Codul din amestecul lui W2 i-a învățat cea mai mare parte din
  școală; 0w e piedica.
