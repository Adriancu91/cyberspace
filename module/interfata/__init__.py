"""Interfața v0: un chat simplu în browser cu Kronos, accesibil doar de pe acest calculator și prin Tailscale.

Nu e un modul de port (portul „interfata” îl ocupă module/interfata_consola.py): e o aplicație separată, care
citește registrul Kronos ca să arate ce modul stă pe fiecare port. Nu pornește antrenări și nu scrie în jurnalul
Kronos; conversațiile ei stau într-o bază SQLite din lucru/interfata/.

    python -m module.interfata --config config/laptop_antrenare_lunga_8.toml --experiment 295 --port 8787

Piesele:
- retea.py      cine are voie să intre (127.0.0.1, ::1 și rețeaua Tailscale 100.64.0.0/10) și pe ce adrese ascultăm
- catalog.py    istoricul conversațiilor, în SQLite
- creiere.py    cine răspunde: CreierFals (de probă) sau CreierKronos (un model salvat de Kronos)
- module_ui.py  lista modulelor, din configurare + fișa MANIFEST a fiecărei clase
- server.py     serverul HTTP (doar biblioteca standard) și paginile din static/
"""

from __future__ import annotations

PORT_IMPLICIT = 8787
