# Pre-înregistrare: S118 (C-126 B) — Kronos învață din conversațiile cu Adrian (regula buclei)

<!-- scrisa: 2026-11-17T18:33:00 -->
*Scrisă la 2026-11-17 18:33, înainte de orice rulare reală a buclei (în baza interfeței sunt acum 2 lecții, 0 deoparte →
bucla refuză să antreneze). Se scrie o singură dată (S118 pasul 3); fiecare rulare a buclei o aplică întocmai, fără
schimbări. Rularea scrie verdictul în `lucru/invatare_conversatii/<eticheta>/jurnal.json`, iar raportul rulării îl copiază.*

## Cine a ales

Adrian: C-126 partea B (16 nov 2026). Pașii și pragurile: supraveghetorul (sarcina S118 din `plan/coada.md`) — pragurile
de mai jos sunt **copiate exact** de acolo. Unealta: `unelte/invata_din_conversatii.py` (executantul, 17 nov 2026).

## Întrebarea

După o oră de antrenare cu lecțiile din conversații (👍 și „răspunsul corect ar fi…”), răspunde modelul mai bine (sau cel
puțin la fel) la lecțiile ținute deoparte, fără să piardă româna, răspunsurile corecte, instrucțiunile și chat-ul?

## Ce rulează (la fiecare rulare)

- **Lecțiile:** `unelte/lectii_din_conversatii.py` → `lucru/lectii/` (în afara Git); 20 % deoparte după amprenta SHA-256
  a întrebării (stabil când vin lecții noi). Fără nicio lecție de antrenare sau fără nicio lecție deoparte → **nu se
  antrenează nimic** (cod 3).
- **Modelul de pornire (V):** cel din interfață = valorile implicite din `unelte/interfata_ws.ps1` (azi #651).
- **Amestecul:** perechile de conversație ale rețetei S117 (`lucru/conversatie_chat/antrenare.jsonl`, 108.541 de rânduri)
  + lecțiile de antrenare, fiecare de **cel mult 3 ori**, iar toate lecțiile la un loc **cel mult 5 %** din rânduri.
- **Configurarea:** copia lui `config/conv_w2_mare_24zch.toml` (S117) cu DOAR numele liniei (`w2_lectii_<eticheta>`),
  `cale_stare`, `conversatie`, `durata_scaderii_secunde = 3600` și eticheta. Rest ca la S117: AdamW 1e-5, conversație
  0,45, hrană 0,30, lot 6 × 16.
- **Antrenarea:** `unelte/antrenare_recalcul.py --config <noua> --ore 1 --porneste-din V` (placa ≤ 7.000 MB, < 83 °C).
- **Examenele**, pe V și pe modelul nou (N), aceleași întrebări: română curat (`examen_validari_ws.py`), R1
  (`romana_raspunsuri.py reper`), `examen_conversatie.py --doar-local` pe S15 + S4 + tipuri noi (corect = nota
  profesorului ≥ 7), `examen_chat.py` (a)+(b) din 200, lecțiile ținute deoparte (corect = verificatorul de text S16 față
  de răspunsul din lecție; răspunsul ca în fila Chat: fără întâmplare, 80 de bucăți, tăiat la primul rând nou).

## Regula (pragurile, fixe)

**MODELUL NOU INTRĂ ÎN INTERFAȚĂ** dacă și numai dacă TOATE:
1. română curat N ≤ V + **0,01**;
2. corecte (S15 + S4 + tipuri noi, profesor) N ≥ V − **10**;
3. R1 instrucțiuni N ≥ **90**;
4. chat (a)+(b) N ≥ V − **5**;
5. lecțiile ținute deoparte: corecte N ≥ corecte V.

Atunci: `interfata_ws.ps1` primește N în ambele file (cu rândul de revenire scris deasupra) și interfața de pe 8787 e
repornită. Altfel: nimic schimbat; jurnalul spune ce condiție a picat. Orice pas cu cod ≠ 0 sau oprit de paza plăcii →
rularea se oprește, interfața rămâne pe V.

## Așteptările, în cifre (înainte de prima rulare reală)

- Cu puține lecții (sub ~30), o oră din V cu lecțiile ≤ 5 % din rânduri mișcă puțin modelul: aștept română curat în
  ±0,01, corecte în ±10, chat în ±5 (la S117, 4 ore pe rețeta asta: română 1,0898, corecte 227, R1 98,05).
- Lecțiile deoparte: cu sub 10 lecții deoparte, diferența N − V e în zgomot (o lecție = 10 pp sau mai mult); un „trece”
  la (5) cu 0 = 0 nu spune că modelul a învățat, doar că n-a pierdut.

## Ce ar infirma ideea

- N **pică** (1)–(4) după o oră = lecțiile (sau ora în plus pe rețeta S117) strică modelul → nu se mai rulează automat
  până nu decide Adrian.
- Pe ≥ 3 rulări cu ≥ 10 lecții deoparte, N nu trece niciodată de V la (5) = bucla nu învață din conversații în forma asta.

## Să nu uite

- Conversațiile lui Adrian **nu** ajung în Git, hub sau rapoarte: în raport doar numere (câte lecții, câte trecute).
- Bucla nu atinge `kronos/`, examenele vechi, #513/#577/#651/#680; modelele vechi nu se șterg.
- Pornirea automată: doar ca sarcină de noapte pusă în coadă de supraveghetor (vezi raportul S118); fără sarcini programate
  noi în Windows.
