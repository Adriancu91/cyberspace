# Raport: datele pentru „răspuns din text” și cele 10 perechi de verificat (19 octombrie 2026, 10:00)

## Ce ai hotărât azi dimineață și ce am făcut

1. **Cele 20 de răspunsuri din noaptea 9:** ești de acord cu toate notele profesorului (20 din 20). Profesorul notează
   la fel ca tine, deci verdictul nopții 9 (INFIRMAT) rămâne.
2. **Sarcina „Kronos raport dimineata”: programată.** Rulează în fiecare zi la 07:40, prima dată mâine, 20 octombrie.
   De data asta paznicul nu m-a mai blocat. Comanda e cea din raportul de la 09:30:
   `conhost.exe --headless powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Kronos\cyberspace\unelte\raport_dimineata.ps1"`.
3. **Conversația, varianta (c), „răspuns din text”:** datele sunt gata, pe procesor, iar pre-înregistrarea e scrisă.
   **Noaptea nu pornește fără „da”-ul tău pe cele 10 perechi de mai jos.**

## Datele (`python unelte/conversatie_text.py --articole 16000`, 34 de secunde pe procesor)

Fiecare pereche are forma:

```
Text: [primul paragraf dintr-un articol Wikipedia]
Întrebare: …
Răspuns: …
```

- **15.534 de perechi cu răspunsul în text.** Răspunsul se ia din text, cuvânt cu cuvânt:
  - 7.767 sunt „Ce este X?” (prima propoziție). Le-am oprit la jumătate, ca Kronos să nu învețe doar să copieze
    prima propoziție;
  - restul sunt întrebări după șabloane: anul nașterii (2.386) și al morții (822), anul filmului sau al cărții (984),
    regizorul (974), autorul (266), locuitorii (885), comuna (576), județul (421), regiunea (138), suprafața (187) și
    încă câteva.
- **3.884 de perechi cu „Nu scrie în text.”** (20%):
  - jumătate întreabă despre același lucru ceva ce lipsește din text („Cine au fost părinții lui X?”, „În ce an a apărut
    X?”);
  - jumătate întreabă despre alt lucru decât cel din text.
- **250 de perechi de conversație simplă:** 50 scrise de mână de mine, fiecare pusă de 5 ori („Cum te numești?” →
  „Mă numesc Kronos.”, „Salut!”, „Mulțumesc!”, „Hello!”…). Lista e în `docs/conversatie/conversatie_simpla.json`.
- **Textele sunt curățate:** am scos paragrafele în care curățarea Wikipedia lăsase găuri („Are o populație de
  locuitori.”, „(în , în trad. …, în )”), cele cu alte alfabete (arabă, chirilică) și cele cu cuvinte necunoscute.
- Toate perechile încap în fereastra modelului: cea mai lungă are 291 de bucăți din 512.

**Examenul, pus deoparte: 80 de întrebări**, din articole care nu intră deloc în antrenare (verificat):
- **50 cu răspunsul în text:** 25 „Ce este X?” și 25 cu celelalte șabloane;
- **20 fără răspuns în text:** 10 despre același lucru și 10 despre alt lucru;
- **10 de conversație**, aceleași ca aseară, **doar urmărite**.

## Ce rulează diseară (dacă dai „da”)

- **Linia:** una nouă, „w2_conv_text”, pornită din **#385**, cu configurarea `config/conv_w2_text.toml`. Durează 3 ore.
- **Amestecul:** 45% perechi, 5% povești cu fapte, **50% text vechi**. Aseară a fost 75/5/20.
- **Rata: 0,00005**, adică jumătate din cea de aseară.
- **Pornirea, la 19:00:** sarcina „Kronos noapte conversatie” e setată, dar scriptul antrenează doar dacă
  `lucru/conversatie_aprobata.txt` pomenește noua configurare. Fișierul îl scriu numai după „da”-ul tău. Am verificat:
  acum noaptea **nu** ar porni.

## Pragurile, scrise înainte (`docs/preinregistrari/2026-10-19_noaptea10_raspuns_din_text.md`)

