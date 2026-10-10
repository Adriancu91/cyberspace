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
| model | `model_ngram` / `model_gpt` / `model_plasa` / `model_plasa_adaptiva` / `model_continuu` | n-gram pe caractere (fără GPU) / GPT mic de la 0 (pe GPU; opțional, rata care scade singură) / GPT cu 5 noduri și plasă (M2) / GPT cu un nod pe raft și noduri libere (M3) / GPT care continuă de unde a rămas (o stare pentru fiecare arhitectură, sau de la zero, sau din aceeași stare de pornire) |
| date | `date_mostra` / `date_fisier` / `date_tinystories` | propoziții generate / un fișier text (Shakespeare) / povești TinyStories (~20 MB) |
| examen | `examen_bpb` | val_bpb pe text nevăzut la antrenare |
| cercetător | `cercetator_aleator` / `cercetator_local` | schimbă câte o setare, pornind de la cea mai bună rețetă / întâi fiecare valoare din listă, apoi strânge căutarea în jurul celor mai bune 3 rețete |
| rulare | `rulare_locala` | laptopul: limită de timp, măsoară memoria video |
| stocare | `stocare_disc` | folderul `lucru/stocare` |
| interfață | `interfata_consola` | mesajele din terminal |
| memorie | `memorie_ierarhica` / `memorie_goala` | biblioteca de sensuri din WordNet (coduri, relații, plasă) / fără memorie |
| profesor | `profesor_gol` / `profesor_qwen` | gol (de jucărie) / Qwen3-4B-Instruct-2507 local, în 4 biți: scrie povești cu un fapt adevărat și le notează |
| traducere | module „de jucărie” | respectă contractul, devin reale în fazele următoare |

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

**Ce a rulat** (`config/laptop_bucla_v1.toml`, la început `config/laptop_bucla.toml`), 3 ore (16:01–19:06):

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
- Ce scrie cel mai bun model (`python -m kronos scrie --config config/laptop_bucla_v1.toml --inceput "Once upon a time"`):
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

