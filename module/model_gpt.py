"""Modelul GPT mic, scris de la 0 (în stilul nanoGPT), pe caractere.

Folosește placa video dacă există (RTX 3060), altfel procesorul.
Cere PyTorch: vezi README, pasul „Instalează PyTorch”.

Setări pe care Cercetătorul le poate schimba:
- n_straturi, n_capete, n_emb: cât de mare e rețeaua
- context: câte caractere vede înapoi
- lot: câte bucăți de text procesează deodată
- rata_invatare: cât de mari sunt pașii de învățare
- memorie: dacă folosește memoria ierarhică (portul „memorie”)
- adancime_memorie: câte niveluri din codul cuvântului folosește
- n_emb_memorie: cât de bogat descrie categoria de pe fiecare nivel

Cum folosește memoria: la fiecare literă primește, în plus, codul ultimului cuvânt
terminat (de ex. „horse” → substantiv → noun.animal → ... → equine → horse). Fiecare
nivel al codului are o descriere învățată; descrierile se alătură și trec printr-o
proiecție care pornește de la zero, deci la început modelul cu memorie e identic cu
cel fără. Fără memorie, calculele sunt exact cele de dinainte de Etapa M1.
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
# Numerele rezervate pentru categoriile din memorie: 0 = nivel gol, 1 = categorie nevăzută la antrenare.
CATEGORIE_GOALA, CATEGORIE_NOUA = 0, 1


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
    def __init__(
        self,
        vocab: int,
        n_straturi: int,
        n_capete: int,
        n_emb: int,
        context: int,
        dropout: float,
        categorii_memorie: list[int] | None = None,
        n_emb_memorie: int = 32,
    ) -> None:
        super().__init__()
        self.context = context
        self.emb_token = nn.Embedding(vocab, n_emb)
        self.emb_pozitie = nn.Embedding(context, n_emb)
        self.straturi = nn.ModuleList(_Bloc(n_emb, n_capete, context, dropout) for _ in range(n_straturi))
        self.ln = nn.LayerNorm(n_emb)
        self.cap = nn.Linear(n_emb, vocab, bias=False)
        self.cap.weight = self.emb_token.weight  # aceleași greutăți la intrare și ieșire
        # Memoria se construiește DUPĂ restul rețelei: cu aceeași sămânță, restul greutăților
        # ies identice cu ale modelului fără memorie. Proiecția pornește de la zero.
        self.memorie: nn.ModuleList | None = None
        if categorii_memorie:
            self.memorie = nn.ModuleList(nn.Embedding(n, n_emb_memorie, padding_idx=CATEGORIE_GOALA) for n in categorii_memorie)
            self.proiectie_memorie = nn.Linear(n_emb_memorie * len(categorii_memorie), n_emb, bias=False)
            nn.init.zeros_(self.proiectie_memorie.weight)

    def forward(self, idx: torch.Tensor, memorie: torch.Tensor | None = None) -> torch.Tensor:
        t = idx.size(1)
        poz = torch.arange(t, device=idx.device)
        x = self.emb_token(idx) + self.emb_pozitie(poz)
        if self.memorie is not None and memorie is not None:
            descrieri = torch.cat([emb(memorie[..., k]) for k, emb in enumerate(self.memorie)], dim=-1)
            x = x + self.proiectie_memorie(descrieri)
        for strat in self.straturi:
            x = strat(x)
        return self.cap(self.ln(x))


class ModelGPT:
    MANIFEST = {
        "nume": "model_gpt",
        "port": "model",
        "versiune": "0.2.0",
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
        memorie: bool = False,
        adancime_memorie: int = 8,
        n_emb_memorie: int = 32,
        dispozitiv: str = "auto",
        samanta: int = 1337,
    ) -> None:
        if n_emb % n_capete != 0:
            raise ValueError("n_emb trebuie să se împartă exact la n_capete")
        if min(n_straturi, n_capete, n_emb, context, lot, adancime_memorie, n_emb_memorie) < 1 or rata_invatare <= 0:
            raise ValueError("toate dimensiunile și rata_invatare trebuie să fie pozitive")
        self.setari = dict(
            n_straturi=n_straturi, n_capete=n_capete, n_emb=n_emb, context=context, dropout=dropout
        )
        self.lot = lot
        self.rata_invatare = rata_invatare
        self.samanta = samanta
        self.foloseste_memorie = bool(memorie)
        self.adancime_memorie = adancime_memorie
        self.n_emb_memorie = n_emb_memorie
        self.sursa_memorie: Any = None
        # harta[k][codul până la nivelul k] = numărul categoriei pe nivelul k (văzută la antrenare)
        self.harta: list[dict[tuple[int, ...], int]] = []
        if dispozitiv == "auto":
            dispozitiv = "cuda" if torch.cuda.is_available() else "cpu"
        self.dispozitiv = torch.device(dispozitiv)
        self.vocabular: list[str] = [NECUNOSCUT]
        self.retea: _GPT | None = None

    # --- memoria ------------------------------------------------------------

    def conecteaza_memorie(self, memorie: Any) -> None:
        """Primește portul „memorie” de la Kronos. Îl folosește doar dacă setarea memorie e pornită."""
        self.sursa_memorie = memorie

    def _memoria(self) -> Any:
        if self.sursa_memorie is None:
            raise RuntimeError("modelul are memorie=true, dar portul „memorie” nu e conectat (conecteaza_memorie)")
        return self.sursa_memorie

    def _construieste_harta(self, coduri: list[tuple[int, ...]]) -> None:
        """Numerotează categoriile văzute la antrenare, pe fiecare nivel.

        Categoria de pe nivelul k = codul până la nivelul k (drumul din bibliotecă), deci „horse” și
        „cat” au aceleași categorii pe nivelurile de sus și diferă abia jos.
        """
        self.harta = [{} for _ in range(self.adancime_memorie)]
        for cod in sorted(set(coduri)):
            for k in range(min(self.adancime_memorie, len(cod))):
                if cod[k] == 0:
                    break
                self.harta[k].setdefault(cod[: k + 1], len(self.harta[k]) + 2)

    def _categorii(self, coduri: list[tuple[int, ...]]) -> torch.Tensor:
        """Pentru fiecare literă: numărul categoriei pe fiecare nivel (lungimea textului × adâncime)."""
        if not coduri:
            return torch.zeros((0, self.adancime_memorie), dtype=torch.long)
        unice = list(dict.fromkeys(coduri))
        tabel = torch.tensor(
            [
                [
                    CATEGORIE_GOALA if k >= len(cod) or cod[k] == 0 else self.harta[k].get(cod[: k + 1], CATEGORIE_NOUA)
                    for k in range(self.adancime_memorie)
                ]
                for cod in unice
            ],
            dtype=torch.long,
        )
        rand = {cod: i for i, cod in enumerate(unice)}
        return tabel[torch.tensor([rand[c] for c in coduri], dtype=torch.long)]

    # --- utilitare --------------------------------------------------------

    def _codifica(self, text: str) -> torch.Tensor:
        idx = {c: i for i, c in enumerate(self.vocabular)}
        nec = idx[NECUNOSCUT]
        return torch.tensor([idx.get(c, nec) for c in text], dtype=torch.long)

    def _construieste(self) -> None:
        torch.manual_seed(self.samanta)
        categorii = [len(h) + 2 for h in self.harta] if self.foloseste_memorie else None
        self.retea = _GPT(
            len(self.vocabular), **self.setari, categorii_memorie=categorii, n_emb_memorie=self.n_emb_memorie
        ).to(self.dispozitiv)

    def _autocast(self):
        if self.dispozitiv.type == "cuda" and torch.cuda.is_bf16_supported():
            return torch.autocast("cuda", dtype=torch.bfloat16)
        return torch.autocast(self.dispozitiv.type, enabled=False)

    # --- contractul ---------------------------------------------------------

    def antreneaza(self, date: Any, buget_secunde: float) -> dict[str, Any]:
        inceput_pregatire = time.perf_counter()
        text = date.text_antrenare()
        self.vocabular = sorted(set(text)) + [NECUNOSCUT]
        memorie_t = None
        pregatire = 0.0
        if self.foloseste_memorie:
            # Pregătirea memoriei intră în bugetul de timp: comparația cu/fără memorie e cinstită.
            coduri = self._memoria().caracteristici(text)
            self._construieste_harta(coduri)
            memorie_t = self._categorii(coduri).to(self.dispozitiv)
            pregatire = time.perf_counter() - inceput_pregatire
        self._construieste()
        assert self.retea is not None
        date_t = self._codifica(text).to(self.dispozitiv)
        ctx = self.setari["context"]
        if len(date_t) <= ctx + 1:
            raise ValueError("textul de antrenare e mai scurt decât contextul")
        optimizator = torch.optim.AdamW(self.retea.parameters(), lr=self.rata_invatare, weight_decay=0.1)
        generator = torch.Generator(device="cpu").manual_seed(self.samanta)

        self.retea.train()
        start = time.perf_counter() - pregatire
        pasi = 0
        pierdere = float("nan")
        while time.perf_counter() - start < buget_secunde:
            pozitii = torch.randint(len(date_t) - ctx - 1, (self.lot,), generator=generator)
            x = torch.stack([date_t[p : p + ctx] for p in pozitii])
            y = torch.stack([date_t[p + 1 : p + ctx + 1] for p in pozitii])
            m = torch.stack([memorie_t[p : p + ctx] for p in pozitii]) if memorie_t is not None else None
            with self._autocast():
                logits = self.retea(x, m)
                loss = F.cross_entropy(logits.float().view(-1, logits.size(-1)), y.view(-1))
            optimizator.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.retea.parameters(), 1.0)
            optimizator.step()
            pasi += 1
            pierdere = loss.item()
            if not math.isfinite(pierdere):
                raise FloatingPointError("pierderea a devenit infinită (rata de învățare prea mare?)")
        statistici: dict[str, Any] = {
            "pasi": pasi,
            "pierdere_finala": pierdere,
            "parametri": sum(p.numel() for p in self.retea.parameters()),
            "dispozitiv": str(self.dispozitiv),
        }
        if self.retea.memorie is not None:
            statistici["parametri_memorie"] = sum(p.numel() for p in self.retea.memorie.parameters()) + (
                self.retea.proiectie_memorie.weight.numel()
            )
            statistici["categorii_memorie"] = [len(h) for h in self.harta]
            statistici["pregatire_memorie_secunde"] = round(pregatire, 2)
            statistici["acoperire_memorie"] = self._memoria().statistici().get("acoperire")
        return statistici

    @torch.no_grad()
    def biti_pentru(self, text: str) -> float:
        if self.retea is None:
            raise RuntimeError("modelul nu a fost antrenat sau încărcat")
        if not text:
            return 0.0
        self.retea.eval()
        idx = self._codifica(text).to(self.dispozitiv)
        memorie = self._categorii(self._memoria().caracteristici(text)).to(self.dispozitiv) if self.foloseste_memorie else None
        ctx = self.setari["context"]
        nats = 0.0
        # primul caracter nu are context: îl socotim cu probabilitate uniformă
        biti_primul = math.log2(len(self.vocabular))
        # bucăți de ctx+1 caractere (ultima poate fi mai scurtă), câte 64 deodată
        starturi = range(0, len(idx) - 1, ctx)
        intregi = [s for s in starturi if s + ctx + 1 <= len(idx)]
        rest = [s for s in starturi if s + ctx + 1 > len(idx)]
        grupuri = [intregi[i : i + 64] for i in range(0, len(intregi), 64)] + [[s] for s in rest]
        for grup in grupuri:
            n = min(ctx, len(idx) - 1 - grup[0])
            x = torch.stack([idx[s : s + n] for s in grup])
            y = torch.stack([idx[s + 1 : s + n + 1] for s in grup])
            m = torch.stack([memorie[s : s + n] for s in grup]) if memorie is not None else None
            with self._autocast():
                logits = self.retea(x, m)
            nats += F.cross_entropy(logits.float().reshape(-1, logits.size(-1)), y.reshape(-1), reduction="sum").item()
        return biti_primul + nats / math.log(2)

    @torch.no_grad()
    def genereaza(self, inceput: str, lungime: int) -> str:
        if self.retea is None:
            raise RuntimeError("modelul nu a fost antrenat sau încărcat")
        self.retea.eval()
        generator = torch.Generator(device="cpu").manual_seed(self.samanta)
        text = inceput or " "
        idx = self._codifica(text).unsqueeze(0).to(self.dispozitiv)
        nec = self.vocabular.index(NECUNOSCUT)
        ctx = self.setari["context"]
        rezultat = []
        for _ in range(lungime):
            m = None
            if self.foloseste_memorie:  # memoria vede tot textul scris până acum, nimic din viitor
                m = self._categorii(self._memoria().caracteristici(text))[-ctx:].unsqueeze(0).to(self.dispozitiv)
            logits = self.retea(idx[:, -ctx:], m)[:, -1, :].float()
            logits[:, nec] = -float("inf")  # nu generăm caracterul „necunoscut”
            prob = F.softmax(logits, dim=-1).cpu()
            urm = torch.multinomial(prob, 1, generator=generator)
            litera = self.vocabular[urm.item()]
            rezultat.append(litera)
            text += litera
            idx = torch.cat([idx, urm.to(self.dispozitiv)], dim=1)
        return "".join(rezultat)

    def salveaza(self, cale: str) -> str:
        if self.retea is None:
            raise RuntimeError("nu am ce salva: modelul nu e antrenat")
        fisier = Path(cale).with_suffix(".pt")
        fisier.parent.mkdir(parents=True, exist_ok=True)
        stare: dict[str, Any] = {"setari": self.setari, "vocabular": self.vocabular, "stare": self.retea.state_dict()}
        if self.foloseste_memorie:
            stare["memorie"] = {
                "adancime": self.adancime_memorie,
                "n_emb": self.n_emb_memorie,
                "harta": [[[list(cod), nr] for cod, nr in nivel.items()] for nivel in self.harta],
            }
        torch.save(stare, fisier)
        return str(fisier)

    def incarca(self, cale: str) -> None:
        fisier = Path(cale)
        if not fisier.exists():
            fisier = fisier.with_suffix(".pt")
        salvat = torch.load(fisier, map_location=self.dispozitiv, weights_only=True)
        self.setari = salvat["setari"]
        self.vocabular = salvat["vocabular"]
        memorie = salvat.get("memorie")  # modelele salvate înainte de Etapa M1 nu au memorie
        self.foloseste_memorie = memorie is not None
        self.harta = []
        if memorie is not None:
            self.adancime_memorie = memorie["adancime"]
            self.n_emb_memorie = memorie["n_emb"]
            self.harta = [{tuple(cod): nr for cod, nr in nivel} for nivel in memorie["harta"]]
        self._construieste()
        assert self.retea is not None
        self.retea.load_state_dict(salvat["stare"])
