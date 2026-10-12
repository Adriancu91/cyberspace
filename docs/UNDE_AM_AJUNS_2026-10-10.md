# Unde am ajuns (sâmbătă, 10 octombrie 2026)

*Scris de Claude Code la sfârșitul planului joi–sâmbătă (`docs/PLAN_joi_sambata.md`). Cifrele vin din jurnale: Kronos
(`lucru/jurnal/experimente.jsonl`), CONTINUUM (`lucru/continuum_pe_bune/`) și școala (`../cyberspace-cod/lucru/cod_v03/`),
plus pre-înregistrările închise (`docs/preinregistrari/`). Rezultatele negative sunt trecute la fel ca cele bune.*

## Scara: treptele din planul acestei săptămâni

Definiția întreagă a scării e în documentul lui Adrian („Cyberspace: AI construit de la 0 care se auto-îmbunătățește”),
nu în proiect. Aici sunt treptele pe care le-a țintit planul joi–sâmbătă. Celelalte nu le reproduc ca să nu le ghicesc.

| Treapta | Ce cere | Starea | Cifra care o susține |
|---|---|---|---|
| **4, întărită** | cel mai bun model: povești ≤ 0,428 și fapte ≥ 60/150, cu hrană în amestec, confirmate pe setul sacru | 🟢 **atinsă** | **#295** (antrenarea 8, ora 8, 10 octombrie), păstrat de Kronos: povești 0,4249, 64 de fapte noi, 5% hrană, setul sacru 30/50, nota profesorului 5,35 |
| **5, „își alege singur ce învață”** | CONTINUUM pe bune două nopți, alege singur ce antrenare pornește, cu fiecare decizie explicată | 🟡 **în lucru**: a ales singur: **NU** în ambele nopți | Pe bune, 221 de cicluri (noaptea 1: 180; noaptea 2: 41), fiecare cu motivul scris. A ales singur o remăsurare. N-a pornit nicio antrenare: poveștile erau „saturate”, iar lista albă avea o singură variantă. Antrenările nopților le-a pornit plasa de siguranță. |
| **7, școala de cod** | verdict: continuă (B trece nivelul 2 fără să uite poveștile) sau parcată, cu rezultatul negativ bine documentat | ⚪ **parcată** (rezultat negativ, documentat) | v0.3: B și D trec numerele 0–99 în 3 runde (80%/85%), poveștile ≤ 0,4383. Lanțul se rupe la cuvinte (0%), pentru că `"moon"` sunt 4 bucăți de tokenizer. Se reia pe workstation. |

**Lecțiile SANDBOX-7, intrate în Kronos:** ✅ toate trei.
1. **Faptele profesorului le verifică omul:** Adrian a verificat toate cele 50 pe 9 octombrie, iar niciunul nu e greșit.
   Mecanismul pentru faptele greșite e gata, dar inactiv.
2. **Biblioteca școlii se curăță după corectitudine:** curățarea e scrisă și testată. În pilot n-a avut ce face, pentru
   că n-a fost nicio regresie.
3. **Așteptările se scriu înainte de fiecare noapte:** ambele nopți au pre-înregistrare închisă din jurnale, cu
   verdictul. Am greșit în ambele direcții, iar asta s-a văzut doar pentru că așteptările erau scrise dinainte.

## Cel mai bun model, după fiecare criteriu

| Criteriul | Cel mai bun păstrat de Kronos | Observații |
|---|---|---|
| Povești (val_bpb, mai mic = mai bine) | **#295: 0,4249** (antrenarea 8) | înainte, #257: 0,4281 |
| Fapte noi (din 150) | #252: 72 (fapte prin injectare) | #295 are 64, iar fapte-zero (#286) 65 |
| Setul sacru (din 50; doar manual) | #295: 30 | #278 (antrenarea 7, ora 8, nepăstrat) are 31, iar #262 29 |
| Nota profesorului (din 10) | **#295: 5,35** | înainte, #260: 5,08 |
| De la zero, cu fapte (7 ore) | fapte-zero #286: 0,4686, 65 de fapte noi, sacru 25 | fără fapte (#225): 0,4636, 34, sacru 11 |

**Modelul de luat mai departe: #295.** E cel mai bun la povești și la notă, are faptele cu hrană confirmate pe setul
sacru și e păstrat de Kronos.

## Ce am aflat săptămâna asta (pe scurt)

