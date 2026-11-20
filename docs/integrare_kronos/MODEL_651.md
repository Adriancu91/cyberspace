# Modelul Kronos cel mare pentru OS: #651, KGR1 Q8_0 (S128, comanda C-150)

| | |
|---|---|
| modelul | **#651**, linia `w2_mare_24zc` — modelul în uz al chat-ului de pe 8787 (fila Chat și fila „din text”, prin `unelte/interfata_ws.ps1`). A rămas câștigătorul după S117, S121, S124, S126 și S127 (ultima re-măsurare, S127: română curat 1,0878, corecte S15 + S4 + tipuri noi 228, R1 99,31, chat (a)+(b) 25, calcule 1/200, formulări 20,5 %) |
| arhitectura | `kronos_gpt`: **24 de straturi**, 12 capete, n_emb 768, context 512, vocabular 16.384, cap legat (`cap_legat = 1`), `ln_eps = 1e-5`; **183.086.592 de parametri** scriși (capul nu se scrie a doua oară); tokenizerul w2 inclus în antet — același ca la #513 |
| fișierul | `kronos_651_q8_0.kgr` (KGR1, matricile Q8_0, restul F32): 292 de tensori, 98 Q8_0 și 194 F32 |
| mărimea | **206.898.464 octeți** (197,3 MiB) |
| SHA-256 | `2edf75ac12eedb54bd2eace55d82bf5c14cc3240e11c0fca40263d3e65ea0bf2` (și în `kronos_651_q8_0.kgr.sha256`, același format ca la #513) |
| locul pe workstation | `C:\Kronos\cyberspace\lucru\export\kronos_651_q8_0.kgr` (nu în Git); suma alături în `kronos_651_q8_0.kgr.sha256`, vectorii de control în `kronos_651_q8_0.vectori.json` |
| Release | nu e nevoie (C-150): centrul de comandă copiază fișierul pe stick, verificând suma |

## Ce diferă față de #513

Verificat cap la cap pe cele două fișiere (`lucru/cascada/S128_proba/fata_de_513.json`):

- **cheile din antet**: aceleași 11 chei (`arhitectura`, `cap_legat`, `context`, `fel`, `ln_eps`, `n_capete`, `n_emb`,
  `n_straturi`, `sursa`, `tokenizer.bpe`, `vocabular`); diferă doar valorile `n_straturi` (12 → **24**) și `sursa`
  (`#513 w2_romana_r1` → `#651 w2_mare_24zc`, aceeași lungime);
- **tokenizerul**: identic, caracter cu caracter (214.851 de caractere, SHA-256 al textului `99ed5a5f…a16df` la ambele);
- **felurile de tensori**: aceleași nume (fără numărul stratului), cu același fel pe fiecare nume și aceleași forme pe
  strat: `emb_token` 16.384 × 768 Q8_0, `emb_pozitie` 512 × 768 Q8_0, `in_proj_weight` 2.304 × 768 Q8_0,
  `out_proj.weight` 768 × 768 Q8_0, `mlp.0.weight` 3.072 × 768 Q8_0, `mlp.2.weight` 768 × 3.072 Q8_0, deplasările și
  LayerNorm F32; doar sunt 24 de straturi în loc de 12 (292 de tensori în loc de 148);
- **câmpuri noi în format**: niciunul. Deci: **nimic în afară de mărimi** (numărul de straturi și, de aici, mărimea
  fișierului și numărul de tensori). Un motor care citește #513 citește și #651, dacă nu are 12 straturi scris fix.

## Testul pe hardware

Motorul OS, pe acest fișier, trebuie să dea **exact** aceleași simboluri (codare + 5 simboluri greedy, argmax fără
întâmplare). Așa au ieșit din `unelte/inferenta_bruta.py` (Python + numpy, Q8_0 desfăcut la încărcare); PyTorch (pe
procesor) pe aceleași greutăți Q8_0 desfăcute dă aceleași simboluri greedy și același argmax pe toate pozițiile, cu
diferența maximă pe logit-uri **3,1e-5** (la #513: 1,4e-4):

| text | simbolurile textului | primele 5 generate (#651) | textul generat (#651) | #513, pentru comparație |
|---|---|---|---|---|
| `Ana are mere.` | 65, 1988, 1585, 2717, 46 | 1471, 1988, 4397, 1547, 3666 | `" Ana stă la et"` | 2233, 1585, 32, 475, 50 (`" Acum are 1192"`) |
| `Capitala României este` | 7132, 1373, 2710, 5734, 1744 | 8369, 4043, 46, 10, 10 | `" orașul București.\n\n"` | 8369, 1497, 4444, 6882, 44 (`" orașul Baia Mare,"`) |
| `def suma(a, b):` | 2082, 15746, 40, 97, 44, 1376, 1754 | 1510, 1947, 5017, 40, 97 | `"\n    return sum(a"` | 1510, 1947, 1358, 1778, 1376 (`"\n    return a * b"`) |

Marjele dintre primul și al doilea logit:

| text | la ultima poziție a textului | cea mai mică pe pozițiile textului | cea mai mică pe pașii greedy | #513 (greedy) |
|---|---|---|---|---|
| `Ana are mere.` | 0,360 | 0,051 | **0,360** | 0,166 |
| `Capitala României este` | 0,499 | 0,499 | **0,349** | 0,172 |
| `def suma(a, b):` | 1,880 | 0,309 | **0,601** | 0,095 |

Cea mai mică marjă de oriunde e 0,051 (o poziție din textul „Ana are mere.”, nu un pas greedy), de 10 ori peste 0,005:
un motor cu abateri de ordinul 1e-3 dă aceleași simboluri. Pe pașii greedy marjele sunt mai mari decât la #513.

Toleranța pe logit-uri pentru modelul mare rămâne întrebarea deschisă către Adrian din S37 (vezi `README.md`).

## Rezervele

`MODEL.md` (#513, cu rezervele #477 și #459) rămâne neschimbat. Fișierele `kronos_513_q8_0.kgr`, `kronos_477_q8_0.kgr`,
`kronos_459_q8_0.kgr` și sumele lor au rămas identice (SHA-256 înainte = după, verificat în S128).
