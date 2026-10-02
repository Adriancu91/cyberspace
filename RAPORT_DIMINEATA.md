# Raport de dimineață

Scris vineri seara, 2 octombrie 2026, în jurul orei 22:00, după ce ai plecat la culcare.
Rularea de noapte a continuat singură după ce am scris raportul. Rezultatele finale le vezi cu comenzile din secțiunea 8.

---

## 1. Pe scurt

- ✅ **PyTorch merge pe placa video** (RTX 3060, 6 GB).
- ✅ **Toate cele 44 de teste trec.**
- ✅ **Rularea de noapte a pornit la 21:51**: 90 de experimente cu GPT-ul nostru, fiecare cu 5 minute de antrenare.
  Rulează ca proces separat, ascuns, și scrie totul în `lucru\noapte.log`.
- 🏆 **Cel mai bun scor la ora raportului: 2,2090** (experimentul #22). Mai mic înseamnă mai bine.
  Scorul de plecare al GPT-ului a fost 2,4347.
- ⏰ **Estimare de final: între 05:30 și 08:30.** Depinde de câte pauze de răcire face placa.

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
| 21:56 | Primul experiment de noapte (#24) s-a terminat | ✅ Rularea merge: `lucru\noapte.log` crește, iar procesul e activ. Placa avea 77°C, deci n-a fost nevoie de pauză. #24 a fost respins (vezi tabelul) |
| ~21:58 | Commit Git cu README-ul și acest raport (fără folderul `lucru/`) | ✅ Apoi m-am oprit, cum ai cerut. Rularea continuă singură |

**Decizie:** înainte de commit n-am mai rulat testele. S-au schimbat doar două fișiere text (README și acest raport), iar codul a rămas cel testat la 21:50, cu 44 de teste trecute. În plus, testele ar fi folosit placa video în timpul unui experiment de noapte și i-ar fi încurcat măsurătorile.

---

## 3. Ce înseamnă scorurile

Scorul se numește **`val_bpb`**. Arată **cât de „surprins” e modelul** de fiecare literă dintr-un text
**pe care nu l-a văzut la antrenare**, adică un fel de examen pe material nou.

- **Mai mic = mai bine.** Un model care ghicește perfect ar avea 0.
- **PĂSTRAT** = schimbarea a făcut modelul mai bun, așa că devine noua rețetă de pornire.
- **respins** = nu a fost mai bun, sau a fost mai bun cu mai puțin decât „pragul de zgomot” (0,005 la GPT).
  Diferențele atât de mici pot fi doar noroc.
- Scorurile de la Pasul 5 (0,31) nu se pot compara cu cele de la Shakespeare. Acolo textul era generat și foarte ușor.

---

## 4. Tabelul experimentelor

### GPT pe placa video (`python -m kronos jurnal --config config/laptop_gpt.toml`)

Acestea sunt experimentele terminate la ora raportului. Cele de noapte se adaugă pe rând.

| nr | decizie | scor | ce a încercat cercetătorul |
| --- | --- | --- | --- |
| 21 | păstrat | 2,4347 | punctul de plecare (setările din configurare) |
| 22 | **păstrat** | **2,2090** | învață cu pași mai mici: rata de învățare 0,001 → 0,0003 |
| 23 | respins | 2,2229 | model de două ori mai adânc: 4 → 8 straturi |
| 24 | respins | 2,2269 | primul experiment de noapte: 4 → 6 straturi |

Nici modelele mai adânci (6 sau 8 straturi) n-au ieșit mai bune în 5 minute. Probabil n-au apucat să învețe destul în timpul ăsta.

### Modelul simplu (n-gram), Pasul 6, ca reper

Cel mai bun scor: **2,4211**. Modelul ghicește fiecare literă după ultimele 5 litere, cu „netezire” 2,0.
**GPT-ul (2,2090) e deja mai bun decât el.**

---

## 5. Cea mai bună rețetă găsită până acum

**GPT, experimentul #22, scor 2,2090**:

| Setare | Valoare | Ce înseamnă, pe scurt |
| --- | --- | --- |
| `n_straturi` | 4 | câte „etaje” de gândire are modelul |
| `n_capete` | 4 | la câte lucruri deodată poate fi atent |
| `n_emb` | 128 | cât de bogat descrie fiecare literă |
| `context` | 128 | câte litere din urmă vede când ghicește următoarea |
| `lot` | 32 | câte bucăți de text învață deodată |
| `rata_invatare` | 0,0003 | cât de mari sunt „pașii” de învățare (mai mic = mai prudent) |

Modelul are aproximativ **818.000 de parametri**, adică „butoane” reglate la antrenare. În 5 minute a făcut
**24.308 pași de învățare** și a folosit doar **138 MB** de memorie video.

---

## 6. Text scris de cel mai bun model

Generat la 21:41 cu `python -m kronos scrie --config config/laptop_gpt.toml --inceput "ROMEO:"`,
cu modelul din experimentul #22. Nu l-am generat din nou în timpul nopții, ca să nu încurc antrenarea de pe placa video.

```
ROMEO:
So he may, was not senced.

DUCHESS OF YORK:
Marry, by the grace; 'tis some name in that
And be letters: partly than tah, that is yon,
With well bear more of the realm; doth them by, to owe
And beg the late templiyy regarements
That we say there from they shall surrieve
with me honour, how could Jo
```

**Cum îl citești:** față de modelul simplu, are mai multe cuvinte reale și bucăți de frază care sună a Shakespeare
(„Marry, by the grace; 'tis some name”). Folosește și un personaj real din piese, Ducesa de York.
Încă inventează cuvinte („templiyy regarements”). Dacă rularea de noapte găsește un scor mai bun,
textul de dimineață ar trebui să fie ceva mai bun.

---

## 7. Probleme întâlnite și ce propun

1. **Smart App Control e oprit.** Trebuie să rămână oprit cât timp folosim PyTorch direct în Windows. Antivirusul (Windows Defender) e în continuare pornit.
   *Propunere:* mai târziu, când trecem la WSL2 (Linux în Windows, oricum planificat în README), îl poți reporni.

2. **Placa se încălzește până la ~87°C.** Paznicul a funcționat: peste 85°C face singur pauze de răcire de 2 minute.
   Pauzele încetinesc rularea, iar o placă fierbinte face puțin mai puțini pași în cele 5 minute, deci scorurile au puțin mai mult „zgomot”.
   Paznicul verifică temperatura doar **între** experimente, nu și în timpul antrenării. Placa are însă propria protecție, care o încetinește singură.
   *Propuneri:* modul **Turbo** al ventilatoarelor (**Fn + F5**) și, eventual, un suport de răcire pentru laptop.
   În planul proiectului (N2–N3) e deja trecută „temperatura în fișă”, adică notarea temperaturii la fiecare experiment.

3. **`python -m pytest` se blochează la final** cu „Access is denied ... pytest-current”.
   **Testele trec toate**, iar blocarea apare abia după ele, la curățenie. Cauza e un fișier-legătură vechi, din **25 septembrie**,
   rămas în dosarul temporar al Windows (`C:\Users\XyZ\AppData\Local\Temp\pytest-of-XyZ\pytest-current`), de la o rulare care nu ține de proiectul nostru.
   Nu l-am șters, pentru că regula ta pentru noapte a fost să nu șterg fișiere.
   *Propunere:* spune-mi „șterge legătura veche de la pytest” și o fac eu. E un fișier temporar și nu afectează nimic altceva.

4. **Placa lucrează doar cam pe jumătate** (~50%). Modelul e mic, iar placa așteaptă după restul calculatorului.
   Nu e o problemă, dar înseamnă că mai e loc de modele mai mari. Va fi treaba cercetătorului în etapele următoare.

5. **Git nu știe încă numele tău.** Commit-urile se fac sub numele „Claude”, cum ai cerut.
   Dacă vrei să apară numele tău: `git config --global user.name "Numele Tău"` și `git config --global user.email "adresa ta"`.

6. **Riscuri pentru noapte, pe care nu le-am putut controla:**
   - Dacă **închizi capacul**, laptopul poate adormi. Nu am putut citi setarea pentru capac.
   - **Windows Update** poate reporni laptopul noaptea.
   În ambele cazuri **nu se pierde nimic**: experimentele terminate rămân în jurnal, iar o rulare nouă pornește de la cea mai bună rețetă.

7. **Setările de repaus.** Nu am notat valorile dinainte. Dacă vrei ca laptopul să adoarmă iar singur la priză,
   de exemplu după 30 de minute: `powercfg /change standby-timeout-ac 30`.

---

## 8. Cum vezi dimineața rezultatele finale

Deschide VS Code în folderul `cyberspace`, apoi un terminal (**Ctrl+`**) și rulează pe rând:

**a) Activează mediul** (linia trebuie să înceapă cu `(.venv)`):
```
.venv\Scripts\activate
```

**b) Verifică dacă rularea s-a terminat.** Comanda arată ultimele 5 rânduri din jurnalul de noapte:
```
Get-Content lucru\noapte.log -Tail 5 -Encoding UTF8
```
- Dacă vezi **`Gata. Experimente: ...`**, rularea s-a terminat.
- Dacă vezi un rând cu **`oprit`**, paznicul a oprit-o. Motivul e scris pe același rând, de exemplu „nu s-a răcit”.
- Dacă ultimul rând e un experiment (`#...`) sau o pauză de răcire, **încă rulează**.

**c) Tabelul cu toate experimentele GPT:**
```
python -m kronos jurnal --config config/laptop_gpt.toml
```

**d) Textul scris de cel mai bun model:**
```
python -m kronos scrie --config config/laptop_gpt.toml --inceput "ROMEO:"
```

**e) Dacă rulează încă și vrei s-o oprești:**
```
python -m kronos opreste --config config/laptop_gpt.toml
```
Termină experimentul în curs, deci mai durează cel mult ~7 minute, apoi se oprește.
**Înainte de următoarea rulare**, ridică semnalul de oprire:
```
python -m kronos porneste --config config/laptop_gpt.toml
```

**Sau, cel mai simplu**, spune-i lui Claude Code:
*„Citește RAPORT_DIMINEATA.md și lucru/noapte.log și spune-mi cum a mers noaptea.”*
