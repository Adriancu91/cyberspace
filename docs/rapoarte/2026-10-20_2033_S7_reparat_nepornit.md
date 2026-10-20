# S7 (noaptea 11, rularea reparată): pregătită, dar NEPORNITĂ, din cauza fișierului rămas de la prima pornire

*Scris de executant (Claude Code, workstation), 20 octombrie 2026, 20:33. Rularea automată a cascadei, fără om de față.*

## Pe scurt

- Am văzut „da”-ul lui Adrian (20:27, varianta 2) și am făcut pregătirea: S7 `in_lucru` (commit `bfa40b4`),
  `nume = "w2_conv_text_v2"` în `config/conv_w2_text_v2.toml` și nota din pre-înregistrare (commit `2ccfdce`).
- **Antrenarea NU a pornit.** `unelte/cascada.py porneste S7` refuză: „S7 a mai fost pornită
  (lucru/cascada/S7.json); nu o pornesc a doua oară.” Fișierul e cel de la prima pornire (19:29:17–19:29:28, cod 0,
  care n-a antrenat nimic).
- Am încercat să redenumesc fișierul vechi (`S7.json` → `S7_prima_1929.json`, la fel `S7.log`), fără să-l șterg.
  Permisiunile rulării automate au cerut aprobare pentru `mv`. N-am ocolit pe altă cale.
- **S7 e acum `oprit`.** Nu putea rămâne `in_lucru`: rularea următoare ar fi citit `S7.json` („terminată, cod 0”) și
  ar fi crezut că noaptea s-a terminat.
- Placa e liberă (712 MB, 29 °C), e fereastra de noapte, mai sunt 626 de minute. Noaptea încape încă (~4 ore) dacă
  pornește până pe la 02:30.

## Ce am făcut, pas cu pas

1. `git pull --rebase`: am primit coada cu „da”-ul lui Adrian și notele supraveghetorului de la 20:15 și 20:30.
2. `cascada.py stare`: fereastra „noapte”, placa liberă, niciun proces greu; S4 și S7 (prima pornire) aveau `merge: false`, cod 0.
3. Am verificat că `lucru/w2_conv_text_v2/` **nu există**, deci `--porneste-din 401` s-ar fi aplicat.
4. Am pus `stare: in_lucru` (textul reparației l-am păstrat sub „reparația aprobată:”). Commit și push.
5. Am pus `nume = "w2_conv_text_v2"` în configurare (cu un comentariu) și am adăugat în pre-înregistrare secțiunea
   „Notă înainte de rularea reparată”: rulare reparată pe linia `w2_conv_text_v2`, din #401, aceleași praguri.
   Testele trec (`CUDA_VISIBLE_DEVICES=-1 python -m pytest -q`: toate trec, câteva sărite, ca de obicei). Commit și push.
6. `cascada.py porneste S7 -- ... antrenare_lunga.py --config config/conv_w2_text_v2.toml --ore 3 --porneste-din 401`:
   refuzat, din cauza fișierului vechi.
7. Redenumirea fișierului vechi a cerut aprobare, așa că m-am oprit aici.

## Cifre

Niciuna: nu s-a antrenat nimic, nu există un id nou de experiment și nu s-a rulat niciun examen. Pre-înregistrarea
`2026-10-20_noaptea11_formulari` rămâne **deschisă** (n-am închis-o, pentru că rularea n-a avut loc).

## Ce aștept (2 variante)

**Varianta 1 (cea mai simplă, recomandată), Adrian sau cineva la workstation**, în `C:\Kronos\cyberspace`:

```
move lucru\cascada\S7.json lucru\cascada\S7_prima_1929.json
move lucru\cascada\S7.log lucru\cascada\S7_prima_1929.log
```

Apoi supraveghetorul (sau Adrian) pune S7 din nou pe `aprobat`. Rularea următoare a executantului pornește noaptea cu
comanda pregătită deja; configurarea și pre-înregistrarea nu mai trebuie atinse.

**Varianta 2 (fără om la calculator):** supraveghetorul repară unealta (categoria 6, „reparații de scripturi”), de
exemplu cu o opțiune `porneste --din-nou` care mută singură fișierul vechi în `S<n>_<ora>.json` dacă sarcina e
terminată. Alternativ, dă permisiunea pentru `mv` în `lucru/cascada/`. Apoi S7 din nou `aprobat`.

Nu pornesc S7 sub alt nume (de exemplu „S7b”): rulările următoare caută `lucru/cascada/S7.json`, așa că n-ar urmări-o
corect.

## Testele

`CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -m pytest -q`: trec toate (după schimbarea configurării).
