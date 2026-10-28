# S41 — Kronos-Cod (C-28, E4), etapa 1a: sursele, examenul de cod, cutia izolată

Raport scris de executant (cascada), 28 octombrie 2026, 14:15. Sarcina: `plan/coada.md`, S41 (aprobată de Adrian prin
C-28, 27 oct 23:45; pașii scriși de supraveghetor). Doar procesor; **nimic descărcat, nimic instalat**; `kronos/`,
examenul BPB, paznicul, jurnalul, modelele și linia română neatinse.

## Pe scurt

- **Sursele** (`docs/kronos_cod/SURSE.md`): 6 surse fără cont, toate MIT / Apache-2.0 / BSD, Python + Rust + C,
  ~10,6 GB de cod curat ≈ **~3,0 miliarde de simboluri** (estimare ±40 %, se măsoară la pilot). Data-limită propusă:
  versiuni publicate **înainte de 29 iunie 2021** (apariția Copilot), ca să nu intre cod generat de LLM.
  8 lucruri trecute la „necesită Adrian” (The Stack cere cont HF, CPython are licență PSF etc.).
- **Examenul de cod** (`unelte/kronos_cod/examen_cod.py`): 20 de șabloane scrise de mine; **setul ascuns = 200 de probleme**,
  SHA-256 `90fc64cdebefc143f414474170eb9e9c936506204f9abfe0cff0268ddbdc3749`, ținut în `lucru/kronos_cod/examen_ascuns/`
  (nu în Git). Verificat: referințele **200/200 (100 %)**, corpul gol **0/200**, `return None` **0/200**. pass@1 și pass@10.
- **Cutia izolată** (`unelte/kronos_cod/cutie.py`): proces separat, dosar temporar, 4 straturi. Blocate și dovedite cu
  teste: citirea și scrierea în afara dosarului, rețeaua, pornirea de procese, `ctypes`, ieșirea prin subclase,
  importurile din afara listei, bucla infinită (limita de timp), alocarea uriașă (limita de memorie). **Pe Windows nu a
  trebuit instalat nimic**: limitele de memorie/procese vin dintr-un „job object” din `kernel32`.
- **Testele**: `999 passed, 1 skipped` (înainte 979; +13 teste ale cutiei, +7 ale examenului).
- Commit-ul cu codul: `cbac20a`.

## 1. Sursele (pe scurt; tot în `docs/kronos_cod/SURSE.md`)

| # | sursa | licența | estimare curat | simboluri |
|---|---|---|---|---|
| 1 | PyPI, arhivele sursă ale celor mai descărcate ~30.000 de pachete | MIT/BSD/Apache, verificat din metadate **și** din fișierul LICENSE | ~5 GB | ~1,4 mld |
| 2 | crates.io (lista și licențele din dump-ul public `db-dump.tar.gz`, arhivele de pe `static.crates.io`) | câmpul SPDX + LICENSE | ~3,5 GB | ~1,0 mld |
| 3 | depozite Git Python mari (numpy, scipy, pandas, scikit-learn, django, flask, sympy, pytorch …) | BSD-3/MIT/Apache | ~0,6 GB unic | ~0,15 mld |
| 4 | depozite Git Rust mari (rust-lang/rust, cargo, tokio, serde, bevy …) | MIT OR Apache-2.0 | ~0,6 GB unic | ~0,17 mld |
| 5 | FreeBSD, sistemul de bază (C), filtrat pe fișier după antetul SPDX | BSD-2/BSD-3 | ~0,8 GB | ~0,25 mld |
| 6 | biblioteci C mici (libuv, lua, jq, cJSON, redis ≤ 6.2, zstd, lz4) | MIT/BSD | ~0,1 GB | ~0,03 mld |

Toate se descarcă fără cont (API JSON public PyPI, fișiere statice crates.io, `git clone` public), cu limite de viteză
politicoase (PyPI ≤ 5 cereri/s, crates.io ≤ 1 cerere/s, cum cere politica lor).

**Necesită Adrian**: The Stack v1/v2 (cont Hugging Face + termeni), Software Heritage (cheie API), GitHub prin API în
masă (cheie), CPython (licență PSF-2.0, nu e în listă), SQLite (domeniu public), curl (licență proprie), pachetele doar
ISC/Zlib/BSL/Unlicense (~5–8 % date în plus), data-limită 30 nov 2022 (+~40 % date, dar include perioada cu Copilot).

Duplicatele: exact (SHA-256 pe text normalizat) + aproape-la-fel (MinHash, Jaccard ≥ 0,85, scris cu numpy, fără nimic
nou) + aruncarea dosarelor `vendor/`. Generatele automat: antete „generated / do not edit”, `*_pb2.py`, migrări,
Cython, bindgen, fișiere > 1 MB, rânduri > 1.000 de caractere, < 25 % alfanumerice, cod care nu se analizează sintactic.
Plus scoaterea examenelor publice cunoscute (HumanEval, MBPP, APPS) și verificarea că enunțurile noastre nu apar în date.

