"""EVALUEAZĂ (etapa 2): starea organismului, din ce s-a observat (secțiunea 4.2 din plan).

- **Capacitățile** (din [capacitati]):
  - linia de bază: cea mai bună valoare dintre experimentele PĂSTRATE de Kronos pe liniile urmărite;
  - scorul curent: valoarea pe ultimul model păstrat;
  - procentul din maxim;
  - dacă e degradată (sub linia de bază cu mai mult decât pragul ei de zgomot);
  - dacă e disponibilă (modulele de care depinde se încarcă).
- **Ultimul model păstrat** (cu model salvat) și **tendința** pe ultima linie: cât s-a îmbunătățit capacitatea
  nevoii „continua” (val_bpb) între ultimele două ore.
- **Configurările Kronos**: câte ore are fiecare linie din câte are planificate.
- **Hrana**: câtă e și dacă a fost deja folosită. E folosită dacă o linie care pomenește dosarul ei a rulat după
  ultima schimbare a hranei.
- **Nivelul** permis de guvernator, cu motivul.

O valoare vine, în ordine:
1. din scorurile fișei (examenul oficial);
2. din fișa unei unelte de examen care pomenește experimentul (ex. unelte/examen_profesor.py): e mai nouă decât ora
   lui și poate fi mai precisă (ex. nota pe 40 de povești, nu pe 20);
3. din criteriile fișei (examene_suplimentare, date la sfârșitul orei).
"""

from __future__ import annotations

import fnmatch
import math
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from module.continuum import guvernator
from module.continuum.observa import ARHITECTURA

REUSITE = ("pastrat", "respins")  # ca la unelte/antrenare_lunga.py: o oră făcută = un experiment reușit


def numar(valoare: Any) -> bool:
    return isinstance(valoare, (int, float)) and not isinstance(valoare, bool) and math.isfinite(valoare)


def criterii_din(fisa: dict[str, Any]) -> dict[str, Any]:
    """Criteriile unei ore (examene_suplimentare): cu [criterii] în fișă; fără, în răspunsul dupa_examen."""
    return fisa.get("criterii") or (fisa.get("dupa_examen") or {}).get("criterii") or {}


def masuratori_unelte(fise: list[dict[str, Any]], config: dict[str, Any]) -> dict[tuple[str, int], dict[str, Any]]:
    """(linia uneltei, experimentul) → scorurile ultimei ei fișe pentru acel experiment."""
    linii = {cap["unealta"]["linie"] for cap in config["capacitati"].values() if cap["unealta"]}
    rezultat: dict[tuple[str, int], dict[str, Any]] = {}
    for fisa in sorted((f for f in fise if f.get("linie") in linii), key=lambda f: f.get("id", 0)):
        experiment = ((fisa.get("module") or {}).get("elev") or {}).get("experiment")
        if isinstance(experiment, int):  # o fișă mai nouă înlocuiește scorurile pe care le are și le păstrează pe rest
            rezultat.setdefault((fisa["linie"], experiment), {}).update(fisa.get("scoruri") or {})
    return rezultat


def valoare(fisa: dict[str, Any], cap: dict[str, Any], unelte: dict[tuple[str, int], dict[str, Any]]) -> float | None:
    """Valoarea capacității pe modelul unei fișe, sau None dacă n-a fost măsurată."""
    oficial = (fisa.get("scoruri") or {}).get(cap["metrica"])
    if numar(oficial):
        return float(oficial)
    if cap["unealta"]:  # măsurarea cu unealta vine după oră: cea mai nouă
        scor = unelte.get((cap["unealta"]["linie"], fisa.get("id")), {}).get(cap["unealta"]["scor"])
        if numar(scor):
            return float(scor)
    criteriu = criterii_din(fisa).get(cap["metrica"])
    return float(criteriu) if numar(criteriu) else None


