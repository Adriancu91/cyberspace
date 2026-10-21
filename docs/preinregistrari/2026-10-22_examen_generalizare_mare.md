# Pre-înregistrare: S15 (22 octombrie). E 2/15 chiar zero? Și s-au învățat măcar tipurile antrenate?

<!-- scrisa: 2026-10-22T00:06:00 -->
*Scrisă la 2026-10-22 00:06, înainte de rulare. După ce examenul a început, textul de mai jos nu se mai schimbă; la
final se adaugă doar „Ce a ieșit” și „Verdictul”.*

## Cine a ales

Sarcina **S15** din `plan/coada.md`, aprobată de supraveghetor pe 21 octombrie, la 23:15 (categoria 2 „examene,
comparații, notări”; propunerea (2) a executantului din raportul S12). O face Claude Code, executantul cascadei.
**Nicio antrenare, doar examen.**

## Întrebarea

Două nopți la rând (#407, #415) tipurile noi de întrebări din S4 (b) au stat la 2–3 din 15. Cu 15 întrebări nu se poate
deosebi „zero” de „puțin”. Și nu știm dacă #415 a învățat măcar tipurile pe care LE-A VĂZUT în S11 (familie, gen, partid,
râu, raion…) pe texte noi. **Există un transfer mic spre tipuri nevăzute? S-au învățat tipurile văzute?**

## Examenul: 80 de întrebări, `docs/conversatie/examen_generalizare_mare.json`

Făcut de `unelte/examen_generalizare_mare.py`, DOAR pe textele celor 280 de articole puse deoparte de
`unelte/conversatie_text.py` (sămânța 1019; din ele vin și cele 70 de texte ale examenului nopții 10 și ale lui S4 —
unealta le reface exact, toate 70 se regăsesc). Răspunsul de referință e luat din text.

- **(b2) 50 de întrebări de tipuri care NU există în nicio antrenare** (`text`, `text_v2`, `text_v3`), scrise de mână:
  13 tipuri, cel mult 6 pe tip — țara (5), orașul / sediul (5), premiul (3), actorii (5), profesia (6), postul în echipă (5),
  cine a pictat (3), cine a produs (3), funcția (6), canalul TV (4), rolul / personajul (2), câștigătorul (2), soțul (1).
- **(e) 30 de întrebări din tipurile adăugate în S11**, făcute de `intrebari_noi()` (aceeași funcție ca la antrenare), cu
  formulările de la antrenare: familie 5, raion 5, descris de cine 4, descris în ce an 3, gen 3, legislatură 3, partid 3,
  fondat în ce an 1, construit în ce an 1, afluent 1, bazin 1. Scoasă de mână una: Wiener Athletiksport Club (anul 1900 e
  al echipei de hochei, nu al clubului).
- Fără „Nu scrie” și fără da/nu.

Verificările automate (pasul 1 din S15; toate **0**): texte de examen în vreo antrenare: **0**; întrebări (b2) al căror
început de 4 cuvinte apare la începutul unei întrebări de antrenare: **0**; întrebări copiate din S4: **0**; răspunsuri
care nu se găsesc în text: **0**.

## Ce rulează

Pe placă, una după alta, `unelte/examen_conversatie.py --experiment <id> --examen
docs/conversatie/examen_generalizare_mare.json --doar-local` pentru **#401, #407, #415**, exact ca la S4 / nopțile 10–12
(„Text: … / Întrebare: … / Răspuns:”, fără întâmplare, cel mult 80 de bucăți, profesorul Qwen3-4B notează 1–10). Cam
10 minute pe model.

## Ce înseamnă (regulile supraveghetorului, copiate exact)

Corect = nota profesorului ≥ 7. Numără pentru fiecare model: (b2) x/50, (e) x/30, „Nu scrie în text.” spus pe nedrept,
„Da./Nu.” spus la întrebări care nu sunt da/nu; și (b2) pe fiecare tip.

- **„Tipurile văzute s-au învățat, dar nu se transferă”:** #415 (e) ≥ 21/30 ȘI #415 (b2) ≤ 7/50.
- **„Nici tipurile văzute nu s-au învățat bine”:** #415 (e) ≤ 14/30 → problema e cantitatea/orele pentru tipurile noi,
  nu felul datelor.
- **„Există transfer mic, pe care 15 întrebări nu-l vedeau”:** #415 (b2) ≥ #407 (b2) + 6.
- Altfel: neclar; se spune ca atare.

## Așteptările mele, în cifre (scrise înainte)

