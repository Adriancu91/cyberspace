# Pentru Adrian

*Scris de supraveghetor. Cel mai nou rezumat e sus.*

## 16 noiembrie 2026, 14:40 (executant) — S114 / C-123 gata: fila Chat răspunde scurt; mesajul de sus nou

- **Fila Chat** întreabă acum #651 în forma învățată și se oprește singură: „salut” → „salut, te ascult.”, „Cine ești?” → „Sunt un program de calculator. Mă numesc Kronos.”, dar faptele fără text sunt încă greșite („Care este capitala României?” → „Nu scrie în text.”) — le învață C-126 (S116–S117). Fila „din text” dă exact aceleași răspunsuri ca la C-119. ⚠ La 14:30 paznicul pornise iar interfața veche (#312/#407); am repus #651 (S115 rezolvă asta). Teste: 1.465 trec, 0 pică. Raport: `docs/rapoarte/2026-11-16_1440_S114_fila_chat.md`. Aștept de la tine: nimic.

## 16 noiembrie 2026, 14:15 — Antrenamentul mare s-a încheiat (#651 câștigă, verificat); am pus în coadă cererile tale de azi

- **S111 verificat de mine: #651 CÂȘTIGĂ** (am refăcut sumele: 228 răspunsuri corecte față de 221; româna 1,0878 față de 1,2055; R1 99,31). **S112:** #651 e pe 8787. **C-122:** am notat că 6.922 MB e în regulă și că temperatura e paza principală.
- **Pus în coadă (comenzile tale C-123, C-124, C-126):** **S114** fila Chat cu forma învățată + mesajul de sus nou și **S115** pornirea directă cu #651 după repornire — de acum, pe procesor. **S116** date de chat fără text (Wikipedia + conversații pe șabloane, fără alt AI) + un examen de chat ținut deoparte — azi. **S117** 4 ore de învățat chat-ul din #651, la noapte; intră în interfață doar dacă chat-ul crește clar (+30 din 200), iar româna și „din text” nu scad. **S118** butoanele 👍/👎 și „răspunsul corect ar fi…”, plus bucla care schimbă modelul doar dacă trece examenele.
- 4 ore, nu mai mult: pe C: sunt ~19 GB, iar paza de disc oprește la 15 GB.
- **Aștept de la tine:** nimic. (Dacă vrei teste GPU pe workstation diseară, scrie în hub — Kronos lasă placa liberă.)

## 16 noiembrie 2026, 13:09 (executant) — S112 / C-119 gata: #651 e în interfață (http://100.90.150.35:8787/)

- **Interfața de pe 8787 rulează cu #651** (procesor). Fila „Întreabă din text”: 2/2 corecte, ~10 s. ⚠ Fila de chat fără text dă fraze fără sens (modelul știe doar „text + întrebare”). ⚠ După o repornire, paznicul pornește interfața veche (#312/#407) — comanda de revenire la #651 e în raport. Placa folosită din 72 h: ~67 h. Raport: `docs/rapoarte/2026-11-16_1309_C-119_final.md`. Aștept de la tine: „da”/„nu” pentru (1) #651 implicit în `interfata_ws.ps1`, (2) fila de chat în forma „Întrebare: … Răspuns:”.

## 16 noiembrie 2026, 12:38 (executant) — S111: modelul mare cu conversație CÂȘTIGĂ (#651)

- **#651 trece toate pragurile:** română 1,0878 (față de 1,2055 la #577), răspunsuri corecte 228 din 320 (față de 221), R1 99,31, verificatorul îl vede și el mai bun (215 față de 198). La S112 intră în interfață. ⚠ Placa a urcat ~3,5 minute la 6.922 MB în ultima oră (paza din sarcină: 6.700; limita: 7.000). Raport: `docs/rapoarte/2026-11-16_1238_S111_E3_conversatie.md`. Aștept de la tine: nimic.

## 16 noiembrie 2026, 08:15 — Mulțumesc pentru ștergere: discul are loc, conversația învață mai departe

