# Formatul KGR1: greutățile unui model Kronos, fără PyTorch (S32, comanda C-21.3)

Contractul pentru motorul Cyber Universe OS. Scrie: `unelte/exporta_greutati.py`; citește și rulează (Python + numpy):
`unelte/inferenta_bruta.py`. Ideea vine de la GGUF, dar codul și formatul sunt ale noastre (nu e compatibil cu GGUF).

## Fișierul

Totul e **little-endian**. `text` = `u64` lungimea în octeți + octeții UTF-8 (fără 0 la capăt).

| bucata | ce conține |
|---|---|
| antet | `"KGR1"` (4 octeți), `u32` versiunea (= 1), `u64` câte chei-valori, `u64` câți tensori |
| chei-valori | pentru fiecare: `text` cheia, `u32` felul (1 = `i64`, 2 = `f64`, 3 = `text`), valoarea |
| lista tensorilor | pentru fiecare: `text` numele, `u32` câte dimensiuni, `u64` × dimensiuni (ordinea numpy: ultima variază cel mai repede), `u32` felul (0 = F32, 1 = Q8_0), `u64` locul (de la începutul zonei de date) |
| umplutură | zerouri până la un multiplu de 32 |
| zona de date | tensorii la rând, fiecare urmat de zerouri până la un multiplu de 32 (deci fiecare începe aliniat la 32) |

**F32**: numerele `f32`, rând după rând.
**Q8_0** (doar tensori cu 2 dimensiuni, coloanele multiplu de 32): pe fiecare rând, pe fiecare bloc de 32 de coloane,
36 de octeți = scara `f32` + 32 de numere `i8`. Valoarea = `scara × număr`. La export: `scara = max|x| / 127`,
`număr = round(x / scara)` (blocul tot 0 → scara 0).

## Cheile

`arhitectura` = `kronos_gpt`, `fel` (`f32` / `q8_0`), `sursa` (ex. `#415 w2_conv_text_v3`), `n_straturi`, `n_capete`,
`n_emb`, `context`, `vocabular`, `ln_eps` (1e-5), `cap_legat` (1: capul folosește `emb_token.weight`, nu se scrie a
doua oară), `tokenizer.bpe` (tokenizerul ca text JSON: `imbinari`, `speciale`, `versiune`, `reguli`; descris complet
mai jos, la „Tokenizerul”).

## Tokenizerul (`tokenizer.bpe`)

Descrierea e completă: un motor poate scrie tokenizerul doar din ea. Exemplele sunt pe tokenizerul liniei w2
(`date/ws/bpe_16384.json`, regulile `ws`, 16.384 de simboluri), cel din fișierele `vectori/` și din modelele exportate.

### Cum stă în fișier

Valoarea cheii `tokenizer.bpe` e un `text` KGR1 (u64 lungimea + octeții UTF-8) care conține un obiect JSON:

| câmp | ce e |
|---|---|
| `versiune` | 2 pentru regulile `ws` (1 = regulile vechi `gpt2`, fără câmpul `reguli`) |
| `reguli` | `"ws"` (lipsește la regulile `gpt2`) |
| `imbinari` | lista lipirilor, în ordine: `[[a, b], …]`, numere întregi. Lipirea cu poziția `k` (de la 0) face simbolul **256 + k** din simbolurile `a` și `b` |
| `speciale` | lista simbolurilor speciale, ca text: `["<|endoftext|>"]` |

Ordinea câmpurilor din JSON nu contează. Un fișier cu alt `versiune`/`reguli` decât perechile (1, `gpt2`) și (2, `ws`)
trebuie refuzat.

### Vocabularul

- simbolurile **0–255** sunt octeții 0–255 (orice text se poate scrie, nu există simbol „necunoscut”);
- simbolul **256 + k** = octeții lui `a` urmați de octeții lui `b`, unde `[a, b] = imbinari[k]` (`a`, `b` < 256 + k);
- simbolurile speciale vin după lipiri: al `j`-lea special (de la 0) are numărul **256 + len(imbinari) + j**; octeții lui
  sunt textul lui în UTF-8;
- mărimea vocabularului = 256 + len(imbinari) + len(speciale) (la w2: 256 + 16.127 + 1 = 16.384; `<|endoftext|>` = 16.383).
  Trebuie să fie egală cu cheia `vocabular`.

