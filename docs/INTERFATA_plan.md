# Cyberspace: interfața, API-ul și panoul de control

*10 octombrie 2026. Plan scris de Claude (chat) cu Adrian, pentru workstation. Se implementează ca modul pe portul `interfata`, în `module/interfata/`, fără nicio schimbare în `kronos/`. Nucleul Kronos (elevul, examenele, CONTINUUM, paznicul) rămâne cum e; interfața e o fereastră spre el, nu un alt creier.*

## 0. Ce vrem

Adrian și câțiva prieteni folosesc Cyberspace zilnic, puțin câte puțin, iar folosirea îl face pe Kronos mai bun. Concret:

- un **chat** cu două creiere etichetate: **Kronos** (elevul, modelul antrenat de la zero, care învață) și **Profesorul** (Qwen3-4B, local, Apache 2.0, care răspunde util azi);
- **încărcare de fișiere** (text, PDF, imagini cu text): conținutul devine material pentru Kronos și context pentru profesor;
- un **agent de cod** separat, etichetat cu ce model îl mișcă (azi un model local de cod sau Claude Code; Kronos când trece școala de cod);
- **butoane pentru toate modulele**, cele de azi și cele viitoare, generate din registrul Kronos (un modul nou apare singur, cu un buton și o pagină);
- un **API** (compatibil cu stilul OpenAI) pentru VS Code și alte unelte, mai târziu;
- un **panou de control admin** separat, cu autentificare, pentru Adrian;
- **bucla de învățare din folosire**: întrebările oamenilor devin teste și hrană, cu reguli care nu contaminează examenele.

## 1. Cinstea interfeței (reguli care nu se negociază)

1. Fiecare răspuns spune **cine l-a dat**: „Kronos (elev, 98 M)” sau „Profesorul (Qwen3-4B)” sau „Agent de cod (model X)”. Niciodată amestecat fără etichetă.
2. Kronos nu e ascuns când răspunde prost. Un răspuns slab de la Kronos e un **semnal util**: utilizatorul apasă „Kronos n-a știut” și întrebarea intră în coada de învățat.
3. Nimic din ce scriu oamenii nu intră în examene sau în hrană fără regulile din secțiunea 6 (separare, consimțământ, fără fragmente comune cu setul sacru).
4. Chat-ul nu pornește antrenări și nu atinge jurnalul Kronos. Doar panoul admin pornește lucruri, și doar prin uneltele existente (CONTINUUM, STOP, configurări).
5. Placa e a antrenării noaptea; ziua e a oamenilor. Elevul (sub 1 GB) răspunde oricând; profesorul (3,6–4,5 GB) se încarcă doar când placa e liberă, altfel răspunde pe procesor (mai încet) sau spune „profesorul e ocupat, revin în N minute”.

## 2. Arhitectura (toate pe portul `interfata`)

```
module/interfata/
  server.py        FastAPI: pagini + API + SSE pentru răspunsuri în flux
  creiere.py       adaptoare: Elev (modelul Kronos păstrat), Profesor (Qwen), AgentCod (model local de cod sau Claude Code)
  fisiere.py       încărcare, extragere text (txt, md, pdf, docx; imagini prin OCR mai târziu), stocare în lucru/interfata/fisiere/
  utilizatori.py   conturi simple cu coduri de invitație, sesiuni, roluri (admin / prieten)
  catalog.py       jurnalul conversațiilor + coada „de învățat” (întrebări la care Kronos n-a știut)
  admin.py         panoul de control (rută separată, doar admin)
  module_ui.py     citește registrul Kronos și generează butoanele și paginile modulelor
  static/, templates/   HTML simplu (Jinja + htmx), fără framework greu
```

