# Pre-înregistrare: E1 (S17, noaptea 22–23 octombrie): „întrebări născute de Kronos” — auto-joc cu verificator, fără niciun model străin, din #415

<!-- scrisa: 2026-10-22T12:16:30 -->
*Scrisă la 2026-10-22 12:16, înainte de rulare. După ce rularea a început, textul de mai jos nu se mai schimbă; la închidere
se adaugă doar secțiunea „Ce a ieșit” (python unelte/preinregistrare.py --inchide E1_intrebari_nascute).*

## Cine a ales

Sarcina S17 din `plan/coada.md`: direcția aprobată de Adrian pe 22 oct 01:45 (punctul 3), aprobarea finală de supraveghetor
la 05:15, după S16 (acordul verificator ↔ Qwen 527/540 = 97,6 % ≥ 90 %). Experimentul e exact §8 din
`docs/rapoarte/2026-10-22_0200_strategie_nucleu_fara_llm.md`. Pregătirea (scripturile, testele, datele de pe procesor și
această pre-înregistrare) e făcută ziua de 22 oct, pe procesor, fără placă, de Claude Code (executantul).

## Întrebarea

Poate Kronos, fără niciun model străin, să-și producă întrebări de **tipuri noi** care, intrate la antrenare, ridică scorul
pe tipuri nevăzute ((b2) din examenul S15)?

## Baseline (#415, cu ACELAȘI judecător: verificatorul din S16)

| examen | #415, verificator | #415, Qwen (doar pentru comparație) |
|---|---|---|
| S15 (b2), 50 de tipuri nevăzute | **6/50** | 6/50 |
| S15 (e), 30 din tipurile S11 | **30/30** | 30/30 |
| S4 (60) | **38/60** (a 11, b 2, c 13, d 12; „Nu scrie” pe nedrept 9/45) | 38/60 |
| noaptea 10 (50 text + 20 „Nu scrie”) | **50/50, 20/20, refuz greșit 0/50** | 50/50, 20/20, 0/50 |

S15 și S4 cu verificatorul vin din raportul S16 (`docs/rapoarte/2026-10-22_0246_S16_verificator_fara_llm.md`). Examenul
nopții 10 cu verificatorul l-am calculat azi, pe procesor, din răspunsurile deja salvate ale lui #415
(`lucru/examen_conversatie/experiment_415_20261021_223154.json`; S4 din `experiment_415_20261021_223319.json`: tot 38/60).

## Ce rulează (o singură comandă, pornită de cascadă după 19:00)

`python unelte/cascada.py porneste S17 -- .venv/Scripts/python.exe -X utf8 unelte/e1_intrebari_nascute.py noaptea`
face, unul după altul (la prima eroare se oprește; pașii și codurile lor în `lucru/e1/noaptea.json`):

1. **Generatorul** (`config/e1_generator.toml`, linia nouă `w2_e1_generator`): aceeași arhitectură W2, **din #415, 1 oră**,
   pe (text, bucată) → întrebare. Datele (făcute azi, pe procesor): `date/conversatie/auto_v1/generator.jsonl`, **21.001 perechi**
   din antrenările `text`, `text_v2`, `text_v3` (doar perechile „text” cu răspunsul găsit în text; fără da/nu, fără „Nu scrie”),
   în forma „Text: … / Întrebare: Pune o întrebare la care răspunsul este: <bucata> / Răspuns: <întrebarea>”. Bucata =
   răspunsul așa cum apare în text (fără „.” și fără „În …”/„Din …” din față). Restul setărilor ca noaptea 12 (45/5/50,
   rata 0,00005, lot 12, context 512).
2. **Generarea** (cel mult 60 de minute pe placă): pe **2.000 de articole noi** (`date/conversatie/auto_v1/articole.jsonl`:
   următoarele după cele 16.000 de antrenare și cele 280 puse deoparte, aceeași alegere cu sămânța 1019). Verificat automat
   azi: **0 texte de examen** (cele 280 puse deoparte + S15 + S4 + noaptea 10), **0 texte deja în vreo antrenare**, 0 subiecte
   repetate. Pe fiecare articol, cel mult 2 bucăți (propoziții, bucăți dintre virgule, ce urmează după o prepoziție; alese
   cu Random(1022)), **8 întrebări pe bucată, temperatura 1,0, nucleu 0,9**.
