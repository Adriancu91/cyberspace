"""Interfața în consolă: scrie pe ecran ce se întâmplă, pe înțelesul omului."""

from __future__ import annotations

from datetime import datetime
from typing import Any

DECIZII = {"pastrat": "PĂSTRAT", "respins": "respins", "anulat": "ANULAT"}


class InterfataConsola:
    MANIFEST = {
        "nume": "interfata_consola",
        "port": "interfata",
        "versiune": "0.1.0",
        "versiune_contract": 1,
        "resurse": {},
        "permisiuni": [],
    }

    def __init__(self, detaliat: bool = False, tacut: bool = False) -> None:
        self.detaliat = detaliat
        self.tacut = tacut

    def _scrie(self, text: str) -> None:
        if not self.tacut:
            print(f"[{datetime.now():%H:%M:%S}] {text}", flush=True)

    def anunta(self, eveniment: str, detalii: dict[str, Any]) -> None:
        if eveniment == "start":
            scor = detalii.get("cel_mai_bun_scor")
            self._scrie(
                f"Pornesc „{detalii['configurare']}”: {detalii['experimente']} experimente. "
                + (f"Cel mai bun scor de până acum: {scor:.4f}" if scor is not None else "Primul start.")
            )
            for port, m in detalii.get("module", {}).items():
                self._scrie(f"   {port:<11} → {m['nume']} v{m['versiune']}")
        elif eveniment == "stare":
            if self.detaliat:
                self._scrie(f"   #{detalii['id']} {detalii['stare']}")
        elif eveniment == "experiment":
            scor = detalii.get("scor")
            scor_text = f"{scor:.4f}" if isinstance(scor, (int, float)) else "-"
            linie = f"#{detalii['id']:<3} {DECIZII.get(detalii['decizie'], detalii['decizie']):<8} scor {scor_text}  ← {detalii['propunere']}"
            self._scrie(linie)
            if detalii.get("decizie") == "anulat" and detalii.get("motiv"):
                self._scrie(f"      motiv: {detalii['motiv']}")
        elif eveniment == "racire":
            self._scrie(f"Pauză de răcire {detalii['pauza_secunde']:.0f} s: {detalii['motiv']}")
        elif eveniment in ("oprit", "gata"):
            self._scrie(f"Oprire: {detalii['motiv']}")
        elif eveniment == "final":
            scor = detalii.get("cel_mai_bun_scor")
            self._scrie(
                f"Gata. Experimente: {detalii['experimente_rulate']}, păstrate: {detalii['pastrate']}. "
                + (f"Cel mai bun scor: {scor:.4f}" if scor is not None else "")
            )
            self._scrie(f"Rețeta câștigătoare: {detalii['setari_castigatoare']}")
        else:
            self._scrie(f"{eveniment}: {detalii}")
