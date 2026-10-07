# CONTINUUM — ritmul de viață al lui Kronos (platforma Cyberspace)

> Specificație adaptată la starea proiectului din 6 octombrie 2026 (după M1–M3, bucla de auto-îmbunătățire, profesor, regula 4).
> Se dă lui Claude Code în repo-ul `cyberspace`, câte o versiune pe rând.
> Principiu de lucru: totul reversibil, totul măsurat, nimic presupus.

---

## 0. Ce s-a schimbat față de planul inițial (citește întâi)

Planul inițial a fost scris înainte ca Kronos să existe în forma de acum. Între timp, platforma are deja:

| Din planul inițial | Există deja în Kronos | Unde |
|---|---|---|
| kill switch extern | fișierul `lucru/STOP`, `python -m kronos opreste / porneste` | `kronos/paznic.py` |
| jurnal de decizii JSONL | `lucru/jurnal/experimente.jsonl`, câte o fișă pe experiment | `kronos/jurnal.py` |
| guvernator de resurse (temperatură, VRAM) | paznicul: limită VRAM, temperatură, pauze de răcire, timp maxim | `kronos/paznic.py` |
| snapshot + rollback | fiecare experiment salvează modelul; păstrat / respins; stări per arhitectură | orchestrator + `lucru/stocare`, `lucru/bucla/stari` |
| evaluator separat, set ascuns | examenul oficial, protejat prin amprentă; paznicul blochează dacă e atins | `module/examen_bpb.py` + paznic |
| măsurare cu prag de zgomot | `prag_zgomot` în configurare; zgomotul dintre semințe măsurat (≈0,02 la 8 ore) | orchestrator |
| „nou ≠ mai bun” pe mai multe criterii | regula 4: `[criterii]` în config, `dupa_examen` înainte de decizie | orchestrator (aprobat 6 oct.) |
| metrici pe capacități | trei examene: val_bpb (povești), fapte_corecte (fapte), nota_profesor (sens) | `module/examene_elev.py` |
| sursă de experiență nouă | profesorul (Qwen3-4B): generează povești cu fapte, notează | `module/profesor_qwen.py` |
| cercetător care propune | listă + strângere în jurul celor mai bune 3 | `module/cercetator_local.py` |

**Concluzia:** CONTINUUM nu e o platformă nouă peste Kronos. E **modulul care decide ce face Kronos când nimeni nu-i spune** — lucrul pe care Adrian și Claude îl fac azi de mână, în fiecare dimineață și seară („ce rulăm diseară? continuare, căutare sau fapte?”). Tot ce înseamnă antrenare, examen, decizie păstrat/respins, jurnal, paznic rămâne în Kronos. CONTINUUM observă, alege nevoia și cere lui Kronos un experiment.

Schimbări concrete față de planul inițial:
1. **Fără contract nou de module.** Planul propunea un `ModuleManifest` paralel (name / capabilities / health / signals / run / evaluate). Kronos are deja `MANIFEST` (nume, port, versiune, versiune_contract) și 10 porturi în `kronos/contracte.py`. CONTINUUM folosește contractele existente; ce nu există (sănătate, semnale) le cere opțional, prin `getattr`, fără să atingă `kronos/`.
2. **CONTINUUM e un modul, nu un pachet lângă nucleu.** Locul lui e `module/continuum/`, încărcat din configurare ca orice modul. Regula „`kronos/` nu importă din `module/`” rămâne; CONTINUUM importă din `kronos/` (orchestrator, jurnal, config), nu invers.
3. **Nu reimplementează măsurarea.** Un „ciclu” CONTINUUM nu antrenează și nu dă examen singur: pornește un experiment Kronos (prin orchestrator sau printr-o unealtă din `unelte/`) și citește fișa din jurnal.
4. **Convențiile proiectului:** nume în română (observa, evalueaza, nevoi, alege, actioneaza, masoara, invata, stare), configurare TOML în `config/continuum.toml`, teste în `teste/`, stare în `lucru/continuum/`.
5. **Setul „sacru” devine o adăugare reală.** Azi validarea R2 e folosită și la fiecare experiment, și la raportare. După sute de experimente, selecția se poate „lipi” de ea. CONTINUUM v2 introduce o a doua bucată de validare, nevăzută de nicio decizie automată, folosită doar la **promovarea** unui model ca „versiune oficială”, cu aprobare umană.
6. **„Trei rulări per măsurătoare” se aplică doar la măsurători ieftine** (examenele, câteva minute). Pentru antrenările de ore se folosește pragul de zgomot deja măsurat între semințe, nu trei repetări.
7. **Utilizarea concretă din v0 nu mai e „cu / fără memorie ierarhică”** (M1 e închisă). E: **să decidă singur ce rulează ziua și noaptea**, și să aleagă capacitatea cea mai slabă de dezvoltat (azi: faptele, 27%).

