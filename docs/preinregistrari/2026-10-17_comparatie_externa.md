# Pre-înregistrare: Comparația externă (pe procesor): Kronos #373 față de GPT-2 small și un GPT-Neo românesc de 125M, pe același examen

<!-- scrisa: 2026-10-17T17:38:01 -->
*Scrisă la 2026-10-17 17:38, înainte de rulare. După ce rularea a început, textul de mai jos nu se mai schimbă; la închidere
se adaugă doar secțiunea „Ce a ieșit” (python unelte/preinregistrare.py --inchide comparatie_externa).*

**Stare: așteaptă „da”-ul lui Adrian.** Nimic nu se descarcă și nimic nu rulează înainte de asta. Comparația nu
atinge placa video, jurnalul Kronos, examenul (`module/examen_bpb.py`) sau vreun model de-al nostru.

## Întrebarea

**Unde stă Kronos față de modele din afară de aceeași mărime, pe același examen?** Până acum am comparat Kronos doar
cu el însuși. Un reper din afară arată dacă 1,31 la română, 0,73 la cod și 0,44 la povești e mult sau puțin.

## Cine se compară

| | Kronos #373 (al nostru) | GPT-2 small | GPT-Neo românesc 125M |
|---|---|---|---|
| unde e | `lucru/stocare/modele/experiment_373.pt` | `openai-community/gpt2` | `iliemihai/gpt-neo-romanian-125m` |
| mărimea | 98 milioane de parametri | 124 milioane | 125 milioane |
| licența | a noastră | **MIT** (pe model) | **MIT** (pe model) |
| pe ce a învățat | 4,89 GB: 46% engleză simplă (TinyStories), 34% română, 15% cod Python, 5% numere; 30 de ore | WebText (2019): 40 GB de pagini web în engleză | ~40 GB de română: OSCAR (web), Opus, Wikipedia, literatură; 5,8 milioane de pași |
| context | 512 bucăți | 1.024 | 2.048 |
| descărcare | — | `model.safetensors`, 548 MB | `pytorch_model.bin`, 593 MB |

- **Licențe verificate azi** (din datele Hugging Face și GitHub, fără să descarc vreun model): GPT-2 small, MIT;
  GPT-Neo românesc 125M, MIT (autori: Ștefan Dumitrescu și Mihai Ilie). Ambele permit folosirea liberă, cu păstrarea
  mențiunii de licență.
- **Nealese:** `readerbench/RoGPT2-base` (124M, mărimea și forma lui GPT-2) are licența Apache-2.0 doar pe cod
  (GitHub), iar modelul de pe Hugging Face nu are nicio licență trecută. Rămâne rezervă, doar dacă Adrian vrea.
  `dumitrescustefan/gpt-neo-romanian-125m` nu mai e public. Cele de 780M și peste sunt de 6 ori mai mari decât Kronos.
- **De știut, despre siguranță:** modelul românesc există doar ca `pytorch_model.bin` (formatul vechi al lui PyTorch).
  Se încarcă cu `transformers` 5.18, care citește astfel de fișiere doar ca greutăți (`weights_only`), nu ca program.
- **Nu se instalează nimic:** `transformers`, `torch` și `safetensors` sunt deja în `.venv`. Descărcările (~1,1 GB)
  merg în `~\.cache\huggingface` (120 GB liberi pe C:).

## Ce rulează

- **Examenul:** exact cel al lui Kronos, `unelte/examen_validari_ws.py`, pe aceleași validări puse deoparte, cu
  aceleași primele 100.000 de litere din fiecare (aceeași tăiere la un text întreg):
  - **română** = Wikipedia, web (FineWeb-2) și cărți (Wikisource), media pe octeți;
  - **cod** = cod Python (The Stack) și sarcini de cod, media pe octeți;
  - **povești** = validarea TinyStories R2 (cea a examenului oficial).
  Se raportează și celelalte (fabule, traducere), dar ele nu intră în așteptări.
- **Nota = biți pe octet** (mai mic e mai bine): biții dați de model pe tot textul, împărțiți la octeții textului în
  UTF-8. Nu depinde de tokenizer, deci modele cu tokenizere diferite se compară direct.
