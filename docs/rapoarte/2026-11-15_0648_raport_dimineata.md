# Raportul de dimineață — duminică, 15 noiembrie 2026, 06:48

Scris automat de sarcina „Kronos raport dimineata”, fără om de față. Doar am citit jurnalele; n-am pornit și n-am schimbat nimic.

## Pe scurt

- **Antrenarea mare S110 merge bine toată noaptea, fără nicio întrerupere.** A ajuns la ora 31 din 52.
- Scorul la română (cât de greu îi e modelului să ghicească textul; **mai mic = mai bine**) a scăzut de la 1,1792 (ora 24, aseară la 22:35) la **1,1603** (ora 31, azi la 05:43). Cel mai bun de până acum.
- Placa video: 5.653 MB din 8.192, 62 °C — sub limita de 7.000 MB.
- Testele: **1.461 trec, 1 pică, 1 sărit.** Cel care pică e o siguranță pentru spațiul pe disc (mai jos), nu o stricăciune.
- Discul C: **34 GB liberi** și scade cu ~0,7 GB pe oră cât merge antrenarea.

## Ce a rulat noaptea

Singurul lucru care a folosit placa a fost **S110**: Kronos cu 24 de straturi, antrenat de la zero, timp de 52 de ore
(pornit vineri 13 nov la 22:08). S-a terminat câte o oră de antrenare cam la fiecare 61 de minute, de fiecare dată cu un
model păstrat (#614–#620 în noaptea asta). În jurnal nu apare nicio eroare și niciun „ANULAT”.

| Ora antrenării | Ceasul | Româna (mai mic = mai bine) |
|---|---|---|
| 24 | 14 nov 22:35 | 1,1792 |
| 25 | 23:36 | 1,1763 |
| 26 | 15 nov 00:37 | 1,1738 |
| 27 | 01:38 | 1,1700 |
| 28 | 02:40 | 1,1679 |
| 29 | 03:41 | 1,1657 |
| 30 | 04:42 | 1,1607 |
| 31 | 05:43 | 1,1603 |

Reper: la ora 12 era 1,2335, la ora 1 era 1,5657. Coborârea a încetinit (normal spre final), dar n-a urcat niciodată.

**Regulile de oprire din pre-înregistrare** (NaN = un număr stricat, sau 3 ore la rând în sus și cu cel puțin 0,03 peste
minim): **niciuna nu s-a declanșat.** Punctele de control de la 12 h și 24 h au fost trecute deja (rapoartele de ieri).

Celelalte programe de noapte:
- **Executantul cascadei** a pornit la fiecare 30 de minute și s-a încheiat de fiecare dată normal (cod 0), în 15–25 de
  secunde — n-avea ce face, placa e ocupată de S110.
- **CONTINUUM** doar observă (stă „în repaus”, ultima intrare 06:35), nu pornește nimic. Așa e stabilit.
- **Examen de conversație** n-a fost noaptea asta → nu sunt cele 20 de răspunsuri de verificat azi.

## Pre-înregistrarea

Pre-înregistrarea S110 (`docs/preinregistrari/2026-11-13_w2_mare_24z2.md`) **rămâne deschisă**: antrenarea nu s-a terminat,
deci nu există încă un verdict final. O închid după examenele de la final. Nu există altă pre-înregistrare de închis.

## Placa video

- Acum: 5.653 MB, 62 °C, folosită 100 %.
- Fișierul care notează placa la fiecare câteva secunde s-a oprit la **14 nov 22:08** (a înregistrat exact 24 de ore).
  Pentru noapte am doar citirile de la verificări: 00:58 — 5.652 MB / 63 °C; 06:40 — 5.653 MB / 62 °C. Maximul din
  primele 24 de ore a fost 6.315 MB. Probabil înregistratorul are o limită de 24 h; nu e grav, dar de știut.

## Testele

Comanda: `CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -m pytest -q` (cu afișarea cifrelor). Rezultat:
**1.461 trec, 1 pică, 1 sărit** (7 min 25 s).

Cel care pică: `teste/test_kronos_cod_tokenizer.py::test_unealta_cap_coada_fara_excluse_si_fara_validare_la_antrenare`.
Rulat singur, pică la fel. Motivul: unealta care împarte codul în bucăți are o siguranță — **se oprește dacă pe disc sunt
sub 40 GB liberi**. Acum sunt ~36,5 GB (34 GB cum le arată Windows), așa că unealta se oprește cuminte și testul o vede
„neterminată”. Aseară la 23:07 erau ~42 GB și testul trecea (1.462). Nu e o stricăciune de cod; va trece din nou când
se eliberează spațiu. **N-am reparat nimic.**

## Discul C:

34 GB liberi acum (aseară la 23:07: 39 GB). Antrenarea mai are ~21 de ore → la final ar trebui să rămână ~19–20 GB.
Regula din S110: dacă scade sub 15 GB, antrenarea se oprește și te întreb. Deocamdată suntem deasupra.

## Ce urmează

- S110 se termină pe la **luni 16 nov, ~03:10–03:20**. Apoi vin examenele de final (pe ultimul model, pe #513 și #577)
  și verdictul: e mai bun decât #513 doar dacă iese cu cel puțin 0,005 mai jos pe română. Raportul final îl scrie executantul.
- După S110 urmează S111 (din coadă).

## Ce aștept de la tine

1. **Nimic urgent.** Antrenarea merge singură.
2. **Spațiul pe disc:** sarcina S113 (ștergerea probelor vechi, ~8,6 GB) nu e încă făcută: executantul face doar
   verificările și îți scrie apoi comenzile de ștergere (vezi `docs/rapoarte/2026-11-14_1137_S110_24z2_12h.md`, secțiunea
   S113). Când le primești și le rulezi, discul trece din nou de 40 GB și testul care pică acum va trece. Până atunci nu e
   grav: S110 are loc să se termine.
3. Dacă vrei, spune dacă înregistratorul plăcii ar trebui să meargă tot timpul antrenării, nu doar 24 de ore (eu nu-l schimb).