---

## 1. Scopul

CONTINUUM ține Kronos într-o stare continuă de **observare, întreținere, învățare și evoluție**, și când nu există nicio cerere din afară.

- Nu e chatbot, nu e un simplu programator de sarcini, nu e agent autonom cu acces la lume.
- E **ritmul de viață**: transformă starea organismului în nevoi, nevoile în experimente Kronos, iar experimentele în experiență măsurată.

---

## 2. Reguli de aur (obligatorii)

1. **Activitate ≠ progres.** Nicio acțiune nu e succes fără măsurătoare înainte / după, pe examenele existente.
2. **Opțional, nu indispensabil.** Kronos merge fără CONTINUUM. CONTINUUM merge cu orice subset de module, inclusiv zero.
3. **Nu presupune niciun modul.** Descoperă ce e încărcat la pornire și la fiecare K cicluri.
4. **STOP-ul uman e absolut și e același.** `lucru/STOP` oprește și Kronos, și CONTINUUM. Nu există un al doilea buton.
5. **Nu modifică cod, greutăți sau structură.** Orice schimbare trece prin ciclul Kronos: propus → verificat → aplicat → testat rapid → antrenat → examinat → decis → înregistrat.
6. **Nu se notează singur.** Decizia păstrat / respins e a orchestratorului, pe examenul oficial + regula 4. Promovarea ca „versiune oficială” e a omului, pe setul sacru (v2).
7. **Totul reversibil.** Kronos salvează fiecare experiment; CONTINUUM ține minte ce stare era „cea mai bună” înainte de fiecare acțiune.
8. **Totul jurnalizat.** Fiecare ciclu lasă un rând: ce a observat, ce nevoie a ales, de ce, ce a cerut, ce a ieșit.
9. **Nu atinge examenul sacru și nu atinge `kronos/`.** Niciodată, nici prin unelte.

---

## 3. Niveluri de activitate (decise de guvernator, nu de buclă)

| Nivel | Când | Ce face | Ciclu |
|---|---|---|---|
| REPAUS | omul folosește laptopul (tastatură / mouse în ultimele N minute), placa fierbinte, sau în afara ferestrei permise | doar observă, fără placă video | 5–15 min |
| ÎNTREȚINERE | totul stabil, placa liberă, ziua | examenele pe ultimul model, verificări, hrană nouă de la profesor | 1–5 min între verificări |
| ÎNVĂȚARE | există hrană nouă sau un model neterminat | antrenare lungă prin Kronos (continuare), noaptea | continuu, cu buget |
| EXPLORARE | stabil + resurse libere + nicio nevoie urgentă | căutare de rețete (bucla cercetătorului), ipoteze | continuu, cu buget |
| INTENSĂ | eroare critică (model stricat, test picat) sau cerere externă | reparare / servire | maxim permis |

Guvernatorul **nu înlocuiește paznicul**: paznicul oprește un experiment în curs (temperatură, VRAM, timp); guvernatorul decide dacă se pornește unul.

---

## 4. Bucla centrală

```
OBSERVĂ → EVALUEAZĂ → NEVOI → ALEGE → ACȚIONEAZĂ → MĂSOARĂ → ÎNVAȚĂ → STARE → (OBSERVĂ)
```

