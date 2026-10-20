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
- stare: aprobat
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
- raport: docs/rapoarte/<data>_<ora>_motor_romana_masurare.md
### S3 — Școala de cod: o sarcină nouă pentru nivelul 0w
- stare: propus
- tip: placă
- fereastră: zi
- durată maximă: 4 ore
- ce faci: supraveghetorul scrie proiectul după verdictul nopții 10
- aprobat de: —
- raport: —

### S4 — Examen de generalizare pentru #401: întrebări puse altfel
- stare: aprobat
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
- raport: docs/rapoarte/<data>_<ora>_S4_generalizare_401.md, cu toate cele 60 de răspunsuri
