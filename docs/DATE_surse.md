# Sursele de date ale workstation-ului

*Scris de `unelte/curata_date_ws.py --raport` din `date/ws/brut/surse.json` (ce s-a descărcat) și din `date/ws/curat/*/info.json` (ce a rămas după curățare). Licența se citește de pe fișa oficială a sursei înainte de fiecare descărcare (`unelte/descarca_date_ws.py`). Datele nu intră în Git.*

## Ce s-a descărcat

| Sursa | De unde | Licența | Obligații | Verificat și descărcat | Mărime | Amprenta sha256 (primul fișier) |
|---|---|---|---|---|---|---|
| **wikipedia_ro**: Wikipedia în română, copia din 1 noiembrie 2023, curățată de Wikimedia | https://huggingface.co/datasets/wikimedia/wikipedia, revizia `b04c8d1ceb` | cc-by-sa-3.0 + gfdl | atribuire; ce redistribuim din ea rămâne sub aceeași licență (CC BY-SA) | 2026-10-12 | 0,47 GB | `3caae45c692dfa9b… (+1 fișiere)` |
| **wikisource_ro**: Wikisource în română, copia din 1 decembrie 2023, curățată de Wikimedia | https://huggingface.co/datasets/wikimedia/wikisource, revizia `f31a033f5f` | cc-by-sa-3.0 + gfdl | atribuire; aceeași licență la redistribuire; operele sunt mai ales în domeniul public | 2026-10-12 | 81,4 MB | `eb52fd71543a52bd…` |
| **tatoeba_en_ro**: Tatoeba engleză–română, prin OPUS (versiunea 2023-04-12) | https://object.pouta.csc.fi/OPUS-Tatoeba/v2023-04-12/moses/en-ro.txt.zip | cc-by-2.0-fr | atribuire (tatoeba.org) | 2026-10-12 | 0,6 MB | `41af9ea7e9aac93d…` |
| **europarl_en_ro**: Europarl v8 engleză–română, prin OPUS | https://object.pouta.csc.fi/OPUS-Europarl/v8/moses/en-ro.txt.zip | fara-licenta-formala | sursa se menționează (Parlamentul European permite reutilizarea) | 2026-10-12 | 39,5 MB | `6fcad948c6f5952a…` |
| **cod_instruct**: self-oss-instruct-sc2-exec-filter-50k: 50.000 de perechi sarcină–cod Python, verificate prin rulare | https://huggingface.co/datasets/bigcode/self-oss-instruct-sc2-exec-filter-50k, revizia `356bb069ee` | odc-by | atribuire | 2026-10-12 | 90,1 MB | `7bd6092e9940aede…` |
| **fabule_ro**: ds-tf3-ro-3m: 3 milioane de fabule în română, generate de alt model | https://huggingface.co/datasets/klusai/ds-tf3-ro-3m, revizia `16f01891f8` | apache-2.0 | atribuire; dacă modelul se publică vreodată, se reverifică termenii modelului care le-a generat | 2026-10-12 | 1,49 GB | `6a81171d4217fc7b… (+9 fișiere)` |
| **fineweb2_ro**: FineWeb-2, ron_Latn: un fișier din 20 (din el se taie o felie de 3 GB de text) | https://huggingface.co/datasets/HuggingFaceFW/fineweb-2, revizia `af9c13333e` | odc-by | atribuire; textele rămân ale site-urilor de unde au fost luate (termenii Common Crawl) | 2026-10-12 | 4,85 GB | `fc26165cfa257590…` |
| **cod_stack_smol**: The Stack smol, Python: 10.000 de fișiere de cod, fiecare cu licența lui | https://huggingface.co/datasets/bigcode/the-stack-smol, revizia `4a6938ce94` | pe-fisier | termenii The Stack, acceptați de Adrian cu contul lui; se păstrează doar fișierele cu licențe permisive, cu atribuirea lor (depozit, cale, licență) | 2026-10-12 | 87,0 MB | `9c40af895077d726…` |
| **cod_stack_dedup**: The Stack dedup, Python: 3 fișiere din 144 (din ele se taie o felie de cod curat) | https://huggingface.co/datasets/bigcode/the-stack-dedup, revizia `17cad72c88` | pe-fisier | termenii The Stack, acceptați de Adrian cu contul lui; se păstrează doar fișierele cu licențe permisive, cu atribuirea lor (depozit, cale, licență) | 2026-10-12 | 0,60 GB | `e505976824a91a4b… (+2 fișiere)` |

Amprentele tuturor fișierelor sunt în `date/ws/brut/surse.json`.

## Ce a rămas după curățare

| Sursa | Texte citite | Prea scurte | Stricate | Duplicate | Sedile înlocuite | Antrenare | Validare (1%, pusă deoparte) |
|---|---|---|---|---|---|---|---|
| cod_instruct | 50.661 | 0 | 0 | 0 | 2 | 50.193 texte, 65,1 MB | 468 texte, 0,6 MB |
| cod_stack | 162.085 | 178 | 25 | 90 | 0 | 138.096 texte, 0,67 GB | 1.454 texte, 6,9 MB |
| europarl_en_ro | 400.277 | 1.912 | 0 | 12.210 | 702.996 | 382.273 texte, 0,13 GB | 3.882 texte, 1,3 MB |
| fabule_ro | 3.000.000 | 0 | 1.459 | 664.231 | 10.981 | 2.310.788 texte, 3,52 GB | 23.522 texte, 35,9 MB |
| fineweb2_ro | 885.974 | 2.903 | 980 | 1 | 13.100.501 | 873.232 texte, 2,97 GB | 8.858 texte, 30,3 MB |
| tatoeba_en_ro | 16.301 | 0 | 0 | 24 | 1.427 | 16.110 texte, 1,5 MB | 167 texte, 0,0 MB |
| wikipedia_ro | 442.389 | 158.105 | 4.138 | 41 | 11.431 | 277.357 texte, 0,76 GB | 2.748 texte, 6,8 MB |
| wikisource_ro | 12.921 | 551 | 18 | 13 | 2.330 | 12.241 texte, 0,13 GB | 98 texte, 0,4 MB |
| **Total** | | | | | | **8,25 GB** | **82,2 MB** |

- **cod_stack** (cod din The Stack): din 162.085 fișiere văzute, aruncate înainte de restul curățării: 5.511 fără licență permisivă, 11.573 prea mici sau prea mari, 875 cu rânduri prea lungi, 4.179 generate automat, 104 cu prea puține litere și cifre. Licențe acceptate: 0BSD, Apache-2.0, BSD-2-Clause, BSD-3-Clause, BSD-3-Clause-Clear, CC0-1.0, ISC, MIT, MIT-0, Unlicense, Zlib. Atribuirile fișierelor păstrate (depozit, cale, licențe): `date/ws/brut/cod_stack_atribuiri.jsonl`. Felia se oprește la 0,68 GB.
- Curățarea: ş/ţ cu sedilă → ș/ț cu virgulă; fără duplicate; fără texte prea scurte sau stricate (codificare greșită, semnul „�”, prea puține litere la proză).
- Validarea: 1% din textele fiecărei surse, alese după amprenta textului. Nu se antrenează nimic pe ea, nici tokenizer-ul.
- TinyStories (CDLA-Sharing-1.0) era deja în `date/tinystories_tot/`, cu validarea lui.
