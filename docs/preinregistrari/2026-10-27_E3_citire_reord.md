# Pre-înregistrare: E3 citește cu căutarea nouă (S33) — #438 răspunde cu bucățile `rrf_reord` față de S25 simplă, pe cele 100 S26

<!-- scrisa: 2026-10-27T08:31:00 -->
*Scrisă la 2026-10-27 ~08:30–08:31 (urcată în commit-ul 0fab1b8, 08:31:38; ora din antet corectată înainte de examen), la S33 pasul 2, ÎNAINTE de examenul de la pasul 3 (din S33 pe placă nu s-a rulat nimic;
pasul 1 a fost doar o numărare pe procesor din fișiere deja măsurate). După ce examenul începe, textul de mai jos nu se mai
schimbă; la închidere se adaugă doar „Ce a ieșit” și „Verdictul”. Nu e o antrenare: nimic nu se antrenează.*

## Cine a ales

Supraveghetorul a pus S33 în coadă la 27 oct 02:15 (granițele 2 și 5 din REGULI_CASCADA.md), din propunerile executantului
din raportul S29 (`docs/rapoarte/2026-10-26_2340_S29_E3_cautare_v2_verdict.md`). Pragurile de mai jos sunt cele scrise de
supraveghetor în coadă. Pre-înregistrarea și examenul le face Claude Code (executantul).

## Întrebarea

S29 a arătat că `rrf_reord` pune răspunsul în primele 3 bucăți la 83 din cele 100 S26, față de 72 la căutarea S25 simplă
(plafonul — răspunsul în bucățile care chiar încap — urcă de la 64 la 72). **Dacă #438 primește bucățile în ordinea nouă,
răspunde corect la mai multe întrebări?**

## Ce rulează (pasul 3, o singură rulare)

`python -X utf8 unelte/e3_citire_reord.py examen --model 438` (comandă nouă, cu test fără placă,
`teste/test_e3_citire_reord.py`; refuză dacă ieșirea există deja) → `lucru/e3/examen_s33.json`:
- setul: `lucru/e3/examen_nou_4096.json` (cele 100 S26), **amprenta verificată înainte** (`3501f307…f523`);
- modelul: **#438** (linia `w2_conv_e3_memorie`), care e și judecătorul la reordonare (ca la S29);
- pentru fiecare întrebare, în aceeași rulare: (i) **`s25`** = primele 3 bucăți ale căutării S25 simple
  (`nume_obligatorii_liste`, exact ca la S27); (ii) **`rrf_reord`** = RRF cu indexul cu rădăcini + primele 20 reordonate după
  log p(întrebare | bucată) dat de #438, promptul `Text: …⏎Întrebare:`, normalizat pe simbol (exact ca la S29);
- la ambele: din primele 3, câte încap în 512 − 64 = 448 de simboluri (regula S27, `cate_incap`), promptul
  `Text: …⏎Întrebare: …⏎Răspuns:`, răspunsul fără întâmplare, cel mult 80 de simboluri, tăiat la primul rând
  (`raspunde` din `e1_intrebari_nascute.py`), nota cu verificatorul S16 (`unelte/verificator_text.py`, doar citit);
- se scriu: corecte din 100, corecte dintre cele cu răspunsul în bucățile care încap și dintre cele fără, pe tipuri, timpul
  pe întrebare (căutarea, judecătorul, răspunsul), memoria plăcii (cea mai mare); paznicul S17 la fiecare 20 de întrebări;
  peste 7.000 MB → oprire, `oprit`, cifrele în raport;
- verificarea reperului: la (i), bucățile date și răspunsurile se compară întrebare cu întrebare cu S27 (`examen_s27.json`).

Placa: estimat 3–6 minute, sub 1.500 MB (S29: 732 MB alocați, ~1.070 MB văzuți; S27 a răspuns pe aceleași 100 fără probleme).

## Criteriile (din coadă, cuvânt cu cuvânt)

- **CONFIRMAT** dacă #438 cu `rrf_reord` răspunde corect la **cel puțin 5 întrebări mai mult** decât #438 cu căutarea S25
  simplă, măsurat în **aceeași rulare** pe cele 100 S26;
- **INFIRMAT** dacă diferența e **sub 2**;
- **între ele: NECLAR.**

În cifre, cu Δ = corecte(`rrf_reord`) − corecte(`s25`), din aceeași rulare: **CONFIRMAT** = Δ ≥ +5; **NECLAR** = Δ de +2,
+3 sau +4; **INFIRMAT** = Δ ≤ +1 (inclusiv negativ). Aceeași notare ca la S27, același prompt, aceeași regulă de încăpere,
fără întâmplare.

## Spus cinstit, înainte

1. **Setul S26 e folosit a patra oară** (S26, S27, S29, acum S33 — doar măsurat, nimic ales pe el).
2. **#438 a văzut `text_v3` la antrenare** (pornește din #415, care a văzut cele 100 de întrebări cu textul lor la noaptea 12);
   la S27 cele 100 au fost scoase cu articolele lor. Și ca judecător le poate „recunoaște”.
