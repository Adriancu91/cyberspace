# Raportul de dimineață — sâmbătă, 7 noiembrie 2026

*Scris la 06:46 de Claude Code, pornit automat de sarcina „Kronos raport dimineata”. Doar am citit jurnalele și am rulat testele;
n-am pornit nimic pe placă și n-am schimbat cod.*

## Pe scurt

- **Noaptea a rulat S85:** prima noapte de 5 ore a lui Kronos „mare” (24 de straturi), cu rețeta nouă „e1” (rată de învățare mică).
  A mers doar **2 ore din 5**. La începutul orei 3 (01:44) s-a umplut iar memoria plăcii video, exact în același loc ca la S77c.
- **Verdictul S85: NEMĂSURAT.** Întrebarea era despre modelul de la ora 5, iar acela nu există.
- **S86 (măsurarea memoriei): verdict DA.** Cu Muon (un alt fel de a corecta modelul, care ține mai puține date pe placă) memoria la
  antrenare scade cu **649 MB** față de AdamW (felul de până acum). Pragul era cel puțin 400 MB.
- **#513 e acum modelul în uz** în pachetul KGR1 (S83b, cu „Da 513”-ul tău). Rămâne de făcut de tine Release-ul pe GitHub (comanda mai jos).
- Aseară, înainte de S85: S77e (rețeta e1 „ȚINE”), S83 (oprit corect, apoi reluat ca S83b) și S84 (lista fișierelor .pt, nimic șters).
- **Testele: 1.278 trec, 1 sărit, 0 picate.** Testul care pica ieri din lipsă de spațiu trece acum: C: are **86 GB liberi**.
- **Placa video** e liberă acum (456 MB, 25 °C). CONTINUUM, bucla automată, e în REPAUS: doar observă (ciclul 6.618 la 06:40).
- Noaptea asta **nu** a avut examen de conversație, deci azi nu sunt cele 20 de răspunsuri de verificat.

## Ce a rulat de aseară până acum

| ora | ce | cum s-a terminat |
|---|---|---|
| 6 nov 19:00 → 21:35 | **S77e**: câte o oră de probă pentru modelul mare, cu două rate mici (e1 = 1e-5, e2 = 2e-5) | gata: e1 ȚINE, e2 AJUTĂ PUȚIN |
| 21:59 → 22:06 | **S83**: #513 ca model în uz — exportul avea altă mărime decât scria în sarcină (32 de octeți mai puțin, doar antetul) | oprit corect, reluat ca S83b |
| 22:29 → 23:05 | **S84**: lista celor 592 de fișiere .pt (107,6 GB) pe grupe: de păstrat, se poate șterge, necunoscut | gata, nimic șters |
| 23:31 → 01:44 | **S85**: noaptea de 5 ore a modelului mare pe rețeta e1 | **oprit** după ora 2 (memorie plină) |
| 02:30 → 02:39 | **S83b**: #513 devine modelul implicit (pe procesor) | gata; Release-ul rămâne la tine |
| 03:00 → 04:06 | **S86**: memoria plăcii, Muon față de AdamW (~35 min pe placă) | gata, verdict DA |
| 04:28 → 06:29 | Executantul a verificat coada la fiecare jumătate de oră: S87 e o sarcină de zi, deci n-a pornit nimic | normal |

## S85 în cifre

*„bpb” = câți biți îi trebuie modelului pentru o literă. **Mai mic = mai bine.***

| ora | model | scor pe povești (R2) | pași pe secundă | memorie PyTorch |
|---|---|---|---|---|
| 1 | #528 | 0,4073 | 6,4 | 5.200 MB |
| 2 | #529 | 0,4069 | 6,4 | 3.892 MB |
| 3 | #530 | — | — | **anulat: memorie plină** la testul rapid (mai trebuiau 12 MB peste plafonul de 5.800 MB) |

Examenele pe #529 (ora 2), doar ca informație:

| măsura | #529 (S85, 2 ore) | pornirea (= #477) | #513 | #518 (S77c, 2 ore) |
|---|---|---|---|---|
| română curat | **1,2108** | 1,2096 | 1,2060 | 1,2268 |
| cod curat | **0,7280** | — | 0,7247 | 0,7413 |
| povești (R2) | **0,4069** | — | 0,4050 | 0,4155 |

- Rețeta e1 ține modelul aproape de punctul de pornire, mult mai bine decât S77c, dar după 2 ore nu e încă mai bun nici decât
  pornirea, nici decât #513.
