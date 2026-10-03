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
3. Plasa (setarea plasa = true): legături între noduri, cu tărie între 0 și 1, păstrate între
   experimente în fișierul cale_plasa (implicit lucru/plasa.json). Un nod își ia partea lui de la
   nodurile legate de el: tăria legăturii + cât „cere” în experimentul ăsta (învățat la antrenare).
   Regulile sunt în clasa Plasa de mai jos; plasa învață din câștigul la examen (doar un număr,
   primit prin dupa_examen), niciodată din textul de examen.
Nodurile pornesc „tăcute” (ieșire zero), deci la început modelul e identic cu GPT-ul simplu.

Cere portul „memorie” cu biblioteca de sensuri (MemorieIerarhica). Fără ea, toate simbolurile
merg la nodul de rezervă (statisticile antrenării arată cât a primit fiecare nod).
"""

from __future__ import annotations

import json
from fnmatch import fnmatch
from pathlib import Path
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


# --- regulile plasei -------------------------------------------------------------------------

VERSIUNE_PLASA = 1
TARIE_NASTERE = 0.1  # o legătură nouă începe cu tăria 0,1, „în probă”
PRAG_CERERE = 0.05  # un nod „cere” de la altul când ponderea învățată către el trece de 0,05
PRAG_ACTIVA = 0.2  # o legătură iese din probă când trece de 0,2
PRAG_DEFINITIVA = 0.9  # peste 0,9 devine definitivă: nu mai uită și nu mai e tăiată
PRAG_TAIERE = 0.05  # sub 0,05 e tăiată
UITARE = 0.01  # la fiecare experiment, fiecare legătură (nedefinitivă) uită 1% din tărie
PAS_INTARIRE = 0.2  # cât se poate întări sau slăbi o legătură într-un experiment
SCALA_CASTIG = 0.01  # un câștig la examen de 0,01 (val_bpb) e un semnal întreg
FOLOSIRE_PLINA = 0.1  # o pondere de 0,1 între două noduri = folosire deplină


def _intre(x: float, jos: float, sus: float) -> float:
    return max(jos, min(sus, x))


class Plasa:
    """Legăturile dintre noduri (tărie între 0 și 1), păstrate între experimente într-un fișier JSON.

    Reguli: o legătură se naște când un nod cere de la altul (tărie 0,1, în probă); se întărește sau
    slăbește după câștigul la examen, înmulțit cu cât a fost folosită (folosirea singură nu ajunge);
    uită 1% la fiecare experiment; peste 0,9 devine definitivă; sub 0,05 e tăiată. Legăturile
    fiecărui nod cu nodul central sunt fixe, deci nu stau aici.
    """

    def __init__(self, noduri: list[str], legaturi: dict[tuple[str, str], dict[str, Any]] | None = None,
                 experimente: int = 0) -> None:
        self.noduri = list(noduri)
        self.legaturi: dict[tuple[str, str], dict[str, Any]] = legaturi or {}
        self.experimente = experimente

    @classmethod
    def incarca(cls, cale: str | Path, noduri: list[str]) -> Plasa:
        fisier = Path(cale)
        if not fisier.exists():
            return cls(noduri)  # o plasă nouă, fără legături
        date = json.loads(fisier.read_text(encoding="utf-8"))
        if date.get("versiune") != VERSIUNE_PLASA or date.get("noduri") != list(noduri):
            raise ValueError(f"Plasa din „{cale}” e pentru alte noduri ({date.get('noduri')}); folosește alt cale_plasa.")
        legaturi = {
            (l["de_la"], l["la"]): {"tarie": l["tarie"], "stare": l["stare"], "nascuta_la": l.get("nascuta_la")}
            for l in date["legaturi"]
        }
        return cls(noduri, legaturi, date.get("experimente", 0))

    def matrice(self) -> list[list[float]]:
        """Tăria legăturii de la fiecare nod (rând) la fiecare nod (coloană); 0 = fără legătură."""
        poz = {nume: i for i, nume in enumerate(self.noduri)}
        m = [[0.0] * len(self.noduri) for _ in self.noduri]
        for (a, b), leg in self.legaturi.items():
            m[poz[a]][poz[b]] = leg["tarie"]
        return m

    def actualizeaza(self, cereri: list[list[float]], folosire: list[list[float]], castig: float | None) -> dict[str, int]:
        """Un experiment s-a încheiat: nașteri, întărire după câștigul la examen, uitare, definitive, tăieri."""
        numar = {"nascute": 0, "intarite": 0, "slabite": 0, "taiate": 0, "devenite_definitive": 0}
        self.experimente += 1
        for a, de_la in enumerate(self.noduri):  # 1. nașteri: un nod a cerut de la altul cu care nu era legat
            for b, la in enumerate(self.noduri):
                if a != b and abs(cereri[a][b]) >= PRAG_CERERE and (de_la, la) not in self.legaturi:
                    self.legaturi[(de_la, la)] = {"tarie": TARIE_NASTERE, "stare": "proba", "nascuta_la": self.experimente}
                    numar["nascute"] += 1
        poz = {nume: i for i, nume in enumerate(self.noduri)}
        semnal = 0.0 if castig is None else _intre(castig / SCALA_CASTIG, -1.0, 1.0)
        for (de_la, la), leg in list(self.legaturi.items()):
            if leg["stare"] == "definitiva":
                continue
            # 2. întărire: câștigul la examen × cât a fost folosită legătura (folosirea singură nu ajunge)
            schimbare = PAS_INTARIRE * semnal * min(1.0, abs(folosire[poz[de_la]][poz[la]]) / FOLOSIRE_PLINA)
            if schimbare > 0:
                numar["intarite"] += 1
            elif schimbare < 0:
                numar["slabite"] += 1
            # 3. uitare 1%, apoi starea: definitivă peste 0,9, tăiată sub 0,05, activă peste 0,2
            leg["tarie"] = round(_intre(leg["tarie"] + schimbare, 0.0, 1.0) * (1 - UITARE), 6)
            if leg["tarie"] > PRAG_DEFINITIVA:
                leg["stare"] = "definitiva"
                numar["devenite_definitive"] += 1
            elif leg["tarie"] < PRAG_TAIERE:
                del self.legaturi[(de_la, la)]
                numar["taiate"] += 1
            elif leg["tarie"] >= PRAG_ACTIVA:
                leg["stare"] = "activa"
        return numar

    def stare(self) -> dict[str, Any]:
        stari = [leg["stare"] for leg in self.legaturi.values()]
        return {
            "experimente": self.experimente,
            "legaturi": len(self.legaturi),
            "in_proba": stari.count("proba"),
            "active": stari.count("activa"),
            "definitive": stari.count("definitiva"),
            "lista": [
                {"de_la": a, "la": b, "tarie": leg["tarie"], "stare": leg["stare"]}
                for (a, b), leg in sorted(self.legaturi.items(), key=lambda x: -x[1]["tarie"])
            ],
        }

    def salveaza(self, cale: str | Path) -> None:
        fisier = Path(cale)
        fisier.parent.mkdir(parents=True, exist_ok=True)
        date = {
            "versiune": VERSIUNE_PLASA,
            "noduri": self.noduri,
            "legaturi_cu_centrul": "fixe (nu se schimbă, nu stau aici)",
            "experimente": self.experimente,
            "legaturi": [
                {"de_la": a, "la": b, "tarie": leg["tarie"], "stare": leg["stare"], "nascuta_la": leg.get("nascuta_la")}
                for (a, b), leg in self.legaturi.items()
            ],
        }
        temporar = fisier.with_name(fisier.name + ".part")
        temporar.write_text(json.dumps(date, ensure_ascii=False, indent=2), encoding="utf-8")
        temporar.replace(fisier)


class _Noduri(nn.Module):
    """Nodurile mici, calculate toate deodată (pe placa video, mult mai repede decât unul câte unul).

    Fiecare nod: normalizare (cu parametrii lui) → strat ascuns → GELU → înapoi la n_emb. Ieșirea
    pornește de la zero („tăcut”), deci la început nodurile nu schimbă nimic.
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

    def forward(self, h: torch.Tensor) -> torch.Tensor:
        """h: lot × poziții × n_emb → lot × poziții × noduri × n_emb."""
        x = F.layer_norm(h, h.shape[-1:]).unsqueeze(-2) * self.ln_pondere + self.ln_deplasare
        ascuns = F.gelu(torch.einsum("lpne,neh->lpnh", x, self.sus) + self.sus_deplasare)
        return torch.einsum("lpnh,nhe->lpne", ascuns, self.jos) + self.jos_deplasare