Fiecare etapă e o funcție separată, testabilă singură. Dacă o etapă cade, ciclul se încheie curat, eroarea intră în jurnal și urmează ciclul următor. Bucla nu cade niciodată din cauza unei etape.

### 4.1 OBSERVĂ
Colectează semnale, fără excepții (port gol sau modul care nu răspunde → semnal `indisponibil`):
- din jurnalul Kronos: ultimele fișe (val_bpb, fapte_corecte, nota_profesor, pași, decizie, motiv);
- de la paznic / sistem: temperatură, VRAM liber, dacă rulează un experiment, `lucru/STOP`;
- de la om: ultima activitate pe laptop (tastatură / mouse), fereastra orară din config, bugetul de ore GPU rămas azi;
- de la module: care sunt încărcate (din config), și, dacă modulul oferă `sanatate()` sau `semnale()`, ce spun;
- din hrană: ce texte noi există și nu au fost încă folosite (de ex. `date/fapte/povesti.txt`).

### 4.2 EVALUEAZĂ
Construiește `StareaOrganismului`: capacitățile cunoscute (povești, fapte, sens), linia de bază a fiecăreia (cel mai bun experiment păstrat), scorul curent, degradare = sub linia de bază minus pragul de zgomot; ce experiment e în curs; ce hrană e nefolosită; ce nivel permite guvernatorul.

### 4.3 NEVOI
Transformă starea în nevoi, fiecare cu tip, capacitate, urgență, motiv. Exemple reale pentru azi:
- „fapte = 27%, cea mai slabă capacitate, și există 7.520 de povești cu fapte nefolosite” → `NEVOIE(dezvolta, fapte)`;
- „val_bpb încă scade de la o oră la alta” → `NEVOIE(continua, povesti)`;
- „nicio rețetă nouă încercată de 3 zile” → `NEVOIE(exploreaza, reteta)`;
- „examenele n-au mai fost date pe ultimul model” → `NEVOIE(masoara, toate)`;
- „nota_profesor a scăzut sub linia de bază” → `NEVOIE(repara, sens)`.

### 4.4 ALEGE
Ordinea de prioritate: 1 stabilitate / reparare · 2 cerere externă · 3 măsurare lipsă · 4 învățare · 5 dezvoltarea celei mai slabe capacități · 6 explorare · 7 opțional. Plus regulile anti-buclă (secțiunea 8). **O singură nevoie pe ciclu.**

### 4.5 ACȚIONEAZĂ
CONTINUUM nu face el munca. Pentru nevoia aleasă pornește **un experiment Kronos** cu o configurare existentă (sau o unealtă din `unelte/` care rulează prin Kronos), cu timeout și buget. Dacă nu există modul sau unealtă pentru nevoie → `capacitate_indisponibila`, trece la următoarea nevoie. Niciodată nu antrenează direct.

### 4.6 MĂSOARĂ
Citește fișa experimentului din jurnal: scor înainte / după pe capacitatea vizată și pe celelalte (regula 4). Verdict: `SUCCES` / `EȘEC` / `NECONCLUDENT` după pragul de zgomot al capacității.

### 4.7 ÎNVAȚĂ
SUCCES → strategia (de ex. „continuare 8 ore pe text întreg”) câștigă încredere; EȘEC → pierde, contor +1; NECONCLUDENT → se repetă cu altă sămânță, maxim N ori.

### 4.8 STARE
Scrie în `lucru/continuum/stare.json` și un rând în `lucru/continuum/cicluri.jsonl`. Liniile de bază se actualizează doar din experimente păstrate de Kronos.

---

## 5. Cum vede CONTINUUM modulele

Prin ce există: `kronos/registru.py` + configurarea TOML (ce clasă pe ce port), `MANIFEST`-ul fiecărui modul, contractele din `kronos/contracte.py`. Nu se adaugă un contract nou.

