"""Kronos la școala de cod: rețeaua GPT a lui #252 (module/model_gpt.py). Niciun alt model în buclă.

- **Încărcarea:** modelul salvat al lui #252 (greutăți și tokenizer), sau starea unei linii, cu optimizatorul ei.
- **Generarea:** n încercări pentru același text din față, într-un singur lot, cu temperatura dată (0 = fără
  întâmplare: mereu simbolul cel mai probabil), până la „RESULT:” sau la max_simboluri.
- **Antrenarea scurtă:**
  - pași exacți și o rată mică, fixă, fără repornire (lecția 6c);
  - optimizatorul se păstrează de la o rundă la alta;
  - loturi de ferestre de `context` simboluri din textul dat (abecedarul, plus biblioteca la linia B).

  Rețeaua din model_gpt.py nu se reconstruiește: antreneaza() de acolo ar porni-o de la zero.
- **Ce știa:** biți pe octet pe un text de povești, ca să se vadă dacă școala strică povestirile.
"""

from __future__ import annotations

import gc
import math
import os
import time
from pathlib import Path
from typing import Any

import torch
import torch.nn.functional as F

from module.model_gpt import ModelGPT


class ElevCod:
    def __init__(self, cale: str | Path, dispozitiv: str = "") -> None:
        if torch.cuda.is_available():  # elevul liniei de dinainte iese de pe placă: memoria video se măsoară cinstit
            gc.collect()
            torch.cuda.empty_cache()
        self.model = ModelGPT(tokenizer="bpe", dispozitiv=dispozitiv or "auto")
        self.model.incarca(str(cale))
        assert self.model.retea is not None and self.model.tok is not None
        self.optimizator: torch.optim.Optimizer | None = None
        salvat = torch.load(cale, map_location="cpu", weights_only=True)
        self.pasi = int(salvat.get("pasi_scoala", 0))
        if "optimizator" in salvat:
            self.optimizator = self._optimizator(1e-5)
            self.optimizator.load_state_dict(salvat["optimizator"])

    @property
    def context(self) -> int:
        return int(self.model.setari["context"])

    @property
    def dispozitiv(self) -> torch.device:
        return self.model.dispozitiv

    def numara(self, text: str) -> int:
        return len(self.model.tok.codifica(text))

    def _optimizator(self, rata: float) -> torch.optim.Optimizer:
        return torch.optim.AdamW(self.model.retea.parameters(), lr=rata, weight_decay=0.1)

    @torch.no_grad()
    def genereaza(self, fata: str, n: int, temperatura: float, max_simboluri: int, samanta: int) -> list[str]:
        """n continuări ale aceluiași text, oprite la „RESULT:” (sau la max_simboluri)."""
        retea, tok = self.model.retea, self.model.tok
        retea.eval()
        x = torch.tensor([tok.codifica(fata)] * n, dtype=torch.long, device=self.dispozitiv)
        generator = torch.Generator(device="cpu").manual_seed(samanta)
        noi: list[list[int]] = [[] for _ in range(n)]
        gata = [False] * n
        for _ in range(max_simboluri):
            with self.model._autocast():
                logits = retea(x[:, -self.context:])[:, -1, :].float()
            if temperatura <= 0:
                urm = logits.argmax(-1).cpu()
            else:
                urm = torch.multinomial(F.softmax(logits / temperatura, dim=-1).cpu(), 1, generator=generator).squeeze(1)
            x = torch.cat([x, urm.to(self.dispozitiv).unsqueeze(1)], dim=1)
            for i in range(n):
                if not gata[i]:
                    noi[i].append(int(urm[i]))
                    gata[i] = "RESULT:" in tok.decodeaza(noi[i])
            if all(gata):
                break
        return [tok.decodeaza(s) for s in noi]

    def antreneaza(self, text: str, pasi: int, rata: float, lot: int, samanta: int) -> dict[str, Any]:
        """`pasi` pași pe ferestre din `text`, cu rata fixă `rata` (optimizatorul rămâne de la o rundă la alta)."""
        retea, ctx = self.model.retea, self.context
        date = torch.tensor(self.model.tok.codifica(text), dtype=torch.long)
        if len(date) <= ctx + 1:
            raise ValueError(f"textul de antrenare are {len(date)} simboluri, sub contextul de {ctx}")
        if self.optimizator is None:
            self.optimizator = self._optimizator(rata)
        for grup in self.optimizator.param_groups:
            grup["lr"] = rata
        generator = torch.Generator(device="cpu").manual_seed(samanta)
        pe_placa = self.dispozitiv.type == "cuda"
        if pe_placa:
            torch.cuda.reset_peak_memory_stats()
        retea.train()
        start, pierdere = time.perf_counter(), math.nan
        for _ in range(pasi):
            pozitii = torch.randint(len(date) - ctx - 1, (lot,), generator=generator)
            x = torch.stack([date[p:p + ctx] for p in pozitii]).to(self.dispozitiv)
            y = torch.stack([date[p + 1:p + ctx + 1] for p in pozitii]).to(self.dispozitiv)
            with self.model._autocast():
                logits = retea(x)
                loss = F.cross_entropy(logits.float().view(-1, logits.size(-1)), y.view(-1))
            self.optimizator.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(retea.parameters(), 1.0)
            self.optimizator.step()
            pierdere = loss.item()
        retea.eval()
        self.pasi += pasi
        return {"pasi": pasi, "pierdere_finala": round(pierdere, 4), "secunde": round(time.perf_counter() - start, 2),
                "simboluri_text": len(date),
                "memorie_video_mb": round(torch.cuda.max_memory_reserved() / 2 ** 20) if pe_placa else 0}

    def salveaza(self, cale: str | Path) -> None:
        """Modelul (ca la Kronos: setări, greutăți, tokenizer), plus optimizatorul și pașii de școală. Scris întâi
        alături, apoi mutat: o oprire bruscă nu lasă un fișier pe jumătate."""
        cale = Path(cale)
        cale.parent.mkdir(parents=True, exist_ok=True)
        stare = self.model._stare_de_salvat()
        if self.optimizator is not None:
            stare["optimizator"] = self.optimizator.state_dict()
        stare["pasi_scoala"] = self.pasi
        temporar = cale.with_name(cale.name + ".tmp")
        torch.save(stare, temporar)
        os.replace(temporar, cale)

    def biti_pe_octet(self, text: str) -> float:
        """Biți pe octet pe un text (ex. o bucată din validarea poveștilor): cât de bine îl prezice modelul."""
        return self.model.biti_pentru(text) / len(text.encode("utf-8"))


def model_de_proba(cale: str | Path, text: str, context: int = 512, marime_vocabular: int = 300) -> Path:
    """Un model GPT minuscul (1 strat, 32 de dimensiuni), cu un tokenizer BPE învățat pe `text`: pentru teste, pe
    procesor. Greutățile sunt la întâmplare."""
    from module.tokenizer_bpe import antreneaza_bpe

    cale = Path(cale)
    cale.parent.mkdir(parents=True, exist_ok=True)
    cale_tok = cale.with_name(cale.stem + "_bpe.json")
    antreneaza_bpe(text, marime_vocabular).salveaza(cale_tok)
    model = ModelGPT(n_straturi=1, n_capete=2, n_emb=32, context=context, tokenizer="bpe", cale_tokenizer=str(cale_tok),
                     dispozitiv="cpu", samanta=0)
    from module.tokenizer_bpe import TokenizerBPE

    model.tok = TokenizerBPE.incarca(cale_tok)
    model._construieste()
    return Path(model.salveaza(str(cale)))
