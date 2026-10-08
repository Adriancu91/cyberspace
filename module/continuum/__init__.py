"""CONTINUUM v1: ritmul zilei, cu măsurare mai atentă (docs/CONTINUUM_plan.md, secțiunea 13: v0 și v1).

v1, pe lângă v0: zgomotul învățat din jurnal, zonele verde / galbenă / roșie față de linia de bază, linia de bază mutată
doar după o a doua măsurătoare (candidat → confirmat), verdictul cu eficiență („SUCCES SCUMP”), vectorul capacităților,
regula „continuă” cu temei (tendința pe ore, „saturat”) și anti-bucla (răcire, strategii blocate, buget zilnic de ore
pe placă). O configurare din v0 merge neschimbată: pragurile noi au valori implicite (IMPLICITE_V1).

CONTINUUM decide ce face Kronos când nimeni nu-i spune. Nu antrenează și nu dă examene singur: la fiecare ciclu
observă, alege o singură nevoie și, dacă nivelul o permite, pornește un experiment Kronos cu o configurare existentă
(sau o unealtă de examene), apoi citește fișa din jurnalul Kronos.

    OBSERVĂ → EVALUEAZĂ → NEVOI → ALEGE → ACȚIONEAZĂ → MĂSOARĂ → ÎNVAȚĂ → STARE

Fiecare etapă e o funcție separată, în fișierul ei. Guvernatorul (guvernator.py) dă nivelul de activitate, iar bucla
(bucla.py) le leagă, cu același buton STOP ca Kronos (lucru/STOP). CONTINUUM nu scrie în kronos/, în examenul oficial,
în jurnalul Kronos sau în date/; ce ține minte stă în lucru/continuum/ (stare.json, cicluri.jsonl).

Aici e ce folosesc toate etapele: nivelurile, verdictele, configurarea (config/continuum.toml) și numerele scrise
românește. Toate pragurile, ferestrele și bugetele vin din configurare, nu din cod.
"""

from __future__ import annotations

import math
import tomllib
from datetime import time as Ora
from pathlib import Path
from typing import Any

# Nivelurile din v0, de la cel mai liniștit: fiecare permite tot ce permite cel dinaintea lui.
REPAUS, INTRETINERE, INVATARE = "REPAUS", "ÎNTREȚINERE", "ÎNVĂȚARE"
NIVELURI = (REPAUS, INTRETINERE, INVATARE)
# Nevoile din v0: doar trei. v1 adaugă „repara” (zona roșie: raport către om) și „remasoara” (zona galbenă, sau un
# candidat care așteaptă a doua măsurătoare).
NEVOI_V0 = ("masoara", "continua", "dezvolta")
NEVOI_V1 = ("repara", "masoara", "remasoara", "continua", "dezvolta")
SUCCES, ESEC, NECONCLUDENT = "SUCCES", "EȘEC", "NECONCLUDENT"
SUCCES_SCUMP = "SUCCES SCUMP"  # un câștig prea mic pentru orele pe placă: încrederea nu urcă
VERDE, GALBENA, ROSIE = "verde", "galbenă", "roșie"

# Valorile implicite ale pragurilor din v1, folosite doar când o configurare mai veche nu le are (config/continuum.toml
# le are pe toate, scrise și explicate). Așa, o configurare din v0 merge neschimbată.
IMPLICITE_V1: dict[str, Any] = {
    "zgomot": {"perechi_minime": 3, "factor": 1.0, "minute_minime": 60},
    "zone": {"galben": 1.0, "rosu": 2.0},
    "stabilitate": {"confirmari": 1},
    "eficienta": {"fractie_scump": 0.5},
    "anti_bucla": {"racire_cicluri": 6, "max_esecuri": 5},
    "buget_ore_placa_pe_zi": 20.0,
    "ore_tendinta": 3,
    "nivel_repara": "REPAUS",  # un raport către om nu cere placa: se poate scrie oricând
}


class EroareContinuum(Exception):
    """Configurarea lui CONTINUUM e greșită; mesajul spune ce și unde."""


def ro(x: float, zecimale: int = 0) -> str:
    """Un număr scris românește: 7.520, 0,4567."""
    text = f"{x:,.{zecimale}f}"
    return text.replace(",", "\0").replace(".", ",").replace("\0", ".")


