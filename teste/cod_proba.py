"""Ajutoare pentru testele școlii de cod: un worktree de probă și un elev scris de mână.

- **worktree_de_proba(tmp):** un dosar cu copiile fișierelor amprentate (generatorul de teste, sandbox-ul, abecedarul),
  un set sacru mic, configurarea reală cu numere mici și un lucru/ gol. Școala lucrează acolo, iar paznicul păzește
  copiile, nu fișierele adevărate.
- **ElevDeProba:** răspunde din soluțiile sarcinilor, ca un model care a învățat deja. Așa, testele pot verifica
  drumurile buclei: trecere, picare, regresie, trișat. Ține minte tot ce i s-a cerut.
"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any

from module.cod import PILOT
from module.cod.examen_cod import genereaza_sacru
from module.cod.mediu import citeste_abecedar

RADACINA = Path(__file__).resolve().parent.parent
GRESIT = 'print("nu stiu")'  # niciodată rezultatul așteptat


def config_din(text: str, schimbari: dict[str, Any]) -> str:
    """Textul configurării, cu valorile din `schimbari` ({"sectiune.cheie": valoare}) înlocuite."""
    ramase, linii, sectiune = dict(schimbari), [], None
    for rand in text.splitlines():
        antet = re.match(r"\[(\w+)\]\s*$", rand)
        cheie = re.match(r"(\w+)\s*=", rand)
        if antet:
            sectiune = antet.group(1)
        elif cheie and f"{sectiune}.{cheie.group(1)}" in ramase:
            rand = f"{cheie.group(1)} = {json.dumps(ramase.pop(f'{sectiune}.{cheie.group(1)}'), ensure_ascii=False)}"
        linii.append(rand)
    assert not ramase, f"chei necunoscute în configurare: {ramase}"
    return "\n".join(linii) + "\n"


def worktree_de_proba(tmp: Path, schimbari: dict[str, Any] | None = None, sacre_pe_nivel: int = 5) -> Path:
    """Întoarce calea configurării. Rădăcina e tmp/wt."""
    rad = tmp / "wt"
    for cale in ("module/cod/examen_cod.py", "module/cod/sandbox.py", "date/cod/abecedar.txt"):
        (rad / cale).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(RADACINA / cale, rad / cale)
    abecedar = citeste_abecedar(rad / "date/cod/abecedar.txt")
    sacru = genereaza_sacru({e.test for e in abecedar.episoade}, sacre_pe_nivel, samanta="test")
    (rad / "date/cod/sacru.json").write_text(json.dumps(sacru, ensure_ascii=False), encoding="utf-8")
    (rad / "date/povesti.txt").write_text("Once upon a time there was a little cat. " * 60, encoding="utf-8")
    valori = {"scoala.model_pornire": "lucru/cod/pornire/model.pt", "scoala.povesti": "date/povesti.txt",
              "scoala.caractere_povesti": 2000, "scoala.dispozitiv": "cpu", "sandbox.fire": 8,
              "examen.vazut": 6, "examen.nevazut": 5, "examen.adversarial": 5, "examen.sacru": sacre_pe_nivel,
              "examen.samanta_seturi": "test", "runda.incercari": 4, "runda.sarcini": 2, "runda.pasi_antrenare": 2,
              "runda.rata": 0.001, "runda.lot": 2, "pregatire.pasi": 2, "pregatire.rata": 0.001,
              "buget.runde_pe_nivel": 2, "pilot.niveluri": ["0", "1"], **(schimbari or {})}
    cale = rad / "config" / "scoala_cod.toml"
    cale.parent.mkdir(parents=True, exist_ok=True)
    cale.write_text(config_din((RADACINA / "config/scoala_cod.toml").read_text(encoding="utf-8"), valori),
                    encoding="utf-8")
    return cale


class ElevDeProba:
    """Un elev scris de mână: scrie soluția corectă a sarcinii, în afară de cele din `gresit`; `trisor` = scrie mereu
    cod interzis. Ține minte textele din față (cu sămânța și temperatura) și textele de antrenare."""

    context = 4096

    def __init__(self, solutii: dict[str, str]) -> None:
        self.solutii = solutii
        self.gresit: set[str] = set()
        self.trisor = False
        self.fete: list[tuple[str, int, float]] = []
        self.antrenari: list[str] = []

    def numara(self, text: str) -> int:
        return len(text) // 4

    def genereaza(self, fata: str, n: int, temperatura: float, max_simboluri: int, samanta: int) -> list[str]:
        self.fete.append((fata, samanta, temperatura))
        sarcina = fata.rsplit("TEST: ", 1)[1].split("\nWRITE:\n")[0]
        cod = "import os" if self.trisor else GRESIT if sarcina in self.gresit else self.solutii.get(sarcina, GRESIT)
        return [cod + "\nRESULT:"] * n

    def antreneaza(self, text: str, pasi: int, rata: float, lot: int, samanta: int) -> dict[str, Any]:
        self.antrenari.append(text)
        return {"pasi": pasi, "pierdere_finala": 1.0, "secunde": 0.0, "simboluri_text": len(text) // 4,
                "memorie_video_mb": 0}

    def salveaza(self, cale: str | Path) -> None:
        Path(cale).parent.mkdir(parents=True, exist_ok=True)
        Path(cale).write_text(json.dumps({"antrenari": len(self.antrenari)}), encoding="utf-8")

    def biti_pe_octet(self, text: str) -> float:
        return 1.5


def solutiile(scoala: Any, niveluri: tuple[str, ...] = PILOT) -> dict[str, str]:
    """Textul fiecărei sarcini (din toate seturile nivelurilor) → soluția ei."""
    return {s.text: s.solutie for n in niveluri for nume in ("vazut", "nevazut", "adversarial", "sacru")
            for s in getattr(scoala.seturi(n), nume)}
