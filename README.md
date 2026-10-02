# Platforma AI: nucleu + module

Un AI construit de la 0, pe o platformă cu un **nucleu mic** și **module înlocuibile**.
O buclă de experimente îl face să se îmbunătățească singur: propune o schimbare, antrenează,
dă examen, păstrează doar ce e mai bun și notează totul în jurnal.

Stadiu: **Etapa N1 (scheletul)** e gata și testată, plus primele module reale
(modelul n-gram și GPT-ul nostru). 44 de teste trec.

---

## Ghid pentru prima seară

Totul se face în terminalul din VS Code. Deschide VS Code, apoi:
**File → Open Folder → alege folderul `platforma`**, apoi terminalul cu **Ctrl+`**.

Poți să-i spui lui Claude Code: *„Citește README.md și CLAUDE.md și ghidează-mă pas cu pas, începând cu Pasul 1.”*

> Pune folderul `platforma` undeva simplu, de ex. `C:\Users\<numele tău>\proiecte\platforma`,
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
python -m nucleu ruleaza --config config/proba.toml
python -m nucleu jurnal --config config/proba.toml
```

Vezi pe ecran fiecare experiment: ce s-a propus, scorul (`val_bpb`, **mai mic = mai bine**)
și decizia: `PĂSTRAT`, `respins` sau `ANULAT`.

### Pasul 6 — Shakespeare (≈2 minute)

```
python unelte/descarca_date.py
python -m nucleu ruleaza --config config/laptop.toml --experimente 10
python -m nucleu scrie --config config/laptop.toml --inceput "ROMEO:"
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

### Pasul 8 — GPT-ul nostru pe placa video

Un test scurt, 2 experimente (≈15 minute, 5 minute de antrenare fiecare):

```
python -m nucleu ruleaza --config config/laptop_gpt.toml --experimente 2
```

Dacă merge, îl poți lăsa peste noapte (~12 experimente pe oră):

```
python -m nucleu ruleaza --config config/laptop_gpt.toml --experimente 100
```

Dimineața: `python -m nucleu jurnal --config config/laptop_gpt.toml` și `python -m nucleu scrie --config config/laptop_gpt.toml --inceput "ROMEO:"`.

**Oprire:** `Ctrl+C` în terminal, sau dintr-un al doilea terminal `python -m nucleu opreste --config config/laptop_gpt.toml`
(termină experimentul în curs, apoi se oprește). Pentru a porni din nou: `python -m nucleu porneste --config ...`.
Dacă placa trece de 85°C, platforma face singură pauze de răcire.

### Pasul 9 — Salvarea în Git

```
git init
git add .
git commit -m "Etapa N1: scheletul platformei"
```

---

## Ce e în proiect

| Folder | Ce conține | Cine îl modifică |
| --- | --- | --- |
| `nucleu/` | registru, contracte, configurare, orchestrator, jurnal, paznic | doar tu (cu teste) |
| `module/` | piesele înlocuibile: modele, date, examen, cercetător... | agentul și noi |
| `config/` | ce modul stă pe fiecare port, cu ce setări | noi |
| `teste/`, `teste_contracte/` | testele platformei și examenul fiecărui port | noi |
| `unelte/` | descărcarea datelor, verificarea mediului | noi |
| `lucru/` | jurnalul experimentelor, modelele salvate (se creează singur) | nimeni de mână |

Modulele de acum, pe cele 9 porturi:

| Port | Modul | Ce face |
| --- | --- | --- |
| model | `model_ngram` / `model_gpt` | n-gram pe caractere (fără GPU) / GPT mic de la 0 (pe GPU) |
| date | `date_mostra` / `date_fisier` | propoziții generate / un fișier text (Shakespeare) |
| examen | `examen_bpb` | val_bpb pe text nevăzut la antrenare |
| cercetător | `cercetator_aleator` | schimbă câte o setare, pornind de la cea mai bună rețetă |
| rulare | `rulare_locala` | laptopul: limită de timp, măsoară memoria video |
| stocare | `stocare_disc` | folderul `lucru/stocare` |
| interfață | `interfata_consola` | mesajele din terminal |
| profesor, traducere | module „de jucărie” | respectă contractul, devin reale în fazele următoare |

## Toate comenzile

```
python -m nucleu verifica      --config <fișier>   # se încarcă toate modulele?
python -m nucleu ruleaza       --config <fișier> [--experimente N]
python -m nucleu jurnal        --config <fișier>
python -m nucleu scrie         --config <fișier> --inceput "text" [--lungime 300]
python -m nucleu opreste       --config <fișier>
python -m nucleu porneste      --config <fișier>
python -m nucleu aproba-examen --config <fișier>   # doar după o schimbare făcută de tine în examen
```

## Ce urmează

- **N2–N3:** jurnal și paznic mai bogate (temperatură în fișă, panou cu grafic), examen de contract la înregistrare.
- **N4:** testele noastre proprii în examen; TinyStories.
- **N5:** cercetătorul cu Claude Code, care modifică direct codul modelului, pe ramuri Git.
- **Mai târziu:** WSL2 (Linux în Windows), necesar pentru Unsloth și `torch.compile`; pentru Etapa N1 nu e nevoie.