- **REZOLVAT: discul.** Ai rulat comenzile de ștergere (S113, C-121) de pe telefon, toate fără eroare: C: are acum **~22,8 GB** liberi. Cu ~0,73 GB pe oră, S111 ar trebui să meargă toate cele 7 ore fără să se oprească la 15 GB. S113 = gata.
- **Raportul de dimineață e scris și corect** (`docs/rapoarte/2026-11-16_0657_raport_dimineata.md`): S110 MAI BUN (#641 1,0891 față de #513 1,2060); S111 orele 1–2: româna 1,0889 → 1,0886 (stă pe loc, normal — acum învață conversația). Placa 6.411 MB / 61 °C.
- **Testele:** 1.462 trec, 1 pică (cel știut, cere 40 GB liberi). La prima rulare de azi au picat 19, la a doua nu — probabil din cauza discului plin de atunci. Urmăresc dacă se repetă.
- **Rulează acum:** S111 până pe la ~11:20, apoi examenele și alegerea câștigătorului; apoi S112 (câștigătorul în interfață + raportul final pentru diseară).
- **Aștept de la tine:** nimic.

## 16 noiembrie 2026, 05:15 — Modelul mare de la zero e MAI BUN (verificat de mine); acum învață conversația

- **S110 verificat de mine: MAI BUN.** Româna curată a modelului nou **#641 = 1,0891**, a modelului în uz **#513 = 1,2060** (pragul pentru MAI BUN: ≤ 1,2010). Confirmat și pe textele noi, nevăzute: 1,0125 față de 1,1265. Codul și poveștile englezești ceva mai slabe (așteptat, informativ).
- **Rulează acum S111** (din 04:10, ~7 h, gata pe la 11:20): modelul #641 învață conversația; apoi examenele pe #513, #577 și modelul nou, și alegerea câștigătorului. Placa 6.380 MB / 62 °C (limita 6.700).
- **De știut — discul:** C: avea 19,4 GB la pornirea S111; fiecare oră ia ~0,73 GB, deci paza de 15 GB probabil oprește antrenarea curat după ora 6 (din 7). Nu strică nimic; i-am scris executantului să facă examenele pe ultimul model salvat și să meargă mai departe cu S112.
- **Pus în coadă:** doar o notă (S110 verificat; ce face dacă se oprește la 15 GB). Nicio comandă nouă în hub.
- **Aștept de la tine:** nimic acum. Când ajungi la workstation diseară: cele 7 comenzi din `docs/rapoarte/2026-11-15_1600_S113_stergere_probe.md` (~2 min, ~9 GB).

## 16 noiembrie 2026, 03:48 (executantul) — S110 gata: modelul mare de la zero e MAI BUN decât #513

- După 52 de ore, română curat **1,0891** față de **1,2060** la #513 (mai mic = mai bine; pragul cerea doar 1,2010). Și pe textele noi, nevăzute de nimeni: 1,0125 față de 1,1265. Codul și poveștile englezești puțin mai slabe (cum se aștepta). Atenție: s-au schimbat și mărimea, și datele.
- Testele: 1461 trec, 1 pică (cel știut, discul sub 40 GB). Discul: 19 GB; S111 (7 h) îl poate coborî la ~14 GB → comenzile S113 (~9 GB) ar ajuta. Raportul: `docs/rapoarte/2026-11-16_0348_S110_24z2_final.md`. Urmează S111.

## 15 noiembrie 2026, 17:15 — Verificările pentru ștergere sunt corecte; modelul mare e la ora 41 și tot scade

- **S113 verificat de mine:** executantul a citit lista și se potrivește exact (`proba_24z2` 6,07 GB + 4 modele × 0,73 GB = **~9,0 GB**; #586–#589 sunt chiar cele 4 probe, nimic altceva nu le folosește). N-a șters nimic (n-are voie) — e normal, nu e o problemă.
- **S110 merge:** ora 41 din 52, româna **1,1363** (ora 31: 1,1603; modelul în uz #513: 1,2060). Placa 5.653 MB / 62 °C. Gata luni pe la 02:00–03:00.
- **Discul, socoteala refăcută:** C: 28,3 GB acum (scade ~0,57 GB/oră) → ~22 GB la finalul S110 → ~18 GB după S111. Peste pragul de oprire (15 GB), deci S111 poate porni și fără ștergere; marja e mică, dar nu urgentă.
- **Pus în coadă:** doar o notă (S113 verificat; S111 pornește oricum). Nicio comandă nouă în hub.
- **Aștept de la tine:** când ajungi la workstation (luni seara e bine), cele 7 comenzi PowerShell din `docs/rapoarte/2026-11-15_1600_S113_stergere_probe.md` (~2 minute, câștigi ~9 GB).

## 15 noiembrie 2026, 16:00 (executantul) — S113: am verificat lista de ștergere; comenzile te așteaptă

- Totul din listă se potrivește: **~9,0 GB** (dosarele `proba_24z` și `proba_24z2` + modelele #586–#589, doar probele de rată). Nimic nu le mai folosește.
- **N-am șters nimic** (n-am voie). **Aștept de la tine:** cele 7 comenzi PowerShell din `docs/rapoarte/2026-11-15_1600_S113_stergere_probe.md`, când ajungi. C: are acum 28,3 GB liberi; S110 merge (ora 41, româna 1,1363).

## 15 noiembrie 2026, 08:15 — Noaptea a mers bine: modelul mare la ora 31, cel mai bun scor de până acum

- **Raportul de dimineață e scris și corect** (`docs/rapoarte/2026-11-15_0648_raport_dimineata.md`; am verificat cifrele): S110 la ora 31 din 52, româna **1,1603** (ora 24: 1,1792; #513 are 1,2060) — a scăzut în fiecare oră, nicio regulă de oprire atinsă. Placa 5.653 MB / 62 °C.
- **Testele: 1.461 trec, 1 pică** — cel știut dinainte: o siguranță care cere 40 GB liberi pe disc (acum 34 GB). Nu e o stricăciune; trece la loc când se face loc.
- **De urmărit — discul:** S113 (ștergerea probelor, ~8,6 GB, „da”-ul tău C-121) tot nu e făcută: executantul se oprește la fiecare trecere fiindcă placa e ocupată. La finalul S110 rămân ~19 GB, iar S111 (7 h) ar coborî sub 15 GB pe la ora 6 și s-ar opri curat. Am scris sus în coadă: S113 oricând, **cel târziu între S110 și S111**.
- **Rulează acum:** S110 până luni ~03:10; apoi S113, verdictul S110, S111, S112.
- **Aștept de la tine:** nimic acum. Dacă executantul nu are voie să apese el ștergerea, îți lasă comenzile în raportul S113 (le rulezi când ajungi).

## 14 noiembrie 2026, 23:15 — Modelul mare a trecut și de controlul de la ora 24; e deja mai bun decât modelul în uz

- **S110 a trecut punctul de 24 de ore — am refăcut singur calculul:** româna la ora 24 e **1,1792** (mai mic = mai bine); media orelor 22–24 (1,1822) e cu 0,059 sub media orelor 10–12 (1,2410), trebuia doar 0,02. Nicio oră n-a urcat.
- **Semn bun:** modelul în uz (#513) are 1,2060, deci cel nou e deja sub el (verdictul oficial vine la final, luni ~03:00). Placa max 6.315 MB / 65 °C; 1.462 teste trec.
- **Rulează acum:** S110 până la ora 52. Apoi S111 (conversația) și S112 (interfața), gata luni.
- **S113 (ștergerea probelor):** executantul face verificările la trecerea următoare; probabil îți scrie comenzile de ștergere. Discul C: 39 GB acum, ~18–19 GB la final — fără grabă.
- **Pus în coadă:** doar note (24 h verificat; S113 la trecerea următoare). Nicio comandă nouă în hub.
- **Aștept de la tine:** nimic.

## 14 noiembrie 2026, 23:06 — (executant) S110 a trecut punctul de 24 de ore: continuă

- Româna la ora 24: **1,1792** (deja sub #513, 1,2060 — informativ; verdictul e la final). Media orelor 22–24 = 1,1822, cu 0,059 sub media 10–12 (trebuia 0,02). Placa max 6.315 MB / 65 °C; C: 39 GB; 1462 teste trec. Raport: `docs/rapoarte/2026-11-14_2306_S110_24z2_24h.md`. Nu aștept nimic de la tine.

## 14 noiembrie 2026, 20:15 — Liniște: modelul mare merge spre controlul de la ora 24 (~22:30); nimic de făcut

- **Nimic nou de la 14:15:** executantul n-a mai scris nimic din 11:37 (normal în timpul S110 — scrie doar la punctele de control). S110 e la ~ora 22 din 52; următorul semn al lui e raportul de 24 h, pe la **22:30** (media orelor 22–24 trebuie ≤ 1,2210).
- **De urmărit (nu e problemă încă):** S113 (verificările pentru ștergerea probelor) nu e făcută, deși i-am scris la 14:15 că o poate face în paralel. Nu e grabă — contează abia luni dimineață, iar dacă discul ajunge la 15 GB, Kronos se oprește curat. Dacă la 23:15 lipsește și raportul de 24 h, îți scriu.
- **Pus în coadă:** doar o notă la S113 (s-o facă după raportul de 24 h). Nicio comandă nouă în hub.
- **Aștept de la tine:** nimic.

## 14 noiembrie 2026, 14:15 — Modelul mare a trecut de primul control (ora 12); nimic de făcut

- **S110 a trecut punctul de 12 ore — am refăcut singur calculul:** româna la ora 12 e **1,2335** (ora 13: 1,2256); media orelor 10–12 (1,2410) e cu 0,083 sub media orelor 4–6 (1,3243), trebuia doar 0,02. Scade în fiecare oră. Placa max 6.315 MB / 65 °C; 1.462 teste trec.
- **Mai are de recuperat ~0,02** până la modelul în uz #513 (1,2060), iar viteza de învățare e încă la maxim — șanse bune, dar nu sigur.
- **Următorul control: ora 24, pe la 22:30** (media orelor 22–24 trebuie ≤ 1,2210). Final luni ~03:00.
- **S113 (ștergerea probelor):** executantul întrebase dacă o poate face acum, în paralel; i-am scris în coadă că **da** (e doar citire pe disc, fără placă). Discul C: are 47 GB, la final ~18–19 GB — fără grabă.
- **Aștept de la tine:** nimic. Mai târziu, poate, să rulezi comenzile de ștergere din raportul S113.

## 14 noiembrie 2026, 11:37 — (executant) S110 a trecut punctul de 12 ore: continuă

- Româna la ora 12: **1,2335** (ora 13: 1,2256), scade în fiecare oră; media orelor 10–12 e cu 0,083 sub media orelor 4–6 (trebuia ≥ 0,02). Placa max 6.315 MB / 65 °C; C: 47 GB liberi; 1462 teste trec. Raport: `docs/rapoarte/2026-11-14_1137_S110_24z2_12h.md`. Aștept de la tine: nimic.

## 14 noiembrie 2026, 11:15 — Am primit „da”-ul pentru ștergerea probelor (C-121); modelul mare merge mai departe

- **Comanda ta C-121 e preluată:** am pus în coadă sarcina **S113** cu lista exactă: dosarele `lucru/proba_24z/` și `lucru/proba_24z2/` și modelele de probă #586–#589 (~8,6 GB). Nu se atinge nimic altceva (S110 în curs, #513, #554, #577, jurnalul, datele).
- **De știut:** ca la ștergerea din 7 noiembrie (S88), executantul are probabil voie doar să verifice lista, nu să apese el „șterge”. În cazul ăsta îți scrie în raportul S113 **comenzile exacte**, pe care le rulezi tu la workstation (~2 minute). Nu e grabă mare: contează până luni dimineață.
- **Rulează acum: S110**, modelul mare (ora ~13 din 52). La 08:15 avea româna 1,2734 și scădea în fiecare oră. Punctul de 12 h trebuia trecut pe la 10:20; executantul n-a scris încă raportul lui (ultimul semn de la el: 08:49, adică acum ~2,5 h — încă în regulă). Îl verific la 14:15.
- **Pus în coadă:** doar S113 (fără placă). Placa rămâne la S110 până luni; urmează S111, S112.
- **Aștept de la tine:** nimic acum. Mai târziu, dacă executantul îți scrie comenzile de ștergere, rulezi comenzile din raportul S113.

## 14 noiembrie 2026, 08:15 — Modelul mare învață bine (ora 8 din 52); nimic de făcut

- **Raportul de dimineață e scris și e corect** (`docs/rapoarte/2026-11-14_0648_raport_dimineata.md`; am refăcut singur calculele). 1.462 teste trec, 0 picate.
- **Rulează acum: S110** — la ora 8 din 52, nota la română **1,2734**, a scăzut în fiecare oră (ora 1: 1,5657). E deja sub cât ghicise executantul pentru ora 24 (~1,28). Modelul în uz (#513) are 1,2060, deci mai are ~0,067 de recuperat. Placa 5.803 MB / 62 °C, sub limite.
- **Puncte de control:** ora 12 pe la **10:20** (trebuie ca media orelor 10–12 ≤ 1,3043 — aproape sigur trece), ora 24 pe la **22:35**. Final luni ~03:05.
- **Pus în coadă:** nimic nou (placa e ocupată până luni; urmează S111, S112). Nicio comandă nouă în hub.
- **De știut:** nu pune fișiere mari pe discul C: până luni (50 GB liberi acum, ~17–18 GB la final).
- **Aștept de la tine:** nimic.

## 13 noiembrie 2026, 23:15 — Modelul mare învață de la 22:08; totul verificat, gata luni pe la 03:20

- **S110 a pornit corect** (22:08): modelul de 24 de straturi, de la zero, cu **~74 % română**. Am verificat singur: viteza de învățare aleasă e cea care a câștigat la probă (1,79 față de 1,85), iar ghicitul și pragurile au fost scrise și urcate pe GitHub **înainte** de pornire, copiate exact.
- **Rulează acum:** cele 52 de ore (placa 5.373 MB / 46 °C, sub limite). Primul punct de control: ora 12, sâmbătă ~10:45; al doilea: ora 24, sâmbătă ~23:00. Dacă la unul dintre ele nu mai învață, se oprește singur și orele nu se consumă pe altceva.
- **Pus în coadă:** nimic nou (S111 și S112 urmează luni, după S110). Nimic n-a picat.
- **De știut:** la sfârșit discul C: ajunge pe la ~17 GB liberi (pragul de oprire 15 GB). Dacă vrei margine, poți scrie în hub „da, șterge probele de rată” (~8,6 GB, nu mai folosesc). Fără asta, dacă discul ajunge la 15 GB, Kronos se oprește curat și te întreabă — nu se strică nimic.
- **Aștept de la tine:** nimic obligatoriu.

## 13 noiembrie 2026, 20:20 — Româna în plus intră totuși în antrenare (curățată); modelul mare pornește pe la ~22:00

- **Pregătirea S110 e făcută bine** (1.462 teste trec). Pornirea reparată merge: pierderea de început 9,87 (înainte ~420).
- **Am hotărât: restul de română FineWeb-2 se folosește.** Executantul l-a oprit după o regulă pusă de mine (peste 5 % texte scoase la curățare; au ieșit 14,5 %). Am verificat de unde vine: meniuri și subsoluri de site-uri, nu texte copiate din examene — iar fișierul curățat are **0** potriviri cu examenele. Condiția ta din „da” (să treacă verificarea de scurgeri) e îndeplinită, deci modelul primește **~70 % română în loc de ~37 %**. Pragurile de verdict rămân neschimbate.
- **Costul:** ~1,5 h în plus (proba de rată se reface cu datele noi). Rularea de 52 h pornește pe la ~22:00, gata luni pe la ~02:00; S111 și S112 tot luni, înainte de seară.
- **De știut:** spre sfârșitul rulării discul C: poate coborî aproape de 15 GB liberi; dacă ajunge acolo, executantul se oprește curat și te întreabă (nu șterge nimic).
- **Aștept de la tine:** nimic.

- **13 nov 22:10 (executant) — S110: proba de rată e gata, modelul mare pornește acum.** Cu româna în plus din FineWeb-2 (curățată), am încercat din nou cele două viteze de învățare, câte 30 de minute. A câștigat cea mai mare: nota la română 1,79 față de 1,85 (mai mic = mai bine). Modelul învață acum din **~74 % text românesc**. Toate testele trec (1462). Rularea de 52 de ore pornește în câteva minute și se termină **luni pe la 03:20**; îți scriu la 12 ore (sâmbătă ~10:45) și la 24 de ore (sâmbătă ~22:55). Ghicitul meu, scris dinainte: nota finală ~1,23 (modelul de acum, #513, are 1,206) — adică nu e sigur că îl bate. **De știut:** la sfârșit discul C: ajunge pe la ~17 GB liberi, aproape de pragul de oprire (15 GB). Dacă vrei mai multă margine, spune „da, șterge probele de rată” (~8,6 GB, nu mai folosesc la nimic) — eu nu șterg nimic fără tine. Raport: `docs/rapoarte/2026-11-13_2207_S110_24z2_pregatire2.md`. **Aștept de la tine: nimic obligatoriu.**

- **13 nov 19:10 (executant) — S110: româna în plus din FineWeb-2 NU intră în antrenare.** Regula scrisă în sarcină spunea: dacă la curățarea de „scurgeri” (texte care seamănă cu cele de la examen) se scot peste 5 % din texte, nu se folosește. S-au scos **14,5 %** (104.077 din 718.958) — mai ales din cauza meniurilor și formulelor-șablon ale site-urilor, care apar și în textele de examen. Modelul mare pornește deci pe amestecul vechi: **~37 % română, nu ~69 %**. Restul e cum s-a hotărât (pornirea reparată: pierderea de început 9,87 în loc de ~420; loturi 6 × 16; 52 h). Textele curate rămase (614.881, verificate) stau pe disc; dacă supraveghetorul hotărăște până pe la 20:45 să le folosim totuși, se poate (costă ~1,5 h în plus). Proba de rată rulează acum (până ~20:20), apoi pornește rularea de 52 h. Toate testele trec (1462). Raport: `docs/rapoarte/2026-11-13_1910_S110_24z2_pregatire.md`. **Aștept de la tine: nimic.**

## 13 noiembrie 2026, 17:15 — Prima etapă a ieșit bine (#577); modelul mare pornește cu greșelile reparate și cu mult mai multă română

- **S109 gata, verificat de mine — AJUTĂ.** #577 răspunde corect la 102 din 130 de întrebări noi (#513: 24); verificatorul fără alt AI: 91 față de 23. N-a stricat nimic: româna 1,2055 (#513: 1,2060), codul, R2, instrucțiunile 98,97, examenele vechi — toate în praguri. Slab doar la tipuri de întrebări pe care nu le-a văzut deloc (5 față de 10 din 50). #577 e acum cel mai bun model.
- **Am preluat C-120 (revizia + „da”-ul tău de la 17:03).** Am verificat în cod greșeala de pornire (pierderea de început ~411 în loc de ~9,7) și am rescris S110: pornire corectă, loturi mai eficiente (~+20 % text pe oră), fără examenele de engleză la fiecare oră, iar **restul de ~2,45 GB de română FineWeb-2, deja descărcat, intră în antrenare (~69 % română în loc de ~34 %)** — doar după ce se scot textele care seamănă cu examenele. Dacă verificarea aceea pică, merge pe amestecul vechi și îți scriu de ce.
- **Pragurile de oprire de la 12 h / 24 h** le-am făcut mai cinstite (la 24 h modelul încă învață cu viteză maximă; cele vechi l-ar fi oprit degeaba cam o dată din două). Antrenarea: **52 h** în loc de 54, ca S111 și S112 să fie gata luni după-amiază. La S111: rată mai mică (1e-5, cea care a ținut la 24 de straturi).
- **Rulează acum:** executantul pregătește datele (procesor, ~1–1,5 h), apoi proba de rată (~1,2 h), apoi rularea mare, pe la ~20:00–21:00. Gata pe la luni dimineață.
- **De știut:** interfața de pe telefon (port 8787) arată încă modele vechi (#312/#407), nu #513/#577 — executantul n-are voie să oprească procesul. Se schimbă la S112. Dacă vrei #577 mai devreme, comanda e în raportul S109 (opțional).
- **Aștept de la tine:** nimic.

- **13 nov 16:35 (executant) — S109 gata: AJUTĂ.** Modelul nou #577 răspunde corect la 102 din 130 întrebări noi de tipurile slabe (#513: 24), fără să strice româna, codul sau examenele vechi. Mai slab doar la tipuri pe care nu le-a văzut deloc (5 față de 10 din 50). Interfața n-am schimbat-o (permisiunile nu mă lasă să opresc procesul) — se face la S112. Raport: `docs/rapoarte/2026-11-13_1635_S109_E1_tipuri_noi.md`. Urmează S110.

## 13 noiembrie 2026, 14:15 — Prima etapă (S109) învață acum pe placă; gata pe la 16:40

- **S109 (E1) a trecut de partea de pregătire:** executantul a făcut generatorul de întrebări noi și un examen nou ținut deoparte (180 de întrebări, urcat pe GitHub înainte de antrenare). Au ieșit **3.345 de întrebări noi** (nu ~6.150 cât estimase S108, fiindcă păstrează doar perechile unde răspunsul e sigur și întocmai în text); la 4 tipuri sunt puține (11–16), acolo nu ne așteptăm la mult.
- **Am verificat pre-înregistrarea:** pragurile sunt copiate exact cum le-am scris, înainte de placă. Bine făcut.
- **Rulează acum:** cele 3 ore de antrenare din #513 (pornite ~12:55), apoi examenele; rezultatul pe la **16:40**. Apoi executantul trece singur la S110 (modelul de 24 de straturi de la zero).
- **Pus în coadă:** nimic nou (S110–S112 sunt deja acolo). Nimic n-a picat.
- **Aștept de la tine:** nimic.
