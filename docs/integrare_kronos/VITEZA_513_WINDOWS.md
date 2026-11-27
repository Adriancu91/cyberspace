# Viteza lui #513 în PyTorch, Windows, RTX 3070 Ti (S130, C-153, 20 nov 2026 17:08)

Modelul: experimentul **#513** (linia `w2_romana_r1`, clasa `module.model_muon:ModelGPTConversatieMuon`; 12 straturi,
12 capete, 768, context 512, vocabular 16.384), încărcat exact ca la exportul KGR1 (`unelte/exporta_greutati.py
--experiment 513`: fișa din jurnal, `lucru/stocare/modele/experiment_513.pt`, tokenizerul din model).
Textul `Buna ziua` (simbolurile de intrare `[66, 2612, 7464]`), **16 simboluri noi, greedy (argmax)**. Fiecare simbol
recalculează tot textul. Pentru fiecare variantă: 1 rulare de încălzire, apoi 5 rulări, **mediana**;
`torch.cuda.synchronize()` înainte de fiecare oprire a ceasului (`time.perf_counter()`).

## Tabelul

| Variantă | Dispozitiv | Precizie | simb/s | ms/simbol | Cele 16 simboluri identice cu OS-ul |
|---|---|---|---:|---:|---|
| (a) fără memoria pașilor | placa (cuda) | FP32 | **129,12** | 7,745 | da |
| (b) cu memoria pașilor (KV cache) | placa | — | — | — | **nu are** (rețeaua `_GPT` n-are KV cache; nu s-a scris acum) |
| (c) fără memoria pașilor | procesorul (18 fire torch) | FP32 | **41,74** | 23,955 | da |
| (d) fără memoria pașilor | placa (cuda) | FP16 (copie în memorie) | **128,84** | 7,762 | da |

(d) în FP32 = varianta (a). Cele 5 rulări (secunde, pentru 16 simboluri):
(a) 0,1390 · 0,1385 · 0,1239 · 0,1232 · 0,1238; (c) 0,3799 · 0,3833 · 0,3965 · 0,3824 · 0,4007;
(d) FP16 0,1246 · 0,1239 · 0,1242 · 0,1446 · 0,1167.

Simbolurile ieșite (toate variantele): `[44, 10, 73, 2524, 10766, 1438, 1505, 1428, 1765, 99, 1547, 3644, 44, 10, 15879, 1505]`
= cele așteptate; textul: `",\nImi doresc sa ma intorc la mine,\nSa ma"`.

Memoria plăcii: `torch.cuda.max_memory_allocated` 387,6 MB la (a); 589,3 MB la (d) (pe placă erau atunci ambele copii,
FP32 și FP16). `nvidia-smi` după măsurare: 1.542 MiB folosiți din 8.192, 34 °C.

## Comparația cu `os-322` (doar cifre)

| Unde | simb/s |
|---|---:|
| Cyber Universe OS, cu driverul (`os-322`) | 94,84 |
| Cyber Universe OS, placa singură (`os-322`) | 381,98 |
| Windows, PyTorch, placa FP32, fără KV cache (a) | 129,12 |
| Windows, PyTorch, placa FP16, fără KV cache (d) | 128,84 |
| Windows, PyTorch, procesorul FP32, fără KV cache (c) | 41,74 |

## Versiunile

- Python 3.12.10; PyTorch 2.14.1+cu132 (CUDA 13.2 în torch); cuDNN 92400
- Driverul NVIDIA 616.56 (KMD 616.56, CUDA UMD 13.4)
- Placa: NVIDIA GeForce RTX 3070 Ti, 8.192 MiB
- Procesorul: `Intel64 Family 6 Model 85 Stepping 7, GenuineIntel`, 36 fire logice; torch a folosit 18 fire
- Windows-11-10.0.26300-SP0

## Starea plăcii în timpul variantei (a) (`nvidia-smi -q -d PERFORMANCE,CLOCK`, ieșirea întreagă)

