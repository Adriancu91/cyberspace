# S7 (noaptea 11): pornită de mână la 20:46, cu Adrian de față

*Scris de executant (Claude Code, workstation), 20 octombrie 2026, 20:50. Rolul executantului făcut de mână, la cererea lui Adrian.*

## Pe scurt

- Am mutat fișierele rămase de la prima pornire, cu aprobarea lui Adrian. Nu le-am șters.
- Toate verificările au trecut. S7 e `in_lucru` (commit `3e3a82a`). Antrenarea a pornit la **20:46:55** (procesul 23960) și scrie în jurnal.
- **Id-ul experimentului nu există încă.** Primul apare după prima oră de antrenare, pe la 21:50. Îl trece în pre-înregistrare sarcina de dimineață sau executantul, odată cu examenele.
- Pasul R (reparația `cascada.py` cu `--din-nou`) **nu l-am făcut**. Rămâne în coadă pentru ziua de mâine.

## Ce am mutat

| înainte | după |
|---|---|
| `lucru/cascada/S7.json` (prima pornire, 19:29:17–19:29:28, cod 0) | `lucru/cascada/S7_prima_1929.json` |
| `lucru/cascada/S7.log` | `lucru/cascada/S7_prima_1929.log` |

Am făcut mutarea cu `Move-Item` în PowerShell, cu aprobarea lui Adrian din conversație.

## Ce am verificat (20:46, înainte de pornire)

- **Placa:** 712 MB folosiți, 29 °C, 2% încărcare. Nu rula niciun proces greu, iar `cascada.py stare` spune „liber: true”.
- **Fereastra:** „noapte”, cu 613 minute rămase.
- **`lucru/w2_conv_text_v2/`:** nu exista, deci `--porneste-din 401` se aplică.
- **`config/conv_w2_text_v2.toml`:** rândul 20 e `nume = "w2_conv_text_v2"`.
- **Pre-înregistrarea** `docs/preinregistrari/2026-10-20_noaptea11_formulari.md` are secțiunea „Notă înainte de rularea reparată (20 octombrie, 20:35)” (rândul 99).
- **`cascada.py`:** caută doar `lucru/cascada/S7.json`, deci fișierul mutat nu mai blochează pornirea. În `stare`, prima pornire apare încă în listă, cu `merge: false`, pentru că se citește și fișierul redenumit. Nu deranjează.

## Pornirea

```
python unelte/cascada.py porneste S7 -- .venv/Scripts/python.exe -X utf8 unelte/antrenare_lunga.py --config config/conv_w2_text_v2.toml --ore 3 --porneste-din 401
```

Jurnalul `lucru/cascada/S7.log` la 20:48:57, după 2 minute:

```
[2026-10-20 20:46:56] Pornesc: .venv/Scripts/python.exe -X utf8 unelte/antrenare_lunga.py --config config/conv_w2_text_v2.toml --ore 3 --porneste-din 401
Pornesc din modelul experimentului #401 (linia „w2_conv_text”, ora 3, val_bpb 0.4357): optimizatorul și rata pornesc din nou. Până la primul experiment păstrat al liniei, regula 4 o judecă față de el.
   Urmărirea plăcii: C:\Kronos\cyberspace\lucru\w2_conv_text_v2\placa_20261020_2047.csv (pornită și oprită odată cu antrenarea).
Antrenarea lungă: orele 1–3, rețeta 12×768, context 512, lot 12, rata 5e-05 constantă, după încălzire (linia „w2_conv_text_v2”).
   Fiecare lot: 5% bucăți din date/fapte/povesti.txt, restul din textul de antrenare.
```

- **Placa:** 6.225 MB, 100%, 55 °C, sub limita de ~7 GB.
- **`cascada.py sarcina S7`:** `merge: true`.
- **Durata:** 3 ore de antrenare, cam până la 23:50. Urmează examenele, cam o oră.

## Ce n-am atins

- `kronos/`, examenul, paznicul, configurările și pre-înregistrarea.
- **Pasul R din S7** (reparația `--din-nou`): l-am lăsat neatins în coadă. În `plan/coada.md` am notat „S7 pornită de mână la 20:47, fără `--din-nou`; pasul R rămâne pentru ziua de mâine”.
  - Supraveghetorul n-a pus o sarcină S9 separată, ci a scris reparația ca pas în S7.
  - Ora reală a pornirii e 20:46:55. În coadă am scris 20:47, înainte de pornire.
- **Examenele și raportul de dimineață** (pașii 2–4 din S7) rămân pentru sarcina de dimineață, cum ai cerut.

## Testele

Nu s-a schimbat cod. S-a schimbat doar `plan/coada.md`, deci testele nu erau necesare. Ultima rulare completă a trecut (pasul de la 20:33).

## Ce aștept

Nimic acum. Verdictul vine dimineață, din raportul sarcinii de dimineață, cu pragurile din pre-înregistrare.
