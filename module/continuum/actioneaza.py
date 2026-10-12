"""ACȚIONEAZĂ (etapa 5): pentru nevoia aleasă pornește un experiment Kronos sau o unealtă (secțiunea 4.5 din plan).

CONTINUUM nu face el munca și nu antrenează direct. Pentru fiecare nevoie:
- **masoara**: uneltele de examen ale capacităților nemăsurate („masurare” din [capacitati], ex.
  unelte/examen_fapte.py), pe ultimul model păstrat. Fiecare unealtă scrie fișa ei în jurnalul Kronos.
- **continua**: o antrenare lungă cu o configurare existentă și neterminată (din „configurari”). Comanda e cea din
  [comenzi] „antrenare”, adică unelte/antrenare_lunga.py: o oră = un experiment Kronos.
- **dezvolta**: depinde de nivel.
  - Noaptea (ÎNVĂȚARE): antrenarea pe hrana capacității, cu o configurare existentă, neterminată, care pomenește
    dosarul hranei.
  - Ziua (ÎNTREȚINERE): hrană nouă de la profesor ([hrana] „comanda”), doar dacă nu există deja hrană nefolosită
    destulă.

v2:
- **linie_noua**: o antrenare lungă, de la zero, cu o configurare neîncepută din lista albă a nevoii.
- **continua**, când toate configurările potrivite și-au făcut orele: linia tendinței se **prelungește** cu
  [nevoi.continua] prelungire_ore (aceeași comandă, cu „--ore” = orele făcute + prelungirea). Cu [nevoi.linie_noua]
  în configurare, „continua” ia doar liniile începute.

`planifica` doar pregătește comanda; dacă lipsește ceva, dă un refuz cu motiv. Un refuz e:
- „capacitate_indisponibila”, dacă lipsește un modul, o unealtă sau o configurare;
- „nu acum”, dacă nu e cazul.
`actioneaza` rulează comenzile pe rând (o singură sarcină pe placă), cu timeout. Ce scriu ele merge în
lucru/continuum/actiuni/. În modul simulat nu rulează nimic, ci doar spune ce ar fi pornit.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from module.continuum import INVATARE, cate, ro_scurt
from module.continuum.evalueaza import StareaOrganismului, se_potriveste, pomeneste
from module.continuum.nevoi import Nevoie

CAMP = re.compile(r"\{(\w+)\}")


@dataclass
class Plan:
    nevoie: str                  # cheia nevoii, ex. „dezvolta:fapte”
    fel: str                     # examene / antrenare / hrana
    strategie: str               # sub ce nume învață ÎNVAȚĂ din rezultat
    descriere: str               # în română, pentru jurnal
    comenzi: list[list[str]]
    timeout_secunde: float       # pentru fiecare comandă
    linie: str | None = None     # la antrenare: linia Kronos în care apar orele
    detalii: dict[str, Any] = field(default_factory=dict)


@dataclass
class Refuz:
    motiv: str
    indisponibila: bool = True   # True: capacitate_indisponibila (lipsește ceva); False: nu e cazul acum


def completeaza(sablon: list[str], valori: dict[str, Any]) -> list[str]:
    """Pune valorile în comandă: {python} e interpretorul de acum. Un câmp fără valoare (None) dispare, împreună cu
    opțiunea dinaintea lui (ex. „--porneste-din {ultimul_model}” fără model = pornire de la zero)."""
    valori = {"python": sys.executable, **valori}
    comanda: list[str] = []
    for parte in sablon:
        campuri = CAMP.findall(parte)
        necunoscute = [c for c in campuri if c not in valori]
        if necunoscute:
            raise KeyError(f"comanda are un câmp necunoscut: {{{necunoscute[0]}}}")
        if any(valori[c] is None for c in campuri):
            if comanda and comanda[-1].startswith("--"):
                comanda.pop()
            continue
        comanda.append(CAMP.sub(lambda m: str(valori[m.group(1)]), parte))
    return comanda


def fisiere_lipsa(comanda: list[str]) -> list[str]:
    """Uneltele (.py) și configurările (.toml) din comandă care nu există."""
    return [p for p in comanda[1:] if p.endswith((".py", ".toml")) and not p.startswith("-") and not Path(p).exists()]


def text_comanda(comanda: list[str]) -> str:
    return subprocess.list2cmdline(["python" if p == sys.executable else p for p in comanda])


def plan_masoara(nevoie: Nevoie, stare: StareaOrganismului, config: dict[str, Any]) -> Plan | Refuz:
    experiment = nevoie.detalii["experiment"]
    comenzi, numite, sarite = [], [], []
    for nume in nevoie.detalii["capacitati"]:
        c = stare.capacitati[nume]
        if not c.disponibila:
            sarite.append(f"{nume}: {c.motiv_indisponibila}")
            continue
        comanda = completeaza(config["capacitati"][nume]["masurare"], {"experiment": experiment})
        lipsa = fisiere_lipsa(comanda)
        if lipsa:
            sarite.append(f"{nume}: lipsește {lipsa[0]}")
            continue
        comenzi.append(comanda)
        numite.append(nume)
    if not comenzi:
        return Refuz("niciun examen nu se poate da (" + "; ".join(sarite) + ")")
    return Plan(nevoie.cheie, "examene", "masoara:examene",
                f"examenele care lipsesc pe modelul #{experiment}: {', '.join(numite)}"
                + (f" (sar peste {'; '.join(sarite)})" if sarite else ""),
                comenzi, config["nevoi"]["masoara"]["timeout_secunde"],
                detalii={"capacitati": numite, "experiment": experiment})


def _model_de_pornire(linie: dict[str, Any], stare: StareaOrganismului) -> int | None:
    """Ultimul model păstrat cu aceeași arhitectură, dacă linia n-a început și nu e „de la zero”."""
    if linie["ore_facute"] > 0 or linie.get("de_la_zero") or not linie.get("arhitectura"):
        return None
    for model in reversed(stare.modele):
        if all(model["arhitectura"].get(k) == v for k, v in linie["arhitectura"].items()):
            return model["experiment"]
    return None


def plan_antrenare(nevoie: Nevoie, stare: StareaOrganismului, config: dict[str, Any], globuri: list[str],
                   potrivita: Any, strategie: str, prelungire: int = 0, de_la_zero: bool = False) -> Plan | Refuz:
    """prelungire (v2): dacă toate configurările potrivite sunt încheiate, linia tendinței primește încă atâtea ore.
    de_la_zero (v2, linie nouă): fără „--porneste-din”, chiar dacă există un model cu aceeași arhitectură."""
    sablon = config["comenzi"]["antrenare"]
    if not sablon:
        return Refuz("lipsește [comenzi] „antrenare” (cum pornește o antrenare lungă)")
    toate = {cale: l for cale, l in stare.linii.items() if l.get("stare") == "ok" and se_potriveste(cale, globuri)
             and potrivita(l)}
    if not toate:
        return Refuz(f"nu există nicio configurare potrivită ({', '.join(globuri)})")
    neterminate = {cale: l for cale, l in toate.items() if not l["terminata"]}
    linia_tendintei = (stare.tendinta or {}).get("linie")
    prelungita = False
    if not neterminate and prelungire > 0:
        # v2: toate și-au făcut orele plănuite; linia tendinței (cea care încă învață) primește încă `prelungire` ore
        neterminate = {cale: l for cale, l in toate.items() if l["linie"] == linia_tendintei}
        prelungita = bool(neterminate)
    if not neterminate:
        incheiate = ", ".join(f"{cale} ({l['ore_facute']} din {l['ore_planificate']})" for cale, l in toate.items())
        return Refuz(f"toate configurările potrivite sunt încheiate: {incheiate}; pentru încă o noapte trebuie "
                     f"pregătită una nouă")
    cale, linie = min(neterminate.items(), key=lambda p: (p[1]["linie"] != linia_tendintei, p[0]))
    model = None if de_la_zero else _model_de_pornire(linie, stare)
    ore = linie["ore_facute"] + prelungire if prelungita else linie["ore_planificate"]
    comanda = completeaza(sablon, {"config": cale, "ore": ore, "ultimul_model": model})
    lipsa = fisiere_lipsa(comanda)
    if lipsa:
        return Refuz(f"lipsește {lipsa[0]}")
    if prelungita:
        cum = f"prelungită cu {prelungire} ore, de la ora {linie['ore_facute'] + 1}"
    elif linie["ore_facute"]:
        cum = f"reluată de la ora {linie['ore_facute'] + 1}"
    else:
        cum = f"din modelul #{model}" if model else "de la zero"
    return Plan(nevoie.cheie, "antrenare", strategie,
                f"antrenare lungă cu {cale} (linia {linie['linie']}, {ore} × "
                f"{ro_scurt(linie['buget_secunde'] / 60)} min, {cum})",
                [comanda], config["nevoi"][nevoie.tip]["timeout_secunde"], linie=linie["linie"],
                detalii={"config": cale, "model_de_pornire": model, "ore": ore, "prelungita": prelungita})


def plan_dezvolta(nevoie: Nevoie, stare: StareaOrganismului, config: dict[str, Any]) -> Plan | Refuz:
    nume = nevoie.capacitate
    h, reguli = stare.hrana.get(nume), config["hrana"].get(nume)
    if h is None or reguli is None:
        return Refuz(f"capacitatea {nume} n-are hrană în [hrana]")
    citita = h.get("stare") == "ok"
    gata = citita and h["nefolosita"] and h["destula"]
    if stare.nivel == INVATARE:
        if not citita:
            return Refuz(f"hrana din {h['dosar']} nu se poate citi ({h.get('eroare')})")
        # O linie care a început pe hrana asta și s-a întrerupt se reia; altfel, hrana folosită nu se mai ia o dată.
        intrerupte = [l for l in stare.linii.values() if l.get("stare") == "ok" and l["linie"] in h["folosita_de"]
                      and not l["terminata"]]
        if not h["nefolosita"] and not intrerupte:
            return Refuz(f"hrana din {h['dosar']} a fost folosită deja ({', '.join(h['folosita_de'])}) și nu s-a "
                         f"schimbat de atunci", indisponibila=False)
        if not h["destula"] and not intrerupte:
            return Refuz(f"prea puțină hrană în {h['dosar']}: {cate(h['povesti'], 'povești')}, minimum {h['minima']}",
                         indisponibila=False)
        return plan_antrenare(nevoie, stare, config, config["nevoi"]["dezvolta"]["configurari"],
                              lambda l: pomeneste(l, h["dosar"]), f"dezvolta:{nume}:antrenare")
    if gata:
        return Refuz(f"hrana pentru {nume} e gata ({cate(h['povesti'], 'povești')} nefolosite în {h['dosar']}); "
                     f"antrenarea pe ea se face noaptea ({INVATARE})", indisponibila=False)
    if not reguli["comanda"]:
        return Refuz(f"[hrana.{nume}] n-are „comanda” (cum scrie profesorul hrană nouă)")
    scrise = h.get("scrise", 0) if citita else 0
    comanda = completeaza(reguli["comanda"], {"tinta_povesti": scrise + reguli["adaos_povesti"]})
    lipsa = fisiere_lipsa(comanda)
    if lipsa:
        return Refuz(f"lipsește {lipsa[0]}")
    de_ce = ("hrana de acum a fost folosită deja" if citita and not h["nefolosita"] else
             f"sunt doar {cate(h['povesti'], 'povești')}, minimum {h['minima']}" if citita else "hrana nu se poate citi")
    return Plan(nevoie.cheie, "hrana", f"dezvolta:{nume}:hrana",
                f"hrană nouă de la profesor pentru {nume}, până la {cate(scrise + reguli['adaos_povesti'], 'povești')} "
                f"scrise ({de_ce})", [comanda], reguli["timeout_secunde"],
                detalii={"povesti_inainte": h.get("povesti") if citita else None})


def text_raport(nevoie: Nevoie, stare: StareaOrganismului) -> str:
    """Raportul către om pentru zona roșie (v1: CONTINUUM nu repară singur)."""
    c = stare.capacitati[nevoie.capacitate]
    model = stare.ultimul_model or {}
    zgomot = (f"zgomot învățat {ro_scurt(c.zgomot_invatat)} din {c.perechi_zgomot} perechi"
              if c.zgomot_invatat is not None else f"zgomot {c.stare_zgomot} ({c.perechi_zgomot} perechi)")
    return (f"# CONTINUUM: {c.nume} e în zona roșie\n\n"
            f"- Scorul acum: {ro_scurt(c.curent)} ({c.metrica}), pe modelul #{model.get('experiment')} "
            f"(linia {model.get('linie')}).\n"
            f"- Linia de bază: {ro_scurt(c.linie_de_baza)}, de la #{c.experiment_baza} "
            f"({'confirmată' if c.baza_confirmata else 'cea mai bună din jurnal'}).\n"
            f"- Scăderea: {ro_scurt(-c.castig(c.curent, c.linie_de_baza))}, peste 2 praguri. Pragul folosit: "
            f"{ro_scurt(c.prag_zgomot)} (podeaua {ro_scurt(c.podea)}; {zgomot}).\n"
            f"- Modelul păstrat la care s-ar întoarce: #{c.experiment_baza}, salvat de Kronos.\n\n"
            f"În v1, CONTINUUM nu repară singur: decide omul (întoarcerea la #{c.experiment_baza}, o remăsurare sau o "
            f"antrenare nouă).\n")


def plan_raport(nevoie: Nevoie, stare: StareaOrganismului, memorie: dict[str, Any] | None) -> Plan | Refuz:
    """Un singur raport cât timp capacitatea stă în zona roșie: se închide când iese din ea (stare.py)."""
    cheie = f"repara:{nevoie.capacitate}"
    trimis = next((r for r in (memorie or {}).get("rapoarte", []) if r.get("cheie") == cheie and r.get("deschis")), None)
    if trimis:
        return Refuz(f"raportul pentru {nevoie.capacitate} e trimis (ciclul {trimis.get('ciclu')}, {trimis.get('fisier')}); "
                     f"aștept decizia omului", indisponibila=False)
    return Plan(nevoie.cheie, "raport", "repara:raport",
                f"raport către om: {nevoie.capacitate} e în zona roșie; modelul păstrat la care s-ar întoarce: "
                f"#{nevoie.detalii.get('model_de_intoarcere')}", [], 0.0,
                detalii={"cheie": cheie, "text": text_raport(nevoie, stare),
                         "model_de_intoarcere": nevoie.detalii.get("model_de_intoarcere")})


def planifica(nevoie: Nevoie, stare: StareaOrganismului, config: dict[str, Any],
              memorie: dict[str, Any] | None = None) -> Plan | Refuz:
    """Comanda pentru nevoie, sau de ce nu se poate. Capacitatea trebuie să fie disponibilă (modulele ei se încarcă).
    „repara” nu cere modulele: e doar un raport."""
    if nevoie.tip == "repara":
        return plan_raport(nevoie, stare, memorie)
    if nevoie.tip != "masoara":
        c = stare.capacitati.get(nevoie.capacitate)
        if c is None:
            return Refuz(f"capacitatea {nevoie.capacitate} nu e în [capacitati]")
        if not c.disponibila:
            return Refuz(f"{nevoie.capacitate}: {c.motiv_indisponibila}")
    try:
        if nevoie.tip == "masoara":
            return plan_masoara(nevoie, stare, config)
        if nevoie.tip == "remasoara":
            if not config["capacitati"][nevoie.capacitate]["masurare"]:
                return Refuz(f"{nevoie.capacitate} n-are o unealtă de remăsurare (examenul ei se dă doar la antrenare)")
            plan = plan_masoara(nevoie, stare, {**config, "nevoi": {**config["nevoi"],
                                                                     "masoara": config["nevoi"]["remasoara"]}})
            if isinstance(plan, Plan):
                plan.strategie = "remasoara:examene"
                plan.descriere = (f"remăsurare ({nevoie.detalii.get('de_ce', 'zona galbenă')}): examenul "
                                  f"{', '.join(plan.detalii['capacitati'])} din nou pe modelul #{plan.detalii['experiment']}")
            return plan
        if nevoie.tip == "continua":
            reguli = config["nevoi"]["continua"]
            # v2: cu „linie_noua” configurată, liniile neîncepute sunt ale ei; „continua” ia doar liniile începute
            doar_incepute = "linie_noua" in config["nevoi"]
            return plan_antrenare(nevoie, stare, config, reguli["configurari"],
                                  (lambda l: l["ore_facute"] > 0) if doar_incepute else (lambda l: True),
                                  f"continua:{nevoie.capacitate}:antrenare", prelungire=reguli.get("prelungire_ore", 0))
        if nevoie.tip == "linie_noua":
            return plan_antrenare(nevoie, stare, config, config["nevoi"]["linie_noua"]["configurari"],
                                  lambda l: l["ore_facute"] == 0, f"linie_noua:{nevoie.capacitate}:antrenare",
                                  de_la_zero=True)
        return plan_dezvolta(nevoie, stare, config)
    except KeyError as e:
        return Refuz(str(e).strip("'\""))


def actioneaza(plan: Plan, simuleaza: bool, director: Path, ciclu: int) -> dict[str, Any]:
    """Rulează comenzile planului, pe rând, fiecare cu timeout. Se oprește la prima care nu reușește. Un raport (fel
    „raport”) doar se scrie, în lucru/continuum/rapoarte/."""
    comenzi = [text_comanda(c) for c in plan.comenzi]
    if simuleaza:
        return {"simulat": True, "reusit": None, "comenzi": comenzi}
    if plan.fel == "raport":
        raport = director / "rapoarte" / f"ciclu_{ciclu:05d}_{plan.nevoie.replace(':', '_')}.md"
        raport.parent.mkdir(parents=True, exist_ok=True)
        raport.write_text(plan.detalii["text"], encoding="utf-8")
        return {"simulat": False, "reusit": True, "motiv": None, "comenzi": [], "raport": raport.as_posix()}
    jurnal = director / "actiuni" / f"ciclu_{ciclu:05d}_{plan.fel}.log"
    jurnal.parent.mkdir(parents=True, exist_ok=True)
    rulate, motiv = [], None
    for comanda, text in zip(plan.comenzi, comenzi):
        inceput = time.monotonic()
        try:
            with jurnal.open("a", encoding="utf-8") as iesire:
                iesire.write(f"\n=== {text}\n")
                iesire.flush()
                cod = subprocess.run(comanda, stdout=iesire, stderr=subprocess.STDOUT, timeout=plan.timeout_secunde,
                                     env={**os.environ, "PYTHONUTF8": "1"}).returncode
        except subprocess.TimeoutExpired:
            rulate.append({"comanda": text, "cod": None, "secunde": round(time.monotonic() - inceput, 1)})
            motiv = f"„{text}” a depășit timpul ({plan.timeout_secunde / 60:g} min) și a fost oprită"
            break
        except OSError as e:
            rulate.append({"comanda": text, "cod": None, "secunde": round(time.monotonic() - inceput, 1)})
            motiv = f"„{text}” nu a putut porni: {e}"
            break
        rulate.append({"comanda": text, "cod": cod, "secunde": round(time.monotonic() - inceput, 1)})
        if cod != 0:
            motiv = f"„{text}” a ieșit cu codul {cod} (vezi {jurnal.as_posix()})"
            break
    return {"simulat": False, "reusit": motiv is None, "motiv": motiv, "comenzi": rulate, "iesire": jurnal.as_posix()}
