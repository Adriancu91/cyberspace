# S15 — Examenul mare de generalizare (22 octombrie 2026, 00:44)

*Scris de Claude Code, executantul din cascadă. Doar examen, nicio antrenare. Pre-înregistrarea:
`docs/preinregistrari/2026-10-22_examen_generalizare_mare.md` (scrisă la 00:06, înainte de rulare; închisă și cu
„Verdictul” adăugat la 00:30).*

## Pe scurt

**#415 a învățat toate tipurile de întrebări pe care le-a văzut (30 din 30, pe texte noi), dar la tipurile pe care nu
le-a văzut stă la 6 din 50 — cât #401, care n-a văzut niciun tip nou.** Se aplică regula „Tipurile văzute s-au învățat,
dar nu se transferă”. Cele 2 din 15 din S4 nu ascundeau un transfer mic: nici pe 50 de întrebări nu se vede.

## Ce a rulat

- Examenul: `docs/conversatie/examen_generalizare_mare.json`, 80 de întrebări (făcut de `unelte/examen_generalizare_mare.py`,
  commit 8ba1289), doar din cele 280 de articole puse deoparte.
  - (b2) 50 de întrebări de 13 tipuri care nu există în nicio antrenare (cel mult 6 pe tip).
  - (e) 30 de întrebări din tipurile adăugate în S11, formulate ca la antrenare, pe texte nevăzute.
- Pe placă, prin cascadă (`cascada.py porneste S15`), una după alta: `unelte/examen_conversatie.py --experiment <id>
  --examen docs/conversatie/examen_generalizare_mare.json --doar-local` pentru #401, #407, #415.
  Pornit 00:12, gata 00:17 (cod 0); în jurnal #419, #420, #421 („masurat”). Profesorul Qwen3-4B notează 1–10.
- Rezultatele: `lucru/examen_conversatie/experiment_401_20261022_001355.json`, `..._407_20261022_001532.json`,
  `..._415_20261022_001707.json`.

## Verificările de la pasul 1 (toate trebuie 0)

| verificarea | a ieșit |
|---|---|
| texte de examen care apar în vreo antrenare | **0** |
| întrebări (b2) al căror început de 4 cuvinte deschide o întrebare de antrenare | **0** |
| întrebări copiate din S4 | **0** |
| răspunsuri de referință care nu se găsesc în text | **0** |

## Cifrele (corect = nota ≥ 7)

| model | (b2) tipuri nevăzute | (e) tipurile din S11 | nota medie (toate 80) | „Nu scrie în text.” pe nedrept (b2 / e) | „Da./Nu.” la întrebări care nu sunt da/nu (b2 / e) |
|---|---|---|---|---|---|
| #401 (`text`) | 6/50 | 14/30 | 3,55 | 24 / 4 | 0 / 0 |
| #407 (`text_v2`) | 9/50 | 4/30 | 2,41 | 25 / 20 | 2 / 2 |
| #415 (`text_v3`) | **6/50** | **30/30** | 5,31 | 20 / 0 | 1 / 0 |

### (b2) pe fiecare tip (corecte: #401 / #407 / #415)

| tip | întrebări | #401 | #407 | #415 |
|---|---|---|---|---|
| țara | 5 | 1 | 0 | 0 |
| orașul / sediul | 5 | 0 | 2 | 0 |
| premiul | 3 | 1 | 1 | 1 |
| actorii | 5 | 0 | 0 | 0 |
| profesia | 6 | 2 | 0 | 0 |
| postul în echipă | 5 | 0 | 2 | 2 |
| cine a pictat | 3 | 0 | 1 | 1 |
| cine a produs | 3 | 0 | 0 | 1 |
| funcția | 6 | 2 | 1 | 1 |
| canalul TV | 4 | 0 | 0 | 0 |
| rolul / personajul | 2 | 0 | 1 | 0 |
| câștigătorul | 2 | 0 | 1 | 0 |
| soțul | 1 | 0 | 0 | 0 |
| **total** | **50** | **6** | **9** | **6** |

### (e) pe fiecare tip (corecte: #401 / #407 / #415)