```
==============NVSMI LOG==============

Timestamp                                              : Fri Nov 20 17:08:54 2026
Driver Version                                         : 616.56 [Deprecated; will be removed in CUDA 14.0. Use KMD Version instead]
CUDA Version                                           : 13.4 [Deprecated; will be removed in CUDA 14.0. Use CUDA UMD Version instead]
KMD Version                                            : 616.56
CUDA UMD Version                                       : 13.4

Attached GPUs                                          : 1
GPU 00000000:B3:00.0
    Performance State                                  : P2
    Clocks Event Reasons
        Idle                                           : Not Active
        Applications Clocks Setting                    : Not Active
        SW Power Cap                                   : Not Active
        HW Slowdown                                    : Not Active
            HW Thermal Slowdown                        : Not Active
            HW Power Brake Slowdown                    : Not Active
        Sync Boost                                     : Not Active
        SW Thermal Slowdown                            : Not Active
        Display Clock Setting                          : Not Active
        Board Limit                                    : Not Active
        Reliability                                    : Not Active
    Clocks Event Reasons Counters
        SW Power Capping                               : 271102427 us
        Sync Boost                                     : 0 us
        SW Thermal Slowdown                            : 0 us
        HW Thermal Slowdown                            : 0 us
        HW Power Braking                               : 0 us
    Sparse Operation Mode                              : N/A
    Clocks
        Graphics                                       : 1785 MHz
        SM                                             : 1785 MHz
        Memory                                         : 9251 MHz
        Video                                          : 1560 MHz
    Applications Clocks
        Graphics                                       : Requested functionality has been deprecated
        Memory                                         : Requested functionality has been deprecated
    Default Applications Clocks
        Graphics                                       : Requested functionality has been deprecated
        Memory                                         : Requested functionality has been deprecated
    Deferred Clocks
        Memory                                         : N/A
    Max Clocks
        Graphics                                       : 2115 MHz
        SM                                             : 2115 MHz
        Memory                                         : 9501 MHz
        Video                                          : 1950 MHz
    Max Customer Boost Clocks
        Graphics                                       : N/A
    SM Clock Samples
        Duration                                       : Not Found
        Number of Samples                              : Not Found
        Max                                            : Not Found
        Min                                            : Not Found
        Avg                                            : Not Found
    Memory Clock Samples
        Duration                                       : Not Found
        Number of Samples                              : Not Found
        Max                                            : Not Found
        Min                                            : Not Found
        Avg                                            : Not Found
    Clock Policy
        Auto Boost                                     : N/A
        Auto Boost Default                             : N/A
    DLA Clocks
        Engine                                         : N/A
        Max Engine                                     : N/A
```

## Comanda exactă

```
.venv/Scripts/python -X utf8 unelte/viteza_inferenta.py --experiment 513 --iesire lucru/s130/s130.json --asteptat 44,10,73,2524,10766,1438,1505,1428,1765,99,1547,3644,44,10,15879,1505 --kgr lucru/export/kronos_513_q8_0.kgr
```

Rezultatul complet: `lucru/s130/s130.json` (doar local). Durata totală: 6,5 s.

## SHA-256, înainte = după

- `lucru/stocare/modele/experiment_513.pt`: `605c4084f0a5db125b1e6c2c037b8e3d96abd17c1d62ec76efe439ecaba58b2c` (neschimbat)
- `lucru/export/kronos_513_q8_0.kgr`: `66f734b3136206d1be8825b1188b1a90f0c5b00c2e19746547f327f9b95c5859` (neschimbat)

---

# S142 — cu memoria de context (KV cache) și FP16/bf16 (C-168 punctul 7, 27 nov 2026 22:01)

Același model #513, același text `Buna ziua` (intrarea `[66, 2612, 7464]`), greedy. Unealta nouă
`unelte/viteza_scris_kv.py` (memoria de context scrisă în unealtă, aceleași greutăți; pe procesor, cu memorie = fără
memorie, logit-urile diferă cel mult 1,8e-5). Pentru fiecare variantă: 1 rulare de încălzire, 5 rulări, **mediana**,
`torch.cuda.synchronize()` înainte de fiecare oprire a ceasului; fiecare variantă într-un proces nou.
FP16/bf16 = o copie a modelului în memorie (nimic salvat).

## Tabelul S142

