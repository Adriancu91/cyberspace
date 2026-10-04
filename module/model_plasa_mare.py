"""Plasa adaptivă mare (Etapa M3, testul în trei trepte): un model mai mare decât încape pe placa video.

Ca plasa adaptivă (model_plasa_adaptiva.py: un nod pe raft plus nodul „rar”, noduri libere care ajută rafturile
încărcate, legături cu tărie, fiecare simbol calculează doar nodul lui și nodurile legate de el), dar:
1. Trunchiul (un GPT) stă pe placa video, cu optimizatorul lui. Nodurile (34 + 6 libere, mai mari) stau în RAM, cu
   greutățile întregi (fp32) și stările optimizatorului. La fiecare pas urcă pe placă doar nodurile cerute de lot, într-o
   copie bf16 (pe jumătate de mărime); după pasul înapoi, gradienții lor coboară, iar optimizatorul lor (AdamW) lucrează
   pe procesor, doar pentru nodurile folosite, fiecare cu numărul lui de pași. Placa nu ține niciodată stările
   optimizatorului nodurilor: asta permite un model mai mare decât cel mai mare GPT care încape.
2. Nimic nu pornește de la zero: cu cale_stare, fiecare experiment pornește din starea salvată de cel dinainte
   (greutățile trunchiului și ale nodurilor, optimizatorii, legăturile cu tăria lor, alocările nodurilor libere) și o
   salvează pe cea nouă după examen (testul rapid al lui Kronos o încarcă, dar nu o scrie). Un nod liber alocat pornește
   ca o copie a nodului pe care îl ajută. Când tăria unei legături se schimbă, cererea învățată se ajustează invers, ca
   rețeaua să nu sară: tăria rămâne punctul spre care trage uitarea greutăților.
3. Măsoară timpul petrecut pe mutatul nodurilor (urcarea pe placă, coborârea gradienților) și pe optimizatorul din RAM.
Textul, cuvintele lui și drumul lor se țin minte în director_cache (un text mare se pregătește o singură dată). Textul
stă în RAM, pe placă urcă doar loturile; pregătirea nu intră în bugetul de timp.
"""

from __future__ import annotations

import time
from collections import Counter
from pathlib import Path
from typing import Any

import torch
import torch.nn as nn
import torch.nn.functional as F

from module.model_continuu import amprenta, ia_placa, salveaza_atomic, simboluri_din_cache
from module.model_gpt import _GPT, ModelGPT
from module.model_plasa import Plasa
from module.model_plasa_adaptiva import (
    MINIM_PERECHE, NOD_RAR, PRAG_ASOCIERE, PRAG_RAFT, UMPLUTURA, ModelPlasaAdaptiva, StareAdaptiva, _asocierea, _cheie,
)

VERSIUNE_STARE = 1


# --- nodurile din RAM ------------------------------------------------------------------------------


