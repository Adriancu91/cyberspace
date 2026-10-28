# Pre-înregistrare: S38, continuarea liniei w2 cu rețeta A, 6 ore din #441

<!-- scrisa: 2026-10-27T19:29:53 -->
*Scrisă la 2026-10-27 19:29, la S38, ÎNAINTE de antrenare (nicio antrenare S38 nu a pornit; `lucru/w2_reteta_A_cont/` nu există).
După ce rularea a început, textul de mai jos nu se mai schimbă; la închidere se adaugă doar „Ce a ieșit” și „Verdictul”
(`python unelte/preinregistrare.py --inchide reteta_A_cont`).*

## Cine a ales

Adrian (27 oct 18:00, prin centrul de comandă, delegarea din DECIZII 26 oct 17:45), cu pragurile de mai jos scrise de supraveghetor
în `plan/coada.md` (S38). Configurarea și această pre-înregistrare: Claude Code (executantul).

## Întrebarea

S34 a CONFIRMAT că rețeta A (AdamW prin `module.model_muon` + gradient adunat pe 8 loturi + răcire liniară la 0 în ultimele 25 %)
aduce câștig real în 2 ore din #415: #441 **1,2332** pe română curat (cel mai bun model de până acum). **Mai aduce încă 6 ore cu
aceeași rețetă, pornind din #441, un câștig real pe română, fără să strice codul și poveștile?**
S36 (proba D, fără adunare) a dat NECLAR, deci, după regula din coadă, continuarea folosește rețeta A (cu adunare), nu D.

## Ce rulează

Un singur proces, prin cascadă (`cascada.py porneste S38 -- python lucru/cascada/S38_proba/s38.py`), pașii pe rând, oprire la
primul cod diferit de 0:
1. **Antrenarea:** `python unelte/antrenare_lunga.py --config config/conv_w2_reteta_A_cont.toml --ore 6 --porneste-din 441`.
   `config/conv_w2_reteta_A_cont.toml` = copie a `config/conv_w2_muon_A.toml`, cu doar `nume = "w2_reteta_A_cont"`, `cale_stare`,
   eticheta, antetul și `durata_scaderii_secunde = 21600` schimbate (răcirea în ultimele 25 % din cele 6 ore; diff-ul în raport).