3. **Filtrele, toate fără LLM** (cele ieftine întâi, ca dus-întorsul să ruleze doar pe ce a rămas; cel mult 45 de minute):
   - (0) **formă** (adăugat de mine, nu e în §8): se termină cu „?”, 3–30 de cuvinte, fără „Text:”/„Răspuns:”, nu-și conține
     bucata întreagă (altfel întrebarea își spune singură răspunsul);
   - (iii) **fără duplicate**;
   - (ii) **noutate**: primele 4 cuvinte nu apar ca început de întrebare în nicio antrenare (`text`, `text_v2`, `text_v3`) —
     exact §8; **plus** (mai strict, adăugat de mine) **tiparul** = cuvintele dinaintea primului cuvânt cu literă mare sau
     cifră, cel mult 4, nu apare în nicio antrenare. Motivul: fără el, „Ce este Gușoeni?” ar trece drept „tip nou” doar
     pentru că numele e nou; cu el, trec doar tipare de întrebare care chiar n-au fost la antrenare;
   - (iv) **motorul de română**: `verifica_text` fără nicio problemă; singura excepție: cuvinte necunoscute motorului
     („ipoteza”/„necunoscut”: nume proprii, cuvinte străine) **luate din text**; un cuvânt necunoscut inventat cade;
   - (i) **dus-întors**: #415 răspunde la întrebare (din text, fără întâmplare) și răspunsul trece verificatorul din S16
     față de bucată (acoperire ≥ 0,8, și nu „Nu scrie în text.”).
4. **Cel mult 3.300 de întrebări** (cât S11), luate pe rând din fiecare tipar (ca să rămână cât mai multe tipuri),
   Random(1023), în `date/conversatie/auto_v1/intrebari.jsonl`; răspunsul de antrenare = bucata (cu literă mare și punct).
   `antrenare.jsonl` = cele 27.468 de perechi din `text_v3` + ele. Se raportează: câte au căzut la fiecare filtru, câte tipuri
   distincte (pe primele 4 cuvinte, ca în §8, și pe tipar), câte păstrate au același tipar ca o întrebare (b2) din S15.
   Dacă nu trece nicio întrebare, nu se antrenează (se raportează așa).
5. **Antrenarea**, `config/conv_w2_auto_v1.toml` (linia nouă `w2_conv_auto_v1`): **3 ore din #415**, ca noaptea 12; față de
   `config/conv_w2_text_v3.toml` doar `nume`, `conversatie` și `cale_stare`.
6. **Examenele**, pe ultimul model al liniei: S15 (b2, e), S4, examenul nopții 10 — răspunsurile date exact ca în
   `unelte/examen_conversatie.py` (fără întâmplare, 80 de simboluri, tăiate la primul rând), **notate de verificatorul din
   S16 (decizia 2 a lui Adrian: Qwen nu mai e judecător)**; apoi `unelte/examen_validari_ws.py` (română, cod, povești).
   val_bpb și faptele noi vin din antrenare (fișa Kronos a fiecărei ore).

Durata estimată pe placă: 1 h 10 (generator + examenele orei) + ≤ 1 h (generare) + ≤ 45 min (dus-întors) + 3 h 15 (antrenare)
+ ~15 min (examene) ≈ **6 ore și jumătate** (sub cele 7 ore din S17); pornire 19:00 → gata pe la 01:30. Paznicul: placa sub
7.000 MB și 83 °C (al lui Kronos la antrenări; la generare, filtre și examene, verificat de unealtă la fiecare 200/500 de pași).

## Criteriile (copiate cuvânt cu cuvânt din §8 / S17)

- **CONFIRMAT:** (b2) ≥ baseline + 10/50 **și** (e) ≥ baseline − 3/30 **și** fără regresie pe S4 și noaptea 10.
- **INFIRMAT:** (b2) < baseline + 4/50, sau tipuri distincte generate < 20 → H3-lite în forma asta se abandonează; trecem la E2 și pregătim H5.
- **Neclar:** între ele → o singură repetare cu 3× date; apoi decizie.