- **La fel ca la Kronos:** textul se taie în ferestre de 512 bucăți, una după alta, fără suprapunere. Prima bucată a
  textului se socotește cu probabilitate egală pe tot vocabularul. Asta e **cifra principală**. Separat, doar ca
  informație, și cu fereastra lor obișnuită (1.024 de bucăți la GPT-2, 2.048 la GPT-Neo): acolo ar trebui să iasă
  puțin mai bine.
- **Kronos nu se măsoară din nou:** cifrele lui sunt cele din examenul de dimineață
  (`lucru/examen_validari_ws/experiment_373_20261017_061359.json`).
- **Doar pe procesor** (`CUDA_VISIBLE_DEVICES=-1`, 6 fire din 18), deci se poate rula și noaptea, lângă antrenare,
  fără să atingă placa video. Cred că durează cel mult 30 de minute pentru ambele modele. Rezultatul ajunge în
  `lucru/comparatie_externa/`, iar codul în `unelte/compara_externe.py`.

## Cu ce se compară: Kronos #373

| | #373 |
|---|---|
| **română** (media) | **1,3102** (Wikipedia 1,0345, web 1,5271, cărți 1,3667) |
| **cod** (media) | **0,7338** (cod Python 0,9256, sarcini de cod 0,5499) |
| **povești** | **0,4422** |

*Notă: în jurnalul Kronos, „bpb_cod” e media pe cod. Nota doar pe fișierul de cod Python (0,9256) se suprascrie cu
media, pentru că fișierul și grupa au același nume. Cifrele de mai sus sunt luate din fișierul complet al examenului.*

## De ce nu e o comparație perfect cinstită (dinainte)

- **Poveștile sunt „acasă” pentru Kronos:** a învățat pe TinyStories, iar validarea e din aceeași sursă. GPT-2 (2019)
  și GPT-Neo n-au văzut TinyStories, care a apărut în 2023. Acolo Kronos are un avantaj.
- **Româna ar putea fi „acasă” pentru GPT-Neo:** a învățat pe Wikipedia în română și pe web (OSCAR), deci se poate să fi
  văzut chiar textele din validările noastre (Wikipedia, web). Validările sunt puse deoparte doar față de Kronos.
- **GPT-2 nu știe română:** tokenizer-ul lui taie diacriticele în bucăți de octeți. La română e un reper de jos, nu un
  adversar.
- **Cantitatea de text:** GPT-2 și GPT-Neo au învățat pe ~40 GB fiecare, adică de vreo 8 ori mai mult decât amestecul
  nostru.

## Așteptările lui Claude Code, în cifre (cifra principală, ferestre de 512)

| | Kronos #373 | GPT-2 small (aștept) | GPT-Neo ro 125M (aștept) |
|---|---|---|---|
| română | 1,3102 | **2,0–2,8** (mult mai rău) | **0,9–1,2** (mai bine decât Kronos) |
| cod | 0,7338 | **0,9–1,4** (mai rău) | **1,4–2,5** (mult mai rău) |
| povești | 0,4422 | **0,75–1,0** (mai rău) | **1,2–2,0** (mult mai rău) |

Pe scurt, aștept ca **Kronos să-l bată pe GPT-2 small la toate trei** și ca **GPT-Neo românesc să-l bată pe Kronos la
română**, dar să piardă la cod și la povești. Cu fereastra lor obișnuită, aștept cifre cu 0,01–0,05 mai bune decât
la 512.

## Ce ar infirma așteptările

- **GPT-2 small mai bun decât Kronos la cod** (sub 0,7338) **sau la povești** (sub 0,4422). Ar însemna că 30 de ore
  pe amestecul nostru valorează mai puțin decât credem, chiar și „acasă”.
- **GPT-Neo românesc nu mai bun decât Kronos la română** (1,3102 sau peste). Asta ar fi o veste bună pentru Kronos:
  ar însemna că un model de aceeași mărime, cu de vreo 12 ori mai multă română, nu face mai bine.
- **Oricare cifră în afara intervalului așteptat cu mai mult de 0,2** înseamnă că am înțeles greșit ceva despre
  modelele astea. Asta se scrie în verdict, oricum ar ieși comparația.
- Verdictul se scrie pe fiecare rând de mai sus: **confirmat** sau **infirmat**, cu cifrele.

## Adăugat înainte de rulare (17 octombrie, 18:52): a văzut GPT-Neo textele noastre?

