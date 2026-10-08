# Planul joi 8 → sâmbătă 10 octombrie 2026

*Un singur plan, cinci faze, până sâmbătă dimineață. Scris de Claude (chat) cu Adrian. Claude Code îl execută fază cu fază și actualizează secțiunea „Stare” de la final după fiecare fază (commit), ca orice sesiune nouă să poată relua de unde a rămas.*

## Țintele (ce vrem să fie altfel sâmbătă dimineață)

1. **Treapta 5, „își alege singur ce învață”:** CONTINUUM a rulat **pe bune** două nopți, a ales singur ce antrenare pornește, iar jurnalul lui explică fiecare decizie. Fără om între 19:00 și 07:00.
2. **Treapta 4 întărită:** cel mai bun model are povești ≤ 0,428 și fapte ≥ 60/150, cu hrana în amestec, confirmate pe setul sacru.
3. **Treapta 7, școala de cod:** verdict scris vineri seara: continuă (B a trecut nivelul 2 fără să uite poveștile) sau parcată ca rezultat negativ bine documentat.
4. **Pachetul de mutare pe workstation** (RTX 3070 8 GB, 128 GB RAM): ce se copiază, ce se regenerează, ce configurări și ce tokenizer nou, cu licențele datelor verificate. Doar plan și liste, fără descărcări mari.
5. Cele trei lecții din SANDBOX-7 intrate în Kronos: faptele profesorului verificate de om, biblioteca școlii curățată după corectitudine, așteptări scrise înainte de fiecare noapte.

## Reguli pe toată durata

- **Placa e una:** nopțile (19:00–07:00) sunt ale liniei principale (CONTINUUM + antrenări lungi); zilele sunt ale școlii de cod. Niciodată amândouă. Școala se oprește singură cel târziu la **18:30** (îngheț + raport parțial), ca placa să fie liberă la 19:00.
- **`kronos/` neatins; `module/examen_bpb.py` neatins; jurnalele nu se editează de mână.** Totul măsurat; rezultatele negative se raportează la fel ca cele bune.
- **Pre-înregistrare:** înainte de fiecare noapte, un fișier `docs/preinregistrari/2026-10-0X_<nume>.md` cu așteptările în cifre. Dimineața, același fișier primește secțiunea „Ce a ieșit”.
- **Raport către Adrian la sfârșitul fiecărei faze**, scurt. Dacă ceva cade, raport imediat, cu ce s-a făcut.
- **Alimentarea:** verificare înainte de fiecare pornire pe placă; pe baterie nu se pornește nimic lung.
- STOP comun (`lucru/STOP`) oprește tot, inclusiv CONTINUUM.

---

## Faza 0 — joi, imediat după pilotul v0.2 al școlii

- Raportul v0.2 către Adrian (ca la pilot: unde se rupe lanțul, tabel nivel × linie, B față de D pe aceleași runde, biții pe byte pe povești la fiecare îngheț, soluțiile noi, trișări).
- Commit pe `kronos-cod`. Actualizează „Stare”.

## Faza 1 — joi după-amiază, procesor, cel mult 2 ore (gata până la 18:45)

**1a. Lecțiile SANDBOX-7.**
- `docs/fapte_de_verificat.md`: cele 50 de fapte din hrană, numerotate, în engleză, cu o traducere în română făcută de profesor (marcată „traducere automată”). Adrian răspunde cu numerele celor greșite sau îndoielnice. Până răspunde, nimic nu se schimbă; după, faptele marcate ies din generarea de hrană viitoare și se marchează în examene (nu se șterg, se marchează).
- Școala: la fiecare regresie, soluțiile din bibliotecă ale căror sarcini pică testele nevăzute ale nivelului lor **ies din bibliotecă** (se mută în `lucru/cod/respinse/`, cu motiv). Frecvența nu e corectitudine. Teste.
- Unealta de pre-înregistrare: `unelte/preinregistrare.py --nume X` creează fișierul din șablon (întrebarea, așteptările cu cifre, ce ar infirma); `--inchide X` adaugă „Ce a ieșit” din jurnal.

