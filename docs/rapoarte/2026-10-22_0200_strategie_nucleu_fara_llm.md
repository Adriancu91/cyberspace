# Strategie de cercetare: Kronos ca nucleu AI propriu, fără LLM — reanaliza din 22 octombrie 2026

*Scris de centrul de comandă (Claude), 22 octombrie 2026, 02:00, la cererea lui Adrian, după metoda „OMNI AI ARCHITECT”
(definire → stadiu → idei → modelare → selecție → prototip → experiment → evaluare → evoluție).*
*E o PROPUNERE. Nu schimbă nimic în coadă, în cod sau în date până la „da”-ul lui Adrian. Supraveghetorul nu acționează pe ea.*

Etichete folosite: **FAPT VERIFICAT** (am văzut în repo sau e rezultat publicat cunoscut), **REZULTAT EXPERIMENTAL** (din
jurnalul Kronos), **IPOTEZĂ**, **ESTIMARE**, **NECUNOSCUT**. Literatura o citez din ce știu până în iunie 2026; fiecare
sursă se reverifică cu link înainte să intre într-o pre-înregistrare.

---

## 1. OBIECTIV

Ținta lui Adrian, cuvânt cu cuvânt: *„AI-ul nostru de la 0 (Kronos), fără LLM, la performanțele AI-urilor de top, cu autonomie
de a se autoîmbunătăți și rescrie singur să devină mai bun.”*

Ca să fie măsurabilă, o despart în patru ținte, fiecare cu propria probă:

| # | Ținta | Cum se măsoară | Se poate atinge de la zero, pe hardware-ul nostru? |
|---|---|---|---|
| T1 | **Fără LLM**: nicio inteligență străină în buclă (nici ca nucleu, nici ca profesor, nici ca evaluator) | lista dependențelor = goală | **Da**, dar azi NU e așa (vezi §2, descoperirea 1) |
| T2 | **Autonomie**: Kronos își propune singur îmbunătățiri, le testează, le păstrează sau le aruncă | câte îmbunătățiri acceptate pe săptămână fără om, cu zero regresii | **Da, pe trepte** (§6): întâi date și configurări, mult mai târziu cod |
| T3 | **Se rescrie singur**: Kronos produce cod/programe noi care devin ale lui | mărimea bibliotecii de programe verificate care rezolvă sarcini noi | **Parțial**: programe mici verificate automat, da; „inginer de cod” fără niciun LLM — NECUNOSCUT, nu există precedent |
| T4 | **Performanță de top** | comparație cu cei mai buni pe aceeași probă | **Da, pe domenii cu verificator** (precedent: AlphaZero, FAPT). **Nu**, pe conversație liberă (§2.3) |

Concluzia de sus, pe scurt: drumul există, dar nu trece prin „un model de limbaj mai bun”. Trece prin **domenii cu verificator +
buclă de auto-joc + memorie explicită + specialiști**. Restul raportului argumentează și propune primul experiment.

---

## 2. STAREA ACTUALĂ (ce am verificat în repo la 01:40)

### 2.1 Ce există și e bun (FAPT VERIFICAT)
- Model propriu W2: 12 straturi × 768, context 512, vocabular 16.384 (tokenizer propriu), **98 M parametri**; antrenare ~95 M de
  simboluri pe oră pe RTX 3070 Ti (`docs/MUTARE_workstation.md`). Cel mai bun pe „răspuns din text”: #407 în interfață, #415 cel mai nou.
- Infrastructură: nucleu cu porturi și contracte, paznic cu amprente, pre-înregistrare obligatorie, 851 teste, 24 de module
  în format comun, cascadă supraveghetor + executant, jurnal, rollback. **Asta e cea mai valoroasă parte a proiectului** și se
  refolosește cu orice arhitectură.
- REZULTAT EXPERIMENTAL (noaptea 12, S12): #415 face **50/50** pe întrebări de tipuri văzute, **2/15** pe tipuri nevăzute,
  fără regresie. S15 (examen 50 + 30, în lucru acum) va spune dacă „2/15” e zero sau „puțin”.
