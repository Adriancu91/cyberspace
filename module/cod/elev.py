"""Kronos la școala de cod: rețeaua GPT a lui #252 (module/model_gpt.py). Niciun alt model în buclă.

- **Încărcarea:** modelul salvat al lui #252 (greutăți și tokenizer), sau starea unei linii, cu optimizatorul ei.
- **Generarea:** n încercări pentru același text din față, într-un singur lot, cu temperatura dată (0 = fără
  întâmplare: mereu simbolul cel mai probabil), până la „RESULT:” sau la max_simboluri.
- **Antrenarea scurtă:**
  - pași exacți și o rată mică, fixă, fără repornire (lecția 6c);
  - optimizatorul se păstrează de la o rundă la alta;
  - loturi de ferestre de `context` simboluri din textul dat (abecedarul, plus biblioteca la liniile B și D);
  - din v0.2, poveștile rămân în lecții: o parte fixă din fiecare lot (ex. 70%) vine din textul de antrenare al
    poveștilor, restul din textul școlii.

  Rețeaua din model_gpt.py nu se reconstruiește: antreneaza() de acolo ar porni-o de la zero.
- **Ce știa:** biți pe octet pe un text de povești, ca să se vadă dacă școala strică povestirile.
- **Pierderea pe un text** (v0.2): pregătirea se oprește când abecedarul e învățat cât trebuie (~0,5), nu pe de rost
  (0,02 în v0.1).
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

    def simboluri(self, text: str) -> list[int]:
        return self.model.tok.codifica(text)

    def tokenizer_ca(self, cale: str | Path) -> bool:
        """Are elevul exact tokenizer-ul din fișierul dat? (Simbolurile poveștilor din memoria lui Kronos sunt făcute cu el.)"""
        from module.tokenizer_bpe import TokenizerBPE

        return TokenizerBPE.incarca(cale).ca_dictionar() == self.model.tok.ca_dictionar()

    @torch.no_grad()
    def pierdere_pe(self, text: str) -> float:
        """Pierderea medie (nats pe simbol, ca pierderea de la antrenare) pe ferestre de `context` care acoperă textul."""
        retea, ctx = self.model.retea, self.context
        date = torch.tensor(self.model.tok.codifica(text), dtype=torch.long)
        retea.eval()
        intregi = [s for s in range(0, len(date) - 1, ctx) if s + ctx + 1 <= len(date)]
        grupuri = [torch.stack([date[s:s + ctx + 1] for s in intregi[i:i + 32]]) for i in range(0, len(intregi), 32)]
        rest = intregi[-1] + ctx if intregi else 0
        if len(date) - rest >= 2:
            grupuri.append(date[rest:].unsqueeze(0))
        total, n = 0.0, 0
        for g in grupuri:
            g = g.to(self.dispozitiv)
            with self.model._autocast():
                logits = retea(g[:, :-1])
            total += F.cross_entropy(logits.float().reshape(-1, logits.size(-1)), g[:, 1:].reshape(-1),
                                     reduction="sum").item()
            n += g[:, 1:].numel()
        return total / max(1, n)

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
        if self.dispozitiv.type == "cuda":  # texte de lungimi diferite: fără asta, memoria rezervată urcă încet
            torch.cuda.empty_cache()
        return [tok.decodeaza(s) for s in noi]

    def antreneaza(self, text: str, pasi: int, rata: float, lot: int, samanta: int,
                   povesti: torch.Tensor | None = None, fractie_povesti: float = 0.0) -> dict[str, Any]:
        """`pasi` pași pe ferestre din `text`, cu rata fixă `rata` (optimizatorul rămâne de la o rundă la alta).

        Cu `povesti` (simbolurile textului de antrenare al poveștilor, pe procesor) și `fractie_povesti` > 0, din fiecare
        lot vin din povești fractie × lot ferestre. Când produsul nu e întreg, numărul alternează (ex. 0,7 × 24 = 16,8:
        16 și 17), ca media să fie exact fracția."""
        retea, ctx = self.model.retea, self.context
        date = torch.tensor(self.model.tok.codifica(text), dtype=torch.long)
        if len(date) <= ctx + 1:
            raise ValueError(f"textul de antrenare are {len(date)} simboluri, sub contextul de {ctx}")
        cu_povesti = povesti is not None and fractie_povesti > 0
        if cu_povesti and len(povesti) <= ctx + 1:
            raise ValueError(f"textul de povești are {len(povesti)} simboluri, sub contextul de {ctx}")
        if self.optimizator is None:
            self.optimizator = self._optimizator(rata)
        for grup in self.optimizator.param_groups:
            grup["lr"] = rata
        generator = torch.Generator(device="cpu").manual_seed(samanta)
        pe_placa = self.dispozitiv.type == "cuda"
        if pe_placa:
            torch.cuda.reset_peak_memory_stats()
        retea.train()
        start, pierdere, ferestre_povesti = time.perf_counter(), math.nan, 0
        for pas in range(pasi):
            k = (math.floor(fractie_povesti * lot * (pas + 1) + 1e-9) - math.floor(fractie_povesti * lot * pas + 1e-9)
                 if cu_povesti else 0)
            surse = [(date, p) for p in torch.randint(len(date) - ctx - 1, (lot - k,), generator=generator)]
            if k:
                surse += [(povesti, p) for p in torch.randint(len(povesti) - ctx - 1, (k,), generator=generator)]
                ferestre_povesti += k
            x = torch.stack([s[p:p + ctx].long() for s, p in surse]).to(self.dispozitiv)
            y = torch.stack([s[p + 1:p + ctx + 1].long() for s, p in surse]).to(self.dispozitiv)
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
                "simboluri_text": len(date), "ferestre_povesti": ferestre_povesti, "ferestre": pasi * lot,
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
