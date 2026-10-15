# Pornirea automată pe workstation (12 octombrie 2026)

*Ce e făcut, ce se întâmplă la o repornire de Windows și ce variante sunt pentru restul. Adrian a aprobat logarea
automată (varianta B) luni seara. **Joi, 15 octombrie, seara, Adrian a activat Autologon** (contul `Computer`, cu
parola locală). Rămân setarea din BIOS și o repornire de probă (vezi la sfârșit).*

## Ce e făcut

- **`unelte/noapte_ws.ps1`** pornește (sau reia) o antrenare lungă fără nicio fereastră și scrie tot în
  `lucru/noapte_<configurare>.log`. Nu pornește nimic dacă există butonul STOP (`lucru/STOP`), dacă antrenarea rulează
  deja sau dacă a trecut de ora de oprire.
- **`unelte/programeaza_noapte_ws.ps1`** o pune în Task Scheduler. Pentru noaptea de azi sunt trei sarcini:

| Sarcina | Când | Ce face |
|---|---|---|
| Kronos noapte ws_w1 | azi la 19:00 | pornește W1, 10 ore |
| Kronos oprire ws_w1 | mâine la 07:30 | dacă încă rulează, cere oprirea (ora în curs se încheie și e ultima) |
| Kronos reluare ws_w1 | la fiecare logare în Windows, până la 07:30 | reia antrenarea de unde a rămas |

- **De ce se poate relua:** fiecare oră e un experiment în jurnalul Kronos, iar starea modelului se salvează după
  fiecare oră. Aceeași comandă continuă cu ora următoare. Se pierde doar ora întreruptă.
- Sarcinile rulează în contul `Computer`, **doar cât timp el e logat** în Windows. Nu cer parolă și nici drepturi de
  administrator. Se șterg cu `... programeaza_noapte_ws.ps1 -Config config/ws_w1.toml -Sterge`.
- Windows e pe „niciodată” la somn și hibernare pe priză, iar unealta de antrenare cere și ea sistemului să stea treaz.
- Încercat azi pe repetiția W1: sarcina a pornit singură la ora dată, fără fereastră, și s-a încheiat cu succes.

## Ce se întâmplă acum la o repornire de Windows

1. Calculatorul repornește și **se oprește la ecranul de logare**.
2. Până nu se loghează cineva, nu rulează nimic: nici antrenarea, nici Claude Code.
3. După logare, „Kronos reluare ws_w1” reia antrenarea singură. Claude Code trebuie pornit de mână.

Adică: **partea a doua merge singură, prima (logarea) nu.** Asta e singura verigă lipsă.

## Variantele pentru veriga lipsă

| Varianta | Ce rezolvă | Riscuri | Cere |
|---|---|---|---|
| **A. Rămâne ca acum** | după logarea de mână, antrenarea se reia singură | o repornire noaptea pierde restul nopții | nimic |
| **B. Logare automată în Windows**, cu blocarea ecranului imediat după | totul repornește singur: antrenarea și, cu o sarcină în plus, Claude Code cu Remote Control | parola contului rămâne salvată pe disc (protejată de Windows, dar recuperabilă de cineva cu drepturi de administrator pe acest calculator); cine pornește calculatorul ajunge într-o sesiune logată, chiar dacă blocată; dacă discul nu e criptat, cine îl scoate poate citi tot | „da”-ul lui Adrian, parola contului, drepturi de administrator |
| **C. Sarcină care rulează „fie că utilizatorul e logat, fie că nu”** | antrenarea pornește după repornire fără nicio logare | merge doar pentru antrenare, nu și pentru Claude Code (el are nevoie de o fereastră de terminal); rulează „în culise”, fără ecran, iar pe acest calculator n-am încercat încă placa video așa; parola e ținută de Task Scheduler | drepturi de administrator, parola contului |
| **D. Mai puține reporniri** (se adaugă la oricare) | scade șansa să fie nevoie | niciunul | orele active și pauza actualizărilor în Windows Update; în BIOS, „pornește singur când revine curentul”; un UPS |