*Adrian a dat „da” la ~18:40 și a cerut să raportez și dacă modelul românesc a văzut probabil textele noastre din
Wikipedia. Secțiunea e scrisă înainte de orice descărcare; restul pre-înregistrării rămâne neschimbat.*

- **Testul „continuă din memorie”:** din fiecare validare (Wikipedia, web, cărți) iau primele 150 de texte de cel puțin
  500 de litere. Modelul primește primele ~300 de litere (tăiate la un spațiu) și scrie mai departe, alegând mereu
  bucata cea mai probabilă (fără întâmplare). Număr câte litere la rând se potrivesc **exact** cu textul adevărat.
  Un pasaj „din memorie” = cel puțin 50 de litere identice.
- **Martorul e Kronos #373**, care sigur n-a văzut validările. Pe Wikipedia sunt multe texte-tipar („X este o comună în
  județul Y…”), pe care le ghicește și un model care n-a văzut pagina. Deci contează diferența față de Kronos, nu cifra
  singură.
- **Regula, dinainte:** GPT-Neo **a văzut probabil** textele unei validări dacă partea lui de pasaje „din memorie” e cu
  **cel puțin 10 puncte procentuale peste Kronos și cel puțin dublă**. Altfel: „nu se vede că le-a văzut”, ceea ce nu
  dovedește că nu le-a văzut.
- **Al doilea semn, doar informativ:** raportul dintre nota pe Wikipedia și nota pe web. La Kronos e 1,0345 / 1,5271 =
  0,677. Dacă la GPT-Neo e mult mai mic, Wikipedia îi e mai „cunoscută” decât ne-am aștepta.
- **Ce aștept:** Kronos 3–15% pasaje „din memorie” pe Wikipedia, GPT-Neo 15–40%, deci „a văzut probabil” Wikipedia.
  Pe web (OSCAR și FineWeb-2 vin amândouă din Common Crawl) aștept o diferență mai mică, iar pe cărți niciuna clară.
- GPT-2 nu face acest test: nu știe română, deci nu spune nimic despre ce a văzut.

## Ce a ieșit

*Rulat sâmbătă, 17 octombrie, 18:58–20:01, doar pe procesor (6 fire, prioritate scăzută), lângă W2 noaptea 4 pe placă.
Modelele la versiunile fixate în `unelte/compara_externe.py`. Toate cifrele:
`lucru/comparatie_externa/comparatie_20261017_185839.json`. Kronos #373 nu s-a măsurat din nou.*

### Cifra principală (biți pe octet, ferestre de 512; mai mic e mai bine)

| | Kronos #373 | GPT-2 small | GPT-Neo ro 125M |
|---|---|---|---|
| **română** (media) | **1,3102** | 2,9542 | 1,5577 |
| — Wikipedia | 1,0345 | 2,5741 | 1,5715 |
| — web | 1,5271 | 3,1324 | 1,6334 |
| — cărți | 1,3667 | 3,1469 | 1,4726 |
| **cod** (media) | **0,7338** | 1,1869 | 3,4029 |
| — cod Python | 0,9256 | 1,3884 | 3,7364 |
| — sarcini de cod | 0,5499 | 0,9939 | 3,0834 |
| **povești** | **0,4422** | 0,9172 | 2,2628 |
| fabule (informativ) | 0,0944 | 2,7280 | 0,7486 |
| traducere (informativ) | 0,7732 | 2,2825 | 1,6612 |

Cu fereastra lor obișnuită: GPT-2 (1.024) iese mai bine cu 0,02–0,13 (română 2,8293, cod 1,1005, povești 0,8929).
GPT-Neo (2.048) iese **mai rău** (română 1,6186, cod 3,7175, povești 2,3314).

### Verdictul, pe fiecare așteptare

- **Kronos îl bate pe GPT-2 small la toate trei: confirmat.** Cod 0,73 față de 1,19, povești 0,44 față de 0,92.
- **GPT-2 la română 2,0–2,8: infirmat, puțin** (2,95). La cod (1,19) și la povești (0,92): **confirmat**.
- **GPT-Neo îl bate pe Kronos la română: infirmat.** 1,5577 față de 1,3102, deci Kronos e mai bun pe fiecare din cele
  trei validări. Asta e regula din „Ce ar infirma” care s-a împlinit. Pe hârtie e o veste bună pentru Kronos, dar
  vezi mai jos de ce nu înseamnă că Kronos știe română mai bine decât GPT-Neo, în general.
