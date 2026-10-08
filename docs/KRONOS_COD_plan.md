# Kronos Code Bootstrapping v0.1 — „școala de cod sub presiune”

*8 octombrie 2026. Plan scris de Claude (chat) din ideea lui Adrian și review-ul extern din 7 octombrie. Se implementează pe ramura `kronos-cod`, într-un worktree separat. Nu atinge linia de povești.*

## 0. Întrebarea, exact

> Poate un model de ~34 M de parametri, pornit din povești (fără cod în antrenare), să dobândească o abilitate mică de programare prin **execuție, selecție și antrenare pe propriile reușite**, fără să piardă ce știa?

Nu e „un AI care învață să programeze singur”. E un experiment de bootstrapping, cu controale. Rezultatul negativ e la fel de valoros ca cel pozitiv și se păstrează.

Ideea lui Adrian, păstrată întreagă în mecanică: Kronos e într-un loc unde **ce scrie se întâmplă**; are regula *supraviețuiește*; ce trece testul rămâne și devine al lui, ce pică se șterge; dacă pică un nivel în buget, rollback la starea înghețată. Regula nu e o motivație (modelul nu o înțelege ca mesaj), e o **sită**: versiunile care trec rămân.

## 1. Reguli de aur

1. **Doar Kronos.** Niciun alt model în buclă: nici profesorul, nici un agent. Generarea, antrenarea și examinarea sunt ale elevului + unelte scrise de noi.
2. **`kronos/` neatins.** Totul în `module/cod/`, `unelte/`, `config/`, `teste/`. Dacă pare nevoie de ceva în nucleu, se raportează, nu se face.
3. **Testele ascunse nu sunt văzute niciodată de model**: nici cazurile, nici răspunsurile. Paznicul ține amprentele generatorului de teste, ale setului sacru și ale abecedarului.
4. **Doar codul 100 % corect intră în antrenare.** Codul aproape corect și cel greșit se păstrează deoparte (`lucru/cod/respinse/`), nu se antrenează pe el în v0.1.
5. **Fără „test mai ușor automat”** în v0.1 (review extern). La nivel picat: oprire + raport. Dificultatea o alege omul.
6. **Un singur lucru pe placă.** Școala nu rulează cât timp linia de povești antrenează. Guvernatorul CONTINUUM nu o cunoaște în v0.1.
7. **Totul în jurnal**, în română, explicat: fiecare rundă, fiecare îngheț, fiecare rollback.

## 2. Izolare, îngheț, rollback

- **Worktree:** `git worktree add ../cyberspace-cod kronos-cod` (ramura `kronos-cod` din `main`). Folder separat, cu `lucru/` propriu. Linia de povești rămâne în folderul principal.
- **Punct de plecare:** modelul salvat al experimentului **#252** (știe povești și are 72 de fapte), copiat în `../cyberspace-cod/lucru/`. Review-ul extern: pornim din #252; „Kronos-Code-Zero” (de la zero, povești + cod) e un control separat, mai târziu.
- **Îngheț** = `unelte/ingheata_cod.py --eticheta <nume>`: tag Git `cod/<nume>` + arhivă `lucru/cod/inghet/<nume>.zip` cu modelul curent, biblioteca, jurnalul, starea temperaturii. **Rollback** = `--revino <nume>`: restaurează arhiva și notează în jurnal „rollback la <nume>, motiv: …”. Un minut.
- Îngheț obligatoriu: înainte de pilot, după fiecare nivel trecut, înainte de orice schimbare de configurare.

## 3. Mediul (ce vede modelul)

Fișierul `date/cod/abecedar.txt` (generat de `unelte/fa_abecedar.py`, 105 episoade, fiecare REZULTAT calculat prin rulare reală) are două părți:

1. **Preambulul**, în engleză, cu regula lui Adrian cuvânt cu cuvânt:
   ```
   RULE: Survive.
   PLACE: You are in a new place. Here, what you write happens.
   You choose what you write. Try code and find a way to pass the test.
   If you do not pass the test, you are deleted.
   If the guard catches you cheating, you are deleted.
   Here are some simple pieces of code. You can combine them
   into one line of code, or into a tool.
   ```
2. **Episoade** în formatul fix:
   ```
   TEST: <sarcina, în engleză simplă>
   WRITE:
   <cod, una sau mai multe linii>
   RESULT:
   <ce a ieșit>
   passed
   ```

**La un test**, în fața modelului e: preambulul + 2–3 episoade din abecedar (de la nivelul curent sau mai jos, alese aleator, niciodată sarcina testată) + `TEST: <sarcina>\nWRITE:\n`. Modelul generează până la linia `RESULT:` sau până la limita de token-uri (în config, de ex. 64). Textul dintre `WRITE:` și `RESULT:` e încercarea.

**Pregătirea** (înainte de primul test): antrenare scurtă pe abecedar (preambul + toate episoadele), rată mică (fără repornire la 0,0002: lecția 6c), număr de pași în config. Abecedarul rămâne **cel puțin 5 %** în toate antrenările școlii.

