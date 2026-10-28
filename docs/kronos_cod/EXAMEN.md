# Kronos-Cod: examenul de cod (scris la S41, 28 octombrie 2026, înainte de date și de antrenare)

- Unealta: `unelte/kronos_cod/examen_cod.py`; cutia în care rulează răspunsurile: `unelte/kronos_cod/cutie.py`.
- 20 de șabloane scrise de mână (niciunul de la un LLM străin), fiecare cu variante (alți parametri, alt nume de funcție).
  Enunțurile sunt în engleză (antetul funcției + docstring), cum e codul pe care va învăța modelul.
- **Setul de probă**: sămânța 0, 20 de probleme (câte una pe șablon), pentru teste și exemple; se poate regenera oricând.
- **Setul ascuns**: generat O SINGURĂ DATĂ pe 28 octombrie 2026, cu o sămânță aleasă la întâmplare, ținută doar în
  `lucru/kronos_cod/examen_ascuns/` (nu în Git). Nu conține variantele setului de probă.
  - **200 de probleme** (20 de șabloane × 10 variante), 4–8 teste pe problemă
  - **SHA-256 al `probleme.jsonl`: `90fc64cdebefc143f414474170eb9e9c936506204f9abfe0cff0268ddbdc3749`**
  - Verificat în cutie: referințele trec 200/200 (100 %), corpul gol (`pass`) 0/200, `return None` 0/200.
- Nota: pass@1 și pass@10, cu estimatorul fără deplasare: n răspunsuri pe problemă, c corecte,
  pass@k = 1 − C(n − c, k) / C(n, k). Un răspuns e corect doar dacă trec toate testele și cutia nu a blocat nimic.
- Setul ascuns se folosește doar ca măsură; nimic nu se alege sau se reglează pe el. Pragurile pentru etapa 2 le scrie
  supraveghetorul înainte de orice antrenare.
- Atenție: șabloanele sunt în Git, deci „ascuns” înseamnă că variantele exacte nu se văd, nu că felul problemelor e
  secret. Datele de antrenare vin din cod publicat înainte de 2021/2022, deci nu pot conține acest depozit.
