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
- pasi_max: dacă e mai mare ca 0, antrenarea se oprește după exact atâția pași
  (pentru comparații la număr egal de pași); bugetul de timp rămâne limita de siguranță
- tokenizer: "litere" (un simbol = o literă, ca la început) sau "bpe" (bucăți de cuvinte,
  din fișierul cale_tokenizer, antrenat cu python unelte/antreneaza_tokenizer.py).
  Examenul rămâne în biți pe octet, deci cele două se pot compara direct.

Cum folosește memoria: la fiecare literă primește, în plus, codul ultimului cuvânt
terminat (de ex. „horse” → substantiv → noun.animal → ... → equine → horse). Fiecare
nivel al codului are o descriere învățată; descrierile se alătură și trec printr-o
proiecție care pornește de la zero, deci la început modelul cu memorie e identic cu
cel fără. Fără memorie, calculele sunt exact cele de dinainte de Etapa M1.
Cu tokenizer = "bpe", fiecare simbol primește codul ultimului cuvânt terminat până la ultima
lui literă completă (nimic din viitor).
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

from module.tokenizer_bpe import TokenizerBPE

TOKENIZERE = ("litere", "bpe")

NECUNOSCUT = "�"
# Categoria 0 = „gol”: nivelul nu există sau categoria n-a fost văzută la antrenare. Descrierea ei e
# mereu zero, deci modelul folosește doar nivelurile de deasupra pe care le cunoaște, ca la un cod mai scurt.
CATEGORIE_GOALA = 0


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

    def trunchi(self, idx: torch.Tensor, memorie: torch.Tensor | None = None) -> torch.Tensor:
        """Simbolurile (și memoria) trec prin straturi; întoarce starea ascunsă, înainte de răspuns."""
        t = idx.size(1)
        poz = torch.arange(t, device=idx.device)
        x = self.emb_token(idx) + self.emb_pozitie(poz)
        if self.memorie is not None and memorie is not None:
            descrieri = torch.cat([emb(memorie[..., k]) for k, emb in enumerate(self.memorie)], dim=-1)
            x = x + self.proiectie_memorie(descrieri)
        for strat in self.straturi:
            x = strat(x)
        return x

    def forward(self, idx: torch.Tensor, memorie: torch.Tensor | None = None) -> torch.Tensor:
        return self.cap(self.ln(self.trunchi(idx, memorie)))


