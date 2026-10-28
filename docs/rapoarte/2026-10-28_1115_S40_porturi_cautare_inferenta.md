# S40 — Porturile opționale `cautare` și `inferenta` + două module-adaptor (28 oct 2026, 11:15)

**Stare: gata.** Sesiune Claude Code deschisă de Adrian pe workstation, cu aprobarea lui explicită pentru schimbarea din
`kronos/` (27 oct 23:49 „Da”, și din nou azi, 28 oct, cu porturile **opționale**). Făcut S40 complet (S40a + S40b într-un singur commit).

## Pe scurt
- Porturile noi sunt **opționale**: `PORTURI` a rămas neschimbat, iar `PORTURI_OPTIONALE = ("cautare", "inferenta")` e separat.
  O configurare **poate** avea `[porturi.cautare]` / `[porturi.inferenta]`, dar nu e obligată → toate configurările vechi merg neschimbate.
  De aceea nu mai apar cele 160 de teste picate din încercarea din cloud (acolo porturile noi deveniseră obligatorii).
- `VERSIUNE_CONTRACTE` rămâne 1.
- În `kronos/` s-au schimbat doar 3 fișiere: `contracte.py`, `registru.py` (validarea portului), `config.py` (porturi necunoscute).
  **Neatinse:** orchestratorul, `cli.py`, paznicul, `module/examen_bpb.py`, jurnalul, modelele.
  (Orchestratorul și `cli` merg doar pe `PORTURI`, deci nu încarcă porturile opționale și nu trebuiau schimbate.)
- **Teste: 979 trec, 1 sărit, 0 picate** (`CUDA_VISIBLE_DEVICES=-1 python -m pytest`; înainte 965). Cel sărit e profesorul Qwen (cere placa), ca înainte.

## Modulele noi (`module/`)
| Modul | Port | Ce face | Refolosește (import, nu copie) |
|---|---|---|---|
| `module/cautare_e3.py:CautareE3` | `cautare` | `cauta(intrebare, k)` → cel mult `k` bucăți cu `text`, `scor` (+ `rowid`, `articol`, `sursa`), ordonate; `statistici()` | `unelte/e3_memorie.py` (căutarea S25, varianta implicită `nume_obligatorii_liste`) + `unelte/e3_reordonare.py:cauta_rrf` (indexul cu rădăcini + RRF k=60 + paginile-listă la urmă) |
| `module/inferenta_kgr1.py:InferentaKGR1` | `inferenta` | `logits(simboluri)` (ultima poziție; peste context ia ultimele `context` simboluri), `genereaza(simboluri, cate)` (greedy), `statistici()` (vocabular, context, format F32/Q8_0, …) | `unelte/inferenta_bruta.py:MotorBrut` |

- Ambele: `MANIFEST` cu versiune 0.1.0, versiune_contract 1, `resurse = {"gpu": False}`. Merg doar pe procesor.
- `CautareE3` e varianta **fără judecător-model** (adică fără reordonarea „rrf_reord” de la S29/S33, care cere placa). Bazele SQLite
  se deschid doar pentru citire. Scorul = `1 / (60 + loc)` în lista unită (mai mare = mai sus).
- Setările implicite arată spre fișierele reale: `lucru/e3/index.sqlite`, `lucru/e3/index_radacini.sqlite`, `lucru/e3/liste_s25.json`,
  respectiv `lucru/export/kronos_459_q8_0.kgr`.
- Fișele comune din Cyber Hub scrise cu `unelte/module_toml.py`: `module/manifeste/cautare_e3.toml`, `module/manifeste/inferenta_kgr1.toml`
  (descrierea și `[ofera]` completate de mine; unealta le păstrează).

## Testele noi
- `teste_contracte/test_contracte.py`: 3 intrări noi în `MODULE` (`CautareE3` pe o bază SQLite de 5 bucăți creată în test;
  `InferentaKGR1` pe modelul minuscul din S39 `integrare/kronos/vectori/mic_f32.kgr`, cu desfacere `la_incarcare` și `la_pas`)
  + verificările `_cautare` și `_inferenta` (ordine stabilă, cel mult k, scoruri descrescătoare; greedy, determinist, peste context nu crapă).
  Fără bazele mari din `lucru/`.
- `teste/test_porturi_optionale.py` (9 teste): porturile opționale sunt separate de `PORTURI`; `config/proba.toml` merge neschimbat;
  o configurare **poate** avea `[porturi.inferenta]`; un port greșit (`cautari`) e tot refuzat (și de config, și de registru);
  **modulul de inferență dă exact aceleași logit-uri și aceleași simboluri generate ca `MotorBrut`** (egalitate exactă, pe F32, Q8_0
  `la_incarcare` și Q8_0 `la_pas`, inclusiv o intrare cât tot contextul); listă goală → eroare clară; bază lipsă / variantă greșită → „Setări greșite”.
- La prima rulare a suitei au picat 3 teste din `teste/test_module_toml.py` (lipseau fișele `.toml` ale modulelor noi). Le-am scris cu
  unealta și am rerulat totul: 979 trec.