**Spus cinstit:** mărimile sunt estimări din ce știu despre aceste surse, nu măsurate (n-am voie la rețea în 1a).
De aceea 1b începe cu un pilot (500 PyPI + 500 crates + câte un depozit mare) care dă cifrele reale.

## 2. Examenul de cod

- 20 de șabloane: suma/numărul multiplilor, numărarea unor caractere, inversarea bucăților, „fizz-buzz” cu alte numere
  și cuvinte, recurențe modulo m, palindroame, rotiri, cifrul Cezar, comprimare RLE, al k-lea distinct, operații pe
  două liste, rânduri/coloane/diagonale de matrice, cuvântul cel mai des, numere prime într-un interval, cifre în baza b,
  paranteze echilibrate, aplatizare cu filtru, împărțire în bucăți, cmmdc/cmmmc, scrierea în baza b.
- Fiecare variantă schimbă parametrii din enunț (de ex. divizorul, baza, perechile de paranteze, regula de egalitate)
  și numele funcției; testele sunt calculate din referința mea, 4–8 pe problemă, cu cazurile-limită (listă goală, 0 …).
- Seturi: **probă** (sămânța 0, 20 de probleme, pentru teste), **ascuns** (200, sămânță aleatoare păstrată doar în
  `lucru/`, fără variantele setului de probă; unealta refuză să-l refacă dacă există). Fișa: `docs/kronos_cod/EXAMEN.md`.
- Verificarea setului ascuns în cutie (600 de rulări, 106 secunde, ~0,18 s pe rulare):

| corpul | pass@1 | stări |
|---|---|---|
| referința mea | **1,000** (200/200) | ok 200 |
| gol (`pass`) | **0,000** | picat 200 |
| greșit (`return None`) | **0,000** | picat 200 |

Cum arată o problemă (din setul de probă; modelul primește doar primele două rânduri și scrie corpul):

```python
def count_divisible_by_8(xs):
    """Return the number of the integers in `xs` that are divisible by 8."""
    return sum(1 for x in xs if x % 8 == 0)

assert count_divisible_by_8([]) == 0
assert count_divisible_by_8([8, 16, -8, 1]) == 3
assert count_divisible_by_8([27, -32, -11, -38, 43, -41, 37, -8, 10, 21, -38]) == 2
...
```

- Nota: pass@k = 1 − C(n − c, k) / C(n, k) (n răspunsuri pe problemă, c corecte); un răspuns e corect doar dacă trec
  toate testele și cutia n-a blocat nimic. Un răspuns care încearcă `import os` iese `interzis` și nu trece (testat).
- Atenție: șabloanele sunt în Git; „ascuns” = variantele exacte. Datele de antrenare (cod dinainte de 2021) nu pot
  conține acest depozit.

## 3. Cutia izolată: ce e blocat, ce nu

Straturile: (1) verificarea dinainte pe arborele codului (importuri doar din 23 de module de bază — math, re,
collections, itertools … —, fără `eval`/`exec`/`getattr`/`__import__`, fără atribute cu `_` în față); (2) `__builtins__`
tăiat (`open` doar în dosar, modulele date ca copii fără sub-module, deci fără `typing.sys`, `random._os`); (3) paznicul
de audit `sys.addaudithook` (nu se poate scoate): fișiere în afara dosarului, `socket.*`, `subprocess.*`, `os.system`,
`os.exec*/spawn*`, `ctypes.*`, `winreg.*`, `shutil.*`, orice import nou; (4) limitele procesului: timp (procesul e
oprit), și pe Windows un job object cu memorie (implicit 256 MB), timp de procesor și **cel mult un proces**.

| încercarea | cu verificarea dinainte | doar straturile 2–4 | testul |
|---|---|---|---|
| citirea unui fișier din afară (și `../../Windows/win.ini`) | — | **blocat** | ✓ |
| scrierea în afară (fișierul nu apare) | — | **blocat** | ✓ |
| conexiune de rețea (`socket.create_connection`) | **interzis** | **blocat** | ✓ |
| pornirea unui proces (`subprocess.run`, `os.system`; fișierul-semn nu apare) | **interzis** | **blocat** | ✓ |
| ieșirea prin `().__class__.__base__.__subclasses__()` → `os.system` | **interzis** | **blocat** | ✓ |
| `import os/sys/importlib/ctypes/shutil/pathlib`, `__import__`, `eval` | **interzis** | **blocat** | ✓ |
| `ctypes.WinDLL('kernel32')` | — | **blocat** | ✓ |
| buclă infinită | — | **timp** (oprit la 2 s) | ✓ |
| `bytearray(3 GB)` și o listă care tot crește | — | **memorie** (256 MB) | ✓ |
| codul tipărește un rezultat fals | — | ignorat (semnul secret e altul) | ✓ |
| citirea/scrierea în dosarul cutiei | merge | merge | ✓ |

