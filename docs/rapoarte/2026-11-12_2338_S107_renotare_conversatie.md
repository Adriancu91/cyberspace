# S107 — Renotarea examenului de conversație: „Nu scrie în text.” numărat corect la întrebările-capcană

*Executant, 12 noiembrie 2026, 23:38. Sarcina S107 din `plan/coada.md` (aprobată de supraveghetor, 12 nov 2026 23:15). Doar procesor, nimic pe placă.*

## Pe scurt

- Unealtă nouă `unelte/renoteaza_conversatie.py` + 5 teste noi. Unealta oficială, fișierele de rezultate și jurnalul Kronos sunt **neatinse** (SHA-256 identic înainte și după).
- La cele 20 de întrebări-capcană („nu știu”), răspunsurile corecte după renotare: **#513: 1 → 16**, **#554: 0 → 16** (din 20).
- **Dar:** aceleași modele refuză cu „Nu scrie în text.” și la întrebările la care ar trebui să știe răspunsul: **#513 la 49 din 50**, **#554 la 46 din 50** întrebări Wikipedia (0 corecte din 50 la amândouă). Deci cele 16 refuzuri „corecte” **nu arată că modelul știe ce nu știe**: modelul refuză aproape orice întrebare fără text. Renotarea corectează un număr greșit, dar nu face examenul să despartă modelele.
- **Verdict #554 față de #513 (pragul S105 neschimbat, notă medie ≥ 0,3 = diferit): LA FEL** (1,913 față de 1,900, +0,013). La „nu știu” corecte: 16 față de 16 (diferența 0, informativ).
- Testele: **1412 trec, 1 sărit**.

## Ce face unealta

`python -X utf8 unelte/renoteaza_conversatie.py <fișiere de rezultate>`

- Citește fișierele scrise de `unelte/examen_conversatie.py`.
- La întrebările cu `fel == "nu_stiu"`: corect = `spune_nu_stiu(r) or spune_nu_scrie(r)` (funcțiile sunt **importate** din unealta oficială, nu copiate). Vechiul „corect” rămâne în câmpul `nu_stiu_corect_vechi`.
- La celelalte feluri: nota profesorului și „corect”-ul rămân exact cele din fișier.
- Scoate aceleași câmpuri ca `scoruri()` plus `nu_stiu_corecte_vechi`, `nu_stiu_corecte_nou`, `refuzuri_la_stiute` („Nu știu” sau „Nu scrie în text.” la întrebările știute), `nu_scrie_la_stiute`, `stiute`.
- Scrie un JSON nou în `lucru/examen_conversatie/renotat/renotat_<nume>.json`. Nu scrie nimic în jurnalul Kronos.

**De știut:** nota medie vine de la profesor (1–10) și renotarea nu o schimbă (profesorul a dat nota 1 la aproape toate refuzurile, și la cele corecte). Doar numărul de „nu știu” corecte se schimbă. De aceea verdictul pe nota medie rămâne exact cel de la S105.

Teste noi (`teste/test_renoteaza_conversatie.py`): „Nu scrie în text.” la `nu_stiu` → corect; „Nu știu.” → corect; un răspuns inventat → greșit; la întrebări știute nota nu se schimbă; fișierul de intrare rămâne neschimbat (SHA).

## Cifrele, una lângă alta

| | #513 | #554 | #396 (reper vechi, 18 oct) |
|---|---|---|---|
| „nu știu” corecte, vechi → nou (din 20) | 1 → **16** | 0 → **16** | 15 → 15 |
| nota medie (toate 80, profesorul) | 1,900 | 1,913 | 3,200 |
| nota medie fără „nu știu” (60) | 2,183 | 2,167 | 1,667 |
| Wikipedia corecte (nota ≥ 7, din 50) | 0 | 0 | 2 |
| conversație corecte (din 10) | 8 | 8 | 0 |
| refuzuri pe nedrept la cele știute (din 60) | **49** (toate la Wikipedia) | **46** (toate la Wikipedia) | 6 („Nu știu”) |

- Fișierele: `lucru/examen_conversatie/experiment_513_20261112_195256.json`, `experiment_554_20261112_195502.json` (S105) și `experiment_396_20261018_221340.json`.
- **#477 și #459:** nu există fișiere ale examenului de conversație cu întrebări „nu știu” (cele de la #477 din 12 nov sunt examenele „din text” de la S106, fără întrebări `nu_stiu`; de #459 nu e niciun fișier). Am pus în loc, doar ca reper, singurul alt fișier cu aceeași formă: #396 (linia `w2_conv`, 18 oct). La el renotarea nu schimbă nimic (15 → 15), cum era de așteptat: a fost antrenat să spună „Nu știu”.
- Cele 4 întrebări „nu știu” rămase greșite: #513 — „În 2007.”, „Nu, plăcere!”, o întrebare repetată înapoi, un șir repetat („300 big, …”); #554 — „Nu, sunt un program de calculator.”, o întrebare repetată înapoi, „A fost un program de calculator.”, o propoziție fără sens în engleză.

