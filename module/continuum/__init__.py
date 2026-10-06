"""CONTINUUM v0: ritmul zilei (docs/CONTINUUM_plan.md, secțiunile 13 și 15).

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
# Nevoile din v0: doar trei.
NEVOI_V0 = ("masoara", "continua", "dezvolta")
SUCCES, ESEC, NECONCLUDENT = "SUCCES", "EȘEC", "NECONCLUDENT"


class EroareContinuum(Exception):
    """Configurarea lui CONTINUUM e greșită; mesajul spune ce și unde."""


def ro(x: float, zecimale: int = 0) -> str:
    """Un număr scris românește: 7.520, 0,4567."""
    text = f"{x:,.{zecimale}f}"
    return text.replace(",", "\0").replace(".", ",").replace("\0", ".")


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
    if len(set(ordinea)) != len(ordinea) or any(n not in NEVOI_V0 for n in ordinea):
        raise EroareContinuum(f"În [continuum], „ordinea_nevoilor” poate avea, o singură dată, doar: {', '.join(NEVOI_V0)}")
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
        if tip not in NEVOI_V0:
            raise EroareContinuum(f"{unde}: v0 are doar nevoile {', '.join(NEVOI_V0)}")
        if tip not in ordinea:
            raise EroareContinuum(f"{unde} e configurată, dar lipsește din [continuum] „ordinea_nevoilor”")
        if not isinstance(n, dict):
            raise EroareContinuum(f"{unde} trebuie să fie o secțiune")
        nevoie: dict[str, Any] = {"nivel": _nivel(n, "nivel", unde)}
        if tip == "masoara":
            nevoie["timeout_secunde"] = _numar(n, "timeout_minute", unde, 1e-6) * 60
        else:
            nevoie["timeout_secunde"] = _numar(n, "timeout_ore", unde, 1e-6) * 3600
            nevoie["configurari"] = _texte(n, "configurari", unde)
        if tip == "continua":
            nevoie["capacitate"] = str(_cere(n, "capacitate", unde))
            nevoie["castig_minim"] = _numar(n, "castig_minim", unde)
        nevoi[tip] = nevoie

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
    }
