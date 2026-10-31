"""GPT-ul lui Kronos-Cod (S59): ca model_muon, dar citește simbolurile gata făcute, nu text.

Datele de cod (`module/date_cod.py`) au ~1,08 miliarde de simboluri deja tokenizate (S55); ca text ar fi ~3,7 GB de
împărțit din nou la fiecare oră. Dacă datele au `simboluri_antrenare()`, modelul le ia direct: o singură copie în RAM,
ca int32 (~4,3 GB pe setul întreg), iar pe placă urcă doar lotul. Fără tokenizare, fără director_cache.

Restul e exact ModelGPTConversatieMuon (AdamW sau Muon, adunarea loturilor, rata care scade, continuarea din cale_stare,
examenul pe text prin biti_pentru, tokenizerul salvat în model). Cu date pe text (fără `simboluri_antrenare`), modelul
se poartă exact ca ModelGPTConversatieMuon. `module/model_gpt.py` și `module/model_muon.py` nu se schimbă: #477 și
linia română rămân identice.

Cu simbolurile: fără memorie ierarhică, fără hrană și fără conversație (ar cere text); modelul refuză clar.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import torch

from module.model_muon import ModelGPTConversatieMuon


class _FaraText:
    """Datele, văzute de bucla din model_gpt: textul de antrenare e gol (simbolurile vin din `_simboluri`)."""

    def __init__(self, date: Any) -> None:
        self.date = date

    def text_antrenare(self) -> str:
        return ""

    def text_validare(self) -> str:
        return self.date.text_validare()


class ModelGPTCod(ModelGPTConversatieMuon):
    MANIFEST = {
        "nume": "model_gpt_cod",
        "port": "model",
        "versiune": "0.2.0",
        "versiune_contract": 1,
        "resurse": {"gpu": True, "memorie_gpu_mb": 6500},
        "permisiuni": ["citire_fisier", "scriere_fisier"],
    }

    def __init__(self, abatere_incorporari: float | None = None, **setari: Any) -> None:
        super().__init__(**setari)
        if abatere_incorporari is not None and abatere_incorporari <= 0:
            raise ValueError("abatere_incorporari pozitivă (sau lipsă: inițializarea implicită)")
        self.abatere_incorporari = abatere_incorporari
        self._date_simboluri: Any = None

    def _construieste(self) -> None:
        """S61: cu `abatere_incorporari`, încorporările (simbolurile, deci și capul legat de ele, și pozițiile) pornesc din
        normala cu media 0 și abaterea dată, ca la GPT-2. Fără ea: exact rețeaua de până acum, bit cu bit. La continuare,
        greutățile din starea salvată le înlocuiesc oricum."""
        super()._construieste()
        if self.abatere_incorporari is None:
            return
        assert self.retea is not None
        with torch.no_grad():
            self.retea.emb_token.weight.normal_(0.0, self.abatere_incorporari)
            self.retea.emb_pozitie.weight.normal_(0.0, self.abatere_incorporari)

    @staticmethod
    def citeste_simboluri(date: Any) -> bool:
        """Datele dau simboluri gata făcute (ca date_cod)?"""
        return callable(getattr(date, "simboluri_antrenare", None))

    def _simboluri(self, text: str) -> Any:
        if self._date_simboluri is None:
            return super()._simboluri(text)
        s = np.asarray(self._date_simboluri.simboluri_antrenare())
        if s.size and int(s.max()) >= self._marime_vocabular():
            raise ValueError(f"datele au simbolul {int(s.max())}, dar tokenizerul are doar {self._marime_vocabular()}")
        return torch.from_numpy(s.astype(np.int32))

    def antreneaza(self, date: Any, buget_secunde: float) -> dict[str, Any]:
        if not self.citeste_simboluri(date):
            return super().antreneaza(date, buget_secunde)
        if self.tokenizer != "bpe":
            raise ValueError("simbolurile gata făcute cer tokenizer = \"bpe\" (cel cu care au fost făcute)")
        if self.foloseste_memorie or self.hrana or self.conversatie:
            raise ValueError("cu simboluri gata făcute nu merg memoria, hrana sau conversația (ar cere text)")
        self._date_simboluri = date
        try:
            statistici = super().antreneaza(_FaraText(date), buget_secunde)
        finally:
            self._date_simboluri = None
        statistici["simboluri_direct"] = True
        return statistici