Un răspuns e corect dacă profesorul îi dă cel puțin 7 din 10. La cele fără răspuns în text, e corect dacă spune
„Nu scrie în text.”.

| | confirmat | infirmat |
|---|---|---|
| cu răspunsul în text, din 50 | cel puțin 30 | sub 15 |
| „Nu scrie în text.”, din 20 | cel puțin 12 | sub 6 |
| „Nu scrie în text.” spus când răspunsul e în text, din 50 | cel mult 5 | — |

Între ele, verdictul e „a început, dar nu ajunge”.

**Să nu uite:** aceleași praguri ca aseară, față de #385. Dacă trece de oricare, linia nu se păstrează.

| | #385 | pragul |
|---|---|---|
| română, validarea curată | 1,2833 | cel mult 1,3133 |
| cod, validarea curată | 0,7874 | cel mult 0,8174 |
| povești | 0,4383 | cel mult 0,47 |
| fapte noi | 73 | cel puțin 65 |

**Setul sacru** e urmărit: dacă scade sub 15 din 50, îl raportez separat.

**Ce cred că va ieși:**
- **cu răspunsul în text:** 22–38 din 50. „Ce este X?” e aproape copiere; restul e mai greu;
- **„Nu scrie în text.”:** 8–16 din 20. Cele despre alt lucru sunt ușoare, cele despre același lucru sunt grele;
- **„Nu scrie în text.” spus pe nedrept:** 2–8 din 50, deci poate trece de pragul de 5;
- **româna curată:** 1,29–1,33 și **codul curat:** 0,80–0,84, amândouă aproape de prag.

## Cele 10 perechi de verificat

Alese la întâmplare (sămânța 1020) din antrenare, câte un fel din fiecare: 2 „Ce este X?”, 4 cu alte șabloane,
2 „Nu scrie în text.” (una despre același lucru, una despre alt lucru) și 2 de conversație.

**1. text (definitie)**

> Text: Primera Divisió d'Andorra este cea mai importantă competiție fotbalistică din Andorra. Toate echipele participante sunt semi-profesioniste. Liga a fost fondată în anul 1995, sponsorizată de Federația Andorreză de Fotbal, creată cu un an mai devreme, toate echipele evoluând pe aceleași stadioane, Estadi Comunal de Aixovall și Estadi Comunal d'Andorra la Vella.
>
> Întrebare: Ce este Primera Divisió d'Andorra?
>
> Răspuns: Primera Divisió d'Andorra este cea mai importantă competiție fotbalistică din Andorra.

- e bine? (tu):

**2. text (definitie)**

> Text: Clubul Sportiv Municipal Ploiești a fost o echipă feminină de handbal din Ploiești, România. Înființată prin Hotărârea Consiliului Local nr. 108 din 31.08.2004, ca secție de handbal feminin a asociației polisportive Clubul Sportiv Municipal Ploiești. Echipa a promovat în sezonul 2011/12 în Liga Națională iar în anul 2016 s-a desființat datorită problemelor financiare.
>
> Întrebare: Ce a fost Clubul Sportiv Municipal Ploiești?
>
> Răspuns: Clubul Sportiv Municipal Ploiești a fost o echipă feminină de handbal din Ploiești, România.

- e bine? (tu):

**3. text (murit)**

> Text: George Demetru (numele său real fiind cel de Dumitru Georgescu) (n. 9 decembrie 1905, București – d. 27 februarie 1984) a fost un actor român de teatru și film.
>
> Întrebare: În ce an a murit George Demetru?
>
> Răspuns: În 1984.

- e bine? (tu):

**4. text (an)**

> Text: Vraciul este un film dramatic polonez din 1982, regizat de Jerzy Hoffman, care a ecranizat romanul omonim al lui Tadeusz Dołęga-Mostowicz, publicat în 1937. Este a doua adaptare cinematografică a cărții; prima adaptare a fost filmată în același an în care a fost scrisă cartea și a fost regizată de Michał Waszyński.
>
> Întrebare: Din ce an este Vraciul?
>
> Răspuns: Din 1982.

