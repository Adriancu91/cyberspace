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
doua oară), `tokenizer.bpe` (tokenizerul ca text JSON: `imbinari`, `speciale`, `versiune`, `reguli`; vezi
`module/tokenizer_bpe.py`).

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
