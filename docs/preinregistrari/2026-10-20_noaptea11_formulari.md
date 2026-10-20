# Pre-înregistrare: Noaptea 11 (20–21 octombrie): „răspuns din text” cu formulări diferite, din #401. Înțelege Kronos întrebarea, nu doar cuvintele ei?

<!-- scrisa: 2026-10-20T13:37:20 -->
*Scrisă la 2026-10-20 13:37, înainte de rulare. După ce rularea a început, textul de mai jos nu se mai schimbă; la închidere
se adaugă doar secțiunea „Ce a ieșit” (python unelte/preinregistrare.py --inchide noaptea11_formulari).*

## Cine a ales

Sarcinile S6 (datele) și S7 (noaptea) din `plan/coada.md`, **aprobate de supraveghetor** pe 20 octombrie, 11:20
(S6: „pregătirea datelor din surse deja descărcate” și „unelte noi cu teste”; S7: „încă o rulare pe o linie care există,
alt amestec de date”). Pragurile de mai jos sunt **copiate exact** din S7. Scrisă de Claude Code (executantul), în S6.
**S7 pornește doar dacă S6 e `gata` și supraveghetorul a scris în coadă „perechi verificate: da”.**

## Întrebarea

Noaptea 10 a ieșit 50/50, dar examenul S4 a arătat că #401 a învățat cuvintele întrebării, nu sensul: la aceleași
informații cerute altfel, 7 din 15; la tipuri noi de întrebări, 3 din 15; „Nu scrie în text.” spus pe nedrept la 22 din
45. **Dacă vede aceleași tipuri de întrebări spuse în mai multe feluri (plus da/nu), răspunde Kronos și la formulări pe
care nu le-a văzut niciodată, fără să strice ce știa din noaptea 10 și fără să uite?**

## Datele (făcute azi, pe procesor: `python unelte/conversatie_text.py --articole 16000 --formulari --dosar date/conversatie/text_v2`)

- **Aceleași 16.000 de articole și același examen ca în noaptea 10** (sămânța 1019; formulările și da/nu au întâmplarea
  lor, 1020, ca alegerea articolelor să nu se schimbe). Verificat: fără `--formulari`, unealta scoate exact fișierele
  nopții 10 (byte cu byte), iar `date/conversatie/text_v2/examen.json` e identic cu cel al nopții 10.
- **Antrenare: 24.149 de perechi** (`date/conversatie/text_v2/antrenare.jsonl`; noaptea 10: 19.668):
  - **15.534 cu răspunsul în text**, aceleași perechi ca în noaptea 10, dar întrebarea e aleasă la întâmplare dintre
    5–6 formulări ale aceluiași șablon (de exemplu „În ce an s-a născut X?” / „Când s-a născut X?” / „Care e anul
    nașterii lui X?” / „Ce an de naștere are X?” / „X s-a născut în ce an?” / „În ce an e născut X?”). „Ce este X?”
    (7.767) rămâne cum era;
  - **3.585 da/nu** (15% din perechile cu text): 1.793 „Da.” și 1.792 „Nu.”, doar pe șabloanele care există (născut
    1.319, murit 363, an 454, locuitori 449, regizat 427, comună 258, județ 202, scris 113). La „Nu.” unealta schimbă
    anul (±1–30), numărul de locuitori sau numele (cu al altui articol), niciodată cu unul care apare în text;
  - **4.780 cu „Nu scrie în text.”** (20%), tot cu formulări diferite la cele despre același subiect;
  - **250 de conversație simplă**, ca în noaptea 10.
- **Ce NU intră** (ca examenul S4 să rămână cinstit): niciun tip nou de întrebare (fără țară, meserie, trupă, club, loc
  al nașterii, nume științific); **0 întrebări** care încep cu primele 4 cuvinte ale unei întrebări din S4 (de aceea
  au ieșit și cele vechi „În ce an a murit / a apărut / a fost atestat documentar X?”, care încep ca „În ce an a venit
  pe lume X?” din S4); **0 texte** din examenul nopții 10 sau din S4.
- Cea mai lungă pereche: 300 de bucăți (fereastra: 512), ca în noaptea 10.

## Ce rulează

- `config/conv_w2_text_v2.toml`: aceeași linie **„w2_conv_text”**, **din #401**, **3 ore**, lot 12 × 512. Față de
  noaptea 10 doar perechile (`text_v2`) și locul modelului (`lucru/w2_conv_text_v2/gpt.pt`); restul identic: 45%
  perechi, 5% hrană, 50% text vechi, rata 0,00005.
- **Pornire: după 19:00**, de cascadă (executantul):
  `python -X utf8 unelte/antrenare_lunga.py --config config/conv_w2_text_v2.toml --ore 3 --porneste-din 401`.
  Înainte, sarcina Windows „Kronos noapte conversatie” e oprită să refacă noaptea 10 (S7, pasul 0).
