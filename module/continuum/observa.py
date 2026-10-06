"""OBSERVĂ (etapa 1): adună semnalele, fără excepții (secțiunea 4.1 din plan).

Ce nu se poate citi devine „indisponibil”, nu o eroare. Semnalele:
- **din jurnalul Kronos**, doar citit: toate fișele;
- **de la sistem**:
  - butonul STOP, același fișier ca la paznic;
  - placa video, prin nvidia-smi: temperatura, memoria și programele care o folosesc;
- **de la om**: de câte minute n-a mai atins tastatura sau mouse-ul (Windows), și ora;
- **de la module**, cele din [module]:
  - dacă se încarcă: sunt descoperite la pornire și la fiecare K cicluri, cu fișierul verificat la fiecare ciclu;
  - ce spun `sanatate()` și `semnale()`, dacă le oferă (opțional);
- **din hrană**: câte povești are fiecare dosar din [hrana] și când s-a schimbat ultima oară;
- **din configurările Kronos urmărite**: linia, câte ore are planificate, arhitectura și ce dosare pomenește.

Despre `sanatate()` și `semnale()`: un modul le oferă ca metode de clasă (classmethod sau staticmethod). CONTINUUM nu
creează instanțe și nu încarcă modele, ca să nu ocupe memoria sau placa.
"""

from __future__ import annotations

import glob
import importlib
import json
import shutil
import subprocess
import sys
import tomllib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from kronos.config import citeste_config as citeste_config_kronos
from kronos.jurnal import Jurnal
from kronos.paznic import Paznic
from kronos.registru import CHEI_MANIFEST

ARHITECTURA = ("n_straturi", "n_capete", "n_emb", "context")


# --- senzorii din afara fișierelor ---------------------------------------------------------------------------------

