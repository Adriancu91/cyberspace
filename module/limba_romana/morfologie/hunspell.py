"""Cititor de dicționar Hunspell (.aff + .dic) și generator de forme, cu trasabilitate.

Nu depinde de biblioteca hunspell: interpretăm direct regulile SFX/PFX (strip, add, condiție) din `.aff`.
Fiecare formă generată vine cu regula care a produs-o (`SFX A 7`), ca să se poată verifica mai târziu.
Nu generăm formele cu prefix (re-, ne-, auto-): sunt derivări, nu flexiune (vezi ARHITECTURA.md), și nici
formele cu clitice lipite prin cratimă („ează-mă”): tokenizatorul desparte cliticele.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator


@dataclass
class RegulaAfix:
    tip: str            # SFX | PFX
    flag: str
    strip: str          # "" dacă „0”
    add: str            # "" dacă „0”
    conditie: str       # „.” = orice
    anotare: str        # textul de după condiție (de ex. „s.f.sg.art.”), gol dacă lipsește
    index: int          # poziția regulii în clasa ei (pentru trasabilitate)
    _re: re.Pattern | None = field(default=None, repr=False)

    def se_potriveste(self, cuvant: str) -> bool:
        if self.tip == "SFX":
            if self.strip and not cuvant.endswith(self.strip):
                return False
            if self._re is None:
                self._re = re.compile("(?:" + _conditie_regex(self.conditie) + ")$")
            return bool(self._re.search(cuvant))
        if self.strip and not cuvant.startswith(self.strip):
            return False
        if self._re is None:
            self._re = re.compile("^(?:" + _conditie_regex(self.conditie) + ")")
        return bool(self._re.search(cuvant))

    def aplica(self, cuvant: str) -> str:
        if self.tip == "SFX":
            baza = cuvant[: len(cuvant) - len(self.strip)] if self.strip else cuvant
            return baza + self.add
        baza = cuvant[len(self.strip):] if self.strip else cuvant
        return self.add + baza


def _conditie_regex(conditie: str) -> str:
    """Condițiile Hunspell sunt aproape regex: `.`, `[abc]`, `[^abc]`, litere. Le traducem literal, cu escape."""
    if conditie == ".":
        return ".?"
    bucati = []
    i = 0
    while i < len(conditie):
        c = conditie[i]
        if c == "[":
            j = conditie.index("]", i)
            bucati.append(conditie[i:j + 1])
            i = j + 1
        elif c == ".":
            bucati.append(".")
            i += 1
        else:
            bucati.append(re.escape(c))
            i += 1
    return "".join(bucati)


@dataclass
class Dictionar:
    reguli: dict[str, list[RegulaAfix]]           # flag → reguli
    cross: dict[str, bool]                         # flag → combinare cu prefixe (Y/N)
    intrari: list[tuple[str, str]]                 # (cuvânt, flaguri)
    comentarii_clase: dict[str, str]               # flag → descrierea din antet (dacă există)
    set_: str = "UTF-8"

    def forme(self, cuvant: str, flaguri: str, cu_prefixe: bool = False, cu_clitice: bool = False) -> Iterator[tuple[str, RegulaAfix]]:
        """Produce (formă, regulă) pentru fiecare sufix aplicabil. Cuvântul de bază nu e inclus."""
        for flag in flaguri:
            for r in self.reguli.get(flag, []):
                if r.tip == "PFX" and not cu_prefixe:
                    continue
                if not cu_clitice and "-" in r.add and "-" not in r.strip and "-" not in cuvant:
                    continue
                if r.se_potriveste(cuvant):
                    yield r.aplica(cuvant), r


def citeste(cale_aff: str | Path, cale_dic: str | Path) -> Dictionar:
    reguli: dict[str, list[RegulaAfix]] = {}
    cross: dict[str, bool] = {}
    comentarii: dict[str, str] = {}
    set_ = "UTF-8"
    ultimul_comentariu = ""
    with open(cale_aff, encoding="utf8") as f:
        for linie in f:
            linie = linie.rstrip("\n")
            if linie.startswith("#"):
                ultimul_comentariu = linie.lstrip("# ").strip()
                continue
            p = linie.split()
            if not p:
                continue
            if p[0] == "SET":
                set_ = p[1]
            elif p[0] in ("SFX", "PFX") and len(p) == 4 and p[2] in ("Y", "N"):
                cross[p[1]] = p[2] == "Y"
                reguli.setdefault(p[1], [])
                if ultimul_comentariu and not ultimul_comentariu.startswith("*"):
                    comentarii[p[1]] = ultimul_comentariu
            elif p[0] in ("SFX", "PFX") and len(p) >= 5:
                flag = p[1]
                strip = "" if p[2] == "0" else p[2]
                add = "" if p[3] == "0" else p[3]
                cond = p[4]
                anotare = " ".join(p[5:]).strip()
                if anotare.startswith("#") and ("?" in anotare or "verificat" in anotare):
                    anotare = ""  # comentarii ale autorilor, nu anotări
                lista = reguli.setdefault(flag, [])
                lista.append(RegulaAfix(p[0], flag, strip, add, cond, anotare, len(lista) + 1))
    intrari: list[tuple[str, str]] = []
    with open(cale_dic, encoding="utf8") as f:
        prima = f.readline()
        for linie in f:
            linie = linie.rstrip("\n")
            if not linie or linie.startswith("#"):
                continue
            if "/" in linie:
                cuvant, flaguri = linie.split("/", 1)
                flaguri = flaguri.split()[0] if flaguri else ""
            else:
                cuvant, flaguri = linie.split()[0], ""
            intrari.append((cuvant, flaguri))
    return Dictionar(reguli, cross, intrari, comentarii, set_)
