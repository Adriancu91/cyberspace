# Raportul de dimineață — luni, 9 noiembrie 2026

*Scris automat de sarcina „Kronos raport dimineata”, la 06:46, fără om de față. Am doar citit jurnalele; n-am pornit nimic
pe placă și n-am schimbat cod.*

## Pe scurt

- **Noaptea a mers bine.** A rulat **S94b**: 5 rețete de antrenare, câte o oră fiecare, pe modelul mare (cel cu 24 de
  straturi). Toate s-au terminat curat, între 19:33 și 00:55. Niciuna n-a fost oprită de pază. Placa e liberă de la 00:58.
- **Verdictul: NU.** Modelul mic, cu 6 straturi, NU poate ghici ce rețetă e bună pentru modelul mare. Ordinea iese chiar
  pe dos: pe modelul mic câștigă rata de învățare mare, iar pe cel mare câștigă rata mică.
- **Testele:** 1.337 trec, 1 sărit, 0 picate.
- **Azi placa și calculatorul sunt ale tale** (testul sistemului de operare). La noapte, de la 19:00, pornește S95, dar
  numai dacă workstation-ul e din nou în Windows.

## Ce a rulat noaptea

**S94b** (sarcina S94 din coadă, pasul 4 din C-85). Întrebarea: dacă încercăm rețetele întâi pe un model mic și ieftin,
iese aceeași ordine ca pe modelul mare? „Rețetă” înseamnă aici setările antrenării, mai ales **rata de învățare**, adică
cât de mari sunt pașii cu care modelul își schimbă greutățile.

| # | rețeta | experiment | început–sfârșit | română (mai mic = mai bine) |
|---|---|---|---|---|
| 2 | rata ×0,5 | #542 | 20:38–21:42 | **1,2102** (cea mai bună) |
| 1 | bază | #540 | 19:34–20:38 | 1,2118 |
| 5 | încălzire ×2 | #548 | 23:51–00:55 | 1,2118 |
| 3 | rata ×2 | #544 | 21:43–22:46 | 1,2158 (strică puțin codul) |
| 4 | rata ×4 | #546 | 22:47–23:50 | 1,2232 (strică poveștile și codul) |

- Toate au pornit din aceeași copie a modelului mare. La pornire, scorul la română era **1,2096**, ca reperul #477 ✓.
- Nicio oră nu a coborât sub punctul de pornire. Asta era de așteptat: o oră e prea puțin pentru un model deja bun.
- Fiecare oră a fost urmată de examenele pe validări (#541, #543, #545, #547, #549, toate „măsurat”).
- **Siguranța:** memoria plăcii a ajuns cel mult la 6.426 MB (limita e 7.000), iar temperatura cel mult la 61 °C.
  Modelele vechi (#477, #513, #536, `gpt_24.pt`) au rămas neschimbate.

## Verdictul

Pre-înregistrarea nopții (`docs/preinregistrari/2026-11-08_avans_spearman.md`) a fost **închisă deja de executant la
01:05**, cu „Ce a ieșit” și „Verdictul”. N-am mai închis-o încă o dată. Am verificat verdictul după pragurile scrise în ea:

- Pragurile: **DA** dacă potrivirea ρ (Spearman, o măsură de la −1 la +1 a cât de asemănătoare sunt două clasamente)
  e ≥ 0,7 și câștigătorul de pe modelul mic e în primele 2 pe cel mare; **NU** dacă ρ ≤ 0,3; altfel NECLAR.
- Am refăcut calculul pe ranguri (mic: 3,5 / 5 / 2 / 1 / 3,5; mare: 2 / 2 / 4 / 5 / 2): **ρ = −0,92**. Iese la fel ca
  la executant.
- Câștigătorul de pe modelul mic (rata ×4) iese **ultimul** pe cel mare.
- **ρ ≤ 0,3, deci NU.** Verdictul executantului se potrivește cu pragurile.

Ce înseamnă: rețetele pentru modelul mare trebuie încercate direct pe modelul mare. Lecția utilă: la modelul mare, rata
mică strică cel mai puțin. De aceea S95 de la noapte folosește rata ×0,5.

## Examenul de conversație

Noaptea n-a avut examen de conversație, deci azi nu sunt cele 20 de răspunsuri de verificat. Ultima intrare din
`lucru/noapte_conversatie.log` e din 19 octombrie.

## Restul stării

- **CONTINUUM** (programul care observă de pe margine) a stat în repaus toată noaptea, cum trebuie. Ultimul lui ciclu e
  #7194, la 06:40: „placa e a executantului, nu pornesc nimic, doar observ”.
- **Executantul** a trecut la 05:28, 05:58 și 06:28. N-a avut nimic de făcut: S95 e pentru noaptea 9→10, iar S96 pentru
  marți.
- **Supraveghetorul** a verificat S94 la 02:15 (ρ −0,92, NU) și a aprobat **S95** și **S96**.
- **Placa acum:** 452 MB folosiți, 24 °C, nicio antrenare pornită.
- **Discul C:** 56 GB liberi (89 % plin). Ieri erau 75 GB; cele 5 modele noi au cam 110 MB fiecare, deci restul vine
  probabil din fișierele de lucru ale celor 5 linii (`lucru/avans_s94_mare_*`). Încă e peste pragul de 20 GB.
- **Un amănunt tehnic, nu urgent:** la fiecare oră din noaptea asta, dar și la S89 (#532–#536), în jurnalul Kronos apare
  o „eroare după examen”: memoria plăcii s-a umplut la un pas făcut după examen. Modelele s-au salvat și notele există,
  deci rezultatele nopții nu sunt afectate. Nu l-am găsit pomenit în rapoartele de până acum, așa că îl semnalez
  supraveghetorului: S95 merge pe același drum.
- **Git:** de ieri seară sunt 4 commit-uri (pornirea S94b, verificarea de la 20:15, S94 `gata` la 01:06, verificarea
  supraveghetorului de la 02:15). Totul e urcat pe GitHub.

## Testele

`CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -m pytest -q`: **1.337 trec, 1 sărit, 0 picate** (5 min 27 s).

## Ce aștept de la tine

1. **Testul OS de azi:** după ce termini, lasă workstation-ul pornit în Windows. Altfel S95 nu poate porni la noapte
   (de la 19:00, cel târziu la 00:30). Dacă mai lucrezi seara pe el, scrie o notă în coadă sau în `COMENZI.md`, ca
   executantul să nu ocupe placa.
2. **Autentificarea lui Claude Code** trebuia să expire între 6 și 9 noiembrie, iar azi e ultima zi. Dacă n-ai reînnoit-o
   încă, rulează pe workstation:
   `claude setup-token`
   Altfel sarcinile automate de la noapte (executantul, raportul de mâine) se pot opri.
3. **Release-ul #513 pe GitHub**, când ești la workstation. Nu e urgent.
4. **S88:** alegi cum se șterg cele 33,4 GB de modele intermediare. Ori rulezi tu comanda din
   `docs/rapoarte/2026-11-07_1040_S88_stergere.md`, ori îi dai executantului o excepție scrisă. Discul scade (56 GB
   liberi), deci devine mai util decât ieri, dar tot nu e urgent.
