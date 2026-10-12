# Unde am ajuns (luni, 12 octombrie 2026): prima zi pe workstation

*Scris de Claude Code. Continuă `docs/UNDE_AM_AJUNS_2026-10-10.md` (scara și cifrele săptămânii rămân acolo). Cifrele
de azi vin din jurnalul Kronos și din documentele zilei: `WORKSTATION_prima_ora_2026-10-12.md`,
`WORKSTATION_etapa2_2026-10-12.md`, `DATE_surse.md`, `PORNIRE_automata.md`. Rezultatele negative sunt trecute la fel
ca cele bune.*

## Pe scurt

- **Mutarea e fidelă.** Pe workstation (RTX 3070 Ti, 8 GB), #262 și #295 dau aceleași cifre ca pe laptop, până la a
  șasea zecimală la val_bpb și identic la fapte noi.
- **Uneltele găsesc din nou modelele** (reparația aprobată în `kronos/`: `kronos/cai.py`).
- **Datele noi** (7 GB, licențe notate), **tokenizer-ul nou** (16.384) și **configurarea W2** sunt gata. W2 e nepornită.
- **Noaptea 3, prima pe workstation:** W1 (88 de milioane de parametri) de la zero, 10 ore, pornită de Windows la
  19:00. Întrebarea: ajută mărimea?
- **CONTINUUM v2** e scris și testat, nepornit.

## Ce merge

| Ce | Cifra |
|---|---|
| Testele | 585 în main (542 dimineața), 661 în `cyberspace-cod` (655 dimineața) |
| #262 cu unealta adevărată (`unelte/examen_fapte_nou.py --experiment 262`) | 59 de fapte noi (62 cu sinonime), ca pe laptop; rândul #296 |
| Reproducerea val_bpb | #262: 0,43043 (laptop 0,43043); #295: 0,42488 (laptop 0,42488) |
| Viteza și memoria W1, pe text adevărat | 6,8 pași pe secundă, 3.906 MB la paznic, 62 °C |
| Viteza și memoria W2, pe text adevărat | 5,9 pași pe secundă, 4.792 MB la paznic, 63 °C |
| Simbolurile TinyStories | împărțite în 4,6 minute (pe laptop, zeci de minute) |
| Pornirea programată, fără fereastră | încercată pe repetiție: merge |

## Ce nu merge sau nu e cum s-a cerut

- **The Stack smol nu s-a descărcat:** cere contul Hugging Face al lui Adrian și nu are licență pe fișă. Avem doar
  65 MB de cod, deci amestecul W2 are 1,6% cod, nu 15%.
- **`"moon"` cu ghilimele cu tot are 3 bucăți, nu „cel mult 2”.** Cuvântul e întreg (înainte era rupt), dar
  ghilimelele rămân bucăți separate.
- **Fabulele în română sunt foarte repetitive:** 22% duplicate exacte și un vocabular de ~4.000 de cuvinte.
- **W2 era la un pas de „memorie insuficientă” la examen** (7.874 MB din 8.192 pentru câteva secunde). Reparat în
  `module/model_gpt.py`; acum 6.324 MB. Probele de dimineață, pe simboluri la întâmplare, nu aveau cum să vadă asta.
- **După o repornire de Windows, nimic nu pornește până nu se loghează cineva.** Reluarea de după logare e făcută;
  logarea automată nu e activată (cere „da”-ul lui Adrian).
- **CONTINUUM v2 alege după o ordine fixă**, nu după un calcul al câștigului așteptat.
- **Ramura `kronos-cod`** a primit doar reparația modelelor și rândul din CLAUDE.md. Tokenizer-ul nou, datele și
  CONTINUUM v2 sunt doar în main.

## Ce e nou în proiect azi

- `kronos/cai.py` (aprobat): modelele din jurnal se găsesc și după mutare; cele noi se notează cu adresă relativă.
- `unelte/descarca_date_ws.py`, `curata_date_ws.py`: datele, cu licența recitită înainte de fiecare descărcare.
- `module/tokenizer_bpe.py`: regulile „ws” (numerele 0–999 întregi), lângă cele vechi, neschimbate.
- `unelte/antreneaza_tokenizer_ws.py`, `pregateste_amestec_ws.py`, `module/date_amestec.py`: tokenizer-ul și amestecul W2.
- `config/ws_w1.toml`, `config/ws_w2.toml`: liniile workstation-ului, cu paznicul la 7.000 MB și 83 °C.
- `unelte/noapte_ws.ps1`, `programeaza_noapte_ws.ps1`, `urmareste_placa.py`: pornirea nopții din Windows.
- `module/continuum/` + `config/continuum_ws.toml`: CONTINUUM v2.
- Rânduri noi în jurnalul Kronos, toate scrise de unelte: #296 (examenul pe #262), #297 și #299 (repetiția W1, linia
  „ws_w1_repetitie”), #298 și #300 (proba W2, linia „ws_w2_proba”). Liniile „ws_w1” și „ws_w2” erau neîncepute
  înainte de noapte.

