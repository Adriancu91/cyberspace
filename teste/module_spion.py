"""Un model „spion” pentru teste: spune în statistici dacă a primit memoria de la orchestrator."""


class ModelSpion:
    MANIFEST = {"nume": "model_spion", "port": "model", "versiune": "0", "versiune_contract": 1}

    def __init__(self, **_):
        self.memorie = None

    def conecteaza_memorie(self, memorie):
        self.memorie = memorie

    def antreneaza(self, date, buget_secunde):
        return {"memorie_conectata": self.memorie is not None, "nivele": getattr(self.memorie, "nivele", None)}

    def biti_pentru(self, text):
        return float(len(text))

    def genereaza(self, inceput, lungime):
        return " " * lungime

    def salveaza(self, cale):
        return cale

    def incarca(self, cale):
        pass
