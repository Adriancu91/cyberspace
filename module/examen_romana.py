"""Examenul de română (S90, C-85 pasul 3, 7 nov 2026): `romana_bpb` = biți pe octet pe validarea „română curat”.

Aceeași regulă și aceleași caractere ca `bpb_romana_curat` din `unelte/examen_validari_ws.py`: din fiecare din cele
trei validări curate (Wikipedia, web, cărți) primele `caractere` litere (implicit 100.000), tăiate la un text întreg
(`unelte/validari_text.py`), apoi media pe octeți a celor trei note `model.biti_pentru(text) / octeți`. Pe aceste
validări nu s-a antrenat nimic.

Opțional (`cu_r1 = true`, implicit oprit fiindcă e lent): **`r1_ascuns`** = nota automată R1 pe setul ascuns de 500
(`lucru/romana_raspunsuri/ascuns.jsonl`), ca `unelte/romana_raspunsuri.py reper`: modelul răspunde cu cel mult
`simboluri` bucăți (cea mai probabilă bucată), apoi nota (corect, în temă, limbă curată → media).

Protecția setului: amprentele SHA-256 ale celor trei validări și ale setului ascuns sunt scrise mai jos ca
constante; la fiecare `examineaza` modulul le recalculează și REFUZĂ (AmprentaGresita) dacă diferă. Altă cale de
fișier în setări cere și amprenta lui, scrisă tot în setări (o configurare schimbată se vede în Git).

Modulul NU e pus în nicio configurare. Ca orice examen, paznicul îi memorează amprenta la prima rulare; orice
schimbare oprește apoi experimentele până la `python -m kronos aproba-examen --config ...` (doar cu aprobarea omului).
`module/examen_bpb.py` nu se folosește și nu se atinge.
"""

from __future__ import annotations

import hashlib
import math
import time
from contextlib import nullcontext
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parent.parent

# numele din raport → validarea curată (aceleași ca grupa „romana_curat” din unelte/examen_validari_ws.py)
VALIDARI_ROMANA_CURAT = {
    "romana_wikipedia_curat": "date/ws/curat/wikipedia_ro/validare_curata.txt",
    "romana_web_curat": "date/ws/curat/fineweb2_ro/validare_curata.txt",
    "romana_carti_curat": "date/ws/curat/wikisource_ro/validare_curata.txt",
}
SET_ASCUNS = "lucru/romana_raspunsuri/ascuns.jsonl"
# SHA-256, calculate la 7 nov 2026 (S90); setul ascuns e cel din S76a (3a333657…)
AMPRENTE = {
    "date/ws/curat/wikipedia_ro/validare_curata.txt": "24916dc66a4ecbe738b05fd04060c4f31f73eab80c623d734f56f7cb8bb71054",
    "date/ws/curat/fineweb2_ro/validare_curata.txt": "9c5e4d2f6a15a3f7239d1277045d338fa07481bae6ad0b90292e6d559e953dcf",
    "date/ws/curat/wikisource_ro/validare_curata.txt": "9eaef8570113f456b9a97470155bb2bc6a1a388967d237f3e30930c8927bc78f",
    "lucru/romana_raspunsuri/ascuns.jsonl": "3a333657c91598d01d59418b244383e33d2c64f248c904b34f3af331bcb45c9e",
}


class AmprentaGresita(RuntimeError):
    """Un fișier al examenului nu mai are amprenta scrisă: examenul refuză să noteze."""


def sha256(cale: Path) -> str:
    h = hashlib.sha256()
    with Path(cale).open("rb") as f:
        for bucata in iter(lambda: f.read(1 << 20), b""):
            h.update(bucata)
    return h.hexdigest()