- Plan deja scris pe 8 octombrie: `docs/KRONOS_COD_plan.md` — „școala de cod”: execuție, selecție, antrenare pe propriile
  reușite, regula de aur **„Doar Kronos, niciun alt model în buclă”**. Ramura `kronos-cod` **nu există** în repo → planul n-a
  fost implementat (NECUNOSCUT de ce; probabil prioritatea liniei de conversație).

### 2.2 Două descoperiri pe care trebuie să le spun pe față
**Descoperirea 1 — Kronos NU e azi „fără LLM”.** FAPT VERIFICAT:
- `module/profesor_qwen.py`: **Qwen3-4B-Instruct** (model extern, Apache 2.0) e **profesorul**: el notează 1–10 fiecare răspuns
  la examene (`unelte/examen_conversatie.py`, `ProfesorQwen`) și el a generat poveștile cu fapte. Deci toate verdictele
  „corect = nota ≥ 7” din S4, noaptea 10, 11, 12 și S15 sunt **judecata unui LLM străin**. Prompt-ul tău interzice exact asta
  (principiul 3: nu LLM ca evaluator).
- Pre-antrenarea e pe **TinyStories** (engleză), un corpus **generat de GPT-3.5/4** de alții. E date, nu model, dar e
  inteligență străină turnată în Kronos. `docs/DATE_surse.md` are deja alternativa: Wikipedia + Wikisource în română (text scris de oameni).

Nu e o vină — au fost alegeri bune pentru a porni repede. Dar dacă ținta e T1, ele trebuie **declarate și înlocuite**:
profesorul-LLM cu **verificatoare** (pentru „răspuns din text” răspunsul de referință e o bucată din text → potrivire de
cuvinte, fără niciun model; pentru cod → testele; pentru gramatică → motorul de română `verifica_text`), iar poveștile
generate de LLM cu text românesc scris de oameni.

**Descoperirea 2 — auto-îmbunătățirea de azi e Claude.** Cascada funcționează, dar cel care observă limitele, formulează
ipoteze și scrie modificările e Claude (supraveghetor + executant). Prompt-ul cere „fără a ascunde dependența de inteligența
altor modele”: o declar. Planul de mai jos o reduce pe trepte (§6), nu pretinde că dispare mâine.

### 2.3 Limita de calcul (ESTIMARE, cu cifre)
- Workstation: ~1 miliard de simboluri pe noapte de 10 ore la 98 M parametri → ~6 × 10^17 operații pe noapte, ~2 × 10^19 pe lună.
- Modelele „de top” pe conversație liberă: ordinul 10^25 operații la antrenare (FAPT, rapoarte publice 2023–2025) → de
  ~500.000 de ori mai mult decât o lună de workstation, plus date de mii de ori mai multe.
- Nu există nicio arhitectură publicată care să închidă o diferență de 5–6 ordine de mărime pe limbaj deschis (FAPT: nici
  Mamba/SSM, nici RWKV, nici MoE nu dau mai mult de un factor mic la aceeași scară; RETRO dă cel mai mare câștig cunoscut,
  echivalent cu ~25× parametri, prin memorie, nu prin calcul).
- Deci **T4 pe conversație liberă = NU, de la zero, pe acest hardware, cu orice arhitectură cunoscută.** Nu e o problemă de
  metodă, e fizică. Ce rămâne posibil și are precedent: **top pe domenii cu verificator** (AlphaZero a bătut campionii la Go
  și șah pornind de la zero, fără date umane, cu auto-joc; pe un singur GPU același mecanism merge la scară mică).

---

## 3. HARTA PROBLEMELOR FUNDAMENTALE (ce trebuie să rezolve un nucleu autonom)

