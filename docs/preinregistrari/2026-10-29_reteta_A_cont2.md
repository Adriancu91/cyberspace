# Pre-înregistrare: S45, a doua continuare a liniei w2 cu rețeta A, 6 ore din #459

<!-- scrisa: 2026-10-29T19:00:31 -->
*Scrisă la 2026-10-29 19:00, la S45, ÎNAINTE de antrenare (nicio antrenare S45 nu a pornit; `lucru/w2_reteta_A_cont2/` nu există).
După ce rularea a început, textul de mai jos nu se mai schimbă; la închidere se adaugă doar „Ce a ieșit” și „Verdictul”
(`python unelte/preinregistrare.py --inchide reteta_A_cont2`).*

## Cine a ales

Centrul de comandă, prin delegarea lui Adrian din 26 oct 17:45 (29 oct 08:25), confirmat de supraveghetor (29 oct 11:15, granița 1:
încă o rulare pe linia w2 existentă, același amestec, nimic descărcat), cu pragurile de mai jos scrise în `plan/coada.md` (S45).
Configurarea și această pre-înregistrare: Claude Code (executantul).

## Întrebarea

S38 a CONFIRMAT că 6 ore în plus cu rețeta A, din #441, aduc câștig real: #459 **1,2162** pe română curat (−0,017), cu cod și
TinyStories R2 mai bune. **Mai aduce încă o noapte (6 ore) cu aceeași rețetă, pornind din #459, un câștig real pe română (cel puțin
−0,005), fără să strice codul și poveștile?**

## Ce rulează

Un singur proces, prin cascadă (`cascada.py porneste S45 -- python lucru/cascada/S45_proba/s45.py`), pașii pe rând, oprire la
primul cod diferit de 0:
1. **Antrenarea:** `python unelte/antrenare_lunga.py --config config/conv_w2_reteta_A_cont2.toml --ore 6 --porneste-din 459`.
   `config/conv_w2_reteta_A_cont2.toml` = copie a `config/conv_w2_reteta_A_cont.toml` (S38), cu doar `nume = "w2_reteta_A_cont2"`,
   `cale_stare`, eticheta și antetul schimbate (diff-ul în raport). Același amestec de date, aceeași răcire (ultimele 25 % din 6 ore).
