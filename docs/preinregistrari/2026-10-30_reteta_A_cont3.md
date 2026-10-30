# Pre-înregistrare: S51, repetarea S45 — a doua continuare a liniei w2 cu rețeta A, 6 ore din #459

<!-- scrisa: 2026-10-30T19:00:00 -->
*Scrisă la 2026-10-30 19:00, la S51, ÎNAINTE de antrenare (nicio antrenare S51 nu a pornit; `lucru/w2_reteta_A_cont3/` nu există —
verificat la 18:59:32). După ce rularea a început, textul de mai jos nu se mai schimbă; la închidere se adaugă doar „Ce a ieșit” și
„Verdictul” (`python unelte/preinregistrare.py --inchide reteta_A_cont3`).*

## Cine a ales

Supraveghetorul (30 oct 02:15, granița 1 din `plan/REGULI_CASCADA.md`: încă o rulare pe linia w2 existentă, același amestec, nimic
descărcat), ca **repetare a S45**, care a căzut fără verdict (procesul întrerupt la 29 oct 23:09:36, ora 4/6, fără eroare și fără cod
de ieșire; examenele n-au rulat; pre-înregistrarea `2026-10-29_reteta_A_cont2.md` e închisă „fără verdict (întreruptă); se repetă ca
S51”). Ordinea: supraveghetor, 30 oct 11:15 (S51 la 19:00, înaintea bucății 2 a S46). Pragurile de mai jos sunt cele din
`plan/coada.md` (S51), copiate exact din S45. Configurarea și această pre-înregistrare: Claude Code (executantul).

## Întrebarea

S38 a CONFIRMAT că 6 ore în plus cu rețeta A, din #441, aduc câștig real: #459 **1,2162** pe română curat (−0,017), cu cod și
TinyStories R2 mai bune. **Mai aduce încă o noapte (6 ore) cu aceeași rețetă, pornind din #459, un câștig real pe română (cel puțin
−0,005), fără să strice codul și poveștile?** (Aceeași întrebare ca la S45, care a rămas fără răspuns.)

## Ce rulează

Un singur proces, prin cascadă (`cascada.py porneste S51 -- python lucru/cascada/S51_proba/s51.py`), pașii pe rând, oprire la
primul cod diferit de 0:
1. **Antrenarea:** `python unelte/antrenare_lunga.py --config config/conv_w2_reteta_A_cont3.toml --ore 6 --porneste-din 459`.
   `config/conv_w2_reteta_A_cont3.toml` = copie a `config/conv_w2_reteta_A_cont2.toml` (S45), cu doar `nume = "w2_reteta_A_cont3"`,
   `cale_stare`, eticheta și antetul schimbate (diff-ul în raport). Același amestec de date, aceeași răcire (ultimele 25 % din 6 ore).
