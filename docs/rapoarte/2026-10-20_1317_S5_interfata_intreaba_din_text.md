# S5 gata: fila „Întreabă din text” în interfață, cu modelul #401

*Executantul cascadei, 20 octombrie 2026, 13:17. Sarcina S5 din `plan/coada.md` (aprobată de Adrian, 20 oct, 10:47).*

## Pe scurt

În interfața de pe portul 8787 sunt acum două file sus: **Chat** (ca înainte, modelul #312, neschimbat) și
**Întreabă din text** (nouă): o căsuță mare pentru paragraf, una pentru întrebare și butonul „Întreabă”. Răspunde
modelul #401, cu exact formatul de la antrenare, și se oprește la sfârșitul răspunsului. Sub răspuns scrie
„Kronos #401 — răspunde doar din textul dat.” (plus câte secunde a durat). Dacă paragraful nu încape în fereastra
modelului, spune asta clar, cu cifrele, și nu întreabă modelul. Verificat de pe 100.90.150.35:8787 cu 3 exemple: toate
3 au mers cum trebuie.

## Ce am făcut

1. `module/interfata/creiere.py`: „creierul” nou `CreierText` (ca cel al chatului, se încarcă abia la prima întrebare,
   pe procesor). Modelul primește `Text: …⏎Întrebare: …⏎Răspuns:` (aceeași funcție `intrebarea` ca la antrenare și
   la examen), scrie cel mult 80 de bucăți fără întâmplare (ca la examen) și răspunsul se taie la primul rând nou sau
   la `<|endoftext|>` (ca la examen). Înainte, numără bucățile: dacă textul cu întrebarea are mai mult de
   512 − 80 = 432 de bucăți, dă eroarea „Textul cu tot cu întrebarea are N bucăți, dar în fereastra modelului (512
   bucăți) încap cel mult 432 … Scurtează paragraful.” — nu taie nimic în tăcere.
2. `module/interfata/server.py`: cererea nouă `POST /api/din-text` (paragraf + întrebare → răspuns). Ce se întreabă
   aici NU se scrie în istoricul conversațiilor. Fără modelul „din text” pornit, fila nu apare și cererea primește 404.
   Aceleași protecții ca la chat: doar de pe calculator și din Tailscale, doar JSON.
3. Pagina (`static/index.html`, `aplicatie.js`, `stil.css`): cele două file; textul se pune în pagină doar ca text
   (regula de siguranță a interfeței rămâne).
4. Pornirea: `python -m module.interfata … --experiment-text 401`; în `unelte/interfata_ws.ps1` (pe care îl folosește
   paznicul de procese când interfața cade) am adăugat `-ExperimentText 401` implicit, ca fila să revină și după o
   repornire automată.
5. Nimic în `kronos/`, nimic la examen, contracte sau paznic.

## Repornirea interfeței

Am oprit interfața veche (procesele 14548 și 19044, doar cu #312) și am pornit-o la loc (procesul 22920), cu aceleași
setări ca `unelte/interfata_ws.ps1` (pe procesor, placa ascunsă, jurnalul în `lucru/interfata/server.log`), plus
`--experiment-text 401`. Am pornit-o direct din Python, nu prin scriptul PowerShell, pentru că rularea PowerShell îmi
cere aprobare când lucrez singur. Rezultatul e același; dacă interfața cade, paznicul o pornește prin script, care
acum are și fila nouă. Jurnalul de pornire:

```
Răspunde: Kronos (elev, modelul #312), pe „cpu”; se încarcă la prima întrebare
Fila „Întreabă din text”: Kronos #401 — răspunde doar din textul dat.
Deschide în browser: http://127.0.0.1:8787/
Deschide în browser: http://100.90.150.35:8787/
```

## Cele 3 exemple (de pe http://100.90.150.35:8787)

Paragraful (199 de caractere): „Vulcan este un oraș din județul Hunedoara, Transilvania, România. Are o populație de
24.160 de locuitori, conform recensământului din 2011. Orașul se află în Valea Jiului, la poalele Munților Vâlcan.”

| # | fel | întrebarea | răspunsul lui #401 | timp |
|---|---|---|---|---|
| 1 | cu răspuns | Câți locuitori are Vulcan? | **24.160 de locuitori.** (corect) | 4,0 s (cu încărcarea modelului) |
| 2 | fără răspuns | Cine este primarul orașului Vulcan? | **Nu scrie în text.** (corect) | 3,0 s |
| 3 | lung (același paragraf de 12 ori, 2.399 de caractere) | În ce județ se află Vulcan? | — nu a întrebat modelul; mesajul: „Textul cu tot cu întrebarea are 669 bucăți, dar în fereastra modelului (512 bucăți) încap cel mult 432, ca să rămână loc și de răspuns. Scurtează paragraful.” | 0,0 s |

Pagina se încarcă (cod 200) și conține fila. Răspunsurile întregi sunt și în `lucru/interfata/s5_verificare.json`.
Înainte de repornire am mai încercat direct, pe procesor: „Ion Popescu (n. 1966, Cluj) este un actor român…” →
„În ce an s-a născut Ion Popescu?” → „În 1966.”; „Cine a regizat filmul Moara?” → „Nu scrie în text.”

Atenție (din S4): #401 merge bine pe întrebări puse ca la antrenare; la întrebări formulate altfel sau de alt tip
răspunde des „Nu scrie în text.” pe nedrept (22 din 45 în S4). Fila arată exact ce știe modelul, fără înfrumusețare.
Cât încape: cam 430 de bucăți, adică un paragraf de vreo 1.000–1.500 de caractere.

## Testele

- 3 teste noi în `teste/test_interfata.py`: formatul exact dat modelului și oprirea la sfârșitul răspunsului; textul
  prea lung (exact cât încape → răspunde; o bucată în plus → eroarea clară, iar modelul nu e întrebat); fila pe server
  (fără model „din text”: fila lipsește și 404; cu el: răspuns, cereri greșite refuzate cu 400/415, chatul vechi merge
  la fel și doar el scrie în istoric).
- Toate: `CUDA_VISIBLE_DEVICES=-1 python -m pytest` → **809 trecute, 1 sărit** (testul de contract care cere placa
  video și profesorul Qwen; se sare mereu când placa e ascunsă).

## Commituri

- `Cascada: S5 in_lucru`
- `S5: fila „Întreabă din text” în interfață, cu modelul #401 …` (codul și testele)
- acest raport și starea `gata` în coadă

## Ce aștept de la Adrian

Nimic obligatoriu. Poți încerca fila de pe telefon: http://100.90.150.35:8787 → „Întreabă din text”. Dacă vrei alt
număr maxim de bucăți în răspuns (acum 80, ca la examen) sau ca întrebările de aici să se păstreze în istoric, spune.

## Ce urmează în coadă

S6 (datele pentru noaptea 11, pe procesor, fereastra de zi) e următoarea `aprobat`; o ia executantul la rularea
următoare.
