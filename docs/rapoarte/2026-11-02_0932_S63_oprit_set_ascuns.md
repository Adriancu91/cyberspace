# S63 oprit înainte de pornire: un al doilea set ascuns de 200 fără variantele S58 nu se poate face

*Executantul, 2 nov 2026, 09:32. Nimic n-a pornit pe placă; nicio antrenare, niciun examen, nicio pre-înregistrare scrisă.*

## Pe scurt

- S62 e `gata` (memoria sub 6.500 MB la ambele măsurări), iar S63 e `aprobat` de Adrian (C-56, „pornește acum”), așa că
  am început-o la 09:28 (placa liberă: 451 MB, 25 °C, niciun proces greu).
- **Pasul 2 nu se poate face așa cum e scris.** Coada cere un set ascuns nou de **200 de probleme (20 de șabloane × 10)**
  care să ocolească setul de probă **și** variantele setului ascuns S58. Șabloanele au însă puține variante diferite:
  13 din 20 au cel mult 24 de variante în total, iar `s07_roteste` are doar **14**. După cele 10 ale S58 și cea a setului
  de probă rămân 3. Unealta se oprește corect cu „prea puține variante diferite”.
- Alegerea (un set mai mic sau o suprapunere parțială cu S58) schimbă pragul „pass@10 ≥ 6/200”, deci nu o fac eu.
  **S63 → `oprit`**, cu motivul „cere alegerea lui Adrian/supraveghetorului: setul ascuns nou”.

## Ce am făcut

1. `git pull --rebase` (la zi), `cascada.py stare`: fereastra „zi”, 541 de minute rămase, placa liberă, `liber: true`.
2. Am verificat cum continuă linia: `lucru/cod_c1/gpt.pt` există (2 nov 05:15), jurnalul are 10 ore pe `cod_c1`, deci
   comanda corectă ar fi `antrenare_lunga.py --config config/cod_c1_init002.toml --ore 20` (orele 11–20, din `gpt.pt`).
   **De știut pentru pre-înregistrare:** `durata_scaderii_secunde = 36000` s-a terminat după ora 10, așa că orele 11–20
   rulează cu rata **fixă la 10 % (6·10⁻⁵)**, fără încălzire nouă (`module/model_gpt.py`, `rata_acum`: progresul e tăiat la 1).
   Zăvorul `lucru/cod_c1/ruleaza.lock` rămas din S58 nu blochează (Windows îl eliberează când moare procesul).
3. Pasul 2: `examen_cod.py ascuns` exclude doar setul de probă. Am adăugat opțiunea `--exclude-dosar` (cu teste) ca să
   excludă și setul S58. Testul cu un set „vechi” fals (din teste, nu cel adevărat) a picat: `RuntimeError:
   s03_inverseaza_bucati: prea puține variante diferite`. Am numărat variantele fiecărui șablon din 20.000 de trageri
   (`lucru/cascada/S63_proba/numara_variante.py`, fără să citesc vreun set ascuns):

| șablon | variante | | șablon | variante |
|---|---|---|---|---|
| s01_divizibile | 22 | | s11_doua_liste | 30 |
| s02_caractere | 17.750 | | s12_matrice | 24 |
| s03_inverseaza_bucati | 16 | | s13_cuvant_frecvent | 16 |
| s04_fizz | 1.260 | | s14_prime | 42 |
| s05_recurenta | 1.296 | | s15_cifre | 36 |
| s06_palindrom | 24 | | s16_paranteze | 15 |
| s07_roteste | 14 | | s17_aplatizeaza | 16 |
| s08_cezar | 50 | | s18_bucati | 20 |
| s09_comprimare | 24 | | s19_cmmdc | 16 |
| s10_al_k_lea | 18 | | s20_baza | 21 |

   Fără nicio suprapunere cu S58 ar încăpea cam **163 de probleme** (estimare: min(10, variante − 11) pe șablon), nu 200.
4. **Am retras schimbarea** din `examen_cod.py` și din teste (o opțiune care nu poate reuși cu șabloanele de acum n-are
   rost; arborele Git e exact ca la 022b615). Setul nou NU e făcut; `lucru/kronos_cod/ascuns2/` nu există; setul ascuns
   S58 nu a fost deschis.

## Testele

`CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -m pytest`: **1174 passed, 1 skipped in 284.94s**, rulat după retragere (cifra de la S62, neschimbată).

## Ce aștept de la Adrian (sau de la supraveghetor)

Alege una (recomandarea mea: **(a)**):

- **(a) Set nou fără nicio suprapunere, cu cât încape (~163 de probleme).** Șabloanele bogate dau 10, cele sărace dau ce
  le-a rămas. Pragurile se scriu pe procente: CONTINUĂ = pass@10 ≥ 3 % (6/200 → ~5/163), PLATOU = ≤ 1,5 % (3/200 → ~2/163).
  E cel mai curat (nicio problemă văzută), dar șabloanele sărace (s07, s16) cântăresc mai puțin decât la S58.
- **(b) 200 de probleme, sămânță nouă, ca la S58 (exclude doar setul de probă).** Pragurile rămân neschimbate (6/200),
  dar o parte din probleme vor fi aceleași variante ca la S58 (la s07 aproape toate). Modelul nu le-a văzut la antrenare
  (S53 a curățat scurgerea), dar noi le-am văzut nota.

Oricare variantă: pasul 3 (cele 10 ore) nu depinde de set. Dacă vrei să nu stea placa, se poate scrie **„S63 pornește
antrenarea acum, setul (a)/(b) se face înainte de examene”**; pre-înregistrarea s-ar scrie înainte de pornire, cu varianta
aleasă deja trecută în ea.

## Ce urmează

- S63 rămâne `oprit` până la alegere; nu mai e altă sarcină `aprobat` în coadă, deci placa stă liberă.
- Comanda pentru (a), dacă o alegi, cere o mică schimbare în `examen_cod.py ascuns` (granița 5: unealtă + test, notarea
  neschimbată), pe care o pot face la următoarea rulare.
