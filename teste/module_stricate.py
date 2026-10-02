"""Module stricate intenționat: registrul trebuie să le refuze pe toate."""


class FaraManifest:
    def text_antrenare(self) -> str:
        return "x"

    def text_validare(self) -> str:
        return "x"


class PortGresit:
    MANIFEST = {"nume": "port_gresit", "port": "examen", "versiune": "0", "versiune_contract": 1}

    def text_antrenare(self) -> str:
        return "x"

    def text_validare(self) -> str:
        return "x"


class ContractVechi:
    MANIFEST = {"nume": "contract_vechi", "port": "date", "versiune": "0", "versiune_contract": 0}

    def text_antrenare(self) -> str:
        return "x"

    def text_validare(self) -> str:
        return "x"


class MetodaLipsa:
    MANIFEST = {"nume": "metoda_lipsa", "port": "date", "versiune": "0", "versiune_contract": 1}

    def text_antrenare(self) -> str:  # lipsește text_validare
        return "x"


class ModelCareCrapa:
    """Respectă contractul, dar crapă la antrenare: orchestratorul trebuie să-l anuleze."""

    MANIFEST = {"nume": "model_care_crapa", "port": "model", "versiune": "0", "versiune_contract": 1}

    def __init__(self, **_):
        pass

    def antreneaza(self, date, buget_secunde):
        raise RuntimeError("bum")

    def biti_pentru(self, text):
        return 1.0

    def genereaza(self, inceput, lungime):
        return " " * lungime

    def salveaza(self, cale):
        return cale

    def incarca(self, cale):
        pass