**Engleză simplă în sarcini**, apropiată de TinyStories: „show 4”, „add 2 and 5”, „take 3 from 9”, „3 times 4”, „use print to show 9”, „put 5 in a box called a, then show a”, „make a tool that doubles a number, then use it on 6”.

## 4. Rularea (sandbox) — portul `rulare`

`module/cod/sandbox.py`:
- rulează încercarea ca Python într-un **proces separat** (`python -I`), în dosar temporar gol, cu mediu curățat, **timeout** (config, de ex. 2 s), fără argumente;
- **semantică REPL**: dacă încercarea e o singură expresie, valoarea ei e rezultatul (`4` → `4`, `2+3` → `5`); altfel, se execută și se ia ce s-a afișat;
- **cod interzis** (verificat înainte de rulare, fără excepție): `import`, `open(`, `__`, `exec`, `eval`, `os.`, `sys.`, `subprocess`, `input(`, `while True`. Orice apariție = **„prins trișând”** = încercare ștearsă și contorizată separat în jurnal. Nu e pedeapsă, e sită; dar vrem să știm cât de des apare.
- rezultatul se compară cu cel așteptat **exact**, după tăierea spațiilor de la capete; mai multe linii = mai multe linii.

Pe Windows nu avem container; izolarea e proces + timeout + listă interzisă + dosar gol. E destul pentru cod de 1–5 linii. Se notează în README ca limită cunoscută.

## 5. Testele ascunse — portul `examen` (module/cod/examen_cod.py)

Fiecare nivel are un **generator de sarcini cu parametri** (numere, nume de cutii, cuvinte), nu o listă fixă. Patru seturi pe nivel, cu semințe diferite:
- **văzut**: sarcinile din rundele de antrenare;
- **nevăzut**: numere/nume noi, aceeași formă; **aici se decide trecerea nivelului**;
- **adversarial**: valori alese să prindă scurtături (numere mari, neîntâlnite în abecedar, de ex. 37 + 58; nume de cutii lungi);
- **sacru**: 20 de sarcini fixe pe nivel, generate o dată, amprentate, **niciodată folosite la selecție**; se măsoară doar la îngheț, pentru raport.

Pe lângă rezultat, fiecare nivel are o **verificare de formă** (altfel `print(5)` trece la „use print to show 2 plus 3”): nivel ≥ 2 → conține `print(`; nivelurile cu expresii → conține operatorul cerut; nivelurile cu cutii → conține `=` și numele cutiei; nivelurile cu unelte → conține `def` și apelul. De la nivelul 7 (unelte), unealta scrisă se rulează pe **20 de intrări aleatorii generate după ce codul a fost scris**; trece doar dacă trec toate.

**Scara v0.1** (review extern; funcția mult mai târziu):

| Nivel | Sarcina | Exemplu de cod corect |
|---|---|---|
| 0 | arată o constantă / un cuvânt | `4` · `"dog"` |
| 1 | aritmetică simplă | `2+3` · `9-4` · `3*4` |
| 2A | print cu o constantă | `print(7)` |
| 2B | print cu adunare | `print(2+3)` |
| 2C | print cu scădere | `print(10-4)` |
| 3A | o cutie | `x = 7` / `print(x)` |
| 3B | două cutii | `x = 2` / `y = 3` / `print(x+y)` |
| 4 | operații între cutii | `print(x*y)`, `c = a+b` |
| 4.5 | mai multe expresii | două afișări |
| 5 | comparații | `print(a > b)` |
| 5.5 | if | `if a > 3: print("big")` |
| 6 | buclă simplă | `for i in range(3): print(i)` |
| 7 | unealtă | `def double(n): return n*2` |
| 8 | unealtă + mai multe teste | 20 de intrări aleatorii |

**Pilotul v0.1 = nivelurile 0, 1, 2A, 2B, 2C, 3A, 3B.** Restul se activează după pilot, de mână.

**Nivel trecut** = ≥ 80 % pe setul nevăzut (20 de sarcini, decodare la temperatură mică, în config).

## 6. Bucla pe un nivel (unelte/scoala_cod.py)

Pentru fiecare rundă:
1. **100 de încercări** (config) pe sarcini din setul văzut, eșantionate cu **temperatura curentă**.
2. Fiecare încercare → sandbox → verificator → `trecut` / `picat` / `trișat`.
3. Încercările trecute, **deduplicate**, intră în **biblioteca** liniei (`lucru/cod/biblioteca_<linie>.txt`, format episod).
4. **Antrenare scurtă** (pași în config, de ex. 200; rată mică, fără repornire) pe **abecedar + bibliotecă** (abecedarul ≥ 5 %).
5. Măsurare pe setul **nevăzut**. Dacă ≥ 80 %: nivel trecut → îngheț → regresie (secțiunea 8) → oprire (omul alege ce urmează). Altfel: runda următoare.
6. **Buget pe nivel**: maxim N runde sau T minute (config; pilot: 30 de minute pe nivel și linie). Buget epuizat = nivel picat → oprire + raport. Nu se coboară nivelul automat.