Opțional, un modul poate oferi în plus (CONTINUUM le caută cu `getattr`, lipsa lor nu e eroare):
- `sanatate() -> dict` — `{"stare": "ok" | "degradat" | "cazut", "detalii": ...}`;
- `semnale() -> list[dict]` — ce s-a întâmplat de la ultimul apel.

Capacitățile de azi și metricile lor:
- **povești** → `val_bpb` (mai mic = mai bine), examenul oficial;
- **fapte** → `fapte_corecte` din 150 (mai mare = mai bine), `unelte/examen_fapte.py`;
- **sens** → `nota_profesor` din 10 (mai mare = mai bine), `unelte/examen_profesor.py`.

O capacitate nouă intră cu examenul ei și cu linia ei de bază măsurată înainte de orice decizie.

---

## 6. Reparare vs evoluție

| | Reparare | Evoluție |
|---|---|---|
| Declanșator | scor sub linia de bază − prag | stabil + ipoteză de mai bine |
| Scop | înapoi la linia de bază | peste linia de bază |
| Prima opțiune | întoarcere la ultimul model păstrat | experiment Kronos nou |
| Acceptare | scor ≥ linia de bază pe toate criteriile | păstrat de Kronos (regula 4); promovare = set sacru + om |
| Prioritate | 1 | 5–6 |

Fluxul comun e **ciclul Kronos**, nu unul nou.

---

## 7. Măsurare corectă

- **Prag de zgomot per capacitate**, în config, pornind de la ce s-a măsurat: povești ≈ 0,02 la 8 ore / ≈ 0,03 la 5 minute; fapte ≈ 3 din 150; sens ≈ 0,3. Se reajustează când avem măsurători pe mai multe semințe.
- **Măsurătorile ieftine** (examene) se repetă de 3 ori doar dacă rezultatul e la limită.
- **Pe lângă calitate:** timp și consum (pași/s, VRAM). Un câștig de 1% cu viteză de 3 ori mai mică nu se promovează automat (lecția M3).
- **Setul sacru (v2):** o bucată de validare separată, pe care n-o citește nicio decizie automată. Doar promovarea „versiune oficială”, cu aprobare umană.

---

## 8. Anti-buclă

- **Răcire:** o nevoie tratată nu se reia timp de N cicluri (excepție: stabilitate).
- **Limită de reîncercări:** după `max_esecuri` (5) pe aceeași strategie → `blocată`, se cere alternativă sau se raportează omului.
- **Oscilație:** aceeași variantă păstrată și apoi retrasă de 2 ori → înghețată până la revizuire umană.
- **Varietate:** la explorare, capacitatea neatinsă de cel mai mult timp.

---

## 9. Guvernatorul (laptop ASUS TUF, RTX 3060 6 GB, 64 GB RAM)

Separat de buclă, simplu, cu totul în `config/continuum.toml`:
- temperatura plăcii peste prag → coboară un nivel; VRAM liber sub prag → nu pornește antrenare (limitele rămân cele ale paznicului: 5,5 GB, 85 °C);
- omul activ pe laptop (ultima tastă / mișcare de mouse sub N minute) → REPAUS;
- fereastră orară pentru ÎNVĂȚARE (de ex. 22:00–07:00) și pentru ÎNTREȚINERE cu profesor (ziua);
- buget zilnic de ore GPU;
- **o singură sarcină grea pe placă odată** (profesorul și antrenarea nu încap împreună).

La mutarea pe server (RTX 3070, 128 GB RAM) se schimbă doar configurarea.

---

## 10. Memoria CONTINUUM

Mică, în `lucru/continuum/`, JSON (ca restul proiectului):
- `capacitati` — nume, metrică, direcție, linie de bază (+ experimentul care a dat-o), ultimul scor, ultima măsurare;
- `strategii` — nume, încredere, succese / eșecuri, stare (activă / blocată);
- `experimente` — ce a cerut CONTINUUM, numărul fișei Kronos, verdict;
- `probleme` — deschise / rezolvate;
- `de_reluat` — cu motiv și dată.

