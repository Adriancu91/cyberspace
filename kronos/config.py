"""Configurarea: citește din fișier ce modul stă pe fiecare port.

A schimba un modul = a schimba o linie într-un fișier .toml din folderul config/.
"""

from __future__ import annotations

import math
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .contracte import PORTURI


class EroareConfig(Exception):
    pass


@dataclass
class Config:
    cale_fisier: Path
    nume: str
    director_lucru: Path
    buget_antrenare_secunde: float
    experimente: int
    prag_zgomot: float
    paznic: dict[str, Any]
    porturi: dict[str, dict[str, Any]]  # port -> {"modul": str, "setari": dict}
    # Regula 4 (nou ≠ mai bun): criterii suplimentare la decizie, pe lângă scorul principal al examenului.
    # nume -> {"mai_mare_e_mai_bine": bool, "prag": cât poate scădea, cel mult, față de cel mai bun experiment păstrat}
    # Unul singur poate avea și "principal": True: atunci el hotărăște (trebuie să crească peste pragul lui), iar
    # scorul examenului devine un criteriu ca celelalte, cu pragul prag_zgomot.
    criterii: dict[str, dict[str, Any]] = field(default_factory=dict)
    # Linia pornește din modelul păstrat al acestui experiment (ex. --porneste-din la antrenarea lungă): până la primul ei
    # experiment păstrat, regula 4 o judecă față de scorurile acelui model, nu păstrează din oficiu primul experiment.
    porneste_din: int | None = None

    def setari_port(self, port: str) -> dict[str, Any]:
        return dict(self.porturi[port].get("setari", {}))

    def criteriu_principal(self) -> str | None:
        """Criteriul marcat principal = true în [criterii]; None: principalul e scorul examenului (ex. val_bpb)."""
        return next((nume for nume, regula in self.criterii.items() if regula.get("principal")), None)


def citeste_config(cale: str | Path) -> Config:
    cale = Path(cale)
    if not cale.exists():
        raise EroareConfig(f"Nu găsesc fișierul de configurare „{cale}”")
    try:
        with cale.open("rb") as f:
            brut = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise EroareConfig(f"„{cale}” are o greșeală de scriere: {e}") from e

    platforma = brut.get("platforma", {})
    porturi = brut.get("porturi", {})

    lipsa = [p for p in PORTURI if p not in porturi]
    if lipsa:
        raise EroareConfig(f"În „{cale}” lipsesc porturile: {', '.join(lipsa)}")
    necunoscute = [p for p in porturi if p not in PORTURI]
    if necunoscute:
        raise EroareConfig(f"În „{cale}” sunt porturi necunoscute: {', '.join(necunoscute)}")
    for port, valoare in porturi.items():
        if not isinstance(valoare, dict) or "modul" not in valoare:
            raise EroareConfig(f"Portul „{port}” din „{cale}” trebuie să aibă „modul = ...”")

    criterii = brut.get("criterii", {})
    if not isinstance(criterii, dict):
        raise EroareConfig(f"În „{cale}”, [criterii] trebuie să fie o secțiune: [criterii.<nume>]")
    for nume, regula in criterii.items():
        directie = regula.get("mai_mare_e_mai_bine") if isinstance(regula, dict) else None
        prag = regula.get("prag") if isinstance(regula, dict) else None
        if not isinstance(directie, bool) or isinstance(prag, bool) or not isinstance(prag, (int, float)) \
                or not math.isfinite(prag) or prag < 0:
            raise EroareConfig(
                f"În „{cale}”, criteriul „{nume}” trebuie să aibă mai_mare_e_mai_bine = true/false și prag = un număr ≥ 0"
            )
        if not isinstance(regula.get("principal", False), bool):
            raise EroareConfig(f"În „{cale}”, la criteriul „{nume}”, principal e true sau false")
    principale = [nume for nume, regula in criterii.items() if regula.get("principal")]
    if len(principale) > 1:
        raise EroareConfig(f"În „{cale}”, un singur criteriu poate fi principal (acum: {', '.join(principale)})")

    porneste_din = platforma.get("porneste_din")
    if porneste_din is not None and (isinstance(porneste_din, bool) or not isinstance(porneste_din, int)
                                     or porneste_din < 1):
        raise EroareConfig(f"În „{cale}”, porneste_din e numărul unui experiment din jurnal (un întreg ≥ 1)")

    director = Path(platforma.get("director_lucru", "lucru"))
    if not director.is_absolute():
        director = Path.cwd() / director

    return Config(
        cale_fisier=cale,
        nume=str(platforma.get("nume", cale.stem)),
        director_lucru=director,
        buget_antrenare_secunde=float(platforma.get("buget_antrenare_secunde", 20)),
        experimente=int(platforma.get("experimente", 5)),
        prag_zgomot=float(platforma.get("prag_zgomot", 0.002)),
        paznic=dict(brut.get("paznic", {})),
        porturi={p: dict(v) for p, v in porturi.items()},
        criterii={nume: {"mai_mare_e_mai_bine": r["mai_mare_e_mai_bine"], "prag": float(r["prag"]),
                         **({"principal": True} if r.get("principal") else {})}
                  for nume, r in criterii.items()},
        porneste_din=porneste_din,
    )