Ce NU face / ce lipsește (spus clar):
- **Nu e o mașină virtuală.** Codul rulează în Python-ul de bază, sub contul Windows al executantului; protecția e în
  interiorul lui Python + limitele job object-ului. O greșeală în Python însuși (un defect de memorie exploatat) ar
  putea ocoli straturile 1–3.
- **Rețeaua e oprită doar din Python** (paznicul + importuri), **nu printr-o regulă de firewall**. O regulă Windows
  Firewall pentru `python.exe` sau un cont Windows separat fără drepturi ar fi stratul în plus; ambele sunt schimbări de
  setări Windows, deci **nu le-am făcut** — le propun lui Adrian dacă vrea o cutie mai tare înainte de etapa de
  auto-îmbunătățire (când codul rulat va fi scris de model în buclă).
- Limita „un singur proces” din job object e pusă, dar nu am putut-o testa separat (paznicul oprește pornirea înainte).
- Pe Linux/macOS limitele vin din `resource.setrlimit` (scris, netestat aici).
- Nu e nevoie de niciun port nou în `kronos/`: totul e în `unelte/kronos_cod/`.

## 4. Testele

`CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -m pytest`: **999 passed, 1 skipped** (4 min 15 s). Noi:
`teste/test_kronos_cod_cutie.py` (13) și `teste/test_kronos_cod_examen.py` (7). Niciun test vechi atins.

## 5. Propunerea pentru etapa 1b (descărcare + curățare + tokenizer BPE pe cod)

1. **Pilotul** (~1 oră): 500 PyPI + 500 crates + numpy + tokio + libuv, toate filtrele; raport cu GB brut → curat,
   simboluri, cât a aruncat fiecare filtru. Corectez cifrele din `SURSE.md`.
2. **Descărcarea întreagă**, în flux: fiecare arhivă se citește din memorie și se păstrează doar fișierele de cod care
   trec filtrele (arhivele nu se scriu pe disc). **Spațiul liber pe C: e doar 74 GB (85 % plin)**, de aceea fluxul;
   nevoie: ~25 GB (cod extras ~12 GB + curat ~11 GB + simbolurile ~6 GB, uint16) — încape, dar strâns.
   Timpul: e dictat de politețe, nu de bandă: crates.io ≤ 1 cerere/s × ~55.000 ≈ **15 ore**; PyPI ~30.000 × 2 cereri la
   5/s ≈ **3–4 ore**; depozitele Git ~1 oră. În total **~20 de ore**, pe procesor și rețea (nu încurcă placa), în 2–3 nopți
   sau în paralel cu antrenările.
3. **Curățarea și duplicatele**: ~3–5 ore pe procesor (128 GB RAM ajung pentru MinHash pe ~3 milioane de fișiere).
4. **Tokenizerul BPE pe cod**: antrenat pe un eșantion de ~1 GB, 32.768 de simboluri, spațiile de indentare păstrate ca
   simboluri; ~1–2 ore; apoi tokenizarea celor ~11 GB, ~2–4 ore. Atenție: e un tokenizer nou ⇒ o linie de model nouă;
   C-28 e comanda lui Adrian, dar îl întreb explicit înainte de antrenare.
5. Ce aștept: „da” pentru descărcarea din 1b (pilotul întâi), răspunsul la data-limită (2021 sau 2022) și la cele 8
   surse „necesită Adrian”; supraveghetorul scrie pragurile pentru etapa 2 (pass@10 pe setul ascuns).

## Ce aștept de la Adrian

- Verificarea listei de surse și „da”/„nu” pentru etapa 1b (descărcarea, începând cu pilotul).
- Data-limită: 29 iunie 2021 (recomandat, mai sigur fără LLM) sau 30 noiembrie 2022 (+~40 % date).
- Dacă vrea o cutie mai tare (regulă de firewall sau cont Windows separat) înainte de bucla de auto-îmbunătățire.

## Altceva din rularea asta

- S42 rămâne `oprit` (nu `aprobat`), deci n-am atins-o. Procesul ei 21116 s-a încheiat la 13:35 (cod 0); am resetat
  butonul STOP pe care îl apăsasem la 12:36 (`python -m kronos porneste --config config/conv_w2_e3_reteta_A.toml`),
  cum scrisesem în raportul `2026-10-28_1236_S42_oprit_reluare.md`. Placa e liberă.