**1b. CONTINUUM pe bune: pregătire.**
- `config/continuum.toml`: `fereastra_invatare = "19:00-07:00"`, `fereastra_intretinere = "07:00-19:00"`; **lista albă** pentru joi: `[linii] configurari = ["config/laptop_antrenare_lunga_7.toml"]` (nimic altceva poate porni); o singură antrenare pe noapte; jurnalul rulării pe bune separat de cel al simulării (`lucru/continuum/`, nu `lucru/continuum_simulare/`).
- Verificare uscată: `--simuleaza --ca-la 19:05` trebuie să aleagă antrenarea 7 și să spună de ce. Dacă nu o alege, se repară cauza (config sau nevoi), nu se forțează.
- Plasa de siguranță, scrisă în README: dacă la **20:00** nu a pornit nimic, Claude Code pornește manual antrenarea 7 și scrie în raport „CONTINUUM n-a ales” + ultimele cicluri din jurnalul lui. Dacă CONTINUUM cade în timpul nopții, antrenarea pornită merge mai departe (e proces separat); se raportează dimineața.

**1c. Pre-înregistrarea nopții 1** (`2026-10-08_noaptea1_continuum.md`). Așteptări propuse (Claude Code le poate ajusta, dar le scrie înainte):
- CONTINUUM alege antrenarea 7 în primul ciclu de după 19:00, cu motivul „dezvoltă/continuă povești+fapte, hrană nefolosită, placă liberă”;
- antrenarea 7 (din #262, 8 ore, hrană 5 %, rata 0,0001 → 0,00001): val_bpb final între 0,420 și 0,430; R ≥ 0,80 la fiecare oră; nota în ±1,0; nicio oră respinsă pentru fapte;
- ce ar infirma: val_bpb peste 0,434 la final (n-a câștigat nimic), sau R sub 0,7 (hrana nu ajunge la rata asta).

**1d. La 18:45:** oprește simularea v0 (închide procesul, nu STOP), notează în README ce a ales în cele 3 zile. Verifică placa (liberă, rece), alimentarea. **La 19:00 pornește CONTINUUM pe bune** (v1, fără `--simuleaza`), ca proces separat, cu urmărire în fundal.

## Faza 2 — joi 19:00 → vineri 07:00: Noaptea 1, CONTINUUM pe bune

- Claude Code nu intervine decât în cazurile din plasa de siguranță.
- Dimineața: închide pre-înregistrarea („Ce a ieșit”), raport: jurnalul CONTINUUM ciclu cu ciclu (ora, ce a văzut, ce a ales, de ce), tabelul antrenării 7 pe ore (val_bpb, fapte_noi, R, nota, decizie), setul sacru pe cel mai bun model, și verdictul pe treapta 5: **„a ales singur: da/nu”**. README. Commit. „Stare”.

## Faza 3 — vineri 07:00–18:30: ziua, școala de cod v0.3 (placă) + pachetul de mutare (procesor)

**3a. Școala v0.3, după regulile de mai jos**, aplicate pe raportul v0.2 (Claude Code alege ramura și o scrie în raport):
- **Dacă B a trecut 0a–1b și 2A cu poveștile ≤ 0,46:** v0.3 = continuă cu 2B, 2C, 3A, 3B, aceleași setări; liniile **B și D** (A și-a făcut treaba, se oprește; se notează); buget 20 de minute pe nivel și linie.
- **Dacă B s-a oprit la 1a/1b (numere):** v0.3 = abecedar mărit la nivelurile 0–1 (încă ~60 de episoade cu numere variate, generate de `fa_abecedar.py`, marcate ca „sămânța v2”), set văzut de 200 de sarcini în loc de 60, aceleași temperaturi; reia 0a–1b, apoi mai departe dacă trece; liniile B și D.
- **Dacă poveștile au trecut din nou peste 0,46:** întâi 85 % povești / 15 % școală și jumătate din pașii pe rundă; abia apoi regula de mai sus.
- **Dacă B n-a trecut nici 0a în v0.2:** școala se parchează: raport negativ complet în README, îngheț final, nimic altceva pe ea săptămâna asta.
- Oprire obligatorie la 18:30: îngheț, raport parțial dacă nu s-a terminat.
- **Verdictul de vineri seara**, scris în README: „continuă” dacă B a trecut nivelul 2A (prima linie de cod adevărată) cu poveștile ≤ 0,46; altfel „parcată, se reia pe workstation cu model mai mare”.

**3b. Pachetul de mutare pe workstation** (`docs/MUTARE_workstation.md`, procesor, în paralel):
- **Ce se copiază:** repo-ul (toate ramurile), `lucru/` cu modelele păstrate (#252, #257, #262, cel mai bun după noaptea 1, și înghețurile școlii), jurnalele, `date/fapte/*.json`, `date/cod/`, tokenizer-ul. Mărimi.
- **Ce se regenerează acolo:** cache-ul TinyStories, indexurile de fragmente, hrana (sau se copiază; se spune care e mai ieftin).
- **Configurări propuse pentru RTX 3070 8 GB:** un model mai mare (propune 2–3 variante, de ex. 12×768, cu estimarea memoriei video la lot și context; ținta: sub 7 GB), rata, lotul, ore pe noapte; și ce se schimbă în paznic (limita 7 GB, temperatura).
- **Tokenizer nou** (plan, nu execuție): engleză + română + cod, dimensiune propusă, pe ce text se învață; **consecință:** modelele vechi nu se pot continua cu tokenizer nou; linia nouă pornește de la zero pe workstation, cu povești + fapte 5 % + abecedar în amestec de la început (experimentul „de la zero”, prioritatea 3 din review-ul extern).
- **Date pentru română și traducere:** listă de surse cu **licența verificată** (de ex. corpusuri paralele EN–RO deschise), mărime, ce ar încăpea. Doar listă; fără descărcare pe laptop.
- **Teste:** care depind de Windows, ce ar trebui să ruleze pe workstation în prima oră.
- **CONTINUUM pe workstation:** ce se schimbă în config (ferestre, buget, VRAM).

**3c. Pre-înregistrarea nopții 2** (`2026-10-09_noaptea2.md`): două variante, scrise amândouă:
- **Noaptea 2a — CONTINUUM alege antrenarea 8** (`config/laptop_antrenare_lunga_8.toml`, de creat în 3b: din cel mai bun model după noaptea 1, 8 ore, hrană 5 %, rata 0,00005 → 0,000005, criterii implicite). Lista albă de vineri = doar config 8. Așteptări: câștig la val_bpb peste 0,005 sau nu (răspunsul pe care 6b nu l-a dat); R ≥ 0,8.
- **Noaptea 2b — dacă CONTINUUM nu pornește nimic până la 20:00** (de ex. „saturat”): Claude Code pornește manual **Kronos-fapte-zero**: model nou, de la zero, aceeași arhitectură și tokenizer, 8 ore pe TinyStories + 5 % fapte de la început, aceleași examene la fiecare oră. Întrebarea: ajunge la fapte comparabile cu injectarea (#252: 72) fără să plătească uitarea? Așteptări scrise.

## Faza 4 — vineri 19:00 → sâmbătă 07:00: Noaptea 2

- La 18:45: placa liberă, alimentare, lista albă = config 8, CONTINUUM pe bune repornit cu noua listă (sau lăsat să ruleze, dacă citește config-ul la redescoperire).
- Plasa de siguranță la 20:00, ca în noaptea 1, cu varianta 2b.
- Dimineața: închide pre-înregistrarea, raport ca în faza 2, plus comparația noaptea 1 / noaptea 2.

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

- [ ] Faza 0 — v0.2 raportat
- [ ] Faza 1 — lecții, CONTINUUM pregătit, pre-înregistrare, pornit pe bune la 19:00
- [ ] Faza 2 — noaptea 1 raportată; treapta 5: …
- [ ] Faza 3 — v0.3 (ramura aleasă: …), verdict: …; pachet de mutare scris; pre-înregistrare noaptea 2
- [ ] Faza 4 — noaptea 2 raportată (varianta 2a / 2b)
- [ ] Faza 5 — închidere