- **GPT-Neo la cod (1,4–2,5) și la povești (1,2–2,0): infirmat.** A ieșit mai rău: 3,40 și 2,26.
- **Trei cifre ale lui GPT-Neo ies din interval cu peste 0,2:** română cu 0,36, cod cu 0,90, povești cu 0,26. După
  regula de dinainte, asta înseamnă că **am înțeles greșit ceva despre model**: îl credeam mult mai bun pe română și
  mai puțin slab pe rest.
- **„Cu fereastra lor iese puțin mai bine”: confirmat doar la GPT-2. La GPT-Neo e infirmat.** La 2.048 iese mai rău
  decât la 512.

### Verificări făcute după, doar ca informație (cifra principală nu se schimbă)

- **Diacriticele nu sunt de vină.** Validările noastre au doar ș/ț cu virgulă dedesubt. Cu ş/ţ cu sedilă, GPT-Neo iese
  mult mai rău (Wikipedia 2,14 față de 1,57), deci virgula e chiar forma pe care a învățat-o.
- **Fereastra (GPT-Neo, Wikipedia):** 1,6994 la 128 de bucăți, 1,6180 la 256, 1,5715 la 512, 1,5632 la 1.024 și 1,6783
  la 2.048. Cel mai probabil a învățat pe texte de cel mult ~1.024 de bucăți, deși scrie că primește 2.048. Pe web e la
  fel (1,6307 la 1.024). Nici cu fereastra cea mai bună nu se apropie de 1,31.

### A văzut GPT-Neo textele noastre? (testul „continuă din memorie”)

| pasaje cu cel puțin 50 de litere identice | Kronos #373 (martor) | GPT-Neo ro 125M | verdictul, după regulă |
|---|---|---|---|
| Wikipedia (150 de texte) | 0,0% | 0,0% | nu se vede că le-a văzut |
| web (150) | 0,0% | 0,7% (un singur pasaj, 65 de litere) | nu se vede că le-a văzut |
| cărți (150) | 0,0% | 0,0% | nu se vede că le-a văzut |

- La amândouă, cele mai lungi potriviri pe Wikipedia sunt de 15–32 de litere, iar mediana e 1 literă.
- Așteptarea mea (GPT-Neo 15–40% pe Wikipedia) e **infirmată**.
- Cu ce s-a putut măsura aici, **nu se vede că GPT-Neo ar fi văzut textele noastre din Wikipedia**. Asta nu dovedește
  că nu le-a văzut: un model de 125M ține minte rar 50 de litere la rând. Dacă le-ar fi văzut, ar fi avut la Wikipedia
  o notă mai bună decât Kronos, dar a avut una mai proastă (1,57 față de 1,03).
- **La fabule e invers:** Kronos are 0,09, deci aproape le știe pe de rost, pentru că le-a văzut la antrenare (sursa e
  în amestecul lui). GPT-Neo are 0,75, neobișnuit de bine față de restul românei lui. E posibil să fi văzut și el
  fabulele, dar n-am testat. Fabulele nu intră în nicio concluzie.

### Ce înseamnă, cinstit

- **Kronos joacă „acasă” pe toate cele trei examene, nu doar la povești.** Validările de română sunt bucăți puse
  deoparte din **aceleași surse** pe care a învățat: aceeași Wikipedia, același FineWeb-2, același Wikisource, curățate
  la fel. GPT-Neo a învățat pe alte texte românești (OSCAR și altele, din 2021 sau mai devreme). Diferența cea mai mare
  e chiar pe Wikipedia (1,03 față de 1,57), unde potrivirea de formă contează cel mai mult. Pe web e cea mai mică
  (1,53 față de 1,63).
- **Concluzia sigură:** pe examenul nostru, Kronos #373 e mai bun decât două modele publice de aceeași mărime, la toate
  trei capitolele.
- **Concluzia care NU rezultă:** că Kronos știe română mai bine decât GPT-Neo în general. Pentru asta ar trebui un text
  românesc din afara surselor amândurora, de exemplu articole de presă scrise după octombrie 2026. Asta ar fi un pas
  următor, doar dacă Adrian vrea.
- GPT-2 nu știe română: e un reper de jos, cum era de așteptat. La cod și la povești e un adversar cinstit, iar Kronos
  îl bate clar.