| Problema | Ce înseamnă pentru Kronos | Unde suntem |
|---|---|---|
| P1 Reprezentarea | cum ține informația înăuntru (simboluri? stări? grafuri?) | simboluri + transformer (convențional, merge) |
| P2 Cunoștințe: în greutăți sau în memorie? | 98 M de parametri nu pot ține lumea; 128 GB RAM pot ține multe documente | totul în greutăți (limitat) |
| P3 Dobândirea abilităților și transferul | de ce 50/50 pe văzut și 2/15 pe nevăzut | **blocajul actual** |
| P4 Verificatorul | cine spune „corect” fără om și fără LLM străin | Qwen (de înlocuit) |
| P5 Bucla de auto-îmbunătățire | ce are voie să se schimbe singur și cine judecă | Claude + paznic + pre-înregistrare |
| P6 Uitarea / regresia | cum adaugi fără să strici | examen „fără regresie” (bun), dar un singur model monolit |
| P7 Economia de calcul | 7 GB VRAM, 128 GB RAM, nopți de 3–10 ore | bine măsurată, dar RAM-ul e nefolosit |
| P8 Măsurarea cinstită | examene nevăzute, pre-înregistrare, scurgeri | foarte bine (cu excepția P4) |

---

## 4. CINCI IPOTEZE ARHITECTURALE DISTINCTE

Pentru fiecare: principiul, ce diferă, de ce ar merge, ce ar infirma-o, costul, cel mai mic experiment, și **ce e cunoscut în
literatură** (metoda cerută la punctul 4 al misiunii: înainte de a numi ceva „al nostru”, caut cea mai apropiată metodă
publicată și o etichetez *principiu cunoscut* / *combinație nouă pentru proiect* / *nou, neverificat*).

### H1 — „Acoperire, nu înțelegere”: proiectarea distribuției de date
- **Principiu:** un model mic învață ce vede (50/50). Atunci îi arătăm **sute** de tipuri de întrebări, generate procedural
  (șabloane + motorul de română + tabele Wikipedia), nu 20.
- **Literatură:** FLAN/T0 (2021–22): generalizarea la sarcini nevăzute crește cu **numărul de sarcini distincte** la antrenare
  (FAPT); TinyStories (2023): modele de 10–30 M fac engleză coerentă dacă distribuția e simplă și curată (FAPT). *Principiu cunoscut.*
- **De ce ar merge:** S12 a mărit **cantitatea** (3.319 întrebări), nu **numărul de tipuri** (~10 noi). FLAN spune că tipurile contează.
- **Ce o infirmă:** 200+ tipuri la antrenare și (b2) pe tipuri nevăzute tot sub 15/50.
- **Cost:** mic (generare pe procesor, o noapte de antrenare). **Experiment minim:** 100 de tipuri noi procedurale, o noapte, examen S15.
- **Tavan:** nu dă „înțelegere”; dă un specialist bun pe documente în română, offline. Util, dar nu T4.

### H2 — „Memoria în loc de parametri”: nucleu mic + memorie explicită mare
- **Principiu:** parametrii țin **abilități**, memoria (RAM, 128 GB) ține **cunoștințe**. Modelul învață să caute și să copieze din
  memorie, nu să memoreze. Un document nou = învățat instant, fără antrenare.
- **Literatură:** RETRO (2021, DeepMind): un model de 7 B cu memorie egalează unul de 175 B (FAPT); kNN-LM (2020); rețele cu memorie.
  *Principiu cunoscut; combinația cu un index propriu pe n-grame, fără niciun model extern, e nouă pentru proiect.*
- **De ce ar merge:** rezolvă P2 și P6 (adaugi fără să reantrenezi, deci fără regresie) și folosește singura resursă mare pe care o avem (RAM).
- **Ce o infirmă:** cu memorie, răspunsul din documente lungi/nevăzute nu depășește modelul fără memorie cu cel puțin 10 puncte.
- **Cost:** mediu (index propriu, antrenare cu context din memorie; VRAM neschimbat). **Experiment minim:** același #415, cu/fără
  paragrafe aduse din index, pe documente de 10× mai lungi decât contextul.

