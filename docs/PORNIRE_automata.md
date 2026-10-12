# Pornirea automată pe workstation (12 octombrie 2026)

*Ce e făcut, ce se întâmplă la o repornire de Windows și ce variante sunt pentru restul. Logarea automată în Windows
NU e activată: o hotărăște Adrian.*

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

## Ce trebuie să hotărască Adrian

1. A, B sau C (și D, pe care îl recomand oricum).
2. Dacă B: îmi dă „da”-ul și e de față la prima încercare.
3. Dacă vrea un UPS (pe laptop, alimentarea a stricat o noapte întreagă).
