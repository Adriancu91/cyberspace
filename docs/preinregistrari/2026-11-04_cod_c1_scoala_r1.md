# Pre-înregistrare: S72b, școala de cod runda 1 (S63 învață din propriile soluții corecte pe P_scoala; măsurat pe P_verif)

<!-- scrisa: 2026-11-04T14:29:52 -->
*Scrisă la 2026-11-04 14:29–14:40, înainte de rulare (nimic din S75 / S72b n-a pornit pe placă; `lucru/kronos_cod/scoala/runda1/`
nu există). După ce rularea a început, textul de mai jos nu se mai schimbă; la închidere se adaugă doar „Ce a ieșit” și „Verdictul”
(`python unelte/preinregistrare.py --inchide cod_c1_scoala_r1`).*

## Cine a ales

Adrian, COMENZI.md C-60 C (3 nov 2026 11:45: „școala cu verificator” da). Instrucțiunile și pragurile: supraveghetorul (4 nov 05:20,
notele din 11:20 și 14:20; S75 = pașii 1–2 mutați ziua). Această pre-înregistrare: Claude Code (executantul), înainte de S75.

## Întrebarea

Dacă S63 învață o singură trecere din propriile sale soluții **corecte** (verificate în cutie) la exercițiile P_scoala, rezolvă cu
cel puțin **10 exerciții mai multe** din P_verif (200, ținute deoparte) fără să strice codul obișnuit (validarea ≤ 0,505)?

## Ce rulează

Mărimile reale din S72a: **P_verif = 200** exerciții cu test bune (122 de pachete), **P_scoala = 689** (124 de pachete; `fluids` 138,
`chemicals` 104 = 35 %). Reperul din S74 (`lucru/kronos_cod/scoala/reper_s63/nota.json`, nu se repetă): **B = 14 din 200**
(pass@10 0,070, pass@1 0,013; 26 „ok” din 2.000); fără `return <valoare fixă>`: 13.

1. **S75, ziua (4 nov):** S63 (`lucru/cod_c1/gpt.pt`, doar citit, SHA-256 înainte și după) scrie **8 încercări** la fiecare din cele
   689 de exerciții P_scoala (temperatura 0,8, sămânța 1, `--lot 2 --memorie-max 6500`) → `lucru/kronos_cod/scoala/runda1/raspunsuri.jsonl`;
   oprire curată la 18:15 dacă nu e gata.
2. **S75, procesor:** cutia verifică fiecare încercare cu testul exercițiului ei (`unelte/kronos_cod/scoala.py corecte`, unealtă nouă,
   cu teste; `cutie.py` neschimbat; control: `examen_cod.py noteaza` pe aceleași răspunsuri dă aceleași „ok”). Se păstrează doar corpurile
   corecte, fără duplicate (după spații); **se scot cele care sunt doar `return <valoare fixă>`** (regula (b)). Pragul: **≥ 100 de corpuri
   corecte diferite după regula (b) = DESTULE**, altfel **PREA PUȚINE** (atunci S72b nu pornește, verdictul PREA PUȚINE).
3. **S72b, noaptea 4→5 nov (doar dacă DESTULE):** copie `lucru/cod_c1/gpt.pt` → `lucru/cod_c1_sc/gpt.pt` (SHA-256 ambele), config
   `config/cod_c1_sc.toml` (= `cod_c1_init002.toml` cu `nume = "cod_c1_sc"`, `cale_stare`, `director` = amestecul, eticheta). Verificare pe
   procesor: starea copiată are **590.110 pași**, rata 6·10⁻⁵, fără încălzire; altfel `oprit`. Amestecul = fiecare corp corect, cu antetul
   și explicația în față (exact ca exercițiul), repetat de **8 ori**, + tot atâtea simboluri de cod obișnuit din `simboluri/antrenare_*.bin`
   (sămânța 0); o singură trecere, rata fixă 6·10⁻⁵ (cel mult `--ore 1` dacă unealta nu are pași/minute).
4. **Examenele, o singură dată, pe starea de după învățare:** (i) biți pe octet pe validarea întreagă (5.686 fișiere); (ii) P_verif
   200 × 10, temperatura 0,8, sămânța 0 → pass@10 = **R**; (iii) `ascuns2` 163 × 10 (temperatura 0,8, sămânța 0); (iv) setul de probă 20 × 10, informativ.