| Variantă | Precizie | Memoria de context | 16 simb.: simb/s | ms/simbol | 256 simb.: simb/s | ms/simbol | Memoria max (16 / 256) | Primele 16 simboluri = cele așteptate |
|---|---|---|---:|---:|---:|---:|---|---|
| (a) martorul (= S130) | FP32 | nu | **132,55** | 7,544 | 128,42 | 7,787 | 389,6 / 418,5 MB | da |
| (b) | FP32 | da | 159,65 | 6,264 | 151,23 | 6,612 | 388,2 / 421,9 MB | da |
| (c) | FP16 | da | 159,43 | 6,272 | 158,44 | 6,312 | 209,1 / 226,0 MB | da |
| (d) | bf16 | da | **160,05** | 6,248 | 159,44 | 6,272 | 209,1 / 226,0 MB | da |

Cele 5 rulări (secunde), 16 simboluri: (a) 0,1258 · 0,1235 · 0,1205 · 0,1207 · 0,1198; (b) 0,0999 · 0,1002 · 0,1004 ·
0,0997 · 0,1002; (c) 0,1004 · 0,1013 · 0,1004 · 0,0998 · 0,0996; (d) 0,0996 · 0,0996 · 0,1003 · 0,1000 · 0,1026.
256 simboluri: (a) 1,985 · 1,994 · 2,082 · 2,010 · 1,986; (b) 1,693 · 1,697 · 1,686 · 1,686 · 1,760;
(c) 1,621 · 1,616 · 1,617 · 1,599 · 1,598; (d) 1,610 · 1,607 · 1,606 · 1,589 · 1,593.

Simbolurile la 16 (toate cele 4 variante): `[44, 10, 73, 2524, 10766, 1438, 1505, 1428, 1765, 99, 1547, 3644, 44, 10, 15879, 1505]`.
Textul la 256 de simboluri începe cu `",\nImi doresc sa ma intorc la mine,\nSa ma intorc la mine,\nSa ma intorc la mine,…"`.

**Cea mai bună rețetă Windows** (pragul pre-înregistrat: cele mai multe simb/s la 16 simboluri dintre (b)–(d)):
**(d) bf16 cu memoria de context, 160,05 simb/s.** (b), (c), (d) sunt la 0,4 % una de alta.

## Comparația cu OS-ul (doar cifre)

| Unde | simb/s (16 simboluri) |
|---|---:|
| Cyber Universe OS (cifra din analiza din 27 nov) | 351 |
| Windows, PyTorch, placa, bf16 cu memoria de context (S142 d) | 160,05 |
| raportul OS / Windows | **×2,19** |

## Versiunile (S142)

Python 3.12.10; PyTorch 2.14.1+cu132 (CUDA 13.2 în torch); cuDNN 92400; driverul NVIDIA 616.56; RTX 3070 Ti 8.192 MiB;
Windows-11-10.0.26300-SP0. Fără `torch.compile`, nimic instalat.

## Comenzile S142

```
.venv/Scripts/python -X utf8 unelte/viteza_scris_kv.py --dispozitiv cuda --precizie f32  --cache nu --simboluri 16  --text "Buna ziua" --kgr lucru/export/kronos_513_q8_0.kgr --iesire lucru/s142/B_a_16
.venv/Scripts/python -X utf8 unelte/viteza_scris_kv.py --dispozitiv cuda --precizie f32  --cache da --simboluri 16  --text "Buna ziua" --kgr lucru/export/kronos_513_q8_0.kgr --iesire lucru/s142/B_b_16
.venv/Scripts/python -X utf8 unelte/viteza_scris_kv.py --dispozitiv cuda --precizie f16  --cache da --simboluri 16  --text "Buna ziua" --kgr lucru/export/kronos_513_q8_0.kgr --iesire lucru/s142/B_c_16
.venv/Scripts/python -X utf8 unelte/viteza_scris_kv.py --dispozitiv cuda --precizie bf16 --cache da --simboluri 16  --text "Buna ziua" --kgr lucru/export/kronos_513_q8_0.kgr --iesire lucru/s142/B_d_16
```
la fel cu `--simboluri 256` (ieșirile `B_<a|b|c|d>_256`). SHA-256 înainte = după la toate 8 (aceleași ca mai sus).
