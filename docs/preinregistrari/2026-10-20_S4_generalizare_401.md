# Pre-înregistrare: S4 (20 octombrie). #401 înțelege și întrebări puse altfel?

<!-- scrisa: 2026-10-20T10:56:00 -->
*Scrisă la 2026-10-20 10:56, înainte de rulare. După ce examenul a început, textul de mai jos nu se mai schimbă; la
final se adaugă doar „Ce a ieșit” și „Verdictul”.*

## Cine a ales

Sarcina **S4** din `plan/coada.md`, aprobată de supraveghetor pe 20 octombrie, la 10:50 (categoria „examene”). O face
Claude Code, ca executant de mână, la cererea lui Adrian. **Nicio antrenare, doar examen.**

## Întrebarea

Noaptea 10 a ieșit 50 din 50, dar întrebările de examen aveau aceleași tipare ca la antrenare. **Găsește #401 răspunsul
în text și când întrebarea e pusă altfel decât a învățat?**

## Examenul: 60 de întrebări noi, scrise de mână

Fișierul e `docs/conversatie/examen_generalizare_401.json`. Am scris întrebările pe textele din examenul pus deoparte al
nopții 10 (`date/conversatie/text/examen.json`), adică pe articole care nu intră în antrenare. Fiecare are câte 15:

- **(a) aceleași informații, altă formulare:** „Când a venit pe lume X?”, „Ce populație are X?”, „Cine este
  regizorul filmului X?”, „Cât de mare este X?”, „În care județ e X?”;
- **(b) tipuri care NU există în antrenare:** „În ce țară se află X?”, „Cu ce trupă a cântat X?”, „Pentru ce club
  joacă X?”, „Unde s-a născut X?”, „Ce meserie are X?”, „Câți membri are X?”, „Ce firmă a lansat X?”;
- **(c) da/nu:** 9 cu „Da.” și 6 cu „Nu.”, după text („S-a născut Cindy Crawford în 1966?”);
- **(d) fără răspuns în text, formulate altfel decât la antrenare:** „Cine cânta la chitară în trupa X?”, „Câte pagini
  are romanul X?”, „Ce suprafață are Parcul din Zastavna?”. Corect: „Nu scrie în text.”.

Am verificat cu un mic program că la (a) și (b) răspunsul se găsește în text.

## Ce rulează

`unelte/examen_conversatie.py --experiment 401 --examen docs/conversatie/examen_generalizare_401.json`, exact ca la
noaptea 10:

- formatul „Text: … / Întrebare: … / Răspuns:”;
- răspunsul fără întâmplare, cel mult 80 de bucăți, tăiat la primul rând nou;
- profesorul Qwen3-4B notează 1–10 față de referință;
- pe placă, cam 15–25 de minute.

## Ce înseamnă confirmat sau infirmat

Un răspuns e **corect** dacă profesorul îi dă **cel puțin 7 din 10**. La (d), e corect dacă spune „Nu scrie în text.”.

- **Confirmat:** **(a) ≥ 9 din 15 și (b) ≥ 6 din 15.**
- **Infirmat:** **(a) < 5 din 15.**
- Între ele: „parțial”.
- **(c) și (d), doar urmărite.** Urmăresc și câte „Nu scrie în text.” spune la (a), (b) și (c), unde răspunsul există.

## Așteptările mele, în cifre (scrise înainte)

- **(a): 8–12 din 15.** Cuvintele-cheie s-au schimbat, dar subiectul și bucata de copiat sunt aceleași. La „Când a
  venit pe lume” cred că răspunde cu anul (nota 7–9).
- **(b): 4–9 din 15.** E greu pentru că n-a văzut niciodată „Ce meserie are X?”. Cred că va copia prima propoziție (o
  definiție) în loc de bucata cerută.
- **(c): 3–8 din 15.** N-a văzut niciodată „Da.”/„Nu.” ca răspuns. Cred că va copia o bucată din text sau va spune „Nu
  scrie în text.”.
- **(d): 6–12 din 15.** Cele cu un tip pe care l-a învățat ca pozitiv (suprafața) sunt capcane.
- **„Nu scrie în text.” spus pe nedrept la (a)+(b)+(c): 3–10 din 45.**

## Ce ar infirma așteptările

- **(b) peste 12 din 15:** #401 a învățat să caute bucata potrivită pentru orice întrebare, nu doar tipare.
- **(a) sub 5 din 15:** a învățat doar tiparele de cuvinte, nu sensul întrebării.
- **(c) peste 10 din 15:** știe să compare o afirmație cu textul, fără să fi învățat asta.

## Ce a ieșit

<!-- inchisa: 2026-10-20T11:10 -->
Examenul a rulat 10:55–10:57 pe placă (`lucru/examen_conversatie/experiment_401_20261020_105728.json`). Profesorul a
notat toate cele 60 de răspunsuri.

| felul | corecte | „Nu scrie în text.” |
|---|---|---|
| (a) altă formulare | 7 din 15 | 8 din 15 (pe nedrept) |
| (b) tip nou | 3 din 15 | 8 din 15 (pe nedrept) |
| (c) da/nu | 2 din 15 | 6 din 15 (pe nedrept) |
| (d) fără răspuns, formulat altfel | 11 din 15 | 11 din 15 (corect) |

Nota medie: 4,68. „Nu scrie în text.” pe nedrept la (a)+(b)+(c): 22 din 45.

## Verdictul

**PARȚIAL.**

- Nu e confirmat: (a) are 7 din 15, sub pragul de 9, iar (b) are 3 din 15, sub pragul de 6.
- Nu e infirmat: (a) are 7, deci nu e sub 5.

Așteptările mele au ieșit astfel:

- (a): în plaja 8–12? Nu, cu unu sub ea.
- (b): în plaja 4–9? Nu, sub ea.
- (c): în plaja 3–8? Nu, sub ea.
- (d): în plaja 6–12? Da.
- „Nu scrie” pe nedrept: am scris 3–10, a ieșit 22. Aici am greșit cel mai tare.

#401 a învățat tiparele de cuvinte ale întrebărilor, nu sensul lor. Când formularea e alta, de obicei refuză. Raportul:
`docs/rapoarte/2026-10-20_1100_S4_generalizare_401.md`.
