"""Modelul GPT mic, scris de la 0 (în stilul nanoGPT), pe caractere.

Folosește placa video dacă există (RTX 3060), altfel procesorul.
Cere PyTorch: vezi README, pasul „Instalează PyTorch”.

Setări pe care Cercetătorul le poate schimba:
- n_straturi, n_capete, n_emb: cât de mare e rețeaua
- context: câte caractere vede înapoi
- lot: câte bucăți de text procesează deodată
- rata_invatare: cât de mari sunt pașii de învățare
"""

from __future__ import annotations

import math
import time
from pathlib import Path
from typing import Any

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
except ImportError as e:  # registrul transformă asta într-un mesaj clar
    raise ImportError("Modulul model_gpt are nevoie de PyTorch. Vezi README: „Instalează PyTorch”.") from e

NECUNOSCUT = "�"


class _Bloc(nn.Module):
    def __init__(self, n_emb: int, n_capete: int, context: int, dropout: float) -> None:
        super().__init__()
        self.ln1 = nn.LayerNorm(n_emb)
        self.atentie = nn.MultiheadAttention(n_emb, n_capete, dropout=dropout, batch_first=True)
        self.ln2 = nn.LayerNorm(n_emb)
        self.mlp = nn.Sequential(
            nn.Linear(n_emb, 4 * n_emb), nn.GELU(), nn.Linear(4 * n_emb, n_emb), nn.Dropout(dropout)
        )
        masca = torch.triu(torch.ones(context, context, dtype=torch.bool), diagonal=1)
        self.register_buffer("masca", masca, persistent=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        t = x.size(1)
        h = self.ln1(x)
        a, _ = self.atentie(h, h, h, attn_mask=self.masca[:t, :t], need_weights=False)
        x = x + a
        return x + self.mlp(self.ln2(x))


class _GPT(nn.Module):
    def __init__(self, vocab: int, n_straturi: int, n_capete: int, n_emb: int, context: int, dropout: float) -> None:
        super().__init__()
        self.context = context
        self.emb_token = nn.Embedding(vocab, n_emb)
        self.emb_pozitie = nn.Embedding(context, n_emb)
        self.straturi = nn.ModuleList(_Bloc(n_emb, n_capete, context, dropout) for _ in range(n_straturi))
        self.ln = nn.LayerNorm(n_emb)
        self.cap = nn.Linear(n_emb, vocab, bias=False)
        self.cap.weight = self.emb_token.weight  # aceleași greutăți la intrare și ieșire

    def forward(self, idx: torch.Tensor) -> torch.Tensor:
        t = idx.size(1)
        poz = torch.arange(t, device=idx.device)
        x = self.emb_token(idx) + self.emb_pozitie(poz)
        for strat in self.straturi:
            x = strat(x)
        return self.cap(self.ln(x))


class ModelGPT:
    MANIFEST = {
        "nume": "model_gpt",
        "port": "model",
        "versiune": "0.1.0",
        "versiune_contract": 1,
        "resurse": {"gpu": True, "memorie_gpu_mb": 4000},
        "permisiuni": [],
    }

    def __init__(
        self,
        n_straturi: int = 4,
        n_capete: int = 4,
        n_emb: int = 128,
        context: int = 128,
        lot: int = 32,
        rata_invatare: float = 1e-3,
        dropout: float = 0.0,
        dispozitiv: str = "auto",
        samanta: int = 1337,
    ) -> None:
        if n_emb % n_capete != 0:
            raise ValueError("n_emb trebuie să se împartă exact la n_capete")
        if min(n_straturi, n_capete, n_emb, context, lot) < 1 or rata_invatare <= 0:
            raise ValueError("toate dimensiunile și rata_invatare trebuie să fie pozitive")
        self.setari = dict(
            n_straturi=n_straturi, n_capete=n_capete, n_emb=n_emb, context=context, dropout=dropout
        )
        self.lot = lot
        self.rata_invatare = rata_invatare
        self.samanta = samanta
        if dispozitiv == "auto":
            dispozitiv = "cuda" if torch.cuda.is_available() else "cpu"
        self.dispozitiv = torch.device(dispozitiv)
        self.vocabular: list[str] = [NECUNOSCUT]
        self.retea: _GPT | None = None

    # --- utilitare --------------------------------------------------------

    def _codifica(self, text: str) -> torch.Tensor:
        idx = {c: i for i, c in enumerate(self.vocabular)}
        nec = idx[NECUNOSCUT]
        return torch.tensor([idx.get(c, nec) for c in text], dtype=torch.long)

    def _construieste(self) -> None:
        torch.manual_seed(self.samanta)
        self.retea = _GPT(len(self.vocabular), **self.setari).to(self.dispozitiv)

    def _autocast(self):
        if self.dispozitiv.type == "cuda" and torch.cuda.is_bf16_supported():
            return torch.autocast("cuda", dtype=torch.bfloat16)
        return torch.autocast(self.dispozitiv.type, enabled=False)

    # --- contractul ---------------------------------------------------------

    def antreneaza(self, date: Any, buget_secunde: float) -> dict[str, Any]:
        text = date.text_antrenare()
        self.vocabular = sorted(set(text)) + [NECUNOSCUT]
        self._construieste()
        assert self.retea is not None
        date_t = self._codifica(text).to(self.dispozitiv)
        ctx = self.setari["context"]
        if len(date_t) <= ctx + 1:
            raise ValueError("textul de antrenare e mai scurt decât contextul")
        optimizator = torch.optim.AdamW(self.retea.parameters(), lr=self.rata_invatare, weight_decay=0.1)
        generator = torch.Generator(device="cpu").manual_seed(self.samanta)

        self.retea.train()
        start = time.perf_counter()
        pasi = 0
        pierdere = float("nan")
        while time.perf_counter() - start < buget_secunde:
            pozitii = torch.randint(len(date_t) - ctx - 1, (self.lot,), generator=generator)
            x = torch.stack([date_t[p : p + ctx] for p in pozitii])
            y = torch.stack([date_t[p + 1 : p + ctx + 1] for p in pozitii])
            with self._autocast():
                logits = self.retea(x)
                loss = F.cross_entropy(logits.float().view(-1, logits.size(-1)), y.view(-1))
            optimizator.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.retea.parameters(), 1.0)
            optimizator.step()
            pasi += 1
            pierdere = loss.item()
            if not math.isfinite(pierdere):
                raise FloatingPointError("pierderea a devenit infinită (rata de învățare prea mare?)")
        return {
            "pasi": pasi,
            "pierdere_finala": pierdere,
            "parametri": sum(p.numel() for p in self.retea.parameters()),
            "dispozitiv": str(self.dispozitiv),
        }

    @torch.no_grad()
    def biti_pentru(self, text: str) -> float:
        if self.retea is None:
            raise RuntimeError("modelul nu a fost antrenat sau încărcat")
        if not text:
            return 0.0
        self.retea.eval()
        idx = self._codifica(text).to(self.dispozitiv)
        ctx = self.setari["context"]
        nats = 0.0
        # primul caracter nu are context: îl socotim cu probabilitate uniformă
        biti_primul = math.log2(len(self.vocabular))
        bucati = [idx[i : i + ctx + 1] for i in range(0, len(idx) - 1, ctx)]
        intregi = [b for b in bucati if len(b) == ctx + 1]
        rest = [b for b in bucati if len(b) != ctx + 1]
        grupuri = [torch.stack(intregi[i : i + 64]) for i in range(0, len(intregi), 64)]
        grupuri += [b.unsqueeze(0) for b in rest]
        for grup in grupuri:
            x, y = grup[:, :-1], grup[:, 1:]
            with self._autocast():
                logits = self.retea(x)
            nats += F.cross_entropy(logits.float().reshape(-1, logits.size(-1)), y.reshape(-1), reduction="sum").item()
        return biti_primul + nats / math.log(2)

    @torch.no_grad()
    def genereaza(self, inceput: str, lungime: int) -> str:
        if self.retea is None:
            raise RuntimeError("modelul nu a fost antrenat sau încărcat")
        self.retea.eval()
        generator = torch.Generator(device="cpu").manual_seed(self.samanta)
        idx = self._codifica(inceput or " ").unsqueeze(0).to(self.dispozitiv)
        nec = self.vocabular.index(NECUNOSCUT)
        rezultat = []
        for _ in range(lungime):
            logits = self.retea(idx[:, -self.setari["context"] :])[:, -1, :].float()
            logits[:, nec] = -float("inf")  # nu generăm caracterul „necunoscut”
            prob = F.softmax(logits, dim=-1).cpu()
            urm = torch.multinomial(prob, 1, generator=generator)
            rezultat.append(self.vocabular[urm.item()])
            idx = torch.cat([idx, urm.to(self.dispozitiv)], dim=1)
        return "".join(rezultat)

    def salveaza(self, cale: str) -> str:
        if self.retea is None:
            raise RuntimeError("nu am ce salva: modelul nu e antrenat")
        fisier = Path(cale).with_suffix(".pt")
        fisier.parent.mkdir(parents=True, exist_ok=True)
        torch.save({"setari": self.setari, "vocabular": self.vocabular, "stare": self.retea.state_dict()}, fisier)
        return str(fisier)

    def incarca(self, cale: str) -> None:
        fisier = Path(cale)
        if not fisier.exists():
            fisier = fisier.with_suffix(".pt")
        salvat = torch.load(fisier, map_location=self.dispozitiv, weights_only=True)
        self.setari = salvat["setari"]
        self.vocabular = salvat["vocabular"]
        self._construieste()
        assert self.retea is not None
        self.retea.load_state_dict(salvat["stare"])
