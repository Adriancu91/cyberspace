# Reguli pentru Claude Code în acest proiect

## Cu cine lucrezi
- Omul cu care lucrezi vorbește română și **nu știe să programeze**. Răspunde în română, simplu, fără jargon nedefinit.
- Explică pe scurt ce faci înainte de fiecare pas și ce a ieșit după. Când îi ceri să ruleze ceva, dă comanda exactă.
- Planul complet al proiectului e în documentul „Cyberspace: AI construit de la 0 care se auto-îmbunătățește” (tabul „Cyberspace: Kronos + module” descrie arhitectura). README.md are pașii pentru prima seară.

## Nume
- Platforma se numește **Cyberspace**, iar nucleul ei se numește **Kronos** (folderul `kronos/`). Comenzile: `python -m kronos ...`.

## Arhitectura (nu o încălca)
- `kronos/` = registru, contracte, configurare, orchestrator, jurnal, paznic. **Se modifică doar cu aprobarea explicită a omului**, iar după orice schimbare toate testele trebuie să treacă.
- `kronos/` nu are voie să importe din `module/` (testul `teste/test_arhitectura.py` verifică). Modulele se încarcă doar din configurare (`pachet.fisier:Clasa`).
- `module/` = piese înlocuibile. Fiecare clasă are `MANIFEST` cu nume, port, versiune, versiune_contract.
- Un modul nou intră doar dacă trece `teste_contracte/` (adaugă-l în lista `MODULE` de acolo).
- `module/examen_bpb.py` = examenul. **Nu-l modifica fără aprobarea omului.** Paznicul blochează experimentele dacă se schimbă; după o schimbare aprobată: `python -m kronos aproba-examen --config ...`.
- `lucru/` = jurnal, modele salvate, amprente. Nu șterge și nu edita de mână jurnalul.

## Cum lucrezi
- După fiecare schimbare: `python -m pytest`. Nu spune „gata” dacă testele nu trec.
- Fă un commit Git după fiecare pas reușit, cu mesaj în română.
- Laptopul: ASUS TUF F15, RTX 3060 Laptop 6 GB, 64 GB RAM, Windows 11. Ține memoria video sub ~5,5 GB.
- Dacă ceva nu merge, explică ce s-a întâmplat și propune 1–2 variante; nu ocoli în tăcere testele sau paznicul.
