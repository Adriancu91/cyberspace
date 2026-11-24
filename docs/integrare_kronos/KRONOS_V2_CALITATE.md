# Kronos v2 — coloanele „calitate” din fișa „Kronos croit pe placă” (S136, C-164)

Scris de executant, 24 nov 2026 (21:30–22:00). Doar citit cod și documente; nicio antrenare, nimic pe placă, nimic schimbat
în `kronos/`, `module/` sau `config/`. Partea „placă” e a lui Cyber-GPU (`plan/hub_KRONOS_V2_FISA.md`, copia din hub de la 20:15).

Semne: **SURSĂ** = scris într-o lucrare / un proiect public (numele e dat); **DEDUS** = socoteala sau părerea mea, nemăsurată;
**KRONOS** = citit din codul sau rapoartele noastre.

## 1. Ce are Kronos azi (#513, și la fel #651 / #736 — doar mai multe straturi)

Toate modelele GPT ale lui Kronos (#513 = `module/model_muon.py:ModelGPTConversatieMuon` → `model_conversatie` → `model_continuu`
→ `model_gpt.ModelGPT`; la fel `module/model_trepte.py`) construiesc aceeași rețea, `_GPT` din `module/model_gpt.py` (KRONOS):

| Piesă | Unde (fișier:rând) | Ce e exact |
|---|---|---|
| Activarea | `module/model_gpt.py:78` | `nn.GELU()` cu setarea implicită = **GELU exact (cu erf)**, nu aproximarea cu tanh. La fel în export (`docs/format_greutati.md:134`) și în `unelte/inferenta_bruta.py:46`. |
| Normele | `module/model_gpt.py:74`, `:76`, `:108` | `nn.LayerNorm(n_emb)` — **cu medie, cu γ (weight) și cu β (bias)**, eps 1e-5. Două pe strat (înainte de atenție și înainte de MLP) + una la final. |
| Deplasări (bias) în înmulțiri | `:75` și `:78` | Atenția: `nn.MultiheadAttention` cu `bias=True` implicit → `in_proj_bias` [3E] și `out_proj.bias` [E]. MLP: `nn.Linear` cu bias implicit → `mlp.0.bias` [4E], `mlp.2.bias` [E]. **4 deplasări pe strat** (cele 48 numărate de Cyber-GPU). |
| Capul | `:109–110` | `nn.Linear(n_emb, vocab, bias=False)` **legat** de `emb_token.weight` (aceleași greutăți la intrare și ieșire). |
| Lățimile | — | E = 768, 3E, 4E, V = 16.384, T = 512, cap de atenție 64 — deja ÷ 64 și ÷ 128. |

Câte greutăți sunt în joc la #513 (DEDUS, socotit din mărimi): deplasările din înmulțiri 12 × 9 × 768 = **82.944**; β ale normelor
**19.200**; γ ale normelor **19.200** — împreună ~121 mii din ~98 milioane (**0,12 %**). Deci la toți candidații de mai jos în afară de
ReLU², ce se schimbă e foarte puțin din rețea; riscul pentru calitate e mic din principiu, iar câștigul de pe placă vine din programe,
nu din greutăți.

Istoria Kronos: în rapoartele din `docs/rapoarte/` **nu există nicio probă** cu ReLU², RMSNorm, fără deplasări sau capul dezlegat
(căutat după „relu”, „rmsnorm”, „gelu”, „deplasări”). Tot ce știm despre aceste piese vine din lucrări publice (KRONOS).

## 2. Coloanele „calitate” — candidat cu candidat

