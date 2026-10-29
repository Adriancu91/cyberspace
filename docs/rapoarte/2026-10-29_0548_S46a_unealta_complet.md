# S46a — Kronos-Cod etapa 1b: modul `complet` al uneltei de descărcare + teste (fără rețea)

Executantul, 29 octombrie 2026, 05:30–05:48. Sarcina S46a (aprobată de supraveghetor la 05:15, granița 5).
**Nu s-a descărcat nimic, nu s-a instalat nimic, nu s-a atins `kronos/`, examenul, paznicul sau jurnalul.**
Dosarul pilotului (`lucru/kronos_cod/pilot/`) a fost doar citit (am verificat după: neschimbat).

## Pe scurt

- `unelte/kronos_cod/descarca.py` are acum modul **`complet`**: toate cele 6 surse din `docs/kronos_cod/SURSE.md`, cu **aceleași**
  funcții ca pilotul pentru licențe, data-limită 29 iunie 2021, filtre, ritm (crates ≤ 1 cerere/s, PyPI ≤ 5/s, GitHub ≤ 1/s),
  User-Agent, arhive doar în memorie și oprire sub 40 GB liberi. Ieșirea: `lucru/kronos_cod/complet/`.
- Reluare fără dubluri, deduplicare globală peste surse, `--limita-ore N` (oprire curată), rezumat pe surse.
- **Pilotul dă exact aceleași rezultate:** (1) amprenta SHA-256 a ieșirii pe o lume falsă, luată cu codul vechi înainte de
  schimbare, e identică după (`a587f715…84aa7`, acum test); (2) rezumatul pilotului **real** (1.003 pachete, 37.088 fișiere),
  refăcut în memorie cu codul nou, e identic cu `rezumat.json` de pe disc, la fel `aproape_duplicate.json` (206 s).
- **13 teste noi** (61 în fișier), toate fără rețea (orice conexiune face testul să pice). Toată suita: **1071 trec, 1 sărit**.
- Commit: `e638b01`.

## Comanda exactă pentru S46 (după „da”-ul lui Adrian)

```
.venv/Scripts/python -X utf8 unelte/cascada.py porneste S46 -- .venv/Scripts/python -X utf8 unelte/kronos_cod/descarca.py complet --limita-ore 10
```

Aceeași comandă, o dată pe noapte, până când `lucru/kronos_cod/complet/rezumat.json` are `"terminat": true`.
Fiecare bucată scrie rezumatul (fără aproape-duplicate); aproape-duplicatele (MinHash) se calculează o singură dată, la final.
Implicit: `--iesire lucru/kronos_cod/complet --pypi 30000`, crate-uri: toate.

## Ce face modul `complet`, pe surse (ordinea din SURSE.md, contează la duplicate)

| rândul din SURSE.md | eticheta în rezumat | ce ia | cum |
|---|---|---|---|
| 3 depozite Python | `git_py` | 22: numpy v1.21.0, scipy v1.6.3, pandas v1.2.5, scikit-learn 0.24.2, sympy-1.8, networkx-2.5.1, django 3.2.4, flask 2.0.1, click 8.0.1, jinja 3.0.1, httpx 0.18.2, scrapy 2.5.0, tornado v6.1.0, requests v2.25.1, pytest 6.2.4, black 21.6b0, attrs 21.2.0, rich v10.4.0, sqlalchemy rel_1_4_18, pydantic v1.8.2, twisted-21.2.0, pytorch v1.9.0 | arhiva tar.gz a tag-ului de la `codeload.github.com` (fără cont), în memorie |
| 4 depozite Rust | `git_rs` | 9: rust 1.53.0, cargo 0.54.0, tokio-1.7.0, serde v1.0.126, rust-analyzer 2021-06-21, bevy v0.5.0, alacritty v0.8.0, deno v1.11.2, ripgrep 13.0.0 (ca MIT) | la fel |
| 5 FreeBSD | `freebsd` | `release/13.0.0` (oglinda `freebsd/freebsd-src` de pe GitHub) | `contrib/` și `gnu/` (oriunde în cale, deci și `sys/contrib`, `sys/gnu`) sărite **înainte de citire**; fiecare fișier intră doar cu antet `SPDX-License-Identifier` BSD-2/BSD-3 (inclusiv `BSD-2-Clause-FreeBSD`/`-NetBSD`); fără antet → filtrul nou `antet_bsd` |
| 6 biblioteci C | `git_c` | 7: libuv v1.41.0, lua v5.4.3, jq-1.6, cJSON v1.7.14, redis 6.2.4 (fără `deps/`, copiate), zstd v1.5.0 (doar `LICENSE` = BSD, cum scrie în SURSE.md, nu `COPYING` = GPLv2), lz4 v1.9.3 (doar `lib/`, singurul dosar BSD-2, cu `lib/LICENSE`) | la fel |
| 1 PyPI | `pypi` | top 30.000 din `hugovk/top-pypi-packages` | exact ca la pilot (3 cereri pe pachet) |
| 2 crates.io | `crates` | **toate** crate-urile cu o versiune dinainte de dată, cele mai descărcate întâi | lista din dump-ul public `static.crates.io/db-dump.tar.gz` (o singură cerere, citit din memorie, păstrat ca `lista_crates_dump.json`); per crate: ultima versiune nescoasă, nu pre-lansare, dinainte de 29 iunie 2021; apoi **o singură cerere** (arhiva) |