Nu stochează cunoștințe. Doar experiența de ritm.

---

## 11. Jurnalul ciclurilor

`lucru/continuum/cicluri.jsonl`, un rând pe ciclu:
```json
{"ciclu": 1042, "timp": "...", "nivel": "ÎNVĂȚARE", "observat": {...}, "nevoie": "dezvolta:fapte", "motiv": "fapte 27%, cea mai slabă; 7.520 povești nefolosite", "actiune": "kronos ruleaza config/laptop_fapte.toml", "fisa": 240, "inainte": {"fapte": 41, "val_bpb": 0.4436}, "dupa": {"fapte": 88, "val_bpb": 0.4451}, "verdict": "SUCCES"}
```
Rotire automată a fișierelor. Nu se editează de mână (ca jurnalul Kronos).

---

## 12. Siguranță

- `lucru/STOP` verificat la începutul fiecărui ciclu și între etape; CONTINUUM nu are buton propriu.
- Promovările „versiune oficială” cer aprobare umană în v0–v3.
- Fără acces la rețea din CONTINUUM; doar modulele care declară explicit (profesorul descarcă o singură dată).
- CONTINUUM nu scrie în `kronos/`, în examenul oficial, în jurnalul Kronos, în `date/` (hrana o produce profesorul, prin Kronos).

---

## 13. Plan pe versiuni

### v0 — Ritmul zilei (prima livrare; fără placă video la construire)
- `module/continuum/` cu cele 8 etape ca funcții separate + `guvernator.py` + `bucla.py` (STOP comun).
- OBSERVĂ din jurnalul Kronos, paznic, activitatea omului, fereastra orară, hrana nefolosită.
- Capacitățile povești / fapte / sens cu liniile de bază citite din jurnal.
- NEVOI și ALEGE doar pentru trei nevoi: `masoara`, `continua`, `dezvolta cea mai slabă capacitate`.
- ACȚIONEAZĂ = pornește un experiment Kronos cu o configurare existentă (`laptop_antrenare_lunga_*.toml`, `laptop_fapte.toml`) sau unealta de examene; timeout; o singură sarcină pe placă.
- Jurnal JSONL + stare JSON. Fără SQLite.
- Mod `--simuleaza`: tot ciclul fără să pornească nimic, doar scrie ce ar fi ales și de ce. **Așa se testează prima zi.**
- **Utilizare concretă:** rulat o zi în `--simuleaza`, deciziile lui trebuie să coincidă cu ce am fi ales de mână (ziua: examene + hrană de la profesor; noaptea: continuare sau fapte). Apoi o noapte reală.
- **Criteriu de acceptare:** 24 de ore fără să cadă, cu un modul scos și reintrodus în timpul rulării, cu omul care folosește laptopul la un moment dat (→ REPAUS), și jurnalul explică fiecare decizie în română.

### v1 — Măsurare atentă și anti-buclă (făcut pe 7 octombrie 2026, aprobat de Adrian)

Șapte puncte, construite în ordinea asta, fiecare cu testele lui (`teste/test_continuum_v1.py`, pe proiectul de probă
din `teste/continuum_proba.py`, fără placă video). Toate pragurile noi stau în `config/continuum.toml`, scrise și
explicate; fiecare are o valoare implicită (`IMPLICITE_V1` în `module/continuum/__init__.py`), deci o configurare din
v0 merge neschimbată.

