"""Creierele: cine răspunde în chat. Un creier are o etichetă (ca fiecare răspuns să spună cine l-a dat) și o
singură metodă, raspunde(text, lungime) -> str.

- CreierFals: de probă, pentru teste și pentru a încerca pagina fără niciun model. Răspunde mereu la fel la același
  text și spune deschis că e de probă.
- CreierKronos: un model salvat de Kronos, ales după numărul experimentului din jurnal. Se încarcă abia la prima
  întrebare (nu la pornire) și, implicit, pe procesor ("cpu"), ca placa video să rămână a antrenării.
- CreierText: ca CreierKronos, dar răspunde la o întrebare despre un paragraf dat (fila „Întreabă din text”).
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


class TextPreaLung(ValueError):
    """Paragraful cu tot cu întrebarea nu încape în fereastra modelului: se spune omului, nu se taie în tăcere."""

    def __init__(self, bucati: int, incap: int, fereastra: int) -> None:
        super().__init__(f"Textul cu tot cu întrebarea are {bucati} bucăți, dar în fereastra modelului ({fereastra} "
                         f"bucăți) încap cel mult {incap}, ca să rămână loc și de răspuns. Scurtează paragraful.")
        self.bucati = bucati
        self.incap = incap


class CreierText(CreierKronos):
    """Fila „Întreabă din text” (20 octombrie 2026, S5): modelul primește exact formatul de la antrenarea „răspuns din
    text” („Text: …⏎Întrebare: …⏎Răspuns:”), scrie cel mult `simboluri` bucăți fără întâmplare și se oprește la
    sfârșitul răspunsului (primul rând nou sau <|endoftext|>), ca la examen (unelte/examen_conversatie.py)."""

    def __init__(self, experiment: int, director_lucru: str | Path = "lucru", dispozitiv: str = "cpu",
                 simboluri: int = 80) -> None:
        super().__init__(experiment, director_lucru, dispozitiv)
        self.simboluri = int(simboluri)
        self.eticheta = f"Kronos #{self.experiment} — răspunde doar din textul dat."

    def raspunde_din_text(self, text: str, intrebare: str) -> str:
        from module.model_conversatie import intrebarea

        inceput = intrebarea(intrebare, text)
        with self._zavor:
            if self._model is None:
                self._model = self._incarca()
            fereastra = int(self._model.setari["context"])
            tok = getattr(self._model, "tok", None)
            bucati = len(tok.codifica(inceput)) if tok is not None else len(inceput)
            incap = fereastra - self.simboluri
            if bucati > incap:
                raise TextPreaLung(bucati, incap, fereastra)
            return taie(str(self._model.completeaza(inceput, self.simboluri)))


def taie(text: str) -> str:
    """Răspunsul până la primul rând nou sau la <|endoftext|> (ca la examenul de conversație)."""
    return text.split("<|endoftext|>")[0].strip().split("\n")[0].strip()


def _are_setarea_dispozitiv(cale: str) -> bool:
    """Are clasa modelului setarea „dispozitiv”? Modelele fără placă video (ex. n-gramul) n-o au și ar refuza-o;
    lor nu le-o dăm, că oricum lucrează doar pe procesor."""
    nume_fisier, _, nume_clasa = cale.partition(":")
    clasa = getattr(importlib.import_module(nume_fisier), nume_clasa)
    parametri = inspect.signature(clasa.__init__).parameters
    return "dispozitiv" in parametri or any(p.kind is p.VAR_KEYWORD for p in parametri.values())
