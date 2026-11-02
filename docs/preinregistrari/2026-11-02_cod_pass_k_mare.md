# Pre-înregistrare: S64, „mai multe încercări ajută?” — pass@k cu 200 de corpuri pe setul de PROBĂ (linia `cod_c1`, după ora 20)

<!-- scrisa: 2026-11-02T23:35:00 -->
*Scrisă la 2026-11-02 23:35, la S64, ÎNAINTE de orice rulare pe placă (`lucru/kronos_cod/s64/` nu există — verificat acum).
Nu e o antrenare: modelul nu se schimbă, doar scrie răspunsuri. După pornire, textul de mai jos nu se mai schimbă; la închidere
se adaugă doar „Ce a ieșit” și „Verdictul” (`python unelte/preinregistrare.py --inchide cod_pass_k_mare`).*

## Cine a ales

Supraveghetorul, 2 nov 2026 23:20 (granițele 2 și 5: examene/notări + unealtă cu test dacă e nevoie). Pragurile: scrise de
supraveghetor în coadă, copiate aici neschimbate. Această pre-înregistrare: Claude Code (executantul).

## Întrebarea

S58 și S63 au ieșit NECLAR: biții scad (0,5141 → 0,5004), dar rezolvarea rămâne ~2 % (3/200, 3/163). Modelul de după ora 20
**poate** rezolva problemele dacă încearcă de foarte multe ori (pass@k cu k mare)? Dacă da, ajută căutarea/verificatorul
(auto-joc, H3), nu mai multe ore de antrenare. Și: de ce pică corpurile?

## Ce rulează

Un singur lanț, prin `unelte/cascada.py porneste S64 -- python lucru/cascada/S64/s64.py` (refuză să se repete), starea
`lucru/cod_c1/gpt.pt` (doar citită), `config/cod_c1_init002.toml`, **setul de PROBĂ** (20 de probleme), sămânța 0,
`--max-simboluri` implicit 256 (ca la S63), `--lot 2 --memorie-max 6500`, plus plasa lanțului la 6.900 MB / 82 °C:

- (a) `examen_cod.py model --set proba --n 200 --temperatura 0.8` → `lucru/kronos_cod/s64/t08.json`, apoi `noteaza`;
- (b) la fel cu `--temperatura 0.4` → `t04.json`, apoi `noteaza`. **Dacă (a) (scrierea răspunsurilor) trece de 70 de minute,
  (b) se face cu `--n 100`** (o decide lanțul singur și o scriu în raport).
- Apoi, pe procesor: pass@k pentru k = 1, 10, 50, 100, 200 din `pe_problema` (n, c), cu același estimator `pass_la_k` din
  `examen_cod.py`; c din 200 pe fiecare problemă, la fiecare temperatură; și „de ce pică” pe corpurile de la (a): numărul pe
  stări, motivul cel mai des la „interzis” și „căzut”, câte corpuri nu se compilează deloc, 3–5 exemple.

Seturile ascunse (S58 și `ascuns2`) **nu se deschid**.

## Pragurile (din coadă, neschimbate; pentru T = 0,8, n = 200)

- **ÎNCERCĂRILE AJUTĂ** = pass@100 ≥ **4/20** (cel puțin 4 probleme rezolvate măcar o dată din 100);
- **NU AJUTĂ** = pass@100 ≤ **1/20**;
- altfel **NECLAR**.
- T = 0,4 și k = 200: doar informație.

Cum le citesc (scris acum): „pass@100 = x/20” = suma pe cele 20 de probleme a estimatorului nedeplasat pass@100 (din n = 200 și c),
adică numărul așteptat de probleme rezolvate cu 100 de încercări; poate fi neîntreg (de exemplu 3,5/20 → NECLAR, fiindcă e sub 4
și peste 1). Dacă (a) iese incomplet (cod 3, peste 6.500 MB) → fără verdict, `oprit`, nu se repetă.

## Să nu uite

- Setul de probă e mic (20) și a fost folosit la dezvoltarea uneltelor (nu la antrenare): cifra e un **diagnostic, nu un examen**.
- Reperul S63 pe setul de probă: n = 10, T = 0,8 → pass@10 = 0/20, 0 corpuri „ok” din 200 (186 picat, 13 interzis, 1 timp).
- O singură sămânță; NECLAR e NECLAR.
- Nu se ating `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, #477, linia română; `gpt.pt` doar se citește.
- Placa: sub 7.000 MB și 83 °C (`--memorie-max 6500` + plasa); S63 pe același set: vârf ~1.956 MB.

## Așteptările mele (în cifre)

- **Durata:** (a) ~35 min scrierea (S63: 200 de corpuri în 103 s → 4.000 în ~34 min) + ~13 min notarea; (b) la fel; total ~1,6 ore.
  Placa ~2.000 MB, sub 60 °C.
- **(a) T = 0,8:** corpuri „ok” ~10–20 din 4.000 (~0,3 %, ca pass@1 pe `ascuns2`; setul de probă a ieșit mai greu, 0/200).
  pass@1 ~0,3 %, pass@10 ~0,5/20, **pass@100 ~2/20** (între 0,5 și 5), pass@200 ~2,5/20.
  Șansa ≥ 4/20: ~25 %; ≤ 1/20: ~35 %. Verdict: **AJUTĂ ~25 %, NU AJUTĂ ~35 %, NECLAR ~40 %**.
- **(b) T = 0,4:** pass@1 puțin mai mare (~0,5 %), pass@100 mai mic sau egal (~1,5/20): mai puțină varietate.
- **De ce pică:** majoritatea „picat” (rezultat greșit, ~90 %), „interzis” ~5–7 %, restul timp/căzut; corpurile care nu se
  compilează deloc ~5–15 % (funcții tăiate la 256 de simboluri sau indentare stricată).

## Ce ar infirma așteptările

- pass@100 ≥ 8/20: modelul „știe” mult mai mult decât arată pass@10; căutarea cu verificator ar fi direcția clară.
- 0 corpuri „ok” din 4.000: pe setul de probă modelul nu rezolvă nimic nici cu 200 de încercări.
- Peste 30 % corpuri care nu se compilează: problema e forma (tăierea, oprirea), nu logica.