class _GPTCuNoduri(_GPT):
    def __init__(
        self,
        *args: Any,
        n_noduri: int = len(GRUPURI),
        n_ascuns_nod: int = 64,
        cu_plasa: bool = False,
        legaturi: list[list[float]] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        n_emb = self.emb_token.embedding_dim
        # Nodurile și centrul se creează DUPĂ trunchi: cu aceeași sămânță, trunchiul pornește ca la GPT-ul simplu.
        self.noduri = _Noduri(n_noduri, n_emb, n_ascuns_nod)
        self.pondere_centru = nn.Parameter(torch.ones(n_noduri))  # nodul central: cât contează fiecare nod
        self.register_buffer("identitate", torch.eye(n_noduri), persistent=False)
        self.cu_plasa = cu_plasa
        if cu_plasa:
            # Legăturile din plasă (fixe în timpul experimentului) și cererile învățate acum (pornesc de la 0).
            self.register_buffer("legaturi", torch.tensor(legaturi or [[0.0] * n_noduri] * n_noduri))
            self.cerere = nn.Parameter(torch.zeros(n_noduri, n_noduri))

    def amestec(self) -> torch.Tensor:
        """Cât ia fiecare nod (rând) de la fiecare nod (coloană): de la el însuși tot; de la celelalte,
        tăria legăturii + cât cere acum (doar cu plasă)."""
        if not self.cu_plasa:
            return self.identitate
        return self.identitate + (self.legaturi + self.cerere) * (1 - self.identitate)

    def forward(self, idx: torch.Tensor, extra: torch.Tensor | None = None) -> torch.Tensor:
        if extra is None:
            raise ValueError("modelul cu noduri trebuie să știe, pentru fiecare simbol, la ce nod merge")
        memorie = extra[..., :-1] if self.memorie is not None else None
        noduri = extra[..., -1]
        h = self.trunchi(idx, memorie)
        iesiri = self.noduri(h)  # lot × poziții × noduri × n_emb
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

    def __init__(
        self,
        n_ascuns_nod: int = 64,
        plasa: bool = False,
        cale_plasa: str = "lucru/plasa.json",
        tokenizer: str = "bpe",
        **setari: Any,
    ) -> None:
        super().__init__(tokenizer=tokenizer, **setari)
        if n_ascuns_nod < 1:
            raise ValueError("n_ascuns_nod trebuie să fie pozitiv")
        self.n_ascuns_nod = n_ascuns_nod
        self.cu_plasa = bool(plasa)
        self.cale_plasa = cale_plasa
        self.plasa: Plasa | None = None
        self._legaturi_start: list[list[float]] | None = None  # plasa cu care s-a antrenat modelul
        self._cereri: list[list[float]] | None = None  # cât a cerut fiecare nod de la celelalte (la antrenare)
        self._folosire: list[list[float]] | None = None
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
            n_noduri=len(GRUPURI), n_ascuns_nod=self.n_ascuns_nod, cu_plasa=self.cu_plasa, legaturi=self._legaturi_start,
        ).to(self.dispozitiv)

    def antreneaza(self, date: Any, buget_secunde: float) -> dict[str, Any]:
        if self.cu_plasa:  # plasa vine din experimentele de dinainte (sau e nouă, fără legături)
            self.plasa = Plasa.incarca(self.cale_plasa, NUME_NODURI)
            self._legaturi_start = self.plasa.matrice()
        statistici = super().antreneaza(date, buget_secunde)
        assert isinstance(self.retea, _GPTCuNoduri)
        total = sum(self.simboluri_pe_nod) or 1
        statistici["noduri"] = {nume: round(n / total, 4) for nume, n in zip(NUME_NODURI, self.simboluri_pe_nod)}
        statistici["pondere_centru"] = dict(
            zip(NUME_NODURI, (round(p, 4) for p in self.retea.pondere_centru.detach().cpu().tolist()))
        )
        if self.cu_plasa and self.plasa is not None:
            # Cererile se învață DOAR pe textul de antrenare; nodurile fără niciun simbol n-au folosit nimic.
            cereri = self.retea.cerere.detach().cpu().tolist()
            amestec = self.retea.amestec().detach().cpu().tolist()
            self._cereri = [[0.0 if a == b else c for b, c in enumerate(rand)] for a, rand in enumerate(cereri)]
            self._folosire = [
                [0.0 if a == b or self.simboluri_pe_nod[a] == 0 else abs(p) for b, p in enumerate(rand)]
                for a, rand in enumerate(amestec)
            ]
            statistici["plasa"] = {
                "legaturi_la_start": len(self.plasa.legaturi),
                "cerere_maxima": round(max(abs(c) for rand in self._cereri for c in rand), 4),
                "cereri": {
                    NUME_NODURI[a]: {NUME_NODURI[b]: round(c, 4) for b, c in enumerate(rand) if a != b}
                    for a, rand in enumerate(self._cereri)
                },
                "cereri_peste_prag": [
                    {"de_la": NUME_NODURI[a], "la": NUME_NODURI[b], "cerere": round(c, 4)}
                    for a, rand in enumerate(self._cereri) for b, c in enumerate(rand) if abs(c) >= PRAG_CERERE
                ],
            }
        return statistici

    def dupa_examen(self, rezultat: dict[str, Any]) -> dict[str, Any] | None:
        """După examen: plasa învață din câștig (un număr), niciodată din textul de examen, și se păstrează."""
        if not self.cu_plasa or self.plasa is None or self._cereri is None or self._folosire is None:
            return None
        schimbari = self.plasa.actualizeaza(self._cereri, self._folosire, rezultat.get("castig"))
        self.plasa.salveaza(self.cale_plasa)
        return {"plasa": {**self.plasa.stare(), **schimbari, "castig_primit": rezultat.get("castig")}}

    def _stare_de_salvat(self) -> dict[str, Any]:
        stare = super()._stare_de_salvat()
        stare["noduri"] = {"nume": NUME_NODURI, "n_ascuns": self.n_ascuns_nod, "cu_plasa": self.cu_plasa}
        return stare

    def _restaureaza(self, salvat: dict[str, Any]) -> None:
        super()._restaureaza(salvat)
        self.n_ascuns_nod = salvat["noduri"]["n_ascuns"]
        self.cu_plasa = salvat["noduri"].get("cu_plasa", False)
        self._legaturi_start = None  # legăturile vin din fișierul modelului (în starea rețelei)
