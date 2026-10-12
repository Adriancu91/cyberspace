# Prima oră pe workstation (luni, 12 octombrie 2026)

*Lista de verificat din `docs/MUTARE_workstation.md`, secțiunea 7, cu cifrele măsurate. Nu s-a pornit nicio antrenare
lungă, nici CONTINUUM, nici tokenizer-ul nou.*

## Calculatorul

- Windows 11 Pro, **RTX 3070 Ti** 8 GB (nu 3070 simplu), driver NVIDIA 616.56, 128 GB RAM, 241 GB liberi pe C: la început.
- Proiectul e în `C:\Kronos\cyberspace` (main) și `C:\Kronos\cyberspace-cod` (kronos-cod, `git worktree`).
- Git 2.55, clonat cu `core.autocrlf=false`: toate fișierele text au capete LF, ca pe GitHub.
- Python 3.12.10 pe 64 de biți; `.venv` din `requirements.txt`; `pip freeze` identic cu laptopul (44 de pachete).
- Fusul orar al Windows era pe Pacific (SUA); pus pe București.

## Ce a ieșit

| Pas | Rezultat |
|---|---|
| Arhiva (221 de fișiere, 26,21 GB) | dezarhivată după `CITESTE.txt`; niciun fișier nu s-a suprapus cu codul din Git |
| Tag-urile școlii | 16, identice în copia de rezervă Git, pe GitHub și aici |
| `python unelte/verifica_mediu.py` | „Totul e în regulă” |
| `python -m pytest`, main | **542 trecute** din 542 (pe laptop: 542), 2 min 38 s, cu placa liberă |
| `python -m pytest`, cyberspace-cod | **655 trecute** din 655, 3 min 26 s |
| Amprenta examenului | identică cu cea aprobată pe laptop (`0ca9cf74…d3028`); `git diff` gol; nu a fost nevoie de `aproba-examen` |
| Amprentele școlii | toate 4 identice cu cele aprobate pe 8 octombrie; nu a fost nevoie de `--aproba-amprente` |

## Reproducerea cifrelor

| Model | val_bpb aici | val_bpb pe laptop | Diferența | Fapte noi aici | Fapte noi pe laptop |
|---|---|---|---|---|---|
| #262 | 0,4304267 | 0,4304289 | −0,0000022 | 59 (62 cu sinonime, 36 de fapte știute) | 59 (62, 36) |
| #295 | 0,4248823 | 0,4248826 | −0,0000003 | 64 (68 cu sinonime, 39 de fapte știute) | 64 (68, 39) |

- Examenul e cel din `module/examen_bpb.py`, pe primele 100.000 de caractere din `date/tinystories_tot/validare.txt`
  (aceiași octeți ca `date/tinystories_r2/validare.txt`). Faptele noi: cele 150 de întrebări din
  `date/fapte/examen_nou.json`.
- **Măsurate cu un script de citire, nu cu `unelte/examen_fapte_nou.py`, și neînregistrate în jurnal.** Unealta pică
  aici (vezi mai jos).

## Problema găsită: căile de pe laptop din jurnal

- În `lucru/jurnal/experimente.jsonl`, `model_salvat` e calea întreagă de pe laptop, de exemplu
  `C:\Users\XyZ\Desktop\ProjectX\cyberspace\lucru\stocare\modele\experiment_262.pt`. Aici calea nu există.
- `python unelte/examen_fapte_nou.py --experiment 262` se oprește cu `FileNotFoundError`, înainte să scrie ceva.
- Aceeași cale o citesc: `unelte/modele_salvate.py`, `unelte/antrenare_lunga.py` (`--porneste-din`),
  `unelte/test_profesor.py` și `kronos/cli.py` (`kronos scrie`).
- Jurnalul nu s-a editat și nimic nu s-a ocolit. Reparația o alege Adrian.

## Probele de memorie (câte 5 minute)

Rețeaua e `_GPT` din `module/model_gpt.py`, cu pasul de antrenare al modelului (bf16, AdamW), pe simboluri la
întâmplare: memoria și viteza nu depind de text, iar W2 și W3 cer vocabularul de 16.384, care nu există încă. Nu s-a
salvat nimic și nu s-a scris în jurnal.

| | W1 | W2 | W3 |
|---|---|---|---|
| Straturi × emb, context, lot, vocabular | 12 × 768, 256, 24, 4.096 | 12 × 768, 512, 12, 16.384 | 16 × 768, 512, 8, 16.384 |
| Parametri | 88,4 M | 98,0 M | 126,4 M |
| Memoria video maximă, cum o măsoară paznicul | **3.904 MB** | **4.793 MB** | **4.743 MB** |
| Memoria rezervată de PyTorch | 4.180 MB | 5.498 MB | 5.464 MB |
| Toată placa în `nvidia-smi`, cu Windows (~780 MB) | 5.147 MB | 6.465 MB | 6.431 MB |
| Pași pe secundă | **6,96** | **5,93** | **6,46** |
| Simboluri pe pas | 6.144 | 6.144 | 4.096 |
| Milioane de simboluri pe oră | 154 | 131 | 95 |
| Temperatura maximă | **63 °C** | **63 °C** | **64 °C** |

- Toate trei stau sub limita paznicului (7.000 MB) și departe de 83 °C; placa a lucrat la 100%.
- Viteza e peste estimarea din document (110 / 95 / 80 de milioane pe oră).
- W2 ajunge la 6,47 GB pe toată placa, cu Windows cu tot. Documentul spunea „dacă W2 trece de 6,5 GB în realitate,
  lotul scade la 8”: e chiar la margine. Cu Chrome sau alte programe deschise, poate trece.
- O antrenare adevărată mai adaugă puțin (examenele de la oră, profesorul rulează după, nu în același timp).

## Ce a rămas nefăcut

- `lucru/cache` (simbolurile lui TinyStories) nu s-a regenerat: se face la prima antrenare adevărată.
- Configurările W2 și W3 nu s-au scris: depind de tokenizer-ul nou. `config/ws_w1.toml` există, nepornită.
