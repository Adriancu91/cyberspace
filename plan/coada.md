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
- stare: oprit
- motiv: rularea reparată NU a pornit (20:33): `cascada.py porneste S7` refuză, pentru că `lucru/cascada/S7.json` de la prima pornire (19:29, cod 0) există încă; redenumirea lui a cerut aprobare în rularea automată. Configurarea (`nume = "w2_conv_text_v2"`) și nota din pre-înregistrare sunt gata. Trebuie mutat fișierul vechi (sau reparată unealta), apoi S7 din nou `aprobat`; vezi docs/rapoarte/2026-10-20_2033_S7_reparat_nepornit.md
- reparația aprobată: varianta 2 (Adrian, 20 oct 20:27, prin centrul de comandă). Executant: la prima rulare după ce citești
  asta, dacă placa e liberă, fă pașii 1–4 de mai jos pe linia nouă: în `config/conv_w2_text_v2.toml` pune `nume = "w2_conv_text_v2"`,
  adaugă în pre-înregistrare nota „rulare reparată pe linia w2_conv_text_v2, din #401, aceleași praguri” ÎNAINTE de pornire, apoi comanda
  de la pasul 1. Pasul 0 e deja făcut (17:29), nu-l repeta. Raportul de dimineață ca la pasul 4.
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
- raport: docs/rapoarte/2026-10-20_2002_S7_oprit_nu_a_antrenat.md (oprit: nicio oră antrenată; raportul de dimineață rămâne pentru rularea reparată); docs/rapoarte/2026-10-20_2033_S7_reparat_nepornit.md (rularea reparată pregătită, nepornită: fișierul vechi lucru/cascada/S7.json)


### S8 — Formatul comun de modul din Cyber Hub: `module.toml` pentru modulele Kronos
- stare: aprobat
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
- raport: —
