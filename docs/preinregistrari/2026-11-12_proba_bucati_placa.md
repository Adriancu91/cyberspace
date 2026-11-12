# Pre-înregistrare: S104: proba pe placă a datelor pe bucăți — modelul adevărat de 24 de straturi, aceiași pași cu datele vechi și cu datele pe bucăți

<!-- scrisa: 2026-11-12T08:02:00 -->
*Scrisă la 2026-11-12 08:02–08:15, la S104, ÎNAINTE de orice rulare pe placă (dosarul `lucru/proba_placa/` încă nu există). După
ce rularea a început, textul de mai jos nu se mai schimbă; la închidere se adaugă doar „Ce a ieșit” și „Verdictul”
(`python unelte/preinregistrare.py --inchide proba_bucati_placa`).*

## Cine a ales

Adrian a spus „da” la legarea datelor pe bucăți, cu condiția „proba că antrenarea iese identică” (hub `COMENZI.md` **C-110**,
12 nov 2026 06:49). Pașii și pragurile le-a scris supraveghetorul (12 nov 06:55, sarcina S104 din `plan/coada.md`); pragurile de
mai jos sunt **copiate exact** din sarcină. Unealta, cele două configurări, copiile de pornire și această pre-înregistrare:
Claude Code (executantul).

## Întrebarea

La S103, pe procesor și cu un model mic, antrenarea cu datele pe bucăți a dat aceleași loturi și aceleași pierderi, bit cu bit,
ca antrenarea cu datele vechi (textul întreg). **Pe placa video, cu modelul adevărat de 24 de straturi și rețeta adevărată
(Muon, gradient adunat pe 24 de loturi, recalculul activărilor), antrenarea cu datele pe bucăți primește aceleași loturi și dă
aceleași pierderi ca antrenarea cu datele vechi** — în limita zgomotului pe care placa îl are oricum de la o rulare la alta?

## Ce rulează

Nu e un experiment Kronos: nimic în jurnalul lui Kronos, niciun examen, niciun model păstrat ca rezultat. Un singur proces prin
cascadă (`cascada.py porneste S104 -- python unelte/proba_placa.py tot --iesire lucru/proba_placa/s104`), care pornește pe rând
trei rulări, fiecare într-un proces nou:

- **V1** = datele vechi (`config/proba_placa_vechi.toml`);
- **V2** = datele vechi încă o dată (aceeași configurare) — arată cât diferă placa de la o rulare la alta;
- **B** = datele pe bucăți (`config/proba_placa_bucati.toml`).

**Configurările (noi, de probă; cele existente neatinse):**

- `config/proba_placa_vechi.toml` = copia lui `config/conv_w2_mare_24n.toml` (S100: Muon, `rata_muon` 0,0001, `rata_invatare`
  5e-6, lot 4, 24 de loturi adunate, context 512) cu DOAR `nume`, `cale_stare = "lucru/proba_placa/vechi/gpt.pt"`, eticheta și
  antetul schimbate.
- `config/proba_placa_bucati.toml` = aceeași, cu portul `date` ca în `conv_w2_mare_24_bucati.toml`
  (`module.date_bucati:DateBucati` pe `lucru/bucati/w2_amestec_be12`) și `cale_stare = "lucru/proba_placa/bucati/gpt.pt"`.
- Diff-urile celor două față de `conv_w2_mare_24n.toml` se pun în raport.

**Starea de pornire:** aceeași copie a lui #554 ca la S99/S100 — din `lucru/w2_mare_24s/gpt.pt` (SHA-256 `ee39471f…4e5e`, doar
citit), cu `minute = 0` și optimizatorul gol, greutățile identice bit cu bit. Copia se scrie o dată și se pune în cele două dosare
(`lucru/proba_placa/vechi/gpt.pt`, `lucru/proba_placa/bucati/gpt.pt`); cele două fișiere trebuie să aibă același SHA-256, și
aștept să fie chiar cel de la S99/S100 (`759963dc…6d60`). Rulările **nu scriu** peste starea de pornire (unealta nu cheamă
`dupa_examen`, singurul loc care salvează): SHA-ul copiilor înainte = după fiecare rulare, deci V1, V2 și B pornesc din exact
aceeași stare.

