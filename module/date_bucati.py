"""Date de antrenare pe bucăți (S98, C-85 pasul 5): simbolurile gata făcute, scrise de unelte/date_bucati.py (S96) în
`bucata_NNNNN.bin` + `index.json`, citite prin mmap. În memorie stau doar paginile atinse de ferestrele cerute, nu șirul
întreg și nu textul brut.

- Amprenta datelor vine din `index.json` (SHA-256 al șirului întreg + SHA-256 al tokenizerului), fără să citească textul
  brut. La pornire modulul recalculează SHA-256 pe fiecare bucată și pe tot șirul și **refuză să pornească** dacă ceva nu
  se potrivește cu indexul (bucată lipsă, stricată, index parțial, alt tokenizer decât cel din `cale_tokenizer`).
- `sir_antrenare()`: șirul întreg văzut ca un singur tablou (`len(sir)`, `sir[a:b]` → tensor cu simbolurile, lipind o
  bucată de următoarea când felia cade la graniță). Are exact ce folosește bucla de antrenare la un tensor întreg.
- `lot(numar, context, generator)`: `numar` ferestre trase la sorți exact ca în bucla de antrenare de acum
  (`torch.randint(len - context - 1, (numar,), generator=generator)` pe tot șirul): intrarea = `context` simboluri,
  ținta = aceleași, mutate cu unu. Cu aceeași sămânță dă aceleași loturi ca tensorul întreg din lucru/cache.
- `text_antrenare()` / `text_validare()` (contractul portului „date”): validarea e fișierul text de până acum (mic).
  Antrenarea nu se dă ca text (4,8 GB): cu `previzualizare = true` dă doar începutul, decodat (pentru teste și privit);
  altfel spune clar că modelul trebuie să citească ferestrele, ca o antrenare să nu învețe din greșeală doar din
  previzualizare.

Legarea (S103, C-110, „da”-ul lui Adrian din 12 noiembrie 2026): modelele GPT care țin datele în RAM (model_continuu și
urmașii: conversație, Muon) văd că portul are `sir_antrenare()` și iau șirul de aici, fără text; în statistici scriu
amprenta acestor date. Un model care cere textul întreg (`date.text_antrenare()`) e refuzat în continuare.
Modulul NU e pus în nicio configurare în uz (doar în cea de probă); asta se face doar cu sarcina care o cere.
"""

from __future__ import annotations

import hashlib
import json
import operator
from pathlib import Path
from typing import Any

import numpy as np

VERSIUNE_INDEX = 1
TIPURI = {"int16": np.int16, "int32": np.int32}
BLOC_VERIFICARE = 16 * 2**20


def _sha256_fisier(cale: Path, peste_tot: Any = None) -> str:
    """SHA-256 al fișierului, citit pe blocuri (nu tot odată); `peste_tot` primește aceiași octeți (SHA-ul șirului)."""
    h = hashlib.sha256()
    with cale.open("rb") as f:
        while bloc := f.read(BLOC_VERIFICARE):
            h.update(bloc)
            if peste_tot is not None:
                peste_tot.update(bloc)
    return h.hexdigest()


