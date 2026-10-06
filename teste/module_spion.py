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


class ModelCareInvataDupaExamen(ModelSpion):
    """Primește rezultatul examenului (doar numere) și îl întoarce, ca să-l vedem în jurnal."""

    def dupa_examen(self, rezultat):
        return {"am_primit": rezultat}


class ModelCuEroareDupaExamen(ModelSpion):
    def dupa_examen(self, rezultat):
        raise RuntimeError("bum după examen")


class ModelCuCriterii(ModelSpion):
    """Pentru regula 4: scorul (biți pe literă = val_bpb) și criteriile vin din setări; criteriile le dă prin dupa_examen."""

    def __init__(self, biti=5.0, fapte=10, nota=5.0, **_):
        super().__init__()
        self.biti, self.fapte, self.nota = biti, fapte, nota

    def biti_pentru(self, text):
        return self.biti * len(text.encode("utf-8"))

    def dupa_examen(self, rezultat):
        return {"am_primit": rezultat,
                "criterii": {"fapte_corecte": self.fapte, "nota_profesor": self.nota, "text": "nu e un număr"}}
