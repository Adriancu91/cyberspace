"""Serverul interfeței: pagina de chat și un API mic în JSON, doar cu biblioteca standard (http.server).

Ce răspunde:
    GET  /                        pagina de chat (static/index.html, cu aplicatie.js și stil.css)
    GET  /api/stare               cine răspunde (eticheta creierului) și limitele de lungime
    GET  /api/module              modulele din registru, câte unul pe port
    GET  /api/conversatii         lista conversațiilor
    GET  /api/conversatii/<nr>    mesajele unei conversații
    POST /api/mesaj               {"text": "...", "conversatie": nr sau null} → întrebarea și răspunsul, scrise în bază

Fiecare cerere trece întâi prin verificarea adresei (retea.adresa_permisa): cine nu e de pe acest calculator sau din
rețeaua Tailscale primește 403. Serverul nu pornește antrenări și nu atinge jurnalul Kronos.
"""

from __future__ import annotations

import json
import sys
import threading
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable

from . import retea
from .catalog import ROL_CREIER, ROL_OM, Catalog
from .creiere import Creier

DIRECTOR_STATIC = Path(__file__).resolve().parent / "static"
# Singurele fișiere servite din static/: calea din browser → (fișierul, tipul lui).
FISIERE_STATICE = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/aplicatie.js": ("aplicatie.js", "text/javascript; charset=utf-8"),
    "/stil.css": ("stil.css", "text/css; charset=utf-8"),
}
# Pagina are voie să încarce și să execute doar fișierele noastre: un text scris în chat nu poate deveni cod.
POLITICA_CONTINUT = ("default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; "
                     "base-uri 'none'; form-action 'none'; frame-ancestors 'none'")
LUNGIME_MAXIMA_MESAJ = 2000       # caractere scrise de om într-un mesaj
LUNGIME_RASPUNS_IMPLICITA = 200   # cât cere interfața de la creier, dacă nu se spune altfel
LUNGIME_RASPUNS_MAXIMA = 2000
OCTETI_MAXIMI_CERERE = 64 * 1024


class EroareCerere(Exception):
    """O cerere greșită: se întoarce clientului cu codul și mesajul date."""

    def __init__(self, cod: int, mesaj: str) -> None:
        super().__init__(mesaj)
        self.cod = cod
        self.mesaj = mesaj


class Aplicatie:
    """Tot ce știe interfața să facă, fără nimic despre HTTP: catalogul, creierul și lista modulelor."""

    def __init__(self, catalog: Catalog, creier: Creier, module: list[dict[str, Any]] | None = None,
                 configurare: str = "", lungime_raspuns: int = LUNGIME_RASPUNS_IMPLICITA) -> None:
        self.catalog = catalog
        self.creier = creier
        self.module = list(module or [])
        self.configurare = configurare
        self.lungime_raspuns = max(1, min(int(lungime_raspuns), LUNGIME_RASPUNS_MAXIMA))
        # Cine are voie să intre; se poate înlocui în teste.
        self.adresa_permisa: Callable[[str], bool] = retea.adresa_permisa

    def stare(self) -> dict[str, Any]:
        return {"creier": self.creier.eticheta, "configurare": self.configurare,
                "lungime_maxima_mesaj": LUNGIME_MAXIMA_MESAJ, "lungime_raspuns": self.lungime_raspuns}

    def lista_module(self) -> dict[str, Any]:
        return {"configurare": self.configurare, "module": self.module}

    def mesaje(self, conversatie: int) -> dict[str, Any]:
        if not self.catalog.exista(conversatie):
            raise EroareCerere(HTTPStatus.NOT_FOUND, f"Conversația #{conversatie} nu există.")
        return {"conversatie": conversatie, "mesaje": self.catalog.mesaje(conversatie)}

    def mesaj_nou(self, cerere: Any) -> dict[str, Any]:
        """Scrie întrebarea omului în bază, cere răspunsul creierului și îl scrie și pe el, cu eticheta creierului
        și timpul de răspuns. Dacă creierul dă o eroare, întrebarea rămâne în bază, iar eroarea se spune cinstit."""
        if not isinstance(cerere, dict):
            raise EroareCerere(HTTPStatus.BAD_REQUEST, "Cererea trebuie să fie un obiect JSON.")
        text = cerere.get("text")
        if not isinstance(text, str) or not text.strip():
            raise EroareCerere(HTTPStatus.BAD_REQUEST, "Mesajul e gol.")
        if len(text) > LUNGIME_MAXIMA_MESAJ:
            raise EroareCerere(HTTPStatus.BAD_REQUEST,
                               f"Mesajul are {len(text)} caractere; cel mult {LUNGIME_MAXIMA_MESAJ}.")
        conversatie = cerere.get("conversatie")
        if conversatie is None:
            conversatie = self.catalog.conversatie_noua(text)
        elif isinstance(conversatie, bool) or not isinstance(conversatie, int) or not self.catalog.exista(conversatie):
            raise EroareCerere(HTTPStatus.NOT_FOUND, f"Conversația „{conversatie}” nu există.")

        intrebare = self.catalog.adauga_mesaj(conversatie, ROL_OM, "Tu", text)
        start = time.perf_counter()
        try:
            raspuns_text = self.creier.raspunde(text, self.lungime_raspuns)
        except Exception as e:  # noqa: BLE001 - orice eroare a modelului se arată omului, nu oprește serverul
            return {"conversatie": conversatie, "intrebare": intrebare, "raspuns": None,
                    "eroare": f"{self.creier.eticheta} n-a putut răspunde: {type(e).__name__}: {e}"}
        secunde = round(time.perf_counter() - start, 3)
        raspuns = self.catalog.adauga_mesaj(conversatie, ROL_CREIER, self.creier.eticheta, raspuns_text, secunde)
        return {"conversatie": conversatie, "intrebare": intrebare, "raspuns": raspuns, "eroare": None}