Raportul complet, cu tabelul pe setări și cele două comparații curate: `python unelte/raport_bucla.py --config config/laptop_bucla_v1.toml`.

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
python -m kronos ruleaza --config config/laptop_bucla_v1.toml --experimente 60   # bucla (oprire: python -m kronos opreste --config ...)
python unelte/raport_bucla.py --config config/laptop_bucla_v1.toml               # raportul: tabel, cel mai bun scor, direcții
python -m kronos scrie --config config/laptop_bucla_v1.toml --inceput "Once upon a time"
```

## După prima buclă: rata care scade, bucla cinstită și antrenarea lungă

### Pasul 1: rata care scade singură (4 octombrie 2026)

**Ce e nou** (`module/model_gpt.py`): setarea opțională `rata_care_scade`, oprită implicit.
- Rata crește în linie dreaptă în primii 100 de pași ai modelului (încălzirea).
- Apoi scade în formă de cosinus până la 10% din rata de pornire, la finalul antrenării.
- Cu `durata_scaderii_secunde`, scăderea se întinde pe toată antrenarea plănuită a unui model care continuă (de exemplu
  8 ore, cu examen la fiecare oră), nu pe fiecare experiment.
- E pornită în `config/laptop_bucla.toml`.

**Testul** (`python unelte/compara_scaderea_ratei.py`): rețeta primei bucle (10 straturi × 512, context 256, lot 30), de
la zero, câte 5 minute, semințele 0 și 1. Aceeași sămânță înseamnă aceleași greutăți de pornire și aceleași bucăți de
text. Toate rulările au făcut ~2.000 de pași.

| Rata de învățare | Sămânța 0 | Sămânța 1 |
| --- | --- | --- |
| fixă 0,00035 (rețeta primei bucle) | 1,1656 | 1,1811 |
| care scade, de la 0,00035 | 1,2361 | 1,2315 |
| fixă 0,0007 | 1,0806 | 1,1187 |
| care scade, de la 0,0007 | **1,0474** | **1,0668** |

- **Cu aceeași rețetă ca prima buclă (0,00035), scăderea STRICĂ:** +0,071 și +0,051, de 10–14 ori pragul de zgomot.
  O rată care scade până la 10% are în medie doar ~55% din rata de pornire, iar 0,00035 e oricum mică pentru primele
  minute de la zero.
- **Cu rata de pornire dublă (0,0007), scăderea AJUTĂ:** față de rata fixă 0,0007, −0,033 și −0,052 (aceeași rețetă,
  la amândouă semințele). Față de vechea rețetă (fixă 0,00035), câștigul e −0,118 și −0,114.
- **De unde vine câștigul total de ~0,116:** cam două treimi din rata mai mare (fixă 0,0007 e cu ~0,074 mai bună decât
  fixă 0,00035) și cam o treime din forma scăderii (~0,043).
- **Ce folosim mai departe:** rata de pornire 0,0007, cu scădere, în bucla cinstită și în antrenarea lungă.

### Pasul 2: bucla cinstită (4 octombrie 2026, 20:32–21:32)

**Cum funcționează** (`python unelte/bucla_pe_faze.py --minute 60`): cele două feluri de comparații stau pe linii de
jurnal diferite, deci nu se amestecă în aceeași decizie.
- **Faza 1, arhitecturile** (`config/laptop_bucla.toml`, linia „bucla_arhitecturi”):
  - fiecare arhitectură pornește de la zero și are exact 10 minute, cu lot 30 și rata 0,0007 care scade;
  - cercetătorul (`cercetator_local`) schimbă câte o setare față de cea mai bună arhitectură de atunci, în ordinea din
    configurare, fără strângere.
- **Faza 2, lotul și rata** (`config/laptop_bucla_lot_rata.toml`):
  - starea arhitecturii câștigătoare se copiază o singură dată (`lucru/bucla_cinstita/stari_de_pornire/din_197.pt`);
  - fiecare experiment pornește din această copie și are 5 minute, cu rata care scade din nou, de la rata lui până la
    10%.

**Faza 1: care arhitectură câștigă la 10 minute** (de la zero, la timp egal):

| # | Arhitectura | Parametri | Pași în 10 minute | Simboluri văzute | val_bpb | Decizie |
| --- | --- | --- | --- | --- | --- | --- |
| 196 | 10 straturi × 512 (punctul de plecare) | 33,8 M | 3.906 | 30,0 M | 0,8245 | păstrat |
| 197 | **8 straturi × 512** | 27,4 M | 4.692 | 36,0 M | **0,8076** | **păstrat: câștigă** |
| 198 | 8 straturi × 640 | 42,2 M | 3.307 | 25,4 M | 0,9069 | respins |
| 199 | 12 straturi × 512 | 40,1 M | 3.243 | 24,9 M | 0,8647 | respins |

- **Câștigă 8 straturi × 512**, cu 0,017 mai bine decât 10 × 512. E mai mic și face cu 20% mai mulți pași în același
  timp.
- **Lățimea 640 pierde clar** (+0,099). A fost încercată pe 8 straturi, pentru că cercetătorul schimbă câte o setare
  față de cea mai bună de atunci.
- **12 straturi pierde clar** (+0,057).
- **De citit cu grijă: e o singură sămânță.** În pasul 1, aceeași rețetă cu sămânța 0 și cu sămânța 1 a dat scoruri
  care diferă cu 0,016–0,038, la 5 minute. Avantajul lui 8 straturi față de 10 (0,017) e de același ordin, deci nu e
  sigur. Pierderile lui 640 și 12 straturi sunt mult peste.
- **Efectul pasului 1:** în prima buclă, 10 × 512 avea după 10 minute de antrenare 0,9059 (rată fixă). Acum, cu rata
  0,0007 care scade, are 0,8245.
- Memoria video a fost cel mult 3,0 GB rezervați (12 straturi).

**Faza 2: lotul și rata**, toate din starea lui #197 (10 minute de antrenare, 0,8076), câte 5 minute:

| # | Lot | Rata de pornire | Pași | val_bpb | Decizie |
| --- | --- | --- | --- | --- | --- |
| 200 | 30 | 0,0007 (reperul: rețeta neschimbată) | 2.363 | 0,7317 | păstrat |
| 201 | 30 | 0,001 | 2.359 | 0,7226 | păstrat (−0,009) |
| 202 | **24** | **0,001** | 2.896 | **0,7167** | **păstrat (−0,006): câștigă** |

- **Rata mai mare (0,001) și lotul mai mic (24) au ajutat, dar puțin:** 0,006–0,009, aproape de pragul de zgomot
  (0,005).
- **Comparația e dreaptă:** toate trei pornesc din aceeași copie a stării, care a rămas neatinsă. Pașii lor totali sunt
  toți „4.692 + pașii proprii”.
- **Neîncercate**, pentru că s-a terminat ora: rata 0,0005 și lotul 36.
- Ora a avut 2 pauze de răcire, de câte 2 minute.

**Rețeta pentru antrenarea lungă:** 8 straturi × 512, context 256, lot 24, rata 0,001 care scade pe toate cele 8 ore
până la 0,0001. Pornește de la zero, ca scorul pe ore să arate tot drumul.

### Pasul 3: antrenarea lungă, peste noapte (4–5 octombrie 2026, 21:35–05:46)

**Ce a rulat** (`python unelte/antrenare_lunga.py --ore 8`, `config/laptop_antrenare_lunga.toml`):
- **Rețeta:** câștigătoarea buclei cinstite: 8 straturi × 512 (27,4 M parametri), context 256, lot 24.
- **Durata și datele:** de la zero, 8 ore pe TinyStories de 10× (R2).
- **Pe ore:** câte un experiment Kronos pe oră, cu examenul oficial la final și starea salvată după fiecare examen
  (`lucru/antrenare_lunga/gpt.pt`).
- **Rata:** a scăzut o singură dată, pe toate cele 8 ore, de la 0,001 (după încălzire) la 0,0001.
- **Între ore:** un minut de pauză, apoi răcire până la 70 °C.

| Ora | val_bpb | Față de ora dinainte | Pași în oră | Pași în total | Text văzut în total (simboluri) | De câte ori tot textul R2 | Rata la final |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 0,5850 | – | 33.908 | 33.908 | 208 M | 4,6 | 0,00097 |
| 2 | 0,5614 | −0,024 | 32.449 | 66.357 | 408 M | 9,0 | 0,00087 |
| 3 | 0,5447 | −0,017 | 33.399 | 99.756 | 613 M | 13,6 | 0,00072 |
| 4 | 0,5292 | −0,016 | 34.041 | 133.797 | 822 M | 18,2 | 0,00055 |
| 5 | 0,5162 | −0,013 | 34.147 | 167.944 | 1.032 M | 22,9 | 0,00038 |
| 6 | 0,5013 | −0,015 | 34.005 | 201.949 | 1.241 M | 27,5 | 0,00023 |
| 7 | 0,4922 | −0,009 | 34.247 | 236.196 | 1.451 M | 32,2 | 0,00013 |
| 8 | **0,4921** | −0,0001 | 34.270 | 270.466 | 1.662 M | 36,8 | 0,00010 |

- **Scorul final: 0,4921**, de la 0,5850 după prima oră. Față de cel mai bun model al primei bucle (0,5409, 10 × 512,
  75 de minute): −0,049.
- **Cât text a văzut:** 270.466 de pași × 24 × 256 = 1.662 M de simboluri, adică ≈ 6,6 miliarde de litere (~6,6 GB de
  text). Asta înseamnă de 36,8 ori tot textul de antrenare R2 (45,1 M de simboluri, 180 MB).
- **Ultima oră n-a mai adus nimic:** 0,4922 → 0,4921, sub pragul de zgomot, deci Kronos a respins-o.
  - Două explicații posibile, pe care testul nu le poate despărți: rata ajunsese la minim (0,0001), iar modelul văzuse
    textul de ~37 de ori.
  - Scorul nu a crescut, deci nu se vede o învățare pe de rost care să strice examenul.
- **Fără probleme:**
  - nicio eroare;
  - memoria video a rămas tot timpul la 1,9 GB rezervați, sub 5,5 GB;
  - viteza a fost de 9,0–9,5 pași pe secundă;
  - a fost o singură așteptare de răcire (înainte de ora 3, cu placa la 87 °C);
  - laptopul a rămas treaz.

**Povestea**, de la „Once upon a time”. A scris-o modelul de după ora 7: Kronos n-a salvat separat modelul orei 8,
fiindcă a fost respinsă, dar scorurile sunt practic egale (0,4922 față de 0,4921).

> Once upon a time, there was a fearful little dog named Coco. Coco was scared of everything. One day, Coco saw a big
> fireplace. The fireplace was in a room where fire could hold hugs. Coco wanted to help baby, but she was too scared to
> go near it. Coco saw a big dog named Max near the fireplace. Coco thought Max could help him, so she decided to shave
> him away. Max smiled at Coco and asked him to help. Coco was so happy that she could help Max. Together, Coco and Max
> worked together to keep the fireplace safe. The family and byvero saw that Tim and Coco were not fearful anymore. They
> were brave and knew that t[…]

Cinstit despre poveste:
- **Ce merge:** propozițiile sunt corecte, iar povestea are un fir (frică → un prieten → curaj).
- **Ce scapă încă:** greșeli de sens („fire could hold hugs”, „shave him away”), un cuvânt inventat („byvero”), un
  „Tim” apărut din senin și „el”/„ea” amestecate pentru același personaj.

**Propuneri pentru pasul următor:**
1. **Mai mult text, nu mai mult timp.** Modelul a văzut R2 de ~37 de ori și s-a oprit. Următorul pas firesc e
   TinyStories întreg (~2 GB, de vreo 10 ori mai mult decât R2), cu aceeași rețetă.
2. **O a doua sămânță pentru 8 față de 10 straturi.** La 10 minute, diferența a fost de ordinul zgomotului dintre
   semințe. Pe termen lung, modelul mai mare ar putea câștiga.

```
python unelte/antrenare_lunga.py --ore 8       # antrenarea lungă (oprire: python -m kronos opreste --config config/laptop_antrenare_lunga.toml)
python unelte/antrenare_lunga.py --raport      # tabelul pe ore și o poveste
```

## A doua antrenare lungă: mai mult text, nu mai mult timp (5 octombrie 2026)

### Pregătirea: TinyStories întreg, cu același examen

Comanda e `python unelte/pregateste_tinystories_tot.py`. Rulează o singură dată și a durat 10 minute.
- **Datele** stau în `date/tinystories_tot/`. E tot fișierul oficial de antrenare TinyStories V2 (GPT-4), de 2,23 GB,
  cu licență CDLA-Sharing-1.0: 2.717.493 de povești (2.226,7 MB de text), de ~12 ori mai mult decât R2.
- **Examenul e același.** Validarea e copia exactă, octet cu octet, a validării R2 (2.457 de povești, 2,0 MB). O face
  setarea nouă `validare_din` din `module/date_tinystories.py`. Așa scorurile se compară direct cu 0,4921.
- **Suprapunerile:** din antrenare se scoate orice poveste care apare identic în validarea R2. N-a fost niciuna.
  Potrivirea e exactă, deci povești doar asemănătoare nu se pot prinde așa.
- **Simbolurile** s-au împărțit o singură dată (201 secunde) și sunt ținute minte în `lucru/cache`: 558.283.756 de
  simboluri, adică 3,99 litere pe simbol.
- **Memoria:** simbolurile ocupă 1,12 GB, deci încap în RAM (64 GB) și nu trebuie citite pe bucăți. Împărțirea în
  simboluri se face totuși pe bucăți (`codifica_pe_bucati` în tokenizer), tăiate între povești, ca să nu se țină în
  memorie liste uriașe. Simbolurile ies exact aceleași ca dintr-o bucată.

### Antrenarea: 8 ore, din modelul orei 7

- **Pornirea:** din modelul orei 7 de aseară (experimentul 209, val_bpb 0,4922), cu `--porneste-din 209`.
  - Greutățile vin de la el.
  - Optimizatorul și numărătoarea pașilor pornesc din nou, deci rata repornește: încălzire în primii 100 de pași,
    apoi de la 0,0005 scade pe toate cele 8 ore până la 0,00005.
  - Ce făcuse modelul înainte (7 ore, pași, text văzut) se ține minte în `lucru/antrenare_lunga_2/pornire.json` și
    intră în totaluri.
- **Aceeași rețetă:** 8 straturi × 512, context 256, lot 24 (`config/laptop_antrenare_lunga_2.toml`).
- **Examen și salvare:** examen la fiecare oră, pe validarea R2, iar starea se salvează după fiecare oră
  (`lucru/antrenare_lunga_2/gpt.pt`).

**Rezultatul (07:47–15:56):**

| Ora | val_bpb | Față de ora dinainte | Pași în oră | Text văzut în aceste ore (simboluri) | De câte ori textul nou (TinyStories întreg) | Rata la final |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 0,5140 | +0,022 (față de pornire: 0,4922) | 34.690 | 213 M | 0,4 | 0,00048 |
| 2 | 0,5029 | −0,011 | 34.781 | 427 M | 0,8 | 0,00043 |
| 3 | 0,4942 | −0,009 | 35.216 | 643 M | 1,2 | 0,00036 |
| 4 | 0,4855 | −0,009 | 34.786 | 857 M | 1,5 | 0,00028 |
| 5 | 0,4700 | −0,016 | 34.293 | 1.068 M | 1,9 | 0,00019 |
| 6 | 0,4582 | −0,012 | 34.067 | 1.277 M | 2,3 | 0,00012 |
| 7 | 0,4482 | −0,010 | 34.148 | 1.487 M | 2,7 | 0,00007 |
| 8 | **0,4436** | −0,005 | 33.993 | 1.696 M | 3,0 | 0,00005 |

- **Scorul final: 0,4436.** Aseară a fost 0,4921, deci câștigul e −0,049, de ~10 ori pragul de zgomot. Examenul e
  același (validarea R2), deci comparația e directă.
- **Urcarea de la început:** la ora 1, scorul a urcat la 0,5140.
  - Rata a repornit la 0,0005, de 5 ori mai mare decât la finalul de aseară (0,0001), iar optimizatorul a pornit de
    la zero. Pașii mari „scutură” modelul.
  - Scorul a coborât sub cel de aseară abia la ora 4 (0,4855).
- **Ora 8:** a câștigat 0,0046, puțin sub pragul de zgomot (0,005), deci Kronos a respins-o și n-a salvat-o separat.
  - Starea de la final e totuși salvată (`lucru/antrenare_lunga_2/gpt.pt`), iar povestea de mai jos o scrie ea.
  - Spre deosebire de aseară, scorul încă scădea la final: textul nou nu s-a „terminat”.
- **De câte ori a văzut textul nou:** de 3,0 ori tot TinyStories întreg. Asta înseamnă 1.696 M de simboluri, ≈ 6,8
  miliarde de litere, în cele 8 ore. Aseară văzuse R2 de 36,8 ori.
- **În total, cu cele 7 ore de aseară:** 512.170 de pași și 3.147 M de simboluri (≈ 12,6 miliarde de litere).
- **Fără probleme:**
  - nicio eroare și nicio așteptare de răcire (pauza de un minut dintre ore a ajuns);
  - memoria video a rămas la 1,9 GB;
  - viteza a fost de 9,4–9,8 pași pe secundă;
  - RAM-ul folosit a fost de ~11,4 GB (textul întreg și simbolurile).

**Povestea, din același început** („Once upon a time, there was a fearful little dog named Coco”), scrisă de cele două
modele:

Azi, modelul de la final (ora 8, 0,4436):
> Once upon a time, there was a fearful little dog named Coco. Coco lived in a big house with a tall stadium. Coco was
> scared to climb the stadium because he saw so many people sitting and talking. Coco wanted to hold a friend, but he
> was too scared. One day, Coco saw a young boy in the stadium. The boy had a bright red hat. Coco thought the hat looked
> nice, so he handed the boy his hat. The boy laughed and said, "Thank you Coco,! Your hat is so funny!" Coco felt
> happy, but he still felt scared. He didn't want to hold a tie. The moral of the story is that Tim's hat is special
> because it helps you when you feel scared. You don't need a tie to be yourself[…]

Aseară, modelul orei 7 (experimentul 209, 0,4922):
> Once upon a time, there was a fearful little dog named Coco. He was scared of everything in the world, and he would
> run away! Coco ran to his friend, the kind old lady named Mrs. Brown. "Mrs. Brown, can you please be my dog? I am too
> scared," Coco refused to be scared, but he followed Chirpy out of her house. Mrs. Brown saw Coco didn't mean any harm.
> He just wanted to play with her. She stopped being scary and went to Coco. "Hey, little dog. Let's play!" she said.
> Coco was scared at first, but then she saw that Mrs. Brown was nice. She decided to be brave. Tim and Coco played
> together in the garden, and she wasn't so fearful anymore.

Cinstit despre povești:
- **Azi:**
  - Coco rămâne „el” de la un capăt la altul, iar cuvintele sunt mai variate (stadium, bright red hat).
  - Sensul încă scapă: o casă „cu un stadion înalt”, „hold a friend”, îi dă băiatului pălăria pe care o avea chiar
    băiatul, „hold a tie”, un „Tim” apărut din senin și o morală care nu decurge din poveste.
- **Aseară:**
  - Coco e când „el”, când „ea”, iar rolurile se amestecă („can you please be my dog?”, „She stopped being scary”).
  - „Chirpy” și „Tim” apar din senin.
- **O singură poveste e o singură mostră.** Modelul orei 7 de azi (0,4482) a scris, din același început, o poveste mai
  legată, despre Coco, o fetiță și un pui de pasăre (e în `lucru/antrenare_lunga_2.log`). Măsura cinstită rămâne
  scorul.

**Propuneri pentru pasul următor:**
1. **Încă o antrenare pe același text întreg.** Scorul încă scădea la final, iar textul a fost văzut doar de 3 ori.
2. **Un model mai mare pe textul întreg** (de exemplu 10 sau 12 straturi). Cu de 12 ori mai mult text, riscul de a
   învăța pe de rost e mai mic, deci un model mai mare ar putea acum să câștige.

```
python unelte/pregateste_tinystories_tot.py
python unelte/antrenare_lunga.py --config config/laptop_antrenare_lunga_2.toml --ore 8 --porneste-din 209 --compara-cu 209 --inceput "Once upon a time, there was a fearful little dog named Coco"
python unelte/antrenare_lunga.py --config config/laptop_antrenare_lunga_2.toml --raport --compara-cu 209 --inceput "Once upon a time, there was a fearful little dog named Coco"   # doar raportul
```

## A treia antrenare lungă: un model mai mare pe textul întreg (5–6 octombrie 2026, 22:45–06:55)

**Ce a rulat** (`config/laptop_antrenare_lunga_3.toml`):
- **Modelul:** 10 straturi × 512 (33,8 M parametri), de la zero, pe TinyStories întreg.
- **Rețeta:** cea din noaptea întâi: lot 24, rata 0,001 care scade pe toate cele 8 ore până la 0,0001.
- **Examen și salvare:** examen la fiecare oră pe validarea R2, starea salvată după fiecare oră.
- **Comparația dreaptă** e cu noaptea întâi: 8 × 512, de la zero, 8 ore, cu aceeași rețetă și același examen. Unealta
  pune scorul ei din aceeași oră alături (`--alaturi-de antrenare_lunga`).

| Ora | 10 × 512 (azi) | 8 × 512 (noaptea întâi) | Diferența | Pași în oră (10 × 512) | Text văzut (simboluri) | De câte ori textul întreg | Rata la final |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 0,5762 | 0,5850 | −0,009 | 27.708 | 170 M | 0,3 | 0,00097 |
| 2 | 0,5501 | 0,5614 | −0,011 | 27.678 | 340 M | 0,6 | 0,00087 |
| 3 | 0,5285 | 0,5447 | −0,016 | 27.647 | 510 M | 0,9 | 0,00072 |
| 4 | 0,5102 | 0,5292 | −0,019 | 27.705 | 680 M | 1,2 | 0,00055 |
| 5 | 0,4941 | 0,5162 | −0,022 | 27.589 | 850 M | 1,5 | 0,00038 |
| 6 | 0,4771 | 0,5013 | −0,024 | 27.682 | 1.020 M | 1,8 | 0,00023 |
| 7 | 0,4636 | 0,4922 | −0,029 | 27.713 | 1.190 M | 2,1 | 0,00013 |
| 8 | **0,4567** | 0,4921 | **−0,036** | 28.119 | 1.363 M | 2,4 | 0,00010 |

**Verdict: modelul mai mare câștigă.** La final, 10 × 512 e sub 0,4921 cu 0,0355, mai mult decât pragul de 0,02 (zgomotul
dintre semințe). După regula stabilită, îl continuăm mâine pe textul întreg.

Ce trebuie știut despre verdict:
- **A câștigat deși a văzut cu 18% mai puțin text.** E mai lent: 7,7 pași pe secundă față de 9,4, deci 221.841 de pași
  față de 270.466 în aceleași 8 ore.
- **Avantajul crește oră de oră**, de la −0,009 la −0,036. A trecut de prag la ora 5.
- **Comparația nu e perfect curată:** 8 × 512 a învățat pe R2, un text de 12 ori mai mic.
  - La ora 7, unde textul încă nu-l limitase, diferența e −0,029, tot peste prag.
  - La ora 8 crește la −0,036 și pentru că 8 × 512 se oprise atunci.
- **E o singură sămânță pentru fiecare model.** Pragul de 0,02 e tocmai pentru asta; diferența finală e de ~1,8 ori
  pragul.
- **Pentru context:** modelul 8 × 512 continuat ieri pe textul întreg are 0,4436, dar după 15 ore de antrenare, nu 8.
  Comparația aceea nu e dreaptă.

**Cât text a văzut în total:** 221.841 de pași și 1.363 M de simboluri (≈ 5,5 miliarde de litere), adică de 2,4 ori tot
TinyStories. Modelul a pornit de la zero, deci acesta e tot ce a văzut.

**Fără probleme:**
- nicio eroare și nicio așteptare de răcire;
- memoria video a rămas la 2,2 GB rezervați;
- viteza a fost de 7,7–7,8 pași pe secundă.

**Povestea, din același început.** Azi, 10 × 512 de la final (0,4567):
> Once upon a time, there was a fearful little dog named Coco. He was scared of everything in his town. One day, Coco
> found a big hole in the ground. He was very curious about the hole. Coco met a nice bird named Titi. Titi said,
> "Don't be scared, Coco. I can help you." She tied the rope to a tree to near a hill. Titi said, "Now, you can wash your
> hand when you are dirty." Coco went to wash his hand. When he was clean, he went back to the hole and saw a wheel. He
> turned the wheel and it made a funny noise. Titi laughed and said, "Surprise! Time for us!" Coco was not fearful
> anymore. He found out that the hole was just a magic hill behind his home. He ha[…]

Povestea modelului 8 × 512 din noaptea întâi (experimentul 209, 0,4922) e mai sus, la a doua antrenare lungă.

Cinstit despre poveste:
- **Ce merge:** Coco rămâne „el”, iar Titi e prezentată cum trebuie („a nice bird named Titi”) și rămâne „ea”. Dialogul
  e scris corect, iar povestea are un drum (frică → curiozitate → ajutor → curaj). Niciun personaj nu mai apare din
  senin.
- **Ce scapă încă:** „tied the rope to a tree to near a hill”, un câine care se spală „pe mână” și o groapă care se
  dovedește „un deal magic”.

```
python unelte/antrenare_lunga.py --config config/laptop_antrenare_lunga_3.toml --ore 8 --alaturi-de antrenare_lunga --compara-cu 209 --inceput "Once upon a time, there was a fearful little dog named Coco"
python unelte/antrenare_lunga.py --config config/laptop_antrenare_lunga_3.toml --raport --alaturi-de antrenare_lunga --compara-cu 209 --inceput "Once upon a time, there was a fearful little dog named Coco"   # doar raportul
```

## Faza 3, pasul 1: profesorul (6 octombrie 2026)

**Ce e:** `module/profesor_qwen.py`, pe portul „profesor”, trece testele de contract. E un model de limbaj mare care
rulează local: **Qwen3-4B-Instruct-2507** (Qwen, licență Apache 2.0, de pe Hugging Face), cuantizat la încărcare în 4
biți (NF4).

**Modelul:** Qwen2.5-3B-Instruct, cerut la început, are licența „qwen-research” (cercetare necomercială), nu Apache 2.0.
Am ales împreună Qwen3-4B-Instruct-2507: Apache 2.0, din aceeași familie, mai nou.

**Cum rulează: transformers + bitsandbytes în 4 biți, nu GGUF prin llama-cpp-python.**
- Pe Windows, llama-cpp-python nu are pe PyPI variante gata făcute, ci doar codul sursă. Acesta trebuie compilat cu
  Visual Studio, CMake și setul de unelte CUDA, pe care laptopul nu le are. Variantele gata făcute cu CUDA stau pe un
  site separat al proiectului, nu pe PyPI.
- transformers 5.18, accelerate 1.15 și bitsandbytes 0.50 vin gata făcute din PyPI. Folosesc PyTorch-ul cu CUDA pe care
  îl aveam deja, fără să-l schimbe.
- Instalarea: `pip install -e .[profesor]`. Modelul (~8 GB) se descarcă de pe Hugging Face la prima folosire.

**Ce face:**
- **`genereaza(subiect, stil)`** scrie o poveste scurtă în engleză simplă, ca în TinyStories, cu un fapt adevărat despre
  lume.
  - Lista de 50 de subiecte (`SUBIECTE`) are, pentru fiecare, faptul scris de noi, ca să fie sigur adevărat. Exemple:
    „Birds have feathers.”, „Water freezes into ice when it is very cold.”.
  - Stilurile: simplu, cu dialog, cu morală (sau un stil scris liber).
- **`noteaza(poveste)`** dă o notă de la 1 la 10 și un rând de motivare, pentru coerență, sens și gramatică. Nu folosește
  întâmplarea, deci aceeași poveste primește mereu aceeași notă.
- **`genereaza_exercitii(tema, numar)`** e cerința contractului portului.

### Testul de calitate (`python unelte/test_profesor.py`)

- **Viteza:**
  - scrie 31,6 povești pe minut, câte 8 deodată (82,9 simboluri pe secundă, ~111 cuvinte pe poveste);
  - dă 99 de note pe minut;
  - se încarcă în 12 secunde.
- **Memoria video:** 3,2 GB folosiți (3,6 GB rezervați), sub limita de 5,5 GB.
- **Notele pentru propriile 100 de povești** (50 de subiecte × 2 stiluri): 10 → 46, 9 → 41, 8 → 11, 7 → 2. Media e
  9,31.
- **Elevul față de TinyStories.** Elevul e 10 × 512, ora 8 de azi-noapte (#226). Ambele sunt notate pe aceleași 20 de
  povești din validarea R2, nevăzute la antrenare. Elevul pornește din prima propoziție a fiecăreia, iar povestea lui se
  taie la ultima propoziție întreagă.

| Cine a scris | Media notelor | Notele (nota → câte) |
| --- | --- | --- |
| Elevul (10 × 512) | **4,7** | 2 → 1, 3 → 5, 4 → 7, 5 → 1, 6 → 2, 7 → 2, 9 → 2 |
| TinyStories (poveștile originale) | **9,35** | 6 → 1, 8 → 2, 9 → 5, 10 → 12 |

**Prima măsură a elevului care nu e val_bpb:** 4,7 din 10, față de 9,35 pentru poveștile originale. Elevul scrie în
medie 125 de cuvinte, originalele 142.

**5 exemple din poveștile profesorului**, cu nota lui. Textele întregi sunt în `lucru/profesor/test_20261006_105259/`.
- *dogs (simplu), nota 8* („mici goluri de cauză și efect”):
  > Lily found a lost dog under a tree. The dog was shivering and sad. Lily sat next to it and whispered, "It's okay."
  > The dog sniffed her hand and wagged its tail. Lily noticed the dog could smell something sweet in the air. It
  > followed a trail of cookies to the park. […] Dogs have a very good sense of smell. They can find things people
  > can't see. […]
- *butterflies (dialog), nota 10*:
  > Lily saw a tiny caterpillar on a flower. "Is that a butterfly?" she asked. "No," said Tom. "It's just a
  > caterpillar." […] Tom smiled. "Yes, but it takes time. A caterpillar changes into a butterfly." […] "First, it eats.
  > Then it grows. Then it makes a chrysalis. Then it becomes a butterfly!"
- *snakes (dialog), nota 9*:
  > Lily saw a snake on the ground. "Wow!" she said. The snake slid slowly. "Is it scary?" asked Ben. […] Ben sat down.
  > "Snakes have no legs." […] "See?" said Ben. "It moves with its belly." Lily smiled. "It's not scary at all."
- *volcanoes (simplu), nota 9*:
  > A volcano sits on a mountain. It is quiet. Then, a big rumble. […] Hot melted rock called lava comes out of
  > volcanoes. It flows down the mountain like a river. […] The volcano is not scary. It is part of nature. […] Nature
  > is kind. Nature is strong. Nature is full of wonder.
- *snow (simplu), nota 7* („explicația despre cum se face zăpada pare nelalocul ei”):
  > Snow falls softly from the sky. […] Water freezes into ice when it is very cold. That is why the snow stays on the
  > ground. […] The snowman turns to water. The water flows down the hill. […]

**Elevul**, cea mai bună și cea mai slabă poveste:
- *nota 9*:
  > Once upon a time, there was a small house. A little cat lived in the house. […] The dog and the cat played with the
  > toy. They took turns. The cat was very happy. The dog was happy too. They became best friends.
- *nota 2* („evenimente fără legătură, cuvinte ca «warriage» și «knee-deine»”):
  > Once there was a boy and his dad. They were both very fearful. He had a big warriage. […] The boy set off for
  > knee-deine, which was his favorite wedding game. […]

### Ce trebuie știut despre note

- **Profesorul se notează generos pe sine.** Media pentru propriile povești e 9,31, cam cât pentru originale. Un model
  care își notează propriile texte are o părtinire cunoscută. Comparația curată e elevul față de originale: același
  profesor, aceeași cerere, texte pe care nu le-a scris el.
- **Scara e strânsă sus.** Aproape tot ce e bun ia 9–10, deci notele nu despart bine poveștile bune între ele. Despart
  însă clar elevul de originale.
- **„Sensul” e citit la propriu.** O poveste originală cu o fantezie (un dulap care se deschide spre cer) a luat 6.
- **Poveștile profesorului au încă scăpări.**
  - Faptul apare uneori de două ori, deși cererea spune „o dată”.
  - Mai apar fraze de umplutură („Nature is kind.”) și legături slabe (în povestea despre zăpadă).
- **Jurnalul are doar numere.** Fișa e pe linia „profesor” (#227): viteze, memorie, medii, distribuțiile notelor,
  fără niciun text generat. Textele, cu note și motive, sunt în `lucru/profesor/`.

```
pip install -e .[profesor]                      # transformers, accelerate, bitsandbytes (din PyPI)
python unelte/test_profesor.py                  # testul de calitate (~7 minute; prima dată descarcă modelul, ~8 GB)
python unelte/test_profesor.py --povesti 8 --elev 4   # probă scurtă
```

## Faza 3, pasul 2: hrana elevului și două examene noi (6 octombrie 2026)

### Hrana: povești cu fapte (`python unelte/genereaza_fapte.py`)

**Cum s-au scris:**
- Profesorul a scris 9.000 de povești în 4,0 ore: 37,5 pe minut, cu tot cu notatul.
- Fiecare poveste e pe unul din cele 50 de subiecte și are un singur fapt.
- Ca poveștile despre același fapt să nu semene între ele, se schimbă pe rând:
  - 8 stiluri: simplu, dialog, morală, o problemă rezolvată, o întrebare cu răspuns, doi prieteni, poveste de seară,
    amuzant;
  - 8 personaje principale (o fetiță, un băiețel, un cățel curios și altele).
- Fiecare poveste a fost notată pe loc.

**Ce a ieșit:**
- **Au rămas 7.520 de povești (84%)**, cu **860.410 cuvinte**.
- **Scoase:** 1.096 cu faptul repetat, cuvânt cu cuvânt, și 384 cu nota sub 8.
- **Notele, pentru toate cele 9.000:** 10 → 4.552, 9 → 3.147, 8 → 917, 7 → 180, 6 → 109, 5 → 36, 4 → 58, 3 → 1. Media
  e 9,28.
- **Pe fapt** au rămas între 74 și 178 de povești.
  - Faptele scurte sunt cele pe care profesorul le repetă cel mai des, deci au rămas cele mai puține: morcovii (74),
    păsările (76), merele (86), vacile (97).
  - Faptele lungi au păstrat aproape toate poveștile: toamna (178), curcubeul și umbrele (177).
- **Faptul spus altfel:** în 762 de povești rămase, faptul nu apare cuvânt cu cuvânt; de obicei e spus la trecut („lava
  came out of volcanoes”). Am scos doar ce ai cerut (nota sub 8 și faptul repetat), deci acestea au rămas, dar sunt
  numărate.

**Fișierele**, în `date/fapte/`:
- `povesti.txt`: poveștile rămase (4,8 MB de text), despărțite ca în TinyStories;
- `fapte.json`: lista fapt → povești;
- `toate.jsonl`: toate cele 9.000, cu notele și motivele.

**Ce am reglat pe drum:**
- **Cererea mai fermă.** Cererea a devenit „exact o dată, nici măcar la final”. La proba de 32 de povești, 34% repetau
  faptul; după schimbare, 16%. Pe toată rularea, 12%.
- **Memoria video.**
  - Rularea a pornit cu loturi de 16, care la probă ocupau 4,3 GB.
  - Memoria rezervată de PyTorch a crescut însă de la un lot la altul, pentru că loturile au lungimi diferite. A ajuns
    la 5,9 GB (văzut în contoarele Windows), peste limita de 5,5 GB.
  - Am oprit generarea curat, imediat după ce a scris o bucată pe disc (la povestea 4.672). Am pus profesorul să dea
    memoria înapoi după fiecare lot, apoi am repornit generarea de unde rămăsese.
  - De atunci a ocupat 3,6 GB între loturi și cel mult 4,2 GB (vârful măsurat de PyTorch), fără să scadă viteza.

### Examenul de fapte (`python unelte/examen_fapte.py`)

**Ce e:** un examen separat de cel oficial (val_bpb), pe care nu-l atinge. Pentru fiecare din cele 50 de fapte sunt 3
propoziții cu golul la capăt, ca elevul să-l poată completa scriind de la stânga la dreapta:
- faptul însuși: „Birds have ___.”;
- spus de mama: „Mom said, "Birds have ___."”;
- învățat de Lily: „Lily learned that birds have ___.”.

**Cum se notează:**
- Elevul completează fără întâmplare: metoda nouă `ModelGPT.completeaza` alege la fiecare pas simbolul cel mai probabil.
- Răspunsul e corect dacă primul cuvânt (după un „the/a/an”) e cuvântul din fapt.
- Separat, se numără și răspunsurile cu câteva sinonime la fel de adevărate (de exemplu „clean” la dinți, „metal” la
  magneți).

**Punctul de plecare: 10 × 512 de azi-noapte (#226).**
- **41 din 150 (27%)** cu cuvântul din fapt; 50 din 150 (33%) cu sinonime.
- 24 din 50 de fapte au măcar un răspuns corect.
- Pe propoziții (din câte 50): faptul însuși 13, spus de mama 14, învățat de Lily 23.

**Nu e aproape de zero, cum ne așteptam.**
- Elevul știe faptele care apar și în poveștile TinyStories: plantele au nevoie de apă și soare ca să crească,
  păianjenii au opt picioare, omida devine fluture, vacile dau lapte, găinile fac ouă.
- Nu știe faptele mai „de carte”. Răspunsurile lui: „Water freezes into the air”, „Birds have a nest”, „The Sun is a
  special thing”, „The Moon goes around the room”, „Fish breathe through their breath”, „Frogs start their lives as they
  are”.
- Măsura are loc să crească: 73% din răspunsuri sunt greșite, iar golurile sunt exact faptele din hrana de mai sus.

### Examenul profesorului (`python unelte/examen_profesor.py`)

**Ce face:** dă nota profesorului pe aceleași 20 de povești nevăzute (aceeași sămânță ca la testul profesorului), pentru
orice model salvat.
- Modelul se alege cu `--experiment <nr.>` sau cu `--linie <linie>` (ultimul model salvat de pe ea).
- Elevul pornește din prima propoziție a fiecărei povești, iar profesorul notează fără întâmplare.

**Se repetă exact.** Pe modelul de azi-noapte (#226) dă din nou **4,7**, cu aceleași 20 de povești și aceleași 20 de
note ca la testul de ieri. Deci se poate folosi pe modelele de acum înainte.

### În jurnal, doar numere

Fișele noi nu conțin niciun text generat:
- #228 și #229: examenul de fapte (a doua are și numărul fără sinonime);
- #230: hrana (9.000 de povești scrise, 7.520 rămase);
- #231: examenul profesorului (4,7).

```
python unelte/genereaza_fapte.py --doar-local                 # 9.000 de povești sau 5 ore (se poate relua)
python unelte/examen_fapte.py --experiment 226 --dispozitiv cpu
python unelte/examen_profesor.py --experiment 226            # sau --linie antrenare_lunga_3
```

## Regula 4: nou ≠ mai bun — criterii suplimentare la decizie (6 octombrie 2026)

O schimbare în `kronos/`, aprobată explicit de Adrian.

**Ce face.** Până acum, Kronos păstra un experiment doar după scorul examenului oficial (val_bpb). Acum, pe lângă el, un
experiment poate aduce **criterii** suplimentare: numere cu nume, de exemplu `fapte_corecte` și `nota_profesor`.

**Configurarea.** În secțiunea `[criterii]` se scrie, pentru fiecare criteriu, direcția și cât are voie să scadă, cel
mult, față de cel mai bun experiment păstrat:

```toml
[criterii.fapte_corecte]
mai_mare_e_mai_bine = true
prag = 3          # cât poate scădea, cel mult, față de cel mai bun experiment păstrat

