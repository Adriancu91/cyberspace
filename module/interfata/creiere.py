"""Creierele: cine răspunde în chat. Un creier are o etichetă (ca fiecare răspuns să spună cine l-a dat) și o
singură metodă, raspunde(text, lungime) -> str.

- CreierFals: de probă, pentru teste și pentru a încerca pagina fără niciun model. Răspunde mereu la fel la același
  text și spune deschis că e de probă.
- CreierKronos: un model salvat de Kronos, ales după numărul experimentului din jurnal. Se încarcă abia la prima
  întrebare (nu la pornire) și, implicit, pe procesor ("cpu"), ca placa video să rămână a antrenării.
"""

from __future__ import annotations

import importlib
import inspect
import threading
from pathlib import Path
from typing import Any, Protocol


class Creier(Protocol):
    """Oricine poate răspunde în chat."""

    eticheta: str

    def raspunde(self, text: str, lungime: int) -> str:
        """Răspunsul la `text`, de cel mult `lungime` caractere."""
        ...


class CreierFals:
    """Creier de probă: nu e niciun model în spate. Același text primește mereu același răspuns."""

    eticheta = "Creier de probă (nu e un model)"

    def raspunde(self, text: str, lungime: int) -> str:
        raspuns = f"[răspuns de probă] Am primit {len(text)} caractere: {text}"
        return raspuns[: max(0, int(lungime))]


class CreierKronos:
    """Elevul: modelul salvat de Kronos la experimentul dat. Răspunde continuând textul primit, cu
    model.genereaza(inceput, lungime), adică exact ce știe modelul, fără nicio înfrumusețare."""

    def __init__(self, experiment: int, director_lucru: str | Path = "lucru", dispozitiv: str = "cpu") -> None:
        self.experiment = int(experiment)
        self.director_lucru = Path(director_lucru)
        self.dispozitiv = dispozitiv
        self.eticheta = f"Kronos (elev, modelul #{self.experiment})"
        self._model: Any = None
        self._zavor = threading.Lock()  # un singur răspuns pe rând: modelul nu e făcut pentru mai multe fire

    @property
    def incarcat(self) -> bool:
        return self._model is not None

    def _incarca(self) -> Any:
        # Importurile sunt aici, nu sus, ca pornirea interfeței (și creierul fals) să nu încarce nimic greu.
        from kronos.jurnal import Jurnal
        from unelte.modele_salvate import fisa_modelului, incarca_modelul

        fisa = fisa_modelului(Jurnal(self.director_lucru), self.experiment)
        dispozitiv = self.dispozitiv if _are_setarea_dispozitiv(fisa["module"]["model"]["cale"]) else ""
        return incarca_modelul(fisa, dispozitiv)

    def raspunde(self, text: str, lungime: int) -> str:
        with self._zavor:
            if self._model is None:
                self._model = self._incarca()
            return str(self._model.genereaza(text, int(lungime)))


def _are_setarea_dispozitiv(cale: str) -> bool:
    """Are clasa modelului setarea „dispozitiv”? Modelele fără placă video (ex. n-gramul) n-o au și ar refuza-o;
    lor nu le-o dăm, că oricum lucrează doar pe procesor."""
    nume_fisier, _, nume_clasa = cale.partition(":")
    clasa = getattr(importlib.import_module(nume_fisier), nume_clasa)
    parametri = inspect.signature(clasa.__init__).parameters
    return "dispozitiv" in parametri or any(p.kind is p.VAR_KEYWORD for p in parametri.values())
