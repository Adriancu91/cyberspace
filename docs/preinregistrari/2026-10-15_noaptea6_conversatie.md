# Pre-înregistrare: Noaptea 6 (15–16 octombrie): W2-conv. Învață Kronos să răspundă la întrebări simple?

<!-- scrisa: 2026-10-15T08:28:53 -->
*Scrisă la 2026-10-15 08:28, înainte de rulare. După ce rularea a început, textul de mai jos nu se mai schimbă; la închidere
se adaugă doar secțiunea „Ce a ieșit” (python unelte/preinregistrare.py --inchide noaptea6_conversatie).*

## Cine a ales

**Alegerea de azi și de la noapte e a lui Adrian, nu a lui CONTINUUM.** CONTINUUM e pus să doar observe până joi la
07:45 (`config/continuum_ws.toml`, `om_decide_pana_la`); fiecare ciclu din jurnalul lui scrie asta.

## Întrebarea

**Învață Kronos să răspundă la întrebări simple, în română și engleză, fără să uite ce știa?** Linia nouă „w2_conv”
pornește dintr-o copie a lui #353 (W2 după 20 de ore, răcită) și învață 3 ore pe perechi întrebare → răspuns scrise de
profesor.

## Datele (scrise ziua, 08:15–18:20, de profesor; `unelte/genereaza_conversatie.py`)

