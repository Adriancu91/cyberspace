# Pre-înregistrare: S76c, C-64 R1 pasul 3 — #513 urmează și instrucțiuni FORMULATE ALTFEL decât în antrenare? (examen pe procesor, fără antrenare)

<!-- scrisa: 2026-11-06T08:34:33 -->
*Scrisă la 2026-11-06 08:34–08:45, la S76c, ÎNAINTE ca vreun model să fi văzut setul nou (`ascuns_reformulat.jsonl` a fost făcut
la 08:31, doar cu reguli; proba vitezei pe procesor s-a făcut pe 6 întrebări din setul VECHI S76a, nu pe cel nou). După ce rularea a
început, textul de mai jos nu se mai schimbă; la închidere se adaugă doar „Ce a ieșit” și „Verdictul”
(`python unelte/preinregistrare.py --inchide s76c_reformulat`).*

## Cine a ales

Adrian (COMENZI.md **C-64**, 4 nov 2026 11:30, partea R1); supraveghetorul a scris sarcina și pragurile (5 nov 2026 07:40, granițele 2,
3 și 5). Pragurile de mai jos sunt cele din `plan/coada.md` (S76c), **copiate exact**. Unealta, setul și această pre-înregistrare:
Claude Code (executantul).

## Întrebarea

S76b = AJUTĂ (#513: R1 pe instrucțiuni **98,97** față de #477 37,47), dar setul ascuns S76a are **aceleași 8 șabloane** ca antrenarea.
**#513 urmează instrucțiunile și când sunt formulate altfel decât în antrenare, sau doar a copiat șabloanele?**

## Setul (gata, făcut doar cu reguli, înainte de orice model)

- `lucru/romana_raspunsuri/ascuns_reformulat.jsonl` (SHA-256 `ec6900f2bf286f460c19d2d3de173ae8c6ae1ddd70f52f71be976a173a8b7646`),
  cu `unelte/romana_raspunsuri.py reformulat` (sămânța 7603) → `info_reformulat.json`.
- **290** de instrucțiuni = toate instrucțiunile setului ascuns S76a (articole care nu intră deloc în antrenare), cu **aceleași
  referințe și chei**, doar întrebarea spusă altfel: instr_propozitie 40, instr_rezuma 40, instr_an 40, instr_nume 40, instr_numar 40,
  instr_judet_tara 40, instr_da_nu 25, instr_nu_scrie 25 (cerința: ≥ 200, ≥ 20 pe fel, ≥ 15 la da/nu și nu_scrie ✓).
- **23 de formulări noi** (3–6 pe fel, ≥ 2 cerute ✓), de exemplu „Când {…}? Răspunde numai cu anul.”, „{X} — județul și țara?”,
  „Despre ce e vorba în text? Răspunde într-o singură frază.”, „Te rog, numai „da” sau „nu”: {…}”.
- Verificări: **0** întrebări din `antrenare.jsonl` (23.251) se potrivesc cu vreo formulare nouă (câmpurile = orice text); **0** întrebări
  noi identice cu antrenarea; **0** identice cu S76a. `antrenare.jsonl` și `ascuns.jsonl` neschimbate (SHA-256 înainte = după:
  `3d8ac5a3…00b0`, `3a333657…c9e`).
- **Numărul reparat:** la „locuitori” numărul se citește întreg („1,091” = „1.091” = „1091”, test nou); în setul ascuns o singură pereche
  avea cheia tăiată: Dunedin, „122,000” → cheia S76a „000”, acum „122.000”. 30 de perechi „locuitori” se notează cu numărul întreg.
- Proba notei pe setul nou (`proba_nota_reformulat.json`): referințele 100 % corect, gol 0 %, răspunsul altei întrebări 1,72 % ✓.

## Ce rulează

Prin cascadă (`cascada.py porneste S76c -- …`), pe procesor (`CUDA_VISIBLE_DEVICES=-1`, `--dispozitiv cpu`), fără placă, pe rând:
1. `python unelte/romana_raspunsuri.py reper --experiment 477 --dispozitiv cpu --set lucru/romana_raspunsuri/ascuns_reformulat.jsonl
   --iesire lucru/romana_raspunsuri/reformulat_477` (**A**);
2. `python unelte/romana_raspunsuri.py reper --experiment 513 --dispozitiv cpu --set lucru/romana_raspunsuri/ascuns_reformulat.jsonl
   --iesire lucru/romana_raspunsuri/reformulat_513` (**B**).

Aceleași setări ca în S76a/S76b: fără întâmplare (cea mai probabilă bucată), cel mult 64 de simboluri, aceeași notă. Greutățile doar
citite (SHA-256 înainte = după, scris în `nota.json`). O singură rulare; `reper` refuză să refacă o notă existentă. Durata estimată:
~3,8 s pe întrebare pe procesor → ~18 min pe model, ~40 min în total.

## Măsura

**R1 pe instrucțiunile reformulate** = `instructiuni.R1` din `reformulat_477/nota.json` (A) și `reformulat_513/nota.json` (B).

## Pragurile (din coadă, S76c, cuvânt cu cuvânt)

- **URMEAZĂ INSTRUCȚIUNI:** B ≥ A + **20** și B ≥ **70**.
- **PARȚIAL:** B ≥ A + **10**, dar nu URMEAZĂ.
- **DOAR ȘABLOANELE:** B < A + **10**.
- Informativ: R1 și „corect” pe fiecare fel, A și B; diferența B față de cifra lui pe setul S76a (98,97); `limba_curata_min2`; și nota
  setului S76a re-calculată cu numărul reparat (doar perechea afectată, fără model nou).

Cum le citesc (scris acum): „≥” include egalul (B = A + 20 și B = 70 → URMEAZĂ; B = A + 10 → PARȚIAL). Cifrele sunt cele cu două zecimale
din `nota.json`, fără rotunjire suplimentară.

Informativ deja calculat (fără model nou, pe răspunsurile vechi): nota S76a re-calculată cu perechea Dunedin reparată rămâne **37,47** (#477,
răspunsese „Nu.”) și **98,97** (#513, răspunsese „122.”) — ambele greșite și cu cheia veche, și cu cea nouă.

## Să nu uite

- Formulările noi sunt tot ale mele, făcute după aceleași 8 feluri, iar referințele sunt aceleași: setul măsoară „aceeași cerere, alte
  cuvinte”, nu instrucțiuni de alt fel. URMEAZĂ nu înseamnă „înțelege orice instrucțiune”.
- Unele formulări noi seamănă cu felurile VECHI pe care #477 le știe perfect („Câți locuitori are X? …”, „În ce an … ? …”, „Cine a regizat
  X? …”, „Da sau nu: …”). Deci **A poate urca mult față de 37,47** — pragul e relativ la A tocmai de aceea.
- „Rezumă” / „Spune într-o propoziție” se notează după cheie (un cuvânt din prima propoziție + subiectul): nota e îngăduitoare acolo.
- Numerele „locuitori” se notează acum citite întreg (și „122,000” e corect): puțin mai îngăduitor decât S76a la 30 de perechi; la fel
  pentru A și B.
- O singură rulare, determinist; NECLAR nu există aici: orice rezultat intră într-unul din cele trei praguri.
- #513 **nu** înlocuiește #477 nicăieri fără „da”-ul lui Adrian. Nu ating `kronos/`, `module/`, examenul, paznicul, jurnalul,
  #477/#459/#513 (doar citire), seturile S76a. Nimic descărcat, instalat sau șters.

## Așteptările, în cifre

- **A (#477): ~50** R1 pe instrucțiuni reformulate (mai mult decât 37,47 pe S76a, fiindcă multe formulări noi sunt întrebări pe care le
  știe din felurile vechi: an, nume, locuitori, da/nu ~70–90; „Rezumă”/„propoziție”/„județul și țara” ~20–35).
- **B (#513): ~78** (scade de la 98,97; cel mai bine la an/nume/da-nu ~90, cel mai slab la „Descrie pe scurt…”, „Despre ce e vorba…” și
  „X — județul și țara?” ~55–65).
- Diferența B − A **~28**. Șansele: URMEAZĂ ~50 %, PARȚIAL ~30 %, DOAR ȘABLOANELE ~20 %.
- Durata: ~40 min pe procesor, fără căderi.

## Ce ar infirma așteptările

- B < A + 10 (DOAR ȘABLOANELE): #513 a învățat cele 8 șabloane, nu cererea din spatele lor.
- B ≥ 90 și A ≤ 40: generalizarea e mai bună decât credeam, iar #477 nu se folosește de felurile vechi.
- A ≥ 65: formulările noi sunt prea aproape de felurile vechi, iar setul măsoară mai mult „întrebare veche” decât „instrucțiune nouă”.

## Ce a ieșit

*Adăugat la 2026-11-06 09:15, din jurnalul Kronos (lucru/jurnal/experimente.jsonl) și din jurnalul CONTINUUM pe bune. Verdictul se scrie dedesubt.*

Niciun experiment Kronos în perioada asta.

Niciun ciclu CONTINUUM pe bune în perioada asta.

Cifrele (examen, nu antrenare; lanțul `lucru/cascada/S76c_proba/s76c.py`, prin cascadă, 08:35–09:10, cod 0, pe procesor; set
`ec6900f2…7646` verificat în ambele `nota.json`; SHA-256 #477 și #513 înainte = după ✓):

| măsura | A (#477) | B (#513) |
|---|---|---|
| **R1 pe instrucțiunile reformulate (290)** | **61,38** | **83,22** |
| corect | 47,24 % | 74,83 % |
| în temă | 53,79 % | 79,66 % |
| limbă curată | 83,10 % | 95,17 % |
| `limba_curata_min2` | 67,59 % | 86,21 % |
| durata | 1.011 s | 1.067 s |

R1 pe fel (A / B; în paranteză B pe setul S76a): instr_an 78,33 / 80,00 (100); instr_da_nu 100 / 100 (100); instr_judet_tara 37,50 /
**38,33** (99,17); instr_nu_scrie 96,00 / 100 (100); instr_numar 67,50 / 83,33 (95,83); instr_nume 77,50 / 98,33 (97,50);
instr_propozitie 39,17 / 100 (100); instr_rezuma 22,50 / 78,33 (100).

B pe setul nou față de S76a: 83,22 vs 98,97 (−15,75).

## Verdictul

**URMEAZĂ INSTRUCȚIUNI** (strict după pragurile de mai sus): B = 83,22 ≥ A + 20 = 81,38 și B = 83,22 ≥ 70. La limită: cu **1,84**
puncte peste pragul relativ.

Față de așteptări: A ~50 → 61,38 (mai sus, dar sub 65, deci nu se declanșează „setul prea aproape de felurile vechi”); B ~78 → 83,22;
diferența ~28 → 21,84. Nu se infirmă nimic din ce am scris, dar diferența e mai mică decât credeam.

Citirea (conform „Să nu uite”): #513 urmează cererile spuse altfel la nume, propoziție, rezumat (mai puțin la „Despre ce e vorba în text?”
1/13) și număr, dar **„județul și țara” spus altfel cade complet** (B 7,5 % corect, ca #477: 0 %) — răspunde „Nu.”, „În județul X.” fără
țară sau „Nu scrie în text.”. La formulări mai neobișnuite („Populația din X, în cifre?”, „Anul în care … — doar cifrele”) ambele
modele spun des „Nu scrie în text.”. URMEAZĂ e aici „aceeași cerere, alte cuvinte”, nu „orice instrucțiune”.
