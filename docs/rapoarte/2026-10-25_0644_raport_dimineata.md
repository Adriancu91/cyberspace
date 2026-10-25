# Raportul de dimineață — duminică, 25 octombrie 2026, 06:44

## Pe scurt
- **Noaptea a fost pauză**, cum ai cerut (până luni, 26 oct). Pe placa video n-a rulat nimic.
- **Testele:** 908 trec, 1 e sărit (cel care are nevoie de placa video), niciunul nu pică.
- **Verdict nou nu e:** nicio pre-înregistrare deschisă. N-a fost nici examen de conversație, deci azi nu ai cele 20 de răspunsuri de verificat.
- **Calculatorul a stat pornit și treaz toată noaptea** (ieri dimineață avusese un gol de 06:15–08:06; azi nu).
- **Azi-noapte s-a trecut la ora de iarnă** (la 04:00 ceasul s-a dat înapoi la 03:00). De aceea raportul ăsta a pornit la 06:40 ora nouă, nu la 07:40. Nu s-a stricat nimic.

## Ce a rulat noaptea (de ieri, 24 oct 08:12, până acum)
- **Pe placa video:** nimic. Acum: 361 MB folosiți din 8.192 MB, 28 °C, 0 % încărcare; niciun program Python pe ea.
- **Antrenări / examene:** niciuna. Ultimul experiment din jurnal rămâne #435 (23 oct, examenele pe validări pentru #432).
  Jurnalul de noapte `noapte_ws_w2.log` scrie la 24 oct 08:06: „Nu pornesc: a trecut de 07:30”; după aceea n-a mai încercat nimic.
- **Executantul (cascada):** a pornit la fiecare 30 de minute, fără nicio pauză, de ieri dimineață până la 06:28 azi.
  De fiecare dată a găsit același lucru: nicio sarcină „în lucru”, nicio sarcină „aprobat”, deci n-a făcut nimic și n-a făcut commit.
  Starea cozii: S3 „propus”, S27 (E3 cu antrenare) „propus — necesită Adrian”, S28 (oprirea calculatorului) „oprit”, restul „gata”.
- **CONTINUUM** (supraveghetorul automat): doar a observat, la fiecare 5 minute (ultimul ciclu: #3194 la 06:35), cu mesajul
  „placa e a executantului, nu pornesc nimic”. Nevoile pe care le notează în așteptare: „repara: povești” și „dezvoltă: sens”.
- **Git:** niciun commit nou de la raportul de ieri (91d7ef4).
- **Interfața** (pagina de conversație, portul 8787): pornită ieri la 08:06, fără erori în jurnal.

## Ora de iarnă (lămurire)
În jurnalul executantului, pornirile de la 03:28 și 03:58 apar de două ori — prima oară pe ora de vară, a doua oară după ce
ceasul s-a dat înapoi. Sarcina Windows a raportului pare legată de ora „universală”, așa că acum pornește cu o oră mai devreme
pe ceas: **06:40 în loc de 07:40**. La fel probabil și fereastra de noapte a altor sarcini. Nu e o greșeală care strică ceva,
dar dacă vrei raportul tot la 07:40, sarcina trebuie reglată (vezi mai jos).

## Testele
`CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -m pytest -q` → **908 trecute, 1 sărit, 0 picate** (3 min 48 s).
Cel sărit e testul care are nevoie de placa video (am rulat fără ea, cum scrie în reguli).

## Verdict
Nu e. Toate pre-înregistrările din `docs/preinregistrari/` au deja secțiunea „Ce a ieșit”; noaptea nu a avut nimic de judecat.

## Examenul de conversație
N-a fost în noaptea asta, deci nu sunt cele 20 de răspunsuri de verificat.

## Ce aștept de la tine
1. **Nimic urgent** — pauza merge cum ai cerut.
2. **Calculatorul tot pornit este** (S28 e „oprit”, pentru că executantul nu are voie la comanda de oprire). Dacă îl vrei oprit
   până luni: îl oprești tu, sau dai executantului voie la `shutdown` și pui S28 înapoi pe „aprobat”.
3. **Ora raportului:** de azi pornește la 06:40 pe ceas, nu la 07:40. Spune-mi dacă vrei să rămână așa sau să fie reglată
   înapoi la 07:40 (asta înseamnă schimbarea sarcinii Windows, deci o faci tu sau îmi dai voie explicit).
4. **Luni** îți aștept răspunsul la S27 (E3 cu antrenare) și, dacă vrei, la S3.