class SirBucati:
    """Șirul de simboluri din mai multe bucăți, văzut ca unul singur: `len(sir)` și `sir[a:b]` (felie cu pasul 1).
    Capetele feliei pot fi numere sau tensori cu un singur element, ca în bucla de antrenare."""

    def __init__(self, dosar: Path, index: dict[str, Any]) -> None:
        self._dosar = dosar
        self._bucati = index["bucati"]
        self._inceputuri = np.array([b["inceput"] for b in self._bucati], dtype=np.int64)
        self._total = int(index["simboluri_total"])
        self._tip = np.dtype(TIPURI[index["tip"]]).newbyteorder("<")
        self._deschise: dict[int, np.ndarray] = {}

    def __len__(self) -> int:
        return self._total

    @property
    def tip(self) -> np.dtype:
        return self._tip

    def _bucata(self, i: int) -> np.ndarray:
        a = self._deschise.get(i)
        if a is None:
            a = np.memmap(self._dosar / self._bucati[i]["fisier"], dtype=self._tip, mode="r")
            self._deschise[i] = a
        return a

    def bucati_atinse(self, inceput: int, sfarsit: int) -> list[int]:
        """Numerele bucăților din care vine felia [inceput, sfarsit)."""
        if sfarsit <= inceput:
            return []
        prima = int(np.searchsorted(self._inceputuri, inceput, side="right")) - 1
        ultima = int(np.searchsorted(self._inceputuri, sfarsit - 1, side="right")) - 1
        return list(range(prima, ultima + 1))

    def felie(self, inceput: int, sfarsit: int) -> np.ndarray:
        """Simbolurile [inceput, sfarsit) ca tablou numpy nou (copie), cu tipul din index."""
        inceput, sfarsit = max(0, min(inceput, self._total)), max(0, min(sfarsit, self._total))
        iesire = np.empty(max(0, sfarsit - inceput), dtype=self._tip.newbyteorder("="))
        scris = 0
        for i in self.bucati_atinse(inceput, sfarsit):
            baza = int(self._inceputuri[i])
            a = self._bucata(i)
            de_la = max(inceput, baza) - baza
            pana_la = min(sfarsit, baza + len(a)) - baza
            iesire[scris:scris + pana_la - de_la] = a[de_la:pana_la]
            scris += pana_la - de_la
        if scris != len(iesire):  # pragma: no cover - indexul a fost verificat la pornire
            raise ValueError(f"felia [{inceput}, {sfarsit}) a dat {scris} simboluri în loc de {len(iesire)}")
        return iesire

    def __getitem__(self, cheie: Any) -> Any:
        import torch

        if not isinstance(cheie, slice) or cheie.step not in (None, 1):
            raise TypeError("șirul pe bucăți se citește doar cu felii cu pasul 1: sir[a:b]")
        inceput = 0 if cheie.start is None else operator.index(cheie.start)
        sfarsit = self._total if cheie.stop is None else operator.index(cheie.stop)
        if inceput < 0:
            inceput += self._total
        if sfarsit < 0:
            sfarsit += self._total
        return torch.from_numpy(self.felie(inceput, sfarsit))

    def inchide(self) -> None:
        self._deschise.clear()


