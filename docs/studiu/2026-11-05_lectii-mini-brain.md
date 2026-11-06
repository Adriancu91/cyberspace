# Lecții din vechiul proiect „Mini Brain” pentru Kronos

Scris de executant, 6 nov 2026 (sarcina S78, COMENZI.md C-77). Sursa: `C:\Users\Computer\Desktop\raport-test-ai-brain.md`
și arhiva copiată în `C:\Kronos\arhiva\mini-brain\` (vezi `CITESTE-MA.md` acolo). Documentul e doar de citit:
nu schimbă nimic în `kronos/`, în examen sau în paznic.

## 1. Un test mic de format înaintea oricărei rulări lungi

**Ce s-a întâmplat acolo:** în rularea finală V15, potrivirea exactă pe datele protejate a ieșit 0. O parte din vină nu
era a modelelor, ci a formatului: răspunsul gol era scris `"NONE"` (text) în antrenare și `null` la examen. O săptămână
de rulări a fost judecată pe o nepotrivire pe care un test de 5 rânduri ar fi prins-o.

**Pentru Kronos:** înainte de o noapte de antrenare sau un examen nou, 5–10 rânduri trec exact pe drumul examenului
(aceleași câmpuri, aceleași etichete, același fel de a scrie „gol”, aceleași numere) și se verifică cu ochiul și cu un
test. Kronos face deja ceva asemănător („proba notei” la S75, testul rapid de la pornirea orelor); regula e să nu sărim
peste el când formatul e nou (de exemplu numerele „1,091” → „091” găsite la S76a sunt exact acest fel de greșeală).

## 2. Păstrează doar câștigătorul; `*.pt` niciodată în Git

**Ce s-a întâmplat acolo:** 26 GB de puncte de salvare pilot/finale în `benchmarks\` și încă ~19,5 GB rămași blocați
în `.git` (21 de fișiere `.pt` intrate cândva în istorie, pe care niciun commit nu le mai folosește).

**Pentru Kronos:** `*.pt` rămâne în `.gitignore` (deja e: `lucru/` nu intră în Git). Un model care nu bate recordul nu
are nevoie să stea pe disc la nesfârșit: în jurnal rămân scorul și SHA-256; ștergerea se face doar cu „da”-ul lui
Adrian, pe grupuri (vezi S79 / C-76). Discul workstation-ului (~34 GB liberi azi) arată că problema e reală și aici.

## 3. Cel mult 2–3 încercări pe aceeași întrebare, apoi decizi

**Ce s-a întâmplat acolo:** 15 versiuni de pregătire/rulare (PREP/RUN) în 7 zile, aproape toate „BLOCKED” din motive de
procedură, până la un raport care spunea „nu mai porni nimic”. Rigoarea era bună; numărul de reluări nu.

**Pentru Kronos:** pre-înregistrarea rămâne, dar o întrebare primește cel mult 2–3 încercări (de exemplu o reluare după
o problemă tehnică, una cu o reparație). Dacă nici atunci nu iese un verdict, se scrie „nemăsurat / nu ajută” și se
trece mai departe sau se cere o idee nouă (cum e scris deja la S77d: „dacă niciuna nu ține → nu mai punem nopți pe 24
de straturi până la o idee nouă”).

## 4. PROPUNERE (fără cod): un modul „fapte verificate”

**Ce a mers acolo:** baza de cunoștințe geografică locală — 61.430 de entități, 258.309 afirmații cu sursă (GeoNames +
Natural Earth), 190/190 întrebări corecte, 0 fapte inventate, ~70 ms, „nu știu” când întrebarea e ambiguă. E singura
parte din Mini Brain care chiar a funcționat. Build-ul activ (`f8547edc…`) și datele brute (`raw\`) sunt acum în arhivă.

**Propunerea:** un modul înlocuibil în `module/` (cu `MANIFEST`, port și contract, ca orice modul), lângă modelul de
limbaj, care răspunde doar din date verificate și cu sursa lângă răspuns, iar altfel spune „nu știu”. S-ar potrivi cu
întrebările de tip „În ce județ e X?” / „Câți locuitori are X?” din setul R1. **Doar propunere:** nu am scris cod;
devine sarcină numai cu „da”-ul lui Adrian (iar datele GeoNames au licența lor, de verificat înainte).

## Bonus, scurt

- Mini Brain ținea examenul separat de model prin cod: o listă de câmpuri interzise (`answer`, `expected`, `correct`…)
  care nu au voie să ajungă la „creier” (`mini_ai_brain\core\contracts.py`). Kronos are deja paznicul și setul ascuns;
  ideea merită ținută minte dacă bucla de auto-îmbunătățire primește acces la mai multe date.
- Păstrarea rezultatelor negative și compararea cu o bază simplă au fost bune acolo și sunt deja obiceiuri aici.
