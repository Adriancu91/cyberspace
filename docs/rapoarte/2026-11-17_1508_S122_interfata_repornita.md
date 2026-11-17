# S122 (C-129) pasul 4 — interfața de pe 8787 repornită cu câștigătorul (#651)

*Executant (cascada), 17 noiembrie 2026, 15:08. Pasul 4 din S122. Oprirea (pașii 1–3) e în
`docs/rapoarte/2026-11-16_2207_S122_interfata_oprita.md`.*

## Pe scurt

- **Chat-ul Kronos merge din nou** pe portul 8787, de la **14:59:54**, cu modelul **#651** în ambele file.
- **De ce #651:** e câștigătorul lanțului. S117 (#668) și S121 (#680) au dat amândouă, strict după pragurile scrise
  dinainte, **„rămâne #651”** (rapoartele `2026-11-17_0100_S117_chat.md` și `2026-11-17_0906_S121_calcule_chat.md`).
- **Repornirea automată e pusă la loc:** comutatorul `lucru\STOP_INTERFATA` e șters, deci paznicul de procese repornește
  iar interfața singur dacă pică (sau după o repornire a calculatorului), cu #651.
- **Verificarea:** cele 8 întrebări dau exact aceleași răspunsuri ca la S114 (16 nov); fila „din text” dă exact răspunsurile din C-119.
- **Teste:** 1497 trec, 1 sărit, 0 pică.
- **De la tine, Adrian:** nimic.

## Cum intri

- De pe workstation: `http://127.0.0.1:8787/`
- De pe telefon sau laptop (Tailscale): `http://100.90.150.35:8787/`

## Ce am făcut, exact

1. Lanțul s-a terminat: S117, S123, S121, S119 sunt `gata` (S119 la 14:37, după S125). Placa liberă (440 MB / 31 °C), nimic altceva în lucru.
2. Scriptul `lucru/cascada/S122_proba/reporneste_8787.py` (în afara Git), jurnalul în `lucru/cascada/S122_proba/repornire.json`:
   - înainte (14:59:51): portul 8787 nu răspundea, niciun proces `module.interfata`, comutatorul exista (pus 16 nov 22:00:11);
   - 14:59:53: comutatorul `lucru\STOP_INTERFATA` șters;
   - am pornit `unelte\interfata_ws.ps1` **fără parametri** (aceeași comandă pe care o folosește paznicul), cod 0:
     `python -X utf8 -m module.interfata --config config/conv_w2_mare_24zc.toml --experiment 651 --port 8787 --dispozitiv cpu --experiment-text 651`
     (procesele 3052 = lansatorul din `.venv` și 24204 = procesul lui, pornite 14:59:54);
   - 15:00:01: portul răspunde.
3. Neatinse: `kronos/`, `module/`, examenele, `unelte/interfata_ws.ps1`, `unelte/paznic_procese_ws.ps1`, sarcinile programate,
   niciun model schimbat sau șters.

## Verificarea, de pe adresa de Tailscale `http://100.90.150.35:8787`

Scriptul `lucru/cascada/S122_proba/intreaba.py` (copia celui de la S114 + „Cât face 3x7?”); rezultatul întreg:
`lucru/cascada/S122_proba/verificare_8787.json`.

Pagina: 200. `/api/stare`: creier **„Kronos (elev, modelul #651)”**, configurarea `w2_mare_24zc`, din text
„Kronos #651 — răspunde doar din textul dat.”, mesajul de sus: „Kronos #651 scrie în română; răspunde cel mai bine cu un
text alături, în fila «Întreabă din text». Fără text, faptele pot fi greșite.”

### Fila Chat (fără text), întocmai

| # | întrebarea | răspunsul lui #651 (întocmai) | timp | la fel ca S114? | citirea |
|---|---|---|---|---|---|
| 1 | salut | „salut, te ascult.” | 7,9 s (cu încărcarea modelului) | ✓ | bun |
| 2 | Care este capitala României? | „Nu scrie în text.” | 5,7 s | ✓ | greșit |
| 3 | Ce este fotosinteza? Explică pe scurt. | „Sunt un program de calculator.” | 5,8 s | ✓ | greșit |
| 4 | Cine ești? | „Sunt un program de calculator. Mă numesc Kronos.” | 5,5 s | ✓ | bun |
| 5 | Câți locuitori are Clujul? | „Sunt un program, loc.” | 5,7 s | ✓ | greșit |
| 6 | Cât face 3x7? | „Nu, puțin.” | 5,7 s | (nou) | greșit |

### Fila „din text” — cele 2 întrebări din raportul C-119

| # | întrebarea | răspunsul acum | răspunsul în C-119 | la fel? | timp |
|---|---|---|---|---|---|
| 7 | Câți locuitori are Vulcan? (cu paragraful despre Vulcan) | „24.160 de locuitori.” | „24.160 de locuitori.” | ✓ | 10,6 s |
| 8 | Când s-a format Lacul Roșu? (cu paragraful despre Lacul Roșu) | „În 1837.” | „În 1837.” | ✓ | 8,4 s |

**Citirea cinstită:** e același #651 de ieri, deci aceleași limite: fără text alături, faptele și calculele ies greșite
(„Cât face 3x7?” → „Nu, puțin.”). #680 (S121) socotea mai bine (51 din 200 la calcule față de 1), dar n-a trecut pragul
de 61, deci nu intră în interfață. S124 (la noapte) încearcă tocmai asta.

Timpii sunt cu ~1,5 s mai mari decât la S114 (5,5–5,8 s față de ~4,2 s), probabil pentru că prima întrebare de după pornire
încarcă modelul, iar procesorul era încă cald de la pornire; nu e o schimbare de model (aceleași răspunsuri, literă cu literă).

## Cum o oprești din nou (dacă e nevoie)

Ca la oprire: pui comutatorul și oprești procesele `module.interfata`. Cel mai simplu, cere în hub; executantul refolosește
`lucru/cascada/S122_proba/opreste_8787.py` (pune comutatorul și oprește doar interfața).

## Teste

`CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -m pytest -o addopts="" --basetemp=lucru/teste_tmp -q`:
**1497 trec, 1 sărit, 0 pică** (7 min 7 s).

## Ce urmează

- **S124** (aprobat, C-132): pașii 1–3 pe procesor (examenul nou cu formulări nevăzute + datele cu de 3 ori mai multe
  formulări) — acum pot porni, fiindcă S125 e `gata` și S122 pasul 4 e făcut; pe placă de la 19:00.
- **S118** (bucla 👍 / 👎): după S124 pașii 1–3; cât rulează S124 pe placă, bucla nu folosește placa.
- **De la tine, Adrian:** nimic.
