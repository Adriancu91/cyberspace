# Pre-înregistrare: S63, a doua noapte pe linia `cod_c1` (orele 11–20, din `lucru/cod_c1/gpt.pt`)

<!-- scrisa: 2026-11-02T11:38:00 -->
*Scrisă la 2026-11-02 11:38, la S63, ÎNAINTE de antrenare și de examene (nimic din S63 n-a pornit pe placă; `lucru/kronos_cod/s63/`
nu există — verificat la 11:37). Setul ascuns nou e deja făcut (pasul 2 al deciziei setului), dar nu l-am citit și nu l-am
arătat; știu doar N și împărțirea pe șabloane. După ce antrenarea a început, textul de mai jos nu se mai schimbă; la închidere
se adaugă doar „Ce a ieșit” și „Verdictul” (`python unelte/preinregistrare.py --inchide cod_c1_noaptea2`).*

## Cine a ales

Adrian, „pornește acum sau cât de curând S63” (2 nov 2026 08:46, COMENZI.md C-56), fereastra oricând (și ziua). Setul ascuns =
**varianta (a)**, fără nicio suprapunere (supraveghetorul, 2 nov 11:20, granițele 2 și 5; restul sarcinii neschimbat).
Pragurile: propuse de supraveghetor, rescrise pe N-ul real după regula din coadă. Această pre-înregistrare: Claude Code (executantul).

## Întrebarea

A doua noapte pe aceeași linie (încă 10 ore din starea de după ora 10 a S58) mai aduce un câștig clar — **biți pe octet pe
validarea întreagă ≤ 0,494 (cel puțin 0,02 sub 0,5141) și pass@10 ≥ 3 % pe un set ascuns nou, nevăzut** — sau linia a ajuns la
platou?

## Ce rulează

Un singur lanț, prin `unelte/cascada.py porneste S63 -- python lucru/cascada/S63_proba/s63.py` (refuză să se repete):

