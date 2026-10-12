"""Lista modulelor pentru pagină: ce modul stă pe fiecare port, citit din registru.

Sursa e configurarea Kronos (ce clasă e pe fiecare port, de forma pachet.fisier:Clasa) plus fișa MANIFEST a fiecărei
clase (nume, port, versiune). Clasele sunt doar importate, NU se creează instanțe: nu se încarcă modele și nu se
citesc date. Un modul nou pus în configurare apare singur în pagină.
"""

from __future__ import annotations

import importlib
from typing import Any

from kronos.config import Config
from kronos.contracte import PORTURI

# Câmpuri opționale din MANIFEST pe care pagina le arată dacă există (planul interfeței, secțiunea 2).
CAMPURI_OPTIONALE = ("nume_afisat", "descriere")


def _manifest(cale: str) -> dict[str, Any]:
    """Fișa MANIFEST a clasei „pachet.fisier:Clasa”. Ridică ValueError cu un mesaj pe înțeles dacă nu se poate citi."""
    if ":" not in cale:
        raise ValueError(f"calea „{cale}” trebuie să fie de forma pachet.fisier:Clasa")
    nume_fisier, nume_clasa = cale.split(":", 1)
    try:
        fisier = importlib.import_module(nume_fisier)
    except Exception as e:  # noqa: BLE001 - orice eroare de import se arată în pagină, nu oprește interfața
        raise ValueError(f"nu pot importa „{nume_fisier}”: {type(e).__name__}: {e}") from e
    manifest = getattr(getattr(fisier, nume_clasa, None), "MANIFEST", None)
    if not isinstance(manifest, dict):
        raise ValueError(f"„{cale}” nu are fișa MANIFEST")
    return manifest


def lista_modulelor(config: Config) -> list[dict[str, Any]]:
    """Câte o intrare pentru fiecare port din configurare, în ordinea porturilor Kronos: portul, calea clasei și,
    din MANIFEST, numele și versiunea. Dacă fișa unui modul nu se poate citi, intrarea are câmpul „eroare”."""
    module: list[dict[str, Any]] = []
    for port in [p for p in PORTURI if p in config.porturi]:
        cale = str(config.porturi[port]["modul"])
        intrare: dict[str, Any] = {"port": port, "cale": cale, "nume": None, "versiune": None, "eroare": None}
        try:
            manifest = _manifest(cale)
            intrare["nume"] = str(manifest.get("nume", ""))
            intrare["versiune"] = str(manifest.get("versiune", ""))
            if manifest.get("port") != port:
                intrare["eroare"] = f"modulul e făcut pentru portul „{manifest.get('port')}”, nu pentru „{port}”"
            for camp in CAMPURI_OPTIONALE:
                if isinstance(manifest.get(camp), str):
                    intrare[camp] = manifest[camp]
        except ValueError as e:
            intrare["eroare"] = str(e)
        module.append(intrare)
    return module
