# Pre-înregistrare: Examenul neutru: texte scrise după 12 octombrie 2026, pe care nu le-a văzut niciun model

<!-- scrisa: 2026-10-17T20:46:18 -->
*Scrisă la 2026-10-17 20:46, înainte de orice descărcare. După ce descărcarea a început, textul de mai jos nu se mai
schimbă; la închidere se adaugă doar secțiunea „Ce a ieșit”.*

**Stare: așteaptă „da”-ul lui Adrian.** Până acum am citit doar liste și licențe (câte articole noi există, câte
proiecte), nu conținut. Totul rulează doar pe procesor, lângă W2 și W2-conv, cu prioritate scăzută.

## Întrebarea

**Rămâne Kronos #373 mai bun decât GPT-2 small și GPT-Neo românesc 125M când niciunul nu joacă „acasă”?** În comparația
de azi, Kronos a fost mai bun la toate trei, dar validările lui sunt din aceleași surse ca antrenarea lui. Un examen pe
texte scrise după ce s-au strâns datele tuturor celor trei modele e neutru: nimeni nu le-a văzut.

## Datele de tăiere

| model | ultimele lui date |
|---|---|
| Kronos #373 | descărcate pe 12 octombrie 2026. Wikipedia din 1 noiembrie 2023, FineWeb-2 și The Stack mai vechi |
| GPT-2 small | WebText, 2019 |
| GPT-Neo ro 125M | OSCAR și altele, cel târziu 2023 (modelul e publicat cu transformers 4.27, din primăvara lui 2023) |

**Regula:** intră doar texte create **după 12 octombrie 2026**, adică începând cu 13 octombrie, 00:00 UTC.

## Ce se descarcă (cel mult ~10 MB în total)

1. **Wikipedia în română, articole noi.** Toate articolele create din 13 octombrie încoace. Sunt 135 la 20:40, cu ~1,7 MB
   de wikitext.
   - Lista vine din „schimbările recente” ale Wikipediei: pagini noi, doar articole, fără redirecționări.
   - **Se scot:** paginile recreate (eticheta `mw-recreated`, adică au mai existat), traducerile făcute cu unealta
     Wikipediei (`contenttranslation`, deci textul a existat în altă limbă) și textele sub 300 de litere, ca la curățarea
     noastră.
   - Textul se ia simplu, fără marcaje (API-ul TextExtracts al Wikipediei), la revizia de la descărcare.
2. **Wikipedia în engleză, articole noi.** Aceleași reguli, aceeași perioadă. Sunt câteva mii, deci se aleg **la
   întâmplare 200** (sămânța 1018).
3. **Cod Python nou de pe GitHub.**
   - **Proiectele:** create din 13 octombrie încoace, cu cel puțin 3 stele (ca să nu fie gunoi), fără copii (fork).
   - **Licența:** doar cu licență permisivă, recunoscută de GitHub și cu fișierul LICENSE prezent: MIT (509 proiecte),
     Apache-2.0 (130), BSD (5).
   - **Alegerea:** 40 de proiecte la întâmplare (sămânța 1018); din fiecare, cel mult 5 fișiere `.py`, de 200 de litere
     până la 50.000 de octeți.
   - **Se scot:** fișierele generate automat, copiate din altă parte (`vendor`, `site-packages`, `node_modules`,
     `third_party`) sau de teste uriașe.
- **Licențele:** textul Wikipedia e sub CC BY-SA 4.0, iar codul sub licențele lui permisive. Le folosim doar pentru
  măsurat, local, nepublicat (`date/neutru/` nu intră în Git).
- **Atribuirea:** pentru fiecare text se păstrează în `date/neutru/surse.json` titlul sau proiectul, adresa, revizia
  sau commit-ul, autorul (la cod) și licența.
- **Totul se scrie o singură dată.** Seturile primesc amprente (sha256) și nu se mai schimbă.

## Ce rulează

- **Același examen ca în comparația de azi:** primele 100.000 de litere din fiecare set, biți pe octet, ferestre de 512
  bucăți (cifra principală), plus fereastra proprie a fiecărui model doar ca informație. Același cod:
  `unelte/compara_externe.py`, care pentru Kronos dă exact nota lui.
- **Cine:** Kronos #373, GPT-2 small, GPT-Neo românesc 125M (aceleași versiuni fixate).
- **Verificarea că nimeni nu le-a văzut:**
  - Kronos se verifică direct, cu `unelte/scurgeri_examen.py`: câte bucăți de 50 de litere din setul nou apar în
    datele lui.
  - Cifra asta arată și **cât se potrivește în mod natural**, din expresii comune („este o comună în județul”, `import
    numpy as np`). E reperul pentru scurgerile găsite azi în validări.
  - Pentru GPT-2 și GPT-Neo garantează data.
- **Codul:** `unelte/examen_neutru.py` (descărcarea și seturile) și testele lui. Notele se scriu în
  `lucru/examen_neutru/`, nu în jurnalul Kronos.

## Așteptările lui Claude Code, în cifre (biți pe octet, ferestre de 512)

| set | Kronos #373 | GPT-2 small | GPT-Neo ro 125M |
|---|---|---|---|
| Wikipedia română nouă | **1,25–1,55** | 2,4–3,0 | **1,45–1,80** |
| Wikipedia engleză nouă | 1,60–2,20 | **1,00–1,30** | 1,80–2,60 |
| cod Python nou | **0,95–1,35** | 1,20–1,60 | 3,0–4,0 |

