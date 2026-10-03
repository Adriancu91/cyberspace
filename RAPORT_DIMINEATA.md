# Raport de dimineață

Scris vineri seara, 2 octombrie 2026, în jurul orei 22:00. **Actualizat sâmbătă, 3 octombrie, la 07:30, cu rezultatele finale ale nopții.**

---

## 1. Pe scurt

- ✅ **PyTorch merge pe placa video** (RTX 3060, 6 GB). Toate cele 44 de teste trec.
- ✅ **Rularea de noapte a mers fără nicio eroare:** 0 experimente anulate și 0 opriri ale paznicului.
- 🏁 **S-a oprit singură la 23:51**, după **21 de experimente din 90**. Cercetătorul **încercase deja toate variațiile**
  din jurul celei mai bune rețete. Nu a fost o defecțiune (vezi secțiunea 7, punctul 5).
- 🏆 **Cel mai bun scor: 2,1873** (experimentul #32). Mai mic înseamnă mai bine.
  GPT-ul a pornit de la 2,4347. Cel mai bun model simplu (n-gram) ajunsese la 2,4211.
- ⚠️ Estimarea mea de aseară pentru ora de final (05:30–08:30) a fost greșită. Nu știam că cercetătorul se oprește singur când rămâne fără variante.
  Laptopul a stat pornit, dar fără să lucreze, de la 23:51 până dimineață.

---

## 2. Ce am făcut și la ce oră

**Seara, împreună cu tine:**

| Ora | Ce s-a întâmplat |
| --- | --- |
| 20:4x | **Pașii 1–3:** Python 3.12 și Git erau deja instalate. Am creat mediul `.venv` și am instalat `pytest`. |
| 20:4x | **Pasul 4:** 2 teste picau. Comanda de oprire nu mergea pe Windows din cauza literei „Ș”. Cu acordul tău, am reparat un rând din `kronos/paznic.py` (commit `de9f583`). |
| 20:48 | **Pasul 5:** bucla de probă. Scorul a coborât de la 4,15 la 0,31. |
| 20:49 | **Pasul 6:** Shakespeare cu modelul simplu (n-gram). Scorul a coborât de la 4,82 la 2,42. |
| 20:52–21:13 | **Pasul 7:** am instalat PyTorch 2.14.1 (CUDA 13.2). Windows îl bloca prin Smart App Control. L-ai oprit tu și ai repornit laptopul. |
| 21:24–21:41 | **Pasul 8, testul scurt:** 3 experimente GPT pe placa video. Scorul a coborât de la 2,43 la 2,21. |

**Noaptea, singur, după instrucțiunile tale:**

| Ora | Ce am făcut | Rezultat |
| --- | --- | --- |
| 21:49 | Am oprit repausul și hibernarea cât laptopul stă la încărcător (`powercfg`) | ✅ Verificat: „niciodată”. Laptopul era la priză, 100% |
| 21:50 | `python unelte/verifica_mediu.py` | ✅ PyTorch vede placa, iar calculul de probă a mers |
| 21:50 | `python -m pytest` | ✅ 44 de teste trecute. ⚠️ La final, pytest se împiedică de un fișier vechi din Windows (vezi secțiunea 7, punctul 3) |
| 21:51 | **Decizie:** n-am repetat testul scurt din Pasul 8 | Îl rulasem deja la 21:24–21:41, după repornire, cu același cod și aceeași configurare. A mers fără erori, cu maximum 690 MB de memorie video. Repetarea ar fi încălzit placa încă 17 minute fără nicio informație nouă |
| 21:51:45 | Am pornit rularea de noapte: `python -m kronos ruleaza --config config/laptop_gpt.toml --experimente 90` | ✅ Pornită ca proces separat, prin Windows (WMI), ca să nu depindă de sesiunea Claude Code |
| 21:52 | Am verificat placa | ✅ Lucrează: încărcare ~50%, consum ~88 W, 355 MB de memorie video |
| 21:5x | Am adăugat în `README.md`, la Pasul 7, o notă despre Smart App Control | Ca să nu te mai încurce data viitoare |
| 21:56 | Primul experiment de noapte (#24) s-a terminat | ✅ Rularea mergea, iar procesul era activ |
| ~21:58 | Commit Git cu README-ul și prima versiune a acestui raport (`85d82dc`) | ✅ Apoi m-am oprit, cum ai cerut |
| 22:45 | **Experimentul #32 a găsit cel mai bun scor al nopții: 2,1873** | Rularea mergea singură |
| 23:51 | **Rularea s-a oprit singură:** „am încercat toate variațiile din jurul celei mai bune rețete” | 21 de experimente, 2 păstrate, 0 erori |
| 07:25 | Am verificat rezultatele, la cererea ta | Procesul nu mai rula, iar placa era în repaus (35°C) |
| 07:30 | Am actualizat acest raport și am făcut commit | Fără să schimb configurarea, cum ai cerut |

**Decizie, la commit-ul de aseară:** nu am mai rulat testele înainte de commit. S-au schimbat doar două fișiere text (README și acest raport), iar codul era cel testat la 21:50, cu 44 de teste trecute. În plus, testele ar fi folosit placa video în timpul unui experiment de noapte.

---

## 3. Ce înseamnă scorurile

Scorul se numește **`val_bpb`**. Arată **cât de „surprins” e modelul** de fiecare literă dintr-un text
**pe care nu l-a văzut la antrenare**, adică un fel de examen pe material nou.

- **Mai mic = mai bine.** Un model care ghicește perfect ar avea 0.
- **PĂSTRAT** = schimbarea a făcut modelul mai bun, așa că devine noua rețetă de pornire.
- **respins** = nu a fost mai bun, sau a fost mai bun cu mai puțin decât „pragul de zgomot” (0,005 la GPT).
  Diferențele atât de mici pot fi doar noroc.
- **ANULAT** = experimentul a fost oprit de paznic, de exemplu pentru prea multă memorie video. **Nu a fost niciunul.**
- Scorurile de la Pasul 5 (0,31) nu se pot compara cu cele de la Shakespeare. Acolo textul era generat și foarte ușor.

---

## 4. Tabelul experimentelor

### GPT pe placa video (`python -m kronos jurnal --config config/laptop_gpt.toml`)

| nr | decizie | scor | ce a încercat cercetătorul |
| --- | --- | --- | --- |
| 21 | păstrat | 2,4347 | punctul de plecare (setările din configurare) |
| 22 | păstrat | 2,2090 | rata de învățare 0,001 → 0,0003 |
| 23 | respins | 2,2229 | 4 → 8 straturi |
| *Noaptea începe aici* | | | |
| 24 | respins | 2,2269 | 4 → 6 straturi |
| 25 | respins | 2,2320 | context 128 → 64 |
| 26 | respins | 2,4025 | rata de învățare 0,0003 → 0,0006 |
| 27 | respins | 2,3302 | lot 32 → 64 |
| 28 | **păstrat** | **2,1973** | 4 → **2** straturi |
| 29 | respins | 2,2236 | rata de învățare 0,0003 → 0,002 |
| 30 | respins | 2,3571 | `n_emb` 128 → 256 |
| 31 | respins | 2,2629 | rata de învățare 0,0003 → 0,001 |
| 32 | **păstrat** | **2,1873** 🏆 | lot 32 → **16** |
| 33 | respins | 2,2219 | context 128 → 64 |
| 34 | respins | 2,2057 | 2 → 6 straturi |
| 35 | respins | 2,1944 | 2 → 4 straturi |
| 36 | respins | 2,2196 | `n_emb` 128 → 192 |
| 37 | respins | 2,2244 | lot 16 → 64 |
| 38 | respins | 2,2103 | context 128 → 256 |
| 39 | respins | 2,2361 | `n_emb` 128 → 256 |
| 40 | respins | 2,2028 | rata de învățare 0,0003 → 0,0006 |
| 41 | respins | 2,4115 | `n_emb` 128 → 384 |
| 42 | respins | 2,2252 | 2 → 8 straturi |
| 43 | respins | 2,1881 | rata de învățare 0,0003 → 0,002 |
| 44 | respins | 2,1983 | rata de învățare 0,0003 → 0,001 |

**Numărătoarea:**

| | Toate experimentele GPT (#21–#44) | Doar noaptea (#24–#44) |
| --- | --- | --- |
| Păstrate | 4 | 2 |
| Respinse | 20 | 19 |
| Anulate | 0 | 0 |

**Ce am învățat din tabel:**
- **În 5 minute, modelele mici câștigă.** Cu 2 straturi a fost mai bine decât cu 4, 6 sau 8. Modelele mari nu apucă să învețe destul în timpul ăsta.
- **Loturile mici au ajutat.** Cu lotul 16, modelul a făcut **45.460 de pași** de învățare în 5 minute, aproape dublu față de lotul 32.
- **Descrierile mai bogate ale literelor** (`n_emb` 192, 256, 384) au fost de fiecare dată mai rele.
- #43 (2,1881) a fost foarte aproape de cel mai bun (2,1873), dar diferența era sub pragul de zgomot, deci a fost respins.

### Modelul simplu (n-gram), Pasul 6, ca reper

Cel mai bun scor: **2,4211**. **GPT-ul (2,1873) e clar mai bun.**

---

## 5. Cea mai bună rețetă găsită

**GPT, experimentul #32, scor 2,1873**:

| Setare | Valoare | Ce înseamnă, pe scurt |
| --- | --- | --- |
| `n_straturi` | **2** | câte „etaje” de gândire are modelul |
| `n_capete` | 4 | la câte lucruri deodată poate fi atent |
| `n_emb` | 128 | cât de bogat descrie fiecare literă |
| `context` | 128 | câte litere din urmă vede când ghicește următoarea |
| `lot` | **16** | câte bucăți de text învață deodată |
| `rata_invatare` | 0,0003 | cât de mari sunt „pașii” de învățare (mai mic = mai prudent) |

Modelul are aproximativ **422.000 de parametri**, adică „butoane” reglate la antrenare. E de două ori mai mic decât cel de aseară.
În 5 minute a făcut **45.460 de pași de învățare** și a folosit doar **60 MB** de memorie video.

---

## 6. Text scris de cel mai bun model

Generat dimineață, la 07:2x, cu `python -m kronos scrie --config config/laptop_gpt.toml --inceput "ROMEO:"`, folosind modelul din experimentul #32:

```
ROMEO:
Perhappy peasant out of you;
And, you say, to this with he--

CAPULET:
A most by insticommiss will see much take them
away wishing tongued me to be lords?
For that direct to the people
To remove thee left be emboad;
And I must strange.

FRIAR LAURENCE:
If thou shalt prefer at grinto the people
Cour
```

**Cum îl citești:** pornind de la „ROMEO:”, modelul a continuat cu **Capulet** și **Fratele Laurențiu**, personaje chiar din *Romeo și Julieta*.
A învățat deci ce nume apar împreună. Are versuri scurte, punctuație și cuvinte vechi („thou shalt”), dar încă inventează cuvinte
(„insticommiss”, „emboad”), iar frazele nu au sens. Pentru un model atât de mic, antrenat 5 minute, e normal.

---

## 7. Probleme întâlnite și ce propun

1. **Smart App Control e oprit.** Trebuie să rămână oprit cât timp folosim PyTorch direct în Windows. Antivirusul (Windows Defender) e în continuare pornit.
   *Propunere:* mai târziu, când trecem la WSL2 (Linux în Windows, oricum planificat în README), îl poți reporni.

2. **Placa se încălzește până la 87°C.** Peste noapte, paznicul a făcut **7 pauze de răcire** de câte 2 minute,
   la 22:06, 22:13, 22:21, 22:38, 23:15, 23:22 și 23:34. De fiecare dată placa avea 87°C, deci totul a funcționat cum trebuie.
   Paznicul verifică temperatura doar **între** experimente, nu și în timpul antrenării. Placa are însă propria protecție, care o încetinește singură.
   *Propuneri:* modul **Turbo** al ventilatoarelor (**Fn + F5**) și, eventual, un suport de răcire.
   În planul proiectului (N2–N3) e deja trecută „temperatura în fișă”, adică notarea temperaturii la fiecare experiment.

3. **`python -m pytest` se blochează la final** cu „Access is denied ... pytest-current”.
   **Testele trec toate**, iar blocarea apare abia după ele, la curățenie. Cauza e un fișier-legătură vechi, din **25 septembrie**,
   rămas în dosarul temporar al Windows (`C:\Users\XyZ\AppData\Local\Temp\pytest-of-XyZ\pytest-current`), de la o rulare care nu ține de proiectul nostru.
   Nu l-am șters, pentru că regula pentru noapte a fost să nu șterg fișiere.
   *Propunere:* spune-mi „șterge legătura veche de la pytest” și o fac eu.

4. **Placa lucrează doar cam pe jumătate.** Memoria video a fost de cel mult **220 MB**, la #27, din 5.500 permiși. Încărcarea a fost de ~40–50%.
   Modelul e mic, iar placa așteaptă după restul calculatorului. Deci mai e mult loc pentru modele mai mari.

5. **Rularea s-a oprit după 21 de experimente, nu după 90.** Cercetătorul de acum („aleator”) schimbă câte **o singură setare**
   pornind de la cea mai bună rețetă și alege doar din lista de valori scrisă în `config/laptop_gpt.toml`.
   După 21 de încercări le epuizase pe toate, așa că s-a oprit singur. Asta e comportamentul corect al modulului, nu o defecțiune.
   *Propunere pentru mai târziu, doar cu acordul tău:* lărgim lista de valori, de exemplu lot 8, rata de învățare 0,0002, 1 strat sau 3 straturi,
   sau trecem la cercetătorul mai deștept din etapa N5. **N-am schimbat nimic acum**, cum ai cerut.

6. **Git nu știe încă numele tău.** Commit-urile se fac sub numele „Claude”, cum ai cerut.
   Dacă vrei să apară numele tău: `git config --global user.name "Numele Tău"` și `git config --global user.email "adresa ta"`.

7. **Setările de repaus au rămas pe „niciodată”** la încărcător. Nu am notat valorile dinainte.
   Dacă vrei ca laptopul să adoarmă iar singur la priză, de exemplu după 30 de minute: `powercfg /change standby-timeout-ac 30`.

---

## 8. Cum vezi singur rezultatele

Deschide VS Code în folderul `cyberspace`, apoi un terminal (**Ctrl+`**) și rulează pe rând:

**a) Activează mediul** (linia trebuie să înceapă cu `(.venv)`):
```
.venv\Scripts\activate
```

**b) Tabelul cu toate experimentele GPT:**
```
python -m kronos jurnal --config config/laptop_gpt.toml
```

**c) Textul scris de cel mai bun model:**
```
python -m kronos scrie --config config/laptop_gpt.toml --inceput "ROMEO:"
```

**d) Ultimele rânduri din jurnalul de noapte**, unde se vede de ce s-a oprit:
```
Get-Content lucru\noapte.log -Tail 5 -Encoding UTF8
```

**e) O rulare nouă, mai târziu.** Cu lista de valori de acum, cercetătorul s-ar opri imediat, pentru că a încercat deja tot.
Are sens doar după ce lărgim lista (punctul 5 din secțiunea 7):
```
python -m kronos ruleaza --config config/laptop_gpt.toml --experimente 90
```
Se oprește oricând cu **Ctrl+C**, sau dintr-un alt terminal cu `python -m kronos opreste --config config/laptop_gpt.toml`.
După `opreste`, înainte de rularea următoare: `python -m kronos porneste --config config/laptop_gpt.toml`.
