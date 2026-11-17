# S118 — Kronos învață din conversațiile cu Adrian: gata (pașii 1–4)

*Scris de executant (Claude Code), 17 noiembrie 2026, 18:40. Sarcina S118 din `plan/coada.md` (C-126 B), pe procesor.*

## Pe scurt

- **Butoanele merg:** în interfață (Chat și „din text”) ai 👍 / 👎 și „Răspunsul corect ar fi…”. În bază sunt deja
  **2 aprecieri** (2 × 👍 în Chat, 0 corecturi), salvate azi la 18:23.
- **Bucla e scrisă și testată:** `unelte/invata_din_conversatii.py` strânge lecțiile, antrenează 1 h din modelul din
  interfață, dă examenele și **schimbă modelul din interfață doar dacă trece tot**. N-am rulat-o pe placă: cu 2 lecții,
  niciuna nu cade în partea ținută deoparte, iar unealta refuză corect („prea puține lecții”, cod 3).
- **Regula** e pre-înregistrată: `docs/preinregistrari/2026-11-17_invatare_conversatii.md`.
- **Testele:** 1529 trec, 1 sărit, 0 pică (7 teste noi).
- **De la tine:** doar dacă vrei, „da” la propunerea de pornire automată de mai jos (pasul 4). Altfel, nimic.

## Ce s-a făcut, pe pași

### Pasul 1 (17:30, commit f2a8e9a) — butoanele
Tabelele `aprecieri`, `intrebari_text`, `aprecieri_text` în baza din `lucru/interfata/` (în afara Git), `POST /api/apreciere`
și `/api/apreciere-text`, butoanele în pagină. 5 teste.

### Pasul 2 (18:15, commit 093b094) — lecțiile
`unelte/lectii_din_conversatii.py`: 👍 fără corectură → lecția e răspunsul modelului; corectură → lecția e corectura;
👎 fără corectură și rândurile fără notă se ignoră. O lecție pe întrebare; 20 % deoparte după amprenta SHA-256 a întrebării
(stabil când vin lecții noi). 5 teste.

### Pasul 3 (acum) — bucla
`unelte/invata_din_conversatii.py`:
- `ruleaza`: lecțiile → modelul din interfață (din `unelte/interfata_ws.ps1`, azi #651) → amestecul (perechile rețetei S117,
  108.541 de rânduri, + lecțiile de **cel mult 3 ori**, toate lecțiile **≤ 5 %** din rânduri) → configurarea (copia lui
  `conv_w2_mare_24zch.toml` cu DOAR numele liniei, `cale_stare`, `conversatie`, scăderea pe 3.600 s și eticheta; AdamW 1e-5
  ca la S117) → `antrenare_recalcul.py --ore 1 --porneste-din <modelul din interfață>` → examenele pe vechi și nou (română
  curat, R1, S15 + S4 + tipuri noi cu profesorul, chat (a)+(b), lecțiile deoparte) → verdictul → dacă trece tot:
  `interfata_ws.ps1` pe modelul nou (cu rândul de revenire) și repornirea interfeței de pe 8787.
- Paza plăcii pe fiecare pas (> 7.000 MB sau ≥ 83 °C → oprire); orice cod ≠ 0 → oprire, interfața rămâne neschimbată.
- `pregateste`: doar partea de procesor (fără antrenare); `lectii`: notează lecțiile deoparte pe un model.
- Jurnalul fiecărei rulări: `lucru/invatare_conversatii/<eticheta>/jurnal.json` (doar numere).

**Regula (praguri copiate din coadă):** română curat N ≤ V + 0,01 · corecte N ≥ V − 10 · R1 N ≥ 90 · chat N ≥ V − 5 ·
lecțiile deoparte N ≥ V. Toate → modelul nou intră; altfel rămâne cel vechi.

**Proba pe baza reală (18:3x, procesor):** 2 aprecieri → 2 lecții (2 de antrenare, **0 deoparte**) → „prea puține lecții”,
nimic antrenat, placa neatinsă. Interfața: `config/conv_w2_mare_24zc.toml`, #651.

**Testele noi** (`teste/test_invata_din_conversatii.py`, 7): citirea și schimbarea lui `interfata_ws.ps1` (pe scriptul real,
fără să-l scrie), configurarea schimbă doar ce trebuie, repetările (≤ 3, ≤ 5 %), amestecul păstrează baza neschimbată,
verdictul strict (exact la praguri trece, peste oricare pică), oprirea fără lecții și la cod ≠ 0, și **notarea lecțiilor cu un
model mic antrenat pe procesor** (1 strat, 60 de pași).

### Pasul 4 — propunerea de pornire automată
Fără sarcini noi în Windows. Propun ca **supraveghetorul** să pună în coadă o sarcină de noapte (placa, ~1 h antrenare +
~1,5 h examene) când `python unelte/invata_din_conversatii.py pregateste` arată **≥ 30 de lecții noi** față de ultima rulare
**și** cel puțin **6 lecții deoparte**, iar placa e liberă; comanda din sarcină:
`python unelte/invata_din_conversatii.py ruleaza` (prin `unelte/cascada.py porneste`). Raportul fiecărei rulări: doar
numere (câte lecții, câte corecte vechi/nou, verdictul).

## Ce n-am făcut / de știut

- **Interfața n-am repornit-o:** rulează din 16:13 și salvează deja aprecierile (cele 2 de la 18:23), iar tu o foloseai; o
  repornire acum ți-ar fi tăiat conversația. Codul nou de la pașii 2–3 e în unelte, nu în server — nu cere repornire.
- **Git local:** rebase-ul rămas deschis de la 17:50 e tot acolo (`git rebase --continue` cere aprobare în rularea fără om);
  commit-urile merg pe GitHub cu `git push origin HEAD:main`. Rezolvarea, o comandă, în `C:\Kronos\cyberspace`:
  `git rebase --continue`.
- Conversațiile tale nu apar nicăieri în Git sau în raport — doar numere.
- `kronos/`, examenele, modelele: neatinse.

## Ce urmează

- S124 pașii 4–5 pe placă, în fereastra de noapte (de la 19:00).
- Bucla S118 pe placă doar când sunt destule lecții (pasul 4).
