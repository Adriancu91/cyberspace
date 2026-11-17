# S119 — trecerea 3 oprită: a doua verificare de scurgeri NU e curată (17 noiembrie 2026, 11:06)

Scris de executant (cascada), fără om de față.

## Pe scurt
- Curățarea textului românesc nou (FineWeb-2 `ron_Latn`, fișierele `000_00001` + o parte din `000_00002`) s-a făcut:
  **2.550.434 de texte, 7,96 GB** în `date/ws/s119/antrenare.txt` (+ 25.708 texte, 80 MB în `validare.txt`).
- A doua verificare de scurgeri (unealta veche `trece` din `unelte/hrana_fineweb_rest.py`) a găsit **162 de texte**
  cu bucăți de 50 de litere comune cu validările (160 cu `validare_fineweb2_ro`, 1 cu `validare_cod_stack`,
  1 cu `validare_wikipedia_ro`). Regula uneltei e „0”, deci **n-a tokenizat** și s-a oprit cu cod 1 (10:45:01).
- Am pus S119 pe **`oprit`**. Nu am reparat nimic și nu am rulat altceva. Aștept decizia (variantele de mai jos).

## Ce a rulat
- Comanda (prin cascadă, procesul 22776): `unelte/text_s119.py tot --limita-gb 8 --procese 8 --minim-liber-gb 30`
- Pornită 10:11:21, încheiată 10:45:01 (cod 1). Jurnal: `lucru/cascada/S119.log`; cifrele: `date/ws/s119/info.json`.
- Curățarea: 1.179 s (oprită la limita de 8 GB de text scris); a doua verificare: 774 s. RAM vârf (procesul principal): 11.346 MB.
- C: liber: 48,5 GB la pornire → 40,4 GB după curățare → **38 GB acum** (peste pragul de 30 GB).

## Cifrele pe sursă
| | FineWeb-2 `ron_Latn` S119 | oasst2 (`lang = ro`) |
|---|---|---|
| descărcat (trecerea 2) | 2 fișiere, 2 × 4,85 GB | `ready.messages` 54 MB |
| citite | 3.293.000 (`000_00001` întreg: 3.151 grupe; `000_00002`: 143 grupe) | 135.174 mesaje, 13.854 arbori |
| prea scurte / stricate | 10.261 / 3.859 | — |
| dubluri identice (față de vechi / între noi) | 7 / 8 | — |
| dubluri aproape identice (față de vechi / între noi) | 146.624 / 145.656 | — |
| scoase pentru scurgeri | 410.443 (12,5 % din ce rămăsese) | — |
| păstrate antrenare / validare | 2.550.434 / 25.708 texte | **0** (niciun mesaj `ro`) |
| octeți antrenare | 7.959.758.931 (SHA-256 f9db94ec…3278653) | 0 |

- Scurgerile vin aproape toate din `validare_fineweb2_ro` (392.467 de texte): sunt mai ales „șabloane de site”
  („Urmareste-ne si pe Facebook…”, „In lipsa unui acord scris din partea InternetCorp…”, „Informatiile publicate de
  opiniatimisoarei.ro…”), adică aceleași subsoluri de pagină care apar și în validarea veche. Ca la S110.
- Simboluri estimate (dacă s-ar tokeniza): ~7,96 GB × ~0,55 ≈ 4,4 GB de simboluri int16 ≈ ~2,2 mld simboluri
  (estimare după raportul amestecului W2, nu măsurată).
- Română nouă față de cea veche: textul vechi românesc are ~7,45 GB (wikipedia 0,76 + wikisource 0,13 + fineweb2 2,99 +
  fabule 3,52 + validările); cele 7,96 GB noi ar fi **≈ +107 %** (de două ori mai mult; față de FineWeb-ul vechi de 3,0 GB ≈ 2,7×).

## Ce s-a întâmplat la a doua verificare (cauza probabilă, nedovedită)
Prima căutare (la curățare) se uită la fiecare text **singur** (cu un rând nou în față). A doua (`trece`) se uită la
blocuri întregi din fișier, unde textele sunt lipite cu `<|endoftext|>` + rând nou; o bucată de 50 de litere care
începe la sfârșitul unui text și trece peste `<|endoftext|>` în textul următor e pusă pe seama primului text. Cum și
fișierele de validare au același `<|endoftext|>`, un sfârșit de text comun (de exemplu un subsol de site scurt) + separatorul
se poate potrivi cu o validare. 162 din 2,55 milioane (0,006 %) se potrivește cu asta, dar **nu am verificat** pe texte
(n-am voie să repar sau să ocolesc pe ascuns; doar raportez).

## Variantele (alege una)
1. **Repar a doua cale și refac doar pasul de scoatere:** în unealtă, prima căutare să caute și cu separatorul la
   capăt (exact ca `trece`), apoi scot cele 162 de texte cu `trece` scriind un fișier nou (`antrenare.txt` curățat),
   verific din nou (0 cerut), apoi tokenizez. ~30 min procesor, fără descărcare. Recomandarea mea.
2. **Scot doar cele 162 de texte** cu `trece` (are deja modul `scrie`) într-un fișier nou și verific a doua oară,
   fără să schimb prima căutare. Mai rapid (~15 min), dar rămâne diferența între cele două căutări pentru data viitoare.

Oricare variantă e o schimbare de unealtă/pas în afara „ce faci” → aștept „da” (de la Adrian sau supraveghetor).

## Încă de la trecerile 1–2 (neschimbat)
- **oasst2:** 0 mesaje românești în `ready` → nu aduce nimic.
- **CulturaX `ro`:** cere acceptarea condițiilor pe Hugging Face → întrebarea pentru Adrian rămâne (n-am acceptat nimic).
- **HPLT v2:** nedescărcat (vezi `docs/rapoarte/2026-11-16_1807_S119_licente.md`).
- **Rămas nedescărcat:** 17 fișiere FineWeb-2 `ron_Latn` (lipsă de loc pe C:, pragul de 30 GB).

## Testele
`CUDA_VISIBLE_DEVICES=-1 python -m pytest`: **1490 trec, 1 sărit** (6 min 55 s).

## Ce aștept
- Alegerea între variantele 1 și 2 (sau altceva). Până atunci S119 rămâne `oprit`; textul curățat rămâne pe disc
  (`date/ws/s119/`, 7,5 GB), nimic șters.
- S122 pasul 4 și S118 vin după S119 `gata` (după ordinea din coadă).