Cu baseline-ul de mai sus (verificatorul): **CONFIRMAT** = (b2) ≥ **16/50** și (e) ≥ **27/30** și fără regresie;
**INFIRMAT** = (b2) ≤ **9/50** (adică < 10/50) sau tipuri distincte < 20; **neclar** = (b2) 10–15/50, sau (b2) ≥ 16/50 dar
(e) < 27/30 sau cu regresie.

**„Tipuri distincte generate”** se numără, ca în §8 pasul 4, pe primele 4 cuvinte ale întrebărilor păstrate (după toate
filtrele). Scriu alături și numărul pe tipar (mai strict). Dacă unul e ≥ 20 și celălalt < 20, o spun anume în verdict.

**„Fără regresie”** (§8 nu dă cifre; le scriu acum, aceleași ca la nopțile 10–12, citite cu verificatorul):
- noaptea 10: din text ≥ 45/50, „Nu scrie” ≥ 16/20, refuz greșit („Nu scrie” la o întrebare din text) ≤ 5/50;
- S4: (a) ≥ 9/15 și (c) ≥ 11/15.

**Să nu uite** (urmărite, ca la nopțile 10–12; nu intră în verdictul E1, dar se spun): română ≤ 1,3133; cod ≤ 0,8174;
povești ≤ 0,47; fapte noi ≥ 65.

## Așteptările mele, în cifre

- **Generarea:** ~3.800 de bucăți posibile (2.000 de articole × ≤ 2); pe placă, cred că încap toate în 60 de minute
  (~30.000 de întrebări-candidat).
- **Filtrele:** (0) formă: cad ~10–20 %; duplicate: ~20–30 % (generatorul repetă des aceeași întrebare la aceeași bucată);
  noutate: cad **cele mai multe, ~80–90 %** din ce a rămas (generatorul a învățat tiparele vechi); motorul: ~5–10 %;
  dus-întors: trec doar ~20–35 % (#415 răspunde prost la tipuri nevăzute — S15 (b2) 6/50).
  Păstrate: **~500–2.000** (probabil sub 3.300). Tipuri distincte: pe 4 cuvinte **≥ 100**, pe tipar **~50–300**.
- **Examenele:** (b2) **7–11/50** (cel mai probabil ~8), (e) 28–30/30, S4 36–40/60, noaptea 10 48–50/50 și 19–20/20.
- **Verdictul pe care îl aștept:** **INFIRMAT** (~60 %), neclar (~35 %), confirmat (~5 %).

## Ce trebuie știut la citirea rezultatelor

- **Dus-întorsul cu #415 alege întrebările la care #415 știe deja să răspundă.** Exact §8, dar e o limită: datele noi pot
  avea tipare noi la suprafață, cu „mecanism” vechi (de exemplu „Ce rol a avut X?” cu răspunsul „actor”, găsit ușor).
  Dacă (b2) nu urcă, asta e prima explicație de verificat.
- **Filtrele (0) și „tiparul” la (ii) sunt adăugate de mine** (sunt mai stricte decât §8, nu mai largi). Excepția de la
  (iv) (nume și cuvinte străine luate din text) e tot alegerea mea: fără ea, aproape orice întrebare cu un nume ar cădea.
- **Textele de examen nu intră nicăieri** (verificat: 0 în articolele noi, 0 în datele generatorului; se verifică din nou
  pe întrebările păstrate). Dar generatorul poate nimeri, de la sine, tipare ca cele din (b2) (de exemplu „În ce țară …”):
  le număr în raport („păstrate cu tipar din b2”). Asta nu e scurgere — e chiar ce vrea E1 —, dar spune de unde vine o
  eventuală creștere.
- **Orele de antrenare au și examenele lor obișnuite** (val_bpb, fapte, povești notate de Qwen — Qwen rămâne doar pentru
  povești, ca înainte). Nota Qwen nu intră în verdictul E1.
- Generatorul (`w2_e1_generator`) e doar unealta care scrie întrebări; nu e un model pentru interfață și nu se compară.
