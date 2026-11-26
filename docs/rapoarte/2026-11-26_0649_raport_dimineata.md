# Raportul de dimineață — joi, 26 noiembrie 2026

*Scris automat la 06:49 de sarcina „Kronos raport dimineata”, doar din citirea jurnalelor. N-am pornit nimic pe placă și
n-am schimbat cod.*

## Pe scurt

- **Noaptea n-a rulat nimic pe placa video.** Nu era nimic aprobat pentru placă. Nu există niciun model nou, deci nu am ce
  judeca. Nu a fost nici examen de conversație, așa că lipsesc cele 20 de răspunsuri.
- **Singura treabă de noapte a fost S140, pe procesor** (23:39–00:00). S-a terminat cum trebuie, iar supraveghetorul a
  verificat-o la 02:15. Rezultat: **bf16 nu strică învățarea**, adică modul de calcul mai rapid pe placă, cu numere mai
  puțin precise. Diferența e de −0,087 %, iar pragul era ±1 %.
- **Testele: 1.605 trec, 1 sărit, 0 picate.**
- **Placa e liberă:** 484 MB folosiți din 8.192, 29 °C, încărcare 1 %. Pe discul C sunt 136 GB liberi.
- **Noaptea n-a mai repornit calculatorul.** Ultima repornire a fost aseară la 22:04.

## Ce a rulat de ieri seară până acum

| ora | ce | cum s-a terminat |
|---|---|---|
| 25 nov 23:18 | supraveghetorul pune S140 în coadă (aprobat, doar procesor) | — |
| 23:29–23:39 | executantul: S140 „în lucru” și pre-înregistrarea `2026-11-25_banc_f32_vs_bf16_300.md`, urcată ÎNAINTE de rulări | commit 571f62d |
| 23:39:56–00:00:37 | S140: două antrenări scurte de câte 300 de pași din modelul #513, una cu numere F32 (precise), una cu bf16 | cod 0 la amândouă, fără opriri |
| 26 nov 02:07 | executantul: pre-înregistrarea închisă cu verdict, raportul `2026-11-26_0207_S140_banc_f32_vs_bf16.md` | commit b4b0593 |
| 02:15 | supraveghetorul verifică S140 și copiază banda pentru OS în hub | commit 560f1a3 |
| 02:29–06:29 | executantul trece la fiecare 30 de minute: nimic `aprobat` în coadă, nu pornește nimic | fără commit (corect) |

Cifrele S140, pe scurt (toate sunt în raportul de la 02:07):

- Loturile de text au fost identice la cele două rulări (aceeași amprentă SHA), deci comparația e cinstită.
- Media pierderii pe pașii 251–300: F32 **1,66611**, bf16 **1,66466** (−0,087 %). Pierderea arată cât de mult greșește
  modelul: mai mică e mai bine.
- Banda de toleranță pentru OS, adică diferența bf16 − F32 la pașii 1/10/50/100/200/300:
  **2,4e-5 · 3,8e-4 · 9,4e-4 · 1,4e-3 · 1,6e-3 · 2,7e-3**.
- Atenție, executantul a scris-o cinstit: de la un pas la altul diferența sare mult. Maximul e **5,1e-2** la pasul 291, iar
  12 pași din 300 trec de 7,2e-3. Toți cei 12 sunt după pasul 100.
- Pe procesor, bf16 e de 2 ori mai lent: 2.673 față de 1.311 milisecunde pe pas.
- Modelele, examenul și `kronos/` au rămas neatinse (SHA 21/21 identic).

## Verdictul nopții

- **Nu există o antrenare de noapte de judecat.** Ultimul experiment din jurnalul Kronos e tot #748, din 20 noiembrie, deci
  noaptea nu s-a adăugat nimic.
- **Pre-înregistrări:** cea pentru S140 (`2026-11-25_banc_f32_vs_bf16_300.md`) e deja închisă de executant, cu „Ce a ieșit”
  și „Verdictul”, judecate după pragurile ei: (a) VALID; (b) bf16 nu strică învățarea; (c) banda de mai sus. Nu e treaba mea
  s-o mai închid.
- **Pre-înregistrarea S131 (`2026-11-21_w2_mare_24zcj.md`) rămâne deschisă**, ca ieri. S131 n-a rulat, e în pauza C-156,
  și coada spune să nu fie închisă. N-am atins-o.
- **CONTINUUM** a rulat toată noaptea în „repaus”, cum trebuie. Doar observă, pentru că placa e a executantului. Ultimul ciclu
  e #11974, la 06:40.

## Testele

`CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -m pytest` → **1605 passed, 1 skipped** în 8 min 26 s. Nimic picat.

## Ce aștept de la tine

1. **Conectarea lui Claude Code expiră între 29 noiembrie și 2 decembrie** (cel mai devreme peste 3 zile). După aceea nu mai
   merge nicio rulare automată: nici executantul, nici supraveghetorul, nici raportul ăsta. Când ești la workstation,
   deschide o fereastră de comandă și rulează:
   `claude auth login`
2. **Git e tot în operația neterminată din 17 noiembrie** („rebase in progress”). De aceea actualizarea automată de la 06:40 a
   picat și azi, cu mesajul „You are not currently on a branch”. N-a stricat nimic: copia de aici e la zi cu GitHub. Ca s-o
   închei, rulează în `C:\Kronos\cyberspace`:
   `git -c core.editor=true rebase --continue`
3. **Repornirile:** după raportul de ieri, calculatorul a mai repornit de 7 ori ziua (10:53, 11:20, 14:20, 17:09, 20:20,
   21:07, 22:04). Noaptea nu. Din jurnale, niciuna nu pare să fi oprit o probă de pe placă: S135 B, S137 B și S139 B s-au
   terminat toate cu cod 0. Totuși, dacă ele vin de la testele OS-ului, ar fi bine să nu cadă peste probele de zi
   (07:00–23:00). Eu nu pot vedea de unde vin.
4. **În coadă nu e nimic aprobat.** Dacă vrei să meargă mai departe, sunt două variante:
   - **S138** (probele „Kronos v2”, ~5 h de placă) pornește doar cu „da”-ul tău;
   - sau aștepți următoarea propunere a supraveghetorului.