class DateBucati:
    MANIFEST = {
        "nume": "date_bucati",
        "port": "date",
        "versiune": "0.1.0",
        "versiune_contract": 1,
        "resurse": {},
        "permisiuni": ["citire_fisier"],
    }

    def __init__(self, director: str, cale_validare: str, cale_tokenizer: str = "", previzualizare: bool = False,
                 simboluri_previzualizare: int = 20_000) -> None:
        d = Path(director)
        if not (d / "index.json").exists():
            raise ValueError(f"Nu găsesc „{director}/index.json”. Bucățile le face: python unelte/date_bucati.py scrie")
        if not Path(cale_validare).exists():
            raise ValueError(f"Nu găsesc textul de validare „{cale_validare}”")
        self.director = d
        self.cale_validare = cale_validare
        self.cale_tokenizer = cale_tokenizer
        self.previzualizare = previzualizare
        self.simboluri_previzualizare = simboluri_previzualizare
        self.index = json.loads((d / "index.json").read_text(encoding="utf-8"))
        self.verificare = self._verifica()
        if not self.verificare["ok"]:
            raise ValueError(f"Bucățile din „{director}” nu trec verificarea, nu pornesc: {self.verificare['gresite']}")
        self._sir = SirBucati(d, self.index)
        self._validare = Path(cale_validare).read_text(encoding="utf-8")
        if len(self._validare) < 100:
            raise ValueError("textul de validare e prea scurt")

    # --- verificarea de la pornire și amprenta --------------------------------------

    def _verifica(self) -> dict[str, Any]:
        """Indexul și bucățile, SHA cu SHA (ca `unelte/date_bucati.py verifica`), plus tokenizerul. Bucățile se citesc pe
        blocuri, deci RAM-ul rămâne mic."""
        index = self.index
        gresite: list[dict[str, str]] = []

        def gresit(fisier: str, problema: str) -> None:
            gresite.append({"fisier": fisier, "problema": problema})

        if index.get("versiune") != VERSIUNE_INDEX:
            gresit("index.json", f"versiune necunoscută: {index.get('versiune')}")
            return {"bucati": 0, "gresite": gresite, "ok": False}
        if index.get("tip") not in TIPURI or index.get("ordine_octeti") != "little":
            gresit("index.json", f"tip sau ordine de octeți necunoscute: {index.get('tip')}, {index.get('ordine_octeti')}")
            return {"bucati": 0, "gresite": gresite, "ok": False}
        if index.get("partial"):
            gresit("index.json", "indexul e parțial (lipsesc bucăți la coadă)")
        pe_simbol = np.dtype(TIPURI[index["tip"]]).itemsize
        tot = hashlib.sha256()
        asteptat = 0
        for b in index["bucati"]:
            cale = self.director / b["fisier"]
            if b["inceput"] != asteptat:
                gresit(b["fisier"], f"începe la {b['inceput']}, trebuia {asteptat}")
            asteptat = b["inceput"] + b["simboluri"]
            if not cale.exists():
                gresit(b["fisier"], "lipsește")
                continue
            if cale.stat().st_size != b["simboluri"] * pe_simbol:
                gresit(b["fisier"], "altă mărime decât în index")
                continue
            if _sha256_fisier(cale, tot) != b["sha256"]:
                gresit(b["fisier"], "SHA diferit")
        if asteptat != index["simboluri_total"]:
            gresit("index.json", f"bucățile au {asteptat} simboluri, indexul zice {index['simboluri_total']}")
        if not gresite and tot.hexdigest() != index["sha256_tot"]:
            gresit("(tot șirul)", "SHA diferit")
        if self.cale_tokenizer:
            din_index = (index.get("tokenizer") or {}).get("sha256")
            if not Path(self.cale_tokenizer).exists():
                gresit(self.cale_tokenizer, "tokenizerul lipsește")
            elif din_index is None:
                gresit("index.json", "indexul nu spune cu ce tokenizer s-au făcut simbolurile")
            elif _sha256_fisier(Path(self.cale_tokenizer)) != din_index:
                gresit(self.cale_tokenizer, "alt tokenizer decât cel cu care s-au făcut simbolurile")
        return {"bucati": len(index["bucati"]), "gresite": gresite, "ok": not gresite}

    def amprenta(self) -> str:
        """Amprenta datelor de antrenare, doar din index: SHA-256 al șirului de simboluri + SHA-256 al tokenizerului."""
        tokenizer = (self.index.get("tokenizer") or {}).get("sha256") or ""
        return hashlib.sha256(f"{self.index['sha256_tot']}:{tokenizer}".encode("ascii")).hexdigest()[:16]

    def descriere(self) -> dict[str, Any]:
        """Ce date sunt acestea (pentru jurnal și rapoarte)."""
        return {"amprenta": self.amprenta(), "sha256_tot": self.index["sha256_tot"],
                "tokenizer": self.index.get("tokenizer"), "simboluri": len(self._sir), "tip": self.index["tip"],
                "bucati": len(self.index["bucati"]), "marime_bucata": self.index["marime_bucata"],
                "sursa": self.index.get("sursa")}

    # --- simbolurile -----------------------------------------------------------------

    def numar_simboluri(self) -> int:
        return len(self._sir)

    def sir_antrenare(self) -> SirBucati:
        return self._sir

    def ferestre(self, pozitii: Any, context: int) -> tuple[Any, Any]:
        """Ferestrele care încep la `pozitii`: (intrarea, ținta), fiecare de mărimea len(pozitii) × context, int64."""
        import torch

        if context < 1:
            raise ValueError("context trebuie să fie cel puțin 1")
        bucati = []
        for p in pozitii:
            p = int(p)
            if not 0 <= p <= len(self._sir) - context - 1:
                raise ValueError(f"fereastra de la {p} iese din șir")
            bucati.append(self._sir.felie(p, p + context + 1).astype(np.int64))
        toate = torch.from_numpy(np.stack(bucati)) if bucati else torch.zeros((0, context + 1), dtype=torch.int64)
        return toate[:, :context], toate[:, 1:]

    def lot(self, numar: int, context: int, generator: Any) -> tuple[Any, Any]:
        """Un lot tras la sorți exact ca în bucla de antrenare: locurile cu torch.randint pe tot șirul."""
        import torch

        if len(self._sir) <= context + 1:
            raise ValueError("șirul de antrenare e mai scurt decât contextul")
        pozitii = torch.randint(len(self._sir) - context - 1, (numar,), generator=generator)
        return self.ferestre(pozitii, context)

    # --- contractul portului „date” ---------------------------------------------------

    def text_antrenare(self) -> str:
        if not self.previzualizare:
            raise RuntimeError("date_bucati dă ferestre de simboluri, nu text: modelul trebuie să folosească "
                               "sir_antrenare() / lot(). Textul e doar o previzualizare (setarea previzualizare = true).")
        if not self.cale_tokenizer:
            raise ValueError("previzualizarea cere cale_tokenizer")
        from module.tokenizer_bpe import TokenizerBPE

        tok = TokenizerBPE.incarca(self.cale_tokenizer)
        return tok.decodeaza(int(x) for x in self._sir.felie(0, self.simboluri_previzualizare))

    def text_validare(self) -> str:
        return self._validare
