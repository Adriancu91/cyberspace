# Cyberspace: Kronos + module

Un AI construit de la 0, pe platforma **Cyberspace**: un nucleu mic, numit **Kronos**, și **module înlocuibile**.
O buclă de experimente îl face să se îmbunătățească singur: propune o schimbare, antrenează,
dă examen, păstrează doar ce e mai bun și notează totul în jurnal.

Stadiu: **Etapa N1 (scheletul)** e gata și testată, plus primele module reale
(modelul n-gram și GPT-ul nostru, care a rulat o noapte pe placa video: cel mai bun scor 2,1873).
**Etapa M1 (memoria ierarhică)** e construită și testată. Ambele comparații (la același timp și la același număr
de pași) arată că memoria, așa cum e acum, strică: ajută la antrenare, dar e mai slabă la examen. 92 de teste trec.

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
| date | `date_mostra` / `date_fisier` | propoziții generate / un fișier text (Shakespeare) |
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
învățat 196.000 de parametri în plus (617.248 față de 421.632). Atenție la zgomot: aceeași rețetă cu aceeași
sămânță a dat 2,1873 azi-noapte și 2,1779 azi, deci diferențele sub ~0,01 nu înseamnă nimic.

**La același număr de pași** (exact 35.000 de pași pentru ambele variante, pe aceleași date, în aceeași ordine):

| Sămânța | Fără memorie | Cu memorie | Diferență | Secunde de antrenare (fără / cu) |
| --- | --- | --- | --- | --- |
| 1337 | **2,1990** | 2,2424 | −0,043 | 239 / 286 |
| 2024 | **2,2055** | 2,2464 | −0,041 | 229 / 285 |
| 7 | **2,1982** | 2,2218 | −0,024 | 245 / 281 |
| media | **2,2009** | 2,2369 | −0,036 | |

Memoria pierde și la număr egal de pași, deci nu doar viteza e de vină: cam 70% din diferența de la comparația
la același timp (0,036 din 0,050) rămâne și când ambele variante fac aceiași pași. Un semn: la antrenare, varianta
cu memorie greșește mai puțin la toate semințele (de ex. 1,755 față de 1,845 biți pe literă, măsurat pe ultimul lot),
dar la examen e mai slabă. Arată a „tocire”: nivelurile adânci ale codului sunt aproape cât cuvântul însuși, iar
modelul le folosește ca să rețină textul de antrenare. Idei de încercat: mai puține niveluri (2–4), cuvintele de
legătură în bibliotecă. Detaliu minor: categoriile nevăzute la antrenare primesc o descriere neantrenată
(0,7% din literele examenului; prea puțin ca să explice diferența, dar de reparat).

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
