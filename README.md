# Cyberspace: Kronos + module

Un AI construit de la 0, pe platforma **Cyberspace**: un nucleu mic, numit **Kronos**, și **module înlocuibile**.
O buclă de experimente îl face să se îmbunătățească singur: propune o schimbare, antrenează,
dă examen, păstrează doar ce e mai bun și notează totul în jurnal.

Stadiu: **Etapa N1 (scheletul)** e gata și testată, plus primele module reale
(modelul n-gram și GPT-ul nostru, care a rulat o noapte pe placa video: cel mai bun scor 2,1873).
**Etapa M1 (memoria ierarhică)** e construită și testată. Comparațiile arată că memoria, așa cum e acum, nu ajută:
cu 8 sau 4 niveluri strică, iar cu 2 niveluri nu schimbă nimic măsurabil.
**Etapa M2, primul pas** e gata: TinyStories, tokenizerul nostru pe bucăți de cuvinte (4.096 simboluri) și GPT-ul
pe litere sau pe bucăți. Pe bucăți de cuvinte, scorul pe TinyStories e 0,8822 (pe litere: 1,3174).
**Etapa M2, pasul 2 (plasa de noduri, versiunea minimă)** e construită și testată. Testul în două runde, la același
număr de pași, arată că plasa păstrată între runde nu schimbă nimic măsurabil (efect +0,0002, sub zgomot). 166 de teste trec.

---

## Ghid pentru prima seară

