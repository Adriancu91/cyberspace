# Pre-înregistrare: S86: memoria plăcii la modelul mare, Muon față de AdamW

<!-- scrisa: 2026-11-07T03:02:09 -->
*Scrisă la 2026-11-07 03:02, înainte de rulare. După ce rularea a început, textul de mai jos nu se mai schimbă; la închidere
se adaugă doar secțiunea „Ce a ieșit” (python unelte/preinregistrare.py --inchide memorie_mare).*

## Întrebarea

Cu Muon (o singură stare pe matricile straturilor) în loc de AdamW (două stări), scade vârful memoriei PyTorch la
antrenarea lui Kronos de 24 de straturi destul cât să nu mai fim la limita plăcii? Și (pasul 3b) crește memoria ținută
de la o „oră” la alta, ca la căderile S77c/S85 de la testul rapid al orei 3?

## Ce rulează

- Sarcina S86 din plan/coada.md (C-85 pasul 2, aprobată de Adrian 6 nov 17:56), pornită de executant prin cascadă, în
  noaptea 6→7 nov, după 03:00 (partea pe placă ~1 oră, cel târziu până la 07:00).
- Unealta nouă `unelte/masoara_memorie_mare.py toate`: modelul de 24 de straturi construit ca în
  `unelte/antrenare_recalcul.py` (recalcul pe straturi, plafon PyTorch 5.800 MB), setările din
  `config/conv_w2_mare_24f.toml`, pornind dintr-o COPIE a `lucru/w2_mare/gpt_24.pt` în `lucru/memorie_mare/<varianta>/`.
- O „oră” scurtă = 50 de pași de optimizator (pasi_max = 50 × adunare_loturi), apoi validarea (examenul
  `ExamenBpb().examineaza`, doar chemat, + `dupa_examen`: salvarea stării în copie și examenele suplimentare, cu
  profesorul), apoi testul rapid al orei următoare (model nou, 2 secunde de antrenare + 500 de caractere), ca în
  orchestrator. 50 de pași în loc de ~200, ca partea pe placă să fie cât mai aproape de „durată maximă: 1 oră”
  (vârfurile apar de la primul pas de optimizator; o „oră” scurtă tot ține ~8 min, din care ~4 min examenele).
- Proba cap-coadă de dinainte (03:05, varianta b, 1 pas, 2 repetări, `lucru/memorie_mare/proba/`, nu intră în
  verdict): ora 1 antrenare vârf 2.289 MB PyTorch, validarea 5.484 MB (nvidia-smi 6.361), ora 2 antrenare 4.390 MB,
  apoi out of memory la validarea orei 2. Deci memoria pare să crească de la o oră la alta chiar și cu Muon.
- Variantele, fiecare în proces nou: (a) adamw, lot 4 × 24, de 3 ori la rând (pasul 3b); (b) muon, lot 4 × 24;
  (c) muon, lot 6 × 16; (d) muon, lot 12 × 8. Dacă la (a) memoria crește de la o oră la alta (alocatul după testul
  rapid urcă cu > 100 MB) sau (a) cade: (a_golit) = (a) cu `del` + `gc.collect()` + `torch.cuda.empty_cache()` după
  fiecare test rapid, tot de 3 ori. Setările Muon: cele implicite din `module/model_muon.py` (rata_muon 0,02,
  momentum 0,95 Nesterov, 5 pași Newton-Schulz, scadere_muon 0).
- Procesul părinte oprește copilul peste 7.000 MB nvidia-smi sau la 83 °C. Nimic în jurnal, niciun model păstrat.

## Așteptările, în cifre

- Pe hârtie: ~183 mil. parametri; AdamW ține 2 × 4 octeți/parametru ≈ 1,46 GB; Muon ține 4 octeți pe matricile
  straturilor (~170 mil. ≈ 0,68 GB) + AdamW pe rest (~13 mil. ≈ 0,10 GB) ≈ 0,78 GB. Câștig așteptat ≈ 650–700 MB la
  vârful PyTorch (max_memory_allocated) la antrenare.
- **Pragul (singurul, DA/NU, scris de supraveghetor):** „(b) muon lot 4 scade vârful PyTorch la antrenare cu cel puțin
  400 MB față de (a)” → DA dacă varf_alocat_mb la antrenare (b, ora 1) ≤ varf_alocat_mb (a, ora 1) − 400; altfel NU.
- Așteptare (fără prag): (c) și (d) încap sub 6.700 MB nvidia-smi; (a) are la ora 2–3 alocatul după testul rapid mai
  mare decât la ora 1 (starea AdamW încărcată din fișier după ora 1).

## Ce ar infirma așteptările

- NU: vârful PyTorch la antrenare (b) e mai mic decât (a) cu mai puțin de 400 MB (sau (b) cade / trece de 6.700 MB).
- Pentru 3b (informativ): alocatul după testul rapid la (a) rămâne în ±100 MB de la ora 1 la ora 3 → memoria nu crește,
  căderea de la ora 3 are altă cauză.
