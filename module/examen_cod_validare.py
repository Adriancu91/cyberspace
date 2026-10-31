"""Examenul de la fiecare oră al lui Kronos-Cod (S59): val_bpb = biți pe octet pe un eșantion FIX al validării de cod.

Folosește `unelte/kronos_cod/examen_validare.py` (aceeași regulă ca examenul întreg de după noapte): fiecare fișier se
notează singur, după simbolul de sfârșit de fișier, fiecare simbol o singură dată; biți pe octet = suma pierderilor
(nats) / ln 2 / suma octeților. Eșantionul: `fisiere` fișiere din cele 5.686 de validare, alese o singură dată cu
`samanta` (implicit 1.000 de fișiere, sămânța 0) — aceleași la fiecare oră și la fiecare rulare, deci orele se pot
compara între ele. Octeții unui fișier = textul lui decodat în UTF-8 (tokenizerul de cod dă înapoi exact textul, S55
(c): 5.686/5.686 identice), deci examenul nu mai citește `cod.jsonl`.

Examenul întreg (toate cele 5.686, pe tot și pe Python / Rust / C) rămâne pentru după noapte:
`python -m unelte.kronos_cod.examen_validare model ...`.

Pe date fără fișiere de validare (date pe text) sau pe un model fără rețea, examenul face ce face și examen_bpb:
biți pe octet pe începutul textului de validare, prin biti_pentru. `module/examen_bpb.py` nu se folosește și nu se atinge.

ATENȚIE: ca orice examen, paznicul îi memorează amprenta la prima rulare; orice schimbare oprește experimentele până la
`python -m kronos aproba-examen --config ...` (doar cu aprobarea omului).
"""

from __future__ import annotations

import math
import time
from contextlib import nullcontext
from typing import Any

import numpy as np


class ExamenCodValidare:
    MANIFEST = {
        "nume": "examen_cod_validare",
        "port": "examen",
        "versiune": "0.1.0",
        "versiune_contract": 1,
        "resurse": {},
        "permisiuni": ["citire_fisier"],
    }

    scor_principal = "val_bpb"
    mai_mic_e_mai_bun = True

    def __init__(self, fisiere: int = 1000, samanta: int = 0, lot: int = 8, max_caractere: int = 100_000) -> None:
        if fisiere < 1 or lot < 1:
            raise ValueError("fisiere și lot: cel puțin 1")
        if max_caractere < 100:
            raise ValueError("max_caractere trebuie să fie cel puțin 100")
        self.fisiere = fisiere
        self.samanta = samanta
        self.lot = lot
        self.max_caractere = max_caractere
        self._octeti: dict[tuple[int, str], list[int]] = {}  # (câte fișiere are validarea, tokenizerul) → octeții eșantionului

    def esantion(self, numar_fisiere: int) -> list[int]:
        """Numerele fișierelor din eșantion (în ordine): aceleași pentru aceeași validare, la fiecare rulare."""
        if self.fisiere >= numar_fisiere:
            return list(range(numar_fisiere))
        ales = np.random.default_rng(self.samanta).choice(numar_fisiere, size=self.fisiere, replace=False)
        return sorted(int(k) for k in ales)

    def _octeti_esantion(self, fisiere: list[np.ndarray], alese: list[int], date: Any) -> list[int]:
        cheie = (len(fisiere), date.cale_tokenizer)
        if cheie not in self._octeti:
            from module.tokenizer_bpe import TokenizerBPE

            tok = TokenizerBPE.incarca(date.cale_tokenizer)
            self._octeti[cheie] = [len(tok.decodeaza(int(x) for x in fisiere[k]).encode("utf-8")) for k in alese]
        return self._octeti[cheie]

    @staticmethod
    def pe_simboluri(model: Any, date: Any) -> bool:
        """Se poate nota pe fișierele de validare (date de cod cu tokenizer, model cu rețea)?"""
        return (callable(getattr(date, "fisiere_validare", None)) and bool(getattr(date, "cale_tokenizer", ""))
                and getattr(model, "retea", None) is not None)

    def examineaza(self, model: Any, date: Any) -> dict[str, float]:
        if not self.pe_simboluri(model, date):
            return self._pe_text(model, date)
        from unelte.kronos_cod import examen_validare as ev

        inceput = time.perf_counter()
        toate = date.fisiere_validare()
        alese = self.esantion(len(toate))
        fisiere = [toate[k] for k in alese]
        octeti = self._octeti_esantion(toate, alese, date)
        retea = model.retea
        retea.eval()
        def logits(x: Any) -> Any:
            with model._autocast() if hasattr(model, "_autocast") else nullcontext():
                return retea(x.to(model.dispozitiv))

        p = ev.pierderi(logits, fisiere, date.context, date.sfarsit_de_fisier, self.lot)
        tot = ev.biti_pe_octet(p, [len(f) for f in fisiere], [("?", o) for o in octeti])["tot"]
        return {"val_bpb": float(tot["biti_pe_octet"]), "fisiere_examinate": float(tot["fisiere"]),
                "simboluri_examinate": float(tot["simboluri"]), "octeti_examinati": float(tot["octeti"]),
                "pierdere_medie": float(tot["pierdere_medie"]),
                "secunde_examen": round(time.perf_counter() - inceput, 2)}

    def _pe_text(self, model: Any, date: Any) -> dict[str, float]:
        text = date.text_validare()[: self.max_caractere]
        biti = float(model.biti_pentru(text))
        octeti = len(text.encode("utf-8"))
        val_bpb = biti / octeti if octeti and math.isfinite(biti) else float("inf")
        return {"val_bpb": val_bpb, "caractere_examinate": float(len(text))}
