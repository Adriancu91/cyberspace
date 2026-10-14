"""EVALUEAZĂ (etapa 2): starea organismului, din ce s-a observat (secțiunea 4.2 din plan).

- **Capacitățile** (din [capacitati]):
  - scorul curent: valoarea pe ultimul model păstrat;
  - linia de bază:
    - cea confirmată din memorie (stare.json), dacă există;
    - altfel cea mai bună valoare dintre experimentele PĂSTRATE de Kronos pe liniile urmărite (o singură dată, la
      început). De acolo se mută doar prin confirmare (stabilitate.py, v1 punctul 3);
  - pragul folosit = max(podea, zgomot învățat): podeaua e prag_zgomot din configurare, iar zgomotul se învață din
    jurnal (zgomot.py, v1 punctul 1);
  - zona față de linia de bază (v1 punctul 2):
    - verde;
    - galbenă: între 1 și 2 praguri sub (cere remăsurare);
    - roșie: peste 2 praguri sub (nevoia „repara”);
  - procentul din maxim și dacă e disponibilă (modulele de care depinde se încarcă).
- **Vectorul capacităților** (v1 punctul 5): toate capacitățile din configurare, și cele nemăsurate, marcate așa.
- **Ultimul model păstrat** și **tendința** pe ultima linie (v1 punctul 6):
  - câștigul pe ultima oră și pe ultimele ore;
  - panta pe ultimele N ore;
  - „saturat”, când două ore la rând au câștigat sub prag.
  Pragul regulii „continuă” e castig_minim din [nevoi.continua], ridicat doar de zgomotul de remăsurare (același model
  examinat de două ori), dacă e învățat. Zgomotul dintre semințe nu se aplică între două ore ale aceleiași antrenări.
- **Retenția R** (8 octombrie 2026, doar raportată, nu criteriu): la capacitățile unde „mai mare e mai bine”, scorul
  ultimului model ÷ scorul modelului din care a pornit linia lui (pornire.json, --porneste-din). La fapte: faptele noi
  rămase din cele de la plecare.
- **Configurările Kronos**, **hrana** și **nivelul** permis de guvernator, ca în v0.

Valorile vin din măsurători (masuratori.py): scorurile fișei, apoi uneltele de examen, apoi criteriile de la oră.
"""

from __future__ import annotations

import fnmatch
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from module.continuum import GALBENA, ROSIE, VERDE, guvernator, peste
from module.continuum.masuratori import REUSITE, criterii_din, masuratori_unelte, numar, valoare  # noqa: F401
from module.continuum.observa import ARHITECTURA
from module.continuum.zgomot import masuratori_pe_experiment, zgomot_invatat

NEMASURATA = "nemăsurată"


