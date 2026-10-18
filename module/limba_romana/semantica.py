"""Stratul semantic (nivel de bază): sensuri și concepte, relații, roluri semantice din sintaxă, alegerea sensului
din context cu dovezi explicite.

Sursele: RoWordNet 3.0 (concepte cu definiții în română, relații) și Wiktionary (glose în engleză, sinonime).
Infrastructura e completă (tabele, API, traversare, cicluri), dar acoperirea e cea a surselor: cuvintele fără
sens documentat sunt raportate ca atare, nu li se inventează definiții.
"""

from __future__ import annotations

import re
from collections import defaultdict

from .baza import Baza
from .sintaxa.structuri import Cuvant, Propozitie
from .text import normalizeaza

RE_CUV = re.compile(r"[a-zăâîșț]+")
CUVINTE_GOALE = {"de", "la", "cu", "în", "pe", "din", "și", "sau", "care", "ce", "se", "a", "al", "o", "un", "unei", "unui", "este", "fi",
                 "sunt", "era", "nu", "mai", "prin", "pentru", "sa", "lui", "ei", "lor", "că", "să", "ca", "ale", "ai", "unor", "acest", "această"}

ROLURI_PREPOZITII = {
    "cu": ("Instrument/Comitativ", "cu + nume: instrument (dacă e lucru) sau însoțitor (dacă e ființă)"),
    "pentru": ("Beneficiar/Scop", "pentru + nume: beneficiar sau scop"), "la": ("Loc/Țintă", "la + nume: loc sau țintă"),
    "în": ("Loc", "în + nume: loc (sau timp, dacă numele e temporal)"), "pe": ("Loc", "pe + nume: loc (sau complement direct cu „pe”)"),
    "din": ("Sursă/Loc", "din + nume: sursă sau loc de proveniență"), "de la": ("Sursă", "de la + nume: sursă/punct de plecare"),
    "spre": ("Țintă", "spre + nume: direcție"), "către": ("Țintă", "către + nume: direcție/destinatar"), "sub": ("Loc", "sub + nume: loc"),
    "lângă": ("Loc", "lângă + nume: loc"), "despre": ("Temă", "despre + nume: tema comunicării"), "prin": ("Cale/Mijloc", "prin + nume: traseu sau mijloc"),
    "de către": ("Agent", "de către + nume: agentul pasivului"), "fără": ("Absență", "fără + nume: lipsa instrumentului/însoțitorului"),
    "după": ("Timp/Ordine", "după + nume: timp sau ordine"), "înainte de": ("Timp", "înainte de + nume: timp"), "până la": ("Țintă/Timp", "până la + nume: limită"),
}
NUME_TEMPORALE = {"zi", "zile", "an", "ani", "lună", "luni", "oră", "ore", "săptămână", "săptămâni", "seară", "dimineață", "noapte", "secol", "minut", "minute",
                  "azi", "astăzi", "mâine", "ieri", "acum", "atunci", "duminică", "luni", "marți", "miercuri", "joi", "vineri", "sâmbătă", "ianuarie", "februarie",
                  "martie", "aprilie", "mai", "iunie", "iulie", "august", "septembrie", "octombrie", "noiembrie", "decembrie", "vară", "iarnă", "toamnă", "primăvară"}
LITERALE_ANIMATE = {"ființă", "persoană", "om", "animal", "organism", "individ", "vietate", "făptură", "pasăre", "mamifer", "insectă", "pește"}


