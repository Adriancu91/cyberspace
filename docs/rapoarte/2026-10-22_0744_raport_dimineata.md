# Raportul de dimineață — joi, 22 octombrie 2026, 07:44

Scris de Claude Code, pornit singur de sarcina Windows „Kronos raport dimineata” (07:40). Am doar citit jurnalele; n-am
pornit nimic pe placă și n-am schimbat cod.

## Pe scurt

- **Noaptea a mers cum trebuie, fără nicio eroare.** Au rulat, una după alta, patru lucrări din coadă: S12 (antrenarea
  nopții 12), S15 (examenul mare), strategia nouă (aprobată de tine la 01:45) și S16 (verificatorul fără Qwen).
- **Noaptea 12 (S12): INFIRMAT, fără regresie.** Tipurile noi de întrebări puse la antrenare nu l-au ajutat pe Kronos la
  tipurile pe care nu le-a văzut (2 din 15, ca înainte). Dar n-a stricat și n-a uitat nimic.
- **Examenul mare (S15): „tipurile văzute s-au învățat, dar nu se transferă”.** Modelul #415 a răspuns bine la 30 din 30
  de întrebări de tipurile pe care le-a văzut, pe texte noi; la tipuri nevăzute doar 6 din 50.
- **S16: verificatorul nostru (fără niciun model străin) dă același verdict ca Qwen în 527 din 540 de cazuri (97,6 %).**
  Pragul era 90 %, deci trece: Qwen poate ieși din rolul de judecător la „răspuns din text”.
- **Diseară la 19:00 pornește S17** („întrebări născute de Kronos”), deja aprobată de supraveghetor după S16.
- **Testele: 868 trecute, 1 sărit, 0 picate.**

## Ce a rulat noaptea, pe ore

| ora | ce | cum s-a terminat |
|---|---|---|
| 19:00–22:12 | S12: antrenarea liniei `w2_conv_text_v3`, 3 ore, pornită din #407 | 3 modele păstrate (#413, #414, #415), fără erori |
| 22:31–22:34 | examenele pe #415 (conversație, română/cod, setul sacru) | toate cu cod 0 (jurnal #416–#418) |
| 22:35 | executantul a închis pre-înregistrarea nopții 12, cu verdictul | INFIRMAT, fără regresie |
| 00:11–00:45 | S15: examenul mare de generalizare, 80 de întrebări, pe #401, #407, #415 | cod 0 (jurnal #419–#421), placa ~15 minute |
| 01:37–01:45 | strategia „Kronos fără LLM” — propusă, apoi aprobată de tine | — |
| 02:29–02:47 | S16: verificatorul fără LLM + re-notarea S15 și S4, doar pe procesor | gata, 17 teste noi |
| 05:15 | supraveghetorul a verificat S16 și a trecut S17 pe „aprobat” | — |
| după 02:47 | nimic pe placă; executantul a verificat la 30 de minute și a lăsat S17 pentru diseară | corect: S17 cere până la 7 ore, nu mai încăpea |

**Pre-înregistrările:** amândouă cele de azi-noapte (`2026-10-21_noaptea12_tipuri_noi.md` și
`2026-10-22_examen_generalizare_mare.md`) erau deja închise de executant, cu secțiunile „Ce a ieșit” și „Verdictul”.
Am verificat verdictele după pragurile scrise în ele și sunt corecte, așa că nu le-am atins.

## Cifrele

### Noaptea 12 (S12), pe modelul #415

| ce se măsoară | pragul | a ieșit | |
|---|---|---|---|
| tipuri noi de întrebări (S4 b) | confirmat ≥ 5/15, infirmat ≤ 2/15 | **2/15** | INFIRMAT |
| aceeași întrebare, altă formulare | ≥ 10/15 | 11/15 | trece |
| „Nu scrie în text.” spus pe nedrept | ≤ 10/45 | 9/45 | trece |
| „Da./Nu.” greșit | ≤ 1 | 3 | nu trece |
| întrebări da/nu | ≥ 11/15 | 13/15 | trece |
| noaptea 10 (din text / „Nu scrie” / refuz greșit) | ≥ 45/50, ≥ 16/20, ≤ 5/50 | 50/50, 20/20, 0/50 | trece |
| română (cât de bine ghicește textul; mai mic = mai bine) | ≤ 1,3133 | 1,2858 | trece |
| cod (la fel) | ≤ 0,8174 | 0,7920 | trece |
| povești (la fel) | ≤ 0,47 | 0,4411 | trece |
| fapte noi | ≥ 65 | 68 | trece |

### Examenul mare (S15): câte corecte (nota profesorului ≥ 7)

| model | tipuri nevăzute (din 50) | tipurile văzute la antrenare (din 30) |
|---|---|---|
| #401 | 6 | 14 |
| #407 | 9 | 4 |
| #415 | **6** | **30** |

### Verificatorul fără LLM (S16)

- Acord cu Qwen pe 540 de răspunsuri: **527 (97,6 %)**; cel mai slab model tot are 97,1 %.
- Cu verificatorul în locul lui Qwen, S15 dă aproape aceleași cifre: tipuri nevăzute 7/9/6, tipuri văzute 13/4/30.
  Concluzia nu se schimbă.

### Placa și CONTINUUM

