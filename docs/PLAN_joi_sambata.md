# Planul joi 8 → sâmbătă 10 octombrie 2026

*Un singur plan, cinci faze, până sâmbătă dimineață. Scris de Claude (chat) cu Adrian. Claude Code îl execută fază cu fază și actualizează secțiunea „Stare” de la final după fiecare fază (commit), ca orice sesiune nouă să poată relua de unde a rămas.*

## Țintele (ce vrem să fie altfel sâmbătă dimineață)

1. **Treapta 5, „își alege singur ce învață”:** CONTINUUM a rulat **pe bune** două nopți, a ales singur ce antrenare pornește, iar jurnalul lui explică fiecare decizie. Fără om între pornire și 07:30.
2. **Treapta 4 întărită:** cel mai bun model are povești ≤ 0,428 și fapte ≥ 60/150, cu hrana în amestec, confirmate pe setul sacru.
3. **Treapta 7, școala de cod:** verdict scris vineri seara: continuă (B a trecut nivelul 2 fără să uite poveștile) sau parcată ca rezultat negativ bine documentat.
4. **Pachetul de mutare pe workstation** (RTX 3070 8 GB, 128 GB RAM): ce se copiază, ce se regenerează, ce configurări și ce tokenizer nou, cu licențele datelor verificate. Doar plan și liste, fără descărcări mari.
5. Cele trei lecții din SANDBOX-7 intrate în Kronos: faptele profesorului verificate de om, biblioteca școlii curățată după corectitudine, așteptări scrise înainte de fiecare noapte.

## Reguli pe toată durata

- **Placa e una:** nopțile (19:00–07:30; joi de la ~23:00, după antrenarea 7) sunt ale liniei principale (CONTINUUM + antrenări lungi); zilele sunt ale școlii de cod. Niciodată amândouă. Școala se oprește singură cel târziu la **18:30** (îngheț + raport parțial), ca placa să fie liberă la 19:00.
- **`kronos/` neatins; `module/examen_bpb.py` neatins; jurnalele nu se editează de mână.** Totul măsurat; rezultatele negative se raportează la fel ca cele bune.
- **Pre-înregistrare:** înainte de fiecare noapte, un fișier `docs/preinregistrari/2026-10-0X_<nume>.md` cu așteptările în cifre. Dimineața, același fișier primește secțiunea „Ce a ieșit”.
- **Raport către Adrian la sfârșitul fiecărei faze**, scurt. Dacă ceva cade, raport imediat, cu ce s-a făcut.
- **Alimentarea:** verificare înainte de fiecare pornire pe placă; pe baterie nu se pornește nimic lung.
- STOP comun (`lucru/STOP`) oprește tot, inclusiv CONTINUUM.

---

## Faza 0 — joi 13:00: v0.2 raportat (făcut). Antrenarea 7 a pornit la 13:09.

*Rezultatul v0.2:* lanțul s-a rupt la 0a pe toate liniile, din cauza treptei (doar 4 sarcini văzute și 4 nevăzute; s-a învățat pe de rost). Poveștile s-au păstrat (0,437), pregătirea scurtă merge (60 de pași, pierdere 0,42). Antrenarea 7 rulează din #262 până pe la 23:00; prima oră respinsă față de #262 (rata repornită la 0,0001), verdictul vine din orele 4–8.

## Faza 1 — joi după-amiază și seară, procesor (placa e a antrenării 7)

**1a. Lecțiile SANDBOX-7.**
- `docs/fapte_de_verificat.md`: cele 50 de fapte din hrană, numerotate, în engleză, cu traducere în română de la profesor (marcată „traducere automată”; profesorul rulează pe placă doar după 23:00, când e liberă, sau traducerea se lasă pe mâine dimineață). Adrian răspunde cu numerele celor greșite; până atunci nimic nu se schimbă; după, faptele marcate ies din generarea de hrană viitoare și se marchează în examene (nu se șterg).
- Școala: la fiecare regresie, soluțiile din bibliotecă ale căror sarcini pică testele nevăzute ale nivelului lor **ies din bibliotecă** (în `lucru/cod*/respinse/`, cu motiv). Teste.
- Unealta de pre-înregistrare: `unelte/preinregistrare.py --nume X` (șablon: întrebarea, așteptările în cifre, ce ar infirma); `--inchide X` adaugă „Ce a ieșit” din jurnal.