2. **Examenele, o singură rulare:** `unelte/examen_validari_ws.py --linie w2_reteta_A_cont` (ultimul model, ora 6), apoi, în același
   proces, `unelte/examen_validari_ws.py --linie w2_muon_A` (#441, re-măsurat ca reper).
   Din antrenare (examenele lui Kronos de la fiecare oră): val_bpb pe TinyStories R2 și faptele noi (din 150).

Ora estimată de sfârșit: **~01:55** (6 ore + pauzele dintre ore + ~2 minute de examene; la S31, A a durat 2 h 07 min pentru 2 ore;
pornire ~19:35). Placa: A a mers sub 6.000 MB cu aceleași loturi (12); paznicul oprește peste 7.000 MB sau 83 °C.

## Măsurile (fixate acum)

- **română** = `bpb_romana_curat` din `unelte/examen_validari_ws.py`, pe ultimul model al liniei noi (ora 6). Reper: #441 **1,2332**
  (re-măsurat în aceeași rulare; dacă iese altceva, contează cifra din rulare și o spun).
- **cod** = `bpb_cod_curat` (#441 **0,7460**); **TinyStories R2** = val_bpb oficial al ultimului model (#441 **0,4154**).
- Alături (NU decid): fapte noi din 150 (#441 76), `bpb_romana` necurățat, val_bpb de la fiecare oră.

## Pragurile (din S38, cuvânt cu cuvânt)

- **CONFIRMAT** dacă română curat ≤ **1,2232** (−0,010 față de #441), fără regresie > 0,005 la cod curat și TinyStories R2;
- **INFIRMAT** dacă română curat > **1,2282**;
- **între ele: NECLAR.**

Cum le citesc (scris acum, ca să nu aleg după): „fără regresie > 0,005” = cod curat ≤ 0,7460 + 0,005 = **0,7510** și TinyStories R2
≤ 0,4154 + 0,005 = **0,4204** (față de cifrele lui #441 din aceeași rulare, respectiv din jurnal). Dacă română ≤ 1,2232, dar una dintre
regresii depășește 0,005, verdictul e **NECLAR** (câștig pe română, cu preț), nu CONFIRMAT.

## Să nu uite

- O singură sămânță și o singură rulare; o diferență mică poate fi și noroc; NECLAR e NECLAR.
- Rata urcă din nou la 0,00005 după încălzire (100 de pași), pornind dintr-un model deja răcit la 0: primele ore pot ieși **mai rele**
  decât #441 la val_bpb; contează doar ultimul model (ora 6), nu se aleg orele după rezultat.
- Comparația e „#441 + 6 ore” față de „#441”, nu față de „#415 + 8 ore dintr-o bucată”: nu spune dacă o răcire lungă unică ar fi mai bună.
- Dacă pică un pas, lanțul se oprește; nu se repornește pe ascuns (de 2 ori aceeași eroare → `oprit`). Peste 7.000 MB → `oprit`.
- Modelul nou NU intră în interfață. Nu se ating `kronos/`, `module/examen_bpb.py`, `module/model_muon.py`, paznicul, jurnalul,
  datele de examen, #415, #441, #447, #451 și liniile/configurările existente.

## Așteptările mele (în cifre)

- Ultimul model (ora 6): română curat **~1,220** (A a câștigat 0,053 în 2 ore din #415; de aici câștigul e mai mic, iar o parte din efectul
  răcirii era deja în #441); TinyStories R2 **~0,410**; cod curat **~0,744**; fapte noi **~75–78**.
- #441 re-măsurat: 1,2332 (aceeași cifră ca la S31, S34, S36).
- Δ română față de #441 așteptat: **~−0,013**. Șansele: CONFIRMAT ~45 %, NECLAR ~30 %, INFIRMAT ~25 %.

## Ce ar infirma așteptările

- Română > 1,2282: continuarea din modelul răcit nu mai aduce câștig real (eventual reîncălzirea strică ce a adus răcirea) → INFIRMAT.
- Cod curat sau TinyStories R2 cu peste 0,005 mai rău: câștigul pe română se plătește pe celelalte → cel mult NECLAR.

## Ce a ieșit

*Adăugat la 2026-10-28 06:29, din jurnalul Kronos (lucru/jurnal/experimente.jsonl) și din jurnalul CONTINUUM pe bune. Verdictul se scrie dedesubt.*

| # | linia | început | val_bpb | decizia | fapte noi | fapte | nota | motivul |
|---|---|---|---|---|---|---|---|---|
| 454 | w2_reteta_A_cont | 27.10 19:34 | 0,4233 | pastrat | — | — | — |  |
| 455 | w2_reteta_A_cont | 27.10 20:38 | 0,4194 | pastrat | — | — | — |  |
| 456 | w2_reteta_A_cont | 27.10 21:42 | 0,4193 | pastrat | — | — | — |  |
| 457 | w2_reteta_A_cont | 27.10 22:46 | 0,4182 | pastrat | — | — | — |  |
| 458 | w2_reteta_A_cont | 27.10 23:50 | 0,4153 | pastrat | — | — | — |  |
| 459 | w2_reteta_A_cont | 28.10 00:54 | 0,4084 | pastrat | — | — | — |  |
| 460 | examen_validari_ws | 28.10 01:57 | — | masurat | — | — | — |  |
| 461 | examen_validari_ws | 28.10 01:57 | — | masurat | — | — | — |  |

- **w2_reteta_A_cont:** 6 ore, 6 păstrate; val_bpb de la 0,4233 la 0,4084; cel mai bun păstrat: #459 (0,4084); pornită din #441 (0,4154).

Niciun ciclu CONTINUUM pe bune în perioada asta.

Examenele (`unelte/examen_validari_ws.py`, aceeași rulare, 28 oct 01:57):

| măsura | #459 (ora 6) | #441 (re-măsurat) | Δ | pragul |
|---|---|---|---|---|
| română curat | **1,2162** | 1,2332 | −0,0170 | ≤ 1,2232 CONFIRMAT / > 1,2282 INFIRMAT |
| cod curat | 0,7321 | 0,7460 | −0,0139 | ≤ 0,7510 |
| TinyStories R2 (val_bpb) | 0,4084 | 0,4154 | −0,0070 | ≤ 0,4204 |
| fapte noi (din 150, nu decide) | 73 | 76 | −3 | — |
| română necurățat (nu decide) | 1,2339 | 1,2521 | −0,0182 | — |

## Verdictul

**CONFIRMAT** (scris de executant, 28 oct 06:33). Română curat 1,2162 ≤ 1,2232 (Δ −0,0170 față de #441, 1,2332 și în rularea asta);
cod curat 0,7321 ≤ 0,7510 și TinyStories R2 0,4084 ≤ 0,4204 — nicio regresie, ba chiar ambele mai bune. Așteptarea mea (~1,220,
Δ ~−0,013) a fost puțin prea prudentă. Ca de obicei: o singură sămânță și o singură rulare. Faptele noi au scăzut ușor (76 → 73),
dar nu decid. Primele 4 ore au fost mai rele decât #441 la val_bpb (cum scria la „Să nu uite”); câștigul a venit în răcire (orele 5–6).