- Placa video (acum, 07:40): liberă, 728 MB folosiți din 8 GB, 29 °C. Noaptea a stat sub limita de ~7 GB (S12: 6.319 MB).
- CONTINUUM doar observă (ultimul ciclu #2357, 07:35, „REPAUS: placa e a executantului”). N-a pornit nimic.

## 20 de răspunsuri alese la întâmplare

Din `lucru/examen_conversatie/experiment_415_20261022_001707.json` (examenul mare S15, modelul #415, ultimul model
antrenat). Alese cu `random.Random(20261022).sample` — **sămânța 20261022**. „b2” = tip de întrebare pe care Kronos nu
l-a văzut; „e” = tip pe care l-a văzut la antrenare (dar pe text nou). Nota e de la profesor (Qwen), din 10.
La întâmplare au ieșit 16 „b2” și 4 „e”; dintre cele 20, 6 au nota ≥ 7.

| nr. | grupa | întrebarea | răspunsul lui Kronos | referința | nota profesorului | e bine? (tu) |
|---|---|---|---|---|---|---|
| 1 (#46) | b2 | Ce rol a interpretat Mary Frances Crosby în Dallas? | Mary Frances Crosby. | Kristin Shepard. | 1 |  |
| 2 (#75) | e | Sergius Tiberiu Sbârcea a fost deputat în ce legislatură? | În legislatura 2000-2004. | În legislatura 2000-2004. | 10 |  |
| 3 (#37) | b2 | Ce funcție a îndeplinit Jan Garrigue Masaryk? | În 1886. | Ministru de externe al Cehoslovaciei. | 1 |  |
| 4 (#23) | b2 | Ce era de profesie Pedro Leandro Ipuche? | Nu scrie în text. | Poet. | 1 |  |
| 5 (#7) | b2 | În ce oraș își are sediul Interpol? | În județul Iași. | În Lyon, Franța. | 1 |  |
| 6 (#31) | b2 | Cine a pictat Mont Sainte-Victoire văzut din Bellevue? | Peisajul. | Paul Cézanne. | 1 |  |
| 7 (#30) | b2 | Cine a pictat Persistența memoriei? | Salvador Dalí. | Salvador Dalí. | 10 |  |
| 8 (#79) | e | În ce legislatură a fost deputat Florea Danciu? | În legislatura 1992-1996. | În legislatura 1992-1996. | 10 |  |
| 9 (#1) | b2 | În ce țară se află Peștera Mondmilchloch? | Nu scrie în text. | În Elveția. | 1 |  |
| 10 (#70) | e | De cine a fost descrisă specia Sphenomorphus kitangladensis? | Brown 1995. | Brown. | 8 |  |
| 11 (#17) | b2 | Ce actori apar în rolurile principale din Amurgul fântânilor? | Virgil Calotescu. | Mircea Diaconu, Costel Constantin, Mircea Albulescu. | 1 |  |
| 12 (#8) | b2 | În ce oraș își are sediul Industria Vehiculelor Elene? | În județul Salonic. | În Salonic. | 4 |  |
| 13 (#26) | b2 | Pe ce post evoluează Nicolae Daniel Balauru? | Pe post evoluează Nicolae Daniel Balauru. | Mijlocaș dreapta. | 3 |  |
| 14 (#25) | b2 | Pe ce post joacă Nicolae Milinceanu? | Pe postul de atacant. | Atacant. | 10 |  |
| 15 (#40) | b2 | Ce funcție a avut Pierre Mauroy între 1981 și 1984? | Nu scrie în text. | Prim-ministrul Franței. | 1 |  |
| 16 (#14) | b2 | Ce actori joacă rolurile principale în Înapoi în cartier? | Gelu Radu. | Mody Levente, Florin Matingo, Horia Radu. | 1 |  |
| 17 (#67) | e | În ce raion se află Tomai? | În raionul Leova. | În raionul Leova. | 10 |  |
| 18 (#49) | b2 | Cine a câștigat Turul Italiei 2016? | Nu scrie în text. | Vincenzo Nibali. | 1 |  |
| 19 (#10) | b2 | În ce oraș este Loftus Versfeld Stadium? | În raionul Pretoria. | În Pretoria, Africa de Sud. | 4 |  |
| 20 (#33) | b2 | Cine a produs Pași pe Lună? | Wernher von Braun. | Barry Coe. | 1 |  |

Se vede ce spune verdictul: la tipurile văzute („legislatura”, „raionul”, „descrisă de”) răspunde bine; la cele nevăzute
lipește tiparul învățat unde nu se potrivește („În județul Iași.” pentru un oraș, „În raionul Pretoria.”).

## Testele

`CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -m pytest -q`: **868 trecute, 1 sărit, 0 picate** (cod de ieșire 0). Testul
sărit e cel care are nevoie de placă, ca de obicei (am rulat fără placă).

## Ce aștept de la tine

1. Completezi coloana „e bine? (tu)” la cele 20 de răspunsuri de mai sus.
2. Nimic nu e căzut și nimic nu trebuie reparat. S17 pornește singură diseară la 19:00; ziua executantul pregătește doar
   scripturile ei pe procesor, fără placă. Dacă vrei s-o oprești sau să schimbi ceva la ea, spune înainte de 19:00.
