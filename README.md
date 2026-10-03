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
| model | `model_ngram` / `model_gpt` | n-gram pe caractere (fără GPU) / GPT mic de la 0 (pe GPU) |
| date | `date_mostra` / `date_fisier` / `date_tinystories` | propoziții generate / un fișier text (Shakespeare) / povești TinyStories (~20 MB) |
| examen | `examen_bpb` | val_bpb pe text nevăzut la antrenare |
| cercetător | `cercetator_aleator` | schimbă câte o setare, pornind de la cea mai bună rețetă |
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
