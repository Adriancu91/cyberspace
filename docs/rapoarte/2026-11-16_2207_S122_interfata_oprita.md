# S122 (C-129) — interfața de pe 8787 oprită cât rulează lanțul S117 → S123 → S121 → S119

*Executant, 16 noiembrie 2026, 22:07. Pașii 1–3 din S122. Pasul 4 (repornirea cu câștigătorul) vine după S119.*

## Pe scurt

- **Interfața de pe portul 8787 e oprită** de la **22:00:11** (cele 2 procese ale ei, cu #651, pornite azi la 15:06).
  Portul nu mai răspunde local (verificat la 22:00:14).
- **Nu mai pornește singură:** paznicul de procese (care rulează la 15 minute) se uită acum după un fișier-comutator,
  `lucru\STOP_INTERFATA`. Cât există fișierul, nu repornește interfața. Claude Code și CONTINUUM le păzește în continuare ca înainte.
- **S117 n-a fost atinsă:** procesul ei (28848) trăiește, ora 2 din 4 s-a încheiat la 21:32 (val_bpb 1,0898), placa 6.563 MB / 63 °C.
- **Teste:** 1488 trec, 1 sărit, 0 pică.

## Ce am făcut, exact

1. **Oprirea (pasul 1).** Scriptul `lucru/cascada/S122_proba/opreste_8787.py` (în afara Git, ca la S112) a oprit doar
   procesele care au `module.interfata` în comandă:
   - PID 6336 și 29796 (lansatorul din `.venv` și procesul lui): `python -m module.interfata --config config/conv_w2_mare_24zc.toml --experiment 651 --port 8787 --dispozitiv cpu --experiment-text 651`, pornite 16 nov 15:06:41.
   - Înainte: portul 8787 răspundea. După: nu mai răspunde, niciun proces `module.interfata` rămas.
   - Jurnalul: `lucru/cascada/S122_proba/oprire.json`.
2. **Oprirea repornirii automate (pasul 2), fără `kronos/` și fără sarcini Windows.** Am schimbat `unelte/paznic_procese_ws.ps1`:
   dacă interfața nu ascultă **și** există `lucru\STOP_INTERFATA`, paznicul nu o pornește (parametru nou `-StopInterfata`
   pentru teste; implicit `lucru\STOP_INTERFATA`). Fișierul l-am pus la 22:00:11. Sarcina programată a paznicului **n-am atins-o**
   (regulile mele nu-mi dau voie la sarcini programate, iar paznicul păzește și Claude Code și CONTINUUM).
   - Test nou: `teste/test_dupa_logare.py::test_paznicul_nu_porneste_interfata_cand_exista_comutatorul`; testul vechi al paznicului
     primește acum un comutator inexistent, ca să nu depindă de fișierul real.
   - O rulare `-Proba` a paznicului adevărat din linia de comandă a fost blocată de permisiuni; comportamentul e verificat prin testul de mai sus.
3. **Cum se anulează** (oricând, de exemplu dacă vrei chat-ul înapoi):
   ```
   Remove-Item C:\Kronos\cyberspace\lucru\STOP_INTERFATA
   ```
   La următoarea trecere a paznicului (cel mult 15 minute) interfața pornește singură, cu modelul din `unelte\interfata_ws.ps1` (#651).
4. **Pasul 3:** la fiecare trecere următoare verific că portul 8787 nu răspunde; dacă paznicul o repornește totuși, o opresc și scriu ora.

## Teste

`CUDA_VISIBLE_DEVICES=-1 python -m pytest`: **1488 trec, 1 sărit, 0 pică** (7 min 10 s).

## Ce urmează

- S117 se termină pe la ~23:40, apoi examenele ei; apoi S123 (E0), S121, S119.
- La final (pasul 4): interfața repornită pe 8787 cu câștigătorul, comutatorul șters, verificarea cu cele 5 întrebări S114 +
  „Cât face 3x7?” + cele 2 „din text” ale C-119 → al doilea raport `..._S122_interfata_repornita.md`.
- **De la tine, Adrian:** nimic. Dacă vrei chat-ul mai devreme, scrie în hub sau șterge fișierul de mai sus.