3. **Reperul S27 (60) trebuie să iasă din nou ~60 la varianta S25 simplă.** Dacă iese altceva, contează cifra din rulare și o spun.
4. **Câștigul de la S29 (+11 la k = 3) e mult peste validare (+1,2).** Pasul 1 arată de ce în parte: pe validare (1.000 de
   întrebări) definițiile câștigă +3,3 puncte, „regizat” +18,8, dar „restul” tipurilor pierde −4,0 și e 30 % din eșantion;
   pe S26 definițiile câștigă +14,8 puncte, iar „restul” e doar 19 % și nu pierde nimic. Deci și câștigul de la citire pe S26
   va fi probabil mai mare decât ar fi pe alt set.
5. Cu 100 de întrebări, 1–3 întrebări sunt zgomot.

## Așteptările mele, în cifre

- (i) `s25`: **60** corecte (exact ca S27: 60 din cele 64 cu răspunsul în bucățile date, 0 din celelalte 36); bucăți date
  1 / 2 / 3 = 17 / 64 / 19.
- (ii) `rrf_reord`: plafonul (răspunsul în bucățile care încap) **72** (ca la S29); corecte **~66 (62–70)**: cam 92 % din
  cele cu răspunsul în bucăți (puțin sub 60/64, fiindcă bucățile urcate de judecător pot fi mai grele de citit), ~0 din celelalte.
- Δ cel mai probabil **+6** (între +2 și +10); reparate ~8, stricate ~2.
- Pe tipuri: aproape tot câștigul la definiții (S27: 23 din 54 corecte; aștept ~29).
- Timpul: căutarea ~0,09 s, judecătorul ~0,14 s, răspunsul ~0,3–0,6 s pe întrebare și variantă (mediane). Placa < 1.500 MB.
- **Verdictul așteptat: CONFIRMAT ~55 %, NECLAR ~30 %, INFIRMAT ~15 %.**

## Ce a ieșit

*Adăugat la 2026-10-27 08:41, din jurnalul Kronos (lucru/jurnal/experimente.jsonl) și din jurnalul CONTINUUM pe bune. Verdictul se scrie dedesubt.*

Niciun experiment Kronos în perioada asta.

Niciun ciclu CONTINUUM pe bune în perioada asta.

**Examenul** (o singură rulare, 08:31:58–08:33:15, 77 s, cod 0, `unelte/e3_citire_reord.py examen --model 438` →
`lucru/e3/examen_s33.json`; amprenta listei `3501f307…f523` ✓; #438, linia `w2_conv_e3_memorie`):

| varianta | corecte din 100 | răspunsul în bucățile care încap | corecte dintre acestea | corecte dintre celelalte | încap 1 / 2 / 3 |
|---|---|---|---|---|---|
| (i) S25 simplă (`s25`, baza) | **60** | 64 | 60 | 0 din 36 | 17 / 64 / 19 |
| (ii) **`rrf_reord`** | **66** | 72 | 66 | 0 din 28 | 19 / 67 / 14 |

- Reperul S27 a ieșit exact: la (i) **aceleași bucăți la toate 100 de întrebări și același răspuns la toate 100**, 60 corecte.
- Față de (i): **15 reparate, 9 stricate** (net +6); la 22 de întrebări bucățile date sunt aceleași. Din cele 9 stricate,
  la 7 răspunsul nu mai e în bucățile care încap; la 2 e acolo, dar #438 a greșit (o definiție tăiată la 80 de simboluri,
  un an greșit).
- Pe tipuri (corecte, (i) → (ii)): definiții 23 → **30** din 54; născut 12 → 13 din 15; an 1 → 2 din 4; regizat 6 → 5 din 8;
  rest 18 → 16 din 19.
- Timpi (mediane): căutarea 0,083 s, judecătorul 0,135 s, răspunsul 0,187 s (i) / 0,178 s (ii). Placa: 732 MB alocați de
  PyTorch, 47 °C la sfârșit; RAM 1,1 GB.

## Verdictul

**CONFIRMAT:** #438 cu bucățile `rrf_reord` răspunde corect la **66** din 100, față de **60** cu bucățile S25 simple, în
aceeași rulare: **Δ = +6 ≥ 5**.

Ce trebuie spus la fel de clar:
- **E la limită:** +6 față de pragul +5. Cu 100 de întrebări, o întrebare = un punct; 15 reparate și 9 stricate înseamnă că
  reordonarea mută mult, nu doar adaugă.
- Câștigul vine **din definiții** (+7 din 54), exact tipul care pe validare câștigă puțin (+3,3 puncte la k = 3) și care pe
  S26 e 54 %. Pe „rest” se pierd 2, ca pe validare (−4,0 puncte). **Pe un set cu alt amestec, câștigul ar fi probabil mai mic.**
- #438 citește bine ce primește: corect la 66 din cele 72 cu răspunsul în bucăți (92 %; la (i): 60 din 64, 94 %) și la **0** dintre cele fără.
  Plafonul, nu cititul, rămâne limita.
- Riscul scris înainte rămâne: #438 a văzut cele 100 de întrebări cu textul lor în `text_v3` (prin #415), și ca judecător.