class ExamenRomana:
    MANIFEST = {
        "nume": "examen_romana",
        "port": "examen",
        "versiune": "0.1.0",
        "versiune_contract": 1,
        "resurse": {},
        "permisiuni": ["citire_fisier"],
    }

    scor_principal = "romana_bpb"
    mai_mic_e_mai_bun = True

    def __init__(self, caractere: int = 100_000, cu_r1: bool = False, simboluri: int = 64,
                 validari: dict[str, str] | None = None, set_ascuns: str = SET_ASCUNS,
                 amprente: dict[str, str] | None = None, radacina: str = "") -> None:
        if caractere < 100:
            raise ValueError("caractere trebuie să fie cel puțin 100")
        if simboluri < 1:
            raise ValueError("simboluri: cel puțin 1")
        self.caractere = caractere
        self.cu_r1 = bool(cu_r1)
        self.simboluri = simboluri
        self.radacina = Path(radacina) if radacina else RADACINA
        self.validari = dict(validari or VALIDARI_ROMANA_CURAT)
        if not self.validari:
            raise ValueError("validari: cel puțin o validare")
        self.set_ascuns = set_ascuns
        self.amprente = {**AMPRENTE, **(amprente or {})}
        de_pazit = list(self.validari.values()) + ([self.set_ascuns] if self.cu_r1 else [])
        fara = [c for c in de_pazit if c not in self.amprente]
        if fara:
            raise ValueError(f"fără amprentă SHA-256 scrisă: {fara} (o cale nouă cere și amprenta ei în setări)")

    def _cale(self, cale: str) -> Path:
        p = Path(cale)
        return p if p.is_absolute() else self.radacina / p

    def verifica_amprentele(self) -> dict[str, str]:
        """Recalculează SHA-256 pentru fiecare fișier folosit; refuză dacă unul lipsește sau diferă."""
        de_pazit = list(self.validari.values()) + ([self.set_ascuns] if self.cu_r1 else [])
        gasite: dict[str, str] = {}
        for cale in de_pazit:
            fisier = self._cale(cale)
            if not fisier.exists():
                raise AmprentaGresita(f"examen_romana: lipsește {cale}")
            gasite[cale] = sha256(fisier)
            if gasite[cale] != self.amprente[cale]:
                raise AmprentaGresita(f"examen_romana: {cale} s-a schimbat (SHA-256 {gasite[cale][:12]}…, "
                                      f"așteptat {self.amprente[cale][:12]}…) — refuz să notez")
        return gasite

    def examineaza(self, model: Any, date: Any) -> dict[str, float]:
        from unelte.validari_text import inceput_de_text

        inceput = time.perf_counter()
        self.verifica_amprentele()
        scoruri: dict[str, float] = {}
        biti_total = octeti_total = 0.0
        for nume, cale in self.validari.items():
            text = inceput_de_text(self._cale(cale), self.caractere)
            octeti = len(text.encode("utf-8"))
            bpb = float(model.biti_pentru(text)) / octeti if octeti else float("inf")
            scoruri[f"bpb_{nume}"] = bpb
            scoruri[f"octeti_{nume}"] = float(octeti)
            biti_total += bpb * octeti
            octeti_total += octeti
        romana = biti_total / octeti_total if octeti_total else float("inf")
        scoruri["romana_bpb"] = romana if math.isfinite(romana) else float("inf")
        scoruri["secunde_romana_bpb"] = round(time.perf_counter() - inceput, 2)
        if self.cu_r1:
            scoruri.update(self._r1(model))
        return scoruri

    def _r1(self, model: Any) -> dict[str, float]:
        from unelte.romana_raspunsuri import citeste, noteaza

        inceput = time.perf_counter()
        perechi = citeste(self._cale(self.set_ascuns))
        try:  # ca `reper`: fără gradienți (același răspuns, mai puțină memorie)
            import torch

            fara_gradienti: Any = torch.no_grad()
        except ImportError:
            fara_gradienti = nullcontext()
        with fara_gradienti:
            raspunsuri = {p["id"]: model.completeaza(p["prompt"], self.simboluri) for p in perechi}
        nota = noteaza(perechi, raspunsuri)
        return {"r1_ascuns": float(nota["scor_R1"]), "r1_instructiuni": float(nota["instructiuni"]["R1"]),
                "r1_vechi": float(nota["vechi"]["R1"]), "r1_intrebari": float(len(perechi)),
                "secunde_r1": round(time.perf_counter() - inceput, 2)}