def citeste_placa(rulare: Callable[..., Any] = subprocess.run) -> dict[str, Any]:
    """Temperatura, memoria video și programele care folosesc placa (nvidia-smi, ca paznicul)."""
    if shutil.which("nvidia-smi") is None:
        return {"stare": "indisponibil", "eroare": "nvidia-smi nu există"}
    try:
        iesire = rulare(["nvidia-smi", "--query-gpu=temperature.gpu,memory.used,memory.total",
                         "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=10, check=True).stdout
        temperatura, folosita, totala = (float(x) for x in iesire.strip().splitlines()[0].split(","))
    except (subprocess.SubprocessError, OSError, ValueError, IndexError) as e:
        return {"stare": "indisponibil", "eroare": f"{type(e).__name__}: {e}"}
    placa: dict[str, Any] = {"stare": "ok", "temperatura": temperatura, "memorie_folosita_mb": folosita,
                             "memorie_totala_mb": totala, "memorie_libera_mb": totala - folosita}
    try:
        iesire = rulare(["nvidia-smi", "--query-compute-apps=pid,process_name", "--format=csv,noheader"],
                        capture_output=True, text=True, timeout=10, check=True).stdout
        placa["procese"] = [{"pid": int(pid), "nume": nume.strip()}
                            for pid, _, nume in (r.partition(",") for r in iesire.strip().splitlines() if r.strip())]
    except (subprocess.SubprocessError, OSError, ValueError) as e:
        placa["procese"] = None  # nu știm; rămâne memoria liberă
        placa["eroare_procese"] = f"{type(e).__name__}: {e}"
    return placa


def minute_de_la_ultima_atingere() -> float | None:
    """Windows: de câte minute n-a mai atins nimeni tastatura sau mouse-ul. None în afara Windows sau într-un proces
    fără ecran (sesiunea 0), unde Windows nu vede tastatura omului."""
    if sys.platform != "win32":
        return None
    import ctypes
    from ctypes import wintypes

    class UltimaAtingere(ctypes.Structure):
        _fields_ = [("cbSize", wintypes.UINT), ("dwTime", wintypes.DWORD)]

    kernel32, user32 = ctypes.windll.kernel32, ctypes.windll.user32
    sesiune = wintypes.DWORD()
    if not kernel32.ProcessIdToSessionId(kernel32.GetCurrentProcessId(), ctypes.byref(sesiune)) or sesiune.value == 0:
        return None
    info = UltimaAtingere()
    info.cbSize = ctypes.sizeof(info)
    if not user32.GetLastInputInfo(ctypes.byref(info)):
        return None
    kernel32.GetTickCount.restype = wintypes.DWORD
    return ((kernel32.GetTickCount() - info.dwTime) & 0xFFFFFFFF) / 60000


def citeste_omul() -> dict[str, Any]:
    minute = minute_de_la_ultima_atingere()
    if minute is None:
        return {"stare": "indisponibil", "eroare": "nu văd tastatura și mouse-ul (alt sistem sau proces fără ecran)"}
    return {"stare": "ok", "minute_de_la_ultima_atingere": round(minute, 1)}


@dataclass
class Senzori:
    """De unde vin semnalele din afara fișierelor. Testele pun aici semnale de probă, fără placă video."""
    acum: Callable[[], datetime] = datetime.now
    placa: Callable[[], dict[str, Any]] = citeste_placa
    om: Callable[[], dict[str, Any]] = citeste_omul


# --- modulele --------------------------------------------------------------------------------------------------------

@dataclass
class ModulDescoperit:
    info: dict[str, Any]  # ce intră în jurnal: stare, cale, nume, port, versiune (sau eroarea)
    obiect: Any = None    # clasa (sau fișierul, pentru o bibliotecă): doar pentru sanatate() și semnale()
    sursa: str = ""       # fișierul modulului: dacă dispare, modulul devine indisponibil chiar din ciclul următor


def descopera_modul(cale: str) -> ModulDescoperit:
    """„pachet.fisier:Clasa” (cu MANIFEST, ca în registrul Kronos, dar fără instanță) sau „pachet.fisier”."""
    nume_fisier, _, nume_clasa = cale.partition(":")
    try:
        importlib.invalidate_caches()
        fisier = importlib.import_module(nume_fisier)
        sursa = getattr(fisier, "__file__", None)
        if sursa and not Path(sursa).exists():
            return ModulDescoperit({"stare": "indisponibil", "cale": cale, "eroare": f"fișierul {sursa} nu mai există"})
        if not nume_clasa:
            return ModulDescoperit({"stare": "ok", "cale": cale}, fisier, sursa or "")
        clasa = getattr(fisier, nume_clasa, None)
        if clasa is None:
            return ModulDescoperit({"stare": "indisponibil", "cale": cale,
                                    "eroare": f"în „{nume_fisier}” nu există clasa „{nume_clasa}”"})
        manifest = getattr(clasa, "MANIFEST", None)
        if not isinstance(manifest, dict) or any(c not in manifest for c in CHEI_MANIFEST):
            return ModulDescoperit({"stare": "indisponibil", "cale": cale, "eroare": "n-are fișa MANIFEST completă"})
        return ModulDescoperit({"stare": "ok", "cale": cale, "nume": str(manifest["nume"]),
                                "port": str(manifest["port"]), "versiune": str(manifest["versiune"])}, clasa, sursa or "")
    except Exception as e:  # noqa: BLE001 - orice eroare la încărcare e o problemă a modulului, nu a buclei
        return ModulDescoperit({"stare": "indisponibil", "cale": cale, "eroare": f"{type(e).__name__}: {e}"})


def descopera_module(config: dict[str, Any]) -> dict[str, ModulDescoperit]:
    return {nume: descopera_modul(cale) for nume, cale in config["module"].items()}


def sanatatea(modul: ModulDescoperit) -> dict[str, Any]:
    """Starea modulului în acest ciclu: fișierul mai există? Ce spun sanatate() și semnale(), dacă le oferă?"""
    info = dict(modul.info)
    if info.get("stare") != "ok":
        return info
    if modul.sursa and not Path(modul.sursa).exists():
        return {**info, "stare": "indisponibil", "eroare": f"fișierul {modul.sursa} nu mai există"}
    for metoda in ("sanatate", "semnale"):
        functie = getattr(modul.obiect, metoda, None)
        if not callable(functie):
            continue
        try:
            raspuns = functie()
        except Exception as e:  # noqa: BLE001 - un modul care cade nu oprește bucla
            return {**info, "stare": "cazut", "eroare": f"{metoda}(): {type(e).__name__}: {e}"}
        info[metoda] = raspuns
    stare = (info.get("sanatate") or {}).get("stare") if isinstance(info.get("sanatate"), dict) else None
    if stare in ("degradat", "cazut"):
        info["stare"] = stare
    return info


# --- hrana și configurările Kronos -----------------------------------------------------------------------------------

def citeste_hrana(config: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Pentru fiecare capacitate cu hrană: câte povești au rămas (info.json, scris de profesor) și când s-a schimbat."""
    rezultat = {}
    for capacitate, h in config["hrana"].items():
        dosar = Path(h["dosar"])
        try:
            info = json.loads((dosar / "info.json").read_text(encoding="utf-8"))
            schimbat = max(f.stat().st_mtime for f in dosar.iterdir() if f.is_file())
            rezultat[capacitate] = {"stare": "ok", "dosar": h["dosar"], "povesti": int(info["ramase"]),
                                    "scrise": int(info.get("scrise", info["ramase"])),
                                    "schimbata": datetime.fromtimestamp(schimbat, tz=timezone.utc).isoformat(timespec="seconds")}
        except (OSError, ValueError, KeyError, TypeError) as e:
            rezultat[capacitate] = {"stare": "indisponibil", "dosar": h["dosar"], "eroare": f"{type(e).__name__}: {e}"}
    return rezultat


def _texte_din(valoare: Any) -> set[str]:
    if isinstance(valoare, str):
        return {valoare.replace("\\", "/")}
    if isinstance(valoare, dict):
        return set().union(*(_texte_din(v) for v in valoare.values())) if valoare else set()
    if isinstance(valoare, list):
        return set().union(*(_texte_din(v) for v in valoare)) if valoare else set()
    return set()


def citeste_configurari(globuri: list[str]) -> dict[str, dict[str, Any]]:
    """Configurările Kronos care se potrivesc cu globurile date (ex. config/laptop_antrenare_lunga*.toml)."""
    rezultat = {}
    for tipar in globuri:
        for cale in sorted(glob.glob(tipar)):
            cheie = Path(cale).as_posix()
            if cheie in rezultat:
                continue
            try:
                kronos = citeste_config_kronos(cale)
                with open(cale, "rb") as f:
                    brut = tomllib.load(f)
                model = kronos.setari_port("model")
                rezultat[cheie] = {"stare": "ok", "linie": kronos.nume, "ore_planificate": kronos.experimente,
                                   "arhitectura": {k: model[k] for k in ARHITECTURA if k in model},
                                   "de_la_zero": bool(model.get("de_la_zero", False)),
                                   "texte": sorted(_texte_din(brut.get("porturi", {})))}
            except Exception as e:  # noqa: BLE001 - o configurare stricată nu oprește observarea
                rezultat[cheie] = {"stare": "indisponibil", "eroare": f"{type(e).__name__}: {e}"}
    return rezultat


# --- observația întreagă ---------------------------------------------------------------------------------------------

@dataclass
class Observatie:
    timp: datetime
    stop: bool
    placa: dict[str, Any]
    om: dict[str, Any]
    module: dict[str, dict[str, Any]]
    hrana: dict[str, dict[str, Any]]
    configurari: dict[str, dict[str, Any]]
    jurnal: dict[str, Any]                                  # {"stare", "fise", "ultimul_id"} sau eroarea
    fise: list[dict[str, Any]] = field(default_factory=list)  # fișele Kronos; nu intră în jurnalul ciclurilor

    def rezumat(self) -> dict[str, Any]:
        """Ce intră în jurnalul ciclurilor. Hrana și configurările intră prin EVALUEAZĂ (cu ce s-a dedus din ele), iar
        din jurnalul Kronos doar câte fișe sunt."""
        return {"stop": self.stop, "placa": self.placa, "om": self.om, "module": self.module, "jurnal": self.jurnal}


def _sigur(functie: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    try:
        return functie()
    except Exception as e:  # noqa: BLE001 - un senzor care cade dă „indisponibil”
        return {"stare": "indisponibil", "eroare": f"{type(e).__name__}: {e}"}


def globuri_urmarite(config: dict[str, Any]) -> list[str]:
    """Configurările Kronos pe care le citește: liniile urmărite și cele pe care le pot porni nevoile."""
    globuri = list(config["linii"]["configurari"])
    for nevoie in config["nevoi"].values():
        globuri += [g for g in nevoie.get("configurari", []) if g not in globuri]
    return globuri


def observa(config: dict[str, Any], module: dict[str, ModulDescoperit], senzori: Senzori) -> Observatie:
    director = config["continuum"]["director_lucru"]
    try:
        fise = Jurnal(director).istoric()
        jurnal = {"stare": "ok", "fise": len(fise), "ultimul_id": max((f.get("id", 0) for f in fise), default=0)}
    except Exception as e:  # noqa: BLE001
        fise, jurnal = [], {"stare": "indisponibil", "eroare": f"{type(e).__name__}: {e}"}
    return Observatie(
        timp=senzori.acum(),
        stop=Paznic({}, director).oprire_ceruta(),
        placa=_sigur(senzori.placa),
        om=_sigur(senzori.om),
        module={nume: sanatatea(m) for nume, m in module.items()},
        hrana=citeste_hrana(config),
        configurari=citeste_configurari(globuri_urmarite(config)),
        jurnal=jurnal,
        fise=fise,
    )
