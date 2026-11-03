# S67 — Funcțiile S65 „cu adevărat ca la examen” (3 nov 2026, 07:04)

Scris de executant (cascada), fără om de față.

## Pe scurt

- **Verdict: ÎNTRE.** Funcțiile „autonome” (nu sunt goale, definiția rulează în cutie și nu folosesc nimic din afara lor) au
  **3,55 mil. simboluri de corp** — peste pragul „PUȚIN” (3 mil.), sub „DESTUL PENTRU A” (10 mil.).
- 83.349 funcții autonome din 319.430; doar 7.182 dintre ele au și exemplu/test (d).
- Scurgere: **0** în proba de 20 de probleme, **0** în seturile ascunse (S58: 200, ascuns2: 163); SHA-urile au rămas neschimbate.
- Testele: **1.186 trec, 1 sărit, 0 picate**.
- Aștept de la Adrian: alegerea S66 (A / B / C), ca în raportul de dimineață.

## Ce a rulat

- Comanda: `.venv/Scripts/python -X utf8 -m unelte.kronos_cod.functii curata --procese 12 --fire 16 --pana-la 08:40`
  (codul și cele 3 teste în dac45c7), pornită prin cascadă la 05:37:45 (proces 13496), încheiată la 06:35:24, **cod 0**.
- Durata: 3.456 s (~58 min), doar procesorul; placa n-a fost folosită. S-a terminat înainte de 08:40, deci nu ocupă fereastra
  lui Adrian 09:00–11:30.
- Intrare: `lucru/kronos_cod/functii/functii.tsv` (S65, (a+b+c) fără duplicate). 319.430 cerute, 0 negăsite.
- Ieșiri (în `lucru/`, NU în Git): `lucru/kronos_cod/functii/curata.json` (cifrele), `autonome.tsv` (lista: fișier, linie, sha,
  marcaje), `cutie.jsonl` (rezultatul cutiei pe fiecare funcție). Nimic șters sau mutat din date; nimic descărcat sau instalat.

## Cifrele, pas cu pas

| Pas | funcții | simboluri întregi | simboluri doar corp | cu (d): funcții | cu (d): simb. corp |
|---|---|---|---|---|---|
| (a+b+c) fără duplicate | 319.430 | 51.090.271 | 23.788.967 | 28.186 | 1.885.770 |
| (ii) netriviale | 301.328 | 49.738.495 | 23.680.193 | 26.620 | 1.876.211 |
| (iii) definiția trece în cutie | 233.498 | 36.243.833 | 17.907.917 | 20.225 | 1.413.332 |
| **(iii) + fără nume libere = autonome** | **83.349** | **9.467.615** | **3.545.959** | **7.182** | **283.714** |

Cutia: 233.498 `ok`, 67.830 `eroare` (definiția nu rulează singură). Cele mai dese nume lipsă la definiție (decoratori, adnotări):
`pytest` 7.412, `Dict` 3.345, `Optional` 2.929, `List` 2.495, `Union` 1.788, `builtins` 1.781, `jsii` 1.386, `Any` 1.353,
`HomeAssistant` 922, `np` 883.

Cele mai dese nume libere care scot o funcție din „autonome” (definiția trece, dar corpul cere ceva din fișier): `np` 14.912,
`os` 7.496, `pytest` 3.087, `sys` 2.409, `logger` 1.611, `warnings` 1.435, `time` 1.335, `numpy` 1.260, `utils` 1.245, `six` 1.201.
De observat: `os`, `sys`, `time`, `warnings`, `logging` sunt module de bază; funcțiile care le folosesc au
căzut probabil pentru că importul e sus în fișier, nu în funcție (de verificat dacă Adrian vrea o regulă mai blândă). Informativ: 4.265 autonome folosesc un modul permis neimportat în corp.

### Lungimea corpului (doar autonomele)

| linii de corp | funcții |
|---|---|
| 1 | 32.368 (38,8 %) |
| 2–3 | 18.112 |
| 4–8 | 20.640 |
| 9–15 | 8.182 |
| 16–30 | 4.047 |

| simboluri de corp | funcții |
|---|---|
| ≤ 16 | 30.633 |
| 17–64 | 36.380 |
| 65–256 | 15.711 |
| > 256 | 625 |

Rezervă: aproape 4 din 10 autonome au un singur rând de corp, iar 37 % au cel mult 16 simboluri; sunt mult mai scurte decât
soluțiile de examen.

### Primele 20 de pachete (autonome)

