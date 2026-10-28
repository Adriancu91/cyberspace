"""Registrul: știe ce modul ocupă fiecare port și verifică dacă are voie să intre.

Nucleul nu importă niciodată direct un modul. Primește din configurare
un text de forma "pachet.fisier:Clasa" și îl încarcă dinamic.
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass
from typing import Any

from .contracte import CONTRACT_PENTRU_PORT, PORTURI, PORTURI_OPTIONALE, VERSIUNE_CONTRACTE, membrii_contract

CHEI_MANIFEST = ("nume", "port", "versiune", "versiune_contract")


class EroareModul(Exception):
    """Un modul nu poate fi încărcat sau nu respectă contractul."""


@dataclass
class ModulIncarcat:
    port: str
    cale: str
    nume: str
    versiune: str
    setari: dict[str, Any]
    instanta: Any


class Registru:
    def __init__(self) -> None:
        self._module: dict[str, ModulIncarcat] = {}

    def creeaza(self, port: str, cale: str, setari: dict[str, Any] | None = None) -> ModulIncarcat:
        """Încarcă și verifică un modul, FĂRĂ să-l pună pe port."""
        setari = dict(setari or {})
        if port not in PORTURI + PORTURI_OPTIONALE:
            raise EroareModul(f"Portul „{port}” nu există. Porturi valide: {', '.join(PORTURI + PORTURI_OPTIONALE)}")
        if ":" not in cale:
            raise EroareModul(f"Calea „{cale}” trebuie să fie de forma pachet.fisier:Clasa")

        nume_fisier, nume_clasa = cale.split(":", 1)
        try:
            fisier = importlib.import_module(nume_fisier)
        except Exception as e:  # noqa: BLE001 - orice eroare de import e o problemă a modulului
            raise EroareModul(f"Nu pot importa „{nume_fisier}”: {type(e).__name__}: {e}") from e

        clasa = getattr(fisier, nume_clasa, None)
        if clasa is None:
            raise EroareModul(f"În „{nume_fisier}” nu există clasa „{nume_clasa}”")

        manifest = getattr(clasa, "MANIFEST", None)
        if not isinstance(manifest, dict):
            raise EroareModul(f"„{cale}” nu are fișa MANIFEST")
        lipsa = [c for c in CHEI_MANIFEST if c not in manifest]
        if lipsa:
            raise EroareModul(f"Fișa MANIFEST din „{cale}” nu are: {', '.join(lipsa)}")
        if manifest["port"] != port:
            raise EroareModul(
                f"„{cale}” e făcut pentru portul „{manifest['port']}”, nu pentru „{port}”"
            )
        if manifest["versiune_contract"] != VERSIUNE_CONTRACTE:
            raise EroareModul(
                f"„{cale}” cere contractul v{manifest['versiune_contract']}, "
                f"nucleul are v{VERSIUNE_CONTRACTE}"
            )

        try:
            instanta = clasa(**setari)
        except (TypeError, ValueError) as e:
            raise EroareModul(f"Setări greșite pentru „{cale}”: {e}") from e

        contract = CONTRACT_PENTRU_PORT[port]
        if not isinstance(instanta, contract):
            lipsesc = [m for m in membrii_contract(contract) if not hasattr(instanta, m)]
            raise EroareModul(
                f"„{cale}” nu respectă contractul portului „{port}”. Lipsesc: {', '.join(lipsesc)}"
            )

        return ModulIncarcat(
            port=port,
            cale=cale,
            nume=str(manifest["nume"]),
            versiune=str(manifest["versiune"]),
            setari=setari,
            instanta=instanta,
        )

    def pune(self, port: str, cale: str, setari: dict[str, Any] | None = None) -> Any:
        """Încarcă un modul și îl pune pe port. Întoarce instanța."""
        modul = self.creeaza(port, cale, setari)
        self._module[port] = modul
        return modul.instanta

    def ia(self, port: str) -> Any:
        if port not in self._module:
            raise EroareModul(f"Pe portul „{port}” nu e niciun modul")
        return self._module[port].instanta

    def info(self, port: str) -> ModulIncarcat:
        return self._module[port]

    def descriere(self) -> dict[str, dict[str, str]]:
        """Ce modul și ce versiune stă pe fiecare port (intră în jurnal)."""
        return {
            p: {"nume": m.nume, "versiune": m.versiune, "cale": m.cale}
            for p, m in sorted(self._module.items())
        }