**O rulare** (unealta nouă `unelte/proba_placa.py`, fără nicio schimbare în `kronos/` sau în `module/`):

- construiește portul `date` și modelul din configurare (prin registrul lui Kronos, ca `unelte/proba_legare.py`), cu recalculul
  activărilor din `unelte/antrenare_recalcul.py` (`instaleaza()`, plafonul PyTorch 5.800 MB) și
  `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`, ca la S99/S100;
- `pasi_max = 7.200` de loturi = **300 de pași de optimizare** × 24 de loturi adunate (unealta poate opri după un număr de pași,
  deci nu e nevoie de varianta „după timp”); aceeași sămânță (0) și același `pasi_total` de pornire (231.488) → după regula
  seminței, aceleași loturi;
- notează **pierderea la fiecare lot** (7.200) și, din ele, **pierderea fiecărui pas de optimizare** (media celor 24 de loturi
  ale lui — 300 de valori); SHA-256 peste toate loturile (intrare + țintă, inclusiv cele de conversație și hrană) și câte un SHA
  scurt pe fiecare lot; RAM-ul de vârf al procesului după încărcarea datelor și la sfârșit; memoria plăcii (PyTorch și
  nvidia-smi); simboluri pe secundă; SHA-ul greutăților la sfârșit (informativ);
- **fără** `torch.use_deterministic_algorithms` — placa lucrează exact ca la o antrenare adevărată (de asta există V2).

**Rata de învățare nu depinde de ceas în proba asta** (am verificat în cod înainte): `fractie_rata_finala = 1.0` (fără scădere
cosinus), încălzirea e terminată (231.488 > 1.000 de pași), răcirea finală începe abia la 75 % din 18.000 s (13.500 s), iar o
rulare durează ~20 de minute. Deci rata e constantă (AdamW 5e-6, Muon 0,0001) la toți pașii, în toate cele trei rulări; unealta
notează `rata_la_final` ca verificare.

**Paza (pasul 5 din sarcină):** procesul-părinte citește nvidia-smi la 5 secunde cât merge fiecare rulare; peste **6.700 MB**
sau la ≥ **83 °C** oprește rularea pe loc (proba nu trece prin Kronos, deci „`python -m kronos opreste`” n-ar opri-o; opresc
direct procesul rulării), sarcina devine `oprit`, cu memoria în raport. Înainte de pornire: placa goală sub 800 MB, C: ≥ 10 GB.

