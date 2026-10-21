# Formatul comun de modul — v0

Aprobat de Adrian în chat, 2026-10-20 16:04 (propunerea `idei/2026-10-20-format-comun-module.md`).
Valabil pentru toate proiectele conectate la hub: `kronos`, `cyber-universe`, `suita-office`.

## Ce este
Fiecare modul are, în folderul lui, un fișier **`module.toml`** care îl descrie. Fișierul doar descrie:
**nu schimbă codul și nu înlocuiește** mecanismele existente (de exemplu `MANIFEST`-ul Kronos rămâne;
`module.toml` trebuie să spună același lucru).

## Câmpuri

```toml
[modul]
nume = "formule"                 # obligatoriu: identificator unic în proiect (litere mici, cifre, liniuță)
proiect = "suita-office"         # obligatoriu: kronos | cyber-universe | suita-office
versiune = "1.4.0"               # obligatoriu: versiunea modulului (MAJOR.MINOR.PATCH)
descriere = "Motorul de formule (~490 de funcții, nume românești)"   # obligatoriu, o propoziție
format = "modul-v0"              # obligatoriu: versiunea acestui standard

[contract]
port = ""                        # Kronos: unul din cele 10 porturi ale platformei; altfel gol
versiune_contract = ""           # versiunea contractului pe care îl respectă modulul; gol dacă nu există

[depinde]                        # de ce are nevoie ca să funcționeze (alte module, cu versiunea minimă)
# "citire-documente" = ">=1.0"

[ofera]                          # ce pune la dispoziția altora: funcții / formate / servicii, câte o linie
# "calcul" = "evaluează o formulă și întoarce rezultatul"

[rulare]
limbaj = "typescript"            # rust | python | typescript | ...
intrare = "src/formule/index.ts" # fișierul principal al modulului
teste = "npm test -- formule"    # comanda care verifică modulul
```

## Reguli
1. Câmpurile marcate obligatoriu trebuie completate; restul pot lipsi.
2. `port` și `versiune_contract` se completează obligatoriu pentru modulele Kronos (fără ele compatibilitatea nu
   se poate verifica automat — cerința Kronos din discuție).
3. Versiunea crește la fiecare schimbare care se vede din afară (MAJOR dacă strică pe cineva, MINOR dacă adaugă, PATCH pentru reparații).
4. Formatul se schimbă doar printr-o propunere nouă în `idei/`, aprobată de Adrian, care creează `modul-v1.md`.

## Cine ce face acum
- `kronos`: adaugă `module.toml` lângă fiecare modul din `module/`, cu aceleași date ca în `MANIFEST` + `depinde` / `ofera`.
- `suita-office`: adaugă `module.toml` în fiecare `src/<modul>/`.
- `cyber-universe`: folosește formatul pentru modulele din `modules/` și `apps/` (Faza 4), iar până atunci pentru driverele din nucleu nu e necesar.
Fiecare proiect face asta ca sarcină mică, în ritmul lui, și notează în „Discuție” la propunere când a terminat.
