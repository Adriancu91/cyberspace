# Raportul de dimineață — marți, 27 octombrie 2026, 06:44

## Pe scurt
- **Prima noapte de lucru după pauză și a fost plină.** Executantul a terminat patru sarcini: S27, S29, S30 și S31. Toate s-au încheiat normal, fără nicio eroare.
- **S27 (Kronos învață să citească din text): CONFIRMAT la limită.** A răspuns corect la 60 de întrebări din 100. Modelul vechi #415 a răspuns la 57.
- **S29 (căutarea nouă de articole): CONFIRMAT.** Articolul bun e printre primele 3 găsite în 83 de cazuri din 100. Căutarea veche reușea în 72.
- **S31 (AdamW contra Muon): INFIRMAT.** Muon a ieșit mai slab. Vestea bună: varianta cu AdamW a dat cel mai bun rezultat pe română de până acum din linia asta (1,2332, mai mic = mai bine).
- **Testele:** 946 trec, 1 e sărit (cel care are nevoie de placa video), niciunul nu pică.
- **N-a fost examen de conversație**, deci azi n-ai cele 20 de răspunsuri de verificat.

## Ce a rulat (de ieri seară până acum)
Câteva cuvinte, ca să fie clar:
- **AdamW** și **Muon** sunt două metode de a corecta modelul în timpul antrenării. Kronos a folosit până acum AdamW.
- **Pre-înregistrarea** e regula scrisă dinainte, care spune ce rezultat înseamnă „CONFIRMAT” sau „INFIRMAT”.