@dataclass
class Capacitate:
    nume: str
    metrica: str
    mai_mare_e_mai_bine: bool
    prag_zgomot: float
    maxim: float | None
    disponibila: bool
    motiv_indisponibila: str | None
    linie_de_baza: float | None = None
    experiment_baza: int | None = None
    curent: float | None = None   # pe ultimul model păstrat
    procent: float | None = None  # curent, din maxim
    degradata: bool = False

    def castig(self, nou: float, vechi: float) -> float:
        """Cât e nou mai bun decât vechi, în direcția capacității (negativ = mai rău)."""
        return nou - vechi if self.mai_mare_e_mai_bine else vechi - nou


@dataclass
class StareaOrganismului:
    timp: str
    nivel: str
    motiv_nivel: str
    ultimul_id: int                        # ultimul număr de fișă din jurnalul Kronos: fișele noi au numere mai mari
    ultimul_model: dict[str, Any] | None   # {"experiment", "linie", "arhitectura"}
    modele: list[dict[str, Any]] = field(default_factory=list)  # toate modelele păstrate, de la cel mai vechi
    capacitati: dict[str, Capacitate] = field(default_factory=dict)
    tendinta: dict[str, Any] | None = None
    linii: dict[str, dict[str, Any]] = field(default_factory=dict)  # configurare → linia ei, ore făcute / planificate
    hrana: dict[str, dict[str, Any]] = field(default_factory=dict)
    module: dict[str, dict[str, Any]] = field(default_factory=dict)

    def rezumat(self) -> dict[str, Any]:
        """Ce intră în jurnalul ciclurilor."""
        return {
            "nivel": self.nivel, "de_ce_nivelul": self.motiv_nivel, "ultimul_id": self.ultimul_id,
            "ultimul_model": self.ultimul_model,
            "capacitati": {n: {k: v for k, v in asdict(c).items() if k not in ("nume", "metrica", "mai_mare_e_mai_bine")}
                           for n, c in self.capacitati.items()},
            "tendinta": self.tendinta, "hrana": self.hrana,
            "linii": {cale: {k: v for k, v in l.items() if k != "texte"} for cale, l in self.linii.items()},
        }


def se_potriveste(cale: str, globuri: list[str]) -> bool:
    return any(fnmatch.fnmatchcase(cale, Path(g).as_posix()) for g in globuri)


def _dupa(inceput: Any, moment: datetime) -> bool:
    """Ora din fișă (ISO) e după momentul dat?"""
    try:
        cand = datetime.fromisoformat(str(inceput))
    except ValueError:
        return False
    if cand.tzinfo is None:
        cand = cand.replace(tzinfo=timezone.utc)
    return cand > moment


def pomeneste(linie: dict[str, Any], dosar: str) -> bool:
    """Configurarea liniei folosește dosarul (un text din setările porturilor e dosarul sau ceva din el)?"""
    return any(t == dosar or t.startswith(dosar.rstrip("/") + "/") for t in linie.get("texte", []))


def _model(fisa: dict[str, Any]) -> dict[str, Any]:
    setari = (fisa.get("setari") or {}).get("model") or {}
    return {"experiment": fisa["id"], "linie": fisa["linie"], "arhitectura": {k: setari.get(k) for k in ARHITECTURA}}


def _indisponibila(cap: dict[str, Any], module: dict[str, dict[str, Any]]) -> str | None:
    for nume in cap["module"]:
        info = module.get(nume)
        if info is None:
            return f"modulul „{nume}” nu e în [module]"
        if info.get("stare") not in ("ok", "degradat"):
            return f"modulul „{nume}” e {info.get('stare')}" + (f" ({info['eroare']})" if info.get("eroare") else "")
    return None