- **Româna:** aștept ca Kronos să rămână mai bun decât GPT-Neo, dar cu o diferență mai mică decât pe validarea lui
  (acolo 1,03 față de 1,57 pe Wikipedia). Pe articolele noi Kronos nu mai are avantajul formei învățate.
- **Engleza de Wikipedia:** Kronos știe doar engleză simplă (TinyStories), deci GPT-2 ar trebui să-l bată clar.
- **Codul nou:** e mai greu decât The Stack pentru toți. Aștept ca Kronos să-l bată tot pe GPT-2, dar mai la limită.

## Ce ar infirma așteptările

- **GPT-Neo mai bun decât Kronos pe Wikipedia română nouă.** Ar însemna că avantajul lui Kronos din comparația de azi
  venea din „acasă”, nu din ce știe.
- **Kronos mai bun decât GPT-2 pe Wikipedia engleză nouă.** Ar fi o surpriză mare: ar arăta că TinyStories + română +
  cod îi ajung și pentru engleza enciclopedică.
- **GPT-2 mai bun decât Kronos pe codul nou.**
- **Oricare cifră în afara intervalului cu peste 0,2** înseamnă că am înțeles greșit ceva. Se scrie în verdict.
- **Peste 5% din bucățile de 50 de litere ale setului nou găsite în datele lui Kronos** înseamnă că setul nu e chiar
  nou (texte copiate de pe web sau cod luat din proiecte vechi). Atunci verdictul se dă și pe partea curată, fără
  textele care se potrivesc.

## Ce nu e perfect (dinainte)

- **Articolele noi nu sunt ca cele vechi.** Mulți le scriu abia începute, unele cu ajutorul unor modele de limbaj.
  Bucăți de text pot exista deja pe web, de exemplu din știri sau biografii.
- **Codul nou din 2026 e adesea scris cu ajutorul unor modele de limbaj** și poate conține bucăți copiate din proiecte
  vechi. Verificarea pe datele lui Kronos prinde asta doar pentru Kronos.
- **Seturile sunt mici** (100.000 de litere fiecare, ca examenul). Diferențe sub ~0,03 nu înseamnă mare lucru.

## Completări cerute de Adrian, scrise înainte de descărcare (17 octombrie, 21:43)

*Adrian a dat „da” cu trei completări. Ele se adaugă aici înainte de orice descărcare. Restul pre-înregistrării rămâne
neschimbat, cu excepția a ce schimbă explicit punctele de mai jos.*

1. **Articolele făcute de roboți.**
   - **Ce e „robot”:** pentru fiecare articol nou se notează cine l-a creat. Articolul e „făcut de robot” dacă crearea
     are semnul de robot al Wikipediei (`bot`), dacă contul e în grupul „bot” sau dacă numele contului se termină în
     „bot” (de exemplu „XyzBot”, „Robot_ABC”).
   - **Ce se raportează:** nota pe **toate articolele**, apoi separat nota **doar pe cele scrise de oameni**, la
     amândouă limbile. Asta înseamnă două seturi în plus, `wikipedia_ro_nou_oameni` și `wikipedia_en_nou_oameni`, cu
     aceleași reguli: primele 100.000 de litere, aceeași ordine la întâmplare.
   - **De ce:** Kronos a văzut șabloanele roboților (sate, specii, sportivi), deci ar fi avantajat pe articolele lor.
   - **Așteptarea:** pe articolele scrise de oameni, Kronos iese cu 0,05–0,20 mai rău decât pe toate, la română.
     GPT-Neo iese cu mai puțin de 0,10 diferență. Dacă la română articolele roboților sunt puține (sub 10% din litere),
     diferența nu înseamnă nimic și se scrie așa.
   - **Verdictul principal la română** („Kronos față de GPT-Neo”) se dă pe amândouă seturile. Dacă cele două dau
     verdicte diferite, contează cel **doar cu oameni**.
2. **Codul copiat în proiecte noi.** Pe lângă regulile de mai sus, se mai exclud:
   - fișierele sub **300 de litere** (în loc de 200);
   - folderele `vendor`, `vendored`, `_vendor`, `third_party`, `thirdparty`, `external`, `extern`, `site-packages`,
     `node_modules`, `dist`, `build`, `migrations`, `venv`, `.venv`;
   - fișierele generate automat: un semn ca „generated by”, „auto-generated”, „do not edit” sau „@generated” în primele
     600 de litere, ori nume ca `*_pb2.py` sau `*_pb2_grpc.py`;
   - fișierele tipice copiate dintr-un șablon: `setup.py`, `conftest.py`, `manage.py`, `wsgi.py`, `asgi.py`,
     `__init__.py`, `docs/conf.py`;
   - fișierele care încep cu o notă de drepturi de autor dinainte de 2026 („Copyright (c) 2018 …”), adică cod vechi
     adus în proiect.
3. **Aceeași fereastră pentru toți.** Cifra principală, pe care se dau toate verdictele, e nota cu **ferestre de 512
   bucăți, la toate cele trei modele**. Separat, doar ca informație, se arată și cea mai bună notă a fiecăruia: cea
   mai mică dintre fereastra de 512 și fereastra lui obișnuită (1.024 la GPT-2, 2.048 la GPT-Neo; la Kronos 512 e chiar
   fereastra lui).
