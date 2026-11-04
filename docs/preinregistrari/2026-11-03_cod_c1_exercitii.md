# Pre-înregistrare: S70, o noapte pe exerciții (linia cod_c1_ex, continuarea cod_c1 20 h + 8 h)

<!-- scrisa: 2026-11-03T19:08:16 -->
*Scrisă la 2026-11-03 19:08–19:14, înainte de rulare (nimic din S70 n-a pornit pe placă; `lucru/kronos_cod/s70/` nu există).
După ce rularea a început, textul de mai jos nu se mai schimbă; la închidere se adaugă doar „Ce a ieșit” și „Verdictul”
(`python unelte/preinregistrare.py --inchide cod_c1_exercitii`).*

## Cine a ales

Adrian, C-60 pasul B („funcții” da + „școala cu verificator” da; COMENZI.md C-60, 3 nov 2026 11:45) și C-63 (3 nov 16:30: tot
lanțul se termină sau se oprește curat până la 06:45; 07:00–~09:30 nimic pe placă). Instrucțiunile și pragurile: supraveghetorul
(3 nov 14:20); varianta (b) pentru nume (3 nov 17:20). Această pre-înregistrare: Claude Code (executantul).

## Întrebarea

Dacă schimbăm DOAR datele — 25 % din simboluri exerciții „antet + explicație → corp”, restul cod obișnuit, aceeași rețetă ca S63
(rata fixă 6·10⁻⁵, fără încălzire nouă) — crește pass@10 pe `ascuns2` la cel puțin **8/163** fără ca validarea întreagă să treacă de
**0,510** biți pe octet?

## Ce rulează

Un singur lanț, prin `unelte/cascada.py porneste S70 -- python lucru/cascada/S70_proba/s70.py` (refuză să se repete; pornire
~19:15, deci **8 ore**, fără scădere de ore):

0. Pe procesor: `lucru/cascada/S70_proba/verifica.py` — starea copiată `lucru/cod_c1_ex/gpt.pt` are **590.110 pași**, 1.200 de minute,
   optimizatorul, iar rata la primul pas e **6·10⁻⁵** fără încălzire; altfel lanțul se oprește (cod 5) și nimic nu pornește pe placă.
   Verificat deja la 19:0x: „pași 590110, minute 1200,02, rata 6e-05 → BUNĂ”.
1. **Antrenarea:** `python unelte/antrenare_lunga.py --config config/cod_c1_ex.toml --ore 8 --inceput "def "`. Configurarea =
   `cod_c1_init002.toml` (S63) schimbată doar la: `nume = "cod_c1_ex"`, `[porturi.date] director = "lucru/kronos_cod/exercitii"`,
   `cale_stare = "lucru/cod_c1_ex/gpt.pt"`, eticheta. Jurnalul arată „orele 1–8” pe linia `cod_c1_ex`: e **continuarea liniei
   `cod_c1`** (20 h + 8 h). `lucru/cod_c1/` rămâne neatins (doar citit, la (iv)).
2. **Examenele, o singură dată, pe ultima stare (după ora 8; nu se alege ora după rezultat)**, ca la S63:
   (i) biți pe octet pe validarea întreagă de 5.686 fișiere (`examen_validare.py model --stare lucru/cod_c1_ex/gpt.pt --memorie-max 6500`;
   `validare_*.bin` = exact cele de la S58/S63);
   (ii) `ascuns2`: `examen_cod.py model --set ascuns --dosar lucru/kronos_cod/ascuns2 --lot 2 --memorie-max 6500` + `noteaza`,
   163 × 10, temperatura 0,8, sămânța 0 → pass@1, pass@10;
   (iii) setul de probă 20 × 10, informativ;
   (iv) informativ: biți pe octet doar pe corpurile celor **5.516** exerciții ținute deoparte la S69 (80 de pachete), pentru
   `lucru/cod_c1_ex/gpt.pt` și pentru `lucru/cod_c1/gpt.pt` (S63). Unealta: `lucru/cascada/S70_proba/exercitii_deoparte.py`
   (sfârșitul de fișier, apoi exercițiul exact ca la antrenare; se notează doar simbolurile de la rândul unde începe corpul, după
   docstring; probată pe procesor pe 20 de exerciții cu S63: 0,450). **Atenție (raportul S69):** fișierele din care vin aceste
   exerciții sunt în codul obișnuit al antrenării — cifra arată forma exercițiului, nu cod nevăzut.
   Plasa lanțului la examene: > 6.900 MB sau > 82 °C oprește pasul. Niciun pas nou după 05:45 (C-63).