**Recomandarea mea:** D acum (nu are riscuri), apoi **B**, dacă la workstation ajung doar oameni de încredere. B e
singura care repornește și Claude Code. Dacă nu, C pentru antrenare și Claude Code pornit de mână.

**Dacă alegi B, pașii ar fi** (nu am făcut niciunul):
1. Logarea automată se pune cu unealta Microsoft „Autologon” (Sysinternals), care ține parola criptată în Windows, nu
   în clar în registru. Pe Windows 11 trebuie întâi oprită opțiunea „permite doar conectarea cu Windows Hello”.
2. O sarcină la logare care blochează imediat ecranul (`rundll32 user32.dll,LockWorkStation`). Sarcinile pornite
   rulează mai departe cu ecranul blocat.
3. O sarcină la logare care deschide un terminal cu `claude --continue --remote-control "Kronos"` în
   `C:\Kronos\cyberspace`. De încercat o dată cu tine de față: dacă reia conversația potrivită și dacă apare pe telefon.

## Remote Control pentru Claude Code, pe scurt

- Claude Code e instalat la `C:\Users\Computer\.local\bin\claude.exe` (versiunea 2.1.296).
- Azi sesiunea merge pentru că cineva a pornit-o de mână. Dacă Windows repornește sau fereastra se închide, Remote
  Control se pierde până o pornește cineva din nou. **Antrenarea nu depinde de Claude Code:** o pornește și o reia
  Task Scheduler.
- Cu A sau C, după o repornire Claude Code se pornește de mână. Cu B, pornește singur.

## Hotărât de Adrian (12 octombrie, 19:30): varianta B, logare automată cu ecranul blocat imediat

**Ce am făcut eu (fără parolă, fără drepturi de administrator):**
- Am descărcat **Autologon** de la Microsoft Sysinternals în `C:\Kronos\unelte_windows\Autologon64.exe` (în afara
  proiectului și a Git-ului). Verificat: semnătura digitală e validă, „Microsoft Corporation”; versiunea 3.10;
  sha256 `5d96bbc4e5b726d8…`. **Nu l-am rulat**: cere parola ta și drepturi de administrator.
- Am pus în Task Scheduler două sarcini care pornesc la fiecare logare (`unelte/programeaza_dupa_logare_ws.ps1`):

| Sarcina | Ce face |
|---|---|
| Kronos blocare ecran | blochează ecranul, dar doar dacă logarea e la cel mult 5 minute după pornirea calculatorului (adică logarea automată); când te loghezi tu mai târziu, nu te blochează |
| Kronos Claude Code | la 30 de secunde după logare pornește `claude --continue --remote-control "Kronos"` în `C:\Kronos`, într-o fereastră de terminal; nu pornește a doua oară dacă rulează deja |

- Reluarea antrenării la logare („Kronos reluare …”) exista deja; se pune pentru fiecare noapte, odată cu pornirea ei.
- Ce fac aceste sarcini se notează în `lucru/dupa_logare.log`.

**Pașii, pentru Adrian (1 și 2 sunt făcuți: joi, 15 octombrie, seara):**
1. Click dreapta pe `C:\Kronos\unelte_windows\Autologon64.exe` → „Run as administrator” → Yes. La prima pornire apare
   licența: „Agree”.
2. În fereastră: **Username** `Computer`, **Domain** `DESKTOP-BR58S2C`, **Password** parola ta de Windows → **Enable**.
   Trebuie să apară „Autologon successfully configured”. Parola o scrii doar acolo: unealta o ține criptată în
   Windows (secret LSA), nu în clar în registru. Nu mi-o scrie mie și nu o pune în niciun fișier.
   **Făcut (15 octombrie).** Verificat de Claude Code, doar citind registrul: logarea automată e pornită, pentru
   `DESKTOP-BR58S2C\Computer`, iar parola **nu** e în registru în clar (valoarea `DefaultPassword` nu există).
