# Raportul de dimineață — vineri, 6 noiembrie 2026

*Scris la 06:46 de Claude Code, pornit automat de sarcina „Kronos raport dimineata”. Doar am citit jurnalele și am rulat testele;
n-am pornit nimic pe placă și n-am schimbat cod.*

## Pe scurt

- **Noaptea a rulat S77c:** prima noapte a lui Kronos „mare”, cu 24 de straturi (de două ori mai adânc decât #513). Trebuia să
  învețe **5 ore**. A mers doar **2 ore**: la începutul orei 3 (01:43) s-a umplut memoria plăcii video și ora 3 a fost anulată.
- **Verdictul: NEMĂSURAT.** Întrebarea pusă dinainte era despre modelul de la ora 5, iar acela nu există.
- Cu titlu informativ, modelul de la ora 2 (#518) e **mai slab** decât #513 și chiar decât punctul lui de pornire (#477).
- După S77c, executantul a mai terminat trei sarcini pe procesor și disc: S78, S79 și S81. Toate sunt GATA, iar supraveghetorul le-a verificat.
- **Testele:** 1.242 trec, 1 sărit, **1 picat**. Pică testul care cere cel puțin 40 GB liberi pe disc, iar discul C: are doar
  **31 GB** liberi.
- **Placa video** e liberă acum (446 MB, 28 °C). CONTINUUM, bucla automată, doar observă și nu pornește nimic.

## Ce a rulat noaptea

| ora | ce | cum s-a terminat |
|---|---|---|
| 5 nov 21:00 | Calculatorul a repornit. Paznicul a repornit interfața la 21:13. Sarcina veche de noapte `ws_w2` doar a reafișat rezultatul ei vechi, de 40 de ore, fără să antreneze nimic. | normal |
| 23:30 → 01:52 | **S77c**: antrenarea modelului de 24 de straturi, apoi examenele | **oprit** după ora 2 (memorie plină) |
| 02:29 → 02:37 | **S78**: am salvat proiectul Mini Brain (1,54 GB în arhivă, 0 diferențe la verificare) | gata |
| 02:59 → 03:13 | **S79**: am verificat arhiva de mutare (26,20 GB): nu conține nimic în plus. Plus o propunere de curățenie a discului, pe grupuri | gata, nimic șters |
| 03:29 → 03:36 | **S81**: antrenarea lungă iese acum cu „eroare” când o oră e anulată, ca lanțurile să nu meargă mai departe pe un model greșit (5 teste noi) | gata |
| 04:29 → 06:29 | Executantul a verificat coada din jumătate în jumătate de oră: nimic de pornit, fiindcă S76c și S77d sunt sarcini de zi | normal |

## S77c, în cifre

*„bpb” = câți biți îi trebuie modelului pentru o literă. **Mai mic = mai bine.***

| ora | model | scor pe povești (R2) | memorie ocupată de PyTorch |
|---|---|---|---|
| 1 | #517 | 0,4154 | 5.738 MB |
| 2 | #518 | 0,4155 | 4.708 MB |
| 3 | #519 | — | **anulat: memorie plină** (mai trebuiau 18 MB peste plafonul de 5.800 MB) |

Examenele, făcute pe #518 (ora 2) și refăcute pe loc pentru #513 și #477:

| măsura | #518 (mare, 2 ore) | #513 | #477 |
|---|---|---|---|
| română curat | **1,2268** | 1,2060 | 1,2097 |
| cod curat | **0,7413** | 0,7247 | 0,7270 |
| povești (R2) | **0,4155** | 0,4050 | 0,4060 |
| răspunsuri la instrucțiuni (R1) | 99,20 | 98,97 | — |
| R1 pe felurile vechi de întrebări | 100,0 | 99,68 | — |

- Placa a urcat cel mult la **6.433 MB** și **64 °C**, sub limitele de 7.000 MB și 83 °C. Memoria nu a fost umplută de placă
  în întregime, ci de plafonul pe care și-l pune singur programul de antrenare (5.800 MB).
- Modelul mare a văzut doar **113 milioane** de simboluri în 2 ore, față de 707 milioane la #513 în 5 ore (16 %).
- Cele trei modele vechi (#477, #513 și punctul de pornire `gpt_24.pt`) au rămas neatinse: amprenta lor e la fel înainte și după.

## Verdictul

Pre-înregistrarea (`docs/preinregistrari/2026-11-05_w2_mare_24b.md`) era deja închisă de executant la 02:05, cu secțiunile „Ce a
ieșit” și „Verdictul”. Am comparat verdictul cu pragurile scrise în ea și se potrivește:

**NEMĂSURAT.** Pragurile (MAI BUN / LA FEL / MAI SLAB / STRICĂ) sunt scrise pentru „ultimul model al liniei (ora 5)”. Antrenarea s-a
oprit după ora 2, așa că acel model nu există și pragurile nu se pot aplica.

Informativ, **nu** e verdictul: dacă aplicăm aceleași praguri pe #518, ies **STRICĂ**. Codul a ieșit 0,7413, peste limita de 0,7320,
iar poveștile 0,4155, peste limita de 0,4110. La română ar fi MAI SLAB (1,2268 > 1,2110). Cinstit spus: în 2 ore, modelul mare a
pierdut puțin din ce știa #477, iar curba nu coboară încă (0,4154 → 0,4155). Pre-înregistrarea avertiza că primele ore pot fi mai
rele și că o noapte scurtă nu spune dacă mărimea ajută. Cu doar 2 ore, nu putem spune nimic sigur.

**Examenul de conversație:** noaptea asta nu a avut, așa că azi nu sunt cele 20 de răspunsuri de verificat.

## Testele

Comanda: `CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -m pytest` (pe procesor, 4 min 58 s).

**1.242 trec, 1 sărit, 1 picat.**

A picat `teste/test_kronos_cod_tokenizer.py::test_unealta_cap_coada_fara_excluse_si_fara_validare_la_antrenare`. Cauza e cunoscută
de ieri: unealta se oprește singură când discul C: are sub 40 GB liberi. Acum C: are **31 GB liberi (94 % plin)**: erau 34 GB la
02:00 și 33,46 GB la S79. Nu e o greșeală în cod și nu am reparat nimic.

## Ce urmează azi (din coadă)

- **S76c** (de la 08:00, pe procesor): examenul cu instrucțiuni formulate altfel decât în exerciții.
- **S77d** (după S76c, pe placă): două ore scurte pentru modelul de 24 de straturi, cu rată de învățare mai mică, ca să vedem dacă
  problema e rata.

## Ce aștept de la tine, Adrian

1. **Discul C: (important).** Sunt doar 31 GB liberi și scad. Până nu se eliberează loc, testul de mai sus va pica, iar uneltele care
   cer 40 GB se vor opri singure. S79 are propunerea de curățenie pe grupuri, în
   `docs/rapoarte/2026-11-06_0311_S79_spatiu_workstation.md`: grupurile A+B eliberează **104 GB fără să se piardă nimic**.
   Supraveghetorul așteaptă să-i spui **ce grupuri se pot șterge**. Fără „da”-ul tău nu se șterge nimic.
2. **Autentificarea lui Claude Code**: ieri expira „între 6 și 9 noiembrie”. Dacă n-ai reînnoit-o încă, rulează pe workstation
   `claude setup-token` (recomandat pentru sarcinile fără om) sau `claude auth login`. Altfel sarcinile automate se pot opri chiar de azi.
3. **Modelul mare (24 de straturi):** nu ai nimic de făcut acum. Supraveghetorul a pus deja S77d pentru azi. Decizia pentru o nouă
   noapte (cu mai multă memorie de rezervă sau altă rată) vine după rezultatul S77d.
4. Rămâne deschisă întrebarea de ieri: îl poate înlocui #513 pe #477 în interfață, în pachetul KGR1 și în OS? Fără „da”-ul tău nu se
   mută nicăieri.

Nimic nu s-a stricat peste noapte și nimic nu cere reparat de urgență, în afară de spațiul pe disc.
