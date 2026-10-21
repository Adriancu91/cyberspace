# Pre-înregistrare: Noaptea 12 (21–22 octombrie): „răspuns din text” cu tipuri noi de întrebări, din #407. Învață Kronos să caute în text răspunsul la ce se întreabă, nu tipare?

<!-- scrisa: 2026-10-21T11:11:28 -->
*Scrisă la 2026-10-21 11:11, înainte de rulare. După ce rularea a început, textul de mai jos nu se mai schimbă; la închidere
se adaugă doar secțiunea „Ce a ieșit” (python unelte/preinregistrare.py --inchide noaptea12_tipuri_noi).*

## Cine a ales

Sarcinile S11 (datele) și S12 (noaptea) din `plan/coada.md`, **aprobate de supraveghetor** pe 21 octombrie, 02:15
(S11: „pregătirea datelor din surse deja descărcate” și „unelte noi cu teste”; S12: „încă o rulare pe o linie care
există, alt amestec de date”: același model, același tokenizer, aceeași mărime, aceleași setări; doar datele noi).
Pragurile de mai jos sunt **copiate exact** din S12. Scrisă de Claude Code (executantul), în S11.
**S12 pornește doar dacă S11 e `gata` și la S11 scrie „perechi verificate: da” de la supraveghetor.**

## Întrebarea

Noaptea 11 a arătat că formulările multe ajută la aceleași tipuri de întrebări (S4 (a): 7 → 11/15), dar nu la tipuri pe
care modelul nu le-a văzut (S4 (b): 3 → 2/15). **Dacă la antrenare vede MAI MULTE TIPURI de întrebări (râuri, specii,
deputați, raioane, anul fondării / construcției), învață Kronos „caută în text răspunsul la ce se întreabă” și răspunde
la tipurile din S4 (b), pe care tot nu le-a văzut, fără să strice ce știa și fără să uite?**

## Datele (făcute azi, pe procesor: `python unelte/conversatie_text.py --articole 16000 --formulari --tipuri-noi --dosar date/conversatie/text_v3`)

- **Aceleași 16.000 de articole și același examen ca în nopțile 10 și 11** (sămânța 1019; tipurile noi au întâmplarea
  lor, 1021). Verificat: fără `--tipuri-noi`, unealta scoate exact fișierele lui `text_v2` (byte cu byte), iar
  `date/conversatie/text_v3/examen.json` e identic cu cel din `text_v2`.
- **Antrenare: 27.468 de perechi** (noaptea 11: 24.149): toate cele 24.149 din `text_v2`, neschimbate, **plus 3.319 din
  tipurile noi**:
  - **2.157 cu răspunsul în text**, luat cuvânt cu cuvânt: familie 360, raion 356, anul fondării 319, partid 283,
    legislatură 248, cine a descris specia 237, anul descrierii 115, pe ce râu se află 94, anul construcției 59,
    afluent 51, lungime (râuri) 25, gen 8, bazin 2. Fiecare tip are 4–5 formulări (de exemplu „Din ce familie face parte
    X?” / „Din ce familie este X?” / „X face parte din ce familie?”);
  - **498 da/nu** (15% din perechile noi; 249 „Da.”, 249 „Nu.”), câte una pe articol. „Nu.” are valoarea altui
    articol (alt râu, altă familie, alt partid, altă legislatură, alt raion) sau alt an (±1–30), niciodată una din text;
  - **664 „Nu scrie în text.”** (20%) despre același subiect, când lucrul lipsește din text (de exemplu „Din ce
    familie face parte X?” la o specie fără familie; „Pe ce râu se află X?” la un sat fără niciun râu): râu 373, cine a
    descris 135, familie 45, raion 41, partid 30, legislatură 20, anul fondării 16, afluent 3, anul construcției 1.
- **Perechi-soră:** toate cele 4.002 texte cu o întrebare da/nu (vechi și noi) au și o întrebare deschisă
  („Ce/Cine/Unde/Când/Cât…”) despre același text; la tipurile noi: 498 din 498.
- **Ce NU intră** (ca examenul S4 să rămână cinstit), verificat automat, toate **0**: (i) niciun tip din S4 (b) (țară,
  trupă, club, loc al nașterii, nume științific, zeu, firmă care a lansat, medalie, profesor, reședință, mare, locuri,
  membri, meserie) — 0 șabloane și 0 întrebări noi; (ii) 0 întrebări de antrenare care încep cu primele 4 cuvinte ale
  unei întrebări din S4; (iii) 0 texte din examenul nopții 10 sau din S4.

## Ce rulează

- `config/conv_w2_text_v3.toml`: linia nouă **„w2_conv_text_v3”**, **din #407**, **3 ore**, lot 12 × 512. Față de
  noaptea 11 doar `nume`, perechile (`text_v3`) și locul modelului (`lucru/w2_conv_text_v3/gpt.pt`); restul identic:
  45% perechi, 5% hrană, 50% text vechi, rata 0,00005. Dosarul `lucru/w2_conv_text_v3/` nu există (verificat 21 oct,
  11:10), deci `--porneste-din 407` se aplică.
- **Pornire: după 19:00**, de cascadă (executantul):
  `python unelte/cascada.py porneste S12 -- .venv/Scripts/python.exe -X utf8 unelte/antrenare_lunga.py --config config/conv_w2_text_v3.toml --ore 3 --porneste-din 407`.
- **După ora 3, pe ultimul model păstrat:** exact examenele din S7: examenul nopții 10, examenul S4
  (`docs/conversatie/examen_generalizare_401.json`), validările curate, setul sacru, fapte noi.
