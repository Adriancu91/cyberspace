"""Structurile de date ale analizei unei propoziții: cuvinte cu analize candidate, scoruri explicate, grupuri, dependențe."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..morfologie.analizator import Analiza


@dataclass
class Candidat:
    analiza: Analiza
    scor: float = 0.0
    motive: list[str] = field(default_factory=list)      # explicațiile regulilor care au mărit / micșorat scorul

    def ca_dict(self) -> dict:
        d = self.analiza.ca_dict()
        d["scor"] = round(self.scor, 2)
        d["motive"] = list(self.motive)
        return d


@dataclass
class Cuvant:
    idx: int                                             # 1-based, ca în CoNLL-U
    text: str
    tip: str                                             # tipul tokenului
    candidati: list[Candidat]
    ales: int | None = None                              # indexul candidatului ales (None = ambiguitate nerezolvată)
    ambiguu: bool = False
    cap: int | None = None                               # capul în arborele de dependențe (0 = rădăcină)
    rel: str = ""
    spatiu_dupa: bool = True
    grup: int | None = None                              # indexul grupului nominal din care face parte

    @property
    def a(self) -> Analiza:
        """Analiza aleasă (sau prima, dacă nu s-a putut alege)."""
        return self.candidati[self.ales if self.ales is not None else 0].analiza

    @property
    def pos(self) -> str:
        return self.a.pos

    def tr(self, cheie: str, implicit: str | None = None) -> str | None:
        return self.a.trasaturi.get(cheie, implicit)

    @property
    def necunoscut(self) -> bool:
        return all(c.analiza.incredere in ("necunoscut",) for c in self.candidati)

    def ca_dict(self) -> dict:
        return {"idx": self.idx, "text": self.text, "tip": self.tip, "ales": self.ales, "ambiguu": self.ambiguu, "cap": self.cap, "rel": self.rel,
                "candidati": [c.ca_dict() for c in self.candidati]}


@dataclass
class Grup:
    """Grup nominal: determinanți + numerale + adjective + substantivul-cap (+ genitiv / al-a-ai-ale)."""
    inceput: int
    sfarsit: int                                         # inclusiv, 1-based
    cap: int
    tip: str = "nominal"
    membri: list[int] = field(default_factory=list)

    def ca_dict(self) -> dict:
        return {"inceput": self.inceput, "sfarsit": self.sfarsit, "cap": self.cap, "tip": self.tip, "membri": list(self.membri)}


@dataclass
class Problema:
    tip: str                                             # acord_subst_adj | acord_subiect_predicat | acord_al | numeral_de | necunoscut | ortografie
    pozitii: list[int]
    mesaj: str
    regula: str
    sugestie: str | None = None
    certitudine: str = "probabila"                        # sigura | probabila | posibila

    def ca_dict(self) -> dict:
        return {"tip": self.tip, "pozitii": list(self.pozitii), "mesaj": self.mesaj, "regula": self.regula, "sugestie": self.sugestie, "certitudine": self.certitudine}


@dataclass
class Propozitie:
    text: str
    cuvinte: list[Cuvant]
    grupuri: list[Grup] = field(default_factory=list)
    probleme: list[Problema] = field(default_factory=list)
    analize_alternative: list[dict] = field(default_factory=list)   # alte structuri sintactice posibile (când există)
    note: list[str] = field(default_factory=list)

    def cuvant(self, idx: int) -> Cuvant:
        return self.cuvinte[idx - 1]

    def ca_dict(self) -> dict:
        return {"text": self.text, "cuvinte": [c.ca_dict() for c in self.cuvinte], "grupuri": [g.ca_dict() for g in self.grupuri],
                "probleme": [p.ca_dict() for p in self.probleme], "analize_alternative": list(self.analize_alternative), "note": list(self.note)}
