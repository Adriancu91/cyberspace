# S104 — Proba pe placă a datelor pe bucăți: DA

*Scris de executant, 12 noiembrie 2026, 09:36. Sarcina S104 din `plan/coada.md` (C-110, „da”-ul lui Adrian din 12 nov 06:49;
pașii scriși de supraveghetor 12 nov 06:55).*

## Pe scurt

Modelul adevărat de 24 de straturi a fost antrenat câte 300 de pași de trei ori, din aceeași stare (#554): de două ori cu
datele vechi (textul întreg în memorie) și o dată cu datele pe bucăți. **Toate cele trei rulări au primit exact aceleași
loturi, iar pierderile cu bucățile diferă de cele cu datele vechi cât diferă placa de ea însăși de la o rulare la alta.**
După pragul scris dinainte, verdictul e **DA**.

Cu bucățile, antrenarea pornește cu **2.156 MB de memorie în loc de 41.709 MB** și merge la aceeași viteză.

## Ce a rulat și cât

- Comanda (prin cascadă): `python unelte/proba_placa.py tot --iesire lucru/proba_placa/s104`.
- Pornită 08:17:03, încheiată 09:17:31 — **60 de minute și 27 de secunde**, cod 0. Limita sarcinii era 2 ore.
- Trei rulări una după alta, fiecare în proces nou, fiecare 7.200 de loturi = **300 de pași de optimizare** (24 de loturi
  adunate pe pas), sămânța 0, pornite de la pasul 231.488:
  - **V1** = datele vechi (`config/proba_placa_vechi.toml`), 20 min 11 s;
  - **V2** = datele vechi încă o dată — arată cât diferă placa de la o rulare la alta, 20 min 14 s;
  - **B** = datele pe bucăți (`config/proba_placa_bucati.toml`), 19 min 45 s.
- Rețeta e cea de la S100: Muon (rata 0,0001), AdamW 5e-6, lot 4, context 512, recalculul activărilor pe 24 de straturi.
  Rata a fost constantă în toate rulările (`rata_la_final` 5e-6 la toate trei).
- Nu e un experiment Kronos: nimic în jurnalul lui Kronos, niciun examen, niciun model păstrat.
- Înainte de pornire: placa goală 431 MB / 29 °C, C: 39,4 GB liberi, testele verzi.
- Înainte de proba adevărată am făcut o probă „de fum” de 1 pas cu B (`lucru/cascada/S104_proba/fum.py`), doar ca să văd că
  unealta pornește; nu intră în rezultat.

## Cifrele

### Pierderea pe pașii de optimizare

| pasul | V1 (vechi) | V2 (vechi, a doua oară) | B (bucăți) | V2 − V1 | B − V1 |
|---|---|---|---|---|---|
| 1 | 1,3649532 | 1,3649532 | 1,3649532 | 0 | 0 |
| 50 | 1,4319511 | 1,4320763 | 1,4321398 | +0,000125 | +0,000189 |
| 100 | 1,3774002 | 1,3773727 | 1,3773411 | −0,000027 | −0,000059 |
| 200 | 1,2597989 | 1,2601021 | 1,2600622 | +0,000303 | +0,000263 |
| 300 | 1,1923089 | 1,1921617 | 1,1920678 | −0,000147 | −0,000241 |

### Diferențele maxime

| comparația | pe cei 300 de pași (verdictul) | la pasul | pe cele 7.200 de loturi (informativ) |
|---|---|---|---|
| V2 față de V1 = zgomotul plăcii | **0,000303** | 200 | 0,002343 |
| B față de V1 | **0,000326** | 109 | 0,002322 |
| V2 față de B | 0,000388 | 136 | 0,002194 |
| pragul = max(2 × zgomotul; 1e-5) | **0,000607** | | 0,004685 |

- B − V1 e de 1,07 ori cât zgomotul plăcii; pragul îngăduia de 2 ori.
- Primul pas la care pierderile nu mai sunt identice bit cu bit: B față de V1 la pasul 2 (lotul 25); V2 față de V1 la
  pasul 6 (lotul 121).
- Greutățile de la sfârșit nu sunt identice bit cu bit între nicio pereche de rulări (nici V1 cu V2).

### Loturile (SHA-256)

| | SHA-256 peste toate cele 7.200 de loturi | rânduri |
|---|---|---|
| V1 | `5868cecc36ef22238b38ce4e16432d461c9b760a85234ada26854317475d9f8e` | conversație 12.960, hrană 1.440, text 14.400 |
| V2 | `5868cecc36ef22238b38ce4e16432d461c9b760a85234ada26854317475d9f8e` | la fel |
| B | `5868cecc36ef22238b38ce4e16432d461c9b760a85234ada26854317475d9f8e` | la fel |

Niciun lot diferit, la nicio pereche.

### Memoria, viteza, placa

| | V1 | V2 | B |
|---|---|---|---|
| RAM de vârf al procesului | 41.709 MB | 41.710 MB | **2.156 MB** |
| secunde până la primul lot | 45,8 | 46,1 | 18,0 |
| loturi pe secundă | 6,201 | 6,184 | 6,186 |
| simboluri pe secundă | 12.698,9 | 12.665,4 | 12.668,7 |
| placa, nvidia-smi max | 3.834 MB | 3.834 MB | 3.834 MB |
| placa, PyTorch rezervat max | 3.212 MB | 3.212 MB | 3.212 MB |
| temperatura max | 61 °C | 61 °C | 61 °C |

- Viteza B e cu 0,24 % sub V1 (V2 e cu 0,26 % sub V1) — adică nicio diferență; așteptarea era sub 5 %.
- RAM B: 2.156 MB, sub așteptarea de 4.000 MB; de 19 ori mai puțin decât V1.
- Paza (6.700 MB / 83 °C) n-a fost atinsă: maximul a fost 3.834 MB și 61 °C.
- B a scris în statistici amprenta datelor: `2b2492ec78569c2b`, 27 de bucăți, 1.341.190.791 de simboluri, SHA-ul șirului
  `560863a9…d4af`, SHA-ul tokenizerului `2fcb9937…b546`.

### Ce a rămas neatins (SHA-256 verificat din nou la 09:35)

| fișier | SHA-256 | față de înainte |
|---|---|---|
| `lucru/w2_mare_24s/gpt.pt` (#554) | `ee39471f…4e5e` | același |
| `lucru/stocare/modele/experiment_554.pt` | `6a6d97d0…23fd` | același |
| `lucru/stocare/modele/experiment_513.pt` | `605c4084…8b2c` | același |
| `lucru/w2_mare/gpt_24.pt` | `d35e3dbe…92cc` | același |
| `lucru/proba_placa/vechi/gpt.pt` (copia de pornire) | `759963dc…6d60` | același, și cel de la S99/S100 |
| `lucru/proba_placa/bucati/gpt.pt` (copia de pornire) | `759963dc…6d60` | același |

`lucru/cache` și `lucru/bucati/w2_amestec_be12` au aceeași listă de fișiere (mărime și dată) înainte și după.
`kronos/`, examenele, paznicul și configurările existente n-au fost atinse. Nimic descărcat, nimic șters.

## Verdictul, strict după pragurile pre-înregistrate

Pragul din `docs/preinregistrari/2026-11-12_proba_bucati_placa.md`: **DA** = SHA-ul loturilor identic V1 = B pe toți pașii
**și** max |B − V1| ≤ max(2 × max |V2 − V1|, 1e-5).

- loturile V1 = B: identice ✓
- max |B − V1| = 0,000326 ≤ 0,000607 ✓

**Verdict: DA.** Citirea informativă lot cu lot dă același răspuns (0,002322 ≤ 0,004685). Pre-înregistrarea e închisă, cu
„Ce a ieșit” și „Verdictul”.

## Ce n-am ghicit bine și ce trebuie știut

- **Placa nu se repetă bit cu bit**: aceeași rulare făcută de două ori (V1 și V2) dă pierderi puțin diferite. Ghicisem
  55 % că se repetă exact. De aceea verdictul nu e „identic bit cu bit”, ci „la fel în limita zgomotului plăcii”. Pe
  procesor (S103) cele două căi au fost identice bit cu bit.
- **B se desparte de V1 mai devreme decât V2 de V1** (pasul 2 față de pasul 6). Mărimea diferențelor e aceeași și loturile
  sunt identice, dar e o singură pereche de rulări, așa că din proba asta nu pot spune dacă e întâmplare. Nu schimbă
  verdictul; o scriu ca să nu se piardă. Dacă supraveghetorul vrea să lămurească: încă o rulare B și încă una V (~20 de
  minute fiecare) ar arăta unde se despart de obicei două rulări.
- Zgomotul a fost mai mic decât ghicisem (0,0003, nu 0,001–0,01), pierderea primului pas mai mică (1,36, nu 1,5–2,5),
  iar memoria plăcii mai mică (3.834 MB, nu 4.450–4.750 MB — proba nu face examene și nu salvează).
- Un DA aici spune că legarea dă aceeași antrenare pe 300 de pași din starea #554. Nu spune nimic despre calitatea vreunui
  model. Modelele de probă nu înlocuiesc nimic.

## Diff-urile celor două configurări față de `conv_w2_mare_24n.toml`

`config/proba_placa_vechi.toml` — doar antetul, plus:

```
-nume = "w2_mare_24n"
+nume = "proba_placa_vechi"
-… cale_stare = "lucru/w2_mare_24n/gpt.pt" …
+… cale_stare = "lucru/proba_placa/vechi/gpt.pt" …
-eticheta = "S100: Muon ×20 din #554, examen de decizie: română, C-88"
+eticheta = "S104: proba pe placă a datelor pe bucăți, rularea cu datele vechi (nu e o linie de model)"
```

`config/proba_placa_bucati.toml` — doar antetul, plus:

```
-nume = "w2_mare_24n"
+nume = "proba_placa_bucati"
-… cale_stare = "lucru/w2_mare_24n/gpt.pt" …
+… cale_stare = "lucru/proba_placa/bucati/gpt.pt" …
-eticheta = "S100: Muon ×20 din #554, examen de decizie: română, C-88"
+eticheta = "S104: proba pe placă a datelor pe bucăți, rularea cu datele pe bucăți (nu e o linie de model)"
-modul = "module.date_amestec:DateAmestec"
-setari = { cale_antrenare = "date/ws/amestec/antrenare.txt", cale_validare = "date/tinystories_r2/validare.txt" }
+modul = "module.date_bucati:DateBucati"
+setari = { director = "lucru/bucati/w2_amestec_be12", cale_validare = "date/tinystories_r2/validare.txt", cale_tokenizer = "date/ws/bpe_16384.json" }
```

Toate celelalte setări (mărimea modelului, ratele, lotul, conversația, hrana, sămânța) sunt aceleași. Diff-urile întregi:
`lucru/cascada/S104_proba/diff_vechi.txt` și `diff_bucati.txt`.

## Testele

`CUDA_VISIBLE_DEVICES=-1 python -m pytest`, după probă (09:28–09:35): **1407 trec, 1 sărit, 0 picate** (6 min 46 s).
Înainte de S104 erau 1390; cele 17 în plus au venit cu S104 (testele uneltei
`unelte/proba_placa.py` și cele două configurări de probă adăugate în listele testelor existente).

## Unde sunt fișierele

- Rezultatul: `lucru/proba_placa/s104/s104.json` (verdictul și comparațiile), `V1.json`, `V2.json`, `B.json` (pierderea
  la fiecare lot), `smi.jsonl` (placa la 5 secunde). Unealta refuză să ruleze a doua oară peste ele.
- Jurnalul rulării: `lucru/cascada/S104.log`.
- Modelele de probă rămân în `lucru/proba_placa/` (nu am șters nimic).
- Discul C: 40 GB liberi (92 % ocupat).

## Ce urmează

- **S105** (deja `aprobat`, la noapte între 19:00 și 23:00): comparația #554 față de #513 pe texte nevăzute și la
  examenul de conversație.
- Nicio antrenare adevărată nu folosește încă datele pe bucăți; asta cere o sarcină care s-o spună anume.

## Ce aștept de la Adrian

Nimic acum.
