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
- stare: **propus — necesită Adrian** (răspunsul în hub, `COMENZI.md`: „da S66 A”, „da S66 B” sau „da S66 C”)
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
- stare: in_lucru (executant, 3 nov 05:37: comanda `curata` + 3 teste în dac45c7, 1186 teste trec, 1 sărit; pornită prin cascadă 05:37:45, proces 13496, `--pana-la 08:40` (oprire curată, reluare cu aceeași comandă după 11:30); 319.430 funcții (a+b+c) fără duplicate = S65; cutia ~85 rulări/s cu 16 fire → estimat ~1 oră)
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
- raport: docs/rapoarte/<data>_<ora>_S67_functii_autonome.md