## Diff-ul complet din `kronos/`
```diff
diff --git a/kronos/config.py b/kronos/config.py
index 913b14e..fde93d8 100644
--- a/kronos/config.py
+++ b/kronos/config.py
@@ -11,7 +11,7 @@ from dataclasses import dataclass, field
 from pathlib import Path
 from typing import Any
 
-from .contracte import PORTURI
+from .contracte import PORTURI, PORTURI_OPTIONALE
 
 
 class EroareConfig(Exception):
@@ -61,7 +61,7 @@ def citeste_config(cale: str | Path) -> Config:
     lipsa = [p for p in PORTURI if p not in porturi]
     if lipsa:
         raise EroareConfig(f"În „{cale}” lipsesc porturile: {', '.join(lipsa)}")
-    necunoscute = [p for p in porturi if p not in PORTURI]
+    necunoscute = [p for p in porturi if p not in PORTURI + PORTURI_OPTIONALE]
     if necunoscute:
         raise EroareConfig(f"În „{cale}” sunt porturi necunoscute: {', '.join(necunoscute)}")
     for port, valoare in porturi.items():
diff --git a/kronos/contracte.py b/kronos/contracte.py
index 810c0c2..3665abb 100644
--- a/kronos/contracte.py
+++ b/kronos/contracte.py
@@ -29,6 +29,13 @@ PORTURI = (
     "memorie",
 )
 
+# Porturi pe care o configurare le POATE avea, dar nu e obligată (configurările vechi merg neschimbate).
+# Orchestratorul nu le încarcă singur; le folosește cine are nevoie de ele.
+PORTURI_OPTIONALE = (
+    "cautare",
+    "inferenta",
+)
+
 
 @dataclass
 class Propunere:
@@ -170,6 +177,38 @@ class Memorie(Protocol):
     def statistici(self) -> dict[str, Any]: ...
 
 
+@runtime_checkable
+class Cautare(Protocol):
+    """Căutarea de bucăți de text: o întrebare → bucățile cele mai potrivite, în ordine.
+
+    Fiecare bucată e un dicționar cu cel puțin `text` (str) și `scor` (float, mai mare = mai potrivit).
+    Aceeași întrebare dă mereu aceeași ordine (fără întâmplare).
+    """
+
+    def cauta(self, intrebare: str, k: int) -> list[dict[str, Any]]:
+        """Cel mult `k` bucăți, de la cea mai potrivită la cea mai puțin potrivită."""
+        ...
+
+    def statistici(self) -> dict[str, Any]: ...
+
+
+@runtime_checkable
+class Inferenta(Protocol):
+    """Un model gata antrenat, doar citit: simboluri → următorul simbol. Nu antrenează nimic."""
+
+    def logits(self, simboluri: list[int]) -> list[float]:
+        """Scorul fiecărui simbol din vocabular pentru poziția de după ultimul simbol primit."""
+        ...
+
+    def genereaza(self, simboluri: list[int], cate: int) -> list[int]:
+        """Exact `cate` simboluri noi, mereu cel mai probabil (fără întâmplare, același rezultat la fiecare rulare)."""
+        ...
+
+    def statistici(self) -> dict[str, Any]:
+        """Cel puțin mărimea vocabularului, contextul și formatul greutăților (de ex. F32 sau Q8_0)."""
+        ...
+
+
 CONTRACT_PENTRU_PORT: dict[str, type] = {
     "model": Model,
     "date": Date,
@@ -181,6 +220,8 @@ CONTRACT_PENTRU_PORT: dict[str, type] = {
     "interfata": Interfata,
     "traducere": Traducere,
     "memorie": Memorie,
+    "cautare": Cautare,
+    "inferenta": Inferenta,
 }
 
 
diff --git a/kronos/registru.py b/kronos/registru.py
index 1acab2b..f502c7a 100644
--- a/kronos/registru.py
+++ b/kronos/registru.py
@@ -10,7 +10,7 @@ import importlib
 from dataclasses import dataclass
 from typing import Any
 
-from .contracte import CONTRACT_PENTRU_PORT, PORTURI, VERSIUNE_CONTRACTE, membrii_contract
+from .contracte import CONTRACT_PENTRU_PORT, PORTURI, PORTURI_OPTIONALE, VERSIUNE_CONTRACTE, membrii_contract
 
 CHEI_MANIFEST = ("nume", "port", "versiune", "versiune_contract")
 
@@ -36,8 +36,8 @@ class Registru:
     def creeaza(self, port: str, cale: str, setari: dict[str, Any] | None = None) -> ModulIncarcat:
         """Încarcă și verifică un modul, FĂRĂ să-l pună pe port."""
         setari = dict(setari or {})
-        if port not in PORTURI:
-            raise EroareModul(f"Portul „{port}” nu există. Porturi valide: {', '.join(PORTURI)}")
+        if port not in PORTURI + PORTURI_OPTIONALE:
+            raise EroareModul(f"Portul „{port}” nu există. Porturi valide: {', '.join(PORTURI + PORTURI_OPTIONALE)}")
         if ":" not in cale:
             raise EroareModul(f"Calea „{cale}” trebuie să fie de forma pachet.fisier:Clasa")
 
```

## Ce aștept de la tine (Adrian)
- Nimic obligatoriu. Dacă vrei, supraveghetorul poate trece `S40a`/`S40b` pe `gata` (am scris în coadă).
- Folosirea efectivă a porturilor (de ex. un `[porturi.cautare]` într-o configurare, sau Cyber Universe OS cu `InferentaKGR1`) e o sarcină nouă, cu „da”-ul tău.
