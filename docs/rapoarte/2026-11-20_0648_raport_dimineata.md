# Raportul de dimineață — 20 noiembrie 2026

*Scris de Claude Code (sarcina „Kronos raport dimineata”), 20 noiembrie 2026, 06:48. Am doar citit: jurnalele din
`lucru/` (cascada, raportul de dimineață, CONTINUUM), raportul S127 (`docs/rapoarte/2026-11-20_0130_S127_formulari_c.md`),
`lucru/jurnal/experimente.jsonl`, `plan/coada.md`, git log și placa video. N-am pornit nimic și n-am schimbat cod.*

## Pe scurt

- **Noaptea a mers fără erori.** S-a rulat **S127**: date noi, în care adunarea, scăderea și împărțirea sunt întrebate în
  de ~7 ori mai multe feluri, apoi 4 ore de învățat pornind din #692, apoi examenele. Toți pașii s-au terminat normal (cod 0).
- **Verdict: rămâne #651.** Modelul nou **#720** a luat la întrebările formulate altfel **46,0 %** — cel mai bun scor de
  până acum (#692 45,0 %, #704 42,0 %), dar pragul scris dinainte era **48,0 %**. Lipsesc 4 răspunsuri din 200.
- Datele noi **au ajutat exact unde trebuia, dar puțin**: adunare + scădere + împărțire formulate altfel au urcat de la
  4 la **8 din 78**. În schimb, răspunsurile „din text” au coborât la **218 — fix la prag**.
- **Testele: 1.539 trec, 1 sărit, 0 picate.**
- **Discul C: ~154 GB liberi.** Placa video e liberă acum (746 MB, 29 °C).

## Ce a rulat noaptea

| ce | când | cât a durat | placa video maxim | s-a terminat bine? |
|---|---|---|---|---|
| S127 pașii 0–3 (procesor): datele noi (338 / 331 / 282 de feluri de a întreba adunarea / scăderea / împărțirea; 0 suprapuneri cu examenele) | 19 nov 19:00 – 19:16 | ~16 min | — | da (cod 0) |
| S127 antrenarea: 4 ore din #692 (configurarea nouă `24zcg`) | 19 nov 19:16 – 23:22 | 4 h 5 min | 6.690 MB / 64 °C | da (cod 0) |
| modele salvate | #717, #718, #719, **#720** (ultimul) | | | |
| S127 examenele pe #651, #720, #692 (și #680 la calcule și formulări) | 23:29 – 01:15 | 1 h 46 min | 4.385 MB / 64 °C | da (cod 0, toți cei 29 de pași) |
| executantul cascadei (verificări la 30 de minute) | toată noaptea, ultima la 06:29 | | | da; „nimic aprobat de făcut” până la 07:00 |

- În jurnalul antrenării apare „Pornesc din modelul experimentului #692” — deci a pornit de unde trebuia.
- Placa a stat tot timpul sub limita de 7.000 MB și s-a eliberat la 01:15.
- Modelele vechi și examenele n-au fost schimbate (amprentele celor 35 de fișiere păzite sunt aceleași înainte și după).
- **CONTINUUM** (paznicul automat) doar a urmărit toată noaptea, în „repaus”, și n-a pornit nimic, cum trebuie. Ultima
  înregistrare: 06:35 (ciclul #10294).
- **Supraveghetorul** a verificat verdictul la 02:15: corect, rămâne #651.

## Cifrele (S127)

| | #651 (modelul din chat) | #692 | #704 (de ieri) | **#720 (nou)** | pragul scris dinainte | trece? |
|---|---|---|---|---|---|---|
| româna (cât de bine prezice textul; mai mic = mai bine) | 1,0878 | 1,0901 | 1,0903 | **1,0906** | ≤ 1,0978 | da |
| răspunsuri corecte „din text” (S15 + S4 + tipuri noi) | 228 | 222 | 219 | **218** | ≥ 218 | da (exact la prag) |
| respectarea instrucțiunilor (R1) | 99,31 | 98,05 | 98,05 | **97,82** | ≥ 90 | da |
| chat (fapte + conversație socială) | 25 | 48 | 49 | **50** | ≥ 30 | da |
| examenul de calcule | 1 | 75 | 70 | **80** | ≥ 61 | da |
| **întrebări formulate altfel (examenul de formulări)** | 20,5 % | 45,0 % | 42,0 % | **46,0 %** (92 din 200) | **≥ 48,0 %** | **NU** |
| — din care adunare + scădere + împărțire (din 78) | 0 | 4 | 3 | **8** | | |
| — din care înmulțire (din 42) | 2 | 18 | 13 | **13** | | |

**Verdictul, strict după pragurile scrise dinainte: rămâne #651.** Interfața de chat nu se schimbă.

Pre-înregistrarea nopții (`docs/preinregistrari/2026-11-19_w2_mare_24zcg.md`) a fost deja închisă de executant la 01:30,
cu „Ce a ieșit” și „Verdictul” (același: rămâne #651). N-am mai avut nimic de închis.

Pe înțeles: #720 e cel mai bun model de până acum la chat, la calcule și la formulări, dar n-a ajuns la pragul de formulări,
iar la „din text” a pierdut iar puțin (222 → 219 → 218 în ultimele trei runde). Înmulțirea a coborât (18 → 13), la fel ca la
#704 — probabil din a doua rundă de învățare, nu din datele noi. La fapte (ani, locuri, oameni) fără text tot inventează.

## Cele 20 de răspunsuri alese la întâmplare

Noaptea a avut examenul de conversație (în lanțul S127, la 00:11). Ultimul model e **#720**, iar fișierul e
`lucru/examen_conversatie/experiment_720_20261120_001138.json`. Pe tot examenul: 180 de întrebări, nota medie **6,49 din
10**, **106** răspunsuri corecte, **49** de „Nu scrie în text.” (adică modelul a zis că răspunsul nu e în textul primit, deși
era). Comparație: #692 6,62 / 109 / 48; #704 6,55 / 108 / 48 — practic la fel, foarte puțin mai jos.

Am ales cu sămânța **20261120** (`random.Random(20261120).sample`, 20 din 180). „Referința” e răspunsul corect, iar nota e
dată de profesor (1 = greșit, 10 = corect).

| # | fel | întrebarea | răspunsul lui Kronos | referința | nota | e bine? (tu) |
|---|---|---|---|---|---|---|
| 1 | tara | În care țară se află Riberalta? | În Bolivia. | Bolivia | 10 | |
| 2 | instrument | La ce instrument cântă Dave „The Beast” Spitz? | Nu scrie în text. | chitară bas | 1 | |
| 3 | absolvit | Ce instituție a absolvit Albert Denn? | Învățământ. | Facultatea de Filologie Hispanică a Universității din Valencia | 1 | |
| 4 | profesie | Cu ce se ocupă Katrine Lunde? | Handbalistă. | handbalistă | 10 | |
| 5 | premiu | Ce distincție a primit Electric Velocipede? | Nu scrie în text. | premiul Hugo | 1 | |
| 6 | personaj | Ce rol a interpretat Scott Edward Adkins în Undisputed II: Last Man Standing? | Yuri Boyka. | Yuri Boyka | 10 | |
| 7 | functie | Ce funcție ocupă Rovnag Ibrahim oglu Abdullayev? | Directorul companiei petroliere. | directorul companiei petroliere | 10 | |
| 8 | sot | Pe cine a luat în căsătorie Carol al X-lea Gustav? | Nu scrie în text. | Hedwig Eleonora de Holstein-Gottorp | 1 | |
| 9 | castigator | Cine s-a impus în Ediția 1948-1949? | Nu scrie în text. | CSCA București | 1 | |
| 10 | sot | Pe cine a luat în căsătorie Natallia Arsiennieva? | Francišak Kušal. | Francišak Kušal | 10 | |
| 11 | functie | În ce funcție a servit Radu Stroe? | Ministru delegat pentru coordonarea Secretariatului General al Guvernului Tăriceanu. | ministru delegat pentru coordonarea Secretariatului General al Guvernului Tăriceanu | 10 | |
| 12 | functie | Ce demnitate a avut George Crin Laurențiu Antonescu? | Nu scrie în text. | președinte interimar al României | 1 | |
| 13 | premiu | Ce premiu a obținut The Encyclopedia of Science Fiction? | Premiul Hugo. | Premiul Hugo | 10 | |
| 14 | personaj | Pe cine a jucat Nikita Mihailovici Efremov în Tetris care a avut premiera la 31 martie 2023? | Alexei Pajitnov. | Alexei Pajitnov | 10 | |
| 15 | tara | În care țară se află Mănăstirea Nechit? | În România. | România | 10 | |
| 16 | profesie | Care a fost profesia lui Jean Frédéric Joliot-Curie - născut Jean Frédéric Joliot -? | Chimist și fizician. | chimist și fizician | 10 | |
| 17 | producator | Cine a produs Vulpea și câinele 2? | Disney Toon Studios. | Disney Toon Studios | 10 | |
| 18 | oras | Unde își are sediul Enosis Neon Paralimni? | În Paralamni. | Paralamni | 10 | |
| 19 | sport | Ce sport practică Neal Skupski? | Jucător. | tenis | 3 | |
| 20 | limba | În ce limbă este Marea Enciclopedie Sovietică? | În limba rusă. | rusă | 10 | |

Din cele 20: **13 note de 10**, o notă de 3 și 6 note de 1. **5 din cele 6 greșeli de nota 1 sunt „Nu scrie în text.”**,
deși răspunsul era în textul primit — aceeași slăbiciune ca în zilele trecute. Celelalte greșeli sunt răspunsuri de felul
greșit („Jucător.” în loc de un sport, „Învățământ.” în loc de o facultate — exact ca ieri la #704).
Câteva întrebări au ieșit și ieri (aceleași întrebări din examen, alt eșantion): nr. 3 și 14 — răspuns identic; nr. 1
(Riberalta) — ieri #704 spunea „Nu scrie în text.”, azi #720 răspunde corect „În Bolivia.”.
(La nr. 18, „Paralamni” e scris așa chiar în textul dat modelului, deci referința și răspunsul se potrivesc.)

## Testele

`CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -m pytest`: **1.539 trec, 1 sărit, 0 picate** (7 min 22 s).

## Ce urmează (din coadă)

- **S128** (aprobat de tine, C-150): exportul lui #651 pentru placa video a OS-ului, **doar pe procesor, de la 07:00**.
  Modelul din chat nu se schimbă.
- **S129** (aprobat de supraveghetor la 02:15): încă o rundă din #720, cu răspunsurile „din text” de 2 ori mai des în date
  și mai multe înmulțiri — pregătirea pe procesor după S128, iar învățarea pe placă **doar la noapte (20 → 21 nov), de la
  19:00**, cu placa liberă la 07:00. Ziua (08:00–18:00) placa rămâne liberă.

## Ce aștept de la tine

1. **Nimic urgent.** Verdictul e după pragul scris dinainte, nimic n-a căzut, testele trec.
2. **O decizie, dacă vrei:** #720 vorbește clar mai bine în chat decât #651 (chat 50 față de 25, calcule 80 față de 1), dar
   e sub pragul de formulări cu 4 răspunsuri și are 10 răspunsuri „din text” mai puțin. Dacă totuși îl vrei în chat, ar fi o
   decizie nouă a ta. Altfel rămâne #651.
3. **S129 la noapte** e aprobată de supraveghetor, nu de tine. Dacă nu vrei încă o rundă pe aceeași linie, spune „nu S129”
   până diseară la 19:00.
4. **Git (tot de rezolvat, ca ieri):** pe calculator a rămas din 17 noiembrie o operație Git neterminată (o „rebazare”).
   Codul e la zi cu GitHub, dar comenzile automate dau eroare din cauza ei (azi la 06:40, la pornirea sarcinii asta:
   `git pull` a picat). Când ai un minut, în dosarul `C:\Kronos\cyberspace` rulează:
   `git rebase --continue`
5. Dacă ai timp: coloana „e bine? (tu)” de la cele 20 de răspunsuri.