**Doar citite, verificate înainte = după:** `lucru/w2_mare_24s/gpt.pt` (#554), `lucru/stocare/modele/experiment_513.pt`,
`experiment_554.pt`, `lucru/w2_mare/gpt_24.pt` (SHA-256); `lucru/cache` și `lucru/bucati/w2_amestec_be12` (lista fișierelor cu
mărime și dată).

Durata estimată: ~20 de minute pe rulare (7.200 de loturi la ~6,2 loturi/s) + încărcarea datelor (~1 minut la cele vechi) →
**~65 de minute** în total; limita sarcinii: 2 ore.

## Pragurile — copiate exact din sarcină (fixe, scrise de supraveghetor)

- **DA** = SHA-ul loturilor identic V1 = B pe toți pașii **și** max |pierdere B − pierdere V1| ≤ max(2 × max |V2 − V1|, 1e-5) pe
  toți pașii comparați.
- **NU** = loturi diferite sau diferența B–V1 peste prag → primul pas diferit, fără reparații pe loc.
- Informativ: RAM de vârf la pornire V1 vs B (așteptare B < 4.000 MB), simboluri/s V1 vs B (așteptare: diferență < 5 %), placa
  max MB / °C.

**Cum citesc „pas” (stabilit acum, înainte de rulare):** „pasul” din prag = **pasul de optimizare** (300 pe rulare), iar
pierderea lui = media pierderilor celor 24 de loturi ale lui — așa cere sarcina („300 de pași de optimizare”, tabelul la pașii
1, 50, 100, 200, 300). Verdictul se dă pe aceste 300 de valori. Aceeași comparație pe cele 7.200 de loturi, luate unul câte
unul, o raportez **informativ** alături (dacă cele două citiri ar da răspunsuri diferite, o scriu limpede în raport; verdictul
rămâne cel pe pașii de optimizare).

**Dacă proba nu se termină** (paza, o eroare, o repornire a calculatorului): **NEMĂSURAT**, cu motivul; nimic repornit fără
supraveghetor (o întrerupere prin repornire nu e vina nimănui).

## Așteptările, în cifre (ghicitul executantului)

- **Loturile: identice V1 = V2 = B** (același SHA-256 peste toate cele 7.200) — **97 %**. La S98 și S103 au fost identice, iar
  alegerea ferestrelor se face pe procesor, cu același generator.
- **Zgomotul plăcii, max |V2 − V1| pe pașii de optimizare:** cel mai probabil **0** (rulări identice bit cu bit: același
  program, aceeași placă, aceleași loturi) — **55 %**; altfel mic la început și crescând cu pașii, până la ~0,001–0,01 la pasul
  300 — **45 %**.
- **max |B − V1|:** de aceeași mărime ca max |V2 − V1|. Dacă placa se repetă bit cu bit, aștept B = V1 bit cu bit (diferența 0).
- **Verdictul: DA 85 %.** NU 12 % — aproape tot din situația „placa nu se repetă bit cu bit și diferența B–V1 iese, din
  întâmplare, de peste două ori mai mare decât V2–V1” (două trageri din același zgomot; pragul de 2× nu acoperă orice
  întâmplare). NEMĂSURAT (pază, eroare) 3 %.
- **Pierderea:** primul pas de optimizare ~1,5–2,5; nicio tendință clară în 300 de pași la ratele astea (modelul e deja antrenat).
- **RAM de vârf:** V1 ~42.000–44.000 MB (textul întreg + simbolurile, plus PyTorch cu placa); **B ~2.500–3.800 MB** (la S103,
  pe procesor, 766 MB; cu bibliotecile plăcii încărcate un proces PyTorch are singur ~2–3 GB) — sub 4.000, dar nu cu mult.
- **Viteza:** ~6,2 loturi/s ≈ 12.700 simboluri/s la amândouă; diferența V1–B sub 2 %.
- **Placa:** goală ~414 MB; în antrenare ~4.450–4.750 MB (ca la S100: 4.455), sub paza de 6.700; ≤ 65 °C.

## Ce ar infirma așteptările

- SHA-ul loturilor diferit V1 ≠ B → legarea nu dă aceleași ferestre pe calea adevărată (cu `cale_stare`, sămânța de
  continuare, hrana din cache) — verdict NU, cu primul lot diferit și felul rândului (conversație / hrană / text).
- SHA-ul loturilor diferit V1 ≠ V2 → nici datele vechi nu dau aceleași loturi de la o rulare la alta (ar fi o surpriză mare:
  generatorul e pe procesor, cu sămânță fixă).
- max |B − V1| peste prag cu loturi identice → ceva diferă în calcul, nu în date (de exemplu tipul numerelor din lot).
- RAM B ≥ 4.000 MB → pe placă, câștigul de memorie e mai mic decât pe procesor (informativ, nu schimbă verdictul).
- Viteza B cu peste 5 % sub V1 → cititul de pe disc (mmap) încetinește antrenarea (informativ).

## Să nu uite

1. Dacă placa NU se repetă bit cu bit (V2 ≠ V1), diferențele cresc cu pașii (fiecare pas pornește din greutăți deja puțin
   diferite); pragul „2 × V2–V1” compară două trageri din același zgomot și poate pica din întâmplare. Un NU cu **loturi
   identice** și o diferență de aceeași mărime ca zgomotul trebuie citit ca „la limita pragului”, nu ca „legarea e greșită” —
   dar verdictul scris rămâne NU, strict după prag, și îl raportez așa.
2. Un DA aici spune că legarea dă aceeași antrenare pe 300 de pași de optimizare din starea #554; nu spune nimic despre
   calitatea vreunui model. Modelele de probă nu înlocuiesc nimic și nu intră în nicio comparație cu #513.
3. Proba nu trece prin orchestratorul lui Kronos (fără test rapid, fără examen, fără salvare) — bucla de antrenare e însă chiar
   cea din `module/` (`antreneaza`), neschimbată.
4. V1 și V2 citesc simbolurile vechi din `lucru/cache` (41,7 GB RAM la pornire): calculatorul are 128 GB, dar rulările merg
   una după alta, niciodată două odată.
5. RAM-ul „la pornire” = vârful procesului după ce datele sunt încărcate și modelul e pe placă (îl notez și doar după date).

## Ce a ieșit

*Adăugat la 2026-11-12 09:36, din jurnalul Kronos (lucru/jurnal/experimente.jsonl) și din jurnalul CONTINUUM pe bune. Verdictul se scrie dedesubt.*

Niciun experiment Kronos în perioada asta.

Niciun ciclu CONTINUUM pe bune în perioada asta.

(Așa trebuie: proba nu e un experiment Kronos. Cifrele ei sunt în `lucru/proba_placa/s104/s104.json`.)

Proba a mers de la 08:17:03 la 09:17:31 (60 min 27 s), cod 0, fără nicio oprire a pazei. Fiecare rulare: 7.200 de loturi =
300 de pași de optimizare.

| | V1 (date vechi) | V2 (date vechi, a doua oară) | B (date pe bucăți) |
|---|---|---|---|
| SHA-256 peste toate loturile | `5868cecc…9f8e` | `5868cecc…9f8e` | `5868cecc…9f8e` |
| pierderea la pasul 1 | 1,3649532 | 1,3649532 | 1,3649532 |
| pasul 50 | 1,4319511 | 1,4320763 | 1,4321398 |
| pasul 100 | 1,3774002 | 1,3773727 | 1,3773411 |
| pasul 200 | 1,2597989 | 1,2601021 | 1,2600622 |
| pasul 300 | 1,1923089 | 1,1921617 | 1,1920678 |
| RAM de vârf | 41.709 MB | 41.710 MB | 2.156 MB |
| simboluri/s | 12.698,9 | 12.665,4 | 12.668,7 |
| placa (nvidia-smi) max | 3.834 MB / 61 °C | 3.834 MB / 61 °C | 3.834 MB / 61 °C |

- Loturile: identice V1 = V2 = B (toate cele 7.200).
- Zgomotul plăcii, max |V2 − V1| pe pașii de optimizare: **0,000303** (la pasul 200). Placa NU se repetă bit cu bit.
- max |B − V1| pe pașii de optimizare: **0,000326** (la pasul 109). Pragul = max(2 × 0,000303; 1e-5) = **0,000607**.
- Informativ, lot cu lot (7.200): max |V2 − V1| 0,002343, max |B − V1| 0,002322, pragul 0,004685 → aceeași citire.
- Starea de pornire neschimbată după fiecare rulare (`759963dc…6d60`); #554, #513, `gpt_24.pt`, `lucru/cache` și bucățile neschimbate.

## Verdictul

**DA** — strict după prag: SHA-ul loturilor identic V1 = B pe toți pașii **și** max |B − V1| = 0,000326 ≤ 0,000607.

Față de așteptări: loturile identice (cum ghicisem, 97 %); placa nu se repetă bit cu bit (ramura de 45 %), dar zgomotul e mai
mic decât ghicisem (0,0003, nu 0,001–0,01); B − V1 e de aceeași mărime ca zgomotul (de 1,07 ori). Greșit ghicit: pierderea
primului pas (1,36, nu 1,5–2,5) și memoria plăcii (3.834 MB, nu 4.450–4.750). RAM B 2.156 MB (sub 4.000, sub ce ghicisem);
viteza B cu 0,24 % sub V1 (sub 5 %).

De ținut minte (nu schimbă verdictul): B se desparte de V1 de la pasul 2, iar V2 de V1 abia de la pasul 6. E o singură
pereche de rulări, iar mărimea diferențelor e aceeași, deci nu pot spune din proba asta dacă e întâmplare sau nu; pe procesor
(S103) cele două căi au dat rezultate identice bit cu bit.
