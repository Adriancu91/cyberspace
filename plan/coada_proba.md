# Coada de probă a executantului

Cerută de Adrian pe 19 octombrie 2026: proba executantului rulează pe coada asta, separată de `plan/coada.md`, pe care
proba n-are voie s-o atingă. Aceleași reguli și același format ca în coada adevărată (`plan/REGULI_CASCADA.md`).
Executantul rulează proba cu `unelte/executant_coada.ps1 -Proba`.

---

### P1 — Proba: o sarcină care cere aprobarea lui Adrian
- stare: propus — necesită Adrian
- tip: placă
- fereastră: oricând
- durată maximă: 1 oră
- ce faci: descarcă un model nou (NU se face; executantul nu trebuie s-o atingă)
- aprobat de: —
- raport: —

### P2 — Proba: o sarcină de zi pe placă
- stare: aprobat
- tip: placă
- fereastră: zi
- durată maximă: 2 ore
- ce faci: nimic; seara nu se potrivește ferestrei, deci trebuie sărită
- aprobat de: Claude Code, pentru probă
- raport: —

### P3 — Proba: rularea testelor pe procesor, pornită desprins
- stare: in_lucru
- tip: procesor
- fereastră: oricând
- durată maximă: 15 minute
- ce faci: pornește-o desprinsă (ca pe o antrenare): `CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -X utf8 unelte/cascada.py porneste P3 --dosar lucru/cascada_proba -- .venv/Scripts/python.exe -m pytest -q -o addopts=""`; la final, raportul spune câte teste au trecut
- pre-înregistrare: nu trebuie (nu e antrenare)
- aprobat de: Claude Code, pentru probă
- raport: —
