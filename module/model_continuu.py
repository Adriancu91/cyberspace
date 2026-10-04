"""GPT-ul care continuă de unde a rămas (Etapa M3, testul în trei trepte: martorul „GPT la plafon”).

Ca model_gpt, plus trei lucruri pentru antrenări lungi, pe bucăți de câte 10 minute:
1. Cu cale_stare: fiecare experiment pornește din starea salvată de cel dinainte (greutățile, optimizatorul, câți pași
   s-au făcut) și își salvează starea nouă după examen. Doar experimentul adevărat ajunge la examen; testul rapid al
   lui Kronos încarcă starea, dar nu o scrie niciodată.
2. Simbolurile textului de antrenare se țin minte în director_cache: un text mare se împarte o singură dată.
3. Textul stă în RAM (pe placă urcă doar loturile), iar pregătirea nu intră în bugetul de timp: bugetul = antrenarea.
Pe placa video stă un singur model mare odată: cel care începe antrenarea o eliberează pe a celorlalte (ex. modelul
din testul rapid al aceluiași experiment, care nu mai e folosit).
"""

from __future__ import annotations

import hashlib
import weakref
from pathlib import Path
from typing import Any

import torch

from module.model_gpt import ModelGPT

_PE_PLACA: list[weakref.ref] = []


def ia_placa(model: Any) -> None:
    """Un singur model mare pe placa video: cel nou o eliberează pe a celorlalte."""
    for ref in _PE_PLACA:
        altul = ref()
        if altul is not None and altul is not model:
            altul.elibereaza_placa()
    _PE_PLACA[:] = [weakref.ref(model)]
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def amprenta(*bucati: bytes) -> str:
    h = hashlib.sha1()
    for bucata in bucati:
        h.update(bucata)
    return h.hexdigest()[:16]


def simboluri_din_cache(tok: Any, text: str, director: str, cale_tokenizer: str) -> Any:
    """Simbolurile textului: din director_cache dacă textul a mai fost împărțit, altfel le împarte și le ține minte."""
    if not director:
        return tok.codifica(text)
    fisier = Path(director) / f"simboluri_{amprenta(text.encode('utf-8'), Path(cale_tokenizer).read_bytes())}.pt"
    if fisier.exists():
        return torch.load(fisier, weights_only=True)
    simboluri = torch.tensor(tok.codifica(text), dtype=torch.int16 if tok.marime < 2**15 else torch.int32)
    salveaza_atomic(simboluri, fisier)
    return simboluri


def salveaza_atomic(obiect: Any, cale: str | Path) -> None:
    """Scrie întâi un fișier temporar, apoi îl pune în locul celui vechi: o întrerupere nu strică starea salvată."""
    fisier = Path(cale)
    fisier.parent.mkdir(parents=True, exist_ok=True)
    temporar = fisier.with_name(fisier.name + ".part")
    torch.save(obiect, temporar)
    temporar.replace(fisier)


class ModelGPTContinuu(ModelGPT):
    MANIFEST = {
        "nume": "model_gpt_continuu",
        "port": "model",
        "versiune": "0.1.0",
        "versiune_contract": 1,
        "resurse": {"gpu": True, "memorie_gpu_mb": 5500},
        "permisiuni": ["citire_fisier", "scriere_fisier"],
    }

    _pregatirea_intra_in_buget = False
    _textul_ramane_in_ram = True

    def __init__(self, cale_stare: str = "", director_cache: str = "", **setari: Any) -> None:
        super().__init__(**setari)
        self.cale_stare = cale_stare
        self.director_cache = director_cache
        self.pasi_total = 0  # câți pași a făcut modelul în toate experimentele de până acum
        self.continuat = False

    def elibereaza_placa(self) -> None:
        self.retea = None
        self.optimizator = None

    def _simboluri(self, text: str) -> Any:
        return simboluri_din_cache(self.tok, text, self.director_cache, self.cale_tokenizer)

    def _stare_salvata(self) -> dict[str, Any] | None:
        if not self.cale_stare or not Path(self.cale_stare).exists():
            return None
        stare = torch.load(self.cale_stare, map_location="cpu", weights_only=True)
        if stare["setari"] != self.setari:
            raise ValueError(f"Starea din „{self.cale_stare}” e a altui model ({stare['setari']}); folosește alt cale_stare.")
        return stare

    def _pregateste_reteaua(self) -> None:
        ia_placa(self)
        stare = self._stare_salvata()
        super()._pregateste_reteaua()
        assert self.retea is not None and self.optimizator is not None
        self.continuat = stare is not None
        if stare is not None:
            self.retea.load_state_dict(stare["retea"])
            self.optimizator.load_state_dict(stare["optimizator"])
            self.pasi_total = stare["pasi_total"]

    def _samanta_loturi(self) -> int:
        # Primul experiment alege bucățile ca GPT-ul simplu; la fiecare continuare, alte bucăți de text.
        return self.samanta if self.pasi_total == 0 else self.samanta * 1_000_003 + self.pasi_total

    def antreneaza(self, date: Any, buget_secunde: float) -> dict[str, Any]:
        statistici = super().antreneaza(date, buget_secunde)
        self.pasi_total += statistici["pasi"]
        statistici.update(pasi_total=self.pasi_total, continuat=self.continuat)
        if self.dispozitiv.type == "cuda":
            statistici["memorie_rezervata_mb"] = round(torch.cuda.max_memory_reserved() / 2**20)
        return statistici

    def dupa_examen(self, rezultat: dict[str, Any]) -> dict[str, Any] | None:
        """După examen (doar experimentul adevărat): starea nouă se salvează pentru experimentul următor."""
        if not self.cale_stare or self.retea is None or self.optimizator is None:
            return None
        salveaza_atomic(
            {"setari": self.setari, "retea": self.retea.state_dict(), "optimizator": self.optimizator.state_dict(),
             "pasi_total": self.pasi_total},
            self.cale_stare,
        )
        return {"continuare": {"pasi_total": self.pasi_total, "fisier": self.cale_stare}}