Ce e nou față de pilot, și de ce:
- **Erori de rețea:** la `complet`, o eroare trecătoare (timeout, 5xx) **nu** închide pachetul: rămâne pentru reluare. După 10 la
  rând, unealta se oprește singură („rețeaua pare căzută”). „Lipsește” (404/403/410) și „prea mare” se închid ca la pilot
  (respins, motiv `retea`). Dacă rămân pachete amânate, rularea **nu** se declară terminată.
- **O eroare neașteptată** într-un pachet (arhivă ciudată) îl închide cu motivul `eroare` (vizibil în rezumat) în loc să
  oprească 2–3 nopți de descărcare. La pilot rămâne ca înainte (oprește tot).
- **Limite mai mari doar pentru depozitele mari:** arhivă ≤ 1 GB (pilot: 300 MB) și ≤ 4 GB citiți din ea (pilot: 2 GB), fiindcă
  FreeBSD și rust trec de 300 MB comprimat. Pentru PyPI și crates limitele rămân cele de la pilot.
- **Rezumatul** are în plus: `terminat`, `oprit` (motivul), `pypi_in_lista`, `crates_din_dump` (total / cu versiune dinainte de
  dată / fără), pe lângă tot ce avea (GB brut → curat, fișiere, simboluri, fiecare filtru, respinse pe motive, `pe_sursa`).
- **Aproape-duplicatele și rezumatul citesc `cod.jsonl` rând cu rând** (înainte îl încărcau tot în memorie; la 10–22 GB n-ar fi
  fost bine). Rezultatul e identic (verificat pe pilotul real).

## Testele noi (toate fără rețea)

1. pilotul dă exact aceeași ieșire ca înainte (amprentă SHA-256 luată cu codul vechi);
2. lista depozitelor urmează SURSE.md (ordinea 3, 4, 5, 6; 39 de depozite; licențe recunoscute; FreeBSD cu `contrib`/`gnu`);
3. dump-ul crates: ultima versiune bună (fără yanked, fără pre-lansare, 29 iunie 2021 00:00 deja exclus), ordinea după descărcări;
4. dump-ul în formatul vechi (descărcările în `crates.csv`);
5. ordinea surselor și **duplicatele între surse** (același fișier din depozit → aruncat la PyPI; din depozitul Rust → aruncat la crate);
   crate-urile nu ating API-ul crates.io; dump-ul se cere o dată;
6. **FreeBSD:** doar antet BSD (2 din 5 păstrate: fără antet, ISC, MIT aruncate), `contrib/` și `gnu/` nici citite; la pilot
   antetul `BSD-2-Clause-FreeBSD` rămâne respins, ca înainte;