**1b. Școala v0.3, codul (fără placă; pilotul rulează vineri).** Rețeta, pe raportul v0.2:
- **Nivelul 0 = numerele 0–99 împreună**, exact ca nivelul 0 din v0.1 (văzut 60 / nevăzut 20 / adversarial cu trei cifre / sacru 20), fără cuvinte. Cuvintele devin nivelul **0w**, separat, imediat după 0.
- **Verificare de formă la nivelul 0 și 0w:** codul e doar valoarea (`46`, `"dog"`) sau `print(valoare)`; orice altceva pică (nu mai trec `t = 0 ⏎ print(t+0)` sau `"7"` pentru 7).
- **Linia D primește exact cât B**, inclusiv repetări sau forme alternative ale aceleiași sarcini, ca să fie comparație curată.
- Rămân din v0.2: 70 % povești în fiecare lot, pregătirea oprită la pierderea 0,5, regresia pe povești la 0,46, codul interzis pe cuvinte întregi, temperaturile, regresia cu „peste 15 puncte și cel puțin 2 sarcini”.
- Nivelurile v0.3: 0, 0w, 1a, 1b, 2A, 2B, 2C, 3A, 3B. Liniile A, B, D. Buget 30 de minute pe nivel și linie. Dosar `lucru/cod_v03/`.
- Teste, commit pe `kronos-cod`.

**1c. CONTINUUM pe bune: pregătire.**
- `config/continuum.toml`: `fereastra_invatare = "19:00-07:30"`, `fereastra_intretinere = "07:30-19:00"`; **lista albă** pentru noaptea 1: `[linii] configurari = ["config/laptop_antrenare_lunga_8.toml"]`; o singură antrenare pe noapte; jurnalul rulării pe bune separat de cel al simulării.
- `config/laptop_antrenare_lunga_8.toml`: continuare din cel mai bun model păstrat după antrenarea 7 (CONTINUUM îl alege singur ca `ultimul_model`), **7 ore** (ca să se termine până la 07:30), hrană 5 %, rata **0,00005 → 0,000005** (fără repornire mare; răspunde la întrebarea rămasă de la 6b: mai câștigă ceva continuarea cu pași mici?), criteriile implicite.
- Verificare uscată după ce se termină antrenarea 7: `--simuleaza --ca-la 23:05` trebuie să aleagă antrenarea 8 (dacă val_bpb a mai scăzut în ultima oră a antrenării 7) sau să spună „saturat” cu motiv. Nu se forțează nimic.
- Plasa de siguranță (în README): dacă la **00:00** n-a pornit nimic, Claude Code pornește manual **Kronos-fapte-zero** (`config/laptop_fapte_zero.toml`: model nou de la zero, aceeași arhitectură și tokenizer, 7 ore pe TinyStories + 5 % fapte de la început, aceleași examene la fiecare oră; întrebarea: ajunge la fapte comparabile cu injectarea fără să plătească uitarea?) și notează „CONTINUUM n-a ales” + ultimele cicluri din jurnalul lui. Dacă CONTINUUM cade în timpul nopții, antrenarea pornită merge mai departe; se raportează dimineața.