- e bine? (tu):

**5. text (nascut)**

> Text: Cory Efram Doctorow (n. 17 iulie 1971) este un blogger, jurnalist și autor științifico-fantastic canadian și are rolul de co-editor al weblog-ului „Boing Boing”. El este activist în favoarea liberalizării drepturilor de autor și un susținător al organizației „Creative Commons”, folosind unele din licențele lor pentru cărțile sale.
>
> Întrebare: În ce an s-a născut Cory Efram Doctorow?
>
> Răspuns: În 1971.

- e bine? (tu):

**6. text (comuna)**

> Text: Petnjica este un sat din comuna Petnjici, Muntenegru. Conform datelor de la recensământul din 2003, localitatea are 565 de locuitori (la recensământul din 1991 erau 643 de locuitori).
>
> Întrebare: În ce comună se află Petnjica?
>
> Răspuns: În comuna Petnjici.

- e bine? (tu):

**7. nu_scrie (lipsa_an)**

> Text: Biserica Sfântul Gheorghe din Malcoci este un lăcaș de cult edificat de germanii dobrogeni în satul Malcoci, Tulcea. Edificiul se află în prezent în stare avansată de degradare. Asociația germanilor dobrogeni din Germania a inițiat un proiect de salvare a monumentului.
>
> Întrebare: În ce an a apărut Biserica Sfântul Gheorghe din Malcoci?
>
> Răspuns: Nu scrie în text.

- e bine? (tu):

**8. nu_scrie (alt_subiect)**

> Text: Lucăceni este un sat din componența comunei Horești, raionul Fălești, Republica Moldova. Satul este situat pe malul stâng al Prutului, la 20 km de centrul raional și 20 km de stația de cale ferată Stolniceni. În popor satului Lucăceni i se zice "Bănari", iar în actele bisericești este întâlnit numele de "Iugani".
>
> Întrebare: Cine a fost Aurel Gore?
>
> Răspuns: Nu scrie în text.

- e bine? (tu):

**9. conversatie (conversatie)**

> Întrebare: Cum ești?
>
> Răspuns: Sunt bine, mulțumesc. Cu ce te pot ajuta?

- e bine? (tu):

**10. conversatie (conversatie)**

> Întrebare: Care e numele tău?
>
> Răspuns: Numele meu este Kronos.

- e bine? (tu):

Observ două lucruri:
- La #2, „datorită problemelor financiare” e greșeala articolului din Wikipedia (corect: „din cauza”). Textele nu le
  corectez, iar răspunsul e prima propoziție, care e corectă.
- La #7, „În ce an a apărut Biserica…?” sună puțin ciudat pentru o biserică, dar răspunsul („Nu scrie în text.”) e
  corect: textul nu are niciun an.

## Testele

`CUDA_VISIBLE_DEVICES=-1 .venv/Scripts/python -m pytest -q`: **741 trec, 1 sărit**, niciunul picat. Sunt 8 teste noi, în
`teste/test_conversatie_text.py`.

## Commit-uri

- 10009ee: unealta, perechile de conversație simplă, configurarea, scriptul nopții și testele.
- commit-ul acestui raport și al pre-înregistrării.

## Ce aștept de la tine

1. **„Da” sau „nu” pe cele 10 perechi.** Dacă dai „da”, scriu aprobarea și noaptea pornește la 19:00. Dacă o pereche e
   greșită, spune-mi care, ca să repar șablonul înainte.
2. **Dacă vrei alte praguri, spune-mi înainte de 19:00.**
3. **CONTINUUM:** perioada în care doar observă s-a încheiat azi la 07:45. Ziua (07:45–18:15) e fereastra de
   întreținere și nu pornește nimic, iar când placa e ocupată de altă sarcină trece în repaus. Totuși, între 18:15 și
   19:00 placa e liberă și ar putea porni ceva peste care să cadă noaptea (scriptul nopții nu verifică dacă rulează
   CONTINUUM). Vrei să prelungesc observarea până mâine la 07:45? E aceeași schimbare de o linie ca ieri, în
   `config/continuum_ws.toml`.