## Noaptea 3 (12–13 octombrie): W1 de la zero

- Pre-înregistrarea: `docs/preinregistrari/2026-10-12_noaptea3_w1.md`, scrisă la 12:30.
- Se compară cu fapte-zero de pe laptop (#280–#286) la aceleași ore. Confirmat = la ora 7, val_bpb ≤ 0,4486 și fapte
  noi ≥ 55; infirmat = val_bpb ≥ 0,4886.
- Pornirea, memoria și temperatura din primele 15 minute: vezi mai jos, la „Pornirea nopții”.
- Dimineața: `python unelte/preinregistrare.py --inchide noaptea3_w1`, apoi verdictul și setul sacru pe modelul final.

## Deciziile pentru Adrian

1. **Pornirea automată** (`docs/PORNIRE_automata.md`): A (ca acum), B (logare automată cu ecranul blocat imediat) sau
   C (antrenarea fără logare). Recomand B, dacă la workstation ajung doar oameni de încredere, plus mai puține
   reporniri (actualizările Windows, BIOS, UPS).
2. **Linia de mâine noapte.** Variantele:
   - **(a)** W2 de la zero (tokenizer nou, engleză + română): linia nouă din plan. Cu 1,6% cod.
   - **(b)** W1 mai departe, încă 8 ore, dacă noaptea asta arată că încă învață.
   - **(c)** îl lași pe CONTINUUM v2 să aleagă între (a) și (b). Cu ordinea de acum alege (b) dacă W1 încă învață,
     altfel (a).
3. ~~The Stack smol~~ **rezolvat seara:** Adrian a acceptat termenii și a dat o cheie de citire. Amestecul W2 are acum
   15,1% cod Python cu licențe permisive (`docs/WORKSTATION_etapa2_2026-10-12.md`, la sfârșit).
4. **Fabulele:** cât din ele intră în antrenare (acum 20% din partea de română), știind că sunt repetitive.
5. **Ordinea lui CONTINUUM v2:** „continuă” înaintea „liniei noi” (cum e acum) sau invers.
6. **Ramura `kronos-cod`:** se unește cu main (ca școala de cod să primească tokenizer-ul nou) sau rămâne separată.

## Opririle bruște de după-amiază (aflate la 17:15, doar din jurnalele Windows)

- **Două opriri fără închidere curată**, amândouă cu placa și procesorul în repaus (nu rula nimic):
  1. între 14:01 (ultimul semn de viață) și 15:50, când calculatorul a pornit din nou. Nimeni nu s-a logat după
     pornirea de la 15:50;
  2. între 16:09 și ~17:00; Adrian l-a repornit la 17:04.
- **Ce nu a fost:** nu Windows Update (azi doar definiții de antivirus, fără nicio cerere de repornire); nu un ecran
  albastru (cod de eroare 0, niciun fișier de avarie); nicio eroare de componentă raportată de Windows (WHEA: zero);
  nu supraîncălzire de la lucru (nu rula nimic; placa e la 31 °C); discul e sănătos.
- **Ce rămâne:** curentul s-a întrerupt de la priză (pană, prelungitor, cablu) sau calculatorul s-a oprit singur
  (sursa lui de curent sau placa de bază). **Din Windows nu se pot deosebi.** Înainte de azi, calculatorul mersese
  4 zile fără oprire.
- **Nimic stricat:** Git curat și la zi în ambele foldere; jurnalul Kronos are 300 de rânduri întregi, primele 295
  neschimbate; modelele, simbolurile și tokenizer-ul sunt la locul lor; sarcinile din Task Scheduler au rămas.
- **Hotărât de Claude Code, după regula lui Adrian:** pornirea de la 19:00 și reluarea la logare au fost dezactivate
  (nu șterse) la 17:25, până hotărăște Adrian.
- **Hotărât de Adrian la 17:34: noaptea pornește.** Opririle au fost în repaus, nu sub efort. Sarcinile sunt din nou
  active. Dacă se mai oprește în timpul nopții, se notează ora și se reia de unde a rămas.
- **Ce ar lămuri cauza:** dacă în casă a căzut curentul (lumini, router, ceasuri); jurnalul din BIOS-ul Dell
  (F2 la pornire → System Logs → Power Events); ce putere are sursa (eticheta din carcasă: Precision 5820 vine cu
  425, 685 sau 950 W, iar placa video singură cere până la 290 W).

## Pornirea nopții

- **W1 a pornit singură la 19:00:01**, din Task Scheduler, fără fereastră (`lucru/noapte_ws_w1.log`).
- **Primele 15 minute** (`lucru/placa_noapte_w1.csv`, o măsurătoare la 5 secunde): temperatura maximă **63 °C**, stabilă
  de la minutul 3; toată placa **5.131 MB** din 8.192 (cu Windows cu tot); placa lucrează la 97%; ~241 W.
- Procesul antrenării folosește un singur nucleu de procesor; restul lucrului de seară e pe cel mult 12 fire, fără placă.
- Oprirea de siguranță e programată la 07:30; cele 10 ore ar trebui să se încheie pe la 05:30.
