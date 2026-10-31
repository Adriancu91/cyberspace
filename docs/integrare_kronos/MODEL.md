# Modelul Kronos pentru OS: #477, KGR1 Q8_0 (S54, comanda C-44)

| | |
|---|---|
| modelul | **#477**, linia `w2_reteta_A_cont3` (S51: rețeta A, încă 6 ore din #459; verdict S51 CONFIRMAT, română curat 1,2097 față de 1,2162 la #459) |
| arhitectura | `kronos_gpt`: 12 straturi, 12 capete, n_emb 768, context 512, vocabular 16.384, cap legat; tokenizerul w2 inclus |
| fișierul | `kronos_477_q8_0.kgr` (KGR1, matricile Q8_0, restul F32) |
| mărimea | **110.859.040 octeți** (105,7 MiB) |
| SHA-256 | `bcbe8187087dbb3e531a8a7b10991cd24ea14a6e067d07c0fcbb8d3edd753963` (și în `kronos_477_q8_0.kgr.sha256`) |
| Release | **nefăcut încă**: în rularea programată a executantului (31 oct 14:00), comanda `gh` cere aprobare, iar nimeni nu era de față. Fișierul e pe workstation, în `C:\Kronos\cyberspace\lucru\export\kronos_477_q8_0.kgr` (nu în Git), cu suma alături în `kronos_477_q8_0.kgr.sha256`. Eticheta: `kronos-kgr1-477` |

Comanda pentru Release (o rulează Adrian sau o sesiune cu aprobare, din `C:\Kronos\cyberspace`):

    gh release create kronos-kgr1-477 lucru/export/kronos_477_q8_0.kgr lucru/export/kronos_477_q8_0.kgr.sha256 --repo Adriancu91/cyberspace --title "Kronos #477 KGR1 Q8_0" --notes "SHA-256 bcbe8187087dbb3e531a8a7b10991cd24ea14a6e067d07c0fcbb8d3edd753963, 110859040 octeți"

## Testul pe hardware

Motorul OS, pe acest fișier, trebuie să dea **exact** aceleași simboluri (codare + 5 simboluri greedy, argmax fără
întâmplare). Așa au ieșit din `unelte/inferenta_bruta.py` (Python + numpy, Q8_0 desfăcut la încărcare):

| text | simbolurile textului | primele 5 generate | textul generat |
|---|---|---|---|
| `Ana are mere.` | 65, 1988, 1585, 2717, 46 | 2233, 1585, 32, 475, 50 | `" Acum are 1192"` |
| `Capitala României este` | 7132, 1373, 2710, 5734, 1744 | 8369, 1497, 2207, 117, 44 | `" orașul Bacău,"` |
| `def suma(a, b):` | 2082, 15746, 40, 97, 44, 1376, 1754 | 1510, 1947, 1358, 1646, 1376 | `"\n    return a + b"` |

Marja cea mai mică dintre primul și al doilea logit, pe pașii greedy: 0,026, 0,024 și 0,016 (mai mici decât la #459:
0,050, 0,022, 0,045). Un motor cu abateri de ordinul 1e-3 ar trebui să dea aceleași simboluri; o abatere de ~0,015
poate schimba al treilea text. Al doilea text e greșit ca fapt (capitala e București): asta e ce știe modelul, nu o
eroare a motorului.

Toleranța pe logit-uri pentru modelul mare rămâne întrebarea deschisă către Adrian din S37 (vezi `README.md`).

## Rezerva: #459

#459 (linia `w2_reteta_A_cont`, S38, română curat 1,2162) rămâne păstrat și poate fi acceptat în continuare de OS:

| | |
|---|---|
| fișierul | `kronos_459_q8_0.kgr` (neschimbat, tot în `lucru/export/`) |
| mărimea | **110.859.040 octeți** |
| SHA-256 | `e80618b4ef555983085c3127acb10114e4f4915d939734207aa849ba0f6d382e` |
| primele 5 generate | `Ana are mere.` → 2233, 1585, 32, 475, 50; `Capitala României este` → 8369, 1497, 4444, 6882, 46 (`" orașul Baia Mare."`); `def suma(a, b):` → 1510, 1947, 1358, 1646, 1376 |