1. **Zgomotul învățat** (`[zgomot]`, `module/continuum/zgomot.py`). Pentru fiecare capacitate, cât diferă de obicei
   două măsurători ale aceluiași lucru, învățat din jurnalul Kronos:
   - același model examinat de două ori (ex. examenul de la oră și unealta de examen);
   - două semințe ale aceleiași configurări (aceleași setări, același text, aceeași durată).

   Zgomotul = rădăcina mediei pătratelor diferențelor × `factor`. **Pragul folosit = max(podea, zgomot învățat)**, unde
   podeaua e `prag_zgomot` de la capacitate. Sub `perechi_minime` (3) perechi rămâne podeaua, iar jurnalul spune
   „neînvățat încă”. Pe jurnalul real (7 oct.), val_bpb are 22 de perechi de semințe, deci zgomotul 0,0144 (pragul
   urcă de la 0,005); fapte_noi (0 perechi) și nota (1 pereche) sunt încă neînvățate.
   *Alegere:* regula „continuă” (punctul 6) nu folosește zgomotul dintre semințe. Două ore ale aceleiași antrenări au
   aceeași sămânță, deci acolo contează doar `castig_minim` și zgomotul de remăsurare (același model de două ori).
2. **Trei zone față de linia de bază** (`[zone]`, în praguri):
   - **verde:** cel mult 1 prag sub;
   - **galbenă:** între 1 și 2 praguri sub (exact 2 e încă galbenă). Nevoia `remasoara` cere o remăsurare a ultimului model, o singură dată;
     nu e o acțiune;
   - **roșie:** peste 2 praguri sub. Nevoia `repara`, cu urgența 1. În v1, „repara” înseamnă doar un raport clar către
     om, în `lucru/continuum/rapoarte/`, cu modelul păstrat la care s-ar întoarce (cel al liniei de bază). Raportul se
     scrie o singură dată cât timp capacitatea stă în zona roșie; se închide când iese din ea. Poate fi scris și în
     REPAUS, pentru că nu folosește placa.
3. **Stabilitate pe două niveluri** (`[stabilitate]`, `module/continuum/stabilitate.py`).
   - Un scor mai bun decât linia de bază cu peste prag devine **candidat**, în coada din `stare.json` („candidati”,
     fiecare cu motivul, de când e și ce l-a decis).
   - Linia de bază, și încrederea strategiei care l-a adus, se mută **doar după o a doua măsurătoare independentă**
     care îl confirmă: a doua examinare a aceluiași model, sau o oră păstrată mai nouă de pe aceeași linie.
   - Pentru un candidat cu unealtă de examen, CONTINUUM cere singur remăsurarea (`remasoara`, „confirmare”).
   - Linia de bază nouă e cea mai slabă dintre măsurătorile care confirmă (prudent) și nu coboară niciodată.
   - După o antrenare pornită de CONTINUUM, toate orele păstrate noi intră în coadă, în ordine: ora 7 e confirmată de
     ora 8. Ultima oră așteaptă o remăsurare sau o oră de după.
   - La prima pornire, linia de bază e cea mai bună valoare păstrată din jurnal („inițializată din jurnal”).
4. **Verdictul cu eficiență** (`[eficienta]`). MĂSOARĂ ia și costul acțiunii: orele pe placă (cât au durat
   comenzile), pașii pe secundă și memoria video (din fișele noi). Un SUCCES cu câștigul pe oră de placă sub
   `fractie_scump` (50%) din media strategiei (din succesele ei de dinainte) devine **SUCCES SCUMP**: încrederea nu
   urcă.
5. **Vectorul capacităților** (`vector_capacitati` în `stare.json` și în jurnalul ciclurilor). Toate capacitățile din
   configurare, și cele nemăsurate (zona „nemăsurată”), fiecare cu: scor, linie de bază (și dacă e confirmată), zonă,
   pragul folosit (podeaua, zgomotul învățat, câte perechi), procentul din maxim. „Cea mai slabă” = cel mai mic procent
   din vector.
6. **Regula „continuă” cu temei** (`[nevoi.continua]`). Se continuă pe povești doar dacă:
   - ultima oră a coborât val_bpb cu **peste** `castig_minim` (0,005);
   - ȘI tendința pe ultimele `ore_tendinta` (3) ore e bună (panta dreptei prin ele). Cu mai puține ore, tendința nu
     se știe încă, deci nu se continuă.

   Două ore la rând cu câștig sub prag = **„saturat”**: „dezvolta” trece înaintea lui „continua”. (În v0, o linie
   neterminată se continua oricum.)