| pachet | funcții | simb. corp |
|---|---|---|
| pypi:tencentcloud-sdk-python | 5.424 | 140.905 |
| pypi:homeassistant | 2.501 | 58.423 |
| git_py:twisted | 2.283 | 100.794 |
| pypi:plotly | 1.912 | 18.590 |
| pypi:ibm-watson | 1.745 | 20.211 |
| git_py:sympy | 999 | 38.522 |
| pypi:spyder | 971 | 38.106 |
| pypi:ibm-platform-services | 916 | 10.342 |
| pypi:pymatgen | 915 | 51.668 |
| pypi:pyface | 733 | 24.826 |
| pypi:traitsui | 659 | 18.820 |
| pypi:zdesk | 636 | 32.933 |
| pypi:apache-libcloud | 615 | 31.570 |
| pypi:silx | 563 | 27.428 |
| pypi:atlassian-python-api | 531 | 23.387 |
| pypi:ezdxf | 526 | 19.737 |
| crates:rustpython | 497 | 21.335 |
| pypi:qiskit-terra | 496 | 20.757 |
| pypi:nltk | 476 | 31.204 |
| pypi:whitebox | 475 | 39.277 |

Licențele autonomelor: MIT 32.833, Apache-2.0 28.455, BSD 18.979, BSD-3-Clause 2.757, Apache-2.0 OR MIT 209,
Apache-2.0 OR BSD 43, BSD OR MIT 39, BSD-2-Clause 34.

### Exemple scurte autonome

1. `pypi:mpmath` (BSD), `mpmath/matrices/linalg.py:578`, 69 simboluri de corp:
   ```python
   def lu_solve_mat(ctx, a, b):
       """Solve a * x = b  where a and b are matrices."""
       r = ctx.matrix(a.rows, b.cols)
       for i in range(b.cols):
           c = ctx.lu_solve(a, b.column(i))
           for j in range(len(c)):
               r[j, i] = c[j]
       return r
   ```
2. `pypi:intervaltree` (Apache-2.0), `intervaltree/node.py:515`, 23 simboluri:
   ```python
   def __setitem__(self, key, value):
       """Sets the left (0) or right (1) child."""
       if key:
           self.right_node = value
       else:
           self.left_node = value
   ```
3. `pypi:biotite` (BSD), `biotite/structure/atoms.py:1009`, 29 simboluri: `__iter__` cu `while i < len(self): yield self.get_array(i)`.
4. `pypi:holoviews` (BSD), `holoviews/core/sheetcoords.py:404`, 50 simboluri: `positionlesscrop` (chemări de metode pe `self`).
5. `pypi:uiautomator2` (MIT), `uiautomator2/__init__.py:1725`, 88 simboluri: `current_ime`.

Observație cinstită: exemplul 5 folosește `re` (modul permis, neimportat în corp) — e printre cele 4.265 „cu modul permis
neimportat”. Iar multe autonome sunt metode care se sprijină pe `self`/`ctx` (nume locale după regulă, dar care nu „merg
singure” în sensul examenului, unde funcția e chemată cu date). Deci „autonome” e o margine de sus pentru „seamănă cu examenul”.

## Scurgerea

- Proba (20 de probleme, suprapuneri de 13 + soluția întreagă): 0 probleme cu suprapunere, 0 cu soluția exactă, 0 funcții atinse.
- Seturile ascunse — doar numărul: S58 (200) → 0 funcții cu soluția întreagă, 0 probleme atinse; ascuns2 (163) → 0 și 0.
  SHA verificat înainte și după: neschimbat la ambele.

## Verdictul (după pragurile scrise dinainte de supraveghetor)

- DESTUL PENTRU A = ≥ 10 mil. simboluri de corp la autonome; PUȚIN = < 3 mil.
- Autonome: **3.545.959** → **ÎNTRE**. Varianta A se poate, dar cu mai multe repetări (3,55 mil. × 3 ≈ 10,6 mil.) sau
  amestecată cu (d) / restul funcțiilor care trec cutia (17,9 mil. simboluri de corp la pasul (iii)).
- Informativ: autonome cu (d) = 7.182 funcții, 283.714 simboluri de corp.
- Nu e antrenare → fără pre-înregistrare (scris în coadă).

## Testele

`CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -m pytest -o addopts="" -q` → **1.186 passed, 1 skipped** (4 min 48 s).

## Ce urmează

- S67 → `gata`. În coadă nu mai e nimic `aprobat`.
- Aștept de la Adrian alegerea **S66** („da S66 A” / „da S66 B” / „da S66 C”, în hub, `COMENZI.md`). Dacă alege A, propun
  ca baza să fie pasul (iii) (17,9 mil.), cu autonomele repetate, nu doar autonomele, din cauza corpurilor de un rând.