La regulile `ws`, primele 1.100 de lipiri sunt fixe (un fișier `ws` care nu începe cu ele trebuie refuzat):
lipirile 0–99 sunt perechile de cifre ASCII `[ord(x), ord(y)]` pentru „00”, „01”, …, „99” (deci „xy” = simbolul
256 + 10·x + y), iar lipirile 100–1.099 sunt `[256 + k, ord(c)]` pentru k = 0…99, c = „0”…„9” (deci „xyz” =
simbolul 356 + 100·x + 10·y + z).

### Codarea unui text

1. **Speciale.** Textul se taie în jurul aparițiilor exacte ale textelor speciale (oriunde, chiar în mijlocul unui
   cuvânt; dacă sunt mai multe, cel mai lung se încearcă primul, de la stânga la dreapta). Fiecare apariție dă direct
   numărul ei. Bucățile dintre ele trec prin pașii 2–4, separat.
2. **Pre-tokenizarea** (tăierea în bucăți; bucățile nu se lipesc niciodată între ele). De la începutul bucății de text,
   repetat: la poziția curentă se încearcă, **în ordinea de mai jos**, prima variantă care se potrivește (nu cea mai
   lungă), cu potrivirea ei cea mai lungă, și se trece după ea. Clasele de litere (exact ca Python 3, verificat pe tot
   Unicode-ul):
   - *literă* = un caracter cu `isalnum()` adevărat, care nu e cifră zecimală (`isdecimal()`, categoria Unicode Nd)
     și nu e `_`. Deci literele din toate alfabetele, cu diacriticele **precompuse** (ă â î ș ț, și ş ţ cu sedilă),
     dar și semne numerice ca „½” sau „²”. Un semn diacritic **combinat** separat (ex. U+0301) NU e literă;
   - *cifră* (regulile `ws`) = un caracter cu `isdecimal()` adevărat (orice alfabet; la `gpt2` la fel);
   - *spațiu* = un caracter cu `isspace()` adevărat (spațiu, \t, \n, \r, \v, \f, \x1c–\x1f, \x85, U+00A0 etc.);
   - *semn* = orice caracter care nu e spațiu, nici literă, nici cifră; `_` e tot *semn*.

   | ordinea | varianta (regulile `ws`) | expresia |
   |---|---|---|
   | 1 | apostroful ASCII `'` urmat de `s`, `d`, `m`, `t`, `ll`, `ve` sau `re` (doar litere mici) | `'(?:[sdmt]\|ll\|ve\|re)` |
   | 2 | un spațiu obișnuit (U+0020) opțional + una sau mai multe *litere* | ` ?[^\W\d_]+` |
   | 3 | 1–3 *cifre* (fără spațiul dinainte; „1234” = „123” + „4”) | `\d{1,3}` |
   | 4 | un spațiu obișnuit opțional + unul sau mai multe *semne* | ` ?(?:[^\s\w]\|_)+` |
   | 5 | șirul de *spații* care **nu** e urmat de un ne-spațiu: dacă după șir vine ceva, ultimul spațiu rămâne pentru bucata următoare | `\s+(?!\S)` |
   | 6 | orice șir de *spații* (prinde spațiul rămas, ex. înaintea unei cifre) | `\s+` |

   Expresia întreagă (sintaxa `re` din Python): `'(?:[sdmt]|ll|ve|re)| ?[^\W\d_]+|\d{1,3}| ?(?:[^\s\w]|_)+|\s+(?!\S)|\s+`.
   La regulile `gpt2`, varianta 3 e ` ?\d+` (spațiul opțional și oricâte cifre).

   Exemple: „x  = 1234;\n\n  y” → `x` · ` ` · ` =` · ` ` · `123` · `4` · `;` · `\n\n ` · ` y`;
   „l'are don't” → `l` · `'` · `are` · ` don` · `'t`; „á” scris ca a + U+0301 → `a` · `◌́` (semn).
3. **Grupele de cifre ASCII** (doar regulile `ws`): o bucată formată numai din 1–3 cifre ASCII ia direct simbolul ei,
   fără lipiri: o cifră → octetul ei (48–57), două „xy” → 256 + 10·x + y, trei „xyz” → 356 + 100·x + 10·y + z
   (deci „07” → 263, „991” → 1.347). Asta e obligatoriu: lipirile de la pasul 4 ar da, de ex., „991” = „9” + „91”.
   Cifrele din alte alfabete merg prin pasul 4, ca orice altă bucată.