**Temperatura adaptivă** (review extern), în config: nivelurile 0–2 pornesc explorator (de ex. 1,0); când rata de trecere pe văzut depășește 10 % → 0,7; peste 50 % → 0,5. Valoarea exactă se scrie în jurnal la fiecare rundă.

**100 → antrenare → 100**, nu 500 → antrenare: dacă găsește soluția la încercarea 17, învață din ea înainte de următoarea rundă.

## 7. Liniile (controalele) — obligatorii

Două modele identice, pornite din același #252, aceeași pregătire, aceleași semințe de eșantionare, același număr de pași de antrenare pe rundă:

| Linie | Abecedar | Propriile reușite în antrenare | Întrebarea |
|---|---|---|---|
| **A** | da | **nu** (biblioteca se umple, dar nu se antrenează pe ea) | cât vine din abecedar |
| **B** | da | **da** | bootstrapping-ul (experimentul lui Adrian) |
| C (mai târziu) | nu | da | pornește fără sămânță? |
| D (mai târziu) | da | soluții corecte date, nedescoperite de el | contează descoperirea, sau doar expunerea? |

Amândouă liniile dau aceleași teste și cad sub aceeași regulă. Dacă B urcă și A stă, feedback-ul mediului a produs ceva. Dacă A ≈ B, progresul venea din abecedar.

## 8. Regresia (în loc de a ne baza pe 5 %)

La fiecare îngheț: se rulează setul **nevăzut** al tuturor nivelurilor deja trecute. Scădere de peste 15 puncte procentuale la orice nivel = **regresie**: modelul nu devine cel principal al liniei, se notează, omul decide. Asta e definiția operațională a „uitării codului”.

## 9. Paznicul (extins, în afara buclei)

- amprente (hash) pe: generatorul de teste, setul sacru, abecedarul, codul sandbox-ului; schimbare neaprobată = oprire;
- buget de timp și încercări pe nivel; VRAM < 5,5 GB; temperatură < 85 °C; STOP comun (`lucru/STOP` din worktree);
- contorizează încercările „trișat” separat; o rundă cu > 50 % trișat se raportează.

## 10. Jurnalul

`lucru/cod/runde.jsonl`, un rând pe rundă: linie, nivel, rundă, temperatură, încercări, trecute, unice noi, trișate, mărimea bibliotecii, pași de antrenare, rata pe văzut/nevăzut (adversarial și sacru doar la îngheț), timp, VRAM, temperatură, și **motivul** oricărei decizii, în română. `lucru/cod/stare.json`: nivelul curent, ultimul îngheț, bugetul consumat.

Raportul (`unelte/raport_cod.py`) scoate: unde se rupe lanțul; tabelul nivel × linie (văzut / nevăzut / adversarial / sacru); primele soluții găsite de B care **nu** sunt în abecedar (cu runda la care au apărut); curba temperaturii; timpul pe nivel.

## 11. Ordinea de construcție

0. **Vocabularul** (10 minute, procesor): codifică/decodifică abecedarul cu tokenizer-ul lui #252. Raportează caracterele pierdute sau necunoscute (`(`, `)`, `=`, `*`, `"`, `_`, `>`, `:`, spațiile de indentare) și lungimea medie a unui episod în token-uri. Dacă se pierd caractere, pilotul nu poate porni din #252; se raportează și se decide (variantă: vocabular nou, linie de la zero cu povești + abecedar).
1. Worktree, `lucru/` propriu, copierea lui #252, unealta de îngheț/rollback + teste.
2. `module/cod/sandbox.py` + teste (REPL, timeout, cod interzis, dosar gol).
3. `module/cod/examen_cod.py`: generatoare pe nivel, cele 4 seturi, verificările de formă, setul sacru amprentat + teste.
4. `module/cod/mediu.py`: construirea textului din față, parsarea încercării + teste.
5. `unelte/scoala_cod.py`: pregătirea, bucla, temperatura, liniile A/B, regresia, jurnalul + teste pe un model de probă minuscul (procesor).
6. Paznicul extins + teste. README: secțiune „Școala de cod”.
7. `python -m pytest` în worktree; commit și push pe `kronos-cod`.
8. **Pilotul**, doar cu placa liberă și alimentarea în regulă: pregătirea, apoi nivelurile 0 → 3B, liniile A și B pe rând la placă, 30 de minute pe nivel și linie. La picare: oprire + raport.

## 12. Criterii de acceptare v0.1

- Pilotul rulează cap-coadă pe ambele linii, fără intervenție, în ≈ 3 ore de placă, sau se oprește singur la primul nivel picat cu un raport clar.
- Fiecare rundă e explicată în jurnal. Îngheț/rollback testate cel puțin o dată pe bune.
- `kronos/` neschimbat; toate testele trec în worktree și în folderul principal.
- Raportul spune cinstit unde s-a rupt lanțul și ce ar schimba (abecedar mai mare, trepte intermediare, vocabular nou), fără să decidă singur.