3. **Încearcă o dată, cât ești de față:** repornește Windows. Ar trebui să vezi, fără să atingi nimic: logarea, ecranul
   blocat după câteva secunde, iar pe telefon, după ~1 minut, sesiunea „Kronos” la Remote Control. Deblochezi cu
   parola și te uiți în `lucru\dupa_logare.log`. **Încă nefăcut:** se face într-o dimineață, după 06:45, când nu
   rulează nimic noaptea pe placă (nu acum).
4. **În BIOS (F2 la pornire): AC Recovery = Power On**, ca workstation-ul să pornească singur când revine curentul.
   Fără asta, după o pană de curent rămâne oprit și nimic din cele de mai sus nu apucă să ruleze. **Încă nefăcut.**
5. ~~Tot în BIOS: System Logs → Power Events.~~ Nu mai trebuie: cauza celor două opriri de luni e cunoscută (un
   angajat a închis workstation-ul de mână). De luni seara, pe priză, butonul de pornire și capacul sunt pe „Nu face
   nimic” în Windows; butonul ținut apăsat ~4 secunde oprește în continuare calculatorul.

**Ce NU am putut încerca:**
- Autologon însuși (cere parola și drepturi de administrator).
- Pornirea lui Claude Code din sarcină: ar fi pornit a doua sesiune peste cea în care lucrez. Comanda și opțiunile
  există în Claude Code 2.1.296 (`--continue`, `--remote-control [name]`), dar prima rulare adevărată e cea de la pasul 3.
- Blocarea ecranului am încercat-o doar pe ramura „nu blochez” (calculatorul era pornit de 154 de minute).

**De știut:**
- Pe acest Windows e activă opțiunea „doar conectare cu Windows Hello” (valoarea 2). Autologon scrie direct setările
  de logare automată și de obicei merge și așa; dacă la pasul 3 rămâne totuși la ecranul de logare, se oprește acea
  opțiune din Setări → Conturi → Opțiuni de conectare și se încearcă din nou.
- **Riscurile, așa cum le-ai acceptat:** oricine pornește calculatorul ajunge într-o sesiune logată (blocată după câteva
  secunde, dar logată); parola stă criptată pe disc și poate fi scoasă de cineva cu drepturi de administrator pe acest
  calculator; discul nu pare criptat cu BitLocker, deci cine îl scoate poate citi tot.
- **Cum se oprește:** rulezi Autologon din nou și apeși „Disable”. Sarcinile de după logare se șterg cu
  `powershell -ExecutionPolicy Bypass -File unelte\programeaza_dupa_logare_ws.ps1 -Sterge`. Ca să sari o singură dată
  peste logarea automată, ții apăsat Shift în timpul pornirii.
- Dacă schimbi parola de Windows, Autologon trebuie rulat din nou cu parola nouă.

## Ce a rămas de făcut de Adrian

1. ~~Autologon~~: **făcut** joi, 15 octombrie, seara.
2. **Repornirea de probă** (pasul 3): într-o dimineață, după 06:45, cu nimic pe placă.
3. **BIOS: AC Recovery = Power On** (pasul 4). Până atunci, o pană de curent oprește tot până vine cineva.
4. Dacă vrei un UPS (pe laptop, alimentarea a stricat o noapte întreagă; aici, opririle de luni au fost un om, nu
   curentul; joi seara, la pana de curent din oraș, workstation-ul n-a fost atins).
5. Mai puține reporniri: orele active și pauza actualizărilor în Windows Update.

**De știut (15 octombrie):** după o repornire, logarea automată pornește sarcinile „după logare” (Claude Code,
blocarea ecranului) și CONTINUUM, dar nu reia singură școala de cod de la noapte: scriptul nopții
(`unelte/noapte_conversatie.ps1`) pornește doar la 19:00. Școala se reia de unde a rămas cu aceeași comandă.
