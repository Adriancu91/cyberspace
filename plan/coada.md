# Coada de lucru

Regulile: `plan/REGULI_CASCADA.md`. Executantul ia de sus în jos prima sarcină cu starea `aprobat` care se potrivește
cu fereastra orară și cu placa liberă.

Stări: `propus` · `propus — necesită Adrian` · `aprobat` · `in_lucru` · `gata` · `oprit`.

Formatul unei sarcini:

```
### S<număr> — titlu scurt
- stare:
- tip: placă / procesor
- fereastră: zi (08:00–18:30) / noapte (19:00–07:00) / oricând
- durată maximă:
- ce faci: (instrucțiunea exactă, cu comanda sau configurarea)
- pre-înregistrare: docs/preinregistrari/…
- aprobat de: Adrian / supraveghetor, data
- raport: docs/rapoarte/…
```

**⚠ ACUM — 9 nov 2026 (supraveghetor, 19:10; COMENZI.md C-94, Adrian):** **Adrian NU mai vine diseară; testul OS (`os-276`) e mâine, 10 nov, la 07:15.** Asta înlocuiește regulile C-93 pentru noaptea 9→10: (1) **rezervarea 19:30–21:00 se anulează — S95 poate porni de acum (de la 19:30)**, cel târziu la **00:00**; (2) antrenarea + examenele trebuie să **elibereze placa până la 06:45** (la 05:30 aplici punctul 6 al lui S95 cu limita 06:45); (3) **de la 06:45 NIMIC pe placă și nimic greu pe procesor** până scrie Adrian (hub `COMENZI.md` sau aici) că a terminat testul; (4) stick-urile rămân neatinse (S97 `oprit`); (5) S98 rămâne pentru după testul de mâine (neschimbat). Restul regulilor S95 (salvare la fiecare oră, întreruperea de la o repornire = NEMĂSURAT fără vină) rămân.

**⚠ ACUM — 9 nov 2026 (supraveghetor, 17:15):** **S96 = GATA, verificat** (proba de identitate DA, același SHA-256 pe 1,34 mld simboluri; doar fișiere noi; 1343 teste). La noapte rămâne exact planul de la 14:15: **S95 de la 21:00** (nu între 19:30 și 21:00), placa liberă până la 07:45. **S98 (NOU, doar procesor, `aprobat`)** = legarea datelor pe bucăți în antrenare, într-un modul NOU, neactivat — **NU mâine dimineață cât e Adrian la workstation**: pornește doar după o notă de la Adrian/centrul de comandă că a terminat testul (hub `COMENZI.md` sau aici) și niciodată în timpul unei sarcini pe placă (detalii la S98).

**⚠ ACUM — 9 nov 2026 (supraveghetor, 14:15; COMENZI.md C-93, Adrian):** **C-90 s-a încheiat** — Adrian a plecat (11:43), workstation-ul rămâne în Windows, stick-urile băgate: **nu le atinge** (S97 rămâne `oprit`; arhivele `os-276` i le dă centrul de comandă). Adrian revine **diseară la ~20:00 SAU mâine la 08:30** (nu e sigur). Reguli pentru azi și la noapte: (1) **placa e liberă până la 19:30**; (2) **între 19:30 și 21:00 NU pornește nimic pe placă**; (3) **S95 pornește la 21:00 (nu la 19:00)**, DOAR dacă până atunci calculatorul n-a fost repornit în Cyber Universe și nu e o notă nouă de la Adrian că lucrează; cel târziu la 00:30; **placa liberă până la 07:45** (testul de mâine la 08:30); dacă e întrerupt de o repornire, orele salvate rămân și le notezi (detalii la S95). (4) **S96 (doar procesor) e adus AZI după-amiază**: pornești până la 16:00 și termini până la 19:15; dacă nu poate porni până la 16:00, rămâne pentru marți de la 08:00 (detalii la S96).

**⚠ ACUM — 9 nov 2026 (supraveghetor, 11:15):** **S97 = OPRIT, verificat — motiv bun** (`gh api` cere aprobare în rularea programată și e refuzat; nimic descărcat, stick-urile neatinse). Release-ul cu reparația **există: `os-276`** (publicat 08:54, CI verde; verificat de supraveghetor pe GitHub). **S97 rămâne `oprit`** — nu-l reîncerca singur în rulările programate (pică la fel); îl face Adrian cu tine de față (sesiune interactivă: „fă S97 acum”, cu `os-276`) sau manual. Restul neschimbat: nimic pe placă cât e Adrian la workstation (C-90); S95 la noapte doar dacă workstation-ul e în Windows; S96 marți.

**⚠ ACUM — 9 nov 2026 (supraveghetor, 08:15; COMENZI.md C-90 și C-92, Adrian):** Adrian e la workstation pentru testul OS (C-90, de la ~08:50; pleacă și revine până la ~13:00, poate mai rămâne după): **nimic pe placă** până scrie el că a plecat (sau ~14:00); calculatorul se repornește în Cyber Universe de mai multe ori — o sarcină pe procesor întreruptă de repornire se reia după, **fără** `oprit`. **S97 (C-92, NOU, `aprobat` de Adrian):** la fiecare trecere verifici dacă a apărut release-ul OS care repară I8 (mai nou decât `os-275`) și, când apare, pregătești singur stick-urile E: și D: — pașii exacți jos, la S97. S97 are prioritate față de orice altă sarcină de procesor azi (nu folosește placa). **S95** rămâne pentru noaptea 9→10 (am adăugat la el nota despre „eroarea după examen” din raportul de dimineață). S96 marți. S88: Adrian poate rula el ștergerea (C-90).

**⚠ ACUM — 9 nov 2026 (supraveghetor, 02:15):** **S94 = GATA, verificat — NU** (ρ recalculat de mine: −0,918 cu rangurile pre-înregistrate; pe valorile brute −0,97 — raportul spune „−1,00 fără egalități”, mică greșeală de calcul, verdictul nu se schimbă; câștigătorul mic ×4 ultimul pe cel mare; placa max 6.426 MB / 61 °C; 1337 teste). Modelul mic de 6 straturi NU se folosește la alegerea ratei pentru cel de 24. **Luni 9 nov, ziua: NIMIC pe placă și nimic lung pe procesor** (fereastra lui Adrian, C-83 — testul OS). **Noaptea 9→10, placa, de la 19:00: S95** (jos, `aprobat`) — continuarea lui #536 cu rata ×0,5, 5 ore, judecată pe română; pornește DOAR dacă workstation-ul e înapoi în Windows și Adrian a terminat (nicio notă nouă de la el în hub/coadă că mai lucrează). **S96** (C-85 pasul 5, doar procesor) — după S95: marți 10 nov de la 08:00. S88 rămâne `oprit` până scrie Adrian.

**⚠ ACUM — 8 nov 2026 (supraveghetor, 14:15):** **S94a = GATA, verificat** (reparare 2,7783 → 1,6648, în intervalul 1,45–1,80; cele 5 mici 1,5892–1,6441, toate măsurate; ordinea mică 4 < 3 < 1 ≈ 5 < 2 — diferențele vecine 0,0224 / 0,0195 / 0,0001 (egalitate, sub 0,002) / 0,0129, recalculate de mine; `mic6`, `mic6r`, `lucru/cache` neschimbate; vârf 4.970 MB / 62 °C; 1337 teste). **S94b rămâne `aprobat` pentru noaptea 8→9** (de la 19:00, pornire cel târziu 00:30, gata până la 07:00 luni) — vezi nota „adăugat de supraveghetor 8 nov 14:15” la S94. Restul zilei de azi placa rămâne liberă (nu încape nimic util înainte de 18:30 fără să riște S94b). S88 rămâne `oprit` până scrie Adrian.

**⚠ ACUM — 8 nov 2026 (supraveghetor, 11:15):** **S94a = OPRIT, verificat — motiv bun** (paznicul a anulat repararea la 600 s: simbolurile se făceau de la zero într-un cache nou și gol; placa n-a lucrat, vârf 463 MB; `mic6` neatins). **Aleg varianta (a)**: repararea și toate încercările citesc simbolurile gata făcute din `lucru/cache` (reparație de unealtă, granițele 5 și 6). **S94 înapoi la `aprobat`** — instrucțiunile exacte jos, la S94, „adăugat de supraveghetor 8 nov 11:15”. S94a trebuie să pornească **cel târziu la 15:30**; altfel nu azi și S94b nu pornește la noapte. S88 rămâne `oprit` până scrie Adrian.

**⚠ ACUM — 8 nov 2026 (supraveghetor, 02:15):** **S89 = GATA, verificat — LA FEL** (română curat #536 1,2063 vs #513 1,2060, praguri 1,2010 / 1,2110; nicio STRICĂ; toate 5 orele trecute, vârf 6.465 MB / 62 °C). **S92 = GATA, verificat** (modul relativ + `mic6`, `gpt_24.pt` neschimbat, 1328 teste). Placa e liberă până la 07:00, dar nu pun nimic pe ea în restul nopții (nu încape o rulare întreagă cu note până la 07:45). **Acum, procesor: S93** (aprobat, C-88). **Ziua de 8 nov, placa: S94a** (jos, `aprobat`) — DOAR după ce S93 e `gata`; pre-înregistrarea întâi. **Noaptea 8→9: S94b**, gata până la 07:00 luni (luni placa e a lui Adrian, C-83). Continuarea liniei `w2_mare_24g` (curba încă scade) se decide după S94. S88 rămâne `oprit` până scrie Adrian.

**⚠ ACUM — 7 nov 2026 (supraveghetor, 20:15; COMENZI.md C-88, Adrian — „Română da”):** **S89 rulează** (pornit 19:31, proces 25092) — **nu-l întrerupi și nu-i schimbi nimic** (C-88 spune explicit asta). **S92** rămâne `aprobat`, pe procesor, după verificarea de la 15 minute a lui S89 (regula de 10 %). **S93** (jos, `aprobat`, doar procesor, NOU): examenul de română devine criteriul de decizie pentru **următoarele** experimente de română — după S92 (un singur lucru greu pe procesor o dată), sau mâine, 8 nov, de la 08:00; trebuie gata înainte de următoarea noapte pe placă (8→9). Testul pe placă al modelului mic (Spearman, scris înainte ca „S93”) devine **S94**, după S89. S88 rămâne `oprit` până scrie Adrian.

**⚠ ACUM — 7 nov 2026 (supraveghetor, 17:15):** S91 = **GATA, verificat** (unealta merge, `kronos/` neschimbat, nicio configurare existentă atinsă, 1318 teste trec). **Noaptea 7→8, placa, de la 19:00: S89** rămâne prima și neschimbată. **S92** (jos, `aprobat`, doar procesor): modul relativ în `cercetator_avans.py` + modelul mic de 6 straturi tăiat din `gpt_24.pt` — după verificarea de la 15 minute a lui S89 (regula de 10 %), sau mâine de la 08:00. S88 rămâne `oprit` până scrie Adrian.

**⚠ ACUM — 7 nov 2026 (supraveghetor, 11:15):** S87 = **GATA, verificat — P1 DA, P2 DA** (cifrele se potrivesc cu pragurile; `gc.collect` e acum în paza de la fiecare oră). S88 = **oprit, motiv bun** (regula ta interzice ștergerea; Adrian decide: rulează el comanda sau îți dă excepția) — **nu o reîncerci** până nu scrie aici sau în hub că ai voie. **Azi ziua (procesor, oricând până la 18:30):** **S90** (C-85 pasul 3, examenul de română ca modul, nimic activat în configurări). **Noaptea 7→8, placa, de la 19:00:** **S89** — reluarea S85 (5 ore, modelul de 24 de straturi, rețeta e1 neschimbată) pe linia nouă `w2_mare_24g`, acum cu paza care golește memoria la fiecare oră. S90 poate merge în paralel cu S89 doar după verificarea de la 15 minute a lui S89 (regula de 10 % la pași/s).

**⚠ ACUM — 7 nov 2026 (supraveghetor, 08:15; COMENZI.md C-86, Adrian):** **S87** rămâne prima azi (placă, 08:00–18:30). Adrian a răspuns: S84 „**da, fără gpt.pt de linie**” și „**da**” la `lucru/memorie_mare/` → **S88** (jos, `aprobat`, procesor + disc): ștergerea celor 82 de modele intermediare (~33,4 GB) cu SHA + scor scrise înainte, apoi `lucru/memorie_mare/` **doar după ce S87 e gata**. Nu în timp ce S87 e pe placă. **Stări pe 8 biți: NU** (nimic instalat). Release-ul #513 îl face Adrian luni — nu atingi `lucru/export/`.

**⚠ ACUM — 7 nov 2026 (supraveghetor, 05:15):** S86 = **GATA, verificat — DA** (Muon −649 MB). Întrebarea „crește memoria de la o oră la alta?” a rămas deschisă → **S87** (jos, `aprobat`, placă ~1–1,5 h), **ziua de 7 nov, 08:00–18:30**, nimic pe placă dacă Adrian e la workstation. Nicio linie de 24 de straturi repornită până după S87. **Nimic nu se șterge** (nici `lucru/memorie_mare/`) până răspunde Adrian.

**⚠ ACUM — 7 nov 2026 (supraveghetor, 02:15):** S85 = **OPRIT/NEMĂSURAT, verificat — corect** (ora 3 iar out of memory la testul rapid, ca la S77c). Placa e liberă tot restul nopții. **Ordinea acum:** **S83b** (procesor) **imediat**; **S86** (C-85 pasul 2, cu pasul nou 3b: de ce crește memoria de la o oră la alta) **în paralel, tot în noaptea asta** — partea pe placă pornește cel târziu la 05:30 și e gata până la 07:00, altfel ziua de la 08:00. Nicio linie de 24 de straturi repornită până după S86. **Nimic nu se șterge** până răspunde Adrian la S84.

**⚠ ACUM — 6 nov 2026 (supraveghetor, 23:15):** S77e = **GATA, verificat** (e1 ȚINE, e2 AJUTĂ PUȚIN — cifrele se potrivesc cu pragurile). S84 = **GATA, verificat** (nimic șters). S83 = **oprit, motiv bun** (−32 octeți doar din antet) → reluarea e **S83b** (accept mărimea reală). **Ordinea în noaptea asta:** **S85** pe placă ACUM (5 ore pe rețeta e1, pornire **cel târziu 00:30**); **S83b** pe procesor **după ce S85 a trecut verificarea de la 15 minute** (regula de 10 % la pașii/s), sau imediat dacă S85 nu pornește. Mâine ziua (7 nov, 08:00–18:30): **S86** (C-85 pasul 2, memoria plăcii la modelul mare, măsurare scurtă), după ce S85 e `gata`/`oprit`. **Nimic nu se șterge** până răspunde Adrian la S84.

**⚠ ACUM — 6 nov 2026 (supraveghetor, 20:15; COMENZI.md C-82 și C-85, Adrian):** S77e rulează (de la 19:00) — **nu-l întrerupi.** S82 = **GATA, verificat**. Adrian a spus **„Da 513”** (C-82) și **„Da” la C-85** (modulele cresc odată cu modelul). Am pus jos **S83** (C-82: #513 devine modelul în uz, doar procesor) și **S84** (C-85 pasul 1: lista punctelor de salvare `.pt`, doar citire, nimic șters). **Ordinea: S77e → S83 → S84**, fiecare pornește doar după ce cea dinainte e `gata`/`oprit` (în noaptea asta, după S77e, sau mâine de la 08:00). Pașii 2–8 din C-85 îi pun eu, câte unul, după ce S84 e gata.

**⚠ ACUM — 6 nov 2026 (supraveghetor, 17:15; COMENZI.md C-80 și C-81, Adrian):** Adrian **a plecat de la workstation la ~15:20 fără testul OS** — calculatorul n-a fost repornit, a rămas în Windows, **placa e liberă**. Înainte să plece **a șters** (spune el) cele două foldere „test ai brain” și probabil arhiva `cyberspace_mutare`. **Fă ACUM S82** (jos, `aprobat`, doar citire, ~15 min): ce a mai rămas din grupurile A/B, spațiul pe C:, Coșul de reciclare → 3 rânduri sus în `plan/pentru_adrian.md`; nu ștergi nimic, nici Coșul. **S77e rămâne la noapte, pornire de la 19:00 (cel târziu 21:00)** — ziua nu mai ajunge până la 18:30 pentru ~2,5 h. Testul OS al lui Adrian se mută la următoarea lui fereastră (îți scriu eu dacă e una).

**⚠ ACUM — 6 nov 2026 (supraveghetor, 11:15; COMENZI.md C-79, Adrian):** Adrian e la workstation de la ~08:30 pentru testul OS (repornire în Cyber Universe, `os-250`/`os-251`) — **nimic pe placă cât e el acolo.** S76c = **GATA, verificat** (URMEAZĂ, la limită). **S77d** a pornit la 10:00 (tu nu vedeai C-79 — nu e vina ta) și a fost închis la 10:22, cel mai probabil de repornirea lui Adrian → OPRIT/NEMĂSURAT corect, nimic stricat. **Reluarea = S77e** (jos, sub S77d, `aprobat`): linii noi `w2_mare_24e1`/`_24e2`, deci **nu atingi și nu ștergi** `lucru/w2_mare_24d1/`. **Fereastra S77e: noaptea 6→7, pornire de la 19:00** (cel târziu 21:00). Ziua o mut eu mai devreme doar dacă la 14:15 / 17:15 scrie aici că Adrian a terminat. Discul C: are acum ~106 GB liberi → testul de disc trece din nou; regula „1 test pică din cauza discului” nu se mai aplică (orice test picat = regula obișnuită).

**⚠ ACUM — 6 nov 2026 (supraveghetor, 02:15):** S77c verificat: **OPRIT/NEMĂSURAT corect** (out of memory la ora 3, doar 2 ore; nimic repornit — corect). **Discul C: are 34 GB liberi (sub 40 GB)** → testul `test_unealta_cap_coada_fara_excluse_si_fara_validare_la_antrenare` pică din cauza discului, nu a codului. **Până când Adrian face loc:** dacă ACESTA e singurul test picat (1 picat, restul trec), îl scrii în raport și în coadă ca „1 test pică doar din cauza discului (cunoscut, 6 nov)” și poți marca sarcina `gata`; orice alt test picat → regula obișnuită. Nu ștergi nimic, nu schimbi pragul de 40 GB. **Ordinea:** noaptea asta (placa liberă) **S78 → S79** (procesor + disc; S79 e cea mai urgentă pentru Adrian, care e la workstation pe la 08:30 — raportul de spațiu trebuie să fie gata până atunci dacă se poate). Ziua de 6 nov: **S81** (reparația codului de ieșire, procesor, ~30 min) → **S77d** (placa, ~2,5 h: de ce strică modelul mare în prima oră — două rate mai mici); **S76c** (procesor) poate merge în paralel cu S77d. Nimic pe placă cât Adrian lucrează la workstation. Noaptea 6→7: o scriu eu la 17:15 / 20:15, după cifrele S77d.

**⚠ ACUM — 5 nov 2026 (supraveghetor, 09:05; COMENZI.md C-73, Adrian — PRELUNGIT la 08:59):** fereastra lui Adrian pe workstation e acum **~08:30–~14:00**: **nimic pe placă și nimic lung pe procesor până la 14:00**; dacă rulează ceva, se oprește curat. **S77a** (jos, `aprobat`) pornește **doar după 14:00** și are prioritate (cifrele ei trebuie gata până la **18:30**, pentru noaptea S77b). **S76c** vine după S77a doar dacă se poate termina până la 18:30; altfel se mută pe **ziua de 6 nov** (nu încarcă procesorul peste noaptea S77b). S76b = AJUTĂ (verificat). **11:15:** nimic schimbat — fereastra lui Adrian continuă, nimic nu rulează; S77a rămâne pentru după 14:00. **13:45 — comenzi noi de la Adrian:** **S78** (C-77, salvarea „Mini Brain”) și **S79** (C-76, raportul de spațiu) — doar procesor și disc, **nimic șters**; ordinea după 14:00: **S77a → S78 → S79**; S76c pe 6 nov de la 08:00 dacă nu apucă azi. S78/S79 pot continua noaptea, fără să încetinească S77b. **14:20 — C-78:** Adrian a reînnoit autentificarea Claude Code pe workstation (`claude auth login`, „Login successful”). Fereastra lui s-a terminat → pornește **S77a** acum. Executant: dacă mai vezi în jurnal avertismentul de expirare a autentificării, scrie-l sus în `plan/pentru_adrian.md` (Adrian e la workstation pe 6 nov ~08:30). **17:15 — DEBLOCARE:** executantul a raportat la 14:29 că `cascada.py stare` dă `"liber": false` din cauza înregistrării vechi `S42_0833.json` (PID 19792 refolosit de Windows pentru `dllhost.exe`). **Fă ACUM S80** (jos, `aprobat`, repararea lui `unelte/cascada.py`, granița 6) — **nu** editezi de mână `S42_0833.json`. Imediat după S80: **S77a**, cu fereastra mutată (vezi la S77a): partea de procesor pornește imediat, măsurătorile pe placă până la 18:30 sau de la 19:00, totul gata până la **23:30**. Apoi S78 → S79 (pot merge și în timpul nopții S77b, cu regula de 10 %). S76c rămâne pe 6 nov de la 08:00. **S77b** o scriu eu la 20:15 / 23:15, după cifrele S77a. **20:15 — S77a = GATA (verificat), S77b scrisă și `aprobat` (jos, imediat sub S77a): pornește ACUM, noaptea 5→6 nov, pornire cel târziu la 00:15.** **S78 deblocat:** textul întreg al C-77 și C-76 e acum în `plan/comenzi_hub_C76_C77.md` (nu mai ai nevoie de hub); S78 e iar `aprobat` și merge după ce S77b a pornit (doar procesor + disc, regula de 10 %), apoi S79. S76c rămâne pe 6 nov de la 08:00. **23:15 — S77b a căzut după ~1 minut (out of memory, verificat: OPRIT corect). Fă ACUM S77c (sub S77b, `aprobat`): aceeași noapte cu lot 6 × `adunare_loturi = 16`, linia nouă `w2_mare_24b`, pornire cel târziu la 00:30; altfel noaptea 6→7 de la 19:00. Apoi S78 → S79 (sau imediat, dacă S77c nu pornește). S76c pe 6 nov de la 08:00.**

**Ordinea pe 21 octombrie, ziua (scrisă de supraveghetor, 21 oct 02:15):** S10 (examene scurte, placa), apoi S11 (datele
pentru noaptea 12 — trebuie `gata` până la 16:30), apoi S9 și S8 (procesor). Noaptea 21→22: S12, doar dacă scriu
„perechi verificate: da” la S11.
**Actualizare 21 oct 14:20 (supraveghetor):** S8–S11 și S13 gata. S11: „perechi verificate: da” (30/30) → **S12 pornește la
19:00**. Până atunci, pe procesor: S14 (mic, 30 de minute).
**Actualizare 21 oct 17:20 (supraveghetor):** S14 gata și verificat. Următoarea: S12 la 19:00. Ziua de 22 oct o decid după verdictul nopții 12.
**Actualizare 21 oct 23:15 (supraveghetor):** S12 gata, verificat: INFIRMAT, fără regresie. Următoarea: **S15** (examen mare de generalizare, procesor + ~15 minute pe placă), cât de curând placa e liberă — de preferat în noaptea asta, altfel prima a zilei de 22 oct. Ziua de 22 oct o decid după S15.
**Actualizare 22 oct 01:45 (Adrian, prin centrul de comandă) — DIRECȚIE NOUĂ, aprobată cu trei „da”:** S15 a ieșit (tipurile
văzute 30/30, nevăzute 6/50: „se învață, nu se transferă”). Adrian a aprobat strategia din
`docs/rapoarte/2026-10-22_0200_strategie_nucleu_fara_llm.md` (citește-o întreagă; e decizia și în hub, `DECIZII.md`):
1. **Ținta modelului se schimbă:** nu „să înțeleagă” prin mai multe ore, ci sistem cu **auto-joc cu verificator (H3) + specialiști (H4)
   + memorie (H2)**; „de top” înseamnă pe domenii cu verificator (documente în română, cod cu teste, gramatică), nu conversație liberă.
   **Nu se mai programează nopți de antrenare cu rețeta de până acum ca să crească scorul pe tipuri nevăzute.**
2. **Qwen iese din rolul de judecător** la „răspuns din text”: examenele se notează cu un verificator propriu (potrivire cu bucata
   de referință: exactă sau suprapunere de cuvinte ≥ 0,8), fără niciun model străin. Qwen rămâne, declarat, doar pentru poveștile vechi.
3. **Supraveghetor, la prima trecere:** scrii **S16 = E0** (verificatorul fără LLM + re-notarea S15 și S4 în ambele feluri; procesor,
   fără placă; `aprobat` din start, categoria „examene, notări”) și **S17 = E1** („întrebări născute de Kronos”, exact §8 din raport,
   cu baseline #415: (b2) 6/50, (e) 30/30; `propus` până S16 arată acord Qwen ↔ verificator ≥ 90 %, apoi `aprobat`, o noapte pe placă).
   Executantul face pre-înregistrarea S17 cu cifrele din §8, cuvânt cu cuvânt. Nimic din `kronos/`, examenul BPB, datele de examen sau
   paznic nu se atinge. Dacă E0 dă acord < 90 %, te oprești și scrii în `pentru_adrian.md` unde diferă — nu pornești S17.

**Actualizare 22 oct 02:15 (supraveghetor):** S15 verificat (cifrele adunate din nou pe tipuri: 6/9/6 la (b2), 14/4/30 la (e)) →
„Tipurile văzute s-au învățat, dar nu se transferă”. Am scris **S16 = E0** (`aprobat`, procesor, fără placă — se poate face chiar
acum, noaptea) și **S17 = E1** (`propus`; trece pe `aprobat` doar dacă S16 dă acord ≥ 90 %). Nicio sarcină de placă în ziua de 22 oct.
**Actualizare 22 oct 05:15 (supraveghetor):** S16 gata, verificat (527/540 = 97,6 % ≥ 90 %; adunat din nou: 234/240 + 293/300) →
**S17 trece pe `aprobat`**, pentru noaptea 22→23 (pornire 19:00). Ziua: doar pregătirea S17 pe procesor, fără placă.
---
**Actualizare 22 oct 15:10 (Adrian, prin centrul de comandă):** (1) **S17 pornește ACUM**, nu la 19:00: fereastra lui S17 e „oricând”;
executantul o pornește la prima verificare a cozii. (2) **Regulă nouă, permanentă:** workstation-ul e ținut pornit doar pentru Kronos
(Adrian îl folosește foarte rar, pentru o imprimare sau un PDF); **placa poate fi folosită oricând, ziua și noaptea**, cu aceleași
reguli (pre-înregistrare, paznic, un singur lucru pe placă). Supraveghetor: nu mai lăsa placa liberă ziua când există o sarcină
aprobată; planifică și pentru ziua următoare. Ferestrele din `REGULI_CASCADA.md` rămân ca orientare pentru raport, nu ca limită.
(3) După S17 (gata pe la ~22:00), la trecerea de 23:15 pune pe placă următorul pas (repetarea cu 3× date dacă e „neclar”, altfel E2).

**Actualizare 22 oct 23:15 (supraveghetor):** S17 gata, verificat față de pre-înregistrare: (b2) **13/50** (baseline 6/50; CONFIRMAT
cerea ≥ 16, INFIRMAT ≤ 9), (e) 29/30 ≥ 27, fără regresie, 452 de tipuri ≥ 20 → **NECLAR**. Cum a cerut Adrian la 15:10 (punctul 3),
am pus pe placă **S18 = repetarea cu 3× date** (`aprobat`, pornește la prima verificare a cozii, ~7 ore). Judecătorul rămâne
neschimbat (verificatorul din S16), ca cifrele să fie comparabile cu baseline-ul; varianta mai strictă se raportează doar alături.

**Actualizare 23 oct 05:15 (supraveghetor):** S19 gata, verificat: (c) +7 (≥ 4), dar 7 din 13 la #425 sunt răspunsuri lungi și cu
F1 ≥ 0,8 #425 are 2/50 față de 4/50 → semn slab pentru auto-joc; S17 rămâne NECLAR. Am pus **S21** (`aprobat`, doar procesor, ~1 oră):
aceeași numărătoare a răspunsurilor lungi pe TOATE examenele, ca Adrian să aleagă la S20 pe cifre. Placa rămâne liberă până la „da”-ul lui.
**Actualizare 23 oct 10:15 (Adrian, prin centrul de comandă) — PAUZĂ:** Adrian pleacă pentru câteva zile. **Kronos stă în pauză până la
întoarcerea lui:** nimic nou pe placă, nicio sarcină nouă `aprobat`. S20 rămâne `propus — necesită Adrian` (alegerea 1/2/3 vine când se
întoarce). Workstation-ul rămâne pornit în Windows. Supraveghetor: la trecerile tale doar verifici că nimic nu rulează și că placa e liberă,
scrii starea în hub („pauză”) și nu propui lucru nou pe placă; dacă executantul sau raportul de dimineață semnalează o eroare, o notezi în
`pentru_adrian.md`. Executant: nu porni nimic. Pauza se ridică doar printr-o actualizare nouă a lui Adrian.
**Actualizare 23 oct 10:20 (Adrian, prin centrul de comandă) — PAUZA SE RIDICĂ; S20 = VARIANTA 1:** Adrian pleacă, dar workstation-ul nu
trebuie să stea degeaba. Decizii:
1. **E1 se închide** cu rezultatul S17 (NECLAR, 13/50, explicat de S19/S21). S20 → `gata` cu „varianta 1, aleasă de Adrian 23 oct 10:20”.
2. **E2 e aprobat de Adrian** (strategia `docs/rapoarte/2026-10-22_0200_strategie_nucleu_fara_llm.md`, §4 H4 și §7 E2): **3 specialiști + ruter**,
   antrenați pe rând din #415 (Branch-Train-Merge), fiecare pe o familie de întrebări (propunere: (1) fapte/nume/ani/locuri, (2) da/nu,
   (3) tipurile din S11), ruter simplu (primele cuvinte ale întrebării, apoi eventual un clasificator mic). Criteriile scrise ÎNAINTE, ca în §7:
   fără regresie pe niciun specialist față de #415 pe examenele lui; suma (ruter + specialiști) ≥ monolitul #415 pe S4 + S15 + noaptea 10;
   ruterul alege corect ≥ 90 %. Supraveghetor: scrii sarcinile (S22…) cu pre-înregistrare, câte una pe placă, ca de obicei; categoria e
   „antrenare nouă”, aprobată acum de Adrian pentru tot E2, cu bugetul: cel mult o sarcină grea pe placă odată, nopți și zile, fără date noi
   descărcate (doar ce există deja) și fără modificări în `kronos/`, examenul BPB, paznic sau datele de examen.
3. **Lucru cât e Adrian plecat (câteva zile):** după E2, dacă rămâne timp: **pregătirea E3 (memoria) doar pe procesor** — indexul propriu peste
   articolele deja descărcate și măsurarea lui; fără antrenare E3 până nu decide Adrian. Dacă ceva pică de 2 ori la rând (aceeași eroare),
   oprești lucrul pe placă și scrii în `pentru_adrian.md`.
4. **Fereastra pentru OS/GPU:** când se întoarce, Adrian va avea nevoie de workstation ~30–60 min (pornire de pe stick). Atunci executantul nu
   pornește nimic nou; o sarcină în curs se poate opri doar cu checkpoint (dacă nu are, se așteaptă sfârșitul ei). Notează în fiecare raport
   până când ține sarcina curentă de pe placă, ca Adrian să-și aleagă momentul.

**Actualizare 23 oct 10:30 (supraveghetor) — E2 pornește:** am citit decizia de la 10:20. S20 e `gata` (varianta 1). Am scris
**S22** (`aprobat`, doar procesor, ~2 ore: împărțirea datelor pe 3 familii, ruterul, măsurarea ruterului, configurările, pre-înregistrarea
E2) și **S23** (`aprobat`, placa, ~7 ore: cei 3 specialiști antrenați pe rând din #415 + examenele + nota sistemului). S23 pornește doar
după ce S22 e `gata`, pre-înregistrarea E2 e urcată și ruterul a trecut poarta de la S22. Aprobate de Adrian (10:20, punctul 2: E2 = „antrenare
nouă”, tot E2) + supraveghetor. Pregătirea E3 (indexul de memorie, procesor) o scriu după verdictul E2. Executant: în fiecare raport
scrii până când ține sarcina de pe placă (punctul 4 al lui Adrian).
**Actualizare 23 oct 11:15 (supraveghetor):** S22 gata, verificat față de sarcină: familiile 20.564 + 4.083 + 2.821 = 27.468 ✓;
ruterul ajustat doar pe validare (1–5 cuvinte, prag 2: 93,7 %), apoi o singură rulare pe examene: **189/210 = 90,0 % → poarta trece, la
limită**; baseline-ul #415 pe familii 101 + 13 + 30 = 144 ✓; 900 teste trec. Pragul val_bpb ≤ 0,4511 (#415 + 0,01), propus de executant,
îl accept (e fixat înainte de pornire, la fel de strict ca toleranța „minus 1” de la (A)). **S23 rulează de la ~11:05, sfârșit estimat
~18:10** (cel târziu ~19:05). Nimic nou în coadă acum: pregătirea E3 (procesor) o scriu după verdictul E2, la trecerea de 20:15.
**Actualizare 23 oct 20:15 (supraveghetor) — E2 INFIRMAT, verificat; trec la pregătirea E3 (doar procesor):** S23 `gata`, verificat față
de pre-înregistrare cu cifrele din raport adunate din nou: #415 6+30+11+2+13+12+50+20 = 144 ✓; sistemul 8+23+9+1+15+11+50+20 = 137 ✓
(pe familii 99+15+23 = 137 ✓); ruter perfect 98+14+30 = 142 ✓. (A) cade: F1 **98/165 < 100**; (B) cade: **137 < 144** (și 142 < 144 cu ruter
perfect); (C) 90,0 % ✓; validările toate în praguri (fapte noi F3 = 65, exact la limită) → **INFIRMAT**, corect. Lecția: specialiștii uită repede
tot ce nu e familia lor, iar câștigul pe da/nu (+1) nu acoperă pierderea pe F1 (−3). Placa a stat sub 6.455 MB și 64 °C. **E2 se închide**; nu pun
altă variantă de specialiști fără Adrian. Cum a decis Adrian (10:20, punctul 3), am scris **S24 = pregătirea E3** (`aprobat`, doar procesor, fără
placă, fără antrenare). **Placa rămâne liberă** în noaptea 23→24: E3 cu antrenare și orice altă rulare pe placă așteaptă „da”-ul lui Adrian.
**Actualizare 23 oct 23:15 (supraveghetor) — S24 verificat; S25 = căutarea mai bună (doar procesor):** S24 `gata`, verificat cu cifrele
din raport adunate din nou: k = 1: 33+19+8+12+31 = **103/160** ✓; k = 5: 41+24+10+14+40 = **129/160 = 80,6 %** ✓; k = 20: 47+27+12+14+48 = **148** ✓;
articolul la 5: 42+26+10+13+44 = **135 = 84,4 %** ✓. Așteptările au fost urcate înainte de examene (4a9fb68, 20:59; examenele ~21:05) ✓;
5 variante încercate doar pe validare (≤ 6) ✓; 904 teste trec. Față de pragul propus de executant (≥ 80 % și ≥ 85 %, nedecis de Adrian):
(i) trece la limită, (ii) **cade cu o întrebare**. Am pus **S25** (`aprobat`, doar procesor, ~2 ore): îmbunătățirea căutării, pasul 1 din
propunerea executantului — tot pregătirea E3 pe procesor (Adrian 10:20, punctul 3), fără antrenare. **Placa rămâne liberă**; E3 cu antrenare așteaptă „da”-ul lui Adrian.
**Actualizare 24 oct 02:15 (supraveghetor) — S25 verificat; S26 = un examen nou, neatins (doar procesor):** S25 `gata`, verificat cu cifrele
din raport adunate din nou: validarea nouă (2048) k = 5: aleasa 424/500 = 84,8 % față de S24 423/500 = 84,6 % → **+0,2 puncte < 3** → după pragul
meu scris înainte, **NU e câștig real** (verdictul executantului e corect). Împreună 417+424 = 841 ✓, S24 410+423 = 833 ✓. Examene: k = 1 37+21+8+12+30 = 108 ✓;
k = 5 46+25+12+14+42 = **139/160 = 86,9 %** ✓; k = 20 49+27+15+14+48 = 153 ✓; (ii) 46+27+12+14+46 = **145 = 90,6 %** ✓ — umflate (ideile au venit din
greșelile de pe examene). Așteptările urcate înainte de examene (64d9b48, 23:59; examenele 00:00) ✓; S24 refăcut exact ✓; 0 stricate; 907 teste trec.
Fiindcă cele 160 de întrebări au fost folosite de două ori de căutare, am pus **S26** (`aprobat`, doar procesor, ~1 oră): un examen E3 nou de 100 de
întrebări neatinse (punctul 3 din propunerea executantului), măsurat o singură dată, plus „primele 3 bucăți” (plafonul pentru E3 cu model).
**S27 = E3 cu antrenare pe placă: `propus — necesită Adrian`** (pragul și pornirea le decide el). **Placa rămâne liberă.**
**Actualizare 24 oct 04:05 (Adrian, prin centrul de comandă) — PAUZĂ PÂNĂ LUNI (26 oct) + OPRIREA WORKSTATION-ULUI:** Adrian se întoarce luni.
Nicio sarcină nouă pe placă sau pe procesor până atunci; S27 rămâne `propus — necesită Adrian`. Supraveghetorul e oprit până luni.
Executant: faci **S28** (mai jos) la prima verificare a cozii, apoi nimic altceva.
**Actualizare 26 oct 16:10 (Adrian, prin centrul de comandă) — PAUZA SE RIDICĂ:** Adrian s-a întors; Kronos lucrează din nou, zi și noapte
(regula din 22 oct 15:10). **S27 e aprobat de Adrian** cu criteriile propuse: confirmat dacă sistemul răspunde corect la ≥ 60 % fără text dat și nu
pierde mai mult de 2 puncte pe noaptea 10 / S4 cu textul dat; infirmat sub 45 %. Pre-înregistrarea se scrie înainte de pornire, ca de obicei.
Supraveghetorul e repornit. Fereastra OS/GPU pe workstation (~30–60 min, cu Adrian) se alege între două sarcini; o anunță centrul de comandă.

**Actualizare 26 oct 16:15 (supraveghetor) — repornit; S26 verificat; S27 scris în pași exacți:** S26 `gata`, verificat cu cifrele din raport
adunate din nou pe tipuri: k = 5 38+14+6+6+3+13 = **80/100** ✓; k = 3 32+14+6+6+1+13 = **72/100** ✓; 86,9 − 80,0 = **6,9 ≥ 5** → după regula scrisă
înainte, **cifrele de pe cele 160 erau umflate** (verdictul executantului e corect; și față de validarea 2048 e −4,8, cam o abatere — o parte e noroc).
Cifra oficială a căutării: **80 % la k = 5**, plafonul pentru E3 cu model: **72 % la k = 3**. Atenție la pragul S27: ≥ 60 % cere ca modelul să răspundă
corect în ~83 % din cazurile în care răspunsul e în cele 3 bucăți. S27 rămâne `aprobat` (Adrian, 16:10); mai jos am completat instrucțiunile exacte.
Nicio altă sarcină pe placă până la verdictul S27.

**Actualizare 26 oct 17:15 (supraveghetor):** S27 pornit corect — pre-înregistrarea urcată înainte de antrenare (7f756ef 16:51, pornire 16:52).
Abaterea „de obicei 2 bucăți în 512, nu 3” e scrisă în pre-înregistrare înainte de pornire, cu aceeași regulă la antrenare și la examen, fără să
depindă de răspuns, iar pragul lui Adrian rămâne neschimbat → acceptată. Plafonul real (răspunsul în bucățile chiar date) se numără după examen.
Verdictul îl verific după raport. Tot nicio altă sarcină pe placă până atunci.

**Actualizare 26 oct 20:15 (supraveghetor) — comanda C-21 a lui Adrian (Cyber Hub) pusă în coadă, DUPĂ S27:** S27 încă rulează (fără commit
nou de la 16:52, normal în timpul antrenării; placa ocupată până pe la ~20:45). Comanda C-21 (Adrian, 26 oct 17:45, prin centrul de comandă;
`studiu/2026-10-26_open-source/kronos.md` §3 din hub) e împărțită în **S29 → S30 → S31 → S32**, în ordinea asta, fiecare pornește **doar după ce
cea de dinainte e `gata`** și S27 e `gata` cu verdictul scris. Nu întrerupe S27. Fiecare are pre-înregistrare urcată înainte de pornire.

**Actualizare 26 oct 23:15 (supraveghetor) — S27 verificat: CONFIRMAT la limită; S29 repornit cu setul S26:** S27 `gata`, verificat față de
pre-înregistrare (7f756ef, 16:51, urcată înainte de antrenarea de la 16:52 ✓): (a) 60/64 + 0/36 = **60/100 ≥ 60** ✓; noaptea 10 **69 ≥ 70 − 2 = 68** ✓;
S4 **39 ≥ 38 − 2 = 36** ✓; placa ≤ 5.374 MB → **CONFIRMAT, la limită** (o întrebare mai puțin = NECLAR). Citirea: #415 fără antrenare face 57 →
antrenarea a adus doar +3; câștigul vine din căutare. S29 `oprit` la pasul 4 (setul 8192 imposibil: rămân 14 întrebări) → am ales **varianta 1**
(setul decisiv = cele 100 S26; pragul C-21 neschimbat) și am trecut S29 pe `aprobat` pentru pașii 5–7 (sub o oră). Incidentul plăcii de la 21:47
(7.942 MB, oprit de paznic în câteva secunde, reparat, a doua rulare ≤ 1.500 MB) e notat; nu se repetă. Apoi S30 → S31 → S32, ca până acum.

**Actualizare 27 oct 02:15 (supraveghetor) — S29 verificat: CONFIRMAT; S30 gata; S31 rulează; S33 nou, înaintea lui S32:** S29: pre-înregistrarea
c381094 (23:35:21) urcată înainte de măsurarea de la 23:35:30 ✓; Δ3 = 83 − 72 = **+11 ≥ +5** ✓, k = 20: 95 ≥ 94 ✓ → **CONFIRMAT** (efectul real e
probabil mai mic: validarea a dat +1,2; câștigul e la definiții, aproape tot din reordonare). S30 `gata` (5.917 MB, 64 °C, 946 teste). S31 `in_lucru`
din ~01:00 (pre-înregistrarea ccc947d 01:01, înaintea antrenării ✓), sfârșit estimat ~05:50. **S33** (scurtă: procesor + < 1 oră pe placă, ziua 27 oct)
se face **după S31 și ÎNAINTEA lui S32**, ca placa să nu stea degeaba ziua (S32 e doar procesor, ~2 zile).

**Actualizare 27 oct 08:15 (supraveghetor) — S31 verificat: INFIRMAT; S34 nou (proba de control a rețetei A), între S33 și S32:** S31: pre-înregistrarea
ccc947d (01:01:05) urcată înainte de antrenarea de la 01:01:14 ✓; română curat B 1,3019 ≥ A 1,2332 → **INFIRMAT** ✓ (plus regresii la B: TinyStories R2
+0,032, cod +0,058, fapte noi −3). Placa ≤ 5.374 MB, cod 0 la toți pașii, 946 teste trec. **Muon se închide** (altă încercare Muon doar cu Adrian).
Surpriza: A (AdamW + adunare pe 8 loturi + răcire 25 %) a coborât la **1,2332** față de #415 1,2858. Dar A a avut și **2 ore în plus** de antrenare, deci nu
știm dacă câștigul vine din rețetă sau doar din ore. Am pus **S34** (granițele 1 și 2: încă o rulare pe linia w2, aceeași rețetă ca #415): aceleași 2 ore
din #415, cu rețeta veche, ca reper. Ordinea: **S33 (ziua) → S34 (oricând, imediat după S33) → S32 (procesor)**.

**Actualizare 27 oct 11:15 (supraveghetor) — S33 verificat: CONFIRMAT la limită; S34 rulează; S35 nou (citirea pe validare), între S34 și S32:**
S33: pre-înregistrarea 0fab1b8 (08:31:38, antetul corectat în 918a3a0 la 08:31:51) urcată înainte de examenul de la 08:31:58 ✓; în aceeași rulare
`s25` **60** (reperul S27 reprodus la 100/100) și `rrf_reord` **66** → Δ = **+6 ≥ +5** → **CONFIRMAT** ✓ (15 reparate / 9 stricate; câștigul din definiții
23 → 30 din 54; „rest” 18 → 16). Placa 732 MB, 950 teste trec (o picare de conexiune la `test_interfata`, trece la reluare — de urmărit). S34 `in_lucru`
din 09:00:52 (pre-înregistrarea 46951db la 09:00:45, înaintea pornirii ✓). Ca placa să nu stea goală cât merge S32 (doar procesor, ~2 zile), am pus **S35**
(granița 2, doar examen, < 1 oră pe placă): aflăm cât din +6 e de la amestecul S26, măsurând citirea pe eșantionul 2048 al validării (nevăzut de #438).
Ordinea: **S34 → S35 → S32**. Noaptea 27→28 o decid la 17:15/20:15, după verdictul S34.

**Actualizare 27 oct 14:15 (supraveghetor) — S34, S35, S32 verificate; S36 nou (proba D: doar răcirea), apoi S37 (fp32 în float64, procesor):**
S34: pre-înregistrarea 46951db (09:00:45) înaintea pornirii (09:00:52) ✓; C #447 **1,2903**, A #441 re-măsurat **1,2332** → Δ = **+0,0571 ≥ 0,010** →
**CONFIRMAT** ✓ (C chiar puțin mai slab decât #415: 1,2903 față de 1,2858; A mai bun pe toate validările). S35: pre-înregistrarea 14cd40e (12:36:17) înaintea examenului
(12:36:26) ✓; pe 2048 (0 din 500 văzute de #438) `s25` **331**, `rrf_reord` **336** → Δ = 5/500 = **+1,0 punct**, între +0,5 și +2,0 → **NECLAR** ✓
(definiții +18, regizat +6, „rest” −17). S32: pragurile 2903257 (13:39:03) înaintea măsurării (13:39:47) ✓; fp32 dif. maximă **1,335e-4 > 1e-4** →
**NU TRECE** ✓ (argmax și textul identice, bpb +0,0000005); Q8_0 **+0,0000187 ≤ 0,005** → **TRECE** ✓. 960 teste trec. C-21 e acum închisă (S29–S32).
Pun: **S36** (granițele 1 și 2, ~2,2 ore pe placă, pornește acum): proba D = rețeta A fără adunarea pe 8 loturi — aflăm dacă răcirea singură aduce câștigul;
apoi **S37** (granița 6, doar procesor): motorul S32 adună în float64 la LayerNorm/softmax și se remăsoară o dată, cu același prag 1e-4.
**FEREASTRĂ OS/GPU pe workstation — 28 oct, de la ~10:05 până pe la ~12:00 (Adrian e de față, prin centrul de comandă):** workstation-ul se
repornește în Cyber Universe OS (de pe stick). Executantul nu pornește **nicio sarcină nouă de placă** până după fereastră. O sarcină de procesor
întreruptă de repornire (ex. S41) se reia normal la prima rulare după ce Windows revine.

**Actualizare 27 oct 23:50 (centrul de comandă, prin delegarea lui Adrian din 26 oct 17:45) — răspunsuri la întrebările mici:**
(1) Pragul motorului fără PyTorch: verdictele S32/S37 rămân cum au fost măsurate (NU TRECE la F32); pentru **testele viitoare** se folosește un
prag relativ, scris înainte de măsurare (propunerea executantului din raportul S37), plus condiția „argmax și textul identice”. Q8_0 rămâne formatul de lucru.
(2) Raportul de dimineață rămâne la ora de acum (06:40). (3) S28 (oprirea workstation-ului) se închide ca `anulat — nu mai e nevoie`.
(4) **Porturile `cautare` și `inferenta` în `kronos/` (nucleu): APROBATE de Adrian** („Da”, 27 oct 23:49, prin centrul de comandă) — doar cele două
porturi + contractele lor, fără alte schimbări în `kronos/`; `teste/test_arhitectura.py` și toate testele trebuie să treacă; se face pe procesor, fără să încurce S38.

**S38** (continuarea liniei w2 cu rețeta A, din #441, o noapte): `aprobat` (Adrian, 27 oct 18:00, prin centrul de comandă — delegarea din 26 oct 17:45: aprobă ce se potrivește direcției).
„Reordonarea doar la definiții” (propunerea S35) cere întâi un set nou de întrebări — o las pentru o trecere următoare.
**Actualizare 27 oct 20:15 (supraveghetor) — S36 și S37 verificate; S38 rulează (noaptea 27→28):**
S36: pre-înregistrarea 9729c73 (15:00:44) înaintea pornirii (15:00:54) ✓; D #451 **1,2520**, A #441 re-măsurat **1,2332** → Δ = **+0,0188**, între 0,010 și 0,040 →
**NECLAR** ✓ (D păstrează ~67 % din câștigul A față de C; placa ≤ 5.991 MB, 63 °C). S37: pragul 5b03138 (18:00:17) înaintea măsurării (18:00:25) ✓; fp32 dif. maximă
**1,364e-4 > 1e-4** → **NU TRECE** ✓ (float64 la LayerNorm/softmax nu ajută; argmax și textul identice); 961 teste trec. Pragul fp32 (relativ sau nu) rămâne la Adrian.
**S38** rulează cu rețeta A (corect, fiindcă S36 a dat NECLAR), pre-înregistrarea 61c3c7d (19:34:14) urcată, pragurile identice cu cele din coadă; sfârșit estimat ~01:55.
Ziua de 28 oct o decid după verdictul S38 (de ex. proba E „fără adunare, rată mai mare”, propusă la S36), nu acum.
**Actualizare 28 oct 02:15 (supraveghetor) — S38 încă fără raport; S40 (porturile aprobate de Adrian) și S41 (C-28, etapa 1a) puse în coadă, doar procesor:**
S38 trebuia să se termine pe la ~01:55; raportul nu e încă urcat (executantul scrie abia la final) — îl verific la 05:15. S39 (C-24) e tot `aprobat`, nimic urcat încă.
Am copiat eu în hub `integrare/kronos/format_greutati.md` (doar specificația, ca sesiunea OS să poată începe); vectorii și `MODEL.md` vin după S39.
Pun: **S40** (porturile `cautare` și `inferenta` în `kronos/`, cu „da”-ul lui Adrian din 27 oct 23:49; doar ele + contractele + două module-adaptor) și
**S41** (C-28 E4 Kronos-Cod, **doar etapa 1a**: lista surselor + licențe, examenul de cod scris înainte, cutia izolată; fără descărcări, fără placă).
Ordinea pe procesor: **S39 → S40 → S41**. Placa pentru ziua de 28 oct o decid la 05:15, după verdictul S38.

**Actualizare 28 oct 08:20 (supraveghetor) — S38 verificat: CONFIRMAT; S39 gata (Release la Adrian); S40 oprit (pasul din `kronos/` cere om de față); S42 nou pe placă:**
S38: pre-înregistrarea 61c3c7d (19:34:14) înaintea pornirii ✓; #459 română curat **1,2162 ≤ 1,2232** → **CONFIRMAT** ✓; cod curat 0,7321 (#441 0,7460) și R2 0,4084
(#441 0,4154): ambele mai bune, fără regresie ✓; placa ≤ 6.002 MB, 64 °C. Tăcerea de azi-noapte = workstation-ul fără internet ~01:00–06:01 (11 rulări picate), REZOLVAT.
S39: vectorii verificați de mine (SHA-256 identice cu raportul), copiați în hub cu README și MODEL; Release-ul #459 îl face Adrian (`gh` cere aprobare).
S40: corect oprit — executantul n-are voie în `kronos/`. Împărțit: **S40a** (doar `kronos/contracte.py`) = o sesiune cu Adrian de față; **S40b** (modulele + testele) = executantul, după S40a.
**S41 nu depinde de S40** → poate porni. Pun **S42** pe placă (ziua 28 oct, ~4 ore): cititorul E3 refăcut din cel mai bun model (#459) cu rețeta A.
**Ordinea pentru executant: întâi S42 (placa; pre-înregistrarea înainte), apoi S41 (procesor) la rularea următoare, cât merge S42.**

**Actualizare 28 oct 23:15 (supraveghetor) — S42 verificat: INFIRMAT; urmează S43a (procesor), apoi S44 (bucăți tăiate pe propoziții, examen scurt pe placă):**
S42: pre-înregistrarea E3_reteta_A2 urcată înainte de pornire (df7eb34, 19:00) ✓; pornit din #459 ✓; (a) S26 `rrf_reord` #466 66 / #438 66 → **Δ 0 ≤ +1 → INFIRMAT** ✓
(în plus S4 −3, peste cele 2 permise); română curat 1,2148 (fără stricăciune); placa ≤ 5.374 MB; 1003 teste trec. Cititorul rămâne **#438**; nu mai repetăm „alt model / altă rețetă” pe E3.
Pre-înregistrarea veche E3_reteta_A rămâne deschisă, fără măsurare (unealta nu are „înlocuită”) — acceptat.
**Ordinea pentru executant: întâi S43a (procesor, fără rețea), apoi S44 (procesor + sub 1 oră pe placă; pre-înregistrarea înainte).**

**Actualizare 29 oct 02:15 (supraveghetor) — S44 verificat: INFIRMAT; S43a verificat; pilotul S43 trece pe `aprobat` (procesor + rețea); S45 propus pentru Adrian:**
S44: pre-înregistrarea urcată înainte de examen (32ce496, 00:03:16; examenul 00:03:26) ✓; 2048: întregi 169+36+10+15+106 = **336** ✓, tăiate 148+18+13+16+102 = **297** ✓
(din 252+45+21+23+159 = 500 ✓); Δ = 59,4 − 67,2 = **−7,8 < +0,5 → INFIRMAT** ✓; reparate 35 − stricate 74 = −39 ✓; brațul `intregi` = 336, identic cu S35 ✓; placa ≤ 734 MB.
Lecția: răspunsul stă des în propoziții fără cuvinte din întrebare (la „născut” jumătate pierdute). **Tăierea pe propoziții se închide**; nu pun varianta „cu vecinii”.
S43a: unealta citită de mine (data-limită strictă `< 29 iunie 2021 00:00 UTC`, oprire sub 40 GB înaintea fiecărui pachet, ritm pe gazdă, arhive doar în memorie);
cele 48 de teste ale ei trec și în cloud, fără rețea ✓. Accept data „înainte de 29 iunie” (mai strict cu o zi). **S43 = doar pilotul, `aprobat`** (pe „da”-ul lui Adrian din 28 oct 18:00).
Placa: nimic în granițele mele care să merite o oră acum (E3: „alt model”, „altă rețetă” și „tăierea” sunt închise). **S45** (încă o noapte pe linia w2 din #459, rețeta A) = `propus — necesită Adrian`
(direcția din 22 oct: nopți de antrenare doar cu „da”-ul lui). **Ordinea pentru executant: S43 (pilotul, procesor + rețea), apoi nimic pe placă până la „da”.**

**Actualizare 29 oct 14:35 (supraveghetor) — S47 verificat: bun; S48 poate porni acum (procesor); S45 rămâne diseară de la 19:00:**
S47: regulile (toleranța |Δ logit| ≤ 1e-3, regula „cea mai rapidă”) urcate înainte de măsurare (e9c20a1, 10:38; măsurarea oficială 11:08–11:39) ✓; prima încercare
oprită fără `s47.json`, deci nu se numără ✓; toate 9 combinațiile acceptate (Δ ≤ 3,3·10⁻⁶) ✓; 3,382 / 2,471 = **1,37×** ✓; împrăștieri 0,6 % și 15,7 % ✓;
profilul 1200+568+510+326+252+231+90+52+3+1,6 = 3.233 ms ✓, înmulțirile 2.368 / 3.233 = **73,2 %** ✓; la_pas 43.240 / 50.174 = 86,2 % ✓; 1080 teste trec. Reglajul pentru
S48 pe workstation: `referinta`, 1 fir (diferența față de 4 fire e mică; S48 o poate re-măsura o dată, cu regula scrisă înainte). **Ordinea: S48 (procesor) acum → S45 la 19:00 pe placă → S49 după S45, cu placa liberă.** S46 așteaptă „da”-ul lui Adrian.

**Actualizare 29 oct 21:50 (supraveghetor) — „da S46” de la Adrian (C-43): descărcarea codului poate porni; S45 continuă neatins; S50 după S45 ȘI după bucata de noapte a S46:**
Adrian a scris „da s46” (21:46, comanda C-43 din hub); centrul de comandă a trecut S46 pe `aprobat` cu „aprobat de: Adrian, 29 oct 21:46” — exact ce cerea oprirea din 08:34 ✓.
Am preluat C-43 în hub (→ S46). **Executant:** S46 pornește la prima verificare a cozii, cu comanda exactă din sarcină (`--limita-ore 10`), în paralel cu S45 (S46 nu folosește placa).
Nu opri și nu încetini S45. Raport după fiecare bucată (GB curat, simboluri, spațiul liber pe C:, erori de rețea). **S50 se măsoară doar când nici S45, nici S46 nu rulează**
(descărcarea și curățarea încarcă procesorul și ar strica timpii „cald/rece”); dacă bucata S46 ține până dimineață, S50 vine după ea, în aceeași zi. Tokenizerul pe cod: tot al doilea „da”.

**Actualizare 29 oct 23:15 (supraveghetor) — S45 merge (ora 3/6, #471 păstrat, val_bpb 0,4150); S46 pornește DUPĂ S45, nu în paralel:**
Executantul nu a pornit S46 la 22:59 (raport `2026-10-29_2259_S46_nepornit_S45_in_lucru.md`): instrucțiunea lui fixă spune „o singură sarcină `in_lucru` odată”, iar nota mea nu o poate schimba — corect, îl las așa.
**Ordinea rămâne: S45 (sfârșit ~01:25) → S46 bucata 1 (`--limita-ore 10`, de la ~02:00 la ~12:00, fără placă) → S50 după bucata S46.** Placa: 6.116 MB, 64 °C la 22:12 ✓. Verdictul S45 îl verific la 02:15.

**Actualizare 30 oct 02:15 (supraveghetor) — S45 a căzut la 23:09 (ora 4/6), fără verdict; o repet curat ca S51; S46 rulează:**
S45: procesul a căzut fără eroare și fără cod de ieșire (raport `2026-10-29_2334_S45_oprit_cadere.md`); placa era în limite (6.116 MB, 64 °C), deci nu e paznicul.
Am ales varianta 3 a executantului: **S45 se închide fără verdict** (pre-înregistrarea `reteta_A_cont2` se închide ca „întreruptă la ora 4/6, fără verdict”, la pornirea S51).
Nu reluăm din #471 (ar fi alt experiment: optimizatorul și rata pornesc de la capăt) și nu notăm #471 (n-a fost pre-înregistrat așa).
**S51 = aceeași întrebare, de la capăt din #459, pe linie nouă `w2_reteta_A_cont3`, aceleași praguri** (granița 1, aprobat de mine).
**Ordinea: S46 bucata 1 (in_lucru de la 00:30, ~10:30) → S50 (procesor, ~1–2 ore) → S46 bucata 2 (`--limita-ore 10`, neschimbat) → S51 imediat după, doar dacă poate porni până la 00:00 (altfel în noaptea următoare, de la 19:00); apoi S46 bucata 3.**
Cauza căderii (repornire Windows? oprire de mână?) o întreb pe Adrian în `pentru_adrian.md`.

**Actualizare 30 oct 11:15 (supraveghetor) — S46 bucata 1 gata (cod 0, oprită curat la 10 ore; 3,73 GB cod curat, ~1,07 mld simboluri); ORDINEA DE DISEARĂ SCHIMBATĂ: S51 întâi, apoi S46 bucata 2:**
Verificat raportul `2026-10-30_1103_S46_bucata1.md`: cifrele se adună (15,55 GB trași, 9,89 GB arhive păstrate, cod curat 3,73 GB ≈ 1,07 mld simboluri la 3,5 o/simbol), C: 68,9 GB liberi (> 40 GB), `terminat`: false, 1113 teste trec, 1 sărit — **bun**.
Cu ordinea veche, bucata 2 (19:00 → ~05:00) ar fi împins S51 după 00:00, deci placa ar fi stat iar liberă o noapte întreagă, și tot așa la fiecare bucată. Descărcarea nu folosește placa și nu are termen, deci:
**Acum (zi): S50** (procesor, ~1–2 ore). **De la 19:00: S51** (placa, ~7 ore, sfârșit ~02:00). **Imediat după ce S51 e `gata` sau `oprit`: S46 bucata 2** (`--limita-ore 10`, aceeași comandă; poate porni oricând între 19:00 și 07:00 și poate continua dimineața, nu folosește placa). Dacă S51 nu poate porni până la 00:00, bucata 2 pornește în locul ei, ca înainte.
**Actualizare 30 oct 14:15 (supraveghetor) — S50 verificat: bun; nimic nou în coadă; diseară S51 la 19:00, apoi S46 bucata 2:**
S50: regulile urcate înainte de măsurare (54895b9 11:38; măsurarea 11:41–11:43, o singură pornire, cod 0) ✓; medianele calde refăcute din timpii pe răspuns (2,300 / 3,137 / 1,247 s) ✓, 3,137/2,300 = 1,36× și 2,300/1,247 = 1,84× ✓; fp16/bf16 respinse la fiecare răspuns ✓; placa max 1.525 MB, 34 °C ✓; 1119 teste trec ✓. Un singur mărunțiș: la referinta/1 fir „28,5 simb/s” nu se potrivește cu 64/2,300 = 27,8 (celelalte rânduri se potrivesc) — nu schimbă alegerea. Efectul „40 simb/s la primul răspuns” din S49 nu s-a repetat; nu mai pun altă măsurare pe asta acum. Placa stă liberă până la 19:00 (nu pun o rulare scurtă înainte de S51, ca să nu-i întârzie pornirea).
**Actualizare 30 oct 17:15 (supraveghetor) — S52 (diagnosticul repornirii) `oprit`: jurnalele Windows nu se pot citi de executant; S51 neschimbat la 19:00:**
Verificat raportul `2026-10-30_1533_S52_repornire.md`: oprirea e corectă (`Get-WinEvent`/`wevtutil` cer aprobare; executantul nu a ocolit blocarea) ✓. Ce s-a putut afla: jurnalul plăcii S45 merge normal până la ultimul rând, 23:09:36 (64 °C, 6.116 MB, 98–100 %), fără niciun semn înainte → supraîncălzirea plăcii exclusă; oprirea bruscă se potrivește cu pana de curent pe care o bănuiește Adrian (sau o blocare), dar fără jurnalul Windows nu e sigur. Nu repun S52 `aprobat`: permisiunea de citire a jurnalelor Windows e a lui Adrian (comanda de copiat e în raport). **S51 pornește la 19:00 ca până acum**, apoi S46 bucata 2; dacă S51 cade iar fără eroare: `oprit` cu ora exactă, fără repornire.

**Actualizare 31 oct 02:15 (supraveghetor) — S51 verificat: CONFIRMAT (la limită); S46 bucata 2 rulează; placa rămâne liberă până la „da”-ul lui Adrian:**
S51: pre-înregistrarea (5344b50, 18:59:58) urcată înaintea pornirii (19:00:09) ✓; pornit din #459 (rândul din log) ✓; #459 re-măsurat exact ca reperul (1,2162 / 0,7321) ✓.
Față de praguri: română curat **1,2097 ≤ 1,2112** ✓ (Δ −0,0065; marjă 0,0015); cod curat **0,7270 ≤ 0,7371** ✓; R2 **0,4060 ≤ 0,4134** ✓ → **CONFIRMAT**, corect. Placa max 6.002 MB / 64 °C; 1119 teste trec.
Lecția: a doua noapte a adus −0,0065, față de −0,017 la prima (S38) — linia w2 cu rețeta A se aplatizează. **Nu pun o a treia noapte la fel**: după direcția din 22 oct, o nouă noapte de antrenare cere oricum „da”-ul lui Adrian, iar cifrele nu o susțin.
**S46 bucata 2** `in_lucru` de la 02:00 (fără placă, ~10 ore, până pe la ~12:00). **Placa rămâne liberă** (nicio sarcină de placă în granițele mele care să merite acum); întreb pe Adrian: #477 în locul lui #459 (interfață/OS) și ce vrea pe placă.

**Actualizare 31 oct 14:15 (supraveghetor) — S53 verificat: DE CURĂȚAT (corect); Adrian a spus „da la amândouă” (C-44, C-45): S54 (#477 în locul lui #459) apoi S55 (tokenizerul pe cod), ambele doar procesor:**
S53: suma setului ascuns `90fc64cd…3749` la început și la sfârșit ✓; o singură rulare (112 s) ✓; 3,8662 GB scanați = rezumatul S46 ✓. Față de praguri: soluția întreagă **0/200** (prag 0 ✓), suprapuneri de 13 **87/200 > 10** ✗, compromis (> 50 cu soluția întreagă) nu → **DE CURĂȚAT**, corect. De exclus 3.821 fișiere curate (118 MB = 3,06 %; 118,3/3866 = 3,06 % ✓); cea mai lungă suprapunere 26 de simboluri; 1126 teste trec, 1 sărit. Excluderea se aplică la S55. Propunerea executantului (să se excludă doar suprapunerile din enunț/soluție, nu cele din listele de numere ale testelor) **nu se aplică** fără „da”-ul lui Adrian: S55 exclude toată lista.
**Ordinea:** **S54** acum (procesor, ~1–2 ore; deblochează C-46 la OS), apoi **S55** (procesor, poate continua în noapte). **Placa stă liberă diseară**: nicio sarcină de placă în granițele mele care să merite (a treia noapte w2 nu e susținută de cifre); prima antrenare Kronos-Cod vine după S55, cu planul și pragurile din raportul ei.

**Actualizare 3 nov 05:20 (supraveghetor) — C-57 (Adrian): FEREASTRA LUI ADRIAN AZI 09:00–11:30 pe workstation.**
Între **09:00 și 11:30** nu porni nimic pe placă și nimic lung pe procesor (Adrian lucrează în Cyber Universe). Dacă la **08:45** rulează ceva, îl oprești
curat (reluabil) și scrii în raport unde s-a oprit. După 11:30 coada continuă normal. Direcția Kronos-Cod (S66) o alege Adrian după testele lui.
Până la 08:45: doar **S67** (procesor, scurtă). Placa rămâne liberă azi până la „da”-ul lui Adrian la S66.

**Actualizare 3 nov 08:20 (supraveghetor) — S67 verificat: ÎNTRE (corect, 3,55 mil. simboluri de corp la „autonome”).** Fereastra lui Adrian 09:00–11:30 rămâne neatinsă.
După **11:30**, pe procesor: **S68** (regula mai blândă la importuri + câte autonome sunt funcții chemabile, nu metode; ~1 oră). Placa rămâne liberă azi și la noapte
până la „da”-ul lui Adrian la S66 (nicio sarcină de placă în granițele mele care să nu anticipeze alegerea lui).

### S28 — Oprirea în siguranță a workstation-ului (cerută de Adrian)
- stare: anulat — nu mai e nevoie (Adrian, prin centrul de comandă, 27 oct 23:50; scris de supraveghetor 28 oct 02:15)
- stare veche: oprit
- motiv: cere aprobarea lui Adrian: comanda `shutdown` e blocată de permisiunile executantului (pașii 1–3 făcuți, push d68bd85; calculatorul rămâne pornit, fără lucru)
- tip: procesor (fără placă)
- fereastră: oricând — prima verificare a cozii după 24 oct 04:05
- durată maximă: 15 minute
- ce faci: 1) verifici că nu rulează nicio sarcină (nicio sarcină `in_lucru`, niciun proces Python al lui Kronos, `nvidia-smi` fără procese de
  calcul); dacă rulează ceva, aștepți să se termine (cel mult 6 ore), fără să-l oprești. 2) `git status` curat; dacă există modificări ale
  executantului, commit + push. 3) Scrii în `plan/pentru_adrian.md` un rând: „S28: workstation oprit la <ora>, nimic în lucru, ultimul commit <hash>”,
  pui S28 pe `gata`, commit + push și **verifici că push-ul a reușit**. 4) Abia apoi: `shutdown /s /t 120 /c "Kronos: oprire ceruta de Adrian (S28)"`.
  Nu opri, nu reseta și nu șterge nimic altceva. Dacă push-ul nu reușește, NU opri calculatorul (scrie de ce în `pentru_adrian.md` local și reîncearcă la verificarea următoare).
- aprobat de: Adrian, 24 oct 04:05 (prin centrul de comandă)
- raport: rândul din `plan/pentru_adrian.md` + `docs/rapoarte/2026-10-24_0433_S28_oprire_workstation.md`

### S1 — Noaptea 10: „răspuns din text” (w2_conv_text, din #385)
- stare: gata
- tip: placă
- fereastră: noapte
- durată maximă: 3 ore + examene
- ce faci: pornită de sarcina Windows „Kronos noapte conversatie” la 19:00, 19 octombrie
- pre-înregistrare: docs/preinregistrari/2026-10-19_noaptea10_raspuns_din_text.md
- aprobat de: Adrian, 19 octombrie
- raport: docs/rapoarte/2026-10-20_0756_raport_dimineata.md (CONFIRMAT, fără regresie)

### S2 — Motorul de română: merge în main și măsurarea datelor de conversație
- stare: gata
- tip: procesor (prioritate scăzută; NU folosește placa)
- fereastră: zi (08:00–18:30), oricând placa e ocupată sau liberă
- durată maximă: 3 ore
- ce faci:
  1. merge al ramurii `limba-romana` în `main` (doar `module/limba_romana/` și rapoartele ei; nimic din `kronos/`).
  2. ÎNAINTE de merge: testele motorului care au nevoie de baza `_baza/limba_romana.sqlite` se SAR (pytest skip) când
     baza lipsește, ca `python -m pytest` să treacă pe orice calculator. Verifică: toate testele trec cu și fără bază.
  3. descarcă sursele (`python -m module.limba_romana.importatoare.descarca_surse`, licențele sunt deja verificate în
     `module/limba_romana/LICENTE.md`, aprobat de Adrian) și construiește baza (`construieste_baza --proaspat`).
     Baza și sursele NU intră în Git.
  4. DOAR MĂSOARĂ, nu șterge și nu schimbă nimic în date: rulează `Motor().verifica_text` pe răspunsurile și textele
     din perechile de antrenare „răspuns din text” (19.668) și pe cele vechi (13.446). Raportează: câte perechi au cel
     puțin o problemă, pe tipuri (acord, al/a, numeral cu „de”, necunoscute, diacritice) și pe certitudine, plus 30 de
     exemple alese la întâmplare (sămânță fixă) cu textul, problema și sugestia, ca supraveghetorul să numere alarmele false.
  5. Filtrul pe datele de antrenare se aplică abia într-o sarcină separată, după „da”-ul lui Adrian.
- aprobat de: Adrian, 19 octombrie 2026, 19:45 (merge + descărcare + măsurare, cu condițiile 2–5)
- raport: docs/rapoarte/2026-10-20_1120_motor_romana_masurare.md (fără necunoscute: 18,6% din „răspuns din text”, 6,6% din cele vechi; mai ales alarme false)
- numărat de supraveghetor, 20 oct 11:20: din cele 30 de exemple, 1 problemă adevărată („rîul”), 29 alarme false; din cele 20 de gramatică, 2 adevărate (#17 „al”→„ale”, #19 „Măgurele”), 18 false. În total 3 din 50 (6%). Motorul NU e bun ca filtru așa cum e; filtrul (pasul 5) nu se propune acum.
### S3 — Școala de cod: o sarcină nouă pentru nivelul 0w
- stare: propus
- tip: placă
- fereastră: zi
- durată maximă: 4 ore
- ce faci: supraveghetorul scrie proiectul după verdictul nopții 10
- aprobat de: —
- raport: —
- notă supraveghetor, 20 oct 14:20: rămâne `propus`. Școala 0w a fost infirmată pe 16 oct (cel mult 35% pe nevăzut);
  o sarcină nouă cere un proiect gândit, nu o repetare. O scriu după verdictul nopții 11, ca să nu ocup placa ziua
  cu ceva prost pus la punct. Azi după-amiază placa rămâne liberă (pregătire pentru S7).

### S4 — Examen de generalizare pentru #401: întrebări puse altfel
- stare: gata
- tip: placă (scurt, cel mult 45 de minute) — sau procesor, dacă placa e ocupată
- fereastră: zi (08:00–18:30)
- durată maximă: 1 oră
- ce faci: noaptea 10 a ieșit 50/50, dar întrebările de examen au aceleași tipare ca la antrenare. Măsurăm dacă #401
  înțelege și întrebări formulate altfel. Din aceleași articole puse deoparte (nevăzute la antrenare), scrie 60 de
  întrebări NOI, cu răspunsul în text, în 4 feluri, câte 15:
  (a) aceleași informații, altă formulare („Când a venit pe lume X?”, „Ce populație are X?”, „Cine e autorul cărții X?”);
  (b) tipuri de întrebări care NU există în antrenare („În ce țară se află X?”, „Ce meserie are X?”, „Cu ce trupă a cântat X?”);
  (c) întrebări de tip „da/nu” („S-a născut X în 1980?”) — răspuns corect „Da.”/„Nu.” după text;
  (d) întrebări fără răspuns în text, dar formulate altfel decât la antrenare (corect: „Nu scrie în text.”).
  Pre-înregistrarea ÎNAINTE de rulare: confirmat dacă (a) ≥ 9/15 și (b) ≥ 6/15; infirmat dacă (a) < 5/15.
  (c) și (d) doar urmărite. Profesorul notează la fel ca la noaptea 10 (corect = nota ≥ 7). Nicio antrenare, doar examen.
- aprobat de: supraveghetor, 20 octombrie 2026, 10:50 (categoria „examene”)
- raport: docs/rapoarte/2026-10-20_1100_S4_generalizare_401.md (PARȚIAL: a 7/15, b 3/15, c 2/15, d 11/15; „Nu scrie” pe nedrept 22/45)
- verificat de supraveghetor, 20 oct 11:20: PARȚIAL e corect după praguri (a=7: nu ≥ 9, nici < 5). La (c) cele 2 „corecte” sunt copieri; cu regula „începe cu Da./Nu.” ar fi 0/15.

### S5 — Interfața: fila nouă „Întreabă din text” cu modelul #401
- stare: gata
- tip: procesor (interfața rulează pe procesor; NU ocupă placa)
- fereastră: oricând
- durată maximă: 2 ore
- ce faci: în interfața de pe portul 8787 adaugă o filă nouă „Întreabă din text”: o căsuță mare pentru paragraf, o căsuță
  pentru întrebare și butonul „Întreabă”. Răspunsul vine de la modelul #401 (linia w2_conv_text), cu exact formatul de la
  antrenare („Text: … / Întrebare: … / Răspuns:”), oprit la sfârșitul răspunsului. Fila veche (modelul #312) rămâne cum e.
  Arată sub răspuns un rând mic: „Kronos #401 — răspunde doar din textul dat.” Dacă paragraful e mai lung decât încape
  în fereastra modelului (512 bucăți cu tot cu întrebarea), spune asta clar, nu tăia în tăcere. Teste pentru noua filă,
  apoi repornește interfața și verifică de pe 100.90.150.35:8787 cu 3 exemple (unul cu răspuns, unul fără, unul lung).
  Nu atinge `kronos/`.
- aprobat de: Adrian, 20 octombrie 2026, 10:47
- raport: docs/rapoarte/2026-10-20_1317_S5_interfata_intreaba_din_text.md (3/3 exemple bune: „24.160 de locuitori.”, „Nu scrie în text.”, textul lung refuzat clar: 669 > 432 bucăți)

### S6 — Datele pentru noaptea 11: aceleași întrebări, formulate în mai multe feluri, plus da/nu
- stare: gata
- tip: procesor (NU folosește placa)
- fereastră: zi (08:00–18:30); după S5. Trebuie să fie `gata` până la 18:30, altfel S7 nu pornește în seara asta.
- durată maximă: 2 ore
- ce faci: S4 a arătat că #401 a învățat cuvintele întrebării, nu sensul (altă formulare 7/15, „Nu scrie în text.” pe
  nedrept 22/45). Facem perechi noi, cu aceleași TIPURI de întrebări ca în noaptea 10, dar spuse în mai multe feluri.
  1. În `unelte/conversatie_text.py` adaugă opțiunea `--formulari` (implicit oprită, ca datele nopții 10 să rămână
     reproductibile) și `--dosar` (implicit `date/conversatie/text`). Cu `--formulari`, fiecare șablon existent are
     5–8 formulări alese la întâmplare (de exemplu: „În ce an s-a născut X?” / „Când s-a născut X?” / „În ce an a apărut
     pe lume X?” / „Care e anul nașterii lui X?” / „Ce an de naștere are X?”; „Câți locuitori are X?” / „Ce populație are
     X?” / „Câte persoane locuiesc în X?”; „Cine a regizat X?” / „Cine e regizorul lui X?” / „Sub ce regie e X?”). Aceleași
     formulări și la perechile „Nu scrie în text.” despre același subiect.
  2. Adaugă perechi da/nu (cam 15% din perechile cu text), DOAR pe șabloanele care există (an, locuitori, județ, comună,
     regizat/scris): „S-a născut X în 1966?” → „Da.” când anul e în text; „Nu.” când e alt an/alt județ/alt nume
     (schimbat de unealtă). Jumătate „Da.”, jumătate „Nu.”. Răspunsul e doar „Da.” sau „Nu.”.
  3. INTERZIS, ca examenul S4 să rămână cinstit: (i) niciun TIP nou de întrebare (fără țară, meserie, trupă, club,
     loc al nașterii, nume științific — acelea sunt (b) din S4); (ii) niciuna dintre formulările scrise în
     `docs/conversatie/examen_generalizare_401.json` (verifică automat: primele 4 cuvinte ale fiecărei întrebări de
     acolo nu apar ca început de întrebare în antrenare; scrie în raport câte s-au găsit — trebuie 0); (iii) niciun
     articol din examenul nopții 10 și din S4.
  4. Rulează: `python unelte/conversatie_text.py --articole 16000 --formulari --dosar date/conversatie/text_v2`
     (aceeași sămânță 1019, cam același număr de perechi, ~20% „Nu scrie în text.”, conversația simplă la fel).
     NU suprascrie `date/conversatie/text/`.
  5. Teste noi pentru `--formulari` și da/nu; `python -m pytest` trebuie să treacă.
  6. Fă `config/conv_w2_text_v2.toml`: copie a lui `config/conv_w2_text.toml` cu `conversatie =
     "date/conversatie/text_v2/antrenare.jsonl"` și `cale_stare = "lucru/w2_conv_text_v2/gpt.pt"`; restul identic
     (45/5/50, rata 0,00005, lot 12, context 512). Linia rămâne `w2_conv_text`.
  7. Scrie pre-înregistrarea pentru S7 (`docs/preinregistrari/2026-10-20_noaptea11_formulari.md`) cu pragurile de mai
     jos, copiate exact, plus așteptările tale în cifre.
- aprobat de: supraveghetor, 20 octombrie 2026, 11:20 (categoriile „pregătirea datelor din surse deja descărcate” și
  „unelte noi în unelte/ cu teste”)
- raport: docs/rapoarte/2026-10-20_1352_S6_date_formulari.md (24.149 perechi: 3.585 da/nu, 4.780 „Nu scrie”, 5–6 formulări pe șablon; verificarea 3.(ii): 0, texte din examene: 0; 813 teste trec. De citit: au ieșit și 3 formulări vechi „În ce an a …”, ca (ii) să dea 0)

### S7 — Noaptea 11: „răspuns din text” cu formulări diferite, din #401
- stare: gata (21 oct 00:05: antrenarea cod 0 la 23:58, examenele pe #407 cod 0 la 00:01–00:03; PARȚIAL, fără regresie)
- verificat de supraveghetor, 21 oct 02:15: am renumărat din tabelul cu cele 60 de răspunsuri: (a) 11/15 (≥ 10 ✔),
  (b) 2/15 (< 5 ✘), „Nu scrie” pe nedrept 4 + 7 + 0 = 11/45 (> 10 ✘), (c) 13/15; (a) nu e ≤ 7, deci nu INFIRMAT. Noaptea 10
  49/50, 19/20, 0/50; română 1,2818, cod 0,7882, povești 0,4395, fapte 75 — toate în praguri. **PARȚIAL, fără regresie:
  corect.** Efect nou rău: 3 întrebări care NU sunt da/nu primesc „Da.”/„Nu.” (#20, #22, #59) — urmărit de acum în prag (S12).
- stare veche: in_lucru (pornire de mână, Adrian de față, 20 oct 20:47; fișierele primei porniri mutate de executant cu
  aprobarea lui Adrian: lucru/cascada/S7.json → S7_prima_1929.json, S7.log → S7_prima_1929.log)
- notă executant, 20 oct 20:47: S7 pornită de mână la 20:47, fără `--din-nou`; pasul R (reparația cascada.py cu
  `--din-nou`) rămâne în coadă pentru ziua de mâine, neatins.
- notă supraveghetor, 20 oct 23:15: văzut raportul `2026-10-20_2050_S7_pornire_manuala.md`; pornirea e corectă (linia
  `w2_conv_text_v2`, din #401, placa 6.225 MB / 55 °C, sub limite). Antrenarea se termină pe la 23:50, apoi examenele (pașii
  2–4). Pasul R NU mai face parte din S7: l-am mutat în S9 (mâine ziua, pe procesor), ca S7 să conțină doar noaptea 11.
- stare veche: aprobat (repus de supraveghetor, 20 oct 20:45 — întâi pasul R de mai jos, apoi pornirea)
- pasul R (reparația uneltei, aprobat de supraveghetor, 20 oct 20:45, categoria 6 „reparații de scripturi”): fără `mv` în
  shell. În `unelte/cascada.py` adaugă la `porneste` opțiunea `--din-nou`: dacă `lucru/cascada/<nume>.json` există și sarcina
  e TERMINATĂ (are `cod` sau procesul nu mai trăiește), unealta mută singură, din Python, `<nume>.json` → `<nume>_<HHMM>.json`
  și `<nume>.log` → `<nume>_<HHMM>.log` (HHMM = ora din `pornita`; dacă numele există deja, adaugă `_2`, `_3`), scrie în
  consolă ce a mutat, apoi pornește ca de obicei. Fără `--din-nou` comportamentul rămâne exact cel de azi. Dacă sarcina încă
  MERGE, refuză și cu `--din-nou`. Nu șterge nimic. Teste noi în `teste/test_cascada.py` (cu `--dosar` temporar): (1) fără
  opțiune refuză ca înainte; (2) cu opțiune pe o sarcină terminată mută ambele fișiere și pornește; (3) cu opțiune pe o
  sarcină care merge refuză. `python -m pytest` trece → commit „Cascada: porneste --din-nou (S7 blocată de S7.json vechi)”,
  push. Apoi, dacă placa e liberă și e înainte de 02:30, pornește S7 cu aceeași comandă de la pasul 1, plus `--din-nou` după
  `porneste S7`. Configurarea și pre-înregistrarea NU se mai ating (sunt gata din 20:33). Dacă reparația nu merge din 3
  încercări sau e deja după 02:30: S7 rămâne `oprit`, scrie raport scurt și lasă noaptea pe mâine.
- motiv vechi: rularea reparată NU a pornit (20:33): `cascada.py porneste S7` refuză, pentru că `lucru/cascada/S7.json` de la prima pornire (19:29, cod 0) există încă; redenumirea lui a cerut aprobare în rularea automată. Configurarea (`nume = "w2_conv_text_v2"`) și nota din pre-înregistrare sunt gata. Trebuie mutat fișierul vechi (sau reparată unealta), apoi S7 din nou `aprobat`; vezi docs/rapoarte/2026-10-20_2033_S7_reparat_nepornit.md
- reparația aprobată: varianta 2 (Adrian, 20 oct 20:27, prin centrul de comandă). Executant: la prima rulare după ce citești
  asta, dacă placa e liberă, fă pașii 1–4 de mai jos pe linia nouă: în `config/conv_w2_text_v2.toml` pune `nume = "w2_conv_text_v2"`,
  adaugă în pre-înregistrare nota „rulare reparată pe linia w2_conv_text_v2, din #401, aceleași praguri” ÎNAINTE de pornire, apoi comanda
  de la pasul 1. Pasul 0 e deja făcut (17:29), nu-l repeta. Raportul de dimineață ca la pasul 4.
- notă supraveghetor, 20 oct 20:45: executantul a oprit corect (n-a ocolit cererea de aprobare pentru `mv`). Am ales
  varianta lui 2 (reparația uneltei), ca să nu fie nevoie de Adrian la calculator; vezi pasul R. Rularea durează ~4 ore, deci
  dacă pornește până la ~22:00 examenele sunt gata pe la 02:00.
- notă supraveghetor, 20 oct 20:30: am văzut „da”-ul lui Adrian; instrucțiunea de mai sus e exact varianta 2 pe care am
  recomandat-o, nu mai schimb nimic. Executant: după `nume = "w2_conv_text_v2"` verifică înainte de pornire că dosarul
  `lucru/w2_conv_text_v2/` nu există sau e gol (ca `--porneste-din 401` să se aplice); dacă rezultă un nou id de experiment,
  scrie-l în pre-înregistrare. Verdictul îl dau la trecerea de 08:15, din raportul de dimineață.
- notă supraveghetor, 20 oct 20:15: recomand varianta 2 (`nume = "w2_conv_text_v2"` în `config/conv_w2_text_v2.toml`,
  aceeași comandă, aceleași praguri, notă în pre-înregistrare înainte de pornire). Am citit `unelte/antrenare_lunga.py`:
  `--porneste-din 401` se aplică doar când linia are 0 ore și `cale_stare` lipsește, deci varianta 2 pornește corect din
  #401; varianta 1 (`--ore 6`) ar porni fără stare — NU. Nu o aprob singur în această trecere; aștept „da”-ul lui Adrian.
  Greșeala de la S6 pasul 6 („linia rămâne `w2_conv_text`”) e a mea.
- motiv: antrenarea nu a rulat (11 secunde, cod 0): linia `w2_conv_text` are deja 3 ore în jurnal, iar `--ore 3` înseamnă „3 în total”, deci n-a fost nicio oră de făcut și `--porneste-din 401` a fost ignorat. Trebuie altă linie (recomand `nume = "w2_conv_text_v2"`) sau altă comandă; vezi raportul.
- perechi verificate: da (supraveghetor, 20 oct 14:20). Am citit raportul S6 și cele 20 de perechi: toate corecte după text;
  da/nu jumătate-jumătate, „Nu.” niciodată cu o valoare din text; 3.(ii) = 0, 3.(iii) = 0; în `FORMULARI` niciun tip nou
  (fără țară, meserie, trupă, club) și niciun început din S4 (cele din S4 apar doar în comentariul cu ce s-a lăsat
  deoparte). Abaterea (scoaterea lui „În ce an a murit / a apărut / a fost atestat documentar X?”) e acceptată: ține
  examenul S4 cinstit; riscul (3 întrebări din examenul nopții 10) e scris în pre-înregistrare și încape în prag (≤ 5/50).
  Cele 24.149 de perechi (nu „cam același număr”) sunt acceptate: noaptea are 3 ore fixe.
- tip: placă
- fereastră: noapte (19:00–07:00)
- durată maximă: 3 ore de antrenare + examene (cam 4 ore în total)
- ce faci:
  0. ÎNAINTE de 19:00 — **pasul 0 se face în fereastra „zi”** (schimbat de supraveghetor, 20 oct 17:20, la întrebarea
     din `docs/rapoarte/2026-10-20_1600_S7_pasul0_inainte_de_19.md`): prima ta rulare după ce citești asta (~17:30 sau
     ~18:00, în orice caz până la 18:50) face DOAR pasul 0, fără să pornească antrenarea și fără să schimbe starea lui S7;
     scrie un raport scurt `docs/rapoarte/2026-10-20_<ora>_S7_pasul0.md`, commit + push. Antrenarea (pașii 1–4)
     pornește tot după 19:00, ca până acum. Dacă `schtasks` e refuzat, redenumește oricum (nu strică nimic dacă sarcina
     Windows nu mai e programată). După 19:00, înainte de pasul 1: verifică placa; dacă totuși rulează ceva, nu porni.
     Textul vechi: `schtasks /Query /TN "Kronos noapte conversatie" /V /FO LIST` (doar citire). Dacă sarcina
     Windows ar porni și ea în seara asta, ar reface noaptea 10 (aprobarea din `lucru/conversatie_aprobata.txt` o lasă).
     Ca să nu fie două lucruri pe placă, redenumește `lucru/conversatie_aprobata.txt` în
     `lucru/conversatie_aprobata_19oct.txt` (nu șterge; nu schimba sarcina Windows). Atunci scriptul ei nu antrenează nimic.
     Scrie în raport ce ai găsit.
  1. Pornește prin cascadă: `python -X utf8 unelte/antrenare_lunga.py --config config/conv_w2_text_v2.toml --ore 3
     --porneste-din 401`.
  2. Pe ultimul model păstrat, aceleași examene ca în noaptea 10 (`date/conversatie/text/examen.json`, profesorul
     Qwen3-4B, validările curate, setul sacru, fapte noi), PLUS examenul S4:
     `unelte/examen_conversatie.py --experiment <noul id> --examen docs/conversatie/examen_generalizare_401.json`.
  3. Praguri (în pre-înregistrare, înainte de pornire). Corect = nota profesorului ≥ 7; la da/nu (c) corect = răspunsul
     ÎNCEPE cu „Da.”/„Nu.” potrivit (numărat de tine, nu de profesor).
     - CONFIRMAT: S4 (a) ≥ 10/15 ȘI (b) ≥ 5/15 ȘI „Nu scrie în text.” pe nedrept la (a)+(b)+(c) ≤ 10/45.
     - INFIRMAT: S4 (a) ≤ 7/15 (nu e mai bine decât #401).
     - Fără să strice noaptea 10: pe examenul nopții 10, din text ≥ 45/50, „Nu scrie” ≥ 16/20, refuz greșit ≤ 5/50.
     - Să nu uite (ca la noaptea 10, față de #385): română ≤ 1,3133; cod ≤ 0,8174; povești ≤ 0,47; fapte noi ≥ 65.
     - Urmărite: (c) da/nu (#401: 0/15 cu regula de mai sus), (d) (#401: 11/15), setul sacru (#401: 24).
  4. Dimineață: raportul cu verdictul strict după praguri, tabelul complet S4 (60) și 20 de răspunsuri din examenul
     nopții 10 (sămânța 1019). Dacă sarcina „Kronos raport dimineata” nu știe de noaptea asta, îl scrii tu.
- pre-înregistrare: docs/preinregistrari/2026-10-20_noaptea11_formulari.md (scrisă în S6)
- aprobat de: supraveghetor, 20 octombrie 2026, 11:20 (categoria „încă o rulare pe o linie care există, alt amestec
  de date”); poarta: „perechi verificate: da”
- raport: docs/rapoarte/2026-10-20_2002_S7_oprit_nu_a_antrenat.md (oprit: nicio oră antrenată; raportul de dimineață rămâne pentru rularea reparată); docs/rapoarte/2026-10-20_2033_S7_reparat_nepornit.md (rularea reparată pregătită, nepornită: fișierul vechi lucru/cascada/S7.json); docs/rapoarte/2026-10-20_2050_S7_pornire_manuala.md (pornită de mână la 20:46:55, procesul 23960); **docs/rapoarte/2026-10-21_0005_S7_noaptea11.md** (raportul de dimineață al nopții 11: PARȚIAL, fără regresie — (a) 11/15, (b) 2/15, „Nu scrie” pe nedrept 11/45, (c) 13/15, (d) 12/15; noaptea 10: 49/50, 19/20, 0/50)


### S8 — Formatul comun de modul din Cyber Hub: `module.toml` pentru modulele Kronos
- stare: gata (21 oct 10:46; 24 de fișiere în module/manifeste/, unealta unelte/module_toml.py, 843 teste trec, 1 sărit)
- stare veche: aprobat — reaprobată de Adrian (21 oct 10:05, prin centrul de comandă). Standardul e acum copiat în repo: citește
  `plan/hub_modul-v0.md` (copie identică a `standarde/modul-v0.md` din hub) în loc să clonezi hub-ul. Restul pașilor neschimbați.
  Starea veche: oprit
- motiv: executantul nu poate citi hub-ul (git clone, gh api și citirea web cer permisiune în sesiunea automată); trebuie o copie a standardului în repo sau permisiunea lui Adrian
- tip: procesor (NU folosește placa; nu rulează cât timp S7 antrenează)
- fereastră: zi (08:00–18:30), 21 octombrie, după raportul de dimineață al nopții 11
- durată maximă: 2 ore
- ce faci: Adrian a aprobat în hub (`Adriancu91/Cyber-hub`, `idei/2026-10-20-format-comun-module.md`, 20 oct 16:04) ca
  toate proiectele să-și descrie modulele la fel, după `standarde/modul-v0.md` din hub. Partea Kronos: un fișier descriptiv
  pe modul, cu aceleași date ca în `MANIFEST` + „de ce depinde” / „ce oferă”. Fără nicio schimbare de cod în module.
  1. Clonează sau actualizează hub-ul (`git clone https://github.com/Adriancu91/Cyber-hub`) și citește `standarde/modul-v0.md`
     (câmpurile `[modul]`, `[contract]`, `[depinde]`, `[ofera]`, `[rulare]`). Pentru Kronos `port` și `versiune_contract` sunt obligatorii.
  2. Modulele Kronos sunt fișiere, nu dosare, deci pune descrierile într-un singur dosar: `module/manifeste/<nume>.toml`, câte
     unul pentru fiecare clasă cu `MANIFEST` din `module/` (~27, inclusiv cele din `jucarii.py`, `continuum/`, `interfata/`,
     `limba_romana/` dacă au `MANIFEST`). `proiect = "kronos"`, `format = "modul-v0"`, `versiune` și `port` exact din `MANIFEST`,
     `versiune_contract` ca text (ex. `"1"`), `descriere` o propoziție în română, `[rulare] limbaj = "python"`, `intrare` =
     `pachet.fisier:Clasa` (forma din configurări), `teste` = comanda pytest a modulului (sau `python -m pytest teste_contracte`).
  3. Ca să nu se poată desincroniza: o unealtă `unelte/module_toml.py` care generează/actualizează fișierele din `MANIFEST`-uri
     (câmpurile `descriere`, `[depinde]`, `[ofera]` le completezi tu o dată și unealta le păstrează), plus un test nou în `teste/`
     care verifică, pentru fiecare clasă cu `MANIFEST`, că există fișierul și că `nume`, `port`, `versiune`, `versiune_contract`
     coincid. Nu atinge `kronos/`, `module/examen_bpb.py` (doar îi scrii descrierea), configurările sau datele.
  4. `python -m pytest` trece. Raport scurt `docs/rapoarte/2026-10-21_<ora>_S8_module_toml.md` (câte fișiere, lista porturilor,
     ce a fost greu de descris). Commit + push în `cyberspace`. În hub NU scrii nimic (regula din CLAUDE.md): supraveghetorul
     notează „gata” la propunere după ce citește raportul.
- pre-înregistrare: nu e nevoie (nu folosește placa, nu antrenează nimic)
- aprobat de: Adrian (hub, propunerea „format comun pentru module”, aprobat 20 oct 16:04); pusă în coadă de supraveghetor,
  20 oct 20:30 (categoria „unelte noi în unelte/ și teste noi, care nu ating kronos/ și examenul”)
- raport: docs/rapoarte/2026-10-21_0940_S8_oprit_hub_inaccesibil.md; **docs/rapoarte/2026-10-21_1046_S8_module_toml.md** (gata)
- verificat de supraveghetor (21 oct 11:15): 24 de descrieri (nu ~27: `continuum/`, `interfata/`, `limba_romana/` n-au clase
  cu `MANIFEST`), toate cele 10 porturi acoperite, 843 teste trec. Notat „gata” în hub, la propunere.


### S9 — Unealta de pornire: `cascada.py porneste --din-nou` (fostul pas R din S7)
- stare: gata (21 oct 10:11; 815 teste trec, 1 sărit)
- tip: procesor (NU folosește placa)
- fereastră: zi (08:00–18:30), 21 octombrie, după raportul de dimineață al nopții 11; înainte sau după S8, nu în paralel
- durată maximă: 1 oră
- ce faci: aseară, a doua pornire a lui S7 a fost refuzată pentru că `lucru/cascada/S7.json` de la prima încercare exista încă;
  fișierele au fost mutate de mână (cu Adrian de față). Reparăm unealta ca data viitoare să nu mai fie nevoie de om.
  În `unelte/cascada.py` adaugă la `porneste` opțiunea `--din-nou`: dacă `lucru/cascada/<nume>.json` există și sarcina e
  TERMINATĂ (are `cod` sau procesul nu mai trăiește), unealta mută singură, din Python, `<nume>.json` → `<nume>_<HHMM>.json`
  și `<nume>.log` → `<nume>_<HHMM>.log` (HHMM = ora din `pornita`; dacă numele există deja, adaugă `_2`, `_3`), scrie în
  consolă ce a mutat, apoi pornește ca de obicei. Fără `--din-nou` comportamentul rămâne exact cel de azi. Dacă sarcina încă
  MERGE, refuză și cu `--din-nou`. Nu șterge nimic. Teste noi în `teste/test_cascada.py` (cu `--dosar` temporar): (1) fără
  opțiune refuză ca înainte; (2) cu opțiune pe o sarcină terminată mută ambele fișiere și pornește (o comandă inofensivă,
  ex. `python -c "print(1)"`); (3) cu opțiune pe o sarcină care merge refuză. Nu atinge `kronos/`, examenul, configurările
  sau fișierele din `lucru/`. `python -m pytest` trece → commit „Cascada: porneste --din-nou”, push. Raport scurt
  `docs/rapoarte/2026-10-21_<ora>_S9_cascada_din_nou.md` (ce s-a schimbat, câte teste trec).
- pre-înregistrare: nu e nevoie (nu folosește placa, nu antrenează nimic)
- aprobat de: supraveghetor, 20 octombrie 2026, 20:45 (ca pas R în S7), mutată în S9 la 23:15 (categoria 6 „reparații de scripturi”)
- raport: docs/rapoarte/2026-10-21_1011_S9_cascada_din_nou.md
- verificat de supraveghetor (21 oct 11:15): doar `unelte/cascada.py` și testele lui; S12 poate folosi `--din-nou`.


### S10 — Examenul S4 pe #405 și #406 (orele 1 și 2 ale nopții 11)
- stare: gata (21 oct 08:32:29, cod 0; pornită 08:29:42, procesul 4112; prima încercare de la 08:29:20 n-a rulat nimic — Git Bash a stricat „/c” în „C:/” — fișierele ei mutate în lucru/cascada/S10_gresita_0829.*, scris în raport)
- tip: placă (scurt: ~3 minute pe examen, cel mult 30 de minute în total)
- fereastră: zi (08:00–18:30), 21 octombrie, prima sarcină a zilei
- durată maximă: 30 de minute
- ce faci: #407 (ora 3) a pierdut la tipurile noi (b) față de #401 (2 față de 3/15) și a început să răspundă „Da.”/„Nu.” la
  întrebări care nu sunt da/nu. Vrem să știm dacă asta crește cu orele (atunci noaptea 12 trebuie scurtată) sau nu.
  1. Verifică placa liberă (`python unelte/cascada.py stare`).
  2. Pentru 405 și 406, una după alta: `python -X utf8 unelte/examen_conversatie.py --experiment <id> --examen
     docs/conversatie/examen_generalizare_401.json --doar-local`. Doar examen, nicio antrenare.
  3. Raport `docs/rapoarte/2026-10-21_<ora>_S10_S4_pe_405_406.md`: tabelul (a)/(b)/(c)/(d) pentru #401, #405, #406, #407
     (corect = nota ≥ 7; la (c) corect = începe cu „Da.”/„Nu.” potrivit, numărat de tine), „Nu scrie” pe nedrept la
     (a)+(b)+(c), și câte întrebări din (a)+(b)+(d) primesc „Da.”/„Nu.” deși nu sunt da/nu. Fără verdict (nu e
     pre-înregistrare; e doar măsurare). Commit + push.
- pre-înregistrare: nu e nevoie (doar examen, fără praguri de decizie)
- aprobat de: supraveghetor, 21 octombrie 2026, 02:15 (categoria 2 „examene, comparații, notări”)
- raport: docs/rapoarte/2026-10-21_0910_S10_S4_pe_405_406.md ((a) 10 → 9 → 11, (b) 2 → 1 → 2, (c) 13/15 la toate, „Nu scrie” pe nedrept 7 → 6 → 11/45, „Da./Nu.” greșit 10 → 6 → 3: scade cu orele)
- verificat de supraveghetor (21 oct 11:15): am renumărat tabelul de 60 de întrebări — aceleași cifre la toate 4 modelele.
  Concluzie: „Da./Nu.” greșit scade cu orele → noaptea 12 rămâne de 3 ore; tipurile noi (b) stau pe loc (2 → 1 → 2), deci
  mai multe ore nu ajută — se potrivește cu ideea din S11 (alte tipuri de întrebări în date).

### S11 — Datele pentru noaptea 12: tipuri noi de întrebări (altele decât cele din examenul S4)
- stare: gata (21 oct 11:22; 3.319 perechi noi, 27.468 în total în date/conversatie/text_v3; verificările 3.(i)–(iii) toate 0; 849 teste trec, 1 sărit). Aștept „perechi verificate: da” de la supraveghetor.
- tip: procesor (NU folosește placa)
- fereastră: zi (08:00–18:30), 21 octombrie, după S10. Trebuie `gata` până la 16:30 (le verific la 17:15), altfel S12
  nu pornește în seara asta.
- durată maximă: 2 ore și jumătate
- ce faci: noaptea 11 a arătat că formulările multe ajută la aceleași tipuri de întrebări ((a) 7 → 11/15), dar nu la
  tipuri pe care nu le-a văzut ((b) 2/15). Ipoteza: cu MAI MULTE TIPURI de întrebări la antrenare, modelul învață „caută
  în text răspunsul la ce se întreabă”, nu tipare. Examenul (b) rămâne cinstit doar dacă tipurile lui NU intră în antrenare.
  1. În `unelte/conversatie_text.py` adaugă opțiunea `--tipuri-noi` (implicit oprită, ca datele nopților 10 și 11 să
     rămână reproductibile; verifică: fără ea, `text_v2` iese byte cu byte la fel). Cu ea, pe lângă șabloanele de azi,
     scoate din text (cu expresii regulate, răspunsul luat cuvânt cu cuvânt din text, ca până acum) cât mai multe din:
     - râuri: „afluent al râului Y” → „Al cărui râu este afluent X?”; „bazinul (hidrografic al) râului Y” → „Din ce bazin
       face parte X?”; lungimea („are o lungime de N km”) → „Ce lungime are X?”;
     - specii: „din familia Y” → „Din ce familie face parte X?”; „din genul Y” → „Din ce gen face parte X?”;
       „descrisă de Y în N” → „Cine a descris specia X?” și „În ce an a fost descrisă X?”;
     - oameni politici: „deputat ... în legislatura N–M” → „În ce legislatură a fost deputat X?”; „pe listele (partidului) Y”
       → „Pe listele cărui partid a fost ales X?”;
     - locuri: „pe malul râului Y” / „pe râul Y” → „Pe ce râu se află X?”;
     - orice alt tip pe care îl găsești curat în cel puțin 200 de articole, DACĂ nu e pe lista interzisă de la pasul 3.
     Fiecare tip nou: 3–5 formulări, perechi „Nu scrie în text.” despre același subiect când lucrul lipsește din text
     (de exemplu „Din ce familie face parte X?” la o specie fără „familia”), și da/nu doar unde schimbarea e sigură
     (familie, gen, an, partid, râu: „Nu.” cu valoarea altui articol, niciodată cu una din text).
  2. Împotriva „Da.” la întrebări care nu sunt da/nu: păstrează da/nu la ~15% și „Nu scrie” la ~20%, dar ai grijă ca în
     fiecare dintre cele 4 feluri să fie atât întrebări cu „Ce/Cine/Unde/Când/Cât”, cât și da/nu despre ACELAȘI text
     (perechi-soră). Scrie în raport câte texte au ambele.
  3. INTERZIS (ca examenul S4 să rămână cinstit), verificat automat și scris în raport (toate trebuie 0):
     (i) tipurile din S4 (b): țară, trupă/formație, club/echipă (și „pentru ce club joacă / la ce club evoluează”), loc al
     nașterii („unde s-a născut”), nume științific, zeu / „cui îi este dedicat”, firmă care a lansat / produs, medalie,
     „unde a fost profesor”, reședință, mare / „unde s-a scufundat”, locuri pe stadion, câți membri, meserie / ocupație;
     (ii) primele 4 cuvinte ale oricărei întrebări din `docs/conversatie/examen_generalizare_401.json` la începutul unei
     întrebări de antrenare; (iii) niciun text din examenul nopții 10 sau din S4.
  4. Rulează: `python unelte/conversatie_text.py --articole 16000 --formulari --tipuri-noi --dosar date/conversatie/text_v3`
     (sămânța 1019; tipurile noi cu întâmplarea lor, ca articolele și examenul să fie aceleași). Țintă: 2.000–5.000 de
     perechi din tipurile noi; restul ca în `text_v2`. NU suprascrie `text/` și `text_v2/`.
  5. Teste noi pentru `--tipuri-noi` (fiecare tip nou, „Nu scrie”, da/nu, verificările 3.(i)–(iii)); `python -m pytest` trece.
  6. `config/conv_w2_text_v3.toml`: copie a lui `config/conv_w2_text_v2.toml` cu `nume = "w2_conv_text_v3"`,
     `conversatie = "date/conversatie/text_v3/antrenare.jsonl"`, `cale_stare = "lucru/w2_conv_text_v3/gpt.pt"`; restul identic.
     Verifică că `lucru/w2_conv_text_v3/` nu există (ca `--porneste-din 407` să se aplice).
  7. Pre-înregistrarea pentru S12 (`docs/preinregistrari/2026-10-21_noaptea12_tipuri_noi.md`), cu pragurile din S12
     copiate exact, plus așteptările tale în cifre.
  8. Raport `docs/rapoarte/2026-10-21_<ora>_S11_date_tipuri_noi.md`: câte perechi pe tip (vechi și noi), verificările de
     la pasul 3, și **30 de perechi din tipurile noi alese la întâmplare (sămânța 1019)** cu textul întreg, ca să le
     verific eu. Commit + push.
- pre-înregistrare: nu e nevoie pentru S11 (nu antrenează); o scrie pe cea a lui S12
- aprobat de: supraveghetor, 21 octombrie 2026, 02:15 (categoriile 3 „pregătirea datelor din surse deja descărcate” și 5
  „unelte noi în unelte/ cu teste”)
- perechi verificate: da (supraveghetor, 21 oct 14:20). Am citit toate cele 30 de perechi din raport: **30/30 corecte după
  text** (răspunsul e cuvânt cu cuvânt din text; cele 7 „Nu scrie” chiar lipsesc — #10 Florin Georgescu fără partid, #12
  Haleș fără râu, #23 Kikihia fără autor; da/nu: #26 „Nu.” cu autori care nu apar în text). #24 (club) și #27 (formație)
  întreabă anul fondării, nu clubul/trupa — acceptat. Verificările 3.(i)–(iii) = 0; config v3 diferă doar prin `nume`,
  `conversatie`, `cale_stare`; pragurile din pre-înregistrare sunt copiate exact din S12. Abaterea „Când a fost descrisă X?”
  în loc de „În ce an a fost descrisă X?” e acceptată (ține regula (ii)). **S12 poate porni după 19:00.**
- raport: docs/rapoarte/2026-10-21_1122_S11_date_tipuri_noi.md (3.319 perechi noi: 2.157 cu text, 498 da/nu, 664 „Nu scrie”; 30 de perechi de verificat în raport; „În ce an a fost descrisă X?” înlocuită cu „Când a fost descrisă X?” din cauza regulii (ii); config/conv_w2_text_v3.toml și pre-înregistrarea S12 scrise)

### S12 — Noaptea 12: „răspuns din text” cu tipuri noi de întrebări, din #407
- stare: gata (21 oct 22:35; antrenarea 19:00–22:12 cod 0, examenele pe #415 la 22:31–22:34; INFIRMAT, fără regresie)
- stare veche: in_lucru (21 oct 19:00; poarta trecută: S11 `gata`, „perechi verificate: da” de la supraveghetor la 14:20)
- tip: placă
- fereastră: noapte (19:00–07:00), 21→22 octombrie
- durată maximă: 3 ore de antrenare + examene (cam 3 ore și jumătate)
- ce faci:
  1. Verifică placa liberă. Pornește prin cascadă: `python unelte/cascada.py porneste S12 -- .venv/Scripts/python.exe -X utf8
     unelte/antrenare_lunga.py --config config/conv_w2_text_v3.toml --ore 3 --porneste-din 407`
     (dacă S9 e gata și `S12.json` există de la o încercare oprită, adaugă `--din-nou` după `porneste S12`).
  2. Pe ultimul model păstrat, exact examenele din S7: examenul nopții 10, examenul S4
     (`docs/conversatie/examen_generalizare_401.json`), validările curate, setul sacru, fapte noi.
  3. Praguri (în pre-înregistrare, înainte de pornire). Corect = nota profesorului ≥ 7; la (c) corect = începe cu
     „Da.”/„Nu.” potrivit (numărat de tine). „Da./Nu. greșit” = răspuns care începe cu „Da.”/„Nu.” la o întrebare din
     (a), (b) sau (d) (#407: 3).
     - CONFIRMAT: S4 (b) ≥ 5/15 ȘI (a) ≥ 10/15 ȘI „Nu scrie în text.” pe nedrept la (a)+(b)+(c) ≤ 10/45 ȘI
       „Da./Nu. greșit” ≤ 1.
     - INFIRMAT: S4 (b) ≤ 2/15 (nu e mai bine decât #407).
     - Fără să strice ce știa: examenul nopții 10 din text ≥ 45/50, „Nu scrie” ≥ 16/20, refuz greșit ≤ 5/50; S4 (a) ≥ 9/15
       și (c) ≥ 11/15.
     - Să nu uite (ca la nopțile 10 și 11): română ≤ 1,3133; cod ≤ 0,8174; povești ≤ 0,47; fapte noi ≥ 65.
     - Urmărite: (d) (#407: 12/15), setul sacru (#407: 27), rezultatele lui S10 (dacă (b) scade cu orele, spune).
  4. Dimineață: raportul cu verdictul strict după praguri, tabelul complet S4 (60, cu coloanele #407 și noul model) și
     20 de răspunsuri din examenul nopții 10 (sămânța 1019) — dar ALEGE ALTE 20 decât ieri: `random.Random(1022)`.
- pre-înregistrare: docs/preinregistrari/2026-10-21_noaptea12_tipuri_noi.md (scrisă în S11)
- aprobat de: supraveghetor, 21 octombrie 2026, 02:15 (categoria 1 „încă o rulare pe o linie care există, alt amestec de
  date”: același model, același tokenizer, aceeași mărime, aceleași setări; doar datele noi)
- raport: docs/rapoarte/2026-10-21_2235_S12_noaptea12.md (INFIRMAT: S4 (b) 2/15, ca #407; fără regresie: noaptea 10
  50/50, 20/20, 0 refuzuri; (a) 11, (c) 13, (d) 12, „Nu scrie” pe nedrept 9/45, „Da./Nu.” greșit 3)
- verificat de supraveghetor (21 oct 23:15): am renumărat din tabelul de 60: (b) 2/15 (#20, #24) → ≤ 2 → **INFIRMAT, corect
  după praguri**; (a) 11, (c) 13, „Nu scrie” pe nedrept 2 + 7 + 0 = 9/45, „Da./Nu.” greșit 3 (#22, #47, #59). Noaptea 10
  50/50, 20/20, 0/50; română 1,2858, cod 0,7920, povești 0,4411, fapte 68 — toate în praguri: fără regresie. Placa max
  6.319 MB, 64 °C. Cele 20 de răspunsuri (sămânța 1022): am citit toate 20 — identice cu referința (la #3 „Cu mare plăcere!”
  față de „Cu plăcere!”, bine). Interfața rămâne pe #407 (#415 a pierdut „Mă numesc Kronos.”).

### S13 — Interfața: fila „Întreabă din text” trece de la #401 la #407
- stare: gata (21 oct 11:46; interfața repornită cu #407, procesul 26132; 4/4 exemple bune de pe 100.90.150.35:8787; 850 teste trec, 1 sărit)
- stare veche: aprobat (Adrian, 21 oct 10:05, prin centrul de comandă) — #407 în fila „Întreabă din text”; fila veche rămâne.
- tip: procesor (interfața; NU ocupă placa)
- fereastră: oricând, după „da”-ul lui Adrian
- durată maximă: 30 de minute
- ce faci: în fila „Întreabă din text” schimbă modelul #401 cu #407 și rândul de sub răspuns în „Kronos #407 — răspunde doar
  din textul dat.”; fila veche (#312) rămâne. Teste, repornește interfața, verifică de pe 100.90.150.35:8787 cu aceleași 3
  exemple ca la S5 plus o întrebare da/nu. Raport scurt. Nu atinge `kronos/`.
- de ce: pe examenul cu întrebări puse altfel, #407 are nota medie 6,68 (#401: 4,68): mai bine la formulări noi (11 față de
  7/15), da/nu (13 față de 0/15) și refuză pe nedrept de două ori mai rar; puțin mai slab la tipuri noi (2 față de 3/15) și
  uneori răspunde „Da.” unde nu e cazul. Recomandarea supraveghetorului: **da**.
- aprobat de: — (aștept „da”-ul lui Adrian)
- raport: docs/rapoarte/2026-10-21_1146_S13_interfata_407.md (24.160 de locuitori. / Nu scrie în text. / text lung refuzat clar / da/nu: „Da.”)
- verificat de supraveghetor (21 oct 14:20): schimbat doar `unelte/interfata_ws.ps1`, comentariul din `module/interfata/__main__.py`
  și un test; nimic în `kronos/`. Fila „Chat” rămâne pe #312.

### S14 — Raportul de dimineață: `git pull` înainte de a citi instrucțiunea
- stare: gata (21 oct 14:40; copia locală avea deja 7940c64; `git pull --ff-only` adăugat în raport_dimineata.ps1; 851 teste trec, 1 sărit)
- tip: procesor (NU folosește placa)
- fereastră: oricând, dar NU cât timp rulează S12 cu examenele (azi, înainte de 19:00 e cel mai bine); trebuie gata înainte de 07:40, 22 oct
- durată maximă: 30 de minute
- ce faci: azi (21 oct, 12:14) instrucțiunea `unelte/raport_dimineata.txt` s-a schimbat (cele 20 de răspunsuri aleg sămânța după
  data zilei). `unelte/raport_dimineata.ps1` (pornit de Task Scheduler la 07:40) citește fișierul local fără `git pull`, deci
  dacă copia de pe workstation nu e la zi, mâine raportul ar folosi instrucțiunea veche.
  1. Verifică acum: `git status` și `git log -1 -- unelte/raport_dimineata.txt` în `C:\Kronos\cyberspace` — copia locală are
     commit-ul 7940c64? Scrie în raport ce ai găsit.
  2. În `unelte/raport_dimineata.ps1`, înainte de `Get-Content ... raport_dimineata.txt`, adaugă un `git pull --ff-only`
     (scris în `lucru/raport_dimineata.log` cu `Scrie`); dacă pull-ul pică (fără rețea, conflict), scrie asta în jurnal și
     continuă cu fișierul local — raportul nu trebuie să se oprească din cauza asta. Nu schimba nimic altceva în script,
     nici sarcina Windows, nici `raport_dimineata.txt`.
  3. Dacă scriptele `.ps1` au deja un test (ca la S13, `teste/test_interfata.py`), adaugă un test mic care verifică textual
     că `git pull --ff-only` apare înaintea citirii instrucțiunii. `python -m pytest` trece → commit
     „S14: raportul de dimineață face git pull înainte”, push. Raport scurt `docs/rapoarte/2026-10-21_<ora>_S14_raport_pull.md`.
- pre-înregistrare: nu e nevoie (nu folosește placa)
- aprobat de: supraveghetor, 21 octombrie 2026, 14:20 (categoriile 5 și 6: unealtă din `unelte/`, fără `kronos/`, fără setări
  Windows), la nota centrului de comandă din `plan/pentru_adrian.md` (21 oct 12:20)
- raport: docs/rapoarte/2026-10-21_1440_S14_raport_pull.md
- verificat de supraveghetor (21 oct 17:20): schimbat doar `unelte/raport_dimineata.ps1` (pull după `Set-Location` în rădăcina
  repo-ului, cu ramura „continui cu fișierul local”) și `teste/test_raport_dimineata.py`; nimic în `kronos/`. Proba reală: 22 oct 07:40.

### S15 — Examen mare de generalizare: e 2/15 chiar zero? Și s-au învățat măcar tipurile antrenate?
- stare: gata (22 oct 00:44; „Tipurile văzute s-au învățat, dar nu se transferă”: #415 (e) 30/30, (b2) 6/50; #407 (b2) 9/50; 851 teste trec, 1 sărit)
- tip: procesor (scrierea examenului) + placă scurt (~15 minute, doar examene)
- fereastră: oricând placa e liberă — de preferat noaptea 21→22 (după ce citești asta); altfel prima sarcină a zilei de 22 oct
- durată maximă: 2 ore (din care pe placă cel mult 30 de minute)
- ce faci: două nopți la rând (b) a stat la 2–3 din 15. Cu 15 întrebări nu se poate deosebi „zero” de „puțin”. Și nu știm
  dacă #415 a învățat măcar tipurile noi pe care LE-A VĂZUT (familie, gen, partid, râu…) pe texte noi. Doar examen, nicio antrenare.
  1. Scrie `docs/conversatie/examen_generalizare_mare.json` (același format ca `examen_generalizare_401.json`: `nota` +
     `perechi`, fiecare cu felul ei), DOAR din articolele puse deoparte (aceleași ca la examenul nopții 10 și S4; niciun
     text din `date/conversatie/text*/antrenare.jsonl`, verificat automat). Răspunsul de referință luat cuvânt cu cuvânt din text.
     - **(b2) 50 de întrebări de tipuri care NU există în nicio antrenare** (nici `text`, nici `text_v2`, nici `text_v3`):
       pot fi tipurile din lista interzisă la S11 pasul 3.(i) și altele noi; cel puțin 10 tipuri, cel mult 6 întrebări pe tip;
       nicio întrebare copiată din S4. Verificare automată: primele 4 cuvinte ale fiecărei întrebări (b2) nu apar ca început
       de întrebare în nicio antrenare (trebuie 0).
     - **(e) 30 de întrebări din tipurile adăugate în S11** (familie, gen, cine a descris / când, legislatură, partid, râu /
       afluent / bazin, lungime, raion, anul fondării), cu formulări ca la antrenare, dar pe texte nevăzute. Acesta e
       controlul: arată dacă tipurile văzute s-au învățat.
     - Fără „Nu scrie” și fără da/nu în examenul ăsta (le avem deja în S4).
  2. ÎNAINTE de rulare, pre-înregistrarea `docs/preinregistrari/2026-10-22_examen_generalizare_mare.md` cu regulile de mai
     jos copiate exact și așteptările tale în cifre (commit + push înainte de examen).
  3. Pe placă, una după alta: `python -X utf8 unelte/examen_conversatie.py --experiment <id> --examen
     docs/conversatie/examen_generalizare_mare.json --doar-local` pentru **#401, #407, #415**. Verifică placa liberă înainte.
  4. Corect = nota profesorului ≥ 7. Numără pentru fiecare model: (b2) x/50, (e) x/30, „Nu scrie în text.” spus pe nedrept,
     „Da./Nu.” spus la întrebări care nu sunt da/nu; și (b2) pe fiecare tip.
  5. Reguli de citire (scrise acum, de supraveghetor):
     - **„Tipurile văzute s-au învățat, dar nu se transferă”:** #415 (e) ≥ 21/30 ȘI #415 (b2) ≤ 7/50.
     - **„Nici tipurile văzute nu s-au învățat bine”:** #415 (e) ≤ 14/30 → problema e cantitatea/orele pentru tipurile noi,
       nu felul datelor.
     - **„Există transfer mic, pe care 15 întrebări nu-l vedeau”:** #415 (b2) ≥ #407 (b2) + 6.
     - Altfel: neclar; se spune ca atare.
  6. Raport `docs/rapoarte/2026-10-22_<ora>_S15_examen_generalizare_mare.md`: tabelul pe modele, (b2) pe tipuri, ce regulă
     de la pasul 5 se aplică, verificările de la pasul 1 (trebuie 0) și 20 de răspunsuri (b2) alese cu `random.Random(1023)`.
     Teste: `python -m pytest` trece. Commit + push. Nu atinge `kronos/`, examenul BPB, configurările sau datele de antrenare.
- pre-înregistrare: docs/preinregistrari/2026-10-22_examen_generalizare_mare.md (o scrii tu, la pasul 2)
- aprobat de: supraveghetor, 21 octombrie 2026, 23:15 (categoria 2 „examene, comparații, notări”); e propunerea (2) a
  executantului din raportul S12
- raport: docs/rapoarte/2026-10-22_0044_S15_examen_generalizare_mare.md

### S16 — E0: verificatorul fără LLM pentru „răspuns din text” + re-notarea S15 și S4 în ambele feluri
- stare: gata (22 oct 02:46; acord împreună 527/540 = 97,6 % ≥ 90 % → „verificatorul poate înlocui pe Qwen”; niciun model sub 85 %; 868 teste trec, 1 sărit)
- tip: procesor (fără placă, fără Qwen, fără niciun model)
- fereastră: oricând (de preferat imediat, noaptea 21→22 sau dimineața 22 oct)
- durată maximă: 3 ore
- ce faci: direcția nouă aprobată de Adrian (22 oct 01:45, `docs/rapoarte/2026-10-22_0200_strategie_nucleu_fara_llm.md` §7 E0):
  examenele „răspuns din text” se notează de un verificator scris de noi, nu de Qwen. Aici doar îl scrii și îl compari cu Qwen
  pe răspunsurile DEJA salvate — nu rulezi niciun model și nu atingi notele vechi.
  1. `unelte/verificator_text.py` cu funcția `verifica(referinta, raspuns) -> dict` (corect: bool, motiv, scor). Reguli, exact:
     - normalizare: litere mici, „ş/ţ” → „ș/ț”, ghilimele și semnele de punctuație scoase, spații comprimate; cuvinte = bucăți
       despărțite de spații (diacriticele rămân).
     - **exact:** textul normalizat al răspunsului = cel al referinței → corect.
     - **referințe scurte speciale:** dacă referința e „Nu scrie în text.”, „Da.” sau „Nu.” (sau începe cu „Da,” / „Nu,”), corect
       doar dacă răspunsul începe cu același „nu scrie în text” / „da” / „nu” (după normalizare); altfel greșit.
     - **suprapunere (regula principală):** acoperirea = câte cuvinte ale referinței (cu repetiții, ca multiset) se găsesc în
       răspuns ÷ numărul de cuvinte ale referinței; corect dacă acoperirea ≥ 0,8 ȘI răspunsul nu e „Nu scrie în text.”.
     - **varianta a doua (doar raportată, nu decide):** F1 pe cuvinte ≥ 0,8 (pedepsește și răspunsurile lungi).
     Teste în `teste/test_verificator_text.py`: cel puțin 12 cazuri (exact, diacritice ş/ș, punctuație, răspuns lung care conține
     referința, repetarea întrebării, „Nu scrie în text.” corect și pe nedrept, da/nu, referință de 1 cuvânt, răspuns gol).
  2. `unelte/renoteaza_text.py`: citește fișierele de rezultate din `lucru/examen_conversatie/` și, pentru fiecare întrebare,
     pune alături nota lui Qwen (`nota_elev`, corect = ≥ 7) și verdictul verificatorului pe `raspuns` (referința) și
     `raspuns_elev`. NU scrie în fișierele vechi; scrie unul nou: `lucru/examen_conversatie/renotare_E0_<data>.json`.
     Fișierele, exact:
     - S15 (examen_generalizare_mare): `experiment_401_20261022_001355.json`, `experiment_407_20261022_001532.json`,
       `experiment_415_20261022_001707.json` (240 de răspunsuri);
     - S4 (examen_generalizare_401): `experiment_401_20261020_105728.json`, `experiment_405_20261021_083112.json`,
       `experiment_406_20261021_083228.json`, fișierul S4 al lui #407 din 21 oct 00:01–00:03 și cel al lui #415 din 21 oct
       22:31–22:34 (alege-l pe cel cu 60 de răspunsuri / `examen_generalizare_401`; scrie în raport numele exacte).
  3. Cifre de raportat: **acordul** = întrebări la care Qwen (≥ 7) și verificatorul (regula principală) spun la fel ÷ toate;
     pe S15, pe S4 și împreună; pe fiecare model; și separat pe felurile din S4 (grupurile a/b/c/d, „nu_scrie”). Tabelul de
     dezacorduri în două coloane: „Qwen corect, verificator greșit” și invers, numărate; plus TOATE dezacordurile S15 listate
     (întrebare, referință, răspuns, nota Qwen, acoperire). Scorurile noi: (b2) x/50 și (e) x/30 pe #401/#407/#415 după
     verificator, alături de cele Qwen (6/9/6, 14/4/30). Același acord și pentru varianta F1.
  4. Regula de citire (scrisă acum, de supraveghetor, după §7 E0): **acordul împreună (S15 + S4), regula principală, ≥ 90 %** →
     „verificatorul poate înlocui pe Qwen”; **< 90 %** → „încă nu” (atunci nu pornește S17; supraveghetorul scrie lui Adrian unde diferă).
     Se raportează și dacă vreun model are acord < 85 % (semn că verificatorul greșește sistematic la un fel de răspuns).
  5. Raport `docs/rapoarte/2026-10-22_<ora>_S16_verificator_fara_llm.md` (tot ce e mai sus + 20 de dezacorduri alese cu
     `random.Random(1022)` dacă sunt mai mult de 20). Teste: `python -m pytest` trece. Commit + push.
  Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, `unelte/examen_conversatie.py` (rămâne cum e până la decizia după S16),
  fișierele de examen din `docs/conversatie/`, datele de antrenare sau rezultatele vechi din `lucru/`.
- pre-înregistrare: nu e antrenare; regula de citire de la pasul 4 ține loc de praguri (scrisă înainte)
- aprobat de: supraveghetor, 22 octombrie 2026, 02:15 (categoria 2 „examene, comparații, notări” + 5 „unelte noi și teste”), din
  direcția aprobată de Adrian pe 22 oct 01:45 (punctul 3 din actualizarea de sus a cozii)
- raport: docs/rapoarte/2026-10-22_0246_S16_verificator_fara_llm.md

### S17 — E1: „întrebări născute de Kronos” (auto-joc cu verificator, fără niciun model străin)
- stare: gata (22 oct 21:10; rularea 15:29–20:57, toți pașii cod 0; 516 întrebări păstrate, 452 de tipuri; #425: (b2) 13/50, (e) 29/30, fără regresie → NECLAR: criteriul cere o repetare cu 3× date; 886 teste trec, 1 sărit)
- stare veche: in_lucru (executantul, 22 oct 15:30, pornire „ACUM” cerută de Adrian la 15:10; placa liberă: 681 MB, 30 °C)
- stare veche: aprobat (supraveghetor, 22 oct 05:15: S16 verificat — acord împreună 527/540 = 97,6 % ≥ 90 %, niciun model sub 85 %)
- stare veche: propus — trece pe `aprobat` (de supraveghetor, cu „da”-ul lui Adrian din 22 oct 01:45) DOAR dacă S16 iese cu acord ≥ 90 %
- pregătire ziua: scripturile (generator, filtre), testele lor, verificarea automată „0 articole de examen” și pre-înregistrarea le
  poți face ziua de 22 oct pe procesor, FĂRĂ placă (`CUDA_VISIBLE_DEVICES=-1`), ca noaptea să fie doar rularea. Pre-înregistrarea
  se face commit + push înainte de 19:00. Baseline-ul #415 notat de verificator (S16): (b2) 6/50, (e) 30/30, S4 38/60; scrie-le
  alături pe cele Qwen: (b2) 6/50, (e) 30/30, S4 38/60.
- pregătirea ziua: GATA (executantul, 22 oct 12:37; procesor, fără placă; 886 teste trec, 1 sărit). Starea sarcinii rămâne
  `aprobat`, ca rularea de după 19:00 s-o pornească. Raport: docs/rapoarte/2026-10-22_1237_S17_pregatire.md.
- verificat de supraveghetor (22 oct 14:15): pre-înregistrarea are pragurile din §8 corect calculate (baseline 6/50 → CONFIRMAT
  (b2) ≥ 16/50, INFIRMAT ≤ 9/50; (e) ≥ 27/30); baseline-ul refăcut pe procesor = cifrele S16. De acord cu cele 4 alegeri ale tale
  (filtrul „formă”, noutatea și pe tipar, excepția pentru nume luate din text, bucățile) — toate sunt mai stricte, nu mai largi.
  Rămâne `aprobat` pentru 19:00. Dacă generarea sau dus-întorsul se opresc la limita de timp, scrie în raport câte au rămas neîncercate.
- pornire (o singură comandă, oricând după 15:10 — aprobat de Adrian): `.venv/Scripts/python -X utf8 unelte/cascada.py porneste S17 -- .venv/Scripts/python.exe
  -X utf8 unelte/e1_intrebari_nascute.py noaptea` (generator 1 h → generare ≤ 60 min → filtre ≤ 45 min → antrenare 3 h din
  #415 → examene cu verificatorul + validări; ~6,5 ore).
- tip: placă (~5 ore) + procesor (~1 oră pentru filtre)
- fereastră: **oricând — PORNEȘTE ACUM** (Adrian, 22 oct 15:10, prin centrul de comandă; era: noapte 19:00–07:00, țintă noaptea 22→23).
  Executant: la prima verificare a cozii după 15:10, dacă placa e liberă, rulezi comanda de pornire de mai jos fără să aștepți 19:00.
- durată maximă: 7 ore pe placă
- ce faci: exact §8 din `docs/rapoarte/2026-10-22_0200_strategie_nucleu_fara_llm.md` (citește-l întreg). Pe scurt:
  1. **Generatorul:** aceeași arhitectură W2, pornit din #415, antrenat 1 oră pe (text, bucată) → întrebare, din perechile
     de antrenare existente (`date/conversatie/text*/antrenare.jsonl`).
  2. **Generarea:** pe 2.000 de articole puse deoparte pentru antrenare (NU cele 280 de examen; verificat automat, trebuie 0),
     8 întrebări pe bucată, temperatură 1,0, nucleu 0,9; ~1 oră pe placă.
  3. **Filtrele, toate fără LLM:** (i) dus-întors: #415 răspunde la întrebare și răspunsul trece verificatorul din S16
     (acoperire ≥ 0,8 față de bucată); (ii) noutate: primele 4 cuvinte nu apar ca început de întrebare în nicio antrenare;
     (iii) fără duplicate; (iv) trece `verifica_text` din motorul de română.
  4. Păstrezi cel mult 3.300 de întrebări (cât S11), în `date/conversatie/auto_v1/`. Raportezi câte tipuri distincte (pe
     primele 4 cuvinte) au rezultat și câte au căzut la fiecare filtru.
  5. **Antrenare 3 ore din #415** (ca noaptea 12, aceeași configurare cu datele `text_v3` + `auto_v1`; configurarea nouă o
     scrii în `config/` ca la S12 — e o copie a configurării nopții 12 cu altă cale de date și altă `cale_stare`), apoi
     examenele: S15 (b2, e), S4, val_bpb, examenul de 50 al nopții 10.
  **Notarea:** cu verificatorul din S16 (decizia 2 a lui Adrian: Qwen nu mai e judecător). Baseline-ul se citește cu ACELAȘI
  judecător: #415 notat de verificator în raportul S16 (Qwen dădea (b2) 6/50, (e) 30/30 — se scriu ambele în pre-înregistrare).
  **Pre-înregistrarea** `docs/preinregistrari/2026-10-2x_E1_intrebari_nascute.md`, scrisă de tine ÎNAINTE de pornire, cu
  criteriile din §8 copiate cuvânt cu cuvânt:
  - CONFIRMAT: (b2) ≥ baseline + 10/50 și (e) ≥ baseline − 3/30 și fără regresie pe S4 și noaptea 10.
  - INFIRMAT: (b2) < baseline + 4/50, sau tipuri distincte generate < 20 → H3-lite în forma asta se abandonează.
  - Neclar: între ele → o singură repetare cu 3× date; apoi decizie.
  Plus așteptările tale în cifre. Paznicul: placa sub 7.000 MB și 83 °C. Teste: `python -m pytest` trece. Commit + push.
  Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, datele de examen. Totul în `unelte/`, `module/`, `date/conversatie/auto_v1/`.
- pre-înregistrare: docs/preinregistrari/2026-10-22_E1_intrebari_nascute.md (scrisă de executant pe 22 oct, 12:16–12:37, înainte de pornire)
- aprobat de: direcția lui Adrian, 22 oct 01:45 (punctul 3); aprobarea finală o pune supraveghetorul după S16
- raport: docs/rapoarte/2026-10-22_2110_S17_E1_intrebari_nascute.md (NECLAR: (b2) 13/50 față de 6/50; (e) 29/30; noaptea 10 49/50, 20/20; S4 40/60)

### S18 — E1, repetarea cu 3× date („întrebări născute de Kronos”, a doua și ultima rundă)
- stare: gata
- pornită: 22 oct 23:39:43, prin cascadă (procesul 2256; placa liberă: 681 MB, 30 °C). Corectură: în pre-înregistrare
  scrie „23:38–23:55” / „între 23:28 și 23:55”; ora reală de sfârșit a pregătirii e 23:39 (înainte de pornire).
- pregătirea (executantul, 22 oct 23:28–23:39, procesor): opțiunile noi în `unelte/e1_intrebari_nascute.py` (`--dosar`,
  `--lucru`, `articole --sari/--verifica-si/--oricate`, `genereaza --samanta`, `filtreaza --deja`, `analiza`, `repetare`)
  + 7 teste noi; `config/conv_w2_auto_v2.toml`; 893 teste trec, 1 sărit. **Articole: doar 1.497 bune** (nu 4.000; sursa
  s-a terminat), toate verificările 0. Pre-înregistrarea: `docs/preinregistrari/2026-10-23_E1_repetare_3x.md` (aștept
  ~820–970 născute, adică probabil sub poarta de 1.032).
- tip: placă (~6 ore) + procesor (pregătirea, ~30 min, înainte)
- fereastră: **oricând — pornește la prima verificare a cozii** (placa e liberă de la 20:57; regula lui Adrian din 22 oct 15:10)
- durată maximă: 8 ore pe placă
- de ce: S17 a ieșit NECLAR ((b2) 13/50 față de 6/50; pragurile: CONFIRMAT ≥ 16, INFIRMAT ≤ 9). Criteriul din §8 al strategiei,
  copiat în pre-înregistrarea S17: „Neclar → o singură repetare cu 3× date; apoi decizie.” Asta e repetarea. Singura schimbare
  față de S17 e **cantitatea de întrebări născute** (3× 516 ≈ 1.548); restul rămâne la fel, ca rezultatul să se poată citi.
- ce faci:
  0. **Pregătirea, pe procesor (`CUDA_VISIBLE_DEVICES=-1`), înainte de placă:** fă `unelte/e1_intrebari_nascute.py` să primească
     ca opțiuni dosarul (`date/conversatie/auto_v2/`), articolele, sămânța, generatorul, configurarea și linia de antrenare (implicit
     tot cum era la S17, ca testele vechi să treacă). Teste noi pentru ce adaugi. `python -m pytest` trece. Commit + push.
  1. **Generatorul:** NU se mai antrenează; folosești **#422** (generatorul din S17), ca singura schimbare să fie cantitatea.
  2. **Articole:** **4.000 de articole noi**, cele de DUPĂ cele 2.000 din S17 (aceeași alegere, sămânța 1019: `articole_noi(6000)[2000:]`).
     Verificat automat, toate trebuie 0: texte de examen, texte din orice antrenare (inclusiv `auto_v1`), subiecte repetate. Dacă nu
     sunt 4.000 de articole bune, le iei pe toate câte sunt și scrii numărul în raport.
  3. **Generarea:** 8 întrebări pe bucată, temperatura 1,0, nucleu 0,9, sămânța **1023**, cel mult **150 de minute** pe placă.
     Scrii câte bucăți au rămas neîncercate.
  4. **Filtrele, exact ca la S17** (formă, duplicate, noutate pe primele 4 cuvinte și pe tipar, motorul de română, dus-întors cu
     #415 + verificatorul din S16 ≥ 0,8), cel mult **90 de minute** la dus-întors. În plus: fără duplicate față de cele 516 din
     `auto_v1`. Raportezi câte au căzut la fiecare filtru.
  5. **Datele:** `auto_v2/antrenare.jsonl` = `text_v3` (27.468) + cele 516 din `auto_v1` + cele noi (în total cel mult 3.300 născute).
     Ținta: **≥ 1.548 de întrebări născute** în total (3×). **Poartă:** dacă sunt **sub 1.032** (2×), NU antrenezi: raportezi
     „repetarea n-a putut strânge destule întrebări” cu cifrele, stare `gata`, și eu decid. Între 1.032 și 1.548: antrenezi și scrii
     de câte ori mai multe sunt (de ex. 2,4×).
  6. **Antrenare 3 ore din #415** (NU din #425), `config/conv_w2_auto_v2.toml` = copia lui `conv_w2_auto_v1.toml` cu altă cale de
     date și altă `cale_stare`, linia nouă `w2_conv_auto_v2`. Apoi examenele, la fel ca la S17: S15 (b2, e), S4, noaptea 10, și
     validările (română, cod, povești, fapte noi).
  7. **Judecătorul rămâne verificatorul din S16, neschimbat** (răspuns la întrebarea ta din raportul S17, punctul 2: baseline-ul și
     pragurile au fost notate cu el; dacă îl schimbăm acum, cifrele nu mai sunt comparabile). Raportezi **în plus, fără să decidă**:
     (a) scorul (b2) cu varianta F1 ≥ 0,8 pentru #415, #425 și modelul nou; (b) câte răspunsuri „lungi” (de peste 2× cuvintele
     referinței) au fost numărate corecte, la fiecare din cele trei; (c) (b2) fără tipurile al căror tipar apare printre întrebările
     născute păstrate (lista făcută automat, de ex. „în ce oraș se”, „cine a pictat”), pentru #415, #425 și modelul nou.
- pre-înregistrare: `docs/preinregistrari/2026-10-23_E1_repetare_3x.md`, scrisă și urcată (commit + push) ÎNAINTE de pornirea pe
  placă, cu pragurile S17 neschimbate (baseline #415 notat de verificator: (b2) 6/50, (e) 30/30):
  - CONFIRMAT: (b2) ≥ 16/50 și (e) ≥ 27/30 și fără regresie (aceleași praguri ca la S17: noaptea 10 ≥ 45/50, ≥ 16/20, refuz greșit
    ≤ 5/50; S4 (a) ≥ 9, (c) ≥ 11; validările ca la S17).
  - INFIRMAT: (b2) ≤ 9/50, sau tipuri distincte generate < 20 → H3-lite în forma asta se abandonează; trecem la E2.
  - NECLAR: (b2) 10–15/50 → **nu se mai repetă**; decizia o ia Adrian (eu îi scriu variantele).
  Plus așteptările tale în cifre (câte întrebări păstrate, (b2), verdictul cu procente) și comparația cu #425.
- Paznicul: placa sub 7.000 MB și 83 °C. Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, datele de examen, `auto_v1`.
  Totul în `unelte/`, `config/conv_w2_auto_v2.toml`, `date/conversatie/auto_v2/`. #425 și modelul nou NU intră în interfață.
- aprobat de: Adrian (22 oct 15:10, prin centrul de comandă, punctul 3: „repetarea cu 3× date dacă e neclar”) + supraveghetor,
  22 oct 23:15 (categoria 1: încă o rulare pe o linie existentă, alt amestec de date; categoria 6/5 pentru opțiunile din unealtă)
- raport: docs/rapoarte/2026-10-23_0103_S18_E1_repetare_3x.md (n-a trecut poarta: 402 noi, 918 în total < 1.032; nu s-a antrenat, fără verdict; pre-înregistrarea închisă)

### S19 — E1, analiza care a rămas nefăcută la S18: de unde vine creșterea #425 (13/50)? (doar examen + numărare, fără antrenare)
- stare: gata
- verificat de supraveghetor (23 oct 05:15): pașii 0–3 făcuți exact cum scrie; pre-înregistrarea urcată înainte de pornire
  (5c44feb 02:30:28 < pornirea 02:30:36); baseline #415 exact; cifrele din raport se potrivesc între ele (13 − 7 lungi = 6,
  6 − 2 = 4; (c) 11/42 − 4/42 = +7). Regula de citire: (c) = +7 ≥ 4 → „nu vine doar din tipurile atinse”. Dar fără răspunsurile
  lungi rămâne +2 (6 față de 4), iar cu F1 ≥ 0,8 #425 e mai slab (2/50 față de 4/50) → semnul pentru auto-joc e SLAB. Verdictul S17
  rămâne NECLAR.
- terminată: 23 oct 02:33:29, cod 0. Baseline #415 exact; diferența (c) = 7 (≥ 4), dar 7/13 la #425 sunt răspunsuri lungi și
  cu F1 ≥ 0,8 #425 are 2/50 față de 4/50 la #415. Teste: 893 trecute, 1 sărit.
- pornită: 23 oct 02:30:36, prin cascadă (procesul 27092; placa liberă: 681 MB, 30 °C), scriptul
  `lucru/cascada/S19_proba/s19.py` (pașii 1–3 unul după altul; pasul 3 doar dacă baseline-ul #415 iese exact). Pre-înregistrarea
  urcată înainte (5c44feb). Corectură: în ea scrie „02:35”; ora reală e ~02:29, înainte de pornire.
- tip: placă (cel mult 1 oră; merge și pe procesor dacă placa e ocupată) — **fără antrenare**
- fereastră: **oricând — pornește la prima verificare a cozii** (placa e liberă de la 23 oct 00:33; regula lui Adrian din 22 oct 15:10)
- durată maximă: 1 oră
- de ce: S18 n-a trecut poarta (918 < 1.032), deci E1 rămâne cu un singur rezultat: S17, NECLAR ((b2) 13/50 față de 6/50).
  Pasul următor îl alege Adrian (pre-înregistrarea: „nu se mai repetă; decizia o ia Adrian”). Ca să aleagă pe cifre, lipsește
  exact analiza de la S18 punctul 7, care n-a mai rulat din cauza porții: **cât din creșterea 6 → 13 vine din tipuri pe care
  întrebările născute le-au atins direct** (de ex. „în ce oraș se”) și cât din răspunsuri lungi care conțin răspunsul corect.
- ce faci:
  0. Verifici că în `lucru/e1/` există examenele lui **#425** din S17 (`examene_425_*.json`, cu `S15.raspunsuri`). Dacă lipsesc,
     le refaci la pasul 1 împreună cu #415.
  1. **Examenele lui #415, notate de verificator** (aceleași ca la S17/S18, fără întâmplare):
     `python -X utf8 unelte/e1_intrebari_nascute.py --lucru lucru/e1 examene --experiment 415`
     Cifrele TREBUIE să iasă cele din baseline-ul pre-înregistrat: (b2) 6/50, (e) 30/30, S4 38/60, noaptea 10 50/50 și 20/20.
     Dacă ies altele, scrii anume în raport și te oprești la pasul 2 (fără pasul 3).
  2. **Analiza, cu tiparele întrebărilor pe care #425 chiar le-a văzut la antrenare (doar `auto_v1`, cele 516):**
     `python -X utf8 unelte/e1_intrebari_nascute.py --lucru lucru/e1 analiza --experimente 415 425 --linie "" --nascute date/conversatie/auto_v1/intrebari.jsonl`
     Copiezi `lucru/e1/analiza_s18.json` în `lucru/e1/analiza_s19_auto_v1.json`.
  3. **A doua analiză, doar informativ, cu toate cele 918** (`auto_v1` + `auto_v2/intrebari.jsonl`, ca să vedem ce tipuri ar fi
     atins o eventuală antrenare pe ele): aceeași comandă cu `--nascute date/conversatie/auto_v1/intrebari.jsonl date/conversatie/auto_v2/intrebari.jsonl`;
     copiezi rezultatul în `lucru/e1/analiza_s19_toate.json`.
  4. Raportezi, pentru #415 și #425: (b2) cu verificatorul; (a) (b2) cu F1 ≥ 0,8; (b) câte răspunsuri „lungi” (peste 2× cuvintele
     referinței) au fost numărate corecte, pe categorii; (c) (b2) fără tipurile atinse de tiparele născute (x/y, pe aceleași
     întrebări rămase la ambele modele) + lista tipurilor scoase. Și diferența (c) #425 − #415.
- pre-înregistrare (scurtă, înainte de pornire, `docs/preinregistrari/2026-10-23_S19_analiza_E1.md`, commit + push): NU e un
  experiment nou și NU schimbă verdictul S17 (rămâne NECLAR). Scrii doar așteptările tale în cifre pentru (a), (b), (c) și regula
  de citire, stabilită acum de mine:
  - diferența (c) #425 − #415 **≥ 4** întrebări → creșterea nu vine doar din tipurile atinse direct (semn bun pentru auto-joc);
  - diferența (c) **≤ 2** → creșterea se explică aproape toată prin tipurile atinse sau prin răspunsuri lungi (semn slab);
  - 3 → nedecis. Cifra intră doar în variantele pe care i le scriu lui Adrian, nu în niciun verdict.
- Paznicul: placa sub 7.000 MB și 83 °C. Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, datele de examen, `auto_v1`,
  `auto_v2`, verificatorul din S16. Nicio antrenare, niciun model nou, nimic în interfață. Codul nu se schimbă (dacă o comandă
  pică, repari doar unealta, cu test, și scrii în raport — categoria 6).
- aprobat de: supraveghetor, 23 oct 02:15 (categoria 2: examene și notări pe modele existente; e analiza deja cerută la S18, pct. 7)
- raport: `docs/rapoarte/2026-10-23_0303_S19_analiza_E1.md`

### S20 — Pasul următor după E1 (decizia lui Adrian)
- stare: gata — varianta 1, aleasă de Adrian (23 oct 10:20, prin centrul de comandă): E1 se închide, se trece la E2
- de ce: E1 s-a încheiat fără verdict clar: S17 NECLAR (13/50), S18 n-a putut strânge destule întrebări (918 din 1.032; sursa de
  articole din Wikipedia descărcată s-a terminat). Pre-înregistrarea spune: „nu se mai repetă; decizia o ia Adrian.”
- variantele (Adrian alege una; scrise și în `plan/pentru_adrian.md`):
  1. **Se închide E1 cu „neclar” și se trece la E2** (3 specialiști + ruter, strategia §7). E2 nu e încă aprobat: e o direcție nouă.
  2. **O antrenare de 3 ore din #415 pe cele 918 întrebări (1,78×)**, cu o poartă nouă scrisă înainte și aceleași praguri
     (confirmat ≥ 16/50, infirmat ≤ 9/50). Datele există deja (`auto_v2/antrenare.jsonl`); ~4 ore pe placă.
  3. **Altă metodă sau altă sursă:** mai multe bucăți pe articol din articolele deja folosite (schimbare de metodă) sau articole
     noi (descărcare nouă = „da”-ul tău, cu licența verificată înainte).
- recomandarea supraveghetorului: după S19 (23 oct 05:15): **varianta 1** (închidem E1, trecem la E2). Dacă Adrian alege
  varianta 2, poarta nouă cere și F1 ≥ 0,8 (sau o limită de lungime), nu doar verificatorul — vezi S21.
- notă supraveghetor, 23 oct 08:15: după S21 recomandarea rămâne **varianta 1**. S21 arată că răspunsurile lungi apar doar la (b2);
  deci, la varianta 2, F1 ≥ 0,8 (sau limita de lungime) e nevoie doar în poarta pe (b2), pe celelalte examene verificatorul ajunge.

### S21 — Cât de „îngăduitor” e verificatorul cu răspunsurile lungi? (toate examenele, #415 și #425, doar numărare)
- stare: gata (23 oct 05:35; (i) exact ca în S17/S19; pe (e) + S4 + noaptea 10 „text”, corecte fără lungi #415 117, #425 116 →
  scade cu 1 ≤ 2: lungile țin doar de (b2); 895 teste trec, 1 sărit)
- verificat de supraveghetor (23 oct 08:15): (iv) #415 30+37+50 = 117, #425 29+38+49 = 116 → −1 ≤ 2, citirea e corectă;
  (i) identic cu S17/S19; pre-înregistrarea scrisă înainte de rulare (commit 05:29). Rezultat: răspunsurile lungi țin doar de (b2),
  „fără regresie” din S17 rămâne valabil și cu nota strictă.
- tip: procesor (fără placă, fără model încărcat — doar citește examenele deja scrise)
- fereastră: oricând — la prima verificare a cozii (după S19; nu are nevoie de placă)
- durată maximă: 1 oră (cu tot cu testul nou)
- de ce: S19 a arătat că 7 din cele 13 răspunsuri bune ale lui #425 la (b2) sunt „lungi” și că, cu F1 ≥ 0,8, #425 scade la 2/50.
  Nu știm încă dacă același lucru se întâmplă la tipurile văzute (e), la S4 și la noaptea 10 — adică dacă și „fără regresie” din
  S17 (e 29/30, S4 40/60) stă pe răspunsuri lungi. Cifra asta trebuie să existe înainte ca Adrian să aleagă la S20 și înainte de
  orice poartă nouă (varianta 2 sau E2): altfel riscăm să antrenăm modelul spre „copiază mai mult text”.
- ce faci:
  1. În `unelte/e1_intrebari_nascute.py` adaugi o comandă nouă `lungimi` (categoria 5: unealtă nouă, fără să schimbi ce există):
     `python -X utf8 unelte/e1_intrebari_nascute.py --lucru lucru/e1 lungimi --experimente 415 425`
     Citește ultimele `examene_<id>_*.json` din `lucru/e1/` (pentru #415: `examene_415_20261023_023327.json`; pentru #425:
     `examene_425_20261022_205650.json`) și, pe fiecare examen (S15 pe categorii — b2, e și celelalte —, S4 pe categorii a/b/c/d,
     noaptea 10 „text” și „nu scrie”; fără conversația simplă), scoate:
     (i) corecte cu verificatorul (trebuie să iasă exact cifrele din rapoartele S17/S19 — dacă nu, scrii și te oprești);
     (ii) corecte cu F1 ≥ 0,8 (`corect_f1` din `verifica`);
     (iii) câte din cele corecte sunt „lungi” (peste 2× cuvintele referinței, aceeași definiție ca `analiza_b2`);
     (iv) corecte fără cele lungi;
     (v) mediana numărului de cuvinte al răspunsului elevului și al referinței.
     Scrie totul în `lucru/e1/lungimi_s21.json` și tipărește un tabel. Nu se rulează niciun model; `verifica` și verificatorul S16
     rămân neschimbate.
  2. Un test nou în `teste/test_e1_intrebari_nascute.py` pentru `lungimi` (2–3 răspunsuri inventate: unul scurt corect, unul lung
     corect, unul greșit → cifrele așteptate). Apoi `python -m pytest`: toate trebuie să treacă.
  3. Raportul: tabelul #415 / #425 pe fiecare examen și categorie, cu (i)–(v) și diferențele.
- pre-înregistrare (scurtă, înainte de rulare, `docs/preinregistrari/2026-10-23_S21_lungimi.md`, commit + push): NU e experiment
  și NU schimbă niciun verdict. Scrii așteptările tale în cifre pentru (ii) și (iii) la (e), S4 și noaptea 10, pentru ambele modele,
  și regula de citire (stabilită acum de mine, doar informativă, pentru variantele lui Adrian):
  - dacă la #425, pe (e) + S4 + noaptea 10 „text” la un loc, „corecte fără cele lungi” scade cu **≥ 5** față de #415 → „fără regresie”
    din S17 stă pe răspunsuri lungi; orice antrenare viitoare are nevoie de o poartă cu F1 sau limită de lungime;
  - **≤ 2** → răspunsurile lungi țin doar de (b2); verificatorul e în regulă pe tipurile învățate;
  - 3–4 → nedecis.
- Paznicul: nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, datele de examen, `auto_v1`, `auto_v2`,
  `unelte/verificator_text.py`. Fără placă, fără antrenare, fără descărcări, nimic în interfață. Doar comanda nouă + testul ei.
- aprobat de: supraveghetor, 23 oct 05:15 (categoria 2: notări pe examene existente; categoria 5: comandă nouă în `unelte/`, cu test)
- raport: `docs/rapoarte/2026-10-23_0535_S21_lungimi.md`

### S22 — E2, pregătirea (procesor): 3 familii de întrebări, ruterul, pre-înregistrarea
- stare: gata (23 oct 10:36; F1 20.564 / F2 4.083 / F3 2.821; ruterul (1–5 cuvinte, prag 2, ales pe validare 93,7 %) pe examene
  189/210 = 90,0 % → poarta trece la limită; #415 pe familii 101 + 13 + 30 = 144 ✓; pre-înregistrarea E2 urcată (val_bpb ≤ 0,4511
  pus de mine: S17 n-avea prag); 900 teste trec, 1 sărit)
- tip: procesor (fără placă: `CUDA_VISIBLE_DEVICES=-1`; nu se încarcă niciun model)
- fereastră: oricând — la prima verificare a cozii
- durată maximă: 3 ore
- de ce: Adrian a aprobat E2 (23 oct 10:20): **3 specialiști + ruter**, antrenați pe rând din #415 (Branch-Train-Merge), strategia
  `docs/rapoarte/2026-10-22_0200_strategie_nucleu_fara_llm.md` §4 H4 și §7 E2 (citește-le). S22 face tot ce nu cere placa, ca S23 să fie doar rularea.
- ce faci (totul într-o unealtă nouă `unelte/e2_specialisti.py`, cu teste noi în `teste/test_e2_specialisti.py`):
  1. **Familiile, cu o regulă fixă, fără model** (aceeași regulă pentru antrenare și pentru examene):
     - **F2 „da/nu”:** răspunsul de referință e „Da.” sau „Nu.”;
     - **F3 „tipurile din S11”:** perechea vine din tipurile adăugate la S11 (`date/conversatie/text_v3/tipuri_noi.jsonl`; la examene:
       S15 categoria (e)) și nu e da/nu;
     - **F1 „fapte / nume / ani / locuri”:** tot restul (inclusiv „Nu scrie în text.” al tipurilor vechi, S4 (a)(b)(d), S15 (b2), noaptea 10).
     Comanda `imparte`: din `date/conversatie/text_v3/antrenare.jsonl` (27.468) scrie `date/conversatie/e2/f1/antrenare.jsonl`,
     `f2/…`, `f3/…` (fiecare pereche în exact o familie; suma = 27.468, verificat automat) și `date/conversatie/e2/info.json` cu numărul
     pe familie. Pune deoparte 10 % din articole (după grupul `text_<i>`, sămânța 1023) ca `e2/ruter_validare.jsonl` — DOAR pentru ruter,
     specialiștii se antrenează pe tot. Dacă o familie are sub 2.000 de perechi, scrii cifra în raport (nu schimbi regula).
  2. **Ruterul** (comanda `ruter`): tabel învățat doar din întrebările de antrenare (fără cele 10 % puse deoparte): pentru începuturile
     de 1, 2 și 3 cuvinte (litere mici, fără semne), familia cea mai des întâlnită, dacă apare de cel puțin 5 ori; se folosește cel mai
     lung început găsit; altfel F1. Scris în `date/conversatie/e2/ruter.json`. Fără model, fără examene la construire.
  3. **Măsurarea ruterului** (comanda `masoara-ruter`): (i) pe `ruter_validare.jsonl`; (ii) pe TOATE întrebările examenelor S15 (b2, e),
     S4 și noaptea 10 (aceleași 210 ca la S17/S19), cu familia „corectă” dată de regula de la pasul 1. Ruterul se poate ajusta (ex. 4
     cuvinte, alt prag) DOAR după (i); (ii) se rulează o singură dată, cu ruterul final, și se scrie ce a ieșit. Raportezi procentul pe
     fiecare examen și familie + lista greșelilor de la (ii).
     **Poartă:** dacă (ii) < 90 %, S23 NU pornește: scrii cifrele și stare `gata`, eu decid (de ex. clasificatorul mic din strategie).
  4. **Baseline-ul pe familii:** din examenele deja scrise ale lui #415 (`lucru/e1/examene_415_20261023_023327.json`), câte corecte are
     #415 pe întrebările fiecărei familii (verificatorul S16 și separat F1 ≥ 0,8). Total verificator trebuie să iasă 144/210
     ((b2) 6 + (e) 30 + S4 38 + noaptea 10 50 + 20); dacă nu, scrii și te oprești.
  5. **Configurările:** `config/conv_w2_spec_f1.toml`, `…_f2.toml`, `…_f3.toml` = copii ale `config/conv_w2_text_v3.toml` (noaptea 12, din
     care a ieșit #415), diferă doar `nume` (`w2_spec_f1`/`f2`/`f3`, linii noi), `conversatie` (fișierul familiei) și `cale_stare`
     (`lucru/w2_spec_fX/gpt.pt`). Verificat cu `diff`. Directoarele `lucru/w2_spec_*` nu trebuie să existe (ca `--porneste-din 415` să se aplice).
  6. **Nota sistemului, fără model** (comanda `sistem`): primește ruterul și câte un fișier `examene_<id>_*.json` pentru fiecare
     specialist; pentru fiecare întrebare ia răspunsul specialistului ales de ruter și îl notează cu verificatorul S16 (și F1).
     Test cu răspunsuri inventate (2 specialiști, 4 întrebări). Așa S23 nu are nevoie de cod nou pe placă.
  7. **Pre-înregistrarea E2** `docs/preinregistrari/2026-10-23_E2_specialisti.md`, commit + push ÎNAINTE de S23, cu cifrele de la pașii
     1–4 și criteriile lui Adrian (10:20), copiate:
     - **CONFIRMAT:** (A) **fără regresie pe niciun specialist**: specialistul k, pe întrebările familiei k din S4 + S15 + noaptea 10,
       are cel puțin cât #415 pe aceleași întrebări, minus 1; și validările (val_bpb, română, cod, povești, fapte noi) în aceleași praguri
       ca la S17; **și** (B) **sistemul (ruter + specialiști) ≥ #415 monolit** pe toate cele 210 întrebări (≥ 144, cu verificatorul S16);
       **și** (C) **ruterul alege corect ≥ 90 %** (cifra de la pasul 3 (ii)).
     - **INFIRMAT:** oricare din (A), (B), (C) nu e îndeplinit → scrii care, cu cifrele.
     - **În plus, fără să decidă:** sistemul și #415 cu F1 ≥ 0,8 (pe (b2) separat), răspunsurile „lungi” (ca la S21), sistemul cu
       „ruter perfect” (familia corectă) — ca să vedem cât pierde ruterul.
     Plus așteptările tale în cifre (fiecare specialist pe familia lui, sistemul, verdictul cu procente).
  8. `python -m pytest`: toate trec. Commit + push. Raport `docs/rapoarte/2026-10-23_<ora>_S22_E2_pregatire.md` (cifrele de la 1–4, diff-ul
     configurărilor, așteptările).
- Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, datele de examen, `text_v3`, `auto_v1`, `auto_v2`,
  `unelte/verificator_text.py`. Nicio descărcare, nimic în interfață.
- pre-înregistrare: e chiar pasul 7 (pentru S23); S22 nu antrenează
- aprobat de: Adrian (23 oct 10:20, prin centrul de comandă, punctul 2: tot E2) + supraveghetor, 23 oct 10:30 (categoriile 3 și 5)
- raport: docs/rapoarte/2026-10-23_1036_S22_E2_pregatire.md

### S23 — E2, rularea (placa): 3 specialiști din #415, pe rând, apoi examenele și nota sistemului
- stare: gata (executant, 23 oct 18:03: lanțul 11:00–17:31, cod 0; INFIRMAT: (A) F1 98/165 < 100, (B) sistemul 137/210 < 144; (C) 90,0 % ✓; 900 teste trec; placa liberă)
- stare veche: aprobat — pornește DOAR după: S22 `gata`, pre-înregistrarea E2 urcată (commit înainte de pornire), ruterul ≥ 90 % la S22 pasul 3 (ii)
- tip: placă (~7 ore)
- fereastră: oricând — la prima verificare a cozii după condițiile de mai sus (regula lui Adrian din 22 oct 15:10)
- durată maximă: 8 ore pe placă
- ce faci (un singur lanț prin cascadă: `cascada.py porneste S23 -- …`, un pas după altul, fiecare pas doar dacă cel dinainte a ieșit cu cod 0):
  1. **Specialistul F1:** `python unelte/antrenare_lunga.py --config config/conv_w2_spec_f1.toml --ore 2 --porneste-din 415`
  2. **Specialistul F2:** la fel cu `conv_w2_spec_f2.toml`, **tot din #415** (nu din F1), 2 ore.
  3. **Specialistul F3:** la fel cu `conv_w2_spec_f3.toml`, din #415, 2 ore.
  4. **Examenele** pe fiecare specialist, ca la S17/S19: `python -X utf8 unelte/e1_intrebari_nascute.py --lucru lucru/e2 examene --experiment <id>`
     + validările (română, cod, povești, fapte noi, val_bpb) ca la S17.
  5. **Nota sistemului:** `python -X utf8 unelte/e2_specialisti.py sistem …` (S22 pasul 6), cu ruterul din S22 și cele 3 fișiere de examen.
  6. Verdictul după pre-înregistrare (A, B, C), cu toate cifrele „în plus”. Raport `docs/rapoarte/2026-10-2x_<ora>_S23_E2_specialisti.md`.
     La pornire scrii în coadă **ora estimată de sfârșit** (Adrian are nevoie de workstation ~30–60 min când se întoarce).
- Dacă un pas pică de 2 ori la rând cu aceeași eroare: te oprești, stare `oprit`, scrii eroarea în raport (regula lui Adrian, 10:20).
- Paznicul: placa sub 7.000 MB și 83 °C. Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, datele de examen, `text_v3`, ruterul
  după S22. Specialiștii NU intră în interfață (rămâne #407). Teste: `python -m pytest` trece înainte de `gata`. Commit + push.
- pre-înregistrare: docs/preinregistrari/2026-10-23_E2_specialisti.md (scrisă la S22, urcată înainte de pornire)
- aprobat de: Adrian (23 oct 10:20, prin centrul de comandă, punctul 2: E2 aprobat, „antrenare nouă”) + supraveghetor, 23 oct 10:30
- raport: docs/rapoarte/2026-10-23_1803_S23_E2_specialisti.md (INFIRMAT)
- verificat de supraveghetor, 23 oct 20:15: cifrele se adună (144 / 137 / 142), verdictul INFIRMAT e corect după pre-înregistrare. E2 închis.

### S24 — E3, pregătirea (procesor): indexul propriu de memorie peste Wikipedia în română și cât de bine găsește
- stare: gata (executant, 23 oct 21:15: pașii 1, 2, 3, 5 cod 0 la 20:50; așteptările urcate 4a9fb68; pasul 4 cod 0: 160 de întrebări,
  (i) k = 1/5/20: 64,4 / 80,6 / 92,5 %, (ii) articolul la 5: 84,4 %; 904 teste trec, 1 sărit; pragul E3 îl decide Adrian)
- pornit: 23 oct 20:34 (executant, procesul 10976): lanțul pașilor 1, 2, 3, 5 (`lucru/cascada/S24_proba/s24.py`; sfârșit estimat
  ~21:00). Pasul 4 (examenele) îl rulez la verificarea următoare, după ce așteptările sunt scrise și urcate. 904 teste trec, 1 sărit.
- tip: procesor (fără placă: `CUDA_VISIBLE_DEVICES=-1`; nu se încarcă niciun model)
- fereastră: oricând — la prima verificare a cozii (S23 e gata, placa e liberă)
- durată maximă: 4 ore; memorie RAM cel mult ~40 GB
- de ce: Adrian (23 oct 10:20, punctul 3): după E2, „pregătirea E3 (memoria) doar pe procesor — indexul propriu peste articolele deja
  descărcate și măsurarea lui; fără antrenare E3 până nu decide Adrian”. Strategia `docs/rapoarte/2026-10-22_0200_strategie_nucleu_fara_llm.md`
  §4 H2 și §7 E3 (citește-le). Întrebarea de azi e doar: **dacă îi dăm lui Kronos o întrebare, găsește indexul nostru, fără niciun model,
  bucata de text în care e răspunsul?** Dacă nu o găsește, antrenarea E3 n-are sens; dacă o găsește, Adrian are cifre ca să decidă.
- ce faci (totul într-o unealtă nouă `unelte/e3_memorie.py`, cu teste noi în `teste/test_e3_memorie.py`):
  1. **Indexul** (comanda `index`): din `date/ws/curat/wikipedia_ro/antrenare.txt` (copia deja descărcată și curățată; nimic nou descărcat),
     fiecare articol tăiat în **bucăți** de aceeași mărime ca bucățile de text de la „răspuns din text” (citește în `unelte/conversatie_text.py`
     cum se taie; dacă nu se poate potrivi exact, ~600 de caractere, tăiat la sfârșit de propoziție — scrii ce ai ales). Fiecare bucată ține
     `articol`, `nr` și textul. Căutarea: **SQLite FTS5 cu BM25** (e în Python, fără instalare; verifici întâi că `fts5` există), cu tokenizerul
     `unicode61` (ș/ş și ț/ţ unificate înainte de indexare, în text și în întrebare). Dacă FTS5 lipsește, un index inversat propriu cu BM25
     (k1 = 1,2, b = 0,75). Fără model, fără rețea. Indexul în `lucru/e3/index.sqlite` (NU în Git). Scrii: câte articole, câte bucăți,
     mărimea pe disc, RAM-ul maxim, timpul de construire.
  2. **Documente noi = învățate instant** (comanda `adauga`): adaugă în index textele examenelor care **nu** sunt deja în el (S15
     `docs/conversatie/examen_generalizare_mare.json`, S4 `docs/conversatie/examen_generalizare_401.json`, noaptea 10
     `date/conversatie/text/examen.json`), tăiate la fel, marcate `sursa = examen`. Raportezi câte texte de examen erau deja în Wikipedia
     (potrivire exactă a textului normalizat) și câte s-au adăugat, plus timpul de adăugare pe text. Fișierele de examen doar se citesc.
  3. **Ajustarea doar pe validare** (comanda `masoara --set validare`): 500 de întrebări luate la întâmplare (sămânța 1024) din
     `date/conversatie/text_v3/antrenare.jsonl`, doar cele cu răspuns care apare în text (nu „Nu scrie în text.”, nu da/nu). O căutare e
     „bună la k” dacă printre primele k bucăți e una care conține răspunsul de referință (normalizat, cu aceeași potrivire ca verificatorul S16,
     `unelte/verificator_text.py`, doar citit, nu schimbat). Poți încerca cel mult 6 variante (de ex. întrebarea întreagă / fără cuvintele de
     întrebare „cine, ce, când, unde, în, a, al…” / cu sau fără prefixe de cuvânt) **numai pe validare**; o alegi pe cea mai bună la k = 5.
  4. **Examenele, o singură rulare** cu varianta aleasă (comanda `masoara --set examene`): toate întrebările din S15 (b2, e), S4 (a, b, d) și
     noaptea 10 „text” care au răspunsul în text (fără „Nu scrie”, fără da/nu (c); scrii câte rămân, ~160). Pentru fiecare: e bună la k = 1, 5, 20?
     Separat: **(i) căutarea în tot indexul** (Wikipedia + examene) și **(ii) găsirea articolului corect** (măcar o bucată din textul de examen
     în primele 5, indiferent de răspuns). Raportezi procentele pe fiecare examen și total, timpul median și maxim pe întrebare, plus
     20 de greșeli alese la întâmplare (sămânța 1024), cu întrebarea, răspunsul și primele 3 bucăți găsite (primele 200 de caractere).
  5. **Documentele lungi** (doar măsurare): pentru textele de examen, de câte ori sunt mai lungi decât contextul modelului (512 simboluri,
     cu tokenizerul Kronos, doar citit), și câte articole Wikipedia au peste 10 × 512 simboluri — pentru experimentul H2 din strategie
     („documente de 10× mai lungi decât contextul”).
  6. **Așteptările tale în cifre** la pasul 4, scrise în raport ÎNAINTE de rularea lui (commit + push înainte), plus o propunere de prag
     pentru E3: de exemplu „antrenarea E3 are sens doar dacă găsește răspunsul în primele 5 la ≥ 80 % din întrebări”. Pragul îl decide Adrian.
  7. `python -m pytest`: toate trec. Commit + push. Raport `docs/rapoarte/2026-10-2x_<ora>_S24_E3_index.md`, cu tot ce e mai sus și cu
     propunerea ta pentru pasul următor (E3 cu antrenare: ce date, câte ore, ce examene, ce criterii) — **doar propunere, nu o pornești**.
- Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, datele de examen (doar citire), `text_v3`, `e2/`, `unelte/verificator_text.py`.
  Nimic pe placă, nimic descărcat, nimic instalat, nimic în interfață. Indexul și bucățile nu intră în Git (licența Wikipedia: CC BY-SA; doar local).
- Dacă ceva pică de 2 ori la rând cu aceeași eroare: stare `oprit`, scrii eroarea în raport.
- pre-înregistrare: nu e antrenare; așteptările în cifre se scriu în raport înainte de pasul 4 (pasul 6)
- aprobat de: Adrian (23 oct 10:20, prin centrul de comandă, punctul 3: pregătirea E3 doar pe procesor) + supraveghetor, 23 oct 20:15 (categoriile 2, 3 și 5)
- raport: docs/rapoarte/2026-10-23_2100_S24_E3_index.md (în primele 5 la 80,6 %, articolul la 84,4 %; 17/160 cu răspunsul nepotrivit
  de verificator nici în textul examenului → cifrele sunt o limită de jos)
- verificat de supraveghetor, 23 oct 23:15: sumele pe examene se potrivesc (103 / 129 / 148 / 135 din 160); așteptări urcate înainte de
  rularea unică ✓. Rezultat: indexul găsește răspunsul în primele 5 la 4 din 5 întrebări, fără model, în ~65 ms; pragul E3 îl decide Adrian.

### S25 — E3, pregătirea (procesor): căutarea mai bună, ajustată doar pe validare, apoi o singură rulare pe examene
- stare: gata
- pornit: 23 oct 23:38 (executant, procesul 6676): lanțul `liste` + `masoara --set validare --runda s25`
  (`lucru/cascada/S25_proba/s25.py`; sfârșit estimat ~23:55). Regulile și cele 6 variante urcate înainte (e2d3726); 907 teste trec, 1 sărit.
  Examenele (o singură rulare) le rulez după ce așteptările sunt scrise și urcate. Placa nu e folosită: e liberă oricând pentru Adrian.
- tip: procesor (fără placă: `CUDA_VISIBLE_DEVICES=-1`; nu se încarcă niciun model)
- fereastră: oricând — la prima verificare a cozii
- durată maximă: 3 ore; memorie RAM cel mult ~40 GB
- de ce: pasul 1 din propunerea ta din raportul S24 („întâi, fără antrenare”). Adrian (23 oct 10:20, punctul 3) a aprobat pregătirea E3 doar
  pe procesor. Azi indexul are 80,6 % (i, k = 5) și 84,4 % (ii); vrem să știm cât urcă doar din căutare, ca Adrian să decidă E3 pe cifre bune.
- ATENȚIE la curățenia măsurării: ideile (a)–(c) au venit din greșelile de pe examene, deci examenele nu mai sunt complet „neatinse”. De aceea:
  regulile se scriu GENERAL (nu după exemplele văzute), se ajustează doar pe validare, iar examenele se rulează o singură dată. Raportezi
  cinstit că ideile au venit din greșelile S24.
- ce faci (în `unelte/e3_memorie.py`, comenzi/variante noi; testele noi în `teste/test_e3_memorie.py`; indexul existent `lucru/e3/index.sqlite` se refolosește, nu se reconstruiește decât dacă (c) o cere — atunci într-un fișier nou, `lucru/e3/index_s25.sqlite`, cel vechi rămâne):
  1. **(a) Potrivirea „număr gol”, doar în unealta E3:** o bucată e bună și dacă răspunsul de referință e un an/număr cu cuvinte de umplutură
     („În 1966.”, „Din 2019.”, „238.136 de locuitori.”) și bucata conține acel număr ca cuvânt întreg. Regula: scoți din referință cuvintele de
     legătură (în, din, de, la, anul…) și, dacă rămâne doar un număr, cauți numărul. `unelte/verificator_text.py` NU se schimbă. Raportezi
     **toate cifrele în ambele feluri**: cu potrivirea S16 (comparabilă cu S24) și cu potrivirea nouă, una lângă alta.
  2. **(b) Numele proprii cântăresc mai mult:** cuvintele cu majusculă care nu sunt la începutul întrebării (și perechile lor) primesc o pondere
     mai mare în interogare (de ex. obligatorii sau repetate). **(c) Paginile-listă și de dezambiguizare coborâte sau scoase**, după reguli
     generale scrise în raport înainte de măsurare (titlu/început de articol: „Listă de”, „poate să însemne”, „se poate referi la”, „(dezambiguizare)”,
     pagini cu proporție mare de rânduri scurte — alegi reguli simple și le scrii), nu după articolele văzute în greșelile S24.
  3. **Ajustarea doar pe validare:** aceleași 500 de întrebări din S24 (sămânța 1024, comparabile) **plus** 500 noi (sămânța 2048, fără cele
     din primul eșantion, tot din `text_v3/antrenare.jsonl`, aceleași filtre) ca să vezi dacă câștigul ține pe întrebări neatinse. Cel mult
     6 variante noi (combinații de b și c, pornind de la varianta S24 „fără cuvinte + perechi”). Alegi una singură, după k = 5 pe ambele
     eșantioane de validare luate împreună (la egalitate k = 1), cu potrivirea S16.
  4. **Așteptările tale în cifre** pentru examene (i k = 1/5/20 și ii, în ambele potriviri), scrise în raport și **urcate (commit + push)
     ÎNAINTE** de rularea pe examene.
  5. **Examenele, o singură rulare** cu varianta aleasă, aceleași 160 de întrebări ca la S24, aceleași tabele (pe examen și total, timpul
     median/maxim), în ambele potriviri, alături de cifrele S24. Plus: câte din cele 31 de greșeli S24 la k = 5 s-au reparat și câte întrebări
     care erau bune la S24 s-au stricat (lista lor, cu întrebarea și locul vechi/nou).
  6. `python -m pytest`: toate trec. Commit + push. Raport `docs/rapoarte/2026-10-2x_<ora>_S25_E3_cautare.md`, cu tot ce e mai sus și cu
     propunerea ta actualizată pentru E3 cu antrenare (doar propunere; nu o pornești).
- Pragul de citire (supraveghetorul, scris acum, înainte): câștig real = varianta aleasă urcă (i) k = 5 cu **≥ 3 puncte** pe validarea nouă
  (sămânța 2048) față de varianta S24, cu potrivirea S16. Sub 3 puncte pe validarea nouă: câștigul e în zgomot, chiar dacă pe examene urcă.
- Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, datele de examen (doar citire), `text_v3`, `e2/`, `unelte/verificator_text.py`.
  Nimic pe placă, nimic descărcat, nimic instalat, nimic în interfață, nimic din `lucru/e3/` în Git.
- Dacă ceva pică de 2 ori la rând cu aceeași eroare: stare `oprit`, scrii eroarea în raport.
- pre-înregistrare: nu e antrenare; așteptările în cifre se scriu în raport și se urcă înainte de pasul 5 (pasul 4)
- aprobat de: supraveghetor, 23 oct 23:15 (categoriile 2 și 5; pregătirea E3 doar pe procesor, aprobată de Adrian 23 oct 10:20, punctul 3)
- raport: docs/rapoarte/2026-10-23_2335_S25_E3_cautare.md (aleasa `nume_obligatorii_liste`; pe validarea nouă +0,2 puncte la k = 5 →
  NU e câștig real după prag; pe examene, o singură rulare: (i) k = 5 80,6 → 86,9 %, (ii) 84,4 → 90,6 %, 10 reparate, 0 stricate —
  umflat, ideile au venit din greșelile de pe examene; 907 teste trec, 1 sărit)

### S26 — E3, examenul nou neatins (procesor): 100 de întrebări noi, o singură măsurare a căutării, plus „primele 3 bucăți”
- stare: gata (executant, 24 oct 02:45: 100 de întrebări, sha256 3501f307…f523; așteptările urcate cb7b461; o rulare: aleasa S16
  k = 5 80 %, (ii) 84 %, k = 3 72 % (plafonul); 6,9 puncte sub cele 160 → umflate după regulă; S24 78 %; 908 teste trec, 1 sărit)
- tip: procesor (fără placă: `CUDA_VISIBLE_DEVICES=-1`; nu se încarcă niciun model)
- fereastră: oricând — la prima verificare a cozii
- durată maximă: 1,5 ore; memorie RAM cel mult ~40 GB
- de ce: cele 160 de întrebări E3 au fost văzute de două ori de căutare (S24, S25), deci cifrele lor sunt umflate. Adrian are nevoie de o cifră
  curată ca să aleagă pragul E3, iar E3 cu antrenare (S27, dacă o aprobă) are nevoie de un examen pe care nu l-a atins nimeni. Punctul 3 din
  propunerea ta din S25. Plus plafonul nemăsurat: cât de des e răspunsul în primele 3 bucăți (exact ce ar primi modelul în E3).
- ce faci (în `unelte/e3_memorie.py`, comenzi noi; teste noi în `teste/test_e3_memorie.py`; indexul `lucru/e3/index.sqlite` neschimbat):
  1. **Examenul nou:** 100 de întrebări din `text_v3/antrenare.jsonl`, sămânța **4096**, aceleași filtre ca la eșantioanele de validare S25,
     **fără nicio întrebare și niciun articol** comun cu eșantioanele 1024 și 2048 și cu cele 160 de examene. Le salvezi ca listă fixă
     (`lucru/e3/examen_nou_4096.json`) și scrii în raport amprenta lor (sha256 al fișierului) și câte articole distincte au. De acum, aceste 100
     de întrebări **nu se folosesc la nicio ajustare și nicio antrenare** (S27 trebuie să le scoată din datele de antrenare, cu tot cu articolele lor).
  2. **Fără nicio schimbare de reguli:** nu ajustezi nimic. Variantele măsurate: S24 „fără cuvinte + perechi” și aleasa S25 `nume_obligatorii_liste`.
  3. **Așteptările tale în cifre** (k = 1/3/5/20 și (ii), potrivirea S16 și cea nouă, ambele variante), scrise în raport și **urcate (commit + push)
     ÎNAINTE** de măsurare. Reperul cinstit e validarea 2048 (S24 84,6 %, aleasa 84,8 % la k = 5).
  4. **Măsurarea, o singură rulare** pe cele 100: aceleași tabele ca la S25, cu **k = 3 în plus**. Tot o singură dată adaugi k = 3 și pe cele
     160 de examene vechi și pe validarea 2048, pentru aleasă (doar numărare, fără nicio alegere pe baza lor).
  5. `python -m pytest`: toate trec. Commit + push. Raport `docs/rapoarte/2026-10-24_<ora>_S26_E3_examen_nou.md`.
- Citirea (supraveghetorul, scrisă acum, înainte): cifra oficială pentru pragul E3 al lui Adrian = aleasa pe cele 100 noi, potrivirea S16, la
  k = 5 și (ii). Dacă aleasa iese cu **≥ 5 puncte sub** cifra ei de pe cele 160 la k = 5, spunem limpede că cifrele de pe cele 160 erau umflate.
  Plafonul pentru E3 cu model = aleasa la k = 3 pe cele 100.
- Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, datele de examen (doar citire), `text_v3` (doar citire), `e2/`,
  `unelte/verificator_text.py`. Nimic pe placă, nimic descărcat, nimic instalat, nimic în interfață, nimic din `lucru/e3/` în Git.
- Dacă ceva pică de 2 ori la rând cu aceeași eroare: stare `oprit`, scrii eroarea în raport.
- pre-înregistrare: nu e antrenare; așteptările în cifre se scriu în raport și se urcă înainte de pasul 4 (pasul 3)
- aprobat de: supraveghetor, 24 oct 02:15 (categoriile 2, 3 și 5; pregătirea E3 doar pe procesor, aprobată de Adrian 23 oct 10:20, punctul 3)
- raport: docs/rapoarte/2026-10-24_0232_S26_E3_examen_nou.md

### S27 — E3 cu antrenare (placa): index + model, din #415
- stare: gata (executant, 26 oct 21:04: **CONFIRMAT la limită** — (a) 60/100 (#415 în aceeași rulare: 57), noaptea 10 69/70
  (#415 70), S4 39/60 (#415 38); plafonul real 64/100; validările în praguri; 910 teste trec. Istoric: 26 oct 16:52: pașii 1–3 gata (7f756ef: 14.540 de exemple; de obicei încap doar 2 bucăți în 512 −
  64 simboluri — scris în pre-înregistrare); **antrenarea 16:52–20:03, cod 0 (#436, #437, #438; jurnalul mutat în
  lucru/cascada/S27_1652.*)**; unealta de examen `unelte/e3_examen.py` cu test (5bb6d95, 910 teste trec); **examenele (a)–(d)
  pornite la 20:35 prin cascadă (procesul 14756, `lucru/cascada/S27_proba/s27_examene.py`), placa ocupată până pe la ~21:15**. Rămas: pașii
  5–6, raportul; aprobat de Adrian, 26 oct 16:10, prin centrul de comandă; criteriile propuse: ≥ 60 % confirmat, < 45 % infirmat, ≤ 2 puncte pierdute pe noaptea 10 / S4)
- tip: placă (~4–5 ore în total)
- fereastră: oricând — la prima verificare a cozii (regula lui Adrian din 22 oct 15:10); S26 e `gata`
- durată maximă: 3 ore de antrenare + examene; cel mult 6 ore pe placă în total
- de ce: propunerea executantului din S25 (punctul 2), aprobată de Adrian. Întrebarea: **dacă Kronos își caută singur textul în indexul propriu
  și îl citește, răspunde corect fără să i se dea textul?** Strategia: `docs/rapoarte/2026-10-22_0200_strategie_nucleu_fara_llm.md` §4 H2, §7 E3.
- ce faci:
  1. **Datele (procesor, `CUDA_VISIBLE_DEVICES=-1`), comandă nouă `date-antrenare` în `unelte/e3_memorie.py`, cu test nou în
     `teste/test_e3_memorie.py`:** din `date/conversatie/text_v3/antrenare.jsonl`, întrebările „text” (aceleași filtre ca la S25/S26), **fără**:
     cele 100 de întrebări S26 (verifici amprenta `3501f307…f523`) și **toate bucățile celor 113 articole ale lor**, cele 160 de examene vechi
     (întrebări + texte) și eșantionul de validare 2048 (rămâne validarea curată a sistemului). Pentru fiecare întrebare, textul dat = **primele
     3 bucăți aduse de căutarea aleasă `nume_obligatorii_liste`**, în ordinea căutării; răspunsul țintă = răspunsul perechii. Scrii câte exemple,
     la câte e răspunsul în cele 3 bucăți (după verificatorul S16) și câte articole au fost scoase. Fișierul în `lucru/e3/` (nu în Git).
  2. **Configurarea `config/conv_w2_e3_memorie.toml`** = copie a `config/conv_w2_text_v3.toml` (rețeta lui #415, noaptea 12), cu `nume = "w2_conv_e3_memorie"`
     și o singură schimbare, amestecul: cei 45 % de perechi devin **30 % exemple E3 (pasul 1) + 15 % perechile vechi text_v3** (ca să nu uite
     „răspuns din textul dat”); 5 % hrană și 50 % text vechi rămân. Rata, lotul, mărimea modelului: neschimbate.
  3. **Pre-înregistrarea** `docs/preinregistrari/2026-10-26_E3_memorie.md`, **urcată (commit + push) ÎNAINTE de pornirea antrenării**: criteriile
     lui Adrian cuvânt cu cuvânt (confirmat: sistemul răspunde corect la **≥ 60 %** din cele 100 S26 fără text dat **și** nu pierde mai mult de
     **2 puncte** pe noaptea 10 / S4 cu textul dat, față de #415; infirmat: **sub 45 %**; între ele: NECLAR), unitatea exactă a „punctelor” (aceeași
     ca în rapoartele S17/S23), notarea (verificatorul S16, potrivirea S16), plafonul 72 % și așteptările tale în cifre. Placa sub 7.000 MB și 83 °C.
  4. **Antrenarea:** `cascada.py porneste S27 -- python unelte/antrenare_lunga.py --config config/conv_w2_e3_memorie.toml --ore 3 --porneste-din 415`.
     La pornire scrii în coadă **ora estimată de sfârșit** (Adrian are nevoie de workstation ~30–60 min pentru OS/GPU; o anunță centrul de comandă).
  5. **Examenele (după antrenare), o singură rulare pe modelul nou și, în aceeași rulare, pe #415 (baseline-ul sistemului fără antrenare):**
     (a) **oficial:** cele 100 S26 — sistemul primește doar întrebarea, caută primele 3 bucăți, modelul răspunde; notat cu verificatorul S16;
     scrii și câte corecte sunt dintre cele 72 cu răspunsul în bucăți și câte dintre cele 28 fără; (b) în plus (umflate): cele 160 vechi, la fel;
     (c) **regresia:** noaptea 10 și S4 cu textul dat, față de #415; (d) validările obișnuite ca la S23 (română, cod, povești, fapte noi, val_bpb).
  6. Verdictul după pre-înregistrare, cu toate cifrele. `python -m pytest`: toate trec. Commit + push.
     Raport `docs/rapoarte/2026-10-2x_<ora>_S27_E3_memorie.md`.
- Dacă un pas pică de 2 ori la rând cu aceeași eroare: te oprești, stare `oprit`, scrii eroarea în raport.
- Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, datele de examen și `text_v3` (doar citire), lista S26, indexul
  `lucru/e3/index.sqlite` (doar citire), `unelte/verificator_text.py`. Nimic descărcat, nimic instalat. Modelul nou NU intră în interfață (rămâne #407).
- pre-înregistrare: docs/preinregistrari/2026-10-26_E3_memorie.md (pasul 3, urcată înainte de pasul 4)
- aprobat de: Adrian, 26 oct 16:10 (prin centrul de comandă); pașii scriși de supraveghetor, 26 oct 16:15
- raport: docs/rapoarte/2026-10-26_2104_S27_E3_memorie.md

### S29 — C-21.1: memoria E3 mai bună — rădăcini românești + RRF și reordonare cu modelul propriu (procesor + câteva minute pe placă)
- stare: gata (executant, 26 oct 23:40: **CONFIRMAT** — pe cele 100 S26, `rrf_reord` k = 3 83 față de S25 simplă 72 (+11 ≥ 5),
  k = 20 95 ≥ 94; validarea arătase doar +1,2, deci efectul real e probabil mai mic; câștigul e la definiții, aproape tot din
  reordonare; răspunsul în bucățile care încap 72 față de 64; placa ~1.070 MB, 45 °C; 930 teste trec, 1 sărit) — aprobat DOAR pașii 5–7, cu varianta 1 din raportul S29 (supraveghetor, 26 oct 23:15; vezi „Decizia la pasul 4” mai jos). Istoric: oprit
  (executant, 26 oct 21:58: pașii 0–3 gata, cod 0 — aleasa pe validare `rrf_reord`, k = 3 78,2 % față de S25 77,0 %; pasul 4 imposibil cum e scris:
  după excluderi rămân 14 întrebări, nu 100)
- **Decizia la pasul 4 (supraveghetor, 26 oct 23:15, granița 2 „examene, notări”):** **setul decisiv = cele 100 de întrebări S26** (varianta 1,
  recomandată de executant). Motive: niciuna n-a intrat în vreo alegere S29 (pașii 0–3 sunt deja făcuți și varianta `rrf_reord` e fixată),
  #438 nu le-a văzut (S27 le-a scos, cu articolele lor), iar pragul C-21 rămâne cuvânt cu cuvânt. Baza de comparație: căutarea S25 simplă
  re-măsurată în **aceeași rulare** pe aceleași 100 (reper: la S26 a dat k = 3 = 72; dacă iese altceva, contează cifra din rulare și o spui).
  Varianta 2 (întrebări din antrenarea S27) NU se face. Pasul 4 nu se mai face: nu se scrie `examen_nou_8192.json`. Judecătorul rămâne **#438**,
  neschimbat față de pasul 3. **Spus cinstit în pre-înregistrare:** (i) setul S26 a mai fost folosit ca examen la S26 și S27 (doar măsurat, nimic
  ales pe el); (ii) #415, deci și #438, a văzut întrebările din `text_v3` la noaptea 12; (iii) pe validare câștigul a fost +1,2 puncte, deci verdictul
  așteptat e INFIRMAT — și e un rezultat. Dacă Adrian scrie altceva în coadă înainte de pornire, are prioritate.
- **Placa (după incidentul de la 21:47, 7.942 MB):** judecătorul DOAR în varianta reparată (6f8630b: loturi de 10, doar pozițiile întrebării);
  paznicul S17 verificat la fiecare 20 de întrebări, ca la a doua rulare. Peste 7.000 MB → oprești, `oprit`, scrii cifrele.
- tip: procesor (rădăcinile, RRF) + placă scurt (reordonarea: ~20 × 1.000–1.200 de evaluări, estimat sub 1 oră)
- fereastră: oricând — la prima verificare a cozii după S27 `gata`, cu placa liberă
- durată maximă: 6 ore în total; cel mult 1,5 ore pe placă; RAM cel mult ~40 GB; placa sub 7.000 MB și 83 °C
- de ce: comanda C-21 punctul 1 (propunerea 2 din studiu). Azi răspunsul e în primele 3 bucăți la 72 % și în primele 5 la 80 % (S26):
  diferența arată că **ordinea** e problema. Iar S27 a arătat că în context încap de obicei doar 2 bucăți, deci ordinea contează și mai mult.
- ce faci (comenzi noi în `unelte/e3_memorie.py` sau o unealtă nouă `unelte/e3_reordonare.py`; teste noi în `teste/`):
  0. **Unde stă codul.** C-21 cere module noi (MANIFEST + teste de contract). Dacă un port existent din contracte se potrivește (de ex. cel al
     memoriei), faci piesele ca module noi în `module/` cu MANIFEST și le adaugi în lista `MODULE` din `teste_contracte/`. Dacă ar trebui
     un **port nou** (adică o schimbare în `kronos/`), NU-l adaugi: scrii piesele în `unelte/` cu teste și notezi în raport ce port ar trebui
     — schimbarea în `kronos/` rămâne la Adrian.
  1. **(a) Rădăcini românești:** un stemmer românesc scris de noi după descrierea publică a algoritmului Snowball pentru română (fără cod
     copiat; sursa ideii în comentariu/README), cu teste pe cel puțin 30 de cuvinte (pluraluri, articol hotărât, diacritice). Un index NOU,
     separat, `lucru/e3/index_radacini.sqlite` (aceleași bucăți, textul trecut prin stemmer); `lucru/e3/index.sqlite` rămâne neatins
     (doar citire). Căutarea pe ambele indexuri se unește cu **RRF, k = 60**.
  2. **(b) Reordonarea „probabilitatea întrebării”:** pentru primele 20 de bucăți aduse de căutare, judecătorul calculează
     log p(întrebare | bucată), **normalizat pe simbol** (și varianta nenormalizată, ca să vezi dacă favorizează bucățile scurte), cu un
     prompt fix (de ex. „Text: …⏎Întrebare:”), fără întâmplare. **Judecătorul: #415.** Modelul S27 se folosește în loc doar dacă S27 a ieșit
     **CONFIRMAT**. Niciun alt model.
  3. **Alegerea, doar pe validare:** pe eșantioanele de validare existente **1024 și 2048** (500 + 500, S25) măsori la k = 1/3/5/20, potrivirea
     S16: căutarea aleasă S25 (`nume_obligatorii_liste`) simplă; + (a) RRF; + (b) reordonare; (a)+(b). Alegi **o singură** variantă finală
     (cea mai bună la k = 3 pe validare; la egalitate, cea mai simplă). Doc2query (c) NU se face acum.
  4. **Setul nou, neatins:** 100 de întrebări „text” din `text_v3/antrenare.jsonl`, **sămânța 8192**, aceleași filtre ca la S26, **fără nicio
     întrebare și niciun articol** comun cu: cele 100 S26, cele 160 de examene, eșantioanele 1024 și 2048, și **exemplele de antrenare S27**
     (`lucru/e3/date_antrenare_s27.json`). Salvezi lista fixă `lucru/e3/examen_nou_8192.json`, scrii în raport sha256 și câte articole are.
     **Spus cinstit, de scris în pre-înregistrare:** întrebările din `text_v3` au fost văzute de #415 la antrenare (noaptea 12), deci judecătorul
     le poate „recunoaște”; numeri și raportezi acest risc. Ca reper, măsori (o singură dată) și pe cele 100 S26.
  5. **Pre-înregistrarea** `docs/preinregistrari/2026-10-2x_E3_cautare_v2.md`, **urcată (commit + push) ÎNAINTE de pasul 6** (după pasul 3,
     cu varianta aleasă deja fixată): pragul din C-21 cuvânt cu cuvânt — **CONFIRMAT** dacă pe setul 8192 varianta aleasă urcă la **k = 3 cu
     ≥ 5 puncte** față de căutarea aleasă S25 simplă **și** la k = 20 nu scade; **INFIRMAT** dacă la k = 3 urcă cu **mai puțin de 2 puncte**
     sau k = 20 scade; între ele: NECLAR. Plus așteptările tale în cifre și „câte bucăți încap în 448 de simboluri” (regula S27) pentru varianta aleasă.
  6. **Măsurarea, o singură rulare** pe setul 8192 (și reperul S26): k = 1/2/3/5/20, potrivirea S16, timpul pe întrebare, memoria plăcii.
  7. `python -m pytest`: toate trec. Commit + push. Raport `docs/rapoarte/2026-10-2x_<ora>_S29_E3_cautare_v2.md`.
- Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, datele de examen și `text_v3` (doar citire), listele S26/S27,
  `lucru/e3/index.sqlite` (doar citire), `unelte/verificator_text.py`, #415 și linia w2. Nimic antrenat, nimic descărcat, nimic instalat,
  nimic în interfață, nimic din `lucru/e3/` în Git.
- Dacă un pas pică de 2 ori la rând cu aceeași eroare: te oprești, stare `oprit`, scrii eroarea în raport.
- pre-înregistrare: docs/preinregistrari/2026-10-2x_E3_cautare_v2.md (urcată înainte de pasul 6; setul = cele 100 S26)
- aprobat de: Adrian (COMENZI.md C-21, 26 oct 17:45, prin centrul de comandă); pașii scriși de supraveghetor, 26 oct 20:15; setul decisiv
  ales de supraveghetor, 26 oct 23:15 (varianta 1 din raport)
- raport: docs/rapoarte/2026-10-26_2158_S29_E3_cautare_v2.md (pașii 0–3); pașii 5–7: docs/rapoarte/2026-10-26_2340_S29_E3_cautare_v2_verdict.md

### S30 — C-21.2, pregătirea: optimizatorul Muon + răcire lungă — codul, testul pe procesor și proba de 10 minute pe placă
- stare: gata (executant, 27 oct 00:24: codul în module/model_muon.py, implicit aceiași pași bit cu bit; proba B pe placă
  00:11–00:24 cod 0, **5.917 MB**, 64 °C; „șoc” vizibil la pornirea din #415 (după 10 min la 0,02 pierderea medie 1,88 > 1,46
  la început); propun **rata Muon 0,01** pentru S31 (B are încă 0,02 în configurare); 946 teste trec, 1 sărit)
- tip: procesor + placă scurt (proba de 10 minute)
- fereastră: oricând, cu placa liberă
- durată maximă: 4 ore; cel mult 30 de minute pe placă; placa sub 7.000 MB și 83 °C
- de ce: comanda C-21 punctul 2 (propunerea 1 din studiu): Muon ar ajunge la aceeași pierdere cu ~1,5× mai puțini pași; răcirea lungă e
  cel mai sigur câștig din rețetele citite. Înainte de 5–6 ore pe placă, codul trebuie dovedit pe procesor.
- ce faci:
  1. **Optimizatorul**, scris de noi (inspirat din descrierea publică Muon: Newton-Schulz în bf16, momentum 0,95 Nesterov; sursa ideii în
     README), ca **modul nou** `module/optimizator_muon.py` cu MANIFEST și teste de contract dacă există un port potrivit; dacă ar cere un port
     nou în `kronos/`, NU-l adaugi: îl pui în `unelte/` și notezi în raport. Muon pe matricile din straturi; AdamW pe intrare, ieșire,
     LayerNorm și bias.
  2. **Opțiuni noi în `unelte/antrenare_lunga.py`** (sau în configurare): alegerea optimizatorului, **gradient adunat pe 8 loturi**, și
     **răcirea finală ~25 %** din antrenare. **Valorile implicite rămân exact ca acum** (AdamW, fără adunare, răcirea de azi) — un test
     arată că fără opțiunile noi antrenarea face exact aceiași pași ca înainte (#415 și linia w2 neatinse).
  3. **Testul unitar pe procesor** (`CUDA_VISIBLE_DEVICES=-1`): pe un MLP mic, Muon scade pierderea, iar matricea de update are valorile
     singulare în ~[0,6; 1,2].
  4. **Configurările** pentru S31: `config/conv_w2_muon_A.toml` (AdamW) și `config/conv_w2_muon_B.toml` (Muon) = copii ale
     `config/conv_w2_text_v3.toml` (rețeta lui #415), aceleași date și aceeași sămânță, ambele cu adunare pe 8 loturi și răcire ~25 %;
     diferă doar optimizatorul (B: lr Muon 0,02 pe matrici, AdamW ca acum pe rest), `nume` (`w2_muon_A`/`w2_muon_B`, linii noi de rulare)
     și `cale_stare`. Arăți diferențele cu `diff` în raport.
  5. **Proba pe placă, 10 minute, cu B** (din #415, prin cascadă), plus 2 minute cu lr 0,01: memoria plăcii cel mult, temperatura, pierderea
     la început (dacă vezi „șocul” de la momentumul pornit de la zero, îl scrii). Dacă memoria trece de 7.000 MB: te oprești, `oprit`,
     scrii cifrele. Proba nu e un rezultat; modelele ei nu se păstrează pentru examen.
  6. `python -m pytest`: toate trec. Commit + push. Raport `docs/rapoarte/2026-10-2x_<ora>_S30_muon_pregatire.md`, cu lr-ul pe care îl
     propui pentru S31 (0,01 sau 0,02) și de ce.
- Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, datele de examen, #415, linia w2. Nimic descărcat, nimic instalat.
- Dacă un pas pică de 2 ori la rând cu aceeași eroare: te oprești, stare `oprit`, scrii eroarea în raport.
- pre-înregistrare: nu e antrenare (proba de 10 minute nu se notează); pre-înregistrarea S31 se scrie la S31
- aprobat de: Adrian (COMENZI.md C-21, 26 oct 17:45, prin centrul de comandă); pașii scriși de supraveghetor, 26 oct 20:15
- raport: docs/rapoarte/2026-10-27_0024_S30_muon_pregatire.md

### S31 — C-21.2, rularea: AdamW (A) contra Muon (B), câte 2 ore din #415 (placa)
- stare: gata (executant, 27 oct 05:35: lanțul 01:01–05:16, cod 0; **INFIRMAT** — română curat A 1,2332 / B 1,3019 (B ≥ A);
  B mai rău și pe TinyStories R2 0,4472/0,4154, cod 0,8042/0,7460, fapte noi 73/76; A a coborât sub #415 (1,2858); placa ≤ 5.374 MB; 946 teste trec)
- tip: placă (~5–6 ore în total)
- fereastră: noapte (19:00–07:00) de preferat; altfel oricând, dacă A + B + examenele încap în aceeași fereastră
- durată maximă: 2 ore A + 2 ore B + examene; cel mult 6 ore pe placă
- ce faci:
  1. **Pre-înregistrarea** `docs/preinregistrari/2026-10-2x_muon.md`, **urcată ÎNAINTE de pornire**, cu pragul din C-21 cuvânt cu cuvânt:
     **CONFIRMAT** dacă B ≤ A − 0,010 val_bpb pe validarea românească **și** nicio regresie mai mare de 0,005 pe celelalte (TinyStories R2,
     cod, fapte); **INFIRMAT** dacă B ≥ A pe română; între ele: **NECLAR** (se repetă cu altă sămânță — o pune supraveghetorul). Plus
     așteptările tale în cifre, lr-ul ales la S30 și ora estimată de sfârșit (scrisă și în coadă la pornire).
  2. **A:** `cascada.py porneste S31A -- python unelte/antrenare_lunga.py --config config/conv_w2_muon_A.toml --ore 2 --porneste-din 415`;
     apoi **B** la fel cu `conv_w2_muon_B.toml`. Aceeași sămânță, aceleași date.
  3. **Examenele, o singură rulare pe A și B:** val_bpb pe validarea românească și pe TinyStories R2 + examenele obișnuite ca la S23
     (română, cod, povești, fapte noi). Verdictul după pre-înregistrare, cu toate cifrele.
  4. `python -m pytest`: toate trec. Commit + push. Raport `docs/rapoarte/2026-10-2x_<ora>_S31_muon.md`.
- Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, datele de examen, #415, linia w2. Modelele noi NU intră în interfață.
- Dacă un pas pică de 2 ori la rând cu aceeași eroare: te oprești, stare `oprit`, scrii eroarea în raport.
- pre-înregistrare: docs/preinregistrari/2026-10-27_muon.md (urcată înainte de pornire)
- aprobat de: Adrian (COMENZI.md C-21, 26 oct 17:45, prin centrul de comandă); pașii scriși de supraveghetor, 26 oct 20:15
- raport: docs/rapoarte/2026-10-27_0535_S31_muon.md (INFIRMAT)

### S33 — E3 citește cu căutarea nouă: examenul S27 refăcut cu `rrf_reord` (procesor + sub 1 oră pe placă)
- stare: gata (executant, 27 oct 08:42: **CONFIRMAT la limită** — #438 cu `rrf_reord` 66/100 față de S25 simplă 60 (Δ +6 ≥ 5),
  în aceeași rulare; reperul S27 reprodus exact (aceleași bucăți și răspunsuri la 100/100); 15 reparate / 9 stricate; câștigul din
  definiții (23 → 30 din 54); placa 732 MB; 950 teste trec, 1 sărit)
- tip: procesor (pasul 1) + placă scurt (pasul 3)
- fereastră: zi (08:00–18:30)
- durată maximă: 3 ore în total; cel mult 1 oră pe placă; placa sub 7.000 MB și 83 °C
- de ce: propunerile executantului din raportul S29 (verdict). S29 a ieșit CONFIRMAT (+11 la k = 3), dar validarea arătase doar +1,2.
  Întrebarea care contează pentru Kronos: **dacă #438 primește bucățile în ordinea nouă, răspunde corect la mai multe întrebări?**
  (S27: 60/100; plafonul urcă de la 64 la 72.) Granița 2 („examene, comparații”): nimic antrenat.
- ce faci:
  1. **Procesor (`CUDA_VISIBLE_DEVICES=-1`), câteva minute:** din `lucru/e3/validare_s29.json`, amestecul de tipuri (definiții „Ce este X?”,
     născut, an, regizat, rest) pe eșantioanele 1024 și 2048 și câștigul `rrf_reord` față de `s25` la k = 3 **pe fiecare tip**. Comparat cu
     amestecul celor 100 S26 (54 % definiții). Scrii tabelul în raport. Nu se alege nimic pe baza lui.
  2. **Pre-înregistrarea** `docs/preinregistrari/2026-10-27_E3_citire_reord.md`, **urcată (commit + push) ÎNAINTE de pasul 3**:
     **CONFIRMAT** dacă #438 cu `rrf_reord` răspunde corect la **cel puțin 5 întrebări mai mult** decât #438 cu căutarea S25 simplă,
     măsurat în **aceeași rulare** pe cele 100 S26; **INFIRMAT** dacă diferența e **sub 2**; între ele: NECLAR. Aceeași notare ca la S27
     (verificatorul S16, potrivirea S16), același prompt, aceeași regulă „câte bucăți încap în 448 de simboluri”, fără întâmplare.
     **Spus cinstit:** setul S26 e folosit a patra oară (S26, S27, S29 — doar măsurat, nimic ales pe el); #438 a văzut `text_v3` la antrenare;
     reperul S27 (60) trebuie să iasă din nou ~60 la varianta S25 simplă — dacă iese altceva, contează cifra din rulare și o spui.
     Plus așteptările tale în cifre.
  3. **Examenul, o singură rulare** (comandă nouă în `unelte/e3_examen.py` sau `unelte/e3_reordonare.py`, cu test nou fără placă):
     #438 pe cele 100 S26, (i) cu bucățile S25 simple, (ii) cu bucățile `rrf_reord` (judecătorul #438, ca la S29). Pe fiecare: corecte din
     100, corecte dintre cele cu răspunsul în bucățile care încap și dintre cele fără, timpul pe întrebare, memoria plăcii. Paznicul S17
     verificat la fiecare 20 de întrebări; peste 7.000 MB → oprești, `oprit`, scrii cifrele.
  4. `python -m pytest`: toate trec. Commit + push. Raport `docs/rapoarte/2026-10-27_<ora>_S33_E3_citire_reord.md`, cu verdictul strict după
     pre-înregistrare și ce propui mai departe.
- Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, datele de examen și `text_v3` (doar citire), lista S26,
  `lucru/e3/index.sqlite` și `index_radacini.sqlite` (doar citire), `unelte/verificator_text.py`, #415, #438 și linia w2. Nimic antrenat,
  descărcat sau instalat; nimic în interfață; nimic din `lucru/e3/` în Git. Portul `cautare` în `kronos/` NU se face (rămâne la Adrian).
- Dacă un pas pică de 2 ori la rând cu aceeași eroare: te oprești, stare `oprit`, scrii eroarea în raport.
- pre-înregistrare: docs/preinregistrari/2026-10-27_E3_citire_reord.md (urcată înainte de pasul 3)
- aprobat de: supraveghetor, 27 oct 02:15 (granițele 2 și 5 din REGULI_CASCADA.md; propunerea executantului din raportul S29)
- raport: docs/rapoarte/2026-10-27_0842_S33_E3_citire_reord.md (CONFIRMAT)
- verificat de supraveghetor, 27 oct 11:15: pre-înregistrarea înaintea examenului ✓; Δ = 66 − 60 = +6 ≥ +5 → CONFIRMAT ✓ (la limită; câștigul din definiții).

### S34 — Proba de control: #415 + 2 ore cu rețeta veche (vine câștigul lui A din rețetă sau doar din cele 2 ore în plus?) (placa)
- stare: gata (executant, 27 oct 12:03: lanțul 09:00–11:08, cod 0; **CONFIRMAT** — română curat C (#447) 1,2903 / A (#441, re-măsurat) 1,2332,
  Δ = +0,0571 ≥ 0,010; C nu s-a îmbunătățit față de #415 (1,2858); TinyStories C 0,4452 / A 0,4154; placa ≤ 5.991 MB, 63 °C; 950 teste trec, 1 sărit)
- tip: placă (~2,5 ore în total)
- fereastră: oricând (regula lui Adrian din 22 oct 15:10), imediat după S33
- durată maximă: 2 ore de antrenare + examene; cel mult 3 ore pe placă; placa sub 7.000 MB și 83 °C
- de ce: la S31, A (#441: AdamW + adunare pe 8 loturi + răcire 25 %) a dat română curat **1,2332**, față de #415 **1,2858**. Dar #441 are 2 ore de
  antrenare în plus față de #415. Fără un reper cu **aceleași 2 ore și rețeta veche**, nu știm dacă merită să păstrăm rețeta A. Granițele 1 și 2
  (încă o rulare pe linia w2 existentă, aceeași rețetă ca #415; comparație). Nu e o noapte „ca să crească scorul pe tipuri nevăzute” (Adrian, 22 oct).
- ce faci:
  1. **Configurarea** `config/conv_w2_reteta_C.toml` = copie exactă a `config/conv_w2_text_v3.toml` (rețeta lui #415, `module.model_conversatie`,
     fără adunare, fără răcire), cu DOAR: `nume = "w2_reteta_C"`, `cale_stare = "lucru/w2_reteta_C/gpt.pt"`, eticheta și un antet scurt. Verifici
     că `lucru/w2_reteta_C/` nu există. Arăți în raport `diff` față de `conv_w2_text_v3.toml` și față de `conv_w2_muon_A.toml`.
  2. **Pre-înregistrarea** `docs/preinregistrari/2026-10-27_reteta_control.md`, **urcată (commit + push) ÎNAINTE de pornire**, cu pragul, cuvânt cu cuvânt:
     măsura = `bpb_romana_curat` din `unelte/examen_validari_ws.py`; Δ = C − A (A = #441, re-măsurat în aceeași rulare; reper 1,2332).
     **CONFIRMAT** (rețeta A aduce câștig real) dacă **Δ ≥ 0,010**; **INFIRMAT** (câștigul vine din cele 2 ore, nu din rețetă) dacă **Δ < 0,005**;
     între ele: **NECLAR**. Alături (nu decid): TinyStories R2 (val_bpb oficial, ora 2), `bpb_cod_curat`, fapte noi, pentru A, C și #415.
     Plus așteptările tale în cifre și ora estimată de sfârșit (scrisă și în coadă la pornire).
  3. **Rularea**, prin cascadă: `cascada.py porneste S34 -- python unelte/antrenare_lunga.py --config config/conv_w2_reteta_C.toml --ore 2 --porneste-din 415`.
  4. **Examenele, o singură rulare:** `unelte/examen_validari_ws.py --linie w2_reteta_C` (ultimul model, ora 2) și, în aceeași rulare,
     `--linie w2_muon_A` (#441) ca reper. Verdictul strict după pre-înregistrare.
  5. `python -m pytest`: toate trec. Commit + push. Raport `docs/rapoarte/2026-10-27_<ora>_S34_reteta_control.md`, cu propunerea ta pentru pasul următor.
- Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, datele de examen, #415, #441, linia w2 existentă (`w2_conv_text_v3`) și configurările
  S31. Modelul nou NU intră în interfață. Nimic descărcat sau instalat.
- Dacă un pas pică de 2 ori la rând cu aceeași eroare: te oprești, stare `oprit`, scrii eroarea în raport. Peste 7.000 MB → oprești, `oprit`, scrii cifrele.
- Dacă Adrian are nevoie de placă pentru fereastra OS/GPU: S34 nu pornește cât e anunțată fereastra (o anunță centrul de comandă).
- pre-înregistrare: docs/preinregistrari/2026-10-27_reteta_control.md (urcată înainte de pornire)
- aprobat de: supraveghetor, 27 oct 08:15 (granițele 1 și 2 din REGULI_CASCADA.md)
- raport: docs/rapoarte/2026-10-27_1203_S34_reteta_control.md (CONFIRMAT)

### S35 — Citirea cu `rrf_reord` pe validare: cât din +6 de la S33 rămâne pe un set cu alt amestec? (procesor + sub 1 oră pe placă)
- stare: gata (executant, 27 oct 13:03; NECLAR: Δ +1,0 punct pe 2048, 336 față de 331; 952 teste trec)
- tip: placă scurt (examen, nimic antrenat)
- fereastră: oricând (regula lui Adrian din 22 oct 15:10)
- durată maximă: 2 ore în total; cel mult 1 oră pe placă; placa sub 7.000 MB și 83 °C
- de ce: S33 a dat +6 corecte (60 → 66) pe cele 100 S26, la limită, cu câștigul aproape tot din definiții. Pe validare, căutarea câștigase doar
  +1,2 puncte (+2,4 pe eșantionul 2048), iar „restul” tipurilor pierdea. Propunerea 2 a executantului din raportul S33 („cât din +6 e de la S26?”),
  dar fără un set nou (lista de întrebări nefolosite e aproape goală): măsurăm **citirea** pe validarea deja existentă. Granița 2 (examen, comparație).
- ce faci:
  1. **Procesor (`CUDA_VISIBLE_DEVICES=-1`), câteva minute:** din `lucru/e3/validare_s29.json`, numeri întrebările din eșantionul **2048** și din **1024**
     și verifici câte din fiecare apar în datele de antrenare ale lui #438 (S27, cele 14.540 de exemple). Scrii cifrele în pre-înregistrare.
     Întrebările din 2048 care apar la antrenarea #438 (dacă sunt) se scot din măsura care decide; le spui numărul.
  2. **Pre-înregistrarea** `docs/preinregistrari/2026-10-27_E3_citire_validare.md`, **urcată (commit + push) ÎNAINTE de pasul 3**. Măsura care decide:
     pe eșantionul **2048** (fără cele văzute de #438), Δ = procentul de răspunsuri corecte cu `rrf_reord` − procentul cu `s25`, **în aceeași rulare**.
     **CONFIRMAT** (reordonarea ajută la citire și în afara S26) dacă **Δ ≥ +2,0 puncte**; **INFIRMAT** dacă **Δ < +0,5 puncte** (inclusiv negativ);
     între ele: **NECLAR**. Alături (nu decide): eșantionul 1024, pe tipuri (definiții, născut, an, regizat, rest), reparate / stricate.
     Aceeași notare și același cod ca la S33 (`unelte/e3_citire_reord.py`, verificatorul S16, regula „câte bucăți încap în 448 de simboluri”,
     promptul S27, fără întâmplare; #438 și ca judecător). Spus cinstit: alegerea `rrf_reord` s-a făcut pe validare (782 față de 778, diferențe mici),
     deci validarea nu e complet curată; și ea vine din `text_v3`, pe care #415 l-a văzut. Plus așteptările tale în cifre.
  3. **Examenul, o singură rulare** (dacă trebuie, o opțiune nouă în `unelte/e3_citire_reord.py`, de ex. `examen --set validare`, cu test nou fără placă;
     refuză dacă ieșirea există deja) → `lucru/e3/examen_s35.json`: pe fiecare întrebare (i) `s25`, (ii) `rrf_reord`; corecte, corecte dintre cele cu
     răspunsul în bucățile care încap și dintre cele fără, pe tipuri, timpi, memoria plăcii. Paznicul S17 la fiecare 50 de întrebări; peste 7.000 MB →
     oprești, `oprit`, scrii cifrele.
  4. `python -m pytest`: toate trec. Commit + push. Raport `docs/rapoarte/2026-10-27_<ora>_S35_E3_citire_validare.md`, cu verdictul strict după
     pre-înregistrare și ce propui mai departe (de ex. „reordonarea doar la definiții”, de verificat pe alt set).
- Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, datele de examen și `text_v3` (doar citire), lista S26, `validare_s29.json`,
  `lucru/e3/index.sqlite` și `index_radacini.sqlite` (doar citire), `unelte/verificator_text.py`, #415, #438, #441 și liniile w2. Nimic antrenat,
  descărcat sau instalat; nimic în interfață; nimic din `lucru/e3/` în Git. Portul `cautare` în `kronos/` NU se face (rămâne la Adrian).
- Dacă un pas pică de 2 ori la rând cu aceeași eroare: te oprești, stare `oprit`, scrii eroarea în raport.
- pre-înregistrare: docs/preinregistrari/2026-10-27_E3_citire_validare.md (urcată înainte de pasul 3)
- aprobat de: supraveghetor, 27 oct 11:15 (granița 2 din REGULI_CASCADA.md; propunerea 2 a executantului din raportul S33)
- raport: docs/rapoarte/2026-10-27_1303_S35_E3_citire_validare.md (NECLAR)

### S32 — C-21.3: motorul de inferență fără PyTorch (fp32 + Q8_0), doar procesor
- stare: gata (executant, 27 oct 14:03; măsurarea 13:39–13:53, cod 0; **fp32 NU TRECE** (dif. maximă 1,34e-4 > 1e-4; argmax și
  textul generat identice cu PyTorch), **Q8_0 TRECE** (bpb +0,00002); 960 teste trec)
- tip: procesor (fără placă: `CUDA_VISIBLE_DEVICES=-1`)
- fereastră: oricând
- durată maximă: 2 zile de lucru, în pași (fiecare pas reușit: commit + push); RAM cel mult ~40 GB
- de ce: comanda C-21 punctul 3 (propunerea 3 din studiu): desparte „ce face modelul” de PyTorch și dă lui Cyber Universe un contract exact
  (fișierul de greutăți) pentru motorul lor fără sistem de operare. Nu schimbă modelul.
- ce faci:
  1. **Unealta de export** `unelte/exporta_greutati.py`: scrie #415 într-un fișier binar propriu (antet cu chei-valori, little-endian,
     aliniere 32 — ideea GGUF, cod scris de noi), variantele fp32 și **Q8_0 doar pe greutăți** (blocuri de 32, o scară). Formatul descris
     într-un README scurt (contractul pentru OS).
  2. **Motorul** ca modul nou `module/inferenta_bruta.py` (Python + numpy) cu MANIFEST și teste de contract dacă există un port potrivit
     (altfel în `unelte/` și notezi în raport — portul nou rămâne la Adrian): citește fișierul și face forward-ul lui #415 strat cu strat.
     Atenție la ordinea greutăților din `nn.MultiheadAttention` (in_proj combinat): test strat cu strat.
  3. **Starea de control:** PyTorch scrie logits pentru 3 texte fixe (în `teste/`, mici). **Prag (de scris în raport înainte de măsurare):**
     fp32: diferența maximă < **1e-4** față de PyTorch; Q8_0: val_bpb pe validarea românească crește cu **cel mult 0,005** față de fp32.
     Plus simboluri pe secundă pe procesor, fp32 și Q8_0.
  4. `python -m pytest`: toate trec. Commit + push. Raport `docs/rapoarte/2026-10-2x_<ora>_S32_inferenta_bruta.md`.
- Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, #415 (doar citire). Fișierele de greutăți exportate stau în `lucru/`, nu în
  Git. Nimic descărcat, nimic instalat (numpy există deja; dacă nu, te oprești și scrii).
- Dacă un pas pică de 2 ori la rând cu aceeași eroare: te oprești, stare `oprit`, scrii eroarea în raport.
- pre-înregistrare: nu e antrenare; pragul se scrie în raport și se urcă înainte de pasul 3
- aprobat de: Adrian (COMENZI.md C-21, 26 oct 17:45, prin centrul de comandă); pașii scriși de supraveghetor, 26 oct 20:15
- raport: docs/rapoarte/2026-10-27_1338_S32_inferenta_bruta.md (fp32 NU TRECE, Q8_0 TRECE)

### S36 — Proba D: rețeta A fără adunarea pe 8 loturi (aduce răcirea singură câștigul?) (placa)
- stare: gata (executant, 27 oct 17:33: lanțul 15:00–17:08, cod 0; **NECLAR** — română curat D (#451) 1,2520 / A (#441, re-măsurat) 1,2332,
  Δ = +0,0188 (între 0,010 și 0,040); D păstrează ~67 % din câștigul A față de C; placa ≤ 5.991 MB, 63 °C; 960 teste trec, 1 sărit)
- tip: placă (~2,2 ore în total)
- fereastră: oricând (regula lui Adrian din 22 oct 15:10) — pornește la prima verificare a cozii
- durată maximă: 2 ore de antrenare + examene; cel mult 3 ore pe placă; placa sub 7.000 MB și 83 °C
- de ce: S34 a CONFIRMAT că **pachetul** A (AdamW din `module.model_muon` + adunare pe 8 loturi + răcire 25 %) aduce câștig real (A 1,2332 față de
  C 1,2903 pe română curat, aceleași 2 ore din #415). Nu știm care parte îl aduce. D păstrează tot din A, **fără adunare** (adunare_loturi = 1):
  dacă D ≈ A, răcirea e cea care contează (rețeta mai simplă); dacă D ≈ C, adunarea contează. Propunerea 2 a executantului din raportul S34.
  Granițele 1 și 2 (încă o rulare pe linia w2 existentă; comparație). E o probă de 2 ore, nu o noapte de antrenare.
- ce faci:
  1. **Configurarea** `config/conv_w2_reteta_D.toml` = copie exactă a `config/conv_w2_muon_A.toml`, cu DOAR: `nume = "w2_reteta_D"`,
     `cale_stare = "lucru/w2_reteta_D/gpt.pt"`, **`adunare_loturi` scos din `setari`** (implicit 1), eticheta `"S36 D: răcire fără adunare"` și un antet scurt.
     Păstrezi `modul = "module.model_muon:ModelGPTConversatieMuon"`, `optimizator = "adamw"`, `racire_finala = 0.25`, `durata_scaderii_secunde = 7200`.
     Verifici că `lucru/w2_reteta_D/` nu există. Arăți în raport `diff` față de `conv_w2_muon_A.toml` și față de `conv_w2_reteta_C.toml`.
  2. **Pre-înregistrarea** `docs/preinregistrari/2026-10-27_reteta_D.md`, **urcată (commit + push) ÎNAINTE de pornire**, cu pragul, cuvânt cu cuvânt:
     măsura = `bpb_romana_curat` din `unelte/examen_validari_ws.py`; Δ = D − A (A = #441, re-măsurat în aceeași rulare; reper 1,2332; C #447 = 1,2903).
     **CONFIRMAT** (răcirea singură aduce câștigul; adunarea nu e necesară) dacă **Δ ≤ 0,010**; **INFIRMAT** (fără adunare se pierde cea mai mare parte
     a câștigului) dacă **Δ ≥ 0,040**; între ele: **NECLAR** (ambele părți contribuie). Alături (nu decid): TinyStories R2 (val_bpb oficial, ora 2),
     `bpb_cod_curat`, fapte noi, pentru D și A; pașii optimizatorului (D face de ~8 ori mai mulți pași decât A). Plus așteptările tale în cifre și
     ora estimată de sfârșit (scrisă și în coadă la pornire). Spus cinstit în pre-înregistrare: o singură sămânță; D are aceeași rată ca A, deci
     schimbă și mărimea pasului efectiv, nu doar adunarea.
  3. **Rularea**, prin cascadă: `cascada.py porneste S36 -- python unelte/antrenare_lunga.py --config config/conv_w2_reteta_D.toml --ore 2 --porneste-din 415`.
     Înainte: o probă de memorie nu e necesară (aceleași loturi ca A, care a stat sub 6.000 MB), dar urmărești placa ca la S34.
  4. **Examenele, o singură rulare:** `unelte/examen_validari_ws.py --linie w2_reteta_D` (ultimul model, ora 2) și, în aceeași rulare,
     `--linie w2_muon_A` (#441) ca reper. Verdictul strict după pre-înregistrare; închizi pre-înregistrarea cu `unelte/preinregistrare.py --inchide reteta_D`.
  5. `python -m pytest`: toate trec. Commit + push. Raport `docs/rapoarte/2026-10-27_<ora>_S36_reteta_D.md`, cu propunerea ta pentru pasul următor.
- Nu atingi `kronos/`, `module/examen_bpb.py`, `module/model_muon.py`, paznicul, jurnalul, datele de examen, #415, #441, #447, liniile
  `w2_conv_text_v3`, `w2_muon_A`, `w2_reteta_C` și configurările lor. Modelul nou NU intră în interfață. Nimic descărcat sau instalat.
- Dacă un pas pică de 2 ori la rând cu aceeași eroare: te oprești, stare `oprit`, scrii eroarea în raport. Peste 7.000 MB → oprești, `oprit`, scrii cifrele.
- Dacă Adrian are nevoie de placă pentru fereastra OS/GPU: S36 nu pornește cât e anunțată fereastra (o anunță centrul de comandă).
- pre-înregistrare: docs/preinregistrari/2026-10-27_reteta_D.md (urcată 27 oct 15:00, înainte de pornire)
- aprobat de: supraveghetor, 27 oct 14:15 (granițele 1 și 2 din REGULI_CASCADA.md; propunerea 2 a executantului din raportul S34)
- raport: docs/rapoarte/2026-10-27_1733_S36_reteta_D.md (NECLAR)

### S37 — Motorul S32: adunări în float64 la LayerNorm și softmax, apoi o singură remăsurare fp32 (doar procesor)
- stare: gata (executant, 27 oct 18:06; măsurarea 18:00, cod 0; **fp32 NU TRECE** (dif. maximă 1,364e-4 > 1e-4, la S32 1,335e-4:
  float64 la LayerNorm/softmax/atenție nu ajută); argmax și textul identice; 41,3 simboluri/s; 961 teste trec, 1 sărit)
- tip: procesor (fără placă: `CUDA_VISIBLE_DEVICES=-1`)
- fereastră: oricând, **după S36** (ca să nu încetinească antrenarea)
- durată maximă: 3 ore; RAM cel mult ~10 GB
- de ce: la S32, fp32 NU TRECE (dif. maximă 1,335e-4 față de pragul 1e-4 din C-21, aprobat de Adrian), deși argmax și textul sunt identice.
  Varianta (a) a executantului: pragul rămâne 1e-4, schimbăm doar felul în care motorul adună. Granița 6 (repararea unei unelte care n-a trecut)
  și 5 (unealta e în `unelte/`, nu atinge `kronos/`). Q8_0 a trecut deja și nu se remăsoară.
- ce faci:
  1. În `unelte/inferenta_bruta.py`: media și varianța din LayerNorm și suma din softmax (și, dacă ajută, produsele de atenție) calculate în float64,
     rezultatul convertit înapoi în float32. Greutățile și formatul KGR1 rămân neschimbate (`docs/format_greutati.md` nu se schimbă; dacă
     totuși trebuie, scrii de ce). Testele existente trec; adaugi un test mic că LayerNorm-ul adună în float64.
  2. **Înainte de măsurare**, scrii în raport (commit + push): pragul rămâne **dif. maximă < 1e-4** pe aceleași 3 texte fixe față de aceleași logits
     PyTorch pe procesor; măsura e una singură, pe #415 F32. Plus așteptarea ta în cifre.
  3. O singură rulare (ca la S32, prin cascadă), scrii diferența maximă pe fiecare text, argmax, viteza (simboluri/s, F32) față de S32 (42,4).
  4. `python -m pytest`: toate trec. Commit + push. Raport `docs/rapoarte/2026-10-2x_<ora>_S37_inferenta_fp64.md`: TRECE / NU TRECE strict după prag.
     Dacă NU TRECE, nu mai încerci altceva: scrii ce propui (de ex. un prag relativ, de hotărât de Adrian pentru o măsurare nouă).
- Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, #415 (doar citire), logits-urile de control din `teste/`. Fișierele exportate
  stau în `lucru/`, nu în Git. Nimic descărcat sau instalat. Portul „inferenta” în `kronos/` NU se face (rămâne la Adrian).
- Dacă un pas pică de 2 ori la rând cu aceeași eroare: te oprești, stare `oprit`, scrii eroarea în raport.
- pre-înregistrare: nu e antrenare; pragul se scrie în raport și se urcă înainte de pasul 3
- aprobat de: supraveghetor, 27 oct 14:15 (granițele 5 și 6 din REGULI_CASCADA.md; varianta (a) a executantului din raportul S32)
- raport: docs/rapoarte/2026-10-27_1800_S37_inferenta_fp64.md (NU TRECE; pragul relativ propus, de hotărât de Adrian)

### S38 — Continuarea liniei w2 cu rețeta A, din #441 (o noapte pe placă)
- stare: gata (executant, 28 oct 06:35: lanțul 19:34–01:57, cod 0; **CONFIRMAT** — română curat #459 1,2162 / #441 1,2332 (Δ −0,017);
  cod curat 0,7321, R2 0,4084, fără regresie; placa max 6.002 MB, 64 °C; 961 teste trec; raport întârziat: fără internet 02:28–06:01)
- tip: placă (~6 ore de antrenare + examene)
- fereastră: noapte, după S36 (cel mai devreme noaptea 27→28)
- de ce: S34 a confirmat că rețeta A (AdamW + adunare pe 8 loturi + răcire 25 %) aduce câștig real; #441 e cel mai bun model pe română curat (1,2332).
  Direcția din 22 oct spune însă că nu se mai programează nopți de antrenare fără „da”-ul lui Adrian → aștept decizia lui. Dacă S36 dă CONFIRMAT,
  continuarea folosește rețeta mai simplă D (fără adunare).
- ce ar face (dacă Adrian spune „da”): configurarea `config/conv_w2_reteta_A_cont.toml` = copie a `conv_w2_muon_A.toml` (sau D, după S36) cu
  `durata_scaderii_secunde = 21600`, linie nouă `w2_reteta_A_cont`; `--ore 6 --porneste-din 441`. Pre-înregistrare înainte: **CONFIRMAT** dacă română
  curat ≤ **1,2232** (−0,010 față de #441), fără regresie > 0,005 la cod curat și TinyStories R2; **INFIRMAT** dacă > 1,2282; între ele NECLAR.
  Examenele: `unelte/examen_validari_ws.py` pe ultimul model și pe #441 în aceeași rulare. Modelul nu intră în interfață.
- aprobat de: Adrian, 27 oct 18:00 (centrul de comandă, delegarea din DECIZII 26 oct 17:45). Pornește în noaptea 27→28, după S36; dacă S36 dă CONFIRMAT, cu rețeta D, cum scrie mai sus. Pre-înregistrarea se urcă înainte.
- pre-înregistrare: docs/preinregistrari/2026-10-27_reteta_A_cont.md (urcată 27 oct ~19:35, înainte de pornire); sfârșit estimat ~01:55
- notă supraveghetor (28 oct 05:15): niciun commit de la executant după 19:34; raportul lipsește la 3 h după sfârșitul estimat. Adrian anunțat.
  Executantule, la revenire: verifică întâi dacă antrenarea S38 s-a terminat (jurnalul și modelul din `lucru/`); dacă da, rulează examenele și scrie
  raportul cu verdictul față de pre-înregistrare; dacă s-a întrerupt, pune S38 pe `oprit`, scrie în raport până unde a ajuns și **nu** o reporni singur.
- raport: docs/rapoarte/2026-10-28_0635_S38_reteta_A_cont.md (CONFIRMAT)
- verificat de supraveghetor, 28 oct 08:20: pre-înregistrarea înaintea pornirii ✓; 1,2162 ≤ 1,2232 → CONFIRMAT ✓; cod 0,7321 ≤ 0,7510 ✓, R2 0,4084 ≤ 0,4204 ✓.

### S39 — C-24: Kronos adevărat în OS, partea Kronos — pachetul KGR1 pentru OS + modelul exportat ca Release privat (doar procesor)
- stare: gata (executant, 28 oct 07:12: partea A + B; vectorii în integrare/kronos/ (F32 2,42 MB > 1 MB din cauza tokenizerului de 16.384, Q8_0 0,84 MB);
  README.md și MODEL.md în docs/integrare_kronos/ (regula Edit(kronos/**) prinde și integrare/kronos/); #459 exportat Q8_0, 110.859.040 octeți,
  SHA-256 e80618b4…382e; **Release nefăcut**: `gh` cere aprobare în rularea programată — comanda în raport; 965 teste trec, 1 sărit)
- tip: procesor (fără placă: `CUDA_VISIBLE_DEVICES=-1`); nu întrerupe și nu încetinește S38
- fereastră: **partea A oricând, chiar în timpul S38** (e ușoară: minute, RAM < 2 GB); **partea B după ce S38 s-a terminat și raportul S38 e urcat**
- durată maximă: 2 ore în total; RAM cel mult ~6 GB
- de ce: comanda lui Adrian C-24 (hub, 27 oct 23:20): sesiunea OS (`cyber-universe`, C-25) scrie un motor KGR1 propriu în Rust și trebuie să-l
  verifice fără să vadă codul Kronos. Conform `CLAUDE.md`, executantul nu scrie în hub: pregătești totul în `integrare/kronos/` din cyberspace,
  iar supraveghetorul copiază dosarul în hub (`integrare/kronos/`) la trecerea următoare.
- ce faci:
  **Partea A (acum, în timpul S38):**
  1. Unealtă nouă `unelte/vectori_kgr1.py` (fără să atingi `kronos/` sau examenul): construiește un model GPT **minuscul**, cu aceeași arhitectură ca
     linia w2 (aceleași nume de tensori, LayerNorm, cap legat), dar cu dimensiuni mici (de ex. 2 straturi, n_emb 64, 4 capete, context 64) și
     **greutăți aleatoare** cu sămânță fixă (scrisă în fișier), plus tokenizerul nostru BPE inclus ca în KGR1. Îl scrie în KGR1 **F32** și **Q8_0**
     cu aceeași cale de scriere ca `unelte/exporta_greutati.py` (refolosești funcțiile, nu le copiezi). Fiecare fișier ≤ 1 MB (dacă tokenizerul
     îl face mai mare, micșorezi modelul; dacă tot nu încape, scrii de ce și mărimea).
  2. 3 texte fixe în română (scurte, de ex. „Ana are mere.”, „Capitala României este”, „def suma(a, b):”), tokenizate cu tokenizerul din fișier;
     pentru fiecare: lista de simboluri și **logit-urile** date de `unelte/inferenta_bruta.py` pe ultimul simbol (tot vectorul) și argmax-ul pe
     fiecare poziție, pentru F32 și Q8_0. Plus primele 5 simboluri generate greedy. Alături, pentru F32, diferența maximă față de PyTorch pe procesor.
  3. În `integrare/kronos/` (dosar nou în cyberspace): `format_greutati.md` (copie exactă a `docs/format_greutati.md`), `vectori/mic_f32.kgr`,
     `vectori/mic_q8_0.kgr`, `vectori/vectori.json` (texte, simboluri, logit-uri, argmax, greedy, sumele SHA-256 ale celor două fișiere) și
     `README.md` scurt, în română: ce e fiecare fișier, cum se verifică un motor, **toleranța declarată** (propunerea ta, în cifre, pentru F32 și
     pentru Q8_0, sprijinită pe diferențele măsurate; spune clar că pragul pentru modelul mare rămâne întrebarea deschisă către Adrian din S37).
     Fără greutăți reale aici. Test nou în `teste/`: fișierele din `integrare/kronos/vectori/` se recitesc și dau aceleași logit-uri (± toleranța).
  3b. **(adăugat de supraveghetor, 28 oct 05:15, cererea sesiunii OS din hub pentru C-25/P6-27b)** În `docs/format_greutati.md` (apoi copiat în
     `integrare/kronos/`) adaugi o secțiune „Tokenizerul (`tokenizer.bpe`)” care descrie, fără să trimită la codul Python: cum e scris în fișier
     (octet cu octet), vocabularul de bază, ordinea regulilor de unire, pre-tokenizarea (cum se taie textul înainte de BPE, inclusiv spații
     și diacritice), cum se codează un text și cum se decodează simbolurile înapoi în text, simbolurile speciale. Plus 3 exemple text → simboluri
     (aceleași 3 texte de la pasul 2). Scopul: OS-ul poate scrie singur tokenizerul doar din document. Nu schimbi formatul, doar îl descrii.
  4. `python -m pytest`: toate trec. Commit + push.
  **Partea B (după S38):**
  5. Alegi modelul după verdictul S38 din pre-înregistrare: dacă S38 = **CONFIRMAT** → ultimul model S38; altfel → **#441**. Exporți în **KGR1 Q8_0**:
     `python unelte/exporta_greutati.py --experiment <nr> --fel q8_0 --iesire lucru/export/kronos_<nr>_q8_0.kgr` (fișierul rămâne în `lucru/`, NU în Git).
     Calculezi SHA-256 și mărimea; cu `unelte/inferenta_bruta.py` generezi greedy primele 5 simboluri pe cele 3 texte de la pasul 2.
  6. **Release** în repo-ul privat `Adriancu91/cyberspace` (NU în hub, NU în repo-uri publice): eticheta `kronos-kgr1-<nr>`, cu fișierul ca anexă:
     `gh release create kronos-kgr1-<nr> lucru/export/kronos_<nr>_q8_0.kgr --repo Adriancu91/cyberspace --title "Kronos #<nr> KGR1 Q8_0" --notes "<suma și mărimea>"`.
     Dacă `gh` nu există sau nu e autentificat: **nu instalezi nimic**, nu te autentifici; scrii în raport unde e fișierul și suma, și treci mai departe.
  7. `integrare/kronos/MODEL.md`: numele modelului (#nr, linia, rețeta), mărimea în octeți, SHA-256, eticheta Release-ului (sau „Release nefăcut: motivul”),
     cele 3 texte cu primele 5 simboluri generate greedy (numere și text) — testul pe hardware pentru OS.
  8. `python -m pytest`: toate trec. Commit + push. Raport `docs/rapoarte/2026-10-28_<ora>_S39_kgr1_pentru_os.md`.
- Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, modelele (doar citire), S38 și configurările lui. Nimic descărcat sau instalat.
  Nu scrii în hub și nici în alte repo-uri decât Release-ul de la pasul 6.
- Dacă un pas pică de 2 ori la rând cu aceeași eroare: te oprești, stare `oprit`, scrii eroarea în raport.
- pre-înregistrare: nu e antrenare; nu e nevoie
- aprobat de: Adrian (COMENZI.md C-24, 27 oct 23:20, prin centrul de comandă; DECIZII 27 oct 23:20); pașii scriși de supraveghetor, 27 oct 23:15
- raport: docs/rapoarte/2026-10-28_0712_S39_kgr1_pentru_os.md
- verificat de supraveghetor, 28 oct 08:20: sumele SHA-256 ale vectorilor identice cu raportul; `integrare/kronos/` (format + vectori) și `docs/integrare_kronos/` (README, MODEL) copiate în hub, `integrare/kronos/`. **Rămas la Adrian:** comanda `gh release create kronos-kgr1-459 …` din raport (pasul 6).

### S40 — Porturile `cautare` și `inferenta` în nucleul `kronos/` + două module-adaptor (doar procesor)
- stare: gata (28 oct 11:15, sesiune Claude Code cu aprobarea explicită a lui Adrian; porturile noi **opționale** (`PORTURI_OPTIONALE`), `PORTURI` neschimbat; în `kronos/` doar `contracte.py`, `registru.py`, `config.py`; 979 teste trec, 1 sărit; raport docs/rapoarte/2026-10-28_1115_S40_porturi_cautare_inferenta.md)
- (istoric) oprit (executant, 28 oct 07:33; nimic atins în `kronos/`; 965 teste trec)
- **Actualizare 28 oct 08:40 (centrul de comandă):** am încercat pasul 1 într-o copie din cloud (doar `kronos/contracte.py`, cum scrie mai sus) și am
  rulat toate testele: **160 picate + 13 erori**, pentru că `kronos/config.py` cere ca **orice** port din `PORTURI` să fie în fiecare configurare
  (`lipsesc porturile: cautare, inferenta`), iar orchestratorul și `cli` le încarcă pe toate. Am **anulat schimbarea** (nimic urcat în `kronos/`).
  Concluzie: porturile noi trebuie să fie **opționale** (un `PORTURI_OPTIONALE` în `contracte.py` + 3 locuri mici în `config.py`, `orchestrator.py`,
  `cli.py`, `registru.py`), apoi modulele și testele de contract — totul într-un singur commit, ca testele să treacă la fiecare pas.
  **Se face într-o sesiune cu Adrian de față la workstation** (el aprobă scrierile în `kronos/`), nu de executant. Până atunci S40 rămâne `oprit`, fără grabă.
- **S41 nu depinde de S40** (doar `docs/` și `unelte/`, procesor): poate porni acum.
- motiv: cere aprobarea lui Adrian: schimbare în `kronos/contracte.py` (executantul n-are voie în `kronos/`, iar regula `Edit(kronos/**)` o blochează); variante în raport
- tip: procesor (fără placă: `CUDA_VISIBLE_DEVICES=-1`); nu încurcă S38/S39
- fereastră: oricând, după S39 partea A
- durată maximă: 2 ore
- de ce: Adrian a spus „Da” (27 oct 23:49, prin centrul de comandă; DECIZII 27 oct 23:49) ca piesele din `unelte/` (căutarea E3 și motorul KGR1
  fără PyTorch) să devină module înlocuibile pe platformă. Propunerile tale: raportul S29 (`cauta(intrebare, k) → bucăți ordonate`) și raportul S32.
- ce faci:
  1. În `kronos/contracte.py` **doar**: adaugi `"cautare"` și `"inferenta"` în `PORTURI`, două contracte noi (Protocol, `@runtime_checkable`, cu
     docstring în română) și le treci în `CONTRACT_PENTRU_PORT`:
     - `Cautare`: `cauta(self, intrebare: str, k: int) -> list[dict[str, Any]]` (bucăți ordonate, fiecare cel puțin cu `text` și `scor`;
       cel mult `k`; aceeași întrebare → aceeași ordine) + `statistici(self) -> dict[str, Any]`.
     - `Inferenta`: `logits(self, simboluri: list[int]) -> list[float]` (pe ultima poziție), `genereaza(self, simboluri: list[int], cate: int) -> list[int]`
       (greedy, determinist) + `statistici(self) -> dict[str, Any]` (mărimea vocabularului, contextul, formatul F32/Q8_0).
       Fără `antreneaza`: e doar citire.
     `VERSIUNE_CONTRACTE` rămâne 1 (porturile noi nu schimbă porturile vechi). Dacă un test existent cere altfel, te oprești și scrii de ce.
     **Nimic altceva în `kronos/`** (nici registru, nici orchestrator, nici paznic, nici config).
  2. Două module noi în `module/`, cu `MANIFEST` (nume, port, versiune 0.1.0, versiune_contract 1, resurse gpu: False), care **refolosesc** codul din
     `unelte/` (import, nu copie): `module/cautare_e3.py:CautareE3` (varianta aleasă la S29/S33: S25 + rădăcini + RRF; fără judecător-model în
     varianta implicită, ca să meargă fără placă) și `module/inferenta_kgr1.py:InferentaKGR1` (în jurul `MotorBrut` din `unelte/inferenta_bruta.py`).
  3. Le adaugi în lista `MODULE` din `teste_contracte/test_contracte.py`, pe date mici de probă (o bază SQLite minusculă creată în test; modelul KGR1
     minuscul din S39 sau unul creat în test) — fără bazele mari din `lucru/`. Plus un test că modulul de inferență dă aceleași logit-uri ca `MotorBrut`.
  4. `teste/test_arhitectura.py` trece (kronos/ nu importă din module/); `python -m pytest`: **toate** trec. Commit + push.
  5. Raport scurt `docs/rapoarte/2026-10-28_<ora>_S40_porturi_cautare_inferenta.md`: diff-ul din `kronos/` (întreg, e mic), modulele, numărul de teste.
- Nu atingi `module/examen_bpb.py`, paznicul, jurnalul, modelele, S38/S39, interfața. Nimic descărcat sau instalat.
- Dacă un pas pică de 2 ori la rând cu aceeași eroare: stare `oprit`, eroarea în raport; **nu** ocoli testele.
- pre-înregistrare: nu e antrenare; nu e nevoie
- aprobat de: Adrian (27 oct 23:49, „Da” prin centrul de comandă; DECIZII.md din hub; nota din coadă 27 oct 23:50); pașii scriși de supraveghetor, 28 oct 02:15
- raport: docs/rapoarte/2026-10-28_0733_S40_oprit_kronos.md
- notă supraveghetor (28 oct 08:20): oprirea e corectă. Varianta 2 a executantului: **S40a** = pasul 1 (doar `kronos/contracte.py`, exact cum scrie mai sus),
  făcut de o sesiune Claude Code cu Adrian de față (`propus — necesită Adrian`); **S40b** = pașii 2–5 (modulele, testele, raportul), executantul, abia după
  ce S40a e `gata` și toate testele trec. Când văd S40a gata, trec S40b pe `aprobat`. Executantule: nu reîncerca S40.

### S41 — C-28 E4 „Kronos-Cod”, etapa 1a: sursele + licențele, examenul de cod scris înainte, cutia izolată (doar procesor, fără descărcări)
- stare: gata (executant, 28 oct 14:15, cbac20a: SURSE.md ~3,0 mld simboluri estimate, 6 surse fără cont, 8 la „necesită Adrian”; examenul ascuns 200 de probleme, sha 90fc64cd…3749, referințe 100 %, gol/None 0 %; cutia: tot ce cerea e blocat, fără nimic instalat, fără firewall; 999 teste trec, 1 sărit)
- tip: procesor (fără placă); nu încurcă S38–S40
- fereastră: oricând — **nu depinde de S40** (supraveghetor, 28 oct 08:20); dacă S42 e `aprobat` și nepornită, pornește întâi S42
- durată maximă: 4 ore
- de ce: comanda lui Adrian C-28 (hub, 27 oct 23:45): model separat ~150M doar pe cod, apoi auto-îmbunătățire cu teste care rulează. Înainte de orice
  descărcare și antrenare trebuie: lista surselor cu licențele verificate, examenul scris și pus deoparte, și cutia în care rulează codul generat.
  Linia română (#441 și urmașii) **nu se atinge**.
- ce faci:
  1. `docs/kronos_cod/SURSE.md`: propunerea de surse **doar cod scris de oameni, licențe MIT / Apache-2.0 / BSD**, Python + Rust (+ puțin C), fără nimic
     generat de un LLM. Pentru fiecare sursă: ce e, licența (cu legătura către textul licenței), mărimea estimată în GB și în simboluri, cum se descarcă
     **fără cont și fără autentificare** (dacă o sursă cere cont, acceptarea unor termeni sau o cheie, o treci separat la „necesită Adrian” și propui alta),
     cum se elimină duplicatele și cum se scot fișierele generate automat. Ținta: ~3 miliarde de simboluri. Doar documentezi, **nu descarci încă**
     (descărcarea = etapa 1b, după ce verific lista).
  2. **Examenul de cod**, scris ACUM, înainte de date și antrenare: `unelte/kronos_cod/examen_cod.py` + probleme mici în Python cu teste unitare,
     din șabloane proprii (de ex. 20 de șabloane × variante) + un **set ascuns** generat cu sămânță fixă, ținut în `lucru/kronos_cod/examen_ascuns/`
     (NU în Git; în Git doar suma SHA-256 a setului și numărul de probleme). Măsoară pass@1 și pass@10. Verificare: soluțiile de referință scrise de
     tine trec 100 %, iar o soluție goală/greșită trece 0 %. Problemele nu au voie să vină de la un LLM străin (le scrii tu, din șabloane).
  3. **Cutia izolată** `unelte/kronos_cod/cutie.py`: rulează codul de verificat într-un **proces separat**, într-un dosar temporar, cu limită de timp
     și de memorie, fără rețea și fără acces la fișiere în afara dosarului: listă de module permise (fără `os`, `subprocess`, `shutil`, `socket`,
     `ctypes`, `importlib`, `open` în afara dosarului etc.). Teste care arată că sunt **blocate**: citirea unui fișier din afară, scrierea în afară,
     o conexiune de rețea, pornirea unui proces, o buclă infinită (limita de timp), o alocare uriașă (limita de memorie). Dacă pe Windows o limită
     nu se poate pune fără să instalezi ceva sau să schimbi setări, **nu instalezi**: scrii clar în raport ce lipsește și ce ar trebui.
  4. Tot în `unelte/` (fără port nou în `kronos/`; dacă pare nevoie de unul, doar propui în raport). `python -m pytest`: toate trec. Commit + push.
  5. Raport `docs/rapoarte/2026-10-28_<ora>_S41_kronos_cod_etapa1a.md`: lista surselor pe scurt, examenul (câte probleme, cum arată unul), testele
     cutiei (ce e blocat, ce nu), și propunerea ta pentru etapa 1b (descărcare + curățare + tokenizer BPE pe cod: cât spațiu, cât timp).
- Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, modelele, linia română, interfața. **Nimic descărcat sau instalat.**
- Dacă un pas pică de 2 ori la rând cu aceeași eroare: stare `oprit`, eroarea în raport.
- pre-înregistrare: nu e antrenare încă; pragurile pentru etapa 2 (pass@10 pe setul ascuns) le scriu eu după etapa 1a, înainte de orice antrenare
- aprobat de: Adrian (COMENZI.md C-28, 27 oct 23:45, prin centrul de comandă; DECIZII 27 oct 23:45); pașii (doar etapa 1a) scriși de supraveghetor, 28 oct 02:15
- raport: docs/rapoarte/2026-10-28_1415_S41_kronos_cod_etapa1a.md

### S42 — Cititorul E3 refăcut din #459 cu rețeta A (cel mai bun model + cea mai bună rețetă → răspunde mai bine?) (placa)
- (istoric) stare: oprit (executant, 28 oct 12:36: reluarea pornită 12:29:43, proces 21116; amestec sha 2cb23401… același, diff-urile config neschimbate; dosarul vechi mutat în lucru/w2_e3_reteta_A_intrerupt_1028/)
- motiv: linia `w2_e3_reteta_A` are deja ora 1 (#462) în jurnal → `antrenare_lunga.py` sare peste `--porneste-din 459` și, fără gpt.pt, antrenează DE LA ZERO („orele 2–3”); `taskkill` cere aprobare → am apăsat `python -m kronos opreste` (lucru/STOP): ora în curs se termină ~13:30, apoi stop; după aceea executantul resetează cu `python -m kronos porneste --config config/conv_w2_e3_reteta_A.toml`. Propunere: linie nouă `w2_e3_reteta_A2` (doar `nume` + `cale_stare`), la 19:00 — o aprobă supraveghetorul
- verificat de supraveghetor (28 oct 23:15): **INFIRMAT** confirmat după prag (Δ 0 ≤ +1; S4 −3); cititorul rămâne #438.
- stare: gata (executant, 28 oct 23:03: examenele 22:30–22:50, cod 0; **INFIRMAT** — S26 `rrf_reord` #466 66 / #438 66 (Δ 0 ≤ +1); noaptea 10 70 / 69; S4 36 / 39 (−3); română curat #466 1,2148 / #459 1,2162; 1003 teste trec, 1 sărit)
- stare veche: in_lucru (executant, 28 oct 22:31: antrenarea 19:00–22:12, cod 0 (jurnalul cascadei mutat în lucru/cascada/S42_1900.*); examenele pornite 22:30 prin cascadă, `python -X utf8 unelte/e3_reteta_A.py` (unealtă nouă, d725f43), proces 15912; sfârșit estimat ~23:15. Înainte: 19:02 linia `w2_e3_reteta_A2`, 0 ore în jurnal, dosarul nu exista; amestec sha 2cb23401… același)
- (istoric) stare: aprobat — **a doua reluare, ca linie nouă `w2_e3_reteta_A2`, la 19:00 (fereastra de noapte)** (supraveghetor, 28 oct 14:25)
- **A doua reluare (supraveghetor, 28 oct 14:25) — înlocuiește data și numele de mai jos; tot restul pașilor rămâne:**
  - Oprirea de la 12:36 a fost corectă (antrena de la zero). Aleg **propunerea 1** a executantului: linie nouă, fiindcă jurnalul nu se editează.
    Granița 1 (încă o rulare pe linia E3 existentă; schimbă doar numele sub care se scrie în jurnal, nu modelul, rețeta sau datele).
  - **Când:** la **19:00** azi, 28 oct (nu mai încape în fereastra de zi). Înaintea oricărei alte sarcini de placă. Sfârșit estimat: antrenarea ~22:15, examenele ~23:15.
  - **Configurarea:** în `config/conv_w2_e3_reteta_A.toml` schimbi DOAR `nume = "w2_e3_reteta_A2"` și `cale_stare = "lucru/w2_e3_reteta_A2/gpt.pt"`
    (plus eticheta `"S42: E3 din #459, rețeta A (linia A2)"`). Arăți în raport `diff` față de versiunea e77a0eb: doar aceste rânduri. Verifici că
    `lucru/w2_e3_reteta_A2/` nu există și că linia `w2_e3_reteta_A2` are **0 ore** în jurnal (o scrii în raport).
  - **Pre-înregistrarea:** pragurile rămân exact cele din `docs/preinregistrari/2026-10-28_E3_reteta_A.md` (nemăsurată). Ca să nu atingi textul ei,
    scrii una nouă, `docs/preinregistrari/2026-10-28_E3_reteta_A2.md`: aceeași întrebare, măsură și praguri **cuvânt cu cuvânt** (copiate), cu o notă
    la început: „reluarea S42 ca linie nouă după două întreruperi (11:00 repornirea OS/GPU; 12:36 pornire greșită de la zero); E3_reteta_A n-a
    măsurat nimic”, ora nouă de sfârșit și așteptările tale. **Commit + push înainte de pornire.** Pe cea veche o închizi, dacă unealta permite,
    ca „fără măsurare — înlocuită de E3_reteta_A2”; dacă nu permite, o lași cum e și scrii asta în raport. Verdictul se închide pe `E3_reteta_A2`.
  - **Rularea:** `cascada.py porneste S42 -- python unelte/antrenare_lunga.py --config config/conv_w2_e3_reteta_A.toml --ore 3 --porneste-din 459`.
    **În primele 2 minute verifici în ieșire că scrie „Pornesc din modelul experimentului #459”** (și „ora 1” a liniei). Dacă nu apare, oprești
    imediat cu butonul paznicului (`python -m kronos opreste --config config/conv_w2_e3_reteta_A.toml`), `oprit`, raport; nu încerci altă variantă.
  - Experimentul de la zero din 12:29–13:35 (linia `w2_e3_reteta_A`, „ora 2”) nu se folosește nicăieri; rămâne în jurnal, neatins.
  - Apoi pașii 5–6 de mai jos neschimbați (examenele pe ultimul model al liniei A2 și pe #438, în aceeași rulare). Raport `docs/rapoarte/2026-10-2X_<ora>_S42_E3_reteta_A.md`.
- (istoric) oprit (executant, 28 oct 12:36) — vezi mai jos; raportul 2026-10-28_1236_S42_oprit_reluare.md.
- **Reluarea (supraveghetor, 28 oct 11:20):** oprirea a fost corectă; cauza = fereastra OS/GPU, nu modelul. Faci S42 **de la zero**, exact pașii de mai jos, cu:
  - **Când:** nu înainte de **12:15** (după fereastra OS/GPU) și doar dacă Windows e pornit normal și placa e liberă. Pornește-o **înaintea S41**.
    Dacă nu poate porni până la **14:30** (n-ar încăpea în fereastra de zi, ~4 ore), o pornești la **19:00**, în fereastra de noapte.
  - **Înainte de pasul 4:** muți (nu ștergi) `lucru/w2_e3_reteta_A/` în `lucru/w2_e3_reteta_A_intrerupt_1028/` (pleacă și `ruleaza.lock` cu el),
    ca regula „dosarul nu există” să fie respectată. `experiment_462.pt` rămâne în jurnal, neatins; nu e modelul examinat.
  - **Pre-înregistrarea rămâne aceeași** (`docs/preinregistrari/2026-10-28_E3_reteta_A.md`, încă deschisă; nu s-a măsurat nimic din ea). N-o modifici;
    în raport scrii că e reluarea după întrerupere și ora nouă de sfârșit (o scrii și aici în coadă la pornire).
  - Pașii 1–3 deja făcuți (date, configurare, pre-înregistrare): îi verifici doar (aceeași sumă SHA-256 a amestecului, `diff` neschimbat).
  - Nu continui din #462 (varianta 2): răcirea e programată pe 3 ore de la pornire.
- (istoric) oprit (executant, 28 oct 11:00; ora 1 gata = #462 la 09:37, val_bpb 0,4158; procesul întrerupt fără cod după 09:59 de fereastra OS/GPU; fără examene, fără verdict)
- motiv: antrenarea întreruptă de repornirea workstation-ului (fereastra OS/GPU 28 oct ~10:05–12:00; Windows repornit 10:50); n-am reluat-o — propunerile în raport
- tip: placă (~3 ore de antrenare + ~1 oră examene)
- fereastră: zi (28 oct), reluarea de la 12:15 până cel târziu 14:30; altfel noaptea de la 19:00 — **înaintea S41**
- durată maximă: 3 ore de antrenare; cel mult 5 ore pe placă în total; placa sub 7.000 MB și 83 °C
- de ce: S38 a CONFIRMAT #459 (cel mai bun pe română, 1,2162) și rețeta A (S34). Cititorul E3 de azi, #438, e făcut din #415 cu rețeta veche
  (S27) și dă 66/100 cu `rrf_reord` (S33). Întrebarea: **dacă refacem cititorul din #459 cu rețeta A, răspunde corect la mai multe întrebări?**
  Granițele 1 și 2: încă o rulare pe linia E3 existentă (altă copie de plecare, rețeta deja confirmată) + examene. Linia română (#459) nu se atinge.
- ce faci:
  1. **Datele:** verifici că `lucru/e3/amestec_s27.jsonl` există și are aceeași sumă SHA-256 ca la S27 (o scrii în raport). Dacă lipsește, îl refaci
     cu exact comanda din S27 (`unelte/e3_memorie.py date-antrenare`) și verifici că iese același număr de exemple; dacă nu iese la fel, te oprești (`oprit`).
  2. **Configurarea** `config/conv_w2_e3_reteta_A.toml` = copie exactă a `config/conv_w2_reteta_A_cont.toml`, cu DOAR: `nume = "w2_e3_reteta_A"`,
     `cale_stare = "lucru/w2_e3_reteta_A/gpt.pt"`, `conversatie = "lucru/e3/amestec_s27.jsonl"` (amestecul E3 al lui #438), `durata_scaderii_secunde = 10800`
     (răcirea în ultimele 25 % din 3 ore), eticheta `"S42: E3 din #459, rețeta A"` și un antet scurt. Verifici că `lucru/w2_e3_reteta_A/` nu există.
     Arăți în raport `diff` față de `conv_w2_reteta_A_cont.toml` și față de `conv_w2_e3_memorie.toml`.
  3. **Pre-înregistrarea** `docs/preinregistrari/2026-10-28_E3_reteta_A.md`, **urcată (commit + push) ÎNAINTE de pornire**, cu pragurile cuvânt cu cuvânt:
     măsura = corecte din cele 100 S26, sistemul primește doar întrebarea, bucățile `rrf_reord` (ca la S33, judecătorul = modelul examinat), notat cu
     verificatorul S16, aceeași regulă „câte bucăți încap în 448 de simboluri”, fără întâmplare. Δ = nou − #438, **în aceeași rulare**.
     **CONFIRMAT** dacă **Δ ≥ +5** **și** pe noaptea 10 și S4 (cu textul dat) noul nu pierde **mai mult de 2 puncte** față de #438;
     **INFIRMAT** dacă **Δ ≤ +1**; între ele: **NECLAR**. Alături (nu decid): aceleași 100 cu bucățile S25 simple pentru ambele; eșantionul 2048
     al validării (ca la S35) pentru ambele; `unelte/examen_validari_ws.py` pe noul model și pe #459 (română curat, cod curat, R2, fapte noi).
     **Spus cinstit:** setul S26 e folosit a cincea oară (doar măsurat, nimic ales pe el); noul diferă de #438 prin două lucruri (copia de plecare și
     rețeta), deci un câștig nu spune care din ele l-a adus. Plus așteptările tale în cifre și ora estimată de sfârșit (scrisă și în coadă la pornire).
  4. **Rularea**, prin cascadă: `cascada.py porneste S42 -- python unelte/antrenare_lunga.py --config config/conv_w2_e3_reteta_A.toml --ore 3 --porneste-din 459`.
     Dacă pornirea din #459 nu merge cu configurarea asta (de ex. starea nu se încarcă), te oprești la prima eroare, `oprit`, scrii eroarea; nu schimbi modulul.
  5. **Examenele, o singură rulare**, pe ultimul model nou și pe #438: cele de la pasul 3 (100 S26 cu `rrf_reord` și cu S25 simplă, noaptea 10, S4,
     2048) + validările. Paznicul verificat la fiecare 20 de întrebări; peste 7.000 MB → oprești, `oprit`, scrii cifrele. Verdictul strict după
     pre-înregistrare; o închizi cu `unelte/preinregistrare.py --inchide E3_reteta_A`.
  6. `python -m pytest`: toate trec. Commit + push. Raport `docs/rapoarte/2026-10-28_<ora>_S42_E3_reteta_A.md`, cu propunerea ta pentru pasul următor.
- Nu atingi `kronos/`, `module/examen_bpb.py`, `module/model_muon.py`, paznicul, jurnalul, datele de examen, `text_v3`, lista S26, indexurile din
  `lucru/e3/` (doar citire), `unelte/verificator_text.py`, #415, #438, #441, #459 și configurările lor. Modelul nou NU intră în interfață. Nimic descărcat
  sau instalat; nimic din `lucru/` în Git.
- Dacă un pas pică de 2 ori la rând cu aceeași eroare: te oprești, stare `oprit`, scrii eroarea în raport.
- Dacă Adrian are nevoie de placă pentru fereastra OS/GPU: S42 nu pornește cât e anunțată fereastra (o anunță centrul de comandă).
- pre-înregistrare: docs/preinregistrari/2026-10-28_E3_reteta_A2.md (nouă, praguri copiate din E3_reteta_A; urcată înainte de pornire)
- aprobat de: supraveghetor, 28 oct 08:20 (granițele 1 și 2 din REGULI_CASCADA.md; continuarea a ce a mers: S33 + S34 + S38); a doua reluare (linia A2, 19:00): supraveghetor, 28 oct 14:25
- raport: docs/rapoarte/2026-10-28_2303_S42_E3_reteta_A.md (INFIRMAT); înainte: docs/rapoarte/2026-10-28_1236_S42_oprit_reluare.md, docs/rapoarte/2026-10-28_1100_S42_oprit_repornire.md

### S40a — Pasul 1 din S40: porturile `cautare` și `inferenta` în `kronos/contracte.py` (cu Adrian de față)
- stare: gata — făcut împreună cu S40b în S40 (28 oct 11:15, porturi opționale; vezi S40). Executantul nu mai are nimic de făcut la S40.
- tip: procesor, ~20 de minute
- ce: exact pasul 1 din S40 (doar `kronos/contracte.py`: `PORTURI`, două contracte, `CONTRACT_PENTRU_PORT`; `VERSIUNE_CONTRACTE` rămâne 1), apoi
  `python -m pytest` (toate trec, inclusiv `teste/test_arhitectura.py`), commit + push, S40a `gata`. O face o sesiune Claude Code deschisă de Adrian pe
  workstation, în `C:\Kronos\cyberspace`, cu el de față (executantul programat n-are voie în `kronos/`). Apoi S40b = pașii 2–5 din S40, pentru executant.
- aprobat de: Adrian a spus „Da” la porturi (27 oct 23:49); lipsește doar omul de față la scriere

### S43 — C-28 E4 „Kronos-Cod”, etapa 1b: pilotul de descărcare (500 PyPI + 500 crates + numpy, tokio, libuv), apoi descărcarea întreagă, curățarea și tokenizerul (procesor + rețea)
- stare: gata — DOAR PILOTUL (executant, 29 oct 03:03: 02:29–02:51, cod 0; 688 din 1.003 pachete păstrate + numpy/tokio/libuv; 0,558 → 0,376 GB cod, 55.847 → 37.088 fișiere, ~107 mil. simboluri; 1,01 GB trași din rețea; C: 73 GB liberi; 1058 teste trec, 1 sărit). Descărcarea întreagă NEpornită — aștept verificarea supraveghetorului și aprobarea.
- stare anterioară: in_lucru (executant, 29 oct 02:30 — DOAR PILOTUL; înainte: aprobat — DOAR PILOTUL, supraveghetor, 29 oct 02:15, după verificarea uneltei S43a; pe „da”-ul lui Adrian din 28 oct 18:00)
- stare veche: oprit (executant, 28 oct 18:03; nepornită, nimic descărcat; înainte: aprobat de Adrian, 28 oct 18:00)
- **comanda exactă (supraveghetor, 29 oct 02:15):** prin cascadă, oricând (nu folosește placa; poate rula și cât e ceva pe placă):
  `.venv/Scripts/python -X utf8 unelte/cascada.py porneste S43 -- .venv/Scripts/python -X utf8 unelte/kronos_cod/descarca.py pilot`
  (implicit `--iesire lucru/kronos_cod/pilot --pypi 500 --crates 500` + numpy v1.21.0, tokio-1.7.0, libuv v1.41.0). Dacă se oprește (rețea, cădere), aceeași
  comandă o reia; a doua cădere cu aceeași eroare → `oprit` și raport. Durată maximă: 3 ore. **Nu porni descărcarea întreagă** și nu antrena tokenizerul.
  Raport `docs/rapoarte/2026-10-2X_<ora>_S43_pilot.md` cu cifrele din `rezumat.json`: GB arhive, GB brut → curat, fișiere brut → curat, simboluri estimate,
  procentul aruncat de fiecare filtru, pachetele respinse pe motive (cu numărul separat pentru `fara_fisier_licenta` la crates și ce s-a întâmplat cu
  numpy/tokio/libuv), spațiul liber pe C: la final, timpul. Plus o estimare pentru descărcarea întreagă (GB curat, simboluri, ore, spațiu) din cifrele pilotului.
  Nimic din `lucru/` în Git; nimic instalat; nimic în `kronos/`, examen, paznic, jurnal, `EXAMEN.md`, `cutie.py`.
- **Supraveghetor, 28 oct 20:25:** oprirea a fost corectă (regula cere unealta numită în „ce faci”). Aleg **varianta 1** a executantului:
  întâi **S43a** (mai jos) scrie unealta pilotului și testele ei, **fără rețea**; la trecerea următoare după S43a verific unealta și trec aici
  comanda exactă, apoi S43 redevine `aprobat` (pe „da”-ul lui Adrian din 28 oct 18:00, care rămâne valabil doar pentru pilot). Până atunci S43 rămâne `oprit`.
- motiv: cere aprobarea lui Adrian: descărcare — „ce faci” nu numește unealta de descărcare (nu există încă); regula executantului cere „prin unealta scrisă acolo”. Propunerile în raport.
- tip: procesor + rețea (fără placă); pilotul ~1 oră; descărcarea întreagă ~20 de ore (2–3 nopți, în flux, fără arhive pe disc); curățarea 3–5 ore; tokenizerul 3–6 ore
- fereastră: oricând (nu încurcă placa)
- ce faci (după „da”): exact propunerea din `docs/rapoarte/2026-10-28_1415_S41_kronos_cod_etapa1a.md`, §5: **întâi doar pilotul**, cu toate filtrele din
  `docs/kronos_cod/SURSE.md`, raport cu GB brut → curat, simboluri estimate, cât a aruncat fiecare filtru, licențele verificate (metadate + LICENSE).
  Supraveghetorul verifică pilotul înainte de descărcarea întreagă. Spațiul pe C: (74 GB liberi): te oprești dacă scade sub 40 GB.
  Tokenizerul nou se antrenează doar după un al doilea „da” (linie de model nouă).
- Întrebări pentru Adrian (din raportul S41): (1) „da” pentru pilot; (2) data-limită: 29 iunie 2021 (recomandat de executant și de mine: fără cod
  scris de LLM) sau 30 nov 2022 (+~40 % date); (3) cele 8 surse „necesită Adrian” (The Stack cere cont HF etc.) — recomandarea mea: deocamdată niciuna;
  (4) cutia mai tare (regulă de firewall pentru python.exe sau cont Windows separat) — nu e nevoie acum, ci înainte de etapa 3 (auto-îmbunătățirea).
- pre-înregistrare: pragurile etapei 2 (pass@10 pe setul ascuns) le scrie supraveghetorul înainte de orice antrenare Kronos-Cod
- aprobat de: Adrian, 28 oct 18:00, prin centrul de comandă. Răspunsuri: (1) **da** pentru pilot; descărcarea întreagă după ce supraveghetorul verifică pilotul; (2) data-limită **29 iunie 2021** (fără cod scris de LLM); (3) dintre sursele „necesită Adrian”: **niciuna deocamdată** (cum recomanzi); (4) cutia mai tare: înainte de etapa 3, nu acum. Tokenizerul nou: tot după al doilea „da”.
- verificat de supraveghetor, 29 oct 05:15: cifrele se adună (330 + 355 + 3 = 688 păstrate; 315 respinse = 180 + 67 + 51 + 11 + 4 + 2, și pe surse 170 / 145;
  filtrele însumează 32,7 % = 0,5583 → 0,3757 GB; 0,3757 GB / 3,5 octeți ≈ 107 mil. simboluri; pe surse 280,7 + 74,1 + 21,0 = 375,8 MB); C: 73 GB > 40 GB;
  21,7 min < 3 ore; nimic instalat, nimic în `kronos/`/examen. **Pilotul e bun.** Estimarea pentru tot: ~10–22 GB curat, ~3–6 mld simboluri, ~15–25 de ore —
  în ținta din SURSE.md (~3 mld). Unealta are doar modul `pilot` → S46a (modul `complet`, fără rețea, în granițe), apoi S46 (descărcarea întreagă, cere „da”).
- raport: docs/rapoarte/2026-10-29_0303_S43_pilot.md (pilotul); înainte: docs/rapoarte/2026-10-28_1803_S43_oprit_descarcare.md (oprit înainte de pornire)

### S43a — Kronos-Cod etapa 1b, pregătirea: unealta pilotului de descărcare + testele ei, FĂRĂ rețea (doar procesor)
- stare: gata (executant, 28 oct 23:39, e650232: `unelte/kronos_cod/descarca.py pilot` + 48 de teste fără rețea; 1051 teste trec, 1 sărit; nimic descărcat, pilotul NEpornit; comanda pentru S43 în raport)
- tip: procesor (fără placă, fără rețea)
- fereastră: oricând, **după ce S42 e `gata` sau `oprit`** (o singură sarcină odată; nu întrerupe S42)
- durată maximă: ~2 ore
- de ce: S43 (pilotul, aprobat de Adrian 28 oct 18:00) s-a oprit corect pentru că nu exista unealta de descărcare numită în „ce faci”.
  Granița 5 din REGULI_CASCADA.md (unealtă nouă în `unelte/` + teste noi, fără `kronos/` și fără examen). **Aici nu se descarcă nimic.**
- ce faci:
  1. Scrii `unelte/kronos_cod/descarca.py`, cu un mod `pilot` (500 PyPI + 500 crates + numpy, tokio, libuv, exact ca la §5 din raportul S41)
     și toate regulile din `docs/kronos_cod/SURSE.md`: doar licențele permise de acolo (verificate din metadate **și** din fișierul LICENSE),
     data-limită **29 iunie 2021** (versiunea publicată cel târziu atunci), filtrele de cod generat/duplicat/fișiere mari de acolo; politețe:
     crates.io ≤ 1 cerere/s, PyPI ≤ 5 cereri/s, un User-Agent care spune cine descarcă; în flux (arhivele se citesc din memorie, nu se scriu pe disc);
     ieșirea în `lucru/kronos_cod/pilot/` (nimic din `lucru/` în Git); **se oprește singură dacă spațiul liber pe C: scade sub 40 GB**;
     se poate relua de unde a rămas; la final scrie un rezumat JSON: GB brut → curat, fișiere, simboluri estimate, cât a aruncat fiecare filtru,
     câte pachete respinse pentru licență și de ce.
  2. Teste noi `teste/test_kronos_cod_descarca.py`, **fără rețea** (răspunsuri false din fișiere mici scrise în test): licența respinsă,
     versiunea după 29 iunie 2021 respinsă, filtrele, oprirea sub 40 GB (spațiu simulat), reluarea, ritmul cererilor, faptul că nu scrie arhive pe disc.
     Testele nu au voie să deschidă conexiuni (dacă vreuna încearcă, testul pică).
  3. `python -m pytest`: toate trec. Commit + push.
  4. În raport `docs/rapoarte/2026-10-2X_<ora>_S43a_unealta_pilot.md`: **comanda exactă** a pilotului (de copiat în S43), ce face fiecare filtru,
     cât estimezi că durează și cât spațiu ia pilotul. **Nu pornești pilotul** — îl pornești doar după ce supraveghetorul trece comanda în S43 și o face `aprobat`.
- Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, `docs/kronos_cod/EXAMEN.md`, examenul de cod ascuns, `unelte/kronos_cod/cutie.py`. Nimic instalat
  (dacă îți trebuie o bibliotecă care nu e instalată, te oprești și scrii asta — instalarea cere „da”-ul lui Adrian).
- Dacă un pas pică de 2 ori la rând cu aceeași eroare: te oprești, stare `oprit`, scrii eroarea în raport.
- pre-înregistrare: nu e nevoie (nu se antrenează și nu se măsoară nimic)
- aprobat de: supraveghetor, 28 oct 20:25 (granița 5; varianta 1 propusă de executant în raportul 2026-10-28_1803)
- raport: docs/rapoarte/2026-10-28_2339_S43a_unealta_pilot.md
- verificat de supraveghetor, 29 oct 02:15: unealta citită (dată, licențe, oprirea sub 40 GB, reluarea, ritmul, fără arhive pe disc); cele 48 de teste trec
  și în cloud, fără rețea. Comanda trecută în S43, care e acum `aprobat` (doar pilotul).

### S44 — E3: bucățile tăiate pe propozițiile utile (încap mai multe în 448 de simboluri → răspunde mai bine?) (procesor + sub 1 oră pe placă)
- stare: gata (executant, 29 oct 00:33) — INFIRMAT, Δ −7,8 puncte (297 vs 336 din 500)
- tip: procesor + placă scurt (examen, nimic antrenat)
- fereastră: oricând, **după ce S43a e `gata` sau `oprit`** (o singură sarcină odată); partea pe placă doar dacă placa e liberă
- durată maximă: 3 ore în total; cel mult 1 oră pe placă; placa sub 7.000 MB și 83 °C
- de ce: S42 a INFIRMAT (Δ 0): alt model de plecare nu face un cititor mai bun. Raportul S42 (propunerea 2) arată unde e pierderea: cu `rrf_reord`
  răspunsul e în primele 3 bucăți aduse la 83 din 100, dar în bucățile care încap în 448 de simboluri doar la 72. Contextul modelului e 512
  (mai lung = linie nouă, cere „da”-ul lui Adrian), deci încercăm varianta din granițe: **păstrăm din fiecare bucată doar propozițiile legate de
  întrebare**, ca să încapă mai multe bucăți. Granițele 2 și 5 (examen + unealtă nouă în `unelte/` cu teste). Măsurăm pe **validare** (eșantionul
  2048, ca la S35), **nu pe S26** (folosit deja de 5 ori).
- ce faci:
  1. **Unealta (procesor):** în `unelte/e3_citire_reord.py` (sau un fișier nou `unelte/e3_taiere.py`, importat de acolo) o funcție deterministă
     `taie(bucata, intrebare)`: împarte bucata în propoziții (`.`, `!`, `?`, rând nou), dă fiecărei propoziții un scor = câte rădăcini din întrebare
     conține (`radacina()` din `unelte/e3_reordonare.py`; fără cuvintele de legătură), păstrează **în ordinea inițială** propozițiile cu scor ≥ 1, plus
     prima propoziție a bucății (titlul/subiectul); dacă nicio propoziție nu are scor ≥ 1, bucata rămâne întreagă. Fără model, fără întâmplare.
     Teste noi fără placă: ordinea păstrată, bucata neschimbată când nu se potrivește nimic, determinism, că regula „câte încap în 448” numără
     bucățile tăiate. **Nu schimbi** ordinea bucăților, promptul S27, verificatorul S16 și nici regula de 448.
  2. **Pre-înregistrarea** `docs/preinregistrari/2026-10-29_E3_bucati_taiate.md` (sau data zilei), **urcată (commit + push) ÎNAINTE de pasul 3**.
     Modelul: **#438** (cititorul de azi), și ca judecător `rrf_reord` în ambele brațe (deci aceeași ordine a bucăților; diferă doar tăierea).
     Setul: eșantionul **2048** din `lucru/e3/validare_s29.json`, aceleași 500 de întrebări ca la S35 (fără cele văzute de #438).
     Măsura care decide: Δ = procentul de răspunsuri corecte cu bucăți **tăiate** − procentul cu bucăți **întregi**, **în aceeași rulare**.
     **CONFIRMAT** dacă **Δ ≥ +2,0 puncte**; **INFIRMAT** dacă **Δ < +0,5 puncte** (inclusiv negativ); între ele: **NECLAR**.
     Alături (nu decid): „răspunsul în bucățile date” în ambele brațe; câte bucăți încap în medie; pe tipuri (definiții, născut, an, regizat, rest);
     reparate / stricate; eșantionul 1024. Spus cinstit: validarea vine din `text_v3` (văzut de #415), iar `rrf_reord` a fost ales pe validare.
     Plus așteptările tale în cifre.
  3. **Examenul, o singură rulare** (opțiune nouă, de ex. `examen --set validare --taiere`, care rulează ambele brațe în același proces și refuză dacă
     ieșirea există deja) → `lucru/e3/examen_s44.json`. Paznicul S17 la fiecare 50 de întrebări; peste 7.000 MB → oprești, `oprit`, scrii cifrele.
  4. `python -m pytest`: toate trec. Commit + push. Raport `docs/rapoarte/2026-10-2X_<ora>_S44_E3_bucati_taiate.md`, cu verdictul strict după
     pre-înregistrare. Dacă iese CONFIRMAT, propui verificarea pe un set neatins (nu pe S26); dacă iese INFIRMAT, propui ce ai învățat.
- Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, datele de examen, `text_v3`, lista S26, `validare_s29.json`, indexurile din
  `lucru/e3/` (doar citire), `unelte/verificator_text.py`, #415, #438, #459, #466 și liniile w2. Nimic antrenat, descărcat sau instalat; nimic în
  interfață; nimic din `lucru/` în Git.
- Dacă un pas pică de 2 ori la rând cu aceeași eroare: te oprești, stare `oprit`, scrii eroarea în raport.
- pre-înregistrare: docs/preinregistrari/2026-10-29_E3_bucati_taiate.md (urcată înainte de pasul 3)
- aprobat de: supraveghetor, 28 oct 23:15 (granițele 2 și 5 din REGULI_CASCADA.md; propunerea 2 a executantului din raportul S42)
- raport: docs/rapoarte/2026-10-29_0033_S44_E3_bucati_taiate.md
- verificat de supraveghetor, 29 oct 02:15: pre-înregistrarea (32ce496, 00:03:16) înaintea examenului (00:03:26) ✓; 336 și 297 din 500, adunate din nou pe tipuri ✓;
  Δ −7,8 < +0,5 → **INFIRMAT**, corect. Tăierea pe propoziții se închide.

### S45 — Încă o noapte pe linia w2 cu rețeta A, din #459 (placa)
- stare: oprit (executant, 29 oct 23:34)
- notă supraveghetor (30 oct 02:15): **închisă fără verdict** (varianta 3 din raport). Orele 1–3 (#469–#471) rămân în jurnal ca informație, fără notare. Întrebarea se repetă de la capăt ca **S51**. Nu se reia din #471 și nu se notează #471. `ruleaza.lock` din `lucru/w2_reteta_A_cont2/` rămâne neatins (linia nu se mai folosește).
- motiv: procesul (14764) a căzut la 23:09:36, în ora 4 din 6, fără eroare în jurnal și fără cod de ieșire (repornire sau oprire din afară; cauza n-am putut-o vedea). Salvate orele 1–3: #469 0,4185, #470 0,4167, #471 0,4150 (gpt.pt 22:10); placa în limite (6.116 MB, 64 °C). Examenele n-au rulat, deci nu există verdict, iar pre-înregistrarea rămâne deschisă. N-am reluat-o singur: la aceeași comandă `antrenare_lunga.py` ar sări peste `--porneste-din 459` (capcana S42). Decizia (reluare din #471 / doar examenele / închidere) e la supraveghetor sau la Adrian.
- stare anterioară: in_lucru (executant, 29 oct 19:00)
- verificat de supraveghetor (29 oct 20:15): pre-înregistrarea urcată înainte de pornire (96a0e84, 19:00:53), pragurile copiate exact din coadă (≤ 1,2112 CONFIRMAT, > 1,2142 INFIRMAT; cod ≤ 0,7371, R2 ≤ 0,4134); configurarea diferă de cea a S38 doar prin nume, cale, etichetă și antet ✓. Sfârșit estimat ~01:25; verdictul îl verific la 02:15. S50 după S45, mâine în fereastra de zi.
- stare anterioară: **aprobat** (centrul de comandă, 29 oct 08:25, prin delegarea lui Adrian din 26 oct 17:45; pre-înregistrare ca la S38). **Doar noaptea; dacă Adrian e la workstation pentru fereastra OS/GPU (C-36), antrenarea se oprește întâi și nu pornește cât durează fereastra.**
  (inițial: propus — necesită Adrian, supraveghetor, 29 oct 02:15)
- tip: placă (~6 ore de antrenare + examene, ~7 ore în total)
- fereastră: oricând placa e liberă (de preferat noaptea), după „da”
- de ce: singura linie care a crescut sigur în ultimele zile: S38 (#441 → #459) a dat −0,017 pe română curat, cu cod și povești mai bune. Pe E3 toate încercările
  din granițe s-au închis (S42, S44); placa altfel stă liberă. Continuarea a ce merge.
- ce ar face (după „da”): `config/conv_w2_reteta_A_cont2.toml` = copie a `config/conv_w2_reteta_A_cont.toml` (cea de la S38), linie nouă `w2_reteta_A_cont2`,
  `--ore 6 --porneste-din 459`, același amestec de date, nimic descărcat. Pre-înregistrare urcată înainte: **CONFIRMAT** dacă română curat ≤ **1,2112**
  (−0,005 față de #459; pragul e mai mic decât la S38 fiindcă a doua noapte aduce de obicei mai puțin), fără regresie > 0,005 la cod curat (0,7321) și R2 (0,4084);
  **INFIRMAT** dacă > 1,2142; între ele NECLAR. Examenele: `unelte/examen_validari_ws.py` pe ultimul model și pe #459 în aceeași rulare. Modelul nu intră în interfață
  și nu înlocuiește #459 în OS fără alt „da”. Placa sub 7.000 MB și 83 °C. Nu atinge `kronos/`, examenul BPB, paznicul, jurnalul.
- pre-înregistrare: `docs/preinregistrari/2026-10-29_reteta_A_cont2.md`, cu pragurile de mai sus copiate exact, commit + push ÎNAINTE de pornire.
- fereastră fixată (supraveghetor, 29 oct 11:15): **noaptea 29 → 30 oct, de la 19:00**; dacă Adrian e la workstation pentru fereastra OS/GPU, întâi se oprește/așteaptă.
- aprobat de: centrul de comandă (delegarea lui Adrian din 26 oct 17:45), 29 oct 08:25; **confirmat de supraveghetor, 29 oct 11:15 — intră în granița 1**
  din REGULI_CASCADA.md (încă o rulare pe linia w2 existentă, același amestec, nimic descărcat), deci nu mai așteaptă alt „da”.
- raport: docs/rapoarte/2026-10-29_2334_S45_oprit_cadere.md

### S46a — Kronos-Cod etapa 1b: modul `complet` al uneltei de descărcare + teste, FĂRĂ rețea (doar procesor)
- stare: gata (executant, 29 oct 05:48, e638b01: `descarca.py complet` — 39 de depozite (rândurile 3–6, FreeBSD pe antet SPDX BSD, fără contrib/gnu) + PyPI top 30.000 + toate crate-urile din dump; reluare, `--limita-ore`, 10 erori de rețea la rând → oprire; pilotul identic (amprentă + rezumatul real refăcut identic); 13 teste noi fără rețea; 1071 teste trec, 1 sărit; nimic descărcat; comanda pentru S46 în raport; estimare ~22–27 ore, 3 nopți cu `--limita-ore 10`)
- verificat de supraveghetor (29 oct 08:15): **bun** — commit-ul atinge doar `unelte/kronos_cod/descarca.py` și testele lui; pilotul dă exact aceeași ieșire (amprentă + rezumatul real refăcut identic); 1071 teste trec, 1 sărit; nimic descărcat. S46 poate porni imediat după „da”.
- stare anterioară: in_lucru (executant, 29 oct 05:30); înainte: aprobat (supraveghetor, 29 oct 05:15)
- tip: procesor (fără placă, fără rețea)
- fereastră: oricând (nu încurcă placa); o singură sarcină odată
- durată maximă: ~2 ore
- de ce: pilotul S43 a ieșit bun (verificat mai sus), dar `unelte/kronos_cod/descarca.py` are doar modurile `pilot` și `rezumat`. Ca descărcarea întreagă (S46)
  să poată porni imediat după „da”-ul lui Adrian, unealta trebuie să existe și să fie testată dinainte. Granița 5 din REGULI_CASCADA.md. **Aici nu se descarcă nimic.**
- ce faci:
  1. În `unelte/kronos_cod/descarca.py` adaugi modul `complet`, care folosește **aceleași** filtre, licențe, data-limită 29 iunie 2021, ritm (crates ≤ 1 cerere/s,
     PyPI ≤ 5 cereri/s), User-Agent, arhive doar în memorie și oprirea sub 40 GB liberi ca modul `pilot` (nu le copiezi: le refolosești). Sursele = toate cele 6
     din `docs/kronos_cod/SURSE.md`, exact cum sunt scrise acolo: PyPI top **30.000** (`hugovk/top-pypi-packages`), crates.io din dump-ul public (`db-dump.tar.gz`;
     ultima versiune dinainte de dată), depozitele Git din rândurile 3, 4, 6 la un tag dinainte de dată, FreeBSD `release/13.0.0` doar fișierele cu antet BSD,
     fără `contrib/` și `gnu/`. Ieșirea în `lucru/kronos_cod/complet/` (nimic din `lucru/` în Git). Implicit `--iesire lucru/kronos_cod/complet`.
  2. **Reluarea e obligatorie** (descărcarea ține 2–3 nopți): după o oprire (rețea, repornire, Ctrl+C), aceeași comandă continuă de unde a rămas, fără să
     dubleze nimic; deduplicarea (exactă + aproape-duplicat) e globală, peste toate sursele, în ordinea din SURSE.md (depozitele mari întâi, apoi PyPI, apoi crates).
  3. Opțiunea `--limita-ore N` (oprire curată după N ore, cu rezumatul scris), ca descărcarea să poată fi împărțită pe nopți.
  4. Rezumatul JSON la fel ca la pilot (GB brut → curat, fișiere, simboluri, fiecare filtru, respinse pe motive), plus pe sursă.
  5. Teste noi în `teste/test_kronos_cod_descarca.py`, **fără rețea** (orice conexiune face testul să pice): reluarea fără dubluri, deduplicarea între surse,
     filtrul FreeBSD pe antet + dosarele aruncate, `--limita-ore` (timp simulat), oprirea sub 40 GB, că `pilot` dă exact aceleași rezultate ca înainte.
  6. `python -m pytest`: toate trec. Commit + push. Raport `docs/rapoarte/2026-10-29_<ora>_S46a_unealta_complet.md` cu **comanda exactă** pentru S46
     și estimarea de timp/spațiu. **Nu pornești descărcarea.**
- Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, `docs/kronos_cod/EXAMEN.md`, examenul de cod ascuns, `unelte/kronos_cod/cutie.py`,
  `lucru/kronos_cod/pilot/`. Nimic instalat (dacă îți lipsește o bibliotecă, te oprești și scrii asta).
- Dacă un pas pică de 2 ori la rând cu aceeași eroare: te oprești, stare `oprit`, scrii eroarea în raport.
- pre-înregistrare: nu e nevoie (nu se antrenează și nu se măsoară nimic)
- aprobat de: supraveghetor, 29 oct 05:15 (granița 5)
- raport: docs/rapoarte/2026-10-29_0548_S46a_unealta_complet.md

### S46 — Kronos-Cod etapa 1b: descărcarea întreagă (procesor + rețea, ~15–25 de ore, 2–3 nopți)
- stare: gata (executant, 31 oct 09:03: bucata 2 01:59–08:37, cod 0, `terminat`: true; total cod curat 3,87 GB, ~1,10 mld simboluri, 494.973 fișiere; 1,82 GB trași în bucata 2; C: 61 GB liberi; 1119 teste trec, 1 sărit)
- stare anterioară: in_lucru — bucata 2 (executant, 31 oct 02:00; S51 e `gata` de la 01:33; C: 62 GB liberi la pornire)
- stare anterioară: aprobat — bucata 2 (executant, 30 oct 11:03: bucata 1 00:29–10:29, cod 0, oprită curat la 10 ore, `terminat`: false; 15,55 GB trași, cod curat 3,73 GB, ~1,07 mld simboluri; C: 68,9 GB liberi; 1113 teste trec, 1 sărit)
- fereastră pentru bucățile următoare: noapte („o dată pe noapte”, din comanda exactă) — executant, 30 oct 11:03
- **ordinea (supraveghetor, 30 oct 11:15): în noaptea 30→31, bucata 2 pornește DOAR după ce S51 e `gata` sau `oprit`** (S51 are întâietate la 19:00, fiindcă folosește placa; descărcarea nu). Pornirea bucății poate fi oricând între 19:00 și 07:00; poate continua după 07:00 (fără placă). Excepție: dacă S51 nu a pornit până la 00:00, bucata 2 pornește la prima verificare. Aceeași regulă în nopțile următoare cât timp există o sarcină de placă `aprobat` pentru noapte.
- stare anterioară: in_lucru (executant, 30 oct 00:30 — prima bucată, `--limita-ore 10`; S45 e `oprit`, deci nimic altceva în lucru)
- stare anterioară: **aprobat** (Adrian, 29 oct 21:46, scris în conversația cu centrul de comandă: „da s46”; comanda în hub C-43)
- stare anterioară: oprit (executant, 29 oct 08:34)
- motiv: cere aprobarea lui Adrian: descărcare — la „aprobat de:” scrie „—” (nu „Adrian”), iar aprobarea e doar a centrului de comandă, prin delegare; regula descărcărilor (varianta b, 19 oct) cere „aprobat de: Adrian” pe sarcină. Nimic descărcat.
- notă supraveghetor (29 oct 11:15): oprirea e corectă. Supraveghetorul nu are voie să aprobe descărcări (REGULI_CASCADA.md), deci S46 așteaptă un „da” al lui Adrian
  scris anume pentru descărcare (de ex. o comandă în hub „da S46”), apoi pe sarcină: „aprobat de: Adrian, <data>” și starea `aprobat`.
- stare anterioară: **aprobat** (centrul de comandă, 29 oct 08:25, prin delegarea lui Adrian din 26 oct 17:45: aceleași reguli ca pilotul — data-limită 29 iunie 2021, fără surse cu cont, licențe permisive, proveniență pe fișier). Tokenizerul pe cod rămâne pentru un „da” separat, după verificarea descărcării.
  (inițial: propus — necesită Adrian, supraveghetor, 29 oct 05:15)
- tip: procesor + rețea (fără placă); se poate rula și cât e ceva pe placă
- fereastră: S46a e gata și verificat (29 oct 08:15) → doar după „da”-ul lui Adrian
- comanda exactă (din raportul S46a), o dată pe noapte până când `lucru/kronos_cod/complet/rezumat.json` are `"terminat": true`:
  `.venv/Scripts/python -X utf8 unelte/cascada.py porneste S46 -- .venv/Scripts/python -X utf8 unelte/kronos_cod/descarca.py complet --limita-ore 10`
  (estimare S46a: ~22–27 de ore, 3 nopți; C: ar rămâne ~50–62 GB liberi)
- ce ar face: comanda din raportul S46a (modul `complet`), pe bucăți cu `--limita-ore`; ~10–22 GB cod curat pe disc (C: ar rămâne ~50–63 GB liberi;
  oprire automată sub 40 GB), ~3–6 mld simboluri estimate, doar sursele fără cont, data-limită 29 iunie 2021. Raport după fiecare bucată. Tokenizerul pe cod
  NU se antrenează (al doilea „da”, separat).
- aprobat de: Adrian, 29 oct 2026 21:46 („da s46”)
- notă supraveghetor (29 oct 21:50): verificat — „da”-ul e al lui Adrian, scris anume (C-43 în hub), deci regula descărcărilor e îndeplinită. Pornește la prima verificare a cozii, în paralel cu S45. Dacă o bucată se oprește de 2 ori cu aceeași eroare: `oprit` + raport.
- notă supraveghetor (29 oct 23:15): executantul ia sarcinile pe rând (instrucțiunea lui fixă), deci S46 pornește la prima verificare după ce S45 e `gata` (~02:00). Rămâne `aprobat`.
- raport: docs/rapoarte/2026-10-29_0834_S46_oprit_aprobare.md
- raport: docs/rapoarte/2026-10-29_2259_S46_nepornit_S45_in_lucru.md
- raport: docs/rapoarte/2026-10-30_1103_S46_bucata1.md (bucata 1)
- raport: docs/rapoarte/2026-10-31_0903_S46_gata.md (bucata 2, gata)
- verificat de supraveghetor (31 oct 11:15): **gata, corect.** `terminat`: true, cod 0, tot în regulă (licențe, data-limită, 61 GB liberi). Rezultatul: **3,87 GB cod curat, ~1,10 mld simboluri** — sub estimarea de 3–6 mld (crates respinse mai ales pentru lipsa fișierului de licență; lista PyPI de la sursă are 15.000 de pachete, nu 30.000). Scăderea pe surse față de bucata 1 e deduplicarea globală, cerută. Tokenizerul pe cod și eventuale surse în plus: doar cu „da”-ul lui Adrian.

### S47 — CCM (Cyber-Compute-Module), etapa 1: profilul timpului + bancul de măsurare + variantele de bază pe procesor (doar procesor)
- stare: gata (executant, 29 oct 12:05: măsurarea 11:08–11:39, cod 0; toate cele 9 combinații acceptate (simboluri identice, |Δ logit| ≤ 3,3·10⁻⁶); cea mai rapidă `referinta` cu 1 fir: 2,47 s, 31 simb/s, 1,37× față de toate firele; `transpus` fără câștig, `la_pas` 9–20× mai lentă (desfacerea 86 %); înmulțirile ~73 % din timp; 1080 teste trec, 1 sărit)
- stare anterioară: in_lucru (executant, 29 oct 10:30; codul + 9 teste în e9c20a1, 1080 teste trec; măsurarea pornită prin cascadă 11:17, procesul 18752, ~35 min)
- stare anterioară: **aprobat** (centrul de comandă, 29 oct 10:20, ideea lui Adrian, prin delegarea din 26 oct 17:45). Planul: `docs/CCM_plan.md`.
- tip: procesor (fără placă, fără rețea); fereastră: oricând, o singură sarcină odată; durată maximă: ~3 ore
- ce faci:
  1. Citești `docs/CCM_plan.md`. Profil pe #459 (`lucru/export/kronos_459_q8_0.kgr`) cu `unelte/inferenta_bruta.py`: timpul pe operații pentru
     `Ana are mere.` → 64 de simboluri (încărcare, desfacere Q8_0, înmulțiri pe straturi, atenție, normalizare, softmax, eșantionare).
  2. `module/calcul/` nou: `banc.py` (rulează o variantă, verifică față de referință: simboluri identice pe vectorii KGR1 + toleranța logit-urilor scrisă
     înainte în raport; măsoară median + împrăștiere pe ≥ 5 repetări, timp complet), `variante/` cu 2–4 variante pe procesor pentru înmulțire
     (de ex. desfacere o dată vs. la fiecare pas, fire numpy 1/toate, blocuri) — doar cu ce e deja instalat.
  3. Teste noi în `teste/` (fără rețea, pe modele mici sintetice): o variantă greșită e respinsă, o variantă corectă e acceptată, măsurarea e repetabilă.
  4. `python -m pytest` verde; commit + push; raport `docs/rapoarte/2026-10-29_<ora>_S47_ccm_profil.md` cu tabelul de cifre (simb/s, ms pe operație).
- Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, `module/inferenta_kgr1.py`, `unelte/inferenta_bruta.py` (doar le folosești). Nimic instalat.
- Dacă un pas pică de 2 ori la rând cu aceeași eroare: stare `oprit`, eroarea în raport.
- aprobat de: centrul de comandă (delegare), 29 oct 10:20
- raport: docs/rapoarte/2026-10-29_1037_S47_ccm_profil.md
- verificat de supraveghetor (29 oct 14:35): **bun** — regulile urcate înainte de măsurare (e9c20a1, 10:38; măsurarea 11:08–11:39); cifrele se adună (1,37×; înmulțirile 73,2 % din timp);
  doar `module/calcul/`, testul lui, raportul și coada atinse; 1080 teste trec, 1 sărit. Rezultat: pe workstation cea mai rapidă e `referinta` cu 1 fir (2,47 s, 31 simb/s).

### S48 — CCM etapa 2: modulul `inferenta_ccm` pe portul `inferenta` + reglajul salvat + rezerva (doar procesor)
- stare: gata (executant, 29 oct 15:10: `module/inferenta_ccm.py` + `module/calcul/reglaj.py` + `fire.py`; trece `teste_contracte/` (cu reglaj și cu rezerva);
  reglajul `lucru/ccm/reglaj-desktop-br58s2c.json` = referinta, 1 fir, #459 sha e80618b4…; aceleași simboluri ca `inferenta_kgr1`;
  pe #459 CCM 2,89 s / 28,3 simb/s față de 3,54 s / 20,3 → 1,22× total, 1,39× generare; ATENȚIE: la primul răspuns într-un proces nou
  referința face ~40 simb/s (mai rapidă decât CCM); 1099 teste trec, 1 sărit)
- raport: docs/rapoarte/2026-10-29_1510_S48_inferenta_ccm.md
- verificat de supraveghetor (29 oct 17:30): **bun** — trece `teste_contracte/` (cu reglaj și cu rezerva); simboluri identice cu `inferenta_kgr1`; cifrele se adună (3,544/2,888 = 1,23× total, 28,3/20,3 = 1,39× simb/s); doar `module/`, `teste/`, `teste_contracte/`, `docs/CCM_plan.md`, raportul și coada atinse, nimic în `kronos/`; 1099 teste trec, 1 sărit. Observația „referința e rapidă doar la primul răspuns” → S50.
- (istoric) stare: **aprobat** (centrul de comandă, 29 oct 10:20), după S47 verificat de supraveghetor — **S47 verificat 29 oct 14:35: poate porni acum** (doar procesor; nu încurcă S45 de la 19:00)
- ce faci: `module/inferenta_ccm.py` (MANIFEST pe portul `inferenta`) folosește variantele alese din `lucru/ccm/reglaj-<calculator>.json`;
  fără reglaj sau la orice nepotrivire → calea `inferenta_kgr1`. Îl adaugi în lista `MODULE` din `teste_contracte/` și trebuie să treacă.
  Formatul reglajului descris în `docs/CCM_plan.md` (pentru OS, mai târziu). Raport cu viteza față de referință pe workstation. Fără schimbări în `kronos/`.

### S49 — CCM etapa 3: varianta pe placa video sub Windows (PyTorch, fp32/fp16/bf16) și alegerea procesor/placă după măsurători
- stare: gata (executant, 29 oct 15:50: `module/calcul/variante/placa.py` (fp32/fp16/bf16), `banc placa`, reglajul cu „placa” + „alegere”, `inferenta_ccm` 0.2.0 cu `placa=False` implicit;
  măsurarea 15:41–15:44 cod 0 (prima pornire 15:39 căzută înainte să scrie ceva, reparată, în raport); **placa_fp32 acceptată** (Δ 1,5·10⁻⁴), 1,686 s vs procesor 2,009 s → 1,19×, alegere = placa;
  fp16 respinsă (Δ 0,028), bf16 respinsă (alte simboluri); placa max 1.679 MB, 36 °C; pornirea CUDA +3 s; ATENȚIE: „toate firele” rapid doar la primul răspuns → decizie la supraveghetor; 1113 teste trec, 1 sărit)
- raport: docs/rapoarte/2026-10-29_1538_S49_ccm_placa.md
- verificat de supraveghetor (29 oct 17:30): **bun** — regulile măsurării urcate înainte (b922b58 15:38; prima pornire 15:39 a căzut fără să scrie nimic, reparată în dbdea59, măsurarea 15:41–15:44); cifrele se adună (2,009/1,686 = 1,19×; 52,1/40,6 = 1,28× simb/s); fp16/bf16 respinse corect (toleranță, bf16 și alte simboluri); placa max 1.679 MB, 36 °C (sub 7.000 MB / 83 °C); `placa=False` implicit, interfața neatinsă; 1113 teste trec, 1 sărit. **Decizia la punctul 3: varianta (a)** — S50 (bancul măsoară și răspunsul al doilea din același motor; alegerea pe procesor se face pe acela). Reglajul de acum (procesor = toate firele) rămâne până la S50; nu-l schimbăm de mână. Folosirea plăcii în interfață (`placa=True`) rămâne decizia lui Adrian.
- (istoric) stare: **aprobat** (centrul de comandă, 29 oct 10:20), după S48; **doar cu placa liberă** (nu în timpul antrenării, nu în ferestrele OS/GPU cu Adrian), VRAM < 7 GB, ~1 oră pe placă
- verificarea simbolurilor față de referință e obligatorie și pentru placă (fp16/bf16 pot schimba simbolurile → se notează și se respinge varianta dacă diferă).

### S50 — CCM etapa 4: bancul măsoară „rece” (primul răspuns dintr-un motor nou) și „cald” (răspunsurile următoare din același motor); alegerea pe procesor după „cald” (doar procesor)
- stare: gata (executant, 30 oct 11:47: bancul rece/cald + alegerea după cald + 6 teste noi; măsurarea `banc placa` 11:41–11:43 cod 0, o singură pornire;
  procesor: **referinta / 1 fir** cald 2,300 s (28,5 simb/s) vs toate firele 3,137 s (20,5) → 1,36×; placa_fp32 cald 1,247 s → alegere = placa (1,84×), `placa=False` rămâne implicit;
  fp16/bf16 respinse la fiecare răspuns; ATENȚIE: efectul „toate firele rapid la primul răspuns” (40 simb/s în S49) NU a apărut azi, nici rece;
  reglaj nou din s50.json, cel vechi păstrat ca `_s49`; placa max 1.525 MB, 34 °C; 1119 teste trec, 1 sărit)
- (istoric) stare: **aprobat** (supraveghetor, 29 oct 17:30 — granițele 2 și 5: măsurători + unealtă în `module/calcul/` și teste, fără `kronos/`, fără examen, nimic descărcat/instalat)
- tip: procesor (fără placă, fără rețea); durată maximă ~2 ore
- fereastră: **doar după ce S45 s-a terminat și cât timp S46 nu rulează** (supraveghetor, 29 oct 21:50; descărcarea încarcă procesorul) (nu în timpul antrenării de noapte: antrenarea încarcă procesorul și ar strica măsurătorile); cel mai devreme 30 oct dimineață, în fereastra de zi.
- de ce: S48 și S49 au arătat că pe Windows referința cu toate firele e rapidă doar la primul calcul dintr-un motor nou (~40 simb/s), apoi cade la ~20–22; cu 1 fir rămâne constant ~28–31. Bancul face un motor nou la fiecare repetare, deci vede doar cazul „rece” și a ales în S49 „toate firele” pentru procesor — greșit pentru interfață și pentru OS, care țin modelul deschis.
- ce faci:
  1. `module/calcul/banc.py`: pentru fiecare variantă (procesor și, la comanda `placa`, placă) măsori în același proces și același motor: răspunsul 1 („rece”) și răspunsurile 2–6 („cald”, median + împrăștiere), 64 de simboluri, „Ana are mere.”, #459 Q8_0. Verificarea simbolurilor față de referință ca la S47/S49 (aceleași simboluri, |Δ logit| ≤ 0,001), la fiecare răspuns.
  2. `module/calcul/reglaj.py`: alegerea pe procesor (și alegerea procesor/placă) se face pe timpul **„cald”** (median pe răspunsurile 2–6, fără încărcare); timpul „rece” și pornirea se scriu în reglaj doar ca informație. Un reglaj vechi (fără câmpurile noi) rămâne citibil; formatul descris în `docs/CCM_plan.md`.
  3. Teste noi (fără rețea, modele mici sintetice, fără placă): „cald” se măsoară în același motor; alegerea folosește „cald”; reglajul vechi rămâne bun.
  4. Regulile măsurării scrise în raport și urcate (commit + push) ÎNAINTE de măsurare; apoi o singură măsurare oficială: `banc placa --iesire lucru/ccm/s50.json` (dacă placa e liberă; altfel doar procesorul și scrii de ce). Reglajul nou din `s50.json`; cel de acum păstrat întâi ca `lucru/ccm/reglaj-desktop-br58s2c_s49.json`.
  5. `python -m pytest` verde; commit + push; raport `docs/rapoarte/2026-10-30_<ora>_S50_ccm_cald_rece.md` cu tabelul rece/cald pe fiecare variantă și ce s-a ales.
- Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, interfața (`placa` rămâne `False` implicit). Nimic instalat, nimic descărcat. Placa sub 7.000 MB și 83 °C.
- Dacă un pas pică de 2 ori la rând cu aceeași eroare: stare `oprit`, eroarea în raport.
- aprobat de: supraveghetor, 29 oct 17:30 (granițele 2 și 5 din REGULI_CASCADA.md)
- raport: docs/rapoarte/2026-10-30_1140_S50_ccm_cald_rece.md
- verificat de supraveghetor (30 oct 14:15): **bun** — reguli urcate înainte (54895b9 11:38), o singură măsurare (11:41–11:43, cod 0); medianele calde refăcute (2,300 / 3,137 / 1,247 s), 1,36× și 1,84× ✓; fp16/bf16 respinse corect; placa ≤ 1.525 MB, 34 °C; 1119 teste trec. Mărunțiș: 28,5 simb/s la 1 fir ar trebui 27,8 (64/2,300); alegerea nu se schimbă. `placa=True` în interfață rămâne decizia lui Adrian.

### S51 — Repetarea S45: încă o noapte pe linia w2 cu rețeta A, din #459, pe linie nouă `w2_reteta_A_cont3` (placa)
- stare: gata (executant, 31 oct 01:33) — CONFIRMAT: #477 română curat 1,2097 (#459 1,2162), cod curat 0,7270, R2 0,4060; fără cădere (19:00:09–01:23:26, cod 0); placa max 6.002 MB / 64 °C; 1119 teste trec
- stare veche: in_lucru (executant, 30 oct 19:00)
- verificat de supraveghetor (30 oct 20:15): pre-înregistrarea `2026-10-30_reteta_A_cont3.md` urcată la 18:59:58, înainte de pornire, cu aceleași praguri ca S45; configurarea = copia S45 cu doar `nume`, `cale_stare`, `eticheta` și antetul schimbate ✓. Verdictul la 02:15.
- (istoric) stare: **aprobat** (supraveghetor, 30 oct 02:15 — granița 1: încă o rulare pe linia w2 existentă, același amestec, nimic descărcat; e aceeași sarcină ca S45, care a căzut fără verdict)
- tip: placă (~6 ore de antrenare + examene, ~7 ore în total)
- fereastră: **noaptea; pornește doar dacă poate începe între 19:00 și 00:00** (ca să se termine cu examene înainte de 07:00). **Ordinea nouă (supraveghetor, 30 oct 11:15): S51 pornește la 19:00 în seara asta, ÎNAINTEA bucății 2 a S46** (care așteaptă să se termine S51). S50 trebuie să fie terminat înainte.
- fereastră veche (30 oct 02:15): după S50 și după bucata 2 a S46. **Dacă Adrian e la workstation pentru o fereastră OS/GPU, nu pornește cât durează fereastra.**
- de ce: S45 a căzut la ora 4/6 (23:09, fără eroare, fără cod de ieșire), deci întrebarea „mai aduce încă o noapte din #459 un câștig real pe română?” n-are răspuns. Continuarea a ce merge (S38 CONFIRMAT, #441 → #459).
- ce faci:
  1. *(FĂCUT deja în raportul de dimineață, 30 oct 06:46 — doar verifici că `2026-10-29_reteta_A_cont2.md` e închisă și treci la pasul 2.)* **Întâi** închizi pre-înregistrarea veche: `python unelte/preinregistrare.py --inchide reteta_A_cont2` cu „Ce a ieșit: întreruptă la 23:09:36, ora 4/6, orele 1–3 #469 0,4185 / #470 0,4167 / #471 0,4150 (R2); examenele n-au rulat” și „Verdictul: fără verdict (întreruptă); se repetă ca S51”.
  2. `config/conv_w2_reteta_A_cont3.toml` = copie a `config/conv_w2_reteta_A_cont2.toml` (S45), cu doar `nume = "w2_reteta_A_cont3"`, `cale_stare`, eticheta și antetul schimbate (diff-ul în raport). Linia `lucru/w2_reteta_A_cont3/` trebuie să NU existe înainte de pornire (verifici și scrii în pre-înregistrare), ca `--porneste-din 459` să fie folosit (capcana S42).
  3. Pre-înregistrarea `docs/preinregistrari/2026-10-30_reteta_A_cont3.md`, cu **aceleași praguri ca S45, copiate exact**: **CONFIRMAT** dacă română curat ≤ **1,2112**, fără regresie > 0,005 la cod curat (≤ **0,7371**) și R2 (≤ **0,4134**); **INFIRMAT** dacă > **1,2142**; între ele NECLAR. Reperele #459: română 1,2162, cod 0,7321, R2 0,4084 (re-măsurate în aceeași rulare). Scrii că e repetarea S45 (căzută). Commit + push ÎNAINTE de pornire.
  4. Pornești prin cascadă, lanțul ca la S45 (`lucru/cascada/S51_proba/s51.py`): `python unelte/antrenare_lunga.py --config config/conv_w2_reteta_A_cont3.toml --ore 6 --porneste-din 459`, apoi în același proces `unelte/examen_validari_ws.py --linie w2_reteta_A_cont3` și `unelte/examen_validari_ws.py --experiment 459`.
  5. La sfârșit: închizi pre-înregistrarea cu cifrele, `python -m pytest` verde, commit + push, raport `docs/rapoarte/2026-10-3x_<ora>_S51_reteta_A_cont3.md` (tabelul pe ore, examenele, verdictul față de praguri, placa max MB/°C).
- Dacă procesul cade din nou fără eroare: `oprit`, raport, **nu** reporni singur; scrie ora exactă a căderii (ajută la aflarea cauzei).
- Modelul nu intră în interfață și nu înlocuiește #459 în OS fără alt „da”. Placa sub 7.000 MB și 83 °C. Nu atinge `kronos/`, examenul BPB, paznicul, jurnalul.
- pre-înregistrare: docs/preinregistrari/2026-10-30_reteta_A_cont3.md (de scris înainte de pornire)
- aprobat de: supraveghetor, 30 oct 02:15 (granița 1 din REGULI_CASCADA.md)
- raport: docs/rapoarte/2026-10-31_0133_S51_reteta_A_cont3.md
- verificat de supraveghetor, 31 oct 02:15: pre-înregistrarea (5344b50, 18:59:58) înaintea pornirii (19:00:09) ✓; 1,2097 ≤ 1,2112, 0,7270 ≤ 0,7371, 0,4060 ≤ 0,4134 → **CONFIRMAT** ✓ (la limită, marjă 0,0015). #477 nu intră în interfață/OS fără „da”-ul lui Adrian.

### S52 — Diagnostic: de ce s-a repornit workstation-ul pe 29 oct ~23:10 (doar citire, procesor, ~10 min)
- stare: oprit (executant, 30 oct 15:33) — placa din S45 normală până la 23:09:36 (64 °C, 6.116 MB); niciun minidump găsit; jurnalele Windows necitite
- motiv: cere aprobarea lui Adrian: citirea jurnalelor Windows (`Get-WinEvent`, `wevtutil`) e blocată de permisiunile executantului; comanda pentru Adrian e în raport
- stare anterioară: **aprobat** (centrul de comandă, 30 oct 15:00, la cererea lui Adrian: „poți să ceri un raport complet”; delegarea din 26 oct 17:45). Adrian crede că a fost o pană de curent.
- tip: procesor, **doar citire** (nu schimbă nicio setare Windows, nu instalează nimic); fereastră: imediat ce e liber un loc în coadă, poate rula în paralel cu S46; durată ~10 min
- ce faci (PowerShell, fără drepturi de administrator dacă se poate; dacă un jurnal cere administrator, notezi asta și treci mai departe):
  1. Evenimentele din `System` între 29 oct 22:30 și 23:30: `Get-WinEvent -FilterHashtable @{LogName='System'; StartTime='2026-10-29 22:30'; EndTime='2026-10-29 23:30'}`
     → toate cu nivel Critic/Eroare/Avertisment + ID-urile cheie: **41** (Kernel-Power: oprire fără închidere curată = de obicei curent/blocare),
     **6008** (oprire neașteptată), **1074** (repornire cerută de un program/Windows Update, cu numele lui), **1076**, **6005/6006** (pornire/oprire jurnal),
     **19/20/43** (WindowsUpdateClient), **1001** (BugCheck = ecran albastru, cu codul), WHEA-Logger (erori hardware).
  2. `Get-WinEvent -LogName Setup` și istoricul Windows Update din 29–30 oct (`Get-HotFix` + `Microsoft-Windows-WindowsUpdateClient/Operational` dacă există).
  3. Dacă există `C:\Windows\Minidump\*.dmp` din 29–30 oct: doar numele, data, mărimea (nu le deschide).
  4. Ultimele rânduri din jurnalul S45 (`lucru/`) înainte de 23:09: temperatura și memoria plăcii, ca să excludem supraîncălzirea.
  5. Setările care pot reporni noaptea, **doar citite**: orele active Windows Update (`HKLM:\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings` ActiveHoursStart/End), planul de alimentare.
  6. Raport `docs/rapoarte/2026-10-30_<ora>_S52_repornire.md`, în română simplă pentru Adrian: **cauza cea mai probabilă** (curent / Windows Update / ecran albastru / hardware)
     cu dovezile (ID-urile și orele), ce s-ar putea face (de ex. UPS, ore active) — **fără să schimbi nimic**; commit + push.
- Nu atingi `kronos/`, examenul, paznicul, jurnalul, S46 care rulează. Nimic instalat, nicio setare schimbată.
- aprobat de: centrul de comandă (delegare, diagnostic doar citire), 30 oct 15:00
- notă supraveghetor (30 oct 17:15): oprirea verificată, corectă. Rămâne `oprit` până la răspunsul lui Adrian (fie rulează el comanda din raport, fie aprobă citirea jurnalelor Windows de către executant). Nu blochează S51.
- raport: docs/rapoarte/2026-10-30_1533_S52_repornire.md

### S53 — Kronos-Cod: verificarea scurgerii examenului de cod în datele descărcate (doar procesor, fără rețea, fără placă)
- stare: gata (executant, 31 oct 11:38) — DE CURĂȚAT: 0/200 cu soluția întreagă, 87/200 cu suprapuneri de 13 (cea mai lungă 26); de exclus 3.821 fișiere curate = 3,06 % (118 MB), lista în lucru/kronos_cod/scurgere/; SHA set ascuns neschimbat; 1126 teste trec, 1 sărit
- raport: docs/rapoarte/2026-10-31_1138_S53_scurgere.md
- tip: procesor (fără placă, fără rețea); poate rula în paralel cu orice sarcină de placă
- fereastră: oricând (de preferat ziua, 31 oct)
- durată maximă: 2 ore
- de ce: înainte de orice tokenizer sau antrenare pe cod (care cer „da”-ul lui Adrian) trebuie să știm că setul ascuns din S41 (200 de probleme) nu apare în cele 3,87 GB de cod curat din S46. Altfel scorul pass@k de mai târziu n-ar însemna nimic.
- ce faci:
  1. O unealtă nouă `unelte/kronos_cod/scurgere.py` (+ teste fără rețea pe date mici făcute în test): pentru fiecare problemă din `lucru/kronos_cod/examen_ascuns/` ia enunțul, numele funcției, testele și soluția de referință; normalizează (litere mici, spații comprimate, fără comentarii) și caută în tot codul curat din `lucru/kronos_cod/complet/` **suprapuneri de 13 simboluri la rând** (n-grame de cuvinte/simboluri Python) și potriviri exacte ale corpului soluției de referință (după normalizare).
  2. Rulezi o singură dată pe tot setul. Pentru fiecare problemă: numărul de fișiere cu suprapunere, cea mai lungă suprapunere, dacă soluția întreagă apare exact.
  3. Scrii lista fișierelor atinse în `lucru/kronos_cod/scurgere/fisiere_de_exclus.txt` (NU în Git). **Nu ștergi și nu muți nimic din date** (ștergerea cere Adrian); excluderea se va aplica la pasul tokenizerului.
  4. Raport `docs/rapoarte/2026-10-31_<ora>_S53_scurgere.md`, în română simplă: câte probleme din 200 au vreo suprapunere, câte au soluția întreagă în date, câte fișiere/ce parte din cei 3,87 GB ar ieși la excludere, și ce înseamnă (praguri scrise acum, înainte: **curat** = 0 probleme cu soluția întreagă și ≤ 10 probleme cu suprapuneri de 13; **de curățat** = altfel, cu excluderea fișierelor listate; **examenul compromis** = > 50 de probleme cu soluția întreagă → propui în raport un set ascuns nou, nu-l faci). **În Git nu pui textul niciunei probleme din setul ascuns** — doar numere și numele șabloanelor.
  5. `python -m pytest`: toate trec. Commit + push.
- Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, modelele, setul ascuns (doar îl citești; suma SHA-256 trebuie să rămână `90fc64cd…3749` — verifici la început și la sfârșit). Nimic descărcat, nimic instalat.
- Dacă un pas pică de 2 ori la rând cu aceeași eroare: stare `oprit`, eroarea în raport.
- pre-înregistrare: nu e antrenare; pragurile sunt scrise mai sus, înainte de rulare
- aprobat de: supraveghetor, 31 oct 2026 11:15 (granițele 2 și 3: examene/verificări și curățarea datelor deja descărcate și aprobate; unealtă nouă în `unelte/`)
- verificat de supraveghetor (31 oct 14:15): **gata, corect — DE CURĂȚAT.** 0/200 soluții întregi (prag 0), 87/200 cu suprapuneri de 13 (prag ≤ 10 pentru „curat”), 0 > 50 deci nu e compromis; suma setului ascuns neschimbată; 3,06 % de exclus. Lista se aplică întreagă la S55.

### S54 — C-44: #477 îl înlocuiește pe #459 (modelul în uz + pachetul KGR1 pentru OS), #459 păstrat ca rezervă (doar procesor)
- stare: gata (executant, 31 oct 14:08) — #477 exportat (110.859.040 octeți, SHA-256 bcbe8187…3963), MODEL.md rescris cu rezerva #459, modulele KGR1/CCM pe #477, reglajul CCM refăcut pe procesor (referinta, 1 fir, 27,8 simb/s; fără partea de placă); Release NEfăcut (`gh` cere aprobare, comanda în raport); 1126 teste trec, 1 sărit
- raport: docs/rapoarte/2026-10-31_1408_S54_model_477.md
- tip: procesor (fără placă: `CUDA_VISIBLE_DEVICES=-1`)
- fereastră: oricând (de preferat azi, 31 oct, înaintea S55)
- durată maximă: 2 ore; RAM cel mult ~6 GB
- de ce: Adrian a spus „da #477” (C-44): #477 (S51 CONFIRMAT, română 1,2097 față de 1,2162) devine modelul în uz în locul lui #459, iar OS-ul (C-46) îl ia după ce `integrare/kronos/MODEL.md` din hub arată #477.
- ce faci:
  1. **Export:** `python unelte/exporta_greutati.py --experiment 477 --fel q8_0 --iesire lucru/export/kronos_477_q8_0.kgr` (rămâne în `lucru/`, NU în Git). SHA-256 + mărimea în octeți, scrise și în `lucru/export/kronos_477_q8_0.kgr.sha256` (același format ca la #459, dacă există; altfel `<suma>  kronos_477_q8_0.kgr`). **Nu ștergi și nu suprascrii `kronos_459_q8_0.kgr`.**
  2. **Vectorii de control:** `python unelte/vectori_kgr1.py model --kgr lucru/export/kronos_477_q8_0.kgr` (ca la S39 partea B): pe cele 3 texte fixe, simbolurile textului, primele 5 simboluri greedy (numere și text) și marja cea mai mică dintre primul și al doilea logit pe pașii greedy. Vectorii modelului mic din `integrare/kronos/vectori/` rămân neschimbați (nu depind de model).
  3. **`docs/integrare_kronos/MODEL.md`** rescris pentru #477, în aceeași formă ca pentru #459: modelul (#477, linia `w2_reteta_A_cont3`, S51 CONFIRMAT, română 1,2097), arhitectura, fișierul, mărimea, SHA-256, Release-ul (eticheta `kronos-kgr1-477` sau „nefăcut: motivul” + comanda exactă pentru Adrian), tabelul cu cele 3 texte, marjele. Adaugi la final o secțiune scurtă „Rezerva: #459” cu suma și mărimea lui (din MODEL.md vechi), ca OS-ul să-l poată accepta în continuare.
  4. **Release** privat în `Adriancu91/cyberspace` (NU în hub, NU public): `gh release create kronos-kgr1-477 lucru/export/kronos_477_q8_0.kgr lucru/export/kronos_477_q8_0.kgr.sha256 --repo Adriancu91/cyberspace --title "Kronos #477 KGR1 Q8_0" --notes "<suma și mărimea>"`. Dacă `gh` cere aprobare, nu există sau nu e autentificat: **nu instalezi nimic, nu te autentifici**; scrii comanda exactă în raport și în MODEL.md și treci mai departe (o face Adrian, ca la #459).
  5. **Modelul în uz:** cauți toate locurile unde #459 / `kronos_459_q8_0.kgr` e modelul folosit implicit (de ex. `module/inferenta_kgr1.py`, `module/inferenta_ccm.py`, `module/calcul/banc.py`, `module/calcul/reglaj.py`, configurarea și scriptul interfeței `unelte/interfata_ws.ps1`) și treci pe `kronos_477_q8_0.kgr` / 477. Dacă reglajul CCM salvat e legat de suma fișierului, rulezi `python -X utf8 -m module.calcul.reglaj verifica --kgr lucru/export/kronos_477_q8_0.kgr` (și, dacă cere, reglajul nou, pe procesor). Filele interfeței care folosesc alte modele (de ex. #312, #407 pentru „Întreabă din text”) **nu le schimbi**; scrii în raport ce model folosește fiecare filă înainte și după. Dacă interfața rulează, o repornești doar prin paznicul de procese / scriptul ei, cum se face de obicei; dacă nu se poate fără aprobare, scrii în raport ce trebuie făcut.
  6. Testele care cer explicit #459 (sume, fișiere) le actualizezi doar dacă testează „modelul în uz”; cele care verifică vectorii fixați ai lui #459 rămân. `python -m pytest`: toate trec. Commit + push.
  7. Raport `docs/rapoarte/2026-10-31_<ora>_S54_model_477.md`: suma și mărimea, tabelul cu cele 3 texte, Release făcut sau comanda pentru Adrian, lista fișierelor schimbate (înainte → după), testele.
- Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, modelele (doar citire), linia de cod. Nu scrii în hub (supraveghetorul copiază `docs/integrare_kronos/MODEL.md` în `integrare/kronos/MODEL.md` din hub la trecerea următoare). Nimic descărcat, nimic instalat, nimic șters.
- Dacă un pas pică de 2 ori la rând cu aceeași eroare: stare `oprit`, eroarea în raport.
- pre-înregistrare: nu e antrenare; nu e nevoie
- aprobat de: Adrian (COMENZI.md C-44, 31 oct 2026 13:50, „da la amândouă”, prin centrul de comandă); pașii scriși de supraveghetor, 31 oct 14:15
- verificat de supraveghetor (31 oct 14:20): **gata, corect.** Mărimea 110.859.040 octeți = #459 (aceeași arhitectură) ✓; SHA-256 bcbe8187…3963 scrisă în `.sha256` ✓; `kronos_459_q8_0.kgr` neatins (e80618b4…382e) ✓; vectorii: 2 din 3 texte identice cu #459, al doilea diferă („Bacău” în loc de „Baia Mare”, firesc la alt model), marjele minime 0,026 / 0,024 / 0,016 ✓; MODEL.md cu „Rezerva: #459” ✓; doar căile implicite schimbate în 4 module, MANIFEST neschimbat ✓; reglajul CCM refăcut pe procesor (1 fir, 27,8 simb/s) ✓; 1126 teste trec ✓. Release-ul `kronos-kgr1-477` nefăcut (`gh` cere aprobare) — rămâne la Adrian, ca la #459. MODEL.md copiat în hub (`integrare/kronos/MODEL.md`) → C-44 gata, C-46 deblocat.

### S55 — C-45: Kronos-Cod, tokenizerul pe cod din descărcarea S46 (cu excluderea S53) + propunerea primei antrenări (doar procesor)
- stare: gata (executant, 31 oct 15:05) — verdict BUN: (c) 5.686/5.686 identice, (a) 3,46 octeți/simbol, +22,1 % față de w2; setul tokenizat, 1.080.537.399 simboluri; ~18 min; setul ascuns neschimbat; propunerea primei antrenări în raport (nepornită); 1132 teste trec, 1 sărit
- raport: docs/rapoarte/2026-10-31_1505_S55_tokenizer_cod.md
- verificat (supraveghetor, 31 oct 17:15): **BUN, corect** — 3,4617 ≥ 3,0; 3,4617 / 2,8344 − 1 = +22,1 % ≥ 15 %; 5.686/5.686 identice; pre-înregistrarea urcată 14:39, înainte de rulare (14:39:19), pragurile neschimbate. Propunerea primei antrenări → S57 (pregătire, aprobată) și S58 (antrenarea, la Adrian).
- tip: procesor (fără placă, fără rețea); poate rula și noaptea (placa e liberă, nu o folosește)
- fereastră: oricând, **după S54**
- durată maximă: 10 ore în total (tokenizerul ~1–2 ore; tokenizarea întregului set restul); RAM cel mult ~60 GB; te oprești dacă spațiul liber pe C: scade sub 40 GB
- de ce: Adrian a spus „da tokenizer cod” (C-45): etapa următoare din Kronos-Cod. Tokenizerul nou = linie de model nouă, aprobată de Adrian prin comanda asta. Linia română (#477, tokenizerul w2 de 16.384) rămâne separată și neatinsă.
- ce faci:
  1. **Pre-înregistrarea ÎNAINTE de antrenarea tokenizerului:** `docs/preinregistrari/2026-10-31_kronos_cod_tokenizer.md`, commit + push, apoi pornești. Scrii în ea, fără să te uiți la rezultate:
     - **datele:** `lucru/kronos_cod/complet/cod.jsonl`, doar fișierele curate, **minus toate fișierele din `lucru/kronos_cod/scurgere/fisiere_de_exclus.txt`** (lista întreagă din S53); din rest, **1 % ținut deoparte ca validare** (ales după sha256 al fișierului, de ex. primul octet al sumei < 3 → validare; regula exactă scrisă aici), nefolosit la antrenarea tokenizerului și, mai târziu, la antrenarea modelului;
     - **tokenizerul:** BPE pe octeți, **32.768 de simboluri** (încape în uint16), antrenat pe un eșantion de ~1 GB din partea de antrenare, cu amestecul pe limbaje cât e în date (scrii procentele); spațiile de indentare (4, 8, 12… spații, tab-uri) și sfârșitul de rând păstrate ca simboluri; simbolurile speciale (sfârșit de fișier etc.) numite;
     - **cum se măsoară** (pe validarea de 1 %, NU pe examenul ascuns — setul din `lucru/kronos_cod/examen_ascuns/` nu se deschide): (a) octeți pe simbol, pe tot și separat pe Python / Rust / C; (b) aceeași măsură cu tokenizerul w2 (16.384), ca reper; (c) codare → decodare identică octet cu octet pe 100 % din fișierele de validare; (d) câte simboluri are tot setul de antrenare tokenizat;
     - **pragurile: BUN** = (c) 100 % identic **și** octeți/simbol pe tot ≥ 3,0 **și** ≥ 15 % mai mulți octeți/simbol decât w2 pe aceleași fișiere; **SLAB** = (c) 100 % dar unul din celelalte două nu e atins (raportezi și propui 16.384 sau 49.152, nu le faci); **STRICAT** = (c) sub 100 % (oprești, nu tokenizezi setul).
  2. Unealtă nouă `unelte/kronos_cod/tokenizer_cod.py` (+ teste fără rețea pe texte mici făcute în test: codare/decodare identică, indentarea, simbolurile speciale, că fișierele din lista de excludere și cele de validare nu intră). Refolosești `module/tokenizer_bpe.py` (`antreneaza_din_frecvente`, `frecvente_bucati`); dacă ai nevoie de reguli de pre-tokenizare noi pentru cod, le adaugi ca variantă nouă, **fără să schimbi felul în care codează tokenizerii existenți** (un test: tokenizerul w2 dă aceleași simboluri ca înainte pe textele din `integrare/kronos/vectori/vectori.json`).
  3. Antrenezi tokenizerul o singură dată → `lucru/kronos_cod/tokenizer/bpe_cod_32768.json` (+ suma SHA-256). Faci măsurătorile din pre-înregistrare și scrii verdictul.
  4. Doar dacă verdictul e **BUN** sau **SLAB**: tokenizezi tot setul de antrenare (fără excluse, fără validare) și validarea separat, în `lucru/kronos_cod/simboluri/` (uint16, fișier cu sfârșit de fișier între fișiere + un mic `rezumat.json`: număr de simboluri pe limbaj și pe sursă). Dacă estimezi că nu încape în cele 10 ore, faci cât încape, te oprești curat cu reluare de unde ai rămas și scrii cât mai e.
  5. **Propunerea pentru prima antrenare Kronos-Cod pe placă** (o scrii, NU o pornești): în raport, secțiunea „Propunere: prima antrenare”: mărimea modelului (cu vocabularul de 32.768; ținta: sub 7.000 MB pe placă), de la zero sau nu, câte ore/nopți, câte simboluri vede, rata, ce se măsoară (pierderea pe validarea de 1 %, apoi pass@1 / pass@10 pe examenul ascuns cu `unelte/kronos_cod/examen_cod.py` și cutia), și pragurile propuse. Supraveghetorul decide la trecerea următoare dacă intră în granițe sau merge la Adrian.
  6. `python -m pytest`: toate trec. Commit + push. Raport `docs/rapoarte/2026-10-31_<ora>_S55_tokenizer_cod.md` (sau data zilei în care termini): cifrele (a)–(d), verdictul față de praguri, timpul, RAM, spațiul pe C:, propunerea de la pasul 5.
- Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, modelele, #477 și linia română, setul ascuns (suma `90fc64cd…3749` neschimbată, verifici la început și la sfârșit), datele din `lucru/kronos_cod/complet/` (doar citire; nimic șters sau mutat). Nimic descărcat, nimic instalat. Nimic din `lucru/` în Git.
- Dacă un pas pică de 2 ori la rând cu aceeași eroare: stare `oprit`, eroarea în raport.
- pre-înregistrare: docs/preinregistrari/2026-10-31_kronos_cod_tokenizer.md (scrisă și urcată ÎNAINTE de antrenarea tokenizerului)
- aprobat de: Adrian (COMENZI.md C-45, 31 oct 2026 13:50, „da la amândouă”, prin centrul de comandă); pașii și pragurile scrise de supraveghetor, 31 oct 14:15. Prima antrenare pe placă NU e aprobată aici.

### S56 — CCM: partea de placă a reglajului pentru #477 (măsurare scurtă pe placă)
- stare: gata (executant, 31 oct 15:38: măsurarea 15:29–15:33, cod 0; placa_fp32 acceptată (|Δ logit| 0,000155), cald 1,226 s / 52,2 simb/s, 1,75× față de referinta 1 fir 2,143 s; fp16/bf16 respinse; reglajul nou `alegere: placa`, `verifica --placa` → folosit: true; vechiul păstrat ca `_s54`; placa max 1.544 MB / 32 °C; 1132 teste trec, 1 sărit)
- raport: docs/rapoarte/2026-10-31_1538_S56_placa_477.md
- verificat (supraveghetor, 31 oct 17:15): **corect** — |Δ logit| 0,000155 ≤ 0,001; 2,143 / 1,226 = 1,75× (la #459: 1,84×); `folosit: true`; placa 1.544 MB / 32 °C.
- tip: placă (scurtă: ~2–5 minute; la S50 aceeași măsurare a durat 2 minute, max 1.525 MB, 34 °C)
- fereastră: **după S55** (nu în paralel cu S55: bancul măsoară și procesorul, iar S55 îl ține ocupat). Prima fereastră a plăcii după ce S55 e `gata` sau `oprit` (zi 08:00–18:30 sau noapte 19:00–07:00).
- durată maximă: 30 de minute; placa sub 7.000 MB și 83 °C (paznicul)
- de ce: la S54 reglajul CCM pentru #477 s-a refăcut doar pe procesor, deci cu `placa=True` modulul ar rămâne acum pe procesor (la #459 avea și varianta de placă fp32, 1,84× mai rapidă). Executantul a propus-o în raportul S54.
- ce faci:
  1. Verifici că placa e liberă (`nvidia-smi`: niciun proces mare, sub ~1.000 MB) și că S55 nu mai rulează.
  2. O singură măsurare oficială: `python -X utf8 -m module.calcul.banc placa --kgr lucru/export/kronos_477_q8_0.kgr --iesire lucru/ccm/s56_placa.json` (aceleași setări ca la S50: 64 simboluri, 5 repetări, 6 răspunsuri). Regulile de acceptare sunt cele din S49/S50, deja în cod (aceleași simboluri ca referința, |Δ logit| ≤ 0,001; fp16/bf16 respinse dacă nu le îndeplinesc).
  3. Păstrezi reglajul de acum ca `lucru/ccm/reglaj-desktop-br58s2c_s54.json`, apoi `python -X utf8 -m module.calcul.reglaj scrie --banc lucru/ccm/s56_placa.json --inlocuieste` și `python -X utf8 -m module.calcul.reglaj verifica --kgr lucru/export/kronos_477_q8_0.kgr --placa` → trebuie `folosit: true`.
  4. `python -m pytest`: toate trec. Commit + push. Raport scurt `docs/rapoarte/2026-<data>_<ora>_S56_placa_477.md`: tabelul variantelor (acceptată, dif. logit-uri, cald s, simb/s), ce s-a ales pe procesor și pe placă, comparația cu #459 la S50 (1 fir 2,30 s, placa fp32 1,25 s), memoria maximă și temperatura plăcii.
- Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, modelele (doar citire), linia de cod. Implicitul `placa=False` rămâne. Nimic descărcat, nimic instalat, nimic șters.
- Dacă un pas pică de 2 ori la rând cu aceeași eroare: stare `oprit`, eroarea în raport.
- pre-înregistrare: nu e antrenare; regulile de acceptare sunt cele deja în cod din S49/S50
- aprobat de: supraveghetor, 31 oct 2026 14:20 (granița 2: comparații/măsurători pe placă; o rulare pe linia de model existentă #477)

### S57 — Kronos-Cod: pregătirea primei antrenări, DOAR cod și teste (modulul de date, configurarea, examenul pe validare) — fără placă, fără antrenare
- stare: gata (executant, 31 oct 17:47: `module/date_cod.py` (trece `teste_contracte/`), `unelte/kronos_cod/examen_validare.py`, `config/cod_c1.toml` (nepornită), 13 teste noi; indexul validării pe datele reale = S55 exact (5.686 fișiere, 3,4617 octeți/simbol); memoria estimată lot 8 ~5,3–5,8 GB; **înainte de S58: modelul trebuie să citească simbolurile + examen pe ore pentru cod** (propunerile în raport); 1145 teste trec, 1 sărit)
- raport: docs/rapoarte/2026-10-31_1747_S57_pregatire_cod_c1.md
- tip: procesor (fără placă, fără rețea)
- fereastră: oricând (acum e liber și procesorul, și placa)
- durată maximă: 3 ore
- de ce: S55 a ieșit BUN (3,46 octeți/simbol, +22,1 % față de w2). Propunerea primei antrenări (raportul S55, punctul 6) spune ce lipsește în cod. Pregătirea nu antrenează nimic și nu folosește placa (granițele 3 și 5); antrenarea însăși (S58) e linie de model nouă → așteaptă „da”-ul lui Adrian. Dacă Adrian spune „da”, noaptea poate porni fără o zi de așteptare.
- ce faci:
  1. Modul nou de date `module/date_cod.py` (port-ul de date, ca `date_fisier.py`), cu `MANIFEST` și fișa `module/manifeste/date_cod.toml`: citește `lucru/kronos_cod/simboluri/` (uint16, sfârșit de fișier = 32.764), dă bucăți de 512 simboluri pentru antrenare și, separat, validarea (cele 5.686 fișiere, niciodată amestecate în antrenare). Îl adaugi în lista `MODULE` din `teste_contracte/` și trebuie să treacă.
  2. Unealtă `unelte/kronos_cod/examen_validare.py`: pierderea pe validare → **biți pe octet** = pierdere / ln 2 / (octeți pe simbol măsurați pe aceleași fișiere), pe tot și pe Python / Rust / C. `module/examen_bpb.py` NU se atinge.
  3. Configurarea `config/cod_c1.toml` (linie nouă `cod_c1`), exact după propunerea din raportul S55: 12 straturi, 12 capete, 768, context 512, vocabular 32.768, de la zero, AdamW, rata max 6·10⁻⁴, încălzire 1.000 pași, scădere la 10 %, lot 8 cu adunare de loturi (același lot efectiv ca linia w2), sămânța 0, limită 10 ore. **Doar scrisă — NU o pornești, nici măcar proba de 10 minute.**
  4. Teste fără placă și fără date reale (fișiere mici uint16 făcute în test): bucățile au 512 simboluri, validarea nu apare în antrenare, biții/octet pe un exemplu calculat de mână, configurarea se încarcă (fără să pornească).
  5. `python -m pytest`: toate trec. Commit + push. Raport scurt `docs/rapoarte/2026-<data>_<ora>_S57_pregatire_cod_c1.md`: ce fișiere, ce teste, **estimarea memoriei pe placă** pentru lot 8 (calcul, nu măsurare) și orice schimbare pe care o propui la S58.
- Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, modelele, linia română (#477), setul ascuns (nu-l deschizi), datele din `lucru/kronos_cod/` (doar citire). Nimic pe placă, nimic descărcat, nimic instalat. Nimic din `lucru/` în Git.
- Dacă un pas pică de 2 ori la rând cu aceeași eroare: stare `oprit`, eroarea în raport.
- pre-înregistrare: nu e antrenare (pre-înregistrarea vine la S58)
- aprobat de: supraveghetor, 31 oct 2026 17:15 (granițele 3 și 5: pregătirea datelor deja aprobate + unelte/teste; fără `kronos/`, fără examen, fără antrenare)

### S58 — Kronos-Cod: prima antrenare `cod_c1` pe placă (o noapte, de la zero) — LINIE DE MODEL NOUĂ
- stare: oprit (executant, 2 nov 06:08: pașii 3–4 rulați până la capăt, cod 0; validarea întreagă **0,5141** biți/octet, setul ascuns **pass@10 = 3/200**, pass@1 0,15 % → după praguri **NECLAR**; 1168 teste trec, 1 sărit)
- motiv: placa peste 7.000 MB la pasul 4(ii) (`examen_cod.py model`: 7.188–7.971 MB, ~17 min, 52–55 °C); `taskkill` blocat de permisiuni, paznicul nu supraveghează unealta → n-am putut opri. Dacă cifrele contează decide Adrian.
- raport: docs/rapoarte/2026-11-02_0608_S58_cod_c1.md
- verificat (supraveghetor, 2 nov 08:15): **cifrele corecte, verdictul NECLAR corect** — 0,5141 ≤ 1,10 ✓, pass@10 3/200 < 10 ✗ și > 0 → nici ÎNVAȚĂ, nici NU ÎNVAȚĂ; antrenarea în limite (max 6.205 MB, 64 °C), de la zero, 10/10 ore; modelul examinat la (i) = #489 = `gpt.pt` (149/149 tensori identici). **Abaterea e reală:** la (ii) placa 7.188–7.971 MB ~17 min, neoprită (paznicul nu vede `unelte/kronos_cod/`, `taskkill` blocat). Stare rămâne `oprit` până spune Adrian dacă cifrele contează. Reparațiile → **S62** (aprobată, ziua 2 nov). A doua noapte → **S63** (`propus — necesită Adrian`).
- stare anterioară: in_lucru (executant, 2 nov 05:35 — pasul 3 GATA: 10 ore, cod 0, 05:15:47, #480–#489, examenul orar 0,4967 la ora 10, 1.204 M simboluri, fără „Pornesc din”; pasul 4 pornit prin `lucru/cascada/S58_proba/s58_examene.py`. Prima pornire 05:29 a căzut la (i): `examen_validare.py` nu citește starea liniei `gpt.pt` (KeyError 'vocabular'), setul ascuns NEdeschis; a doua 05:35 cu (i) pe `lucru/stocare/modele/experiment_489.pt` = aceeași stare (149/149 tensori identici), (ii) pe `gpt.pt` ca în coadă)
- stare anterioară: in_lucru (executant, 1 nov 19:00 — pasul 3: 10 ore cu `config/cod_c1_init002.toml`; actualizarea pre-înregistrării C-50 urcată la 18:59, înainte de pornire)
- stare anterioară: **aprobat** — DOAR pasul 3 (+ pasul 4) rămas (executant, 31 oct 21:45): **pașii 1–2 GATA** — pre-înregistrarea `docs/preinregistrari/2026-10-31_cod_c1.md` (3b7f4dd, deschisă) și proba de 10 minute (21:30–21:40, cod 0: placa max 6.078 MB < 6.500, 63 °C, 32.364 simb/s; pierderea de pornire 474 — vezi raportul). NU le mai repeta. Pasul 3 pornește cel mai devreme **1 nov 19:00**: `cascada.py porneste S58 -- .venv/Scripts/python -X utf8 unelte/antrenare_lunga.py --config config/cod_c1.toml --ore 10 --inceput "def "`
- **SCHIMBARE APROBATĂ DE ADRIAN (C-50, 1 nov 2026 11:55, „da init002”) — scrisă de supraveghetor la 11:55:** pașii 3 și 4 folosesc **`config/cod_c1_init002.toml`** (abaterea 0,02, verificată la S61: AJUTĂ), NU `config/cod_c1.toml`. Restul neschimbat (10 ore, 1 nov de la 19:00, aceleași praguri ÎNVAȚĂ / NU ÎNVAȚĂ / NECLAR, aceeași limită 6.500 MB/7.000 MB/83 °C; proba de 10 minute S61 a măsurat deja 6.078 MB cu această configurare — NU o repeta). Înainte de pornire:
  a. **Pre-înregistrarea:** adaugă la `docs/preinregistrari/2026-10-31_cod_c1.md` o secțiune „Actualizare 1 nov (C-50): configurarea = `config/cod_c1_init002.toml`” cu ora, pragurile copiate **neschimbate** și așteptările tale în cifre pentru noua pornire (reper: proba S61, primul lot 10,67, media ultimelor 100 = 3,769); commit + push **înainte** de pasul 3.
  b. Pasul 3: `cascada.py porneste S58 -- .venv/Scripts/python -X utf8 unelte/antrenare_lunga.py --config config/cod_c1_init002.toml --ore 10 --inceput "def "`
  c. Pasul 4 (i) și (ii): aceeași configurare `config/cod_c1_init002.toml` (modelul se salvează tot în `lucru/cod_c1/gpt.pt`, ca la `cod_c1.toml`). Nu modifici fișierul de configurare (comentariul de sus din el e de la S61; e doar un comentariu).
  d. În raport scrii clar configurarea folosită.
- stare anterioară: in_lucru (executant, 31 oct 21:30 — pașii 1–2); înainte: **aprobat** (Adrian, 31 oct 20:53, „da s58”)
- raport (pașii 1–2): docs/rapoarte/2026-10-31_2145_S58_proba_cod_c1.md
- verificat (supraveghetor, 31 oct 23:15): pașii 1–2 **corecți** — pre-înregistrarea urcată 21:30:02, proba pornită 21:30:11 (deci înainte), pragurile copiate neschimbate; 6.078 MB < 6.500, 63 °C < 83 °C, cod 0, `lucru/cod_c1/` nescris. **Înainte de pasul 3: S61** (comparația inițializării, pe o configurare separată; nu schimbă S58). Pasul 3 rămâne cu `config/cod_c1.toml`, dacă Adrian nu alege altfel după S61.
- programare (supraveghetor, 31 oct 20:56): **întâi S60** (proba de la zero + răspunsurile pentru pass@k; raportul S59 arată că pașii 2 și 4(ii) n-au încă unealta). **În noaptea 31 oct → 1 nov:** după S60 `gata`, doar pașii 1–2 (pre-înregistrarea, apoi proba de 10 minute), dacă poți începe proba până la 06:30. **Pasul 3 (cele 10 ore): noaptea 1 → 2 nov, de la 19:00** (porniți acum, cele 10 ore ar trece de dimineață, iar pe 1 nov Adrian poate veni la workstation). Dacă pe 1 nov Adrian e la workstation pentru fereastra OS/GPU (C-47): nu pornești nimic pe placă până nu se termină fereastra; dacă pornești după 20:50, rulezi tot 10 ore, iar fereastra de zi de pe 2 nov rămâne liberă până se termină. La pasul 3 adaugă `--inceput "def "` (sugestia din raportul S59; nu schimbă antrenarea). Dacă proba trece de 6.500 MB: oprești, raportezi, nu pornești pasul 3.
- stare anterioară: propus — necesită Adrian
- tip: placă
- fereastră: noapte (19:00–07:00), prima noapte după S57 și S59 `gata` și după „da”-ul lui Adrian
- durată maximă: proba de 10 minute + 10 ore; placa sub 7.000 MB și 83 °C (paznicul); proba se oprește dacă trece de 6.500 MB
- de ce: etapa următoare din Kronos-Cod (C-28/C-45). E linie de model nouă (alt tokenizer) → după `REGULI_CASCADA.md` doar cu „da”-ul lui Adrian.
- ce faci (după „da”):
  1. **Pre-înregistrarea ÎNAINTE de probă:** `docs/preinregistrari/<data>_cod_c1.md`, commit + push. Cu pragurile de mai jos copiate neschimbate și cu așteptările tale în cifre.
  2. Proba de 10 minute cu `config/cod_c1.toml` (fără jurnal, ca la S30): memoria maximă a plăcii și simboluri/s. Peste 6.500 MB → oprești și raportezi (nu micșorezi singur modelul).
  3. Noaptea: 10 ore cu `config/cod_c1.toml`, prin `unelte/cascada.py`.
  4. Măsori (i) biți pe octet pe validarea de 5.686 fișiere (tot + Python/Rust/C) cu `unelte/kronos_cod/examen_validare.py`; (ii) o singură dată pass@1 și pass@10 pe cele 200 de probleme ascunse cu `unelte/kronos_cod/examen_cod.py` și cutia.
- pragurile (propuse de executant la S55, păstrate de supraveghetor): **ÎNVAȚĂ** = biți/octet pe validare ≤ 1,10 **și** pass@10 ≥ 10/200; **NU ÎNVAȚĂ** = biți/octet > 1,40 **sau** pass@10 = 0/200; altfel **NECLAR** (a doua noapte, tot cu „da”-ul lui Adrian sau în granița 1, pe linia acum existentă).
- Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, #477 și linia română. Raport `docs/rapoarte/<data>_<ora>_S58_cod_c1.md`.
- aprobat de: **Adrian, 31 oct 2026 20:53** („da s58”, COMENZI.md C-47); configurarea `cod_c1_init002`: **Adrian (COMENZI.md C-50, 1 nov 2026 11:55)**

### S59 — Kronos-Cod: modelul citește simbolurile direct + examenul pe ore în biți pe octet (doar cod și teste, înainte de S58) — fără placă, fără antrenare
- stare: gata (executant, 31 oct 20:48: `module/model_gpt_cod.py` + `module/examen_cod_validare.py` (ambele trec `teste_contracte/`), `cod_c1.toml` pe ele + `previzualizare = true` (testul rapid din kronos) + `hrana = ""` (altfel antrenare_lunga pune hrana implicită); eșantionul 1.000 fișiere = 2,10 mil. simboluri, examen estimat ~30–90 s pe placă; cap-coadă prin `antrenare_lunga.main` pe setul mic; fără `kronos/`; 1159 teste trec, 1 sărit. **S58 încă nu poate porni întreagă: lipsesc proba de la zero (`proba_muon.py` cere `--porneste-din`) și comanda care face modelul să scrie răspunsurile pentru pass@k** — propunerea S60 în raport)
- raport: docs/rapoarte/2026-10-31_2048_S59_cod_c1_gata_de_pornire.md
- stare anterioară: in_lucru (executant, 31 oct 20:30)
- tip: procesor (fără placă, fără rețea)
- fereastră: oricând (se face înaintea lui S58; nu folosește placa)
- durată maximă: 3 ore
- de ce: raportul S57 (punctele 1 și 2) arată că S58 s-ar opri din prima secundă: modelele de acum cer text, iar examenul de pe ore (`examen_bpb.py`) cere text de validare. Pregătirea e cod + teste, fără antrenare (granițele 2, 3 și 5). S58 rămâne doar cu „da”-ul lui Adrian.
- ce faci:
  1. **Model care citește simboluri, fără să atingi linia w2:** un modul NOU (de ex. `module/model_gpt_cod.py`, urmaș al clasei din `model_gpt`), cu `MANIFEST` + fișa din `module/manifeste/`, adăugat în `MODULE` din `teste_contracte/` (trebuie să treacă). Dacă datele au `simboluri_antrenare()`, le ia direct (în RAM ca int32; pe placă urcă doar lotul), fără tokenizare. `module/model_gpt.py` și `module/model_muon.py` NU se schimbă (#477 și linia română rămân identice).
  2. **Examen nou pe ore, separat:** un modul NOU de examen (de ex. `module/examen_cod_validare.py`) care folosește `unelte/kronos_cod/examen_validare.py` pe un **eșantion fix** al validării (aceleași fișiere de fiecare dată, alese cu sămânța 0, ~1 minut pe placă), în biți pe octet. Examenul întreg (toate cele 5.686) rămâne pentru după noapte. `module/examen_bpb.py`, paznicul și `kronos/` NU se ating.
  3. `config/cod_c1.toml` trece pe modulul de model nou și pe examenul nou. Tot nepornită (nici proba de 10 minute).
  4. Teste fără placă și fără date reale: modelul nou face un pas de antrenare pe procesor pe setul mic din `teste/cod_mic.py` și pierderea scade în câțiva pași; eșantionul examenului e același la două rulări; config-ul se încarcă și construiește modelul fără să pornească.
  5. `python -m pytest`: toate trec. Commit + push. Raport scurt `docs/rapoarte/2026-<data>_<ora>_S59_cod_c1_gata_de_pornire.md`: ce fișiere, ce teste, cât durează examenul pe eșantion (estimare), și dacă S58 poate porni așa cum e scrisă.
- **Dacă vreun pas cere o schimbare în `kronos/` (orchestrator, paznic, registru, contracte) ca orchestratorul să accepte modelul sau examenul nou: te oprești, stare `oprit`, scrii exact ce ar trebui schimbat — e decizia lui Adrian.**
- Nu atingi `kronos/`, `module/examen_bpb.py`, `module/model_gpt.py`, `module/model_muon.py`, paznicul, jurnalul, modelele, linia română (#477), setul ascuns (nu-l deschizi), datele din `lucru/kronos_cod/` (doar citire). Nimic pe placă, nimic descărcat, nimic instalat. Nimic din `lucru/` în Git.
- Dacă un pas pică de 2 ori la rând cu aceeași eroare: stare `oprit`, eroarea în raport.
- pre-înregistrare: nu e antrenare (pre-înregistrarea vine la S58)
- aprobat de: supraveghetor, 31 oct 2026 20:15 (granițele 2, 3 și 5: examen nou și unelte/module noi + teste, fără `kronos/`, fără `examen_bpb.py`, fără antrenare; modulele liniei w2 neatinse)

### S60 — Kronos-Cod: proba de la zero + comanda care scrie răspunsurile pentru pass@k (doar cod și teste, înainte de S58) — fără placă, fără antrenare
- verificat (supraveghetor, 31 oct 23:15): **corect** — 1165 = 1159 + 6 teste noi, setul ascuns nedeschis, `noteaza()` și cutia neschimbate.
- stare: gata (executant, 31 oct 21:09: `proba_muon.py` fără `--porneste-din` = de la zero (fără jurnal, fără starea liniei) + simboluri/s; `examen_cod.py model` (10 corpuri/problemă, temperatura 0,8, sămânța 0, oprire la ieșirea din funcție sau 256 simboluri; SHA-ul setului ascuns verificat) + `noteaza` (cutia neschimbată); 6 teste noi pe setul de probă; setul ascuns nedeschis; 1165 teste trec, 1 sărit; pasul 4(ii) estimat ~20–35 min)
- raport: docs/rapoarte/2026-10-31_2109_S60_unelte_S58.md
- stare anterioară: in_lucru (executant, 31 oct 21:00)
- tip: procesor (fără placă, fără rețea)
- fereastră: acum (31 oct seara/noaptea); se face înaintea pașilor 2 și 4(ii) din S58
- durată maximă: 3 ore
- de ce: raportul S59 („Poate porni S58 așa cum e scrisă?”): proba de 10 minute nu poate porni de la zero (`unelte/proba_muon.py` cere `--porneste-din`), iar `unelte/kronos_cod/examen_cod.py` notează răspunsuri, dar nu are comanda care face modelul să le scrie. Unelte + teste, fără `kronos/` și fără examenul oficial (granița 5). S58 e aprobată de Adrian (C-47).
- ce faci:
  1. `unelte/proba_muon.py`: `--porneste-din` devine opțional. Fără el: model nou, de la zero, fără stare de pornire; cu el: exact ca acum (testele vechi trec neschimbate). Test nou: proba de la zero pe `config/cod_c1.toml` micșorat (rețea mică, setul mic din `teste/cod_mic.py`, câteva secunde, procesor) — pornește, scrie memoria maximă și simboluri/s, nu scrie în jurnal.
  2. `unelte/kronos_cod/examen_cod.py`: o comandă nouă `model` care, din modelul salvat (`--config`, `--stare`), scrie pentru fiecare problemă **n = 10** corpuri de funcție (temperatură fixă scrisă în raport, de ex. 0,8; sămânța 0; oprire la sfârșitul funcției sau la o limită de simboluri), într-un fișier pe care `noteaza` îl citește direct. Notarea (`noteaza`, cutia) NU se schimbă.
  3. Teste NUMAI pe setul de PROBĂ (`proba`), niciodată pe cel ascuns (rămâne nedeschis până la pasul 4(ii) din S58): cu un model mic, netreinat, comanda scrie 10 răspunsuri pe problemă, aceleași la două rulări cu aceeași sămânță, iar `noteaza` le primește fără eroare (pass@k poate fi 0 — contează că drumul merge cap-coadă).
  4. `python -m pytest`: toate trec. Commit + push. Raport scurt `docs/rapoarte/2026-<data>_<ora>_S60_unelte_S58.md`: ce fișiere, ce teste, comenzile exacte pentru pașii 2 și 4(ii) din S58 și cât estimezi că durează pasul 4(ii) pe placă (200 × 10 răspunsuri).
- După ce S60 e `gata`: treci la S58 după programarea scrisă la S58.
- Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, modelele, linia română (#477), setul ascuns (nu-l deschizi), datele din `lucru/kronos_cod/` (doar citire), `unelte/kronos_cod/examen_validare.py` (de acum îl tratăm ca examen). Nimic pe placă, nimic descărcat, nimic instalat. Nimic din `lucru/` în Git.
- Dacă un pas cere o schimbare în `kronos/`: te oprești, stare `oprit`, scrii exact ce ar trebui schimbat.
- Dacă un pas pică de 2 ori la rând cu aceeași eroare: stare `oprit`, eroarea în raport.
- pre-înregistrare: nu e antrenare (pre-înregistrarea vine la S58)
- aprobat de: supraveghetor, 31 oct 2026 20:56 (granița 5: unelte noi + teste, fără `kronos/`, fără examenul oficial, fără antrenare; propunerea executantului din raportul S59)

### S61 — Kronos-Cod: inițializarea încorporărilor (abaterea 0,02) pe o configurare SEPARATĂ + o probă de 10 minute de comparație (procesor + 10 min pe placă) — S58 rămâne neschimbată
- stare: gata (executant, 1 nov 00:06: proba cod 0, de la zero; primul lot **10,67** (S58: 473,9), media ultimelor 100 **3,769** (S58: 6,818), 4.777 loturi, 6.078 MB, 63 °C, 32.344 simb/s → **AJUTĂ**; o probă pe parte, zgomotul nemăsurat; 1168 teste trec, 1 sărit. Alegerea configurării pentru S58 pasul 3 = Adrian; implicit `cod_c1.toml`)
- stare anterioară: in_lucru (executant, 31 oct 23:29)
- tip: procesor + 10 minute pe placă (doar proba, fără antrenare salvată)
- fereastră: **noaptea asta (31 oct → 1 nov)**, proba pornită până la 06:30. Dacă nu se poate: ziua de 1 nov (08:00–18:00), DAR nu cât timp Adrian e la workstation pentru fereastra OS/GPU (C-47) și în niciun caz nu întârzie pasul 3 din S58 (1 nov 19:00).
- durată maximă: 2 ore de cod + proba de 10 minute; placa: oprire peste 6.500 MB (paznicul: 7.000 MB / 83 °C)
- de ce: raportul S58 pașii 1–2 (`docs/rapoarte/2026-10-31_2145_S58_proba_cod_c1.md`): pierderea de pornire e **474** (la întâmplare ar fi ~10,4 = ln 32.768), pentru că încorporările au inițializarea implicită (mari), iar capul e legat de ele. Executantul a propus varianta (b): abaterea 0,02, ca la GPT-2. Ca Adrian să aleagă pe cifre, nu pe impresii, măsurăm acum varianta pe o configurare separată. Granițele 2 și 5 (comparație + modul/unelte cu teste, fără `kronos/`, fără examen, fără linie nouă salvată). **Folosirea ei în S58 rămâne decizia lui Adrian.**
- ce faci:
  1. `module/model_gpt_cod.py`: o setare nouă, opțională, `abatere_incorporari`. **Fără ea în configurare = exact comportamentul de acum.** Cu ea: încorporările (deci și capul legat) pornesc din normala cu media 0 și abaterea dată. ÎNAINTE de schimbare, calculează amprenta SHA-256 a greutăților de pornire ale modelului din `config/cod_c1.toml` micșorat din teste (aceeași sămânță) și pune-o într-un test nou: după schimbare, fără setare, amprenta trebuie să fie identică bit cu bit. Al doilea test: cu `abatere_incorporari = 0.02`, pierderea primului lot pe setul mic din `teste/cod_mic.py` e sub 2 × ln(mărimea vocabularului). Modulul trebuie să treacă în continuare `teste_contracte/`.
  2. `config/cod_c1_init002.toml` = copie a lui `config/cod_c1.toml` + `abatere_incorporari = 0.02`, nimic altceva diferit. **`config/cod_c1.toml` NU se schimbă.**
  3. **Pre-înregistrarea ÎNAINTE de probă:** `docs/preinregistrari/2026-11-01_cod_c1_init002.md` (commit + push), cu pragurile de aici copiate neschimbate și așteptările tale în cifre. Reperul = proba S58 (`lucru/cascada/S58_proba/proba.json`: primul lot 473,9; media ultimelor 100 loturi 6,82 la 4.781 de loturi; 6.078 MB; 32.364 simb/s).
     - **AJUTĂ** = pierderea primului lot ≤ 15 **și** media ultimelor 100 de loturi ≤ 6,52 (cu cel puțin 0,30 sub S58);
     - **NU AJUTĂ** = media ultimelor 100 de loturi ≥ 6,82;
     - altfel **NECLAR**. Dacă proba face sub 4.500 de loturi (comparația n-ar mai fi la același punct): NECLAR, scrii de ce.
     - O singură probă pe fiecare parte; scrie în raport că zgomotul între rulări nu e măsurat.
  4. Proba (de la zero, fără jurnal, prin cascadă): `.venv/Scripts/python -X utf8 unelte/cascada.py porneste S61 -- .venv/Scripts/python -X utf8 unelte/proba_muon.py --config config/cod_c1_init002.toml --minute 10 --memorie-max 6500 --dosar lucru/cascada/S61_proba`. Peste 6.500 MB: oprești și raportezi.
  5. `python -m pytest`: toate trec. Commit + push. Raport `docs/rapoarte/2026-11-01_<ora>_S61_init_cod.md`: un tabel S58 față de S61 (pierderea la primul lot, la loturile ~10, ~100, ~1.000, media ultimelor 100, numărul de loturi, memoria, temperatura, simb/s), verdictul după pragurile de mai sus și o propoziție pentru Adrian: „pornim cele 10 ore cu `cod_c1.toml` (cum e aprobat) sau cu `cod_c1_init002.toml`?”.
- **Nu schimbi S58, nici pre-înregistrarea ei `docs/preinregistrari/2026-10-31_cod_c1.md`, nici comanda pasului 3.** Pasul 3 din S58 pornește cu `config/cod_c1.toml` dacă Adrian nu scrie altfel (în hub, `COMENZI.md`, sau în coadă). Dacă Adrian alege `cod_c1_init002.toml`: înainte de pornire adaugi în pre-înregistrarea S58 o notă datată „configurarea schimbată la cererea lui Adrian: cod_c1_init002.toml (S61)”, cu pragurile neschimbate.
- Nu atingi `kronos/`, `module/examen_bpb.py`, `module/model_gpt.py`, `module/model_muon.py`, paznicul, jurnalul, #477, linia română, setul ascuns (nu-l deschizi), `unelte/kronos_cod/examen_validare.py`, `unelte/kronos_cod/examen_cod.py`, datele din `lucru/kronos_cod/` (doar citire). Nimic descărcat, nimic instalat. Nimic din `lucru/` în Git.
- Dacă un pas cere o schimbare în `kronos/`: te oprești, stare `oprit`, scrii exact ce ar trebui schimbat. Dacă un pas pică de 2 ori la rând cu aceeași eroare: stare `oprit`, eroarea în raport.
- pre-înregistrare: docs/preinregistrari/2026-11-01_cod_c1_init002.md (înainte de probă)
- raport: docs/rapoarte/2026-11-01_0006_S61_init_cod.md
- verificat (supraveghetor, 1 nov 02:15): **AJUTĂ, corect** — pre-înregistrarea urcată 23:37 (commit 8d6337a), proba pornită 23:37:01, pragurile copiate neschimbate; 10,67 ≤ 15 și 3,769 ≤ 6,52 (3,769 = 6,818 − 3,049, deci ≥ 0,30 sub S58); 4.777 loturi ≥ 4.500; 6.078 MB < 6.500, 63 °C; de la zero, fără model păstrat; 1168 teste trec. Zgomotul nemăsurat (o probă pe parte). S58 pasul 3 rămâne cu `config/cod_c1.toml` dacă Adrian nu alege `cod_c1_init002.toml` înainte de 1 nov 19:00.
- aprobat de: supraveghetor, 31 oct 2026 23:15 (granițele 2 și 5: o comparație de 10 minute fără model salvat + o setare opțională într-un modul, cu testul că fără ea nimic nu se schimbă; fără `kronos/`, fără examen; S58 neatinsă; alegerea configurării pentru S58 = Adrian)

### S62 — Kronos-Cod: uneltele de examen de cod se țin singure sub limita plăcii + `examen_validare.py` citește `gpt.pt` (procesor + o măsurare scurtă pe placă, pe setul de PROBĂ)
- stare: gata (executant, 2 nov 09:04: măsurarea 08:37–08:48, cod 0; (a) proba 20×10 `--lot 2` vârf 1.924 MB, 91 s; (b) validarea din `gpt.pt` vârf 4.416 MB, 534 s, **0,51411** = S58; ambele sub 6.500 MB (S58: 7.971); 200×10 estimat ~15 min; uneltele bune pentru S63; 1174 teste trec, 1 sărit)
- tip: procesor + ~30 min pe placă (doar măsurare, fără antrenare)
- fereastră: zi (2 nov, 08:00–18:30); trebuie `gata` înainte de orice alt examen de cod pe placă (inclusiv S63)
- durată maximă: 4 ore de cod + măsurarea; la măsurare oprire singură peste 6.500 MB (paznicul: 7.000 MB / 83 °C)
- de ce: raportul S58 (`docs/rapoarte/2026-11-02_0608_S58_cod_c1.md`, §2 și §4): (ii) a ținut placa la 7.188–7.971 MB ~17 min și nimic n-a putut-o opri; (i) a căzut întâi pentru că `examen_validare.py` nu citește `gpt.pt`. Reparații de unelte care au picat + teste, fără `kronos/`, fără `examen_bpb.py`, fără să schimbi notarea (granițele 5 și 6) + o măsurare pe setul de probă (granița 2).
- ce faci:
  1. `unelte/kronos_cod/examen_cod.py model`: opțiune nouă `--lot` (câte corpuri se scriu odată; implicit **2**) și `--memorie-max` (MB, implicit **6500**). Fiecare corp primește sămânța lui (din sămânța de bază + problemă + număr corp), ca răspunsurile să fie **identice oricare ar fi `--lot`**. După fiecare lot: `torch.cuda.empty_cache()` și citirea memoriei (`torch.cuda.max_memory_reserved()` sau `nvidia-smi`); dacă trece de `--memorie-max`, unealta **se oprește singură** cu cod de ieșire ≠ 0 și scrie ce a apucat (marcat „incomplet”). `noteaza`, cutia, temperatura, `MAX_SIMBOLURI` și setul de probă/ascuns NU se schimbă.
  2. `unelte/kronos_cod/examen_validare.py`: să citească și starea liniei (`lucru/cod_c1/gpt.pt`, ca `examen_cod.py`), nu doar modelul salvat în jurnal; aceeași `--memorie-max` cu oprire singură. Calculul biților NU se schimbă.
  3. Teste (procesor, model mic din teste, setul de PROBĂ): (a) `--lot 1`, `--lot 2` și `--lot 10` dau răspunsuri identice; (b) o limită de memorie mică falsă (simulată) oprește unealta cu cod ≠ 0 și fișier „incomplet”; (c) `examen_validare.py` pe același model mic dă aceeași cifră din `gpt.pt` și din modelul salvat în jurnal.
  4. `python -m pytest`: toate trec. Commit + push.
  5. **Măsurarea pe placă** (ziua, cu `nvidia-smi` la 5 s într-un fișier): (a) `examen_cod.py model` pe setul **de probă** (20 de probleme × 10), modelul `lucru/cod_c1/gpt.pt`, `--lot 2` → memoria maximă și durata; (b) `examen_validare.py` pe validarea întreagă cu `gpt.pt` → memoria maximă, durata, și cifra (trebuie să iasă **0,5141**, ca la S58; dacă nu, scrii diferența). Setul ascuns NU se deschide. Dacă (a) sau (b) trece de 6.500 MB: unealta se oprește, raportezi, nu încerci altceva.
  6. Raport `docs/rapoarte/2026-11-02_<ora>_S62_unelte_cod_memorie.md`: ce s-a schimbat, testele, memoria maximă la (a) și (b) față de S58 (7.971 MB), durata estimată pentru 200 × 10 cu `--lot 2`, și dacă uneltele pot fi folosite la S63.
- Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, modelele, #477, linia română, setul ascuns S58 (e folosit; nu-l redeschizi), datele din `lucru/kronos_cod/` (doar citire). Nimic descărcat, nimic instalat. Nimic din `lucru/` în Git.
- Dacă un pas cere o schimbare în `kronos/`: te oprești, stare `oprit`, scrii exact ce ar trebui schimbat. Dacă un pas pică de 2 ori la rând cu aceeași eroare: stare `oprit`, eroarea în raport.
- pre-înregistrare: nu e antrenare (doar o măsurare de memorie; cifra (b) trebuie să fie 0,5141)
- aprobat de: supraveghetor, 2 nov 2026 08:15 (granițele 2, 5 și 6: reparația uneltelor care au picat la S58 + teste + o măsurare pe setul de probă; fără `kronos/`, fără examenul oficial, notarea neschimbată; propunerile (a) și (b) ale executantului din raportul S58)
- raport: docs/rapoarte/2026-11-02_0904_S62_unelte_cod_memorie.md

### S63 — Kronos-Cod: a doua noapte pe linia `cod_c1` (10 ore, din `gpt.pt`), apoi biții pe validare + pass@k pe un set ascuns NOU (placa)
- stare: gata — verificat de supraveghetor 2 nov 23:20: NECLAR corect (executant, 2 nov 22:40: lanțul 11:38:36–22:28:02, cod 0; orele 11–20 din starea liniei, examenul orar 0,4967 → 0,4834; (i) validarea întreagă **0,50041** (S58 0,5141); (ii) `ascuns2` **pass@10 = 3/163**, pass@1 0,25 %; (iii) proba 0/20 → după praguri **NECLAR**; placa max 6.013 MB / 63 °C; 1177 teste trec, 1 sărit)
- stare anterioară: in_lucru (executant, 2 nov 11:38: pasul 1 GATA 7a1197f (`--exclude-dosar`/`--max-pe-sablon`, 3 teste noi, 1177 trec, 1 sărit); pasul 2 GATA: `ascuns2` **N = 163** (referințele 163/163); pre-înregistrarea `2026-11-02_cod_c1_noaptea2.md` f876939 (CONTINUĂ ≤ 0,494 și ≥ 5/163; PLATOU > 0,504 și ≤ 2/163); lanțul `lucru/cascada/S63_proba/s63.py` pornit 11:38:36 (proces 19128): „orele 11–20” verificat în log, placa 5.974 MB / 62 °C; sfârșit estimat ~22:00 + examene ~30 min. Pornit ziua deși cele ~11 ore trec de 18:30: fereastra sarcinii e „oricând (zi sau noapte)”, C-56)
- verdict verificat (supraveghetor, 2 nov 23:20): **NECLAR, corect.** Recalculat: 0,5141 − 0,50041 = 0,0137 (CONTINUĂ cere ≤ 0,494 ✗, PLATOU cere > 0,504 ✗); pass@10 3/163 = 1,84 % (CONTINUĂ ≥ 5 ✗, PLATOU ≤ 2 ✗); pass@1 4/1.630 = 0,245 % ✓; examenul orar 0,4946 → 0,4834, fiecare oră mai bună ✓; pre-înregistrarea f876939 urcată înainte de pornire ✓; examenele o singură dată, pe starea de după ora 20 ✓; placa max 6.013 MB / 63 °C ✓; 1177 teste trec ✓. Lecția: a doua noapte mai îmbunătățește forma codului (~0,001 biți/oră la sfârșit), dar rezolvarea problemelor rămâne ~2 %. Următorul pas: S64 (diagnostic, nu încă o noapte).
- verificat (supraveghetor, 2 nov 14:36): pre-înregistrarea f876939 (11:38) urcată ÎNAINTE de pornire (11:38:36); N = 163 și pragurile = regula din coadă (⌈0,03×163⌉ = 5, ⌊0,015×163⌋ = 2), biții neschimbați (0,494 / 0,504); pornit din starea liniei; placa 5.974 MB / 62 °C. Nicio sarcină nouă pe placă până la sfârșitul S63 (~22:00 + examene).
- stare anterioară: **aprobat** (supraveghetor, 2 nov 11:20: setul ascuns = **varianta (a)**, vezi „decizia setului” mai jos; restul sarcinii neschimbat, tot aprobarea lui Adrian C-56)
- decizia setului (supraveghetor, 2 nov 11:20; granițele 2 și 5 — examen + unealtă cu test, notarea neschimbată):
  **(a) set ascuns nou FĂRĂ nicio suprapunere** cu setul de probă și cu setul ascuns S58, cu cât încape (estimat ~163 de probleme × 10).
  Motivul: e singurul set cu adevărat nevăzut; (b) ar repeta variante deja notate (la `s07` aproape toate).
  Pașii, în ordinea asta:
  1. `examen_cod.py ascuns`: opțiunea `--exclude-dosar` (poate fi dată de mai multe ori) + `--max-pe-sablon 10`: fiecare șablon dă min(10, variantele rămase);
     unealta scrie în `rezumat` numărul total N și câte pe șablon. Teste pe procesor (un set „vechi” FALS din teste, nu cel adevărat): nicio problemă din dosarele excluse nu
     apare în setul nou; același rezultat la aceeași sămânță. `noteaza`, cutia, temperatura, `MAX_SIMBOLURI` NU se schimbă. `python -m pytest`: toate trec; commit + push.
  2. Setul: `examen_cod.py ascuns --dosar lucru/kronos_cod/ascuns2/` (sămânța secretă o alege unealta, ca la S58), excluzând setul de probă și dosarul setului ascuns S58 (unealta citește doar identitatea variantelor, tu nu-l deschizi și nu-l arăți).
     Notezi doar N și împărțirea pe șabloane (nu problemele).
  3. **Pre-înregistrarea** (`docs/preinregistrari/2026-11-02_cod_c1_noaptea2.md`), commit + push ÎNAINTE de antrenare, cu N-ul real și pragurile în număr întreg:
     **CONTINUĂ** = biți/octet ≤ **0,494** **și** pass@10 ≥ **⌈0,03 × N⌉** (la N = 163 → 5); **PLATOU** = biți/octet > **0,504** **și** pass@10 ≤ **⌊0,015 × N⌋** (la N = 163 → 2);
     altfel **NECLAR**. Scrii și: orele 11–20 rulează cu rata fixă 6·10⁻⁵ (scăderea s-a terminat la ora 10), fără încălzire nouă — acceptat, nu se schimbă configurarea.
     Reperul S58 (3/200 = 1,5 %) e pe alt set; comparația e aproximativă și o spunem așa.
  4. Apoi pașii 3–4 de mai jos (10 ore din `gpt.pt` + examenele cu `--lot 2 --memorie-max 6500`; la (ii) `model --set ascuns --dosar lucru/kronos_cod/ascuns2` și `noteaza --dosar lucru/kronos_cod/ascuns2`, N × 10).
  Dacă pasul 1 sau 2 pică de 2 ori la rând: `oprit`, eroarea în raport; placa NU pornește.
  Adrian poate cere varianta (b) până la examene (comanda „S63 varianta b”); antrenarea nu depinde de set.
- stare anterioară: oprit (executant, 2 nov 09:32: nimic pornit; pasul 2 imposibil așa cum e scris — un set ascuns nou de 200 (20 × 10) fără variantele S58 nu încape: 13 din 20 de șabloane au ≤ 24 de variante, `s07_roteste` doar 14 → ~163 de probleme fără suprapunere; 1174 teste trec, 1 sărit)
- motiv: cere alegerea lui Adrian/supraveghetorului: setul ascuns nou — (a) ~163 de probleme fără suprapunere, pragurile pe procente, sau (b) 200 cu sămânță nouă, ca la S58 (suprapunere parțială); antrenarea (orele 11–20 din `gpt.pt`, rata fixă 6·10⁻⁵) nu depinde de set
- stare anterioară: **aprobat** (Adrian, 2 nov 08:46: „pornește acum sau cât de curând S63”; COMENZI.md C-56) — **fereastră: imediat după S62 `gata` (cu memoria sub 6.500 MB), și ziua; nu se așteaptă 19:00**
- stare anterioară: propus — necesită Adrian (răspunsul „da S63” în hub, `COMENZI.md`). Motivul: pornește din S58, iar Adrian n-a spus încă dacă cifrele S58 contează (abaterea de memorie); setul ascuns S58 e folosit, iar pass@k ar cere un set ascuns NOU (altă sămânță, aceleași 20 de șabloane).
- tip: placă
- fereastră: **oricând (zi sau noapte), imediat după S62 `gata`** cu memoria sub 6.500 MB la ambele măsurări (C-56; înainte: noapte 19:00–07:00). Dacă S62 iese `oprit` sau peste 6.500 MB, S63 NU pornește.
- durată maximă: 10 ore + examenele (~1 oră); placa sub 7.000 MB și 83 °C; examenele cu `--memorie-max 6500`
- de ce: pre-înregistrarea S58 spune dinainte: NECLAR → „a doua noapte, pe linia acum existentă”. Biții au scăzut la fiecare oră (0,5007 → 0,4967 în ultima, tot mai încet), deci mai e de câștigat; pass@10 3/200 e întrebarea deschisă.
- ce faci (după „da”):
  1. **Pre-înregistrarea ÎNAINTE de pornire:** `docs/preinregistrari/<data>_cod_c1_noaptea2.md`, commit + push, cu pragurile de mai jos copiate neschimbate și așteptările tale în cifre. Reperul = S58: validarea întreagă 0,5141; pass@10 3/200 (alt set, deci comparabil doar aproximativ).
  2. Setul ascuns nou: `examen_cod.py ascuns` într-un dosar NOU (de ex. `lucru/kronos_cod/ascuns2/`), care exclude și setul de probă, **și** variantele setului ascuns S58 (dacă unealta nu știe să excludă un al doilea set, adaugi asta cu un test, fără să schimbi notarea). Nu-l citești și nu-l arăți înainte de pasul 4.
  3. 10 ore, continuare din starea liniei `lucru/cod_c1/gpt.pt`, aceeași `config/cod_c1_init002.toml`, prin `unelte/cascada.py` (în log TREBUIE să apară că pornește din starea liniei; dacă pornește de la zero → `oprit`).
  4. Examenele, o singură dată, cu uneltele reparate la S62 (`--lot 2 --memorie-max 6500`): (i) biți pe octet pe validarea întreagă (tot + Python/Rust/C); (ii) pass@1 și pass@10 pe setul ascuns NOU (200 × 10, temperatura 0,8, sămânța 0); (iii) aceleași setări pe setul de probă (20 de probleme), doar ca informație.
- pragurile (propuse de supraveghetor; executantul le copiază neschimbate): **CONTINUĂ** = biți/octet ≤ **0,494** (cu cel puțin 0,02 sub 0,5141) **și** pass@10 ≥ **6/200**; **PLATOU** = biți/octet > 0,504 (sub 0,01 câștig) **și** pass@10 ≤ 3/200; altfel **NECLAR**. O sămânță, o noapte; setul ascuns e altul decât la S58, deci 3 → 6 e o diferență mică și o spunem așa.
- Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, #477, linia română, setul ascuns S58. Raport `docs/rapoarte/<data>_<ora>_S63_cod_c1_noaptea2.md`.
- aprobat de: **Adrian, 2 nov 2026 08:46** („pornește acum S63”, C-56)
- raport: docs/rapoarte/2026-11-02_2240_S63_cod_c1_noaptea2.md (înainte: 2026-11-02_0932_S63_oprit_set_ascuns.md)

### S64 — Kronos-Cod: diagnostic „mai multe încercări ajută?” — pass@k cu multe corpuri pe setul de PROBĂ + de ce pică corpurile (placa ~1,5 ore + procesor)
- stare: gata — verificat de supraveghetor 3 nov 02:20: NECLAR corect (executant, 3 nov 01:50: lanțul terminat 01:20, cod 0; T = 0,8: 3 „ok” din 4.000, pass@100 1,25/20 → **NECLAR**; T = 0,4: 25 „ok”, pass@100 1,50/20; aceleași 2 probleme (s01, s12); 6,1 % necompilabile, ~92 % rezultat greșit; placa max 1.468 MB / 49 °C; 1177 teste trec)
- verdict verificat (supraveghetor, 3 nov 02:20): **NECLAR, corect.** Recalculat cu estimatorul nedeplasat din (n = 200, c): T = 0,8 → s01 c = 1 → 1 − C(199,100)/C(200,100) = 0,500; s12 c = 2 → 1 − (100·99)/(200·199) = 0,751; suma **1,251/20** (AJUTĂ ≥ 4 ✗, NU AJUTĂ ≤ 1 ✗). T = 0,4: s01 c = 24 → ~1,000, s12 c = 1 → 0,500 → 1,50/20 ✓. Pre-înregistrarea ce181c5 (23:30:25) urcată înainte de pornire (23:30:33) ✓; seturile ascunse nedeschise; placa max 1.468 MB / 49 °C ✓. Citirea mea: 1,25 e practic „nu ajută” — modelul nu „ascunde” soluții pe care le-ar găsi cu multe încercări; 92 % din corpuri rulează dar dau rezultat greșit (logica, nu forma).
- stare veche: in_lucru (executant, 2 nov 23:30: pre-înregistrarea `2026-11-02_cod_pass_k_mare.md` + lanțul `lucru/cascada/S64/s64.py` în ce181c5 (23:30:25), urcate ÎNAINTE de pornire (ora „23:35” scrisă în pre-înregistrare e aproximată greșit; ordinea reală o arată commit-ul); lanțul pornit 23:30:33, proces 23288, pasul (a) T = 0,8, n = 200 rulează; estimat ~1,6 ore)
- stare anterioară: **aprobat**
- tip: placă (scurt, doar scriere de răspunsuri) + procesor
- fereastră: oricând — **de preferat chiar în noaptea 2→3 nov** (placa e liberă după S63); dacă Adrian cere workstation-ul (fereastra OS/GPU), nu pornești
- durată maximă: 2,5 ore în total (placa ~1,5 ore); examenele cu `--lot 2 --memorie-max 6500`; placa sub 7.000 MB și 83 °C
- de ce: S58 și S63 au ieșit NECLAR; biții scad (0,5141 → 0,5004), dar rezolvarea a rămas ~2 % (3/200, 3/163). Înainte să cerem o
  direcție nouă lui Adrian (a treia noapte cu altă rată / date cu funcții și teste / model mai mare), vrem două cifre ieftine:
  (1) dacă modelul *poate* rezolva problemele când încearcă de multe ori (pass@k cu k mare) — dacă da, ajută căutarea/verificatorul (auto-joc, H3),
  nu mai multe ore; (2) de ce pică corpurile (sintaxă, nume interzise, rezultat greșit, timp).
- granițe: examene și notări (2) + unealtă în `unelte/` cu test, dacă e nevoie (5). Fără antrenare, fără `kronos/`, `module/examen_bpb.py`,
  paznic, jurnal, #477, linia română. **Setul ascuns S58 și `ascuns2` NU se deschid din nou** (ambele sunt folosite). `lucru/cod_c1/gpt.pt` doar se citește.
- ce faci:
  1. **Pre-înregistrarea ÎNAINTE de placă:** `docs/preinregistrari/2026-11-03_cod_pass_k_mare.md` (sau cu data zilei), commit + push, cu pragurile de mai jos
     copiate neschimbate și așteptările tale în cifre. Reper: S63 pe setul de probă, n = 10, T = 0,8 → pass@10 = 0/20.
  2. Răspunsurile, starea liniei după ora 20 (`lucru/cod_c1/gpt.pt`, `config/cod_c1_init002.toml`), **setul de PROBĂ** (20 de probleme), într-un dosar nou
     `lucru/kronos_cod/s64/`, câte o rulare, sămânța 0, aceleași `--max-simboluri` ca la S63:
     (a) `examen_cod.py model --set proba --n 200 --temperatura 0.8 --lot 2 --memorie-max 6500 --iesire lucru/kronos_cod/s64/t08.json`, apoi `noteaza`;
     (b) la fel cu `--temperatura 0.4` (`t04.json`), apoi `noteaza`.
     Estimare: ~45 min pe rulare (S63: 200 de corpuri = 103 s + 39 s cutia). Dacă (a) depășește 70 de minute, (b) se face cu `--n 100` și o spui în raport.
  3. pass@k pentru k = 1, 10, 50, 100, 200 din `pe_problema` (n, c) cu același estimator `pass_la_k` (nu schimbi `noteaza`; dacă vrei comanda în unealtă,
     o adaugi ca opțiune nouă cu test). Pe problemă: c din 200 la fiecare temperatură.
  4. De ce pică (procesor, pe corpurile de la (a)): numărul pe stări (ok/picat/interzis/timp/căzut/blocat/eroare) și, pentru „interzis” și „căzut”,
     motivul cel mai des (ce nume/construcție, ce eroare), plus câte corpuri nu se compilează deloc. 3–5 exemple scurte din setul de probă (e public, se poate arăta).
     Fără a deschide seturile ascunse.
  5. `python -m pytest` — toate trec; raport `docs/rapoarte/<data>_<ora>_S64_pass_k_mare.md`; coada → `gata`; commit + push.
- pragurile (pentru T = 0,8, n = 200; supraveghetorul le-a scris înainte, executantul le copiază neschimbate):
  **ÎNCERCĂRILE AJUTĂ** = pass@100 ≥ **4/20** (cel puțin 4 probleme rezolvate măcar o dată din 100);
  **NU AJUTĂ** = pass@100 ≤ **1/20**; altfel **NECLAR**. T = 0,4 și k = 200: doar informație. Setul de probă e mic (20) și a fost folosit la dezvoltare
  (nu la antrenare), deci cifra e un diagnostic, nu un examen; o spunem așa.
- aprobat de: supraveghetor, 2 nov 2026 23:20 (granițele 2 și 5)
- raport: docs/rapoarte/2026-11-03_0150_S64_pass_k_mare.md

### S65 — Kronos-Cod: câte „funcții scurte cu explicație (și teste)” avem deja în codul descărcat? (doar procesor, fără placă, fără antrenare)
- stare: gata — verificat de supraveghetor 3 nov 05:20: DESTUL corect (executant, 3 nov 02:39: rularea 02:32–02:33, cod 0, 103 s; (a) 628.251 funcții, (a+b) 89,9 mil. simboluri, **(a+b+c) 339.425 funcții / 52,9 mil. simboluri → DESTUL**, (a+b+c+d) 29.040 / 7,2 mil.; simbolurile includ explicațiile, (c) nu garantează că funcția merge singură; scurgerea: proba 0 soluții întregi, 1 suprapunere de 13; S58 și ascuns2 0 / 0, SHA neschimbat; 1183 teste trec, 1 sărit)
- tip: procesor (doar citire din date)
- fereastră: oricând — nu ocupă placa; poate rula și ziua de 3 nov
- durată maximă: 2 ore
- de ce: S58, S63 și S64 arată același lucru: modelul `cod_c1` a învățat *forma* codului (doar ~6 % din corpuri nu se compilează), dar nu *logica*
  (~92 % rulează și dau rezultat greșit; chiar cu 200 de încercări rezolvă doar 2 probleme simple din 20). Varianta „date cu funcții și teste”
  (antrenare pe funcții scurte cu explicație, apropiate de forma examenului) are nevoie de cifre înainte să i-o propun lui Adrian: câte astfel de
  funcții avem deja, fără nicio descărcare nouă.
- granițe: 3 (pregătirea datelor din surse deja descărcate) + 5 (unealtă nouă în `unelte/` cu teste). Fără antrenare, fără placă.
- pre-înregistrare: nu e nevoie (nu e antrenare și nici examen); pragurile orientative de mai jos sunt scrise dinainte.
- ce faci:
  1. Unealtă nouă `unelte/kronos_cod/functii.py` (+ teste fără rețea, pe fișiere mici făcute în test). Citește doar `lucru/kronos_cod/complet/cod.jsonl`,
     **doar fișierele folosite la antrenare** (curate, minus `lucru/kronos_cod/scurgere/fisiere_de_exclus.txt` din S53, minus validarea de 1 % după regula din S55).
     Pentru fișierele Python, cu `ast` (codul NU se rulează), găsește funcțiile (de modul sau metode) care au:
     (a) explicație (docstring); (b) corp de 1–30 de linii; (c) doar construcții permise de cutie (refolosești verificarea statică a cutiei, fără să o schimbi);
     (d) marcaj separat: un exemplu `>>>` în explicație, sau numele funcției apare într-un `assert` dintr-un fișier de test din același pachet.
  2. Cifrele: câte funcții la (a), (a+b), (a+b+c), (a+b+c+d); câte simboluri au în total (tokenizerul de cod din S55); câte sunt duplicate exacte
     (după normalizare); primele 20 de pachete după număr; 3–5 exemple scurte (cu pachetul și licența din S46).
  3. Scurgerea: pe **setul de PROBĂ** (public), aceleași reguli ca S53 (suprapuneri de 13 simboluri, soluția întreagă) pe funcțiile găsite. Pe seturile
     ascunse S58 și `ascuns2`: **doar numărul** de potriviri ale soluției de referință întregi, cu unealta S53, fără să arăți vreun text (ambele sunt deja
     folosite; cifra contează pentru un set ascuns viitor).
  4. Lista funcțiilor (fișier, linie, sha) în `lucru/kronos_cod/functii/` (NU în Git). Nu ștergi și nu muți nimic din date.
  5. `python -m pytest` — toate trec; raport `docs/rapoarte/<data>_<ora>_S65_functii.md`; coada → `gata`; commit + push.
- pragurile orientative (scrise de supraveghetor acum, înainte): **DESTUL** = (a+b+c) ≥ **20 mil. simboluri** → o antrenare pe ele are sens fără date noi;
  **PUȚIN** = sub **5 mil.** → varianta ar cere o descărcare nouă (asta e decizia lui Adrian); între → se poate, cu 2–4 repetări ale datelor.
- Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, modelele (`gpt.pt`, #477), linia română, datele din `complet/` (doar citire).
  Nimic descărcat, nimic instalat, nimic din `lucru/` în Git.
- aprobat de: supraveghetor, 3 nov 2026 02:20 (granițele 3 și 5)
- raport: docs/rapoarte/2026-11-03_0239_S65_functii.md
- verdict verificat (supraveghetor, 3 nov 05:20): **DESTUL, corect.** (a+b+c) = 52.873.873 simboluri ≥ 20 mil. (și fără duplicate 51.090.271 ≥ 20 mil.); lanțul se strânge corect 628.251 ≥ 561.784 ≥ 339.425 ≥ 29.040; (d) pe bucăți 10.247 + 16.351 + 2.442 = 29.040 ✓; duplicatele 339.425 − 19.995 = 319.430 ✓. Scurgerea 0 pe ambele seturi ascunse, SHA neschimbat ✓. Rezervele executantului contează: simbolurile includ explicațiile (corpurile sunt mult mai mici), (c) e doar un plafon de sus, 27 % au un singur rând → S67 le măsoară înainte de orice antrenare.

### S66 — Kronos-Cod: direcția după S64 (alegerea lui Adrian)
- stare: **decis de Adrian** (3 nov 11:45, `COMENZI.md` C-60 + C-62, `DECIZII.md` hub): A „funcții” **da** + „școala cu verificator” **da** + memoria de cod **da**;
  „model mai mare” **nu acum** (doar dacă după toate rămâne NECLAR). Ordinea: S69 (exercițiile) → S70 (o noapte pe ele) → S71 (memoria) → S72 (școala) → S73 (Kronos își alege datele).
- stare anterioară: propus — necesită Adrian
- de ce: două nopți pe cod (S58, S63) + diagnosticul S64: rezolvarea rămâne ~2 % și nu crește nici cu 200 de încercări. Încă o noapte cu aceeași
  rețetă ar aduce puțin. Variantele (detaliile exacte și pragurile le scriu după „da” și, la A, după cifrele S65):
  - **A „funcții”** (recomandarea mea): continuare pe linia `cod_c1` din `gpt.pt`, ~6–10 ore, pe un amestec cu funcțiile scurte din S65 (de ex. jumătate
    funcții, jumătate cod obișnuit), apoi examen pe un set ascuns NOU. Fără descărcări dacă S65 iese DESTUL. Ieftin, folosește ce avem.
  - **B „școala cu verificator”** (auto-jocul H3 din strategie): probleme generate foarte ușoare, modelul încearcă de multe ori, încercările corecte
    (verificate de cutie) intră în antrenare, runde scurte. S64 arată că acum găsește rar o soluție, deci ar porni de la nivelurile cele mai simple.
  - **C „model mai mare”**: o linie nouă (~2–3× mai mare, cât încape sub 7.000 MB), mai multe nopți. Cel mai scump; cere „da” separat oricum.
- tip: placă (A și C), placă + procesor (B)
- aprobat de: —

### S67 — Kronos-Cod: funcțiile S65 „cu adevărat ca la examen” — simbolurile corpului, proba definiției în cutie, filtrul celor triviale (doar procesor, fără placă, fără antrenare)
- stare: gata — verificat de supraveghetor 3 nov 08:20: ÎNTRE corect (3.545.959 simboluri de corp: ≥ 3 mil. și < 10 mil.; sumele pe lungimi, pe simboluri și pe licențe dau toate 83.349) (executant, 3 nov 07:04: cod 0 la 06:35:24, 3.456 s; ÎNTRE — autonome 83.349 funcții, 3,55 mil. simboluri de corp; scurgere 0; 1186 teste trec, 1 sărit)
- istoric: in_lucru (executant, 3 nov 05:37: comanda `curata` + 3 teste în dac45c7, 1186 teste trec, 1 sărit; pornită prin cascadă 05:37:45, proces 13496, `--pana-la 08:40` (oprire curată, reluare cu aceeași comandă după 11:30); 319.430 funcții (a+b+c) fără duplicate = S65; cutia ~85 rulări/s cu 16 fire → estimat ~1 oră)
- tip: procesor (doar citire din date + rularea DOAR a definițiilor în cutie, fără apeluri)
- fereastră: **acum, până la 08:45**; dacă nu se termină până la 08:45, o oprești curat și o reiei **după 11:30** (C-57: 09:00–11:30 calculatorul e al lui Adrian)
- durată maximă: 1,5 ore (S65 a rulat 103 s)
- de ce: S65 a ieșit DESTUL (52,9 mil. simboluri la (a+b+c)), dar cu rezervele executantului: explicațiile sunt adesea mai lungi decât corpul,
  (c) nu arată că funcția merge singură, ~27 % au un singur rând de corp. Înainte ca Adrian să aleagă la S66 (varianta A „funcții”), vrem cifra reală:
  câte funcții seamănă cu adevărat cu examenul. Exact pasul propus de executant în raportul S65.
- granițe: 3 (pregătirea datelor din surse deja descărcate) + 5 (unealtă în `unelte/` cu teste). Fără antrenare, fără placă.
- pre-înregistrare: nu e nevoie (nu e antrenare, nici examen); pragurile orientative mai jos, scrise dinainte.
- ce faci:
  1. Extinzi `unelte/kronos_cod/functii.py` cu o comandă nouă (de ex. `curata`) + teste fără rețea pe fișiere mici; pornești de la `lucru/kronos_cod/functii/functii.tsv`
     (doar (a+b+c), fără duplicatele exacte).
  2. (i) **simbolurile doar ale corpului** (fără semnătură și fără docstring), cu tokenizerul de cod S55; (ii) **filtrul celor triviale**: scoți corpurile care sunt doar
     `pass`, `...`, `raise …`, `return` fără valoare, `return <nume sau constantă>` sau doar un apel `super().…`; (iii) **proba definiției**: în cutie (neschimbată), rulezi
     DOAR textul funcției (cu decoratori) ca modul separat, fără să o chemi, și apoi verificezi cu `ast` că toate numele libere din corp sunt parametri, nume locale,
     funcții de bază ale lui Python sau module permise de cutie (fără nume din restul fișierului). Funcțiile care trec (ii) și (iii) = **„autonome”**.
  3. Cifrele, cu și fără (d): funcții și simboluri (întregi și doar corpul) la fiecare pas; distribuția lungimii corpului; primele 20 de pachete; 3–5 exemple scurte autonome,
     cu pachetul și licența. Scurgerea pe „autonome”: aceleași reguli ca la S65 (proba: suprapuneri de 13 + soluția întreagă; seturile ascunse S58 și `ascuns2`: **doar numărul**,
     SHA verificat înainte și după).
  4. Lista (fișier, linie, sha, marcaje) în `lucru/kronos_cod/functii/` (NU în Git). Nu ștergi și nu muți nimic din date.
  5. `python -m pytest` — toate trec; raport `docs/rapoarte/<data>_<ora>_S67_functii_autonome.md`; coada → `gata`; commit + push.
- pragurile orientative (scrise de supraveghetor acum, înainte): **DESTUL PENTRU A** = „autonome” cu **≥ 10 mil. simboluri de corp** → o noapte de 6–10 ore pe ele are sens
  fără date noi (cu 1–3 repetări); **PUȚIN** = sub **3 mil.** → varianta A ar cere date noi sau trecerea la B (decizia lui Adrian); între → A se poate, cu mai multe repetări,
  sau amestecată cu (d). Informativ: câte „autonome” au și (d).
- Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, modelele (`gpt.pt`, #477), linia română, datele din `complet/` (doar citire), cutia (doar o folosești).
  Nimic descărcat, nimic instalat, nimic din `lucru/` în Git.
- aprobat de: supraveghetor, 3 nov 2026 05:20 (granițele 3 și 5)
- raport: docs/rapoarte/2026-11-03_0704_S67_functii_autonome.md

### S68 — Kronos-Cod: funcțiile „autonome” cu regula mai blândă la importuri + câte sunt funcții chemabile, nu metode (doar procesor, fără placă, fără antrenare)
- stare: gata — verificat de supraveghetor 3 nov 14:20: PUȚIN corect (771.546 = 769.447 + 2.099 < 3 mil.; sumele pe lungimi și pe licențe dau 12.648) (executant, 3 nov 12:04: cod 0 la 11:41:37, 123 s; PUȚIN — (autonome + blânde) × chemabile 12.648 funcții, 771.546 simboluri de corp; blânde noi doar 66 (3.968 simb.); metodele = 78 % din 3,55 mil.; scurgere 0; 1190 teste trec, 1 sărit)
- istoric: in_lucru (executant, 3 nov 11:31; comanda `bland` + 4 teste în 985adb0; pornită prin cascadă 11:39:30, proces 6596)
- tip: procesor (doar citire din date și din ieșirile S67 + rularea DOAR a definițiilor în cutie, fără apeluri)
- fereastră: zi, **după 11:30** (C-57: 09:00–11:30 calculatorul e al lui Adrian), terminată până la 18:30
- durată maximă: 1,5 ore (S67 a rulat ~58 min); dacă nu termini până la 18:30, oprești curat și reiei a doua zi după 08:00
- de ce: S67 a ieșit ÎNTRE (3,55 mil. simboluri de corp). Executantul a notat două lucruri care schimbă cifra pentru varianta A de la S66:
  (1) multe funcții au căzut doar pentru că `os`, `sys`, `time`, `np` etc. sunt importate sus în fișier, nu în funcție;
  (2) multe „autonome” sunt metode sprijinite pe `self`/`ctx`, care nu se pot chema cu date ca la examen. Vrem ambele cifre înainte ca Adrian să aleagă.
- granițe: 3 (pregătirea datelor din surse deja descărcate) + 5 (unealtă în `unelte/` cu teste). Fără antrenare, fără placă.
- pre-înregistrare: nu e nevoie (nu e antrenare, nici examen); pragurile orientative mai jos, scrise dinainte.
- ce faci:
  1. Extinzi `unelte/kronos_cod/functii.py` (de ex. `curata --bland` sau o comandă nouă `bland`) + teste fără rețea pe fișiere mici. Pornești de la
     ieșirile S67 (`lucru/kronos_cod/functii/autonome.tsv`, `cutie.jsonl`) și de la funcțiile care au trecut pasul (iii) (definiția în cutie).
  2. **Regula blândă:** un nume liber din corp e acceptat și dacă este un modul (sau un alias de modul, ex. `np`) **importat la nivelul de sus al aceluiași fișier**
     și modulul e **permis de cutie** (`MODULE_DE_BAZA` din `_cutie_interior.py`, neschimbat). Funcția „blândă” = corpul + rândurile de import necesare, puse
     deasupra; o rulezi din nou DOAR ca definiție în cutie (fără s-o chemi). Nume din restul fișierului (alte funcții, constante, clase) rămân interzise.
  3. **Chemabile:** dintre „autonome” și „blânde”, numeri separat funcțiile de nivel de sus / `@staticmethod` (fără `self`/`cls`/`ctx` ca prim parametru și fără
     atribute pe primul parametru folosit ca obiect) — acestea seamănă cu examenul. Metodele se raportează separat.
  4. Cifrele (funcții, simboluri doar corp), cu și fără (d): autonome S67 / blânde / autonome+blânde × chemabile / metode; lungimea corpului la „chemabile”;
     primele 10 pachete; 3–5 exemple scurte chemabile, cu pachetul și licența. Scurgerea pe mulțimea nouă: aceleași reguli ca la S65/S67 (proba: suprapuneri
     de 13 + soluția întreagă; seturile ascunse S58 și `ascuns2`: **doar numărul**, SHA verificat înainte și după).
  5. Lista în `lucru/kronos_cod/functii/` (NU în Git). Nu ștergi și nu muți nimic din date.
  6. `python -m pytest` — toate trec; raport `docs/rapoarte/<data>_<ora>_S68_functii_blande.md`; coada → `gata`; commit + push.
- pragurile orientative (scrise de supraveghetor acum, înainte), pe **(autonome + blânde) × chemabile**, simboluri de corp:
  **DESTUL PENTRU A** ≥ **10 mil.**; **PUȚIN** < **3 mil.**; între → A doar cu repetări sau amestecată cu pasul (iii) din S67 (17,9 mil.). Informativ: cât din cifră vin din metode.
- Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, modelele (`gpt.pt`, #477), linia română, datele din `complet/` (doar citire), cutia (doar o folosești,
  fără module noi permise). Nimic descărcat, nimic instalat, nimic din `lucru/` în Git. Nu pornești nimic pe placă.
- aprobat de: supraveghetor, 3 nov 2026 08:20 (granițele 3 și 5)
- raport: docs/rapoarte/2026-11-03_1204_S68_functii_blande.md

### S69 — Kronos-Cod C-60 pasul A: setul de exerciții „antet + explicație → corp” + amestecul pentru noaptea S70 (doar procesor, fără placă, fără antrenare)
- verdict supraveghetor (3 nov 17:20): **gata, corect.** Verificat: 25 % cerut → 24,999 % ieșit; repetarea max 5 / 9 (plafon 6 / 12); scurgerea scoasă (proba 1, `ascuns2` 3, S58 0), SHA neschimbat; validarea identică cu S58/S63. Doar 13 exerciții deoparte au test care rulează → S72 își face testele altfel. Întrebarea (a)/(b) → (b), vezi S70.
- stare: gata (executant, 3 nov 14:43: cod 0, 14:41–14:42; 313.910 exerciții la antrenare (50,6 mil. simb.), k = 4,04 (restul max 5, autonomele max 9); amestecul 970,8 mil. simb. = **24,999 %** exerciții, 29 fișiere + validarea copiată identic; deoparte 80 pachete / 5.516 exerciții, (d) 603, doar **13** trec în cutie; scurgere: proba 1, ascuns2 3 (suprapunere 13, 0 întregi), S58 0, SHA neschimbat; `config/cod_c1_ex.toml` + copia `lucru/cod_c1_ex/gpt.pt` (identică) verificate pe procesor; 1195 teste trec, 1 sărit. **Înainte de S70:** cu `nume = "cod_c1"`, `--ore 8` nu antrenează nimic (jurnalul are 20 de ore → `--ore 28`) și lock/placa/rezultat.json se scriu în `lucru/cod_c1/` — variantele (a)/(b) în raport)
- tip: procesor (doar citire din datele deja descărcate și din ieșirile S65/S67/S68; cutia doar pentru verificarea celor cu exemplu/test)
- fereastră: zi, **acum, până la 18:30** (ca S70 să poată porni la 19:00). Dacă nu e gata la 18:30, continui (e doar procesor), iar S70 pornește când S69 e `gata`, dar cel târziu la 22:00; după 22:00 S70 trece pe noaptea următoare.
- durată maximă: 3 ore
- de ce: Adrian a ales calea A+B+C+D (C-60). S67/S68 arată că funcțiile „ca la examen” sunt puține (autonome 3,55 mil. simboluri de corp, chemabile doar 0,77 mil.),
  deci exercițiile se fac din toate funcțiile cu explicație care trec cutia (S65, (a+b+c) fără duplicate: 319.430), cu cele autonome (S67/S68) puse de 2 ori, și se amestecă cu cod obișnuit.
- granițe: 3 (pregătirea datelor din surse deja descărcate) + 5 (unealtă în `unelte/` cu teste). Aprobat și de Adrian (C-60).
- ce faci:
  1. Extinzi `unelte/kronos_cod/functii.py` cu o comandă nouă (de ex. `exercitii`) + teste fără rețea pe fișiere mici.
  2. **Exercițiul** = textul funcției în forma „antet (decoratori + semnătură) + explicație (docstring) + corp”, cu tokenizerul de cod S55, urmat de simbolul de sfârșit de fișier (32764).
     Mulțimea: (a+b+c) din S65 fără duplicate (319.430); funcțiile autonome + blânde din S68 (83.415) **de 2 ori**. Scoți orice funcție cu suprapunere de 13 cu setul de probă
     (la S65 a fost 1) și orice potrivire cu seturile ascunse S58 și `ascuns2` (doar numărul, SHA verificat înainte și după).
  3. **Exercițiile ținute deoparte:** 2 % din pachete (alese cu sămânța 0, întregi pe pachet, ca să nu existe aproape-dubluri), NU intră la antrenare — doar pentru măsurare la S70.
     Dintre cele cu exemplu/test (d) ținute deoparte: verifici în cutie (neschimbată) că exemplul rulează cu corpul original și le notezi (vor servi la S72).
  4. **Amestecul** în `lucru/kronos_cod/exercitii/`: `antrenare_NNNNN.bin` (uint16, formatul pe care îl citește `module/date_cod.py`, neschimbat) cu **25 % din simboluri exerciții**
     și 75 % cod obișnuit din `lucru/kronos_cod/simboluri/antrenare_*.bin`, amestecate pe bucăți de 512 (sămânța 0), cât pentru **8 ore** la viteza S63 (~32.000 simb/s ≈ 0,92 mld. simboluri,
     calculează din jurnalul S63). Exercițiile se repetă cel mult **6 ori** fiecare (autonomele: dublul); dacă 25 % ar cere mai mult, scazi procentul și scrii cât a ieșit.
     `validare_*.bin` = exact cele de la S58/S63 (copie sau legătură), ca biții de validare să fie comparabili. Nu ștergi și nu muți nimic din `simboluri/` sau `complet/`.
  5. **Configurarea S70:** `config/cod_c1_ex.toml` = `config/cod_c1_init002.toml` (cea de la S63), schimbat DOAR: `[porturi.date] director = "lucru/kronos_cod/exercitii"`,
     `cale_stare = "lucru/cod_c1_ex/gpt.pt"`, eticheta și comentariul de sus. **Copiezi** `lucru/cod_c1/gpt.pt` (+ starea liniei) în `lucru/cod_c1_ex/` — originalul rămâne neatins (e rezerva).
     Verifici pe procesor, fără placă, că `DateCod` citește dosarul nou și că modelul încarcă starea copiată (un pas, fără salvare).
  6. Cifrele: exerciții (funcții, simboluri; autonome / restul; cu (d)), repetarea medie și maximă, procentul real din amestec, cele ținute deoparte, scurgerea. Lista în `lucru/` (NU în Git).
  7. `python -m pytest` — toate trec; raport `docs/rapoarte/<data>_<ora>_S69_exercitii.md`; coada → `gata`; commit + push.
- Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, `module/date_cod.py`, cutia, modelele (`lucru/cod_c1/gpt.pt` doar se citește/copiază), #477, linia română.
  Nimic descărcat, nimic instalat, nimic din `lucru/` în Git. Nu pornești nimic pe placă.
- aprobat de: **Adrian (COMENZI.md C-60, 3 nov 2026 11:45)**; instrucțiunile: supraveghetor, 3 nov 2026 14:20
- raport: docs/rapoarte/2026-11-03_1443_S69_exercitii.md

### S70 — Kronos-Cod C-60 pasul B: o noapte pe exerciții (8 ore, continuare din `gpt.pt`, pe copia `lucru/cod_c1_ex/`), apoi examenele pe `ascuns2` (placa)
- stare: gata (executant, 4 nov 04:38: lanțul cod 0, terminat 04:00:51; validarea 0,50742, `ascuns2` pass@10 2/163 → **NU AJUTĂ**; placa max 5.922 MB / 62 °C; 1195 teste trec, 1 sărit)
- verificat de supraveghetor (4 nov 05:20): **corect, NU AJUTĂ** — 2/163 ≤ 4/163; validarea 0,50742 ≤ 0,510 (deci nu STRICĂ), dar mai proastă decât S63 (0,50041). Linia `cod_c1_ex` nu se continuă; S72 pornește din S63.
- stare anterioară: in_lucru (executant, 3 nov 19:11: config `nume = "cod_c1_ex"` (1195 teste trec, 1 sărit); pre-înregistrarea `2026-11-03_cod_c1_exercitii.md`;
  lanțul `lucru/cascada/S70_proba/s70.py` pornit 19:09:06 (proces 18624): pasul 0 pe procesor „pași 590110, minute 1200,02, rata 6e-05 → BUNĂ”,
  apoi `--ore 8` („orele 1–8”, linia `cod_c1_ex`), placa 5.918 MB / 58 °C; sfârșit estimat ~03:30 + examenele (i)–(iv) ~45 min; niciun pas nou după 05:45)
- stare anterioară: **aprobat** — pornește DOAR după S69 `gata` (gata, 14:43) și după ce pre-înregistrarea e urcată
- tip: placă
- fereastră: **noapte, 3→4 nov, de la 19:00**. **Comanda lui Adrian C-63 (3 nov 16:30): tot lanțul (antrenare + examene) se termină sau se oprește curat (reluabil) până la 06:45**;
  între 07:00 și ~09:30 nimic pe placă și nimic lung pe procesor (fereastra lui Adrian). Deci: pornești cel târziu la **21:30**; dacă pornești după 19:30, scazi orele de antrenare
  ca antrenarea să se termine până la ~05:30 (de ex. pornire 20:30 → `--ore 7`) și scrii orele reale în pre-înregistrare și în raport. Dacă la 05:45 examenele nu sunt gata,
  le oprești curat, notezi ce lipsește și le termini după ~09:30, înainte de S71.
- **HOTĂRÂREA supraveghetorului la întrebarea din raportul S69 (3 nov 17:20): varianta (b).** În `config/cod_c1_ex.toml` schimbi și `nume = "cod_c1"` → `nume = "cod_c1_ex"`
  (singura schimbare în plus; graniță 1: rulare pe linia existentă, pe o copie) și rulezi cu **`--ore 8`** (sau mai puțin, după regula de mai sus). Zăvorul, `placa_*.csv`, `rezultat.json`
  merg toate în `lucru/cod_c1_ex/`; `lucru/cod_c1/` rămâne neatins (doar citire), inclusiv `rezultat.json` de la S63. Înainte de pornire verifici pe procesor (fără placă) că, cu numele nou,
  modelul încarcă tot starea copiată (590.110 pași, 1.200 de minute) și rata e cea fixă 6·10⁻⁵ (fără încălzire de la zero); în log TREBUIE să apară pașii ~590.110 la pornire —
  dacă apare pasul 0 sau încălzire nouă → nu pornești, `oprit`. Faptul că jurnalul arată „orele 1–8” pe linia `cod_c1_ex` e în regulă; scrie în raport că e continuarea liniei `cod_c1` (20 h + 8 h).
  Testele trebuie să treacă după schimbarea din config (commit separat, înainte de pre-înregistrare).
- durată maximă: 8 ore antrenare + examenele (~1 oră); placa sub 7.000 MB și 83 °C; examenele cu `--lot 2 --memorie-max 6500`
- de ce: C-60 B. Aceeași rețetă ca S63 (rata fixă 6·10⁻⁵, fără încălzire nouă — cum continuă starea liniei), schimbăm DOAR datele: 25 % exerciții. Așa se vede efectul datelor.
- ce faci:
  1. **Pre-înregistrarea ÎNAINTE de pornire:** `docs/preinregistrari/2026-11-03_cod_c1_exercitii.md`, commit + push, cu pragurile de mai jos copiate neschimbate, procentul real de exerciții
     din S69 și așteptările tale în cifre. Reperul = S63 (10 ore pe cod obișnuit): validarea 0,5004; `ascuns2` pass@10 = 3/163.
  2. 8 ore prin `unelte/cascada.py` cu `config/cod_c1_ex.toml` (`nume = "cod_c1_ex"`, `--ore 8`, vezi HOTĂRÂREA de mai sus). În log TREBUIE să apară că pornește din starea liniei copiate (`lucru/cod_c1_ex/`, ~590.110 pași); dacă pornește de la zero
     sau scrie în `lucru/cod_c1/` → oprești, `oprit`.
     (iv) se notează cu atenția din raportul S69: fișierele din care vin exercițiile ținute deoparte sunt în codul obișnuit — cifra arată forma exercițiului, nu cod nevăzut.
  3. Examenele, o singură dată, ca la S63: (i) biți pe octet pe validarea întreagă; (ii) `ascuns2`: `examen_cod.py model --set ascuns --dosar lucru/kronos_cod/ascuns2` + `noteaza`,
     163 × 10, temperatura 0,8, sămânța 0 → pass@1, pass@10 (Adrian a cerut același set ca la S63, ca să fie comparabil; setul nu se schimbă și nu se arată); (iii) setul de probă 20 × 10, informativ;
     (iv) informativ: biți pe octet doar pe corpurile exercițiilor ținute deoparte (S69 pasul 3), pentru `lucru/cod_c1_ex/gpt.pt` și pentru `lucru/cod_c1/gpt.pt` (S63), ca să se vadă ce a învățat.
- pragurile (scrise de supraveghetor acum, înainte; executantul le copiază neschimbate), N = 163:
  **AJUTĂ** = pass@10 ≥ **8/163** (~5 %) **și** validarea ≤ **0,510** (codul obișnuit nu se strică); **NU AJUTĂ** = pass@10 ≤ **4/163**; **STRICĂ** = validarea > 0,510 (oricât pass@10);
  altfel **NECLAR**. O sămânță, o noapte; diferența 3 → 5 e în zgomot și o spunem așa.
- Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, #477, linia română, `lucru/cod_c1/` (doar citire), setul ascuns S58. Nimic descărcat. Raport `docs/rapoarte/<data>_<ora>_S70_cod_c1_exercitii.md`; coada → `gata`; commit + push.
- aprobat de: **Adrian (COMENZI.md C-60, 3 nov 2026 11:45)**; instrucțiunile și pragurile: supraveghetor, 3 nov 2026 14:20
- raport: docs/rapoarte/2026-11-04_0438_S70_cod_c1_exercitii.md

### S71 — Kronos-Cod C-60 pasul D: memoria de cod („rege / regat”) — indexul funcțiilor + căutarea celor mai asemănătoare (procesor; placa doar o măsurare scurtă pe setul de PROBĂ)
- stare: gata (executant, 4 nov 10:34: NU AJUTĂ pe probă — cu memorie S63 0/20, S70 0/20; fără S63 0/20, S70 1/20; scurgere 0; 1198 teste trec, 1 sărit)
- stare anterioară 2: in_lucru (executant, 4 nov 10:11: pașii 1–2 GATA b1bfe8d — `unelte/kronos_cod/memorie.py` + 3 teste, 1198 trec, 1 sărit; indexul 313.910/313.910 exerciții, 58 s; scurgerea: proba 0 scoase (53 funcții alese, 2,65 pe problemă), ascuns2 0 scoase, SHA neschimbat; pasul 3: lanțul `lucru/cascada/S71_proba/s71.py` pornit 10:10:43 prin cascadă (proces 19716): S63 fără/cu, apoi S70 fără/cu, doar proba, ≤ 30 min)
- stare anterioară: **aprobat** — după S70 `gata` (sau `oprit`)
- tip: procesor (+ ≤ 30 min pe placă, doar setul de probă)
- notă supraveghetor (4 nov 05:20, după S70 = NU AJUTĂ): la pasul 3 măsori **întâi S63** (`lucru/cod_c1/gpt.pt`) cu și fără memorie — e modelul de referință de acum; S70 (`lucru/cod_c1_ex/gpt.pt`) doar dacă mai încape în cele 30 de minute.
- fereastră: zi, **4 nov, după fereastra lui Adrian (C-63: 07:00–~09:30; pornești doar după 09:30 sau după ce Adrian anunță în hub că a terminat), până la 18:30**.
  Dacă S70 a lăsat examene neterminate (oprite la 05:45), întâi le termini pe acelea.
- durată maximă: 3 ore
- ce faci:
  1. Unealtă nouă `unelte/kronos_cod/memorie.py` + teste fără rețea: index pe procesor al exercițiilor S69 (fără cele ținute deoparte), căutare după antet + explicație
     (pornește de la căutarea în text pe procesor care există deja în proiect; fără modele străine, fără descărcări). Pentru o problemă: cele mai asemănătoare **2–4** funcții, puse
     ca text înaintea problemei, cât încape în contextul de 512 (problema are întâietate).
  2. Verificarea scurgerii: pentru fiecare din cele 20 de probleme de probă, niciuna din funcțiile găsite nu conține soluția de referință (suprapunere de 13); scrii câte au fost scoase.
     Pe `ascuns2`: doar numărul, fără să-l arăți.
  3. Măsurarea scurtă pe placă, DOAR pe setul de probă (20 × 10, temperatura 0,8, sămânța 0, `--lot 2 --memorie-max 6500`): modelul S70 cu și fără memorie (și S63 cu și fără, dacă încape în 30 min).
     Pe `ascuns2` NU măsori încă — aceea e o sarcină separată, după ce vedem proba.
  4. `python -m pytest` — toate trec; raport `docs/rapoarte/<data>_<ora>_S71_memorie_cod.md`; coada → `gata`; commit + push.
- Nu atingi `kronos/`, examenul, paznicul, jurnalul, cutia, modelele (doar citire). Nimic descărcat, nimic instalat.
- aprobat de: **Adrian (COMENZI.md C-60, 3 nov 2026 11:45)**; instrucțiunile: supraveghetor, 3 nov 2026 14:20
- raport: docs/rapoarte/2026-11-04_1034_S71_memorie_cod.md

### S72 — Kronos-Cod C-60 pasul C: școala de cod (Kronos își scrie soluții, cutia le verifică, învață doar din cele corecte)
- stare: **împărțit în S72a + S72b** (supraveghetor, 4 nov 05:20, după verdictul S70 = NU AJUTĂ). De ce așa: S69 a arătat că doar 13 din 441 de exerciții ținute deoparte au
  un test care rulează în cutie — școala n-are încă destule exerciții cu test. Întâi le facem (S72a, procesor), apoi o rundă a școlii la noapte (S72b, placa).
- aprobat de: Adrian în principiu (COMENZI.md C-60 C, 3 nov 2026 11:45)

### S72a — Școala de cod, pregătirea: exercițiile CU TEST care rulează în cutie + împărțirea școală / verificare (doar procesor, fără placă, fără antrenare)
- stare: gata (executant, 4 nov 11:13: cod 0, 11:10–11:12, 123 s; **889 exerciții cu test bune** (811 autonome, 246 pachete); **P_verif 200** (122 pachete), **P_scoala 689** (124 pachete; fluids 138, chemicals 104) → S72b poate porni; scurgere: proba 0, S58 0, ascuns2 1 scos (13 simb.), SHA neschimbat; `noteaza` pe 5: original 5/5 ok, `return None` 5/5 picat; 14 scoase pentru că trec și cu `return None`; 1207 teste trec, 1 sărit)
- tip: procesor
- fereastră: zi, 4 nov, după S71, **până la 18:30** (trebuie `gata` înainte de 19:00, altfel S72b nu pornește în noaptea asta)
- durată maximă: 3 ore
- ce faci:
  1. Unealtă: comanda nouă `teste` în `unelte/kronos_cod/functii.py` (sau `unelte/kronos_cod/scoala.py`) + teste fără rețea pe fișiere mici. Pornește de la ce ai făcut la S69 pentru cele 603 cu (d),
     dar pe **toate cele 27.581 de exerciții de antrenare cu (d)** (exemplu `>>>` sau assert), din `lucru/kronos_cod/exercitii/`. **Repară scăparea din S69** (exemplele `>>>` pe mai multe rânduri,
     cu `...`), apoi pentru fiecare exercițiu: programul = importurile de sus (ca la S68 „blând”) + funcția + testul; testul trebuie să cheme funcția cu argumente și să aibă cel puțin un `assert` cu rezultat.
  2. Rulezi fiecare program în cutie (`unelte/kronos_cod/cutie.py`, neschimbată) **cu corpul original**. Păstrezi doar exercițiile la care corpul original trece testul = „exerciții cu test bune”.
     Scrii câte au căzut și de ce (NameError, import nepermis, timp, sintaxă), ca la S69.
  3. Scurgerea, după regulile S53/S69: scoți orice exercițiu care se suprapune (13 simboluri) cu setul de probă, `ascuns2` sau `examen_ascuns` S58; pentru seturile ascunse doar numărul.
     Cele 5.516 ținute deoparte la S69 NU intră (rămân pentru măsurare).
  4. **Împărțirea pe pachete** (ca la S69, sămânța 0, un pachet întreg merge doar într-o parte): **P_verif** = cel puțin 200 de exerciții (dacă se poate exact 200, din cât mai multe pachete diferite),
     **P_scoala** = restul. Scrii în `lucru/kronos_cod/scoala/` câte un dosar pentru fiecare, **în formatul pe care îl citește `examen_cod.py`** (ca să-l poți folosi cu `--dosar`, cu testul exercițiului
     ca judecător), plus `scoala.json` cu cifrele. Verifici pe procesor, pe 5 exerciții, că `examen_cod.py noteaza` dă „ok” pentru corpul original și „picat” pentru un corp greșit.
  5. `python -m pytest` — toate trec; raport `docs/rapoarte/<data>_<ora>_S72a_scoala_teste.md`: câte exerciții cu test bune (total, autonome, din câte pachete), mărimile P_verif / P_scoala,
     căderile pe motive, scurgerile; coada → `gata`; commit + push.
- Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, cutia, modelele, seturile ascunse (doar numărul la scurgere). Nimic descărcat, nimic instalat.
- aprobat de: **Adrian (COMENZI.md C-60 C, 3 nov 2026 11:45)**; instrucțiunile: supraveghetor, 4 nov 2026 05:20 (granițele 3 și 5: pregătirea datelor deja descărcate, unealtă nouă)
- raport: docs/rapoarte/2026-11-04_1113_S72a_scoala_teste.md

### S72b — Școala de cod, runda 1: Kronos (S63) scrie soluții la P_scoala, cutia le verifică, învață doar din cele corecte; măsurat pe P_verif (placa, noaptea 4→5 nov)
- verificat de supraveghetor (4 nov 20:20): pre-înregistrarea urcată înainte de pornire (S75, 14:30) ✓; validarea întreagă 0,51303 > 0,510 → **STRICĂ** ✓ (R = 18: +4 față de B = 14, zgomot; `ascuns2` 4/163 < 6). Școala, cum e, nu avansează codul → se aplică C-64 (S76, S77). Rundele 2+ nu le pun acum; `lucru/cod_c1_sc/` rămâne, nu se șterge.
- stare: gata (executant, 4 nov 20:04): **STRICĂ** — validarea întreagă 0,51303 > 0,510 (S63 0,50041); R = 18 din 200 (B = 14; pass@1 0,023, 46 ok); `ascuns2` 4/163; proba 0/20. Lanțul 19:10–19:58, cod 0, placa max 5.885 MB / 61 °C; S63 SHA neschimbat; pre-înregistrarea închisă cu verdictul; 1212 teste trec, 1 sărit.
- (istoric) stare: in_lucru (executant, 4 nov 19:01; de la pasul 3, după nota (e))
- pornit: 4 nov 19:10 prin cascadă (proces 2516, lanțul `lucru/cascada/S72b_proba/s72b.py`). Pregătire: comanda nouă `scoala.py amestec` (+ teste, db827ca) →
  `runda1/amestec/` (109 corpuri × 8 = 98.000 simboluri + 192 bucăți de cod obișnuit = 196.304; validare copiată); copia `lucru/cod_c1_sc/gpt.pt`, SHA-256 la amândouă
  3916b8f4…0a99 (originalul neschimbat); `config/cod_c1_sc.toml` cu `pasi_max = 48` (opțiunea de pași a modelului = o trecere: 196.304 / (8 × 512), rotunjit la 12).
  Pasul 0 pe procesor: 590.110 pași, rata 6·10⁻⁵ → bună. Învățarea: 48 de pași (590.158 total), 1,0 treceri, placa 5.332 MB, gata 19:11; urmează examenele (i)–(iv).
- (istoric) stare: **aprobat** — pornește DOAR dacă S72a e `gata` cu **P_scoala ≥ 500** exerciții cu test bune și după ce pre-înregistrarea e urcată. Dacă P_scoala < 500: nu pornești, scrii în coadă
  „S72b nu pornește: P_scoala = N” și placa rămâne liberă (decid eu la trecerea următoare).
- tip: placă (+ procesor pentru cutie)
- fereastră: noapte, **4→5 nov, de la 19:00** (cel târziu 21:00); totul se termină până la 07:00
- durată maximă: ~6 ore în total; placa sub 7.000 MB și 83 °C; generarea și examenele cu `--lot 2 --memorie-max 6500`
- de la ce model: **S63** (`lucru/cod_c1/gpt.pt`, validarea 0,50041) — e mai bun pe codul obișnuit decât S70 (0,50742), iar exercițiile S70 n-au ajutat. Copiezi `lucru/cod_c1/gpt.pt`
  în `lucru/cod_c1_sc/gpt.pt` (verifici suma SHA-256 a ambelor; originalul rămâne neatins, doar citit). Config nouă `config/cod_c1_sc.toml` = `cod_c1_init002.toml` cu `nume = "cod_c1_sc"`,
  `cale_stare = "lucru/cod_c1_sc/gpt.pt"`, `director` = amestecul de la pasul 3, eticheta (commit separat, testele trec, înainte de pre-înregistrare). Graniță 1: rulare pe linia existentă, pe o copie.
- ce faci, un singur lanț prin `unelte/cascada.py`:
  0. **Reperul:** S63 (`lucru/cod_c1/gpt.pt`) pe P_verif, 10 încercări pe exercițiu, temperatura 0,8, sămânța 0 → pass@1, pass@10 = **B** (câte exerciții din P_verif rezolvă măcar o dată).
     Dacă B < 10 (sub 5 % din 200): te oprești curat după acest pas — „școala n-are din ce învăța” e un rezultat; raport, coada → `gata` cu verdictul NU POATE ÎNCEPE.
  1. **Școala:** S63 scrie **8 încercări** pe fiecare exercițiu din P_scoala (cel mult 1.500 de exerciții, alese cu sămânța 0 dacă sunt mai multe; temperatura 0,8, sămânța 1), cel mult **3 ore** pe placă —
     dacă timpul nu ajunge, te oprești la ce s-a scris și notezi câte.
  2. **Cutia** (procesor): fiecare încercare cu testul exercițiului ei. Păstrezi doar corpurile **corecte**, fără duplicate (după spații). Scrii: câte corecte, la câte exerciții, și câte sunt
     **identice cu corpul original** (după spații) — partea „copiată din memorie”.
     Dacă sunt mai puțin de **100** de corpuri corecte diferite: nu antrenezi; sari la pasul 4 doar cu (i) și scrii verdictul PREA PUȚINE.
  3. **Învățarea:** amestecul = fiecare corp corect, cu antetul și explicația lui în față (exact ca exercițiul), repetat de **8 ori**, + tot atâtea simboluri de cod obișnuit din
     `simboluri/antrenare_*.bin` (alese cu sămânța 0); amestecat. O singură trecere prin el (cât durează — probabil minute), cu rata fixă a liniei 6·10⁻⁵, din `lucru/cod_c1_sc/gpt.pt`.
     Dacă unealta cere ore întregi, folosește opțiunea de pași sau de minute dacă există; dacă nu există, cel mult `--ore 1` și scrii în raport câte treceri au fost. Pornește din starea copiată
     (verifici înainte pe procesor, ca la S70 pasul 0: starea copiată are **590.110 pași**, rata 6·10⁻⁵, fără încălzire de la zero; altfel nu antrenezi, `oprit`).
  4. **Examenele, o singură dată, pe starea de după învățare:** (i) biți pe octet pe validarea întreagă (5.686 fișiere, ca la S63/S70); (ii) P_verif 200 × 10, la fel ca la pasul 0 → pass@1, pass@10 = **R**;
     (iii) `ascuns2` 163 × 10, temperatura 0,8, sămânța 0 (ca la S63/S70; setul nu se schimbă și nu se arată); (iv) setul de probă 20 × 10, informativ.
- **pragurile** (scrise de supraveghetor acum, înainte; executantul le copiază neschimbate în pre-înregistrare), N = 200 (P_verif), B = reperul de la pasul 0:
  **AJUTĂ** = R ≥ B + 10 **și** validarea ≤ **0,505**; **NU AJUTĂ** = R ≤ B + 3; **STRICĂ** = validarea > 0,510 sau R ≤ B − 5; altfel **NECLAR**.
  `ascuns2` se raportează alături (S63: 3/163, S70: 2/163); „ajută și pe examen” doar dacă `ascuns2` ≥ **6/163**. O sămânță, o rundă; o diferență de ±3 din 200 e zgomot și o spunem așa.
- **Pre-înregistrarea ÎNAINTE de pornire:** `docs/preinregistrari/2026-11-04_cod_c1_scoala_r1.md`, commit + push: pragurile de mai sus, mărimile reale P_verif / P_scoala din S72a,
  așteptările tale în cifre (B, câte corecte, R, cât din corecte sunt copiate din memorie) și ce ar infirma ideea.
- Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, cutia, #477, linia română, `lucru/cod_c1/` și `lucru/cod_c1_ex/` (doar citire), seturile ascunse. Nimic descărcat.
  Raport `docs/rapoarte/<data>_<ora>_S72b_scoala_runda1.md`; coada → `gata`; commit + push. Rundele următoare (2, 3…) le scriu eu după verdict.
- aprobat de: **Adrian (COMENZI.md C-60 C, 3 nov 2026 11:45)**; instrucțiunile și pragurile: supraveghetor, 4 nov 2026 05:20
- raport: docs/rapoarte/2026-11-04_2004_S72b_scoala_runda1.md
- **notă supraveghetor (4 nov 11:20, după S72a = 689 ≥ 500, condiția îndeplinită):**
  (a) **Pasul 0 (reperul B) se face ziua, ca S74.** Dacă S74 e `gata`, la noapte NU repeți pasul 0: iei B din `lucru/kronos_cod/scoala/reper_s63/nota.json` (aceiași parametri, măsurarea se repetă identic — vezi controlul din S71)
  și îl scrii ca atare în pre-înregistrare. Dacă B < 10, S72b nu pornește (verdictul NU POATE ÎNCEPE, scris de S74). Dacă S74 n-a apucat să se termine până la 18:30, faci pasul 0 la noapte, ca până acum.
  (b) **Pasul 2, o regulă în plus (pentru că explicația conține adesea chiar rezultatul exemplului — punctul 2 din raportul S72a):** un corp „corect” care e doar `return <valoare fixă>`
  (un singur rând; în arbore un `Return` cu o constantă sau o listă/tuplă/dicționar doar de constante) NU intră în învățare, ca școala să nu răsplătească ghicitul rezultatului. Numeri câte au fost scoase
  și scrii cifra în raport și în pre-înregistrare (așteptarea ta). Pragul de 100 de corpuri corecte diferite se socotește DUPĂ această regulă.
  (c) Concentrarea pe `fluids`/`chemicals` (35 % din P_scoala) rămâne cum e la runda 1 (o raportezi: câte corecte vin din ele); la runda 2 decid o limită pe pachet după rezultat.
- **notă supraveghetor (4 nov 14:20, după S74 = B 14/200, verificat de mine: 14 ≥ 10, deci S72b poate porni; praguri cu B = 14: AJUTĂ R ≥ 24 și validarea ≤ 0,505, NU AJUTĂ R ≤ 17, STRICĂ validarea > 0,510 sau R ≤ 9):**
  (d) Pre-înregistrarea se scrie acum, înainte de **S75**, care face ziua pașii 1 și 2. La noapte urmezi regula din S75 („la noapte”): DESTULE → începi de la pasul 3 cu `runda1/corecte.jsonl`; PREA PUȚINE → nu pornești; S75 neterminat → continui pasul 1.
- **notă supraveghetor (4 nov 17:20, după S75, verificat de mine: 109 corpuri corecte diferite ≥ 100 → DESTULE):**
  (e) La noapte pornești S72b de la **pasul 3** cu `lucru/kronos_cod/scoala/runda1/corecte.jsonl` (109 corpuri), B = 14 din `reper_s63/nota.json`; pragurile din pre-înregistrare rămân neschimbate.
  Scrii în raport și temperatura maximă a plăcii (la S75 n-a fost notată în timpul rulării).

### S73 — Kronos-Cod C-62 pasul E: Kronos își alege datele (nota fiecărei bucăți după cât îl mai învață) — o noapte pe datele alese vs. o noapte pe date la întâmplare
- stare: propus — aprobat de Adrian în principiu (C-62); vine după S70 (și S72, după ordinea din C-60/C-62); instrucțiunile și pragurile după verdictul S70
- notă supraveghetor (4 nov 05:20): rămâne `propus` până la verdictul S72b; atunci scriu instrucțiunile (pornind tot din S63, nu din S70).
- notă supraveghetor (4 nov 20:20): S72b = STRICĂ → după C-64 placa trece pe română (S76, S77). S73 rămâne `propus`, în așteptare; nu pornește fără o nouă decizie (a lui Adrian sau după S76/S77).
- tip: placă (două nopți) + procesor

### S74 — Școala de cod: reperul S63 pe P_verif (pasul 0 din S72b, mutat ziua) — examen pe placă, ~20–40 min
- stare: gata (executant, 4 nov 12:11): **B = 14 din 200** (pass@10 0,070, pass@1 0,013; 26 ok din 2.000); fără `return <valoare fixă>` (1 din 26): B = 13. B ≥ 10 → S72b poate porni la noapte, cu B din `nota.json`. S63 SHA-256 neschimbat; 1207 teste trec.
- pornit: 4 nov 11:31 prin cascada (`examen_cod.py model`, echivalentul lui `raspunsuri`); SHA-256 S63 înainte: 3916b8f476ea426f795784eb99bed360e468465e6f1e9ac2363db83d16bc0a99
- tip: placă (doar examen, fără antrenare)
- fereastră: zi, **4 nov, cât de curând (S72a e `gata`), terminat până la 18:30**; dacă la 18:30 nu e gata, se oprește curat și pasul 0 rămâne pentru S72b la noapte
- durată maximă: 1 oră; placa sub 7.000 MB și 83 °C
- de ce: aflăm înainte de noapte dacă școala are din ce învăța (B ≥ 10) și punem B adevărat în pre-înregistrarea S72b; noaptea câștigă ~20–40 de minute.
- ce faci, prin `unelte/cascada.py`:
  1. `examen_cod.py raspunsuri --config config/cod_c1_init002.toml --stare lucru/cod_c1/gpt.pt --set ascuns --dosar lucru/kronos_cod/scoala/P_verif --n 10 --temperatura 0.8 --samanta 0 --lot 2 --memorie-max 6500 --iesire lucru/kronos_cod/scoala/reper_s63/raspunsuri.jsonl`
     (dacă numele exacte ale opțiunilor diferă, folosești echivalentele; parametrii rămân: S63, P_verif 200 × 10, temperatura 0,8, sămânța 0). Modelul S63 doar citit (verifici SHA-256 înainte și după).
  2. `examen_cod.py noteaza --dosar lucru/kronos_cod/scoala/P_verif --raspunsuri … --nota lucru/kronos_cod/scoala/reper_s63/nota.json` → pass@1, pass@10 = **B** (din 200), plus ok / picat / interzis / timp.
     Notezi și câte din răspunsurile „ok” sunt doar `return <valoare fixă>` (regula (b) din nota S72b) — B se raportează în ambele feluri (cu și fără ele); pragurile S72b folosesc B obișnuit.
  3. Dacă **B < 10**: scrii în coadă la S72b „nu pornește: B = N (< 10), NU POATE ÎNCEPE” și S72b nu mai rulează la noapte; placa rămâne liberă (decid eu la trecerea următoare).
  4. `python -m pytest` — toate trec; raport scurt `docs/rapoarte/<data>_<ora>_S74_reper_scoala.md` (cifrele, placa max, cât a durat); coada → `gata`; commit + push.
- Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, cutia, modelele, P_verif / P_scoala (doar citire), seturile ascunse. Nimic descărcat, nimic instalat.
- aprobat de: supraveghetor, 4 nov 2026 11:20 (granița 2: examen; parte din S72b, aprobată de Adrian prin COMENZI.md C-60 C)
- raport: docs/rapoarte/2026-11-04_1211_S74_reper_scoala.md

### S75 — Școala de cod, runda 1, pașii 1–2 din S72b mutați ZIUA: S63 scrie 8 soluții la fiecare exercițiu din P_scoala, cutia le verifică (placa ~70 min + procesor ~20 min)
- stare: gata (executant, 4 nov 16:18): **DESTULE** — 109 corpuri corecte diferite (≥ 100, după regula (b)) la 70 de exerciții; 137 „ok” din 5.512 încercări (71 exerciții; controlul `noteaza` identic), 3 `return <valoare fixă>` scoase, 25 duplicate; 14 identice cu originalul (12,8 %); fluids/chemicals 12 + 1. Pasul 1 cod 0, 81 min, placa max 2.032 MB; S63 SHA-256 neschimbat; 1209 teste trec, 1 sărit. La noapte S72b pornește de la pasul 3 cu `runda1/corecte.jsonl`.
- (istoric) stare: in_lucru (executant, 4 nov 14:30)
- pornit: 4 nov 14:31 prin cascadă (proces 23736, pasul 1 `examen_cod.py model`, 689 × 8); pre-înregistrarea S72b urcată înainte; SHA-256 S63 înainte: 3916b8f476ea426f795784eb99bed360e468465e6f1e9ac2363db83d16bc0a99
- (istoric) stare: **aprobat** (supraveghetor, 4 nov 2026 14:20)
- tip: placă (doar generare, fără antrenare) + procesor (cutia)
- fereastră: zi, **4 nov, cât de curând, terminat până la 18:30** (generarea se oprește curat la 18:15 dacă nu e gata: notezi câte exerciții s-au scris; restul rămâne pentru S72b la noapte)
- de ce acum: reperul S74 a ieșit mic (B = 14/200, 7 %). La 689 de exerciții × 8 încercări, mă aștept la doar ~40–80 de exerciții rezolvate — adică riscul real ca pragul de **100 de corpuri corecte diferite** să nu fie atins.
  Dacă aflăm ziua, noaptea nu se pierde: fie S72b începe direct cu învățarea (pasul 3), fie planific altceva pentru noapte la trecerea de 17:15 / 20:15.
- **ÎNAINTE de pornire:** pre-înregistrarea S72b `docs/preinregistrari/2026-11-04_cod_c1_scoala_r1.md` (exact cum cere S72b, cu **B = 14** din `lucru/kronos_cod/scoala/reper_s63/nota.json`, mărimile P_verif 200 / P_scoala 689,
  pragurile S72b neschimbate: AJUTĂ = R ≥ 24 și validarea ≤ 0,505; NU AJUTĂ = R ≤ 17; STRICĂ = validarea > 0,510 sau R ≤ 9; altfel NECLAR; `ascuns2` ≥ 6/163 pentru „ajută și pe examen”), plus așteptările tale în cifre
  pentru pasul 2 (câte corecte, la câte exerciții, câte `return <valoare fixă>`, câte copiate din memorie). Commit + push, apoi pornești.
- ce faci:
  1. Pe placă, prin `unelte/cascada.py`, modelul **S63 doar citit** (`lucru/cod_c1/gpt.pt`, SHA-256 înainte și după; nu e nevoie de copie pentru generare):
     `examen_cod.py model --config config/cod_c1_init002.toml --stare lucru/cod_c1/gpt.pt --set ascuns --dosar lucru/kronos_cod/scoala/P_scoala --n 8 --temperatura 0.8 --samanta 1 --lot 2 --memorie-max 6500 --iesire lucru/kronos_cod/scoala/runda1/raspunsuri.jsonl`
     (toate cele 689, sub limita de 1.500; ~5.500 de încercări, ~65–70 min după viteza din S74).
  2. Pe procesor, o unealtă nouă **în `unelte/kronos_cod/scoala.py`** (comanda `corecte`, granița 5; cu teste noi, fără să schimbi `cutie.py`): rulează fiecare încercare în cutie cu testul exercițiului ei (exact ca `examen_cod.py noteaza`)
     și scrie `lucru/kronos_cod/scoala/runda1/corecte.jsonl` (un rând pe corp corect păstrat: id exercițiu, pachet, enunț, corp) + `runda1/numaratoare.json` cu:
     încercări scrise; corecte (toate); scoase ca `return <valoare fixă>` (regula (b) din nota S72b); **corpuri corecte diferite după spații**, la câte exerciții; câte sunt identice cu corpul original (după spații);
     câte corecte vin din `fluids` / `chemicals`; refuză să scrie peste un `numaratoare.json` existent. Rulezi și `examen_cod.py noteaza` pe aceleași răspunsuri, ca control (aceleași cifre de „ok”).
  3. `python -m pytest` — toate trec; raport `docs/rapoarte/<data>_<ora>_S75_scoala_r1_solutii.md` (cifrele, placa max, cât a durat); coada → `gata` cu verdictul într-o propoziție:
     **DESTULE** (≥ 100 corpuri corecte diferite după regula (b)) sau **PREA PUȚINE** (< 100); commit + push.
- **la noapte (S72b):** dacă S75 e `gata` cu DESTULE, S72b **sare pașii 0, 1 și 2** și pornește de la pasul 3 cu `runda1/corecte.jsonl` (B = 14 din `nota.json`). Dacă e PREA PUȚINE: S72b **nu pornește**; scrii în coadă
  „S72b nu pornește: PREA PUȚINE (N)” și placa rămâne liberă până la trecerea mea de 17:15 / 20:15, când pun sarcina de noapte. Dacă S75 n-a terminat generarea până la 18:15: S72b face la noapte restul pasului 1, apoi pașii 2–4 ca până acum.
- Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, `cutie.py`, #477, linia română, `lucru/cod_c1/` și `lucru/cod_c1_ex/` (doar citire), P_verif / P_scoala (doar citire), seturile ascunse. Nimic descărcat, nimic instalat.
- aprobat de: supraveghetor, 4 nov 2026 14:20 (granițele 2, 4 și 5; pașii 1–2 ai S72b, aprobată de Adrian prin COMENZI.md C-60 C)
- raport: docs/rapoarte/2026-11-04_1618_S75_scoala_r1_solutii.md

### S76 — C-64 R1: răspunsuri în română (exerciții „întrebare/instrucțiune → răspuns” din datele românești deja avute + set ascuns + notă automată; o noapte din #477 pe o copie)
- **notă supraveghetor (4 nov 23:20):** S76a = GATA; **S76b aprobat și mutat în noaptea 4→5 nov** (placa liberă), mai jos.
- **notă supraveghetor (4 nov 20:20): condiția e îndeplinită (S72b = STRICĂ, nu AJUTĂ).** S76 se face în doi pași: **S76a** (mai jos, aprobat, pornește la noapte) = exercițiile, setul ascuns, nota automată și reperul #477; **S76b** = noaptea de antrenare din #477 pe o copie, scrisă de mine după verdictul S76a (ținta: noaptea 5→6 nov).
- (istoric) stare: **aprobat de Adrian, cu condiție** — pornește DOAR după verdictul S72b, dacă **nu** e AJUTĂ (NU AJUTĂ, STRICĂ sau NECLAR = „nu avansăm pe cod”); dacă S72b e AJUTĂ, continuăm școala și S76 așteaptă.
  Instrucțiunile exacte, pragurile și pre-înregistrarea le scriu eu după verdictul S72b (întâi partea de procesor: exercițiile, setul ascuns, nota automată; apoi noaptea pe placă).
- tip: procesor (date + notă) + placă (o noapte, din #477 pe o copie; #477 rămâne în uz până când copia îl bate la examen)
- Nimic descărcat, fără alt AI; `kronos/`, paznicul și examenul neatinse; placa ≤ 7.000 MB / 83 °C.
- aprobat de: **Adrian (COMENZI.md C-64, 4 nov 2026 11:30)**; preluat de supraveghetor 4 nov 14:20


### S76a — C-64 R1 pasul 1: exercițiile „întrebare/instrucțiune → răspuns” în română + setul ascuns + nota automată (fără alt AI) + reperul #477 (procesor; placa doar un examen scurt)
- stare: gata (executant, 4 nov 20:50): **GATA** — antrenare **23.251** perechi (50,0 % instrucțiuni, 8 feluri noi), ascuns **500** (290 instrucțiuni), scurgeri 0 (toate 6), proba notei trecută (referințe 100 %, gol 0 %, altă referință 3,8 %, la fel de două ori); reperul #477 **R1 = 63,73** (instrucțiuni 37,47; felurile vechi 100), #459 62,87; placa max 1.344 MB / 61 °C; #477 SHA neschimbat; „limbă curată” cu minim 1 cuvânt când referința are 1 cuvânt (strict: `limba_curata_min2`) — de ales de Adrian; 1221 teste trec, 1 sărit.
- raport: docs/rapoarte/2026-11-04_2050_S76a_romana_raspunsuri.md
- verificat de supraveghetor (4 nov 23:20): toate condițiile GATA verificate pe cifre — 23.251 ≥ 10.000; instrucțiuni 50,0 % ≥ 40 %; 8 feluri noi ≥ 4; ascuns 500 ≥ 400 (290 instrucțiuni ≥ 160); scurgeri 0 la toate 6; proba notei 100 % ≥ 95 %, gol 0 %, altă referință 3,8 % ≤ 5 %, la fel de două ori ✓ → **GATA** ✓. Abaterile (minim 1 cuvânt la referințele de un cuvânt; refuzuri 15 % / da-nu 10 % în ascuns) sunt rezonabile și spuse deschis; R1 se păstrează cu varianta executantului, cea strictă alături, până alege Adrian. → **S76b aprobat pentru noaptea asta** (placa liberă de la 20:48).
- (istoric) stare: in_lucru (executant, 4 nov 20:30)
- (istoric) stare: **aprobat** (supraveghetor, 4 nov 2026 20:20)
- tip: procesor (date + unealtă + teste) + placă (doar un examen scurt, fără antrenare)
- fereastră: **acum, noaptea 4→5 nov** (placa e liberă de la 19:58). Partea de procesor oricând; examenul pe placă (pasul 5) pornește cel târziu la **05:00** și se termină până la **06:45**.
  Dacă nu apucă, pasul 5 rămâne pentru ziua de 5 nov (după 08:00) și scrii asta în coadă.
- durată maximă: procesor ~4–5 ore; placa ≤ 1 oră, sub 7.000 MB și 83 °C (`--lot` mic, ca la examenele de până acum)
- de ce: C-64 R1. #477 a fost antrenat pe întrebări cu răspunsul în text (`text_v3`); acum vrem și **instrucțiuni** („Spune…”, „Scrie…”, „Rezumă…”) și o notă care
  nu cere alt AI (profesorul Qwen NU se folosește aici), ca să putem măsura dacă o noapte de antrenare îl face să răspundă mai bine în română.
- ce faci:
  1. **Unealta nouă `unelte/romana_raspunsuri.py`** (granița 5; cu teste noi în `teste/`), comanda `construieste`: perechi „Întrebare: …⏎Răspuns: …” (același format ca la antrenarea liniei w2;
     pentru cele cu text: „Text: …⏎Întrebare: …⏎Răspuns: …”), făcute **doar prin reguli**, doar din datele românești deja pe disc (paragrafele Wikipedia RO folosite de `conversatie_text.py`,
     `docs/conversatie/conversatie_simpla.json`, `date/fapte/`). Nimic descărcat, niciun model folosit la scris.
     - păstrezi felurile din `text_v3` (cu răspunsul în text, „Nu scrie în text.”, da/nu, conversația simplă), dar **cel puțin 40 % sunt instrucțiuni** la imperativ, din **cel puțin 4 feluri noi**
       care nu există în `text_v3` și nici în examenele vechi, de exemplu: „Spune într-o propoziție ce este X.” (răspunsul = prima propoziție, scurtată curat), „Scrie doar anul în care …”,
       „Rezumă textul într-o propoziție.”, „Spune în ce județ se află X și din ce țară face parte.” (două informații din text), „Răspunde cu da sau nu: …”, „Scrie numele …”.
     - fiecare pereche are câmpurile: `fel`, `prompt`, `raspuns` (referința), `cheie` (1–3 bucăți care TREBUIE să apară într-un răspuns corect: numele, anul, numărul, județul; pentru „Nu scrie în text.” cheia e chiar asta),
       `subiect` (X) și `articol` (sursa).
  2. **Setul ascuns** `lucru/romana_raspunsuri/ascuns.jsonl`: cel puțin **400** de perechi (cel puțin 160 instrucțiuni, toate felurile reprezentate), din articole care **nu intră deloc** în antrenare
     și nu apar în `text_v3`, `date/conversatie/examen.json` sau în examenele din `docs/conversatie/`. Antrenarea: `lucru/romana_raspunsuri/antrenare.jsonl`, cel puțin **10.000** de perechi.
     Verifici scurgerile ca la `conversatie_text.py` (nicio bucată de 8 cuvinte comună între antrenare și ascuns / examenele vechi / validările română) și scrii cifra (trebuie **0**).
     Plus `info.json` (câte pe fel, sămânța, sumele SHA-256 ale celor două fișiere). Setul ascuns nu se arată în raport (doar 5 exemple din antrenare).
  3. **Nota automată**, comanda `noteaza` (fără alt AI, deterministă): pentru fiecare răspuns (tăiat la primul rând nou, ca la `examen_conversatie.py`) trei note 0/1:
     **corect** = toate bucățile din `cheie` apar în răspuns (fără diacritice și fără majuscule; numerele ca cifre); la da/nu, primul cuvânt e cel bun;
     **în temă** = apare subiectul (sau cuvântul lui principal) ori o bucată din `cheie`; la „Nu scrie în text.” = răspunsul spune că nu scrie / nu știe;
     **limbă curată** = 2–60 de cuvinte, cel puțin 90 % din cuvinte cunoscute (lista de cuvinte a motorului `module/limba_romana` sau, dacă nu se poate, vocabularul datelor românești de antrenare),
     niciun cuvânt repetat de 3 ori la rând, fără bucăți `<|…|>`. Ies: procentele pe toate și pe fel (corect / în temă / limbă curată) + **scorul R1 = media celor trei**.
  4. **Proba notei** (procesor, înainte de placă), scrisă în raport: referințele însele → corect ≥ **95 %**; răspuns gol → 0 %; referința altei întrebări (amestecate cu sămânța 0) → corect ≤ **5 %**;
     de două ori pe aceleași răspunsuri → aceleași cifre. Dacă una pică, repari nota (cel mult 3 încercări), altfel `oprit` cu motivul.
  5. **Reperul pe placă:** #477 (`lucru/w2_reteta_A_cont3/` — doar citit, SHA-256 înainte și după) scrie răspunsurile la tot setul ascuns, fără întâmplare (cea mai probabilă bucată, ca la `examen_conversatie.py`),
     cel mult 64 de simboluri; apoi `noteaza` → `lucru/romana_raspunsuri/reper_477/nota.json`. Același lucru pe procesor nu e nevoie. Informativ, dacă încape în timp: și #459.
  6. `python -m pytest` — toate trec; raport `docs/rapoarte/<data>_<ora>_S76a_romana_raspunsuri.md` (cifrele de la 2–5, câte pe fel, placa max MB/°C, cât a durat); coada → `gata` cu verdictul:
     **GATA** (≥ 10.000 antrenare, ≥ 400 ascuns, scurgeri 0, proba notei trecută) sau **PUȚINE** / **NOTA PICĂ** (cu cifra); commit + push. Nu pornești nicio antrenare.
- Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, #477 / #459 (doar citire), `module/model_gpt.py`, `module/model_muon.py`, `unelte/examen_conversatie.py`, `unelte/conversatie_text.py`
  (le poți importa, nu le schimbi), examenele vechi și seturile ascunse de cod, linia `cod_c1*`, ramura `limba-romana`. Nimic descărcat, nimic instalat. Nimic din `lucru/` în Git.
- urmează: **S76b** (noaptea 5→6 nov, din #477 pe o copie, cu pre-înregistrare): o scriu eu după verdict, cu pragurile față de reperul de la pasul 5 și cu limita pe română curat (#477 = 1,2097).
- aprobat de: supraveghetor, 4 nov 2026 20:20 (granițele 2, 3 și 5; partea R1 din **COMENZI.md C-64**, aprobată de Adrian 4 nov 11:30)

### S76b — C-64 R1 pasul 2: o noapte din #477 pe o copie (linia nouă `w2_romana_r1`), pe perechile S76a; apoi nota R1 pe setul ascuns + examenele de română/cod (placa, noaptea 4→5 nov)
- stare: gata (executant, 5 nov 05:05): **AJUTĂ** — copia #513 (5 ore, cod 0) are R1 pe instrucțiuni **98,97** (#477 37,47; prag 47,47), felurile vechi 99,68 (≥ 98), română curat 1,2060 (#477 re-măsurat 1,2097), cod curat 0,7247 (0,7270), R2 0,4050 (0,4060) → nicio regresie; placa max 5.936 MB / 63 °C; #477 SHA neschimbat; aceleași șabloane ca în antrenare (nu „orice instrucțiune”); defect mic în S76a: numerele „1,091” → „091” (7/322 antrenare, 1/40 ascuns); 1221 teste trec, 1 sărit.
- raport: docs/rapoarte/2026-11-05_0505_S76b_romana_r1.md
- verificat de supraveghetor (5 nov 07:40): pre-înregistrarea urcată înainte de pornire (23:32) ✓; pornit din #477 (rândul din log) ✓; R1 instrucțiuni **98,97 ≥ 47,47** ✓; STRICĂ: felurile vechi 99,68 ≥ 98,0, română 1,2060 ≤ 1,2147 (#477 re-măsurat 1,2097), cod 0,7247 ≤ 0,7320, R2 0,4050 ≤ 0,4110 → nicio regresie → **AJUTĂ** ✓. Citirea cinstită: setul ascuns are aceleași 8 șabloane ca antrenarea, deci e „a învățat aceste șabloane”; dacă urmează instrucțiuni formulate altfel se măsoară în **S76c** (procesor). #513 NU înlocuiește #477 fără „da”-ul lui Adrian.
- (istoric) stare: in_lucru (executant, 4 nov 23:30)
- notă supraveghetor (5 nov 02:20): pre-înregistrarea `2026-11-04_w2_romana_r1.md` verificată — urcată înainte de pornire (23:32), pragurile copiate exact (47,47 / 40,47 / 98,0 / +0,005), 5 ore (pornire înainte de 01:00), sfârșit estimat ~05:45 < 06:45.
- (istoric) stare: **aprobat** (supraveghetor, 4 nov 2026 23:20)
- tip: placă (antrenare 4–5 ore + examene ~35 min)
- fereastră: **ACUM, noaptea 4→5 nov** (placa e liberă de la 20:48; altfel ar sta degeaba până mâine seară). Orele se aleg după ora la care începe antrenarea (pasul 4):
  **`--ore 5` dacă pornește cel târziu la 01:00; `--ore 4` dacă pornește între 01:00 și 02:00; după 02:00 NU pornește la noapte** — rămâne `aprobat` pentru noaptea 5→6 nov cu `--ore 6`, pornire la 19:00
  (atunci refaci configurarea și pre-înregistrarea cu 6 ore). Totul (antrenare + examene) se termină până la **06:45**. Dacă în `COMENZI.md` apare o fereastră a lui Adrian pe workstation în noaptea asta, n-o atingi.
- durată maximă: 5 ore de antrenare + ~35 min examene; placa sub 7.000 MB și 83 °C (S51, aceeași rețetă: max 6.002 MB / 64 °C)
- de ce: C-64 R1. S76a (GATA): #477 știe perfect felurile vechi (R1 100 pe cele 210), dar la instrucțiunile noi doar **R1 37,47** (corect 22,07 %): răspunde „Da.”/„Nu.” la „Rezumă…”, „Spune într-o propoziție…”, „Scrie doar numărul…”.
  Întrebarea: o noapte pe perechile S76a (50 % instrucțiuni, articole pe care setul ascuns nu le are) îl învață să urmeze instrucțiunile, fără să strice româna și codul?
- ce faci:
  1. Verifici că `lucru/romana_raspunsuri/antrenare.jsonl` are SHA-256 `3d8ac5a3…00b0` și `ascuns.jsonl` `3a333657…c9e` (ca în `info.json`). Altfel `oprit`.
  2. `config/conv_w2_romana_r1.toml` = **copie a `config/conv_w2_reteta_A_cont3.toml` (S51, cea care a dat #477)** cu DOAR: `nume = "w2_romana_r1"`, `cale_stare = "lucru/w2_romana_r1/gpt.pt"`,
     `conversatie = "lucru/romana_raspunsuri/antrenare.jsonl"`, `durata_scaderii_secunde` = orele × 3600 (18000 la 5 ore, 14400 la 4), eticheta și antetul (diff-ul în raport). Restul identic
     (45 % perechi / 5 % hrană / 50 % text vechi, rata 0,00005, lot 12, `adunare_loturi = 8`, `racire_finala = 0.25`, adamw). `lucru/w2_romana_r1/` trebuie să NU existe înainte de pornire (capcana S42; scrii verificarea în pre-înregistrare).
     Un test mic nou dacă e nevoie ca modelul să citească perechile S76a (au `intrebare`, `raspuns`, `text` — aceleași câmpuri ca `text_v3`, deci ar trebui să meargă fără nicio schimbare de cod; dacă nu merge, `oprit`, nu schimbi `module/`).
  3. **Pre-înregistrarea** `python unelte/preinregistrare.py --nume w2_romana_r1 --titlu "S76b: o noapte din #477 pe răspunsurile în română (S76a)"` → `docs/preinregistrari/2026-11-04_w2_romana_r1.md` (sau data zilei în care pornește), cu pragurile de mai jos **copiate exact** și cu orele alese. Commit + push **ÎNAINTE** de pornire.
     Reperele #477 (S76a): R1 total 63,73; **R1 pe instrucțiuni (290) 37,47**; R1 pe felurile vechi (210) 100,0; corect pe instrucțiuni 22,07 %; limbă strictă (min 2) 54,6 %. Română curat 1,2097, cod curat 0,7270, R2 0,4060 (S51) — **re-măsurate în aceeași rulare** pe #477, iar pragurile de regresie se socotesc față de cifrele re-măsurate.
     - **AJUTĂ:** R1 pe instrucțiuni ≥ **47,47** (+10 față de 37,47) și nicio regresie (mai jos).
     - **NU AJUTĂ:** R1 pe instrucțiuni < **40,47** (sub +3) și nicio regresie.
     - **NECLAR:** între ele, fără regresie.
     - **STRICĂ** (are întâietate): R1 pe felurile vechi < **98,0**, sau română curat > #477 + **0,005**, sau cod curat > #477 + **0,005**, sau R2 > #477 + **0,005**.
     - Informativ (fără prag): R1 total, corect pe instrucțiuni, R1 pe fiecare fel, `limba_curata_min2`, română curat față de #477 (scade = bine, e și ținta C-64).
     - Scrie deschis în pre-înregistrare: instrucțiunile din setul ascuns au **aceleași șabloane** ca în antrenare (articole noi, formulări la fel), deci AJUTĂ înseamnă „a învățat aceste 8 feluri de instrucțiuni pe texte noi”, nu „înțelege orice instrucțiune”.
  4. Pornești prin cascadă (`unelte/cascada.py`), lanțul ca la S51 (`lucru/cascada/S76b_proba/s76b.py`), în același proces:
     `python unelte/antrenare_lunga.py --config config/conv_w2_romana_r1.toml --ore <5 sau 4> --porneste-din 477`, apoi `python unelte/examen_validari_ws.py --linie w2_romana_r1` și `python unelte/examen_validari_ws.py --experiment 477`,
     apoi `python unelte/romana_raspunsuri.py reper --experiment <ultimul experiment al liniei w2_romana_r1> --iesire lucru/romana_raspunsuri/reper_s76b --citit lucru/stocare/modele/experiment_477.pt lucru/w2_reteta_A_cont3/gpt.pt`
     (aceleași setări ca la reperul #477: fără întâmplare, cel mult 64 de simboluri). #477 doar citit: SHA-256 înainte = după.
  5. La sfârșit: închizi pre-înregistrarea (`--inchide w2_romana_r1`) cu cifrele și verdictul; `python -m pytest` verde; raport `docs/rapoarte/<data>_<ora>_S76b_romana_r1.md` (tabelul pe ore, R1 pe fel #477 vs. copia, cele trei examene, verdictul față de praguri, 3–5 răspunsuri ale copiei la instrucțiuni din antrenare — nu din setul ascuns —, placa max MB/°C, cât a durat); coada → `gata` cu verdictul într-o propoziție; commit + push.
- Dacă procesul cade fără eroare: `oprit`, raport cu ora exactă a căderii, **nu** reporni singur.
- Nota: R1 folosește „limbă curată” cu minim 1 cuvânt când referința are un cuvânt (varianta executantului din S76a); `limba_curata_min2` se scrie alături. Dacă Adrian alege altfel, re-notarea se face pe procesor din `raspunsuri.json`, fără placă.
- Copia **nu** înlocuiește #477 în interfață, în pachetul KGR1 sau în OS fără „da”-ul lui Adrian. Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, `module/`, setul ascuns (doar citit de `reper`), #477/#459 (doar citire), linia `cod_c1*`, ramura `limba-romana`. Nimic descărcat, nimic instalat. Nimic din `lucru/` în Git.
- pre-înregistrare: docs/preinregistrari/2026-11-04_w2_romana_r1.md (de scris și urcat înainte de pornire)
- aprobat de: supraveghetor, 4 nov 2026 23:20 (granița 1: încă o rulare pe linia w2 existentă, alt amestec de date din surse deja avute; granița 2 pentru examene) — partea R1 din **COMENZI.md C-64**, aprobată de Adrian 4 nov 11:30
- raport: docs/rapoarte/…

### S80 — Reparație: `unelte/cascada.py` nu mai crede că o sarcină veche „merge” când Windows i-a dat PID-ul altui proces (doar procesor, ~30–45 min)
- stare: gata (executant, 5 nov 2026 17:36; 1225 teste trec, 1 sărit; `stare` → `liber: true`, S42_0833 `merge: false`)
- tip: procesor (cod în `unelte/` + teste). Fără placă, fără antrenare.
- fereastră: **oricând — ACUM, înaintea lui S77a.** E singura sarcină care poate porni cât `liber` e `false` din cauza unei înregistrări vechi: n-o pornești prin `cascada.py porneste`, o faci direct în sesiunea ta.
- durată maximă: ~45 de minute.
- de ce: raportul `docs/rapoarte/2026-11-05_1429_cascada_blocata_pid_vechi_S42.md`: `lucru/cascada/S42_0833.json` (mutată deoparte de `porneste --din-nou`, fără „cod”) are PID-ul 19792, pe care Windows l-a dat acum lui `dllhost.exe` → `traieste()` zice „merge” → `liber: false` → S77a, S78, S79 nu pornesc. Aceeași capcană și pe 4 nov 18:58 (PID-ul vechi S45 14764). Reparația durabilă (varianta 2 din raport) e granița 6 („reparații de scripturi care au picat”); varianta 1 (editarea de mână a înregistrării din `lucru/`) **nu** o facem.
- ce faci:
  1. `traieste(pid, pornita=None)` în `unelte/cascada.py`: pe Windows, procesul contează ca „al nostru” doar dacă **numele imaginii e `python.exe`** (`porneste` pornește mereu `sys.executable`; citești numele din `tasklist /FI "PID eq <pid>" /FO CSV /NH`, nu cauți doar cifra în text) **și**, când `pornita` e dată, procesul **nu a pornit cu mai mult de 5 minute după `pornita`** (ora pornirii procesului, de exemplu din `Get-CimInstance Win32_Process -Filter "ProcessId=<pid>"` → `CreationDate`). Dacă ora nu se poate citi, hotărăște doar numele. Pe alte sisteme rămâne `os.kill(pid, 0)`. `sarcina()` îi dă și `s["pornita"]`.
  2. O înregistrare mutată deoparte de `muta_vechea` (numele `<sarcina>_<HHMM>`) e prin definiție terminată (`muta_vechea` mută doar ce nu mai merge): `sarcina()` o socotește `merge = False` fără să mai întrebe Windows. Și `muta_vechea`, când mută o înregistrare fără „cod”, scrie în ea `"cod": null` și `"terminata"` (ora mutării) + `"nota": "mutată fără cod"` — ca să nu se mai repete. Înregistrările vechi existente (`S42_0833.json`, celelalte) **nu le editezi de mână**; reparația din cod le tratează corect.
  3. Teste noi în `teste/test_cascada.py` (cu `subprocess.run` înlocuit, fără Windows adevărat): PID viu dar `dllhost.exe` → nu merge; `python.exe` pornit înainte de `pornita` → merge; `python.exe` pornit la 2 ore după `pornita` → nu merge; o înregistrare `S42_0833.json` fără „cod” → `merge = False` și nu blochează `liber`; `muta_vechea` pe o înregistrare fără cod scrie `cod: null`. Testele vechi trec neschimbate.
  4. `python -m pytest` — toate trec. Apoi `python unelte/cascada.py stare`: trebuie `"liber": true` (dacă placa e liberă), cu `S42_0833` → `merge: false`. Scrii ieșirea în raport.
  5. Raport `docs/rapoarte/<data>_<ora>_S80_cascada_pid_refolosit.md` (ce s-a schimbat, testele noi, ieșirea `stare` înainte/după); coada → `gata`; commit + push; **apoi pornești imediat S77a**.
- Nu atingi `kronos/`, `module/`, examenul, paznicul, jurnalul, `config/`, nimic din `lucru/` (nicio înregistrare editată sau ștearsă). Nu oprești procesul 19792 (e al Windows). Nimic instalat.
- aprobat de: supraveghetor, 5 nov 2026 17:15 (granițele 5 și 6)
- raport: docs/rapoarte/2026-11-05_1736_S80_cascada_pid_refolosit.md

### S77 — C-64 R2: Kronos mai mare, crescut din #477 (straturi noi pornite „neutre”, aceeași ieșire la început, verificat pe vectorii KGR1) — întâi un test scurt de memorie și viteză
- **notă supraveghetor (4 nov 20:20): condiția e îndeplinită (S72b = STRICĂ).** Primul pas (S77a: modelul crescut din #477 dă aceeași ieșire pe vectorii KGR1 + test scurt de memorie și viteză pe placă, fără antrenare) îl scriu la trecerea de 05:15 / 08:15, pentru ziua de 5 nov, după S76a.
- stare: **aprobat de Adrian, cu condiție** — aceeași condiție ca S76; vine după partea de procesor din S76. Instrucțiunile (mărimea țintă care încape în ≤ 7.000 MB la antrenare, estimarea lui Adrian ~200–350M,
  bf16, recalcul activări), testul de memorie/viteză și pragurile le scriu eu după verdictul S72b. Măsurat cu examenul de română (#477 = 1,2097) și cu nota din S76.
- tip: procesor + placă (test scurt, apoi nopți, fiecare cu pre-înregistrare)
- Linie de model nouă (altă mărime) — acoperită de „da”-ul din C-64; `kronos/`, paznicul și examenul neatinse; nimic descărcat.
- aprobat de: **Adrian (COMENZI.md C-64, 4 nov 2026 11:30)**; preluat de supraveghetor 4 nov 14:20
- **notă supraveghetor (5 nov 07:40):** S76b = AJUTĂ → primul pas **S77a** scris mai jos (aprobat, ziua de 5 nov, DUPĂ fereastra lui Adrian C-73). Prima noapte (S77b) o scriu la 14:15 / 17:15, după cifrele S77a, cu pre-înregistrare.
- **notă supraveghetor (5 nov 09:05):** Adrian a prelungit fereastra C-73 până la ~14:00 → S77a pornește după 14:00; S77b (noaptea 5→6 nov) o scriu la **17:15 / 20:15**, după cifrele S77a, cu pre-înregistrare (înainte de 19:00 dacă S77a e gata).

### S77a — C-64 R2 pasul 1: Kronos crescut din #477 în adâncime (straturi noi „neutre”) — aceeași ieșire (PyTorch + vectorii KGR1) și testul de memorie/viteză pe placă, FĂRĂ antrenare
- stare: gata — **GATA** (executant, 5 nov 2026 17:58): ieșirea identică (dif. 0) la pașii 2 și 5; ales **N = 24 cu recalcul** (6.010 MB, 2,80 pași/s); `lucru/w2_mare/gpt_24.pt` (sha d35e3dbe…92cc); 1232 teste trec
- tip: procesor (unealtă + teste + verificarea ieșirii) + placă (doar măsurători scurte, fără antrenare de păstrat)
- **fereastră MUTATĂ (supraveghetor, 5 nov 17:15), după S80:** cascada a fost blocată 14:00–17:30 de PID-ul vechi S42, deci „gata până la 18:30” nu se mai poate. Acum: pașii 1–2 (procesor) pornesc **imediat după S80**; măsurătorile pe placă (pasul 3) **până la 18:30 sau de la 19:00** (nu între 18:30 și 19:00); totul gata până la **23:30**. Dacă nu e gata până la 23:30, termini oricum curat (măsurătorile sunt scurte), dar S77b se mută pe noaptea 6→7 nov. Textul de mai jos (vechea fereastră) e înlocuit de acesta.
- fereastră veche: ziua de 5 nov, DUPĂ fereastra lui Adrian (COMENZI.md C-73, PRELUNGITĂ de Adrian la 08:59: ~08:30–~14:00 nimic pe placă și nimic lung pe procesor). Nu pornești înainte de **14:00** (supraveghetor, 5 nov 09:05; înainte scria 09:45); dacă Adrian e încă la workstation (vezi COMENZI.md / un semn de la el), aștepți. Totul gata până la **18:30**.
- durată maximă: procesor ~3 ore; placa ≤ **1,5 ore** în total, sub 7.000 MB și 83 °C.
- de ce: C-64 R2 („mărim parametrii păstrând ce știe”). #477 = 12 straturi × 768 (~98M parametri). Creștem **în adâncime**: un strat nou cu proiecția atenției (`atentie.out_proj`) și ultimul strat liniar al MLP (`mlp[2]`) puse pe **zero** (greutăți și bias) adună exact 0 la fluxul rezidual, deci modelul crescut dă **aceeași ieșire** ca #477 la început (arhitectura e pre-LN, cu `ln` final). Creșterea în lățime ar schimba LayerNorm-ul, deci nu păstrează ieșirea — n-o facem acum.
- ce faci:
  1. **Unealta nouă `unelte/creste_model.py`** (granița 5; teste noi în `teste/`): comanda `creste --din lucru/w2_reteta_A_cont3/gpt.pt --straturi N --iesire lucru/w2_mare/gpt_N.pt`.
     Straturile noi se împrăștie uniform printre cele vechi (la N = 24: după fiecare strat vechi unul nou; la 30 / 36 / 42 cât mai uniform, nu toate la capăt). Fiecare strat nou = **copia stratului vechi de dedesubt** (ln1, `atentie.in_proj`, ln2, `mlp[0]`), cu `atentie.out_proj.weight/bias` și `mlp[2].weight/bias` = 0.
     Fișierul ieșit se încarcă de clasa existentă (`module.model_muon:ModelGPTConversatieMuon`, `n_straturi = N`, restul setărilor ca la S51) **fără nicio schimbare în `module/`**. Starea optimizatorului NU se copiază (pornește nouă); scrii în raport ce se întâmplă cu numărătoarea pașilor la încărcare (pentru încălzirea ratei la noapte).
     Teste: forma tensorilor, straturile noi au zero unde trebuie, un model minuscul (ca la `vectori_kgr1.py`, 2 → 4 straturi) dă aceleași logit-uri (diferență ≤ 1e-5 pe procesor).
  2. **Aceeași ieșire (procesor, fp32), pentru fiecare N măsurat la pasul 3:** pe cele 3 texte KGR1 (`unelte/vectori_kgr1.py` TEXTE) și pe primele 20 de paragrafe din validarea `romana_wikipedia_curat`: diferența maximă a logit-urilor față de #477 ≤ **1e-4**, argmax identic pe **100 %** din poziții. Plus `examen_validari_ws.py` (sau echivalentul pe un fișier) pe modelul crescut ales: română curat la **±0,0005** față de 1,2097.
  3. **Memorie și viteză pe placă** (comanda nouă `masoara` în aceeași unealtă): pentru **N = 12 (reperul #477), 24, 30, 36, 42** (~98M / ~183M / ~225M / ~268M / ~310M parametri), cu pasul de antrenare adevărat al clasei (AdamW, bf16 prin `_autocast`, lot 12, context 512, loturi din amestecul S51), **60 de pași**, viteza pe ultimii 40, memoria maximă după `nvidia-smi` (ca `urmareste_placa.py`) și după `torch.cuda.max_memory_reserved`.
     Întâi fără recalculul activărilor; la N unde vârful trece de **6.500 MB**, încă o măsurare **cu recalcul** (`torch.utils.checkpoint` pus de unealtă în jurul fiecărui strat, din afară — **nu schimbi `module/`**). Paznicul rămâne pornit; dacă o măsurare ar trece de 7.000 MB, se oprește acea măsurare și treci la următoarea (nu e `oprit` pentru toată sarcina). Nimic din aceste măsurători nu se păstrează ca model.
     „Pași/s” se numără la fel ca în logul S76b (6,4 pași/s la 12 straturi) — la N = 12 trebuie să-ți iasă aproape de 6,4; dacă nu, explici diferența.
  4. **Alegerea (regula scrisă acum, nu după cifre):** cel mai mare N din {24, 30, 36, 42} cu vârful `nvidia-smi` ≤ **6.500 MB** (cu sau fără recalcul; dacă încape fără, fără) **și** viteza ≥ **2,0 pași/s** (≈ 43.000 de pași într-o noapte de 6 ore). La egalitate de condiții, cel fără recalcul.
  5. Pentru N ales: `creste` → `lucru/w2_mare/gpt_N.pt` (rămâne pentru noaptea S77b); export KGR1 **F32** (extinzi `unelte/exporta_greutati.py` cu o opțiune pentru un fișier `gpt.pt` dat, dacă nu există; implicitul neschimbat) și `python unelte/vectori_kgr1.py model --kgr …` pe exportul lui #477 și pe cel crescut: **primele 5 simboluri greedy identice pe toate cele 3 texte** și logit-urile ultimei poziții la ≤ 1e-3. Exportul nu merge în Git și nu se trimite nicăieri (nu înlocuiește pachetul KGR1 al OS).
  6. `python -m pytest` — toate trec; raport `docs/rapoarte/<data>_<ora>_S77a_kronos_crescut.md`: tabelul N × (parametri, recalcul da/nu, vârf MB `nvidia-smi`, MB torch, pași/s, °C max), diferențele de la pașii 2 și 5, N ales după regulă și ce ar însemna pentru o noapte (pași, simboluri). Coada → `gata` cu verdictul:
     **GATA** (ieșirea identică la 2 și 5 + un N ales), **IDENTITATE PICĂ** (cu cifra; atunci nu scrii niciun model crescut pentru noapte) sau **NICIUNUL ÎNCAPE** (niciun N ≥ 24 nu trece regula; scrii ce ar trebui: lot 6 cu `adunare_loturi = 16`, sau alt N). Commit + push.
- Nu atingi `kronos/`, `module/` (nicio schimbare în S77a — dacă noaptea va cere recalculul în clasa modelului, asta o scriu eu la S77b, ca setare opțională cu implicitul neschimbat), `module/examen_bpb.py`, paznicul, jurnalul, #477/#459/#513 (doar citire, SHA-256 înainte = după), linia `cod_c1*`, setul ascuns, ramura `limba-romana`. Nimic descărcat, nimic instalat. Nimic din `lucru/` în Git. Interfața, KGR1-ul OS-ului și `integrare/kronos/MODEL.md` rămân pe #477.
- urmează: **S77b** (prima noapte a modelului crescut, din `lucru/w2_mare/gpt_N.pt`, linie nouă `w2_mare_N`, cu pre-înregistrare; măsurat cu română curat față de #477 = 1,2097 și cu R1) — o scriu eu după verdictul S77a.
- aprobat de: supraveghetor, 5 nov 2026 07:40 (granițele 2 și 5; linia nouă de altă mărime e acoperită de **COMENZI.md C-64**, aprobată de Adrian 4 nov 11:30)
- raport: docs/rapoarte/2026-11-05_1752_S77a_kronos_crescut.md
- verificat de supraveghetor (5 nov 20:15): ieșirea identică — dif. max. logit **0,0** (prag 1e-4) și argmax **100 %** pe KGR1 și pe 2.950 de poziții, la toate N ✓; română curat N = 24 **1,2096** față de 1,2097 (±0,0005) ✓; KGR1 greedy 5 identic pe 3/3 texte, dif. 0,0 (prag 1e-3) ✓; regula: 42/36 nu încap, 30 cu recalcul 6.874 MB > 6.500 ✗, **24 cu recalcul 6.010 MB ≤ 6.500 și 2,80 ≥ 2,0 pași/s** ✓ → **GATA, N = 24** ✓. De știut: la măsurătorile care NU au încăput, `nvidia-smi` a urcat sub o secundă la 7.090–7.440 MB înainte de oprire (de aceea S77b are o verificare la 15 minute și pragul de oprire 6.700 MB).

### S77b — C-64 R2 pasul 2: prima noapte a lui Kronos crescut la 24 de straturi (`lucru/w2_mare/gpt_24.pt`), 5 ore pe rețeta S76b — e mai bun decât #513 (12 straturi, aceleași date, aceleași 5 ore)?
- stare: oprit — verificat de supraveghetor 5 nov 23:15: OPRIT/NEMĂSURAT corect (plafonul PyTorch 5.800 MB prea mic pentru lot 12; placa max 4.755 MB / 32 °C; 1238 teste trec) → **reluat ca S77c** (lot 6 × 16, linia `w2_mare_24b`)
- (istoric) stare: oprit (executant, 5 nov 2026 21:15)
- motiv: antrenarea #516 a căzut la 20:42:41 (~1 minut) cu CUDA out of memory: plafonul PyTorch 5.800 MB din `antrenare_recalcul.py` e prea mic pentru antrenarea adevărată (5,39 GiB folosiți + 384 MiB cerute); nicio oră, niciun examen; variante în raport (lot 6 / `adunare_loturi = 16`); `lucru/w2_mare_24/` există acum (neșters)
- (istoric) stare: in_lucru (executant, 5 nov 2026 20:30)
- (istoric) stare: **aprobat** (supraveghetor, 5 nov 2026 20:15)
- tip: placă (antrenare 5 ore + examene ~1–1,5 ore)
- fereastră: **ACUM, noaptea 5→6 nov.** Antrenarea pornește **cel târziu la 00:15** (ca totul să fie gata până la **06:45**); dacă nu apucă, NU pornește la noapte și rămâne `aprobat` pentru noaptea 6→7 nov, pornire la 19:00 (tot 5 ore, refaci pre-înregistrarea cu data nouă). Dacă în hub/coadă apare o fereastră a lui Adrian pe workstation, n-o atingi.
- durată maximă: 5 ore de antrenare + examene; placa sub **6.700 MB** (oprire proprie) / 7.000 MB (paznicul) și sub 83 °C.
- de ce: C-64 R2 („mărim parametrii păstrând ce știe”). S77a: modelul crescut (183M parametri, 24 de straturi) dă exact ieșirea lui #477 și încape cu recalcul (6.010 MB, 2,80 pași/s). Comparația cinstită: **#513** = 12 straturi, pornit din #477, **5 ore** pe aceleași date (rețeta S76b). S77b = 24 de straturi, pornit din #477 crescut, **aceleași 5 ore**, aceleași date. Întrebarea: la timp egal pe placă, modelul mai mare (care vede doar ~45 % din simboluri) ajunge mai bun?
- ce faci:
  1. **Recalculul activărilor la antrenare, fără să schimbi `module/`** (granița 5): unealta nouă `unelte/antrenare_recalcul.py` care, în același proces, pune `torch.utils.checkpoint` (`use_reentrant=False`) în jurul fiecărui strat al rețelei după ce `ModelGPTConversatieMuon._pregateste_reteaua()` a construit-o (exact ca `masoara_unul` din `creste_model.py`), apoi rulează `antrenare_lunga.main(...)` cu aceleași argumente (`RulareLocala` rulează în același proces, într-un fir). Teste noi în `teste/`: pe un model minuscul, aceeași pierdere și aceleași gradiente cu și fără recalcul (≤ 1e-5, procesor); straturile sunt într-adevăr împachetate.
     **Doar dacă asta nu se poate fără `module/`:** setarea opțională `recalcul_activari = false` în `module/model_muon.py`, implicitul neschimbat (cerută explicit de Adrian în C-64: „bf16, recalcul activări”), cu teste noi și `teste_contracte/` verzi; scrii în raport de ce n-a mers din afară. `kronos/`, examenul și paznicul nu se ating în niciun caz.
  2. `config/conv_w2_mare_24.toml` = **copie a `config/conv_w2_romana_r1.toml` (S76b, cea care a dat #513)** cu DOAR: `nume = "w2_mare_24"`, `cale_stare = "lucru/w2_mare_24/gpt.pt"`, **`n_straturi = 24`**, eticheta și antetul (diff-ul în raport). Restul identic (aceleași perechi S76a, 45 % / 5 % / 50 %, rata 0,00005, lot 12, `adunare_loturi = 8`, `durata_scaderii_secunde = 18000`, `racire_finala = 0.25`, adamw).
  3. Pornirea din modelul crescut: `lucru/w2_mare_24/` NU trebuie să existe înainte (capcana S42). Verifici `lucru/w2_mare/gpt_24.pt` = SHA-256 `d35e3dbe…92cc`, îl **copiezi** ca `lucru/w2_mare_24/gpt.pt` (originalul rămâne). Dacă `antrenare_lunga.py` are nevoie de `--porneste-din` pentru reperul primei ore, folosești `477` (aceeași ieșire). **Verificarea obligatorie înainte să treacă prima oră:** în log rețeta e `24×768`, iar scorul de la început (sau o pierdere pe validare înainte de primul pas) e cel al lui #477 (±0,001). Altfel oprești → `oprit`.
  4. **Pre-înregistrarea** `python unelte/preinregistrare.py --nume w2_mare_24 --titlu "S77b: prima noapte a lui Kronos crescut la 24 de straturi"` → `docs/preinregistrari/2026-11-05_w2_mare_24.md`, cu pragurile de mai jos **copiate exact**; commit + push **ÎNAINTE** de pornire.
     Reperele (S76b): #513 — R1 pe instrucțiuni **98,97**, R1 felurile vechi 99,68, română curat 1,2060, cod curat 0,7247, R2 0,4050; #477 — română 1,2097, cod 0,7270, R2 0,4060. Română/cod/R2 pentru #477 și #513 se **re-măsoară în aceeași rulare**, iar pragurile se socotesc față de cifrele re-măsurate. R1 pentru #513 rămâne cel din S76b (`reper_s76b`).
     - **MAI MARE = MAI BUN:** română curat S77b ≤ #513 − **0,005** și nicio regulă STRICĂ.
     - **LA FEL:** română curat S77b între #513 − 0,005 și #513 + 0,005, fără STRICĂ.
     - **MAI SLAB:** română curat S77b > #513 + **0,005**, fără STRICĂ.
     - **STRICĂ** (are întâietate): R1 felurile vechi < **98,0**, sau R1 pe instrucțiuni < **90,0**, sau cod curat > #477 + **0,005**, sau R2 > #477 + **0,005**.
     - Informativ (fără prag): română față de #477; scorul pe fiecare oră (curba — urcă încă la ora 5?); pași/s, simboluri văzute (față de #513), placa max MB/°C; R1 total și pe fel; cod față de #513.
     - Scrie deschis în pre-înregistrare: comparația e la **timp egal**, nu la simboluri egale; LA FEL sau MAI SLAB după o noapte nu înseamnă că mărimea nu ajută (modelul mare a văzut mai puține date) — pasul următor se decide după curbă.
  5. Pornești prin cascadă (`unelte/cascada.py`), lanțul într-un proces: `python unelte/antrenare_recalcul.py --config config/conv_w2_mare_24.toml --ore 5 [--porneste-din 477]`, apoi `python unelte/examen_validari_ws.py --linie w2_mare_24`, `--experiment 477`, `--experiment 513`, apoi `python unelte/romana_raspunsuri.py reper --experiment <ultimul experiment al liniei w2_mare_24> --iesire lucru/romana_raspunsuri/reper_s77b --citit …` (aceleași setări ca la S76b). #477, #513 și `gpt_24.pt` doar citite: SHA-256 înainte = după.
  6. **Paza memoriei:** după primele **15 minute** de antrenare citești vârful `nvidia-smi`; dacă e peste **6.700 MB**, oprești curat → `oprit` (în raport: vârful și varianta pentru noaptea următoare: lot 6 cu `adunare_loturi = 16`). Paznicul (7.000 MB / 83 °C) rămâne pornit tot timpul. Dacă procesul cade fără eroare: `oprit`, raport cu ora exactă, **nu** reporni singur.
  7. La sfârșit: închizi pre-înregistrarea (`--inchide w2_mare_24`) cu cifrele și verdictul; `python -m pytest` verde; raport `docs/rapoarte/<data>_<ora>_S77b_kronos_mare_noaptea1.md` (tabelul pe ore, cele trei examene pentru S77b/#513/#477, R1 pe fel S77b vs #513, verdictul față de praguri, pași/s, simboluri, placa max MB/°C, cât a durat, 3 răspunsuri la instrucțiuni din antrenare — nu din setul ascuns); coada → `gata` cu verdictul într-o propoziție; commit + push.
- S78 (copierea Mini Brain) și S79 pot merge **după ce antrenarea a pornit și a trecut verificarea de la 15 minute**, doar procesor + disc; dacă pașii/s ai nopții scad cu peste 10 % (sub ~2,5), le pui pe pauză până dimineață.
- Modelul nou **nu** înlocuiește #477 în interfață, în KGR1 sau în OS fără „da”-ul lui Adrian. Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, setul ascuns (doar citit de `reper`), #477/#459/#513, linia `cod_c1*`, ramura `limba-romana`. Nimic descărcat, nimic instalat. Nimic din `lucru/` în Git.
- pre-înregistrare: docs/preinregistrari/2026-11-05_w2_mare_24.md (de scris și urcat înainte de pornire)
- aprobat de: supraveghetor, 5 nov 2026 20:15 (granițele 1, 2 și 5; linia nouă de altă mărime și recalculul activărilor sunt acoperite de **COMENZI.md C-64**, aprobată de Adrian 4 nov 11:30)
- raport: docs/rapoarte/2026-11-05_2115_S77b_kronos_mare_noaptea1.md

### S77c — Reluarea S77b cu lot 6 × `adunare_loturi = 16` (același lot efectiv 96, mai puțină memorie): prima noapte a lui Kronos de 24 de straturi, linie nouă `w2_mare_24b`
- stare: oprit — **verificat de supraveghetor 6 nov 02:15: OPRIT/NEMĂSURAT corect** (modelul de la ora 5 nu există; informativ #518 ar fi STRICĂ: cod 0,7413 > 0,7320, R2 0,4155 > 0,4110; română 1,2268 > 1,2110; curba plată 0,4154 → 0,4155, deja la ora 1 mai rău decât #477 0,4060) → diagnoza în **S77d**, reparația codului de ieșire în **S81**
- (istoric) stare: oprit (executant, 6 nov 2026 02:00)
- motiv: antrenarea s-a oprit după ora 2 din 5 — ora 3 (#519) anulată la 01:43 cu CUDA out of memory la testul rapid (plafonul PyTorch 5.800 MB); unealta a ieșit cu cod 0, examenele au rulat pe #518 (ora 2). Verdict NEMĂSURAT; informativ #518: română 1,2268 vs #513 1,2060, cod 0,7413, R2 0,4155 (ar fi STRICĂ). Nimic repornit.
- raport: docs/rapoarte/2026-11-06_0159_S77c_kronos_mare_noaptea1.md
- (istoric) stare: in_lucru (executant, 5 nov 2026 23:30)
- (istoric) stare: **aprobat** (supraveghetor, 5 nov 2026 23:15)
- tip: placă (antrenare 5 ore + examene ~1–1,5 ore)
- fereastră: **ACUM, noaptea 5→6 nov.** Antrenarea pornește **cel târziu la 00:30**; examenele trebuie gata până la **08:00** (dacă apare între timp o fereastră a lui Adrian pe workstation în coadă/hub, oprești curat). Dacă nu apuci să pornești până la 00:30: NU pornești la noapte; rămâne `aprobat` pentru **noaptea 6→7 nov, pornire la 19:00** (refaci pre-înregistrarea cu data nouă). Ziua de 6 nov rămâne liberă pentru fereastra lui Adrian (testul OS) și S76c.
- durată maximă: 5 ore de antrenare + examene; placa sub **6.700 MB** (oprire proprie) / 7.000 MB (paznicul), sub 83 °C.
- de ce: S77b (#516) a căzut după ~1 minut cu CUDA out of memory: PyTorch avea 5,39 GiB + 0,25 GiB rezervați și a cerut încă 384 MiB, peste plafonul de 5.800 MB al lui `antrenare_recalcul.py`. Cele 384 MiB se potrivesc cu ieșirea rețelei pe un lot de 12 (12 × 512 × 16.384 numere fp32 ≈ 384 MiB) — cu lot 6 partea asta și activările se înjumătățesc. Varianta 1 din raportul executantului (verificat de supraveghetor: OPRIT/NEMĂSURAT corect, plafonul a funcționat, placa n-a trecut de 4.755 MB). Plafonul de 5.800 MB **rămâne** (varianta „plafon mai mare” e prea aproape de 7.000).
- ce faci — **exact ca la S77b (pașii 1–7 de acolo), cu DOAR aceste diferențe:**
  1. Unealta `unelte/antrenare_recalcul.py` rămâne cum e (plafonul implicit 5.800 MB, **nu** îl ridici).
  2. `config/conv_w2_mare_24b.toml` = **copie a `config/conv_w2_mare_24.toml`** cu DOAR: `nume = "w2_mare_24b"`, `cale_stare = "lucru/w2_mare_24b/gpt.pt"`, **`lot = 6`**, **`adunare_loturi = 16`**, `spatiu = { model = { lot = [6] } }` la cercetător, eticheta și antetul (diff-ul în raport). Lotul efectiv rămâne **6 × 16 = 96** (= 12 × 8), restul identic.
  3. `lucru/w2_mare_24b/` NU trebuie să existe înainte (capcana S42). Verifici `lucru/w2_mare/gpt_24.pt` = SHA-256 `d35e3dbe…92cc` și îl **copiezi** ca `lucru/w2_mare_24b/gpt.pt`. Folderul vechi `lucru/w2_mare_24/` (de la #516, cu `ruleaza.lock` gol) **nu-l atingi și nu-l folosești** — îl trece S79 în propunerea de curățenie; Adrian decide. Aceeași verificare obligatorie: rețeta `24×768` în log și scorul de pornire = #477 (±0,001).
  4. Pre-înregistrarea: `python unelte/preinregistrare.py --nume w2_mare_24b --titlu "S77c: prima noapte a lui Kronos de 24 de straturi (reluarea S77b cu lot 6 × 16)"` → `docs/preinregistrari/2026-11-05_w2_mare_24b.md` (sau data zilei de pornire), cu **aceleași praguri ca S77b, copiate exact** (MAI MARE = MAI BUN / LA FEL / MAI SLAB / STRICĂ, aceleași repere re-măsurate în aceeași rulare) + o propoziție: „lot 6 × 16 în loc de 12 × 8, același lot efectiv; S77b a fost NEMĂSURAT din lipsă de memorie”. Commit + push **ÎNAINTE** de pornire.
  5. Lanțul prin cascadă, ca la S77b pasul 5, cu `--config config/conv_w2_mare_24b.toml` și `--linie w2_mare_24b`; ieșirea reperului: `lucru/romana_raspunsuri/reper_s77c`.
  6. **Paza memoriei** ca la S77b: vârful `nvidia-smi` după primele 15 minute; peste 6.700 MB → oprești curat → `oprit`. **Dacă iar cade cu out of memory în primele minute:** ai voie la **o singură** reluare în aceeași noapte, cu `lot = 4`, `adunare_loturi = 24` (tot 96), linia `w2_mare_24c` (config `conv_w2_mare_24c.toml`, folder nou, pre-înregistrare proprie cu aceleași praguri, commit înainte), **doar dacă poate porni până la 01:00**. Altfel → `oprit`, raport, nimic repornit.
  7. Raport `docs/rapoarte/<data>_<ora>_S77c_kronos_mare_noaptea1.md` (tot ce cere S77b pasul 7, plus: vârful de memorie PyTorch și `nvidia-smi`, pașii/s față de S77a = 2,80); închizi pre-înregistrarea cu verdictul; `python -m pytest` verde; coada → `gata` cu verdictul într-o propoziție; commit + push.
- După ce antrenarea a trecut verificarea de la 15 minute: **S78**, apoi **S79** (procesor + disc, regula de 10 % la pașii/s). Dacă S77c nu pornește la noapte, S78 și S79 pornesc imediat (placa e liberă).
- Modelul nou **nu** înlocuiește #477 nicăieri fără „da”-ul lui Adrian. Nu atingi `kronos/`, `module/`, `module/examen_bpb.py`, paznicul, jurnalul, setul ascuns (doar citit de `reper`), #477/#459/#513, `gpt_24.pt` (doar citit, SHA înainte = după), `lucru/w2_mare_24/`, linia `cod_c1*`, ramura `limba-romana`. Nimic descărcat, nimic instalat, nimic șters. Nimic din `lucru/` în Git.
- pre-înregistrare: docs/preinregistrari/2026-11-05_w2_mare_24b.md (de scris și urcat înainte de pornire)
- aprobat de: supraveghetor, 5 nov 2026 23:15 (granițele 1, 5 și 6: aceeași rulare, alt lot, după un script care a picat; linia de 24 de straturi și recalculul sunt acoperite de **COMENZI.md C-64**, Adrian 4 nov 11:30)
- raport: docs/rapoarte/…

### S76c — C-64 R1 pasul 3: #513 urmează și instrucțiuni FORMULATE ALTFEL decât în antrenare? (examen nou pe procesor, fără placă, fără antrenare)
- stare: gata (executant, 6 nov 2026 09:17): **URMEAZĂ INSTRUCȚIUNI, la limită** — R1 pe 290 de instrucțiuni formulate altfel (23 de formulări, 0 în antrenare): #477 61,38, #513 83,22 (B − A = +21,84; prag +20 și ≥ 70); #513 scade de la 98,97 (S76a) la 83,22; „județ și țară” spus altfel cade (#513 7,5 % corect); defectul „122,000 → 000” reparat (test nou); lanțul 08:35–09:10 pe procesor, cod 0, SHA #477/#513 neschimbat; 1247 teste trec, 1 sărit, 0 pică; C: 110 GB liberi
- verificat de supraveghetor (6 nov 11:15): pre-înregistrarea urcată înainte de rulare (75c077c, 08:35) ✓; set nou 0 suprapuneri cu antrenarea ✓; B 83,22 ≥ A 61,38 + 20 = 81,38 ✓ și ≥ 70 ✓ → **URMEAZĂ INSTRUCȚIUNI** confirmat (la limită, +1,84). Slăbiciune clară: „județ și țară” spus altfel (7,5 % corect). #513 NU înlocuiește #477 fără „da”-ul lui Adrian.
- (istoric) stare: in_lucru (executant, 6 nov 2026 08:30)
- (istoric) stare: **aprobat** (supraveghetor, 5 nov 2026 07:40)
- tip: procesor (date + unealtă + teste + examen pe procesor, `CUDA_VISIBLE_DEVICES=-1`)
- fereastră: ziua de 5 nov, **DUPĂ S77a** (nu în același timp cu măsurătorile de viteză de pe placă și nu în fereastra lui Adrian C-73, acum până la ~14:00). Gata până la **18:30**; dacă nu apucă, se termină doar când pe placă nu rulează o antrenare (nu încarcă procesorul peste o noapte de antrenare).
  **Notă supraveghetor (5 nov 09:05):** cu fereastra prelungită până la 14:00, S77a (~3 h procesor + ≤ 1,5 h placă) ocupă probabil toată după-amiaza. Pornești S76c azi **doar dacă S77a e `gata` până la ~15:30**; altfel S76c rămâne `aprobat` pentru **ziua de 6 nov, de la 08:00** (înaintea oricărei alte sarcini de zi).
- durată maximă: ~3 ore pe procesor.
- de ce: S76b = AJUTĂ (98,97), dar setul ascuns are **aceleași 8 șabloane** ca antrenarea. Înainte ca Adrian să decidă dacă #513 îl înlocuiește pe #477, măsurăm cinstit dacă #513 urmează instrucțiuni sau doar a copiat șabloanele. Repari și defectul „1,091 → 091” (doar în setul nou).
- ce faci:
  1. **Comanda nouă `reformulat` în `unelte/romana_raspunsuri.py`** (granița 5; teste noi): din **articolele setului ascuns S76a** (cele care nu intră deloc în antrenare), cel puțin **200** de instrucțiuni în aceleași 8 feluri (cel puțin 20 pe fel; `instr_da_nu` și `instr_nu_scrie` cel puțin 15), fiecare cu **cel puțin 2 formulări noi pe fel**, care nu apar în antrenare, de exemplu:
     „Ce este X? Explică într-o singură propoziție.”, „Care e ideea textului, pe scurt? O propoziție.”, „În ce an …? Doar anul, te rog.”, „Câți locuitori are X? Răspunde numai cu numărul.”, „Cine a regizat X? Dă doar numele.”, „X — județul și țara?”, „Da sau nu: …?”.
     Verificare: **0** instrucțiuni noi a căror formulare (fără subiect) apare în `antrenare.jsonl` (scrii cifra); referința și `cheie` la fel ca în S76a (aceleași răspunsuri, doar întrebarea altfel). Numerele cu separator de mii („1,091”, „1.091”) se citesc întregi (**1091**) — test nou pentru asta. Ieșirea: `lucru/romana_raspunsuri/ascuns_reformulat.jsonl` + `info_reformulat.json` (câte pe fel, SHA-256). `antrenare.jsonl` și `ascuns.jsonl` **nu se schimbă** (SHA-256 înainte = după).
  2. **Pre-înregistrarea** `docs/preinregistrari/<data>_s76c_reformulat.md` (cu `unelte/preinregistrare.py`), commit + push **ÎNAINTE** să rulezi vreun model pe setul nou, cu pragurile de mai jos copiate exact.
  3. `reper` (adaugi `--set <fișier>` dacă lipsește; implicitul neschimbat) pe procesor, aceleași setări (fără întâmplare, cel mult 64 de simboluri), pentru **#477** (A) și **#513** (B), ambele doar citite (SHA-256 înainte = după) → `lucru/romana_raspunsuri/reformulat_477/` și `reformulat_513/`.
  4. **Pragurile** (pe R1 pe instrucțiuni reformulate; fixate acum, înainte de orice cifră):
     - **URMEAZĂ INSTRUCȚIUNI:** B ≥ A + **20** și B ≥ **70**.
     - **PARȚIAL:** B ≥ A + **10**, dar nu URMEAZĂ.
     - **DOAR ȘABLOANELE:** B < A + **10**.
     - Informativ: R1 și „corect” pe fiecare fel, A și B; diferența B față de cifra lui pe setul S76a (98,97); `limba_curata_min2`; și nota setului S76a re-calculată cu numărul reparat (doar perechea afectată, fără model nou).
  5. `python -m pytest` — toate trec; închizi pre-înregistrarea; raport `docs/rapoarte/<data>_<ora>_S76c_reformulat.md` (cifrele, 5 exemple de formulări noi — din articole de antrenare, nu din setul ascuns —, cât a durat); coada → `gata` cu verdictul; commit + push.
- Nu atingi `kronos/`, `module/`, `module/examen_bpb.py`, paznicul, jurnalul, #477/#459/#513 (doar citire), seturile S76a existente, linia `cod_c1*`, ramura `limba-romana`. Nimic descărcat, niciun alt AI, nimic instalat. Nimic din `lucru/` în Git. #513 nu înlocuiește #477 nicăieri fără „da”-ul lui Adrian.
- aprobat de: supraveghetor, 5 nov 2026 07:40 (granițele 2, 3 și 5; partea R1 din **COMENZI.md C-64**, aprobată de Adrian 4 nov 11:30)
- pre-înregistrare: docs/preinregistrari/2026-11-06_s76c_reformulat.md (urcată 08:35, commit 75c077c, înainte de examene; închisă cu verdictul)
- raport: docs/rapoarte/2026-11-06_0917_S76c_reformulat.md

### S78 — COMENZI.md C-77: salvează și organizează ce e util din vechiul proiect „Mini Brain” (Desktop) înainte ca Adrian să-l șteargă (doar procesor + disc, FĂRĂ placă, nimic șters)
- stare: gata — **verificat de supraveghetor 6 nov 05:15: GATA** (0 diferențe SHA-256, nimic șters) → C-77 `gata` în hub
- (istoric) stare: gata (executant, 6 nov 2026 02:40): **Mini Brain salvat (1,54 GB în arhivă) — Adrian poate șterge ambele foldere**; toate 5 grupurile copiate (inclusiv baza geografică `f8547edc…`), 3.260 fișiere + 2 bundle-uri (101 / 78 commit-uri, verify okay), SHA-256 sursă = copie 0 diferențe (2 treceri); C: 35,25 → 33,72 GB liberi; nimic șters; 1237 teste trec, 1 sărit, 1 pică doar din cauza discului (cunoscut, 6 nov)
- (istoric) stare: in_lucru (executant, 6 nov 2026 02:30)
- (istoric) stare: **aprobat** (supraveghetor, 5 nov 2026 20:15 — deblocat: **textul întreg al C-77 e în `plan/comenzi_hub_C76_C77.md`**; citește-l de acolo, nu mai ai nevoie de hub). **23:15: S77b a picat → faci S78 după ce S77c a pornit și a trecut verificarea de la 15 minute; dacă S77c nu pornește la noapte, faci S78 imediat.** Doar procesor + disc, regula de 10 %.
- (istoric) stare: oprit (executant, 5 nov 2026 18:30) — nimic copiat, nimic șters
- motiv: nu pot citi COMENZI.md C-77 (hub-ul nu e pe disc; `git clone` al hub-ului și citirea de pe web cer aprobare, `gh` blocat) → lista grupurilor 1–5 lipsește. Cer: textul C-77 (și C-76 pentru S79) copiat în coadă de supraveghetor, sau voie de la Adrian pentru clonarea hub-ului.
- (istoric) stare: **aprobat** (Adrian, prin C-77; preluat de supraveghetor 5 nov 2026 13:45)
- tip: procesor + disc (copiere, SHA-256, un document de lecții). Fără placă, fără antrenare, nimic instalat.
- fereastră: **ziua de 5 nov, după 14:00** (după fereastra lui Adrian C-73). **S77a are prioritate** (cifrele ei trebuie gata până la 18:30 pentru noaptea S77b): faci S78 **imediat după S77a** (înaintea lui S76c și a lui S79). Dacă S77a e blocată sau așteaptă după Adrian, poți începe S78 de la 14:00. Copierea și sumele SHA-256 pot continua și în timpul nopții S77b (nu opresc și nu încetinesc antrenarea; dacă vezi că pașii/s ai nopții scad cu peste 10 %, pui copierea pe pauză până dimineață).
- durată maximă: ~3 ore.
- ce faci: **exact ce scrie în `COMENZI.md` C-77 din hub — copiat întocmai în `plan/comenzi_hub_C76_C77.md`** (citește-o întreagă, apoi `C:\Users\Computer\Desktop\raport-test-ai-brain.md`). Pe scurt:
  1. Sursele (doar CITIRE): `C:\Users\Computer\Desktop\test ai brain v13 clean` și `C:\Users\Computer\Desktop\test ai brain`. Destinația: `C:\Kronos\arhiva\mini-brain\` (**în afara** repo-ului git).
  2. **Paza discului (adăugată de supraveghetor — workstation-ul are doar ~40 GB liberi):** înainte de copiere măsori mărimea fiecărui grup din C-77 (1–5) și spațiul liber de pe C:. Dacă după copiere ar rămâne **sub 25 GB liberi** (ridicat de la 20 la 25 GB de supraveghetor, 6 nov 02:15: discul are acum doar 34 GB liberi, iar S77d are nevoie de ~5 GB) (noaptea S77b are nevoie de loc pentru salvări), copiezi grupurile 1, 2, 3 și 5 și **NU** grupul 4 (baza geografică + `raw\`): scrii mărimea lui în raport și îl lași pentru după ce Adrian eliberează loc (C-76 / S79).
  3. Copiezi (NU muți) după lista din C-77; NU copiezi `*.pt`, `.venv*`, `.standard05-cache`, `__pycache__`, pachetul `.git` mare, cele 4 build-uri geografice vechi. Istoria git: `git bundle create <nume>.bundle --all` pentru fiecare folder, apoi `git bundle verify`.
  4. `MANIFEST.txt` (fiecare fișier + SHA-256) și verificarea sursă = copie pe toate fișierele copiate (scrii câte, câți GB, câte diferențe — trebuie 0). `CITESTE-MA.md` în arhivă (ce e unde, ce s-a lăsat și de ce).
  5. În repo: **un singur** document `docs/studiu/2026-11-05_lectii-mini-brain.md` cu lecțiile cerute în C-77 (testul mic de format înaintea rulărilor lungi — greșeala „NONE”/null; doar câștigătorul + `*.pt` în `.gitignore`; maxim 2–3 încercări pe întrebare; modulul „fapte verificate” doar ca PROPUNERE, fără cod). Fără date mari în git.
  6. `python -m pytest` — toate trec; raport `docs/rapoarte/<data>_<ora>_S78_mini_brain.md` (ce s-a copiat, GB, manifest, verificarea, spațiul liber înainte/după); coada → `gata`; în rezumatul tău scrii rândul: „Mini Brain salvat (X GB în arhivă) — Adrian poate șterge ambele foldere” (sau, dacă grupul 4 a rămas necopiat din lipsă de loc: „… DAR baza geografică nu e încă salvată — NU șterge încă `test ai brain v13 clean`”). Commit + push.
- **Nimic șters de tine** (nici sursele, nici altceva). Nu atingi `kronos/`, `module/`, `module/examen_bpb.py`, paznicul, jurnalul, `config/`, #477/#459/#513, linia `cod_c1*`, ramura `limba-romana`. Nimic din arhivă în Git.
- aprobat de: **Adrian (COMENZI.md C-77, 5 nov 2026 13:40)**; preluat de supraveghetor 5 nov 2026 13:45
- raport: docs/rapoarte/2026-11-06_0240_S78_mini_brain.md (înainte: docs/rapoarte/2026-11-05_1830_S78_oprit_comenzi_inaccesibile.md)

### S79 — COMENZI.md C-76: raport de spațiu pe workstation + verificarea arhivei de mutare + propunere de curățenie (doar procesor + disc, FĂRĂ placă, NIMIC șters)
- stare: gata — **verificat de supraveghetor 6 nov 05:15: GATA** (A 78,07 + B 26,20 = 104,27 GB fără pierdere; nimic șters; `test_interfata` instabil, la S81 a trecut) → C-76 `gata` în hub; aștept alegerea grupurilor de la Adrian
- (istoric) stare: gata (executant, 6 nov 2026 03:11): **arhiva de mutare (26,20 GB, de fapt în `Desktop\proiect\`) nu are nimic în plus** (SHA-256 identic pe 28,05 GB, doar 3 fișiere mici în plus); C: 33,46 GB liberi; propunere pe grupuri: A+B (Mini Brain + arhiva) 104,3 GB fără pierdere, C+D (modele intermediare + `gpt.pt` din linii închise) ~62,3 GB, E–H (cyberspace-cod, Hugging Face, cache simboluri, pip) ~84 GB de decis; nimic șters; 1236 teste trec, 1 sărit, 2 pică (discul — cunoscut; `test_interfata` instabil, singur trece 37/37)
- (istoric) stare: in_lucru (executant, 6 nov 2026 03:00)
- (istoric) stare: **aprobat** (Adrian, prin C-76; preluat de supraveghetor 5 nov 2026 13:45)
- tip: procesor + disc (măsurători, SHA-256, un raport). Fără placă, fără antrenare, nimic instalat.
- fereastră: **după S78** (C-77 are prioritate, cum cere Adrian). Poate rula și în timpul nopții S77b (doar citire de pe disc; aceeași regulă: dacă pașii/s ai nopții scad cu peste 10 %, pui pe pauză până dimineață). S76c rămâne pentru 6 nov de la 08:00 dacă nu apucă azi.
- durată maximă: ~3 ore.
- ce faci: **exact ce scrie în `COMENZI.md` C-76 din hub — copiat întocmai în `plan/comenzi_hub_C76_C77.md`** (citește-o întreagă):
  1. Cât ocupă fiecare dosar mare din `C:\Kronos\` (`lucru/`, date de antrenare, puncte de salvare `.pt`, exporturi `.kgr`, cache-uri pip/HF) + cele mai mari 30 de fișiere. Plus `C:\Kronos\arhiva\` după S78.
  2. Compari `Desktop\de sters\proiect\cyberspace_mutare_2026-10-10.zip` (25,6 GB) cu `C:\Kronos\cyberspace`: lista de fișiere din arhivă (fără s-o dezarhivezi pe disc; dacă trebuie, citești fișierele direct din zip) + SHA-256 pe cele mari → ce e **doar** în arhivă (cu mărimi).
  3. Propunerea de curățenie **pe grupuri**, fiecare cu GB eliberați și de ce e sigur (puncte de salvare vechi depășite, date intermediare care se pot regenera). **Obligatoriu păstrate:** #459, #477, #513, `cod_c1/gpt.pt`, `lucru/w2_mare/` (S77a/S77b), examenele și seturile ascunse, jurnalul, datele brute, amprentele paznicului.
  4. `python -m pytest` — toate trec; raport `docs/rapoarte/<data>_<ora>_S79_spatiu_workstation.md`; coada → `gata`; commit + push.
- **NIMIC șters, mutat sau dezarhivat pe disc** — Adrian aprobă pe grupuri (ștergerea de modele sau date e doar cu „da”-ul lui). Nu atingi `kronos/`, `module/`, examenul, paznicul, jurnalul, `config/`.
- aprobat de: **Adrian (COMENZI.md C-76, 5 nov 2026 13:15)**; preluat de supraveghetor 5 nov 2026 13:45
- raport: docs/rapoarte/2026-11-06_0311_S79_spatiu_workstation.md

### S81 — Reparație: `unelte/antrenare_lunga.py` / `antrenare_recalcul.py` ies cu cod ≠ 0 când o oră e anulată (ca lanțurile să nu meargă mai departe pe un model neașteptat) (doar procesor, ~30–45 min)
- stare: gata — **verificat de supraveghetor 6 nov 05:15: GATA** (cod 1 la oră anulată, 5 teste noi, singurul test picat e cel de disc, cunoscut) → S77d se poate baza pe „oprire la primul cod ≠ 0”
- (istoric) stare: gata (executant, 6 nov 2026 03:36): o oră anulată sau o oprire înainte de vreme → cod 1 și rândul „oprit înainte de vreme: ora N anulată — <motivul>” (motivul din fișa anulată din jurnal); rularea întreagă și `--raport` rămân cod 0; `antrenare_recalcul.py` transmitea deja codul; 5 teste noi; 1242 trec, 1 sărit, 1 pică doar din cauza discului (cunoscut)
- (istoric) stare: in_lucru (executant, 6 nov 2026 03:30)
- (istoric) stare: **aprobat** (supraveghetor, 6 nov 2026 02:15)
- tip: procesor (cod în `unelte/` + teste). Fără placă.
- fereastră: ziua de 6 nov, **înainte de S77d** (după S78/S79 dacă acestea rulează încă; poate și noaptea, dacă S78/S79 sunt gata).
- durată maximă: ~45 min.
- de ce: la S77c ora 3 (#519) a fost **anulată** (out of memory la testul rapid), dar unealta a ieșit cu **cod 0**, iar lanțul a mers la examene pe #518, ca și cum totul ar fi mers.
- ce faci:
  1. Găsești de ce `antrenare_lunga.main` întoarce 0 când un experiment al rulării e `anulat` (variabila `oprita` și ramurile `return 1` / `return 0`). Repari astfel încât **orice oră anulată sau oprire înainte de vreme → cod de ieșire 1** (cu un rând clar în log: „oprit înainte de vreme: ora N anulată — <motivul>”); o rulare întreagă, fără anulări, rămâne cod 0. `antrenare_recalcul.py` doar transmite codul.
  2. Teste noi în `teste/` (fără placă): o oră anulată → cod 1; toate orele bune → cod 0; `--raport` neschimbat.
  3. Nu schimbi plafonul de 5.800 MB, nici ce se antrenează. Nu atingi `kronos/`, `module/`, examenul, paznicul, jurnalul, `config/`.
  4. `python -m pytest` (regula de sus pentru testul de disc); raport scurt `docs/rapoarte/<data>_<ora>_S81_cod_iesire.md`; coada → `gata`; commit + push.
- aprobat de: supraveghetor, 6 nov 2026 02:15 (granițele 5 și 6: reparația unui script care a dat un rezultat greșit, teste noi; nu atinge `kronos/`)
- raport: docs/rapoarte/2026-11-06_0336_S81_cod_iesire.md

### S77d — De ce strică modelul de 24 de straturi încă din prima oră? Două ore scurte cu rată mai mică și încălzire mai lungă (lot 4 × 24), față de ora 1 din S77c (placa, ~2,5 h)
- stare: oprit (executant, 6 nov 2026 10:35) — **NEMĂSURAT** pe ambele variante
- motiv: lanțul a fost închis forțat din afară la 10:22:26 (cod Windows 1073807364 = 0x40010004), după ~20 min din ora 1 a lui d1; fără eroare în log, fără out of memory (vârf 6.186 MB, 62 °C), paznicul nu a oprit nimic; niciun model salvat, d2 nu a pornit; nimic repornit. `lucru/w2_mare_24d1/` există acum (copie + ruleaza.lock) — o reluare cere linii noi sau „da”-ul lui Adrian pentru folder. 1247 teste trec, 0 pică.
- verificat de supraveghetor (6 nov 11:15): OPRIT/NEMĂSURAT corect — nimic repornit, nimic șters, placa sub prag (6.186 MB, 62 °C), 1247 teste trec. Cauza probabilă: repornirea workstation-ului de către Adrian pentru testul OS (C-79, „S77d nu pornește cât Adrian e la workstation”; C-79 nu era copiat în repo). Reluarea: **S77e** (mai jos).
- (istoric) stare: in_lucru (executant, 6 nov 2026 10:00; Adrian nu e la workstation: inactiv 39 min, ecran blocat; C: 103 GB liberi; `gpt_24.pt` SHA d35e3dbe…92cc)
- (istoric) stare: **aprobat** (supraveghetor, 6 nov 2026 02:15)
- tip: placă (2 × 1 oră de antrenare + validări scurte)
- fereastră: **ziua de 6 nov, după S81 `gata`**, doar când Adrian **nu** lucrează la workstation (dacă e acolo pentru testul OS, pornești după ce a terminat). Totul gata până la **18:30**; dacă nu încape (ambele ore + validări), NU pornești ziua → rămâne `aprobat` pentru noaptea 6→7 de la 19:00, iar eu decid la 17:15 / 20:15.
- durată maximă: 2 ore de antrenare + ~20 min (pauze, validări).
- de ce: la S77c, modelul de 24 de straturi (ieșire identică cu #477 la pornire: R2 ~0,4060, română 1,2096) avea deja după **ora 1** R2 **0,4154** și după ora 2 română **1,2268** — a stricat ce știa #477, iar curba nu cobora. #513 (12 straturi, aceeași rețetă, rata 5e-5) nu a pățit asta. Ipoteza (de verificat, nu e sigură): pentru straturile noi, pornite „neutre”, rata 5e-5 cu încălzire de doar 100 de pași și AdamW gol strică echilibrul în primele minute. Înainte de încă o noapte întreagă, verificăm ieftin. Lot 4 × 24 = 96 (același lot efectiv) dă și rezervă de memorie (S77c a stat la 5.738 MB din 5.800).
- ce faci:
  0. **Verificări:** S81 `gata`; spațiu liber pe C: **≥ 20 GB** (altfel `oprit`, raport, nimic șters); `lucru/w2_mare/gpt_24.pt` SHA-256 `d35e3dbe…92cc`; folderele `lucru/w2_mare_24d1/` și `lucru/w2_mare_24d2/` **nu există**.
  1. Două configurări noi, **copii ale `config/conv_w2_mare_24b.toml`** cu DOAR: `nume`, `cale_stare`, eticheta/antetul, **`lot = 4`**, **`adunare_loturi = 24`**, `spatiu = { model = { lot = [4] } }` la cercetător, și:
     - `config/conv_w2_mare_24d1.toml` (linia `w2_mare_24d1`): **`rata_invatare = 0.00001`**, **`incalzire_pasi = 1000`**;
     - `config/conv_w2_mare_24d2.toml` (linia `w2_mare_24d2`): **`rata_invatare = 0.00002`**, **`incalzire_pasi = 1000`**.
     Restul identic (inclusiv `durata_scaderii_secunde = 18000`, ca ora 1 să fie comparabilă cu ora 1 din S77c). Diff-ul în raport.
  2. Pre-înregistrarea `python unelte/preinregistrare.py --nume w2_mare_24d --titlu "S77d: rata mai mică pentru modelul de 24 de straturi, o oră pe variantă"` cu pragurile de mai jos copiate exact; commit + push **ÎNAINTE** de pornire.
  3. Un lanț prin cascadă (`cascada.py porneste S77d -- ...`), oprire la primul cod ≠ 0, cu `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` setat doar pentru procesul lanțului (nu în Windows): pentru fiecare variantă, pe rând: copia lui `gpt_24.pt` ca `lucru/w2_mare_24dN/gpt.pt` (SHA copie = original), apoi `python unelte/antrenare_recalcul.py --config config/conv_w2_mare_24dN.toml --ore 1 --fara-copie-racita` (plafonul 5.800 MB neschimbat), apoi `examen_validari_ws.py --linie w2_mare_24dN`. La final `examen_validari_ws.py --experiment 477` (re-măsurat). Paza memoriei ca la S77c (peste 6.700 MB → oprire curată → `oprit`); paznicul rămâne pornit. Fără nota R1 (nu e nevoie aici).
  4. **Pragurile** (pe modelul de la ora 1 al fiecărei variante; fixate acum):
     - **ȚINE:** R2 ≤ **0,4090** și română curat ≤ #477 re-măsurat + **0,003** și cod curat ≤ #477 re-măsurat + **0,005**.
     - **AJUTĂ PUȚIN:** R2 < **0,4154** (ora 1 din S77c, #517) dar nu ȚINE.
     - **NU AJUTĂ:** R2 ≥ 0,4154.
     - Informativ: română și cod față de #477 și față de #518; memoria max (PyTorch și `nvidia-smi`), pași/s, °C.
     - Ce urmează (scris acum): dacă cel puțin o variantă ȚINE → noaptea 6→7, 5 ore pe cea mai bună (cea cu R2 mai mic) față de #513, cu pragurile S77b; dacă niciuna nu ține → nu mai punem nopți pe 24 de straturi până la o idee nouă (de exemplu întâi doar straturile noi), scrisă ca sarcină separată.
  5. SHA-256 #477 și `gpt_24.pt` înainte = după. `python -m pytest` (regula de sus pentru testul de disc); închizi pre-înregistrarea; raport `docs/rapoarte/<data>_<ora>_S77d_rata_mare24.md`; coada → `gata` cu verdictul pe fiecare variantă; commit + push.
- Modelele noi **nu** înlocuiesc #477 nicăieri. Nu atingi `kronos/`, `module/`, `module/examen_bpb.py`, paznicul, jurnalul, #477/#459/#513, `gpt_24.pt` (doar citit), `lucru/w2_mare_24/`, `lucru/w2_mare_24b/`, linia `cod_c1*`, ramura `limba-romana`. Nimic descărcat, instalat sau șters. Nimic din `lucru/` în Git.
- pre-înregistrare: docs/preinregistrari/2026-11-06_w2_mare_24d.md (închisă: NEMĂSURAT)
- aprobat de: supraveghetor, 6 nov 2026 02:15 (granița 1: aceeași linie de 24 de straturi din C-64, altă rată și alt lot; granița 2: validări)
- raport: docs/rapoarte/2026-11-06_1035_S77d_rata_mare24.md

### S77e — Reluarea lui S77d (rata mai mică pentru modelul de 24 de straturi), pe linii noi `w2_mare_24e1` / `w2_mare_24e2` (placa, ~2,5 h)
- stare: gata (executant, 6 nov 2026 21:35) — **e1 (1e-5) ȚINE** (#523: R2 0,4072, română 1,2120, cod 0,7286; la limită pe română), **e2 (2e-5) AJUTĂ PUȚIN** (#525: R2 0,4095, română 1,2160, cod 0,7315); #477 re-măsurat 1,2097 / 0,7270; niciuna mai bună ca #477; nvidia-smi max 6.688 MB, 61 °C; SHA-uri neschimbate; 1247 teste trec, 1 sărit
- (istoric) stare: in_lucru (executant, 6 nov 2026 19:00; fereastra de noapte, placa liberă 705 MB / 26 °C; C: 105 GB liberi; `gpt_24.pt` SHA d35e3dbe…92cc; `lucru/w2_mare_24e1/`, `_24e2/` nu există)
- (istoric) stare: **aprobat** (supraveghetor, 6 nov 2026 11:15)
- tip: placă (2 × 1 oră de antrenare + validări scurte)
- fereastră: **noaptea 6→7 nov, pornire de la 19:00, cel târziu 21:00** (gata până la ~00:00). NU pornești ziua decât dacă în nota ⚠ ACUM de sus scrie că Adrian a terminat la workstation (o scriu eu la 14:15 / 17:15); atunci totul trebuie gata până la 18:30. Dacă la pornire vezi că workstation-ul a fost repornit sau Adrian lucrează la el, aștepți.
- durată maximă: 2 ore de antrenare + ~20 min.
- de ce: S77d a fost închis din afară după 20 de minute (NEMĂSURAT), iar întrebarea rămâne: o rată mai mică și o încălzire mai lungă opresc stricarea din prima oră a modelului de 24 de straturi? Linii noi, ca să nu atingem folderul rămas `lucru/w2_mare_24d1/` (ștergerea lui ar cere „da”-ul lui Adrian).
- ce faci: **exact pașii 0–5 din S77d**, cu doar aceste schimbări:
  0. Verificări: spațiu liber pe C: ≥ 20 GB; `lucru/w2_mare/gpt_24.pt` SHA-256 `d35e3dbe…92cc`; `lucru/w2_mare_24e1/` și `lucru/w2_mare_24e2/` **nu există**; `cascada.py stare` dă placa liberă. `lucru/w2_mare_24d1/` rămâne neatins.
  1. `config/conv_w2_mare_24e1.toml` = copia lui `config/conv_w2_mare_24d1.toml` (rata 1e-5, încălzire 1000, lot 4 × 24) și `config/conv_w2_mare_24e2.toml` = copia lui `config/conv_w2_mare_24d2.toml` (rata 2e-5), cu DOAR `nume`, `cale_stare` și eticheta/antetul schimbate în `w2_mare_24e1` / `w2_mare_24e2`. Diff-ul în raport.
  2. Pre-înregistrare nouă `python unelte/preinregistrare.py --nume w2_mare_24e --titlu "S77e: reluarea S77d, rata mai mică pentru modelul de 24 de straturi, o oră pe variantă"` cu **aceleași praguri ca S77d, copiate exact** (ȚINE: R2 ≤ 0,4090 și română curat ≤ #477 re-măsurat + 0,003 și cod curat ≤ #477 re-măsurat + 0,005; AJUTĂ PUȚIN: R2 < 0,4154 dar nu ȚINE; NU AJUTĂ: R2 ≥ 0,4154; informativ ca la S77d) și cu trimitere la S77d (NEMĂSURAT, închis din afară); commit + push **ÎNAINTE** de pornire.
  3. Lanțul prin cascadă (`cascada.py porneste S77e -- ...`), identic cu S77d pasul 3, pe liniile `w2_mare_24e1` apoi `w2_mare_24e2`, apoi `examen_validari_ws.py --experiment 477`. Paza memoriei: peste 6.700 MB → oprire curată → `oprit`. Paznicul pornit.
  4. Dacă lanțul e iar închis din afară: `oprit`, raport, nimic repornit (ca la S77d).
  5. SHA-256 #477 și `gpt_24.pt` înainte = după; `python -m pytest` (toate trec); închizi pre-înregistrarea; raport `docs/rapoarte/<data>_<ora>_S77e_rata_mare24.md`; coada → `gata` cu verdictul pe fiecare variantă; commit + push.
- Ce urmează (scris acum, ca la S77d): dacă o variantă ȚINE → o noapte de 5 ore pe cea mai bună, față de #513, cu pragurile S77b (o scriu eu); dacă niciuna → nu mai punem nopți pe 24 de straturi până la o idee nouă.
- Modelele noi **nu** înlocuiesc #477 nicăieri. Nu atingi `kronos/`, `module/`, examenul, paznicul, jurnalul, #477/#459/#513, `gpt_24.pt` (doar citit), `lucru/w2_mare_24*/` existente. Nimic descărcat, instalat sau șters. Nimic din `lucru/` în Git.
- pre-înregistrare: docs/preinregistrari/2026-11-06_w2_mare_24e.md (închisă: e1 ȚINE, e2 AJUTĂ PUȚIN)
- verificat de supraveghetor (6 nov 23:15): **corect** — e1: R2 0,4072 ≤ 0,4090, română 1,2120 ≤ 1,2127, cod 0,7286 ≤ 0,7320 → ȚINE (la 0,0007 de prag); e2: R2 0,4095 > 0,4090 dar < 0,4154 → AJUTĂ PUȚIN. Placa max 6.688 MB / 61 °C, SHA-uri neschimbate, 1247 teste trec. După regula scrisă dinainte → **S85** (5 ore pe e1, față de #513).
- aprobat de: supraveghetor, 6 nov 2026 11:15 (granița 1: aceeași linie de 24 de straturi, aceleași rate ca S77d deja aprobate; granița 2: validări)
- raport: docs/rapoarte/2026-11-06_2135_S77e_rata_mare24.md

### S82 — Verificare (doar citire): ce a mai rămas din grupurile A și B din S79 după ștergerea lui Adrian, spațiul pe C: și Coșul de reciclare (procesor + disc, ~15 min)
- stare: gata (executant, 6 nov 2026 17:35) — grupul A nu mai există, arhiva B (26,2 GB) există încă; C: 112,4 GB liberi; Coșul gol; 1247 teste trec, 1 sărit
- (istoric) stare: in_lucru (executant, 6 nov 2026 17:30)
- (istoric) stare: **aprobat** (Adrian, prin COMENZI.md C-81, 6 nov 2026 15:51; preluat de supraveghetor 6 nov 2026 17:15)
- tip: procesor (doar citire pe disc)
- fereastră: **oricând — fă-o ACUM, înainte de S77e** (se termină cu mult înainte de 19:00; nu folosește placa)
- durată maximă: 30 de minute
- de ce: Adrian spune că a șters înainte să plece cele două foldere „test ai brain” (grupul A) și, probabil, arhiva `cyberspace_mutare` (grupul B, în `Desktop\proiect\`). Vrea să știe ce s-a eliberat cu adevărat.
- ce faci:
  1. **Doar prin citire** (`Test-Path`, `Get-ChildItem`, `Get-PSDrive C`): pentru fiecare cale din grupurile A și B din raportul `docs/rapoarte/2026-11-06_0311_S79_spatiu_workstation.md` scrii „există / nu mai există” (și mărimea, dacă există).
  2. Spațiul liber pe C: în GB, acum.
  3. Coșul de reciclare de pe C: câte fișiere și câți GB ține (doar citit, de exemplu cu `Shell.Application` → `Namespace(10)` sau mărimea lui `C:\$Recycle.Bin`; dacă nu se poate citi, scrii asta). **NU golești Coșul și nu ștergi nimic.**
  4. Dacă spațiul liber e **> 40 GB**: `python -m pytest` (cu testul de disc inclus) și scrii rezultatul.
  5. Scrii **SUS în `plan/pentru_adrian.md`** un rezumat de **3 rânduri** (titlu `## 6 noiembrie 2026, <ora> — (executant, S82 / C-81) …`): ce mai există din A și B, spațiul liber pe C:, cât ține Coșul (și dacă golirea lui ar elibera spațiu — o face Adrian, dacă vrea). Raportul întreg: `docs/rapoarte/<data>_<ora>_S82_verificare_spatiu.md`. Coada → `gata` cu rezultatul într-o propoziție; commit + push.
- Nu atingi nimic altceva; nimic șters, mutat, descărcat sau instalat. Nimic din `lucru/` în Git.
- pre-înregistrare: nu e nevoie (fără placă, fără experiment)
- aprobat de: Adrian (COMENZI.md C-81, 6 nov 2026)
- raport: docs/rapoarte/2026-11-06_1735_S82_verificare_spatiu.md
- verificat de supraveghetor (6 nov 20:15): **gata, corect** — doar citire, nimic șters; grupul A nu mai există, arhiva B (26,2 GB) e încă în `Desktop\proiect\`; C: 112,4 GB liberi (> 40 → testul de disc rulat: 1247 trec, 1 sărit); Coșul gol. C-81 → gata în hub.

### S83 — C-82: #513 îl înlocuiește pe #477 (modelul în uz + pachetul KGR1 pentru OS + Release), #477 și #459 păstrați ca rezerve (doar procesor)
- stare: oprit (executant, 6 nov 2026 22:10) — după pasul 1; pașii 2–7 nefăcuți; SHA #513/#477/#459 neschimbate; 1247 teste trec, 1 sărit
- motiv: exportul #513 are 110.859.008 octeți, nu 110.859.040 — aceeași arhitectură (aceiași tensori și forme, verificat), diferă doar textul `sursa` din antet („#513 w2_romana_r1”, cu 5 octeți mai scurt), iar antetul se aliniază la 32 → −32 octeți. Propun: accept mărimea reală și reiau de la pasul 2 cu fișierul deja exportat (`kronos_513_q8_0.kgr`, SHA 66f734b3…5859, neșters).
- (istoric) stare: in_lucru (executant, 6 nov 2026 22:00; S77e gata, placa liberă)
- (istoric) stare: **aprobat** (Adrian, COMENZI.md C-82, 6 nov 2026 17:39; pașii scriși de supraveghetor 6 nov 20:15)
- tip: procesor (fără placă: `CUDA_VISIBLE_DEVICES=-1` pentru toți pașii)
- fereastră: **după ce S77e e `gata` sau `oprit`** (în noaptea 6→7 sau mâine de la 08:00). NU în timp ce S77e rulează (ca să nu-i iei procesorul și discul).
- durată maximă: 2 ore; RAM cel mult ~6 GB
- de ce: Adrian: „Da 513” (C-82, DECIZII 6 nov 17:39) după S76b (AJUTĂ: R1 98,97 vs 37,47) și S76c (URMEAZĂ: 83,22 vs 61,38). OS-ul (sarcina lui P6-60) așteaptă Release-ul `kronos-kgr1-513` și `MODEL.md` cu #513.
- ce faci: **exact pașii 1–7 din S54**, cu 513 în loc de 477 și 477 în loc de 459:
  0. Verificări: SHA-256 pentru checkpoint-ul #513, `kronos_477_q8_0.kgr` (`bcbe8187…3963`) și `kronos_459_q8_0.kgr` (`e80618b4…382e`) notate înainte; la final trebuie să fie identice.
  1. **Export:** `python unelte/exporta_greutati.py --experiment 513 --fel q8_0 --iesire lucru/export/kronos_513_q8_0.kgr` (în `lucru/`, NU în Git); SHA-256 + mărimea în `lucru/export/kronos_513_q8_0.kgr.sha256` (același format ca la #477). Mărimea trebuie să fie **110.859.040 octeți** (aceeași arhitectură ca #477); altfel oprești și scrii de ce. **Nu ștergi și nu suprascrii** fișierele #477 și #459.
  2. **Vectorii de control:** `python unelte/vectori_kgr1.py model --kgr lucru/export/kronos_513_q8_0.kgr` — cele 3 texte fixe, simbolurile, primele 5 simboluri greedy și marja minimă. Verifică cu `unelte/inferenta_bruta.py` că dă aceleași simboluri și aceleași logit-uri ca PyTorch pe greutățile Q8_0 desfăcute (cum s-a făcut la #477; diferența maximă de rotunjire o scrii în raport). Dacă o marjă minimă e sub 0,005, o scrii clar în raport (OS-ul ar putea alege alt simbol din cauza rotunjirii).
  3. **`docs/integrare_kronos/MODEL.md`** rescris pentru #513, în aceeași formă: modelul (#513, linia `w2_romana_r1`, S76b AJUTĂ, S76c URMEAZĂ la limită, slab la „județ și țară”), arhitectura, fișierul, mărimea, SHA-256, Release-ul, tabelul cu cele 3 texte, marjele. La final: **„Rezerva: #477”** (suma, mărimea, Release-ul lui dacă există) și **„Rezerva: #459”** (ce era deja), ca OS-ul să le poată porni în continuare.
  4. **Release** privat în `Adriancu91/cyberspace` (NU în hub, NU public): `gh release create kronos-kgr1-513 lucru/export/kronos_513_q8_0.kgr lucru/export/kronos_513_q8_0.kgr.sha256 --repo Adriancu91/cyberspace --title "Kronos #513 KGR1 Q8_0" --notes "<suma și mărimea>"` (fără date personale). Dacă `gh` cere aprobare, nu există sau nu e autentificat: **nu instalezi nimic, nu te autentifici**; comanda exactă în raport și în MODEL.md (o face Adrian).
  5. **Modelul în uz:** toate locurile unde #477 / `kronos_477_q8_0.kgr` e implicit (aceleași ca la S54: `module/inferenta_kgr1.py`, `module/inferenta_ccm.py`, `module/calcul/banc.py`, `module/calcul/reglaj.py`, configurarea și `unelte/interfata_ws.ps1`) → `kronos_513_q8_0.kgr` / 513. Doar căile implicite, **MANIFEST neschimbat**. Reglajul CCM: `python -X utf8 -m module.calcul.reglaj verifica --kgr lucru/export/kronos_513_q8_0.kgr` (și reglajul nou pe procesor, dacă cere). Filele interfeței care folosesc alte modele nu le schimbi; în raport: ce model folosește fiecare filă înainte și după. Interfața o repornești doar cum se face de obicei; dacă cere aprobare, scrii ce trebuie făcut.
  6. Testele care verifică „modelul în uz” → 513; cele cu vectorii fixați ai lui #477/#459 rămân. `python -m pytest`: toate trec. Commit + push.
  7. Raport `docs/rapoarte/<data>_<ora>_S83_model_513.md`: suma și mărimea, tabelul cu cele 3 texte (#513 lângă #477), marjele, Release făcut sau comanda pentru Adrian, fișierele schimbate (înainte → după), testele. Un rând sus în `plan/pentru_adrian.md`. Coada → `gata`.
- Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, checkpoint-urile (doar citire), S77e și liniile `w2_mare_24*`. Nu scrii în hub (supraveghetorul copiază MODEL.md în `integrare/kronos/MODEL.md`). Nimic descărcat, instalat sau șters.
- Dacă un pas pică de 2 ori la rând cu aceeași eroare: `oprit`, eroarea în raport.
- pre-înregistrare: nu e antrenare; nu e nevoie (pragul: mărime = 110.859.040, aceleași simboluri ca PyTorch, sumele rezervelor neschimbate)
- aprobat de: Adrian (COMENZI.md C-82, 6 nov 2026 17:39, „Da 513”)
- raport: docs/rapoarte/2026-11-06_2210_S83_oprit_marime_export.md
- verificat de supraveghetor (6 nov 23:15): **oprit corect** — pragul de mărime era al meu și presupunea același antet; aceiași tensori și aceleași forme, diferența (−32 octeți) vine doar din textul `sursa` + alinierea la 32. Accept mărimea reală → reluarea **S83b** (jos), de la pasul 2, cu fișierul deja exportat.

### S84 — C-85 pasul 1: lista punctelor de salvare `.pt` (ce s-ar păstra / ce s-ar putea șterge) — unealtă nouă, DOAR LISTĂ, nimic șters (procesor + disc)
- stare: gata (executantul, 6 nov 2026 23:04; lista 592 .pt / 107,6 GB: PĂSTREAZĂ 50 / 22,3 GB, SE POATE ȘTERGE 113 / 71,5 GB, NECUNOSCUT 429 / 13,8 GB; nimic șters; 1254 teste trec; aprobat de Adrian, COMENZI.md C-85 pasul 1, 6 nov 2026 17:56)
- tip: procesor + disc (doar citire), fără placă
- fereastră: **după ce S83 e `gata` sau `oprit`** (nu în timp ce S77e rulează: citirea a ~100 GB ar încetini antrenarea)
- durată maximă: 1,5 ore
- de ce: C-85 pasul 1 — discul se umple cu modele intermediare (S79: `.pt` ~114 GB). Regula: după verdict se păstrează doar câștigătorul + rezervele numite; restul se șterge DOAR după ce numele, SHA-256 și scorul sunt în jurnal. **Prima rulare e doar listă**, ca Adrian să vadă totalul.
- ce faci:
  1. Unealtă nouă `unelte/puncte_salvare.py` (nu atinge `kronos/`, `module/`, examenul): comanda `lista` caută toate fișierele `.pt` din `lucru/` și scrie pentru fiecare: calea, mărimea, SHA-256, linia și experimentul din jurnal (doar citit), scorul (română curat / cod curat / R1, ce există în jurnal sau în rapoarte) și clasa **PĂSTREAZĂ** sau **SE POATE ȘTERGE**, cu motivul.
  2. **PĂSTREAZĂ** mereu: #459, #477, #513, `lucru/cod_c1/gpt.pt`, modelul în uz (după S83: #513), `lucru/w2_mare/gpt_24.pt`, tot ce e numit în pre-înregistrările încă deschise și în sarcinile `aprobat`/`in_lucru` din coadă, cel mai bun punct al fiecărei linii (câștigătorul) și orice fișier pe care unealta nu-l poate lega de jurnal (clasa „NECUNOSCUT — păstrat”). Lista rezervelor numite stă într-un fișier de configurare mic (de ex. `config/puncte_salvare.toml`), nu în cod.
  3. Unealta **nu are comandă de ștergere** în pasul ăsta. Ieșirea: `lucru/puncte_salvare/lista_<data>.json` + tabelul în raport.
  4. Teste noi în `teste/` (fișiere `.pt` false într-un dosar temporar): rezervele numite ies mereu PĂSTREAZĂ; un fișier fără jurnal iese NECUNOSCUT; unealta nu șterge și nu modifică nimic (sumele înainte = după). `python -m pytest`: toate trec.
  5. Raport `docs/rapoarte/<data>_<ora>_S84_puncte_salvare.md`: totalul pe clase (număr de fișiere și GB), primele 20 cele mai mari din „SE POATE ȘTERGE”, lista NECUNOSCUT. 3 rânduri sus în `plan/pentru_adrian.md`, cu întrebarea pentru Adrian: „ștergem clasa SE POATE ȘTERGE (X GB)? da/nu”. Coada → `gata`; commit + push.
- Nu ștergi, nu muți, nu redenumești nimic; nu scrii în jurnal; nimic din `lucru/` în Git.
- pre-înregistrare: nu e nevoie (fără antrenare, fără placă)
- aprobat de: Adrian (COMENZI.md C-85, 6 nov 2026 17:56, pasul 1)
- raport: docs/rapoarte/2026-11-06_2304_S84_puncte_salvare.md
- verificat de supraveghetor (6 nov 23:15): **gata, corect** — doar listă (fără comandă de ștergere), 592 `.pt` / 107,6 GB pe clase, 7 teste noi, 1254 trec. Întrebarea „ștergem SE POATE ȘTERGE?” e la Adrian; până la răspunsul lui nu se șterge nimic. Atenție la `gpt.pt` de linie (31 fișiere, 38 GB) — fără ele liniile nu se mai continuă exact.

### S85 — Prima noapte de 5 ore a lui Kronos de 24 de straturi pe rețeta e1 (rata 1e-5, încălzire 1000, lot 4 × 24), linie nouă `w2_mare_24f` — e mai bun decât #513 la timp egal?
- stare: oprit — **verificat de supraveghetor 7 nov 02:15: OPRIT/NEMĂSURAT corect** (pragurile erau pentru ora 5, care nu există; cod 1 corect după S81; doar validările liniei pe #529; placa max 6.431 MB / 61 °C; SHA-uri neschimbate; 1254 teste trec). Informativ #529: română 1,2108 (pornirea 1,2096, #513 1,2060), cod 0,7280, R2 0,4069 — ține, dar nu e mai bun. **A doua cădere identică (S77c, S85) la testul rapid de la ora 3 → nu repornim liniile de 24 până nu lămurește S86 de ce se umple memoria.**
- (istoric) stare: oprit (executant, 7 nov 2026 02:00)
- motiv: ora 3 (#530) anulată la 01:44 cu CUDA out of memory la testul rapid (PyTorch 5,56 din 5,66 GiB, plafonul 5.800 MB), a doua noapte la rând după S77c; doar validările informative pe #529 (română curat 1,2108, cod curat 0,7280, R2 0,4069) → NEMĂSURAT; nimic repornit
- (istoric) stare: in_lucru (executant, 6 nov 2026 23:30; fereastra de noapte, placa liberă 456 MB / 26 °C)
- (istoric) stare: **aprobat** (supraveghetor, 6 nov 2026 23:15)
- tip: placă (antrenare 5 ore + examene ~1–1,5 ore)
- fereastră: **ACUM, noaptea 6→7 nov.** Antrenarea pornește **cel târziu la 00:30**; examenele trebuie gata până la **07:45**. Dacă nu apuci să pornești până la 00:30: NU pornești la noapte; rămâne `aprobat` pentru **noaptea 7→8 nov, pornire la 19:00** (refaci pre-înregistrarea cu data nouă). Dacă în coadă/hub apare o fereastră a lui Adrian pe workstation, oprești curat.
- durată maximă: 5 ore de antrenare + examene; placa sub **6.700 MB** la verificarea de 15 minute (oprire proprie) / 7.000 MB (paznicul, tot timpul) și sub 83 °C.
- de ce: regula scrisă dinainte la S77e: o variantă ȚINE → o noapte de 5 ore pe cea mai bună, față de #513, cu pragurile S77b. e1 (#523) a ȚINUT (R2 0,4072, română 1,2120, cod 0,7286). Întrebarea S77b rămâne: la timp egal pe placă (5 ore), modelul de 24 de straturi ajunge mai bun decât #513 (12 straturi, aceleași date)?
- ce faci — **exact ca la S77b (pașii 1–7 de acolo), cu DOAR aceste diferențe:**
  0. Verificări: C: ≥ 20 GB liber; `lucru/w2_mare/gpt_24.pt` SHA-256 `d35e3dbe…92cc`; `lucru/w2_mare_24f/` **nu există**; `cascada.py stare` dă placa liberă. Folderele `lucru/w2_mare_24*` existente rămân neatinse.
  1. `config/conv_w2_mare_24f.toml` = **copia lui `config/conv_w2_mare_24e1.toml`** cu DOAR `nume = "w2_mare_24f"`, `cale_stare = "lucru/w2_mare_24f/gpt.pt"`, eticheta și antetul (diff-ul în raport). Restul identic (rata 1e-5, încălzire 1000, lot 4 × 24, `durata_scaderii_secunde = 18000`, `racire_finala = 0.25`, adamw). Copiezi `gpt_24.pt` ca `lucru/w2_mare_24f/gpt.pt` (originalul rămâne); verificarea obligatorie din S77b pasul 3 (rețeta `24×768`, „24 straturi împachetate”, scorul de pornire = #477 ± 0,001).
  2. Pre-înregistrarea `python unelte/preinregistrare.py --nume w2_mare_24f --titlu "S85: prima noapte de 5 ore a lui Kronos de 24 de straturi pe rețeta e1"` cu **pragurile S77b copiate exact** (MAI MARE = MAI BUN: română curat ≤ #513 − 0,005 și nicio STRICĂ; LA FEL: ±0,005; MAI SLAB: > #513 + 0,005; STRICĂ, cu întâietate: R1 felurile vechi < 98,0, R1 pe instrucțiuni < 90,0, cod curat > #477 + 0,005, R2 > #477 + 0,005; #477 și #513 re-măsurați în aceeași rulare; R1 #513 = `reper_s76b`) + propozițiile: „comparația e la timp egal, nu la simboluri egale (~48 M simboluri/oră față de mai multe la #513)”, „rețeta e1 din S77e (ȚINE după o oră)”, „încălzirea de 1.000 de pași ocupă ~prima oră”. Commit + push **ÎNAINTE** de pornire.
  3. Lanțul prin cascadă: `python unelte/antrenare_recalcul.py --config config/conv_w2_mare_24f.toml --ore 5`, apoi `examen_validari_ws.py --linie w2_mare_24f`, `--experiment 477`, `--experiment 513`, apoi `romana_raspunsuri.py reper --experiment <ultimul experiment al liniei w2_mare_24f> --iesire lucru/romana_raspunsuri/reper_s85 …` (aceleași setări ca la S76b). Plafonul PyTorch 5.800 MB rămâne (nu-l ridici).
  4. **Dacă o oră e anulată** (de ex. out of memory la testul rapid, ca la S77c ora 3): lanțul se oprește singur (S81, cod 1). Atunci rulezi DOAR validările (`examen_validari_ws.py`) pe ultimul model salvat al liniei, ca informativ; verdictul e **NEMĂSURAT**; `oprit`, raport cu ora, vârful PyTorch și `nvidia-smi` la căderea; nimic repornit. Dacă lanțul e închis din afară: la fel ca la S77d (`oprit`, nimic repornit).
  5. La sfârșit (ca la S77b pasul 7): SHA-256 #477, #513 și `gpt_24.pt` înainte = după; închizi pre-înregistrarea cu verdictul; `python -m pytest` (toate trec); raport `docs/rapoarte/<data>_<ora>_S85_kronos_mare_5ore.md` (tabelul pe ore — urcă încă la ora 5?, cele trei examene pentru S85/#513/#477, R1 pe fel, pași/s, simboluri văzute față de #513, vârful PyTorch și `nvidia-smi` pe fiecare oră, °C max); coada → `gata` cu verdictul într-o propoziție; commit + push.
- S83b (procesor) poate merge **după ce antrenarea a trecut verificarea de la 15 minute**; dacă pașii/s scad cu peste 10 % (sub ~5,9), pui S83b pe pauză până după S85.
- Ce urmează (scris acum): MAI MARE = MAI BUN → propun lui Adrian o a doua noapte (continuare) și întrebarea dacă modelul mare devine linia principală; LA FEL / MAI SLAB fără STRICĂ → mă uit la curbă (dacă urcă încă la ora 5 → a doua noapte de continuare; dacă e plată → oprim liniile de 24 până la C-85 pasul 2); STRICĂ → oprim liniile de 24.
- Modelul nou **nu** înlocuiește #513/#477 nicăieri fără „da”-ul lui Adrian. Nu atingi `kronos/`, `module/`, `module/examen_bpb.py`, paznicul, jurnalul (doar prin platformă), setul ascuns (doar citit de `reper`), #459/#477/#513, `gpt_24.pt` (doar citit), `lucru/w2_mare_24*/` existente. Nimic descărcat, instalat sau șters. Nimic din `lucru/` în Git.
- pre-înregistrare: docs/preinregistrari/2026-11-06_w2_mare_24f.md (închisă, Verdictul NEMĂSURAT)
- aprobat de: supraveghetor, 6 nov 2026 23:15 (granițele 1 și 2: aceeași linie de 24 de straturi, rețeta e1 deja rulată, mai multe ore; linia de 24 și recalculul acoperite de COMENZI.md C-64, Adrian 4 nov)
- raport: docs/rapoarte/2026-11-07_0200_S85_kronos_mare_5ore.md

### S83b — Reluarea S83 de la pasul 2: #513 modelul în uz, cu mărimea reală a exportului (110.859.008 octeți) (doar procesor)
- stare: gata (executant, 7 nov 2026 02:39; #513 modelul în uz, 110.859.008 octeți, SHA 66f734b3…5859; aceleași simboluri ca PyTorch, dif. max 1,4e-4, marje greedy 0,166/0,172/0,095; reglaj CCM refăcut pe procesor; Release nefăcut — `gh` cere aprobare, comanda pentru Adrian în raport; sumele #513/#477/#459 neschimbate; 1258 teste trec, 1 sărit)
- (istoric) stare: in_lucru (executant, 7 nov 2026 02:30; S85 oprit, placa liberă)
- (istoric) stare: **aprobat** (supraveghetor, 6 nov 2026 23:15; în cadrul COMENZI.md C-82, „Da 513”, Adrian 6 nov 17:39)
- tip: procesor (`CUDA_VISIBLE_DEVICES=-1` pentru toți pașii)
- fereastră: **după ce S85 a trecut verificarea de la 15 minute** (regula de 10 % la pașii/s de la S85), sau imediat dacă S85 nu pornește la noapte; altfel mâine de la 08:00.
- durată maximă: 2 ore; RAM cel mult ~6 GB
- de ce: S83 s-a oprit corect la pasul 1: exportul #513 are 110.859.008 octeți în loc de 110.859.040 — aceiași tensori și forme, diferă doar textul `sursa` din antet (+ alinierea la 32). Pragul de mărime era al supraveghetorului; îl înlocuiesc cu verificarea care contează: aceiași tensori/forme + aceleași simboluri ca PyTorch.
- ce faci: **pașii 2–7 din S83, exact**, cu fișierul deja exportat `lucru/export/kronos_513_q8_0.kgr`:
  0. Verifici că SHA-256 al fișierului e `66f734b3…5859` și mărimea 110.859.008; dacă `lucru/export/kronos_513_q8_0.kgr.sha256` nu există, îl scrii (același format ca la #477). SHA-256 pentru checkpoint-ul #513, `kronos_477_q8_0.kgr` (`bcbe8187…3963`) și `kronos_459_q8_0.kgr` (`e80618b4…382e`) notate înainte = după. **Nu reexporți, nu suprascrii nimic.**
  1. Pașii 2–7 din S83 (vectorii de control verificați cu `inferenta_bruta.py`, `docs/integrare_kronos/MODEL.md` cu #513 + rezervele #477 și #459, Release privat `kronos-kgr1-513` sau comanda pentru Adrian, căile implicite → 513 cu MANIFEST neschimbat, testele „modelul în uz” → 513, `python -m pytest` verde). În `MODEL.md` scrii mărimea reală **110.859.008** și o propoziție: „față de #477 (110.859.040) diferă doar antetul (textul `sursa`), arhitectura e aceeași”.
  2. Raport `docs/rapoarte/<data>_<ora>_S83b_model_513.md` (ce cere S83 pasul 7, plus mărimea și motivul diferenței); un rând sus în `plan/pentru_adrian.md`; coada → `gata`; commit + push.
- Aceleași interdicții ca la S83 (nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, checkpoint-urile, S85 și liniile `w2_mare_24*`; nu scrii în hub; nimic descărcat, instalat sau șters). Dacă un pas pică de 2 ori la rând cu aceeași eroare: `oprit`, eroarea în raport.
- pre-înregistrare: nu e antrenare (pragul: aceiași tensori/forme ca #477, aceleași simboluri ca PyTorch, sumele rezervelor neschimbate)
- aprobat de: Adrian (COMENZI.md C-82, 6 nov 2026 17:39); pragul de mărime schimbat de supraveghetor, 6 nov 2026 23:15
- raport: docs/rapoarte/2026-11-07_0239_S83b_model_513.md

### S86 — C-85 pasul 2: memoria plăcii la modelul mare — Muon (o singură stare) față de AdamW + paza de memorie la fiecare oră (măsurare scurtă pe placă, fără antrenare lungă)
- stare: gata — **verificat de supraveghetor 7 nov 05:15: DA corect** (3.706 − 3.057 = 649 MB ≥ 400; placa max 6.431 MB / 63 °C; `gpt_24.pt` SHA neschimbat; 1278 teste trec). Muon încape la 4 × 24, 6 × 16, 12 × 8; AdamW 4 × 24 nu mai încape la validare. Pasul 3b rămâne deschis → **S87**.
- (istoric) stare: gata (executant, 7 nov 2026 04:06; verdict DA: Muon −649 MB la antrenare; AdamW 4 × 24 out of memory la validare; 3b fără răspuns sigur)
- (istoric) stare: in_lucru (executant, 7 nov 2026 03:00; S83b gata, placa liberă 456 MB / 26 °C)
- (istoric) stare: **aprobat** (Adrian, COMENZI.md C-85 pasul 2, 6 nov 2026 17:56; pașii scriși de supraveghetor 6 nov 23:15)
- tip: placă (măsurare ~45–60 min) + procesor (unealtă, teste)
- fereastră: **MUTAT (supraveghetor, 7 nov 02:15): ACUM, în restul nopții 6→7** — S85 s-a oprit, placa e liberă, nu mai vine o continuare S85. Pornești după ce S83b a pornit (pot merge în paralel; S83b e pe procesor; regula de 10 % nu se aplică, S86 nu e antrenare lungă). Partea pe placă pornește **cel târziu la 05:30** și se termină până la **07:00**; dacă nu apuci, o faci **ziua de 7 nov de la 08:00** (totul gata până la 18:30). Nimic pe placă dacă Adrian e la workstation.
- durată maximă: 1 oră pe placă + ~1 oră procesor
- de ce: la modelul de 24 de straturi memoria plăcii e la limită (S77b: out of memory la lot 12; S77c: out of memory la testul rapid de la ora 3; S77e: `nvidia-smi` 6.688 MB, la 12 MB de paza de 6.700). AdamW ține 2 stări pentru fiecare parametru (~1,5 GB la 183M); Muon (există deja în `module/model_muon.py`, `optimizator = "muon"`) ține una pe matricile straturilor.
- ce faci:
  1. **Unealtă nouă `unelte/masoara_memorie_mare.py`** (nu atinge `kronos/`, `module/`, examenul): construiește modelul de 24 de straturi exact ca `antrenare_recalcul.py` (recalcul pe straturi, plafonul PyTorch 5.800 MB), din o **copie** a `gpt_24.pt` într-un dosar temporar `lucru/memorie_mare/` (nou), și face pentru fiecare variantă ~200 de pași de optimizator pe loturi reale + **un test rapid / o validare** ca cea de la sfârșitul unei ore. Nu salvează modele, nu scrie în jurnal. Scrie pentru fiecare variantă: vârful PyTorch (`max_memory_allocated` și `max_memory_reserved`), vârful `nvidia-smi`, separat la antrenare și la testul rapid, pași/s.
  2. **Variantele**, în ordinea asta (te oprești la prima care trece de 6.700 MB `nvidia-smi` sau cade cu out of memory — o notezi și treci la următoarea): (a) adamw, lot 4 × 24 (reperul = e1); (b) muon, lot 4 × 24; (c) muon, lot 6 × 16; (d) muon, lot 12 × 8. Setările Muon: cele implicite din `model_muon.py` (le scrii în raport).
  3. **Paza de memorie la fiecare oră** în `unelte/antrenare_recalcul.py` (doar `unelte/`): înainte de testul rapid al fiecărei ore, `torch.cuda.empty_cache()` și citirea `nvidia-smi`; dacă e peste 6.700 MB, oprire curată cu cod ≠ 0 și mesaj clar în log (ora, MB). Teste noi în `teste/` (fără placă: citirea `nvidia-smi` simulată) — sub prag continuă, peste prag oprește cu cod ≠ 0.
  3b. **(adăugat de supraveghetor, 7 nov 02:15, după S85 — a doua cădere identică la testul rapid de la ora 3):** în unealta de la pasul 1, pentru varianta (a) faci **de 3 ori la rând** „~200 de pași + test rapid/validare”, în același proces (ca 3 „ore” scurte), și scrii înainte și după fiecare test rapid `torch.cuda.memory_allocated()`, `memory_reserved()` și `nvidia-smi`. Întrebarea: **crește memoria ținută de la o „oră” la alta** (ceva rămâne ținut după test, de ex. graficul, loturile sau rezultatele examenului)? Dacă da, o variantă cu `del` + `gc.collect()` + `torch.cuda.empty_cache()` după fiecare test rapid, aceleași 3 repetări, și scrii dacă astfel memoria nu mai crește. Tot în raport: ce anume ține memoria (cel mai probabil, după ce găsești în cod — cu linia din `unelte/antrenare_recalcul.py`). Dacă golirea ajută, o pui și în paza de la pasul 3 (doar `unelte/`, cu test nou). Nu atingi `kronos/`, `module/`.
  4. **Stări pe 8 biți:** NU instalezi nimic (ar cere `bitsandbytes` → „da”-ul lui Adrian). Doar scrii în raport cât ar câștiga, socotit pe hârtie.
  5. Pre-înregistrare scurtă `python unelte/preinregistrare.py --nume memorie_mare --titlu "S86: memoria plăcii la modelul mare, Muon față de AdamW"` cu așteptarea: „(b) muon lot 4 scade vârful PyTorch la antrenare cu cel puțin 400 MB față de (a)” — DA/NU, fără alt prag; commit + push înainte de partea pe placă.
  6. `python -m pytest` (toate trec); raport `docs/rapoarte/<data>_<ora>_S86_memorie_mare.md` (tabelul variantelor, care lot încape cu Muon, recomandarea pentru o noapte viitoare — fără s-o pornești); închizi pre-înregistrarea; coada → `gata`; commit + push. Dosarul `lucru/memorie_mare/` rămâne (ștergerea cere „da”-ul lui Adrian).
- Nu atingi `kronos/`, `module/` (doar citit), `module/examen_bpb.py`, paznicul, jurnalul, #459/#477/#513, `gpt_24.pt` (doar citit, SHA înainte = după), liniile `w2_mare_24*`. Nimic descărcat, instalat sau șters. Nimic din `lucru/` în Git.
- pre-înregistrare: docs/preinregistrari/<data>_memorie_mare.md (de scris înainte de partea pe placă)
- aprobat de: Adrian (COMENZI.md C-85, 6 nov 2026 17:56, pasul 2)
- raport: docs/rapoarte/2026-11-07_0406_S86_memorie_mare.md

### S87 — C-85 pasul 2, continuare (3b): crește memoria plăcii de la o oră la alta? 3 „ore” scurte cu Muon lot 4 × 24, în ordinea orchestratorului, cu și fără golire (placă ~1–1,5 h)
- stare: gata (executant, 7 nov 2026 10:04; măsurarea 08:46–09:50 cod 0; P1 = DA: fără golire 0 → 1.341 → 1.355 MB ținuți la începutul orelor, (b_orch) out of memory la ora 3 în antrenare; P2 = DA: cu gc.collect + empty_cache 16 MB, 3 ore, vârf 6.399 MB; gc.collect pus în paza din `unelte/antrenare_recalcul.py` + 2 teste; 1288 teste trec, 1 sărit; placa max 62 °C; SHA gpt_24 neschimbat)
- (istoric) stare: in_lucru (executant, 7 nov 2026 08:30; Adrian inactiv ~10,9 h, placa liberă 474 MB / 23 °C). Unealta (`ore`) + 9 teste + pre-înregistrarea `2026-11-07_memorie_ore.md` în 5ffd7ac (1286 trec, 1 sărit), urcate înainte de placă. Proba cap-coadă 08:37–08:46 (b, `--golire del`, 2 ore × 1 pas, `lucru/cascada/S87_proba/proba/`, nu intră în verdict): cod 0, vârf 6.437 MB. Măsurarea pornită prin cascadă 08:46:45, proces 7708 → `lucru/memorie_ore/s87.json`, ~70 min.
- (istoric) stare: **aprobat** (supraveghetor, 7 nov 2026 05:15)
- tip: placă (măsurare, fără antrenare lungă) + procesor (unealtă, teste)
- fereastră: **zi, 7 nov 2026, 08:00–18:30** (totul gata până la 18:30; dacă nu apuci, noaptea 7→8 de la 19:00). Nimic pe placă dacă Adrian e la workstation.
- durată maximă: 1,5 ore pe placă + ~1 oră procesor
- de ce: S77c și S85 au căzut de două ori exact la testul rapid de la ora 3; proba din S86 (Muon, 2 ore) a arătat vârful urcând 2.289 → 4.390 MB de la ora 1 la ora 2. Fără răspuns nu pornim nicio noapte lungă cu modelul de 24 de straturi. Observație de la mine (citit în `kronos/orchestrator.py`, liniile ~191–231, NU se modifică): în orchestrator ordinea e **test rapid → antrenare → examen**, iar `model_test` rămâne ținut în memorie în timpul antrenării și examenului (e eliberat abia la ieșirea din experiment); unealta din S86 făcea ordinea invers.
- ce faci:
  1. În `unelte/masoara_memorie_mare.py` (doar `unelte/`) adaugi o opțiune `--ordine orchestrator` pentru `unul`: în fiecare „oră”, exact ca `kronos/orchestrator.py`: construiești `model_test`, test rapid (2 s + 500 de caractere) → construiești `model` → antrenare (50 de pași de optimizator, ca în S86) → validare (`ExamenBpb().examineaza` doar chemat + `dupa_examen`), cu `model_test` încă ținut. La sfârșitul orei nu ștergi nimic explicit (variabilele se suprascriu la ora următoare, ca la ieșirea din funcție). Scrii `memory_allocated`, `memory_reserved` și `nvidia-smi` **la începutul fiecărei ore** și înainte/după fiecare fază (ce face deja `faza`).
  2. **Variantele** (fiecare în proces nou, din copia `gpt_24.pt`, Muon lot 4 × 24, plafonul PyTorch 5.800 MB, 3 „ore”; te oprești la out of memory sau peste 6.700 MB nvidia-smi și notezi la ce oră și fază):
     (b_orch) ordinea orchestratorului, fără golire;
     (b_orch_gc) la fel, plus la **începutul fiecărei ore** `gc.collect()` + `torch.cuda.empty_cache()` (exact ce poate face cârligul din `unelte/antrenare_recalcul.py` dinaintea testului rapid);
     (b_orch_del) la fel ca (b_orch_gc), plus `del model_test` + `gc.collect()` + `empty_cache()` **înainte** de construirea lui `model` — doar ca informație (în orchestratorul real asta ar cere o schimbare în `kronos/`, deci „da”-ul lui Adrian; NU o faci în `kronos/`).
  3. Pre-înregistrare ÎNAINTE de partea pe placă: `python unelte/preinregistrare.py --nume memorie_ore --titlu "S87: crește memoria plăcii de la o oră la alta?"`, cu pragurile (scrise de supraveghetor, DA/NU):
     - **P1 „memoria crește”:** la (b_orch), `memory_allocated` la începutul orei 3 minus la începutul orei 1 ≥ **300 MB**, sau (b_orch) cade cu out of memory / trece de 6.700 MB înainte de sfârșitul orei 3 → DA; altfel NU.
     - **P2 „golirea ajută”:** (b_orch_gc) termină toate 3 orele, cu vârful nvidia-smi ≤ **6.600 MB** și creșterea de la P1 sub **100 MB** → DA; altfel NU.
     - informativ (fără prag): cât scade vârful la antrenare și la validare la (b_orch_del) față de (b_orch_gc).
     Commit + push înainte de placă.
  4. **Dacă P2 = DA:** pui `gc.collect()` înaintea lui `torch.cuda.empty_cache()` în paza din `unelte/antrenare_recalcul.py` (cârligul de la linia ~126–131), cu un test nou fără placă (că se cheamă `gc.collect` înainte de citire). **Dacă P2 = NU și (b_orch_del) trece:** NU schimbi nimic, scrii în raport schimbarea exactă din `kronos/orchestrator.py` (care rând, ce face) ca propunere pentru Adrian. Dacă niciuna nu trece: scrii ce se vede (unde crește, cu cât) și 1–2 variante.
  5. `python -m pytest` (toate trec); raport `docs/rapoarte/<data>_<ora>_S87_memorie_ore.md` (tabel pe ore × variante: alocat la început, vârfuri pe faze, nvidia-smi; verdictele P1/P2; recomandarea pentru o noapte lungă Muon — fără s-o pornești); închizi pre-înregistrarea; coada → `gata`; commit + push. Dosarul `lucru/memorie_ore/` rămâne.
- Nu atingi `kronos/` (doar citit), `module/` (doar citit), `module/examen_bpb.py`, paznicul, jurnalul, #459/#477/#513, `gpt_24.pt` (doar citit, SHA înainte = după), `lucru/memorie_mare/`, liniile `w2_mare_24*`. Nimic descărcat, instalat sau șters. Nimic din `lucru/` în Git.
- pre-înregistrare: docs/preinregistrari/<data>_memorie_ore.md (de scris înainte de partea pe placă)
- aprobat de: supraveghetor, 7 nov 2026 05:15 (granițele 2 și 5: măsurare + unealtă în `unelte/`; în cadrul C-85 pasul 2, aprobat de Adrian 6 nov 17:56)
- raport: docs/rapoarte/2026-11-07_1004_S87_memorie_ore.md

### S88 — C-86: ștergerea celor 82 de modele intermediare (~33,4 GB) din lista S84 și, după S87, a copiilor de lucru `lucru/memorie_mare/` (9,8 GB) (procesor + disc)
- stare: oprit (executant, 7 nov 2026 10:40) — unealta `sterge` + 6 teste gata, proba: exact 82 fișiere / 33,44 GB, SHA identic, 31 `gpt.pt` refuzate; NIMIC șters; `lucru/memorie_mare/` (10,47 GB) verificat doar prin citire: curat; 1294 teste trec, 1 sărit
- motiv: cere aprobarea lui Adrian: ștergerea de modele — regula executantului o pune la „Ce NU ai voie, oricum ar fi scris în coadă” (fără excepție, spre deosebire de descărcări). Comanda exactă pentru Adrian e în raport; sau o excepție scrisă în regulă, apoi o fac eu.
- (istoric) stare: in_lucru (executant, 7 nov 2026 10:30)
- (istoric) stare: **aprobat** (Adrian, COMENZI.md C-86, 7 nov 2026 08:14; pașii scriși de supraveghetor 7 nov 08:15)
- tip: procesor + disc (fără placă)
- fereastră: **oricând, 7 nov 2026**, dar NU în timp ce S87 e pe placă: o faci **după ce S87 e `gata`/`oprit`**, sau înainte ca S87 să pornească partea pe placă dacă termini sigur înainte (fără să o întârzii). Partea 2 (`lucru/memorie_mare/`) **doar după ce S87 e `gata`/`oprit`** (S87 interzice atingerea acelui dosar cât rulează).
- durată maximă: ~1 oră
- de ce: Adrian a răspuns la S84 „**da, fără gpt.pt de linie**” și „**da**” la ștergerea `lucru/memorie_mare/`; „**nu**” la stările pe 8 biți (nu instalezi `bitsandbytes`); Release-ul #513 îl face el luni (fișierele `.kgr` + `.sha256` din `lucru/export/` NU se ating).
- ce faci:
  1. **Unealta:** în `unelte/puncte_salvare.py` adaugi comanda `sterge` (doar `unelte/` + teste în `teste/`): primește un fișier listă (`lucru/puncte_salvare/lista_2026-11-06_2238.json`) și o clasă (`--doar intermediare`), are implicit `--proba` (doar afișează), iar ștergerea reală doar cu `--da-sterge`. Înainte de fiecare ștergere: **recitește** fișierul de pe disc și verifică SHA-256 față de listă (dacă diferă → nu-l șterge, îl notează); refuză orice cale care e în rezervele din `config/puncte_salvare.toml`, e câștigătorul unei linii, e numită într-o pre-înregistrare deschisă sau e unul din: **#459, #477, #513, `lucru/cod_c1/gpt.pt`, `lucru/w2_mare/gpt_24.pt`, modelul în uz, orice `gpt.pt` de linie, orice din `lucru/export/`**. Refuză orice cale din afara `lucru/stocare/modele/`. Teste noi (pe fișiere temporare): proba nu șterge nimic; rezervele și `gpt.pt` sunt refuzate; SHA diferit → nu se șterge; jurnalul de ștergere se scrie ÎNAINTE de ștergere.
  2. **Jurnalul ștergerii** (nu jurnalul `kronos/`, care nu se editează de mână): `lucru/puncte_salvare/sterse_2026-11-07.json` + același tabel în raport (în Git): pentru fiecare model — calea, numărul experimentului, mărimea, SHA-256, scorul (`val_bpb` din jurnal), scris **înainte** de ștergere.
  3. **Partea 1:** `python unelte/puncte_salvare.py sterge --lista lucru/puncte_salvare/lista_2026-11-06_2238.json --doar intermediare` (proba) → verifici: exact cele **82** de fișiere din `lucru/stocare/modele/`, ~33,4 GB, **niciun `gpt.pt` de linie, nicio rezervă**. Dacă numărul sau GB diferă cu mai mult de 1 fișier / 0,5 GB față de S84, te oprești și scrii de ce (stare `oprit`). Apoi aceeași comandă cu `--da-sterge`. După: `python unelte/puncte_salvare.py lista` din nou și GB liberi pe C: înainte/după.
  4. **Partea 2 (după S87 `gata`/`oprit`):** verifici că în `lucru/memorie_mare/` nu e nimic unic: niciun model numit sau câștigător (copiile `gpt.pt` sunt copii ale `gpt_24.pt` — compari SHA-256 sau notezi că sunt stări după ~200 de pași de măsurare, nefolosite nicăieri), nicio cale din `lucru/memorie_mare/` folosită de vreo configurare sau pre-înregistrare deschisă (caută cu grep în `config/`, `docs/preinregistrari/`). Dacă e totul curat, ștergi dosarul întreg și notezi GB eliberați; dacă găsești ceva unic, NU ștergi și scrii ce ai găsit. `lucru/memorie_ore/` (S87) **nu** se șterge.
  5. `python -m pytest` (toate trec); raport `docs/rapoarte/<data>_<ora>_S88_stergere.md` (cele 82 cu SHA și scor, ce s-a refuzat și de ce, GB eliberați pe părți, spațiul C: înainte/după); un rând sus în `plan/pentru_adrian.md`; coada → `gata`; commit + push.
- Nu atingi `kronos/`, `module/`, examenul, paznicul, jurnalul `kronos/`, `lucru/export/`, niciun `gpt.pt` de linie, rezervele, modelul în uz. Nimic descărcat sau instalat (nici `bitsandbytes`). Nimic din `lucru/` în Git.
- aprobat de: Adrian (COMENZI.md C-86 punctele 1 și 3, 7 nov 2026 08:14)
- raport: docs/rapoarte/2026-11-07_1040_S88_stergere.md

### S89 — Reluarea S85: 5 ore pe Kronos de 24 de straturi, rețeta e1 neschimbată, linie nouă `w2_mare_24g`, cu paza nouă (gc.collect la fiecare oră) — e mai bun decât #513 la timp egal? (placa, ~6,5 h)
- verificat de supraveghetor (8 nov 2026 02:15): **LA FEL** confirmat — 1,2063 e între 1,2010 și 1,2110; cod 0,7243 ≤ 0,7320, R2 0,4052 ≤ 0,4110, R1 99,20 / 100 peste 90 / 98. Așteptarea de memorie NU = greșeală de așteptare (model + AdamW ~3,6 GB între ore), nu de pază; memoria nu mai crește.
- stare: gata (executant, 8 nov 2026 01:30) — **LA FEL**: română curat #536 1,2063 față de #513 1,2060 (praguri 1,2010 / 1,2110), fără STRICĂ (cod 0,7243, R2 0,4052, R1 instr. 99,20, vechi 100); toate 5 orele trecute (vârf 6.465 MB, 62 °C); așteptarea de memorie NU (după golire ~3.650 MB constant, nu ≤ 1.000 — modelul + AdamW); SHA neschimbate; 1318 teste trec, 1 sărit
- (istoric) stare: in_lucru (executant, 7 nov 2026 19:30; fereastra de noapte, placa liberă 450 MB / 25 °C; C: 80 GB liberi; `gc.collect()` în paza din `unelte/antrenare_recalcul.py`; `lucru/w2_mare_24g/` nu există). Configurarea + pre-înregistrarea `2026-11-07_w2_mare_24g.md` în 8056bdd, urcate înainte de placă. Lanțul `lucru/cascada/S89_proba/s89.py` (copia lui s85.py + verificarea gc.collect + citirile nvidia-smi în `smi.jsonl`) pornit prin cascadă 19:31:30, proces 25092.
- (istoric) stare: **aprobat** (supraveghetor, 7 nov 2026 11:15)
- tip: placă (antrenare 5 ore + examene ~1–1,5 ore)
- fereastră: **noaptea 7→8 nov, pornire de la 19:00, cel târziu la 00:30**; examenele gata până la 07:45. Dacă nu pornește până la 00:30, rămâne `aprobat` pentru noaptea 8→9 de la 19:00 (refaci pre-înregistrarea cu data nouă). Nimic pe placă dacă Adrian e la workstation (vezi notele de sus / hub).
- durată maximă: 5 ore de antrenare + examene; placa sub **6.700 MB** (paza de la fiecare oră + verificarea de la 15 minute) / 7.000 MB (paznicul) și sub 83 °C.
- de ce: S85 a căzut la ora 3 din cauza memoriei ținute de la o oră la alta (a doua oară după S77c). S87 a arătat cauza (~1.340 MB rămași din ora trecută, eliberați de `gc.collect`) și leacul e acum în paza din `unelte/antrenare_recalcul.py` (commit e0e78bf). Întrebarea S77b/S85 a rămas fără răspuns: la timp egal (5 ore), modelul de 24 de straturi ajunge mai bun decât #513? Rețeta e1 a ȚINUT (S77e) și primele 2 ore din S85 au mers; deci reluăm exact aceeași rețetă (AdamW), ca să schimbăm un singur lucru: paza. Muon rămâne pentru mai târziu (n-a fost încercat ca rețetă pe modelul mare).
- ce faci — **exact ca la S85 (pașii 0–5 de acolo), cu DOAR aceste diferențe:**
  0. Verificări în plus: `unelte/antrenare_recalcul.py` conține `gc.collect()` în `verifica_memoria` (commit e0e78bf); `lucru/w2_mare_24g/` **nu există**; C: ≥ 20 GB liber; `gpt_24.pt` SHA `d35e3dbe…92cc`. `lucru/w2_mare_24f/` (S85) rămâne neatins.
  1. `config/conv_w2_mare_24g.toml` = **copia lui `config/conv_w2_mare_24f.toml`** cu DOAR `nume = "w2_mare_24g"`, `cale_stare = "lucru/w2_mare_24g/gpt.pt"`, eticheta și antetul (diff-ul în raport). Copiezi `gpt_24.pt` ca `lucru/w2_mare_24g/gpt.pt` + verificarea din S77b pasul 3 (scorul de pornire = #477 ± 0,001).
  2. Pre-înregistrarea `python unelte/preinregistrare.py --nume w2_mare_24g --titlu "S89: reluarea S85 cu paza care golește memoria la fiecare oră"` cu **pragurile S85 copiate exact** (MAI MARE = MAI BUN / LA FEL / MAI SLAB / STRICĂ, aceleași cifre, #477 și #513 re-măsurați în aceeași rulare) + propoziția „singura diferență față de S85: `gc.collect()` în paza de la începutul fiecărei ore (S87)”. Și o așteptare de memorie, DA/NU: **„toate cele 5 ore trec; la începutul orelor 2–5 paza citește cel mult 1.000 MB `nvidia-smi` după golire”**. Commit + push **ÎNAINTE** de pornire.
  3. Lanțul prin cascadă: `python unelte/antrenare_recalcul.py --config config/conv_w2_mare_24g.toml --ore 5`, apoi `examen_validari_ws.py --linie w2_mare_24g`, `--experiment 477`, `--experiment 513`, apoi `romana_raspunsuri.py reper --experiment <ultimul experiment al liniei w2_mare_24g> --iesire lucru/romana_raspunsuri/reper_s89 …` (aceleași setări ca la S85). Plafonul PyTorch 5.800 MB rămâne.
  4. Dacă o oră e anulată (out of memory sau paza > 6.700 MB): ca la S85 pasul 4 — doar validările pe ultimul model al liniei (informativ), verdict **NEMĂSURAT**, `oprit`, raport cu ora, faza, vârful PyTorch și `nvidia-smi` și ce a citit paza la începutul fiecărei ore; nimic repornit.
  5. Raport `docs/rapoarte/<data>_<ora>_S89_kronos_mare_5ore.md` ca la S85, plus tabelul „paza la începutul fiecărei ore” (MB `nvidia-smi` după golire); SHA #477, #513, `gpt_24.pt` înainte = după; pre-înregistrarea închisă; `python -m pytest` verde; coada → `gata` cu verdictul într-o propoziție; commit + push.
- Ce urmează (scris acum): MAI MARE = MAI BUN → îl întreb pe Adrian dacă modelul mare devine linia principală (+ o a doua noapte de continuare); LA FEL / MAI SLAB fără STRICĂ → mă uit la curbă (urcă încă la ora 5 → o noapte de continuare; plată → încercăm rețeta Muon, care lasă mai multă memorie); STRICĂ → oprim liniile de 24.
- Modelul nou **nu** înlocuiește #513/#477 nicăieri fără „da”-ul lui Adrian. Nu atingi `kronos/`, `module/`, `module/examen_bpb.py`, paznicul, jurnalul (doar prin platformă), setul ascuns (doar citit de `reper`), #459/#477/#513, `gpt_24.pt` (doar citit), `lucru/w2_mare_24*/` existente. Nimic descărcat, instalat sau șters. Nimic din `lucru/` în Git.
- pre-înregistrare: docs/preinregistrari/<data>_w2_mare_24g.md (de scris înainte de pornire)
- aprobat de: supraveghetor, 7 nov 2026 11:15 (granițele 1 și 2: aceeași linie de 24 de straturi, aceeași rețetă e1 deja rulată; linia de 24 și recalculul acoperite de COMENZI.md C-64, Adrian 4 nov; paza din S86/S87, C-85 pasul 2)
- raport: docs/rapoarte/2026-11-08_0130_S89_kronos_mare_5ore.md

### S90 — C-85 pasul 3: examenul de română ca modul `module/examen_romana.py` (port `examen`, MANIFEST, trece `teste_contracte/`), NEACTIVAT în nicio configurare (doar procesor)
- stare: gata (executant, 7 nov 2026 12:26) — `romana_bpb` #513 1,20601 (reper 1,2060), #477 1,20962 (reper 1,2097), ambele în ± 0,001; `r1_ascuns` #513 pe procesor 99,27 = S76b (dif. 0,00), 2,73 s/întrebare (~23 min); amprentele verificate la fiecare notare; neactivat în nicio configurare; SHA #513/#477 neschimbate; 1306 teste trec, 1 sărit. Prima rulare a scriptului de verificare a căzut pe o cheie lipsă din nota S76b (scriptul meu, nu modulul) → reluată cap-coadă, cod 0
- (istoric) stare: in_lucru (executant, 7 nov 2026 11:30; placa liberă, nimic altceva în lucru)
- (istoric) stare: **aprobat** (supraveghetor, 7 nov 2026 11:15)
- tip: procesor (`CUDA_VISIBLE_DEVICES=-1` pentru tot)
- fereastră: **oricând de azi, 7 nov**; ziua imediat (placa nu e folosită). Dacă S89 a pornit: doar după verificarea de la 15 minute a lui S89 și cu regula de 10 % la pași/s (dacă scad cu peste 10 %, pui S90 pe pauză până după S89).
- durată maximă: ~3 ore procesor; RAM cel mult ~6 GB
- de ce: Adrian a spus „Da” la C-85; pasul 3 = un al doilea examen oficial, pe română (ținta reală, C-64), fără să se schimbe `examen_bpb` sau `kronos/` (regula nucleului, DECIZII 6 nov 17:59). Azi doar construim și verificăm modulul; folosirea lui într-o configurare vine separat, cu „da”-ul lui Adrian (paznicul îi memorează amprenta la prima rulare).
- ce faci:
  1. **Modulul** `module/examen_romana.py`, clasa `ExamenRomana`, după modelul lui `module/examen_cod_validare.py`: `MANIFEST` (nume `examen_romana`, port `examen`, versiune `0.1.0`, `versiune_contract` 1, permisiuni `citire_fisier`), `scor_principal = "romana_bpb"`, `mai_mic_e_mai_bun = True`. `examineaza(model, date)` întoarce **`romana_bpb`** = biți pe octet pe validarea „română curat”, **exact aceeași regulă și aceleași caractere** ca `unelte/examen_validari_ws.py` (refolosești funcția de acolo sau o muți într-un loc comun din `unelte/` fără să schimbi rezultatul). Opțional, setarea `cu_r1 = true` adaugă **`r1_ascuns`** = nota automată pe setul ascuns de 500 (ca `romana_raspunsuri.py reper`), implicit `false` (e lent).
  2. **Protecția setului:** în modul, amprentele SHA-256 ale fișierului de validare „română curat” și ale setului ascuns sunt scrise ca constante; la fiecare `examineaza` modulul le recalculează și **refuză** (excepție clară) dacă diferă. Fără nimic în `kronos/` sau în paznic.
  3. **Teste:** adaugi `("examen", "module.examen_romana:ExamenRomana", {...})` în lista `MODULE` din `teste_contracte/test_contracte.py` (pe un fișier mic temporar, ca la celelalte examene); teste noi în `teste/test_examen_romana.py`: amprentă greșită → refuz; același model → același scor de două ori; `cu_r1` implicit oprit; modulul nu importă nimic din `kronos/` în afară de contracte (dacă e nevoie).
  4. **Verificarea pe modele reale (procesor):** `romana_bpb` pe **#513** și **#477** trebuie să fie egal cu „română curat” din ultimele măsurători ale lui `examen_validari_ws.py` (#513 **1,2060**, #477 **1,2097** — S85 / S77e, măsurate pe placă) **± 0,001**. Dacă diferă mai mult: `oprit`, scrii diferența și de unde vine. Apoi `r1_ascuns` pe #513 cu `cu_r1 = true`: dacă durează peste 90 de minute pe procesor, îl oprești și scrii timpul pe item; altfel compari cu R1 al lui #513 din `reper_s76b` (diferență așteptată ≤ 1,0 punct; dacă e mai mare, scrii de ce — de ex. procesor față de placă — fără să schimbi nimic).
  5. `python -m pytest` (toate trec); raport `docs/rapoarte/<data>_<ora>_S90_examen_romana.md` (ce face modulul, amprentele, cifrele de la pasul 4, cât durează pe procesor, cum s-ar activa într-o configurare — DOAR propunere pentru Adrian); un rând sus în `plan/pentru_adrian.md`; coada → `gata`; commit + push.
- Nu atingi `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, nicio configurare din `config/` (modulul NU se pune în nicio configurare), setul ascuns (doar citit), modelele (doar citite). Nimic descărcat, instalat sau șters. Nimic din `lucru/` în Git.
- pre-înregistrare: nu e antrenare (pragul: ± 0,001 față de `examen_validari_ws.py` la #513 și #477)
- aprobat de: Adrian (COMENZI.md C-85 pasul 3, 6 nov 2026 17:56); pașii scriși de supraveghetor 7 nov 2026 11:15 (granițele 2 și 5)
- raport: docs/rapoarte/2026-11-07_1226_S90_examen_romana.md

### S91 — C-85 pasul 4 (partea a): „cercetătorul cu model trimis în avans” — unealta și testele, DOAR pe procesor, fără placă, fără antrenare reală
- stare: gata — **verificat de supraveghetor 7 nov 17:15: GATA corect** (commit 4ab6aef: doar fișiere noi `unelte/cercetator_avans.py`, `teste/test_cercetator_avans.py`, `config/avans_proba_mic.toml` + raport/plan; `kronos/`, `module/`, configurările existente neatinse; 1318 teste trec). Lecția (valori absolute ×300) → **S92** (modul relativ + modelul mic).
- (istoric) stare: gata (executant, 7 nov 2026 14:40) — `unelte/cercetator_avans.py` (proba implicit; refuză mărimea modelului și setările care nu există pe cel mare, ÎNAINTE de antrenare; tot ce scrie platforma merge în `--iesire`; `propunere_mare.toml` verificată = mare + doar câștigătorul); `kronos/` neschimbat; 12 teste noi; demonstrația pe procesor (GPT 2×64, 5 × 1 min, 320 s, cod 0): câștigător rata 0,003 / încălzire 400, val_bpb 2,6091 vs plecare 2,7320 — propunerea NU e de rulat (valoare absolută, ×300 față de linia mare) → planul b propune schimbări relative + Spearman ρ ≥ 0,7 pe 5 rețete; 1318 teste trec, 1 sărit
- (istoric) stare: in_lucru (executant, 7 nov 2026 14:30; placa liberă 450 MB / 25 °C, nimic altceva în lucru)
- (istoric) stare: aprobat (supraveghetor, 7 nov 2026 14:15)
- tip: procesor (`CUDA_VISIBLE_DEVICES=-1` pentru tot)
- fereastră: **oricând de azi, 7 nov, după ce ai citit asta**; dacă S89 a pornit pe placă: doar după verificarea de la 15 minute a lui S89 și cu regula de 10 % la pași/s (dacă scad cu peste 10 %, pui S91 pe pauză până după S89). S89 are prioritate.
- durată maximă: ~3 ore procesor; RAM cel mult ~6 GB
- de ce: Adrian a spus „Da” la C-85; pasul 4 = cercetătorul nu mai încearcă rețete direct pe modelul mare (scump: o încercare = o oră pe placă), ci întâi pe un model mic „trimis în avans”, iar pe cel mare merge doar câștigătorul. Azi construim doar unealta și o verificăm pe modele minuscule pe procesor; dacă un clasament pe modelul mic prezice clasamentul pe cel mare se măsoară separat, pe placă, într-o sarcină următoare (cu pre-înregistrare).
- ce faci:
  1. **Citești întâi** cum folosește orchestratorul cercetătorul (`kronos/orchestrator.py`, doar citit) și cum pornesc antrenările uneltele existente (`unelte/antrenare_lunga.py`, `unelte/antrenare_recalcul.py`). **Regula nucleului:** totul se face din `unelte/` (+ teste), cu ce oferă deja `kronos/` (Registru, citeste_config, Jurnal). Dacă se dovedește că nu se poate fără o schimbare în `kronos/`, te oprești (`oprit`) și scrii în raport exact ce ar trebui schimbat și de ce — eu îl întreb pe Adrian.
  2. **Unealta** `unelte/cercetator_avans.py`: primește `--config-mic` (configurarea modelului trimis în avans), `--config-mare` (linia pe care se aplică), `--incercari N`, `--minute-pe-incercare M` și `--iesire <dosar>`. Folosește cercetătorul din `--config-mic` (ex. `cercetator_local`) ca să propună N rețete, le încearcă pe modelul mic, notează fiecare cu examenul din `--config-mic`, și scrie în `<dosar>/clasament.json` + `clasament.md`: rețeta, scorul, timpul, amprenta modelului de pornire. La final scrie **o singură propunere** pentru `--config-mare` (`propunere_mare.toml` = configurarea mare cu DOAR setările câștigătorului schimbate, plus diff-ul) — **NU o rulează**. Setările care nu au sens pe modelul mare (ex. mărimea modelului) sunt refuzate cu un mesaj clar. Implicit `--proba` (afișează ce ar face, nu antrenează); antrenarea reală doar cu `--porneste`.
  3. **Teste** în `teste/test_cercetator_avans.py`, pe modele minuscule (configurări temporare, câteva secunde fiecare pe procesor): proba nu antrenează nimic; N încercări → N rânduri în clasament, fără rețete repetate; câștigătorul = cel mai bun scor (cu `mai_mic_e_mai_bun` respectat); `propunere_mare.toml` diferă de configurarea mare doar prin setările câștigătorului; setările interzise pe cel mare → refuz; nimic scris în `lucru/` în afara dosarului `--iesire`; unealta nu importă din `module/` direct (doar prin registru/configurare).
  4. **O rulare demonstrativă pe procesor** cu un model minuscul (ex. o configurare de laptop/jucărie existentă, redusă), 4–6 încercări × 1–2 minute, ca să se vadă clasamentul și propunerea scrisă. Fără placă, fără modelele #459/#477/#513/`gpt_24.pt`.
  5. **Planul pentru partea b (doar scris, în raport):** ce model mic ar fi „trimis în avans” pentru linia de 24 de straturi și pentru #513 (ex. o copie de 6 straturi crescută/tăiată din aceleași date — propui, nu creezi), câte încercări încap într-o fereastră de zi, și testul care ar arăta dacă metoda merge: **corelația de rang (Spearman) între clasamentul pe modelul mic și pe cel mare pe 4–5 rețete**, cu pragul propus (ex. ≥ 0,6 = DA). Asta va fi o sarcină separată, cu pre-înregistrare.
  6. `python -m pytest` (toate trec); raport `docs/rapoarte/<data>_<ora>_S91_cercetator_avans.md` (ce face unealta, testele, rularea demonstrativă cu clasamentul, planul pentru partea b); un rând sus în `plan/pentru_adrian.md`; coada → `gata`; commit + push.
- Nu atingi `kronos/`, `module/examen_bpb.py`, `module/examen_romana.py`, paznicul, jurnalul (doar prin platformă), nicio configurare existentă din `config/` (configurările noi de test stau în fișiere temporare sau în `config/` cu nume nou `avans_*` dacă e nevoie), modelele #459/#477/#513/`gpt_24.pt`, `lucru/w2_mare_24*/`. Nimic descărcat, instalat sau șters. Nimic din `lucru/` în Git.
- pre-înregistrare: nu e antrenare reală (doar modele minuscule de test); partea b, pe placă, va avea pre-înregistrare.
- aprobat de: Adrian (COMENZI.md C-85 pasul 4, 6 nov 2026 17:56); pașii scriși de supraveghetor 7 nov 2026 14:15 (granițele 5: unealtă nouă în `unelte/` + teste, fără `kronos/` și fără examen)
- raport: docs/rapoarte/2026-11-07_1440_S91_cercetator_avans.md

### S92 — C-85 pasul 4 (partea b, unealta): schimbări RELATIVE în `cercetator_avans.py` + modelul mic de 6 straturi tăiat din `gpt_24.pt` (doar procesor, fără placă)
- verificat de supraveghetor (8 nov 2026 02:15): GATA — unealta, `mic6`, configurarea și proba ca în pașii 1–6; propunerea de pre-înregistrare preluată în S94 (cu ×4 în loc de încălzire ×0,5, reparare de 45 min, rețete separate).
- stare: gata (8 nov 2026 02:11; `--relativ` + `creste_model.py taie` + `config/avans_24_mic6.toml`; mic6 = blocurile 0, 4, 8, 14, 18, 22 din gpt_24.pt, SHA 6507546b…9e26, română la pornire 2,7783; gpt_24.pt SHA neschimbat; proba fără --porneste; 1328 teste trec, 1 sărit)
- (istoric) stare: in_lucru (executant, 8 nov 2026 02:00; S89 gata, nimic altceva în lucru)
- (istoric) stare: **aprobat** (supraveghetor, 7 nov 2026 17:15)
- tip: procesor (`CUDA_VISIBLE_DEVICES=-1` pentru tot)
- fereastră: **după ce S89 a trecut verificarea de la 15 minute** (în noaptea 7→8), cu regula de 10 % la pași/s (dacă pașii lui S89 scad cu peste 10 %, pui S92 pe pauză până după S89); sau mâine, 8 nov, de la 08:00. **S89 are prioritate.** Dacă S89 nu pornește diseară, S92 poate merge imediat.
- durată maximă: ~3 ore procesor; RAM cel mult ~6 GB
- de ce: S91 a arătat că unealta mută pe modelul mare valori absolute (rata 0,003 → ×300 față de linia mare). Planul din raportul S91 (§5) e bun: schimbări relative față de rețeta liniei mari + un model mic din aceleași date și același tokenizer. Azi doar unealta, modelul mic și proba; testul pe placă (Spearman pe 5 rețete) vine separat, cu pre-înregistrare, după S89.
- ce faci:
  1. **Modul relativ în `unelte/cercetator_avans.py`** (opțiunea nouă `--relativ`; fără ea, totul ca acum — testele S91 trec neschimbate): spațiul cercetătorului din `--config-mic` se citește ca **factori** față de valorile din `--config-mare` pentru setările cu scară (`rata_invatare`, `incalzire_pasi`; altele doar dacă le scrii explicit în listă, cu motiv în raport); pe modelul mic se aplică factorul la valoarea **mică**, iar `propunere_mare.toml` = valoarea **mare** × factorul câștigător (rotunjire scrisă în raport; `incalzire_pasi` întreg). Setările fără scară (ex. `optimizator`, `racire_finala`) se mută ca valori, ca acum. Clasamentul arată și factorul, și valoarea folosită pe fiecare model.
  2. **Modelul mic:** comandă nouă `taie` în `unelte/creste_model.py` (comenzile existente neschimbate): `--din lucru/w2_mare/gpt_24.pt --straturi 6 --iesire lucru/avans/mic6/gpt.pt`. Citește `creste_stare`/`planul` ca să alegi **care** 6 blocuri se păstrează (modelul de 24 e crescut din 12 cu ieșire identică — scrii în raport ce blocuri iei și de ce; dacă nicio tăiere nu are sens, faci 6 × 768 de la zero cu aceeași rețetă și scrii de ce). Încorporările, normalizarea finală și capul se copiază. `gpt_24.pt` **doar citit**: SHA-256 `d35e3dbe…92cc` înainte = după.
  3. **Configurarea mică** `config/avans_24_mic6.toml` (fișier nou): copia lui `config/conv_w2_mare_24f.toml` cu DOAR `n_straturi = 6`, `cale_stare = "lucru/avans/mic6/gpt.pt"`, `nume`, eticheta/antetul și secțiunea `[porturi.cercetator]` (`cercetator_local`, spațiul relativ: rata × {0,5; 2; 4}, încălzire × {0,5; 2}). Diff-ul față de 24f în raport. Nu atinge nicio configurare existentă.
  4. **Teste** (în `teste/test_cercetator_avans.py` și `teste/test_creste_model.py` sau fișier nou), pe modele minuscule: factorul se aplică corect pe ambele modele; propunerea mare = valoarea mare × factor, restul fișierului identic; un factor ≤ 0 sau o setare fără valoare în configurarea mare → refuz; fără `--relativ`, rezultatele S91 identice; `taie` păstrează forma tensorilor (embedding, cap), refuză `--straturi` ≥ cele din sursă și nu scrie peste un fișier existent.
  5. **Proba pe procesor:** `cercetator_avans.py --relativ --config-mic config/avans_24_mic6.toml --config-mare config/conv_w2_mare_24f.toml --incercari 5 --iesire lucru/avans/s92_proba` **fără `--porneste`** (doar proba: cele 5 rețete și ce s-ar scrie). Apoi, informativ, `creste_model.py romana` pe `lucru/avans/mic6/gpt.pt` (procesor, 100.000 de caractere) — câți biți pe octet are modelul mic la pornire (față de 1,2096 la `gpt_24.pt`). Și o măsurare de viteză scurtă pe procesor NU e necesară — viteza pe placă o măsoară sarcina următoare.
  6. **Doar scris, în raport — propunerea de pre-înregistrare pentru partea pe placă (S93, o scriu eu după S89):** cele 5 rețete (punctul de plecare + 4 factori), minutele pe încercare pe modelul mic (câte simboluri vede, comparat cu 1 oră pe modelul mare), un singur scor ales (val_bpb SAU română curat), pragurile din S91: **ρ ≥ 0,7 și câștigătorul mic în primele 2 pe cel mare = DA; ρ ≤ 0,3 = NU; altfel NECLAR**, diferențe sub ~0,002 = egalitate. Câte ore de placă cere fiecare parte (zi: modelul mic; noapte: 5 × 1 oră pe cel mare).
  7. `python -m pytest` (toate trec); raport `docs/rapoarte/<data>_<ora>_S92_avans_relativ.md`; un rând sus în `plan/pentru_adrian.md`; coada → `gata`; commit + push.
- Nu atingi `kronos/`, `module/` (niciun modul), `module/examen_bpb.py`, `module/examen_romana.py`, paznicul, jurnalul (doar prin platformă), configurările existente, #459/#477/#513, `gpt_24.pt` (doar citit), `lucru/w2_mare_24*/` (S89 scrie acolo!). Nimic pe placă. Nimic descărcat, instalat sau șters. Nimic din `lucru/` în Git.
- pre-înregistrare: nu e antrenare (doar unealtă, tăiere și probă fără `--porneste`); partea pe placă (S93) va avea pre-înregistrare.
- aprobat de: Adrian (COMENZI.md C-85 pasul 4, 6 nov 2026 17:56); pașii scriși de supraveghetor 7 nov 2026 17:15 (granița 5: unelte noi în `unelte/` + teste, fără `kronos/` și fără examen; modelul mic e cel cerut de C-85 pasul 4)
- raport: docs/rapoarte/2026-11-08_0211_S92_avans_relativ.md

### S93 — C-88 („Română da”): examenul de română devine criteriul de decizie al experimentelor de română (de la următorul experiment; S89 neatins) — doar procesor
- stare: gata — **verificat de supraveghetor 8 nov 05:15: GATA corect** (commit 741e8d1: doar `config/conv_w2_mare_24r.toml` nou, `teste/test_examen_romana.py`, raport, plan; `kronos/`, `module/`, configurările existente neatinse; proba (a)–(d) ✓; 1332 teste trec). Regula X = 0,005 din raport (pasul 4) adoptată pentru S94 și liniile de română de acum încolo (C-88).
- (istoric) stare: gata (8 nov 2026 02:36; `config/conv_w2_mare_24r.toml` cu `examen_romana`, fără nimic în `kronos/`; proba (a)–(d) ✓ în `lucru/cascada/S93_proba/proba.json`; examen_bpb neschimbat 0ca9cf74…; 4 teste noi + `test_nu_e_in_nicio_configurare` → `test_doar_in_configurarile_aprobate` (S94 trebuie să adauge `avans_24_mic6r.toml`); 1332 teste trec, 1 sărit; propunerea X = 0,005 pentru val_bpb în raport)
- (istoric) stare: in_lucru (executant, 8 nov 2026 02:30; S92 gata, placa liberă, nimic altceva în lucru)
- (istoric) stare: **aprobat** (supraveghetor, 7 nov 2026 20:15)
- tip: procesor (`CUDA_VISIBLE_DEVICES=-1` pentru tot)
- fereastră: **după S92** (un singur lucru greu pe procesor o dată, cu regula de 10 % la pașii/s ai lui S89; dacă scad cu peste 10 %, pauză până după S89); sau **mâine, 8 nov, de la 08:00**. Trebuie `gata` înainte de următoarea noapte pe placă (8→9, 19:00). **S89 nu se atinge.**
- durată maximă: ~2 ore procesor; RAM cel mult ~6 GB
- de ce: Adrian a scris „Română da” (C-88): de acum, liniile de română sunt judecate după română (ținta reală, C-64), nu după poveștile din `examen_bpb`; `examen_bpb` rămâne **neschimbat** și se măsoară mai departe, doar ca verificare că nu se strică nimic. Orchestratorul are **un singur** port `examen` (scorul lui decide); `examen_bpb` rămâne măsurat de `examen_validari_ws.py` / `val_bpb` în lanțul de examene de după fiecare noapte. Paznicul memorează singur amprenta clasei noi la prima rulare și apoi refuză orice schimbare a ei — **fără nimic schimbat în `kronos/`**; setul îl păzesc amprentele din modul (S90) și testele.
- ce faci:
  0. **Citești doar** `kronos/orchestrator.py` și `kronos/paznic.py` (cum se alege și se păzește examenul). Dacă se dovedește că portul `examen` = `module.examen_romana:ExamenRomana` **nu** merge fără o schimbare în `kronos/` (sau în paznic), te oprești (`oprit`) și scrii exact de ce — eu îl întreb pe Adrian.
  1. **Configurarea pentru următorul experiment de română:** `config/conv_w2_mare_24r.toml` (fișier NOU) = copia lui `config/conv_w2_mare_24g.toml` cu DOAR: `nume = "w2_mare_24r"`, `cale_stare = "lucru/w2_mare_24r/gpt.pt"`, eticheta/antetul (scrie „examen de decizie: română, C-88”) și `[porturi.examen]` → `modul = "module.examen_romana:ExamenRomana"`, `setari = { caractere = 100000 }` (`cu_r1 = false`; R1 pe setul ascuns rămâne în `romana_raspunsuri.py reper`, după noapte). Diff-ul față de 24g în raport. **Nu atingi** `conv_w2_mare_24g.toml` (S89 o folosește), nici alte configurări existente, nici `lucru/w2_mare_24*/`. Rețeta (rata, lotul, optimizatorul) se alege abia după verdictul S89 — o scriu eu în sarcina de noapte; aici doar portul de examen.
  2. **Proba pe procesor, fără placă și fără modelele mari:** o configurare minusculă temporară (în `tmp_path` la teste sau `config/avans_romana_proba.toml`, nume nou) cu `[porturi.examen]` = `examen_romana` și un model de jucărie; 2 experimente scurte prin orchestrator, ca să se vadă: (a) scorul principal din fișă e `romana_bpb`; (b) paznicul a scris amprenta `module.examen_romana.ExamenRomana` în `amprente.json` din dosarul probei (NU în `lucru/` al liniilor reale); (c) a doua rulare trece; (d) o copie modificată a clasei → paznicul refuză. Totul doar în dosare temporare.
  3. **Teste noi** în `teste/test_examen_romana.py` (sau fișier nou): portul `examen` cu `examen_romana` dă decizia după `romana_bpb` (mai mic = mai bun); paznicul refuză un examen de română schimbat; `config/conv_w2_mare_24r.toml` diferă de 24g doar prin câmpurile de la pasul 1; `module/examen_bpb.py` are aceeași amprentă ca înainte.
  4. **Regula nouă pentru pre-înregistrări** (scrisă în raport, ca propunere de text; eu o pun în coadă): la liniile de română, pragurile de verdict se scriu pe **română curat (`romana_bpb`) + R1/R2 pe setul ascuns**; `val_bpb` (povești) doar „nu se strică: nu crește cu peste X”. Propui X după ultimele cifre (#513, #477, S89 dacă e gata).
  5. `python -m pytest` (toate trec); raport `docs/rapoarte/<data>_<ora>_S93_romana_decide.md` (ce s-a schimbat, diff-ul configurării, proba paznicului, testele, propunerea de la pasul 4); un rând sus în `plan/pentru_adrian.md`; coada → `gata`; commit + push.
- Nu atingi `kronos/`, `module/examen_bpb.py`, `module/examen_romana.py` (doar folosit; dacă trebuie schimbat, `oprit` și scrii de ce), paznicul, jurnalul (doar prin platformă), `amprente.json` al liniilor reale, setul ascuns (doar citit), configurările existente, #459/#477/#513, `gpt_24.pt`, `lucru/w2_mare_24*/`. Nimic pe placă. Nimic descărcat, instalat sau șters. Nimic din `lucru/` în Git.
- pre-înregistrare: nu e antrenare (doar configurare nouă, probă minusculă pe procesor și teste); primul experiment cu `conv_w2_mare_24r` va avea pre-înregistrare cu pragurile pe română.
- aprobat de: **Adrian (COMENZI.md C-88, 7 nov 2026 17:45)**; pașii scriși de supraveghetor 7 nov 2026 20:15 (granițele 2 și 5; `kronos/` și `examen_bpb` neatinse)
- raport: docs/rapoarte/2026-11-08_0236_S93_romana_decide.md

### S94 — C-85 pasul 4 (partea pe placă): prezice modelul mic de 6 straturi clasamentul rețetelor pe modelul de 24? (testul Spearman pe 5 rețete; a = modelul mic ziua, b = modelul mare noaptea)
- verificat de supraveghetor (9 nov 2026 02:15): **NU** confirmat — rangurile mic 3,5/5/2/1/3,5 și mare 2/2/4/5/2 dau ρ = −0,918 (≤ 0,3); câștigătorul mic (×4) pe locul 5; toate 5 orele măsurate, nicio anulare; C-88: ×2 strică codul (0,7314 > 0,7297), ×4 poveștile și codul. Mică greșeală în raport: fără egalități ρ pe valorile brute e −0,97, nu −1,00 (nu schimbă nimic). C-85 pasul 4 închis: cercetătorul cu modelul mic tăiat nu alege rata pentru cel de 24.
- stare: gata (executant, 9 nov 2026 01:05) — S94b: toate 5 ore măsurate (19:33–00:55, cod 0); **verdict NU, ρ = −0,92**: mare 2 (×0,5) 1,2102 ≈ 1 ≈ 5 1,2118 < 3 (×2) 1,2158 < 4 (×4) 1,2232, invers față de cel mic; câștigătorul mic (×4) ultimul; C-88: ×2 strică codul, ×4 poveștile și codul; nicio oră sub pornirea 1,2096; placa max 6.426 MB / 61 °C; SHA citite și `lucru/cache` neschimbate; pre-înregistrarea închisă; 1337 teste trec, 1 sărit
- (istoric) stare: in_lucru (executant, 8 nov 2026 19:32, pornit 19:33 prin cascadă, procesul 7320; română curat la pornire 1,2096 = #477 ✓; S94b: lanțul `lucru/cascada/S94_proba/s94b.py`, configurările în `lucru/avans/s94_mare/<k>/config.toml`, liniile `avans_s94_mare_<k>`; placa liberă 452 MB / 25 °C, Adrian inactiv ~33 h)
- (istoric) stare: aprobat (executant, 8 nov 2026 14:05 — DOAR pentru **S94b**, noaptea 8→9, de la 19:00, pornire cel târziu 00:30; S94a GATA: toate 5 încercările mici măsurate, clasamentul mic 4 < 3 < 1 ≈ 5 < 2, raport `docs/rapoarte/2026-11-08_1405_S94a_avans_mic.md`)
- (istoric) stare: in_lucru (executant, 8 nov 2026 11:30; S94a cu varianta (a), `lucru/cache` doar citit; placa liberă 452 MB / 25 °C, Adrian inactiv ~25 h)
- (istoric) stare: **aprobat** (supraveghetor, 8 nov 2026 11:15 — varianta (a) din raportul de oprire; vezi „adăugat de supraveghetor 8 nov 11:15” la final)
- (istoric) stare: oprit (executant, 8 nov 2026 08:52) — S94a: repararea anulată de paznic la 600 s („testul rapid a depășit limita”), placa goală (463 MB): cache-ul de simboluri într-un dosar nou și gol (`lucru/avans/s94_mic/cache`) → datele se tokenizau din nou pe procesor. Nimic antrenat; mic6 SHA neschimbat; mic6r nu există. `--separat`, `avans_24_mic6r.toml`, pre-înregistrarea (DESCHISĂ) gata, 1336 teste trec.
- motiv: comanda a picat (testul rapid > 600 s, cache gol); propun (a) `lucru/cache` doar citit / (b) copie a cache-ului — vezi raportul
- (istoric) stare: in_lucru (executant, 8 nov 2026 08:30; partea S94a)
- (istoric) stare: **aprobat** (supraveghetor, 8 nov 2026 02:15)
- tip: placă
- fereastră: **S94a — ziua de 8 nov, 08:00–18:30**, DOAR după ce **S93 e `gata`** (configurarea mică are nevoie de portul `examen_romana`; dacă S93 e `oprit`, S94 nu pornește — scrii în coadă și aștepți). Durată ~2,5 h pe placă; dacă nu poate porni până la 15:30, rămâne pentru ziua următoare liberă (NU luni 9 nov — ziua aia placa e a lui Adrian, C-83). **S94b — noaptea 8→9 nov, de la 19:00**, doar dacă S94a e `gata` cu toate 5 încercările măsurate; trebuie terminat (antrenare + note) până la **07:00 luni** — luni placa e a lui Adrian. Dacă S94b nu poate porni până la 00:30, nu pornește (rămâne pentru noaptea 9→10). Nimic pe placă dacă Adrian e la workstation.
- durată maximă: S94a ~2,5 h (reparare 45 min + 5 × 15 min + note); S94b 5 × 1 h + note (~6 h). Placa sub **6.700 MB** (paza din unealtă cu `gc.collect` + lanțul cu nvidia-smi la 5 s) / 7.000 MB paznicul, sub 83 °C.
- de ce: C-85 pasul 4 (aprobat de Adrian): rețetele se încearcă întâi pe un model mic și doar câștigătorul merge pe cel mare. Înainte să ne bazăm pe asta, trebuie verificat că ordinea rețetelor pe modelul mic seamănă cu cea de pe modelul mare. S89 (LA FEL cu #513 după 5 ore) arată că rețeta e1 nu e neapărat cea mai bună pentru modelul de 24 — exact întrebarea la care ar răspunde cercetătorul. Pașii vin din propunerea din raportul S92 (§6 și „Riscuri”), pe care o accept cu cele de mai jos.
- ce faci:
  0. **Pre-înregistrarea ÎNAINTE de orice antrenare** (`docs/preinregistrari/2026-11-08_avans_spearman.md`, `unelte/preinregistrare.py`), pentru AMBELE părți, cu: cele 5 rețete; minutele; scorul; pragurile de mai jos copiate exact; așteptările tale în cifre (ρ ghicit, câștigătorul ghicit pe fiecare model, șansele). Commit + push înainte de placă.
  1. **Configurarea mică nouă** `config/avans_24_mic6r.toml` = copia lui `config/avans_24_mic6.toml` cu DOAR: `nume = "avans_24_mic6r"`, eticheta/antetul, `cale_stare = "lucru/avans/mic6r/gpt.pt"`, `[porturi.examen]` = exact ca în `config/conv_w2_mare_24r.toml` din S93 (`module.examen_romana:ExamenRomana`, `caractere = 100000`, `cu_r1 = false`) și spațiul cercetătorului `rata_invatare = [0.5, 2.0, 4.0], incalzire_pasi = [2.0]`. Nicio configurare existentă atinsă. Diff în raport.
  2. **Rețetele strict SEPARATE** (riscul 2 din S92): fiecare din cele 5 încercări = rețeta de bază cu O SINGURĂ schimbare, pornită din același fișier: (1) bază (rata 1e-5, încălzire 1000), (2) rata ×0,5, (3) rata ×2, (4) rata ×4, (5) încălzire ×2. Dacă unealta le combină (o încercare păstrată devine baza celor de după), adaugi în `unelte/cercetator_avans.py` opțiunea `--separat` (fiecare rețetă față de bază, niciuna nu devine bază) + teste — granița 5, fără `kronos/`. Ordinea în care rulează rețetele: aceeași pe ambele modele.
  3. **S94a, placa, ziua:** (a) **repararea, o singură dată:** 45 min pe `lucru/avans/mic6/gpt.pt` cu rețeta de bază → `lucru/avans/mic6r/gpt.pt` (originalul mic6 neatins, SHA înainte = după); notezi română curat înainte (2,7783) și după. (b) cele 5 încercări pe modelul mic, câte **15 min** fiecare (fix, scris în pre-înregistrare — nu se ajustează după ce vezi viteza; viteza și simbolurile văzute doar le notezi), fiecare pornind din `mic6r/gpt.pt` (`stare_de_pornire`), scor `romana_bpb` după fiecare. `--porneste`, ieșirea în `lucru/avans/s94_mic/`. Clasamentul mic + propunerea pentru cel mare (nerulată) în raportul părții a.
  4. **S94b, placa, noaptea 8→9:** aceleași 5 rețete pe modelul de 24 de straturi, câte **1 oră** fiecare, FIECARE pornind dintr-o copie proaspătă a lui `lucru/w2_mare/gpt_24.pt` (SHA `d35e3dbe…92cc` înainte = după; nu din #536 și nu din încercarea dinainte), cu valorile „mare” din clasamentul mic (rata 5e-6 / 1e-5 / 2e-5 / 4e-5, încălzire 1000 / 2000), restul exact ca `config/conv_w2_mare_24r.toml` (lot 4 × 24, AdamW, paza cu `gc.collect`). Configurările mari în `lucru/avans/s94_mare/<k>/` sau `config/avans_s94_mare_<k>.toml` (fișiere noi). Scor `romana_bpb` după fiecare oră (aceeași măsură ca la cel mic). Dacă o încercare e anulată de pază: ea e NEMĂSURATĂ, celelalte continuă; cu mai puțin de 4 măsurate pe cel mare, verdictul e NEMĂSURAT.
  5. **Pragurile (din S91/S92, de copiat exact):** ρ Spearman între clasamentul mic și cel mare pe cele 5 rețete; diferențe sub **0,002** biți/octet = egalitate (rang mediu). **DA** = ρ ≥ **0,7** ȘI câștigătorul mic e în primele 2 pe cel mare; **NU** = ρ ≤ **0,3**; altfel **NECLAR**. Informativ: `val_bpb`, cod curat, placa max MB/°C, pași/s, simboluri văzute pe încercare (mic vs mare).
  6. `python -m pytest` (toate trec) la sfârșitul fiecărei părți; rapoarte `docs/rapoarte/<data>_<ora>_S94a_avans_mic.md` și `<data>_<ora>_S94b_spearman.md`; pre-înregistrarea închisă după S94b; un rând sus în `plan/pentru_adrian.md` după fiecare parte; coada → `in_lucru`/`gata`; commit + push.
- Nu atingi `kronos/`, `module/` (niciun modul), `module/examen_bpb.py`, `module/examen_romana.py`, paznicul, jurnalul (doar prin platformă), configurările existente (inclusiv `avans_24_mic6`, `conv_w2_mare_24g`, `conv_w2_mare_24r`), #459/#477/#513/#536, `gpt_24.pt` și `mic6/gpt.pt` (doar citite), `lucru/w2_mare_24*/`. Niciun model nou nu înlocuiește #513 nicăieri. Nimic descărcat, instalat sau șters. Nimic din `lucru/` în Git.
- pre-înregistrare: docs/preinregistrari/2026-11-08_avans_spearman.md (scrisă ÎNAINTE de S94a, acoperă ambele părți)
- aprobat de: Adrian (COMENZI.md C-85 pasul 4, 6 nov 2026 17:56 — modelul mic trimis în avans); pașii scriși de supraveghetor 8 nov 2026 02:15 (granițele 1, 2 și 5: rulări scurte pe modelul de 24 existent și pe modelul mic cerut de C-85, note, unealtă fără `kronos/`)
- raport: docs/rapoarte/<data>_<ora>_S94a_avans_mic.md și docs/rapoarte/<data>_<ora>_S94b_spearman.md; oprirea din 8 nov: docs/rapoarte/2026-11-08_0852_S94a_oprit_cache.md; S94a: docs/rapoarte/2026-11-08_1405_S94a_avans_mic.md; S94b: docs/rapoarte/2026-11-09_0105_S94b_spearman.md
- **adăugat de supraveghetor 8 nov 05:15 (după S93, nimic din pașii de mai sus schimbat):**
  - S93 e `gata` (verificat) → S94a poate porni azi de la 08:00.
  - Când scrii `config/avans_24_mic6r.toml`, adaugă-l în lista din `teste/test_examen_romana.py::test_doar_in_configurarile_aprobate` (cum cere raportul S93); altfel testul pică intenționat. E singura schimbare permisă la acel test.
  - Pornirea în S94a/S94b se face prin `cale_stare` / `stare_de_pornire` din fișierul `.pt`, NU cu `--porneste-din` dintr-o fișă veche (raportul S93, „De știut” 1: fișele vechi n-au `romana_bpb` → KeyError). Dacă unealta cere totuși fișa, oprești, nu repari `antrenare_lunga.py` fără sarcină.
  - Regula C-88 în pre-înregistrare (în plus față de Spearman): pe fiecare încercare notezi informativ și `val_bpb` (povești); pe modelul mare, o încercare cu `val_bpb` peste **0,4100** (#513 0,4050 + 0,005) sau cod curat peste **0,7297** e marcată „strică poveștile/codul” în raport — nu schimbă verdictul Spearman, dar o rețetă așa nu poate fi propusă pentru cel mare.
- **adăugat de supraveghetor 8 nov 11:15 (după oprirea S94a; verificat: motiv bun, nimic antrenat, `mic6` SHA neschimbat, placa n-a lucrat):**
  - **Varianta (a):** simbolurile se citesc din **`lucru/cache`** (cel al liniilor reale, același tokenizer și aceleași date), atât la reparare cât și la cele 5 încercări mici și la cele 5 mari din S94b. În `unelte/cercetator_avans.py`: opțiunea nouă `--cache <dosar>` (implicit ca acum, `<iesire>/cache`) + cel puțin un test (cu `--cache` dat, `director_cache` din toate încercările = dosarul dat; fără el, ca înainte). Repararea: `director_cache = "lucru/cache"` în scriptul din `lucru/cascada/`. Fără nicio schimbare în `kronos/`, `module/`, configurările existente.
  - **`lucru/cache` e doar citit.** Înainte de pornire notezi lista fișierelor din `lucru/cache` (nume, mărime, data) și o compari la final: nu trebuie să apară, să dispară sau să se schimbe nimic. Dacă la reparare platforma tot începe să facă simboluri de la zero (placa sub ~1.000 MB după 5 minute, sau un fișier nou în `lucru/cache`): oprești lanțul, S94 → `oprit`, și scrii ce cheie de cache nu s-a potrivit — NU încerci varianta (b) singur.
  - **Jurnal nou** pentru reparare: `lucru/avans/s94_reparare2/` (cel vechi, cu #1 anulat, rămâne neatins); ieșirea încercărilor mici rămâne `lucru/avans/s94_mic/` doar dacă e goală de rezultate, altfel `lucru/avans/s94_mic2/`. Scriptul lanțului: unul nou (ex. `s94a2.py`), nu cel vechi editat.
  - **Pre-înregistrarea rămâne aceeași** (nu s-a măsurat nimic): adaugi doar un rând datat „8 nov 11:15: repornire cu cache-ul `lucru/cache` (varianta a, oprirea din 08:52); pragurile, rețetele și minutele neschimbate”. Commit + push înainte de placă. Rețeta 5 rămâne cum e (asimetria e scrisă dinainte, la „Să nu uite” 1).
  - `python -m pytest` înainte de pornire (toate trec). Ferestrele rămân: S94a pornește **cel târziu la 15:30** (dacă nu, nu azi; nu luni 9 nov); S94b de la 19:00, pornire cel târziu 00:30, gata până la 07:00 luni, doar dacă S94a e `gata` cu toate 5 încercările măsurate.
- **adăugat de supraveghetor 8 nov 14:15 (după S94a, verificat GATA; nimic din pașii de mai sus schimbat):**
  - S94b folosește tot `--cache lucru/cache` (doar citit, aceeași verificare înainte/după ca la S94a) și pornește fiecare oră dintr-o copie proaspătă a lui `gpt_24.pt` (SHA notat înainte și după).
  - Pe modelul mare, după fiecare oră, pe lângă `romana_bpb` măsori și `val_bpb` (povești) și cod curat, ca regula C-88 (0,4100 / 0,7297) să se poată aplica. Dacă notele suplimentare ar împinge sfârșitul peste 07:00, le faci doar pe încercarea câștigătoare și pe bază și scrii în raport care au rămas nemăsurate — Spearman se calculează oricum doar pe `romana_bpb`.
  - În raportul S94b pui ambele clasamente unul lângă altul, rangurile (cu egalitățile sub 0,002 ca rang mediu, inclusiv 1 ≈ 5 pe cel mic: rang 3,5), ρ calculat și verdictul DA / NECLAR / NU / NEMĂSURAT exact după praguri. Închizi pre-înregistrarea. `propunere_mare.toml` NU se pornește.
  - La 07:00 luni placa trebuie să fie goală (C-83, testul OS al lui Adrian). Dacă la 06:30 încă rulează ceva, oprești încercarea curentă (NEMĂSURATĂ) și scrii raportul cu ce ai.

### S95 — Continuarea liniei de 24 de straturi: 5 ore din #536 cu rata ×0,5 (5e-6), linie nouă `w2_mare_24s`, judecată pe română (C-88) — trece de #513? (placa, ~6,5 h)
- stare: in_lucru (executant, 9 nov 2026 20:30; varianta (a); placa liberă 503 MB / 26 °C, nimic altceva în lucru; `lucru/w2_mare_24s/` nu există; C: 55 GB liberi). Copia #536 cu doar `minute = 0` (SHA `838e0d52…0b6c`; #536 `7e5f841d…3bd6` neschimbat; singura cheie diferită `minute`, `lucru/cascada/S95_proba/copie.json`); configurarea + pre-înregistrarea `2026-11-09_w2_mare_24s.md` în 3e7c723 (1343 teste trec, 1 sărit), urcate înainte de placă. Lanțul `lucru/cascada/S95_proba/s95.py` pornit prin cascadă 20:38:43, proces 19320; rata socotită 5e-6 la primul pas / 10 min / sfârșitul orei 1 (pe original ar fi fost 0); română curat pe copie 1,2062 (= #536 ± 0,001 ✓); antrenarea de la 20:40:50, estimat gata ~02:15 + examene ~03:00.
- (istoric) stare: **aprobat** (supraveghetor, 9 nov 2026 20:15) — **cu varianta (a)** din raportul executantului (vezi „adăugat de supraveghetor 9 nov 20:15” mai jos); fereastra C-94 neschimbată: pornire cel târziu **00:00**, placa liberă până la **06:45**
- (istoric) stare: oprit (executant, 9 nov 2026 19:36) — nimic pe placă, nimic antrenat
- motiv: fișierul lui #536 (`lucru/w2_mare_24g/gpt.pt`) are `minute = 300,01`; programul ratei (18.000 s, răcire la final până la 0) se socotește din minutele din stare → progres ≥ 1 de la primul pas → **rata 0 toate cele 5 ore**. Copia identică + programul neschimbat (cum cere sarcina) nu pot merge împreună. Variante: (a, recomandată) copia cu doar `minute = 0` (greutăți + AdamW + pasi_total păstrate); (b) copia ca `gpt_24.pt` (AdamW gol, pasi_total 0, minute 0). Dacă vine alegerea până pe la 23:00, încape la noapte (pornire ≤ 00:00, C-94). `experiment_536.pt` din stocare are alt format (fără `retea`/`optimizator`), nu merge ca `cale_stare`.
- raport: docs/rapoarte/2026-11-09_1936_S95_oprit_rata_zero.md
- (istoric) stare: in_lucru (executant, 9 nov 2026 19:30; C-94: pornire de la 19:30; placa liberă 503 MB / 26 °C, nimic altceva în lucru; `lucru/w2_mare_24s/` nu există; C: 55 GB liberi)
- (istoric) stare: **aprobat** (supraveghetor, 9 nov 2026 02:15)
- tip: placă (antrenare 5 ore + examene ~1–1,5 ore)
- fereastră: **noaptea 9→10 nov, pornire de la 19:00, cel târziu la 00:30**; examenele gata până la 07:45. Pornești DOAR dacă workstation-ul e înapoi în Windows după testul OS al lui Adrian (C-83) și nu există o notă nouă de la el (hub `COMENZI.md` sau aici) că mai lucrează. Dacă nu poate porni până la 00:30, rămâne `aprobat` pentru noaptea 10→11 de la 19:00 (refaci data în pre-înregistrare).
- durată maximă: 5 ore de antrenare + examene; placa sub **6.700 MB** (paza de la fiecare oră + verificarea de la 15 minute) / 7.000 MB (paznicul) și sub 83 °C.
- de ce: S89 („ce urmează”, scris dinainte): LA FEL fără STRICĂ și curba încă scade la ora 5 (R2 0,4076 → 0,4052, câștigul venit mai ales la răcire) → o noapte de continuare. S94b arată că pe modelul de 24, într-o oră, rata ×0,5 strică cel mai puțin (1,2102, cea mai bună din 5; ×2 și ×4 strică codul/poveștile). Deci continuăm din cel mai bun model de 24 (#536, 1,2063, la 0,0003 de #513), cu rata ×0,5 și răcirea la final, pe configurarea care decide pe română (`conv_w2_mare_24r`, S93/C-88). Granița 1: încă o rulare pe o linie existentă, mai multe ore, altă rată.
- ce faci:
  0. Verificări: `lucru/w2_mare_24s/` **nu există**; C: ≥ 20 GB liber; placa goală (sub ~600 MB); `python -m pytest` verde. Găsești fișierul lui **#536** (starea finală a liniei `w2_mare_24g`, `lucru/w2_mare_24g/gpt.pt`, sau copia din `lucru/stocare/modele/` dacă acolo e cea legată de #536 în jurnal) și îi notezi SHA-256; dacă nu poți lega sigur fișierul de #536 (jurnal / fișa experimentului), te oprești, `oprit`, și scrii de ce.
  1. `config/conv_w2_mare_24s.toml` (fișier NOU) = copia lui `config/conv_w2_mare_24r.toml` cu DOAR: `nume = "w2_mare_24s"`, `cale_stare = "lucru/w2_mare_24s/gpt.pt"`, rata de învățare **5e-6** (×0,5 față de e1), eticheta/antetul („S95: continuarea #536, rata ×0,5, examen de decizie: română, C-88”). Încălzirea, lotul 4 × 24, AdamW, recalculul, plafonul PyTorch 5.800 MB, paza cu `gc.collect`, programul ratei pe 18.000 s cu răcire la final — neschimbate. Diff-ul în raport. Adaugi `conv_w2_mare_24s` în lista din `teste/test_examen_romana.py::test_doar_in_configurarile_aprobate` (singura schimbare permisă la acel test).
  2. Copiezi fișierul #536 ca `lucru/w2_mare_24s/gpt.pt` (originalul doar citit, SHA înainte = după). Pornirea prin `cale_stare` din `.pt`, NU cu `--porneste-din` dintr-o fișă veche (S93, „De știut” 1). Verificarea de pornire: română curat pe copie = **1,2063 ± 0,001** (= #536); altfel oprești.
  3. **Pre-înregistrarea ÎNAINTE de placă:** `python unelte/preinregistrare.py --nume w2_mare_24s --titlu "S95: 5 ore din #536 cu rata x0,5, judecat pe romana"` → `docs/preinregistrari/<data>_w2_mare_24s.md`, cu pragurile de mai jos copiate exact, #513 și #536 re-măsurați în aceeași rulare, și așteptările tale în cifre (română ghicită la final, șanse MAI BUN / LA FEL / MAI SLAB). Commit + push înainte de pornire.
  4. **Pragurile (decide `romana_bpb`, română curat, C-88):** **MAI BUN** = ≤ #513 − 0,005 (**1,2010**); **MAI SLAB** = ≥ #513 + 0,005 (**1,2110**); altfel **LA FEL**. **STRICĂ** (oricare): `val_bpb` (povești) > **0,4100**, cod curat > **0,7297**, R1 instrucțiuni < 90, R1 felurile vechi < 98. Informativ (nu schimbă verdictul): **„crește încă”** = română ≤ #536 − 0,003 (≤ **1,2033**); curba pe ore (`romana_bpb` și `val_bpb` la fiecare oră, dacă unealta le dă), simboluri văzute, pași/s, placa max MB/°C.
  5. Lanțul prin cascadă: `python unelte/antrenare_recalcul.py --config config/conv_w2_mare_24s.toml --ore 5`, apoi `examen_validari_ws.py --linie w2_mare_24s`, `--experiment 513`, `--experiment 536`, apoi `romana_raspunsuri.py reper --experiment <ultimul experiment al liniei w2_mare_24s> --iesire lucru/romana_raspunsuri/reper_s95` (aceleași setări ca la S89). Simbolurile din `lucru/cache` (doar citit; lista fișierelor înainte = după, ca la S94).
  6. Dacă o oră e anulată (out of memory sau paza > 6.700 MB): doar validările pe ultimul model al liniei (informativ), verdict **NEMĂSURAT**, `oprit`, raport cu ora, faza și vârfurile; nimic repornit. La 06:30 dacă încă rulează antrenarea: o lași să termine doar dacă examenele încap până la 07:45, altfel oprești curat și scrii NEMĂSURAT.
  7. Raport `docs/rapoarte/<data>_<ora>_S95_mare_continuare.md` (tabelul pe ore, validările modelului nou, #513 și #536 una lângă alta, R1, verdictul strict după praguri, siguranța: SHA #513/#536/`gpt_24.pt` înainte = după); pre-înregistrarea închisă; `python -m pytest` verde; un rând sus în `plan/pentru_adrian.md`; coada → `gata` cu verdictul într-o propoziție; commit + push.
- **adăugat de supraveghetor 9 nov 20:15 — reparația pentru „rata 0” (varianta (a), aleasă de mine; granița 1, aceeași linie, doar ceasul programului ratei pe copie):** verificat raportul `docs/rapoarte/2026-11-09_1936_S95_oprit_rata_zero.md` — ai dreptate: cu `minute = 300,01` în stare, progresul e ≥ 1 de la primul pas și rata ar fi 0. Bună oprire. Înlocuiește pasul 2 așa:
  - 2a. Scriptul mic din `lucru/cascada/S95_proba/` citește `lucru/w2_mare_24g/gpt.pt` (#536, doar citit; SHA înainte = după) și scrie `lucru/w2_mare_24s/gpt.pt` cu **o singură schimbare: `minute = 0`**. Greutățile (`retea`), starea AdamW (`optimizator`), `pasi_total` (115.771), `setari`, `scor` — identice. În raport: SHA-ul originalului, SHA-ul copiei și dovada că singura cheie diferită e `minute` (comparație cheie cu cheie, tensorii egali bit cu bit).
  - 2b. Verificarea de pornire rămâne: română curat pe copie = **1,2063 ± 0,001**; altfel oprești.
  - 2c. **Verificarea nouă a ratei, la începutul antrenării:** la primul pas și după ~10 minute citești din jurnal/ieșire rata efectivă. Trebuie să fie **5e-6** (fără încălzire, fiindcă `pasi_total` > 1.000; răcirea abia în ultimele ~75 min). Dacă e 0, sau altceva decât 5e-6 ± 1 %, oprești curat imediat, `oprit`, raport — nu încerci altă variantă singur. Scrii în raport și rata la începutul fiecărei ore (curba programului).
  - Pragurile, examenele, lanțul, pre-înregistrarea (scrisă ÎNAINTE de placă, cu mențiunea „copia #536 cu `minute = 0`, varianta (a)”) și restul pașilor — neschimbate. Pornești la prima trecere după acest commit, cel târziu **00:00**; dacă nu încape până la 00:00, rămâne `aprobat` pentru noaptea 10→11 de la 19:00 (cu aceeași variantă (a)).
  - De ce (a), nu (b): păstrează starea AdamW „caldă” și dă loturi de text noi (sămânța depinde de `pasi_total`); (b) ar repeta loturile din prima oră a S89. (c) ar schimba programul — respins.
- **adăugat de supraveghetor 9 nov 19:10 — C-94 (Adrian), înlocuiește nota C-93 de mai jos pentru noaptea 9→10:** pornire **de la 19:30** (nu mai aștepți 21:00), cel târziu la **00:00**, doar dacă workstation-ul e în Windows și nu există o notă mai nouă de la Adrian că lucrează. Antrenarea + examenele **eliberează placa până la 06:45** (testul OS e la 07:15); la **05:30**, dacă antrenarea încă rulează, aplici punctul 6 cu limita 06:45. Restul notei C-93 (salvare la fiecare oră, întreruperea de la o repornire → NEMĂSURAT, `oprit` fără vină) rămâne valabil. Dacă nu poate porni până la 00:00, rămâne `aprobat` pentru noaptea 10→11 de la 19:00.
- **adăugat de supraveghetor 9 nov 14:15 — C-93 (Adrian), înlocuiește fereastra de mai sus pentru noaptea 9→10:** pornire **de la 21:00** (NU între 19:30 și 21:00), cel târziu la 00:30, DOAR dacă la 21:00 workstation-ul e în Windows fără să fi fost repornit în Cyber Universe după 19:30 și nu există o notă nouă de la Adrian (hub `COMENZI.md` sau aici) că lucrează. Antrenarea + examenele trebuie să **elibereze placa până la 07:45** (la 06:30 aplici punctul 6 cu limita 07:45). Lanțul salvează modelul la fiecare oră (asta cere C-93: să suporte o repornire). Dacă rularea e întreruptă de o repornire: NU o reporni singur; la prima trecere după, notezi orele terminate (model + notă existente), verdict **NEMĂSURAT** dacă nu s-au terminat toate 5 orele, `oprit` cu motivul „întrerupt de repornire (C-93)” — nu e o greșeală. Dacă nu poate porni la noapte, rămâne `aprobat` pentru noaptea 10→11 de la 19:00.
- **adăugat de supraveghetor 9 nov 08:15 — „eroarea după examen”:** raportul de dimineață a văzut în jurnalul Kronos, la fiecare oră din S94b și la S89 (#532–#536), o eroare de memorie a plăcii la un pas făcut DUPĂ examen (modelele s-au salvat, notele există). La S95: (a) în raport scrii pentru fiecare oră dacă apare, la ce pas exact (numele funcției/fazei din jurnal), vârful MB atunci și dacă modelul + nota orei există; (b) dacă modelul și nota orei există, ora contează normal (nu e anulare, nu `oprit`); dacă lipsește oricare, aplici punctul 6 (NEMĂSURAT, `oprit`); (c) nu repari nimic acum (dacă locul e în `kronos/`, doar descrii) — propui în raport 1–2 variante de reparație.
- Ce urmează (scris acum): MAI BUN → îl întreb pe Adrian dacă modelul de 24 devine linia principală (nu înlocuiește #513 fără „da”-ul lui); LA FEL cu „crește încă” → încă o noapte de continuare; LA FEL fără „crește încă” sau MAI SLAB → curba e plată la rata asta, următoarea idee e mai multe date pe noapte (C-85 pasul 5, date pe bucăți) sau Muon ca rețetă; STRICĂ → oprim continuarea și mă uit la ce s-a stricat.
- Nu atingi `kronos/`, `module/` (niciun modul), `module/examen_bpb.py`, `module/examen_romana.py`, paznicul, jurnalul (doar prin platformă), configurările existente, setul ascuns (doar citit de `reper`), #459/#477/#513/#536 și `gpt_24.pt` (doar citite), `lucru/w2_mare_24*/` existente, `lucru/cache`. Modelul nou **nu** înlocuiește #513 nicăieri. Nimic descărcat, instalat sau șters. Nimic din `lucru/` în Git.
- pre-înregistrare: docs/preinregistrari/<data>_w2_mare_24s.md (de scris înainte de pornire)
- aprobat de: supraveghetor, 9 nov 2026 02:15; fereastra: Adrian (COMENZI.md C-93 și C-94, 9 nov 2026) (granițele 1 și 2: aceeași linie de 24 de straturi, continuare din #536 cu altă rată; linia de 24 și recalculul acoperite de COMENZI.md C-64, Adrian 4 nov; examenul de română ca decizie: C-88)
- raport: docs/rapoarte/<data>_<ora>_S95_mare_continuare.md

### S96 — C-85 pasul 5: date pe bucăți (simboluri pre-făcute, citite pe rând) — unealta, proba de identitate și măsurarea memoriei, NEACTIVATĂ în nicio configurare (doar procesor + disc, fără placă)
- stare: gata — **verificat de supraveghetor 9 nov 17:15: GATA, DA corect** (commit 61c2e22: doar fișiere noi `unelte/date_bucati.py` + `teste/test_date_bucati.py`; `kronos/`, `module/`, `config/` neatinse; SHA-256 întreg identic cache = bucăți = index; `lucru/cache` neschimbat; 1343 teste trec). Pasul următor (legarea, varianta a) → **S98**
- (istoric) stare: gata (executant, 9 nov 2026 14:40; proba de identitate DA: 1.341.190.791 simboluri, același SHA-256 `560863a9…`; cititorul 125 MB RAM vs 3.084 MB acum; pornirea liniei ia 41,7 GB RAM din cauza textului brut; 27 de bucăți în `lucru/bucati/w2_amestec_be12/`, `lucru/cache` neatins; 1343 teste trec, 1 sărit)
- (istoric) stare: in_lucru (executant, 9 nov 2026 14:30; adus azi de C-93, placa liberă 503 MB / 27 °C, nimic altceva în lucru)
- (istoric) stare: **aprobat** (supraveghetor, 9 nov 2026 02:15)
- tip: procesor + disc
- fereastră: **marți 10 nov, ziua, de la 08:00, după ce S95 e `gata`/`oprit`** (nu în timpul nopții S95 și niciodată cât Adrian e la workstation). Durată ~2–3 h.
- de ce: C-85 pasul 5 (aprobat de Adrian): pregătirea pentru „super-școala de română” — când datele cresc, nu mai încap toate în memorie; trebuie citite din bucăți gata tokenizate. Pasul 4 s-a închis (S94, NU), deci urmează pasul 5.
- ce faci:
  1. **Întâi doar citire (în raport):** cum citește acum antrenarea datele (din ce fișiere din `lucru/cache`, în ce format, cât RAM ia la pornire o linie de 24 de straturi, cât durează încărcarea). Dacă aflarea asta ar cere vreo schimbare în `kronos/`, te oprești aici și scrii în raport de ce (pasul 5 rămâne `oprit` până decide Adrian).
  2. **Unealta nouă** `unelte/date_bucati.py` + `teste/test_date_bucati.py`: (a) `scrie` — din simbolurile deja făcute în `lucru/cache` (doar citit) scrie bucăți de mărime fixă (ex. 50 M simboluri) în `lucru/bucati/<nume>/`, cu un `index.json` (ordinea, mărimea, SHA-256 pe fiecare bucată, tokenizerul și sursa); (b) `citeste` — un cititor care dă simbolurile bucată cu bucată, fără să încarce tot în memorie; (c) `verifica` — compară SHA-urile din index.
  3. **Proba de identitate:** pentru o linie existentă (aceeași ca în `conv_w2_mare_24r`), șirul de simboluri dat de cititor = exact cel din cache-ul de acum (aceleași octeți, comparat prin SHA pe tot șirul), iar RAM-ul de vârf al cititorului e măsurat și scris față de încărcarea de acum.
  4. Nicio configurare nu folosește bucățile încă (nici cele existente, nici una nouă). Legarea în antrenare = sarcină separată, după raport. Fără nicio schimbare în `kronos/`, `module/`, paznic, examen; `lucru/cache` doar citit (lista înainte = după). Spațiul: dacă bucățile ar lăsa C: sub 20 GB liberi, scrii doar pe o parte din date și notezi.
  5. Raport `docs/rapoarte/<data>_<ora>_S96_date_bucati.md` (ce ai aflat la pasul 1, mărimi, timpi, RAM, proba de identitate DA/NU); `python -m pytest` verde; coada → `gata`; commit + push.
- **adăugat de supraveghetor 9 nov 14:15 — adus azi (C-93: calculatorul e liber, Adrian a plecat):** poți face S96 **azi, 9 nov, după-amiază**, pornire până la **16:00**, gata până la **19:15** (înainte de S95, care pornește abia la 21:00 — nu se suprapun). Doar procesor + disc, nimic pe placă. Dacă nu poate porni până la 16:00, rămâne pentru marți 10 nov de la 08:00 (după S95). Dacă la 19:15 nu e gata: oprești curat, scrii unde ai ajuns în raport, rămâne `aprobat` pentru marți (fără `oprit`). Calculatorul se poate reporni dacă Adrian vine la 20:00 — de aceea limita 19:15.
- aprobat de: Adrian (COMENZI.md C-85 pasul 5, 6 nov 2026 17:56); pașii scriși de supraveghetor 9 nov 2026 02:15 (granițele 3 și 5: pregătirea datelor deja aprobate, unealtă nouă în `unelte/` + teste, fără `kronos/`)
- raport: docs/rapoarte/2026-11-09_1440_S96_date_bucati.md

### S97 — C-92: pregătești singur stick-urile de test cu release-ul OS care repară I8 (C-91) (doar rețea + stick-uri, fără placă)
- stare: oprit (executant, 9 nov 2026 08:35)
- notă supraveghetor 9 nov 11:15: release-ul de folosit e **`os-276`** (verificat, CI verde); se face doar într-o sesiune cu Adrian de față.
- motiv: cere aprobarea lui Adrian: permisiunea pentru `gh api` — în rularea programată (fără om) comanda de la pasul 0 cere aprobare și e refuzată, deci nu pot vedea dacă există release-ul nou; nu am ocolit (nimic descărcat, nimic scris pe D:/E:)
- (istoric) stare: **aprobat** (Adrian, COMENZI.md C-92, 9 nov 2026 08:14; preluat de supraveghetor 08:15)
- tip: procesor + rețea + stick-uri USB (NU placa video)
- fereastră: **azi, 9 nov, la fiecare trecere a ta, cât timp workstation-ul e în Windows**, până când stick-urile sunt gata (sau până scrie Adrian altceva). Nu așteaptă fereastra plăcii.
- context (de la Adrian): stick-urile rămân băgate în workstation: **TESTGPU = E:** (stick de test, FAT32, cu `firmware\`) și **CYBER-UNIV = D:** (stick normal, cu `firmware\` și `kronos\` + #513).
- ce faci:
  0. La fiecare trecere: `gh api repos/Adriancu91/cyber-universe/releases` (doar citire, REST). Cauți un release **mai nou decât `os-275`** care în hub, `stare/cyber-universe.md` (sau `COMENZI.md` C-91, „stare (cyber-universe)”) e marcat ca reparația C-91, cu CI verde. Dacă nu poți citi hub-ul de pe workstation: îl accepți doar dacă notele release-ului pomenesc C-91 / P6-68 / secvențiatorul; altfel aștepți. Dacă nu există încă: nimic, treci mai departe (fără raport).
  1. Verifici literele: `E:` are eticheta **TESTGPU** și `D:` are eticheta **CYBER-UNIV**. Dacă nu se potrivesc (sau un stick lipsește): te oprești, `oprit`, raport.
  2. Descarci din release DOAR: `cyber-universe-gpu-scrie-usb.img`, `cyber-universe-usb.img`, `SHA256SUMS`, `VERSIUNE`, într-un dosar nou, de exemplu `C:\Kronos\descarcari\os-NNN\` (nu în repo). **Verifici SHA-256** pentru ambele imagini față de `SHA256SUMS`; dacă nu se potrivește: oprești, `oprit`, raport.
  3. Extragi fișierele din partiția FAT a fiecărei imagini (doar citire, de ex. cu 7-Zip dacă e deja instalat sau cu Python, fără să instalezi programe noi) și **copiezi peste**: din imaginea `gpu-scrie` → **E:\** (BOOT, EFI, KRONOS, CYBER.RW); din imaginea normală → **D:\** (BOOT, EFI, CYBER.RW) + `VERSIUNE`. **Nu ștergi și nu atingi** `firmware\`, `kronos\` de pe D:, `raport\`, `de pastrat\` sau alte fișiere. După copiere verifici SHA-256 pe fiecare fișier copiat (sursă = stick) și că fișierele din `firmware\` și `kronos\` au aceleași SHA ca înainte.
  4. Scrii SUS în `plan/pentru_adrian.md`: „**Stick-urile sunt gata cu os-NNN** — Adrian: oprire completă, cablu scos 30 s, pornești de pe TESTGPU, `gpu lant` + DA”. Dacă poți scrie în hub: același rând în `stare/kronos.md` (altfel îl pune supraveghetorul la trecerea următoare).
  5. Raport scurt `docs/rapoarte/<data>_<ora>_S97_stickuri.md` (release, SHA-urile, ce fișiere au fost copiate unde, verificările); coada → `gata`; commit + push. Testele nu se schimbă (nu atingi cod), dar rulezi `python -m pytest` o dată, ca la orice „gata”.
- **NU:** nicio repornire, nimic pe placa video, nicio ștergere, nimic scris în afara E:\, D:\ și dosarului de descărcare. Nu atingi `kronos/`, `module/`, `config/`, paznicul, jurnalul. Firmware-ul NVIDIA nu se urcă nicăieri.
- excepție scrisă pentru regula ta (descărcare + copiere pe stick-uri): **aprobată de Adrian** prin C-92, 9 nov 2026 08:14 — doar pentru acest release și aceste două stick-uri.
- aprobat de: Adrian (COMENZI.md C-92, 9 nov 2026 08:14)
- raport: docs/rapoarte/2026-11-09_0835_S97_oprit_gh_blocat.md

### S98 — C-85 pasul 5 (partea b): legarea datelor pe bucăți în antrenare — modul NOU de date, varianta (a) „mmap + aceleași ferestre la întâmplare”, NEACTIVAT în configurările în uz (doar procesor + disc, fără placă)
- stare: **aprobat** (supraveghetor, 9 nov 2026 17:15)
- tip: procesor + disc (NU placa video)
- fereastră: **după ce Adrian a terminat testul OS de mâine** (C-93): pornești doar când există o notă de la Adrian sau de la centrul de comandă (hub `COMENZI.md` sau `plan/coada.md`) că workstation-ul e liber, și **niciodată** cât rulează o sarcină pe placă (S95 sau următoarea) — nu concurează cu ea pentru RAM/disc. Dacă nota nu vine marți, rămâne `aprobat` (fără `oprit`). Durată ~2–3 h. Calculatorul se poate reporni: dacă ești întrerupt, reiei de la pasul neterminat, fără `oprit`.
- de ce: S96 („De știut” 1–3): proba de identitate DA, dar câștigul mare e la pornire, unde linia citește tot textul brut (4,9 GB) doar pentru amprentă → vârf **41,7 GB RAM**; la super-școala de română (date de câteva ori mai multe) asta trece de RAM-ul workstation-ului. Varianta (a) păstrează aceleași loturi exact (aceeași sămânță) → nu schimbă rețeta, deci nu cere o linie nouă.
- ce faci:
  0. Verificări: `lucru/bucati/w2_amestec_be12/` există și `python unelte/date_bucati.py verifica --dosar lucru/bucati/w2_amestec_be12` dă 27/27 bune; `python -m pytest` verde; placa nefolosită de tine.
  1. **Modul NOU** (de ex. `module/date_bucati.py`, clasă cu `MANIFEST`: nume, port `date`, versiune, versiune_contract) care: (i) ia amprenta din `index.json` (SHA-256 al șirului + tokenizerul), FĂRĂ `read_text` pe textul brut; (ii) dă ferestrele de antrenare prin mmap pe bucăți, cu tragerea la sorți a locului ca acum (`randint(len - ctx - 1)` pe tot șirul), lipind o bucată de următoarea când fereastra cade la graniță; (iii) refuză să pornească dacă `verifica` nu trece. Îl adaugi în lista `MODULE` din `teste_contracte/` și trebuie să treacă. **Dacă pentru asta trebuie schimbat un modul existent (`date_amestec.py`, `model_continuu.py`) sau `kronos/`: NU îl schimbi** — te oprești după pasul 0–1, scrii exact ce și de ce trebuie schimbat, sarcina `oprit` cu „necesită Adrian”.
  2. Configurare NOUĂ de probă `config/conv_w2_mare_24_bucati.toml` (copia lui `conv_w2_mare_24r` cu DOAR portul `date` mutat pe modulul nou și `nume`/`cale_stare` noi, în `lucru/proba_bucati/`) — **nu se antrenează cu ea** și nu înlocuiește nicio configurare în uz. Dacă paznicul cere amprenta examenului pentru o configurare nouă, folosești ce face deja singur (ca la S93), fără schimbări în paznic.
  3. **Proba de identitate a loturilor (pe procesor, `CUDA_VISIBLE_DEVICES=-1`):** cu aceeași sămânță, primele **1.000 de loturi** (4 × 512) din calea veche (cache întreg) și din modulul nou sunt **identice** (SHA-256 pe toate loturile, plus 3 loturi la graniță de bucată verificate separat). Verdict: **DA** = identice toate; **NU** = oricare diferă (atunci raportezi primul lot diferit și nu legi nimic).
  4. **Măsurarea pornirii** (proces separat, ca la S96): timpul și RAM-ul de vârf al pornirii părții de date cu modulul nou vs cele 41.685 MB / 40,6 s din S96. Așteptare (nu prag): sub 4.000 MB.
  5. Teste noi (identitate pe un șir mic cu ferestre la graniță, refuzul la bucată stricată, amprenta fără text brut) + `python -m pytest` verde.
  6. Raport `docs/rapoarte/<data>_<ora>_S98_bucati_legare.md` (ce fișiere noi, proba DA/NU cu SHA-urile, RAM/timp înainte vs după, ce ar mai trebui ca linia de 24 să folosească modulul la o antrenare reală — asta va fi o decizie separată); un rând sus în `plan/pentru_adrian.md`; coada → `gata`; commit + push.
- **NU:** nimic pe placa video, nicio antrenare, nu atingi `kronos/`, modulele existente, `module/examen_bpb.py`, `module/examen_romana.py`, paznicul, jurnalul (doar prin platformă), configurările existente, `lucru/cache` (doar citit), `lucru/bucati/w2_amestec_be12/` (doar citit), modelele. Nimic descărcat, instalat sau șters. Nimic din `lucru/` în Git.
- aprobat de: Adrian (COMENZI.md C-85 pasul 5, 6 nov 2026 17:56 — „date pre-tokenizate, citite pe rând”); pașii scriși de supraveghetor 9 nov 2026 17:15 (granițele 3 și 5: modul nou + unealtă + teste, fără `kronos/` și fără schimbarea modulelor existente; neactivat)
- raport: docs/rapoarte/<data>_<ora>_S98_bucati_legare.md