7. opțiunile lz4 (`lib/`), zstd (doar `LICENSE`; fără opțiune ar fi respins pentru `COPYING` GPL), redis (fără `deps/`);
8. **`--limita-ore` + reluarea fără dubluri:** aceeași lume descărcată dintr-o bucată și în „nopți” de 1 oră (timp simulat) dă
   `cod.jsonl`, `pachete.jsonl` și `aproape_duplicate.json` **identice octet cu octet**; nicio arhivă cerută de două ori;
9. oprirea sub 40 GB (nicio cerere făcută);
10. rețeaua căzută: oprire după 10 erori la rând, pachetele nu se închid, reluarea le termină;
11. câteva erori de rețea: rularea nu se declară terminată;
12. 404 și eroare neașteptată la `complet` (închise cu motiv), la pilot eroarea oprește tot;
13. comanda `complet` cu valorile implicite.

`python -m pytest`: **1071 trec, 1 sărit** (4 min 12 s).

## Estimarea pentru S46 (timp și spațiu)

Din cifrele pilotului (21,7 min pentru 1.003 pachete; cam 17 min din ele erau ritmul de 1 cerere/s la crates):

| parte | cereri | timp estimat |
|---|---|---|
| 39 de depozite + FreeBSD | 39 arhive (~1–1,5 GB) | ~0,5 oră |
| PyPI 30.000 | 3 pe pachet, ≤ 5/s | ~5 ore (ritmul) + descărcarea; dacă lista are doar ~15.000, jumătate |
| crates.io | dump-ul (~1 GB, o cerere) + 1 pe crate, ≤ 1/s | ~60.000 de crate-uri cu versiune dinainte de dată (estimare) → ~17 ore |
| aproape-duplicatele, la final | — | ~1,5–3,5 ore (pilotul: 206 s pentru 0,376 GB) |
| **total** | | **~22–27 de ore** → 3 nopți cu `--limita-ore 10` (puțin peste cele 15–25 estimate de supraveghetor, din cauza crate-urilor la 1/s) |

Spațiu: ~10–22 GB cod curat (+~5 % pentru JSON) în `lucru/kronos_cod/complet/`; C: are acum ~73 GB liberi → ar rămâne ~50–62 GB.
Oprire automată sub 40 GB. Memorie: arhivele mari și dump-ul stau în memorie câte unul (≤ ~4 GB); semnăturile MinHash
~1 KB pe fișier (~1–2 GB la final). Workstation-ul are 128 GB.

## Ce n-am putut verifica fără rețea (spus deschis)

- **Tag-urile depozitelor** le-am scris din ce știu, fără să le pot verifica. Unul greșit dă 404 → pachetul apare respins cu
  motivul `retea` în rezumat (nu oprește nimic) și se poate corecta după. Cele mai nesigure: `rust-lang/cargo` `0.54.0`,
  `lua/lua` `v5.4.3`, `rust-lang/rust-analyzer` `2021-06-21`. Data se verifică oricum din arhivă (un tag de după 29 iunie 2021
  e respins cu `dupa_data_limita`).
- **lua:** oglinda de pe GitHub nu are, din câte știu, fișier LICENSE (licența e în `lua.h`) → probabil respinsă
  `fara_fisier_licenta`, după regula din SURSE.md. Nu am făcut excepție.
- **Lista PyPI:** din câte știu, `hugovk/top-pypi-packages` are acum ~15.000 de pachete, nu 30.000. Unealta ia câte sunt și scrie
  numărul în `pypi_in_lista`. Dacă e așa, PyPI aduce cam jumătate din cât estima SURSE.md (~5 GB).
- **Mărimea dump-ului crates.io** și a arhivei FreeBSD: limitele (4 GB, 1 GB) ar trebui să ajungă; dacă nu, pachetul apare respins
  cu motivul „prea mare”.
- Pasul 4 din „Cum se scot duplicatele” (scoaterea problemelor HumanEval/MBPP/APPS după 13-grame) **nu** e în unealta de
  descărcare: ține de curățare, după descărcare.

## Ce urmează

- Supraveghetorul verifică unealta (S46a) și trece comanda de mai sus în S46.
- **S46 (descărcarea întreagă) cere „da”-ul lui Adrian** (e `propus — necesită Adrian`). Eu nu pornesc nimic din rețea.
- Tokenizerul pe cod rămâne pentru al doilea „da”.
