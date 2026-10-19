# Pre-înregistrare: Noaptea 9 (18–19 octombrie): W2-conv din #385. Răspunde Kronos la întrebări fără să uite româna?

<!-- scrisa: 2026-10-18T09:33:16 -->
*Scrisă la 2026-10-18 09:33, înainte de rulare. După ce rularea a început, textul de mai jos nu se mai schimbă; la închidere
se adaugă doar secțiunea „Ce a ieșit” (python unelte/preinregistrare.py --inchide noaptea9_w2_conv).*

## Cine a ales

**Alegerea e a lui Adrian** (17 și 18 octombrie): W2-conv pornește din **#385** (copia răcită a lui W2 după ora 40),
cu datele de conversație refăcute azi și examenul de mai jos. CONTINUUM doar observă până luni, 19 octombrie, 07:45
(`config/continuum_ws.toml`, prelungit azi cu aprobarea lui Adrian).

## Întrebarea

**Învață Kronos să răspundă scurt și corect la întrebări simple (și să spună „nu știu” la lucruri care nu există), fără
să uite româna, poveștile și codul?**

## Datele (refăcute azi, 09:26; `python unelte/genereaza_conversatie.py --finalizeaza-v3`)

- **Antrenare: 13.446 de perechi** „Întrebare: … / Răspuns: …”:
  - **Wikipedia v3: 7.948** (fișa a trecut cu 2 greșite din 30; #1 și #9 au ieșit);
  - **„nu știu” în română: 400** (șabloane scrise de Claude Code: oameni, locuri, azi, viitor);
  - **profesorul, în engleză: 4.859** (3.731 de zi cu zi, 553 despre fapte, 575 „nu știu”);
  - **profesorul, fapte în română: 239.**
  - **Fără traduceri** (scoase definitiv pe 15 octombrie) și fără româna liberă a lui Qwen.
- **Examenul, nevăzut la antrenare: 80 de întrebări** (`date/conversatie/examen.json`; nicio întrebare și niciun grup
  nu e în antrenare, verificat):
  - **50 din Wikipedia v3,** alese la întâmplare (sămânța 1018) dintre cele pe care Adrian **nu** le-a văzut în nicio
    fișă (cele 506 verificate până pe 17 octombrie și cele 30 din fișa v3);
  - **20 „nu știu”** despre lucruri inventate (15 în română, 5 în engleză), scrise de mână de Claude Code
    (`docs/conversatie/examen_scris_de_mana.json`). Exemple: „Cât de lung este râul Zămbrița?”, „Ce animal este
    zulvarul de munte?”. Am verificat că niciun nume inventat nu apare în amestecul de antrenare, în hrană sau în
    perechile de conversație. **Altfel decât șabloanele din antrenare** (acolo: „Ce a mâncat X ieri?”), deci examenul
    arată dacă Kronos recunoaște lucrul necunoscut, nu doar forma întrebării;
  - **10 de conversație** („Cum te cheamă?”, „Ce poți face?”, „What is your name?”), cu răspunsuri de referință scrise
    de mână. **În antrenare nu e nicio pereche de felul ăsta**, deci acestea sunt doar urmărite, fără prag.

## Ce rulează

- `config/conv_w2.toml` (neschimbat față de 15 octombrie): linia „w2_conv”, **3 ore**, lot 12 × 512, 75% perechi
  (pierderea doar pe răspunsuri), 5% hrană, 20% amestecul lui W2; **rata 0,0001** constantă, după 100 de pași de
  încălzire.
- **Pornire: 19:00**, de Windows (sarcina „Kronos noapte conversatie”: `unelte/noapte_conversatie.ps1 -PornesteDin 385
  -FaraScoala`), doar dacă placa e liberă și testele trec (verific la 18:45). Fără școala de cod.
- La fiecare oră: val_bpb, fapte, fapte noi, nota profesorului. Kronos păstrează fiecare oră (`prag_zgomot = -1`).
- **După ora 3, pe ultimul model păstrat:** examenul de conversație (`unelte/examen_conversatie.py`: răspunsul fără
  întâmplare, cel mult 80 de bucăți, tăiat la primul rând nou; profesorul Qwen3-4B notează 1–10 față de referință),
  examenul pe validări (cu variantele curate) și setul sacru.
- Examenul neutru pe seturile întregi rulează ziua pe procesor și se oprește la 18:55, dacă nu e gata.

## Ce înseamnă confirmat sau infirmat

Un răspuns e **corect** dacă profesorul îi dă **cel puțin 7 din 10**. La „nu știu” e corect dacă spune că nu știe („Nu
știu…”, „I don't know…”).

- **Confirmat:**
  - **cel puțin 15 din cele 50** de întrebări Wikipedia corecte,
  - **și cel puțin 10 din cele 20** „nu știu” corecte,
  - **și „nu știu” spus la cel mult 10 din cele 50** de întrebări Wikipedia, ca să nu fi învățat doar să se ferească.
- **Infirmat:** **sub 8 din 50** la Wikipedia **sau sub 5 din 20** la „nu știu”.
- Între ele: „a început, dar nu ajunge”.
- **Regresia, pe ultimul model, față de #385.** Peste oricare prag, linia nu se păstrează (nu intră în interfață), oricum
  ar ieși examenul:
  - **română pe validarea curată: cel mult +0,03,** adică **≤ 1,3133** (#385: 1,2833);
  - **cod pe validarea curată: cel mult +0,03,** adică **≤ 0,8174** (#385: 0,7874);
  - **povești (val_bpb): ≤ 0,47** (#385: 0,4383);
  - **fapte noi: ≥ 65** (#385: 73).
- **Setul sacru, urmărit** (#385: 18 din 50): dacă scade **sub 15 din 50**, îl raportez separat, cu întrebările pierdute
  față de #385.
- **Dimineață:** lui Adrian îi trimit **20 de răspunsuri alese la întâmplare** (sămânța 1019) din cele 80, cu
  întrebarea, răspunsul lui Kronos, referința și nota profesorului, ca să le verifice.
- **Dacă trece** (confirmat și fără regresie): Adrian hotărăște dacă intră în interfață.

## Așteptările mele, în cifre (Claude Code, scrise înainte)

- **Wikipedia: 6–14 din 50 corecte.** Forma („X este un sat în comuna Y, județul Z”) o va învăța repede, dar amănuntele
  (comuna, județul, anul) le nimerește greu un model de 98 de milioane de parametri. Cred că e mai probabil „a început,
  dar nu ajunge” decât confirmat.
- **„Nu știu”: 3–9 din 20.** Șabloanele din antrenare sunt despre oameni și „azi”. Lucrurile inventate seamănă cu
  întrebările Wikipedia („Ce este X?”), la care Kronos va învăța să dea o definiție, deci va inventa des.
- **„Nu știu” la Wikipedia: 1–5 din 50.**
- **Conversația: 0–3 din 10** (n-a văzut nimic de felul ăsta; poate „Mulțumesc” și „La revedere”).
- **Regresia:**
  - româna curată 1,27–1,30, pentru că perechile Wikipedia sunt tot română;
  - codul curat 0,79–0,82, **aproape de prag**: codul vine doar din cei 20% de amestec;
  - poveștile 0,44–0,46;
  - fapte noi 60–75, deci **aproape de prag**;
  - sacru 14–20.
- **Placa:** ~5.400 MB, sub 70 °C, ~5,9 pași pe secundă, nicio oprire.

## Ce ar infirma așteptările

- **Peste 20 din 50 la Wikipedia,** adică mult mai bine decât cred: Kronos ține minte Wikipedia mai bine decât arată
  examenele de până acum;
- **peste 12 din 20 la „nu știu”**: recunoaște lucrurile necunoscute, nu doar forma întrebării;
- **codul curat peste 0,85 sau poveștile peste 0,48**: 20% din amestec nu ajunge ca să nu uite.

## Ce a ieșit

*Adăugat la 2026-10-19 09:15, din jurnalul Kronos (lucru/jurnal/experimente.jsonl) și din jurnalul CONTINUUM pe bune. Verdictul se scrie dedesubt.*

| # | linia | început | val_bpb | decizia | fapte noi | fapte | nota | motivul |
|---|---|---|---|---|---|---|---|---|
| 394 | w2_conv | 18.10 19:00 | 0,4779 | pastrat | — | — | — |  |
| 395 | w2_conv | 18.10 20:05 | 0,4832 | pastrat | — | — | — |  |
| 396 | w2_conv | 18.10 21:09 | 0,4877 | pastrat | — | — | — |  |
| 397 | examen_conversatie | 18.10 22:13 | — | masurat | — | — | — |  |
| 398 | examen_validari_ws | 18.10 22:13 | — | masurat | — | — | — |  |

- **w2_conv:** 3 ore, 3 păstrate; val_bpb de la 0,4779 la 0,4877; cel mai bun păstrat: #394 (0,4779); pornită din #385 (0,4383).

Niciun ciclu CONTINUUM pe bune în perioada asta.

## Verdictul

*Scris la 2026-10-19 09:25 de Claude Code, strict după pragurile de mai sus. Examenele pe ultimul model, #396 (ora 3):
`lucru/examen_conversatie/experiment_396_20261018_221340.json`, `lucru/examen_validari_ws/experiment_396_20261018_221354.json`,
`lucru/examen_sacru/experiment_396_20261018_221402.json`.*

| | prag | #396 | |
|---|---|---|---|
| Wikipedia corecte (nota ≥ 7), din 50 | confirmat ≥ 15, infirmat < 8 | **2** | **infirmat** |
| „nu știu” corecte, din 20 | confirmat ≥ 10, infirmat < 5 | 15 | trece |
| „nu știu” spus la Wikipedia, din 50 | ≤ 10 | 0 | trece |
| conversație, din 10 (doar urmărit) | — | 0 | — |
| română, validarea curată | ≤ 1,3133 | **1,3781** | **depășit** |
| cod, validarea curată | ≤ 0,8174 | **0,8736** | **depășit** |
| povești (val_bpb) | ≤ 0,47 | **0,4877** | **depășit** |
| fapte noi | ≥ 65 | 75 | trece |
| setul sacru (urmărit), din 50 | sub 15 = raport separat | 26 (#385: 18) | nu e nevoie |

**Verdict: INFIRMAT** (Wikipedia 2 din 50, sub 8), **cu regresie** la română, cod și povești. Linia w2_conv nu se
păstrează și nu intră în interfață.

Față de așteptări:
- **Wikipedia, 2 față de 6–14:** mai rău decât credeam. Modelul a învățat forma („X este un film / un sat în comuna
  …”), dar inventează amănuntele: 40 din 50 de răspunsuri au nota 1.
- **„Nu știu”, 15 față de 3–9:** mult mai bine decât credeam, deci așteptarea „peste 12 din 20” din „Ce ar infirma
  așteptările” s-a îndeplinit. Totuși, la Wikipedia n-a spus niciodată „nu știu”, iar la conversație l-a spus la 6 din 10
  („Cum te cheamă?” → „Nu știu sigur.”). Pare să se ia după cât de ciudat sună numele, nu după ce știe; cele 5 ratate sunt
  tocmai cele cu nume obișnuite („Ce este planeta Ostrovia?”, „Unde se află muntele Căpraru Înalt?”).
- **Uitarea, mai mare decât credeam:** codul curat 0,87 și poveștile 0,49 au trecut și de pragul din „Ce ar infirma
  așteptările” (0,85 și 0,48). 20% amestec nu ajunge. val_bpb a crescut în fiecare oră (0,4383 → 0,4779 → 0,4832 → 0,4877).
- **Setul sacru, 26 față de 14–20:** a crescut față de #385 (18), deși restul a scăzut.
- Placa: ~5.370 MB, 5,9 pași pe secundă, nicio oprire, cum mă așteptam.