4. **Lipirile (BPE).** Bucata se scrie în octeți UTF-8; fiecare octet e un simbol. Cât timp sunt cel puțin 2 simboluri:
   dintre toate perechile de vecini, se alege perechea care are lipirea cu **poziția cea mai mică** în `imbinari`
   (dacă perechea apare de mai multe ori, e aceeași pereche); dacă nicio pereche nu e în listă, gata. Altfel, de la
   stânga la dreapta, fiecare apariție a perechii (fără suprapuneri: simbolurile a, a, a cu perechea (a, a) → aa, a) se
   înlocuiește cu simbolul 256 + poziția, și se reia.
5. Simbolurile tuturor bucăților, puse la rând, sunt codarea textului.

### Decodarea

Se pun la rând octeții fiecărui simbol (tabelul de mai sus) și se citesc ca UTF-8. Octeții care nu formează UTF-8
valid se înlocuiesc cu U+FFFD, după regula „subpartea maximală” (Unicode, cap. 3; așa fac Python
`decode(errors="replace")` și Rust `String::from_utf8_lossy`): de ex. octeții C3 41 E2 82 → „�A�”. Un
singur simbol poate fi o jumătate de literă (ex. „ș” = C8 99 poate fi în două simboluri), deci un motor care scrie
textul pe bucăți trebuie să țină octeții rămași până se completează litera.

### Cele 3 texte de control (tokenizerul w2)

| text | bucățile | simbolurile | octeții fiecărui simbol |
|---|---|---|---|
| `Ana are mere.` | `Ana` · ` are` · ` mere` · `.` | 65, 1988, 1585, 2717, 46 | `A` · `na` · ` are` · ` mere` · `.` |
| `Capitala României este` | `Capitala` · ` României` · ` este` | 7132, 1373, 2710, 5734, 1744 | `Cap` · `it` · `ala` · ` României` · ` este` |
| `def suma(a, b):` | `def` · ` suma` · `(` · `a` · `,` · ` b` · `):` | 2082, 15746, 40, 97, 44, 1376, 1754 | `def` · ` suma` · `(` · `a` · `,` · ` b` · `):` |

Și: `<|endoftext|>Ana` → 16383, 65, 1988; `991 07` → 1347, 32, 263.

## Tensorii (numele din PyTorch) și calculul

`E` = n_emb, `H` = n_capete, `D` = E / H. În fișierul `q8_0`, toți tensorii cu 2 dimensiuni sunt Q8_0; restul F32.

- `emb_token.weight` [vocabular, E], `emb_pozitie.weight` [context, E]: `x = emb_token[simbol] + emb_pozitie[poziție]`.
- pentru fiecare strat `i` (prefixul `straturi.i.`):
  - `h = LayerNorm(x; ln1.weight, ln1.bias)`;
  - `qkv = h · atentie.in_proj_weightᵀ + atentie.in_proj_bias` ([3E, E] și [3E]; rândurile sunt q, apoi k, apoi v);
    capul `j` = coloanele `j·D … j·D + D − 1` din q, k, v;
  - `scor = q·kᵀ / √D`, cu poziția `t` care vede doar pozițiile `0 … t`; softmax; `· v`; capetele puse la loc la rând;
  - `x = x + (… · atentie.out_proj.weightᵀ + atentie.out_proj.bias)`;
  - `h = LayerNorm(x; ln2.weight, ln2.bias)`; `x = x + mlp.2.weight · GELU(mlp.0.weight · h + mlp.0.bias) + mlp.2.bias`
    (`mlp.0.weight` [4E, E], `mlp.2.weight` [E, 4E]; GELU exact, cu erf).
- la final: `logits = LayerNorm(x; ln.weight, ln.bias) · emb_tokenᵀ`.

LayerNorm: `(x − medie) / √(varianța + ln_eps) · weight + bias` (varianța împărțită la E).

## Starea de control

`teste/test_inferenta_bruta.py`: un GPT mic, cu greutăți la întâmplare, iese din motor la fel ca din PyTorch, strat cu
strat (< 1e-5), la logits (< 1e-4), la biți și la completare. Pe #415: raportul S32.
