"""Contractele (porturile) platformei.

Un contract spune CE trebuie să știe să facă un modul, nu CUM.
Nucleul vorbește cu modulele doar prin aceste contracte, deci orice modul
care le respectă poate fi pus în locul altuia fără să schimbăm nucleul.

Reguli:
- Contractele se schimbă rar și doar cu aprobarea omului.
- La o schimbare incompatibilă crește VERSIUNE_CONTRACTE.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Protocol, runtime_checkable

VERSIUNE_CONTRACTE = 1

PORTURI = (
    "model",
    "date",
    "examen",
    "cercetator",
    "profesor",
    "rulare",
    "stocare",
    "interfata",
    "traducere",
    "memorie",
)


@dataclass
class Propunere:
    """O schimbare propusă de Cercetător.

    modificari: {port: {setare: valoare_noua}}, de ex. {"model": {"ordin": 3}}
    """

    descriere: str
    modificari: dict[str, dict[str, Any]] = field(default_factory=dict)


@dataclass
class RezultatRulare:
    """Ce întoarce portul Rulare după ce execută o sarcină."""

    reusit: bool
    valoare: Any
    durata_secunde: float
    memorie_gpu_max_mb: float | None = None
    eroare: str | None = None


@runtime_checkable
class Date(Protocol):
    """Sursa de text pentru antrenare și validare."""

    def text_antrenare(self) -> str: ...

    def text_validare(self) -> str: ...


@runtime_checkable
class Model(Protocol):
    """Modelul de limbaj, construit de la 0."""

    def antreneaza(self, date: Date, buget_secunde: float) -> dict[str, Any]:
        """Antrenează cel mult `buget_secunde` și întoarce statistici."""
        ...

    def biti_pentru(self, text: str) -> float:
        """Câți biți îi trebuie modelului ca să „ghicească” textul (mai puțin = mai bine)."""
        ...

    def genereaza(self, inceput: str, lungime: int) -> str:
        """Întoarce DOAR continuarea, de exact `lungime` caractere."""
        ...

    def salveaza(self, cale: str) -> str:
        """Salvează modelul; întoarce calea fișierului scris."""
        ...

    def incarca(self, cale: str) -> None: ...


@runtime_checkable
class Examen(Protocol):
    """Notează un model. Agentul NU are voie să-l modifice."""

    scor_principal: str
    mai_mic_e_mai_bun: bool

    def examineaza(self, model: Model, date: Date) -> dict[str, float]: ...


@runtime_checkable
class Cercetator(Protocol):
    """Citește istoricul și propune următoarea schimbare."""

    def propune(
        self, istoric: list[dict[str, Any]], setari_curente: dict[str, dict[str, Any]]
    ) -> Propunere: ...


@runtime_checkable
class Profesor(Protocol):
    """Generează exerciții (Faza 5). Deocamdată un modul gol."""

    def genereaza_exercitii(self, tema: str, numar: int) -> list[dict[str, str]]: ...


@runtime_checkable
class Rulare(Protocol):
    """Execută o sarcină cu limită de timp și măsoară consumul."""

    def executa(self, functie: Callable[[], Any], limita_secunde: float) -> RezultatRulare: ...


@runtime_checkable
class Stocare(Protocol):
    """Salvează și readuce fișiere (modele, rezultate)."""

    def cale_pentru(self, nume: str) -> str: ...

    def salveaza_json(self, nume: str, obiect: Any) -> str: ...

    def incarca_json(self, nume: str) -> Any | None: ...


@runtime_checkable
class Interfata(Protocol):
    """Arată oamenilor ce se întâmplă."""

    def anunta(self, eveniment: str, detalii: dict[str, Any]) -> None: ...


@runtime_checkable
class Traducere(Protocol):
    """Traduce text între limbi (ro <-> en)."""

    def traduce(self, text: str, din_limba: str, in_limba: str) -> str: ...


@runtime_checkable
class Memorie(Protocol):
    """Memoria ierarhică: unde stă fiecare cuvânt în bibliotecă și ce legături are.

    Modelele o primesc prin `conecteaza_memorie(memorie)`, dacă au această metodă.
    """

    nivele: int

    def caracteristici(self, text: str) -> list[tuple[int, ...]]:
        """Pentru fiecare literă: codul ultimului cuvânt TERMINAT până la ea (fără viitor)."""
        ...

    def cauta(self, cuvant: str) -> list[dict[str, Any]]: ...

    def statistici(self) -> dict[str, Any]: ...


CONTRACT_PENTRU_PORT: dict[str, type] = {
    "model": Model,
    "date": Date,
    "examen": Examen,
    "cercetator": Cercetator,
    "profesor": Profesor,
    "rulare": Rulare,
    "stocare": Stocare,
    "interfata": Interfata,
    "traducere": Traducere,
    "memorie": Memorie,
}


def membrii_contract(contract: type) -> list[str]:
    """Numele metodelor și atributelor cerute de un contract."""
    nume = [n for n in vars(contract) if not n.startswith("_")]
    nume += [n for n in getattr(contract, "__annotations__", {}) if not n.startswith("_")]
    return sorted(set(nume))