class _NoduriInRAM:
    """Greutățile nodurilor (fp32, în RAM), optimizatorul lor (AdamW „topit” al PyTorch, pe procesor) și urcarea pe placă
    la cerere. Fiecare nod are parametrii lui (felii din tensorii mari), deci optimizatorul îi actualizează doar pe cei
    care au primit gradienți (nodurile urcate), fiecare cu numărul lui de pași."""

    def __init__(self, greutati: dict[str, torch.Tensor]) -> None:
        self.greutati = greutati
        self.n = greutati["sus"].shape[0]
        self._parametri = {(nume, k): nn.Parameter(t[k]) for nume, t in greutati.items() for k in range(self.n)}
        self.optimizator: torch.optim.Optimizer | None = None  # se face la primul pas (are nevoie de rata de învățare)
        self._stare_optimizator: dict[str, Any] | None = None
        self._tampon: dict[str, torch.Tensor] | None = None
        self.timp: Counter[str] = Counter()  # secunde: „sus” (pe placă), „jos” (gradienții înapoi), „optimizator”
        self.noduri_urcate = 0
        self.urcari = 0

    def _optimizatorul(self, rata: float, scadere: float) -> torch.optim.Optimizer:
        if self.optimizator is None:
            self.optimizator = torch.optim.AdamW(list(self._parametri.values()), lr=rata, weight_decay=scadere, fused=True)
            if self._stare_optimizator is not None:
                self.optimizator.load_state_dict(self._stare_optimizator)
                self._stare_optimizator = None
        return self.optimizator

    @classmethod
    def noi(cls, n_noduri: int, n_emb: int, n_ascuns: int, samanta: int) -> _NoduriInRAM:
        """Ca nodurile din M2: strat ascuns cu greutăți mici la întâmplare, ieșirea de la zero („tăcute”)."""
        g = torch.Generator().manual_seed(samanta)
        limita = n_emb**-0.5  # ca la nn.Linear
        return cls({
            "ln_pondere": torch.ones(n_noduri, n_emb),
            "ln_deplasare": torch.zeros(n_noduri, n_emb),
            "sus": torch.empty(n_noduri, n_emb, n_ascuns).uniform_(-limita, limita, generator=g),
            "sus_deplasare": torch.empty(n_noduri, n_ascuns).uniform_(-limita, limita, generator=g),
            "jos": torch.zeros(n_noduri, n_ascuns, n_emb),
            "jos_deplasare": torch.zeros(n_noduri, n_emb),
        })

    def parametri(self) -> int:
        return sum(v.numel() for v in self.greutati.values())

    def _tampoane(self, pe_placa: bool) -> dict[str, torch.Tensor]:
        if self._tampon is None:  # bf16, fixat în RAM (pinned) când există placă: urcă și coboară repede
            self._tampon = {
                k: torch.empty(v.shape, dtype=torch.bfloat16, pin_memory=pe_placa) for k, v in self.greutati.items()
            }
        return self._tampon

    def urca(self, sloturi: list[int], dispozitiv: torch.device, cu_gradient: bool) -> dict[str, torch.Tensor]:
        """Copiile nodurilor cerute, pe placă (bf16; pe procesor rămân fp32), în ordinea din `sloturi`."""
        start = time.perf_counter()
        urcate = {}
        if dispozitiv.type == "cuda":
            tampon = self._tampoane(True)
            for nume, sursa in self.greutati.items():
                for j, k in enumerate(sloturi):
                    tampon[nume][j].copy_(sursa[k])
                urcate[nume] = tampon[nume][: len(sloturi)].to(dispozitiv)
        else:
            urcate = {nume: sursa[sloturi].clone() for nume, sursa in self.greutati.items()}
        if cu_gradient:
            for t in urcate.values():
                t.requires_grad_(True)
        self.timp["sus"] += time.perf_counter() - start
        self.noduri_urcate += len(sloturi)
        self.urcari += 1
        return urcate

    def pas(self, sloturi: list[int], gradiente: dict[str, torch.Tensor | None], factor: float, rata: float,
            scadere: float) -> None:
        """AdamW doar pentru nodurile urcate: gradienții coboară în RAM, apoi optimizatorul face pasul lor."""
        start = time.perf_counter()
        folositi = []
        for nume, g in gradiente.items():
            if g is None:
                continue
            if g.device.type == "cuda":
                tampon = self._tampoane(True)[nume][: len(sloturi)]
                tampon.copy_(g)
                g = tampon
            for j, k in enumerate(sloturi):
                p = self._parametri[(nume, k)]
                p.grad = g[j].float() if factor == 1.0 else g[j].float().mul_(factor)
                folositi.append(p)
        self.timp["jos"] += time.perf_counter() - start
        start = time.perf_counter()
        self._optimizatorul(rata, scadere).step()  # nodurile fără gradient (neurcate) nu se schimbă
        for p in folositi:
            p.grad = None
        self.timp["optimizator"] += time.perf_counter() - start

    def copiaza(self, din: int, in_: int) -> None:
        """Nodul `in_` devine o copie a nodului `din` (greutăți și optimizator): un ajutor nou pornește de unde e cel ajutat."""
        for nume, t in self.greutati.items():
            t[in_].copy_(t[din])
            if self.optimizator is not None:
                sursa = self.optimizator.state.get(self._parametri[(nume, din)])
                if sursa:
                    self.optimizator.state[self._parametri[(nume, in_)]] = {k: v.clone() for k, v in sursa.items()}

    def stare(self) -> dict[str, Any]:
        stare: dict[str, Any] = {"greutati": self.greutati}
        optimizator = self.optimizator.state_dict() if self.optimizator is not None else self._stare_optimizator
        if optimizator is not None:
            stare["optimizator"] = optimizator
        return stare

    @classmethod
    def din_stare(cls, stare: dict[str, Any]) -> _NoduriInRAM:
        noduri = cls({k: t.float().contiguous() for k, t in stare["greutati"].items()})
        noduri._stare_optimizator = stare.get("optimizator")  # se încarcă la primul pas
        return noduri