## Pragurile (copiate neschimbate din coadă), N = 200, B = 14

- **AJUTĂ** = R ≥ B + 10 = **24** **și** validarea ≤ **0,505**;
- **NU AJUTĂ** = R ≤ B + 3 = **17**;
- **STRICĂ** = validarea > **0,510** sau R ≤ B − 5 = **9**;
- altfel **NECLAR**.
- `ascuns2` se raportează alături (S63: 3/163, S70: 2/163); „ajută și pe examen” doar dacă `ascuns2` ≥ **6/163**.
- O sămânță, o rundă; o diferență de ±3 din 200 e zgomot și o spunem așa.

Cum le citesc (scris acum): R = numărul de exerciții din P_verif cu măcar un corp „ok” din 10 (pass@10 din `noteaza` × 200). STRICĂ are
întâietate. Dacă S75 dă PREA PUȚINE, verdictul rundei e **PREA PUȚINE** (nu se antrenează, nu se dă examen pe P_verif).

## Să nu uite

- Exercițiile P_scoala sunt funcții din codul de antrenare: un corp „corect” poate fi doar amintit, nu rezolvat. Se numără câte corecte
  sunt **identice cu corpul original** (după spații).
- Explicația din exercițiu conține adesea chiar rezultatul exemplului → regula (b) scoate `return <valoare fixă>`; se numără câte.
- Reperul B = 14 e mic și un singur exercițiu (v00139, 7/10) face jumătate din „ok”-urile lui: R se poate mișca mult din noroc.
- 35 % din P_scoala sunt `fluids` / `chemicals`: se raportează câte corecte vin din ele.
- Nu se ating `kronos/`, `module/examen_bpb.py`, paznicul, jurnalul, `cutie.py`, #477, linia română, `lucru/cod_c1/` și `lucru/cod_c1_ex/`
  (doar citire), P_verif / P_scoala (doar citire), seturile ascunse. Nimic descărcat, nimic instalat.
- Placa sub 7.000 MB și 83 °C. Cădere fără eroare → `oprit`, ora exactă, nu se repornește singur.

## Așteptările, în cifre

- **S75, pasul 1:** 689 × 8 = **5.512 încercări**, ~66 min (S74: 2.000 în 1.433 s), placa ~2.000–2.100 MB.
- **S75, pasul 2:** rata de „ok” ca la S74 (1,3 %) → **~70 de corecte** (între 40 și 130), la **~40 de exerciții** (între 25 și 65; ~6 %
  din 689, puțin sub 7 % pentru că sunt 8 încercări, nu 10). Corpuri corecte **diferite** după spații: **~50** (între 30 și 100).
  `return <valoare fixă>` scoase: **~3** (între 0 și 10). Identice cu corpul original: **~35 %** din cele diferite (între 15 % și 60 %).
  Din `fluids` / `chemicals`: ~25 % din corecte (sub cei 35 % din exerciții).
- **Pragul S75:** șansa de **DESTULE (≥ 100)**: **~15 %**; **PREA PUȚINE: ~85 %**.
- **Dacă DESTULE și S72b rulează:** validarea **~0,501** (între 0,499 și 0,505; o singură trecere scurtă la rata 6·10⁻⁵ mișcă puțin);
  **R ~17** (între 12 și 24); `ascuns2` ~3/163. Verdictul, condiționat de DESTULE: AJUTĂ ~15 %, NU AJUTĂ ~50 %, STRICĂ ~5 %, NECLAR ~30 %.
- **Per total (înainte de S75):** PREA PUȚINE ~85 %, AJUTĂ ~2 %, NU AJUTĂ ~8 %, NECLAR ~4 %, STRICĂ ~1 %.

## Ce ar infirma așteptările

- ≥ 150 de corpuri corecte diferite: S63 rezolvă exercițiile din școală mult mai des decât pe P_verif (probabil din memorie) — de verificat
  partea identică cu originalul.
- Peste 60 % din corecte identice cu originalul: „școala” ar învăța mai ales ce știa deja pe de rost.
- R ≥ 24 cu validarea ≤ 0,505 (AJUTĂ) după o singură trecere scurtă: învățarea din propriile soluții corecte are efect mare chiar la doză mică.
- R ≤ 9 (STRICĂ): repetarea de 8 ori a câtorva zeci de corpuri strică generarea.
