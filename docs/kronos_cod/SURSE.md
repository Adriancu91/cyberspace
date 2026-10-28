# Kronos-Cod (C-28, E4): sursele propuse și licențele lor

Scris de executant la S41 (etapa 1a), 28 octombrie 2026. **Nimic nu e descărcat încă**: lista o verifică supraveghetorul
și, pentru ce e marcat „necesită Adrian”, Adrian. Descărcarea = etapa 1b.

Cifrele de mărime sunt **estimări** (fără acces la rețea în etapa 1a nu le-am putut măsura); în etapa 1b se măsoară
întâi pe un eșantion pilot (vezi la sfârșit) și se corectează aici înainte de descărcarea mare.

## Regulile pentru tot ce intră

1. **Doar licențe MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause** (și combinațiile lor, de ex. `MIT OR Apache-2.0`).
   Licența se verifică de DOUĂ ori: din metadate (PyPI: clasificatorii `License :: OSI Approved :: ...`; crates.io:
   câmpul `license`, expresie SPDX) **și** din fișierul `LICENSE`/`COPYING` din arhivă (comparat cu textele de mai jos).
   Dacă cele două nu se potrivesc sau lipsește fișierul, pachetul nu intră. În fișierele cu antet
   `SPDX-License-Identifier:` contează antetul fișierului (se aruncă fișierele cu altă licență din pachete mixte).
   - MIT: <https://opensource.org/license/mit>
   - Apache-2.0: <https://www.apache.org/licenses/LICENSE-2.0>
   - BSD-3-Clause: <https://opensource.org/license/bsd-3-clause>
   - BSD-2-Clause: <https://opensource.org/license/bsd-2-clause>
   Apache-2.0 și BSD cer păstrarea mențiunilor de autor: păstrăm pentru fiecare fișier sursa, versiunea și licența
   (`lucru/kronos_cod/provenienta.jsonl`), ca lista de atribuiri să poată fi publicată dacă modelul iese din casă.
2. **Doar cod scris de oameni, fără nimic generat de un LLM.** Nu există un test sigur pentru asta, așa că folosim data:
   **doar versiuni publicate înainte de 29 iunie 2021** (ziua în care a apărut GitHub Copilot, primul asistent de cod
   larg folosit). Varianta mai largă, **30 noiembrie 2022** (apariția ChatGPT), aduce cam +40 % date, dar include anul
   în care Copilot era deja folosit; o propun doar ca alternativă (decide Adrian). Plus filtrele de cod generat automat
   de mai jos (generatoare clasice: protobuf, migrări, parsere generate etc.).
3. **Fără cont, fără autentificare, fără acceptarea unor termeni, fără cheie.** Tot ce cere așa ceva e mutat la
   „necesită Adrian”.
4. Limbaje: **Python** (~55 %), **Rust** (~35 %), **C** (~10 %). Doar fișierele `.py`, `.pyi`, `.rs`, `.c`, `.h`.
5. Ținta: **~3 miliarde de simboluri** după curățare (cu un tokenizer BPE pe cod, ~3,5 octeți pe simbol ⇒ ~10–11 GB de cod curat).

## Sursele propuse

| # | sursa | ce e | licența (cum se verifică) | estimare curat | simboluri (est.) | cum se descarcă fără cont |
|---|---|---|---|---|---|---|
| 1 | **PyPI, arhivele sursă (sdist)** | codul sursă al pachetelor Python publice; lista = cele mai descărcate ~30.000 de pachete (`hugovk/top-pypi-packages`, fișier JSON public) | clasificatorii PyPI + fișierul LICENSE din arhivă; rămân ~65–70 % din pachete | ~5 GB `.py` | ~1,4 mld | API-ul JSON public `https://pypi.org/pypi/<pachet>/json` (alegem ultima versiune dinainte de dată, sdist), fișierul de la `files.pythonhosted.org`; ≤ 5 cereri/s |
| 2 | **crates.io, arhivele `.crate`** | codul sursă al bibliotecilor Rust publice | câmpul `license` (SPDX) din dump + fișierul LICENSE din arhivă; rămân ~80 % | ~3,5 GB `.rs` | ~1,0 mld | lista și licențele din dump-ul public al bazei de date `https://static.crates.io/db-dump.tar.gz` (recomandat de crates.io în locul cererilor la API); arhivele de la `https://static.crates.io/crates/<nume>/<nume>-<versiune>.crate`; ≤ 1 cerere/s, cum cere politica crates.io |
| 3 | **Depozite Git mari, Python** (numpy, scipy, pandas, scikit-learn, sympy, networkx, django, flask, click, jinja, httpx, scrapy, tornado, requests, pytest, black, attrs, rich, sqlalchemy, pydantic, twisted, pytorch) | proiecte mari, bine întreținute; majoritatea sunt și pe PyPI (duplicatele se scot) | BSD-3 / MIT / Apache-2.0, fișierul LICENSE din depozit, la tag-ul ales | ~0,6 GB unic | ~0,15 mld | `git clone --depth 1 --branch <tag dinainte de dată> https://github.com/<org>/<proiect>.git` (clonarea publică nu cere cont) |
| 4 | **Depozite Git mari, Rust** (rust-lang/rust, cargo, tokio, serde, rust-analyzer, bevy, alacritty, deno, ripgrep) | compilatorul Rust și proiecte mari | `MIT OR Apache-2.0` / MIT / Apache-2.0 (ripgrep: `MIT OR Unlicense` → îl luăm ca MIT) | ~0,6 GB unic | ~0,17 mld | `git clone --depth 1 --branch <tag>` |
| 5 | **C: FreeBSD (sistemul de bază)** | nucleul și uneltele de bază FreeBSD, C scris de oameni din 1993 încoace | BSD-2/BSD-3, **pe fișier** după antetul `SPDX-License-Identifier` (prezent în FreeBSD din 2017); se aruncă `contrib/`, `gnu/` și orice fișier fără antet BSD | ~0,8 GB | ~0,25 mld | `git clone --depth 1 --branch release/13.0.0 https://git.freebsd.org/src.git` (sau oglinda de pe GitHub) |
| 6 | **C, biblioteci mici** (libuv, lua, jq, cJSON, redis ≤ 6.2, zstd, lz4) | cod C curat, bine scris | MIT / BSD-3 / BSD-2 (zstd: dublu BSD sau GPLv2 → îl luăm ca BSD; redis doar versiunile BSD-3, de dinainte de 2024) | ~0,1 GB | ~0,03 mld | `git clone --depth 1 --branch <tag>` |
| | **total** | | | **~10,6 GB** | **~3,0 mld** (incertitudine ±40 %) | |