def peste(valoare: float, prag: float) -> bool:
    """valoare > prag, fără resturile de rotunjire ale numerelor cu virgulă: 4,7 − 3,7 dă 1,0000000000000004, care nu
    trebuie să treacă de un prag de exact 1."""
    return round(valoare - prag, 9) > 0


def ro_scurt(x: float) -> str:
    """Cel mult 4 zecimale, fără cele de prisos: 31, 3,75, 0,4567."""
    return ro(x, 4).rstrip("0").rstrip(",")


def cate(n: int, substantiv: str) -> str:
    """„5 povești”, dar „7.520 de povești” (de la 20 în sus, în afară de cele terminate în 01–19)."""
    return f"{ro(n)} de {substantiv}" if n >= 20 and not 1 <= n % 100 <= 19 else f"{ro(n)} {substantiv}"


# --- configurarea -------------------------------------------------------------------------------------------------

def _cere(sectiune: dict[str, Any], cheie: str, unde: str) -> Any:
    if cheie not in sectiune:
        raise EroareContinuum(f"În {unde} lipsește „{cheie}”")
    return sectiune[cheie]


def _numar(sectiune: dict[str, Any], cheie: str, unde: str, minim: float = 0.0, intreg: bool = False) -> float:
    valoare = _cere(sectiune, cheie, unde)
    if isinstance(valoare, bool) or not isinstance(valoare, (int, float)) or not math.isfinite(valoare) \
            or valoare < minim or (intreg and not float(valoare).is_integer()):
        tip = "un număr întreg" if intreg else "un număr"
        raise EroareContinuum(f"În {unde}, „{cheie}” trebuie să fie {tip} ≥ {minim:g}")
    return int(valoare) if intreg else float(valoare)


def _texte(sectiune: dict[str, Any], cheie: str, unde: str, obligatoriu: bool = True) -> list[str] | None:
    if cheie not in sectiune and not obligatoriu:
        return None
    valoare = _cere(sectiune, cheie, unde)
    if not isinstance(valoare, list) or not all(isinstance(v, str) for v in valoare):
        raise EroareContinuum(f"În {unde}, „{cheie}” trebuie să fie o listă de texte")
    return list(valoare)


def _fereastra(sectiune: dict[str, Any], cheie: str, unde: str) -> tuple[Ora, Ora]:
    """„22:00-07:00” → (22:00, 07:00); o fereastră poate trece peste miezul nopții."""
    text = str(_cere(sectiune, cheie, unde)).replace("–", "-").replace(" ", "")
    try:
        inceput, sfarsit = (Ora.fromisoformat(parte) for parte in text.split("-"))
    except ValueError:
        raise EroareContinuum(f"În {unde}, „{cheie}” trebuie să fie de forma „22:00-07:00”") from None
    return inceput, sfarsit


def _nivel(sectiune: dict[str, Any], cheie: str, unde: str) -> str:
    valoare = _cere(sectiune, cheie, unde)
    if valoare not in NIVELURI:
        raise EroareContinuum(f"În {unde}, „{cheie}” trebuie să fie unul dintre: {', '.join(NIVELURI)}")
    return valoare