- Perechi întrebare → răspuns, ~80% română, ~20% engleză: întrebări de zi cu zi și explicații scurte (80 de teme),
  întrebări despre faptele hranei (doar cele nemarcate greșite) și câteva sute de „nu știu” (răspunsul: „Nu știu
  sigur.” / „I don't know for sure.”).
- Profesorul notează fiecare pereche 1–10 (adevărul și limba); rămân cele cu cel puțin 8. Se scot și întrebările repetate
  și orice pereche cu 8 cuvinte la rând din examenul de fapte nou, setul sacru sau validări.
- **300 de perechi puse deoparte ca examen de conversație nevăzut**, dintre care 30 „nu știu”. Restul, pentru antrenare.
- **De știut, văzut dimineață la probă:** româna profesorului (Qwen3-4B) e slabă. Cu notarea strictă, rămân ~50% din
  perechi, dar trec și unele cu greșeli (ex. „Ce este vară?”, „temperaturi frisoase”). Adrian verifică 30 de perechi
  (`docs/conversatie_de_verificat.md`) **după** noapte: antrenarea de la noapte se face înainte de verificarea omului.
- Același profesor scrie datele și notează examenul: nota lui e un examen cu limite (nu un om).

## Ce rulează

- `config/conv_w2.toml`, linia „w2_conv”, **3 ore**, pornită de Windows la 19:00 (`unelte/noapte_conversatie.ps1`).
- **Antrenare doar pe răspunsuri:** din fiecare lot (12 × 512), 75% perechi „Întrebare: … / Răspuns: …”, cu pierderea
  socotită doar pe răspunsuri (`module/model_conversatie.py`); 5% hrană (poveștile cu fapte); 20% amestecul lui W2.
- **Rata 0,0001**, constantă după 100 de pași de încălzire (optimizatorul pornește din nou din #353).
- La fiecare oră: val_bpb, fapte, fapte noi, nota profesorului pe 40 de povești. Kronos păstrează fiecare oră
  (`prag_zgomot = -1`, fără criterii): linia nu se judecă la oră după povești, ci la sfârșit, după pragurile de mai jos.
- **După ora 3, pe ultimul model păstrat:** examenul de conversație (`unelte/examen_conversatie.py`: modelul răspunde
  fără întâmplare, profesorul notează 1–10 față de răspunsul de referință) și examenele de română și cod.
- Apoi, restul nopții, școala de cod (pre-înregistrarea ei, în ramura școlii). Urmărirea plăcii: toată noaptea, pornită
  și oprită de scriptul nopții (`lucru/placa_noapte_2026-10-15.csv`), plus cea a antrenării, pe orele ei.

## Ce înseamnă confirmat sau infirmat (date de Adrian)

- **Confirmat:** pe cele 300 de întrebări nevăzute, nota medie ≥ 5,0 **și** „nu știu” corect pe cel puțin jumătate din
  întrebările de tip „nu știu” (cel puțin 15 din 30).
- **Infirmat:** nota medie < 3,5.
- Între ele: „a început, dar nu ajunge”.
- **Regresia (pe ultimul model):** povești (val_bpb) ≤ 0,47, română ≤ 1,38, cod ≤ 0,78, fapte noi ≥ 65. **Peste oricare
  = linia nu se păstrează** (nu intră în interfață), oricum ar ieși examenul de conversație.
- **Dacă trece** (confirmat și fără regresie): intră în interfață, pe procesor, ca model implicit, cu rândul de sus
  „Răspunde la întrebări simple, în română sau engleză; poate greși.”

## Așteptările mele, în cifre (Claude Code, scrise înainte)

- Nota medie: între 4,0 și 5,5 (forma o învață repede; adevărul răspunsurilor, mai greu, la 98 de milioane de
  parametri). Fără „nu știu”: puțin mai mică.
- „Nu știu” corecte: 20–28 din 30 (forma e foarte regulată). Dar și „nu știu” spus la întrebări care se știu: 5–15%.
- Povești: 0,46–0,47 (#353: 0,4552), deci aproape de prag. Română 1,35–1,40 și cod 0,75–0,80 (#353: 1,349 și 0,753):
  **cel puțin unul dintre ele poate trece de prag**. Fapte noi: 65–80 (#353: 75).
- Viteza ~5,9 pași pe secundă; toată placa sub 6.500 MB; sub 70 °C; nicio oprire.

## Ce ar infirma așteptările

- nota medie peste 6,0 sau sub 3,5;
- poveștile peste 0,48 (amestecul de 20% nu ajunge ca să nu uite);
- „nu știu” la mai mult de 30% din întrebările care se știu (a învățat să se ferească).

## Adendum 1 (scris joi, 15 octombrie, 10:48, înainte de pornire; cerut de Adrian la ~10:40)

- **Profesorul:** rămâne **Qwen3-4B**. Qwen3-8B (Apache 2.0, licența verificată pe fișa oficială, revizia
  `b968826d…`) n-a putut fi încercat azi: rețeta merge cu ~0,4 MB/s spre Hugging Face, deci cei 16,4 GB ar dura ~11
  ore. Descărcarea merge mai departe în fundal, pentru mâine. Comparația 50 + 50 nu s-a făcut.
- **Filtrul de ortografie** (`unelte/ortografie_ro.py`): orice pereche românească cu un cuvânt necunoscut iese.
  - **Dicționarul hunspell ro_RO nu e folosit:** licența lui e GPL-2.0 / LGPL-2.1 / MPL-1.1, nu e pe lista lui Adrian.
    În locul lui: cuvintele care apar de cel puțin 3 ori în Wikipedia și Wikisource în română (date pe care le avem
    deja), 615.020 de forme. Nume proprii (cu literă mare, nu la început de propoziție) și excepții din
    `date/conversatie/exceptii_ortografie.txt` sunt permise.
  - Aplicat și pe perechile deja scrise: **au ieșit 286 din 2.593** (rămân 2.307). Exemple de cuvinte prinse:
    „anturile”, „camelușii”, „magneț”, „păsăre”, „pâina”, „mănâncăm”, „frisoase”, „răcosește”. Scoate și câteva forme
    corecte, dar rare („reciclăm”, „becele”): e preferat așa.
  - **Ce NU prinde:** greșelile de gramatică sau de sens cu cuvinte existente („Ce este vară?”, „ploaia apare des
    iarna”). Pe acestea le vede doar verificarea lui Adrian.
- **Ținta:** 4.000–8.000 de perechi bune (calitatea, nu numărul); generarea se oprește la 8.000 sau la 18:20.
- **Poarta de dinaintea nopții (regula lui Adrian):** la 13:00, 30 de perechi alese la întâmplare după filtru, în
  `docs/conversatie_de_verificat.md`. **Dacă Adrian găsește peste 3 greșite din 30, W2-conv nu pornește** la noapte
  (rămâne doar școala de cod), iar perechile se refac mâine. Scriptul nopții pornește W2-conv doar dacă există
  `lucru/conversatie_aprobata.txt`, scris de Claude Code după răspunsul lui. Fără răspuns: nu pornește.
- Restul pre-înregistrării (rețeta, examenul, pragurile, așteptările) nu se schimbă.

## Adendum 2 (scris joi, 15 octombrie, 11:10, înainte de pornire): Qwen3-8B față de Qwen3-4B

- Descărcarea lui Qwen3-8B s-a terminat totuși la 11:05 (rețeaua s-a îndreptat). Comparația cerută de Adrian s-a
  făcut: aceleași 10 cereri românești „zi” (aceleași teme), câte 50 de perechi, fără filtre. Perechile:
  `docs/conversatie/comparatie_qwen3_8b.json` și `comparatie_qwen3_4b.json`.
- **Greșelile, numărate de Claude Code** (o pereche e greșită dacă are o greșeală de română sau un lucru fals ori
  fără sens): **Qwen3-8B: ~40 din 50; Qwen3-4B: ~30 din 50.** La 8B: „Ce este păsăre?”, „mânâncă”, „Se se cade pe
  spate”, „Înțepă aerul”, „plăcintă” în loc de placă dentară. La 4B: „un jucărie”, „a zboara”, „vaselor sanguine”,
  „pătrunjel de foc”.
- Qwen3-8B în 4 biți, cu lotul de 8: 6.624 MB la paznic, dar **7.533 MB pe toată placa**.
- **Rămâne Qwen3-4B**, cum a hotărât Adrian pentru cazul în care 8B e mai slab.
- **Cât curăță filtrele:** pe cele 50 de perechi ale lui 4B, nota ≥ 8 și ortografia lasă să treacă 18, dintre care
  **10 sunt tot greșite** (după Claude Code). Deci e foarte probabil ca la verificarea de la 13:00 să fie peste 3
  greșite din 30, iar W2-conv să nu pornească la noapte.

## Adendum 3 (scris joi, 15 octombrie, 11:18, înainte de orice antrenare): rezultat negativ și surse noi pentru română

- **Rezultat negativ, notat ca atare:** profesorul Qwen nu scrie o română destul de bună pentru Kronos. Qwen3-8B (~40
  de perechi greșite din 50) e mai slab decât Qwen3-4B (~30 din 50), iar filtrele (nota și ortografia) nu ajung: din
  perechile lui 4B care le trec, ~10 din 18 sunt tot greșite (Adendumul 2).
- **Hotărârea lui Adrian (~11:15):** nu luăm româna liberă de la Qwen, nici de la 4B, nici de la 8B.
  - Generarea în română a lui Qwen e oprită: de acum scrie doar în engleză (`--doar-engleza`).
  - Perechile lui românești „zi” și „nu știu” deja scrise ies toate (**1.479**). Rămân perechile lui în engleză și cele
    despre fapte (în română și engleză).
- **Sursele noi pentru română:**
  1. **Wikipedia în română** (o avem în `date/ws/`): perechi „Ce este X?” / „Cine a fost X?” / „Unde se află X?”;
     răspunsul = primele 1–3 propoziții ale articolului, scrise de oameni. Doar articole cu început curat; niciun
     articol din validări sau din examene. Ținta: 5.000–10.000. Atribuire CC BY-SA în `docs/DATE_surse.md`.
  2. **Traducere:** perechile lui Qwen în engleză (deja notate ≥ 8), traduse în română de Helsinki-NLP/opus-mt-en-ro
     (licența pe fișa lui: Apache 2.0; revizia `96e8fea9…`), pe procesor. Ținta: 2.000–4.000.
  3. Câteva sute de „Nu știu sigur.” în română, scrise de Claude Code (șabloane scurte, verificate).
  4. Filtrul de ortografie pe toate perechile românești.
- **Fișa pentru Adrian: la 16:00** (nu la 13:00): 30 de perechi românești la întâmplare, 15 din Wikipedia și 15 din
  traducere. Regula rămâne: peste 3 greșite din 30 → W2-conv nu pornește la noapte.
- Proporția română / engleză nu mai e fixată la 80 / 20: iese din câte perechi bune dă fiecare sursă (se raportează).
- Restul pre-înregistrării (rețeta, examenul, pragurile, așteptările) nu se schimbă. Examenul de 300 se ia din același
  amestec de surse; o pereche tradusă și originalul ei englezesc nu se despart între examen și antrenare.
