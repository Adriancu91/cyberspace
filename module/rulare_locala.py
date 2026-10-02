"""Rulare pe calculatorul local (laptopul).

Execută o sarcină cu limită de timp și măsoară cât a durat și câtă
memorie video a folosit (dacă există PyTorch și o placă NVIDIA).

Limitare cunoscută: dacă o sarcină depășește timpul, o raportăm ca eșec,
dar Python nu poate opri forțat firul de execuție; modelele noastre
respectă oricum bugetul de timp primit.
"""

from __future__ import annotations

import threading
import time
import traceback
from typing import Any, Callable

from nucleu.contracte import RezultatRulare


def _torch_cuda():
    try:
        import torch

        return torch if torch.cuda.is_available() else None
    except ImportError:
        return None


class RulareLocala:
    MANIFEST = {
        "nume": "rulare_locala",
        "port": "rulare",
        "versiune": "0.1.0",
        "versiune_contract": 1,
        "resurse": {},
        "permisiuni": [],
    }

    def executa(self, functie: Callable[[], Any], limita_secunde: float) -> RezultatRulare:
        torch = _torch_cuda()
        if torch is not None:
            torch.cuda.reset_peak_memory_stats()

        rezultat: dict[str, Any] = {}

        def tinta() -> None:
            try:
                rezultat["valoare"] = functie()
            except BaseException as e:  # noqa: BLE001 - orice eroare devine eșecul experimentului
                rezultat["eroare"] = f"{type(e).__name__}: {e}"
                rezultat["urma"] = traceback.format_exc(limit=5)

        start = time.perf_counter()
        fir = threading.Thread(target=tinta, daemon=True)
        fir.start()
        fir.join(limita_secunde)
        durata = time.perf_counter() - start

        memorie = None
        if torch is not None:
            memorie = torch.cuda.max_memory_allocated() / 2**20
            if "eroare" in rezultat:
                torch.cuda.empty_cache()  # după o eroare (ex. memorie plină) eliberăm placa

        if fir.is_alive():
            return RezultatRulare(False, None, durata, memorie, f"a depășit limita de {limita_secunde:.0f} s")
        if "eroare" in rezultat:
            return RezultatRulare(False, None, durata, memorie, rezultat["eroare"])
        return RezultatRulare(True, rezultat.get("valoare"), durata, memorie)
