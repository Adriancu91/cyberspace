# Modelul Kronos pentru OS: #459, KGR1 Q8_0 (S39, comanda C-24)

| | |
|---|---|
| modelul | **#459**, linia `w2_reteta_A_cont` (S38: rețeta A, încă 6 ore din #441; verdict S38 CONFIRMAT, română curat 1,2162) |
| arhitectura | `kronos_gpt`: 12 straturi, 12 capete, n_emb 768, context 512, vocabular 16.384, cap legat; tokenizerul w2 inclus |
| fișierul | `kronos_459_q8_0.kgr` (KGR1, matricile Q8_0, restul F32) |
| mărimea | **110.859.040 octeți** (105,7 MiB) |
| SHA-256 | `e80618b4ef555983085c3127acb10114e4f4915d939734207aa849ba0f6d382e` |
| Release | **nefăcut încă**: în rularea programată a executantului, comanda `gh` cere aprobare (nu e în uneltele lui permise), iar nimeni nu era de față. Fișierul e pe workstation, în `C:\Kronos\cyberspace\lucru\export\kronos_459_q8_0.kgr` (nu în Git). Eticheta propusă: `kronos-kgr1-459` |

Comanda pentru Release (o rulează Adrian sau o sesiune cu aprobare, din `C:\Kronos\cyberspace`):

    gh release create kronos-kgr1-459 lucru/export/kronos_459_q8_0.kgr --repo Adriancu91/cyberspace --title "Kronos #459 KGR1 Q8_0" --notes "SHA-256 e80618b4ef555983085c3127acb10114e4f4915d939734207aa849ba0f6d382e, 110859040 octeți"

## Testul pe hardware

Motorul OS, pe acest fișier, trebuie să dea **exact** aceleași simboluri (codare + 5 simboluri greedy, argmax fără
întâmplare). Așa au ieșit din `unelte/inferenta_bruta.py` (Python + numpy, Q8_0 desfăcut la încărcare):

| text | simbolurile textului | primele 5 generate | textul generat |
|---|---|---|---|
| `Ana are mere.` | 65, 1988, 1585, 2717, 46 | 2233, 1585, 32, 475, 50 | `" Acum are 1192"` |
| `Capitala României este` | 7132, 1373, 2710, 5734, 1744 | 8369, 1497, 4444, 6882, 46 | `" orașul Baia Mare."` |
| `def suma(a, b):` | 2082, 15746, 40, 97, 44, 1376, 1754 | 1510, 1947, 1358, 1646, 1376 | `"\n    return a + b"` |

Marja cea mai mică dintre primul și al doilea logit, pe pașii greedy: 0,050, 0,022 și 0,045 (deci un motor cu abateri
de ordinul 1e-3 ar trebui să dea aceleași simboluri; o abatere de 0,02 poate schimba al doilea text). Al doilea text
e greșit ca fapt (capitala e București): asta e ce știe modelul, nu o eroare a motorului.

Toleranța pe logit-uri pentru modelul mare rămâne întrebarea deschisă către Adrian din S37 (vezi `README.md`).
