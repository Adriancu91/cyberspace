"""NEVOI (etapa 3): starea organismului → nevoi, fiecare cu tip, capacitate, urgență și motiv (secțiunea 4.3).

Urgența e locul tipului în [continuum] „ordinea_nevoilor” („repara” e mereu prima: urgența 1). Nevoile din v1:
- **repara** (zona roșie, v1 punctul 2): o capacitate a căzut peste 2 praguri sub linia de bază. În v1, acțiunea e un
  raport clar către om, cu modelul păstrat la care s-ar întoarce.
- **masoara**: ultimul model păstrat n-a dat toate examenele.
- **remasoara**, o singură dată pe model:
  - zona galbenă: o capacitate e între 1 și 2 praguri sub linia de bază. Se cere o remăsurare, nu o acțiune;
  - confirmare: un candidat din coadă (stabilitate.py) așteaptă a doua măsurătoare, iar capacitatea are o unealtă de
    examen.
- **continua** (v1 punctul 6): povestirile încă învață. Se cere doar dacă ultima oră a câștigat peste prag ȘI
  tendința pe ultimele N ore e bună. Două ore la rând sub prag înseamnă „saturat”: nu se mai continuă, iar „dezvolta”
  trece în față.
- **dezvolta**: cea mai slabă capacitate din vectorul capacităților (cel mai mic procent din maxim, dintre cele
  măsurate), cu ce se știe despre hrana ei.

- **linie_noua** (v2): în lista ei albă e o configurare neîncepută (nicio oră în jurnal). E o variantă adevărată
  lângă „continua”: care se alege o spune ordinea din configurare. Motivul spune și cum stă linia de acum.

Nevoile nu țin cont de nivel, de module, de răcire sau de configurările care lipsesc. Asta o face ALEGE: sare peste
ce nu se poate face acum și spune de ce.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from module.continuum import GALBENA, ROSIE, cate, peste, ro, ro_scurt  # noqa: F401
from module.continuum.evalueaza import StareaOrganismului, se_potriveste
from module.continuum.stabilitate import in_asteptare


@dataclass
class Nevoie:
    tip: str          # repara / masoara / remasoara / continua / dezvolta
    capacitate: str   # ex. „fapte”; la masoara, capacitățile nemăsurate, legate cu „+”
    urgenta: float    # 1 = cea mai urgentă
    motiv: str        # în română, pentru jurnal
    detalii: dict[str, Any] = field(default_factory=dict)

    @property
    def cheie(self) -> str:
        return f"{self.tip}:{self.capacitate}"


def _sub_baza(c: Any) -> str:
    scadere = -c.castig(c.curent, c.linie_de_baza)
    return (f"{c.nume} = {ro_scurt(c.curent)}, sub linia de bază {ro_scurt(c.linie_de_baza)} (#{c.experiment_baza}) cu "
            f"{ro_scurt(scadere)}, adică {ro(scadere / c.prag_zgomot, 2) if c.prag_zgomot else '∞'} praguri "
            f"(pragul folosit: {ro_scurt(c.prag_zgomot)})")


def nevoie_repara(stare: StareaOrganismului, config: dict[str, Any], urgenta: float,
                  memorie: dict[str, Any] | None = None) -> list[Nevoie]:
    return [Nevoie("repara", c.nume, urgenta, f"zona roșie: {_sub_baza(c)}; modelul păstrat la care s-ar întoarce: "
                                              f"#{c.experiment_baza}",
                   {"model_de_intoarcere": c.experiment_baza, "curent": c.curent, "linie_de_baza": c.linie_de_baza,
                    "prag": c.prag_zgomot, "pe_modelul": (stare.ultimul_model or {}).get("experiment")})
            for c in stare.capacitati.values() if c.zona == ROSIE]


def nevoie_masoara(stare: StareaOrganismului, config: dict[str, Any], urgenta: float,
                   memorie: dict[str, Any] | None = None) -> Nevoie | None:
    if stare.ultimul_model is None:
        return None
    lipsa = [n for n, c in stare.capacitati.items() if config["capacitati"][n]["masurare"] and c.curent is None]
    if not lipsa:
        return None
    experiment = stare.ultimul_model["experiment"]
    return Nevoie("masoara", "+".join(lipsa), urgenta,
                  f"examenele n-au mai fost date pe ultimul model păstrat (#{experiment}): lipsesc {', '.join(lipsa)}",
                  {"capacitati": lipsa, "experiment": experiment})


def nevoie_remasoara(stare: StareaOrganismului, config: dict[str, Any], urgenta: float,
                     memorie: dict[str, Any] | None = None) -> list[Nevoie]:
    """O remăsurare pe capacitate: zona galbenă (dacă ultimul model n-a fost deja remăsurat), apoi candidații."""
    if stare.ultimul_model is None:
        return []
    experiment = stare.ultimul_model["experiment"]
    gasite = {c.nume: Nevoie("remasoara", c.nume, urgenta, f"zona galbenă: {_sub_baza(c)}; cer o remăsurare, nu o "
                                                          f"acțiune",
                             {"capacitati": [c.nume], "experiment": experiment, "de_ce": "zona galbenă"})
              for c in stare.capacitati.values() if c.zona == GALBENA and c.masuratori < 2}
    for k in in_asteptare(memorie or {}):
        cap = config["capacitati"].get(k["capacitate"])
        if cap and cap["masurare"] and k["capacitate"] not in gasite:
            gasite[k["capacitate"]] = Nevoie("remasoara", k["capacitate"], urgenta, f"candidat: {k['motiv']}",
                                             {"capacitati": [k["capacitate"]], "experiment": k["experiment"],
                                              "de_ce": "confirmare"})
    return list(gasite.values())


def nevoie_continua(stare: StareaOrganismului, config: dict[str, Any], urgenta: float,
                    memorie: dict[str, Any] | None = None) -> Nevoie | None:
    reguli = config["nevoi"]["continua"]
    t = stare.tendinta
    if not t or t["castig"] is None or not peste(t["castig"], t["prag"]) or t["panta"] is None \
            or not peste(t["panta"], 0):
        return None
    c = stare.capacitati[t["capacitate"]]
    directia = "crește" if c.mai_mare_e_mai_bine else "scade"
    motiv = (f"{c.metrica} încă {directia}: în ultima oră {ro(t['de_la']['valoare'], 4)} → {ro(t['la']['valoare'], 4)} "
             f"(#{t['de_la']['experiment']} → #{t['la']['experiment']}, linia {t['linie']}), un câștig de "
             f"{ro(t['castig'], 4)}, peste pragul de {ro_scurt(t['prag'])}; pe ultimele {t['ore_tendinta']} ore "
             f"tendința e bună ({ro(abs(t['panta']), 4)} pe oră)")
    return Nevoie("continua", reguli["capacitate"], urgenta, motiv, {"linie": t["linie"]})


def nevoie_dezvolta(stare: StareaOrganismului, config: dict[str, Any], urgenta: float,
                    memorie: dict[str, Any] | None = None) -> Nevoie | None:
    vector = stare.vector()
    masurate = sorted((n for n, v in vector.items() if v["masurata"] and v["procent"] is not None),
                      key=lambda n: (vector[n]["procent"], n))
    if not masurate:
        return None
    slaba, c = masurate[0], stare.capacitati[masurate[0]]
    motiv = f"{slaba} = {ro(c.procent)}% ({ro_scurt(c.curent)} din {ro_scurt(c.maxim)}), cea mai slabă capacitate"
    if len(masurate) > 1:
        motiv += " (" + ", ".join(f"{n} = {ro(vector[n]['procent'])}%" for n in masurate[1:]) + ")"
    h = stare.hrana.get(slaba)
    if h is None:
        motiv += "; n-are hrană în [hrana]"
    elif h.get("stare") != "ok":
        motiv += f"; hrana din {h['dosar']} nu se poate citi"
    elif h["nefolosita"]:
        motiv += f"; {cate(h['povesti'], 'povești')} nefolosite în {h['dosar']}"
    else:
        motiv += f"; hrana din {h['dosar']} ({cate(h['povesti'], 'povești')}) a fost folosită de {', '.join(h['folosita_de'])}"
    if (stare.tendinta or {}).get("saturat"):
        motiv += "; povestirile sunt saturate (două ore la rând sub prag), deci dezvoltarea trece în față"
    return Nevoie("dezvolta", slaba, urgenta, motiv, {"procent": c.procent})


def nevoie_linie_noua(stare: StareaOrganismului, config: dict[str, Any], urgenta: float,
                      memorie: dict[str, Any] | None = None) -> Nevoie | None:
    reguli = config["nevoi"]["linie_noua"]
    neincepute = sorted(cale for cale, l in stare.linii.items() if l.get("stare") == "ok" and l["ore_facute"] == 0
                        and se_potriveste(cale, reguli["configurari"]))
    if not neincepute:
        return None
    t = stare.tendinta
    if not t:
        context = "nicio linie urmărită n-are încă ore"
    elif t.get("saturat"):
        context = f"linia {t['linie']} e saturată (două ore la rând sub pragul de {ro_scurt(t['prag'])})"
    elif t["castig"] is not None and peste(t["castig"], t["prag"]):
        context = f"linia {t['linie']} încă învață (ultima oră: {ro(t['castig'], 4)}), deci e o variantă lângă continuare"
    else:
        context = f"linia {t['linie']} a câștigat puțin în ultima oră"
    motiv = f"în lista albă sunt configurări care n-au pornit niciodată ({', '.join(neincepute)}); {context}"
    return Nevoie("linie_noua", reguli["capacitate"], urgenta, motiv, {"configurari": neincepute})


def nevoie_deprinde(stare: StareaOrganismului, config: dict[str, Any], urgenta: float,
                    memorie: dict[str, Any] | None = None) -> Nevoie | None:
    """v3: capacitățile din lista nevoii pe care ultimul model păstrat le are măsurate și sub „prag_deprins”. Ținta e
    cea mai departe de pragul ei; celelalte sunt pomenite în motiv."""
    reguli = config["nevoi"]["deprinde"]
    if "scadere_minima" in reguli:
        return nevoi_deprinde_dupa_scadere(stare, config, urgenta)
    departe: list[tuple[float, str, str]] = []
    for nume in reguli["capacitati"]:
        c, prag = stare.capacitati.get(nume), (config["capacitati"].get(nume) or {}).get("prag_deprins")
        if c is None or prag is None or c.curent is None:
            continue
        lipsa = -c.castig(c.curent, prag)  # cât e sub prag, în direcția capacității
        if peste(lipsa, 0):
            departe.append((lipsa / abs(prag) if prag else lipsa, nume,
                            f"{nume} = {ro_scurt(c.curent)} ({c.metrica}; deprins înseamnă "
                            f"{'peste' if c.mai_mare_e_mai_bine else 'sub'} {ro_scurt(prag)})"))
    if not departe:
        return None
    departe.sort(key=lambda d: (-d[0], d[1]))
    model = stare.ultimul_model or {}
    motiv = (f"ultimul model păstrat (#{model.get('experiment')}, linia {model.get('linie')}) n-a deprins încă: "
             + "; ".join(d[2] for d in departe) + f". Se învață doar pe o linie din lista albă "
             f"({', '.join(reguli['configurari'])})")
    return Nevoie("deprinde", departe[0][1], urgenta, motiv, {"capacitati": [d[1] for d in departe]})


def nevoi_deprinde_dupa_scadere(stare: StareaOrganismului, config: dict[str, Any], urgenta: float) -> list[Nevoie]:
    """v3, din 14 octombrie 2026 (Adrian): o nevoie pe capacitate, cât timp ultima noapte a scăzut-o (pe copiile răcite)
    cu cel puțin scadere_minima față de cea dinainte. Fără două nopți măsurate, nevoia nu apare (nu se ghicește)."""
    reguli = config["nevoi"]["deprinde"]
    gasite: list[tuple[float, Nevoie]] = []
    for nume in reguli["capacitati"]:
        sir = [(e, v) for e, v in stare.nopti.get(nume, [])]
        if len(sir) < 2 or sir[-1][1] is None or sir[-2][1] is None:
            continue
        c = stare.capacitati[nume]
        (e0, v0), (e1, v1) = sir[-2], sir[-1]
        castig = c.castig(v1, v0)  # cât a scăzut (la biți pe octet, mai mic = mai bine)
        if round(castig - reguli["scadere_minima"], 9) < 0:
            continue
        motiv = (f"{nume} ({c.metrica}) a scăzut în ultima noapte {ro_scurt(v0)} → {ro_scurt(v1)} (#{e0} → #{e1}, "
                 f"{'modelul de pornire → ' if e0 == reguli['pornire'] else ''}copia răcită), cu {ro_scurt(castig)}, "
                 f"cel puțin {ro_scurt(reguli['scadere_minima'])}: linia încă o învață. Se învață doar pe o linie din "
                 f"lista albă ({', '.join(reguli['configurari'])})")
        gasite.append((castig, Nevoie("deprinde", nume, urgenta, motiv, {"capacitati": [nume], "noaptea": [e0, e1]})))
    return [n for _, n in sorted(gasite, key=lambda g: -g[0])]


NEVOI = {"deprinde": nevoie_deprinde, "repara": nevoie_repara, "masoara": nevoie_masoara, "remasoara": nevoie_remasoara,
         "continua": nevoie_continua, "dezvolta": nevoie_dezvolta, "linie_noua": nevoie_linie_noua}


def nevoi(stare: StareaOrganismului, config: dict[str, Any], memorie: dict[str, Any] | None = None) -> list[Nevoie]:
    """Nevoile de acum, în ordinea urgenței. Doar tipurile configurate în [nevoi] (plus „repara”, mereu). Când
    povestirile sunt saturate, „dezvolta” trece înaintea lui „continua”."""
    ordinea = list(config["continuum"]["ordinea_nevoilor"])
    if (stare.tendinta or {}).get("saturat") and "dezvolta" in ordinea and "continua" in ordinea \
            and ordinea.index("dezvolta") > ordinea.index("continua"):
        ordinea.remove("dezvolta")
        ordinea.insert(ordinea.index("continua"), "dezvolta")
    rezultat: list[Nevoie] = []
    for urgenta, tip in enumerate(ordinea, start=1):
        if tip in config["nevoi"]:
            gasite = NEVOI[tip](stare, config, urgenta, memorie)
            gasite = gasite if isinstance(gasite, list) else [gasite] if gasite is not None else []
            for nevoie in gasite:  # v3: nota omului din configurare intră în motiv, deci în jurnalul fiecărui ciclu
                if config["nevoi"][tip].get("nota"):
                    nevoie.motiv += f". Notă: {config['nevoi'][tip]['nota']}"
            rezultat += gasite
    return rezultat