**1d. Pre-înregistrarea nopții 1** (`2026-10-08_noaptea1.md`), scrisă înainte de 23:00, cu amândouă variantele:
- antrenarea 7 (în curs): val_bpb final între 0,420 și 0,430; R ≥ 0,8; orele 4–8 păstrate;
- varianta 1a, CONTINUUM alege antrenarea 8: câștig total peste 0,005 în 7 ore = „continuarea cu pași mici merită”; sub 0,005 = „saturat, repornirile sunt necesare”;
- varianta 1b, fapte-zero: fapte_noi la ora 7 față de 72 (#252) și val_bpb față de ce avea linia veche după 7 ore de la zero (noaptea a treia, ~0,46).

**1e. La ~23:00**, când se termină antrenarea 7: raport scurt al antrenării 7 (tabel pe ore, decizia fiecărei ore, setul sacru pe cel mai bun model). Oprește simularea v0 (închide procesul, nu STOP), notează în README ce a ales în cele 3 zile. Verifică placa (liberă, răcită), alimentarea. **Pornește CONTINUUM pe bune** (v1, fără `--simuleaza`), proces separat, urmărire în fundal.

## Faza 2 — joi 23:00 → vineri 07:30: Noaptea 1, CONTINUUM pe bune

- Claude Code nu intervine decât în cazurile din plasa de siguranță.
- Dimineața: închide pre-înregistrarea, raport: jurnalul CONTINUUM ciclu cu ciclu (ora, ce a văzut, ce a ales, de ce), tabelul antrenării pe ore, setul sacru pe cel mai bun model, verdictul pe treapta 5: **„a ales singur: da/nu”**, și răspunsul la întrebarea nopții (1a sau 1b). README. Commit. „Stare”.

## Faza 3 — vineri 07:30–18:30: ziua, școala v0.3 (placă) + pachetul de mutare (procesor)

**3a. Pilotul v0.3** (rețeta din 1b), pornit după ce placa e liberă și răcită. Oprire obligatorie la 18:30: îngheț, raport parțial dacă nu s-a terminat.
- **Verdictul de vineri seara**, scris în README: „continuă” dacă B a trecut nivelul 2A (prima linie de cod adevărată, `print`) cu poveștile ≤ 0,46; altfel „parcată, se reia pe workstation cu model mai mare și tokenizer care nu taie numerele în cifre”. În ambele cazuri: raport complet, îngheț final, B față de A și D pe aceleași runde.

**3b. Pachetul de mutare pe workstation** (`docs/MUTARE_workstation.md`, procesor, în paralel):
- **Ce se copiază:** repo-ul (toate ramurile), `lucru/` cu modelele păstrate (#252, #257, #262, cel mai bun după nopțile 1–2, înghețurile școlii), jurnalele, `date/fapte/*.json`, `date/cod/`, tokenizer-ul. Mărimi.
- **Ce se regenerează acolo:** cache-ul TinyStories, indexurile de fragmente, hrana (sau se copiază; se spune care e mai ieftin).
- **Configurări propuse pentru RTX 3070 8 GB:** 2–3 variante de model mai mare (de ex. 12×768), cu estimarea memoriei video la lot și context, ținta sub 7 GB; rata, lotul, ore pe noapte; ce se schimbă în paznic.
- **Tokenizer nou** (plan, nu execuție): engleză + română + cod, **cu numerele ca bucăți întregi (0–999) sau cel puțin cifrele grupate**, dimensiune propusă, pe ce text se învață; consecință: linia nouă pornește de la zero pe workstation, cu povești + fapte 5 % + abecedar în amestec de la început.
- **Date pentru română și traducere:** listă de surse cu licența verificată, mărime, ce ar încăpea. Doar listă; fără descărcare pe laptop.
- **Teste** care depind de Windows; ce trebuie să ruleze pe workstation în prima oră. **CONTINUUM pe workstation:** ce se schimbă în config.

**3c. Pre-înregistrarea nopții 2** (`2026-10-09_noaptea2.md`), cu regula de alegere:
- dacă noaptea 1 a rulat antrenarea 8 și a câștigat peste 0,005: lista albă = `laptop_antrenare_lunga_9.toml` (încă 8 ore, aceeași rețetă, din cel mai bun model), CONTINUUM alege;
- dacă noaptea 1 a rulat antrenarea 8 și a fost „saturat” (sub 0,005): noaptea 2 = **fapte-zero**, pornit de Claude Code la 19:00, pre-înregistrat;
- dacă noaptea 1 a rulat fapte-zero: noaptea 2 = CONTINUUM cu lista albă `laptop_antrenare_lunga_8.toml` (continuarea liniei vechi, 8 ore).

## Faza 4 — vineri 19:00 → sâmbătă 07:30: Noaptea 2

- La 18:45: placa liberă, alimentare, lista albă potrivită, CONTINUUM pe bune repornit cu noua listă (sau lăsat să ruleze dacă citește config-ul la redescoperire).
- Plasa de siguranță la 20:00, ca în noaptea 1.
- Dimineața: închide pre-înregistrarea, raport ca în faza 2, plus comparația noaptea 1 / noaptea 2 și, dacă a rulat fapte-zero, comparația „de la zero cu fapte” față de „injectate” (#252/#262) la același număr de ore.

## Faza 5 — sâmbătă dimineață: închidere

- README actualizat cu tot (nopțile 1 și 2, școala v0.2/v0.3 și verdictul, lecțiile SANDBOX-7, pachetul de mutare).
- `docs/UNDE_AM_AJUNS_2026-10-10.md`: tabelul scării (ce treaptă e verde / în lucru / neatinsă, cu cifra care o susține), cel mai bun model după fiecare criteriu, cifrele pentru prezentare (zile, experimente, antrenări, teste).
- Lista deciziilor pentru Adrian, pe scurt (max 5), pentru weekend.
- Toate ramurile trimise pe GitHub. `kronos-cod` rămâne ramură separată (nu se unește cu `main` fără decizia lui Adrian).
- Toate testele trec în ambele foldere.

## Sarcinile lui Adrian

- Joi seara: încărcătorul conectat, laptopul nefolosit de altcineva.
- Vineri: citește `docs/fapte_de_verificat.md` și răspunde cu numerele faptelor greșite.
- Sâmbătă: citește `docs/UNDE_AM_AJUNS_2026-10-10.md` și pachetul de mutare; decide ce se mută în weekend.

---

## Stare (actualizată de Claude Code după fiecare fază)

- [x] Faza 0 — v0.2 raportat (13:03); antrenarea 7 pornită 13:09
- [x] Faza 1 — lecții, codul v0.3, CONTINUUM pregătit (lista albă: antrenarea 8; plasă: fapte-zero la 00:00), pre-înregistrare, pornit pe bune la ~23:00
  - **Gata joi, 21:40.**
  - **Lecțiile SANDBOX-7:**
    - `docs/fapte_de_verificat.md` are cele 50 de fapte. Traducerea profesorului (21:34) e slabă, deci am adăugat și
      traducerea lui Claude Code. Mecanismul pentru faptele greșite e inactiv până răspunde Adrian.
    - Biblioteca școlii se curăță la regresie (`kronos-cod`).
    - Unealta de pre-înregistrare ia și orele începute înainte, dar terminate după.
  - **v0.3 pe `kronos-cod`** (69faa04): 0n (numerele 0–99), 0w, forma „doar valoarea”, D exact cât B, curățarea,
    oprirea la 18:20.
  - **Antrenarea 7, terminată la 21:30:** 0,4263, R 1,08, sacru 31/50. Nicio oră păstrată: ora 8 bate #262 cu 0,0041,
    sub pragul de 0,005.
  - **Simularea v0** e oprită, cu rezumatul în README.
  - **Proba la uscat:** „saturat” (ultimele ore +0,0039, +0,0013), prima alegere o remăsurare a faptelor.
  - **CONTINUUM pe bune**, pornit la 21:36 (`lucru/continuum_pe_bune/`).
    - #1: remăsurarea faptelor pe #262, reușită.
    - #2: „nu pornesc nimic”.
    - Plasa rămâne la 00:00.
  - **Teste:** main 541 trec (490 + 51 cu placa), `kronos-cod` 653 (602 + 51); câte 1 sărit.
  - **Abateri** de la textul planului:
    - lista albă stă la `[nevoi.continua]`, nu la `[linii]` (de ce: README, „Noaptea 1”);
    - văzutul la nivelul 0 e 55, nu 60, pentru că mai multe nu încap în 0–99 (`config/scoala_cod_v03.toml`);
    - pornirea a fost la 21:36, nu la ~23:00, cu adendum datat în pre-înregistrare.
- [x] Faza 2 — noaptea 1 raportată; treapta 5: **a ales singur: NU**
  - **CONTINUUM pe bune** (21:36–07:30, 180 de cicluri, oprit la 07:30):
    - o remăsurare a faptelor pe #262, aleasă singur;
    - 133 de „nu pornesc nimic”: poveștile sunt saturate, iar lista albă n-are altceva;
    - 46 de REPAUS.
  - **Plasa de siguranță:** fapte-zero, la 00:00:27.
  - **Răspunsul 1b: da.** La ora 7, fapte-zero are 0,4686 (noaptea 3: 0,4636, deci +0,0050), 65 de fapte noi
    (#252: 72, sub zgomot) și sacru 25/50 (#252: 26).
  - **Pre-înregistrarea** e închisă, cu verdictul. README e actualizat.
- [x] Faza 3 — v0.3 (ramura aleasă: `kronos-cod`), verdict: **parcată**; pachet de mutare scris; pre-înregistrare noaptea 2
  - **Gata vineri, ~09:45.**
  - **v0.3 pe `kronos-cod`**, pilotul 07:38–09:17:
    - 0n trecut de B și D în 3 runde (80% / 85%), A pică;
    - 0w picat de B și D (0%): modelul copiază cuvintele exemplelor, iar `"moon"` se taie în 4 bucăți;
    - poveștile ≤ 0,4383.
  - **Verdict: PARCATĂ** (B n-a ajuns la 2A). Înghețul final e `v03_final`.
  - **Pachetul de mutare** e scris (`docs/MUTARE_workstation.md`, cu licențele verificate). Modelul nopții 2 se adaugă
    sâmbătă.
  - **Pre-înregistrarea nopții 2** e scrisă: CONTINUUM cu lista albă antrenarea 8 (8 ore); plasa la 20:00 pornește tot
    antrenarea 8.
  - **Comparația pentru sâmbătă:** de la zero, fără fapte, 7 ore (#225): 34 de fapte noi și sacru 11, față de 65 și 25
    cu 5% fapte (#286).
  - **Adrian** a verificat faptele: niciunul greșit.
  - **STOP-ul comun** oprește și școala.
- [ ] Faza 4 — noaptea 2 raportată (ce a rulat: …)
- [ ] Faza 5 — închidere