Datele (S69): 313.910 exerciții la antrenare (50,6 mil. simboluri distincte; autonomele 81.746), repetate în medie de 4,04 ori
(autonomele 8,09); amestecul 970,8 mil. simboluri, din care **24,999 %** exerciții. Scurgerea: setul de probă 1 funcție scoasă,
`ascuns2` 3 funcții cu suprapunere de 13 scoase (0 soluții întregi), S58 0; SHA-urile neschimbate.

## Pragurile (copiate neschimbate din coadă), N = 163

- **AJUTĂ** = pass@10 ≥ **8/163** (~5 %) **și** validarea ≤ **0,510** (codul obișnuit nu se strică);
- **NU AJUTĂ** = pass@10 ≤ **4/163**;
- **STRICĂ** = validarea > **0,510** (oricât pass@10);
- altfel **NECLAR**.
- O sămânță, o noapte; diferența 3 → 5 e în zgomot și o spunem așa.

Cum le citesc (scris acum): „validarea” = biți pe octet pe **toată** validarea de 5.686 fișiere din (i). „pass@10” = numărul de
probleme din 163 cu măcar un corp „ok” din 10 (suma estimatorului pass@10 din `noteaza` × 163). STRICĂ are întâietate față de
AJUTĂ/NU AJUTĂ. Dacă (ii) iese incomplet (cod 3, peste 6.500 MB) → fără verdict pe pass@10, `oprit`, nu se repetă.
Reperul: S63 (10 ore pe cod obișnuit) — validarea **0,50041**; `ascuns2` pass@10 = **3/163**, pass@1 0,25 %.

## Să nu uite

- `ascuns2` s-a mai deschis o dată (S63); se folosește din nou pentru că așa a cerut Adrian (comparabil cu S63). Nu se schimbă,
  nu se arată; SHA verificat de unealtă.
- Setul ascuns S58 nu se deschide.
- 8 ore în plus pe aceeași linie: o parte din câștig poate veni doar din orele în plus, nu din exerciții (fără control cu 8 ore pe
  cod obișnuit). O sămânță.