class Semantica:
    def __init__(self, baza: Baza):
        self.baza = baza
        self._animat: dict[str, bool | None] = {}

    # ---- sensuri și concepte ----------------------------------------------------------------------------------
    def sensuri(self, lexem_id: str) -> list[dict]:
        rez = []
        for s in self.baza.sensuri_lexem(lexem_id):
            d = {"sens_id": s["id"], "concept_id": s["concept_id"], "nr": s["nr"], "sursa": s["sursa_id"], "etichete": s["etichete"],
                 "definitie": s["definitie_concept"] if s["concept_id"] else s["definitie"],
                 "limba_definitiei": "ro" if s["concept_id"] else "en"}
            if s["concept_id"]:
                c = self.baza.concept(s["concept_id"])
                d["sinonime"] = [x["lema"] for x in (c or {}).get("lexeme", []) if x["lexem_id"] != lexem_id]
                d["ili"] = (c or {}).get("ili")
            rez.append(d)
        return rez

    def relatii_concept(self, concept_id: str) -> dict[str, list[dict]]:
        rez: dict[str, list[dict]] = defaultdict(list)
        for r in self.baza.relatii(concept_id):
            c = self.baza.concept(r["celalalt"])
            rez[r["tip"]].append({"concept_id": r["celalalt"], "lexeme": [x["lema"] for x in (c or {}).get("lexeme", [])][:6], "definitie": (c or {}).get("definitie")})
        return dict(rez)

    def lant_hiperonime(self, concept_id: str) -> list[dict]:
        rez = []
        for cid in self.baza.lant(concept_id, "hypernym"):
            c = self.baza.concept(cid)
            rez.append({"concept_id": cid, "lexeme": [x["lema"] for x in (c or {}).get("lexeme", [])][:4]})
        return rez

    def este_animat(self, lexem_id: str) -> bool | None:
        """True/False după lanțurile de hiperonime ale sensurilor RoWordNet; None dacă nu există sensuri RoWN."""
        if lexem_id in self._animat:
            return self._animat[lexem_id]
        rez: bool | None = None
        for s in self.baza.sensuri_lexem(lexem_id):
            if not s["concept_id"]:
                continue
            rez = False if rez is None else rez
            for cid in [s["concept_id"]] + self.baza.lant(s["concept_id"], "hypernym"):
                c = self.baza.concept(cid)
                if c and any(x["lema"] in LITERALE_ANIMATE for x in c["lexeme"]):
                    rez = True
                    break
            if rez:
                break
        self._animat[lexem_id] = rez
        return rez

    # ---- roluri semantice (din dependențe) ----------------------------------------------------------------------
    def roluri(self, prop: Propozitie) -> list[dict]:
        rez = []
        for c in prop.cuvinte:
            if c.cap is None or c.cap == 0 or c.rel not in ("nsubj", "nsubj:pass", "obj", "iobj", "obl", "obl:agent", "obl:tmod") or c.pos not in ("NOUN", "PROPN", "PRON", "NUM"):
                continue
            verb = prop.cuvant(c.cap)
            animat = self.este_animat(c.a.lexem_id) if c.a.lexem_id else None
            if c.pos == "PRON" and c.tr("Person") in ("1", "2"):
                animat = True
            if c.pos == "PROPN" and animat is None:
                animat = None
            rol, motiv = None, ""
            prep = None
            for d in prop.cuvinte:
                if d.cap == c.idx and d.rel == "case":
                    prep = normalizeaza(d.text)
            if c.rel == "nsubj":
                pasiv = any(d.cap == verb.idx and d.rel == "aux:pass" for d in prop.cuvinte)
                if pasiv:
                    rol, motiv = "Pacient", "subiectul unui verb la pasiv"
                elif animat:
                    rol, motiv = "Agent", "subiectul unui verb activ, nume de ființă (RoWordNet)"
                elif animat is False:
                    rol, motiv = "Temă/Cauză", "subiectul unui verb activ, nume de lucru (RoWordNet)"
                else:
                    rol, motiv = "Agent?", "subiect; animat/inanimat nedeterminat (fără sens RoWordNet)"
            elif c.rel == "nsubj:pass":
                rol, motiv = "Pacient", "subiectul pasivului"
            elif c.rel == "obj":
                rol, motiv = "Pacient/Temă", "complement direct"
            elif c.rel == "iobj":
                rol, motiv = "Beneficiar/Destinatar", "complement indirect (dativ)"
            elif c.rel == "obl:agent" or prep == "de către":
                rol, motiv = "Agent", "complement de agent"
            elif c.rel == "obl:tmod" or normalizeaza(c.a.lema) in NUME_TEMPORALE:
                rol, motiv = "Timp", "nume temporal"
            elif prep in ROLURI_PREPOZITII:
                rol, motiv = ROLURI_PREPOZITII[prep]
                if prep == "cu":
                    rol = "Comitativ" if animat else ("Instrument" if animat is False else "Instrument/Comitativ")
                if prep in ("în", "pe", "la") and normalizeaza(c.a.lema) in NUME_TEMPORALE:
                    rol = "Timp"
            else:
                rol, motiv = "Circumstanță", f"complement prepozițional cu „{prep}”" if prep else "complement"
            rez.append({"cuvant": c.idx, "text": c.text, "verb": verb.idx, "verb_text": verb.text, "rol": rol, "motiv": motiv, "animat": animat, "prepozitie": prep})
        return rez

    # ---- alegerea sensului din context (Lesk explicabil) ----------------------------------------------------------
    def sensuri_in_context(self, prop: Propozitie, maxim_per_cuvant: int = 6) -> dict[int, dict]:
        """Pentru fiecare cuvânt cu sensuri în bază: sensurile ordonate după dovezile din propoziție.
        Dovezi: cuvinte din definiția sensului / sinonimele / hiperonimele lui care apar (ca leme) în propoziție."""
        leme_prop: dict[str, int] = {}
        for c in prop.cuvinte:
            if c.pos in ("NOUN", "VERB", "ADJ", "ADV", "PROPN"):
                leme_prop[normalizeaza(c.a.lema)] = c.idx
        rez: dict[int, dict] = {}
        for c in prop.cuvinte:
            if not c.a.lexem_id or c.pos not in ("NOUN", "VERB", "ADJ", "ADV"):
                continue
            sensuri = self.sensuri(c.a.lexem_id)
            if not sensuri:
                continue
            scorate = []
            for s in sensuri[:40]:
                dovezi = []
                text = (s.get("definitie") or "")
                cuvinte_def = {w for w in RE_CUV.findall(normalizeaza(text)) if len(w) > 2 and w not in CUVINTE_GOALE}
                for w in cuvinte_def:
                    if w in leme_prop and leme_prop[w] != c.idx:
                        dovezi.append(f"definiția conține „{w}”")
                for sin in s.get("sinonime", [])[:10]:
                    if normalizeaza(sin) in leme_prop and leme_prop[normalizeaza(sin)] != c.idx:
                        dovezi.append(f"sinonimul „{sin}” e în propoziție")
                if s.get("concept_id"):
                    for h in self.lant_hiperonime(s["concept_id"])[:4]:
                        for l in h["lexeme"]:
                            if normalizeaza(l) in leme_prop and leme_prop[normalizeaza(l)] != c.idx:
                                dovezi.append(f"hiperonimul „{l}” e în propoziție")
                scorate.append((len(dovezi), s, dovezi))
            scorate.sort(key=lambda x: (-x[0], x[1]["sursa"] != "rown", x[1]["nr"]))
            ales = scorate[0] if scorate and scorate[0][0] > 0 else None
            rez[c.idx] = {
                "text": c.text, "lema": c.a.lema, "numar_sensuri": len(sensuri),
                "ales": {"sens_id": ales[1]["sens_id"], "definitie": ales[1]["definitie"], "dovezi": ales[2]} if ales else None,
                "stare": "ales din context" if ales else ("un singur sens" if len(sensuri) == 1 else "nedeterminat (fără dovezi în propoziție)"),
                "candidati": [{"sens_id": s["sens_id"], "sursa": s["sursa"], "definitie": (s["definitie"] or "")[:160], "limba": s["limba_definitiei"],
                               "sinonime": s.get("sinonime", [])[:5], "dovezi": d} for n_, s, d in scorate[:maxim_per_cuvant]],
            }
        return rez