2. **Examenele, o singură rulare:** `unelte/examen_validari_ws.py --linie w2_reteta_A_cont3` (ultimul model, ora 6), apoi, în același
   proces, `unelte/examen_validari_ws.py --experiment 459` (#459, re-măsurat ca reper).
   Din antrenare (examenele lui Kronos de la fiecare oră): val_bpb pe TinyStories R2 și faptele noi (din 150).

Ora estimată de sfârșit: **~01:30** (6 ore + pauzele dintre ore + ~2 minute de examene; S38 a durat 19:34–01:57; pornire ~19:01).
Placa: S45 a mers la ~6.116 MB cu aceleași loturi (12); paznicul oprește peste 7.000 MB sau 83 °C.

## Măsurile (fixate acum)

- **română** = `bpb_romana_curat` din `unelte/examen_validari_ws.py`, pe ultimul model al liniei noi (ora 6). Reper: #459 **1,2162**
  (re-măsurat în aceeași rulare; dacă iese altceva, contează cifra din rulare și o spun).
- **cod** = `bpb_cod_curat` (#459 **0,7321**); **TinyStories R2** = val_bpb oficial al ultimului model (#459 **0,4084**).
- Alături (NU decid): fapte noi din 150 (#459 73), `bpb_romana` necurățat, val_bpb de la fiecare oră; orele 1–3 ale S45
  (#469 0,4185 / #470 0,4167 / #471 0,4150) ca termen de comparație al mersului pe ore.

## Pragurile (din S51 = S45, cuvânt cu cuvânt)

- **CONFIRMAT** dacă română curat ≤ **1,2112**, fără regresie > 0,005 la cod curat (≤ **0,7371**) și R2 (≤ **0,4134**);
- **INFIRMAT** dacă > **1,2142**;
- **între ele: NECLAR.**

Cum le citesc (scris acum, ca să nu aleg după): „fără regresie > 0,005” = cod curat ≤ 0,7321 + 0,005 = **0,7371** și TinyStories R2
≤ 0,4084 + 0,005 = **0,4134**. Dacă română ≤ 1,2112, dar una dintre regresii depășește 0,005, verdictul e **NECLAR** (câștig pe
română, cu preț), nu CONFIRMAT. Pragurile 1,2112 / 1,2142 / 0,7371 / 0,4134 sunt fixe (din coadă), chiar dacă #459 re-măsurat iese
puțin altfel.

## Să nu uite

- E repetarea S45 (căzută la 23:09:36 fără eroare). Dacă procesul cade din nou fără eroare: `oprit`, raport cu **ora exactă a
  căderii**, **nu** se repornește singur.
- O singură sămânță și o singură rulare; o diferență mică poate fi și noroc; NECLAR e NECLAR.
- Rata urcă din nou la 0,00005 după încălzire (100 de pași), pornind dintr-un model deja răcit la 0: la S38 primele 4 ore au fost
  **mai rele** decât modelul de plecare la val_bpb; contează doar ultimul model (ora 6), nu se aleg orele după rezultat.
- Comparația e „#459 + 6 ore” față de „#459”; nu spune dacă o singură răcire lungă ar fi fost mai bună.
- Verific în log rândul „Pornesc din modelul experimentului #459” (lecția S42: fără el, antrenarea pornește de la zero → `oprit`).
- Dacă pică un pas, lanțul se oprește; nu se repornește pe ascuns. Peste 7.000 MB sau 83 °C → `oprit`.
- Modelul nou NU intră în interfață și nu înlocuiește #459 în OS fără alt „da”. Nu se ating `kronos/`, `module/examen_bpb.py`,
  `module/model_muon.py`, paznicul, jurnalul, datele de examen, #441, #459 și liniile/configurările existente.

## Așteptările mele (în cifre)

- Ultimul model (ora 6): română curat **~1,207**; TinyStories R2 **~0,404**; cod curat **~0,725**; fapte noi **~70–75**
  (aceleași ca la S45: nimic nou nu s-a aflat, orele 1–3 ale S45 au mers ca la S38).
- #459 re-măsurat: 1,2162.
- Δ română față de #459 așteptat: **~−0,009**. Șansele: CONFIRMAT ~55 %, NECLAR ~25 %, INFIRMAT ~20 %.
- Șansa ca procesul să cadă din nou înainte de ora 6 (cauza căderii S45 e încă necunoscută, S52 n-a putut citi jurnalele Windows):
  ~20 %.

## Ce ar infirma așteptările

- Română > 1,2142: a doua continuare din modelul răcit nu mai aduce câștig real (linia s-a plafonat la rata asta) → INFIRMAT.
- Cod curat sau TinyStories R2 cu peste 0,005 mai rău: câștigul pe română se plătește pe celelalte → cel mult NECLAR.

## Ce a ieșit

*Notă (executant): titlul „## Ce a ieșit” era deja pus, gol, în fișierul urcat la 18:59:58 (5344b50), așa că --inchide a refuzat
(„deja închisă”). Conținutul de mai jos e generat cu aceleași funcții ale uneltei (ce_a_iesit), adăugat doar sub titlul gol; textul
de deasupra n-a fost atins.*


*Adăugat la 2026-10-31 01:30, din jurnalul Kronos (lucru/jurnal/experimente.jsonl) și din jurnalul CONTINUUM pe bune. Verdictul se scrie dedesubt.*

| # | linia | început | val_bpb | decizia | fapte noi | fapte | nota | motivul |
|---|---|---|---|---|---|---|---|---|
| 472 | w2_reteta_A_cont3 | 30.10 19:00 | 0,4187 | pastrat | — | — | — |  |
| 473 | w2_reteta_A_cont3 | 30.10 20:05 | 0,4162 | pastrat | — | — | — |  |
| 474 | w2_reteta_A_cont3 | 30.10 21:08 | 0,4151 | pastrat | — | — | — |  |
| 475 | w2_reteta_A_cont3 | 30.10 22:12 | 0,4155 | pastrat | — | — | — |  |
| 476 | w2_reteta_A_cont3 | 30.10 23:16 | 0,4118 | pastrat | — | — | — |  |
| 477 | w2_reteta_A_cont3 | 31.10 00:20 | 0,4060 | pastrat | — | — | — |  |
| 478 | examen_validari_ws | 31.10 01:23 | — | masurat | — | — | — |  |
| 479 | examen_validari_ws | 31.10 01:23 | — | masurat | — | — | — |  |

- **w2_reteta_A_cont3:** 6 ore, 6 păstrate; val_bpb de la 0,4187 la 0,4060; cel mai bun păstrat: #477 (0,4060); pornită din #459 (0,4084).

Niciun ciclu CONTINUUM pe bune în perioada asta.

- Antrenarea: 19:00:09 → 01:22:57, cod 0; rândul „Pornesc din modelul experimentului #459 (linia „w2_reteta_A_cont”, ora 6,
  val_bpb 0.4084)” e în log ✓ (nu a pornit de la zero). 137.824 de pași, 847 M de simboluri, 6,4 pași/s. **Procesul NU a căzut.**
- Pe ore (TinyStories R2): 0,4187 / 0,4162 / 0,4151 / 0,4155 / 0,4118 / **0,4060**; fapte noi 72 / 80 / 71 / 79 / 75 / **75** (din 150).
  Orele 1–3 aproape identice cu ale S45 (0,4185 / 0,4167 / 0,4150).
- Examenele (`examen_validari_ws.py`, aceeași rulare, 01:22:57–01:23:26, cod 0):

| măsura | #477 (ora 6, linia nouă) | #459 (reper, re-măsurat) | Δ |
|---|---|---|---|
| **română curat** | **1,2097** | 1,2162 | −0,0065 |
| **cod curat** | **0,7270** | 0,7321 | −0,0051 |
| **TinyStories R2** (val_bpb oficial) | **0,4060** | 0,4084 | −0,0024 |
| română necurățat | 1,2274 | 1,2339 | −0,0065 |
| cod necurățat | 0,6606 | 0,6654 | −0,0048 |

- #459 re-măsurat a ieșit exact ca reperul (1,2162 / 0,7321).
- Placa (`lucru/w2_reteta_A_cont3/placa_20261030_1900.csv`, 2.276 de citiri): maxim **6.002 MB**, maxim **64 °C** (sub 7.000 MB și 83 °C).

## Verdictul

*Scris la 2026-10-31 01:30, de executant, strict după pragurile de mai sus.*

**CONFIRMAT.**

- română curat **1,2097 ≤ 1,2112** ✓ (pragul CONFIRMAT; INFIRMAT ar fi fost > 1,2142);
- cod curat **0,7270 ≤ 0,7371** ✓ (mai bun cu 0,005 decât #459, nu regresie);
- TinyStories R2 **0,4060 ≤ 0,4134** ✓ (mai bun cu 0,0024).

Față de așteptări: Δ română −0,0065 (așteptat ~−0,009; câștig mai mic decât credeam, dar trece pragul cu 0,0015). Cod 0,727 și
R2 0,406, aproape exact cum le așteptam (~0,725 / ~0,404). Fapte noi 75 (așteptat 70–75).

Ce NU spune: o singură sămânță; marja față de pragul CONFIRMAT e mică (0,0015), deci o parte din câștig poate fi noroc. Câștigul
celei de-a doua nopți (−0,0065) e mai mic decât al primei (−0,017 la S38): linia începe să se aplatizeze la rata asta. Modelul #477
NU intră în interfață și nu înlocuiește #459 în OS fără alt „da”.
