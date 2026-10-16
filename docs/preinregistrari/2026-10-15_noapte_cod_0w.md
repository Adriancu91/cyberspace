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
