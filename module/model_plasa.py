"""Plasa de noduri, versiunea minimă (Etapa M2, pasul 2).

Pornește de la GPT-ul pe bucăți de cuvinte și adaugă:
1. Trunchiul comun (straturile GPT-ului) și, deasupra, câteva noduri mici, câte unul pentru un grup
   de rafturi din biblioteca de sensuri:
      ființe              noun.animal, noun.person, noun.plant
      locuri și obiecte   noun.location, noun.artifact, noun.object
      acțiuni             toate verb.*
      însușiri            adj.*, adv.*
      rezervă             cuvintele negăsite, cele de legătură și rafturile nepuse în alt grup
   Fiecare simbol merge la nodul raftului ultimului cuvânt terminat (din memorie, fără viitor).
2. Nodul central adună ieșirile nodurilor, ponderate, și dă răspunsul final.
Nodurile pornesc „tăcute” (ieșire zero), deci la început modelul e identic cu GPT-ul simplu.

Cere portul „memorie” cu biblioteca de sensuri (MemorieIerarhica). Fără ea, toate simbolurile
merg la nodul de rezervă (statisticile antrenării arată cât a primit fiecare nod).
"""

from __future__ import annotations

from fnmatch import fnmatch
from typing import Any

import torch
import torch.nn as nn
import torch.nn.functional as F

from module.model_gpt import _GPT, ModelGPT

GRUPURI: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("fiinte", ("noun.animal", "noun.person", "noun.plant")),
    ("locuri_obiecte", ("noun.location", "noun.artifact", "noun.object")),
    ("actiuni", ("verb.*",)),
    ("insusiri", ("adj.*", "adv.*")),
    ("rezerva", ()),
)
NUME_NODURI = [nume for nume, _ in GRUPURI]
REZERVA = len(GRUPURI) - 1


def nod_pentru_raft(raft: str) -> int:
    """La ce nod merge un raft din bibliotecă (ex. „noun.animal” → ființe)."""
    for k, (_, tipare) in enumerate(GRUPURI):
        if any(fnmatch(raft, tipar) for tipar in tipare):
            return k
    return REZERVA


class _Nod(nn.Module):
    """Un nod mic: prelucrează starea trunchiului pentru felul lui de cuvinte. Pornește tăcut."""

    def __init__(self, n_emb: int, n_ascuns: int) -> None:
        super().__init__()
        self.ln = nn.LayerNorm(n_emb)
        self.sus = nn.Linear(n_emb, n_ascuns)
        self.jos = nn.Linear(n_ascuns, n_emb)
        nn.init.zeros_(self.jos.weight)
        nn.init.zeros_(self.jos.bias)

    def forward(self, h: torch.Tensor) -> torch.Tensor:
        return self.jos(F.gelu(self.sus(self.ln(h))))


