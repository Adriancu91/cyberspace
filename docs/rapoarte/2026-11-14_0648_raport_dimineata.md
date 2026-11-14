# Raportul de dimineață — sâmbătă, 14 noiembrie 2026, 06:48

*Scris de Claude Code, pornit singur de sarcina „Kronos raport dimineata”. Doar am citit jurnalele: n-am pornit nimic pe placă și n-am schimbat cod.*

## Pe scurt

- Noaptea a rulat **S110**: Kronos cel mare (24 de straturi, 183 de milioane de parametri), antrenat **de la zero**, cu ~74 % română. Rularea e gândită pe **52 de ore**, așa că **încă nu s-a terminat**: la 06:17 avea **8 ore din 52** făcute.
- **Merge sănătos.** Nota la română a scăzut la fiecare oră (mai mic = mai bine): de la **1,5657** după ora 1 la **1,2734** după ora 8. Nicio regulă de oprire nu s-a atins.
- Merge **mai bine decât ghicisem** în pre-înregistrare: la ora 8 e deja sub cât ghicisem pentru ora 24 (~1,28).
- Testele: **1462 trec, 1 sărit, 0 picate.**
- **De la tine nu am nevoie de nimic acum.** Verdictul se dă abia la final (luni dimineață).

## Ce a rulat noaptea

Comanda (pornită aseară la 22:08 de executant, procesul 19736):
`unelte/antrenare_recalcul.py --config config/conv_w2_mare_24z2.toml --ore 52 --pauza 5`.

O „oră” = 60 de minute de învățat + ~1 minut de examen și salvare. După fiecare oră, Kronos dă un examen scurt de română și modelul se salvează.

| ora | terminată la | nota la română (mai mic = mai bine) | cât a scăzut față de ora dinainte | experimentul |
|---|---|---|---|---|
| 1 | 23:09 | 1,5657 | — | #590 |
| 2 | 00:10 | 1,4383 | −0,1274 | #591 |
| 3 | 01:11 | 1,3864 | −0,0519 | #592 |
| 4 | 02:12 | 1,3505 | −0,0359 | #593 |
| 5 | 03:13 | 1,3217 | −0,0288 | #594 |
| 6 | 04:14 | 1,3008 | −0,0209 | #595 |
| 7 | 05:15 | 1,2879 | −0,0129 | #596 |
| 8 | 06:16 | **1,2734** | −0,0145 | #597 |

- Viteza: ~17.500 de pași pe oră (4,9 pe secundă), la fel în fiecare oră — nicio încetinire.
- Scăderea se micșorează de la o oră la alta, ceea ce e normal. Viteza de învățare rămâne la maxim până la ora 39; abia după aceea „răcirea” de la final mai aduce de obicei încă ~0,03.
- Ca reper: modelul pe care îl folosim acum (#513, 12 straturi) are **1,2060**. Cel nou mai are de recuperat **~0,067**.

## Pre-înregistrarea

Pre-înregistrarea nopții e `docs/preinregistrari/2026-11-13_w2_mare_24z2.md`. **N-am închis-o**, fiindcă rularea nu s-a terminat. Se închide după ora 52, cu verdictul pe pragurile scrise în ea.

Unde suntem față de praguri (le-am doar citit, nu le-am schimbat):

- **Oricând — oprire dacă** apare o eroare de calcul (NaN) sau nota la română crește 3 ore la rând și ajunge cu cel puțin 0,03 peste cea mai bună. → **Nu s-a întâmplat.** Nota a scăzut în fiecare oră.
- **La 12 h — oprire dacă** nota orei 12 > 1,90 sau media orelor 10–12 nu e cu cel puțin 0,02 sub media orelor 4–6. Media orelor 4–6 = **1,3243**, deci media orelor 10–12 trebuie să fie **≤ 1,3043**. Ora 8 e deja la 1,2734, așa că, dacă nota nu urcă brusc, verificarea va trece. Ora 12 se termină pe la **10:20** azi.
- **La 24 h** (pe la **22:35** azi): oprire dacă nota orei 24 > 1,70 sau media orelor 22–24 nu e cu cel puțin 0,02 sub media orelor 10–12. Aici e riscul mai mare, fiindcă scăderea încetinește.
- **Verdictul final** (după ora 52, **luni 16 noiembrie, pe la 03:05**): MAI BUN dacă nota re-măsurată e ≤ #513 − 0,005; MAI SLAB dacă e ≥ #513 + 0,005; altfel LA FEL.

Ghicitul executantului din pre-înregistrare, comparat cu ce s-a întâmplat:

| | ghicit | real |
|---|---|---|
| ora 1 | ~1,62 (între 1,55 și 1,72) | 1,5657 — în interval, puțin mai bine |
| ora 6 | ~1,40 | 1,3008 — cu ~0,10 mai bine |
| ora 24 | ~1,28 | (ora 8 are deja 1,2734) |

De ținut minte: notele de la fiecare oră sunt măsurate pe o bucată mai mică de text. Verdictul final se dă pe o re-măsurare completă, făcută în aceeași rulare cu #513.

## Placa și discul

- **Placa video acum (06:40):** 5.803 MB ocupați din 8.192, 62 °C, folosită 98 %. Limitele de pază sunt 6.700 MB și 83 °C, deci e departe de ele. (Pre-înregistrarea ghicise ~5.373 MB pentru antrenare; cifra de acum include și ce mai folosesc alte programe de pe calculator, deci nu se compară exact.) Urmărirea plăcii se scrie la fiecare 10 secunde în `lucru/w2_mare_24z2/placa_20261113_2208.csv`.
- **Discul C:** 50 GB liberi. Fiecare oră salvează un model de 0,73 GB. Cu cele 44 de ore rămase vor rămâne **~17–18 GB la final**, peste pragul de oprire de 15 GB. Marginea e mică (~3 GB), dar e exact cât s-a socotit în pre-înregistrare. Te rog să **nu pui fișiere mari pe C: până luni**. Când liberul scade sub 40 GB (pe la ora ~23), un test anume (`test_kronos_cod_tokenizer…`) va pica din lipsă de spațiu. Asta e cunoscut și nu oprește rularea.

## CONTINUUM

CONTINUUM (bucla care se îngrijește singură de Kronos) a stat **în repaus** toată noaptea, cum trebuie: ultimul ciclu e #8596, la 06:35. La fiecare 5 minute a scris „placa e a executantului… nu pornesc nimic, doar observ”. Are în așteptare două nevoi vechi: „repara:povesti” și „dezvolta:sens”.

## Examenul de conversație

Noaptea **n-a avut** examen de conversație (`lucru/noapte_conversatie.log` e neatins din 19 octombrie). De aceea raportul nu are cele 20 de răspunsuri alese la întâmplare.

## Git

De aseară au intrat 8 commit-uri, toate legate de S110: pregătirea, proba de viteză de învățare (a câștigat varianta „a”: 1,7868 față de 1,8519), pre-înregistrarea, pornirea rulării la 22:08 și verificarea supraveghetorului („S110 verificat — nimic nou în coadă”). Nimic nu a fost nepotrivit.

## Testele

`CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -m pytest -q` (pe procesor, ca să nu încurce placa):
**1462 trec, 1 sărit, 0 picate** (7 min 22 s).

## Ce aștept de la tine

- **Nimic urgent.** Rularea își vede singură de drum până luni dimineață, iar verificările de la 12 h și de la 24 h se fac automat.
- Doar de știut: **nu pune fișiere mari pe discul C:** până luni, ca să nu se oprească rularea din lipsă de spațiu, și **nu porni nimic pe placa video** până atunci.