7. **Anti-buclă** (`[anti_bucla]` și `[guvernator]`):
   - **răcire:** o nevoie tratată pe bune nu se reia `racire_cicluri` (6) cicluri; „repara” n-are răcire;
   - **limita de reîncercări:** după `max_esecuri` (5) eșecuri la rând, strategia e **„blocată”** (ALEGE n-o mai
     alege), iar omul primește un raport;
   - **bugetul zilnic:** `buget_ore_placa_pe_zi` (20) ore pe placă, adunate din jurnalul Kronos (tot ce a rulat azi,
     oricine l-a pornit). Peste buget: REPAUS până mâine.

**Ordinea nevoilor în v1:** repara (mereu prima), masoara, remasoara (după masoara), apoi restul, din configurare.
ALEGE spune pentru fiecare nevoie sărită de ce, în ordinea asta: nivelul; ce lipsește; răcirea; strategia blocată.

**Opțiuni noi la `python -m module.continuum.bucla`:**
- `--stare DOSAR`: alt dosar pentru `stare.json` și `cicluri.jsonl`, ca o probă să nu amestece memoria;
- `--placa-libera`: doar cu `--simuleaza`, ca și cum placa ar fi liberă (ce ar alege după antrenarea de acum).

**Ce n-a intrat în v1:** întoarcerea automată la modelul păstrat (o decide omul, din raport), oscilația, explorarea,
cererea externă și setul sacru. Rămân pentru v2–v3.

### v2 — Setul sacru și promovarea
- A doua bucată de validare, invizibilă deciziilor automate.
- „Versiune oficială” a modelului: propusă de CONTINUUM, aprobată de om, cu rollback.
- Detecție de degradare și reparare.

### v3 — Evoluție
- CONTINUUM cere cercetătorului rețete noi (explorare) când totul e stabil.
- Profesorul propune și el (de ex. subiecte noi de fapte unde elevul e slab).
- Detecție de oscilație.

### v4 — Plasa de noduri (când o reluăm, pe server)
- Nodurile raportează semnale; CONTINUUM decide alocarea nodurilor libere după încărcare (plasa adaptivă).

---

## 14. Structura de fișiere

```
cyberspace/
  module/continuum/
    __init__.py
    bucla.py          # bucla + STOP comun + --simuleaza
    observa.py
    evalueaza.py
    nevoi.py
    alege.py
    actioneaza.py
    masoara.py
    invata.py
    stare.py
    guvernator.py
    masuratori.py     # v1: de unde vine valoarea unei capacități (oră, unealtă, criterii)
    zgomot.py         # v1: zgomotul învățat
    stabilitate.py    # v1: candidații și confirmarea lor
  config/continuum.toml   # praguri, ferestre orare, bugete, nevoi permise
  teste/test_continuum_*.py
  lucru/continuum/        # stare.json, cicluri.jsonl (nu se editează de mână)
  docs/CONTINUUM_plan.md  # acest fișier
```

---

## 15. Instrucțiuni pentru Claude Code

1. Implementează **doar v0**. Nu trece la v1 fără confirmare. (v1 a fost cerut de Adrian și făcut pe 7 octombrie
   2026; v2 tot doar după confirmare.)
2. Fiecare etapă = funcție separată, cu teste proprii; testează cu 0 module, 1 modul și un modul care cade în timpul rulării.
3. Toate pragurile, ferestrele și bugetele în `config/continuum.toml`, nu în cod.
4. Nu modifica `kronos/`, examenul oficial și nici jurnalul Kronos. Dacă ai nevoie de ceva din nucleu care lipsește, spune ce și de ce, nu improviza.
5. Construiește și testează **fără placă video** (module de probă); prima rulare reală doar în `--simuleaza`, când nu rulează altceva pe placă.
6. După fiecare pas: `python -m pytest` (toate testele), commit în română, push.
7. La final explică, în română, pe scurt: cum pornesc, cum opresc (același STOP), cum citesc jurnalul ciclurilor și cum văd ce ar fi ales în modul simulat.
