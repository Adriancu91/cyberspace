# S9 — `cascada.py porneste --din-nou` (21 octombrie 2026, 10:11)

Executantul, rulare automată de la ~09:58. Sarcina: S9 din `plan/coada.md` (aprobată de supraveghetor, categoria 6
„reparații de scripturi”). Pe procesor, placa n-a fost folosită.

## De ce

Aseară, a doua pornire a lui S7 a fost refuzată, pentru că `lucru/cascada/S7.json` de la prima încercare (terminată)
exista încă. Fișierele au trebuit mutate de mână, cu Adrian de față. Acum unealta poate face asta singură.

## Ce s-a schimbat

Doar `unelte/cascada.py` și `teste/test_cascada.py` (+72 / −3 rânduri). Nimic în `kronos/`, examen, configurări sau `lucru/`.

- Opțiune nouă: `python unelte/cascada.py porneste S<n> --din-nou -- <comanda>`.
  - Dacă `lucru/cascada/S<n>.json` nu există: pornește ca de obicei.
  - Dacă există și sarcina e **terminată** (are `cod` sau procesul nu mai trăiește): mută, din Python,
    `S<n>.json` → `S<n>_<HHMM>.json` și `S<n>.log` → `S<n>_<HHMM>.log` (HHMM = ora din `pornita`; dacă numele e luat:
    `_2`, `_3`, …), scrie în consolă ce a mutat, apoi pornește.
  - Dacă sarcina încă **merge**: refuză („încă merge (procesul …); nu o pornesc din nou.”), nu mută nimic.
- **Fără `--din-nou`** comportamentul e exact cel de până acum (refuză dacă `S<n>.json` există).
- Nu șterge nimic.

## Teste

- Noi, în `teste/test_cascada.py` (cu dosar temporar):
  1. fără opțiune refuză ca înainte, iar `S0.json` rămâne neatins;
  2. cu opțiune, pe o sarcină terminată (pornită la 19:29, cu `S0_1929.json` deja existent): mută ambele fișiere în
     `S0_1929_2.*`, conținutul e păstrat, pornește `python -c "print('a doua')"` care se încheie cu cod 0;
  3. cu opțiune, pe o sarcină care încă merge: refuză, nu mută nimic.
- Toate testele: `CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -m pytest` → **815 trecute, 1 sărit** (înainte: 813 + 1 sărit;
  +2 teste noi), în 3 min 34 s.

## Ce urmează

- S12 (noaptea 12) poate folosi `porneste S12 --din-nou` dacă o încercare oprită lasă `S12.json` în urmă.
- Următoarea sarcină `aprobat` din coadă: S11 (datele pentru noaptea 12, trebuie `gata` până la 16:30) — o iau la
  rularea următoare (~10:30).
- De la Adrian nu aștept nimic pentru S9.