- Placa: cel mult **6.431 MB** și **61 °C** (sub limitele de 6.700 MB și 83 °C).
- Modelul a văzut **95 milioane** de simboluri în 2 ore, față de 707 milioane la #513 în 5 ore.
- E **a doua noapte la rând** în care ora 3 cade în același loc, deci nu e întâmplare: ceva rămâne ținut în memoria plăcii de la o oră la alta.
- Modelele vechi (#477, #513, `gpt_24.pt`) au rămas neatinse: amprenta e la fel înainte și după.

## S86 în cifre (memoria plăcii)

| varianta | vârf la antrenare (PyTorch) | vârf pe placă (nvidia-smi) | încape? |
|---|---|---|---|
| AdamW, lot 4 × 24 | 3.706 MB | — | **nu**: memorie plină la examenul de la sfârșitul primei ore |
| Muon, lot 4 × 24 | **3.057 MB** | 6.373 MB | da |
| Muon, lot 6 × 16 | — | 6.273 MB | da |
| Muon, lot 12 × 8 | — | 6.303 MB | da |

- Vârful real de memorie nu e la antrenare, ci la **examenul de la sfârșitul fiecărei ore** (încă ~3,2 GB peste model).
- Întrebarea „crește memoria de la o oră la alta?” a rămas **fără răspuns sigur**: AdamW s-a oprit deja în prima oră. Asta o măsoară S87 azi.
- În cod s-a pus o pază: înainte de testul fiecărei ore, dacă placa trece de 6.700 MB, antrenarea se oprește curat.

## Verdictele

Toate pre-înregistrările nopții erau deja închise de executant, cu „Ce a ieșit” și „Verdictul”, deci n-am avut nimic de închis.
Le-am comparat cu pragurile scrise în ele și se potrivesc:

- **S85** (`docs/preinregistrari/2026-11-06_w2_mare_24f.md`): **NEMĂSURAT.** Pragurile (MAI BUN / LA FEL / MAI SLAB / STRICĂ) sunt
  pentru modelul de după 5 ore, care nu există. Nu se poate spune nimic despre întrebarea „la timp egal, modelul mare e mai bun decât #513?”.
- **S86** (`docs/preinregistrari/2026-11-07_memorie_mare.md`): **DA.** Pragul: Muon ≤ AdamW − 400 MB, adică ≤ 3.306 MB.
  A ieșit 3.057 MB (−649 MB), iar Muon nu a căzut și nu a trecut de 6.700 MB.
- **S77e** (`docs/preinregistrari/2026-11-06_w2_mare_24e.md`, aseară): **e1 ȚINE** (povești 0,4072 ≤ 0,4090; română 1,2120 ≤ 1,2127;
  cod 0,7286 ≤ 0,7320), **e2 AJUTĂ PUȚIN** (povești 0,4095, peste 0,4090, dar sub 0,4154). „ȚINE” înseamnă „aproape nu strică”, nu „învață mai bine”.

## Testele

Comanda: `CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -m pytest` (pe procesor, 5 min 03 s).

**1.278 trec, 1 sărit, 0 picate.**

## Ce urmează azi (din coadă)

- **S87** (azi ziua, 08:00–18:30, ~1–1,5 ore pe placă): verifică dacă memoria crește de la o oră la alta, cu Muon, în ordinea în
  care lucrează antrenarea reală, cu și fără golirea memoriei între ore. **Nu pornește dacă tu lucrezi la workstation.** Dacă nu
  apucă ziua, pornește la noapte de la 19:00.

## Ce aștept de la tine, Adrian

1. **Release-ul pentru #513** (din S83b; executantul nu l-a putut face, fiindcă cere aprobare). Rulează în `C:\Kronos\cyberspace`:

       gh release create kronos-kgr1-513 lucru/export/kronos_513_q8_0.kgr lucru/export/kronos_513_q8_0.kgr.sha256 --repo Adriancu91/cyberspace --title "Kronos #513 KGR1 Q8_0" --notes "SHA-256 66f734b3136206d1be8825b1188b1a90f0c5b00c2e19746547f327f9b95c5859, 110859008 octeți"

   Sau spune „nu e nevoie”, dacă OS-ul ia fișierul altfel.
2. **Trei întrebări din S86** (raportul `docs/rapoarte/2026-11-07_0406_S86_memorie_mare.md`):
   - facem o măsurare de 3 ore cu Muon înainte de o nouă noapte lungă?
   - trecem la stări „pe 8 biți” (economisesc memorie, dar cer o instalare)?
   - ștergem dosarul `lucru/memorie_mare/` (**9,8 GB**, rămas de la măsurare)? Fără „da”-ul tău nu se șterge.
3. **S84, curățenia de disc:** lista spune că se pot șterge 113 fișiere (71,5 GB) fără pierderi. Spune ce grupe se pot șterge (raportul
   `docs/rapoarte/2026-11-06_2304_S84_puncte_salvare.md`). Discul nu mai e urgent (86 GB liberi), dar scade.
4. **Autentificarea lui Claude Code** expira „între 6 și 9 noiembrie”. Dacă n-ai reînnoit-o, rulează pe workstation `claude setup-token`
   (recomandat pentru sarcinile fără om), altfel sarcinile automate se pot opri.
5. **Azi ziua:** dacă vrei să lucrezi la workstation, S87 așteaptă; dacă nu, lasă-l liber între 08:00 și 18:30.

Nimic nu s-a stricat peste noapte. Căderea S85 a fost oprită corect, iar cauza (memoria) e exact ce studiază S86 și S87.