[criterii.nota_profesor]
mai_mare_e_mai_bine = true
prag = 0.5
```

**Decizia.**
- Un experiment e **păstrat** doar dacă val_bpb e mai bun **și** niciun criteriu n-a scăzut mai mult decât pragul lui.
- Dacă val_bpb e mai bun, dar un criteriu a căzut, experimentul e **respins**. Motivul e de forma „a pierdut
  fapte_corecte: 5 față de 10 la #12 (a scăzut cu 5, pragul e 2)” și apare și pe ecran.
- Decizia rămâne scrisă „respins”, iar „a pierdut…” stă în motiv, ca uneltele care citesc jurnalul să meargă mai
  departe (ele recunosc doar „păstrat”, „respins” și „anulat”).

**Ordinea.**
- Cu `[criterii]`, modelul dă criteriile prin ușa existentă, `dupa_examen`, chemată acum **înainte** de decizie.
  Modelul primește decizia pe care ar lua-o val_bpb singur.
- **Fără `[criterii]`, totul e exact ca înainte:** aceeași ordine și aceeași decizie. Testele vechi trec neschimbate.

**Amănunte:**
- Contează doar numerele; orice altceva primit de la model se lasă deoparte.
- Un criteriu configurat pe care modelul nu-l dă se notează în `criterii_lipsa` și nu oprește nimic.
- Un criteriu pe care cel mai bun experiment păstrat nu-l are nu se poate compara.
- La reluare, referința se citește din jurnal.

**Partea din module.** GPT-ul (`model_gpt`, `model_continuu`) are setarea opțională `examene_suplimentare = ["fapte",
"profesor"]`. După examenul oficial, care nu s-a schimbat, `dupa_examen` întoarce doar numere:
- **`fapte_corecte`**: examenul de fapte, doar cu cuvântul din fapt. Vin și `fapte_corecte_cu_sinonime` și
  `fapte_stiute`.
- **`nota_profesor`**: media notelor profesorului pe aceleași 20 de povești nevăzute, din `validare_examene` (implicit,
  validarea R2).

Alte lucruri de știut:
- **Unde stă codul.** Nucleul celor două examene s-a mutat în `module/examene_elev.py`, ca să-l poată folosi și GPT-ul.
  Uneltele îl folosesc la fel ca înainte.
- **GPT-ul simplu fără setare** nu are `dupa_examen`, deci fișele lui rămân neschimbate.
- **GPT-ul care continuă** salvează întâi starea, apoi rulează examenele suplimentare. Așa, o eroare într-un examen nu
  poate pierde antrenamentul.

**Costul pe experiment:**
- examenul de fapte: câteva secunde;
- examenul profesorului: ~1 minut (încărcarea profesorului, 20 de povești, notele);
- memoria video: elevul și profesorul împreună încap sub 5,5 GB.

**Teste: 327, toate trec.**
- 11 sunt noi pentru regulă:
  - un criteriu care cade → respins, deși val_bpb e mai bun;
  - un criteriu stabil sau exact la prag → păstrat;
  - referința e cel mai bun experiment păstrat, și după reluare;
  - direcția inversă (mai mic e mai bine);
  - criterii lipsă;
  - configurări greșite;
  - motivul apare pe ecran;
  - fără `[criterii]`, totul e ca înainte.
- 5 sunt noi pentru partea din module.
- `test_arhitectura` trece: `kronos/` nu importă nimic din `module/`.

### Criteriul principal (7 octombrie 2026, aprobat de Adrian)

În `[criterii]`, un criteriu poate fi marcat `principal = true`, cel mult unul. Fără el, val_bpb rămâne principalul și
totul e exact ca înainte.

```toml
[criterii.fapte_corecte]
mai_mare_e_mai_bine = true
prag = 10
principal = true    # el hotărăște