- Dimineață: raportul cu verdictul strict după praguri, tabelul complet S4 (60, cu coloanele #407 și noul model) și 20
  de răspunsuri din examenul nopții 10, alese cu `random.Random(1022)` (altele decât ieri).

## Ce înseamnă confirmat sau infirmat (copiat exact din S12)

Corect = nota profesorului ≥ 7; la (c) corect = începe cu „Da.”/„Nu.” potrivit (numărat de mine). „Da./Nu. greșit” =
răspuns care începe cu „Da.”/„Nu.” la o întrebare din (a), (b) sau (d) (#407: 3).

- **CONFIRMAT:** S4 (b) ≥ 5/15 ȘI (a) ≥ 10/15 ȘI „Nu scrie în text.” pe nedrept la (a)+(b)+(c) ≤ 10/45 ȘI
  „Da./Nu. greșit” ≤ 1.
- **INFIRMAT:** S4 (b) ≤ 2/15 (nu e mai bine decât #407).
- Între ele: parțial.
- **Fără să strice ce știa:** examenul nopții 10 din text ≥ 45/50, „Nu scrie” ≥ 16/20, refuz greșit ≤ 5/50; S4 (a) ≥ 9/15
  și (c) ≥ 11/15.
- **Să nu uite** (ca la nopțile 10 și 11): română ≤ 1,3133; cod ≤ 0,8174; povești ≤ 0,47; fapte noi ≥ 65.
- **Urmărite:** (d) (#407: 12/15), setul sacru (#407: 27), rezultatele lui S10 (dacă (b) scade cu orele, spune).

## Ce trebuie știut la citirea rezultatelor

- **Unele întrebări din S4 sunt înrudite cu tipurile noi, fără să fie aceleași:** (c) „Se unește râul Tazlăul Mare cu
  Tazlăul Sărat?” seamănă ca subiect cu da/nu la afluent („Este X afluent al râului Y?”); (c) „A fost ales Costel Claudiu
  Pavelescu în județul Ialomița?” e tot despre un deputat (dar la antrenare nu se întreabă județul în care a fost ales și
  nicio întrebare nu începe cu „A fost ales”); (d) „Cât de lungă este specia…?” / „Cât de lung este canalul…?” sunt
  despre lungime (la antrenare lungimea apare doar la 25 de râuri, cu „Ce lungime are X?”, și fără „Nu scrie” la
  lungime). Dacă (c) sau (d) urcă, poate fi și de aici.
- **„În ce an a fost descrisă X?”** (sugerat în S11) **nu a intrat:** începe cu „În ce an a …”, ca „În ce an a venit pe
  lume X?” din S4, deci (ii) l-ar fi încălcat. În locul lui: „Când a fost descrisă X?”, „În ce an e descrisă X?”, „X a
  fost descrisă în ce an?”, „Care e anul în care a fost descrisă X?”. La fel la fondare și construcție.
- **Genul (8) și bazinul (2) au ieșit foarte puține:** la aproape toate speciile genul e chiar primul cuvânt din nume
  („Drosera rupicola … din genul Drosera”), deci întrebarea ar fi fost un răspuns copiat din întrebare; le-am scos.
  „Bazinul râului Y” apare curat doar de 2 ori în cele 16.000 de articole.
- **Tipuri în plus față de lista din S11** (găsite curat în peste 200 de articole, niciunul pe lista interzisă): raion
  (356), anul fondării (319). Anul construcției (59) e sub 200, dar l-am păstrat pentru că are același șablon ca anul
  fondării („Când a fost construită X?”).
- Partea nouă e doar 12% din perechi (3.319 din 27.468) și perechile sunt 45% din antrenare: modelul vede în 3 ore cam
  de 1–2 ori fiecare pereche nouă. Efectul poate fi mic.

## Așteptările mele, în cifre (Claude Code, scrise înainte)

- **S4 (b): 2–5 din 15** (#407: 2). Tipurile noi sunt alte tipuri decât (b), iar partea nouă e mică; cred că mai degrabă
  rămâne PARȚIAL sau INFIRMAT decât CONFIRMAT. Cel mai probabil: 3.
- **S4 (a): 9–12 din 15** (#407: 11).
- **„Nu scrie în text.” pe nedrept la (a)+(b)+(c): 7–13 din 45** (#407: 11). Mai multe tipuri ar trebui să scadă
  refuzul la (b), dar cele 664 de „Nu scrie” noi îl pot și crește.
- **„Da./Nu. greșit”: 1–5** (#407: 3). Perechile-soră ajută, dar pragul de ≤ 1 e greu.
- **S4 (c): 11–14 din 15** (#407: 13). **S4 (d): 10–14 din 15** (#407: 12).
- **Noaptea 10:** din text 46–50 din 50, „Nu scrie” 17–20 din 20, refuz greșit 0–3 din 50.
- **Să nu uite:** româna curată 1,28–1,30; codul curat 0,785–0,80; poveștile 0,437–0,445; fapte noi 70–77.
- **Setul sacru:** 22–30 din 50.
- **Placa:** ~6.300 MB (ca în noaptea 11), nicio oprire.

## Ce ar infirma așteptările

- **(b) ≥ 6 din 15:** tipurile noi ajută mai mult decât credeam la tipurile niciodată văzute (ipoteza supraveghetorului
  e mai tare decât am crezut).
- **(b) ≤ 1 din 15:** tipurile noi chiar strică, nu doar nu ajută.
- **„Nu scrie” pe nedrept peste 15 din 45:** cele 664 de „Nu scrie” noi l-au făcut să refuze mai des.
- **Noaptea 10 sub 45 din 50 sau S4 (a) sub 9:** datele noi au stricat ce știa.
- **„Da./Nu. greșit” peste 6:** perechile-soră n-au ajutat deloc.
