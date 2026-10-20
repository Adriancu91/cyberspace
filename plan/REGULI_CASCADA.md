# Lucrul în cascadă: cine face ce (aprobat de Adrian pe 19 octombrie 2026, 19:35)

Scopul: placa și calculatorul să nu mai stea degeaba. Lucrul trece singur de la o sarcină la alta, fără să aștepte
ca Adrian să copieze mesaje între sesiuni.

## Cei trei

| cine | unde | ce face |
|---|---|---|
| **Adrian** | telefon | stabilește direcția; aprobă ce iese din granițele de mai jos; citește `plan/pentru_adrian.md` |
| **Supraveghetorul** (Claude, sesiune programată în cloud) | GitHub | de 8 ori pe zi citește rapoartele, scrie verdictul lui, pune sarcinile următoare în `plan/coada.md`, aprobă singur ce intră în granițe, scrie rezumatul pentru Adrian |
| **Executantul** (Claude Code pe workstation) | calculatorul Kronos | la fiecare 30 de minute citește `plan/coada.md`; dacă placa e liberă și există o sarcină `aprobat`, o face; scrie raportul în `docs/rapoarte/`, actualizează starea sarcinii, commit + push |

Supravegherea rulează la 02:15, 05:15, 08:15, 11:15, 14:15, 17:15, 20:15, 23:15 (ora României), ca trecerea de dimineață să vină după raportul de la 07:40.

## Granițele: ce poate aproba supraveghetorul singur

1. încă o rulare pe o linie de model care există deja (mai multe ore, altă rată, alt amestec de date, altă copie răcită);
2. examene, comparații, notări (pe procesor sau pe placă), inclusiv examenul neutru și validările curate;
3. pregătirea și curățarea datelor din sursele deja descărcate și aprobate;
4. școala de cod (nivele noi, sarcini noi), pe ramura `kronos-cod`;
5. unelte noi în `unelte/` și teste noi, care nu ating `kronos/` și examenul;
6. reparații de scripturi care au picat.

Fiecare sarcină de antrenare are pre-înregistrare scrisă ÎNAINTE de pornire (`docs/preinregistrari/`), cu praguri.

## Doar cu „da”-ul lui Adrian

- orice descărcare nouă de date sau modele (și verificarea licenței înainte);
- orice schimbare în `kronos/`, `module/examen_bpb.py`, contracte, paznic, jurnal;
- o linie de model nouă (altă mărime, alt tokenizer), schimbarea modelului din interfață;
- merge al ramurii `limba-romana` (motorul de română) în `main`;
- orice costă bani, orice instalare de programe, orice schimbare de setări Windows;
- ștergerea de modele sau date.

Sarcinile de felul ăsta intră în coadă cu starea `propus — necesită Adrian` și se trec în `plan/pentru_adrian.md`.

## Regulile care rămân

- O singură sarcină grea pe placă o dată. Paznicul: memoria plăcii sub 7.000 MB, sub 83 °C.
- Toate testele trec înainte de „gata”. Commit în română după fiecare pas.
- Rezultatele negative se raportează la fel ca cele pozitive.
- Ferestrele plăcii: ziua 08:00–18:30, noaptea 19:00–07:00. Raportul de dimineață: 07:40.
- CONTINUUM rămâne doar observator cât timp merge cascada (altfel s-ar bate pe placă cu executantul).

## Cyber Hub (adăugat cu aprobarea lui Adrian, 20 octombrie 2026)

- Supraveghetorul citește la fiecare trecere `Adriancu91/cyber-hub` (stările celorlalte proiecte, propunerile din `idei/`).
- Când s-a schimbat ceva la Kronos, rescrie `stare/kronos.md` și adaugă 1–3 rânduri în `jurnal/kronos.md` din hub.
- Poate scrie propuneri de colaborare în `idei/` din hub. O propunere nu intră în `plan/coada.md` decât după „da”-ul lui Adrian.
- Hub-ul nu schimbă nimic din granițele de mai sus.

## Când ceva merge prost

- Executantul oprește sarcina, scrie de ce în raport și pune sarcina pe `oprit`.
- Supraveghetorul vede la următoarea trecere; dacă e grav (calculatorul nu mai raportează de peste 3 ore, teste
  picate, paznicul a oprit ceva, placa fierbinte), trimite notificare pe telefonul lui Adrian.