| Candidat | Riscul pentru calitate (Kronos) | Probă C-163 (Kronos) |
|---|---|---|
| **ReLU²** în loc de GELU | **mic, poate chiar câștig.** SURSĂ: *Primer* (So et al., 2021, arXiv 2109.08668) — ReLU² e una din cele două schimbări care aduc cel mai mult la modelele de limbaj, la același calcul; *modded-nanogpt* (Keller Jordan, 2024) îl folosește în recordurile de viteză pe GPT-2 mic. *ReLU Strikes Back* (Mirzadeh et al., 2023, arXiv 2310.04564): ReLU simplu pierde foarte puțin față de GELU. DEDUS: e singura piesă care schimbă forma rețelei (activarea are 4E = 3.072 de valori pe poziție); la un model de 98 M de la zero mă aștept la ±0,01 bpb. Neverificat la română. | intră în (2) |
| **Fără deplasări** (bias) | **foarte mic.** SURSĂ: *PaLM* (Chowdhery et al., 2022, arXiv 2204.02311) — fără deplasări în înmulțiri și în norme, „mai stabil la modele mari”; *LLaMA* (Touvron et al., 2023, arXiv 2302.13971) la fel; *nanoGPT* (Karpathy) are `bias=False` cu nota „un pic mai bun și mai rapid”. DEDUS: 0,12 % din greutăți; la noi β de la norme și deplasările MLP pot fi înlocuite de rest. | intră în (2) |
| **RMS cu γ** în loc de LayerNorm | **foarte mic.** SURSĂ: *RMSNorm* (Zhang & Sennrich, 2019, arXiv 1910.07467) — aceeași calitate ca LayerNorm pe mai multe sarcini; folosit în *T5*, *LLaMA* și aproape toate modelele mari de azi. | intră în (2) |
| **RMS fără γ** | **mic, dar cu o capcană la noi.** SURSĂ: *modded-nanogpt* folosește `F.rms_norm` fără γ peste tot; *OLMo* (Groeneveld et al., 2024, arXiv 2402.00838) a antrenat 1B/7B cu normă fără greutăți. DEDUS — capcana: la ei **capul nu e legat** de încorporări (și modded-nanogpt mai taie logiturile cu „soft-cap”). La Kronos capul e legat, deci după norma finală fără γ mărimea logiturilor ar depinde doar de mărimea încorporărilor — nimic nu mai poate „ascuți” singur distribuția. Propun: **fără γ în straturi, dar γ păstrat la norma finală** (768 de valori; Cyber-GPU poate spune cât costă o singură sumă pe coloane). | (3) = (2) + fără γ în straturi |
| **Lățimi ÷ 64** | — (deja așa) | — |
| **Capul** — dezlegat | **ar putea câștiga ceva, cu cost.** SURSĂ: *Press & Wolf* (2017, arXiv 1608.05859) — legarea ajută modelele mici (mai puțini parametri, perplexitate mai bună); GPT-2 îl leagă; modded-nanogpt îl dezleagă. DEDUS: +12,6 M parametri (+13 % la #513), ~200 MB în plus cu AdamW (încape în 7 GB, de verificat la proba de 3 minute); la o oră de la zero câștigul e nesigur. Nu e pe lista vitezei (același calcul), deci prioritate mică. | (4), doar dacă (2)/(3) nu pierd |
| **Capul** — vocabular 8.192 | **necunoscut + cost mare.** DEDUS: un vocabular mai mic face mai multe simboluri pe același text (pe cod, S55 a văzut cât contează tokenizerul: +22 % octeți/simbol față de w2), deci o parte din cele −6,5 % înmulțiri se pierde pe secvențe mai lungi. bpb rămâne comparabil (e pe octet), dar **toate datele trebuie re-tokenizate** și niciun model vechi nu mai poate fi pornit. | **cere „da” separat al lui Adrian** — vezi §5 |

## 3. Ce ar însemna pentru Kronos (doar descris, nimic făcut)

- **Un modul nou** (ca `module/model_trepte.py`), de exemplu `module/model_v2.py`, cu `MANIFEST` (port `model`) și setări noi:
  `activare = "gelu" | "relu2"`, `norma = "layer" | "rms"`, `gamma = true | false`, `gamma_final = true | false`, `deplasari = true | false`,
  `cap_legat = true | false`. Cu toate setările „ca azi” trebuie să dea **exact** rețeaua de azi.
- **Testele** (ca la S135): (a) toate setările „ca azi” → aceleași ieșiri ca `_GPT` pe aceleași greutăți (F32, procesor); (b) ReLU² și
  RMS verificate pe un exemplu mic calculat de mână; (c) gradientul față de diferențe finite pe 3–5 elemente; (d) modulul în lista
  `MODULE` din `teste_contracte/test_contracte.py` + fișa din `unelte/module_toml.py`; (e) unealta laboratorului primește
  `--arhitectura` (sau `--reteta 2|3|4`), restul rețetei neschimbat.
- **Exportul KGR1** (`docs/format_greutati.md`, `unelte/exporta_greutati.py`, `unelte/inferenta_bruta.py`, `module/inferenta_kgr1.py`):
  chei noi în antet (`activare`, `norma`, `gamma`, `deplasari`, `cap_legat`), iar tensorii lipsă (`*.bias`, `ln*.weight`) pur și simplu
  nu se scriu. Cititorii vechi trebuie să refuze un fișier cu chei necunoscute (nu să-l citească greșit). Motorul brut primește
  `relu2(x) = max(x,0)²` și `rms_norm(x) = x / √(medie(x²) + eps) · γ`. DEDUS: ~1 zi de lucru cu testele; OS-ul are deja oracolele
  (`gpu_compute::v2`).

## 4. Probele de o oră din laborator (C-163) care ar verifica

Aceeași rețetă ca S135 (0): de la zero, sămânța 1163, doar W2, AdamW, bf16, vârf 6e-4, încălzire 3 min, răcire în ultimele 15, 60 de
minute pe ceas; aceleași examene (română curat = judecătorul, `examen_bpb` = martorul, R1). Singura diferență = arhitectura.

| Proba | Ce schimbă față de (0) | Cost placă (DEDUS, ca la S135) | De ce |
|---|---|---|---|
| **(0′)** | nimic — doar sămânța 1164 | ~1 h 40 min | **Zgomotul.** Pragul „câștigă” e 0,010 bpb; nu știm cât diferă două rulări identice cu altă sămânță. Fără (0′) un ±0,010 poate fi întâmplare. O singură dată, folosește și la S135. |
| **(2)** | ReLU² + fără deplasări + RMS cu γ, toate deodată | ~1 h 40 min | „toate piesele ieftine”: dacă (2) e LA FEL sau CÂȘTIGĂ, le luăm împreună; dacă PIERDE, le despart (câte o probă). |
| **(3)** | (2) + fără γ în straturi (γ păstrat la final) | ~1 h 40 min | candidatul care dă cel mai mult pe placă (−5,0 % împreună). |
| **(4)** | cel mai bun dintre (0)/(2)/(3) + capul dezlegat | ~1 h 40 min (+ ~200 MB) | doar dacă vrem; nu schimbă viteza. |

Pragurile ar fi cele din S135 (CÂȘTIGĂ ≤ −0,010 română și `examen_bpb` ≤ +0,005; LA FEL < 0,010; PIERDE ≥ +0,010), plus (0′) ca să
știm dacă 0,010 e peste zgomot. Total: 3 probe obligatorii ((0′), (2), (3)) ≈ **5 h de placă**, adică o zi din fereastra 07:00–23:00.

O atenție la comparația „la aceeași oră de ceas” (DEDUS): în PyTorch pe Windows, ReLU² și lipsa deplasărilor aproape nu grăbesc pasul
(câștigul e în programele OS-ului). Deci în laborator (2)/(3) vor face cam **același număr de pași** ca (0) — proba măsoară
**calitatea la același număr de pași**, ceea ce e exact întrebarea pentru fișă. În raport scriu și pașii, ca să se vadă.

## 5. Vocabularul 8.192 — doar costul (cere „da”-ul lui Adrian)

DEDUS: tokenizer nou (o unealtă ca la S55, unde tokenizerul de cod a luat ~18 min de procesor), re-tokenizarea W2 (câteva ore de procesor, zeci de GB pe disc — C: e
strâmt), linie nouă de modele de la zero (nimic din #513 / #651 nu se poate refolosi: încorporările și capul depind de vocabular),
toate examenele pe bpb rămân comparabile, dar R1/chat trebuie re-verificate. Câștigul pe placă: −6,5 % din înmulțiri, din care o parte
se pierde pe secvențe mai lungi. Nu propun asta acum.

## 6. Recomandarea (pe calitate)

Riscul pentru calitate e **mic la toate piesele ieftine** (ReLU², fără deplasări, RMS cu γ; toate folosite de modele publice bune),
iar la **RMS fără γ** doar dacă păstrăm γ la norma finală (capul nostru e legat). Recomand probele **(0′), (2), (3)** în laborator
după S135 (~5 h de placă), cu modulul nou `module/model_v2.py`; capul dezlegat și vocabularul 8.192 rămân pe mai târziu.