def _calcul_noduri(x: torch.Tensor, poz: torch.Tensor, loc: torch.Tensor, cap: int, w: dict[str, torch.Tensor]) -> torch.Tensor:
    """Nodurile urcate, fiecare pe coada lui: x = perechi × n_emb (normalizat), poz = al câtelea nod urcat."""
    tip = w["sus"].dtype
    coada = torch.zeros(w["sus"].shape[0], cap, x.size(-1), dtype=tip, device=x.device).index_put(
        (poz, loc), (x * w["ln_pondere"][poz] + w["ln_deplasare"][poz]).to(tip)
    )
    ascuns = F.gelu(torch.baddbmm(w["sus_deplasare"].unsqueeze(1), coada, w["sus"]))
    return torch.baddbmm(w["jos_deplasare"].unsqueeze(1), ascuns, w["jos"])[poz, loc]


class _GPTCuNoduriInRAM(_GPT):
    def __init__(
        self, *args: Any, noduri: _NoduriInRAM, vecini: list[list[int]] | None = None,
        legaturi: list[list[float]] | None = None, **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.noduri = noduri  # nu e un nn.Module: greutățile nodurilor nu sunt parametri ai rețelei, stau în RAM
        n = noduri.n
        self.pondere_centru = nn.Parameter(torch.ones(n))  # nodul central: cât contează fiecare nod
        self.cerere = nn.Parameter(torch.zeros(n, n))  # cât „cere” un nod de la altul (învățat)
        vecini = vecini or [[k] for k in range(n)]
        latime = max(len(v) for v in vecini)
        self.register_buffer(
            "vecini", torch.tensor([v + [UMPLUTURA] * (latime - len(v)) for v in vecini], dtype=torch.long), persistent=False
        )
        self.register_buffer("legaturi", torch.tensor(legaturi or [[0.0] * n for _ in range(n)]), persistent=False)
        self.register_buffer("identitate", torch.eye(n), persistent=False)
        self.ultimele_noduri: tuple[list[int], dict[str, torch.Tensor]] | None = None

    def amestec(self) -> torch.Tensor:
        return self.identitate + (self.legaturi + self.cerere) * (1 - self.identitate)

    def _plan(self, noduri: torch.Tensor) -> tuple[Any, ...] | None:
        """Perechile (simbol, nod) de calculat, puse la coadă pe noduri. Umplutura n-are niciuna."""
        plat = noduri.reshape(-1)
        vecini = torch.where((plat >= 0).unsqueeze(-1), self.vecini[plat.clamp_min(0)], UMPLUTURA)
        simbol, coloana = (vecini >= 0).nonzero(as_tuple=True)
        if simbol.numel() == 0:
            return None
        nod = vecini[simbol, coloana]
        ordine = torch.argsort(nod, stable=True)
        simbol, nod = simbol[ordine], nod[ordine]
        numar = torch.bincount(nod, minlength=self.vecini.size(0))
        loc = torch.arange(nod.numel(), device=nod.device) - (torch.cumsum(numar, 0) - numar)[nod]
        return simbol, plat[simbol], nod, loc, int(numar.max())

    def forward(self, idx: torch.Tensor, extra: torch.Tensor | None = None) -> torch.Tensor:
        if extra is None:
            raise ValueError("modelul cu noduri trebuie să știe, pentru fiecare simbol, la ce nod merge")
        memorie = extra[..., :-1] if self.memorie is not None else None
        plan = self._plan(extra[..., -1])
        h = self.trunchi(idx, memorie)
        self.ultimele_noduri = None
        if plan is not None:
            simbol, nod_simbol, nod, loc, cap = plan
            sloturi = torch.unique_consecutive(nod).tolist()  # doar nodurile cerute de lot urcă pe placă
            la_antrenare = self.training and torch.is_grad_enabled()
            urcate = self.noduri.urca(sloturi, h.device, la_antrenare)
            harta = torch.full((self.noduri.n,), -1, dtype=torch.long, device=h.device)
            harta[torch.tensor(sloturi, device=h.device)] = torch.arange(len(sloturi), device=h.device)
            plat = h.reshape(-1, h.size(-1))
            iesiri = _calcul_noduri(F.layer_norm(plat[simbol], plat.shape[-1:]), harta[nod], loc, cap, urcate)
            ponderi = self.amestec()[nod_simbol, nod] * self.pondere_centru[nod]
            adaos = torch.zeros_like(plat).index_add(0, simbol, (iesiri.float() * ponderi.unsqueeze(-1)).to(plat.dtype))
            h = h + adaos.view_as(h)
            if la_antrenare:
                self.ultimele_noduri = (sloturi, urcate)
        return self.cap(self.ln(h))


class _CuvintePeNod:
    """Cuvintele primite de un nod la antrenare, socotite doar când e nevoie (la împărțirea unui nod încărcat)."""

    def __init__(self, nume_noduri: list[str], nod_cuvant: torch.Tensor, cuvant: torch.Tensor, vocabular: list[str]) -> None:
        self._index = {n: i for i, n in enumerate(nume_noduri)}
        self._nod_cuvant, self._cuvant, self._vocabular = nod_cuvant, cuvant, vocabular

    def get(self, nod: str, implicit: Any = None) -> Counter[str]:
        if nod not in self._index:
            return implicit if implicit is not None else Counter()
        numar = torch.bincount(self._cuvant[self._nod_cuvant == self._index[nod]].long(), minlength=len(self._vocabular))
        return Counter({self._vocabular[i]: int(numar[i]) for i in numar.nonzero().view(-1).tolist()})


# --- modelul ---------------------------------------------------------------------------------------


class ModelPlasaMare(ModelPlasaAdaptiva):
    MANIFEST = {
        "nume": "model_plasa_mare",
        "port": "model",
        "versiune": "0.1.0",
        "versiune_contract": 1,
        "resurse": {"gpu": True, "memorie_gpu_mb": 5500, "ram_mb": 16000},
        "permisiuni": ["citire_fisier", "scriere_fisier"],
    }

    _pregatirea_intra_in_buget = False
    _textul_ramane_in_ram = True

    def __init__(
        self,
        n_ascuns_nod: int = 3072,
        noduri_libere: int = 6,
        cale_stare: str = "",
        director_cache: str = "",
        tokenizer: str = "bpe",
        **setari: Any,
    ) -> None:
        super().__init__(n_ascuns_nod=n_ascuns_nod, noduri_libere=noduri_libere, cale_plasa="", tokenizer=tokenizer, **setari)
        if self.foloseste_memorie:
            raise ValueError("plasa mare nu folosește memorie=true (nodurile vin oricum din memorie)")
        self.cale_stare = cale_stare
        self.director_cache = director_cache
        self.noduri_ram: _NoduriInRAM | None = None
        self.pasi_total = 0
        self.continuat = False
        self._salvat: dict[str, Any] | None = None
        self._cuvinte_antrenare: tuple[torch.Tensor, torch.Tensor, list[str]] | None = None

    # --- drumul cuvintelor (40 de locuri fixe: rafturile, „rar”, apoi cele 6 libere) --------------

    def _foloseste_starea(self, stare: StareAdaptiva) -> None:
        self.nume_noduri = [*(stare.rafturi or []), NOD_RAR, *(f"liber{i}" for i in range(1, self.noduri_libere + 1))]
        self._index = {nume: i for i, nume in enumerate(self.nume_noduri)}
        self._rafturi_cu_nod = list(stare.rafturi or [])
        self._ajutor_pentru = {}
        for ajutor in stare.ajutoare:  # în ordinea alocării: ajutorul unui ajutor îl înlocuiește pe primul
            for cuvant in ajutor["cuvinte"]:
                self._ajutor_pentru[(ajutor["raft"], cuvant)] = ajutor["nume"]

    def _semnatura_memoriei(self) -> bytes:
        m = self.sursa_memorie
        return repr((type(m).__name__, getattr(m, "MANIFEST", {}).get("versiune"), getattr(m, "sursa", None),
                     getattr(m, "fara_cuvinte_de_legatura", None), getattr(m, "sens_dupa_context", None))).encode()

    def _cuvintele_textului(self, text: str, simboluri: Any, tine_minte: bool) -> dict[str, Any]:
        """Pentru fiecare cuvânt terminat: raftul (−1 = umplutură) și cuvântul (număr); pentru fiecare simbol: al câtelea
        cuvânt terminat e ultimul până la ultima lui literă completă (−1 = niciunul). Fără viitor, ca la plasa adaptivă."""
        memoria = self.sursa_memorie
        rafturi = list(getattr(memoria, "rafturi", None) or [])
        fisier = None
        if tine_minte and self.director_cache and rafturi:
            cheie = amprenta(text.encode("utf-8"), Path(self.cale_tokenizer).read_bytes(), self._semnatura_memoriei())
            fisier = Path(self.director_cache) / f"cuvinte_{cheie}.pt"
            if fisier.exists():
                return torch.load(fisier, weights_only=True)
        assert self.tok is not None
        lista = simboluri.tolist() if isinstance(simboluri, torch.Tensor) else simboluri
        text, capete = self.tok.capete_caractere(lista)
        pozitii: list[int] = []
        raft: list[int] = []
        cuvant: list[int] = []
        vocabular: dict[str, int] = {}
        if rafturi and hasattr(memoria, "cuvinte_cu_coduri"):
            for pozitie, c, cod, _ in memoria.cuvinte_cu_coduri(text):
                pozitii.append(pozitie)
                raft.append(cod[1] - 1 if len(cod) > 1 and 1 <= cod[0] <= 4 else -1)
                cuvant.append(vocabular.setdefault(_cheie(c), len(vocabular)))
        cuvant_simbol = torch.searchsorted(torch.tensor(pozitii, dtype=torch.long), torch.tensor(capete) - 1, right=True) - 1
        date = {
            "rafturi_memoriei": rafturi,
            "raft": torch.tensor(raft, dtype=torch.int16),
            "cuvant": torch.tensor(cuvant, dtype=torch.int32),
            "vocabular": list(vocabular),
            "cuvant_simbol": cuvant_simbol.to(torch.int32),
        }
        if fisier is not None:
            salveaza_atomic(date, fisier)
        return date

    def _noduri_cuvintelor(self, date: dict[str, Any]) -> torch.Tensor:
        """Nodul fiecărui cuvânt: al raftului lui, „rar” sau ajutorul care l-a preluat (−1 = umplutură)."""
        rafturi = date["rafturi_memoriei"]
        raft = date["raft"].long()
        if not rafturi or raft.numel() == 0:
            return torch.full((raft.numel(),), UMPLUTURA, dtype=torch.long)
        baza = torch.tensor([self._index[r] if r in self._rafturi_cu_nod else self._index[NOD_RAR] for r in rafturi])
        nod_baza = torch.where(raft >= 0, baza[raft.clamp_min(0)], UMPLUTURA)
        nod = nod_baza.clone()
        pe_ajutor: dict[tuple[str, str], list[int]] = {}
        numar_cuvant = {c: i for i, c in enumerate(date["vocabular"])}
        for (raft_ajutor, c), ajutor in self._ajutor_pentru.items():
            if c in numar_cuvant:
                pe_ajutor.setdefault((raft_ajutor, ajutor), []).append(numar_cuvant[c])
        for (raft_ajutor, ajutor), cuvinte in pe_ajutor.items():
            masca = (nod_baza == self._index[raft_ajutor]) & torch.isin(date["cuvant"], torch.tensor(cuvinte, dtype=torch.int32))
            nod[masca] = self._index[ajutor]
        return nod

    def _pozitii(self, text: str, simboluri: list[int] | None, la_antrenare: bool = False) -> torch.Tensor:
        """Pentru fiecare simbol: nodul la care merge (−1 = trunchi). La antrenare, și tot ce măsoară plasa pe text."""
        assert self.tok is not None, "plasa mare lucrează pe bucăți de cuvinte (tokenizer = bpe)"
        if simboluri is None:
            simboluri = self.tok.codifica(text)
        date = self._cuvintele_textului(text, simboluri, tine_minte=la_antrenare)
        if la_antrenare:
            self._pregateste_mare(date)
        nod_cuvant = self._noduri_cuvintelor(date)
        k = date["cuvant_simbol"].long()
        noduri = torch.full(k.shape, UMPLUTURA, dtype=torch.long)
        if nod_cuvant.numel():
            noduri = torch.where(k >= 0, nod_cuvant[k.clamp_min(0)], noduri)
        if la_antrenare:
            self.simboluri_pe_nod = torch.bincount(noduri[noduri >= 0], minlength=len(self.nume_noduri)).tolist()
            self.simboluri_umplutura = int((noduri < 0).sum())
            return noduri.to(torch.int8).unsqueeze(-1)  # în RAM, mic: lotul urcă pe placă ca numere întregi
        return noduri.unsqueeze(-1)

    def _pregateste_mare(self, date: dict[str, Any]) -> None:
        """La antrenare: rafturile cu nod (doar la primul experiment), drumul cuvintelor, încărcarea nodurilor, asocierea
        dintre noduri și ce noduri calculează fiecare simbol (ca la plasa adaptivă, dar pe tensori: texte mari)."""
        if self.stare is None:
            self.stare = StareAdaptiva(self.noduri_libere)
        stare = self.stare
        if stare.rafturi is None:
            raft = date["raft"].long()
            numar = torch.bincount(raft[raft >= 0], minlength=len(date["rafturi_memoriei"]))
            total = int(numar.sum())
            ordine = sorted(range(len(numar)), key=lambda i: (-int(numar[i]), date["rafturi_memoriei"][i]))
            stare.rafturi = [date["rafturi_memoriei"][i] for i in ordine if total and int(numar[i]) / total >= PRAG_RAFT]
        self._foloseste_starea(stare)
        n = len(self.nume_noduri)
        nod_cuvant = self._noduri_cuvintelor(date)
        self._cuvinte_antrenare = (nod_cuvant, date["cuvant"], date["vocabular"])
        self._incarcari = torch.bincount(nod_cuvant[nod_cuvant >= 0], minlength=n).tolist()
        self._asociere, perechi = _asocierea(nod_cuvant, n)
        self._asociere_nastere = [
            [v if perechi[a][b] >= MINIM_PERECHE else 0.0 for b, v in enumerate(rand)] for a, rand in enumerate(self._asociere)
        ]
        legate = {(self._index[a], self._index[b]) for a, b in stare.legaturi if a in self._index and b in self._index}
        self._legaturi_start = [[0.0] * n for _ in range(n)]
        for a, b in legate:
            self._legaturi_start[a][b] = stare.legaturi[(self.nume_noduri[a], self.nume_noduri[b])]["tarie"]
        self._vecini = [
            [a] + [b for b in range(n) if b != a and ((a, b) in legate or self._asociere_nastere[a][b] >= PRAG_ASOCIERE)]
            for a in range(n)
        ]

    # --- rețeaua, starea păstrată și antrenarea -----------------------------------------------------

    def elibereaza_placa(self) -> None:
        self.retea = None
        self.optimizator = None

    def _simboluri(self, text: str) -> Any:
        return simboluri_din_cache(self.tok, text, self.director_cache, self.cale_tokenizer)

    def _incarca_starea(self) -> None:
        """La începutul antrenării: plasa și (dacă există) tot modelul, din starea salvată după examenul de dinainte."""
        ia_placa(self)
        self.stare = StareAdaptiva(self.noduri_libere)
        self._salvat = None
        self.continuat = False
        if not self.cale_stare or not Path(self.cale_stare).exists():
            return
        salvat = torch.load(self.cale_stare, map_location="cpu", weights_only=True)
        if salvat.get("versiune") != VERSIUNE_STARE or salvat["setari"] != self.setari or salvat["n_ascuns_nod"] != self.n_ascuns_nod:
            raise ValueError(f"Starea din „{self.cale_stare}” e a altui model; folosește alt cale_stare.")
        plasa = salvat["plasa"]
        self.stare.rafturi = plasa["rafturi"]
        self.stare.ajutoare = plasa["ajutoare"]
        self.stare.experimente = plasa["experimente"]
        self.stare.legaturi = {(l["de_la"], l["la"]): {k: l[k] for k in ("tarie", "stare", "nascuta_la", "sub_prag")}
                               for l in plasa["legaturi"]}
        self.pasi_total = salvat["pasi_total"]
        self._salvat = salvat
        self.continuat = True

    def _construieste(self) -> None:
        torch.manual_seed(self.samanta)
        if self.noduri_ram is None or self.noduri_ram.n != len(self.nume_noduri):
            self.noduri_ram = _NoduriInRAM.noi(len(self.nume_noduri), self.setari["n_emb"], self.n_ascuns_nod, self.samanta)
        self.retea = _GPTCuNoduriInRAM(
            self._marime_vocabular(), **self.setari, noduri=self.noduri_ram, vecini=self._vecini, legaturi=self._legaturi_start,
        ).to(self.dispozitiv)

    def _pregateste_reteaua(self) -> None:
        if self._salvat is not None:  # nodurile din starea salvată, înainte de construirea rețelei
            self.noduri_ram = _NoduriInRAM.din_stare(self._salvat["noduri"])
        super()._pregateste_reteaua()
        assert self.retea is not None and self.optimizator is not None
        if self._salvat is not None:
            self.retea.load_state_dict(self._salvat["retea"], strict=False)  # vecinii și legăturile vin din plasă
            self.optimizator.load_state_dict(self._salvat["optimizator"])
            self._salvat = None

    def _samanta_loturi(self) -> int:
        # Primul experiment alege bucățile ca GPT-ul simplu; la fiecare continuare, alte bucăți de text.
        return self.samanta if self.pasi_total == 0 else self.samanta * 1_000_003 + self.pasi_total

    def _pas(self, x: torch.Tensor, y: torch.Tensor, m: torch.Tensor | None) -> float:
        """Un pas: înainte și înapoi pe placă; trunchiul face pasul acolo, nodurile urcate în RAM (gradienții coboară)."""
        retea, optimizator = self.retea, self.optimizator
        assert isinstance(retea, _GPTCuNoduriInRAM) and optimizator is not None and self.noduri_ram is not None
        with self._autocast():
            logits = retea(x, m)
            loss = F.cross_entropy(logits.float().view(-1, logits.size(-1)), y.view(-1))
        optimizator.zero_grad(set_to_none=True)
        loss.backward()
        sloturi, urcate = retea.ultimele_noduri or ([], {})
        gradiente = {nume: t.grad for nume, t in urcate.items()}
        norme = [p.grad.detach().float().norm() for p in retea.parameters() if p.grad is not None]
        norme += [g.detach().float().norm() for g in gradiente.values() if g is not None]
        total = float(torch.linalg.vector_norm(torch.stack(norme))) if norme else 0.0
        factor = min(1.0, 1.0 / (total + 1e-6))  # ca clip_grad_norm_(..., 1.0), pe trunchi și noduri împreună
        if factor < 1.0:
            for p in retea.parameters():
                if p.grad is not None:
                    p.grad.mul_(factor)
        optimizator.step()
        if sloturi:
            self.noduri_ram.pas(sloturi, gradiente, factor, self.rata_invatare, 0.1)
        retea.ultimele_noduri = None
        return loss.item()

    def antreneaza(self, date: Any, buget_secunde: float) -> dict[str, Any]:
        statistici = super().antreneaza(date, buget_secunde)
        assert self.noduri_ram is not None and self.retea is not None and self.stare is not None
        statistici["noduri"]["active"] = len(self.stare.noduri())  # cele 6 libere numără doar când sunt alocate
        self.pasi_total += statistici["pasi"]
        timp = self.noduri_ram.timp
        bucla = statistici.get("secunde_bucla") or 1e-9
        trunchi = sum(p.numel() for p in self.retea.parameters())
        statistici.update(
            pasi_total=self.pasi_total,
            continuat=self.continuat,
            parametri_trunchi=trunchi,
            parametri_noduri=self.noduri_ram.parametri(),
            parametri_total=trunchi + self.noduri_ram.parametri(),
            mutare_noduri={
                "secunde_sus": round(timp["sus"], 1),
                "secunde_jos": round(timp["jos"], 1),
                "secunde_optimizator_ram": round(timp["optimizator"], 1),
                "parte_din_antrenare": round((timp["sus"] + timp["jos"] + timp["optimizator"]) / bucla, 3),
                "noduri_urcate_pe_pas": round(self.noduri_ram.noduri_urcate / max(1, self.noduri_ram.urcari), 1),
            },
        )
        if self.dispozitiv.type == "cuda":
            statistici["memorie_rezervata_mb"] = round(torch.cuda.max_memory_reserved() / 2**20)
        return statistici

    def dupa_examen(self, rezultat: dict[str, Any]) -> dict[str, Any] | None:
        """După examen (doar experimentul adevărat): plasa învață din câștig (un număr), nodurile libere se alocă după
        cuvintele primite la antrenare, iar tot modelul se salvează pentru experimentul următor."""
        if self.stare is None or self._cereri is None or self._folosire is None or self.retea is None:
            return None
        retea = self.retea
        assert isinstance(retea, _GPTCuNoduriInRAM) and self.noduri_ram is not None and self._cuvinte_antrenare is not None
        tarii_vechi = {pereche: leg["tarie"] for pereche, leg in self.stare.legaturi.items()}
        plasa = Plasa(self.nume_noduri, self.stare.legaturi, self.stare.experimente, prag_asociere=PRAG_ASOCIERE)
        schimbari = plasa.actualizeaza(self._cereri, self._folosire, rezultat.get("castig"), self._asociere_nastere)
        nascute = [{"de_la": a, "la": b} for (a, b), leg in plasa.legaturi.items() if leg["nascuta_la"] == plasa.experimente]
        with torch.no_grad():  # tăria s-a schimbat: cererea se ajustează invers, ca rețeaua să nu sară
            for a, b in set(tarii_vechi) | set(plasa.legaturi):
                delta = plasa.legaturi.get((a, b), {}).get("tarie", 0.0) - tarii_vechi.get((a, b), 0.0)
                if delta and a in self._index and b in self._index:
                    retea.cerere[self._index[a], self._index[b]] -= delta
        self.stare.legaturi, self.stare.experimente = plasa.legaturi, plasa.experimente
        nod_cuvant, cuvant, vocabular = self._cuvinte_antrenare
        alocari = self.stare.actualizeaza_alocarile(
            dict(zip(self.nume_noduri, self._incarcari)), _CuvintePeNod(self.nume_noduri, nod_cuvant, cuvant, vocabular)
        )
        with torch.no_grad():  # un ajutor nou pornește ca o copie a nodului pe care îl ajută
            for alocare in alocari["alocate"]:
                din, in_ = self._index[alocare["ajuta"]], self._index[alocare["nod"]]
                self.noduri_ram.copiaza(din, in_)
                retea.pondere_centru[in_] = retea.pondere_centru[din]
                legaturi = torch.zeros_like(retea.cerere[din])
                for (a, b), leg in self.stare.legaturi.items():
                    if a == alocare["ajuta"] and b in self._index:
                        legaturi[self._index[b]] = leg["tarie"]
                retea.cerere[in_] = retea.cerere[din] + legaturi
                retea.cerere[:, in_] = 0.0
        self._salveaza_starea()
        return {
            "plasa": {**plasa.stare(), **schimbari, "nascute_acum": nascute, "castig_primit": rezultat.get("castig")},
            "noduri": alocari,
            "continuare": {"pasi_total": self.pasi_total, "fisier": self.cale_stare},
        }

    def _salveaza_starea(self) -> None:
        if not self.cale_stare or self.stare is None or self.retea is None or self.optimizator is None:
            return
        assert self.noduri_ram is not None
        salveaza_atomic(
            {
                "versiune": VERSIUNE_STARE,
                "setari": self.setari,
                "n_ascuns_nod": self.n_ascuns_nod,
                "retea": self.retea.state_dict(),
                "optimizator": self.optimizator.state_dict(),
                "noduri": self.noduri_ram.stare(),
                "plasa": {
                    "rafturi": self.stare.rafturi, "ajutoare": self.stare.ajutoare, "experimente": self.stare.experimente,
                    "legaturi": [{"de_la": a, "la": b, **leg} for (a, b), leg in self.stare.legaturi.items()],
                },
                "pasi_total": self.pasi_total,
            },
            self.cale_stare,
        )
        self.stare.salveaza(Path(self.cale_stare).with_suffix(".plasa.json"))  # pentru oameni: plasa, ca text

    # --- salvarea modelului (pentru Kronos) ---------------------------------------------------------

    def _stare_de_salvat(self) -> dict[str, Any]:
        stare = super()._stare_de_salvat()
        assert self.noduri_ram is not None
        stare["noduri_ram"] = {"greutati": self.noduri_ram.greutati}
        return stare

    def _restaureaza(self, salvat: dict[str, Any]) -> None:
        super()._restaureaza(salvat)
        self.noduri_ram = _NoduriInRAM.din_stare(salvat["noduri_ram"])