### H3 — „Auto-joc cu verificator”: Kronos își face singur datele și le verifică fără LLM
- **Principiu:** într-un domeniu unde corectitudinea se poate **verifica automat** (răspunsul e o bucată din text; codul trece
  testele; propoziția trece motorul de română; calculul are rezultat), modelul **generează**, verificatorul **cerne**, ce trece
  intră la antrenare, se repetă. Nicio inteligență străină: elevul + unelte scrise de noi.
- **Literatură:** AlphaZero / expert iteration (2017): de la zero la supra-uman, fără date umane, cu auto-joc (FAPT); STaR (2022) și
  „self-play QA / consistență dus-întors” (întrebare → răspuns → trebuie să fie bucata de pornire). *Principiu cunoscut; aplicarea
  la „răspuns din text” în română, cu tipuri de întrebări **născute de model**, e combinație nouă pentru proiect.* E, de fapt,
  **planul lui Adrian din 8 octombrie** (`KRONOS_COD_plan.md`), neimplementat.
- **De ce ar merge:** e singurul mecanism cu precedent pentru T2 și T4 „de la zero”. Pentru blocajul actual (P3): generatorul
  de întrebări, pus să scrie **diversificat** (eșantionare), poate produce forme de întrebări pe care noi nu le-am scris; filtrul
  dus-întors + filtrul de noutate (primele 4 cuvinte nu există în antrenare) rețin doar ce e corect și nou.
- **Ce o infirmă:** după o noapte cu date auto-generate, (b2) nu crește cu cel puțin 10/50 față de #415, sau cresc numai
  parafrazele (tipurile distincte, numărate pe primele 4 cuvinte, sub 20).
- **Cost:** mediu (generare ~1 oră pe placă + o noapte). **Experiment minim:** §8.
- **Risc principal:** generatorul antrenat pe tipuri văzute produce doar variații ale lor. IPOTEZĂ cu probabilitate medie; de asta e primul test.

### H4 — „Specialiști cu activare selectivă”: multe modele mici + un ruter
- **Principiu:** nu un model monolit de 98 M, ci N specialiști mici (fiecare pe o familie de tipuri/sarcini) + un ruter care
  pornește unul singur per întrebare. Capacitatea crește cu RAM-ul (128 GB), nu cu VRAM-ul; un specialist nou = un modul nou
  cu manifest; nu poate strica pe ceilalți (regresie zero prin construcție).
- **Literatură:** Mixture-of-Experts (Switch, 2021); **Branch-Train-Merge** (2022): experți antrenați independent, pe rând, fără
  sincronizare — exact ce permite un singur GPU (FAPT). *Principiu cunoscut; se potrivește perfect filozofiei „nucleu + module”.*
- **Ce o infirmă:** ruterul greșește peste 10 % sau suma specialiștilor nu bate monolitul pe același examen.
- **Cost:** liniar în specialiști; fiecare la 20–30 M parametri → 10 specialiști = o noapte fiecare. **Experiment minim:** 3
  specialiști (fapte, da/nu, tipuri S11) + ruter pe primele cuvinte ale întrebării, examen S4 + S15.

### H5 — „Bibliotecă de programe învățate”: neuro-simbolic
- **Principiu:** o abilitate = un **program** mic (ex. „găsește numele după cuvântul X”). Partea neurală propune programe, un
  executor le rulează pe text, verificatorul le ține pe cele corecte, biblioteca crește și programele se **compun**. Aici „se
  rescrie singur” (T3) înseamnă literal: biblioteca de programe e cod al lui Kronos, verificat.
- **Literatură:** DreamCoder (2021): învață biblioteci de programe reutilizabile pe domenii mici, cu generalizare prin compunere
  (FAPT); AutoML-Zero (2020): algoritmi de învățare evoluați de la zero, extrem de scump (FAPT). *Principiu cunoscut; aplicarea
  la întrebări pe text românesc e nouă, neverificată.*
- **De ce ar merge:** singura dintre cele cinci care promite **generalizare adevărată** la tipuri nevăzute (prin compunere), nu acoperire.
- **Ce o infirmă:** biblioteca nu depășește 30 de programe utile sau nu rezolvă niciun tip nevăzut în 4 săptămâni.
- **Cost:** calcul mic, **inginerie mare** (limbaj de programe, executor, căutare). Dificultate de validare: mare. Pistă de cercetare, nu primul pas.

