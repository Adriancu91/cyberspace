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
