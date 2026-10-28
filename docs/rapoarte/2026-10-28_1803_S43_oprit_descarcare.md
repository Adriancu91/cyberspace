# S43 — oprită înainte de pornire: descărcarea nu are unealta numită (executant, 28 oct 2026, 18:03)

## Pe scurt

- **S43 (Kronos-Cod, pilotul de descărcare) n-a pornit.** Am pus-o `oprit`, cu motivul
  „cere aprobarea lui Adrian: descărcare — „ce faci” nu numește unealta de descărcare”.
- **Nu s-a descărcat nimic.** Nu s-a scris cod nou. Placa n-a fost atinsă.
- Testele: **999 trec, 1 sărit** (4 min 12 s).
- S42 rămâne `aprobat` pentru **19:00** (fereastra de noapte); n-am atins-o.

## De ce n-am pornit-o

Regula executantului pentru descărcări (Adrian, 19 octombrie, varianta b): o descărcare e voie doar dacă sarcina are
„aprobat de: Adrian” **și** pomenește anume descărcarea în „ce faci”, **„doar ce scrie acolo, prin unealta scrisă acolo”**
(exemplul din regulă: `python -m module.limba_romana.importatoare.descarca_surse`).

La S43:
- „aprobat de: Adrian, 28 oct 18:00” — **da**, și „da” pentru pilot e clar.
- „ce faci” pomenește pilotul (500 PyPI + 500 crates + numpy, tokio, libuv) — **da**.
- **unealta**: „ce faci” trimite la §5 din raportul S41, unde nu e numită nicio comandă. În proiect nu există încă o
  unealtă de descărcare pentru Kronos-Cod (singura e `unelte/descarca_date.py`, pentru altceva). Ar trebui să o scriu
  acum și să o pornesc pe internet în aceeași rulare, fără om de față — exact ce interzice partea „prin unealta scrisă acolo”.

Un motiv în plus de prudență: dacă porneam acum pilotul (~1 oră + scrierea uneltei), la 19:00 S43 ar fi fost încă
`in_lucru`, iar regula „o singură sarcină odată” ar fi blocat pornirea S42, pe care supraveghetorul a pus-o înaintea oricărei
alte sarcini de placă.

## Starea la 18:03

- Fereastra: zi, 31 de minute rămase; placa liberă (29 °C, 938 MB); niciun proces greu.
- Spațiu pe C: **73 GB liberi** (pragul de oprire din S43: 40 GB).

## Ce propun (alege una)

1. **(recomandat)** O rulare în două pași: întâi scriu unealta pilotului (de exemplu
   `python -m module.kronos_cod.descarca_pilot`, cu toate filtrele din `docs/kronos_cod/SURSE.md`, data-limită
   29 iunie 2021, oprire sub 40 GB liberi) și testele ei, **fără rețea**; apoi supraveghetorul (sau Adrian) trece comanda
   exactă în „ce faci” la S43 și o pune iar `aprobat` — rularea următoare o pornește.
2. Adrian spune explicit că, pentru S43, executantul poate scrie unealta și o poate porni în aceeași rulare.

## Testele

`CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -m pytest -q`: **999 passed, 1 skipped** (252 s). Nimic schimbat în cod.

## Ce aștept de la Adrian

- Varianta 1 sau 2 de mai sus pentru S43.
