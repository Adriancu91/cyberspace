# Raportul de dimineață — luni, 16 noiembrie 2026

*Scris automat de sarcina „Kronos raport dimineata”, la 06:57. Doar am citit jurnalele și am rulat testele; n-am pornit nimic
pe placă și n-am schimbat cod.*

## Pe scurt

- **S110 s-a terminat bine** (cele 52 de ore cu modelul mare de 24 de straturi): verdict **MAI BUN**. Nota la română
  (cu cât mai mică, cu atât mai bine): modelul nou **#641 = 1,0891**, modelul în uz **#513 = 1,2060**. Raportul complet e
  deja scris de executant: `docs/rapoarte/2026-11-16_0348_S110_24z2_final.md`.
- **S111 rulează acum** (pornită la 04:10): îl învață pe #641 să converseze, 7 ore. Ora 1 și ora 2 au trecut normal.
  Se termină pe la **~11:20**, apoi vin examenele și verdictul (le scrie executantul).
- **Testele:** 1462 trec, 1 pică (cel cunoscut, din lipsă de spațiu pe disc), 1 sărit. Atenție: la prima rulare de azi au picat
  19, dar la a doua rulare doar cel cunoscut (detalii mai jos).
- **De la tine:** spațiul pe disc e strâns (vezi „Ce aștept de la tine”).

## Ce a rulat de aseară până acum

| ce | când | cum s-a terminat |
|---|---|---|
| S110: antrenarea de 52 h (modelul de 24 de straturi, de la zero) | vineri 13 nov 22:08 → azi 03:08 | normal (cod 0), nicio cădere, nicio regulă de oprire atinsă |
| S110: examenele de final (română, cod, examenul neutru) | 03:29 → 03:40 | normal |
| S111: pregătirea (configurarea, testul ei, pre-înregistrarea) | 03:59 → 04:10 | gata, încărcat pe GitHub |
| S111: antrenarea conversației din #641, 7 h | pornită 04:10:51 | **încă merge** (ora 2 din 7 gata la 06:13) |
| CONTINUUM (bucla care se auto-îmbunătățește) | toată noaptea | doar a observat („repaus”, placa e a executantului), cum trebuie; ciclul #9173 la 06:40 |
| Executantul cascadei | la fiecare 30 min | a verificat S111 de 5 ori, totul în regulă |

Jurnalele de noapte vechi (`noapte_ws_w2.log`, `paznic_procese.log`) n-au nimic nou din 12 noiembrie.

## Cifrele

**S110 — final** (re-măsurat la 03:30, în aceeași rulare):

| examenul | #641 (nou) | #513 (în uz) | diferența |
|---|---:|---:|---:|
| română curat | **1,0891** | 1,2060 | −0,117 (mai bine) |
| examenul neutru (Wikipedia română apărută după 12 oct) | **1,0125** | 1,1265 | −0,114 (mai bine) |
| cod curat | 0,7418 | 0,7247 | +0,017 (puțin mai slab) |
| povești englezești | 0,4154 | 0,4049 | +0,011 (puțin mai slab) |

**S111 — până acum** (nota la română după fiecare oră; pornește de la 1,0891 al lui #641):

| ora | model | româna | la |
|---:|:---:|---:|:---:|
| 1 | #645 | 1,0889 | 05:12 |
| 2 | #646 | 1,0886 | 06:13 |

Viteza: 5,1 pași pe secundă (~18.430 pe oră). Româna stă pe loc, cum e de așteptat: S111 învață conversația, nu româna.

**Placa video:** acum 6.411 MB și 61 °C (limita: 6.700 MB pentru S111, 7.000 MB pe workstation; 83 °C). În regulă.

**Discul C:** la 06:40 avea **15 GB** liberi, la 06:56 **23 GB** (spațiul variază în timpul antrenării și al testelor).
Lanțul S111 apasă singur butonul de oprire dacă scade sub 15 GB; deocamdată nu l-a apăsat.

## Pre-înregistrări și verdict

- **S110** (`docs/preinregistrari/2026-11-13_w2_mare_24z2.md`): deja închisă de executant la 03:48, cu „Ce a ieșit” și
  „Verdictul”: **MAI BUN** (pragul era ≤ 1,2010; a ieșit 1,0891). N-am mai atins-o.
- **S111** (`docs/preinregistrari/2026-11-16_w2_mare_24zc.md`): rămâne **deschisă** intenționat. Experimentul nu s-a terminat
  (mai are ~4,5 ore + examenele), deci verdictul nu se poate judeca acum. O închide executantul după examene.

## Cele 20 de răspunsuri

Noaptea asta **n-a avut examen de conversație** (ultimele fișiere de acest fel sunt din 13 noiembrie). Deci nu am ce să-ți arăt
azi. Vor apărea după examenele S111 (în raportul executantului).

## Testele

Comanda: `CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -m pytest -o addopts="" -q` (pe procesor, ca să nu încurce placa).

- **Prima rulare (06:41):** 1444 trec, **19 pică**, 1 sărit. Au picat aproape toate din `teste/test_bucati_din_text.py`
  (eroarea „FileNotFound” — un fișier de probă care n-a fost găsit) plus cel cunoscut.
- Am rulat singur `test_bucati_din_text.py`: **22 din 22 trec**.
- **A doua rulare (06:49), întreaga suită:** **1462 trec, 1 pică, 1 sărit** (7 min 21 s). Cel care pică e cel cunoscut:
  `test_kronos_cod_tokenizer.py::test_unealta_cap_coada_fara_excluse_si_fara_validare_la_antrenare` — vrea 40 GB liberi pe C:.
  Nu e o stricăciune.

Ce cred că s-a întâmplat la prima rulare: pe disc erau doar ~15 GB liberi, iar antrenarea S111 scrie în același timp; probabil
un fișier temporar al testelor n-a mai putut fi scris sau citit. N-am reparat nimic — doar îți spun, ca să știi că e „instabil”,
nu stricat.

## Ce aștept de la tine

1. **Spațiul pe disc** (cel mai important). C: oscilează între 15 și 23 GB liberi. Dacă scade sub 15 GB, S111 se oprește singură
   după ora în curs (curat, modelul ultimei ore rămâne salvat), iar examenele se fac pe acel model. Ca să nu se întâmple:
   rulează comenzile de ștergere S113 (~9 GB), care te așteaptă în `docs/rapoarte/2026-11-15_1600_S113_stergere_probe.md`.
   Tot ele fac să treacă la loc testul cunoscut (cel de 40 GB).
2. **Nimic altceva urgent.** Pe la 11:20 S111 termină antrenarea, apoi executantul face examenele și îți scrie raportul cu
   verdictul și cele 20 de răspunsuri. Apoi urmează S112 (câștigătorul pus în interfața de convorbire).
3. Dacă vrei, uită-te la prima rulare de teste (cele 19 picate): dacă se repetă în zilele următoare, merită o sarcină de
   reparat; deocamdată pare legată de discul aproape plin.