def citeste_config(cale: str | Path) -> dict[str, Any]:
    """config/continuum.toml, verificat. Secțiunile [continuum], [guvernator] și [invatare] sunt obligatorii (acolo
    stau pragurile); [module], [capacitati], [hrana], [nevoi], [comenzi], [linii] pot lipsi: CONTINUUM merge și cu
    zero module, doar că n-are ce alege."""
    cale = Path(cale)
    if not cale.exists():
        raise EroareContinuum(f"Nu găsesc configurarea „{cale}”")
    try:
        with cale.open("rb") as f:
            brut = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise EroareContinuum(f"„{cale}” are o greșeală de scriere: {e}") from e

    def sectiune(nume: str, obligatorie: bool = True) -> dict[str, Any]:
        valoare = brut.get(nume)
        if valoare is None and not obligatorie:
            return {}
        if not isinstance(valoare, dict):
            raise EroareContinuum(f"În „{cale}” lipsește secțiunea [{nume}]")
        return valoare

    c = sectiune("continuum")
    ordinea = _texte(c, "ordinea_nevoilor", "[continuum]")
    if len(set(ordinea)) != len(ordinea) or any(n not in NEVOI_V1 for n in ordinea):
        raise EroareContinuum(f"În [continuum], „ordinea_nevoilor” poate avea, o singură dată, doar: {', '.join(NEVOI_V1)}")
    # v1: „repara” e mereu prima (urgența 1); „remasoara” vine după „masoara”, dacă ordinea n-o pomenește.
    ordinea = ["repara"] + [n for n in ordinea if n != "repara"]
    if "remasoara" not in ordinea and "masoara" in ordinea:
        ordinea.insert(ordinea.index("masoara") + 1, "remasoara")
    director = Path(str(_cere(c, "director_lucru", "[continuum]")))
    continuum = {
        "director_lucru": director if director.is_absolute() else Path.cwd() / director,
        "redescopera_la_cicluri": _numar(c, "redescopera_la_cicluri", "[continuum]", 1, intreg=True),
        "jurnal_max_mb": _numar(c, "jurnal_max_mb", "[continuum]", 0.001),
        "ordinea_nevoilor": ordinea,
    }

    g = sectiune("guvernator")
    pauze = g.get("pauza_minute")
    if not isinstance(pauze, dict):
        raise EroareContinuum("În [guvernator] lipsește „pauza_minute” (câte minute între cicluri, pe nivel)")
    guvernator = {
        "fereastra_invatare": _fereastra(g, "fereastra_invatare", "[guvernator]"),
        "fereastra_intretinere": _fereastra(g, "fereastra_intretinere", "[guvernator]"),
        "minute_fara_om": _numar(g, "minute_fara_om", "[guvernator]"),
        "temperatura_max": _numar(g, "temperatura_max", "[guvernator]"),
        "memorie_video_libera_min_mb": _numar(g, "memorie_video_libera_min_mb", "[guvernator]"),
        "procese_grele": _texte(g, "procese_grele", "[guvernator]"),
        "pauza_minute": {n: _numar(pauze, n, "[guvernator.pauza_minute]") for n in NIVELURI},
        "buget_ore_placa_pe_zi": _numar({"buget_ore_placa_pe_zi": IMPLICITE_V1["buget_ore_placa_pe_zi"], **g},
                                        "buget_ore_placa_pe_zi", "[guvernator]"),
    }

    i = sectiune("invatare")
    invatare = {"incredere_initiala": _numar(i, "incredere_initiala", "[invatare]"),
                "pas_incredere": _numar(i, "pas_incredere", "[invatare]")}
    if invatare["incredere_initiala"] > 1:
        raise EroareContinuum("În [invatare], „incredere_initiala” e între 0 și 1")

    module = sectiune("module", obligatorie=False)
    if not all(isinstance(v, str) for v in module.values()):
        raise EroareContinuum("În [module], fiecare modul e un text: „pachet.fisier:Clasa” sau „pachet.fisier”")

    capacitati = {}
    for nume, cap in sectiune("capacitati", obligatorie=False).items():
        unde = f"[capacitati.{nume}]"
        if not isinstance(cap, dict):
            raise EroareContinuum(f"{unde} trebuie să fie o secțiune")
        directie = _cere(cap, "mai_mare_e_mai_bine", unde)
        if not isinstance(directie, bool):
            raise EroareContinuum(f"În {unde}, „mai_mare_e_mai_bine” e true sau false")
        unealta = cap.get("unealta")
        if unealta is not None and (not isinstance(unealta, dict) or not all(
                isinstance(unealta.get(k), str) for k in ("linie", "scor"))):
            raise EroareContinuum(f"În {unde}, „unealta” e de forma {{ linie = \"...\", scor = \"...\" }}")
        capacitati[nume] = {
            "metrica": str(_cere(cap, "metrica", unde)),
            "mai_mare_e_mai_bine": directie,
            "prag_zgomot": _numar(cap, "prag_zgomot", unde),
            "maxim": _numar(cap, "maxim", unde, 1e-9) if "maxim" in cap else None,
            "module": _texte(cap, "module", unde, obligatoriu=False) or [],
            "masurare": _texte(cap, "masurare", unde, obligatoriu=False),
            "unealta": unealta,
            # ex. nota: comparabilă doar pe același număr de povești; celelalte măsurători nu intră nicăieri
            "povesti": int(_numar(cap, "povesti", unde, 2, intreg=True)) if "povesti" in cap else None,
        }

    hrana = {}
    for capacitate, h in sectiune("hrana", obligatorie=False).items():
        unde = f"[hrana.{capacitate}]"
        if not isinstance(h, dict):
            raise EroareContinuum(f"{unde} trebuie să fie o secțiune")
        hrana[capacitate] = {
            "dosar": Path(str(_cere(h, "dosar", unde))).as_posix(),
            "minima_povesti": _numar(h, "minima_povesti", unde, intreg=True),
            "comanda": _texte(h, "comanda", unde, obligatoriu=False),
            "adaos_povesti": _numar(h, "adaos_povesti", unde, 1, intreg=True) if "adaos_povesti" in h else None,
            "timeout_secunde": _numar(h, "timeout_ore", unde, 1e-6) * 3600 if "timeout_ore" in h else None,
        }
        if hrana[capacitate]["comanda"] and (hrana[capacitate]["adaos_povesti"] is None
                                             or hrana[capacitate]["timeout_secunde"] is None):
            raise EroareContinuum(f"În {unde}, cu „comanda” trebuie și „adaos_povesti” și „timeout_ore”")

    nevoi = {}
    for tip, n in sectiune("nevoi", obligatorie=False).items():
        unde = f"[nevoi.{tip}]"
        if tip not in NEVOI_V1:
            raise EroareContinuum(f"{unde}: nevoile sunt doar {', '.join(NEVOI_V1)}")
        if tip not in ordinea:
            raise EroareContinuum(f"{unde} e configurată, dar lipsește din [continuum] „ordinea_nevoilor”")
        if not isinstance(n, dict):
            raise EroareContinuum(f"{unde} trebuie să fie o secțiune")
        nevoie: dict[str, Any] = {"nivel": _nivel(n, "nivel", unde)}
        if tip in ("masoara", "remasoara"):
            nevoie["timeout_secunde"] = _numar(n, "timeout_minute", unde, 1e-6) * 60
        elif tip != "repara":
            nevoie["timeout_secunde"] = _numar(n, "timeout_ore", unde, 1e-6) * 3600
            nevoie["configurari"] = _texte(n, "configurari", unde)
        if tip == "continua":
            nevoie["capacitate"] = str(_cere(n, "capacitate", unde))
            nevoie["castig_minim"] = _numar(n, "castig_minim", unde)
            nevoie["ore_tendinta"] = _numar({"ore_tendinta": IMPLICITE_V1["ore_tendinta"], **n}, "ore_tendinta", unde, 2,
                                            intreg=True)
        nevoi[tip] = nevoie
    # v1: „repara” (raport către om) merge oricând; „remasoara” folosește setările lui „masoara”, dacă n-are ale ei.
    nevoi.setdefault("repara", {"nivel": IMPLICITE_V1["nivel_repara"]})
    if "masoara" in nevoi:
        nevoi.setdefault("remasoara", dict(nevoi["masoara"]))

    minime = {"perechi_minime": 1, "confirmari": 1, "max_esecuri": 1}

    def sectiune_v1(nume: str, chei: dict[str, Any]) -> dict[str, Any]:
        s = {**IMPLICITE_V1[nume], **sectiune(nume, obligatorie=False)}
        return {k: _numar(s, k, f"[{nume}]", minime.get(k, 0.0), intreg=isinstance(v, int)) for k, v in chei.items()}

    zgomot = sectiune_v1("zgomot", IMPLICITE_V1["zgomot"])
    zone = sectiune_v1("zone", IMPLICITE_V1["zone"])
    if not 0 < zone["galben"] < zone["rosu"]:
        raise EroareContinuum("În [zone], 0 < galben < rosu (în praguri sub linia de bază)")

    comenzi = sectiune("comenzi", obligatorie=False)
    antrenare = _texte(comenzi, "antrenare", "[comenzi]", obligatoriu=False)
    linii = sectiune("linii", obligatorie=False)
    return {
        "cale": cale.as_posix(),
        "continuum": continuum,
        "guvernator": guvernator,
        "invatare": invatare,
        "module": dict(module),
        "capacitati": capacitati,
        "hrana": hrana,
        "nevoi": nevoi,
        "comenzi": {"antrenare": antrenare},
        "linii": {"configurari": _texte(linii, "configurari", "[linii]", obligatoriu=False) or []},
        "zgomot": zgomot,
        "zone": zone,
        "stabilitate": sectiune_v1("stabilitate", IMPLICITE_V1["stabilitate"]),
        "eficienta": sectiune_v1("eficienta", IMPLICITE_V1["eficienta"]),
        "anti_bucla": sectiune_v1("anti_bucla", IMPLICITE_V1["anti_bucla"]),
    }
