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
- stare: in_lucru
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
- raport: docs/rapoarte/2026-10-2x_<ora>_S24_E3_index.md
