# Pre-înregistrare: E2 (S23): „3 specialiști + ruter”, antrenați pe rând din #415 (Branch-Train-Merge)

<!-- scrisa: 2026-10-23T10:35:00 -->
*Scrisă la 2026-10-23 10:35, la S22, pe procesor, ÎNAINTE de S23 (nicio antrenare nu a pornit). După ce S23 începe,
textul de mai jos nu se mai schimbă; la închidere se adaugă doar „Ce a ieșit” și „Verdictul”
(`python unelte/preinregistrare.py --inchide E2_specialisti`).*

## Cine a ales

Adrian a aprobat E2 pe 23 oct 10:20 (centrul de comandă, punctul 2: „E2 aprobat, antrenare nouă”), după închiderea lui E1
cu „neclar” (S20, varianta 1). Supraveghetorul a pus S22 (pregătirea) și S23 (rularea) în coadă la 10:30. Experimentul e
§4 H4 și §7 E2 din `docs/rapoarte/2026-10-22_0200_strategie_nucleu_fara_llm.md`. Pregătirea (unealta
`unelte/e2_specialisti.py`, testele, datele, ruterul, configurările și această pre-înregistrare) e făcută de Claude Code
(executantul), pe procesor, fără placă.

## Întrebarea

Pot 3 specialiști mici (copii ale lui #415, fiecare antrenat 2 ore pe o singură familie de întrebări) plus un ruter fără
model (primele cuvinte ale întrebării) să facă **cel puțin cât monolitul #415**, fără ca vreun specialist să piardă pe
familia lui?

## Familiile (regula fixă, aceeași la antrenare și la examene, fără model)

- **F2 „da/nu”:** răspunsul de referință, normalizat, e „da” sau „nu” (exact „Da.”/„Nu.”);
- **F3 „tipurile din S11”:** tipul perechii e unul din cele adăugate la S11 (`date/conversatie/text_v3/tipuri_noi.jsonl`) și
  nu e da/nu; la examene asta înseamnă **exact S15 (e)** (verificat automat: toate cele 30 și numai ele);
- **F1 „fapte / nume / ani / locuri”:** tot restul, inclusiv „Nu scrie în text.” al tipurilor vechi și conversația simplă
  (cele 45 de „Da, știu română…” din conversația simplă nu sunt „Da.” și rămân în F1).

| familia | perechi de antrenare (din 27.468) | din care „text” / „Nu scrie” / conversație | la examene (210) |
|---|---|---|---|
| F1 | **20.564** | 15.534 / 4.780 / 250 | 165 (S15 b2 50, S4 a+b+d 45, noaptea 10 70) |
| F2 | **4.083** | 4.083 / 0 / 0 | 15 (S4 c) |
| F3 | **2.821** | 2.157 / 664 / 0 | 30 (S15 e) |

Suma = 27.468 (verificat automat). Nicio familie sub 2.000. Fișierele: `date/conversatie/e2/f1|f2|f3/antrenare.jsonl`,
`date/conversatie/e2/info.json`. Specialiștii se antrenează pe **toată** familia lor (cu tot cu cele 10 % puse deoparte
pentru ruter).

## Ruterul (fără model) și cât de bine alege

Tabel învățat doar din întrebările de antrenare, fără cele 10 % din articole puse deoparte (1.252 din 12.521 de grupuri,
sămânța 1023; 2.770 de perechi de validare). Pentru fiecare început de întrebare (litere mici, fără semne), familia cea
mai des întâlnită; se folosește cel mai lung început găsit; altfel F1. `date/conversatie/e2/ruter.json`.

**Ajustarea (doar după (i), cum cere S22):** am încercat 12 variante **numai pe validare** (începuturi de 1–3 / 1–4 / 1–5
cuvinte × pragul 2 / 3 / 5 / 10). Varianta din sarcină (1–3 cuvinte, prag 5) dă 92,2 % (F2 71,3 %, F3 70,0 %); cea mai
bună, **1–5 cuvinte, prag 2**, dă **93,7 %** (F1 99,4 %, F2 72,5 %, F3 82,3 %). Am ales-o pe ea. Limita se vede în greșeli:
întrebările care încep cu un nume („Marius Nae s-a născut în 1981?”) nu se pot recunoaște după primele cuvinte, oricâte.

**(ii) pe cele 210 întrebări de examen, rulat o singură dată, cu ruterul final:**

| grup | corect |
|---|---|
| S15 (b2) | 41/50 (9 trimise la F3: „Pe ce post joacă …”, „Pe ce canal …”, „Al cui tablou …”) |
| S15 (e) | 21/30 (8 la F1, 1 la F2: „X este din ce familie?”, „X a fost descrisă în ce an?”) |
| S4 (a) / (b) / (c) / (d) | 13/15 / 15/15 / 14/15 / 15/15 |
| noaptea 10 „text” / „Nu scrie” | 50/50 / 20/20 |
| pe familii: F1 / F2 / F3 | 154/165 (93,3 %) / 14/15 (93,3 %) / 21/30 (70,0 %) |
| **total** | **189/210 = 90,0 %** — poarta S22 (≥ 90 %) trece, **exact la limită** |

## Baseline: #415 pe familii (din `lucru/e1/examene_415_20261023_023327.json`, verificatorul S16)

| | verificator | F1 ≥ 0,8 | lungi corecte |
|---|---|---|---|
| F1 (165) | **101** | 98 | 3 |
| F2 (15) | **13** | 13 | 0 |
| F3 (30) | **30** | 28 | 0 |
| **total (210)** | **144** | 139 | 3 |
| S15 (b2) | 6/50 | 4/50 | 2 |

Verificarea cerută de S22: (b2) 6 + (e) 30 + S4 38 + noaptea 10 50 + 20 = **144/210** ✓.

## Ce rulează (S23, un singur lanț prin cascadă, fiecare pas doar dacă cel dinainte a ieșit cu cod 0)

1. `python unelte/antrenare_lunga.py --config config/conv_w2_spec_f1.toml --ore 2 --porneste-din 415`
2. la fel cu `config/conv_w2_spec_f2.toml`, **tot din #415**, 2 ore;
3. la fel cu `config/conv_w2_spec_f3.toml`, din #415, 2 ore;
4. examenele pe ultimul model al fiecărei linii (`w2_spec_f1/f2/f3`):
   `python -X utf8 unelte/e1_intrebari_nascute.py --lucru lucru/e2 examene --linie w2_spec_fX` + `unelte/examen_validari_ws.py`;
5. `python -X utf8 unelte/e2_specialisti.py sistem --specialisti F1=<examene f1> F2=<examene f2> F3=<examene f3>`
   (monolitul implicit: examenele #415 de mai sus).

Configurările sunt copii ale `config/conv_w2_text_v3.toml` (noaptea 12, din care a ieșit #415); diferă doar `nume`
(`w2_spec_f1/f2/f3`), `conversatie` (fișierul familiei) și `cale_stare` (`lucru/w2_spec_fX/gpt.pt`) — 2 rânduri, verificat cu
`diff`. Restul identic: 45 % perechi / 5 % hrană / 50 % text vechi, rata 0,00005, lot 12, context 512. Directoarele
`lucru/w2_spec_*` nu există (verificat la 10:33), deci `--porneste-din 415` se aplică.
Durata: 3 × ~2 h 10 + ~25 min examene ≈ **7 ore** pe placă. Paznicul: sub 7.000 MB și 83 °C.

## Criteriile (ale lui Adrian, 23 oct 10:20, copiate din S22)

- **CONFIRMAT:** (A) **fără regresie pe niciun specialist**: specialistul k, pe întrebările familiei k din S4 + S15 +
  noaptea 10, are cel puțin cât #415 pe aceleași întrebări, minus 1; și validările (val_bpb, română, cod, povești, fapte noi)
  în aceleași praguri ca la S17; **și** (B) **sistemul (ruter + specialiști) ≥ #415 monolit** pe toate cele 210 întrebări
  (≥ 144, cu verificatorul S16); **și** (C) **ruterul alege corect ≥ 90 %** (cifra de la pasul 3 (ii)).
- **INFIRMAT:** oricare din (A), (B), (C) nu e îndeplinit → scrii care, cu cifrele.
- **În plus, fără să decidă:** sistemul și #415 cu F1 ≥ 0,8 (pe (b2) separat), răspunsurile „lungi” (ca la S21), sistemul
  cu „ruter perfect” (familia corectă) — ca să vedem cât pierde ruterul.

În cifre, cu baseline-ul de mai sus:
- (A) specialistul F1 pe F1 **≥ 100/165**; specialistul F2 pe F2 **≥ 12/15**; specialistul F3 pe F3 **≥ 29/30**;
  validările fiecărui specialist: română ≤ 1,3133; cod ≤ 0,8174; povești ≤ 0,47; fapte noi ≥ 65 (pragurile S17).
  **val_bpb:** S17 n-a avut prag numeric pentru val_bpb (doar l-a raportat); îl scriu acum, alegerea mea:
  **val_bpb ≤ 0,4511** (#415: 0,4411, plus 0,01). Dacă supraveghetorul vrea alt prag, îl schimbă **înainte** de S23.
- (B) sistemul **≥ 144/210**.
- (C) **90,0 % ≥ 90 %: îndeplinit** (deja măsurat; nu se mai măsoară).

## Așteptările mele, în cifre

- **Specialistul F1** pe F1: **98–106/165** (cel mai probabil ~101); (b2) 5–9/50.
- **Specialistul F2** pe F2: **13–15/15** (da/nu e ușor, și are 2 ore doar pe asta).
- **Specialistul F3** pe F3: **28–30/30**; riscul principal la (A): 2.821 de perechi, repetate de multe ori în 2 ore —
  dacă scade la 28, (A) cade.
- **Întrebările trimise greșit** (21): un specialist antrenat 2 ore fără familia respectivă poate uita puțin (de exemplu
  F1 care primește 8 din (e), F3 care primește 9 din (b2)); cred că pierde 1–4 față de #415 pe ele.
- **Sistemul:** **138–148/210** (cel mai probabil ~143); cu „ruter perfect” cu 1–4 mai mult.
- **Validările:** toate în praguri (sunt aceleași amestecuri ca noaptea 12, doar perechile diferă).
- **Verdictul pe care îl aștept:** **INFIRMAT ~65 %** (cel mai probabil prin (B) sub 144 sau (A) la F3), **CONFIRMAT ~35 %**.

## Ce trebuie știut la citirea rezultatelor

- **Ruterul trece (C) exact la limită (189/210 = 90,0 %)**, după o ajustare făcută doar pe validare. Cu varianta din
  sarcină (1–3 cuvinte, prag 5) cifra pe examene nu e cunoscută (n-am rulat-o: (ii) se rulează o singură dată).
- Cele 21 de greșeli ale ruterului cad mai ales pe (b2) și (e); (B) depinde mult de ce răspund specialiștii la întrebările
  care nu sunt ale lor.
- F3 la examene = S15 (e), pe care #415 are deja 30/30: aici specialistul F3 nu poate decât să egaleze sau să piardă.
- Cele 7 ore pe placă sunt doar pentru S23; specialiștii nu intră în interfață (rămâne #407).

## Ce a ieșit

*Adăugat la 2026-10-23 18:03, din jurnalul Kronos (lucru/jurnal/experimente.jsonl) și din jurnalul CONTINUUM pe bune. Verdictul se scrie dedesubt.*

| # | linia | început | val_bpb | decizia | fapte noi | fapte | nota | motivul |
|---|---|---|---|---|---|---|---|---|
| 427 | w2_spec_f1 | 23.10 11:00 | 0,4438 | pastrat | — | — | — |  |
| 428 | w2_spec_f1 | 23.10 12:05 | 0,4432 | pastrat | — | — | — |  |
| 429 | w2_spec_f2 | 23.10 13:08 | 0,4403 | pastrat | — | — | — |  |
| 430 | w2_spec_f2 | 23.10 14:12 | 0,4447 | pastrat | — | — | — |  |
| 431 | w2_spec_f3 | 23.10 15:15 | 0,4441 | pastrat | — | — | — |  |
| 432 | w2_spec_f3 | 23.10 16:19 | 0,4449 | pastrat | — | — | — |  |
| 433 | examen_validari_ws | 23.10 17:25 | — | masurat | — | — | — |  |
| 434 | examen_validari_ws | 23.10 17:28 | — | masurat | — | — | — |  |
| 435 | examen_validari_ws | 23.10 17:30 | — | masurat | — | — | — |  |

- **w2_spec_f1:** 2 ore, 2 păstrate; val_bpb de la 0,4438 la 0,4432; cel mai bun păstrat: #428 (0,4432); pornită din #415 (0,4411).
- **w2_spec_f2:** 2 ore, 2 păstrate; val_bpb de la 0,4403 la 0,4447; cel mai bun păstrat: #429 (0,4403); pornită din #415 (0,4411).
- **w2_spec_f3:** 2 ore, 2 păstrate; val_bpb de la 0,4441 la 0,4449; cel mai bun păstrat: #431 (0,4441); pornită din #415 (0,4411).

Niciun ciclu CONTINUUM pe bune în perioada asta.

Examenele (verificatorul S16): specialiștii #428 (F1), #430 (F2), #432 (F3); nota sistemului în `lucru/e2/sistem_s23.json`.

| | #415 monolit | specialistul familiei | sistem (ruter) | sistem (ruter perfect) |
|---|---|---|---|---|
| F1 (165) | 101 | **98** (#428) | 99 | 98 |
| F2 (15) | 13 | **14** (#430) | 15 | 14 |
| F3 (30) | 30 | **30** (#432) | 23 | 30 |
| **total (210)** | **144** | — | **137** | **142** |
| F1 ≥ 0,8 (total) | 139 | — | 130 | 138 |
| S15 (b2), verificator / F1 ≥ 0,8 | 6 / 4 | — | 8 / 3 | 6 / 4 |
| lungi corecte | 3 | — | 6 | 4 |

Validările (prag S17 / pre-înregistrare): val_bpb ≤ 0,4511 → 0,4432 / 0,4447 / 0,4449 ✓; română ≤ 1,3133 → 1,3116 / 1,3093 /
1,3120 ✓; cod ≤ 0,8174 → 0,7266 / 0,7256 / 0,7332 ✓; povești ≤ 0,47 → 0,4432 / 0,4447 / 0,4449 ✓; fapte noi ≥ 65 → 72 / 73 / 65 ✓
(F3 exact la limită).

## Verdictul

**INFIRMAT.** Strict după pragurile de mai sus:
- **(A) nu e îndeplinit:** specialistul F1 are **98/165** pe familia lui, pragul era ≥ 100 (#415: 101, minus 1). F2 14/15 ≥ 12 ✓,
  F3 30/30 ≥ 29 ✓; toate validările în praguri ✓.
- **(B) nu e îndeplinit:** sistemul are **137/210**, pragul era ≥ 144 (minus 7). Nici cu ruter perfect nu ar fi trecut (142).
- **(C) îndeplinit:** 189/210 = 90,0 % (măsurat la S22).

Față de așteptări: F1 98 (capătul de jos al 98–106), F2 14 și F3 30 în interval; sistemul 137, sub intervalul 138–148.
Verdictul așteptat cu ~65 % (INFIRMAT) s-a adeverit, dar prin (A) la F1 și (B), nu la F3. Ruterul pierde 5 întrebări față de
„ruterul perfect” (mai ales cele 9 din S15 (e) trimise greșit: 23/30 în loc de 30/30).