- Exercițiile sunt funcții din codul de antrenare (deja văzute în fișierele lor), repetate de ~4–8 ori: riscul e supraînvățarea.
- Nu se ating `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, #477, linia română, `lucru/cod_c1/` (doar citire).
- Placa: sub 7.000 MB și 83 °C. Cădere fără eroare → `oprit`, ora exactă, nu se repornește singur.
- După pornire verific în jurnal (prima oră) că fișa are `continuat` și `pasi_total` ≈ 590.110 + ~29.600; dacă nu → `oprit`.

## Așteptările, în cifre

- **Antrenarea:** ~8 × 29.600 ≈ **237.000 de pași** (8,2 pași/s), ~0,93 mld. simboluri; sfârșit ~03:30, examenele gata ~04:15.
  Placa ~6.000–6.200 MB (S63: max 6.013), 60–66 °C.
- **Examenul orar (1.000 de fișiere de validare):** prima oră ~0,484–0,487 (puțin peste 0,4834 de la S63 ora 20: doar 75 % cod
  obișnuit), apoi coborâre lentă la **~0,481** la ora 8 (între 0,476 și 0,488).
- **(i) Validarea întreagă:** **~0,497** (între 0,490 și 0,505). Șansa > 0,510: ~5 %.
- **(ii) `ascuns2`:** pass@1 ~0,4 %; **pass@10 ~5/163** (între 2 și 10). Șansa ≥ 8/163: ~20 %; ≤ 4/163: ~45 %.
- **(iii) setul de probă:** pass@10 ~0–2/20.
- **(iv) corpurile ținute deoparte:** S63 ~0,45 biți/octet; `cod_c1_ex` **~0,41** (cu 0,02–0,06 mai jos); autonomele mai jos
  decât restul la ambele.
- Verdict: **AJUTĂ ~18 %, NU AJUTĂ ~45 %, STRICĂ ~5 %, NECLAR ~32 %**.

## Ce ar infirma așteptările

- Validarea > 0,510: exercițiile repetate strică codul obișnuit (STRICĂ) — rețeta de amestec trebuie schimbată înainte de S72.
- pass@10 ≥ 10/163: forma „antet + explicație → corp” se potrivește cu examenul mult mai bine decât cred.
- (iv) fără câștig (diferență < 0,01) dar pass@10 urcă: câștigul vine din altceva (orele în plus / zgomot), nu din forma exercițiului.
- (iv) câștig mare (> 0,08) cu pass@10 ≤ 4: modelul învață forma exercițiilor, dar nu să rezolve probleme noi.

## Ce a ieșit

*Adăugat la 2026-11-04 04:29, din jurnalul Kronos (lucru/jurnal/experimente.jsonl) și din jurnalul CONTINUUM pe bune. Verdictul se scrie dedesubt.*

| # | linia | început | val_bpb | decizia | fapte noi | fapte | nota | motivul |
|---|---|---|---|---|---|---|---|---|
| 500 | cod_c1_ex | 03.11 19:09 | 0,4900 | pastrat | — | — | — |  |
| 501 | cod_c1_ex | 03.11 20:10 | 0,4903 | pastrat | — | — | — |  |
| 502 | cod_c1_ex | 03.11 21:12 | 0,4908 | pastrat | — | — | — |  |
| 503 | cod_c1_ex | 03.11 22:14 | 0,4917 | pastrat | — | — | — |  |
| 504 | cod_c1_ex | 03.11 23:15 | 0,4909 | pastrat | — | — | — |  |
| 505 | cod_c1_ex | 04.11 00:17 | 0,4899 | pastrat | — | — | — |  |
| 506 | cod_c1_ex | 04.11 01:18 | 0,4910 | pastrat | — | — | — |  |
| 507 | cod_c1_ex | 04.11 02:20 | 0,4911 | pastrat | — | — | — |  |

- **cod_c1_ex:** 8 ore, 8 păstrate; val_bpb de la 0,4900 la 0,4911; cel mai bun păstrat: #505 (0,4899).

Niciun ciclu CONTINUUM pe bune în perioada asta.

**Examenele (o singură dată, pe starea de după ora 8):** (i) validarea întreagă **0,50742** (S63: 0,50041);
(ii) `ascuns2` pass@10 = 0,01227 × 163 = **2/163**, pass@1 0,18 % (3 corpuri „ok” din 1.630), complet;
(iii) proba 1/20; (iv) corpurile ținute deoparte: `cod_c1_ex` 0,56463, S63 0,57434 (−0,0097).

## Verdictul

*Scris la 2026-11-04 04:38 de executant, strict după pragurile de sus.*

- STRICĂ (validarea > 0,510)? 0,50742 → **nu**.
- AJUTĂ (pass@10 ≥ 8/163 și validarea ≤ 0,510)? 2/163 → **nu**.
- NU AJUTĂ (pass@10 ≤ 4/163)? 2/163 → **da**.

**Verdict: NU AJUTĂ.** 25 % exerciții, 8 ore, nu au urcat pass@10 pe `ascuns2` (2/163 față de 3/163 la S63; diferența e în zgomot),
iar validarea a urcat cu 0,007 (mai prost, dar sub pragul 0,510). O sămânță, o noapte.
Față de așteptări: validarea 0,507 (așteptam ~0,497, în intervalul 0,490–0,505: peste interval); examenul orar plat ~0,490–0,492
(așteptam coborâre la ~0,481); (iv) câștig mic, 0,0097 (așteptam 0,02–0,06), iar cifrele absolute ~0,57, nu ~0,45 cum arătase proba pe 20.
