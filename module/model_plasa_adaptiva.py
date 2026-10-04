"""Plasa adaptivă de noduri (Etapa M3, pasul 2).

Pornește de la GPT-ul pe bucăți de cuvinte (trunchiul comun) și de la regulile plasei din M2 (model_plasa.py):

1. Nodurile: câte un nod mic pentru fiecare raft al bibliotecii care primește cel puțin 0,5% din cuvintele cu sens
   ale textului de antrenare, plus nodul „rar” pentru celelalte rafturi. Se aleg la primul experiment și nu se mai
   mută niciodată. Umplutura (cuvintele de legătură, cele negăsite, începutul textului) rămâne pe trunchi, fără nod.
   Memoria trebuie să aibă pornite fara_cuvinte_de_legatura și sens_dupa_context (config/laptop_plasa_adaptiva.toml).
2. Rezerva: noduri_libere noduri libere (implicit 6). După fiecare examen se numără cuvintele primite de fiecare nod
   la antrenare (nimic din textul de examen). Un nod cu peste 2× media primește în ajutor un nod liber, care preia
   cam jumătate din cuvintele lui: cuvinte întregi (de ex. Tim și Mom pe un nod, Lily și Tom pe celălalt), aceleași
   de la un experiment la altul. Pe coduri n-ar merge: toate numele au același cod, „nume de persoană”. Un ajutor se
   întoarce în rezervă după 3 examene la rând în care raftul lui a primit mai puțin decât media. Nodurile alocate nu
   se mută niciodată. Alocările intră în jurnal și se folosesc de la experimentul următor.
3. Fiecare simbol calculează doar nodul lui și nodurile legate de el: legăturile vii și perechile care se pot naște
   (cuvinte vecine, cu ordine, cu asociere de cel puțin 3×, văzute de cel puțin 100 de ori). Fără acestea din urmă,
   un nod n-ar putea „cere” o legătură nouă. Nodurile de care un simbol n-are nevoie nu se calculează deloc.
Legăturile urmează regulile din M2 (clasa Plasa: naștere, întărire, slăbire, uitare, tăiere), cu pragul de naștere 3×.
Nodul central adună nodurile, ponderat. Nodurile pornesc tăcute: la început, modelul e identic cu GPT-ul simplu.
Starea (rafturile cu nod, ajutoarele, legăturile) se păstrează între experimente în cale_plasa.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import torch
import torch.nn as nn
import torch.nn.functional as F

from module.model_gpt import _GPT, ModelGPT
from module.model_plasa import PRAG_CERERE, Plasa

NOD_RAR = "rar"
UMPLUTURA = -1  # simbolurile fără nod: rămân pe trunchi
PRAG_RAFT = 0.005  # un raft cu cel puțin 0,5% din cuvintele cu sens primește un nod
PRAG_SUPRAINCARCARE = 2.0  # un nod cu peste 2× media primește un ajutor din rezervă
EXAMENE_SUB_MEDIE = 3  # un ajutor se întoarce în rezervă după atâtea examene la rând cu raftul sub medie
PRAG_ASOCIERE = 3.0  # o legătură se poate naște doar între noduri ale căror cuvinte stau alături de 3× mai des...
MINIM_PERECHE = 100  # ...decât întâmplător, într-o pereche văzută de cel puțin 100 de ori
VERSIUNE_STARE = 1


def _cheie(cuvant: str) -> str:
    return cuvant.lower().strip("'")


def _jumatate(cuvinte: Counter[str]) -> list[str]:
    """Cuvintele pe care le preia un ajutor: de la cele mai dese, fiecare spre partea care are mai puține (cam jumătate)."""
    preluate: list[str] = []
    la_ajutor = ramase = 0
    for cuvant, n in sorted(cuvinte.items(), key=lambda x: (-x[1], x[0])):
        if la_ajutor <= ramase:
            preluate.append(cuvant)
            la_ajutor += n
        else:
            ramase += n
    return preluate


def _asocierea(noduri: list[int], n: int) -> tuple[list[list[float]], list[list[int]]]:
    """asociere[a][b] = de câte ori mai des decât întâmplător e urmat un cuvânt al nodului a de unul al lui b (cuvinte
    vecine; umplutura stă și ea în șir, dar nu are nod) și de câte ori apare fiecare pereche."""
    zero = [[0.0] * n for _ in range(n)], [[0] * n for _ in range(n)]
    total = len(noduri)
    if total < 2 or n == 0:
        return zero
    t = torch.as_tensor(noduri, dtype=torch.long)
    a, b = t[:-1], t[1:]
    bune = (a >= 0) & (b >= 0)
    perechi = torch.bincount(a[bune] * n + b[bune], minlength=n * n).view(n, n)
    frecventa = torch.bincount(t[t >= 0], minlength=n).double() / total
    asteptat = frecventa.unsqueeze(1) * frecventa.unsqueeze(0)
    asociere = torch.where(
        asteptat > 0, (perechi.double() / (total - 1)) / asteptat.clamp_min(1e-12), torch.zeros(n, n, dtype=torch.double)
    )
    return asociere.tolist(), perechi.tolist()


# --- starea păstrată între experimente ------------------------------------------------------------


class StareAdaptiva:
    """Ce se păstrează între experimente: rafturile cu nod, ajutoarele luate din rezervă și legăturile dintre noduri."""

    def __init__(self, noduri_libere: int = 6) -> None:
        self.rafturi: list[str] | None = None  # rafturile cu nod propriu, alese la primul experiment
        self.noduri_libere = noduri_libere
        # Ajutoarele alocate, în ordinea alocării: {"nume", "ajuta", "raft", "cuvinte", "alocat_la", "sub_medie"}.
        self.ajutoare: list[dict[str, Any]] = []
        self.legaturi: dict[tuple[str, str], dict[str, Any]] = {}
        self.experimente = 0

    @classmethod
    def incarca(cls, cale: str | Path, noduri_libere: int) -> StareAdaptiva:
        stare = cls(noduri_libere)
        fisier = Path(cale)
        if not fisier.exists():
            return stare  # prima dată: rafturile se aleg la antrenare
        date = json.loads(fisier.read_text(encoding="utf-8"))
        if date.get("versiune") != VERSIUNE_STARE:
            raise ValueError(f"Starea plasei din „{cale}” are altă versiune ({date.get('versiune')}); folosește alt cale_plasa.")
        stare.rafturi = date["rafturi"]
        stare.ajutoare = date["ajutoare"]
        stare.experimente = date["experimente"]
        stare.legaturi = {
            (l["de_la"], l["la"]): {k: l[k] for k in ("tarie", "stare", "nascuta_la", "sub_prag")} for l in date["legaturi"]
        }
        return stare

    def salveaza(self, cale: str | Path) -> None:
        fisier = Path(cale)
        fisier.parent.mkdir(parents=True, exist_ok=True)
        date = {
            "versiune": VERSIUNE_STARE,
            "rafturi": self.rafturi,
            "noduri_libere": self.noduri_libere,
            "experimente": self.experimente,
            "ajutoare": self.ajutoare,
            "legaturi": [{"de_la": a, "la": b, **leg} for (a, b), leg in self.legaturi.items()],
        }
        temporar = fisier.with_name(fisier.name + ".part")
        temporar.write_text(json.dumps(date, ensure_ascii=False, indent=2), encoding="utf-8")
        temporar.replace(fisier)

    def noduri(self) -> list[str]:
        """Nodurile active, în ordine: rafturile cu nod, „rar”, apoi ajutoarele alocate."""
        return [*(self.rafturi or []), NOD_RAR, *(a["nume"] for a in self.ajutoare)]

    def libere(self) -> list[str]:
        alocate = {a["nume"] for a in self.ajutoare}
        return [nume for nume in (f"liber{i}" for i in range(1, self.noduri_libere + 1)) if nume not in alocate]

    def raftul(self, nod: str) -> str:
        """Raftul pe care lucrează un nod: al lui, „rar” sau al nodului pe care îl ajută."""
        return next((a["raft"] for a in self.ajutoare if a["nume"] == nod), nod)

    def actualizeaza_alocarile(self, incarcari: dict[str, int], cuvinte_pe_nod: dict[str, Counter[str]]) -> dict[str, Any]:
        """După examen. incarcari = câte cuvinte a primit fiecare nod activ la antrenare.

        1. Ajutoarele al căror raft a primit mai puțin decât media la 3 examene la rând se întorc în rezervă (cu
           legăturile lor); cuvintele lor se întorc la nodul ajutat.
        2. Fiecare nod cu peste 2× media primește un ajutor liber (cât ajung), care preia cam jumătate din cuvintele lui.
        Nodurile alocate nu se mută.
        """
        noduri = self.noduri()
        media = sum(incarcari.get(n, 0) for n in noduri) / len(noduri)
        pe_raft: Counter[str] = Counter()
        for nod in noduri:
            pe_raft[self.raftul(nod)] += incarcari.get(nod, 0)
        for ajutor in self.ajutoare:
            ajutor["sub_medie"] = ajutor["sub_medie"] + 1 if pe_raft[ajutor["raft"]] < media else 0
        eliberate = [a for a in self.ajutoare if a["sub_medie"] >= EXAMENE_SUB_MEDIE]
        for ajutor in eliberate:
            self.ajutoare.remove(ajutor)
            self.legaturi = {pereche: leg for pereche, leg in self.legaturi.items() if ajutor["nume"] not in pereche}
        plecate = {a["nume"] for a in eliberate}
        alocate = []
        libere = self.libere()
        for nod in sorted(noduri, key=lambda n: (-incarcari.get(n, 0), n)):
            cuvinte = cuvinte_pe_nod.get(nod, Counter())
            if not libere:
                break
            if nod in plecate or incarcari.get(nod, 0) <= PRAG_SUPRAINCARCARE * media or len(cuvinte) < 2:
                continue  # sub prag, sau un singur cuvânt: n-are ce împărți
            preluate = _jumatate(cuvinte)
            ajutor = {"nume": libere.pop(0), "ajuta": nod, "raft": self.raftul(nod), "cuvinte": preluate,
                      "alocat_la": self.experimente, "sub_medie": 0}
            self.ajutoare.append(ajutor)
            alocate.append({
                "nod": ajutor["nume"], "ajuta": nod, "raft": ajutor["raft"], "cuvinte_nodului": incarcari.get(nod, 0),
                "preia": round(sum(cuvinte[c] for c in preluate) / sum(cuvinte.values()), 3), "exemple": preluate[:5],
            })
        return {
            "media_cuvinte_pe_nod": round(media, 1),
            "alocate": alocate,
            "eliberate": [{"nod": a["nume"], "raft": a["raft"]} for a in eliberate],
            "ajutoare": [{"nod": a["nume"], "ajuta": a["ajuta"], "raft": a["raft"]} for a in self.ajutoare],
            "libere": len(self.libere()),
        }


# --- rețeaua ---------------------------------------------------------------------------------------


class _NoduriRare(nn.Module):
    """Nodurile mici (aceiași parametri ca în M2), dar fiecare pereche (simbol, nod) trece doar prin nodul ei.

    Perechile stau la coadă pe noduri, ca la ghișee: fiecare nod își calculează doar coada lui, toate deodată pe placa
    video. Ieșirea pornește de la zero („tăcut”), deci la început nodurile nu schimbă nimic.
    """

    def __init__(self, n_noduri: int, n_emb: int, n_ascuns: int) -> None:
        super().__init__()
        limita = n_emb**-0.5  # ca la nn.Linear
        self.ln_pondere = nn.Parameter(torch.ones(n_noduri, n_emb))
        self.ln_deplasare = nn.Parameter(torch.zeros(n_noduri, n_emb))
        self.sus = nn.Parameter(torch.empty(n_noduri, n_emb, n_ascuns).uniform_(-limita, limita))
        self.sus_deplasare = nn.Parameter(torch.empty(n_noduri, n_ascuns).uniform_(-limita, limita))
        self.jos = nn.Parameter(torch.zeros(n_noduri, n_ascuns, n_emb))
        self.jos_deplasare = nn.Parameter(torch.zeros(n_noduri, n_emb))

    def forward(self, x: torch.Tensor, nod: torch.Tensor, loc: torch.Tensor, cap: int) -> torch.Tensor:
        """x: perechi × n_emb (normalizat); nod, loc: nodul perechii și locul ei la coadă; cap: cea mai lungă coadă."""
        coada = x.new_zeros(self.sus.size(0), cap, x.size(-1)).index_put(
            (nod, loc), x * self.ln_pondere[nod] + self.ln_deplasare[nod]
        )
        ascuns = F.gelu(torch.baddbmm(self.sus_deplasare.unsqueeze(1), coada, self.sus))
        return torch.baddbmm(self.jos_deplasare.unsqueeze(1), ascuns, self.jos)[nod, loc]


class _GPTCuNoduriRare(_GPT):
    def __init__(
        self,
        *args: Any,
        n_ascuns_nod: int = 64,
        vecini: list[list[int]] | None = None,
        legaturi: list[list[float]] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        vecini = vecini or [[0]]
        n = len(vecini)
        # Nodurile și centrul se creează DUPĂ trunchi: cu aceeași sămânță, trunchiul pornește ca la GPT-ul simplu.
        self.noduri = _NoduriRare(n, self.emb_token.embedding_dim, n_ascuns_nod)
        self.pondere_centru = nn.Parameter(torch.ones(n))  # nodul central: cât contează fiecare nod
        # vecini[a] = nodurile calculate pentru un simbol al nodului a: el însuși, legăturile și perechile care se pot naște.
        latime = max(len(v) for v in vecini)
        self.register_buffer(
            "vecini", torch.tensor([v + [UMPLUTURA] * (latime - len(v)) for v in vecini], dtype=torch.long)
        )
        self.register_buffer("legaturi", torch.tensor(legaturi or [[0.0] * n for _ in range(n)]))
        self.cerere = nn.Parameter(torch.zeros(n, n))  # cât „cere” un nod de la altul, învățat acum
        self.register_buffer("identitate", torch.eye(n), persistent=False)

    def amestec(self) -> torch.Tensor:
        """Cât ia fiecare nod (rând) de la fiecare nod (coloană): de la el tot; de la vecini, legătura + cererea."""
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
        plan = self._plan(extra[..., -1])  # înainte de trunchi, cât placa video e încă liberă
        h = self.trunchi(idx, memorie)
        if plan is not None:
            simbol, nod_simbol, nod, loc, cap = plan
            plat = h.reshape(-1, h.size(-1))
            iesiri = self.noduri(F.layer_norm(plat[simbol], plat.shape[-1:]), nod, loc, cap)
            ponderi = self.amestec()[nod_simbol, nod] * self.pondere_centru[nod]
            adaos = torch.zeros_like(plat).index_add(0, simbol, (iesiri.float() * ponderi.unsqueeze(-1)).to(plat.dtype))
            h = h + adaos.view_as(h)
        return self.cap(self.ln(h))


# --- modelul ---------------------------------------------------------------------------------------


class ModelPlasaAdaptiva(ModelGPT):
    MANIFEST = {
        "nume": "model_plasa_adaptiva",
        "port": "model",
        "versiune": "0.1.0",
        "versiune_contract": 1,
        "resurse": {"gpu": True, "memorie_gpu_mb": 4000},
        "permisiuni": [],
    }

    def __init__(
        self,
        n_ascuns_nod: int = 64,
        noduri_libere: int = 6,
        cale_plasa: str = "lucru/plasa_adaptiva.json",
        tokenizer: str = "bpe",
        **setari: Any,
    ) -> None:
        super().__init__(tokenizer=tokenizer, **setari)
        if n_ascuns_nod < 1:
            raise ValueError("n_ascuns_nod trebuie să fie pozitiv")
        if noduri_libere < 0:
            raise ValueError("noduri_libere nu poate fi negativ")
        self.n_ascuns_nod = n_ascuns_nod
        self.noduri_libere = noduri_libere
        self.cale_plasa = cale_plasa
        self.stare: StareAdaptiva | None = None
        # Drumul cuvintelor în experimentul curent: fix după antrenare, intră și în modelul salvat.
        self._foloseste_starea(StareAdaptiva(noduri_libere))
        self._vecini: list[list[int]] = [[0]]
        self._legaturi_start: list[list[float]] = [[0.0]]
        # Ce s-a măsurat pe textul de antrenare: pentru plasă și pentru alocări, după examen.
        self._incarcari: list[int] = [0]
        self._cuvinte_pe_nod: list[Counter[str]] = [Counter()]
        self._asociere: list[list[float]] = [[0.0]]
        self._asociere_nastere: list[list[float]] = [[0.0]]
        self._cereri: list[list[float]] | None = None
        self._folosire: list[list[float]] | None = None
        self.simboluri_pe_nod: list[int] = [0]
        self.simboluri_umplutura = 0

    # --- drumul fiecărui cuvânt și simbol ------------------------------------------------------

    def _foloseste_starea(self, stare: StareAdaptiva) -> None:
        """Nodurile active și drumul cuvintelor, din starea păstrată (rafturile, „rar”, apoi ajutoarele)."""
        self.nume_noduri = stare.noduri()
        self._index = {nume: i for i, nume in enumerate(self.nume_noduri)}
        self._rafturi_cu_nod = list(stare.rafturi or [])
        self._ajutor_pentru: dict[tuple[str, str], str] = {}  # (raftul, cuvântul) → ajutorul care îl preia
        for ajutor in stare.ajutoare:  # în ordinea alocării: ajutorul unui ajutor îl înlocuiește pe primul
            for cuvant in ajutor["cuvinte"]:
                self._ajutor_pentru[(ajutor["raft"], cuvant)] = ajutor["nume"]

    def _nod_cuvant(self, raft: str | None, cheie: str) -> int:
        """Indicele nodului unui cuvânt terminat: al raftului lui, „rar” sau ajutorul care l-a preluat (-1 = umplutură)."""
        if raft is None:
            return UMPLUTURA
        baza = raft if raft in self._rafturi_cu_nod else NOD_RAR
        return self._index[self._ajutor_pentru.get((baza, cheie), baza)]

    def _cuvinte(self, text: str) -> tuple[list[int], list[str | None], list[str]]:
        """Cuvintele terminate (din memorie, fără viitor): unde se termină, raftul lor (None = umplutură), cuvântul."""
        memoria = self.sursa_memorie
        rafturi = getattr(memoria, "rafturi", None)
        pozitii: list[int] = []
        raft: list[str | None] = []
        chei: list[str] = []
        if not rafturi or not hasattr(memoria, "cuvinte_cu_coduri"):
            return pozitii, raft, chei  # fără biblioteca de sensuri, totul rămâne pe trunchi
        unice: dict[str, str] = {}
        for pozitie, cuvant, cod, _ in memoria.cuvinte_cu_coduri(text):
            pozitii.append(pozitie)
            raft.append(rafturi[cod[1] - 1] if len(cod) > 1 and 1 <= cod[0] <= 4 else None)
            cheie = _cheie(cuvant)
            chei.append(unice.setdefault(cheie, cheie))
        return pozitii, raft, chei

    def _are_pozitii(self) -> bool:
        return True  # fiecare simbol trebuie să știe la ce nod merge

    def _pozitii(self, text: str, simboluri: list[int] | None, la_antrenare: bool = False) -> torch.Tensor:
        """Pentru fiecare simbol: [categoriile din memorie (dacă memorie=true)..., nodul la care merge (-1 = trunchi)].

        Nodul vine de la ultimul cuvânt terminat până la ultima literă completă a simbolului: nimic din viitor.
        """
        if self.tokenizer == "bpe":
            assert self.tok is not None
            if simboluri is None:
                simboluri = self.tok.codifica(text)
            text, capete = self.tok.capete_caractere(simboluri)
        else:
            capete = list(range(1, len(text) + 1))
        pozitii, rafturi, chei = self._cuvinte(text)
        if la_antrenare:
            self._pregateste(rafturi, chei)
        noduri = torch.full((len(capete),), UMPLUTURA, dtype=torch.long)
        if pozitii:
            noduri_cuvinte = torch.tensor([self._nod_cuvant(r, c) for r, c in zip(rafturi, chei)], dtype=torch.long)
            k = torch.searchsorted(torch.tensor(pozitii), torch.tensor(capete) - 1, right=True) - 1
            noduri = torch.where(k >= 0, noduri_cuvinte[k.clamp_min(0)], noduri)
        if la_antrenare:
            self.simboluri_pe_nod = torch.bincount(noduri[noduri >= 0], minlength=len(self.nume_noduri)).tolist()
            self.simboluri_umplutura = int((noduri < 0).sum())
        if not self.foloseste_memorie:
            return noduri.unsqueeze(-1)
        coduri = self._coduri_memorie(text, simboluri)
        if la_antrenare:
            self._construieste_harta(coduri)
        return torch.cat([self._categorii(coduri), noduri.unsqueeze(-1)], dim=-1)

    def _pregateste(self, rafturi: list[str | None], chei: list[str]) -> None:
        """La antrenare: alege rafturile cu nod (doar la primul experiment), pune drumul cuvintelor, numără ce primește
        fiecare nod, măsoară asocierea dintre noduri și hotărăște ce noduri calculează fiecare simbol."""
        if self.stare is None:
            self.stare = StareAdaptiva(self.noduri_libere)
        stare = self.stare
        if stare.rafturi is None:
            pe_raft = Counter(r for r in rafturi if r is not None)
            total = sum(pe_raft.values())
            stare.rafturi = [r for r, n in pe_raft.most_common() if n / total >= PRAG_RAFT] if total else []
        self._foloseste_starea(stare)
        n = len(self.nume_noduri)
        noduri = [self._nod_cuvant(r, c) for r, c in zip(rafturi, chei)]
        self._incarcari = [0] * n
        self._cuvinte_pe_nod = [Counter() for _ in range(n)]
        for nod, cheie in zip(noduri, chei):
            if nod >= 0:
                self._incarcari[nod] += 1
                self._cuvinte_pe_nod[nod][cheie] += 1
        self._asociere, perechi = _asocierea(noduri, n)
        self._asociere_nastere = [  # doar perechile văzute de destule ori pot naște o legătură
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

    # --- rețeaua și antrenarea -------------------------------------------------------------------

    def _construieste(self) -> None:
        torch.manual_seed(self.samanta)
        categorii = [len(h) + 1 for h in self.harta] if self.foloseste_memorie else None
        self.retea = _GPTCuNoduriRare(
            self._marime_vocabular(), **self.setari, categorii_memorie=categorii, n_emb_memorie=self.n_emb_memorie,
            n_ascuns_nod=self.n_ascuns_nod, vecini=self._vecini, legaturi=self._legaturi_start,
        ).to(self.dispozitiv)

    def _incarca_starea(self) -> None:
        self.stare = StareAdaptiva.incarca(self.cale_plasa, self.noduri_libere)  # din experimentele de dinainte

    def antreneaza(self, date: Any, buget_secunde: float) -> dict[str, Any]:
        self._incarca_starea()
        statistici = super().antreneaza(date, buget_secunde)
        assert self.retea is not None and hasattr(self.retea, "cerere") and self.stare is not None
        nume = self.nume_noduri
        vecini = [set(v) for v in self._vecini]
        # Cererile se învață DOAR pe textul de antrenare; nodurile fără niciun simbol n-au folosit nimic.
        cereri = self.retea.cerere.detach().cpu().tolist()
        amestec = self.retea.amestec().detach().cpu().tolist()
        self._cereri = [[c if b in vecini[a] and a != b else 0.0 for b, c in enumerate(rand)] for a, rand in enumerate(cereri)]
        self._folosire = [
            [abs(p) if b in vecini[a] and a != b and self.simboluri_pe_nod[a] else 0.0 for b, p in enumerate(rand)]
            for a, rand in enumerate(amestec)
        ]
        cuvinte = sum(self._incarcari) or 1
        cu_nod = sum(self.simboluri_pe_nod)
        statistici["noduri"] = {
            "active": len(nume),
            "libere": len(self.stare.libere()),
            "simboluri_pe_trunchi": round(self.simboluri_umplutura / max(1, cu_nod + self.simboluri_umplutura), 4),
            "noduri_calculate_pe_simbol": round(
                sum(s * len(v) for s, v in zip(self.simboluri_pe_nod, self._vecini)) / max(1, cu_nod), 2
            ),
            "cuvinte_pe_nod": {nume[i]: round(c / cuvinte, 4) for i, c in enumerate(self._incarcari)},
            "ajutoare": [{"nod": a["nume"], "ajuta": a["ajuta"], "raft": a["raft"]} for a in self.stare.ajutoare],
        }
        statistici["pondere_centru"] = dict(zip(nume, (round(p, 4) for p in self.retea.pondere_centru.detach().cpu().tolist())))
        statistici["plasa"] = {
            "legaturi_la_start": len(self.stare.legaturi),
            # Legăturile cu care a pornit: tăria lor și cât le-a folosit rețeaua (|ponderea|; 0,1 = folosire deplină).
            "legaturi": [
                {"de_la": a, "la": b, "tarie": leg["tarie"],
                 "folosire": round(self._folosire[self._index[a]][self._index[b]], 4)}
                for (a, b), leg in self.stare.legaturi.items() if a in self._index and b in self._index
            ],
            "perechi_care_se_pot_naste": [
                {"de_la": nume[a], "la": nume[b], "asociere": round(v, 2)}
                for a, rand in enumerate(self._asociere_nastere) for b, v in enumerate(rand) if a != b and v >= PRAG_ASOCIERE
            ],
            "cerere_maxima": round(max((abs(c) for rand in self._cereri for c in rand), default=0.0), 4),
            "cereri_peste_prag": [
                {"de_la": nume[a], "la": nume[b], "cerere": round(c, 4)}
                for a, rand in enumerate(self._cereri) for b, c in enumerate(rand) if abs(c) >= PRAG_CERERE
            ],
        }
        return statistici

    def dupa_examen(self, rezultat: dict[str, Any]) -> dict[str, Any] | None:
        """După examen: legăturile învață din câștig (doar un număr), iar nodurile libere se alocă după cuvintele primite
        la antrenare. Nimic din textul de examen. Starea nouă se păstrează în cale_plasa și intră în jurnal."""
        if self.stare is None or self._cereri is None or self._folosire is None:
            return None
        plasa = Plasa(self.nume_noduri, self.stare.legaturi, self.stare.experimente, prag_asociere=PRAG_ASOCIERE)
        schimbari = plasa.actualizeaza(self._cereri, self._folosire, rezultat.get("castig"), self._asociere_nastere)
        nascute = [{"de_la": a, "la": b} for (a, b), leg in plasa.legaturi.items() if leg["nascuta_la"] == plasa.experimente]
        self.stare.legaturi, self.stare.experimente = plasa.legaturi, plasa.experimente
        alocari = self.stare.actualizeaza_alocarile(
            dict(zip(self.nume_noduri, self._incarcari)), dict(zip(self.nume_noduri, self._cuvinte_pe_nod))
        )
        self.stare.salveaza(self.cale_plasa)
        return {
            "plasa": {**plasa.stare(), **schimbari, "nascute_acum": nascute, "castig_primit": rezultat.get("castig")},
            "noduri": alocari,
        }

    # --- salvare ---------------------------------------------------------------------------------

    def _stare_de_salvat(self) -> dict[str, Any]:
        stare = super()._stare_de_salvat()
        stare["noduri"] = {
            "nume": self.nume_noduri,
            "n_ascuns": self.n_ascuns_nod,
            "rafturi": self._rafturi_cu_nod,
            "ajutor_pentru": [[raft, cuvant, nod] for (raft, cuvant), nod in self._ajutor_pentru.items()],
            "vecini": self._vecini,
            "legaturi": self._legaturi_start,
        }
        return stare

    def _restaureaza(self, salvat: dict[str, Any]) -> None:
        super()._restaureaza(salvat)
        noduri = salvat["noduri"]
        self.n_ascuns_nod = noduri["n_ascuns"]
        self.nume_noduri = noduri["nume"]
        self._index = {nume: i for i, nume in enumerate(self.nume_noduri)}
        self._rafturi_cu_nod = noduri["rafturi"]
        self._ajutor_pentru = {(raft, cuvant): nod for raft, cuvant, nod in noduri["ajutor_pentru"]}
        self._vecini = noduri["vecini"]
        self._legaturi_start = noduri["legaturi"]