@dataclass
class Capacitate:
    nume: str
    metrica: str
    mai_mare_e_mai_bine: bool
    prag_zgomot: float            # pragul folosit: max(podea, zgomot învățat)
    maxim: float | None
    disponibila: bool
    motiv_indisponibila: str | None
    linie_de_baza: float | None = None
    experiment_baza: int | None = None
    curent: float | None = None   # pe ultimul model păstrat
    procent: float | None = None  # curent, din maxim
    degradata: bool = False       # sub linia de bază cu mai mult decât pragul (zona galbenă sau roșie)
    podea: float | None = None    # prag_zgomot din configurare
    zgomot_invatat: float | None = None
    zgomot_remasurare: float | None = None  # doar din „același model examinat de două ori”
    perechi_zgomot: int = 0
    stare_zgomot: str = ""
    zona: str | None = None
    baza_confirmata: bool = False  # linia de bază vine din memorie, confirmată; altfel e cea mai bună din jurnal
    masuratori: int = 0            # de câte ori a fost măsurat ultimul model (oră, unelte): 2+ = remăsurat
    retentie: float | None = None  # R = scorul de acum ÷ scorul modelului de pornire al liniei (doar raportat)
    retentie_fata_de: int | None = None

    def castig(self, nou: float, vechi: float) -> float:
        """Cât e nou mai bun decât vechi, în direcția capacității (negativ = mai rău)."""
        return nou - vechi if self.mai_mare_e_mai_bine else vechi - nou

    def in_vector(self) -> dict[str, Any]:
        return {"masurata": self.curent is not None, "scor": self.curent, "linie_de_baza": self.linie_de_baza,
                "experiment_baza": self.experiment_baza, "baza_confirmata": self.baza_confirmata,
                "zona": self.zona or NEMASURATA, "prag_folosit": self.prag_zgomot, "podea": self.podea,
                "zgomot_invatat": self.zgomot_invatat, "stare_zgomot": self.stare_zgomot,
                "perechi_zgomot": self.perechi_zgomot, "masuratori_ultimul_model": self.masuratori,
                "retentie": self.retentie, "retentie_fata_de": self.retentie_fata_de,
                "procent": self.procent, "disponibila": self.disponibila,
                "motiv_indisponibila": self.motiv_indisponibila}


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
    # v3 (14 octombrie 2026): pentru „deprinde” cu scadere_minima, capacitate → [(experiment, valoare)], întâi modelul de
    # pornire, apoi copiile răcite (modelele zilei), în ordine; valoarea e None dacă n-a fost măsurată
    nopti: dict[str, list[tuple[int, float | None]]] = field(default_factory=dict)

    def vector(self) -> dict[str, dict[str, Any]]:
        """Vectorul capacităților (v1 punctul 5): toate, cu scor, linie de bază, zonă, prag folosit și procent."""
        return {n: c.in_vector() for n, c in self.capacitati.items()}

    def rezumat(self) -> dict[str, Any]:
        """Ce intră în jurnalul ciclurilor."""
        return {
            "nivel": self.nivel, "de_ce_nivelul": self.motiv_nivel, "ultimul_id": self.ultimul_id,
            "ultimul_model": self.ultimul_model, "capacitati": self.vector(), "tendinta": self.tendinta,
            "hrana": self.hrana, **({"nopti": self.nopti} if self.nopti else {}),
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


def zona(c: Capacitate, reguli: dict[str, float]) -> str | None:
    """Verde / galbenă (între „galben” și „rosu” praguri sub linia de bază) / roșie (peste „rosu” praguri sub)."""
    if c.curent is None or c.linie_de_baza is None:
        return None
    scadere = -c.castig(c.curent, c.linie_de_baza)
    if peste(scadere, reguli["rosu"] * c.prag_zgomot):
        return ROSIE
    if peste(scadere, reguli["galben"] * c.prag_zgomot):
        return GALBENA
    return VERDE


def panta(valori: list[float]) -> float:
    """Panta dreptei celei mai potrivite prin valori (pe oră); 0 pentru mai puțin de 2 valori."""
    n = len(valori)
    if n < 2:
        return 0.0
    medie_x, medie_y = (n - 1) / 2, sum(valori) / n
    return sum((x - medie_x) * (y - medie_y) for x, y in enumerate(valori)) / sum((x - medie_x) ** 2 for x in range(n))


def tendinta(puncte: list[tuple[int, float]], c: Capacitate, reguli: dict[str, Any], linie: str) -> dict[str, Any]:
    """Pe ultima linie: câștigul ultimei ore, câștigurile ultimelor ore, panta pe ultimele N ore (în direcția bună: pozitivă
    = se îmbunătățește) și dacă e saturat (două ore la rând cu câștig sub prag)."""
    prag = max(reguli.get("castig_minim", 0.0), c.zgomot_remasurare or 0.0)
    n = reguli.get("ore_tendinta", 3)
    castiguri = [c.castig(b, a) for (_, a), (_, b) in zip(puncte, puncte[1:])]
    ultimele = [v for _, v in puncte[-n:]]
    t: dict[str, Any] = {"linie": linie, "capacitate": c.nume, "la": {"experiment": puncte[-1][0], "valoare": puncte[-1][1]},
                         "castig": castiguri[-1] if castiguri else None, "castiguri": castiguri[-n:], "prag": prag,
                         "ore_tendinta": n, "panta": None, "saturat": len(castiguri) >= 2 and not any(
                             peste(g, prag) for g in castiguri[-2:])}
    if len(puncte) >= 2:
        t["de_la"] = {"experiment": puncte[-2][0], "valoare": puncte[-2][1]}
    if len(ultimele) >= n:
        p = panta(ultimele)
        t["panta"] = p if c.mai_mare_e_mai_bine else -p
    return t


def evalueaza(observat: Any, config: dict[str, Any], memorie: dict[str, Any] | None = None) -> StareaOrganismului:
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

    din_memorie = (memorie or {}).get("capacitati") or {}
    for nume, cap in config["capacitati"].items():
        motiv = _indisponibila(cap, observat.module)
        zg = zgomot_invatat(fise, cap, config["zgomot"])
        c = Capacitate(nume, cap["metrica"], cap["mai_mare_e_mai_bine"], zg["prag"], cap["maxim"],
                       disponibila=motiv is None, motiv_indisponibila=motiv, podea=zg["podea"],
                       zgomot_invatat=zg["zgomot"], perechi_zgomot=zg["perechi"], stare_zgomot=zg["stare"],
                       zgomot_remasurare=zg["zgomot_remasurare"])
        confirmata = din_memorie.get(nume) or {}
        if confirmata.get("baza_confirmata") and numar(confirmata.get("linie_de_baza")):
            c.linie_de_baza, c.experiment_baza = float(confirmata["linie_de_baza"]), confirmata.get("experiment_baza")
            c.baza_confirmata = True
        else:
            valori = [(f["id"], v) for f in pastrate if (v := valoare(f, cap, unelte)) is not None]
            if valori:
                c.experiment_baza, c.linie_de_baza = (max if c.mai_mare_e_mai_bine else min)(valori, key=lambda p: p[1])
        c.curent = valoare(ultimul, cap, unelte) if ultimul else None
        c.masuratori = len(masuratori_pe_experiment(fise, cap).get(ultimul["id"], [])) if ultimul else 0
        if c.curent is not None and c.maxim:
            c.procent = round(100 * c.curent / c.maxim, 1)
        c.zona = zona(c, config["zone"])
        c.degradata = c.zona in (GALBENA, ROSIE)
        stare.capacitati[nume] = c

    if ultimul:  # retenția R: față de modelul din care a pornit linia ultimului model (doar raportată)
        pornire = next((l.get("pornire") for l in linii.values()
                        if l.get("stare") == "ok" and l.get("linie") == ultimul["linie"]), None)
        fisa_pornire = next((f for f in fise if f.get("id") == pornire), None) if pornire is not None else None
        for nume, c in stare.capacitati.items():
            la_plecare = valoare(fisa_pornire, config["capacitati"][nume], unelte) if fisa_pornire else None
            if c.mai_mare_e_mai_bine and c.curent is not None and la_plecare:
                c.retentie, c.retentie_fata_de = round(c.curent / la_plecare, 3), pornire

    continua = config["nevoi"].get("continua")
    if continua and continua["capacitate"] in stare.capacitati and reusite:
        cap = config["capacitati"][continua["capacitate"]]
        linie = reusite[-1]["linie"]
        puncte = [(f["id"], v) for f in reusite if f["linie"] == linie and (v := valoare(f, cap, unelte)) is not None]
        if puncte:
            stare.tendinta = tendinta(puncte, stare.capacitati[continua["capacitate"]], continua, linie)

    deprinde = config["nevoi"].get("deprinde") or {}
    if "scadere_minima" in deprinde:
        copii = sorted((f for f in fise if fnmatch.fnmatchcase(str(f.get("linie", "")), deprinde["copii"])
                        and f.get("decizie") == "pastrat"), key=lambda f: f.get("id", 0))
        pornire = next((f for f in fise if f.get("id") == deprinde["pornire"]), None)
        for nume in deprinde["capacitati"]:
            cap = config["capacitati"][nume]
            stare.nopti[nume] = ([(deprinde["pornire"], valoare(pornire, cap, unelte) if pornire else None)]
                                 + [(f["id"], valoare(f, cap, unelte)) for f in copii])

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
