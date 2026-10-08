"""Mediul școlii de cod: ce vede modelul și ce se ia din ce scrie (planul, secțiunea 3).

- **Abecedarul** (date/cod/abecedar.txt, scris de unelte/fa_abecedar.py): preambulul, cu regula lui Adrian cuvânt cu
  cuvânt, apoi 105 episoade TEST → WRITE → RESULT → passed. Fiecare episod primește nivelul lui pe scară, după cod
  (nivelul_codului).
- **Textul din față** la un test: [regula] + câteva episoade din abecedar (de la nivelul testului sau mai jos, alese
  aleator, niciodată sarcina testată) + „TEST: <sarcina>\\nWRITE:\\n”.
  - Modelul vede cel mult `context` simboluri (256 la #252), iar preambulul lung are singur 129.
  - De aceea episoadele se pun doar cât încap, lăsând loc pentru ce generează modelul (max_simboluri).
  - Câte au încăput se scrie în jurnal.
- **Regula** din față poate fi:
  - regula scurtată (varianta 3, aleasă de Adrian): aceeași și în textul de pregătire și antrenare (text_cu_regula),
    ca modelul să vadă la test ce a văzut la antrenare;
  - preambulul lung (varianta 1);
  - niciuna (varianta 2).

  Regula lungă rămâne oricum în fișierul abecedarului, ca document.
- **Încercarea** e textul dintre „WRITE:” și „RESULT:”. Dacă modelul n-a ajuns la „RESULT:”, se taie la primul „TEST:”
  sau „passed” nou, ori la final.
- **Scheletul** unui cod: numerele, cuvintele dintre ghilimele și numele cutiilor puse deoparte („x = 7” → „V = N”).
  Așa se vede dacă o soluție are o formă care nu e în abecedar.
"""

from __future__ import annotations

import keyword
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from module.cod import ordinea

CAP_EXEMPLE = "EXAMPLES:\n\n"


@dataclass(frozen=True)
class Episod:
    test: str
    cod: str
    rezultat: str
    nivel: str

    def text(self) -> str:
        return f"TEST: {self.test}\nWRITE:\n{self.cod}\nRESULT:\n{self.rezultat}\npassed\n"


@dataclass
class Abecedar:
    preambul: str           # regula lui Adrian, cuvânt cu cuvânt (fără „EXAMPLES:”)
    episoade: list[Episod]
    text: str               # tot fișierul, pentru pregătire și antrenare


def nivelul_codului(cod: str) -> str:
    """Nivelul unui cod corect pe scara v0.1 (pentru episoadele abecedarului)."""
    if re.search(r"\bdef\b", cod):
        return "7"
    if re.search(r"\bfor\b", cod):
        return "6"
    if re.search(r"\bif\b", cod):
        return "5.5"
    if re.search(r"[<>]|==", cod):
        return "5"
    atribuiri = re.findall(r"^\s*([A-Za-z_]\w*)\s*=(?!=)\s*(.*)$", cod, re.M)
    afisari = [linie for linie in cod.splitlines() if linie.strip().startswith("print(")]
    if atribuiri:
        if '"' in cod:
            return "4.5"  # cutii cu cuvinte
        cutii = {nume for nume, _ in atribuiri}
        cu_cutii_in_dreapta = any(re.search(r"[A-Za-z_]", dreapta) for _, dreapta in atribuiri)
        if len(cutii) >= 3 or cu_cutii_in_dreapta or len(afisari) > 1:
            return "4"
        return "3B" if len(cutii) == 2 else "3A"
    if afisari:
        interior = cod[cod.index("print(") + 6:]
        if '"' in interior and re.search(r"[+*\[]|len\(", interior):
            return "4.5"  # operații cu cuvinte
        operatori = set(re.findall(r"[+\-*]", interior))
        if not operatori:
            return "2A"
        return "2B" if operatori == {"+"} else "2C"
    return "1" if re.search(r"[+\-*]", cod) else "0"


def citeste_abecedar(cale: str | Path) -> Abecedar:
    text = Path(cale).read_text(encoding="utf-8")
    preambul, rest = text.split("EXAMPLES:", 1)
    episoade = []
    for bloc in re.split(r"\n[ \t]*\n", rest):
        bloc = bloc.strip("\n")
        m = re.fullmatch(r"TEST: (.*?)\nWRITE:\n(.*?)\nRESULT:\n(.*?)\npassed", bloc, re.S)
        if m:
            episoade.append(Episod(m.group(1), m.group(2), m.group(3), nivelul_codului(m.group(2))))
    return Abecedar(preambul.rstrip("\n") + "\n", episoade, text)


def _cap(regula: str) -> str:
    return (regula.rstrip("\n") + "\n\n" + CAP_EXEMPLE) if regula else CAP_EXEMPLE


def text_cu_regula(abecedar: Abecedar, regula: str) -> str:
    """Abecedarul cu `regula` în locul preambulului, în același format ca fișierul: textul de pregătire și antrenare.
    Cu preambulul lui, e exact fișierul."""
    return _cap(regula) + "\n".join(e.text() for e in abecedar.episoade)


def text_fata(abecedar: Abecedar, sarcina: str, nivel: str, rng: random.Random, numara: Callable[[str], int],
              context: int, max_simboluri: int, regula: str, max_episoade: int = 2) -> tuple[str, list[Episod]]:
    """(textul din fața modelului, episoadele puse). `regula` = textul de deasupra exemplelor („” = fără regulă).
    `numara(text)` = câte simboluri are textul (tokenizer-ul modelului). Episoadele (cel mult max_episoade) se pun doar
    dacă textul + max_simboluri încap în context; unul prea lung se sare și se încearcă următorul."""
    cap = _cap(regula)
    coada = f"TEST: {sarcina}\nWRITE:\n"
    candidati = [e for e in abecedar.episoade if ordinea(e.nivel) <= ordinea(nivel) and e.test != sarcina]
    rng.shuffle(candidati)
    alese: list[Episod] = []
    for episod in candidati:
        if len(alese) >= max_episoade:
            break
        if numara(cap + "".join(e.text() + "\n" for e in alese + [episod]) + coada) + max_simboluri <= context:
            alese.append(episod)
    return cap + "".join(e.text() + "\n" for e in alese) + coada, alese


def incercarea(generat: str) -> tuple[str, bool]:
    """(codul încercat, dacă modelul a ajuns la „RESULT:”). Se taie la primul „RESULT:”, „TEST:” sau „passed” nou."""
    capete = [i for i in (generat.find("RESULT:"), generat.find("\nTEST:"), generat.find("\npassed")) if i >= 0]
    taiat = generat[:min(capete)] if capete else generat
    return taiat.strip("\n").rstrip(), generat.find("RESULT:") >= 0 and generat.find("RESULT:") == min(capete or [-1])


def schelet(cod: str) -> str:
    """Forma codului: cuvintele dintre ghilimele → W, numerele → N, numele cutiilor → V (fără cuvintele lui Python și
    fără funcțiile lui de bază)."""
    forma = re.sub(r'"[^"]*"', "W", cod)
    forma = re.sub(r"\b\d+\b", "N", forma)
    rezervate = set(keyword.kwlist) | {"print", "len", "range", "W", "N"}
    return re.sub(r"\b[A-Za-z_]\w*\b", lambda m: m.group(0) if m.group(0) in rezervate else "V", forma)
