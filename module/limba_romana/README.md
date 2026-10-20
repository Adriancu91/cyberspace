# Romanian Language Core (RLC) — motorul lingvistic simbolic pentru limba română

Modul al platformei Cyberspace (`module/limba_romana/`), independent de nucleul Kronos. Reprezintă limba română
explicit: lexicon cu identificatori stabili, forme cu trăsături și proveniență, reguli de acord, sensuri și
concepte — totul inspectabil, versionat și verificabil, fără niciun model neuronal.

Documente: `ARHITECTURA.md` (straturi, model de date, decizii), `LICENTE.md` (surse și licențe), `LIMITARI.md`
(ce nu face încă), raportul final în `docs/rapoarte/`.

## Instalare și construirea bazei

Cerințe: Python 3.11+ (doar biblioteca standard). Comenzile se dau din rădăcina depozitului `cyberspace`.

```bash
# 1. sursele lingvistice (≈ 370 MB; licențele sunt în LICENTE.md; datele nu intră în Git)
python -m module.limba_romana.importatoare.descarca_surse
# 2. baza lingvistică (≈ 8–12 minute; scrie module/limba_romana/_baza/limba_romana.sqlite, ≈ 1,3 GB)
python -m module.limba_romana.importatoare.construieste_baza --proaspat
# 3. testele (cele de integrare se sar dacă baza lipsește)
python -m pytest module/limba_romana/teste -q
# 4. evaluarea pe corpusul UD RRT (setul de test) și raportul de acoperire
python -m module.limba_romana.sintaxa.evaluare --set evaluare --scrie
python -m module.limba_romana acoperire --fisier raport_acoperire.json
```

Pe Windows comenzile sunt aceleași (`python` din mediul virtual al proiectului). Baza se construiește o singură
dată; fără `--proaspat`, `construieste_baza` adaugă peste ce există; `--continua` rulează doar paradigmele, clasele
închise și finalizarea; `--fara hunspell` (sau `rown`, `kaikki`, `ud_rrt`) construiește fără o sursă.

## Folosire din terminal

```bash
python -m module.limba_romana analizeaza "Copiii frumoși au plecat la școală."
python -m module.limba_romana verifica "Copii frumoasă a plecat."       # greșeli de acord, numerale, necunoscute
python -m module.limba_romana forma casei                               # analizele unei forme
python -m module.limba_romana forme casă NOUN                           # toate formele unui lexem, cu statut și surse
python -m module.limba_romana sensuri carte                             # sensuri (RoWordNet în română, Wiktionary în engleză)
python -m module.limba_romana explica "Am văzut o fată." 3              # de ce „o” e articol aici
python -m module.limba_romana reguli acord                              # regulile explicite
python -m module.limba_romana statistici | integritate | acoperire | exporta director
```
`--json` dă rezultatul în JSON. Exemplu de ieșire pentru `verifica`:

```
3 probleme
  ! acord_subst_adj: Adjectivul „frumoasă” (feminin singular) nu se acordă cu substantivul „Copii” (masculin plural). Sugestie: frumoși [subst_adj, sigura]
  ...
```

## Folosire din Python (API-ul public, versiunea 1)

```python
from module.limba_romana import Motor

motor = Motor()                                   # deschide baza (doar citire)
rezultat = motor.analizeaza("Copiii frumoși au plecat la școală.")
probleme = motor.verifica_text("Copii frumoasă a plecat.")   # interfața simplă pentru alte module (Kronos)
analize = motor.analiza_morfologica("casei")
forme = motor.forme_lema("casă", "NOUN")
sensuri = motor.sensuri("carte", "NOUN")
motor.inchide()
```

| Funcție | Ce întoarce |
|---|---|
| `cauta_forma(forma)` | toate analizele cunoscute ale unei forme (lexem, trăsături, statut, proveniență) |
| `cauta_lema(lema, pos=None)` | lexemele cu această lemă (id stabil, gen, omonim, surse) |
| `forme_lema(lema, pos=None)` | formele fiecărui lexem, cu trăsături, statut (atestat/generat/validat) și surse |
| `analiza_morfologica(cuvant)` | analize candidate; pentru necunoscute: ipoteze marcate ca atare |
| `analizeaza(text, context=None)` | analiza completă: propoziții → cuvinte (candidați cu scoruri și motive, alesul, ambiguitatea), grupuri nominale, dependențe (UD), sensuri cu dovezi, roluri semantice, probleme, necunoscute, proveniența bazei, versiunea |
| `verifica_text(text)` | doar problemele: `acord_subst_adj`, `acord_subst_det`, `acord_subiect_predicat`, `acord_al`, `acord_numeral`, `numeral_de`, `regim_prepozitie`, `necunoscut`, `ipoteza`, `ortografie`, fiecare cu mesaj, regulă, poziții, sugestie, certitudine (`sigura`/`probabila`/`posibila`) |
| `verifica_acord(text)`, `necunoscute(text)` | subseturi ale lui `verifica_text` |
| `explica(text, pozitie)` | analiza aleasă pentru un cuvânt, cu motivele, și candidații respinși |
| `sensuri(lema, pos=None)`, `relatii(concept_id)`, `lant_hiperonime(concept_id)`, `concept(concept_id)` | stratul semantic |
| `reguli(tip=None)`, `exemple(lema=…, forma=…)` | regulile explicite; exemple din corpus |
| `statistici()`, `integritate()`, `exporta(director)`, `acoperire()`, `surse()` | baza și rapoartele |

Rezultatele sunt dicționare/liste simple (serializabile JSON). Scorurile din `candidati` sunt dovezi euristice însumate,
nu probabilități calibrate; cuvintele cu `ambiguu: true` nu au o analiză sigură.

Pentru Kronos (sau orice alt modul): `verifica_text(text)` întoarce greșelile de acord și cuvintele necunoscute într-o
singură structură; modulul nu are nicio legătură cu `kronos/` și poate fi înlocuit sau folosit separat.

## Ce e în bază (rezumat; cifrele exacte sunt în raportul de acoperire)

- 4 surse: Hunspell ro_RO (dicționar ortografic cu reguli de flexiune), UD Romanian RRT (corpus adnotat), RoWordNet 3.0
  (concepte și relații), Wiktionary/kaikki (tabele de flexiune, sensuri, etimologii, registru) — licențele în `LICENTE.md`;
- tabele proprii scrise explicit: pronume, determinanți, articole, auxiliare, particule, prepoziții cu cazul cerut,
  conjuncții, numerale; paradigmele regulate ale substantivelor, adjectivelor și verbelor;
- regulile de acord și de dezambiguizare, cu nume și descriere (`python -m module.limba_romana reguli`).

## Teste

`python -m pytest module/limba_romana/teste -q` — unitare (tokenizare, trăsături, paradigme, clase închise, cititorul
Hunspell, baza: integritate, cicluri, export/import, determinism) pe fixturi scrise de mână; integrare și regresie pe
baza completă (propoziții corecte fără alarme false, propoziții greșite detectate cu sugestia așteptată, API, sensuri,
roluri). Evaluarea pe corpus: `python -m module.limba_romana.sintaxa.evaluare`.