class Cerere(BaseHTTPRequestHandler):
    """O cerere HTTP. Aplicația o găsește pe server (self.server.aplicatie)."""

    server_version = "Cyberspace"
    sys_version = ""
    timeout = 30  # secunde: o legătură care tace nu ține un fir ocupat la nesfârșit

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002 - numele vine din biblioteca standard
        if getattr(self.server, "detaliat", False):
            print(f"[{time.strftime('%H:%M:%S')}] {self.client_address[0]} {format % args}", file=sys.stderr, flush=True)

    # --- răspunsuri ------------------------------------------------------------

    def _trimite(self, cod: int, continut: bytes, tip: str) -> None:
        self.send_response(cod)
        self.send_header("Content-Type", tip)
        self.send_header("Content-Length", str(len(continut)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", POLITICA_CONTINUT)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(continut)

    def _trimite_json(self, cod: int, obiect: Any) -> None:
        self._trimite(cod, json.dumps(obiect, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def _eroare(self, cod: int, mesaj: str) -> None:
        self._trimite_json(cod, {"eroare": mesaj})

    def _are_voie(self) -> bool:
        if self.server.aplicatie.adresa_permisa(self.client_address[0]):
            return True
        self._eroare(HTTPStatus.FORBIDDEN, "Interfața e accesibilă doar de pe acest calculator sau prin Tailscale.")
        return False

    # --- cereri ----------------------------------------------------------------

    def do_GET(self) -> None:  # noqa: N802 - numele vine din biblioteca standard
        if not self._are_voie():
            return
        aplicatie: Aplicatie = self.server.aplicatie
        cale = self.path.split("?", 1)[0]
        try:
            if cale in FISIERE_STATICE:
                nume, tip = FISIERE_STATICE[cale]
                self._trimite(HTTPStatus.OK, (DIRECTOR_STATIC / nume).read_bytes(), tip)
            elif cale == "/api/stare":
                self._trimite_json(HTTPStatus.OK, aplicatie.stare())
            elif cale == "/api/module":
                self._trimite_json(HTTPStatus.OK, aplicatie.lista_module())
            elif cale == "/api/conversatii":
                self._trimite_json(HTTPStatus.OK, {"conversatii": aplicatie.catalog.conversatii()})
            elif cale.startswith("/api/conversatii/") and cale.rsplit("/", 1)[1].isdecimal():
                self._trimite_json(HTTPStatus.OK, aplicatie.mesaje(int(cale.rsplit("/", 1)[1])))
            else:
                self._eroare(HTTPStatus.NOT_FOUND, "Pagina nu există.")
        except EroareCerere as e:
            self._eroare(e.cod, e.mesaj)

    do_HEAD = do_GET  # noqa: N815

    def do_POST(self) -> None:  # noqa: N802
        if not self._are_voie():
            return
        try:
            if self.path.split("?", 1)[0] != "/api/mesaj":
                raise EroareCerere(HTTPStatus.NOT_FOUND, "Pagina nu există.")
            # Doar JSON: un formular de pe alt site, deschis în același browser, nu poate trimite așa ceva.
            if self.headers.get_content_type() != "application/json":
                raise EroareCerere(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, "Cererea trebuie să fie application/json.")
            try:
                octeti = int(self.headers.get("Content-Length", ""))
            except ValueError:
                raise EroareCerere(HTTPStatus.LENGTH_REQUIRED, "Lipsește lungimea cererii.") from None
            if not 0 < octeti <= OCTETI_MAXIMI_CERERE:
                raise EroareCerere(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "Cererea e goală sau prea mare.")
            try:
                cerere = json.loads(self.rfile.read(octeti).decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                raise EroareCerere(HTTPStatus.BAD_REQUEST, "Cererea nu e JSON corect.") from None
            self._trimite_json(HTTPStatus.OK, self.server.aplicatie.mesaj_nou(cerere))
        except EroareCerere as e:
            self._eroare(e.cod, e.mesaj)


class ServerInterfata(ThreadingHTTPServer):
    """Un server pe o singură adresă. Refuză din construcție adresele care înseamnă „toate plăcile de rețea”."""

    daemon_threads = True
    # Pe Windows, „reuse address” ar lăsa două servere pe același port fără nicio eroare; vrem eroarea.
    allow_reuse_address = sys.platform != "win32"

    def __init__(self, adresa: str, port: int, aplicatie: Aplicatie, detaliat: bool = False) -> None:
        if adresa in retea.ADRESE_INTERZISE or not retea.adresa_permisa(adresa):
            raise ValueError(f"Serverul nu ascultă pe „{adresa}”: doar pe 127.0.0.1 și pe adresa Tailscale.")
        self.aplicatie = aplicatie
        self.detaliat = detaliat
        super().__init__((adresa, port), Cerere)

    @property
    def port(self) -> int:
        return int(self.server_address[1])


class Servere:
    """Serverele pornite (câte unul pe adresă), fiecare în firul lui. `opreste()` le închide pe toate."""

    def __init__(self, servere: list[ServerInterfata], neascultate: list[tuple[str, str]]) -> None:
        self.servere = servere
        self.neascultate = neascultate  # (adresa, motivul) pentru adresele pe care nu s-a putut asculta
        self._fire = [threading.Thread(target=s.serve_forever, name=f"interfata-{s.server_address[0]}", daemon=True)
                      for s in servere]
        for fir in self._fire:
            fir.start()

    @property
    def adrese(self) -> list[str]:
        return [f"http://{s.server_address[0]}:{s.port}/" for s in self.servere]

    def opreste(self) -> None:
        for server in self.servere:
            server.shutdown()
            server.server_close()
        for fir in self._fire:
            fir.join(timeout=5)


def porneste(aplicatie: Aplicatie, port: int, adrese: list[str] | None = None, detaliat: bool = False) -> Servere:
    """Pornește serverul pe fiecare adresă dată (implicit doar 127.0.0.1) și întoarce imediat. Prima adresă trebuie
    să meargă (altfel OSError, de ex. port ocupat); dacă pe celelalte nu se poate asculta, se notează și se merge
    mai departe. Cu port 0, sistemul alege un port liber, același pentru toate adresele."""
    adrese = list(adrese or [retea.ADRESA_LOCALA])
    servere: list[ServerInterfata] = []
    neascultate: list[tuple[str, str]] = []
    for adresa in adrese:
        try:
            servere.append(ServerInterfata(adresa, servere[0].port if servere else port, aplicatie, detaliat))
        except OSError as e:
            if not servere:
                raise
            neascultate.append((adresa, str(e)))
        except ValueError:
            for server in servere:
                server.server_close()
            raise
    return Servere(servere, neascultate)