- **#415 (e): 18–25 din 30.** A văzut aceste tipuri cu 3–5 formulări fiecare; cred că „familie”, „gen”, „raion” merg,
  iar „descris de cine” (nume scurte ca „Meek.”) și „afluent / bazin” se încurcă.
- **#407 (e): 8–15 din 30**; **#401 (e): 5–12 din 30** (n-au văzut tipurile; unele se pot ghici din text, ca „raionul X”).
- **(b2): #401 5–12, #407 5–12, #415 5–12 din 50.** Cred că diferența dintre #407 și #415 la (b2) e sub 6 (adică nu se
  vede transfer). Tipurile cu răspunsul „la vedere” (țara, orașul, pictorul) merg mai bine decât profesia sau postul.
- **„Nu scrie în text.” pe nedrept la (b2):** #401 15–30, #407 8–20, #415 8–20 din 50.
- **Regula pe care o aștept:** „Tipurile văzute s-au învățat, dar nu se transferă” (cu (e) aproape de prag) sau „neclar”.

## Ce ar infirma așteptările

- **#415 (e) ≤ 14:** nici ce a văzut n-a învățat pe texte noi — atunci problema e cantitatea de date pe tip, nu felul lor.
- **#415 (b2) ≥ #407 (b2) + 6:** tipurile noi din S11 au ajutat și la tipuri nevăzute.
- **(b2) peste 20 din 50 la oricare model:** cele 15 întrebări din S4 (b) erau mai grele decât tipurile noi în general.

## Ce a ieșit

*Adăugat la 2026-10-22 00:29, din jurnalul Kronos (lucru/jurnal/experimente.jsonl) și din jurnalul CONTINUUM pe bune. Verdictul se scrie dedesubt.*

| # | linia | început | val_bpb | decizia | fapte noi | fapte | nota | motivul |
|---|---|---|---|---|---|---|---|---|
| 419 | examen_conversatie | 22.10 00:13 | — | masurat | — | — | — |  |
| 420 | examen_conversatie | 22.10 00:15 | — | masurat | — | — | — |  |
| 421 | examen_conversatie | 22.10 00:17 | — | masurat | — | — | — |  |


Niciun ciclu CONTINUUM pe bune în perioada asta.

## Verdictul

*Scris de Claude Code (executantul din cascadă), 22 octombrie 2026, 00:30, strict după regulile de mai sus. Examenele
s-au dat între 00:13 și 00:17 (jurnal #419–#421), cod 0. Corect = nota profesorului ≥ 7.*

| model | (b2) tipuri nevăzute | (e) tipurile din S11 | „Nu scrie” pe nedrept (b2 / e) | „Da./Nu.” greșit (b2 / e) |
|---|---|---|---|---|
| #401 | 6/50 | 14/30 | 24 / 4 | 0 / 0 |
| #407 | 9/50 | 4/30 | 25 / 20 | 2 / 2 |
| #415 | **6/50** | **30/30** | 20 / 0 | 1 / 0 |

- „Tipurile văzute s-au învățat, dar nu se transferă” (#415 (e) ≥ 21/30 ȘI #415 (b2) ≤ 7/50): **30 ≥ 21 și 6 ≤ 7 → DA.**
- „Nici tipurile văzute nu s-au învățat bine” (#415 (e) ≤ 14/30): 30 → nu.
- „Există transfer mic” (#415 (b2) ≥ #407 (b2) + 6 = 15): 6 → nu (#415 e chiar cu 3 sub #407).

**Se aplică regula „Tipurile văzute s-au învățat, dar nu se transferă”.** #415 a răspuns corect la toate cele 30 de
întrebări din tipurile pe care le-a văzut la antrenare, pe texte nevăzute; la tipurile pe care nu le-a văzut a rămas la
6 din 50 (12%), cât #401, care n-a văzut niciun tip nou. „2/15” din S4 nu era un zero ascuns sub un transfer mic: pe 50 de
întrebări tot nu se vede niciun transfer.

**Față de așteptările mele:** #415 (e) 30, peste intervalul 18–25 (n-am crezut că „descris de cine” și „afluent / bazin”
merg toate). #407 (e) 4, sub 8–15; #401 (e) 14, peste 5–12 (#401 ghicește din text mai des decât #407, care refuză 20 din
30). (b2): 6, 9, 6 — toate în 5–12; diferența #415 − #407 = −3, sub 6, cum am scris. „Nu scrie” pe nedrept la (b2): #401
24 (în 15–30), #407 25 (peste 8–20), #415 20 (la marginea de sus). Regula așteptată: cea care a ieșit. Niciuna din
„ce ar infirma așteptările” nu s-a întâmplat ((b2) nicăieri peste 20).