2. **Examenele, o singură rulare:** `unelte/examen_validari_ws.py --linie w2_reteta_A_cont2` (ultimul model, ora 6), apoi, în același
   proces, `unelte/examen_validari_ws.py --experiment 459` (#459, re-măsurat ca reper).
   Din antrenare (examenele lui Kronos de la fiecare oră): val_bpb pe TinyStories R2 și faptele noi (din 150).

Ora estimată de sfârșit: **~01:25** (6 ore + pauzele dintre ore + ~2 minute de examene; S38 a durat 19:34–01:57; pornire ~19:05).
Placa: S38 a mers la ~5.913 MB cu aceleași loturi (12); paznicul oprește peste 7.000 MB sau 83 °C.

## Măsurile (fixate acum)

- **română** = `bpb_romana_curat` din `unelte/examen_validari_ws.py`, pe ultimul model al liniei noi (ora 6). Reper: #459 **1,2162**
  (re-măsurat în aceeași rulare; dacă iese altceva, contează cifra din rulare și o spun).
- **cod** = `bpb_cod_curat` (#459 **0,7321**); **TinyStories R2** = val_bpb oficial al ultimului model (#459 **0,4084**).
- Alături (NU decid): fapte noi din 150 (#459 73), `bpb_romana` necurățat, val_bpb de la fiecare oră.

## Pragurile (din S45, cuvânt cu cuvânt)

- **CONFIRMAT** dacă română curat ≤ **1,2112** (−0,005 față de #459; pragul e mai mic decât la S38 fiindcă a doua noapte aduce de obicei
  mai puțin), fără regresie > 0,005 la cod curat (0,7321) și R2 (0,4084);
- **INFIRMAT** dacă > **1,2142**;
- **între ele: NECLAR.**

Cum le citesc (scris acum, ca să nu aleg după): „fără regresie > 0,005” = cod curat ≤ 0,7321 + 0,005 = **0,7371** și TinyStories R2
≤ 0,4084 + 0,005 = **0,4134** (față de cifrele lui #459 din aceeași rulare, respectiv din jurnal). Dacă română ≤ 1,2112, dar una dintre
regresii depășește 0,005, verdictul e **NECLAR** (câștig pe română, cu preț), nu CONFIRMAT. Pragurile 1,2112 / 1,2142 sunt fixe (din coadă),
chiar dacă #459 re-măsurat iese puțin altfel.

## Să nu uite

- O singură sămânță și o singură rulare; o diferență mică poate fi și noroc; NECLAR e NECLAR.
- Rata urcă din nou la 0,00005 după încălzire (100 de pași), pornind dintr-un model deja răcit la 0: la S38 primele 4 ore au fost
  **mai rele** decât modelul de plecare la val_bpb; contează doar ultimul model (ora 6), nu se aleg orele după rezultat.
- Comparația e „#459 + 6 ore” față de „#459”; nu spune dacă o singură răcire lungă ar fi fost mai bună.
- Verific în log rândul „Pornesc din modelul experimentului #459” (lecția S42: fără el, antrenarea pornește de la zero → `oprit`).
- Dacă pică un pas, lanțul se oprește; nu se repornește pe ascuns (de 2 ori aceeași eroare → `oprit`). Peste 7.000 MB → `oprit`.
- Modelul nou NU intră în interfață și nu înlocuiește #459 în OS fără alt „da”. Nu se ating `kronos/`, `module/examen_bpb.py`,
  `module/model_muon.py`, paznicul, jurnalul, datele de examen, #441, #459 și liniile/configurările existente.

## Așteptările mele (în cifre)

- Ultimul model (ora 6): română curat **~1,207** (S38 a câștigat 0,017 din #441; a doua noapte cam jumătate, ~−0,009); TinyStories R2
  **~0,404**; cod curat **~0,725**; fapte noi **~70–75**.
- #459 re-măsurat: 1,2162 (aceeași cifră ca la S38).
- Δ română față de #459 așteptat: **~−0,009**. Șansele: CONFIRMAT ~55 %, NECLAR ~25 %, INFIRMAT ~20 %.

## Ce ar infirma așteptările

- Română > 1,2142: a doua continuare din modelul răcit nu mai aduce câștig real (linia s-a plafonat la rata asta) → INFIRMAT.
- Cod curat sau TinyStories R2 cu peste 0,005 mai rău: câștigul pe română se plătește pe celelalte → cel mult NECLAR.

## Ce a ieșit

*Adăugat la 2026-10-30 06:41, din jurnalul Kronos (lucru/jurnal/experimente.jsonl) și din jurnalul CONTINUUM pe bune. Verdictul se scrie dedesubt.*

| # | linia | început | val_bpb | decizia | fapte noi | fapte | nota | motivul |
|---|---|---|---|---|---|---|---|---|
| 469 | w2_reteta_A_cont2 | 29.10 19:01 | 0,4185 | pastrat | — | — | — |  |
| 470 | w2_reteta_A_cont2 | 29.10 20:06 | 0,4167 | pastrat | — | — | — |  |
| 471 | w2_reteta_A_cont2 | 29.10 21:09 | 0,4150 | pastrat | — | — | — |  |

- **w2_reteta_A_cont2:** 3 ore, 3 păstrate; val_bpb de la 0,4185 la 0,4150; cel mai bun păstrat: #471 (0,4150); pornită din #459 (0,4084).

Niciun ciclu CONTINUUM pe bune în perioada asta.

- **Întreruptă la 23:09:36, în ora 4 din 6** (procesul 14764, fără eroare în jurnal, fără cod de ieșire). Orele 1–3 salvate
  (#469 0,4185 / #470 0,4167 / #471 0,4150 pe TinyStories R2); ora 4 nu s-a salvat. **Examenele (`examen_validari_ws.py`) n-au rulat.**
- Indiciu despre cauză (citit la raportul de dimineață, 30 oct 06:41): `lucru/dupa_logare.log` are la 23:12:16 „Logare la 0.4 minute
  după pornirea calculatorului”, iar CONTINUUM (`lucru/continuum_ws/bucla.log`) are ultimul ciclu la 23:05 și repornirea la 23:12:16.
  Deci calculatorul s-a oprit/repornit între 23:09 și 23:12 (cine sau ce a cerut repornirea nu se vede în jurnalele din `lucru/`).

## Verdictul

*Scris la 2026-10-30 06:41, de raportul de dimineață, strict după pragurile de mai sus.*

**Fără verdict (întreruptă); se repetă ca S51.** Toate cele trei măsuri care decid sunt pe ultimul model al liniei (ora 6) și din
examenele de la final; ora 6 n-a existat și examenele n-au rulat, deci:

- română curat (prag CONFIRMAT ≤ 1,2112, INFIRMAT > 1,2142): **nu se poate măsura**;
- cod curat (≤ 0,7371): **nu se poate măsura**;
- TinyStories R2 al ultimului model, ora 6 (≤ 0,4134): **nu se poate măsura** (#471, ora 3, are 0,4150, dar pre-înregistrarea spune
  că „contează doar ultimul model (ora 6), nu se aleg orele după rezultat”, deci #471 nu se notează).

Nu e nici CONFIRMAT, nici INFIRMAT, nici NECLAR: întrebarea n-are răspuns. Supraveghetorul a închis-o la fel (30 oct 02:15, `plan/coada.md`
la S45) și a pus repetarea ca S51, pe linie nouă `w2_reteta_A_cont3`, cu aceleași praguri.
