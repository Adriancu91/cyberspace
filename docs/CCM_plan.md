# Cyber-Compute-Module (CCM) — planul adaptat pentru Kronos

Ideea lui Adrian (29 oct 2026, dezvoltată cu ChatGPT, adaptată de centrul de comandă la ce există).
Aprobat prin delegare (29 oct 10:20). Sarcinile: S47, S48, S49 în `plan/coada.md`.

## Ce e, într-o frază
Kronos decide **ce** calculează; CCM decide **cum** se calculează cel mai repede pe calculatorul respectiv: are câteva variante
pentru fiecare operație, le verifică față de o referință, le măsoară și o alege pe cea mai bună — doar pe baza măsurătorilor.

## Ce există deja (nu se refac)
- Portul `inferenta` + `module/inferenta_kgr1.py` (învelește `unelte/inferenta_bruta.py`, fără PyTorch) — referința de corectitudine.
- Formatul KGR1 (Q8_0) și vectorii de test din `integrare/kronos/` (hub); OS-ul are a doua implementare, cu simboluri identice.
- În OS: C-27 `run kronos-calcul --cauta` (aceeași idee, pe procesorul OS-ului) — CCM e versiunea lui pe Windows, cu același format de reglaj.
- Cutia izolată `unelte/kronos_cod/cutie.py` (pentru variante scrise mai târziu de Kronos-Cod).

## Ce s-a tăiat din planul original (și de ce)
- Biblioteca pe 7 niveluri (aritmetică … metode numerice): Kronos folosește ~6 operații (înmulțire matrice-vector/matrice, softmax,
  normalizare, atenție, desfacerea Q8_0, eșantionarea). Biblioteca = aceste operații × câteva variante.
- Cache-ul SSD → RAM pentru scheme: variantele sunt cod mic; ajunge un fișier de reglaj per calculator.
- Împărțirea automată CPU + GPU a fiecărui calcul: la ~100M parametri transferurile costă de obicei mai mult; se alege un dispozitiv
  pentru tot pasul, iar împărțirea se încearcă doar unde măsurătoarea o justifică.
- CCM nu antrenează nimic și nu atinge antrenarea (PyTorch rămâne cum e).

## Unde trăiește
- `module/calcul/` (pachet nou): `variante/` (câte un fișier pe operație), `banc.py` (măsurare + verificare), `reglaj.py` (citire/scriere reglaj).
- `module/inferenta_ccm.py`: a doua implementare a portului `inferenta`, care folosește variantele alese. **Fără schimbări în `kronos/`.**
  Rezerva: dacă o variantă lipsește sau nu e verificată → calea din `inferenta_kgr1` (referința).
- Reglajul: `lucru/ccm/reglaj-<calculator>.json` (în afara Git); formatul se pune în hub (`integrare/kronos/CCM_REGLAJ.md`), ca OS-ul să-l poată folosi.

## Reguli (judecătorul rămâne în afara lui Kronos)
1. O variantă intră doar dacă dă **aceleași simboluri** ca referința la vectorii KGR1 (greedy), iar logit-urile sunt în toleranța scrisă înainte.
2. Viteza se raportează doar din măsurători repetate (median + împrăștiere), cu timpul complet: pregătire + transfer + calcul.
3. Nicio „accelerare” declarată fără cifre; variantele mai lente se notează ca respinse, cu motivul.
4. Placa video doar când e liberă (nu în timpul antrenării, nu în ferestrele OS/GPU cu Adrian); VRAM sub ~7 GB.
5. Nimic instalat fără „da”; se folosesc ce e deja în `.venv` (numpy, PyTorch).
6. Testele și examenul nu se ating; `python -m pytest` verde după fiecare pas.

## Etape
- **S47 — profilul și bancul (procesor):** unde se duce timpul la un răspuns al lui #459 (pe operații); bancul de măsurare + verificare;
  variantele de bază pe procesor (numpy pe un fir / pe toate nucleele, mărimea blocurilor, desfacerea Q8_0 o dată vs. la fiecare pas). Raport cu cifre.
- **S48 — `inferenta_ccm` + reglajul (procesor):** modulul nou pe portul `inferenta`, reglajul salvat, rezerva; trece `teste_contracte/`.
- **S49 — varianta pe placa video sub Windows (PyTorch, cu placa liberă):** fp32/fp16/bf16, cu verificarea simbolurilor; CCM alege între procesor și placă după măsurători.
- **Mai târziu:** formatul reglajului trimis OS-ului (C-27 îl citește); variante noi scrise de Kronos-Cod și verificate de bancul CCM în cutia izolată
  (bucla de autoîmbunătățire); placa video în OS când cyber-gpu ajunge la primul calcul.

## Criterii de acceptare (din planul original, păstrate)
Variantele nevalidate nu sunt alese; rezultatele corecte în toleranță; costurile de transfer incluse; comparația cu referința;
Kronos merge și fără CCM (rezerva); nicio afirmație de accelerare fără test.
