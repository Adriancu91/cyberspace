"""Memoria ierarhică: biblioteca de sensuri, cu coduri pe niveluri, relații și o plasă.

Cele trei straturi:
1. Biblioteca: fiecare SENS are un loc fix: parte de vorbire → raft (ex. noun.animal)
   → strămoșii lui din WordNet (organism → animal → ... → horse). Locul se scrie ca un
   cod pe niveluri, de ex. 1.7.1.2.3.38...
2. Relațiile: legături între sensuri: parte din, are parte, membru din, are membru, opus.
3. Plasa: ține minte drumurile deja căutate și de câte ori a fost folosit fiecare,
   ca a doua căutare a aceluiași cuvânt să meargă direct la țintă.

Ce primește modelul: pentru fiecare literă din text, codul ULTIMULUI CUVÂNT TERMINAT
până la ea. Niciodată cuvântul în curs de scriere: i-ar dezvălui literele care urmează,
adică ar trișa la examen. Testul test_memoria_nu_dezvaluie_viitorul verifică asta.

Biblioteca se construiește o singură dată: python unelte/construieste_biblioteca.py
"""

from __future__ import annotations

import gzip
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterator

GOL = 0  # nivel gol: încă niciun cuvânt terminat, sau codul cuvântului s-a terminat
NECUNOSCUT = 5  # pe primul nivel (partea de vorbire are 1-4): cuvânt care nu e în bibliotecă
VERSIUNE_BIBLIOTECA = 1

# Ca „morphy” din WordNet: terminație → înlocuire, pentru formele regulate pe care biblioteca
# nu le are (horses → horse, galloping → gallop), plus terminații vechi din Shakespeare.
TERMINATII = (
    ("'s", ""),
    ("ies", "y"), ("ses", "s"), ("xes", "x"), ("zes", "z"), ("ches", "ch"), ("shes", "sh"),
    ("men", "man"), ("es", "e"), ("es", ""), ("s", ""),
    ("ied", "y"), ("ed", "e"), ("ed", ""), ("ing", "e"), ("ing", ""),
    ("er", ""), ("er", "e"), ("est", ""), ("est", "e"),
    ("eth", ""), ("eth", "e"), ("'st", ""), ("st", ""), ("'d", "e"), ("'d", ""),
)


def _e_litera(c: str) -> bool:
    return c.isascii() and c.isalpha()


def _consoana_dubla(baza: str) -> bool:
    """„runn” (din running) → run, „stopp” (din stopped) → stop."""
    return len(baza) >= 3 and baza[-1] == baza[-2] and baza[-1] not in "aeiou"