### Alternative analizate și lăsate deoparte (deocamdată)
- **Învățare fără backpropagation** (Forward-Forward 2022, reguli hebbiene): ESTIMARE — în literatură rămân sub backprop la
  aceeași scară; nicio dovadă că ar închide diferența de calcul. Se reia doar dacă apare o dovadă.
- **Arhitecturi secvențiale noi (Mamba/SSM, RWKV):** FAPT — câștig de viteză la context lung, nu de inteligență per operație. Utile
  mai târziu pentru H2 (context lung), nu acum.
- **Hardware mai mare:** nu e o metodă.

---

## 5. SELECȚIA (criterii explicite)

| Criteriu | H1 | H2 | H3 | H4 | H5 |
|---|---|---|---|---|---|
| Atacă blocajul de azi (P3, tipuri nevăzute) | parțial | nu | **da** | parțial | **da** |
| Duce spre autonomie (T2) | nu | nu | **da** | puțin | da |
| Duce spre „se rescrie singur” (T3) | nu | nu | parțial | nu | **da** |
| Fără LLM (T1) | da | da | da | da | da |
| Încape în 7 GB VRAM / folosește 128 GB RAM | da / nu | da / **da** | da / nu | da / **da** | da / da |
| Testabil în ≤ 1 săptămână | **da** | da | **da** | da | nu |
| Refolosește infrastructura Kronos | da | da | da | **da** | parțial |
| Risc de a nu da nimic | mic | mic | mediu | mic | mare |

**Recomandarea:** nu o singură ipoteză, ci o **coloană vertebrală + un motor**:
- **Motorul = H3** (auto-joc cu verificator): e singurul mecanism cu precedent pentru T2 și T4 de la zero și e ideea lui Adrian din 8 octombrie.
- **Coloana vertebrală = H4 + H2** („nucleu mic, specialiști, memorie mare”): adaugi abilități și cunoștințe fără regresie, folosești RAM-ul.
- **H1 ca disciplină de date** (generare procedurală de tipuri), nu ca strategie.
- **H5 ca pistă de cercetare** după ce H3 dă primul rezultat (peste ~2 luni), pentru T3 adevărat.
- **Două precondiții obligatorii pentru T1:** (a) verificator fără LLM la „răspuns din text” în locul lui Qwen; (b) pre-antrenare
  pe text românesc scris de oameni (Wikipedia + Wikisource, deja listate în `DATE_surse.md`) în locul TinyStories, când vine rândul.

Compromisul asumat: renunțăm la „conversație liberă de top”. Câștigăm un sistem care poate deveni de top pe **documente în
română, cod mic verificat și gramatică**, și care are o buclă reală de auto-îmbunătățire, nu una împrumutată.

---

## 6. ARHITECTURA PROPUSĂ (pe înțeles)