Totul se face în terminalul din VS Code. Deschide VS Code, apoi:
**File → Open Folder → alege folderul `cyberspace`**, apoi terminalul cu **Ctrl+`**.

Poți să-i spui lui Claude Code: *„Citește README.md și CLAUDE.md și ghidează-mă pas cu pas, începând cu Pasul 1.”*

> Pune folderul `cyberspace` undeva simplu, de ex. `C:\Users\<numele tău>\proiecte\cyberspace`,
> nu pe Desktop sau în OneDrive (sincronizarea încetinește și poate bloca fișiere).

### Pasul 1 — Python și Git (≈10 min)

Verifică dacă le ai deja:

```
python --version
git --version
```

Dacă lipsesc (sau Python e mai vechi de 3.11):

```
winget install Python.Python.3.12
winget install Git.Git
```

Închide și redeschide terminalul după instalare.

### Pasul 2 — Mediul proiectului (≈3 min)

```
python -m venv .venv
.venv\Scripts\activate
pip install pytest
```

Dacă PowerShell spune că rularea scripturilor e blocată, rulează o singură dată
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, apoi din nou `.venv\Scripts\activate`.
Când mediul e activ, linia din terminal începe cu `(.venv)`. **Activează-l de fiecare dată** când redeschizi terminalul.

### Pasul 3 — Verificarea mediului

```
python unelte/verifica_mediu.py
```

Arată Python, Git, placa video (RTX 3060) și spațiul pe disc. PyTorch încă lipsește; e normal.

### Pasul 4 — Testele

```
python -m pytest
```

Trebuie să vezi `passed`. Câteva teste pot fi `skipped` până instalăm PyTorch (Pasul 7).

### Pasul 5 — Prima buclă, de probă (≈30 secunde)

```
python -m kronos ruleaza --config config/proba.toml
python -m kronos jurnal --config config/proba.toml
```

Vezi pe ecran fiecare experiment: ce s-a propus, scorul (`val_bpb`, **mai mic = mai bine**)
și decizia: `PĂSTRAT`, `respins` sau `ANULAT`.

### Pasul 6 — Shakespeare (≈2 minute)

```
python unelte/descarca_date.py
python -m kronos ruleaza --config config/laptop.toml --experimente 10
python -m kronos scrie --config config/laptop.toml --inceput "ROMEO:"
```

Testat: în ~45 de secunde, scorul a coborât singur de la 4,82 la 2,42.
Ultima comandă pune cel mai bun model să scrie în stilul Shakespeare.

### Pasul 7 — PyTorch cu placa video (≈10 min)

1. Deschide [pytorch.org/get-started/locally](https://pytorch.org/get-started/locally/).
2. Alege: **Stable · Windows · Pip · Python · CUDA** (cea mai nouă versiune CUDA din listă).
3. Copiază comanda afișată și rulează-o în terminal (cu `.venv` activ).
4. Verifică:

```
python unelte/verifica_mediu.py
python -m pytest
```

Trebuie să apară `PyTorch vede placa: NVIDIA GeForce RTX 3060 Laptop GPU` și toate testele `passed`.

> **Dacă apare `WinError 4551` („An Application Control policy has blocked this file ... shm.dll”):**
> e Smart App Control din Windows 11, care blochează fișierele nesemnate din PyTorch.
> Se oprește din *Windows Security → App & browser control → Smart App Control settings → Off*
> (din aprilie 2026 se poate reporni oricând din același loc, dar cât e pornit, PyTorch nu merge direct în Windows).
> Varianta care îl păstrează pornit: rularea prin WSL2 (Linux în Windows).

### Pasul 8 — GPT-ul nostru pe placa video

Un test scurt, 2 experimente (≈15 minute, 5 minute de antrenare fiecare):

```
python -m kronos ruleaza --config config/laptop_gpt.toml --experimente 2
```

Dacă merge, îl poți lăsa peste noapte (~12 experimente pe oră):

```
python -m kronos ruleaza --config config/laptop_gpt.toml --experimente 100
```

Dimineața: `python -m kronos jurnal --config config/laptop_gpt.toml` și `python -m kronos scrie --config config/laptop_gpt.toml --inceput "ROMEO:"`.

**Oprire:** `Ctrl+C` în terminal, sau dintr-un al doilea terminal `python -m kronos opreste --config config/laptop_gpt.toml`
(termină experimentul în curs, apoi se oprește). Pentru a porni din nou: `python -m kronos porneste --config ...`.
Dacă placa trece de 85°C, platforma face singură pauze de răcire.

### Pasul 9 — Salvarea în Git

Proiectul are deja Git, cu primul commit făcut. O singură dată, spune-i lui Git cine ești:

```
git config --global user.name "Numele tău"
git config --global user.email "adresa ta de email"
```

Apoi, după fiecare pas reușit:

```
git add .
git commit -m "ce am făcut, pe scurt"
```

---

## Ce e în proiect

| Folder | Ce conține | Cine îl modifică |
| --- | --- | --- |
| `kronos/` | registru, contracte, configurare, orchestrator, jurnal, paznic | doar tu (cu teste) |
| `module/` | piesele înlocuibile: modele, date, examen, cercetător... | agentul și noi |
| `config/` | ce modul stă pe fiecare port, cu ce setări | noi |
| `teste/`, `teste_contracte/` | testele platformei și examenul fiecărui port | noi |
| `unelte/` | descărcarea datelor, verificarea mediului | noi |
| `lucru/` | jurnalul experimentelor, modelele salvate (se creează singur) | nimeni de mână |

Modulele de acum, pe cele 10 porturi:

| Port | Modul | Ce face |
| --- | --- | --- |
| model | `model_ngram` / `model_gpt` / `model_plasa` / `model_plasa_adaptiva` / `model_continuu` | n-gram pe caractere (fără GPU) / GPT mic de la 0 (pe GPU) / GPT cu 5 noduri și plasă (M2) / GPT cu un nod pe raft și noduri libere (M3) / GPT care continuă de unde a rămas (bucla: o stare pentru fiecare arhitectură) |
| date | `date_mostra` / `date_fisier` / `date_tinystories` | propoziții generate / un fișier text (Shakespeare) / povești TinyStories (~20 MB) |
| examen | `examen_bpb` | val_bpb pe text nevăzut la antrenare |
| cercetător | `cercetator_aleator` / `cercetator_local` | schimbă câte o setare, pornind de la cea mai bună rețetă / întâi fiecare valoare din listă, apoi strânge căutarea în jurul celor mai bune 3 rețete |
| rulare | `rulare_locala` | laptopul: limită de timp, măsoară memoria video |
| stocare | `stocare_disc` | folderul `lucru/stocare` |
| interfață | `interfata_consola` | mesajele din terminal |
| memorie | `memorie_ierarhica` / `memorie_goala` | biblioteca de sensuri din WordNet (coduri, relații, plasă) / fără memorie |
| profesor, traducere | module „de jucărie” | respectă contractul, devin reale în fazele următoare |

## Memoria ierarhică (Etapa M1)

O bibliotecă de sensuri construită din Open English WordNet 2024 (120.630 de sensuri, licență CC-BY 4.0).
Fiecare sens are un cod pe niveluri, ca o cotă de bibliotecă: parte de vorbire → raft (ex. `noun.animal`)
→ poziția fiecărui strămoș (entity > … > mammal > … > equine > horse). Memoria mai ține relațiile dintre
sensuri (parte din, membru din, opus) și o „plasă” cu drumurile deja căutate și de câte ori au fost folosite.

GPT-ul cu `memorie = true` primește, la fiecare literă, codul **ultimului cuvânt terminat**, niciodată
al cuvântului în curs (ar fi trișat la examen; testul `test_memoria_nu_dezvaluie_viitorul` verifică).

```
python unelte/construieste_biblioteca.py                              # o singură dată (~13 MB, câteva secunde)
python -m kronos cauta horse --config config/laptop_gpt_memorie.toml   # unde stă un cuvânt în memorie
python unelte/compara_memorie.py                                      # cu / fără memorie, 3 semințe, la același timp
python unelte/compara_memorie.py --pasi 35000                         # cu / fără memorie, la același număr de pași
python -m kronos ruleaza --config config/laptop_gpt_memorie.toml --experimente 60   # bucla cu memorie
```

Limită cunoscută: WordNet nu are cuvintele de legătură (the, and, to, my, you), iar unele cuvinte vechi
primesc un sens greșit („thou” = prescurtarea lui „thousand”). Pe Shakespeare, memoria găsește 69% din cuvinte.

### Rezultate (3 octombrie 2026)

**La același timp** (5 minute de antrenare, rețeta câștigătoare: 2 straturi, lot 16, rata 0.0003; `val_bpb`, mai mic = mai bine):

| Sămânța | Fără memorie | Cu memorie | Diferență | Pași (fără / cu) |
| --- | --- | --- | --- | --- |
| 1337 | **2,1779** | 2,2414 | −0,064 | 44.949 / 36.921 |
| 2024 | **2,1856** | 2,2496 | −0,064 | 45.657 / 32.609 |
| 7 | **2,1983** | 2,2218 | −0,024 | 42.825 / 37.182 |
| media | **2,1873** | 2,2376 | −0,050 | |

Memoria a fost mai slabă la toate cele trei semințe. Face cu 15–29% mai puțini pași în același timp și are de
învățat 196.000 de parametri în plus (617.248 față de 421.632). Atenție: la același timp, numărul de pași depinde
de cât de repede merge placa în acel moment, așa că aceeași rețetă cu aceeași sămânță a dat 2,1873 azi-noapte și
2,1779 azi. La același număr de pași, rezultatul se repetă exact (vezi mai jos).

**La același număr de pași** (exact 35.000 de pași pentru ambele variante, pe aceleași date, în aceeași ordine,
3 semințe), după câte niveluri din codul cuvântului folosește memoria:

| Niveluri folosite | Parametri ai memoriei | Fără memorie (media) | Cu memorie (media) | Diferență (media) | Diferența la semințele 1337 / 2024 / 7 | Secunde cu memorie | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 8 | 195.616 | **2,2009** | 2,2369 | −0,036 | −0,043 / −0,041 / −0,024 | 281–286 | strică |
| 4 | 78.816 | **2,2009** | 2,2199 | −0,019 | −0,026 / −0,022 / −0,009 | 264–271 | strică |
| 2 | 9.856 | 2,2009 | 2,2032 | −0,002 | −0,008 / −0,008 / +0,009 | 254–295 | nehotărât |

- Fără memorie, scorurile s-au repetat exact în toate cele trei comparații (2,1990 / 2,2055 / 2,1982), iar
  antrenarea a durat 229–245 de secunde. Antrenarea la număr fix de pași e reproductibilă: diferențele vin din
  memorie și din sămânță, nu din placa video. De la o sămânță la alta, câștigul variază cu aproximativ ±0,01.
- Toate trei folosesc biblioteca cu 12 niveluri, din care modelul ia primele 8, 4 sau 2. Rândul cu 8 niveluri e
  dinainte de reparația categoriilor nevăzute la antrenare (care primeau o descriere neantrenată, la 0,7% din
  literele examenului); 4 și 2 au rulat după reparație.

**Concluzie:** cu cât memoria folosește mai multe niveluri, cu atât strică mai mult. Cu 8 niveluri, la antrenare
greșește mai puțin la toate semințele (de ex. 1,755 față de 1,845 biți pe literă, măsurat pe ultimul lot), dar la
examen e mai slabă: arată a „tocire”, pentru că nivelurile adânci sunt aproape cât cuvântul însuși. Cu 2 niveluri
(partea de vorbire și raftul) nu strică, dar nici nu ajută măsurabil. Pentru acest GPT mic, pe litere, memoria din
WordNet în forma de acum nu aduce câștig. Idei rămase: cuvintele de legătură în bibliotecă (acum lipsesc 31% din
cuvinte), un model mai mare sau o antrenare mai lungă.

## Etapa M2: TinyStories și bucăți de cuvinte (primul pas, fără plasa de noduri)

- **Datele** (`module/date_tinystories.py`): povești scurte în engleză din `roneneldan/TinyStories` (Hugging Face,
  licență CDLA-Sharing-1.0). Se descarcă doar începutul fișierelor oficiale: 21.896 de povești de antrenare (18 MB)
  și 2.466 de validare (2 MB), din fișierul oficial de validare. Poveștile rămân întregi, iar validarea nu conține
  povești din antrenare.
- **Tokenizerul** (`module/tokenizer_bpe.py`): bucăți de cuvinte (BPE pe octeți), scris de noi și antrenat doar pe
  textul de antrenare: 4.096 de simboluri, aproximativ 4 octeți pe simbol („ the”, „ and”, „ uncomfortable”...).
  Orice text se poate scrie cu el, fără simbol „necunoscut”.
- **GPT-ul** are setarea `tokenizer = "litere"` sau `"bpe"`. Examenul rămâne în biți pe octet, deci cele două se
  compară direct. Cu memorie, fiecare simbol primește codul ultimului cuvânt terminat până la ultima lui literă
  completă (nimic din viitor; testul `test_memoria_pe_simboluri_nu_vede_viitorul`).

```
python -m module.date_tinystories                                       # datele (o singură dată, ~15 s)
python unelte/antreneaza_tokenizer.py                                   # tokenizerul (o singură dată, câteva secunde)
python -m kronos ruleaza --config config/laptop_tinystories.toml --experimente 1   # bucăți de cuvinte, apoi litere
python -m kronos scrie --config config/laptop_tinystories.toml --inceput "Once upon a time"
```

### Primul test (3 octombrie 2026)

Aceeași rețetă (2 straturi, lot 16, rata 0.0003), 5 minute de antrenare pe placa video, fără memorie:

| Tokenizer | val_bpb (mai mic = mai bine) | Pași | Parametri | Memorie video |
| --- | --- | --- | --- | --- |
| **bucăți de cuvinte** (4.096) | **0,8822** | 43.916 | 937.472 | 204 MB |
| litere | 1,3174 | 43.294 | 425.216 | 191 MB |

Pe bucăți de cuvinte, scorul e cu o treime mai bun. În același timp, ambele au apucat aproape același număr de
pași (~44.000), dar fiecare pas al modelului pe bucăți vede de aproximativ 4 ori mai mult text (128 de simboluri ≈
500 de litere); în schimb, are și de 2 ori mai mulți parametri (tabela de 4.096 de simboluri). Scorurile de pe TinyStories nu se compară cu cele de pe Shakespeare: textul e mult mai simplu.
Început de poveste scris de modelul pe bucăți: *„Once upon a time, there was a big slide. Inside, there was a little
swing and he was loving around with lots of fun. The sun was bright… Lily and the fairy had fun playing all day.”*

**Acoperirea bibliotecii de sensuri pe TinyStories:** 71,5% din cuvinte sunt găsite (Shakespeare: 69%). Textul de
antrenare are 3,5 milioane de cuvinte, dar doar 9.846 de cuvinte diferite. Lipsesc tot cuvintele de legătură
(the, and, to, they, she, with, you), numele (Tim) și separatorul dintre povești.

## Etapa M2, pasul 2: plasa de noduri (versiunea minimă)

`module/model_plasa.py` (ModelPlasa, pe portul „model”), pornind de la GPT-ul pe bucăți de cuvinte:

- **Trunchiul comun** (straturile GPT-ului) și, deasupra, **5 noduri mici**: ființe (noun.animal, noun.person,
  noun.plant), locuri și obiecte (noun.location, noun.artifact, noun.object), acțiuni (verb.\*), însușiri (adj.\*,
  adv.\*) și rezervă (cuvinte negăsite, de legătură și rafturile nepuse în alt grup). Fiecare simbol merge la nodul
  raftului ultimului cuvânt terminat (din memorie, fără viitor). Pe TinyStories: rezervă 58% din simboluri,
  însușiri 16%, locuri și obiecte 9%, ființe 8%, acțiuni 8%.
- **Nodul central** adună ieșirile nodurilor, ponderate. Nodurile pornesc „tăcute”: la început, modelul e identic
  cu GPT-ul simplu.
- **Plasa** (`plasa = true`): legături între noduri, cu tărie între 0 și 1, păstrate între experimente în
  `lucru/plasa.json`. Regulile:
  - **naștere** (tărie 0,1, în probă): un nod „cere” de la altul (ponderea învățată către el trece de 0,05) **și**
    un cuvânt al primului nod e urmat de unul al celuilalt de cel puțin **1,5× mai des decât întâmplător** (măsurat
    pe textul de antrenare). Cerut inițial 3×, dar pe TinyStories nicio pereche nu trece de 1,95×;
  - **întărire**: câștigul la examen × cât a fost folosită legătura (folosirea singură nu ajunge);
  - **slăbire**: un câștig negativ înmulțește tăria cu până la 0,7, fără s-o taie direct;
  - **uitare** 1% la fiecare experiment; peste 0,9 devine **definitivă**;
  - **tăiere**: doar după 2 experimente la rând cu tăria sub 0,05.
  Legăturile cu nodul central sunt fixe. Plasa nu vede niciodată textul de examen: primește câștigul doar ca număr,
  prin ușa `dupa_examen` din Kronos (schimbare aprobată), iar starea ei intră în jurnal la fiecare experiment.
- **Costul:** cu nodurile, modelul face ~90–100 de pași pe secundă (GPT-ul simplu: ~147).

Asocierea măsurată (de câte ori mai des decât întâmplător e urmat un cuvânt al nodului din stânga de unul al
nodului de sus): ființe → acțiuni 1,95; acțiuni → însușiri 1,86; locuri/obiecte → acțiuni 1,65; toate celelalte
perechi sub 1,3.

```
python unelte/compara_plasa.py     # testul în două runde, la același număr de pași (25.000), semințele 0, 1, 2, ~1 oră
```

### Primul test în două runde (3 octombrie 2026)

Validarea împărțită în două jumătăți; pentru fiecare sămânță: fără plasă runda 1 și 2, apoi cu plasă runda 1 și 2
(plasa păstrată între rundele ei). 5 minute de antrenare fiecare:

| Varianta | Sămânța | Runda 1 | Runda 2 | Runda 2 − runda 1 | Pași (runda 1 / runda 2) |
| --- | --- | --- | --- | --- | --- |
| fără plasă | 1337 | 0,9236 | 0,9201 | −0,004 | 34.511 / 35.981 |
| fără plasă | 2024 | 0,9092 | 0,9580 | +0,049 | 36.263 / 28.617 |
| cu plasă | 1337 | 0,9762 | 0,9325 | −0,044 | 25.848 / 33.807 |
| cu plasă | 2024 | 0,9477 | 0,9219 | −0,026 | 28.746 / 33.916 |

Scriptul a scris „plasa a ajutat runda 2”, dar **testul e neconcludent**:
- În runda 1, varianta cu plasă a pierdut la ambele semințe, deci câștigul primit a fost negativ și toate legăturile
  născute (17, respectiv 20) au fost slăbite și tăiate. **Runda 2 cu plasă a pornit tot cu o plasă goală**, ca runda 1:
  nu s-a păstrat nimic de folosit.
- În aceleași 5 minute, numărul de pași a variat între 25.848 și 36.263 (placa s-a încins: 3 pauze de răcire), iar
  scorul urmează aproape exact numărul de pași. Diferențele vin din viteză, nu din plasă; probabil și pierderea din
  runda 1 (care a tăiat legăturile) vine tot de aici.

### Al doilea test în două runde: la același număr de pași (3 octombrie 2026)

Cu regulile de mai sus: 25.000 de pași pentru fiecare rulare (nu 5 minute), semințele 0, 1, 2, pauze de răcire
între rulări (până la 70°C). Toate cele 12 rulări au ajuns exact la 25.000 de pași, iar plasa a avut 3 legături la
începutul rundei 2 la fiecare sămânță, deci testul e valid.

| Sămânța | Fără R1 | Fără R2 | Cu R1 | Cu R2 | Δ fără (R2−R1) | Δ cu (R2−R1) | Legături la final R1 → R2 | Pași/s fără / cu |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 0,9707 | 0,9811 | 0,9697 | 0,9804 | +0,0104 | +0,0107 | 3 → 3 | 114 / 92 |
| 1 | 0,9744 | 0,9832 | 0,9743 | 0,9824 | +0,0088 | +0,0081 | 3 → 3 | 89 / 86 |
| 2 | 0,9760 | 0,9834 | 0,9750 | 0,9831 | +0,0074 | +0,0081 | 3 → 3 | 92 / 98 |

- **Legături născute: 9 în total**, câte 3 la fiecare sămânță, în runda 1: exact cele trei perechi permise de
  asociere (ființe → acțiuni, locuri/obiecte → acțiuni, acțiuni → însușiri). Câștigurile primite au fost pozitive dar
  mici (+0,0001…+0,0011), deci legăturile s-au întărit doar puțin (0,10 → 0,11–0,13) și au rămas în probă. Toate
  legăturile unei semințe au aceeași tărie: câștigul e un singur număr pentru tot modelul.
- **Efectul plasei păstrate**, (cu R2−R1) − (fără R2−R1): +0,0004, −0,0006, +0,0008; în medie **+0,0002**, de 25 de ori
  sub pragul de zgomot (0,005). **Verdict: MIC (noroc).** Plasa păstrată din runda 1 nu schimbă nimic măsurabil în
  runda 2.
- În schimb, în toate cele 6 perechi, varianta cu plasă a fost puțin mai bună decât cea fără, pe aceeași rundă și
  sămânță (cu 0,0001…0,0011; în medie 0,0007). E constant, dar de 7 ori sub pragul de zgomot: practic neglijabil.
- Runda 2 e ceva mai grea decât runda 1 (Δ fără ≈ +0,009); de aceea se compară diferențele, nu scorurile direct.

## Etapa M3: plasa adaptivă

### Pasul 1: rafturile WordNet pe TinyStories (fără antrenare)

`unelte/masoara_rafturi.py` numără, pe textul de antrenare (3.548.954 de cuvinte), câte cuvinte cad pe fiecare raft
al bibliotecii și câte sunt **umplutură**: cuvintele de legătură (the, a, and, it, to, can...) și cele negăsite.

Sensul principal din dicționar greșește des pe povești: said = adjectiv, saw = proverb, play = piesă de teatru,
very = adjectiv, Lily = crin, Tom = motan. De aceea memoria are acum setarea `sens_dupa_context` (oprită implicit,
deci rezultatele vechi rămân la fel), cu 4 reguli care se uită **doar în urmă**:

- **a) formele de verb** (said, saw, went; looked, smiling) primesc sensul de verb. Excepții: ground, feed, wound, bit
  (în dicționar sunt și trecutul lui grind, fee, wind, bite).
- **b) numele:** un cuvânt cu literă mare în mijlocul propoziției e nume de persoană (noun.person), dar nu și cele
  scrise numai cu majuscule (TV). Un nume văzut în mijlocul unei propoziții rămâne nume și la început de propoziție,
  **în aceeași poveste** (textul de antrenare are 21.895 de povești lipite; ținute minte pe tot textul, „One-Eye”
  dintr-o poveste făcea nume din fiecare „One day...” de după, iar „Yes”, „Thank”, „Look” deveneau și ele nume).
- **c) 16 adverbe fixe:** very, then, now, back, still, just, only, here, well, much, even, away, later, together,
  far, fast („little” nu: în povești e aproape mereu adjectiv).
- **d) după** to / will / can / let's / don't / I / you / we / they, în aceeași propoziție, cuvântul primește sensul
  de verb (to play, let's go, I want).

Cu toate regulile, **648.889 de cuvinte (18,3%) și-au schimbat raftul**: a) 301.520, d) 110.186, b) 91.326 în mijlocul
propoziției și 71.632 ținute minte, c) 74.225. Primele 10 rafturi (procente din cuvintele cu sens, 51,2% din text):

| Raft | % | Cele mai dese |
| --- | --- | --- |
| noun.person | 15,1 | tim, mom, lily, tom, friends |
| adj.all | 8,3 | big, happy, sad, new, other |
| noun.artifact | 7,4 | ball, toy, car, house, toys |
| adv.all | 7,2 | very, once, together, too, then |
| verb.communication | 4,9 | said, named, asked, thank, told |
| verb.motion | 4,4 | went, came, go, ran, walked |
| noun.animal | 3,8 | bird, dog, cat, bear, fish |
| verb.emotion | 3,8 | wanted, loved, liked, felt, scared |
| noun.act | 3,1 | fun, let's, put, best, help |
| noun.quantity | 3,0 | one, little, lots, lot, two |

- **33 de rafturi** au cel puțin 0,5% din cuvintele cu sens (un nod fiecare); celelalte 11 merg la nodul „rar”.
  25 de rafturi acoperă 90%.
- **Asocierea** (cuvinte vecine, cu ordine, perechi văzute de cel puțin 100 de ori): din 592 de perechi, 62 trec de
  2×, **29 trec de 3×**, 10 trec de 5×. Cele mai puternice: noun.quantity → noun.time 24,8× („one day”),
  verb.social → noun.shape 17,0× („took turns”), noun.phenomenon → verb.body 9,8× („wind blew”).
- Greșeli rămase: adjectivele pe care WordNet le pune întâi ca substantive (little, small, good, red, old, sweet) și
  numele de la începutul unei povești, înainte să apară în mijlocul unei propoziții.

```
python unelte/masoara_rafturi.py --sens-dupa-context    # ~15 secunde; rezultatul și în lucru/rafturi_tinystories_context.json
```

### Pasul 2: modelul adaptiv

`module/model_plasa_adaptiva.py` (ModelPlasaAdaptiva, pe portul „model”), cu `config/laptop_plasa_adaptiva.toml`:

- **Un nod pe raft:** câte un nod mic (64 de neuroni ascunși, ca în M2) pentru fiecare raft cu cel puțin 0,5% din
  cuvintele cu sens (33 pe TinyStories), plus nodul „rar” pentru celelalte 11 rafturi: 34 de noduri. Rafturile se aleg
  la primul experiment și nu se mai schimbă. Umplutura (44% din simboluri) rămâne pe trunchi, fără nod. Memoria are
  pornite `sens_dupa_context` și `fara_cuvinte_de_legatura`.
- **Rezerva de 6 noduri libere:** după fiecare examen se numără cuvintele primite de fiecare nod la antrenare (nimic din
  textul de examen). Un nod cu peste 2× media primește un nod liber, care preia cam jumătate din cuvintele lui: cuvinte
  întregi (Tim și Mom pe un nod, Lily și Tom pe celălalt); pe coduri n-ar merge, fiindcă toate numele au același cod.
  Nodurile alocate nu se mută. Un nod liber se întoarce în rezervă după 3 examene la rând în care raftul lui a primit
  mai puțin decât media. Alocările intră în jurnal și lucrează **de la experimentul următor**.
- **Legăturile** urmează regulile din M2 (naștere, întărire, slăbire, uitare, tăiere), cu pragul de naștere **3×**
  (cuvinte vecine, cu ordine, perechi văzute de cel puțin 100 de ori). Pe TinyStories, 18 perechi de noduri trec.
- **Fiecare simbol calculează doar nodul lui și nodurile legate de el**: legăturile vii și perechile care se pot naște
  (fără ele, un nod n-ar putea „cere” o legătură nouă). În medie, 1,9 noduri pe simbol din 34; restul nu se calculează.
- Nodurile pornesc tăcute: la început, modelul e identic cu GPT-ul simplu (testul `test_la_inceput_e_identic_cu_gpt_ul`).

**Costul**, cu aceeași rețetă (2 straturi, lot 16), 1.500 de pași pe placa video:

| Model | Pași pe secundă | Memorie video |
| --- | --- | --- |
| GPT simplu | 143 | 344 MB |
| plasa veche (5 noduri, toate calculate) | 99 | 345 MB |
| plasa adaptivă (34 de noduri, doar cele necesare) | 98 | 349 MB |

Memoria video rămâne mult sub limita de 5,5 GB, deci nodurile n-au trebuit micșorate.

### Pasul 3: comparația la 25.000 de pași (4 octombrie 2026)

Prin Kronos, pentru fiecare sămânță (0, 1, 2), câte un experiment din fiecare variantă, pe toată validarea (o singură
rundă), oprit la exact 25.000 de pași, cu aceeași rețetă (2 straturi, lot 16, rata 0,0003, bucăți de cuvinte). Cu
aceeași sămânță, cele trei văd aceleași bucăți de text, în aceeași ordine. Între rulări: 30 de secunde de pauză și
răcire până la 70°C. Toate cele 9 rulări au ajuns exact la 25.000 de pași, deci scorurile se pot compara.

| Sămânța | GPT simplu | Plasa veche (5 noduri) | Plasa adaptivă | Adaptivă − simplu | Adaptivă − plasa veche | Pași/s: simplu / veche / adaptivă |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | 0,9818 | 0,9697 | **0,9670** | −0,0148 | −0,0026 | 146 / 118 / 98 |
| 1 | 0,9770 | 0,9743 | **0,9704** | −0,0066 | −0,0039 | 145 / 116 / 102 |
| 2 | **0,9761** | 0,9750 | 0,9774 | +0,0013 | +0,0025 | 145 / 98 / 102 |
| media | 0,9783 | 0,9730 | **0,9716** | −0,0067 | −0,0014 | |

- **Plasa adaptivă față de GPT-ul simplu: NECONCLUDENT.** În medie e mai bună cu 0,0067 (peste pragul de zgomot de
  0,005), dar doar la 2 semințe din 3; la sămânța 2 e puțin mai slabă. O bună parte din avantaj vine de la sămânța 0,
  la care GPT-ul simplu a ieșit cel mai slab.
- **Plasa adaptivă față de plasa veche: MICĂ (noroc).** Diferența medie (−0,0014) e de 3,5 ori sub prag, iar semnul
  diferă de la o sămânță la alta.
- Plasa veche a fost mai bună decât GPT-ul simplu la toate cele 3 semințe (−0,0121, −0,0027, −0,0011), dar doar o dată
  peste prag. De la o sămânță la alta, scorul aceleiași variante variază cu 0,005–0,010: cam cât pragul.
- **Legături născute:** în plasa veche, 3 la fiecare sămânță (singurele permise: ființe → acțiuni, locuri/obiecte →
  acțiuni, acțiuni → însușiri). În plasa adaptivă, 13, 11 și 12 din cele 18 perechi posibile (cererile învățate au
  ajuns la 0,22; pragul e 0,05). La toate trei semințele: noun.person → verb.communication, noun.animal →
  verb.communication, verb.communication → noun.communication, verb.motion → noun.location, noun.quantity →
  noun.animal, adj.all → noun.possession, noun.attribute → noun.artifact, verb.competition → adv.all, verb.change →
  noun.attribute, noun.body → noun.animal, noun.substance → noun.group.
- **Noduri libere alocate:** 4 din 6, aceleași la fiecare sămânță (încărcarea vine din același text de antrenare):
  pentru noun.person (preia tim, tom, girl...), adj.all (big, new, many...), noun.artifact (ball, house, box...) și
  adv.all (very, too, back...), fiecare cu jumătate din cuvintele raftului.
- **Important:** legăturile născute și nodurile alocate lucrează abia de la experimentul următor. În această rundă
  unică, plasa adaptivă a lucrat cu 34 de noduri, fără ajutoare și fără legături, deci scorurile compară doar
  împărțirea pe rafturi (34 de noduri față de 5), nu și adaptarea. Efectul ei se vede doar într-o a doua rundă.
- **Costul:** la același număr de pași, nodurile ajută cel mult puțin; la același timp, nu. GPT-ul simplu face ~145 de
  pași pe secundă, plasa adaptivă ~100, deci în același timp GPT-ul ar face ~36.000 de pași în loc de 25.000. Pașii în
  plus contează mult: GPT-ul simplu a ajuns la 0,8822 după 43.916 pași (Etapa M2), față de ~0,978 după 25.000 aici.

```
python unelte/compara_plasa_adaptiva.py     # semințele 0, 1, 2; 25.000 de pași; ~45 de minute
```

### Pasul 4: runda 2 (4 octombrie 2026)

Ca testul în două runde din M2: aceleași semințe și 25.000 de pași, dar examenul pe a doua jumătate a poveștilor de
validare. Fiecare plasă a pornit cu ce a hotărât în runda 1 la aceeași sămânță: plasa adaptivă cu 11–13 legături
(tăria 0,099) și 4 noduri libere alocate (38 de noduri active), plasa veche cu cele 3 legături ale ei. GPT-ul simplu a
rulat primul, ca martor, pe aceeași linie din jurnal: câștigul primit de plasa adaptivă după examen e cât a bătut-o pe
el. R1 = toată validarea (din pasul 3), R2 = a doua jumătate; GPT-ul simplu, antrenat la fel, arată cât de diferit e
textul de examen. **Efectul adaptării = (R2 − R1 plasa adaptivă) − (R2 − R1 GPT simplu).**

| Sămânța | Simplu R1 | Simplu R2 | Adaptivă R1 | Adaptivă R2 | R2−R1 simplu | R2−R1 adaptivă | Efectul adaptării | Plasa veche R1 → R2 | Efectul plasei vechi |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 0,9818 | 0,9926 | 0,9670 | 0,9778 | +0,0108 | +0,0108 | −0,0000 | 0,9697 → 0,9798 | −0,0007 |
| 1 | 0,9770 | 0,9886 | 0,9704 | 0,9784 | +0,0115 | +0,0080 | −0,0036 | 0,9743 → 0,9821 | −0,0037 |
| 2 | 0,9761 | 0,9850 | 0,9774 | 0,9910 | +0,0089 | +0,0136 | +0,0047 | 0,9750 → 0,9831 | −0,0008 |

- **Verdict, plasa adaptivă: MICĂ (noroc).** Efectul mediu e +0,0004, de 12 ori sub pragul de zgomot (0,005), cu semn
  diferit de la o sămânță la alta. Plasa n-a pornit goală, toate rulările au avut exact 25.000 de pași, deci testul e
  valid: ce a hotărât plasa în runda 1 (legăturile și nodurile libere) nu schimbă nimic măsurabil în runda 2.
- **Plasa veche: MICĂ (noroc)**, efect mediu −0,0017, la toate semințele în același sens, dar sub prag (ca în M2).
- **Legăturile:** toate au fost folosite (folosire 0,05–0,42; 0,1 = deplină). La semințele 0 și 1, câștigul primit a
  fost pozitiv (+0,0148, +0,0102), deci s-au întărit de la 0,099 la 0,296; la sămânța 2, negativ (−0,0060), deci au
  slăbit la 0,080. **Atenție:** câștigul vine din avantajul întregii plase față de GPT-ul simplu, pe care îl avea și în
  runda 1, fără legături. Legăturile s-au întărit deci fără să fi adus ele câștigul: semnalul de învățare din M2 nu
  deosebește contribuția legăturilor de restul rețelei.
- **Noduri libere folosite:** liber1 (jumătate din noun.person: 7,6% din cuvinte), liber2 (adj.all, 4,2%), liber3
  (noun.artifact, 3,7%), liber4 (adv.all, 3,6%). După runda 2 s-au alocat și ultimele două, pentru o rundă 3:
  liber5 ia jumătate din cuvintele lui liber1 (tim, friend, mia...), liber6 jumătate din noun.person (mom, max, sue...).
- **Legături noi în runda 2:** câte 10–11, multe spre și dinspre nodurile libere (liber1 → verb.communication,
  verb.motion → liber4...). La final: 22–23 de legături pe sămânță.
- Viteza în runda 2, cu 38 de noduri: ~97 de pași pe secundă (cu 34: ~100).

```
python unelte/runda2_plasa_adaptiva.py      # pornește de la ultima comparație din lucru/; ~45 de minute
```

### Pasul 5: comparația la timp egal (4 octombrie 2026)

Câte 5 minute de antrenare fiecare (pregătirea plasei intră în timpul ei), fără limită de pași, pe toată validarea,
plasa adaptivă pornită goală. Înainte de fiecare rulare: 30 de secunde de pauză și răcire până la 70°C (placa a pornit
de fiecare dată la 60–70°C).

| Sămânța | Pași GPT simplu | Scor GPT simplu | Pași plasa adaptivă | Scor plasa adaptivă | Adaptivă − simplu |
| --- | --- | --- | --- | --- | --- |
| 0 | 40.047 | **0,8970** | 27.744 | 0,9440 | +0,0470 |
| 1 | 41.150 | **0,8864** | 28.468 | 0,9465 | +0,0602 |
| 2 | 40.792 | **0,8855** | 27.119 | 0,9627 | +0,0772 |
| media | 40.663 | **0,8896** | 27.777 | 0,9511 | +0,0614 |

- **Verdict: MARE, dar în rău.** La același timp, GPT-ul simplu e mai bun la fiecare sămânță, în medie cu 0,061: de 12
  ori pragul de zgomot. În aceleași 5 minute face cu ~46% mai mulți pași (~40.700 față de ~27.800), iar pașii în plus
  contează mult mai mult decât câștigul pe pas al nodurilor (cel mult ~0,007, la pași egali).
- Concluzia etapei M3: la pași egali, plasa adaptivă e cel mult puțin mai bună (neconcludent), adaptarea dintre runde
  nu aduce nimic măsurabil, iar la timp egal pierde clar. Ca să merite, nodurile ar trebui să fie aproape gratuite
  (sub ~5% încetinire) sau să aducă un câștig pe pas de zeci de ori mai mare.

```
python unelte/compara_timp_egal.py           # semințele 0, 1, 2; 5 minute fiecare; ~40 de minute
```

## Etapa M3: testul în trei trepte (propus de Adrian)

O plasă adaptivă mai mare decât cel mai mare GPT care încape pe placă, antrenată pe trei texte tot mai mari, fără să
pornească vreodată de la zero, cu GPT-ul la plafon ca martor.

### Pregătirea (4 octombrie 2026)

**Plafonul GPT-ului simplu** (`unelte/plafon_gpt.py`): cel mai mare GPT care se antrenează sub 5,5 GB (memoria rezervată,
mai strictă decât cea verificată de paznic), cu lot 8 și context 256, 20 de pași; fiecare încercare într-un proces separat.

| Lățime (n_emb) | Straturi | Capete | Parametri | Memorie ocupată / rezervată | Pași pe secundă |
| --- | --- | --- | --- | --- | --- |
| 512 | 55 | 8 | 175,6 M | 5.339 / 5.462 MB | 3,8 |
| 768 | 27 | 12 | 194,7 M | 5.064 / 5.478 MB | 4,2 |
| 1024 | 17 | 16 | 218,6 M | 5.158 / 5.256 MB | 4,0 |
| **1280** | **11** | **20** | **222,0 M** | **5.094 / 5.400 MB** | **4,3** |
| 1536 | 7 | 24 | 205,0 M | 4.466 / 5.010 MB | 4,8 |
| 2048 | 4 | 32 | 210,4 M | 4.340 / 4.938 MB | 5,0 |

**Plafonul: 1280 × 11 straturi, 20 de capete, 222.024.960 de parametri.** Atenție: pe Windows, o placă plină nu dă
eroare, ci împrumută în tăcere memorie din RAM și devine foarte lentă; de aceea limita se păzește strict.

**Plasa mare** (`module/model_plasa_mare.py`, `config/laptop_m3_plasa_mare.toml`), **333,6 M parametri = 1,50× plafonul**:
- trunchiul pe placă: 1280 × 6 straturi (123,6 M), cu optimizatorul lui;
- 34 de noduri + 6 libere în RAM, câte 2.048 de neuroni ascunși (210,0 M), cu greutățile întregi și optimizatorul lor
  (AdamW „topit” al PyTorch, pe procesor). La fiecare pas urcă pe placă doar nodurile cerute de lot (o copie bf16, pe
  jumătate de mărime), iar gradienții lor coboară înapoi; placa nu ține niciodată stările optimizatorului nodurilor;
- între experimente se păstrează tot: greutățile trunchiului și ale nodurilor, optimizatorii, legăturile cu tăria lor,
  alocările nodurilor libere. Un nod liber alocat pornește ca o copie a nodului ajutat; când tăria unei legături se
  schimbă, cererea învățată se ajustează invers, ca rețeaua să nu sară.
- Pe TinyStories, 2 minute: **2,0 pași pe secundă** (GPT-ul la plafon: 4,3), memorie video 3,4 GB ocupată / 4,3 GB
  rezervată; pe pas, urcarea nodurilor ~0,07 s, coborârea gradienților ~0,14 s, optimizatorul din RAM ~0,16 s: împreună
  **75% din timpul de antrenare** (cu un optimizator scris pas cu pas era 82%, 1,45 pași pe secundă).

**Martorul** (`module/model_continuu.py`, `config/laptop_m3_gpt_plafon.toml`): GPT-ul la plafon, care continuă și el de
unde a rămas (greutăți, optimizator).

**Datele**, fără suprapunere (poveștile identice cu ale lui R1 se scot din R2); examenul fiecărei trepte pe o bucată
nevăzută din textul ei (primele 100.000 de caractere ale validării, ca până acum):

| Treapta | Text | Antrenare | Examen |
| --- | --- | --- | --- |
| R1 | TinyStories de acum | 21.896 de povești, 18 MB, 3,5 M cuvinte | 2 MB |
| R2 | TinyStories, bucata de după R1 (10×) | 219.751 de povești, 180 MB, 35,5 M cuvinte | 2 MB (tot de după R1) |
| R3 | Simple English Wikipedia (20231101, CC BY-SA 4.0 / GFDL) | 239.329 de articole, 270 MB, 43,4 M cuvinte | 1.758 de articole, 2 MB |

De ce Simple English Wikipedia pentru R3: e liberă, mai grea (fapte, nume, cifre, cuvinte rare, propoziții mai lungi;
tokenizerul TinyStories o taie în mai multe bucăți), dar tot în engleză simplă, deci memoria rămâne folositoare; și e
mai mare decât R2. Cere pachetul `pyarrow` (instalat cu pip).

**Cum se măsoară:** fiecare treaptă e împărțită în bucăți de câte 10 minute de antrenare, fiecare bucată un experiment
Kronos cu examenul oficial la final, deci scorul la fiecare 10 minute. Pregătirea (un text de 270 MB se împarte o singură
dată și se ține minte în `lucru/cache/`) nu intră în cele 10 minute. În fiecare interval rulează întâi martorul, apoi
plasa, cu pauză și răcire înainte.

```
python unelte/plafon_gpt.py                       # plafonul GPT-ului (~10 minute)
python unelte/trepte_plasa_mare.py --trepte 1     # treapta 1 (~50 de minute); apoi --trepte 2, --trepte 3
```

### Treapta 1: R1, TinyStories, 20 de minute (4 octombrie 2026)

Sămânța 0; în fiecare interval de 10 minute, întâi martorul, apoi plasa, fiecare continuând de unde a rămas.

| Minutul | Plasa mare | GPT la plafon | Pași/s plasa / GPT | Mutarea nodurilor |
| --- | --- | --- | --- | --- |
| 10 | 1,4836 | **1,2560** | 2,1 / 4,1 | 73% din timp |
| 20 | 1,3019 | **1,0880** | 1,9 / 4,1 | 75% din timp |

- **Verdict: DA, funcționează și învață.** Scorul plasei scade cu 0,18 între minutul 10 și minutul 20 (pragul de zgomot:
  0,005). GPT-ul la plafon e însă mai bun (1,088 față de 1,302), cu de două ori mai mulți pași (4.949 față de 2.407).
- **Memoria video:** plasa 4,0 GB ocupată / 4,9–5,0 GB rezervată, sub 5,5 GB. GPT-ul la plafon 5,1 GB ocupată /
  5,4–5,6 GB rezervată: în rularea întreagă trece puțin de 5,5 GB rezervați (la proba de 20 de pași: 5,4); paznicul
  verifică memoria ocupată, deci n-a oprit nimic, iar viteza n-a scăzut.
- **Mutarea nodurilor**, pe 10 minute: urcarea ~84 s, coborârea gradienților ~163 s, optimizatorul din RAM ~197 s. Pe
  pas urcă toate nodurile active (34, apoi 38): în fiecare lot de 2.048 de simboluri apar cuvinte de pe toate rafturile.
- **Plasa:** n-a avut legături la început și nu s-a născut niciuna. Cea mai mare cerere a ajuns la 0,048, iar pragul de
  naștere e 0,05. Nodurile libere s-au alocat toate 6. După primele 10 minute: liber1 → noun.person (tim, tom, girl...),
  liber2 → adj.all (big, new, many...), liber3 → noun.artifact (ball, house, box...), liber4 → adv.all (very, too,
  back...). După 20 de minute: liber5 → liber1 (tim, friend, mia...) și liber6 → noun.person (mom, max, sue...). Rezerva
  e acum goală.

### Treapta 2: R2, TinyStories de 10× mai mult, 40 de minute (4 octombrie 2026)

Ambele modele continuă din starea de la finalul treptei 1; examenul pe validarea lui R2 (nevăzută).

| Minutul | Plasa mare | GPT la plafon | Plasa − GPT | Pași/s plasa / GPT | Mutarea nodurilor |
| --- | --- | --- | --- | --- | --- |
| 10 | 1,1592 | **0,9903** | +0,1689 | 1,8 / 4,1 | 77% |
| 20 | 1,0906 | **0,9333** | +0,1573 | 1,8 / 4,0 | 78% |
| 30 | 1,0539 | **0,8755** | +0,1784 | 1,8 / 4,0 | 78% |
| 40 | 1,0158 | **0,8302** | +0,1857 | 1,8 / 3,9 | 78% |

- **Verdict: NU, nu ține pasul.** La 40 de minute rămâne în urmă cu 0,186 (de 37 de ori pragul de zgomot), iar diferența
  nu se micșorează: GPT-ul face de 2,2 ori mai mulți pași (9.604 față de 4.280) și coboară mai repede.
- **Memoria video:** plasa 4,0 GB ocupată / 4,9–5,3 GB rezervată (sub 5,5 GB); GPT-ul 5,1 / 5,56–5,57 GB.
- **Mutarea nodurilor**, pe 10 minute: urcarea ~87 s, coborârea gradienților ~173 s, optimizatorul din RAM ~205 s:
  77–78% din timpul de antrenare. Pe pas urcă toate cele 40 de noduri; fiecare simbol calculează în medie 2,4 noduri.
- **Plasa:** 0 legături la început; s-au născut 4: noun.body → liber3 (după 10 minute), verb.communication →
  noun.communication și liber2 → noun.animal (după 20), liber2 → noun.attribute (după 30). Toate au fost folosite
  (folosire 0,045–0,09; 0,1 = deplină) și s-au întărit la fiecare examen, de la 0,10 la 0,33–0,56 (active): câștigul
  primit a fost mereu pozitiv, pentru că modelul se îmbunătățește oricum de la o bucată la alta, deci întărirea nu
  arată cât au ajutat ele. Nodurile libere: nicio alocare nouă (rezerva era goală), toate 6 au lucrat.

### Treapta 3: R3, Simple English Wikipedia, 60 de minute (4 octombrie 2026)

Ambele modele continuă din starea de la finalul treptei 2; examenul pe articole nevăzute. Un GPT de mărimea plasei (333 M)
nu încape pe placă; martorul de referință e cel mai mare GPT care încape (222 M).

| Minutul | Plasa mare | Scădere față de minutul de dinainte | GPT la plafon (referință) | Pași/s plasa / GPT | Mutarea nodurilor |
| --- | --- | --- | --- | --- | --- |
| 10 | 2,2938 | — | **1,9775** | 1,8 / 4,0 | 74% |
| 20 | 2,1227 | −0,1711 | **1,8295** | 1,8 / 4,0 | 73% |
| 30 | 2,0426 | −0,0801 | **1,7318** | 1,8 / 4,0 | 73% |
| 40 | 1,9803 | −0,0623 | **1,6787** | 1,8 / 4,0 | 73% |
| 50 | 1,9337 | −0,0466 | **1,6389** | 1,8 / 4,0 | 73% |
| 60 | 1,8992 | −0,0345 | **1,6018** | 1,4 / 4,0 | 71% |

- **Pe scor: DA, scade constant.** Scorul plasei scade la fiecare 10 minute, de fiecare dată peste pragul de zgomot
  (0,005), în total cu 0,395. Scăderile se micșorează (0,17 → 0,03), ca la orice antrenare.
- **Verdictul uneltei e totuși „NU”**, din cauza memoriei: în primele 10 minute, plasa a rezervat 5.506 MB, cu 6 MB peste
  5,5 GB (ocupată: 4,1 GB; paznicul, care verifică memoria ocupată, n-a oprit nimic, iar viteza n-a scăzut). În celelalte
  bucăți a rămas sub: 5.388–5.498 MB. Pe Wikipedia, mai puține cuvinte sunt umplutură (34% față de 44%), deci nodurile
  au cozi mai lungi și vârful de memorie urcă.
- **GPT-ul la plafon e mai bun la fiecare punct**, cu ~0,30 (1,602 față de 1,899 la final), cu de 2,3 ori mai mulți pași
  (14.472 față de 6.292).
- În ultima bucată, plasa a făcut doar 834 de pași (1,4 pe secundă, nu 1,8): și calculul de pe placă, și coborârea
  gradienților au mers mai încet, deci probabil placa a încetinit (căldură sau energie); cauza nu e sigură.
- **Plasa:** 4 legături la început (cele din R2), toate folosite; s-au născut încă 13, deci 17 la final, multe între
  animale, plante și mâncare (noun.animal → noun.food, noun.plant → noun.food, noun.food → noun.substance...). Tăria a
  crescut la fiecare examen (câștigul primit a fost mereu pozitiv): 6 au ajuns la 0,99 (definitive). Nodurile libere au
  rămas aceleași 6.

### Concluzia testului în trei trepte (sămânța 0)

| Treapta | Întrebarea | Răspunsul | Plasa la final | GPT la plafon la final |
| --- | --- | --- | --- | --- |
| R1, TinyStories, 20 min | funcționează și învață? | **DA** (−0,18 în 10 minute) | 1,3019 | 1,0880 |
| R2, TinyStories 10×, 40 min | ține pasul cu GPT-ul la limită? | **NU** (în urmă cu 0,186) | 1,0158 | 0,8302 |
| R3, Wikipedia, 60 min | scade scorul constant? | **DA pe scor**, dar memoria rezervată a trecut o dată de 5,5 GB cu 6 MB | 1,8992 | 1,6018 |

- Plasa mare (1,5× plafonul) **merge**: se antrenează cu nodurile în RAM, sub 5,5 GB aproape tot timpul, păstrează tot
  între trepte și învață pe trei texte diferite fără să pornească de la zero.
- Dar **pierde clar la timp egal** în toate trei treptele: face 1,8 pași pe secundă față de 4,0 ai GPT-ului, pentru că
  mutarea nodurilor între RAM și placă și optimizatorul din RAM iau 71–78% din timp (pe tot testul: urcarea ~17 minute,
  coborârea gradienților ~33 de minute, optimizatorul ~39 de minute, din 2 ore de antrenare). Capacitatea în plus (333 M
  față de 222 M) nu compensează pașii lipsă.
- O singură sămânță (0): pragul de 0,005 e singura măsură a zgomotului; o a doua sămânță ar cere încă ~4,5 ore.

**La pași egali, nu la timp egal.** Pentru fiecare treaptă, scorul final al plasei și scorul GPT-ului la cel mai apropiat
număr de pași, din fișele experimentelor. Se compară doar scoruri de pe același examen (din aceeași treaptă). Pașii se pot
număra în două feluri: toți pașii de până atunci, sau doar pașii pe textul treptei; în R2 și R3 cele două diferă, pentru
că cele două modele au ajuns la treaptă cu antrenamente diferite.

| Treapta | Plasa: pași (total / pe textul treptei) → scor | GPT la cel mai apropiat număr total de pași | GPT la cel mai apropiat număr de pași pe textul treptei |
| --- | --- | --- | --- |
| R1 | 2.407 / 2.407 → 1,3019 | 2.490 → **1,2560** (GPT mai bun cu 0,046) | la fel |
| R2 | 6.687 / 4.280 → 1,0158 | 7.421 (2.472 pe text) → **0,9903** (GPT mai bun cu 0,026) | 4.860 (9.809 total) → **0,9333** (GPT mai bun cu 0,083) |
| R3 | 12.979 / 6.292 → 1,8992 | 16.953 (doar 2.400 pe Wikipedia) → 1,9775 (**plasa** mai bună cu 0,078) | 7.228 (21.781 total) → **1,7318** (GPT mai bun cu 0,167) |

**Pe pas, plasa nu învață mai mult.** Comparația cea mai curată e R1: amândouă pornesc de la zero, pe același text, cu
pași aproape egali (2.407 față de 2.490), iar GPT-ul e mai bun cu 0,046 (de 9 ori pragul de zgomot). În R2, GPT-ul e mai
bun oricum s-ar număra pașii. În R3, răspunsul depinde de numărătoare: la pași totali apropiați plasa pare mai bună, dar
doar pentru că făcuse de 2,6 ori mai mulți pași pe Wikipedia; la pași apropiați pe Wikipedia, GPT-ul e mai bun cu 0,167
(dar ajunsese la R3 cu mai mult antrenament). Deci nicio dovadă că plasa învață mai mult pe pas, iar acolo unde
comparația e curată, învață mai puțin. **Direcția „plasa mare” se închide aici**; din ea rămâne folosit
`ModelGPTContinuu` (GPT-ul care continuă de unde a rămas).

```
python unelte/trepte_plasa_mare.py --trepte 3     # treapta 3 (~2 ore și 20 de minute)
```

## Bucla de auto-îmbunătățire pe GPT-ul simplu (4 octombrie 2026)

După închiderea plasei mari, bucla lui Kronos rulează pe GPT-ul simplu, **cu continuare**: cercetătorul schimbă rețeta,
iar modelul nu o ia de la zero la fiecare experiment, ci continuă să învețe de unde a rămas.

**Ce a rulat** (`config/laptop_bucla.toml`), 3 ore (16:01–19:06):

- **Date:** TinyStories de 10× (R2, 180 MB), pe bucăți de cuvinte (BPE). Examenul oficial e pe validarea lui R2
  (nevăzută), același ca în treapta 2 din M3.
- **Modelul la pornire:** GPT-ul simplu de ~52 M parametri (10 straturi × 640, context 256, lot 16, rata 0,0003).
  Fiecare experiment = 5 minute de antrenare.
- **Continuarea** (`ModelGPTContinuu`, cu setarea nouă `director_stari`): fiecare arhitectură (straturi, lățime, capete,
  context) are starea ei în `lucru/bucla/stari/`. O rețetă cu o arhitectură deja încercată continuă din cea mai bună
  stare a ei, cu lotul și rata noi; o arhitectură nouă pornește de la zero. Starea se scrie doar dacă scorul
  arhitecturii s-a îmbunătățit, deci un experiment stricat nu strică starea bună.
- **Cercetătorul nou** (`cercetator_local`):
  - întâi **lista**: fiecare valoare o dată, ca singură schimbare față de cea mai bună rețetă de atunci (straturi
    6/8/10/12/14, lățime 512/576/640/704/768, context 128/192/256/384/512, lot 8/12/16/24/32, rata
    0,0001/0,0002/0,0003/0,0005/0,0008);
  - când lista s-a epuizat, **strângerea** în jurul celor mai bune 3 rețete: la jumătatea drumului spre valorile vecine
    deja încercate, întâi golurile mari, până la pasul setării (un strat; 32 la lățime și context; 2 la lot; la rată,
    până la schimbări de 10%).
- La 16:11, după #155, am oprit bucla curat și am repornit-o, ca să intre o reparație a cercetătorului: strângerea sărea
  peste pașii mici la numere întregi, de exemplu un strat în plus. Niciun experiment nu s-a pierdut, pentru că Kronos a
  continuat din jurnal.

### Rezultatul

- **34 de experimente** (#154–#187), **13 păstrate**. Lista a ținut 20 de experimente (#155–#174), iar strângerea
  13 (#175–#187).
- **Cel mai bun scor: 0,5409** la #187: 10 straturi × 512, context 256, lot 30, rata 0,00035; 33,8 M parametri; 75 de
  minute de antrenare în spate, 40.770 de pași. La punctul de plecare era **1,2283**.
- Fără erori și fără experimente anulate. Memoria video: cel mult 4,3 GB rezervați (#169, lățimea 768 cu lot 32), sub
  5,5 GB. Paznicul a făcut 6 pauze de răcire de câte 2 minute: placa a ajuns la 86–87 °C, iar limita e 85 °C.
- Ce scrie cel mai bun model (`python -m kronos scrie --config config/laptop_bucla.toml --inceput "Once upon a time"`):
  > Once upon a time, there was a fearful crocodile in the big pond. He lived in a pond with his fish friends. One day,
  > he wanted to balance on a tree. He tried very hard, but he was too scared. The crocodile felt sad and baby, and he
  > wanted to make friends. He stayed still and watched the other animals playing. His friends saw him trying and
  > joined him. They all had a great time, […]

| # | Faza | Schimbarea | Rețeta (straturi×lățime · context · lot · rata) | Parametri | Pornire | Pași (simboluri văzute) | Minute în spate | val_bpb | Câștig | Decizie |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 154 | pornire | – | 10×640 · c256 · lot 16 · 0,0003 | 52,0 M | de la zero | 2.320 (9,5 M) | 5 | 1,2283 | – | **păstrat** |
| 155 | lista | lățime: 640 → 512 | 10×512 · c256 · lot 16 · 0,0003 | 33,8 M | de la zero | 3.160 (12,9 M) | 5 | 1,0869 | +0,1414 | **păstrat** |
| 156 | lista | rata: 0,0003 → 0,0001 | 10×512 · c256 · lot 16 · 0,0001 | 33,8 M | din starea cu 1,0869 | 3.183 (13,0 M) | 10 | 0,9059 | +0,1810 | **păstrat** |
| 157 | lista | rata: 0,0001 → 0,0008 | 10×512 · c256 · lot 16 · 0,0008 | 33,8 M | din starea cu 0,9059 | 3.248 (13,3 M) | 15 | 0,7955 | +0,1105 | **păstrat** |
| 158 | lista | rata: 0,0008 → 0,0002 | 10×512 · c256 · lot 16 · 0,0002 | 33,8 M | din starea cu 0,7955 | 3.239 (13,3 M) | 20 | 0,6849 | +0,1106 | **păstrat** |
| 159 | lista | rata: 0,0002 → 0,0005 | 10×512 · c256 · lot 16 · 0,0005 | 33,8 M | din starea cu 0,6849 | 3.216 (13,2 M) | 25 | 0,6779 | +0,0070 | **păstrat** |
| 160 | lista | lot: 16 → 8 | 10×512 · c256 · lot 8 · 0,0005 | 33,8 M | din starea cu 0,6779 | 5.463 (11,2 M) | 30 | 0,6663 | +0,0116 | **păstrat** |
| 161 | lista | lățime: 512 → 704 | 10×704 · c256 · lot 8 · 0,0005 | 62,6 M | de la zero | 3.238 (6,6 M) | 5 | 1,1755 | -0,5092 | respins |
| 162 | lista | straturi: 10 → 8 | 8×512 · c256 · lot 8 · 0,0005 | 27,4 M | de la zero | 6.671 (13,7 M) | 5 | 0,9415 | -0,2752 | respins |
| 163 | lista | lot: 8 → 32 | 10×512 · c256 · lot 32 · 0,0005 | 33,8 M | din starea cu 0,6663 | 1.859 (15,2 M) | 35 | 0,6090 | +0,0573 | **păstrat** |
| 164 | lista | lățime: 512 → 576 | 10×576 · c256 · lot 32 · 0,0005 | 42,4 M | de la zero | 1.415 (11,6 M) | 5 | 1,2249 | -0,6159 | respins |
| 165 | lista | context: 256 → 128 | 10×512 · c128 · lot 32 · 0,0005 | 33,7 M | de la zero | 3.349 (13,7 M) | 5 | 0,9758 | -0,3668 | respins |
| 166 | lista | context: 256 → 192 | 10×512 · c192 · lot 32 · 0,0005 | 33,7 M | de la zero | 2.290 (14,1 M) | 5 | 1,0904 | -0,4814 | respins |
| 167 | lista | lot: 32 → 12 | 10×512 · c256 · lot 12 · 0,0005 | 33,8 M | din starea cu 0,6090 | 3.992 (12,3 M) | 40 | 0,6215 | -0,0125 | respins |
| 168 | lista | straturi: 10 → 14 | 14×512 · c256 · lot 32 · 0,0005 | 46,4 M | de la zero | 1.320 (10,8 M) | 5 | 1,2182 | -0,6092 | respins |
| 169 | lista | lățime: 512 → 768 | 10×768 · c256 · lot 32 · 0,0005 | 74,2 M | de la zero | 947 (7,8 M) | 5 | 1,4298 | -0,8208 | respins |
| 170 | lista | straturi: 10 → 6 | 6×512 · c256 · lot 32 · 0,0005 | 21,1 M | de la zero | 2.774 (22,7 M) | 5 | 1,0491 | -0,4401 | respins |
| 171 | lista | context: 256 → 384 | 10×512 · c384 · lot 32 · 0,0005 | 33,8 M | de la zero | 1.205 (14,8 M) | 5 | 1,3634 | -0,7543 | respins |
| 172 | lista | lot: 32 → 24 | 10×512 · c256 · lot 24 · 0,0005 | 33,8 M | din starea cu 0,6090 | 2.242 (13,8 M) | 40 | 0,6039 | +0,0051 | **păstrat** |
| 173 | lista | straturi: 10 → 12 | 12×512 · c256 · lot 24 · 0,0005 | 40,1 M | de la zero | 1.874 (11,5 M) | 5 | 1,1539 | -0,5500 | respins |
| 174 | lista | context: 256 → 512 | 10×512 · c512 · lot 24 · 0,0005 | 33,9 M | de la zero | 1.117 (13,7 M) | 5 | 1,4181 | -0,8142 | respins |
| 175 | strângere | rata: 0,0005 → 0,00065 | 10×512 · c256 · lot 24 · 0,00065 | 33,8 M | din starea cu 0,6039 | 2.231 (13,7 M) | 45 | 0,6035 | +0,0004 | respins |
| 176 | strângere | context: 256 → 320 | 10×512 · c320 · lot 24 · 0,00065 | 33,8 M | de la zero | 1.837 (14,1 M) | 5 | 1,1572 | -0,5533 | respins |
| 177 | strângere | rata: 0,0005 → 0,0004 | 10×512 · c256 · lot 24 · 0,0004 | 33,8 M | din starea cu 0,6035 | 2.302 (14,1 M) | 50 | 0,5744 | +0,0295 | **păstrat** |
| 178 | strângere | lot: 24 → 20 | 10×512 · c256 · lot 20 · 0,0004 | 33,8 M | din starea cu 0,5744 | 2.651 (13,6 M) | 55 | 0,5705 | +0,0039 | respins |
| 179 | strângere | lot: 24 → 28 | 10×512 · c256 · lot 28 · 0,0004 | 33,8 M | din starea cu 0,5705 | 1.980 (14,2 M) | 60 | 0,5567 | +0,0177 | **păstrat** |
| 180 | strângere | rata: 0,0004 → 0,00035 | 10×512 · c256 · lot 28 · 0,00035 | 33,8 M | din starea cu 0,5567 | 1.976 (14,2 M) | 65 | 0,5496 | +0,0071 | **păstrat** |
| 181 | strângere | context: 256 → 224 | 10×512 · c224 · lot 28 · 0,00035 | 33,7 M | de la zero | 2.185 (13,7 M) | 5 | 1,1365 | -0,5870 | respins |
| 182 | strângere | context: 256 → 288 | 10×512 · c288 · lot 28 · 0,00035 | 33,8 M | de la zero | 1.707 (13,8 M) | 5 | 1,2352 | -0,6857 | respins |
| 183 | strângere | rata: 0,0004 → 0,00045 | 10×512 · c256 · lot 28 · 0,00045 | 33,8 M | din starea cu 0,5496 | 1.995 (14,3 M) | 70 | 0,5528 | -0,0033 | respins |
| 184 | strângere | straturi: 10 → 9 | 9×512 · c256 · lot 28 · 0,00035 | 30,6 M | de la zero | 2.273 (16,3 M) | 5 | 1,1410 | -0,5914 | respins |
| 185 | strângere | straturi: 10 → 11 | 11×512 · c256 · lot 28 · 0,00035 | 36,9 M | de la zero | 1.890 (13,5 M) | 5 | 1,1494 | -0,5998 | respins |
| 186 | strângere | lot: 28 → 26 | 10×512 · c256 · lot 26 · 0,00035 | 33,8 M | din starea cu 0,5496 | 2.119 (14,1 M) | 70 | 0,5449 | +0,0047 | respins |
| 187 | strângere | lot: 28 → 30 | 10×512 · c256 · lot 30 · 0,00035 | 33,8 M | din starea cu 0,5449 | 1.901 (14,6 M) | 75 | 0,5409 | +0,0087 | **păstrat** |

Cum se citesc coloanele:
- **Schimbarea:** e față de rețeta de bază a cercetătorului. În faza „lista”, baza e cea mai bună rețetă de atunci; în
  faza „strângere”, e rețeta în jurul căreia a căutat.
- **Pornire:** modelul a pornit de la zero sau din starea arhitecturii lui (cu scorul acelei stări).
- **Minute în spate:** toată antrenarea modelului până la examen, cu tot cu experimentele anterioare din care a
  continuat.
- **Câștig:** cât e mai bun decât cea mai bună rețetă de atunci (pozitiv = mai bun). Kronos păstrează doar câștigurile
  peste pragul de zgomot (0,005).

Raportul complet, cu tabelul pe setări și cele două comparații curate: `python unelte/raport_bucla.py`.

### Ce direcții au ajutat

1. **Continuarea însăși, de departe.** Același model (10 × 512) a învățat 75 de minute în 15 bucăți de câte 5 minute:
   1,0869 → 0,5409. Câștigul pe bucată scade: 0,18 la minutul 10, doar 0,004–0,005 la minutele 70–75.
2. **Un model mai mic, la început.** La 5 minute de la zero, cu același lot și aceeași rată, lățimea 512 bate lățimea
   640: 1,0869 față de 1,2283. Motivul: face cu 36% mai mulți pași (3.160 față de 2.320). E o comparație curată.
3. **Pe parcurs: rata mai mică și lotul mai mare**, adică pași cu mai puțin „zgomot”.
   - **Două comparații curate**, din aceeași stare și cu aceleași 5 minute:
     - din starea cu 0,6090: lot 24 → 0,6039, dar lot 12 → 0,6215 (mai slab decât la pornire);
     - din starea cu 0,5496: rata 0,00035 cu lot 26 → 0,5449, dar rata 0,00045 cu lot 28 → 0,5528 (tot mai slab decât
       la pornire).
   - **Pe drum, între minutele 30 și 60**, câștigurile mari au venit imediat după ce rata a scăzut sau lotul a crescut:
     lot 8 → 32: −0,057; rata 0,00065 → 0,0004: −0,029; lot 20 → 28: −0,014. Când rata a crescut (0,0005 → 0,00065),
     câștigul a fost aproape zero (−0,0004). La minutele 65–75, diferențele sunt cât pragul de zgomot și nu mai arată
     o direcție clară.
   - Rețeta finală are lot 30 și rata 0,00035. Asta face și un program de rată care scade pe parcurs; bucla l-a găsit
     „de mână”.
4. **Ce n-a ajutat, în 5 minute de la zero:** modelele mai mari sau cu context mai lung (14 straturi: 1,2182; lățimea
   768: 1,4298; contextul 384: 1,3634; contextul 512: 1,4181). La 5 minute câștigă cele care fac mai mulți pași: 8
   straturi cu lot 8 (0,9415) și contextul 128 (0,9758). Asta nu spune nimic despre cum s-ar fi descurcat ele în 75 de
   minute.

**Comparația cu M3, pe același examen R2:**
- GPT-ul la plafon (222 M parametri) a ajuns la 0,8302 după 40 de minute pe R2, plus 20 de minute pe R1 înainte.
- Modelul de 34 M din buclă avea 0,6039 după 40 de minute (#172) și 0,5409 după 75. Lotul și rata lui au fost schimbate
  pe drum de cercetător.
- În 40 de minute, modelul mic a văzut ~106 M de simboluri din R2, iar cel mare ~20 M.
- Concluzia: pe laptopul ăsta, la bugete de o oră, un model mai mic care vede mai mult text câștigă clar.

### Limita buclei cu continuare

Citește asta înainte de tabelul pe setări din raport:

- **Continuările câștigă aproape mereu, arhitecturile noi pierd mereu.**
  - Au fost păstrate 11 din 16 continuări, dar doar 1 din 17 rețete pornite de la zero. Aceea a fost #155, comparată
    cu punctul de plecare, care pornise tot de la zero.
  - O arhitectură nouă are 5 minute de antrenare, iar cea mai bună rețetă avea între 30 și 75. Nu poate câștiga, oricât
    de bună ar fi.
  - Așa s-au dus 16 din cele 33 de experimente, adică ~80 de minute.
- **Tabelul pe setări din raport amestecă efectul setării cu minutele în plus.** De exemplu, „rata ↓: 4 din 4
  păstrate”: fiecare dintre ele a fost o continuare cu încă 5 minute de antrenare. Dovezile curate sunt doar cele de la
  punctele 2 și 3 de mai sus.
- **Un amănunt:** starea unei arhitecturi se scrie ori de câte ori scorul ei se îmbunătățește, chiar și sub pragul de
  zgomot.
  - Experimentele #175, #178 și #186 au fost respinse de Kronos, dar starea lor a fost păstrată, iar experimentele
    următoare au continuat din ea.
  - Cele două experimente care au stricat modelul (#167, #183) au fost aruncate.

**Variante pentru pasul următor:**
1. **Căutare cinstită, apoi antrenare lungă.** Fiecare rețetă pornește de la zero, cu același timp și fără continuare,
   ca arhitecturile să fie comparate drept. Apoi rețeta câștigătoare se antrenează lung, cu continuare.
2. **O rată care scade singură în GPT**, de exemplu pe toată durata plănuită a antrenării. Bucla a găsit de mână că o
   rată mai mică spre final ajută; un program în model ar face asta automat, iar cercetătorul ar putea căuta altceva.

```
python -m kronos ruleaza --config config/laptop_bucla.toml --experimente 60   # bucla (oprire: python -m kronos opreste --config ...)
python unelte/raport_bucla.py                                                  # raportul: tabel, cel mai bun scor, direcții
python -m kronos scrie --config config/laptop_bucla.toml --inceput "Once upon a time"
```

## Toate comenzile

```
python -m kronos verifica      --config <fișier>   # se încarcă toate modulele?
python -m kronos ruleaza       --config <fișier> [--experimente N]
python -m kronos jurnal        --config <fișier>
python -m kronos scrie         --config <fișier> --inceput "text" [--lungime 300]
python -m kronos cauta <cuvânt> --config <fișier>  # unde stă cuvântul în memoria ierarhică
python -m kronos opreste       --config <fișier>
python -m kronos porneste      --config <fișier>
python -m kronos aproba-examen --config <fișier>   # doar după o schimbare făcută de tine în examen
```

## Ce urmează

- **N2–N3:** jurnal și paznic mai bogate (temperatură în fișă, panou cu grafic), examen de contract la înregistrare.
- **N4:** testele noastre proprii în examen; TinyStories.
- **N5:** cercetătorul cu Claude Code, care modifică direct codul modelului, pe ramuri Git.
- **Mai târziu:** WSL2 (Linux în Windows), necesar pentru Unsloth și `torch.compile`; pentru Etapa N1 nu e nevoie.