class MemorieIerarhica:
    MANIFEST = {
        "nume": "memorie_ierarhica",
        "port": "memorie",
        "versiune": "0.1.2",
        "versiune_contract": 1,
        "resurse": {"ram_mb": 300},
        "permisiuni": ["citire_fisier"],
    }

    def __init__(self, cale: str = "date/biblioteca.json.gz", nivele: int = 12) -> None:
        if not 1 <= nivele <= 64:
            raise ValueError("nivele trebuie să fie între 1 și 64")
        fisier = Path(cale)
        if not fisier.exists():
            raise ValueError(
                f"Nu găsesc biblioteca „{cale}”. Construiește-o întâi: python unelte/construieste_biblioteca.py"
            )
        with gzip.open(fisier, "rt", encoding="utf-8") as f:
            biblioteca = json.load(f)
        if biblioteca.get("versiune") != VERSIUNE_BIBLIOTECA:
            raise ValueError(
                f"Biblioteca „{cale}” are versiunea {biblioteca.get('versiune')}, aștept {VERSIUNE_BIBLIOTECA}. "
                "Reconstruiește-o: python unelte/construieste_biblioteca.py"
            )
        self.nivele = nivele
        self.sursa: str = biblioteca["sursa"]
        self._parti: list[str] = biblioteca["parti_de_vorbire"]
        self._rafturi: list[str] = biblioteca["rafturi"]
        self.rafturi = self._rafturi  # public: raftul k din cod = rafturi[k - 1] (ex. plasa grupează nodurile pe rafturi)
        self._nume: list[str] = biblioteca["nume"]
        self._parinte: list[int] = biblioteca["parinte"]
        self._cod: list[list[int]] = biblioteca["cod"]
        self._forme: dict[str, list[int]] = biblioteca["forme"]
        self._relatii: dict[str, list[list[Any]]] = biblioteca["relatii"]
        # Plasa: cuvânt → codul deja găsit (drumul știut) și de câte ori a fost folosit.
        self._plasa: dict[str, tuple[int, ...]] = {}
        self._folosiri: Counter[str] = Counter()
        self._cautari = 0
        self._gasite = 0

    # --- căutarea în bibliotecă -----------------------------------------------

    def _sensuri(self, cuvant: str) -> list[int]:
        """Sensurile cuvântului (principalul primul); încearcă și forma de bază (horses → horse)."""
        cuvant = cuvant.lower().strip("'")
        if cuvant in self._forme:
            return self._forme[cuvant]
        for terminatie, inlocuire in TERMINATII:
            if cuvant.endswith(terminatie) and len(cuvant) - len(terminatie) >= 2:
                baza = cuvant[: -len(terminatie)]
                if baza + inlocuire in self._forme:
                    return self._forme[baza + inlocuire]
                if not inlocuire and _consoana_dubla(baza) and baza[:-1] in self._forme:
                    return self._forme[baza[:-1]]
        return []

    def _completeaza(self, cod: list[int]) -> tuple[int, ...]:
        cod = cod[: self.nivele]
        return tuple(cod) + (GOL,) * (self.nivele - len(cod))

    def _drum(self, sens: int) -> list[str]:
        drum: list[str] = []
        vazute: set[int] = set()
        while sens != -1 and sens not in vazute:
            vazute.add(sens)
            drum.append(self._nume[sens])
            sens = self._parinte[sens]
        return drum[::-1]

    # --- contractul -------------------------------------------------------------

    def cod(self, cuvant: str) -> tuple[int, ...]:
        """Codul sensului principal: exact `nivele` numere, completat cu 0 (GOL)."""
        cheie = cuvant.lower().strip("'")
        self._cautari += 1
        self._folosiri[cheie] += 1
        cod = self._plasa.get(cheie)
        if cod is None:  # drum nou: îl căutăm în bibliotecă și îl prindem în plasă
            sensuri = self._sensuri(cheie)
            cod = self._completeaza(self._cod[sensuri[0]] if sensuri else [NECUNOSCUT])
            self._plasa[cheie] = cod
        if cod[0] != NECUNOSCUT:
            self._gasite += 1
        return cod

    @staticmethod
    def _terminari(text: str) -> Iterator[tuple[int, str]]:
        """Cuvintele terminate, în ordine: (poziția semnului care încheie cuvântul, cuvântul).

        Un cuvânt = litere englezești, cu apostrof în interior (know'st). Se termină la primul
        semn care nu-l poate continua. Despre un apostrof după litere nu știm încă dacă e în
        interior (know'st) sau la final (horses'), așa că decidem la semnul următor; fiecare
        decizie folosește doar ce s-a scris deja. Cuvântul în curs, la finalul textului, nu intră.
        """
        inceput = -1  # unde a început cuvântul în curs (-1 = niciunul)
        apostrof = False  # semnul de dinainte a fost un apostrof după litere
        for i, c in enumerate(text):
            if _e_litera(c):
                if inceput < 0:
                    inceput = i
                apostrof = False
            elif c == "'" and inceput >= 0 and not apostrof:
                apostrof = True
            elif inceput >= 0:
                yield i, text[inceput:i]
                inceput, apostrof = -1, False

    def caracteristici(self, text: str) -> list[tuple[int, ...]]:
        """Pentru fiecare literă: codul ultimului cuvânt TERMINAT până la ea, inclusiv."""
        curent = (GOL,) * self.nivele
        rezultat: list[tuple[int, ...]] = []
        ultima = 0
        for pozitie, cuvant in self._terminari(text):
            rezultat.extend([curent] * (pozitie - ultima))  # până aici, codul cuvântului de dinainte
            curent = self.cod(cuvant)
            ultima = pozitie
        rezultat.extend([curent] * (len(text) - ultima))
        return rezultat

    def coduri_cuvinte(self, text: str) -> list[tuple[int, ...]]:
        """Codul fiecărui cuvânt terminat, în ordine (ex. pentru a vedea ce fel de cuvinte stau alături)."""
        return [self.cod(cuvant) for _, cuvant in self._terminari(text)]

    def cauta(self, cuvant: str) -> list[dict[str, Any]]:
        """Toate sensurile unui cuvânt, pentru oameni: cod, parte de vorbire, raft, drum, relații."""
        rezultat = []
        for sens in self._sensuri(cuvant):
            cod = self._cod[sens]
            rezultat.append({
                "cod": ".".join(str(x) for x in cod),
                "parte_de_vorbire": self._parti[cod[0] - 1],
                "raft": self._rafturi[cod[1] - 1],
                "drum": self._drum(sens),
                "relatii": [{"tip": tip, "catre": self._nume[tinta]} for tip, tinta in self._relatii.get(str(sens), [])],
            })
        return rezultat

    def statistici(self) -> dict[str, Any]:
        """Cât de des găsește memoria cuvintele căutate și ce ține minte plasa."""
        necunoscute = Counter(
            {c: n for c, n in self._folosiri.items() if self._plasa.get(c, (GOL,))[0] == NECUNOSCUT}
        )
        return {
            "cautari": self._cautari,
            "acoperire": round(self._gasite / self._cautari, 4) if self._cautari else 0.0,
            "drumuri_in_plasa": len(self._plasa),
            "cele_mai_folosite": [c for c, _ in self._folosiri.most_common(10)],
            "necunoscute_frecvente": [c for c, _ in necunoscute.most_common(10)],
        }