[criterii.nota_profesor]
mai_mare_e_mai_bine = true
prag = 0.5
```

**Decizia, cu un criteriu principal.** Experimentul e păstrat doar dacă:
- principalul e mai bun cu **peste** pragul lui;
- **și** niciun alt criteriu nu scade peste pragul lui. Asta include val_bpb, al cărui prag e `prag_zgomot` (0,005).

Motivele de respingere:
- „criteriul principal fapte_corecte: 30 față de 25 la #12 (câștig +5, trebuie peste 10)”;
- sau „a pierdut val_bpb: …”, ori „a pierdut nota_profesor: …”.

**Referința** e cel mai bun experiment păstrat după criteriul principal, și la reluarea din jurnal. Primul experiment
al unei linii e păstrat, ca înainte.

**Teste:** 8 noi (`teste/test_criteriu_principal.py`). Cele vechi ale regulii 4 trec neschimbate.

## A patra antrenare lungă: martorul, cu toate trei examenele la fiecare oră (6–7 octombrie 2026, 17:27–01:43)

**Ce a rulat** (`config/laptop_antrenare_lunga_4.toml`):
- **Modelul:** 10 × 512 de la sfârșitul nopții a treia (experimentul #226), continuat 8 ore pe TinyStories întreg.
  Fără poveștile cu fapte: noaptea asta e **martorul**.
- **Rețeta:** lot 24. Rata repornește la 0,0005 (optimizatorul pornește din nou, cu 100 de pași de încălzire), apoi
  scade pe toate cele 8 ore până la 0,00005.
- **La fiecare oră:**
  - examenul oficial (val_bpb pe validarea R2);
  - apoi cele două examene suplimentare: faptele și nota profesorului, pe aceleași 20 de povești nevăzute;
  - salvarea modelului.

  Setarea `examene_suplimentare` a fost pornită fără `[criterii]`: s-a măsurat, dar nu s-a respins nimic pentru ele.

| Ora | Experimentul | val_bpb | Fapte corecte (din 150) | Nota profesorului | Rata la final |
| --- | --- | --- | --- | --- | --- |
| 0 (plecarea) | #226 | 0,4567 | 41 | 4,7 | – |
| 1 | #232 | 0,5048 | 27 | 3,55 ± 0,37 | 0,00048 |
| 2 | #233 | 0,4976 | 27 | 3,55 ± 0,26 | 0,00043 |
| 3 | #234 | 0,4880 | 28 | 3,75 ± 0,36 | 0,00036 |
| 4 | #235 | 0,4769 | 31 | 3,9 ± 0,34 | 0,00028 |
| 5 | #236 | 0,4667 | 27 | 3,8 ± 0,31 | 0,00019 |
| 6 | #237 | 0,4534 | 40 | 3,9 ± 0,31 | 0,00012 |
| 7 | #238 | 0,4453 | 38 | 4,2 ± 0,38 | 0,00007 |
| 8 | #239 | **0,4389** | **51** | **4,5 ± 0,49** | 0,00005 |

Cum se citește tabelul:
- „± …” e cât poate varia nota doar din întâmplare (eroarea standard a mediei celor 20 de note).
- Plecarea (#226) e măsurată cu aceleași examene, pe același model.
- Fiecare oră a avut ~27.000 de pași (7,4–7,6 pe secundă).

**Concluzia cinstită: nota profesorului urcă odată cu val_bpb? Da, pe ansamblu, dar e o măsură grosieră.**
- **Legătura e puternică.**
  - Pe cele 9 puncte (plecarea + 8 ore), legătura dintre val_bpb și notă e −0,80; doar pe cele 8 ore, −0,91.
  - Cu cât val_bpb e mai mic, cu atât nota e mai mare: în medie, +0,14 puncte pentru fiecare 0,01 în minus la
    val_bpb.
- **Cel mai convingător e începutul.**
  - La repornirea ratei, val_bpb s-a stricat (0,4567 → 0,5048), iar nota a căzut odată cu el (4,7 → 3,55), la fel ca
    faptele (41 → 27).
  - Apoi au urcat toate trei împreună.
  - Deci nota nu urcă doar „cu timpul”: când val_bpb a dat înapoi, a dat și ea.
- **Dar nota e grosieră.** O măsurare are o eroare de ±0,26–0,49, pentru că sunt doar 20 de povești. Vede deci doar
  schimbări mari de val_bpb, de ordinul 0,03–0,05. De la o oră la alta, val_bpb s-a schimbat cu 0,006–0,013, iar nota
  a stat pe loc sau s-a mișcat cu 0,1–0,3, adică în zgomot.
- **La final, nota nu poate confirma câștigul mic.**
  - val_bpb e mai bun decât la plecare cu 0,018, sub pragul de 0,02.
  - Nota e 4,5, față de 4,7 la plecare.
  - Nota nu poate deosebi diferența asta de zgomot, nici într-un sens, nici în celălalt.
- **De urmărit, nedovedit.** Modelul de plecare (#226) a luat o notă mai mare decât ar „prezice” val_bpb-ul lui
  (4,7 față de ~4,2). Era, ca și ora 8, la capătul scăderii ratei. Poate că modelele „răcite” la final scriu puțin mai
  bine decât arată val_bpb, dar cu 20 de povești nu se poate spune.

**Faptele urcă și ele odată cu val_bpb.**
- Legătura e −0,85: de la 27 la 51, peste plecare (41).
- Dar sar mult de la o oră la alta: 27 → 40 → 38 → 51, de două ori cu +13 într-o singură oră.
- Pentru CONTINUUM, asta înseamnă că pragul de zgomot de 3 fapte din plan e prea mic. După noaptea asta, o
  diferență sub ~10 între două modele poate fi întâmplare.

**Martorul e gata.** La final, modelul fără povești cu fapte are 0,4389, 51 de fapte și nota 4,5. Cu el se compară
noaptea cu poveștile profesorului.

**Scorul se compară cu 0,4436.** 0,4389 e cel mai mic val_bpb de până acum pe validarea R2. Recordul de dinainte,
0,4436, era al modelului 8 × 512, după 15 ore. Diferența e de 0,005, sub pragul de 0,02, deci scorurile sunt
comparabile, nu unul clar mai bun.

**Cât text a văzut:**
- în noaptea asta: 215.865 de pași și 1.326 M de simboluri (≈ 5,3 miliarde de litere), adică de 2,4 ori tot
  TinyStories;
- împreună cu noaptea a treia, din care a pornit: 437.706 de pași și 2.689 M de simboluri (≈ 10,8 miliarde de
  litere), adică de 4,8 ori tot textul.

**Fără probleme:**
- nicio eroare și nicio așteptare de răcire;
- toate cele 8 ore păstrate;
- memoria rezervată la antrenare: 2,2 GB;
- fiecare oră a durat ~61 de minute, cu examenele.

**Povestea, din același început.** Modelul de la final (ora 8, #239, 0,4389):
> Once upon a time, there was a fearful little dog named Coco. Coco was fearful of big things. One day, Coco saw a big
> red ball. He wanted to play with it. He looked at the ball and felt scared. Coco saw a friend, a cat named Fluffy.
> Coco said, "Fluffy, do you want to play with the big red ball?" Fluffy said, "Yes, Coco! Let's play together!" They
> played with the big red ball all day. They were very happy. But then, something unexpected happened. The big red ball
> popped! Coco and Fluffy were sad. They thought the popped ball would not be fun anymore. But they were still happy
> and decided to play together. Tim said, "Coco, use your brain to think and sol[…]

Povestea modelului de plecare (#226) e mai sus, la a treia antrenare lungă.

Cinstit despre poveste:
- **Ce merge:**
  - Coco rămâne „el”, iar prietenul e prezentat cum trebuie („a cat named Fluffy”);
  - dialogul e scris corect;
  - povestea are o întorsătură („The big red ball popped!”) și un sfârșit cu sentimente.
- **Ce scapă:**
  - „Tim” apare din senin;
  - frica lui Coco dispare fără motiv: se joacă toată ziua cu mingea de care se speria;
  - povestea e mai simplă decât cea de plecare.
- **Ce spune profesorul:** o vede la fel, cu nota medie 4,5 față de 4,7.

```
python unelte/antrenare_lunga.py --config config/laptop_antrenare_lunga_4.toml --ore 8 --porneste-din 226 --compara-cu 226 --inceput "Once upon a time, there was a fearful little dog named Coco"
python unelte/antrenare_lunga.py --config config/laptop_antrenare_lunga_4.toml --raport --compara-cu 226 --inceput "Once upon a time, there was a fearful little dog named Coco"   # doar raportul
```

## CONTINUUM v0: ritmul zilei (7 octombrie 2026)

Planul e în `docs/CONTINUUM_plan.md`, adus din ramura `claude-continuum`. Aici e construit doar **v0** (secțiunile 13
și 15 din plan).

**Ce face.** CONTINUUM decide ce face Kronos când nimeni nu-i spune. Nu antrenează și nu dă examene singur. La fiecare
ciclu:
1. se uită în jur;
2. alege **o singură nevoie**;
3. dacă e voie, cere lui Kronos un experiment, cu o configurare existentă, sau pornește o unealtă de examene;
4. citește fișa din jurnalul Kronos și notează ce a ieșit.

Nu atinge `kronos/`, examenul oficial, jurnalul Kronos sau `date/`. Ce ține minte stă în `lucru/continuum/`.

### Cum îl pornești, îl oprești și îl citești

```
python -m module.continuum.bucla --config config/continuum.toml --simuleaza   # doar spune ce ar alege și de ce
python -m module.continuum.bucla --config config/continuum.toml               # pornește și experimentele
python -m module.continuum.bucla --config config/continuum.toml --jurnal      # ultimele 20 de cicluri, pe scurt
python -m module.continuum.bucla --config config/continuum.toml --simuleaza --pauza-minute 15   # o zi, un ciclu la 15 min
python -m module.continuum.bucla --config config/continuum.toml --simuleaza --ca-la 23:00       # ce ar alege la noapte
python -m kronos opreste  --config config/proba.toml    # oprirea: același buton STOP ca la Kronos (lucru/STOP)
python -m kronos porneste --config config/proba.toml    # ca să poată porni din nou
```

- **Modul simulat** (`--simuleaza`): face tot ciclul, dar nu pornește nimic. Doar scrie ce ar fi pornit și de ce
  („[simulat] Aș porni: …”). Așa se testează prima zi.
- **Oprirea:**
  - STOP-ul se verifică la începutul fiecărui ciclu, înainte de acțiune și, în pauze, la câteva secunde.
  - O antrenare pornită de CONTINUUM vede și ea STOP-ul și se oprește după ora în curs, ca de obicei.
- **Jurnalul ciclurilor:** `lucru/continuum/cicluri.jsonl`, un rând pe ciclu.
  - Câmpul `pe_scurt` spune ciclul în una-două propoziții, în română; `--jurnal` le arată pe ultimele.
  - Restul rândului are amănuntele: ce a observat, nivelul și de ce, nevoile, ce a sărit și de ce, ce a ales,
    comanda, verdictul.
- **Memoria:** `lucru/continuum/stare.json`. Ține:
  - capacitățile, cu liniile lor de bază;
  - strategiile și experimentele cerute (cu modelul de dinainte, de unde se poate reveni);
  - problemele, deschise sau rezolvate.

### Ce face un ciclu

OBSERVĂ → EVALUEAZĂ → NEVOI → ALEGE → ACȚIONEAZĂ → MĂSOARĂ → ÎNVAȚĂ → STARE. Fiecare etapă e în fișierul ei din
`module/continuum/`, plus guvernatorul (`guvernator.py`) și bucla (`bucla.py`).

**Ce observă:**
- jurnalul Kronos, doar citit, și butonul STOP;
- placa video: temperatura, memoria și ce programe o folosesc;
- dacă omul a atins tastatura sau mouse-ul, și ora;
- modulele din `[module]`, descoperite la pornire și la fiecare 6 cicluri;
- hrana din `date/fapte` și configurările de antrenare.

**Nivelul, dat de guvernator:**
- **REPAUS:** doar observă. Se ajunge aici dacă:
  - omul a folosit laptopul în ultimele 10 minute;
  - placa e ocupată (un program Python pe ea, sau sub 4.500 MB liberi) ori nu poate fi citită;
  - ora e în afara ferestrelor.
- **ÎNTREȚINERE:** ziua (07:00–22:00), cu placa liberă: examene și hrană de la profesor, fără antrenări.
- **ÎNVĂȚARE:** noaptea (22:00–07:00), cu placa liberă: și antrenări lungi.
- Placa peste 85 °C coboară un nivel.

**Capacitățile:**
- povestirile: val_bpb;
- faptele: fapte_noi, din 150 (examenul de fapte nou, reformulat; până pe 7 octombrie, fapte_corecte);
- sensul: nota profesorului, din 10.

Linia de bază e cea mai bună valoare dintre experimentele **păstrate** de Kronos în antrenările lungi. Toate dau
examenul pe validarea R2, deci se pot compara.

**Cele trei nevoi, în ordinea urgenței** (din 7 octombrie, „dezvolta” vine înaintea lui „continua”):
1. **masoara:** ultimul model păstrat n-a dat examenele de fapte sau al profesorului. CONTINUUM le dă, cu
   `unelte/examen_fapte.py` și `unelte/examen_profesor.py` (pe 40 de povești).
2. **dezvolta**, pentru cea mai slabă capacitate (cel mai mic procent din maxim; azi, faptele):
   - noaptea: antrenare pe hrana ei, cu o configurare `config/laptop_fapte*.toml` care pomenește `date/fapte`;
   - ziua: hrană nouă de la profesor, dar doar dacă hrana nefolosită s-a terminat (e sub 5.000 de povești sau a fost
     folosită deja).
3. **continua:** val_bpb a coborât în ultima oră cu cel puțin 0,005, sau ultima antrenare lungă e neterminată.
   CONTINUUM pornește o antrenare lungă cu o configurare `config/laptop_antrenare_lunga*.toml` existentă și
   neterminată.

De ce „dezvolta” înaintea lui „continua”: planul definește ÎNVĂȚAREA ca „hrană nouă sau un model neterminat”, cu
hrana nouă întâi. Cu ordinea veche, CONTINUUM ar fi ales continuarea simplă (val_bpb încă scade), deși
`laptop_antrenare_lunga_5.toml` trebuie să vină abia după fapte.

**Verdictul (MĂSOARĂ):** SUCCES, EȘEC sau NECONCLUDENT.
- Contează pragul de zgomot al fiecărei capacități: 0,005 la val_bpb, 10 fapte, 0,5 la notă (alese de Adrian
  pe 7 octombrie).
- Se aplică și regula 4: un câștig care pierde altă capacitate e EȘEC.

**Ce învață (ÎNVAȚĂ):** fiecare strategie are o încredere. Pornește de la 0,5 și se schimbă cu ±0,1 la SUCCES sau
EȘEC. În v0 doar se ține minte.

Toate pragurile, ferestrele și comenzile sunt în `config/continuum.toml`, nu în cod.

### Ce trebuie știut, cinstit

- **Nu creează configurări.** Pentru o noapte nouă, configurarea (de ex. `laptop_antrenare_lunga_5.toml` sau
  `laptop_fapte.toml`) trebuie pregătită de om, ca până acum. Fără ea, CONTINUUM spune ce ar vrea și ce lipsește, de
  exemplu „capacitate_indisponibila: nu există nicio configurare potrivită (config/laptop_fapte*.toml)”.
  Din 7 octombrie, amândouă există.
- **De unde pornește o antrenare:**
  - o linie nouă pornește din ultimul model păstrat cu aceeași arhitectură (`--porneste-din`);
  - fără un astfel de model, sau dacă configurarea cere `de_la_zero`, pornește de la zero;
  - o linie începută și întreruptă se reia de unde a rămas.
- **Hrana „folosită”:** hrana e folosită dacă o linie care o pomenește a rulat după ultima ei schimbare. Când
  profesorul adaugă povești, hrana redevine nouă.
- **Modulele:** CONTINUUM nu creează instanțe și nu încarcă modele.
  - Verifică doar dacă modulul se încarcă și are MANIFEST.
  - Dacă un modul oferă `sanatate()` sau `semnale()`, ca metode de clasă, le întreabă. Niciun modul de azi nu le
    oferă.
  - CONTINUUM nu stă pe niciun port Kronos, deci nu intră în `teste_contracte/`.
- **Pragurile de zgomot:** cele din plan (0,02, 3 fapte, 0,3 la notă) s-au dovedit prea mici în noaptea a patra.
  Faptele sar cu până la ±13 de la o oră la alta, iar o notă are eroarea ±0,3–0,5. Adrian a ales pe 7 octombrie:
  0,005 la val_bpb (ca `prag_zgomot`), 10 fapte și 0,5 la notă.
- **Măsurători:** când o capacitate e măsurată și la oră, și apoi cu unealta (ex. nota pe 40 de povești), contează
  măsurătoarea uneltei, care e mai nouă.
- **Ce nu e în v0:** răcirea nevoilor, limita de reîncercări, bugetul zilnic de ore pe placă, setul sacru, repararea
  și explorarea. Vin în v1–v3, doar după confirmare.

### Testele: 71 noi, toate fără placă video (399 trec în total)

Testele folosesc module de probă (`teste/continuum_proba.py`) și un proiect mic într-un dosar temporar: configurări,
jurnal, hrană și unelte care doar scriu fișe.
- Fiecare etapă are testele ei (`teste/test_continuum_*.py`).
- Bucla e încercată întreagă în aceste situații:
  - o noapte simulată (jurnalul Kronos rămâne neatins);
  - o zi și o noapte „pe bune”, cu unelte de probă;
  - 0 module și 1 modul;
  - un modul care cade, și unul scos și reintrodus în timpul rulării;
  - omul la laptop (→ REPAUS);
  - o etapă care cade și configurarea stricată în timpul rulării;
  - butonul STOP.

### Primul ciclu pe datele adevărate (7 octombrie, 01:46, simulat)

După antrenare, cu placa liberă, am rulat un singur ciclu simulat (`--cicluri 1`, 3 secunde):
> ÎNVĂȚARE: e fereastra de noapte (22:00–07:00), placa e liberă (6.144 MB liberi, 51 °C), omul n-a mai atins
> laptopul de 191 min. Nu pornesc nimic: continua:povesti — capacitate_indisponibila: toate configurările potrivite
> sunt încheiate: config/laptop_antrenare_lunga.toml (8 din 8), […]_2, […]_3, […]_4 (8 din 8); pentru încă o noapte
> trebuie pregătită una nouă; dezvolta:fapte — capacitate_indisponibila: nu există nicio configurare potrivită
> (config/laptop_fapte*.toml).

Ce a văzut:
- toate cele 4 module se încarcă;
- liniile de bază: val_bpb 0,4389 (#239), 51 de fapte (#239), nota 4,7 (#226);
- ultimul model (#239) are deja toate examenele, din noaptea asta, deci nu cere măsurare.

Ce ar face:
- **ar continua**, pentru că val_bpb încă scădea în ultima oră (−0,0064, peste pragul de 0,005);
- **ar dezvolta faptele**, pentru că sunt cea mai slabă capacitate (34%) și au 7.520 de povești nefolosite.

Ambele cer o configurare nouă, pregătită de om. E chiar alegerea pentru diseară: continuare sau fapte.

### Ce urmează, după plan

Urmează proba lui Adrian: o zi întreagă în `--simuleaza`, cu deciziile comparate cu ce am fi ales de mână, apoi o
noapte reală. Criteriul de acceptare:
- 24 de ore fără să cadă;
- un modul scos și reintrodus în timpul rulării;
- omul folosește laptopul la un moment dat (→ REPAUS);
- jurnalul explică fiecare decizie în română.

## 7 octombrie: pregătirea antrenării pe fapte

### Nota profesorului, pe 40 de povești

Examenul profesorului (`unelte/examen_profesor.py`) folosește acum **40 de povești nevăzute**, nu 20.
- **Metoda e aceeași:** aceeași sămânță, deci primele 20 sunt cele de până acum, plus 20 noi.
- **Eroarea estimată** intră în fișă și pe ecran. E abaterea standard a notelor împărțită la √40.

| Modelul #239 (sfârșitul nopții a patra) | Nota |
| --- | --- |
| pe 20 de povești, la ora 8 | 4,5 ± 0,49 |
| **pe 40 de povești** | **4,4 ± 0,34** |
| din ele, cele 20 vechi | 4,55 |
| din ele, cele 20 noi | 4,25 |

Ce trebuie știut:
- Cele 20 de povești vechi au ieșit aproape la fel ca la oră. Diferența mică vine probabil de la notarea în alte loturi.
- Memoria video a fost de cel mult 3.573 MB.
- În GPT, setarea nouă `povesti_profesor` spune pe câte povești se dă nota la fiecare oră. Implicit rămâne 20, ca
  înainte; configurările noi au 40.

### `config/laptop_fapte.toml`: 3 ore pe fapte

(Varianta de dimineață; schimbată în aceeași zi, vezi secțiunea următoare.)

- **Pornirea:** continuare din #239.
- **Rata:** repornește la 0,0002 și scade pe cele 3 ore până la 0,00002.
- **Hrana în loturi:** fiecare lot de 24 are 10% bucăți din `date/fapte/povesti.txt`, restul din TinyStories întreg.
  - Setările `hrana` și `fractie_hrana` sunt noi în GPT; fără ele, antrenarea e exact ca înainte.
  - 24 × 10% = 2,4, deci loturile iau pe rând 2 sau 3 bucăți (2, 2, 3, 2, 3, …), iar media e exact 10%.
- **Examen la fiecare 30 de minute** (6 experimente): val_bpb, faptele și nota pe 40 de povești.
- **Regula 4, cu criteriul principal `fapte_corecte`:** faptele trebuie să crească cu peste 10, iar nota (prag 0,5) și
  val_bpb (prag 0,005) nu au voie să scadă.

**De știut: modelul va memora mult.** Hrana are doar 1,37 milioane de simboluri. Cu 2,4 bucăți de câte 256 în fiecare
lot, în 3 ore modelul o vede de ~35–40 de ori, pe când TinyStories doar de ~0,8 ori.

### Verificarea examenului de fapte: NU e zero

Am căutat cele 150 de propoziții ale examenului (cu răspunsul cerut) în cele 7.520 de povești cu fapte, cuvânt cu
cuvânt. **97 din 150 apar.**

| Forma întrebării | Câte din 50 apar în povești | În câte povești |
| --- | --- | --- |
| „Birds have ___.” (forma simplă) | 49 | 6.621 |
| „Mom said, "Birds have ___."” | 44 | 191 |
| „Lily learned that birds have ___.” | 4 | 4 |

Forma simplă e chiar faptul pe care l-a primit profesorul ca să scrie poveștile, iar poveștile trebuiau să-l spună cuvânt
cu cuvânt. Deci, după antrenarea pe fapte, `fapte_corecte` va măsura în bună parte **memorarea propozițiilor din
antrenare**, nu înțelegerea faptelor. Examenul nu l-am schimbat (ar strica comparația cu noaptea a patra). Variante:
1. **Un examen nou, cu propoziții reformulate**, verificat automat să nu apară în povești. Examenul vechi rămâne pentru
   comparația cu martorul, iar cel nou se măsoară întâi pe #239, ca punct de plecare.
2. **Fără examen nou.** Cele 150 de întrebări se împart în „văzute” (97) și „nevăzute” (53, mai ales forma „Lily
   learned that…”) și se raportează separat. Criteriul principal ar putea fi doar pe cele nevăzute. E mai rapid, dar
   setul nevăzut e mic.

### `config/laptop_antrenare_lunga_5.toml`: 5 ore după fapte

(Varianta de dimineață; rata s-a schimbat la 0,0002 în aceeași zi, vezi secțiunea următoare.)

- **Pornirea:** continuare simplă din cel mai bun model după fapte, adică ultimul experiment păstrat pe linia
  `fapte_1`. Cu criteriul principal, fiecare experiment păstrat are mai multe fapte decât cel dinainte.
- **Rețeta e ca în noaptea a patra:** TinyStories întreg, fără hrană, lot 24, rata repornită la 0,0005 care scade pe
  cele 5 ore până la 0,00005.
- **Examenele:** toate trei, la fiecare oră (nota pe 40), fără `[criterii]`: doar se măsoară.

**De știut: rata 0,0005 poate strica ce s-a câștigat.** În noaptea a patra, repornirea la 0,0005 a stricat val_bpb în
prima oră (0,4567 → 0,5048), iar modelul a avut nevoie de 6 ore ca să revină sub plecare. În 5 ore s-ar putea să nu
revină, iar o rată mare poate șterge și faptele învățate. Variantă: pornirea la 0,0002, ca la fapte.

### CONTINUUM, simulat toată ziua

CONTINUUM rulează în modul simulat, cu un ciclu la 15 minute:
```
python -m module.continuum.bucla --config config/continuum.toml --simuleaza --pauza-minute 15
```

Un ciclu „ca la 23:00, fără om” (`--ca-la 23:00`), pe datele adevărate, a ales singur faptele:
> [ca la 23:00, fără om] ÎNVĂȚARE: e fereastra de noapte (22:00–07:00), placa e liberă (6.144 MB liberi, 57 °C), omul
> n-a mai atins laptopul de 60 min. Aleg dezvolta:fapte: fapte = 34% (51 din 150), cea mai slabă capacitate (sens =
> 44%); 7.520 de povești nefolosite în date/fapte. [simulat] Aș porni: antrenare lungă cu config/laptop_fapte.toml
> (linia fapte_1, 6 × 30 min, din modelul #239).

Ce ar urma: după fapte, hrana devine „folosită”, iar următoarea alegere de noapte e continuarea. Ea ar porni
`laptop_antrenare_lunga_5.toml` din ultimul model păstrat, adică cel mai bun după fapte.

**Schimbat în aceeași zi:** după alegerea examenului de fapte nou (secțiunea următoare), antrenarea pe fapte are 2 ore,
5% hrană și criteriul principal `fapte_noi`, iar a cincea antrenare pornește cu rata 0,0002. Comenzile pentru diseară
sunt în secțiunea următoare.

## 7 octombrie, ziua: examenul de fapte nou (varianta 1)

Examenul vechi întreabă faptele exact cum le-a primit profesorul ca să scrie poveștile: 97 din cele 150 de propoziții ale
lui apar cuvânt cu cuvânt în poveștile de antrenare. Adrian a ales varianta 1: un examen nou, cu propoziții reformulate.

### Cum s-a făcut (`python unelte/examen_fapte_nou.py --genereaza`)

Pentru fiecare din cele 50 de fapte, profesorul scrie 3 propoziții reformulate, cu golul la capăt și același
cuvânt-răspuns. Totul se verifică automat. O propoziție intră în examen doar dacă:
- **forma e bună:** e o singură propoziție, de 5–16 cuvinte, cu răspunsul abia la capăt; nu începe cu aceleași două
  cuvinte ca faptul și nu seamănă prea mult cu celelalte două ale faptului;
- **niciun fragment de 5 cuvinte la rând** (deci nici propoziția întreagă) nu apare în poveștile cu fapte
  (869.012 cuvinte) sau în TinyStories întreg (439.692.799 de cuvinte, antrenare și validare);
- **profesorul confirmă sensul:** întrebat fără întâmplare, spune că propoziția spune același fapt, numind despre ce e
  vorba, și că e adevărată;
- **golul e clar:** pus să completeze golul singur, profesorul scrie chiar răspunsul (sau un sinonim acceptat).

Cele respinse se regenerează: profesorul primește propoziția respinsă și motivul și scrie 3 variante noi.

**Cât a trebuit regenerat:**
- **114 din 150 de propoziții** au fost respinse cel puțin o dată; doar 36 au trecut din prima.
- În total au fost **4.208 încercări:**
  - 3.511 la generarea întreagă (60 de runde, după care au rămas 10 nereușite);
  - 684 la prima completare (`--completeaza` păstrează propozițiile bune și le scrie doar pe cele care lipsesc);
  - 13 la a doua.

**Motivele respingerilor, la generarea întreagă:**
- 2.581 pentru formă (de cele mai multe ori, răspunsul nu era la capăt);
- 299 pentru un fragment din poveștile cu fapte și 121 pentru unul din TinyStories;
- 244 pentru că nu spuneau clar același fapt;
- 126 pentru că golul era neclar.

**Verificarea finală:** toate cele 150, trecute din nou prin aceleași reguli, într-o singură trecere independentă: 0
probleme, 0 fragmente de 5 cuvinte găsite.

**Cinstit, despre drum:**
- Primele trei generări le-am aruncat.
  - La prima, „alt subiect” a ajuns uneori „alt animal”: „A worm moves through the soil without ___.” pentru
    „Snakes have no legs.”.
  - La a doua și a treia, profesorul lipea răspunsul după punct („… of a whale. blowhole”) sau scria goluri
    neclare („…a shadow shows up in the ___.” cerea „light”).
  - De aici au venit verificarea sensului, completarea golului de către profesor și cererea propoziției direct cu
    „___” la capăt.
- Chiar exemplul „When it is very cold, water turns into ___.” ar fi fost respins: „when it is very cold” apare în
  poveștile cu fapte, pentru că e în faptul însuși.
- Câteva propoziții rămân stângace, deși trec toate verificările. De exemplu, „These birds walk on ice and can't
  ___.” nu numește pinguinii, iar cele trei de la curcubeu sunt construite la fel („… a rainbow … when there are
  ___”). Toate sunt în `date/fapte/examen_nou.json`, cu încercările în `lucru/examen_fapte_nou/`.

**5 exemple:**

| Faptul | Propoziția nouă | Răspuns |
| --- | --- | --- |
| Water freezes into ice when it is very cold. | When water gets cold enough, it turns into ___. | ice |
| Birds have feathers. | The thing that covers a bird is ___. | feathers |
| The heart pumps blood around the body. | What the heart moves around your body is ___. | blood |
| Whales breathe air through a blowhole on top of their heads. | Whales push air out through a hole on their heads called a ___. | blowhole |
| Dogs have a very good sense of smell. | Dogs can track a person using their strong sense of ___. | smell |

### Punctul de plecare, pe examenul nou (`python unelte/examen_fapte_nou.py --experiment N`)

| Modelul | Examenul vechi (fapte_corecte) | **Examenul nou (fapte_noi)** | cu sinonime | fapte cu măcar un răspuns corect |
| --- | --- | --- | --- | --- |
| #226 (sfârșitul nopții a treia) | 41 | **36** din 150 | 41 | 23 din 50 |
| #239 (sfârșitul nopții a patra) | 51 | **36** din 150 | 39 | 24 din 50 |

Pe examenul nou, cele două modele sunt la egalitate. Creșterea 41 → 51 de la examenul vechi, într-o noapte fără
povești cu fapte, ține deci de examenul vechi, nu de fapte învățate. Asta se potrivește cu ce s-a văzut în noaptea a
patra: faptele vechi săreau cu ±13 de la o oră la alta.

### Configurările pentru diseară

- **`config/laptop_fapte.toml`:**
  - criteriul principal e acum `fapte_noi` (prag 10); `fapte_corecte` doar se raportează;
  - nota are pragul 0,5, iar val_bpb pragul 0,005;
  - hrana e 5% din fiecare lot (24 × 5% = 1,2, deci pe rând 1 sau 2 bucăți);
  - 2 ore, cu examen la fiecare 30 de minute: val_bpb, fapte_noi, fapte_corecte și nota pe 40;
  - rata 0,0002 → 0,00002 pe cele 2 ore.
- **`config/laptop_antrenare_lunga_5.toml`:** rata pornește la 0,0002 și scade la 0,00002 pe 5 ore, din cel mai bun
  model după fapte. La fiecare oră se măsoară și `fapte_noi`.
- **GPT-ul** dă examenul nou la fiecare oră, cu `examene_suplimentare = ["fapte", "fapte_noi", "profesor"]`. Tabelul
  uneltei de antrenare lungă are o coloană „fapte noi” (doar când e măsurat).
- **CONTINUUM** măsoară acum capacitatea „fapte” cu examenul nou (`fapte_noi`, prin `unelte/examen_fapte_nou.py`).
  Rularea simulată de toată ziua recitește configurarea singură.

### Comenzile pentru diseară

```
python unelte/antrenare_lunga.py --config config/laptop_fapte.toml --ore 4 --porneste-din 239 --compara-cu 239 --inceput "Once upon a time, there was a fearful little dog named Coco"
python -m kronos jurnal --config config/laptop_fapte.toml        # ultimul „păstrat” = cel mai bun model după fapte
python unelte/antrenare_lunga.py --config config/laptop_antrenare_lunga_5.toml --ore 5 --porneste-din <nr> --compara-cu <nr> --inceput "Once upon a time, there was a fearful little dog named Coco"
python -m module.continuum.bucla --config config/continuum.toml --jurnal 100    # ce a ales CONTINUUM azi
```

## 7 octombrie, ziua: lanțul de antrenare și CONTINUUM v1

Din 7 octombrie, laptopul e doar al lui Kronos, zi și noapte. Deci antrenarea nu mai așteaptă seara.

### Lanțul de antrenare (`python unelte/lant_antrenare.py`)

Un script mic pornește cele două antrenări una după alta, fără să aștepte nimeni între ele. Nu schimbă `kronos/` și nici
uneltele, doar le pornește pe rând:
1. **antrenarea pe fapte:** `config/laptop_fapte.toml`, 4 × 30 de minute, din #239;
2. **cel mai bun model după fapte:** experimentul păstrat al liniei `fapte_1` cu cele mai multe `fapte_noi` (criteriul
   principal; Kronos îl alege la fel);
3. **a cincea antrenare lungă:** `config/laptop_antrenare_lunga_5.toml`, 5 ore, din modelul de la pasul 2.

Înainte de fiecare etapă se uită la butonul STOP. Apoi așteaptă, cel mult 30 de minute, ca placa să fie liberă:
- niciun alt program Python pe ea (o singură sarcină grea);
- cel puțin 5.500 MB liberi;
- temperatura sub 85 °C.

O etapă care iese cu eroare oprește lanțul. Pornit pe 7 octombrie la 09:33, în fundal; ce scrie e în
`lucru/lant_7_octombrie.log`.

**De știut:** Kronos păstrează automat **primul** experiment al unei linii noi, pentru că n-are încă un „cel mai bun” cu
care să-l compare. Deci prima jumătate de oră pe fapte (#249) n-a trecut prin regula 4. Celelalte se compară cu ea.

În `config/continuum.toml`, fereastra de învățare e acum toată ziua (`00:00-23:59`); `minute_fara_om` a rămas 10.

### CONTINUUM v1: măsurare atentă și anti-buclă

Cerut de Adrian pe 7 octombrie și construit cât rula lanțul: doar cod și teste, fără placa video. N-am atins `kronos/`
și nici examenul oficial. Toate pragurile noi stau în `config/continuum.toml`, scrise și explicate, cu valori implicite:
o configurare din v0 merge neschimbată. Amănuntele sunt în `docs/CONTINUUM_plan.md` (secțiunea 13, v1).

**Ce face în plus:**
1. **Zgomotul învățat.** Pentru fiecare capacitate, CONTINUUM învață din jurnal cât diferă de obicei două măsurători
   ale aceluiași lucru: același model examinat de două ori, sau aceeași rețetă cu altă sămânță.
   - Pragul folosit e cel mai mare dintre pragul din configurare (care rămâne „podea”) și zgomotul învățat.
   - Sub 3 perechi rămâne podeaua, iar jurnalul spune „neînvățat încă”.
2. **Trei zone, față de linia de bază:**
   - **verde:** cel mult 1 prag sub;
   - **galbenă:** între 1 și 2 praguri sub (exact 2 e încă galbenă). Cere o remăsurare, nu o acțiune;
   - **roșie:** peste 2 praguri sub. CONTINUUM scrie un raport către om în `lucru/continuum/rapoarte/`, cu modelul
     păstrat la care s-ar întoarce. Nu repară singur.
3. **Linia de bază se mută doar confirmată.**
   - Un scor mai bun e întâi „candidat”, în coada din `stare.json`, cu motivul lui.
   - Linia de bază și încrederea strategiei se mută abia după o a doua măsurătoare care îl confirmă: încă un examen pe
     același model, sau ora următoare a aceleiași antrenări.
   - Când are unealta de examen, CONTINUUM cere singur remăsurarea.
   - Linia de bază nu coboară niciodată.
4. **Cât a costat.** MĂSOARĂ notează orele pe placă, pașii pe secundă și memoria video. Un succes cu câștigul pe oră sub
   jumătate din media strategiei e „SUCCES SCUMP”: încrederea nu urcă.
5. **Vectorul capacităților.** Toate capacitățile, și cele nemăsurate, au scor, linie de bază, zonă, prag folosit și
   procent. „Cea mai slabă” iese din el.
6. **„Continuă” doar cu temei.** Povestirile se continuă doar dacă:
   - ultima oră a coborât val_bpb cu peste 0,005;
   - și pe ultimele 3 ore tendința e bună.

   Două ore la rând sub prag înseamnă „saturat”, iar dezvoltarea trece în față.
7. **Anti-buclă:**
   - o nevoie tratată nu se reia 6 cicluri (în afară de raportul pentru zona roșie);
   - după 5 eșecuri la rând, strategia e blocată și omul primește un raport;
   - cel mult 20 de ore pe placă pe zi, cu tot ce a rulat azi, oricine l-a pornit.

**Ordinea nevoilor:** repara, masoara, remasoara, dezvolta, continua.

**Comenzi noi:**
```
python -m module.continuum.bucla --config config/continuum.toml --simuleaza --stare lucru/continuum_v1_proba   # memorie separată
python -m module.continuum.bucla --config config/continuum.toml --simuleaza --placa-libera   # ca și cum placa ar fi liberă
```

### Ce trebuie știut, cinstit

- **Pe jurnalul real, pragul la val_bpb urcă de la 0,005 la 0,0144.**
  - Vine din 22 de perechi de semințe, mai ales din experimentele scurte de căutare, unde două semințe diferă mai mult
    decât la antrenările lungi.
  - Deci zonele și verdictele pe povești sunt acum mai prudente.
  - Pentru „continuă” nu se aplică: două ore ale aceleiași antrenări au aceeași sămânță, deci acolo pragul rămâne 0,005.
- **Faptele și nota n-au încă zgomot învățat** (0 și 1 perechi). Rămân pragurile alese de Adrian: 10 și 0,5.
- **Examenul de fapte e determinist:** același model dă aceleași răspunsuri. Deci o remăsurare a lui confirmă aproape
  mereu. Confirmarea mai tare vine de la ora păstrată de după.
- **Ultima oră a unei antrenări** rămâne candidat până la o remăsurare sau o oră de după. La val_bpb nu există unealtă de
  remăsurare, deci doar o oră de după o poate confirma.
- **Nota de bază vine din alt examen.** Linia de bază la „sens” (4,7, #226) e o notă pe 20 de povești. Modelele noi au
  nota pe 40, iar cele 20 de povești noi ies mai greu (la #239: 4,25 față de 4,55). Comparația nu e deci de la egal la
  egal. Variantă: o capacitate separată pentru nota pe 40, cu linia ei de bază.
- **Bugetul de ore** se adună din duratele fișelor Kronos începute azi. Examenele date separat, cu unelte, nu au durată în
  fișă, deci nu intră în buget.
- **Pragurile se compară fără resturile de rotunjire ale calculatorului.** De exemplu, 4,4 − 3,4 dă în calculator
  1,0000000000000004: fără grijă, o scădere de exact 2 praguri ar fi ieșit zona roșie.

### Prima rulare v1 pe jurnalul real (7 octombrie, 10:18, simulat)

Un singur ciclu, cu memoria în `lucru/continuum_v1_proba/` (ca să nu se amestece cu rularea v0 de toată ziua):
> REPAUS: placa e ocupată de altă sarcină (python.exe (17816)): o singură sarcină grea odată, doar observ. Nevoi în
> așteptare: remasoara:povesti, remasoara:sens, dezvolta:sens.

**Ce vede v1** pe ultimul model păstrat, #249 (prima jumătate de oră pe fapte):

| Capacitatea | Scor pe #249 | Linia de bază | Pragul folosit | Zona |
| --- | --- | --- | --- | --- |
| povești (val_bpb) | 0,4675 | 0,4389 (#239) | 0,0144, învățat din 22 de perechi de semințe | galbenă (1,99 praguri sub) |
| fapte (fapte_noi) | 59 din 150 (39%) | 59 (#249) | 10, neînvățat încă | verde |
| sens (nota) | 3,7 din 10 (37%) | 4,7 (#226) | 0,5, neînvățat încă | galbenă (exact 2 praguri sub) |

**Dacă placa ar fi fost liberă** (`--placa-libera`, ca probă): ar fi remăsurat nota pe #249 („remasoara:sens”), nu ar fi
pornit o acțiune. Nivelul ar fi fost ÎNTREȚINERE, nu ÎNVĂȚARE, pentru că placa avea 87 °C, încălzită de antrenare.

**V0, la aceeași oră (10:15):** tot REPAUS, cu „dezvolta:sens” în așteptare. V0 nu vede cele două scăderi. Mai devreme,
azi, v0 a ales:
- „masoara:fapte” la 08:45, când #239 încă n-avea examenul de fapte nou;
- „dezvolta:fapte” la proba „ca la 23:00”;
- în rest, nimic: ziua, ÎNTREȚINEREA nu permitea antrenări.

**Diferența:** v1 remăsoară întâi ce pare să fi scăzut, apoi dezvoltă. V0 trece direct la „dezvoltă”. Amândouă văd acum
„sensul” drept cea mai slabă capacitate. Atenție însă: nota de bază (4,7) e pe 20 de povești, iar cea de pe #249 pe 40.

### Testele: 37 noi pentru v1 și lanț, toate fără placă video

- **Cât rula lanțul,** suita a mers pe procesor, cu placa ascunsă: 431 trec, iar 1 e sărit (contractul cu profesorul
  adevărat, care cere placa).
- **4 fișiere (41 de teste) le-am lăsat pentru după lanț:** `test_cap_coada`, `test_criterii`, `test_criteriu_principal`
  și `test_examene_suplimentare`.
  - Ele pornesc Kronos, iar paznicul lor citește temperatura reală a plăcii.
  - Cu antrenarea, placa stă la ~87 °C, peste limita de 85 °C din `config/proba.toml`, deci ar face pauze de răcire la
    nesfârșit.
  - Nu ating nimic din ce s-a schimbat azi. Rulează după lanț, cu toată suita pe placă.

- `teste/test_continuum_v1.py`: câte un grup pentru fiecare din cele 7 puncte, plus configurarea veche și cea greșită.
  Testele merg pe proiectul de probă din `teste/continuum_proba.py`.
- Testele din v0 au fost aduse la regulile v1. De exemplu:
  - „repara” are mereu urgența 1;
  - o linie neterminată nu se mai continuă fără câștig;
  - noaptea pe fapte se încheie acum cu o remăsurare care confirmă sau infirmă ultima oră.
- `teste/test_lant_antrenare.py`: alegerea celui mai bun model după fapte, citirea plăcii și ordinea etapelor.

## 7 octombrie: rezultatele lanțului (fapte, apoi a cincea antrenare, 09:33–16:57)

Lanțul a mers singur, fără erori, în 7 ore și 24 de minute: faptele în 2 ore și 10 minute, apoi a cincea antrenare în 5
ore și 13 minute. Placa a stat la 86–87 °C cât a antrenat. Paznicul a făcut o singură pauză de răcire, la pornirea
etapei a doua (73 °C → 70 °C). Antrenarea a rezervat cel mult 2.226 MB de memorie video. Cu profesorul, la examene,
placa avea ~3,2 GB ocupați când m-am uitat (limita: 5,5 GB).

Peste tot:
- „fapte noi” = examenul nou, din 150. În paranteză: aceeași cifră cu sinonime, apoi din câte din cele 50 de fapte s-a
  știut măcar un răspuns;
- „fapte vechi” = examenul vechi, din 150;
- nota e pe 40 de povești, cu eroarea estimată.

### Antrenarea pe fapte (`config/laptop_fapte.toml`, din #239, 4 × 30 de minute, 5% hrană)

| Ora | Exp. | Decizia lui Kronos | val_bpb | Fapte noi | Fapte vechi | Nota | Pași |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | #239 | punctul de plecare | 0,4389 | 36 (39 / 24) | 51 | 4,4 ± 0,34 | – |
| 1 | #249 | păstrat: primul pe linie, fără comparație | 0,4675 | 59 (62 / 35) | 147 | 3,7 ± 0,24 | 14.048 |
| 2 | #250 | respins: fapte noi +1 față de #249, trebuia peste 10 | 0,4573 | 60 (61 / 38) | 147 | 4,4 ± 0,27 | 13.661 |
| 3 | #251 | respins: +7 | 0,4415 | 66 (68 / 40) | 146 | 4,47 ± 0,34 | 13.657 |
| 4 | #252 | **păstrat: +13** | **0,4340** | **72 (76 / 41)** | 146 | 4,75 ± 0,32 | 13.716 |

- **Pragul de 10 la fapte noi a fost trecut la limită.** #252 are +13 față de #249, doar cu 3 peste prag, iar zgomotul
  examenului nou nu e încă măsurat (0 perechi).
- **Creșterea în sine e însă reală:** a urcat în toate cele 4 jumătăți de oră (59, 60, 66, 72). Față de #239 (36),
  faptele noi s-au dublat, iar faptele știute au urcat de la 24 la 41 din 50.
- **Prima jumătate de oră n-a trecut prin regula 4:** Kronos păstrează automat primul experiment al unei linii noi. Ea a
  stricat val_bpb (0,4389 → 0,4675) și nota (4,4 → 3,7), din cauza ratei repornite la 0,0002. Amândouă și-au revenit
  până la ora 4.
- **La final, #252 e la egalitate cu #239 pe celelalte două:**
  - val_bpb 0,4340: cu 0,0049 mai bun, sub pragul de 0,005;
  - nota 4,75 ± 0,32 față de 4,4 ± 0,34: diferența e în eroare.
- **Examenul vechi de fapte (146–147 din 150) măsoară memorarea:** 97 din propozițiile lui apar cuvânt cu cuvânt în
  hrană.
- **Legătura cu val_bpb pe cele 4 ore: fapte noi −0,96.** Faptele noi au urcat cât timp val_bpb cobora, odată cu rata.
  Cifra din rezumatul uneltei (−0,01) pune la socoteală și ora 0 (#239, de dinainte de hrană).

### A cincea antrenare lungă (`config/laptop_antrenare_lunga_5.toml`, din #252, 5 × 60 de minute, fără hrană)

| Ora | Exp. | Decizia lui Kronos | val_bpb | Fapte noi | Fapte vechi | Nota | Pași | Rata la final |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | #252 | punctul de plecare | 0,4340 | 72 (76 / 41) | 146 | 4,75 ± 0,32 | – | – |
| 1 | #253 | păstrat: primul pe linie, fără comparație | 0,4692 | 33 (35 / 19) | 42 | 3,8 ± 0,21 | 27.279 | 0,000183 |
| 2 | #254 | păstrat: −0,0088 | 0,4605 | 32 (34 / 20) | 45 | 4,65 ± 0,35 | 27.277 | 0,000138 |
| 3 | #255 | păstrat: −0,0132 | 0,4473 | 27 (31 / 18) | 44 | 4,2 ± 0,29 | 27.189 | 0,000082 |
| 4 | #256 | păstrat: −0,0137 | 0,4336 | 36 (39 / 24) | 50 | 4,83 ± 0,36 | 27.090 | 0,000037 |
| 5 | #257 | păstrat: −0,0055 | **0,4281** | 37 (40 / 24) | 54 | 4,4 ± 0,31 | 27.002 | 0,000020 |

Configurarea n-are `[criterii]`, deci Kronos a decis doar după val_bpb (prag 0,005). Examenele doar s-au măsurat. Ora 5 a
trecut pragul la limită: −0,0055, față de 0,005.

**Verdict cinstit:**
- **val_bpb 0,4281 e cel mai bun scor de până acum.** E cu 0,0108 sub #239 și cu 0,0059 sub #252. Dar vine după încă 5
  ore de antrenare, deci e în bună parte efectul pașilor în plus.
- **Faptele învățate s-au pierdut.**
  - În prima oră fără hrană, faptele noi au căzut de la 72 la 33, iar cele vechi de la 146 la 42.
  - La final, faptele noi sunt 37 (24 de fapte știute din 50), adică exact cât avea #239 dimineață (36, tot 24).
  - Deci cele 2 ore pe fapte n-au lăsat nimic durabil, după 5 ore fără hrană.
- **Nota a ajuns la 4,4 ± 0,31**, ca la #239 (4,4 ± 0,34).
- **Repornirea ratei la 0,0002 a costat din nou prima oră:** val_bpb a urcat cu 0,035 (0,4340 → 0,4692) și abia la
  ora 4 a revenit la plecare. În noaptea a patra, cu 0,0005, saltul a fost +0,048.

**Ce e „cel mai bun model” acum depinde de criteriu:**
- după val_bpb: #257 (0,4281, 37 de fapte noi);
- după fapte: #252 (72 de fapte noi, val_bpb 0,4340).

Variante pentru data viitoare:
1. **Hrana și în antrenarea lungă.** Aceeași 5% povești cu fapte în fiecare lot, ca faptele să nu se piardă. Se măsoară
   la fel, pe ore, și se vede dacă faptele rămân.
2. **Fără repornirea ratei.** Continuarea pornește de la rata la care s-a oprit etapa de dinainte (0,00002) sau urcă
   încet. Așa nu se pierde prima oră.

### CONTINUUM v0, simulat toată ziua (36 de cicluri, 0 erori)

| Când | Ce a ales și de ce |
| --- | --- |
| 01:46 | nimic: toate configurările lungi erau încheiate, iar `laptop_fapte.toml` nu exista încă |
| proba „ca la 23:00” | **dezvolta:fapte**, din #239 (fapte 34%, cea mai slabă; 7.520 de povești nefolosite) |
| 07:15–08:15, 09:00–09:30 | nimic: ziua (ÎNTREȚINERE) antrenarea nu era permisă, iar hrana era gata |
| 08:45 | **masoara:fapte**: #239 încă n-avea examenul de fapte nou |
| 08:30 | REPAUS: placa era ocupată de altă sarcină |
| 09:45–16:45 | REPAUS: placa era ocupată de lanț |
| 17:00 | nimic, cu placa liberă: hrana de fapte a fost folosită (`fapte_1`), iar toate configurările lungi sunt încheiate, și `laptop_antrenare_lunga_5.toml` (5 din 5). Pentru mai departe trebuie pregătită una nouă |

În REPAUS, nevoile în așteptare au urmat modelele noi:
- **dezvolta:sens**, după #249 (nota 3,7): sensul devenise cel mai slab;
- **dezvolta:fapte**, după #253 (33 de fapte noi): faptele redeveniseră cele mai slabe;
- **continua:povesti**, cât timp val_bpb încă scădea.

Simularea rulează în continuare cu codul v0, pornită la 07:15.

**Testele, după lanț:** toată suita, cu placa: 473 trec (cu cele 4 fișiere amânate și cu profesorul adevărat).

## Noaptea 7–8 octombrie: lanțul 6 (de ce se uită faptele)

Patru rulări, una după alta, cu `python unelte/lant_antrenare.py --plan config/lant_6.toml`. Scriptul de înlănțuire
citește acum etapele dintr-un plan. Fiecare configurare e o copie a antrenării 5, cu doar diferențele de mai jos:

| Rulare | Configurarea | Întrebarea | Diferențe față de antrenarea 5 |
| --- | --- | --- | --- |
| 6a | `laptop_antrenare_lunga_6a.toml` | Rămân faptele dacă hrana e mereu în amestec? | 5% hrană cu fapte în fiecare lot; `[criterii]`: val_bpb principal (0,005), fapte_noi −10 cel mult, nota −0,5 cel mult |
| 6c-restart | `laptop_masurare_6c_restart.toml` | Uitarea vine din pașii mari ai ratei repornite... | doar prima oră, examen la fiecare 15 minute; fără criterii |
| 6c-continuare | `laptop_masurare_6c_continuare.toml` | ...sau din simplul fapt că antrenează pe altceva? | ca 6c-restart, dar rata 0,00002 → 0,000002 (fără repornire) |
| 6b | `laptop_antrenare_lunga_6b.toml` | Mai câștigă continuarea cu pași mici, peste zgomot? | din #257; rata 0,00002 → 0,000002; criteriile ca la 6a |

De știut:
- **De unde pornesc.** 6a și ambele 6c pornesc din #252: 72 de fapte noi, val_bpb 0,4340. 6b pornește din #257:
  val_bpb 0,4281.
- **6c sunt măsurători, nu candidați.**
  - Liniile lor se numesc `masurare_6c_*`, iar numele configurărilor nu se potrivesc cu liniile urmărite de CONTINUUM.
  - Scăderea ratei e aceeași ca la antrenarea 5 (cosinus pe 5 ore), dar se face doar prima oră.
  - Între cele două rulări diferă doar mărimea ratei (de 10 ori).
- **Nota se dă la toate cele 4 puncte ale lui 6c**, nu doar la 30 și 60 de minute: modelul nu poate sări examenul
  profesorului la unele experimente. Costă ~1 minut în plus pe punct și nu schimbă antrenarea.
- **Optimizatorul pornește din nou în toate rulările.** Așa face unealta cu `--porneste-din`, cu încălzire în primii 100
  de pași. „Fără repornire” înseamnă aici doar că rata nu sare înapoi la 0,0002.

### Rezultatele nopții 7–8 octombrie (18:55–02:41)

**Pe scurt:**
- **6a, 6c-restart și 6c-continuare au mers.**
- **6b n-a mai rulat.** L-am oprit la 02:41, după 4 minute, din cauza unei probleme cu alimentarea laptopului (mai jos).
- **Pentru toate tabelele:** R = fapte_noi împărțit la 72 (cât avea #252 la plecare); fapte vechi și nota sunt pe
  40 de povești, cu eroarea estimată.

**6a: hrana mereu în amestec** (din #252, 5 ore, 5% hrană, criterii: val_bpb principal 0,005, fapte_noi −10, nota −0,5)

| Ora | Exp. | Decizia lui Kronos | val_bpb | Fapte noi | R | Fapte vechi | Nota | Pași |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | #258 | păstrat: primul pe linie, fără comparație | 0,4703 | 65 | 0,90 | 146 | 4,17 ± 0,26 | 27.831 |
| 2 | #259 | păstrat: −0,0098 | 0,4605 | 57 | 0,79 | 145 | 3,88 ± 0,25 | 27.560 |
| 3 | #260 | păstrat: −0,0120 | 0,4485 | 67 | 0,93 | 146 | 5,08 ± 0,36 | 27.733 |
| 4 | #261 | respins: nota a scăzut cu 0,98 față de #260 (pragul 0,5) | 0,4370 | 65 | 0,90 | 146 | 4,1 ± 0,19 | 29.148 |
| 5 | #262 | păstrat: −0,0181 față de #260 | **0,4304** | 59 | 0,82 | 145 | 4,67 ± 0,31 | 29.032 |

**6a lângă antrenarea 5** (aceeași rețetă, aceeași sămânță; diferă doar hrana):

| Ora | val_bpb 5 | val_bpb 6a | Costul hranei | Fapte noi 5 (R) | Fapte noi 6a (R) |
| --- | --- | --- | --- | --- | --- |
| 1 | 0,4692 | 0,4703 | +0,0011 | 33 (0,46) | 65 (0,90) |
| 2 | 0,4605 | 0,4605 | +0,0001 | 32 (0,44) | 57 (0,79) |
| 3 | 0,4473 | 0,4485 | +0,0013 | 27 (0,38) | 67 (0,93) |
| 4 | 0,4336 | 0,4370 | +0,0034 | 36 (0,50) | 65 (0,90) |
| 5 | 0,4281 | 0,4304 | +0,0023 | 37 (0,51) | 59 (0,82) |

- **Hrana păstrează faptele:** R a stat între 0,79 și 0,93, față de 0,38–0,51 fără hrană.
- **Costul la val_bpb e mic:** +0,0023 la final, sub pragul de 0,005. Cinstit, costul e puțin subestimat la orele 4–5:
  atunci 6a a avut cu ~7% mai mulți pași decât antrenarea 5 (29,1 mii față de 27,0 mii pe oră; placa a mers mai repede
  noaptea).
- **Respingerea lui #261 vine din zgomotul notei.** #260 avusese o notă mare (5,08 ± 0,36), iar #261 a coborât la 4,1,
  deși val_bpb se îmbunătățise cu 0,0115.

**6c: curba uitării** (din #252, TinyStories fără hrană, examen la fiecare 15 minute; măsurători, nu candidați)

| Minutul | 6c-restart (0,0002) | | | 6c-continuare (0,00002) | | |
| --- | --- | --- | --- | --- | --- | --- |
| | **fapte noi (R)** | val_bpb | pași adunați | **fapte noi (R)** | val_bpb | pași adunați |
| 0 | 72 (1,00) | 0,4340 | 0 | 72 (1,00) | 0,4340 | 0 |
| 15 | 35 (0,49) | 0,4731 | 7.336 | 63 (0,88) | 0,4331 | 7.313 |
| 30 | 33 (0,46) | 0,4726 | 14.703 | 56 (0,78) | 0,4322 | 13.148 |
| 45 | 30 (0,42) | 0,4714 | 22.058 | 48 (0,67) | 0,4317 | 18.884 |
| 60 | 31 (0,43) | 0,4670 | 29.386 | 45 (0,62) | 0,4317 | 21.248 |

Nota, la 30 și 60 de minute: restart 4,0 și 3,85; continuare 4,45 și 4,22. Decizia lui Kronos nu contează aici.

- **Cu rata repornită, faptele cad în primele 15 minute,** de la 72 la 35, apoi stau pe loc (30–35). La 60 de minute,
  restart-ul se potrivește cu ora 1 a antrenării 5 (31 față de 33, val_bpb 0,4670 față de 0,4692).
- **Cu rata mică, faptele scad încet și constant:** 63, 56, 48, 45.
  - Chiar la aceiași pași, uitarea e mult mai mică: la ~7.300 de pași, 63 față de 35; la ~21.000–22.000, 45 față de 30.
  - val_bpb nu se strică (0,4317–0,4331).
- **Răspunsul la întrebare:** căderea bruscă vine din pașii mari ai ratei repornite. Simplul fapt că antrenează pe
  altceva le roade și el, dar încet: cam 7 fapte pe sfert de oră.
- **Atenție, 6c-continuare a avut mai puțini pași în sferturile 2–4,** din cauza problemei cu curentul: 80%, 78% și
  32% din normal. De aceea am pus și pașii adunați. Comparația la pași egali rămâne clară, dar curba „pe minute” a
  continuării e mai scurtă decât ar fi trebuit.

**6b: n-a rulat.** Întrebarea lui (mai câștigă ceva continuarea cu pași mici?) rămâne deschisă. Un indiciu din 6c-continuare
(alt model de plecare, #252): în 15 minute, val_bpb a coborât cu ~0,002 (0,4340 → 0,4317), apoi a stat pe loc. Asta e sub
pragul de 0,005.

**Cel mai bun model păstrat, după fiecare criteriu** (antrenările lungi de la #239 încoace, fără 6c):
- **val_bpb:** #257, sfârșitul antrenării 5: 0,4281 (37 de fapte noi).
- **fapte noi:** #252, sfârșitul etapei pe fapte: 72 (val_bpb 0,4340).
- **nota:** #260, ora 3 din 6a: 5,08 ± 0,36 (val_bpb 0,4485). Notele sunt zgomotoase: 4,4–5,1 se suprapun în ±2 erori.
- **cel mai bun compromis:** #262, sfârșitul lui 6a: val_bpb 0,4304 (doar +0,0023 față de #257, sub prag), 59 de fapte
  noi, nota 4,67.

**Problema cu alimentarea (de verificat înainte de altă rulare lungă):**
- **Ce s-a întâmplat.** De la 22:31, Windows a înregistrat tot mai des „schimbarea sursei de curent” (evenimentul
  Kernel-Power 105):
  - 4 în ora 22;
  - 121 în ora 01;
  - 699 în primele 40 de minute ale orei 02, la 1–3 secunde una de alta.
- **Efectul.** Laptopul trecea mereu între priză și baterie. Bateria a coborât la 34%, iar placa a fost frânată: 210 MHz
  în loc de ~1.500, în regimul de repaus P8, cu motivele „limitare de putere” și „limitare termică” din partea
  sistemului.
- **De aceea a încetinit 6c-continuare** (8,1 → 6,5 → 6,4 → 2,6 pași pe secundă).
- **De ce am oprit 6b.** Ar fi rulat frânat, iar prima lui oră ar fi fost păstrată automat ca prima a liniei, deși
  nu era comparabilă.
- **După oprire:**
  - 6 comutări în 3 minute, față de 175 în cele 9 minute de dinainte, cu sarcină;
  - bateria se încarcă din nou.

  Deci încărcătorul sau contactul lui cedează sub sarcină.
- **De verificat:** încărcătorul original de 200 W, mufa bine introdusă la ambele capete și cablul neîndoit.
- **Ce a rămas de la 6b.** Starea lui de pornire, în `lucru/antrenare_lunga_6b/`, e cea din #257, neantrenată. O rulare
  nouă pornește de acolo.
- **Antrenările de dinainte nu par atinse** (6a, 6c-restart: 7,7–8,2 pași pe secundă, ca de obicei).

## 8 octombrie, dimineața: setul sacru, retenția R, hrana implicită, configurarea 7 și prima oră judecată

### Setul sacru de fapte (`date/fapte/examen_sacru.json`)

O a patra formulare pentru fiecare din cele 50 de fapte, scrisă de profesor. Verificările sunt aceleași ca la examenul
nou:
- niciun fragment de 5 cuvinte comun cu hrana sau cu TinyStories;
- profesorul confirmă că propoziția spune același fapt;
- profesorul completează singur golul cu răspunsul.

În plus, fiecare propoziție trebuie să difere de cele 3 ale examenului nou: cel mult 60% cuvinte comune cu fiecare.

```
python unelte/examen_fapte_nou.py --genereaza --sacru --doar-local     # setul (o singură dată, cu profesorul)
python unelte/examen_fapte_nou.py --sacru --experiment N               # examenul, doar manual
```

**Scorul pe setul sacru nu se folosește la selecție.**
- Setul nu intră în `examene_suplimentare`, nu-l vede CONTINUUM și nu-l folosește nicio decizie automată.
- Rezultatele nu intră nici măcar în jurnalul Kronos: stau în `lucru/examen_sacru/rezultate.jsonl`.
- Un test verifică că nici modelele, nici `kronos/`, nici CONTINUUM, nici unealta de antrenare nu pomenesc setul sacru.

**Cum s-a făcut** (8 octombrie, 07:41–07:48):
- 50 de propoziții, niciuna nereușită; 41 au avut nevoie de mai multe încercări (429 în total, în 39 de runde).
- Respingeri:
  - 57 pentru un fragment din poveștile cu fapte, 56 pentru unul din TinyStories;
  - 214 pentru formă;
  - 27 pentru că nu spuneau clar același fapt;
  - 25 pentru că golul era neclar.
- Ca la examenul nou, câteva rămân stângace, deși trec toate verificările. De exemplu: „Cows make a soft substance that
  babies drink ___.” sau „Cold dessert turns runny when the temperature goes to ___.”.
- 18 n-au punct la final (ca 6 din cele 150 ale examenului nou). Nu contează: elevul primește doar textul dinaintea
  golului.

**Punctul de plecare**, dat o singură dată:

| Modelul | Setul sacru (din 50) | Cu sinonime | Examenul nou (din 150), pentru comparație |
| --- | --- | --- | --- |
| #252 (sfârșitul etapei pe fapte) | 26 | 26 | 72 |
| #257 (sfârșitul antrenării 5, fără hrană) | 11 | 13 | 37 |
| #262 (sfârșitul lui 6a, cu hrană) | 29 | 29 | 59 |

Pe 50 de întrebări, eroarea e cam ±3,5. #252 și #262 sunt deci la egalitate, iar #257 e clar mai jos, ca la examenul
nou. Ordinea confirmă, pe întrebări pe care nicio decizie nu le-a văzut, că hrana păstrează faptele.

### Retenția R

R = faptele noi ale unui model ÷ faptele noi ale modelului din care a pornit linia lui. E doar raportată, nu e criteriu.
- **Unealta de antrenare lungă** o arată la fiecare oră, în tabel (coloana R) și în `rezultat.json`. Punctul de plecare
  ia acum și criteriile din fișa modelului de pornire: la 6a, ora 0 are în sfârșit 72 de fapte noi.
- **CONTINUUM** o scrie în `stare.json`, la capacitate și în vector. Pe jurnalul de azi, la #262: R = 0,82 față de #252.

### Hrana implicită și configurarea 7

- **Hrana cu fapte, 5% din fiecare lot, e implicită** în orice antrenare lungă (lecția 6a).
  - Unealta o adaugă singură când configurarea nu pomenește `hrana`; fișele din jurnal o înregistrează.
  - Pentru o antrenare fără hrană: `hrana = ""`. Așa le-am marcat pe 5, 6b și cele două 6c, ca o reluare să răspundă la
    aceeași întrebare.
- **`config/laptop_antrenare_lunga_7.toml`**, pentru diseară:
  - din #262, 8 ore, hrană 5%;
  - rata 0,0001 → 0,00001, fără repornire la 0,0002 (lecția 6c);
  - criteriile: val_bpb principal (0,005), fapte_noi −10 cel mult, nota −1,0 cel mult (eroarea notei e ±0,35, cu
    valori extreme; 0,5 a respins #261 din zgomot).

  N-a pornit încă. Comanda e în antetul configurării.

### CONTINUUM v1: două corecturi

- **Zgomotul se învață doar din experimente de cel puțin 60 de minute** (`[zgomot] minute_minime`).
  - Pe jurnalul real nu rămâne nicio pereche: toate cele 42 de ore lungi au sămânța 0.
  - Pragul la val_bpb revine de la 0,0144 la podeaua de 0,005.
- **Nota se compară doar pe 40 de povești** (`povesti = 40` la „sens”).
  - Linia de bază a notei nu mai e 4,7 (#226, pe 20 de povești), ci 5,08 (#260, pe 40).
  - Orele de dinainte de 7 octombrie (nota pe 20) nu mai contează nici la scorul de acum, nici la zgomot.

### kronos: prima oră a unei linii pornite dintr-un model păstrat nu mai e păstrată din oficiu (aprobat de Adrian)

- **Ce face.** Cu `porneste_din` (unealta îl pune din `pornire.json` la `--porneste-din`), regula 4 judecă primul
  experiment al liniei față de scorurile acelui model: val_bpb și criteriile.
- **Ce rămâne la fel.**
  - Rețeta liniei rămâne cea din configurare.
  - Din primul experiment păstrat încolo, referința e linia însăși.
  - Fără `porneste_din`, totul e ca înainte.
- **Ce se vede în fișă.** O fișă judecată astfel are `fata_de_pornire`, iar motivul pomenește modelul de pornire.
- **Cât s-a schimbat.** 30 de rânduri în `kronos/config.py` și `kronos/orchestrator.py`, cu 10 teste noi
  (`teste/test_porneste_din.py`). Toate testele vechi trec.
- **Povestea de la final.** Când nicio oră a liniei nu e păstrată, o scrie starea de la final, cu rețeaua construită după
  modelul de pornire. Până acum era nevoie de o oră păstrată.
- **Ce înseamnă pentru diseară.** Prima oră din 7 e păstrată doar dacă val_bpb coboară sub 0,4254 (0,4304 − 0,005), cu
  fapte_noi peste 49 și nota peste 3,67. Altfel, linia merge mai departe fără niciun model păstrat, până când o oră bate
  #262.

### Testele: 36 noi; toată suita, cu placa: 521 trec

- `teste/test_porneste_din.py`: kronos, prima oră judecată față de modelul de pornire, inclusiv cap-coadă cu unealta.
- `teste/test_retentie.py`: retenția R și punctul de plecare în unealta de antrenare lungă.
- `teste/test_reteta_implicita.py`: hrana implicită, configurarea 7 și rulările gândite fără hrană.
- `teste/test_examen_sacru.py`: setul sacru, plus verificarea că nicio parte automată nu-l pomenește.
- `teste/test_continuum_v1.py`: zgomotul doar din experimentele lungi, nota doar pe 40 de povești și R în
  `stare.json`.

Configurările mici din teste spun acum `hrana = ""`. Fără asta, unealta le-ar fi pus hrana implicită, iar fișierul ei
nu există în dosarele de probă.

### Trei lucruri mici, înainte de școala de cod (8 octombrie)

- **CONTINUUM:** pragul notei e 1,0, ca în Kronos (înainte 0,5).
- **Unealta de antrenare lungă:** criteriile din configurarea 7 sunt implicite.
  - Ele sunt: val_bpb principal (prag_zgomot, implicit 0,005), fapte_noi −10 cel mult, nota −1,0 cel mult.
  - Se aplică doar dacă fișierul n-are deloc `[criterii]` și doar pentru examenele date la fiecare oră.
  - Un `[criterii]` gol înseamnă „fără criterii”.
- **Configurările vechi** (1–5 și cele două 6c) au `hrana = ""` și un `[criterii]` gol, ca la o reluare să răspundă la
  aceleași întrebări ca atunci.

## 8–10 octombrie: planul joi–sâmbătă (`docs/PLAN_joi_sambata.md`)

Starea fiecărei faze e la sfârșitul planului, în secțiunea „Stare”.

### Faza 1a: cele trei lecții SANDBOX-7

- **Faptele profesorului le verifică omul.**
  - `docs/fapte_de_verificat.md` are cele 50 de fapte ale hranei, numerotate, în engleză.
  - Traducerea automată o face profesorul, pe placă, vineri dimineață (`python unelte/fapte_de_verificat.py --traduce`).
  - Adrian trimite numerele celor greșite. Doar atunci: `python unelte/fapte_de_verificat.py --aplica 3,17,42`, care
    scrie `date/fapte/fapte_gresite.json`.
  - De atunci, faptele marcate ies din hrana generată de acum înainte. În examene se marchează, dar nu se șterg.
    Fiecare examen de fapte dă și scorul fără ele (`fapte_corecte_fara_gresite`, `fapte_noi_fara_gresite`).
  - Fără fișier, totul merge exact ca înainte.
  - **Verificate de om pe 9 octombrie 2026:** Adrian a citit toate cele 50 de fapte și niciunul nu e greșit.
    - Hrana și examenele rămân neschimbate.
    - `date/fapte/fapte_gresite.json` nu s-a scris, deci mecanismul rămâne inactiv.
- **Biblioteca școlii se curăță după corectitudine** (ramura `kronos-cod`, școala v0.3):
  - la fiecare regresie, fiecare soluție din bibliotecă e mutată pe sarcinile nevăzute de aceeași formă ale nivelului ei;
  - cele care pică ies în `lucru/cod_v03/respinse/curatare_<linie>.jsonl`, cu motivul.
- **Așteptările se scriu înainte de fiecare noapte.**
  - `python unelte/preinregistrare.py --nume noaptea1 --titlu "..."` creează `docs/preinregistrari/<data>_noaptea1.md`:
    întrebarea, așteptările în cifre și ce le-ar infirma.
  - Dimineața, `python unelte/preinregistrare.py --inchide noaptea1` adaugă „Ce a ieșit”, scos din jurnal. Unealta doar
    adaugă: nu schimbă nimic din ce era scris.

### Noaptea 1 (joi ~23:00 → vineri 07:30): CONTINUUM pe bune

- **Ce rulează:** `python -m module.continuum.bucla --config config/continuum.toml --stare lucru/continuum_pe_bune`.
  - Pornește fără `--simuleaza`, ca proces separat.
  - Are jurnalul lui, `lucru/continuum_pe_bune/`, separat de cel al simulării (`lucru/continuum/`).
- **Ce are voie să pornească:** doar `config/laptop_antrenare_lunga_8.toml`, adică 7 ore din cel mai bun model păstrat,
  cu 5% hrană și rata 0,00005 → 0,000005. Nevoia „continuă” o pornește doar dacă:
  - ultima oră a antrenării 7 a câștigat peste 0,005;
  - tendința pe 3 ore e bună.

  Altfel, CONTINUUM spune „saturat”. Nimic nu se forțează.
- **De ce lista albă stă în nevoi, nu în `[linii]`:**
  - `[linii]` îi spune lui CONTINUUM ce linii măsoară și unde e ultimul model păstrat.
  - Dacă acolo ar fi doar antrenarea 8, care încă nu există, n-ar vedea nicio istorie și n-ar ști de unde să continue.
  - De aceea, `[linii]` urmărește liniile adevărate (antrenările lungi și faptele), iar lista albă e în
    `[nevoi.continua] configurari`. `[nevoi.dezvolta]` e goală.
- **O singură antrenare pe noapte:** e permisă doar antrenarea 8, de 7 ore.
- **Plasa de siguranță:** la 00:00, Claude Code verifică dacă a pornit vreo antrenare. Se uită după un proces
  `antrenare_lunga` sau un jurnal de acțiune `…_antrenare.log` în `lucru/continuum_pe_bune/actiuni/`.
  - Dacă nu, pornește de mână Kronos-fapte-zero:
    `python unelte/antrenare_lunga.py --config config/laptop_fapte_zero.toml --ore 7 --inceput "Once upon a time, there was a fearful little dog named Coco"`.
  - Fapte-zero e un model nou, de la zero, cu aceeași arhitectură și același tokenizer. Învață 7 ore pe TinyStories, cu
    5% fapte de la început, și dă aceleași examene în fiecare oră.
  - În jurnalul nopții se notează „CONTINUUM n-a ales”, plus ultimele lui cicluri.
  - Dacă la 00:00 CONTINUUM e în mijlocul unui examen, se așteaptă alegerea lui următoare (cel mult 30 de minute).
- **Dacă CONTINUUM cade în timpul nopții**, antrenarea pornită merge mai departe. Se raportează dimineața.
- **Ziua (07:30–19:00) placa e a școlii.**
  - La 07:30, Claude Code închide procesul CONTINUUM. Ziua, CONTINUUM ar da examene pe placă, adică s-ar bate cu școala.
  - Nu se folosește STOP pentru asta, pentru că STOP ar opri și școala.
  - Butonul STOP (`lucru/STOP`) oprește tot, inclusiv CONTINUUM.

### Antrenarea 7 (8 octombrie, 13:09–21:30): din #262, 8 ore, rata 0,0001 → 0,00001, hrană 5%

| Ora | # | val_bpb | Față de ora dinainte | Decizia | Fapte noi (R față de 59) | Nota profesorului |
|---|---|---|---|---|---|---|
| 1 | 271 | 0,4547 | — | respinsă | 70 (1,19) | 4,08 |
| 2 | 272 | 0,4511 | −0,0036 | respinsă | 61 (1,03) | 4,62 |
| 3 | 273 | 0,4450 | −0,0061 | respinsă | 58 (0,98) | 4,45 |
| 4 | 274 | 0,4411 | −0,0039 | respinsă | 65 (1,10) | 4,97 |
| 5 | 275 | 0,4375 | −0,0035 | respinsă | 62 (1,05) | 4,75 |
| 6 | 276 | 0,4315 | −0,0060 | respinsă | 64 (1,08) | 4,45 |
| 7 | 277 | 0,4276 | −0,0039 | respinsă (câștig +0,0028 sub pragul de 0,005) | 64 (1,08) | 4,70 |
| 8 | 278 | 0,4263 | −0,0013 | respinsă (câștig +0,0041 sub pragul de 0,005) | 64 (1,08) | 4,70 |

- **Faptele se țin:**
  - R = 1,08 la final;
  - setul sacru pe starea de după ora 8: 31 din 50 (#262: 29, #252: 26), o diferență în zgomot (±3,5 pe 50 de
    întrebări).
- **Niciuna din ore nu e păstrată.**
  - Ora 8 bate #262 (0,4304) cu 0,0041, sub pragul de 0,005. Cel mai bun model păstrat rămâne #262.
  - Ultimele două ore au câștigat 0,0039 și 0,0013, deci pentru CONTINUUM poveștile sunt „saturate”.
- **Față de pre-înregistrare:**
  - val_bpb final între 0,420 și 0,430: da (0,4263);
  - R ≥ 0,8: da (1,08);
  - orele 4–8 păstrate: **nu**, nicio oră.
- **Factor de influență mic:** în ora 3 am rulat testele pe procesor (prioritate minimă), iar ora 3 are cu 2% mai puțini
  pași (26.608 față de ~27.100 în celelalte).

### Simularea CONTINUUM v0 (7–8 octombrie), oprită la 21:31

- A rulat din 7 octombrie, 01:46, până pe 8 octombrie, 21:16: 155 de cicluri, toate simulate.
- **108 cicluri:** placa era ocupată de antrenările adevărate, deci doar a observat.
- **47 de cicluri cu placa liberă:**
  - de 28 de ori ar fi ales „continua:povesti”: v0 nu avea încă pragul de câștig al lui v1;
  - de 16 ori n-ar fi pornit nimic: „dezvolta:fapte, nu acum”, ziua;
  - o dată „dezvolta:fapte”, o dată „masoara:fapte”;
  - o dată nimic, pentru că toate configurările potrivite erau încheiate.
- Procesul a fost închis (nu cu STOP); jurnalul lui rămâne în `lucru/continuum/`.

### Noaptea 1, pornirea (8 octombrie, 21:36)

- **Proba la uscat** (`--simuleaza --ca-la 23:05`, placa reală, liberă): ÎNVĂȚARE.
  - Prima alegere: o remăsurare a faptelor pe #262 (zona galbenă: 59 față de 72).
  - Poveștile sunt „saturate”, deci antrenarea 8 nu e cerută.
- **CONTINUUM pe bune** a pornit la 21:36, nu la ~23:00, fiindcă antrenarea 7 s-a terminat la 21:30. Primele cicluri:
  - #1: remăsurarea faptelor pe #262, reușită (59, deci zona galbenă e confirmată);
  - #2: „Nu pornesc nimic: dezvolta:fapte — nicio configurare potrivită”.
- **Plasa de siguranță** rămâne la 00:00.
- **Traducerea faptelor** (`docs/fapte_de_verificat.md`) a făcut-o profesorul pe placă, la 21:34, înainte de pornire.
  - A ieșit slabă: „Birds have feathers” → „Păsări au pălării”.
  - Documentul are de aceea și o traducere a lui Claude Code, pentru citit. Traducerea profesorului rămâne, marcată
    „nu judeca faptele după ea”.
  - Ambele stau în `date/fapte/traduceri.json`.

### Noaptea 1, rezultatul (9 octombrie, 07:30)

Detaliile, cu verdictul, sunt în `docs/preinregistrari/2026-10-08_noaptea1.md` („Ce a ieșit”) și în
`docs/noaptea1_plasa.md`.

**CONTINUUM pe bune** (21:36–07:30, 180 de cicluri, oprit la 07:30 prin închiderea procesului):

| Ciclurile | Ora | Ce a văzut și ce a ales |
|---|---|---|
| #1 | 21:36 | ÎNVĂȚARE, placa liberă. **A ales remasoara:fapte**: zona galbenă, 59 de fapte noi pe #262 față de 72 la #252. Examenul, 6 s, a confirmat 59. |
| #2–#3, #5–#135 | 21:37–00:00 | ÎNVĂȚARE, placa liberă. **„Nu pornesc nimic”**: „dezvolta:fapte” n-are nicio configurare permisă. „continua” nu e cerută: poveștile sunt saturate (+0,0039, +0,0013). |
| #4 | 21:39 | REPAUS: placa ocupată de testele mele. |
| #136–#180 | 00:01–07:21 | REPAUS: placa ocupată de fapte-zero. |

- **Treapta 5: a ales singur: NU.**
  - Fiecare decizie a fost a lui, cu motiv, după regulile scrise.
  - N-a pornit nimic din afara listei albe.
  - Antrenarea nopții a pornit-o însă plasa de siguranță, nu el.
- **Plasa de siguranță:** fapte-zero, pornit de Claude Code la 00:00:27.

**Fapte-zero** (model nou de la zero, 10×512, 5% fapte din prima oră; alături, noaptea 3: aceeași rețetă, fără fapte):

| Ora | # | val_bpb | Noaptea 3 | Diferența | Fapte noi | Nota |
|---|---|---|---|---|---|---|
| 1 | 280 | 0,5834 | 0,5762 | +0,0072 | 43 | 3,42 |
| 2 | 281 | 0,5530 | 0,5501 | +0,0029 | 51 | 3,12 |
| 3 | 282 | 0,5347 | 0,5285 | +0,0062 | 59 | 3,55 |
| 4 | 283 | 0,5133 | 0,5102 | +0,0031 | 66 | 3,55 |
| 5 | 284 | 0,5012 | 0,4941 | +0,0071 | 60 | 3,83 |
| 6 | 285 | 0,4816 | 0,4771 | +0,0045 | 69 | 3,55 |
| 7 | 286 | 0,4686 | 0,4636 | +0,0050 | 65 | 4,03 |

- **Setul sacru pe #286:** 25 din 50 (26 cu sinonime). #252, prin injectare, avea 26; #262 29; antrenarea 7 după ora 8,
  31.
- **Răspunsul nopții (1b): da.**
  - De la zero, cu 5% fapte de la început, modelul ajunge în 7 ore la fapte comparabile cu injectarea: 65 față de 72 pe
    examenul nou (zgomotul e ±13) și 25 față de 26 pe setul sacru.
  - Nu are ce uita, iar costul pe povești e ~0,005 față de aceeași rețetă fără fapte.
  - 7 ore nu ajung însă pentru povești (0,4686 față de 0,4304 la #262). Comparația la ore egale cu injectarea vine
    sâmbătă.
- **Treapta 4, observație:** starea antrenării 7 după ora 8 (#278) are val_bpb 0,4263 ≤ 0,428 și 64 de fapte noi ≥ 60,
  cu hrană, iar pe setul sacru 31/50, cel mai bun. Kronos n-a păstrat-o, pentru că bate #262 cu doar 0,0041, sub
  pragul de 0,005. Ca model păstrat, treapta 4 nu e atinsă.

### Faza 3 (vineri, 9 octombrie): școala v0.3, verdictul și ce știe un model de la zero fără fapte

**Școala de cod v0.3, pilotul** (07:38–09:17, pe ramura `kronos-cod`; detalii în README-ul de acolo și în
`../cyberspace-cod/lucru/cod_v03/raport.md`):
- **0n (numerele 0–99):**
  - B și D l-au trecut în 3 runde (nevăzut 80% și 85%, sacru 75%);
  - A, doar cu abecedarul, nu: cel mai bun nevăzut 65% în 55 de runde.
- **0w (cuvintele):** B și D au picat, cu 0% tot timpul.
  - Modelul repetă cuvintele din exemplele puse în fața lui: „moon” → `"sun"`.
  - Cauza e tokenizer-ul: ` moon` e o singură bucată, iar `"moon"` sunt 4 (`"`, `m`, `oon`, `"`).
- **B și D au mers la fel pe aceleași runde:** ajută exemplele în plus, nu descoperirea.
- **Poveștile:** cel mult 0,4383, sub 0,46.
- **Verdictul: PARCATĂ.**
  - B n-a ajuns la 2A, deci, după plan, școala se reia pe workstation cu un model mai mare și un tokenizer nou.
  - Tokenizer-ul nou nu trebuie să taie nici numerele în cifre, nici cuvintele după ghilimele.
  - Înghețul final e `v03_final`.

**Ce știe un model de la zero fără fapte** (pentru comparația de sâmbătă): aceeași rețetă, aceleași 7 ore, singura
diferență fiind hrana.

| Modelul | val_bpb | Fapte noi (din 150) | Setul sacru (din 50) |
|---|---|---|---|
| Noaptea 3, ora 7 (#225): de la zero, fără fapte | 0,4636 | 34 | 11 |
| Fapte-zero, ora 7 (#286): de la zero, 5% fapte | 0,4686 | 65 | 25 |
| #252: fapte prin injectare (referință) | 0,434 | 72 | 26 |

- 5% fapte de la început aproape dublează faptele (34 → 65) și dublează setul sacru (11 → 25). Costul e +0,005 la
  val_bpb.
- Faptele ajung cât prin injectare: 65 față de 72 (zgomotul e ±13) și 25 față de 26.

### Noaptea 2 (10 octombrie, 02:41–12:11): CONTINUUM cu lista albă „antrenarea 8”; antrenarea 8 → #295, treapta 4

Detaliile sunt în `docs/preinregistrari/2026-10-09_noaptea2.md` (adendum, „Ce a ieșit”, verdict) și în
`docs/noaptea2_plasa.md`.

- **Pornirea întârziată:** vineri, încărcătorul s-a deconectat de 1.732 de ori (09:42–11:01), iar laptopul a dormit
  11:01–02:38. CONTINUUM a pornit la 02:41, nu la 18:45.
- **CONTINUUM:** 41 de cicluri, fără nicio acțiune. **A ales singur: NU**, ca în noaptea 1: tendința e saturată, iar
  „dezvolta” n-are nicio configurare. La 07:30 a fost închis.
- **Plasa de siguranță** a pornit antrenarea 8 la 03:03:30, după 20 de minute de alimentare stabilă.
  - La 09:53, cineva de la laptop i-a închis fereastra.
  - Adrian a ales reluarea, iar orele 7–8 au rulat 10:06–12:11, din starea de după ora 6. De acum, rulările lungi pornesc
    cu fereastra ascunsă.

**Antrenarea 8** (din #262, 8 ore, rata 0,00005 → 0,000005, 5% hrană):

| Ora | # | val_bpb | Decizia | Fapte noi (R) | Nota |
|---|---|---|---|---|---|
| 1 | 288 | 0,4404 | respinsă | 59 (1,00) | 4,55 |
| 2 | 289 | 0,4387 | respinsă | 61 (1,03) | 4,75 |
| 3 | 290 | 0,4372 | respinsă | 67 (1,14) | 4,38 |
| 4 | 291 | 0,4344 | respinsă | 60 (1,02) | 4,70 |
| 5 | 292 | 0,4307 | respinsă | 59 (1,00) | 4,78 |
| 6 | 293 | 0,4281 | respinsă (+0,0023 sub prag) | 63 (1,07) | 4,62 |
| 7 | 294 | 0,4259 | respinsă (+0,0045 sub prag) | 61 (1,03) | 4,17 |
| 8 | **295** | **0,4249** | **păstrată** (+0,0055) | 64 (1,08) | **5,35** |

- **Răspunsul la 1a: da, la limită.** Continuarea cu pași mici mai câștigă +0,0055 în 8 ore și bate repornirea cu rată
  dublă (antrenarea 7: 0,4263).
  - Am greșit în pre-înregistrare: mă așteptam la sub 0,005.
  - Ultimele două ore au adus doar +0,0022 și +0,0010.
- **Setul sacru pe #295:** 30 din 50.
- **Treapta 4 e atinsă de #295:** povești 0,4249 ≤ 0,428, 64 de fapte noi ≥ 60, cu 5% hrană, păstrat de Kronos,
  confirmat pe setul sacru. E și cel mai bun model păstrat la povești (înainte, #257: 0,4281) și la notă (înainte,
  #260: 5,08).

**Bilanțul săptămânii:** `docs/UNDE_AM_AJUNS_2026-10-10.md` (scara, cel mai bun model pe fiecare criteriu, cifrele,
deciziile pentru Adrian).

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
python -m module.continuum.bucla --config config/continuum.toml [--simuleaza] [--cicluri N]   # CONTINUUM
python -m module.continuum.bucla --config config/continuum.toml --jurnal [N]                  # ultimele cicluri
python -m module.continuum.bucla --config config/continuum.toml --simuleaza [--placa-libera] [--stare DOSAR]
python unelte/lant_antrenare.py                                  # fapte, apoi a cincea antrenare (7 octombrie)
python unelte/lant_antrenare.py --plan config/lant_6.toml        # etapele dintr-un plan (noaptea 7–8 octombrie)
python unelte/examen_fapte_nou.py --sacru --experiment N         # setul sacru de fapte: doar manual, nu la selecție
```

## Ce urmează

- **N2–N3:** jurnal și paznic mai bogate (temperatură în fișă, panou cu grafic), examen de contract la înregistrare.
- **N4:** testele noastre proprii în examen; TinyStories.
- **N5:** cercetătorul cu Claude Code, care modifică direct codul modelului, pe ramuri Git.
- **Mai târziu:** WSL2 (Linux în Windows), necesar pentru Unsloth și `torch.compile`; pentru Etapa N1 nu e nevoie.
