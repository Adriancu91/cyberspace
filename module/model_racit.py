"""Copia răcită a unei antrenări lungi cu rata constantă (13 octombrie 2026, rețeta liniei W2).

Linia principală învață cu rata de învățare constantă, oricâte nopți. La sfârșitul unei nopți, o COPIE a ei se „răcește”:
pornește din starea liniei (stare_de_pornire: greutățile, optimizatorul, numărul de pași), învață încă puțin (bugetul
experimentului, ex. 30 de minute) cu rata care scade LINIAR de la rata_invatare la rata_finala, apoi dă examenele.
Copia e „modelul zilei”. Starea liniei nu se scrie niciodată de aici: linia continuă din punctul de dinainte de răcire.

Ca model_continuu, cu trei deosebiri:
- cale_stare și director_stari nu sunt permise (nimic nu se scrie peste starea vreunei linii);
- rata scade liniar pe bugetul antrenării de acum, fără încălzire;
- statisticile spun „racit” și între ce rate.
Pornirea copiei: unelte/copie_racita.py (un experiment Kronos, pe o linie de jurnal separată).
"""

from __future__ import annotations

from typing import Any

from module.model_continuu import ModelGPTContinuu


class ModelGPTRacit(ModelGPTContinuu):
    MANIFEST = {
        "nume": "model_gpt_racit",
        "port": "model",
        "versiune": "0.1.0",
        "versiune_contract": 1,
        "resurse": {"gpu": True, "memorie_gpu_mb": 5500},
        "permisiuni": ["citire_fisier", "scriere_fisier"],
    }

    def __init__(self, rata_finala: float = 0.0, **setari: Any) -> None:
        super().__init__(**setari)
        if self.cale_stare or self.director_stari:
            raise ValueError("copia răcită nu scrie nicio stare: fără cale_stare și fără director_stari (starea liniei "
                             "se dă în stare_de_pornire, care doar se citește)")
        rata_finala = rata_finala or self.rata_invatare * 0.1
        if not 0 < rata_finala <= self.rata_invatare:
            raise ValueError("rata_finala e între 0 și rata_invatare")
        self.rata_finala = rata_finala
        self.rata_care_scade = True  # bucla de antrenare cere rata la fiecare pas

    def _progres(self, pasi: int, secunde_buget: float, secunde_bucla: float, buget_secunde: float) -> float:
        return secunde_buget / buget_secunde if buget_secunde > 0 else 1.0

    def rata_acum(self, pasi: int, progres: float) -> float:
        """Liniar: rata_invatare la început (progres 0), rata_finala la capăt (progres 1)."""
        return self.rata_invatare + (self.rata_finala - self.rata_invatare) * min(max(progres, 0.0), 1.0)

    def antreneaza(self, date: Any, buget_secunde: float) -> dict[str, Any]:
        statistici = super().antreneaza(date, buget_secunde)
        statistici.update(racit=True, rata_la_inceput=self.rata_invatare, rata_finala=self.rata_finala)
        return statistici