class _GPTCuNoduri(_GPT):
    def __init__(self, *args: Any, n_noduri: int = len(GRUPURI), n_ascuns_nod: int = 64, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        n_emb = self.emb_token.embedding_dim
        # Nodurile și centrul se creează DUPĂ trunchi: cu aceeași sămânță, trunchiul pornește ca la GPT-ul simplu.
        self.noduri = nn.ModuleList(_Nod(n_emb, n_ascuns_nod) for _ in range(n_noduri))
        self.pondere_centru = nn.Parameter(torch.ones(n_noduri))  # nodul central: cât contează fiecare nod
        self.register_buffer("identitate", torch.eye(n_noduri), persistent=False)

    def amestec(self) -> torch.Tensor:
        """Cât ia fiecare nod (rând) de la fiecare nod (coloană). Fără legături: doar de la el însuși."""
        return self.identitate

    def forward(self, idx: torch.Tensor, extra: torch.Tensor | None = None) -> torch.Tensor:
        if extra is None:
            raise ValueError("modelul cu noduri trebuie să știe, pentru fiecare simbol, la ce nod merge")
        memorie = extra[..., :-1] if self.memorie is not None else None
        noduri = extra[..., -1]
        h = self.trunchi(idx, memorie)
        iesiri = torch.stack([nod(h) for nod in self.noduri], dim=-2)  # lot × poziții × noduri × n_emb
        ponderi = self.amestec()[noduri] * self.pondere_centru  # lot × poziții × noduri
        return self.cap(self.ln(h + (ponderi.unsqueeze(-1) * iesiri).sum(dim=-2)))


class ModelPlasa(ModelGPT):
    MANIFEST = {
        "nume": "model_plasa",
        "port": "model",
        "versiune": "0.1.0",
        "versiune_contract": 1,
        "resurse": {"gpu": True, "memorie_gpu_mb": 4000},
        "permisiuni": [],
    }

    def __init__(self, n_ascuns_nod: int = 64, tokenizer: str = "bpe", **setari: Any) -> None:
        super().__init__(tokenizer=tokenizer, **setari)
        if n_ascuns_nod < 1:
            raise ValueError("n_ascuns_nod trebuie să fie pozitiv")
        self.n_ascuns_nod = n_ascuns_nod
        self._nod_pentru_cod: dict[tuple[int, ...], int] = {}
        self.simboluri_pe_nod = [0] * len(GRUPURI)

    # --- drumul fiecărui simbol ---------------------------------------------------------

    def conecteaza_memorie(self, memorie: Any) -> None:
        super().conecteaza_memorie(memorie)
        self._nod_pentru_cod = {}

    def _nod(self, cod: tuple[int, ...]) -> int:
        """Nodul pentru codul ultimului cuvânt terminat: după raftul lui; negăsit sau gol → rezervă."""
        nod = self._nod_pentru_cod.get(cod)
        if nod is None:
            nod = REZERVA
            rafturi = getattr(self.sursa_memorie, "rafturi", None)
            if rafturi and len(cod) > 1 and 1 <= cod[0] <= 4 and 1 <= cod[1] <= len(rafturi):
                nod = nod_pentru_raft(rafturi[cod[1] - 1])
            self._nod_pentru_cod[cod] = nod
        return nod

    def _are_pozitii(self) -> bool:
        return True  # fiecare simbol trebuie să știe la ce nod merge

    def _pozitii(self, text: str, simboluri: list[int] | None, la_antrenare: bool = False) -> torch.Tensor:
        """Pentru fiecare simbol: [categoriile din memorie (dacă memorie=true)..., nodul la care merge]."""
        coduri = None
        if self.foloseste_memorie or self.sursa_memorie is not None:
            coduri = self._coduri_memorie(text, simboluri)
            noduri = torch.tensor([self._nod(c) for c in coduri], dtype=torch.long).unsqueeze(-1)
        else:  # fără memorie, totul merge la nodul de rezervă
            numar = len(simboluri) if simboluri is not None else len(self._codifica(text))
            noduri = torch.full((numar, 1), REZERVA, dtype=torch.long)
        if la_antrenare:
            self.simboluri_pe_nod = torch.bincount(noduri.view(-1), minlength=len(GRUPURI)).tolist()
        if not self.foloseste_memorie:
            return noduri
        assert coduri is not None
        if la_antrenare:
            self._construieste_harta(coduri)
        return torch.cat([self._categorii(coduri), noduri], dim=-1)

    # --- rețeaua --------------------------------------------------------------------

    def _construieste(self) -> None:
        torch.manual_seed(self.samanta)
        categorii = [len(h) + 1 for h in self.harta] if self.foloseste_memorie else None
        self.retea = _GPTCuNoduri(
            self._marime_vocabular(), **self.setari, categorii_memorie=categorii, n_emb_memorie=self.n_emb_memorie,
            n_noduri=len(GRUPURI), n_ascuns_nod=self.n_ascuns_nod,
        ).to(self.dispozitiv)

    def antreneaza(self, date: Any, buget_secunde: float) -> dict[str, Any]:
        statistici = super().antreneaza(date, buget_secunde)
        assert isinstance(self.retea, _GPTCuNoduri)
        total = sum(self.simboluri_pe_nod) or 1
        statistici["noduri"] = {nume: round(n / total, 4) for nume, n in zip(NUME_NODURI, self.simboluri_pe_nod)}
        statistici["pondere_centru"] = dict(
            zip(NUME_NODURI, (round(p, 4) for p in self.retea.pondere_centru.detach().cpu().tolist()))
        )
        return statistici

    def _stare_de_salvat(self) -> dict[str, Any]:
        stare = super()._stare_de_salvat()
        stare["noduri"] = {"nume": NUME_NODURI, "n_ascuns": self.n_ascuns_nod}
        return stare

    def _restaureaza(self, salvat: dict[str, Any]) -> None:
        super()._restaureaza(salvat)
        self.n_ascuns_nod = salvat["noduri"]["n_ascuns"]
