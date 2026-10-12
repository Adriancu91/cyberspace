"""Căile modelelor salvate, ca jurnalul să rămână bun și după mutarea proiectului pe alt calculator.

- Modelele noi se notează în jurnal cu calea relativă la proiect (folderul din care rulează Kronos).
- Fișele vechi au calea întreagă de pe calculatorul unde au fost scrise (de ex. laptopul). Jurnalul nu se schimbă:
  la citire, dacă fișierul nu e acolo, se caută după nume în stocarea de aici.
"""

from __future__ import annotations

from pathlib import Path, PureWindowsPath


def relativ_la_proiect(cale: str) -> str:
    """Calea de notat în jurnal: relativă la folderul proiectului, dacă fișierul e în el; altfel neschimbată."""
    try:
        return Path(cale).resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return cale


def gaseste_model(cale: str, director_lucru: str | Path = "lucru") -> str:
    """Calea de la care se încarcă un model notat în jurnal. Dacă fișierul din jurnal nu există aici, îl caută după
    numele fișierului în <director_lucru>/stocare/modele/. Dacă nu e nici acolo, întoarce calea din jurnal, ca eroarea
    să arate ce s-a căutat."""
    if Path(cale).exists():
        return cale
    nume = PureWindowsPath(cale).name  # desparte și la „\”, și la „/”
    aici = Path(director_lucru) / "stocare" / "modele" / nume
    return str(aici) if nume and aici.exists() else cale
