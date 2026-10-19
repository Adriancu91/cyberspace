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
- stare: in_lucru
- tip: placă
- fereastră: noapte
- durată maximă: 3 ore + examene
- ce faci: pornită de sarcina Windows „Kronos noapte conversatie” la 19:00, 19 octombrie
- pre-înregistrare: docs/preinregistrari/2026-10-19_noaptea10_raspuns_din_text.md
- aprobat de: Adrian, 19 octombrie
- raport: verdictul vine la 07:40, 20 octombrie (raportul automat)

### S2 — Motorul de română ca filtru pentru datele de conversație
- stare: propus — necesită Adrian
- tip: procesor
- fereastră: oricând
- durată maximă: 2 ore
- ce faci: merge al ramurii `limba-romana` în `main`, construirea bazei (≈ 370 MB descărcați, 1,1 GB bază, licențele
  sunt deja în `module/limba_romana/LICENTE.md`), apoi `verifica_text` pe toate perechile de conversație; raport cu
  câte greșeli de acord găsește și 30 de exemple
- aprobat de: —
- raport: —

### S3 — Școala de cod: o sarcină nouă pentru nivelul 0w
- stare: propus
- tip: placă
- fereastră: zi
- durată maximă: 4 ore
- ce faci: supraveghetorul scrie proiectul după verdictul nopții 10
- aprobat de: —
- raport: —
