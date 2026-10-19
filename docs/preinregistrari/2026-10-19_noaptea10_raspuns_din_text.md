# Pre-înregistrare: Noaptea 10 (19–20 octombrie): „răspuns din text” din #385. Răspunde Kronos din textul dat, fără să uite?

<!-- scrisa: 2026-10-19T09:52:38 -->
*Scrisă la 2026-10-19 09:52, înainte de rulare. După ce rularea a început, textul de mai jos nu se mai schimbă; la închidere
se adaugă doar secțiunea „Ce a ieșit” (python unelte/preinregistrare.py --inchide noaptea10_raspuns_din_text).*

## Cine a ales

**Alegerea e a lui Adrian** (19 octombrie, după noaptea 9 infirmată): nici mai mult amestec, nici doar „nu știu”, ci
varianta (c), **„răspuns din text”**. Kronos nu mai trebuie să țină minte Wikipedia: primește paragraful în față și
răspunde din el. Amestecul are 50% text vechi, ca să nu uite, iar rata e mai mică decât aseară. **Pornește diseară, la
19:00, doar dacă Adrian dă „da” pe cele 10 perechi** din `docs/rapoarte/2026-10-19_1000_date_raspuns_din_text.md`.

## Întrebarea

**Învață Kronos să răspundă la o întrebare luând răspunsul din textul primit, și să spună „Nu scrie în text.” când
răspunsul lipsește, fără să uite româna, poveștile și codul?**

## Datele (făcute azi, 09:51, pe procesor: `python unelte/conversatie_text.py --articole 16000`)

- **Textele:** primul paragraf din 16.000 de articole Wikipedia în română (partea de antrenare), alese la întâmplare
  din tot fișierul (sămânța 1019), între 150 și 700 de litere, cu început curat (filtrele Wikipedia v3). Paragraful se
  oprește la prima propoziție ruptă de curățarea Wikimedia („Are o populație de locuitori.”). Ies parantezele rupte, alte
  alfabete, cuvintele necunoscute și bucățile de 8 cuvinte din examene sau validări.
- **Antrenare: 19.668 de perechi** (`date/conversatie/text/antrenare.jsonl`):
  - **15.534 cu răspunsul în text** („Text: … / Întrebare: … / Răspuns: …”). Răspunsul se ia din text, cuvânt cu cuvânt,
    după șabloane: „Ce este X?” (prima propoziție, cel mult jumătate din aceste perechi: 7.767), „În ce an s-a născut /
    a murit X?” (2.386 / 822), „Din ce an este X?” (984), „Cine a regizat / scris / fondat / dezvoltat X?” (974 / 266 /
    33 / 27), „Câți locuitori are X?” (885), „În ce comună / județ / regiune se află X?” (576 / 421 / 138), „Ce suprafață
    are X?” (187), „La ce distanță de Y se află X?” (54), „Ce capitală are X?” (14);
  - **3.884 cu „Nu scrie în text.”** (20%): 1.942 despre același subiect, cu un lucru care lipsește din text („Cine au
    fost părinții lui X?”, „În ce an a apărut X?”, „La ce altitudine se află X?”, „Cine a creat X?”), și 1.942 despre alt
    subiect (întrebarea altui articol, cu textul acesta);
  - **250 de conversație simplă** (50 de perechi scrise de mână, `docs/conversatie/conversatie_simpla.json`, puse de
    5 ori): „Cum te numești?” → „Mă numesc Kronos.”, „Salut!”, „Mulțumesc!”, „Hello!”… Fără text în față.
- **Pierderea, tot doar pe răspunsuri.** Cea mai lungă pereche are 291 de bucăți (fereastra are 512).
- **Examenul, pus deoparte: 80 de întrebări** (`date/conversatie/text/examen.json`), din **articole care nu intră deloc
  în antrenare** (verificat: niciun text de examen în antrenare), câte o întrebare pe articol:
  - **50 cu răspunsul în text:** 25 „Ce este X?” și 25 cu celelalte șabloane (11 născut, 3 an, 3 locuitori, 2 scris,
    2 murit, 2 regizat, 1 județ, 1 suprafață);
  - **20 fără răspuns în text:** 10 despre același subiect (6 „Cine a creat”, 1 „În ce an a apărut”, 1 locuitori,
    1 „Unde a murit”, 1 părinți) și 10 despre alt subiect;
  - **10 de conversație,** aceleași ca în noaptea 9 („Cum te cheamă?”, „Ce poți face?”, „What is your name?”), **doar
    urmărite**: în antrenare sunt doar întrebări asemănătoare, nu acestea.

## Ce rulează

- `config/conv_w2_text.toml`: linia nouă **„w2_conv_text”**, o copie a lui **#385**, **3 ore**, lot 12 × 512.
  Față de noaptea 9: perechile de mai sus; **45% perechi, 5% hrană, 50% text vechi** (amestecul lui W2; aseară
  75/5/20); **rata 0,00005** constantă, după 100 de pași de încălzire (aseară 0,0001). Restul neschimbat.