**Cinstit:** cifrele „nu știu” (16 din 20 la amândouă) erau deja cunoscute din renumărarea S106 înainte de renotare. Nu e o măsurare nouă, ci o renumărare a unor răspunsuri deja scrise și deja văzute; de aceea nu a fost nevoie de pre-înregistrare (cum scrie în sarcină).

## Verdictul

Pragul S105, neschimbat: diferența de notă medie ≥ 0,3 = diferit, altfel LA FEL.
- Nota medie: #554 1,913 − #513 1,900 = **+0,013 → LA FEL.**
- „Nu știu” corecte după renotare: 16 − 16 = **0** (informativ).
- **„#513 rămâne”** (la fel ca la S105 și S106).

## 5 refuzuri numărate acum corect (#554, alese cu `random.Random(107)`)

| întrebarea | referința | răspunsul modelului | nota profesorului |
|---|---|---|---|
| Ce limbă se vorbește în insula Merovla? | Nu știu sigur. | Nu scrie în text. | 1 |
| Ce a descoperit chimistul Aurel Pietroșanu-Dima? | Nu știu sigur. | Nu scrie în text. | 1 |
| Who wrote the novel "The Glass Orchard of Tobias Wren"? | I don't know for sure. | Nu scrie în text. | 1 |
| Cine a câștigat Cupa Moldovei la șah din 1931 de la Vaslui-Târg? | Nu știu sigur. | Nu scrie în text. | 1 |
| Ce animal este zulvarul de munte? | Nu știu sigur. | Nu scrie în text. | 1 |

## 5 răspunsuri la care nota nu s-a schimbat (#554, întrebări știute, același `Random(107)`)

| întrebarea | referința (scurtată) | răspunsul modelului | nota |
|---|---|---|---|
| Unde se află Șmig? | sat în comuna Alma, județul Sibiu | Nu scrie în text. | 1 |
| Ce este Bijuterii de familie? | film dramatic românesc din 1958 | Nu scrie în text. | 1 |
| Unde se află Dârja? | sat în comuna Panticeu, județul Cluj | Dârja se află în Kronos, în spatele unui calculator. | 1 |
| Unde se află Larsa? | oraș din anticul Sumer | Nu scrie în text. | 1 |
| Cine este Oana Pellea? | actriță română de teatru și film | Nu scrie în text. | 1 |

## Ce n-am atins

`unelte/examen_conversatie.py`, `unelte/renoteaza_text.py`, `kronos/`, `module/examen_bpb.py`, `module/examen_romana.py`, fișierele de examen din `docs/conversatie/`, notele din jurnal, configurările, modelele. Nimic pe placă, nimic descărcat, plătit sau șters. N-a fost nevoie de nicio schimbare în unealta oficială.

SHA-256, înainte = după:
- `unelte/examen_conversatie.py` `4bd13e5b…cd35f`
- `experiment_513_20261112_195256.json` `a68cbf8b…2a98`
- `experiment_554_20261112_195502.json` `decd7117…80f7`

## Testele

`CUDA_VISIBLE_DEVICES=-1 python -m pytest -q` → **1412 trec, 1 sărit** (6 min 45 s). Cele 5 teste noi trec.

## Durata și placa

~10 minute de lucru plus 7 minute de teste, doar procesor. Placa n-a fost folosită (602 MB / 29 °C la pornire).

## Ce urmează (propuneri, nu le fac fără aprobare)

1. Examenul de conversație fără text nu mai poate despărți modelele din linia „text”: ele refuză aproape orice întrebare fără text. Dacă vrem să măsurăm „știe ce nu știe”, avem nevoie de o măsură care pune la un loc refuzul la capcane și răspunsul la întrebările știute (de exemplu: corecte la capcane **minus** refuzuri pe nedrept la cele știute). La #513: 16 − 49; la #554: 16 − 46. Ambele foarte slabe.
2. Pentru modelul în uz, examenele „răspuns din text” (S106) rămân cele care contează. Direcția mare (S101 sau mai multe tipuri de întrebări) e tot decizia lui Adrian.

**Ce aștept de la Adrian:** nimic urgent; doar de citit.
