# Unde am ajuns (sâmbătă, 10 octombrie 2026)

*Scris de Claude Code la sfârșitul planului joi–sâmbătă (`docs/PLAN_joi_sambata.md`). Cifrele vin din jurnale: Kronos
(`lucru/jurnal/experimente.jsonl`), CONTINUUM (`lucru/continuum_pe_bune/`) și școala (`../cyberspace-cod/lucru/cod_v03/`).
Rezultatele negative sunt trecute la fel ca cele bune.*

## Scara: treptele din planul acestei săptămâni

Definiția întreagă a scării e în documentul lui Adrian („Cyberspace: AI construit de la 0 care se auto-îmbunătățește”),
nu în proiect. Aici sunt treptele pe care le-a țintit planul joi–sâmbătă. Celelalte nu le reproduc ca să nu le ghicesc.

| Treapta | Ce cere | Starea | Cifra care o susține |
|---|---|---|---|
| **4, întărită** | cel mai bun model: povești ≤ 0,428 și fapte ≥ 60/150, cu hrană în amestec, confirmate pe setul sacru | 🟡 **în lucru** | #278 (antrenarea 7, ora 8) are 0,4263, 64 de fapte noi și sacru 31/50, cu 5% hrană. Kronos nu l-a păstrat: bate #262 cu 0,0041, sub pragul de 0,005. Noaptea 2: *(după 11:25)* |
| **5, „își alege singur ce învață”** | CONTINUUM pe bune două nopți, alege singur ce antrenare pornește, cu fiecare decizie explicată | 🟡 **în lucru**: a ales singur: **NU** în ambele nopți | Pe bune: 195 de cicluri (noaptea 1: 180; noaptea 2: din 02:41), fiecare cu motivul scris. A ales singur o remăsurare. N-a pornit nicio antrenare: poveștile erau „saturate”, iar lista albă n-avea altceva. Antrenările nopților le-a pornit plasa de siguranță. |
| **7, școala de cod** | verdict: continuă (B trece nivelul 2 fără să uite poveștile) sau parcată, cu rezultatul negativ bine documentat | ⚪ **parcată** (rezultat negativ, documentat) | v0.3: B și D trec numerele 0–99 în 3 runde (80%/85%), poveștile ≤ 0,4383. Lanțul se rupe la cuvinte (0%), pentru că `"moon"` sunt 4 bucăți de tokenizer. Se reia pe workstation. |

**Lecțiile SANDBOX-7, intrate în Kronos:** ✅ toate trei.
1. **Faptele profesorului le verifică omul:** Adrian a verificat toate cele 50 pe 9 octombrie, iar niciunul nu e greșit.
   Mecanismul pentru faptele greșite e gata, dar inactiv.
2. **Biblioteca școlii se curăță după corectitudine:** curățarea e scrisă și testată. În pilot n-a avut ce face, pentru
   că n-a fost nicio regresie.
3. **Așteptările se scriu înainte de fiecare noapte:** ambele nopți au pre-înregistrare închisă din jurnale, cu
   verdictul.

## Cel mai bun model, după fiecare criteriu

| Criteriul | Cel mai bun păstrat de Kronos | Cel mai bun măsurat, chiar dacă nepăstrat |
|---|---|---|
| Povești (val_bpb, mai mic = mai bine) | #257: 0,4281 | #278: 0,4263, nepăstrat (+0,0041 față de #262) |
| Fapte noi (din 150) | #252: 72 | *(noaptea 2)* |
| Setul sacru (din 50; doar manual) | #262: 29 | #278: 31 |
| Nota profesorului (din 10) | #260: 5,08 | — |
| Cu fapte de la zero (7 ore) | fapte-zero #286: 0,4686, 65 de fapte noi, sacru 25 | — |

## Ce am aflat săptămâna asta (pe scurt)

- **Faptele de la zero:** un model nou, cu 5% fapte în fiecare lot de la început, ajunge în 7 ore la fapte cât prin
  injectare: 65 față de 72 fapte noi, 25 față de 26 pe setul sacru.
  - Aceeași rețetă fără fapte (#225) are doar 34 de fapte noi și 11 pe setul sacru.
  - Costul la povești e +0,005 val_bpb.
- **Repornirea ratei (antrenarea 7):** 8 ore din #262 duc la 0,4263, adică +0,0041, sub prag. Faptele se țin: R 1,08.
- **Continuarea cu pași mici (antrenarea 8, noaptea 2):** *(după 11:25)*
- **CONTINUUM** decide corect după regulile lui, dar „saturat” îl blochează: fără date noi pe liniile urmărite nu mai
  cere nimic. Ca să poată alege cu adevărat, are nevoie de cel puțin două variante în lista albă.
- **Școala de cod:** numerele merg cu exemple în plus, iar cuvintele între ghilimele, nu. B și D merg la fel, deci
  ajută exemplele, nu descoperirea.
- **Alimentarea:** vineri, încărcătorul s-a deconectat de 1.732 de ori, iar laptopul a dormit 15,5 ore. Noaptea 2 a
  pornit de aceea abia la 02:41.

## Cifrele pentru prezentare

| | |
|---|---|
| Zile de proiect | 9 (2–10 octombrie 2026) |
| Experimente în jurnalul Kronos | 287 până vineri dimineață, plus orele nopții 2: 163 păstrate, 108 respinse, 16 măsurători |
| Ore de experimente | ~81 până vineri dimineață, plus noaptea 2 |
| Antrenări lungi | 9: lungă 1–5, 6a, 7, fapte-zero, 8 |
| Cicluri CONTINUUM | 155 simulate (v0) + 195 pe bune (v1) |
| Școala de cod | 3 piloți (v0.1, v0.2, v0.3); ~16.800 de încercări de cod judecate în v0.3, din care 2 prinse trișând |
| Teste | 542 în main, 655 în `cyberspace-cod` |
| Commit-uri | 90 pe main |

## Deciziile pentru Adrian (weekend)

*(se completează după noaptea 2; cel mult 5)*
