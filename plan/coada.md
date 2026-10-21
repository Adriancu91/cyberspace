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
---

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
- stare: aprobat
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
- raport: docs/rapoarte/2026-10-22_<ora>_S16_verificator_fara_llm.md

### S17 — E1: „întrebări născute de Kronos” (auto-joc cu verificator, fără niciun model străin)
- stare: propus — trece pe `aprobat` (de supraveghetor, cu „da”-ul lui Adrian din 22 oct 01:45) DOAR dacă S16 iese cu acord ≥ 90 %
- tip: placă (~5 ore) + procesor (~1 oră pentru filtre)
- fereastră: noapte (19:00–07:00), prima după aprobare — țintă: noaptea 22→23 octombrie
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
- pre-înregistrare: docs/preinregistrari/2026-10-2x_E1_intrebari_nascute.md (o scrii tu, înainte de pornire)
- aprobat de: direcția lui Adrian, 22 oct 01:45 (punctul 3); aprobarea finală o pune supraveghetorul după S16
- raport: docs/rapoarte/2026-10-2x_<ora>_S17_E1_intrebari_nascute.md