- **Continuarea cu pași mici merită, la limită** (antrenarea 8, din #262, rata 0,00005 → 0,000005, 8 ore): +0,0055.
  - Bate repornirea cu rată dublă (antrenarea 7: 0,4263).
  - Prima oră urcă totuși (0,4404), iar câștigul vine în ultimele ore, când rata coboară.
  - Ultimele două ore au adus doar +0,0022 și +0,0010, deci linia veche se apropie de plafon pe laptop.
- **Faptele de la zero:** un model nou, cu 5% fapte de la început, ajunge în 7 ore la fapte cât prin injectare: 65 față
  de 72 fapte noi, 25 față de 26 pe setul sacru.
  - Aceeași rețetă fără fapte (#225) are doar 34 de fapte noi și 11 pe setul sacru.
  - Costul la povești e +0,005 val_bpb.
- **Hrana ține faptele:** în ambele antrenări din #262, R a stat la 1,0–1,14 toată noaptea.
- **CONTINUUM** decide corect după regulile lui, dar „saturat” îl blochează: fără date noi pe liniile urmărite nu mai
  cere nimic. Ca să poată alege cu adevărat, are nevoie de cel puțin două variante în lista albă.
- **Școala de cod:** numerele merg cu exemple în plus, iar cuvintele între ghilimele, nu. B și D merg la fel, deci
  ajută exemplele, nu descoperirea.
- **Alimentarea și oamenii:**
  - vineri, încărcătorul s-a deconectat de 1.732 de ori, iar laptopul a dormit 15,5 ore, deci noaptea 2 a pornit abia
    la 02:41;
  - sâmbătă, la 09:53, cineva a închis fereastra antrenării. Rulările lungi pornesc de acum cu fereastra ascunsă.

## Cifrele pentru prezentare

| | |
|---|---|
| Zile de proiect | 9 (2–10 octombrie 2026) |
| Experimente în jurnalul Kronos | 295: 164 păstrate, 115 respinse, 16 măsurători |
| Ore de experimente | 89 |
| Antrenări lungi | 9: lungă 1–5, 6a, 7, fapte-zero, 8 |
| Cicluri CONTINUUM | 155 simulate (v0) + 221 pe bune (v1, două nopți) |
| Școala de cod | 3 piloți (v0.1, v0.2, v0.3); ~16.800 de încercări de cod judecate în v0.3, din care 2 prinse trișând |
| Teste | 542 în main, 655 în `cyberspace-cod` |
| Commit-uri | 92 pe main |

## Deciziile pentru Adrian (weekend)

1. **Alimentarea (înainte de orice noapte nouă).**
   - Încărcătorul a cedat de două ori. Pe 8 octombrie, sub sarcină, a trecut de sute de ori între baterie și încărcător.
     Pe 9 octombrie s-a deconectat de 1.732 de ori, iar laptopul a dormit 15,5 ore.
   - Verifică încărcătorul, mufa, cablul și priza sau prelungitorul. Până atunci, laptopul nu rămâne singur noaptea.
   - Pe workstation, un UPS ar rezolva problema de tot.
2. **CONTINUUM și treapta 5.** Cu regulile de acum, după o antrenare „saturată” nu mai cere nimic. Cu o singură
   variantă în lista albă n-are ce alege, așa că a ieșit „a ales singur: NU” în ambele nopți.
   - **(a), recomandat:** lista albă cu cel puțin două variante, de exemplu continuarea din #295 cu pași mici și
     continuarea liniei fapte-zero.
   - **(b):** „dezvolta” poate porni singură o linie de la zero când poveștile sunt saturate.
3. **Ce rulează în noaptea următoare** (pe laptop, dacă alimentarea e rezolvată):
   - **(a):** încă 8 ore din #295, cu pași mici. Ultimele ore au adus doar +0,002 și +0,001, deci câștigul probabil e mic.
   - **(b), recomandat dacă rămânem pe laptop:** fapte-zero mai departe, încă 8 ore. Ar arăta dacă linia de la zero
     cu fapte ajunge la poveștile liniei vechi.
   - **(c):** nicio noapte pe laptop; trecem pe workstation.
4. **Mutarea pe workstation** (`docs/MUTARE_workstation.md`). Aprobi:
   - configurarea W2: 12×768, context 512, ~98 M parametri, ~5,6 GB;
   - tokenizer-ul nou: numerele 0–999 întregi, cuvintele întregi și după ghilimele, engleză + română + cod;
   - sursele de date cu licență verificată;
   - regula din CLAUDE.md pentru memoria video: 5,5 → 7 GB pe workstation.
5. **Școala de cod.**
   - Rămâne parcată până la workstation, cum spune planul, sau încercăm o zi de v0.4 pe laptop, cu mai multe cuvinte în
     abecedar?
   - Ramura `kronos-cod` rămâne separată sau se unește cu main?