- **Server:** FastAPI, un singur proces, pornit ca serviciu Windows (sau `nssm`), pe portul 8787, doar în rețeaua locală la început. Pentru prieteni din afară: Tailscale sau Cloudflare Tunnel, cu HTTPS; niciodată portul deschis direct spre internet.
- **Stocare:** `lucru/interfata/` cu SQLite pentru utilizatori, conversații și fișiere (nu e jurnalul Kronos; jurnalul rămâne JSONL și neatins). Backup zilnic în arhiva de îngheț.
- **Creierele** sunt înlocuibile din config (`config/interfata.toml`): ce model e „Kronos” (numărul experimentului păstrat, de ex. #295 sau ultimul păstrat de CONTINUUM), ce model e profesorul, ce model e agentul de cod, câți tokeni, ce temperaturi, când are voie profesorul pe placă.
- **Modulele** apar singure: `module_ui.py` citește registrul și contractele Kronos; pentru fiecare modul încărcat face un buton și o pagină cu: ce e, starea (`sanatate()` dacă există), ultimele rezultate din jurnal, acțiunile permise (doar din admin). Un modul viitor (traducere, memorie, calcul) nu cere cod nou în interfață, ci doar un mic descriptor în MANIFEST (`nume_afisat`, `descriere`, `actiuni`).

## 3. Chat

- **Trei butoane sus:** Kronos · Profesorul · Agent de cod. Implicit e **Kronos**, ca să se vadă cât știe; „Profesorul” e la un clic.
- Fiecare mesaj arată eticheta creierului, timpul de răspuns și, la Kronos, numărul modelului (#295).
- La fiecare răspuns de la Kronos: două butoane, „a mers” / „n-a știut”. „N-a știut” pune întrebarea în coada de învățat (secțiunea 6), cu răspunsul profesorului atașat ca lecție candidat.
- Opțiunea „întreabă-i pe amândoi”: răspunsul lui Kronos și al profesorului, unul lângă altul; cea mai directă demonstrație a drumului de parcurs.
- Răspunsurile vin în flux (SSE). Istoricul conversației e per utilizator, cu căutare.
- Limită de lungime pentru elev (contextul lui e scurt); interfața taie cinstit și spune.

## 4. Fișiere

- Încărcare din chat, ca la GPT/Claude: txt, md, pdf, docx; imagini acceptate dar OCR vine mai târziu (ROADMAP).
- Textul extras se stochează cu amprentă, sursă (cine, când) și licență/consimțământ („am voie să-l folosesc pentru învățare?”, bifat la încărcare).
- În chat: profesorul primește textul (sau un rezumat, dacă e lung) ca context; Kronos primește doar primele N cuvinte, cu eticheta „Kronos vede doar începutul”.
- În admin: un fișier marcat „bun pentru hrană” intră în coada de hrană viitoare (secțiunea 6), nu direct în antrenare.

## 5. Agentul de cod

- Buton separat, etichetat cu modelul: la început un model local de cod cu licență verificată (Qwen2.5-Coder-7B-Instruct, Apache 2.0, 4 biți ≈ 5 GB; doar când placa e liberă) sau, mai simplu, nimic local și un link spre Claude Code.
- Rulează în sandbox-ul școlii de cod (proces separat, fără rețea, timeout), niciodată în folderul proiectului.
- Kronos apare aici doar când trece nivelul uneltelor în școala de cod; până atunci butonul spune „Kronos: la școală, nivelul X”.

## 6. Bucla de învățare din folosire (partea care contează)

Întrebările oamenilor sunt cel mai bun test. Dar nu intră în examene oricum:

1. **Coada „de învățat”:** întrebări marcate „n-a știut”, cu răspunsul profesorului. Adrian le vede în admin și le aprobă (sau respinge: private, greșite, periculoase).
2. **Împărțirea sacră:** din cele aprobate, 70 % devin **hrană** (profesorul scrie lecții pe tema lor, ca la fapte), 20 % **examen „întrebările oamenilor”** (reformulate, fără fragmente de 5 cuvinte comune cu hrana), 10 % **set sacru al oamenilor**, niciodată folosit la selecție. Împărțirea se face o dată, la aprobare, și nu se schimbă.
3. **Măsura nouă în CONTINUUM:** capacitatea „întrebările oamenilor” (procent corect pe examenul lor), cu prag de zgomot măsurat. CONTINUUM o vede ca pe fapte și poate alege „dezvoltă” pe ea.
4. **Tabloul de bord public (pentru prieteni):** „din întrebările voastre, Kronos știe azi X %; acum o săptămână știa Y %”. Ăsta e motivul pentru care oamenii revin.
5. **Confidențialitate:** nimic personal nu intră în hrană; aprobarea lui Adrian e filtrul; utilizatorii pot șterge conversațiile lor; ce a intrat deja în hrană rămâne anonimizat.

## 7. API

- `POST /v1/chat/completions` în stilul OpenAI (model = `kronos`, `profesor` sau `agent-cod`), cu flux; destul pentru extensii de VS Code (de ex. Continue) și pentru orice unealtă care știe formatul.
- `GET /api/stare` (modelul curent, placa, ce rulează, CONTINUUM), `GET /api/module`, `GET /api/jurnal?ultimele=20`, `POST /api/fisiere`.
- Chei de API per utilizator, generate din admin, cu limită de cereri pe minut.
- Documentație generată automat (FastAPI o face singur) la `/docs`.

## 8. Panoul de control admin (rută separată, doar Adrian)

- **Stare:** placa (memorie, temperatură, ce proces o folosește), modelul principal, ultimul experiment, CONTINUUM (ciclul curent, ce a ales, de ce), butonul **STOP** (același fișier `lucru/STOP`).
- **Module:** lista din registru, sănătatea fiecăruia, activare/dezactivare din config, ultimele rezultate.
- **Experimente:** jurnalul Kronos citit (nu editat): tabel cu filtre, graficul val_bpb / fapte / notă în timp.
- **CONTINUUM:** lista albă, ferestrele orare, bugetul; pornire/oprire; jurnalul lui.
- **Învățare din folosire:** coada „de învățat”, aprobare/respingere, împărțirea sacră, cât a intrat în hrană.
- **Utilizatori:** invitații, roluri, chei de API, consum.
- **Jurnal de audit:** cine a apăsat ce, când. Append-only.

## 9. Ce nu facem în v0

- Fără aplicație mobilă (pagina merge pe telefon).
- Fără voce (ROADMAP, odată cu traducerea).
- Fără OCR pe imagini (ROADMAP).
- Fără deschiderea portului direct spre internet; doar Tailscale/Cloudflare Tunnel.
- Fără schimbări în `kronos/`; dacă un contract trebuie extins (de ex. `interfata`), se raportează și se așteaptă aprobarea.

## 10. Etape

| Etapa | Ce conține | Gata când | Efort estimat |
| --- | --- | --- | --- |
| **v0, săptămâna 1 (zile; nopțile antrenează)** | server + chat Kronos/Profesor cu etichete și „n-a știut”; conturi cu invitație; încărcare txt/md/pdf; admin cu stare, STOP, module, jurnal citit; API `/v1/chat/completions` | Adrian și 2 prieteni folosesc chat-ul în rețeaua locală; 20 de întrebări în coada „de învățat” | 3–4 zile de Claude Code |
| **v1, săptămâna 2** | bucla de învățare: aprobare, împărțirea sacră, hrana din întrebări, examenul „întrebările oamenilor”, capacitatea în CONTINUUM, tabloul public | prima noapte în care CONTINUUM alege „dezvoltă întrebările oamenilor” și examenul urcă | 3 zile |
| **v2, săptămâna 3** | agentul de cod (model local sau Claude Code), docx, chei de API, Tailscale pentru prieteni din afară, backup | un prieten din alt oraș folosește Cyberspace | 2–3 zile |
| **v3 (ROADMAP)** | OCR, voce, traducere RO↔EN în chat (treapta 6), memoria cu proveniență (planul „Modul viitor”) | după tokenizer-ul nou și linia cu română | – |

## 11. Reguli pentru Claude Code

- CLAUDE.md rămâne deasupra. `kronos/` neatins; examenul neatins; jurnalele nu se editează de mână; testele trec înainte de „gata”; commit în română după fiecare pas.
- Interfața nu pornește antrenări și nu scrie în jurnalul Kronos; folosește uneltele existente.
- Teste pentru fiecare piesă (server pe port de probă, creiere de probă, fișiere de probă); nicio funcționalitate „mock” prezentată ca reală.
- Rapoarte cu etichete: EXISTENT / IMPLEMENTAT / EXPERIMENTAL / IPOTEZĂ / ROADMAP / BLOCAT.
- Licențele oricărui pachet nou verificate înainte de instalare; preferate: FastAPI, Jinja2, htmx, pypdf, python-docx, uvicorn (toate cu licențe permisive; de verificat la instalare).
