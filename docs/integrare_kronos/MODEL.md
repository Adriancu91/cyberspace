# Modelul Kronos pentru OS: #513, KGR1 Q8_0 (S83b, comanda C-82)

| | |
|---|---|
| modelul | **#513**, linia `w2_romana_r1` (S76b: 5 ore din #477 cu răspunsuri în română, verdict AJUTĂ — R1 pe instrucțiuni 98,97 față de 37,47 la #477, felurile vechi 99,68, română curat 1,2060, cod curat 0,7247, R2 0,4050; S76c: URMEAZĂ la limită pe întrebări reformulate, 83,22 față de 61,38 la #477; slab la „județ și țară”) |
| arhitectura | `kronos_gpt`: 12 straturi, 12 capete, n_emb 768, context 512, vocabular 16.384, cap legat; tokenizerul w2 inclus — aceeași ca la #477 |
| fișierul | `kronos_513_q8_0.kgr` (KGR1, matricile Q8_0, restul F32) |
| mărimea | **110.859.008 octeți** (105,7 MiB). Față de #477 (110.859.040) diferă doar antetul (textul `sursa`), arhitectura e aceeași: aceiași tensori, în aceeași ordine, cu aceleași forme; textul `sursa` e cu 5 octeți mai scurt, iar antetul se aliniază la 32 de octeți → 32 de octeți mai puțin |
| SHA-256 | `66f734b3136206d1be8825b1188b1a90f0c5b00c2e19746547f327f9b95c5859` (și în `kronos_513_q8_0.kgr.sha256`) |
| Release | **nefăcut încă**: în rularea programată a executantului (7 nov 02:30), comanda `gh` cere aprobare, iar nimeni nu era de față. Fișierul e pe workstation, în `C:\Kronos\cyberspace\lucru\export\kronos_513_q8_0.kgr` (nu în Git), cu suma alături în `kronos_513_q8_0.kgr.sha256`. Eticheta: `kronos-kgr1-513` |

Comanda pentru Release (o rulează Adrian sau o sesiune cu aprobare, din `C:\Kronos\cyberspace`):

    gh release create kronos-kgr1-513 lucru/export/kronos_513_q8_0.kgr lucru/export/kronos_513_q8_0.kgr.sha256 --repo Adriancu91/cyberspace --title "Kronos #513 KGR1 Q8_0" --notes "SHA-256 66f734b3136206d1be8825b1188b1a90f0c5b00c2e19746547f327f9b95c5859, 110859008 octeți"

## Testul pe hardware

Motorul OS, pe acest fișier, trebuie să dea **exact** aceleași simboluri (codare + 5 simboluri greedy, argmax fără
întâmplare). Așa au ieșit din `unelte/inferenta_bruta.py` (Python + numpy, Q8_0 desfăcut la încărcare); PyTorch pe
aceleași greutăți Q8_0 desfăcute dă aceleași simboluri pe toate pozițiile, cu diferența maximă pe logit-uri 1,4e-4:

| text | simbolurile textului | primele 5 generate (#513) | textul generat (#513) | #477, pentru comparație |
|---|---|---|---|---|
| `Ana are mere.` | 65, 1988, 1585, 2717, 46 | 2233, 1585, 32, 475, 50 | `" Acum are 1192"` | la fel |
| `Capitala României este` | 7132, 1373, 2710, 5734, 1744 | 8369, 1497, 4444, 6882, 44 | `" orașul Baia Mare,"` | 8369, 1497, 2207, 117, 44 (`" orașul Bacău,"`) |
| `def suma(a, b):` | 2082, 15746, 40, 97, 44, 1376, 1754 | 1510, 1947, 1358, 1778, 1376 | `"\n    return a * b"` | 1510, 1947, 1358, 1646, 1376 (`"\n    return a + b"`) |

Marja cea mai mică dintre primul și al doilea logit, pe pașii greedy: **0,166, 0,172 și 0,095** (mult mai mari decât la
#477: 0,026, 0,024, 0,016). Un motor cu abateri de ordinul 1e-3 (sau chiar 1e-2) dă aceleași simboluri. Al doilea text e
greșit ca fapt (capitala e București), iar al treilea înmulțește în loc să adune: asta e ce știe modelul, nu o eroare a
motorului.

Toleranța pe logit-uri pentru modelul mare rămâne întrebarea deschisă către Adrian din S37 (vezi `README.md`).

## Rezerva: #477

#477 (linia `w2_reteta_A_cont3`, S51, română curat 1,2097) rămâne păstrat și poate fi acceptat în continuare de OS:

| | |
|---|---|
| fișierul | `kronos_477_q8_0.kgr` (neschimbat, tot în `lucru/export/`, cu `kronos_477_q8_0.kgr.sha256`) |
| mărimea | **110.859.040 octeți** |
| SHA-256 | `bcbe8187087dbb3e531a8a7b10991cd24ea14a6e067d07c0fcbb8d3edd753963` |
| Release | `kronos-kgr1-477` — nefăcut de executant (comanda e în raportul S54, `docs/rapoarte/2026-10-31_1408_S54_model_477.md`) |
| primele 5 generate | `Ana are mere.` → 2233, 1585, 32, 475, 50; `Capitala României este` → 8369, 1497, 2207, 117, 44 (`" orașul Bacău,"`); `def suma(a, b):` → 1510, 1947, 1358, 1646, 1376; marjele greedy 0,026 / 0,024 / 0,016 |

## Rezerva: #459

#459 (linia `w2_reteta_A_cont`, S38, română curat 1,2162) rămâne păstrat și poate fi acceptat în continuare de OS:

| | |
|---|---|
| fișierul | `kronos_459_q8_0.kgr` (neschimbat, tot în `lucru/export/`) |
| mărimea | **110.859.040 octeți** |
| SHA-256 | `e80618b4ef555983085c3127acb10114e4f4915d939734207aa849ba0f6d382e` |
| primele 5 generate | `Ana are mere.` → 2233, 1585, 32, 475, 50; `Capitala României este` → 8369, 1497, 4444, 6882, 46 (`" orașul Baia Mare."`); `def suma(a, b):` → 1510, 1947, 1358, 1646, 1376 |