def evalueaza(observat: Any, config: dict[str, Any]) -> StareaOrganismului:
    nivel, motiv_nivel = guvernator.nivel(observat, config)
    fise = observat.fise
    linii: dict[str, dict[str, Any]] = {}
    for cale, c in observat.configurari.items():
        if c.get("stare") != "ok":
            linii[cale] = dict(c)
            continue
        facute = sum(1 for f in fise if f.get("linie") == c["linie"] and f.get("decizie") in REUSITE)
        linii[cale] = {**c, "ore_facute": facute, "terminata": facute >= c["ore_planificate"],
                       "urmarita": se_potriveste(cale, config["linii"]["configurari"])}
    urmarite = {l["linie"] for l in linii.values() if l.get("stare") == "ok" and l["urmarita"]}
    reusite = sorted((f for f in fise if f.get("linie") in urmarite and f.get("decizie") in REUSITE),
                     key=lambda f: f.get("id", 0))
    pastrate = [f for f in reusite if f.get("decizie") == "pastrat"]
    unelte = masuratori_unelte(fise, config)
    cu_model = [f for f in pastrate if f.get("model_salvat")]
    ultimul = cu_model[-1] if cu_model else None
    stare = StareaOrganismului(
        timp=observat.timp.isoformat(timespec="seconds"), nivel=nivel, motiv_nivel=motiv_nivel,
        ultimul_id=max((f.get("id", 0) for f in fise), default=0),
        ultimul_model=_model(ultimul) if ultimul else None, modele=[_model(f) for f in cu_model],
        linii=linii, module=observat.module,
    )

    for nume, cap in config["capacitati"].items():
        motiv = _indisponibila(cap, observat.module)
        c = Capacitate(nume, cap["metrica"], cap["mai_mare_e_mai_bine"], cap["prag_zgomot"], cap["maxim"],
                       disponibila=motiv is None, motiv_indisponibila=motiv)
        valori = [(f["id"], v) for f in pastrate if (v := valoare(f, cap, unelte)) is not None]
        if valori:
            c.experiment_baza, c.linie_de_baza = (max if c.mai_mare_e_mai_bine else min)(valori, key=lambda p: p[1])
        c.curent = valoare(ultimul, cap, unelte) if ultimul else None
        if c.curent is not None and c.maxim:
            c.procent = round(100 * c.curent / c.maxim, 1)
        if c.curent is not None and c.linie_de_baza is not None:
            c.degradata = c.castig(c.curent, c.linie_de_baza) < -c.prag_zgomot
        stare.capacitati[nume] = c

    continua = config["nevoi"].get("continua")
    if continua and continua["capacitate"] in stare.capacitati and reusite:
        cap = config["capacitati"][continua["capacitate"]]
        linie = reusite[-1]["linie"]
        puncte = [(f["id"], v) for f in reusite if f["linie"] == linie and (v := valoare(f, cap, unelte)) is not None]
        if puncte:
            c = stare.capacitati[continua["capacitate"]]
            stare.tendinta = {"linie": linie, "capacitate": c.nume,
                              "la": {"experiment": puncte[-1][0], "valoare": puncte[-1][1]}, "castig": None}
            if len(puncte) >= 2:
                stare.tendinta["de_la"] = {"experiment": puncte[-2][0], "valoare": puncte[-2][1]}
                stare.tendinta["castig"] = c.castig(puncte[-1][1], puncte[-2][1])

    for capacitate, h in observat.hrana.items():
        minima = config["hrana"][capacitate]["minima_povesti"]
        if h.get("stare") != "ok":
            stare.hrana[capacitate] = {**h, "nefolosita": False, "destula": False, "minima": minima}
            continue
        schimbata = datetime.fromisoformat(h["schimbata"])
        folosita_de = sorted({l["linie"] for l in linii.values() if l.get("stare") == "ok" and pomeneste(l, h["dosar"])
                              and any(f.get("linie") == l["linie"] and f.get("decizie") in REUSITE
                                      and _dupa(f.get("inceput"), schimbata) for f in fise)})
        stare.hrana[capacitate] = {**h, "folosita_de": folosita_de, "nefolosita": not folosita_de,
                                   "destula": h["povesti"] >= minima, "minima": minima}
    return stare