- **După ora 3, pe ultimul model păstrat:** aceleași examene ca în noaptea 10 (`date/conversatie/text/examen.json`,
  profesorul Qwen3-4B, validările curate, setul sacru, fapte noi), plus examenul S4:
  `unelte/examen_conversatie.py --experiment <noul id> --examen docs/conversatie/examen_generalizare_401.json`.
- Dimineață: raportul cu verdictul strict după praguri, tabelul complet S4 (60) și 20 de răspunsuri din examenul nopții
  10 (sămânța 1019).

## Ce înseamnă confirmat sau infirmat (copiat exact din S7)

Corect = nota profesorului ≥ 7; la da/nu (c) corect = răspunsul ÎNCEPE cu „Da.”/„Nu.” potrivit (numărat de mine, nu de
profesor).

- **CONFIRMAT:** S4 (a) ≥ 10/15 ȘI (b) ≥ 5/15 ȘI „Nu scrie în text.” pe nedrept la (a)+(b)+(c) ≤ 10/45.
- **INFIRMAT:** S4 (a) ≤ 7/15 (nu e mai bine decât #401).
- Între ele: parțial.
- **Fără să strice noaptea 10:** pe examenul nopții 10, din text ≥ 45/50, „Nu scrie” ≥ 16/20, refuz greșit ≤ 5/50.
- **Să nu uite** (ca la noaptea 10, față de #385): română ≤ 1,3133; cod ≤ 0,8174; povești ≤ 0,47; fapte noi ≥ 65.
- **Urmărite:** (c) da/nu (#401: 0/15 cu regula de mai sus), (d) (#401: 11/15), setul sacru (#401: 24).

## Ce trebuie știut la citirea rezultatelor

- **(c) nu mai e cu totul nou:** câteva întrebări da/nu din S4 au exact forma celor din antrenare („S-a născut X în
  1966?”, „Se află X în județul Suceava?”), pentru că S6 cere da/nu pe șabloanele care există. Celelalte (c) („Se unește
  râul…”, „A durat… până în…”, „A jucat X la…”) sunt noi. De aceea (c) rămâne doar urmărit.
- **(a) e aproape, dar nu identic:** „Cine e regizorul lui X?” (sugerat în S6) seamănă cu „Cine este regizorul filmului
  X?” din S4; primele 4 cuvinte diferă. Restul formulărilor din (a) nu apar în antrenare.

## Așteptările mele, în cifre (Claude Code, scrise înainte)

- **S4 (a): 9–12 din 15** (#401: 7). Formulările văzute seamănă ca sens cu cele din S4, dar nu ca vorbe.
- **S4 (b): 3–6 din 15** (#401: 3). Tipurile noi nu sunt antrenate; câștigul poate veni doar din „citește întrebarea”.
- **„Nu scrie în text.” pe nedrept la (a)+(b)+(c): 8–16 din 45** (#401: 22). Da/nu și formulările ar trebui să scadă
  refuzul; deci CONFIRMAT e posibil, dar nu sigur: cred că mai degrabă PARȚIAL (prag greu: ≤ 10).
- **S4 (c): 7–11 din 15** (#401: 0) cu regula „începe cu Da./Nu. potrivit”.
- **S4 (d): 9–13 din 15** (#401: 11).
- **Noaptea 10:** din text 46–50 din 50, „Nu scrie” 17–20 din 20, refuz greșit 0–3 din 50. Riscul cel mai mare: cele 2
  întrebări „În ce an a murit X?”, a căror formulare nu mai e în antrenare.
- **Să nu uite:** româna curată 1,27–1,29; codul curat 0,78–0,80; poveștile 0,434–0,440; fapte noi 70–76.
- **Setul sacru:** 20–26 din 50.
- **Placa:** ~5.400 MB, nicio oprire.

## Ce ar infirma așteptările

- **(a) ≤ 7 din 15:** formulările nu ajută; Kronos tot după cuvinte caută, nu după sens (INFIRMAT).
- **(b) peste 7 din 15:** variația formulărilor ajută și la tipuri de întrebări niciodată văzute.
- **„Nu scrie” pe nedrept tot peste 18 din 45:** refuzul vine din altceva decât formularea (de exemplu, din cât de
  departe e răspunsul în text).
- **Noaptea 10 sub 45 din 50:** formulările noi au stricat ce știa (atunci verific întâi cele 2 „În ce an a murit X?”).
- **(c) sub 5 din 15:** nici da/nu antrenat pe aceleași șabloane nu trece la întrebările da/nu din S4.

## Notă înainte de rularea reparată (20 octombrie, 20:35)

Rulare reparată pe linia `w2_conv_text_v2`, din #401, aceleași praguri. Prima pornire (19:29) n-a antrenat nimic
(11 secunde, cod 0): linia `w2_conv_text` avea deja 3 ore în jurnal, iar `--ore 3` înseamnă „3 în total”
(`docs/rapoarte/2026-10-20_2002_S7_oprit_nu_a_antrenat.md`). Reparația, varianta 2, aprobată de Adrian la 20:27: în
`config/conv_w2_text_v2.toml` doar `nume = "w2_conv_text_v2"`; datele, setările, comanda și pragurile de mai sus rămân
neschimbate. Dosarul `lucru/w2_conv_text_v2/` nu exista înainte de pornire, deci `--porneste-din 401` se aplică. Noul id
de experiment se scrie mai jos când apare.

## Ce a ieșit

*Adăugat la 2026-10-21 00:04, din jurnalul Kronos (lucru/jurnal/experimente.jsonl) și din jurnalul CONTINUUM pe bune. Verdictul se scrie dedesubt.*

| # | linia | început | val_bpb | decizia | fapte noi | fapte | nota | motivul |
|---|---|---|---|---|---|---|---|---|
| 405 | w2_conv_text_v2 | 20.10 20:47 | 0,4370 | pastrat | — | — | — |  |
| 406 | w2_conv_text_v2 | 20.10 21:52 | 0,4384 | pastrat | — | — | — |  |
| 407 | w2_conv_text_v2 | 20.10 22:56 | 0,4395 | pastrat | — | — | — |  |
| 408 | examen_conversatie | 21.10 00:01 | — | masurat | — | — | — |  |
| 409 | examen_conversatie | 21.10 00:02 | — | masurat | — | — | — |  |
| 410 | examen_validari_ws | 21.10 00:03 | — | masurat | — | — | — |  |

- **w2_conv_text_v2:** 3 ore, 3 păstrate; val_bpb de la 0,4370 la 0,4395; cel mai bun păstrat: #405 (0,4370); pornită din #401 (0,4357).

Niciun ciclu CONTINUUM pe bune în perioada asta.

## Verdictul

*Scris de Claude Code (executantul din cascadă), 21 octombrie 2026, 00:05, strict după pragurile de mai sus. Examenele
s-au dat pe ultimul model păstrat, #407 (ora 3), între 00:01 și 00:03 (jurnal #408–#410, plus setul sacru).*

| ce se măsoară | pragul | a ieșit (#407) | #401 | |
|---|---|---|---|---|
| S4 (a) aceeași informație, altă formulare | confirmat ≥ 10/15; infirmat ≤ 7/15 | **11/15** | 7/15 | trece |
| S4 (b) tipuri noi de întrebări | confirmat ≥ 5/15 | **2/15** | 3/15 | NU trece |
| „Nu scrie în text.” pe nedrept, (a)+(b)+(c) | confirmat ≤ 10/45 | **11/45** (a 4, b 7, c 0) | 22/45 | NU trece (la una) |
| noaptea 10: din text | ≥ 45/50 | **49/50** | 50/50 | trece |
| noaptea 10: „Nu scrie” | ≥ 16/20 | **19/20** | 20/20 | trece |
| noaptea 10: refuz greșit | ≤ 5/50 | **0/50** | 0/50 | trece |
| română, validarea curată | ≤ 1,3133 | **1,2818** | 1,2769 | trece |
| cod, validarea curată | ≤ 0,8174 | **0,7882** | 0,7852 | trece |
| povești (val_bpb) | ≤ 0,47 | **0,4395** | 0,4357 | trece |
| fapte noi | ≥ 65 | **75** | 74 | trece |
| urmărit: (c) da/nu, începe cu „Da.”/„Nu.” potrivit | — | **13/15** | 0/15 | — |
| urmărit: (d) fără răspuns | — | **12/15** | 11/15 | — |
| urmărit: setul sacru | — | **27/50** (28 cu sinonime) | 24 | — |

**PARȚIAL, fără regresie.** (a) a trecut de prag (11 ≥ 10) și nu e infirmat, dar (b) a rămas la 2/15 (prag 5) și
refuzul pe nedrept e 11/45 (prag 10), deci nu e CONFIRMAT. Noaptea 10 și „să nu uite” trec toate.

Față de așteptările mele: (a) 11 în 9–12 (bine); (b) 2 sub 3–6 (am greșit, mai prost decât #401); refuzul 11 în 8–16;
(c) 13 peste 7–11 (am greșit în bine); (d) 12 în 9–13; noaptea 10 în așteptări; română 1,2818 în 1,27–1,29; cod 0,7882
în 0,78–0,80; povești 0,4395 în 0,434–0,440; fapte noi 75 în 70–76; setul sacru 27 peste 20–26; placa 6.303 MB (peste
~5.400 cât așteptam, dar sub 7.000), nicio oprire. Dintre „ce ar infirma așteptările”: (b) peste 7 nu; refuzul peste 18 nu;
noaptea 10 sub 45 nu; (c) sub 5 nu. Cele 2 „În ce an a murit X?” din examenul nopții 10: ambele corecte. Singura greșeală
din text: „Cine a scris Pasărea albastră?” → „Maurice Tourneur.” (regizorul, nu autorul; nota 2).
