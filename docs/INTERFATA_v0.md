# Interfața v0: chat în browser cu Kronos

*12 octombrie 2026. Prima treaptă din `docs/INTERFATA_plan.md` (ramura `claude-cod`). Codul e în `module/interfata/`.*

## Ce este

O pagină de chat pe care o deschizi în browser, pe calculator sau pe telefon. Scrii un text, iar Kronos (un model
salvat, ales de tine după numărul experimentului) îl continuă. Fiecare răspuns spune cine l-a dat și cât a durat.
Conversațiile se păstrează și le găsești în lista din stânga data viitoare.

## Cum o pornești

Deschizi PowerShell în `C:\Kronos\cyberspace` și scrii:

```
.venv\Scripts\python.exe -m module.interfata --config config/laptop_antrenare_lunga_8.toml --experiment 295 --port 8787
```

- `--experiment 295` = modelul care răspunde (numărul experimentului din jurnalul Kronos).
- `--config ...` = configurarea din care pagina citește lista modulelor.
- `--port 8787` = „ușa” pe care ascultă; 8787 e și valoarea implicită, deci poate lipsi.

Pe ecran apar adresele de deschis în browser, de exemplu `http://127.0.0.1:8787/`.

Modelul se încarcă abia la prima întrebare, pe procesor (nu pe placa video), ca antrenarea să nu fie deranjată. De
aceea primul răspuns durează mai mult, iar răspunsurile sunt mai lente decât pe placă.

Doar ca să vezi pagina, fără niciun model:

```
.venv\Scripts\python.exe -m module.interfata --config config/proba.toml --fals
```

Atunci răspunde un „creier de probă”, care spune deschis că nu e un model.

Opțiuni în plus: `--lungime 200` (cât de lung e un răspuns), `--dispozitiv cpu` (pe ce rulează modelul),
`--baza cale.db` (alt fișier pentru istoric), `--detaliat` (scrie pe ecran fiecare cerere).

## Cum o oprești

În fereastra în care ai pornit-o apeși **Ctrl+C**. Conversațiile rămân salvate.

## Cum ajungi la ea de pe telefon, prin Tailscale

1. Pe calculator și pe telefon e instalat Tailscale, cu același cont, și e pornit pe amândouă.
2. Pornești interfața. Dacă Tailscale merge, pe ecran apare și o a doua adresă, care începe cu `100.`, de exemplu
   `http://100.90.150.35:8787/`.
3. Pe telefon deschizi exact adresa aceea în browser.

Dacă apare mesajul „Tailscale nu a fost găsit sau nu e pornit”, interfața merge doar de pe calculator: pornește
Tailscale și apoi repornește interfața.

Dacă pagina nu se deschide pe telefon deși adresa cu `100.` apare: la prima pornire, Windows poate întreba dacă lași
Python să primească legături din rețea; răspunde „Permite”.

## Cine poate intra

Doar acest calculator și aparatele din rețeaua ta Tailscale. Sunt două lacăte:

- serverul ascultă numai pe `127.0.0.1` (calculatorul însuși) și pe adresa lui Tailscale, niciodată pe toate
  plăcile de rețea; din Wi-Fi-ul casei sau din internet nu se vede;
- fiecare cerere e verificată: dacă adresa celui care cere nu e a calculatorului sau din rețeaua Tailscale
  (`100.64.0.0/10`), primește refuz (403).

Atenție: v0 nu are conturi sau parole. Oricine e în rețeaua ta Tailscale poate citi și scrie conversațiile.

## Unde stau conversațiile

În `lucru/interfata/conversatii.db` (o bază SQLite, un singur fișier). Folderul `lucru/` nu intră în Git. Jurnalul
Kronos (`lucru/jurnal/`) nu e atins: interfața doar îl citește, ca să găsească modelul.

## Ce face v0

- chat cu un singur creier: Kronos (modelul ales) sau creierul de probă;
- eticheta celui care a răspuns și timpul de răspuns, la fiecare mesaj;
- istoricul conversațiilor, păstrat și după repornire;
- butoane cu modulele din registru: pentru fiecare port, modulul lui, versiunea și clasa (citite din configurare și
  din fișa MANIFEST a fiecărui modul); un modul nou apare singur;
- textul scris în chat rămâne text: diacriticele se păstrează, iar ceva de felul `<script>` nu se execută.

## Ce NU face v0 (vine în treptele următoare din plan)

- fără conturi de prieteni, invitații sau parole;
- fără Profesor (Qwen) și fără agent de cod: răspunde doar Kronos;
- fără butoanele „a mers” / „n-a știut” și fără coada „de învățat”;
- fără încărcare de fișiere;
- fără panou de admin (stare, STOP, jurnal) și fără API în stilul OpenAI;
- fără răspuns „în flux”: răspunsul apare întreg, la sfârșit;
- Kronos nu ține minte mesajele dinainte: primește doar ultimul mesaj și îl continuă;
- nu pornește antrenări și nu schimbă nimic în Kronos;
- nu pornește singură la deschiderea calculatorului: o pornești tu, cu comanda de mai sus.

## Teste

```
$env:CUDA_VISIBLE_DEVICES='-1'; .venv\Scripts\python.exe -m pytest teste/test_interfata.py -q -p no:cacheprovider
```