- **Pornire: 19:00**, de Windows (sarcina „Kronos noapte conversatie”: `unelte/noapte_conversatie.ps1 -PornesteDin 385
  -FaraScoala -Config config/conv_w2_text.toml -Linie w2_conv_text -Examen date/conversatie/text/examen.json`). **Scriptul
  pornește antrenarea doar dacă `lucru/conversatie_aprobata.txt` pomenește `config/conv_w2_text.toml`.** Fișierul îl
  scriu doar după „da”-ul lui Adrian pe cele 10 perechi; fără el, noaptea nu antrenează nimic. La 18:45 verific testele
  și placa.
- La fiecare oră: val_bpb, fapte, fapte noi, nota profesorului. Kronos păstrează fiecare oră (`prag_zgomot = -1`).
- **După ora 3, pe ultimul model păstrat:**
  - examenul de conversație: răspunsul fără întâmplare, cel mult 80 de bucăți, tăiat la primul rând nou; profesorul
    Qwen3-4B notează 1–10 față de referință;
  - examenul pe validări, cu variantele curate;
  - setul sacru.
- Dimineață, raportul în `docs/rapoarte/`, cu 20 de răspunsuri alese la întâmplare (sămânța 1019). Îl scrie sarcina
  „Kronos raport dimineata” (07:40) sau eu.

## Ce înseamnă confirmat sau infirmat

Un răspuns din text e **corect** dacă profesorul îi dă **cel puțin 7 din 10**. La „fără răspuns în text” e corect dacă
spune „Nu scrie în text.”.

- **Confirmat:**
  - **cel puțin 30 din cele 50** cu răspunsul în text corecte,
  - **și cel puțin 12 din cele 20** „Nu scrie în text.” corecte,
  - **și „Nu scrie în text.” spus la cel mult 5 din cele 50** care au răspunsul în text (ca să nu fi învățat doar să
    refuze).
- **Infirmat:** **sub 15 din 50** cu răspunsul în text **sau sub 6 din 20** „Nu scrie în text.”.
- Între ele: „a început, dar nu ajunge”.
- **Să nu uite: aceleași praguri ca în noaptea 9,** pe ultimul model, față de #385. Peste oricare prag, linia nu se
  păstrează (nu intră în interfață), oricum ar ieși examenul:
  - **română pe validarea curată: cel mult +0,03,** adică **≤ 1,3133** (#385: 1,2833);
  - **cod pe validarea curată: cel mult +0,03,** adică **≤ 0,8174** (#385: 0,7874);
  - **povești (val_bpb): ≤ 0,47** (#385: 0,4383);
  - **fapte noi: ≥ 65** (#385: 73).
- **Setul sacru, urmărit** (#385: 18 din 50; noaptea 9: 26): dacă scade **sub 15 din 50**, îl raportez separat, cu
  întrebările pierdute față de #385.
- **Dacă trece** (confirmat și fără regresie): Adrian hotărăște dacă intră în interfață.

## Așteptările mele, în cifre (Claude Code, scrise înainte)

- **Cu răspunsul în text: 22–38 din 50.** „Ce este X?” e aproape copiere (prima propoziție), deci cred că 17–23 din
  25. La celelalte, Kronos trebuie să găsească bucata potrivită (anul nașterii, regizorul), deci 5–15 din 25.
- **„Nu scrie în text.”: 8–16 din 20.** Cele despre alt subiect sunt ușoare (numele din întrebare nu e în text): 7–10
  din 10. Cele despre același subiect sunt grele: 1–6 din 10.
- **„Nu scrie în text.” la cele care au răspunsul: 2–8 din 50,** deci se poate să cadă peste pragul de 5.
- **Conversația: 3–7 din 10** (a văzut întrebări asemănătoare).
- **Să nu uite:**
  - româna curată 1,29–1,33, **aproape de prag** (aseară +0,095 cu 20% text vechi și rata 0,0001; acum 50% și rata
    pe jumătate);
  - codul curat 0,80–0,84, **aproape de prag**;
  - poveștile 0,45–0,47;
  - fapte noi 65–75;
  - sacru 18–26.
- **Placa:** ~5.400 MB, ~5,9 pași pe secundă, nicio oprire.

## Ce ar infirma așteptările

- **Peste 40 din 50 cu răspunsul în text:** Kronos citește mai bine decât cred.
- **Sub 15 din 25 la „Ce este X?”:** nici măcar copierea primei propoziții nu iese, deci textul în față nu ajută.
- **Româna curată sub 1,30 și codul curat sub 0,80:** 50% text vechi oprește uitarea aproape de tot.
- **Româna curată peste 1,35:** nici 50% text vechi nu ajunge; atunci problema e alta (rata, felul perechilor).