```
            ┌──────────────────────── Nucleul Kronos (există: porturi, contracte, paznic, jurnal) ─────────────────────────┐
            │                                                                                                             │
 întrebare → Ruter → Specialist k (model mic, modul cu manifest) ← Memoria (index propriu peste documente, în RAM) → răspuns
            │                                                                                                             │
            │   Bucla de auto-îmbunătățire (H3):                                                                           │
            │   Generator → candidați → VERIFICATOARE (bucată din text / teste cod / motorul de română / calcul)           │
            │            → filtru de noutate → date noi → specialist-candidat → examen nevăzut → ACCEPT sau ROLLBACK        │
            │   Judecători: numai verificatoare scrise de noi. Niciun LLM.                                                 │
            └─────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Ce are voie să se schimbe singur, pe trepte (autonomia crește prin rezultate, nu prin permisiuni):**
- **L0 (azi):** Claude propune și scrie; paznicul și pre-înregistrarea judecă; Adrian aprobă. *Dependență declarată: Claude.*
- **L1:** Kronos își **propune singur datele** (întrebări, exerciții, tipuri) și le verifică; Claude aprobă doar bugetul nopții.
- **L2:** Kronos rulează singur bucla generare → verificare → antrenare → examen → accept/rollback într-un buget pre-aprobat
  (ore, VRAM, număr de candidați); Claude și Adrian citesc raportul săptămânal. Interzis să atingă: paznicul, testele,
  versionarea, verificatoarele, datele de examen (regula din prompt, §self_development 10).
- **L3:** Kronos produce **programe** (H5) care intră în biblioteca lui după verificare = „se rescrie singur” în sensul verificabil.
- **L4 (inginer de cod fără niciun LLM):** NECUNOSCUT; nu promit un termen. Se reevaluează după L3.

---

## 7. PLANUL ETAPIZAT (fiecare etapă produce un rezultat verificabil înainte de următoarea)

| Etapa | Ce | Durată | Rezultatul care o închide |
|---|---|---|---|
| **E0** Verificatorul fără LLM | notare prin potrivirea răspunsului cu bucata de referință (exactă + suprapunere de cuvinte ≥ 0,8); re-notarea S15 și S4 în ambele feluri | 1–2 zile, procesor | acord Qwen ↔ verificator ≥ 90 % → Qwen iese din examene de „răspuns din text”; dacă < 90 %, analizăm unde diferă înainte de orice |
| **E1** H3-lite: „întrebări născute de Kronos” | experimentul din §8 | 1 săptămână (o noapte pe placă) | criteriile numerice din §8 |
| **E2** H4: 3 specialiști + ruter | antrenați pe rând (BTM), ruter simplu; examen S4 + S15 | 1–2 săptămâni | fără regresie pe niciun specialist; suma ≥ monolit; ruter ≥ 90 % |
| **E3** H2: memoria | index propriu peste Wikipedia ro (procesor + RAM); modelul învață să folosească paragrafele aduse | 2–3 săptămâni | +10 puncte pe documente lungi nevăzute; document nou = răspuns corect fără antrenare |
| **E4** H3 complet pe cod | `KRONOS_COD_plan.md` așa cum e scris (regula „doar Kronos”), cu rollback | 1 lună | nivelurile din plan trecute cu bugetul lor; cod verificat intrat în antrenare |
| **E5** H5: biblioteca de programe | pistă de cercetare | după E4 | ≥ 30 de programe utile; ≥ 1 tip nevăzut rezolvat prin compunere |
| **E6** Pre-antrenare pe română umană | Wikipedia + Wikisource, tokenizer actual | când placa e liberă 2–3 nopți | val_bpb pe text românesc nevăzut sub cel al #415 |

Ordinea E0 → E1 e obligatorie (fără E0, E1 ar fi notată tot de Qwen). E2/E3 pot merge în paralel cu E4 pe procesor.

---

## 8. PRIMUL EXPERIMENT: „Întrebări născute de Kronos” (E1), cu criterii numerice

- **Întrebarea:** poate Kronos, fără niciun model străin, să-și producă întrebări de **tipuri noi** care, intrate la antrenare,
  ridică scorul pe tipuri nevăzute?
- **Baseline:** #415 pe examenul S15: (b2) x/50 și (e) y/30 (valorile vin din raportul S15; dacă S15 nu s-a terminat, DATE INSUFICIENTE, se așteaptă).
- **Pași:**
  1. Generatorul: aceeași arhitectură W2, pornit din #415, antrenat 1 oră pe (text, bucată) → întrebare, din perechile existente.
  2. Generare pe 2.000 de articole puse deoparte pentru antrenare (nu cele de examen; verificat automat), 8 întrebări pe bucată,
     cu eșantionare (temperatură 1,0, nucleu 0,9), ~1 oră pe placă.
  3. Filtre, toate fără LLM: (i) dus-întors: #415 răspunde la întrebare și răspunsul se suprapune ≥ 0,8 cu bucata; (ii) noutate:
     primele 4 cuvinte nu apar ca început de întrebare în nicio antrenare; (iii) fără duplicate; (iv) trece `verifica_text`.
  4. Se păstrează cel mult 3.300 de întrebări (cât S11), ca să fie comparabil cu noaptea 12. Se raportează câte tipuri distincte
     (pe primele 4 cuvinte) au rezultat.
  5. Antrenare 3 ore din #415 (ca noaptea 12), apoi examenele: S15 (b2, e), S4, val_bpb, examenul de 50 de la noaptea 10.
- **Criterii stabilite înainte:**
  - **CONFIRMAT:** (b2) ≥ baseline + 10/50 **și** (e) ≥ baseline − 3/30 **și** fără regresie pe S4 și noaptea 10.
  - **INFIRMAT:** (b2) < baseline + 4/50, sau tipuri distincte generate < 20 → H3-lite în forma asta se abandonează; trecem la E2 și pregătim H5.
  - **Neclar:** între ele → o singură repetare cu 3× date; apoi decizie.
- **Resurse (ESTIMARE):** VRAM ≤ 5,6 GB (bugetul W2); placă ~5 ore în total; procesor pentru filtre ~1 oră; stocare < 100 MB.
- **Ce NU se atinge:** `kronos/`, examenul BPB, datele de examen, paznicul. Totul în `unelte/`, `module/`, `date/conversatie/auto_v1/`.
- **Pre-înregistrare:** obligatorie, cu cifrele de mai sus, înainte de rulare.

---

## 9. RISCURI ȘI LIMITE

- **Generatorul face parafraze, nu tipuri noi** (cel mai probabil mod de eșec al E1): măsurat explicit prin tipurile distincte; dacă se
  întâmplă, H3 rămâne valabil pe cod (E4), unde verificatorul e tare, iar generalizarea pe text o cerem de la H5.
- **Schimbarea judecătorului (E0) schimbă toate cifrele vechi:** se păstrează ambele notări pe un examen întreg, ca să avem
  puntea; nimic din istoric nu se rescrie.
- **S15 e notat tot de Qwen:** verdictul lui se citește cu grija asta; E0 îl re-notează.
- **Dependența de Claude rămâne la L0–L2:** declarată, nu ascunsă. Nu promit L4.
- **Nopți pierdute:** fiecare etapă are criteriu de oprire; nicio etapă nu primește a doua noapte fără rezultat pe prima.
- **Date și versiuni:** nicio modificare de producție fără îngheț + rollback (există deja).

---

## 10. DECIZIE (propusă lui Adrian)

- **PĂSTRĂM:** nucleul, paznicul, pre-înregistrarea, cascada, modulele, examenele nevăzute. Modelul W2 ca punct de plecare.
- **MODIFICĂM:** ținta modelului — de la „să înțeleagă” la „sistem cu specialiști + memorie + buclă de auto-joc cu verificator”;
  judecătorul — de la Qwen la verificatoare proprii (E0); direcția de după S15 — E0 → E1.
- **ABANDONĂM:** „încă o noapte de antrenare cu aceeași rețetă ca să treacă de 2/15”. Dovada: S12 (3.319 întrebări, zero efect).

**Cele trei „da”-uri de care am nevoie de la Adrian:**
1. Ținta reformulată ca în §1 (T1–T4), cu „top” pe domenii cu verificator, nu pe conversație liberă.
2. Qwen iese din rolul de judecător la „răspuns din text” (E0). Rămâne, declarat, doar pentru poveștile vechi, până la E6.
3. După verdictul S15, supraveghetorul primește direcția E0 → E1 (le scriu eu în `plan/coada.md` ca aprobări, în stilul de până acum).

---

## 11. URMĂTORUL EXPERIMENT

**E0** (fără placă, azi): verificatorul fără LLM + re-notarea S15/S4. Rezultat așteptat (ESTIMARE): acord ≥ 90 % la întrebările
cu răspuns-bucată, dezacorduri mai ales la „Nu scrie în text”. Criteriu de succes: ≥ 90 %. Apoi **E1** cu criteriile din §8.