1. **Antrenarea:** `python unelte/antrenare_lunga.py --config config/cod_c1_init002.toml --ore 20 --inceput "def "`.
   Jurnalul are deja 10 ore pe `cod_c1` (#480–#489), deci rulează **orele 11–20**, continuând din `lucru/cod_c1/gpt.pt`
   (starea de după #489). În log trebuie să apară „Antrenarea lungă: orele 11–20”; dacă apare „orele 1–…” sau starea lipsește
   → `oprit`. Aceeași configurare ca S58 (C-50), neschimbată.
   **Acceptat, nu se schimbă configurarea:** `durata_scaderii_secunde = 36000` s-a terminat la ora 10, așa că orele 11–20
   rulează cu rata **fixă 6·10⁻⁵** (10 % din maxim), fără încălzire nouă.
2. **Examenele, o singură dată, pe ultima stare a liniei (după ora 20, nu se alege ora după rezultat)**, cu uneltele reparate la S62
   (`--lot 2 --memorie-max 6500`; plus plasa lanțului la 6.900 MB / 82 °C):
   (i) biți pe octet pe validarea întreagă de 5.686 fișiere (tot + Python / Rust / C), `examen_validare.py model --stare lucru/cod_c1/gpt.pt`;
   (ii) pass@1 și pass@10 pe **setul ascuns nou** `lucru/kronos_cod/ascuns2` (`examen_cod.py model --set ascuns --dosar lucru/kronos_cod/ascuns2`,
   10 corpuri pe problemă, temperatura 0,8, sămânța 0, oprire la ieșirea din funcție sau la 256 de simboluri; apoi `noteaza --dosar
   lucru/kronos_cod/ascuns2`);
   (iii) aceleași setări pe setul de probă (20 de probleme), doar ca informație (nu intră în verdict).

## Setul ascuns nou (varianta (a))

`examen_cod.py ascuns --dosar lucru/kronos_cod/ascuns2 --exclude-dosar lucru/kronos_cod/examen_ascuns --max-pe-sablon 10`
(sămânța secretă aleasă de unealtă). Nicio variantă din setul de probă sau din setul ascuns S58. **N = 163** de probleme
(SHA-256 2508e943…965d), referințele trec 163/163, corpul gol 0/163. Pe șabloane: s01 10, s02 10, s03 5, s04 10, s05 10, s06 10,
s07 3, s08 10, s09 10, s10 7, s11 10, s12 10, s13 5, s14 10, s15 10, s16 4, s17 5, s18 9, s19 5, s20 10.

## Pragurile (din coadă, cu N = 163)

- **CONTINUĂ** = biți/octet ≤ **0,494** **și** pass@10 ≥ **⌈0,03 × 163⌉ = 5** (adică ≥ 5/163);
- **PLATOU** = biți/octet > **0,504** **și** pass@10 ≤ **⌊0,015 × 163⌋ = 2** (adică ≤ 2/163);
- altfel **NECLAR**.

Cum le citesc (scris acum): „biți/octet” = cifra pe **toată** validarea de 5.686 fișiere din (i) (nu examenul orar de 1.000 de
fișiere, nu un singur limbaj). „pass@10 ≥ 5” = suma pe probleme a estimatorului pass@10 din `noteaza` (n = 10, deci 1 dacă măcar un
corp trece, altfel 0) × 163, adică numărul de probleme rezolvate cu 10 încercări. Dacă examenul (ii) iese incomplet (cod 3, peste
6.500 MB) → fără verdict pe pass@10, `oprit`, nu se repetă.

## Să nu uite

- Reperul S58 (pass@10 3/200 = 1,5 %) e pe **alt set**; comparația e aproximativă și o spunem așa. Setul nou are șabloanele
  sărace (s07, s16, s03, s13, s17, s19) cu mai puține probleme, deci alt amestec de greutate decât la S58.
- O singură sămânță, o singură noapte; NECLAR e NECLAR.
- Setul ascuns nou se deschide **o singură dată**, după cele 10 ore (SHA-256 verificat de unealtă); nu se reface și nu se repetă.
- Setul ascuns S58 nu se deschide (unealta a citit din el doar identitatea variantelor, ca să le excludă).
- Nu se ating `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, #477, linia română.
- Placa: sub 7.000 MB și 83 °C (paznicul la antrenare; `--memorie-max 6500` + plasa la examene). Cădere fără eroare → `oprit`,
  ora exactă, nu se repornește singur.
- Antrenarea pornește ziua (11:4x) și trece de 18:30 → se termină pe la ~22:00, apoi examenele (~25–30 min).

## Așteptările mele (în cifre)

- **Antrenarea:** ~1,2 miliarde simboluri în plus (a doua trecere prin cea mai mare parte a setului); placa ~6.100–6.300 MB
  (S58: max 6.205), 60–66 °C.
- **Examenul orar (1.000 de fișiere):** de la 0,4967 (ora 10) la **~0,483** la ora 20 (între 0,475 și 0,492); câștig mai mic
  pe oră decât în ultimele ore din S58 (rata fixă mică, date repetate), ~0,001–0,002 pe oră.
- **(i) Biți pe octet pe validarea întreagă:** **~0,500** (între 0,490 și 0,508), față de 0,5141. Șansa ≤ 0,494: ~25 %;
  > 0,504: ~25 %.
- **(ii) pass@1** ~0,3 %; **pass@10 ~4/163** (între 1 și 9). Șansa ≥ 5/163: ~40 %; ≤ 2/163: ~30 %.
- **(iii) setul de probă:** pass@10 ~1–2/20.
- Verdict: **CONTINUĂ ~12 %, PLATOU ~10 %, NECLAR ~78 %**.

## Ce ar infirma așteptările

- Biți > 0,5141 după a doua noapte: a doua trecere prin date strică (supraînvățare) — linia ar trebui oprită, nu continuată.
- Biți ≤ 0,490 cu pass@10 ≤ 2: modelul învață tot mai bine forma codului, dar nu rezolvarea problemelor; mai multe ore nu ajută pass@k.
- pass@10 ≥ 9/163: rata mică fixă ajută mai mult decât mă aștept (sau setul nou e mai ușor decât cel S58).

## Ce a ieșit

*Adăugat la 2026-11-02 22:34, din jurnalul Kronos (lucru/jurnal/experimente.jsonl) și din jurnalul CONTINUUM pe bune. Verdictul se scrie dedesubt.*

| # | linia | început | val_bpb | decizia | fapte noi | fapte | nota | motivul |
|---|---|---|---|---|---|---|---|---|
| 490 | cod_c1 | 02.11 11:38 | 0,4946 | pastrat | — | — | — |  |
| 491 | cod_c1 | 02.11 12:40 | 0,4928 | pastrat | — | — | — |  |
| 492 | cod_c1 | 02.11 13:42 | 0,4910 | pastrat | — | — | — |  |
| 493 | cod_c1 | 02.11 14:43 | 0,4899 | pastrat | — | — | — |  |
| 494 | cod_c1 | 02.11 15:45 | 0,4887 | pastrat | — | — | — |  |
| 495 | cod_c1 | 02.11 16:46 | 0,4885 | pastrat | — | — | — |  |
| 496 | cod_c1 | 02.11 17:48 | 0,4863 | pastrat | — | — | — |  |
| 497 | cod_c1 | 02.11 18:50 | 0,4850 | pastrat | — | — | — |  |
| 498 | cod_c1 | 02.11 19:51 | 0,4846 | pastrat | — | — | — |  |
| 499 | cod_c1 | 02.11 20:53 | 0,4834 | pastrat | — | — | — |  |

- **cod_c1:** 10 ore, 10 păstrate; val_bpb de la 0,4946 la 0,4834; cel mai bun păstrat: #499 (0,4834).

Niciun ciclu CONTINUUM pe bune în perioada asta.

**Examenele (o singură dată, pe starea de după ora 20, `lucru/cod_c1/gpt.pt`):**
- (i) biți pe octet pe validarea întreagă (5.686 fișiere): **0,50041** (Python 0,54068, Rust 0,42698, C 0,60137); S58: 0,5141.
- (ii) setul ascuns nou `ascuns2` (163 × 10): pass@1 **0,25 %** (4 corpuri „ok” din 1.630), pass@10 **3/163 = 1,84 %**; complet.
- (iii) setul de probă (20 × 10, doar informație): pass@1 0, pass@10 **0/20**.

## Verdictul

*Scris la 2026-11-02 22:40, de executant, strict după pragurile de mai sus.*

- CONTINUĂ = biți ≤ 0,494 **și** pass@10 ≥ 5/163 → 0,50041 ✗, 3/163 ✗ → **nu**.
- PLATOU = biți > 0,504 **și** pass@10 ≤ 2/163 → 0,50041 ✗, 3/163 ✗ → **nu**.
- **→ NECLAR.**

Față de așteptări: examenul orar 0,4834 (așteptat ~0,483, exact), validarea întreagă 0,5004 (așteptat ~0,500, exact),
pass@10 3/163 (așteptat ~4, în interval), setul de probă 0/20 (așteptat 1–2, mai slab). Câștigul celei de-a doua nopți
pe validarea întreagă: 0,0137 biți/octet (sub cele 0,02 cerute de CONTINUĂ, peste cele 0,01 ale PLATOU-ului). pass@10
1,84 % față de 1,5 % la S58, pe alt set — practic la fel. O sămânță, o noapte; NECLAR e NECLAR.
