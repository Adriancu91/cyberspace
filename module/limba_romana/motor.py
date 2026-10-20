"""API-ul public al motorului lingvistic: clasa `Motor`.

Toate funcțiile întorc dicționare/liste simple (serializabile JSON), ca să poată fi folosite din orice alt modul
(Kronos sau altceva) fără dependențe; motorul nu importă nimic din `kronos/`.

Operațiile (versiunea API 1):
    cauta_forma(forma)                   → toate analizele cunoscute ale unei forme
    cauta_lema(lema, pos=None)           → lexemele cu această lemă
    forme_lema(lema, pos=None)           → formele cunoscute ale unui lexem, cu trăsături și statut
    analiza_morfologica(cuvant)          → analize candidate (inclusiv ipoteze pentru necunoscute)
    analizeaza(text, context=None)       → analiza completă a unui text (propoziții, cuvinte, grupuri, dependențe,
                                           sensuri, roluri, probleme, ambiguități, necunoscute, proveniență, versiune)
    verifica_text(text)                  → doar problemele: greșeli de acord, numerale, cuvinte necunoscute, diacritice
    sensuri(lema, pos=None)              → sensurile și conceptele unui cuvânt
    relatii(concept_id)                  → relațiile semantice ale unui concept; lant_hiperonime(concept_id)
    verifica_acord(text)                 → problemele de acord ale textului
    explica(text, pozitie)               → de ce a ales motorul o analiză pentru cuvântul de la poziție (și de ce nu altele)
    necunoscute(text)                    → cuvintele necunoscute / cunoscute doar ortografic
    reguli(tip=None)                     → regulile explicite înregistrate
    statistici(), integritate(), exporta(director), importa(director), acoperire()
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import VERSIUNE
from .baza import CALE_IMPLICITA, Baza
from .morfologie.analizator import Analizator
from .semantica import Semantica
from .sintaxa.analiza import analizeaza_propozitie
from .text import segmenteaza_propozitii

VERSIUNE_API = 1


class Motor:
    def __init__(self, cale_baza: str | Path | None = None):
        self.cale = Path(cale_baza) if cale_baza else CALE_IMPLICITA
        if not self.cale.exists():
            raise FileNotFoundError(f"Baza lingvistică lipsește: {self.cale}. Rulați întâi: python -m module.limba_romana.importatoare.descarca_surse "
                                    f"și python -m module.limba_romana.importatoare.construieste_baza")
        self.baza = Baza(self.cale, doar_citire=True)
        self.analizator = Analizator(self.baza)
        self.semantica = Semantica(self.baza)

    def inchide(self) -> None:
        self.baza.inchide()

    # ---- lexicon ---------------------------------------------------------------------------------------------------
    def cauta_forma(self, forma: str) -> list[dict]:
        return self.baza.cauta_forma(forma)

    def cauta_lema(self, lema: str, pos: str | None = None) -> list[dict]:
        return self.baza.cauta_lema(lema, pos)

    def forme_lema(self, lema: str, pos: str | None = None) -> list[dict]:
        rez = []
        for lx in self.baza.cauta_lema(lema, pos):
            rez.append({"lexem": lx, "forme": self.baza.forme_lexem(lx["id"])})
        return rez

    def analiza_morfologica(self, cuvant: str) -> list[dict]:
        return [a.ca_dict() for a in self.analizator.analizeaza(cuvant)]

    # ---- analiză ----------------------------------------------------------------------------------------------------
    def analizeaza(self, text: str, context: dict | None = None, cu_sensuri: bool = True, cu_dependente: bool = True) -> dict:
        propozitii = []
        for inceput, sfarsit, bucata in segmenteaza_propozitii(text):
            prop = analizeaza_propozitie(self.baza, self.analizator, bucata, cu_dependente=cu_dependente)
            d = prop.ca_dict()
            d["inceput"], d["sfarsit"] = inceput, sfarsit
            if cu_sensuri:
                d["sensuri"] = self.semantica.sensuri_in_context(prop)
                d["roluri"] = self.semantica.roluri(prop) if cu_dependente else []
            d["ambiguitati"] = [{"cuvant": c.idx, "text": c.text, "variante": [(x.analiza.lema, x.analiza.pos, round(x.scor, 2)) for x in c.candidati[:4]]}
                                for c in prop.cuvinte if c.ambiguu]
            d["necunoscute"] = [{"cuvant": c.idx, "text": c.text, "stare": "necunoscut" if c.necunoscut else "ipoteză", "detalii": c.a.dovezi}
                                for c in prop.cuvinte if c.necunoscut or all(x.analiza.incredere in ("ipoteza", "necunoscut") for x in c.candidati)]
            propozitii.append(d)
        return {"text": text, "versiune_motor": VERSIUNE, "versiune_api": VERSIUNE_API, "baza": {"cale": str(self.cale), "surse": [s["id"] for s in self.baza.surse()]},
                "context": context or {}, "propozitii": propozitii,
                "probleme": [p for d in propozitii for p in d["probleme"]]}

    def verifica_text(self, text: str) -> dict:
        """Interfața simplă pentru alte module: problemele textului (acord, numerale, necunoscute, diacritice)."""
        rez = self.analizeaza(text, cu_sensuri=False, cu_dependente=False)
        probleme = []
        for d in rez["propozitii"]:
            for p in d["probleme"]:
                cuvinte = [d["cuvinte"][i - 1]["text"] for i in p["pozitii"] if 0 < i <= len(d["cuvinte"])]
                probleme.append({**p, "propozitie": d["text"], "cuvinte": cuvinte})
        return {"text": text, "versiune_motor": VERSIUNE, "numar_probleme": len(probleme), "probleme": probleme,
                "necunoscute": [n for d in rez["propozitii"] for n in d["necunoscute"]],
                "ambiguitati": [a for d in rez["propozitii"] for a in d["ambiguitati"]]}

    def verifica_acord(self, text: str) -> list[dict]:
        return [p for p in self.verifica_text(text)["probleme"] if p["tip"].startswith("acord") or p["tip"] in ("numeral_de", "regim_prepozitie")]

    def necunoscute(self, text: str) -> list[dict]:
        return self.verifica_text(text)["necunoscute"]

    def explica(self, text: str, pozitie: int) -> dict:
        """Explicația alegerii pentru cuvântul `pozitie` (1-based) din prima propoziție a textului."""
        prop = analizeaza_propozitie(self.baza, self.analizator, text, cu_dependente=True)
        if not 1 <= pozitie <= len(prop.cuvinte):
            return {"eroare": "poziție în afara propoziției"}
        c = prop.cuvant(pozitie)
        return {"cuvant": c.text, "ales": c.candidati[c.ales].ca_dict() if c.ales is not None else None, "ambiguu": c.ambiguu,
                "respinse": [x.ca_dict() for x in c.candidati[1:6]], "cap": c.cap, "relatie": c.rel,
                "nota": "scorurile sunt dovezi euristice însumate, nu probabilități calibrate"}

    # ---- semantică ------------------------------------------------------------------------------------------------
    def sensuri(self, lema: str, pos: str | None = None) -> list[dict]:
        rez = []
        for lx in self.baza.cauta_lema(lema, pos):
            rez.append({"lexem": {k: lx[k] for k in ("id", "lema", "pos", "omonim", "gen")}, "sensuri": self.semantica.sensuri(lx["id"])})
        return rez

    def relatii(self, concept_id: str) -> dict:
        return self.semantica.relatii_concept(concept_id)

    def lant_hiperonime(self, concept_id: str) -> list[dict]:
        return self.semantica.lant_hiperonime(concept_id)

    def concept(self, concept_id: str) -> dict | None:
        return self.baza.concept(concept_id)

    # ---- reguli, bază, rapoarte ---------------------------------------------------------------------------------------
    def reguli(self, tip: str | None = None) -> list[dict]:
        return self.baza.reguli(tip)

    def exemple(self, lema: str | None = None, forma: str | None = None, limita: int = 10) -> list[dict]:
        return self.baza.exemple_cu(lema=lema, forma=forma, limita=limita)

    def statistici(self) -> dict:
        return self.baza.statistici()

    def integritate(self) -> dict:
        return self.baza.verifica_integritate()

    def exporta(self, director: str | Path, doar_sursa: str | None = None) -> dict:
        return self.baza.exporta(director, doar_sursa)

    def acoperire(self) -> dict:
        from .acoperire import raport_acoperire
        return raport_acoperire(self.baza)

    def surse(self) -> list[dict]:
        return self.baza.surse()


def analizeaza_json(text: str, cale_baza: str | None = None) -> str:
    m = Motor(cale_baza)
    try:
        return json.dumps(m.analizeaza(text), ensure_ascii=False, indent=1)
    finally:
        m.inchide()