class ModelGPT:
    MANIFEST = {
        "nume": "model_gpt",
        "port": "model",
        "versiune": "0.4.0",
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
        pasi_max: int = 0,
        tokenizer: str = "litere",
        cale_tokenizer: str = "date/tinystories/bpe_4096.json",
        dispozitiv: str = "auto",
        samanta: int = 1337,
    ) -> None:
        if n_emb % n_capete != 0:
            raise ValueError("n_emb trebuie să se împartă exact la n_capete")
        if min(n_straturi, n_capete, n_emb, context, lot, adancime_memorie, n_emb_memorie) < 1 or rata_invatare <= 0:
            raise ValueError("toate dimensiunile și rata_invatare trebuie să fie pozitive")
        if pasi_max < 0:
            raise ValueError("pasi_max trebuie să fie 0 (fără limită de pași) sau un număr pozitiv")
        if tokenizer not in TOKENIZERE:
            raise ValueError(f"tokenizer trebuie să fie unul din: {', '.join(TOKENIZERE)}")
        self.pasi_max = pasi_max
        self.tokenizer = tokenizer
        self.cale_tokenizer = cale_tokenizer
        self.tok: TokenizerBPE | None = None  # se încarcă la antrenare (sau din modelul salvat)
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

    def _coduri_memorie(self, text: str, simboluri: list[int] | None = None) -> list[tuple[int, ...]]:
        """Pentru fiecare poziție (literă sau simbol): codul ultimului cuvânt terminat până la ea, inclusiv.

        Pe litere, e chiar ce dă memoria. Pe simboluri, fiecare simbol primește codul de la ultima lui
        literă completă, deci nimic din viitor. Cu simbolurile date, textul se ia din ele.
        """
        memoria = self._memoria()
        if self.tokenizer == "litere":
            return memoria.caracteristici(text)
        assert self.tok is not None
        text, capete = self.tok.capete_caractere(self.tok.codifica(text) if simboluri is None else simboluri)
        coduri = memoria.caracteristici(text)
        gol = (0,) * memoria.nivele
        return [coduri[cap - 1] if cap > 0 else gol for cap in capete]

    def _are_pozitii(self) -> bool:
        """Primește fiecare poziție ceva în plus pe lângă simbol? La GPT: categoriile din memorie, dacă e pornită."""
        return self.foloseste_memorie

    def _pozitii(self, text: str, simboluri: list[int] | None, la_antrenare: bool = False) -> torch.Tensor:
        """Ce primește în plus fiecare poziție (poziții × coloane). La GPT: categoriile din memorie."""
        coduri = self._coduri_memorie(text, simboluri)
        if la_antrenare:
            self._construieste_harta(coduri)
        return self._categorii(coduri)

    def _construieste_harta(self, coduri: list[tuple[int, ...]]) -> None:
        """Numerotează (de la 1) categoriile văzute la antrenare, pe fiecare nivel.

        Categoria de pe nivelul k = codul până la nivelul k (drumul din bibliotecă), deci „horse” și
        „cat” au aceleași categorii pe nivelurile de sus și diferă abia jos.
        """
        self.harta = [{} for _ in range(self.adancime_memorie)]
        for cod in sorted(set(coduri)):
            for k in range(min(self.adancime_memorie, len(cod))):
                if cod[k] == 0:
                    break
                self.harta[k].setdefault(cod[: k + 1], len(self.harta[k]) + 1)

    def _categorii(self, coduri: list[tuple[int, ...]]) -> torch.Tensor:
        """Pentru fiecare literă: numărul categoriei pe fiecare nivel (lungimea textului × adâncime).

        O categorie nevăzută la antrenare (apare doar în textul nou) primește 0, ca un nivel gol: altfel
        modelul ar primi o descriere pe care n-a antrenat-o niciodată, adică zgomot.
        """
        if not coduri:
            return torch.zeros((0, self.adancime_memorie), dtype=torch.long)
        unice = list(dict.fromkeys(coduri))
        tabel = torch.tensor(
            [
                [
                    CATEGORIE_GOALA if k >= len(cod) or cod[k] == 0 else self.harta[k].get(cod[: k + 1], CATEGORIE_GOALA)
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
        if self.tokenizer == "bpe":
            assert self.tok is not None
            return torch.tensor(self.tok.codifica(text), dtype=torch.long)
        idx = {c: i for i, c in enumerate(self.vocabular)}
        nec = idx[NECUNOSCUT]
        return torch.tensor([idx.get(c, nec) for c in text], dtype=torch.long)

    def _marime_vocabular(self) -> int:
        if self.tokenizer == "bpe":
            assert self.tok is not None
            return self.tok.marime
        return len(self.vocabular)

    def _construieste(self) -> None:
        torch.manual_seed(self.samanta)
        categorii = [len(h) + 1 for h in self.harta] if self.foloseste_memorie else None
        self.retea = _GPT(
            self._marime_vocabular(), **self.setari, categorii_memorie=categorii, n_emb_memorie=self.n_emb_memorie
        ).to(self.dispozitiv)

    def _autocast(self):
        if self.dispozitiv.type == "cuda" and torch.cuda.is_bf16_supported():
            return torch.autocast("cuda", dtype=torch.bfloat16)
        return torch.autocast(self.dispozitiv.type, enabled=False)

    # --- contractul ---------------------------------------------------------

    def antreneaza(self, date: Any, buget_secunde: float) -> dict[str, Any]:
        text = date.text_antrenare()
        simboluri = None
        if self.tokenizer == "bpe":
            self.tok = TokenizerBPE.incarca(self.cale_tokenizer)
            simboluri = self.tok.codifica(text)
        else:
            self.vocabular = sorted(set(text)) + [NECUNOSCUT]
        memorie_t = None
        pregatire = 0.0
        if self._are_pozitii():
            # Pregătirea (memoria, nodurile) intră în bugetul de timp: comparațiile rămân cinstite.
            inceput_pregatire = time.perf_counter()
            memorie_t = self._pozitii(text, simboluri, la_antrenare=True).to(self.dispozitiv)
            pregatire = time.perf_counter() - inceput_pregatire
        self._construieste()
        assert self.retea is not None
        date_t = (torch.tensor(simboluri, dtype=torch.long) if simboluri is not None else self._codifica(text)).to(
            self.dispozitiv
        )
        ctx = self.setari["context"]
        if len(date_t) <= ctx + 1:
            raise ValueError("textul de antrenare e mai scurt decât contextul")
        optimizator = torch.optim.AdamW(self.retea.parameters(), lr=self.rata_invatare, weight_decay=0.1)
        generator = torch.Generator(device="cpu").manual_seed(self.samanta)

        self.retea.train()
        start = time.perf_counter() - pregatire
        pasi = 0
        pierdere = float("nan")
        while time.perf_counter() - start < buget_secunde and not (self.pasi_max and pasi >= self.pasi_max):
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
        if self.pasi_max:
            statistici["pasi_max"] = self.pasi_max
        if self.tokenizer == "bpe":
            statistici["tokenizer"] = "bpe"
            statistici["simboluri_antrenare"] = len(date_t)
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
        simboluri = self.tok.codifica(text) if self.tokenizer == "bpe" and self.tok is not None else None
        idx = (torch.tensor(simboluri, dtype=torch.long) if simboluri is not None else self._codifica(text)).to(
            self.dispozitiv
        )
        memorie = self._pozitii(text, simboluri).to(self.dispozitiv) if self._are_pozitii() else None
        ctx = self.setari["context"]
        nats = 0.0
        # primul simbol nu are context: îl socotim cu probabilitate uniformă
        biti_primul = math.log2(self._marime_vocabular())
        # bucăți de ctx+1 simboluri (ultima poate fi mai scurtă), câte 64 deodată
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
        if self.tokenizer == "bpe":
            return self._genereaza_simboluri(inceput, lungime, generator)
        text = inceput or " "
        idx = self._codifica(text).unsqueeze(0).to(self.dispozitiv)
        nec = self.vocabular.index(NECUNOSCUT)
        ctx = self.setari["context"]
        rezultat = []
        for _ in range(lungime):
            m = None
            if self._are_pozitii():  # memoria vede tot textul scris până acum, nimic din viitor
                m = self._pozitii(text, None)[-ctx:].unsqueeze(0).to(self.dispozitiv)
            logits = self.retea(idx[:, -ctx:], m)[:, -1, :].float()
            logits[:, nec] = -float("inf")  # nu generăm caracterul „necunoscut”
            prob = F.softmax(logits, dim=-1).cpu()
            urm = torch.multinomial(prob, 1, generator=generator)
            litera = self.vocabular[urm.item()]
            rezultat.append(litera)
            text += litera
            idx = torch.cat([idx, urm.to(self.dispozitiv)], dim=1)
        return "".join(rezultat)

    def _genereaza_simboluri(self, inceput: str, lungime: int, generator: torch.Generator) -> str:
        """Pe bucăți de cuvinte: generează simboluri până are cel puțin `lungime` litere, apoi taie exact."""
        assert self.retea is not None and self.tok is not None
        simboluri = self.tok.codifica(inceput or " ")
        noi: list[int] = []
        continuare = ""
        ctx = self.setari["context"]
        for _ in range(8 * lungime + 16):  # fiecare simbol adaugă cel puțin un octet; limită de siguranță
            if len(continuare) >= lungime:
                break
            toate = simboluri + noi
            idx = torch.tensor([toate[-ctx:]], dtype=torch.long, device=self.dispozitiv)
            m = None
            if self._are_pozitii():  # memoria vede tot ce s-a scris până acum, nimic din viitor
                m = self._pozitii("", toate)[-ctx:].unsqueeze(0).to(self.dispozitiv)
            logits = self.retea(idx, m)[:, -1, :].float()
            prob = F.softmax(logits, dim=-1).cpu()
            noi.append(int(torch.multinomial(prob, 1, generator=generator).item()))
            continuare = self.tok.decodeaza(noi)
        return (continuare + " " * lungime)[:lungime]

    def salveaza(self, cale: str) -> str:
        if self.retea is None:
            raise RuntimeError("nu am ce salva: modelul nu e antrenat")
        fisier = Path(cale).with_suffix(".pt")
        fisier.parent.mkdir(parents=True, exist_ok=True)
        torch.save(self._stare_de_salvat(), fisier)
        return str(fisier)

    def _stare_de_salvat(self) -> dict[str, Any]:
        """Tot ce trebuie ca modelul să poată fi reconstruit exact (modelele derivate adaugă ce le trebuie)."""
        assert self.retea is not None
        stare: dict[str, Any] = {"setari": self.setari, "vocabular": self.vocabular, "stare": self.retea.state_dict()}
        if self.foloseste_memorie:
            stare["memorie"] = {
                "adancime": self.adancime_memorie,
                "n_emb": self.n_emb_memorie,
                "harta": [[[list(cod), nr] for cod, nr in nivel.items()] for nivel in self.harta],
            }
        if self.tokenizer == "bpe" and self.tok is not None:  # tokenizerul intră în model: se încarcă singur
            stare["tokenizer"] = {"tip": "bpe", "bpe": self.tok.ca_dictionar()}
        return stare

    def incarca(self, cale: str) -> None:
        fisier = Path(cale)
        if not fisier.exists():
            fisier = fisier.with_suffix(".pt")
        salvat = torch.load(fisier, map_location=self.dispozitiv, weights_only=True)
        self._restaureaza(salvat)
        self._construieste()
        assert self.retea is not None
        self.retea.load_state_dict(salvat["stare"])

    def _restaureaza(self, salvat: dict[str, Any]) -> None:
        """Pune înapoi setările din fișierul salvat, înainte ca rețeaua să fie reconstruită."""
        self.setari = salvat["setari"]
        self.vocabular = salvat["vocabular"]
        tokenizer = salvat.get("tokenizer")  # modelele salvate înainte de Etapa M2 sunt pe litere
        self.tokenizer = "bpe" if tokenizer else "litere"
        self.tok = TokenizerBPE.din_dictionar(tokenizer["bpe"]) if tokenizer else None
        memorie = salvat.get("memorie")  # modelele salvate înainte de Etapa M1 nu au memorie
        self.foloseste_memorie = memorie is not None
        self.harta = []
        if memorie is not None:
            self.adancime_memorie = memorie["adancime"]
            self.n_emb_memorie = memorie["n_emb"]
            self.harta = [{tuple(cod): nr for cod, nr in nivel} for nivel in memorie["harta"]]