| tip | întrebări | #401 | #407 | #415 |
|---|---|---|---|---|
| familie | 5 | 1 | 0 | 5 |
| descris de cine | 4 | 1 | 3 | 4 |
| descris în ce an | 3 | 1 | 0 | 3 |
| gen | 3 | 1 | 0 | 3 |
| raion | 5 | 1 | 0 | 5 |
| afluent | 1 | 1 | 0 | 1 |
| legislatură | 3 | 3 | 0 | 3 |
| partid | 3 | 3 | 0 | 3 |
| bazin | 1 | 0 | 0 | 1 |
| construit în ce an | 1 | 1 | 0 | 1 |
| fondat în ce an | 1 | 1 | 1 | 1 |
| **total** | **30** | **14** | **4** | **30** |

## Verdictul (regulile supraveghetorului de la pasul 5)

- „Tipurile văzute s-au învățat, dar nu se transferă” (#415 (e) ≥ 21/30 ȘI #415 (b2) ≤ 7/50): 30 și 6 → **SE APLICĂ.**
- „Nici tipurile văzute nu s-au învățat bine” (#415 (e) ≤ 14/30): 30 → nu.
- „Există transfer mic” (#415 (b2) ≥ #407 (b2) + 6 = 15): 6 → nu; #415 e chiar cu 3 sub #407.

Ce înseamnă, simplu: Kronos învață bine un tip de întrebare dacă îl vede la antrenare (de la 4 la 30 din 30 între #407 și
#415), dar nu învață „să răspundă la orice întrebare din text”. Fiecare tip nou trebuie arătat. Ce greșește la tipurile
nevăzute: cel mai des spune „Nu scrie în text.” (20 din 50 la #415), iar în rest repetă bucăți din întrebare („Pe post
evoluează Nicolae Daniel Balauru.”) sau dă un răspuns de alt tip (o dată, „Din 1978.” la „prin ce rol…”).

**Față de așteptările mele (din pre-înregistrare):** #415 (e) 30 — peste intervalul meu 18–25; #407 (e) 4 — sub 8–15;
#401 (e) 14 — peste 5–12 (#401 ghicește din text mai des decât #407, care refuză 20 din 30). (b2) 6 / 9 / 6 — toate în
5–12, iar diferența #415 − #407 (−3) sub 6, cum scrisesem. „Nu scrie” pe nedrept la (b2): 24 / 25 / 20 (al lui #407 peste
intervalul meu 8–20). Regula așteptată a ieșit. Niciunul din semnele „ce ar infirma așteptările” nu s-a întâmplat.

## 20 de răspunsuri (b2), alese cu `random.Random(1023)` dintre cele 50

Notele profesorului în paranteză. ✔ = corect (≥ 7).

| # | tip | întrebarea | referința | #401 | #407 | #415 |
|---|---|---|---|---|---|---|
| 0 | țara | În ce țară se află Peștera Mondmilchloch? | În Elveția. | În 2019. (1) | Nu scrie în text. (1) | Nu scrie în text. (1) |
| 4 | țara | În ce țară e orașul Sacavém? | În Portugalia. | În Portugalia. (10) ✔ | Nu scrie în text. (1) | Nu scrie în text. (1) |
| 8 | oraș | În ce oraș se află Liceul de Artă „Ioan Sima”? | În Zalău. | În județul Sălaj. (6) | În comuna Zalău. (7) ✔ | În județul Sălaj. (6) |
| 17 | actori | Cine sunt actorii principali din Doar cu buletinul la Paris? | Mircea Diaconu și Dorel Vișan. | Nu scrie în text. (1) | Șerban Marinescu. (1) | „…film românesc din 2015 regizat de Șerban Marinescu.” (2) |
| 19 | profesie | Ce profesie a avut Julius Lothar Meyer? | Chimist. | Nu scrie în text. (1) | Nu scrie în text. (1) | Nu scrie în text. (1) |
| 22 | profesie | Ce era de profesie Pedro Leandro Ipuche? | Poet. | „Pedro Leandro Ipuche a fost un poet uruguayan, …” (10) ✔ | Nu scrie în text. (1) | Nu scrie în text. (1) |
| 23 | profesie | Cu ce se ocupa Eddie Hazel? | Chitarist de muzică funk. | Nu scrie în text. (1) | Nu scrie în text. (1) | Nu scrie în text. (1) |
| 25 | post | Pe ce post evoluează Nicolae Daniel Balauru? | Mijlocaș dreapta. | Pe 6 decembrie 1980. (1) | Pe postul de mijlocaș dreapta, în prezent fiind liber de contract. (10) ✔ | Pe post evoluează Nicolae Daniel Balauru. (3) |
| 26 | post | Pe ce post joacă Mirza Hasanović? | Mijlocaș defensiv. | Pe 16 septembrie 1990. (1) | Nu scrie în text. (1) | „…evoluează pe postul de mijlocaș defensiv.” (10) ✔ |
| 27 | post | Pe ce post a jucat Elena Jianu? | Intermediar drepta. | Pe 7 septembrie 1928. (1) | Nu scrie în text. (1) | Pe post a jucat Elena Jianu. (2) |
| 28 | post | Ce post are Nuri Șahin în echipă? | Mijlocaș. | „…joacă pe post de mijlocaș pentru Werder Bremen…” (5) | același răspuns lung (7) ✔ | Nuri Șahin. (3) |
| 29 | pictor | Cine a pictat Persistența memoriei? | Salvador Dalí. | Nu scrie în text. (1) | Salvador Dalí. (10) ✔ | Salvador Dalí. (10) ✔ |
| 30 | pictor | Cine a pictat Mont Sainte-Victoire văzut din Bellevue? | Paul Cézanne. | Nu scrie în text. (1) | Nu scrie în text. (1) | Peisajul. (1) |
| 31 | pictor | Al cui tablou este Barca de pescuit? | Gustave Courbet. | Nu scrie în text. (1) | Nu scrie în text. (1) | Nu. (1) |
| 34 | producător | Ce companie a produs A Million Bid? | Vitagraph Company of America. | Nu scrie în text. (1) | Ralph Ince. (1) | Vitagraph Company. (9) ✔ |
| 38 | funcție | Ce funcție a avut Igor Colenov între 2001 și 2009? | Director general al Serviciului de Grăniceri al Republicii Moldova. | Nu scrie în text. (1) | Nu scrie în text. (1) | Nu scrie în text. (1) |
| 40 | funcție | Ce funcție a avut Ștefan-Constantin Ciurel în 1990? | Primarul municipiului București. | Ștefan-Constantin Ciurel. (5) | Nu scrie în text. (1) | Ștefan-Constantin Ciurel. (5) |
| 41 | canal | Pe ce canal a avut premiera Elevi Interdimensionali Zero? | Pe Cartoon Network. | Nu scrie în text. (1) | Nu scrie în text. (1) | Nu scrie în text. (1) |
| 45 | personaj | Ce rol a interpretat Mary Frances Crosby în Dallas? | Kristin Shepard. | Mary Frances Crosby. (1) | „…a interpretat rolul Kristin Shepard în filmul serial…” (8) ✔ | Mary Frances Crosby. (1) |
| 46 | personaj | Prin ce rol a devenit cunoscut Joshua Jackson? | Peter Bishop. | „…Joshua Jackson este un actor canadian.” (3) | Nu scrie în text. (1) | Din 1978. (1) |

(Notele profesorului par cinstite la aceste 20: răspunsurile lungi care conțin referința primesc 7–10, cele care repetă
întrebarea 2–5. „În 2019.” la țară, „Pe 6 decembrie 1980.” la post și „Din 1978.” la rol arată că #401 și #415 răspund
uneori cu tipul de răspuns al unui tip văzut — data — în loc de tipul cerut.)

## Testele

`CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -m pytest`: **851 trec, 1 sărit** (testul de contract care cere placa
video și modelul), 3 min 35 s. Nu s-a schimbat niciun fișier de cod în rularea asta; nimic în `kronos/`, examenul BPB,
configurări sau date de antrenare.

## Ce urmează (propuneri, nu le pornesc eu)

1. Dacă scopul e „răspunde la orice întrebare din text”, datele trebuie să acopere mult mai multe tipuri (zeci, nu 11),
   fiindcă fiecare tip văzut se învață aproape perfect, iar cele nevăzute aproape deloc. O idee: o noapte cu tipurile din
   (b2) adăugate la antrenare și un set (b3) de alte 10+ tipuri ținute deoparte, ca să vedem dacă de la un număr mai mare
   de tipuri apare transferul.
2. Alternativ, o încercare mai ieftină: întrebări generate din mai multe feluri de propoziții (nu doar din șabloane pe
   tip), ca modelul să învețe „caută în text bucata care răspunde”, nu „la tipul X răspunde cu Y”.

Decizia e a lui Adrian / a supraveghetorului. Eu n-am atins coada în afară de S15.