Dacă pilotul arată mai puțin decât ținta, se mărește lista PyPI (de la 30.000 la 50.000 de pachete) și se adaugă toate
crate-urile, nu doar ultima versiune majoră; dacă e mai mult, se taie din coada PyPI (pachetele cele mai puțin descărcate).

## Necesită Adrian (nu le folosesc fără „da”)

| sursa | de ce |
|---|---|
| **The Stack v1/v2** (BigCode, Hugging Face) | cere cont Hugging Face și acceptarea termenilor; ar fi cea mai simplă sursă mare (deja deduplicată, cu licențe detectate) |
| **Software Heritage** (arhiva) | descărcarea în masă cere cont/cheie API |
| **GitHub în masă prin API** (căutare de depozite după licență) | fără cheie, limita e 60 de cereri/oră; cu cheie, ar cere un cont |
| **CPython** (biblioteca standard Python) | licența PSF-2.0: permisivă, dar nu e în lista MIT/Apache/BSD; cod Python foarte bun |
| **SQLite** | domeniu public (nu e o licență din listă) |
| **curl** | licența curl (asemănătoare MIT, dar alt text) |
| **ISC, Zlib, BSL-1.0, Unlicense, Python-2.0** (pachete PyPI/crates doar cu acestea) | permisive, dar în afara listei; ar adăuga ~5–8 % date |
| **data-limită 30 noiembrie 2022** în loc de 29 iunie 2021 | vezi regula 2 |

Nu se folosesc deloc: Stack Overflow (CC BY-SA), soluții de pe LeetCode/Codeforces (licențe neclare), orice set de
date „sintetic” sau „instruct” (generat de LLM), orice cod GPL/LGPL/MPL/AGPL.

## Cum se scot duplicatele

1. **Exact:** SHA-256 pe conținutul normalizat (CRLF → LF, fără spații la capăt de rând, fără rânduri goale la sfârșit);
   rămâne o singură copie (prima după ordinea surselor: depozitele mari întâi, apoi PyPI, apoi crates).
2. **Aproape la fel:** MinHash pe 5-grame de simboluri (128 de permutări, LSH cu 16 benzi × 8 rânduri), pragul
   Jaccard ≥ 0,85, într-un grup se păstrează fișierul cel mai lung. Scris de mine cu numpy (deja instalat), fără nimic nou.
3. **Bibliotecile copiate în alte pachete** (`vendor/`, `_vendor/`, `third_party/`, `site-packages/` din arhive) se
   aruncă înainte de pasul 1; codul original vine din sursa lui.
4. **Examenele:** se scot fișierele care conțin probleme din seturile publice cunoscute (HumanEval, MBPP, APPS — căutare
   după numele funcțiilor și 13-grame din enunțuri), ca rezultatele viitoare să nu fie umflate; și se verifică (13-grame)
   că niciun enunț din examenul nostru nu apare în date.

## Cum se scot fișierele generate automat sau nepotrivite

Se aruncă un fișier dacă:
- are în primele 20 de rânduri `generated by`, `auto-generated`, `autogenerated`, `do not edit`, `@generated`,
  `code generated`, `this file was automatically`;
- e un tip cunoscut de fișier generat: `*_pb2.py`, `*_pb2_grpc.py`, `*.pb.rs`, migrări Django (`*/migrations/0*.py`),
  `parsetab.py`, `lextab.py`, ieșiri Cython (`.c` cu antetul „Generated by Cython”), `bindgen` (`bindings.rs`), SWIG;
- e mai mare de 1 MB, are un rând mai lung de 1.000 de caractere, lungimea medie a rândului > 100, sau mai puțin de
  25 % caractere alfanumerice (date, tabele, cod minimizat);
- e în dosare de date de test (`fixtures/`, `testdata/`, `test_data/`) și are peste 50 % literali;
- nu se poate citi ca UTF-8 sau nu trece de analiza sintactică (Python: `ast.parse`; Rust/C: verificare simplă de
  paranteze echilibrate).

## Pilotul (primul pas din 1b)

Înainte de descărcarea mare: 500 de pachete PyPI + 500 de crate-uri + un depozit mare din fiecare limbaj, toate
filtrele de mai sus, apoi raport cu: GB brut → GB curat, simboluri, ce procent a aruncat fiecare filtru, câte licențe
nu s-au potrivit. Abia după ce supraveghetorul vede cifrele, descărcarea întreagă.