| sarcina | ce a făcut | când | cum s-a terminat |
|---|---|---|---|
| S27 | Kronos a învățat să răspundă din text (#436–#438), apoi a dat examenele | 16:52 → 21:04 | cod 0, **CONFIRMAT la limită** |
| S29 | Căutarea nouă de articole (ordinea refăcută de modelul #438), măsurată o singură dată pe cele 100 de întrebări puse deoparte | 21:29 → 23:41 | cod 0, **CONFIRMAT** |
| S30 | Pregătirea pentru Muon: codul nou, testele și o probă de 10 minute pe placă | 23:59 → 00:25 | cod 0, fără verdict (era doar pregătire) |
| S31 | Câte 2 ore de antrenare din #415: A cu AdamW (#440, #441), B cu Muon (#442, #443), apoi examenele (#444, #445) | 01:01 → 05:16 | cod 0, **INFIRMAT** |

- **Executantul** (cel care ia sarcinile din coadă) a pornit la fiecare 30 de minute, de la 18:28 la 06:28: 25 de porniri, toate încheiate normal (cod 0).
- **Supraveghetorul** a verificat S27 și S29 și le-a găsit corecte. A pus S33 înaintea lui S32 în coadă (commit 757fe06).
- **CONTINUUM** (bucla care observă calculatorul) a mers la fiecare 5 minute toată noaptea, fără goluri: 152 de cicluri între 18:00 (#3619) și 06:40 (#3771). A stat în repaus, pentru că placa e a executantului. Mai notează două nevoi în așteptare: `repara:povesti` și `dezvolta:sens`.
- **Placa video:** în timpul antrenărilor a folosit cel mult 5.374 MB (limita e 7.000 MB), iar paznicul n-a oprit nimic. Proba scurtă de la S30 a urcat până la 5.917 MB. **Acum** placa e liberă: 400 MB, 30 °C, folosită 1 %.
- **Git:** 19 commituri de ieri, de la 18:00, până acum, ultimul dcd812d (S31 gata), toate urcate pe GitHub.

## Cifrele principale

**S27 — Kronos învață să citească din text** (raportul `2026-10-26_2104_S27_E3_memorie.md`)
- Cele 100 de întrebări noi: modelul nou #438 a răspuns la **60**, #415 la 57. Pragul era 60, deci a trecut la limită.
- Celelalte examene au ieșit în praguri: noaptea 10 69/70 (#415: 70), S4 39/60 (#415: 38).
- Cel mai mult pe care îl putea lua: 64. La celelalte întrebări, articolul bun nu încăpea în ce citește modelul.

**S29 — căutarea nouă** (raportul `2026-10-26_2340_S29_E3_cautare_v2_verdict.md`)
- Articolul bun printre primele 3 găsite: **83 din 100**, față de 72 cu căutarea veche. Pragul cerea un câștig de cel puțin 5, iar câștigul a fost de 11.
- Printre primele 20 găsite: 95, față de 94.
- La proba de dinainte, câștigul fusese doar de +1,2, deci câștigul real e probabil mai mic de 11.

**S31 — AdamW contra Muon** (raportul `2026-10-27_0535_S31_muon.md`; mai mic = mai bine, în afară de „fapte noi”)

| măsura | A (AdamW, #441) | B (Muon, #443) | punctul de plecare #415 |
|---|---|---|---|
| română (curat) | **1,2332** | 1,3019 | 1,2858 |
| povești în engleză (TinyStories R2) | 0,4154 | 0,4472 | 0,4411 |
| cod (curat) | 0,7460 | 0,8042 | — |
| fapte noi (din 150; mai mare = mai bine) | 76 | 73 | — |

Muon a pornit cu un „șoc”: în prima oră a fost mai slab chiar decât #415, apoi și-a revenit mult. Probabil o parte din pierdere vine din schimbarea bruscă a metodei pe un model deja antrenat. Asta nu schimbă verdictul.

## Pre-înregistrări și verdict
Nu a rămas nicio pre-înregistrare deschisă: toate au deja secțiunea „Ce a ieșit”. Cele de azi-noapte le-a închis executantul, cu verdictul judecat după pragurile scrise dinainte:
- `2026-10-26_E3_memorie.md` → **CONFIRMAT la limită**;
- `2026-10-26_E3_cautare_v2.md` → **CONFIRMAT**;
- `2026-10-27_muon.md` → **INFIRMAT**.

Eu n-am mai avut nimic de închis sau de judecat.

## Examenul de conversație
N-a fost (ultimul e din 22 octombrie). Fără cele 20 de răspunsuri azi; sămânța n-a fost folosită.

## Testele
Comanda: `CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -m pytest -q`
Rezultat: **946 trec, 1 sărit, 0 picate** (3 minute și 53 de secunde).

## Ce urmează în coadă (fără să faci nimic)
- **S33** (E3 citește cu căutarea nouă: examenul de la S27 refăcut cu căutarea de la S29) e `aprobat`. Se face doar ziua, deci pornește la prima verificare de după 08:00. Pe placă stă cel mult o oră.
- **S32** (Kronos răspunde fără PyTorch, doar pe procesor) e `aprobat` și pornește după S33.

## Ce aștept de la tine
1. **Nimic obligatoriu azi.** S33 și S32 sunt deja aprobate și merg singure.
2. **De gândit: rețeta A de la S31.** E AdamW, cu adunare pe 8 loturi și cu încetinirea antrenării pe ultimul sfert. A dat cel mai bun rezultat pe română de până acum din linia asta: 1,2332, față de 1,2858 la #415. Dacă vrei, spune „da” și supraveghetorul propune o continuare cu ea.
   - Muon poate fi încercat din nou altfel: de la zero, sau cu o pornire mai lentă. Asta doar dacă vrei tu.
   - Modelele noi (#441, #443) **nu** sunt în interfață.
3. **Rămase de ieri, fără răspuns:**
   - Ora raportului: pornește acum la 06:40, nu la 07:40, din cauza orei de iarnă. Ca să-l muți înapoi, trebuie schimbată sarcina Windows „Kronos raport dimineata”: o schimbi tu sau îmi dai voie.
   - S28 (oprirea calculatorului) e încă `oprit`. Spune-mi dacă o trec la `gata`.
